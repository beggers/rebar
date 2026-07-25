#!/usr/bin/env python3
"""Qualify the literal complete CPython suite against a current owned graph.

The source-only mode is deliberately standalone: it never imports the V6
upstream controller, an ownership auditor, a proof producer, or a candidate.
Actual candidate execution remains fail-closed until independently published
V21/V24 sources, reports, and original edge/deep archives are supplied.
"""

from __future__ import annotations

import argparse
import builtins
import contextlib
import copy
import hashlib
import importlib
import importlib.machinery
import importlib.util
import io
import json
import multiprocessing
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import tempfile
import threading
import time
import types
from typing import Any, Callable, Iterator, Mapping


ROOT = Path(__file__).resolve().parent.parent
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

SCHEMA = "rebar-postfinal-cpython-full-public-locale-v15"
SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v15.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V15.md"
PROTOCOL_SHA256 = (
    "d685374a6698056022aa2ef8a46f16bd3d2b8548aab2ac122a59bba7ac0e9f7a"
)
V6_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v6.py"
V6_SOURCE_SHA256 = (
    "b1522b55b37de2e004b029c128e2e75c3020cda34165bcf0de07cb5ebb3136cb"
)
V6_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V6.md"
V6_PROTOCOL_SHA256 = (
    "8e43ceaa61f6e70e2e1193de71bde8583c101cdbe40bc78d862ae789531aff57"
)
V6_REFERENCE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v6-self-oracle.json"
)
V6_REFERENCE_SHA256 = (
    "1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf"
)
V12_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v12.py"
V12_SOURCE_SHA256 = (
    "c678d02dd906953d320ef0da4b9f0216750c33b81663107127082a98d09e8b64"
)
V12_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V12.md"
V12_PROTOCOL_SHA256 = (
    "2d3da88d31a131f3452c3a884df5285775fd9af9e794339af870f02ed249c00c"
)
V12_FIRST_UPSTREAM_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "postfinal-locale-v12-rust-failures.json"
)
V12_FIRST_UPSTREAM_FAILURE_SHA256 = (
    "fda1204c92f843f3610231f33f1271e113374a5dec8fcfa30e1778658655439e"
)
V12_FIRST_UPSTREAM_FAILURE_BYTES = 6_007
V12_FIRST_UPSTREAM_CAPTURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "postfinal-locale-v12-rust-failures-production-summary.json"
)
V12_FIRST_UPSTREAM_CAPTURE_SHA256 = (
    "a9dec1d4798472773a54cb164c6a68d8026e09bc6edd2ab640916fadc5f10dff"
)
V12_FIRST_UPSTREAM_CAPTURE_BYTES = 6_706
V12_FIRST_UPSTREAM_STDOUT_SHA256 = (
    "92f2d44e311de751c6caddc0f84d1c6a72c8c449522fef2dadf5a9a1a78406a7"
)
V12_FIRST_UPSTREAM_STDOUT_BYTES = 1_221
V12_FIRST_UPSTREAM_STDERR_SHA256 = (
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
)
V13_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v13.py"
V13_SOURCE_SHA256 = (
    "5f9ca285ba617308dead53b97a6d6c707bd4371b7cad79345da8b99223260015"
)
V13_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V13.md"
V13_PROTOCOL_SHA256 = (
    "7ab886971b63faddecb56f4403a582d48903fbb228bc0fccdca80c46f5c4c0dc"
)
V13_FIRST_UPSTREAM_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "postfinal-locale-v13-rust-failures.json"
)
V13_FIRST_UPSTREAM_FAILURE_SHA256 = (
    "18f572e44382130fe6ae29a05bb4c063fccf95d92fc305c9548cb1a63ac01844"
)
V13_FIRST_UPSTREAM_FAILURE_BYTES = 9_479
V13_FIRST_UPSTREAM_CAPTURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "postfinal-locale-v13-rust-failures-production-summary.json"
)
V13_FIRST_UPSTREAM_CAPTURE_SHA256 = (
    "7ae58265f0b845b9f50b30fcb7c7c75018cbcb40d49d240760373a517c2b46c1"
)
V13_FIRST_UPSTREAM_CAPTURE_BYTES = 10_178
V13_FIRST_UPSTREAM_STDOUT_SHA256 = (
    "2df0a9a95f40a3e2dd3c3ee87ccbd4c36567b8c27b660f55ebcacd828c2ea160"
)
V13_FIRST_UPSTREAM_STDOUT_BYTES = 2_089
V13_FIRST_UPSTREAM_STDERR_SHA256 = (
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
)
V14_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v14.py"
V14_SOURCE_SHA256 = (
    "834abdda264bfc81ecf5d6712e524ce1c852b84ed7d8f69cfc26aba6a9ebeb42"
)
V14_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V14.md"
V14_PROTOCOL_SHA256 = (
    "68d8a9044540b0bfeca86316fd4fedded23587333370903d818fce9cc8cf33f9"
)
V14_FIRST_UPSTREAM_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "postfinal-locale-v14-rust-failures.json"
)
V14_FIRST_UPSTREAM_FAILURE_SHA256 = (
    "81112de149d835befaf605419d7426355a4be5d82d97f696d956bcd82627cd8f"
)
V14_FIRST_UPSTREAM_FAILURE_BYTES = 9_023
V14_FIRST_UPSTREAM_CAPTURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "postfinal-locale-v14-rust-failures-production-summary.json"
)
V14_FIRST_UPSTREAM_CAPTURE_SHA256 = (
    "6390b27630888ea1dc77b3d65decb7680b32f7df859dfde8f227a92dc4b1951d"
)
V14_FIRST_UPSTREAM_CAPTURE_BYTES = 9_722
V14_FIRST_UPSTREAM_STDOUT_SHA256 = (
    "6a9273b3fb308dad3bd803cf299f64571378ba1b1c9a545b3ee6653733348b57"
)
V14_FIRST_UPSTREAM_STDOUT_BYTES = 1_975
V14_FIRST_UPSTREAM_STDERR_SHA256 = (
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
)
V13_FIRST_FAILURE_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-FROM-SCRATCH-AUDIT-V13-HISTORICAL-GRAPH-PREFLIGHT-FAILURE.json"
)
V13_FIRST_FAILURE_SHA256 = (
    "465820b50be4d544199844d7bde4c5b8e58391828bdb1c716cc33c50ca6c964b"
)
V13_FAILURE_SOURCE_RELATIVE = "tools/postfinal_independent_engine_audit_v13.py"
V13_FAILURE_SOURCE_SHA256 = (
    "4570798942ab884c1a760b9685ef1a67379febd1c0da81aa18eef221126758fe"
)
V13_FAILURE_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V13.md"
)
V13_FAILURE_PROTOCOL_SHA256 = (
    "f325fe84dc4d14363e3dd4a6038866d8bc2aacd59625231f7dffc4c73257c0c3"
)
V15_FIRST_FAILURE_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-FROM-SCRATCH-AUDIT-V15-"
    "PRESERVED-FAILURE-CODEC-PREFLIGHT-FAILURE.json"
)
V15_FIRST_FAILURE_SHA256 = (
    "a3695f1fd847e9ad882783d18c519b551d7791c5327f55964e202a31ade818ff"
)
V15_FAILURE_SOURCE_RELATIVE = "tools/postfinal_independent_engine_audit_v15.py"
V15_FAILURE_SOURCE_SHA256 = (
    "05ef6b3186aee2a294247e76a3ec20a63ca609e9eebf5b2f882f6b35485514ea"
)
V15_FAILURE_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V15.md"
)
V15_FAILURE_PROTOCOL_SHA256 = (
    "d8e74273945f0047513e7a720183d8b2cd866cbb31911510a16bc64d5219c1f3"
)
V17_FIRST_FAILURE_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-FROM-SCRATCH-AUDIT-V17-POST-OWNER-INTEGRITY-FAILURE.json"
)
V17_FIRST_FAILURE_SHA256 = (
    "8aa1021ba4fc9dcb2456f05c174214c8c7f6c8f4fa2215a13c3373f00e5f557d"
)
V17_FAILURE_SOURCE_RELATIVE = "tools/postfinal_independent_engine_audit_v17.py"
V17_FAILURE_SOURCE_SHA256 = (
    "3184060f66835f0f49cc533a6abb51961de7f92ae2d72ee8c2bd58a94b37ad48"
)
V17_FAILURE_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V17.md"
)
V17_FAILURE_PROTOCOL_SHA256 = (
    "ba912f19b21f0264ecb2066f1141e4ad667802c599437df5a4328e089aa7ba4f"
)
V19_FIRST_FAILURE_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-FROM-SCRATCH-AUDIT-V19-PUBLICATION-FAILURE.json"
)
V19_FIRST_FAILURE_SHA256 = (
    "6d4d73c153bcf1995db78fb4b90ce2851bdece3b13748c75ae045bd1081af390"
)
V19_FAILURE_SOURCE_RELATIVE = "tools/postfinal_independent_engine_audit_v19.py"
V19_FAILURE_SOURCE_SHA256 = (
    "f8f76365749d6893779756844424d1b3f5390bd37c3507f3b6655cce1390b1d6"
)
V19_FAILURE_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V19.md"
)
V19_FAILURE_PROTOCOL_SHA256 = (
    "78cd73d751caccb3458c709b2953e6c9cfc6c7a0edd8406b99d5aee36a9034e5"
)
V22_FIRST_FAILURE_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-CURRENT-BUILD-V22-READONLY-INTEGRATION-PREFLIGHT-FAILURE.json"
)
V22_FIRST_FAILURE_SHA256 = (
    "c6e765f142f25667dd0e7dab45ff16a60abcaae6e230ba05acc596a72d304b01"
)
V22_FAILURE_SOURCE_RELATIVE = "tools/postfinal_current_build_proofs_v22.py"
V22_FAILURE_SOURCE_SHA256 = (
    "ba3062b5fe4aea944e89022266c8d9a7a035708bb30d736f074fc29ce7157e27"
)
V22_FAILURE_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V22.md"
)
V22_FAILURE_PROTOCOL_SHA256 = (
    "e06a24155ca95bf287a5dece90d1a385dad806de8512f177d3146c7bba7acc29"
)
V19_DURABLE_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V19.json"
)
V19_DURABLE_REPORT_SHA256 = (
    "e46484d4a8b389fde66131ac3f8c2db94b1a95ebbf35760f1602117e8c9f23c6"
)
V19_DURABLE_REPORT_BYTES = 161_316
V19_ORIGINAL_OWNER_STDOUT = {
    "rust": (
        12_108,
        "13f647d66cc48354f41ca643b5ff18d94bdccf86cb525aded821e16859b865ce",
    ),
    "vm": (
        11_990,
        "82b444dccee6b61c5b9e41fa25d08cd5e086bb35946a01a6c4b25a473780cf38",
    ),
    "zig": (
        12_096,
        "573c8b30a67657b63431f56c8e8f81826db09ffa39b0c70f19928d1d685a0b33",
    ),
}
V19_ORIGINAL_EMPTY_STDERR_SHA256 = (
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
)
V21_SOURCE_RELATIVE = "tools/postfinal_independent_engine_audit_v21.py"
V21_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V21.md"
)
V21_SOURCE_SHA256 = (
    "ded077962416ada3bddd825d77b2e6785fe3b01184fe5d9058ec17a57b08ea4d"
)
V21_PROTOCOL_SHA256 = (
    "5a78673c6b23e4781070cf5a2290d5f6cecd402fff77ff388d8795370de93a1f"
)
V24_SOURCE_RELATIVE = "tools/postfinal_current_build_proofs_v24.py"
V24_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V24.md"
)
# Freeze only root-authorized, independently reviewed controller bytes.
# Actual owner reports and original proof artifacts remain external runtime pins.
V24_SOURCE_SHA256 = (
    "92b1f082196592e578a5fa6e09b63637c6a1304c04875e5816938ed4fc28eb52"
)
V24_PROTOCOL_SHA256 = (
    "f3ab4f5c3c697a6d39c109b743d949b980bfe0d79aeb6b58a0bc392a3f81e534"
)

METHOD_MATRIX_SHA256 = (
    "5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a"
)
FAMILIES = ("rust", "vm", "zig")
FAMILY_MODULES = {
    "rust": "candidates.rust_candidate",
    "vm": "candidates.vm_candidate",
    "zig": "candidates.zig_candidate",
}
REFERENCE_LABELS = ("reference_a", "reference_b")
PROOF_KINDS = ("edge_archive", "edge_proof", "deep_archive", "deep_proof")
CONTROLLER_PIN_KEYS = (
    "audit_source", "audit_protocol", "proof_source", "proof_protocol",
)
PUBLIC_METHODS = 152
PRIVATE_METHODS = 13
SUPPORT_MODULES = 26
CORPUS_CASES = 403
EXTERNAL_FIXTURE_ASSERTIONS = 11
CONFIGURED_MEMORY_BYTES = 40 * 1024**3
REQUIRED_SUBN_MEMORY_BYTES = 18 * 2**31
EDGE_CHECKS = 223_198
EDGE_CATEGORIES = 49
DEEP_CHECKS = 393
DEEP_SEEDED_CASES = 64
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_EVIDENCE_BYTES = 128 * 1024 * 1024
MAX_WORKER_OUTPUT_BYTES = 64 * 1024 * 1024
PINNED_CPYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)

REPORT_RELATIVE = "oracle/cpython-3.14.6/evidence/postfinal-locale-v15-all.json"
REPORT_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v15-all-failures.json"
)
REPORT_RECEIPT_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "postfinal-locale-v15-all-publication-receipt.json"
)
ROLE_REPORT_RELATIVES = {
    family: "oracle/cpython-3.14.6/evidence/postfinal-locale-v15-"
    + family + ".json"
    for family in FAMILIES
}
ROLE_FAILURE_RELATIVES = {
    family: "oracle/cpython-3.14.6/evidence/postfinal-locale-v15-"
    + family + "-failures.json"
    for family in FAMILIES
}
ROLE_RECEIPT_RELATIVES = {
    family: "oracle/cpython-3.14.6/evidence/postfinal-locale-v15-"
    + family + "-publication-receipt.json"
    for family in FAMILIES
}
APPROVED_OUTPUTS = frozenset({
    REPORT_RELATIVE, REPORT_FAILURE_RELATIVE, REPORT_RECEIPT_RELATIVE,
    *ROLE_REPORT_RELATIVES.values(), *ROLE_FAILURE_RELATIVES.values(),
    *ROLE_RECEIPT_RELATIVES.values(),
})
original: Any = None
inventory: Any = None
durable: Any = None


class OfficialV15Error(AssertionError):
    """The genuine original suite or current independent owner is unproven."""


class OfficialV15WorkerFailure(OfficialV15Error):
    """Retain the genuine partial original methods, guards, and streams."""

    def __init__(self, role: str, message: str, details: Mapping[str, Any]):
        super().__init__(message)
        self.role = role
        self.details = dict(details)


class OfficialV15PublicationFailure(OfficialV15Error):
    """Preserve the instant an exclusive output was really materialized."""

    def __init__(
        self,
        message: str,
        receipt: Mapping[str, Any],
        prior_receipts: tuple[Mapping[str, Any], ...] = (),
    ):
        super().__init__(message)
        self.receipt = copy.deepcopy(dict(receipt))
        self.prior_receipts = tuple(
            copy.deepcopy(dict(prior)) for prior in prior_receipts
        )


V13_FIRST_FAILURE_FIELDS: dict[str, Any] = {
    "failure_path": V13_FIRST_FAILURE_RELATIVE,
    "failure_sha256": V13_FIRST_FAILURE_SHA256,
    "failure_schema": (
        "rebar-postfinal-independent-engine-audit-v13-"
        "actual-historical-graph-preflight-failure"
    ),
    "status": "FAIL",
    "failed_stage": (
        "historical-zig-edge-authentication-before-any-new-native-owner-worker"
    ),
    "actual_error_type": "AssertionError",
    "actual_error_message": "the ZIG native-bridge is stale or unproven",
    "actual_exit_code": 1,
    "native_owner_workers_started": 0,
    "original_edge_worker_started": False,
    "synthetic": False,
    "qualifies_current_engine": False,
    "v13_source_path": V13_FAILURE_SOURCE_RELATIVE,
    "v13_source_sha256": V13_FAILURE_SOURCE_SHA256,
    "v13_protocol_path": V13_FAILURE_PROTOCOL_RELATIVE,
    "v13_protocol_sha256": V13_FAILURE_PROTOCOL_SHA256,
    "stdout_capture": "NOT CAPTURED",
    "stderr_capture": "NOT CAPTURED",
    "combined_traceback_line_count": 34,
    "combined_traceback_separately_captured": False,
    "fresh_ownership_report": "NOT CREATED",
    "fresh_ownership_failure_report": "NOT CREATED",
    "fresh_strict_report": "NOT CREATED",
    "fresh_strict_failure_report": "NOT CREATED",
    "performance": "NOT MEASURED",
    "holdout": "NOT ACCESSED",
}
V15_FIRST_FAILURE_FIELDS: dict[str, Any] = {
    "failure_path": V15_FIRST_FAILURE_RELATIVE,
    "failure_sha256": V15_FIRST_FAILURE_SHA256,
    "failure_schema": (
        "rebar-postfinal-independent-engine-audit-v15-"
        "actual-preserved-failure-codec-preflight-failure"
    ),
    "status": "FAIL",
    "failed_stage": (
        "strict-authentication-of-the-original-v13-failure-"
        "before-any-new-native-owner-worker"
    ),
    "actual_error_type": "AuditV15Error",
    "actual_error_message": (
        "the complete genuine first V13 failure is not frozen canonical JSON"
    ),
    "actual_exit_code": 1,
    "native_owner_workers_started": 0,
    "original_edge_worker_started": False,
    "synthetic": False,
    "qualifies_current_engine": False,
    "v15_source_path": V15_FAILURE_SOURCE_RELATIVE,
    "v15_source_sha256": V15_FAILURE_SOURCE_SHA256,
    "v15_protocol_path": V15_FAILURE_PROTOCOL_RELATIVE,
    "v15_protocol_sha256": V15_FAILURE_PROTOCOL_SHA256,
    "stdout_capture": "NOT CAPTURED",
    "stderr_capture": "NOT CAPTURED",
    "combined_traceback_line_count": 20,
    "combined_traceback_separately_captured": False,
    "fresh_ownership_report": "NOT CREATED",
    "fresh_ownership_failure_report": "NOT CREATED",
    "fresh_strict_report": "NOT CREATED",
    "fresh_strict_failure_report": "NOT CREATED",
    "preserved_v13_first_failure_path": V13_FIRST_FAILURE_RELATIVE,
    "preserved_v13_first_failure_sha256": V13_FIRST_FAILURE_SHA256,
    "performance": "NOT MEASURED",
    "holdout": "NOT ACCESSED",
}
V17_FIRST_FAILURE_FIELDS: dict[str, Any] = {
    "source_path": V17_FIRST_FAILURE_RELATIVE,
    "sha256": V17_FIRST_FAILURE_SHA256,
    "schema": (
        "rebar-postfinal-independent-engine-audit-v17-"
        "actual-post-owner-integrity-failure"
    ),
    "status": "FAIL",
    "exit_code": 1,
    "failed_stage": (
        "unpreserved-static-graph-integrity-recheck-after-"
        "three-genuine-native-owner-workers"
    ),
    "actual_error_type": (
        "tools.postfinal_from_scratch_audit_v2.AuditV2Error"
    ),
    "actual_error_message": (
        "actual current 76-control source audit changed the immutable "
        "universal audit contract"
    ),
    "actual_completed_native_owner_families": ["rust", "vm", "zig"],
    "actual_native_owner_workers_completed": 3,
    "actual_native_owner_observations": (
        "NOT PRESERVED BY THE FAILED CONTROLLER"
    ),
    "actual_captured_combined_output_lines": 27,
    "output_capture": (
        "complete combined command output; stdout and stderr were not "
        "separately captured"
    ),
    "fresh_ownership_report": "NOT CREATED",
    "fresh_ownership_failure_report": "NOT CREATED",
    "fresh_strict_report": "NOT CREATED",
    "fresh_strict_failure_report": "NOT CREATED",
    "historical_failure_qualifies_current_build": False,
}
V19_FIRST_FAILURE_FIELDS: dict[str, Any] = {
    "source_path": V19_FIRST_FAILURE_RELATIVE,
    "sha256": V19_FIRST_FAILURE_SHA256,
    "schema": (
        "rebar-postfinal-independent-engine-audit-v19-"
        "actual-exclusive-publication-first-failure"
    ),
    "status": "FAIL",
    "exit_code": 1,
    "invocation_count": 1,
    "actual_error_message": (
        "the exclusive V19 publication failed; actual syscall receipt retained"
    ),
    "actual_inner_error_message": (
        "an exact exclusively published V19 all-family report was changed"
    ),
    "v19_source_path": V19_FAILURE_SOURCE_RELATIVE,
    "v19_source_sha256": V19_FAILURE_SOURCE_SHA256,
    "v19_protocol_path": V19_FAILURE_PROTOCOL_RELATIVE,
    "v19_protocol_sha256": V19_FAILURE_PROTOCOL_SHA256,
    "durable_report_path": V19_DURABLE_REPORT_RELATIVE,
    "durable_report_sha256": V19_DURABLE_REPORT_SHA256,
    "durable_report_bytes": V19_DURABLE_REPORT_BYTES,
    "durable_embedded_document_status": "PASS",
    "actual_controller_status": "FAIL",
    "canonical_report_bytes_independently_verified": True,
    "embedded_pass_qualifies_current_engine": False,
    "historical_failure_qualifies_current_build": False,
    "completed_native_owner_worker_count": 3,
    "complete_actual_native_owner_streams_preserved": True,
    "actual_original_native_owner_workers": {
        family: {
            "actual_returncode": 0,
            "original_stdout_bytes": length,
            "original_stdout_sha256": sha256,
            "complete_original_stdout_verified": True,
            "original_stderr_bytes": 0,
            "original_stderr_sha256": V19_ORIGINAL_EMPTY_STDERR_SHA256,
            "complete_original_stderr_verified": True,
            "matcher_guards": 13,
            "native_loader_guards": 5,
            "standard_pickle_checks": 16,
            "standard_pickle_failures": 0,
            "external_regex_packages": 0,
        }
        for family, (length, sha256) in V19_ORIGINAL_OWNER_STDOUT.items()
    },
    "exclusive_create_succeeded": True,
    "actual_bytes_written": V19_DURABLE_REPORT_BYTES,
    "file_fsync_succeeded": True,
    "parent_directory_fsync_succeeded": True,
    "canonical_reread_succeeded": False,
    "actual_write_calls": [{
        "requested_bytes": V19_DURABLE_REPORT_BYTES,
        "returned_bytes": V19_DURABLE_REPORT_BYTES,
    }],
    "original_non_roundtripping_in_memory_value": (
        "NOT PRESERVED BY THE FAILED CONTROLLER"
    ),
    "fresh_v19_ownership_failure_report": False,
    "fresh_v19_strict_report": False,
    "fresh_v19_strict_failure_report": False,
    "strict_audit": "NOT RUN",
    "performance": "NOT MEASURED",
    "holdout": "NOT ACCESSED",
}

V22_FIRST_FAILURE_FIELDS: dict[str, Any] = {
    "source_path": V22_FIRST_FAILURE_RELATIVE,
    "sha256": V22_FIRST_FAILURE_SHA256,
    "schema": (
        "rebar-postfinal-current-build-proof-v22-"
        "actual-read-only-integration-preflight-failure"
    ),
    "status": "FAIL",
    "synthetic": False,
    "production_observations_invented": False,
    "qualifies_current_engine": False,
    "failed_stage": (
        "candidate-free authentication of the genuine historical V13 "
        "summary before the first original edge worker"
    ),
    "attempted_family": "rust",
    "families_not_reached": ["vm", "zig"],
    "actual_exception_type": (
        "tools.postfinal_current_build_proofs_v22.ProofV22Error"
    ),
    "actual_exception_message": (
        "the genuine original failed V13 first invocation was forged"
    ),
    "actual_combined_traceback_line_count": 24,
    "actual_failed_invocation_boundary_counters": (
        "NOT PRESERVED BY THE FAILED CONTROLLER"
    ),
    "native_owner_workers_started": 0,
    "original_edge_workers_started": 0,
    "original_deep_workers_started": 0,
    "correctness_results_published": False,
    "benchmark_or_timing_executed": False,
    "performance": "NOT MEASURED",
    "holdout": "NOT ACCESSED",
}
V22_FIRST_FAILURE_KEYS = frozenset(V22_FIRST_FAILURE_FIELDS) | frozenset({
    "actual_invocation",
    "frozen_failed_controller",
    "actual_passing_prerequisites",
    "actual_combined_traceback_lines",
    "actual_historical_summary_mismatch",
    "independent_follow_up_differential",
})
V22_FAILED_CONTROLLER_FIELDS: dict[str, str] = {
    "source_path": V22_FAILURE_SOURCE_RELATIVE,
    "source_sha256": V22_FAILURE_SOURCE_SHA256,
    "protocol_path": V22_FAILURE_PROTOCOL_RELATIVE,
    "protocol_sha256": V22_FAILURE_PROTOCOL_SHA256,
}
V22_HISTORICAL_MISMATCH_FIELDS: dict[str, Any] = {
    "historical_version": "v13",
    "field": "failed_stage",
    "expected_field_count": 26,
    "actual_authenticated_field_count": 26,
    "missing_fields": [],
    "extra_fields": [],
    "v22_expected_value": "historical-zig-edge-preflight",
    "actual_authenticated_v21_value": (
        "historical-zig-edge-authentication-before-any-new-native-owner-worker"
    ),
    "other_fields_match": True,
    "other_historical_summaries_exactly_match": ["v15", "v17", "v19"],
}
V22_FOLLOW_UP_READ_ONLY_EFFECTS: dict[str, int] = {
    "candidate_imports": 0,
    "clock_samples": 0,
    "filesystem_writes": 0,
    "native_workers_started": 0,
    "subprocesses_started": 0,
}
V24_REQUIRED_NONQUALIFYING_FLAGS = (
    "v13_first_owner_preflight_failure_qualifies_current_engine",
    "v15_first_owner_preflight_failure_qualifies_current_engine",
    "v17_first_owner_postflight_failure_qualifies_current_engine",
    "v19_first_owner_publication_failure_qualifies_current_engine",
    "v22_first_proof_preflight_failure_qualifies_current_engine",
    "historical_v10_graph_qualifies_current_engine",
)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise OfficialV15Error(message)


def valid_sha256(value: Any) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
        and len(set(value)) > 1
    )


def canonical(document: Any) -> bytes:
    return json.dumps(
        document, ensure_ascii=True, allow_nan=False,
        sort_keys=True, separators=(",", ":"),
    ).encode("ascii")


def digest(document: Any) -> str:
    return hashlib.sha256(canonical(document)).hexdigest()


def _synthetic_digest(label: str) -> str:
    return hashlib.sha256(
        ("candidate-free-official-v15:" + label).encode("ascii"),
    ).hexdigest()


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and Path(sys.executable).resolve() == PINNED_CPYTHON.resolve()
        and bool(sys.path)
        and sys.path[0] == str(ROOT)
        and Path(__file__).resolve() == ROOT / SOURCE_RELATIVE,
        "the exact isolated pinned CPython 3.14.6 V15 source is required",
    )


def _read_regular(path: Path, bound: int, label: str) -> bytes:
    require(isinstance(path, Path) and type(bound) is int and bound > 0,
            "an exact bounded regular input is required: " + label)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise OfficialV15Error("BLOCKED: unavailable frozen " + label) from error
    try:
        metadata = os.fstat(descriptor)
        require(stat.S_ISREG(metadata.st_mode)
                and 0 < metadata.st_size <= bound,
                "an actual frozen input is not a bounded regular file: " + label)
        pieces: list[bytes] = []
        remaining = metadata.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1024 * 1024))
            require(bool(chunk), "a frozen input was truncated: " + label)
            pieces.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "a frozen input grew during authentication: " + label)
        return b"".join(pieces)
    finally:
        os.close(descriptor)


def _frozen(relative: str, expected: str) -> bytes:
    approved = {
        SOURCE_RELATIVE, PROTOCOL_RELATIVE,
        V6_SOURCE_RELATIVE, V6_PROTOCOL_RELATIVE,
        V12_SOURCE_RELATIVE, V12_PROTOCOL_RELATIVE,
        V13_SOURCE_RELATIVE, V13_PROTOCOL_RELATIVE,
        V14_SOURCE_RELATIVE, V14_PROTOCOL_RELATIVE,
        V21_SOURCE_RELATIVE, V21_PROTOCOL_RELATIVE,
        V24_SOURCE_RELATIVE, V24_PROTOCOL_RELATIVE,
    }
    require(type(relative) is str and relative in approved
            and valid_sha256(expected),
            "only an individually frozen V6/V12/V13/V14/V15/V21/V24 source or protocol is permitted")
    result = _read_regular(ROOT / relative, MAX_SOURCE_BYTES, relative)
    require(hashlib.sha256(result).hexdigest() == expected,
            "an independently frozen source or protocol changed: " + relative)
    return result


def _chosen(selected: str) -> tuple[str, ...]:
    require(type(selected) is str and selected in ("all", *FAMILIES),
            "select exactly one genuine owned native family or all families")
    return FAMILIES if selected == "all" else (selected,)


def _known_controller_pins() -> dict[str, str]:
    return {
        "audit_source": V21_SOURCE_SHA256,
        "audit_protocol": V21_PROTOCOL_SHA256,
        "proof_source": V24_SOURCE_SHA256,
        "proof_protocol": V24_PROTOCOL_SHA256,
    }


