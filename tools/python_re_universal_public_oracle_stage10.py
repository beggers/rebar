#!/usr/bin/env python3
"""Check the full Python regex surface with an isolated metadata observer."""

from __future__ import annotations

import sys

if __name__ == "__main__":
    import os as _stage10_os
    from pathlib import Path as _Stage10Path

    _stage10_root = str(_Stage10Path(__file__).resolve().parent.parent)
    _stage10_entry = (
        "import sys;sys.path.insert(0,sys.argv[1]);"
        "from tools.python_re_universal_public_oracle_stage10 import main;"
        "raise SystemExit(main(sys.argv[2:]))"
    )
    _stage10_os.execv(
        sys.executable,
        [sys.executable, "-I", "-B", "-c", _stage10_entry, _stage10_root, *sys.argv[1:]],
    )

import argparse
import importlib
import json
import os
import types
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator


ROOT = Path(__file__).resolve().parent.parent
SOURCE_RELATIVE = "tools/python_re_universal_public_oracle_stage10.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V10.md"
SCHEMA = "rebar-python-re-public-contract-v10"
SELF_TEST_SCHEMA = SCHEMA + "-self-test"
SELF_ORACLE_SCHEMA = SCHEMA + "-self-oracle"
ALL_CANDIDATE_SCHEMA = SCHEMA + "-all-candidates"
OBSERVATION_DOMAIN = "rebar/python-re/public-contract/v10"
SELF_ORACLE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-contract-v10-self-oracle.json"
)
SELF_ORACLE_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-contract-v10-self-oracle-failures.json"
)
ALL_CANDIDATE_RELATIVE = (
    "candidates/evidence/python-re-universal-public-oracle-v10-all.json"
)
REQUIRED_CANDIDATES = ("rust", "vm", "zig")
CANDIDATE_FAILURE_RELATIVES = {
    family: (
        "candidates/evidence/python-re-universal-public-oracle-v10-"
        + family
        + "-failures.json"
    )
    for family in REQUIRED_CANDIDATES
}
FROZEN_STAGE08_SOURCE_RELATIVE = (
    "tools/python_re_universal_public_oracle_stage08.py"
)
FROZEN_STAGE08_SOURCE_SHA256 = (
    "10464ca347e6eab248a2887a6fd0625cff63497173024616ca8338af0801b0aa"
)
FROZEN_STAGE08_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V8.md"
)
FROZEN_STAGE08_PROTOCOL_SHA256 = (
    "502f300e8ffbd33cf3cbbf6fde7e9cb5e81ed3f87f83634f47068015cdd9dbdd"
)
FROZEN_STAGE08_SELF_ORACLE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-contract-v8-self-oracle.json"
)
FROZEN_STAGE08_SELF_ORACLE_SHA256 = (
    "efcf0f661363e9032ce8c0afe7ea06a4762b783eec4c4ee6ec7c7059c14994df"
)
FROZEN_STAGE08_RUST_FAILURE_RELATIVE = (
    "candidates/evidence/python-re-universal-public-oracle-v8-rust-failures.json"
)
FROZEN_STAGE08_RUST_FAILURE_SHA256 = (
    "f509cedf5f58d1c211b63177fb843bfba3dc0b132469a392df43a9c802e323b1"
)
MATRIX_SHA256 = (
    "0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db"
)

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import python_re_universal_public_oracle_stage08 as previous


stage07 = previous.stage07
stage06 = previous.stage06
frozen = previous.frozen
official_locale = previous.official_locale
canonical = previous.canonical
digest = previous.digest
frozen.candidate_free()
frozen.require(
    Path(previous.__file__).resolve() == ROOT / FROZEN_STAGE08_SOURCE_RELATIVE
    and previous.FROZEN_STAGE07_SOURCE_SHA256
    == "150abcfc597658f48d64c04053889bd4b299c75ad7413bc1cafa5f864e9e7c25"
    and previous.FROZEN_STAGE07_PROTOCOL_SHA256
    == "b4d719609179dde5f582695393539e7a320c09438e4bc635ca843627ac9d7524"
    and previous.FROZEN_STAGE07_FAILURE_SHA256
    == "765e635745a7e332a1bd22426065c43fd52036d013add0d88d840d8fde1121e0"
    and previous.REQUIRED_CANDIDATES == REQUIRED_CANDIDATES
    and previous.MATRIX_SHA256 == MATRIX_SHA256
    and stage07.EXPECTED_CASES == 3_584
    and len(stage07.COHORTS) == 8,
    "stage-10 substituted a frozen source, actual failure, family, or public matrix",
)

WORKER_BOOTSTRAP = (
    "import sys;"
    "sys.path.insert(0,sys.argv[1]);"
    "from tools.python_re_universal_public_oracle_stage10 "
    "import _worker_entry;"
    "raise SystemExit(_worker_entry(sys.argv[2],sys.argv[3]))"
)

_FROZEN_STAGE07_WORKER_REPORT = stage07._worker_report
_FROZEN_STAGE07_SURFACE = stage07._surface_obligation
_FROZEN_STAGE08_AUTHENTICATE = previous._authenticate_current_provenance
_FROZEN_STAGE07_RUN_WORKER = stage07._run_worker
_FROZEN_STAGE07_WORKER_ENVIRONMENT = stage07._worker_environment
_FROZEN_SETPROFILE = sys.setprofile
_FROZEN_SETTRACE = sys.settrace
_FROZEN_GETPROFILE = sys.getprofile
METADATA_SCHEMA = SCHEMA + "-isolated-public-metadata"
METADATA_ENVIRONMENT = "REBAR_PUBLIC_CONTRACT_V10_AUTHENTICATED_METADATA"
MAX_METADATA_BYTES = 96 * 1024
_ACTIVE_METADATA_PAYLOAD: str | None = None
_CHILD_METADATA: dict[str, Any] | None = None
SURFACE_EXPORTS = (
    "compile", "search", "match", "fullmatch", "findall", "finditer",
    "split", "sub", "subn", "escape", "purge", "Pattern", "Match",
    "Scanner", "RegexFlag", "PatternError", "error", "A", "ASCII", "I",
    "IGNORECASE", "L", "LOCALE", "M", "MULTILINE", "S", "DOTALL", "X",
    "VERBOSE", "U", "UNICODE", "DEBUG", "NOFLAG",
)
SURFACE_SIGNATURES = frozenset(
    ("compile", "search", "match", "fullmatch", "findall", "finditer",
     "split", "sub", "subn", "escape", "purge")
)
SURFACE_FLAGS = frozenset(
    ("A", "ASCII", "I", "IGNORECASE", "L", "LOCALE", "M", "MULTILINE",
     "S", "DOTALL", "X", "VERBOSE", "U", "UNICODE", "DEBUG", "NOFLAG")
)
METADATA_WORKER_BOOTSTRAP = (
    "import sys;"
    "sys.path.insert(0,sys.argv[1]);"
    "from tools.python_re_universal_public_oracle_stage10 "
    "import _metadata_worker_entry;"
    "raise SystemExit(_metadata_worker_entry(sys.argv[2],sys.argv[3]))"
)


def _reject_metadata_production(frame: Any, event: str, argument: Any) -> None:
    if event == "call":
        owner = str(frame.f_globals.get("__name__", ""))
        if owner.startswith("candidates."):
            frozen.require(
                frame.f_code.co_name not in SURFACE_SIGNATURES
                and frame.f_code.co_name not in ("scanner", "execute", "run"),
                "the isolated metadata observer attempted candidate matching",
            )
    elif event == "c_call":
        owner = str(getattr(argument, "__module__", ""))
        name = str(getattr(argument, "__name__", ""))
        bound = getattr(argument, "__self__", None)
        bound_owner = str(getattr(type(bound), "__module__", ""))
        caller = frame
        candidate_frame = False
        while caller is not None:
            if str(caller.f_globals.get("__name__", "")).startswith("candidates."):
                candidate_frame = True
                break
            caller = caller.f_back
        if candidate_frame:
            frozen.require(
                argument is not _FROZEN_SETPROFILE
                and argument is not _FROZEN_SETTRACE
                and not (
                    (owner in ("re", "_sre") or bound_owner in ("re", "_sre"))
                    and name in SURFACE_SIGNATURES
                ),
                "isolated metadata rejected candidate regex or profiler tampering",
            )
        if owner.startswith("candidates."):
            frozen.require(
                name not in SURFACE_SIGNATURES
                and name not in ("scanner", "execute", "run", "rebar_zig_compile"),
                "the isolated metadata observer attempted native candidate matching",
            )


