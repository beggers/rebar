#!/usr/bin/env python3
"""Prove genuine native ownership without mistaking a guard for an engine."""

from __future__ import annotations

import argparse
import ast
import base64
import copy
import gc
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
from typing import Any, Callable, Mapping


ROOT = Path(__file__).resolve().parent.parent
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

from tools import postfinal_cpython_locale_oracle_v5 as reference_v5
from tools import postfinal_current_build_proofs_v8 as refresh_v8
from tools import postfinal_from_scratch_audit_v5 as source_v5
from tools import postfinal_from_scratch_audit_v6 as source_v6
from tools import postfinal_from_scratch_audit_v8 as original_v8


core = original_v8.core
SCHEMA = "rebar-postfinal-from-scratch-audit-v9"
SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v9.py"
SOURCE_PATH = ROOT / SOURCE_RELATIVE
REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V9.json"
FAILURE_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V9-FAILURES.json"
)
REPORT_PATH = ROOT / REPORT_RELATIVE
FAILURE_PATH = ROOT / FAILURE_RELATIVE
PROTOCOL_RELATIVE = "candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V9.md"
PROTOCOL_SHA256 = (
    "d7946e85be148fa0d141afb4091c03469b4a3d142f587ec01163817a3f7f3219"
)
CORE_FAMILIES = tuple(original_v8.CORE_FAMILIES)
OWNED_NATIVE_MODULES = dict(original_v8.OWNED_NATIVE_MODULES)
OWNED_SOURCE_PATHS = dict(original_v8.OWNED_SOURCE_PATHS)
OWNED_NATIVE_PATHS = dict(original_v8.OWNED_NATIVE_PATHS)
NATIVE_LOADER_ALIASES = tuple(original_v8.NATIVE_LOADER_ALIASES)
PICKLE_PROTOCOLS = tuple(original_v8.PICKLE_PROTOCOLS)
PINNED_EXECUTABLE = original_v8.PINNED_EXECUTABLE
MAX_SOURCE_BYTES = original_v8.MAX_SOURCE_BYTES
MAX_REPORT_BYTES = original_v8.MAX_REPORT_BYTES
MAX_WORKER_BYTES = original_v8.MAX_WORKER_BYTES
V7_EDGE_FAILURES = dict(original_v8.V7_EDGE_FAILURES)
V7_EDGE_EXPECTATIONS = dict(original_v8.V7_EDGE_EXPECTATIONS)
EDGE_SCHEMA = original_v8.EDGE_SCHEMA
EDGE_SEED = original_v8.EDGE_SEED
EDGE_CHECKS = original_v8.EDGE_CHECKS
EDGE_CATEGORIES = original_v8.EDGE_CATEGORIES
EDGE_REFERENCE_SHA256 = original_v8.EDGE_REFERENCE_SHA256
STAGE07_RELATIVE = "tools/python_re_universal_public_oracle_stage07.py"
STAGE07_SHA256 = (
    "150abcfc597658f48d64c04053889bd4b299c75ad7413bc1cafa5f864e9e7c25"
)
V8_BASE_RELATIVE = "tools/postfinal_from_scratch_audit_v8.py"
V8_BASE_SHA256 = (
    "14b8daeebfb620eafa778529f6bf11e1a4f48256dd010b25621f4e94666692c6"
)
V8_STRICT_RELATIVE = "tools/postfinal_no_delegation_audit_v8.py"
V8_STRICT_SHA256 = (
    "bb22b1983c11a896d3639077050dfaac746876ccbb9e4909518fb33d19987c01"
)
V8_PROOF_RELATIVE = "tools/postfinal_current_build_proofs_v8.py"
V8_PROOF_SHA256 = (
    "0f9e12847855797669206ea89de94948da66c29742d64820a625ce5a6570b313"
)
V8_OWNER_FAILURE_RELATIVE = (
    "candidates/evidence/"
    "rust-v7-edge-oracle-rust-postfinal-current-build-v8-"
    "diagnostic-native-owner-failure.json.gz"
)
V8_OWNER_FAILURE_SHA256 = (
    "2f8bfcba726d729865cb8411a25ef1c3e0633e80c70af8895e5875a71f15ed7b"
)
V5_SOURCE_SHA256 = (
    "9a4f2ac53617fb91e498ae2935bde622417921415af255e390668f69ba908730"
)
V5_PROTOCOL_SHA256 = (
    "1329cf9c8e36391af134b2fb2b212e71067ace736b282dacd2a6c90233384840"
)
V5_REFERENCE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v5-self-oracle.json"
)
V5_REFERENCE_SHA256 = (
    "3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916"
)
SENTINEL_FLAGS = (
    "sentinel_type_exact",
    "sys_modules_sentinel_identity",
    "imported_sentinel_identity",
    "before_matching_verified",
    "after_matching_verified",
    "fresh_sentinel_rejected",
    "subclass_sentinel_rejected",
    "same_name_forged_sentinel_rejected",
    "live_module_rejected",
)


class AuditV9Error(source_v6.AuditV6Error):
    """Actual independent native ownership or a genuine matching guard failed."""


class NativeWorkerFailure(AuditV9Error):
    """Retain the entire actual bounded failure without inventing observations."""

    def __init__(self, message: str, evidence: Mapping[str, Any]):
        super().__init__(message)
        self.evidence = dict(evidence)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditV9Error(message)


def verify_runtime() -> None:
    require(
        tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.implementation.name == "cpython"
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and Path(sys.executable).resolve() == PINNED_EXECUTABLE.resolve()
        and bool(sys.path) and sys.path[0] == str(ROOT)
        and Path(__file__).resolve() == SOURCE_PATH.resolve(),
        "the exact directly isolated pinned V9 controller and trusted root are required",
    )


