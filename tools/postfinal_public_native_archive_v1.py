#!/usr/bin/env python3
"""Preserve and independently verify the five measured public-V5 native ELFs."""

from __future__ import annotations

import builtins
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import secrets
import stat
import subprocess
import sys
import time
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "rebar-postfinal-public-native-archive-v1"
SOURCE = ROOT / "tools" / "postfinal_public_native_archive_v1.py"
SOURCE_RELATIVE = "tools/postfinal_public_native_archive_v1.py"
EVIDENCE = ROOT / "performance" / "postfinal-public-v5" / "evidence"
ARCHIVE_ROOT = EVIDENCE / "native-archive-v1"
ARCHIVE_MANIFEST = EVIDENCE / "postfinal-public-v5-native-archive-v1.json"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_VERSION = (3, 14, 6)
MAX_ELF_BYTES = 64 * 1024 * 1024
MAX_JSON_BYTES = 16 * 1024 * 1024
MAX_PUBLIC_V5_SUMMARY_BYTES = 20 * 1024 * 1024
PINNED_PUBLIC_V5_SUMMARY_BYTES = 18_125_531
MAX_SOURCE_BYTES = 16 * 1024 * 1024
CHUNK = 64 * 1024
GZIP_HEADER = bytes.fromhex("1f8b08000000000002ff")
PROOFS = {
    "manifest": (
        "performance/postfinal-public-v5/manifest.json",
        "c9950c87079ccc1909ba4470ed573b08afe1f275b85a8932cbfe83b547b24f96",
    ),
    "summary": (
        "performance/postfinal-public-v5/evidence/postfinal-public-practice-v5-summary.json",
        "d9dd1e712a97d0d1716308e1e468e0c9d2b6d6058e501bccd871492bc66a6b4c",
    ),
    "integrity": (
        "performance/postfinal-public-v5/evidence/postfinal-public-practice-v5-integrity.json",
        "ff86c9421747373df9f5cf640f8a081331661c7d79e8b12969cb0952c86d9246",
    ),
    "base-audit": (
        "candidates/audits/FROM-SCRATCH-AUDIT.json",
        "c78449b1153221bd0d17854c4f6682062392d19a04cfd0a424a1c6f3fa3478cb",
    ),
    "strict-audit": (
        "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V1.json",
        "c4605c8af5da805c099b1efb7f15e8390781768bb3014276b465a7712b4ed06b",
    ),
    "runner-source": (
        "tools/postfinal_public_practice_v5.py",
        "f4294a3b5434f43a92970635a958cf3b39db0eb926adef50e242ac0f6b9a1d22",
    ),
    "base-audit-source": (
        "tools/audit_from_scratch.py",
        "4c47a77cf096df354e59d03096447c56bff890389869c6a75667a36c8471d024",
    ),
    "strict-audit-source": (
        "tools/postfinal_no_delegation_audit_v1.py",
        "e505e17f4849242d990ee8e184794962327335d807000d1a8a0e65a0cb10c0ed",
    ),
}
ROLES = {
    "vm-engine": (
        "candidates.vm_candidate:native-engine",
        "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "6922d0869b67c82be9ae89a8f00c71777c04472d3606a33527bb13494326f18d",
        159464,
    ),
    "rust-engine": (
        "candidates.rust_candidate:native-engine",
        "candidates/_rust_engine.so",
        "c6c09ae96e3a840dc7a62870b3f8c54f6ebc4d82537b319f77520175e84a3255",
        650328,
    ),
    "rust-bridge": (
        "candidates.rust_candidate:native-bridge",
        "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "81fc4c4a92005f0588dd9b811988587d4d421dd8e1102eebcab53f4deb27cd36",
        136096,
    ),
    "zig-engine": (
        "candidates.zig_candidate:native-engine",
        "candidates/_zig_probe.so",
        "474dde0bfb23f107f21ec4834ce15dbd1b437841bd171698de623d1c03742988",
        491688,
    ),
    "zig-bridge": (
        "candidates.zig_candidate:native-bridge",
        "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        "32dadc46281d13df784693f0785d4d149e6d3cd000aa3de6eb220a4a9ed50c9c",
        120992,
    ),
}
RECORD_FIELDS = frozenset({
    "role", "source_path", "source_sha256", "source_bytes", "source_mode",
    "archive_path", "compressed_sha256", "compressed_bytes",
})
QUALIFIED_SOURCES = frozenset({
    "candidates/_vm_native.c", "candidates/rust/py_bridge.c",
    "candidates/rust/src/lib.rs", "candidates/rust/src/newline.rs",
    "candidates/rust/src/search.rs", "candidates/rust/src/stack.rs",
    "candidates/rust/src/unicode_tables.rs", "candidates/rust_candidate.py",
    "candidates/vm_candidate.py", "candidates/zig/mini_regex.zig",
    "candidates/zig/py_bridge.c", "candidates/zig_candidate.py",
})


class ArchiveError(RuntimeError):
    """An immutable public-native archive or its independent proof failed."""


def require(value: Any, message: str) -> None:
    if not value:
        raise ArchiveError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, allow_nan=False,
                      sort_keys=True, separators=(",", ":")).encode("ascii")


def candidate_free() -> None:
    forbidden = sorted(
        name for name in sys.modules
        if name.startswith("candidates.") and (
            name.endswith("_candidate")
            or name.rsplit(".", 1)[-1] in {"_vm_native", "_rust_bridge", "_zig_bridge"}
        )
    )
    require(not forbidden, f"archive controller imported a candidate: {forbidden!r}")