def _validate_metadata_report(
    document: Any, *, role: str, source_sha256: str
) -> dict[str, Any]:
    restored = previous._restore_portable(document)
    frozen.require(isinstance(restored, dict), "isolated metadata evidence is invalid")
    required = {
        "schema": METADATA_SCHEMA,
        "status": "PASS",
        "role": role,
        "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "source_sha256": source_sha256,
        "seed": stage07.SEED,
        "seed_domain": stage07.SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "surface_cases": 256,
        "production_matching_executed": False,
        "production_call_profile_enabled": True,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for name, expected in required.items():
        frozen.require(
            restored.get(name) == expected
            and type(restored.get(name)) is type(expected),
            "isolated metadata worker changed " + name,
        )
    records = restored.get("records")
    frozen.require(
        role in REQUIRED_CANDIDATES
        and isinstance(records, list)
        and len(records) == 256
        and all(isinstance(record, dict) for record in records)
        and [record.get("id") for record in records]
        == [f"public-surface:{index:04d}" for index in range(256)]
        and [record.get("index") for record in records] == list(range(256))
        and all(
            record.get("name") == SURFACE_EXPORTS[index % len(SURFACE_EXPORTS)]
            and isinstance(record.get("value"), dict)
            and record["value"].get("name") == record["name"]
            for index, record in enumerate(records)
        )
        and restored.get("record_sha256") == previous.digest(records),
        "isolated metadata concealed, reordered, or substituted a public signature",
    )
    guard = restored.get("guard")
    natives = restored.get("native_binary_sha256")
    expected_modules = {f"candidates.{role}_candidate"}
    if role == "rust":
        expected_modules.add("candidates._rust_bridge")
    elif role == "vm":
        expected_modules.add("candidates._vm_native")
    else:
        expected_modules.add("candidates._zig_bridge")
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
        and guard.get("loaded_candidate_modules") == sorted(expected_modules)
        and isinstance(natives, dict)
        and bool(natives),
        "isolated public metadata weakened the audited candidate-family guard",
    )
    return restored


def _observe_metadata_case(module: Any, index: int) -> dict[str, Any]:
    frozen.require(
        sys.setprofile is _FROZEN_SETPROFILE
        and sys.settrace is _FROZEN_SETTRACE
        and sys.getprofile is _FROZEN_GETPROFILE
        and _FROZEN_GETPROFILE() is _reject_metadata_production,
        "the isolated signature observer lost its production-call monitor",
    )
    value = _FROZEN_STAGE07_SURFACE(module, index)
    frozen.require(
        sys.setprofile is _FROZEN_SETPROFILE
        and sys.settrace is _FROZEN_SETTRACE
        and sys.getprofile is _FROZEN_GETPROFILE
        and _FROZEN_GETPROFILE() is _reject_metadata_production,
        "a candidate disabled the isolated signature production monitor",
    )
    return {
        "id": f"public-surface:{index:04d}",
        "index": index,
        "name": SURFACE_EXPORTS[index % len(SURFACE_EXPORTS)],
        "value": value,
    }


def _metadata_worker_report(role: str, source_sha256: str) -> dict[str, Any]:
    """Inspect signatures only in a separate, production-profiled interpreter."""

    frozen.require(role in REQUIRED_CANDIDATES, "unknown metadata candidate family")
    frozen.candidate_free()
    import inspect as metadata_inspect
    import tokenize as metadata_tokenize

    provenance = _authenticate_current_provenance()
    frozen.require(
        provenance.get("source_sha256") == source_sha256,
        "isolated public metadata changed its pinned stage-10 source",
    )
    natives = provenance["native_sha256_by_family"].get(role)
    frozen.require(
        isinstance(natives, dict) and bool(natives),
        "the metadata candidate has no authenticated native engine",
    )
    guard = stage07._install_family_guard(role, natives)
    frozen.require(
        sys.setprofile is _FROZEN_SETPROFILE
        and sys.settrace is _FROZEN_SETTRACE
        and sys.getprofile is _FROZEN_GETPROFILE,
        "the isolated metadata profiler was replaced before candidate import",
    )
    original_profile = _FROZEN_GETPROFILE()
    try:
        _FROZEN_SETPROFILE(_reject_metadata_production)
        module = importlib.import_module(f"candidates.{role}_candidate")
        mapped = stage07._verify_family_native_mappings(role, provenance)
        loaded = {
            name
            for name, value in sys.modules.items()
            if name.startswith("candidates.")
            and value is not None
            and not isinstance(value, stage07._ForbiddenRegexModule)
        }
        allowed = {f"candidates.{role}_candidate"}
        if role == "rust":
            allowed.add("candidates._rust_bridge")
        elif role == "vm":
            allowed.add("candidates._vm_native")
        else:
            allowed.add("candidates._zig_bridge")
        frozen.require(
            loaded <= allowed,
            "isolated metadata imported a foreign regex candidate family",
        )
        guard["loaded_candidate_modules"] = sorted(loaded)
        records = [_observe_metadata_case(module, index) for index in range(256)]
    finally:
        _FROZEN_SETPROFILE(original_profile)
    frozen.require(
        isinstance(metadata_inspect.re, stage07._ForbiddenRegexModule)
        and isinstance(metadata_tokenize.re, stage07._ForbiddenRegexModule),
        "the isolated metadata process weakened forbidden matcher imports",
    )
    return {
        "schema": METADATA_SCHEMA,
        "status": "PASS",
        "role": role,
        "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "source_sha256": source_sha256,
        "seed": stage07.SEED,
        "seed_domain": stage07.SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "surface_cases": 256,
        "records": records,
        "record_sha256": previous.digest(records),
        "guard": guard,
        "native_binary_sha256": mapped,
        "production_matching_executed": False,
        "production_call_profile_enabled": True,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }


def _metadata_worker_entry(role: str, source_sha256: str) -> int:
    try:
        with _stage10_context():
            document = _metadata_worker_report(role, source_sha256)
            sys.stdout.buffer.write(previous.canonical(document) + b"\n")
            sys.stdout.buffer.flush()
            return 0
    except (Exception, RecursionError) as error:
        failure = {
            "schema": METADATA_SCHEMA,
            "status": "FAIL",
            "role": role,
            "error": stage07._normalize(error),
            "production_matching_executed": False,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }
        sys.stdout.buffer.write(previous.canonical(failure) + b"\n")
        sys.stdout.buffer.flush()
        return 1


