#!/usr/bin/env python3
"""Safely supply actual published report fingerprints to frozen V8 controllers."""

from __future__ import annotations

import argparse
import ast
import builtins
import contextlib
import copy
import hashlib
import importlib
import io
import json
import multiprocessing
import os
from pathlib import Path
import platform
import stat
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Callable, Iterator, Mapping
import unicodedata


ROOT = Path(__file__).resolve().parent.parent
PINNED_EXECUTABLE = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
SCHEMA = "rebar-postfinal-published-pins-v8"
SOURCE_RELATIVE = "tools/postfinal_published_pins_v8.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-PUBLISHED-PINS-V8.md"
PUBLISHED_PROTOCOL_SHA256 = (
    "2c5f69f928049c6f8e6d22a9fa7c60f3093948cc4e2a44c38bd197711e8d39f9"
)
MAX_FILE_BYTES = 32 * 1024 * 1024
FAMILIES = ("rust", "vm", "zig")
CANDIDATE_MODULES = {
    "rust": "candidates.rust_candidate",
    "vm": "candidates.vm_candidate",
    "zig": "candidates.zig_candidate",
}
BASE_SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v8.py"
BASE_SOURCE_SHA256 = (
    "14b8daeebfb620eafa778529f6bf11e1a4f48256dd010b25621f4e94666692c6"
)
BASE_REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V8.json"
STRICT_SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v8.py"
STRICT_SOURCE_SHA256 = (
    "bb22b1983c11a896d3639077050dfaac746876ccbb9e4909518fb33d19987c01"
)
STRICT_REPORT_RELATIVE = "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V8.json"
PROOF_SOURCE_RELATIVE = "tools/postfinal_current_build_proofs_v8.py"
PROOF_SOURCE_SHA256 = (
    "0f9e12847855797669206ea89de94948da66c29742d64820a625ce5a6570b313"
)
OWNERSHIP_PROTOCOL_RELATIVE = "candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V8.md"
OWNERSHIP_PROTOCOL_SHA256 = (
    "5c60e6ce63ff1e4c5593eaafe29971cb3557b1a0389dcd5cf41cfb00647bc399"
)
PROOF_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V8.md"
PROOF_PROTOCOL_SHA256 = (
    "76e66c091ae06ad56b8f4e22c76f4db44810cdb512b839201c9cc7cb83f4cfa0"
)
HISTORICAL_FAILURES = {
    "rust": (
        "3ffdb21d10f40deabd70fa1f408fa38ff2b027a2d269c4b75e607a05cefde3b8",
        16,
    ),
    "vm": (
        "2cce7c26d2487c8e400d2fd6b8cfbc81d4b734b08f7a8f356def910a9cbb385c",
        33,
    ),
    "zig": (
        "5fa7283942994139d531593cc1bdf25f5da48f6de424d7604ce2ce569100788a",
        16,
    ),
}

FROZEN_INPUTS = {
    "GOAL.md":
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    BASE_SOURCE_RELATIVE: BASE_SOURCE_SHA256,
    STRICT_SOURCE_RELATIVE: STRICT_SOURCE_SHA256,
    PROOF_SOURCE_RELATIVE: PROOF_SOURCE_SHA256,
    OWNERSHIP_PROTOCOL_RELATIVE: OWNERSHIP_PROTOCOL_SHA256,
    PROOF_PROTOCOL_RELATIVE: PROOF_PROTOCOL_SHA256,
    "tools/rust_v7_edge_oracle.py":
        "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca",
    "tools/rust_v8_deep_contract_oracle.py":
        "ba4b640d12444a5346d918a039d8a7a9fef0c78a54f6b66c6f0eb0c9dddbe978",
    "tools/rust_v8_multi_candidate_contract.py":
        "167f9d9114f95cd9c9821465339264f8b6eca9bf7f70b84774f4108f62f11a70",
}


