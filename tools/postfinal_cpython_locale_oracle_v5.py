#!/usr/bin/env python3
"""Run the untouched complete CPython regex suite without circular evidence."""

from __future__ import annotations

import argparse
import builtins
import contextlib
import copy
import hashlib
import importlib
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
from typing import Any, Callable, Iterator, Mapping


ROOT = Path(__file__).resolve().parent.parent
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

from tools import postfinal_cpython_locale_oracle_v4 as upstream


SCHEMA = "rebar-postfinal-cpython-full-public-locale-v5"
SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v5.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V5.md"
PROTOCOL_SHA256 = (
    "1329cf9c8e36391af134b2fb2b212e71067ace736b282dacd2a6c90233384840"
)
V4_SOURCE_SHA256 = (
    "9f39e055922daf9b2a5f4a93048d97df6dcd4164eb9b6017bf4a20c3dcbb0652"
)
V4_PROTOCOL_SHA256 = (
    "54a4e397860ddab092dd9386a3a8cf3521d96b1fcf4d7d35bcbe55118d8a7a76"
)
METHOD_MATRIX_SHA256 = (
    "5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a"
)
V8_BASE_SOURCE_SHA256 = (
    "14b8daeebfb620eafa778529f6bf11e1a4f48256dd010b25621f4e94666692c6"
)
V8_STRICT_SOURCE_SHA256 = (
    "bb22b1983c11a896d3639077050dfaac746876ccbb9e4909518fb33d19987c01"
)
V8_OWNERSHIP_PROTOCOL_SHA256 = (
    "5c60e6ce63ff1e4c5593eaafe29971cb3557b1a0389dcd5cf41cfb00647bc399"
)
V8_PROOF_SOURCE_RELATIVE = "tools/postfinal_current_build_proofs_v8.py"
V8_PROOF_SOURCE_SHA256 = (
    "0f9e12847855797669206ea89de94948da66c29742d64820a625ce5a6570b313"
)
V8_PROOF_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V8.md"
)
V8_PROOF_PROTOCOL_SHA256 = (
    "76e66c091ae06ad56b8f4e22c76f4db44810cdb512b839201c9cc7cb83f4cfa0"
)
FAMILIES = ("rust", "vm", "zig")
REFERENCE_LABELS = ("reference_a", "reference_b")
MAX_SOURCE_BYTES = upstream.MAX_FROZEN_SOURCE_BYTES
MAX_EVIDENCE_BYTES = upstream.MAX_EVIDENCE_BYTES
MAX_WORKER_OUTPUT_BYTES = upstream.MAX_WORKER_OUTPUT_BYTES
WORKER_TIMEOUT_SECONDS = 3_600
SELF_ORACLE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v5-self-oracle.json"
)
SELF_ORACLE_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "postfinal-locale-v5-self-oracle-failures.json"
)
REPORT_RELATIVE = "oracle/cpython-3.14.6/evidence/postfinal-locale-v5-all.json"
ROLE_REPORT_RELATIVES = {
    name: "oracle/cpython-3.14.6/evidence/postfinal-locale-v5-"
    + name + ".json"
    for name in FAMILIES
}
ROLE_FAILURE_RELATIVES = {
    name: "oracle/cpython-3.14.6/evidence/postfinal-locale-v5-"
    + name + "-failures.json"
    for name in FAMILIES
}
APPROVED_OUTPUTS = frozenset({
    SELF_ORACLE_RELATIVE,
    SELF_ORACLE_FAILURE_RELATIVE,
    REPORT_RELATIVE,
    *ROLE_REPORT_RELATIVES.values(),
    *ROLE_FAILURE_RELATIVES.values(),
})


class OfficialV5Error(AssertionError):
    """An actual original upstream obligation cannot honestly qualify."""


class OfficialV5WorkerFailure(OfficialV5Error):
    """Keep real partial original records and real worker failure details."""

    def __init__(self, role: str, message: str, details: Mapping[str, Any]):
        super().__init__(message)
        self.role = role
        self.details = dict(details)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise OfficialV5Error(message)


def valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def verify_runtime() -> None:
    require(
        tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.implementation.name == "cpython"
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and Path(sys.executable).resolve() == upstream.PINNED_CPYTHON.resolve(),
        "the exact isolated, bytecode-free pinned CPython 3.14.6 is required",
    )
    require(
        bool(sys.path)
        and sys.path[0] == str(ROOT)
        and Path(__file__).resolve()
        == (ROOT / SOURCE_RELATIVE).resolve(),
        "direct isolated execution requires only the exact trusted V5 root",
    )
    require(
        upstream.SCHEMA == "rebar-postfinal-cpython-full-public-locale-v4"
        and upstream.METHOD_MATRIX_SHA256 == METHOD_MATRIX_SHA256
        and upstream.PUBLIC_METHODS == 152
        and upstream.PRIVATE_METHODS == 13
        and upstream.ORIGINAL_METHODS == 165
        and upstream.CORPUS_CASES == 403
        and upstream.EXTERNAL_FIXTURE_ASSERTION_CASES == 11
        and len(upstream.OFFICIAL_SUPPORT_MODULES) == 26
        and upstream.CONFIGURED_OFFICIAL_MEMORY_BYTES == 40 * 1024**3
        and upstream.REQUIRED_OFFICIAL_SUBN_MEMORY_BYTES == 18 * 2**31,
        "the complete authentic version-four upstream source contract changed",
    )


def _read_bounded(path: Path, maximum: int, label: str) -> bytes:
    require(type(maximum) is int and maximum > 0,
            "a real bounded regular source or evidence input is required")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise OfficialV5Error("a genuine frozen input is unavailable: " + label) from error
    try:
        metadata = os.fstat(descriptor)
        require(stat.S_ISREG(metadata.st_mode)
                and 0 < metadata.st_size <= maximum,
                "a frozen input must be one bounded regular file: " + label)
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, 65_536)
            if not chunk:
                break
            total += len(chunk)
            require(total <= maximum,
                    "a genuine frozen input exceeded its bound: " + label)
            chunks.append(chunk)
    finally:
        os.close(descriptor)
    payload = b"".join(chunks)
    require(len(payload) == metadata.st_size,
            "a frozen input changed while it was being authenticated: " + label)
    return payload


def _verify_frozen(relative: str, expected: str, maximum: int) -> bytes:
    require(valid_sha256(expected), "an actual frozen SHA-256 is required")
    require(
        isinstance(relative, str)
        and PurePosixPath(relative).as_posix() == relative
        and not PurePosixPath(relative).is_absolute()
        and ".." not in PurePosixPath(relative).parts
        and "\\" not in relative
        and "\x00" not in relative,
        "a frozen input escaped its exact repository-relative path",
    )
    payload = _read_bounded(ROOT / relative, maximum, relative)
    require(hashlib.sha256(payload).hexdigest() == expected,
            "the independently frozen input changed: " + relative)
    return payload


def authenticate_reference_prerequisites(
    source_sha256: str,
    protocol_sha256: str,
) -> dict[str, Any]:
    """Authenticate only Python and the exact V5/V4 upstream source graph."""
    verify_runtime()
    require(valid_sha256(source_sha256),
            "BLOCKED: publish the actual frozen V5 controller SHA-256 first")
    require(protocol_sha256 == PROTOCOL_SHA256,
            "BLOCKED: publish the exact frozen V5 protocol SHA-256 first")
    _verify_frozen(SOURCE_RELATIVE, source_sha256, MAX_SOURCE_BYTES)
    _verify_frozen(PROTOCOL_RELATIVE, protocol_sha256, MAX_SOURCE_BYTES)
    _verify_frozen(upstream.SOURCE_RELATIVE, V4_SOURCE_SHA256, MAX_SOURCE_BYTES)
    _verify_frozen(upstream.PROTOCOL_RELATIVE, V4_PROTOCOL_SHA256, MAX_SOURCE_BYTES)
    require(Path(upstream.__file__).resolve()
            == (ROOT / upstream.SOURCE_RELATIVE).resolve(),
            "the authenticated original V4 upstream helper was substituted")
    support = upstream.authenticate_upstream_support()
    official = upstream.introspect_official_sources()
    require(
        official.get("public_method_matrix_sha256") == METHOD_MATRIX_SHA256
        and len(official.get("public_method_matrix", ())) == 152
        and official.get("all_original_methods") == 165
        and official.get("public_original_methods") == 152
        and official.get("private_original_methods") == 13
        and official.get("public_method_waivers") == []
        and official.get("actual_upstream_corpus_cases") == 403
        and official.get("actual_external_fixture_assertion_cases") == 11
        and support.get("official_support_module_count") == 26
        and support.get("official_support_tree_sha256")
        == upstream.OFFICIAL_SUPPORT_TREE_SHA256,
        "the complete unchanged 152-method upstream matrix or fixtures changed",
    )
    return {
        "source_sha256": source_sha256,
        "protocol_sha256": protocol_sha256,
        "upstream_v4_source_sha256": V4_SOURCE_SHA256,
        "upstream_v4_protocol_sha256": V4_PROTOCOL_SHA256,
        "official": official,
        "support": support,
        "native_sha256_by_family": {},
    }


