#!/usr/bin/env python3
"""Exclusively preserve the five independently verified public-V6 native ELFs."""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_public_native_archive_v1 as inherited


SCHEMA = "rebar-postfinal-public-native-archive-v2"
SOURCE_RELATIVE = "tools/postfinal_public_native_archive_v2.py"
SOURCE = ROOT / SOURCE_RELATIVE
PREVIOUS_SOURCE_RELATIVE = "tools/postfinal_public_native_archive_v1.py"
PREVIOUS_SOURCE_SHA256 = (
    "49f9d32ff619aeb43dda5811f6f9cf3c66ce5ec819b06b74f0599c1bcf619101"
)
PUBLIC_VERSION = "postfinal-public-practice-v6"
EVIDENCE_RELATIVE = "performance/postfinal-public-v6/evidence"
EVIDENCE = ROOT / EVIDENCE_RELATIVE
ARCHIVE_ROOT_RELATIVE = EVIDENCE_RELATIVE + "/native-archive-v1"
ARCHIVE_ROOT = ROOT / ARCHIVE_ROOT_RELATIVE
ARCHIVE_MANIFEST_RELATIVE = (
    EVIDENCE_RELATIVE + "/postfinal-public-v6-native-archive-v1.json"
)
ARCHIVE_MANIFEST = ROOT / ARCHIVE_MANIFEST_RELATIVE
PINNED_PYTHON = inherited.PINNED_PYTHON
PINNED_VERSION = inherited.PINNED_VERSION
MAX_ELF_BYTES = inherited.MAX_ELF_BYTES
MAX_JSON_BYTES = inherited.MAX_JSON_BYTES
MAX_SOURCE_BYTES = inherited.MAX_SOURCE_BYTES
MAX_PUBLIC_V6_SUMMARY_BYTES = 20 * 1024 * 1024
PINNED_PUBLIC_V6_SUMMARY_BYTES = 18_592_770
GZIP_HEADER = inherited.GZIP_HEADER
QUALIFIED_SOURCES = inherited.QUALIFIED_SOURCES
PROOFS: dict[str, tuple[str, str]] = {
    "manifest": (
        "performance/postfinal-public-v6/manifest.json",
        "65e024a1a79d13b03e4e5ad0f3d4ae010dbb6e4f09b52a8542837a2ea4c6198a",
    ),
    "summary": (
        "performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-summary.json",
        "539fe6ba0ac492ffab121845da21033676ad7e7154ce9107f7f1778f55ceed4c",
    ),
    "integrity": (
        "performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-integrity.json",
        "8eb2e6bba6894a71f63e32cc35cca5317bb1beccc32c2905bbeacebedb868fd2",
    ),
    "base-audit": (
        "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json",
        "5e299a767cbd494683100519a6ad461d1a0eb9de1564b1437c7e0229cca7a551",
    ),
    "strict-audit": (
        "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V2.json",
        "183cd04f5e1587c181505c09867566b4bd18db270f974475c2b456ff09af1d9f",
    ),
    "runner-source": (
        "tools/postfinal_public_practice_v6.py",
        "16a56d1573526894733b6284204ff3712b4d4e2a9c63027d51b8de1869df3fc3",
    ),
    "base-audit-source": (
        "tools/postfinal_from_scratch_audit_v2.py",
        "6f540074c9f7f4bdffe9e53939efe4cec25e5c029ca1f73ec791d377bddc9306",
    ),
    "strict-audit-source": (
        "tools/postfinal_no_delegation_audit_v2.py",
        "571c11885f9c9694025ea0434e57bfaa56651057eee62fa4396a2bcb95ae4cb5",
    ),
    "previous-archive-source": (
        PREVIOUS_SOURCE_RELATIVE,
        PREVIOUS_SOURCE_SHA256,
    ),
}
ROLES: dict[str, tuple[str, str, str, int]] = {
    "vm-native": (
        "candidates.vm_candidate:native-engine",
        "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "6922d0869b67c82be9ae89a8f00c71777c04472d3606a33527bb13494326f18d",
        159_464,
    ),
    "rust-engine": (
        "candidates.rust_candidate:native-engine",
        "candidates/_rust_engine.so",
        "83394c5c3b5d9e9d98c8474aac60ca5a81517dc7ec7c53b3b625e6ed0a04c165",
        651_024,
    ),
    "rust-bridge": (
        "candidates.rust_candidate:native-bridge",
        "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "81fc4c4a92005f0588dd9b811988587d4d421dd8e1102eebcab53f4deb27cd36",
        136_096,
    ),
    "zig-engine": (
        "candidates.zig_candidate:native-engine",
        "candidates/_zig_probe.so",
        "474dde0bfb23f107f21ec4834ce15dbd1b437841bd171698de623d1c03742988",
        491_688,
    ),
    "zig-bridge": (
        "candidates.zig_candidate:native-bridge",
        "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        "32dadc46281d13df784693f0785d4d149e6d3cd000aa3de6eb220a4a9ed50c9c",
        120_992,
    ),
}
RECORD_FIELDS = inherited.RECORD_FIELDS
HISTORICAL_RUST_SOURCE_PATH = "candidates/rust/src/lib.rs"
HISTORICAL_RUST_SOURCE_SHA256 = (
    "398773b8542c88cfc55fe13ceac1e84a00155217b76b8461ddf9704d2f6c82c5"
)


