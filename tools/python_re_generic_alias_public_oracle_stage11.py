#!/usr/bin/env python3
"""Independently verify the full public Python regex generic-alias contract."""

from __future__ import annotations

import sys

if __name__ == "__main__":
    import os as _stage11_os
    from pathlib import Path as _Stage11Path

    _stage11_root = str(_Stage11Path(__file__).resolve().parent.parent)
    _stage11_entry = (
        "import sys;sys.path.insert(0,sys.argv[1]);"
        "from tools.python_re_generic_alias_public_oracle_stage11 import main;"
        "raise SystemExit(main(sys.argv[2:]))"
    )
    _stage11_os.execv(
        sys.executable,
        [sys.executable, "-I", "-B", "-c", _stage11_entry, _stage11_root,
         *sys.argv[1:]],
    )

import copy
import importlib
import json
import os
import pickle
import types
import typing
import warnings
from pathlib import Path, PurePosixPath
from typing import Any, Callable

from tools import python_re_universal_public_oracle_stage10 as stage10


stage07 = stage10.stage07
stage06 = stage10.stage06
frozen = stage10.frozen
official_locale = stage10.official_locale
canonical = stage07.canonical
digest = stage07.digest
ROOT = Path(__file__).resolve().parent.parent

SOURCE_RELATIVE = "tools/python_re_generic_alias_public_oracle_stage11.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V11.md"
SCHEMA = "rebar-python-re-public-generic-alias-v11"
SELF_TEST_SCHEMA = SCHEMA + "-self-test"
WORKER_SCHEMA = SCHEMA + "-worker"
SELF_ORACLE_SCHEMA = SCHEMA + "-self-oracle"
ALL_CANDIDATE_SCHEMA = SCHEMA + "-all-candidates"
SEED = 2026072461
SEED_DOMAIN = "rebar/python-re/public-generic-alias/v11"
REQUIRED_CANDIDATES = ("rust", "vm", "zig")
ORIGINS = ("Pattern", "Match")
NORMAL_ARGUMENTS = ("str", "bytes")
NORMAL_ACTIONS = (
    "generic-alias-type", "exact-origin", "exact-arguments",
    "exact-parameters", "typing-origin", "typing-arguments",
    "public-representation", "repeated-equality", "different-equality",
    "equal-hash-relation",
)
DIVERSE_ARGUMENTS = (
    "int", "none", "ellipsis", "empty-tuple", "str-and-bytes",
    "type-variable", "nested-list-str", "object",
)
DIVERSE_ACTIONS = ("construction", "arguments", "parameters-and-typing")
REJECTION_ACTIONS = (
    "isinstance-real-instance", "isinstance-other-instance",
    "issubclass-real-origin", "issubclass-other-origin",
)
LIFECYCLE_ACTIONS = (
    "copy", "deepcopy", "pickle-protocol-0", "pickle-protocol-2",
    "pickle-protocol-4", "pickle-highest-protocol",
)
COHORTS = (
    ("ordinary-alias", 40),
    ("diverse-argument", 48),
    ("parameterized-type-rejection", 16),
    ("alias-lifecycle", 24),
)
EXPECTED_CASES = 128


class _Stage11TypeVariableSource[RebarPublicGenericAliasT]:
    """Obtain a real typing.TypeVar without importing Python's inspector."""


TYPE_PARAMETER = _Stage11TypeVariableSource.__type_params__[0]

STAGE10_SOURCE_RELATIVE = "tools/python_re_universal_public_oracle_stage10.py"
STAGE10_SOURCE_SHA256 = (
    "a24cfa72f44931c76b425ea3eb6568ff67dc87236c8d5fe930837a14c2f58f08"
)
STAGE10_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V10.md"
STAGE10_PROTOCOL_SHA256 = (
    "c0194ee2ef1e32bd64dc646e2f395bee6036b9c053e31d95ebb3cfbc52b0a543"
)
STAGE10_SELF_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-contract-v10-self-oracle.json"
)
STAGE10_SELF_SHA256 = (
    "5207ca3829216b9482f0b5a2928b339261e2c51d673cce7d80da0f4f4622a8f9"
)
STAGE10_ALL_RELATIVE = (
    "candidates/evidence/python-re-universal-public-oracle-v10-all.json"
)
STAGE10_ALL_SHA256 = (
    "0af512f940ce7c28e50c1977794e3fbb8a2c33206e77dd2379d4fa12b391fec7"
)

SELF_ORACLE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-generic-alias-v11-self-oracle.json"
)
SELF_ORACLE_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-generic-alias-v11-self-oracle-failures.json"
)
ALL_CANDIDATE_RELATIVE = (
    "candidates/evidence/python-re-generic-alias-public-oracle-v11-all.json"
)
CANDIDATE_FAILURE_RELATIVES = {
    family: (
        "candidates/evidence/python-re-generic-alias-public-oracle-v11-"
        + family + "-failures.json"
    )
    for family in REQUIRED_CANDIDATES
}
APPROVED_OUTPUTS = (
    SELF_ORACLE_RELATIVE,
    SELF_ORACLE_FAILURE_RELATIVE,
    ALL_CANDIDATE_RELATIVE,
    *(CANDIDATE_FAILURE_RELATIVES[role] for role in REQUIRED_CANDIDATES),
)
MAX_WORKER_BYTES = 1024 * 1024


def _cohort_seed(cohort: str) -> str:
    frozen.require(cohort in dict(COHORTS), "unknown generic-alias cohort")
    return digest({"domain": SEED_DOMAIN, "seed": SEED, "cohort": cohort})


def _matrix_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def append(cohort: str, origin: str, argument: str, action: str) -> None:
        rows.append({
            "id": cohort + ":" + origin + ":" + argument + ":" + action,
            "cohort": cohort,
            "origin": origin,
            "argument": argument,
            "action": action,
            "seed": _cohort_seed(cohort),
        })

    for origin in ORIGINS:
        for argument in NORMAL_ARGUMENTS:
            for action in NORMAL_ACTIONS:
                append("ordinary-alias", origin, argument, action)
    for origin in ORIGINS:
        for argument in DIVERSE_ARGUMENTS:
            for action in DIVERSE_ACTIONS:
                append("diverse-argument", origin, argument, action)
    for origin in ORIGINS:
        for argument in NORMAL_ARGUMENTS:
            for action in REJECTION_ACTIONS:
                append("parameterized-type-rejection", origin, argument, action)
    for origin in ORIGINS:
        for argument in NORMAL_ARGUMENTS:
            for action in LIFECYCLE_ACTIONS:
                append("alias-lifecycle", origin, argument, action)
    return rows


MATRIX_SHA256 = (
    "7e5adbf2ca9c0f752a0c9dddaabe812a780cf58ca9b60efc178bafbaceee7e65"
)


def validate_matrix(matrix: Any) -> None:
    frozen.require(
        isinstance(matrix, list)
        and len(matrix) == EXPECTED_CASES
        and matrix == _matrix_rows()
        and digest(matrix) == MATRIX_SHA256
        and len({row["id"] for row in matrix}) == EXPECTED_CASES,
        "the frozen generic-alias matrix omitted, reordered, or changed a case",
    )
    for cohort, expected in COHORTS:
        frozen.require(
            sum(row["cohort"] == cohort for row in matrix) == expected,
            "the generic-alias matrix changed a public cohort: " + cohort,
        )