def _run_metadata_worker(
    role: str, *, source_sha256: str, locale_root: Path
) -> dict[str, Any]:
    command = [
        str(stage07.PINNED_INTERPRETER),
        "-I",
        "-B",
        "-c",
        METADATA_WORKER_BOOTSTRAP,
        str(ROOT),
        role,
        source_sha256,
    ]
    try:
        child = stage07.subprocess.run(
            command,
            cwd=str(ROOT),
            env=_FROZEN_STAGE07_WORKER_ENVIRONMENT(locale_root),
            stdin=stage07.subprocess.DEVNULL,
            stdout=stage07.subprocess.PIPE,
            stderr=stage07.subprocess.PIPE,
            check=False,
            timeout=600,
        )
    except stage07.subprocess.SubprocessError as error:
        raise stage07.PublicWorkerFailure(
            role,
            "the isolated public metadata worker failed",
            {"kind": type(error).__name__, "exception": stage07._normalize(error)},
        ) from error
    if (
        not 0 < len(child.stdout) <= MAX_METADATA_BYTES
        or len(child.stderr) > stage07.MAX_WORKER_BYTES
    ):
        raise stage07.PublicWorkerFailure(
            role,
            "the isolated public metadata returned empty or excessive evidence",
            {
                "kind": "invalid-isolated-metadata-output",
                "returncode": child.returncode,
                "stdout_bytes": len(child.stdout),
                "stderr": stage07._normalize(child.stderr[:stage07.MAX_WORKER_BYTES]),
            },
        )
    try:
        document = json.loads(child.stdout)
    except (UnicodeError, ValueError) as error:
        raise stage07.PublicWorkerFailure(
            role,
            "the isolated public metadata produced malformed evidence",
            {"kind": "invalid-isolated-metadata-json", "exception": stage07._normalize(error)},
        ) from error
    if child.returncode != 0:
        raise stage07.PublicWorkerFailure(
            role,
            "the isolated public metadata worker rejected its own guard",
            {
                "kind": "isolated-metadata-nonzero-exit",
                "returncode": child.returncode,
                "metadata": document,
                "stderr": stage07._normalize(child.stderr),
            },
        )
    return _validate_metadata_report(document, role=role, source_sha256=source_sha256)


def _worker_environment(locale_root: Path) -> dict[str, str]:
    environment = _FROZEN_STAGE07_WORKER_ENVIRONMENT(locale_root)
    if _ACTIVE_METADATA_PAYLOAD is not None:
        frozen.require(
            len(_ACTIVE_METADATA_PAYLOAD.encode("ascii")) <= MAX_METADATA_BYTES,
            "source-bound public metadata exceeds its bounded transport",
        )
        environment[METADATA_ENVIRONMENT] = _ACTIVE_METADATA_PAYLOAD
    return environment


def _surface_obligation(module: Any, index: int) -> Any:
    """Recompute every public attribute; source only its real isolated signature."""

    if _CHILD_METADATA is None:
        return _FROZEN_STAGE07_SURFACE(module, index)
    role = _CHILD_METADATA["role"]
    frozen.require(
        getattr(module, "__name__", None) == f"candidates.{role}_candidate"
        and type(index) is int
        and 0 <= index < 256,
        "the guarded matcher substituted its authenticated public candidate",
    )
    metadata = _CHILD_METADATA["records"][index]
    name = SURFACE_EXPORTS[index % len(SURFACE_EXPORTS)]
    frozen.require(
        metadata.get("id") == f"public-surface:{index:04d}"
        and metadata.get("index") == index
        and metadata.get("name") == name,
        "the guarded matcher substituted an independently observed surface case",
    )
    present = hasattr(module, name)
    if not present:
        result: dict[str, Any] = {"name": name, "present": False}
    else:
        item = getattr(module, name)
        result = {"name": name, "present": True}
        if name in SURFACE_FLAGS:
            result.update(value=int(item), representation=repr(item))
        elif name in SURFACE_SIGNATURES:
            observed_signature = metadata["value"].get("signature")
            frozen.require(
                type(observed_signature) is str,
                "the isolated observer omitted a genuine callable signature",
            )
            result["signature"] = observed_signature
        elif name == "error":
            result["is_pattern_error"] = item is getattr(module, "PatternError", item)
        elif name in ("Pattern", "Match", "RegexFlag", "PatternError", "Scanner"):
            result["class_name"] = item.__name__
        if index % 3 == 0 and hasattr(module, "__all__"):
            result["listed"] = name in module.__all__
    frozen.require(
        result == metadata.get("value"),
        "the independent metadata and strict matching processes disagree",
    )
    return result


def _worker_report(role: str, source_sha256: str) -> dict[str, Any]:
    if role in ("stdlib-a", "stdlib-b"):
        frozen.require(
            _CHILD_METADATA is None,
            "an independent Python reference received candidate metadata",
        )
        return _FROZEN_STAGE07_WORKER_REPORT(role, source_sha256)
    frozen.require(
        role in REQUIRED_CANDIDATES
        and isinstance(_CHILD_METADATA, dict)
        and _CHILD_METADATA.get("role") == role
        and "inspect" not in sys.modules
        and "tokenize" not in sys.modules,
        "a strict matching worker contains metadata, tokenizer, or a foreign role",
    )
    report = _FROZEN_STAGE07_WORKER_REPORT(role, source_sha256)
    frozen.require(
        "inspect" not in sys.modules and "tokenize" not in sys.modules,
        "candidate production matching imported the Python metadata inspector",
    )
    verified_metadata = _validate_metadata_report(
        _CHILD_METADATA, role=role, source_sha256=source_sha256
    )
    guard = report.get("guard")
    frozen.require(
        isinstance(guard, dict)
        and guard.get("native_loader_aliases_blocked")
        == list(stage07.NATIVE_LOADER_ALIASES)
        and report.get("native_binary_sha256")
        == verified_metadata.get("native_binary_sha256"),
        "isolated metadata does not describe the actual guarded native matcher",
    )
    guard["isolated_public_metadata"] = {
        "enabled": True,
        "schema": METADATA_SCHEMA,
        "source_sha256": source_sha256,
        "role": role,
        "surface_cases": 256,
        "record_sha256": verified_metadata["record_sha256"],
        "production_matching_executed": False,
        "metadata_and_matcher_processes_distinct": True,
        "matcher_inspect_loaded": False,
        "matcher_tokenizer_loaded": False,
    }
    return report


def _run_worker(
    role: str, *, source_sha256: str, locale_root: Path
) -> dict[str, Any]:
    global _ACTIVE_METADATA_PAYLOAD

    if role in ("stdlib-a", "stdlib-b"):
        frozen.require(_ACTIVE_METADATA_PAYLOAD is None, "baseline metadata was substituted")
        return _FROZEN_STAGE07_RUN_WORKER(
            role, source_sha256=source_sha256, locale_root=locale_root
        )
    frozen.require(
        role in REQUIRED_CANDIDATES and _ACTIVE_METADATA_PAYLOAD is None,
        "an isolated metadata role was omitted or recursively activated",
    )
    metadata = _run_metadata_worker(
        role, source_sha256=source_sha256, locale_root=locale_root
    )
    payload = previous.canonical(metadata).decode("ascii")
    frozen.require(
        len(payload.encode("ascii")) <= MAX_METADATA_BYTES,
        "authenticated public metadata exceeds the safe process boundary",
    )
    _ACTIVE_METADATA_PAYLOAD = payload
    try:
        worker = _FROZEN_STAGE07_RUN_WORKER(
            role, source_sha256=source_sha256, locale_root=locale_root
        )
    finally:
        _ACTIVE_METADATA_PAYLOAD = None
    guard = worker.get("guard")
    frozen.require(
        isinstance(guard, dict)
        and isinstance(guard.get("isolated_public_metadata"), dict)
        and guard["isolated_public_metadata"].get("record_sha256")
        == metadata["record_sha256"],
        "the strict candidate worker did not consume its own metadata receipt",
    )
    return worker


