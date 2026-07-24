#!/usr/bin/env python3
"""Check all frozen public regex cases inside the genuine guarded native owner.

The only intentionally opened inputs in ``--self-test`` are the two explicitly
declared, already frozen V17 source and protocol. No evidence, candidate,
holdout, report, clock, process, locale, or regular-expression match is read or
executed. The real candidate path requires the complete two-reference V18
baseline, both passing V10 audits, and every exact V11 archive-and-proof pair.
"""

from __future__ import annotations

import argparse
import ast
import base64
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
from collections.abc import Mapping
from typing import Any, Callable, Iterator


ROOT = Path(os.path.abspath(__file__)).parent.parent
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

# This one immutable, explicit source dependency is loaded before the
# candidate-free effect boundary. It is neither evidence nor a matching run.
from tools import python_re_public_surface_oracle_stage17 as v17


SCHEMA = "rebar-python-re-guarded-durable-public-surface-v18"
SOURCE_RELATIVE = "tools/python_re_public_surface_oracle_stage18.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-SURFACE-V18.md"
V17_SOURCE_RELATIVE = "tools/python_re_public_surface_oracle_stage17.py"
V17_SOURCE_SHA256 = (
    "cc36700fd5e43ed409472423a74b7da686804b09c92511d90bec863026c25bf8"
)
V17_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-SURFACE-V17.md"
V17_PROTOCOL_SHA256 = (
    "a703805d1cc711488f84bf4d5a4596de8ef194fd47a2116162ec6a490a3da0e5"
)
V11_SOURCE_RELATIVE = "tools/postfinal_current_build_proofs_v11.py"
V11_SOURCE_SHA256 = (
    "2895dd28b3dc69985cc0f6f8575398e8b8b10f58141f0612645a687478da9f04"
)
V11_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V11.md"
V11_PROTOCOL_SHA256 = (
    "334405521f2f945cc58cabf246cf8f784e8a6a5be7091a20587b0daf428412af"
)
V10_OWNER_RELATIVE = "tools/postfinal_from_scratch_audit_v10.py"
V10_OWNER_SHA256 = (
    "0c4d3f07bb51b0ce5ddc148810cb157d21067ddb07b578d3a793aaac5c671505"
)
V10_STRICT_RELATIVE = "tools/postfinal_no_delegation_audit_v10.py"
V10_STRICT_SHA256 = (
    "885168bd6df92ac9cabc8fc78a8389ee487f0be8d3c7fe67a393e984011b8d95"
)
V10_OWNERSHIP_PROTOCOL_RELATIVE = (
    "candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V10.md"
)
V10_OWNERSHIP_PROTOCOL_SHA256 = (
    "902bc095d08331089dcc1d1d11233747438a0cacb0cf1057ae41a2474bde2fa6"
)
FAMILIES = ("rust", "vm", "zig")
CONTRACT_NAMES = {"rust": "RUST", "vm": "C", "zig": "ZIG"}
V10_BASE_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V10.json"
)
V10_STRICT_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V10.json"
)
V11_EDGE_ARCHIVE_RELATIVES = {
    family: (
        "candidates/evidence/rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v11-qualified-pass.json.gz"
    )
    for family in FAMILIES
}
V11_EDGE_PROOF_RELATIVES = {
    family: (
        "candidates/evidence/rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v11-qualified-pass-proof.json"
    )
    for family in FAMILIES
}
V11_DEEP_ARCHIVE_RELATIVES = {
    family: (
        "candidates/audits/RUST-V8-DEEP-CONTRACT-"
        + CONTRACT_NAMES[family]
        + "-POSTFINAL-CURRENT-BUILD-V11-PASS.json.gz"
    )
    for family in FAMILIES
}
V11_DEEP_PROOF_RELATIVES = {
    family: (
        "candidates/audits/RUST-V8-DEEP-CONTRACT-"
        + CONTRACT_NAMES[family]
        + "-POSTFINAL-CURRENT-BUILD-V11-PASS-PROOF.json"
    )
    for family in FAMILIES
}

SELF_ORACLE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-surface-v18-self-oracle.json"
)
SELF_ORACLE_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-surface-v18-self-oracle-failures.json"
)
ALL_CANDIDATE_RELATIVE = (
    "candidates/evidence/python-re-public-surface-v18-all.json"
)
CANDIDATE_FAILURE_RELATIVES = {
    family: (
        "candidates/evidence/python-re-public-surface-v18-"
        + family + "-failures.json"
    )
    for family in FAMILIES
}
APPROVED_OUTPUTS = frozenset({
    SELF_ORACLE_RELATIVE,
    SELF_ORACLE_FAILURE_RELATIVE,
    ALL_CANDIDATE_RELATIVE,
    *CANDIDATE_FAILURE_RELATIVES.values(),
})
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_REPORT_BYTES = 64 * 1024 * 1024
MAX_ARCHIVE_BYTES = 32 * 1024 * 1024
MAX_WORKER_BYTES = 48 * 1024 * 1024
EXPECTED_CASES = 1376
EXPECTED_COHORTS = 43
EXPECTED_ADDITIONAL_CASES = 736
EXPECTED_LOCALE_CASES = 64
EXPECTED_LOCALE_TRANSITIONS = 192
MATRIX_SHA256 = (
    "7885a9ac0b2e22db88db7dc4ab9c33c4ba229ddb6d15fcdd4bfe9b0d6f10e8aa"
)
STIMULUS_SHA256 = (
    "8c1a4fd434af5fb1ea0dcd1aa3faaa06b07e7d186ca52c1593575eff93b4d7da"
)

PRELOAD_MARKER = (
    "matcher_descendant_names, matcher_descendant_originals, \\\n"
    "    matcher_descendant_aliases, matcher_alias_replacements = (\n"
    "        _install_real_cached_matcher_guards()\n"
    "    )\n"
)
AFTER_GUARD_MARKER = (
    'matcher_descendant_guards_after = '
    '_verify_real_cached_matcher_guards("after")\n'
)
OWNER_RECORD_MARKER = '    "stage07_guard_sentinel": stage07_guard_sentinel,\n'
PRELOAD_INJECTION = (
    "# BEGIN FROZEN V18 PRELOAD BEFORE CACHED-MATCHER POISON\n"
    "import os as _rebar18_os\n"
    "import json as _rebar18_json\n"
    "import importlib as _rebar18_importlib\n"
    "_rebar18_configuration = _rebar18_json.loads(\n"
    "    _rebar18_os.environ[\"REBAR_PUBLIC_SURFACE_V18_CONTEXT\"]\n"
    ")\n"
    "if any(_rebar18_name in sys.modules for _rebar18_name in (\n"
    "    \"candidates.rust_candidate\", \"candidates.vm_candidate\",\n"
    "    \"candidates.zig_candidate\",\n"
    ")):\n"
    "    raise RuntimeError(\"a candidate loaded before the V10 guard\")\n"
    "_rebar18_surface = _rebar18_importlib.import_module(\n"
    "    \"tools.python_re_public_surface_oracle_stage18\"\n"
    ")\n"
    "_rebar18_surface.verify_embedded_configuration(_rebar18_configuration)\n"
    "# END FROZEN V18 PRELOAD BEFORE CACHED-MATCHER POISON\n"
)
OBSERVATION_INJECTION = (
    "# BEGIN FROZEN V18 MATCHING INSIDE THE LIVE V10 GUARD\n"
    "_rebar18_candidate_name = (\n"
    "    \"candidates.\" + _rebar18_configuration[\"family\"] + \"_candidate\"\n"
    ")\n"
    "_rebar18_candidate = sys.modules.get(_rebar18_candidate_name)\n"
    "if _rebar18_candidate is None:\n"
    "    raise RuntimeError(\"the live guarded candidate was not imported\")\n"
    "if getattr(_rebar18_candidate, \"__name__\", None) != _rebar18_candidate_name:\n"
    "    raise RuntimeError(\"the live guarded candidate was substituted\")\n"
    "_rebar18_public_observation = _rebar18_surface.guarded_public_records(\n"
    "    _rebar18_candidate, _rebar18_configuration,\n"
    ")\n"
    "# END FROZEN V18 MATCHING INSIDE THE LIVE V10 GUARD\n"
)
OWNER_RECORD_INJECTION = (
    '    "rebar_v18_guarded_public_surface": '
    '_rebar18_public_observation,\n'
)


class PublicSurfaceV18Error(AssertionError):
    """A real frozen public case or native ownership obligation failed."""


class PublicSurfaceV18WorkerFailure(PublicSurfaceV18Error):
    """Keep an actual isolated worker's real streams and partial records."""

    def __init__(self, role: str, message: str, details: Mapping[str, Any]):
        super().__init__(message)
        self.role = role
        self.details = dict(details)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise PublicSurfaceV18Error(message)


def valid_sha256(value: Any) -> bool:
    return v17.valid_sha256(value)


def canonical(value: Any) -> bytes:
    return v17.canonical(value)


def digest(value: Any) -> str:
    return v17.digest(value)


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == str(v17.PINNED_PYTHON)
        and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
        and os.path.abspath(v17.__file__) == str(ROOT / V17_SOURCE_RELATIVE)
        and v17.SCHEMA == "rebar-python-re-independent-public-surface-v17"
        and v17.SOURCE_RELATIVE == V17_SOURCE_RELATIVE
        and v17.PROTOCOL_RELATIVE == V17_PROTOCOL_RELATIVE
        and v17.MATRIX_SHA256 == MATRIX_SHA256
        and v17.STIMULUS_SHA256 == STIMULUS_SHA256
        and v17.EXPECTED_CASES == EXPECTED_CASES
        and len(v17.COHORTS) == EXPECTED_COHORTS
        and v17.EXPECTED_ADDITIONAL_CASES == EXPECTED_ADDITIONAL_CASES
        and v17.V5_REFERENCE_SHA256
        == "3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916",
        "the exact pinned Python or immutable 1,376-case V17 source changed",
    )


def authenticate_frozen_v17() -> None:
    verify_runtime()
    v17._read_bounded(
        V17_SOURCE_RELATIVE, MAX_SOURCE_BYTES, expected=V17_SOURCE_SHA256,
    )
    v17._read_bounded(
        V17_PROTOCOL_RELATIVE, MAX_SOURCE_BYTES, expected=V17_PROTOCOL_SHA256,
    )


def safe_relative(relative: Any, *, outputs_only: bool = False) -> str:
    require(type(relative) is str, "an exact repository-relative path is required")
    path = PurePosixPath(relative)
    require(
        not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in relative
        and "\x00" not in relative
        and path.as_posix() == relative
        and (not outputs_only or relative in APPROVED_OUTPUTS),
        "refusing an unapproved, escaping, or reused correctness evidence path",
    )
    return relative


def read_frozen(relative: str, expected: str, maximum: int) -> bytes:
    safe_relative(relative)
    require(valid_sha256(expected),
            "an actual independently observed frozen SHA-256 is required")
    return v17._read_bounded(relative, maximum, expected=expected)


def _strict_canonical(payload: bytes, label: str) -> dict[str, Any]:
    try:
        document = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=v17._unique_json_pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(
                PublicSurfaceV18Error("a non-finite proof was forged: " + value),
            ),
        )
    except (ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise PublicSurfaceV18Error(
            "the complete canonical real proof is malformed: " + label,
        ) from error
    require(
        isinstance(document, dict)
        and payload in {canonical(document), canonical(document) + b"\n"},
        "an independently published real proof is not complete canonical JSON: "
        + label,
    )
    return document


def capture_complete_stream(raw: bytes) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= MAX_WORKER_BYTES,
            "a complete actual worker stream must be bounded original bytes")
    return {
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "complete": True,
        "base64": base64.b64encode(raw).decode("ascii"),
    }


