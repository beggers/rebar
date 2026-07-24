#!/usr/bin/env python3
"""Prove cached Python regex internals cannot power an owned native engine."""

from __future__ import annotations

import argparse
import ast
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

from tools import postfinal_current_build_proofs_v8 as refresh_v8
from tools import postfinal_from_scratch_audit_v5 as source_v5
from tools import postfinal_from_scratch_audit_v6 as source_v6
from tools import postfinal_from_scratch_audit_v9 as previous


core = previous.core
SCHEMA = "rebar-postfinal-from-scratch-audit-v10"
SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v10.py"
SOURCE_PATH = ROOT / SOURCE_RELATIVE
REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V10.json"
FAILURE_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V10-FAILURES.json"
)
REPORT_PATH = ROOT / REPORT_RELATIVE
FAILURE_PATH = ROOT / FAILURE_RELATIVE
PROTOCOL_RELATIVE = "candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V10.md"
PROTOCOL_SHA256 = (
    "902bc095d08331089dcc1d1d11233747438a0cacb0cf1057ae41a2474bde2fa6"
)
CORE_FAMILIES = tuple(previous.CORE_FAMILIES)
OWNED_NATIVE_MODULES = dict(previous.OWNED_NATIVE_MODULES)
OWNED_SOURCE_PATHS = dict(previous.OWNED_SOURCE_PATHS)
OWNED_NATIVE_PATHS = dict(previous.OWNED_NATIVE_PATHS)
NATIVE_LOADER_ALIASES = tuple(previous.NATIVE_LOADER_ALIASES)
PICKLE_PROTOCOLS = tuple(previous.PICKLE_PROTOCOLS)
PINNED_EXECUTABLE = previous.PINNED_EXECUTABLE
MAX_SOURCE_BYTES = previous.MAX_SOURCE_BYTES
MAX_REPORT_BYTES = previous.MAX_REPORT_BYTES
MAX_WORKER_BYTES = previous.MAX_WORKER_BYTES
V7_EDGE_FAILURES = dict(previous.V7_EDGE_FAILURES)
V7_EDGE_EXPECTATIONS = dict(previous.V7_EDGE_EXPECTATIONS)
EDGE_SCHEMA = previous.EDGE_SCHEMA
EDGE_SEED = previous.EDGE_SEED
EDGE_CHECKS = previous.EDGE_CHECKS
EDGE_CATEGORIES = previous.EDGE_CATEGORIES
EDGE_REFERENCE_SHA256 = previous.EDGE_REFERENCE_SHA256
STAGE07_RELATIVE = previous.STAGE07_RELATIVE
STAGE07_SHA256 = previous.STAGE07_SHA256
V5_REFERENCE_RELATIVE = previous.V5_REFERENCE_RELATIVE
V5_REFERENCE_SHA256 = previous.V5_REFERENCE_SHA256
V8_OWNER_FAILURE_RELATIVE = previous.V8_OWNER_FAILURE_RELATIVE
V8_OWNER_FAILURE_SHA256 = previous.V8_OWNER_FAILURE_SHA256
V9_BASE_RELATIVE = "tools/postfinal_from_scratch_audit_v9.py"
V9_BASE_SHA256 = (
    "30822ec9a66a75528c0bf5b94f5451ba81f1fd3689e1d3849f35acf52507f8e1"
)
V9_STRICT_RELATIVE = "tools/postfinal_no_delegation_audit_v9.py"
V9_STRICT_SHA256 = (
    "5a236445936362b738d9fbfc5ed239a47c75d6f4f1e40e3d8d3b86883a502f7c"
)
V9_PROOF_RELATIVE = "tools/postfinal_current_build_proofs_v9.py"
V9_PROOF_SHA256 = (
    "5604c513efef32a352336506e23b855ee7fb6010722dc3dae2b97c9601ad4c86"
)
V9_REFRESH_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V9.md"
)
V9_REFRESH_PROTOCOL_SHA256 = (
    "986f29f6a31981f8bf5155bd1b04f5d3ba569ba80a49652ed638c99f01e92680"
)
V9_OWNERSHIP_PROTOCOL_RELATIVE = previous.PROTOCOL_RELATIVE
V9_OWNERSHIP_PROTOCOL_SHA256 = previous.PROTOCOL_SHA256
V9_OWNER_FAILURE_RELATIVE = (
    "candidates/evidence/"
    "rust-v7-edge-oracle-rust-postfinal-current-build-v9-"
    "diagnostic-native-owner-failure.json.gz"
)
V9_OWNER_FAILURE_SHA256 = (
    "04e52f831534458e9af50ad3ab962d78ad43e6a8725cbfccfee37bf9c234f07c"
)
EMPTY_STREAM_SHA256 = (
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
)
V9_OWNER_STDERR_SHA256 = (
    "7cfcf842efd492372ee01c330db0fc632aac9182c5f5b45870c5286a3e841097"
)
SENTINEL_FLAGS = tuple(previous.SENTINEL_FLAGS)
REQUIRED_MATCHER_DESCENDANTS = ("re._compiler", "re._parser")
MATCHER_GUARD_FLAGS = (
    "blocked", "sentinel_identity", "cache_identity", "sentinel_type_exact",
)