class ArchiveV2Error(RuntimeError):
    """The unique source-bound public-V6 native archive is unsafe or invalid."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ArchiveV2Error(message)


def canonical(document: Any) -> bytes:
    return inherited.canonical(document)


def valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def candidate_free() -> None:
    try:
        inherited.candidate_free()
    except inherited.ArchiveError as error:
        raise ArchiveV2Error("the V6 archive controller imported a candidate") from error


def production_runtime() -> dict[str, Any]:
    try:
        return inherited.production_runtime()
    except (inherited.ArchiveError, OSError) as error:
        raise ArchiveV2Error("V6 preservation requires pinned CPython 3.14.6 -I -B") from error


def validate_proof_size(name: str, size: Any) -> int:
    require(name in PROOFS, "an unapproved V6 public proof was selected")
    maximum = MAX_PUBLIC_V6_SUMMARY_BYTES if name == "summary" else MAX_JSON_BYTES
    if name.endswith("source"):
        maximum = MAX_SOURCE_BYTES
    require(
        type(size) is int and 0 < size <= maximum,
        f"the exact V6 public {name} proof exceeds its individual finite bound",
    )
    if name == "summary":
        require(
            size == PINNED_PUBLIC_V6_SUMMARY_BYTES,
            "the exact measured 18,592,770-byte V6 summary was substituted",
        )
    return maximum


def fingerprint(
    path: Path, maximum: int, *, retain: bool = False
) -> dict[str, Any]:
    try:
        return inherited.fingerprint(path, maximum, retain=retain)
    except (inherited.ArchiveError, OSError, TypeError, ValueError) as error:
        raise ArchiveV2Error("an exact owned V6 public artifact is unsafe") from error


def load_proof(name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    require(name in PROOFS, "a foreign or private proof was selected")
    relative, expected = PROOFS[name]
    maximum = MAX_PUBLIC_V6_SUMMARY_BYTES if name == "summary" else MAX_JSON_BYTES
    require(
        name in {"manifest", "summary", "integrity", "base-audit", "strict-audit"},
        "only explicit V6 public JSON proof paths may be decoded",
    )
    observed = fingerprint(ROOT / relative, maximum, retain=True)
    validate_proof_size(name, observed["bytes"])
    require(observed["sha256"] == expected, f"the pinned public V6 {name} proof changed")
    try:
        document = json.loads(observed["payload"])
    except (TypeError, ValueError, UnicodeError) as error:
        raise ArchiveV2Error(f"the exact public V6 {name} proof is invalid JSON") from error
    require(isinstance(document, dict), f"the exact public V6 {name} proof is not an object")
    return document, observed


def exact_native_map(value: Any, *, allow_extras: bool = False) -> dict[str, str]:
    expected = {item[0]: item[2] for item in ROLES.values()}
    require(isinstance(value, dict), "public V6 omitted its exact native role map")
    if not allow_extras:
        require(set(value) == set(expected), "public V6 changed its five native roles")
    observed = {name: value.get(name) for name in expected}
    require(observed == expected, "public V6 swapped or changed a measured native ELF")
    return observed


def validate_controls(value: Any, count: int) -> None:
    try:
        inherited.check_controls(value, count)
    except inherited.ArchiveError as error:
        raise ArchiveV2Error("a complete V2 76/32-control source audit changed") from error


def validate_frozen_proofs(
    plan: Any,
    summary: Any,
    integrity: Any,
    base: Any,
    strict: Any,
) -> dict[str, Any]:
    require(
        all(isinstance(item, dict) for item in (plan, summary, integrity, base, strict)),
        "the exclusive V6 archive is missing an exact public proof",
    )
    require(
        plan.get("protocol_version") == PUBLIC_VERSION
        and plan.get("postfinal_schema") == "rebar-postfinal-public-practice-plan-v6"
        and plan.get("runner_sha256") == PROOFS["runner-source"][1]
        and plan.get("holdout_accessed") is False
        and plan.get("held_out_cases_generated") == 0
        and plan.get("held_out_records_deserialized") == 0
        and plan.get("failed") == 0,
        "the immutable, public-only V6 prospective manifest was substituted",
    )
    require(
        summary.get("protocol_version") == PUBLIC_VERSION
        and summary.get("postfinal_schema") == "rebar-postfinal-public-practice-report-v6"
        and summary.get("manifest_sha256") == PROOFS["manifest"][1]
        and summary.get("runner_sha256") == PROOFS["runner-source"][1]
        and summary.get("holdout_accessed") is False
        and summary.get("held_out_cases_generated") == 0
        and summary.get("held_out_records_deserialized") == 0
        and summary.get("failed") == 0,
        "the independently measured, public-only V6 summary was substituted",
    )
    require(
        integrity.get("schema") == "rebar-postfinal-public-practice-integrity-v6"
        and integrity.get("protocol_version") == PUBLIC_VERSION
        and integrity.get("result") == "PASS"
        and integrity.get("manifest_sha256") == PROOFS["manifest"][1]
        and integrity.get("summary_sha256") == PROOFS["summary"][1]
        and integrity.get("runner_sha256") == PROOFS["runner-source"][1]
        and integrity.get("verified_native_library_count") == 5
        and integrity.get("from_scratch_control_count") == 76
        and integrity.get("postfinal_no_delegation_control_count") == 32
        and integrity.get("candidate_imported") is False
        and integrity.get("timing_performed") is False
        and integrity.get("holdout_accessed") is False
        and integrity.get("held_out_cases_generated") == 0
        and integrity.get("held_out_records_deserialized") == 0
        and integrity.get("failed") == 0,
        "the independently replayed public V6 integrity evidence was substituted",
    )
    expected = exact_native_map(plan.get("native_elf_fingerprints"))
    require(
        exact_native_map(integrity.get("native_elf_fingerprints")) == expected,
        "the frozen public V6 plan and independent replay disagree about native ELFs",
    )
    for document in (summary, integrity):
        require(
            exact_native_map(
                document.get("candidate_binary_sha256_before"), allow_extras=True
            )
            == expected
            and exact_native_map(
                document.get("candidate_binary_sha256_after"), allow_extras=True
            )
            == expected,
            "a current V6 native binary changed before or after measurement",
        )
    validate_controls(base.get("self_test"), 76)
    validate_controls(strict.get("self_test"), 32)
    validate_controls(strict.get("inherited_self_test"), 76)
    require(
        base.get("schema_version") == 1
        and base.get("audit") == "bounded-from-scratch-engine-provenance"
        and base.get("postfinal_schema") == "rebar-postfinal-from-scratch-audit-v2"
        and base.get("status") == "PASS"
        and base.get("result") == "PASS"
        and base.get("passed") is True
        and base.get("audit_source_path") == PROOFS["base-audit-source"][0]
        and base.get("audit_source_sha256") == PROOFS["base-audit-source"][1],
        "the immutable public V6 76-control V2 source audit was substituted",
    )
    require(
        strict.get("schema") == "rebar-postfinal-no-delegation-audit-v2"
        and strict.get("postfinal_schema") == "rebar-postfinal-no-delegation-audit-v2"
        and strict.get("status") == "PASS"
        and strict.get("result") == "PASS"
        and strict.get("passed") is True
        and strict.get("base_audit_report_sha256") == PROOFS["base-audit"][1]
        and strict.get("base_audit_source_sha256") == PROOFS["base-audit-source"][1]
        and strict.get("audit_source_sha256") == PROOFS["strict-audit-source"][1]
        and strict.get("inherited_control_count") == 76
        and exact_native_map(strict.get("native_elf_fingerprints")) == expected,
        "the immutable public V6 32-control native-isolation audit was substituted",
    )
    for document in (plan, summary, integrity):
        require(
            document.get("from_scratch_audit_sha256") == PROOFS["base-audit"][1]
            and document.get("postfinal_no_delegation_audit_sha256")
            == PROOFS["strict-audit"][1]
            and document.get("postfinal_no_delegation_control_count") == 32,
            "a public V6 proof changed its exact 76/32-control source audits",
        )
    source_hashes = plan.get("qualified_source_fingerprints")
    require(
        isinstance(source_hashes, dict)
        and set(source_hashes) == QUALIFIED_SOURCES
        and all(valid_sha256(value) for value in source_hashes.values())
        and integrity.get("qualified_source_fingerprints") == source_hashes
        and source_hashes.get(HISTORICAL_RUST_SOURCE_PATH)
        == HISTORICAL_RUST_SOURCE_SHA256
        and strict.get("qualified_source_fingerprints") == source_hashes,
        "the immutable V6 historical source map or original Rust architecture changed",
    )
    candidate_free()
    return {"native": expected, "sources": dict(source_hashes)}


def proof_state() -> dict[str, Any]:
    """Read only named immutable public evidence; never fingerprint live source."""

    candidate_free()
    require(
        Path(inherited.__file__).resolve() == (ROOT / PREVIOUS_SOURCE_RELATIVE).resolve(),
        "the immutable V1 archive verifier was imported from a substituted source",
    )
    plan, _ = load_proof("manifest")
    summary, _ = load_proof("summary")
    integrity, _ = load_proof("integrity")
    base, _ = load_proof("base-audit")
    strict, _ = load_proof("strict-audit")
    for name in (
        "runner-source",
        "base-audit-source",
        "strict-audit-source",
        "previous-archive-source",
    ):
        path, expected = PROOFS[name]
        observed = fingerprint(ROOT / path, MAX_SOURCE_BYTES)
        require(observed["sha256"] == expected, f"a frozen public V6 source changed: {name}")
    return validate_frozen_proofs(plan, summary, integrity, base, strict)


def archive_records(records: Any) -> dict[str, dict[str, Any]]:
    require(
        isinstance(records, dict) and set(records) == set(ROLES),
        "the immutable V6 archive omitted, duplicated, or added a native role",
    )
    seen: set[str] = set()
    for label, (role, source, digest, size) in ROLES.items():
        item = records[label]
        relative = ARCHIVE_ROOT_RELATIVE + "/" + label + ".elf.gz"
        require(
            isinstance(item, dict)
            and set(item) == RECORD_FIELDS
            and item.get("role") == role
            and item.get("source_path") == source
            and item.get("source_sha256") == digest
            and item.get("source_bytes") == size
            and item.get("source_mode") == 0o700
            and item.get("archive_path") == relative
            and valid_sha256(item.get("compressed_sha256"))
            and type(item.get("compressed_bytes")) is int
            and len(GZIP_HEADER) < item["compressed_bytes"] <= MAX_ELF_BYTES
            and str(PurePosixPath(relative)) == relative,
            "a measured V6 native role, digest, mode, or exclusive path was changed",
        )
        require(relative not in seen, "the exclusive V6 native archive reused a slot")
        seen.add(relative)
    return records


def verify_archive_provenance(
    document: Any,
    *,
    source_sha256: str,
    runtime: Mapping[str, Any],
    state: Mapping[str, Any],
) -> None:
    expected_proofs = {
        name: {"path": pair[0], "sha256": pair[1]}
        for name, pair in PROOFS.items()
    }
    require(
        isinstance(document, dict)
        and document.get("schema") == SCHEMA
        and document.get("status") == "PASS"
        and document.get("result") == "PASS"
        and document.get("passed") is True
        and document.get("public_protocol_version") == PUBLIC_VERSION
        and document.get("archive_source_path") == SOURCE_RELATIVE
        and valid_sha256(source_sha256)
        and document.get("archive_source_sha256") == source_sha256
        and document.get("inherited_archive_source_path") == PREVIOUS_SOURCE_RELATIVE
        and document.get("inherited_archive_source_sha256") == PREVIOUS_SOURCE_SHA256
        and document.get("pinned_interpreter") == json.loads(canonical(runtime))
        and document.get("proofs") == expected_proofs
        and document.get("v6_native_elf_fingerprints") == state.get("native")
        and document.get("v6_qualified_source_fingerprints") == state.get("sources")
        and document.get("native_archive_count") == len(ROLES) == 5
        and document.get("gzip")
        == {
            "compresslevel": 9,
            "filename": "",
            "mtime": 0,
            "header_hex": GZIP_HEADER.hex(),
        },
        "the immutable public V6 archive lost its genuine proof or source provenance",
    )
    scope = document.get("scope")
    require(
        isinstance(scope, dict)
        and scope.get("archive_is_historical_bytes_only") is True
        and scope.get("current_live_source_files_read") == 0
        and scope.get("current_runtime_native_mapping_attested") is False
        and scope.get("current_candidate_qualification_attested") is False
        and scope.get("source_to_binary_reproducibility_attested") is False
        and scope.get("automatic_native_restoration_permitted") is False
        and scope.get("candidate_imported") is False
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "the V6 historical archive falsely claims native execution or source restoration",
    )
    archive_records(document.get("records"))


def open_exact_directory(path: Path, expected: Path) -> int:
    try:
        return inherited.open_exact_directory(path, expected)
    except (inherited.ArchiveError, OSError, ValueError) as error:
        raise ArchiveV2Error("the exclusive V6 archive output parent is unsafe") from error


def compress_source(
    source: Path, expected: Mapping[str, Any], sink: Any
) -> dict[str, Any]:
    try:
        return inherited.compress_source(source, expected, sink)
    except (inherited.ArchiveError, OSError, TypeError, ValueError) as error:
        raise ArchiveV2Error("a measured V6 ELF changed during deterministic compression") from error


def exclusive_archive(
    destination: Path,
    source: Path,
    expected: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        destination.name in {label + ".elf.gz" for label in ROLES}
        and destination.parent.resolve() == ARCHIVE_ROOT.resolve(),
        "the V6 compressed ELF escaped its exact exclusive archive slot",
    )
    parent = open_exact_directory(destination.parent, ARCHIVE_ROOT)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    try:
        try:
            descriptor = os.open(destination.name, flags, 0o644, dir_fd=parent)
        except OSError as error:
            raise ArchiveV2Error("refusing an existing or substituted V6 native archive") from error
        try:
            with os.fdopen(descriptor, "wb", closefd=False) as output:
                result = compress_source(source, expected, inherited.DigestSink(output))
                output.flush()
                os.fsync(descriptor)
            os.fsync(parent)
        finally:
            os.close(descriptor)
    finally:
        os.close(parent)
    return result


def exclusive_json(path: Path, document: Mapping[str, Any]) -> None:
    require(
        path.name == ARCHIVE_MANIFEST.name
        and path.parent.resolve() == EVIDENCE.resolve(),
        "the V6 native archive manifest escaped its exclusive output slot",
    )
    payload = canonical(document) + b"\n"
    require(len(payload) <= MAX_JSON_BYTES, "the exclusive V6 archive manifest exceeds its bound")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    parent = open_exact_directory(path.parent, EVIDENCE)
    try:
        try:
            descriptor = os.open(path.name, flags, 0o644, dir_fd=parent)
        except OSError as error:
            raise ArchiveV2Error("refusing an existing or unsafe V6 native archive manifest") from error
        try:
            view = memoryview(payload)
            while view:
                count = os.write(descriptor, view)
                require(count > 0, "the exclusive V6 archive manifest write stalled")
                view = view[count:]
            os.fsync(descriptor)
            os.fsync(parent)
        finally:
            os.close(descriptor)
    finally:
        os.close(parent)


def make_archive_manifest(
    *,
    runtime: Mapping[str, Any],
    controller: Mapping[str, Any],
    state: Mapping[str, Any],
    records: Mapping[str, Any],
) -> dict[str, Any]:
    """Build JSON-normalized, source-bound provenance before publication."""

    manifest = {
        "schema": SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "public_protocol_version": PUBLIC_VERSION,
        "archive_source_path": SOURCE_RELATIVE,
        "archive_source_sha256": controller["sha256"],
        "inherited_archive_source_path": PREVIOUS_SOURCE_RELATIVE,
        "inherited_archive_source_sha256": PREVIOUS_SOURCE_SHA256,
        "proofs": {
            name: {"path": pair[0], "sha256": pair[1]}
            for name, pair in PROOFS.items()
        },
        "v6_qualified_source_fingerprints": state["sources"],
        "v6_native_elf_fingerprints": state["native"],
        "native_archive_count": len(ROLES),
        "gzip": {
            "compresslevel": 9,
            "filename": "",
            "mtime": 0,
            "header_hex": GZIP_HEADER.hex(),
        },
        "records": dict(records),
        "scope": {
            "archive_is_historical_bytes_only": True,
            "current_live_source_files_read": 0,
            "current_runtime_native_mapping_attested": False,
            "current_candidate_qualification_attested": False,
            "source_to_binary_reproducibility_attested": False,
            "automatic_native_restoration_permitted": False,
            "candidate_imported": False,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
            "restoration_requirements": (
                "A separate clean checkout of the original V6 source revision; "
                "all five owned mode-0700 ELF identities and sibling engines; "
                "independent SHA-256 verification before an isolated native load."
            ),
        },
        "pinned_interpreter": json.loads(canonical(runtime)),
    }
    verify_archive_provenance(
        manifest,
        source_sha256=controller["sha256"],
        runtime=runtime,
        state=state,
    )
    return manifest


def validate_resume_state(
    *,
    directory_present: Any,
    directory_symlink: Any,
    manifest_present: Any,
    manifest_symlink: Any,
    filenames: Any,
) -> tuple[str, ...]:
    """Accept only the exact interrupted five-role, unpublished V6 state."""

    expected = frozenset(label + ".elf.gz" for label in ROLES)
    require(
        directory_present is True
        and directory_symlink is False
        and manifest_present is False
        and manifest_symlink is False
        and isinstance(filenames, (tuple, list))
        and len(filenames) == len(expected)
        and all(isinstance(value, str) for value in filenames)
        and len(set(filenames)) == len(expected)
        and frozenset(filenames) == expected,
        "only the exact interrupted five-role V6 archive may be explicitly resumed",
    )
    return tuple(sorted(filenames))


def archive() -> dict[str, Any]:
    """Exclusively archive V6 binary bytes; never inspect current Rust source."""

    runtime = production_runtime()
    controller = fingerprint(SOURCE, MAX_SOURCE_BYTES)
    state = proof_state()
    require(
        not ARCHIVE_ROOT.is_symlink() and not ARCHIVE_ROOT.exists(),
        "refusing an existing, interrupted, or symlinked V6 native archive",
    )
    require(
        not ARCHIVE_MANIFEST.is_symlink() and not ARCHIVE_MANIFEST.exists(),
        "refusing an existing, interrupted, or symlinked V6 archive manifest",
    )
    prepared: dict[str, dict[str, Any]] = {}
    identities: dict[str, tuple[int, int, int, int, int, int]] = {}
    for label, (role, relative, digest, size) in ROLES.items():
        observed = fingerprint(ROOT / relative, MAX_ELF_BYTES)
        require(
            observed["prefix"][:5] == b"\x7fELF\x02"
            and observed["sha256"] == digest
            and observed["bytes"] == size
            and observed["mode"] == 0o700,
            "the exact measured public V6 ELF changed before preservation",
        )
        packed = compress_source(ROOT / relative, observed, inherited.DigestSink())
        identities[label] = observed["identity"]
        prepared[label] = {
            "role": role,
            "source_path": relative,
            "source_sha256": digest,
            "source_bytes": size,
            "source_mode": observed["mode"],
            "archive_path": ARCHIVE_ROOT_RELATIVE + "/" + label + ".elf.gz",
            **packed,
        }
    archive_records(prepared)
    refreshed_state = proof_state()
    require(refreshed_state == state, "immutable public V6 proofs changed before archive creation")
    refreshed_controller = fingerprint(SOURCE, MAX_SOURCE_BYTES)
    require(
        refreshed_controller["sha256"] == controller["sha256"]
        and refreshed_controller["identity"] == controller["identity"],
        "the V6 archive controller changed before exclusive creation",
    )
    evidence_parent = open_exact_directory(EVIDENCE, EVIDENCE)
    try:
        try:
            os.mkdir(ARCHIVE_ROOT.name, 0o755, dir_fd=evidence_parent)
        except OSError as error:
            raise ArchiveV2Error("refusing to recreate the one-use V6 archive directory") from error
        os.fsync(evidence_parent)
    finally:
        os.close(evidence_parent)
    for label, (_role, relative, _digest, _size) in ROLES.items():
        fresh_controller = fingerprint(SOURCE, MAX_SOURCE_BYTES)
        require(
            fresh_controller["sha256"] == controller["sha256"]
            and fresh_controller["identity"] == controller["identity"],
            "the V6 archive controller changed before an irreversible role write",
        )
        record = prepared[label]
        expected = {
            "identity": identities[label],
            "bytes": record["source_bytes"],
            "sha256": record["source_sha256"],
        }
        result = exclusive_archive(
            ARCHIVE_ROOT / (label + ".elf.gz"),
            ROOT / relative,
            expected,
        )
        require(
            result["compressed_sha256"] == record["compressed_sha256"]
            and result["compressed_bytes"] == record["compressed_bytes"],
            "a deterministic V6 compressed archive changed between passes",
        )
        for other, (_other_role, other_path, other_digest, other_size) in ROLES.items():
            current = fingerprint(ROOT / other_path, MAX_ELF_BYTES)
            require(
                current["sha256"] == other_digest
                and current["bytes"] == other_size
                and current["identity"] == identities[other],
                "a measured V6 native ELF changed before archive publication",
            )
    require(proof_state() == state, "an immutable V6 public proof changed during archival")
    fresh_controller = fingerprint(SOURCE, MAX_SOURCE_BYTES)
    require(
        fresh_controller["sha256"] == controller["sha256"]
        and fresh_controller["identity"] == controller["identity"],
        "the V6 archive controller changed before exclusive publication",
    )
    manifest = make_archive_manifest(
        runtime=runtime,
        controller=controller,
        state=state,
        records=prepared,
    )
    exclusive_json(ARCHIVE_MANIFEST, manifest)
    candidate_free()
    return manifest


def resume() -> dict[str, Any]:
    """Seal only five exact interrupted archives; never recreate or overwrite."""

    runtime = production_runtime()
    candidate_free()
    controller = fingerprint(SOURCE, MAX_SOURCE_BYTES)
    state = proof_state()
    require(
        ARCHIVE_ROOT.is_dir() and not ARCHIVE_ROOT.is_symlink(),
        "refusing to resume a missing or substituted V6 archive directory",
    )
    directory = open_exact_directory(ARCHIVE_ROOT, ARCHIVE_ROOT)
    try:
        try:
            names = os.listdir(directory)
        except OSError as error:
            raise ArchiveV2Error("cannot enumerate the exact interrupted V6 archive") from error
    finally:
        os.close(directory)
    validate_resume_state(
        directory_present=True,
        directory_symlink=ARCHIVE_ROOT.is_symlink(),
        manifest_present=ARCHIVE_MANIFEST.exists(),
        manifest_symlink=ARCHIVE_MANIFEST.is_symlink(),
        filenames=names,
    )
    records: dict[str, dict[str, Any]] = {}
    native_identities: dict[str, tuple[int, int, int, int, int, int]] = {}
    archive_identities: dict[str, tuple[int, int, int, int, int, int]] = {}
    for label, (role, relative, digest, size) in ROLES.items():
        observed = fingerprint(ROOT / relative, MAX_ELF_BYTES)
        require(
            observed["prefix"][:5] == b"\x7fELF\x02"
            and observed["sha256"] == digest
            and observed["bytes"] == size
            and observed["mode"] == 0o700,
            "refusing to resume without the exact historical V6 live native ELF",
        )
        canonical_gzip = compress_source(
            ROOT / relative,
            observed,
            inherited.DigestSink(),
        )
        packed = fingerprint(
            ARCHIVE_ROOT / (label + ".elf.gz"),
            MAX_ELF_BYTES,
            retain=True,
        )
        require(
            packed["prefix"][: len(GZIP_HEADER)] == GZIP_HEADER
            and packed["sha256"] == canonical_gzip["compressed_sha256"]
            and packed["bytes"] == canonical_gzip["compressed_bytes"],
            "an interrupted V6 native archive is not the exact deterministic ELF",
        )
        try:
            checked = inherited.verify_bounded_gzip(
                packed["payload"],
                expected_size=size,
                expected_sha256=digest,
            )
        except (inherited.ArchiveError, OSError, EOFError, TypeError, ValueError) as error:
            raise ArchiveV2Error("an interrupted V6 native archive is truncated or poisoned") from error
        require(
            checked.get("source_sha256") == digest
            and checked.get("source_bytes") == size,
            "the interrupted V6 gzip contains substituted historical ELF bytes",
        )
        native_identities[label] = observed["identity"]
        archive_identities[label] = packed["identity"]
        records[label] = {
            "role": role,
            "source_path": relative,
            "source_sha256": digest,
            "source_bytes": size,
            "source_mode": observed["mode"],
            "archive_path": ARCHIVE_ROOT_RELATIVE + "/" + label + ".elf.gz",
            "compressed_sha256": packed["sha256"],
            "compressed_bytes": packed["bytes"],
        }
    archive_records(records)
    for label, (_role, relative, digest, size) in ROLES.items():
        native = fingerprint(ROOT / relative, MAX_ELF_BYTES)
        packed = fingerprint(ARCHIVE_ROOT / (label + ".elf.gz"), MAX_ELF_BYTES)
        require(
            native["identity"] == native_identities[label]
            and native["sha256"] == digest
            and native["bytes"] == size
            and packed["identity"] == archive_identities[label]
            and packed["sha256"] == records[label]["compressed_sha256"]
            and packed["bytes"] == records[label]["compressed_bytes"],
            "an interrupted V6 native ELF or compressed role changed before sealing",
        )
    require(
        proof_state() == state,
        "a frozen public V6/V2 proof changed before interrupted archive publication",
    )
    refreshed = fingerprint(SOURCE, MAX_SOURCE_BYTES)
    require(
        refreshed["sha256"] == controller["sha256"]
        and refreshed["identity"] == controller["identity"],
        "the V6 archive controller changed before interrupted archive publication",
    )
    manifest = make_archive_manifest(
        runtime=runtime,
        controller=controller,
        state=state,
        records=records,
    )
    final_directory = open_exact_directory(ARCHIVE_ROOT, ARCHIVE_ROOT)
    try:
        try:
            final_names = os.listdir(final_directory)
        except OSError as error:
            raise ArchiveV2Error(
                "the interrupted V6 native archive changed before publication"
            ) from error
    finally:
        os.close(final_directory)
    validate_resume_state(
        directory_present=ARCHIVE_ROOT.is_dir(),
        directory_symlink=ARCHIVE_ROOT.is_symlink(),
        manifest_present=ARCHIVE_MANIFEST.exists(),
        manifest_symlink=ARCHIVE_MANIFEST.is_symlink(),
        filenames=final_names,
    )
    exclusive_json(ARCHIVE_MANIFEST, manifest)
    candidate_free()
    return manifest


def verify() -> dict[str, Any]:
    """Verify only frozen public proofs and archived bytes, never live ELFs."""

    runtime = production_runtime()
    state = proof_state()
    controller = fingerprint(SOURCE, MAX_SOURCE_BYTES)
    current = fingerprint(ARCHIVE_MANIFEST, MAX_JSON_BYTES, retain=True)
    try:
        document = json.loads(current["payload"])
    except (TypeError, ValueError, UnicodeError) as error:
        raise ArchiveV2Error("the V6 native archive manifest is invalid JSON") from error
    verify_archive_provenance(
        document,
        source_sha256=controller["sha256"],
        runtime=runtime,
        state=state,
    )
    for label, record in archive_records(document["records"]).items():
        packed = fingerprint(
            ARCHIVE_ROOT / (label + ".elf.gz"),
            MAX_ELF_BYTES,
            retain=True,
        )
        require(
            packed["sha256"] == record["compressed_sha256"]
            and packed["bytes"] == record["compressed_bytes"]
            and packed["prefix"][: len(GZIP_HEADER)] == GZIP_HEADER,
            "an immutable V6 compressed ELF was truncated or substituted",
        )
        try:
            inherited.verify_bounded_gzip(
                packed["payload"],
                expected_size=record["source_bytes"],
                expected_sha256=record["source_sha256"],
            )
        except (inherited.ArchiveError, OSError, EOFError, ValueError) as error:
            raise ArchiveV2Error("an archived V6 ELF changed or contains extra gzip members") from error
    candidate_free()
    return {
        "schema": SCHEMA + "-verification",
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "public_protocol_version": PUBLIC_VERSION,
        "archive_manifest_sha256": current["sha256"],
        "verified_archives": len(ROLES),
        "current_live_native_files_read": 0,
        "current_live_source_files_read": 0,
        "historical_bytes_only": True,
        "candidate_imported": False,
        "source_to_binary_reproducibility_attested": False,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
    }


def _synthetic_sha(label: str) -> str:
    return hashlib.sha256(("v6-native-archive-self-test:" + label).encode()).hexdigest()


def _synthetic_controls(count: int) -> dict[str, Any]:
    return {
        "passed": True,
        "check_count": count,
        "failed": [],
        "checks": [
            {"name": f"synthetic-public-native-control-{index}", "passed": True}
            for index in range(count)
        ],
    }


def _synthetic_proofs() -> tuple[dict[str, Any], ...]:
    native = {entry[0]: entry[2] for entry in ROLES.values()}
    sources = {
        path: (
            HISTORICAL_RUST_SOURCE_SHA256
            if path == HISTORICAL_RUST_SOURCE_PATH
            else _synthetic_sha(path)
        )
        for path in QUALIFIED_SOURCES
    }
    measured = {**native, "re:module": _synthetic_sha("reference")}
    common = {
        "protocol_version": PUBLIC_VERSION,
        "runner_sha256": PROOFS["runner-source"][1],
        "from_scratch_audit_sha256": PROOFS["base-audit"][1],
        "postfinal_no_delegation_audit_sha256": PROOFS["strict-audit"][1],
        "postfinal_no_delegation_control_count": 32,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "failed": 0,
    }
    plan = {
        **common,
        "postfinal_schema": "rebar-postfinal-public-practice-plan-v6",
        "native_elf_fingerprints": native,
        "qualified_source_fingerprints": sources,
    }
    summary = {
        **common,
        "postfinal_schema": "rebar-postfinal-public-practice-report-v6",
        "manifest_sha256": PROOFS["manifest"][1],
        "candidate_binary_sha256_before": measured,
        "candidate_binary_sha256_after": measured,
    }
    integrity = {
        **common,
        "schema": "rebar-postfinal-public-practice-integrity-v6",
        "result": "PASS",
        "manifest_sha256": PROOFS["manifest"][1],
        "summary_sha256": PROOFS["summary"][1],
        "verified_native_library_count": 5,
        "from_scratch_control_count": 76,
        "candidate_imported": False,
        "timing_performed": False,
        "native_elf_fingerprints": native,
        "qualified_source_fingerprints": sources,
        "candidate_binary_sha256_before": measured,
        "candidate_binary_sha256_after": measured,
    }
    base = {
        "schema_version": 1,
        "audit": "bounded-from-scratch-engine-provenance",
        "postfinal_schema": "rebar-postfinal-from-scratch-audit-v2",
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "audit_source_path": PROOFS["base-audit-source"][0],
        "audit_source_sha256": PROOFS["base-audit-source"][1],
        "self_test": _synthetic_controls(76),
    }
    strict = {
        "schema": "rebar-postfinal-no-delegation-audit-v2",
        "postfinal_schema": "rebar-postfinal-no-delegation-audit-v2",
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "base_audit_report_sha256": PROOFS["base-audit"][1],
        "base_audit_source_sha256": PROOFS["base-audit-source"][1],
        "audit_source_sha256": PROOFS["strict-audit-source"][1],
        "inherited_control_count": 76,
        "self_test": _synthetic_controls(32),
        "inherited_self_test": _synthetic_controls(76),
        "native_elf_fingerprints": native,
        "qualified_source_fingerprints": sources,
    }
    return plan, summary, integrity, base, strict


def _changed(document: dict[str, Any], path: tuple[str, ...], value: Any) -> dict[str, Any]:
    result = copy.deepcopy(document)
    selected: Any = result
    for part in path[:-1]:
        selected = selected[part]
    selected[path[-1]] = value
    return result


def self_test() -> dict[str, Any]:
    """Prove all V6 archive guards purely in memory, with every effect denied."""

    candidate_free()
    checks: list[dict[str, Any]] = []
    effects = inherited.BlockEffects()

    def check(name: str, value: Any) -> None:
        checks.append({"name": name, "passed": bool(value)})

    def reject(name: str, operation: Any) -> None:
        try:
            operation()
        except (
            ArchiveV2Error,
            inherited.ArchiveError,
            OSError,
            EOFError,
            TypeError,
            ValueError,
            UnicodeError,
        ):
            check(name, True)
        else:
            check(name, False)

    with effects:
        inherited_report = inherited.self_test()
        require(
            inherited_report.get("result") == "PASS"
            and inherited_report.get("passed") is True
            and isinstance(inherited_report.get("check_count"), int)
            and inherited_report["check_count"] >= 64
            and inherited_report.get("candidate_imported") is False
            and inherited_report.get("file_reads") == 0
            and inherited_report.get("file_writes") == 0
            and inherited_report.get("subprocesses") == 0
            and inherited_report.get("clock_samples") == 0
            and inherited_report.get("historical_holdout_accessed") is False
            and inherited_report.get("benchmark_or_timing_executed") is False,
            "an immutable V1 candidate-free deterministic archive control failed",
        )
        check("preserve-all-immutable-v1-candidate-free-archive-controls", True)
        check("preserve-five-exact-v6-native-role-identities", len(ROLES) == 5)
        check("preserve-twelve-frozen-historical-v6-sources", len(QUALIFIED_SOURCES) == 12)
        check("pin-original-651024-byte-v6-rust-engine", ROLES["rust-engine"][3] == 651_024)
        check("reject-stale-v5-rust-engine-identity", ROLES["rust-engine"][2] != inherited.ROLES["rust-engine"][2])
        check("preserve-distinct-v6-vm-native-output-label", "vm-native" in ROLES and "vm-engine" not in ROLES)
        check(
            "allow-only-exact-18592770-byte-v6-summary",
            validate_proof_size("summary", PINNED_PUBLIC_V6_SUMMARY_BYTES)
            == MAX_PUBLIC_V6_SUMMARY_BYTES,
        )
        for name, label, size in (
            ("reject-short-v6-public-summary", "summary", PINNED_PUBLIC_V6_SUMMARY_BYTES - 1),
            ("reject-long-v6-public-summary", "summary", PINNED_PUBLIC_V6_SUMMARY_BYTES + 1),
            ("reject-v6-summary-over-twenty-mib", "summary", MAX_PUBLIC_V6_SUMMARY_BYTES + 1),
            ("reject-v6-integrity-over-sixteen-mib", "integrity", MAX_JSON_BYTES + 1),
            ("reject-v6-proof-zero-bytes", "manifest", 0),
            ("reject-v6-proof-boolean-size", "manifest", True),
            ("reject-private-proof-selection", "holdout", 1),
        ):
            reject(name, lambda item=label, value=size: validate_proof_size(item, value))
        plan, summary, integrity, base, strict = _synthetic_proofs()
        state = validate_frozen_proofs(plan, summary, integrity, base, strict)
        check("accept-exact-source-bound-synthetic-v6-evidence", True)
        expected_native = {record[0]: record[2] for record in ROLES.values()}
        check("bind-exact-five-v6-native-digests", state["native"] == expected_native)
        check(
            "bind-historical-rust-source-without-reading-live-source",
            state["sources"][HISTORICAL_RUST_SOURCE_PATH]
            == HISTORICAL_RUST_SOURCE_SHA256,
        )
        poisoned: tuple[tuple[str, int, tuple[str, ...], Any], ...] = (
            ("reject-stale-v5-public-manifest", 0, ("protocol_version",), "postfinal-public-practice-v5"),
            ("reject-stale-v5-manifest-schema", 0, ("postfinal_schema",), "rebar-postfinal-public-practice-plan-v5"),
            ("reject-substituted-v6-runner-source", 0, ("runner_sha256",), "0" * 64),
            ("reject-hidden-holdout-in-v6-manifest", 0, ("holdout_accessed",), True),
            ("reject-hidden-case-generation", 0, ("held_out_cases_generated",), 1),
            ("reject-failing-v6-manifest", 0, ("failed",), 1),
            ("reject-stale-v5-public-summary", 1, ("protocol_version",), "postfinal-public-practice-v5"),
            ("reject-substituted-summary-manifest-pin", 1, ("manifest_sha256",), "0" * 64),
            ("reject-hidden-v6-summary-holdout", 1, ("holdout_accessed",), True),
            ("reject-failing-v6-summary", 1, ("failed",), 1),
            ("reject-unverified-v6-independent-replay", 2, ("result",), "FAIL"),
            ("reject-substituted-v6-summary-digest", 2, ("summary_sha256",), "0" * 64),
            ("reject-substituted-v6-replay-manifest-digest", 2, ("manifest_sha256",), "0" * 64),
            ("reject-missing-v6-native-replay-elf", 2, ("verified_native_library_count",), 4),
            ("reject-weakened-original-76-controls", 2, ("from_scratch_control_count",), 75),
            ("reject-weakened-strict-32-controls", 2, ("postfinal_no_delegation_control_count",), 31),
            ("reject-v6-replay-candidate-import", 2, ("candidate_imported",), True),
            ("reject-v6-replay-timing", 2, ("timing_performed",), True),
            ("reject-v6-replay-holdout", 2, ("holdout_accessed",), True),
            ("reject-stale-v1-base-audit-schema", 3, ("postfinal_schema",), "rebar-postfinal-from-scratch-audit-v1"),
            ("reject-substituted-v2-base-source", 3, ("audit_source_sha256",), "0" * 64),
            ("reject-substituted-v2-strict-source", 4, ("audit_source_sha256",), "0" * 64),
            ("reject-v2-strict-cross-base-report", 4, ("base_audit_report_sha256",), "0" * 64),
            ("reject-weakened-v2-original-control-count", 4, ("inherited_control_count",), 75),
            ("reject-historical-rust-source-fingerprint-swap", 0, ("qualified_source_fingerprints", HISTORICAL_RUST_SOURCE_PATH), "0" * 64),
        )
        documents = (plan, summary, integrity, base, strict)
        for name, index, path, value in poisoned:
            modified = list(documents)
            modified[index] = _changed(documents[index], path, value)
            reject(
                name,
                lambda current=tuple(modified): validate_frozen_proofs(*current),
            )
        for label in ROLES:
            key = ROLES[label][0]
            for name, index, field in (
                ("reject-swapped-v6-plan-native-role", 0, "native_elf_fingerprints"),
                ("reject-swapped-v6-replay-native-role", 2, "native_elf_fingerprints"),
                ("reject-swapped-v6-measured-before-role", 1, "candidate_binary_sha256_before"),
                ("reject-swapped-v6-measured-after-role", 1, "candidate_binary_sha256_after"),
                ("reject-swapped-v6-replayed-before-role", 2, "candidate_binary_sha256_before"),
                ("reject-swapped-v6-replayed-after-role", 2, "candidate_binary_sha256_after"),
                ("reject-swapped-v2-strict-native-role", 4, "native_elf_fingerprints"),
            ):
                modified = list(documents)
                modified[index] = _changed(documents[index], (field, key), "0" * 64)
                reject(
                    name + ":" + label,
                    lambda current=tuple(modified): validate_frozen_proofs(*current),
                )
        fake: dict[str, dict[str, Any]] = {}
        for label, (role, source, digest, size) in ROLES.items():
            fake[label] = {
                "role": role,
                "source_path": source,
                "source_sha256": digest,
                "source_bytes": size,
                "source_mode": 0o700,
                "archive_path": ARCHIVE_ROOT_RELATIVE + "/" + label + ".elf.gz",
                "compressed_sha256": _synthetic_sha(label + ":compressed"),
                "compressed_bytes": 64,
            }
        check("accept-all-five-exact-exclusive-v6-archive-slots", archive_records(fake) == fake)
        exact_names = tuple(label + ".elf.gz" for label in ROLES)
        valid_interruption = {
            "directory_present": True,
            "directory_symlink": False,
            "manifest_present": False,
            "manifest_symlink": False,
            "filenames": exact_names,
        }
        check(
            "accept-only-exact-five-role-unpublished-interruption",
            validate_resume_state(**valid_interruption) == tuple(sorted(exact_names)),
        )
        for name, field, value in (
            ("reject-resume-missing-archive-directory", "directory_present", False),
            ("reject-resume-symlinked-archive-directory", "directory_symlink", True),
            ("reject-resume-existing-archive-manifest", "manifest_present", True),
            ("reject-resume-symlinked-archive-manifest", "manifest_symlink", True),
            ("reject-resume-omitted-native-role", "filenames", exact_names[:-1]),
            ("reject-resume-extra-native-role", "filenames", (*exact_names, "foreign.elf.gz")),
            ("reject-resume-duplicate-native-role", "filenames", (*exact_names[:-1], exact_names[0])),
            ("reject-resume-stale-v5-native-role", "filenames", ("vm-engine.elf.gz", *exact_names[1:])),
            ("reject-resume-nonlist-native-roles", "filenames", frozenset(exact_names)),
        ):
            reject(
                name,
                lambda key=field, item=value: validate_resume_state(
                    **{**valid_interruption, key: item}
                ),
            )
        for name, label, field, value in (
            ("reject-historical-v5-rust-engine", "rust-engine", "source_sha256", inherited.ROLES["rust-engine"][2]),
            ("reject-historical-v5-rust-size", "rust-engine", "source_bytes", inherited.ROLES["rust-engine"][3]),
            ("reject-swapped-v6-native-source-path", "vm-native", "source_path", ROLES["rust-engine"][1]),
            ("reject-unsafe-v6-native-source-mode", "rust-bridge", "source_mode", 0o755),
            ("reject-invalid-v6-compressed-digest", "zig-engine", "compressed_sha256", "foreign"),
            ("reject-empty-v6-compressed-elf", "zig-bridge", "compressed_bytes", 0),
            ("reject-v6-native-archive-path-traversal", "vm-native", "archive_path", "../foreign.elf.gz"),
            ("reject-v6-native-archive-v5-parent", "rust-engine", "archive_path", "performance/postfinal-public-v5/evidence/native-archive-v1/rust-engine.elf.gz"),
        ):
            reject(
                name,
                lambda role=label, key=field, item=value: archive_records(
                    {**fake, role: {**fake[role], key: item}}
                ),
            )
        reject("reject-omitted-v6-native-archive-role", lambda: archive_records(dict(list(fake.items())[:-1])))
        reject("reject-extra-v6-native-archive-role", lambda: archive_records({**fake, "foreign": fake["vm-native"]}))
        runtime = {
            "implementation": "cpython",
            "version": PINNED_VERSION,
            "executable": PINNED_PYTHON,
            "isolated": 1,
            "dont_write_bytecode": True,
        }
        check("accept-pinned-isolated-cpython-3146", inherited.pinned_runtime(runtime) == runtime)
        for name, key, value in (
            ("reject-foreign-production-python", "implementation", "pypy"),
            ("reject-foreign-production-python-version", "version", (3, 14, 5)),
            ("reject-foreign-production-interpreter-path", "executable", "/usr/bin/python3"),
            ("reject-unisolated-production-python", "isolated", 0),
            ("reject-production-bytecode-writes", "dont_write_bytecode", False),
        ):
            reject(
                name,
                lambda field=key, item=value: inherited.pinned_runtime({**runtime, field: item}),
            )
        synthetic_source = _synthetic_sha("current-v6-controller")
        document = {
            "schema": SCHEMA,
            "status": "PASS",
            "result": "PASS",
            "passed": True,
            "public_protocol_version": PUBLIC_VERSION,
            "archive_source_path": SOURCE_RELATIVE,
            "archive_source_sha256": synthetic_source,
            "inherited_archive_source_path": PREVIOUS_SOURCE_RELATIVE,
            "inherited_archive_source_sha256": PREVIOUS_SOURCE_SHA256,
            "pinned_interpreter": json.loads(canonical(runtime)),
            "proofs": {
                name: {"path": item[0], "sha256": item[1]}
                for name, item in PROOFS.items()
            },
            "v6_native_elf_fingerprints": state["native"],
            "v6_qualified_source_fingerprints": state["sources"],
            "native_archive_count": 5,
            "gzip": {
                "compresslevel": 9,
                "filename": "",
                "mtime": 0,
                "header_hex": GZIP_HEADER.hex(),
            },
            "records": fake,
            "scope": {
                "archive_is_historical_bytes_only": True,
                "current_live_source_files_read": 0,
                "current_runtime_native_mapping_attested": False,
                "current_candidate_qualification_attested": False,
                "source_to_binary_reproducibility_attested": False,
                "automatic_native_restoration_permitted": False,
                "candidate_imported": False,
                "benchmark_or_timing_executed": False,
                "holdout_or_case_fixture_access": False,
            },
        }
        check(
            "accept-exact-v6-native-archive-source-provenance",
            verify_archive_provenance(
                document,
                source_sha256=synthetic_source,
                runtime=runtime,
                state=state,
            )
            is None,
        )
        generated = make_archive_manifest(
            runtime=runtime,
            controller={"sha256": synthetic_source},
            state=state,
            records=fake,
        )
        check(
            "normalize-pinned-runtime-before-manifest-publication",
            generated["pinned_interpreter"] == json.loads(canonical(runtime))
            and isinstance(generated["pinned_interpreter"]["version"], list),
        )
        reject(
            "reject-unnormalized-prepublication-runtime-tuple",
            lambda: verify_archive_provenance(
                {**generated, "pinned_interpreter": runtime},
                source_sha256=synthetic_source,
                runtime=runtime,
                state=state,
            ),
        )
        for name, path, value in (
            ("reject-stale-v5-archive-schema", ("schema",), inherited.SCHEMA),
            ("reject-stale-v5-archive-protocol", ("public_protocol_version",), "postfinal-public-practice-v5"),
            ("reject-substituted-v6-archive-source", ("archive_source_path",), PREVIOUS_SOURCE_RELATIVE),
            ("reject-substituted-v6-archive-source-hash", ("archive_source_sha256",), "0" * 64),
            ("reject-substituted-immutable-v1-controller", ("inherited_archive_source_sha256",), "0" * 64),
            ("reject-claimed-live-source-fingerprinting", ("scope", "current_live_source_files_read"), 1),
            ("reject-falsely-claimed-runtime-native-mapping", ("scope", "current_runtime_native_mapping_attested"), True),
            ("reject-falsely-claimed-native-qualification", ("scope", "current_candidate_qualification_attested"), True),
            ("reject-falsely-claimed-reproducible-build", ("scope", "source_to_binary_reproducibility_attested"), True),
            ("reject-automatic-native-restoration", ("scope", "automatic_native_restoration_permitted"), True),
            ("reject-candidate-import-during-archival", ("scope", "candidate_imported"), True),
            ("reject-holdout-access-during-archival", ("scope", "holdout_or_case_fixture_access"), True),
            ("reject-timing-during-archival", ("scope", "benchmark_or_timing_executed"), True),
        ):
            reject(
                name,
                lambda key_path=path, item=value: verify_archive_provenance(
                    _changed(document, key_path, item),
                    source_sha256=synthetic_source,
                    runtime=runtime,
                    state=state,
                ),
            )
        for item in (float("nan"), float("inf"), -float("inf")):
            reject("reject-nonfinite-v6-archive-provenance:" + repr(item), lambda value=item: canonical({"value": value}))
        candidate_free()
        check("candidate-free-after-all-v6-archive-controls", True)
    check("zero-v6-synthetic-public-evidence-reads", effects.counts["files"] == 0)
    check("zero-v6-synthetic-public-evidence-writes", effects.counts["files"] == 0)
    check("zero-v6-synthetic-candidate-worker-starts", effects.counts["processes"] == 0)
    check("zero-v6-synthetic-production-clock-samples", effects.counts["clocks"] == 0)
    check("zero-v6-synthetic-production-entropy", effects.counts["entropy"] == 0)
    names = [record["name"] for record in checks]
    failed = sorted(record["name"] for record in checks if not record["passed"])
    if len(names) != len(set(names)):
        failed.append("duplicate-v6-native-archive-control")
    candidate_free()
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS" if not failed else "FAIL",
        "result": "PASS" if not failed else "FAIL",
        "passed": not failed,
        "checks": checks,
        "check_count": len(checks),
        "failed": failed,
        "inherited_self_test": inherited_report,
        "inherited_control_count": inherited_report["check_count"],
        "fixture_storage": "in-memory only",
        "candidate_imported": False,
        "file_reads": effects.counts["files"],
        "file_writes": 0,
        "subprocesses": effects.counts["processes"],
        "clock_samples": effects.counts["clocks"],
        "production_entropy_drawn": False,
        "archive_created": False,
        "production_cases_materialized": 0,
        "current_live_source_files_read": 0,
        "current_live_native_files_read": 0,
        "historical_holdout_accessed": False,
        "holdout_or_case_fixture_access": False,
        "benchmark_or_timing_executed": False,
    }


def main(arguments: list[str] | None = None) -> int:
    selected = list(sys.argv[1:] if arguments is None else arguments)
    try:
        if selected == ["--self-test"]:
            result = self_test()
        elif selected in (["--archive"], ["--resume"]):
            was_resumed = selected == ["--resume"]
            manifest = resume() if was_resumed else archive()
            result = {
                "schema": SCHEMA,
                "status": "PASS",
                "result": "PASS",
                "passed": True,
                "public_protocol_version": PUBLIC_VERSION,
                "manifest": ARCHIVE_MANIFEST_RELATIVE,
                "archive_source_path": SOURCE_RELATIVE,
                "archive_source_sha256": manifest["archive_source_sha256"],
                "resumed": was_resumed,
                "archives": 5,
                "native_source_bytes": sum(item[3] for item in ROLES.values()),
                "historical_bytes_only": True,
                "current_live_source_files_read": 0,
                "source_to_binary_reproducibility_attested": False,
                "current_runtime_native_mapping_attested": False,
                "candidate_imported": False,
                "benchmark_or_timing_executed": False,
                "holdout_or_case_fixture_access": False,
            }
        elif selected == ["--verify"]:
            result = verify()
        else:
            raise ArchiveV2Error(
                "select exactly --self-test, --archive, --resume, or --verify"
            )
        sys.stdout.buffer.write(canonical(result) + b"\n")
        return 0 if result.get("passed") is True else 1
    except (
        ArchiveV2Error,
        inherited.ArchiveError,
        OSError,
        TypeError,
        ValueError,
        UnicodeError,
        EOFError,
        subprocess.SubprocessError,
    ) as error:
        sys.stdout.buffer.write(
            canonical(
                {
                    "schema": SCHEMA,
                    "status": "FAIL",
                    "result": "FAIL",
                    "passed": False,
                    "error": str(error),
                    "candidate_imported": False,
                    "benchmark_or_timing_executed": False,
                    "holdout_or_case_fixture_access": False,
                }
            )
            + b"\n"
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