_FOREIGN_OLD = r'''def audit_foreign_engines():
    observations = []
    for forbidden in sorted(foreign):
        try:
            importlib.import_module(forbidden)
        except ImportError:
            observations.append({"module": forbidden, "blocked": True})
            continue
        raise RuntimeError("the V8 native guard admitted an external engine: " + forbidden)
    return observations
'''

_FOREIGN_NEW = r'''def _actual_stage07_sentinel(observed, forbidden):
    return (
        stage07._ForbiddenRegexModule is foreign_poison_type
        and type(observed) is foreign_poison_type
        and observed is foreign_poison
        and sys.modules.get(forbidden) is foreign_poison
    )


def _verify_stage07_sentinel(phase):
    if phase not in ("before", "after"):
        raise RuntimeError("the genuine V9 sentinel phase was substituted")
    if stage07._ForbiddenRegexModule is not foreign_poison_type:
        raise RuntimeError("the genuine Stage 07 poison class was replaced")
    if not _actual_stage07_sentinel(foreign_poison, "candidates.ast_candidate"):
        raise RuntimeError("the genuine Stage 07 cached poison was replaced")
    observed = importlib.import_module("candidates.ast_candidate")
    if not _actual_stage07_sentinel(observed, "candidates.ast_candidate"):
        raise RuntimeError("a real foreign matcher replaced the exact cached poison")

    fresh = foreign_poison_type(foreign_poison.__name__)

    class ForgedPoison(foreign_poison_type):
        pass

    forged_subclass = ForgedPoison(foreign_poison.__name__)
    forged_same_name = types.ModuleType(foreign_poison.__name__)
    live_foreign = types.ModuleType("candidates.ast_candidate")
    fresh_rejected = not _actual_stage07_sentinel(
        fresh, "candidates.ast_candidate",
    )
    subclass_rejected = not _actual_stage07_sentinel(
        forged_subclass, "candidates.ast_candidate",
    )
    same_name_rejected = not _actual_stage07_sentinel(
        forged_same_name, "candidates.ast_candidate",
    )
    live_rejected = not _actual_stage07_sentinel(
        live_foreign, "candidates.ast_candidate",
    )
    if not all((fresh_rejected, subclass_rejected,
                same_name_rejected, live_rejected)):
        raise RuntimeError("a forged Stage 07 guard poison was accepted")
    return {
        "stage07_source_sha256": actual_stage07_source_sha256,
        "sentinel_type_exact": type(foreign_poison) is foreign_poison_type,
        "sys_modules_sentinel_identity": (
            sys.modules.get("candidates.ast_candidate") is foreign_poison
        ),
        "imported_sentinel_identity": observed is foreign_poison,
        "before_matching_verified": True,
        "after_matching_verified": phase == "after",
        "fresh_sentinel_rejected": fresh_rejected,
        "subclass_sentinel_rejected": subclass_rejected,
        "same_name_forged_sentinel_rejected": same_name_rejected,
        "live_module_rejected": live_rejected,
    }


def audit_foreign_engines():
    observations = []
    for forbidden in sorted(foreign):
        try:
            observed = importlib.import_module(forbidden)
        except ImportError:
            observations.append({"module": forbidden, "blocked": True})
            continue
        if _actual_stage07_sentinel(observed, forbidden):
            observations.append({"module": forbidden, "blocked": True})
            continue
        raise RuntimeError("the V9 native guard admitted an external engine: " + forbidden)
    return observations
'''


def _replace_once(source: str, old: str, new: str, label: str) -> str:
    require(source.count(old) == 1,
            "the immutable genuine native worker changed: " + label)
    return source.replace(old, new, 1)


def _build_native_owner_worker() -> str:
    source = original_v8.NATIVE_OWNER_WORKER
    source = _replace_once(
        source, "import inspect\n", "import hashlib\nimport inspect\n",
        "worker hashing import",
    )
    source = _replace_once(
        source,
        "guard = stage07._install_family_guard(role, expected)\n",
        'stage07_path = root / "' + STAGE07_RELATIVE + '"\n'
        'if stage07_path.is_symlink() or not stage07_path.is_file():\n'
        '    raise RuntimeError("the immutable V9 Stage 07 source is unavailable")\n'
        'with open(stage07_path, "rb") as stage07_input:\n'
        '    stage07_bytes = stage07_input.read(1048577)\n'
        'if not stage07_bytes or len(stage07_bytes) > 1048576:\n'
        '    raise RuntimeError("the V9 Stage 07 source exceeded its bound")\n'
        'actual_stage07_source_sha256 = hashlib.sha256(stage07_bytes).hexdigest()\n'
        'if actual_stage07_source_sha256 != "' + STAGE07_SHA256 + '":\n'
        '    raise RuntimeError("the immutable V9 Stage 07 source was replaced")\n'
        'if Path(stage07.__file__).resolve(strict=True) != stage07_path.resolve(strict=True):\n'
        '    raise RuntimeError("an unauthenticated V9 Stage 07 module was loaded")\n'
        'guard = stage07._install_family_guard(role, expected)\n'
        'foreign_poison = sys.modules.get("candidates.ast_candidate")\n'
        'foreign_poison_type = stage07._ForbiddenRegexModule\n'
        'if type(foreign_poison) is not foreign_poison_type:\n'
        '    raise RuntimeError("the actual Stage 07 foreign guard was replaced")\n',
        "immutable real stage07 source and captured exact poison",
    )
    source = _replace_once(
        source, _FOREIGN_OLD, _FOREIGN_NEW,
        "actual exact foreign-engine poison identity",
    )
    source = _replace_once(
        source,
        "foreign_guards_before = audit_foreign_engines()\n",
        'sentinel_before = _verify_stage07_sentinel("before")\n'
        'foreign_guards_before = audit_foreign_engines()\n',
        "actual cached sentinel before native matching",
    )
    source = _replace_once(
        source,
        "foreign_guards_after = audit_foreign_engines()\n",
        'foreign_guards_after = audit_foreign_engines()\n'
        'stage07_guard_sentinel = _verify_stage07_sentinel("after")\n'
        'if any(stage07_guard_sentinel[key] != sentinel_before[key]\n'
        '       for key in sentinel_before if key != "after_matching_verified"):\n'
        '    raise RuntimeError("the exact genuine cached foreign poison changed")\n',
        "actual cached sentinel after native matching",
    )
    source = _replace_once(
        source,
        '"schema": "rebar-postfinal-from-scratch-audit-v8-native-owner-worker",\n',
        '"schema": "rebar-postfinal-from-scratch-audit-v9-native-owner-worker",\n',
        "distinct immutable V9 actual owner-worker schema",
    )
    source = _replace_once(
        source,
        '    "guard": guard,\n',
        '    "guard": guard,\n'
        '    "stage07_guard_sentinel": stage07_guard_sentinel,\n',
        "complete exact before-and-after Stage 07 sentinel evidence",
    )
    return source


