#!/usr/bin/env python3
"""Authenticate current native regexes against the actual frozen Python oracle.

Source-only controls open only six explicitly frozen V17, V18, and V19
public-oracle instruction files. The reference is the authentic V19
two-CPython report. No candidate can run before externally supplied current V21
audits and all twelve genuine V24 original archive-and-owner proofs pass.
"""

from __future__ import annotations

import argparse
import ast
import base64
import contextlib
import copy
import hashlib
import importlib
import json
import os
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import types
from typing import Any, Callable


ROOT = Path(os.path.abspath(__file__)).parent.parent
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

# Exactly the already frozen instruction modules; no candidate or evidence.
from tools import python_re_public_surface_oracle_stage17 as base17
from tools import python_re_public_surface_oracle_stage18 as base18
from tools import python_re_public_surface_oracle_stage19 as base19


SCHEMA = "rebar-python-re-current-native-public-surface-v27"
SOURCE_RELATIVE = "tools/python_re_public_surface_oracle_stage27.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-SURFACE-V27.md"

BASE17_SOURCE_RELATIVE = base19.V17_SOURCE_RELATIVE
BASE17_SOURCE_SHA256 = base19.V17_SOURCE_SHA256
BASE17_PROTOCOL_RELATIVE = base19.V17_PROTOCOL_RELATIVE
BASE17_PROTOCOL_SHA256 = base19.V17_PROTOCOL_SHA256
BASE18_SOURCE_RELATIVE = base19.V18_SOURCE_RELATIVE
BASE18_SOURCE_SHA256 = base19.V18_SOURCE_SHA256
BASE18_PROTOCOL_RELATIVE = base19.V18_PROTOCOL_RELATIVE
BASE18_PROTOCOL_SHA256 = base19.V18_PROTOCOL_SHA256
BASE19_SOURCE_RELATIVE = "tools/python_re_public_surface_oracle_stage19.py"
BASE19_SOURCE_SHA256 = (
    "fda386f3c00be660a41e92d8005fc287706d9dc050967cf2b708cb6f8aba113e"
)
BASE19_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-SURFACE-V19.md"
BASE19_PROTOCOL_SHA256 = (
    "53a415c7257222602ae69870c0e4343d85f77e1a2963f508d18d227038abc2ea"
)
BASE19_REFERENCE_RELATIVE = base19.SELF_ORACLE_RELATIVE
BASE19_REFERENCE_SHA256 = (
    "a2ac2853a6551b9eb95564ee74731c9e7d44998f5ec32ad5aac2259b5b313ad8"
)
BASE19_REFERENCE_RECORD_SHA256 = (
    "c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef"
)
BASE18_FAILURE_RELATIVE = base19.V18_HISTORICAL_FAILURE_RELATIVE
BASE18_FAILURE_SHA256 = base19.V18_HISTORICAL_FAILURE_SHA256
V13_FAILURE_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-FROM-SCRATCH-AUDIT-V13-HISTORICAL-GRAPH-"
    "PREFLIGHT-FAILURE.json"
)
V13_FAILURE_SHA256 = (
    "465820b50be4d544199844d7bde4c5b8e58391828bdb1c716cc33c50ca6c964b"
)
V13_FAILURE_SCHEMA = (
    "rebar-postfinal-independent-engine-audit-v13-actual-"
    "historical-graph-preflight-failure"
)

V13_FAILURE_ACTUAL_STAGE = (
    "historical-zig-edge-authentication-before-any-new-native-owner-worker"
)
V13_FAILED_OWNER_RELATIVE = "tools/postfinal_independent_engine_audit_v13.py"
V13_FAILED_OWNER_SHA256 = (
    "4570798942ab884c1a760b9685ef1a67379febd1c0da81aa18eef221126758fe"
)
V13_FAILED_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V13.md"
)
V13_FAILED_PROTOCOL_SHA256 = (
    "f325fe84dc4d14363e3dd4a6038866d8bc2aacd59625231f7dffc4c73257c0c3"
)
V13_FAILURE_ACTUAL_MESSAGE = "the ZIG native-bridge is stale or unproven"

V15_FAILURE_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-FROM-SCRATCH-AUDIT-V15-PRESERVED-FAILURE-"
    "CODEC-PREFLIGHT-FAILURE.json"
)
V15_FAILURE_SHA256 = (
    "a3695f1fd847e9ad882783d18c519b551d7791c5327f55964e202a31ade818ff"
)
V15_FAILURE_SCHEMA = (
    "rebar-postfinal-independent-engine-audit-v15-actual-"
    "preserved-failure-codec-preflight-failure"
)

V17_FAILURE_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-FROM-SCRATCH-AUDIT-V17-POST-OWNER-"
    "INTEGRITY-FAILURE.json"
)
V17_FAILURE_SHA256 = (
    "8aa1021ba4fc9dcb2456f05c174214c8c7f6c8f4fa2215a13c3373f00e5f557d"
)
V17_FAILURE_SCHEMA = (
    "rebar-postfinal-independent-engine-audit-v17-actual-"
    "post-owner-integrity-failure"
)

V19_FAILURE_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-FROM-SCRATCH-AUDIT-V19-PUBLICATION-FAILURE.json"
)
V19_FAILURE_SHA256 = (
    "6d4d73c153bcf1995db78fb4b90ce2851bdece3b13748c75ae045bd1081af390"
)
V19_FAILURE_SCHEMA = (
    "rebar-postfinal-independent-engine-audit-v19-actual-"
    "exclusive-publication-first-failure"
)
V19_FAILED_SOURCE_RELATIVE = "tools/postfinal_independent_engine_audit_v19.py"
V19_FAILED_SOURCE_SHA256 = (
    "f8f76365749d6893779756844424d1b3f5390bd37c3507f3b6655cce1390b1d6"
)
V19_FAILED_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V19.md"
)
V19_FAILED_PROTOCOL_SHA256 = (
    "78cd73d751caccb3458c709b2953e6c9cfc6c7a0edd8406b99d5aee36a9034e5"
)
V19_FAILED_EMBEDDED_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V19.json"
)
V19_FAILED_EMBEDDED_SHA256 = (
    "e46484d4a8b389fde66131ac3f8c2db94b1a95ebbf35760f1602117e8c9f23c6"
)
V19_FAILED_EMBEDDED_BYTES = 161_316

V22_FAILURE_RELATIVE = (
    "candidates/audits/"
    "POSTFINAL-CURRENT-BUILD-V22-READONLY-INTEGRATION-"
    "PREFLIGHT-FAILURE.json"
)
V22_FAILURE_SHA256 = (
    "c6e765f142f25667dd0e7dab45ff16a60abcaae6e230ba05acc596a72d304b01"
)
V22_FAILURE_SCHEMA = (
    "rebar-postfinal-current-build-proof-v22-actual-read-only-"
    "integration-preflight-failure"
)
V22_FAILED_SOURCE_RELATIVE = "tools/postfinal_current_build_proofs_v22.py"
V22_FAILED_SOURCE_SHA256 = (
    "ba3062b5fe4aea944e89022266c8d9a7a035708bb30d736f074fc29ce7157e27"
)
V22_FAILED_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V22.md"
)
V22_FAILED_PROTOCOL_SHA256 = (
    "e06a24155ca95bf287a5dece90d1a385dad806de8512f177d3146c7bba7acc29"
)

# Bind only exact corrected instruction hashes explicitly supplied by root.
# All produced owner report and original proof hashes remain runtime-only.
V21_SOURCE_RELATIVE = "tools/postfinal_independent_engine_audit_v21.py"
V21_SOURCE_SHA256 = (
    "ded077962416ada3bddd825d77b2e6785fe3b01184fe5d9058ec17a57b08ea4d"
)
V21_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V21.md"
)
V21_PROTOCOL_SHA256 = (
    "5a78673c6b23e4781070cf5a2290d5f6cecd402fff77ff388d8795370de93a1f"
)
V24_SOURCE_RELATIVE = "tools/postfinal_current_build_proofs_v24.py"
V24_SOURCE_SHA256 = (
    "92b1f082196592e578a5fa6e09b63637c6a1304c04875e5816938ed4fc28eb52"
)
V24_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V24.md"
V24_PROTOCOL_SHA256 = (
    "f3ab4f5c3c697a6d39c109b743d949b980bfe0d79aeb6b58a0bc392a3f81e534"
)
V21_BASE_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V21.json"
)
V21_STRICT_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V21.json"
)

FAMILIES = base19.FAMILIES
CONTRACT_NAMES = base19.CONTRACT_NAMES
MATRIX_SHA256 = base19.MATRIX_SHA256
STIMULUS_SHA256 = base19.STIMULUS_SHA256
EXPECTED_CASES = base19.EXPECTED_CASES
EXPECTED_COHORTS = base19.EXPECTED_COHORTS
EXPECTED_ADDITIONAL_CASES = base19.EXPECTED_ADDITIONAL_CASES
EXPECTED_LOCALE_CASES = base19.EXPECTED_LOCALE_CASES
EXPECTED_LOCALE_TRANSITIONS = base19.EXPECTED_LOCALE_TRANSITIONS
MAX_SOURCE_BYTES = base19.MAX_SOURCE_BYTES
MAX_REPORT_BYTES = base19.MAX_REPORT_BYTES
MAX_ARCHIVE_BYTES = base19.MAX_ARCHIVE_BYTES
MAX_WORKER_BYTES = base19.MAX_WORKER_BYTES

SELF_ORACLE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-surface-v27-self-oracle.json"
)
SELF_ORACLE_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-surface-v27-self-oracle-failures.json"
)
ALL_CANDIDATE_RELATIVE = (
    "candidates/evidence/python-re-public-surface-v27-all.json"
)
ALL_CANDIDATE_FAILURE_RELATIVE = (
    "candidates/evidence/python-re-public-surface-v27-all-failures.json"
)
CANDIDATE_FAILURE_RELATIVES = {
    family: (
        "candidates/evidence/python-re-public-surface-v27-"
        + family + "-failures.json"
    )
    for family in FAMILIES
}
APPROVED_OUTPUTS = frozenset({
    SELF_ORACLE_RELATIVE,
    SELF_ORACLE_FAILURE_RELATIVE,
    ALL_CANDIDATE_RELATIVE,
    ALL_CANDIDATE_FAILURE_RELATIVE,
    *CANDIDATE_FAILURE_RELATIVES.values(),
})

PRELOAD_MARKER = base19.PRELOAD_MARKER
AFTER_GUARD_MARKER = base19.AFTER_GUARD_MARKER
OWNER_RECORD_MARKER = base19.OWNER_RECORD_MARKER
PRELOAD_INJECTION = (
    "# BEGIN FROZEN V27 PRELOAD BEFORE CACHED-MATCHER POISON\n"
    "import os as _rebar27_os\n"
    "import json as _rebar27_json\n"
    "import importlib as _rebar27_importlib\n"
    "_rebar27_configuration = _rebar27_json.loads(\n"
    "    _rebar27_os.environ[\"REBAR_PUBLIC_SURFACE_V27_CONTEXT\"]\n"
    ")\n"
    "if any(_rebar27_name in sys.modules for _rebar27_name in (\n"
    "    \"candidates.rust_candidate\", \"candidates.vm_candidate\",\n"
    "    \"candidates.zig_candidate\",\n"
    ")):\n"
    "    raise RuntimeError(\"a candidate loaded before the current guard\")\n"
    "_rebar27_surface = _rebar27_importlib.import_module(\n"
    "    \"tools.python_re_public_surface_oracle_stage27\"\n"
    ")\n"
    "_rebar27_surface.verify_embedded_configuration(_rebar27_configuration)\n"
    "# END FROZEN V27 PRELOAD BEFORE CACHED-MATCHER POISON\n"
)
OBSERVATION_INJECTION = (
    "# BEGIN FROZEN V27 MATCHING INSIDE THE CURRENT NATIVE GUARD\n"
    "_rebar27_candidate_name = (\n"
    "    \"candidates.\" + _rebar27_configuration[\"family\"] + \"_candidate\"\n"
    ")\n"
    "_rebar27_candidate = sys.modules.get(_rebar27_candidate_name)\n"
    "if _rebar27_candidate is None:\n"
    "    raise RuntimeError(\"the real guarded candidate was not imported\")\n"
    "if getattr(_rebar27_candidate, \"__name__\", None) != "
    "_rebar27_candidate_name:\n"
    "    raise RuntimeError(\"the real guarded candidate was substituted\")\n"
    "try:\n"
    "    _rebar27_public_observation = "
    "_rebar27_surface.guarded_public_records(\n"
    "        _rebar27_candidate, _rebar27_configuration,\n"
    "    )\n"
    "except BaseException as _rebar27_actual_failure:\n"
    "    _rebar27_failure = _rebar27_surface.guarded_failure_document(\n"
    "        _rebar27_configuration[\"family\"], "
    "_rebar27_actual_failure,\n"
    "    )\n"
    "    sys.stderr.write(_rebar27_surface.canonical(\n"
    "        _rebar27_failure\n"
    "    ).decode(\"ascii\") + \"\\n\")\n"
    "    raise\n"
    "# END FROZEN V27 MATCHING INSIDE THE CURRENT NATIVE GUARD\n"
)
OWNER_RECORD_INJECTION = (
    '    "rebar_v27_guarded_public_surface": '
    '_rebar27_public_observation,\n'
)


class PublicSurfaceV27Error(base17.PublicSurfaceError):
    """A real frozen input, current graph, proof, or public worker failed."""


class PublicSurfaceV27WorkerFailure(PublicSurfaceV27Error):
    """Preserve genuine role, full streams, active rows, and guard details."""

    def __init__(self, role: str, message: str, details: Mapping[str, Any]):
        super().__init__(message)
        self.role = role
        self.details = dict(details)


class PublicSurfaceV27PublicationFailure(PublicSurfaceV27Error):
    """Preserve every actual syscall that happened before publication failed."""

    def __init__(self, message: str, receipt: Mapping[str, Any]):
        super().__init__(message)
        self.receipt = dict(receipt)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise PublicSurfaceV27Error(message)


def canonical(value: Any) -> bytes:
    return base19.canonical(value)


def digest(value: Any) -> str:
    return base19.digest(value)


def valid_sha256(value: Any) -> bool:
    return base19.valid_sha256(value)


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == str(base17.PINNED_PYTHON)
        and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
        and os.path.abspath(base19.__file__) == str(ROOT / BASE19_SOURCE_RELATIVE)
        and base19.SCHEMA == "rebar-python-re-cycle-safe-guarded-public-surface-v19"
        and base19.SOURCE_RELATIVE == BASE19_SOURCE_RELATIVE
        and base19.PROTOCOL_RELATIVE == BASE19_PROTOCOL_RELATIVE
        and base19.V17_SOURCE_SHA256 == BASE17_SOURCE_SHA256
        and base19.V18_SOURCE_SHA256 == BASE18_SOURCE_SHA256
        and base19.MATRIX_SHA256 == MATRIX_SHA256
        and base19.STIMULUS_SHA256 == STIMULUS_SHA256
        and base19.EXPECTED_CASES == EXPECTED_CASES
        and tuple(FAMILIES) == ("rust", "vm", "zig")
        and len(base17.COHORTS) == EXPECTED_COHORTS
        and BASE19_REFERENCE_SHA256 != BASE19_REFERENCE_RECORD_SHA256,
        "use the exact isolated CPython 3.14.6 and authentic frozen V19 oracle",
    )


def authenticate_frozen_instructions() -> None:
    verify_runtime()
    for relative, fingerprint in (
        (BASE17_SOURCE_RELATIVE, BASE17_SOURCE_SHA256),
        (BASE17_PROTOCOL_RELATIVE, BASE17_PROTOCOL_SHA256),
        (BASE18_SOURCE_RELATIVE, BASE18_SOURCE_SHA256),
        (BASE18_PROTOCOL_RELATIVE, BASE18_PROTOCOL_SHA256),
        (BASE19_SOURCE_RELATIVE, BASE19_SOURCE_SHA256),
        (BASE19_PROTOCOL_RELATIVE, BASE19_PROTOCOL_SHA256),
    ):
        base17._read_bounded(relative, MAX_SOURCE_BYTES, expected=fingerprint)


def safe_relative(relative: Any, *, outputs_only: bool = False) -> str:
    require(type(relative) is str, "an exact repository-relative path is required")
    value = PurePosixPath(relative)
    require(not value.is_absolute()
            and ".." not in value.parts
            and "\\" not in relative
            and "\x00" not in relative
            and value.as_posix() == relative
            and (not outputs_only or relative in APPROVED_OUTPUTS),
            "refusing an escaping, historical, reused, or unapproved output")
    return relative


def read_frozen(relative: str, expected: str, maximum: int) -> bytes:
    safe_relative(relative)
    require(valid_sha256(expected),
            "BLOCKED: supply an actual independently published SHA-256")
    return base17._read_bounded(relative, maximum, expected=expected)


def strict_canonical(raw: bytes, label: str) -> dict[str, Any]:
    try:
        return base19.strict_canonical(raw, label)
    except (base17.PublicSurfaceError, base18.PublicSurfaceV18Error,
            base19.PublicSurfaceV19Error, ValueError, UnicodeError) as error:
        raise PublicSurfaceV27Error(
            "the complete actual canonical JSON was forged: " + label,
        ) from error


def capture_complete_stream(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_WORKER_BYTES,
            "an actual original worker stream must be complete bounded bytes")
    return {
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "complete": True,
        "base64": base64.b64encode(raw).decode("ascii"),
    }


def restore_complete_stream(record: Any, *, label: str) -> bytes:
    require(isinstance(record, dict)
            and set(record) == {"bytes", "sha256", "complete", "base64"}
            and type(record.get("bytes")) is int
            and 0 <= record["bytes"] <= MAX_WORKER_BYTES
            and valid_sha256(record.get("sha256"))
            and record.get("complete") is True
            and type(record.get("base64")) is str,
            "a complete actual worker stream is missing: " + label)
    try:
        actual = base64.b64decode(record["base64"].encode("ascii"), validate=True)
    except (ValueError, UnicodeError, base64.binascii.Error) as error:
        raise PublicSurfaceV27Error(
            "the complete original worker stream was forged: " + label,
        ) from error
    require(len(actual) == record["bytes"]
            and hashlib.sha256(actual).hexdigest() == record["sha256"]
            and capture_complete_stream(actual) == record,
            "actual complete worker bytes changed: " + label)
    return actual


def validate_process_streams(
    process: Any,
    *,
    role: str,
    expected_document: Mapping[str, Any],
) -> dict[str, Any]:
    require(isinstance(process, dict)
            and set(process) == {"role", "returncode", "stdout", "stderr"}
            and process.get("role") == role
            and type(process.get("returncode")) is int
            and process["returncode"] == 0,
            "the actual independent current owner has an invalid exit code")
    stdout = restore_complete_stream(process.get("stdout"), label=role + " stdout")
    stderr = restore_complete_stream(process.get("stderr"), label=role + " stderr")
    require(stderr == b"", "a passing actual current owner concealed stderr")
    require(strict_canonical(stdout, role + " complete current stdout")
            == dict(expected_document),
            "the actual original stdout differs from the real owner report")
    return process


def build_matrix() -> list[dict[str, Any]]:
    matrix = base19.build_matrix()
    require(len(matrix) == EXPECTED_CASES
            and base17.validate_matrix(matrix, expected_sha256=MATRIX_SHA256)
            == MATRIX_SHA256,
            "an independently frozen actual public compatibility case changed")
    details = base17.validate_stimuli(matrix, expected_sha256=STIMULUS_SHA256)
    require(details.get("cases") == EXPECTED_CASES
            and details.get("cohorts") == EXPECTED_COHORTS
            and details.get("additional_cases") == EXPECTED_ADDITIONAL_CASES
            and details.get("distinct_stimuli") == EXPECTED_CASES,
            "the genuine frozen 43-by-32 public behavior was weakened")
    return matrix


def validate_public_records(records: Any) -> str:
    actual = base19.validate_public_records(records)
    require(valid_sha256(actual),
            "all original actual Python outcomes and expected errors are required")
    return actual


def error_details(error: BaseException) -> dict[str, Any]:
    return base19._error_details(error)


def verify_embedded_configuration(value: Any) -> dict[str, Any]:
    require(
        isinstance(value, dict)
        and set(value) == {
            "schema", "family", "source_sha256", "protocol_sha256",
            "baseline_v19_source_sha256", "baseline_v19_protocol_sha256",
            "v19_reference_sha256", "v19_record_sha256",
            "matrix_sha256", "stimulus_sha256", "cases",
            "iso8859_1_locale", "utf8_locale", "expected_native_sha256",
        }
        and value.get("schema") == SCHEMA + "-embedded-configuration"
        and value.get("family") in FAMILIES
        and valid_sha256(value.get("source_sha256"))
        and valid_sha256(value.get("protocol_sha256"))
        and value.get("baseline_v19_source_sha256") == BASE19_SOURCE_SHA256
        and value.get("baseline_v19_protocol_sha256") == BASE19_PROTOCOL_SHA256
        and value.get("v19_reference_sha256") == BASE19_REFERENCE_SHA256
        and value.get("v19_record_sha256") == BASE19_REFERENCE_RECORD_SHA256
        and value.get("matrix_sha256") == MATRIX_SHA256
        and value.get("stimulus_sha256") == STIMULUS_SHA256
        and value.get("cases") == EXPECTED_CASES
        and type(value.get("iso8859_1_locale")) is str
        and bool(value["iso8859_1_locale"])
        and type(value.get("utf8_locale")) is str
        and bool(value["utf8_locale"])
        and value["iso8859_1_locale"] != value["utf8_locale"]
        and isinstance(value.get("expected_native_sha256"), dict)
        and bool(value["expected_native_sha256"])
        and all(type(path) is str and valid_sha256(actual)
                for path, actual in value["expected_native_sha256"].items()),
        "the actual current same-process native owner configuration was forged",
    )
    return dict(value)


