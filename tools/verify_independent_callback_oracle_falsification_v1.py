#!/usr/bin/env python3
"""Read-only, independently reproducible proof of frozen callback artifacts.

No candidate, reference, regex matcher, benchmark, holdout, clock, or worker is
run.  Historical worker observations are authenticated and replayed as data.
The self-test uses only synthetic, in-memory data behind a deny-all boundary.
"""

from __future__ import annotations

import base64
import binascii
import builtins
import codecs
import collections
import contextlib
import hashlib
import io
import json
import os
import pathlib
import stat
import subprocess
import sys
import threading
import time
import types
import zlib
from dataclasses import dataclass
from typing import Any, Callable, Iterator, Mapping

ROOT = "/home/dev-user/src/rebar"
SOURCE_RELATIVE = "tools/verify_independent_callback_oracle_falsification_v1.py"
SCHEMA = "rebar-independent-callback-oracle-falsification-v1"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
PINNED_STDLIB_DIRECTORY = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/"
)
PINNED_STDLIB_SOURCES = {
    "re": (
        "__init__.py",
        "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35",
    ),
    "re._compiler": (
        "_compiler.py",
        "d49f30cf9a1dbae33b200ed8befd9d0ce3ac612783a10ac35196536f98923e91",
    ),
    "re._parser": (
        "_parser.py",
        "e57bd194a2d42398355ae7c1ccc2ddfb78421dd431eb81e3809dbe8ca9057dc4",
    ),
    "re._constants": (
        "_constants.py",
        "42253b3181b81aad6c46392f44a0ab26dcfa31feea411296f43ba16616a1ab0b",
    ),
}
V5_RELATIVE = "tools/independent_original_cpython_suite_v5.py"
V5_SHA256 = "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
AUDIT_RELATIVE = "tools/independent_from_scratch_audit_v3.py"
AUDIT_SHA256 = "377c63eecccea021562694e00d624d54f61adfb0d3a4700586a29ed424f389ee"
POLICY_RELATIVE = "tools/independent_from_scratch_audit_v2.py"
POLICY_SHA256 = "e68aaeddc8cf63a553e00ad919f3cb5c9bd584ba8c5d87214a0a36c3846dca8d"
TRUSTED_CTYPES_SHA256 = (
    "349448c149c46962d6004808a214b4677267563204ec32cb6ef933effe0ee923"
)
CHUNK_BYTES = 131_072
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_RECEIPT_BYTES = 8 * 1024 * 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 384 * 1024 * 1024
MAX_PROCESS_BYTES = 192 * 1024 * 1024
MAX_ENCODED_PROCESS_STREAM_BYTES = ((MAX_PROCESS_BYTES + 2) // 3) * 4
MAX_SELECTED_VALUE_BYTES = 320 * 1024 * 1024
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
APIS = ("module.sub", "module.subn", "pattern.sub", "pattern.subn")
GUARD_TRUE_FIELDS = (
    "original_matchers_blocked",
    "adapter_import_quarantined",
    "native_sre_blocked",
    "builtins_import_guarded",
    "importlib_import_guarded",
    "actual_object_identity_guarded",
    "warning_registry_introspection_safe",
    "warning_registry_exactly_absent",
    "cross_family_imports_blocked",
    "external_regex_imports_blocked",
)
GUARD_COUNTER_FIELDS = (
    "cached_original_matcher_descendant_count",
    "cached_original_holder_count",
    "owned_ctypes_load_count",
    "owned_ctypes_symbol_count",
)
FORBIDDEN_IMPORT_ROOTS = frozenset(
    {"candidates", "rebar", "regex", "pcre", "pcre2", "re2", "hyperscan"}
)


class VerificationError(Exception):
    """An immutable observation, process, guard, ledger, or boundary changed."""


class SourceOnlyError(VerificationError):
    """A synthetic self-test attempted to touch real external state."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def checked_digest(value: Any, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        "an exact lowercase SHA-256 is mandatory: " + label,
    )
    return value


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in result, "a JSON field was duplicated")
        result[key] = value
    return result


def reject_nonfinite(value: str) -> Any:
    raise VerificationError("a non-finite JSON value is forbidden: " + value)


def canonical(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                ensure_ascii=True,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("ascii")
            + b"\n"
        )
    except (TypeError, ValueError, UnicodeError, OverflowError) as error:
        raise VerificationError("evidence is not canonical lossless JSON") from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def decode_document(raw: bytes, maximum: int, label: str) -> dict[str, Any]:
    require(
        type(raw) is bytes and 0 < len(raw) <= maximum,
        "complete bounded canonical bytes are mandatory: " + label,
    )
    try:
        value = json.loads(
            raw,
            object_pairs_hook=unique_object,
            parse_constant=reject_nonfinite,
        )
    except (json.JSONDecodeError, UnicodeError, RecursionError) as error:
        raise VerificationError("a complete JSON document was forged: " + label) from error
    require(
        type(value) is dict and canonical(value) == raw,
        "noncanonical, duplicate, or trailing JSON is forbidden: " + label,
    )
    return value


@dataclass(frozen=True, slots=True)
class ArchivePin:
    relative: str
    sha256: str
    compressed_bytes: int
    report_sha256: str
    report_bytes: int
    receipt_relative: str
    receipt_sha256: str


@dataclass(frozen=True, slots=True)
class SuitePin:
    name: str
    oracle_relative: str
    oracle_sha256: str
    recorder_relative: str
    recorder_sha256: str
    matrix_sha256: str
    seed: int
    case_count: int
    variants_per_cohort: int
    baseline_records_sha256: str
    callback_class: str
    callback_message: str
    callback_module: str
    baseline: ArchivePin
    previous_recorder_relative: str | None = None
    previous_recorder_sha256: str | None = None


@dataclass(frozen=True, slots=True)
class CandidatePin:
    suite: SuitePin
    family: str
    label: str
    archive: ArchivePin
    records_sha256: str
    full_ledger_sha256: str
    mismatch_count: int
    artifact_count: int
    genuine_count: int
    candidate_source_sha256: str
    native_bridge_sha256: str
    native_engine_sha256: str


SUBSTITUTION = SuitePin(
    name="substitution-buffer-semantics",
    oracle_relative="tools/independent_substitution_buffer_semantics_v1.py",
    oracle_sha256="a325528aa62f107969b9dfdf5dea2ae8f9426607887a317fe20fcf9a1b7fd445",
    recorder_relative="tools/record_independent_substitution_buffer_semantics_v2.py",
    recorder_sha256="a7cf45ce72a178fead7eb0d0789fd1f0f37ed63789fe086070eefa613e959a33",
    matrix_sha256="26f46fe7f1abc5135d1265a7882ccd4a2e2b45cdec80ba293520fda510235b54",
    seed=6_004_778_603_531_028_017,
    case_count=5_120,
    variants_per_cohort=80,
    baseline_records_sha256=(
        "3e74498c0c6997bcb86fab81a4be2962809c77b49d7214837633c9539c42ad18"
    ),
    callback_class="ReplacementCallbackError",
    callback_message="frozen substitution callback failure",
    callback_module="tools.independent_substitution_buffer_semantics_v1",
    baseline=ArchivePin(
        relative=(
            "experiments/rust_public_practice_v1/"
            "substitution-buffer-semantics-v1-shared-suite-v1.json.gz"
        ),
        sha256="2e24e17862e75f4f2f778d15d67416f6e643eff01c0d110e750cea99b2550fab",
        compressed_bytes=6_340_529,
        report_sha256="4f1334d4935034b62be06139bcbbe0226af31e889dba9de2716c87b81d7992f3",
        report_bytes=87_081_836,
        receipt_relative=(
            "experiments/rust_public_practice_v1/"
            "substitution-buffer-semantics-v1-shared-suite-v1-publication-receipt.json"
        ),
        receipt_sha256="9a707f4953b8ed23d1f3e0cb5f4f6fd6e2e104e675fe502a3e991ebb2e884cd2",
    ),
    previous_recorder_relative=(
        "tools/record_independent_substitution_buffer_semantics_v1.py"
    ),
    previous_recorder_sha256=(
        "1dbb45e8950a0eceb966a56adcbe2f9d1da35ec04883458a780b6f08f5a4735d"
    ),
)
SHAPE = SuitePin(
    name="shape-changing-buffer-semantics",
    oracle_relative="tools/independent_shape_changing_buffer_semantics_v1.py",
    oracle_sha256="866dbf7bf4a48a867b3aaacd05cfa4f1346c747931543fa386835e783f0073aa",
    recorder_relative="tools/record_independent_shape_changing_buffer_semantics_v1.py",
    recorder_sha256="047bcc25a3b033fa374576c434b0e6ebcc6c97cf99965e9cc9083c012249529c",
    matrix_sha256="10fe3e3fd4b4650bff1da6a745b5b883f01033ed14df3f9795aa2f7a30c6d8d8",
    seed=6_001_118_316_486_346_290,
    case_count=10_240,
    variants_per_cohort=160,
    baseline_records_sha256=(
        "0aeddfa2835be5895bc6d88edae5ecc4945241c7ea456c0487497be4c47f8373"
    ),
    callback_class="ShapeCallbackError",
    callback_message="frozen shape-changing callback failure",
    callback_module="tools.independent_shape_changing_buffer_semantics_v1",
    baseline=ArchivePin(
        relative=(
            "experiments/rust_public_practice_v1/"
            "shape-changing-buffer-semantics-v1-shared-suite-v1.json.gz"
        ),
        sha256="8bf48813d82966edbed05330ce26f6c8a3d80ee72c59a6dbfa104ff397906b5b",
        compressed_bytes=11_933_273,
        report_sha256="8605fd0dd72e505f58eac0a6ea79ff4a5b9f21d0a0415ee1404aca6a848c0552",
        report_bytes=179_411_616,
        receipt_relative=(
            "experiments/rust_public_practice_v1/"
            "shape-changing-buffer-semantics-v1-shared-suite-v1-publication-receipt.json"
        ),
        receipt_sha256="8744ebf8fb29924661d8c379b3fa1d7662e6dd44ebca49ecd7d37219f06ac7c9",
    ),
)
C_SOURCE_SHA256 = "9fe2e30ee6be7c5daa80df0174b371b1b7074f379724aee530c1ebfa0707eb6d"
C_NATIVE_SHA256 = "075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd"
ZIG_SOURCE_SHA256 = "03a3312833252ef0a0c84df0e7e375c89b115ad772ccdd72faa51fc563950435"
ZIG_BRIDGE_SHA256 = "d8ac0da492d960716cbc74c25d7cb5027aea3fcfe2bf0a6fb2ec8e432345fb3b"
ZIG_NATIVE_SHA256 = "b76eb6c7ecd60c1d221f6ddb822573a5f962641cf4e6f16da75d21561b104652"
C_SUBSTITUTION = CandidatePin(
    suite=SUBSTITUTION,
    family="c",
    label="native-lifetime-repair-v1",
    archive=ArchivePin(
        relative=(
            "experiments/rust_public_practice_v1/"
            "c-substitution-buffer-semantics-v1-native-lifetime-repair-v1.json.gz"
        ),
        sha256="b1545e5850caaf59fd9640358527dfaf160f90b3f48fc9f80accd5a49a305111",
        compressed_bytes=839_723,
        report_sha256="cd6ed6aa853f51989e473b0cfe3a5d8b4cd8c8576d758919954e27cd4de4ed7c",
        report_bytes=18_841_043,
        receipt_relative=(
            "experiments/rust_public_practice_v1/"
            "c-substitution-buffer-semantics-v1-native-lifetime-repair-v1-"
            "publication-receipt.json"
        ),
        receipt_sha256="933852815241f3b2c82f6e5a07a5624422c323c7d4f86cebeb3f6f700cefa5b2",
    ),
    records_sha256="39e318519c1b463c853103b14c099df56b974c595a6a5301bad91e386fabbf04",
    full_ledger_sha256="dd3662164eddb3ac983f9618f0b53a2c52fbbe31f8cc456731109ef89cad9f13",
    mismatch_count=464,
    artifact_count=128,
    genuine_count=336,
    candidate_source_sha256=C_SOURCE_SHA256,
    native_bridge_sha256=C_NATIVE_SHA256,
    native_engine_sha256=C_NATIVE_SHA256,
)
ZIG_SUBSTITUTION = CandidatePin(
    suite=SUBSTITUTION,
    family="zig",
    label="owned-safe-buffer-repair-v1",
    archive=ArchivePin(
        relative=(
            "experiments/rust_public_practice_v1/"
            "zig-substitution-buffer-semantics-v1-owned-safe-buffer-repair-v1.json.gz"
        ),
        sha256="8adefae4fb5248d3a95cefc852bfafa9dfca39d0d868a0b424df6394eef9a402",
        compressed_bytes=815_309,
        report_sha256="0d6b6a5878e408125e09177f36003004da161c2104af297d41ac2331ed0a8c93",
        report_bytes=18_750_611,
        receipt_relative=(
            "experiments/rust_public_practice_v1/"
            "zig-substitution-buffer-semantics-v1-owned-safe-buffer-repair-v1-"
            "publication-receipt.json"
        ),
        receipt_sha256="89d5f12fb076b4152cf14a12d6fd22f18a0ba99c07a82a2a8efdb4d1ff12a03e",
    ),
    records_sha256="027bb34006927e9f86134b7c6f29ebf81b331b077b1133f4d12af6267cfb4a1b",
    full_ledger_sha256="a01c0e3a9bbe11be08502e2469f9052f31748520fc5cd513ea20795719d4a48a",
    mismatch_count=192,
    artifact_count=128,
    genuine_count=64,
    candidate_source_sha256=ZIG_SOURCE_SHA256,
    native_bridge_sha256=ZIG_BRIDGE_SHA256,
    native_engine_sha256=ZIG_NATIVE_SHA256,
)
C_SHAPE = CandidatePin(
    suite=SHAPE,
    family="c",
    label="native-lifetime-repair-pid-retry-v1",
    archive=ArchivePin(
        relative=(
            "experiments/rust_public_practice_v1/"
            "c-shape-changing-buffer-semantics-v1-native-lifetime-repair-"
            "pid-retry-v1.json.gz"
        ),
        sha256="8660c07a379901e4163b6204199c5a903013c2e9efa051ac67560d89085542db",
        compressed_bytes=1_763_037,
        report_sha256="199448cc81c3c544a95ef0ccb75fad78141ecae347b2883231deddf86a31ebac",
        report_bytes=55_851_919,
        receipt_relative=(
            "experiments/rust_public_practice_v1/"
            "c-shape-changing-buffer-semantics-v1-native-lifetime-repair-"
            "pid-retry-v1-publication-receipt.json"
        ),
        receipt_sha256="d4d7c6f184e3a0dbea06ab9bbf8cbe13a945dcb4914a567e17a7b25a9a74b1b2",
    ),
    records_sha256="b54207667c3922e57fd1af0f209bf2e468a8f2cfb9906e83bf2ebd845e4b8295",
    full_ledger_sha256="e98fc451e765f2c196ca8c4b8fceeefff1c909d2416b71ec0c4cdeeaf37589e3",
    mismatch_count=1_888,
    artifact_count=496,
    genuine_count=1_392,
    candidate_source_sha256=C_SOURCE_SHA256,
    native_bridge_sha256=C_NATIVE_SHA256,
    native_engine_sha256=C_NATIVE_SHA256,
)
CANDIDATES = (C_SUBSTITUTION, ZIG_SUBSTITUTION, C_SHAPE)
SUITES = (SUBSTITUTION, SHAPE)
APPROVED_FILES = frozenset(
    {SOURCE_RELATIVE, V5_RELATIVE, AUDIT_RELATIVE, POLICY_RELATIVE}
    | {
        relative
        for suite in SUITES
        for relative in (
            suite.oracle_relative,
            suite.recorder_relative,
            suite.baseline.relative,
            suite.baseline.receipt_relative,
        )
    }
    | {
        relative
        for suite in SUITES
        for relative in (suite.previous_recorder_relative,)
        if relative is not None
    }
    | {
        relative
        for candidate in CANDIDATES
        for relative in (
            candidate.archive.relative,
            candidate.archive.receipt_relative,
        )
    }
)


def safe_parts(relative: str) -> tuple[str, ...]:
    require(
        type(relative) is str
        and relative in APPROVED_FILES
        and "\x00" not in relative
        and not relative.startswith("/")
        and "\\" not in relative,
        "only an exact immutable approved evidence path may be opened",
    )
    parts = tuple(relative.split("/"))
    require(
        bool(parts) and all(part not in ("", ".", "..") for part in parts),
        "a path alias, traversal, or empty evidence component is forbidden",
    )
    return parts


@contextlib.contextmanager
def open_owned(relative: str, maximum: int) -> Iterator[tuple[int, os.stat_result]]:
    parts = safe_parts(relative)
    require(
        type(maximum) is int and 0 < maximum <= MAX_UNCOMPRESSED_BYTES,
        "an exact positive, bounded evidence limit is mandatory",
    )
    regular = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    directory_flags = regular | getattr(os, "O_DIRECTORY", 0)
    opened: list[int] = []
    try:
        current = os.open(ROOT, directory_flags)
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode), "the workspace was substituted")
        for part in parts[:-1]:
            current = os.open(part, directory_flags, dir_fd=current)
            opened.append(current)
            require(
                stat.S_ISDIR(os.fstat(current).st_mode),
                "an approved evidence parent was replaced by a symlink",
            )
        descriptor = os.open(parts[-1], regular, dir_fd=current)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(
            stat.S_ISREG(before.st_mode)
            and stat.S_ISREG(named.st_mode)
            and (before.st_dev, before.st_ino, before.st_size)
            == (named.st_dev, named.st_ino, named.st_size)
            and 0 < before.st_size <= maximum,
            "an approved bounded evidence owner was substituted",
        )
        yield descriptor, before
        after = os.fstat(descriptor)
        named_after = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        require(
            identity
            == (
                after.st_dev,
                after.st_ino,
                after.st_size,
                after.st_mtime_ns,
            )
            == (
                named_after.st_dev,
                named_after.st_ino,
                named_after.st_size,
                named_after.st_mtime_ns,
            ),
            "an approved immutable evidence owner changed while being read",
        )
    except (OSError, ValueError, OverflowError) as error:
        raise VerificationError("an approved no-follow evidence owner is inaccessible") from error
    finally:
        for descriptor in reversed(opened):
            try:
                os.close(descriptor)
            except OSError:
                pass


def read_frozen(relative: str, expected: str, maximum: int) -> bytes:
    checked_digest(expected, relative)
    with open_owned(relative, maximum) as (descriptor, owner):
        output = bytearray()
        hasher = hashlib.sha256()
        while len(output) < owner.st_size:
            block = os.read(descriptor, min(CHUNK_BYTES, owner.st_size - len(output)))
            require(type(block) is bytes and bool(block), "a frozen evidence file was truncated")
            output.extend(block)
            hasher.update(block)
        require(
            os.read(descriptor, 1) == b""
            and len(output) == owner.st_size
            and hasher.hexdigest() == expected,
            "a complete frozen evidence file failed its exact hash",
        )
        return bytes(output)


class VerifiedGzipReader:
    """Authenticate exactly one complete, bounded frozen gzip member."""

    def __init__(
        self,
        descriptor: int,
        archive_bytes: int,
        archive_sha256: str,
        original_bytes: int,
        original_sha256: str,
        read_block: Callable[[int, int], bytes] | None = None,
    ) -> None:
        require(
            type(descriptor) is int
            and type(archive_bytes) is int
            and 0 < archive_bytes <= MAX_ARCHIVE_BYTES
            and type(original_bytes) is int
            and 0 < original_bytes <= MAX_UNCOMPRESSED_BYTES,
            "exact bounded compressed and original evidence is mandatory",
        )
        self.descriptor = descriptor
        self.read_block = os.read if read_block is None else read_block
        self.archive_bytes = archive_bytes
        self.archive_sha256 = checked_digest(
            archive_sha256,
            "complete callback-evidence gzip",
        )
        self.original_bytes = original_bytes
        self.original_sha256 = checked_digest(
            original_sha256,
            "complete restored callback-evidence report",
        )
        self.inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
        self.compressed_hash = hashlib.sha256()
        self.original_hash = hashlib.sha256()
        self.compressed_count = 0
        self.original_count = 0
        self.pending = b""
        self.finished = False

    def read(self, requested: int) -> bytes:
        require(
            type(requested) is int and 0 < requested <= CHUNK_BYTES,
            "stream only bounded complete frozen evidence blocks",
        )
        result = bytearray()
        while len(result) < requested and not self.finished:
            if (
                not self.pending
                and self.compressed_count < self.archive_bytes
            ):
                block = self.read_block(
                    self.descriptor,
                    min(
                        CHUNK_BYTES,
                        self.archive_bytes - self.compressed_count,
                    ),
                )
                require(
                    type(block) is bytes and bool(block),
                    "a genuinely authenticated gzip was truncated",
                )
                self.compressed_count += len(block)
                self.compressed_hash.update(block)
                self.pending = block
            if self.pending:
                limit = min(
                    requested - len(result),
                    self.original_bytes - self.original_count + 1,
                )
                try:
                    plain = self.inflater.decompress(
                        self.pending,
                        limit,
                    )
                except (
                    zlib.error, ValueError, OverflowError,
                ) as error:
                    raise VerificationError(
                        "the callback-evidence gzip archive is invalid",
                    ) from error
                require(
                    not self.inflater.unused_data,
                    "extra gzip members and trailing bytes are forbidden",
                )
                self.pending = self.inflater.unconsumed_tail
                if plain:
                    self.original_count += len(plain)
                    require(
                        self.original_count <= self.original_bytes,
                        "gzip expansion exceeded its frozen safe bound",
                    )
                    self.original_hash.update(plain)
                    result.extend(plain)
                continue
            require(
                self.compressed_count == self.archive_bytes
                and self.inflater.eof
                and not self.inflater.unused_data
                and self.read_block(self.descriptor, 1) == b"",
                "a complete single-member gzip footer is mandatory",
            )
            try:
                tail = self.inflater.flush(CHUNK_BYTES)
            except (zlib.error, ValueError) as error:
                raise VerificationError(
                    "the lossless callback-evidence gzip footer is invalid",
                ) from error
            require(
                not tail
                and self.compressed_hash.hexdigest()
                == self.archive_sha256
                and self.original_count == self.original_bytes
                and self.original_hash.hexdigest()
                == self.original_sha256,
                "a complete lossless report failed its exact size or SHA-256",
            )
            self.finished = True
        return bytes(result)



class StreamingObject:
    """Validate every report field while streaming its authenticated gzip."""

    def __init__(self, stream: Any) -> None:
        self.stream = stream
        self.utf8 = codecs.getincrementaldecoder("utf-8")("strict")
        self.decoder = json.JSONDecoder(
            object_pairs_hook=unique_object,
        )
        self.buffer = ""
        self.position = 0
        self.ended = False

    def fill(self) -> bool:
        if self.ended:
            return False
        block = self.stream.read(CHUNK_BYTES)
        require(
            type(block) is bytes,
            "a streamed complete report emitted non-byte evidence",
        )
        if not block:
            self.buffer += self.utf8.decode(b"", final=True)
            self.ended = True
            return False
        self.buffer += self.utf8.decode(block, final=False)
        return True

    def compact(self) -> None:
        if self.position >= 2 * CHUNK_BYTES:
            self.buffer = self.buffer[self.position:]
            self.position = 0

    def peek(self) -> str | None:
        while self.position == len(self.buffer) and self.fill():
            pass
        if self.position < len(self.buffer):
            return self.buffer[self.position]
        return None

    def take(self) -> str:
        value = self.peek()
        require(
            value is not None,
            "the complete callback-evidence report was truncated",
        )
        self.position += 1
        return value

    def whitespace(self) -> None:
        while self.peek() in (" ", "\t", "\r", "\n"):
            self.position += 1
            self.compact()

    def literal(self, expected: str) -> None:
        self.whitespace()
        require(
            self.take() == expected,
            "an authenticated report delimiter was substituted",
        )

    def value(self) -> Any:
        self.whitespace()
        self.compact()
        while True:
            try:
                result, ending = self.decoder.raw_decode(
                    self.buffer,
                    self.position,
                )
            except json.JSONDecodeError as error:
                require(
                    not self.ended,
                    "a complete streamed JSON value was clipped",
                )
                require(
                    len(self.buffer) - self.position
                    <= MAX_SELECTED_VALUE_BYTES,
                    "a complete streamed worker exceeds its safe bound",
                )
                if not self.fill():
                    raise VerificationError(
                        "a complete streamed JSON value is missing",
                    ) from error
                continue
            self.position = ending
            return result

    def skip(self) -> None:
        self.whitespace()
        first = self.peek()
        require(
            first is not None,
            "a complete report value was truncated",
        )
        if first == '"':
            self.take()
            escaped = False
            while True:
                item = self.take()
                if escaped:
                    escaped = False
                elif item == "\\":
                    escaped = True
                elif item == '"':
                    return
                self.compact()
        elif first in ("{", "["):
            stack: list[str] = []
            quoted = False
            escaped = False
            while True:
                item = self.take()
                if quoted:
                    if escaped:
                        escaped = False
                    elif item == "\\":
                        escaped = True
                    elif item == '"':
                        quoted = False
                elif item == '"':
                    quoted = True
                elif item in ("{", "["):
                    stack.append("}" if item == "{" else "]")
                elif item in ("}", "]"):
                    require(
                        bool(stack) and stack[-1] == item,
                        "an unselected complete JSON container is invalid",
                    )
                    stack.pop()
                    if not stack:
                        return
                self.compact()
        else:
            beginning = self.position
            while True:
                item = self.peek()
                if item is None or item in (
                    ",", "}", "]", " ", "\t", "\r", "\n",
                ):
                    break
                self.position += 1
            raw = self.buffer[beginning:self.position]
            try:
                _, ending = self.decoder.raw_decode(raw)
            except json.JSONDecodeError as error:
                raise VerificationError(
                    "an unselected complete JSON scalar was forged",
                ) from error
            require(
                ending == len(raw),
                "an unselected complete JSON scalar was corrupted",
            )

    def select(self, fields: frozenset[str]) -> dict[str, Any]:
        require(
            type(fields) is frozenset and bool(fields),
            "an exact complete streamed evidence schema is mandatory",
        )
        self.literal("{")
        found: set[str] = set()
        result: dict[str, Any] = {}
        self.whitespace()
        if self.peek() == "}":
            self.take()
        else:
            while True:
                key = self.value()
                require(
                    type(key) is str and key not in found,
                    "a complete report field was duplicated",
                )
                found.add(key)
                self.literal(":")
                if key in fields:
                    result[key] = self.value()
                else:
                    self.skip()
                self.whitespace()
                ending = self.take()
                if ending == "}":
                    break
                require(
                    ending == ",",
                    "a complete report separator was substituted",
                )
        self.whitespace()
        require(
            self.peek() is None
            and fields.issubset(found)
            and set(result) == fields,
            "a required pinned complete report field was omitted or concealed",
        )
        return result




BASELINE_FIELDS = frozenset(
    {
        "schema",
        "status",
        "python",
        "label",
        "case_count",
        "cohort_count",
        "variants_per_cohort",
        "matrix_sha256",
        "published_seed",
        "oracle_relative",
        "oracle_source_sha256",
        "recorder_relative",
        "recorder_source_sha256",
        "original_v5_relative",
        "original_v5_sha256",
        "ownership_audit_relative",
        "ownership_audit_sha256",
        "baseline_records_sha256",
        "baseline_reference_pids",
        "actual_reference_workers",
        "actual_candidate_workers",
        "actual_candidate_imports",
        "actual_baseline_controller_invocations",
        "actual_baseline_process_returncode",
        "actual_baseline_process_signal",
        "actual_baseline_process_spawn_error",
        "actual_baseline_process_timed_out",
        "complete_baseline_process_stdout",
        "complete_baseline_process_stderr",
        "clock_samples",
        "timing_trials_run",
        "benchmark_files_read",
        "hidden_cases_read",
        "performance",
        "candidate_qualified_for_hidden_benchmark",
        "final_winner_selected",
        "source_closure_before",
        "source_closure_after",
        "source_closure_unchanged",
        "validated_reference_a_case_count",
        "validated_reference_b_case_count",
    }
)
CANDIDATE_FIELDS = frozenset(
    {
        "schema",
        "status",
        "python",
        "label",
        "candidate_family",
        "case_count",
        "cohort_count",
        "variants_per_cohort",
        "matrix_sha256",
        "published_seed",
        "oracle_relative",
        "oracle_source_sha256",
        "recorder_relative",
        "recorder_source_sha256",
        "original_v5_relative",
        "original_v5_sha256",
        "ownership_audit_relative",
        "ownership_audit_sha256",
        "baseline_archive_relative",
        "baseline_archive_sha256",
        "baseline_receipt_relative",
        "baseline_receipt_sha256",
        "baseline_records_sha256",
        "baseline_reference_pids",
        "candidate_source_sha256",
        "native_bridge_sha256",
        "native_engine_sha256",
        "candidate_owner_before",
        "candidate_owner_after",
        "candidate_owner_unchanged",
        "candidate_records_sha256",
        "actual_candidate_pid",
        "actual_candidate_process_invocations",
        "actual_candidate_process_returncode",
        "actual_candidate_process_signal",
        "actual_candidate_process_spawn_error",
        "actual_candidate_process_timed_out",
        "actual_reference_workers",
        "actual_candidate_workers",
        "actual_candidate_imports",
        "validated_prior_reference_workers",
        "actual_method_guard_checks",
        "actual_warning_registry_guard_checks",
        "complete_candidate_process_stdout",
        "complete_candidate_process_stderr",
        "failure_count",
        "all_failure_reasons",
        "mismatch_count",
        "all_mismatches",
        "all_mismatches_preserved",
        "mismatches_by_api",
        "mismatches_by_cohort",
        "clock_samples",
        "timing_trials_run",
        "benchmark_files_read",
        "hidden_cases_read",
        "performance",
        "candidate_qualified_for_hidden_benchmark",
        "final_winner_selected",
        "validated_baseline_record_count",
        "validated_candidate_record_count",
    }
)


def read_archive(pin: ArchivePin, fields: frozenset[str]) -> dict[str, Any]:
    require(
        pin.relative in APPROVED_FILES
        and type(pin.compressed_bytes) is int
        and 0 < pin.compressed_bytes <= MAX_ARCHIVE_BYTES
        and type(pin.report_bytes) is int
        and 0 < pin.report_bytes <= MAX_UNCOMPRESSED_BYTES,
        "a complete immutable bounded archive pin is mandatory",
    )
    with open_owned(pin.relative, MAX_ARCHIVE_BYTES) as (descriptor, owner):
        require(
            owner.st_size == pin.compressed_bytes,
            "the complete compressed archive has the wrong exact size",
        )
        reader = VerifiedGzipReader(
            descriptor,
            pin.compressed_bytes,
            pin.sha256,
            pin.report_bytes,
            pin.report_sha256,
        )
        result = StreamingObject(reader).select(fields)
        require(reader.finished, "the complete authenticated archive was not consumed")
        return result


def decode_envelope(value: Any, label: str, *, allow_empty: bool = False) -> bytes:
    require(
        type(value) is dict
        and set(value) == {"base64", "bytes", "complete", "sha256"}
        and value.get("complete") is True
        and type(value.get("base64")) is str
        and type(value.get("bytes")) is int
        and 0 <= value["bytes"] <= MAX_PROCESS_BYTES
        and len(value["base64"]) <= MAX_ENCODED_PROCESS_STREAM_BYTES,
        "a complete bounded authenticated worker stream is mandatory: " + label,
    )
    if not allow_empty:
        require(value["bytes"] > 0, "a mandatory isolated worker stream was empty")
    checked_digest(value["sha256"], label)
    try:
        encoded = value["base64"].encode("ascii")
        raw = base64.b64decode(encoded, validate=True)
    except (binascii.Error, UnicodeError, ValueError) as error:
        raise VerificationError("a complete strict base64 worker was forged: " + label) from error
    require(
        len(raw) == value["bytes"]
        and hashlib.sha256(raw).hexdigest() == value["sha256"]
        and base64.b64encode(raw) == encoded,
        "a complete worker stream failed exact canonical base64, size, or SHA-256",
    )
    return raw


def require_empty_stream(value: Any, label: str) -> None:
    require(
        decode_envelope(value, label, allow_empty=True) == b""
        and value.get("bytes") == 0
        and value.get("base64") == ""
        and value.get("sha256") == EMPTY_SHA256,
        "a historical worker stderr was concealed or changed: " + label,
    )


def assert_no_measurements(value: Mapping[str, Any], label: str) -> None:
    require(
        all(value.get(name) == 0 for name in (
            "clock_samples",
            "timing_trials_run",
            "benchmark_files_read",
            "hidden_cases_read",
        ))
        and value.get("performance") == "NOT MEASURED"
        and value.get("candidate_qualified_for_hidden_benchmark") is False
        and value.get("final_winner_selected") is False,
        "a correctness-only observation sampled time, benchmarks, or hidden data: " + label,
    )


def validate_common(
    value: Mapping[str, Any],
    suite: SuitePin,
    label: str,
    *,
    candidate: bool,
) -> None:
    require(
        type(value) is dict
        and value.get("python") == "3.14.6"
        and value.get("case_count") == suite.case_count
        and value.get("cohort_count") == 64
        and value.get("variants_per_cohort") == suite.variants_per_cohort
        and value.get("matrix_sha256") == suite.matrix_sha256
        and value.get("published_seed") == suite.seed
        and value.get("oracle_source_sha256") == suite.oracle_sha256
        and value.get("recorder_source_sha256") == suite.recorder_sha256
        and value.get("original_v5_sha256") == V5_SHA256
        and value.get("ownership_audit_sha256") == AUDIT_SHA256
        and value.get("baseline_records_sha256") == suite.baseline_records_sha256
        and value.get("baseline_reference_pids") == [82, 83],
        "a frozen V1 source, seed, matrix, baseline, owner, or Python changed: " + label,
    )
    if "oracle_relative" in value:
        require(value["oracle_relative"] == suite.oracle_relative, "the V1 oracle path was aliased")
    if "recorder_relative" in value:
        require(
            value["recorder_relative"] == suite.recorder_relative,
            "the frozen historical recorder path was aliased",
        )
    if "original_v5_relative" in value:
        require(value["original_v5_relative"] == V5_RELATIVE, "the frozen V5 owner was aliased")
    if "ownership_audit_relative" in value:
        require(value["ownership_audit_relative"] == AUDIT_RELATIVE, "the policy audit was aliased")
    assert_no_measurements(value, label)
    if candidate:
        require(
            value.get("actual_reference_workers") == 0
            and value.get("actual_candidate_workers") == 1
            and value.get("actual_candidate_imports") == 3
            and value.get("validated_prior_reference_workers") == 2,
            "the exact historical candidate-only process provenance changed",
        )
    else:
        require(
            value.get("actual_reference_workers") == 2
            and value.get("actual_candidate_workers") == 0
            and value.get("actual_candidate_imports") == 0,
            "the exact independently isolated two-reference provenance changed",
        )


def validate_receipt(pin: ArchivePin, suite: SuitePin, candidate: CandidatePin | None) -> dict[str, Any]:
    raw = read_frozen(pin.receipt_relative, pin.receipt_sha256, MAX_RECEIPT_BYTES)
    receipt = decode_document(raw, MAX_RECEIPT_BYTES, pin.receipt_relative)
    role = "candidate" if candidate is not None else "baseline"
    expected_schema = (
        "rebar-independent-"
        + suite.name
        + "-recorder-"
        + ("v2" if suite is SUBSTITUTION else "v1")
        + "-durable-"
        + role
        + "-publication-receipt"
    )
    require(
        receipt.get("schema") == expected_schema
        and receipt.get("status") == "PASS"
        and receipt.get("report_relative") == pin.relative
        and receipt.get("report_bytes") == pin.compressed_bytes
        and receipt.get("report_sha256") == pin.sha256
        and receipt.get("report_uncompressed_bytes") == pin.report_bytes
        and receipt.get("report_uncompressed_sha256") == pin.report_sha256
        and receipt.get("report_compression") == "gzip-mtime-zero-level-9"
        and receipt.get("receipt_relative") == pin.receipt_relative
        and receipt.get("report_complete_readback_verified") is True
        and receipt.get("report_file_fsync_completed") is True
        and receipt.get("report_directory_fsync_completed") is True
        and receipt.get("report_atomic_no_overwrite_link") is True,
        "a signed complete durable publication receipt was substituted",
    )
    validate_common(receipt, suite, role + " receipt", candidate=candidate is not None)
    if candidate is None:
        require(
            receipt.get("baseline_result_status") == "PASS"
            and receipt.get("validated_reference_a_case_count") == suite.case_count
            and receipt.get("validated_reference_b_case_count") == suite.case_count
            and receipt.get("label") == "shared-suite-v1",
            "the signed two-reference baseline receipt did not genuinely pass",
        )
        if suite is SUBSTITUTION:
            require(
                receipt.get("previous_recorder_relative") == suite.previous_recorder_relative
                and receipt.get("previous_recorder_sha256") == suite.previous_recorder_sha256,
                "the signed previous replacement recorder provenance changed",
            )
    else:
        require(
            receipt.get("candidate_result_status") == "FAIL"
            and receipt.get("candidate_family") == candidate.family
            and receipt.get("label") == candidate.label
            and receipt.get("baseline_archive_relative") == suite.baseline.relative
            and receipt.get("baseline_archive_sha256") == suite.baseline.sha256
            and receipt.get("baseline_receipt_relative") == suite.baseline.receipt_relative
            and receipt.get("baseline_receipt_sha256") == suite.baseline.receipt_sha256
            and receipt.get("candidate_records_sha256") == candidate.records_sha256
            and receipt.get("candidate_source_sha256") == candidate.candidate_source_sha256
            and receipt.get("native_bridge_sha256") == candidate.native_bridge_sha256
            and receipt.get("native_engine_sha256") == candidate.native_engine_sha256
            and receipt.get("mismatch_count") == candidate.mismatch_count
            and receipt.get("all_mismatches_preserved") is True
            and receipt.get("validated_baseline_record_count") == suite.case_count
            and receipt.get("validated_candidate_record_count") == suite.case_count
            and receipt.get("actual_candidate_process_invocations") == 1
            and receipt.get("actual_method_guard_checks") == 2 * suite.case_count
            and receipt.get("actual_warning_registry_guard_checks") == 2 * suite.case_count
            and receipt.get("candidate_owner_unchanged") is True
            and type(receipt.get("candidate_owner_before")) is dict
            and receipt["candidate_owner_before"] == receipt.get("candidate_owner_after"),
            "a failed historical candidate, complete signed ledger, or owner was misrepresented",
        )
        if suite is SUBSTITUTION:
            require(
                receipt.get("mismatch_evidence_sha256") == candidate.full_ledger_sha256
                and receipt.get("previous_recorder_relative") == suite.previous_recorder_relative
                and receipt.get("previous_recorder_sha256") == suite.previous_recorder_sha256,
                "the full signed replacement mismatch ledger or old recorder was changed",
            )
    return receipt


def expected_reference_guard(suite: SuitePin) -> dict[str, Any]:
    return {
        "candidate_import_count": 0,
        "external_regex_import_count": 0,
        "actual_method_guard_checks": 2 * suite.case_count,
        "required_method_guard_checks": 2 * suite.case_count,
        "future_candidate_guard_relative": V5_RELATIVE,
        "future_candidate_guard_sha256": V5_SHA256,
        "future_ownership_audit_relative": AUDIT_RELATIVE,
        "future_ownership_audit_sha256": AUDIT_SHA256,
        "future_candidate_guard_installed": False,
    }


def validate_reference_source_owners(owners: Any, suite: SuitePin) -> None:
    require(type(owners) is dict, "the complete historical reference source closure is mandatory")
    expected = {
        "oracle": (ROOT + "/" + suite.oracle_relative, suite.oracle_sha256),
        "python": (PINNED_PYTHON, PINNED_PYTHON_SHA256),
        "v5_guard": (ROOT + "/" + V5_RELATIVE, V5_SHA256),
        "ownership_audit": (ROOT + "/" + AUDIT_RELATIVE, AUDIT_SHA256),
    }
    expected.update(
        {
            name: (PINNED_STDLIB_DIRECTORY + filename, source_sha256)
            for name, (filename, source_sha256) in PINNED_STDLIB_SOURCES.items()
        }
    )
    require(
        set(owners) == set(expected),
        "a complete pinned stable CPython reference source owner was omitted or injected",
    )
    for name, (path, sha256) in expected.items():
        owner = owners.get(name)
        require(
            type(owner) is dict
            and set(owner) == {"path", "sha256", "bytes", "device", "inode"}
            and owner.get("path") == path
            and owner.get("sha256") == sha256
            and type(owner.get("bytes")) is int
            and owner["bytes"] > 0
            and type(owner.get("device")) is int
            and owner["device"] >= 0
            and type(owner.get("inode")) is int
            and owner["inode"] > 0,
            "a historical isolated reference source owner was forged: " + name,
        )


def validate_worker_common(worker: Mapping[str, Any], suite: SuitePin) -> None:
    require(
        worker.get("python") == "3.14.6"
        and worker.get("case_count") == suite.case_count
        and worker.get("cohort_count") == 64
        and worker.get("variants_per_cohort") == suite.variants_per_cohort
        and worker.get("matrix_sha256") == suite.matrix_sha256
        and worker.get("published_seed") == suite.seed
        and worker.get("oracle_source_sha256") == suite.oracle_sha256,
        "a complete isolated worker changed the frozen source, matrix, or seed",
    )
    assert_no_measurements(worker, "complete historical isolated worker")
    require(
        worker.get("workspace_files_written") == 0
        and worker.get("evidence_files_created") == 0,
        "a historically correctness-only worker wrote extra evidence",
    )


def validate_record_rows(records: Any, suite: SuitePin, expected_digest: str) -> list[dict[str, Any]]:
    require(
        type(records) is list
        and len(records) == suite.case_count
        and digest(records) == expected_digest,
        "the complete source-ordered candidate or reference outcome vector was changed",
    )
    prefix = suite.name + ".v1."
    required = {"case", "cohort", "api", "outcome"}
    if suite is SHAPE:
        required |= {"outer_size", "nested_size"}
    for index, row in enumerate(records):
        require(
            type(row) is dict
            and set(row) == required
            and row.get("case") == prefix + str(index).zfill(5)
            and type(row.get("cohort")) is str
            and bool(row["cohort"])
            and row.get("api") in APIS + ("match.expand",)
            and type(row.get("outcome")) is dict,
            "an exact source-ordered observation was omitted, aliased, or relabeled",
        )
        if suite is SHAPE:
            require(
                type(row.get("outer_size")) is int
                and type(row.get("nested_size")) is int
                and row["outer_size"] >= 0
                and row["nested_size"] >= 0,
                "an exact visible outer or nested buffer size was forged",
            )
    return records


def validate_reference_worker(
    worker: Any,
    process: Any,
    suite: SuitePin,
    role: str,
    pid: int,
) -> list[dict[str, Any]]:
    require(
        type(worker) is dict
        and worker.get("schema")
        == "rebar-independent-" + suite.name + "-v1-isolated-reference-worker"
        and worker.get("status") == "OBSERVED"
        and worker.get("role") == role
        and worker.get("pid") == pid
        and worker.get("actual_reference_workers") == 1
        and worker.get("actual_candidate_workers") == 0
        and worker.get("actual_candidate_imports") == 0
        and worker.get("reference_guard") == expected_reference_guard(suite)
        and worker.get("records_sha256") == suite.baseline_records_sha256,
        "a genuine independent complete reference process was forged",
    )
    validate_worker_common(worker, suite)
    validate_reference_source_owners(worker.get("source_owners"), suite)
    require(
        type(process) is dict
        and set(process) == {"role", "pid", "returncode", "stdout", "stderr"}
        and process.get("role") == role
        and process.get("pid") == pid
        and process.get("returncode") == 0,
        "an isolated reference process role, PID, or return code changed",
    )
    raw_worker = decode_envelope(process.get("stdout"), role + " complete stdout")
    require(
        decode_document(raw_worker, MAX_PROCESS_BYTES, role + " complete worker") == worker,
        "the preserved full reference stdout does not equal the declared worker",
    )
    require_empty_stream(process.get("stderr"), role + " complete stderr")
    return validate_record_rows(worker["records"], suite, suite.baseline_records_sha256)


def verify_baseline(suite: SuitePin) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    receipt = validate_receipt(suite.baseline, suite, None)
    report = read_archive(suite.baseline, BASELINE_FIELDS)
    require(
        report.get("schema")
        == (
            "rebar-independent-"
            + suite.name
            + "-recorder-"
            + ("v2" if suite is SUBSTITUTION else "v1")
            + "-complete-baseline-report"
        )
        and report.get("status") == "PASS"
        and report.get("label") == "shared-suite-v1"
        and report.get("actual_baseline_controller_invocations") == 1
        and report.get("actual_baseline_process_returncode") == 0
        and report.get("actual_baseline_process_signal") is None
        and report.get("actual_baseline_process_spawn_error") is None
        and report.get("actual_baseline_process_timed_out") is False
        and report.get("source_closure_unchanged") is True
        and type(report.get("source_closure_before")) is dict
        and report["source_closure_before"] == report.get("source_closure_after")
        and report.get("validated_reference_a_case_count") == suite.case_count
        and report.get("validated_reference_b_case_count") == suite.case_count,
        "the complete signed baseline report did not pass with two genuine references",
    )
    validate_common(report, suite, "complete baseline report", candidate=False)
    require_empty_stream(report["complete_baseline_process_stderr"], "baseline controller stderr")
    controller_raw = decode_envelope(
        report["complete_baseline_process_stdout"],
        "complete historical two-reference controller",
    )
    controller = decode_document(
        controller_raw,
        MAX_PROCESS_BYTES,
        "complete historical two-reference controller",
    )
    require(
        controller.get("schema") == "rebar-independent-" + suite.name + "-v1-two-reference-baseline"
        and controller.get("status") == "PASS"
        and controller.get("python") == "3.14.6"
        and controller.get("case_count") == suite.case_count
        and controller.get("cohort_count") == 64
        and controller.get("variants_per_cohort") == suite.variants_per_cohort
        and controller.get("matrix_sha256") == suite.matrix_sha256
        and controller.get("published_seed") == suite.seed
        and controller.get("oracle_source_sha256") == suite.oracle_sha256
        and controller.get("baseline_records_sha256") == suite.baseline_records_sha256
        and controller.get("actual_reference_workers") == 2
        and controller.get("actual_candidate_workers") == 0
        and controller.get("actual_candidate_imports") == 0
        and controller.get("workspace_files_written") == 0
        and controller.get("evidence_files_created") == 0,
        "the full independently isolated historical two-reference controller was forged",
    )
    assert_no_measurements(controller, "complete isolated two-reference controller")
    validate_reference_source_owners(controller.get("source_owners"), suite)
    first = validate_reference_worker(
        controller.get("reference_a"),
        controller.get("reference_a_process"),
        suite,
        "reference_a",
        82,
    )
    second = validate_reference_worker(
        controller.get("reference_b"),
        controller.get("reference_b_process"),
        suite,
        "reference_b",
        83,
    )
    require(
        first == second
        and digest(first) == receipt["baseline_records_sha256"],
        "the two independent full reference streams disagree or were truncated",
    )
    return first, receipt


def validate_candidate_guard(value: Any, candidate: CandidatePin) -> None:
    suite = candidate.suite
    require(type(value) is dict, "a complete genuine candidate ownership guard is mandatory")
    for name in GUARD_TRUE_FIELDS:
        require(value.get(name) is True, "a native no-delegation guard was omitted: " + name)
    require(
        value.get("public_type_names_used_for_ownership") is False
        and value.get("actual_method_guard_checks") == 2 * suite.case_count
        and value.get("actual_warning_registry_guard_checks") == 2 * suite.case_count,
        "the independently owned exact per-case ownership guard changed",
    )
    owned = candidate.family == "zig"
    for name in (
        "owned_native_ffi_allowed",
        "trusted_stdlib_ctypes_preloaded",
        "trusted_stdlib_ctypes_builtin_verified",
        "trusted_stdlib_ctypes_pythonapi_initialized",
    ):
        require(value.get(name) is owned, "the exact independently owned FFI policy changed: " + name)
    require(
        value.get("trusted_stdlib_ctypes_source_sha256")
        == (TRUSTED_CTYPES_SHA256 if owned else None),
        "the frozen trusted standard FFI owner was replaced",
    )
    for name in GUARD_COUNTER_FIELDS:
        require(
            type(value.get(name)) is int and value[name] >= 0,
            "a continuous no-delegation guard counter was concealed: " + name,
        )
    if owned:
        require(
            value["owned_ctypes_load_count"] >= 1
            and value["owned_ctypes_symbol_count"] >= 1,
            "the signed independently owned Zig native engine was not loaded",
        )
    else:
        require(
            value["owned_ctypes_load_count"] == 0
            and value["owned_ctypes_symbol_count"] == 0,
            "an unowned native FFI was used by the C candidate",
        )


def validate_candidate_manifest(worker: Mapping[str, Any], candidate: CandidatePin) -> None:
    manifest = worker.get("audit_manifest")
    require(
        type(manifest) is dict
        and manifest.get("family") == candidate.family
        and manifest.get("candidate_source_sha256") == candidate.candidate_source_sha256
        and manifest.get("native_bridge_sha256") == candidate.native_bridge_sha256
        and manifest.get("native_engine_sha256") == candidate.native_engine_sha256
        and manifest.get("immutable_policy_sha256")
        == {POLICY_RELATIVE: POLICY_SHA256, V5_RELATIVE: V5_SHA256}
        and type(manifest.get("native_sha256")) is dict
        and type(manifest.get("source_sha256")) is dict,
        "the frozen independently authored candidate ownership manifest was forged",
    )
    native = worker.get("native_provenance")
    require(type(native) is dict, "the complete immutable native provenance is mandatory")
    expected = {
        "source": candidate.candidate_source_sha256,
        "native_bridge": candidate.native_bridge_sha256,
        "native_engine": candidate.native_engine_sha256,
    }
    for role, expected_sha in expected.items():
        owner = native.get(role)
        require(
            type(owner) is dict
            and owner.get("sha256") == expected_sha
            and type(owner.get("relative")) is str
            and owner["relative"].startswith("candidates/")
            and type(owner.get("bytes")) is int
            and owner["bytes"] > 0,
            "a recorded native candidate provenance owner was changed: " + role,
        )


def validate_candidate_worker(worker: Any, candidate: CandidatePin) -> list[dict[str, Any]]:
    suite = candidate.suite
    require(
        type(worker) is dict
        and worker.get("schema")
        == (
            "rebar-independent-"
            + suite.name
            + "-recorder-"
            + ("v2" if suite is SUBSTITUTION else "v1")
            + "-isolated-candidate-worker"
        )
        and worker.get("status") == "OBSERVED"
        and worker.get("role") == "candidate-" + candidate.family
        and worker.get("pid") == 81
        and worker.get("label") == "shared-suite-v1"
        and worker.get("candidate_family") == candidate.family
        and worker.get("actual_reference_workers") == 0
        and worker.get("actual_candidate_workers") == 1
        and worker.get("actual_candidate_imports") == 3
        and worker.get("validated_prior_reference_workers") == 2
        and worker.get("baseline_records_sha256") == suite.baseline_records_sha256
        and worker.get("baseline_reference_pids") == [82, 83]
        and worker.get("baseline_archive_relative") == suite.baseline.relative
        and worker.get("baseline_archive_sha256") == suite.baseline.sha256
        and worker.get("baseline_receipt_relative") == suite.baseline.receipt_relative
        and worker.get("baseline_receipt_sha256") == suite.baseline.receipt_sha256
        and worker.get("records_sha256") == candidate.records_sha256,
        "the historical single candidate worker or validated baseline provenance changed",
    )
    validate_worker_common(worker, suite)
    validate_candidate_guard(worker.get("matcher_guard"), candidate)
    validate_candidate_manifest(worker, candidate)
    provenance = worker.get("source_provenance")
    require(type(provenance) is dict, "the complete isolated candidate source closure is mandatory")
    source_roles = {
        "from_scratch_audit_v3": (AUDIT_RELATIVE, AUDIT_SHA256),
        "original_v5": (V5_RELATIVE, V5_SHA256),
        "recorder": (suite.recorder_relative, suite.recorder_sha256),
    }
    oracle_role = "substitution_oracle" if suite is SUBSTITUTION else "shape_oracle"
    source_roles[oracle_role] = (suite.oracle_relative, suite.oracle_sha256)
    if suite is SUBSTITUTION:
        require(
            suite.previous_recorder_relative is not None
            and suite.previous_recorder_sha256 is not None,
            "a frozen previous replacement recorder is mandatory",
        )
        source_roles["previous_recorder"] = (
            suite.previous_recorder_relative,
            suite.previous_recorder_sha256,
        )
    for name, (relative, sha256) in source_roles.items():
        owner = provenance.get(name)
        require(
            type(owner) is dict
            and owner.get("relative") == relative
            and owner.get("sha256") == sha256
            and type(owner.get("bytes")) is int
            and owner["bytes"] > 0,
            "a historical candidate source closure entry was replaced: " + name,
        )
    return validate_record_rows(worker["records"], suite, candidate.records_sha256)


def owned_callback_artifact(
    baseline: Any,
    candidate: Any,
    suite: SuitePin,
    *,
    api: str,
    cohort: str,
    target: str | None = None,
) -> bool:
    if (
        type(baseline) is not dict
        or type(candidate) is not dict
        or set(baseline) != set(candidate)
        or baseline.get("status") != "raise"
        or candidate.get("status") != "raise"
        or api not in APIS
        or baseline.get("stage") != api
        or candidate.get("stage") != api
    ):
        return False
    if suite is SUBSTITUTION:
        if cohort not in ("text-callback-error", "bytes-callback-error") or target is not None:
            return False
    elif target != "callback-error":
        return False
    expected = baseline.get("exception")
    observed = candidate.get("exception")
    fields = {"kind", "type", "module", "message", "args"}
    expected_args = {
        "type": "tuple",
        "items": [{"type": "str", "value": suite.callback_message}],
    }
    if (
        type(expected) is not dict
        or type(observed) is not dict
        or set(expected) != fields
        or set(observed) != fields
        or expected.get("kind") != "ordinary-python-error"
        or observed.get("kind") != "ordinary-python-error"
        or expected.get("type") != suite.callback_class
        or observed.get("type") != suite.callback_class
        or expected.get("message") != suite.callback_message
        or observed.get("message") != suite.callback_message
        or expected.get("args") != expected_args
        or observed.get("args") != expected_args
        or expected.get("module") != "__main__"
        or observed.get("module") != suite.callback_module
        or {key: value for key, value in baseline.items() if key != "exception"}
        != {key: value for key, value in candidate.items() if key != "exception"}
    ):
        return False
    callbacks = baseline.get("callbacks")
    if (
        type(callbacks) is not list
        or len(callbacks) != 1
        or type(callbacks[0]) is not dict
        or callbacks[0].get("event") != "callback"
        or callbacks[0].get("index") != 0
        or callbacks[0].get("raises") is not True
        or type(callbacks[0].get("match")) is not dict
        or callbacks[0]["match"].get("pattern_is_expected") is not True
        or callbacks[0]["match"].get("string_is_subject") is not True
        or type(baseline.get("events")) is not list
        or sum(event == callbacks[0] for event in baseline["events"]) != 1
        or type(baseline.get("warnings")) is not list
    ):
        return False
    return True


def reconstruct_substitution_mismatch(
    index: int,
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "index": index,
        "case": baseline["case"],
        "cohort": baseline["cohort"],
        "api": baseline["api"],
        "baseline_outcome_sha256": digest(baseline["outcome"]),
        "candidate_outcome_sha256": digest(candidate["outcome"]),
    }


def validate_shape_mismatch(
    entry: Any,
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    suite: SuitePin,
) -> tuple[str, str]:
    require(
        type(entry) is dict
        and set(entry)
        == {
            "case",
            "cohort",
            "api",
            "outer_size",
            "nested_size",
            "target",
            "behavior",
            "input",
            "baseline_outcome",
            "candidate_outcome",
        }
        and entry.get("case") == baseline["case"]
        and entry.get("cohort") == baseline["cohort"]
        and entry.get("api") == baseline["api"]
        and entry.get("outer_size") == baseline["outer_size"]
        and entry.get("nested_size") == baseline["nested_size"]
        and entry.get("baseline_outcome") == baseline["outcome"]
        and entry.get("candidate_outcome") == candidate["outcome"]
        and type(entry.get("input")) is dict,
        "a complete genuine source-ordered shape mismatch or visible outcome was changed",
    )
    case = entry["input"]
    require(
        case.get("case") == entry["case"]
        and case.get("cohort") == entry["cohort"]
        and case.get("api") == entry["api"]
        and case.get("outer_size") == entry["outer_size"]
        and case.get("nested_size") == entry["nested_size"]
        and case.get("target") == entry["target"]
        and case.get("behavior") == entry["behavior"]
        and case.get("seed") == suite.seed
        and type(case.get("variant")) is int
        and 0 <= case["variant"] < suite.variants_per_cohort,
        "the complete frozen shape case, seed, target, or behavior was substituted",
    )
    return entry["target"], entry["behavior"]


def verify_candidate(
    candidate: CandidatePin,
    baseline: list[dict[str, Any]],
    baseline_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    suite = candidate.suite
    receipt = validate_receipt(candidate.archive, suite, candidate)
    fields = CANDIDATE_FIELDS | (
        frozenset({"mismatch_evidence_sha256"})
        if suite is SUBSTITUTION
        else frozenset({"matcher_guard", "mismatches_by_behavior", "mismatches_by_target"})
    )
    report = read_archive(candidate.archive, fields)
    require(
        report.get("schema")
        == (
            "rebar-independent-"
            + suite.name
            + "-recorder-"
            + ("v2" if suite is SUBSTITUTION else "v1")
            + "-complete-candidate-report"
        )
        and report.get("status") == "FAIL"
        and report.get("candidate_family") == candidate.family
        and report.get("label") == candidate.label
        and report.get("baseline_archive_relative") == suite.baseline.relative
        and report.get("baseline_archive_sha256") == suite.baseline.sha256
        and report.get("baseline_receipt_relative") == suite.baseline.receipt_relative
        and report.get("baseline_receipt_sha256") == suite.baseline.receipt_sha256
        and baseline_receipt.get("baseline_records_sha256") == suite.baseline_records_sha256
        and report.get("candidate_records_sha256") == candidate.records_sha256
        and report.get("candidate_source_sha256") == candidate.candidate_source_sha256
        and report.get("native_bridge_sha256") == candidate.native_bridge_sha256
        and report.get("native_engine_sha256") == candidate.native_engine_sha256
        and report.get("actual_candidate_pid") == 81
        and report.get("actual_candidate_process_invocations") == 1
        and report.get("actual_candidate_process_returncode") == 0
        and report.get("actual_candidate_process_signal") is None
        and report.get("actual_candidate_process_spawn_error") is None
        and report.get("actual_candidate_process_timed_out") is False
        and report.get("actual_method_guard_checks") == 2 * suite.case_count
        and report.get("actual_warning_registry_guard_checks") == 2 * suite.case_count
        and report.get("candidate_owner_unchanged") is True
        and type(report.get("candidate_owner_before")) is dict
        and report["candidate_owner_before"] == report.get("candidate_owner_after")
        and report.get("validated_baseline_record_count") == suite.case_count
        and report.get("validated_candidate_record_count") == suite.case_count
        and report.get("mismatch_count") == candidate.mismatch_count
        and report.get("all_mismatches_preserved") is True
        and report.get("failure_count") == 1
        and type(report.get("all_failure_reasons")) is list,
        "a complete failed signed candidate report or process provenance was replaced",
    )
    validate_common(report, suite, "complete historical candidate report", candidate=True)
    if suite is SUBSTITUTION:
        require(
            report.get("mismatch_evidence_sha256") == candidate.full_ledger_sha256,
            "the full frozen replacement mismatch ledger was replaced",
        )
    else:
        validate_candidate_guard(report.get("matcher_guard"), candidate)
    require_empty_stream(report["complete_candidate_process_stderr"], "candidate process stderr")
    candidate_raw = decode_envelope(
        report["complete_candidate_process_stdout"],
        "complete historical candidate worker",
    )
    worker = decode_document(
        candidate_raw,
        MAX_PROCESS_BYTES,
        "complete historical candidate worker",
    )
    records = validate_candidate_worker(worker, candidate)
    original_ledger = report["all_mismatches"]
    require(
        type(original_ledger) is list
        and len(original_ledger) == candidate.mismatch_count
        and digest(original_ledger) == candidate.full_ledger_sha256,
        "the complete original signed source-ordered mismatch ledger was forged",
    )
    artifacts: list[dict[str, Any]] = []
    genuine: list[dict[str, Any]] = []
    reconstructed: list[dict[str, Any]] = []
    artifact_by_api: collections.Counter[str] = collections.Counter()
    artifact_by_group: collections.Counter[str] = collections.Counter()
    mismatch_by_api: collections.Counter[str] = collections.Counter()
    mismatch_by_cohort: collections.Counter[str] = collections.Counter()
    mismatch_by_target: collections.Counter[str] = collections.Counter()
    mismatch_by_behavior: collections.Counter[str] = collections.Counter()
    next_entry = 0
    for index, (expected, observed) in enumerate(zip(baseline, records, strict=True)):
        metadata = ("case", "cohort", "api")
        require(
            all(expected.get(name) == observed.get(name) for name in metadata)
            and (
                suite is not SHAPE
                or (
                    expected["outer_size"] == observed["outer_size"]
                    and expected["nested_size"] == observed["nested_size"]
                )
            ),
            "a source-ordered genuine candidate case was relabeled",
        )
        if expected["outcome"] == observed["outcome"]:
            continue
        require(next_entry < len(original_ledger), "a full signed mismatch was dropped")
        actual_entry = original_ledger[next_entry]
        if suite is SUBSTITUTION:
            entry = reconstruct_substitution_mismatch(index, expected, observed)
            require(
                type(actual_entry) is dict and actual_entry == entry,
                "a full original replacement mismatch digest or index was replaced",
            )
            target = None
            behavior = None
        else:
            target, behavior = validate_shape_mismatch(
                actual_entry,
                expected,
                observed,
                suite,
            )
            entry = actual_entry
            mismatch_by_target[target] += 1
            mismatch_by_behavior[behavior] += 1
        reconstructed.append(entry)
        mismatch_by_api[expected["api"]] += 1
        mismatch_by_cohort[expected["cohort"]] += 1
        artifact = owned_callback_artifact(
            expected["outcome"],
            observed["outcome"],
            suite,
            api=expected["api"],
            cohort=expected["cohort"],
            target=target,
        )
        if artifact:
            artifacts.append(entry)
            artifact_by_api[expected["api"]] += 1
            artifact_by_group[
                expected["cohort"] if suite is SUBSTITUTION else str(behavior)
            ] += 1
        else:
            genuine.append(entry)
        next_entry += 1
    require(
        next_entry == len(original_ledger)
        and reconstructed == original_ledger
        and digest(reconstructed) == candidate.full_ledger_sha256
        and len(reconstructed) == candidate.mismatch_count
        and len(artifacts) == candidate.artifact_count
        and len(genuine) == candidate.genuine_count
        and len(artifacts) + len(genuine) == len(reconstructed),
        "a full genuine mismatch was dropped or falsely excused as a callback artifact",
    )
    observed_api = {name: mismatch_by_api.get(name, 0) for name in APIS + ("match.expand",)}
    require(
        receipt.get("mismatches_by_api") == observed_api
        and report.get("mismatches_by_api") == observed_api,
        "a signed all-case API mismatch denominator changed",
    )
    signed_cohorts = receipt.get("mismatches_by_cohort")
    require(
        type(signed_cohorts) is dict
        and len(signed_cohorts) == 64
        and all(type(name) is str and bool(name) for name in signed_cohorts)
        and set(mismatch_by_cohort).issubset(signed_cohorts)
        and all(
            type(count) is int and count >= 0
            for count in signed_cohorts.values()
        ),
        "a complete signed 64-cohort mismatch denominator was dropped or forged",
    )
    observed_cohort = {
        name: mismatch_by_cohort.get(name, 0) for name in signed_cohorts
    }
    require(
        receipt.get("mismatches_by_cohort") == observed_cohort
        and report.get("mismatches_by_cohort") == observed_cohort
        and sum(observed_cohort.values()) == candidate.mismatch_count,
        "a signed all-case, all-cohort mismatch denominator changed",
    )
    if suite is SUBSTITUTION:
        require(
            dict(artifact_by_group)
            == {"text-callback-error": 64, "bytes-callback-error": 64}
            and all(artifact_by_api.get(api, 0) == 32 for api in APIS)
            and artifact_by_api.get("match.expand", 0) == 0,
            "the exact four-API text and bytes callback artifact cohort was changed",
        )
    else:
        expected_target = {
            "both-direct": 1_104,
            "both-wrapped": 0,
            "callback-error": 496,
            "callback-return": 0,
            "subject-direct": 0,
            "subject-wrapped": 0,
            "template-direct": 288,
            "template-wrapped": 0,
        }
        expected_behavior = {
            "fail-nested": 256,
            "fail-outer": 256,
            "mutate": 584,
            "stable": 792,
        }
        expected_api = {
            "match.expand": 176,
            "module.sub": 432,
            "module.subn": 416,
            "pattern.sub": 432,
            "pattern.subn": 432,
        }
        observed_target = {name: mismatch_by_target.get(name, 0) for name in expected_target}
        observed_behavior = {
            name: mismatch_by_behavior.get(name, 0) for name in expected_behavior
        }
        require(
            observed_target == expected_target
            and observed_behavior == expected_behavior
            and observed_api == expected_api
            and report.get("mismatches_by_target") == expected_target
            and receipt.get("mismatches_by_target") == expected_target
            and report.get("mismatches_by_behavior") == expected_behavior
            and receipt.get("mismatches_by_behavior") == expected_behavior
            and dict(artifact_by_group) == {"stable": 248, "mutate": 248}
            and dict(artifact_by_api)
            == {
                "module.sub": 128,
                "module.subn": 112,
                "pattern.sub": 128,
                "pattern.subn": 128,
            },
            "the full signed shape, behavior, target, or callback artifact ledger changed",
        )
    return {
        "suite": suite.name + "-v1",
        "candidate_family": candidate.family,
        "candidate_label": candidate.label,
        "candidate_result_status": "FAIL",
        "case_count": suite.case_count,
        "frozen_matrix_sha256": suite.matrix_sha256,
        "frozen_seed": suite.seed,
        "baseline_records_sha256": suite.baseline_records_sha256,
        "candidate_records_sha256": candidate.records_sha256,
        "original_all_mismatches_sha256": candidate.full_ledger_sha256,
        "original_all_mismatches_count": len(reconstructed),
        "owned_callback_module_only_artifact_count": len(artifacts),
        "genuine_visible_mismatch_count": len(genuine),
        "genuine_mismatches_sha256": digest(genuine),
        "owned_callback_artifacts_sha256": digest(artifacts),
        "owned_callback_artifacts_by_api": {
            api: artifact_by_api.get(api, 0) for api in APIS + ("match.expand",)
        },
        "owned_callback_artifacts_by_cohort_or_behavior": dict(
            sorted(artifact_by_group.items())
        ),
        "all_mismatches_by_api": observed_api,
        "historical_reference_processes": 2,
        "historical_candidate_processes": 1,
        "new_reference_processes": 0,
        "new_candidate_processes": 0,
        "regex_matcher_calls": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def verify_runtime(source_sha256: str) -> None:
    checked_digest(source_sha256, "immutable verifier source")
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == PINNED_PYTHON
        and os.path.realpath(sys.executable) == PINNED_PYTHON
        and os.path.abspath(__file__) == ROOT + "/" + SOURCE_RELATIVE
        and os.path.realpath(__file__) == ROOT + "/" + SOURCE_RELATIVE,
        "use the exact pinned isolated Python 3.14.6 and immutable verifier",
    )
    require(
        hashlib.sha256(
            read_frozen(SOURCE_RELATIVE, source_sha256, MAX_SOURCE_BYTES)
        ).hexdigest()
        == source_sha256,
        "the sole-authored frozen verifier source changed",
    )
    regular = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor: int | None = None
    try:
        descriptor = os.open(PINNED_PYTHON, regular)
        before = os.fstat(descriptor)
        named = os.stat(PINNED_PYTHON, follow_symlinks=False)
        require(
            stat.S_ISREG(before.st_mode)
            and (before.st_dev, before.st_ino, before.st_size)
            == (named.st_dev, named.st_ino, named.st_size)
            and 0 < before.st_size <= MAX_UNCOMPRESSED_BYTES,
            "the exact pinned CPython executable owner was substituted",
        )
        hasher = hashlib.sha256()
        count = 0
        while count < before.st_size:
            block = os.read(descriptor, min(CHUNK_BYTES, before.st_size - count))
            require(type(block) is bytes and bool(block), "the pinned Python binary was truncated")
            hasher.update(block)
            count += len(block)
        after = os.fstat(descriptor)
        named_after = os.stat(PINNED_PYTHON, follow_symlinks=False)
        require(
            os.read(descriptor, 1) == b""
            and count == before.st_size
            and hasher.hexdigest() == PINNED_PYTHON_SHA256
            and (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
            == (
                named_after.st_dev,
                named_after.st_ino,
                named_after.st_size,
                named_after.st_mtime_ns,
            ),
            "the exact independently pinned stable CPython binary changed",
        )
    except (OSError, ValueError, OverflowError) as error:
        raise VerificationError("the pinned no-follow CPython binary cannot be authenticated") from error
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
    require(
        not any(
            name.partition(".")[0] in FORBIDDEN_IMPORT_ROOTS
            for name in sys.modules
        ),
        "an independent verifier imported a candidate, adapter, or external regex engine",
    )


def authenticate_source_pins() -> None:
    pins: dict[str, str] = {
        V5_RELATIVE: V5_SHA256,
        AUDIT_RELATIVE: AUDIT_SHA256,
        POLICY_RELATIVE: POLICY_SHA256,
    }
    for suite in SUITES:
        pins[suite.oracle_relative] = suite.oracle_sha256
        pins[suite.recorder_relative] = suite.recorder_sha256
        if suite.previous_recorder_relative is not None:
            require(
                suite.previous_recorder_sha256 is not None,
                "the exact previous replacement recorder hash is mandatory",
            )
            pins[suite.previous_recorder_relative] = suite.previous_recorder_sha256
    for relative, expected in sorted(pins.items()):
        read_frozen(relative, expected, MAX_SOURCE_BYTES)


class SourceOnlyBoundary:
    """Deny all real files, engines, subprocesses, threads, clocks, and imports."""

    def __init__(self) -> None:
        self.saved: list[tuple[Any, str, Any]] = []
        self.counts: collections.Counter[str] = collections.Counter()

    def deny(self, category: str) -> Callable[..., Any]:
        def blocked(*args: Any, **kwargs: Any) -> Any:
            self.counts[category] += 1
            raise SourceOnlyError("synthetic self-test blocked real " + category)
        return blocked

    def install(self, owner: Any, name: str, category: str) -> None:
        if hasattr(owner, name):
            original = getattr(owner, name)
            self.saved.append((owner, name, original))
            setattr(owner, name, self.deny(category))

    def __enter__(self) -> SourceOnlyBoundary:
        for name in ("open", "listdir", "scandir", "stat", "lstat", "walk"):
            self.install(os, name, "file_or_archive_reads")
        for name in (
            "remove",
            "unlink",
            "rename",
            "replace",
            "mkdir",
            "makedirs",
            "rmdir",
            "symlink",
            "link",
            "chmod",
            "chown",
            "utime",
        ):
            self.install(os, name, "file_or_archive_writes")
        self.install(builtins, "open", "file_or_archive_reads")
        self.install(io, "open", "file_or_archive_reads")
        for name in (
            "open",
            "read_text",
            "read_bytes",
            "iterdir",
            "glob",
            "rglob",
            "exists",
            "is_file",
            "is_dir",
            "stat",
        ):
            self.install(pathlib.Path, name, "file_or_archive_reads")
        for name in (
            "write_text",
            "write_bytes",
            "touch",
            "mkdir",
            "unlink",
            "rename",
            "replace",
        ):
            self.install(pathlib.Path, name, "file_or_archive_writes")
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            self.install(subprocess, name, "worker_or_process_calls")
        for name in ("system", "popen", "fork", "spawnv", "spawnve", "posix_spawn"):
            self.install(os, name, "worker_or_process_calls")
        self.install(threading.Thread, "start", "thread_calls")
        for name in (
            "time",
            "time_ns",
            "monotonic",
            "monotonic_ns",
            "perf_counter",
            "perf_counter_ns",
            "process_time",
            "thread_time",
            "sleep",
        ):
            self.install(time, name, "clock_or_timing_calls")
        standard_re = sys.modules.get("re")
        if isinstance(standard_re, types.ModuleType):
            for name in (
                "compile",
                "search",
                "match",
                "fullmatch",
                "findall",
                "finditer",
                "sub",
                "subn",
                "split",
            ):
                self.install(standard_re, name, "regex_matcher_calls")
        native_sre = sys.modules.get("_sre")
        if isinstance(native_sre, types.ModuleType):
            self.install(native_sre, "compile", "regex_matcher_calls")
        self.install(builtins, "__import__", "imports_or_external_engines")
        return self

    def __exit__(self, error_type: Any, error: Any, traceback: Any) -> bool:
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)
        return False


def synthetic_callback_outcome(suite: SuitePin, module: str, api: str) -> dict[str, Any]:
    callback = {
        "event": "callback",
        "index": 0,
        "match": {"pattern_is_expected": True, "string_is_subject": True},
        "raises": True,
    }
    return {
        "status": "raise",
        "stage": api,
        "exception": {
            "kind": "ordinary-python-error",
            "type": suite.callback_class,
            "module": module,
            "message": suite.callback_message,
            "args": {
                "type": "tuple",
                "items": [{"type": "str", "value": suite.callback_message}],
            },
        },
        "callbacks": [callback],
        "events": [
            {"event": "phase", "name": "operation-start"},
            callback,
            {"event": "phase", "name": "operation-raise"},
        ],
        "warnings": [],
        "value": {"type": "none"},
    }


def synthetic_envelope(raw: bytes) -> dict[str, Any]:
    return {
        "base64": base64.b64encode(raw).decode("ascii"),
        "bytes": len(raw),
        "complete": True,
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


class MemoryDescriptor:
    """A synthetic descriptor; never resolves, opens, or reads a real path."""

    def __init__(self, raw: bytes) -> None:
        self.raw = raw
        self.offset = 0

    def read(self, descriptor: int, maximum: int) -> bytes:
        require(
            descriptor == 7331 and type(maximum) is int and maximum > 0,
            "a synthetic bounded descriptor was forged",
        )
        result = self.raw[self.offset:self.offset + maximum]
        self.offset += len(result)
        return result


def synthetic_gzip(raw: bytes, *, suffix: bytes = b"") -> bytes:
    compressor = zlib.compressobj(
        level=9,
        method=zlib.DEFLATED,
        wbits=16 + zlib.MAX_WBITS,
    )
    return compressor.compress(raw) + compressor.flush() + suffix


def synthetic_stream(
    payload: bytes,
    *,
    expected_compressed: bytes | None = None,
    expected_plain: bytes | None = None,
    fields: frozenset[str] = frozenset({"alpha", "nested"}),
) -> dict[str, Any]:
    archive = synthetic_gzip(payload)
    frozen_archive = archive if expected_compressed is None else expected_compressed
    frozen_plain = payload if expected_plain is None else expected_plain
    memory = MemoryDescriptor(archive)
    reader = VerifiedGzipReader(
        7331,
        len(frozen_archive),
        hashlib.sha256(frozen_archive).hexdigest(),
        len(frozen_plain),
        hashlib.sha256(frozen_plain).hexdigest(),
        read_block=memory.read,
    )
    result = StreamingObject(reader).select(fields)
    require(reader.finished, "the synthetic authenticated stream was not fully read")
    return result


def expect_rejection(operation: Callable[[], Any], label: str) -> int:
    try:
        operation()
    except (VerificationError, SourceOnlyError, TypeError, ValueError):
        return 1
    raise VerificationError("a forged synthetic negative control was accepted: " + label)


def self_test() -> dict[str, Any]:
    positive = 0
    negative = 0
    before_modules = frozenset(sys.modules)
    with SourceOnlyBoundary() as boundary:
        for suite in SUITES:
            for api in APIS:
                expected = synthetic_callback_outcome(suite, "__main__", api)
                observed = synthetic_callback_outcome(suite, suite.callback_module, api)
                group = "text-callback-error" if suite is SUBSTITUTION else "synthetic"
                target = None if suite is SUBSTITUTION else "callback-error"
                require(
                    owned_callback_artifact(
                        expected,
                        observed,
                        suite,
                        api=api,
                        cohort=group,
                        target=target,
                    ),
                    "a genuine exact owned callback module-only control was rejected",
                )
                positive += 1
                bad_outcomes: list[dict[str, Any]] = []
                for field in ("kind", "type", "module", "message", "args"):
                    mutation = json.loads(canonical(observed))
                    if field == "kind":
                        mutation["exception"][field] = "ordinary-user-error"
                    elif field == "type":
                        mutation["exception"][field] = suite.callback_class + "Subclass"
                    elif field == "module":
                        mutation["exception"][field] = "user.unrelated_callback"
                    elif field == "message":
                        mutation["exception"][field] = suite.callback_message + "!"
                    else:
                        mutation["exception"][field]["items"][0]["value"] += "!"
                    bad_outcomes.append(mutation)
                for field in ("callbacks", "events", "warnings", "value", "stage", "status"):
                    mutation = json.loads(canonical(observed))
                    if field in ("callbacks", "events", "warnings"):
                        mutation[field].append({"forged": True})
                    elif field == "value":
                        mutation[field] = {"type": "str", "value": "forged"}
                    elif field == "stage":
                        mutation[field] = "pattern.sub" if api != "pattern.sub" else "module.sub"
                    else:
                        mutation[field] = "return"
                    bad_outcomes.append(mutation)
                removed_exception = json.loads(canonical(observed))
                del removed_exception["exception"]["args"]
                bad_outcomes.append(removed_exception)
                extra_exception = json.loads(canonical(observed))
                extra_exception["exception"]["subclass"] = True
                bad_outcomes.append(extra_exception)
                missing_outcome = json.loads(canonical(observed))
                del missing_outcome["warnings"]
                bad_outcomes.append(missing_outcome)
                for mutation in bad_outcomes:
                    require(
                        not owned_callback_artifact(
                            expected,
                            mutation,
                            suite,
                            api=api,
                            cohort=group,
                            target=target,
                        ),
                        "a forged callback, subclass, user error, or dropped visible field passed",
                    )
                    negative += 1
                for wrong_api in ("match.expand", "user.sub", ""):
                    require(
                        not owned_callback_artifact(
                            expected,
                            observed,
                            suite,
                            api=wrong_api,
                            cohort=group,
                            target=target,
                        ),
                        "a non-substitution API was misclassified as an owned callback",
                    )
                    negative += 1
                if suite is SUBSTITUTION:
                    require(
                        not owned_callback_artifact(
                            expected,
                            observed,
                            suite,
                            api=api,
                            cohort="text-callback",
                            target=None,
                        )
                        and not owned_callback_artifact(
                            expected,
                            observed,
                            suite,
                            api=api,
                            cohort=group,
                            target="callback-error",
                        ),
                        "a non-frozen replacement callback cohort or target was excused",
                    )
                else:
                    require(
                        not owned_callback_artifact(
                            expected,
                            observed,
                            suite,
                            api=api,
                            cohort=group,
                            target="callback-return",
                        ),
                        "a genuine non-error shape target was falsely excused",
                    )
                negative += 1
        document = {"alpha": 7, "nested": {"ordered": [1, 2, 3]}}
        raw = canonical(document)
        require(
            decode_document(raw, 1024, "synthetic canonical document") == document,
            "a canonical synthetic JSON document was rejected",
        )
        positive += 1
        require(
            synthetic_stream(raw) == document,
            "a complete bounded synthetic gzip stream did not round-trip",
        )
        positive += 1
        envelope = synthetic_envelope(raw)
        require(
            decode_envelope(envelope, "synthetic authenticated stdout") == raw,
            "a complete synthetic strict base64 worker failed authentication",
        )
        positive += 1
        empty = synthetic_envelope(b"")
        require_empty_stream(empty, "synthetic empty stderr")
        positive += 1
        malformed_documents = (
            b'{"alpha":1,"alpha":2}\n',
            b'{"alpha":NaN}\n',
            b'{"alpha":Infinity}\n',
            b'{"alpha":-Infinity}\n',
            b'{"alpha":1}\n trailing',
            b'{"alpha": 1}\n',
            b'{"alpha":1}',
            b'',
            b'{"alpha":"\xff"}\n',
        )
        for index, malformed in enumerate(malformed_documents):
            negative += expect_rejection(
                lambda item=malformed: decode_document(
                    item, 1024, "synthetic malformed document"
                ),
                "malformed canonical document " + str(index),
            )
        for index, mutate in enumerate((
            {"base64": envelope["base64"] + "!", "bytes": envelope["bytes"], "complete": True, "sha256": envelope["sha256"]},
            {"base64": envelope["base64"], "bytes": envelope["bytes"] + 1, "complete": True, "sha256": envelope["sha256"]},
            {"base64": envelope["base64"], "bytes": envelope["bytes"], "complete": False, "sha256": envelope["sha256"]},
            {"base64": envelope["base64"], "bytes": envelope["bytes"], "complete": True, "sha256": "0" * 64},
            {"base64": envelope["base64"], "bytes": envelope["bytes"], "complete": True},
            {"base64": envelope["base64"], "bytes": envelope["bytes"], "complete": True, "sha256": envelope["sha256"], "extra": 1},
        )):
            negative += expect_rejection(
                lambda item=mutate: decode_envelope(item, "forged synthetic envelope"),
                "strict worker envelope " + str(index),
            )
        negative += expect_rejection(
            lambda: decode_envelope(empty, "forged missing worker"),
            "empty mandatory worker stdout",
        )
        negative += expect_rejection(
            lambda: require_empty_stream(envelope, "forged non-empty stderr"),
            "hidden process stderr",
        )
        for index, bad in enumerate((
            raw + b"x",
            canonical({"alpha": 7}),
            b'{"alpha":7,"alpha":8,"nested":{}}\n',
            b'{"alpha":7,"nested":{}}\n trailing',
        )):
            negative += expect_rejection(
                lambda item=bad: synthetic_stream(item),
                "bounded full-stream JSON " + str(index),
            )
        negative += expect_rejection(
            lambda: synthetic_stream(
                raw,
                expected_compressed=synthetic_gzip(raw + b"x"),
            ),
            "complete compressed gzip hash and size",
        )
        negative += expect_rejection(
            lambda: synthetic_stream(raw, expected_plain=raw + b"x"),
            "complete uncompressed gzip hash and size",
        )
        for index, invalid in enumerate((
            "",
            ".",
            "..",
            "../GOAL.md",
            "GOAL.md",
            "/tmp/hidden.json",
            "tools/../GOAL.md",
            "experiments/rust_public_practice_v1/holdout.json",
            "experiments/rust_public_practice_v1/performance.json",
            SOURCE_RELATIVE + "/../GOAL.md",
            SOURCE_RELATIVE + "\x00",
            SOURCE_RELATIVE.replace("/", "\\"),
        )):
            negative += expect_rejection(
                lambda item=invalid: safe_parts(item),
                "non-approved evidence path " + str(index),
            )
        for path in sorted(APPROVED_FILES):
            require(safe_parts(path) == tuple(path.split("/")), "a genuine frozen evidence path failed")
            positive += 1
        blockers: tuple[tuple[str, Callable[[], Any]], ...] = (
            ("read real archive", lambda: builtins.open("GOAL.md", "rb")),
            ("read archive with os.open", lambda: os.open("GOAL.md", os.O_RDONLY)),
            ("inspect real path", lambda: os.stat("GOAL.md")),
            ("read pathlib archive", lambda: pathlib.Path("GOAL.md").read_bytes()),
            ("spawn candidate process", lambda: subprocess.run(["true"])),
            ("spawn reference process", lambda: subprocess.Popen(["true"])),
            ("sample performance clock", lambda: time.perf_counter_ns()),
            ("sample wall clock", lambda: time.time_ns()),
            ("start worker thread", lambda: threading.Thread(target=lambda: None).start()),
            ("import candidate or engine", lambda: builtins.__import__("candidates")),
        )
        for label, operation in blockers:
            negative += expect_rejection(operation, label)
        standard_re = sys.modules.get("re")
        if isinstance(standard_re, types.ModuleType):
            for name in ("compile", "search", "match", "fullmatch", "sub", "subn"):
                operation = getattr(standard_re, name, None)
                if callable(operation):
                    negative += expect_rejection(
                        lambda action=operation: action("x", "x"),
                        "preloaded standard regex matcher " + name,
                    )
        for field in (
            "file_or_archive_reads",
            "worker_or_process_calls",
            "clock_or_timing_calls",
            "thread_calls",
            "imports_or_external_engines",
        ):
            require(
                boundary.counts[field] > 0,
                "a required synthetic-only effect blocker was never exercised: " + field,
            )
        if isinstance(standard_re, types.ModuleType):
            require(
                boundary.counts["regex_matcher_calls"] > 0,
                "a preloaded standard regex matcher was not continuously blocked",
            )
        counts = dict(sorted(boundary.counts.items()))
    require(
        frozenset(sys.modules) == before_modules,
        "a synthetic callback self-test imported a hidden candidate or engine",
    )
    require(positive >= 20 and negative >= 150, "the exhaustive synthetic controls were weakened")
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS",
        "positive_controls": positive,
        "negative_controls": negative,
        "effect_blockers_exercised": counts,
        "real_files_read": 0,
        "real_files_written": 0,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "candidate_imports": 0,
        "stdlib_matcher_calls": 0,
        "native_matcher_calls": 0,
        "external_engine_calls": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def verify(source_sha256: str) -> dict[str, Any]:
    verify_runtime(source_sha256)
    before_modules = frozenset(sys.modules)
    authenticate_source_pins()
    baselines: dict[str, tuple[list[dict[str, Any]], dict[str, Any]]] = {}
    for suite in SUITES:
        baselines[suite.name] = verify_baseline(suite)
    results = [
        verify_candidate(candidate, *baselines[candidate.suite.name])
        for candidate in CANDIDATES
    ]
    require(
        frozenset(sys.modules) == before_modules
        and not any(
            name.partition(".")[0] in FORBIDDEN_IMPORT_ROOTS
            for name in sys.modules
        ),
        "read-only historical replay imported a candidate, engine, or matcher",
    )
    require(
        [(item["original_all_mismatches_count"],
          item["owned_callback_module_only_artifact_count"],
          item["genuine_visible_mismatch_count"]) for item in results]
        == [(464, 128, 336), (192, 128, 64), (1_888, 496, 1_392)],
        "a frozen callback-falsification proof or genuine loss was changed",
    )
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "verifier_source_relative": SOURCE_RELATIVE,
        "verifier_source_sha256": source_sha256,
        "pinned_python": PINNED_PYTHON,
        "pinned_python_sha256": PINNED_PYTHON_SHA256,
        "pinned_python_version": "3.14.6",
        "suites": [
            {
                "suite": suite.name + "-v1",
                "oracle_relative": suite.oracle_relative,
                "oracle_sha256": suite.oracle_sha256,
                "recorder_relative": suite.recorder_relative,
                "recorder_sha256": suite.recorder_sha256,
                "matrix_sha256": suite.matrix_sha256,
                "published_seed": suite.seed,
                "case_count": suite.case_count,
                "cohort_count": 64,
                "variants_per_cohort": suite.variants_per_cohort,
                "baseline_receipt_sha256": suite.baseline.receipt_sha256,
                "baseline_archive_sha256": suite.baseline.sha256,
                "baseline_records_sha256": suite.baseline_records_sha256,
                "independent_reference_workers": 2,
                "reference_worker_pids": [82, 83],
                "reference_streams_match": True,
            }
            for suite in SUITES
        ],
        "candidates": results,
        "candidate_count": len(results),
        "complete_historical_mismatches": sum(
            item["original_all_mismatches_count"] for item in results
        ),
        "proven_module_only_callback_artifacts": sum(
            item["owned_callback_module_only_artifact_count"] for item in results
        ),
        "preserved_genuine_visible_mismatches": sum(
            item["genuine_visible_mismatch_count"] for item in results
        ),
        "new_reference_processes": 0,
        "new_candidate_processes": 0,
        "candidate_imports": 0,
        "regex_matcher_calls": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def main(argv: list[str]) -> int:
    try:
        if argv == ["--self-test"]:
            result = self_test()
        elif (
            len(argv) == 3
            and argv[0] == "--verify"
            and argv[1] == "--source-sha256"
        ):
            result = verify(argv[2])
        else:
            raise VerificationError(
                "use exactly --self-test or --verify --source-sha256 <frozen-sha256>"
            )
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (
        VerificationError,
        OSError,
        UnicodeError,
        RecursionError,
        MemoryError,
        zlib.error,
        binascii.Error,
    ) as error:
        try:
            sys.stderr.write("FAIL: " + str(error) + "\n")
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