def _validate_preserved_v8_self(document: Any) -> dict[str, Any]:
    """Validate every real, strictly encoded historical reference record."""

    restored = previous._restore_portable(document)
    frozen.require(isinstance(restored, dict), "the frozen stage-08 self-oracle is invalid")
    required = {
        "schema": "rebar-python-re-public-contract-v8-self-oracle",
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": FROZEN_STAGE08_SOURCE_RELATIVE,
        "source_sha256": FROZEN_STAGE08_SOURCE_SHA256,
        "protocol_path": FROZEN_STAGE08_PROTOCOL_RELATIVE,
        "protocol_sha256": FROZEN_STAGE08_PROTOCOL_SHA256,
        "seed": stage07.SEED,
        "seed_domain": stage07.SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": 8,
        "cases": 3_584,
        "stdlib_checks": 7_168,
        "mismatches": 0,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for name, expected in required.items():
        frozen.require(
            restored.get(name) == expected
            and type(restored.get(name)) is type(expected),
            "stage-10 rejected a substituted actual stage-08 self-oracle: " + name,
        )
    records = restored.get("baseline_records")
    frozen.require(
        isinstance(records, list)
        and len(records) == stage07.EXPECTED_CASES
        and all(isinstance(record, dict) for record in records)
        and [record.get("id") for record in records]
        == [row["id"] for row in stage07.build_matrix()]
        and restored.get("baseline_record_sha256") == previous.digest(records)
        and restored.get("second_record_sha256") == previous.digest(records)
        and restored.get("failure_records") == []
        and restored.get("cohort_cases")
        == {name: count for name, _operation, count in stage07.COHORTS}
        and restored.get("independent_stdlib_roles") == ["stdlib-a", "stdlib-b"],
        "stage-10 omitted or substituted a genuine stage-08 Python observation",
    )
    provenance = restored.get("current_provenance")
    frozen.require(
        isinstance(provenance, dict)
        and provenance.get("source_path") == FROZEN_STAGE08_SOURCE_RELATIVE
        and provenance.get("source_sha256") == FROZEN_STAGE08_SOURCE_SHA256
        and provenance.get("protocol_path") == FROZEN_STAGE08_PROTOCOL_RELATIVE
        and provenance.get("protocol_sha256") == FROZEN_STAGE08_PROTOCOL_SHA256
        and provenance.get("observation_domain")
        == "rebar/python-re/public-contract/v8"
        and provenance.get("previous_self_oracle_failure_sha256")
        == previous.FROZEN_STAGE07_FAILURE_SHA256
        and provenance.get("previous_self_oracle_failure_count") == 32
        and provenance.get("previous_hash_nondeterminism_only") is True
        and provenance.get("previous_public_comparisons") == 1_179_648
        and provenance.get("official_methods_per_role") == 146
        and provenance.get("official_role_count") == 4
        and provenance.get("official_skipped") == 0,
        "stage-10 rejected unauthenticated historical Python or locale provenance",
    )
    return restored


def _validate_preserved_v8_rust_failure(
    document: Any, historical_self: dict[str, Any]
) -> dict[str, Any]:
    """Reconstruct all archived results without disguising the Rust failure."""

    restored = previous._restore_portable(document)
    frozen.require(isinstance(restored, dict), "the genuine stage-08 Rust failure is invalid")
    required = {
        "schema": "rebar-python-re-public-contract-v8-all-candidates-failure",
        "status": "FAIL",
        "result": "FAIL",
        "candidate": "rust",
        "module": "candidates.rust_candidate",
        "source_path": FROZEN_STAGE08_SOURCE_RELATIVE,
        "source_sha256": FROZEN_STAGE08_SOURCE_SHA256,
        "protocol_path": FROZEN_STAGE08_PROTOCOL_RELATIVE,
        "protocol_sha256": FROZEN_STAGE08_PROTOCOL_SHA256,
        "seed": stage07.SEED,
        "seed_domain": stage07.SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": 8,
        "cases": 3_584,
        "mismatches": 256,
        "failures_recorded": 256,
        "self_oracle_path": FROZEN_STAGE08_SELF_ORACLE_RELATIVE,
        "self_oracle_sha256": FROZEN_STAGE08_SELF_ORACLE_SHA256,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for name, expected in required.items():
        frozen.require(
            restored.get(name) == expected
            and type(restored.get(name)) is type(expected),
            "stage-10 rejected a concealed stage-08 Rust failure: " + name,
        )
    baseline = restored.get("baseline_records")
    candidate = restored.get("candidate_records")
    failures = restored.get("failure_records")
    identities = [row["id"] for row in stage07.build_matrix()]
    frozen.require(
        isinstance(baseline, list)
        and isinstance(candidate, list)
        and isinstance(failures, list)
        and len(baseline) == len(candidate) == 3_584
        and len(failures) == 256
        and all(isinstance(record, dict) for record in baseline)
        and all(isinstance(record, dict) for record in candidate)
        and [record.get("id") for record in baseline] == identities
        and [record.get("id") for record in candidate] == identities
        and baseline == historical_self["baseline_records"]
        and restored.get("baseline_record_sha256") == previous.digest(baseline)
        and restored.get("candidate_record_sha256") == previous.digest(candidate),
        "stage-10 cannot omit any of the 3,584 real Rust or Python observations",
    )
    actual = [
        {"id": left["id"], "expected": left, "actual": right}
        for left, right in zip(baseline, candidate, strict=True)
        if left != right
    ]
    frozen.require(
        len(actual) == 256
        and failures == actual
        and [failure["id"] for failure in failures]
        == [f"public-surface:{index:04d}" for index in range(256)],
        "stage-10 hid, reordered, or fabricated a genuine public-surface failure",
    )
    for failure in failures:
        expected = failure["expected"]
        observed = failure["actual"]
        exception = observed.get("exception")
        arguments = exception.get("args") if isinstance(exception, dict) else None
        frozen.require(
            expected.get("status") == "returned"
            and expected.get("cohort") == "public-surface"
            and observed.get("cohort") == "public-surface"
            and observed.get("status") == "raised"
            and isinstance(exception, dict)
            and exception.get("type") == "ImportError"
            and exception.get("msg")
            == "stage-07 blocked unowned matching import: re"
            and isinstance(arguments, dict)
            and arguments.get("type") == "tuple"
            and arguments.get("items")
            == ["stage-07 blocked unowned matching import: re"],
            "stage-10 misidentified the genuine harness-only metadata failure",
        )
    guard = restored.get("guard")
    natives = restored.get("native_binary_sha256")
    completed = restored.get("completed_candidate_reports")
    frozen.require(
        isinstance(guard, dict)
        and guard.get("enabled") is True
        and guard.get("family") == "rust"
        and guard.get("stdlib_re_blocked") is True
        and guard.get("cpython_sre_blocked") is True
        and guard.get("third_party_regex_blocked") is True
        and guard.get("cross_family_blocked") is True
        and guard.get("foreign_dynamic_libraries_blocked") is True
        and guard.get("native_loader_aliases_blocked")
        == list(stage07.NATIVE_LOADER_ALIASES)
        and guard.get("loaded_candidate_modules")
        == ["candidates._rust_bridge", "candidates.rust_candidate"]
        and isinstance(natives, dict)
        and set(natives)
        == {
            "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
            "candidates/_rust_engine.so",
        }
        and isinstance(completed, dict)
        and set(completed) == {"rust"}
        and completed["rust"].get("status") == "FAIL"
        and completed["rust"].get("cases") == 3_584
        and completed["rust"].get("mismatches") == 256
        and completed["rust"].get("failure_records") == failures
        and completed["rust"].get("native_binary_sha256") == natives
        and completed["rust"].get("guard") == guard
        and restored.get("current_provenance")
        == historical_self.get("current_provenance")
        and restored.get("locales") == historical_self.get("locales")
        and restored.get("cohort_cases")
        == historical_self.get("cohort_cases"),
        "stage-10 weakened the real Rust native, locality, isolation, or failure proof",
    )
    return restored


def _authenticate_current_provenance() -> dict[str, Any]:
    """Pin V10 to both complete V8 experiments and the immutable V7 failure."""

    provenance = _FROZEN_STAGE08_AUTHENTICATE()
    for relative, expected in (
        (FROZEN_STAGE08_SOURCE_RELATIVE, FROZEN_STAGE08_SOURCE_SHA256),
        (FROZEN_STAGE08_PROTOCOL_RELATIVE, FROZEN_STAGE08_PROTOCOL_SHA256),
    ):
        source = official_locale.checked_repo_path(relative)
        frozen.require(
            official_locale.sha256_path(source, maximum=frozen.MAX_SOURCE_BYTES)
            == expected,
            "stage-10 cannot modify frozen stage-08 source or protocol",
        )
    historical_self, self_sha256 = stage06._read_public_document(
        FROZEN_STAGE08_SELF_ORACLE_RELATIVE,
        expected_sha256=FROZEN_STAGE08_SELF_ORACLE_SHA256,
    )
    validated_self = _validate_preserved_v8_self(historical_self)
    rust_failure, failure_sha256 = stage06._read_public_document(
        FROZEN_STAGE08_RUST_FAILURE_RELATIVE,
        expected_sha256=FROZEN_STAGE08_RUST_FAILURE_SHA256,
    )
    _validate_preserved_v8_rust_failure(rust_failure, validated_self)
    frozen.require(
        self_sha256 == FROZEN_STAGE08_SELF_ORACLE_SHA256
        and failure_sha256 == FROZEN_STAGE08_RUST_FAILURE_SHA256,
        "stage-10 substituted actual pinned Python or failed Rust evidence",
    )
    frozen.candidate_free()
    return {
        **provenance,
        "observation_domain": OBSERVATION_DOMAIN,
        "previous_stage08_source_path": FROZEN_STAGE08_SOURCE_RELATIVE,
        "previous_stage08_source_sha256": FROZEN_STAGE08_SOURCE_SHA256,
        "previous_stage08_protocol_path": FROZEN_STAGE08_PROTOCOL_RELATIVE,
        "previous_stage08_protocol_sha256": FROZEN_STAGE08_PROTOCOL_SHA256,
        "previous_stage08_self_oracle_path": FROZEN_STAGE08_SELF_ORACLE_RELATIVE,
        "previous_stage08_self_oracle_sha256": FROZEN_STAGE08_SELF_ORACLE_SHA256,
        "previous_stage08_rust_failure_path": FROZEN_STAGE08_RUST_FAILURE_RELATIVE,
        "previous_stage08_rust_failure_sha256": FROZEN_STAGE08_RUST_FAILURE_SHA256,
        "previous_stage08_rust_failure_count": 256,
        "previous_stage08_rust_matching_observations": 3_328,
        "previous_stage08_rust_failure_preserved": True,
    }


@contextmanager
def _stage10_context() -> Iterator[None]:
    """Retain V8's strict codec and V7 engine guard in every V10 process."""

    with previous._stage08_context():
        updates = {
            "SOURCE_RELATIVE": SOURCE_RELATIVE,
            "PROTOCOL_RELATIVE": PROTOCOL_RELATIVE,
            "SCHEMA": SCHEMA,
            "SELF_TEST_SCHEMA": SELF_TEST_SCHEMA,
            "SELF_ORACLE_SCHEMA": SELF_ORACLE_SCHEMA,
            "ALL_CANDIDATE_SCHEMA": ALL_CANDIDATE_SCHEMA,
            "SELF_ORACLE_RELATIVE": SELF_ORACLE_RELATIVE,
            "SELF_ORACLE_FAILURE_RELATIVE": SELF_ORACLE_FAILURE_RELATIVE,
            "ALL_CANDIDATE_RELATIVE": ALL_CANDIDATE_RELATIVE,
            "CANDIDATE_FAILURE_RELATIVES": CANDIDATE_FAILURE_RELATIVES,
            "WORKER_BOOTSTRAP": WORKER_BOOTSTRAP,
            "_authenticate_current_provenance": _authenticate_current_provenance,
            "_worker_report": _worker_report,
            "_run_worker": _run_worker,
            "_worker_environment": _worker_environment,
            "_surface_obligation": _surface_obligation,
        }
        originals = {name: getattr(stage07, name) for name in updates}
        try:
            for name, value in updates.items():
                setattr(stage07, name, value)
            yield
        finally:
            for name, value in originals.items():
                setattr(stage07, name, value)


def _worker_entry(role: str, source_sha256: str) -> int:
    global _CHILD_METADATA

    with _stage10_context():
        provenance = _authenticate_current_provenance()
        frozen.require(
            provenance.get("source_sha256") == source_sha256,
            "the independent stage-10 child substituted its frozen source",
        )
        payload = os.environ.pop(METADATA_ENVIRONMENT, None)
        if role in REQUIRED_CANDIDATES:
            frozen.require(
                isinstance(payload, str)
                and 0 < len(payload.encode("ascii")) <= MAX_METADATA_BYTES
                and "inspect" not in sys.modules
                and "tokenize" not in sys.modules,
                "the strict matcher has no isolated source-bound public metadata",
            )
            try:
                decoded = json.loads(payload)
            except (UnicodeError, ValueError) as error:
                raise frozen.OracleIntegrityError(
                    "the strict matcher rejected malformed isolated public metadata"
                ) from error
            _CHILD_METADATA = _validate_metadata_report(
                decoded, role=role, source_sha256=source_sha256
            )
            frozen.require(
                _CHILD_METADATA["native_binary_sha256"]
                == provenance["native_sha256_by_family"].get(role),
                "isolated metadata substituted a different audited native engine",
            )
        else:
            frozen.require(
                payload is None and _CHILD_METADATA is None,
                "a standard Python reference received candidate metadata",
            )
        try:
            return stage07._worker_entry(role, source_sha256)
        finally:
            _CHILD_METADATA = None


def run_self_oracle() -> dict[str, Any]:
    with _stage10_context():
        return stage07.run_self_oracle()


def run_all_candidates() -> dict[str, Any]:
    with _stage10_context():
        return stage07.run_all_candidates()


def _synthetic_archives(
    matrix: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build complete surrogate-bearing historical experiments in memory."""

    records: list[dict[str, Any]] = []
    candidate: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for row in matrix:
        sample: Any = None
        if row["cohort"] == "bounded-unicode":
            if row["index"] % 16 == 10:
                sample = "\ud800"
            elif row["index"] % 16 == 11:
                sample = "\udfff"
        expected = {
            "id": row["id"],
            "cohort": row["cohort"],
            "status": "returned",
            "value": sample,
            "warnings": [],
        }
        records.append(expected)
        if row["cohort"] == "public-surface":
            observed = {
                "id": row["id"],
                "cohort": row["cohort"],
                "status": "raised",
                "exception": {
                    "type": "ImportError",
                    "msg": "stage-07 blocked unowned matching import: re",
                    "args": {
                        "type": "tuple",
                        "items": ["stage-07 blocked unowned matching import: re"],
                    },
                },
                "warnings": [],
            }
            failures.append(
                {"id": row["id"], "expected": expected, "actual": observed}
            )
        else:
            observed = expected
        candidate.append(observed)
    cohort_cases = {name: count for name, _operation, count in stage07.COHORTS}
    natives = {
        "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so": (
            "81fc4c4a92005f0588dd9b811988587d4d421dd8e1102eebcab53f4deb27cd36"
        ),
        "candidates/_rust_engine.so": (
            "d590300720215718782227dd8da1192047b4781bdb41ed94446cac06ba880e84"
        ),
    }
    provenance = {
        "source_path": FROZEN_STAGE08_SOURCE_RELATIVE,
        "source_sha256": FROZEN_STAGE08_SOURCE_SHA256,
        "protocol_path": FROZEN_STAGE08_PROTOCOL_RELATIVE,
        "protocol_sha256": FROZEN_STAGE08_PROTOCOL_SHA256,
        "observation_domain": "rebar/python-re/public-contract/v8",
        "previous_self_oracle_failure_sha256": (
            previous.FROZEN_STAGE07_FAILURE_SHA256
        ),
        "previous_self_oracle_failure_count": 32,
        "previous_hash_nondeterminism_only": True,
        "previous_public_comparisons": 1_179_648,
        "official_methods_per_role": 146,
        "official_role_count": 4,
        "official_skipped": 0,
        "native_sha256_by_family": {"rust": natives},
    }
    locales = {"synthetic_archive_only": True}
    archived_self = {
        "schema": "rebar-python-re-public-contract-v8-self-oracle",
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": FROZEN_STAGE08_SOURCE_RELATIVE,
        "source_sha256": FROZEN_STAGE08_SOURCE_SHA256,
        "protocol_path": FROZEN_STAGE08_PROTOCOL_RELATIVE,
        "protocol_sha256": FROZEN_STAGE08_PROTOCOL_SHA256,
        "seed": stage07.SEED,
        "seed_domain": stage07.SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": 8,
        "cohort_cases": cohort_cases,
        "cases": 3_584,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "stdlib_checks": 7_168,
        "baseline_record_sha256": previous.digest(records),
        "second_record_sha256": previous.digest(records),
        "baseline_records": records,
        "mismatches": 0,
        "failure_records": [],
        "current_provenance": provenance,
        "locales": locales,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    guard = {
        "enabled": True,
        "family": "rust",
        "stdlib_re_blocked": True,
        "cpython_sre_blocked": True,
        "third_party_regex_blocked": True,
        "cross_family_blocked": True,
        "foreign_dynamic_libraries_blocked": True,
        "native_loader_aliases_blocked": list(stage07.NATIVE_LOADER_ALIASES),
        "loaded_candidate_modules": [
            "candidates._rust_bridge",
            "candidates.rust_candidate",
        ],
    }
    completed = {
        "candidate": "rust",
        "module": "candidates.rust_candidate",
        "status": "FAIL",
        "cases": 3_584,
        "mismatches": 256,
        "failure_records": failures,
        "failures_recorded": 256,
        "native_binary_sha256": natives,
        "guard": guard,
    }
    archived_failure = {
        "schema": "rebar-python-re-public-contract-v8-all-candidates-failure",
        "status": "FAIL",
        "result": "FAIL",
        "candidate": "rust",
        "module": "candidates.rust_candidate",
        "source_path": FROZEN_STAGE08_SOURCE_RELATIVE,
        "source_sha256": FROZEN_STAGE08_SOURCE_SHA256,
        "protocol_path": FROZEN_STAGE08_PROTOCOL_RELATIVE,
        "protocol_sha256": FROZEN_STAGE08_PROTOCOL_SHA256,
        "seed": stage07.SEED,
        "seed_domain": stage07.SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": 8,
        "cohort_cases": cohort_cases,
        "cases": 3_584,
        "self_oracle_path": FROZEN_STAGE08_SELF_ORACLE_RELATIVE,
        "self_oracle_sha256": FROZEN_STAGE08_SELF_ORACLE_SHA256,
        "baseline_record_sha256": previous.digest(records),
        "candidate_record_sha256": previous.digest(candidate),
        "baseline_records": records,
        "candidate_records": candidate,
        "mismatches": 256,
        "failure_records": failures,
        "failures_recorded": 256,
        "completed_candidate_reports": {"rust": completed},
        "current_provenance": provenance,
        "locales": locales,
        "native_binary_sha256": natives,
        "guard": guard,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    return archived_self, archived_failure


def _synthetic_metadata(
    matrix: list[dict[str, Any]], *, role: str, source_sha256: str
) -> tuple[dict[str, Any], types.ModuleType]:
    """Produce metadata-only in-memory fixtures without imports or workers."""

    module = types.ModuleType(f"candidates.{role}_candidate")

    def synthetic_compile(pattern, flags=0):
        return pattern, flags

    def synthetic_split(pattern, string, *args, **kwargs):
        return pattern, string, args, kwargs

    def synthetic_sub(pattern, repl, string, *args, **kwargs):
        return pattern, repl, string, args, kwargs

    def synthetic_subn(pattern, repl, string, *args, **kwargs):
        return pattern, repl, string, args, kwargs

    module.compile = synthetic_compile
    module.split = synthetic_split
    module.sub = synthetic_sub
    module.subn = synthetic_subn
    module.__all__ = ["compile", "split", "sub", "subn"]
    signatures = {
        "compile": "(pattern, flags=0)",
        "split": "(pattern, string, maxsplit=0, flags=0)",
        "sub": "(pattern, repl, string, count=0, flags=0)",
        "subn": "(pattern, repl, string, count=0, flags=0)",
    }
    rows: list[dict[str, Any]] = []
    for index in range(256):
        name = SURFACE_EXPORTS[index % len(SURFACE_EXPORTS)]
        present = hasattr(module, name)
        value: dict[str, Any] = {"name": name, "present": present}
        if present:
            if name in SURFACE_SIGNATURES:
                value["signature"] = signatures[name]
            if index % 3 == 0:
                value["listed"] = name in module.__all__
        rows.append(
            {
                "id": f"public-surface:{index:04d}",
                "index": index,
                "name": name,
                "value": value,
            }
        )
    allowed = {
        "rust": ["candidates._rust_bridge", "candidates.rust_candidate"],
        "vm": ["candidates._vm_native", "candidates.vm_candidate"],
        "zig": ["candidates._zig_bridge", "candidates.zig_candidate"],
    }
    guard = {
        "enabled": True,
        "family": role,
        "stdlib_re_blocked": True,
        "cpython_sre_blocked": True,
        "third_party_regex_blocked": True,
        "cross_family_blocked": True,
        "foreign_dynamic_libraries_blocked": True,
        "native_loader_aliases_blocked": list(stage07.NATIVE_LOADER_ALIASES),
        "loaded_candidate_modules": allowed[role],
    }
    return {
        "schema": METADATA_SCHEMA,
        "status": "PASS",
        "role": role,
        "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "source_sha256": source_sha256,
        "seed": stage07.SEED,
        "seed_domain": stage07.SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "surface_cases": 256,
        "records": rows,
        "record_sha256": previous.digest(rows),
        "guard": guard,
        "native_binary_sha256": {
            f"candidates/_synthetic_{role}_native.so": "a" * 64
        },
        "production_matching_executed": False,
        "production_call_profile_enabled": True,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }, module


def self_test() -> dict[str, Any]:
    """Test strict process separation in memory; never execute either worker."""

    global _CHILD_METADATA

    frozen.candidate_free()
    with stage06.previous._candidate_free_file_and_timing_guard() as effects:
        inherited = previous.self_test()
        frozen.require(
            inherited.get("stage") == "stage08"
            and inherited.get("status") == "PASS"
            and inherited.get("check_count", 0) >= 597
            and inherited.get("candidate_imports") == 0
            and inherited.get("candidate_processes") == 0
            and inherited.get("files_read") == 0
            and inherited.get("files_written") == 0
            and inherited.get("benchmark_or_timing_executed") is False
            and inherited.get("performance_fixtures_read") == 0
            and inherited.get("holdout_cases_read") == 0,
            "stage-10 weakened an inherited candidate-free phase-one control",
        )
        stage07.gc.collect()
        checks = list(inherited["checks"])

        def check(name: str, condition: Any) -> None:
            frozen.require(condition, "stage-10 synthetic control failed: " + name)
            checks.append({"name": name, "passed": True})

        def reject(name: str, action: Callable[[], Any]) -> None:
            try:
                action()
            except (
                frozen.OracleIntegrityError,
                AssertionError,
                AttributeError,
                ImportError,
                KeyError,
                TypeError,
                UnicodeError,
                ValueError,
            ):
                check(name, True)
            else:
                check(name, False)

        matrix = stage07.build_matrix()
        check(
            "stage10-preserves-all-3584-original-public-obligations",
            len(matrix) == 3_584 and previous.digest(matrix) == MATRIX_SHA256,
        )
        check(
            "stage10-preserves-the-exact-original-public-seed-domain",
            stage07.SEED == 2026072437
            and stage07.SEED_DOMAIN == "rebar/python-re/public-contract/v7",
        )
        check(
            "stage10-preserves-all-33-real-cpython-public-exports",
            len(SURFACE_EXPORTS) == 33,
        )
        for name, _operation, count in stage07.COHORTS:
            check(
                "stage10-preserves-exact-public-cohort-" + name,
                sum(row["cohort"] == name for row in matrix) == count,
            )
        check(
            "stage10-keeps-inspect-out-of-production-source-globals",
            "inspect" not in globals(),
        )
        check(
            "stage10-keeps-tokenize-out-of-production-source-globals",
            "tokenize" not in globals(),
        )
        check(
            "stage10-publishes-no-regex-proxy-or-owner-capability",
            not any(
                item in globals()
                for item in (
                    "inspect", "tokenize", "_ObserverOnlyPattern",
                    "_FROZEN_COOKIE_PATTERN", "_FROZEN_BLANK_PATTERN",
                    "_OBSERVER_STATE", "_metadata_observer", "_trusted_signature",
                    "_private_token_patterns",
                )
            ),
        )
        check(
            "stage10-isolates-metadata-and-matching-bootstrap-processes",
            METADATA_WORKER_BOOTSTRAP != WORKER_BOOTSTRAP
            and "_metadata_worker_entry" in METADATA_WORKER_BOOTSTRAP
            and "_worker_entry" in WORKER_BOOTSTRAP,
        )
        check(
            "stage10-retains-all-five-real-foreign-library-denials",
            stage07.NATIVE_LOADER_ALIASES
            == (
                "ctypes.CDLL", "ctypes.cdll.LoadLibrary",
                "ctypes.cdll._dlltype", "ctypes._dlopen", "_ctypes.dlopen",
            ),
        )
        check(
            "stage10-freezes-profile-and-trace-controls-before-candidate-import",
            sys.setprofile is _FROZEN_SETPROFILE
            and sys.settrace is _FROZEN_SETTRACE
            and sys.getprofile is _FROZEN_GETPROFILE,
        )

        synthetic_source = "b" * 64
        for family in REQUIRED_CANDIDATES:
            metadata, module = _synthetic_metadata(
                matrix, role=family, source_sha256=synthetic_source
            )
            validated = _validate_metadata_report(
                metadata, role=family, source_sha256=synthetic_source
            )
            check(
                "stage10-validates-all-256-isolated-surface-records-" + family,
                len(validated["records"]) == 256,
            )
            check(
                "stage10-authenticates-isolated-surface-receipt-digest-" + family,
                validated["record_sha256"] == previous.digest(validated["records"]),
            )
            _CHILD_METADATA = validated
            try:
                for index in (0, 6, 7, 8, 16, 25, 32, 33, 127, 255):
                    check(
                        "stage10-recomputes-authenticated-surface-"
                        + family + "-" + f"{index:04d}",
                        _surface_obligation(module, index)
                        == validated["records"][index]["value"],
                    )
                foreign = types.ModuleType("candidates.foreign_candidate")
                reject(
                    "stage10-rejects-foreign-metadata-module-" + family,
                    lambda: _surface_obligation(foreign, 0),
                )
                reject(
                    "stage10-rejects-invalid-metadata-index-" + family,
                    lambda: _surface_obligation(module, 256),
                )
            finally:
                _CHILD_METADATA = None
            for field, poisoned in (
                ("schema", "foreign-schema"),
                ("status", "FAIL"),
                ("role", "foreign"),
                ("source_path", FROZEN_STAGE08_SOURCE_RELATIVE),
                ("source_sha256", "0" * 64),
                ("seed", 0),
                ("seed_domain", OBSERVATION_DOMAIN),
                ("matrix_sha256", "0" * 64),
                ("surface_cases", 255),
                ("record_sha256", "0" * 64),
                ("native_binary_sha256", {}),
                ("production_matching_executed", True),
                ("production_call_profile_enabled", False),
                ("benchmark_or_timing_executed", True),
                ("holdout_cases_read", 1),
            ):
                reject(
                    "stage10-rejects-poisoned-" + family + "-metadata-" + field,
                    lambda field=field, value=poisoned, doc=metadata, role=family: (
                        _validate_metadata_report(
                            {**doc, field: value},
                            role=role,
                            source_sha256=synthetic_source,
                        )
                    ),
                )
            corrupted_guard = {
                **metadata["guard"],
                "loaded_candidate_modules": [f"candidates.{family}_candidate"],
            }
            reject(
                "stage10-rejects-foreign-or-missing-native-metadata-module-" + family,
                lambda doc=metadata, role=family, guard=corrupted_guard: (
                    _validate_metadata_report(
                        {**doc, "guard": guard},
                        role=role,
                        source_sha256=synthetic_source,
                    )
                ),
            )
            changed = list(metadata["records"])
            changed[6] = {
                **changed[6],
                "value": {**changed[6]["value"], "signature": "(fake)"},
            }
            reject(
                "stage10-rejects-edited-real-signature-receipt-" + family,
                lambda rows=changed, doc=metadata, role=family: (
                    _validate_metadata_report(
                        {**doc, "records": rows},
                        role=role,
                        source_sha256=synthetic_source,
                    )
                ),
            )
            duplicate = list(metadata["records"])
            duplicate[-1] = duplicate[0]
            reject(
                "stage10-rejects-duplicated-public-metadata-case-" + family,
                lambda rows=duplicate, doc=metadata, role=family: (
                    _validate_metadata_report(
                        {**doc, "records": rows},
                        role=role,
                        source_sha256=synthetic_source,
                    )
                ),
            )
            reject(
                "stage10-rejects-an-omitted-public-metadata-case-" + family,
                lambda doc=metadata, role=family: _validate_metadata_report(
                    {**doc, "records": doc["records"][:-1]},
                    role=role,
                    source_sha256=synthetic_source,
                ),
            )

        candidate_frame = types.SimpleNamespace(
            f_globals={"__name__": "candidates.stage10_synthetic_attack"},
            f_code=types.SimpleNamespace(co_name="compile"),
            f_back=None,
        )
        helper_frame = types.SimpleNamespace(
            f_globals={"__name__": "candidates.stage10_synthetic_attack"},
            f_code=types.SimpleNamespace(co_name="innocent_helper"),
            f_back=None,
        )
        regex_call = types.SimpleNamespace(
            __module__="re", __name__="match", __self__=None
        )
        native_call = types.SimpleNamespace(
            __module__="candidates._synthetic_bridge",
            __name__="compile",
            __self__=None,
        )
        reject(
            "stage10-profile-rejects-candidate-owned-production-call",
            lambda: _reject_metadata_production(candidate_frame, "call", None),
        )
        reject(
            "stage10-profile-rejects-cached-tokenizer-matcher-in-candidate-helper",
            lambda: _reject_metadata_production(helper_frame, "c_call", regex_call),
        )
        reject(
            "stage10-profile-rejects-native-production-call",
            lambda: _reject_metadata_production(helper_frame, "c_call", native_call),
        )
        reject(
            "stage10-profile-rejects-candidate-profile-disabling",
            lambda: _reject_metadata_production(
                helper_frame, "c_call", _FROZEN_SETPROFILE
            ),
        )
        reject(
            "stage10-profile-rejects-candidate-trace-disabling",
            lambda: _reject_metadata_production(
                helper_frame, "c_call", _FROZEN_SETTRACE
            ),
        )
        trusted_frame = types.SimpleNamespace(
            f_globals={"__name__": "tokenize"},
            f_code=types.SimpleNamespace(co_name="detect_encoding"),
            f_back=None,
        )
        _reject_metadata_production(trusted_frame, "c_call", regex_call)
        check("stage10-profile-preserves-genuine-isolated-cpython-inspection", True)

        historical_self, historical_failure = _synthetic_archives(matrix)
        validated_self = _validate_preserved_v8_self(historical_self)
        _validate_preserved_v8_rust_failure(historical_failure, validated_self)
        check("stage10-authenticates-both-complete-frozen-python-reference-runs", True)
        check("stage10-preserves-all-3584-real-historical-rust-results", True)
        check("stage10-preserves-exactly-3328-real-historical-rust-agreements", True)
        check("stage10-preserves-exactly-256-ordered-real-historical-rust-failures", True)
        check(
            "stage10-preserves-real-historical-unpaired-unicode",
            sum(
                item.get("value") == "\ud800"
                for item in historical_self["baseline_records"]
            ) == 64
            and sum(
                item.get("value") == "\udfff"
                for item in historical_self["baseline_records"]
            ) == 64,
        )
        for field, poisoned in (
            ("schema", "foreign-schema"),
            ("status", "FAIL"),
            ("source_sha256", "0" * 64),
            ("protocol_sha256", "0" * 64),
            ("baseline_record_sha256", "0" * 64),
            ("second_record_sha256", "0" * 64),
            ("mismatches", 1),
            ("cases", 3_583),
        ):
            reject(
                "stage10-rejects-changed-actual-v8-self-oracle-" + field,
                lambda field=field, value=poisoned: _validate_preserved_v8_self(
                    {**historical_self, field: value}
                ),
            )
        for field, poisoned in (
            ("schema", "foreign-schema"),
            ("status", "PASS"),
            ("result", "PASS"),
            ("candidate", "vm"),
            ("module", "candidates.vm_candidate"),
            ("source_sha256", "0" * 64),
            ("protocol_sha256", "0" * 64),
            ("self_oracle_sha256", "0" * 64),
            ("baseline_record_sha256", "0" * 64),
            ("candidate_record_sha256", "0" * 64),
            ("mismatches", 255),
            ("failures_recorded", 255),
        ):
            reject(
                "stage10-rejects-concealed-actual-v8-rust-failure-" + field,
                lambda field=field, value=poisoned: (
                    _validate_preserved_v8_rust_failure(
                        {**historical_failure, field: value}, validated_self
                    )
                ),
            )
        reject(
            "stage10-rejects-an-omitted-actual-rust-failure",
            lambda: _validate_preserved_v8_rust_failure(
                {
                    **historical_failure,
                    "failure_records": historical_failure["failure_records"][:-1],
                },
                validated_self,
            ),
        )
        reject(
            "stage10-rejects-an-omitted-actual-rust-observation",
            lambda: _validate_preserved_v8_rust_failure(
                {
                    **historical_failure,
                    "candidate_records": historical_failure["candidate_records"][:-1],
                },
                validated_self,
            ),
        )

        outputs = (
            SELF_ORACLE_RELATIVE,
            SELF_ORACLE_FAILURE_RELATIVE,
            ALL_CANDIDATE_RELATIVE,
            *CANDIDATE_FAILURE_RELATIVES.values(),
        )
        previous_outputs = (
            previous.SELF_ORACLE_RELATIVE,
            previous.SELF_ORACLE_FAILURE_RELATIVE,
            previous.ALL_CANDIDATE_RELATIVE,
            *previous.CANDIDATE_FAILURE_RELATIVES.values(),
        )
        check(
            "stage10-authorizes-six-new-exclusive-evidence-destinations",
            len(outputs) == len(set(outputs)) == 6
            and not set(outputs).intersection(previous_outputs),
        )
        check(
            "stage10-never-uses-reserved-stage09-or-v9",
            "stage09" not in SOURCE_RELATIVE
            and "V9" not in PROTOCOL_RELATIVE
            and all("-v9-" not in value for value in outputs),
        )
        with _stage10_context():
            check(
                "stage10-binds-independent-source-and-both-real-worker-bootstraps",
                stage07.SOURCE_RELATIVE == SOURCE_RELATIVE
                and stage07.PROTOCOL_RELATIVE == PROTOCOL_RELATIVE
                and stage07.WORKER_BOOTSTRAP == WORKER_BOOTSTRAP
                and METADATA_WORKER_BOOTSTRAP != WORKER_BOOTSTRAP,
            )
            check(
                "stage10-binds-the-independent-metadata-controller",
                stage07._run_worker is _run_worker
                and stage07._worker_environment is _worker_environment
                and stage07._surface_obligation is _surface_obligation,
            )
            check(
                "stage10-preserves-the-strict-v8-unicode-codec-and-frozen-matrix",
                stage07.canonical is previous.canonical
                and stage07.digest is previous.digest
                and stage07.digest(stage07.build_matrix()) == MATRIX_SHA256,
            )
            check(
                "stage10-preserves-the-hardened-original-exclusive-report-writer",
                stage07._exclusive_evidence is previous._FROZEN_EVIDENCE_WRITER,
            )
            inner_self = _validate_preserved_v8_self(historical_self)
            _validate_preserved_v8_rust_failure(historical_failure, inner_self)
            check(
                "stage10-validates-genuine-surrogate-bearing-archives-in-v10-context",
                True,
            )
            for output in outputs:
                check(
                    "stage10-accepts-only-exact-exclusive-" + Path(output).name,
                    stage07.exact_output(output, output) == output,
                )
                for poisoned in (
                    "/" + output,
                    "../" + output,
                    output.replace("/", "//", 1),
                    output + "\x00",
                    next(item for item in outputs if item != output),
                ):
                    reject(
                        "stage10-rejects-foreign-exclusive-"
                        + Path(output).name + "-" + str(len(checks)),
                        lambda path=poisoned, expected=output: (
                            stage07.exact_output(path, expected)
                        ),
                    )
        check(
            "stage10-restores-the-immutable-stage07-oracle-and-workers",
            stage07.SOURCE_RELATIVE == previous.FROZEN_STAGE07_SOURCE_RELATIVE
            and stage07._run_worker is _FROZEN_STAGE07_RUN_WORKER
            and stage07._worker_report is _FROZEN_STAGE07_WORKER_REPORT
            and stage07._surface_obligation is _FROZEN_STAGE07_SURFACE,
        )
        check(
            "stage10-never-starts-an-isolated-metadata-or-candidate-process",
            effects["workers"] == 0,
        )
        check(
            "stage10-never-opens-files-times-work-or-accesses-randomness",
            all(value == 0 for value in effects.values()),
        )
        frozen.candidate_free()
        check("stage10-never-imports-a-production-candidate", True)
        names = [item["name"] for item in checks]
        frozen.require(
            len(names) == len(set(names)) and len(checks) >= 700,
            "stage-10 independent metadata or inherited controls were weakened",
        )
        return {
            "schema": SELF_TEST_SCHEMA,
            "stage": "stage10",
            "status": "PASS",
            "result": "PASS",
            "seed": stage07.SEED,
            "seed_domain": stage07.SEED_DOMAIN,
            "observation_domain": OBSERVATION_DOMAIN,
            "cohorts": len(stage07.COHORTS),
            "cases": stage07.EXPECTED_CASES,
            "matrix_sha256": MATRIX_SHA256,
            "cohort_cases": {
                name: count for name, _operation, count in stage07.COHORTS
            },
            "inherited_stage08_control_count": inherited["check_count"],
            "checks": checks,
            "check_count": len(checks),
            "failed": [],
            "candidate_imports": 0,
            "candidate_processes": 0,
            "metadata_processes": 0,
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
            "previous_stage07_failure_sha256": previous.FROZEN_STAGE07_FAILURE_SHA256,
            "previous_stage07_failure_count": 32,
            "previous_stage08_self_oracle_sha256": FROZEN_STAGE08_SELF_ORACLE_SHA256,
            "previous_stage08_rust_failure_sha256": FROZEN_STAGE08_RUST_FAILURE_SHA256,
            "previous_stage08_rust_failure_count": 256,
            "previous_stage08_rust_matching_observations": 3_328,
            "isolated_surface_cases_per_candidate": 256,
            "matching_worker_imports_inspect": False,
            "matching_worker_imports_tokenize": False,
            "self_oracle_output": SELF_ORACLE_RELATIVE,
            "self_oracle_failure_output": SELF_ORACLE_FAILURE_RELATIVE,
            "all_candidate_output": ALL_CANDIDATE_RELATIVE,
            "candidate_failure_outputs": dict(CANDIDATE_FAILURE_RELATIVES),
            "native_loader_aliases_blocked": list(stage07.NATIVE_LOADER_ALIASES),
        }



def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--self-oracle", action="store_true")
    modes.add_argument("--candidate", choices=("all",))
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            report = self_test()
        elif args.self_oracle:
            report = run_self_oracle()
        else:
            frozen.require(
                args.candidate == "all",
                "all three independently implemented native families are mandatory",
            )
            report = run_all_candidates()
        sys.stdout.buffer.write(canonical(report) + b"\n")
        sys.stdout.buffer.flush()
        return 0
    except (
        frozen.OracleIntegrityError,
        AssertionError,
        OSError,
        ValueError,
        stage07.subprocess.SubprocessError,
    ) as error:
        sys.stderr.buffer.write(
            canonical({"schema": SCHEMA, "status": "FAIL", "error": str(error)})
            + b"\n"
        )
        sys.stderr.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