def restore_complete_stream(record: Any, *, label: str) -> bytes:
    require(
        isinstance(record, dict)
        and set(record) == {"bytes", "sha256", "complete", "base64"}
        and type(record.get("bytes")) is int
        and 0 <= record["bytes"] <= MAX_WORKER_BYTES
        and valid_sha256(record.get("sha256"))
        and record.get("complete") is True
        and type(record.get("base64")) is str,
        "the complete independently retained worker stream was forged: " + label,
    )
    try:
        payload = base64.b64decode(record["base64"].encode("ascii"), validate=True)
    except (ValueError, UnicodeError, base64.binascii.Error) as error:
        raise PublicSurfaceV18Error(
            "the complete original worker stream is invalid base64: " + label,
        ) from error
    require(
        len(payload) == record["bytes"]
        and hashlib.sha256(payload).hexdigest() == record["sha256"]
        and capture_complete_stream(payload) == record,
        "the exact retained worker stream bytes changed: " + label,
    )
    return payload


def validate_process_streams(
    process: Any,
    *,
    role: str,
    expected_document: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        isinstance(process, dict)
        and set(process) == {"role", "returncode", "stdout", "stderr"}
        and process.get("role") == role
        and process.get("returncode") == 0,
        "the genuine isolated correctness worker returned an invalid exit code",
    )
    stdout = restore_complete_stream(process.get("stdout"), label=role + " stdout")
    stderr = restore_complete_stream(process.get("stderr"), label=role + " stderr")
    require(stderr == b"", "the genuine isolated worker concealed actual stderr")
    decoded = _strict_canonical(stdout, role + " complete original stdout")
    require(decoded == dict(expected_document),
            "the complete actual worker stdout does not equal its retained report")
    return process


def build_matrix() -> list[dict[str, Any]]:
    matrix = v17.build_matrix()
    require(
        v17.validate_matrix(matrix, expected_sha256=MATRIX_SHA256)
        == MATRIX_SHA256,
        "the independently frozen exact 1,376-case matrix changed",
    )
    semantic = v17.validate_stimuli(matrix, expected_sha256=STIMULUS_SHA256)
    require(
        semantic.get("cases") == EXPECTED_CASES
        and semantic.get("cohorts") == EXPECTED_COHORTS
        and semantic.get("additional_cases") == EXPECTED_ADDITIONAL_CASES
        and semantic.get("distinct_stimuli") == EXPECTED_CASES
        and semantic.get("stimulus_sha256") == STIMULUS_SHA256,
        "a complete V17 public input or semantic variant was omitted",
    )
    return matrix


def validate_public_records(records: Any) -> str:
    matrix = build_matrix()
    try:
        result = v17.validate_records(records, matrix)
    except (v17.PublicSurfaceError, ValueError, TypeError, KeyError) as error:
        raise PublicSurfaceV18Error(
            "a full public record, true locale transition, or exception changed",
        ) from error
    require(valid_sha256(result), "all actual public records must be retained")
    return result


def proof_pin_values(values: Mapping[str, Any]) -> dict[str, str]:
    names = (
        "v10_base_report", "v10_strict_report",
        *(
            family + "_" + kind
            for family in FAMILIES
            for kind in (
                "edge_archive", "edge_proof", "deep_archive", "deep_proof",
            )
        ),
    )
    require(
        isinstance(values, Mapping)
        and set(values) == set(names)
        and all(valid_sha256(values.get(name)) for name in names)
        and len({values[name] for name in names}) == len(names),
        "BLOCKED: independently publish both genuine all-family V10 report "
        "hashes and all 12 distinct qualified V11 original-archive and "
        "complete durable-owner-proof hashes",
    )
    return {name: str(values[name]) for name in names}


def verify_embedded_configuration(value: Any) -> dict[str, Any]:
    require(
        isinstance(value, dict)
        and set(value) == {
            "schema", "family", "source_sha256", "protocol_sha256",
            "v17_source_sha256", "v17_protocol_sha256", "matrix_sha256",
            "stimulus_sha256", "cases", "iso8859_1_locale", "utf8_locale",
            "expected_native_sha256",
        }
        and value.get("schema") == SCHEMA + "-embedded-configuration"
        and value.get("family") in FAMILIES
        and valid_sha256(value.get("source_sha256"))
        and valid_sha256(value.get("protocol_sha256"))
        and value.get("v17_source_sha256") == V17_SOURCE_SHA256
        and value.get("v17_protocol_sha256") == V17_PROTOCOL_SHA256
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
        and all(
            type(relative) is str and valid_sha256(actual)
            for relative, actual in value["expected_native_sha256"].items()
        ),
        "an exact guarded same-process public worker configuration was forged",
    )
    return dict(value)