def _status_vector(records: Any) -> list[dict[str, Any]]:
    require(isinstance(records, list),
            "all actual original upstream method records are required")
    return [
        {
            "test": row.get("test"),
            "source_ast_sha256": row.get("source_ast_sha256"),
            "status": row.get("status"),
            "skip_kind": row.get("skip_kind"),
            "reason": row.get("reason"),
        }
        for row in records
        if isinstance(row, Mapping)
    ]


def _safe_output_path(relative: str) -> Path:
    require(
        isinstance(relative, str)
        and relative in APPROVED_OUTPUTS
        and PurePosixPath(relative).as_posix() == relative
        and not PurePosixPath(relative).is_absolute()
        and ".." not in PurePosixPath(relative).parts
        and "\\" not in relative
        and "\x00" not in relative,
        "only an exact, new, allowlisted V5 evidence destination is permitted",
    )
    return ROOT / relative


def _preflight_fresh_outputs(relatives: tuple[str, ...]) -> None:
    require(len(relatives) == len(set(relatives)),
            "an official role cannot reuse or overwrite an evidence destination")
    for relative in relatives:
        path = _safe_output_path(relative)
        parent = path.parent
        require(parent.is_dir() and not parent.is_symlink()
                and path.resolve(strict=False) == path
                and not path.exists() and not path.is_symlink(),
                "an exact V5 report already exists or traverses a symlink: "
                + relative)