def build_matrix() -> list[dict[str, Any]]:
    rows = _matrix_rows()
    validate_matrix(rows)
    return rows


def _operand(name: str) -> Any:
    values = {
        "str": str,
        "bytes": bytes,
        "int": int,
        "none": None,
        "ellipsis": Ellipsis,
        "empty-tuple": (),
        "str-and-bytes": (str, bytes),
        "type-variable": TYPE_PARAMETER,
        "nested-list-str": list[str],
        "object": object,
    }
    frozen.require(name in values, "unrecognized frozen generic type argument")
    return values[name]


def _normal(value: Any, public_module: Any = None) -> Any:
    if value is TYPE_PARAMETER:
        return {
            "kind": "type-variable", "name": TYPE_PARAMETER.__name__,
            "module": "typing",
        }
    if isinstance(value, types.GenericAlias):
        origin = value.__origin__
        return {
            "kind": "types.GenericAlias",
            "origin": _normal(origin, public_module),
            "arguments": _normal(value.__args__, public_module),
            "parameters": _normal(value.__parameters__, public_module),
            "representation": _alias_representation(value, public_module),
        }
    if isinstance(value, type):
        if public_module is not None:
            for public_name in ORIGINS:
                if value is getattr(public_module, public_name, None):
                    return {
                        "kind": "type", "module": "re", "name": public_name,
                        "exact_public_origin": True,
                    }
        return {
            "kind": "type", "module": value.__module__,
            "name": value.__qualname__,
        }
    if value is Ellipsis:
        return {"kind": "ellipsis"}
    if isinstance(value, tuple):
        return {
            "kind": "tuple",
            "items": [_normal(item, public_module) for item in value],
        }
    if isinstance(value, list):
        return [_normal(item, public_module) for item in value]
    if isinstance(value, dict):
        return {
            key: _normal(item, public_module)
            for key, item in sorted(value.items())
        }
    return stage07._normalize(value)


def _alias_representation(
    alias: types.GenericAlias, public_module: Any,
) -> dict[str, Any]:
    origin = alias.__origin__
    origin_module = getattr(origin, "__module__", None)
    actual = repr(alias)
    normalized = actual
    public_name: str | None = None
    if public_module is not None:
        for name in ORIGINS:
            if origin is getattr(public_module, name, None):
                public_name = name
                break
    if (
        public_name is not None
        and type(origin_module) is str
        and type(getattr(origin, "__qualname__", None)) is str
    ):
        prefix = origin_module + "." + origin.__qualname__
        normalized = actual.replace(prefix, "re." + public_name, 1)
    return {
        "text": normalized,
        "public_origin_name": public_name,
        "exact_public_origin": public_name is not None,
    }


def _ordinary(module: Any, row: dict[str, Any]) -> Any:
    origin = getattr(module, row["origin"])
    argument = _operand(row["argument"])
    alias = origin[argument]
    action = row["action"]
    if action == "generic-alias-type":
        return {
            "actual_type": _normal(type(alias), module),
            "is_generic_alias": isinstance(alias, types.GenericAlias),
        }
    if action == "exact-origin":
        return {
            "origin": _normal(alias.__origin__, module),
            "same_public_origin": alias.__origin__ is origin,
        }
    if action == "exact-arguments":
        return _normal(alias.__args__, module)
    if action == "exact-parameters":
        return _normal(alias.__parameters__, module)
    if action == "typing-origin":
        observed = typing.get_origin(alias)
        return {
            "origin": _normal(observed, module),
            "same_public_origin": observed is origin,
        }
    if action == "typing-arguments":
        return _normal(typing.get_args(alias), module)
    if action == "public-representation":
        return _alias_representation(alias, module)
    repeated = origin[argument]
    if action == "repeated-equality":
        return {
            "equal": alias == repeated,
            "reverse_equal": repeated == alias,
        }
    if action == "different-equality":
        other_origin = getattr(module, "Match" if row["origin"] == "Pattern" else "Pattern")
        other_argument = bytes if argument is str else str
        return {
            "different_origin_equal": alias == other_origin[argument],
            "different_argument_equal": alias == origin[other_argument],
        }
    frozen.require(action == "equal-hash-relation", "unknown ordinary alias action")
    return {
        "aliases_equal": alias == repeated,
        "equal_hashes": hash(alias) == hash(repeated),
        "hash_is_integer": type(hash(alias)) is int,
    }


def _diverse(module: Any, row: dict[str, Any]) -> Any:
    origin = getattr(module, row["origin"])
    alias = origin[_operand(row["argument"])]
    action = row["action"]
    if action == "construction":
        return {
            "actual_type": _normal(type(alias), module),
            "is_generic_alias": isinstance(alias, types.GenericAlias),
            "origin": _normal(alias.__origin__, module),
            "same_public_origin": alias.__origin__ is origin,
            "representation": _alias_representation(alias, module),
        }
    if action == "arguments":
        return {
            "arguments": _normal(alias.__args__, module),
            "typing_arguments": _normal(typing.get_args(alias), module),
        }
    frozen.require(action == "parameters-and-typing", "unknown diverse alias action")
    observed = typing.get_origin(alias)
    return {
        "parameters": _normal(alias.__parameters__, module),
        "typing_origin": _normal(observed, module),
        "same_public_origin": observed is origin,
        "typing_arguments": _normal(typing.get_args(alias), module),
    }


def _rejection(module: Any, row: dict[str, Any]) -> Any:
    origin = getattr(module, row["origin"])
    alias = origin[_operand(row["argument"])]
    action = row["action"]
    if action == "isinstance-real-instance":
        compiled = module.compile("a")
        instance = compiled if row["origin"] == "Pattern" else compiled.search("a")
        frozen.require(instance is not None, "the generic-alias real match is missing")
        return isinstance(instance, alias)
    if action == "isinstance-other-instance":
        return isinstance(object(), alias)
    if action == "issubclass-real-origin":
        return issubclass(origin, alias)
    frozen.require(action == "issubclass-other-origin", "unknown alias rejection action")
    return issubclass(object, alias)


def _lifecycle(module: Any, row: dict[str, Any]) -> Any:
    origin = getattr(module, row["origin"])
    alias = origin[_operand(row["argument"])]
    action = row["action"]
    protocol: int | None = None
    if action == "copy":
        restored = copy.copy(alias)
    elif action == "deepcopy":
        restored = copy.deepcopy(alias)
    else:
        protocols = {
            "pickle-protocol-0": 0,
            "pickle-protocol-2": 2,
            "pickle-protocol-4": 4,
            "pickle-highest-protocol": pickle.HIGHEST_PROTOCOL,
        }
        frozen.require(action in protocols, "unknown alias serialization protocol")
        protocol = protocols[action]
        restored = pickle.loads(pickle.dumps(alias, protocol=protocol))
    frozen.require(
        isinstance(restored, types.GenericAlias),
        "the public alias lifecycle returned a non-generic replacement",
    )
    return {
        "protocol": protocol,
        "actual_type": _normal(type(restored), module),
        "origin": _normal(restored.__origin__, module),
        "same_public_origin": restored.__origin__ is origin,
        "arguments": _normal(restored.__args__, module),
        "parameters": _normal(restored.__parameters__, module),
        "representation": _alias_representation(restored, module),
        "equal": restored == alias,
        "reverse_equal": alias == restored,
        "equal_hashes": hash(restored) == hash(alias),
    }


