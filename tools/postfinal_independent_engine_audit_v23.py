#!/usr/bin/env python3
"""Independently audit a freshly rehashed Rust, C-VM, and Zig source graph."""

from __future__ import annotations

import argparse
import ast
import builtins
import contextlib
import copy
import hashlib
import importlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import time
import types
from typing import Any, Callable, Iterator, Mapping


ROOT = Path(__file__).resolve().parent.parent
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

from tools import postfinal_current_build_proofs_v11 as v11
from tools import postfinal_from_scratch_audit_v10 as original_owner
from tools import postfinal_independent_engine_audit_v21 as historical_v21
from tools import postfinal_no_delegation_audit_v10 as original_strict


SCHEMA = "rebar-postfinal-independent-engine-audit-v23"
BASE_SCHEMA = "rebar-postfinal-from-scratch-audit-v23"
STRICT_SCHEMA = "rebar-postfinal-no-delegation-audit-v23"
SOURCE_RELATIVE = "tools/postfinal_independent_engine_audit_v23.py"
PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V23.md"
)
PROTOCOL_SHA256 = (
    "8b3da77ba5a659d72c940cd595726b1d9b000ed7db1fac5027745c37d504f6bd"
)
BASE_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V23.json"
)
BASE_FAILURE_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V23-FAILURES.json"
)
STRICT_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V23.json"
)
STRICT_FAILURE_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V23-FAILURES.json"
)
BASE_RECEIPT_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-FROM-SCRATCH-AUDIT-V23-PUBLICATION-RECEIPT.json"
)
BASE_FAILURE_RECEIPT_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-FROM-SCRATCH-AUDIT-V23-FAILURES-PUBLICATION-RECEIPT.json"
)
STRICT_RECEIPT_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-NO-DELEGATION-AUDIT-V23-PUBLICATION-RECEIPT.json"
)
STRICT_FAILURE_RECEIPT_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-NO-DELEGATION-AUDIT-V23-FAILURES-PUBLICATION-RECEIPT.json"
)
APPROVED_OUTPUTS = frozenset({
    BASE_REPORT_RELATIVE,
    BASE_FAILURE_RELATIVE,
    STRICT_REPORT_RELATIVE,
    STRICT_FAILURE_RELATIVE,
    BASE_RECEIPT_RELATIVE,
    BASE_FAILURE_RECEIPT_RELATIVE,
    STRICT_RECEIPT_RELATIVE,
    STRICT_FAILURE_RECEIPT_RELATIVE,
})
CORE_FAMILIES = tuple(original_owner.CORE_FAMILIES)
OWNED_SOURCE_PATHS = {
    family: tuple(paths)
    for family, paths in original_owner.OWNED_SOURCE_PATHS.items()
}
OWNED_NATIVE_PATHS = {
    family: dict(paths)
    for family, paths in original_owner.OWNED_NATIVE_PATHS.items()
}
MAX_REPORT_BYTES = original_owner.MAX_REPORT_BYTES

HISTORICAL_V21_SOURCE_SHA256 = (
    "ded077962416ada3bddd825d77b2e6785fe3b01184fe5d9058ec17a57b08ea4d"
)
HISTORICAL_V21_PROTOCOL_SHA256 = (
    "5a78673c6b23e4781070cf5a2290d5f6cecd402fff77ff388d8795370de93a1f"
)
V15_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v15.py"
V15_SOURCE_SHA256 = (
    "12adb54e895ac0154b1b08ea96cd73b6cbfff4713c764058c5551fe6bba68c43"
)
V15_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V15.md"
V15_PROTOCOL_SHA256 = (
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
METHOD_MATRIX_SHA256 = (
    "5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a"
)
ORIGINAL_METHODS = 165
PUBLIC_METHODS = 152
PRIVATE_METHODS = 13
PRIVATE_CLASS_WAIVERS = {
    "DebugTests": {
        "methods": 4,
        "reason": "CPython-only textual disassembly of private matching opcodes",
    },
    "ImplementationTest": {
        "methods": 9,
        "reason": (
            "private CPython regex compiler, _sre, type internals, "
            "and deprecated private implementation modules"
        ),
    },
}
V6_BASELINE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v6-self-oracle.json"
)
V6_BASELINE_SHA256 = (
    "1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf"
)
V15_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v15-rust-failures.json"
)
V15_FAILURE_SHA256 = (
    "fcd83830b36afd94dee6b926764a6300eaf048d5fa81404563d7e8afea2482c2"
)
V15_OWNERSHIP_FAILURE_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-FROM-SCRATCH-AUDIT-V15-"
    "PRESERVED-FAILURE-CODEC-PREFLIGHT-FAILURE.json"
)
V15_OWNERSHIP_FAILURE_SHA256 = (
    "a3695f1fd847e9ad882783d18c519b551d7791c5327f55964e202a31ade818ff"
)
V15_FAILURE_BYTES = 17_338_567
V15_STDOUT_SHA256 = (
    "bb6ed67d4cf96c2bc1be9dd64779cb5219ac3cdcf909fd5efd93dbf6da8a55ac"
)
V15_STDOUT_BYTES = 3_474_497
V15_FORENSIC_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "postfinal-locale-v15-rust-readonly-failure-forensic.json"
)
V15_FORENSIC_SHA256 = (
    "4613b2421b3df30c5bebdbb4ae7c0d3530d80b70d5a627396aad2a25fefe85eb"
)
V15_SUMMARY_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "postfinal-locale-v15-rust-failures-production-summary.json"
)
V15_SUMMARY_SHA256 = (
    "d923e4687be96751e11b334cf8a37c0744552d01592cbb665bc4ec0cf9432c10"
)
PRIVATE_DEBUG_METHOD = "ReTests.test_memory_leaks"
PRIVATE_DEBUG_REASON = "requires debug build"
PRIVATE_DEBUG_SKIP_KIND = "named-private-debug-condition"
PRIVATE_DEBUG_AST_SHA256 = (
    "840264aaf4bf27c06d29ac78664767327a8f4b90008c5db994c88542c692b389"
)
PICKLING_METHOD = "ReTests.test_pickling"
PICKLING_ERROR = "cannot import name '_compile' from 'candidates.rust_candidate'"
HARNESS_ERROR_MARKER = "stage07_blocked_regex"


class AuditV23Error(AssertionError):
    """Fresh ownership, immutable history, or exclusive publication failed."""


class AuditV23PublicationFailure(AuditV23Error):
    """Keep only the publication transitions that actually took place."""

    def __init__(self, message: str, receipt: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.receipt = copy.deepcopy(dict(receipt))


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise AuditV23Error(message)


def valid_sha256(value: Any) -> bool:
    return bool(original_owner.core.valid_sha256(value))


def canonical(document: Mapping[str, Any]) -> bytes:
    require(isinstance(document, Mapping), "V23 requires a complete JSON object")
    try:
        raw = (
            json.dumps(
                document,
                ensure_ascii=True,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError) as error:
        raise AuditV23Error("V23 requires strict finite canonical JSON") from error
    require(0 < len(raw) <= MAX_REPORT_BYTES,
            "V23 canonical evidence exceeds the real bounded report limit")
    decoded = v11.decode_json(raw, "strict complete V23 canonical evidence")
    require(decoded == dict(document),
            "V23 canonical normalization changed its complete Python document")
    return raw


def digest_value(value: Any) -> str:
    try:
        payload = json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError) as error:
        raise AuditV23Error("V23 requires the exact original finite value digest") from error
    return hashlib.sha256(payload).hexdigest()


def verify_runtime_source_only() -> None:
    v11.verify_runtime()
    original_owner.verify_runtime()
    original_strict.verify_runtime()
    require(
        ROOT == v11.ROOT == original_owner.ROOT == original_strict.ROOT
        == historical_v21.ROOT
        and Path(__file__).resolve() == ROOT / SOURCE_RELATIVE
        and CORE_FAMILIES == ("rust", "vm", "zig")
        and set(OWNED_SOURCE_PATHS) == set(CORE_FAMILIES)
        and set(OWNED_NATIVE_PATHS) == set(CORE_FAMILIES)
        and sum(map(len, OWNED_SOURCE_PATHS.values())) == 12
        and len({p for rows in OWNED_SOURCE_PATHS.values() for p in rows}) == 12
        and sum(map(len, OWNED_NATIVE_PATHS.values())) == 5
        and len({
            path
            for rows in OWNED_NATIVE_PATHS.values()
            for path in rows.values()
        }) == 5
        and original_strict.independent is original_owner
        and historical_v21.SCHEMA
        == "rebar-postfinal-independent-engine-audit-v21"
        and historical_v21.PROTOCOL_SHA256 == HISTORICAL_V21_PROTOCOL_SHA256
        and historical_v21.V15_FIRST_FAILURE_RELATIVE
        == V15_OWNERSHIP_FAILURE_RELATIVE
        and historical_v21.V15_FIRST_FAILURE_SHA256
        == V15_OWNERSHIP_FAILURE_SHA256
        and V15_FAILURE_SHA256 != V15_OWNERSHIP_FAILURE_SHA256
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "V23 requires isolated pinned CPython and all twelve owned sources/five ELFs",
    )


def validate_parent_environment(environment: Mapping[str, Any]) -> dict[str, str]:
    require(isinstance(environment, Mapping), "the actual V23 parent is missing")
    expected = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONPATH": str(ROOT),
    }
    for key, value in expected.items():
        require(type(environment.get(key)) is str and environment.get(key) == value,
                "V23 requires the exact isolated production parent: " + key)
    return expected


def verify_production_runtime() -> dict[str, str]:
    verify_runtime_source_only()
    return validate_parent_environment(os.environ)


def authenticate_controller() -> dict[str, str]:
    verify_production_runtime()
    source = v11.read_regular(ROOT / SOURCE_RELATIVE, "the actual V23 owner source")
    protocol = v11.authenticate_frozen(PROTOCOL_RELATIVE, PROTOCOL_SHA256)
    require(hashlib.sha256(protocol).hexdigest() == PROTOCOL_SHA256,
            "the separately frozen V23 protocol changed")
    pins = (
        (historical_v21.SOURCE_RELATIVE, HISTORICAL_V21_SOURCE_SHA256),
        (historical_v21.PROTOCOL_RELATIVE, HISTORICAL_V21_PROTOCOL_SHA256),
        (original_owner.SOURCE_RELATIVE, historical_v21.V10_OWNER_SOURCE_SHA256),
        (original_strict.SOURCE_RELATIVE, historical_v21.V10_STRICT_SOURCE_SHA256),
        (original_owner.PROTOCOL_RELATIVE, historical_v21.V10_PROTOCOL_SHA256),
        (v11.SOURCE_RELATIVE, historical_v21.V11_SOURCE_SHA256),
        (v11.STAGE07_RELATIVE, v11.STAGE07_SHA256),
        (V6_SOURCE_RELATIVE, V6_SOURCE_SHA256),
        (V6_PROTOCOL_RELATIVE, V6_PROTOCOL_SHA256),
        (V15_SOURCE_RELATIVE, V15_SOURCE_SHA256),
        (V15_PROTOCOL_RELATIVE, V15_PROTOCOL_SHA256),
    )
    for relative, digest in pins:
        v11.authenticate_frozen(relative, digest)
    original_owner.validate_worker_source()
    return {
        "source_path": SOURCE_RELATIVE,
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": PROTOCOL_SHA256,
    }


def destination_name(value: Any) -> str:
    require(type(value) is str and value in APPROVED_OUTPUTS,
            "only an exact new V23 report or durable receipt is authorized")
    parsed = PurePosixPath(value)
    require(not parsed.is_absolute() and ".." not in parsed.parts
            and "\\" not in value and "\x00" not in value
            and parsed.as_posix() == value,
            "a V23 report destination escapes its immutable allowlist")
    return value


def mode_destinations(strict: bool, passed: bool) -> tuple[str, str]:
    require(type(strict) is bool and type(passed) is bool,
            "a V23 destination requires exact boolean mode and status")
    choices = {
        (False, True): (BASE_REPORT_RELATIVE, BASE_RECEIPT_RELATIVE),
        (False, False): (BASE_FAILURE_RELATIVE, BASE_FAILURE_RECEIPT_RELATIVE),
        (True, True): (STRICT_REPORT_RELATIVE, STRICT_RECEIPT_RELATIVE),
        (True, False): (STRICT_FAILURE_RELATIVE, STRICT_FAILURE_RECEIPT_RELATIVE),
    }
    report, receipt = choices[strict, passed]
    return destination_name(report), destination_name(receipt)


def full_graph(document: Mapping[str, Any]) -> dict[str, Any]:
    original = original_owner.source_v6._validate_fresh_graph(document)
    families = document.get("families")
    require(isinstance(families, dict), "the complete V23 source audit is missing")
    sources: dict[str, dict[str, str]] = {}
    for family in CORE_FAMILIES:
        row = families.get(family)
        require(isinstance(row, dict), "V23 omitted a genuine engine: " + family)
        public = row.get("python_source")
        native_sources = row.get("native_sources")
        require(isinstance(public, dict) and isinstance(native_sources, list),
                "V23 omitted a family parser/compiler source: " + family)
        actual: dict[str, str] = {}
        for item in [public, *native_sources]:
            require(isinstance(item, dict)
                    and type(item.get("file")) is str
                    and valid_sha256(item.get("sha256"))
                    and item.get("passed") is True
                    and item.get("issues") == [],
                    "a complete owned V23 source failed: " + family)
            actual[item["file"]] = item["sha256"]
        require(tuple(actual) == OWNED_SOURCE_PATHS[family],
                "V23 substituted or reordered an independently owned source")
        sources[family] = actual
    graph = {
        "source_count": original["source_count"],
        "source_paths": list(original["source_paths"]),
        "source_sha256_by_family": sources,
        "native_binary_count": original["native_binary_count"],
        "native_sha256_by_family": copy.deepcopy(
            original["native_sha256_by_family"]
        ),
    }
    require(graph["source_count"] == 12
            and len(graph["source_paths"]) == 12
            and len(set(graph["source_paths"])) == 12
            and graph["native_binary_count"] == 5
            and set(graph["source_sha256_by_family"]) == set(CORE_FAMILIES)
            and set(graph["native_sha256_by_family"]) == set(CORE_FAMILIES)
            and sum(map(len, graph["native_sha256_by_family"].values())) == 5,
            "V23 changed its complete twelve-source/five-native denominator")
    for family in CORE_FAMILIES:
        require(set(graph["native_sha256_by_family"][family])
                == set(OWNED_NATIVE_PATHS[family].values()),
                "V23 accepted cross-family or foreign native FFI: " + family)
    return graph


def read_only_current_graph() -> dict[str, Any]:
    verify_production_runtime()
    source_map: dict[str, dict[str, str]] = {}
    native_map: dict[str, dict[str, str]] = {}
    source_paths: list[str] = []
    for family in CORE_FAMILIES:
        family_sources: dict[str, str] = {}
        for relative in OWNED_SOURCE_PATHS[family]:
            raw = v11.read_regular(ROOT / relative,
                                   "actual current V23 owned source " + relative)
            if relative.endswith(".py"):
                ast.parse(raw.decode("utf-8"), filename=relative)
            family_sources[relative] = hashlib.sha256(raw).hexdigest()
            source_paths.append(relative)
        source_map[family] = family_sources
        family_native: dict[str, str] = {}
        for relative in OWNED_NATIVE_PATHS[family].values():
            raw = v11.read_regular(ROOT / relative,
                                   "actual current V23 owned ELF " + relative)
            require(raw.startswith(b"\x7fELF"),
                    "V23 accepted a foreign or invalid native binary")
            family_native[relative] = hashlib.sha256(raw).hexdigest()
        native_map[family] = family_native
    require(len(source_paths) == 12 and len(set(source_paths)) == 12
            and sum(map(len, native_map.values())) == 5
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "the candidate-free V23 current graph is incomplete or contaminated")
    return {
        "source_count": 12,
        "source_paths": source_paths,
        "source_sha256_by_family": source_map,
        "native_binary_count": 5,
        "native_sha256_by_family": native_map,
    }


def snapshot_current_report() -> tuple[dict[str, Any], dict[str, Any]]:
    verify_production_runtime()
    original_owner.core.ensure_candidate_free()
    with original_owner.source_v5.allow_owned_locale_ctype():
        report = original_owner.core.audit()
    original_owner.core.validate_v3_report(
        report, label="the genuinely fresh complete V23 static source audit"
    )
    graph = full_graph(report)
    require(read_only_current_graph() == graph,
            "the fresh V23 static audit differs from its actual rehashed graph")
    original_owner.core.ensure_candidate_free()
    return report, graph


def validate_native_owner(
    document: Any, family: str, expected_native: Mapping[str, str]
) -> dict[str, Any]:
    require(family in CORE_FAMILIES and isinstance(expected_native, Mapping)
            and set(expected_native) == set(OWNED_NATIVE_PATHS[family].values()),
            "V23 requires one exact independently owned family/FFI graph")
    actual = original_owner.validate_worker(document, family, dict(expected_native))
    v11.validate_owner(original_owner, actual, family, expected_native)
    require(actual.get("schema") == original_owner.SCHEMA + "-native-owner-worker"
            and actual.get("match_repr_checks") == 2
            and actual.get("standard_pickle_check_count") == 16
            and actual.get("standard_pickle_failure_count") == 0
            and actual.get("regex_guard_count") == 13
            and actual.get("native_loader_guard_count") == 5
            and actual.get("persistent_cross_engine_guard") is True
            and actual.get("genuine_matching_executed") is True
            and actual.get("external_regex_packages") == 0
            and actual.get("benchmark_or_timing_executed") is False
            and actual.get("holdout_or_case_fixture_access") is False,
            "V23 accepted a weakened matcher, sentinel, pickle, or FFI guard")
    return actual