def _exclusive_write(document: Mapping[str, Any], relative: str) -> str:
    path = _safe_output_path(relative)
    require(path.parent.is_dir() and not path.parent.is_symlink(),
            "the exact official V5 evidence directory is unavailable")
    payload = canonical(document) + b"\n"
    require(0 < len(payload) <= MAX_EVIDENCE_BYTES,
            "a real V5 official report exceeded its frozen bounded size")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as error:
        raise OfficialV5Error(
            "refusing to replace, retry, or redirect existing V5 evidence: "
            + relative
        ) from error
    try:
        remaining = memoryview(payload)
        while remaining:
            count = os.write(descriptor, remaining)
            require(count > 0, "an exclusively created V5 report was truncated")
            remaining = remaining[count:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return hashlib.sha256(payload).hexdigest()


def _read_verified_evidence(relative: str, expected: str) -> dict[str, Any]:
    require(valid_sha256(expected),
            "the actual independently published V5 evidence hash is required")
    payload = _read_bounded(
        _safe_output_path(relative), MAX_EVIDENCE_BYTES, relative,
    )
    require(hashlib.sha256(payload).hexdigest() == expected,
            "the actual exclusive V5 evidence bytes changed: " + relative)
    document = upstream._strict_json(payload, relative)
    require(isinstance(document, dict)
            and canonical(document) + b"\n" == payload,
            "V5 evidence must retain its exact original canonical JSON bytes")
    return document


def _base_document(provenance: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "source_sha256": provenance["source_sha256"],
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": provenance["protocol_sha256"],
        "immutable_v4_source_sha256": V4_SOURCE_SHA256,
        "immutable_v4_protocol_sha256": V4_PROTOCOL_SHA256,
        "test_source_sha256": upstream.TEST_SOURCE_SHA256,
        "corpus_source_sha256": upstream.CORPUS_SOURCE_SHA256,
        "upstream_archive_sha256": upstream.UPSTREAM_ARCHIVE_SHA256,
        "official_support_tree_sha256": upstream.OFFICIAL_SUPPORT_TREE_SHA256,
        "official_support_module_count": 26,
        "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
        "all_original_methods": 165,
        "public_original_methods": 152,
        "private_original_methods": 13,
        "actual_upstream_corpus_cases": 403,
        "actual_external_fixture_assertion_cases": 11,
        "public_method_waivers": [],
        "named_private_class_waivers": upstream.PRIVATE_CLASS_WAIVERS,
        "synthetic": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
        "old_v7_campaign_prerequisite": False,
    }


def _execute_original_role(
    role: str,
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    """Execute V4's literal original methods with only the acyclic V5 gate."""
    require(role in ("stdlib", *FAMILIES),
            "only an approved isolated original upstream role is permitted")
    matrix = provenance["official"]["public_method_matrix"]
    expected_path = upstream.UPSTREAM_LIB / "test" / "test_re.py"
    exact_source = _read_bounded(
        expected_path, MAX_SOURCE_BYTES, "authentic original Lib/test/test_re.py",
    )
    require(hashlib.sha256(exact_source).hexdigest() == upstream.TEST_SOURCE_SHA256,
            "the literal executed original upstream test source was changed")
    previous_path = list(sys.path)
    output = io.StringIO()
    error_output = io.StringIO()
    records: list[dict[str, Any]] = []
    active_method: str | None = None
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
        require(
            support.bigmemtest.__module__ == "test.support"
            and support.requires_resource.__module__ == "test.support"
            and support._2G == 2**31,
            "the original role loaded a fabricated upstream resource decorator",
        )
        support.verbose = 0
        support.set_memlimit("40G")
        require(
            support.real_max_memuse == upstream.CONFIGURED_OFFICIAL_MEMORY_BYTES
            and support.is_resource_enabled("cpu"),
            "the real original 40-GiB memory or CPU resource is unavailable",
        )
        require("fork" in multiprocessing.get_all_start_methods(),
                "the original multiprocessing regression requires real fork")
        multiprocessing.set_start_method("fork", force=True)
        require(multiprocessing.get_start_method() == "fork",
                "the original multiprocessing start method was substituted")
        with upstream._single_memory_worker():
            with upstream._fresh_private_locales() as locale_report:
                with upstream._role_regex_module(
                    role, baseline, constants, provenance,
                ) as (regex, guard):
                    specification = importlib.util.spec_from_file_location(
                        "test.test_re", expected_path,
                    )
                    require(specification is not None
                            and specification.loader is not None,
                            "the untouched original upstream test is unavailable")
                    namespace = importlib.util.module_from_spec(specification)
                    previous_official = sys.modules.get("test.test_re")
                    try:
                        sys.modules["test.test_re"] = namespace
                        with contextlib.redirect_stdout(output):
                            with contextlib.redirect_stderr(error_output):
                                specification.loader.exec_module(namespace)
                                require(
                                    upstream._verify_live_official_fixtures(
                                        support, warnings_helper, corpus,
                                    ) == fixtures_before,
                                    "the unchanged original fixtures were replaced",
                                )
                                for requirement in matrix:
                                    active_method = requirement["test"]
                                    if active_method in {
                                        "ExternalTests.test_re_tests",
                                        "ExternalTests.test_re_benchmarks",
                                    }:
                                        require(
                                            upstream._verify_live_official_fixtures(
                                                support, warnings_helper, corpus,
                                            ) == fixtures_before,
                                            "the original 403/11 upstream fixture changed",
                                        )
                                    records.append(upstream._run_one_original_method(
                                        namespace, requirement, expected_path,
                                        support, "fork",
                                    ))
                                    active_method = None
                                fixtures_after = upstream._verify_live_official_fixtures(
                                    support, warnings_helper, corpus,
                                )
                                require(fixtures_after == fixtures_before,
                                        "an original live upstream fixture changed")
                    finally:
                        if previous_official is None:
                            sys.modules.pop("test.test_re", None)
                        else:
                            sys.modules["test.test_re"] = previous_official
                    require(
                        error_output.getvalue() == "",
                        "the actual original upstream role wrote genuine stderr",
                    )
                    summary = upstream.assess_role_records(role, records, matrix)
                    return {
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
                            "cpu_resource_enabled": support.is_resource_enabled("cpu"),
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
                        "captured_official_stderr": error_output.getvalue(),
                    }
    except OfficialV5WorkerFailure:
        raise
    except (OfficialV5Error, upstream.OfficialV4Error, OSError, MemoryError) as error:
        if records or active_method is not None:
            raise OfficialV5WorkerFailure(
                role,
                "the genuine original upstream worker stopped: " + role,
                {
                    "completed_original_method_records": records,
                    "completed_original_method_count": len(records),
                    "active_original_method": active_method,
                    "actual_error_type": type(error).__name__,
                    "actual_error": str(error),
                    "captured_official_stdout": upstream._bounded_failure_stream(
                        output.getvalue(),
                    ),
                    "captured_official_stderr": upstream._bounded_failure_stream(
                        error_output.getvalue(),
                    ),
                },
            ) from error
        raise
    finally:
        sys.path[:] = previous_path


def _validate_role(
    role: str,
    report: Mapping[str, Any],
    matrix: list[dict[str, Any]],
) -> dict[str, Any]:
    try:
        require(
            isinstance(report, Mapping)
            and report.get("captured_official_stderr") == "",
            "the actual original upstream role wrote or concealed stderr: "
            + role,
        )
        return upstream._validate_role_evidence(role, report, matrix)
    except upstream.OfficialV4Error as error:
        raise OfficialV5Error(
            "the complete authentic 152-method original role did not qualify: "
            + role + ": " + str(error)
        ) from error


def _candidate_pin_values(
    values: Mapping[str, Any],
) -> dict[str, str]:
    required = {
        "v8_base_source": values.get("v8_base_source"),
        "v8_base_report": values.get("v8_base_report"),
        "v8_strict_source": values.get("v8_strict_source"),
        "v8_strict_report": values.get("v8_strict_report"),
        **{
            name + "_" + kind: values.get(name + "_" + kind)
            for name in FAMILIES for kind in ("edge", "deep")
        },
    }
    for name, value in required.items():
        require(valid_sha256(value),
                "BLOCKED: the actual independently published V8 "
                + name + " SHA-256 is required before candidate import")
    require(required["v8_base_source"] == V8_BASE_SOURCE_SHA256,
            "the frozen actual independently owned V8 base source changed")
    require(required["v8_strict_source"] == V8_STRICT_SOURCE_SHA256,
            "the frozen actual independently owned V8 strict source changed")
    require(len(set(required.values())) == len(required),
            "distinct actual audit sources, reports, and proofs cannot share a pin")
    return {name: str(value) for name, value in required.items()}


def authenticate_candidate_prerequisites(
    provenance: Mapping[str, Any],
    candidate_pins: Mapping[str, str],
) -> dict[str, Any]:
    """Verify real V8 audits and all six real proofs before candidate import."""
    pins = _candidate_pin_values(candidate_pins)
    _verify_frozen(
        V8_PROOF_SOURCE_RELATIVE, V8_PROOF_SOURCE_SHA256, MAX_SOURCE_BYTES,
    )
    _verify_frozen(
        V8_PROOF_PROTOCOL_RELATIVE, V8_PROOF_PROTOCOL_SHA256, MAX_SOURCE_BYTES,
    )
    _verify_frozen(
        "candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V8.md",
        V8_OWNERSHIP_PROTOCOL_SHA256,
        MAX_SOURCE_BYTES,
    )
    proof = importlib.import_module("tools.postfinal_current_build_proofs_v8")
    require(
        Path(proof.__file__).resolve() == (ROOT / V8_PROOF_SOURCE_RELATIVE).resolve()
        and proof.REFRESH_PROTOCOL_SHA256 == V8_PROOF_PROTOCOL_SHA256
        and proof.V8_SOURCE_AUDIT_SHA256 == V8_BASE_SOURCE_SHA256
        and proof.V8_STRICT_AUDIT_SHA256 == V8_STRICT_SOURCE_SHA256
        and tuple(proof.FAMILIES) == FAMILIES,
        "the frozen all-family current-build proof controller was substituted",
    )
    audit_pins = {
        "source_audit": pins["v8_base_source"],
        "source_report": pins["v8_base_report"],
        "strict_audit": pins["v8_strict_source"],
        "strict_report": pins["v8_strict_report"],
    }
    try:
        owner, observed_owner = proof.source_audit_module(
            audit_pins["source_audit"],
        )
        require(observed_owner == V8_BASE_SOURCE_SHA256
                and owner.PROTOCOL_SHA256 == V8_OWNERSHIP_PROTOCOL_SHA256,
                "the independently frozen V8 native owner was substituted")
        preserved_failures = proof.authenticate_history(owner)
        audit = proof.authenticate_v8_audits(owner, audit_pins)
        contract = proof.load_contract()
        graph = audit["graph"]
        require(set(graph["native_sha256_by_family"]) == set(FAMILIES),
                "an all-family V8 audit omitted an independently owned engine")
        qualified: dict[str, Any] = {}
        for family in FAMILIES:
            snapshot = proof.snapshot_family(family)
            require(snapshot["native_sha256_by_path"]
                    == graph["native_sha256_by_family"][family]
                    and set(snapshot["source_sha256_by_path"])
                    <= set(graph["source_paths"]),
                    "the actual audited source or native ELF changed: " + family)
            edge_path = proof.edge_target(family, True, True)
            edge_raw = proof.read_regular(
                edge_path, "actual V8 audit-qualified passing edge: " + family,
            )
            require(hashlib.sha256(edge_raw).hexdigest()
                    == pins[family + "_edge"],
                    "the actual current-build qualified edge changed: " + family)
            _, edge_report, edge_passed = proof.validate_original_edge(
                edge_raw, edge_path, family, snapshot, contract,
            )
            require(edge_passed is True,
                    "the complete genuine current edge did not pass: " + family)
            deep_path = proof.deep_target(family, True)
            deep_raw = proof.read_regular(
                deep_path, "actual V8 audit-qualified passing deep proof: " + family,
            )
            require(hashlib.sha256(deep_raw).hexdigest()
                    == pins[family + "_deep"],
                    "the actual current-build qualified deep proof changed: "
                    + family)
            deep_report, deep_passed = proof.validate_deep(
                deep_raw, family, edge_report, snapshot, contract,
            )
            require(deep_passed is True
                    and deep_report.get("status") == "PASS"
                    and deep_report.get("public_mismatch_count") == 0,
                    "the complete genuine current deep proof did not pass: "
                    + family)
            qualified[family] = {
                "edge_path": edge_path.relative_to(ROOT).as_posix(),
                "edge_sha256": pins[family + "_edge"],
                "edge_checks": proof.EDGE_CHECKS,
                "edge_categories": proof.EDGE_CATEGORIES,
                "deep_path": deep_path.relative_to(ROOT).as_posix(),
                "deep_sha256": pins[family + "_deep"],
                "deep_checks": proof.DEEP_CHECKS,
                "native_sha256_by_path": snapshot["native_sha256_by_path"],
                "source_sha256_by_path": snapshot["source_sha256_by_path"],
            }
    except (AssertionError, ImportError, OSError, ValueError, KeyError) as error:
        if isinstance(error, OfficialV5Error):
            raise
        raise OfficialV5Error(
            "the actual current all-family V8 ownership or qualified proof failed: "
            + str(error)
        ) from error
    require(set(qualified) == set(FAMILIES)
            and set(preserved_failures) == set(FAMILIES),
            "all three genuine V8 families and historical failures are required")
    return {
        **provenance,
        "native_sha256_by_family": graph["native_sha256_by_family"],
        "candidate_prerequisite_sha256": pins,
        "v8_proof_source_sha256": V8_PROOF_SOURCE_SHA256,
        "v8_proof_protocol_sha256": V8_PROOF_PROTOCOL_SHA256,
        "v8_ownership_protocol_sha256": V8_OWNERSHIP_PROTOCOL_SHA256,
        "qualified_family_proofs": qualified,
        "preserved_historical_edge_failures": preserved_failures,
    }


WORKER_BOOTSTRAP = (
    "import sys;sys.path.insert(0,sys.argv[1]);"
    "from tools.postfinal_cpython_locale_oracle_v5 import worker_entry;"
    "raise SystemExit(worker_entry(sys.argv[2],sys.argv[3],"
    "sys.argv[4],sys.argv[5],sys.argv[6]))"
)


def worker_entry(
    role: str,
    reference_label: str,
    source_sha256: str,
    protocol_sha256: str,
    encoded_candidate_pins: str,
) -> int:
    try:
        require(role in ("stdlib", *FAMILIES),
                "an unapproved actual original V5 worker was requested")
        require(
            (role == "stdlib" and reference_label in REFERENCE_LABELS)
            or (role in FAMILIES and reference_label == "candidate"),
            "a real original worker reference or candidate role was substituted",
        )
        pins = upstream._strict_json(
            encoded_candidate_pins.encode("ascii"),
            "exact isolated V5 candidate pin arguments",
        )
        require(isinstance(pins, dict),
                "isolated actual V5 proof pins must be one JSON object")
        require(role != "stdlib" or pins == {},
                "a Python-only original reference must not consume candidate pins")
        provenance = authenticate_reference_prerequisites(
            source_sha256, protocol_sha256,
        )
        if role != "stdlib":
            provenance = authenticate_candidate_prerequisites(provenance, pins)
        report = _execute_original_role(role, provenance)
    except OfficialV5WorkerFailure as error:
        print(json.dumps({
            "schema": SCHEMA + "-actual-worker-failure",
            "status": "FAIL",
            "role": error.role,
            "reference_label": reference_label,
            "reason": str(error),
            "details": error.details,
            "performance": "NOT MEASURED",
        }, sort_keys=True, separators=(",", ":")))
        return 2
    except (
        OfficialV5Error, upstream.OfficialV4Error, OSError, MemoryError,
        subprocess.SubprocessError, UnicodeError, ValueError,
    ) as error:
        print(json.dumps({
            "schema": SCHEMA + "-actual-worker-failure",
            "status": "FAIL",
            "role": role,
            "reference_label": reference_label,
            "actual_error_type": type(error).__name__,
            "reason": str(error),
            "performance": "NOT MEASURED",
        }, sort_keys=True, separators=(",", ":")))
        return 2
    print(json.dumps({
        "schema": SCHEMA + "-actual-worker",
        "python": "3.14.6",
        "role": role,
        "reference_label": reference_label,
        "source_sha256": source_sha256,
        "protocol_sha256": protocol_sha256,
        "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
        "role_report": report,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }, sort_keys=True, separators=(",", ":")))
    return 0


def _validate_worker_stderr(
    role: str,
    stderr: bytes,
    details: Mapping[str, Any],
) -> None:
    if not isinstance(stderr, bytes) or stderr:
        raise OfficialV5WorkerFailure(
            role,
            "a genuine isolated original V5 worker wrote stderr: " + role,
            details,
        )


def _run_isolated_worker(
    role: str,
    reference_label: str,
    source_sha256: str,
    protocol_sha256: str,
    candidate_pins: Mapping[str, str],
) -> dict[str, Any]:
    require(role in ("stdlib", *FAMILIES),
            "an exact approved isolated original V5 worker is required")
    require(
        (role == "stdlib" and reference_label in REFERENCE_LABELS
         and not candidate_pins)
        or (role in FAMILIES and reference_label == "candidate"
            and bool(candidate_pins)),
        "an isolated Python reference cannot consume native candidate proofs",
    )
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        completed = subprocess.run(
            [
                str(upstream.PINNED_CPYTHON), "-I", "-B", "-c",
                WORKER_BOOTSTRAP, str(ROOT), role, reference_label,
                source_sha256, protocol_sha256,
                canonical(dict(candidate_pins)).decode("ascii"),
            ],
            check=False,
            capture_output=True,
            env=environment,
            timeout=WORKER_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        raise OfficialV5WorkerFailure(
            role,
            "an actual isolated original V5 worker timed out: " + role,
            {
                "status": "TIMEOUT",
                "reference_label": reference_label,
                "timeout_seconds": WORKER_TIMEOUT_SECONDS,
                "stdout": upstream._bounded_failure_stream(error.stdout),
                "stderr": upstream._bounded_failure_stream(error.stderr),
            },
        ) from error
    stdout = upstream._bounded_failure_stream(completed.stdout)
    stderr = upstream._bounded_failure_stream(completed.stderr)
    details: dict[str, Any] = {
        "reference_label": reference_label,
        "returncode": completed.returncode,
        "signal": -completed.returncode if completed.returncode < 0 else None,
        "stdout_bytes": len(completed.stdout),
        "stderr_bytes": len(completed.stderr),
        "stdout_sha256": stdout["sha256"],
        "stderr_sha256": stderr["sha256"],
        "stdout_truncated": len(completed.stdout) > MAX_WORKER_OUTPUT_BYTES,
        "stderr_truncated": len(completed.stderr) > MAX_WORKER_OUTPUT_BYTES,
        "stdout": stdout,
        "stderr": stderr,
    }
    require_bound = (
        len(completed.stdout) <= MAX_WORKER_OUTPUT_BYTES
        and len(completed.stderr) <= MAX_WORKER_OUTPUT_BYTES
    )
    if not require_bound:
        raise OfficialV5WorkerFailure(
            role, "an actual original worker exceeded bounded output", details,
        )
    try:
        document = upstream._strict_json(completed.stdout, "actual V5 " + role)
    except upstream.OfficialV4Error as error:
        details["json_error"] = str(error)
        raise OfficialV5WorkerFailure(
            role, "an actual original V5 worker returned invalid evidence", details,
        ) from error
    if isinstance(document, Mapping):
        details["actual_worker_document"] = document
    if completed.returncode != 0:
        raise OfficialV5WorkerFailure(
            role, "a genuine isolated original V5 worker failed: " + role, details,
        )
    _validate_worker_stderr(role, completed.stderr, details)
    if not (
        isinstance(document, dict)
        and document.get("schema") == SCHEMA + "-actual-worker"
        and document.get("python") == "3.14.6"
        and document.get("role") == role
        and document.get("reference_label") == reference_label
        and document.get("source_sha256") == source_sha256
        and document.get("protocol_sha256") == protocol_sha256
        and document.get("public_method_matrix_sha256") == METHOD_MATRIX_SHA256
        and document.get("performance") == "NOT MEASURED"
        and document.get("holdout") == "NOT ACCESSED"
        and isinstance(document.get("role_report"), dict)
    ):
        raise OfficialV5WorkerFailure(
            role, "the genuine original V5 worker changed frozen provenance", details,
        )
    return document["role_report"]


def _validate_reference(
    document: Mapping[str, Any],
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        document.get("schema") == SCHEMA + "-self-oracle"
        and document.get("status") == "PASS"
        and document.get("synthetic") is False
        and document.get("python") == "3.14.6"
        and document.get("source_sha256") == provenance["source_sha256"]
        and document.get("protocol_sha256") == provenance["protocol_sha256"]
        and document.get("public_method_matrix_sha256") == METHOD_MATRIX_SHA256
        and document.get("actual_independent_reference_count") == 2
        and document.get("old_v7_campaign_prerequisite") is False
        and document.get("reference_candidate_imports") == 0
        and document.get("reference_candidate_audits_read") == 0
        and document.get("reference_candidate_proofs_read") == 0
        and document.get("reference_holdout_cases_read") == 0
        and document.get("performance") == "NOT MEASURED",
        "an actual two-worker candidate-free V5 standard-library report is required",
    )
    roles = document.get("roles")
    require(isinstance(roles, dict) and tuple(roles) == REFERENCE_LABELS,
            "two distinct actual isolated standard-library workers are required")
    matrix = provenance["official"]["public_method_matrix"]
    for label in REFERENCE_LABELS:
        require(isinstance(roles[label], dict),
                "an actual original reference role disappeared: " + label)
        _validate_role("stdlib", roles[label], matrix)
    first = _status_vector(roles[REFERENCE_LABELS[0]]["records"])
    second = _status_vector(roles[REFERENCE_LABELS[1]]["records"])
    require(first == second and len(first) == 152,
            "the independently executed original Python reference vectors disagree")
    require(document.get("reference_status_vector_sha256") == digest(first),
            "the frozen two-reference original status vector changed")
    return dict(roles)


def run_self_oracle(source_sha256: str, protocol_sha256: str) -> dict[str, Any]:
    provenance = authenticate_reference_prerequisites(
        source_sha256, protocol_sha256,
    )
    _preflight_fresh_outputs((SELF_ORACLE_RELATIVE, SELF_ORACLE_FAILURE_RELATIVE))
    matrix = provenance["official"]["public_method_matrix"]
    observed: dict[str, dict[str, Any]] = {}
    for label in REFERENCE_LABELS:
        try:
            report = _run_isolated_worker(
                "stdlib", label, source_sha256, protocol_sha256, {},
            )
            _validate_role("stdlib", report, matrix)
            observed[label] = report
        except (OfficialV5WorkerFailure, OfficialV5Error) as error:
            if isinstance(error, OfficialV5WorkerFailure):
                details = dict(error.details)
            else:
                details = {"validation_failure": str(error)}
                if "report" in locals():
                    details["actual_role_report"] = report
            details["actual_completed_reference_roles"] = observed
            details["actual_failed_reference_label"] = label
            raise OfficialV5WorkerFailure(
                "stdlib", "the actual Python-vs-Python reference failed: " + label,
                details,
            ) from error
    first = _status_vector(observed["reference_a"]["records"])
    second = _status_vector(observed["reference_b"]["records"])
    if first != second:
        raise OfficialV5WorkerFailure(
            "stdlib", "the two independently executed original references differ",
            {
                "actual_completed_reference_roles": observed,
                "reference_a_status_vector": first,
                "reference_b_status_vector": second,
            },
        )
    document = {
        **_base_document(provenance),
        "schema": SCHEMA + "-self-oracle",
        "status": "PASS",
        "actual_independent_reference_count": 2,
        "reference_status_vector_sha256": digest(first),
        "reference_candidate_imports": 0,
        "reference_candidate_audits_read": 0,
        "reference_candidate_proofs_read": 0,
        "reference_holdout_cases_read": 0,
        "roles": observed,
    }
    _validate_reference(document, provenance)
    _exclusive_write(document, SELF_ORACLE_RELATIVE)
    return document


def run_candidates(
    selected: str,
    source_sha256: str,
    protocol_sha256: str,
    reference_sha256: str,
    supplied_pins: Mapping[str, Any],
) -> dict[str, Any]:
    require(selected in ("all", *FAMILIES),
            "an explicitly approved isolated native candidate is required")
    candidate_pins = _candidate_pin_values(supplied_pins)
    provenance = authenticate_reference_prerequisites(
        source_sha256, protocol_sha256,
    )
    baseline = _read_verified_evidence(SELF_ORACLE_RELATIVE, reference_sha256)
    references = _validate_reference(baseline, provenance)
    provenance = authenticate_candidate_prerequisites(provenance, candidate_pins)
    chosen = FAMILIES if selected == "all" else (selected,)
    destinations = tuple(
        relative
        for family in chosen
        for relative in (
            ROLE_REPORT_RELATIVES[family], ROLE_FAILURE_RELATIVES[family],
        )
    )
    if selected == "all":
        destinations += (REPORT_RELATIVE,)
    _preflight_fresh_outputs(destinations)
    matrix = provenance["official"]["public_method_matrix"]
    baseline_vector = _status_vector(references["reference_a"]["records"])
    reports: dict[str, Any] = dict(references)
    for family in chosen:
        evidence: dict[str, Any] | None = None
        try:
            evidence = _run_isolated_worker(
                family, "candidate", source_sha256, protocol_sha256,
                candidate_pins,
            )
            _validate_role(family, evidence, matrix)
            require(_status_vector(evidence["records"]) == baseline_vector,
                    "an actual original native outcome differs from both references")
        except (OfficialV5WorkerFailure, OfficialV5Error) as error:
            details = (
                dict(error.details)
                if isinstance(error, OfficialV5WorkerFailure)
                else {"validation_failure": str(error)}
            )
            if evidence is not None:
                details["actual_role_report"] = evidence
            details["actual_completed_candidate_roles"] = {
                name: value for name, value in reports.items()
                if name in FAMILIES
            }
            raise OfficialV5WorkerFailure(
                family, "the authentic full original native role failed: " + family,
                details,
            ) from error
        role_document = {
            **_base_document(provenance),
            "schema": SCHEMA + "-actual-" + family + "-role",
            "status": "PASS",
            "reference_path": SELF_ORACLE_RELATIVE,
            "reference_sha256": reference_sha256,
            "reference_status_vector_sha256": digest(baseline_vector),
            "candidate_prerequisite_sha256": candidate_pins,
            "qualified_family_proofs": provenance["qualified_family_proofs"],
            "preserved_historical_edge_failures": provenance[
                "preserved_historical_edge_failures"
            ],
            "roles": {family: evidence},
        }
        _exclusive_write(role_document, ROLE_REPORT_RELATIVES[family])
        reports[family] = evidence
    if selected != "all":
        return {
            "schema": SCHEMA + "-single-candidate-result",
            "status": "PASS",
            "role": selected,
            "path": ROLE_REPORT_RELATIVES[selected],
            "reference_sha256": reference_sha256,
            "original_public_methods": 152,
            "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED",
        }
    require(set(reports) == {*REFERENCE_LABELS, *FAMILIES},
            "both real references and all three real candidate families are required")
    document = {
        **_base_document(provenance),
        "schema": SCHEMA,
        "status": "PASS",
        "reference_path": SELF_ORACLE_RELATIVE,
        "reference_sha256": reference_sha256,
        "actual_independent_reference_count": 2,
        "reference_status_vector_sha256": digest(baseline_vector),
        "candidate_prerequisite_sha256": candidate_pins,
        "v8_proof_source_sha256": V8_PROOF_SOURCE_SHA256,
        "v8_proof_protocol_sha256": V8_PROOF_PROTOCOL_SHA256,
        "v8_ownership_protocol_sha256": V8_OWNERSHIP_PROTOCOL_SHA256,
        "qualified_family_proofs": provenance["qualified_family_proofs"],
        "preserved_historical_edge_failures": provenance[
            "preserved_historical_edge_failures"
        ],
        "roles": reports,
    }
    _exclusive_write(document, REPORT_RELATIVE)
    return document


@contextlib.contextmanager
def _source_only_boundary() -> Iterator[dict[str, int]]:
    counts = {
        "clock_attempts_blocked": 0,
        "worker_attempts_blocked": 0,
        "candidate_import_attempts_blocked": 0,
        "file_read_attempts_blocked": 0,
        "file_write_attempts_blocked": 0,
        "locale_attempts_blocked": 0,
        "candidate_imports": 0,
        "subprocesses": 0,
        "file_reads": 0,
        "file_writes": 0,
        "clock_samples": 0,
    }
    replacements: list[tuple[Any, str, Any]] = []

    def reject(kind: str, label: str) -> Callable[..., Any]:
        def blocked(*args: Any, **kwargs: Any) -> Any:
            del args, kwargs
            counts[kind] += 1
            raise OfficialV5Error(
                "the source-only V5 boundary forbids " + label,
            )

        return blocked

    def replace(target: Any, name: str, value: Any) -> None:
        if hasattr(target, name):
            replacements.append((target, name, getattr(target, name)))
            setattr(target, name, value)

    for name in (
        "time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
        "perf_counter_ns", "process_time", "process_time_ns", "thread_time",
        "thread_time_ns",
    ):
        replace(time, name, reject("clock_attempts_blocked", "clock " + name))
    for target, name in (
        (subprocess, "run"),
        (subprocess, "Popen"),
        (threading.Thread, "start"),
        (multiprocessing.Process, "start"),
    ):
        replace(target, name, reject("worker_attempts_blocked", "worker " + name))
    for name in ("fork", "posix_spawn", "posix_spawnp", "system"):
        replace(os, name, reject("worker_attempts_blocked", "process " + name))
    replace(os, "open", reject("file_read_attempts_blocked", "any file access"))

    def block_builtin_open(
        file: Any, mode: str = "r", *args: Any, **kwargs: Any,
    ) -> Any:
        del file, args, kwargs
        writing = not isinstance(mode, str) or any(
            marker in mode for marker in ("w", "a", "x", "+")
        )
        counter = (
            "file_write_attempts_blocked"
            if writing else "file_read_attempts_blocked"
        )
        counts[counter] += 1
        raise OfficialV5Error("the source-only V5 boundary forbids all files")

    replace(builtins, "open", block_builtin_open)
    replace(io, "open", block_builtin_open)
    for name in (
        "unlink", "remove", "rename", "replace", "mkdir", "makedirs",
    ):
        replace(os, name, reject("file_write_attempts_blocked", "filesystem " + name))
    replace(
        tempfile, "TemporaryDirectory",
        reject("locale_attempts_blocked", "private locale generation"),
    )
    module = sys.modules[__name__]
    for name in ("_exclusive_write",):
        replace(module, name, reject("file_write_attempts_blocked", name))
    for name in ("_read_bounded", "_verify_frozen", "_read_verified_evidence"):
        replace(module, name, reject("file_read_attempts_blocked", name))
    replace(module, "_run_isolated_worker",
            reject("worker_attempts_blocked", "isolated original worker"))
    previous_import = importlib.import_module
    previous_builtin_import = builtins.__import__

    def candidate_name(name: str) -> bool:
        return name == "rebar" or name.startswith("rebar.") or (
            name == "candidates" or name.startswith("candidates.")
        )

    def checked_import(name: str, package: str | None = None) -> Any:
        if candidate_name(name):
            counts["candidate_import_attempts_blocked"] += 1
            raise OfficialV5Error("a source-only V5 test cannot import a candidate")
        return previous_import(name, package)

    def checked_builtin_import(
        name: str,
        globals: Mapping[str, Any] | None = None,
        locals: Mapping[str, Any] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> Any:
        if candidate_name(name):
            counts["candidate_import_attempts_blocked"] += 1
            raise OfficialV5Error("a source-only V5 test cannot import a candidate")
        return previous_builtin_import(name, globals, locals, fromlist, level)

    replace(importlib, "import_module", checked_import)
    replace(builtins, "__import__", checked_builtin_import)
    try:
        yield counts
    finally:
        for target, name, previous in reversed(replacements):
            setattr(target, name, previous)


def _synthetic_matrix() -> list[dict[str, Any]]:
    return [
        {
            "test": identity,
            "source_ast_sha256": hashlib.sha256(
                ("synthetic-only-v5:" + identity).encode("ascii"),
            ).hexdigest(),
        }
        for identity in upstream.PUBLIC_ORIGINAL_METHODS
    ]


def _synthetic_release(
    role: str,
    matrix: list[dict[str, Any]],
) -> dict[str, Any]:
    records = [
        {
            "test": item["test"],
            "source_ast_sha256": item["source_ast_sha256"],
            "status": "PASS",
        }
        for item in matrix
    ]
    for record in records:
        identity = record["test"]
        if identity == "ReTests.test_memory_leaks":
            record.update({
                "status": "SKIP",
                "reason": "requires debug build",
                "skip_kind": "named-private-debug-condition",
            })
        elif identity in {
            "ReTests.test_large_search", "ReTests.test_large_subn",
        }:
            record["resource"] = {
                "delivered_size": 2**31,
                "real_max_memuse": upstream.CONFIGURED_OFFICIAL_MEMORY_BYTES,
                "declared_size": 2**31,
                "dry_run": False,
            }
        elif identity == "ReTests.test_search_anchor_at_beginning":
            record["resource"] = {
                "cpu_resource_enabled": True,
                "subject_characters": 10**7,
                "original_upper_bound_seconds": 0.1,
                "original_stopwatch_assertion_passed": True,
            }
        elif identity == "ReTests.test_regression_gh94675":
            record["resource"] = {
                "process_started": True,
                "start_method": "fork",
                "short_timeout_seconds": 30.0,
            }
    native = {"synthetic-owned-native": "e" * 64}
    native_digest = digest(native)
    guard: dict[str, Any] = {
        "passed": True,
        "candidate_isolation": True,
        "baseline_only": True,
    }
    if role != "stdlib":
        guard = {
            "passed": True,
            "candidate_isolation": True,
            "native_matching_executed": True,
            "stdlib_re_delegation": False,
            "sre_delegation": False,
            "external_package_delegation": False,
            "other_candidate_delegation": False,
            "oracle_maxgroups_constant_only": True,
            "native_binary_sha256": native,
            "native_guard_sha256_before": "d" * 64,
            "native_guard_sha256_after": "d" * 64,
            "native_mapping_sha256_before": native_digest,
            "native_mapping_sha256_after": native_digest,
            "loaded_native_modules_after": [],
        }
    return {
        **upstream.assess_role_records(role, records, matrix),
        "records": records,
        "locale": {
            "fresh_private_localedef": True,
            "iso_8859_1_passed": True,
            "utf_8_passed": True,
        },
        "guard": guard,
        "resource_provenance": {
            "real_max_memuse": upstream.CONFIGURED_OFFICIAL_MEMORY_BYTES,
            "large_method_sizes": {
                "ReTests.test_large_search": 2**31,
                "ReTests.test_large_subn": 2**31,
            },
            "cpu_resource_enabled": True,
            "multiprocessing_extension_available": True,
            "multiprocessing_start_method": "fork",
            "private_debug_fail_after": False,
            "actual_upstream_corpus_cases": 403,
            "actual_external_fixture_assertion_cases": 11,
            "exclusive_big_memory_worker": True,
            "official_support_shim_used": False,
            "official_test_source_rewritten": False,
        },
        "executed_test_source_sha256": upstream.TEST_SOURCE_SHA256,
        "official_support_tree_sha256": upstream.OFFICIAL_SUPPORT_TREE_SHA256,
        "captured_official_stdout": "",
        "captured_official_stderr": "",
        "live_official_fixture_provenance": {
            "actual_upstream_corpus_cases": 403,
            "actual_external_fixture_assertion_cases": 11,
            "support_tree_sha256": upstream.OFFICIAL_SUPPORT_TREE_SHA256,
            "official_support_shim_used": False,
            "modules": {
                "test.support": {
                    "sha256": upstream.UPSTREAM_SUPPORT_INIT_SHA256,
                },
                "test.support.warnings_helper": {
                    "sha256": upstream.UPSTREAM_WARNINGS_HELPER_SHA256,
                },
                "test.re_tests": {
                    "sha256": upstream.CORPUS_SOURCE_SHA256,
                },
            },
        },
    }


def source_self_test() -> dict[str, Any]:
    """Run exclusively synthetic poison controls; never open any file."""
    verify_runtime()
    before = {
        name for name, module in sys.modules.items()
        if module is not None and (
            name == "rebar" or name.startswith("rebar.")
            or name == "candidates" or name.startswith("candidates.")
        )
    }
    require(not before, "a candidate was already imported into the source controller")
    checks: list[dict[str, Any]] = []

    def accept(name: str, condition: Any) -> None:
        require(not any(record["name"] == name for record in checks),
                "a source-only V5 poison control was duplicated")
        checks.append({"name": name, "passed": bool(condition)})

    def rejected(name: str, operation: Callable[[], Any]) -> None:
        try:
            operation()
        except (
            OfficialV5Error, upstream.OfficialV4Error, OSError, ValueError,
            TypeError, KeyError, ImportError,
        ):
            accept(name, True)
        else:
            accept(name, False)

    with _source_only_boundary() as effects:
        matrix = _synthetic_matrix()
        baseline = _synthetic_release("stdlib", matrix)
        accept("freeze-exact-original-152-method-matrix-hash",
               upstream.METHOD_MATRIX_SHA256 == METHOD_MATRIX_SHA256)
        accept("bootstrap-direct-isolation-with-only-the-exact-trusted-root",
               bool(sys.path) and sys.path[0] == str(ROOT))
        accept("preserve-every-one-of-152-original-public-identities",
               len(matrix) == 152 and tuple(item["test"] for item in matrix)
               == upstream.PUBLIC_ORIGINAL_METHODS)
        accept("account-for-all-165-original-upstream-methods",
               upstream.ORIGINAL_METHODS == 165)
        accept("name-and-limit-the-13-original-private-methods",
               upstream.PRIVATE_METHODS == 13
               and len(upstream.PRIVATE_CLASS_WAIVERS) == 2)
        accept("never-waive-an-original-public-method",
               not upstream.PUBLIC_METHOD_WAIVERS)
        accept("preserve-the-complete-26-file-real-support-denominator",
               len(upstream.OFFICIAL_SUPPORT_MODULES) == 26)
        accept("preserve-the-403-real-original-upstream-corpus-denominator",
               upstream.CORPUS_CASES == 403)
        accept("preserve-all-11-original-external-correctness-fixtures",
               upstream.EXTERNAL_FIXTURE_ASSERTION_CASES == 11)
        accept("freeze-the-exact-40-gibibyte-original-memory-limit",
               upstream.CONFIGURED_OFFICIAL_MEMORY_BYTES == 40 * 1024**3)
        accept("preserve-the-real-36-gibibyte-original-subn-declaration",
               upstream.REQUIRED_OFFICIAL_SUBN_MEMORY_BYTES == 38_654_705_664)
        accept("freeze-the-actual-independent-v8-proof-controller",
               V8_PROOF_SOURCE_SHA256
               == "0f9e12847855797669206ea89de94948da66c29742d64820a625ce5a6570b313")
        accept("freeze-the-actual-independent-v8-strict-audit-controller",
               V8_STRICT_SOURCE_SHA256
               == "bb22b1983c11a896d3639077050dfaac746876ccbb9e4909518fb33d19987c01")
        accept("freeze-the-actual-independent-v8-proof-protocol",
               V8_PROOF_PROTOCOL_SHA256
               == "76e66c091ae06ad56b8f4e22c76f4db44810cdb512b839201c9cc7cb83f4cfa0")
        accept("require-two-distinct-real-reference-labels",
               REFERENCE_LABELS == ("reference_a", "reference_b"))
        accept("never-require-old-v7-campaigns-for-python-references",
               "authenticate_production_prerequisites"
               not in authenticate_reference_prerequisites.__code__.co_names
               and "CAMPAIGN_REPORT_SHA256"
               not in authenticate_reference_prerequisites.__code__.co_names)
        accept("never-import-a-candidate-in-reference-prerequisites",
               "authenticate_candidate_prerequisites"
               not in authenticate_reference_prerequisites.__code__.co_names)
        accept("validate-the-synthetic-exact-release-outcome-honestly",
               _validate_role("stdlib", baseline, matrix)["passed"] == 151)
        accept("retain-one-genuine-private-debug-condition-not-a-public-waiver",
               baseline["named_private_debug_skips"] == 1
               and baseline["applicable"] == 151
               and baseline["debug_build_coverage"] == "NOT RUN")
        accept("retain-the-exact-original-bigmem-method-identities",
               {"ReTests.test_large_search", "ReTests.test_large_subn"}
               <= set(upstream.PUBLIC_ORIGINAL_METHODS))
        accept("retain-the-exact-original-cpu-and-real-process-methods",
               {"ReTests.test_search_anchor_at_beginning",
                "ReTests.test_regression_gh94675"}
               <= set(upstream.PUBLIC_ORIGINAL_METHODS))
        accept("retain-the-exact-original-public-group-reference-overflow",
               "ReTests.test_re_groupref_overflow"
               in upstream.PUBLIC_ORIGINAL_METHODS)
        accept("retain-both-original-external-fixture-test-methods",
               {"ExternalTests.test_re_tests", "ExternalTests.test_re_benchmarks"}
               <= set(upstream.PUBLIC_ORIGINAL_METHODS))
        accept("retain-the-real-unknown-flags-representation-method",
               "PatternReprTests.test_unknown_flags"
               in upstream.PUBLIC_ORIGINAL_METHODS)
        accept("keep-synthetic-source-controls-out-of-official-evidence",
               all(row["source_ast_sha256"] != METHOD_MATRIX_SHA256
                   for row in matrix))

        def poison(name: str, transform: Callable[[dict[str, Any]], None]) -> None:
            altered = copy.deepcopy(baseline)
            transform(altered)
            rejected(name, lambda: _validate_role("stdlib", altered, matrix))

        poison("reject-a-missing-real-original-method",
               lambda report: report["records"].pop())
        poison("reject-a-reordered-real-original-method",
               lambda report: report["records"].reverse())
        poison("reject-a-substituted-real-original-method-body",
               lambda report: report["records"][0].update(
                   {"source_ast_sha256": "0" * 64},
               ))
        poison("reject-captured-original-upstream-stderr",
               lambda report: report.update({
                   "captured_official_stderr": "synthetic source-only poison",
               }))
        accept("accept-only-an-actually-empty-original-worker-stderr-stream",
               _validate_worker_stderr("stdlib", b"", {}) is None)
        rejected("reject-actual-worker-level-native-or-process-stderr",
                 lambda: _validate_worker_stderr(
                     "stdlib", b"synthetic source-only stderr poison", {
                         "stderr": upstream._bounded_failure_stream(
                             b"synthetic source-only stderr poison",
                         ),
                     },
                 ))
        poison("reject-an-actual-unexplained-original-public-skip",
               lambda report: report["records"][0].update(
                   {"status": "SKIP", "reason": "synthetic resource skip"},
               ))
        for status in ("FAIL", "ERROR", "TIMEOUT", "CRASH"):
            poison("reject-actual-original-method-" + status.lower(),
                   lambda report, status=status: report["records"][0].update({
                       "status": status, "reason": "source-only poison",
                   }))
        poison("reject-a-dry-run-disguised-as-two-gibibytes",
               lambda report: next(
                   row for row in report["records"]
                   if row["test"] == "ReTests.test_large_subn"
               )["resource"].update({"delivered_size": 5_147, "dry_run": True}))
        poison("reject-a-real-bigmem-role-without-40-gibibytes",
               lambda report: report["resource_provenance"].update(
                   {"real_max_memuse": 0},
               ))
        poison("reject-a-real-bigmem-role-with-a-substituted-36-gibibyte-limit",
               lambda report: report["resource_provenance"].update({
                   "real_max_memuse": upstream.REQUIRED_OFFICIAL_SUBN_MEMORY_BYTES,
               }))
        for key in (
            "cpu_resource_enabled", "multiprocessing_extension_available",
            "exclusive_big_memory_worker",
        ):
            poison("reject-missing-authentic-resource-" + key,
                   lambda report, key=key:
                   report["resource_provenance"].update({key: False}))
        poison("reject-a-changed-genuine-fork-start-method",
               lambda report: report["resource_provenance"].update(
                   {"multiprocessing_start_method": "spawn"},
               ))
        for key, wrong in (
            ("actual_upstream_corpus_cases", 400),
            ("actual_external_fixture_assertion_cases", 10),
        ):
            poison("reject-a-substituted-original-fixture-" + key,
                   lambda report, key=key, wrong=wrong:
                   report["resource_provenance"].update({key: wrong}))
        for key in ("official_support_shim_used", "official_test_source_rewritten"):
            poison("reject-synthetic-upstream-substitution-" + key,
                   lambda report, key=key:
                   report["resource_provenance"].update({key: True}))
        poison("reject-a-falsified-release-private-debug-hook",
               lambda report: report["resource_provenance"].update(
                   {"private_debug_fail_after": True},
               ))
        for key in (
            "fresh_private_localedef", "iso_8859_1_passed", "utf_8_passed",
        ):
            poison("reject-missing-genuine-private-locale-" + key,
                   lambda report, key=key: report["locale"].update({key: False}))
        poison("reject-a-missing-genuine-original-process-start",
               lambda report: next(
                   row for row in report["records"]
                   if row["test"] == "ReTests.test_regression_gh94675"
               )["resource"].update({"process_started": False}))
        poison("reject-a-failed-real-original-stopwatch-assertion",
               lambda report: next(
                   row for row in report["records"]
                   if row["test"] == "ReTests.test_search_anchor_at_beginning"
               )["resource"].update({
                   "original_stopwatch_assertion_passed": False,
               }))
        for family in FAMILIES:
            candidate = _synthetic_release(family, matrix)
            accept("validate-in-memory-independent-native-guard:" + family,
                   _validate_role(family, candidate, matrix)["passed"] == 151)
            for key in (
                "stdlib_re_delegation", "sre_delegation",
                "external_package_delegation", "other_candidate_delegation",
            ):
                changed = copy.deepcopy(candidate)
                changed["guard"][key] = True
                rejected("reject-native-delegation:" + family + ":" + key,
                         lambda changed=changed, family=family:
                         _validate_role(family, changed, matrix))
            for key in ("passed", "candidate_isolation", "native_matching_executed",
                        "oracle_maxgroups_constant_only"):
                changed = copy.deepcopy(candidate)
                changed["guard"][key] = False
                rejected("reject-broken-native-guard:" + family + ":" + key,
                         lambda changed=changed, family=family:
                         _validate_role(family, changed, matrix))
            for key in ("native_guard_sha256_after", "native_mapping_sha256_after"):
                changed = copy.deepcopy(candidate)
                changed["guard"][key] = "0" * 64
                rejected("reject-changed-native-observation:" + family + ":" + key,
                         lambda changed=changed, family=family:
                         _validate_role(family, changed, matrix))
        for name, relative in (
            ("absolute", "/tmp/forged-postfinal-locale-v5.json"),
            ("traversal", "oracle/cpython-3.14.6/evidence/../forged.json"),
            ("old-v4", upstream.REPORT_RELATIVE),
            ("backslash", "oracle\\cpython-3.14.6\\forged.json"),
            ("nul", "oracle/cpython-3.14.6/evidence/forged\x00.json"),
        ):
            rejected("reject-unsafe-or-historical-output:" + name,
                     lambda relative=relative: _safe_output_path(relative))
        for relative in sorted(APPROVED_OUTPUTS):
            accept("allow-only-the-exact-v5-output:" + relative,
                   _safe_output_path(relative) == ROOT / relative)
        rejected("reject-all-unpublished-current-build-candidate-pins",
                 lambda: _candidate_pin_values({}))
        fabricated = {
            "v8_base_source": V8_BASE_SOURCE_SHA256,
            "v8_base_report": "a" * 64,
            "v8_strict_source": V8_STRICT_SOURCE_SHA256,
            "v8_strict_report": "c" * 64,
            **{
                name + "_" + kind: hashlib.sha256(
                    ("synthetic-only-v5:" + name + ":" + kind).encode("ascii"),
                ).hexdigest()
                for name in FAMILIES for kind in ("edge", "deep")
            },
        }
        accept("validate-ten-distinct-synthetic-candidate-pin-shapes-only",
               len(_candidate_pin_values(fabricated)) == 10)
        for name in tuple(fabricated):
            omitted = dict(fabricated)
            del omitted[name]
            rejected("reject-each-omitted-independent-candidate-pin:" + name,
                     lambda omitted=omitted: _candidate_pin_values(omitted))
        repeated = dict(fabricated)
        repeated["zig_deep"] = repeated["rust_edge"]
        rejected("reject-a-cross-family-reused-qualified-proof-fingerprint",
                 lambda: _candidate_pin_values(repeated))
        wrong_base = dict(fabricated)
        wrong_base["v8_base_source"] = "f" * 64
        rejected("reject-a-substituted-independently-frozen-v8-base-source",
                 lambda: _candidate_pin_values(wrong_base))
        wrong_strict = dict(fabricated)
        wrong_strict["v8_strict_source"] = "f" * 64
        rejected("reject-a-substituted-independently-frozen-v8-strict-source",
                 lambda: _candidate_pin_values(wrong_strict))
        for name in ("time", "monotonic", "perf_counter", "process_time"):
            rejected("forbid-every-source-only-clock:" + name,
                     lambda name=name: getattr(time, name)())
        rejected("forbid-source-only-subprocess",
                 lambda: subprocess.run([str(upstream.PINNED_CPYTHON), "-V"]))
        rejected("forbid-source-only-thread",
                 lambda: threading.Thread(target=lambda: None).start())
        for family in FAMILIES:
            rejected("forbid-source-only-candidate-import:" + family,
                     lambda family=family:
                     importlib.import_module("candidates." + family + "_candidate"))
        rejected("forbid-source-only-builtin-candidate-import",
                 lambda: builtins.__import__("candidates.rust_candidate"))
        rejected("forbid-source-only-os-file-read",
                 lambda: os.open(ROOT / SOURCE_RELATIVE, os.O_RDONLY))
        rejected("forbid-source-only-builtin-file-read",
                 lambda: builtins.open(ROOT / SOURCE_RELATIVE, "r"))
        rejected("forbid-source-only-path-file-read",
                 lambda: (ROOT / SOURCE_RELATIVE).open("r"))
        rejected("forbid-source-only-builtin-file-write",
                 lambda: builtins.open(ROOT / "v5-forbidden-control", "w"))
        rejected("forbid-source-only-path-file-write",
                 lambda: (ROOT / "v5-forbidden-control").open("w"))
        rejected("forbid-source-only-exclusive-report",
                 lambda: _exclusive_write({"synthetic": True}, REPORT_RELATIVE))
        rejected("forbid-source-only-existing-evidence-read",
                 lambda: _read_verified_evidence(REPORT_RELATIVE, "0" * 64))
        rejected("forbid-source-only-frozen-source-read",
                 lambda: _verify_frozen(SOURCE_RELATIVE, "0" * 64, 100))
        rejected("forbid-source-only-real-original-worker",
                 lambda: _run_isolated_worker(
                     "stdlib", "reference_a", "0" * 64, "0" * 64, {},
                 ))
        rejected("forbid-source-only-real-private-locale",
                 lambda: tempfile.TemporaryDirectory())
        accept("actually-block-all-source-only-external-effects",
               effects["clock_attempts_blocked"] >= 4
               and effects["worker_attempts_blocked"] >= 3
               and effects["candidate_import_attempts_blocked"] >= 4
               and effects["file_read_attempts_blocked"] >= 5
               and effects["file_write_attempts_blocked"] >= 3
               and effects["locale_attempts_blocked"] >= 1)
        accept("never-actually-read-a-source-fixture-or-evidence-file",
               effects["file_reads"] == 0 and effects["file_writes"] == 0)
        accept("never-actually-start-a-worker-sample-a-clock-or-import-a-candidate",
               effects["subprocesses"] == 0 and effects["clock_samples"] == 0
               and effects["candidate_imports"] == 0)
        after = {
            name for name, module in sys.modules.items()
            if module is not None and (
                name == "rebar" or name.startswith("rebar.")
                or name == "candidates" or name.startswith("candidates.")
            )
        }
        accept("leave-the-real-controller-free-of-any-candidate-module",
               after == before)
        failed = [item["name"] for item in checks if item["passed"] is not True]
        require(not failed,
                "an actual V5 source-only poison control failed: "
                + ", ".join(failed))
        require(len(checks) >= 69,
                "at least 69 actual candidate-free V5 source poisons are required")
        observed_effects = dict(effects)
    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "passed": True,
        "check_count": len(checks),
        "checks": checks,
        "python": "3.14.6",
        "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
        "original_public_method_count": 152,
        "synthetic_poison_controls_are_official_results": False,
        "candidate_imports": 0,
        "subprocesses": 0,
        "file_reads": 0,
        "file_writes": 0,
        "clock_samples": 0,
        "actual_official_roles_run": 0,
        "actual_official_method_checks": 0,
        "actual_reference_workers": 0,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "effects": observed_effects,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def _memory_environment() -> dict[str, Any]:
    available: int | None = None
    with builtins.open("/proc/meminfo", "r", encoding="ascii") as source:
        payload = source.read(65_537)
    require(len(payload) <= 65_536,
            "the actual host-memory preflight exceeded its bounded source")
    for line in payload.splitlines():
        fields = line.split()
        if len(fields) == 3 and fields[0] == "MemAvailable:" and fields[2] == "kB":
            available = int(fields[1]) * 1024
            break
    require(available is not None and available > 0,
            "the genuine available host memory cannot be authenticated")
    memory_max: int | None = None
    memory_current: int | None = None
    cgroup_limit = Path("/sys/fs/cgroup/memory.max")
    if cgroup_limit.is_file():
        with builtins.open(cgroup_limit, "r", encoding="ascii") as source:
            raw_limit = source.read(129).strip()
        require(len(raw_limit) <= 128,
                "the genuine cgroup memory limit exceeded its bounded source")
        if raw_limit != "max":
            memory_max = int(raw_limit)
            with builtins.open(
                "/sys/fs/cgroup/memory.current", "r", encoding="ascii",
            ) as source:
                raw_current = source.read(129).strip()
            require(len(raw_current) <= 128,
                    "the genuine current cgroup memory exceeded its bound")
            memory_current = int(raw_current)
    effective = available
    if memory_max is not None:
        require(memory_current is not None and memory_max >= memory_current,
                "the genuine cgroup memory limit is inconsistent")
        effective = min(effective, memory_max - memory_current)
    return {
        "host_mem_available_bytes": available,
        "cgroup_memory_max_bytes": memory_max,
        "cgroup_memory_current_bytes": memory_current,
        "effective_available_memory_bytes": effective,
        "required_original_subn_memory_bytes": (
            upstream.REQUIRED_OFFICIAL_SUBN_MEMORY_BYTES
        ),
        "configured_original_memory_bytes": (
            upstream.CONFIGURED_OFFICIAL_MEMORY_BYTES
        ),
        "sufficient_for_actual_original_subn": (
            effective >= upstream.REQUIRED_OFFICIAL_SUBN_MEMORY_BYTES
        ),
    }


def preflight() -> dict[str, Any]:
    verify_runtime()
    _verify_frozen(upstream.SOURCE_RELATIVE, V4_SOURCE_SHA256, MAX_SOURCE_BYTES)
    _verify_frozen(upstream.PROTOCOL_RELATIVE, V4_PROTOCOL_SHA256, MAX_SOURCE_BYTES)
    official = upstream.introspect_official_sources()
    environment = upstream.inspect_environment()
    memory = _memory_environment()
    blockers: list[str] = []
    if official.get("public_method_matrix_sha256") != METHOD_MATRIX_SHA256:
        blockers.append("the actual complete 152-method original AST matrix changed")
    if environment.get("authenticated_official_support_available") is not True:
        blockers.append("the genuine complete 26-file upstream support is unavailable")
    if environment.get("multiprocessing_extension_available") is not True:
        blockers.append("the actual original multiprocessing regression would skip")
    if environment.get("localedef_program_available") is not True:
        blockers.append("the original private ISO-8859-1 and UTF-8 locales cannot run")
    if memory["sufficient_for_actual_original_subn"] is not True:
        blockers.append("insufficient real available memory for the original 36-GiB subn")
    return {
        "schema": SCHEMA + "-preflight",
        "status": "READY" if not blockers else "BLOCKED",
        "python": "3.14.6",
        "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
        "original_public_method_count": 152,
        "public_method_waivers": [],
        "environment": environment,
        "memory": memory,
        "blockers": blockers,
        "reference_requires_candidate_audits": False,
        "reference_requires_candidate_proofs": False,
        "reference_requires_old_v7_campaigns": False,
        "actual_official_roles_run": 0,
        "actual_official_method_checks": 0,
        "candidate_imports": 0,
        "native_workers_started": 0,
        "evidence_files_read": 0,
        "evidence_files_written": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def _failure_document(
    error: OfficialV5WorkerFailure,
    options: argparse.Namespace,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-actual-role-failure",
        "status": "FAIL",
        "role": error.role,
        "reason": str(error),
        "details": error.details,
        "source_sha256": options.source_sha256,
        "protocol_sha256": options.protocol_sha256,
        "synthetic": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def parse_arguments(arguments: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the unchanged complete original Python regex suite.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--self-oracle", action="store_true")
    mode.add_argument("--candidate", choices=("all", *FAMILIES))
    parser.add_argument("--source-sha256")
    parser.add_argument("--protocol-sha256")
    parser.add_argument("--reference-sha256")
    parser.add_argument("--v8-base-source-sha256")
    parser.add_argument("--v8-base-report-sha256")
    parser.add_argument("--v8-strict-source-sha256")
    parser.add_argument("--v8-strict-report-sha256")
    for family in FAMILIES:
        parser.add_argument("--" + family + "-edge-sha256")
        parser.add_argument("--" + family + "-deep-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    try:
        if options.self_test:
            document = source_self_test()
        elif options.preflight:
            document = preflight()
        elif options.self_oracle:
            require(valid_sha256(options.source_sha256)
                    and valid_sha256(options.protocol_sha256),
                    "BLOCKED: publish only the actual frozen V5 source and protocol")
            document = run_self_oracle(
                options.source_sha256, options.protocol_sha256,
            )
        else:
            require(valid_sha256(options.source_sha256)
                    and valid_sha256(options.protocol_sha256)
                    and valid_sha256(options.reference_sha256),
                    "BLOCKED: publish the actual V5 source, protocol, and "
                    "genuine two-reference report first")
            supplied = {
                "v8_base_source": options.v8_base_source_sha256,
                "v8_base_report": options.v8_base_report_sha256,
                "v8_strict_source": options.v8_strict_source_sha256,
                "v8_strict_report": options.v8_strict_report_sha256,
                **{
                    family + "_" + kind:
                    getattr(options, family + "_" + kind + "_sha256")
                    for family in FAMILIES for kind in ("edge", "deep")
                },
            }
            document = run_candidates(
                options.candidate,
                options.source_sha256,
                options.protocol_sha256,
                options.reference_sha256,
                supplied,
            )
    except OfficialV5WorkerFailure as error:
        failure = _failure_document(error, options)
        relative = (
            SELF_ORACLE_FAILURE_RELATIVE
            if error.role == "stdlib"
            else ROLE_FAILURE_RELATIVES.get(error.role)
        )
        if relative is not None:
            try:
                failure["exclusive_report_sha256"] = _exclusive_write(
                    failure, relative,
                )
                failure["exclusive_report_path"] = relative
            except (OfficialV5Error, OSError) as preservation_error:
                failure["preservation_error"] = str(preservation_error)
        print(json.dumps(failure, sort_keys=True, separators=(",", ":")),
              file=sys.stderr)
        return 2
    except (
        OfficialV5Error, upstream.OfficialV4Error, OSError, MemoryError,
        subprocess.SubprocessError, UnicodeError, ValueError,
    ) as error:
        print(json.dumps({
            "schema": SCHEMA + "-controller-failure",
            "status": "BLOCKED",
            "reason": str(error),
            "native_workers_started": 0,
            "evidence_files_written": 0,
            "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED",
        }, sort_keys=True, separators=(",", ":")), file=sys.stderr)
        return 2
    print(json.dumps(document, sort_keys=True, separators=(",", ":")))
    if options.preflight and document["status"] != "READY":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