NATIVE_OWNER_WORKER = _build_native_owner_worker()
NATIVE_OWNER_WORKER_SHA256 = hashlib.sha256(
    NATIVE_OWNER_WORKER.encode("utf-8"),
).hexdigest()


def validate_worker_source(source: str = NATIVE_OWNER_WORKER) -> ast.Module:
    require(isinstance(source, str) and bool(source),
            "the complete independently frozen V9 native worker is missing")
    try:
        tree = original_v8.validate_worker_source(source)
    except (original_v8.AuditV8Error, SyntaxError, TypeError, ValueError) as error:
        raise AuditV9Error("the independently frozen V9 worker is invalid") from error
    functions = {
        item.name for item in tree.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    require({"_actual_stage07_sentinel", "_verify_stage07_sentinel",
             "audit_foreign_engines"} <= functions,
            "a real before-and-after cached-guard verifier was removed")
    require('stage07._ForbiddenRegexModule is foreign_poison_type' in source
            and 'stage07._ForbiddenRegexModule is not foreign_poison_type' in source
            and "type(observed) is foreign_poison_type" in source
            and "observed is foreign_poison" in source
            and "sys.modules.get(forbidden) is foreign_poison" in source
            and "type(foreign_poison) is not foreign_poison_type" in source
            and source.count('_verify_stage07_sentinel("before")') == 1
            and source.count('_verify_stage07_sentinel("after")') == 1
            and STAGE07_SHA256 in source
            and '"rebar-postfinal-from-scratch-audit-v9-native-owner-worker"' in source,
            "the actual V9 worker weakened the exact original cached-poison contract")
    return tree


def validate_worker(
    document: Any,
    family: str,
    expected_native: Mapping[str, str],
    *,
    allow_failure: bool = False,
) -> dict[str, Any]:
    require(isinstance(document, dict)
            and document.get("schema") == SCHEMA + "-native-owner-worker",
            "the actual native proof must come from the exact V9 owner worker")
    sentinel = document.get("stage07_guard_sentinel")
    require(isinstance(sentinel, dict)
            and set(sentinel) == {"stage07_source_sha256", *SENTINEL_FLAGS}
            and sentinel.get("stage07_source_sha256") == STAGE07_SHA256
            and all(sentinel.get(name) is True for name in SENTINEL_FLAGS),
            "a genuine exact Stage 07 poison was substituted before or after matching")
    original_shape = dict(document)
    original_shape["schema"] = original_v8.SCHEMA + "-native-owner-worker"
    try:
        original_v8.validate_worker(
            original_shape, family, expected_native,
            allow_failure=allow_failure,
        )
    except original_v8.AuditV8Error as error:
        raise AuditV9Error(
            "the exact original 13-guard/5-loader/16-pickle owner failed: "
            + family + ": " + str(error)
        ) from error
    return document


def synthetic_worker(family: str) -> tuple[dict[str, Any], dict[str, str]]:
    report, native = original_v8.synthetic_worker(family)
    report["schema"] = SCHEMA + "-native-owner-worker"
    report["stage07_guard_sentinel"] = {
        "stage07_source_sha256": STAGE07_SHA256,
        **{name: True for name in SENTINEL_FLAGS},
    }
    return report, native


def worker_failure_evidence(
    family: str,
    returncode: int | None,
    stdout: bytes | None,
    stderr: bytes | None,
    *,
    timed_out: bool = False,
    message: str,
) -> dict[str, Any]:
    return {
        **original_v8.worker_failure_evidence(
            family, returncode, stdout, stderr,
            timed_out=timed_out, message=message,
        ),
        "schema": SCHEMA + "-native-owner-worker-failure",
        "native_owner_worker_sha256": NATIVE_OWNER_WORKER_SHA256,
        "stage07_source_sha256": STAGE07_SHA256,
        "previous_v8_owner_failure_qualifies_current_engine": False,
    }


def run_native_worker(family: str, expected: Mapping[str, str]) -> dict[str, Any]:
    require(family in CORE_FAMILIES
            and isinstance(expected, dict) and bool(expected),
            "an actual independently owned V9 native family is required")
    validate_worker_source()
    payload = json.dumps(expected, ensure_ascii=True,
                         sort_keys=True, separators=(",", ":"))
    require(len(payload.encode("ascii")) <= 16 * 1024,
            "the genuinely isolated V9 worker exceeded its bounded arguments")
    environment = {
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
        "LC_ALL": "C", "PATH": "/usr/bin:/bin",
    }
    try:
        child = subprocess.run(
            [str(PINNED_EXECUTABLE), "-I", "-B", "-c", NATIVE_OWNER_WORKER,
             str(ROOT), family, payload],
            cwd=str(ROOT), env=environment, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, timeout=120,
        )
    except subprocess.TimeoutExpired as error:
        evidence = worker_failure_evidence(
            family, None, error.stdout, error.stderr, timed_out=True,
            message="the actual V9 native owner exceeded its 120-second limit",
        )
        raise NativeWorkerFailure(evidence["failure_message"], evidence) from error
    if (child.returncode != 0 or not 0 < len(child.stdout) <= MAX_WORKER_BYTES
            or child.stderr or len(child.stderr) > MAX_WORKER_BYTES):
        evidence = worker_failure_evidence(
            family, child.returncode, child.stdout, child.stderr,
            message="the real V9 native worker crashed, wrote stderr, or returned unsafe evidence",
        )
        raise NativeWorkerFailure(evidence["failure_message"], evidence)
    try:
        report = core.decode_report(child.stdout, label="actual V9 native owner")
        return validate_worker(report, family, expected, allow_failure=True)
    except (AuditV9Error, source_v6.AuditV6Error, UnicodeError, ValueError,
            TypeError, KeyError) as error:
        evidence = worker_failure_evidence(
            family, child.returncode, child.stdout, child.stderr,
            message="the actual V9 owner returned incomplete evidence: " + str(error),
        )
        raise NativeWorkerFailure(evidence["failure_message"], evidence) from error


def destination_name(value: Any) -> str:
    require(type(value) is str,
            "the exclusive V9 owner evidence destination must be exact text")
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts
            and "\\" not in value and "\x00" not in value
            and path.as_posix() == value
            and value in {REPORT_RELATIVE, FAILURE_RELATIVE},
            "only distinct exact exclusively created V9 owner paths are authorized")
    return value