def _native_payload(expected_native: Mapping[str, str]) -> str:
    payload = json.dumps(dict(expected_native), ensure_ascii=True,
                         sort_keys=True, separators=(",", ":"))
    require(0 < len(payload.encode("ascii")) <= 16 * 1024,
            "V23 received an invalid actual native-worker argument")
    return payload


def validate_native_worker_transcript(
    transcript: Any,
    record: Mapping[str, Any],
    family: str,
    expected_native: Mapping[str, str],
    *,
    historical: bool = False,
) -> dict[str, Any]:
    require(type(historical) is bool, "V23 needs an exact transcript generation")
    expected_schema = (
        historical_v21.SCHEMA if historical else SCHEMA
    ) + "-actual-native-owner-process"
    require(isinstance(transcript, dict)
            and transcript.get("schema") == expected_schema
            and transcript.get("family") == family
            and transcript.get("candidate_module") == v11.FAMILIES[family]["module"]
            and transcript.get("actual_executable") == str(v11.PINNED_EXECUTABLE)
            and transcript.get("actual_python_flags") == ["-I", "-B"]
            and transcript.get("actual_working_directory") == str(ROOT)
            and transcript.get("native_owner_worker_sha256")
            == original_owner.NATIVE_OWNER_WORKER_SHA256
            and transcript.get("actual_worker_environment") == {
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
                "LC_ALL": "C",
                "PATH": "/usr/bin:/bin",
            }
            and transcript.get("actual_native_argument")
            == _native_payload(expected_native)
            and transcript.get("actual_returncode") == 0
            and transcript.get("production_observations_invented") is False,
            "V23 rejected an invented, foreign, stale, or incomplete owner process")
    stdout = v11.restore_complete_stream(
        transcript.get("actual_original_worker_stdout"),
        "complete genuine V23 original native-owner stdout",
    )
    stderr = v11.restore_complete_stream(
        transcript.get("actual_original_worker_stderr"),
        "complete genuine V23 original native-owner stderr",
    )
    require(0 < len(stdout) <= original_owner.MAX_WORKER_BYTES and stderr == b"",
            "V23 requires the actual complete successful owner process streams")
    decoded = original_owner.core.decode_report(
        stdout, label="complete actual V23 original native-worker stdout"
    )
    require(decoded == record, "V23 substituted the true owner process stdout")
    validate_native_owner(decoded, family, expected_native)
    return transcript


def _decode_worker_output(
    family: str,
    expected_native: Mapping[str, str],
    returncode: int,
    stdout: bytes,
    stderr: bytes,
) -> tuple[dict[str, Any], dict[str, Any]]:
    require(type(returncode) is int and type(stdout) is bytes
            and type(stderr) is bytes and returncode == 0
            and 0 < len(stdout) <= original_owner.MAX_WORKER_BYTES
            and stderr == b"",
            "V23 requires true complete zero-exit original native-worker stdout")
    document = original_owner.core.decode_report(
        stdout, label="actual complete independently executed V23 owner"
    )
    actual = validate_native_owner(document, family, expected_native)
    require(stdout == original_owner.core.canonical(actual) + b"\n",
            "V23 requires the exact complete canonical owner stdout line")
    transcript = {
        "schema": SCHEMA + "-actual-native-owner-process",
        "family": family,
        "candidate_module": v11.FAMILIES[family]["module"],
        "actual_executable": str(v11.PINNED_EXECUTABLE),
        "actual_python_flags": ["-I", "-B"],
        "actual_working_directory": str(ROOT),
        "native_owner_worker_sha256": original_owner.NATIVE_OWNER_WORKER_SHA256,
        "actual_worker_environment": {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "LC_ALL": "C",
            "PATH": "/usr/bin:/bin",
        },
        "actual_native_argument": _native_payload(expected_native),
        "actual_returncode": returncode,
        "actual_original_worker_stdout": v11.observed_stream(stdout, True),
        "actual_original_worker_stderr": v11.observed_stream(stderr, True),
        "production_observations_invented": False,
    }
    validate_native_worker_transcript(transcript, actual, family, expected_native)
    return actual, transcript


def run_native_worker_with_transcript(
    family: str, expected_native: Mapping[str, str]
) -> tuple[dict[str, Any], dict[str, Any]]:
    verify_production_runtime()
    require(family in CORE_FAMILIES
            and set(expected_native) == set(OWNED_NATIVE_PATHS[family].values()),
            "V23 requires the actual same-family complete original owner")
    original_owner.validate_worker_source()
    payload = _native_payload(expected_native)
    environment = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "LC_ALL": "C",
        "PATH": "/usr/bin:/bin",
    }
    try:
        completed = subprocess.run(
            [str(v11.PINNED_EXECUTABLE), "-I", "-B", "-c",
             original_owner.NATIVE_OWNER_WORKER, str(ROOT), family, payload],
            cwd=str(ROOT),
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=120,
        )
    except subprocess.TimeoutExpired as error:
        evidence = original_owner.worker_failure_evidence(
            family, None, error.stdout, error.stderr,
            timed_out=True,
            message="the genuine V23 native owner exceeded its actual timeout",
        )
        raise original_owner.NativeWorkerFailure(evidence["failure_message"], evidence)
    try:
        result = _decode_worker_output(
            family, expected_native, completed.returncode,
            completed.stdout, completed.stderr,
        )
    except (AuditV23Error, original_owner.AuditV10Error,
            original_owner.source_v6.AuditV6Error,
            original_owner.core.AuditV3Error, v11.ProofV11Error,
            UnicodeError, ValueError, TypeError, KeyError) as error:
        evidence = original_owner.worker_failure_evidence(
            family,
            completed.returncode,
            completed.stdout,
            completed.stderr,
            timed_out=False,
            message="the genuine V23 native owner failed: " + str(error),
        )
        evidence["actual_original_worker_stdout"] = v11.observed_stream(
            completed.stdout, True
        )
        evidence["actual_original_worker_stderr"] = v11.observed_stream(
            completed.stderr, True
        )
        evidence["production_observations_invented"] = False
        raise original_owner.NativeWorkerFailure(
            evidence["failure_message"], evidence
        ) from error
    original_owner.core.ensure_candidate_free()
    return result


def _read_pinned_json(
    relative: str, digest: str, label: str, *, byte_count: int | None = None
) -> tuple[dict[str, Any], bytes]:
    raw = v11.authenticate_frozen(relative, digest)
    require(byte_count is None or len(raw) == byte_count,
            "genuine preserved V23 historical bytes changed: " + relative)
    return v11.decode_json(raw, label), raw


def _validate_v15_receipt(receipt: Any) -> dict[str, Any]:
    required_keys = {
        "schema", "path", "expected_payload_sha256", "expected_payload_bytes",
        "actual_file_created", "actual_payload_bytes_written",
        "actual_write_calls", "actual_file_fsync", "actual_directory_fsync",
        "canonical_reread_succeeded", "fully_durable_publication",
    }
    require(isinstance(receipt, dict) and set(receipt) == required_keys
            and receipt.get("schema")
            == "rebar-postfinal-cpython-full-public-locale-v15"
            + "-actual-exclusive-publication-receipt"
            and receipt.get("path") == V15_FAILURE_RELATIVE
            and receipt.get("expected_payload_sha256") == V15_FAILURE_SHA256
            and receipt.get("expected_payload_bytes") == V15_FAILURE_BYTES
            and receipt.get("actual_payload_bytes_written") == V15_FAILURE_BYTES
            and receipt.get("actual_write_calls") == [{
                "requested_bytes": V15_FAILURE_BYTES,
                "returned_bytes": V15_FAILURE_BYTES,
            }]
            and all(receipt.get(name) is True for name in (
                "actual_file_created", "actual_file_fsync",
                "actual_directory_fsync", "canonical_reread_succeeded",
                "fully_durable_publication",
            )),
            "V23 must preserve the actual sole fully durable V15 failure receipt")
    return receipt