def _candidate_pin_values(
    selected: str, supplied: Mapping[str, Any], *,
    expected_controllers: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    require(isinstance(supplied, Mapping),
            "independently published V21/V24 ownership and proof pins are required")
    approved_keys = {
        *CONTROLLER_PIN_KEYS,
        "base_report", "strict_report",
        *(family + "_" + kind
          for family in FAMILIES for kind in PROOF_KINDS),
    }
    require(set(supplied) <= approved_keys,
            "an undeclared report, candidate, or proof pin is forbidden")
    families = _chosen(selected)
    expected = (
        _known_controller_pins()
        if expected_controllers is None else dict(expected_controllers)
    )
    require(set(expected) == set(CONTROLLER_PIN_KEYS),
            "the complete independent V21/V24 source graph is required")
    values: dict[str, Any] = {
        key: supplied.get(key)
        for key in (*CONTROLLER_PIN_KEYS, "base_report", "strict_report")
    }
    for family in FAMILIES:
        for kind in PROOF_KINDS:
            key = family + "_" + kind
            observed = supplied.get(key)
            if family in families:
                values[key] = observed
            else:
                require(observed is None,
                        "an unselected family cannot provide hidden proof pins: "
                        + key)
    for key, value in values.items():
        require(valid_sha256(value),
                "BLOCKED: independently publish the actual " + key + " SHA-256")
    for key in CONTROLLER_PIN_KEYS:
        require(valid_sha256(expected[key]) and values[key] == expected[key],
                "BLOCKED: the final independently published " + key
                + " source or protocol is unavailable or substituted")
    forbidden = {
        PROTOCOL_SHA256, V6_SOURCE_SHA256, V6_PROTOCOL_SHA256,
        V6_REFERENCE_SHA256, METHOD_MATRIX_SHA256,
    }
    require(len(set(values.values())) == len(values)
            and not (set(values.values()) & forbidden),
            "actual independent reports, sources, and family archives must be "
            "distinct and cannot reuse a frozen reference or method identity")
    return {key: str(value) for key, value in values.items()}


def _safe_output_path(relative: Any) -> Path:
    require(type(relative) is str and relative in APPROVED_OUTPUTS,
            "only a new exact V15 official result or failure path is permitted")
    parsed = PurePosixPath(relative)
    require(not parsed.is_absolute() and ".." not in parsed.parts
            and "\\" not in relative and "\x00" not in relative
            and parsed.as_posix() == relative,
            "an official result destination escaped the genuine V15 allowlist")
    return ROOT / relative


def _validate_publication_receipt(receipt: Any) -> dict[str, Any]:
    require(isinstance(receipt, dict)
            and set(receipt) == {
                "schema", "path", "expected_payload_sha256",
                "expected_payload_bytes", "actual_file_created",
                "actual_payload_bytes_written", "actual_write_calls",
                "actual_file_fsync", "actual_directory_fsync",
                "canonical_reread_succeeded", "fully_durable_publication",
            }
            and receipt.get("schema")
            == SCHEMA + "-actual-exclusive-publication-receipt"
            and type(receipt.get("path")) is str
            and receipt["path"] in APPROVED_OUTPUTS
            and valid_sha256(receipt.get("expected_payload_sha256"))
            and type(receipt.get("expected_payload_bytes")) is int
            and 0 < receipt["expected_payload_bytes"] <= MAX_EVIDENCE_BYTES
            and type(receipt.get("actual_payload_bytes_written")) is int
            and 0 <= receipt["actual_payload_bytes_written"]
            <= receipt["expected_payload_bytes"]
            and isinstance(receipt.get("actual_write_calls"), list)
            and all(type(receipt.get(name)) is bool for name in (
                "actual_file_created", "actual_file_fsync",
                "actual_directory_fsync", "canonical_reread_succeeded",
                "fully_durable_publication",
            )),
            "a genuine exclusive-output creation/fsync receipt was forged")
    created = receipt["actual_file_created"]
    written = receipt["actual_payload_bytes_written"]
    file_sync = receipt["actual_file_fsync"]
    directory_sync = receipt["actual_directory_fsync"]
    reread = receipt["canonical_reread_succeeded"]
    complete = receipt["fully_durable_publication"]
    remaining = receipt["expected_payload_bytes"]
    counted = 0
    for index, call in enumerate(receipt["actual_write_calls"]):
        require(isinstance(call, dict)
                and set(call) == {"requested_bytes", "returned_bytes"}
                and type(call.get("requested_bytes")) is int
                and call["requested_bytes"] == remaining
                and remaining > 0,
                "a genuine exclusive-publication write continuation was forged")
        returned = call.get("returned_bytes")
        if returned is None:
            require(index == len(receipt["actual_write_calls"]) - 1,
                    "an actual failed publication syscall was falsely retried")
            break
        require(type(returned) is int and 0 <= returned <= remaining,
                "an actual exclusive-publication syscall return was forged")
        counted += returned
        remaining -= returned
        if returned == 0:
            require(index == len(receipt["actual_write_calls"]) - 1,
                    "a genuinely failed zero-byte write was falsely retried")
            break
    require((created or written == 0)
            and (created or not receipt["actual_write_calls"])
            and counted == written
            and (created or not file_sync)
            and (file_sync or not directory_sync)
            and (not file_sync
                 or written == receipt["expected_payload_bytes"])
            and (not reread or complete)
            and complete == (
                created and written == receipt["expected_payload_bytes"]
                and file_sync and directory_sync
            ),
            "an actual partial exclusive publication was hidden or falsely "
            "claimed fully durable")
    return receipt


def _freeze_successful_publication_receipt(receipt: Any) -> bytes:
    validated = _validate_publication_receipt(receipt)
    require(validated["actual_file_created"] is True
            and validated["actual_file_fsync"] is True
            and validated["actual_directory_fsync"] is True
            and validated["canonical_reread_succeeded"] is True
            and validated["fully_durable_publication"] is True,
            "an incomplete or failed publication cannot become a success receipt")
    frozen = canonical(validated)
    decoded = json.loads(frozen)
    require(isinstance(decoded, dict)
            and canonical(decoded) == frozen
            and _validate_publication_receipt(decoded) == validated,
            "an actual complete success receipt lost immutable canonical bytes")
    return frozen


def _thaw_successful_publication_receipt(
    frozen: Any,
    relative: str,
    expected_sha256: str,
) -> dict[str, Any]:
    require(type(frozen) is bytes and 0 < len(frozen) <= MAX_EVIDENCE_BYTES
            and type(relative) is str and relative in APPROVED_OUTPUTS
            and valid_sha256(expected_sha256),
            "an immutable real exclusive-publication receipt is mandatory")
    decoded = json.loads(frozen)
    require(isinstance(decoded, dict)
            and canonical(decoded) == frozen
            and _validate_publication_receipt(decoded) == decoded
            and decoded["path"] == relative
            and decoded["expected_payload_sha256"] == expected_sha256
            and decoded["fully_durable_publication"] is True
            and decoded["canonical_reread_succeeded"] is True,
            "an immutable successful real receipt was omitted or substituted")
    return decoded


def _validate_durable_success_publication(
    record: Any,
    relative: str,
    receipt_relative: str,
) -> dict[str, Any]:
    require(isinstance(record, dict)
            and set(record) == {
                "path", "sha256", "fully_durable_publication",
                "actual_exclusive_publication_receipt",
                "publication_receipt_path", "publication_receipt_sha256",
                "actual_receipt_publication_receipt",
            }
            and type(relative) is str and relative in APPROVED_OUTPUTS
            and type(receipt_relative) is str
            and receipt_relative in APPROVED_OUTPUTS
            and relative != receipt_relative
            and record.get("path") == relative
            and record.get("publication_receipt_path") == receipt_relative
            and valid_sha256(record.get("sha256"))
            and valid_sha256(record.get("publication_receipt_sha256"))
            and type(record.get("fully_durable_publication")) is bool
            and record["fully_durable_publication"] is True,
            "a successful original publication lost its durable receipt")
    primary = _validate_publication_receipt(
        record.get("actual_exclusive_publication_receipt"),
    )
    stored = _validate_publication_receipt(
        record.get("actual_receipt_publication_receipt"),
    )
    require(primary["path"] == relative
            and primary["expected_payload_sha256"] == record["sha256"]
            and primary["fully_durable_publication"] is True
            and primary["canonical_reread_succeeded"] is True
            and stored["path"] == receipt_relative
            and stored["expected_payload_sha256"]
            == record["publication_receipt_sha256"]
            and stored["fully_durable_publication"] is True
            and stored["canonical_reread_succeeded"] is True,
            "a genuine role or all-family receipt was dropped, forged, "
            "reused, or not actually durably published")
    return record


def _normalize_publication_document(
    document: Mapping[str, Any],
) -> tuple[dict[str, Any], bytes]:
    require(isinstance(document, Mapping),
            "a genuine official result must be frozen before exclusive creation")
    raw = canonical(dict(document))
    require(0 < len(raw) + 1 <= MAX_EVIDENCE_BYTES,
            "a genuine canonical publication exceeded its exact byte boundary")
    normalized = json.loads(raw)
    require(isinstance(normalized, dict) and canonical(normalized) == raw,
            "a finite unique-key canonical result failed exact JSON normalization")
    return normalized, raw + b"\n"


def _validate_normalized_publication_readback(
    raw: Any,
    expected: bytes,
    normalized: Mapping[str, Any],
) -> dict[str, Any]:
    require(type(raw) is bytes and type(expected) is bytes
            and isinstance(normalized, Mapping)
            and 0 < len(raw) <= MAX_EVIDENCE_BYTES and raw == expected,
            "the actually durable original report changed its frozen bytes")
    decoded = json.loads(raw)
    require(isinstance(decoded, dict)
            and decoded == dict(normalized)
            and canonical(decoded) + b"\n" == raw,
            "the durable official report failed its exact normalized reread")
    return decoded


def _preflight_fresh_outputs(relatives: tuple[str, ...]) -> None:
    require(len(relatives) == len(set(relatives)),
            "a genuine V15 failure or result destination cannot be reused")
    for relative in relatives:
        path = _safe_output_path(relative)
        require(path.parent.is_dir() and not path.parent.is_symlink()
                and path.resolve(strict=False) == path
                and not path.exists() and not path.is_symlink(),
                "refusing to overwrite, retry, or redirect genuine V15 evidence: "
                + relative)


def _exclusive_write(
    document: Mapping[str, Any],
    relative: str,
) -> tuple[str, bytes]:
    require(isinstance(document, Mapping),
            "only genuine complete official V15 evidence may be published")
    path = _safe_output_path(relative)
    require(path.parent.is_dir() and not path.parent.is_symlink()
            and path.resolve(strict=False) == path,
            "the exact independently guarded V15 report parent is unsafe")
    normalized_document, payload = _normalize_publication_document(document)
    receipt: dict[str, Any] = {
        "schema": SCHEMA + "-actual-exclusive-publication-receipt",
        "path": relative,
        "expected_payload_sha256": hashlib.sha256(payload).hexdigest(),
        "expected_payload_bytes": len(payload),
        "actual_file_created": False,
        "actual_payload_bytes_written": 0,
        "actual_write_calls": [],
        "actual_file_fsync": False,
        "actual_directory_fsync": False,
        "canonical_reread_succeeded": False,
        "fully_durable_publication": False,
    }
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    directory_flags |= getattr(os, "O_CLOEXEC", 0)
    directory_flags |= getattr(os, "O_NOFOLLOW", 0)
    directory = -1
    descriptor = -1
    try:
        directory = os.open(path.parent, directory_flags)
        actual = os.fstat(directory)
        named = os.stat(path.parent, follow_symlinks=False)
        require(stat.S_ISDIR(actual.st_mode)
                and (actual.st_dev, actual.st_ino)
                == (named.st_dev, named.st_ino),
                "the genuine exclusively guarded report directory changed")
        flags = os.O_RDWR | os.O_CREAT | os.O_EXCL
        flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        try:
            descriptor = os.open(path.name, flags, 0o600, dir_fd=directory)
        except OSError as error:
            raise OfficialV15Error(
                "refusing to replace or retry a genuine V15 result: " + relative,
            ) from error
        receipt["actual_file_created"] = True
        remaining = memoryview(payload)
        while remaining:
            attempt: dict[str, int | None] = {
                "requested_bytes": len(remaining),
                "returned_bytes": None,
            }
            receipt["actual_write_calls"].append(attempt)
            written = os.write(descriptor, remaining)
            attempt["returned_bytes"] = written
            require(type(written) is int and 0 < written <= len(remaining),
                    "an exclusively created genuine V15 report was truncated")
            receipt["actual_payload_bytes_written"] += written
            remaining = remaining[written:]
        os.fsync(descriptor)
        receipt["actual_file_fsync"] = True
        os.fsync(directory)
        receipt["actual_directory_fsync"] = True
        receipt["fully_durable_publication"] = True
        actual_file = os.fstat(descriptor)
        named_file = os.stat(
            path.name, dir_fd=directory, follow_symlinks=False,
        )
        require(stat.S_ISREG(actual_file.st_mode)
                and (actual_file.st_dev, actual_file.st_ino)
                == (named_file.st_dev, named_file.st_ino)
                and actual_file.st_size == len(payload),
                "the fully durable exclusive V15 report changed its identity")
        os.lseek(descriptor, 0, os.SEEK_SET)
        actual_pieces: list[bytes] = []
        outstanding = len(payload)
        while outstanding:
            piece = os.read(descriptor, min(outstanding, 1024 * 1024))
            require(bool(piece),
                    "the fully durable original V15 report was truncated")
            actual_pieces.append(piece)
            outstanding -= len(piece)
        require(os.read(descriptor, 1) == b"",
                "the fully durable original V15 report grew during reread")
        _validate_normalized_publication_readback(
            b"".join(actual_pieces), payload, normalized_document,
        )
        receipt["canonical_reread_succeeded"] = True
        _validate_publication_receipt(receipt)
    except (OfficialV15Error, OSError, ValueError, TypeError, MemoryError) as error:
        if receipt["actual_file_created"]:
            preserved = _validate_publication_receipt(receipt)
            raise OfficialV15PublicationFailure(
                "a genuine exclusive V15 output was created but could not be "
                "fully durably published and canonically verified: " + relative,
                preserved,
            ) from error
        raise
    finally:
        if descriptor != -1:
            os.close(descriptor)
        if directory != -1:
            os.close(directory)
    return (
        receipt["expected_payload_sha256"],
        _freeze_successful_publication_receipt(receipt),
    )


def _publish_with_durable_success_receipt(
    document: Mapping[str, Any],
    relative: str,
    receipt_relative: str,
) -> dict[str, Any]:
    require(type(relative) is str and type(receipt_relative) is str
            and relative in APPROVED_OUTPUTS
            and receipt_relative in APPROVED_OUTPUTS
            and relative != receipt_relative,
            "an actual original result requires a distinct safe receipt file")
    primary_sha256, primary_frozen = _exclusive_write(document, relative)
    primary = _thaw_successful_publication_receipt(
        primary_frozen, relative, primary_sha256,
    )
    receipt_document = {
        "schema": SCHEMA + "-actual-durable-success-publication-receipt",
        "status": "PASS",
        "report_path": relative,
        "report_sha256": primary_sha256,
        "actual_exclusive_publication_receipt": copy.deepcopy(primary),
        "production_observations_invented": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    try:
        receipt_sha256, receipt_frozen = _exclusive_write(
            receipt_document, receipt_relative,
        )
        stored = _thaw_successful_publication_receipt(
            receipt_frozen, receipt_relative, receipt_sha256,
        )
        record = {
            "path": relative,
            "sha256": primary_sha256,
            "fully_durable_publication": True,
            "actual_exclusive_publication_receipt": copy.deepcopy(primary),
            "publication_receipt_path": receipt_relative,
            "publication_receipt_sha256": receipt_sha256,
            "actual_receipt_publication_receipt": copy.deepcopy(stored),
        }
        return _validate_durable_success_publication(
            record, relative, receipt_relative,
        )
    except OfficialV15PublicationFailure as error:
        raise OfficialV15PublicationFailure(
            "a fully durable original V15 report could not preserve its "
            "separate complete actual syscall receipt: " + relative,
            error.receipt,
            (primary, *error.prior_receipts),
        ) from error
    except (OfficialV15Error, OSError, ValueError, TypeError, MemoryError) as error:
        raise OfficialV15PublicationFailure(
            "a fully durable original V15 report lost its separate "
            "complete actual syscall receipt: " + relative,
            primary,
        ) from error


def _validate_original_contract(module: Any) -> None:
    upstream = module.original.upstream
    require(module.SCHEMA == "rebar-postfinal-cpython-full-public-locale-v6"
            and module.SOURCE_RELATIVE == V6_SOURCE_RELATIVE
            and module.PROTOCOL_RELATIVE == V6_PROTOCOL_RELATIVE
            and module.PROTOCOL_SHA256 == V6_PROTOCOL_SHA256
            and module.METHOD_MATRIX_SHA256 == METHOD_MATRIX_SHA256
            and tuple(module.FAMILIES) == FAMILIES
            and tuple(module.REFERENCE_LABELS) == REFERENCE_LABELS
            and module.SELF_ORACLE_RELATIVE == V6_REFERENCE_RELATIVE
            and upstream.PUBLIC_METHODS == PUBLIC_METHODS
            and upstream.PRIVATE_METHODS == PRIVATE_METHODS
            and upstream.ORIGINAL_METHODS == PUBLIC_METHODS + PRIVATE_METHODS
            and len(upstream.OFFICIAL_SUPPORT_MODULES) == SUPPORT_MODULES
            and upstream.CORPUS_CASES == CORPUS_CASES
            and upstream.EXTERNAL_FIXTURE_ASSERTION_CASES
            == EXTERNAL_FIXTURE_ASSERTIONS
            and upstream.CONFIGURED_OFFICIAL_MEMORY_BYTES
            == CONFIGURED_MEMORY_BYTES
            and upstream.REQUIRED_OFFICIAL_SUBN_MEMORY_BYTES
            == REQUIRED_SUBN_MEMORY_BYTES
            and not upstream.PUBLIC_METHOD_WAIVERS
            and Path(module.__file__).resolve() == ROOT / V6_SOURCE_RELATIVE,
            "the actual immutable 152-method, 26-file, 403/11 original V6 "
            "CPython contract was substituted")


def _authenticate_controller(source_sha256: str, protocol_sha256: str) -> Any:
    global original
    verify_runtime()
    require(valid_sha256(source_sha256) and protocol_sha256 == PROTOCOL_SHA256,
            "BLOCKED: independently publish the exact genuine V15 source and protocol")
    _frozen(SOURCE_RELATIVE, source_sha256)
    _frozen(PROTOCOL_RELATIVE, PROTOCOL_SHA256)
    _frozen(V6_SOURCE_RELATIVE, V6_SOURCE_SHA256)
    _frozen(V6_PROTOCOL_RELATIVE, V6_PROTOCOL_SHA256)
    if original is None:
        original = importlib.import_module(
            "tools.postfinal_cpython_locale_oracle_v6",
        )
    _validate_original_contract(original)
    return original


def _load_candidate_modules(pins: Mapping[str, str]) -> tuple[Any, Any]:
    global inventory, durable
    for relative, key in (
        (V21_SOURCE_RELATIVE, "audit_source"),
        (V21_PROTOCOL_RELATIVE, "audit_protocol"),
        (V24_SOURCE_RELATIVE, "proof_source"),
        (V24_PROTOCOL_RELATIVE, "proof_protocol"),
    ):
        _frozen(relative, pins[key])
    if inventory is None:
        inventory = importlib.import_module(
            "tools.postfinal_independent_engine_audit_v21",
        )
    if durable is None:
        durable = importlib.import_module(
            "tools.postfinal_current_build_proofs_v24",
        )
    require(inventory.SCHEMA == "rebar-postfinal-independent-engine-audit-v21"
            and inventory.SOURCE_RELATIVE == V21_SOURCE_RELATIVE
            and inventory.PROTOCOL_RELATIVE == V21_PROTOCOL_RELATIVE
            and inventory.PROTOCOL_SHA256 == pins["audit_protocol"]
            and tuple(inventory.CORE_FAMILIES) == FAMILIES
            and Path(inventory.__file__).resolve() == ROOT / V21_SOURCE_RELATIVE
            and durable.SCHEMA == "rebar-postfinal-current-build-proofs-v24"
            and durable.SOURCE_RELATIVE == V24_SOURCE_RELATIVE
            and durable.PROTOCOL_RELATIVE == V24_PROTOCOL_RELATIVE
            and durable.PROTOCOL_SHA256 == pins["proof_protocol"]
            and Path(durable.__file__).resolve() == ROOT / V24_SOURCE_RELATIVE
            and callable(inventory.authenticate_qualified_audits)
            and callable(inventory.snapshot_current_graph)
            and callable(inventory.run_native_worker)
            and callable(inventory.validate_native_owner)
            and callable(durable.preflight)
            and callable(durable.authenticate_qualified_edge)
            and callable(durable.authenticate_qualified_deep),
            "a final separately authenticated V21/V24 genuine owner or original "
            "edge/deep proof controller was substituted")
    return inventory, durable


def _safe_graph_path(relative: Any) -> bool:
    if type(relative) is not str or not relative or "\\" in relative:
        return False
    parsed = PurePosixPath(relative)
    return (not parsed.is_absolute() and ".." not in parsed.parts
            and "\x00" not in relative and parsed.as_posix() == relative)


def _validate_current_graph(
    graph: Any,
    expected_sources: Mapping[str, Any],
    expected_natives: Mapping[str, Any],
) -> dict[str, Any]:
    require(isinstance(graph, dict)
            and graph.get("source_count") == 12
            and graph.get("native_binary_count") == 5
            and isinstance(graph.get("source_paths"), list)
            and isinstance(graph.get("source_sha256_by_family"), dict)
            and isinstance(graph.get("native_sha256_by_family"), dict)
            and set(expected_sources) == set(FAMILIES)
            and set(expected_natives) == set(FAMILIES)
            and set(graph["source_sha256_by_family"]) == set(FAMILIES)
            and set(graph["native_sha256_by_family"]) == set(FAMILIES),
            "the actual independent all-family 12-source/five-native graph "
            "is incomplete or substituted")
    source_paths: set[str] = set()
    native_paths: set[str] = set()
    for family in FAMILIES:
        actual_sources = graph["source_sha256_by_family"][family]
        actual_natives = graph["native_sha256_by_family"][family]
        expected_source_paths = expected_sources[family]
        expected_native_entries = expected_natives[family]
        require(isinstance(actual_sources, dict)
                and isinstance(actual_natives, dict)
                and isinstance(expected_source_paths, (tuple, list))
                and isinstance(expected_native_entries, Mapping)
                and set(actual_sources) == set(expected_source_paths)
                and set(actual_natives) == set(expected_native_entries.values())
                and all(_safe_graph_path(path) and valid_sha256(value)
                        for path, value in actual_sources.items())
                and all(_safe_graph_path(path) and valid_sha256(value)
                        for path, value in actual_natives.items())
                and source_paths.isdisjoint(actual_sources)
                and native_paths.isdisjoint(actual_natives),
                "an actual V21-owned family source or mapped native ELF was "
                "omitted, repeated, or substituted: " + family)
        source_paths.update(actual_sources)
        native_paths.update(actual_natives)
    require(len(source_paths) == 12 and len(native_paths) == 5
            and len(graph["source_paths"]) == 12
            and set(graph["source_paths"]) == source_paths,
            "the complete original ownership denominator must remain 12/5")
    return graph


def _verify_family_native_mappings(
    family: str,
    graph: Mapping[str, Any],
    expected_natives: Mapping[str, Any],
) -> dict[str, str]:
    require(type(family) is str and family in FAMILIES,
            "the actual original role requires its own mapped native family")
    verified = _validate_authenticated_native_bridge(
        copy.deepcopy(graph.get("native_sha256_by_family", {})),
        graph,
        expected_natives,
    )
    require(set(verified[family]) == set(expected_natives[family].values())
            and bool(verified[family]),
            "an actual current-family native loader was cross-family, "
            "missing, delegated, or substituted")
    return copy.deepcopy(verified[family])


def _verify_candidate_context_current_graph(
    graph: Mapping[str, Any],
    expected_sources: Mapping[str, Any],
    expected_natives: Mapping[str, Any],
    *,
    read_regular: Callable[[Path, int, str], bytes] | None = None,
) -> dict[str, Any]:
    verified = _validate_current_graph(graph, expected_sources, expected_natives)
    read = _read_regular if read_regular is None else read_regular
    require(callable(read),
            "actual candidate-safe descriptor graph authentication is required")
    for family in FAMILIES:
        _verify_family_native_mappings(family, verified, expected_natives)
        for group in ("source_sha256_by_family", "native_sha256_by_family"):
            for relative, expected_sha256 in verified[group][family].items():
                raw = read(
                    ROOT / relative,
                    MAX_EVIDENCE_BYTES,
                    "candidate-safe authenticated owned graph: " + relative,
                )
                require(type(raw) is bytes and 0 < len(raw)
                        <= MAX_EVIDENCE_BYTES
                        and hashlib.sha256(raw).hexdigest() == expected_sha256,
                        "an actual no-follow owned source or native ELF "
                        "changed inside its legitimate candidate context: "
                        + family + ":" + relative)
                require(group != "native_sha256_by_family"
                        or raw.startswith(b"\x7fELF"),
                        "an authenticated current-family native path no "
                        "longer contains its original ELF: "
                        + family + ":" + relative)
    return verified


def _validate_authenticated_native_bridge(
    candidate: Any,
    graph: Mapping[str, Any],
    expected_natives: Mapping[str, Any],
) -> dict[str, dict[str, str]]:
    require(isinstance(graph, Mapping)
            and isinstance(graph.get("native_sha256_by_family"), dict)
            and isinstance(candidate, dict)
            and isinstance(expected_natives, Mapping)
            and set(candidate) == set(FAMILIES)
            and set(expected_natives) == set(FAMILIES)
            and set(graph["native_sha256_by_family"]) == set(FAMILIES)
            and candidate is not graph["native_sha256_by_family"],
            "the complete independently copied all-family V15 native "
            "bridge is missing, substituted, or aliased to its graph")
    source_native = graph["native_sha256_by_family"]
    seen: set[str] = set()
    seen_family_maps: set[int] = set()
    for family in FAMILIES:
        observed = candidate[family]
        original_family = source_native[family]
        owned = expected_natives[family]
        require(isinstance(observed, dict)
                and isinstance(original_family, dict)
                and isinstance(owned, Mapping)
                and observed is not original_family
                and id(observed) not in seen_family_maps
                and set(observed) == set(owned.values())
                and set(observed) == set(original_family)
                and all(_safe_graph_path(path)
                        and valid_sha256(sha256)
                        and sha256 == original_family[path]
                        for path, sha256 in observed.items())
                and seen.isdisjoint(observed),
                "an actual owned all-family native bridge ELF was missing, "
                "cross-family, forged, mutable, or aliased: " + family)
        seen.update(observed)
        seen_family_maps.add(id(observed))
    require(len(seen) == 5,
            "the original five independently owned native bridges are required")
    detached = copy.deepcopy(candidate)
    require(detached is not candidate
            and detached is not source_native
            and all(detached[family] is not candidate[family]
                    and detached[family] is not source_native[family]
                    for family in FAMILIES)
            and canonical(detached) == canonical(source_native),
            "the complete owned native bridge was not independently "
            "deep-copied before original upstream matching")
    return detached


def _install_authenticated_native_bridge(
    provenance: Any,
    qualification: Any,
    graph: Mapping[str, Any],
    expected_natives: Mapping[str, Any],
) -> dict[str, Any]:
    require(isinstance(provenance, dict)
            and provenance.get("native_sha256_by_family") == {}
            and isinstance(qualification, Mapping)
            and isinstance(qualification.get("native_sha256_by_family"), dict),
            "the immutable V5 empty bridge or actual V15 ownership "
            "qualification was concealed or replaced")
    bridge = _validate_authenticated_native_bridge(
        copy.deepcopy(qualification["native_sha256_by_family"]),
        graph, expected_natives,
    )
    provenance.update(qualification)
    provenance["native_sha256_by_family"] = bridge
    require(provenance["native_sha256_by_family"]
            is not qualification["native_sha256_by_family"]
            and provenance["native_sha256_by_family"]
            is not graph["native_sha256_by_family"]
            and all(provenance["native_sha256_by_family"][family]
                    is not qualification["native_sha256_by_family"][family]
                    and provenance["native_sha256_by_family"][family]
                    is not graph["native_sha256_by_family"][family]
                    for family in FAMILIES),
            "the actual upstream adapter received an aliased native bridge")
    return provenance


def _validate_snapshot(
    family: str, snapshot: Any, graph: Mapping[str, Any],
) -> dict[str, Any]:
    require(family in FAMILIES and isinstance(snapshot, dict)
            and snapshot.get("family") == family
            and snapshot.get("module") == FAMILY_MODULES[family]
            and snapshot.get("source_sha256_by_path")
            == graph["source_sha256_by_family"][family]
            and snapshot.get("native_sha256_by_path")
            == graph["native_sha256_by_family"][family],
            "the actual current family source graph or mapped native engine "
            "does not match both passing independent V21 audits: " + family)
    return snapshot


def _require_real_proof_bytes(
    raw: Any, expected: str, family: str, kind: str,
) -> bytes:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_EVIDENCE_BYTES
            and valid_sha256(expected)
            and hashlib.sha256(raw).hexdigest() == expected,
            "the complete original passing V24 " + kind
            + " archive or independent ownership proof changed: " + family)
    return raw


def _validate_preserved_v13_failure(
    audits: Any, state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    require(isinstance(audits, Mapping)
            and isinstance(audits.get("history"), Mapping)
            and isinstance(audits.get("preserved_v13_failure"), dict),
            "the real first V13 historical-graph preflight failure was concealed")
    failure = audits["preserved_v13_failure"]
    require(audits["history"].get("preserved_v13_first_audit_failure")
            == failure,
            "the genuine first V13 failure was not bound to immutable history")
    for key, expected in V13_FIRST_FAILURE_FIELDS.items():
        observed = failure.get(key)
        require(type(observed) is type(expected) and observed == expected,
                "the genuine first failed V13 audit was replaced, weakened, "
                "or falsely qualified: " + key)
    traceback = {
        key: value for key, value in failure.items()
        if type(key) is str and key.startswith("combined_traceback_")
    }
    require(bool(traceback),
            "the actual combined V13 failure traceback was discarded")
    for key, value in traceback.items():
        if key.endswith("_sha256"):
            require(valid_sha256(value),
                    "the genuine first-failure combined traceback hash changed")
        elif key.endswith("_line_count"):
            require(type(value) is int and value > 0,
                    "the genuine first-failure traceback line count was forged")
    if state is not None:
        incidents = state.get("preserved_incidents")
        require(isinstance(incidents, Mapping)
                and incidents.get("v13_first_owner_preflight_failure") == failure,
                "the genuine V24 proof concealed its actual failed V13 history")
    return failure


def _validate_preserved_v15_failure(
    audits: Any, state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    require(isinstance(audits, Mapping)
            and isinstance(audits.get("history"), Mapping)
            and isinstance(audits.get("preserved_v15_failure"), dict),
            "the real first V15 preserved-failure-codec preflight failure "
            "was concealed")
    failure = audits["preserved_v15_failure"]
    require(audits["history"].get("preserved_v15_first_audit_failure")
            == failure,
            "the genuine first V15 failure was not bound to immutable history")
    for key, expected in V15_FIRST_FAILURE_FIELDS.items():
        observed = failure.get(key)
        require(type(observed) is type(expected) and observed == expected,
                "the genuine first failed V15 audit was replaced, weakened, "
                "disconnected from its real V13 ancestry, or falsely "
                "qualified: " + key)
    traceback = {
        key: value for key, value in failure.items()
        if type(key) is str and key.startswith("combined_traceback_")
    }
    require(bool(traceback),
            "the actual combined V15 failure traceback was discarded")
    for key, value in traceback.items():
        if key.endswith("_sha256"):
            require(valid_sha256(value),
                    "the genuine V15 failure combined traceback hash changed")
        elif key.endswith("_line_count"):
            require(type(value) is int and value > 0,
                    "the genuine V15 failure traceback line count was forged")
    if state is not None:
        incidents = state.get("preserved_incidents")
        require(isinstance(incidents, Mapping)
                and incidents.get("v15_first_owner_preflight_failure")
                == failure,
                "the genuine V24 proof concealed its actual failed V15 history")
    return failure


def _validate_preserved_v17_failure(
    audits: Any, state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    require(isinstance(audits, Mapping)
            and isinstance(audits.get("history"), Mapping)
            and isinstance(audits.get("preserved_v17_failure"), dict),
            "the real first V17 post-owner integrity failure was concealed")
    failure = audits["preserved_v17_failure"]
    require(audits["history"].get("preserved_v17_first_audit_failure")
            == failure,
            "the genuine first V17 failure was not bound to immutable history")
    for key, expected in V17_FIRST_FAILURE_FIELDS.items():
        observed = failure.get(key)
        require(type(observed) is type(expected) and observed == expected,
                "the genuine first V17 integrity failure was replaced, "
                "misrepresented as a current qualification, or given "
                "invented historical native observations: " + key)
    require(not any(key in failure for key in (
        "combined_traceback_sha256", "actual_native_owner_stdout",
        "actual_native_owner_stderr", "actual_native_owner_proofs",
        "actual_native_owner_returncodes", "stdout_capture", "stderr_capture",
    )),
            "the failed V17 controller never preserved its historical native "
            "observations or separate output streams")
    if state is not None:
        incidents = state.get("preserved_incidents")
        require(isinstance(incidents, Mapping)
                and incidents.get("v17_first_owner_postflight_failure")
                == failure,
                "the genuine V24 proof concealed its actual failed V17 history")
    return failure


def _validate_preserved_v19_failure(
    audits: Any, state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    require(isinstance(audits, Mapping)
            and isinstance(audits.get("history"), Mapping)
            and isinstance(audits.get("preserved_v19_failure"), dict),
            "the actual fully durable first V19 publication failure was hidden")
    failure = audits["preserved_v19_failure"]
    require(set(failure) == set(V19_FIRST_FAILURE_FIELDS)
            and audits["history"].get("preserved_v19_first_audit_failure")
            == failure,
            "the exact genuine V19 failed-controller history was replaced "
            "or its durable report was falsely qualified")
    for key, expected in V19_FIRST_FAILURE_FIELDS.items():
        observed = failure.get(key)
        require(type(observed) is type(expected) and observed == expected,
                "the real V19 exclusive-write, actual native owner stream, "
                "failed canonical reread, or external exit was forged: " + key)
    workers = failure["actual_original_native_owner_workers"]
    for family in FAMILIES:
        require(isinstance(workers.get(family), dict),
                "a genuine V19 historical native owner was omitted: " + family)
        for key, expected in V19_FIRST_FAILURE_FIELDS[
            "actual_original_native_owner_workers"
        ][family].items():
            actual = workers[family].get(key)
            require(type(actual) is type(expected) and actual == expected,
                    "a complete real V19 historical native owner stream "
                    "or guard was forged: " + family + ":" + key)
    for actual, expected in zip(
        failure["actual_write_calls"],
        V19_FIRST_FAILURE_FIELDS["actual_write_calls"],
        strict=True,
    ):
        require(isinstance(actual, dict) and set(actual) == set(expected)
                and all(type(actual[key]) is type(value)
                        and actual[key] == value
                        for key, value in expected.items()),
                "the genuine V19 full-write syscall receipt was fabricated")
    require(failure["durable_embedded_document_status"] == "PASS"
            and failure["actual_controller_status"] == "FAIL"
            and failure["exclusive_create_succeeded"] is True
            and failure["file_fsync_succeeded"] is True
            and failure["parent_directory_fsync_succeeded"] is True
            and failure["canonical_reread_succeeded"] is False
            and failure["embedded_pass_qualifies_current_engine"] is False
            and failure["historical_failure_qualifies_current_build"] is False,
            "a genuinely durable but failed V19 report was relabeled as "
            "passing, unpublished, recoverable, or current")
    if state is not None:
        incidents = state.get("preserved_incidents")
        require(isinstance(incidents, Mapping)
                and incidents.get("v19_first_owner_publication_failure")
                == failure,
                "the genuine V24 proof omitted the actual failed V19 publication")
    return failure


def _validate_preserved_v22_proof_failure(
    state: Mapping[str, Any], proof: Any | None = None,
) -> dict[str, Any]:
    require(isinstance(state, Mapping)
            and isinstance(state.get("preserved_incidents"), Mapping)
            and isinstance(state.get("audits"), Mapping)
            and isinstance(state["audits"].get("pins"), Mapping)
            and isinstance(state["audits"].get("history"), Mapping)
            and "preserved_v22_first_audit_failure"
            not in state["audits"]["history"]
            and "v22_first_proof_preflight_failure"
            not in state["audits"]["history"],
            "the complete genuine V22 read-only proof failure was concealed")
    incidents = state["preserved_incidents"]
    failure = incidents.get("v22_first_proof_preflight_failure")
    require(isinstance(failure, dict)
            and set(failure) == V22_FIRST_FAILURE_KEYS
            and len(failure) == 27
            and {
                "v13_first_owner_preflight_failure",
                "v15_first_owner_preflight_failure",
                "v17_first_owner_postflight_failure",
                "v19_first_owner_publication_failure",
                "v22_first_proof_preflight_failure",
            } <= incidents.keys()
            and all(incidents.get(flag) is False
                    for flag in V24_REQUIRED_NONQUALIFYING_FLAGS),
            "the complete 25-field failed V22 document, its two genuine "
            "provenance fields, the five separately preserved failures, "
            "or their genuine historical nonqualification was replaced")
    for key, expected in V22_FIRST_FAILURE_FIELDS.items():
        observed = failure.get(key)
        require(type(observed) is type(expected) and observed == expected,
                "the genuine first V22 read-only proof failure was forged "
                "or falsely qualified: " + key)
    invocation = failure["actual_invocation"]
    require(isinstance(invocation, dict)
            and set(invocation) == {
                "executable", "python_flags", "environment", "exit_code",
                "output_capture", "actual_inline_python_source_lines",
            }
            and invocation.get("executable") == str(PINNED_CPYTHON)
            and invocation.get("python_flags") == ["-I", "-B", "-c"]
            and invocation.get("environment") == {
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
                "PYTHONPATH": str(ROOT),
                "LC_ALL": "C",
                "PATH": "/usr/bin:/bin",
            }
            and type(invocation.get("exit_code")) is int
            and invocation["exit_code"] == 1
            and invocation.get("output_capture") == (
                "complete combined traceback; stdout and stderr "
                "were not separately captured"
            )
            and isinstance(
                invocation.get("actual_inline_python_source_lines"), list,
            )
            and len(invocation["actual_inline_python_source_lines"]) == 25
            and all(type(line) is str and bool(line)
                    for line in invocation[
                        "actual_inline_python_source_lines"
                    ]),
            "the actual isolated failed V22 invocation, its genuine 25 "
            "inline source lines, or its exit was forged")
    traceback = failure["actual_combined_traceback_lines"]
    require(isinstance(traceback, list) and len(traceback) == 24
            and all(type(line) is str and bool(line) for line in traceback),
            "the genuine 24-line combined V22 failure traceback was lost "
            "or replaced with invented separate captures")
    require(failure["frozen_failed_controller"]
            == V22_FAILED_CONTROLLER_FIELDS,
            "the frozen failed V22 source or protocol was falsely offered "
            "as a qualifying current V24 proof")
    audit_pins = state["audits"]["pins"]
    base_sha256 = audit_pins.get("base_report")
    strict_sha256 = audit_pins.get("strict_report")
    require(valid_sha256(base_sha256) and valid_sha256(strict_sha256)
            and base_sha256 != strict_sha256
            and failure["actual_passing_prerequisites"] == {
                "audit_source_sha256": V21_SOURCE_SHA256,
                "audit_protocol_sha256": V21_PROTOCOL_SHA256,
                "base_report_path": (
                    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V21.json"
                ),
                "base_report_sha256": base_sha256,
                "strict_report_path": (
                    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V21.json"
                ),
                "strict_report_sha256": strict_sha256,
                "both_independent_ownership_audits_passed": True,
            },
            "the genuine V22 failure was disconnected from the same "
            "externally supplied independently passing V21 reports")
    require(failure["actual_historical_summary_mismatch"]
            == V22_HISTORICAL_MISMATCH_FIELDS
            and V13_FIRST_FAILURE_FIELDS["failed_stage"]
            == V22_HISTORICAL_MISMATCH_FIELDS[
                "actual_authenticated_v21_value"
            ],
            "the authentic full V13 historical stage or its actual V22 "
            "26-field mismatch was weakened")
    require(failure["independent_follow_up_differential"] == {
                "status": "PASS",
                "validation_scope": (
                    "read-only authentication of the exact published V21 "
                    "reports and all four historical summary shapes only"
                ),
                "read_only_boundary_effects": V22_FOLLOW_UP_READ_ONLY_EFFECTS,
            },
            "the independent genuinely read-only V22 follow-up was changed "
            "or confused with counters the failed controller did not retain")
    if proof is not None:
        expected_summary = getattr(proof, "expected_v22_failure_summary", None)
        require(callable(expected_summary),
                "the authenticated V24 controller must independently "
                "validate the complete genuine first V22 proof failure")
        expected_failure = expected_summary(audit_pins)
        require(type(expected_failure) is dict
                and len(expected_failure) == 27
                and set(expected_failure) == V22_FIRST_FAILURE_KEYS
                and canonical(expected_failure) == canonical(failure),
                "the complete root-bound genuine V22 incident and all 24 "
                "traceback and 25 inline lines must independently match "
                "the authenticated V24 proof controller")
    return failure


def _validate_preserved_v12_first_upstream_failure(
    failure: Any,
    captured: Any,
    *,
    failure_sha256: str = V12_FIRST_UPSTREAM_FAILURE_SHA256,
    failure_bytes: int = V12_FIRST_UPSTREAM_FAILURE_BYTES,
    captured_sha256: str = V12_FIRST_UPSTREAM_CAPTURE_SHA256,
    captured_bytes: int = V12_FIRST_UPSTREAM_CAPTURE_BYTES,
    stdout_sha256: str = V12_FIRST_UPSTREAM_STDOUT_SHA256,
    stdout_bytes: int = V12_FIRST_UPSTREAM_STDOUT_BYTES,
) -> dict[str, Any]:
    require(isinstance(failure, dict) and isinstance(captured, dict)
            and valid_sha256(failure_sha256)
            and valid_sha256(captured_sha256)
            and valid_sha256(stdout_sha256)
            and type(failure_bytes) is int and failure_bytes > 0
            and type(captured_bytes) is int and captured_bytes > 0
            and type(stdout_bytes) is int and stdout_bytes > 0,
            "the complete genuine first V12 upstream failure was concealed")
    for document, expected_sha256, expected_size in (
        (failure, failure_sha256, failure_bytes),
        (captured, captured_sha256, captured_bytes),
    ):
        encoded = canonical(document)
        require(any(len(raw) == expected_size
                    and hashlib.sha256(raw).hexdigest() == expected_sha256
                    for raw in (encoded, encoded + b"\n")),
                "the exact genuine first V12 failure bytes or fully "
                "captured outer output were changed")
    schema = "rebar-postfinal-cpython-full-public-locale-v12-actual-role-failure"
    for document in (failure, captured):
        require(document.get("schema") == schema
                and document.get("status") == "FAIL"
                and document.get("role") == "rust"
                and document.get("source_sha256") == V12_SOURCE_SHA256
                and document.get("protocol_sha256") == V12_PROTOCOL_SHA256
                and document.get("immutable_v6_reference_sha256")
                == V6_REFERENCE_SHA256
                and document.get("synthetic") is False
                and document.get("production_observations_invented") is False
                and document.get("performance") == "NOT MEASURED"
                and document.get("holdout") == "NOT ACCESSED",
                "the actual failed V12 Rust controller was forged, "
                "falsely qualified, or assigned invented observations")
    reports = captured.get("actual_exclusively_preserved_failure_reports")
    require(isinstance(reports, list) and len(reports) == 1
            and isinstance(reports[0], dict)
            and set(reports[0]) == {
                "path", "sha256", "actual_exclusive_publication_receipt",
            }
            and reports[0]["path"] == V12_FIRST_UPSTREAM_FAILURE_RELATIVE
            and reports[0]["sha256"] == failure_sha256,
            "the actual sole exclusively preserved V12 failure was omitted "
            "or replaced with a retry or fabricated destination")
    expected_receipt = {
        "schema": (
            "rebar-postfinal-cpython-full-public-locale-v12-"
            "actual-exclusive-publication-receipt"
        ),
        "path": V12_FIRST_UPSTREAM_FAILURE_RELATIVE,
        "expected_payload_sha256": failure_sha256,
        "expected_payload_bytes": failure_bytes,
        "actual_file_created": True,
        "actual_payload_bytes_written": failure_bytes,
        "actual_write_calls": [{
            "requested_bytes": failure_bytes,
            "returned_bytes": failure_bytes,
        }],
        "actual_file_fsync": True,
        "actual_directory_fsync": True,
        "canonical_reread_succeeded": True,
        "fully_durable_publication": True,
    }
    receipt = reports[0]["actual_exclusive_publication_receipt"]
    require(type(receipt) is dict
            and set(receipt) == set(expected_receipt)
            and canonical(receipt) == canonical(expected_receipt),
            "the exact genuine 11-field V12 exclusive receipt or its "
            "single actual full 6007-byte write was forged")
    expected_failure = dict(captured)
    expected_failure.pop("actual_exclusively_preserved_failure_reports")
    expected_failure["actual_failure_destination"] = (
        V12_FIRST_UPSTREAM_FAILURE_RELATIVE
    )
    require(canonical(failure) == canonical(expected_failure),
            "the exact captured V12 controller output does not preserve "
            "the same exclusively created canonical failure")
    details = captured.get("details")
    require(isinstance(details, dict)
            and details.get("actual_error_type") == "OfficialV12Error"
            and type(details.get("returncode")) is int
            and details["returncode"] == 2,
            "the actual first V12 upstream worker exit was not 2")
    document = details.get("actual_worker_document")
    require(isinstance(document, dict)
            and document.get("schema") == (
                "rebar-postfinal-cpython-full-public-locale-v12-"
                "actual-worker-failure"
            )
            and document.get("status") == "FAIL"
            and document.get("role") == "rust"
            and isinstance(document.get("details"), dict),
            "the complete original first V12 failing worker was discarded")
    nested = document["details"]
    require(nested.get("actual_error_type") == "OfficialV4Error"
            and nested.get("actual_error") == (
                "the current independently owned native bridge is not "
                "authenticated"
            )
            and type(nested.get("completed_original_method_count")) is int
            and nested["completed_original_method_count"] == 0
            and type(nested.get("actual_native_owner_method_guard_checks"))
            is int
            and nested["actual_native_owner_method_guard_checks"] == 0
            and type(nested.get("actual_cached_matcher_method_guard_checks"))
            is int
            and nested["actual_cached_matcher_method_guard_checks"] == 0,
            "the first V12 worker completed no method, native guard, or "
            "matcher before its authentic missing-bridge failure")
    stdout = details.get("stdout")
    stderr = details.get("stderr")
    require(isinstance(stdout, dict)
            and stdout.get("encoding") == "hex"
            and stdout.get("bytes") == stdout_bytes
            and stdout.get("sha256") == stdout_sha256
            and stdout.get("truncated") is False
            and type(stdout.get("complete_hex")) is str,
            "the complete actual first V12 worker stdout was omitted")
    try:
        actual_stdout = bytes.fromhex(stdout["complete_hex"])
    except (TypeError, ValueError) as error:
        raise OfficialV15Error(
            "the genuine original V12 worker stdout is not complete hex",
        ) from error
    require(len(actual_stdout) == stdout_bytes
            and hashlib.sha256(actual_stdout).hexdigest() == stdout_sha256
            and canonical(document) + b"\n" == actual_stdout
            and isinstance(stderr, dict)
            and stderr.get("encoding") == "hex"
            and stderr.get("bytes") == 0
            and stderr.get("sha256") == V12_FIRST_UPSTREAM_STDERR_SHA256
            and stderr.get("complete_hex") == ""
            and stderr.get("truncated") is False,
            "the authentic 1221-byte failed V12 worker or genuine empty "
            "stderr was forged or separately invented")
    return {
        "source_path": V12_FIRST_UPSTREAM_FAILURE_RELATIVE,
        "sha256": failure_sha256,
        "bytes": failure_bytes,
        "captured_output_path": V12_FIRST_UPSTREAM_CAPTURE_RELATIVE,
        "captured_output_sha256": captured_sha256,
        "captured_output_bytes": captured_bytes,
        "v12_source_sha256": V12_SOURCE_SHA256,
        "v12_protocol_sha256": V12_PROTOCOL_SHA256,
        "schema": schema,
        "status": "FAIL",
        "role": "rust",
        "worker_returncode": 2,
        "worker_stdout_sha256": stdout_sha256,
        "worker_stdout_bytes": stdout_bytes,
        "worker_stderr_sha256": V12_FIRST_UPSTREAM_STDERR_SHA256,
        "completed_original_method_count": 0,
        "actual_native_owner_method_guard_checks": 0,
        "actual_cached_matcher_method_guard_checks": 0,
        "actual_exclusive_publication_receipt": copy.deepcopy(receipt),
        "historical_failure_qualifies_current_engine": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def _authenticate_preserved_v12_first_upstream_failure() -> dict[str, Any]:
    _frozen(V12_SOURCE_RELATIVE, V12_SOURCE_SHA256)
    _frozen(V12_PROTOCOL_RELATIVE, V12_PROTOCOL_SHA256)
    decoded: list[dict[str, Any]] = []
    for relative, expected_sha256, expected_size in (
        (V12_FIRST_UPSTREAM_FAILURE_RELATIVE,
         V12_FIRST_UPSTREAM_FAILURE_SHA256,
         V12_FIRST_UPSTREAM_FAILURE_BYTES),
        (V12_FIRST_UPSTREAM_CAPTURE_RELATIVE,
         V12_FIRST_UPSTREAM_CAPTURE_SHA256,
         V12_FIRST_UPSTREAM_CAPTURE_BYTES),
    ):
        raw = _read_regular(ROOT / relative, MAX_EVIDENCE_BYTES, relative)
        require(len(raw) == expected_size
                and hashlib.sha256(raw).hexdigest() == expected_sha256,
                "the root-published immutable first V12 failure changed: "
                + relative)
        document = json.loads(raw)
        require(isinstance(document, dict)
                and raw in (canonical(document), canonical(document) + b"\n"),
                "the authentic first V12 failure lost its exact canonical "
                "production bytes: " + relative)
        decoded.append(document)
    return _validate_preserved_v12_first_upstream_failure(
        decoded[0], decoded[1],
    )


def _validate_preserved_v13_first_upstream_failure(
    failure: Any,
    captured: Any,
    *,
    failure_sha256: str = V13_FIRST_UPSTREAM_FAILURE_SHA256,
    failure_bytes: int = V13_FIRST_UPSTREAM_FAILURE_BYTES,
    captured_sha256: str = V13_FIRST_UPSTREAM_CAPTURE_SHA256,
    captured_bytes: int = V13_FIRST_UPSTREAM_CAPTURE_BYTES,
    stdout_sha256: str = V13_FIRST_UPSTREAM_STDOUT_SHA256,
    stdout_bytes: int = V13_FIRST_UPSTREAM_STDOUT_BYTES,
) -> dict[str, Any]:
    require(isinstance(failure, dict) and isinstance(captured, dict)
            and valid_sha256(failure_sha256)
            and valid_sha256(captured_sha256)
            and valid_sha256(stdout_sha256)
            and type(failure_bytes) is int and failure_bytes > 0
            and type(captured_bytes) is int and captured_bytes > 0
            and type(stdout_bytes) is int and stdout_bytes > 0,
            "the complete genuine first V13 upstream failure was concealed")
    for document, expected_sha256, expected_size in (
        (failure, failure_sha256, failure_bytes),
        (captured, captured_sha256, captured_bytes),
    ):
        encoded = canonical(document)
        require(any(len(raw) == expected_size
                    and hashlib.sha256(raw).hexdigest() == expected_sha256
                    for raw in (encoded, encoded + b"\n")),
                "the exact genuine first V13 failure bytes or fully "
                "captured outer output were changed")
    schema = "rebar-postfinal-cpython-full-public-locale-v13-actual-role-failure"
    for document in (failure, captured):
        require(document.get("schema") == schema
                and document.get("status") == "FAIL"
                and document.get("role") == "rust"
                and document.get("source_sha256") == V13_SOURCE_SHA256
                and document.get("protocol_sha256") == V13_PROTOCOL_SHA256
                and document.get("immutable_v6_reference_sha256")
                == V6_REFERENCE_SHA256
                and document.get("synthetic") is False
                and document.get("production_observations_invented") is False
                and document.get("performance") == "NOT MEASURED"
                and document.get("holdout") == "NOT ACCESSED",
                "the actual failed V13 Rust controller was forged, "
                "falsely qualified, or assigned invented observations")
    reports = captured.get("actual_exclusively_preserved_failure_reports")
    require(isinstance(reports, list) and len(reports) == 1
            and isinstance(reports[0], dict)
            and set(reports[0]) == {
                "path", "sha256", "actual_exclusive_publication_receipt",
            }
            and reports[0]["path"] == V13_FIRST_UPSTREAM_FAILURE_RELATIVE
            and reports[0]["sha256"] == failure_sha256,
            "the actual sole exclusively preserved V13 failure was omitted "
            "or replaced with a retry or fabricated destination")
    expected_receipt = {
        "schema": (
            "rebar-postfinal-cpython-full-public-locale-v13-"
            "actual-exclusive-publication-receipt"
        ),
        "path": V13_FIRST_UPSTREAM_FAILURE_RELATIVE,
        "expected_payload_sha256": failure_sha256,
        "expected_payload_bytes": failure_bytes,
        "actual_file_created": True,
        "actual_payload_bytes_written": failure_bytes,
        "actual_write_calls": [{
            "requested_bytes": failure_bytes,
            "returned_bytes": failure_bytes,
        }],
        "actual_file_fsync": True,
        "actual_directory_fsync": True,
        "canonical_reread_succeeded": True,
        "fully_durable_publication": True,
    }
    receipt = reports[0]["actual_exclusive_publication_receipt"]
    require(type(receipt) is dict
            and set(receipt) == set(expected_receipt)
            and canonical(receipt) == canonical(expected_receipt),
            "the exact genuine 11-field V13 exclusive receipt or its "
            "single actual full 9479-byte write was forged")
    expected_failure = dict(captured)
    expected_failure.pop("actual_exclusively_preserved_failure_reports")
    expected_failure["actual_failure_destination"] = (
        V13_FIRST_UPSTREAM_FAILURE_RELATIVE
    )
    require(canonical(failure) == canonical(expected_failure),
            "the exact captured V13 controller output does not preserve "
            "the same exclusively created canonical failure")
    details = captured.get("details")
    require(isinstance(details, dict)
            and details.get("actual_error_type") == "OfficialV13Error"
            and type(details.get("returncode")) is int
            and details["returncode"] == 2,
            "the actual first V13 upstream worker exit was not 2")
    document = details.get("actual_worker_document")
    require(isinstance(document, dict)
            and document.get("schema") == (
                "rebar-postfinal-cpython-full-public-locale-v13-"
                "actual-worker-failure"
            )
            and document.get("status") == "FAIL"
            and document.get("role") == "rust"
            and isinstance(document.get("details"), dict),
            "the complete original first V13 failing worker was discarded")
    nested = document["details"]
    require(nested.get("actual_error_type") == "ImportError"
            and nested.get("actual_error") == (
                "stage-07 blocked unowned matching import: "
                "re"
            )
            and type(nested.get("completed_original_method_count")) is int
            and nested["completed_original_method_count"] == 0
            and type(nested.get("actual_native_owner_method_guard_checks"))
            is int
            and nested["actual_native_owner_method_guard_checks"] == 0
            and type(nested.get("actual_cached_matcher_method_guard_checks"))
            is int
            and nested["actual_cached_matcher_method_guard_checks"] == 0,
            "the first V13 worker completed no method, native guard, or "
            "matcher before its authentic missing-bridge failure")
    stdout = details.get("stdout")
    stderr = details.get("stderr")
    require(isinstance(stdout, dict)
            and stdout.get("encoding") == "hex"
            and stdout.get("bytes") == stdout_bytes
            and stdout.get("sha256") == stdout_sha256
            and stdout.get("truncated") is False
            and type(stdout.get("complete_hex")) is str,
            "the complete actual first V13 worker stdout was omitted")
    try:
        actual_stdout = bytes.fromhex(stdout["complete_hex"])
    except (TypeError, ValueError) as error:
        raise OfficialV15Error(
            "the genuine original V13 worker stdout is not complete hex",
        ) from error
    require(len(actual_stdout) == stdout_bytes
            and hashlib.sha256(actual_stdout).hexdigest() == stdout_sha256
            and canonical(document) + b"\n" == actual_stdout
            and isinstance(stderr, dict)
            and stderr.get("encoding") == "hex"
            and stderr.get("bytes") == 0
            and stderr.get("sha256") == V13_FIRST_UPSTREAM_STDERR_SHA256
            and stderr.get("complete_hex") == ""
            and stderr.get("truncated") is False,
            "the authentic 2089-byte failed V13 worker or genuine empty "
            "stderr was forged or separately invented")
    return {
        "source_path": V13_FIRST_UPSTREAM_FAILURE_RELATIVE,
        "sha256": failure_sha256,
        "bytes": failure_bytes,
        "captured_output_path": V13_FIRST_UPSTREAM_CAPTURE_RELATIVE,
        "captured_output_sha256": captured_sha256,
        "captured_output_bytes": captured_bytes,
        "v13_source_sha256": V13_SOURCE_SHA256,
        "v13_protocol_sha256": V13_PROTOCOL_SHA256,
        "schema": schema,
        "status": "FAIL",
        "role": "rust",
        "worker_returncode": 2,
        "worker_stdout_sha256": stdout_sha256,
        "worker_stdout_bytes": stdout_bytes,
        "worker_stderr_sha256": V13_FIRST_UPSTREAM_STDERR_SHA256,
        "completed_original_method_count": 0,
        "actual_native_owner_method_guard_checks": 0,
        "actual_cached_matcher_method_guard_checks": 0,
        "actual_exclusive_publication_receipt": copy.deepcopy(receipt),
        "historical_failure_qualifies_current_engine": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def _authenticate_preserved_v13_first_upstream_failure() -> dict[str, Any]:
    _frozen(V13_SOURCE_RELATIVE, V13_SOURCE_SHA256)
    _frozen(V13_PROTOCOL_RELATIVE, V13_PROTOCOL_SHA256)
    decoded: list[dict[str, Any]] = []
    for relative, expected_sha256, expected_size in (
        (V13_FIRST_UPSTREAM_FAILURE_RELATIVE,
         V13_FIRST_UPSTREAM_FAILURE_SHA256,
         V13_FIRST_UPSTREAM_FAILURE_BYTES),
        (V13_FIRST_UPSTREAM_CAPTURE_RELATIVE,
         V13_FIRST_UPSTREAM_CAPTURE_SHA256,
         V13_FIRST_UPSTREAM_CAPTURE_BYTES),
    ):
        raw = _read_regular(ROOT / relative, MAX_EVIDENCE_BYTES, relative)
        require(len(raw) == expected_size
                and hashlib.sha256(raw).hexdigest() == expected_sha256,
                "the root-published immutable first V13 failure changed: "
                + relative)
        document = json.loads(raw)
        require(isinstance(document, dict)
                and raw in (canonical(document), canonical(document) + b"\n"),
                "the authentic first V13 failure lost its exact canonical "
                "production bytes: " + relative)
        decoded.append(document)
    return _validate_preserved_v13_first_upstream_failure(
        decoded[0], decoded[1],
    )


def _validate_preserved_v14_first_upstream_failure(
    failure: Any,
    captured: Any,
    *,
    failure_sha256: str = V14_FIRST_UPSTREAM_FAILURE_SHA256,
    failure_bytes: int = V14_FIRST_UPSTREAM_FAILURE_BYTES,
    captured_sha256: str = V14_FIRST_UPSTREAM_CAPTURE_SHA256,
    captured_bytes: int = V14_FIRST_UPSTREAM_CAPTURE_BYTES,
    stdout_sha256: str = V14_FIRST_UPSTREAM_STDOUT_SHA256,
    stdout_bytes: int = V14_FIRST_UPSTREAM_STDOUT_BYTES,
) -> dict[str, Any]:
    require(isinstance(failure, dict) and isinstance(captured, dict)
            and valid_sha256(failure_sha256)
            and valid_sha256(captured_sha256)
            and valid_sha256(stdout_sha256)
            and type(failure_bytes) is int and failure_bytes > 0
            and type(captured_bytes) is int and captured_bytes > 0
            and type(stdout_bytes) is int and stdout_bytes > 0,
            "the complete genuine first V14 upstream failure was concealed")
    for document, expected_sha256, expected_size in (
        (failure, failure_sha256, failure_bytes),
        (captured, captured_sha256, captured_bytes),
    ):
        encoded = canonical(document)
        require(any(len(raw) == expected_size
                    and hashlib.sha256(raw).hexdigest() == expected_sha256
                    for raw in (encoded, encoded + b"\n")),
                "the exact genuine first V14 failure bytes or fully "
                "captured outer output were changed")
    schema = "rebar-postfinal-cpython-full-public-locale-v14-actual-role-failure"
    for document in (failure, captured):
        require(document.get("schema") == schema
                and document.get("status") == "FAIL"
                and document.get("role") == "rust"
                and document.get("source_sha256") == V14_SOURCE_SHA256
                and document.get("protocol_sha256") == V14_PROTOCOL_SHA256
                and document.get("immutable_v6_reference_sha256")
                == V6_REFERENCE_SHA256
                and document.get("synthetic") is False
                and document.get("production_observations_invented") is False
                and document.get("performance") == "NOT MEASURED"
                and document.get("holdout") == "NOT ACCESSED",
                "the actual failed V14 Rust controller was forged, "
                "falsely qualified, or assigned invented observations")
    reports = captured.get("actual_exclusively_preserved_failure_reports")
    require(isinstance(reports, list) and len(reports) == 1
            and isinstance(reports[0], dict)
            and set(reports[0]) == {
                "path", "sha256", "actual_exclusive_publication_receipt",
            }
            and reports[0]["path"] == V14_FIRST_UPSTREAM_FAILURE_RELATIVE
            and reports[0]["sha256"] == failure_sha256,
            "the actual sole exclusively preserved V14 failure was omitted "
            "or replaced with a retry or fabricated destination")
    expected_receipt = {
        "schema": (
            "rebar-postfinal-cpython-full-public-locale-v14-"
            "actual-exclusive-publication-receipt"
        ),
        "path": V14_FIRST_UPSTREAM_FAILURE_RELATIVE,
        "expected_payload_sha256": failure_sha256,
        "expected_payload_bytes": failure_bytes,
        "actual_file_created": True,
        "actual_payload_bytes_written": failure_bytes,
        "actual_write_calls": [{
            "requested_bytes": failure_bytes,
            "returned_bytes": failure_bytes,
        }],
        "actual_file_fsync": True,
        "actual_directory_fsync": True,
        "canonical_reread_succeeded": True,
        "fully_durable_publication": True,
    }
    receipt = reports[0]["actual_exclusive_publication_receipt"]
    require(type(receipt) is dict
            and set(receipt) == set(expected_receipt)
            and canonical(receipt) == canonical(expected_receipt),
            "the exact genuine 11-field V14 exclusive receipt or its "
            "single actual full 9023-byte write was forged")
    expected_failure = dict(captured)
    expected_failure.pop("actual_exclusively_preserved_failure_reports")
    expected_failure["actual_failure_destination"] = (
        V14_FIRST_UPSTREAM_FAILURE_RELATIVE
    )
    require(canonical(failure) == canonical(expected_failure),
            "the exact captured V14 controller output does not preserve "
            "the same exclusively created canonical failure")
    details = captured.get("details")
    require(isinstance(details, dict)
            and details.get("actual_error_type") == "OfficialV14Error"
            and type(details.get("returncode")) is int
            and details["returncode"] == 2,
            "the actual first V14 upstream worker exit was not 2")
    document = details.get("actual_worker_document")
    require(isinstance(document, dict)
            and document.get("schema") == (
                "rebar-postfinal-cpython-full-public-locale-v14-"
                "actual-worker-failure"
            )
            and document.get("status") == "FAIL"
            and document.get("role") == "rust"
            and isinstance(document.get("details"), dict),
            "the complete original first V14 failing worker was discarded")
    nested = document["details"]
    require(nested.get("actual_error_type") == "ProofV11Error"
            and nested.get("actual_error") == (
                "the V11 correctness controller must never import a candidate"
            )
            and type(nested.get("completed_original_method_count")) is int
            and nested["completed_original_method_count"] == 0
            and type(nested.get("actual_native_owner_method_guard_checks"))
            is int
            and nested["actual_native_owner_method_guard_checks"] == 0
            and type(nested.get("actual_cached_matcher_method_guard_checks"))
            is int
            and nested["actual_cached_matcher_method_guard_checks"] == 0,
            "the first V14 worker completed no method, native guard, or "
            "matcher before its authentic candidate-context snapshot failure")
    stdout = details.get("stdout")
    stderr = details.get("stderr")
    require(isinstance(stdout, dict)
            and stdout.get("encoding") == "hex"
            and stdout.get("bytes") == stdout_bytes
            and stdout.get("sha256") == stdout_sha256
            and stdout.get("truncated") is False
            and type(stdout.get("complete_hex")) is str,
            "the complete actual first V14 worker stdout was omitted")
    try:
        actual_stdout = bytes.fromhex(stdout["complete_hex"])
    except (TypeError, ValueError) as error:
        raise OfficialV15Error(
            "the genuine original V14 worker stdout is not complete hex",
        ) from error
    require(len(actual_stdout) == stdout_bytes
            and hashlib.sha256(actual_stdout).hexdigest() == stdout_sha256
            and canonical(document) + b"\n" == actual_stdout
            and isinstance(stderr, dict)
            and stderr.get("encoding") == "hex"
            and stderr.get("bytes") == 0
            and stderr.get("sha256") == V14_FIRST_UPSTREAM_STDERR_SHA256
            and stderr.get("complete_hex") == ""
            and stderr.get("truncated") is False,
            "the authentic 1975-byte failed V14 worker or genuine empty "
            "stderr was forged or separately invented")
    return {
        "source_path": V14_FIRST_UPSTREAM_FAILURE_RELATIVE,
        "sha256": failure_sha256,
        "bytes": failure_bytes,
        "captured_output_path": V14_FIRST_UPSTREAM_CAPTURE_RELATIVE,
        "captured_output_sha256": captured_sha256,
        "captured_output_bytes": captured_bytes,
        "v14_source_sha256": V14_SOURCE_SHA256,
        "v14_protocol_sha256": V14_PROTOCOL_SHA256,
        "schema": schema,
        "status": "FAIL",
        "role": "rust",
        "worker_returncode": 2,
        "worker_stdout_sha256": stdout_sha256,
        "worker_stdout_bytes": stdout_bytes,
        "worker_stderr_sha256": V14_FIRST_UPSTREAM_STDERR_SHA256,
        "completed_original_method_count": 0,
        "actual_native_owner_method_guard_checks": 0,
        "actual_cached_matcher_method_guard_checks": 0,
        "actual_exclusive_publication_receipt": copy.deepcopy(receipt),
        "historical_failure_qualifies_current_engine": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def _authenticate_preserved_v14_first_upstream_failure() -> dict[str, Any]:
    _frozen(V14_SOURCE_RELATIVE, V14_SOURCE_SHA256)
    _frozen(V14_PROTOCOL_RELATIVE, V14_PROTOCOL_SHA256)
    decoded: list[dict[str, Any]] = []
    for relative, expected_sha256, expected_size in (
        (V14_FIRST_UPSTREAM_FAILURE_RELATIVE,
         V14_FIRST_UPSTREAM_FAILURE_SHA256,
         V14_FIRST_UPSTREAM_FAILURE_BYTES),
        (V14_FIRST_UPSTREAM_CAPTURE_RELATIVE,
         V14_FIRST_UPSTREAM_CAPTURE_SHA256,
         V14_FIRST_UPSTREAM_CAPTURE_BYTES),
    ):
        raw = _read_regular(ROOT / relative, MAX_EVIDENCE_BYTES, relative)
        require(len(raw) == expected_size
                and hashlib.sha256(raw).hexdigest() == expected_sha256,
                "the root-published immutable first V14 failure changed: "
                + relative)
        document = json.loads(raw)
        require(isinstance(document, dict)
                and raw in (canonical(document), canonical(document) + b"\n"),
                "the authentic first V14 failure lost its exact canonical "
                "production bytes: " + relative)
        decoded.append(document)
    return _validate_preserved_v14_first_upstream_failure(
        decoded[0], decoded[1],
    )


def authenticate_candidate_prerequisites(
    selected: str, supplied: Mapping[str, Any],
) -> dict[str, Any]:
    pins = _candidate_pin_values(selected, supplied)
    v21, v24 = _load_candidate_modules(pins)
    audits = v21.authenticate_qualified_audits(
        pins["base_report"], pins["strict_report"],
    )
    require(isinstance(audits, dict)
            and set(audits) == {
                "base", "strict", "graph", "pins", "history",
                "preserved_zig_failure", "preserved_v13_failure",
                "preserved_v15_failure", "preserved_v17_failure",
                "preserved_v19_failure", "owner",
            }
            and isinstance(audits.get("pins"), Mapping)
            and audits["pins"].get("base_report") == pins["base_report"]
            and audits["pins"].get("strict_report") == pins["strict_report"]
            and audits["pins"].get("audit_source") == pins["audit_source"]
            and audits["pins"].get("audit_protocol") == pins["audit_protocol"],
            "both separately published complete real V21 owner and strict "
            "reports must authenticate the same exact source and protocol")
    preserved_v13_failure = _validate_preserved_v13_failure(audits)
    preserved_v15_failure = _validate_preserved_v15_failure(audits)
    preserved_v17_failure = _validate_preserved_v17_failure(audits)
    preserved_v19_failure = _validate_preserved_v19_failure(audits)
    graph = _validate_current_graph(
        audits.get("graph"), v21.OWNED_SOURCE_PATHS, v21.OWNED_NATIVE_PATHS,
    )
    require(v21.snapshot_current_graph() == graph,
            "the full independent owned 12-source/five-native graph changed")
    native_bridge = _validate_authenticated_native_bridge(
        copy.deepcopy(graph["native_sha256_by_family"]),
        graph,
        v21.OWNED_NATIVE_PATHS,
    )
    preserved_v12_failure = _authenticate_preserved_v12_first_upstream_failure()
    preserved_v13_upstream_failure = (
        _authenticate_preserved_v13_first_upstream_failure()
    )
    preserved_v14_upstream_failure = (
        _authenticate_preserved_v14_first_upstream_failure()
    )
    qualification: dict[str, dict[str, Any]] = {}
    states: dict[str, dict[str, Any]] = {}
    common_pins = {
        key: pins[key]
        for key in ("audit_source", "audit_protocol", "base_report", "strict_report")
    }
    for family in _chosen(selected):
        state = v24.preflight(family, common_pins)
        require(isinstance(state, dict)
                and set(state) == {
                    "v21", "owner", "v8", "audits", "snapshot",
                    "history", "preserved_incidents", "controller",
                    "parent_environment",
                }
                and state.get("v21") is v21
                and isinstance(state.get("audits"), Mapping)
                and state["audits"].get("graph") == graph
                and callable(getattr(state.get("v8"), "load_contract", None)),
                "the genuine fresh V24 original proof was not bound to the "
                "same passing current V21 all-family graph: " + family)
        _validate_preserved_v13_failure(audits, state)
        _validate_preserved_v15_failure(audits, state)
        _validate_preserved_v17_failure(audits, state)
        _validate_preserved_v19_failure(audits, state)
        preserved_v22_failure = _validate_preserved_v22_proof_failure(
            state, v24,
        )
        _validate_preserved_v13_failure(state["audits"], state)
        _validate_preserved_v15_failure(state["audits"], state)
        _validate_preserved_v17_failure(state["audits"], state)
        _validate_preserved_v19_failure(state["audits"], state)
        snapshot = _validate_snapshot(family, state.get("snapshot"), graph)
        contract = state["v8"].load_contract()
        edge = v24.authenticate_qualified_edge(family, state, contract)
        deep = v24.authenticate_qualified_deep(family, state, contract)
        require(isinstance(edge, tuple) and len(edge) == 4
                and isinstance(deep, tuple) and len(deep) == 4,
                "the actual complete original edge/deep archives and their "
                "independent owner wrappers are required: " + family)
        edge_original, edge_descriptor, edge_raw, edge_wrapper = edge
        deep_original, deep_descriptor, deep_raw, deep_wrapper = deep
        _require_real_proof_bytes(
            edge_raw, pins[family + "_edge_archive"], family, "edge",
        )
        _require_real_proof_bytes(
            edge_wrapper, pins[family + "_edge_proof"], family, "edge owner",
        )
        _require_real_proof_bytes(
            deep_raw, pins[family + "_deep_archive"], family, "deep",
        )
        _require_real_proof_bytes(
            deep_wrapper, pins[family + "_deep_proof"], family, "deep owner",
        )
        require(isinstance(edge_original, Mapping)
                and isinstance(deep_original, Mapping)
                and isinstance(edge_descriptor, Mapping)
                and isinstance(deep_descriptor, Mapping)
                and edge_original.get("failed") == 0
                and deep_original.get("public_mismatch_count") == 0,
                "the actual original 223,198/49 edge and 393/64 deep "
                "observations did not both pass: " + family)
        require(v21.snapshot_current_graph() == graph,
                "the real all-family native graph changed during complete "
                "original edge/deep authentication: " + family)
        qualification[family] = {
            "family": family,
            "candidate_module": FAMILY_MODULES[family],
            "edge_archive_sha256": pins[family + "_edge_archive"],
            "edge_proof_sha256": pins[family + "_edge_proof"],
            "edge_checks": EDGE_CHECKS,
            "edge_categories": EDGE_CATEGORIES,
            "deep_archive_sha256": pins[family + "_deep_archive"],
            "deep_proof_sha256": pins[family + "_deep_proof"],
            "deep_checks": DEEP_CHECKS,
            "deep_seeded_cases": DEEP_SEEDED_CASES,
            "edge_qualification": dict(edge_descriptor),
            "deep_qualification": dict(deep_descriptor),
            "preserved_v22_first_proof_preflight_failure": copy.deepcopy(
                preserved_v22_failure,
            ),
            "source_sha256_by_path": dict(snapshot["source_sha256_by_path"]),
            "native_sha256_by_path": dict(snapshot["native_sha256_by_path"]),
            "all_family_audit_qualified": True,
            "campaign_qualified": True,
            "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED",
        }
        states[family] = dict(state)
    return {
        "candidate_prerequisite_sha256": pins,
        "actual_v21_base_report_sha256": pins["base_report"],
        "actual_v21_strict_report_sha256": pins["strict_report"],
        "v21_source_sha256": pins["audit_source"],
        "v21_protocol_sha256": pins["audit_protocol"],
        "v24_source_sha256": pins["proof_source"],
        "v24_protocol_sha256": pins["proof_protocol"],
        "audits": audits,
        "graph": graph,
        "native_sha256_by_family": native_bridge,
        "preserved_v12_first_upstream_failure": preserved_v12_failure,
        "preserved_v13_first_upstream_failure": preserved_v13_upstream_failure,
        "preserved_v14_first_upstream_failure": preserved_v14_upstream_failure,
        "preserved_v13_first_audit_failure": dict(preserved_v13_failure),
        "preserved_v15_first_audit_failure": dict(preserved_v15_failure),
        "preserved_v17_first_audit_failure": copy.deepcopy(
            preserved_v17_failure,
        ),
        "preserved_v19_first_audit_failure": copy.deepcopy(
            preserved_v19_failure,
        ),
        "qualified_family_proofs": qualification,
        "family_states": states,
    }


def _read_frozen_reference(provenance: Mapping[str, Any]) -> dict[str, Any]:
    require(original is not None,
            "the exact authenticated V6 upstream reference validator is required")
    path, references = original._read_reference(
        V6_REFERENCE_SHA256, provenance, V6_SOURCE_SHA256,
    )
    require(path == V6_REFERENCE_RELATIVE
            and isinstance(references, dict)
            and tuple(references) == REFERENCE_LABELS,
            "only the genuine independently executed frozen double V6 "
            "reference can qualify an official V15 candidate")
    matrix = provenance["official"]["public_method_matrix"]
    require(isinstance(matrix, list) and len(matrix) == PUBLIC_METHODS,
            "the real complete original ordered 152-method matrix is missing")
    for label in REFERENCE_LABELS:
        original.original._validate_role("stdlib", references[label], matrix)
        role = references[label]
        require(role.get("applicable") == 151
                and role.get("passed") == 151
                and role.get("named_private_debug_skips") == 1,
                "an actual immutable V6 reference changed its sole authentic "
                "private debug-only upstream skip: " + label)
    first = original.original._status_vector(references["reference_a"]["records"])
    second = original.original._status_vector(references["reference_b"]["records"])
    require(len(first) == PUBLIC_METHODS and first == second,
            "the two authentic complete frozen V6 upstream references disagree")
    return references


OWNER_BOOTSTRAP = (
    "import sys;sys.path.insert(0,sys.argv[1]);"
    "from tools.postfinal_cpython_locale_oracle_v15 import native_owner_entry;"
    "raise SystemExit(native_owner_entry(sys.argv[2],sys.argv[3],sys.argv[4],"
    "sys.argv[5],sys.argv[6],sys.argv[7]))"
)


def _isolated_owner_environment() -> dict[str, str]:
    return {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONPATH": str(ROOT),
        "PATH": "/usr/bin:/bin",
    }


def native_owner_entry(
    family: str,
    source_sha256: str,
    protocol_sha256: str,
    audit_source_sha256: str,
    audit_protocol_sha256: str,
    encoded_native: str,
) -> int:
    try:
        verify_runtime()
        require(family in FAMILIES
                and valid_sha256(source_sha256)
                and protocol_sha256 == PROTOCOL_SHA256
                and audit_source_sha256 == V21_SOURCE_SHA256
                and audit_protocol_sha256 == V21_PROTOCOL_SHA256
                and not any(name == "candidates"
                            or name.startswith("candidates.")
                            for name in sys.modules),
                "an independently isolated candidate-free V21 owner helper "
                "requires the exact frozen V15 and V21 controllers")
        _frozen(SOURCE_RELATIVE, source_sha256)
        _frozen(PROTOCOL_RELATIVE, PROTOCOL_SHA256)
        _frozen(V21_SOURCE_RELATIVE, audit_source_sha256)
        _frozen(V21_PROTOCOL_RELATIVE, audit_protocol_sha256)
        expected = json.loads(encoded_native)
        require(isinstance(expected, dict)
                and all(_safe_graph_path(path) and valid_sha256(value)
                        for path, value in expected.items()),
                "a complete genuine current mapped native graph is required")
        v21 = importlib.import_module(
            "tools.postfinal_independent_engine_audit_v21",
        )
        require(v21.SCHEMA == "rebar-postfinal-independent-engine-audit-v21"
                and v21.SOURCE_RELATIVE == V21_SOURCE_RELATIVE
                and v21.PROTOCOL_RELATIVE == V21_PROTOCOL_RELATIVE
                and v21.PROTOCOL_SHA256 == audit_protocol_sha256
                and Path(v21.__file__).resolve() == ROOT / V21_SOURCE_RELATIVE,
                "the isolated genuine method-adjacent V21 owner was substituted")
        observed = v21.run_native_worker(family, expected)
        validated = v21.validate_native_owner(observed, family, expected)
        require(isinstance(validated, dict) and validated == observed
                and not any(name == "candidates"
                            or name.startswith("candidates.")
                            for name in sys.modules),
                "the genuine independently isolated V21 native owner failed "
                "or imported a candidate")
        document = {
            "schema": SCHEMA + "-actual-isolated-method-native-owner",
            "status": "PASS",
            "family": family,
            "source_sha256": source_sha256,
            "protocol_sha256": protocol_sha256,
            "audit_source_sha256": audit_source_sha256,
            "audit_protocol_sha256": audit_protocol_sha256,
            "native_sha256_by_path": expected,
            "native_owner": validated,
            "candidate_imports": 0,
            "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED",
        }
    except (Exception, MemoryError) as error:
        print(json.dumps({
            "schema": SCHEMA + "-actual-isolated-method-native-owner-failure",
            "status": "FAIL",
            "family": family,
            "actual_error_type": type(error).__name__,
            "reason": str(error),
            "production_observations_invented": False,
            "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED",
        }, ensure_ascii=True, allow_nan=False,
            sort_keys=True, separators=(",", ":")), file=sys.stderr)
        return 2
    print(json.dumps(document, ensure_ascii=True, allow_nan=False,
                     sort_keys=True, separators=(",", ":")))
    return 0


def _observe_native_owner(
    family: str,
    graph: Mapping[str, Any],
    method: str,
    phase: str,
    *,
    source_sha256: str,
    pins: Mapping[str, str],
) -> dict[str, Any]:
    require(inventory is not None and family in FAMILIES
            and type(method) is str and bool(method)
            and phase in ("before", "after")
            and valid_sha256(source_sha256)
            and pins.get("audit_source") == V21_SOURCE_SHA256
            and pins.get("audit_protocol") == V21_PROTOCOL_SHA256,
            "a genuine method-adjacent native owner and phase are required")
    native = graph["native_sha256_by_family"][family]
    command = [
        str(PINNED_CPYTHON), "-I", "-B", "-c", OWNER_BOOTSTRAP,
        str(ROOT), family, source_sha256, PROTOCOL_SHA256,
        pins["audit_source"], pins["audit_protocol"],
        canonical(dict(native)).decode("ascii"),
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=str(ROOT),
            env=_isolated_owner_environment(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=300,
        )
    except subprocess.TimeoutExpired as error:
        failure = _timeout_worker_failure(
            family,
            error,
            message="the isolated real method-adjacent V21 native owner "
            "timed out: " + method + ":" + phase,
            details={
                "active_original_method": method,
                "active_original_method_phase": phase,
            },
        )
        failure.details["actual_native_owner_stdout"] = failure.details["stdout"]
        failure.details["actual_native_owner_stderr"] = failure.details["stderr"]
        raise failure from error
    details = {
        "active_original_method": method,
        "active_original_method_phase": phase,
        "actual_native_owner_returncode": completed.returncode,
        "actual_native_owner_signal": (
            -completed.returncode if completed.returncode < 0 else None
        ),
        "actual_native_owner_stdout": (
            _complete_captured_stream(
                completed.stdout, "actual isolated method-native owner stdout",
            )
            if type(completed.stdout) is bytes
            and len(completed.stdout) <= MAX_WORKER_OUTPUT_BYTES
            else _bounded_stream(completed.stdout)
        ),
        "actual_native_owner_stderr": (
            _complete_captured_stream(
                completed.stderr, "actual isolated method-native owner stderr",
            )
            if type(completed.stderr) is bytes
            and len(completed.stderr) <= MAX_WORKER_OUTPUT_BYTES
            else _bounded_stream(completed.stderr)
        ),
        "production_observations_invented": False,
    }
    if (len(completed.stdout) > MAX_WORKER_OUTPUT_BYTES
            or len(completed.stderr) > MAX_WORKER_OUTPUT_BYTES):
        raise OfficialV15WorkerFailure(
            family,
            "the genuine isolated method-adjacent V21 native owner failed: "
            + method + ":" + phase,
            details,
        )
    try:
        document = json.loads(completed.stdout)
        if isinstance(document, dict):
            details["actual_native_owner_document"] = dict(document)
            actual_owner = document.get("native_owner")
            if isinstance(actual_owner, dict):
                details["actual_native_owner_observation"] = dict(actual_owner)
        require(completed.returncode == 0 and completed.stderr == b"",
                "the genuine isolated method-adjacent native owner failed")
        require(isinstance(document, dict)
                and canonical(document) + b"\n" == completed.stdout
                and document.get("schema")
                == SCHEMA + "-actual-isolated-method-native-owner"
                and document.get("status") == "PASS"
                and document.get("family") == family
                and document.get("source_sha256") == source_sha256
                and document.get("protocol_sha256") == PROTOCOL_SHA256
                and document.get("audit_source_sha256")
                == pins["audit_source"]
                and document.get("audit_protocol_sha256")
                == pins["audit_protocol"]
                and document.get("native_sha256_by_path") == native
                and document.get("candidate_imports") == 0
                and document.get("performance") == "NOT MEASURED"
                and document.get("holdout") == "NOT ACCESSED",
                "the genuine isolated V21 owner changed canonical provenance")
        observed = document["native_owner"]
        validated = inventory.validate_native_owner(observed, family, native)
        require(isinstance(validated, dict) and validated == observed,
                "the actual returned method-adjacent owner was not "
                "independently validated")
    except (Exception, MemoryError) as error:
        details.update({
            "actual_error_type": type(error).__name__,
            "actual_error": str(error),
        })
        raise OfficialV15WorkerFailure(
            family,
            "the genuine complete isolated V21 native owner was invalid: "
            + method + ":" + phase,
            details,
        ) from error
    return {"method": method, "phase": phase, "native_owner": validated}


def _validate_native_method_trace(
    family: str,
    matrix: list[dict[str, Any]],
    observations: Any,
    expected_native: Mapping[str, str],
    validator: Callable[[Any, str, Mapping[str, str]], Any],
) -> list[dict[str, Any]]:
    require(family in FAMILIES and isinstance(matrix, list)
            and len(matrix) == PUBLIC_METHODS
            and isinstance(observations, list)
            and len(observations) == 2 * PUBLIC_METHODS
            and callable(validator),
            "all 304 freshly executed original-method native owners are required")
    for index, requirement in enumerate(matrix):
        require(isinstance(requirement, Mapping)
                and type(requirement.get("test")) is str,
                "an exact original public method identity disappeared")
        for offset, phase in enumerate(("before", "after")):
            row = observations[2 * index + offset]
            require(isinstance(row, dict)
                    and set(row) == {"method", "phase", "native_owner"}
                    and row.get("method") == requirement["test"]
                    and row.get("phase") == phase
                    and isinstance(row.get("native_owner"), dict)
                    and validator(row["native_owner"], family, expected_native)
                    == row["native_owner"],
                    "a fresh real independent native owner was missing, "
                    "reordered, repeated, or invalid: "
                    + requirement["test"] + ":" + phase)
    return observations


def _validate_inline_guard(record: Any, owner_module: Any) -> dict[str, Any]:
    require(isinstance(record, dict)
            and set(record) == {
                "stage07_source_sha256", "required_descendants",
                "discovered_descendants", "observations_before",
                "observations_after", "cached_alias_count",
                "helper_alias_replacement_count",
                "all_cached_aliases_same_sentinel",
                "before_matching_verified", "after_matching_verified",
            }
            and record.get("stage07_source_sha256")
            == owner_module.STAGE07_SHA256
            and record.get("required_descendants")
            == list(owner_module.REQUIRED_MATCHER_DESCENDANTS)
            and record.get("all_cached_aliases_same_sentinel") is True
            and record.get("before_matching_verified") is True
            and record.get("after_matching_verified") is True,
            "the authentic original Stage 07 method guard was substituted")
    names = record["discovered_descendants"]
    require(isinstance(names, list) and names == sorted(set(names))
            and set(owner_module.REQUIRED_MATCHER_DESCENDANTS) <= set(names)
            and all(type(name) is str and name.startswith("re.") for name in names),
            "a genuinely cached upstream Python regex matcher was omitted")
    expected = [
        {"module": name, "blocked": True, "sentinel_identity": True,
         "cache_identity": True, "sentinel_type_exact": True}
        for name in names
    ]
    count = record["cached_alias_count"]
    replacement = record["helper_alias_replacement_count"]
    require(record["observations_before"] == expected
            and record["observations_after"] == expected
            and type(count) is int and count >= 0
            and type(replacement) is int and replacement == count,
            "a real upstream matcher, exact holder sentinel, or alias count "
            "was forged or restored")
    return record


@contextlib.contextmanager
def _official_cached_matcher_guard(
    owner_module: Any,
    constants_shim: types.ModuleType,
) -> Iterator[tuple[dict[str, Any], Callable[[], list[dict[str, Any]]]]]:
    stage07 = importlib.import_module(
        "tools.python_re_universal_public_oracle_stage07",
    )
    require(Path(stage07.__file__).resolve()
            == ROOT / owner_module.STAGE07_RELATIVE
            and callable(stage07._poison_cached_module_aliases),
            "the authentic independently audited Stage 07 helper changed")
    sentinel_type = stage07._ForbiddenRegexModule
    candidates = {
        id(value): value for value in tuple(sys.modules.values())
        if type(value) is sentinel_type
    }
    require(len(candidates) == 1,
            "the exact original candidate matcher sentinel was substituted")
    sentinel = next(iter(candidates.values()))
    cached = tuple(
        (name, module) for name, module in tuple(sys.modules.items())
        if name.startswith("re.") and isinstance(module, types.ModuleType)
        and module is not sentinel
        and not (name == "re._constants" and module is constants_shim)
    )
    by_name = {name: module for name, module in cached}
    require(set(owner_module.REQUIRED_MATCHER_DESCENDANTS) <= set(by_name)
            and len({id(module) for _, module in cached}) == len(cached),
            "a real original regex parser, compiler, or matcher disappeared")
    originals = tuple(module for _, module in cached)
    bindings: list[tuple[types.ModuleType, str, types.ModuleType]] = []
    for holder in tuple(sys.modules.values()):
        if not isinstance(holder, types.ModuleType):
            continue
        try:
            entries = tuple(vars(holder).items())
        except (TypeError, ValueError):
            continue
        for alias, observed in entries:
            if any(observed is module for module in originals):
                bindings.append((holder, alias, observed))
    replaced = stage07._poison_cached_module_aliases(
        sys.modules, originals, sentinel,
    )
    require(type(replaced) is int and replaced >= 0
            and replaced == len(bindings),
            "the real Stage 07 cached-alias helper returned a forged count")
    names = tuple(sorted(by_name))
    record: dict[str, Any] = {
        "stage07_source_sha256": owner_module.STAGE07_SHA256,
        "required_descendants": list(owner_module.REQUIRED_MATCHER_DESCENDANTS),
        "discovered_descendants": list(names),
        "observations_before": [], "observations_after": [],
        "cached_alias_count": len(bindings),
        "helper_alias_replacement_count": replaced,
        "all_cached_aliases_same_sentinel": True,
        "before_matching_verified": False,
        "after_matching_verified": False,
    }

    def observe() -> list[dict[str, Any]]:
        require(stage07._ForbiddenRegexModule is sentinel_type
                and type(sentinel) is sentinel_type,
                "the genuine cached upstream matcher sentinel was replaced")
        observations: list[dict[str, Any]] = []
        for name in names:
            observed = sys.modules.get(name)
            imported = importlib.import_module(name)
            row = {
                "module": name, "blocked": True,
                "sentinel_identity": imported is sentinel,
                "cache_identity": observed is sentinel,
                "sentinel_type_exact": type(observed) is sentinel_type,
            }
            require(all(row[key] is True for key in (
                "blocked", "sentinel_identity", "cache_identity",
                "sentinel_type_exact",
            )), "an original cached regex engine escaped: " + name)
            observations.append(row)
        require(all(vars(holder).get(alias) is sentinel
                    for holder, alias, _ in bindings),
                "an original cached matcher holder alias escaped the sentinel")
        for holder in tuple(sys.modules.values()):
            if not isinstance(holder, types.ModuleType):
                continue
            try:
                values = tuple(vars(holder).values())
            except (TypeError, ValueError):
                continue
            require(not any(value is module for value in values
                            for module in originals),
                    "a live holder retained a genuine original stdlib matcher")
        return observations

    try:
        for name, _ in cached:
            sys.modules[name] = sentinel
        record["observations_before"] = observe()
        record["before_matching_verified"] = True
        yield record, observe
        record["observations_after"] = observe()
        record["after_matching_verified"] = True
        _validate_inline_guard(record, owner_module)
    finally:
        for holder, alias, previous in reversed(bindings):
            setattr(holder, alias, previous)
        for name, module in cached:
            sys.modules[name] = module


def _validate_owned_original_re_import(
    name: Any,
    level: Any,
    family: Any,
    candidate: Any,
    modules: Any,
    graph: Mapping[str, Any],
    expected_natives: Mapping[str, Any],
    *,
    owned_family: str,
) -> types.ModuleType:
    require(type(name) is str and name == "re"
            and type(level) is int and level == 0
            and type(family) is str and family in FAMILIES
            and type(owned_family) is str and family == owned_family
            and isinstance(candidate, types.ModuleType)
            and isinstance(modules, Mapping)
            and modules.get("re") is candidate,
            "only the exact authenticated current-family absolute root "
            "candidate re import may bypass the Stage 07 owner guard")
    verified = _validate_authenticated_native_bridge(
        copy.deepcopy(graph.get("native_sha256_by_family", {})),
        graph,
        expected_natives,
    )
    require(set(verified) == set(FAMILIES)
            and bool(verified[family])
            and set(verified[family])
            == set(expected_natives[family].values()),
            "the exact owned re alias is detached from the authenticated "
            "current-family native graph")
    return candidate


def _validate_owned_original_constants_import(
    name: Any,
    fromlist: Any,
    level: Any,
    family: Any,
    candidate: Any,
    shim: Any,
    baseline_maxgroups: Any,
    modules: Any,
    graph: Mapping[str, Any],
    expected_natives: Mapping[str, Any],
    *,
    owned_family: str,
) -> types.ModuleType:
    _validate_owned_original_re_import(
        "re", 0, family, candidate, modules,
        graph, expected_natives, owned_family=owned_family,
    )
    require(type(name) is str and name == "re._constants"
            and type(fromlist) is tuple
            and fromlist == ("MAXGROUPS",)
            and type(level) is int and level == 0
            and type(shim) is types.ModuleType
            and modules.get("re._constants") is shim
            and set(vars(shim)) <= {
                "__name__", "__doc__", "__package__", "__loader__",
                "__spec__", "MAXGROUPS",
            }
            and shim.__name__ == "re._constants"
            and shim.__package__ == "re"
            and shim.__loader__ is None
            and isinstance(shim.__spec__, importlib.machinery.ModuleSpec)
            and shim.__spec__.name == "re._constants"
            and shim.__spec__.parent == "re"
            and shim.__spec__.loader is None
            and type(baseline_maxgroups) is int
            and type(getattr(shim, "MAXGROUPS", None)) is int
            and shim.MAXGROUPS == baseline_maxgroups,
            "only the exact immutable V4 constant-only MAXGROUPS shim "
            "owned by the current candidate may bypass Stage 07")
    return shim


@contextlib.contextmanager
def _owned_original_test_re_alias(
    family: str,
    candidate: Any,
    graph: Mapping[str, Any],
    constants_shim: types.ModuleType,
    baseline_maxgroups: int,
) -> Iterator[None]:
    require(inventory is not None
            and _verify_candidate_context_current_graph(
                graph, inventory.OWNED_SOURCE_PATHS,
                inventory.OWNED_NATIVE_PATHS,
            ) is graph,
            "the actual all-family graph changed before the exact "
            "owned original-test re import")
    _validate_owned_original_re_import(
        "re", 0, family, candidate, sys.modules,
        graph, inventory.OWNED_NATIVE_PATHS,
        owned_family=family,
    )
    _validate_owned_original_constants_import(
        "re._constants", ("MAXGROUPS",), 0,
        family, candidate, constants_shim, baseline_maxgroups,
        sys.modules, graph, inventory.OWNED_NATIVE_PATHS,
        owned_family=family,
    )
    stage07_import = builtins.__import__
    require(callable(stage07_import),
            "the genuine Stage 07 guarded import was not installed")

    def import_owned_re(
        name: str,
        globals: Any = None,
        locals: Any = None,
        fromlist: Any = (),
        level: int = 0,
    ) -> Any:
        if name == "re" and level == 0:
            return _validate_owned_original_re_import(
                name, level, family, candidate, sys.modules,
                graph, inventory.OWNED_NATIVE_PATHS,
                owned_family=family,
            )
        if (name == "re._constants" and level == 0
                and type(fromlist) is tuple
                and fromlist == ("MAXGROUPS",)):
            return _validate_owned_original_constants_import(
                name, fromlist, level, family, candidate,
                constants_shim, baseline_maxgroups, sys.modules,
                graph, inventory.OWNED_NATIVE_PATHS,
                owned_family=family,
            )
        return stage07_import(name, globals, locals, fromlist, level)

    builtins.__import__ = import_owned_re
    try:
        yield
        require(builtins.__import__ is import_owned_re
                and sys.modules.get("re") is candidate
                and sys.modules.get("re._constants") is constants_shim
                and _verify_candidate_context_current_graph(
                    graph, inventory.OWNED_SOURCE_PATHS,
                    inventory.OWNED_NATIVE_PATHS,
                ) is graph,
                "the original-test owned root re import or actual native "
                "graph escaped its strictly scoped guard")
    finally:
        builtins.__import__ = stage07_import


def _bounded_stream(value: Any) -> dict[str, Any]:
    if original is not None:
        return original.original.upstream._bounded_failure_stream(value)
    data = value if isinstance(value, bytes) else str(value or "").encode()
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "prefix": data[: min(len(data), 4096)].decode("utf-8", "replace"),
        "truncated": len(data) > 4096,
    }


def _complete_captured_stream(value: Any, label: str) -> dict[str, Any]:
    require(type(value) is bytes and len(value) <= MAX_WORKER_OUTPUT_BYTES,
            "an actual complete bounded " + label + " was not captured")
    return {
        "encoding": "hex",
        "bytes": len(value),
        "sha256": hashlib.sha256(value).hexdigest(),
        "complete_hex": value.hex(),
        "truncated": False,
    }


def _timeout_worker_failure(
    family: str,
    error: subprocess.TimeoutExpired,
    *,
    message: str,
    details: Mapping[str, Any] | None = None,
) -> OfficialV15WorkerFailure:
    require(family in FAMILIES
            and isinstance(error, subprocess.TimeoutExpired)
            and type(message) is str,
            "a genuine original timeout and actual family are required")

    def actual_stream(value: Any, label: str) -> dict[str, Any]:
        if value is None:
            return {"capture": "NOT CAPTURED"}
        if type(value) is bytes and len(value) <= MAX_WORKER_OUTPUT_BYTES:
            return _complete_captured_stream(value, label)
        if type(value) is str:
            encoded = value.encode("utf-8")
            if len(encoded) <= MAX_WORKER_OUTPUT_BYTES:
                return _complete_captured_stream(encoded, label)
        return _bounded_stream(value)

    observed: dict[str, Any] = dict(details or {})
    observed.update({
        "status": "TIMEOUT",
        "timeout_seconds": error.timeout,
        "returncode": None,
        "signal": None,
        "stdout": actual_stream(error.stdout, "actual timed-out worker stdout"),
        "stderr": actual_stream(error.stderr, "actual timed-out worker stderr"),
        "production_observations_invented": False,
    })
    return OfficialV15WorkerFailure(family, message, observed)


def _validate_captured_worker(
    completed: Any,
    *,
    family: str,
    source_sha256: str,
    pins: Mapping[str, str],
    expected_command: list[str],
    validate_document: Callable[[dict[str, Any]], Any] | None = None,
) -> dict[str, Any]:
    require(isinstance(completed, subprocess.CompletedProcess)
            and family in FAMILIES
            and type(completed.returncode) is int
            and type(completed.stdout) is bytes
            and type(completed.stderr) is bytes
            and isinstance(expected_command, list)
            and completed.args == expected_command,
            "an actual original isolated worker process was substituted")
    if (len(completed.stdout) > MAX_WORKER_OUTPUT_BYTES
            or len(completed.stderr) > MAX_WORKER_OUTPUT_BYTES):
        raise OfficialV15WorkerFailure(
            family,
            "the genuine original worker exceeded complete bounded streams",
            {
                "returncode": completed.returncode,
                "signal": (
                    -completed.returncode if completed.returncode < 0 else None
                ),
                "stdout": _bounded_stream(completed.stdout),
                "stderr": _bounded_stream(completed.stderr),
                "complete_streams_available": False,
                "production_observations_invented": False,
            },
        )
    details: dict[str, Any] = {
        "returncode": completed.returncode,
        "signal": -completed.returncode if completed.returncode < 0 else None,
        "stdout": _complete_captured_stream(
            completed.stdout, "isolated original worker stdout",
        ),
        "stderr": _complete_captured_stream(
            completed.stderr, "isolated original worker stderr",
        ),
        "complete_streams_available": True,
        "production_observations_invented": False,
    }
    try:
        try:
            decoded = json.loads(completed.stdout)
        except (UnicodeError, ValueError, TypeError) as error:
            details["actual_json_error"] = str(error)
            raise OfficialV15Error(
                "the actual complete worker stdout contains no decoded JSON",
            ) from error
        require(isinstance(decoded, dict),
                "the actual upstream worker returned no genuine object")
        document = decoded
        details["actual_worker_document"] = dict(document)
        observed_role = document.get("role_report")
        if isinstance(observed_role, Mapping):
            records = observed_role.get("records")
            if isinstance(records, list):
                details["actual_completed_original_method_records"] = (
                    copy.deepcopy(records)
                )
                details["actual_completed_original_method_count"] = len(records)
        trace = document.get("actual_native_method_owners")
        if isinstance(trace, list):
            details["actual_completed_native_method_owners"] = (
                copy.deepcopy(trace)
            )
            details["actual_native_owner_method_guard_checks"] = len(trace)
        nested_failure = document.get("details")
        if isinstance(nested_failure, Mapping):
            details["actual_worker_failure_details"] = copy.deepcopy(
                dict(nested_failure),
            )
            completed_records = nested_failure.get(
                "actual_completed_original_method_records",
            )
            if isinstance(completed_records, list):
                details["actual_completed_original_method_records"] = (
                    copy.deepcopy(completed_records)
                )
                details["actual_completed_original_method_count"] = len(
                    completed_records,
                )
            completed_owners = nested_failure.get(
                "actual_completed_native_method_owners",
            )
            if isinstance(completed_owners, list):
                details["actual_completed_native_method_owners"] = (
                    copy.deepcopy(completed_owners)
                )
                details["actual_native_owner_method_guard_checks"] = len(
                    completed_owners,
                )
            completed_role = nested_failure.get("actual_completed_original_role")
            if isinstance(completed_role, Mapping):
                details["actual_completed_original_role"] = copy.deepcopy(
                    dict(completed_role),
                )
            active_postflight = nested_failure.get("active_postflight_stage")
            if type(active_postflight) is str:
                details["active_postflight_stage"] = active_postflight
        require(completed.returncode == 0 and completed.stderr == b"",
                "the actual isolated original worker failed or emitted stderr")
        require(canonical(document) + b"\n" == completed.stdout,
                "the actual zero-exit worker output is not complete canonical JSON")
        require(document.get("schema") == SCHEMA + "-actual-worker"
                and document.get("status") == "PASS"
                and document.get("role") == family
                and document.get("source_sha256") == source_sha256
                and document.get("protocol_sha256") == PROTOCOL_SHA256
                and document.get("reference_sha256") == V6_REFERENCE_SHA256
                and document.get("public_method_matrix_sha256")
                == METHOD_MATRIX_SHA256
                and document.get("candidate_prerequisite_sha256") == dict(pins)
                and document.get("actual_inline_cached_matcher_method_guard_checks")
                == 2 * PUBLIC_METHODS
                and document.get("actual_native_owner_method_guard_checks")
                == 2 * PUBLIC_METHODS
                and document.get("performance") == "NOT MEASURED"
                and document.get("holdout") == "NOT ACCESSED",
                "a genuine zero-exit original worker changed source, role, "
                "reference, report pins, method provenance, or guarded counts")
        if validate_document is not None:
            require(callable(validate_document),
                    "a genuine complete original-role validator was substituted")
            validate_document(document)
        return document
    except OfficialV15WorkerFailure as error:
        details["actual_nested_worker_failure"] = dict(error.details)
        raise OfficialV15WorkerFailure(
            family,
            "the actual original worker failed complete post-capture validation",
            details,
        ) from error
    except (Exception, MemoryError) as error:
        details["actual_error_type"] = type(error).__name__
        details["actual_error"] = str(error)
        raise OfficialV15WorkerFailure(
            family,
            "the actual original worker failed complete post-capture validation",
            details,
        ) from error


def _execute_guarded_original_role(
    family: str, provenance: Mapping[str, Any], graph: Mapping[str, Any],
    owner_module: Any, source_sha256: str, pins: Mapping[str, str],
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    require(original is not None and inventory is not None and family in FAMILIES,
            "an actual immutable original upstream and fresh V21 owner are required")
    upstream = original.original.upstream
    legacy = original.original
    matrix = provenance["official"]["public_method_matrix"]
    require(isinstance(matrix, list) and len(matrix) == PUBLIC_METHODS,
            "all original upstream public methods must run in source order")
    expected_path = upstream.UPSTREAM_LIB / "test" / "test_re.py"
    raw = _read_regular(expected_path, MAX_SOURCE_BYTES,
                        "literal original CPython Lib/test/test_re.py")
    require(hashlib.sha256(raw).hexdigest() == upstream.TEST_SOURCE_SHA256,
            "the actual literal original CPython upstream test source changed")
    previous_path = list(sys.path)
    output = io.StringIO()
    errors = io.StringIO()
    records: list[dict[str, Any]] = []
    native_observations: list[dict[str, Any]] = []
    active: str | None = None
    phase: str | None = None
    inline: dict[str, Any] | None = None
    matcher_checks = 0
    try:
        sys.path.insert(0, str(upstream.UPSTREAM_LIB))
        baseline = importlib.import_module("re")
        constants = importlib.import_module("re._constants")
        support = importlib.import_module("test.support")
        warnings_helper = importlib.import_module("test.support.warnings_helper")
        corpus = importlib.import_module("test.re_tests")
        upstream._validate_preloaded_support(sys.modules)
        fixtures_before = upstream._verify_live_official_fixtures(
            support, warnings_helper, corpus,
        )
        require(support.bigmemtest.__module__ == "test.support"
                and support.requires_resource.__module__ == "test.support"
                and support._2G == 2**31,
                "an original upstream resource decorator was replaced")
        support.verbose = 0
        support.set_memlimit("40G")
        require(support.real_max_memuse == CONFIGURED_MEMORY_BYTES
                and support.is_resource_enabled("cpu"),
                "the genuine complete upstream 40-GiB/CPU resources are unavailable")
        require("fork" in multiprocessing.get_all_start_methods(),
                "the unchanged original upstream process test requires real fork")
        multiprocessing.set_start_method("fork", force=True)
        require(multiprocessing.get_start_method() == "fork",
                "the original real upstream fork process was substituted")
        with upstream._single_memory_worker():
            with upstream._fresh_private_locales() as locale_report:
                with upstream._role_regex_module(
                    family, baseline, constants, provenance,
                ) as (regex, guard):
                    owned_constants = _validate_owned_original_constants_import(
                        "re._constants", ("MAXGROUPS",), 0,
                        family, regex, sys.modules.get("re._constants"),
                        constants.MAXGROUPS, sys.modules, graph,
                        inventory.OWNED_NATIVE_PATHS,
                        owned_family=family,
                    )
                    with (
                        _official_cached_matcher_guard(
                            owner_module, owned_constants,
                        ) as (
                            inline, observe_matchers,
                        ),
                        _owned_original_test_re_alias(
                            family, regex, graph, owned_constants,
                            constants.MAXGROUPS,
                        ),
                    ):
                        specification = importlib.util.spec_from_file_location(
                            "test.test_re", expected_path,
                        )
                        require(specification is not None
                                and specification.loader is not None,
                                "the unchanged full upstream source is unavailable")
                        namespace = importlib.util.module_from_spec(specification)
                        previous = sys.modules.get("test.test_re")
                        try:
                            sys.modules["test.test_re"] = namespace
                            with contextlib.redirect_stdout(output):
                                with contextlib.redirect_stderr(errors):
                                    require(observe_matchers()
                                            == inline["observations_before"],
                                            "a cached matcher escaped before "
                                            "the literal original module import")
                                    specification.loader.exec_module(namespace)
                                    require(observe_matchers()
                                            == inline["observations_before"],
                                            "a cached matcher escaped during "
                                            "the literal original module import")
                                    for requirement in matrix:
                                        active = requirement["test"]
                                        phase = "before"
                                        native_observations.append(
                                            _observe_native_owner(
                                                family, graph, active, phase,
                                                source_sha256=source_sha256,
                                                pins=pins,
                                            )
                                        )
                                        require(observe_matchers()
                                                == inline["observations_before"],
                                                "an original cached matcher "
                                                "escaped before: " + active)
                                        matcher_checks += 1
                                        if active in {
                                            "ExternalTests.test_re_tests",
                                            "ExternalTests.test_re_benchmarks",
                                        }:
                                            require(
                                                upstream._verify_live_official_fixtures(
                                                    support, warnings_helper, corpus,
                                                ) == fixtures_before,
                                                "the genuine original 403/11 "
                                                "upstream fixture changed",
                                            )
                                        phase = "method"
                                        records.append(
                                            upstream._run_one_original_method(
                                                namespace, requirement,
                                                expected_path, support, "fork",
                                            )
                                        )
                                        phase = "after"
                                        require(observe_matchers()
                                                == inline["observations_before"],
                                                "an original cached matcher "
                                                "escaped during: " + active)
                                        matcher_checks += 1
                                        native_observations.append(
                                            _observe_native_owner(
                                                family, graph, active, phase,
                                                source_sha256=source_sha256,
                                                pins=pins,
                                            )
                                        )
                                        active = None
                                        phase = None
                                    fixtures_after = (
                                        upstream._verify_live_official_fixtures(
                                            support, warnings_helper, corpus,
                                        )
                                    )
                                    require(fixtures_after == fixtures_before,
                                            "the actual original support fixture "
                                            "changed during upstream execution")
                        finally:
                            if previous is None:
                                sys.modules.pop("test.test_re", None)
                            else:
                                sys.modules["test.test_re"] = previous
                    require(errors.getvalue() == "" and inline is not None,
                            "a genuine original official candidate emitted "
                            "stderr or lost the matcher sentinel")
                    _validate_inline_guard(inline, owner_module)
                    _validate_native_method_trace(
                        family, matrix, native_observations,
                        graph["native_sha256_by_family"][family],
                        inventory.validate_native_owner,
                    )
                    require(matcher_checks == 2 * PUBLIC_METHODS,
                            "an original public method lost an adjacent matcher guard")
                    summary = upstream.assess_role_records(family, records, matrix)
                    role = {
                        **summary,
                        "records": records,
                        "locale": locale_report,
                        "guard": guard,
                        "resource_provenance": {
                            "real_max_memuse": support.real_max_memuse,
                            "large_method_sizes": {
                                item["test"]: item.get("resource", {}).get(
                                    "delivered_size",
                                )
                                for item in records
                                if item["test"] in {
                                    "ReTests.test_large_search",
                                    "ReTests.test_large_subn",
                                }
                            },
                            "cpu_resource_enabled": support.is_resource_enabled(
                                "cpu",
                            ),
                            "multiprocessing_extension_available": (
                                importlib.util.find_spec("_multiprocessing")
                                is not None
                            ),
                            "multiprocessing_start_method": "fork",
                            "private_debug_fail_after": hasattr(
                                regex.Pattern, "_fail_after",
                            ),
                            "actual_upstream_corpus_cases": len(corpus.tests),
                            "actual_external_fixture_assertion_cases": len(
                                corpus.benchmarks,
                            ),
                            "exclusive_big_memory_worker": True,
                            "official_support_shim_used": False,
                            "official_test_source_rewritten": False,
                        },
                        "executed_test_source_sha256": upstream.TEST_SOURCE_SHA256,
                        "official_support_tree_sha256": (
                            upstream.OFFICIAL_SUPPORT_TREE_SHA256
                        ),
                        "live_official_fixture_provenance": fixtures_after,
                        "captured_official_stdout": output.getvalue(),
                        "captured_official_stderr": errors.getvalue(),
                        "actual_cached_matcher_method_guard_checks": matcher_checks,
                        "actual_native_owner_method_guard_checks": len(
                            native_observations,
                        ),
                    }
                    legacy._validate_role(family, role, matrix)
                    return role, dict(inline), native_observations
    except OfficialV15WorkerFailure as error:
        details = dict(error.details)
        details.update({
            "completed_original_method_records": records,
            "completed_original_method_count": len(records),
            "active_original_method": active,
            "active_original_method_phase": phase,
            "captured_official_stdout": _bounded_stream(output.getvalue()),
            "captured_official_stderr": _bounded_stream(errors.getvalue()),
            "actual_inline_cached_matcher_guard": inline,
            "actual_cached_matcher_method_guard_checks": matcher_checks,
            "actual_completed_native_method_owners": native_observations,
            "actual_native_owner_method_guard_checks": len(native_observations),
            "production_observations_invented": False,
            "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED",
        })
        raise OfficialV15WorkerFailure(
            family,
            "a genuine original method lost its isolated native owner: " + family,
            details,
        ) from error
    except (Exception, MemoryError) as error:
        raise OfficialV15WorkerFailure(
            family,
            "the genuinely guarded original complete upstream method stopped: "
            + family,
            {
                "completed_original_method_records": records,
                "completed_original_method_count": len(records),
                "active_original_method": active,
                "active_original_method_phase": phase,
                "actual_error_type": type(error).__name__,
                "actual_error": str(error),
                "captured_official_stdout": _bounded_stream(output.getvalue()),
                "captured_official_stderr": _bounded_stream(errors.getvalue()),
                "actual_inline_cached_matcher_guard": inline,
                "actual_cached_matcher_method_guard_checks": matcher_checks,
                "actual_completed_native_method_owners": native_observations,
                "actual_native_owner_method_guard_checks": len(
                    native_observations,
                ),
                "production_observations_invented": False,
                "performance": "NOT MEASURED",
                "holdout": "NOT ACCESSED",
            },
        ) from error
    finally:
        sys.path[:] = previous_path


def _capture_completed_original_progress(
    family: str,
    role: Mapping[str, Any],
    inline: Mapping[str, Any],
    native_trace: list[dict[str, Any]],
    stage: str,
) -> dict[str, Any]:
    require(family in FAMILIES
            and isinstance(role, Mapping)
            and isinstance(role.get("records"), list)
            and len(role["records"]) == PUBLIC_METHODS
            and role.get("actual_cached_matcher_method_guard_checks")
            == 2 * PUBLIC_METHODS
            and role.get("actual_native_owner_method_guard_checks")
            == 2 * PUBLIC_METHODS
            and isinstance(inline, Mapping)
            and isinstance(native_trace, list)
            and len(native_trace) == 2 * PUBLIC_METHODS
            and all(isinstance(row, Mapping) for row in native_trace)
            and type(stage) is str and bool(stage),
            "the genuinely completed 152 original methods and 304 real "
            "native owners must be captured before any postflight")
    return {
        "actual_completed_original_method_records": copy.deepcopy(
            role["records"],
        ),
        "actual_completed_original_method_count": len(role["records"]),
        "actual_completed_original_role": copy.deepcopy(dict(role)),
        "actual_inline_cached_matcher_guard": copy.deepcopy(dict(inline)),
        "actual_completed_native_method_owners": copy.deepcopy(native_trace),
        "actual_native_owner_method_guard_checks": len(native_trace),
        "active_postflight_stage": stage,
        "production_observations_invented": False,
    }


WORKER_BOOTSTRAP = (
    "import sys;sys.path.insert(0,sys.argv[1]);"
    "from tools.postfinal_cpython_locale_oracle_v15 import worker_entry;"
    "raise SystemExit(worker_entry(sys.argv[2],sys.argv[3],sys.argv[4],"
    "sys.argv[5],sys.argv[6]))"
)


def worker_entry(
    family: str, source_sha256: str, protocol_sha256: str,
    reference_sha256: str, encoded_pins: str,
) -> int:
    completed_progress: dict[str, Any] | None = None
    postflight_stage = "preflight-before-any-completed-original-role"
    try:
        require(family in FAMILIES
                and reference_sha256 == V6_REFERENCE_SHA256,
                "only an actual current native role and frozen double V6 "
                "reference are permitted")
        controller = _authenticate_controller(source_sha256, protocol_sha256)
        decoded = json.loads(encoded_pins)
        require(isinstance(decoded, dict),
                "exact complete externally published candidate pins are required")
        pins = _candidate_pin_values(family, decoded)
        qualified = authenticate_candidate_prerequisites(family, pins)
        provenance = controller._original_reference_prerequisites()
        references = _read_frozen_reference(provenance)
        graph = qualified["graph"]
        state = qualified["family_states"][family]
        owner_module = state["owner"]
        _install_authenticated_native_bridge(
            provenance, qualified, graph, state["v21"].OWNED_NATIVE_PATHS,
        )
        role, inline, native_trace = _execute_guarded_original_role(
            family, provenance, graph, owner_module, source_sha256, pins,
        )
        completed_progress = _capture_completed_original_progress(
            family, role, inline, native_trace,
            "complete-original-role-captured-before-any-postflight",
        )
        postflight_stage = "frozen-independent-double-reference-status-vector"
        matrix = provenance["official"]["public_method_matrix"]
        expected = controller.original._status_vector(
            references["reference_a"]["records"],
        )
        require(controller.original._status_vector(role["records"]) == expected
                and controller.original._status_vector(
                    references["reference_b"]["records"],
                ) == expected,
                "the actual original candidate differs from both real V6 roles")
        postflight_stage = "current-complete-source-and-native-graph-integrity"
        require(_verify_candidate_context_current_graph(
                    graph, inventory.OWNED_SOURCE_PATHS,
                    inventory.OWNED_NATIVE_PATHS,
                ) is graph,
                "the full audited source/native graph changed during the suite")
        postflight_stage = "complete-method-adjacent-native-owner-integrity"
        _validate_native_method_trace(
            family, matrix, native_trace,
            graph["native_sha256_by_family"][family],
            inventory.validate_native_owner,
        )
        postflight_stage = "complete-canonical-original-worker-document"
        document = {
            "schema": SCHEMA + "-actual-worker",
            "status": "PASS",
            "python": "3.14.6",
            "role": family,
            "source_sha256": source_sha256,
            "protocol_sha256": protocol_sha256,
            "reference_sha256": reference_sha256,
            "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
            "candidate_prerequisite_sha256": pins,
            "qualified_family_proof": qualified["qualified_family_proofs"][family],
            "role_report": role,
            "actual_inline_cached_matcher_guards": inline,
            "actual_inline_cached_matcher_method_guard_checks": 2 * PUBLIC_METHODS,
            "actual_native_method_owners": native_trace,
            "actual_native_owner_method_guard_checks": 2 * PUBLIC_METHODS,
            "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED",
        }
    except OfficialV15WorkerFailure as error:
        details = dict(error.details)
        if completed_progress is not None:
            details.update(copy.deepcopy(completed_progress))
            details["active_postflight_stage"] = postflight_stage
        print(json.dumps({
            "schema": SCHEMA + "-actual-worker-failure",
            "status": "FAIL", "role": error.role,
            "reason": str(error), "details": details,
            "production_observations_invented": False,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }, ensure_ascii=True, allow_nan=False,
            sort_keys=True, separators=(",", ":")))
        return 2
    except (Exception, MemoryError) as error:
        details: dict[str, Any] = {
            "actual_error_type": type(error).__name__,
            "actual_error": str(error),
            "active_postflight_stage": postflight_stage,
            "actual_complete_original_progress_captured": (
                completed_progress is not None
            ),
            "production_observations_invented": False,
        }
        if completed_progress is not None:
            details.update(copy.deepcopy(completed_progress))
            details["active_postflight_stage"] = postflight_stage
        print(json.dumps({
            "schema": SCHEMA + "-actual-worker-failure",
            "status": "FAIL", "role": family,
            "actual_error_type": type(error).__name__,
            "reason": str(error),
            "details": details,
            "production_observations_invented": False,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }, ensure_ascii=True, allow_nan=False,
            sort_keys=True, separators=(",", ":")))
        return 2
    print(json.dumps(document, ensure_ascii=True, allow_nan=False,
                     sort_keys=True, separators=(",", ":")))
    return 0


def _run_isolated_worker(
    family: str,
    source_sha256: str,
    pins: Mapping[str, str],
    *,
    matrix: list[dict[str, Any]],
    expected_baseline: list[Any],
    expected_native: Mapping[str, str],
    owner_module: Any,
    expected_proof: Mapping[str, Any],
) -> dict[str, Any]:
    require(family in FAMILIES and valid_sha256(source_sha256),
            "only a genuinely pinned actual V15 native worker is permitted")
    environment = _isolated_owner_environment()
    timeout = getattr(original, "WORKER_TIMEOUT_SECONDS", 24 * 60 * 60)
    command = [
        str(PINNED_CPYTHON), "-I", "-B", "-c", WORKER_BOOTSTRAP,
        str(ROOT), family, source_sha256, PROTOCOL_SHA256,
        V6_REFERENCE_SHA256, canonical(dict(pins)).decode("ascii"),
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=str(ROOT), env=environment, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        raise _timeout_worker_failure(
            family,
            error,
            message="the real complete original V15 upstream worker timed out",
        ) from error

    def validate_complete_original_role(document: dict[str, Any]) -> None:
        require(original is not None and inventory is not None,
                "actual immutable upstream and independent owners are required")
        role = document.get("role_report")
        require(isinstance(role, dict),
                "the complete original public candidate role was omitted")
        original.original._validate_role(family, role, matrix)
        require(original.original._status_vector(role["records"])
                == expected_baseline,
                "the actual complete native role differs from both frozen "
                "genuine standard-library reference processes")
        require(document.get("qualified_family_proof") == dict(expected_proof),
                "the real worker substituted its complete actual V24 proof pair")
        _validate_inline_guard(
            document.get("actual_inline_cached_matcher_guards"), owner_module,
        )
        _validate_native_method_trace(
            family, matrix, document.get("actual_native_method_owners"),
            expected_native, inventory.validate_native_owner,
        )
        require(role.get("actual_cached_matcher_method_guard_checks")
                == 2 * PUBLIC_METHODS
                and role.get("actual_native_owner_method_guard_checks")
                == 2 * PUBLIC_METHODS,
                "an actual upstream role omitted a matcher or isolated native owner")

    return _validate_captured_worker(
        completed,
        family=family,
        source_sha256=source_sha256,
        pins=pins,
        expected_command=command,
        validate_document=validate_complete_original_role,
    )


def _base_document(
    provenance: Mapping[str, Any], source_sha256: str,
) -> dict[str, Any]:
    require(original is not None,
            "the genuine immutable V6 upstream provenance is required")
    document = original._base_document(provenance, V6_SOURCE_SHA256)
    document.update({
        "source_path": SOURCE_RELATIVE,
        "source_sha256": source_sha256,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": PROTOCOL_SHA256,
        "immutable_v6_source_path": V6_SOURCE_RELATIVE,
        "immutable_v6_source_sha256": V6_SOURCE_SHA256,
        "immutable_v6_protocol_path": V6_PROTOCOL_RELATIVE,
        "immutable_v6_protocol_sha256": V6_PROTOCOL_SHA256,
        "immutable_v6_reference_path": V6_REFERENCE_RELATIVE,
        "immutable_v6_reference_sha256": V6_REFERENCE_SHA256,
        "synthetic": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    })
    return document


def run_candidates(
    selected: str, source_sha256: str, supplied: Mapping[str, Any],
) -> dict[str, Any]:
    pins = _candidate_pin_values(selected, supplied)
    controller = _authenticate_controller(source_sha256, PROTOCOL_SHA256)
    qualified = authenticate_candidate_prerequisites(selected, pins)
    provenance = controller._original_reference_prerequisites()
    references = _read_frozen_reference(provenance)
    chosen = _chosen(selected)
    destinations = tuple(
        item for family in chosen for item in (
            ROLE_REPORT_RELATIVES[family], ROLE_FAILURE_RELATIVES[family],
            ROLE_RECEIPT_RELATIVES[family],
        )
    )
    if selected == "all":
        destinations += (
            REPORT_RELATIVE, REPORT_FAILURE_RELATIVE, REPORT_RECEIPT_RELATIVE,
        )
    _preflight_fresh_outputs(destinations)
    _install_authenticated_native_bridge(
        provenance, qualified, qualified["graph"], inventory.OWNED_NATIVE_PATHS,
    )
    matrix = provenance["official"]["public_method_matrix"]
    baseline = controller.original._status_vector(
        references["reference_a"]["records"],
    )
    reports: dict[str, Any] = dict(references)
    workers: dict[str, Any] = {}
    publications: list[dict[str, Any]] = []
    for family in chosen:
        current: dict[str, Any] | None = None
        family_pins = {
            key: value for key, value in pins.items()
            if key in (*CONTROLLER_PIN_KEYS, "base_report", "strict_report")
            or key.startswith(family + "_")
        }
        try:
            state = qualified["family_states"][family]
            current = _run_isolated_worker(
                family,
                source_sha256,
                family_pins,
                matrix=matrix,
                expected_baseline=baseline,
                expected_native=qualified["graph"][
                    "native_sha256_by_family"
                ][family],
                owner_module=state["owner"],
                expected_proof=qualified["qualified_family_proofs"][family],
            )
            role = current["role_report"]
            controller.original._validate_role(family, role, matrix)
            require(controller.original._status_vector(role["records"])
                    == baseline,
                    "an original complete candidate differs from both frozen "
                    "independent V6 references")
            _validate_inline_guard(
                current["actual_inline_cached_matcher_guards"], state["owner"],
            )
            trace = _validate_native_method_trace(
                family, matrix, current["actual_native_method_owners"],
                qualified["graph"]["native_sha256_by_family"][family],
                inventory.validate_native_owner,
            )
            require(role.get("actual_cached_matcher_method_guard_checks")
                    == 2 * PUBLIC_METHODS
                    and role.get("actual_native_owner_method_guard_checks")
                    == 2 * PUBLIC_METHODS
                    and inventory.snapshot_current_graph()
                    == qualified["graph"],
                    "an actual complete original role lost an adjacent owner, "
                    "matcher, source, or native binary")
            document = {
                **_base_document(provenance, source_sha256),
                "schema": SCHEMA + "-actual-" + family + "-role",
                "status": "PASS",
                "reference_sha256": V6_REFERENCE_SHA256,
                "candidate_prerequisite_sha256": family_pins,
                "qualified_family_proof": qualified[
                    "qualified_family_proofs"
                ][family],
                "actual_inline_cached_matcher_guards": current[
                    "actual_inline_cached_matcher_guards"
                ],
                "actual_inline_cached_matcher_method_guard_checks": (
                    2 * PUBLIC_METHODS
                ),
                "actual_native_method_owners": trace,
                "actual_native_owner_method_guard_checks": 2 * PUBLIC_METHODS,
                "roles": {family: role},
            }
            publication = _publish_with_durable_success_receipt(
                document,
                ROLE_REPORT_RELATIVES[family],
                ROLE_RECEIPT_RELATIVES[family],
            )
            publications.append(copy.deepcopy(publication))
        except (Exception, MemoryError) as error:
            details = (
                dict(error.details) if isinstance(error, OfficialV15WorkerFailure)
                else {"actual_error_type": type(error).__name__,
                      "actual_error": str(error)}
            )
            if isinstance(error, OfficialV15PublicationFailure):
                details["actual_exclusive_publication_receipts"] = [
                    *(copy.deepcopy(dict(prior))
                      for prior in error.prior_receipts),
                    copy.deepcopy(dict(error.receipt)),
                ]
                details["actual_partial_publication_created"] = (
                    error.receipt["actual_file_created"]
                )
                details["actual_partial_publication_fully_durable"] = (
                    error.receipt["fully_durable_publication"]
                )
            if current is not None:
                details["complete_actual_original_worker"] = current
            details["actual_completed_candidate_roles"] = {
                name: item for name, item in reports.items() if name in FAMILIES
            }
            details["actual_fully_durable_role_publications"] = copy.deepcopy(
                publications,
            )
            details["production_observations_invented"] = False
            raise OfficialV15WorkerFailure(
                family, "the genuine fully guarded original V15 candidate failed",
                details,
            ) from error
        reports[family] = role
        workers[family] = {
            "inline": current["actual_inline_cached_matcher_guards"],
            "inline_method_guard_checks": 2 * PUBLIC_METHODS,
            "native_method_owners": trace,
            "native_method_guard_checks": 2 * PUBLIC_METHODS,
        }
    if selected != "all":
        return {
            "schema": SCHEMA + "-single-candidate-result",
            "status": "PASS",
            "role": selected,
            "path": ROLE_REPORT_RELATIVES[selected],
            "actual_fully_durable_role_publications": publications,
            "reference_sha256": V6_REFERENCE_SHA256,
            "original_public_methods": PUBLIC_METHODS,
            "actual_method_adjacent_native_owners": 2 * PUBLIC_METHODS,
            "actual_method_adjacent_cached_matcher_guards": 2 * PUBLIC_METHODS,
            "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED",
        }
    require(set(reports) == {*REFERENCE_LABELS, *FAMILIES}
            and set(workers) == set(FAMILIES),
            "two actual frozen references and all three current native "
            "candidate families are required")
    document = {
        **_base_document(provenance, source_sha256),
        "schema": SCHEMA,
        "status": "PASS",
        "reference_sha256": V6_REFERENCE_SHA256,
        "actual_independent_reference_count": 2,
        "candidate_prerequisite_sha256": pins,
        "actual_v21_base_report_sha256": pins["base_report"],
        "actual_v21_strict_report_sha256": pins["strict_report"],
        "v21_source_sha256": pins["audit_source"],
        "v21_protocol_sha256": pins["audit_protocol"],
        "v24_source_sha256": pins["proof_source"],
        "v24_protocol_sha256": pins["proof_protocol"],
        "qualified_family_proofs": qualified["qualified_family_proofs"],
        "actual_fully_durable_role_publications": publications,
        "actual_v21_native_method_owners": workers,
        "all_official_method_contexts_cache_guarded": True,
        "cached_matcher_guard_checks_per_original_role": 2 * PUBLIC_METHODS,
        "native_owner_guard_checks_per_original_role": 2 * PUBLIC_METHODS,
        "roles": reports,
    }
    try:
        all_publication = _publish_with_durable_success_receipt(
            document, REPORT_RELATIVE, REPORT_RECEIPT_RELATIVE,
        )
    except (Exception, MemoryError) as error:
        details: dict[str, Any] = {
            "actual_error_type": type(error).__name__,
            "actual_error": str(error),
            "complete_actual_all_family_document": document,
            "actual_completed_candidate_roles": {
                family: reports[family] for family in FAMILIES
            },
            "actual_native_owner_method_traces": workers,
            "actual_fully_durable_role_publications": copy.deepcopy(
                publications,
            ),
            "production_observations_invented": False,
        }
        if isinstance(error, OfficialV15PublicationFailure):
            details["actual_exclusive_publication_receipts"] = [
                *(copy.deepcopy(dict(prior))
                  for prior in error.prior_receipts),
                copy.deepcopy(dict(error.receipt)),
            ]
            details["actual_partial_publication_created"] = (
                error.receipt["actual_file_created"]
            )
            details["actual_partial_publication_fully_durable"] = (
                error.receipt["fully_durable_publication"]
            )
        raise OfficialV15WorkerFailure(
            "all",
            "all actual original V15 families passed but the complete result "
            "could not be durably published",
            details,
        ) from error
    return {
        **document,
        "actual_all_family_durable_publication": copy.deepcopy(all_publication),
        "actual_all_family_success_receipt_path": (
            REPORT_RECEIPT_RELATIVE
        ),
        "actual_all_family_success_receipt_sha256": (
            all_publication["publication_receipt_sha256"]
        ),
    }


@contextlib.contextmanager
def _source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {
        "file_reads": 0,
        "file_writes": 0,
        "subprocesses": 0,
        "threads": 0,
        "clock_samples": 0,
        "candidate_imports": 0,
        "locale_generations": 0,
        "file_read_attempts_blocked": 0,
        "file_write_attempts_blocked": 0,
        "worker_attempts_blocked": 0,
        "thread_attempts_blocked": 0,
        "clock_attempts_blocked": 0,
        "candidate_import_attempts_blocked": 0,
        "locale_attempts_blocked": 0,
    }
    restore: list[tuple[Any, str, Any]] = []

    def deny(kind: str, message: str) -> Callable[..., Any]:
        def blocked(*_args: Any, **_kwargs: Any) -> Any:
            effects[kind] += 1
            raise OfficialV15Error(message)
        return blocked

    def patch(holder: Any, name: str, replacement: Any) -> None:
        if hasattr(holder, name):
            restore.append((holder, name, getattr(holder, name)))
            setattr(holder, name, replacement)

    blocked_read = deny("file_read_attempts_blocked",
                        "source-only controls cannot read a file or evidence")
    blocked_write = deny("file_write_attempts_blocked",
                         "source-only controls cannot write a file or evidence")
    blocked_worker = deny("worker_attempts_blocked",
                          "source-only controls cannot start a production worker")
    blocked_thread = deny("thread_attempts_blocked",
                          "source-only controls cannot start a thread")
    blocked_clock = deny("clock_attempts_blocked",
                         "source-only controls cannot sample a performance clock")
    blocked_import = deny("candidate_import_attempts_blocked",
                          "source-only controls cannot import production sources")
    blocked_locale = deny("locale_attempts_blocked",
                          "source-only controls cannot generate a real locale")
    try:
        patch(builtins, "open", blocked_read)
        patch(io, "open", blocked_read)
        for name in ("open", "read_bytes", "read_text", "stat", "lstat",
                     "exists", "is_file", "is_dir", "is_symlink", "glob",
                     "rglob", "iterdir"):
            patch(Path, name, blocked_read)
        for name in ("open", "stat", "lstat", "access", "listdir", "scandir"):
            patch(os, name, blocked_read)
        for name in ("write", "fsync", "mkdir", "makedirs", "replace",
                     "rename", "remove", "unlink", "rmdir"):
            patch(os, name, blocked_write)
        patch(Path, "write_bytes", blocked_write)
        patch(Path, "write_text", blocked_write)
        patch(subprocess, "run", blocked_worker)
        patch(subprocess, "Popen", blocked_worker)
        patch(os, "system", blocked_worker)
        patch(os, "popen", blocked_worker)
        patch(os, "fork", blocked_worker)
        patch(multiprocessing.Process, "start", blocked_worker)
        patch(threading.Thread, "start", blocked_thread)
        patch(tempfile, "TemporaryDirectory", blocked_locale)
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns"):
            patch(time, name, blocked_clock)
        patch(importlib, "import_module", blocked_import)
        patch(builtins, "__import__", blocked_import)
        yield effects
    finally:
        for holder, name, previous in reversed(restore):
            setattr(holder, name, previous)


def _synthetic_controllers() -> dict[str, str]:
    return {
        key: _synthetic_digest("actual-controller-shape:" + key)
        for key in CONTROLLER_PIN_KEYS
    }


def _synthetic_pins(selected: str) -> dict[str, str]:
    return {
        **_synthetic_controllers(),
        "base_report": _synthetic_digest("actual-v21-all-family-base-report"),
        "strict_report": _synthetic_digest("actual-v21-all-family-strict-report"),
        **{
            family + "_" + kind:
            _synthetic_digest("actual-v24-proof-shape:" + family + ":" + kind)
            for family in _chosen(selected)
            for kind in PROOF_KINDS
        },
    }


def _synthetic_v12_first_upstream_failure() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any],
]:
    worker = {
        "schema": (
            "rebar-postfinal-cpython-full-public-locale-v12-"
            "actual-worker-failure"
        ),
        "status": "FAIL",
        "role": "rust",
        "details": {
            "actual_error_type": "OfficialV4Error",
            "actual_error": (
                "the current independently owned native bridge is not "
                "authenticated"
            ),
            "completed_original_method_count": 0,
            "actual_native_owner_method_guard_checks": 0,
            "actual_cached_matcher_method_guard_checks": 0,
        },
    }
    stdout = canonical(worker) + b"\n"
    stdout_sha256 = hashlib.sha256(stdout).hexdigest()
    empty = V12_FIRST_UPSTREAM_STDERR_SHA256
    base = {
        "schema": (
            "rebar-postfinal-cpython-full-public-locale-v12-"
            "actual-role-failure"
        ),
        "status": "FAIL",
        "role": "rust",
        "reason": "synthetic source-only preserved historical failure",
        "details": {
            "actual_error_type": "OfficialV12Error",
            "returncode": 2,
            "actual_worker_document": worker,
            "stdout": {
                "encoding": "hex", "bytes": len(stdout),
                "sha256": stdout_sha256, "complete_hex": stdout.hex(),
                "truncated": False,
            },
            "stderr": {
                "encoding": "hex", "bytes": 0, "sha256": empty,
                "complete_hex": "", "truncated": False,
            },
        },
        "source_sha256": V12_SOURCE_SHA256,
        "protocol_sha256": V12_PROTOCOL_SHA256,
        "immutable_v6_reference_sha256": V6_REFERENCE_SHA256,
        "synthetic": False,
        "production_observations_invented": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    failure = copy.deepcopy(base)
    failure["actual_failure_destination"] = V12_FIRST_UPSTREAM_FAILURE_RELATIVE
    raw_failure = canonical(failure) + b"\n"
    failure_sha256 = hashlib.sha256(raw_failure).hexdigest()
    receipt = {
        "schema": (
            "rebar-postfinal-cpython-full-public-locale-v12-"
            "actual-exclusive-publication-receipt"
        ),
        "path": V12_FIRST_UPSTREAM_FAILURE_RELATIVE,
        "expected_payload_sha256": failure_sha256,
        "expected_payload_bytes": len(raw_failure),
        "actual_file_created": True,
        "actual_payload_bytes_written": len(raw_failure),
        "actual_write_calls": [{
            "requested_bytes": len(raw_failure),
            "returned_bytes": len(raw_failure),
        }],
        "actual_file_fsync": True,
        "actual_directory_fsync": True,
        "canonical_reread_succeeded": True,
        "fully_durable_publication": True,
    }
    captured = copy.deepcopy(base)
    captured["actual_exclusively_preserved_failure_reports"] = [{
        "path": V12_FIRST_UPSTREAM_FAILURE_RELATIVE,
        "sha256": failure_sha256,
        "actual_exclusive_publication_receipt": receipt,
    }]
    raw_captured = canonical(captured) + b"\n"
    return failure, captured, {
        "failure_sha256": failure_sha256,
        "failure_bytes": len(raw_failure),
        "captured_sha256": hashlib.sha256(raw_captured).hexdigest(),
        "captured_bytes": len(raw_captured),
        "stdout_sha256": stdout_sha256,
        "stdout_bytes": len(stdout),
    }


def _synthetic_v13_first_upstream_failure() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any],
]:
    worker = {
        "schema": (
            "rebar-postfinal-cpython-full-public-locale-v13-"
            "actual-worker-failure"
        ),
        "status": "FAIL",
        "role": "rust",
        "details": {
            "actual_error_type": "ImportError",
            "actual_error": (
                "stage-07 blocked unowned matching import: "
                "re"
            ),
            "completed_original_method_count": 0,
            "actual_native_owner_method_guard_checks": 0,
            "actual_cached_matcher_method_guard_checks": 0,
        },
    }
    stdout = canonical(worker) + b"\n"
    stdout_sha256 = hashlib.sha256(stdout).hexdigest()
    empty = V13_FIRST_UPSTREAM_STDERR_SHA256
    base = {
        "schema": (
            "rebar-postfinal-cpython-full-public-locale-v13-"
            "actual-role-failure"
        ),
        "status": "FAIL",
        "role": "rust",
        "reason": "synthetic source-only preserved historical failure",
        "details": {
            "actual_error_type": "OfficialV13Error",
            "returncode": 2,
            "actual_worker_document": worker,
            "stdout": {
                "encoding": "hex", "bytes": len(stdout),
                "sha256": stdout_sha256, "complete_hex": stdout.hex(),
                "truncated": False,
            },
            "stderr": {
                "encoding": "hex", "bytes": 0, "sha256": empty,
                "complete_hex": "", "truncated": False,
            },
        },
        "source_sha256": V13_SOURCE_SHA256,
        "protocol_sha256": V13_PROTOCOL_SHA256,
        "immutable_v6_reference_sha256": V6_REFERENCE_SHA256,
        "synthetic": False,
        "production_observations_invented": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    failure = copy.deepcopy(base)
    failure["actual_failure_destination"] = V13_FIRST_UPSTREAM_FAILURE_RELATIVE
    raw_failure = canonical(failure) + b"\n"
    failure_sha256 = hashlib.sha256(raw_failure).hexdigest()
    receipt = {
        "schema": (
            "rebar-postfinal-cpython-full-public-locale-v13-"
            "actual-exclusive-publication-receipt"
        ),
        "path": V13_FIRST_UPSTREAM_FAILURE_RELATIVE,
        "expected_payload_sha256": failure_sha256,
        "expected_payload_bytes": len(raw_failure),
        "actual_file_created": True,
        "actual_payload_bytes_written": len(raw_failure),
        "actual_write_calls": [{
            "requested_bytes": len(raw_failure),
            "returned_bytes": len(raw_failure),
        }],
        "actual_file_fsync": True,
        "actual_directory_fsync": True,
        "canonical_reread_succeeded": True,
        "fully_durable_publication": True,
    }
    captured = copy.deepcopy(base)
    captured["actual_exclusively_preserved_failure_reports"] = [{
        "path": V13_FIRST_UPSTREAM_FAILURE_RELATIVE,
        "sha256": failure_sha256,
        "actual_exclusive_publication_receipt": receipt,
    }]
    raw_captured = canonical(captured) + b"\n"
    return failure, captured, {
        "failure_sha256": failure_sha256,
        "failure_bytes": len(raw_failure),
        "captured_sha256": hashlib.sha256(raw_captured).hexdigest(),
        "captured_bytes": len(raw_captured),
        "stdout_sha256": stdout_sha256,
        "stdout_bytes": len(stdout),
    }


def _synthetic_v14_first_upstream_failure() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any],
]:
    worker = {
        "schema": (
            "rebar-postfinal-cpython-full-public-locale-v14-"
            "actual-worker-failure"
        ),
        "status": "FAIL",
        "role": "rust",
        "details": {
            "actual_error_type": "ProofV11Error",
            "actual_error": (
                "the V11 correctness controller must never import a candidate"
            ),
            "completed_original_method_count": 0,
            "actual_native_owner_method_guard_checks": 0,
            "actual_cached_matcher_method_guard_checks": 0,
        },
    }
    stdout = canonical(worker) + b"\n"
    stdout_sha256 = hashlib.sha256(stdout).hexdigest()
    empty = V14_FIRST_UPSTREAM_STDERR_SHA256
    base = {
        "schema": (
            "rebar-postfinal-cpython-full-public-locale-v14-"
            "actual-role-failure"
        ),
        "status": "FAIL",
        "role": "rust",
        "reason": "synthetic source-only preserved historical failure",
        "details": {
            "actual_error_type": "OfficialV14Error",
            "returncode": 2,
            "actual_worker_document": worker,
            "stdout": {
                "encoding": "hex", "bytes": len(stdout),
                "sha256": stdout_sha256, "complete_hex": stdout.hex(),
                "truncated": False,
            },
            "stderr": {
                "encoding": "hex", "bytes": 0, "sha256": empty,
                "complete_hex": "", "truncated": False,
            },
        },
        "source_sha256": V14_SOURCE_SHA256,
        "protocol_sha256": V14_PROTOCOL_SHA256,
        "immutable_v6_reference_sha256": V6_REFERENCE_SHA256,
        "synthetic": False,
        "production_observations_invented": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    failure = copy.deepcopy(base)
    failure["actual_failure_destination"] = V14_FIRST_UPSTREAM_FAILURE_RELATIVE
    raw_failure = canonical(failure) + b"\n"
    failure_sha256 = hashlib.sha256(raw_failure).hexdigest()
    receipt = {
        "schema": (
            "rebar-postfinal-cpython-full-public-locale-v14-"
            "actual-exclusive-publication-receipt"
        ),
        "path": V14_FIRST_UPSTREAM_FAILURE_RELATIVE,
        "expected_payload_sha256": failure_sha256,
        "expected_payload_bytes": len(raw_failure),
        "actual_file_created": True,
        "actual_payload_bytes_written": len(raw_failure),
        "actual_write_calls": [{
            "requested_bytes": len(raw_failure),
            "returned_bytes": len(raw_failure),
        }],
        "actual_file_fsync": True,
        "actual_directory_fsync": True,
        "canonical_reread_succeeded": True,
        "fully_durable_publication": True,
    }
    captured = copy.deepcopy(base)
    captured["actual_exclusively_preserved_failure_reports"] = [{
        "path": V14_FIRST_UPSTREAM_FAILURE_RELATIVE,
        "sha256": failure_sha256,
        "actual_exclusive_publication_receipt": receipt,
    }]
    raw_captured = canonical(captured) + b"\n"
    return failure, captured, {
        "failure_sha256": failure_sha256,
        "failure_bytes": len(raw_failure),
        "captured_sha256": hashlib.sha256(raw_captured).hexdigest(),
        "captured_bytes": len(raw_captured),
        "stdout_sha256": stdout_sha256,
        "stdout_bytes": len(stdout),
    }


def _synthetic_graph() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    counts = {"rust": 7, "vm": 2, "zig": 3}
    native_counts = {"rust": 2, "vm": 1, "zig": 2}
    sources: dict[str, tuple[str, ...]] = {}
    natives: dict[str, dict[str, str]] = {}
    source_values: dict[str, dict[str, str]] = {}
    native_values: dict[str, dict[str, str]] = {}
    for family in FAMILIES:
        paths = tuple(
            "synthetic/" + family + "/source-" + str(index)
            for index in range(counts[family])
        )
        sources[family] = paths
        source_values[family] = {
            path: _synthetic_digest("source:" + path) for path in paths
        }
        roles = {
            "role-" + str(index):
            "synthetic/" + family + "/native-" + str(index) + ".so"
            for index in range(native_counts[family])
        }
        natives[family] = roles
        native_values[family] = {
            path: _synthetic_digest("native:" + path)
            for path in roles.values()
        }
    graph = {
        "source_count": 12,
        "source_paths": [
            path for family in FAMILIES for path in sources[family]
        ],
        "source_sha256_by_family": source_values,
        "native_binary_count": 5,
        "native_sha256_by_family": native_values,
    }
    return graph, sources, natives


def _synthetic_matrix() -> list[dict[str, Any]]:
    names = [
        "SyntheticOriginal.test_method_" + str(index).zfill(3)
        for index in range(PUBLIC_METHODS)
    ]
    names[0] = "ReTests.test_large_search"
    names[1] = "ReTests.test_large_subn"
    names[-1] = "ReTests.test_memory_leaks"
    return [
        {"test": name,
         "source_ast_sha256": _synthetic_digest("original-method:" + name)}
        for name in names
    ]


def _synthetic_owner_validator(
    record: Any, family: str, expected_native: Mapping[str, str],
) -> dict[str, Any]:
    require(family in FAMILIES and isinstance(record, dict)
            and set(record) == {"family", "native_sha256_by_path", "genuine"}
            and record.get("family") == family
            and record.get("native_sha256_by_path") == dict(expected_native)
            and record.get("genuine") is True,
            "an in-memory-only synthetic real-owner shape was substituted")
    return record


def _synthetic_native_trace(
    family: str, matrix: list[dict[str, Any]],
    native: Mapping[str, str],
) -> list[dict[str, Any]]:
    return [
        {
            "method": requirement["test"],
            "phase": phase,
            "native_owner": {
                "family": family,
                "native_sha256_by_path": dict(native),
                "genuine": True,
            },
        }
        for requirement in matrix for phase in ("before", "after")
    ]


def _validate_synthetic_reference(
    document: Any, matrix: list[dict[str, Any]],
) -> dict[str, Any]:
    require(isinstance(document, dict)
            and document.get("schema")
            == "rebar-postfinal-cpython-full-public-locale-v6-self-oracle"
            and document.get("status") == "PASS"
            and document.get("synthetic") is False
            and document.get("python") == "3.14.6"
            and document.get("source_path") == V6_SOURCE_RELATIVE
            and document.get("source_sha256") == V6_SOURCE_SHA256
            and document.get("protocol_path") == V6_PROTOCOL_RELATIVE
            and document.get("protocol_sha256") == V6_PROTOCOL_SHA256
            and document.get("public_method_matrix_sha256") == METHOD_MATRIX_SHA256
            and document.get("actual_independent_reference_count") == 2
            and document.get("reference_candidate_imports") == 0
            and document.get("reference_candidate_audits_read") == 0
            and document.get("reference_candidate_proofs_read") == 0
            and document.get("reference_holdout_cases_read") == 0
            and document.get("performance") == "NOT MEASURED"
            and document.get("holdout") == "NOT ACCESSED"
            and isinstance(document.get("roles"), dict)
            and tuple(document["roles"]) == REFERENCE_LABELS
            and len(matrix) == PUBLIC_METHODS,
            "the genuine frozen double V6 reference shape was substituted")
    vectors: list[list[str]] = []
    for label in REFERENCE_LABELS:
        role = document["roles"][label]
        require(isinstance(role, dict)
                and role.get("applicable") == 151
                and role.get("passed") == 151
                and role.get("named_private_debug_skips") == 1
                and isinstance(role.get("records"), list)
                and len(role["records"]) == PUBLIC_METHODS,
                "one complete original reference or debug condition disappeared")
        vector: list[str] = []
        for requirement, record in zip(matrix, role["records"], strict=True):
            require(isinstance(record, dict)
                    and record.get("test") == requirement["test"],
                    "an original ordered frozen reference method changed")
            if requirement["test"] == "ReTests.test_memory_leaks":
                require(record.get("status") == "SKIP"
                        and record.get("reason") == "requires debug build"
                        and record.get("classification")
                        == "named-private-debug-condition",
                        "the only genuine conditional upstream skip changed")
            else:
                require(record.get("status") == "PASS",
                        "a genuine original upstream reference method did not pass")
            vector.append(record["status"])
        vectors.append(vector)
    require(vectors[0] == vectors[1]
            and document.get("reference_status_vector_sha256")
            == digest(vectors[0]),
            "the two complete genuine frozen reference vectors disagree")
    return document


def _synthetic_reference(matrix: list[dict[str, Any]]) -> dict[str, Any]:
    records = [
        ({
            "test": requirement["test"],
            "status": "SKIP",
            "reason": "requires debug build",
            "classification": "named-private-debug-condition",
        } if requirement["test"] == "ReTests.test_memory_leaks" else {
            "test": requirement["test"], "status": "PASS",
        })
        for requirement in matrix
    ]
    roles = {
        label: {
            "applicable": 151, "passed": 151,
            "named_private_debug_skips": 1,
            "records": copy.deepcopy(records),
        }
        for label in REFERENCE_LABELS
    }
    return {
        "schema": "rebar-postfinal-cpython-full-public-locale-v6-self-oracle",
        "status": "PASS", "synthetic": False, "python": "3.14.6",
        "source_path": V6_SOURCE_RELATIVE,
        "source_sha256": V6_SOURCE_SHA256,
        "protocol_path": V6_PROTOCOL_RELATIVE,
        "protocol_sha256": V6_PROTOCOL_SHA256,
        "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
        "actual_independent_reference_count": 2,
        "reference_candidate_imports": 0,
        "reference_candidate_audits_read": 0,
        "reference_candidate_proofs_read": 0,
        "reference_holdout_cases_read": 0,
        "reference_status_vector_sha256": digest(
            [record["status"] for record in records],
        ),
        "roles": roles,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    require(original is None and inventory is None and durable is None
            and not any(name in sys.modules for name in (
                "tools.postfinal_cpython_locale_oracle_v6",
                "tools.postfinal_independent_engine_audit_v21",
                "tools.postfinal_current_build_proofs_v24",
            ))
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "source-only controls must never import production controllers "
            "or any candidate")
    canonical({"prewarm": True})
    _synthetic_digest("prewarm")
    checks: list[dict[str, Any]] = []

    def accept(name: str, condition: Any) -> None:
        require(not any(row["name"] == name for row in checks),
                "a genuine V15 source-only poison control was duplicated")
        checks.append({"name": name, "passed": condition is True})

    def rejected(name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except (OfficialV15Error, AssertionError, OSError,
                UnicodeError, ValueError, TypeError, KeyError,
                ImportError, subprocess.SubprocessError):
            accept(name, True)
        else:
            accept(name, False)

    with _source_only_boundary() as effects:
        matrix = _synthetic_matrix()
        reference = _synthetic_reference(matrix)
        synthetic_v12_failure, synthetic_v12_capture, synthetic_v12_pins = (
            _synthetic_v12_first_upstream_failure()
        )
        preserved_synthetic_v12 = _validate_preserved_v12_first_upstream_failure(
            synthetic_v12_failure,
            synthetic_v12_capture,
            **synthetic_v12_pins,
        )
        accept("freeze-actual-failed-v12-controller-without-reading-source",
               V12_SOURCE_SHA256
               == "c678d02dd906953d320ef0da4b9f0216750c33b81663107127082a98d09e8b64"
               and V12_PROTOCOL_SHA256
               == "2d3da88d31a131f3452c3a884df5285775fd9af9e794339af870f02ed249c00c")
        accept("freeze-root-published-actual-first-v12-failure-without-reading",
               V12_FIRST_UPSTREAM_FAILURE_SHA256
               == "fda1204c92f843f3610231f33f1271e113374a5dec8fcfa30e1778658655439e"
               and V12_FIRST_UPSTREAM_FAILURE_BYTES == 6_007)
        accept("freeze-root-published-actual-v12-captured-output-without-reading",
               V12_FIRST_UPSTREAM_CAPTURE_SHA256
               == "a9dec1d4798472773a54cb164c6a68d8026e09bc6edd2ab640916fadc5f10dff"
               and V12_FIRST_UPSTREAM_CAPTURE_BYTES == 6_706)
        accept("freeze-complete-actual-v12-failed-worker-without-inventing-bytes",
               V12_FIRST_UPSTREAM_STDOUT_SHA256
               == "92f2d44e311de751c6caddc0f84d1c6a72c8c449522fef2dadf5a9a1a78406a7"
               and V12_FIRST_UPSTREAM_STDOUT_BYTES == 1_221)
        accept("validate-complete-v12-failure-shape-only-in-synthetic-memory",
               preserved_synthetic_v12["status"] == "FAIL"
               and preserved_synthetic_v12["worker_returncode"] == 2
               and preserved_synthetic_v12[
                   "completed_original_method_count"
               ] == 0
               and preserved_synthetic_v12[
                   "historical_failure_qualifies_current_engine"
               ] is False)
        for key in ("schema", "status", "role", "source_sha256",
                    "protocol_sha256", "actual_failure_destination"):
            altered = copy.deepcopy(synthetic_v12_failure)
            altered[key] = "FORGED"
            rejected("reject-forged-first-v12-upstream-failure:" + key,
                     lambda altered=altered:
                     _validate_preserved_v12_first_upstream_failure(
                         altered, synthetic_v12_capture, **synthetic_v12_pins,
                     ))
        for key in ("actual_error_type", "returncode", "stdout", "stderr",
                    "actual_worker_document"):
            altered = copy.deepcopy(synthetic_v12_capture)
            altered["details"][key] = "FORGED"
            rejected("reject-lost-genuine-first-v12-worker-observation:" + key,
                     lambda altered=altered:
                     _validate_preserved_v12_first_upstream_failure(
                         synthetic_v12_failure, altered, **synthetic_v12_pins,
                     ))
        for key in synthetic_v12_capture[
            "actual_exclusively_preserved_failure_reports"
        ][0]["actual_exclusive_publication_receipt"]:
            altered = copy.deepcopy(synthetic_v12_capture)
            altered["actual_exclusively_preserved_failure_reports"][0][
                "actual_exclusive_publication_receipt"
            ].pop(key)
            rejected("reject-omitted-real-v12-failure-receipt-field:" + key,
                     lambda altered=altered:
                     _validate_preserved_v12_first_upstream_failure(
                         synthetic_v12_failure, altered, **synthetic_v12_pins,
                     ))
        synthetic_v13_failure, synthetic_v13_capture, synthetic_v13_pins = (
            _synthetic_v13_first_upstream_failure()
        )
        preserved_synthetic_v13 = _validate_preserved_v13_first_upstream_failure(
            synthetic_v13_failure,
            synthetic_v13_capture,
            **synthetic_v13_pins,
        )
        accept("freeze-actual-failed-v13-controller-without-reading-source",
               V13_SOURCE_SHA256
               == "5f9ca285ba617308dead53b97a6d6c707bd4371b7cad79345da8b99223260015"
               and V13_PROTOCOL_SHA256
               == "7ab886971b63faddecb56f4403a582d48903fbb228bc0fccdca80c46f5c4c0dc")
        accept("freeze-root-published-actual-v13-import-failure-without-reading",
               V13_FIRST_UPSTREAM_FAILURE_SHA256
               == "18f572e44382130fe6ae29a05bb4c063fccf95d92fc305c9548cb1a63ac01844"
               and V13_FIRST_UPSTREAM_FAILURE_BYTES == 9_479)
        accept("freeze-root-published-actual-v13-captured-output-without-reading",
               V13_FIRST_UPSTREAM_CAPTURE_SHA256
               == "7ae58265f0b845b9f50b30fcb7c7c75018cbcb40d49d240760373a517c2b46c1"
               and V13_FIRST_UPSTREAM_CAPTURE_BYTES == 10_178)
        accept("freeze-genuine-2089-byte-v13-failed-worker-without-reading",
               V13_FIRST_UPSTREAM_STDOUT_SHA256
               == "2df0a9a95f40a3e2dd3c3ee87ccbd4c36567b8c27b660f55ebcacd828c2ea160"
               and V13_FIRST_UPSTREAM_STDOUT_BYTES == 2_089)
        accept("validate-genuine-stage07-v13-import-failure-only-in-memory",
               preserved_synthetic_v13["status"] == "FAIL"
               and preserved_synthetic_v13["worker_returncode"] == 2
               and preserved_synthetic_v13["completed_original_method_count"]
               == 0
               and preserved_synthetic_v13[
                   "historical_failure_qualifies_current_engine"
               ] is False
               and synthetic_v13_capture["details"]["actual_worker_document"][
                   "details"
               ]["actual_error"] == "stage-07 blocked unowned matching import: re")
        for key in ("schema", "status", "role", "source_sha256",
                    "protocol_sha256", "actual_failure_destination"):
            altered_v13 = copy.deepcopy(synthetic_v13_failure)
            altered_v13[key] = "FORGED"
            rejected("reject-forged-actual-first-v13-upstream-failure:" + key,
                     lambda altered_v13=altered_v13:
                     _validate_preserved_v13_first_upstream_failure(
                         altered_v13, synthetic_v13_capture,
                         **synthetic_v13_pins,
                     ))
        for key in ("actual_error_type", "returncode", "stdout", "stderr",
                    "actual_worker_document"):
            altered_v13 = copy.deepcopy(synthetic_v13_capture)
            altered_v13["details"][key] = "FORGED"
            rejected("reject-forged-actual-v13-original-worker-capture:" + key,
                     lambda altered_v13=altered_v13:
                     _validate_preserved_v13_first_upstream_failure(
                         synthetic_v13_failure, altered_v13,
                         **synthetic_v13_pins,
                     ))
        for key in synthetic_v13_capture[
            "actual_exclusively_preserved_failure_reports"
        ][0]["actual_exclusive_publication_receipt"]:
            altered_v13 = copy.deepcopy(synthetic_v13_capture)
            altered_v13["actual_exclusively_preserved_failure_reports"][0][
                "actual_exclusive_publication_receipt"
            ].pop(key)
            rejected("reject-omitted-actual-v13-exclusive-receipt-field:" + key,
                     lambda altered_v13=altered_v13:
                     _validate_preserved_v13_first_upstream_failure(
                         synthetic_v13_failure, altered_v13,
                         **synthetic_v13_pins,
                     ))
        synthetic_v14_failure, synthetic_v14_capture, synthetic_v14_pins = (
            _synthetic_v14_first_upstream_failure()
        )
        preserved_synthetic_v14 = _validate_preserved_v14_first_upstream_failure(
            synthetic_v14_failure,
            synthetic_v14_capture,
            **synthetic_v14_pins,
        )
        accept("freeze-actual-failed-v14-controller-without-reading-source",
               V14_SOURCE_SHA256
               == "834abdda264bfc81ecf5d6712e524ce1c852b84ed7d8f69cfc26aba6a9ebeb42"
               and V14_PROTOCOL_SHA256
               == "68d8a9044540b0bfeca86316fd4fedded23587333370903d818fce9cc8cf33f9")
        accept("freeze-actual-v14-candidate-context-failure-without-reading",
               V14_FIRST_UPSTREAM_FAILURE_SHA256
               == "81112de149d835befaf605419d7426355a4be5d82d97f696d956bcd82627cd8f"
               and V14_FIRST_UPSTREAM_FAILURE_BYTES == 9_023)
        accept("freeze-actual-v14-complete-production-summary-without-reading",
               V14_FIRST_UPSTREAM_CAPTURE_SHA256
               == "6390b27630888ea1dc77b3d65decb7680b32f7df859dfde8f227a92dc4b1951d"
               and V14_FIRST_UPSTREAM_CAPTURE_BYTES == 9_722)
        accept("freeze-actual-v14-candidate-free-proof-error-worker-stream",
               V14_FIRST_UPSTREAM_STDOUT_SHA256
               == "6a9273b3fb308dad3bd803cf299f64571378ba1b1c9a545b3ee6653733348b57"
               and V14_FIRST_UPSTREAM_STDOUT_BYTES == 1_975)
        accept("preserve-actual-v14-prohibited-candidate-snapshot-in-memory",
               preserved_synthetic_v14["status"] == "FAIL"
               and preserved_synthetic_v14["worker_returncode"] == 2
               and preserved_synthetic_v14[
                   "completed_original_method_count"
               ] == 0
               and preserved_synthetic_v14[
                   "historical_failure_qualifies_current_engine"
               ] is False
               and synthetic_v14_capture["details"][
                   "actual_worker_document"
               ]["details"]["actual_error_type"] == "ProofV11Error"
               and synthetic_v14_capture["details"][
                   "actual_worker_document"
               ]["details"]["actual_error"]
               == "the V11 correctness controller must never import a candidate")
        for key in ("schema", "status", "role", "source_sha256",
                    "protocol_sha256", "actual_failure_destination"):
            changed_v14 = copy.deepcopy(synthetic_v14_failure)
            changed_v14[key] = "FORGED"
            rejected("reject-forged-genuine-v14-upstream-failure:" + key,
                     lambda changed_v14=changed_v14:
                     _validate_preserved_v14_first_upstream_failure(
                         changed_v14, synthetic_v14_capture,
                         **synthetic_v14_pins,
                     ))
        for key in ("actual_error_type", "returncode", "stdout", "stderr",
                    "actual_worker_document"):
            changed_v14 = copy.deepcopy(synthetic_v14_capture)
            changed_v14["details"][key] = "FORGED"
            rejected("reject-forged-genuine-v14-snapshot-worker-capture:" + key,
                     lambda changed_v14=changed_v14:
                     _validate_preserved_v14_first_upstream_failure(
                         synthetic_v14_failure, changed_v14,
                         **synthetic_v14_pins,
                     ))
        for key in synthetic_v14_capture[
            "actual_exclusively_preserved_failure_reports"
        ][0]["actual_exclusive_publication_receipt"]:
            changed_v14 = copy.deepcopy(synthetic_v14_capture)
            changed_v14["actual_exclusively_preserved_failure_reports"][0][
                "actual_exclusive_publication_receipt"
            ].pop(key)
            rejected("reject-omitted-genuine-v14-durable-receipt-field:" + key,
                     lambda changed_v14=changed_v14:
                     _validate_preserved_v14_first_upstream_failure(
                         synthetic_v14_failure, changed_v14,
                         **synthetic_v14_pins,
                     ))
        authentic_failure_shape = dict(V13_FIRST_FAILURE_FIELDS)
        authentic_v15_failure_shape = dict(V15_FIRST_FAILURE_FIELDS)
        authentic_v17_failure_shape = copy.deepcopy(V17_FIRST_FAILURE_FIELDS)
        authentic_v19_failure_shape = copy.deepcopy(V19_FIRST_FAILURE_FIELDS)
        synthetic_historical_pins = {
            "audit_source": V21_SOURCE_SHA256,
            "audit_protocol": V21_PROTOCOL_SHA256,
            "base_report": _synthetic_digest("v22-source-only-base-report"),
            "strict_report": _synthetic_digest("v22-source-only-strict-report"),
        }
        synthetic_v22_failure_shape = copy.deepcopy(V22_FIRST_FAILURE_FIELDS)
        synthetic_v22_failure_shape.update({
            "actual_invocation": {
                "executable": str(PINNED_CPYTHON),
                "python_flags": ["-I", "-B", "-c"],
                "environment": {
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "PYTHONHASHSEED": "0",
                    "PYTHONPATH": str(ROOT),
                    "LC_ALL": "C",
                    "PATH": "/usr/bin:/bin",
                },
                "exit_code": 1,
                "output_capture": (
                    "complete combined traceback; stdout and stderr "
                    "were not separately captured"
                ),
                "actual_inline_python_source_lines": [
                    "synthetic-source-only-inline-line:" + str(index)
                    for index in range(25)
                ],
            },
            "frozen_failed_controller": copy.deepcopy(
                V22_FAILED_CONTROLLER_FIELDS,
            ),
            "actual_passing_prerequisites": {
                "audit_source_sha256": V21_SOURCE_SHA256,
                "audit_protocol_sha256": V21_PROTOCOL_SHA256,
                "base_report_path": (
                    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V21.json"
                ),
                "base_report_sha256": synthetic_historical_pins[
                    "base_report"
                ],
                "strict_report_path": (
                    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V21.json"
                ),
                "strict_report_sha256": synthetic_historical_pins[
                    "strict_report"
                ],
                "both_independent_ownership_audits_passed": True,
            },
            "actual_combined_traceback_lines": [
                "synthetic-source-only-combined-traceback-line:" + str(index)
                for index in range(24)
            ],
            "actual_historical_summary_mismatch": copy.deepcopy(
                V22_HISTORICAL_MISMATCH_FIELDS,
            ),
            "independent_follow_up_differential": {
                "status": "PASS",
                "validation_scope": (
                    "read-only authentication of the exact published V21 "
                    "reports and all four historical summary shapes only"
                ),
                "read_only_boundary_effects": copy.deepcopy(
                    V22_FOLLOW_UP_READ_ONLY_EFFECTS,
                ),
            },
        })
        historic_audits = {
            "pins": copy.deepcopy(synthetic_historical_pins),
            "history": {
                "preserved_v13_first_audit_failure": copy.deepcopy(
                    authentic_failure_shape,
                ),
                "preserved_v15_first_audit_failure": copy.deepcopy(
                    authentic_v15_failure_shape,
                ),
                "preserved_v17_first_audit_failure": copy.deepcopy(
                    authentic_v17_failure_shape,
                ),
                "preserved_v19_first_audit_failure": copy.deepcopy(
                    authentic_v19_failure_shape,
                ),
            },
            "preserved_v13_failure": copy.deepcopy(authentic_failure_shape),
            "preserved_v15_failure": copy.deepcopy(authentic_v15_failure_shape),
            "preserved_v17_failure": copy.deepcopy(authentic_v17_failure_shape),
            "preserved_v19_failure": copy.deepcopy(authentic_v19_failure_shape),
        }
        historic_state = {
            "audits": historic_audits,
            "preserved_incidents": {
                "v13_first_owner_preflight_failure": copy.deepcopy(
                    authentic_failure_shape,
                ),
                "v13_first_owner_preflight_failure_qualifies_current_engine": (
                    False
                ),
                "v15_first_owner_preflight_failure": copy.deepcopy(
                    authentic_v15_failure_shape,
                ),
                "v15_first_owner_preflight_failure_qualifies_current_engine": (
                    False
                ),
                "v17_first_owner_postflight_failure": copy.deepcopy(
                    authentic_v17_failure_shape,
                ),
                "v17_first_owner_postflight_failure_qualifies_current_engine": (
                    False
                ),
                "v19_first_owner_publication_failure": copy.deepcopy(
                    authentic_v19_failure_shape,
                ),
                "v19_first_owner_publication_failure_qualifies_current_engine": (
                    False
                ),
                "v22_first_proof_preflight_failure": copy.deepcopy(
                    synthetic_v22_failure_shape,
                ),
                "v22_first_proof_preflight_failure_qualifies_current_engine": (
                    False
                ),
                "historical_v10_graph_qualifies_current_engine": False,
            },
        }
        accept("preserve-root-published-exact-real-first-v13-failure-shape",
               _validate_preserved_v13_failure(
                   historic_audits, historic_state,
               ) == authentic_failure_shape)
        accept("freeze-actual-real-v13-preflight-failure-without-opening-it",
               V13_FIRST_FAILURE_SHA256
               == "465820b50be4d544199844d7bde4c5b8e58391828bdb1c716cc33c50ca6c964b")
        accept("preserve-root-published-exact-real-first-v15-failure-shape",
               _validate_preserved_v15_failure(
                   historic_audits, historic_state,
               ) == authentic_v15_failure_shape)
        accept("freeze-actual-real-v15-preflight-failure-without-opening-it",
               V15_FIRST_FAILURE_SHA256
               == "a3695f1fd847e9ad882783d18c519b551d7791c5327f55964e202a31ade818ff")
        accept("preserve-root-published-exact-real-first-v17-failure-shape",
               _validate_preserved_v17_failure(
                   historic_audits, historic_state,
               ) == authentic_v17_failure_shape)
        accept("freeze-actual-real-v17-postflight-failure-without-opening-it",
               V17_FIRST_FAILURE_SHA256
               == "8aa1021ba4fc9dcb2456f05c174214c8c7f6c8f4fa2215a13c3373f00e5f557d")
        accept("preserve-root-published-exact-real-first-v19-failure-shape",
               _validate_preserved_v19_failure(
                   historic_audits, historic_state,
               ) == authentic_v19_failure_shape)
        accept("freeze-actual-v19-exclusive-failure-without-opening-it",
               V19_FIRST_FAILURE_SHA256
               == "6d4d73c153bcf1995db78fb4b90ce2851bdece3b13748c75ae045bd1081af390")
        accept("freeze-root-published-fifth-v22-failure-without-opening-it",
               V22_FIRST_FAILURE_SHA256
               == "c6e765f142f25667dd0e7dab45ff16a60abcaae6e230ba05acc596a72d304b01")
        accept("freeze-failed-v22-source-as-historical-provenance-only",
               V22_FAILURE_SOURCE_SHA256
               == "ba3062b5fe4aea944e89022266c8d9a7a035708bb30d736f074fc29ce7157e27")
        accept("freeze-failed-v22-protocol-as-historical-provenance-only",
               V22_FAILURE_PROTOCOL_SHA256
               == "e06a24155ca95bf287a5dece90d1a385dad806de8512f177d3146c7bba7acc29")
        accept("preserve-v22-exact-25-document-and-27-normalized-fields",
               len(V22_FIRST_FAILURE_KEYS) == 27
               and len(synthetic_v22_failure_shape) == 27
               and len(set(synthetic_v22_failure_shape)
                       - {"source_path", "sha256"}) == 25)
        accept("preserve-fifth-v22-proof-failure-outside-four-v21-histories",
               len(historic_audits["history"]) == 4
               and "preserved_v22_first_audit_failure"
               not in historic_audits["history"]
               and _validate_preserved_v22_proof_failure(historic_state)
               == synthetic_v22_failure_shape)
        accept("preserve-five-failures-and-historical-graph-as-nonqualifying",
               len(V24_REQUIRED_NONQUALIFYING_FLAGS) == 6
               and all(historic_state["preserved_incidents"].get(flag)
                       is False
                       for flag in V24_REQUIRED_NONQUALIFYING_FLAGS))
        accept("preserve-authentic-long-v13-stage-in-fifth-v22-mismatch",
               V13_FIRST_FAILURE_FIELDS["failed_stage"]
               == "historical-zig-edge-authentication-before-any-new-native-owner-worker"
               and V22_HISTORICAL_MISMATCH_FIELDS[
                   "actual_authenticated_v21_value"
               ] == V13_FIRST_FAILURE_FIELDS["failed_stage"])
        accept("preserve-genuine-v22-inline-25-and-combined-traceback-24",
               len(synthetic_v22_failure_shape["actual_invocation"][
                   "actual_inline_python_source_lines"
               ]) == 25
               and len(synthetic_v22_failure_shape[
                   "actual_combined_traceback_lines"
               ]) == 24
               and synthetic_v22_failure_shape[
                   "actual_combined_traceback_line_count"
               ] == 24)
        accept("preserve-v22-lost-original-failed-invocation-boundary",
               synthetic_v22_failure_shape[
                   "actual_failed_invocation_boundary_counters"
               ] == "NOT PRESERVED BY THE FAILED CONTROLLER")
        accept("preserve-independent-v22-follow-up-five-zero-effects",
               len(V22_FOLLOW_UP_READ_ONLY_EFFECTS) == 5
               and all(type(value) is int and value == 0
                       for value in V22_FOLLOW_UP_READ_ONLY_EFFECTS.values())
               and synthetic_v22_failure_shape[
                   "independent_follow_up_differential"
               ]["read_only_boundary_effects"]
               == V22_FOLLOW_UP_READ_ONLY_EFFECTS)
        synthetic_v24_proof = types.SimpleNamespace(
            expected_v22_failure_summary=lambda pins: (
                copy.deepcopy(synthetic_v22_failure_shape)
                if pins == synthetic_historical_pins else None
            ),
        )
        accept("bind-complete-fifth-incident-to-independent-v24-summary",
               _validate_preserved_v22_proof_failure(
                   historic_state, synthetic_v24_proof,
               ) == synthetic_v22_failure_shape)
        accept("freeze-real-durable-v19-report-without-reading-its-bytes",
               V19_DURABLE_REPORT_SHA256
               == "e46484d4a8b389fde66131ac3f8c2db94b1a95ebbf35760f1602117e8c9f23c6"
               and V19_DURABLE_REPORT_BYTES == 161_316)
        accept("preserve-v19-real-three-owner-streams-without-rerunning-them",
               set(authentic_v19_failure_shape[
                   "actual_original_native_owner_workers"
               ]) == set(FAMILIES)
               and authentic_v19_failure_shape[
                   "completed_native_owner_worker_count"
               ] == 3
               and authentic_v19_failure_shape[
                   "complete_actual_native_owner_streams_preserved"
               ] is True)
        accept("reject-embedded-v19-pass-after-real-outer-controller-failure",
               authentic_v19_failure_shape[
                   "durable_embedded_document_status"
               ] == "PASS"
               and authentic_v19_failure_shape[
                   "actual_controller_status"
               ] == "FAIL"
               and authentic_v19_failure_shape["exit_code"] == 1
               and authentic_v19_failure_shape[
                   "embedded_pass_qualifies_current_engine"
               ] is False
               and authentic_v19_failure_shape[
                   "historical_failure_qualifies_current_build"
               ] is False)
        accept("preserve-real-v19-full-fsync-and-failed-canonical-reread",
               authentic_v19_failure_shape["exclusive_create_succeeded"] is True
               and authentic_v19_failure_shape["file_fsync_succeeded"] is True
               and authentic_v19_failure_shape[
                   "parent_directory_fsync_succeeded"
               ] is True
               and authentic_v19_failure_shape[
                   "canonical_reread_succeeded"
               ] is False
               and authentic_v19_failure_shape[
                   "original_non_roundtripping_in_memory_value"
               ] == "NOT PRESERVED BY THE FAILED CONTROLLER")
        accept("preserve-real-three-v17-owner-families-without-inventing-bytes",
               authentic_v17_failure_shape[
                   "actual_completed_native_owner_families"
               ] == ["rust", "vm", "zig"]
               and authentic_v17_failure_shape[
                   "actual_native_owner_workers_completed"
               ] == 3
               and authentic_v17_failure_shape[
                   "actual_native_owner_observations"
               ] == "NOT PRESERVED BY THE FAILED CONTROLLER")
        accept("preserve-real-v17-merged-output-without-inventing-streams",
               authentic_v17_failure_shape[
                   "actual_captured_combined_output_lines"
               ] == 27
               and "combined_traceback_sha256"
               not in authentic_v17_failure_shape
               and "actual_native_owner_stdout"
               not in authentic_v17_failure_shape
               and "actual_native_owner_stderr"
               not in authentic_v17_failure_shape)
        accept("preserve-real-v13-merged-traceback-without-inventing-bytes",
               "combined_traceback_sha256" not in authentic_failure_shape
               and authentic_failure_shape[
                   "combined_traceback_separately_captured"
               ] is False)
        accept("preserve-real-v15-merged-traceback-without-inventing-bytes",
               "combined_traceback_sha256" not in authentic_v15_failure_shape
               and authentic_v15_failure_shape[
                   "combined_traceback_separately_captured"
               ] is False)
        accept("bind-real-first-v15-failure-to-genuine-first-v13-ancestry",
               authentic_v15_failure_shape["preserved_v13_first_failure_path"]
               == authentic_failure_shape["failure_path"]
               and authentic_v15_failure_shape[
                   "preserved_v13_first_failure_sha256"
               ] == authentic_failure_shape["failure_sha256"])
        withdrawn_short_v13 = copy.deepcopy(historic_audits)
        withdrawn_short_v13["preserved_v13_failure"]["failed_stage"] = (
            "historical-zig-edge-preflight"
        )
        withdrawn_short_v13["history"][
            "preserved_v13_first_audit_failure"
        ] = copy.deepcopy(withdrawn_short_v13["preserved_v13_failure"])
        rejected("reject-withdrawn-incorrect-short-historical-v13-stage",
                 lambda: _validate_preserved_v13_failure(
                     withdrawn_short_v13,
                 ))
        for key, expected in V22_FIRST_FAILURE_FIELDS.items():
            changed = copy.deepcopy(historic_state)
            wrong: Any = (
                "0" * 64 if key == "sha256"
                else (not expected if type(expected) is bool
                      else (expected + 1 if type(expected) is int
                            else "FORGED"))
            )
            changed["preserved_incidents"][
                "v22_first_proof_preflight_failure"
            ][key] = wrong
            rejected("reject-every-forged-real-fifth-v22-failure-field:"
                     + key,
                     lambda changed=changed:
                     _validate_preserved_v22_proof_failure(
                         changed, synthetic_v24_proof,
                     ))
        for key in sorted(V22_FIRST_FAILURE_KEYS):
            omitted = copy.deepcopy(historic_state)
            omitted["preserved_incidents"][
                "v22_first_proof_preflight_failure"
            ].pop(key)
            rejected("reject-every-omitted-fifth-v22-normalized-field:"
                     + key,
                     lambda omitted=omitted:
                     _validate_preserved_v22_proof_failure(
                         omitted, synthetic_v24_proof,
                     ))
        for section in (
            "actual_invocation",
            "frozen_failed_controller",
            "actual_passing_prerequisites",
            "actual_historical_summary_mismatch",
            "independent_follow_up_differential",
        ):
            for key, expected in synthetic_v22_failure_shape[section].items():
                changed = copy.deepcopy(historic_state)
                wrong = (
                    not expected if type(expected) is bool
                    else (expected + 1 if type(expected) is int else "FORGED")
                )
                changed["preserved_incidents"][
                    "v22_first_proof_preflight_failure"
                ][section][key] = wrong
                rejected("reject-forged-fifth-v22-nested-original-field:"
                         + section + ":" + key,
                         lambda changed=changed:
                         _validate_preserved_v22_proof_failure(
                             changed, synthetic_v24_proof,
                         ))
        for key in V22_FOLLOW_UP_READ_ONLY_EFFECTS:
            changed = copy.deepcopy(historic_state)
            changed["preserved_incidents"][
                "v22_first_proof_preflight_failure"
            ]["independent_follow_up_differential"][
                "read_only_boundary_effects"
            ][key] = 1
            rejected("reject-forged-independent-v22-follow-up-effect:" + key,
                     lambda changed=changed:
                     _validate_preserved_v22_proof_failure(
                         changed, synthetic_v24_proof,
                     ))
            boolean_counter = copy.deepcopy(historic_state)
            boolean_counter["preserved_incidents"][
                "v22_first_proof_preflight_failure"
            ]["independent_follow_up_differential"][
                "read_only_boundary_effects"
            ][key] = False
            rejected("reject-boolean-v22-independent-read-only-counter:"
                     + key,
                     lambda boolean_counter=boolean_counter:
                     _validate_preserved_v22_proof_failure(
                         boolean_counter, synthetic_v24_proof,
                     ))
        for section, key in (
            ("actual_passing_prerequisites",
             "both_independent_ownership_audits_passed"),
            ("actual_historical_summary_mismatch", "other_fields_match"),
        ):
            integer_boolean = copy.deepcopy(historic_state)
            integer_boolean["preserved_incidents"][
                "v22_first_proof_preflight_failure"
            ][section][key] = 1
            rejected("reject-integer-as-genuine-v22-historical-boolean:"
                     + section + ":" + key,
                     lambda integer_boolean=integer_boolean:
                     _validate_preserved_v22_proof_failure(
                         integer_boolean, synthetic_v24_proof,
                     ))
        for invented_key in (
            "stdout_capture",
            "stderr_capture",
            "stdout_sha256",
            "stderr_sha256",
            "combined_traceback_sha256",
            "actual_native_owner_observations",
            "actual_original_edge_observations",
            "actual_original_deep_observations",
        ):
            invented = copy.deepcopy(historic_state)
            invented["preserved_incidents"][
                "v22_first_proof_preflight_failure"
            ][invented_key] = "FORGED"
            rejected("reject-invented-lost-v22-original-observation:"
                     + invented_key,
                     lambda invented=invented:
                     _validate_preserved_v22_proof_failure(
                         invented, synthetic_v24_proof,
                     ))
        for section, nested in (
            ("actual_combined_traceback_lines", None),
            ("actual_invocation", "actual_inline_python_source_lines"),
        ):
            changed = copy.deepcopy(historic_state)
            failure = changed["preserved_incidents"][
                "v22_first_proof_preflight_failure"
            ]
            lines = failure[section] if nested is None else failure[section][nested]
            lines[0] += ":FORGED"
            rejected("reject-substitution-of-complete-fifth-v22-lines:"
                     + section,
                     lambda changed=changed:
                     _validate_preserved_v22_proof_failure(
                         changed, synthetic_v24_proof,
                     ))
        for misplaced_key in (
            "preserved_v22_first_audit_failure",
            "v22_first_proof_preflight_failure",
        ):
            contaminated = copy.deepcopy(historic_state)
            contaminated["audits"]["history"][misplaced_key] = (
                copy.deepcopy(synthetic_v22_failure_shape)
            )
            rejected("reject-later-v22-incident-inside-immutable-v21-history:"
                     + misplaced_key,
                     lambda contaminated=contaminated:
                     _validate_preserved_v22_proof_failure(
                         contaminated, synthetic_v24_proof,
                     ))
        for flag in V24_REQUIRED_NONQUALIFYING_FLAGS:
            omitted_flag = copy.deepcopy(historic_state)
            omitted_flag["preserved_incidents"].pop(flag)
            rejected("reject-omitted-v24-authentic-nonqualification-flag:"
                     + flag,
                     lambda omitted_flag=omitted_flag:
                     _validate_preserved_v22_proof_failure(
                         omitted_flag, synthetic_v24_proof,
                     ))
            qualifying_flag = copy.deepcopy(historic_state)
            qualifying_flag["preserved_incidents"][flag] = True
            rejected("reject-v24-historical-failure-claiming-qualification:"
                     + flag,
                     lambda qualifying_flag=qualifying_flag:
                     _validate_preserved_v22_proof_failure(
                         qualifying_flag, synthetic_v24_proof,
                     ))
            integer_flag = copy.deepcopy(historic_state)
            integer_flag["preserved_incidents"][flag] = 0
            rejected("reject-v24-integer-historical-nonqualification-flag:"
                     + flag,
                     lambda integer_flag=integer_flag:
                     _validate_preserved_v22_proof_failure(
                         integer_flag, synthetic_v24_proof,
                     ))
        falsely_qualifying_v22 = copy.deepcopy(historic_state)
        falsely_qualifying_v22["preserved_incidents"][
            "v22_first_proof_preflight_failure_qualifies_current_engine"
        ] = True
        rejected("reject-v22-fifth-failure-as-current-engine-qualification",
                 lambda: _validate_preserved_v22_proof_failure(
                     falsely_qualifying_v22, synthetic_v24_proof,
                 ))
        missing_v24_v22_validator = types.SimpleNamespace()
        rejected("reject-v24-without-independent-complete-v22-validator",
                 lambda: _validate_preserved_v22_proof_failure(
                     historic_state, missing_v24_v22_validator,
                 ))
        forged_v24_v22_validator = types.SimpleNamespace(
            expected_v22_failure_summary=lambda pins: {},
        )
        rejected("reject-v24-forged-independent-complete-v22-summary",
                 lambda: _validate_preserved_v22_proof_failure(
                     historic_state, forged_v24_v22_validator,
                 ))
        for key, expected in V13_FIRST_FAILURE_FIELDS.items():
            altered = copy.deepcopy(historic_audits)
            wrong: Any = (
                "0" * 64 if key.endswith("_sha256")
                else (not expected if type(expected) is bool
                      else (expected + 1 if type(expected) is int else "FORGED"))
            )
            altered["preserved_v13_failure"][key] = wrong
            altered["history"]["preserved_v13_first_audit_failure"] = (
                copy.deepcopy(altered["preserved_v13_failure"])
            )
            rejected("reject-fabricated-real-first-v13-failure:" + key,
                     lambda altered=altered:
                     _validate_preserved_v13_failure(altered))
        for key, expected in V15_FIRST_FAILURE_FIELDS.items():
            altered = copy.deepcopy(historic_audits)
            wrong: Any = (
                "0" * 64 if key.endswith("_sha256")
                else (not expected if type(expected) is bool
                      else (expected + 1 if type(expected) is int else "FORGED"))
            )
            altered["preserved_v15_failure"][key] = wrong
            altered["history"]["preserved_v15_first_audit_failure"] = (
                copy.deepcopy(altered["preserved_v15_failure"])
            )
            rejected("reject-fabricated-real-first-v15-failure:" + key,
                     lambda altered=altered:
                     _validate_preserved_v15_failure(altered))
        for key, expected in V17_FIRST_FAILURE_FIELDS.items():
            altered = copy.deepcopy(historic_audits)
            wrong: Any = (
                "0" * 64 if key == "sha256"
                else (not expected if type(expected) is bool
                      else (expected + 1 if type(expected) is int
                            else (list(reversed(expected))
                                  if isinstance(expected, list)
                                  else "FORGED")))
            )
            altered["preserved_v17_failure"][key] = wrong
            altered["history"]["preserved_v17_first_audit_failure"] = (
                copy.deepcopy(altered["preserved_v17_failure"])
            )
            rejected("reject-fabricated-real-first-v17-failure:" + key,
                     lambda altered=altered:
                     _validate_preserved_v17_failure(altered))
        for key, expected in V19_FIRST_FAILURE_FIELDS.items():
            altered = copy.deepcopy(historic_audits)
            wrong: Any = (
                "0" * 64 if key.endswith("sha256")
                else (not expected if type(expected) is bool
                      else (expected + 1 if type(expected) is int
                            else ({} if isinstance(expected, dict)
                                  else ([] if isinstance(expected, list)
                                        else "FORGED"))))
            )
            altered["preserved_v19_failure"][key] = wrong
            altered["history"]["preserved_v19_first_audit_failure"] = (
                copy.deepcopy(altered["preserved_v19_failure"])
            )
            rejected("reject-fabricated-real-first-v19-failure:" + key,
                     lambda altered=altered:
                     _validate_preserved_v19_failure(altered))
        for family in FAMILIES:
            for key, expected in V19_FIRST_FAILURE_FIELDS[
                "actual_original_native_owner_workers"
            ][family].items():
                altered = copy.deepcopy(historic_audits)
                wrong: Any = (
                    "0" * 64 if key.endswith("sha256")
                    else (not expected if type(expected) is bool
                          else (expected + 1 if type(expected) is int
                                else "FORGED"))
                )
                altered["preserved_v19_failure"][
                    "actual_original_native_owner_workers"
                ][family][key] = wrong
                altered["history"]["preserved_v19_first_audit_failure"] = (
                    copy.deepcopy(altered["preserved_v19_failure"])
                )
                rejected("reject-fabricated-real-v19-owner-stream:"
                         + family + ":" + key,
                         lambda altered=altered:
                         _validate_preserved_v19_failure(altered))
        for key in (
            "combined_traceback_sha256", "actual_native_owner_stdout",
            "actual_native_owner_stderr", "actual_native_owner_proofs",
            "actual_native_owner_returncodes", "stdout_capture",
            "stderr_capture",
        ):
            fabricated = copy.deepcopy(historic_audits)
            fabricated["preserved_v17_failure"][key] = "FORGED"
            fabricated["history"]["preserved_v17_first_audit_failure"] = (
                copy.deepcopy(fabricated["preserved_v17_failure"])
            )
            rejected("reject-invented-lost-v17-native-observation:" + key,
                     lambda fabricated=fabricated:
                     _validate_preserved_v17_failure(fabricated))
        omitted_history = copy.deepcopy(historic_audits)
        omitted_history["history"].pop("preserved_v13_first_audit_failure")
        rejected("reject-concealed-historical-v13-preflight-failure",
                 lambda: _validate_preserved_v13_failure(omitted_history))
        omitted_v15_history = copy.deepcopy(historic_audits)
        omitted_v15_history["history"].pop(
            "preserved_v15_first_audit_failure",
        )
        rejected("reject-concealed-historical-v15-preflight-failure",
                 lambda: _validate_preserved_v15_failure(omitted_v15_history))
        omitted_v17_history = copy.deepcopy(historic_audits)
        omitted_v17_history["history"].pop(
            "preserved_v17_first_audit_failure",
        )
        rejected("reject-concealed-historical-v17-postflight-failure",
                 lambda: _validate_preserved_v17_failure(omitted_v17_history))
        omitted_v19_history = copy.deepcopy(historic_audits)
        omitted_v19_history["history"].pop(
            "preserved_v19_first_audit_failure",
        )
        rejected("reject-concealed-real-v19-durable-publication-failure",
                 lambda: _validate_preserved_v19_failure(omitted_v19_history))
        omitted_traceback = copy.deepcopy(historic_audits)
        for key in tuple(omitted_traceback["preserved_v13_failure"]):
            if key.startswith("combined_traceback_"):
                omitted_traceback["preserved_v13_failure"].pop(key)
        omitted_traceback["history"]["preserved_v13_first_audit_failure"] = (
            copy.deepcopy(omitted_traceback["preserved_v13_failure"])
        )
        rejected("reject-discarded-genuine-v13-combined-traceback",
                 lambda: _validate_preserved_v13_failure(omitted_traceback))
        omitted_v15_traceback = copy.deepcopy(historic_audits)
        for key in tuple(omitted_v15_traceback["preserved_v15_failure"]):
            if key.startswith("combined_traceback_"):
                omitted_v15_traceback["preserved_v15_failure"].pop(key)
        omitted_v15_traceback["history"][
            "preserved_v15_first_audit_failure"
        ] = copy.deepcopy(omitted_v15_traceback["preserved_v15_failure"])
        rejected("reject-discarded-genuine-v15-combined-traceback",
                 lambda: _validate_preserved_v15_failure(
                     omitted_v15_traceback,
                 ))
        omitted_v24_incident = {
            "preserved_incidents": {},
        }
        rejected("reject-v24-proof-that-conceals-genuine-v13-failure",
                 lambda: _validate_preserved_v13_failure(
                     historic_audits, omitted_v24_incident,
                 ))
        rejected("reject-v24-proof-that-conceals-genuine-v15-failure",
                 lambda: _validate_preserved_v15_failure(
                     historic_audits, omitted_v24_incident,
                 ))
        rejected("reject-v24-proof-that-conceals-genuine-v17-failure",
                 lambda: _validate_preserved_v17_failure(
                     historic_audits, omitted_v24_incident,
                 ))
        rejected("reject-v24-proof-that-conceals-genuine-v19-failure",
                 lambda: _validate_preserved_v19_failure(
                     historic_audits, omitted_v24_incident,
                 ))
        boolean_v13_count = copy.deepcopy(historic_audits)
        boolean_v13_count["preserved_v13_failure"][
            "native_owner_workers_started"
        ] = False
        boolean_v13_count["history"]["preserved_v13_first_audit_failure"] = (
            copy.deepcopy(boolean_v13_count["preserved_v13_failure"])
        )
        rejected("reject-boolean-real-v13-native-owner-worker-count",
                 lambda: _validate_preserved_v13_failure(boolean_v13_count))
        boolean_v15_count = copy.deepcopy(historic_audits)
        boolean_v15_count["preserved_v15_failure"][
            "native_owner_workers_started"
        ] = False
        boolean_v15_count["history"]["preserved_v15_first_audit_failure"] = (
            copy.deepcopy(boolean_v15_count["preserved_v15_failure"])
        )
        rejected("reject-boolean-real-v15-native-owner-worker-count",
                 lambda: _validate_preserved_v15_failure(boolean_v15_count))
        boolean_v17_count = copy.deepcopy(historic_audits)
        boolean_v17_count["preserved_v17_failure"][
            "actual_native_owner_workers_completed"
        ] = True
        boolean_v17_count["history"]["preserved_v17_first_audit_failure"] = (
            copy.deepcopy(boolean_v17_count["preserved_v17_failure"])
        )
        rejected("reject-boolean-real-v17-native-owner-worker-count",
                 lambda: _validate_preserved_v17_failure(boolean_v17_count))
        boolean_v19_count = copy.deepcopy(historic_audits)
        boolean_v19_count["preserved_v19_failure"][
            "completed_native_owner_worker_count"
        ] = True
        boolean_v19_count["history"]["preserved_v19_first_audit_failure"] = (
            copy.deepcopy(boolean_v19_count["preserved_v19_failure"])
        )
        rejected("reject-boolean-real-v19-native-owner-worker-count",
                 lambda: _validate_preserved_v19_failure(boolean_v19_count))
        accept("preserve-exactly-152-original-public-method-obligations",
               len(matrix) == PUBLIC_METHODS)
        accept("preserve-all-13-original-private-method-obligations",
               PRIVATE_METHODS == 13)
        accept("preserve-all-26-original-upstream-support-files",
               SUPPORT_MODULES == 26)
        accept("preserve-all-403-original-upstream-corpus-observations",
               CORPUS_CASES == 403)
        accept("preserve-all-11-original-external-fixture-assertions",
               EXTERNAL_FIXTURE_ASSERTIONS == 11)
        accept("preserve-genuine-original-40-gibibyte-resource-limit",
               CONFIGURED_MEMORY_BYTES == 40 * 1024**3)
        accept("preserve-genuine-original-large-subn-resource-requirement",
               REQUIRED_SUBN_MEMORY_BYTES == 18 * 2**31)
        accept("preserve-both-real-at-least-two-gibibyte-method-identities",
               {matrix[0]["test"], matrix[1]["test"]}
               == {"ReTests.test_large_search", "ReTests.test_large_subn"})
        accept("accept-genuine-platform-specific-pathlib-source-paths",
               isinstance(ROOT / SOURCE_RELATIVE, Path))
        accept("preserve-exact-candidate-free-v21-owner-parent-environment",
               _isolated_owner_environment() == {
                   "PYTHONDONTWRITEBYTECODE": "1",
                   "PYTHONHASHSEED": "0",
                   "PYTHONPATH": str(ROOT),
                   "PATH": "/usr/bin:/bin",
               })
        accept("freeze-root-authorized-final-reviewed-v21-owner-source-only",
               V21_SOURCE_SHA256
               == "ded077962416ada3bddd825d77b2e6785fe3b01184fe5d9058ec17a57b08ea4d")
        accept("freeze-root-authorized-final-reviewed-v21-owner-protocol-only",
               V21_PROTOCOL_SHA256
               == "5a78673c6b23e4781070cf5a2290d5f6cecd402fff77ff388d8795370de93a1f")
        accept("freeze-root-authorized-reviewed-integrated-v24-proof-source",
               V24_SOURCE_SHA256
               == "92b1f082196592e578a5fa6e09b63637c6a1304c04875e5816938ed4fc28eb52")
        accept("freeze-root-authorized-reviewed-integrated-v24-proof-protocol",
               V24_PROTOCOL_SHA256
               == "f3ab4f5c3c697a6d39c109b743d949b980bfe0d79aeb6b58a0bc392a3f81e534")
        accept("launch-every-method-owner-in-an-isolated-source-bound-helper",
               "native_owner_entry" in OWNER_BOOTSTRAP
               and "postfinal_cpython_locale_oracle_v15" in OWNER_BOOTSTRAP)
        accept("freeze-parent-supplied-authentic-double-v6-reference-only",
               V6_REFERENCE_SHA256
               == "1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf")
        accept("freeze-actual-immutable-complete-v6-controller-source",
               V6_SOURCE_SHA256
               == "b1522b55b37de2e004b029c128e2e75c3020cda34165bcf0de07cb5ebb3136cb")
        accept("freeze-actual-immutable-complete-v6-upstream-protocol",
               V6_PROTOCOL_SHA256
               == "8e43ceaa61f6e70e2e1193de71bde8583c101cdbe40bc78d862ae789531aff57")
        accept("validate-the-complete-double-v6-reference-shape-in-memory",
               _validate_synthetic_reference(reference, matrix) == reference)
        accept("preserve-exactly-one-original-private-debug-only-skip",
               all(role["applicable"] == 151 and role["passed"] == 151
                   and role["named_private_debug_skips"] == 1
                   for role in reference["roles"].values()))
        for index, requirement in enumerate(matrix):
            accept("retain-original-source-order-public-method:" + str(index),
                   reference["roles"]["reference_a"]["records"][index]["test"]
                   == requirement["test"]
                   and valid_sha256(requirement["source_ast_sha256"]))

        for key, wrong in (
            ("schema", SCHEMA + "-forged"), ("status", "FAIL"),
            ("synthetic", True), ("python", "3.14.5"),
            ("source_path", SOURCE_RELATIVE),
            ("source_sha256", "0" * 64),
            ("protocol_path", PROTOCOL_RELATIVE),
            ("protocol_sha256", "0" * 64),
            ("public_method_matrix_sha256", "0" * 64),
            ("actual_independent_reference_count", 1),
            ("reference_candidate_imports", 1),
            ("reference_candidate_audits_read", 1),
            ("reference_candidate_proofs_read", 1),
            ("reference_holdout_cases_read", 1),
            ("reference_status_vector_sha256", "0" * 64),
            ("performance", "MEASURED"), ("holdout", "ACCESSED"),
        ):
            changed = copy.deepcopy(reference)
            changed[key] = wrong
            rejected("reject-forged-frozen-real-double-reference:" + key,
                     lambda changed=changed:
                     _validate_synthetic_reference(changed, matrix))
        for label in REFERENCE_LABELS:
            missing = copy.deepcopy(reference)
            missing["roles"].pop(label)
            rejected("reject-omitted-real-independent-reference:" + label,
                     lambda missing=missing:
                     _validate_synthetic_reference(missing, matrix))
            omitted = copy.deepcopy(reference)
            omitted["roles"][label]["records"].pop()
            rejected("reject-dropped-genuine-public-upstream-method:" + label,
                     lambda omitted=omitted:
                     _validate_synthetic_reference(omitted, matrix))
            reordered = copy.deepcopy(reference)
            reordered["roles"][label]["records"].reverse()
            rejected("reject-reordered-original-upstream-method:" + label,
                     lambda reordered=reordered:
                     _validate_synthetic_reference(reordered, matrix))
            for status in ("FAIL", "ERROR", "TIMEOUT", "CRASH", "SKIP"):
                changed = copy.deepcopy(reference)
                changed["roles"][label]["records"][0]["status"] = status
                rejected("reject-original-reference-method-" + status.lower()
                         + ":" + label,
                         lambda changed=changed:
                         _validate_synthetic_reference(changed, matrix))
            for field in ("reason", "classification"):
                changed = copy.deepcopy(reference)
                changed["roles"][label]["records"][-1][field] = "forged"
                rejected("reject-fabricated-private-debug-skip:"
                         + label + ":" + field,
                         lambda changed=changed:
                         _validate_synthetic_reference(changed, matrix))

        expected_controllers = _synthetic_controllers()
        for selected in (*FAMILIES, "all"):
            pins = _synthetic_pins(selected)
            approved = _candidate_pin_values(
                selected, pins, expected_controllers=expected_controllers,
            )
            accept("require-complete-v21-v24-and-four-proof-pins:" + selected,
                   len(approved) == 6 + 4 * len(_chosen(selected)))
            for key in tuple(pins):
                changed = dict(pins)
                changed.pop(key)
                rejected("reject-each-missing-current-graph-proof-pin:"
                         + selected + ":" + key,
                         lambda changed=changed, selected=selected:
                         _candidate_pin_values(
                             selected, changed,
                             expected_controllers=expected_controllers,
                         ))
                forged = dict(pins)
                forged[key] = "0" * 64
                rejected("reject-each-forged-current-graph-proof-pin:"
                         + selected + ":" + key,
                         lambda forged=forged, selected=selected:
                         _candidate_pin_values(
                             selected, forged,
                             expected_controllers=expected_controllers,
                         ))
            duplicate = dict(pins)
            duplicate["base_report"] = pins["strict_report"]
            rejected("reject-reused-independent-all-family-report:" + selected,
                     lambda duplicate=duplicate, selected=selected:
                     _candidate_pin_values(
                         selected, duplicate,
                         expected_controllers=expected_controllers,
                     ))
            undeclared = dict(pins)
            undeclared["undeclared_evidence"] = _synthetic_digest(
                "secret-undeclared-evidence:" + selected,
            )
            rejected("reject-undeclared-current-evidence-pin:" + selected,
                     lambda undeclared=undeclared, selected=selected:
                     _candidate_pin_values(
                         selected, undeclared,
                         expected_controllers=expected_controllers,
                     ))
            historical = dict(pins)
            historical["base_report"] = V6_REFERENCE_SHA256
            rejected("reject-frozen-reference-as-current-owner:" + selected,
                     lambda historical=historical, selected=selected:
                     _candidate_pin_values(
                         selected, historical,
                         expected_controllers=expected_controllers,
                     ))
            for key, historical_sha256 in (
                ("proof_source", V22_FAILURE_SOURCE_SHA256),
                ("proof_protocol", V22_FAILURE_PROTOCOL_SHA256),
            ):
                failed_v22 = dict(pins)
                failed_v22[key] = historical_sha256
                rejected("reject-failed-v22-as-qualifying-v24-proof-pin:"
                         + selected + ":" + key,
                         lambda failed_v22=failed_v22, selected=selected:
                         _candidate_pin_values(
                             selected, failed_v22,
                             expected_controllers=expected_controllers,
                         ))
            for family in FAMILIES:
                if family not in _chosen(selected):
                    changed = dict(pins)
                    changed[family + "_edge_archive"] = _synthetic_digest(
                        "secret-unselected-family:" + family,
                    )
                    rejected("reject-secret-unselected-family-proof:"
                             + selected + ":" + family,
                             lambda changed=changed, selected=selected:
                             _candidate_pin_values(
                                 selected, changed,
                                 expected_controllers=expected_controllers,
                             ))

        graph, source_paths, native_paths = _synthetic_graph()
        accept("validate-all-12-owned-source-and-five-native-binary-shapes",
               _validate_current_graph(graph, source_paths, native_paths) == graph)
        candidate_safe_graph = copy.deepcopy(graph)
        candidate_safe_payloads: dict[str, bytes] = {}
        for owned_family in FAMILIES:
            for group in ("source_sha256_by_family", "native_sha256_by_family"):
                for relative in candidate_safe_graph[group][owned_family]:
                    payload = (
                        (b"\x7fELF" if group == "native_sha256_by_family"
                         else b"# genuine synthetic source\n")
                        + ("candidate-safe:" + relative).encode("ascii")
                    )
                    candidate_safe_payloads[relative] = payload
                    candidate_safe_graph[group][owned_family][relative] = (
                        hashlib.sha256(payload).hexdigest()
                    )
        candidate_safe_reads: list[str] = []

        def read_candidate_safe_synthetic(
            path: Path, bound: int, label: str,
        ) -> bytes:
            require(isinstance(path, Path)
                    and type(bound) is int and bound == MAX_EVIDENCE_BYTES
                    and type(label) is str
                    and label.startswith("candidate-safe authenticated owned graph: "),
                    "a synthetic-only descriptor verifier was substituted")
            relative = path.relative_to(ROOT).as_posix()
            require(_safe_graph_path(relative)
                    and relative in candidate_safe_payloads,
                    "a synthetic-only owned graph escaped its allowed paths")
            candidate_safe_reads.append(relative)
            return candidate_safe_payloads[relative]

        verified_live_graph = _verify_candidate_context_current_graph(
            candidate_safe_graph, source_paths, native_paths,
            read_regular=read_candidate_safe_synthetic,
        )
        accept("verify-full-candidate-context-12-source-five-elf-graph",
               verified_live_graph is candidate_safe_graph
               and len(candidate_safe_reads) == 17
               and len(set(candidate_safe_reads)) == 17)
        accept("verify-candidate-context-with-zero-v11-v21-snapshot-calls",
               inventory is None and original is None and durable is None)
        for owned_family in FAMILIES:
            accept("verify-candidate-context-same-family-native-loader:"
                   + owned_family,
                   _verify_family_native_mappings(
                       owned_family, candidate_safe_graph, native_paths,
                   ) == candidate_safe_graph[
                       "native_sha256_by_family"
                   ][owned_family])
            for group in ("source_sha256_by_family",
                          "native_sha256_by_family"):
                for relative in candidate_safe_graph[group][owned_family]:
                    tampered = copy.deepcopy(candidate_safe_graph)
                    tampered[group][owned_family][relative] = (
                        _synthetic_digest("forged-live-owned-path:" + relative)
                    )
                    rejected("reject-tampered-candidate-context-owned-file:"
                             + owned_family + ":" + relative,
                             lambda tampered=tampered:
                             _verify_candidate_context_current_graph(
                                 tampered, source_paths, native_paths,
                                 read_regular=read_candidate_safe_synthetic,
                             ))
            replaced_native = copy.deepcopy(candidate_safe_graph)
            native_relative = next(iter(
                replaced_native["native_sha256_by_family"][owned_family]
            ))
            forged_elf = b"not-an-ELF-native: " + native_relative.encode("ascii")

            def read_forged_native(
                path: Path, bound: int, label: str,
                *, native_relative: str = native_relative,
                forged_elf: bytes = forged_elf,
            ) -> bytes:
                relative = path.relative_to(ROOT).as_posix()
                return (forged_elf if relative == native_relative
                        else candidate_safe_payloads[relative])

            replaced_native["native_sha256_by_family"][owned_family][
                native_relative
            ] = hashlib.sha256(forged_elf).hexdigest()
            rejected("reject-hash-valid-but-non-elf-owned-native:"
                     + owned_family,
                     lambda replaced_native=replaced_native,
                     read_forged_native=read_forged_native:
                     _verify_candidate_context_current_graph(
                         replaced_native, source_paths, native_paths,
                         read_regular=read_forged_native,
                     ))
        authenticated_bridge = _validate_authenticated_native_bridge(
            copy.deepcopy(graph["native_sha256_by_family"]),
            graph,
            native_paths,
        )
        synthetic_owned_re = types.ModuleType("synthetic_owned_candidate_re")
        synthetic_owned_constants = types.ModuleType("re._constants")
        synthetic_owned_constants.__package__ = "re"
        synthetic_owned_constants.__spec__ = importlib.machinery.ModuleSpec(
            "re._constants", loader=None,
        )
        synthetic_owned_constants.MAXGROUPS = 65_535
        synthetic_owned_modules = {
            "re": synthetic_owned_re,
            "re._constants": synthetic_owned_constants,
        }
        for owned_family in FAMILIES:
            accept("allow-only-authenticated-absolute-owned-root-re-import:"
                   + owned_family,
                   _validate_owned_original_re_import(
                       "re", 0, owned_family, synthetic_owned_re,
                       synthetic_owned_modules, graph, native_paths,
                       owned_family=owned_family,
                   ) is synthetic_owned_re)
            accept("allow-only-exact-owned-v4-maxgroups-constant-shim:"
                   + owned_family,
                   _validate_owned_original_constants_import(
                       "re._constants", ("MAXGROUPS",), 0,
                       owned_family, synthetic_owned_re,
                       synthetic_owned_constants, 65_535,
                       synthetic_owned_modules, graph, native_paths,
                       owned_family=owned_family,
                   ) is synthetic_owned_constants)
            for label, name, fromlist, level in (
                ("relative-constants", "re._constants", ("MAXGROUPS",), 1),
                ("root-module-as-constants", "re", ("MAXGROUPS",), 0),
                ("empty-fromlist", "re._constants", (), 0),
                ("additional-fromlist", "re._constants",
                 ("MAXGROUPS", "compile"), 0),
                ("foreign-fromlist", "re._constants", ("compile",), 0),
                ("compiler-descendant", "re._compiler", ("MAXGROUPS",), 0),
                ("parser-descendant", "re._parser", ("MAXGROUPS",), 0),
                ("casefix-descendant", "re._casefix", ("MAXGROUPS",), 0),
                ("sre-native-matcher", "_sre", ("MAXGROUPS",), 0),
            ):
                rejected("reject-unowned-v4-constant-shim-import:"
                         + owned_family + ":" + label,
                         lambda owned_family=owned_family,
                         name=name, fromlist=fromlist, level=level:
                         _validate_owned_original_constants_import(
                             name, fromlist, level,
                             owned_family, synthetic_owned_re,
                             synthetic_owned_constants, 65_535,
                             synthetic_owned_modules, graph, native_paths,
                             owned_family=owned_family,
                         ))
            for label in (
                "swap-constants-identity",
                "foreign-maxgroups",
                "boolean-maxgroups",
                "injected-matcher-export",
                "forged-spec-name",
                "forged-package",
                "forged-loader",
            ):
                forged = types.ModuleType("re._constants")
                forged.__package__ = "re"
                forged.__spec__ = importlib.machinery.ModuleSpec(
                    "re._constants", loader=None,
                )
                forged.MAXGROUPS = 65_535
                module_cache = {
                    "re": synthetic_owned_re,
                    "re._constants": forged,
                }
                if label == "swap-constants-identity":
                    module_cache["re._constants"] = synthetic_owned_constants
                elif label == "foreign-maxgroups":
                    forged.MAXGROUPS = 65_536
                elif label == "boolean-maxgroups":
                    forged.MAXGROUPS = True
                elif label == "injected-matcher-export":
                    forged.compile = object()
                elif label == "forged-spec-name":
                    forged.__spec__ = importlib.machinery.ModuleSpec(
                        "re._compiler", loader=None,
                    )
                elif label == "forged-package":
                    forged.__package__ = "forged"
                elif label == "forged-loader":
                    forged.__loader__ = object()
                rejected("reject-forged-owned-v4-maxgroups-shim:"
                         + owned_family + ":" + label,
                         lambda owned_family=owned_family,
                         forged=forged, module_cache=module_cache:
                         _validate_owned_original_constants_import(
                             "re._constants", ("MAXGROUPS",), 0,
                             owned_family, synthetic_owned_re,
                             forged, 65_535, module_cache,
                             graph, native_paths, owned_family=owned_family,
                         ))
            for name, level in (
                ("re", 1),
                ("re._constants", 0),
                ("re._compiler", 0),
                ("re._parser", 0),
                ("re._casefix", 0),
                ("_sre", 0),
                ("regex", 0),
                ("candidates.forged_candidate", 0),
            ):
                rejected("reject-unowned-standard-matcher-import:"
                         + owned_family + ":" + name + ":" + str(level),
                         lambda name=name, level=level,
                         owned_family=owned_family:
                         _validate_owned_original_re_import(
                             name, level, owned_family, synthetic_owned_re,
                             synthetic_owned_modules, graph, native_paths,
                             owned_family=owned_family,
                         ))
            other_family = next(item for item in FAMILIES
                                if item != owned_family)
            rejected("reject-cross-family-original-root-re-import:"
                     + owned_family,
                     lambda owned_family=owned_family,
                     other_family=other_family:
                     _validate_owned_original_re_import(
                         "re", 0, other_family, synthetic_owned_re,
                         synthetic_owned_modules, graph, native_paths,
                         owned_family=owned_family,
                     ))
            swapped = types.ModuleType("synthetic_forged_standard_re")
            rejected("reject-swapped-sys-modules-original-root-re-import:"
                     + owned_family,
                     lambda owned_family=owned_family, swapped=swapped:
                     _validate_owned_original_re_import(
                         "re", 0, owned_family, synthetic_owned_re,
                         {"re": swapped}, graph, native_paths,
                         owned_family=owned_family,
                     ))
        accept("expose-exact-deep-copied-all-three-family-owned-native-bridge",
               set(authenticated_bridge) == set(FAMILIES)
               and authenticated_bridge == graph["native_sha256_by_family"]
               and authenticated_bridge is not graph["native_sha256_by_family"]
               and all(authenticated_bridge[family]
                       is not graph["native_sha256_by_family"][family]
                       for family in FAMILIES)
               and sum(map(len, authenticated_bridge.values())) == 5)
        for label, invalid in (
            ("empty-v5-native-map", {}),
            ("missing-native-map", None),
            ("graph-top-level-alias", graph["native_sha256_by_family"]),
        ):
            rejected("reject-unauthenticated-original-native-bridge:" + label,
                     lambda invalid=invalid:
                     _validate_authenticated_native_bridge(
                         invalid, graph, native_paths,
                     ))
        for family in FAMILIES:
            missing = copy.deepcopy(graph["native_sha256_by_family"])
            missing.pop(family)
            rejected("reject-missing-owned-family-native-bridge:" + family,
                     lambda missing=missing:
                     _validate_authenticated_native_bridge(
                         missing, graph, native_paths,
                     ))
            for path in graph["native_sha256_by_family"][family]:
                changed = copy.deepcopy(graph["native_sha256_by_family"])
                changed[family][path] = _synthetic_digest(
                    "forged-native-bridge:" + family + ":" + path,
                )
                rejected("reject-substituted-owned-native-bridge-hash:"
                         + family + ":" + path,
                         lambda changed=changed:
                         _validate_authenticated_native_bridge(
                             changed, graph, native_paths,
                         ))
            swapped = copy.deepcopy(graph["native_sha256_by_family"])
            other = next(item for item in FAMILIES if item != family)
            swapped[family] = copy.deepcopy(swapped[other])
            rejected("reject-cross-family-owned-native-bridge:" + family,
                     lambda swapped=swapped:
                     _validate_authenticated_native_bridge(
                         swapped, graph, native_paths,
                     ))
            nested_alias = copy.deepcopy(graph["native_sha256_by_family"])
            nested_alias[family] = graph["native_sha256_by_family"][family]
            rejected("reject-aliased-owned-family-native-bridge:" + family,
                     lambda nested_alias=nested_alias:
                     _validate_authenticated_native_bridge(
                         nested_alias, graph, native_paths,
                     ))
        synthetic_provenance = {
            "native_sha256_by_family": {},
            "synthetic_reference_marker": True,
        }
        synthetic_qualification = {
            "native_sha256_by_family": authenticated_bridge,
            "synthetic_qualification_marker": True,
        }
        installed_bridge = _install_authenticated_native_bridge(
            synthetic_provenance, synthetic_qualification, graph, native_paths,
        )
        accept("install-independent-full-native-bridge-into-v5-provenance",
               installed_bridge is synthetic_provenance
               and installed_bridge["native_sha256_by_family"]
               == graph["native_sha256_by_family"]
               and installed_bridge["native_sha256_by_family"]
               is not synthetic_qualification["native_sha256_by_family"]
               and installed_bridge["native_sha256_by_family"]
               is not graph["native_sha256_by_family"])
        for label, prior in (
            ("missing-v5-native-map", {}),
            ("forged-nonempty-v5-native-map", {
                "native_sha256_by_family": {"rust": {}},
            }),
        ):
            rejected("reject-untrusted-original-v5-native-provenance:" + label,
                     lambda prior=prior:
                     _install_authenticated_native_bridge(
                         prior, synthetic_qualification, graph, native_paths,
                     ))
        for field, wrong in (("source_count", 11), ("native_binary_count", 4)):
            changed = copy.deepcopy(graph)
            changed[field] = wrong
            rejected("reject-omitted-complete-owned-graph-denominator:" + field,
                     lambda changed=changed:
                     _validate_current_graph(changed, source_paths, native_paths))
        omitted_paths = copy.deepcopy(graph)
        omitted_paths["source_paths"].pop()
        rejected("reject-missing-actual-all-family-owned-source-path",
                 lambda: _validate_current_graph(
                     omitted_paths, source_paths, native_paths,
                 ))
        for family in FAMILIES:
            snapshot = {
                "family": family,
                "module": FAMILY_MODULES[family],
                "source_sha256_by_path": copy.deepcopy(
                    graph["source_sha256_by_family"][family],
                ),
                "native_sha256_by_path": copy.deepcopy(
                    graph["native_sha256_by_family"][family],
                ),
            }
            accept("accept-only-the-exact-current-native-family:" + family,
                   _validate_snapshot(family, snapshot, graph) == snapshot)
            for key, wrong in (
                ("family", "forged"),
                ("module", "candidates.forged_candidate"),
            ):
                changed = copy.deepcopy(snapshot)
                changed[key] = wrong
                rejected("reject-substituted-current-family:"
                         + family + ":" + key,
                         lambda changed=changed, family=family:
                         _validate_snapshot(family, changed, graph))
            for group in ("source_sha256_by_path", "native_sha256_by_path"):
                for path in snapshot[group]:
                    changed = copy.deepcopy(snapshot)
                    changed[group][path] = "0" * 64
                    rejected("reject-changed-current-owned-identity:"
                             + family + ":" + group + ":" + path,
                             lambda changed=changed, family=family:
                             _validate_snapshot(family, changed, graph))
            trace = _synthetic_native_trace(
                family, matrix, graph["native_sha256_by_family"][family],
            )
            accept("require-304-fresh-method-adjacent-native-owners:" + family,
                   _validate_native_method_trace(
                       family, matrix, trace,
                       graph["native_sha256_by_family"][family],
                       _synthetic_owner_validator,
                   ) == trace)
            capture_source = _synthetic_digest(
                "actual-captured-original-worker-source:" + family,
            )
            capture_pins = _synthetic_pins(family)
            capture_proof = {
                "family": family,
                "status": "PASS",
                "campaign_qualified": True,
            }
            capture_role = {
                "records": copy.deepcopy(
                    reference["roles"]["reference_a"]["records"],
                ),
                "actual_cached_matcher_method_guard_checks": 2 * PUBLIC_METHODS,
                "actual_native_owner_method_guard_checks": 2 * PUBLIC_METHODS,
            }
            capture_inline = {"synthetic_sentinel_guarded": True}
            captured_progress = _capture_completed_original_progress(
                family, capture_role, capture_inline, trace,
                "complete-original-role-captured-before-any-postflight",
            )
            accept("capture-all-152-real-methods-before-any-postflight:" + family,
                   captured_progress[
                       "actual_completed_original_method_records"
                   ] == capture_role["records"]
                   and captured_progress[
                       "actual_completed_original_method_count"
                   ] == PUBLIC_METHODS)
            accept("capture-all-304-real-native-owners-before-postflight:"
                   + family,
                   captured_progress[
                       "actual_completed_native_method_owners"
                   ] == trace
                   and captured_progress[
                       "actual_native_owner_method_guard_checks"
                   ] == 2 * PUBLIC_METHODS
                   and captured_progress[
                       "production_observations_invented"
                   ] is False)
            detached_role = copy.deepcopy(capture_role)
            detached_trace = copy.deepcopy(trace)
            detached_progress = _capture_completed_original_progress(
                family, detached_role, capture_inline, detached_trace,
                "complete-original-role-captured-before-any-postflight",
            )
            detached_role["records"].pop()
            detached_trace.pop()
            accept("detach-real-152-method-and-304-owner-progress-before-failure:"
                   + family,
                   len(detached_progress[
                       "actual_completed_original_method_records"
                   ]) == PUBLIC_METHODS
                   and len(detached_progress[
                       "actual_completed_native_method_owners"
                   ]) == 2 * PUBLIC_METHODS)
            incomplete_capture_role = copy.deepcopy(capture_role)
            incomplete_capture_role["records"].pop()
            rejected("reject-incomplete-151-method-pre-postflight-capture:"
                     + family,
                     lambda family=family,
                     incomplete_capture_role=incomplete_capture_role,
                     capture_inline=capture_inline, trace=trace:
                     _capture_completed_original_progress(
                         family, incomplete_capture_role, capture_inline, trace,
                         "complete-original-role-captured-before-any-postflight",
                     ))
            rejected("reject-incomplete-303-owner-pre-postflight-capture:"
                     + family,
                     lambda family=family, capture_role=capture_role,
                     capture_inline=capture_inline, trace=trace:
                     _capture_completed_original_progress(
                         family, capture_role, capture_inline, trace[:-1],
                         "complete-original-role-captured-before-any-postflight",
                     ))
            captured_document = {
                "schema": SCHEMA + "-actual-worker",
                "status": "PASS",
                "role": family,
                "source_sha256": capture_source,
                "protocol_sha256": PROTOCOL_SHA256,
                "reference_sha256": V6_REFERENCE_SHA256,
                "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
                "candidate_prerequisite_sha256": capture_pins,
                "qualified_family_proof": capture_proof,
                "role_report": capture_role,
                "actual_inline_cached_matcher_guards": copy.deepcopy(
                    capture_inline,
                ),
                "actual_inline_cached_matcher_method_guard_checks": (
                    2 * PUBLIC_METHODS
                ),
                "actual_native_method_owners": copy.deepcopy(trace),
                "actual_native_owner_method_guard_checks": 2 * PUBLIC_METHODS,
                "performance": "NOT MEASURED",
                "holdout": "NOT ACCESSED",
            }
            capture_command = [
                "genuine-source-only-injected-captured-worker", family,
            ]

            def validate_synthetic_captured_role(
                document: dict[str, Any],
                *,
                family: str = family,
                proof: Mapping[str, Any] = capture_proof,
            ) -> None:
                require(document.get("qualified_family_proof") == dict(proof),
                        "an in-memory original worker substituted its V24 proofs")
                role = document.get("role_report")
                require(isinstance(role, dict)
                        and role.get("records")
                        == reference["roles"]["reference_a"]["records"]
                        and role.get("actual_cached_matcher_method_guard_checks")
                        == 2 * PUBLIC_METHODS
                        and role.get("actual_native_owner_method_guard_checks")
                        == 2 * PUBLIC_METHODS
                        and document.get("actual_inline_cached_matcher_guards")
                        == {"synthetic_sentinel_guarded": True},
                        "a zero-exit original worker concealed its actual "
                        "full method records or matcher guards")
                _validate_native_method_trace(
                    family, matrix, document.get("actual_native_method_owners"),
                    graph["native_sha256_by_family"][family],
                    _synthetic_owner_validator,
                )

            genuine_completed = subprocess.CompletedProcess(
                capture_command,
                0,
                stdout=canonical(captured_document) + b"\n",
                stderr=b"",
            )
            accept("validate-full-zero-exit-original-worker-inside-capture:"
                   + family,
                   _validate_captured_worker(
                       genuine_completed,
                       family=family,
                       source_sha256=capture_source,
                       pins=capture_pins,
                       expected_command=capture_command,
                       validate_document=validate_synthetic_captured_role,
                   ) == captured_document)

            def capture_rejected(
                label: str,
                completed: subprocess.CompletedProcess[bytes],
                *,
                decoded: Mapping[str, Any] | None,
                family: str = family,
            ) -> None:
                try:
                    _validate_captured_worker(
                        completed,
                        family=family,
                        source_sha256=capture_source,
                        pins=capture_pins,
                        expected_command=capture_command,
                        validate_document=validate_synthetic_captured_role,
                    )
                except OfficialV15WorkerFailure as error:
                    actual = error.details
                    expected_stdout = _complete_captured_stream(
                        completed.stdout,
                        "candidate-free injected actual worker stdout",
                    )
                    expected_stderr = _complete_captured_stream(
                        completed.stderr,
                        "candidate-free injected actual worker stderr",
                    )
                    truthful = (
                        error.role == family
                        and actual.get("returncode") == completed.returncode
                        and actual.get("signal")
                        == (-completed.returncode
                            if completed.returncode < 0 else None)
                        and actual.get("stdout") == expected_stdout
                        and actual.get("stderr") == expected_stderr
                        and actual.get("complete_streams_available") is True
                        and actual.get("production_observations_invented")
                        is False
                    )
                    if decoded is None:
                        truthful = (
                            truthful
                            and "actual_worker_document" not in actual
                            and "actual_completed_original_method_records"
                            not in actual
                        )
                    else:
                        truthful = (
                            truthful
                            and actual.get("actual_worker_document")
                            == dict(decoded)
                        )
                        observed_role = decoded.get("role_report")
                        if (isinstance(observed_role, Mapping)
                                and isinstance(
                                    observed_role.get("records"), list,
                                )):
                            truthful = (
                                truthful
                                and actual.get(
                                    "actual_completed_original_method_records",
                                ) == observed_role["records"]
                                and actual.get(
                                    "actual_completed_original_method_count",
                                ) == len(observed_role["records"])
                            )
                        observed_failure = decoded.get("details")
                        if isinstance(observed_failure, Mapping):
                            truthful = (
                                truthful
                                and actual.get("actual_worker_failure_details")
                                == dict(observed_failure)
                                and actual.get(
                                    "actual_completed_original_method_records",
                                ) == observed_failure.get(
                                    "actual_completed_original_method_records",
                                )
                                and actual.get(
                                    "actual_completed_original_method_count",
                                ) == observed_failure.get(
                                    "actual_completed_original_method_count",
                                )
                                and actual.get(
                                    "actual_completed_native_method_owners",
                                ) == observed_failure.get(
                                    "actual_completed_native_method_owners",
                                )
                                and actual.get(
                                    "actual_native_owner_method_guard_checks",
                                ) == observed_failure.get(
                                    "actual_native_owner_method_guard_checks",
                                )
                                and actual.get("active_postflight_stage")
                                == observed_failure.get(
                                    "active_postflight_stage",
                                )
                            )
                    accept("preserve-complete-zero-exit-worker-failure:"
                           + family + ":" + label, truthful)
                else:
                    accept("preserve-complete-zero-exit-worker-failure:"
                           + family + ":" + label, False)

            malformed = subprocess.CompletedProcess(
                capture_command, 0, stdout=b"{not genuine JSON", stderr=b"",
            )
            capture_rejected("malformed-json-no-invented-document",
                             malformed, decoded=None)
            invalid_utf8 = subprocess.CompletedProcess(
                capture_command, 0, stdout=b"\xff\xfe", stderr=b"",
            )
            capture_rejected("invalid-utf8-no-invented-document",
                             invalid_utf8, decoded=None)
            for label, timeout_stdout, timeout_stderr in (
                ("both-streams", b"genuine synthetic stdout\n",
                 b"genuine synthetic stderr\n"),
                ("stdout-not-captured", None,
                 b"genuine synthetic stderr\n"),
                ("stderr-not-captured", b"genuine synthetic stdout\n", None),
                ("neither-captured", None, None),
            ):
                timeout_error = subprocess.TimeoutExpired(
                    capture_command,
                    17,
                    output=timeout_stdout,
                    stderr=timeout_stderr,
                )
                timeout_failure = _timeout_worker_failure(
                    family,
                    timeout_error,
                    message="actual synthetic-only injected timeout",
                    details={"active_original_method": matrix[0]["test"]},
                )
                expected_stdout = (
                    {"capture": "NOT CAPTURED"}
                    if timeout_stdout is None else _complete_captured_stream(
                        timeout_stdout, "source-only genuine timeout stdout",
                    )
                )
                expected_stderr = (
                    {"capture": "NOT CAPTURED"}
                    if timeout_stderr is None else _complete_captured_stream(
                        timeout_stderr, "source-only genuine timeout stderr",
                    )
                )
                accept("preserve-only-real-captured-timeout-streams:"
                       + family + ":" + label,
                       timeout_failure.role == family
                       and timeout_failure.details.get("status") == "TIMEOUT"
                       and timeout_failure.details.get("timeout_seconds") == 17
                       and timeout_failure.details.get("returncode") is None
                       and timeout_failure.details.get("signal") is None
                       and timeout_failure.details.get("stdout") == expected_stdout
                       and timeout_failure.details.get("stderr") == expected_stderr
                       and timeout_failure.details.get(
                           "production_observations_invented",
                       ) is False)
            for returncode in (1, -9):
                failed_process = subprocess.CompletedProcess(
                    capture_command,
                    returncode,
                    stdout=canonical(captured_document) + b"\n",
                    stderr=b"",
                )
                capture_rejected("actual-return-or-signal:" + str(returncode),
                                 failed_process, decoded=captured_document)
            stderr_failure = subprocess.CompletedProcess(
                capture_command,
                0,
                stdout=canonical(captured_document) + b"\n",
                stderr=b"actual synthetic-only original child stderr\n",
            )
            capture_rejected("retain-complete-real-child-stderr",
                             stderr_failure, decoded=captured_document)
            for stage in (
                "frozen-independent-double-reference-status-vector",
                "current-complete-source-and-native-graph-integrity",
                "complete-method-adjacent-native-owner-integrity",
            ):
                postflight_progress = copy.deepcopy(captured_progress)
                postflight_progress["active_postflight_stage"] = stage
                failed_postflight_document = {
                    "schema": SCHEMA + "-actual-worker-failure",
                    "status": "FAIL",
                    "role": family,
                    "actual_error_type": "OfficialV15Error",
                    "reason": "synthetic-only real postflight-shape failure",
                    "details": postflight_progress,
                    "production_observations_invented": False,
                    "performance": "NOT MEASURED",
                    "holdout": "NOT ACCESSED",
                }
                failed_postflight = subprocess.CompletedProcess(
                    capture_command,
                    2,
                    stdout=canonical(failed_postflight_document) + b"\n",
                    stderr=b"",
                )
                capture_rejected(
                    "postflight-keeps-152-original-methods-and-304-owners:"
                    + stage,
                    failed_postflight,
                    decoded=failed_postflight_document,
                )
            noncanonical = subprocess.CompletedProcess(
                capture_command,
                0,
                stdout=b" " + canonical(captured_document) + b"\n",
                stderr=b"",
            )
            capture_rejected("noncanonical-zero-exit-retains-real-document",
                             noncanonical, decoded=captured_document)
            for key, wrong in (
                ("schema", SCHEMA + "-forged-worker"),
                ("status", "FAIL"),
                ("role", "forged"),
                ("source_sha256", "0" * 64),
                ("protocol_sha256", "0" * 64),
                ("reference_sha256", "0" * 64),
                ("public_method_matrix_sha256", "0" * 64),
                ("candidate_prerequisite_sha256", {}),
                ("qualified_family_proof", {"status": "FAIL"}),
                ("actual_inline_cached_matcher_method_guard_checks", 303),
                ("actual_native_owner_method_guard_checks", 303),
                ("actual_inline_cached_matcher_guards", {}),
                ("performance", "MEASURED"),
                ("holdout", "ACCESSED"),
            ):
                changed = copy.deepcopy(captured_document)
                changed[key] = wrong
                completed = subprocess.CompletedProcess(
                    capture_command,
                    0,
                    stdout=canonical(changed) + b"\n",
                    stderr=b"",
                )
                capture_rejected("zero-exit-forged-document:" + key,
                                 completed, decoded=changed)
            for row_index in (0, len(capture_role["records"]) - 1):
                changed = copy.deepcopy(captured_document)
                changed["role_report"]["records"].pop(row_index)
                completed = subprocess.CompletedProcess(
                    capture_command,
                    0,
                    stdout=canonical(changed) + b"\n",
                    stderr=b"",
                )
                capture_rejected("zero-exit-preserves-real-partial-method:"
                                 + str(row_index),
                                 completed, decoded=changed)
            for row_index in (0, len(trace) - 1):
                changed = copy.deepcopy(captured_document)
                changed["actual_native_method_owners"].pop(row_index)
                completed = subprocess.CompletedProcess(
                    capture_command,
                    0,
                    stdout=canonical(changed) + b"\n",
                    stderr=b"",
                )
                capture_rejected("zero-exit-preserves-real-partial-owner:"
                                 + str(row_index),
                                 completed, decoded=changed)
            for index in (0, 1, len(trace) - 2, len(trace) - 1):
                omitted = copy.deepcopy(trace)
                omitted.pop(index)
                rejected("reject-missing-exact-adjacent-native-owner:"
                         + family + ":" + str(index),
                         lambda omitted=omitted, family=family:
                         _validate_native_method_trace(
                             family, matrix, omitted,
                             graph["native_sha256_by_family"][family],
                             _synthetic_owner_validator,
                         ))
                changed = copy.deepcopy(trace)
                changed[index]["native_owner"]["genuine"] = False
                rejected("reject-forged-exact-adjacent-native-owner:"
                         + family + ":" + str(index),
                         lambda changed=changed, family=family:
                         _validate_native_method_trace(
                             family, matrix, changed,
                             graph["native_sha256_by_family"][family],
                             _synthetic_owner_validator,
                         ))
            for phase in ("before", "after", None, True, "during"):
                changed = copy.deepcopy(trace)
                changed[0]["phase"] = phase
                if phase == "before":
                    accept("retain-actual-method-adjacent-before-phase:" + family,
                           _validate_native_method_trace(
                               family, matrix, changed,
                               graph["native_sha256_by_family"][family],
                               _synthetic_owner_validator,
                           ) == changed)
                else:
                    rejected("reject-reordered-native-owner-phase:"
                             + family + ":" + repr(phase),
                             lambda changed=changed, family=family:
                             _validate_native_method_trace(
                                 family, matrix, changed,
                                 graph["native_sha256_by_family"][family],
                                 _synthetic_owner_validator,
                             ))
            raw = canonical({"synthetic_only": family})
            actual = hashlib.sha256(raw).hexdigest()
            for kind in PROOF_KINDS:
                accept("bind-full-canonical-original-proof-bytes:"
                       + family + ":" + kind,
                       _require_real_proof_bytes(raw, actual, family, kind) == raw)
                rejected("reject-substituted-full-original-proof-bytes:"
                         + family + ":" + kind,
                         lambda kind=kind, family=family:
                         _require_real_proof_bytes(
                             raw + b"forged", actual, family, kind,
                         ))

        for name, relative in (
            ("absolute", "/tmp/postfinal-locale-v15-forged.json"),
            ("traversal", "oracle/cpython-3.14.6/evidence/../forged.json"),
            ("v6-reference", V6_REFERENCE_RELATIVE),
            ("v6-all", "oracle/cpython-3.14.6/evidence/postfinal-locale-v6-all.json"),
            ("backslash", "oracle\\cpython-3.14.6\\forged.json"),
            ("nul", "oracle/cpython-3.14.6/evidence/forged\x00.json"),
        ):
            rejected("reject-unsafe-or-historical-evidence-destination:" + name,
                     lambda relative=relative: _safe_output_path(relative))
        for relative in sorted(APPROVED_OUTPUTS):
            accept("allow-only-an-exact-separate-v15-destination:" + relative,
                   _safe_output_path(relative) == ROOT / relative)

        nonroundtripping_original = {
            "genuine_tuple": ("source-only", 7, True),
            "genuine_nested_integer_keys": {7: "actual integer key"},
            "status": "PASS",
        }
        normalized_publication, normalized_payload = (
            _normalize_publication_document(nonroundtripping_original)
        )
        accept("freeze-normalized-canonical-json-before-exclusive-creation",
               normalized_publication != nonroundtripping_original
               and normalized_publication["genuine_tuple"]
               == ["source-only", 7, True]
               and normalized_publication["genuine_nested_integer_keys"]
               == {"7": "actual integer key"}
               and canonical(normalized_publication) + b"\n"
               == normalized_payload)
        accept("reread-exact-normalized-report-without-python-shape-equality",
               _validate_normalized_publication_readback(
                   normalized_payload, normalized_payload,
                   normalized_publication,
               ) == normalized_publication)
        for label, poisoned in (
            ("missing-newline", normalized_payload[:-1]),
            ("appended-bytes", normalized_payload + b"forged"),
            ("whitespace-before-canonical-json", b" " + normalized_payload),
            ("substituted-canonical-json", canonical({"status": "FAIL"})
             + b"\n"),
        ):
            rejected("reject-fabricated-canonical-publication-reread:" + label,
                     lambda poisoned=poisoned:
                     _validate_normalized_publication_readback(
                         poisoned, normalized_payload,
                         normalized_publication,
                     ))
        for label, unsafe in (
            ("not-a-mapping", []),
            ("nonfinite-nan", {"status": float("nan")}),
            ("positive-infinity", {"status": float("inf")}),
            ("negative-infinity", {"status": -float("inf")}),
            ("not-json-serializable", {"status": {"non-json-set"}}),
        ):
            rejected("reject-unsafe-original-before-exclusive-creation:" + label,
                     lambda unsafe=unsafe:
                     _normalize_publication_document(unsafe))

        receipt_payload = canonical({"synthetic_publication": True}) + b"\n"
        base_receipt: dict[str, Any] = {
            "schema": SCHEMA + "-actual-exclusive-publication-receipt",
            "path": REPORT_RELATIVE,
            "expected_payload_sha256": hashlib.sha256(
                receipt_payload,
            ).hexdigest(),
            "expected_payload_bytes": len(receipt_payload),
            "actual_file_created": False,
            "actual_payload_bytes_written": 0,
            "actual_write_calls": [],
            "actual_file_fsync": False,
            "actual_directory_fsync": False,
            "canonical_reread_succeeded": False,
            "fully_durable_publication": False,
        }
        receipt_states: dict[str, dict[str, Any]] = {
            "not-created": dict(base_receipt),
            "exclusively-created": {
                **base_receipt,
                "actual_file_created": True,
            },
            "partially-written": {
                **base_receipt,
                "actual_file_created": True,
                "actual_payload_bytes_written": 1,
                "actual_write_calls": [{
                    "requested_bytes": len(receipt_payload),
                    "returned_bytes": 1,
                }],
            },
            "complete-not-synced": {
                **base_receipt,
                "actual_file_created": True,
                "actual_payload_bytes_written": len(receipt_payload),
                "actual_write_calls": [{
                    "requested_bytes": len(receipt_payload),
                    "returned_bytes": len(receipt_payload),
                }],
            },
            "file-synced-only": {
                **base_receipt,
                "actual_file_created": True,
                "actual_payload_bytes_written": len(receipt_payload),
                "actual_write_calls": [{
                    "requested_bytes": len(receipt_payload),
                    "returned_bytes": len(receipt_payload),
                }],
                "actual_file_fsync": True,
            },
            "fully-directory-durable": {
                **base_receipt,
                "actual_file_created": True,
                "actual_payload_bytes_written": len(receipt_payload),
                "actual_write_calls": [{
                    "requested_bytes": len(receipt_payload),
                    "returned_bytes": len(receipt_payload),
                }],
                "actual_file_fsync": True,
                "actual_directory_fsync": True,
                "fully_durable_publication": True,
            },
            "fully-durable-canonical-reread": {
                **base_receipt,
                "actual_file_created": True,
                "actual_payload_bytes_written": len(receipt_payload),
                "actual_write_calls": [{
                    "requested_bytes": len(receipt_payload),
                    "returned_bytes": len(receipt_payload),
                }],
                "actual_file_fsync": True,
                "actual_directory_fsync": True,
                "canonical_reread_succeeded": True,
                "fully_durable_publication": True,
            },
        }
        for stage, receipt in receipt_states.items():
            accept("preserve-immediate-truthful-exclusive-receipt:" + stage,
                   _validate_publication_receipt(receipt) == receipt)
        completed_success_receipt = copy.deepcopy(
            receipt_states["fully-durable-canonical-reread"],
        )
        immutable_success_receipt = _freeze_successful_publication_receipt(
            completed_success_receipt,
        )
        accept("return-immutable-complete-actual-success-receipt-bytes",
               type(immutable_success_receipt) is bytes
               and _thaw_successful_publication_receipt(
                   immutable_success_receipt,
                   REPORT_RELATIVE,
                   completed_success_receipt["expected_payload_sha256"],
               ) == completed_success_receipt)
        aliased_success_receipt = copy.deepcopy(completed_success_receipt)
        detached_success_receipt = _freeze_successful_publication_receipt(
            aliased_success_receipt,
        )
        aliased_success_receipt["actual_write_calls"][0][
            "returned_bytes"
        ] = 0
        accept("freeze-success-receipt-before-any-later-alias-mutation",
               _thaw_successful_publication_receipt(
                   detached_success_receipt,
                   REPORT_RELATIVE,
                   completed_success_receipt["expected_payload_sha256"],
               ) == completed_success_receipt)
        for stage in (
            "not-created", "exclusively-created", "partially-written",
            "complete-not-synced", "file-synced-only",
            "fully-directory-durable",
        ):
            rejected("reject-incomplete-success-receipt-freeze:" + stage,
                     lambda stage=stage:
                     _freeze_successful_publication_receipt(
                         receipt_states[stage],
                     ))
        for label, poisoned in (
            ("empty", b""),
            ("truncated", immutable_success_receipt[:-1]),
            ("appended", immutable_success_receipt + b"forged"),
            ("whitespace", b" " + immutable_success_receipt),
        ):
            rejected("reject-forged-immutable-success-receipt:" + label,
                     lambda poisoned=poisoned:
                     _thaw_successful_publication_receipt(
                         poisoned, REPORT_RELATIVE,
                         completed_success_receipt["expected_payload_sha256"],
                     ))
        rejected("reject-immutable-success-receipt-for-wrong-report-path",
                 lambda: _thaw_successful_publication_receipt(
                     immutable_success_receipt,
                     REPORT_RECEIPT_RELATIVE,
                     completed_success_receipt["expected_payload_sha256"],
                 ))
        rejected("reject-immutable-success-receipt-for-wrong-report-sha256",
                 lambda: _thaw_successful_publication_receipt(
                     immutable_success_receipt, REPORT_RELATIVE,
                     _synthetic_digest("forged-original-success-receipt"),
                 ))
        synthetic_sidecar_digest = _synthetic_digest(
            "actual-separate-v15-success-receipt-file",
        )
        synthetic_sidecar_receipt = copy.deepcopy(completed_success_receipt)
        synthetic_sidecar_receipt["path"] = REPORT_RECEIPT_RELATIVE
        synthetic_sidecar_receipt["expected_payload_sha256"] = (
            synthetic_sidecar_digest
        )
        complete_durable_publication = {
            "path": REPORT_RELATIVE,
            "sha256": completed_success_receipt[
                "expected_payload_sha256"
            ],
            "fully_durable_publication": True,
            "actual_exclusive_publication_receipt": copy.deepcopy(
                completed_success_receipt,
            ),
            "publication_receipt_path": REPORT_RECEIPT_RELATIVE,
            "publication_receipt_sha256": synthetic_sidecar_digest,
            "actual_receipt_publication_receipt": copy.deepcopy(
                synthetic_sidecar_receipt,
            ),
        }
        accept("retain-complete-primary-and-durable-sidecar-success-receipts",
               _validate_durable_success_publication(
                   complete_durable_publication,
                   REPORT_RELATIVE,
                   REPORT_RECEIPT_RELATIVE,
               ) == complete_durable_publication)
        for family in FAMILIES:
            role_digest = _synthetic_digest(
                "actual-complete-original-role-publication:" + family,
            )
            role_receipt_digest = _synthetic_digest(
                "actual-complete-original-role-receipt-publication:" + family,
            )
            role_receipt = copy.deepcopy(completed_success_receipt)
            role_receipt["path"] = ROLE_REPORT_RELATIVES[family]
            role_receipt["expected_payload_sha256"] = role_digest
            role_sidecar = copy.deepcopy(completed_success_receipt)
            role_sidecar["path"] = ROLE_RECEIPT_RELATIVES[family]
            role_sidecar["expected_payload_sha256"] = role_receipt_digest
            genuine_role_publication = {
                "path": ROLE_REPORT_RELATIVES[family],
                "sha256": role_digest,
                "fully_durable_publication": True,
                "actual_exclusive_publication_receipt": role_receipt,
                "publication_receipt_path": ROLE_RECEIPT_RELATIVES[family],
                "publication_receipt_sha256": role_receipt_digest,
                "actual_receipt_publication_receipt": role_sidecar,
            }
            accept("retain-durable-success-receipt-for-original-role:" + family,
                   _validate_durable_success_publication(
                       genuine_role_publication,
                       ROLE_REPORT_RELATIVES[family],
                       ROLE_RECEIPT_RELATIVES[family],
                   ) == genuine_role_publication)
            swapped_role_publication = copy.deepcopy(genuine_role_publication)
            swapped_role_publication["actual_receipt_publication_receipt"] = (
                copy.deepcopy(role_receipt)
            )
            rejected("reject-swapped-real-role-and-receipt-publications:"
                     + family,
                     lambda swapped_role_publication=swapped_role_publication,
                     family=family:
                     _validate_durable_success_publication(
                         swapped_role_publication,
                         ROLE_REPORT_RELATIVES[family],
                         ROLE_RECEIPT_RELATIVES[family],
                     ))
        for key in tuple(complete_durable_publication):
            changed = copy.deepcopy(complete_durable_publication)
            changed.pop(key)
            rejected("reject-omitted-durable-success-receipt-field:" + key,
                     lambda changed=changed:
                     _validate_durable_success_publication(
                         changed, REPORT_RELATIVE, REPORT_RECEIPT_RELATIVE,
                     ))
        for label, key, wrong in (
            ("primary-path", "path", REPORT_RECEIPT_RELATIVE),
            ("primary-sha256", "sha256", _synthetic_digest(
                "forged-primary-success-document",
            )),
            ("false-durability", "fully_durable_publication", False),
            ("boolean-as-integer", "fully_durable_publication", 1),
            ("sidecar-path", "publication_receipt_path", REPORT_RELATIVE),
            ("sidecar-sha256", "publication_receipt_sha256",
             _synthetic_digest("forged-sidecar-success-document")),
            ("missing-primary-receipt",
             "actual_exclusive_publication_receipt", {}),
            ("missing-sidecar-receipt",
             "actual_receipt_publication_receipt", {}),
        ):
            changed = copy.deepcopy(complete_durable_publication)
            changed[key] = wrong
            rejected("reject-forged-durable-original-success-receipt:" + label,
                     lambda changed=changed:
                     _validate_durable_success_publication(
                         changed, REPORT_RELATIVE, REPORT_RECEIPT_RELATIVE,
                     ))
        lost_sidecar_failure = OfficialV15PublicationFailure(
            "candidate-free-durable-success-receipt-sidecar-failure",
            synthetic_sidecar_receipt,
            (completed_success_receipt,),
        )
        accept("preserve-actual-durable-primary-when-receipt-sidecar-fails",
               len(lost_sidecar_failure.prior_receipts) == 1
               and lost_sidecar_failure.prior_receipts[0]
               == completed_success_receipt
               and lost_sidecar_failure.receipt == synthetic_sidecar_receipt)
        actual_partial = receipt_states["partially-written"]
        actual_error = OfficialV15PublicationFailure(
            "candidate-free-partial-receipt-only", actual_partial,
        )
        accept("retain-partial-created-file-receipt-on-publication-failure",
               actual_error.receipt == actual_partial
               and actual_error.receipt["actual_file_created"] is True
               and actual_error.receipt["fully_durable_publication"] is False)
        durable_reread_failure = receipt_states["fully-directory-durable"]
        durable_reread_error = OfficialV15PublicationFailure(
            "candidate-free-fully-durable-canonical-reread-failure",
            durable_reread_failure,
        )
        accept("retain-fully-durable-real-file-when-canonical-reread-fails",
               durable_reread_error.receipt == durable_reread_failure
               and durable_reread_error.receipt["actual_file_created"] is True
               and durable_reread_error.receipt["actual_file_fsync"] is True
               and durable_reread_error.receipt["actual_directory_fsync"] is True
               and durable_reread_error.receipt[
                   "fully_durable_publication"
               ] is True
               and durable_reread_error.receipt[
                   "canonical_reread_succeeded"
               ] is False)
        for key, wrong in (
            ("schema", SCHEMA + "-forged-receipt"),
            ("path", V6_REFERENCE_RELATIVE),
            ("expected_payload_sha256", "0" * 64),
            ("expected_payload_bytes", 0),
            ("expected_payload_bytes", True),
            ("actual_payload_bytes_written", -1),
            ("actual_payload_bytes_written", len(receipt_payload) + 1),
            ("actual_payload_bytes_written", True),
            ("actual_file_created", 1),
            ("actual_file_fsync", 1),
            ("actual_directory_fsync", 1),
            ("canonical_reread_succeeded", 1),
            ("fully_durable_publication", 1),
            ("actual_write_calls", "FORGED"),
        ):
            changed = copy.deepcopy(base_receipt)
            changed[key] = wrong
            rejected("reject-fabricated-immediate-publication-receipt:"
                     + key + ":" + repr(wrong),
                     lambda changed=changed:
                     _validate_publication_receipt(changed))
        inconsistent_receipts = {
            "hide-created-partial-file": {
                **actual_partial,
                "actual_file_created": False,
            },
            "claim-file-fsync-before-complete-write": {
                **actual_partial,
                "actual_file_fsync": True,
            },
            "claim-directory-fsync-before-file-fsync": {
                **receipt_states["complete-not-synced"],
                "actual_directory_fsync": True,
            },
            "claim-full-durability-before-directory-fsync": {
                **receipt_states["file-synced-only"],
                "fully_durable_publication": True,
            },
            "conceal-successfully-durable-publication": {
                **receipt_states["fully-directory-durable"],
                "fully_durable_publication": False,
            },
            "claim-canonical-reread-before-real-directory-durability": {
                **receipt_states["file-synced-only"],
                "canonical_reread_succeeded": True,
            },
            "conceal-actual-returned-write-syscall": {
                **actual_partial,
                "actual_write_calls": [],
            },
            "forge-actual-write-syscall-requested-bytes": {
                **actual_partial,
                "actual_write_calls": [{
                    "requested_bytes": len(receipt_payload) + 1,
                    "returned_bytes": 1,
                }],
            },
            "forge-actual-write-syscall-returned-bytes": {
                **actual_partial,
                "actual_write_calls": [{
                    "requested_bytes": len(receipt_payload),
                    "returned_bytes": 2,
                }],
            },
        }
        for label, changed in inconsistent_receipts.items():
            rejected("reject-misstated-actual-partial-publication:" + label,
                     lambda changed=changed:
                     _validate_publication_receipt(changed))
        for key in tuple(base_receipt):
            changed = dict(base_receipt)
            changed.pop(key)
            rejected("reject-omitted-actual-publication-receipt-field:" + key,
                     lambda changed=changed:
                     _validate_publication_receipt(changed))

        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns"):
            rejected("block-every-source-only-performance-clock:" + name,
                     lambda name=name: getattr(time, name)())
        for family in FAMILIES:
            rejected("block-every-source-only-candidate-import:" + family,
                     lambda family=family: importlib.import_module(
                         FAMILY_MODULES[family],
                     ))
        for name in (
            "tools.postfinal_cpython_locale_oracle_v6",
            "tools.postfinal_independent_engine_audit_v21",
            "tools.postfinal_current_build_proofs_v24",
        ):
            rejected("block-every-source-only-production-controller:" + name,
                     lambda name=name: importlib.import_module(name))
        rejected("block-source-only-builtin-production-import",
                 lambda: builtins.__import__("candidates.rust_candidate"))
        rejected("block-source-only-builtin-evidence-read",
                 lambda: builtins.open(ROOT / V6_REFERENCE_RELATIVE, "rb"))
        rejected("block-source-only-io-evidence-read",
                 lambda: io.open(ROOT / V6_REFERENCE_RELATIVE, "rb"))
        rejected("block-source-only-raw-evidence-read",
                 lambda: os.open(ROOT / V6_REFERENCE_RELATIVE, os.O_RDONLY))
        rejected("block-source-only-path-evidence-read",
                 lambda: (ROOT / V6_REFERENCE_RELATIVE).read_bytes())
        for label, relative in (
            ("v12-upstream-failure", V12_FIRST_UPSTREAM_FAILURE_RELATIVE),
            ("v12-upstream-captured-output", V12_FIRST_UPSTREAM_CAPTURE_RELATIVE),
            ("v13-upstream-failure", V13_FIRST_UPSTREAM_FAILURE_RELATIVE),
            ("v13-upstream-captured-output", V13_FIRST_UPSTREAM_CAPTURE_RELATIVE),
            ("v14-upstream-failure", V14_FIRST_UPSTREAM_FAILURE_RELATIVE),
            ("v14-upstream-captured-output", V14_FIRST_UPSTREAM_CAPTURE_RELATIVE),
            ("v13", V13_FIRST_FAILURE_RELATIVE),
            ("v15", V15_FIRST_FAILURE_RELATIVE),
            ("v17", V17_FIRST_FAILURE_RELATIVE),
            ("v19", V19_FIRST_FAILURE_RELATIVE),
            ("v19-durable", V19_DURABLE_REPORT_RELATIVE),
            ("v22", V22_FIRST_FAILURE_RELATIVE),
        ):
            rejected("block-source-only-historical-builtin-read:" + label,
                     lambda relative=relative:
                     builtins.open(ROOT / relative, "rb"))
            rejected("block-source-only-historical-io-read:" + label,
                     lambda relative=relative:
                     io.open(ROOT / relative, "rb"))
            rejected("block-source-only-historical-raw-read:" + label,
                     lambda relative=relative:
                     os.open(ROOT / relative, os.O_RDONLY))
            rejected("block-source-only-historical-path-read:" + label,
                     lambda relative=relative:
                     (ROOT / relative).read_bytes())
        rejected("block-source-only-production-source-read",
                 lambda: (ROOT / V21_SOURCE_RELATIVE).read_text())
        rejected("block-source-only-frozen-failed-v12-controller-source-read",
                 lambda: (ROOT / V12_SOURCE_RELATIVE).read_text())
        rejected("block-source-only-frozen-failed-v13-controller-source-read",
                 lambda: (ROOT / V13_SOURCE_RELATIVE).read_text())
        rejected("block-source-only-frozen-failed-v14-controller-source-read",
                 lambda: (ROOT / V14_SOURCE_RELATIVE).read_text())
        rejected("block-source-only-performance-directory-inspection",
                 lambda: (ROOT / "performance").exists())
        rejected("block-source-only-hidden-directory-inspection",
                 lambda: (ROOT / "oracle").iterdir())
        rejected("block-source-only-actual-reference-or-candidate-worker",
                 lambda: subprocess.run([str(PINNED_CPYTHON)]))
        rejected("block-source-only-actual-native-owner-process",
                 lambda: subprocess.Popen([str(PINNED_CPYTHON)]))
        rejected("block-source-only-actual-original-fork",
                 lambda: os.fork())
        rejected("block-source-only-actual-background-thread",
                 lambda: threading.Thread(target=lambda: None).start())
        rejected("block-source-only-generated-private-locale",
                 lambda: tempfile.TemporaryDirectory())
        rejected("block-source-only-actual-evidence-write",
                 lambda: (ROOT / REPORT_RELATIVE).write_bytes(b"forged"))
        rejected("block-unpublished-production-current-graph-proof-pins",
                 lambda: _candidate_pin_values("all", {}))
        accept("actually-intercept-evidence-and-production-source-reads",
               effects["file_read_attempts_blocked"] >= 58)
        accept("actually-intercept-every-source-only-worker-and-fork",
               effects["worker_attempts_blocked"] >= 3)
        accept("actually-intercept-candidate-and-proof-source-imports",
               effects["candidate_import_attempts_blocked"] >= 7)
        accept("actually-intercept-all-frozen-performance-clocks",
               effects["clock_attempts_blocked"] >= 8)
        accept("actually-intercept-private-locale-generation",
               effects["locale_attempts_blocked"] >= 1)
        accept("actually-intercept-background-thread-creation",
               effects["thread_attempts_blocked"] >= 1)
        accept("actually-intercept-production-result-file-writes",
               effects["file_write_attempts_blocked"] >= 1)
        accept("perform-zero-actual-source-reference-evidence-or-fixture-reads",
               effects["file_reads"] == 0)
        accept("perform-zero-actual-source-or-evidence-file-writes",
               effects["file_writes"] == 0)
        accept("start-zero-actual-candidate-reference-or-native-workers",
               effects["subprocesses"] == 0)
        accept("start-zero-actual-background-threads",
               effects["threads"] == 0)
        accept("sample-zero-actual-performance-clocks",
               effects["clock_samples"] == 0)
        accept("import-zero-actual-production-candidates",
               effects["candidate_imports"] == 0)
        accept("generate-zero-actual-private-locales",
               effects["locale_generations"] == 0)
        failed = [row["name"] for row in checks
                  if row.get("passed") is not True]
        require(not failed,
                "a genuine candidate-free V15 control failed: "
                + ", ".join(failed))
        require(len(checks) >= 1_000,
                "at least 1,000 deterministic candidate-free V15 controls "
                "are required")
        observed_effects = dict(effects)
    require(original is None and inventory is None and durable is None,
            "a source-only test must not load V6, V21, V24, or candidate code")
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "passed": True,
        "synthetic_only": True,
        "python": "3.14.6",
        "check_count": len(checks),
        "checks": checks,
        "immutable_v6_source_sha256": V6_SOURCE_SHA256,
        "immutable_v6_protocol_sha256": V6_PROTOCOL_SHA256,
        "immutable_v6_reference_sha256": V6_REFERENCE_SHA256,
        "preserved_v12_upstream_failure_path": (
            V12_FIRST_UPSTREAM_FAILURE_RELATIVE
        ),
        "preserved_v12_upstream_failure_sha256": (
            V12_FIRST_UPSTREAM_FAILURE_SHA256
        ),
        "preserved_v12_upstream_failure_bytes": (
            V12_FIRST_UPSTREAM_FAILURE_BYTES
        ),
        "preserved_v12_captured_output_path": (
            V12_FIRST_UPSTREAM_CAPTURE_RELATIVE
        ),
        "preserved_v12_captured_output_sha256": (
            V12_FIRST_UPSTREAM_CAPTURE_SHA256
        ),
        "preserved_v12_captured_output_bytes": (
            V12_FIRST_UPSTREAM_CAPTURE_BYTES
        ),
        "preserved_v12_worker_stdout_sha256": (
            V12_FIRST_UPSTREAM_STDOUT_SHA256
        ),
        "preserved_v12_worker_stdout_bytes": (
            V12_FIRST_UPSTREAM_STDOUT_BYTES
        ),
        "historical_v12_upstream_failure_qualifies_current_engine": False,
        "preserved_v13_upstream_failure_path": (
            V13_FIRST_UPSTREAM_FAILURE_RELATIVE
        ),
        "preserved_v13_upstream_failure_sha256": (
            V13_FIRST_UPSTREAM_FAILURE_SHA256
        ),
        "preserved_v13_upstream_failure_bytes": (
            V13_FIRST_UPSTREAM_FAILURE_BYTES
        ),
        "preserved_v13_captured_output_path": (
            V13_FIRST_UPSTREAM_CAPTURE_RELATIVE
        ),
        "preserved_v13_captured_output_sha256": (
            V13_FIRST_UPSTREAM_CAPTURE_SHA256
        ),
        "preserved_v13_captured_output_bytes": (
            V13_FIRST_UPSTREAM_CAPTURE_BYTES
        ),
        "preserved_v13_worker_stdout_sha256": (
            V13_FIRST_UPSTREAM_STDOUT_SHA256
        ),
        "preserved_v13_worker_stdout_bytes": (
            V13_FIRST_UPSTREAM_STDOUT_BYTES
        ),
        "historical_v13_upstream_failure_qualifies_current_engine": False,
        "preserved_v14_upstream_failure_path": (
            V14_FIRST_UPSTREAM_FAILURE_RELATIVE
        ),
        "preserved_v14_upstream_failure_sha256": (
            V14_FIRST_UPSTREAM_FAILURE_SHA256
        ),
        "preserved_v14_upstream_failure_bytes": (
            V14_FIRST_UPSTREAM_FAILURE_BYTES
        ),
        "preserved_v14_captured_output_path": (
            V14_FIRST_UPSTREAM_CAPTURE_RELATIVE
        ),
        "preserved_v14_captured_output_sha256": (
            V14_FIRST_UPSTREAM_CAPTURE_SHA256
        ),
        "preserved_v14_captured_output_bytes": (
            V14_FIRST_UPSTREAM_CAPTURE_BYTES
        ),
        "preserved_v14_worker_stdout_sha256": (
            V14_FIRST_UPSTREAM_STDOUT_SHA256
        ),
        "preserved_v14_worker_stdout_bytes": (
            V14_FIRST_UPSTREAM_STDOUT_BYTES
        ),
        "historical_v14_upstream_failure_qualifies_current_engine": False,
        "preserved_v13_first_failure_path": V13_FIRST_FAILURE_RELATIVE,
        "preserved_v13_first_failure_sha256": V13_FIRST_FAILURE_SHA256,
        "historical_v13_failure_qualifies_current_engine": False,
        "preserved_v15_first_failure_path": V15_FIRST_FAILURE_RELATIVE,
        "preserved_v15_first_failure_sha256": V15_FIRST_FAILURE_SHA256,
        "historical_v15_failure_qualifies_current_engine": False,
        "preserved_v17_first_failure_path": V17_FIRST_FAILURE_RELATIVE,
        "preserved_v17_first_failure_sha256": V17_FIRST_FAILURE_SHA256,
        "historical_v17_failure_qualifies_current_engine": False,
        "preserved_v19_first_failure_path": V19_FIRST_FAILURE_RELATIVE,
        "preserved_v19_first_failure_sha256": V19_FIRST_FAILURE_SHA256,
        "preserved_v19_durable_embedded_report_path": (
            V19_DURABLE_REPORT_RELATIVE
        ),
        "preserved_v19_durable_embedded_report_sha256": (
            V19_DURABLE_REPORT_SHA256
        ),
        "preserved_v19_durable_embedded_report_bytes": (
            V19_DURABLE_REPORT_BYTES
        ),
        "historical_v19_failure_qualifies_current_engine": False,
        "preserved_v22_first_failure_path": V22_FIRST_FAILURE_RELATIVE,
        "preserved_v22_first_failure_sha256": V22_FIRST_FAILURE_SHA256,
        "preserved_v22_original_document_field_count": 25,
        "preserved_v22_normalized_incident_field_count": 27,
        "preserved_v22_inline_source_line_count": 25,
        "preserved_v22_combined_traceback_line_count": 24,
        "historical_v22_failure_qualifies_current_engine": False,
        "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
        "original_public_method_count": PUBLIC_METHODS,
        "original_private_method_count": PRIVATE_METHODS,
        "original_support_module_count": SUPPORT_MODULES,
        "original_corpus_case_count": CORPUS_CASES,
        "original_external_fixture_assertion_count": EXTERNAL_FIXTURE_ASSERTIONS,
        "actual_configured_upstream_memory_bytes": CONFIGURED_MEMORY_BYTES,
        "qualified_artifacts_required_per_family": len(PROOF_KINDS),
        "native_method_owners_required_per_role": 2 * PUBLIC_METHODS,
        "cached_matcher_checks_required_per_role": 2 * PUBLIC_METHODS,
        "candidate_imports": 0,
        "subprocesses": 0,
        "threads": 0,
        "file_reads": 0,
        "file_writes": 0,
        "clock_samples": 0,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "actual_native_owner_workers": 0,
        "actual_official_method_checks": 0,
        "synthetic_results_qualify_candidates": False,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "effects": observed_effects,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Qualify all original CPython methods against genuine "
        "current independently guarded native engines.",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--candidate", choices=("all", *FAMILIES))
    parser.add_argument("--source-sha256")
    parser.add_argument("--protocol-sha256")
    parser.add_argument("--reference-sha256")
    parser.add_argument("--v21-source-sha256")
    parser.add_argument("--v21-protocol-sha256")
    parser.add_argument("--v24-source-sha256")
    parser.add_argument("--v24-protocol-sha256")
    parser.add_argument("--base-report-sha256")
    parser.add_argument("--strict-report-sha256")
    for family in FAMILIES:
        for kind in PROOF_KINDS:
            parser.add_argument(
                "--" + family + "-" + kind.replace("_", "-") + "-sha256",
            )
    return parser.parse_args(arguments)


def _failure_document(
    error: OfficialV15WorkerFailure, options: argparse.Namespace,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-actual-role-failure",
        "status": "FAIL",
        "role": error.role,
        "reason": str(error),
        "details": error.details,
        "source_sha256": options.source_sha256,
        "protocol_sha256": options.protocol_sha256,
        "immutable_v6_reference_sha256": V6_REFERENCE_SHA256,
        "synthetic": False,
        "production_observations_invented": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    try:
        if options.self_test:
            require(options.source_sha256 is None
                    and options.protocol_sha256 is None
                    and options.reference_sha256 is None
                    and options.v21_source_sha256 is None
                    and options.v21_protocol_sha256 is None
                    and options.v24_source_sha256 is None
                    and options.v24_protocol_sha256 is None
                    and options.base_report_sha256 is None
                    and options.strict_report_sha256 is None
                    and all(
                        getattr(options, family + "_" + kind + "_sha256")
                        is None
                        for family in FAMILIES for kind in PROOF_KINDS
                    ),
                    "candidate-free V15 source controls cannot consume actual "
                    "reference, owner, proof, source, or evidence pins")
            result = source_self_test()
        else:
            require(valid_sha256(options.source_sha256)
                    and options.protocol_sha256 == PROTOCOL_SHA256
                    and options.reference_sha256 == V6_REFERENCE_SHA256,
                    "BLOCKED: publish the genuine V15 source/protocol and "
                    "authenticate the exact parent-supplied double V6 reference")
            supplied: dict[str, Any] = {
                "audit_source": options.v21_source_sha256,
                "audit_protocol": options.v21_protocol_sha256,
                "proof_source": options.v24_source_sha256,
                "proof_protocol": options.v24_protocol_sha256,
                "base_report": options.base_report_sha256,
                "strict_report": options.strict_report_sha256,
                **{
                    family + "_" + kind:
                    getattr(options, family + "_" + kind + "_sha256")
                    for family in FAMILIES for kind in PROOF_KINDS
                },
            }
            _candidate_pin_values(str(options.candidate), supplied)
            result = run_candidates(
                str(options.candidate), str(options.source_sha256), supplied,
            )
    except OfficialV15WorkerFailure as error:
        failure = _failure_document(error, options)
        destinations: list[str] = []
        if error.role in FAMILIES:
            destinations.append(ROLE_FAILURE_RELATIVES[error.role])
            if options.candidate == "all":
                destinations.append(REPORT_FAILURE_RELATIVE)
        elif error.role == "all" and options.candidate == "all":
            destinations.append(REPORT_FAILURE_RELATIVE)
        preserved: list[dict[str, Any]] = []
        for destination in destinations:
            try:
                payload = dict(failure)
                payload["actual_failure_destination"] = destination
                if destination == REPORT_FAILURE_RELATIVE:
                    payload["schema"] = SCHEMA + "-all-family-failure"
                    payload["all_family_campaign_qualified"] = False
                observed, immutable_receipt = _exclusive_write(
                    payload, destination,
                )
                actual_receipt = _thaw_successful_publication_receipt(
                    immutable_receipt, destination, observed,
                )
                preserved.append({
                    "path": destination,
                    "sha256": observed,
                    "actual_exclusive_publication_receipt": actual_receipt,
                })
            except (OfficialV15Error, OSError, ValueError,
                    TypeError) as preservation_error:
                observed_error: dict[str, Any] = {
                    "path": destination,
                    "actual_error_type": type(preservation_error).__name__,
                    "actual_error": str(preservation_error),
                }
                if isinstance(preservation_error, OfficialV15PublicationFailure):
                    observed_error["actual_exclusive_publication_receipt"] = (
                        copy.deepcopy(dict(preservation_error.receipt))
                    )
                    observed_error["actual_prior_publication_receipts"] = [
                        copy.deepcopy(dict(prior))
                        for prior in preservation_error.prior_receipts
                    ]
                failure.setdefault(
                    "actual_preservation_errors", [],
                ).append(observed_error)
        failure["actual_exclusively_preserved_failure_reports"] = preserved
        print(json.dumps(failure, ensure_ascii=True, allow_nan=False,
                         sort_keys=True, separators=(",", ":")), file=sys.stderr)
        return 2
    except (Exception, MemoryError) as error:
        print(json.dumps({
            "schema": SCHEMA + "-controller-failure",
            "status": "BLOCKED",
            "reason": str(error),
            "actual_error_type": type(error).__name__,
            "production_observations_invented": False,
            "actual_execution_or_publication_not_asserted": True,
            "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED",
        }, ensure_ascii=True, allow_nan=False,
            sort_keys=True, separators=(",", ":")), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True, allow_nan=False,
                     sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