class PublishedPinError(AssertionError):
    """An actual frozen source or published audit report is missing or unsafe."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise PublishedPinError(message)


def valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str) and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, allow_nan=False,
        sort_keys=True, separators=(",", ":"),
    ).encode("ascii")


def decode_json(raw: bytes, label: str) -> dict[str, Any]:
    def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(key not in result, label + " contains a duplicate JSON key")
            result[key] = value
        return result

    def reject_constant(value: str) -> Any:
        raise PublishedPinError(label + " contains non-finite JSON: " + value)

    try:
        document = json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique,
            parse_constant=reject_constant,
        )
    except (UnicodeError, ValueError, TypeError) as error:
        raise PublishedPinError(label + " is not complete strict JSON") from error
    require(isinstance(document, dict), label + " is not a complete JSON object")
    return document


def read_regular(path: Path, label: str) -> bytes:
    require(isinstance(path, Path) and path.is_absolute()
            and path.resolve() == path and not path.is_symlink(),
            label + " is not its exact canonical, regular path")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and 0 < before.st_size <= MAX_FILE_BYTES,
                label + " is not a nonempty bounded regular file")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = -1
            raw = stream.read(MAX_FILE_BYTES + 1)
            after = os.fstat(stream.fileno())
        require(len(raw) == before.st_size and len(raw) <= MAX_FILE_BYTES,
                label + " exceeded or changed its complete byte size")
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns),
                label + " changed during complete authentication")
        return raw
    finally:
        if descriptor != -1:
            os.close(descriptor)


def authenticate_frozen(relative: str, expected: str) -> bytes:
    require(relative in FROZEN_INPUTS and FROZEN_INPUTS[relative] == expected
            and valid_sha256(expected),
            "an unapproved or guessed immutable input was requested")
    raw = read_regular(ROOT / relative, "exact immutable V8 input " + relative)
    require(hashlib.sha256(raw).hexdigest() == expected,
            "a frozen V8 controller or protocol changed: " + relative)
    return raw


def verify_runtime() -> None:
    require(platform.python_implementation() == "CPython"
            and sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and Path(sys.executable).resolve() == PINNED_EXECUTABLE.resolve()
            and sys.flags.isolated == 1 and sys.dont_write_bytecode,
            "published pins require exact isolated CPython 3.14.6 with -I -B")
    require(os.environ.get("PYTHONDONTWRITEBYTECODE") == "1"
            and unicodedata.unidata_version == "16.0.0",
            "published pins require disabled bytecode and pinned Unicode 16")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a published-pin parent must never import a candidate")


def validated_pins(
    mode: str, base_report: Any, strict_report: Any, module: Any,
) -> dict[str, Any]:
    require(mode in {"strict-audit", "qualified-edge", "qualified-deep"},
            "only unchanged strict, qualified edge, and qualified deep are authorized")
    require(valid_sha256(base_report),
            "the actual exclusively published passing base report hash is required")
    require(base_report not in {
        BASE_SOURCE_SHA256, STRICT_SOURCE_SHA256, PROOF_SOURCE_SHA256,
        OWNERSHIP_PROTOCOL_SHA256, PROOF_PROTOCOL_SHA256,
    }, "an immutable source or protocol is not an actual passing report")
    if mode == "strict-audit":
        require(strict_report is None and module is None,
                "strict audit accepts exactly one real base report and no candidate")
    else:
        require(valid_sha256(strict_report),
                "the actual exclusively published passing strict report hash is required")
        require(strict_report not in {
            base_report, BASE_SOURCE_SHA256, STRICT_SOURCE_SHA256,
            PROOF_SOURCE_SHA256, OWNERSHIP_PROTOCOL_SHA256,
            PROOF_PROTOCOL_SHA256,
        }, "a source, base report, or protocol cannot replace the strict report")
        require(module in CANDIDATE_MODULES.values(),
                "qualified correctness requires exactly one owned native candidate")
    return {
        "mode": mode, "base_report": base_report,
        "strict_report": strict_report, "module": module,
    }


def authenticate_report(relative: str, expected: str) -> dict[str, Any]:
    require(relative in {BASE_REPORT_RELATIVE, STRICT_REPORT_RELATIVE}
            and valid_sha256(expected),
            "only exact actually published V8 all-family reports are authorized")
    raw = read_regular(ROOT / relative, "complete published V8 report " + relative)
    require(hashlib.sha256(raw).hexdigest() == expected,
            "the actual complete published V8 report differs from its explicit hash")
    document = decode_json(raw, "complete authentic published V8 report")
    require(raw == canonical(document) + b"\n" or raw == canonical(document),
            "the published report is not its original strict canonical JSON")
    return document


def import_frozen(name: str, relative: str, digest: str) -> Any:
    authenticate_frozen(relative, digest)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    module = importlib.import_module(name)
    require(Path(module.__file__).resolve() == ROOT / relative,
            "a different immutable V8 controller was substituted: " + name)
    require(hashlib.sha256(read_regular(
        ROOT / relative, "rechecked immutable V8 controller " + relative
    )).hexdigest() == digest,
            "an immutable V8 controller changed while it was imported")
    verify_runtime()
    return module


def validate_base_shape(document: Any, expected_digest: str) -> None:
    require(valid_sha256(expected_digest) and isinstance(document, dict),
            "a published V8 base report is not a fully pinned object")
    for key, value in {
        "schema": "rebar-postfinal-from-scratch-audit-v8",
        "postfinal_schema": "rebar-postfinal-from-scratch-audit-v8",
        "status": "PASS", "result": "PASS", "passed": True,
        "audit_source_path": BASE_SOURCE_RELATIVE,
        "audit_source_sha256": BASE_SOURCE_SHA256,
        "native_ownership_protocol_path": OWNERSHIP_PROTOCOL_RELATIVE,
        "native_ownership_protocol_sha256": OWNERSHIP_PROTOCOL_SHA256,
        "historical_v7_results_qualify_current_build": False,
        "historical_first_campaign_failure_preserved": True,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": 12,
        "verified_native_role_count": 5,
        "verified_match_repr_checks": 6,
        "standard_pickle_checks_per_family": 16,
        "standard_pickle_checks": 48,
        "standard_pickle_failure_count": 0,
    }.items():
        require(document.get(key) == value,
                "the complete published base report changed: " + key)
    workers = document.get("actual_native_owner_workers")
    require(isinstance(workers, dict) and set(workers) == set(FAMILIES),
            "the passing base report omitted an actual independent native owner")
    historical = document.get("historical_current_build_edge_failures")
    require(isinstance(historical, dict) and set(historical) == set(FAMILIES),
            "the passing base report omitted a real historical edge failure")
    source_paths = document.get("verified_candidate_source_paths")
    require(isinstance(source_paths, list) and len(source_paths) == 12
            and len(set(source_paths)) == 12,
            "the passing base report lost its exact 12-source denominator")
    native = document.get("native_sha256_by_family")
    require(isinstance(native, dict) and set(native) == set(FAMILIES)
            and sum(len(rows) for rows in native.values()
                    if isinstance(rows, dict)) == 5,
            "the passing base report lost its exact five real ELF roles")
    for family in FAMILIES:
        worker = workers[family]
        require(isinstance(worker, dict)
                and worker.get("family") == family
                and worker.get("candidate_module") == CANDIDATE_MODULES[family]
                and worker.get("status") == "PASS"
                and worker.get("passed") is True
                and worker.get("standard_pickle_check_count") == 16
                and worker.get("standard_pickle_failure_count") == 0
                and worker.get("regex_guard_count") == 13
                and worker.get("persistent_cross_engine_guard") is True
                and worker.get("genuine_matching_executed") is True,
                "the passing base report lost an actual poisoned native owner: "
                + family)
        failure = historical[family]
        archive_sha256, count = HISTORICAL_FAILURES[family]
        require(isinstance(failure, dict)
                and failure.get("status") == "FAIL"
                and failure.get("qualifies_current_engine") is False
                and failure.get("family") == family
                and failure.get("archive_sha256") == archive_sha256
                and failure.get("failed") == count
                and failure.get("failure_rows_preserved") == count
                and failure.get("checks") == 223198
                and failure.get("category_count") == 49,
                "the passing base report concealed an actual original failure: "
                + family)


def authenticate_production_sources() -> None:
    verify_runtime()
    protocol = read_regular(ROOT / PROTOCOL_RELATIVE,
                            "actual independently frozen V8 published-pin protocol")
    require(hashlib.sha256(protocol).hexdigest() == PUBLISHED_PROTOCOL_SHA256,
            "the independently frozen V8 published-pin protocol was changed")
    for relative, digest in FROZEN_INPUTS.items():
        authenticate_frozen(relative, digest)


def load_actual_base(base_digest: str) -> tuple[Any, Any, dict[str, Any], dict[str, Any]]:
    require(valid_sha256(base_digest), "the actual passing base hash was not supplied")
    owner = import_frozen(
        "tools.postfinal_from_scratch_audit_v8",
        BASE_SOURCE_RELATIVE, BASE_SOURCE_SHA256,
    )
    strict = import_frozen(
        "tools.postfinal_no_delegation_audit_v8",
        STRICT_SOURCE_RELATIVE, STRICT_SOURCE_SHA256,
    )
    require(strict.independent is owner
            and strict.BASE_SOURCE_SHA256 == BASE_SOURCE_SHA256
            and strict.BASE_REPORT_SHA256 is None
            and tuple(owner.CORE_FAMILIES) == FAMILIES
            and owner.PROTOCOL_RELATIVE == OWNERSHIP_PROTOCOL_RELATIVE
            and owner.PROTOCOL_SHA256 == OWNERSHIP_PROTOCOL_SHA256,
            "the frozen V8 source/strict controller graph or absent report pin changed")
    document = authenticate_report(BASE_REPORT_RELATIVE, base_digest)
    validate_base_shape(document, base_digest)
    graph = strict.validate_base_report(document, {
        "base_source": BASE_SOURCE_SHA256,
        "base_report": base_digest,
    })
    require(graph["source_count"] == 12 and graph["native_binary_count"] == 5,
            "original strict validation lost the 12-source/five-ELF graph")
    return owner, strict, document, graph


@contextlib.contextmanager
def publish_only_missing_pin(module: Any, attribute: str, digest: str) -> Iterator[None]:
    authorized = {
        "tools.postfinal_no_delegation_audit_v8": {"BASE_REPORT_SHA256"},
        "tools.postfinal_current_build_proofs_v8": {
            "V8_SOURCE_REPORT_SHA256", "V8_STRICT_REPORT_SHA256",
        },
    }
    require(getattr(module, "__name__", None) in authorized
            and attribute in authorized[module.__name__]
            and valid_sha256(digest)
            and getattr(module, attribute, object()) is None,
            "only an actually published, originally absent V8 report pin may be set")
    setattr(module, attribute, digest)
    try:
        require(getattr(module, attribute) == digest,
                "the actual in-memory report pin did not remain immutable")
        yield
    finally:
        setattr(module, attribute, None)


def preflight_strict_target(strict: Any) -> None:
    require(strict.SCHEMA == "rebar-postfinal-no-delegation-audit-v8"
            and strict.SOURCE_RELATIVE == STRICT_SOURCE_RELATIVE
            and strict.REPORT_RELATIVE == STRICT_REPORT_RELATIVE,
            "the immutable original strict source or exclusive target changed")
    strict.verify_fresh_report_target(strict.REPORT_PATH)


def run_strict_audit(base_digest: str) -> int:
    validated_pins("strict-audit", base_digest, None, None)
    authenticate_production_sources()
    owner, strict, _, _ = load_actual_base(base_digest)
    require(strict.independent is owner,
            "the passing base and original strict native-owner graphs diverged")
    preflight_strict_target(strict)
    with publish_only_missing_pin(strict, "BASE_REPORT_SHA256", base_digest):
        require(strict.required_pins() == {
            "base_source": BASE_SOURCE_SHA256,
            "base_report": base_digest,
        }, "the genuine strict audit did not accept only its actual published base")
        preflight_strict_target(strict)
        return strict.main(["--audit"])


def validate_actual_qualified_reports(
    base_digest: str, strict_digest: str,
) -> tuple[Any, Any, Any, dict[str, Any]]:
    owner, strict, _, graph = load_actual_base(base_digest)
    strict_document = authenticate_report(STRICT_REPORT_RELATIVE, strict_digest)
    proof = import_frozen(
        "tools.postfinal_current_build_proofs_v8",
        PROOF_SOURCE_RELATIVE, PROOF_SOURCE_SHA256,
    )
    require(proof.REFRESH_PROTOCOL_SHA256 == PROOF_PROTOCOL_SHA256
            and proof.V8_SOURCE_AUDIT_SHA256 == BASE_SOURCE_SHA256
            and proof.V8_STRICT_AUDIT_SHA256 == STRICT_SOURCE_SHA256
            and proof.V8_SOURCE_REPORT_SHA256 is None
            and proof.V8_STRICT_REPORT_SHA256 is None,
            "the immutable V8 proof source, actual protocols, or absent pins changed")
    approved = proof.authenticate_v8_audits(owner, {
        "source_audit": BASE_SOURCE_SHA256,
        "source_report": base_digest,
        "strict_audit": STRICT_SOURCE_SHA256,
        "strict_report": strict_digest,
    })
    require(approved["graph"] == graph
            and approved["strict"] == strict_document
            and strict.BASE_REPORT_SHA256 is None,
            "the actual independently passing all-family strict graph was substituted")
    return owner, strict, proof, approved


def preflight_proof_targets(proof: Any, mode: str, family: str) -> None:
    require(family in FAMILIES
            and proof.FAMILIES[family]["module"] == CANDIDATE_MODULES[family],
            "the immutable qualified proof substituted an owned native family")
    if mode == "qualified-edge":
        for path in (
            proof.edge_target(family, True, True),
            proof.edge_target(family, True, False),
            proof.native_owner_failure_target(family, True),
            proof.producer_failure_target(family, True, deep=False),
            proof.invalidated_original_target(family, True, deep=False),
        ):
            proof.fresh_target(path, ROOT / "candidates/evidence", path.name)
        return
    require(mode == "qualified-deep",
            "an unqualified or unsupported proof destination was requested")
    for path in (
        proof.deep_target(family, True),
        proof.deep_target(family, False),
        proof.producer_failure_target(family, True, deep=True),
        proof.invalidated_original_target(family, True, deep=True),
    ):
        proof.fresh_target(path, ROOT / "candidates/audits", path.name)
    owner_failure = proof.native_owner_failure_target(family, True)
    proof.fresh_target(owner_failure, ROOT / "candidates/evidence", owner_failure.name)
    edge_path = proof.edge_target(family, True, True)
    raw = proof.read_regular(edge_path, "actual required passing qualified V8 edge")
    snapshot = proof.snapshot_family(family)
    _, edge, passed = proof.validate_original_edge(
        raw, edge_path, family, snapshot, proof.load_contract(),
    )
    require(passed and edge.get("failed") == 0
            and edge.get("checks") == 223198
            and edge.get("category_count") == 49,
            "a diagnostic, failed, or incomplete edge cannot run the deep contract")


def run_qualified_proof(
    mode: str, base_digest: str, strict_digest: str, module: str,
) -> int:
    pins = validated_pins(mode, base_digest, strict_digest, module)
    authenticate_production_sources()
    owner, strict, proof, approved = validate_actual_qualified_reports(
        pins["base_report"], pins["strict_report"],
    )
    require(owner is strict.independent
            and approved["pins"]["source_report"] == base_digest
            and approved["pins"]["strict_report"] == strict_digest,
            "published all-family audits were substituted before qualification")
    family = next(name for name in FAMILIES
                  if CANDIDATE_MODULES[name] == module)
    preflight_proof_targets(proof, mode, family)
    with (
        publish_only_missing_pin(
            proof, "V8_SOURCE_REPORT_SHA256", base_digest,
        ),
        publish_only_missing_pin(
            proof, "V8_STRICT_REPORT_SHA256", strict_digest,
        ),
    ):
        require(proof.required_campaign_pins() == {
            "source_audit": BASE_SOURCE_SHA256,
            "source_report": base_digest,
            "strict_audit": STRICT_SOURCE_SHA256,
            "strict_report": strict_digest,
        }, "the frozen proof received an unobserved published report fingerprint")
        preflight_proof_targets(proof, mode, family)
        return proof.main(["--" + mode, "--module", module])


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    counts = {
        "candidate_import_attempts_blocked": 0,
        "worker_attempts_blocked": 0,
        "clock_attempts_blocked": 0,
        "write_attempts_blocked": 0,
        "evidence_read_attempts_blocked": 0,
        "unauthorized_read_attempts_blocked": 0,
    }
    originals: list[tuple[Any, str, Any]] = []
    allowed = {
        (ROOT / relative).resolve()
        for relative in FROZEN_INPUTS if not relative.startswith("candidates/")
    }
    allowed.update({(ROOT / SOURCE_RELATIVE).resolve(),
                    (ROOT / PROTOCOL_RELATIVE).resolve()})

    def replace(target: Any, name: str, value: Any) -> None:
        if hasattr(target, name):
            originals.append((target, name, getattr(target, name)))
            setattr(target, name, value)

    def blocked(kind: str, label: str) -> Callable[..., Any]:
        def reject(*args: Any, **kwargs: Any) -> Any:
            del args, kwargs
            counts[kind] += 1
            raise PublishedPinError("source-only published pins forbid " + label)

        return reject

    def authorized(path: Any) -> bool:
        try:
            return Path(os.fsdecode(path)).resolve() in allowed
        except (OSError, TypeError, ValueError):
            return False

    original_os_open = os.open

    def guarded_os_open(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
        write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
        write_flags |= getattr(os, "O_APPEND", 0)
        if flags & write_flags:
            return blocked("write_attempts_blocked", "filesystem writes")()
        if isinstance(path, int) or not authorized(path):
            kind = ("evidence_read_attempts_blocked"
                    if not isinstance(path, int)
                    and any(part in {"candidates", "performance", "holdout"}
                            for part in Path(os.fsdecode(path)).parts)
                    else "unauthorized_read_attempts_blocked")
            return blocked(kind, "report, holdout, or unrelated reads")()
        return original_os_open(path, flags, *args, **kwargs)

    original_open = builtins.open

    def guarded_open(path: Any, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if any(character in mode for character in "wax+"):
            return blocked("write_attempts_blocked", "filesystem writes")()
        if isinstance(path, int):
            return original_open(path, mode, *args, **kwargs)
        if not authorized(path):
            kind = ("evidence_read_attempts_blocked"
                    if isinstance(path, (str, bytes, os.PathLike))
                    and any(part in {"candidates", "performance", "holdout"}
                            for part in Path(os.fsdecode(path)).parts)
                    else "unauthorized_read_attempts_blocked")
            return blocked(kind, "report, holdout, or unrelated reads")()
        return original_open(path, mode, *args, **kwargs)

    forbidden = {
        "candidates", "regex", "_regex", "pcre", "pcre2", "re2",
        "hyperscan", "rure", "onig", "oniguruma",
    }
    original_import = builtins.__import__
    original_import_module = importlib.import_module

    def guarded_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if isinstance(name, str) and name.partition(".")[0] in forbidden:
            return blocked("candidate_import_attempts_blocked",
                           "candidate or external matching-engine imports")()
        return original_import(name, *args, **kwargs)

    def guarded_import_module(name: str, package: str | None = None) -> Any:
        if isinstance(name, str) and name.partition(".")[0] in forbidden:
            return blocked("candidate_import_attempts_blocked",
                           "importlib candidate or matching-engine imports")()
        return original_import_module(name, package)

    replace(os, "open", guarded_os_open)
    replace(builtins, "open", guarded_open)
    replace(io, "open", guarded_open)
    replace(builtins, "__import__", guarded_import)
    replace(importlib, "import_module", guarded_import_module)
    for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                 "perf_counter", "perf_counter_ns", "process_time",
                 "process_time_ns", "thread_time", "thread_time_ns",
                 "clock_gettime", "clock_gettime_ns"):
        replace(time, name, blocked("clock_attempts_blocked", "clock " + name))
    for target, name in ((subprocess, "run"), (subprocess, "Popen"),
                         (threading.Thread, "start"),
                         (multiprocessing.Process, "start"),
                         (tempfile, "mkdtemp"),
                         (tempfile, "TemporaryDirectory")):
        replace(target, name, blocked("worker_attempts_blocked", "worker " + name))
    for name in ("fork", "posix_spawn", "posix_spawnp", "system"):
        replace(os, name, blocked("worker_attempts_blocked", "process " + name))
    for name in ("unlink", "remove", "rename", "replace", "mkdir", "makedirs",
                 "rmdir", "removedirs", "chmod", "chown", "link", "symlink",
                 "truncate", "utime"):
        replace(os, name, blocked("write_attempts_blocked", "filesystem " + name))
    for name in ("write_bytes", "write_text", "touch", "mkdir", "unlink",
                 "rename", "replace", "rmdir", "chmod", "hardlink_to",
                 "symlink_to"):
        replace(Path, name, blocked("write_attempts_blocked", "path " + name))
    try:
        yield counts
    finally:
        for target, name, value in reversed(originals):
            setattr(target, name, value)


def rejected(name: str, action: Callable[[], Any]) -> dict[str, Any]:
    try:
        action()
    except (PublishedPinError, AssertionError, OSError, TypeError,
            ValueError, KeyError, UnicodeError):
        return {"name": name, "passed": True}
    return {"name": name, "passed": False}


def synthetic_digest(label: str) -> str:
    return hashlib.sha256(("source-only-v8-published-pin:" + label).encode(
        "ascii"
    )).hexdigest()


def synthetic_base_report() -> tuple[dict[str, Any], str]:
    digest = synthetic_digest("actual-base-report")
    native = {
        "rust": {
            "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so":
                synthetic_digest("rust-bridge"),
            "candidates/_rust_engine.so": synthetic_digest("rust-engine"),
        },
        "vm": {
            "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so":
                synthetic_digest("vm-native"),
        },
        "zig": {
            "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so":
                synthetic_digest("zig-bridge"),
            "candidates/_zig_probe.so": synthetic_digest("zig-engine"),
        },
    }
    source_paths = [
        "candidates/rust_candidate.py", "candidates/rust/py_bridge.c",
        "candidates/rust/src/lib.rs", "candidates/rust/src/search.rs",
        "candidates/rust/src/newline.rs", "candidates/rust/src/stack.rs",
        "candidates/rust/src/unicode_tables.rs",
        "candidates/vm_candidate.py", "candidates/_vm_native.c",
        "candidates/zig_candidate.py", "candidates/zig/py_bridge.c",
        "candidates/zig/mini_regex.zig",
    ]
    workers = {
        family: {
            "family": family,
            "candidate_module": CANDIDATE_MODULES[family],
            "status": "PASS", "result": "PASS", "passed": True,
            "standard_pickle_check_count": 16,
            "standard_pickle_failure_count": 0,
            "regex_guard_count": 13,
            "persistent_cross_engine_guard": True,
            "genuine_matching_executed": True,
        }
        for family in FAMILIES
    }
    history = {
        family: {
            "status": "FAIL", "qualifies_current_engine": False,
            "family": family,
            "archive_sha256": HISTORICAL_FAILURES[family][0],
            "failed": HISTORICAL_FAILURES[family][1],
            "failure_rows_preserved": HISTORICAL_FAILURES[family][1],
            "checks": 223198, "category_count": 49,
        }
        for family in FAMILIES
    }
    report = {
        "schema": "rebar-postfinal-from-scratch-audit-v8",
        "postfinal_schema": "rebar-postfinal-from-scratch-audit-v8",
        "status": "PASS", "result": "PASS", "passed": True,
        "audit_source_path": BASE_SOURCE_RELATIVE,
        "audit_source_sha256": BASE_SOURCE_SHA256,
        "native_ownership_protocol_path": OWNERSHIP_PROTOCOL_RELATIVE,
        "native_ownership_protocol_sha256": OWNERSHIP_PROTOCOL_SHA256,
        "historical_v7_results_qualify_current_build": False,
        "historical_first_campaign_failure_preserved": True,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": 12,
        "verified_candidate_source_paths": source_paths,
        "verified_native_role_count": 5,
        "native_sha256_by_family": native,
        "verified_match_repr_checks": 6,
        "standard_pickle_checks_per_family": 16,
        "standard_pickle_checks": 48,
        "standard_pickle_failure_count": 0,
        "actual_native_owner_workers": workers,
        "historical_current_build_edge_failures": history,
    }
    return report, digest


def candidate_free_self_test() -> dict[str, Any]:
    verify_runtime()
    checks: list[dict[str, Any]] = []

    def accept(name: str, condition: Any) -> None:
        checks.append({"name": name, "passed": bool(condition)})

    with source_only_boundary() as effects:
        for relative, digest in FROZEN_INPUTS.items():
            if relative.startswith("candidates/"):
                accept("preserve-immutable-evidence-protocol-pin-without-reading:"
                       + relative, valid_sha256(digest))
                continue
            raw = authenticate_frozen(relative, digest)
            accept("authenticate-actual-immutable-source:" + relative,
                   hashlib.sha256(raw).hexdigest() == digest)
            if relative.endswith(".py"):
                accept("parse-immutable-source-without-importing:" + relative,
                       isinstance(ast.parse(raw.decode("utf-8"),
                                            filename=relative), ast.Module))
        source = read_regular(ROOT / SOURCE_RELATIVE,
                              "source-only immutable published-pin launcher")
        own_tree = ast.parse(source.decode("utf-8"), filename=SOURCE_RELATIVE)
        accept("parse-additive-published-pin-launcher-without-executing",
               isinstance(own_tree, ast.Module))
        immutable_pin_function = next((
            node for node in own_tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "publish_only_missing_pin"
        ), None)
        accept("require-one-transparent-authorized-original-pin-context",
               isinstance(immutable_pin_function, ast.FunctionDef))
        if isinstance(immutable_pin_function, ast.FunctionDef):
            calls = [
                node for node in ast.walk(immutable_pin_function)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "setattr"
            ]
            accept("allow-only-temporary-original-digest-assignment-and-restoration",
                   len(calls) == 2
                   and all(len(call.args) == 3
                           and isinstance(call.args[1], ast.Name)
                           and call.args[1].id == "attribute"
                           for call in calls))
        protocol = read_regular(ROOT / PROTOCOL_RELATIVE,
                                "source-only immutable published-pin protocol")
        accept("authenticate-exact-independent-published-pin-protocol",
               hashlib.sha256(protocol).hexdigest() == PUBLISHED_PROTOCOL_SHA256)
        for token in (
            BASE_SOURCE_SHA256.encode("ascii"),
            STRICT_SOURCE_SHA256.encode("ascii"),
            PROOF_SOURCE_SHA256.encode("ascii"),
            OWNERSHIP_PROTOCOL_SHA256.encode("ascii"),
            PROOF_PROTOCOL_SHA256.encode("ascii"),
            b"BASE_REPORT_SHA256", b"V8_SOURCE_REPORT_SHA256",
            b"V8_STRICT_REPORT_SHA256", b"223,198", b"393", b"48",
            b"NOT MEASURED", b"NOT ACCESSED",
        ):
            accept("preserve-explicit-immutable-protocol-contract:"
                   + token.decode("ascii"), token in protocol)
        accept("preserve-exact-three-real-historical-edge-failure-pins",
               HISTORICAL_FAILURES == {
                   "rust": (
                       "3ffdb21d10f40deabd70fa1f408fa38ff2b027a2d269c4b75e607a05cefde3b8",
                       16,
                   ),
                   "vm": (
                       "2cce7c26d2487c8e400d2fd6b8cfbc81d4b734b08f7a8f356def910a9cbb385c",
                       33,
                   ),
                   "zig": (
                       "5fa7283942994139d531593cc1bdf25f5da48f6de424d7604ce2ce569100788a",
                       16,
                   ),
               })
        base_document, base_digest = synthetic_base_report()
        strict_digest = synthetic_digest("actual-strict-report")
        validate_base_shape(base_document, base_digest)
        accept("accept-complete-in-memory-three-owner-base-shape", True)
        accept("accept-in-memory-explicit-published-base-pin",
               validated_pins("strict-audit", base_digest, None, None)["base_report"]
               == base_digest)
        strict_control = type("SyntheticSourceOnlyPin", (), {
            "__name__": "tools.postfinal_no_delegation_audit_v8",
            "BASE_REPORT_SHA256": None,
        })()
        with publish_only_missing_pin(
            strict_control, "BASE_REPORT_SHA256", base_digest,
        ):
            accept("set-only-authenticated-original-absent-strict-pin-in-memory",
                   strict_control.BASE_REPORT_SHA256 == base_digest)
        accept("restore-original-absent-strict-report-pin-after-source-control",
               strict_control.BASE_REPORT_SHA256 is None)
        proof_control = type("SyntheticProofSourceOnlyPin", (), {
            "__name__": "tools.postfinal_current_build_proofs_v8",
            "V8_SOURCE_REPORT_SHA256": None,
            "V8_STRICT_REPORT_SHA256": None,
        })()
        with (
            publish_only_missing_pin(
                proof_control, "V8_SOURCE_REPORT_SHA256", base_digest,
            ),
            publish_only_missing_pin(
                proof_control, "V8_STRICT_REPORT_SHA256", strict_digest,
            ),
        ):
            accept("set-only-two-original-absent-qualified-report-pins",
                   proof_control.V8_SOURCE_REPORT_SHA256 == base_digest
                   and proof_control.V8_STRICT_REPORT_SHA256 == strict_digest)
        accept("restore-both-original-absent-qualified-report-pins",
               proof_control.V8_SOURCE_REPORT_SHA256 is None
               and proof_control.V8_STRICT_REPORT_SHA256 is None)

        def enter_control(module: Any, attribute: str, digest: str) -> None:
            with publish_only_missing_pin(module, attribute, digest):
                pass

        for attribute in (
            "BASE_SOURCE_SHA256", "PROTOCOL_SHA256", "main",
            "validate_worker", "NATIVE_OWNER_WORKER", "sys.modules",
            "__file__", "__name__",
        ):
            checks.append(rejected(
                "reject-matcher-source-guard-or-module-replacement:" + attribute,
                lambda field=attribute: enter_control(
                    strict_control, field, base_digest,
                ),
            ))
        occupied = type("OccupiedSourceOnlyPin", (), {
            "__name__": "tools.postfinal_no_delegation_audit_v8",
            "BASE_REPORT_SHA256": synthetic_digest("already-published"),
        })()
        checks.append(rejected(
            "reject-existing-conflicting-actual-report-pin",
            lambda: enter_control(occupied, "BASE_REPORT_SHA256", base_digest),
        ))
        for family in FAMILIES:
            module = CANDIDATE_MODULES[family]
            for mode in ("qualified-edge", "qualified-deep"):
                pins = validated_pins(mode, base_digest, strict_digest, module)
                accept("accept-explicit-in-memory-independent-proof-pins:"
                       + family + ":" + mode,
                       pins["module"] == module
                       and pins["base_report"] == base_digest
                       and pins["strict_report"] == strict_digest)
        for replacement in (
            None, "", "0", "A" * 64, "z" * 64,
            BASE_SOURCE_SHA256, STRICT_SOURCE_SHA256,
            PROOF_SOURCE_SHA256, OWNERSHIP_PROTOCOL_SHA256,
            PROOF_PROTOCOL_SHA256,
        ):
            for mode in ("strict-audit", "qualified-edge", "qualified-deep"):
                module = None if mode == "strict-audit" else CANDIDATE_MODULES["rust"]
                other = None if mode == "strict-audit" else strict_digest
                checks.append(rejected(
                    "reject-missing-invented-or-source-base-pin:"
                    + mode + ":" + repr(replacement),
                    lambda value=replacement, mode=mode, other=other, module=module:
                        validated_pins(mode, value, other, module),
                ))
        for replacement in (
            None, "", "0", "A" * 64, "z" * 64, base_digest,
            BASE_SOURCE_SHA256, STRICT_SOURCE_SHA256, PROOF_SOURCE_SHA256,
            OWNERSHIP_PROTOCOL_SHA256, PROOF_PROTOCOL_SHA256,
        ):
            for mode in ("qualified-edge", "qualified-deep"):
                checks.append(rejected(
                    "reject-missing-repeated-or-source-strict-pin:"
                    + mode + ":" + repr(replacement),
                    lambda value=replacement, mode=mode:
                        validated_pins(mode, base_digest, value,
                                       CANDIDATE_MODULES["rust"]),
                ))
        for foreign in (None, "", "re", "_sre", "regex",
                        "candidates.ast_candidate", "candidates.foreign_candidate"):
            for mode in ("qualified-edge", "qualified-deep"):
                checks.append(rejected(
                    "reject-foreign-or-absent-candidate:"
                    + mode + ":" + repr(foreign),
                    lambda value=foreign, mode=mode:
                        validated_pins(mode, base_digest, strict_digest, value),
                ))
        for key, value in (
            ("schema", "forged"), ("postfinal_schema", "forged"),
            ("status", "FAIL"), ("result", "FAIL"), ("passed", False),
            ("audit_source_path", "tools/foreign.py"),
            ("audit_source_sha256", "0" * 64),
            ("native_ownership_protocol_path", "foreign.md"),
            ("native_ownership_protocol_sha256", "0" * 64),
            ("historical_v7_results_qualify_current_build", True),
            ("historical_first_campaign_failure_preserved", False),
            ("verified_core_family_count", 2),
            ("verified_distinct_pipeline_count", 3),
            ("verified_candidate_source_count", 11),
            ("verified_native_role_count", 4),
            ("verified_match_repr_checks", 5),
            ("standard_pickle_checks_per_family", 15),
            ("standard_pickle_checks", 47),
            ("standard_pickle_failure_count", 1),
        ):
            changed = copy.deepcopy(base_document)
            changed[key] = value
            checks.append(rejected(
                "reject-forged-or-incomplete-source-audit:" + key,
                lambda doc=changed: validate_base_shape(doc, base_digest),
            ))
        for family in FAMILIES:
            for key, value in (
                ("status", "FAIL"), ("passed", False),
                ("candidate_module", "candidates.foreign_candidate"),
                ("standard_pickle_check_count", 15),
                ("standard_pickle_failure_count", 1),
                ("regex_guard_count", 12),
                ("persistent_cross_engine_guard", False),
                ("genuine_matching_executed", False),
            ):
                changed = copy.deepcopy(base_document)
                changed["actual_native_owner_workers"][family][key] = value
                checks.append(rejected(
                    "reject-incomplete-native-owner:" + family + ":" + key,
                    lambda doc=changed: validate_base_shape(doc, base_digest),
                ))
            for key, value in (
                ("status", "PASS"), ("qualifies_current_engine", True),
                ("family", "foreign"), ("archive_sha256", "0" * 64),
                ("failed", 0), ("failure_rows_preserved", 0),
                ("checks", 223197), ("category_count", 48),
            ):
                changed = copy.deepcopy(base_document)
                changed["historical_current_build_edge_failures"][family][key] = value
                checks.append(rejected(
                    "reject-concealed-real-edge-failure:" + family + ":" + key,
                    lambda doc=changed: validate_base_shape(doc, base_digest),
                ))
        for mode in ("diagnostic-edge", "self-test", "campaign", "benchmark",
                     "holdout", "", "strict-audit;rm"):
            checks.append(rejected(
                "reject-unauthorized-production-mode:" + repr(mode),
                lambda value=mode: validated_pins(value, base_digest,
                                                   strict_digest,
                                                   CANDIDATE_MODULES["rust"]),
            ))
        for label, action in (
            ("builtin-candidate", lambda: builtins.__import__("candidates")),
            ("importlib-candidate",
             lambda: importlib.import_module("candidates.rust_candidate")),
            ("builtin-external-engine", lambda: builtins.__import__("regex")),
            ("importlib-external-engine", lambda: importlib.import_module("regex")),
            ("actual-base-report",
             lambda: read_regular(ROOT / BASE_REPORT_RELATIVE,
                                  "forbidden actual base report")),
            ("actual-strict-report",
             lambda: read_regular(ROOT / STRICT_REPORT_RELATIVE,
                                  "forbidden actual strict report")),
            ("performance-or-holdout",
             lambda: builtins.open(ROOT / "performance" / "holdout.json", "rb")),
            ("unrelated-read",
             lambda: builtins.open(ROOT / "README.md", "rb")),
            ("clock", lambda: time.perf_counter()),
            ("subprocess", lambda: subprocess.run(["forbidden"])),
            ("temporary-directory", lambda: tempfile.mkdtemp()),
            ("direct-path-write",
             lambda: (ROOT / "forbidden-published-pins").write_bytes(b"blocked")),
            ("file-delete", lambda: os.unlink(str(ROOT / "forbidden-remove"))),
            ("file-replace", lambda: os.replace("forbidden-a", "forbidden-b")),
        ):
            checks.append(rejected("enforce-genuine-source-only-boundary:" + label,
                                   action))
        accept("block-builtin-and-importlib-production-imports",
               effects["candidate_import_attempts_blocked"] >= 4)
        accept("never-load-a-candidate-during-source-controls",
               not any(name == "candidates" or name.startswith("candidates.")
                       for name in sys.modules))
        accept("enforce-more-than-one-hundred-real-source-poison-controls",
               len(checks) >= 100)
        require(all(item["passed"] for item in checks),
                "an immutable source, real report, or native-owner poison passed")
        require(len({item["name"] for item in checks}) == len(checks),
                "a published-pin source-only poison denominator was duplicated")
        blocked_counts = dict(effects)
    verify_runtime()
    return {
        "schema": SCHEMA + "-self-test", "status": "PASS", "passed": True,
        "check_count": len(checks), "checks": checks,
        "candidate_imports": 0, "subprocesses": 0,
        "file_writes": 0, "clock_samples": 0,
        "historical_evidence_reads": 0,
        "actual_audit_report_reads": 0,
        "synthetic_results_qualify_candidates": False,
        "immutable_base_source_sha256": BASE_SOURCE_SHA256,
        "immutable_strict_source_sha256": STRICT_SOURCE_SHA256,
        "immutable_proof_source_sha256": PROOF_SOURCE_SHA256,
        "published_protocol_path": PROTOCOL_RELATIVE,
        "published_protocol_sha256": PUBLISHED_PROTOCOL_SHA256,
        "blocked_effect_attempts": blocked_counts,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--strict-audit", action="store_true")
    modes.add_argument("--qualified-edge", action="store_true")
    modes.add_argument("--qualified-deep", action="store_true")
    parser.add_argument("--base-report-sha256")
    parser.add_argument("--strict-report-sha256")
    parser.add_argument("--module", choices=tuple(CANDIDATE_MODULES.values()))
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    options = parse_arguments(sys.argv[1:] if arguments is None else arguments)
    if options.self_test:
        require(options.base_report_sha256 is None
                and options.strict_report_sha256 is None
                and options.module is None,
                "a source-only published-pin control cannot authorize production")
        report = candidate_free_self_test()
        print(canonical(report).decode("ascii"), flush=True)
        return 0
    if options.strict_audit:
        validated_pins("strict-audit", options.base_report_sha256,
                       options.strict_report_sha256, options.module)
        return run_strict_audit(options.base_report_sha256)
    mode = "qualified-edge" if options.qualified_edge else "qualified-deep"
    validated_pins(mode, options.base_report_sha256,
                   options.strict_report_sha256, options.module)
    return run_qualified_proof(
        mode, options.base_report_sha256,
        options.strict_report_sha256, options.module,
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PublishedPinError as error:
        print(canonical({
            "schema": SCHEMA, "status": "FAIL", "passed": False,
            "error_type": type(error).__name__, "error": str(error),
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }).decode("ascii"), file=sys.stderr, flush=True)
        raise SystemExit(1) from error