def evaluate_case(module: Any, row: dict[str, Any]) -> dict[str, Any]:
    with warnings.catch_warnings(record=True) as observed_warnings:
        warnings.simplefilter("always")
        try:
            handlers = {
                "ordinary-alias": _ordinary,
                "diverse-argument": _diverse,
                "parameterized-type-rejection": _rejection,
                "alias-lifecycle": _lifecycle,
            }
            frozen.require(row["cohort"] in handlers, "unrecognized alias case cohort")
            result: dict[str, Any] = {
                "status": "returned",
                "value": _normal(handlers[row["cohort"]](module, row), module),
            }
        except (Exception, RecursionError) as error:
            result = {"status": "raised", "exception": stage07._normalize(error)}
        captured = [
            {
                "category": item.category.__name__,
                "message": str(item.message),
            }
            for item in observed_warnings
        ]
    return {
        "id": row["id"],
        "cohort": row["cohort"],
        "origin": row["origin"],
        "argument": row["argument"],
        "action": row["action"],
        **result,
        "warnings": captured,
    }


def _public_origin_provenance(module: Any) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for public_name in ORIGINS:
        origin = getattr(module, public_name, None)
        frozen.require(
            isinstance(origin, type),
            "the evaluated module omitted its real public " + public_name,
        )
        result[public_name] = {
            "actual_module": origin.__module__,
            "actual_name": origin.__name__,
            "actual_qualified_name": origin.__qualname__,
            "public_name": public_name,
        }
    return result