class AuditV10Error(source_v6.AuditV6Error):
    """A genuine cached matcher, source, owner, or native failure escaped."""


class NativeWorkerFailure(AuditV10Error):
    """Preserve all actual bounded native-owner process and stream observations."""

    def __init__(self, message: str, evidence: Mapping[str, Any]):
        super().__init__(message)
        self.evidence = dict(evidence)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditV10Error(message)


def verify_runtime() -> None:
    require(tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.implementation.name == "cpython"
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and Path(sys.executable).resolve() == PINNED_EXECUTABLE.resolve()
            and bool(sys.path) and sys.path[0] == str(ROOT)
            and Path(__file__).resolve() == SOURCE_PATH.resolve(),
            "the exact direct isolated pinned V10 source and trusted root are required")


_MATCHER_DESCENDANT_SETUP = r'''

def _install_real_cached_matcher_guards():
    cached = tuple(
        (name, module)
        for name, module in tuple(sys.modules.items())
        if name.startswith("re.")
        and isinstance(module, types.ModuleType)
        and module is not foreign_poison
    )
    by_name = {name: module for name, module in cached}
    required = ("re._compiler", "re._parser")
    if not all(name in by_name for name in required):
        raise RuntimeError("the actual original cached Python matcher disappeared")
    originals = tuple(module for _, module in cached)
    if len({id(module) for module in originals}) != len(originals):
        raise RuntimeError("genuine cached Python matcher objects were substituted")

    bindings = []
    for holder in tuple(sys.modules.values()):
        if not isinstance(holder, types.ModuleType):
            continue
        try:
            entries = tuple(vars(holder).items())
        except (TypeError, ValueError):
            continue
        for alias, observed in entries:
            if any(observed is original for original in originals):
                bindings.append((holder, alias))

    replaced = stage07._poison_cached_module_aliases(
        sys.modules, originals, foreign_poison,
    )
    if type(replaced) is not int or replaced < 0 or replaced != len(bindings):
        raise RuntimeError("a genuine cached Python matcher alias escaped poisoning")
    for name, _ in cached:
        sys.modules[name] = foreign_poison
    if any(vars(holder).get(alias) is not foreign_poison
           for holder, alias in bindings):
        raise RuntimeError("a cached real Python matcher alias was not blocked")
    return tuple(sorted(by_name)), originals, tuple(bindings), replaced


matcher_descendant_names, matcher_descendant_originals, \
    matcher_descendant_aliases, matcher_alias_replacements = (
        _install_real_cached_matcher_guards()
    )


def _verify_real_cached_matcher_guards(phase):
    if phase not in ("before", "after"):
        raise RuntimeError("the real Python matcher cache verification was substituted")
    if stage07._ForbiddenRegexModule is not foreign_poison_type:
        raise RuntimeError("the original genuine Stage 07 poison class was replaced")
    if type(foreign_poison) is not foreign_poison_type:
        raise RuntimeError("the original genuine Stage 07 poison object was replaced")
    if not all(name in matcher_descendant_names
               for name in ("re._compiler", "re._parser")):
        raise RuntimeError("an actual cached original Python matcher was removed")
    observations = []
    for name in matcher_descendant_names:
        cached = sys.modules.get(name)
        imported = importlib.import_module(name)
        record = {
            "module": name,
            "blocked": True,
            "sentinel_identity": imported is foreign_poison,
            "cache_identity": cached is foreign_poison,
            "sentinel_type_exact": type(cached) is foreign_poison_type,
        }
        if not all(record[key] is True for key in (
            "blocked", "sentinel_identity", "cache_identity", "sentinel_type_exact"
        )):
            raise RuntimeError("a genuine cached Python matcher was restored: " + name)
        observations.append(record)
    if any(vars(holder).get(alias) is not foreign_poison
           for holder, alias in matcher_descendant_aliases):
        raise RuntimeError("a genuine cached Python matcher alias was restored")
    for holder in tuple(sys.modules.values()):
        if not isinstance(holder, types.ModuleType):
            continue
        try:
            values = tuple(vars(holder).values())
        except (TypeError, ValueError):
            continue
        if any(value is original for value in values
               for original in matcher_descendant_originals):
            raise RuntimeError("a cached alias still reaches a real Python matcher")
    return observations
'''


def _replace_once(source: str, old: str, new: str, label: str) -> str:
    require(source.count(old) == 1,
            "the immutable genuine V9 native worker changed: " + label)
    return source.replace(old, new, 1)