def validate_v6_baseline(document: Any) -> dict[str, Any]:
    require(isinstance(document, dict),
            "V23 requires the exact frozen double V6 reference")
    expected = {
        "schema": "rebar-postfinal-cpython-full-public-locale-v6-self-oracle",
        "status": "PASS",
        "synthetic": False,
        "python": "3.14.6",
        "source_path": V6_SOURCE_RELATIVE,
        "source_sha256": V6_SOURCE_SHA256,
        "protocol_path": V6_PROTOCOL_RELATIVE,
        "protocol_sha256": V6_PROTOCOL_SHA256,
        "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
        "all_original_methods": ORIGINAL_METHODS,
        "public_original_methods": PUBLIC_METHODS,
        "private_original_methods": PRIVATE_METHODS,
        "public_method_waivers": [],
        "actual_independent_reference_count": 2,
        "reference_candidate_imports": 0,
        "reference_candidate_audits_read": 0,
        "reference_candidate_proofs_read": 0,
        "reference_holdout_cases_read": 0,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    for key, value in expected.items():
        require(document.get(key) == value,
                "V23 changed a genuine complete V6 matrix or waiver: " + key)
    private_waivers = document.get("named_private_class_waivers")
    require(type(private_waivers) is dict
            and private_waivers == PRIVATE_CLASS_WAIVERS
            and all(type(value) is dict for value in private_waivers.values())
            and sum(value["methods"] for value in private_waivers.values())
            == PRIVATE_METHODS,
            "V23 changed the exact authentic two-class/13-method private-waiver mapping")
    roles = document.get("roles")
    require(type(roles) is dict
            and tuple(roles) == ("reference_a", "reference_b"),
            "V23 replaced the two independent actual V6 baseline roles")
    previous: list[dict[str, Any]] | None = None
    for label in ("reference_a", "reference_b"):
        role = roles[label]
        require(type(role) is dict
                and role.get("role") == "stdlib"
                and role.get("methods") == PUBLIC_METHODS
                and role.get("applicable") == PUBLIC_METHODS - 1
                and role.get("passed") == PUBLIC_METHODS - 1
                and role.get("skipped") == 1
                and role.get("named_private_debug_skips") == 1
                and role.get("unexplained_skips") == 0
                and role.get("failed") == 0
                and role.get("errors") == 0
                and role.get("timeouts") == 0
                and role.get("crashes") == 0
                and role.get("status") == "PASS"
                and role.get("debug_build_coverage") == "NOT RUN"
                and role.get("record_count") == PUBLIC_METHODS
                and type(role.get("records")) is list
                and len(role["records"]) == PUBLIC_METHODS,
                "V23 changed an actual 151-pass/one-skip V6 reference role")
        records = role["records"]
        require(role.get("records_sha256") == digest_value(records),
                "V23 changed the exact full original V6 role-record dictionaries")
        current: list[dict[str, Any]] = []
        named = 0
        for record in records:
            require(type(record) is dict
                    and type(record.get("test")) is str
                    and valid_sha256(record.get("source_ast_sha256")),
                    "V23 changed an original frozen public-method identity")
            identity = record["test"]
            state = record.get("status")
            if identity == PRIVATE_DEBUG_METHOD:
                require(state == "SKIP"
                        and record.get("reason") == PRIVATE_DEBUG_REASON
                        and record.get("skip_kind") == PRIVATE_DEBUG_SKIP_KIND
                        and "classification" not in record
                        and record.get("source_ast_sha256")
                        == PRIVATE_DEBUG_AST_SHA256,
                        "V23 forged the canonical V6 named private-debug waiver")
                named += 1
            else:
                require(state == "PASS" and record.get("skip_kind") is None,
                        "V23 waived an actual original public baseline method")
            current.append({
                "test": identity,
                "source_ast_sha256": record["source_ast_sha256"],
                "status": state,
                "skip_kind": record.get("skip_kind"),
                "reason": record.get("reason"),
            })
        require(named == 1
                and len({item["test"] for item in current}) == PUBLIC_METHODS,
                "V23 changed the genuine unique 152-method reference denominator")
        require(previous is None or previous == current,
                "the two independent V6 original reference vectors disagree")
        previous = current
    require(previous is not None
            and document.get("reference_status_vector_sha256")
            == digest_value(previous),
            "V23 changed the complete original V6 status-vector dictionaries or digest")
    return document


def _validate_v15_history(
    failure: Mapping[str, Any],
    forensic: Mapping[str, Any],
    summary: Mapping[str, Any],
    baseline: Mapping[str, Any],
) -> dict[str, Any]:
    require(failure.get("schema")
            == "rebar-postfinal-cpython-full-public-locale-v15-actual-role-failure"
            and failure.get("status") == "FAIL"
            and failure.get("role") == "rust"
            and failure.get("source_sha256") == V15_SOURCE_SHA256
            and failure.get("protocol_sha256") == V15_PROTOCOL_SHA256
            and failure.get("immutable_v6_reference_sha256") == V6_BASELINE_SHA256
            and failure.get("actual_failure_destination") == V15_FAILURE_RELATIVE
            and failure.get("synthetic") is False
            and failure.get("production_observations_invented") is False,
            "V23 rejected the exact independently frozen V15 upstream failure")
    details = failure.get("details")
    require(isinstance(details, dict)
            and details.get("returncode") == 2
            and details.get("complete_streams_available") is True
            and details.get("production_observations_invented") is False,
            "V23 rejected the real complete V15 process failure")
    stdout = details.get("stdout")
    stderr = details.get("stderr")
    require(isinstance(stdout, dict)
            and stdout.get("encoding") == "hex"
            and stdout.get("bytes") == V15_STDOUT_BYTES
            and stdout.get("sha256") == V15_STDOUT_SHA256
            and stdout.get("truncated") is False
            and type(stdout.get("complete_hex")) is str
            and isinstance(stderr, dict)
            and stderr.get("encoding") == "hex"
            and stderr.get("bytes") == 0
            and stderr.get("sha256") == hashlib.sha256(b"").hexdigest()
            and stderr.get("truncated") is False
            and stderr.get("complete_hex") == "",
            "V23 rejected the actual preserved V15 stdout or empty stderr")
    try:
        raw_stdout = bytes.fromhex(stdout["complete_hex"])
    except ValueError as error:
        raise AuditV23Error("the actual V15 stdout is not complete hex") from error
    require(len(raw_stdout) == V15_STDOUT_BYTES
            and hashlib.sha256(raw_stdout).hexdigest() == V15_STDOUT_SHA256,
            "V23 detected substituted genuine V15 worker stdout")
    actual_worker = v11.decode_json(raw_stdout, "actual complete V15 Rust failure")
    require(actual_worker == details.get("actual_worker_document")
            and actual_worker.get("schema")
            == "rebar-postfinal-cpython-full-public-locale-v15-actual-worker-failure"
            and actual_worker.get("status") == "FAIL"
            and actual_worker.get("role") == "rust",
            "V23 rejected the genuine V15 original worker observation")
    observed = details.get("actual_worker_failure_details")
    require(isinstance(observed, dict)
            and actual_worker.get("details") == observed
            and observed.get("completed_original_method_count") == 152
            and observed.get("actual_native_owner_method_guard_checks") == 304
            and observed.get("actual_cached_matcher_method_guard_checks") == 304
            and observed.get("production_observations_invented") is False,
            "V23 rejected the complete 152-method/304-guard original failure")
    roles = baseline.get("roles")
    validate_v6_baseline(baseline)
    require(isinstance(roles, dict)
            and set(roles) == {"reference_a", "reference_b"},
            "V23 omitted one independently frozen V6 CPython reference")
    reference_role = roles.get("reference_a")
    require(isinstance(reference_role, dict), "V23 lost the actual V6 reference")
    expected_records = reference_role.get("records")
    records = observed.get("completed_original_method_records")
    require(isinstance(records, list) and isinstance(expected_records, list)
            and len(records) == len(expected_records) == 152,
            "V23 changed the complete genuine V15 original method denominator")
    passed = skipped = interference = missing_hook = 0
    for expected, actual in zip(expected_records, records, strict=True):
        require(isinstance(expected, dict) and isinstance(actual, dict)
                and actual.get("test") == expected.get("test")
                and actual.get("source_ast_sha256")
                == expected.get("source_ast_sha256"),
                "V23 changed the actual original method identity or source")
        state = actual.get("status")
        if state == "PASS":
            require(expected.get("status") == "PASS",
                    "V23 falsely passed an original private method")
            passed += 1
        elif state == "SKIP":
            require(expected.get("status") == "SKIP"
                    and actual.get("test") == PRIVATE_DEBUG_METHOD
                    and actual.get("reason") == PRIVATE_DEBUG_REASON
                    and actual.get("skip_kind") == PRIVATE_DEBUG_SKIP_KIND
                    and actual.get("source_ast_sha256") == PRIVATE_DEBUG_AST_SHA256,
                    "V23 forged the one genuine named private-debug waiver")
            skipped += 1
        elif state == "ERROR":
            reason = actual.get("reason")
            require(expected.get("status") == "PASS"
                    and type(reason) is str and bool(reason),
                    "V23 concealed an actual original V15 error")
            if HARNESS_ERROR_MARKER in reason:
                require(actual.get("test") != PICKLING_METHOD,
                        "V23 disguised the missing private hook as harness failure")
                interference += 1
            else:
                require(actual.get("test") == PICKLING_METHOD
                        and PICKLING_ERROR in reason,
                        "V23 concealed an unexplained original V15 candidate error")
                missing_hook += 1
        else:
            raise AuditV23Error("V23 changed a genuine original method status")
    require((passed, interference, missing_hook, skipped) == (139, 11, 1, 1),
            "V23 changed the actual V15 139/11/1/1 failure denominator")
    require(forensic.get("schema")
            == "rebar-root-v15-genuine-rust-original-suite-read-only-failure-forensic"
            and forensic.get("status") == "PASS"
            and forensic.get("source_sha256") == V15_SOURCE_SHA256
            and forensic.get("protocol_sha256") == V15_PROTOCOL_SHA256
            and forensic.get("actual_candidate_result") == "FAIL"
            and forensic.get("actual_failure_path") == V15_FAILURE_RELATIVE
            and forensic.get("actual_failure_sha256") == V15_FAILURE_SHA256
            and forensic.get("actual_failure_bytes") == V15_FAILURE_BYTES
            and forensic.get("original_method_denominator") == 152
            and forensic.get("actual_original_methods_completed") == 152
            and forensic.get("actual_passing_original_methods") == 139
            and forensic.get("actual_error_original_methods") == 12
            and forensic.get("actual_harness_interference_errors") == 11
            and forensic.get("actual_required_original_test_candidate_gaps") == 1
            and forensic.get("actual_named_private_debug_skips") == 1
            and forensic.get("authentic_named_private_debug_skip_kind")
            == PRIVATE_DEBUG_SKIP_KIND
            and forensic.get("actual_native_owner_method_guard_checks") == 304
            and forensic.get("actual_cached_matcher_method_guard_checks") == 304
            and forensic.get("actual_worker_returncode") == 2
            and forensic.get("actual_worker_stdout_bytes") == V15_STDOUT_BYTES
            and forensic.get("actual_worker_stdout_sha256") == V15_STDOUT_SHA256
            and forensic.get("actual_worker_stdout_completely_preserved_inside_failure")
            is True
            and forensic.get("historical_failure_qualifies_current_engine") is False
            and forensic.get("production_observations_invented") is False,
            "V23 rejected the genuine read-only V15 Rust forensic")
    boundary = forensic.get("read_only_boundary_effects")
    require(isinstance(boundary, dict)
            and set(boundary) == {
                "native_workers_started", "subprocesses_started",
                "candidate_imports", "filesystem_writes", "clock_samples",
            }
            and all(value == 0 for value in boundary.values()),
            "V23 accepted a V15 forensic with real production side effects")
    require(summary.get("schema")
            == "rebar-root-v15-rust-actual-complete-original-suite-production-summary"
            and summary.get("status") == "FAIL"
            and summary.get("role") == "rust"
            and summary.get("source_sha256") == V15_SOURCE_SHA256
            and summary.get("protocol_sha256") == V15_PROTOCOL_SHA256
            and summary.get("actual_failure_path") == V15_FAILURE_RELATIVE
            and summary.get("actual_failure_sha256") == V15_FAILURE_SHA256
            and summary.get("actual_failure_bytes") == V15_FAILURE_BYTES
            and summary.get("actual_controller_returncode") == 2
            and summary.get("actual_original_method_denominator") == 152
            and summary.get("actual_original_methods_completed") == 152
            and summary.get("actual_passing_original_methods") == 139
            and summary.get("actual_error_original_methods") == 12
            and summary.get("actual_harness_interference_errors") == 11
            and summary.get("actual_required_original_test_candidate_gaps") == 1
            and summary.get("actual_named_private_debug_skips") == 1
            and summary.get("actual_native_owner_method_guard_checks") == 304
            and summary.get("actual_cached_matcher_method_guard_checks") == 304
            and summary.get("actual_complete_original_worker_stdout_bytes")
            == V15_STDOUT_BYTES
            and summary.get("actual_complete_original_worker_stdout_sha256")
            == V15_STDOUT_SHA256
            and summary.get("actual_complete_original_worker_stdout_preserved_inside_failure")
            is True
            and summary.get("actual_read_only_failure_forensic_path")
            == V15_FORENSIC_RELATIVE
            and summary.get("actual_read_only_failure_forensic_sha256")
            == V15_FORENSIC_SHA256
            and summary.get("full_original_suite_candidate_qualified") is False
            and summary.get("production_observations_invented") is False,
            "V23 rejected the actual immutable V15 production failure summary")
    receipt = _validate_v15_receipt(
        forensic.get("actual_exclusive_publication_receipt")
    )
    require(receipt == summary.get("actual_failure_publication_receipt"),
            "V23 substituted the once-only preserved V15 publication receipt")
    return {
        "failure_path": V15_FAILURE_RELATIVE,
        "failure_sha256": V15_FAILURE_SHA256,
        "failure_bytes": V15_FAILURE_BYTES,
        "forensic_path": V15_FORENSIC_RELATIVE,
        "forensic_sha256": V15_FORENSIC_SHA256,
        "production_summary_path": V15_SUMMARY_RELATIVE,
        "production_summary_sha256": V15_SUMMARY_SHA256,
        "original_method_denominator": 152,
        "passing_original_methods": passed,
        "harness_interference_errors": interference,
        "missing_private_compile_errors": missing_hook,
        "named_private_debug_skips": skipped,
        "native_owner_method_guard_checks": 304,
        "cached_matcher_method_guard_checks": 304,
        "actual_worker_returncode": 2,
        "actual_worker_stdout_sha256": V15_STDOUT_SHA256,
        "actual_worker_stdout_bytes": V15_STDOUT_BYTES,
        "actual_exclusive_publication_receipt": copy.deepcopy(receipt),
        "historical_failure_qualifies_current_engine": False,
        "production_observations_invented": False,
    }


def _validate_historical_v21_document(
    document: Any, digest: str, *, strict: bool
) -> dict[str, Any]:
    require(valid_sha256(digest) and isinstance(document, dict)
            and hashlib.sha256(canonical(document)).hexdigest() == digest,
            "V23 requires exact independently supplied canonical V21 history")
    schema = historical_v21.STRICT_SCHEMA if strict else historical_v21.BASE_SCHEMA
    require(document.get("schema") == schema
            and document.get("postfinal_schema") == schema
            and document.get("status") == "PASS"
            and document.get("result") == "PASS"
            and document.get("passed") is True
            and document.get("audit_source_path") == historical_v21.SOURCE_RELATIVE
            and document.get("audit_source_sha256") == HISTORICAL_V21_SOURCE_SHA256
            and document.get("audit_protocol_path")
            == historical_v21.PROTOCOL_RELATIVE
            and document.get("audit_protocol_sha256")
            == HISTORICAL_V21_PROTOCOL_SHA256
            and document.get("verified_core_family_count") == 3
            and document.get("verified_candidate_source_count") == 12
            and document.get("verified_native_role_count") == 5
            and document.get("completed_native_owner_worker_count") == 3
            and document.get("actual_native_owner_worker_failure") is None
            and document.get("complete_actual_native_owner_streams_preserved") is True
            and document.get("historical_v10_graph_qualifies_current_engine") is False,
            "V23 rejected a forged, failing, or incorrectly qualified V21 archive")
    graph = full_graph(document)
    require(document.get("verified_candidate_source_paths") == graph["source_paths"]
            and document.get("source_sha256_by_family")
            == graph["source_sha256_by_family"]
            and document.get("native_sha256_by_family")
            == graph["native_sha256_by_family"],
            "the immutable V21 report changed its own historical source/ELF graph")
    workers = document.get("actual_native_owner_workers")
    transcripts = document.get("actual_native_owner_processes")
    require(isinstance(workers, dict) and isinstance(transcripts, dict)
            and set(workers) == set(transcripts) == set(CORE_FAMILIES),
            "a genuine V21 historical native process was omitted")
    for family in CORE_FAMILIES:
        validate_native_worker_transcript(
            transcripts[family], workers[family], family,
            graph["native_sha256_by_family"][family], historical=True,
        )
    historical_v21.validate_preserved_history(
        document.get("preserved_immutable_history")
    )
    return graph


def validate_preserved_history(document: Any) -> dict[str, Any]:
    require(isinstance(document, dict), "V23 omitted real immutable prior evidence")
    require(valid_sha256(document.get("historical_v21_base_report_sha256"))
            and valid_sha256(document.get("historical_v21_strict_report_sha256"))
            and document["historical_v21_base_report_sha256"]
            != document["historical_v21_strict_report_sha256"]
            and document.get("historical_v21_base_report_path")
            == historical_v21.BASE_REPORT_RELATIVE
            and document.get("historical_v21_strict_report_path")
            == historical_v21.STRICT_REPORT_RELATIVE
            and document.get("historical_v21_source_sha256")
            == HISTORICAL_V21_SOURCE_SHA256
            and document.get("historical_v21_protocol_sha256")
            == HISTORICAL_V21_PROTOCOL_SHA256
            and document.get("historical_v21_graph_qualifies_current_engine") is False
            and document.get("historical_failure_qualifies_current_engine") is False
            and document.get("historical_v5_baseline_sha256")
            == v11.BASELINE_SHA256
            and document.get("historical_v5_baseline_path")
            == v11.BASELINE_RELATIVE
            and document.get("historical_v6_baseline_sha256") == V6_BASELINE_SHA256
            and document.get("historical_v6_baseline_path") == V6_BASELINE_RELATIVE
            and document.get("original_method_count") == ORIGINAL_METHODS
            and document.get("original_public_method_count") == PUBLIC_METHODS
            and document.get("original_private_method_count") == PRIVATE_METHODS
            and document.get("public_method_waiver_count") == 0
            and document.get("named_private_class_waiver_count") == 2
            and document.get("named_private_debug_skip_kind")
            == PRIVATE_DEBUG_SKIP_KIND
            and document.get("preserved_v15_ownership_failure_path")
            == V15_OWNERSHIP_FAILURE_RELATIVE
            and document.get("preserved_v15_ownership_failure_sha256")
            == V15_OWNERSHIP_FAILURE_SHA256
            and document.get("production_observations_invented") is False,
            "V23 forged or qualified an immutable historical source/report graph")
    archived_history = historical_v21.validate_preserved_history(
        document.get("preserved_v21_immutable_history")
    )
    archived_owner_failure = historical_v21.validate_v15_first_failure_summary(
        archived_history.get("preserved_v15_first_audit_failure")
    )
    require(archived_owner_failure.get("failure_path")
            == V15_OWNERSHIP_FAILURE_RELATIVE
            and archived_owner_failure.get("failure_sha256")
            == V15_OWNERSHIP_FAILURE_SHA256
            and archived_owner_failure.get("failure_sha256") != V15_FAILURE_SHA256,
            "V23 confused the genuine V15 ownership incident with the upstream failure")
    failure = document.get("preserved_v15_original_failure")
    require(isinstance(failure, dict)
            and failure.get("failure_path") == V15_FAILURE_RELATIVE
            and failure.get("failure_sha256") == V15_FAILURE_SHA256
            and failure.get("failure_bytes") == V15_FAILURE_BYTES
            and failure.get("forensic_path") == V15_FORENSIC_RELATIVE
            and failure.get("forensic_sha256") == V15_FORENSIC_SHA256
            and failure.get("production_summary_path") == V15_SUMMARY_RELATIVE
            and failure.get("production_summary_sha256") == V15_SUMMARY_SHA256
            and failure.get("original_method_denominator") == 152
            and failure.get("passing_original_methods") == 139
            and failure.get("harness_interference_errors") == 11
            and failure.get("missing_private_compile_errors") == 1
            and failure.get("named_private_debug_skips") == 1
            and failure.get("native_owner_method_guard_checks") == 304
            and failure.get("cached_matcher_method_guard_checks") == 304
            and failure.get("actual_worker_returncode") == 2
            and failure.get("actual_worker_stdout_sha256") == V15_STDOUT_SHA256
            and failure.get("actual_worker_stdout_bytes") == V15_STDOUT_BYTES
            and failure.get("historical_failure_qualifies_current_engine") is False
            and failure.get("production_observations_invented") is False,
            "V23 concealed or rewrote the actual 139/11/1/1 V15 failure")
    _validate_v15_receipt(failure.get("actual_exclusive_publication_receipt"))
    return document


def authenticate_historical_evidence(
    historical_base_sha256: str, historical_strict_sha256: str
) -> dict[str, Any]:
    verify_production_runtime()
    require(valid_sha256(historical_base_sha256)
            and valid_sha256(historical_strict_sha256)
            and historical_base_sha256 != historical_strict_sha256,
            "V23 requires two distinct externally supplied historical V21 pins")
    base, base_raw = _read_pinned_json(
        historical_v21.BASE_REPORT_RELATIVE,
        historical_base_sha256,
        "genuine immutable historical V21 base",
    )
    strict, strict_raw = _read_pinned_json(
        historical_v21.STRICT_REPORT_RELATIVE,
        historical_strict_sha256,
        "genuine immutable historical V21 strict report",
    )
    require(canonical(base) == base_raw and canonical(strict) == strict_raw,
            "V23 refuses to normalize or rewrite genuine old V21 report bytes")
    old_base_graph = _validate_historical_v21_document(
        base, historical_base_sha256, strict=False
    )
    old_strict_graph = _validate_historical_v21_document(
        strict, historical_strict_sha256, strict=True
    )
    require(old_base_graph == old_strict_graph
            and strict.get("strict_base_report_path")
            == historical_v21.BASE_REPORT_RELATIVE
            and strict.get("strict_base_report_sha256") == historical_base_sha256
            and strict.get("independent_base_native_owner_workers")
            == base.get("actual_native_owner_workers")
            and strict.get("preserved_immutable_history")
            == base.get("preserved_immutable_history"),
            "V23 rejected internally inconsistent immutable V21 history")
    archived = historical_v21.authenticate_historical_audits()
    require(archived == base.get("preserved_immutable_history"),
            "V23 lost an actual historical ownership incident or baseline proof")
    v5, _ = _read_pinned_json(
        v11.BASELINE_RELATIVE, v11.BASELINE_SHA256,
        "genuine independent historical V5 CPython baseline",
    )
    v11.validate_official_baseline(v5)
    v6, _ = _read_pinned_json(
        V6_BASELINE_RELATIVE, V6_BASELINE_SHA256,
        "genuine independent historical V6 CPython baseline",
    )
    validate_v6_baseline(v6)
    failure, _ = _read_pinned_json(
        V15_FAILURE_RELATIVE, V15_FAILURE_SHA256,
        "actual immutable complete V15 Rust upstream failure",
        byte_count=V15_FAILURE_BYTES,
    )
    forensic, _ = _read_pinned_json(
        V15_FORENSIC_RELATIVE, V15_FORENSIC_SHA256,
        "actual immutable read-only V15 Rust failure forensic",
    )
    summary, _ = _read_pinned_json(
        V15_SUMMARY_RELATIVE, V15_SUMMARY_SHA256,
        "actual immutable V15 Rust production failure summary",
    )
    actual_failure = _validate_v15_history(failure, forensic, summary, v6)
    result = {
        "historical_v21_base_report_path": historical_v21.BASE_REPORT_RELATIVE,
        "historical_v21_base_report_sha256": historical_base_sha256,
        "historical_v21_strict_report_path": historical_v21.STRICT_REPORT_RELATIVE,
        "historical_v21_strict_report_sha256": historical_strict_sha256,
        "historical_v21_source_sha256": HISTORICAL_V21_SOURCE_SHA256,
        "historical_v21_protocol_sha256": HISTORICAL_V21_PROTOCOL_SHA256,
        "historical_v21_graph_qualifies_current_engine": False,
        "historical_failure_qualifies_current_engine": False,
        "historical_v5_baseline_path": v11.BASELINE_RELATIVE,
        "historical_v5_baseline_sha256": v11.BASELINE_SHA256,
        "historical_v6_baseline_path": V6_BASELINE_RELATIVE,
        "historical_v6_baseline_sha256": V6_BASELINE_SHA256,
        "original_method_count": ORIGINAL_METHODS,
        "original_public_method_count": PUBLIC_METHODS,
        "original_private_method_count": PRIVATE_METHODS,
        "public_method_waiver_count": 0,
        "named_private_class_waiver_count": 2,
        "named_private_debug_skip_kind": PRIVATE_DEBUG_SKIP_KIND,
        "preserved_v15_ownership_failure_path": V15_OWNERSHIP_FAILURE_RELATIVE,
        "preserved_v15_ownership_failure_sha256": V15_OWNERSHIP_FAILURE_SHA256,
        "preserved_v21_immutable_history": copy.deepcopy(archived),
        "preserved_v15_original_failure": actual_failure,
        "production_observations_invented": False,
    }
    return validate_preserved_history(result)


def summarize_controls(document: Mapping[str, Any]) -> dict[str, Any]:
    require(isinstance(document, Mapping)
            and document.get("schema") == SCHEMA + "-self-test"
            and document.get("status") == "PASS"
            and document.get("passed") is True
            and type(document.get("check_count")) is int
            and document["check_count"] >= 150
            and all(document.get(key) == 0 for key in (
                "candidate_imports", "subprocesses", "file_reads", "file_writes",
                "clock_samples", "historical_evidence_reads",
                "actual_audit_report_reads", "holdout_reads",
            ))
            and document.get("synthetic_results_qualify_candidates") is False,
            "V23 requires genuine candidate-free, evidence-free source controls")
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS",
        "passed": True,
        "check_count": document["check_count"],
        **{key: 0 for key in (
            "candidate_imports", "subprocesses", "file_reads", "file_writes",
            "clock_samples", "historical_evidence_reads",
            "actual_audit_report_reads", "holdout_reads",
        )},
        "synthetic_results_qualify_candidates": False,
    }