def compose_guarded_owner(
    owner_source: str,
    *,
    owner_source_sha256: str,
) -> tuple[str, str]:
    require(type(owner_source) is str
            and valid_sha256(owner_source_sha256)
            and hashlib.sha256(owner_source.encode("utf-8")).hexdigest()
            == owner_source_sha256,
            "the immutable original current-graph native owner was substituted")
    for marker, label in (
        (PRELOAD_MARKER, "before the original matcher guard"),
        (AFTER_GUARD_MARKER, "inside the original live matcher guard"),
        (OWNER_RECORD_MARKER, "inside the authentic complete owner report"),
    ):
        require(owner_source.count(marker) == 1,
                "the authentic current native owner lost its unique marker "
                + label)
    require(owner_source.index(PRELOAD_MARKER)
            < owner_source.index(AFTER_GUARD_MARKER)
            < owner_source.index(OWNER_RECORD_MARKER),
            "the authentic live native guard order was changed")
    try:
        original_tree = ast.parse(owner_source)
    except (SyntaxError, TypeError, ValueError) as error:
        raise PublicSurfaceV27Error(
            "the authentic current native owner source cannot be parsed",
        ) from error
    composed = owner_source.replace(
        PRELOAD_MARKER, PRELOAD_INJECTION + PRELOAD_MARKER, 1,
    ).replace(
        AFTER_GUARD_MARKER, OBSERVATION_INJECTION + AFTER_GUARD_MARKER, 1,
    ).replace(
        OWNER_RECORD_MARKER, OWNER_RECORD_INJECTION + OWNER_RECORD_MARKER, 1,
    )
    try:
        actual_tree = ast.parse(composed)
    except (SyntaxError, TypeError, ValueError) as error:
        raise PublicSurfaceV27Error(
            "the actual composed current guarded owner cannot be parsed",
        ) from error
    expected_imports = {
        alias.name
        for node in ast.walk(original_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    actual_imports = {
        alias.name
        for node in ast.walk(actual_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    require(actual_imports - expected_imports <= {"os", "json", "importlib"}
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in actual_imports - expected_imports)
            and composed.count(PRELOAD_INJECTION) == 1
            and composed.count(OBSERVATION_INJECTION) == 1
            and composed.count(OWNER_RECORD_INJECTION) == 1
            and composed.index(PRELOAD_INJECTION)
            < composed.index(PRELOAD_MARKER)
            and composed.index(OBSERVATION_INJECTION)
            < composed.index(AFTER_GUARD_MARKER)
            and composed.index(OWNER_RECORD_INJECTION)
            < composed.index(OWNER_RECORD_MARKER),
            "the real public observations escaped the current native guard")
    restored = composed.replace(
        PRELOAD_INJECTION + PRELOAD_MARKER, PRELOAD_MARKER, 1,
    ).replace(
        OBSERVATION_INJECTION + AFTER_GUARD_MARKER, AFTER_GUARD_MARKER, 1,
    ).replace(
        OWNER_RECORD_INJECTION + OWNER_RECORD_MARKER, OWNER_RECORD_MARKER, 1,
    )
    require(restored == owner_source
            and hashlib.sha256(restored.encode("utf-8")).hexdigest()
            == owner_source_sha256,
            "a genuine native guard or the immutable original owner changed")
    return composed, hashlib.sha256(composed.encode("utf-8")).hexdigest()


def guarded_failure_document(family: str, error: BaseException) -> dict[str, Any]:
    details = (
        dict(error.details)
        if isinstance(error, PublicSurfaceV27WorkerFailure)
        else {}
    )
    return {
        "schema": SCHEMA + "-embedded-public-failure",
        "status": "FAIL",
        "family": family,
        "actual_failure_details": details,
        **error_details(error),
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
    }


def _validate_locale_preflight(value: Any) -> None:
    require(isinstance(value, dict)
            and value.get("iso8859_1_codeset") in {"iso88591", "latin1"}
            and value.get("utf8_codeset") == "utf8"
            and value.get("ctype_restored") is True
            and value.get("locale_path_unchanged") is True,
            "actual independent restored ISO-8859-1 and UTF-8 are required")


def guarded_public_records(
    module: Any,
    configuration: Mapping[str, Any],
) -> dict[str, Any]:
    settings = verify_embedded_configuration(configuration)
    family = settings["family"]
    expected_name = "candidates." + family + "_candidate"
    require(getattr(module, "__name__", None) == expected_name
            and sys.modules.get(expected_name) is module,
            "use exclusively the actual candidate already loaded by its owner")
    authenticate_frozen_instructions()
    read_frozen(SOURCE_RELATIVE, settings["source_sha256"], MAX_SOURCE_BYTES)
    read_frozen(PROTOCOL_RELATIVE, settings["protocol_sha256"], MAX_SOURCE_BYTES)
    matrix = build_matrix()
    locale_names = {
        "iso8859_1": settings["iso8859_1_locale"],
        "utf8": settings["utf8_locale"],
    }
    completed: list[dict[str, Any]] = []
    active_case: str | None = None
    preflight: dict[str, Any] | None = None
    stage = "preflight"
    try:
        preflight = base17._preflight_real_locales(locale_names)
        _validate_locale_preflight(preflight)
        with base19.cycle_safe_normalization():
            for row in matrix:
                stage = "case"
                active_case = row["id"]
                observed = base17.evaluate_case(
                    module, row, locale_names=locale_names,
                )
                if row["cohort"] in {
                    "real-locale-switch-on-compiled-bytes",
                    "real-locale-invalid-flags-and-cache",
                }:
                    base17._validate_locale_case(observed)
                completed.append(observed)
                active_case = None
        stage = "postflight"
        counts = base19.validate_partial_records(completed, matrix)
        return {
            "schema": SCHEMA + "-embedded-public-records",
            "status": "PASS",
            "family": family,
            "candidate_module": expected_name,
            "source_sha256": settings["source_sha256"],
            "protocol_sha256": settings["protocol_sha256"],
            "baseline_v19_source_sha256": BASE19_SOURCE_SHA256,
            "baseline_v19_protocol_sha256": BASE19_PROTOCOL_SHA256,
            "v19_reference_sha256": BASE19_REFERENCE_SHA256,
            "v19_reference_record_sha256": BASE19_REFERENCE_RECORD_SHA256,
            "matrix_sha256": MATRIX_SHA256,
            "stimulus_sha256": STIMULUS_SHA256,
            "cases": EXPECTED_CASES,
            "retained_additional_cases": counts["additional_cases"],
            "returned_additional_cases": counts["returned_additional_cases"],
            "raised_additional_cases": counts["raised_additional_cases"],
            "successful_real_locale_cases": counts["real_locale_cases"],
            "real_locale_transition_count": EXPECTED_LOCALE_TRANSITIONS,
            "locale_preflight": preflight,
            "expected_native_sha256": settings["expected_native_sha256"],
            "records": completed,
            "record_sha256": validate_public_records(completed),
            "matched_inside_live_current_native_owner_guard": True,
            "candidate_imported_by_frozen_owner_only": True,
            "holdout_cases_read": 0,
            "performance_fixtures_read": 0,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }
    except BaseException as error:
        raise PublicSurfaceV27WorkerFailure(
            family,
            "the actual current candidate failed inside its live native guard",
            {
                "completed_records": completed,
                "completed_count": len(completed),
                "failure_stage": stage,
                "active_case": active_case,
                "locale_preflight": preflight,
                **error_details(error),
            },
        ) from error


def validate_embedded_records(
    document: Any,
    *,
    family: str,
    source_sha256: str,
    protocol_sha256: str,
    expected_native: Mapping[str, str],
    baseline: list[dict[str, Any]],
) -> dict[str, Any]:
    require(isinstance(document, dict)
            and document.get("schema") == SCHEMA + "-embedded-public-records"
            and document.get("status") == "PASS"
            and document.get("family") == family
            and document.get("candidate_module")
            == "candidates." + family + "_candidate"
            and document.get("source_sha256") == source_sha256
            and document.get("protocol_sha256") == protocol_sha256
            and document.get("baseline_v19_source_sha256") == BASE19_SOURCE_SHA256
            and document.get("baseline_v19_protocol_sha256") == BASE19_PROTOCOL_SHA256
            and document.get("v19_reference_sha256") == BASE19_REFERENCE_SHA256
            and document.get("v19_reference_record_sha256")
            == BASE19_REFERENCE_RECORD_SHA256
            and document.get("matrix_sha256") == MATRIX_SHA256
            and document.get("stimulus_sha256") == STIMULUS_SHA256
            and document.get("cases") == EXPECTED_CASES
            and document.get("retained_additional_cases")
            == EXPECTED_ADDITIONAL_CASES
            and type(document.get("returned_additional_cases")) is int
            and type(document.get("raised_additional_cases")) is int
            and document["returned_additional_cases"]
            + document["raised_additional_cases"] == EXPECTED_ADDITIONAL_CASES
            and document.get("successful_real_locale_cases")
            == EXPECTED_LOCALE_CASES
            and document.get("real_locale_transition_count")
            == EXPECTED_LOCALE_TRANSITIONS
            and document.get("expected_native_sha256") == dict(expected_native)
            and document.get("matched_inside_live_current_native_owner_guard")
            is True
            and document.get("candidate_imported_by_frozen_owner_only") is True
            and document.get("holdout_cases_read") == 0
            and document.get("performance_fixtures_read") == 0
            and document.get("benchmark_or_timing_executed") is False
            and document.get("performance") == "NOT MEASURED",
            "the genuine complete current same-process public record was forged")
    _validate_locale_preflight(document.get("locale_preflight"))
    records = document.get("records")
    require(validate_public_records(records) == document.get("record_sha256")
            and records == baseline,
            "the actual current native candidate differs from both Python oracles")
    counts = base19.validate_partial_records(records, build_matrix())
    require(counts["returned_additional_cases"]
            == document["returned_additional_cases"]
            and counts["raised_additional_cases"]
            == document["raised_additional_cases"],
            "actual expected Python errors were removed or replaced")
    return document


def authenticate_reference(
    source_sha256: str,
    protocol_sha256: str,
) -> dict[str, Any]:
    verify_runtime()
    read_frozen(SOURCE_RELATIVE, source_sha256, MAX_SOURCE_BYTES)
    read_frozen(PROTOCOL_RELATIVE, protocol_sha256, MAX_SOURCE_BYTES)
    authenticate_frozen_instructions()
    provenance = base19.authenticate_reference_prerequisites(
        BASE19_SOURCE_SHA256, BASE19_PROTOCOL_SHA256,
    )
    reference = base19.authenticate_surface_reference(
        provenance,
        source_sha256=BASE19_SOURCE_SHA256,
        protocol_sha256=BASE19_PROTOCOL_SHA256,
        reference_sha256=BASE19_REFERENCE_SHA256,
    )
    require(reference.get("v5_reference_sha256") == base17.V5_REFERENCE_SHA256
            and reference.get("reference_sha256") == BASE19_REFERENCE_SHA256
            and reference.get("record_sha256") == BASE19_REFERENCE_RECORD_SHA256
            and isinstance(reference.get("baseline_records"), list)
            and len(reference["baseline_records"]) == EXPECTED_CASES
            and validate_public_records(reference["baseline_records"])
            == BASE19_REFERENCE_RECORD_SHA256
            and provenance.get("candidate_audits_read") == 0
            and provenance.get("candidate_proofs_read") == 0
            and provenance.get("candidate_imports") == 0
            and provenance.get("v12_sources_read") == 0,
            "the complete actual V19 two-worker Python reference changed")
    return {
        "source_sha256": source_sha256,
        "protocol_sha256": protocol_sha256,
        "baseline_v19_source_sha256": BASE19_SOURCE_SHA256,
        "baseline_v19_protocol_sha256": BASE19_PROTOCOL_SHA256,
        "v19_reference_sha256": BASE19_REFERENCE_SHA256,
        "v19_reference_record_sha256": BASE19_REFERENCE_RECORD_SHA256,
        "baseline_records": reference["baseline_records"],
        "actual_independent_reference_count": 2,
        "fresh_reference_workers_started": 0,
        "cases": EXPECTED_CASES,
        "candidate_imports": 0,
        "candidate_audits_read": 0,
        "candidate_proofs_read": 0,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
    }


def import_frozen_validator(name: str, relative: str, fingerprint: str) -> Any:
    read_frozen(relative, fingerprint, MAX_SOURCE_BYTES)
    require(not any(key == "candidates" or key.startswith("candidates.")
                    for key in sys.modules),
            "a candidate imported before its current proof was authenticated")
    module = importlib.import_module(name)
    require(os.path.abspath(module.__file__) == str(ROOT / relative),
            "the exact real current native owner validator was substituted")
    read_frozen(relative, fingerprint, MAX_SOURCE_BYTES)
    require(not any(key == "candidates" or key.startswith("candidates.")
                    for key in sys.modules),
            "a current source validator imported a candidate too early")
    return module


def current_proof_pins(values: Mapping[str, Any]) -> dict[str, str]:
    names = {
        "v21_source", "v21_protocol", "v24_source", "v24_protocol",
        "v21_base_report", "v21_strict_report",
        *{
            family + "_" + kind
            for family in FAMILIES
            for kind in (
                "edge_archive", "edge_proof", "deep_archive", "deep_proof",
            )
        },
    }
    require(isinstance(values, Mapping)
            and set(values) == names
            and all(valid_sha256(values.get(name)) for name in names)
            and values.get("v21_source") == V21_SOURCE_SHA256
            and values.get("v21_protocol") == V21_PROTOCOL_SHA256
            and values.get("v24_source") == V24_SOURCE_SHA256
            and values.get("v24_protocol") == V24_PROTOCOL_SHA256
            and len({values[name] for name in names}) == len(names),
            "BLOCKED: independently publish both current V21 source/protocol "
            "and all-family audits, both actual V24 source/protocol identities, "
            "and every distinct qualified V24 original archive/owner proof")
    return {name: str(values[name]) for name in sorted(names)}


def validate_actual_v13_failure(summary: Any) -> dict[str, Any]:
    exact_fields = {
        "failure_path", "failure_sha256", "failure_schema", "status",
        "failed_stage", "actual_error_type", "actual_error_message",
        "actual_exit_code", "native_owner_workers_started",
        "original_edge_worker_started", "synthetic", "qualifies_current_engine",
        "v13_source_path", "v13_source_sha256", "v13_protocol_path",
        "v13_protocol_sha256", "stdout_capture", "stderr_capture",
        "combined_traceback_line_count",
        "combined_traceback_separately_captured", "fresh_ownership_report",
        "fresh_ownership_failure_report", "fresh_strict_report",
        "fresh_strict_failure_report", "performance", "holdout",
    }
    require(
        isinstance(summary, dict)
        and set(summary) == exact_fields
        and summary.get("failure_schema") == V13_FAILURE_SCHEMA
        and summary.get("failure_path") == V13_FAILURE_RELATIVE
        and summary.get("failure_sha256") == V13_FAILURE_SHA256
        and summary.get("status") == "FAIL"
        and summary.get("failed_stage") == V13_FAILURE_ACTUAL_STAGE
        and summary.get("actual_error_type") == "AssertionError"
        and summary.get("actual_error_message") == V13_FAILURE_ACTUAL_MESSAGE
        and type(summary.get("actual_exit_code")) is int
        and summary["actual_exit_code"] == 1
        and type(summary.get("native_owner_workers_started")) is int
        and summary["native_owner_workers_started"] == 0
        and summary.get("original_edge_worker_started") is False
        and summary.get("synthetic") is False
        and summary.get("qualifies_current_engine") is False
        and summary.get("v13_source_path") == V13_FAILED_OWNER_RELATIVE
        and summary.get("v13_source_sha256") == V13_FAILED_OWNER_SHA256
        and summary.get("v13_protocol_path") == V13_FAILED_PROTOCOL_RELATIVE
        and summary.get("v13_protocol_sha256") == V13_FAILED_PROTOCOL_SHA256
        and summary.get("stdout_capture") == "NOT CAPTURED"
        and summary.get("stderr_capture") == "NOT CAPTURED"
        and type(summary.get("combined_traceback_line_count")) is int
        and summary["combined_traceback_line_count"] == 34
        and summary.get("combined_traceback_separately_captured") is False
        and all(
            summary.get(field) == "NOT CREATED"
            for field in (
                "fresh_ownership_report", "fresh_ownership_failure_report",
                "fresh_strict_report", "fresh_strict_failure_report",
            )
        )
        and summary.get("performance") == "NOT MEASURED"
        and summary.get("holdout") == "NOT ACCESSED",
        "the authentic 26-field V13 pre-worker failure or its exact long "
        "historical-zig-edge stage was forged, shortened, or qualified",
    )
    return summary


def validate_actual_v15_failure(summary: Any) -> dict[str, Any]:
    expected_fields = {
        "failure_schema", "failure_path", "failure_sha256", "status",
        "failed_stage", "actual_error_type", "actual_error_message",
        "actual_exit_code", "native_owner_workers_started",
        "original_edge_worker_started", "synthetic", "qualifies_current_engine",
        "v15_source_path", "v15_source_sha256", "v15_protocol_path",
        "v15_protocol_sha256", "stdout_capture", "stderr_capture",
        "combined_traceback_line_count",
        "combined_traceback_separately_captured", "fresh_ownership_report",
        "fresh_ownership_failure_report", "fresh_strict_report",
        "fresh_strict_failure_report", "preserved_v13_first_failure_path",
        "preserved_v13_first_failure_sha256", "performance", "holdout",
    }
    require(
        isinstance(summary, dict)
        and set(summary) == expected_fields
        and summary.get("failure_schema") == V15_FAILURE_SCHEMA
        and summary.get("failure_path") == V15_FAILURE_RELATIVE
        and summary.get("failure_sha256") == V15_FAILURE_SHA256
        and summary.get("status") == "FAIL"
        and type(summary.get("actual_exit_code")) is int
        and summary["actual_exit_code"] == 1
        and type(summary.get("native_owner_workers_started")) is int
        and summary["native_owner_workers_started"] == 0
        and summary.get("original_edge_worker_started") is False
        and summary.get("synthetic") is False
        and summary.get("qualifies_current_engine") is False
        and summary.get("stdout_capture") == "NOT CAPTURED"
        and summary.get("stderr_capture") == "NOT CAPTURED"
        and type(summary.get("combined_traceback_line_count")) is int
        and summary["combined_traceback_line_count"] == 20
        and summary.get("combined_traceback_separately_captured") is False
        and summary.get("preserved_v13_first_failure_path")
        == V13_FAILURE_RELATIVE
        and summary.get("preserved_v13_first_failure_sha256")
        == V13_FAILURE_SHA256,
        "the genuine failed first V15 preserved-failure-codec preflight "
        "was concealed, synthesized, retroactively qualified, or replaced",
    )
    return summary


def validate_actual_v17_failure(summary: Any) -> dict[str, Any]:
    exact_fields = {
        "source_path", "sha256", "schema", "status", "exit_code",
        "failed_stage", "actual_error_type", "actual_error_message",
        "actual_completed_native_owner_families",
        "actual_native_owner_workers_completed",
        "actual_native_owner_observations",
        "actual_captured_combined_output_lines", "output_capture",
        "fresh_ownership_report", "fresh_ownership_failure_report",
        "fresh_strict_report", "fresh_strict_failure_report",
        "historical_failure_qualifies_current_build",
    }
    require(
        isinstance(summary, dict)
        and set(summary) == exact_fields
        and summary.get("source_path") == V17_FAILURE_RELATIVE
        and summary.get("sha256") == V17_FAILURE_SHA256
        and summary.get("schema") == V17_FAILURE_SCHEMA
        and summary.get("status") == "FAIL"
        and type(summary.get("exit_code")) is int
        and summary["exit_code"] == 1
        and summary.get("failed_stage")
        == (
            "unpreserved-static-graph-integrity-recheck-"
            "after-three-genuine-native-owner-workers"
        )
        and summary.get("actual_error_type")
        == "tools.postfinal_from_scratch_audit_v2.AuditV2Error"
        and summary.get("actual_error_message")
        == (
            "actual current 76-control source audit changed "
            "the immutable universal audit contract"
        )
        and type(summary.get("actual_completed_native_owner_families")) is list
        and summary["actual_completed_native_owner_families"] == list(FAMILIES)
        and type(summary.get("actual_native_owner_workers_completed")) is int
        and summary["actual_native_owner_workers_completed"] == 3
        and summary.get("actual_native_owner_observations")
        == "NOT PRESERVED BY THE FAILED CONTROLLER"
        and type(summary.get("actual_captured_combined_output_lines")) is int
        and summary["actual_captured_combined_output_lines"] == 27
        and summary.get("output_capture")
        == (
            "complete combined command output; stdout and stderr "
            "were not separately captured"
        )
        and all(
            summary.get(name) == "NOT CREATED"
            for name in (
                "fresh_ownership_report",
                "fresh_ownership_failure_report",
                "fresh_strict_report",
                "fresh_strict_failure_report",
            )
        )
        and summary.get("historical_failure_qualifies_current_build") is False,
        "the exact failed V17 post-owner integrity run, its three genuinely "
        "returned owners, its actual 27 merged lines, or its genuinely lost "
        "observations were concealed, synthesized, or marked as passing",
    )
    return summary


def validate_actual_v19_failure(summary: Any) -> dict[str, Any]:
    exact_fields = {
        "source_path", "sha256", "schema", "status", "exit_code",
        "invocation_count", "actual_error_message",
        "actual_inner_error_message", "v19_source_path", "v19_source_sha256",
        "v19_protocol_path", "v19_protocol_sha256", "durable_report_path",
        "durable_report_sha256", "durable_report_bytes",
        "durable_embedded_document_status", "actual_controller_status",
        "canonical_report_bytes_independently_verified",
        "embedded_pass_qualifies_current_engine",
        "historical_failure_qualifies_current_build",
        "completed_native_owner_worker_count",
        "complete_actual_native_owner_streams_preserved",
        "actual_original_native_owner_workers", "exclusive_create_succeeded",
        "actual_bytes_written", "file_fsync_succeeded",
        "parent_directory_fsync_succeeded", "canonical_reread_succeeded",
        "actual_write_calls", "original_non_roundtripping_in_memory_value",
        "fresh_v19_ownership_failure_report", "fresh_v19_strict_report",
        "fresh_v19_strict_failure_report", "strict_audit", "performance",
        "holdout",
    }
    require(
        isinstance(summary, dict)
        and set(summary) == exact_fields
        and summary.get("source_path") == V19_FAILURE_RELATIVE
        and summary.get("sha256") == V19_FAILURE_SHA256
        and summary.get("schema") == V19_FAILURE_SCHEMA
        and summary.get("status") == "FAIL"
        and type(summary.get("exit_code")) is int
        and summary["exit_code"] == 1
        and type(summary.get("invocation_count")) is int
        and summary["invocation_count"] == 1
        and summary.get("actual_error_message")
        == "the exclusive V19 publication failed; actual syscall receipt retained"
        and summary.get("actual_inner_error_message")
        == "an exact exclusively published V19 all-family report was changed"
        and summary.get("v19_source_path") == V19_FAILED_SOURCE_RELATIVE
        and summary.get("v19_source_sha256") == V19_FAILED_SOURCE_SHA256
        and summary.get("v19_protocol_path") == V19_FAILED_PROTOCOL_RELATIVE
        and summary.get("v19_protocol_sha256") == V19_FAILED_PROTOCOL_SHA256
        and summary.get("durable_report_path") == V19_FAILED_EMBEDDED_RELATIVE
        and summary.get("durable_report_sha256") == V19_FAILED_EMBEDDED_SHA256
        and type(summary.get("durable_report_bytes")) is int
        and summary["durable_report_bytes"] == V19_FAILED_EMBEDDED_BYTES
        and summary.get("durable_embedded_document_status") == "PASS"
        and summary.get("actual_controller_status") == "FAIL"
        and summary.get("canonical_report_bytes_independently_verified") is True
        and summary.get("embedded_pass_qualifies_current_engine") is False
        and summary.get("historical_failure_qualifies_current_build") is False
        and type(summary.get("completed_native_owner_worker_count")) is int
        and summary["completed_native_owner_worker_count"] == 3
        and summary.get("complete_actual_native_owner_streams_preserved") is True
        and isinstance(summary.get("actual_original_native_owner_workers"), dict)
        and set(summary["actual_original_native_owner_workers"]) == set(FAMILIES)
        and summary.get("exclusive_create_succeeded") is True
        and type(summary.get("actual_bytes_written")) is int
        and summary["actual_bytes_written"] == V19_FAILED_EMBEDDED_BYTES
        and summary.get("file_fsync_succeeded") is True
        and summary.get("parent_directory_fsync_succeeded") is True
        and summary.get("canonical_reread_succeeded") is False
        and summary.get("actual_write_calls") == [{
            "requested_bytes": V19_FAILED_EMBEDDED_BYTES,
            "returned_bytes": V19_FAILED_EMBEDDED_BYTES,
        }]
        and summary.get("original_non_roundtripping_in_memory_value")
        == "NOT PRESERVED BY THE FAILED CONTROLLER"
        and summary.get("fresh_v19_ownership_failure_report") is False
        and summary.get("fresh_v19_strict_report") is False
        and summary.get("fresh_v19_strict_failure_report") is False
        and summary.get("strict_audit") == "NOT RUN"
        and summary.get("performance") == "NOT MEASURED"
        and summary.get("holdout") == "NOT ACCESSED",
        "the genuine 161316-byte V19 embedded PASS, outer EXIT 1, complete "
        "three-owner transcripts, actual durable syscall receipt, or genuinely "
        "unstarted strict audit was concealed or retroactively qualified",
    )
    return summary


def validate_actual_v22_failure(
    summary: Any,
    pins: Mapping[str, str],
) -> dict[str, Any]:
    exact_fields = {
        "source_path", "sha256", "actual_combined_traceback_line_count",
        "actual_combined_traceback_lines", "actual_exception_message",
        "actual_exception_type", "actual_failed_invocation_boundary_counters",
        "actual_historical_summary_mismatch", "actual_invocation",
        "actual_passing_prerequisites", "attempted_family",
        "benchmark_or_timing_executed", "correctness_results_published",
        "failed_stage", "families_not_reached", "frozen_failed_controller",
        "holdout", "independent_follow_up_differential",
        "native_owner_workers_started", "original_deep_workers_started",
        "original_edge_workers_started", "performance",
        "production_observations_invented", "qualifies_current_engine",
        "schema", "status", "synthetic",
    }
    require(
        isinstance(pins, Mapping)
        and set(pins) == {
            "audit_source", "audit_protocol", "base_report", "strict_report",
        }
        and pins.get("audit_source") == V21_SOURCE_SHA256
        and pins.get("audit_protocol") == V21_PROTOCOL_SHA256
        and valid_sha256(pins.get("base_report"))
        and valid_sha256(pins.get("strict_report"))
        and pins.get("base_report") != pins.get("strict_report")
        and isinstance(summary, dict)
        and set(summary) == exact_fields
        and summary.get("source_path") == V22_FAILURE_RELATIVE
        and summary.get("sha256") == V22_FAILURE_SHA256
        and summary.get("schema") == V22_FAILURE_SCHEMA
        and summary.get("status") == "FAIL"
        and summary.get("synthetic") is False
        and summary.get("attempted_family") == "rust"
        and summary.get("failed_stage")
        == (
            "candidate-free authentication of the genuine historical V13 "
            "summary before the first original edge worker"
        )
        and summary.get("actual_exception_type")
        == "tools.postfinal_current_build_proofs_v22.ProofV22Error"
        and summary.get("actual_exception_message")
        == "the genuine original failed V13 first invocation was forged"
        and type(summary.get("actual_combined_traceback_line_count")) is int
        and summary["actual_combined_traceback_line_count"] == 24
        and isinstance(summary.get("actual_combined_traceback_lines"), list)
        and len(summary["actual_combined_traceback_lines"]) == 24
        and all(
            type(line) is str
            for line in summary["actual_combined_traceback_lines"]
        )
        and summary.get("actual_failed_invocation_boundary_counters")
        == "NOT PRESERVED BY THE FAILED CONTROLLER"
        and type(summary.get("native_owner_workers_started")) is int
        and summary["native_owner_workers_started"] == 0
        and type(summary.get("original_edge_workers_started")) is int
        and summary["original_edge_workers_started"] == 0
        and type(summary.get("original_deep_workers_started")) is int
        and summary["original_deep_workers_started"] == 0
        and summary.get("families_not_reached") == ["vm", "zig"]
        and summary.get("benchmark_or_timing_executed") is False
        and summary.get("correctness_results_published") is False
        and summary.get("production_observations_invented") is False
        and summary.get("qualifies_current_engine") is False
        and summary.get("performance") == "NOT MEASURED"
        and summary.get("holdout") == "NOT ACCESSED",
        "the exact fifth failed V22 proof preflight, its 24 real traceback "
        "lines, its 25 actual inline lines, or true zero workers was forged",
    )
    invocation = summary["actual_invocation"]
    require(
        isinstance(invocation, dict)
        and set(invocation) == {
            "actual_inline_python_source_lines", "environment", "executable",
            "exit_code", "output_capture", "python_flags",
        }
        and type(invocation.get("exit_code")) is int
        and invocation["exit_code"] == 1
        and invocation.get("python_flags") == ["-I", "-B", "-c"]
        and invocation.get("output_capture")
        == "complete combined traceback; stdout and stderr were not separately captured"
        and isinstance(invocation.get("actual_inline_python_source_lines"), list)
        and len(invocation["actual_inline_python_source_lines"]) == 25
        and all(
            type(line) is str
            for line in invocation["actual_inline_python_source_lines"]
        )
        and isinstance(invocation.get("environment"), dict)
        and set(invocation["environment"]) == {
            "LC_ALL", "PATH", "PYTHONDONTWRITEBYTECODE",
            "PYTHONHASHSEED", "PYTHONPATH",
        }
        and invocation["environment"].get("LC_ALL") == "C"
        and invocation["environment"].get("PYTHONDONTWRITEBYTECODE") == "1"
        and invocation["environment"].get("PYTHONHASHSEED") == "0"
        and type(invocation["environment"].get("PATH")) is str
        and bool(invocation["environment"]["PATH"])
        and type(invocation["environment"].get("PYTHONPATH")) is str
        and bool(invocation["environment"]["PYTHONPATH"])
        and invocation.get("executable") == str(base17.PINNED_PYTHON),
        "the exact fifth V22 real exit-one combined invocation was invented",
    )
    mismatch = summary["actual_historical_summary_mismatch"]
    require(
        isinstance(mismatch, dict)
        and set(mismatch) == {
            "historical_version", "field", "expected_field_count",
            "actual_authenticated_field_count", "missing_fields",
            "extra_fields", "v22_expected_value",
            "actual_authenticated_v21_value", "other_fields_match",
            "other_historical_summaries_exactly_match",
        }
        and mismatch.get("historical_version") == "v13"
        and mismatch.get("field") == "failed_stage"
        and type(mismatch.get("expected_field_count")) is int
        and mismatch["expected_field_count"] == 26
        and type(mismatch.get("actual_authenticated_field_count")) is int
        and mismatch["actual_authenticated_field_count"] == 26
        and mismatch.get("missing_fields") == []
        and mismatch.get("extra_fields") == []
        and mismatch.get("v22_expected_value") == "historical-zig-edge-preflight"
        and mismatch.get("actual_authenticated_v21_value")
        == V13_FAILURE_ACTUAL_STAGE
        and mismatch.get("other_fields_match") is True
        and mismatch.get("other_historical_summaries_exactly_match")
        == ["v15", "v17", "v19"],
        "the root-observed sole genuine long-stage V13 discrepancy was forged",
    )
    prior = summary["actual_passing_prerequisites"]
    require(
        isinstance(prior, dict)
        and set(prior) == {
            "audit_source_sha256", "audit_protocol_sha256", "base_report_path",
            "base_report_sha256", "strict_report_path", "strict_report_sha256",
            "both_independent_ownership_audits_passed",
        }
        and prior.get("audit_source_sha256") == pins["audit_source"]
        and prior.get("audit_protocol_sha256") == pins["audit_protocol"]
        and prior.get("base_report_path") == V21_BASE_REPORT_RELATIVE
        and prior.get("base_report_sha256") == pins["base_report"]
        and prior.get("strict_report_path") == V21_STRICT_REPORT_RELATIVE
        and prior.get("strict_report_sha256") == pins["strict_report"]
        and prior.get("both_independent_ownership_audits_passed") is True,
        "actual passing V21 evidence for the genuine fifth failure was replaced",
    )
    failed = summary["frozen_failed_controller"]
    require(
        isinstance(failed, dict)
        and set(failed) == {
            "source_path", "source_sha256", "protocol_path",
            "protocol_sha256",
        }
        and failed.get("source_path") == V22_FAILED_SOURCE_RELATIVE
        and failed.get("source_sha256") == V22_FAILED_SOURCE_SHA256
        and failed.get("protocol_path") == V22_FAILED_PROTOCOL_RELATIVE
        and failed.get("protocol_sha256") == V22_FAILED_PROTOCOL_SHA256,
        "the genuine historically failed V22 source or protocol was replaced",
    )
    followup = summary["independent_follow_up_differential"]
    require(
        isinstance(followup, dict)
        and set(followup) == {
            "read_only_boundary_effects", "status", "validation_scope",
        }
        and followup.get("status") == "PASS"
        and followup.get("validation_scope")
        == (
            "read-only authentication of the exact published V21 reports "
            "and all four historical summary shapes only"
        )
        and isinstance(followup.get("read_only_boundary_effects"), dict)
        and set(followup["read_only_boundary_effects"]) == {
            "candidate_imports", "clock_samples", "filesystem_writes",
            "native_workers_started", "subprocesses_started",
        }
        and all(
            type(value) is int and value == 0
            for value in followup["read_only_boundary_effects"].values()
        ),
        "the genuine candidate-free follow-up after the fifth failure changed",
    )
    return summary


def _proof_relative(path: Any) -> str:
    require(isinstance(path, Path)
            and path.is_absolute()
            and path.parent.parent.parent == ROOT,
            "a genuine exact current V24 proof target was redirected")
    return safe_relative(path.relative_to(ROOT).as_posix())


def validate_current_v24_descriptor(
    value: Any,
    *,
    family: str,
    kind: str,
    archive_relative: str,
    archive_sha256: str,
    proof_relative: str,
    proof_sha256: str,
    qualified_edge: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    common_fields = {
        "status", "campaign_qualified", "archive_path", "archive_sha256",
        "proof_path", "proof_sha256",
    }
    require(
        family in FAMILIES
        and kind in {"edge", "deep"}
        and safe_relative(archive_relative) == archive_relative
        and safe_relative(proof_relative) == proof_relative
        and valid_sha256(archive_sha256)
        and valid_sha256(proof_sha256)
        and archive_relative != proof_relative
        and archive_sha256 != proof_sha256
        and type(value) is dict
        and set(value) == (
            common_fields | ({"qualified_edge"} if kind == "deep" else set())
        )
        and value.get("status") == "PASS"
        and value.get("campaign_qualified") is True
        and value.get("archive_path") == archive_relative
        and value.get("archive_sha256") == archive_sha256
        and value.get("proof_path") == proof_relative
        and value.get("proof_sha256") == proof_sha256
        and (
            (
                kind == "edge"
                and qualified_edge is None
            )
            or (
                kind == "deep"
                and type(qualified_edge) is dict
                and set(qualified_edge) == common_fields
                and qualified_edge.get("status") == "PASS"
                and qualified_edge.get("campaign_qualified") is True
                and value.get("qualified_edge") == qualified_edge
            )
        ),
        "the exact authentic current V24 " + str(kind)
        + " original archive, durable proof, or edge-to-deep binding "
        + "was substituted for family " + str(family),
    )
    return dict(value)


def validate_current_v24_preflight_state(
    state: Any,
    *,
    family: str,
    v21: Any,
    audits: Mapping[str, Any],
    preserved_v22_failure: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    require(
        family in FAMILIES
        and isinstance(audits, Mapping)
        and {
            "owner",
            "pins",
            "graph",
            "preserved_v13_failure",
            "preserved_v15_failure",
            "preserved_v17_failure",
            "preserved_v19_failure",
        } <= set(audits)
        and audits.get("owner") is not None
        and isinstance(audits.get("pins"), Mapping)
        and isinstance(audits.get("graph"), Mapping)
        and isinstance(state, dict)
        and set(state) == {
            "v21", "owner", "v8", "audits", "snapshot", "history",
            "preserved_incidents", "controller", "parent_environment",
        }
        and state.get("v21") is v21
        and state.get("owner") is audits.get("owner")
        and isinstance(state.get("audits"), Mapping)
        and state["audits"].get("pins") == audits.get("pins")
        and state["audits"].get("graph") == audits.get("graph")
        and isinstance(state.get("snapshot"), Mapping)
        and state["snapshot"].get("family") == family
        and isinstance(state.get("history"), Mapping)
        and state["history"].get("preserved_v13_first_audit_failure")
        == audits.get("preserved_v13_failure")
        and state["history"].get("preserved_v15_first_audit_failure")
        == audits.get("preserved_v15_failure")
        and state["history"].get("preserved_v17_first_audit_failure")
        == audits.get("preserved_v17_failure")
        and state["history"].get("preserved_v19_first_audit_failure")
        == audits.get("preserved_v19_failure")
        and isinstance(state.get("preserved_incidents"), Mapping)
        and state["preserved_incidents"].get("v13_first_owner_preflight_failure")
        == audits.get("preserved_v13_failure")
        and state["preserved_incidents"].get(
            "v13_first_owner_preflight_failure_qualifies_current_engine",
        ) is False
        and state["preserved_incidents"].get("v15_first_owner_preflight_failure")
        == audits.get("preserved_v15_failure")
        and state["preserved_incidents"].get(
            "v15_first_owner_preflight_failure_qualifies_current_engine",
        ) is False
        and state["preserved_incidents"].get("v17_first_owner_postflight_failure")
        == audits.get("preserved_v17_failure")
        and state["preserved_incidents"].get(
            "v17_first_owner_postflight_failure_qualifies_current_engine",
        ) is False
        and state["preserved_incidents"].get(
            "v19_first_owner_publication_failure",
        ) == audits.get("preserved_v19_failure")
        and state["preserved_incidents"].get(
            "v19_first_owner_publication_failure_qualifies_current_engine",
        ) is False
        and state["preserved_incidents"].get(
            "v22_first_proof_preflight_failure_qualifies_current_engine",
        ) is False
        and state["preserved_incidents"].get(
            "historical_v10_graph_qualifies_current_engine",
        ) is False
        and (
            preserved_v22_failure is None
            or (
                isinstance(preserved_v22_failure, Mapping)
                and state["preserved_incidents"].get(
                    "v22_first_proof_preflight_failure",
                ) == preserved_v22_failure
            )
        )
        and not any(
            key == "candidates" or key.startswith("candidates.")
            for key in sys.modules
        ),
        "the exact nine-field current V24 family state, actual V21 owner "
        "and graph, or required genuine historical-failure subset was forged",
    )
    return state


def authenticate_current_v24_family(
    family: str,
    *,
    pins: Mapping[str, str],
    v21: Any,
    v24: Any,
    audits: Mapping[str, Any],
) -> dict[str, Any]:
    v24_pins = {
        "audit_source": pins["v21_source"],
        "audit_protocol": pins["v21_protocol"],
        "base_report": pins["v21_base_report"],
        "strict_report": pins["v21_strict_report"],
    }
    state = validate_current_v24_preflight_state(
        v24.preflight(family, v24_pins),
        family=family,
        v21=v21,
        audits=audits,
    )
    authenticated_fifth = v24.authenticate_v22_failure(v24_pins)
    validated_fifth = validate_actual_v22_failure(
        authenticated_fifth,
        v24_pins,
    )
    require(
        validated_fifth == authenticated_fifth
        and v24.expected_v22_failure_summary(v24_pins) == validated_fifth
        and validate_current_v24_preflight_state(
            state,
            family=family,
            v21=v21,
            audits=audits,
            preserved_v22_failure=validated_fifth,
        ) is state,
        "the genuine 27-field failed V22 integration or the root-observed "
        "authentic long 26-field V13 summary was forged",
    )
    edge_path = v24.edge_target(family, True)
    edge_proof_path = v24.edge_proof_target(family, True)
    deep_path = v24.deep_target(family, True)
    deep_proof_path = v24.deep_proof_target(family, True)
    edge_relative = _proof_relative(edge_path)
    edge_proof_relative = _proof_relative(edge_proof_path)
    deep_relative = _proof_relative(deep_path)
    deep_proof_relative = _proof_relative(deep_proof_path)
    original_edge = read_frozen(
        edge_relative, pins[family + "_edge_archive"], MAX_ARCHIVE_BYTES,
    )
    original_edge_proof = read_frozen(
        edge_proof_relative, pins[family + "_edge_proof"], MAX_ARCHIVE_BYTES,
    )
    original_deep = read_frozen(
        deep_relative, pins[family + "_deep_archive"], MAX_ARCHIVE_BYTES,
    )
    original_deep_proof = read_frozen(
        deep_proof_relative, pins[family + "_deep_proof"], MAX_ARCHIVE_BYTES,
    )
    contract = state["v8"].load_contract()
    edge_original, edge, edge_bytes, edge_proof_bytes = (
        v24.authenticate_qualified_edge(family, state, contract)
    )
    deep_original, deep, deep_bytes, deep_proof_bytes = (
        v24.authenticate_qualified_deep(family, state, contract)
    )
    edge = validate_current_v24_descriptor(
        edge,
        family=family,
        kind="edge",
        archive_relative=edge_relative,
        archive_sha256=pins[family + "_edge_archive"],
        proof_relative=edge_proof_relative,
        proof_sha256=pins[family + "_edge_proof"],
    )
    deep = validate_current_v24_descriptor(
        deep,
        family=family,
        kind="deep",
        archive_relative=deep_relative,
        archive_sha256=pins[family + "_deep_archive"],
        proof_relative=deep_proof_relative,
        proof_sha256=pins[family + "_deep_proof"],
        qualified_edge=edge,
    )
    require(isinstance(edge_original, Mapping)
            and isinstance(deep_original, Mapping)
            and isinstance(edge, Mapping)
            and isinstance(deep, Mapping)
            and edge_bytes == original_edge
            and edge_proof_bytes == original_edge_proof
            and deep_bytes == original_deep
            and deep_proof_bytes == original_deep_proof
            and edge.get("status") == "PASS"
            and edge.get("campaign_qualified") is True
            and edge.get("archive_path") == edge_relative
            and edge.get("archive_sha256") == pins[family + "_edge_archive"]
            and edge.get("proof_path") == edge_proof_relative
            and edge.get("proof_sha256") == pins[family + "_edge_proof"]
            and deep.get("status") == "PASS"
            and deep.get("campaign_qualified") is True
            and deep.get("archive_path") == deep_relative
            and deep.get("archive_sha256") == pins[family + "_deep_archive"]
            and deep.get("proof_path") == deep_proof_relative
            and deep.get("proof_sha256") == pins[family + "_deep_proof"]
            and deep_original.get("public_mismatch_count") == 0,
            "the actual complete current V24 223,198-edge or 393-deep "
            "archive-and-native-owner pair failed: " + family)
    require(not any(key == "candidates" or key.startswith("candidates.")
                    for key in sys.modules),
            "a candidate was imported before all current original proofs")
    return {
        "family": family,
        "snapshot": dict(state["snapshot"]),
        "edge": dict(edge),
        "deep": dict(deep),
        "full_edge_checks": 223_198,
        "full_edge_categories": 49,
        "full_deep_checks": 393,
        "full_deep_seeded_cases": 64,
    }


def authenticate_current_candidate_prerequisites(
    reference: Mapping[str, Any],
    supplied: Mapping[str, Any],
) -> dict[str, Any]:
    require(isinstance(reference, Mapping)
            and reference.get("v19_reference_sha256") == BASE19_REFERENCE_SHA256
            and reference.get("v19_reference_record_sha256")
            == BASE19_REFERENCE_RECORD_SHA256
            and isinstance(reference.get("baseline_records"), list)
            and len(reference["baseline_records"]) == EXPECTED_CASES
            and not any(key == "candidates" or key.startswith("candidates.")
                        for key in sys.modules),
            "authenticate the complete Python-only V19 oracle before any audit")
    pins = current_proof_pins(supplied)
    read_frozen(
        V21_PROTOCOL_RELATIVE, pins["v21_protocol"], MAX_SOURCE_BYTES,
    )
    v21 = import_frozen_validator(
        "tools.postfinal_independent_engine_audit_v21",
        V21_SOURCE_RELATIVE,
        pins["v21_source"],
    )
    require(
        callable(getattr(v21, "authenticate_qualified_audits", None))
        and callable(getattr(v21, "snapshot_current_graph", None))
        and callable(getattr(v21, "validate_native_owner", None))
        and callable(getattr(v21, "validate_v13_first_failure_summary", None))
        and callable(getattr(v21, "validate_v15_first_failure_summary", None))
        and callable(getattr(v21, "validate_v17_first_failure_summary", None))
        and callable(getattr(v21, "validate_v19_first_failure_summary", None)),
        "the immutable complete current V21 native-owner validator is absent",
    )
    audits = v21.authenticate_qualified_audits(
        pins["v21_base_report"], pins["v21_strict_report"],
    )
    require(
        isinstance(audits, dict)
        and set(audits) == {
            "base", "strict", "graph", "pins", "history",
            "preserved_zig_failure", "preserved_v13_failure",
            "preserved_v15_failure", "preserved_v17_failure",
            "preserved_v19_failure", "owner",
        }
        and isinstance(audits.get("graph"), Mapping)
        and isinstance(audits.get("pins"), Mapping)
        and isinstance(audits.get("history"), Mapping)
        and isinstance(audits.get("owner"), types.ModuleType),
        "both actual current all-family V21 native-owner audits are required",
    )
    preserved_v13 = audits["preserved_v13_failure"]
    validated_v13 = validate_actual_v13_failure(
        v21.validate_v13_first_failure_summary(preserved_v13),
    )
    require(
        validated_v13 == preserved_v13
        and audits["history"].get("preserved_v13_first_audit_failure")
        == preserved_v13,
        "the actual failed V13 owner preflight was retroactively qualified",
    )
    preserved_v15 = audits["preserved_v15_failure"]
    validated_v15 = validate_actual_v15_failure(
        v21.validate_v15_first_failure_summary(preserved_v15),
    )
    require(
        validated_v15 == preserved_v15
        and audits["history"].get("preserved_v15_first_audit_failure")
        == preserved_v15,
        "the actual failed first V15 preserved-failure-codec preflight "
        "was concealed or retroactively qualified",
    )
    preserved_v17 = audits["preserved_v17_failure"]
    validated_v17 = validate_actual_v17_failure(
        v21.validate_v17_first_failure_summary(preserved_v17),
    )
    require(
        validated_v17 == preserved_v17
        and audits["history"].get("preserved_v17_first_audit_failure")
        == preserved_v17,
        "the genuinely failed V17 post-owner integrity audit, its exact "
        "three returned owners, or its truly unpreserved observations "
        "were concealed or retroactively qualified",
    )
    preserved_v19 = audits["preserved_v19_failure"]
    validated_v19 = validate_actual_v19_failure(
        v21.validate_v19_first_failure_summary(preserved_v19),
    )
    require(
        validated_v19 == preserved_v19
        and audits["history"].get("preserved_v19_first_audit_failure")
        == preserved_v19,
        "the genuine failed V19 exclusive publisher, outer EXIT 1, "
        "internally passing e464 report, preserved native transcripts, "
        "or unstarted strict audit was retroactively qualified",
    )
    read_frozen(
        V24_PROTOCOL_RELATIVE, pins["v24_protocol"], MAX_SOURCE_BYTES,
    )
    v24 = import_frozen_validator(
        "tools.postfinal_current_build_proofs_v24",
        V24_SOURCE_RELATIVE,
        pins["v24_source"],
    )
    require(callable(getattr(v24, "preflight", None))
            and callable(getattr(v24, "edge_target", None))
            and callable(getattr(v24, "edge_proof_target", None))
            and callable(getattr(v24, "deep_target", None))
            and callable(getattr(v24, "deep_proof_target", None))
            and callable(getattr(v24, "authenticate_qualified_edge", None))
            and callable(getattr(v24, "authenticate_qualified_deep", None))
            and callable(getattr(v24, "authenticate_v22_failure", None))
            and callable(getattr(v24, "expected_v22_failure_summary", None))
            and callable(getattr(v24, "validate_v22_failure_document", None)),
            "the immutable complete current V24 original-suite owner is absent")
    completed = {
        family: authenticate_current_v24_family(
            family, pins=pins, v21=v21, v24=v24, audits=audits,
        )
        for family in FAMILIES
    }
    require(set(completed) == set(FAMILIES)
            and not any(key == "candidates" or key.startswith("candidates.")
                        for key in sys.modules),
            "all 12 current full original-suite and owner proofs must pass "
            "before importing a production candidate")
    return {
        "v21": v21,
        "v24": v24,
        "owner": audits["owner"],
        "audits": audits,
        "families": completed,
        "pins": pins,
    }


def _first_actual_public_mismatch(actual: Any, expected: Any) -> Any:
    return base19._first_actual_public_mismatch(actual, expected)


def capture_current_native_owner(
    family: str,
    *,
    expected_native: Mapping[str, str],
    phase: str,
    observe: Callable[[], Any],
    validate: Callable[[Any], Any],
) -> dict[str, dict[str, Any]]:
    require(
        family in FAMILIES
        and phase in {"before-matching", "after-matching"}
        and isinstance(expected_native, Mapping)
        and bool(expected_native)
        and all(
            type(path) is str and valid_sha256(fingerprint)
            for path, fingerprint in expected_native.items()
        ),
        "the true current native-owner observation context was substituted",
    )
    stage = "observe-current-native-owner-" + phase
    actual: Mapping[str, Any] | None = None
    try:
        observed = observe()
        require(
            isinstance(observed, Mapping),
            "the genuine current native owner returned no complete observation",
        )
        actual = dict(observed)
        stage = "validate-current-native-owner-" + phase
        validated = validate(observed)
        require(
            isinstance(validated, dict),
            "the genuine complete observed native owner did not validate",
        )
        return {
            "complete_original_observation": dict(actual),
            "validated_owner": dict(validated),
        }
    except BaseException as error:
        details: dict[str, Any] = {
            "role": family,
            "failure_stage": stage,
            "expected_native_sha256": dict(expected_native),
            "actual_native_owner_observation_preserved": actual is not None,
            **error_details(error),
        }
        if actual is not None:
            details["actual_native_owner_observation"] = dict(actual)
        raise PublicSurfaceV27WorkerFailure(
            family,
            "the genuine current native owner failed " + stage,
            details,
        ) from error


def validate_zero_exit_guarded_worker(
    family: str,
    *,
    retained_process: Mapping[str, Any],
    owner_before: Mapping[str, Any],
    owner_before_observation: Mapping[str, Any],
    composed_worker_sha256: str,
    expected_snapshot: Mapping[str, Any],
    baseline: list[dict[str, Any]],
    decode_owner: Callable[[bytes], Any],
    validate_owner_record: Callable[[Any], Any],
    validate_public_observations: Callable[[Any], Any],
    observe_snapshot: Callable[[], Any],
    observe_owner_after: Callable[[], Any],
    validate_owner_after: Callable[[Any], Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    stage = "decode-owner-report"
    original_report: Mapping[str, Any] | None = None
    original_public: Mapping[str, Any] | None = None
    actual_snapshot: Mapping[str, Any] | None = None
    actual_after: Mapping[str, Any] | None = None
    try:
        require(isinstance(retained_process, Mapping)
                and retained_process.get("role") == family
                and type(retained_process.get("returncode")) is int
                and retained_process.get("returncode") == 0,
                "an actual current native owner did not genuinely return zero")
        stdout = restore_complete_stream(
            retained_process.get("stdout"),
            label=family + " complete zero-exit owner stdout",
        )
        restore_complete_stream(
            retained_process.get("stderr"),
            label=family + " complete zero-exit owner stderr",
        )
        decoded = decode_owner(stdout)
        require(isinstance(decoded, dict),
                "the genuine zero-exit owner returned no complete document")
        original_report = decoded
        embedded = decoded.get("rebar_v27_guarded_public_surface")
        if isinstance(embedded, Mapping):
            original_public = embedded

        stage = "validate-augmented-native-owner"
        validate_owner_record(decoded)
        stage = "validate-complete-public-observations"
        observations = validate_public_observations(embedded)
        require(isinstance(observations, dict),
                "complete actual public candidate observations were omitted")
        stage = "validate-complete-original-worker-streams"
        validate_process_streams(
            retained_process, role=family, expected_document=decoded,
        )
        stage = "validate-unmodified-original-native-owner"
        original = dict(decoded)
        original.pop("rebar_v27_guarded_public_surface", None)
        validate_owner_record(original)

        stage = "validate-current-native-snapshot-after-matching"
        current_snapshot = observe_snapshot()
        if isinstance(current_snapshot, Mapping):
            actual_snapshot = current_snapshot
        require(current_snapshot == expected_snapshot,
                "the actual owned source or native ELF changed during matching")
        stage = "observe-current-native-owner-after-matching"
        after_observation = observe_owner_after()
        if isinstance(after_observation, Mapping):
            actual_after = after_observation
        stage = "validate-current-native-owner-after-matching"
        after = validate_owner_after(after_observation)
        require(isinstance(after, dict),
                "the actual independently guarded owner-after result is absent")
        actual_after = after
        stage = "validate-final-current-native-snapshot"
        final_snapshot = observe_snapshot()
        if isinstance(final_snapshot, Mapping):
            actual_snapshot = final_snapshot
        require(final_snapshot == expected_snapshot,
                "the actual current native graph changed after public matching")
        return decoded, observations, after
    except BaseException as error:
        details: dict[str, Any] = {
            "role": family,
            "returncode": retained_process.get("returncode"),
            "stdout": retained_process.get("stdout"),
            "stderr": retained_process.get("stderr"),
            "complete_original_worker_streams": dict(retained_process),
            "owner_before": dict(owner_before),
            "complete_original_owner_before_observation": dict(
                owner_before_observation,
            ),
            "composed_worker_sha256": composed_worker_sha256,
            "failure_stage": stage,
            **error_details(error),
        }
        if original_report is not None:
            details["actual_decoded_owner_report"] = original_report
        if original_public is not None:
            details["actual_embedded_public_observations"] = original_public
            records = original_public.get("records")
            if isinstance(records, list):
                details["completed_records"] = records
                details["completed_count"] = len(records)
                mismatch = _first_actual_public_mismatch(records, baseline)
                if mismatch is not None:
                    details["first_actual_public_mismatch"] = mismatch
        if actual_snapshot is not None:
            details["actual_observed_family_snapshot"] = actual_snapshot
        if actual_after is not None:
            details["actual_observed_owner_after"] = actual_after
        raise PublicSurfaceV27WorkerFailure(
            family,
            "the complete current zero-exit native owner failed " + stage,
            details,
        ) from error


def _locale_names(options: argparse.Namespace) -> dict[str, str]:
    require(type(options.iso8859_1_locale) is str
            and bool(options.iso8859_1_locale)
            and type(options.utf8_locale) is str
            and bool(options.utf8_locale)
            and options.iso8859_1_locale != options.utf8_locale,
            "BLOCKED: provide genuine distinct fresh ISO-8859-1/UTF-8 locales")
    return {"iso8859_1": options.iso8859_1_locale,
            "utf8": options.utf8_locale}


class _RealPublicationOperations:
    """Actual descriptor-relative syscalls; never used by source controls."""

    @staticmethod
    def open_directory(path: Path) -> int:
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        return os.open(path, flags)

    @staticmethod
    def verify_directory(descriptor: int, path: Path) -> bool:
        opened = os.fstat(descriptor)
        current = os.stat(path, follow_symlinks=False)
        return (
            stat.S_ISDIR(opened.st_mode)
            and stat.S_ISDIR(current.st_mode)
            and (opened.st_dev, opened.st_ino)
            == (current.st_dev, current.st_ino)
        )

    @staticmethod
    def create_leaf(directory: int, name: str) -> int:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        return os.open(name, flags, 0o600, dir_fd=directory)

    @staticmethod
    def write_file(descriptor: int, payload: memoryview) -> int:
        return os.write(descriptor, payload)

    @staticmethod
    def open_readback(directory: int, name: str) -> int:
        flags = os.O_RDONLY
        flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        return os.open(name, flags, dir_fd=directory)

    @staticmethod
    def read_file(descriptor: int, maximum: int) -> bytes:
        return os.read(descriptor, maximum)

    @staticmethod
    def sync(descriptor: int) -> None:
        os.fsync(descriptor)

    @staticmethod
    def close(descriptor: int) -> None:
        os.close(descriptor)


def publish_with_receipt(
    document: Mapping[str, Any],
    relative: str,
    *,
    operations: Any | None = None,
) -> dict[str, Any]:
    """Record each real open/create/write/file-sync/directory-sync boundary."""
    relative = safe_relative(relative, outputs_only=True)
    target = ROOT / relative
    payload = canonical(document) + b"\n"
    require(0 < len(payload) <= MAX_REPORT_BYTES,
            "complete real correctness evidence exceeds its safe size")
    actual = operations if operations is not None else _RealPublicationOperations()
    receipt: dict[str, Any] = {
        "path": relative,
        "expected_bytes": len(payload),
        "expected_sha256": hashlib.sha256(payload).hexdigest(),
        "directory_opened": False,
        "directory_identity_verified": False,
        "file_created": False,
        "actual_write_calls": [],
        "bytes_written": 0,
        "file_fsync_completed": False,
        "directory_fsync_completed": False,
        "file_closed": False,
        "readback_opened": False,
        "readback_bytes": 0,
        "readback_sha256": None,
        "readback_exact_bytes_verified": False,
        "readback_canonical_document_verified": False,
        "readback_closed": False,
        "directory_closed": False,
        "fully_published": False,
        "exclusive_creation": True,
        "no_symlink_followed": True,
    }
    directory: int | None = None
    descriptor: int | None = None
    readback: int | None = None
    try:
        directory = actual.open_directory(target.parent)
        require(type(directory) is int and directory >= 0,
                "the true current evidence directory was not opened")
        receipt["directory_opened"] = True
        require(actual.verify_directory(directory, target.parent) is True,
                "the original current evidence directory identity changed")
        receipt["directory_identity_verified"] = True
        descriptor = actual.create_leaf(directory, target.name)
        require(type(descriptor) is int and descriptor >= 0,
                "the exclusive current evidence leaf was not created")
        # Record creation immediately, before any write or later failing call.
        receipt["file_created"] = True
        remaining = memoryview(payload)
        while remaining:
            attempt = {
                "requested_bytes": len(remaining),
                "returned_bytes": None,
            }
            receipt["actual_write_calls"].append(attempt)
            count = actual.write_file(descriptor, remaining)
            attempt["returned_bytes"] = count
            require(
                type(count) is int
                and 0 < count <= attempt["requested_bytes"],
                "the actual exclusive current evidence write returned "
                "an invalid byte count",
            )
            receipt["bytes_written"] += count
            remaining = remaining[count:]
        require(receipt["bytes_written"] == len(payload),
                "the real current proof was truncated")
        actual.sync(descriptor)
        receipt["file_fsync_completed"] = True
        actual.close(descriptor)
        descriptor = None
        receipt["file_closed"] = True
        actual.sync(directory)
        receipt["directory_fsync_completed"] = True

        readback = actual.open_readback(directory, target.name)
        require(
            type(readback) is int and readback >= 0,
            "the actual no-follow published evidence could not be reopened",
        )
        receipt["readback_opened"] = True
        retained = bytearray()
        while True:
            maximum = min(
                65_536,
                max(1, len(payload) + 1 - receipt["readback_bytes"]),
            )
            chunk = actual.read_file(readback, maximum)
            require(
                type(chunk) is bytes and len(chunk) <= maximum,
                "the actual exclusive publication readback was substituted",
            )
            if not chunk:
                break
            retained.extend(chunk)
            receipt["readback_bytes"] += len(chunk)
            require(
                receipt["readback_bytes"] <= len(payload),
                "the actual durable exclusive report returned excess bytes",
            )
        observed = bytes(retained)
        receipt["readback_sha256"] = hashlib.sha256(observed).hexdigest()
        require(
            observed == payload
            and receipt["readback_sha256"] == receipt["expected_sha256"],
            "the actual exclusive publication did not preserve canonical bytes",
        )
        receipt["readback_exact_bytes_verified"] = True
        require(
            observed.endswith(b"\n")
            and observed.count(b"\n") == 1,
            "the canonical current evidence lost its exact newline boundary",
        )
        decoded = strict_canonical(
            observed[:-1],
            "actual normalized V27 descriptor-relative publication readback",
        )
        require(
            canonical(decoded) + b"\n" == observed,
            "the canonical durable report failed its JSON-normalized readback",
        )
        receipt["readback_canonical_document_verified"] = True
        actual.close(readback)
        readback = None
        receipt["readback_closed"] = True
        actual.close(directory)
        directory = None
        receipt["directory_closed"] = True
        receipt["fully_published"] = True
        return receipt
    except BaseException as error:
        if readback is not None:
            try:
                actual.close(readback)
                receipt["readback_closed"] = True
            except BaseException as close_error:
                receipt["actual_readback_close_error"] = error_details(
                    close_error,
                )
        if descriptor is not None:
            try:
                actual.close(descriptor)
                receipt["file_closed"] = True
            except BaseException as close_error:
                receipt["actual_file_close_error"] = error_details(close_error)
        if directory is not None:
            try:
                actual.close(directory)
                receipt["directory_closed"] = True
            except BaseException as close_error:
                receipt["actual_directory_close_error"] = error_details(
                    close_error,
                )
        receipt.update(error_details(error))
        raise PublicSurfaceV27PublicationFailure(
            "the real current correctness report failed exclusive publication",
            receipt,
        ) from error


def preflight_outputs(relatives: tuple[str, ...]) -> None:
    require(len(relatives) == len(set(relatives)),
            "true passing and failed current reports must be independent")
    for relative in relatives:
        path = ROOT / safe_relative(relative, outputs_only=True)
        require(path.parent.is_dir()
                and not path.parent.is_symlink()
                and path.resolve(strict=False) == path
                and not path.exists()
                and not path.is_symlink(),
                "refusing a reused, replaced, or redirected current report: "
                + relative)


def run_self_oracle(options: argparse.Namespace) -> dict[str, Any]:
    reference = authenticate_reference(
        options.source_sha256, options.protocol_sha256,
    )
    preflight_outputs((SELF_ORACLE_RELATIVE, SELF_ORACLE_FAILURE_RELATIVE))
    try:
        result = {
            "schema": SCHEMA + "-self-oracle",
            "status": "PASS",
            "synthetic": False,
            "python": "3.14.6",
            "source_path": SOURCE_RELATIVE,
            "source_sha256": options.source_sha256,
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": options.protocol_sha256,
            "baseline_v19_source_sha256": BASE19_SOURCE_SHA256,
            "baseline_v19_protocol_sha256": BASE19_PROTOCOL_SHA256,
            "v19_actual_reference_path": BASE19_REFERENCE_RELATIVE,
            "v19_actual_reference_sha256": BASE19_REFERENCE_SHA256,
            "record_sha256": BASE19_REFERENCE_RECORD_SHA256,
            "actual_independent_reference_count": 2,
            "fresh_reference_workers_started": 0,
            "matrix_sha256": MATRIX_SHA256,
            "stimulus_sha256": STIMULUS_SHA256,
            "cohorts": EXPECTED_COHORTS,
            "cases": EXPECTED_CASES,
            "additional_cases": EXPECTED_ADDITIONAL_CASES,
            "real_locale_cases_per_reference": EXPECTED_LOCALE_CASES,
            "real_locale_transitions_per_reference": EXPECTED_LOCALE_TRANSITIONS,
            "candidate_audits_read": 0,
            "candidate_proofs_read": 0,
            "candidate_imports": 0,
            "preserved_v18_failure_path": BASE18_FAILURE_RELATIVE,
            "preserved_v18_failure_sha256": BASE18_FAILURE_SHA256,
            "historical_failure_qualifies_current_build": False,
            "holdout_cases_read": 0,
            "performance_fixtures_read": 0,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }
        receipt = publish_with_receipt(result, SELF_ORACLE_RELATIVE)
        require(receipt.get("fully_published") is True,
                "the actual authentic Python-only reference was not durable")
        return result
    except BaseException as error:
        failure = {
            "schema": SCHEMA + "-self-oracle-failure",
            "status": "FAIL",
            "synthetic": False,
            "source_path": SOURCE_RELATIVE,
            "protocol_path": PROTOCOL_RELATIVE,
            "v19_reference_sha256": BASE19_REFERENCE_SHA256,
            **error_details(error),
            "candidate_imports": 0,
            "candidate_audits_read": 0,
            "candidate_proofs_read": 0,
            "holdout_cases_read": 0,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }
        if isinstance(error, PublicSurfaceV27PublicationFailure):
            failure["actual_partial_publication_receipt"] = error.receipt
        publish_with_receipt(failure, SELF_ORACLE_FAILURE_RELATIVE)
        raise


def _candidate_configuration(
    family: str,
    *,
    source_sha256: str,
    protocol_sha256: str,
    locales: Mapping[str, str],
    expected_native: Mapping[str, str],
) -> dict[str, Any]:
    return verify_embedded_configuration({
        "schema": SCHEMA + "-embedded-configuration",
        "family": family,
        "source_sha256": source_sha256,
        "protocol_sha256": protocol_sha256,
        "baseline_v19_source_sha256": BASE19_SOURCE_SHA256,
        "baseline_v19_protocol_sha256": BASE19_PROTOCOL_SHA256,
        "v19_reference_sha256": BASE19_REFERENCE_SHA256,
        "v19_record_sha256": BASE19_REFERENCE_RECORD_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "stimulus_sha256": STIMULUS_SHA256,
        "cases": EXPECTED_CASES,
        "iso8859_1_locale": locales["iso8859_1"],
        "utf8_locale": locales["utf8"],
        "expected_native_sha256": dict(expected_native),
    })


def _decode_guarded_stderr(raw: bytes, family: str) -> dict[str, Any] | None:
    if not raw:
        return None
    try:
        result = strict_canonical(raw.split(b"\n", 1)[0], family + " failure")
    except (PublicSurfaceV27Error, base17.PublicSurfaceError, ValueError,
            UnicodeError, TypeError):
        return None
    require(result.get("schema") == SCHEMA + "-embedded-public-failure"
            and result.get("status") == "FAIL"
            and result.get("family") == family,
            "the actual real guarded native failure was substituted")
    return result


def _timeout_failure_details(
    role: str,
    error: subprocess.TimeoutExpired,
    *,
    owner_before: Mapping[str, Any] | None = None,
    owner_before_observation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    details: dict[str, Any] = {
        "role": role,
        "timed_out": True,
        "timeout_seconds": error.timeout,
        "returncode": None,
        **error_details(error),
    }
    for label in ("stdout", "stderr"):
        raw = getattr(error, label, None)
        if raw is None:
            details[label] = None
            continue
        require(type(raw) is bytes,
                "the current timed-out native process changed its " + label)
        observed = capture_complete_stream(raw)
        observed["complete"] = False
        observed["captured_before_timeout"] = True
        details[label] = observed
    if owner_before is not None:
        details["owner_before"] = dict(owner_before)
    if owner_before_observation is not None:
        details["complete_original_owner_before_observation"] = dict(
            owner_before_observation,
        )
    return details


def run_guarded_candidate(
    family: str,
    *,
    source_sha256: str,
    protocol_sha256: str,
    locales: Mapping[str, str],
    current: Mapping[str, Any],
    baseline: list[dict[str, Any]],
) -> dict[str, Any]:
    owner = current["owner"]
    v21 = current["v21"]
    state = current["families"][family]
    snapshot = state["snapshot"]
    expected_native = snapshot["native_sha256_by_path"]
    before_capture = capture_current_native_owner(
        family,
        expected_native=expected_native,
        phase="before-matching",
        observe=lambda: v21.run_native_worker(
            family, dict(expected_native),
        ),
        validate=lambda observed: v21.validate_native_owner(
            observed, family, dict(expected_native),
        ),
    )
    before_observation = before_capture["complete_original_observation"]
    before = before_capture["validated_owner"]
    original = owner.NATIVE_OWNER_WORKER
    original_hash = owner.NATIVE_OWNER_WORKER_SHA256
    owner.validate_worker_source(original)
    composed, composed_hash = compose_guarded_owner(
        original, owner_source_sha256=original_hash,
    )
    owner.validate_worker_source(composed)
    configuration = _candidate_configuration(
        family,
        source_sha256=source_sha256,
        protocol_sha256=protocol_sha256,
        locales=locales,
        expected_native=expected_native,
    )
    environment = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "LC_ALL": "C",
        "PATH": "/usr/bin:/bin",
        "REBAR_PUBLIC_SURFACE_V27_CONTEXT": canonical(configuration).decode(
            "ascii",
        ),
    }
    if "LOCPATH" in os.environ:
        environment["LOCPATH"] = os.environ["LOCPATH"]
    arguments = [
        str(base17.PINNED_PYTHON), "-I", "-B", "-c", composed,
        str(ROOT), family, canonical(dict(expected_native)).decode("ascii"),
    ]
    try:
        child = subprocess.run(
            arguments,
            cwd=str(ROOT),
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=3_600,
        )
    except subprocess.TimeoutExpired as error:
        raise PublicSurfaceV27WorkerFailure(
            family,
            "the genuine same-process current native guard timed out",
            _timeout_failure_details(
                family,
                error,
                owner_before=before,
                owner_before_observation=before_observation,
            ),
        ) from error
    except (OSError, subprocess.SubprocessError) as error:
        raise PublicSurfaceV27WorkerFailure(
            family,
            "the genuine same-process current native guard crashed",
            {
                "owner_before": before,
                "complete_original_owner_before_observation":
                    before_observation,
                **error_details(error),
            },
        ) from error
    require(len(child.stdout) <= MAX_WORKER_BYTES
            and len(child.stderr) <= MAX_WORKER_BYTES,
            "the genuine current owner returned oversized original streams")
    process = {
        "role": family,
        "returncode": child.returncode,
        "stdout": capture_complete_stream(child.stdout),
        "stderr": capture_complete_stream(child.stderr),
    }
    if child.returncode != 0 or not child.stdout or child.stderr:
        details: dict[str, Any] = {
            "role": family,
            "returncode": child.returncode,
            "stdout": process["stdout"],
            "stderr": process["stderr"],
            "complete_original_worker_streams": process,
            "owner_before": before,
            "complete_original_owner_before_observation": before_observation,
            "composed_worker_sha256": composed_hash,
        }
        try:
            inner = _decode_guarded_stderr(child.stderr, family)
        except BaseException as decode_error:
            inner = None
            details["actual_failure_decode_error"] = error_details(decode_error)
        if inner is not None:
            details["actual_guarded_failure"] = inner
            partial = inner.get("actual_failure_details")
            if isinstance(partial, dict):
                for field in (
                    "completed_records", "completed_count", "failure_stage",
                    "active_case", "locale_preflight", "actual_error",
                    "traceback",
                ):
                    if field in partial:
                        details[field] = partial[field]
        raise PublicSurfaceV27WorkerFailure(
            family,
            "the genuine complete current guarded native owner failed",
            details,
        )
    report, observations, after = validate_zero_exit_guarded_worker(
        family,
        retained_process=process,
        owner_before=before,
        owner_before_observation=before_observation,
        composed_worker_sha256=composed_hash,
        expected_snapshot=snapshot,
        baseline=baseline,
        decode_owner=lambda payload: owner.core.decode_report(
            payload,
            label="complete V27 observations inside the current native guard",
        ),
        validate_owner_record=lambda document: owner.validate_worker(
            document, family, dict(expected_native),
        ),
        validate_public_observations=lambda document: validate_embedded_records(
            document,
            family=family,
            source_sha256=source_sha256,
            protocol_sha256=protocol_sha256,
            expected_native=expected_native,
            baseline=baseline,
        ),
        observe_snapshot=lambda: v21.snapshot_current_graph()[family],
        observe_owner_after=lambda: v21.run_native_worker(
            family, dict(expected_native),
        ),
        validate_owner_after=lambda document: v21.validate_native_owner(
            document, family, dict(expected_native),
        ),
    )
    return {
        "schema": SCHEMA + "-candidate-worker",
        "status": "PASS",
        "family": family,
        "candidate_module": "candidates." + family + "_candidate",
        "source_sha256": source_sha256,
        "protocol_sha256": protocol_sha256,
        "v19_reference_sha256": BASE19_REFERENCE_SHA256,
        "v19_record_sha256": BASE19_REFERENCE_RECORD_SHA256,
        "native_sha256_by_path": dict(expected_native),
        "original_owner_worker_sha256": original_hash,
        "composed_owner_worker_sha256": composed_hash,
        "owner_before": before,
        "complete_original_owner_before_observation": before_observation,
        "same_process_owner": report,
        "same_process_original_streams": process,
        "public_observations": observations,
        "owner_after": after,
        "v24_edge_archive_sha256": state["edge"]["archive_sha256"],
        "v24_edge_proof_sha256": state["edge"]["proof_sha256"],
        "v24_deep_archive_sha256": state["deep"]["archive_sha256"],
        "v24_deep_proof_sha256": state["deep"]["proof_sha256"],
        "cases": EXPECTED_CASES,
        "record_sha256": observations["record_sha256"],
        "matched_inside_live_current_native_owner_guard": True,
        "fresh_current_native_owner_checks": 2,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
    }


def run_all_candidates(options: argparse.Namespace) -> dict[str, Any]:
    reference = authenticate_reference(
        options.source_sha256, options.protocol_sha256,
    )
    supplied: dict[str, Any] = {
        "v21_source": options.v21_source_sha256,
        "v21_protocol": options.v21_protocol_sha256,
        "v24_source": options.v24_source_sha256,
        "v24_protocol": options.v24_protocol_sha256,
        "v21_base_report": options.v21_base_report_sha256,
        "v21_strict_report": options.v21_strict_report_sha256,
    }
    for family in FAMILIES:
        for kind in ("edge_archive", "edge_proof", "deep_archive", "deep_proof"):
            supplied[family + "_" + kind] = getattr(
                options, family + "_" + kind + "_sha256",
            )
    current = authenticate_current_candidate_prerequisites(reference, supplied)
    locales = _locale_names(options)
    preflight_outputs((
        ALL_CANDIDATE_RELATIVE,
        ALL_CANDIDATE_FAILURE_RELATIVE,
        *CANDIDATE_FAILURE_RELATIVES.values(),
    ))
    completed: dict[str, dict[str, Any]] = {}
    active_family: str | None = None
    result: dict[str, Any] | None = None
    try:
        for family in FAMILIES:
            active_family = family
            completed[family] = run_guarded_candidate(
                family,
                source_sha256=options.source_sha256,
                protocol_sha256=options.protocol_sha256,
                locales=locales,
                current=current,
                baseline=reference["baseline_records"],
            )
            active_family = None
        require(set(completed) == set(FAMILIES),
                "an independently owned real current engine was omitted")
        result = {
            "schema": SCHEMA + "-all-candidates",
            "status": "PASS",
            "synthetic": False,
            "python": "3.14.6",
            "source_path": SOURCE_RELATIVE,
            "source_sha256": options.source_sha256,
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": options.protocol_sha256,
            "v19_reference_sha256": BASE19_REFERENCE_SHA256,
            "v19_reference_record_sha256": BASE19_REFERENCE_RECORD_SHA256,
            "v21_source_sha256": supplied["v21_source"],
            "v21_protocol_sha256": supplied["v21_protocol"],
            "v21_base_report_sha256": supplied["v21_base_report"],
            "v21_strict_report_sha256": supplied["v21_strict_report"],
            "v24_source_sha256": supplied["v24_source"],
            "v24_protocol_sha256": supplied["v24_protocol"],
            "matrix_sha256": MATRIX_SHA256,
            "stimulus_sha256": STIMULUS_SHA256,
            "cohorts": EXPECTED_COHORTS,
            "cases_per_candidate": EXPECTED_CASES,
            "actual_candidate_checks": len(FAMILIES) * EXPECTED_CASES,
            "completed_families": list(FAMILIES),
            "genuine_current_v24_original_archive_count": 6,
            "genuine_current_v24_durable_owner_proof_count": 6,
            "fresh_current_native_owner_checks_per_family": 2,
            "matching_inside_live_current_native_owner_guard": True,
            "preserved_actual_v13_failure_sha256": V13_FAILURE_SHA256,
            "preserved_actual_v15_failure_sha256": V15_FAILURE_SHA256,
            "preserved_actual_v17_failure_sha256": V17_FAILURE_SHA256,
            "preserved_actual_v19_publication_failure_sha256":
                V19_FAILURE_SHA256,
            "preserved_actual_v19_nonqualifying_embedded_sha256":
                V19_FAILED_EMBEDDED_SHA256,
            "preserved_actual_v19_nonqualifying_embedded_bytes":
                V19_FAILED_EMBEDDED_BYTES,
            "preserved_actual_v19_outer_controller_status": "FAIL",
            "preserved_actual_v19_inner_document_status": "PASS",
            "preserved_actual_v22_preflight_failure_sha256":
                V22_FAILURE_SHA256,
            "preserved_actual_v22_preflight_status": "FAIL",
            "preserved_actual_v22_preflight_native_workers": 0,
            "preserved_actual_v17_owner_observations": (
                "NOT PRESERVED BY THE FAILED CONTROLLER"
            ),
            "historical_failure_qualifies_current_build": False,
            "candidate_records": completed,
            "failure_records": [],
            "holdout_cases_read": 0,
            "performance_fixtures_read": 0,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }
        receipt = publish_with_receipt(result, ALL_CANDIDATE_RELATIVE)
        require(receipt.get("fully_published") is True,
                "the real all-family evidence was not durably published")
        return result
    except BaseException as error:
        family = (
            error.role
            if isinstance(error, PublicSurfaceV27WorkerFailure)
            else active_family
        )
        if family is None:
            failure: dict[str, Any] = {
                "schema": SCHEMA + "-all-candidates-failure",
                "status": "FAIL",
                "synthetic": False,
                "failure_scope": (
                    "all-family-publication"
                    if result is not None else "all-family-validation"
                ),
                "failed_family": None,
                "completed_families": completed,
                "completed_family_count": len(completed),
                "complete_unpublished_passing_result": result,
                **error_details(error),
                "holdout_cases_read": 0,
                "benchmark_or_timing_executed": False,
                "performance": "NOT MEASURED",
            }
            if isinstance(error, PublicSurfaceV27PublicationFailure):
                failure["actual_partial_publication_receipt"] = error.receipt
            publish_with_receipt(failure, ALL_CANDIDATE_FAILURE_RELATIVE)
        else:
            failure = {
                "schema": SCHEMA + "-candidate-failure",
                "status": "FAIL",
                "synthetic": False,
                "failed_family": family,
                "completed_families": completed,
                **error_details(error),
                "holdout_cases_read": 0,
                "benchmark_or_timing_executed": False,
                "performance": "NOT MEASURED",
            }
            if isinstance(error, PublicSurfaceV27WorkerFailure):
                failure["actual_failure_details"] = error.details
            if isinstance(error, PublicSurfaceV27PublicationFailure):
                failure["actual_partial_publication_receipt"] = error.receipt
            publish_with_receipt(failure, CANDIDATE_FAILURE_RELATIVES[family])
        raise


def _synthetic_configuration(family: str = "rust") -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-embedded-configuration",
        "family": family,
        "source_sha256": "a" * 64,
        "protocol_sha256": "b" * 64,
        "baseline_v19_source_sha256": BASE19_SOURCE_SHA256,
        "baseline_v19_protocol_sha256": BASE19_PROTOCOL_SHA256,
        "v19_reference_sha256": BASE19_REFERENCE_SHA256,
        "v19_record_sha256": BASE19_REFERENCE_RECORD_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "stimulus_sha256": STIMULUS_SHA256,
        "cases": EXPECTED_CASES,
        "iso8859_1_locale": "source-only-iso8859-1",
        "utf8_locale": "source-only-utf8",
        "expected_native_sha256": {
            "source-only/current-owner.elf": "c" * 64,
        },
    }


class _SyntheticPublicationOperations:
    """Strict in-memory syscall boundary; never opens or writes a real file."""

    def __init__(self, *, fail_at: str | None = None):
        self.fail_at = fail_at
        self.writes = bytearray()
        self.closed: list[int] = []
        self.created = False
        self.synced: list[int] = []
        self.readback_offset = 0
        self.readback_opened = False

    def _fail(self, stage: str) -> None:
        if self.fail_at == stage:
            raise OSError("source-only genuine " + stage + " failure")

    def open_directory(self, _path: Path) -> int:
        self._fail("directory-open")
        return 90

    def verify_directory(self, descriptor: int, _path: Path) -> bool:
        self._fail("directory-identity")
        return descriptor == 90

    def create_leaf(self, descriptor: int, _name: str) -> int:
        self._fail("before-create")
        require(descriptor == 90, "the synthetic publication escaped its parent")
        self.created = True
        return 91

    def write_file(self, descriptor: int, payload: memoryview) -> int:
        require(descriptor == 91, "the synthetic proof wrote another descriptor")
        self._fail("first-write")
        if self.fail_at == "zero-write":
            return 0
        if self.fail_at == "negative-write":
            return -1
        if self.fail_at == "oversized-write":
            return len(payload) + 1
        if self.fail_at == "boolean-write":
            return True
        count = min(len(payload), 17)
        if self.fail_at == "partial-write" and self.writes:
            raise OSError("source-only genuine partial-write failure")
        self.writes.extend(payload[:count])
        return count

    def open_readback(self, descriptor: int, _name: str) -> int:
        self._fail("readback-open")
        require(
            descriptor == 90
            and self.created is True
            and 91 in self.synced
            and 90 in self.synced,
            "the source-only reread escaped its durable original parent",
        )
        self.readback_opened = True
        self.readback_offset = 0
        return 92

    def read_file(self, descriptor: int, maximum: int) -> bytes:
        require(
            descriptor == 92 and type(maximum) is int and maximum > 0,
            "the source-only readback escaped its genuine no-follow descriptor",
        )
        self._fail("readback-read")
        if self.fail_at == "readback-partial" and self.readback_offset:
            raise OSError("source-only genuine readback-partial failure")
        data = bytes(self.writes)
        if self.fail_at == "readback-truncated" and data:
            data = data[:-1]
        elif self.fail_at == "readback-mismatch" and data:
            data = b"!" + data[1:]
        elif self.fail_at == "readback-noncanonical":
            data = b" " + data
        count = min(maximum, 19, max(0, len(data) - self.readback_offset))
        chunk = data[self.readback_offset:self.readback_offset + count]
        self.readback_offset += len(chunk)
        return chunk

    def sync(self, descriptor: int) -> None:
        if descriptor == 91:
            self._fail("file-fsync")
        elif descriptor == 90:
            self._fail("directory-fsync")
        else:
            raise OSError("source-only unknown fsync descriptor")
        self.synced.append(descriptor)

    def close(self, descriptor: int) -> None:
        if descriptor == 91:
            self._fail("file-close")
        elif descriptor == 90:
            self._fail("directory-close")
        elif descriptor == 92:
            self._fail("readback-close")
        self.closed.append(descriptor)


def _synthetic_zero_exit_worker(
    family: str,
    baseline: list[dict[str, Any]],
    snapshot: Mapping[str, Any],
    *,
    mode: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    require(mode in {
        "pass", "malformed", "mismatch", "augmented-owner",
        "restored-owner", "snapshot", "owner-after", "final-snapshot",
    }, "the actual source-only zero-exit poison was substituted")
    records = copy.deepcopy(baseline)
    if mode == "mismatch":
        records[14]["outcome"] = {
            "status": "return", "value": "source-only actual V27 mismatch",
        }
    public = {
        "schema": "source-only-v27-complete-original-observations",
        "status": "PASS",
        "records": records,
    }
    report = {
        "schema": "source-only-v27-complete-current-owner",
        "status": "PASS",
        "rebar_v27_guarded_public_surface": public,
    }
    stdout = (
        b'{"source-only-v27-malformed-zero-exit":'
        if mode == "malformed"
        else canonical(report) + b"\n"
    )
    process = {
        "role": family,
        "returncode": 0,
        "stdout": capture_complete_stream(stdout),
        "stderr": capture_complete_stream(b""),
    }
    before = {"status": "PASS", "family": family,
              "schema": "source-only-v27-owner-before"}
    worker_hash = hashlib.sha256(
        ("source-only-v27-current-owner:" + family).encode("ascii"),
    ).hexdigest()
    snapshot_calls = [0]

    def decode(payload: bytes) -> dict[str, Any]:
        return strict_canonical(payload, "source-only V27 complete owner")

    def validate_owner(actual: Any) -> Any:
        require(isinstance(actual, dict) and actual.get("status") == "PASS",
                "the actual source-only current owner was malformed")
        augmented = "rebar_v27_guarded_public_surface" in actual
        require(not (mode == "augmented-owner" and augmented),
                "the source-only augmented current owner actually failed")
        require(not (mode == "restored-owner" and not augmented),
                "the source-only restored current owner actually failed")
        return actual

    def validate_public(actual: Any) -> Any:
        require(isinstance(actual, Mapping)
                and actual.get("status") == "PASS"
                and actual.get("records") == baseline,
                "the complete source-only current candidate actually mismatched")
        return dict(actual)

    def observe_snapshot() -> dict[str, Any]:
        snapshot_calls[0] += 1
        observed = copy.deepcopy(dict(snapshot))
        if ((mode == "snapshot" and snapshot_calls[0] == 1)
                or (mode == "final-snapshot" and snapshot_calls[0] == 2)):
            sources = observed.get("source_sha256_by_path")
            if isinstance(sources, dict) and sources:
                sources[next(iter(sources))] = "0" * 64
        return observed

    def observe_after() -> dict[str, Any]:
        return {"family": family,
                "status": "FAIL" if mode == "owner-after" else "PASS"}

    def validate_after(actual: Any) -> dict[str, Any]:
        require(isinstance(actual, dict) and actual.get("status") == "PASS",
                "the genuine source-only current after-owner failed")
        return actual

    return validate_zero_exit_guarded_worker(
        family,
        retained_process=process,
        owner_before=before,
        owner_before_observation=before,
        composed_worker_sha256=worker_hash,
        expected_snapshot=snapshot,
        baseline=baseline,
        decode_owner=decode,
        validate_owner_record=validate_owner,
        validate_public_observations=validate_public,
        observe_snapshot=observe_snapshot,
        observe_owner_after=observe_after,
        validate_owner_after=validate_after,
    )


def self_test() -> dict[str, Any]:
    verify_runtime()
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a candidate imported before the source-only current public control")
    authenticate_frozen_instructions()
    inherited = base19.self_test()
    require(inherited.get("status") == "PASS"
            and inherited.get("check_count", 0) >= 864
            and inherited.get("inherited_v18_check_count", 0) >= 474
            and inherited.get("inherited_v17_check_count", 0) >= 336
            and inherited.get("total_independent_source_controls", 0) >= 1_674
            and inherited.get("cases") == EXPECTED_CASES
            and inherited.get("cohorts") == EXPECTED_COHORTS
            and inherited.get("matrix_sha256") == MATRIX_SHA256
            and inherited.get("stimulus_sha256") == STIMULUS_SHA256
            and inherited.get("current_graph_candidate_qualification")
            == "BLOCKED"
            and inherited.get("candidate_evidence_current") == "NOT QUALIFIED"
            and inherited.get("candidate_source_files_read") == 0
            and inherited.get("evidence_files_read") == 0
            and inherited.get("v12_source_files_read") == 0
            and inherited.get("files_written") == 0
            and inherited.get("candidate_imports") == 0
            and inherited.get("subprocesses") == 0
            and inherited.get("threads_started") == 0
            and inherited.get("clock_samples") == 0
            and inherited.get("entropy_draws") == 0
            and inherited.get("locale_changes") == 0
            and inherited.get("regex_matching_calls") == 0
            and inherited.get("holdout_cases_read") == 0,
            "the complete actual frozen V19 source-only controls did not pass")
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: Any) -> None:
        require(not any(row["name"] == name for row in checks),
                "an independent V27 source-only poison was counted twice")
        checks.append({"name": name, "passed": bool(condition)})

    def reject(name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except (PublicSurfaceV27Error, base17.PublicSurfaceError,
                base18.PublicSurfaceV18Error, base19.PublicSurfaceV19Error,
                AssertionError, OSError, ValueError, TypeError, KeyError,
                SyntaxError, UnicodeError):
            check(name, True)
        else:
            check(name, False)

    with base17._source_only_effects() as effects:
        matrix = build_matrix()
        check("preserve-all-1674-real-inherited-v19-source-only-controls",
              inherited["total_independent_source_controls"] >= 1_674)
        check("preserve-the-actual-v19-two-reference-report-fingerprint",
              valid_sha256(BASE19_REFERENCE_SHA256)
              and BASE19_REFERENCE_SHA256 != BASE19_REFERENCE_RECORD_SHA256)
        check("preserve-the-actual-v19-complete-record-fingerprint",
              valid_sha256(BASE19_REFERENCE_RECORD_SHA256))
        check("retain-the-preserved-real-base18-failure-without-opening-it",
              BASE18_FAILURE_SHA256 == base19.V18_HISTORICAL_FAILURE_SHA256
              and BASE18_FAILURE_RELATIVE not in APPROVED_OUTPUTS)
        check("retain-the-preserved-real-v13-first-failure-without-opening-it",
              valid_sha256(V13_FAILURE_SHA256)
              and V13_FAILURE_RELATIVE not in APPROVED_OUTPUTS)
        check("never-qualify-the-real-v13-failed-first-native-owner",
              V13_FAILURE_SCHEMA.endswith("preflight-failure"))
        check("retain-the-preserved-real-v15-first-failure-without-opening-it",
              valid_sha256(V15_FAILURE_SHA256)
              and V15_FAILURE_RELATIVE not in APPROVED_OUTPUTS
              and V15_FAILURE_SHA256 != V13_FAILURE_SHA256)
        check("never-qualify-the-real-v15-failed-first-native-owner",
              V15_FAILURE_SCHEMA.endswith("preflight-failure"))

        check("retain-real-v17-post-owner-failure-without-opening-it",
              valid_sha256(V17_FAILURE_SHA256)
              and V17_FAILURE_RELATIVE not in APPROVED_OUTPUTS
              and len({V13_FAILURE_SHA256, V15_FAILURE_SHA256,
                       V17_FAILURE_SHA256}) == 3)
        check("never-qualify-the-real-v17-failed-post-owner-integrity",
              V17_FAILURE_SCHEMA.endswith("post-owner-integrity-failure"))

        check("retain-root-verified-v19-publication-failure-without-opening-it",
              valid_sha256(V19_FAILURE_SHA256)
              and valid_sha256(V19_FAILED_EMBEDDED_SHA256)
              and V19_FAILURE_RELATIVE not in APPROVED_OUTPUTS
              and V19_FAILED_EMBEDDED_RELATIVE not in APPROVED_OUTPUTS
              and len({
                  V13_FAILURE_SHA256, V15_FAILURE_SHA256,
                  V17_FAILURE_SHA256, V19_FAILURE_SHA256,
              }) == 4)
        check("never-qualify-genuine-v19-inner-pass-and-outer-exit-one",
              V19_FAILURE_SCHEMA.endswith("exclusive-publication-first-failure")
              and V19_FAILED_EMBEDDED_BYTES == 161_316
              and V19_FAILURE_SHA256 != V19_FAILED_EMBEDDED_SHA256)

        check("retain-actual-fifth-v22-integration-failure-without-opening-it",
              valid_sha256(V22_FAILURE_SHA256)
              and V22_FAILURE_RELATIVE not in APPROVED_OUTPUTS
              and len({
                  V13_FAILURE_SHA256, V15_FAILURE_SHA256,
                  V17_FAILURE_SHA256, V19_FAILURE_SHA256,
                  V22_FAILURE_SHA256,
              }) == 5)
        check("never-qualify-real-fifth-v22-zero-worker-preflight",
              V22_FAILURE_SCHEMA.endswith(
                  "read-only-integration-preflight-failure",
              ))

        source_only_v13_failure = {
            "failure_path": V13_FAILURE_RELATIVE,
            "failure_sha256": V13_FAILURE_SHA256,
            "failure_schema": V13_FAILURE_SCHEMA,
            "status": "FAIL",
            "failed_stage": V13_FAILURE_ACTUAL_STAGE,
            "actual_error_type": "AssertionError",
            "actual_error_message": V13_FAILURE_ACTUAL_MESSAGE,
            "actual_exit_code": 1,
            "native_owner_workers_started": 0,
            "original_edge_worker_started": False,
            "synthetic": False,
            "qualifies_current_engine": False,
            "v13_source_path": V13_FAILED_OWNER_RELATIVE,
            "v13_source_sha256": V13_FAILED_OWNER_SHA256,
            "v13_protocol_path": V13_FAILED_PROTOCOL_RELATIVE,
            "v13_protocol_sha256": V13_FAILED_PROTOCOL_SHA256,
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
        check(
            "authenticate-exact-source-only-normalized-v13-incident-shape",
            len(source_only_v13_failure) == 26
            and validate_actual_v13_failure(source_only_v13_failure)
            == source_only_v13_failure,
        )
        for field in tuple(source_only_v13_failure):
            removed = dict(source_only_v13_failure)
            removed.pop(field)
            reject(
                "reject-missing-source-only-v13-failure-field-" + field,
                lambda removed=removed: validate_actual_v13_failure(removed),
            )
        for field, wrong in (
            ("failure_schema", "forged"),
            ("failure_path", V15_FAILURE_RELATIVE),
            ("failure_sha256", V15_FAILURE_SHA256),
            ("status", "PASS"),
            ("failed_stage", "historical-zig-edge-preflight"),
            ("actual_exit_code", False),
            ("native_owner_workers_started", False),
            ("stdout_capture", ""),
            ("stderr_capture", ""),
            ("combined_traceback_line_count", 20),
            ("combined_traceback_separately_captured", True),
        ):
            forged = dict(source_only_v13_failure)
            forged[field] = wrong
            reject(
                "reject-forged-source-only-v13-failure-field-" + field,
                lambda forged=forged: validate_actual_v13_failure(forged),
            )

        source_only_v15_failure = {
            "failure_schema": V15_FAILURE_SCHEMA,
            "failure_path": V15_FAILURE_RELATIVE,
            "failure_sha256": V15_FAILURE_SHA256,
            "status": "FAIL",
            "failed_stage": "source-only-preserved-failure-codec",
            "actual_error_type": "SourceOnlyV15Failure",
            "actual_error_message": "source-only synthetic incident control",
            "actual_exit_code": 1,
            "native_owner_workers_started": 0,
            "original_edge_worker_started": False,
            "synthetic": False,
            "qualifies_current_engine": False,
            "v15_source_path": "tools/postfinal_independent_engine_audit_v15.py",
            "v15_source_sha256": hashlib.sha256(
                b"source-only-v15-incident-source",
            ).hexdigest(),
            "v15_protocol_path": (
                "oracle/cpython-3.14.6/"
                "POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V15.md"
            ),
            "v15_protocol_sha256": hashlib.sha256(
                b"source-only-v15-incident-protocol",
            ).hexdigest(),
            "stdout_capture": "NOT CAPTURED",
            "stderr_capture": "NOT CAPTURED",
            "combined_traceback_line_count": 20,
            "combined_traceback_separately_captured": False,
            "fresh_ownership_report": "NOT WRITTEN",
            "fresh_ownership_failure_report": "NOT WRITTEN",
            "fresh_strict_report": "NOT WRITTEN",
            "fresh_strict_failure_report": "NOT WRITTEN",
            "preserved_v13_first_failure_path": V13_FAILURE_RELATIVE,
            "preserved_v13_first_failure_sha256": V13_FAILURE_SHA256,
            "performance": "NOT MEASURED",
            "holdout": "NOT MEASURED",
        }
        check(
            "authenticate-exact-28-source-only-normalized-v15-failure-fields",
            len(source_only_v15_failure) == 28
            and validate_actual_v15_failure(source_only_v15_failure)
            == source_only_v15_failure,
        )
        for field in tuple(source_only_v15_failure):
            removed = dict(source_only_v15_failure)
            removed.pop(field)
            reject(
                "reject-missing-source-only-v15-failure-field-" + field,
                lambda removed=removed: validate_actual_v15_failure(removed),
            )
        for field, wrong in (
            ("failure_schema", V13_FAILURE_SCHEMA),
            ("failure_path", V13_FAILURE_RELATIVE),
            ("failure_sha256", V13_FAILURE_SHA256),
            ("status", "PASS"),
            ("actual_exit_code", False),
            ("native_owner_workers_started", False),
            ("original_edge_worker_started", True),
            ("synthetic", True),
            ("qualifies_current_engine", True),
            ("stdout_capture", "invented separate stream"),
            ("stderr_capture", "invented separate stream"),
            ("combined_traceback_line_count", 34),
            ("combined_traceback_separately_captured", True),
            ("preserved_v13_first_failure_path", V15_FAILURE_RELATIVE),
            ("preserved_v13_first_failure_sha256", V15_FAILURE_SHA256),
        ):
            forged = dict(source_only_v15_failure)
            forged[field] = wrong
            reject(
                "reject-forged-source-only-v15-failure-field-" + field,
                lambda forged=forged: validate_actual_v15_failure(forged),
            )
        source_only_v17_failure = {
            "source_path": V17_FAILURE_RELATIVE,
            "sha256": V17_FAILURE_SHA256,
            "schema": V17_FAILURE_SCHEMA,
            "status": "FAIL",
            "exit_code": 1,
            "failed_stage": (
                "unpreserved-static-graph-integrity-recheck-"
                "after-three-genuine-native-owner-workers"
            ),
            "actual_error_type": (
                "tools.postfinal_from_scratch_audit_v2.AuditV2Error"
            ),
            "actual_error_message": (
                "actual current 76-control source audit changed "
                "the immutable universal audit contract"
            ),
            "actual_completed_native_owner_families": list(FAMILIES),
            "actual_native_owner_workers_completed": 3,
            "actual_native_owner_observations": (
                "NOT PRESERVED BY THE FAILED CONTROLLER"
            ),
            "actual_captured_combined_output_lines": 27,
            "output_capture": (
                "complete combined command output; stdout and stderr "
                "were not separately captured"
            ),
            "fresh_ownership_report": "NOT CREATED",
            "fresh_ownership_failure_report": "NOT CREATED",
            "fresh_strict_report": "NOT CREATED",
            "fresh_strict_failure_report": "NOT CREATED",
            "historical_failure_qualifies_current_build": False,
        }
        check(
            "authenticate-exact-18-root-confirmed-v17-failure-fields",
            len(source_only_v17_failure) == 18
            and validate_actual_v17_failure(source_only_v17_failure)
            == source_only_v17_failure,
        )
        for field in tuple(source_only_v17_failure):
            removed = dict(source_only_v17_failure)
            removed.pop(field)
            reject(
                "reject-missing-source-only-v17-post-owner-field-" + field,
                lambda removed=removed: validate_actual_v17_failure(removed),
            )
        for field, wrong in (
            ("source_path", V15_FAILURE_RELATIVE),
            ("sha256", V15_FAILURE_SHA256),
            ("schema", V15_FAILURE_SCHEMA),
            ("status", "PASS"),
            ("exit_code", False),
            ("failed_stage", "invented historical pass"),
            ("actual_error_type", "RuntimeError"),
            ("actual_error_message", "invented message"),
            ("actual_completed_native_owner_families", ["rust"]),
            ("actual_native_owner_workers_completed", True),
            ("actual_native_owner_observations", []),
            ("actual_captured_combined_output_lines", False),
            ("output_capture", "invented separated streams"),
            ("fresh_ownership_report", "PASS"),
            ("fresh_ownership_failure_report", "PASS"),
            ("fresh_strict_report", "PASS"),
            ("fresh_strict_failure_report", "PASS"),
            ("historical_failure_qualifies_current_build", True),
        ):
            forged = dict(source_only_v17_failure)
            forged[field] = wrong
            reject(
                "reject-forged-source-only-v17-post-owner-field-" + field,
                lambda forged=forged: validate_actual_v17_failure(forged),
            )
        with_extra = dict(source_only_v17_failure)
        with_extra["invented_native_owner_observations"] = []
        reject(
            "reject-invented-genuine-v17-native-owner-observations",
            lambda with_extra=with_extra: validate_actual_v17_failure(
                with_extra,
            ),
        )

        source_only_v19_failure = {
            "source_path": V19_FAILURE_RELATIVE,
            "sha256": V19_FAILURE_SHA256,
            "schema": V19_FAILURE_SCHEMA,
            "status": "FAIL",
            "exit_code": 1,
            "invocation_count": 1,
            "actual_error_message": (
                "the exclusive V19 publication failed; "
                "actual syscall receipt retained"
            ),
            "actual_inner_error_message": (
                "an exact exclusively published V19 all-family report "
                "was changed"
            ),
            "v19_source_path": V19_FAILED_SOURCE_RELATIVE,
            "v19_source_sha256": V19_FAILED_SOURCE_SHA256,
            "v19_protocol_path": V19_FAILED_PROTOCOL_RELATIVE,
            "v19_protocol_sha256": V19_FAILED_PROTOCOL_SHA256,
            "durable_report_path": V19_FAILED_EMBEDDED_RELATIVE,
            "durable_report_sha256": V19_FAILED_EMBEDDED_SHA256,
            "durable_report_bytes": V19_FAILED_EMBEDDED_BYTES,
            "durable_embedded_document_status": "PASS",
            "actual_controller_status": "FAIL",
            "canonical_report_bytes_independently_verified": True,
            "embedded_pass_qualifies_current_engine": False,
            "historical_failure_qualifies_current_build": False,
            "completed_native_owner_worker_count": 3,
            "complete_actual_native_owner_streams_preserved": True,
            "actual_original_native_owner_workers": {
                family: {
                    "schema": "source-only-v27-original-native-owner",
                    "status": "PASS",
                    "family": family,
                }
                for family in FAMILIES
            },
            "exclusive_create_succeeded": True,
            "actual_bytes_written": V19_FAILED_EMBEDDED_BYTES,
            "file_fsync_succeeded": True,
            "parent_directory_fsync_succeeded": True,
            "canonical_reread_succeeded": False,
            "actual_write_calls": [{
                "requested_bytes": V19_FAILED_EMBEDDED_BYTES,
                "returned_bytes": V19_FAILED_EMBEDDED_BYTES,
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
        check(
            "authenticate-all-genuine-normalized-v19-publication-failure-fields",
            len(source_only_v19_failure) == 36
            and validate_actual_v19_failure(source_only_v19_failure)
            == source_only_v19_failure,
        )
        for field in tuple(source_only_v19_failure):
            removed = dict(source_only_v19_failure)
            removed.pop(field)
            reject(
                "reject-missing-source-only-v19-publication-field-" + field,
                lambda removed=removed: validate_actual_v19_failure(removed),
            )
        for field, wrong in (
            ("source_path", V17_FAILURE_RELATIVE),
            ("sha256", V17_FAILURE_SHA256),
            ("schema", V17_FAILURE_SCHEMA),
            ("status", "PASS"),
            ("exit_code", False),
            ("invocation_count", False),
            ("actual_error_message", "invented outer failure"),
            ("actual_inner_error_message", "invented syscall failure"),
            ("v19_source_path", V21_SOURCE_RELATIVE),
            ("v19_source_sha256", V21_SOURCE_SHA256),
            ("v19_protocol_path", V21_PROTOCOL_RELATIVE),
            ("v19_protocol_sha256", V21_PROTOCOL_SHA256),
            ("durable_report_path", V19_FAILURE_RELATIVE),
            ("durable_report_sha256", V19_FAILURE_SHA256),
            ("durable_report_bytes", False),
            ("durable_embedded_document_status", "FAIL"),
            ("actual_controller_status", "PASS"),
            ("canonical_report_bytes_independently_verified", False),
            ("embedded_pass_qualifies_current_engine", True),
            ("historical_failure_qualifies_current_build", True),
            ("completed_native_owner_worker_count", True),
            ("complete_actual_native_owner_streams_preserved", False),
            ("actual_original_native_owner_workers", {}),
            ("exclusive_create_succeeded", False),
            ("actual_bytes_written", False),
            ("file_fsync_succeeded", False),
            ("parent_directory_fsync_succeeded", False),
            ("canonical_reread_succeeded", True),
            ("actual_write_calls", []),
            ("original_non_roundtripping_in_memory_value", "invented"),
            ("fresh_v19_ownership_failure_report", True),
            ("fresh_v19_strict_report", True),
            ("fresh_v19_strict_failure_report", True),
            ("strict_audit", "PASS"),
            ("performance", "1.5x"),
            ("holdout", "invented"),
        ):
            forged = dict(source_only_v19_failure)
            forged[field] = wrong
            reject(
                "reject-forged-source-only-v19-publication-field-" + field,
                lambda forged=forged: validate_actual_v19_failure(forged),
            )
        invented = dict(source_only_v19_failure)
        invented["invented_successful_exit_code"] = 0
        reject(
            "never-qualify-v19-internal-pass-after-actual-controller-exit-one",
            lambda invented=invented: validate_actual_v19_failure(invented),
        )

        v22_failure_pins = {
            "audit_source": V21_SOURCE_SHA256,
            "audit_protocol": V21_PROTOCOL_SHA256,
            "base_report": hashlib.sha256(
                b"source-only-v27-fifth-base",
            ).hexdigest(),
            "strict_report": hashlib.sha256(
                b"source-only-v27-fifth-strict",
            ).hexdigest(),
        }
        source_only_v22_failure = {
            "source_path": V22_FAILURE_RELATIVE,
            "sha256": V22_FAILURE_SHA256,
            "schema": V22_FAILURE_SCHEMA,
            "status": "FAIL",
            "synthetic": False,
            "attempted_family": "rust",
            "failed_stage": (
                "candidate-free authentication of the genuine historical V13 "
                "summary before the first original edge worker"
            ),
            "actual_exception_type": (
                "tools.postfinal_current_build_proofs_v22.ProofV22Error"
            ),
            "actual_exception_message": (
                "the genuine original failed V13 first invocation was forged"
            ),
            "actual_combined_traceback_line_count": 24,
            "actual_combined_traceback_lines": [
                "source-only-v27 combined traceback " + str(index)
                for index in range(24)
            ],
            "actual_failed_invocation_boundary_counters": (
                "NOT PRESERVED BY THE FAILED CONTROLLER"
            ),
            "native_owner_workers_started": 0,
            "original_edge_workers_started": 0,
            "original_deep_workers_started": 0,
            "families_not_reached": ["vm", "zig"],
            "benchmark_or_timing_executed": False,
            "correctness_results_published": False,
            "production_observations_invented": False,
            "qualifies_current_engine": False,
            "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED",
            "actual_invocation": {
                "actual_inline_python_source_lines": [
                    "source-only-v27 inline source " + str(index)
                    for index in range(25)
                ],
                "environment": {
                    "LC_ALL": "C",
                    "PATH": "/usr/bin:/bin",
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "PYTHONHASHSEED": "0",
                    "PYTHONPATH": "source-only-v27",
                },
                "executable": str(base17.PINNED_PYTHON),
                "exit_code": 1,
                "output_capture": (
                    "complete combined traceback; "
                    "stdout and stderr were not separately captured"
                ),
                "python_flags": ["-I", "-B", "-c"],
            },
            "actual_historical_summary_mismatch": {
                "historical_version": "v13",
                "field": "failed_stage",
                "expected_field_count": 26,
                "actual_authenticated_field_count": 26,
                "missing_fields": [],
                "extra_fields": [],
                "v22_expected_value": "historical-zig-edge-preflight",
                "actual_authenticated_v21_value": V13_FAILURE_ACTUAL_STAGE,
                "other_fields_match": True,
                "other_historical_summaries_exactly_match": [
                    "v15", "v17", "v19",
                ],
            },
            "actual_passing_prerequisites": {
                "audit_source_sha256": V21_SOURCE_SHA256,
                "audit_protocol_sha256": V21_PROTOCOL_SHA256,
                "base_report_path": V21_BASE_REPORT_RELATIVE,
                "base_report_sha256": v22_failure_pins["base_report"],
                "strict_report_path": V21_STRICT_REPORT_RELATIVE,
                "strict_report_sha256": v22_failure_pins["strict_report"],
                "both_independent_ownership_audits_passed": True,
            },
            "frozen_failed_controller": {
                "source_path": V22_FAILED_SOURCE_RELATIVE,
                "source_sha256": V22_FAILED_SOURCE_SHA256,
                "protocol_path": V22_FAILED_PROTOCOL_RELATIVE,
                "protocol_sha256": V22_FAILED_PROTOCOL_SHA256,
            },
            "independent_follow_up_differential": {
                "status": "PASS",
                "validation_scope": (
                    "read-only authentication of the exact published V21 "
                    "reports and all four historical summary shapes only"
                ),
                "read_only_boundary_effects": {
                    "candidate_imports": 0,
                    "clock_samples": 0,
                    "filesystem_writes": 0,
                    "native_workers_started": 0,
                    "subprocesses_started": 0,
                },
            },
        }
        check(
            "authenticate-exact-27-normalized-fifth-v22-preflight-fields",
            len(source_only_v22_failure) == 27
            and validate_actual_v22_failure(
                source_only_v22_failure,
                v22_failure_pins,
            ) == source_only_v22_failure,
        )
        for field in tuple(source_only_v22_failure):
            removed = dict(source_only_v22_failure)
            removed.pop(field)
            reject(
                "reject-missing-source-only-fifth-v22-field-" + field,
                lambda removed=removed: validate_actual_v22_failure(
                    removed,
                    v22_failure_pins,
                ),
            )
        for field, wrong in (
            ("source_path", V19_FAILURE_RELATIVE),
            ("sha256", V19_FAILURE_SHA256),
            ("schema", V19_FAILURE_SCHEMA),
            ("status", "PASS"),
            ("synthetic", True),
            ("attempted_family", "zig"),
            ("failed_stage", "historical-zig-edge-preflight"),
            ("actual_exception_type", "AssertionError"),
            ("actual_exception_message", "invented V22 failure"),
            ("actual_combined_traceback_line_count", False),
            ("actual_combined_traceback_lines", ["invented"]),
            ("actual_failed_invocation_boundary_counters", {}),
            ("native_owner_workers_started", False),
            ("original_edge_workers_started", False),
            ("original_deep_workers_started", False),
            ("families_not_reached", ["zig", "vm"]),
            ("benchmark_or_timing_executed", True),
            ("correctness_results_published", True),
            ("production_observations_invented", True),
            ("qualifies_current_engine", True),
            ("performance", "1.5x"),
            ("holdout", "invented"),
            ("actual_invocation", {}),
            ("actual_historical_summary_mismatch", {}),
            ("actual_passing_prerequisites", {}),
            ("frozen_failed_controller", {}),
            ("independent_follow_up_differential", {}),
        ):
            forged = dict(source_only_v22_failure)
            forged[field] = wrong
            reject(
                "reject-forged-source-only-fifth-v22-field-" + field,
                lambda forged=forged: validate_actual_v22_failure(
                    forged,
                    v22_failure_pins,
                ),
            )

        def reject_v22_nested(
            parent_field: str,
            child_field: str,
            wrong: Any,
        ) -> None:
            forged = copy.deepcopy(source_only_v22_failure)
            forged[parent_field][child_field] = wrong
            reject(
                "reject-forged-source-only-fifth-v22-"
                + parent_field + "-" + child_field,
                lambda forged=forged: validate_actual_v22_failure(
                    forged,
                    v22_failure_pins,
                ),
            )

        for field, wrong in (
            ("actual_inline_python_source_lines", ["invented"] * 24),
            ("environment", {"LC_ALL": "C"}),
            ("executable", "/tmp/source-only-forged-python"),
            ("exit_code", True),
            ("output_capture", "invented separately captured streams"),
            ("python_flags", ["-I", "-B"]),
        ):
            reject_v22_nested("actual_invocation", field, wrong)
        for field, wrong in (
            ("historical_version", "v15"),
            ("field", "status"),
            ("expected_field_count", 25),
            ("actual_authenticated_field_count", True),
            ("missing_fields", ["failed_stage"]),
            ("extra_fields", ["invented"]),
            ("v22_expected_value", V13_FAILURE_ACTUAL_STAGE),
            ("actual_authenticated_v21_value", "historical-zig-edge-preflight"),
            ("other_fields_match", False),
            ("other_historical_summaries_exactly_match", ["v15", "v17"]),
        ):
            reject_v22_nested(
                "actual_historical_summary_mismatch",
                field,
                wrong,
            )
        for field, wrong in (
            ("audit_source_sha256", V22_FAILED_SOURCE_SHA256),
            ("audit_protocol_sha256", V22_FAILED_PROTOCOL_SHA256),
            ("base_report_path", V21_STRICT_REPORT_RELATIVE),
            ("base_report_sha256", v22_failure_pins["strict_report"]),
            ("strict_report_path", V21_BASE_REPORT_RELATIVE),
            ("strict_report_sha256", v22_failure_pins["base_report"]),
            ("both_independent_ownership_audits_passed", False),
        ):
            reject_v22_nested("actual_passing_prerequisites", field, wrong)
        for field, wrong in (
            ("source_path", V24_SOURCE_RELATIVE),
            ("source_sha256", V21_SOURCE_SHA256),
            ("protocol_path", V24_PROTOCOL_RELATIVE),
            ("protocol_sha256", V21_PROTOCOL_SHA256),
        ):
            reject_v22_nested("frozen_failed_controller", field, wrong)
        for field, wrong in (
            ("status", "FAIL"),
            ("validation_scope", "invented candidate execution"),
            ("read_only_boundary_effects", {}),
        ):
            reject_v22_nested(
                "independent_follow_up_differential",
                field,
                wrong,
            )
        for parent_field in (
            "actual_invocation",
            "actual_historical_summary_mismatch",
            "actual_passing_prerequisites",
            "frozen_failed_controller",
            "independent_follow_up_differential",
        ):
            for child_field in tuple(
                source_only_v22_failure[parent_field],
            ):
                forged = copy.deepcopy(source_only_v22_failure)
                forged[parent_field].pop(child_field)
                reject(
                    "reject-missing-source-only-fifth-v22-"
                    + parent_field + "-" + child_field,
                    lambda forged=forged: validate_actual_v22_failure(
                        forged,
                        v22_failure_pins,
                    ),
                )
            forged = copy.deepcopy(source_only_v22_failure)
            forged[parent_field]["source_only_invented_extra"] = True
            reject(
                "reject-extra-source-only-fifth-v22-" + parent_field,
                lambda forged=forged: validate_actual_v22_failure(
                    forged,
                    v22_failure_pins,
                ),
            )
        for field, wrong in (
            ("LC_ALL", "source-only-invalid-locale"),
            ("PATH", ""),
            ("PYTHONDONTWRITEBYTECODE", "0"),
            ("PYTHONHASHSEED", "1"),
            ("PYTHONPATH", ""),
        ):
            forged = copy.deepcopy(source_only_v22_failure)
            forged["actual_invocation"]["environment"][field] = wrong
            reject(
                "reject-forged-source-only-fifth-v22-environment-" + field,
                lambda forged=forged: validate_actual_v22_failure(
                    forged,
                    v22_failure_pins,
                ),
            )
            forged = copy.deepcopy(source_only_v22_failure)
            forged["actual_invocation"]["environment"].pop(field)
            reject(
                "reject-missing-source-only-fifth-v22-environment-" + field,
                lambda forged=forged: validate_actual_v22_failure(
                    forged,
                    v22_failure_pins,
                ),
            )
        for field, child_field in (
            ("actual_combined_traceback_lines", None),
            ("actual_invocation", "actual_inline_python_source_lines"),
        ):
            forged = copy.deepcopy(source_only_v22_failure)
            actual_lines = (
                forged[field]
                if child_field is None
                else forged[field][child_field]
            )
            actual_lines[0] = False
            reject(
                "reject-nonstring-source-only-fifth-v22-"
                + (field if child_field is None else child_field),
                lambda forged=forged: validate_actual_v22_failure(
                    forged,
                    v22_failure_pins,
                ),
            )
        for effect in (
            "candidate_imports",
            "clock_samples",
            "filesystem_writes",
            "native_workers_started",
            "subprocesses_started",
        ):
            forged = copy.deepcopy(source_only_v22_failure)
            forged["independent_follow_up_differential"][
                "read_only_boundary_effects"
            ][effect] = 1
            reject(
                "reject-nonzero-source-only-fifth-v22-follow-up-" + effect,
                lambda forged=forged: validate_actual_v22_failure(
                    forged,
                    v22_failure_pins,
                ),
            )
            forged = copy.deepcopy(source_only_v22_failure)
            forged["independent_follow_up_differential"][
                "read_only_boundary_effects"
            ][effect] = False
            reject(
                "reject-boolean-source-only-fifth-v22-follow-up-" + effect,
                lambda forged=forged: validate_actual_v22_failure(
                    forged,
                    v22_failure_pins,
                ),
            )
            forged = copy.deepcopy(source_only_v22_failure)
            forged["independent_follow_up_differential"][
                "read_only_boundary_effects"
            ].pop(effect)
            reject(
                "reject-missing-source-only-fifth-v22-follow-up-" + effect,
                lambda forged=forged: validate_actual_v22_failure(
                    forged,
                    v22_failure_pins,
                ),
            )
        for field in tuple(v22_failure_pins):
            removed_pins = dict(v22_failure_pins)
            removed_pins.pop(field)
            reject(
                "reject-missing-source-only-fifth-v22-runtime-pin-" + field,
                lambda removed_pins=removed_pins: validate_actual_v22_failure(
                    source_only_v22_failure,
                    removed_pins,
                ),
            )
        for field, wrong in (
            ("audit_source", V22_FAILED_SOURCE_SHA256),
            ("audit_protocol", V22_FAILED_PROTOCOL_SHA256),
            ("base_report", v22_failure_pins["strict_report"]),
            ("strict_report", v22_failure_pins["base_report"]),
        ):
            forged_pins = dict(v22_failure_pins)
            forged_pins[field] = wrong
            reject(
                "reject-forged-source-only-fifth-v22-runtime-pin-" + field,
                lambda forged_pins=forged_pins: validate_actual_v22_failure(
                    source_only_v22_failure,
                    forged_pins,
                ),
            )
        extra_pins = dict(v22_failure_pins)
        extra_pins["invented_report"] = hashlib.sha256(
            b"source-only-v27-invented-report",
        ).hexdigest()
        reject(
            "reject-extra-source-only-fifth-v22-runtime-pin",
            lambda: validate_actual_v22_failure(
                source_only_v22_failure,
                extra_pins,
            ),
        )
        invented_fifth = dict(source_only_v22_failure)
        invented_fifth["invented_successful_exit_code"] = 0
        reject(
            "never-qualify-zero-worker-failed-v22-preflight",
            lambda invented_fifth=invented_fifth: validate_actual_v22_failure(
                invented_fifth,
                v22_failure_pins,
            ),
        )

        source_only_v21 = object()
        source_only_owner = object()
        source_only_graph = {
            "schema": "source-only-v27-exact-original-native-graph",
            "status": "PASS",
        }
        source_only_audits = {
            "owner": source_only_owner,
            "pins": dict(v22_failure_pins),
            "graph": source_only_graph,
            "preserved_v13_failure": source_only_v13_failure,
            "preserved_v15_failure": source_only_v15_failure,
            "preserved_v17_failure": source_only_v17_failure,
            "preserved_v19_failure": source_only_v19_failure,
        }
        required_incidents = {
            "v13_first_owner_preflight_failure": source_only_v13_failure,
            "v13_first_owner_preflight_failure_qualifies_current_engine": (
                False
            ),
            "v15_first_owner_preflight_failure": source_only_v15_failure,
            "v15_first_owner_preflight_failure_qualifies_current_engine": (
                False
            ),
            "v17_first_owner_postflight_failure": source_only_v17_failure,
            "v17_first_owner_postflight_failure_qualifies_current_engine": (
                False
            ),
            "v19_first_owner_publication_failure": source_only_v19_failure,
            "v19_first_owner_publication_failure_qualifies_current_engine": (
                False
            ),
            "v22_first_proof_preflight_failure": source_only_v22_failure,
            "v22_first_proof_preflight_failure_qualifies_current_engine": (
                False
            ),
            "historical_v10_graph_qualifies_current_engine": False,
        }
        source_only_incidents = {
            **required_incidents,
            "source_only_extra_v14_zig_history": {
                "schema": "source-only-v27-independent-zig-history",
                "status": "FAIL",
            },
            "source_only_extra_v14_zig_qualifies_current_engine": False,
            "source_only_extra_v14_rust_history": {
                "schema": "source-only-v27-independent-rust-history",
                "status": "FAIL",
            },
            "source_only_extra_v14_rust_qualifies_current_engine": False,
        }
        source_only_history = {
            "preserved_v13_first_audit_failure": source_only_v13_failure,
            "preserved_v15_first_audit_failure": source_only_v15_failure,
            "preserved_v17_first_audit_failure": source_only_v17_failure,
            "preserved_v19_first_audit_failure": source_only_v19_failure,
        }
        source_only_state = {
            "v21": source_only_v21,
            "owner": source_only_owner,
            "v8": types.SimpleNamespace(
                load_contract=lambda: {"source_only": True},
            ),
            "audits": {
                "pins": dict(v22_failure_pins),
                "graph": dict(source_only_graph),
            },
            "snapshot": {
                "schema": "source-only-v27-original-family-snapshot",
                "family": "rust",
            },
            "history": source_only_history,
            "preserved_incidents": source_only_incidents,
            "controller": types.SimpleNamespace(source_only=True),
            "parent_environment": {"source_only": "preserved"},
        }

        def check_source_only_v24_state(
            state: Any,
            *,
            family: str = "rust",
            audits: Mapping[str, Any] = source_only_audits,
            fifth: Mapping[str, Any] = source_only_v22_failure,
        ) -> dict[str, Any]:
            return validate_current_v24_preflight_state(
                state,
                family=family,
                v21=source_only_v21,
                audits=audits,
                preserved_v22_failure=fifth,
            )

        check(
            "accept-exact-nine-field-v24-state-with-extra-v14-history",
            len(source_only_state) == 9
            and len(source_only_incidents) == 15
            and check_source_only_v24_state(source_only_state)
            is source_only_state,
        )
        minimal_state = dict(source_only_state)
        minimal_state["preserved_incidents"] = dict(required_incidents)
        check(
            "accept-five-genuine-v24-incidents-as-a-required-subset",
            len(minimal_state["preserved_incidents"]) == 11
            and check_source_only_v24_state(minimal_state) is minimal_state,
        )
        for field in tuple(source_only_state):
            removed = dict(source_only_state)
            removed.pop(field)
            reject(
                "reject-missing-source-only-v24-nine-field-state-" + field,
                lambda removed=removed: check_source_only_v24_state(removed),
            )
        invented_state = dict(source_only_state)
        invented_state["invented_tenth_state_field"] = True
        reject(
            "reject-extra-source-only-v24-nine-field-state",
            lambda: check_source_only_v24_state(invented_state),
        )
        for field, wrong in (
            ("v21", object()),
            ("owner", object()),
            ("audits", {}),
            ("snapshot", {"family": "vm"}),
            ("history", {}),
            ("preserved_incidents", {}),
        ):
            forged = dict(source_only_state)
            forged[field] = wrong
            reject(
                "reject-forged-source-only-v24-state-" + field,
                lambda forged=forged: check_source_only_v24_state(forged),
            )
        for field in tuple(source_only_history):
            forged = dict(source_only_state)
            forged["history"] = dict(source_only_history)
            forged["history"].pop(field)
            reject(
                "reject-missing-source-only-v24-preserved-history-" + field,
                lambda forged=forged: check_source_only_v24_state(forged),
            )
            forged = dict(source_only_state)
            forged["history"] = dict(source_only_history)
            forged["history"][field] = {"status": "PASS"}
            reject(
                "reject-forged-source-only-v24-preserved-history-" + field,
                lambda forged=forged: check_source_only_v24_state(forged),
            )
        for field in ("pins", "graph"):
            forged = dict(source_only_state)
            forged["audits"] = dict(source_only_state["audits"])
            forged["audits"].pop(field)
            reject(
                "reject-missing-source-only-v24-independent-audits-" + field,
                lambda forged=forged: check_source_only_v24_state(forged),
            )
            forged = dict(source_only_state)
            forged["audits"] = dict(source_only_state["audits"])
            forged["audits"][field] = {}
            reject(
                "reject-forged-source-only-v24-independent-audits-" + field,
                lambda forged=forged: check_source_only_v24_state(forged),
            )
        for field, actual in required_incidents.items():
            forged = dict(source_only_state)
            forged["preserved_incidents"] = dict(source_only_incidents)
            forged["preserved_incidents"].pop(field)
            reject(
                "reject-missing-source-only-v24-required-incident-" + field,
                lambda forged=forged: check_source_only_v24_state(forged),
            )
            forged = dict(source_only_state)
            forged["preserved_incidents"] = dict(source_only_incidents)
            forged["preserved_incidents"][field] = (
                True if actual is False else {"status": "PASS"}
            )
            reject(
                "reject-forged-source-only-v24-required-incident-" + field,
                lambda forged=forged: check_source_only_v24_state(forged),
            )
        for family in ("vm", "source-only-invented-family"):
            reject(
                "reject-foreign-source-only-v24-state-family-" + family,
                lambda family=family: check_source_only_v24_state(
                    source_only_state,
                    family=family,
                ),
            )
        forged_fifth = dict(source_only_v22_failure)
        forged_fifth["status"] = "PASS"
        reject(
            "reject-unbound-source-only-v24-fifth-preserved-incident",
            lambda: check_source_only_v24_state(
                source_only_state,
                fifth=forged_fifth,
            ),
        )
        for field in tuple(source_only_audits):
            removed_audits = dict(source_only_audits)
            removed_audits.pop(field)
            reject(
                "reject-missing-source-only-v24-owner-audit-field-" + field,
                lambda removed_audits=removed_audits:
                check_source_only_v24_state(
                    source_only_state,
                    audits=removed_audits,
                ),
            )

        check("retain-all-1376-genuine-public-compatibility-inputs",
              len(matrix) == EXPECTED_CASES)
        check("retain-all-43-independent-real-public-cohorts",
              len(base17.COHORTS) == EXPECTED_COHORTS)
        check("require-all-64-genuine-current-locale-cases",
              EXPECTED_LOCALE_CASES == 64)
        check("require-all-192-genuine-current-locale-transitions",
              EXPECTED_LOCALE_TRANSITIONS == 192)
        check("never-reuse-frozen-v21-report-or-failure-paths",
              not (set(APPROVED_OUTPUTS) & set(base19.APPROVED_OUTPUTS)))

        for cohort in base17.COHORTS:
            rows = [row for row in matrix if row["cohort"] == cohort]
            stimuli = [base17.build_stimulus(row) for row in rows]
            check("retain-32-source-local-current-public-rows-" + cohort,
                  len(rows) == 32)
            check("retain-32-actual-current-public-stimuli-" + cohort,
                  len({digest(row) for row in stimuli}) == 32)
            check("retain-32-genuinely-distinct-current-expressions-" + cohort,
                  len({row["expression"] for row in stimuli}) == 32)
            check("retain-32-genuinely-distinct-current-subjects-" + cohort,
                  len({row["subject"] for row in stimuli}) == 32)
        for symbol in base17.PUBLIC_EXPORTS:
            check("retain-genuine-current-public-export-" + symbol,
                  base17.PUBLIC_EXPORTS.count(symbol) == 1)
        for member in base17.PUBLIC_PATTERN_MEMBERS:
            check("retain-genuine-current-public-pattern-member-" + member,
                  base17.PUBLIC_PATTERN_MEMBERS.count(member) == 1)
        for member in base17.PUBLIC_MATCH_MEMBERS:
            check("retain-genuine-current-public-match-member-" + member,
                  base17.PUBLIC_MATCH_MEMBERS.count(member) == 1)

        configuration = _synthetic_configuration()
        check("authenticate-genuine-source-only-current-owner-context",
              verify_embedded_configuration(configuration) == configuration)
        for field in tuple(configuration):
            removed = dict(configuration)
            removed.pop(field)
            reject("reject-missing-current-native-owner-context-" + field,
                   lambda removed=removed: verify_embedded_configuration(removed))
        for field, wrong in (
            ("schema", "forged"), ("family", "foreign"),
            ("source_sha256", "not-a-hash"),
            ("protocol_sha256", "not-a-hash"),
            ("baseline_v19_source_sha256", "0" * 64),
            ("baseline_v19_protocol_sha256", "0" * 64),
            ("v19_reference_sha256", "0" * 64),
            ("v19_record_sha256", "0" * 64),
            ("matrix_sha256", "0" * 64),
            ("stimulus_sha256", "0" * 64),
            ("cases", EXPECTED_CASES - 1),
            ("iso8859_1_locale", ""), ("utf8_locale", ""),
            ("expected_native_sha256", {}),
        ):
            forged = dict(configuration)
            forged[field] = wrong
            reject("reject-forged-current-native-owner-context-" + field,
                   lambda forged=forged: verify_embedded_configuration(forged))

        actual_owner = base18._synthetic_owner_source()
        actual_hash = hashlib.sha256(actual_owner.encode("utf-8")).hexdigest()
        composed, composed_hash = compose_guarded_owner(
            actual_owner, owner_source_sha256=actual_hash,
        )
        check("parse-actual-source-only-current-native-owner",
              isinstance(ast.parse(composed), ast.Module))
        check("preserve-exact-source-only-original-current-owner",
              valid_sha256(composed_hash) and composed_hash != actual_hash)
        check("preload-current-evaluator-before-real-matcher-guard",
              composed.count(PRELOAD_INJECTION) == 1
              and composed.index(PRELOAD_INJECTION)
              < composed.index(PRELOAD_MARKER))
        check("match-exactly-once-inside-live-current-native-guard",
              composed.count(OBSERVATION_INJECTION) == 1
              and composed.index(OBSERVATION_INJECTION)
              < composed.index(AFTER_GUARD_MARKER))
        check("retain-all-original-current-owner-records",
              composed.count(OWNER_RECORD_INJECTION) == 1
              and composed.count(OWNER_RECORD_MARKER) == 1)
        check("never-import-a-candidate-in-the-guard-injection",
              "import candidates" not in PRELOAD_INJECTION
              and "import candidates" not in OBSERVATION_INJECTION
              and "sys.modules.get(_rebar27_candidate_name)"
              in OBSERVATION_INJECTION)
        for name, marker in (
            ("before-cached-matcher-poison", PRELOAD_MARKER),
            ("inside-live-native-owner", AFTER_GUARD_MARKER),
            ("inside-complete-original-owner", OWNER_RECORD_MARKER),
        ):
            removed = actual_owner.replace(marker, "", 1)
            removed_hash = hashlib.sha256(removed.encode("utf-8")).hexdigest()
            reject("reject-missing-current-native-owner-marker-" + name,
                   lambda removed=removed, removed_hash=removed_hash:
                   compose_guarded_owner(
                       removed, owner_source_sha256=removed_hash,
                   ))
            duplicated = actual_owner.replace(marker, marker + marker, 1)
            duplicate_hash = hashlib.sha256(duplicated.encode("utf-8")).hexdigest()
            reject("reject-duplicate-current-native-owner-marker-" + name,
                   lambda duplicated=duplicated, duplicate_hash=duplicate_hash:
                   compose_guarded_owner(
                       duplicated, owner_source_sha256=duplicate_hash,
                   ))

        good_pins = {
            name: hashlib.sha256(
                ("source-only-current-proof:" + name).encode("ascii"),
            ).hexdigest()
            for name in (
                "v21_source", "v21_protocol", "v24_source", "v24_protocol",
                "v21_base_report", "v21_strict_report",
                *(
                    family + "_" + kind
                    for family in FAMILIES
                    for kind in (
                        "edge_archive", "edge_proof", "deep_archive", "deep_proof",
                    )
                ),
            )
        }
        good_pins.update({
            "v21_source": V21_SOURCE_SHA256,
            "v21_protocol": V21_PROTOCOL_SHA256,
            "v24_source": V24_SOURCE_SHA256,
            "v24_protocol": V24_PROTOCOL_SHA256,
        })
        check("require-all-18-real-current-source-audit-and-proof-pins",
              len(current_proof_pins(good_pins)) == 18)
        for name, fingerprint in (
            ("v21_source", V21_SOURCE_SHA256),
            ("v21_protocol", V21_PROTOCOL_SHA256),
            ("v24_source", V24_SOURCE_SHA256),
            ("v24_protocol", V24_PROTOCOL_SHA256),
        ):
            check(
                "bind-only-root-reviewed-current-owner-or-proof-instruction-" + name,
                current_proof_pins(good_pins)[name] == fingerprint,
            )
            forged = dict(good_pins)
            forged[name] = hashlib.sha256(
                ("source-only-v27-valid-wrong-instruction:" + name).encode(
                    "ascii",
                ),
            ).hexdigest()
            reject(
                "reject-valid-alternative-current-owner-or-proof-sha256-" + name,
                lambda forged=forged: current_proof_pins(forged),
            )
        for name in tuple(good_pins):
            missing = dict(good_pins)
            missing.pop(name)
            reject("reject-missing-real-current-proof-pin-" + name,
                   lambda missing=missing: current_proof_pins(missing))
            forged = dict(good_pins)
            forged[name] = "not-a-real-sha256"
            reject("reject-forged-real-current-proof-pin-" + name,
                   lambda forged=forged: current_proof_pins(forged))
        for family in FAMILIES:
            for left, right in (
                ("edge_archive", "edge_proof"),
                ("deep_archive", "deep_proof"),
                ("edge_proof", "deep_proof"),
            ):
                reused = dict(good_pins)
                reused[family + "_" + right] = reused[family + "_" + left]
                reject("reject-reused-current-family-proof-" + family
                       + "-" + left + "-" + right,
                       lambda reused=reused: current_proof_pins(reused))

        for family in FAMILIES:
            seed = "source-only-v24-current-proof-" + family + "-"
            archive_hashes = {
                name: hashlib.sha256((seed + name).encode("ascii")).hexdigest()
                for name in (
                    "edge-archive", "edge-proof", "deep-archive", "deep-proof",
                )
            }
            edge_archive = (
                "candidates/evidence/" + seed + "edge-archive.json.gz"
            )
            edge_proof = (
                "candidates/audits/" + seed + "edge-owner-proof.json"
            )
            deep_archive = (
                "candidates/evidence/" + seed + "deep-archive.json"
            )
            deep_proof = (
                "candidates/audits/" + seed + "deep-owner-proof.json"
            )
            source_only_edge = {
                "status": "PASS",
                "campaign_qualified": True,
                "archive_path": edge_archive,
                "archive_sha256": archive_hashes["edge-archive"],
                "proof_path": edge_proof,
                "proof_sha256": archive_hashes["edge-proof"],
            }
            source_only_deep = {
                "status": "PASS",
                "campaign_qualified": True,
                "archive_path": deep_archive,
                "archive_sha256": archive_hashes["deep-archive"],
                "proof_path": deep_proof,
                "proof_sha256": archive_hashes["deep-proof"],
                "qualified_edge": dict(source_only_edge),
            }

            def source_descriptor(
                value: Any,
                *,
                kind: str,
                edge: Mapping[str, Any] | None = None,
                expected_family: str = family,
            ) -> dict[str, Any]:
                deep_kind = kind == "deep"
                return validate_current_v24_descriptor(
                    value,
                    family=expected_family,
                    kind=kind,
                    archive_relative=deep_archive if deep_kind else edge_archive,
                    archive_sha256=archive_hashes[
                        "deep-archive" if deep_kind else "edge-archive"
                    ],
                    proof_relative=deep_proof if deep_kind else edge_proof,
                    proof_sha256=archive_hashes[
                        "deep-proof" if deep_kind else "edge-proof"
                    ],
                    qualified_edge=edge,
                )

            check(
                "authenticate-exact-six-current-original-edge-fields-" + family,
                len(source_only_edge) == 6
                and source_descriptor(source_only_edge, kind="edge")
                == source_only_edge,
            )
            check(
                "authenticate-exact-seven-edge-bound-current-deep-fields-"
                + family,
                len(source_only_deep) == 7
                and source_descriptor(
                    source_only_deep,
                    kind="deep",
                    edge=source_only_edge,
                ) == source_only_deep,
            )
            for kind, descriptor in (
                ("edge", source_only_edge),
                ("deep", source_only_deep),
            ):
                expected_edge = source_only_edge if kind == "deep" else None
                for field in tuple(descriptor):
                    removed = dict(descriptor)
                    removed.pop(field)
                    reject(
                        "reject-missing-current-original-"
                        + family + "-" + kind + "-" + field,
                        lambda removed=removed, kind=kind,
                        expected_edge=expected_edge: source_descriptor(
                            removed, kind=kind, edge=expected_edge,
                        ),
                    )
                for field, wrong in (
                    ("status", "FAIL"),
                    ("campaign_qualified", False),
                    ("archive_path", "../forged"),
                    ("archive_sha256", "0" * 64),
                    ("proof_path", "../forged"),
                    ("proof_sha256", "0" * 64),
                ):
                    forged = dict(descriptor)
                    forged[field] = wrong
                    reject(
                        "reject-forged-current-original-"
                        + family + "-" + kind + "-" + field,
                        lambda forged=forged, kind=kind,
                        expected_edge=expected_edge: source_descriptor(
                            forged, kind=kind, edge=expected_edge,
                        ),
                    )
                extra = dict(descriptor)
                extra["unexpected"] = True
                reject(
                    "reject-extra-current-original-proof-field-"
                    + family + "-" + kind,
                    lambda extra=extra, kind=kind,
                    expected_edge=expected_edge: source_descriptor(
                        extra, kind=kind, edge=expected_edge,
                    ),
                )
            forged_edge = dict(source_only_edge)
            forged_edge["proof_sha256"] = archive_hashes["deep-proof"]
            forged_deep = dict(source_only_deep)
            forged_deep["qualified_edge"] = forged_edge
            reject(
                "reject-swapped-current-deep-edge-owner-" + family,
                lambda forged_deep=forged_deep: source_descriptor(
                    forged_deep, kind="deep", edge=source_only_edge,
                ),
            )
            reject(
                "reject-unbound-current-original-deep-edge-" + family,
                lambda source_only_deep=source_only_deep: source_descriptor(
                    source_only_deep, kind="deep", edge=None,
                ),
            )
            reject(
                "reject-foreign-current-original-proof-family-" + family,
                lambda source_only_edge=source_only_edge: source_descriptor(
                    source_only_edge,
                    kind="edge",
                    expected_family="foreign",
                ),
            )

        _, snapshots, _ = base19._synthetic_audited_graph()
        for family in FAMILIES:
            owner_fingerprint = hashlib.sha256(
                ("source-only-v27-real-owner:" + family).encode("ascii"),
            ).hexdigest()
            expected_native = {
                "source-only/" + family + "-current-native.elf":
                    owner_fingerprint,
            }
            actual_observation = {
                "schema": "source-only-v27-preserved-native-owner",
                "status": "PASS",
                "family": family,
                "genuine_native_sha256": owner_fingerprint,
            }
            captured = capture_current_native_owner(
                family,
                expected_native=expected_native,
                phase="before-matching",
                observe=lambda actual=actual_observation: dict(actual),
                validate=lambda actual: dict(actual),
            )
            check(
                "capture-full-owner-before-before-validating-" + family,
                captured["complete_original_observation"] == actual_observation
                and captured["validated_owner"] == actual_observation,
            )

            def reject_observed_owner(
                actual: Mapping[str, Any],
            ) -> dict[str, Any]:
                require(
                    False,
                    "source-only original owner validator failed after capture",
                )
                return dict(actual)

            try:
                capture_current_native_owner(
                    family,
                    expected_native=expected_native,
                    phase="before-matching",
                    observe=lambda actual=actual_observation: dict(actual),
                    validate=reject_observed_owner,
                )
            except PublicSurfaceV27WorkerFailure as error:
                details = error.details
                check(
                    "preserve-full-real-owner-before-validator-failure-"
                    + family,
                    error.role == family
                    and details.get("role") == family
                    and details.get("failure_stage")
                    == "validate-current-native-owner-before-matching"
                    and details.get("actual_native_owner_observation_preserved")
                    is True
                    and details.get("actual_native_owner_observation")
                    == actual_observation
                    and details.get("expected_native_sha256")
                    == expected_native
                    and bool(details.get("traceback")),
                )
            else:
                check(
                    "preserve-full-real-owner-before-validator-failure-"
                    + family,
                    False,
                )

            try:
                capture_current_native_owner(
                    family,
                    expected_native=expected_native,
                    phase="before-matching",
                    observe=lambda: None,
                    validate=lambda actual: dict(actual),
                )
            except PublicSurfaceV27WorkerFailure as error:
                details = error.details
                check(
                    "never-invent-missing-real-owner-before-observation-"
                    + family,
                    details.get("failure_stage")
                    == "observe-current-native-owner-before-matching"
                    and details.get("actual_native_owner_observation_preserved")
                    is False
                    and "actual_native_owner_observation" not in details,
                )
            else:
                check(
                    "never-invent-missing-real-owner-before-observation-"
                    + family,
                    False,
                )

        source_records = base19._synthetic_reference_failure(
            "reference_a",
            matrix,
            prefix_count=EXPECTED_CASES,
            failure_stage="postflight",
        )["completed_records"]
        success, observed, after = _synthetic_zero_exit_worker(
            "rust", source_records, snapshots["rust"], mode="pass",
        )
        check("retain-all-1376-current-zero-exit-source-only-observations",
              success["status"] == "PASS"
              and observed["records"] == source_records
              and len(observed["records"]) == EXPECTED_CASES
              and after["status"] == "PASS")
        for mode, expected in (
            ("malformed", "decode-owner-report"),
            ("mismatch", "validate-complete-public-observations"),
            ("augmented-owner", "validate-augmented-native-owner"),
            ("restored-owner", "validate-unmodified-original-native-owner"),
            ("snapshot", "validate-current-native-snapshot-after-matching"),
            ("owner-after", "validate-current-native-owner-after-matching"),
            ("final-snapshot", "validate-final-current-native-snapshot"),
        ):
            try:
                _synthetic_zero_exit_worker(
                    "rust", source_records, snapshots["rust"], mode=mode,
                )
            except PublicSurfaceV27WorkerFailure as error:
                details = error.details
                process = details.get("complete_original_worker_streams")
                check("preserve-full-zero-exit-current-owner-failure-" + mode,
                      error.role == "rust"
                      and details.get("role") == "rust"
                      and type(details.get("returncode")) is int
                      and details["returncode"] == 0
                      and details.get("failure_stage") == expected
                      and isinstance(process, dict)
                      and process.get("returncode") == 0
                      and details.get("stdout") == process.get("stdout")
                      and details.get("stderr") == process.get("stderr")
                      and restore_complete_stream(
                          process["stderr"],
                          label="source-only complete current stderr",
                      ) == b""
                      and isinstance(details.get("owner_before"), dict)
                      and isinstance(
                          details.get(
                              "complete_original_owner_before_observation",
                          ),
                          dict,
                      )
                      and valid_sha256(details.get("composed_worker_sha256"))
                      and bool(details.get("traceback")))
                if mode == "malformed":
                    check("never-invent-a-malformed-current-owner-document",
                          restore_complete_stream(
                              process["stdout"],
                              label="source-only malformed current owner",
                          ) == b'{"source-only-v27-malformed-zero-exit":'
                          and "actual_decoded_owner_report" not in details
                          and "completed_records" not in details)
                else:
                    check("retain-all-1376-current-failed-owner-records-" + mode,
                          isinstance(details.get("actual_decoded_owner_report"),
                                     dict)
                          and isinstance(
                              details.get("actual_embedded_public_observations"),
                              dict,
                          )
                          and details.get("completed_count") == EXPECTED_CASES
                          and len(details["completed_records"]) == EXPECTED_CASES
                          and restore_complete_stream(
                              process["stdout"],
                              label="source-only current complete worker stdout",
                          ) == canonical(
                              details["actual_decoded_owner_report"],
                          ) + b"\n")
                if mode == "mismatch":
                    mismatch = details.get("first_actual_public_mismatch")
                    check("retain-actual-first-current-public-mismatch",
                          isinstance(mismatch, dict)
                          and mismatch.get("index") == 14
                          and mismatch.get("case_id") == matrix[14]["id"]
                          and mismatch.get("expected_record") == source_records[14]
                          and mismatch.get("actual_record")
                          == details["completed_records"][14]
                          and mismatch["actual_record"]
                          != mismatch["expected_record"])
                if mode == "owner-after":
                    check("retain-the-actual-current-failed-owner-after",
                          isinstance(details.get("actual_observed_owner_after"),
                                     dict)
                          and details["actual_observed_owner_after"]
                          .get("status") == "FAIL")
                if mode in {"snapshot", "final-snapshot"}:
                    check("retain-actual-changed-current-source-snapshot-" + mode,
                          isinstance(
                              details.get("actual_observed_family_snapshot"),
                              Mapping,
                          )
                          and details["actual_observed_family_snapshot"]
                          != snapshots["rust"])
            else:
                check("preserve-full-zero-exit-current-owner-failure-" + mode,
                      False)

        publication_document = {
            "schema": "source-only-v27-authentic-publication",
            "status": "PASS",
            "actual": ["complete", "original", "bytes"],
            "python_only_tuple": ("root-verified-normalization", 161_316),
            "nested": {"python_only_tuple": ("preserved", "canonical")},
        }
        working = _SyntheticPublicationOperations()
        receipt = publish_with_receipt(
            publication_document,
            ALL_CANDIDATE_RELATIVE,
            operations=working,
        )
        check("retain-the-complete-current-source-only-publication-receipt",
              receipt.get("fully_published") is True
              and receipt.get("file_created") is True
              and receipt.get("directory_identity_verified") is True
              and receipt.get("bytes_written") == len(working.writes)
              and bytes(working.writes)
              == canonical(publication_document) + b"\n"
              and receipt.get("file_fsync_completed") is True
              and receipt.get("directory_fsync_completed") is True
              and receipt.get("file_closed") is True
              and receipt.get("readback_opened") is True
              and receipt.get("readback_bytes") == len(working.writes)
              and receipt.get("readback_sha256")
              == hashlib.sha256(bytes(working.writes)).hexdigest()
              and receipt.get("readback_exact_bytes_verified") is True
              and receipt.get("readback_canonical_document_verified") is True
              and receipt.get("readback_closed") is True
              and receipt.get("directory_closed") is True)
        write_calls = receipt.get("actual_write_calls")
        check(
            "retain-all-exact-real-17-byte-exclusive-write-attempts",
            isinstance(write_calls, list)
            and len(write_calls) > 1
            and all(
                isinstance(call, dict)
                and set(call) == {"requested_bytes", "returned_bytes"}
                and type(call.get("requested_bytes")) is int
                and type(call.get("returned_bytes")) is int
                and 0 < call["returned_bytes"] <= call["requested_bytes"]
                for call in write_calls
            )
            and sum(call["returned_bytes"] for call in write_calls)
            == receipt.get("bytes_written")
            == len(working.writes),
        )
        if isinstance(write_calls, list):
            previous_returns = 0
            for index, call in enumerate(write_calls):
                expected_requested = len(working.writes) - previous_returns
                expected_returned = min(expected_requested, 17)
                check(
                    "preserve-immediate-17-byte-exclusive-write-call-"
                    + str(index),
                    call.get("requested_bytes") == expected_requested
                    and call.get("returned_bytes") == expected_returned,
                )
                previous_returns += call.get("returned_bytes", 0)

        normalized_publication = json.loads(bytes(working.writes))
        check(
            "accept-authentic-json-normalization-of-original-python-tuples",
            normalized_publication != publication_document
            and normalized_publication["python_only_tuple"]
            == ["root-verified-normalization", 161_316]
            and normalized_publication["nested"]["python_only_tuple"]
            == ["preserved", "canonical"]
            and canonical(normalized_publication) + b"\n"
            == bytes(working.writes)
            and receipt.get("fully_published") is True,
        )
        for stage in (
            "directory-open", "directory-identity", "before-create",
            "first-write", "partial-write", "zero-write", "negative-write",
            "oversized-write", "boolean-write", "file-fsync", "file-close",
            "directory-fsync", "readback-open", "readback-read",
            "readback-partial", "readback-truncated", "readback-mismatch",
            "readback-noncanonical", "readback-close", "directory-close",
        ):
            operations = _SyntheticPublicationOperations(fail_at=stage)
            try:
                publish_with_receipt(
                    publication_document,
                    ALL_CANDIDATE_RELATIVE,
                    operations=operations,
                )
            except PublicSurfaceV27PublicationFailure as error:
                actual = error.receipt
                expect_created = stage not in {
                    "directory-open", "directory-identity", "before-create",
                }
                calls = actual.get("actual_write_calls")
                valid_written = (
                    sum(
                        call["returned_bytes"]
                        for call in calls
                        if isinstance(call, dict)
                        and type(call.get("returned_bytes")) is int
                        and type(call.get("requested_bytes")) is int
                        and 0 < call["returned_bytes"] <= call["requested_bytes"]
                    )
                    if isinstance(calls, list)
                    else -1
                )
                check("preserve-real-current-publication-syscall-stage-" + stage,
                      actual.get("fully_published") is False
                      and actual.get("file_created") is expect_created
                      and isinstance(calls, list)
                      and all(
                          isinstance(call, dict)
                          and set(call) == {
                              "requested_bytes", "returned_bytes",
                          }
                          for call in calls
                      )
                      and actual.get("bytes_written") == valid_written
                      and actual.get("bytes_written") == len(operations.writes)
                      and actual.get("exclusive_creation") is True
                      and actual.get("no_symlink_followed") is True
                      and bool(actual.get("traceback")))
                if stage == "partial-write":
                    check("retain-genuine-partial-current-publication-bytes",
                          0 < actual.get("bytes_written", 0)
                          < actual.get("expected_bytes", 0)
                          and actual.get("file_fsync_completed") is False
                          and operations.created is True
                          and isinstance(calls, list)
                          and len(calls) == 2
                          and calls[0].get("returned_bytes") == 17
                          and calls[1].get("requested_bytes")
                          == actual.get("expected_bytes", 0) - 17
                          and calls[1].get("returned_bytes") is None)
                if stage == "first-write":
                    check("retain-current-created-file-before-first-write-failure",
                          actual.get("file_created") is True
                          and actual.get("bytes_written") == 0
                          and isinstance(calls, list)
                          and len(calls) == 1
                          and calls[0].get("requested_bytes")
                          == actual.get("expected_bytes")
                          and calls[0].get("returned_bytes") is None)
                if stage in {
                    "zero-write", "negative-write",
                    "oversized-write", "boolean-write",
                }:
                    expected_invalid = {
                        "zero-write": 0,
                        "negative-write": -1,
                        "oversized-write": actual.get("expected_bytes", 0) + 1,
                        "boolean-write": True,
                    }[stage]
                    check(
                        "capture-exact-invalid-exclusive-syscall-return-" + stage,
                        actual.get("file_created") is True
                        and actual.get("bytes_written") == 0
                        and isinstance(calls, list)
                        and len(calls) == 1
                        and calls[0].get("requested_bytes")
                        == actual.get("expected_bytes")
                        and calls[0].get("returned_bytes") == expected_invalid
                        and type(calls[0].get("returned_bytes"))
                        is type(expected_invalid)
                        and actual.get("file_fsync_completed") is False,
                    )
                if stage == "directory-fsync":
                    check("retain-complete-current-file-before-dir-fsync-failure",
                          actual.get("file_fsync_completed") is True
                          and actual.get("directory_fsync_completed") is False)
                if stage.startswith("readback-"):
                    check(
                        "retain-both-durable-syncs-before-readback-failure-"
                        + stage,
                        actual.get("file_fsync_completed") is True
                        and actual.get("directory_fsync_completed") is True
                        and actual.get("bytes_written")
                        == actual.get("expected_bytes")
                        and actual.get("fully_published") is False,
                    )
                if stage == "readback-open":
                    check(
                        "never-invent-an-unopened-real-readback-descriptor",
                        actual.get("readback_opened") is False
                        and actual.get("readback_bytes") == 0,
                    )
                if stage == "readback-read":
                    check(
                        "retain-opened-real-readback-before-read-failure",
                        actual.get("readback_opened") is True
                        and actual.get("readback_bytes") == 0
                        and actual.get("readback_exact_bytes_verified") is False,
                    )
                if stage == "readback-partial":
                    check(
                        "retain-exact-actual-partial-readback-before-failure",
                        0 < actual.get("readback_bytes", 0)
                        < actual.get("expected_bytes", 0)
                        and actual.get("readback_exact_bytes_verified") is False,
                    )
                if stage in {"readback-truncated", "readback-mismatch",
                             "readback-noncanonical"}:
                    check(
                        "reject-malformed-original-canonical-readback-" + stage,
                        actual.get("readback_exact_bytes_verified") is False
                        and actual.get("readback_canonical_document_verified")
                        is False,
                    )
                if stage == "readback-close":
                    check(
                        "retain-verified-canonical-before-readback-close-failure",
                        actual.get("readback_exact_bytes_verified") is True
                        and actual.get("readback_canonical_document_verified")
                        is True
                        and actual.get("readback_closed") is False,
                    )
            else:
                check("preserve-real-current-publication-syscall-stage-" + stage,
                      False)

        for role in ("reference_a", "reference_b", *FAMILIES):
            document = {"schema": "source-only-v27-original-worker",
                        "status": "PASS", "role": role}
            process = {
                "role": role,
                "returncode": 0,
                "stdout": capture_complete_stream(canonical(document) + b"\n"),
                "stderr": capture_complete_stream(b""),
            }
            check("retain-complete-current-source-only-worker-stream-" + role,
                  validate_process_streams(
                      process, role=role, expected_document=document,
                  ) is process)
            for label, forged in (
                ("false", False), ("true", True), ("none", None),
                ("negative", -1), ("failed", 1),
            ):
                substituted = copy.deepcopy(process)
                substituted["returncode"] = forged
                reject("reject-forged-current-native-exit-"
                       + role + "-" + label,
                       lambda substituted=substituted, role=role,
                       document=document: validate_process_streams(
                           substituted, role=role, expected_document=document,
                       ))
            for field, forged in (
                ("bytes", 0), ("sha256", "0" * 64),
                ("complete", False), ("base64", "forged!"),
            ):
                substituted = copy.deepcopy(process)
                substituted["stdout"][field] = forged
                reject("reject-incomplete-current-native-original-stream-"
                       + role + "-" + field,
                       lambda substituted=substituted, role=role,
                       document=document: validate_process_streams(
                           substituted, role=role, expected_document=document,
                       ))

        for label, relative in (
            ("absolute", "/tmp/forged-v27.json"),
            ("parent", "../forged-v27.json"),
            ("nested-parent", "candidates/../forged-v27.json"),
            ("backslash", "candidates\\forged-v27.json"),
            ("nul", "candidates/forged\x00-v27.json"),
            ("actual-base18-failure", BASE18_FAILURE_RELATIVE),
            ("actual-v13-failure", V13_FAILURE_RELATIVE),
            ("actual-v15-failure", V15_FAILURE_RELATIVE),
            ("actual-v17-post-owner-failure", V17_FAILURE_RELATIVE),
            ("actual-v19-publication-failure", V19_FAILURE_RELATIVE),
            ("actual-v22-integration-failure", V22_FAILURE_RELATIVE),
            ("actual-v19-nonqualifying-inner-pass",
             V19_FAILED_EMBEDDED_RELATIVE),
            ("actual-v19-reference", BASE19_REFERENCE_RELATIVE),
        ):
            reject("reject-dangerous-or-historical-current-output-" + label,
                   lambda relative=relative:
                   safe_relative(relative, outputs_only=True))
        for relative in sorted(APPROVED_OUTPUTS):
            check("allow-only-an-additive-v27-output-"
                  + relative.rsplit("/", 1)[-1],
                  safe_relative(relative, outputs_only=True) == relative)

        for name, counter in (
            ("read-no-real-current-evidence-candidates-audits-or-holdouts",
             "files_read"),
            ("write-no-bytecode-reports-or-current-production-evidence",
             "files_written"),
            ("start-no-current-native-reference-or-proof-workers", "processes"),
            ("start-no-current-background-oracle-threads", "threads"),
            ("sample-no-current-correctness-or-performance-clocks",
             "clock_samples"),
            ("draw-no-current-production-entropy", "entropy_draws"),
            ("change-no-real-current-global-locale", "locale_changes"),
            ("import-no-current-production-candidate", "candidate_imports"),
            ("execute-no-standard-library-regular-expression-match",
             "regex_matches"),
        ):
            check(name, effects[counter] == 0)

    failed = [item["name"] for item in checks if item["passed"] is not True]
    require(not failed,
            "a real current V27 candidate-free poison failed: "
            + ", ".join(failed))
    require(
        len(checks) >= 1_000,
        "at least 1000 distinct current V27 source-only controls are required",
    )
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "protocol_path": PROTOCOL_RELATIVE,
        "baseline_v19_source_sha256": BASE19_SOURCE_SHA256,
        "baseline_v19_protocol_sha256": BASE19_PROTOCOL_SHA256,
        "v19_actual_reference_sha256": BASE19_REFERENCE_SHA256,
        "v19_actual_reference_record_sha256": BASE19_REFERENCE_RECORD_SHA256,
        "preserved_v18_failure_sha256": BASE18_FAILURE_SHA256,
        "preserved_v13_failure_sha256": V13_FAILURE_SHA256,
        "preserved_v15_failure_sha256": V15_FAILURE_SHA256,
        "preserved_v17_failure_sha256": V17_FAILURE_SHA256,
        "preserved_v19_failure_sha256": V19_FAILURE_SHA256,
        "preserved_v19_embedded_report_sha256": V19_FAILED_EMBEDDED_SHA256,
        "preserved_v19_embedded_report_bytes": V19_FAILED_EMBEDDED_BYTES,
        "preserved_v19_outer_controller_status": "FAIL",
        "preserved_v22_failure_sha256": V22_FAILURE_SHA256,
        "preserved_v22_native_owner_workers_started": 0,
        "preserved_v22_original_edge_workers_started": 0,
        "preserved_v22_original_deep_workers_started": 0,
        "preserved_v22_combined_traceback_lines": 24,
        "preserved_v22_inline_source_lines": 25,
        "authentic_v13_failure_field_count": 26,
        "authentic_v13_failure_stage": V13_FAILURE_ACTUAL_STAGE,
        "preserved_v19_embedded_document_status": "PASS",
        "preserved_v19_embedded_pass_qualifies_current_build": False,
        "preserved_v17_actual_native_owner_workers": 3,
        "preserved_v17_owner_observations": (
            "NOT PRESERVED BY THE FAILED CONTROLLER"
        ),
        "historical_failure_qualifies_current_build": False,
        "check_count": len(checks),
        "inherited_v19_check_count": inherited["check_count"],
        "inherited_v18_check_count": inherited["inherited_v18_check_count"],
        "inherited_v17_check_count": inherited["inherited_v17_check_count"],
        "total_independent_source_controls": (
            len(checks) + inherited["total_independent_source_controls"]
        ),
        "failed": [],
        "cases": EXPECTED_CASES,
        "cohorts": EXPECTED_COHORTS,
        "distinct_behavioral_stimuli": EXPECTED_CASES,
        "additional_cases": EXPECTED_ADDITIONAL_CASES,
        "real_locale_cases": EXPECTED_LOCALE_CASES,
        "real_locale_transitions": EXPECTED_LOCALE_TRANSITIONS,
        "matrix_sha256": MATRIX_SHA256,
        "stimulus_sha256": STIMULUS_SHA256,
        "required_current_v21_owner_source_sha256": V21_SOURCE_SHA256,
        "required_current_v21_owner_protocol_sha256": V21_PROTOCOL_SHA256,
        "required_current_v21_all_family_audits": 2,
        "required_current_v24_proof_source_sha256": V24_SOURCE_SHA256,
        "required_current_v24_proof_protocol_sha256": V24_PROTOCOL_SHA256,
        "required_current_v24_original_archives": 6,
        "required_current_v24_durable_owner_proofs": 6,
        "current_candidate_evidence": "NOT QUALIFIED",
        "declared_immutable_instruction_files_read": 6,
        "candidate_source_files_read": effects["files_read"],
        "evidence_files_read": effects["files_read"],
        "v21_source_files_read": 0,
        "v24_source_files_read": 0,
        "files_written": effects["files_written"],
        "candidate_imports": effects["candidate_imports"],
        "subprocesses": effects["processes"],
        "threads_started": effects["threads"],
        "clock_samples": effects["clock_samples"],
        "entropy_draws": effects["entropy_draws"],
        "locale_changes": effects["locale_changes"],
        "regex_matching_calls": effects["regex_matches"],
        "reference_oracle_executed": False,
        "candidate_oracle_executed": False,
        "report_written": False,
        "subinterpreter_coverage": "NOT RUN",
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--self-oracle", action="store_true")
    modes.add_argument("--candidate", choices=("all",))
    parser.add_argument("--source-sha256")
    parser.add_argument("--protocol-sha256")
    parser.add_argument("--v21-source-sha256")
    parser.add_argument("--v21-protocol-sha256")
    parser.add_argument("--v24-source-sha256")
    parser.add_argument("--v24-protocol-sha256")
    parser.add_argument("--v21-base-report-sha256")
    parser.add_argument("--v21-strict-report-sha256")
    parser.add_argument("--iso8859-1-locale", dest="iso8859_1_locale")
    parser.add_argument("--utf8-locale")
    for family in FAMILIES:
        for kind in ("edge-archive", "edge-proof", "deep-archive", "deep-proof"):
            parser.add_argument("--" + family + "-" + kind + "-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    try:
        if options.self_test:
            result = self_test()
        elif options.self_oracle:
            result = run_self_oracle(options)
        else:
            result = run_all_candidates(options)
        sys.stdout.write(canonical(result).decode("ascii") + "\n")
        return 0 if result.get("status") == "PASS" else 1
    except (
        PublicSurfaceV27Error, base17.PublicSurfaceError,
        base18.PublicSurfaceV18Error, base19.PublicSurfaceV19Error,
        AssertionError, OSError, subprocess.SubprocessError,
        ValueError, TypeError, KeyError, UnicodeError, json.JSONDecodeError,
    ) as error:
        sys.stderr.write(canonical({
            "schema": SCHEMA,
            "status": "FAIL",
            **error_details(error),
            "performance": "NOT MEASURED",
        }).decode("ascii") + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