def _build_native_owner_worker() -> str:
    source = previous.NATIVE_OWNER_WORKER
    marker = (
        'if type(foreign_poison) is not foreign_poison_type:\n'
        '    raise RuntimeError("the actual Stage 07 foreign guard was replaced")\n'
    )
    source = _replace_once(
        source, marker, marker + _MATCHER_DESCENDANT_SETUP,
        "authenticate and poison every cached genuine Python matcher",
    )
    source = _replace_once(
        source,
        "regex_guards = audit_python_matchers()\n",
        'matcher_descendant_guards_before = '
        '_verify_real_cached_matcher_guards("before")\n'
        'regex_guards = audit_python_matchers()\n',
        "verify every cached matcher before all thirteen genuine guards",
    )
    source = _replace_once(
        source,
        "regex_guards_after = audit_python_matchers()\n",
        'matcher_descendant_guards_after = '
        '_verify_real_cached_matcher_guards("after")\n'
        'if matcher_descendant_guards_after != matcher_descendant_guards_before:\n'
        '    raise RuntimeError("a genuine cached Python matcher changed after matching")\n'
        'regex_guards_after = audit_python_matchers()\n',
        "verify every cached matcher after actual native matching",
    )
    source = _replace_once(
        source,
        '"schema": "rebar-postfinal-from-scratch-audit-v9-native-owner-worker",\n',
        '"schema": "rebar-postfinal-from-scratch-audit-v10-native-owner-worker",\n',
        "the distinct actually executed V10 native-owner worker schema",
    )
    source = _replace_once(
        source,
        '    "stage07_guard_sentinel": stage07_guard_sentinel,\n',
        '    "stage07_guard_sentinel": stage07_guard_sentinel,\n'
        '    "stage07_matcher_descendant_guards": {\n'
        '        "stage07_source_sha256": actual_stage07_source_sha256,\n'
        '        "required_descendants": ["re._compiler", "re._parser"],\n'
        '        "discovered_descendants": list(matcher_descendant_names),\n'
        '        "observations_before": matcher_descendant_guards_before,\n'
        '        "observations_after": matcher_descendant_guards_after,\n'
        '        "cached_alias_count": len(matcher_descendant_aliases),\n'
        '        "helper_alias_replacement_count": matcher_alias_replacements,\n'
        '        "all_cached_aliases_same_sentinel": True,\n'
        '        "before_matching_verified": True,\n'
        '        "after_matching_verified": True,\n'
        '    },\n',
        "complete observed before-and-after real matcher cache evidence",
    )
    return source


NATIVE_OWNER_WORKER = _build_native_owner_worker()
NATIVE_OWNER_WORKER_SHA256 = hashlib.sha256(
    NATIVE_OWNER_WORKER.encode("utf-8"),
).hexdigest()