def _require_same_graph(actual: Mapping[str, Any], expected: Mapping[str, Any]) -> None:
    require(isinstance(actual, Mapping) and isinstance(expected, Mapping)
            and actual == expected and actual.get("source_count") == 12
            and actual.get("native_binary_count") == 5,
            "an exact independently rehashed current V23 source or ELF changed")


def build_report(
    current: Mapping[str, Any],
    graph: Mapping[str, Any],
    history: Mapping[str, Any],
    controls: Mapping[str, Any],
    controller: Mapping[str, str],
    *,
    strict: bool,
    workers: Mapping[str, Mapping[str, Any]],
    transcripts: Mapping[str, Mapping[str, Any]],
    failure: Mapping[str, Any] | None,
    base_document: Mapping[str, Any] | None = None,
    base_digest: str | None = None,
) -> dict[str, Any]:
    require(isinstance(current, Mapping) and isinstance(graph, Mapping)
            and isinstance(workers, Mapping) and isinstance(transcripts, Mapping)
            and type(strict) is bool,
            "V23 requires genuine static, owner, and process observations")
    passed = failure is None and set(workers) == set(CORE_FAMILIES)
    require(set(transcripts) == set(workers),
            "V23 lost an actual observed owner process")
    schema = STRICT_SCHEMA if strict else BASE_SCHEMA
    report_path, receipt_path = mode_destinations(strict, passed)
    result = dict(current)
    result.update({
        "schema": schema,
        "postfinal_schema": schema,
        "status": "PASS" if passed else "FAIL",
        "result": "PASS" if passed else "FAIL",
        "passed": passed,
        "audit_source_path": SOURCE_RELATIVE,
        "audit_source_sha256": controller["source_sha256"],
        "audit_protocol_path": PROTOCOL_RELATIVE,
        "audit_protocol_sha256": PROTOCOL_SHA256,
        "v10_native_owner_source_path": original_owner.SOURCE_RELATIVE,
        "v10_native_owner_source_sha256": historical_v21.V10_OWNER_SOURCE_SHA256,
        "v10_no_delegation_source_path": original_strict.SOURCE_RELATIVE,
        "v10_no_delegation_source_sha256": historical_v21.V10_STRICT_SOURCE_SHA256,
        "native_owner_worker_sha256": original_owner.NATIVE_OWNER_WORKER_SHA256,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": 12,
        "verified_candidate_source_paths": list(graph["source_paths"]),
        "source_sha256_by_family": copy.deepcopy(graph["source_sha256_by_family"]),
        "verified_native_role_count": 5,
        "native_sha256_by_family": copy.deepcopy(graph["native_sha256_by_family"]),
        "actual_native_owner_workers": copy.deepcopy(dict(workers)),
        "actual_native_owner_processes": copy.deepcopy(dict(transcripts)),
        "complete_actual_native_owner_streams_preserved": True,
        "actual_native_owner_worker_failure": copy.deepcopy(dict(failure))
        if failure is not None else None,
        "completed_native_owner_worker_count": len(workers),
        "unstarted_native_owner_families": [
            family for family in CORE_FAMILIES
            if family not in workers
            and (failure is None or family != failure.get("family"))
        ],
        "verified_match_repr_checks": sum(
            record.get("match_repr_checks", 0) for record in workers.values()
        ),
        "verified_standard_pickle_count": sum(
            record.get("standard_pickle_check_count", 0)
            for record in workers.values()
        ),
        "standard_pickle_failure_count": sum(
            record.get("standard_pickle_failure_count", 0)
            for record in workers.values()
        ),
        "genuine_python_matching_guards_per_family": 13,
        "genuine_native_loader_guards_per_family": 5,
        "preserved_immutable_history": copy.deepcopy(dict(history)),
        "historical_v21_graph_qualifies_current_engine": False,
        "historical_failure_qualifies_current_engine": False,
        "postfinal_wrapper_self_test": summarize_controls(controls),
        "strict_base_report_path": BASE_REPORT_RELATIVE if strict else None,
        "strict_base_report_sha256": base_digest if strict else None,
        "independent_base_native_owner_workers": copy.deepcopy(
            base_document.get("actual_native_owner_workers")
        ) if strict and base_document is not None else None,
        "postfinal_scope": {
            "append_only": True,
            "exclusive_report_path": report_path,
            "exclusive_receipt_path": receipt_path,
            "separate_pass_and_failure_destinations": True,
            "actual_current_native_binary_count": 5,
            "exact_current_owned_candidate_source_count": 12,
            "actual_python_matching_guards_per_family": 13,
            "actual_native_loader_guards_per_family": 5,
            "exact_stage07_sentinel_checked_before_and_after": True,
            "all_cached_matcher_descendants_poisoned_before_and_after": True,
            "original_stage07_cached_alias_helper_used": True,
            "persistent_cross_family_import_and_loader_guards": True,
            "mapped_binaries_hashed_against_static_elf": True,
            "historical_v21_graph_qualifies_current_graph": False,
            "historical_v15_failure_qualifies_current_graph": False,
            "base_report_hash_supplied_externally": strict,
            "independently_executed_native_owner_workers": len(workers)
            + int(failure is not None and failure.get("family") not in workers),
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
        "production_observations_invented": False,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    })
    if passed:
        digest = hashlib.sha256(canonical(result)).hexdigest()
        validate_report(result, digest, strict=strict, base_digest=base_digest)
    return result


def validate_report(
    document: Any,
    digest: str,
    *,
    strict: bool,
    base_digest: str | None = None,
) -> dict[str, Any]:
    require(type(strict) is bool and valid_sha256(digest)
            and isinstance(document, dict)
            and hashlib.sha256(canonical(document)).hexdigest() == digest,
            "V23 requires exact actual canonical current report bytes")
    schema = STRICT_SCHEMA if strict else BASE_SCHEMA
    expected = {
        "schema": schema,
        "postfinal_schema": schema,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "audit_source_path": SOURCE_RELATIVE,
        "audit_protocol_path": PROTOCOL_RELATIVE,
        "audit_protocol_sha256": PROTOCOL_SHA256,
        "v10_native_owner_source_path": original_owner.SOURCE_RELATIVE,
        "v10_native_owner_source_sha256": historical_v21.V10_OWNER_SOURCE_SHA256,
        "v10_no_delegation_source_path": original_strict.SOURCE_RELATIVE,
        "v10_no_delegation_source_sha256": historical_v21.V10_STRICT_SOURCE_SHA256,
        "native_owner_worker_sha256": original_owner.NATIVE_OWNER_WORKER_SHA256,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": 12,
        "verified_native_role_count": 5,
        "completed_native_owner_worker_count": 3,
        "complete_actual_native_owner_streams_preserved": True,
        "actual_native_owner_worker_failure": None,
        "verified_match_repr_checks": 6,
        "verified_standard_pickle_count": 48,
        "standard_pickle_failure_count": 0,
        "genuine_python_matching_guards_per_family": 13,
        "genuine_native_loader_guards_per_family": 5,
        "historical_v21_graph_qualifies_current_engine": False,
        "historical_failure_qualifies_current_engine": False,
        "production_observations_invented": False,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    for key, value in expected.items():
        require(document.get(key) == value,
                "a complete independently executed V23 report changed: " + key)
    require(valid_sha256(document.get("audit_source_sha256")),
            "V23 must record, not predict, its actual frozen source hash")
    graph = full_graph(document)
    require(document.get("verified_candidate_source_paths") == graph["source_paths"]
            and document.get("source_sha256_by_family")
            == graph["source_sha256_by_family"]
            and document.get("native_sha256_by_family")
            == graph["native_sha256_by_family"],
            "V23 substituted its actual twelve-source/five-native current graph")
    workers = document.get("actual_native_owner_workers")
    processes = document.get("actual_native_owner_processes")
    require(isinstance(workers, dict) and isinstance(processes, dict)
            and set(workers) == set(processes) == set(CORE_FAMILIES),
            "V23 lost a genuinely independently executed native family")
    for family in CORE_FAMILIES:
        validate_native_worker_transcript(
            processes[family], workers[family], family,
            graph["native_sha256_by_family"][family],
        )
    validate_preserved_history(document.get("preserved_immutable_history"))
    summarize_controls(document.get("postfinal_wrapper_self_test"))
    report_path, receipt_path = mode_destinations(strict, True)
    scope = document.get("postfinal_scope")
    require(isinstance(scope, dict)
            and scope.get("append_only") is True
            and scope.get("exclusive_report_path") == report_path
            and scope.get("exclusive_receipt_path") == receipt_path
            and scope.get("separate_pass_and_failure_destinations") is True
            and scope.get("actual_current_native_binary_count") == 5
            and scope.get("exact_current_owned_candidate_source_count") == 12
            and scope.get("actual_python_matching_guards_per_family") == 13
            and scope.get("actual_native_loader_guards_per_family") == 5
            and scope.get("exact_stage07_sentinel_checked_before_and_after") is True
            and scope.get("all_cached_matcher_descendants_poisoned_before_and_after")
            is True
            and scope.get("original_stage07_cached_alias_helper_used") is True
            and scope.get("persistent_cross_family_import_and_loader_guards")
            is True
            and scope.get("mapped_binaries_hashed_against_static_elf") is True
            and scope.get("historical_v21_graph_qualifies_current_graph") is False
            and scope.get("historical_v15_failure_qualifies_current_graph") is False
            and scope.get("base_report_hash_supplied_externally") is strict
            and scope.get("independently_executed_native_owner_workers") == 3
            and scope.get("benchmark_or_timing_executed") is False
            and scope.get("holdout_or_case_fixture_access") is False,
            "V23 lost its current guard, graph, history, or exclusive-output scope")
    if strict:
        require(valid_sha256(base_digest) and base_digest != digest
                and document.get("strict_base_report_path") == BASE_REPORT_RELATIVE
                and document.get("strict_base_report_sha256") == base_digest,
                "V23 strict audit requires the real externally supplied base SHA")
        prior = document.get("independent_base_native_owner_workers")
        require(isinstance(prior, dict) and set(prior) == set(CORE_FAMILIES),
                "V23 strict audit lost the genuine independently observed base")
        for family in CORE_FAMILIES:
            validate_native_owner(
                prior[family], family, graph["native_sha256_by_family"][family]
            )
    else:
        require(base_digest is None
                and document.get("strict_base_report_path") is None
                and document.get("strict_base_report_sha256") is None
                and document.get("independent_base_native_owner_workers") is None,
                "V23 base falsely predicted a future strict report or digest")
    return graph


def validate_descriptor_lifetimes(
    receipt: Mapping[str, Any], *, complete: bool
) -> list[dict[str, Any]]:
    require(isinstance(receipt, Mapping) and type(complete) is bool,
            "V23 requires an exact actual descriptor-lifetime receipt")
    events = receipt.get("actual_descriptor_events")
    closures = receipt.get("actual_close_observations")
    require(type(events) is list and type(closures) is list,
            "V23 omitted actual descriptor-open or close observations")
    active: dict[int, str] = {}
    opened_roles: set[str] = set()
    failed_descriptors: set[int] = set()
    observed_closures: list[dict[str, Any]] = []
    for event in events:
        require(type(event) is dict
                and event.get("operation") in ("open", "close")
                and event.get("role") in ("parent", "writer", "reader")
                and type(event.get("descriptor")) is int
                and event["descriptor"] >= 0
                and event.get("status") in ("PASS", "FAIL"),
                "V23 forged an actual descriptor lifetime event")
        role = event["role"]
        descriptor = event["descriptor"]
        if event["operation"] == "open":
            require(set(event) == {"operation", "role", "descriptor", "status"}
                    and event["status"] == "PASS"
                    and descriptor not in active
                    and descriptor not in failed_descriptors
                    and role not in opened_roles,
                    "V23 reused a live, failed-close, or previously opened descriptor role")
            active[descriptor] = role
            opened_roles.add(role)
            continue
        require(descriptor in active and active[descriptor] == role,
                "V23 repeated a consumed descriptor close or forged its live role")
        del active[descriptor]
        close = {key: value for key, value in event.items()
                 if key != "operation"}
        if close["status"] == "PASS":
            require(set(close) == {"role", "descriptor", "status"},
                    "V23 forged a successful actual descriptor close")
        else:
            require(type(close.get("actual_error_type")) is str
                    and type(close.get("actual_error_message")) is str
                    and close.get("stage") == role + "-close",
                    "V23 hid a genuine failed descriptor-close observation")
            failed_descriptors.add(descriptor)
        observed_closures.append(close)
    require(observed_closures == closures and not active,
            "V23 lost an actual descriptor close or left a descriptor live")
    if complete:
        require(
            [(event["operation"], event["role"]) for event in events]
            == [
                ("open", "parent"),
                ("open", "writer"),
                ("close", "writer"),
                ("open", "reader"),
                ("close", "reader"),
                ("close", "parent"),
            ]
            and all(event["status"] == "PASS" for event in events),
            "V23 returned PASS before six genuine ordered descriptor lifetime events",
        )
    return events


def validate_publication_receipt(
    receipt: Any, relative: str, digest: str, expected_bytes: int
) -> dict[str, Any]:
    destination_name(relative)
    require(isinstance(receipt, dict) and valid_sha256(digest)
            and type(expected_bytes) is int and 0 < expected_bytes <= MAX_REPORT_BYTES,
            "V23 requires a complete bounded actual syscall receipt")
    expected = {
        "schema": SCHEMA + "-actual-exclusive-publication-receipt",
        "status": "PASS",
        "report_path": relative,
        "report_sha256": digest,
        "expected_bytes": expected_bytes,
        "actual_bytes_written": expected_bytes,
        "exclusive_create_succeeded": True,
        "file_fsync_succeeded": True,
        "writer_close_succeeded": True,
        "parent_directory_fsync_succeeded": True,
        "canonical_reread_succeeded": True,
        "reader_close_succeeded": True,
        "parent_directory_close_succeeded": True,
        "actual_primary_failure": None,
        "actual_cleanup_failures": [],
        "production_observations_invented": False,
    }
    for key, value in expected.items():
        require(receipt.get(key) == value,
                "V23 rejected an invented actual publication transition: " + key)
    parent_flags = receipt.get("actual_parent_open_flags")
    create_flags = receipt.get("actual_create_open_flags")
    reread_flags = receipt.get("actual_reread_open_flags")
    require(type(parent_flags) is int and type(create_flags) is int
            and type(reread_flags) is int
            and bool(create_flags & os.O_EXCL)
            and bool(create_flags & os.O_CREAT)
            and bool(create_flags & os.O_WRONLY)
            and (not hasattr(os, "O_NOFOLLOW")
                 or all(flags & os.O_NOFOLLOW
                        for flags in (parent_flags, create_flags, reread_flags)))
            and (not hasattr(os, "O_DIRECTORY")
                 or bool(parent_flags & os.O_DIRECTORY)),
            "V23 rejected missing exclusive, directory, or no-follow flags")
    calls = receipt.get("actual_write_calls")
    require(isinstance(calls, list) and bool(calls),
            "V23 lost a real exclusive-publication write syscall")
    remaining = expected_bytes
    for call in calls:
        require(isinstance(call, dict)
                and set(call) == {"requested_bytes", "returned_bytes"}
                and type(call.get("requested_bytes")) is int
                and call.get("requested_bytes") == remaining
                and type(call.get("returned_bytes")) is int
                and 0 < call["returned_bytes"] <= remaining,
                "V23 forged an actual partial-write continuation")
        remaining -= call["returned_bytes"]
    require(remaining == 0, "V23 omitted actual complete publication bytes")
    closures = receipt.get("actual_close_observations")
    require(type(closures) is list and len(closures) == 3
            and [row.get("role") for row in closures]
            == ["writer", "reader", "parent"]
            and all(type(row) is dict
                    and set(row) == {"role", "descriptor", "status"}
                    and type(row.get("descriptor")) is int
                    and row.get("status") == "PASS"
                    for row in closures),
            "V23 returned PASS before three independently observed descriptor closes")
    validate_descriptor_lifetimes(receipt, complete=True)
    return receipt


def _exclusive_publish(
    relative: str, payload: bytes, *, operations: Any = os
) -> dict[str, Any]:
    relative = destination_name(relative)
    require(type(payload) is bytes and 0 < len(payload) <= MAX_REPORT_BYTES,
            "V23 can publish only complete bounded actual evidence bytes")
    parent = ROOT / "candidates/audits"
    target = ROOT / relative
    require(target.parent == parent, "a V23 output changed its genuine audit parent")
    parent_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    parent_flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    create_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    create_flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    reread_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    reread_flags |= getattr(os, "O_NOFOLLOW", 0)
    digest = hashlib.sha256(payload).hexdigest()
    receipt: dict[str, Any] = {
        "schema": SCHEMA + "-actual-exclusive-publication-receipt",
        "status": "NOT COMPLETED",
        "report_path": relative,
        "report_sha256": digest,
        "expected_bytes": len(payload),
        "actual_bytes_written": 0,
        "actual_write_calls": [],
        "actual_parent_open_flags": parent_flags,
        "actual_create_open_flags": create_flags,
        "actual_reread_open_flags": reread_flags,
        "exclusive_create_succeeded": False,
        "file_fsync_succeeded": False,
        "writer_close_succeeded": False,
        "parent_directory_fsync_succeeded": False,
        "canonical_reread_succeeded": False,
        "reader_close_succeeded": False,
        "parent_directory_close_succeeded": False,
        "actual_descriptor_events": [],
        "actual_close_observations": [],
        "actual_primary_failure": None,
        "actual_cleanup_failures": [],
        "production_observations_invented": False,
    }
    descriptors: dict[str, int] = {}
    phase = "parent-open"

    def observe_open(role: str, descriptor: Any) -> int:
        require(role in ("parent", "writer", "reader")
                and type(descriptor) is int and descriptor >= 0
                and role not in descriptors
                and descriptor not in descriptors.values(),
                "V23 received a foreign or simultaneously live descriptor alias")
        descriptors[role] = descriptor
        receipt["actual_descriptor_events"].append({
            "operation": "open",
            "role": role,
            "descriptor": descriptor,
            "status": "PASS",
        })
        return descriptor

    def observe_error(error: BaseException, stage: str) -> dict[str, Any]:
        observed = {
            "stage": stage,
            "actual_error_type": type(error).__name__,
            "actual_error_message": str(error),
        }
        if isinstance(error, OSError):
            observed["actual_errno"] = error.errno
        return observed

    def close_once(role: str) -> None:
        descriptor = descriptors.pop(role)
        row: dict[str, Any] = {
            "role": role,
            "descriptor": descriptor,
            "status": "NOT COMPLETED",
        }
        receipt["actual_close_observations"].append(row)
        event = {"operation": "close", **row}
        receipt["actual_descriptor_events"].append(event)
        try:
            operations.close(descriptor)
        except (AuditV23Error, AssertionError, OSError,
                TypeError, ValueError, KeyError) as error:
            row["status"] = "FAIL"
            row.update(observe_error(error, role + "-close"))
            event.update(row)
            raise
        row["status"] = "PASS"
        event["status"] = "PASS"
        field = {
            "writer": "writer_close_succeeded",
            "reader": "reader_close_succeeded",
            "parent": "parent_directory_close_succeeded",
        }[role]
        receipt[field] = True

    primary: BaseException | None = None
    try:
        directory = observe_open("parent", operations.open(parent, parent_flags))
        phase = "parent-fstat"
        actual_parent = operations.fstat(directory)
        phase = "parent-stat"
        named_parent = operations.stat(parent, follow_symlinks=False)
        phase = "parent-identity"
        require(stat.S_ISDIR(actual_parent.st_mode)
                and (actual_parent.st_dev, actual_parent.st_ino)
                == (named_parent.st_dev, named_parent.st_ino),
                "the exclusive V23 parent was swapped or replaced by a symlink")
        phase = "exclusive-create"
        descriptor = observe_open(
            "writer",
            operations.open(target.name, create_flags, 0o644, dir_fd=directory),
        )
        receipt["exclusive_create_succeeded"] = True
        remaining = memoryview(payload)
        while remaining:
            phase = "write"
            call = {"requested_bytes": len(remaining), "returned_bytes": None}
            receipt["actual_write_calls"].append(call)
            written = operations.write(descriptor, remaining)
            call["returned_bytes"] = written
            require(type(written) is int and 0 < written <= len(remaining),
                    "a genuine V23 publication returned an unsafe partial write")
            receipt["actual_bytes_written"] += written
            remaining = remaining[written:]
        phase = "file-fsync"
        operations.fsync(descriptor)
        receipt["file_fsync_succeeded"] = True
        phase = "writer-close"
        close_once("writer")
        phase = "directory-fsync"
        operations.fsync(directory)
        receipt["parent_directory_fsync_succeeded"] = True
        phase = "reread-open"
        reader = observe_open(
            "reader", operations.open(target.name, reread_flags, dir_fd=directory)
        )
        phase = "reread-fstat"
        identity = operations.fstat(reader)
        require(stat.S_ISREG(identity.st_mode)
                and identity.st_size == len(payload),
                "V23 cannot reread a complete genuine regular publication")
        chunks: list[bytes] = []
        total = 0
        while total <= len(payload):
            phase = "reread"
            piece = operations.read(reader, min(1024 * 1024, len(payload) + 1 - total))
            require(type(piece) is bytes, "V23 reread returned invented non-bytes")
            if not piece:
                break
            total += len(piece)
            require(total <= len(payload), "V23 reread contained extra evidence")
            chunks.append(piece)
        actual = b"".join(chunks)
        phase = "reread-verification"
        require(actual == payload and hashlib.sha256(actual).hexdigest() == digest,
                "the actual exclusively published V23 evidence changed")
        receipt["canonical_reread_succeeded"] = True
        phase = "reader-close"
        close_once("reader")
        phase = "parent-close"
        close_once("parent")
        phase = "complete-receipt-validation"
        receipt["status"] = "PASS"
        return validate_publication_receipt(receipt, relative, digest, len(payload))
    except (AuditV23Error, AssertionError, OSError,
            TypeError, ValueError, KeyError) as error:
        primary = error
        observed = observe_error(error, phase)
        receipt["actual_primary_failure"] = observed
        receipt["actual_error_type"] = observed["actual_error_type"]
        receipt["actual_error_message"] = observed["actual_error_message"]
        if "actual_errno" in observed:
            receipt["actual_errno"] = observed["actual_errno"]
    for role in ("reader", "writer", "parent"):
        if role not in descriptors:
            continue
        try:
            close_once(role)
        except (AuditV23Error, AssertionError, OSError,
                TypeError, ValueError, KeyError) as error:
            receipt["actual_cleanup_failures"].append(
                observe_error(error, role + "-close")
            )
    require(primary is not None,
            "V23 attempted to invent an exclusive-publication primary failure")
    receipt["status"] = "FAIL"
    raise AuditV23PublicationFailure(
        "the exclusive V23 publication failed; first error and actual cleanup retained",
        receipt,
    ) from primary


def write_report(
    report: Mapping[str, Any], *, strict: bool, operations: Any = os
) -> dict[str, Any]:
    require(isinstance(report, Mapping) and type(strict) is bool,
            "V23 can publish only its exact independently observed mode")
    passed = report.get("passed") is True
    relative, receipt_relative = mode_destinations(strict, passed)
    raw = canonical(report)
    digest = hashlib.sha256(raw).hexdigest()
    if passed:
        validate_report(
            dict(report), digest, strict=strict,
            base_digest=report.get("strict_base_report_sha256"),
        )
    report_receipt = _exclusive_publish(relative, raw, operations=operations)
    validate_publication_receipt(report_receipt, relative, digest, len(raw))
    receipt_raw = canonical(report_receipt)
    durable_receipt = _exclusive_publish(
        receipt_relative, receipt_raw, operations=operations
    )
    receipt_digest = hashlib.sha256(receipt_raw).hexdigest()
    validate_publication_receipt(
        durable_receipt, receipt_relative, receipt_digest, len(receipt_raw)
    )
    return {
        "report_path": relative,
        "report_sha256": digest,
        "actual_exclusive_publication_receipt": copy.deepcopy(report_receipt),
        "durable_publication_receipt_path": receipt_relative,
        "durable_publication_receipt_sha256": receipt_digest,
        "actual_receipt_publication_receipt": copy.deepcopy(durable_receipt),
    }


def run_audit(
    *,
    strict: bool,
    historical_base_sha256: str,
    historical_strict_sha256: str,
    base_report_sha256: str | None = None,
) -> dict[str, Any]:
    verify_production_runtime()
    require(type(strict) is bool, "V23 must select one exact independent mode")
    require((strict and valid_sha256(base_report_sha256))
            or (not strict and base_report_sha256 is None),
            "V23 strict proof requires an externally supplied current V23 base SHA")
    controller = authenticate_controller()
    base_document: dict[str, Any] | None = None
    base_graph: dict[str, Any] | None = None
    if strict:
        base_document, raw = _read_pinned_json(
            BASE_REPORT_RELATIVE,
            str(base_report_sha256),
            "actual externally pinned current V23 base report",
        )
        require(canonical(base_document) == raw,
                "V23 strict audit rejects rewritten or noncanonical base bytes")
        base_graph = validate_report(
            base_document, str(base_report_sha256), strict=False
        )
        require(base_document.get("audit_source_sha256")
                == controller["source_sha256"],
                "the externally pinned V23 base belongs to another controller")
    history = authenticate_historical_evidence(
        historical_base_sha256, historical_strict_sha256
    )
    controls = candidate_free_self_test()
    current, graph = snapshot_current_report()
    if strict:
        require(base_graph is not None, "V23 strict lost its authentic current base")
        _require_same_graph(graph, base_graph)
    workers: dict[str, dict[str, Any]] = {}
    processes: dict[str, dict[str, Any]] = {}
    failure: dict[str, Any] | None = None
    for family in CORE_FAMILIES:
        try:
            worker, process = run_native_worker_with_transcript(
                family, graph["native_sha256_by_family"][family]
            )
            workers[family] = worker
            processes[family] = process
        except original_owner.NativeWorkerFailure as error:
            failure = copy.deepcopy(dict(error.evidence))
            break
        except (AuditV23Error, AssertionError, OSError,
                TypeError, ValueError, KeyError) as error:
            failure = {
                "schema": SCHEMA + "-actual-native-owner-validation-failure",
                "status": "FAIL",
                "family": family,
                "candidate_module": v11.FAMILIES[family]["module"],
                "actual_validation_error_type": type(error).__name__,
                "actual_validation_error_message": str(error),
                "production_observations_invented": False,
                "qualifies_current_engine": False,
            }
            break
    if failure is None:
        try:
            _require_same_graph(read_only_current_graph(), graph)
        except (AuditV23Error, AssertionError, OSError,
                TypeError, ValueError, KeyError) as error:
            failure = {
                "schema": SCHEMA + "-actual-post-owner-graph-failure",
                "status": "FAIL",
                "actual_exception_type": type(error).__name__,
                "actual_exception_message": str(error),
                "actual_native_owner_workers_completed": len(workers),
                "actual_completed_native_owner_families": list(workers),
                "complete_actual_native_owner_observations":
                    copy.deepcopy(workers),
                "complete_actual_native_owner_processes":
                    copy.deepcopy(processes),
                "production_observations_invented": False,
                "qualifies_current_engine": False,
            }
    original_owner.core.ensure_candidate_free()
    report = build_report(
        current, graph, history, controls, controller,
        strict=strict, workers=workers, transcripts=processes,
        failure=failure, base_document=base_document,
        base_digest=base_report_sha256,
    )
    publication = write_report(report, strict=strict)
    return {
        "schema": SCHEMA + "-durable-audit-summary",
        "status": report["status"],
        "result": report["result"],
        "passed": report["passed"],
        "mode": "strict-no-delegation" if strict else "independent-native-ownership",
        **publication,
        "audit_source_path": SOURCE_RELATIVE,
        "audit_source_sha256": controller["source_sha256"],
        "audit_protocol_path": PROTOCOL_RELATIVE,
        "audit_protocol_sha256": PROTOCOL_SHA256,
        "strict_base_report_sha256": base_report_sha256,
        "historical_v21_base_report_sha256": historical_base_sha256,
        "historical_v21_strict_report_sha256": historical_strict_sha256,
        "historical_v21_graph_qualifies_current_engine": False,
        "historical_v15_failure_sha256": V15_FAILURE_SHA256,
        "verified_core_family_count": 3,
        "verified_candidate_source_count": 12,
        "verified_native_role_count": 5,
        "completed_native_owner_worker_count": len(workers),
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    with v11.source_only_boundary() as blocked:
        previous_import = builtins.__import__
        previous_import_module = importlib.import_module
        denied = {
            "candidates", "re", "_sre", "regex", "_regex", "pcre",
            "pcre2", "re2", "hyperscan", "rure", "onig", "oniguruma",
            "ctypes", "_ctypes", "cffi", "_cffi_backend",
        }
        effects = {
            "additional_forbidden_engine_imports_blocked": 0,
            "synthetic_publication_operations": 0,
        }

        def guarded_import(name: str, *args: Any, **kwargs: Any) -> Any:
            if isinstance(name, str) and name.partition(".")[0] in denied:
                effects["additional_forbidden_engine_imports_blocked"] += 1
                raise AuditV23Error("V23 source controls forbid candidate/matcher/FFI import")
            return previous_import(name, *args, **kwargs)

        def guarded_module(name: str, package: str | None = None) -> Any:
            if isinstance(name, str) and name.partition(".")[0] in denied:
                effects["additional_forbidden_engine_imports_blocked"] += 1
                raise AuditV23Error("V23 source controls forbid candidate/matcher/FFI import")
            return previous_import_module(name, package)

        builtins.__import__ = guarded_import
        importlib.import_module = guarded_module
        try:
            yield {**blocked, **effects, "_blocked": blocked, "_effects": effects}
        finally:
            importlib.import_module = previous_import_module
            builtins.__import__ = previous_import


def rejected(name: str, action: Callable[[], Any]) -> dict[str, Any]:
    try:
        action()
    except (AuditV23Error, historical_v21.AuditV21Error,
            original_owner.AuditV10Error, original_strict.AuditV10Error,
            original_owner.source_v6.AuditV6Error,
            original_owner.core.AuditV3Error, v11.ProofV11Error,
            AssertionError, OSError, UnicodeError, ValueError, TypeError, KeyError):
        return {"name": name, "passed": True}
    return {"name": name, "passed": False}


class _MemoryPublication:
    """Source-test-only syscall model; never touches a real file or descriptor."""

    def __init__(
        self,
        *,
        limit: int = 11,
        fail: str | tuple[str, ...] | None = None,
        reuse_closed: bool = False,
    ) -> None:
        require(type(limit) is int and limit > 0 and type(reuse_closed) is bool,
                "the modeled V23 syscall lifetime must have exact finite options")
        self.limit = limit
        self.reuse_closed = reuse_closed
        if fail is None:
            self.failures = frozenset()
        elif isinstance(fail, str):
            self.failures = frozenset({fail})
        else:
            require(type(fail) is tuple
                    and all(type(item) is str for item in fail)
                    and len(fail) == len(set(fail)),
                    "the source-only fake duplicated an invented failure")
            self.failures = frozenset(fail)
        self.files: dict[str, bytearray] = {}
        self.descriptors: dict[int, tuple[str, str, int]] = {}
        self.next_descriptor = 4
        self.reusable_descriptors: list[int] = []
        self.parent_identity = types.SimpleNamespace(
            st_mode=stat.S_IFDIR | 0o755, st_dev=41, st_ino=73, st_size=0
        )
        self.fsync_calls: list[int] = []
        self.close_calls: list[dict[str, Any]] = []

    def _allocate_descriptor(self) -> int:
        if self.reuse_closed and self.reusable_descriptors:
            descriptor = min(self.reusable_descriptors)
            self.reusable_descriptors.remove(descriptor)
        else:
            descriptor = self.next_descriptor
            self.next_descriptor += 1
        require(descriptor not in self.descriptors,
                "the source-only fake returned a simultaneously live descriptor")
        return descriptor

    def open(self, path: Any, flags: int, mode: int = 0o644,
             *, dir_fd: int | None = None) -> int:
        del mode
        if "open-parent" in self.failures and dir_fd is None:
            raise OSError("source-only modeled parent open failure")
        if dir_fd is None:
            require(Path(path) == ROOT / "candidates/audits",
                    "source-only fake rejected a foreign parent")
            descriptor = self._allocate_descriptor()
            self.descriptors[descriptor] = ("parent", "", 0)
            return descriptor
        require(dir_fd in self.descriptors
                and self.descriptors[dir_fd][0] == "parent",
                "source-only fake rejected a foreign directory descriptor")
        name = os.fspath(path)
        if flags & os.O_CREAT:
            if "exclusive-create" in self.failures or name in self.files:
                raise FileExistsError("source-only actual exclusive destination exists")
            if "simultaneous-writer-alias" in self.failures:
                return dir_fd
            require(bool(flags & os.O_EXCL),
                    "source-only fake rejected non-exclusive creation")
            descriptor = self._allocate_descriptor()
            self.files[name] = bytearray()
            self.descriptors[descriptor] = ("write", name, 0)
        else:
            if "reread-open" in self.failures:
                raise OSError("source-only modeled reread failure")
            require(name in self.files, "source-only fake lost actual written bytes")
            if "simultaneous-reader-alias" in self.failures:
                return dir_fd
            descriptor = self._allocate_descriptor()
            self.descriptors[descriptor] = ("read", name, 0)
        return descriptor

    def stat(self, path: Any, *, follow_symlinks: bool = False) -> Any:
        require(Path(path) == ROOT / "candidates/audits"
                and follow_symlinks is False,
                "source-only fake rejected an unsafe parent stat")
        if "swapped-parent" in self.failures:
            return types.SimpleNamespace(
                st_mode=stat.S_IFDIR | 0o755, st_dev=41, st_ino=74, st_size=0
            )
        return self.parent_identity

    def fstat(self, descriptor: int) -> Any:
        kind, name, _ = self.descriptors[descriptor]
        if kind == "parent":
            return self.parent_identity
        size = len(self.files[name])
        if "wrong-reread-size" in self.failures and kind == "read":
            size += 1
        return types.SimpleNamespace(
            st_mode=stat.S_IFREG | 0o644, st_dev=41, st_ino=1000, st_size=size
        )

    def write(self, descriptor: int, data: Any) -> int:
        kind, name, _ = self.descriptors[descriptor]
        require(kind == "write", "source-only fake rejected a foreign write")
        if "write" in self.failures:
            raise OSError("source-only modeled write failure")
        if "zero-write" in self.failures:
            return 0
        count = min(len(data), self.limit)
        self.files[name].extend(bytes(data[:count]))
        return count

    def fsync(self, descriptor: int) -> None:
        kind = self.descriptors[descriptor][0]
        if "file-fsync" in self.failures and kind == "write":
            raise OSError("source-only modeled file durability failure")
        if "directory-fsync" in self.failures and kind == "parent":
            raise OSError("source-only modeled directory durability failure")
        self.fsync_calls.append(descriptor)

    def read(self, descriptor: int, count: int) -> bytes:
        kind, name, offset = self.descriptors[descriptor]
        require(kind == "read", "source-only fake rejected a foreign read")
        if "read" in self.failures:
            raise OSError("source-only modeled complete readback failure")
        payload = self.files[name]
        result = bytes(payload[offset:offset + count])
        if "changed-reread" in self.failures and offset == 0 and result:
            result = bytes([result[0] ^ 1]) + result[1:]
        self.descriptors[descriptor] = (kind, name, offset + len(result))
        return result

    def close(self, descriptor: int) -> None:
        require(descriptor in self.descriptors,
                "the source-only fake detected a repeated or invented descriptor close")
        kind, _, _ = self.descriptors.pop(descriptor)
        role = {"write": "writer", "read": "reader", "parent": "parent"}[kind]
        observation = {
            "role": role,
            "descriptor": descriptor,
            "status": "NOT COMPLETED",
        }
        self.close_calls.append(observation)
        if self.reuse_closed:
            require(descriptor not in self.reusable_descriptors,
                    "the source-only fake recycled a descriptor twice")
            self.reusable_descriptors.append(descriptor)
        if role + "-close" in self.failures:
            observation["status"] = "FAIL"
            raise OSError("source-only modeled " + role + " descriptor close failure")
        observation["status"] = "PASS"


def _source_digest(label: str) -> str:
    return hashlib.sha256(("v23-source-only:" + label).encode("ascii")).hexdigest()


def _synthetic_v15_receipt() -> dict[str, Any]:
    return {
        "schema": "rebar-postfinal-cpython-full-public-locale-v15"
        + "-actual-exclusive-publication-receipt",
        "path": V15_FAILURE_RELATIVE,
        "expected_payload_sha256": V15_FAILURE_SHA256,
        "expected_payload_bytes": V15_FAILURE_BYTES,
        "actual_file_created": True,
        "actual_payload_bytes_written": V15_FAILURE_BYTES,
        "actual_write_calls": [{
            "requested_bytes": V15_FAILURE_BYTES,
            "returned_bytes": V15_FAILURE_BYTES,
        }],
        "actual_file_fsync": True,
        "actual_directory_fsync": True,
        "canonical_reread_succeeded": True,
        "fully_durable_publication": True,
    }


def _synthetic_history() -> dict[str, Any]:
    receipt = _synthetic_v15_receipt()
    return {
        "historical_v21_base_report_path": historical_v21.BASE_REPORT_RELATIVE,
        "historical_v21_base_report_sha256": _source_digest("historical-v21-base"),
        "historical_v21_strict_report_path": historical_v21.STRICT_REPORT_RELATIVE,
        "historical_v21_strict_report_sha256": _source_digest("historical-v21-strict"),
        "historical_v21_source_sha256": HISTORICAL_V21_SOURCE_SHA256,
        "historical_v21_protocol_sha256": HISTORICAL_V21_PROTOCOL_SHA256,
        "historical_v21_graph_qualifies_current_engine": False,
        "historical_failure_qualifies_current_engine": False,
        "historical_v5_baseline_path": v11.BASELINE_RELATIVE,
        "historical_v5_baseline_sha256": v11.BASELINE_SHA256,
        "historical_v6_baseline_path": V6_BASELINE_RELATIVE,
        "historical_v6_baseline_sha256": V6_BASELINE_SHA256,
        "original_method_count": ORIGINAL_METHODS,
        "original_public_method_count": PUBLIC_METHODS,
        "original_private_method_count": PRIVATE_METHODS,
        "public_method_waiver_count": 0,
        "named_private_class_waiver_count": 2,
        "named_private_debug_skip_kind": PRIVATE_DEBUG_SKIP_KIND,
        "preserved_v15_ownership_failure_path": V15_OWNERSHIP_FAILURE_RELATIVE,
        "preserved_v15_ownership_failure_sha256": V15_OWNERSHIP_FAILURE_SHA256,
        "preserved_v21_immutable_history": historical_v21.synthetic_history(),
        "preserved_v15_original_failure": {
            "failure_path": V15_FAILURE_RELATIVE,
            "failure_sha256": V15_FAILURE_SHA256,
            "failure_bytes": V15_FAILURE_BYTES,
            "forensic_path": V15_FORENSIC_RELATIVE,
            "forensic_sha256": V15_FORENSIC_SHA256,
            "production_summary_path": V15_SUMMARY_RELATIVE,
            "production_summary_sha256": V15_SUMMARY_SHA256,
            "original_method_denominator": 152,
            "passing_original_methods": 139,
            "harness_interference_errors": 11,
            "missing_private_compile_errors": 1,
            "named_private_debug_skips": 1,
            "native_owner_method_guard_checks": 304,
            "cached_matcher_method_guard_checks": 304,
            "actual_worker_returncode": 2,
            "actual_worker_stdout_sha256": V15_STDOUT_SHA256,
            "actual_worker_stdout_bytes": V15_STDOUT_BYTES,
            "actual_exclusive_publication_receipt": receipt,
            "historical_failure_qualifies_current_engine": False,
            "production_observations_invented": False,
        },
        "production_observations_invented": False,
    }


def _synthetic_v6_baseline() -> dict[str, Any]:
    records = [
        {
            "test": "ReTests.source_only_public_" + str(index),
            "status": "PASS",
            "source_ast_sha256": _source_digest("v6-public-method:" + str(index)),
        }
        for index in range(PUBLIC_METHODS - 1)
    ]
    records.append({
        "test": PRIVATE_DEBUG_METHOD,
        "status": "SKIP",
        "reason": PRIVATE_DEBUG_REASON,
        "skip_kind": PRIVATE_DEBUG_SKIP_KIND,
        "source_ast_sha256": PRIVATE_DEBUG_AST_SHA256,
    })
    role = {
        "role": "stdlib",
        "methods": PUBLIC_METHODS,
        "applicable": PUBLIC_METHODS - 1,
        "passed": PUBLIC_METHODS - 1,
        "skipped": 1,
        "named_private_debug_skips": 1,
        "unexplained_skips": 0,
        "failed": 0,
        "errors": 0,
        "timeouts": 0,
        "crashes": 0,
        "status": "PASS",
        "debug_build_coverage": "NOT RUN",
        "records_sha256": digest_value(records),
        "record_count": PUBLIC_METHODS,
        "records": records,
    }
    vector = [
        {
            "test": record["test"],
            "source_ast_sha256": record["source_ast_sha256"],
            "status": record["status"],
            "skip_kind": record.get("skip_kind"),
            "reason": record.get("reason"),
        }
        for record in records
    ]
    return {
        "schema": "rebar-postfinal-cpython-full-public-locale-v6-self-oracle",
        "status": "PASS",
        "synthetic": False,
        "python": "3.14.6",
        "source_path": V6_SOURCE_RELATIVE,
        "source_sha256": V6_SOURCE_SHA256,
        "protocol_path": V6_PROTOCOL_RELATIVE,
        "protocol_sha256": V6_PROTOCOL_SHA256,
        "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
        "all_original_methods": ORIGINAL_METHODS,
        "public_original_methods": PUBLIC_METHODS,
        "private_original_methods": PRIVATE_METHODS,
        "public_method_waivers": [],
        "named_private_class_waivers": copy.deepcopy(PRIVATE_CLASS_WAIVERS),
        "actual_independent_reference_count": 2,
        "reference_candidate_imports": 0,
        "reference_candidate_audits_read": 0,
        "reference_candidate_proofs_read": 0,
        "reference_holdout_cases_read": 0,
        "reference_status_vector_sha256": digest_value(vector),
        "roles": {
            "reference_a": copy.deepcopy(role),
            "reference_b": copy.deepcopy(role),
        },
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def candidate_free_self_test() -> dict[str, Any]:
    verify_runtime_source_only()
    source = v11.read_regular(ROOT / SOURCE_RELATIVE,
                              "exact source-only V23 controller")
    protocol = v11.authenticate_frozen(PROTOCOL_RELATIVE, PROTOCOL_SHA256)
    source_sha256 = hashlib.sha256(source).hexdigest()
    tree = ast.parse(source.decode("utf-8"), filename=SOURCE_RELATIVE)
    checks: list[dict[str, Any]] = []

    def accept(name: str, condition: Any) -> None:
        checks.append({"name": name, "passed": bool(condition)})

    with source_only_boundary() as observed:
        blocked = observed["_blocked"]
        additional = observed["_effects"]
        accept("parse-only-the-exact-independent-v23-controller",
               isinstance(tree, ast.Module))
        accept("authenticate-only-the-frozen-v23-protocol",
               hashlib.sha256(protocol).hexdigest() == PROTOCOL_SHA256)
        accept("rehash-the-actual-v23-source-without-predicting-it",
               valid_sha256(source_sha256))
        accept("preserve-three-separate-engine-families",
               CORE_FAMILIES == ("rust", "vm", "zig"))
        accept("preserve-exactly-twelve-owned-source-paths",
               sum(map(len, OWNED_SOURCE_PATHS.values())) == 12)
        accept("preserve-exactly-five-family-owned-native-paths",
               sum(map(len, OWNED_NATIVE_PATHS.values())) == 5)
        accept("preserve-exactly-all-165-original-upstream-methods",
               ORIGINAL_METHODS == 165)
        accept("preserve-exactly-152-original-public-methods-with-no-public-waiver",
               PUBLIC_METHODS == 152)
        accept("preserve-exactly-13-separately-accounted-private-methods",
               PRIVATE_METHODS == 13
               and ORIGINAL_METHODS == PUBLIC_METHODS + PRIVATE_METHODS)
        forbidden_calls = {
            node.attr for node in ast.walk(tree)
            if isinstance(node, ast.Attribute)
            and node.attr in {"authenticate_qualified_audits", "snapshot_current_graph"}
        }
        accept("never-qualify-an-edited-engine-with-a-live-v21-history",
               not forbidden_calls)
        for label, digest, expected in (
            ("v21-frozen-source", HISTORICAL_V21_SOURCE_SHA256,
             "ded077962416ada3bddd825d77b2e6785fe3b01184fe5d9058ec17a57b08ea4d"),
            ("v21-frozen-protocol", HISTORICAL_V21_PROTOCOL_SHA256,
             "5a78673c6b23e4781070cf5a2290d5f6cecd402fff77ff388d8795370de93a1f"),
            ("v15-original-failure", V15_FAILURE_SHA256,
             "fcd83830b36afd94dee6b926764a6300eaf048d5fa81404563d7e8afea2482c2"),
            ("v15-independent-ownership-failure", V15_OWNERSHIP_FAILURE_SHA256,
             "a3695f1fd847e9ad882783d18c519b551d7791c5327f55964e202a31ade818ff"),
            ("v15-read-only-forensic", V15_FORENSIC_SHA256,
             "4613b2421b3df30c5bebdbb4ae7c0d3530d80b70d5a627396aad2a25fefe85eb"),
            ("v15-actual-production-summary", V15_SUMMARY_SHA256,
             "d923e4687be96751e11b334cf8a37c0744552d01592cbb665bc4ec0cf9432c10"),
            ("v15-complete-worker-stdout", V15_STDOUT_SHA256,
             "bb6ed67d4cf96c2bc1be9dd64779cb5219ac3cdcf909fd5efd93dbf6da8a55ac"),
            ("v6-double-reference", V6_BASELINE_SHA256,
             "1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf"),
            ("original-public-method-matrix", METHOD_MATRIX_SHA256,
             "5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a"),
        ):
            accept("freeze-real-historical-pin-without-reading-evidence:" + label,
                   digest == expected and valid_sha256(digest))
        environment = {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "PYTHONPATH": str(ROOT),
        }
        accept("accept-only-an-exact-synthetic-isolated-production-parent",
               validate_parent_environment(environment) == environment)
        for key in environment:
            missing = dict(environment)
            del missing[key]
            checks.append(rejected(
                "reject-missing-isolated-production-parent:" + key,
                lambda row=missing: validate_parent_environment(row),
            ))
            for label, forged_value in (
                ("none", None), ("empty", ""), ("integer", 1),
                ("false", "false"), ("space", " "),
                ("foreign", "v23-source-only-forged"),
            ):
                changed = {**environment, key: forged_value}
                checks.append(rejected(
                    "reject-forged-production-parent:" + key + ":" + label,
                    lambda row=changed: validate_parent_environment(row),
                ))
        v6_fixture = _synthetic_v6_baseline()
        accept("validate-exact-source-only-v6-165-152-13-reference-matrix",
               validate_v6_baseline(copy.deepcopy(v6_fixture)) == v6_fixture)
        accept("keep-original-v15-upstream-and-ownership-failures-independent",
               V15_FAILURE_SHA256 != V15_OWNERSHIP_FAILURE_SHA256)
        accept("use-the-exact-authentic-private-class-waiver-dictionary",
               type(v6_fixture["named_private_class_waivers"]) is dict
               and v6_fixture["named_private_class_waivers"]
               == PRIVATE_CLASS_WAIVERS)
        accept("preserve-the-true-private-skip-kind-with-no-fake-classification",
               v6_fixture["roles"]["reference_a"]["records"][-1]
               .get("skip_kind") == PRIVATE_DEBUG_SKIP_KIND
               and "classification"
               not in v6_fixture["roles"]["reference_a"]["records"][-1])
        for field in (
            "schema", "status", "synthetic", "python", "source_path",
            "source_sha256", "protocol_path", "protocol_sha256",
            "public_method_matrix_sha256", "all_original_methods",
            "public_original_methods", "private_original_methods",
            "public_method_waivers", "named_private_class_waivers",
            "actual_independent_reference_count", "reference_candidate_imports",
            "reference_candidate_audits_read", "reference_candidate_proofs_read",
            "reference_holdout_cases_read", "reference_status_vector_sha256",
            "roles", "performance", "holdout",
        ):
            forged = copy.deepcopy(v6_fixture)
            previous = forged[field]
            forged[field] = None if previous is not None else "forged"
            checks.append(rejected(
                "reject-forged-genuine-v6-method-matrix-or-reference:" + field,
                lambda row=forged: validate_v6_baseline(row),
            ))
        for field, replacement in (
            ("test", "ReTests.source_only_fake_skip"),
            ("status", "PASS"),
            ("reason", "source-only unauthorized public waiver"),
            ("classification", "source-only-forged-private-skip"),
            ("skip_kind", "source-only-forged-private-skip"),
            ("source_ast_sha256", _source_digest("forged-private-method-ast")),
        ):
            forged = copy.deepcopy(v6_fixture)
            forged["roles"]["reference_a"]["records"][-1][field] = replacement
            checks.append(rejected(
                "reject-forged-canonical-v6-named-private-debug-waiver:" + field,
                lambda row=forged: validate_v6_baseline(row),
            ))
        for label, replacement in (
            ("list", ["DebugTests", "ImplementationTest"]),
            ("tuple", ("DebugTests", "ImplementationTest")),
            ("missing-debug-class", {
                "ImplementationTest": copy.deepcopy(
                    PRIVATE_CLASS_WAIVERS["ImplementationTest"]
                ),
            }),
            ("missing-implementation-class", {
                "DebugTests": copy.deepcopy(PRIVATE_CLASS_WAIVERS["DebugTests"]),
            }),
            ("forged-debug-method-count", {
                **copy.deepcopy(PRIVATE_CLASS_WAIVERS),
                "DebugTests": {
                    **PRIVATE_CLASS_WAIVERS["DebugTests"], "methods": 5,
                },
            }),
            ("forged-implementation-method-count", {
                **copy.deepcopy(PRIVATE_CLASS_WAIVERS),
                "ImplementationTest": {
                    **PRIVATE_CLASS_WAIVERS["ImplementationTest"], "methods": 8,
                },
            }),
            ("forged-debug-reason", {
                **copy.deepcopy(PRIVATE_CLASS_WAIVERS),
                "DebugTests": {
                    **PRIVATE_CLASS_WAIVERS["DebugTests"],
                    "reason": "forged public waiver",
                },
            }),
            ("forged-implementation-reason", {
                **copy.deepcopy(PRIVATE_CLASS_WAIVERS),
                "ImplementationTest": {
                    **PRIVATE_CLASS_WAIVERS["ImplementationTest"],
                    "reason": "forged third-party matcher waiver",
                },
            }),
            ("unexpected-private-class", {
                **copy.deepcopy(PRIVATE_CLASS_WAIVERS),
                "ForgedTests": {"methods": 0, "reason": "forged"},
            }),
        ):
            forged = copy.deepcopy(v6_fixture)
            forged["named_private_class_waivers"] = replacement
            checks.append(rejected(
                "reject-noncanonical-v6-private-waiver-dictionary:" + label,
                lambda row=forged: validate_v6_baseline(row),
            ))

        def rehash_synthetic_reference(row: dict[str, Any]) -> dict[str, Any]:
            vectors: list[list[dict[str, Any]]] = []
            for label in ("reference_a", "reference_b"):
                role = row["roles"][label]
                records = role["records"]
                role["records_sha256"] = digest_value(records)
                vectors.append([
                    {
                        "test": record.get("test"),
                        "source_ast_sha256": record.get("source_ast_sha256"),
                        "status": record.get("status"),
                        "skip_kind": record.get("skip_kind"),
                        "reason": record.get("reason"),
                    }
                    for record in records
                ])
            if vectors[0] == vectors[1]:
                row["reference_status_vector_sha256"] = digest_value(vectors[0])
            return row

        for label, transform in (
            ("classification-only", lambda record: (
                record.pop("skip_kind"),
                record.__setitem__("classification", PRIVATE_DEBUG_SKIP_KIND),
            )),
            ("extra-classification", lambda record:
             record.__setitem__("classification", PRIVATE_DEBUG_SKIP_KIND)),
            ("missing-skip-kind", lambda record: record.pop("skip_kind")),
            ("wrong-skip-kind", lambda record:
             record.__setitem__("skip_kind", "forged-private-debug-condition")),
            ("wrong-private-reason", lambda record:
             record.__setitem__("reason", "forged debug waiver")),
            ("wrong-private-source-ast", lambda record:
             record.__setitem__("source_ast_sha256",
                                _source_digest("forged-private-ast-after-rehash"))),
        ):
            forged = copy.deepcopy(v6_fixture)
            for role in ("reference_a", "reference_b"):
                transform(forged["roles"][role]["records"][-1])
            rehash_synthetic_reference(forged)
            checks.append(rejected(
                "reject-rehashed-classification-or-forged-private-skip:" + label,
                lambda row=forged: validate_v6_baseline(row),
            ))
        for role_name in ("reference_a", "reference_b"):
            for field in (
                "role", "methods", "applicable", "passed", "skipped",
                "named_private_debug_skips", "unexplained_skips", "failed",
                "errors", "timeouts", "crashes", "status",
                "debug_build_coverage", "record_count", "records_sha256",
            ):
                forged = copy.deepcopy(v6_fixture)
                value = forged["roles"][role_name][field]
                forged["roles"][role_name][field] = (
                    None if value is not None else "forged"
                )
                checks.append(rejected(
                    "reject-complete-original-v6-role-summary:"
                    + role_name + ":" + field,
                    lambda row=forged: validate_v6_baseline(row),
                ))
        for relative in sorted(APPROVED_OUTPUTS):
            accept("allow-only-one-exact-fresh-v23-destination:" + relative,
                   destination_name(relative) == relative)
        for label, relative in (
            ("v21-base", historical_v21.BASE_REPORT_RELATIVE),
            ("v21-strict", historical_v21.STRICT_REPORT_RELATIVE),
            ("v10-base", original_owner.REPORT_RELATIVE),
            ("v10-strict", original_strict.REPORT_RELATIVE),
            ("v15-failure", V15_FAILURE_RELATIVE),
            ("v15-forensic", V15_FORENSIC_RELATIVE),
            ("holdout", "performance/private-holdout.json"),
            ("parent", "../POSTFINAL-FROM-SCRATCH-AUDIT-V23.json"),
            ("absolute", "/tmp/POSTFINAL-FROM-SCRATCH-AUDIT-V23.json"),
            ("windows", "candidates\\audits\\forged.json"),
            ("nul", "candidates/audits/forged\x00.json"),
            ("unknown", "candidates/audits/POSTFINAL-FORGED-V23.json"),
        ):
            checks.append(rejected(
                "reject-historical-foreign-or-unsafe-v23-destination:" + label,
                lambda value=relative: destination_name(value),
            ))
        for strict in (False, True):
            for passed in (False, True):
                report_path, receipt_path = mode_destinations(strict, passed)
                accept(
                    "separate-v23-report-and-receipt:"
                    + str(int(strict)) + ":" + str(int(passed)),
                    report_path != receipt_path
                    and report_path in APPROVED_OUTPUTS
                    and receipt_path in APPROVED_OUTPUTS,
                )
        workers: dict[str, dict[str, Any]] = {}
        natives: dict[str, dict[str, str]] = {}
        processes: dict[str, dict[str, Any]] = {}
        for family in CORE_FAMILIES:
            worker, native = original_owner.synthetic_worker(family)
            workers[family] = worker
            natives[family] = native
            accept("validate-complete-source-only-native-owner:" + family,
                   validate_native_owner(copy.deepcopy(worker), family, native)
                   == worker)
            raw_stdout = original_owner.core.canonical(worker) + b"\n"
            actual, process = _decode_worker_output(
                family, native, 0, raw_stdout, b""
            )
            processes[family] = process
            accept("validate-true-complete-modeled-worker-stdout:" + family,
                   actual == worker
                   and validate_native_worker_transcript(
                       process, actual, family, native
                   ) == process)
            for field, changed in (
                ("schema", "rebar-forged-native-owner"),
                ("status", "FAIL"), ("result", "FAIL"), ("passed", False),
                ("family", "foreign-family"),
                ("candidate_module", "candidates.foreign_candidate"),
                ("native_binary_sha256", {}),
                ("match_repr_checks", 1),
                ("standard_pickle_check_count", 15),
                ("standard_pickle_failure_count", 1),
                ("regex_guard_count", 12),
                ("native_loader_guard_count", 4),
                ("persistent_cross_engine_guard", False),
                ("genuine_matching_executed", False),
                ("external_regex_packages", 1),
                ("benchmark_or_timing_executed", True),
                ("holdout_or_case_fixture_access", True),
                ("stage07_guard_sentinel", {}),
                ("stage07_matcher_descendant_guards", {}),
                ("regex_guard_observations", []),
                ("native_loader_guard_observations", []),
                ("standard_pickle_checks", []),
            ):
                forged = copy.deepcopy(worker)
                forged[field] = changed
                checks.append(rejected(
                    "reject-cross-engine-sentinel-or-ffi:" + family + ":" + field,
                    lambda row=forged, selected=family, expected=native:
                    validate_native_owner(row, selected, expected),
                ))
            for other in CORE_FAMILIES:
                if family != other:
                    checks.append(rejected(
                        "reject-cross-family-matcher-and-native-owner:"
                        + family + ":" + other,
                        lambda row=copy.deepcopy(worker), selected=other,
                        expected=native:
                        validate_native_owner(row, selected, expected),
                    ))
            for label, code, candidate_stdout, candidate_stderr in (
                ("failure-exit", 1, raw_stdout, b""),
                ("negative-exit", -9, raw_stdout, b""),
                ("empty-stdout", 0, b"", b""),
                ("truncated-stdout", 0, raw_stdout[:-1], b""),
                ("extra-stdout", 0, raw_stdout + b"forged", b""),
                ("nonempty-stderr", 0, raw_stdout, b"forged"),
            ):
                checks.append(rejected(
                    "reject-invented-or-partial-actual-worker-stream:"
                    + family + ":" + label,
                    lambda selected=family, expected=native, status=code,
                    out=candidate_stdout, err=candidate_stderr:
                    _decode_worker_output(selected, expected, status, out, err),
                ))
            for field in (
                "schema", "family", "candidate_module", "actual_executable",
                "actual_python_flags", "actual_working_directory",
                "native_owner_worker_sha256", "actual_worker_environment",
                "actual_native_argument", "actual_returncode",
                "actual_original_worker_stdout", "actual_original_worker_stderr",
                "production_observations_invented",
            ):
                forged = copy.deepcopy(process)
                forged[field] = None if forged[field] is not None else "forged"
                checks.append(rejected(
                    "reject-incomplete-true-owner-process:"
                    + family + ":" + field,
                    lambda row=forged, record=worker, selected=family,
                    expected=native:
                    validate_native_worker_transcript(
                        row, record, selected, expected
                    ),
                ))
        history = _synthetic_history()
        accept("validate-history-without-reading-an-actual-report-or-failure",
               validate_preserved_history(copy.deepcopy(history)) == history)
        for key in tuple(history):
            forged = copy.deepcopy(history)
            forged[key] = None if forged[key] is not None else "forged"
            checks.append(rejected(
                "reject-forged-or-retroactively-qualified-old-history:" + key,
                lambda row=forged: validate_preserved_history(row),
            ))
        failure_fixture = history["preserved_v15_original_failure"]
        for key in tuple(failure_fixture):
            forged = copy.deepcopy(history)
            previous = forged["preserved_v15_original_failure"][key]
            forged["preserved_v15_original_failure"][key] = (
                None if previous is not None else "forged"
            )
            checks.append(rejected(
                "reject-forged-real-v15-failure-or-receipt:" + key,
                lambda row=forged: validate_preserved_history(row),
            ))
        synthetic = original_strict.synthetic_base({
            "base_source": historical_v21.V10_OWNER_SOURCE_SHA256,
            "base_report": _source_digest("legacy-v10-source-only-base"),
        })
        graph = full_graph(synthetic)
        accept("validate-complete-modeled-twelve-source-five-native-graph",
               graph["source_count"] == 12
               and graph["native_binary_count"] == 5)
        for family in CORE_FAMILIES:
            for relative in OWNED_SOURCE_PATHS[family]:
                forged = copy.deepcopy(graph)
                forged["source_sha256_by_family"][family][relative] = (
                    _source_digest("stale-owned-source:" + relative)
                )
                checks.append(rejected(
                    "reject-stale-or-changed-owned-source:" + relative,
                    lambda row=forged, expected=graph:
                    _require_same_graph(row, expected),
                ))
            for relative in OWNED_NATIVE_PATHS[family].values():
                forged = copy.deepcopy(graph)
                forged["native_sha256_by_family"][family][relative] = (
                    _source_digest("foreign-owned-elf:" + relative)
                )
                checks.append(rejected(
                    "reject-stale-or-cross-family-native-ffi:" + relative,
                    lambda row=forged, expected=graph:
                    _require_same_graph(row, expected),
                ))
        current_workers = {
            family: original_owner.synthetic_worker(family)[0]
            for family in CORE_FAMILIES
        }
        current_processes: dict[str, dict[str, Any]] = {}
        for family in CORE_FAMILIES:
            expected = graph["native_sha256_by_family"][family]
            template = copy.deepcopy(current_workers[family])
            template["native_binary_sha256"] = copy.deepcopy(expected)
            current_workers[family] = template
            raw_stdout = original_owner.core.canonical(template) + b"\n"
            _, current_processes[family] = _decode_worker_output(
                family, expected, 0, raw_stdout, b""
            )
        synthetic_controls = {
            "schema": SCHEMA + "-self-test",
            "status": "PASS",
            "passed": True,
            "check_count": 150,
            **{key: 0 for key in (
                "candidate_imports", "subprocesses", "file_reads", "file_writes",
                "clock_samples", "historical_evidence_reads",
                "actual_audit_report_reads", "holdout_reads",
            )},
            "synthetic_results_qualify_candidates": False,
        }
        controller = {
            "source_path": SOURCE_RELATIVE,
            "source_sha256": source_sha256,
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": PROTOCOL_SHA256,
        }
        base = build_report(
            synthetic, graph, history, synthetic_controls, controller,
            strict=False, workers=current_workers, transcripts=current_processes,
            failure=None,
        )
        base_digest = hashlib.sha256(canonical(base)).hexdigest()
        accept("validate-full-source-only-v23-base-without-a-production-run",
               validate_report(copy.deepcopy(base), base_digest, strict=False)
               == graph)
        strict = build_report(
            synthetic, graph, history, synthetic_controls, controller,
            strict=True, workers=current_workers, transcripts=current_processes,
            failure=None, base_document=base, base_digest=base_digest,
        )
        strict_digest = hashlib.sha256(canonical(strict)).hexdigest()
        accept("validate-distinct-source-only-strict-with-external-base-hash",
               strict_digest != base_digest
               and validate_report(
                   copy.deepcopy(strict), strict_digest,
                   strict=True, base_digest=base_digest
               ) == graph)
        checks.append(rejected(
            "reject-a-predicted-or-missing-strict-base-hash",
            lambda: validate_report(strict, strict_digest,
                                    strict=True, base_digest=None),
        ))
        checks.append(rejected(
            "reject-reusing-a-strict-hash-as-its-independent-base",
            lambda: validate_report(strict, strict_digest,
                                    strict=True, base_digest=strict_digest),
        ))
        protected = (
            "schema", "postfinal_schema", "status", "result", "passed",
            "audit_source_path", "audit_source_sha256", "audit_protocol_path",
            "audit_protocol_sha256", "v10_native_owner_source_path",
            "v10_native_owner_source_sha256", "v10_no_delegation_source_path",
            "v10_no_delegation_source_sha256", "native_owner_worker_sha256",
            "verified_core_family_count", "verified_distinct_pipeline_count",
            "verified_candidate_source_count", "verified_candidate_source_paths",
            "source_sha256_by_family", "verified_native_role_count",
            "native_sha256_by_family", "actual_native_owner_workers",
            "actual_native_owner_processes",
            "complete_actual_native_owner_streams_preserved",
            "actual_native_owner_worker_failure",
            "completed_native_owner_worker_count", "verified_match_repr_checks",
            "verified_standard_pickle_count", "standard_pickle_failure_count",
            "genuine_python_matching_guards_per_family",
            "genuine_native_loader_guards_per_family", "preserved_immutable_history",
            "historical_v21_graph_qualifies_current_engine",
            "historical_failure_qualifies_current_engine",
            "postfinal_wrapper_self_test", "strict_base_report_path",
            "strict_base_report_sha256", "independent_base_native_owner_workers",
            "postfinal_scope", "production_observations_invented",
            "benchmark_or_timing_executed", "holdout_or_case_fixture_access",
            "performance", "holdout", "families", "native_elf_provenance",
            "manifest_provenance", "runtime_native_mapping_provenance",
        )
        for label, document, digest, is_strict in (
            ("base", base, base_digest, False),
            ("strict", strict, strict_digest, True),
        ):
            for field in protected:
                if field not in document:
                    continue
                forged = copy.deepcopy(document)
                previous = forged[field]
                forged[field] = None if previous is not None else "forged"
                forged_digest = hashlib.sha256(canonical(forged)).hexdigest()
                checks.append(rejected(
                    "reject-forged-complete-v23-report:" + label + ":" + field,
                    lambda row=forged, observed_digest=forged_digest,
                    selected=is_strict:
                    validate_report(
                        row, observed_digest, strict=selected,
                        base_digest=base_digest if selected else None,
                    ),
                ))
            checks.append(rejected(
                "reject-wrong-canonical-v23-report-hash:" + label,
                lambda row=document, selected=is_strict:
                validate_report(
                    row, _source_digest("wrong-report:" + label), strict=selected,
                    base_digest=base_digest if selected else None,
                ),
            ))
        payload = canonical({"schema": SCHEMA + "-source-only-publication",
                             "status": "PASS", "synthetic": True})
        memory = _MemoryPublication(limit=7)
        receipt = _exclusive_publish(BASE_REPORT_RELATIVE, payload,
                                     operations=memory)
        additional["synthetic_publication_operations"] += 1
        payload_digest = hashlib.sha256(payload).hexdigest()
        accept("model-exact-directory-relative-exclusive-durable-publication",
               validate_publication_receipt(
                   receipt, BASE_REPORT_RELATIVE, payload_digest, len(payload)
               ) == receipt
               and len(receipt["actual_write_calls"]) > 1
               and len(memory.fsync_calls) == 2
               and [item["role"] for item in receipt["actual_close_observations"]]
               == ["writer", "reader", "parent"]
               and receipt["actual_close_observations"] == memory.close_calls
               and memory.descriptors == {})
        reused_memory = _MemoryPublication(limit=7, reuse_closed=True)
        reused_receipt = _exclusive_publish(
            BASE_REPORT_RELATIVE, payload, operations=reused_memory
        )
        additional["synthetic_publication_operations"] += 1
        reused_closes = reused_receipt["actual_close_observations"]
        accept(
            "accept-genuine-kernel-writer-to-reader-descriptor-reuse",
            validate_publication_receipt(
                reused_receipt, BASE_REPORT_RELATIVE,
                payload_digest, len(payload),
            ) == reused_receipt
            and [row["role"] for row in reused_closes]
            == ["writer", "reader", "parent"]
            and [row["descriptor"] for row in reused_closes] == [5, 5, 4]
            and len({row["descriptor"] for row in reused_closes}) == 2
            and reused_closes == reused_memory.close_calls
            and not reused_memory.descriptors
            and validate_descriptor_lifetimes(reused_receipt, complete=True)
            == reused_receipt["actual_descriptor_events"],
        )
        for field in (
            "schema", "status", "report_path", "report_sha256",
            "expected_bytes", "actual_bytes_written",
            "actual_parent_open_flags", "actual_create_open_flags",
            "actual_reread_open_flags", "exclusive_create_succeeded",
            "file_fsync_succeeded", "writer_close_succeeded",
            "parent_directory_fsync_succeeded", "canonical_reread_succeeded",
            "reader_close_succeeded", "parent_directory_close_succeeded",
            "actual_primary_failure", "actual_cleanup_failures",
            "actual_close_observations", "actual_descriptor_events",
            "production_observations_invented",
            "actual_write_calls",
        ):
            forged = copy.deepcopy(receipt)
            previous = forged[field]
            forged[field] = None if previous is not None else "forged"
            checks.append(rejected(
                "reject-forged-exclusive-v23-syscall-transition:" + field,
                lambda row=forged:
                validate_publication_receipt(
                    row, BASE_REPORT_RELATIVE, payload_digest, len(payload)
                ),
            ))
        for flag, label in (
            (os.O_EXCL, "exclusive"),
            (os.O_CREAT, "create"),
            (getattr(os, "O_NOFOLLOW", 0), "no-follow"),
        ):
            if flag:
                forged = copy.deepcopy(receipt)
                forged["actual_create_open_flags"] &= ~flag
                checks.append(rejected(
                    "reject-unsafe-real-publication-flag:" + label,
                    lambda row=forged:
                    validate_publication_receipt(
                        row, BASE_REPORT_RELATIVE, payload_digest, len(payload)
                    ),
                ))
        for index, (operation, role) in enumerate((
            ("open", "parent"),
            ("open", "writer"),
            ("close", "writer"),
            ("open", "reader"),
            ("close", "reader"),
            ("close", "parent"),
        )):
            for field, replacement in (
                ("operation", "forged-lifetime"),
                ("role", "forged-role"),
                ("descriptor", None),
                ("status", "FAIL"),
            ):
                forged = copy.deepcopy(reused_receipt)
                forged["actual_descriptor_events"][index][field] = replacement
                checks.append(rejected(
                    "reject-forged-role-tagged-descriptor-lifetime:"
                    + operation + ":" + role + ":" + field,
                    lambda row=forged:
                    validate_publication_receipt(
                        row, BASE_REPORT_RELATIVE, payload_digest, len(payload)
                    ),
                ))
        for label, mutate in (
            ("simultaneous-parent-and-writer", lambda rows:
             rows[1].__setitem__("descriptor", rows[0]["descriptor"])),
            ("simultaneous-parent-and-reader", lambda rows:
             rows[3].__setitem__("descriptor", rows[0]["descriptor"])),
            ("reader-reused-before-writer-close", lambda rows:
             rows.insert(2, copy.deepcopy(rows[3]))),
            ("duplicate-writer-close", lambda rows:
             rows.insert(3, copy.deepcopy(rows[2]))),
            ("duplicate-reader-close", lambda rows:
             rows.insert(5, copy.deepcopy(rows[4]))),
            ("missing-parent-open", lambda rows: rows.pop(0)),
            ("missing-parent-close", lambda rows: rows.pop()),
        ):
            forged = copy.deepcopy(reused_receipt)
            mutate(forged["actual_descriptor_events"])
            checks.append(rejected(
                "reject-live-alias-or-duplicate-descriptor-event:" + label,
                lambda row=forged:
                validate_publication_receipt(
                    row, BASE_REPORT_RELATIVE, payload_digest, len(payload)
                ),
            ))
        forged_after_failure = copy.deepcopy(reused_receipt)
        failed_event = forged_after_failure["actual_descriptor_events"][2]
        failed_close = forged_after_failure["actual_close_observations"][0]
        close_error = {
            "status": "FAIL",
            "stage": "writer-close",
            "actual_error_type": "OSError",
            "actual_error_message": "source-only modeled writer descriptor close failure",
        }
        failed_event.update(close_error)
        failed_close.update(close_error)
        checks.append(rejected(
            "reject-descriptor-reuse-after-a-failed-writer-close",
            lambda row=forged_after_failure:
            validate_descriptor_lifetimes(row, complete=False),
        ))
        for index, role in enumerate(("writer", "reader", "parent")):
            for field, replacement in (
                ("role", "source-only-forged-descriptor"),
                ("descriptor", None),
                ("status", "FAIL"),
            ):
                forged = copy.deepcopy(receipt)
                forged["actual_close_observations"][index][field] = replacement
                checks.append(rejected(
                    "reject-forged-independent-descriptor-close:"
                    + role + ":" + field,
                    lambda row=forged:
                    validate_publication_receipt(
                        row, BASE_REPORT_RELATIVE, payload_digest, len(payload)
                    ),
                ))
        for forged_closures, label in (
            (receipt["actual_close_observations"][:2], "missing-parent-close"),
            (receipt["actual_close_observations"][1:], "missing-writer-close"),
            (list(reversed(receipt["actual_close_observations"])),
             "wrong-close-order"),
            ([*receipt["actual_close_observations"],
              receipt["actual_close_observations"][0]], "repeated-close"),
        ):
            forged = copy.deepcopy(receipt)
            forged["actual_close_observations"] = copy.deepcopy(forged_closures)
            checks.append(rejected(
                "reject-unobserved-or-repeated-real-descriptor-close:" + label,
                lambda row=forged:
                validate_publication_receipt(
                    row, BASE_REPORT_RELATIVE, payload_digest, len(payload)
                ),
            ))
        failure_cases: tuple[tuple[str, str | tuple[str, ...], str,
                                   tuple[str, ...]], ...] = (
            ("open-parent", "open-parent", "parent-open", ()),
            ("exclusive-create", "exclusive-create", "exclusive-create", ()),
            ("swapped-parent", "swapped-parent", "parent-identity", ()),
            ("simultaneous-writer-alias", "simultaneous-writer-alias",
             "exclusive-create", ()),
            ("write", "write", "write", ()),
            ("zero-write", "zero-write", "write", ()),
            ("file-fsync", "file-fsync", "file-fsync", ()),
            ("directory-fsync", "directory-fsync", "directory-fsync", ()),
            ("reread-open", "reread-open", "reread-open", ()),
            ("simultaneous-reader-alias", "simultaneous-reader-alias",
             "reread-open", ()),
            ("wrong-reread-size", "wrong-reread-size", "reread-fstat", ()),
            ("read", "read", "reread", ()),
            ("changed-reread", "changed-reread", "reread-verification", ()),
            ("writer-close", "writer-close", "writer-close", ()),
            ("reader-close", "reader-close", "reader-close", ()),
            ("parent-close", "parent-close", "parent-close", ()),
            ("write-and-writer-close", ("write", "writer-close"),
             "write", ("writer-close",)),
            ("write-and-parent-close", ("write", "parent-close"),
             "write", ("parent-close",)),
            ("write-and-both-cleanup-closes",
             ("write", "writer-close", "parent-close"),
             "write", ("writer-close", "parent-close")),
            ("read-and-both-cleanup-closes",
             ("read", "reader-close", "parent-close"),
             "reread", ("reader-close", "parent-close")),
            ("reader-close-and-parent-cleanup",
             ("reader-close", "parent-close"),
             "reader-close", ("parent-close",)),
            ("writer-close-and-parent-cleanup",
             ("writer-close", "parent-close"),
             "writer-close", ("parent-close",)),
            ("reread-open-and-parent-cleanup",
             ("reread-open", "parent-close"),
             "reread-open", ("parent-close",)),
            ("file-fsync-and-both-cleanup-closes",
             ("file-fsync", "writer-close", "parent-close"),
             "file-fsync", ("writer-close", "parent-close")),
        )
        for label, stages, expected_primary, expected_cleanup in failure_cases:
            modeled = _MemoryPublication(limit=7, fail=stages, reuse_closed=True)

            def fails_once(
                mock: _MemoryPublication = modeled,
                expected_stage: str = expected_primary,
                expected_cleanup_stages: tuple[str, ...] = expected_cleanup,
            ) -> bool:
                try:
                    _exclusive_publish(BASE_REPORT_RELATIVE, payload,
                                       operations=mock)
                except AuditV23PublicationFailure as error:
                    evidence = error.receipt
                    primary = evidence.get("actual_primary_failure")
                    cleanup = evidence.get("actual_cleanup_failures")
                    close_observations = evidence.get("actual_close_observations")
                    require(evidence.get("status") == "FAIL"
                            and evidence.get("report_path")
                            == BASE_REPORT_RELATIVE
                            and evidence.get("production_observations_invented")
                            is False
                            and isinstance(primary, dict)
                            and primary.get("stage") == expected_stage
                            and evidence.get("actual_error_type")
                            == primary.get("actual_error_type")
                            and evidence.get("actual_error_message")
                            == primary.get("actual_error_message")
                            and isinstance(cleanup, list)
                            and tuple(item.get("stage") for item in cleanup)
                            == expected_cleanup_stages
                            and isinstance(close_observations, list)
                            and validate_descriptor_lifetimes(
                                evidence, complete=False
                            ) == evidence.get("actual_descriptor_events")
                            and [
                                {
                                    "role": item["role"],
                                    "descriptor": item["descriptor"],
                                    "status": item["status"],
                                }
                                for item in close_observations
                            ] == mock.close_calls
                            and not mock.descriptors,
                            "V23 hid its first error, cleanup, or descriptor closure")
                    calls = evidence.get("actual_write_calls")
                    require(isinstance(calls, list)
                            and sum(
                                row["returned_bytes"]
                                for row in calls
                                if type(row.get("returned_bytes")) is int
                                and row["returned_bytes"] > 0
                            ) == evidence.get("actual_bytes_written"),
                            "V23 fabricated an incomplete real partial-write ledger")
                    return True
                return False

            accept(
                "reject-sole-actual-exclusive-publication-failure:" + label,
                fails_once(),
            )
        modeled = _MemoryPublication(limit=9, reuse_closed=True)
        published = write_report(base, strict=False, operations=modeled)
        additional["synthetic_publication_operations"] += 1
        accept("model-distinct-completely-durable-report-and-receipt",
               published["report_path"] == BASE_REPORT_RELATIVE
               and published["durable_publication_receipt_path"]
               == BASE_RECEIPT_RELATIVE
               and published["report_sha256"] == base_digest
               and set(modeled.files) == {
                   PurePosixPath(BASE_REPORT_RELATIVE).name,
                   PurePosixPath(BASE_RECEIPT_RELATIVE).name,
               }
               and len(modeled.fsync_calls) == 4
               and len(modeled.close_calls) == 6
               and [item["role"] for item in modeled.close_calls]
               == ["writer", "reader", "parent", "writer", "reader", "parent"]
               and modeled.close_calls[0]["descriptor"]
               == modeled.close_calls[1]["descriptor"]
               and modeled.close_calls[3]["descriptor"]
               == modeled.close_calls[4]["descriptor"]
               and modeled.descriptors == {})
        for name in ("candidates.rust_candidate", "candidates.vm_candidate",
                     "candidates.zig_candidate", "re", "_sre", "regex",
                     "pcre2", "re2", "ctypes", "cffi"):
            checks.append(rejected(
                "actively-block-candidate-stdlib-or-foreign-matcher:" + name,
                lambda selected=name: importlib.import_module(selected),
            ))
        for label, relative in (
            ("historical-failure", V15_FAILURE_RELATIVE),
            ("historical-forensic", V15_FORENSIC_RELATIVE),
            ("historical-base", historical_v21.BASE_REPORT_RELATIVE),
            ("new-base-report", BASE_REPORT_RELATIVE),
            ("candidate-source", "candidates/rust_candidate.py"),
            ("candidate-native", "candidates/_rust_engine.so"),
            ("holdout", "performance/private-holdout.json"),
        ):
            checks.append(rejected(
                "actively-block-evidence-candidate-and-holdout-reads:" + label,
                lambda selected=relative: builtins.open(ROOT / selected, "rb"),
            ))
        checks.append(rejected(
            "actively-block-actual-native-worker-process",
            lambda: subprocess.run([str(v11.PINNED_EXECUTABLE), "-I", "-B"]),
        ))
        checks.append(rejected(
            "actively-block-actual-source-control-filesystem-write",
            lambda: builtins.open(ROOT / BASE_REPORT_RELATIVE, "wb"),
        ))
        checks.append(rejected(
            "actively-block-actual-clock-or-performance-sample",
            lambda: time.perf_counter(),
        ))
        accept("block-all-candidate-standard-library-and-foreign-engine-imports",
               additional["additional_forbidden_engine_imports_blocked"] >= 10)
        accept("block-all-real-historical-evidence-candidate-and-holdout-reads",
               blocked["evidence_read_attempts_blocked"] >= 7)
        accept("block-a-genuine-native-worker-before-it-can-start",
               blocked["worker_attempts_blocked"] >= 1)
        accept("block-a-genuine-report-write-before-it-can-start",
               blocked["write_attempts_blocked"] >= 1)
        accept("block-a-genuine-clock-before-a-performance-sample",
               blocked["clock_attempts_blocked"] >= 1)
        accept("prove-durable-syscalls-only-with-in-memory-models",
               additional["synthetic_publication_operations"] == 3)
        accept("never-import-any-production-candidate",
               not any(name == "candidates" or name.startswith("candidates.")
                       for name in sys.modules))
        accept("retain-at-least-150-independent-v23-source-only-adversaries",
               len(checks) >= 150)
        names = [row["name"] for row in checks]
        require(len(names) == len(set(names)),
                "V23 repeated a source-only control or changed its denominator")
        failures = [row["name"] for row in checks if row.get("passed") is not True]
        require(not failures,
                "a real V23 source-only adversary escaped: "
                + ", ".join(failures[:12]))
        counts = dict(blocked)
        extra = dict(additional)
    verify_runtime_source_only()
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "check_count": len(checks),
        "checks": checks,
        "audit_source_path": SOURCE_RELATIVE,
        "audit_source_sha256": source_sha256,
        "audit_protocol_path": PROTOCOL_RELATIVE,
        "audit_protocol_sha256": PROTOCOL_SHA256,
        "historical_v21_source_sha256": HISTORICAL_V21_SOURCE_SHA256,
        "historical_v21_protocol_sha256": HISTORICAL_V21_PROTOCOL_SHA256,
        "preserved_v15_failure_sha256": V15_FAILURE_SHA256,
        "preserved_v15_ownership_failure_sha256": V15_OWNERSHIP_FAILURE_SHA256,
        "preserved_v15_forensic_sha256": V15_FORENSIC_SHA256,
        "preserved_v15_production_summary_sha256": V15_SUMMARY_SHA256,
        "independent_family_count": 3,
        "owned_source_count": 12,
        "owned_native_binary_count": 5,
        "original_method_count": ORIGINAL_METHODS,
        "original_public_method_count": PUBLIC_METHODS,
        "original_private_method_count": PRIVATE_METHODS,
        "public_method_waiver_count": 0,
        "named_private_class_waiver_count": 2,
        "named_private_debug_skip_kind": PRIVATE_DEBUG_SKIP_KIND,
        "actual_matching_guards_required_per_family": 13,
        "actual_native_loader_guards_required_per_family": 5,
        "genuine_pickle_checks_required_per_family": 16,
        "candidate_imports": 0,
        "subprocesses": 0,
        "file_reads": 0,
        "file_writes": 0,
        "clock_samples": 0,
        "historical_evidence_reads": 0,
        "actual_audit_report_reads": 0,
        "holdout_reads": 0,
        "synthetic_results_qualify_candidates": False,
        "blocked_effect_attempts": counts,
        "additional_forbidden_engine_import_attempts_blocked":
            extra["additional_forbidden_engine_imports_blocked"],
        "in_memory_publication_models_executed":
            extra["synthetic_publication_operations"],
        "kernel_descriptor_reuse_modeled": True,
        "role_tagged_descriptor_lifetime_events_required": 6,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--ownership-audit", action="store_true")
    modes.add_argument("--strict-audit", action="store_true")
    parser.add_argument("--base-report-sha256")
    parser.add_argument("--historical-v21-base-sha256")
    parser.add_argument("--historical-v21-strict-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(sys.argv[1:] if arguments is None else arguments)
    if options.self_test:
        require(options.base_report_sha256 is None
                and options.historical_v21_base_sha256 is None
                and options.historical_v21_strict_sha256 is None,
                "V23 source-only controls must never consume actual evidence pins")
        result = candidate_free_self_test()
    else:
        require(valid_sha256(options.historical_v21_base_sha256)
                and valid_sha256(options.historical_v21_strict_sha256),
                "V23 requires externally supplied historical V21 report pins")
        result = run_audit(
            strict=bool(options.strict_audit),
            historical_base_sha256=str(options.historical_v21_base_sha256),
            historical_strict_sha256=str(options.historical_v21_strict_sha256),
            base_report_sha256=options.base_report_sha256,
        )
    print(json.dumps(result, ensure_ascii=True, allow_nan=False,
                     sort_keys=True, separators=(",", ":")), flush=True)
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditV23Error, historical_v21.AuditV21Error,
            original_owner.AuditV10Error, original_strict.AuditV10Error,
            original_owner.source_v6.AuditV6Error,
            original_owner.core.AuditV3Error, v11.ProofV11Error,
            OSError, UnicodeError, ValueError, TypeError, KeyError) as error:
        failure: dict[str, Any] = {
            "schema": SCHEMA + "-actual-controller-failure",
            "status": "FAIL",
            "actual_error_type": type(error).__name__,
            "actual_error_message": str(error),
            "production_observations_invented": False,
            "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED",
        }
        if isinstance(error, AuditV23PublicationFailure):
            failure["schema"] = SCHEMA + "-actual-exclusive-publication-failure"
            failure["actual_exclusive_publication_receipt"] = error.receipt
        print(json.dumps(failure, ensure_ascii=True, allow_nan=False,
                         sort_keys=True, separators=(",", ":")),
              file=sys.stderr, flush=True)
        raise SystemExit(1) from error