def _validate_preserved_all(
    document: Any,
    *,
    provenance: dict[str, Any],
    reference: dict[str, Any],
) -> dict[str, Any]:
    frozen.require(isinstance(document, dict), "the passed stage-ten comparison is absent")
    exact: dict[str, Any] = {
        "schema": "rebar-python-re-public-contract-v10-all-candidates",
        "status": "PASS",
        "result": "PASS",
        "selected": "all",
        "selected_candidates": list(REQUIRED_CANDIDATES),
        "completed_candidates": list(REQUIRED_CANDIDATES),
        "comparison_complete": True,
        "python": "3.14.6",
        "source_path": STAGE10_SOURCE_RELATIVE,
        "source_sha256": STAGE10_SOURCE_SHA256,
        "protocol_path": STAGE10_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE10_PROTOCOL_SHA256,
        "matrix_sha256": stage10.MATRIX_SHA256,
        "cohorts": 8,
        "cases_per_candidate": 3_584,
        "candidate_checks": 10_752,
        "mismatches": 0,
        "candidate_cross_delegation": False,
        "external_regex_packages": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for field, expected in exact.items():
        frozen.require(
            document.get(field) == expected
            and type(document.get(field)) is type(expected),
            "invalid actually passing stage-ten comparison: " + field,
        )
    frozen.require(
        document.get("current_provenance") == provenance
        and document.get("self_oracle_path") == STAGE10_SELF_RELATIVE
        and document.get("self_oracle_sha256") == STAGE10_SELF_SHA256,
        "the passed three-engine report is not bound to both real Python references",
    )
    reports = document.get("candidate_reports")
    frozen.require(
        isinstance(reports, dict)
        and set(reports) == set(REQUIRED_CANDIDATES),
        "the passed stage-ten comparison omitted a from-scratch family",
    )
    for role in REQUIRED_CANDIDATES:
        report = reports[role]
        frozen.require(
            isinstance(report, dict)
            and report.get("candidate") == role
            and report.get("module") == "candidates." + role + "_candidate"
            and report.get("status") == "PASS"
            and report.get("cases") == 3_584
            and report.get("mismatches") == 0
            and report.get("failure_records") == []
            and report.get("failures_recorded") == 0
            and report.get("record_sha256") == reference["baseline_record_sha256"]
            and report.get("native_binary_sha256")
            == provenance["native_sha256_by_family"][role]
            and report.get("benchmark_or_timing_executed") is False
            and report.get("holdout_cases_read") == 0
            and report.get("performance") == "NOT MEASURED",
            "the passed stage-ten native proof changed: " + role,
        )
        guard = report.get("guard")
        metadata = guard.get("isolated_public_metadata") if isinstance(guard, dict) else None
        frozen.require(
            isinstance(guard, dict)
            and guard.get("enabled") is True
            and guard.get("family") == role
            and guard.get("stdlib_re_blocked") is True
            and guard.get("cpython_sre_blocked") is True
            and guard.get("third_party_regex_blocked") is True
            and guard.get("cross_family_blocked") is True
            and guard.get("foreign_dynamic_libraries_blocked") is True
            and guard.get("native_loader_aliases_blocked")
            == list(stage07.NATIVE_LOADER_ALIASES)
            and isinstance(metadata, dict)
            and metadata.get("enabled") is True
            and metadata.get("role") == role
            and metadata.get("source_sha256") == STAGE10_SOURCE_SHA256
            and metadata.get("surface_cases") == 256
            and metadata.get("production_matching_executed") is False
            and metadata.get("metadata_and_matcher_processes_distinct") is True
            and metadata.get("matcher_inspect_loaded") is False
            and metadata.get("matcher_tokenizer_loaded") is False,
            "the preserved stage-ten no-delegation proof was weakened: " + role,
        )
    return document


def _authenticate_provenance() -> dict[str, Any]:
    official_locale.verify_runtime()
    frozen.candidate_free()
    for relative, expected in (
        (STAGE10_SOURCE_RELATIVE, STAGE10_SOURCE_SHA256),
        (STAGE10_PROTOCOL_RELATIVE, STAGE10_PROTOCOL_SHA256),
    ):
        source = official_locale.checked_repo_path(relative)
        frozen.require(
            official_locale.sha256_path(source, maximum=frozen.MAX_SOURCE_BYTES)
            == expected,
            "the generic-alias stage changed a frozen stage-ten artifact: " + relative,
        )
    with stage10._stage10_context():
        inherited = stage10._authenticate_current_provenance()
        frozen.require(
            inherited.get("source_path") == STAGE10_SOURCE_RELATIVE
            and inherited.get("source_sha256") == STAGE10_SOURCE_SHA256
            and inherited.get("protocol_path") == STAGE10_PROTOCOL_RELATIVE
            and inherited.get("protocol_sha256") == STAGE10_PROTOCOL_SHA256
            and inherited.get("observation_domain") == stage10.OBSERVATION_DOMAIN,
            "the generic-alias oracle lost frozen stage-ten source provenance",
        )
        baseline, baseline_sha = stage06._read_public_document(
            STAGE10_SELF_RELATIVE,
            expected_sha256=STAGE10_SELF_SHA256,
        )
        reference = stage07._validate_self_oracle(baseline, inherited)
        comparison, comparison_sha = stage06._read_public_document(
            STAGE10_ALL_RELATIVE,
            expected_sha256=STAGE10_ALL_SHA256,
        )
        _validate_preserved_all(
            comparison, provenance=inherited, reference=reference,
        )
    frozen.require(
        baseline_sha == STAGE10_SELF_SHA256
        and comparison_sha == STAGE10_ALL_SHA256,
        "the exact passing stage-ten references were substituted",
    )
    source = official_locale.checked_repo_path(SOURCE_RELATIVE)
    protocol = official_locale.checked_repo_path(PROTOCOL_RELATIVE)
    source_sha256 = official_locale.sha256_path(
        source, maximum=frozen.MAX_SOURCE_BYTES,
    )
    protocol_sha256 = official_locale.sha256_path(
        protocol, maximum=frozen.MAX_SOURCE_BYTES,
    )
    validate_matrix(build_matrix())
    frozen.candidate_free()
    return {
        "source_path": SOURCE_RELATIVE,
        "source_sha256": source_sha256,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": protocol_sha256,
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "stage10_source_path": STAGE10_SOURCE_RELATIVE,
        "stage10_source_sha256": STAGE10_SOURCE_SHA256,
        "stage10_protocol_path": STAGE10_PROTOCOL_RELATIVE,
        "stage10_protocol_sha256": STAGE10_PROTOCOL_SHA256,
        "stage10_self_oracle_path": STAGE10_SELF_RELATIVE,
        "stage10_self_oracle_sha256": STAGE10_SELF_SHA256,
        "stage10_all_candidates_path": STAGE10_ALL_RELATIVE,
        "stage10_all_candidates_sha256": STAGE10_ALL_SHA256,
        "stage10_cases_per_role": 3_584,
        "stage10_stdlib_checks": 7_168,
        "stage10_candidate_checks": 10_752,
        "stage10_provenance": inherited,
        "native_sha256_by_family": inherited["native_sha256_by_family"],
    }


def _worker_report(role: str, source_sha256: str) -> dict[str, Any]:
    frozen.require(
        role in ("stdlib-a", "stdlib-b", *REQUIRED_CANDIDATES),
        "the generic-alias worker received an unknown family",
    )
    provenance = _authenticate_provenance()
    frozen.require(
        provenance["source_sha256"] == source_sha256,
        "the isolated generic-alias worker substituted its source",
    )
    matrix = build_matrix()
    if role in ("stdlib-a", "stdlib-b"):
        frozen.candidate_free()
        module = importlib.import_module("re")
        guard: dict[str, Any] = {
            "baseline_only": True, "candidate_imported": False,
        }
        natives: dict[str, str] = {}
    else:
        frozen.require(
            "inspect" not in sys.modules and "tokenize" not in sys.modules,
            "the generic-alias matching worker contains a tokenizer or inspector",
        )
        expected_native = provenance["native_sha256_by_family"].get(role)
        frozen.require(
            isinstance(expected_native, dict) and bool(expected_native),
            "the generic-alias candidate has no audited owned native engine",
        )
        guard = stage07._install_family_guard(role, expected_native)
        module = importlib.import_module("candidates." + role + "_candidate")
        natives = stage07._verify_family_native_mappings(
            role, provenance["stage10_provenance"],
        )
        allowed = {"candidates." + role + "_candidate"}
        bridge = {
            "rust": "candidates._rust_bridge",
            "vm": "candidates._vm_native",
            "zig": "candidates._zig_bridge",
        }[role]
        allowed.add(bridge)
        loaded = {
            name
            for name, value in sys.modules.items()
            if name.startswith("candidates.")
            and value is not None
            and not isinstance(value, stage07._ForbiddenRegexModule)
        }
        frozen.require(
            loaded <= allowed,
            "the generic-alias worker loaded a cross-family candidate",
        )
        guard["loaded_candidate_modules"] = sorted(loaded)
        guard["matcher_inspect_loaded"] = False
        guard["matcher_tokenizer_loaded"] = False
    public_origins = _public_origin_provenance(module)
    for public_name, origin in public_origins.items():
        frozen.require(
            origin["actual_name"] == public_name
            and origin["actual_qualified_name"] == public_name,
            "the generic-alias worker substituted a public class identity: "
            + public_name,
        )
    if role in ("stdlib-a", "stdlib-b"):
        frozen.require(
            all(item["actual_module"] == "re" for item in public_origins.values()),
            "the independent Python reference substituted its regex origin",
        )
    else:
        allowed_origin_modules = {
            "re", "candidates." + role + "_candidate",
            {
                "rust": "candidates._rust_bridge",
                "vm": "candidates._vm_native",
                "zig": "candidates._zig_bridge",
            }[role],
        }
        frozen.require(
            all(
                item["actual_module"] in allowed_origin_modules
                for item in public_origins.values()
            ),
            "the candidate's generic alias is owned by a foreign engine",
        )
    records = [evaluate_case(module, row) for row in matrix]
    frozen.require(
        len(records) == EXPECTED_CASES
        and [record["id"] for record in records]
        == [row["id"] for row in matrix],
        "the generic-alias worker concealed or reordered an observation",
    )
    if role in REQUIRED_CANDIDATES:
        frozen.require(
            "inspect" not in sys.modules and "tokenize" not in sys.modules,
            "a generic-alias candidate imported a tokenizer or inspector",
        )
        natives = stage07._verify_family_native_mappings(
            role, provenance["stage10_provenance"],
        )
    return {
        "schema": WORKER_SCHEMA,
        "status": "PASS",
        "role": role,
        "python": "3.14.6",
        "source_sha256": source_sha256,
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cases": EXPECTED_CASES,
        "cohort_cases": dict(COHORTS),
        "records": records,
        "record_sha256": digest(records),
        "guard": guard,
        "native_binary_sha256": natives,
        "public_origins": public_origins,
        "inspect_loaded": "inspect" in sys.modules,
        "tokenize_loaded": "tokenize" in sys.modules,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }


WORKER_BOOTSTRAP = (
    "import sys;sys.path.insert(0,sys.argv[1]);"
    "from tools.python_re_generic_alias_public_oracle_stage11 "
    "import _worker_entry;"
    "raise SystemExit(_worker_entry(sys.argv[2],sys.argv[3]))"
)


def _worker_entry(role: str, source_sha256: str) -> int:
    try:
        report = _worker_report(role, source_sha256)
        sys.stdout.buffer.write(canonical(report) + b"\n")
        sys.stdout.buffer.flush()
        return 0
    except (Exception, RecursionError) as error:
        failure = {
            "schema": WORKER_SCHEMA,
            "status": "FAIL",
            "role": role,
            "error": stage07._normalize(error),
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
        }
        sys.stdout.buffer.write(canonical(failure) + b"\n")
        sys.stdout.buffer.flush()
        return 1


def _validate_worker(
    document: Any, *, role: str, source_sha256: str,
) -> dict[str, Any]:
    frozen.require(isinstance(document, dict), "the generic-alias worker report is invalid")
    expected: dict[str, Any] = {
        "schema": WORKER_SCHEMA,
        "status": "PASS",
        "role": role,
        "python": "3.14.6",
        "source_sha256": source_sha256,
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cases": EXPECTED_CASES,
        "cohort_cases": dict(COHORTS),
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for name, value in expected.items():
        frozen.require(
            document.get(name) == value
            and type(document.get(name)) is type(value),
            "the isolated generic-alias worker changed " + name,
        )
    records = document.get("records")
    frozen.require(
        isinstance(records, list)
        and len(records) == EXPECTED_CASES
        and [item.get("id") for item in records]
        == [row["id"] for row in build_matrix()]
        and document.get("record_sha256") == digest(records),
        "the isolated generic-alias worker concealed exact public observations",
    )
    guard = document.get("guard")
    public_origins = document.get("public_origins")
    frozen.require(
        isinstance(public_origins, dict)
        and set(public_origins) == set(ORIGINS)
        and all(
            isinstance(public_origins[name], dict)
            and public_origins[name].get("public_name") == name
            and public_origins[name].get("actual_name") == name
            and public_origins[name].get("actual_qualified_name") == name
            and type(public_origins[name].get("actual_module")) is str
            for name in ORIGINS
        ),
        "the isolated generic-alias worker concealed an actual class origin",
    )
    if role in ("stdlib-a", "stdlib-b"):
        frozen.require(
            guard == {"baseline_only": True, "candidate_imported": False}
            and document.get("native_binary_sha256") == {}
            and all(
                item["actual_module"] == "re"
                for item in public_origins.values()
            ),
            "the standard-library alias worker imported a candidate",
        )
    else:
        allowed_origin_modules = {
            "re", "candidates." + role + "_candidate",
            {
                "rust": "candidates._rust_bridge",
                "vm": "candidates._vm_native",
                "zig": "candidates._zig_bridge",
            }[role],
        }
        frozen.require(
            isinstance(guard, dict)
            and guard.get("enabled") is True
            and guard.get("family") == role
            and guard.get("stdlib_re_blocked") is True
            and guard.get("cpython_sre_blocked") is True
            and guard.get("third_party_regex_blocked") is True
            and guard.get("cross_family_blocked") is True
            and guard.get("foreign_dynamic_libraries_blocked") is True
            and guard.get("native_loader_aliases_blocked")
            == list(stage07.NATIVE_LOADER_ALIASES)
            and guard.get("matcher_inspect_loaded") is False
            and guard.get("matcher_tokenizer_loaded") is False
            and document.get("inspect_loaded") is False
            and document.get("tokenize_loaded") is False
            and isinstance(document.get("native_binary_sha256"), dict)
            and bool(document["native_binary_sha256"])
            and all(
                item["actual_module"] in allowed_origin_modules
                for item in public_origins.values()
            ),
            "the generic-alias candidate weakened the audited no-delegation guard",
        )
    return document


def _run_worker(role: str, *, source_sha256: str) -> dict[str, Any]:
    frozen.require(
        role in ("stdlib-a", "stdlib-b", *REQUIRED_CANDIDATES),
        "refusing an unaudited generic-alias process",
    )
    command = [
        str(stage07.PINNED_INTERPRETER), "-I", "-B", "-c",
        WORKER_BOOTSTRAP, str(ROOT), role, source_sha256,
    ]
    environment = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONPATH": str(ROOT),
        "LC_ALL": "C",
        "PATH": "/usr/bin:/bin",
    }
    try:
        child = stage07.subprocess.run(
            command,
            cwd=str(ROOT),
            env=environment,
            stdin=stage07.subprocess.DEVNULL,
            stdout=stage07.subprocess.PIPE,
            stderr=stage07.subprocess.PIPE,
            check=False,
            timeout=600,
        )
    except stage07.subprocess.SubprocessError as error:
        raise stage07.PublicWorkerFailure(
            role,
            "the isolated generic-alias process did not complete",
            {"kind": type(error).__name__, "exception": stage07._normalize(error)},
        ) from error
    if not 0 < len(child.stdout) <= MAX_WORKER_BYTES or len(child.stderr) > MAX_WORKER_BYTES:
        raise stage07.PublicWorkerFailure(
            role,
            "the isolated generic-alias worker returned unsafe evidence",
            {
                "kind": "invalid-bounded-worker-output",
                "returncode": child.returncode,
                "stdout_bytes": len(child.stdout),
                "stderr_bytes": len(child.stderr),
            },
        )
    try:
        document = json.loads(child.stdout)
    except (UnicodeError, ValueError) as error:
        raise stage07.PublicWorkerFailure(
            role,
            "the isolated generic-alias worker returned malformed evidence",
            {
                "kind": "malformed-worker-evidence",
                "returncode": child.returncode,
                "exception": stage07._normalize(error),
            },
        ) from error
    if child.returncode != 0:
        raise stage07.PublicWorkerFailure(
            role,
            "the isolated generic-alias worker failed",
            {
                "kind": "worker-nonzero-exit",
                "returncode": child.returncode,
                "worker_report": document,
                "stderr": stage07._normalize(child.stderr),
            },
        )
    return _validate_worker(document, role=role, source_sha256=source_sha256)


def _exclusive_evidence(document: dict[str, Any], relative: str) -> str:
    frozen.require(
        type(relative) is str and relative in APPROVED_OUTPUTS,
        "the generic-alias oracle rejected an unapproved evidence destination",
    )
    path = PurePosixPath(relative)
    frozen.require(
        not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in relative
        and "\x00" not in relative
        and str(path) == relative,
        "the generic-alias oracle rejected an unsafe evidence path",
    )
    target = ROOT / relative
    parent = target.parent
    frozen.require(
        parent.is_dir()
        and not parent.is_symlink()
        and parent.resolve(strict=True).is_relative_to(ROOT.resolve(strict=True))
        and not target.is_symlink(),
        "the generic-alias evidence escaped its approved repository directory",
    )
    flags = (
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(target, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as output:
            descriptor = -1
            output.write(canonical(document) + b"\n")
            output.flush()
            os.fsync(output.fileno())
        directory = os.open(parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    return official_locale.sha256_path(
        target, maximum=official_locale.MAX_JSON_BYTES,
    )


def _mismatches(
    expected: list[dict[str, Any]], actual: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    frozen.require(
        len(expected) == len(actual) == EXPECTED_CASES,
        "the generic-alias comparison changed its public denominator",
    )
    mismatches: list[dict[str, Any]] = []
    for left, right in zip(expected, actual, strict=True):
        frozen.require(
            left.get("id") == right.get("id"),
            "the generic-alias comparison changed a case identity",
        )
        if left != right:
            mismatches.append({
                "id": left["id"], "expected": left, "actual": right,
            })
    return mismatches


def _persist_failure(
    *, role: str, provenance: dict[str, Any],
    baseline: list[dict[str, Any]] | None,
    error: BaseException | None = None,
    observed: list[dict[str, Any]] | None = None,
    mismatch_records: list[dict[str, Any]] | None = None,
    completed: dict[str, Any] | None = None,
    self_oracle_sha256: str | None = None,
) -> str:
    baseline_role = role in ("stdlib-a", "stdlib-b")
    frozen.require(
        baseline_role or role in REQUIRED_CANDIDATES,
        "refusing to preserve an unknown generic-alias failure",
    )
    output = (
        SELF_ORACLE_FAILURE_RELATIVE if baseline_role
        else CANDIDATE_FAILURE_RELATIVES[role]
    )
    details = None
    if error is not None:
        details = (
            error.details
            if isinstance(error, stage07.PublicWorkerFailure)
            else {"kind": type(error).__name__, "exception": stage07._normalize(error)}
        )
    records = mismatch_records if mismatch_records is not None else []
    document = {
        "schema": (
            SELF_ORACLE_SCHEMA + "-failure"
            if baseline_role else ALL_CANDIDATE_SCHEMA + "-failure"
        ),
        "status": "FAIL",
        "result": "FAIL",
        "failed_role": role,
        "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "source_sha256": provenance["source_sha256"],
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": provenance["protocol_sha256"],
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": len(COHORTS),
        "cohort_cases": dict(COHORTS),
        "expected_cases": EXPECTED_CASES,
        "baseline_records": baseline,
        "candidate_records": observed,
        "mismatches": len(records),
        "failure_records": records,
        "failures_recorded": len(records),
        "worker_failure": details,
        "completed_candidate_reports": completed,
        "self_oracle_path": None if baseline_role else SELF_ORACLE_RELATIVE,
        "self_oracle_sha256": self_oracle_sha256,
        "current_provenance": provenance,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    sha256 = _exclusive_evidence(document, output)
    return output + " (sha256 " + sha256 + ")"


def _base_document(provenance: dict[str, Any]) -> dict[str, Any]:
    return {
        "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "source_sha256": provenance["source_sha256"],
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": provenance["protocol_sha256"],
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": len(COHORTS),
        "cohort_cases": dict(COHORTS),
        "current_provenance": provenance,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }


def run_self_oracle() -> dict[str, Any]:
    provenance = _authenticate_provenance()
    frozen.require(
        not (ROOT / SELF_ORACLE_RELATIVE).exists(),
        "the exclusively frozen generic-alias Python reference already exists",
    )
    first: list[dict[str, Any]] | None = None
    for role in ("stdlib-a", "stdlib-b"):
        try:
            worker = _run_worker(role, source_sha256=provenance["source_sha256"])
        except (Exception, RecursionError) as error:
            retained = _persist_failure(
                role=role, provenance=provenance, baseline=first, error=error,
            )
            raise frozen.OracleIntegrityError(
                "the independent Python generic-alias failure was preserved in "
                + retained
            ) from error
        if first is None:
            first = worker["records"]
            continue
        differences = _mismatches(first, worker["records"])
        if differences:
            retained = _persist_failure(
                role=role, provenance=provenance, baseline=first,
                observed=worker["records"], mismatch_records=differences,
            )
            raise frozen.OracleIntegrityError(
                "the independent Python generic-alias mismatch was preserved in "
                + retained
            )
    frozen.require(first is not None, "both independent Python references are required")
    document = {
        "schema": SELF_ORACLE_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        **_base_document(provenance),
        "cases": EXPECTED_CASES,
        "stdlib_checks": EXPECTED_CASES * 2,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "baseline_records": first,
        "baseline_record_sha256": digest(first),
        "second_record_sha256": digest(first),
        "mismatches": 0,
        "failure_records": [],
        "candidate_imports": 0,
        "candidate_processes": 0,
    }
    sha256 = _exclusive_evidence(document, SELF_ORACLE_RELATIVE)
    return {
        "schema": SELF_ORACLE_SCHEMA,
        "status": "PASS",
        "cases": EXPECTED_CASES,
        "stdlib_checks": EXPECTED_CASES * 2,
        "mismatches": 0,
        "evidence": SELF_ORACLE_RELATIVE,
        "evidence_sha256": sha256,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
    }


def _validate_self_oracle(
    document: Any, provenance: dict[str, Any],
) -> dict[str, Any]:
    frozen.require(isinstance(document, dict), "the generic-alias reference is absent")
    expected: dict[str, Any] = {
        "schema": SELF_ORACLE_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        **_base_document(provenance),
        "cases": EXPECTED_CASES,
        "stdlib_checks": EXPECTED_CASES * 2,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "mismatches": 0,
        "failure_records": [],
        "candidate_imports": 0,
        "candidate_processes": 0,
    }
    for name, value in expected.items():
        frozen.require(
            document.get(name) == value
            and type(document.get(name)) is type(value),
            "the generic-alias candidate requires a real Python reference: " + name,
        )
    records = document.get("baseline_records")
    frozen.require(
        isinstance(records, list)
        and len(records) == EXPECTED_CASES
        and [record.get("id") for record in records]
        == [row["id"] for row in build_matrix()]
        and document.get("baseline_record_sha256") == digest(records)
        and document.get("second_record_sha256") == digest(records),
        "the generic-alias Python reference concealed a public observation",
    )
    return document


def run_all_candidates() -> dict[str, Any]:
    provenance = _authenticate_provenance()
    frozen.require(
        not (ROOT / ALL_CANDIDATE_RELATIVE).exists(),
        "the exclusively frozen three-family generic-alias report already exists",
    )
    reference, self_sha256 = stage06._read_public_document(
        SELF_ORACLE_RELATIVE, expected_sha256=None,
    )
    _validate_self_oracle(reference, provenance)
    expected = reference["baseline_records"]
    outcomes: dict[str, Any] = {}
    for role in REQUIRED_CANDIDATES:
        try:
            worker = _run_worker(role, source_sha256=provenance["source_sha256"])
        except (Exception, RecursionError) as error:
            retained = _persist_failure(
                role=role, provenance=provenance, baseline=expected,
                error=error, completed=outcomes,
                self_oracle_sha256=self_sha256,
            )
            raise frozen.OracleIntegrityError(
                "the guarded generic-alias worker failure was preserved in " + retained
            ) from error
        differences = _mismatches(expected, worker["records"])
        outcome = {
            "candidate": role,
            "module": "candidates." + role + "_candidate",
            "status": "FAIL" if differences else "PASS",
            "cases": EXPECTED_CASES,
            "cohort_cases": dict(COHORTS),
            "record_sha256": worker["record_sha256"],
            "mismatches": len(differences),
            "failure_records": differences,
            "failures_recorded": len(differences),
            "guard": worker["guard"],
            "native_binary_sha256": worker["native_binary_sha256"],
            "public_origins": worker["public_origins"],
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
        }
        outcomes[role] = outcome
        if differences:
            retained = _persist_failure(
                role=role, provenance=provenance, baseline=expected,
                observed=worker["records"], mismatch_records=differences,
                completed=outcomes, self_oracle_sha256=self_sha256,
            )
            raise frozen.OracleIntegrityError(
                "the real " + role + " generic-alias mismatch was preserved in "
                + retained
            )
    frozen.require(
        set(outcomes) == set(REQUIRED_CANDIDATES),
        "the generic-alias comparison omitted a from-scratch candidate",
    )
    report = {
        "schema": ALL_CANDIDATE_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "selected": "all",
        "selected_candidates": list(REQUIRED_CANDIDATES),
        "completed_candidates": list(REQUIRED_CANDIDATES),
        "comparison_complete": True,
        **_base_document(provenance),
        "cases_per_candidate": EXPECTED_CASES,
        "candidate_checks": EXPECTED_CASES * len(REQUIRED_CANDIDATES),
        "self_oracle_path": SELF_ORACLE_RELATIVE,
        "self_oracle_sha256": self_sha256,
        "baseline_record_sha256": reference["baseline_record_sha256"],
        "candidate_reports": outcomes,
        "candidate_cross_delegation": False,
    }
    sha256 = _exclusive_evidence(report, ALL_CANDIDATE_RELATIVE)
    return {
        "schema": ALL_CANDIDATE_SCHEMA,
        "status": "PASS",
        "cases_per_candidate": EXPECTED_CASES,
        "candidate_checks": EXPECTED_CASES * len(REQUIRED_CANDIDATES),
        "completed_candidates": list(REQUIRED_CANDIDATES),
        "mismatches": 0,
        "evidence": ALL_CANDIDATE_RELATIVE,
        "evidence_sha256": sha256,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
    }


def _synthetic_module(
    owner: str = "rebar_stage11_synthetic_reference", *, forged: bool = False,
) -> Any:
    def class_getitem(origin: type, item: Any) -> types.GenericAlias:
        if forged:
            return types.GenericAlias(list, item)
        return types.GenericAlias(origin, item)

    match_type = type(
        "Match", (), {
            "__module__": owner,
            "__class_getitem__": classmethod(class_getitem),
        },
    )

    def search(_pattern: Any, _subject: str) -> Any:
        return match_type()

    pattern_type = type(
        "Pattern", (), {
            "__module__": owner,
            "__class_getitem__": classmethod(class_getitem),
            "search": search,
        },
    )
    return types.SimpleNamespace(
        Pattern=pattern_type,
        Match=match_type,
        compile=lambda _value: pattern_type(),
    )


_INSPECT_PRESENT_AT_IMPORT = "inspect" in sys.modules
_TOKENIZE_PRESENT_AT_IMPORT = "tokenize" in sys.modules


def self_test() -> dict[str, Any]:
    frozen.candidate_free()
    with stage06.previous._candidate_free_file_and_timing_guard() as effects:
        checks: list[dict[str, Any]] = []

        def check(name: str, value: Any) -> None:
            frozen.require(value, "generic-alias synthetic control failed: " + name)
            checks.append({"name": name, "passed": True})

        def reject(name: str, action: Callable[[], Any]) -> None:
            try:
                action()
            except (
                frozen.OracleIntegrityError, AssertionError, AttributeError,
                ImportError, KeyError, OSError, TypeError, UnicodeError, ValueError,
            ):
                check(name, True)
                return
            check(name, False)

        check(
            "isolated-stage11-source-does-not-import-an-inspector",
            ("inspect" in sys.modules) == _INSPECT_PRESENT_AT_IMPORT,
        )
        check(
            "isolated-stage11-source-does-not-import-a-tokenizer",
            ("tokenize" in sys.modules) == _TOKENIZE_PRESENT_AT_IMPORT,
        )
        inherited_matrix = stage07.build_matrix()
        check(
            "all-3584-frozen-stage10-obligations-remain-source-bound",
            len(inherited_matrix) == 3_584
            and digest(inherited_matrix) == stage10.MATRIX_SHA256,
        )
        check(
            "all-eight-frozen-stage10-cohorts-remain-intact",
            len(stage07.COHORTS) == 8
            and sum(row["cohort"] == "public-surface" for row in inherited_matrix)
            == 256,
        )
        matrix = build_matrix()
        check("all-128-frozen-public-generic-alias-obligations", len(matrix) == 128)
        check("source-bound-distinct-stage11-domain", SEED_DOMAIN == SCHEMA.replace(
            "rebar-python-re-public-generic-alias-v11",
            "rebar/python-re/public-generic-alias/v11",
        ))
        check("exact-fresh-stage11-seed", SEED == 2026072461)
        check("exact-source-bound-canonical-matrix-digest", digest(matrix) == MATRIX_SHA256)
        check("every-public-case-has-a-unique-identity", len({row["id"] for row in matrix}) == 128)
        for cohort, count in COHORTS:
            check(
                "exact-complete-public-cohort-" + cohort,
                sum(row["cohort"] == cohort for row in matrix) == count,
            )
        check("both-real-public-alias-origins", set(ORIGINS) == {"Pattern", "Match"})
        check("both-text-and-binary-public-arguments", set(NORMAL_ARGUMENTS) == {"str", "bytes"})
        check("all-ten-normal-public-alias-observations", len(NORMAL_ACTIONS) == 10)
        check("all-eight-genuinely-diverse-type-operands", len(DIVERSE_ARGUMENTS) == 8)
        check("all-three-diverse-construction-observations", len(DIVERSE_ACTIONS) == 3)
        check("all-four-real-parameterized-rejections", len(REJECTION_ACTIONS) == 4)
        check("all-six-real-copy-and-pickle-lifecycles", len(LIFECYCLE_ACTIONS) == 6)
        check("real-stdlib-types-generic-alias", types.GenericAlias is type(list[str]))
        check("real-stdlib-typing-type-variable", isinstance(TYPE_PARAMETER, typing.TypeVar))
        check("actual-highest-pickle-protocol-is-distinct", pickle.HIGHEST_PROTOCOL not in (0, 2, 4))
        check("real-typing-introspection-is-bound", callable(typing.get_origin) and callable(typing.get_args))
        check("all-five-real-owned-library-loader-denials", stage07.NATIVE_LOADER_ALIASES == (
            "ctypes.CDLL", "ctypes.cdll.LoadLibrary", "ctypes.cdll._dlltype",
            "ctypes._dlopen", "_ctypes.dlopen",
        ))
        check("all-three-independent-frozen-engine-families", REQUIRED_CANDIDATES == stage10.REQUIRED_CANDIDATES)
        check("exact-previous-stage10-source-binding", stage10.SOURCE_RELATIVE == STAGE10_SOURCE_RELATIVE)
        check("exact-previous-stage10-protocol-binding", stage10.PROTOCOL_RELATIVE == STAGE10_PROTOCOL_RELATIVE)
        check("exact-previous-stage10-reference-evidence-binding", stage10.SELF_ORACLE_RELATIVE == STAGE10_SELF_RELATIVE)
        check("exact-previous-stage10-three-candidate-evidence-binding", stage10.ALL_CANDIDATE_RELATIVE == STAGE10_ALL_RELATIVE)
        check("all-six-exclusively-distinct-new-evidence-destinations", len(APPROVED_OUTPUTS) == len(set(APPROVED_OUTPUTS)) == 6)
        check("no-stage10-evidence-can-be-overwritten", not set(APPROVED_OUTPUTS).intersection({
            stage10.SELF_ORACLE_RELATIVE, stage10.SELF_ORACLE_FAILURE_RELATIVE,
            stage10.ALL_CANDIDATE_RELATIVE, *stage10.CANDIDATE_FAILURE_RELATIVES.values(),
        }))
        check("isolated-new-worker-is-source-bound", SOURCE_RELATIVE in WORKER_BOOTSTRAP.replace(
            "tools.python_re_generic_alias_public_oracle_stage11",
            "tools/python_re_generic_alias_public_oracle_stage11.py",
        ))
        for index, mutation in enumerate((
            matrix[:-1],
            matrix[1:],
            list(reversed(matrix)),
            [matrix[0], *matrix[:-1]],
            [{**matrix[0], "action": "hidden"}, *matrix[1:]],
            [{**matrix[0], "origin": "foreign"}, *matrix[1:]],
            [{**matrix[0], "argument": "foreign"}, *matrix[1:]],
            [{**matrix[0], "seed": "0" * 64}, *matrix[1:]],
            [{**matrix[0], "cohort": "hidden"}, *matrix[1:]],
            [{**matrix[0], "id": matrix[1]["id"]}, *matrix[1:]],
        )):
            reject("rejects-poisoned-public-alias-matrix-" + str(index), lambda value=mutation: validate_matrix(value))
        module = _synthetic_module()
        records = [evaluate_case(module, row) for row in matrix]
        check(
            "all-128-synthetic-observations-do-not-import-an-inspector",
            ("inspect" in sys.modules) == _INSPECT_PRESENT_AT_IMPORT,
        )
        check(
            "all-128-synthetic-observations-do-not-import-a-tokenizer",
            ("tokenize" in sys.modules) == _TOKENIZE_PRESENT_AT_IMPORT,
        )
        check("all-128-synthetic-cases-actually-execute", len(records) == EXPECTED_CASES)
        check("all-128-synthetic-case-identities-remain-exact", [item["id"] for item in records] == [row["id"] for row in matrix])
        for cohort, count in COHORTS:
            check(
                "synthetic-observes-every-" + cohort,
                sum(item["cohort"] == cohort for item in records) == count,
            )
        rejections = [record for record in records if record["cohort"] == "parameterized-type-rejection"]
        check("all-16-real-generic-alias-rejections-execute", len(rejections) == 16)
        check("all-16-parameterized-type-errors-are-observed", all(
            item["status"] == "raised" and item["exception"]["type"] == "TypeError"
            for item in rejections
        ))
        check("synthetic-type-variable-is-really-preserved", any(
            item["cohort"] == "diverse-argument"
            and item["argument"] == "type-variable"
            and item["status"] == "returned"
            for item in records
        ))
        check("no-raw-process-randomized-hash-is-an-observation", all(
            "raw_hash" not in item and "hash_value" not in item
            for item in records
        ))
        candidate_like = _synthetic_module("rebar_stage11_synthetic_owner")
        comparable_rows = [
            row for row in matrix
            if not row["action"].startswith("pickle-")
        ]
        reference_comparable = [
            evaluate_case(module, row) for row in comparable_rows
        ]
        candidate_comparable = [
            evaluate_case(candidate_like, row) for row in comparable_rows
        ]
        check(
            "candidate-like-in-memory-origins-do-not-import-an-inspector",
            ("inspect" in sys.modules) == _INSPECT_PRESENT_AT_IMPORT,
        )
        check(
            "exact-owned-candidate-like-origins-normalize-without-false-mismatches",
            len(comparable_rows) == 112
            and reference_comparable == candidate_comparable,
        )
        check(
            "actual-worker-origin-modules-remain-separately-observable",
            _public_origin_provenance(module)["Pattern"]["actual_module"]
            == "rebar_stage11_synthetic_reference"
            and _public_origin_provenance(candidate_like)["Pattern"]["actual_module"]
            == "rebar_stage11_synthetic_owner",
        )
        forged = _synthetic_module("rebar_stage11_synthetic_forgery", forged=True)
        poisoned = evaluate_case(forged, matrix[1])
        check(
            "a-foreign-origin-cannot-be-normalized-into-a-public-origin",
            poisoned["status"] == "returned"
            and poisoned["value"]["same_public_origin"] is False
            and poisoned["value"]["origin"]["name"] == "list",
        )
        expected = [dict(record) for record in records]
        check("identical-public-observations-compare-exactly", _mismatches(expected, records) == [])
        altered = [dict(record) for record in records]
        altered[0] = {**altered[0], "warnings": [{"category": "UserWarning", "message": "poison"}]}
        check("actual-warning-substitution-is-rejected", len(_mismatches(expected, altered)) == 1)
        altered = [dict(record) for record in records]
        altered[1] = {**altered[1], "status": "raised", "exception": {"type": "TypeError", "args": {"type": "tuple", "items": []}}}
        check("actual-return-or-exception-substitution-is-rejected", len(_mismatches(expected, altered)) == 1)
        reject("omitted-reference-observation-is-rejected", lambda: _mismatches(expected[:-1], records))
        reject("omitted-candidate-observation-is-rejected", lambda: _mismatches(expected, records[:-1]))
        reordered = list(records)
        reordered[0], reordered[1] = reordered[1], reordered[0]
        reject("reordered-candidate-observations-are-rejected", lambda: _mismatches(expected, reordered))
        check(
            "no-candidate-module-is-imported-by-synthetic-controls",
            not any(
                name == "candidates" or name.startswith("candidates.")
                for name in sys.modules
            ),
        )
        check(
            "synthetic-controls-do-not-import-an-inspector",
            ("inspect" in sys.modules) == _INSPECT_PRESENT_AT_IMPORT,
        )
        check(
            "synthetic-controls-do-not-import-a-tokenizer",
            ("tokenize" in sys.modules) == _TOKENIZE_PRESENT_AT_IMPORT,
        )
        check("synthetic-test-never-starts-a-worker", effects["workers"] == 0)
        check("synthetic-test-never-opens-or-writes-a-file", effects["files"] == 0)
        check("synthetic-test-never-reads-a-clock", effects["timing"] == 0)
        check("synthetic-test-never-reads-production-entropy", effects["entropy"] == 0)
        check("all-synthetic-effect-counters-stay-zero", all(value == 0 for value in effects.values()))
        frozen.candidate_free()
        check("synthetic-test-never-imports-a-production-candidate", True)
        names = [item["name"] for item in checks]
        frozen.require(
            len(names) == len(set(names)) and len(checks) >= 45,
            "the generic-alias synthetic safety controls were weakened",
        )
        return {
            "schema": SELF_TEST_SCHEMA,
            "stage": "stage11",
            "status": "PASS",
            "result": "PASS",
            "seed": SEED,
            "seed_domain": SEED_DOMAIN,
            "matrix_sha256": MATRIX_SHA256,
            "cohorts": len(COHORTS),
            "cohort_cases": dict(COHORTS),
            "cases": EXPECTED_CASES,
            "inherited_stage10_synthetic_self_test_executed": False,
            "inherited_stage10_matrix_cases": len(inherited_matrix),
            "inherited_stage10_matrix_sha256": stage10.MATRIX_SHA256,
            "checks": checks,
            "check_count": len(checks),
            "failed": [],
            "candidate_imports": 0,
            "candidate_processes": 0,
            "inspect_present_before_self_test": _INSPECT_PRESENT_AT_IMPORT,
            "inspect_imported_by_self_test": (
                ("inspect" in sys.modules) != _INSPECT_PRESENT_AT_IMPORT
            ),
            "tokenize_present_before_self_test": _TOKENIZE_PRESENT_AT_IMPORT,
            "tokenize_imported_by_self_test": (
                ("tokenize" in sys.modules) != _TOKENIZE_PRESENT_AT_IMPORT
            ),
            "files_read": 0,
            "files_written": 0,
            "clock_samples": 0,
            "entropy_drawn": False,
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
            "self_oracle_executed": False,
            "production_evidence_written": False,
            "stage10_source_sha256": STAGE10_SOURCE_SHA256,
            "stage10_protocol_sha256": STAGE10_PROTOCOL_SHA256,
            "stage10_self_oracle_sha256": STAGE10_SELF_SHA256,
            "stage10_all_candidates_sha256": STAGE10_ALL_SHA256,
            "native_loader_aliases_blocked": list(stage07.NATIVE_LOADER_ALIASES),
            "self_oracle_output": SELF_ORACLE_RELATIVE,
            "self_oracle_failure_output": SELF_ORACLE_FAILURE_RELATIVE,
            "all_candidate_output": ALL_CANDIDATE_RELATIVE,
            "candidate_failure_outputs": dict(CANDIDATE_FAILURE_RELATIVES),
        }


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    try:
        if arguments == ["--self-test"]:
            document = self_test()
        elif arguments == ["--self-oracle"]:
            document = run_self_oracle()
        elif arguments == ["--candidate", "all"]:
            document = run_all_candidates()
        else:
            raise frozen.OracleIntegrityError(
                "select exactly --self-test, --self-oracle, or --candidate all"
            )
        sys.stdout.buffer.write(canonical(document) + b"\n")
        sys.stdout.buffer.flush()
        return 0
    except (
        frozen.OracleIntegrityError, AssertionError, OSError,
        TypeError, UnicodeError, ValueError, stage07.subprocess.SubprocessError,
    ) as error:
        sys.stderr.buffer.write(
            canonical({"schema": SCHEMA, "status": "FAIL", "error": str(error)})
            + b"\n"
        )
        sys.stderr.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