def validate_worker_source(source: str = NATIVE_OWNER_WORKER) -> ast.Module:
    require(isinstance(source, str) and bool(source),
            "the complete independently owned V10 native worker is missing")
    try:
        tree = previous.validate_worker_source(
            source.replace(
                '"rebar-postfinal-from-scratch-audit-v10-native-owner-worker"',
                '"rebar-postfinal-from-scratch-audit-v9-native-owner-worker"',
                1,
            ),
        )
    except (previous.AuditV9Error, source_v6.AuditV6Error,
            SyntaxError, TypeError, ValueError) as error:
        raise AuditV10Error("the actual complete V10 owner cannot be compiled") from error
    functions = {
        row.name for row in tree.body
        if isinstance(row, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    require({"_install_real_cached_matcher_guards",
             "_verify_real_cached_matcher_guards",
             "_actual_stage07_sentinel", "_verify_stage07_sentinel",
             "audit_foreign_engines"} <= functions
            and "stage07._poison_cached_module_aliases(" in source
            and 'name.startswith("re.")' in source
            and '"re._compiler", "re._parser"' in source
            and source.count('_verify_real_cached_matcher_guards("before")') == 1
            and source.count('_verify_real_cached_matcher_guards("after")') == 1
            and 'sys.modules[name] = foreign_poison' in source
            and '"stage07_matcher_descendant_guards"' in source
            and '"rebar-postfinal-from-scratch-audit-v10-native-owner-worker"'
            in source,
            "a genuine cached internal matcher or before-and-after guard was removed")
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
            "the proof must be an actual distinct V10 native owner worker")
    descendants = document.get("stage07_matcher_descendant_guards")
    require(isinstance(descendants, dict)
            and set(descendants) == {
                "stage07_source_sha256", "required_descendants",
                "discovered_descendants", "observations_before",
                "observations_after", "cached_alias_count",
                "helper_alias_replacement_count",
                "all_cached_aliases_same_sentinel",
                "before_matching_verified", "after_matching_verified",
            }
            and descendants.get("stage07_source_sha256") == STAGE07_SHA256
            and descendants.get("required_descendants")
            == list(REQUIRED_MATCHER_DESCENDANTS)
            and descendants.get("all_cached_aliases_same_sentinel") is True
            and descendants.get("before_matching_verified") is True
            and descendants.get("after_matching_verified") is True,
            "the exact cached original CPython matcher guard is incomplete")
    names = descendants.get("discovered_descendants")
    require(isinstance(names, list)
            and names == sorted(set(names))
            and set(REQUIRED_MATCHER_DESCENDANTS) <= set(names)
            and all(isinstance(name, str) and name.startswith("re.")
                    for name in names),
            "the exact cached original Python matcher descendants were concealed")
    expected = [
        {"module": name, **{flag: True for flag in MATCHER_GUARD_FLAGS}}
        for name in names
    ]
    require(descendants.get("observations_before") == expected
            and descendants.get("observations_after") == expected,
            "a real cached original Python matcher or alias was restored")
    alias_count = descendants.get("cached_alias_count")
    helper_count = descendants.get("helper_alias_replacement_count")
    require(type(alias_count) is int and alias_count >= 0
            and type(helper_count) is int and helper_count >= 0
            and helper_count == alias_count,
            "the genuine Stage 07 matcher-alias poison helper was not applied")
    old = dict(document)
    old["schema"] = previous.SCHEMA + "-native-owner-worker"
    try:
        previous.validate_worker(
            old, family, expected_native, allow_failure=allow_failure,
        )
    except (previous.AuditV9Error, source_v6.AuditV6Error) as error:
        raise AuditV10Error(
            "the unchanged complete sentinel/13-guard/5-loader/16-pickle "
            "native owner failed: " + family + ": " + str(error)
        ) from error
    return document


def synthetic_worker(family: str) -> tuple[dict[str, Any], dict[str, str]]:
    report, native = previous.synthetic_worker(family)
    names = list(REQUIRED_MATCHER_DESCENDANTS)
    observations = [
        {"module": name, **{flag: True for flag in MATCHER_GUARD_FLAGS}}
        for name in names
    ]
    report["schema"] = SCHEMA + "-native-owner-worker"
    report["stage07_matcher_descendant_guards"] = {
        "stage07_source_sha256": STAGE07_SHA256,
        "required_descendants": names,
        "discovered_descendants": names,
        "observations_before": observations,
        "observations_after": copy.deepcopy(observations),
        "cached_alias_count": 2,
        "helper_alias_replacement_count": 2,
        "all_cached_aliases_same_sentinel": True,
        "before_matching_verified": True,
        "after_matching_verified": True,
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
        **previous.worker_failure_evidence(
            family, returncode, stdout, stderr,
            timed_out=timed_out, message=message,
        ),
        "schema": SCHEMA + "-native-owner-worker-failure",
        "native_owner_worker_sha256": NATIVE_OWNER_WORKER_SHA256,
        "previous_v9_owner_failure_qualifies_current_engine": False,
    }


def run_native_worker(family: str, expected: Mapping[str, str]) -> dict[str, Any]:
    require(family in CORE_FAMILIES
            and isinstance(expected, dict) and bool(expected),
            "an actual isolated independently owned V10 engine is required")
    validate_worker_source()
    payload = json.dumps(expected, ensure_ascii=True,
                         sort_keys=True, separators=(",", ":"))
    require(len(payload.encode("ascii")) <= 16 * 1024,
            "the actual V10 native-owner process arguments exceeded their bound")
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
        failure = worker_failure_evidence(
            family, None, error.stdout, error.stderr, timed_out=True,
            message="the genuine V10 native owner exceeded its 120-second limit",
        )
        raise NativeWorkerFailure(failure["failure_message"], failure) from error
    if (child.returncode != 0 or not 0 < len(child.stdout) <= MAX_WORKER_BYTES
            or child.stderr or len(child.stderr) > MAX_WORKER_BYTES):
        failure = worker_failure_evidence(
            family, child.returncode, child.stdout, child.stderr,
            message="the actual V10 native worker crashed, wrote stderr, "
            "or returned unsafe evidence",
        )
        raise NativeWorkerFailure(failure["failure_message"], failure)
    try:
        observed = core.decode_report(child.stdout, label="genuine V10 native owner")
        return validate_worker(observed, family, expected, allow_failure=True)
    except (AuditV10Error, previous.AuditV9Error, source_v6.AuditV6Error,
            UnicodeError, ValueError, TypeError, KeyError) as error:
        failure = worker_failure_evidence(
            family, child.returncode, child.stdout, child.stderr,
            message="the actual V10 native owner produced invalid proof: "
            + str(error),
        )
        raise NativeWorkerFailure(failure["failure_message"], failure) from error


def destination_name(value: Any) -> str:
    require(type(value) is str,
            "the exclusive V10 ownership destination must be exact text")
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts
            and "\\" not in value and "\x00" not in value
            and path.as_posix() == value
            and value in {REPORT_RELATIVE, FAILURE_RELATIVE},
            "only exact separate V10 native-owner pass/failure paths are allowed")
    return value


def verify_fresh_report_targets() -> None:
    for path in (REPORT_PATH, FAILURE_PATH):
        require(path.resolve(strict=False) == path
                and path.parent.is_dir() and not path.parent.is_symlink()
                and not path.exists() and not path.is_symlink(),
                "refusing to retry existing actual V10 ownership evidence: "
                + path.relative_to(ROOT).as_posix())
        destination_name(path.relative_to(ROOT).as_posix())


def _read_frozen(relative: str, expected: str) -> bytes:
    require(core.valid_sha256(expected),
            "an actual independently frozen V10 input fingerprint is required")
    maximum = MAX_REPORT_BYTES if relative.endswith((".gz", ".json")) else MAX_SOURCE_BYTES
    observed, payload = core.bounded_file(
        ROOT / relative, maximum=maximum,
        label="exact complete frozen V10 ownership history: " + relative,
        keep=True,
    )
    require(observed == expected and isinstance(payload, bytes),
            "an actual immutable V10 history input changed: " + relative)
    return payload