def compose_guarded_owner(
    owner_source: str,
    *,
    owner_source_sha256: str,
) -> tuple[str, str]:
    require(
        type(owner_source) is str
        and valid_sha256(owner_source_sha256)
        and hashlib.sha256(owner_source.encode("utf-8")).hexdigest()
        == owner_source_sha256,
        "the exact complete frozen V10 native owner worker was substituted",
    )
    for marker, label in (
        (PRELOAD_MARKER, "before the original cached-matcher poison"),
        (AFTER_GUARD_MARKER, "before the genuine original after guards"),
        (OWNER_RECORD_MARKER, "inside the unchanged complete owner record"),
    ):
        require(
            owner_source.count(marker) == 1,
            "the genuine native owner has no unique V18 insertion point " + label,
        )
    require(
        owner_source.index(PRELOAD_MARKER)
        < owner_source.index(AFTER_GUARD_MARKER)
        < owner_source.index(OWNER_RECORD_MARKER),
        "the genuine live guard and candidate evidence order was changed",
    )
    try:
        original_tree = ast.parse(owner_source)
    except SyntaxError as error:
        raise PublicSurfaceV18Error(
            "the genuine frozen V10 native-owner process cannot be parsed",
        ) from error
    composed = owner_source.replace(
        PRELOAD_MARKER, PRELOAD_INJECTION + PRELOAD_MARKER, 1,
    )
    composed = composed.replace(
        AFTER_GUARD_MARKER, OBSERVATION_INJECTION + AFTER_GUARD_MARKER, 1,
    )
    composed = composed.replace(
        OWNER_RECORD_MARKER, OWNER_RECORD_INJECTION + OWNER_RECORD_MARKER, 1,
    )
    try:
        composed_tree = ast.parse(composed)
    except SyntaxError as error:
        raise PublicSurfaceV18Error(
            "the exactly composed guarded public worker is invalid Python",
        ) from error
    original_imports = {
        alias.name
        for node in ast.walk(original_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    composed_imports = {
        alias.name
        for node in ast.walk(composed_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    require(
        composed_imports - original_imports <= {"os", "json", "importlib"}
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in composed_imports - original_imports
        )
        and composed.count(PRELOAD_INJECTION) == 1
        and composed.count(OBSERVATION_INJECTION) == 1
        and composed.count(OWNER_RECORD_INJECTION) == 1
        and composed.count(AFTER_GUARD_MARKER) == 1
        and composed.index(PRELOAD_INJECTION) < composed.index(PRELOAD_MARKER)
        and composed.index(OBSERVATION_INJECTION)
        < composed.index(AFTER_GUARD_MARKER)
        and composed.index(OWNER_RECORD_INJECTION)
        < composed.index(OWNER_RECORD_MARKER),
        "the public work was not exactly once inside the live native guard",
    )
    restored = composed.replace(
        PRELOAD_INJECTION + PRELOAD_MARKER, PRELOAD_MARKER, 1,
    ).replace(
        OBSERVATION_INJECTION + AFTER_GUARD_MARKER, AFTER_GUARD_MARKER, 1,
    ).replace(
        OWNER_RECORD_INJECTION + OWNER_RECORD_MARKER, OWNER_RECORD_MARKER, 1,
    )
    require(
        restored == owner_source
        and hashlib.sha256(restored.encode("utf-8")).hexdigest()
        == owner_source_sha256,
        "the original frozen native owner or any genuine guard was modified",
    )
    return composed, hashlib.sha256(composed.encode("utf-8")).hexdigest()


def guarded_public_records(
    module: Any,
    configuration: Mapping[str, Any],
) -> dict[str, Any]:
    settings = verify_embedded_configuration(configuration)
    family = settings["family"]
    expected_name = "candidates." + family + "_candidate"
    require(
        getattr(module, "__name__", None) == expected_name
        and sys.modules.get(expected_name) is module,
        "the selected public module is not the already-guarded actual owner",
    )
    authenticate_frozen_v17()
    read_frozen(SOURCE_RELATIVE, settings["source_sha256"], MAX_SOURCE_BYTES)
    read_frozen(PROTOCOL_RELATIVE, settings["protocol_sha256"], MAX_SOURCE_BYTES)
    matrix = build_matrix()
    locale_names = {
        "iso8859_1": settings["iso8859_1_locale"],
        "utf8": settings["utf8_locale"],
    }
    locale_preflight = v17._preflight_real_locales(locale_names)
    records: list[dict[str, Any]] = []
    active: str | None = None
    try:
        for row in matrix:
            active = row["id"]
            actual = v17.evaluate_case(module, row, locale_names=locale_names)
            if row["cohort"] in v17.ADDITIONAL_COHORTS:
                require(actual["outcome"]["status"] == "return",
                        "an actual guarded public probe failed")
            if row["cohort"] in {
                "real-locale-switch-on-compiled-bytes",
                "real-locale-invalid-flags-and-cache",
            }:
                v17._validate_locale_case(actual)
            records.append(actual)
            active = None
    except (BaseException, v17.PublicSurfaceError) as error:
        raise PublicSurfaceV18WorkerFailure(
            family,
            "the real guarded public candidate stopped inside its native owner",
            {
                "completed_records": records,
                "completed_count": len(records),
                "active_case": active,
                "actual_error": v17.normalize(error),
            },
        ) from error
    return {
        "schema": SCHEMA + "-embedded-public-records",
        "status": "PASS",
        "family": family,
        "candidate_module": expected_name,
        "source_sha256": settings["source_sha256"],
        "protocol_sha256": settings["protocol_sha256"],
        "v17_source_sha256": V17_SOURCE_SHA256,
        "v17_protocol_sha256": V17_PROTOCOL_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "stimulus_sha256": STIMULUS_SHA256,
        "cases": EXPECTED_CASES,
        "successful_additional_cases": EXPECTED_ADDITIONAL_CASES,
        "successful_real_locale_cases": EXPECTED_LOCALE_CASES,
        "real_locale_transition_count": EXPECTED_LOCALE_TRANSITIONS,
        "locale_preflight": locale_preflight,
        "expected_native_sha256": settings["expected_native_sha256"],
        "records": records,
        "record_sha256": validate_public_records(records),
        "matched_inside_live_v10_owner_guard": True,
        "candidate_imported_by_frozen_owner_only": True,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
    }


def validate_embedded_records(
    document: Any,
    *,
    family: str,
    source_sha256: str,
    protocol_sha256: str,
    expected_native: Mapping[str, str],
    baseline: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    require(
        isinstance(document, dict)
        and document.get("schema") == SCHEMA + "-embedded-public-records"
        and document.get("status") == "PASS"
        and document.get("family") == family
        and document.get("candidate_module") == "candidates." + family + "_candidate"
        and document.get("source_sha256") == source_sha256
        and document.get("protocol_sha256") == protocol_sha256
        and document.get("v17_source_sha256") == V17_SOURCE_SHA256
        and document.get("v17_protocol_sha256") == V17_PROTOCOL_SHA256
        and document.get("matrix_sha256") == MATRIX_SHA256
        and document.get("stimulus_sha256") == STIMULUS_SHA256
        and document.get("cases") == EXPECTED_CASES
        and document.get("successful_additional_cases") == EXPECTED_ADDITIONAL_CASES
        and document.get("successful_real_locale_cases") == EXPECTED_LOCALE_CASES
        and document.get("real_locale_transition_count") == EXPECTED_LOCALE_TRANSITIONS
        and document.get("expected_native_sha256") == dict(expected_native)
        and document.get("matched_inside_live_v10_owner_guard") is True
        and document.get("candidate_imported_by_frozen_owner_only") is True
        and document.get("performance_fixtures_read") == 0
        and document.get("holdout_cases_read") == 0
        and document.get("benchmark_or_timing_executed") is False
        and document.get("performance") == "NOT MEASURED",
        "the candidate's complete same-process guarded public record was forged",
    )
    locale_report = document.get("locale_preflight")
    require(
        isinstance(locale_report, dict)
        and locale_report.get("iso8859_1_codeset") in {"iso88591", "latin1"}
        and locale_report.get("utf8_codeset") == "utf8"
        and locale_report.get("ctype_restored") is True
        and locale_report.get("locale_path_unchanged") is True,
        "an actual same-process guarded fresh locale was unavailable",
    )
    records = document.get("records")
    actual = validate_public_records(records)
    require(actual == document.get("record_sha256"),
            "a complete real guarded public record was hidden")
    if baseline is not None:
        require(records == baseline,
                "the actual native candidate disagrees with both Python references")
    return document


def authenticate_reference_prerequisites(
    source_sha256: str,
    protocol_sha256: str,
) -> dict[str, Any]:
    verify_runtime()
    read_frozen(SOURCE_RELATIVE, source_sha256, MAX_SOURCE_BYTES)
    read_frozen(PROTOCOL_RELATIVE, protocol_sha256, MAX_SOURCE_BYTES)
    authenticate_frozen_v17()
    baseline = v17.authenticate_reference(V17_SOURCE_SHA256, V17_PROTOCOL_SHA256)
    require(
        baseline.get("v5_reference_sha256") == v17.V5_REFERENCE_SHA256
        and baseline.get("original_matrix_sha256") == v17.ORIGINAL_MATRIX_SHA256
        and baseline.get("original_public_methods") == 152
        and baseline.get("original_passed") == 151
        and baseline.get("original_named_private_skips") == 1
        and baseline.get("candidate_audits_read") == 0
        and baseline.get("candidate_proofs_read") == 0
        and baseline.get("candidate_imports") == 0,
        "the actual complete original V5 dual Python baseline did not pass",
    )
    build_matrix()
    return {
        "source_sha256": source_sha256,
        "protocol_sha256": protocol_sha256,
        "v17_source_sha256": V17_SOURCE_SHA256,
        "v17_protocol_sha256": V17_PROTOCOL_SHA256,
        "v5_reference_sha256": v17.V5_REFERENCE_SHA256,
        "original_public_methods": 152,
        "original_passed": 151,
        "original_named_private_debug_skips": 1,
        "candidate_audits_read": 0,
        "candidate_proofs_read": 0,
        "candidate_imports": 0,
        "performance": "NOT MEASURED",
    }


def _locale_names(options: argparse.Namespace) -> dict[str, str]:
    require(
        type(options.iso8859_1_locale) is str
        and bool(options.iso8859_1_locale)
        and type(options.utf8_locale) is str
        and bool(options.utf8_locale)
        and options.iso8859_1_locale != options.utf8_locale,
        "BLOCKED: provision genuinely distinct working fresh ISO-8859-1 "
        "and UTF-8 locales before a real public reference or candidate",
    )
    return {
        "iso8859_1": options.iso8859_1_locale,
        "utf8": options.utf8_locale,
    }


def _reference_worker_document(
    role: str,
    source_sha256: str,
    protocol_sha256: str,
    locale_names: Mapping[str, str],
) -> dict[str, Any]:
    verify_runtime()
    require(role in {"reference_a", "reference_b"},
            "a candidate cannot be imported in a true Python reference worker")
    read_frozen(SOURCE_RELATIVE, source_sha256, MAX_SOURCE_BYTES)
    read_frozen(PROTOCOL_RELATIVE, protocol_sha256, MAX_SOURCE_BYTES)
    authenticate_frozen_v17()
    require(
        not any(name == "candidates" or name.startswith("candidates.")
                for name in sys.modules),
        "a genuine Python reference process preloaded a candidate",
    )
    locale_preflight = v17._preflight_real_locales(locale_names)
    module = importlib.import_module("re")
    require(module.__name__ == "re", "the actual Python reference was replaced")
    records: list[dict[str, Any]] = []
    active: str | None = None
    try:
        for row in build_matrix():
            active = row["id"]
            record = v17.evaluate_case(module, row, locale_names=locale_names)
            if row["cohort"] in v17.ADDITIONAL_COHORTS:
                require(record["outcome"]["status"] == "return",
                        "a real Python public probe or resource did not pass")
            if row["cohort"] in {
                "real-locale-switch-on-compiled-bytes",
                "real-locale-invalid-flags-and-cache",
            }:
                v17._validate_locale_case(record)
            records.append(record)
            active = None
    except BaseException as error:
        raise PublicSurfaceV18WorkerFailure(
            role,
            "the genuine independent Python public reference failed",
            {
                "completed_records": records,
                "completed_count": len(records),
                "active_case": active,
                "actual_error": v17.normalize(error),
            },
        ) from error
    return {
        "schema": SCHEMA + "-reference-worker",
        "status": "PASS",
        "role": role,
        "python": "3.14.6",
        "source_sha256": source_sha256,
        "protocol_sha256": protocol_sha256,
        "v17_source_sha256": V17_SOURCE_SHA256,
        "v17_protocol_sha256": V17_PROTOCOL_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "stimulus_sha256": STIMULUS_SHA256,
        "cases": EXPECTED_CASES,
        "successful_additional_cases": EXPECTED_ADDITIONAL_CASES,
        "successful_real_locale_cases": EXPECTED_LOCALE_CASES,
        "real_locale_transition_count": EXPECTED_LOCALE_TRANSITIONS,
        "locale_preflight": locale_preflight,
        "records": records,
        "record_sha256": validate_public_records(records),
        "guard": {"baseline_only": True, "candidate_imported": False},
        "subinterpreter_coverage": "NOT RUN",
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
    }


def validate_reference_worker(
    document: Any,
    *,
    role: str,
    source_sha256: str,
    protocol_sha256: str,
) -> dict[str, Any]:
    require(
        isinstance(document, dict)
        and document.get("schema") == SCHEMA + "-reference-worker"
        and document.get("status") == "PASS"
        and document.get("role") == role
        and document.get("python") == "3.14.6"
        and document.get("source_sha256") == source_sha256
        and document.get("protocol_sha256") == protocol_sha256
        and document.get("v17_source_sha256") == V17_SOURCE_SHA256
        and document.get("v17_protocol_sha256") == V17_PROTOCOL_SHA256
        and document.get("matrix_sha256") == MATRIX_SHA256
        and document.get("stimulus_sha256") == STIMULUS_SHA256
        and document.get("cases") == EXPECTED_CASES
        and document.get("successful_additional_cases") == EXPECTED_ADDITIONAL_CASES
        and document.get("successful_real_locale_cases") == EXPECTED_LOCALE_CASES
        and document.get("real_locale_transition_count") == EXPECTED_LOCALE_TRANSITIONS
        and document.get("guard") == {
            "baseline_only": True, "candidate_imported": False,
        }
        and document.get("subinterpreter_coverage") == "NOT RUN"
        and document.get("holdout_cases_read") == 0
        and document.get("performance_fixtures_read") == 0
        and document.get("benchmark_or_timing_executed") is False
        and document.get("performance") == "NOT MEASURED",
        "an actual complete separately isolated Python reference was forged",
    )
    locales = document.get("locale_preflight")
    require(
        isinstance(locales, dict)
        and locales.get("iso8859_1_codeset") in {"iso88591", "latin1"}
        and locales.get("utf8_codeset") == "utf8"
        and locales.get("ctype_restored") is True
        and locales.get("locale_path_unchanged") is True,
        "a genuine Python reference lacks actual restored fresh locales",
    )
    require(
        validate_public_records(document.get("records"))
        == document.get("record_sha256"),
        "an actual Python reference concealed a public result",
    )
    return document


def _run_reference_worker(
    role: str,
    source_sha256: str,
    protocol_sha256: str,
    locales: Mapping[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    command = [
        str(v17.PINNED_PYTHON), "-I", "-B", str(ROOT / SOURCE_RELATIVE),
        "--reference-worker", role,
        "--source-sha256", source_sha256,
        "--protocol-sha256", protocol_sha256,
        "--iso8859-1-locale", locales["iso8859_1"],
        "--utf8-locale", locales["utf8"],
    ]
    try:
        process = subprocess.run(
            command,
            cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=3_600,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise PublicSurfaceV18WorkerFailure(
            role,
            "a true independent Python reference crashed or timed out",
            {"actual_error": v17.normalize(error)},
        ) from error
    details = {
        "returncode": process.returncode,
        "stdout": process.stdout.decode("utf-8", errors="backslashreplace"),
        "stderr": process.stderr.decode("utf-8", errors="backslashreplace"),
    }
    require(len(process.stdout) <= MAX_WORKER_BYTES
            and len(process.stderr) <= MAX_WORKER_BYTES,
            "a genuine Python reference exceeded its bounded actual streams")
    if process.returncode != 0 or process.stderr:
        raise PublicSurfaceV18WorkerFailure(
            role, "an actual independent Python reference failed", details,
        )
    result = _strict_canonical(process.stdout, role)
    validated = validate_reference_worker(
        result, role=role, source_sha256=source_sha256,
        protocol_sha256=protocol_sha256,
    )
    retained_process = {
        "role": role,
        "returncode": process.returncode,
        "stdout": capture_complete_stream(process.stdout),
        "stderr": capture_complete_stream(process.stderr),
    }
    validate_process_streams(
        retained_process, role=role, expected_document=validated,
    )
    return validated, retained_process


def _preflight_destinations(paths: tuple[str, ...]) -> None:
    require(len(paths) == len(set(paths)),
            "actual passing and failed reports must never share a destination")
    for relative in paths:
        path = ROOT / safe_relative(relative, outputs_only=True)
        require(
            path.parent.is_dir()
            and not path.parent.is_symlink()
            and path.resolve(strict=False) == path
            and not path.exists()
            and not path.is_symlink(),
            "refusing to overwrite or follow a real correctness report: " + relative,
        )


def exclusive_write(document: Mapping[str, Any], relative: str) -> str:
    path = ROOT / safe_relative(relative, outputs_only=True)
    payload = canonical(document) + b"\n"
    require(0 < len(payload) <= MAX_REPORT_BYTES,
            "the complete original correctness report exceeds its bound")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as error:
        raise PublicSurfaceV18Error(
            "refusing to overwrite or retry actual public evidence: " + relative,
        ) from error
    try:
        pending = memoryview(payload)
        while pending:
            count = os.write(descriptor, pending)
            require(count > 0, "an actual durable public report was truncated")
            pending = pending[count:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    directory_flags |= getattr(os, "O_CLOEXEC", 0)
    directory = os.open(path.parent, directory_flags)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return hashlib.sha256(payload).hexdigest()


def run_self_oracle(options: argparse.Namespace) -> dict[str, Any]:
    provenance = authenticate_reference_prerequisites(
        options.source_sha256, options.protocol_sha256,
    )
    locales = _locale_names(options)
    _preflight_destinations((SELF_ORACLE_RELATIVE, SELF_ORACLE_FAILURE_RELATIVE))
    complete: dict[str, dict[str, Any]] = {}
    processes: dict[str, dict[str, Any]] = {}
    try:
        for role in ("reference_a", "reference_b"):
            report, actual_process = _run_reference_worker(
                role, options.source_sha256, options.protocol_sha256, locales,
            )
            complete[role] = report
            processes[role] = actual_process
        first, second = complete["reference_a"], complete["reference_b"]
        require(first["records"] == second["records"],
                "the two genuine 1,376-case Python references disagree")
        result = {
            "schema": SCHEMA + "-self-oracle",
            "status": "PASS",
            "synthetic": False,
            "python": "3.14.6",
            "source_path": SOURCE_RELATIVE,
            "source_sha256": options.source_sha256,
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": options.protocol_sha256,
            "v17_source_path": V17_SOURCE_RELATIVE,
            "v17_source_sha256": V17_SOURCE_SHA256,
            "v17_protocol_path": V17_PROTOCOL_RELATIVE,
            "v17_protocol_sha256": V17_PROTOCOL_SHA256,
            "v5_reference_path": v17.V5_REFERENCE_RELATIVE,
            "v5_reference_sha256": v17.V5_REFERENCE_SHA256,
            "original_public_methods": 152,
            "original_applicable_passes": 151,
            "original_named_private_debug_skips": 1,
            "original_public_method_waivers": 0,
            "matrix_sha256": MATRIX_SHA256,
            "stimulus_sha256": STIMULUS_SHA256,
            "cohorts": EXPECTED_COHORTS,
            "cases": EXPECTED_CASES,
            "actual_independent_reference_count": 2,
            "successful_additional_cases_per_worker": EXPECTED_ADDITIONAL_CASES,
            "successful_real_locale_cases_per_worker": EXPECTED_LOCALE_CASES,
            "real_locale_transitions_per_worker": EXPECTED_LOCALE_TRANSITIONS,
            "reference_worker_reports": complete,
            "reference_worker_processes": processes,
            "record_sha256": first["record_sha256"],
            "candidate_audits_read": provenance["candidate_audits_read"],
            "candidate_proofs_read": provenance["candidate_proofs_read"],
            "candidate_imports": 0,
            "subinterpreter_coverage": "NOT RUN",
            "holdout_cases_read": 0,
            "performance_fixtures_read": 0,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }
        exclusive_write(result, SELF_ORACLE_RELATIVE)
        return result
    except (PublicSurfaceV18Error, v17.PublicSurfaceError, OSError,
            subprocess.SubprocessError) as error:
        failed: dict[str, Any] = {
            "schema": SCHEMA + "-self-oracle-failure",
            "status": "FAIL",
            "synthetic": False,
            "completed_reference_workers": complete,
            "completed_reference_worker_processes": processes,
            "actual_error": v17.normalize(error),
            "performance": "NOT MEASURED",
        }
        if isinstance(error, PublicSurfaceV18WorkerFailure):
            failed["failed_role"] = error.role
            failed["actual_failure_details"] = error.details
        exclusive_write(failed, SELF_ORACLE_FAILURE_RELATIVE)
        raise


def authenticate_surface_reference(
    provenance: Mapping[str, Any],
    *,
    source_sha256: str,
    protocol_sha256: str,
    reference_sha256: str | None,
) -> dict[str, Any]:
    require(
        provenance.get("v5_reference_sha256") == v17.V5_REFERENCE_SHA256
        and provenance.get("candidate_imports") == 0
        and provenance.get("candidate_audits_read") == 0
        and provenance.get("candidate_proofs_read") == 0,
        "the genuinely candidate-free V5 baseline must be validated first",
    )
    require(valid_sha256(reference_sha256),
            "BLOCKED: independently publish the complete actual V18 "
            "two-worker Python reference hash before any candidate audit")
    raw = read_frozen(SELF_ORACLE_RELATIVE, str(reference_sha256), MAX_REPORT_BYTES)
    result = _strict_canonical(raw, SELF_ORACLE_RELATIVE)
    require(
        result.get("schema") == SCHEMA + "-self-oracle"
        and result.get("status") == "PASS"
        and result.get("synthetic") is False
        and result.get("python") == "3.14.6"
        and result.get("source_path") == SOURCE_RELATIVE
        and result.get("source_sha256") == source_sha256
        and result.get("protocol_path") == PROTOCOL_RELATIVE
        and result.get("protocol_sha256") == protocol_sha256
        and result.get("v17_source_sha256") == V17_SOURCE_SHA256
        and result.get("v17_protocol_sha256") == V17_PROTOCOL_SHA256
        and result.get("v5_reference_sha256") == v17.V5_REFERENCE_SHA256
        and result.get("original_public_methods") == 152
        and result.get("original_applicable_passes") == 151
        and result.get("original_named_private_debug_skips") == 1
        and result.get("original_public_method_waivers") == 0
        and result.get("matrix_sha256") == MATRIX_SHA256
        and result.get("stimulus_sha256") == STIMULUS_SHA256
        and result.get("cases") == EXPECTED_CASES
        and result.get("cohorts") == EXPECTED_COHORTS
        and result.get("actual_independent_reference_count") == 2
        and result.get("successful_additional_cases_per_worker")
        == EXPECTED_ADDITIONAL_CASES
        and result.get("successful_real_locale_cases_per_worker")
        == EXPECTED_LOCALE_CASES
        and result.get("real_locale_transitions_per_worker")
        == EXPECTED_LOCALE_TRANSITIONS
        and result.get("candidate_audits_read") == 0
        and result.get("candidate_proofs_read") == 0
        and result.get("candidate_imports") == 0
        and result.get("subinterpreter_coverage") == "NOT RUN"
        and result.get("holdout_cases_read") == 0
        and result.get("performance_fixtures_read") == 0
        and result.get("benchmark_or_timing_executed") is False
        and result.get("performance") == "NOT MEASURED",
        "the exact actual independently published V18 Python reference failed",
    )
    workers = result.get("reference_worker_reports")
    processes = result.get("reference_worker_processes")
    require(isinstance(workers, dict)
            and set(workers) == {"reference_a", "reference_b"}
            and isinstance(processes, dict)
            and set(processes) == {"reference_a", "reference_b"},
            "both complete actual V18 Python reference records are mandatory")
    first = validate_reference_worker(
        workers["reference_a"], role="reference_a",
        source_sha256=source_sha256, protocol_sha256=protocol_sha256,
    )
    second = validate_reference_worker(
        workers["reference_b"], role="reference_b",
        source_sha256=source_sha256, protocol_sha256=protocol_sha256,
    )
    validate_process_streams(
        processes["reference_a"],
        role="reference_a",
        expected_document=first,
    )
    validate_process_streams(
        processes["reference_b"],
        role="reference_b",
        expected_document=second,
    )
    require(
        first["records"] == second["records"]
        and first["record_sha256"] == second["record_sha256"]
        and first["record_sha256"] == result.get("record_sha256"),
        "the two actual complete V18 reference streams disagree",
    )
    return {
        "source_sha256": source_sha256,
        "protocol_sha256": protocol_sha256,
        "reference_sha256": reference_sha256,
        "baseline_records": first["records"],
        "record_sha256": first["record_sha256"],
        "v5_reference_sha256": v17.V5_REFERENCE_SHA256,
    }


def import_frozen_validator(name: str, relative: str, fingerprint: str) -> Any:
    read_frozen(relative, fingerprint, MAX_SOURCE_BYTES)
    module = importlib.import_module(name)
    require(
        os.path.abspath(module.__file__) == str(ROOT / relative),
        "an exact authenticated independent owner validator was replaced: " + name,
    )
    read_frozen(relative, fingerprint, MAX_SOURCE_BYTES)
    return module


def _restore_original_producer(v11: Any, proof: Mapping[str, Any]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.CompletedProcess(
        args=["durably-recorded-genuine-original-v11-producer"],
        returncode=proof.get("original_worker_returncode"),
        stdout=v11.restore_complete_stream(
            proof.get("original_worker_stdout"),
            "the actual original qualified V11 worker stdout",
        ),
        stderr=v11.restore_complete_stream(
            proof.get("original_worker_stderr"),
            "the actual original qualified V11 worker stderr",
        ),
    )


def validate_durable_pair_identity(
    document: Any,
    family: str,
    *,
    deep: bool,
    archive_relative: str,
    archive_sha256: str,
    proof_relative: str,
    snapshot: Mapping[str, Any],
    v10_base_report_sha256: str,
    v10_strict_report_sha256: str,
    qualified_edge: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    require(family in FAMILIES and type(deep) is bool,
            "an exact real durable candidate family and proof kind are required")
    expected_archive = (
        V11_DEEP_ARCHIVE_RELATIVES[family]
        if deep else V11_EDGE_ARCHIVE_RELATIVES[family]
    )
    expected_proof = (
        V11_DEEP_PROOF_RELATIVES[family]
        if deep else V11_EDGE_PROOF_RELATIVES[family]
    )
    mode = "qualified-deep" if deep else "qualified-edge"
    require(
        isinstance(document, dict)
        and isinstance(snapshot, Mapping)
        and archive_relative == expected_archive
        and proof_relative == expected_proof
        and valid_sha256(archive_sha256)
        and valid_sha256(v10_base_report_sha256)
        and valid_sha256(v10_strict_report_sha256)
        and v10_base_report_sha256 != v10_strict_report_sha256
        and document.get("schema")
        == "rebar-postfinal-current-build-proofs-v11-" + mode + "-durable-proof"
        and document.get("status") == "PASS"
        and document.get("result") == "PASS"
        and document.get("mode") == mode
        and document.get("candidate_family") == CONTRACT_NAMES[family]
        and document.get("candidate_module")
        == "candidates." + family + "_candidate"
        and document.get("campaign_qualified") is True
        and document.get("proof_path") == expected_proof
        and document.get("original_archive_path") == expected_archive
        and document.get("original_archive_sha256") == archive_sha256
        and type(document.get("original_archive_bytes")) is int
        and 0 < document["original_archive_bytes"] <= MAX_ARCHIVE_BYTES
        and document.get("complete_original_producer_bytes_preserved") is True
        and document.get("original_archive_is_unmodified_original") is True
        and document.get("stdout_is_not_durable_proof") is True
        and document.get("original_worker_returncode") == 0
        and isinstance(document.get("original_worker_stdout"), dict)
        and isinstance(document.get("original_worker_stderr"), dict)
        and document.get("full_current_family_source_sha256")
        == snapshot.get("source_sha256_by_path")
        and document.get("full_current_family_native_elf_sha256")
        == snapshot.get("native_sha256_by_path")
        and isinstance(document.get("corrected_v10_native_owner_before"), dict)
        and isinstance(document.get("corrected_v10_native_owner_after"), dict)
        and document.get("refresh_protocol_path") == V11_PROTOCOL_RELATIVE
        and document.get("refresh_protocol_sha256") == V11_PROTOCOL_SHA256
        and document.get("v10_native_owner_source_path") == V10_OWNER_RELATIVE
        and document.get("v10_native_owner_source_sha256") == V10_OWNER_SHA256
        and document.get("v10_no_delegation_source_path") == V10_STRICT_RELATIVE
        and document.get("v10_no_delegation_source_sha256") == V10_STRICT_SHA256
        and document.get("v10_native_ownership_protocol_path")
        == V10_OWNERSHIP_PROTOCOL_RELATIVE
        and document.get("v10_native_ownership_protocol_sha256")
        == V10_OWNERSHIP_PROTOCOL_SHA256
        and document.get("actual_v10_base_report_sha256")
        == v10_base_report_sha256
        and document.get("actual_v10_strict_report_sha256")
        == v10_strict_report_sha256
        and document.get("exclusive_creation") is True
        and document.get("performance") == "NOT MEASURED"
        and document.get("holdout") == "NOT ACCESSED",
        "a complete qualified durable V11 original archive-and-owner pair "
        "was missing, diagnostic, swapped, or forged",
    )
    graph = document.get("all_family_audited_provenance")
    require(
        isinstance(graph, dict)
        and graph.get("all_family_audit_qualified") is True
        and isinstance(graph.get("all_family_source_sha256_by_path"), dict)
        and len(graph["all_family_source_sha256_by_path"]) == 12
        and isinstance(graph.get("all_family_native_elf_sha256_by_path"), dict)
        and len(graph["all_family_native_elf_sha256_by_path"]) == 5,
        "a complete durable owner proof omitted the genuine all-family graph",
    )
    if deep:
        require(
            isinstance(qualified_edge, Mapping)
            and document.get("checks") == 393
            and document.get("seeded_case_count") == 64
            and document.get("reference_sha256")
            == "b184f3388320909b3c28fbd3ce9c15cefc992d3e852e9495ad8fb503d1cbaad8"
            and document.get("public_mismatch_count") == 0
            and document.get("qualified_edge") == dict(qualified_edge),
            "a real durable deep proof lost its genuine qualified edge pair",
        )
    else:
        require(
            document.get("checks") == 223_198
            and document.get("category_count") == 49
            and document.get("reference_sha256")
            == "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526"
            and document.get("failure_count") == 0
            and document.get("complete_failure_row_count") == 0,
            "a complete genuine 223,198-case durable edge proof was weakened",
        )
    return document


def _validate_v11_family(
    family: str,
    pins: Mapping[str, str],
    *,
    owner: Any,
    v11: Any,
    v8: Any,
    audits: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    snapshot = v11.snapshot_family(family)
    require(
        snapshot.get("family") == family
        and snapshot.get("module") == "candidates." + family + "_candidate"
        and snapshot.get("native_sha256_by_path")
        == audits["validated_audits"]["graph"]["native_sha256_by_family"][family],
        "the actual independently owned V11 source or native family changed",
    )
    raw_edge = read_frozen(
        V11_EDGE_ARCHIVE_RELATIVES[family],
        pins[family + "_edge_archive"],
        MAX_ARCHIVE_BYTES,
    )
    raw_edge_proof = read_frozen(
        V11_EDGE_PROOF_RELATIVES[family],
        pins[family + "_edge_proof"],
        MAX_ARCHIVE_BYTES,
    )
    edge_path = ROOT / V11_EDGE_ARCHIVE_RELATIVES[family]
    require(edge_path == v11.edge_target(family, True, True),
            "a diagnostic or different-family edge archive cannot qualify")
    edge_proof_path = ROOT / V11_EDGE_PROOF_RELATIVES[family]
    require(edge_proof_path == v11.edge_proof_target(family, True, True),
            "the actual independently durable qualified edge proof is missing")
    edge_document, edge_result, passed = v8.validate_original_edge(
        raw_edge, edge_path, family, snapshot, contract,
    )
    require(
        isinstance(edge_document, dict)
        and isinstance(edge_result, dict)
        and passed is True
        and edge_result.get("failed") == 0
        and edge_result.get("checks") == v11.EDGE_CHECKS
        and edge_result.get("category_count") == v11.EDGE_CATEGORIES,
        "the complete 223,198-case actual original qualified V11 edge failed",
    )
    edge_wrapper = _strict_canonical(raw_edge_proof, V11_EDGE_PROOF_RELATIVES[family])
    validate_durable_pair_identity(
        edge_wrapper,
        family,
        deep=False,
        archive_relative=V11_EDGE_ARCHIVE_RELATIVES[family],
        archive_sha256=pins[family + "_edge_archive"],
        proof_relative=V11_EDGE_PROOF_RELATIVES[family],
        snapshot=snapshot,
        v10_base_report_sha256=pins["v10_base_report"],
        v10_strict_report_sha256=pins["v10_strict_report"],
    )
    state = {
        "owner": owner,
        "strict": audits["strict_module"],
        "v8": v8,
        "history": edge_wrapper.get("preserved_immutable_history"),
        "snapshot": snapshot,
        "audits": audits["validated_audits"],
    }
    edge_producer = _restore_original_producer(v11, edge_wrapper)
    v11.validate_durable_wrapper(
        edge_wrapper,
        family,
        state,
        qualified=True,
        deep=False,
        passed=True,
        original=edge_document,
        archive_path=edge_path,
        archive_sha256=pins[family + "_edge_archive"],
        archive_bytes=len(raw_edge),
        owner_before=edge_wrapper.get("corrected_v10_native_owner_before"),
        owner_after=edge_wrapper.get("corrected_v10_native_owner_after"),
        producer=edge_producer,
    )
    qualified_edge = {
        "status": "PASS",
        "campaign_qualified": True,
        "archive_path": V11_EDGE_ARCHIVE_RELATIVES[family],
        "archive_sha256": pins[family + "_edge_archive"],
        "proof_path": V11_EDGE_PROOF_RELATIVES[family],
        "proof_sha256": pins[family + "_edge_proof"],
    }

    raw_deep = read_frozen(
        V11_DEEP_ARCHIVE_RELATIVES[family],
        pins[family + "_deep_archive"],
        MAX_ARCHIVE_BYTES,
    )
    raw_deep_proof = read_frozen(
        V11_DEEP_PROOF_RELATIVES[family],
        pins[family + "_deep_proof"],
        MAX_ARCHIVE_BYTES,
    )
    deep_path = ROOT / V11_DEEP_ARCHIVE_RELATIVES[family]
    require(deep_path == v11.deep_target(family, True),
            "an actual independently qualified deep archive is required")
    deep_proof_path = ROOT / V11_DEEP_PROOF_RELATIVES[family]
    require(deep_proof_path == v11.deep_proof_target(family, True),
            "an actual complete durable deep owner proof is required")
    deep_document, deep_passed = v8.validate_deep(
        raw_deep, family, edge_result, snapshot, contract,
    )
    require(
        isinstance(deep_document, dict)
        and deep_passed is True
        and deep_document.get("public_mismatch_count") == 0,
        "the complete actual 393-observation original V11 deep suite failed",
    )
    deep_wrapper = _strict_canonical(raw_deep_proof, V11_DEEP_PROOF_RELATIVES[family])
    validate_durable_pair_identity(
        deep_wrapper,
        family,
        deep=True,
        archive_relative=V11_DEEP_ARCHIVE_RELATIVES[family],
        archive_sha256=pins[family + "_deep_archive"],
        proof_relative=V11_DEEP_PROOF_RELATIVES[family],
        snapshot=snapshot,
        v10_base_report_sha256=pins["v10_base_report"],
        v10_strict_report_sha256=pins["v10_strict_report"],
        qualified_edge=qualified_edge,
    )
    require(
        deep_wrapper.get("preserved_immutable_history") == state["history"],
        "the actual complete V11 durable edge and deep history differs",
    )
    deep_producer = _restore_original_producer(v11, deep_wrapper)
    v11.validate_durable_wrapper(
        deep_wrapper,
        family,
        state,
        qualified=True,
        deep=True,
        passed=True,
        original=deep_document,
        archive_path=deep_path,
        archive_sha256=pins[family + "_deep_archive"],
        archive_bytes=len(raw_deep),
        owner_before=deep_wrapper.get("corrected_v10_native_owner_before"),
        owner_after=deep_wrapper.get("corrected_v10_native_owner_after"),
        producer=deep_producer,
        qualified_edge=qualified_edge,
    )
    return {
        "family": family,
        "snapshot": snapshot,
        "edge": qualified_edge,
        "deep": {
            "status": "PASS",
            "campaign_qualified": True,
            "archive_path": V11_DEEP_ARCHIVE_RELATIVES[family],
            "archive_sha256": pins[family + "_deep_archive"],
            "proof_path": V11_DEEP_PROOF_RELATIVES[family],
            "proof_sha256": pins[family + "_deep_proof"],
        },
    }


def authenticate_durable_candidate_prerequisites(
    surface_reference: Mapping[str, Any],
    supplied: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        surface_reference.get("v5_reference_sha256") == v17.V5_REFERENCE_SHA256
        and valid_sha256(surface_reference.get("reference_sha256"))
        and valid_sha256(surface_reference.get("record_sha256"))
        and isinstance(surface_reference.get("baseline_records"), list)
        and len(surface_reference["baseline_records"]) == EXPECTED_CASES,
        "authenticate both complete original and V18 Python references "
        "before any audit, durable proof, or candidate import",
    )
    require(
        not any(name == "candidates" or name.startswith("candidates.")
                for name in sys.modules),
        "no candidate can be imported before genuine full durable qualification",
    )
    pins = proof_pin_values(supplied)
    read_frozen(
        V10_OWNERSHIP_PROTOCOL_RELATIVE,
        V10_OWNERSHIP_PROTOCOL_SHA256,
        MAX_SOURCE_BYTES,
    )
    read_frozen(V11_PROTOCOL_RELATIVE, V11_PROTOCOL_SHA256, MAX_SOURCE_BYTES)
    owner = import_frozen_validator(
        "tools.postfinal_from_scratch_audit_v10",
        V10_OWNER_RELATIVE,
        V10_OWNER_SHA256,
    )
    strict = import_frozen_validator(
        "tools.postfinal_no_delegation_audit_v10",
        V10_STRICT_RELATIVE,
        V10_STRICT_SHA256,
    )
    v11 = import_frozen_validator(
        "tools.postfinal_current_build_proofs_v11",
        V11_SOURCE_RELATIVE,
        V11_SOURCE_SHA256,
    )
    require(
        strict.independent is owner
        and v11.SCHEMA == "rebar-postfinal-current-build-proofs-v11"
        and v11.REFRESH_PROTOCOL_SHA256 == V11_PROTOCOL_SHA256
        and v11.V10_BASE_SOURCE_SHA256 == V10_OWNER_SHA256
        and v11.V10_STRICT_SOURCE_SHA256 == V10_STRICT_SHA256
        and v11.V10_OWNERSHIP_PROTOCOL_SHA256 == V10_OWNERSHIP_PROTOCOL_SHA256
        and v11.BASELINE_SHA256 == v17.V5_REFERENCE_SHA256
        and tuple(v11.FAMILIES) == FAMILIES,
        "an actual immutable V11 durable owner or V10 audit was substituted",
    )
    audit_pins = v11.validated_report_pins(
        True, pins["v10_base_report"], pins["v10_strict_report"],
    )
    require(
        isinstance(audit_pins, dict)
        and audit_pins.get("base_source") == V10_OWNER_SHA256
        and audit_pins.get("strict_source") == V10_STRICT_SHA256,
        "the two real all-family V10 audit source or report pins were forged",
    )
    full_audits = v11.audit_v11_reports(owner, strict, audit_pins)
    require(
        isinstance(full_audits, dict)
        and isinstance(full_audits.get("graph"), dict)
        and full_audits["graph"].get("source_count") == 12
        and full_audits["graph"].get("native_binary_count") == 5,
        "an actual three-family V10 full native-ownership audit did not pass",
    )
    v8 = v11.import_frozen(
        "tools.postfinal_current_build_proofs_v8",
        v11.V8_PROOF_RELATIVE,
        v11.V8_PROOF_SHA256,
    )
    contract = v8.load_contract()
    context = {
        "validated_audits": full_audits,
        "strict_module": strict,
    }
    complete = {
        family: _validate_v11_family(
            family,
            pins,
            owner=owner,
            v11=v11,
            v8=v8,
            audits=context,
            contract=contract,
        )
        for family in FAMILIES
    }
    require(
        set(complete) == set(FAMILIES)
        and not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
        "all twelve actual proofs must pass before any candidate is imported",
    )
    return {
        "owner": owner,
        "v11": v11,
        "audits": full_audits,
        "families": complete,
        "pins": pins,
    }


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
        "v17_source_sha256": V17_SOURCE_SHA256,
        "v17_protocol_sha256": V17_PROTOCOL_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "stimulus_sha256": STIMULUS_SHA256,
        "cases": EXPECTED_CASES,
        "iso8859_1_locale": locales["iso8859_1"],
        "utf8_locale": locales["utf8"],
        "expected_native_sha256": dict(expected_native),
    })


def run_guarded_candidate(
    family: str,
    *,
    source_sha256: str,
    protocol_sha256: str,
    locales: Mapping[str, str],
    durable: Mapping[str, Any],
    baseline: list[dict[str, Any]],
) -> dict[str, Any]:
    owner = durable["owner"]
    v11 = durable["v11"]
    state = durable["families"][family]
    snapshot = state["snapshot"]
    expected_native = snapshot["native_sha256_by_path"]
    require(v11.snapshot_family(family) == snapshot,
            "the actual audited native source changed before public matching")
    before = v11.validate_owner(
        owner,
        owner.run_native_worker(family, dict(expected_native)),
        family,
        expected_native,
    )
    original_hash = owner.NATIVE_OWNER_WORKER_SHA256
    original = owner.NATIVE_OWNER_WORKER
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
        "REBAR_PUBLIC_SURFACE_V18_CONTEXT": canonical(configuration).decode("ascii"),
    }
    if "LOCPATH" in os.environ:
        environment["LOCPATH"] = os.environ["LOCPATH"]
    arguments = [
        str(v17.PINNED_PYTHON), "-I", "-B", "-c", composed,
        str(ROOT), family, canonical(dict(expected_native)).decode("ascii"),
    ]
    try:
        process = subprocess.run(
            arguments,
            cwd=str(ROOT),
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=3_600,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise PublicSurfaceV18WorkerFailure(
            family,
            "the genuine same-process guarded public native worker crashed",
            {"actual_error": v17.normalize(error), "owner_before": before},
        ) from error
    details = {
        "returncode": process.returncode,
        "stdout": process.stdout.decode("utf-8", errors="backslashreplace"),
        "stderr": process.stderr.decode("utf-8", errors="backslashreplace"),
        "owner_before": before,
        "composed_worker_sha256": composed_hash,
    }
    if (process.returncode != 0
            or not 0 < len(process.stdout) <= MAX_WORKER_BYTES
            or process.stderr
            or len(process.stderr) > MAX_WORKER_BYTES):
        raise PublicSurfaceV18WorkerFailure(
            family,
            "the complete actually guarded public native owner failed",
            details,
        )
    report = owner.core.decode_report(
        process.stdout,
        label="actual complete V18 public observations inside the frozen V10 owner",
    )
    owner.validate_worker(report, family, dict(expected_native))
    observed = validate_embedded_records(
        report.get("rebar_v18_guarded_public_surface"),
        family=family,
        source_sha256=source_sha256,
        protocol_sha256=protocol_sha256,
        expected_native=expected_native,
        baseline=baseline,
    )
    retained_process = {
        "role": family,
        "returncode": process.returncode,
        "stdout": capture_complete_stream(process.stdout),
        "stderr": capture_complete_stream(process.stderr),
    }
    validate_process_streams(retained_process, role=family, expected_document=report)
    inside_owner = dict(report)
    inside_owner.pop("rebar_v18_guarded_public_surface", None)
    owner.validate_worker(inside_owner, family, dict(expected_native))
    require(v11.snapshot_family(family) == snapshot,
            "the owned current native binary changed during guarded matching")
    after = v11.validate_owner(
        owner,
        owner.run_native_worker(family, dict(expected_native)),
        family,
        expected_native,
    )
    require(v11.snapshot_family(family) == snapshot,
            "the actual audited candidate changed after its guarded worker")
    return {
        "schema": SCHEMA + "-candidate-worker",
        "status": "PASS",
        "family": family,
        "candidate_module": "candidates." + family + "_candidate",
        "source_sha256": source_sha256,
        "protocol_sha256": protocol_sha256,
        "native_sha256_by_path": dict(expected_native),
        "original_owner_worker_sha256": original_hash,
        "composed_owner_worker_sha256": composed_hash,
        "owner_before": before,
        "same_process_owner": report,
        "same_process_original_streams": retained_process,
        "public_observations": observed,
        "owner_after": after,
        "v11_edge_archive_sha256": state["edge"]["archive_sha256"],
        "v11_edge_proof_sha256": state["edge"]["proof_sha256"],
        "v11_deep_archive_sha256": state["deep"]["archive_sha256"],
        "v11_deep_proof_sha256": state["deep"]["proof_sha256"],
        "cases": EXPECTED_CASES,
        "record_sha256": observed["record_sha256"],
        "matched_inside_live_v10_owner_guard": True,
        "fresh_isolated_owner_checks": 2,
        "benchmark_or_timing_executed": False,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "performance": "NOT MEASURED",
    }


def run_all_candidates(options: argparse.Namespace) -> dict[str, Any]:
    base = authenticate_reference_prerequisites(
        options.source_sha256, options.protocol_sha256,
    )
    reference = authenticate_surface_reference(
        base,
        source_sha256=options.source_sha256,
        protocol_sha256=options.protocol_sha256,
        reference_sha256=options.reference_sha256,
    )
    values: dict[str, Any] = {
        "v10_base_report": options.v10_base_report_sha256,
        "v10_strict_report": options.v10_strict_report_sha256,
    }
    for family in FAMILIES:
        for kind in ("edge_archive", "edge_proof", "deep_archive", "deep_proof"):
            values[family + "_" + kind] = getattr(
                options, family + "_" + kind + "_sha256",
            )
    durable = authenticate_durable_candidate_prerequisites(reference, values)
    locales = _locale_names(options)
    _preflight_destinations((
        ALL_CANDIDATE_RELATIVE,
        *CANDIDATE_FAILURE_RELATIVES.values(),
    ))
    actual: dict[str, dict[str, Any]] = {}
    try:
        for family in FAMILIES:
            actual[family] = run_guarded_candidate(
                family,
                source_sha256=options.source_sha256,
                protocol_sha256=options.protocol_sha256,
                locales=locales,
                durable=durable,
                baseline=reference["baseline_records"],
            )
        require(set(actual) == set(FAMILIES),
                "an independently implemented actual family was omitted")
        result = {
            "schema": SCHEMA + "-all-candidates",
            "status": "PASS",
            "synthetic": False,
            "python": "3.14.6",
            "source_path": SOURCE_RELATIVE,
            "source_sha256": options.source_sha256,
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": options.protocol_sha256,
            "v17_source_sha256": V17_SOURCE_SHA256,
            "v17_protocol_sha256": V17_PROTOCOL_SHA256,
            "v11_source_sha256": V11_SOURCE_SHA256,
            "v11_protocol_sha256": V11_PROTOCOL_SHA256,
            "v10_owner_source_sha256": V10_OWNER_SHA256,
            "v10_strict_source_sha256": V10_STRICT_SHA256,
            "v10_ownership_protocol_sha256": V10_OWNERSHIP_PROTOCOL_SHA256,
            "v10_base_report_sha256": values["v10_base_report"],
            "v10_strict_report_sha256": values["v10_strict_report"],
            "v5_reference_sha256": v17.V5_REFERENCE_SHA256,
            "v18_reference_sha256": reference["reference_sha256"],
            "matrix_sha256": MATRIX_SHA256,
            "stimulus_sha256": STIMULUS_SHA256,
            "cohorts": EXPECTED_COHORTS,
            "cases_per_candidate": EXPECTED_CASES,
            "actual_candidate_checks": len(FAMILIES) * EXPECTED_CASES,
            "completed_families": list(FAMILIES),
            "genuine_durable_original_archive_count": 6,
            "genuine_durable_owner_proof_count": 6,
            "fresh_isolated_owner_checks_per_family": 2,
            "matching_inside_live_original_owner_guard": True,
            "candidate_records": actual,
            "failure_records": [],
            "holdout_cases_read": 0,
            "performance_fixtures_read": 0,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }
        exclusive_write(result, ALL_CANDIDATE_RELATIVE)
        return result
    except (
        PublicSurfaceV18Error, v17.PublicSurfaceError, AssertionError,
        OSError, subprocess.SubprocessError, ValueError, TypeError, KeyError,
    ) as error:
        family = error.role if isinstance(error, PublicSurfaceV18WorkerFailure) else (
            next((name for name in FAMILIES if name not in actual), FAMILIES[-1])
        )
        failure: dict[str, Any] = {
            "schema": SCHEMA + "-candidate-failure",
            "status": "FAIL",
            "synthetic": False,
            "failed_family": family,
            "completed_families": actual,
            "actual_error": v17.normalize(error),
            "performance": "NOT MEASURED",
        }
        if isinstance(error, PublicSurfaceV18WorkerFailure):
            failure["actual_failure_details"] = error.details
        exclusive_write(failure, CANDIDATE_FAILURE_RELATIVES[family])
        raise


def _synthetic_owner_source() -> str:
    return (
        "import sys\n"
        "import json\n"
        "import importlib\n"
        "matcher_descendant_names, matcher_descendant_originals, \\\n"
        "    matcher_descendant_aliases, matcher_alias_replacements = (\n"
        "        _install_real_cached_matcher_guards()\n"
        "    )\n"
        'matcher_descendant_guards_after = '
        '_verify_real_cached_matcher_guards("after")\n'
        "document = {\n"
        '    "stage07_guard_sentinel": stage07_guard_sentinel,\n'
        "}\n"
    )


def _synthetic_configuration(family: str = "rust") -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-embedded-configuration",
        "family": family,
        "source_sha256": "a" * 64,
        "protocol_sha256": "b" * 64,
        "v17_source_sha256": V17_SOURCE_SHA256,
        "v17_protocol_sha256": V17_PROTOCOL_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "stimulus_sha256": STIMULUS_SHA256,
        "cases": EXPECTED_CASES,
        "iso8859_1_locale": "source-only-iso8859-1",
        "utf8_locale": "source-only-utf8",
        "expected_native_sha256": {
            "candidates/source-only-synthetic-owner.so": "c" * 64,
        },
    }


def _synthetic_durable_pair(
    family: str,
    deep: bool,
    pins: Mapping[str, str],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    synthetic_native = {
        "candidates/synthetic-" + family + ".so": hashlib.sha256(
            ("source-only-native:" + family).encode("ascii"),
        ).hexdigest(),
    }
    synthetic_sources = {
        "candidates/synthetic-" + family + ".py": hashlib.sha256(
            ("source-only-owned-source:" + family).encode("ascii"),
        ).hexdigest(),
    }
    snapshot = {
        "family": family,
        "module": "candidates." + family + "_candidate",
        "source_sha256_by_path": synthetic_sources,
        "native_sha256_by_path": synthetic_native,
    }
    edge = {
        "status": "PASS",
        "campaign_qualified": True,
        "archive_path": V11_EDGE_ARCHIVE_RELATIVES[family],
        "archive_sha256": pins[family + "_edge_archive"],
        "proof_path": V11_EDGE_PROOF_RELATIVES[family],
        "proof_sha256": pins[family + "_edge_proof"],
    }
    mode = "qualified-deep" if deep else "qualified-edge"
    archive = (
        V11_DEEP_ARCHIVE_RELATIVES[family]
        if deep else V11_EDGE_ARCHIVE_RELATIVES[family]
    )
    proof = (
        V11_DEEP_PROOF_RELATIVES[family]
        if deep else V11_EDGE_PROOF_RELATIVES[family]
    )
    archive_hash = (
        pins[family + "_deep_archive"]
        if deep else pins[family + "_edge_archive"]
    )
    document: dict[str, Any] = {
        "schema": "rebar-postfinal-current-build-proofs-v11-"
        + mode + "-durable-proof",
        "status": "PASS",
        "result": "PASS",
        "mode": mode,
        "candidate_family": CONTRACT_NAMES[family],
        "candidate_module": "candidates." + family + "_candidate",
        "campaign_qualified": True,
        "proof_path": proof,
        "original_archive_path": archive,
        "original_archive_sha256": archive_hash,
        "original_archive_bytes": 512,
        "complete_original_producer_bytes_preserved": True,
        "original_archive_is_unmodified_original": True,
        "stdout_is_not_durable_proof": True,
        "original_worker_returncode": 0,
        "original_worker_stdout": {"source_only": True},
        "original_worker_stderr": {"source_only": True},
        "full_current_family_source_sha256": synthetic_sources,
        "full_current_family_native_elf_sha256": synthetic_native,
        "corrected_v10_native_owner_before": {"source_only": True},
        "corrected_v10_native_owner_after": {"source_only": True},
        "refresh_protocol_path": V11_PROTOCOL_RELATIVE,
        "refresh_protocol_sha256": V11_PROTOCOL_SHA256,
        "v10_native_owner_source_path": V10_OWNER_RELATIVE,
        "v10_native_owner_source_sha256": V10_OWNER_SHA256,
        "v10_no_delegation_source_path": V10_STRICT_RELATIVE,
        "v10_no_delegation_source_sha256": V10_STRICT_SHA256,
        "v10_native_ownership_protocol_path": V10_OWNERSHIP_PROTOCOL_RELATIVE,
        "v10_native_ownership_protocol_sha256": V10_OWNERSHIP_PROTOCOL_SHA256,
        "actual_v10_base_report_sha256": pins["v10_base_report"],
        "actual_v10_strict_report_sha256": pins["v10_strict_report"],
        "all_family_audited_provenance": {
            "all_family_audit_qualified": True,
            "all_family_source_sha256_by_path": {
                "source-only-" + str(index): hashlib.sha256(
                    ("source-only-graph-source:" + str(index)).encode("ascii"),
                ).hexdigest()
                for index in range(12)
            },
            "all_family_native_elf_sha256_by_path": {
                "native-only-" + str(index): hashlib.sha256(
                    ("source-only-graph-native:" + str(index)).encode("ascii"),
                ).hexdigest()
                for index in range(5)
            },
        },
        "exclusive_creation": True,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    if deep:
        document.update({
            "checks": 393,
            "seeded_case_count": 64,
            "reference_sha256":
                "b184f3388320909b3c28fbd3ce9c15cefc992d3e852e9495ad8fb503d1cbaad8",
            "public_mismatch_count": 0,
            "qualified_edge": edge,
        })
    else:
        document.update({
            "checks": 223_198,
            "category_count": 49,
            "reference_sha256":
                "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526",
            "failure_count": 0,
            "complete_failure_row_count": 0,
        })
    return snapshot, document, edge


def self_test() -> dict[str, Any]:
    verify_runtime()
    require(
        not any(name == "candidates" or name.startswith("candidates.")
                for name in sys.modules),
        "the public source-only control preloaded a candidate",
    )
    # Explicitly declare and authenticate the two immutable instruction files
    # before entering the zero-evidence, zero-candidate effect boundary.
    authenticate_frozen_v17()
    inherited = v17.self_test()
    require(
        inherited.get("status") == "PASS"
        and inherited.get("check_count", 0) >= 336
        and inherited.get("cases") == EXPECTED_CASES
        and inherited.get("cohorts") == EXPECTED_COHORTS
        and inherited.get("matrix_sha256") == MATRIX_SHA256
        and inherited.get("stimulus_sha256") == STIMULUS_SHA256
        and inherited.get("candidate_imports") == 0
        and inherited.get("subprocesses") == 0
        and inherited.get("source_files_read") == 0
        and inherited.get("evidence_files_read") == 0
        and inherited.get("files_written") == 0
        and inherited.get("clock_samples") == 0
        and inherited.get("locale_changes") == 0
        and inherited.get("regex_matching_calls") == 0
        and inherited.get("holdout_cases_read") == 0,
        "the genuine independently frozen V17 source-only controls failed",
    )
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: Any) -> None:
        require(not any(row["name"] == name for row in checks),
                "a V18 source-only poison control was counted twice")
        checks.append({"name": name, "passed": bool(condition)})

    def reject(name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except (PublicSurfaceV18Error, v17.PublicSurfaceError,
                AssertionError, ValueError, TypeError, KeyError, SyntaxError):
            check(name, True)
        else:
            check(name, False)

    with v17._source_only_effects() as effects:
        matrix = build_matrix()
        check("retain-all-336-actual-inherited-no-effect-controls",
              inherited["check_count"] >= 336)
        check("retain-all-43-genuine-independent-public-cohorts",
              len(v17.COHORTS) == EXPECTED_COHORTS)
        check("retain-all-1376-genuine-distinct-behavioral-stimuli",
              len(matrix) == EXPECTED_CASES)
        check("freeze-all-31-real-ordered-python-public-exports",
              len(v17.PUBLIC_EXPORTS) == 31)
        check("freeze-all-13-real-public-pattern-members",
              len(v17.PUBLIC_PATTERN_MEMBERS) == 13)
        check("freeze-all-14-real-public-match-members",
              len(v17.PUBLIC_MATCH_MEMBERS) == 14)
        check("preserve-original-152-public-upstream-methods",
              v17.PRIVATE_CONDITIONAL_METHOD == "ReTests.test_memory_leaks")
        check("require-real-source-local-151-passes-and-one-private-skip",
              v17.ORIGINAL_MATRIX_SHA256
              == "5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a")
        check("freeze-distinct-historical-v17-source-and-protocol",
              V17_SOURCE_SHA256 != V17_PROTOCOL_SHA256)
        check("freeze-distinct-real-durable-v11-source-and-protocol",
              V11_SOURCE_SHA256 != V11_PROTOCOL_SHA256)
        check("freeze-both-real-independent-v10-owner-source-identities",
              V10_OWNER_SHA256 != V10_STRICT_SHA256)
        check("preserve-two-separately-authentic-actual-python-workers",
              SELF_ORACLE_RELATIVE != SELF_ORACLE_FAILURE_RELATIVE)
        for cohort in v17.COHORTS:
            rows = [row for row in matrix if row["cohort"] == cohort]
            check("retain-32-real-source-stimuli-" + cohort,
                  len(rows) == 32
                  and len({digest(v17.build_stimulus(row)) for row in rows}) == 32)
            check("retain-32-independent-actual-expressions-" + cohort,
                  len({v17.build_stimulus(row)["expression"] for row in rows}) == 32)
            check("retain-32-independent-actual-subjects-" + cohort,
                  len({v17.build_stimulus(row)["subject"] for row in rows}) == 32)
        for symbol in v17.PUBLIC_EXPORTS:
            check("retain-exact-public-export-" + symbol,
                  v17.PUBLIC_EXPORTS.count(symbol) == 1)
        for member in v17.PUBLIC_PATTERN_MEMBERS:
            check("retain-exact-public-pattern-member-" + member,
                  v17.PUBLIC_PATTERN_MEMBERS.count(member) == 1)
        for member in v17.PUBLIC_MATCH_MEMBERS:
            check("retain-exact-public-match-member-" + member,
                  v17.PUBLIC_MATCH_MEMBERS.count(member) == 1)
        for family in FAMILIES:
            check("require-distinct-real-qualified-v11-edge-pair-" + family,
                  V11_EDGE_ARCHIVE_RELATIVES[family]
                  != V11_EDGE_PROOF_RELATIVES[family]
                  and V11_EDGE_ARCHIVE_RELATIVES[family].endswith(
                      "-v11-qualified-pass.json.gz",
                  )
                  and V11_EDGE_PROOF_RELATIVES[family].endswith(
                      "-v11-qualified-pass-proof.json",
                  ))
            check("require-distinct-real-qualified-v11-deep-pair-" + family,
                  V11_DEEP_ARCHIVE_RELATIVES[family]
                  != V11_DEEP_PROOF_RELATIVES[family]
                  and V11_DEEP_ARCHIVE_RELATIVES[family].endswith(
                      "-POSTFINAL-CURRENT-BUILD-V11-PASS.json.gz",
                  )
                  and V11_DEEP_PROOF_RELATIVES[family].endswith(
                      "-POSTFINAL-CURRENT-BUILD-V11-PASS-PROOF.json",
                  ))
        proof_paths = [
            *V11_EDGE_ARCHIVE_RELATIVES.values(),
            *V11_EDGE_PROOF_RELATIVES.values(),
            *V11_DEEP_ARCHIVE_RELATIVES.values(),
            *V11_DEEP_PROOF_RELATIVES.values(),
        ]
        check("retain-twelve-distinct-real-original-and-owner-proof-paths",
              len(proof_paths) == len(set(proof_paths)) == 12)

        synthetic_owner = _synthetic_owner_source()
        synthetic_hash = hashlib.sha256(synthetic_owner.encode("utf-8")).hexdigest()
        composed, composed_hash = compose_guarded_owner(
            synthetic_owner, owner_source_sha256=synthetic_hash,
        )
        check("parse-exact-source-only-composed-v10-owner",
              isinstance(ast.parse(composed), ast.Module))
        check("preserve-original-owner-hash-without-rewriting-source",
              hashlib.sha256(synthetic_owner.encode("utf-8")).hexdigest()
              == synthetic_hash)
        check("derive-actual-distinct-composed-worker-fingerprint",
              valid_sha256(composed_hash) and composed_hash != synthetic_hash)
        check("preload-frozen-evaluator-exactly-once-before-poison",
              composed.count(PRELOAD_INJECTION) == 1
              and composed.index(PRELOAD_INJECTION) < composed.index(PRELOAD_MARKER))
        check("run-public-calls-exactly-once-inside-live-matcher-guard",
              composed.count(OBSERVATION_INJECTION) == 1
              and composed.index(OBSERVATION_INJECTION)
              < composed.index(AFTER_GUARD_MARKER))
        check("retain-full-original-owner-schema-and-evidence",
              composed.count(OWNER_RECORD_INJECTION) == 1
              and composed.count(OWNER_RECORD_MARKER) == 1)
        check("never-import-candidate-from-injected-public-observation",
              "import candidates" not in PRELOAD_INJECTION
              and "import candidates" not in OBSERVATION_INJECTION
              and 'sys.modules.get(_rebar18_candidate_name)' in OBSERVATION_INJECTION)
        for name, marker in (
            ("preload-before-original-guard", PRELOAD_MARKER),
            ("match-before-original-after-guard", AFTER_GUARD_MARKER),
            ("retain-original-owner-json-schema", OWNER_RECORD_MARKER),
        ):
            missing = synthetic_owner.replace(marker, "", 1)
            missing_hash = hashlib.sha256(missing.encode("utf-8")).hexdigest()
            reject("reject-missing-exact-owner-marker-" + name,
                   lambda missing=missing, missing_hash=missing_hash:
                   compose_guarded_owner(
                       missing, owner_source_sha256=missing_hash,
                   ))
            duplicated = synthetic_owner.replace(marker, marker + marker, 1)
            duplicated_hash = hashlib.sha256(duplicated.encode("utf-8")).hexdigest()
            reject("reject-duplicated-owner-marker-" + name,
                   lambda duplicated=duplicated, duplicated_hash=duplicated_hash:
                   compose_guarded_owner(
                       duplicated, owner_source_sha256=duplicated_hash,
                   ))
        reject("reject-forged-original-owner-worker-source-hash",
               lambda: compose_guarded_owner(
                   synthetic_owner, owner_source_sha256="0" * 64,
               ))

        good_pins = {
            "v10_base_report": hashlib.sha256(b"source-only-base").hexdigest(),
            "v10_strict_report": hashlib.sha256(b"source-only-strict").hexdigest(),
            **{
                family + "_" + kind: hashlib.sha256(
                    ("source-only-v18:" + family + ":" + kind).encode("ascii"),
                ).hexdigest()
                for family in FAMILIES
                for kind in (
                    "edge_archive", "edge_proof", "deep_archive", "deep_proof",
                )
            },
        }
        check("validate-fourteen-distinct-source-only-durable-pin-shapes",
              len(proof_pin_values(good_pins)) == 14)
        for name in tuple(good_pins):
            missing = dict(good_pins)
            missing.pop(name)
            reject("reject-missing-actual-durable-proof-pin-" + name,
                   lambda missing=missing: proof_pin_values(missing))
            forged = dict(good_pins)
            forged[name] = "not-an-actual-hash"
            reject("reject-forged-actual-durable-proof-pin-" + name,
                   lambda forged=forged: proof_pin_values(forged))
        for family in FAMILIES:
            for left, right in (
                ("edge_archive", "edge_proof"),
                ("deep_archive", "deep_proof"),
                ("edge_proof", "deep_proof"),
            ):
                forged = dict(good_pins)
                forged[family + "_" + right] = forged[family + "_" + left]
                reject("reject-reused-durable-proof-" + family
                       + "-" + left + "-" + right,
                       lambda forged=forged: proof_pin_values(forged))

        for family in FAMILIES:
            for deep in (False, True):
                snapshot, actual, edge = _synthetic_durable_pair(
                    family, deep, good_pins,
                )
                kind = "deep" if deep else "edge"
                archive_relative = (
                    V11_DEEP_ARCHIVE_RELATIVES[family]
                    if deep else V11_EDGE_ARCHIVE_RELATIVES[family]
                )
                proof_relative = (
                    V11_DEEP_PROOF_RELATIVES[family]
                    if deep else V11_EDGE_PROOF_RELATIVES[family]
                )

                def validate_pair(
                    document: Any,
                    *,
                    snapshot: Mapping[str, Any] = snapshot,
                    family: str = family,
                    deep: bool = deep,
                    archive_relative: str = archive_relative,
                    proof_relative: str = proof_relative,
                    edge: Mapping[str, Any] = edge,
                ) -> Any:
                    return validate_durable_pair_identity(
                        document,
                        family,
                        deep=deep,
                        archive_relative=archive_relative,
                        archive_sha256=good_pins[
                            family + ("_deep_archive" if deep else "_edge_archive")
                        ],
                        proof_relative=proof_relative,
                        snapshot=snapshot,
                        v10_base_report_sha256=good_pins["v10_base_report"],
                        v10_strict_report_sha256=good_pins["v10_strict_report"],
                        qualified_edge=edge if deep else None,
                    )

                check("validate-source-only-complete-durable-" + family + "-" + kind,
                      validate_pair(actual) is actual)
                for field, wrong in (
                    ("status", "FAIL"),
                    ("campaign_qualified", False),
                    ("candidate_module", "candidates.other_candidate"),
                    ("proof_path", "candidates/evidence/forged-proof.json"),
                    ("original_archive_path", "candidates/evidence/forged.json.gz"),
                    ("original_archive_sha256", "0" * 64),
                    ("original_archive_bytes", 0),
                    ("complete_original_producer_bytes_preserved", False),
                    ("original_archive_is_unmodified_original", False),
                    ("stdout_is_not_durable_proof", False),
                    ("original_worker_returncode", 1),
                    ("corrected_v10_native_owner_before", None),
                    ("corrected_v10_native_owner_after", None),
                    ("actual_v10_base_report_sha256", "0" * 64),
                    ("actual_v10_strict_report_sha256", "0" * 64),
                    ("exclusive_creation", False),
                    ("performance", "MEASURED"),
                    ("holdout", "ACCESSED"),
                ):
                    forged = copy.deepcopy(actual)
                    forged[field] = wrong
                    reject("reject-forged-durable-" + family + "-" + kind
                           + "-" + field,
                           lambda forged=forged, validate_pair=validate_pair:
                           validate_pair(forged))
                for name, graph_field in (
                    ("missing-twelve-source-native-graph",
                     "all_family_source_sha256_by_path"),
                    ("missing-five-current-native-elf-graph",
                     "all_family_native_elf_sha256_by_path"),
                ):
                    forged = copy.deepcopy(actual)
                    forged["all_family_audited_provenance"][graph_field].popitem()
                    reject("reject-" + name + "-" + family + "-" + kind,
                           lambda forged=forged, validate_pair=validate_pair:
                           validate_pair(forged))
                if deep:
                    forged = copy.deepcopy(actual)
                    forged["qualified_edge"]["proof_sha256"] = "0" * 64
                    reject("reject-missing-durable-qualified-edge-inside-deep-" + family,
                           lambda forged=forged, validate_pair=validate_pair:
                           validate_pair(forged))

        good_configuration = _synthetic_configuration()
        check("validate-source-only-live-owner-context-shape",
              verify_embedded_configuration(good_configuration)
              == good_configuration)
        for field in tuple(good_configuration):
            removed = dict(good_configuration)
            removed.pop(field)
            reject("reject-missing-live-owner-configuration-" + field,
                   lambda removed=removed: verify_embedded_configuration(removed))
        for field, wrong in (
            ("schema", "unqualified"),
            ("family", "other"),
            ("source_sha256", "not-a-digest"),
            ("protocol_sha256", "not-a-digest"),
            ("v17_source_sha256", "0" * 64),
            ("v17_protocol_sha256", "0" * 64),
            ("matrix_sha256", "0" * 64),
            ("stimulus_sha256", "0" * 64),
            ("cases", EXPECTED_CASES - 1),
            ("iso8859_1_locale", ""),
            ("utf8_locale", ""),
            ("expected_native_sha256", {}),
        ):
            changed = dict(good_configuration)
            changed[field] = wrong
            reject("reject-forged-live-owner-configuration-" + field,
                   lambda changed=changed: verify_embedded_configuration(changed))
        reused_locale = dict(good_configuration)
        reused_locale["utf8_locale"] = reused_locale["iso8859_1_locale"]
        reject("reject-the-same-actual-locale-for-two-real-encodings",
               lambda: verify_embedded_configuration(reused_locale))

        for role in ("reference_a", "reference_b", *FAMILIES):
            synthetic_document = {
                "schema": "source-only-v18-complete-worker-observation",
                "role": role,
                "status": "PASS",
            }
            actual_stdout = canonical(synthetic_document) + b"\n"
            actual_process = {
                "role": role,
                "returncode": 0,
                "stdout": capture_complete_stream(actual_stdout),
                "stderr": capture_complete_stream(b""),
            }
            check("retain-exact-source-only-original-worker-stream-" + role,
                  validate_process_streams(
                      actual_process, role=role,
                      expected_document=synthetic_document,
                  ) is actual_process)
            for field, wrong in (
                ("role", "substituted-worker"),
                ("returncode", 1),
            ):
                forged_process = copy.deepcopy(actual_process)
                forged_process[field] = wrong
                reject("reject-changed-original-worker-" + role + "-" + field,
                       lambda forged_process=forged_process,
                       role=role, synthetic_document=synthetic_document:
                       validate_process_streams(
                           forged_process,
                           role=role,
                           expected_document=synthetic_document,
                       ))
            for field, wrong in (
                ("bytes", 0),
                ("sha256", "0" * 64),
                ("complete", False),
                ("base64", "not genuine base64!"),
            ):
                forged_process = copy.deepcopy(actual_process)
                forged_process["stdout"][field] = wrong
                reject("reject-incomplete-original-worker-stdout-"
                       + role + "-" + field,
                       lambda forged_process=forged_process,
                       role=role, synthetic_document=synthetic_document:
                       validate_process_streams(
                           forged_process,
                           role=role,
                           expected_document=synthetic_document,
                       ))
            forged_stderr = copy.deepcopy(actual_process)
            forged_stderr["stderr"] = capture_complete_stream(
                b"genuine concealed worker failure",
            )
            reject("reject-concealed-real-worker-stderr-" + role,
                   lambda forged_stderr=forged_stderr,
                   role=role, synthetic_document=synthetic_document:
                   validate_process_streams(
                       forged_stderr,
                       role=role,
                       expected_document=synthetic_document,
                   ))

        for label, value in (
            ("absolute", "/tmp/forged.json"),
            ("parent", "../forged.json"),
            ("nested-parent", "candidates/../forged.json"),
            ("backslash", "candidates\\forged.json"),
            ("nul", "candidates/forged\x00.json"),
            ("unapproved", "candidates/evidence/not-approved-v18.json"),
        ):
            reject("reject-dangerous-exclusive-correctness-output-" + label,
                   lambda value=value: safe_relative(value, outputs_only=True))
        for value in sorted(APPROVED_OUTPUTS):
            check("allow-exact-private-v18-output-" + value.rsplit("/", 1)[-1],
                  safe_relative(value, outputs_only=True) == value)
        for name, counter in (
            ("read-zero-candidate-evidence-reports-fixtures-or-holdouts", "files_read"),
            ("write-zero-reports-bytecode-or-evidence", "files_written"),
            ("start-zero-reference-candidate-or-proof-workers", "processes"),
            ("start-zero-correctness-or-background-threads", "threads"),
            ("sample-zero-correctness-performance-or-wall-clocks", "clock_samples"),
            ("draw-zero-production-randomness", "entropy_draws"),
            ("change-zero-global-locales", "locale_changes"),
            ("import-zero-candidates-or-native-implementations", "candidate_imports"),
            ("perform-zero-standard-library-regex-matches", "regex_matches"),
        ):
            check(name, effects[counter] == 0)

    failures = [row["name"] for row in checks if row["passed"] is not True]
    require(not failures,
            "a genuine V18 candidate-free poison failed: " + ", ".join(failures))
    require(len(checks) >= 250,
            "at least 250 distinct actual V18 source-only controls are required")
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "protocol_path": PROTOCOL_RELATIVE,
        "v17_source_sha256": V17_SOURCE_SHA256,
        "v17_protocol_sha256": V17_PROTOCOL_SHA256,
        "v11_source_sha256": V11_SOURCE_SHA256,
        "v11_protocol_sha256": V11_PROTOCOL_SHA256,
        "v10_owner_sha256": V10_OWNER_SHA256,
        "v10_strict_sha256": V10_STRICT_SHA256,
        "v10_ownership_protocol_sha256": V10_OWNERSHIP_PROTOCOL_SHA256,
        "check_count": len(checks),
        "inherited_v17_check_count": inherited["check_count"],
        "total_independent_source_controls": len(checks) + inherited["check_count"],
        "failed": [],
        "cohorts": EXPECTED_COHORTS,
        "cases": EXPECTED_CASES,
        "source_local_base_cases": inherited["source_local_base_cases"],
        "additional_cases": EXPECTED_ADDITIONAL_CASES,
        "distinct_behavioral_stimuli": EXPECTED_CASES,
        "matrix_sha256": MATRIX_SHA256,
        "stimulus_sha256": STIMULUS_SHA256,
        "public_exports": len(v17.PUBLIC_EXPORTS),
        "public_pattern_members": len(v17.PUBLIC_PATTERN_MEMBERS),
        "public_match_members": len(v17.PUBLIC_MATCH_MEMBERS),
        "required_v11_qualified_original_archives": 6,
        "required_v11_complete_durable_owner_proofs": 6,
        "declared_immutable_instruction_files_read": 2,
        "candidate_source_files_read": effects["files_read"],
        "evidence_files_read": effects["files_read"],
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
    modes.add_argument("--reference-worker", choices=("reference_a", "reference_b"),
                       help=argparse.SUPPRESS)
    parser.add_argument("--source-sha256")
    parser.add_argument("--protocol-sha256")
    parser.add_argument("--reference-sha256")
    parser.add_argument("--iso8859-1-locale", dest="iso8859_1_locale")
    parser.add_argument("--utf8-locale")
    parser.add_argument("--v10-base-report-sha256")
    parser.add_argument("--v10-strict-report-sha256")
    for family in FAMILIES:
        for kind in ("edge-archive", "edge-proof", "deep-archive", "deep-proof"):
            parser.add_argument("--" + family + "-" + kind + "-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    try:
        if options.self_test:
            document = self_test()
        elif options.reference_worker:
            document = _reference_worker_document(
                options.reference_worker,
                options.source_sha256,
                options.protocol_sha256,
                _locale_names(options),
            )
        elif options.self_oracle:
            document = run_self_oracle(options)
        else:
            document = run_all_candidates(options)
        sys.stdout.write(canonical(document).decode("ascii") + "\n")
    except (
        PublicSurfaceV18Error,
        v17.PublicSurfaceError,
        AssertionError,
        OSError,
        subprocess.SubprocessError,
        ValueError,
        UnicodeError,
        json.JSONDecodeError,
    ) as error:
        sys.stderr.write(canonical({
            "schema": SCHEMA,
            "status": "FAIL",
            "error": str(error),
            "performance": "NOT MEASURED",
        }).decode("ascii") + "\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