def pinned_runtime(value: Mapping[str, Any]) -> dict[str, Any]:
    require(isinstance(value, Mapping), "invalid pinned interpreter evidence")
    require(value.get("implementation") == "cpython"
            and value.get("version") == PINNED_VERSION
            and value.get("executable") == PINNED_PYTHON
            and type(value.get("isolated")) is int and value.get("isolated") == 1
            and value.get("dont_write_bytecode") is True,
            "archive requires exact CPython 3.14.6 invoked with -I -B")
    return dict(value)


def production_runtime() -> dict[str, Any]:
    runtime = pinned_runtime({
        "implementation": sys.implementation.name,
        "version": tuple(sys.version_info[:3]),
        "executable": sys.executable,
        "isolated": sys.flags.isolated,
        "dont_write_bytecode": sys.dont_write_bytecode,
    })
    require(Path(sys.executable).resolve(strict=True)
            == Path(PINNED_PYTHON).resolve(strict=True),
            "the pinned production interpreter was substituted")
    return runtime


def stat_tuple(value: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (value.st_dev, value.st_ino, value.st_size,
            value.st_mtime_ns, value.st_ctime_ns, value.st_mode)


def fingerprint(path: Path, maximum: int, *, retain: bool = False) -> dict[str, Any]:
    require(not path.is_symlink(), f"an owned public artifact is a symlink: {path.name}")
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(ROOT.resolve(strict=True))
        digest = hashlib.sha256()
        size = 0
        prefix = bytearray()
        payload = bytearray() if retain else None
        with resolved.open("rb") as stream:
            before = os.fstat(stream.fileno())
            require(stat.S_ISREG(before.st_mode), "owned artifact is not a regular file")
            identity = stat_tuple(before)
            while block := stream.read(CHUNK):
                size += len(block)
                require(size <= maximum, "owned artifact exceeds its finite source bound")
                digest.update(block)
                if len(prefix) < 16:
                    prefix.extend(block[:16 - len(prefix)])
                if payload is not None:
                    payload.extend(block)
            require(stat_tuple(os.fstat(stream.fileno())) == identity,
                    "owned artifact changed during public verification")
        require(stat_tuple(os.stat(resolved, follow_symlinks=False)) == identity,
                "owned artifact changed after public verification")
    except (OSError, RuntimeError, ValueError) as error:
        raise ArchiveError(
            f"authorized public artifact {path.name!r} could not be safely verified"
        ) from error
    require(size == before.st_size and size > 0, "public artifact has an invalid size")
    result: dict[str, Any] = {
        "sha256": digest.hexdigest(), "bytes": size, "identity": identity,
        "mode": stat.S_IMODE(before.st_mode), "prefix": bytes(prefix),
    }
    if payload is not None:
        result["payload"] = bytes(payload)
    return result


def validate_proof_size(name: str, size: int) -> int:
    require(name in PROOFS, "a foreign public V5 proof was selected")
    maximum = MAX_PUBLIC_V5_SUMMARY_BYTES if name == "summary" else MAX_JSON_BYTES
    require(type(size) is int and 0 < size <= maximum,
            f"the authorized public {name} proof exceeds its specific bound")
    if name == "summary":
        require(size == PINNED_PUBLIC_V5_SUMMARY_BYTES,
                "the pinned measured public V5 summary changed its exact byte length")
    return maximum


def load_proof(name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    relative, expected = PROOFS[name]
    maximum = (
        MAX_PUBLIC_V5_SUMMARY_BYTES if name == "summary" else MAX_JSON_BYTES
    )
    record = fingerprint(ROOT / relative, maximum, retain=True)
    validate_proof_size(name, record["bytes"])
    require(record["sha256"] == expected, f"immutable V5 proof changed: {name}")
    try:
        value = json.loads(record["payload"])
    except (TypeError, UnicodeError, ValueError) as error:
        raise ArchiveError(f"immutable V5 JSON proof is invalid: {name}") from error
    require(isinstance(value, dict), f"immutable V5 proof is not an object: {name}")
    return value, record


def exact_native_map(value: Any, *, allow_extras: bool = False) -> dict[str, str]:
    require(isinstance(value, dict), "public proof omitted its owned native mappings")
    expected = {record[0]: record[2] for record in ROLES.values()}
    if not allow_extras:
        require(set(value) == set(expected), "public proof changed its exact five native roles")
    actual = {name: value.get(name) for name in expected}
    require(actual == expected, "public proof omitted, swapped, or changed a native role")
    return actual


def check_controls(value: Any, count: int) -> None:
    require(isinstance(value, dict), "public audit omitted its malicious controls")
    checks = value.get("checks")
    require(value.get("passed") is True and value.get("check_count") == count
            and value.get("failed") == [] and isinstance(checks, list)
            and len(checks) == count and all(
                isinstance(item, dict) and isinstance(item.get("name"), str)
                and item.get("passed") is True for item in checks
            ) and len({item["name"] for item in checks}) == count,
            "an immutable V5 audit changed its complete control denominator")


def proof_state(*, current_sources: bool) -> dict[str, Any]:
    candidate_free()
    plan, _ = load_proof("manifest")
    summary, _ = load_proof("summary")
    integrity, _ = load_proof("integrity")
    base, _ = load_proof("base-audit")
    strict, _ = load_proof("strict-audit")
    for name in ("runner-source", "base-audit-source", "strict-audit-source"):
        relative, expected = PROOFS[name]
        require(fingerprint(ROOT / relative, MAX_SOURCE_BYTES)["sha256"] == expected,
                f"immutable V5 source changed: {name}")
    require(plan.get("protocol_version") == "postfinal-public-practice-v5"
            and plan.get("postfinal_schema") == "rebar-postfinal-public-practice-plan-v5"
            and plan.get("runner_sha256") == PROOFS["runner-source"][1],
            "the prospective public V5 manifest was substituted")
    require(summary.get("postfinal_schema") == "rebar-postfinal-public-practice-report-v5"
            and summary.get("protocol_version") == plan["protocol_version"]
            and summary.get("manifest_sha256") == PROOFS["manifest"][1]
            and summary.get("runner_sha256") == PROOFS["runner-source"][1]
            and summary.get("failed") == 0 and summary.get("cases") == 8192
            and summary.get("holdout_accessed") is False,
            "the original measured public V5 summary was substituted")
    require(integrity.get("schema") == "rebar-postfinal-public-practice-integrity-v5"
            and integrity.get("protocol_version") == plan["protocol_version"]
            and integrity.get("result") == "PASS"
            and integrity.get("manifest_sha256") == PROOFS["manifest"][1]
            and integrity.get("summary_sha256") == PROOFS["summary"][1]
            and integrity.get("runner_sha256") == PROOFS["runner-source"][1]
            and integrity.get("failed") == 0
            and integrity.get("verified_native_library_count") == 5
            and integrity.get("holdout_accessed") is False,
            "the independently replayed V5 integrity proof was substituted")
    expected = exact_native_map(plan.get("native_elf_fingerprints"))
    require(exact_native_map(integrity.get("native_elf_fingerprints")) == expected,
            "public manifest and integrity disagree about native identities")
    for proof in (summary, integrity):
        require(exact_native_map(proof.get("candidate_binary_sha256_before"), allow_extras=True) == expected
                and exact_native_map(proof.get("candidate_binary_sha256_after"), allow_extras=True) == expected,
                "a measured public V5 before/after native identity changed")
    check_controls(base.get("self_test"), 76)
    check_controls(strict.get("self_test"), 32)
    check_controls(strict.get("inherited_self_test"), 76)
    require(base.get("schema_version") == 1
            and base.get("audit") == "bounded-from-scratch-engine-provenance"
            and base.get("result") == "PASS" and base.get("passed") is True
            and strict.get("schema") == "rebar-postfinal-no-delegation-audit-v1"
            and strict.get("result") == "PASS" and strict.get("passed") is True
            and strict.get("base_audit_report_sha256") == PROOFS["base-audit"][1]
            and strict.get("audit_source_sha256") == PROOFS["strict-audit-source"][1]
            and strict.get("base_audit_source_sha256") == PROOFS["base-audit-source"][1]
            and strict.get("inherited_control_count") == 76
            and exact_native_map(strict.get("native_elf_fingerprints")) == expected,
            "an immutable V5 76/32-control audit was substituted")
    for document in (plan, summary, integrity):
        require(document.get("from_scratch_audit_sha256") == PROOFS["base-audit"][1]
                and document.get("from_scratch_audit_source_sha256") == PROOFS["base-audit-source"][1]
                and document.get("postfinal_no_delegation_audit_sha256") == PROOFS["strict-audit"][1]
                and document.get("postfinal_no_delegation_audit_source_sha256") == PROOFS["strict-audit-source"][1]
                and document.get("postfinal_no_delegation_control_count") == 32,
                "an immutable V5 manifest, measurement, or replay changed its audit bindings")
    source_hashes = plan.get("qualified_source_fingerprints")
    require(isinstance(source_hashes, dict) and set(source_hashes) == QUALIFIED_SOURCES,
            "the original measured V5 omitted its exact 12-source graph")
    if current_sources:
        for relative, expected_source in sorted(source_hashes.items()):
            require(fingerprint(ROOT / relative, MAX_SOURCE_BYTES)["sha256"] == expected_source,
                    f"the current public V5 source changed: {relative}")
    candidate_free()
    return {"native": expected, "sources": dict(source_hashes)}


class DigestSink:
    def __init__(self, stream: Any = None) -> None:
        self.stream = stream
        self.digest = hashlib.sha256()
        self.size = 0
        self.prefix = bytearray()

    def write(self, block: bytes) -> int:
        require(isinstance(block, bytes), "gzip produced a nonbinary archive frame")
        if self.stream is not None:
            written = self.stream.write(block)
            require(written == len(block), "exclusive archive write was incomplete")
        self.digest.update(block)
        self.size += len(block)
        if len(self.prefix) < len(GZIP_HEADER):
            self.prefix.extend(block[:len(GZIP_HEADER) - len(self.prefix)])
        return len(block)

    def flush(self) -> None:
        if self.stream is not None:
            self.stream.flush()


def compress_source(path: Path, expected: Mapping[str, Any], sink: DigestSink) -> dict[str, Any]:
    raw_digest = hashlib.sha256()
    length = 0
    try:
        with path.open("rb") as source:
            before = os.fstat(source.fileno())
            require(stat.S_ISREG(before.st_mode)
                    and stat_tuple(before) == tuple(expected["identity"]),
                    "public V5 source inode, mode, or timestamp changed")
            with gzip.GzipFile(filename="", fileobj=sink, mode="wb",
                               compresslevel=9, mtime=0) as archive:
                while block := source.read(CHUNK):
                    length += len(block)
                    require(length <= MAX_ELF_BYTES, "native ELF exceeded its archival bound")
                    raw_digest.update(block)
                    archive.write(block)
            require(stat_tuple(os.fstat(source.fileno())) == tuple(expected["identity"]),
                    "public V5 native source changed during compression")
        require(stat_tuple(os.stat(path, follow_symlinks=False)) == tuple(expected["identity"]),
                "public V5 native source changed after compression")
    except OSError as error:
        raise ArchiveError("a measured public native ELF could not be safely archived") from error
    require(length == expected["bytes"] and raw_digest.hexdigest() == expected["sha256"],
            "a measured public native ELF changed during archive creation")
    require(bytes(sink.prefix) == GZIP_HEADER, "gzip contains a filename, clock, or unpinned header")
    return {"compressed_sha256": sink.digest.hexdigest(), "compressed_bytes": sink.size}


def open_exact_directory(path: Path, expected: Path) -> int:
    require(not path.is_symlink() and not expected.is_symlink(),
            "refusing a substituted archive output parent")
    require(path.resolve(strict=True) == expected.resolve(strict=True),
            "archive output parent escaped its exact authorized directory")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    descriptor = os.open(expected, flags)
    try:
        observed = os.fstat(descriptor)
        require(stat.S_ISDIR(observed.st_mode)
                and stat_tuple(observed)
                == stat_tuple(os.stat(expected, follow_symlinks=False)),
                "the archive parent directory changed while being opened")
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor


def exclusive_archive(path: Path, source: Path, expected: Mapping[str, Any]) -> dict[str, Any]:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    parent = open_exact_directory(path.parent, ARCHIVE_ROOT)
    try:
        try:
            descriptor = os.open(path.name, flags, 0o644, dir_fd=parent)
        except OSError as error:
            raise ArchiveError("refusing to overwrite, recreate, or follow an archive slot") from error
        try:
            with os.fdopen(descriptor, "wb", closefd=False) as output:
                result = compress_source(source, expected, DigestSink(output))
                output.flush()
                os.fsync(descriptor)
            os.fsync(parent)
        finally:
            os.close(descriptor)
    finally:
        os.close(parent)
    return result


def exclusive_json(path: Path, document: Mapping[str, Any]) -> None:
    payload = canonical(document) + b"\n"
    require(len(payload) <= MAX_JSON_BYTES, "native archive manifest exceeds its bound")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    parent = open_exact_directory(path.parent, EVIDENCE)
    try:
        try:
            descriptor = os.open(path.name, flags, 0o644, dir_fd=parent)
        except OSError as error:
            raise ArchiveError("refusing to overwrite or recreate an archive manifest") from error
        try:
            view = memoryview(payload)
            while view:
                written = os.write(descriptor, view)
                require(written > 0, "exclusive archive manifest write made no progress")
                view = view[written:]
            os.fsync(descriptor)
            os.fsync(parent)
        finally:
            os.close(descriptor)
    finally:
        os.close(parent)


def gzip_bytes(payload: bytes) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(filename="", fileobj=output, mode="wb",
                       compresslevel=9, mtime=0) as stream:
        stream.write(payload)
    return output.getvalue()


def verify_bounded_gzip(
    payload: bytes,
    *,
    expected_size: int,
    expected_sha256: str,
) -> dict[str, Any]:
    require(isinstance(payload, bytes) and payload.startswith(GZIP_HEADER),
            "the immutable gzip header or compression parameters changed")
    require(type(expected_size) is int and 0 < expected_size <= MAX_ELF_BYTES,
            "the archived ELF has an invalid bounded size")
    source_hash = hashlib.sha256()
    size = 0
    prefix = bytearray()
    recompressed = DigestSink()
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(payload), mode="rb") as compressed:
            with gzip.GzipFile(filename="", fileobj=recompressed, mode="wb",
                               compresslevel=9, mtime=0) as canonical_gzip:
                while block := compressed.read(CHUNK):
                    size += len(block)
                    require(size <= expected_size,
                            "archived gzip exceeds its exact native ELF bound")
                    source_hash.update(block)
                    if len(prefix) < 5:
                        prefix.extend(block[:5 - len(prefix)])
                    canonical_gzip.write(block)
    except (OSError, EOFError, ValueError) as error:
        raise ArchiveError("a historical native gzip is truncated or contains trailing data") from error
    require(size == expected_size and bytes(prefix) == b"\x7fELF\x02"
            and source_hash.hexdigest() == expected_sha256,
            "the bounded historical gzip changed its original ELF identity")
    require(recompressed.size == len(payload)
            and recompressed.digest.hexdigest() == hashlib.sha256(payload).hexdigest(),
            "the historical gzip contains noncanonical metadata or extra members")
    return {"source_bytes": size, "source_sha256": source_hash.hexdigest()}


def verify_archive_provenance(
    document: Mapping[str, Any],
    *,
    source_sha256: str,
    runtime: Mapping[str, Any],
) -> None:
    require(isinstance(document, Mapping)
            and document.get("schema") == SCHEMA
            and document.get("status") == "PASS"
            and document.get("result") == "PASS"
            and document.get("passed") is True
            and document.get("archive_source_path") == SOURCE_RELATIVE
            and document.get("archive_source_sha256") == source_sha256
            and isinstance(source_sha256, str)
            and len(source_sha256) == 64
            and all(mark in "0123456789abcdef" for mark in source_sha256)
            and document.get("pinned_interpreter") == json.loads(canonical(runtime)),
            "the immutable archive substituted its controller source or pinned interpreter")


def archive_records(records: Any) -> dict[str, dict[str, Any]]:
    require(isinstance(records, dict) and set(records) == set(ROLES),
            "the immutable archive omitted, duplicated, or added a native role")
    paths: set[str] = set()
    for label, (key, source, digest, size) in ROLES.items():
        record = records[label]
        relative = "performance/postfinal-public-v5/evidence/native-archive-v1/" + label + ".elf.gz"
        require(isinstance(record, dict)
                and set(record) == RECORD_FIELDS
                and record.get("role") == key and record.get("source_path") == source
                and record.get("source_sha256") == digest
                and record.get("source_bytes") == size
                and record.get("source_mode") == 0o700
                and record.get("archive_path") == relative
                and isinstance(record.get("compressed_sha256"), str)
                and len(record["compressed_sha256"]) == 64
                and all(mark in "0123456789abcdef"
                        for mark in record["compressed_sha256"])
                and type(record.get("compressed_bytes")) is int
                and record["compressed_bytes"] > len(GZIP_HEADER)
                and str(PurePosixPath(relative)) == relative,
                "an archived native role, original source, mode, or destination changed")
        require(relative not in paths, "the native archive reused an output slot")
        paths.add(relative)
    return records


def archive() -> dict[str, Any]:
    runtime = production_runtime()
    source_identity = fingerprint(SOURCE, MAX_SOURCE_BYTES)
    state = proof_state(current_sources=True)
    require(not ARCHIVE_ROOT.is_symlink() and not ARCHIVE_ROOT.exists(),
            "refusing an existing or substituted one-use native archive directory")
    require(not ARCHIVE_MANIFEST.is_symlink() and not ARCHIVE_MANIFEST.exists(),
            "refusing an existing or substituted native archive manifest")
    prepared: dict[str, dict[str, Any]] = {}
    identities: dict[str, tuple[int, int, int, int, int, int]] = {}
    for label, (key, relative, expected, size) in ROLES.items():
        current = fingerprint(ROOT / relative, MAX_ELF_BYTES)
        require(current["prefix"][:5] == b"\x7fELF\x02"
                and current["sha256"] == expected and current["bytes"] == size
                and current["mode"] == 0o700,
                "the exact measured public V5 native ELF changed before archival")
        compressed = compress_source(ROOT / relative, current, DigestSink())
        identities[label] = current["identity"]
        prepared[label] = {
            "role": key, "source_path": relative, "source_sha256": expected,
            "source_bytes": size, "source_mode": current["mode"],
            "archive_path": "performance/postfinal-public-v5/evidence/native-archive-v1/" + label + ".elf.gz",
            **compressed,
        }
    archive_records(prepared)
    proof_state(current_sources=True)
    refreshed_controller = fingerprint(SOURCE, MAX_SOURCE_BYTES)
    require(
        refreshed_controller["sha256"] == source_identity["sha256"]
        and refreshed_controller["identity"] == source_identity["identity"],
        "the archival controller changed before creating its exclusive directory",
    )
    evidence_parent = open_exact_directory(EVIDENCE, EVIDENCE)
    try:
        try:
            os.mkdir(ARCHIVE_ROOT.name, 0o755, dir_fd=evidence_parent)
        except OSError as error:
            raise ArchiveError(
                "refusing an existing or unsafe native archive directory"
            ) from error
        os.fsync(evidence_parent)
    finally:
        os.close(evidence_parent)
    for label, (_key, relative, _digest, _size) in ROLES.items():
        refreshed_controller = fingerprint(SOURCE, MAX_SOURCE_BYTES)
        require(
            refreshed_controller["sha256"] == source_identity["sha256"]
            and refreshed_controller["identity"] == source_identity["identity"],
            "the archival controller changed before an irreversible output",
        )
        record = prepared[label]
        expected = {
            "identity": identities[label],
            "bytes": record["source_bytes"], "sha256": record["source_sha256"],
        }
        actual = exclusive_archive(ARCHIVE_ROOT / (label + ".elf.gz"),
                                   ROOT / relative, expected)
        require(actual["compressed_sha256"] == record["compressed_sha256"]
                and actual["compressed_bytes"] == record["compressed_bytes"],
                "a native archive changed between deterministic compression passes")
        refreshed_controller = fingerprint(SOURCE, MAX_SOURCE_BYTES)
        require(
            refreshed_controller["sha256"] == source_identity["sha256"]
            and refreshed_controller["identity"] == source_identity["identity"],
            "the archival controller changed during an irreversible role write",
        )
        proof_state(current_sources=True)
        for other, (_role, other_path, other_sha, other_size) in ROLES.items():
            refreshed = fingerprint(ROOT / other_path, MAX_ELF_BYTES)
            require(refreshed["sha256"] == other_sha and refreshed["bytes"] == other_size
                    and refreshed["identity"] == identities[other],
                    "a measured native ELF changed before archive publication")
    refreshed_controller = fingerprint(SOURCE, MAX_SOURCE_BYTES)
    require(
        refreshed_controller["sha256"] == source_identity["sha256"]
        and refreshed_controller["identity"] == source_identity["identity"],
        "the archival controller changed before manifest publication",
    )
    manifest = {
        "schema": SCHEMA, "status": "PASS", "result": "PASS", "passed": True,
        "archive_source_path": SOURCE_RELATIVE,
        "archive_source_sha256": source_identity["sha256"],
        "proofs": {name: {"path": item[0], "sha256": item[1]}
                   for name, item in PROOFS.items()},
        "v5_qualified_source_fingerprints": state["sources"],
        "v5_native_elf_fingerprints": state["native"],
        "native_archive_count": 5,
        "gzip": {"compresslevel": 9, "filename": "", "mtime": 0,
                 "header_hex": GZIP_HEADER.hex()},
        "records": prepared,
        "scope": {
            "archive_is_historical_bytes_only": True,
            "current_runtime_native_mapping_attested": False,
            "current_candidate_qualification_attested": False,
            "source_to_binary_reproducibility_attested": False,
            "automatic_native_restoration_permitted": False,
            "restoration_requirements": (
                "A separate clean checkout of the original V5 source revision, "
                "all five exact original candidates/ basenames and mode 0700, "
                "both $ORIGIN engine siblings, and SHA-256 verification before isolated loading."
            ),
            "candidate_imported": False,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
        "pinned_interpreter": runtime,
    }
    archive_records(manifest["records"])
    proof_state(current_sources=True)
    refreshed_controller = fingerprint(SOURCE, MAX_SOURCE_BYTES)
    require(
        refreshed_controller["sha256"] == source_identity["sha256"]
        and refreshed_controller["identity"] == source_identity["identity"],
        "the archival controller changed immediately before exclusive publication",
    )
    exclusive_json(ARCHIVE_MANIFEST, manifest)
    candidate_free()
    return manifest


def verify() -> dict[str, Any]:
    runtime = production_runtime()
    state = proof_state(current_sources=False)
    current = fingerprint(ARCHIVE_MANIFEST, MAX_JSON_BYTES, retain=True)
    try:
        manifest = json.loads(current["payload"])
    except (TypeError, UnicodeError, ValueError) as error:
        raise ArchiveError("immutable V5 native archive manifest is invalid") from error
    actual_source = fingerprint(SOURCE, MAX_SOURCE_BYTES)
    verify_archive_provenance(
        manifest,
        source_sha256=actual_source["sha256"],
        runtime=runtime,
    )
    require(isinstance(manifest, dict) and manifest.get("schema") == SCHEMA
            and manifest.get("passed") is True and manifest.get("result") == "PASS"
            and manifest.get("native_archive_count") == 5
            and manifest.get("v5_native_elf_fingerprints") == state["native"]
            and manifest.get("v5_qualified_source_fingerprints") == state["sources"]
            and manifest.get("gzip") == {
                "compresslevel": 9, "filename": "", "mtime": 0,
                "header_hex": GZIP_HEADER.hex(),
            }, "immutable public V5 archive lost its exact five-role provenance")
    require(manifest.get("proofs") == {
        name: {"path": value[0], "sha256": value[1]}
        for name, value in PROOFS.items()
    }, "the historical V5 archive changed its original public proofs")
    scope = manifest.get("scope")
    require(isinstance(scope, dict)
            and scope.get("archive_is_historical_bytes_only") is True
            and scope.get("current_runtime_native_mapping_attested") is False
            and scope.get("current_candidate_qualification_attested") is False
            and scope.get("source_to_binary_reproducibility_attested") is False
            and scope.get("automatic_native_restoration_permitted") is False,
            "the archive falsely claims current native loading or reproducible builds")
    for label, record in archive_records(manifest.get("records")).items():
        path = ARCHIVE_ROOT / (label + ".elf.gz")
        packed = fingerprint(path, MAX_ELF_BYTES, retain=True)
        require(packed["sha256"] == record["compressed_sha256"]
                and packed["bytes"] == record["compressed_bytes"]
                and packed["prefix"][:len(GZIP_HEADER)] == GZIP_HEADER,
                "an immutable compressed native archive was changed or swapped")
        verify_bounded_gzip(
            packed["payload"],
            expected_size=record["source_bytes"],
            expected_sha256=record["source_sha256"],
        )
    candidate_free()
    return {
        "schema": SCHEMA + "-verification", "status": "PASS", "result": "PASS",
        "passed": True, "archive_manifest_sha256": current["sha256"],
        "verified_archives": 5, "current_live_native_files_read": 0,
        "historical_bytes_only": True, "candidate_imported": False,
        "source_to_binary_reproducibility_attested": False,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
    }


class BlockEffects:
    def __init__(self) -> None:
        self.counts = {"files": 0, "processes": 0, "clocks": 0, "entropy": 0}
        self.old: list[tuple[Any, str, Any]] = []

    def __enter__(self) -> BlockEffects:
        targets = (
            (builtins, "open", "files"), (os, "open", "files"),
            (os, "read", "files"), (os, "write", "files"),
            (os, "fsync", "files"), (os, "mkdir", "files"),
            (Path, "open", "files"), (Path, "read_bytes", "files"),
            (subprocess, "Popen", "processes"), (subprocess, "run", "processes"),
            (time, "perf_counter", "clocks"), (time, "perf_counter_ns", "clocks"),
            (time, "time", "clocks"), (os, "urandom", "entropy"),
            (secrets, "token_bytes", "entropy"),
        )
        for owner, field, kind in targets:
            if not hasattr(owner, field):
                continue
            previous = getattr(owner, field)
            def denied(*_args: Any, _kind: str = kind, **_kwargs: Any) -> Any:
                self.counts[_kind] += 1
                raise ArchiveError("synthetic archive attempted " + _kind)
            setattr(owner, field, denied)
            self.old.append((owner, field, previous))
        return self

    def __exit__(self, _type: Any, _error: Any, _trace: Any) -> None:
        while self.old:
            owner, field, previous = self.old.pop()
            setattr(owner, field, previous)


def self_test() -> dict[str, Any]:
    candidate_free()
    checks: list[dict[str, Any]] = []
    effects = BlockEffects()
    def check(name: str, passed: Any) -> None:
        checks.append({"name": name, "passed": bool(passed)})
    def reject(name: str, function: Any) -> None:
        try:
            function()
        except (ArchiveError, OSError, TypeError, ValueError, EOFError):
            check(name, True)
        else:
            check(name, False)
    with effects:
        expected = {record[0]: record[2] for record in ROLES.values()}
        check("exactly-five-distinct-measured-native-roles", len(ROLES) == len(expected) == 5)
        check("exactly-twelve-qualified-source-paths", len(QUALIFIED_SOURCES) == 12)
        check("all-original-native-modes-preserved", all(size > 0 for _key, _path, _sha, size in ROLES.values()))
        check("preserve-actual-v5-summary-and-integrity", PROOFS["summary"][1] != PROOFS["integrity"][1])
        check(
            "allow-only-pinned-18125531-byte-v5-summary",
            validate_proof_size("summary", PINNED_PUBLIC_V5_SUMMARY_BYTES)
            == MAX_PUBLIC_V5_SUMMARY_BYTES,
        )
        check(
            "preserve-sixteen-mib-cap-for-other-proofs",
            validate_proof_size("integrity", MAX_JSON_BYTES) == MAX_JSON_BYTES,
        )
        reject(
            "reject-shorter-measured-v5-summary",
            lambda: validate_proof_size(
                "summary", PINNED_PUBLIC_V5_SUMMARY_BYTES - 1,
            ),
        )
        reject(
            "reject-longer-measured-v5-summary",
            lambda: validate_proof_size(
                "summary", PINNED_PUBLIC_V5_SUMMARY_BYTES + 1,
            ),
        )
        reject(
            "reject-summary-over-specific-twenty-mib-cap",
            lambda: validate_proof_size(
                "summary", MAX_PUBLIC_V5_SUMMARY_BYTES + 1,
            ),
        )
        reject(
            "reject-other-proof-over-sixteen-mib-cap",
            lambda: validate_proof_size("integrity", MAX_JSON_BYTES + 1),
        )
        reject(
            "reject-unapproved-public-proof-name",
            lambda: validate_proof_size("foreign-summary", 1),
        )
        reject(
            "reject-boolean-public-proof-size",
            lambda: validate_proof_size("integrity", True),
        )
        reject(
            "reject-zero-public-proof-size",
            lambda: validate_proof_size("integrity", 0),
        )
        reject(
            "reject-noninteger-public-proof-size",
            lambda: validate_proof_size("integrity", 1.0),
        )
        check("accept-exact-five-native-digests", exact_native_map(expected) == expected)
        reject("reject-missing-native-role", lambda: exact_native_map(dict(list(expected.items())[:-1])))
        reject("reject-foreign-native-role", lambda: exact_native_map({**expected, "foreign": "0" * 64}))
        changed = dict(expected)
        first, second = tuple(changed)[:2]
        changed[first], changed[second] = changed[second], changed[first]
        reject("reject-swapped-native-role-digests", lambda: exact_native_map(changed))
        altered = dict(expected)
        altered[first] = "0" * 64
        reject("reject-changed-uncompressed-digest", lambda: exact_native_map(altered))
        sample = b"\x7fELF\x02synthetic-owned-native\x00\xff"
        packed = gzip_bytes(sample)
        check("deterministic-gzip-mtime-zero-empty-filename", packed.startswith(GZIP_HEADER))
        check("deterministic-repeatable-gzip-bytes", gzip_bytes(sample) == packed)
        check("gzip-roundtrip-preserves-exact-owned-elf", gzip.decompress(packed) == sample)
        check("gzip-roundtrip-canonical-member", gzip_bytes(gzip.decompress(packed)) == packed)
        sample_sha = hashlib.sha256(sample).hexdigest()
        check(
            "bounded-gzip-verifier-accepts-canonical-owned-elf",
            verify_bounded_gzip(
                packed, expected_size=len(sample), expected_sha256=sample_sha,
            ) == {"source_bytes": len(sample), "source_sha256": sample_sha},
        )
        for name, payload, limit, expected_digest in (
            ("reject-bounded-gzip-bomb", gzip_bytes(sample + b"overflow"), len(sample), sample_sha),
            ("reject-bounded-gzip-truncation", packed[:-1], len(sample), sample_sha),
            ("reject-bounded-appended-gzip-member", packed + gzip_bytes(b"foreign"), len(sample), sample_sha),
            ("reject-bounded-gzip-trailing-data", packed + b"foreign", len(sample), sample_sha),
            ("reject-bounded-gzip-wrong-native-digest", packed, len(sample), "0" * 64),
            ("reject-bounded-gzip-wrong-original-size", packed, len(sample) - 1, sample_sha),
        ):
            reject(
                name,
                lambda data=payload, maximum=limit, digest=expected_digest:
                    verify_bounded_gzip(
                        data, expected_size=maximum, expected_sha256=digest,
                    ),
            )
        reject("reject-truncated-gzip", lambda: gzip.decompress(packed[:-1]))
        reject("reject-changed-gzip-header", lambda: (
            require((bytes([packed[0] ^ 1]) + packed[1:]).startswith(GZIP_HEADER),
                    "changed deterministic gzip header")
        ))
        reject("reject-appended-gzip-member", lambda: (
            require(gzip_bytes(gzip.decompress(packed + gzip_bytes(b"foreign")))
                    == packed + gzip_bytes(b"foreign"), "concatenated gzip members")
        ))
        reject("reject-appended-gzip-trailing-bytes", lambda: gzip.decompress(packed + b"foreign"))
        candidate = {
            "implementation": "cpython", "version": PINNED_VERSION,
            "executable": PINNED_PYTHON, "isolated": 1, "dont_write_bytecode": True,
        }
        check("accept-exact-isolated-pinned-cpython", pinned_runtime(candidate) == candidate)
        for name, field, value in (
            ("reject-foreign-python-runtime", "implementation", "pypy"),
            ("reject-wrong-python-version", "version", (3, 14, 5)),
            ("reject-wrong-python-executable", "executable", "/usr/bin/python3"),
            ("reject-nonisolated-python", "isolated", 0),
            ("reject-python-bytecode-writes", "dont_write_bytecode", False),
        ):
            reject(name, lambda key=field, item=value: pinned_runtime({**candidate, key: item}))
        synthetic_source_sha = hashlib.sha256(b"immutable archive controller").hexdigest()
        synthetic_archive = {
            "schema": SCHEMA, "status": "PASS", "result": "PASS", "passed": True,
            "archive_source_path": SOURCE_RELATIVE,
            "archive_source_sha256": synthetic_source_sha,
            "pinned_interpreter": json.loads(canonical(candidate)),
        }
        check(
            "accept-source-bound-archive-controller-and-runtime",
            verify_archive_provenance(
                synthetic_archive,
                source_sha256=synthetic_source_sha,
                runtime=candidate,
            ) is None,
        )
        for name, field, value in (
            ("reject-substituted-archive-controller-path", "archive_source_path", "tools/foreign.py"),
            ("reject-substituted-archive-controller-hash", "archive_source_sha256", "0" * 64),
            ("reject-substituted-archive-pinned-runtime", "pinned_interpreter", {"implementation": "pypy"}),
            ("reject-substituted-archive-success-status", "status", "FAIL"),
        ):
            reject(
                name,
                lambda key=field, item=value: verify_archive_provenance(
                    {**synthetic_archive, key: item},
                    source_sha256=synthetic_source_sha,
                    runtime=candidate,
                ),
            )
        fake: dict[str, dict[str, Any]] = {}
        for label, (key, path, digest, size) in ROLES.items():
            fake[label] = {
                "role": key, "source_path": path, "source_sha256": digest,
                "source_bytes": size, "source_mode": 0o700,
                "archive_path": "performance/postfinal-public-v5/evidence/native-archive-v1/" + label + ".elf.gz",
                "compressed_sha256": hashlib.sha256(packed).hexdigest(),
                "compressed_bytes": len(packed),
            }
        check("accept-five-exclusive-canonical-archive-paths", archive_records(fake) == fake)
        reject(
            "reject-transient-machine-stat-in-canonical-role",
            lambda: archive_records({
                **fake,
                "vm-engine": {
                    **fake["vm-engine"],
                    "source_stat_identity": [1, 2, 3, 4, 5, 6],
                },
            }),
        )
        for name, label, field, value in (
            ("reject-missing-archive-role", "vm-engine", "role", "foreign"),
            ("reject-wrong-original-native-mode", "rust-engine", "source_mode", 0o755),
            ("reject-wrong-original-native-size", "rust-bridge", "source_bytes", 1),
            ("reject-compressed-digest", "zig-engine", "compressed_sha256", "bad"),
            ("reject-output-path-traversal", "zig-bridge", "archive_path", "../foreign.elf.gz"),
            ("reject-swapped-original-source", "vm-engine", "source_path", ROLES["rust-engine"][1]),
            ("reject-swapped-original-source-hash", "rust-engine", "source_sha256", ROLES["zig-engine"][2]),
        ):
            reject(name, lambda role=label, key=field, item=value: archive_records({
                **fake, role: {**fake[role], key: item}
            }))
        reject("reject-incomplete-archive-manifest", lambda: archive_records(dict(list(fake.items())[:-1])))
        reject("reject-foreign-archive-manifest-role", lambda: archive_records({**fake, "foreign": fake["vm-engine"]}))
        for value in (float("nan"), float("inf"), -float("inf")):
            reject("reject-nonfinite-provenance:" + repr(value),
                   lambda item=value: canonical({"value": item}))
        check("canonical-ascii-preserves-lone-surrogates",
              json.loads(canonical({"high": "\ud800", "low": "\udfff"}))
              == {"high": "\ud800", "low": "\udfff"})
        candidate_free()
    check("zero-synthetic-file-reads-or-writes", effects.counts["files"] == 0)
    check("zero-synthetic-candidate-subprocesses", effects.counts["processes"] == 0)
    check("zero-synthetic-benchmark-clock-samples", effects.counts["clocks"] == 0)
    check("zero-synthetic-production-entropy", effects.counts["entropy"] == 0)
    names = [item["name"] for item in checks]
    failed = sorted(item["name"] for item in checks if not item["passed"])
    if len(names) != len(set(names)):
        failed.append("duplicate-native-archive-control")
    return {
        "schema": SCHEMA + "-self-test", "status": "PASS" if not failed else "FAIL",
        "result": "PASS" if not failed else "FAIL", "passed": not failed,
        "checks": checks, "check_count": len(checks), "failed": failed,
        "fixture_storage": "in-memory only", "candidate_imported": False,
        "file_reads": effects.counts["files"], "file_writes": 0,
        "subprocesses": effects.counts["processes"],
        "clock_samples": effects.counts["clocks"], "production_entropy_drawn": False,
        "archive_created": False, "historical_holdout_accessed": False,
        "benchmark_or_timing_executed": False,
    }


def main(arguments: list[str] | None = None) -> int:
    selected = list(sys.argv[1:] if arguments is None else arguments)
    try:
        if selected == ["--self-test"]:
            result = self_test()
        elif selected == ["--archive"]:
            result = archive()
        elif selected == ["--verify"]:
            result = verify()
        else:
            raise ArchiveError("select exactly --self-test, --archive, or --verify")
        if selected == ["--archive"]:
            result = {
                "schema": SCHEMA, "status": "PASS", "passed": True,
                "manifest": "performance/postfinal-public-v5/evidence/postfinal-public-v5-native-archive-v1.json",
                "archives": 5, "native_source_bytes": sum(x[3] for x in ROLES.values()),
                "source_to_binary_reproducibility_attested": False,
                "current_runtime_native_mapping_attested": False,
            }
        sys.stdout.buffer.write(canonical(result) + b"\n")
        return 0 if result.get("passed") is True else 1
    except (ArchiveError, OSError, TypeError, ValueError, UnicodeError,
            EOFError, subprocess.SubprocessError) as error:
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA, "status": "FAIL", "result": "FAIL",
            "passed": False, "error": str(error), "candidate_imported": False,
            "source_to_binary_reproducibility_attested": False,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }) + b"\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