def validate_v8_owner_failure(document: Any) -> dict[str, Any]:
    return previous.validate_v8_owner_failure(document)


def validate_v9_owner_failure(document: Any) -> dict[str, Any]:
    require(isinstance(document, dict),
            "the actual frozen V9 native-owner failure is not complete JSON")
    expected = {
        "schema": "rebar-postfinal-current-build-proofs-v9-native-owner-failure",
        "status": "FAIL", "result": "FAIL", "mode": "diagnostic",
        "candidate_family": "RUST",
        "candidate_module": "candidates.rust_candidate",
        "stage": "before-original-edge",
        "native_worker_crashed": True,
        "refresh_protocol_path": V9_REFRESH_PROTOCOL_RELATIVE,
        "refresh_protocol_sha256": V9_REFRESH_PROTOCOL_SHA256,
        "original_edge_worker_started": False,
        "original_deep_worker_started": False,
        "passing_evidence_published": False,
        "campaign_qualified": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    for key, value in expected.items():
        require(document.get(key) == value,
                "the real pre-import V9 matcher-cache failure changed: " + key)
    failure = document.get("complete_actual_native_worker")
    require(isinstance(failure, dict)
            and failure.get("schema")
            == previous.SCHEMA + "-native-owner-worker-failure"
            and failure.get("status") == "FAIL"
            and failure.get("family") == "rust"
            and failure.get("candidate_module") == "candidates.rust_candidate"
            and failure.get("actual_returncode") == 1
            and failure.get("signal") is None
            and failure.get("timed_out") is False
            and failure.get("stdout_bytes") == 0
            and failure.get("stderr_bytes") == 203
            and failure.get("stdout_sha256") == EMPTY_STREAM_SHA256
            and failure.get("stderr_sha256") == V9_OWNER_STDERR_SHA256
            and failure.get("production_observations_invented") is False
            and failure.get("qualifies_current_engine") is False,
            "the complete genuine V9 cached-matcher failure streams were replaced")
    return {
        "path": V9_OWNER_FAILURE_RELATIVE,
        "sha256": V9_OWNER_FAILURE_SHA256,
        "status": "FAIL", "stage": "before-original-edge",
        "candidate_module": "candidates.rust_candidate",
        "actual_returncode": 1,
        "stdout_bytes": 0, "stderr_bytes": 203,
        "stdout_sha256": EMPTY_STREAM_SHA256,
        "stderr_sha256": V9_OWNER_STDERR_SHA256,
        "original_edge_worker_started": False,
        "qualifies_current_engine": False,
    }


def _synthetic_v9_owner_failure() -> dict[str, Any]:
    return {
        "schema": "rebar-postfinal-current-build-proofs-v9-native-owner-failure",
        "status": "FAIL", "result": "FAIL", "mode": "diagnostic",
        "candidate_family": "RUST",
        "candidate_module": "candidates.rust_candidate",
        "stage": "before-original-edge",
        "native_worker_crashed": True,
        "refresh_protocol_path": V9_REFRESH_PROTOCOL_RELATIVE,
        "refresh_protocol_sha256": V9_REFRESH_PROTOCOL_SHA256,
        "original_edge_worker_started": False,
        "original_deep_worker_started": False,
        "passing_evidence_published": False,
        "campaign_qualified": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        "complete_actual_native_worker": {
            "schema": previous.SCHEMA + "-native-owner-worker-failure",
            "status": "FAIL", "family": "rust",
            "candidate_module": "candidates.rust_candidate",
            "actual_returncode": 1, "signal": None, "timed_out": False,
            "stdout_bytes": 0, "stderr_bytes": 203,
            "stdout_sha256": EMPTY_STREAM_SHA256,
            "stderr_sha256": V9_OWNER_STDERR_SHA256,
            "production_observations_invented": False,
            "qualifies_current_engine": False,
        },
    }


def verify_history() -> dict[str, Any]:
    verify_runtime()
    for relative, expected in (
        (V9_BASE_RELATIVE, V9_BASE_SHA256),
        (V9_STRICT_RELATIVE, V9_STRICT_SHA256),
        (V9_PROOF_RELATIVE, V9_PROOF_SHA256),
        (V9_REFRESH_PROTOCOL_RELATIVE, V9_REFRESH_PROTOCOL_SHA256),
        (V9_OWNERSHIP_PROTOCOL_RELATIVE, V9_OWNERSHIP_PROTOCOL_SHA256),
        (PROTOCOL_RELATIVE, PROTOCOL_SHA256),
    ):
        _read_frozen(relative, expected)
    require(Path(previous.__file__).resolve()
            == (ROOT / V9_BASE_RELATIVE).resolve(),
            "the genuine immutable V9 cached-sentinel owner was substituted")
    historical = previous.verify_history()
    archived = _read_frozen(V9_OWNER_FAILURE_RELATIVE, V9_OWNER_FAILURE_SHA256)
    document, _ = refresh_v8.decode_archive(
        archived, "complete actual pre-edge V9 cached internal matcher failure",
    )
    return {
        **historical,
        "actual_v9_native_owner_failure": validate_v9_owner_failure(document),
        "historical_v9_owner_failure_qualifies_current_build": False,
    }


def candidate_free_self_test() -> dict[str, Any]:
    verify_runtime()
    core.ensure_candidate_free()
    inherited = previous.candidate_free_self_test()
    require(inherited.get("passed") is True
            and inherited.get("check_count", 0) >= 150,
            "the unchanged genuine V9 source-only sentinel controls failed")
    checks: list[dict[str, Any]] = []

    def accept(name: str, condition: Any) -> None:
        require(not any(row["name"] == name for row in checks),
                "a cached-matcher source-only V10 poison was repeated")
        checks.append({"name": name, "passed": bool(condition)})

    def reject(name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except (AuditV10Error, previous.AuditV9Error,
                source_v6.AuditV6Error, AssertionError,
                OSError, TypeError, ValueError, KeyError):
            accept(name, True)
        else:
            accept(name, False)

    effects = core.previous.BlockSelfTestEffects()
    with effects:
        for row in inherited["checks"]:
            accept("immutable-v9:" + row["name"], row.get("passed") is True)
        accept("use-only-the-genuine-direct-isolated-v10-trusted-root",
               bool(sys.path) and sys.path[0] == str(ROOT))
        accept("compile-only-the-complete-additive-v10-cache-safe-worker",
               isinstance(validate_worker_source(), ast.Module))
        accept("never-run-the-failing-v9-owner-worker-instead-of-v10",
               NATIVE_OWNER_WORKER != previous.NATIVE_OWNER_WORKER)
        accept("require-both-original-live-cpython-matcher-children",
               REQUIRED_MATCHER_DESCENDANTS == ("re._compiler", "re._parser"))
        accept("call-only-the-actual-original-stage07-cached-alias-helper",
               "stage07._poison_cached_module_aliases(" in NATIVE_OWNER_WORKER)
        accept("freeze-the-true-failed-v9-native-worker-archive",
               V9_OWNER_FAILURE_SHA256
               == "04e52f831534458e9af50ad3ab962d78ad43e6a8725cbfccfee37bf9c234f07c")
        accept("freeze-the-true-failed-v9-native-worker-stderr",
               V9_OWNER_STDERR_SHA256
               == "7cfcf842efd492372ee01c330db0fc632aac9182c5f5b45870c5286a3e841097")

        for family in CORE_FAMILIES:
            original, native = synthetic_worker(family)
            accept("validate-all-cached-matcher-guards:" + family,
                   validate_worker(copy.deepcopy(original), family, native)
                   ["stage07_matcher_descendant_guards"]
                   ["all_cached_aliases_same_sentinel"] is True)
            for actual_aliases in (0, 1):
                real_shape = copy.deepcopy(original)
                real_shape["stage07_matcher_descendant_guards"].update({
                    "cached_alias_count": actual_aliases,
                    "helper_alias_replacement_count": actual_aliases,
                })
                accept("preserve-the-genuine-nonnegative-real-alias-count:"
                       + family + ":" + str(actual_aliases),
                       validate_worker(real_shape, family, native)
                       ["stage07_matcher_descendant_guards"]
                       ["cached_alias_count"] == actual_aliases)

            def poison(label: str,
                       change: Callable[[dict[str, Any]], None]) -> None:
                changed = copy.deepcopy(original)
                change(changed)
                reject("reject-v10:" + family + ":" + label,
                       lambda: validate_worker(changed, family, native))

            poison("stale-v9-native-owner-worker",
                   lambda row: row.update({
                       "schema": previous.SCHEMA + "-native-owner-worker",
                   }))
            poison("missing-all-cached-matcher-observations",
                   lambda row: row.pop("stage07_matcher_descendant_guards"))
            for field, wrong in (
                ("stage07_source_sha256", "0" * 64),
                ("required_descendants", ["re._compiler"]),
                ("discovered_descendants", ["re._compiler"]),
                ("all_cached_aliases_same_sentinel", False),
                ("before_matching_verified", False),
                ("after_matching_verified", False),
                ("cached_alias_count", -1),
                ("helper_alias_replacement_count", 1),
            ):
                poison("forge-real-matcher-cache-evidence:" + field,
                       lambda row, field=field, wrong=wrong:
                       row["stage07_matcher_descendant_guards"].update({field: wrong}))
            for field in ("cached_alias_count", "helper_alias_replacement_count"):
                for wrong in (-1, False, True):
                    poison("reject-noninteger-or-negative-alias-count:"
                           + field + ":" + repr(wrong),
                           lambda row, field=field, wrong=wrong:
                           row["stage07_matcher_descendant_guards"].update({
                               field: wrong,
                           }))
            for phase in ("observations_before", "observations_after"):
                poison("remove-real-cached-matcher-phase:" + phase,
                       lambda row, phase=phase:
                       row["stage07_matcher_descendant_guards"][phase].pop())
                for index, name in enumerate(REQUIRED_MATCHER_DESCENDANTS):
                    for flag in MATCHER_GUARD_FLAGS:
                        poison("restore-cached-matcher:" + phase
                               + ":" + name + ":" + flag,
                               lambda row, phase=phase, index=index, flag=flag:
                               row["stage07_matcher_descendant_guards"]
                               [phase][index].update({flag: False}))
            for flag in SENTINEL_FLAGS:
                poison("forge-the-original-stage07-blocker:" + flag,
                       lambda row, flag=flag:
                       row["stage07_guard_sentinel"].update({flag: False}))
            for field in (
                "regex_guard_observations", "regex_guard_observations_after",
                "foreign_engine_guard_observations",
                "foreign_engine_guard_observations_after",
                "native_loader_guard_observations",
                "native_loader_guard_observations_after",
                "standard_pickle_checks",
            ):
                poison("drop-a-real-original-owner-observation:" + field,
                       lambda row, field=field: row[field].pop())
            for flag in (
                "stdlib_re_blocked", "cpython_sre_blocked",
                "third_party_regex_blocked", "cross_family_blocked",
                "foreign_dynamic_libraries_blocked",
            ):
                poison("disable-the-real-frozen-guard:" + flag,
                       lambda row, flag=flag: row["guard"].update({flag: False}))

        incident = _synthetic_v9_owner_failure()
        accept("preserve-the-real-203-byte-pre-edge-v9-failure-as-fail",
               validate_v9_owner_failure(copy.deepcopy(incident))["status"] == "FAIL")
        for key, wrong in (
            ("status", "PASS"), ("result", "PASS"),
            ("candidate_family", "ZIG"),
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
            forged[key] = wrong
            reject("reject-forged-real-v9-owner-failure:" + key,
                   lambda forged=forged: validate_v9_owner_failure(forged))
        for key, wrong in (
            ("status", "PASS"), ("family", "vm"),
            ("actual_returncode", 0), ("timed_out", True),
            ("stdout_bytes", 1), ("stderr_bytes", 202),
            ("stdout_sha256", "0" * 64), ("stderr_sha256", "0" * 64),
            ("production_observations_invented", True),
            ("qualifies_current_engine", True),
        ):
            forged = copy.deepcopy(incident)
            forged["complete_actual_native_worker"][key] = wrong
            reject("reject-forged-real-v9-worker-stream:" + key,
                   lambda forged=forged: validate_v9_owner_failure(forged))
        for value in (
            previous.REPORT_RELATIVE, previous.FAILURE_RELATIVE,
            "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V10.json",
            "performance/private-holdout.json",
            "../POSTFINAL-FROM-SCRATCH-AUDIT-V10.json",
            "/tmp/POSTFINAL-FROM-SCRATCH-AUDIT-V10.json",
        ):
            reject("reject-historical-or-forged-v10-owner-output:" + value,
                   lambda value=value: destination_name(value))
        for value in (REPORT_RELATIVE, FAILURE_RELATIVE):
            accept("authorize-only-the-distinct-v10-owner-output:" + value,
                   destination_name(value) == value)

    require(len(checks) >= 150 and all(row["passed"] for row in checks),
            "an actual cached Python regex matcher escaped a V10 source poison")
    require(effects.counts["processes"] == 0
            and effects.counts["files"] == 0
            and effects.counts["clocks"] == 0,
            "an isolated source-only V10 owner performed an external effect")
    core.ensure_candidate_free()
    verify_runtime()
    return {
        "schema": SCHEMA + "-self-test", "status": "PASS", "passed": True,
        "check_count": len(checks), "checks": checks,
        "immutable_v9_control_count": inherited["check_count"],
        "stage07_source_sha256": STAGE07_SHA256,
        "v9_native_owner_failure_sha256": V9_OWNER_FAILURE_SHA256,
        "v8_native_owner_failure_sha256": V8_OWNER_FAILURE_SHA256,
        "v5_reference_sha256": V5_REFERENCE_SHA256,
        "required_cached_python_matchers": list(REQUIRED_MATCHER_DESCENDANTS),
        "candidate_imports": 0,
        "subprocesses": effects.counts["processes"],
        "file_reads": effects.counts["files"],
        "file_writes": effects.counts["files"],
        "clock_samples": effects.counts["clocks"],
        "owned_source_count": 12, "owned_native_binary_count": 5,
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
    core.validate_v3_report(current, label="genuine cache-safe V10 native graph")
    graph = source_v6._validate_fresh_graph(current)
    core.ensure_candidate_free()
    observations: dict[str, dict[str, Any]] = {}
    failure: dict[str, Any] | None = None
    for family in CORE_FAMILIES:
        try:
            worker = run_native_worker(
                family, graph["native_sha256_by_family"][family],
            )
            observations[family] = worker
            if worker.get("status") != "PASS":
                failure = {
                    "schema": SCHEMA + "-actual-native-owner-failure",
                    "status": "FAIL", "family": family,
                    "actual_native_owner_worker": worker,
                    "production_observations_invented": False,
                    "qualifies_current_engine": False,
                }
                break
        except NativeWorkerFailure as error:
            failure = error.evidence
            break
    core.ensure_candidate_free()
    pickle_failures = sum(
        report["standard_pickle_failure_count"]
        for report in observations.values()
    )
    passed = (failure is None and len(observations) == len(CORE_FAMILIES)
              and pickle_failures == 0)
    source_digest, _ = core.bounded_file(
        SOURCE_PATH, maximum=MAX_SOURCE_BYTES,
        label="actual frozen independent cached-matcher-safe V10 owner source",
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
        "actual_v9_native_owner_failure": history[
            "actual_v9_native_owner_failure"
        ],
        "actual_v8_native_owner_failure": history[
            "actual_v8_native_owner_failure"
        ],
        "historical_v9_owner_failure_qualifies_current_build": False,
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
            family: report["public_type_ownership"]
            for family, report in observations.items()
        },
        "public_match_repr": observations,
        "match_repr_checks_per_family": 2,
        "verified_match_repr_checks": sum(
            report["match_repr_checks"] for report in observations.values()
        ),
        "standard_pickle_checks_per_family": 16,
        "standard_pickle_checks": sum(
            report["standard_pickle_check_count"]
            for report in observations.values()
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
            "previous_v9_owner_failure_preserved": True,
            "previous_v8_owner_failure_preserved": True,
            "historical_v9_owner_failure_qualifies_current_build": False,
            "historical_v8_owner_failure_qualifies_current_build": False,
            "previous_v7_reports_historical": True,
            "actual_edge_failures_preserved": True,
            "exact_current_owned_candidate_source_count": 12,
            "actual_current_native_binary_count": 5,
            "actual_native_matching_workers": (
                len(observations) + int(failure is not None
                                        and failure.get("family") not in observations)
            ),
            "genuine_public_pickle_checks": sum(
                report["standard_pickle_check_count"]
                for report in observations.values()
            ),
            "genuine_match_repr_checks": sum(
                report["match_repr_checks"] for report in observations.values()
            ),
            "actual_python_matching_guards_per_family": 13,
            "actual_native_loader_guards_per_family": 5,
            "exact_stage07_sentinel_checked_before_and_after": True,
            "all_cached_matcher_descendants_poisoned_before_and_after": True,
            "original_stage07_cached_alias_helper_used": True,
            "native_identity_is_independent_of_public_module": True,
            "candidate_imports": "isolated guarded subprocesses only",
            "mapped_binaries_hashed_against_static_elf": True,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
    })
    require(graph["source_count"] == 12 and graph["native_binary_count"] == 5,
            "the exact independently owned V10 source or native graph changed")
    if passed:
        require(report["verified_match_repr_checks"] == 6
                and report["standard_pickle_checks"] == 48,
                "a passing V10 owner weakened the complete native matching suite")
    else:
        require(failure is not None,
                "a failed V10 owner did not preserve an actual genuine failure")
    core.ensure_candidate_free()
    return report


def write_report(report: Mapping[str, Any], target: Path | None = None) -> str:
    require(isinstance(report, Mapping),
            "actual exclusively published V10 owner evidence must be complete")
    expected = REPORT_PATH if report.get("passed") is True else FAILURE_PATH
    chosen = expected if target is None else target
    require(isinstance(chosen, Path) and chosen.resolve(strict=False) == expected
            and expected.parent.is_dir() and not expected.parent.is_symlink(),
            "genuine V10 owner observations escaped their exact distinct path")
    destination_name(expected.relative_to(ROOT).as_posix())
    payload = core.canonical(report) + b"\n"
    require(0 < len(payload) <= MAX_REPORT_BYTES,
            "the complete actual V10 native-owner evidence exceeds its bound")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory = os.open(expected.parent, flags)
    try:
        require(stat.S_ISDIR(os.fstat(directory).st_mode),
                "the exclusive V10 owner parent is not a real safe directory")
        create = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        create |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(expected.name, create, 0o644, dir_fd=directory)
        try:
            remaining = memoryview(payload)
            while remaining:
                count = os.write(descriptor, remaining)
                require(count > 0, "an exclusive real V10 report was truncated")
                remaining = remaining[count:]
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
                    "a source-only V10 control must not select evidence output")
            report = candidate_free_self_test()
            sys.stdout.buffer.write(core.canonical(report) + b"\n")
            return 0
        verify_fresh_report_targets()
        report = audit()
        observed = write_report(report, options.output)
        result = {
            "schema": SCHEMA,
            "status": report["status"], "result": report["result"],
            "passed": report["passed"],
            "report": REPORT_RELATIVE if report["passed"] else FAILURE_RELATIVE,
            "report_sha256": observed,
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
            "actual_v9_native_owner_failure": report[
                "actual_v9_native_owner_failure"
            ],
            "actual_v8_native_owner_failure": report[
                "actual_v8_native_owner_failure"
            ],
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }
        sys.stdout.buffer.write(core.canonical(result) + b"\n")
        return int(not report["passed"])
    except (AuditV10Error, previous.AuditV9Error,
            previous.refresh_v8.ProofV8Error,
            previous.reference_v5.OfficialV5Error,
            source_v6.AuditV6Error, OSError,
            RuntimeError, TypeError, ValueError, KeyError,
            UnicodeError, subprocess.SubprocessError) as error:
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