def verify_fresh_report_targets() -> None:
    for path in (REPORT_PATH, FAILURE_PATH):
        require(path.resolve(strict=False) == path
                and path.parent.is_dir() and not path.parent.is_symlink()
                and not path.exists() and not path.is_symlink(),
                "refusing to rerun or overwrite exact V9 owner evidence: "
                + path.relative_to(ROOT).as_posix())
        destination_name(path.relative_to(ROOT).as_posix())


def _read_frozen(relative: str, expected: str) -> bytes:
    require(core.valid_sha256(expected), "an actual frozen V9 input hash is required")
    path = ROOT / relative
    maximum = MAX_REPORT_BYTES if relative.endswith((".json", ".gz")) else MAX_SOURCE_BYTES
    observed, payload = core.bounded_file(
        path, maximum=maximum,
        label="exact immutable V9 native-ownership input: " + relative,
        keep=True,
    )
    require(observed == expected and isinstance(payload, bytes),
            "a genuine frozen V9 native-ownership input changed: " + relative)
    return payload


def validate_v8_owner_failure(document: Any) -> dict[str, Any]:
    require(isinstance(document, dict),
            "the preserved actual V8 Rust owner failure is not complete JSON")
    expected = {
        "schema": "rebar-postfinal-current-build-proofs-v8-native-owner-failure",
        "status": "FAIL", "result": "FAIL", "mode": "diagnostic",
        "candidate_family": "RUST",
        "candidate_module": "candidates.rust_candidate",
        "stage": "before-original-edge",
        "native_worker_crashed": True,
        "refresh_protocol_path": refresh_v8.PROTOCOL_RELATIVE,
        "refresh_protocol_sha256": refresh_v8.REFRESH_PROTOCOL_SHA256,
        "original_edge_worker_started": False,
        "original_deep_worker_started": False,
        "passing_evidence_published": False,
        "campaign_qualified": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    for key, value in expected.items():
        require(document.get(key) == value,
                "the real V8 pre-edge native-owner failure changed: " + key)
    worker = document.get("complete_actual_native_worker")
    require(isinstance(worker, dict)
            and worker.get("status") == "FAIL"
            and worker.get("family") == "rust"
            and worker.get("candidate_module") == "candidates.rust_candidate"
            and worker.get("actual_returncode") == 1
            and worker.get("signal") is None
            and worker.get("timed_out") is False
            and worker.get("stdout_bytes") == 0
            and worker.get("stderr_bytes") == 216
            and worker.get("stdout_sha256")
            == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            and worker.get("stderr_sha256")
            == "020e506be39aab54cc62c7fc5f5ce15a2e8a505e6585df6089298c833e42ba2c"
            and worker.get("production_observations_invented") is False
            and worker.get("qualifies_current_engine") is False,
            "the genuine failed V8 Rust worker or complete real streams were hidden")
    return {
        "path": V8_OWNER_FAILURE_RELATIVE,
        "sha256": V8_OWNER_FAILURE_SHA256,
        "status": "FAIL",
        "stage": "before-original-edge",
        "candidate_module": "candidates.rust_candidate",
        "actual_returncode": 1,
        "stdout_bytes": 0,
        "stderr_bytes": 216,
        "original_edge_worker_started": False,
        "qualifies_current_engine": False,
    }


def verify_history() -> dict[str, Any]:
    verify_runtime()
    for relative, expected in (
        (STAGE07_RELATIVE, STAGE07_SHA256),
        (V8_BASE_RELATIVE, V8_BASE_SHA256),
        (V8_STRICT_RELATIVE, V8_STRICT_SHA256),
        (V8_PROOF_RELATIVE, V8_PROOF_SHA256),
        (PROTOCOL_RELATIVE, PROTOCOL_SHA256),
    ):
        _read_frozen(relative, expected)
    require(Path(original_v8.__file__).resolve()
            == (ROOT / V8_BASE_RELATIVE).resolve()
            and Path(refresh_v8.__file__).resolve()
            == (ROOT / V8_PROOF_RELATIVE).resolve(),
            "the immutable authentic V8 source or original producer was substituted")
    history = original_v8.verify_history()
    compressed = _read_frozen(V8_OWNER_FAILURE_RELATIVE, V8_OWNER_FAILURE_SHA256)
    document, _ = refresh_v8.decode_archive(
        compressed, "actual immutable first V8 Rust native-owner failure",
    )
    incident = validate_v8_owner_failure(document)
    provenance = reference_v5.authenticate_reference_prerequisites(
        V5_SOURCE_SHA256, V5_PROTOCOL_SHA256,
    )
    baseline = reference_v5._read_verified_evidence(
        V5_REFERENCE_RELATIVE, V5_REFERENCE_SHA256,
    )
    roles = reference_v5._validate_reference(baseline, provenance)
    require(set(roles) == {"reference_a", "reference_b"},
            "the actual frozen V5 two-reference Python baseline was omitted")
    return {
        **history,
        "actual_v8_native_owner_failure": incident,
        "actual_v5_reference_path": V5_REFERENCE_RELATIVE,
        "actual_v5_reference_sha256": V5_REFERENCE_SHA256,
        "actual_v5_reference_schema": reference_v5.SCHEMA + "-self-oracle",
        "actual_v5_reference_role_count": 2,
        "actual_v5_reference_methods_per_role": 152,
        "actual_v5_reference_applicable_per_role": 151,
        "actual_v5_reference_private_debug_skips_per_role": 1,
        "stage07_source_sha256": STAGE07_SHA256,
        "historical_v8_owner_failure_qualifies_current_engine": False,
    }


def _synthetic_v8_owner_failure() -> dict[str, Any]:
    return {
        "schema": "rebar-postfinal-current-build-proofs-v8-native-owner-failure",
        "status": "FAIL", "result": "FAIL", "mode": "diagnostic",
        "candidate_family": "RUST",
        "candidate_module": "candidates.rust_candidate",
        "stage": "before-original-edge",
        "native_worker_crashed": True,
        "refresh_protocol_path": refresh_v8.PROTOCOL_RELATIVE,
        "refresh_protocol_sha256": refresh_v8.REFRESH_PROTOCOL_SHA256,
        "original_edge_worker_started": False,
        "original_deep_worker_started": False,
        "passing_evidence_published": False,
        "campaign_qualified": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        "complete_actual_native_worker": {
            "status": "FAIL", "family": "rust",
            "candidate_module": "candidates.rust_candidate",
            "actual_returncode": 1, "signal": None, "timed_out": False,
            "stdout_bytes": 0, "stderr_bytes": 216,
            "stdout_sha256":
                "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "stderr_sha256":
                "020e506be39aab54cc62c7fc5f5ce15a2e8a505e6585df6089298c833e42ba2c",
            "production_observations_invented": False,
            "qualifies_current_engine": False,
        },
    }


def candidate_free_self_test() -> dict[str, Any]:
    verify_runtime()
    core.ensure_candidate_free()
    inherited = original_v8.candidate_free_self_test()
    require(inherited.get("passed") is True and inherited.get("check_count", 0) >= 540,
            "the immutable original native-owner source-only guards failed")
    checks: list[dict[str, Any]] = []

    def accept(name: str, condition: Any) -> None:
        require(not any(item["name"] == name for item in checks),
                "an actual source-only V9 poison was repeated")
        checks.append({"name": name, "passed": bool(condition)})

    def reject(name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except (AuditV9Error, original_v8.AuditV8Error,
                source_v6.AuditV6Error, AssertionError, TypeError,
                ValueError, KeyError, OSError):
            accept(name, True)
        else:
            accept(name, False)

    effects = core.previous.BlockSelfTestEffects()
    with effects:
        for item in inherited["checks"]:
            accept("immutable-v8:" + item["name"], item.get("passed") is True)
        accept("direct-clean-isolation-uses-only-the-exact-trusted-root",
               bool(sys.path) and sys.path[0] == str(ROOT))
        accept("freeze-the-actual-stage07-source-before-poison-composition",
               STAGE07_SHA256
               == "150abcfc597658f48d64c04053889bd4b299c75ad7413bc1cafa5f864e9e7c25")
        accept("preserve-the-actual-v8-rust-owner-failure",
               V8_OWNER_FAILURE_SHA256
               == "2f8bfcba726d729865cb8411a25ef1c3e0633e80c70af8895e5875a71f15ed7b")
        accept("preserve-the-real-independent-two-python-reference",
               V5_REFERENCE_SHA256
               == "3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916")
        accept("compile-only-the-complete-additive-v9-owner-worker",
               isinstance(validate_worker_source(), ast.Module))
        accept("do-not-dispatch-or-modify-the-frozen-v8-native-owner-worker",
               NATIVE_OWNER_WORKER != original_v8.NATIVE_OWNER_WORKER
               and NATIVE_OWNER_WORKER_SHA256
               == hashlib.sha256(NATIVE_OWNER_WORKER.encode("utf-8")).hexdigest())
        accept("keep-all-three-distinct-native-engine-families",
               CORE_FAMILIES == ("rust", "vm", "zig"))
        accept("keep-all-12-distinct-current-owned-native-sources",
               sum(len(rows) for rows in OWNED_SOURCE_PATHS.values()) == 12)
        accept("keep-all-five-current-owned-native-elf-roles",
               sum(len(rows) for rows in OWNED_NATIVE_PATHS.values()) == 5)
        for name, value in (
            ("stage07-source", STAGE07_RELATIVE),
            ("base-v8-source", V8_BASE_RELATIVE),
            ("strict-v8-source", V8_STRICT_RELATIVE),
            ("owner-failure", V8_OWNER_FAILURE_RELATIVE),
            ("real-double-reference", V5_REFERENCE_RELATIVE),
        ):
            accept("freeze-only-the-exact-actual-historical-path:" + name,
                   isinstance(value, str) and ".." not in PurePosixPath(value).parts)

        for family in CORE_FAMILIES:
            original, native = synthetic_worker(family)
            accept("accept-only-the-complete-in-memory-v9-sentinel:" + family,
                   validate_worker(copy.deepcopy(original), family, native)
                   ["stage07_guard_sentinel"]["sentinel_type_exact"] is True)

            def poison(label: str,
                       change: Callable[[dict[str, Any]], None]) -> None:
                changed = copy.deepcopy(original)
                change(changed)
                reject("reject-v9:" + family + ":" + label,
                       lambda: validate_worker(changed, family, native))

            poison("stale-v8-owner-worker-schema",
                   lambda row: row.update({
                       "schema": original_v8.SCHEMA + "-native-owner-worker",
                   }))
            poison("substituted-stage07-source",
                   lambda row: row["stage07_guard_sentinel"].update({
                       "stage07_source_sha256": "0" * 64,
                   }))
            for flag in SENTINEL_FLAGS:
                poison("forged-or-missing-exact-stage07-sentinel:" + flag,
                       lambda row, flag=flag:
                       row["stage07_guard_sentinel"].update({flag: False}))
            poison("missing-stage07-exact-sentinel-proof",
                   lambda row: row.pop("stage07_guard_sentinel"))
            poison("unauthorized-extra-stage07-sentinel-claim",
                   lambda row: row["stage07_guard_sentinel"].update({
                       "unaudited_success": True,
                   }))
            for field in (
                "regex_guard_observations",
                "regex_guard_observations_after",
                "foreign_engine_guard_observations",
                "foreign_engine_guard_observations_after",
                "native_loader_guard_observations",
                "native_loader_guard_observations_after",
                "standard_pickle_checks",
            ):
                poison("drop-real-before-or-after-observation:" + field,
                       lambda row, field=field: row[field].pop())
            for field in (
                "persistent_cross_engine_guard",
                "guarded_builtin_import_unchanged",
                "poisoned_module_bindings_unchanged",
                "protected_loader_identities_unchanged",
                "native_type_identity_verified",
                "public_cpython_module_verified",
                "genuine_matching_executed",
            ):
                poison("disable-real-persistent-native-guard:" + field,
                       lambda row, field=field: row.update({field: False}))
            for field in (
                "stdlib_re_blocked", "cpython_sre_blocked",
                "third_party_regex_blocked", "cross_family_blocked",
                "foreign_dynamic_libraries_blocked",
            ):
                poison("disable-real-stage07-matcher-guard:" + field,
                       lambda row, field=field: row["guard"].update({field: False}))
            poison("retain-a-foreign-native-family",
                   lambda row: row["loaded_candidate_modules"].append(
                       "candidates._foreign",
                   ))
            poison("claim-benchmark-execution-as-an-ownership-pass",
                   lambda row: row.update({"benchmark_or_timing_executed": True}))
            poison("read-holdout-while-claiming-an-ownership-pass",
                   lambda row: row.update({"holdout_or_case_fixture_access": True}))
            genuine_failure = copy.deepcopy(original)
            genuine_failure["standard_pickle_checks"][8].update({
                "passed": False, "error_type": "PicklingError",
                "error_message": "an actual native origin was not restored",
            })
            genuine_failure.update({
                "standard_pickle_failure_count": 1,
                "status": "FAIL", "result": "FAIL", "passed": False,
            })
            accept("retain-a-real-nonqualifying-v9-pickle-failure:" + family,
                   validate_worker(genuine_failure, family, native,
                                   allow_failure=True)["status"] == "FAIL")
            reject("never-promote-an-actual-v9-pickle-failure:" + family,
                   lambda failure=genuine_failure, name=family, owned=native:
                   validate_worker(failure, name, owned))

        incident = _synthetic_v8_owner_failure()
        accept("preserve-the-actual-pre-edge-v8-owner-failure-as-fail",
               validate_v8_owner_failure(copy.deepcopy(incident))["status"] == "FAIL")
        for key, value in (
            ("status", "PASS"), ("result", "PASS"),
            ("mode", "qualified"), ("candidate_family", "ZIG"),
            ("candidate_module", "candidates.zig_candidate"),
            ("stage", "after-original-edge"),
            ("native_worker_crashed", False),
            ("original_edge_worker_started", True),
            ("original_deep_worker_started", True),
            ("passing_evidence_published", True),
            ("campaign_qualified", True),
            ("refresh_protocol_sha256", "0" * 64),
            ("performance", "faster"), ("holdout", "ACCESSED"),
        ):
            forged = copy.deepcopy(incident)
            forged[key] = value
            reject("reject-a-forged-real-v8-owner-failure:" + key,
                   lambda forged=forged: validate_v8_owner_failure(forged))
        for key, value in (
            ("status", "PASS"), ("family", "vm"),
            ("actual_returncode", 0), ("timed_out", True),
            ("stdout_bytes", 1), ("stderr_bytes", 0),
            ("stdout_sha256", "0" * 64), ("stderr_sha256", "0" * 64),
            ("production_observations_invented", True),
            ("qualifies_current_engine", True),
        ):
            forged = copy.deepcopy(incident)
            forged["complete_actual_native_worker"][key] = value
            reject("reject-a-forged-real-v8-worker-stream:" + key,
                   lambda forged=forged: validate_v8_owner_failure(forged))
        oversized = b"v9-real-worker-observation:" * (
            MAX_WORKER_BYTES // len(b"v9-real-worker-observation:") + 2
        )
        crash = worker_failure_evidence(
            "rust", -9, oversized, b"source-only-real-stream-poison",
            message="synthetic-only V9 native signal preservation",
        )
        accept("preserve-the-complete-oversized-real-stream-fingerprint",
               crash["stdout_sha256"] == hashlib.sha256(oversized).hexdigest()
               and crash["stdout_bytes"] == len(oversized)
               and crash["stdout_complete"] is False)
        accept("never-invent-a-real-crashed-native-owner-observation",
               crash["signal"] == 9
               and crash["production_observations_invented"] is False
               and crash["qualifies_current_engine"] is False)
        for value in (
            original_v8.REPORT_RELATIVE,
            "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V9.json",
            "performance/private-holdout.json",
            "../POSTFINAL-FROM-SCRATCH-AUDIT-V9.json",
            "/tmp/POSTFINAL-FROM-SCRATCH-AUDIT-V9.json",
        ):
            reject("reject-unsafe-or-historical-v9-owner-output:" + value,
                   lambda value=value: destination_name(value))
        for value in (REPORT_RELATIVE, FAILURE_RELATIVE):
            accept("allow-only-exact-distinct-v9-owner-destination:" + value,
                   destination_name(value) == value)

    require(len(checks) >= 150 and all(item["passed"] for item in checks),
            "an actual V9 candidate-free sentinel or ownership poison escaped")
    require(effects.counts["processes"] == 0
            and effects.counts["files"] == 0
            and effects.counts["clocks"] == 0,
            "the source-only V9 owner control caused an external side effect")
    core.ensure_candidate_free()
    verify_runtime()
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS", "passed": True,
        "check_count": len(checks), "checks": checks,
        "immutable_v8_control_count": inherited["check_count"],
        "stage07_source_sha256": STAGE07_SHA256,
        "v8_native_owner_failure_sha256": V8_OWNER_FAILURE_SHA256,
        "v5_reference_sha256": V5_REFERENCE_SHA256,
        "candidate_imports": 0,
        "subprocesses": effects.counts["processes"],
        "file_reads": effects.counts["files"],
        "file_writes": effects.counts["files"],
        "clock_samples": effects.counts["clocks"],
        "owned_source_count": 12,
        "owned_native_binary_count": 5,
        "native_family_count": 3,
        "genuine_public_pickle_checks_required": 48,
        "genuine_python_matching_guards_per_family": 13,
        "genuine_native_loader_guards_per_family": 5,
        "synthetic_results_qualify_candidates": False,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
    }


def audit() -> dict[str, Any]:
    verify_runtime()
    runtime = core.verify_production_runtime()
    core.ensure_candidate_free()
    history = verify_history()
    controls = candidate_free_self_test()
    core.ensure_candidate_free()
    gc.collect()
    with source_v5.allow_owned_locale_ctype():
        current = core.audit()
    core.validate_v3_report(current, label="genuine fresh V9 bounded source ownership")
    graph = source_v6._validate_fresh_graph(current)
    core.ensure_candidate_free()
    observations: dict[str, dict[str, Any]] = {}
    failure: dict[str, Any] | None = None
    for family in CORE_FAMILIES:
        try:
            observation = run_native_worker(
                family, graph["native_sha256_by_family"][family],
            )
            observations[family] = observation
            if observation.get("status") != "PASS":
                failure = {
                    "schema": SCHEMA + "-actual-observed-native-owner-failure",
                    "status": "FAIL", "family": family,
                    "actual_native_owner_worker": observation,
                    "production_observations_invented": False,
                    "qualifies_current_engine": False,
                }
                break
        except NativeWorkerFailure as error:
            failure = error.evidence
            break
    core.ensure_candidate_free()
    pickle_failures = sum(
        worker["standard_pickle_failure_count"]
        for worker in observations.values()
    )
    passed = (failure is None and len(observations) == len(CORE_FAMILIES)
              and pickle_failures == 0)
    source_digest, _ = core.bounded_file(
        SOURCE_PATH, maximum=MAX_SOURCE_BYTES,
        label="actual frozen independently guarded V9 native owner source",
    )
    report = dict(current)
    report.update({
        "schema": SCHEMA, "postfinal_schema": SCHEMA,
        "status": "PASS" if passed else "FAIL",
        "result": "PASS" if passed else "FAIL", "passed": passed,
        "audit_source_path": SOURCE_RELATIVE,
        "audit_source_sha256": source_digest,
        "native_ownership_protocol_path": PROTOCOL_RELATIVE,
        "native_ownership_protocol_sha256": PROTOCOL_SHA256,
        "stage07_source_path": STAGE07_RELATIVE,
        "stage07_source_sha256": STAGE07_SHA256,
        "native_owner_worker_sha256": NATIVE_OWNER_WORKER_SHA256,
        "v5_reference_path": V5_REFERENCE_RELATIVE,
        "v5_reference_sha256": V5_REFERENCE_SHA256,
        "v5_reference_role_count": 2,
        "v5_reference_methods_per_role": 152,
        "v5_reference_applicable_per_role": 151,
        "v5_reference_private_debug_skips_per_role": 1,
        "actual_v8_native_owner_failure": history[
            "actual_v8_native_owner_failure"
        ],
        "historical_v8_owner_failure_qualifies_current_build": False,
        "historical_v7_results_qualify_current_build": False,
        "historical_first_campaign_failure_preserved": True,
        "historical_public_input_sha256": history["historical_input_sha256"],
        "historical_current_build_edge_failures": history["real_edge_failures"],
        "postfinal_wrapper_self_test": controls,
        "postfinal_interpreter": runtime,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": graph["source_count"],
        "verified_candidate_source_paths": graph["source_paths"],
        "verified_native_role_count": graph["native_binary_count"],
        "native_sha256_by_family": graph["native_sha256_by_family"],
        "public_type_ownership": {
            family: worker["public_type_ownership"]
            for family, worker in observations.items()
        },
        "public_match_repr": observations,
        "match_repr_checks_per_family": 2,
        "verified_match_repr_checks": sum(
            worker["match_repr_checks"] for worker in observations.values()
        ),
        "standard_pickle_checks_per_family": 16,
        "standard_pickle_checks": sum(
            worker["standard_pickle_check_count"]
            for worker in observations.values()
        ),
        "standard_pickle_failure_count": pickle_failures,
        "actual_native_owner_workers": observations,
        "actual_native_owner_worker_failure": failure,
        "completed_native_owner_worker_count": len(observations),
        "unstarted_native_owner_families": [
            family for family in CORE_FAMILIES
            if family not in observations
            and (failure is None or family != failure.get("family"))
        ],
        "postfinal_scope": {
            "append_only": True,
            "exclusive_report_path": REPORT_RELATIVE if passed else FAILURE_RELATIVE,
            "separate_pass_and_failure_destinations": True,
            "previous_v7_reports_historical": True,
            "previous_v8_owner_failure_preserved": True,
            "historical_v8_owner_failure_qualifies_current_build": False,
            "actual_edge_failures_preserved": True,
            "exact_current_owned_candidate_source_count": 12,
            "actual_current_native_binary_count": 5,
            "actual_native_matching_workers": (
                len(observations) + int(failure is not None
                                        and failure.get("family") not in observations)
            ),
            "genuine_public_pickle_checks": sum(
                worker["standard_pickle_check_count"]
                for worker in observations.values()
            ),
            "genuine_match_repr_checks": sum(
                worker["match_repr_checks"] for worker in observations.values()
            ),
            "actual_python_matching_guards_per_family": 13,
            "actual_native_loader_guards_per_family": 5,
            "exact_stage07_sentinel_checked_before_and_after": True,
            "native_identity_is_independent_of_public_module": True,
            "candidate_imports": "isolated guarded subprocesses only",
            "mapped_binaries_hashed_against_static_elf": True,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
    })
    require(graph["source_count"] == 12 and graph["native_binary_count"] == 5,
            "the current independently owned V9 source or ELF denominator changed")
    if passed:
        require(report["verified_match_repr_checks"] == 6
                and report["standard_pickle_checks"] == 48,
                "a passing V9 owner weakened the actual native match or pickle suite")
    else:
        require(failure is not None,
                "a failing V9 owner invented rather than retaining an actual failure")
    core.ensure_candidate_free()
    return report


def write_report(report: Mapping[str, Any], target: Path | None = None) -> str:
    require(isinstance(report, Mapping),
            "the exclusively preserved V9 owner report must be complete")
    expected = REPORT_PATH if report.get("passed") is True else FAILURE_PATH
    chosen = expected if target is None else target
    require(isinstance(chosen, Path) and chosen.resolve(strict=False) == expected
            and expected.parent.is_dir() and not expected.parent.is_symlink(),
            "an actual V9 success or failure escaped its distinct exact destination")
    destination_name(expected.relative_to(ROOT).as_posix())
    payload = core.canonical(report) + b"\n"
    require(0 < len(payload) <= MAX_REPORT_BYTES,
            "complete genuine V9 owner evidence exceeded its frozen safe bound")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    directory = os.open(expected.parent, flags)
    try:
        require(stat.S_ISDIR(os.fstat(directory).st_mode),
                "the genuine V9 report parent is not an actual directory")
        create = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        create |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
        descriptor = os.open(expected.name, create, 0o644, dir_fd=directory)
        try:
            pending = memoryview(payload)
            while pending:
                wrote = os.write(descriptor, pending)
                require(wrote > 0, "an exclusively created V9 report was truncated")
                pending = pending[wrote:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.fsync(directory)
    finally:
        os.close(directory)
    return hashlib.sha256(payload).hexdigest()


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--gate", action="store_true")
    modes.add_argument("--audit", action="store_true")
    parser.add_argument("--output", type=Path)
    options = parser.parse_args(arguments)
    try:
        verify_runtime()
        core.ensure_candidate_free()
        if options.self_test:
            require(options.output is None,
                    "the candidate-free V9 owner self-test cannot redirect evidence")
            result = candidate_free_self_test()
            sys.stdout.buffer.write(core.canonical(result) + b"\n")
            return 0
        verify_fresh_report_targets()
        report = audit()
        observed = write_report(report, options.output)
        relative = REPORT_RELATIVE if report["passed"] else FAILURE_RELATIVE
        result = {
            "schema": SCHEMA,
            "status": report["status"], "result": report["result"],
            "passed": report["passed"],
            "report": relative, "report_sha256": observed,
            "audit_source_sha256": report["audit_source_sha256"],
            "stage07_source_sha256": STAGE07_SHA256,
            "verified_core_family_count": 3,
            "verified_candidate_source_count": 12,
            "verified_native_role_count": 5,
            "verified_match_repr_checks": report["verified_match_repr_checks"],
            "standard_pickle_checks": report["standard_pickle_checks"],
            "standard_pickle_failure_count": report["standard_pickle_failure_count"],
            "completed_native_owner_worker_count": report[
                "completed_native_owner_worker_count"
            ],
            "actual_native_owner_worker_failure": report[
                "actual_native_owner_worker_failure"
            ],
            "actual_v8_native_owner_failure": report[
                "actual_v8_native_owner_failure"
            ],
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }
        sys.stdout.buffer.write(core.canonical(result) + b"\n")
        return int(not report["passed"])
    except (AuditV9Error, original_v8.AuditV8Error, source_v6.AuditV6Error,
            refresh_v8.ProofV8Error, reference_v5.OfficialV5Error,
            OSError, RuntimeError, TypeError, ValueError,
            KeyError, UnicodeError, subprocess.SubprocessError) as error:
        sys.stdout.buffer.write(core.canonical({
            "schema": SCHEMA, "status": "BLOCKED", "result": "BLOCKED",
            "passed": False, "error_type": type(error).__name__,
            "error": str(error),
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }) + b"\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
