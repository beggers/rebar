#!/usr/bin/env python3
"""Safely refresh the frozen 1,024-case memory-safety comparison.

Version 2 retains the immutable V1 manifest, chart paths, baseline, source
closures, full candidate evidence, and lossless validators.  Replacing an
existing chart is allowed only when the caller explicitly pins both old graph
files. Both generated files are staged, backed up, authenticated, and restored
as a pair if any publication step fails.
"""

from __future__ import annotations

import argparse
import builtins
import codecs
import contextlib
import hashlib
import importlib
import io
import json
import os
import stat
import subprocess
import sys
import threading
import time
import zlib
from collections.abc import Callable, Iterator, Mapping
from typing import Any


ROOT = "/home/dev-user/src/rebar"
SOURCE_RELATIVE = "tools/render_managed_buffer_lifetime_overview_v2.py"
FROZEN_V1_RELATIVE = "tools/render_managed_buffer_lifetime_overview_v1.py"
FROZEN_V1_SHA256 = "9415853895f02abd0cebdd35f8ec8b6634191c6373b96b53859ebd4e2d8195a3"
SCHEMA = "rebar-managed-buffer-lifetime-overview-v1"
MANIFEST_RELATIVE = "docs/evidence/managed-buffer-lifetime-overview-v1.inputs.json"
SVG_RELATIVE = "docs/evidence/managed-buffer-lifetime-overview-v1.svg"
SUMMARY_RELATIVE = "docs/evidence/managed-buffer-lifetime-overview-v1.json"
EVIDENCE_DIRECTORY = "experiments/rust_public_practice_v1"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
ORACLE_RELATIVE = "tools/independent_managed_buffer_lifetime_v1.py"
ORACLE_SHA256 = "cedbab1227ea58a97d407cb339d2959a9f9be58a2085ce3106b65bb3385de489"
MATRIX_SHA256 = "28ef84b6989542ba8865c98e5296639c780c786078e2a99c7c0a95bfcb4b0976"
RECORDER_RELATIVE = "tools/record_independent_managed_buffer_candidates_v1.py"
RECORDER_SHA256 = "d7f9fdeb9979eaeaa5ffdcea5a655be31c070356d93d293289b9b90de876877a"
BASELINE_RECORDER_RELATIVE = "tools/record_independent_managed_buffer_lifetime_v1.py"
BASELINE_RECORDER_SHA256 = "dddc90f3b6449deeb31098d062af9077e3bea558645b3f2d71de2cd4e6488abd"
ORIGINAL_V5_RELATIVE = "tools/independent_original_cpython_suite_v5.py"
ORIGINAL_V5_SHA256 = "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
BASELINE_STEM = EVIDENCE_DIRECTORY + "/managed-buffer-lifetime-v1-shared-suite-v1"
BASELINE_ARCHIVE_RELATIVE = BASELINE_STEM + ".json.gz"
BASELINE_ARCHIVE_SHA256 = "1840d5c5faf0422cfaaae0e277cf5d9bc5ed954fe50beca3d9794b9fd33e5fba"
BASELINE_ARCHIVE_BYTES = 4_374_362
BASELINE_RECEIPT_RELATIVE = BASELINE_STEM + "-publication-receipt.json"
BASELINE_RECEIPT_SHA256 = "adb34ba45089983ac1857639995c51bdc3ae81e0656fa4b89fd5c0f72420b3ba"
BASELINE_REPORT_RELATIVE = BASELINE_STEM + ".json"
BASELINE_REPORT_SHA256 = "8c1acb346f476be4f05edd3e7afa73c9a4196bdafa19c2b6f90259ce6b622b68"
BASELINE_REPORT_BYTES = 108_978_141
BASELINE_RECORDS_SHA256 = "80293f5332300220f38c3f017d38611a5514b1b686918e692a53491945b196df"
PUBLISHED_SEED = 0x4D424C4946455631
CASE_COUNT = 1024
CASES_PER_GROUP = 32
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_RECEIPT_BYTES = 8 * 1024 * 1024
MAX_ARCHIVE_BYTES = 100 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 256 * 1024 * 1024
MAX_SELECTED_VALUE_BYTES = 64 * 1024 * 1024
CHUNK_BYTES = 131_072
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
GROUPS = (
    "direct-bytes-control", "direct-bytearray-control",
    "readonly-contiguous-view", "writable-contiguous-view",
    "readonly-sliced-contiguous-view", "writable-sliced-contiguous-view",
    "readonly-strided-view", "writable-strided-view",
    "released-before-operation", "released-after-match-before-group",
    "released-after-match-before-expand", "backing-mutated-after-match",
    "bytearray-resize-during-live-iterator",
    "bytearray-resize-after-iterator-teardown",
    "pep688-subject-acquire-release", "pep688-subject-overwrite-on-release",
    "pep688-subject-exporter-error", "pep688-template-exporter-error",
    "readonly-template-memoryview", "writable-template-memoryview",
    "strided-template-memoryview", "released-template-memoryview",
    "match-group-retained-lifetime", "iterator-create-and-advance-lifetime",
    "iterator-exhaust-release", "iterator-delete-and-gc-release",
    "native-scanner-search-lifetime", "native-scanner-match-lifetime",
    "public-scanner-branch-and-callback-identity",
    "public-scanner-lexicon-mutation-and-flags",
    "bytes-vs-unicode-type-separation",
    "unicode-surrogate-and-normalization-boundaries",
)
FAMILY_ORDER = ("rust", "c", "zig")
FAMILY_SPECS: dict[str, tuple[str, str, str, tuple[str, ...], bool]] = {
    "rust": (
        "candidates/rust_candidate.py", "candidates/_rust_engine.so",
        "candidates/_rust_bridge" + EXTENSION_SUFFIX,
        (
            "candidates/rust_candidate.py", "candidates/rust/py_bridge.c",
            "candidates/rust/Cargo.toml", "candidates/rust/Cargo.lock",
            "candidates/rust/src/lib.rs", "candidates/rust/src/newline.rs",
            "candidates/rust/src/search.rs", "candidates/rust/src/stack.rs",
            "candidates/rust/src/unicode_tables.rs",
        ),
        False,
    ),
    "c": (
        "candidates/vm_candidate.py",
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        "candidates/_vm_native" + EXTENSION_SUFFIX,
        ("candidates/vm_candidate.py", "candidates/_vm_native.c"),
        False,
    ),
    "zig": (
        "candidates/zig_candidate.py", "candidates/_zig_probe.so",
        "candidates/_zig_bridge" + EXTENSION_SUFFIX,
        ("candidates/zig_candidate.py", "candidates/zig/mini_regex.zig",
         "candidates/zig/py_bridge.c"),
        True,
    ),
}
GUARD_TRUE = (
    "original_matchers_blocked", "adapter_import_quarantined",
    "native_sre_blocked", "builtins_import_guarded",
    "importlib_import_guarded", "actual_object_identity_guarded",
    "warning_registry_introspection_safe", "warning_registry_exactly_absent",
    "cross_family_imports_blocked", "external_regex_imports_blocked",
)
TRUSTED_CTYPES_SHA256 = "349448c149c46962d6004808a214b4677267563204ec32cb6ef933effe0ee923"
FORBIDDEN_ROOTS = frozenset({
    "candidates", "_regex", "fancy_regex", "google_re2", "hyperscan",
    "onig", "oniguruma", "pcre", "pcre2", "re2", "regex", "rust_regex",
    "sre_compile", "sre_constants", "sre_parse", "vectorscan",
})
BASELINE_FIELDS = frozenset({
    "schema", "status", "label", "python", "oracle_source_sha256",
    "matrix_sha256", "published_seed", "group_count", "cases_per_group",
    "case_count", "groups", "source_closure_before", "source_closure_after",
    "source_closure_unchanged", "baseline_records_sha256",
    "baseline_reference_pids", "validated_reference_a_case_count",
    "validated_reference_b_case_count", "reference_a_records",
    "reference_b_records", "actual_reference_workers",
    "actual_candidate_workers", "actual_candidate_imports",
    "actual_baseline_controller_invocations", "clock_samples",
    "timing_trials_run", "benchmark_files_read", "hidden_cases_read",
    "performance", "candidate_qualified_for_hidden_benchmark",
    "final_winner_selected",
})
CANDIDATE_FIELDS = frozenset({
    "schema", "status", "python", "candidate_family", "label",
    "recorder_source_sha256", "managed_oracle_relative", "managed_oracle_sha256",
    "baseline_recorder_relative", "baseline_recorder_sha256",
    "original_v5_relative", "original_v5_sha256", "matrix_sha256",
    "published_seed", "group_count", "cases_per_group", "case_count", "groups",
    "baseline_receipt_relative", "baseline_receipt_sha256",
    "baseline_archive_relative", "baseline_archive_sha256",
    "baseline_uncompressed_report_sha256", "baseline_uncompressed_report_bytes",
    "baseline_records_sha256", "baseline_reference_pids",
    "candidate_owner_before", "candidate_owner_after", "candidate_owner_unchanged",
    "validated_baseline_record_count", "validated_candidate_record_count",
    "candidate_records_sha256", "candidate_records", "baseline_records",
    "mismatch_count", "all_mismatches", "mismatches_by_group",
    "all_mismatches_preserved", "matcher_guard", "actual_method_guard_checks",
    "actual_warning_registry_guard_checks", "actual_reference_workers",
    "validated_prior_reference_workers", "actual_candidate_workers",
    "actual_candidate_imports", "actual_candidate_process_invocations",
    "actual_candidate_pid", "actual_candidate_process_returncode",
    "actual_candidate_process_signal", "actual_candidate_process_timed_out",
    "actual_candidate_process_spawn_error", "all_failure_reasons", "failure_count",
    "clock_samples", "timing_trials_run", "benchmark_files_read",
    "hidden_cases_read", "performance", "candidate_qualified_for_hidden_benchmark",
    "final_winner_selected",
})


class OverviewError(Exception):
    """The frozen memory-lifetime evidence was incomplete or substituted."""


class SourceOnlyError(OverviewError):
    """A synthetic chart control attempted an actual external effect."""


def require(value: Any, message: str) -> None:
    if not value:
        raise OverviewError(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, ensure_ascii=True, allow_nan=False,
            sort_keys=True, separators=(",", ":"),
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, OverflowError) as error:
        raise OverviewError("the chart requires complete canonical JSON") from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_hash(value: Any, label: str) -> str:
    require(
        type(value) is str and len(value) == 64
        and all(item in "0123456789abcdef" for item in value),
        "an exact lowercase SHA-256 is mandatory: " + label,
    )
    return value


def safe_parts(value: Any) -> tuple[str, ...]:
    require(type(value) is str and bool(value)
            and "\\" not in value and "\x00" not in value,
            "a safe exact relative path is mandatory")
    parts = tuple(value.split("/"))
    require(all(item not in {"", ".", ".."} for item in parts),
            "the frozen chart path escapes the workspace")
    return parts


def unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "a complete evidence field was duplicated")
        result[key] = value
    return result


def decode_document(raw: Any, label: str, maximum: int = MAX_RECEIPT_BYTES) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= maximum,
            "complete bounded canonical evidence is mandatory: " + label)

    def reject_nonfinite(_: str) -> None:
        raise OverviewError("nonfinite evidence cannot enter a chart")

    try:
        value = json.loads(raw, object_pairs_hook=unique_object,
                           parse_constant=reject_nonfinite)
    except (OverviewError, TypeError, ValueError, UnicodeError) as error:
        raise OverviewError("invalid complete chart evidence: " + label) from error
    require(type(value) is dict and canonical(value) == raw,
            "chart evidence was clipped or is not canonical: " + label)
    return value


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == PINNED_PYTHON
        and os.path.realpath(sys.executable) == PINNED_PYTHON
        and os.path.abspath(__file__) == ROOT + "/" + SOURCE_RELATIVE
        and os.path.realpath(__file__) == ROOT + "/" + SOURCE_RELATIVE,
        "use only the isolated pinned Python 3.14.6 and exact chart source",
    )
    for name in sys.modules:
        require(type(name) is str and name.partition(".")[0] not in FORBIDDEN_ROOTS,
                "the chart must not import a candidate or external regex")


@contextlib.contextmanager
def open_owned(relative: str, maximum: int) -> Iterator[tuple[int, os.stat_result]]:
    parts = safe_parts(relative)
    require(type(maximum) is int and 0 < maximum <= MAX_UNCOMPRESSED_BYTES,
            "a bounded exact owned input is mandatory")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    directory_flags = flags | getattr(os, "O_DIRECTORY", 0)
    opened: list[int] = []
    try:
        current = os.open(ROOT, directory_flags)
        opened.append(current)
        for part in parts[:-1]:
            current = os.open(part, directory_flags, dir_fd=current)
            opened.append(current)
        descriptor = os.open(parts[-1], flags, dir_fd=current)
        opened.append(descriptor)
        before = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode)
                and (before.st_dev, before.st_ino, before.st_size)
                == (named.st_dev, named.st_ino, named.st_size)
                and 0 < before.st_size <= maximum,
                "a frozen regular chart input was substituted")
        yield descriptor, before
        after = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require((before.st_dev, before.st_ino, before.st_size)
                == (after.st_dev, after.st_ino, after.st_size)
                == (named.st_dev, named.st_ino, named.st_size),
                "an authenticated chart input changed during its complete read")
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def read_frozen(relative: str, expected: str, maximum: int) -> bytes:
    valid_hash(expected, relative)
    with open_owned(relative, maximum) as (descriptor, before):
        remaining = before.st_size
        hasher = hashlib.sha256()
        blocks: list[bytes] = []
        while remaining:
            block = os.read(descriptor, min(CHUNK_BYTES, remaining))
            require(type(block) is bytes and bool(block), "chart evidence was truncated")
            blocks.append(block)
            hasher.update(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"" and hasher.hexdigest() == expected,
                "chart evidence gained a suffix or failed its pinned SHA-256")
        return b"".join(blocks)


class VerifiedGzipReader:
    """Stream exactly one authenticated gzip member with bounded expansion."""

    def __init__(
        self, descriptor: int, archive_bytes: int, archive_sha256: str,
        report_bytes: int, report_sha256: str,
    ) -> None:
        require(type(archive_bytes) is int and 0 < archive_bytes <= MAX_ARCHIVE_BYTES
                and type(report_bytes) is int and 0 < report_bytes <= MAX_UNCOMPRESSED_BYTES,
                "exact bounded compressed and original byte counts are required")
        self.descriptor = descriptor
        self.archive_bytes = archive_bytes
        self.archive_sha256 = valid_hash(archive_sha256, "gzip archive")
        self.report_bytes = report_bytes
        self.report_sha256 = valid_hash(report_sha256, "original JSON")
        self.inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
        self.compressed = hashlib.sha256()
        self.original = hashlib.sha256()
        self.compressed_count = 0
        self.original_count = 0
        self.pending = b""
        self.finished = False

    def read(self, requested: int) -> bytes:
        require(type(requested) is int and 0 < requested <= CHUNK_BYTES,
                "stream only bounded complete evidence blocks")
        result = bytearray()
        while len(result) < requested and not self.finished:
            if not self.pending and self.compressed_count < self.archive_bytes:
                remaining = self.archive_bytes - self.compressed_count
                block = os.read(self.descriptor, min(CHUNK_BYTES, remaining))
                require(type(block) is bytes and bool(block),
                        "an authenticated gzip archive was truncated")
                self.compressed_count += len(block)
                self.compressed.update(block)
                self.pending = block
            if self.pending:
                limit = min(requested - len(result),
                            self.report_bytes - self.original_count + 1)
                try:
                    plain = self.inflater.decompress(self.pending, limit)
                except (zlib.error, ValueError, OverflowError) as error:
                    raise OverviewError("the authenticated gzip archive is invalid") from error
                require(not self.inflater.unused_data,
                        "gzip trailing bytes and extra members are forbidden")
                self.pending = self.inflater.unconsumed_tail
                if plain:
                    self.original_count += len(plain)
                    require(self.original_count <= self.report_bytes,
                            "gzip expansion exceeded its frozen bound")
                    self.original.update(plain)
                    result.extend(plain)
                continue
            require(self.compressed_count == self.archive_bytes,
                    "gzip input ended before its exact byte count")
            require(self.inflater.eof and not self.inflater.unused_data,
                    "the complete single-member gzip footer is missing")
            require(os.read(self.descriptor, 1) == b"",
                    "the pinned gzip file gained an unauthenticated suffix")
            try:
                tail = self.inflater.flush(CHUNK_BYTES)
            except (zlib.error, ValueError) as error:
                raise OverviewError("the complete gzip stream could not finish") from error
            require(not tail, "gzip retained unauthenticated original bytes")
            require(self.compressed.hexdigest() == self.archive_sha256,
                    "the compressed evidence failed its pinned SHA-256")
            require(self.original_count == self.report_bytes
                    and self.original.hexdigest() == self.report_sha256,
                    "the restored evidence failed its exact bytes or SHA-256")
            self.finished = True
        return bytes(result)


class StreamingObject:
    """Select complete top-level JSON fields without loading a giant archive."""

    def __init__(self, stream: Any) -> None:
        self.stream = stream
        self.utf8 = codecs.getincrementaldecoder("utf-8")("strict")
        self.decoder = json.JSONDecoder(object_pairs_hook=unique_object)
        self.buffer = ""
        self.position = 0
        self.ended = False

    def fill(self) -> bool:
        if self.ended:
            return False
        block = self.stream.read(CHUNK_BYTES)
        require(type(block) is bytes, "a streamed report produced non-byte output")
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
        return self.buffer[self.position] if self.position < len(self.buffer) else None

    def take(self) -> str:
        value = self.peek()
        require(value is not None, "the complete streamed JSON document was clipped")
        self.position += 1
        return value

    def whitespace(self) -> None:
        while self.peek() in (" ", "\t", "\r", "\n"):
            self.position += 1
            self.compact()

    def literal(self, expected: str) -> None:
        self.whitespace()
        require(self.take() == expected, "a streamed JSON delimiter was changed")

    def value(self) -> Any:
        self.whitespace()
        self.compact()
        while True:
            try:
                result, ending = self.decoder.raw_decode(self.buffer, self.position)
            except json.JSONDecodeError as error:
                require(not self.ended, "a complete selected JSON field was clipped")
                require(len(self.buffer) - self.position <= MAX_SELECTED_VALUE_BYTES,
                        "a selected full case vector exceeds its safe bound")
                if not self.fill():
                    raise OverviewError("a selected JSON value is incomplete") from error
                continue
            self.position = ending
            return result

    def skip(self) -> None:
        self.whitespace()
        first = self.peek()
        require(first is not None, "an unselected streamed JSON value was clipped")
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
                    require(bool(stack) and stack[-1] == item,
                            "an unselected JSON container was corrupted")
                    stack.pop()
                    if not stack:
                        return
                self.compact()
        else:
            start = self.position
            while True:
                item = self.peek()
                if item is None or item in (",", "}", "]", " ", "\t", "\r", "\n"):
                    break
                self.position += 1
            raw = self.buffer[start:self.position]
            try:
                actual, ending = self.decoder.raw_decode(raw)
            except json.JSONDecodeError as error:
                raise OverviewError("an unselected JSON scalar is invalid") from error
            require(ending == len(raw) and actual is not ...,
                    "an unselected JSON scalar was corrupted")

    def select(self, fields: frozenset[str]) -> dict[str, Any]:
        require(type(fields) is frozenset and bool(fields),
                "an exact frozen selected field set is required")
        self.literal("{")
        seen: set[str] = set()
        selected: dict[str, Any] = {}
        self.whitespace()
        if self.peek() == "}":
            self.take()
        else:
            while True:
                key = self.value()
                require(type(key) is str and key not in seen,
                        "a full streamed JSON field was duplicated")
                seen.add(key)
                self.literal(":")
                if key in fields:
                    selected[key] = self.value()
                else:
                    self.skip()
                self.whitespace()
                ending = self.take()
                if ending == "}":
                    break
                require(ending == ",", "a streamed JSON separator was substituted")
        self.whitespace()
        require(self.peek() is None, "a complete report gained a hidden JSON suffix")
        require(set(selected) == fields,
                "a mandatory complete baseline or candidate field was hidden")
        return selected


def evidence_pin(value: Any, seen: set[str]) -> tuple[str, str]:
    require(type(value) is dict and set(value) == {"relative", "sha256"},
            "an exact source-pinned evidence file is mandatory")
    relative = value["relative"]
    parts = safe_parts(relative)
    require(parts[:2] == ("experiments", "rust_public_practice_v1")
            and len(parts) == 3 and relative not in seen,
            "evidence was reused, escaped, or silently substituted")
    seen.add(relative)
    return relative, valid_hash(value["sha256"], relative)


def validate_outcome(value: Any) -> None:
    require(type(value) is dict and set(value) == {
        "status", "stage", "value", "exception", "events",
        "checkpoints", "callbacks", "warnings",
    } and value.get("status") in {"return", "raise"}
            and type(value.get("stage")) is str
            and all(type(value.get(name)) is list
                    for name in ("events", "checkpoints", "callbacks", "warnings")),
            "a full memory-lifetime case outcome was omitted")
    if value["status"] == "return":
        require(value["exception"] is None, "a returned result concealed an exception")
    else:
        require(value["value"] is None and type(value["exception"]) is dict,
                "an observed exception was concealed")
    canonical(value)


def validate_records(
    records: Any, expected: str, digestor: Callable[[Any], str] = digest,
) -> list[dict[str, Any]]:
    valid_hash(expected, "complete lifetime outcomes")
    require(type(records) is list and len(records) == CASE_COUNT,
            "every one of the 1,024 ordered cases is mandatory")
    for index, record in enumerate(records):
        require(type(record) is dict and set(record) == {
            "case", "group", "variant", "outcome",
        } and record.get("case")
            == "managed-buffer-lifetime.v1." + format(index, "04d")
            and record.get("group") == GROUPS[index // CASES_PER_GROUP]
            and type(record.get("variant")) is int
            and record["variant"] == index % CASES_PER_GROUP,
            "a frozen memory-lifetime case was reordered or removed")
        validate_outcome(record["outcome"])
    require(digestor(records) == expected,
            "a complete source-ordered outcome vector failed its SHA-256")
    return records


def fixed_fields(value: Mapping[str, Any], expected: Mapping[str, Any], label: str) -> None:
    for key, wanted in expected.items():
        actual = value.get(key)
        require(type(actual) is type(wanted) and actual == wanted,
                label + " changed: " + key)


def validate_baseline_receipt(value: Any) -> dict[str, Any]:
    require(type(value) is dict, "the passing original Python receipt is mandatory")
    fixed_fields(value, {
        "schema": "rebar-independent-managed-buffer-lifetime-v1-recorder-durable-publication-receipt",
        "status": "PASS", "baseline_result_status": "PASS",
        "label": "shared-suite-v1", "python": "3.14.6",
        "oracle_relative": ORACLE_RELATIVE, "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256, "published_seed": PUBLISHED_SEED,
        "group_count": len(GROUPS), "cases_per_group": CASES_PER_GROUP,
        "case_count": CASE_COUNT, "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "actual_reference_workers": 2, "actual_candidate_workers": 0,
        "actual_candidate_imports": 0, "actual_baseline_controller_invocations": 1,
        "report_relative": BASELINE_REPORT_RELATIVE,
        "report_sha256": BASELINE_REPORT_SHA256,
        "report_bytes": BASELINE_REPORT_BYTES,
        "report_file_fsync_completed": True,
        "report_directory_fsync_completed": True,
        "report_atomic_no_overwrite_link": True,
        "report_complete_readback_verified": True,
        "receipt_relative": BASELINE_RECEIPT_RELATIVE,
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }, "the actual two-reference passing baseline receipt")
    pids = value.get("baseline_reference_pids")
    require(type(pids) is list and len(pids) == 2
            and all(type(pid) is int and pid > 0 for pid in pids)
            and pids[0] != pids[1],
            "two distinct original Python baseline processes are mandatory")
    return value


def validate_baseline(
    value: Any, receipt: Mapping[str, Any],
    digestor: Callable[[Any], str] = digest,
) -> list[dict[str, Any]]:
    require(type(value) is dict and set(value) == BASELINE_FIELDS,
            "the complete selected Python baseline was omitted")
    fixed_fields(value, {
        "schema": "rebar-independent-managed-buffer-lifetime-v1-recorder-complete-baseline-report",
        "status": "PASS", "label": "shared-suite-v1", "python": "3.14.6",
        "oracle_source_sha256": ORACLE_SHA256, "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED, "group_count": len(GROUPS),
        "cases_per_group": CASES_PER_GROUP, "case_count": CASE_COUNT,
        "source_closure_unchanged": True,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "actual_reference_workers": 2, "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }, "the complete archived Python baseline")
    require(value.get("groups") == list(GROUPS),
            "the frozen 32 memory-lifetime groups were changed")
    require(value.get("baseline_reference_pids") == receipt["baseline_reference_pids"],
            "the archived original Python reference workers were substituted")
    require(type(value.get("source_closure_before")) is dict
            and value["source_closure_before"] == value.get("source_closure_after"),
            "a genuine frozen Python reference source changed during observation")
    first = validate_records(value["reference_a_records"], BASELINE_RECORDS_SHA256, digestor)
    second = validate_records(value["reference_b_records"], BASELINE_RECORDS_SHA256, digestor)
    require(first == second, "the two original Python reference vectors do not agree")
    return first


def validate_owner(owner: Any, relative: str, expected: str | None = None) -> dict[str, Any]:
    require(type(owner) is dict and set(owner) == {
        "relative", "sha256", "bytes", "device", "inode",
    } and owner.get("relative") == relative
            and type(owner.get("bytes")) is int and owner["bytes"] > 0
            and type(owner.get("device")) is int and owner["device"] >= 0
            and type(owner.get("inode")) is int and owner["inode"] > 0,
            "a complete owned candidate source or binary was concealed")
    valid_hash(owner.get("sha256"), relative)
    require(expected is None or owner["sha256"] == expected,
            "a source-matched candidate was silently replaced")
    return owner


def validate_closure(value: Any, family: str, source_hash: str) -> dict[str, Any]:
    adapter, engine, bridge, sources, _ = FAMILY_SPECS[family]
    expected_paths = set(sources) | {engine, bridge}
    require(type(value) is dict and set(value) == expected_paths,
            "an independently owned complete engine source closure was omitted")
    for path in expected_paths:
        validate_owner(value[path], path, source_hash if path == adapter else None)
    require((value[engine] == value[bridge]) is (family == "c"),
            "independent engine and native-bridge ownership was mixed")
    return value


def validate_guard(value: Any, family: str) -> None:
    require(type(value) is dict, "a continuous no-delegation guard is mandatory")
    for key in GUARD_TRUE:
        require(value.get(key) is True,
                "the candidate's original-engine guard was disabled: " + key)
    require(value.get("public_type_names_used_for_ownership") is False,
            "a compatible owned pattern was treated as another engine")
    for key in ("actual_method_guard_checks", "actual_warning_registry_guard_checks"):
        require(type(value.get(key)) is int and value[key] == 2 * CASE_COUNT,
                "a before-and-after per-case guard was omitted")
    ffi = FAMILY_SPECS[family][4]
    require(value.get("owned_native_ffi_allowed") is ffi,
            "the independent native library policy changed")
    for key in ("trusted_stdlib_ctypes_preloaded",
                "trusted_stdlib_ctypes_builtin_verified",
                "trusted_stdlib_ctypes_pythonapi_initialized"):
        require(value.get(key) is ffi, "a guarded native preload was changed")
    require(value.get("trusted_stdlib_ctypes_source_sha256")
            == (TRUSTED_CTYPES_SHA256 if ffi else None),
            "the approved trusted native-binding source changed")
    for key in ("cached_original_matcher_descendant_count",
                "cached_original_holder_count", "owned_ctypes_load_count",
                "owned_ctypes_symbol_count"):
        require(type(value.get(key)) is int and value[key] >= 0,
                "an actual no-delegation guard counter was hidden")
    require((value["owned_ctypes_load_count"] > 0
             and value["owned_ctypes_symbol_count"] > 0) is ffi,
            "the owned native engine loading evidence was changed")


def validate_candidate_receipt(
    value: Any, family: str, source_hash: str,
    report_path: str, report_hash: str, receipt_path: str,
) -> dict[str, Any]:
    require(type(value) is dict, "a complete candidate publication receipt is mandatory")
    fixed_fields(value, {
        "schema": "rebar-independent-managed-buffer-candidate-recorder-v1-durable-publication-receipt",
        "status": "PASS", "python": "3.14.6", "candidate_family": family,
        "recorder_source_sha256": RECORDER_SHA256,
        "managed_oracle_sha256": ORACLE_SHA256,
        "baseline_recorder_sha256": BASELINE_RECORDER_SHA256,
        "original_v5_sha256": ORIGINAL_V5_SHA256,
        "matrix_sha256": MATRIX_SHA256, "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "baseline_receipt_relative": BASELINE_RECEIPT_RELATIVE,
        "baseline_receipt_sha256": BASELINE_RECEIPT_SHA256,
        "baseline_archive_relative": BASELINE_ARCHIVE_RELATIVE,
        "baseline_archive_sha256": BASELINE_ARCHIVE_SHA256,
        "baseline_uncompressed_report_sha256": BASELINE_REPORT_SHA256,
        "baseline_uncompressed_report_bytes": BASELINE_REPORT_BYTES,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": CASE_COUNT,
        "all_mismatches_preserved": True,
        "actual_method_guard_checks": 2 * CASE_COUNT,
        "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
        "actual_candidate_workers": 1,
        "actual_candidate_process_invocations": 1,
        "candidate_owner_unchanged": True,
        "report_relative": report_path,
        "report_sha256": report_hash,
        "report_compression": "gzip-mtime-zero-level-9",
        "report_file_fsync_completed": True,
        "report_directory_fsync_completed": True,
        "report_atomic_no_overwrite_link": True,
        "report_complete_readback_verified": True,
        "receipt_relative": receipt_path,
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_candidate": True,
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }, "the candidate's authentic durable publication receipt")
    status = value.get("candidate_result_status")
    mismatches = value.get("mismatch_count")
    require(status in {"PASS", "FAIL"}
            and type(mismatches) is int and 0 <= mismatches <= CASE_COUNT
            and (status == "PASS") is (mismatches == 0),
            "publication success was confused with candidate correctness")
    require(type(value.get("actual_candidate_imports")) is int
            and value["actual_candidate_imports"] >= 2,
            "the actual independent adapter and native bridge were never loaded")
    require(type(value.get("report_bytes")) is int
            and 0 < value["report_bytes"] <= MAX_ARCHIVE_BYTES
            and type(value.get("report_uncompressed_bytes")) is int
            and 0 < value["report_uncompressed_bytes"] <= MAX_UNCOMPRESSED_BYTES,
            "the exact bounded candidate report byte counts were omitted")
    valid_hash(value.get("report_uncompressed_sha256"), "full candidate report")
    valid_hash(value.get("candidate_records_sha256"), "full candidate outcomes")
    before = validate_closure(value.get("candidate_owner_before"), family, source_hash)
    after = validate_closure(value.get("candidate_owner_after"), family, source_hash)
    require(before == after, "the owned candidate source or native engine changed")
    by_group = value.get("mismatches_by_group")
    require(type(by_group) is dict and set(by_group) == set(GROUPS)
            and all(type(by_group[name]) is int
                    and 0 <= by_group[name] <= CASES_PER_GROUP for name in GROUPS)
            and sum(by_group.values()) == mismatches,
            "the receipt concealed or redistributed a failing safety case")
    return value


def validate_candidate(
    value: Any, receipt: Mapping[str, Any], family: str, source_hash: str,
    baseline: list[dict[str, Any]], digestor: Callable[[Any], str] = digest,
) -> dict[str, Any]:
    require(type(value) is dict and set(value) == CANDIDATE_FIELDS,
            "a mandatory selected candidate report field was omitted")
    fixed_fields(value, {
        "schema": "rebar-independent-managed-buffer-candidate-recorder-v1-complete-candidate-report",
        "status": receipt["candidate_result_status"],
        "python": "3.14.6", "candidate_family": family,
        "label": receipt["label"], "recorder_source_sha256": RECORDER_SHA256,
        "managed_oracle_relative": ORACLE_RELATIVE,
        "managed_oracle_sha256": ORACLE_SHA256,
        "baseline_recorder_relative": BASELINE_RECORDER_RELATIVE,
        "baseline_recorder_sha256": BASELINE_RECORDER_SHA256,
        "original_v5_relative": ORIGINAL_V5_RELATIVE,
        "original_v5_sha256": ORIGINAL_V5_SHA256,
        "matrix_sha256": MATRIX_SHA256, "published_seed": PUBLISHED_SEED,
        "group_count": len(GROUPS), "cases_per_group": CASES_PER_GROUP,
        "case_count": CASE_COUNT,
        "baseline_receipt_relative": BASELINE_RECEIPT_RELATIVE,
        "baseline_receipt_sha256": BASELINE_RECEIPT_SHA256,
        "baseline_archive_relative": BASELINE_ARCHIVE_RELATIVE,
        "baseline_archive_sha256": BASELINE_ARCHIVE_SHA256,
        "baseline_uncompressed_report_sha256": BASELINE_REPORT_SHA256,
        "baseline_uncompressed_report_bytes": BASELINE_REPORT_BYTES,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "candidate_owner_unchanged": True,
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": CASE_COUNT,
        "candidate_records_sha256": receipt["candidate_records_sha256"],
        "mismatch_count": receipt["mismatch_count"],
        "all_mismatches_preserved": True,
        "actual_method_guard_checks": 2 * CASE_COUNT,
        "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
        "actual_reference_workers": 0,
        "validated_prior_reference_workers": 2,
        "actual_candidate_workers": 1,
        "actual_candidate_imports": receipt["actual_candidate_imports"],
        "actual_candidate_process_invocations": 1,
        "actual_candidate_process_returncode": 0,
        "actual_candidate_process_signal": None,
        "actual_candidate_process_timed_out": False,
        "actual_candidate_process_spawn_error": None,
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }, "the complete genuinely observed candidate result")
    require(value.get("groups") == list(GROUPS),
            "candidate results changed the 32 frozen case groups")
    pids = value.get("baseline_reference_pids")
    require(type(pids) is list and len(pids) == 2
            and all(type(pid) is int and pid > 0 for pid in pids)
            and pids[0] != pids[1], "the authentic reference worker PIDs were concealed")
    candidate_pid = value.get("actual_candidate_pid")
    require(type(candidate_pid) is int and candidate_pid > 0
            and candidate_pid not in pids,
            "the actual candidate was not an independent isolated process")
    before = validate_closure(value.get("candidate_owner_before"), family, source_hash)
    after = validate_closure(value.get("candidate_owner_after"), family, source_hash)
    require(before == after == receipt["candidate_owner_before"]
            == receipt["candidate_owner_after"],
            "the candidate report silently mixed different source or binary revisions")
    validate_guard(value.get("matcher_guard"), family)
    require(value.get("baseline_records") == baseline,
            "the candidate was compared with a different Python baseline")
    actual = validate_records(value.get("candidate_records"),
                              receipt["candidate_records_sha256"], digestor)
    mismatches: list[dict[str, Any]] = []
    counts = {group: 0 for group in GROUPS}
    for index, (expected, observed) in enumerate(zip(baseline, actual, strict=True)):
        if expected["outcome"] != observed["outcome"]:
            mismatch = value["all_mismatches"][len(mismatches)]
            require(type(mismatch) is dict and set(mismatch) == {
                "case", "group", "input", "baseline_outcome", "candidate_outcome",
            } and mismatch.get("case") == expected["case"]
                    and mismatch.get("group") == expected["group"]
                    and mismatch.get("baseline_outcome") == expected["outcome"]
                    and mismatch.get("candidate_outcome") == observed["outcome"],
                    "a complete failing case or original outcome was hidden")
            case_input = mismatch["input"]
            require(type(case_input) is dict
                    and case_input.get("case") == expected["case"]
                    and case_input.get("group") == expected["group"]
                    and case_input.get("variant") == index % CASES_PER_GROUP
                    and case_input.get("seed") == PUBLISHED_SEED,
                    "a full mismatch was attached to a different frozen case")
            mismatches.append(mismatch)
            counts[expected["group"]] += 1
    require(type(value.get("all_mismatches")) is list
            and value["all_mismatches"] == mismatches
            and len(mismatches) == receipt["mismatch_count"]
            and value.get("mismatches_by_group") == counts
            and receipt["mismatches_by_group"] == counts,
            "a candidate mismatch was omitted, duplicated, or miscounted")
    failures = value.get("all_failure_reasons")
    require(type(failures) is list and type(value.get("failure_count")) is int
            and value["failure_count"] == len(failures),
            "complete candidate failure reasons were hidden")
    if mismatches:
        require(value["status"] == "FAIL" and len(failures) >= 1,
                "real incompatible cases were rendered as a passing candidate")
    else:
        require(value["status"] == "PASS" and failures == [],
                "a candidate with a runtime failure cannot be shown as passing")
    return {
        "passed": CASE_COUNT - len(mismatches),
        "failed": len(mismatches),
        "not_measured": 0,
        "mismatches_by_group": counts,
    }


Loader = Callable[[str, str, str, str | None, int | None], dict[str, Any]]


def manifest_rows(
    manifest: Any, loader: Loader, digestor: Callable[[Any], str] = digest,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    require(type(manifest) is dict and set(manifest) == {
        "schema", "python", "case_denominator", "oracle_source_sha256",
        "matrix_sha256", "baseline", "families",
    }, "the exact separate 1,024-case chart manifest is mandatory")
    fixed_fields(manifest, {
        "schema": SCHEMA + "-inputs", "python": "3.14.6",
        "case_denominator": CASE_COUNT,
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
    }, "the frozen 1,024-case lifetime chart manifest")
    seen: set[str] = set()
    base = manifest.get("baseline")
    require(type(base) is dict and set(base) == {"archive", "receipt"},
            "the exact authentic archived Python baseline is mandatory")
    receipt_path, receipt_hash = evidence_pin(base["receipt"], seen)
    archive_path, archive_hash = evidence_pin(base["archive"], seen)
    require((receipt_path, receipt_hash)
            == (BASELINE_RECEIPT_RELATIVE, BASELINE_RECEIPT_SHA256)
            and (archive_path, archive_hash)
            == (BASELINE_ARCHIVE_RELATIVE, BASELINE_ARCHIVE_SHA256),
            "the frozen two-reference baseline was silently substituted")
    base_receipt = validate_baseline_receipt(
        loader(receipt_path, receipt_hash, "receipt", None, None)
    )
    baseline = validate_baseline(
        loader(archive_path, archive_hash, "baseline",
               BASELINE_REPORT_SHA256, BASELINE_REPORT_BYTES),
        base_receipt, digestor,
    )
    rows: list[dict[str, Any]] = [{
        "family": "python", "label": "Python baseline",
        "state": "RUN", "passed": CASE_COUNT, "failed": 0,
        "not_measured": 0, "case_denominator": CASE_COUNT,
        "mismatches_by_group": {group: 0 for group in GROUPS},
    }]
    families = manifest.get("families")
    require(type(families) is list and len(families) == len(FAMILY_ORDER),
            "all three independently written candidate families are mandatory")
    for expected, item in zip(FAMILY_ORDER, families, strict=True):
        require(type(item) is dict and set(item) == {
            "family", "candidate_source_sha256", "state", "report", "receipt",
            "superseded",
        } and item.get("family") == expected,
                "an independently written engine was omitted or reordered")
        family_hash = valid_hash(item.get("candidate_source_sha256"), expected)
        state = item.get("state")
        require(state in {"RUN", "NOT MEASURED"}
                and type(item.get("superseded")) is list,
                "unmeasured or historical work was misclassified")
        previous: list[dict[str, Any]] = []
        for older in item["superseded"]:
            require(type(older) is dict and set(older) == {"report", "receipt"},
                    "a superseded complete candidate pair was omitted")
            old_receipt_path, old_receipt_hash = evidence_pin(older["receipt"], seen)
            old_report_path, old_report_hash = evidence_pin(older["report"], seen)
            old_receipt = loader(old_receipt_path, old_receipt_hash, "receipt", None, None)
            require(type(old_receipt) is dict
                    and old_receipt.get("candidate_family") == expected,
                    "a historical report was borrowed from another engine")
            old_before = old_receipt.get("candidate_owner_before")
            adapter = FAMILY_SPECS[expected][0]
            require(type(old_before) is dict and adapter in old_before,
                    "a historical engine omitted its adapter identity")
            old_hash = valid_hash(old_before[adapter].get("sha256"), "historical adapter")
            valid_old = validate_candidate_receipt(
                old_receipt, expected, old_hash, old_report_path,
                old_report_hash, old_receipt_path,
            )
            old_report = loader(old_report_path, old_report_hash, "candidate",
                                valid_old["report_uncompressed_sha256"],
                                valid_old["report_uncompressed_bytes"])
            historic = validate_candidate(old_report, valid_old, expected,
                                          old_hash, baseline, digestor)
            previous.append({
                "report": {"relative": old_report_path, "sha256": old_report_hash},
                "receipt": {"relative": old_receipt_path, "sha256": old_receipt_hash},
                "candidate_source_sha256": old_hash,
                "passed": historic["passed"], "failed": historic["failed"],
            })
        row: dict[str, Any] = {
            "family": expected, "label": {"rust": "Rust", "c": "C", "zig": "Zig"}[expected],
            "candidate_source_sha256": family_hash,
            "state": state, "case_denominator": CASE_COUNT,
            "superseded": previous,
        }
        if state == "NOT MEASURED":
            require(item["report"] is None and item["receipt"] is None,
                    "a gray engine must not claim an actual current result")
            row.update({"passed": 0, "failed": 0,
                        "not_measured": CASE_COUNT, "report": None,
                        "receipt": None, "mismatches_by_group": None})
        else:
            report_path, report_hash = evidence_pin(item["report"], seen)
            candidate_receipt_path, candidate_receipt_hash = evidence_pin(item["receipt"], seen)
            receipt = validate_candidate_receipt(
                loader(candidate_receipt_path, candidate_receipt_hash,
                       "receipt", None, None),
                expected, family_hash, report_path, report_hash,
                candidate_receipt_path,
            )
            candidate = loader(report_path, report_hash, "candidate",
                               receipt["report_uncompressed_sha256"],
                               receipt["report_uncompressed_bytes"])
            row.update(validate_candidate(candidate, receipt, expected,
                                          family_hash, baseline, digestor))
            row["report"] = {"relative": report_path, "sha256": report_hash}
            row["receipt"] = {"relative": candidate_receipt_path,
                              "sha256": candidate_receipt_hash}
        require(all(type(row[key]) is int and row[key] >= 0
                    for key in ("passed", "failed", "not_measured"))
                and row["passed"] + row["failed"] + row["not_measured"] == CASE_COUNT,
                "a candidate silently changed its 1,024-case denominator")
        rows.append(row)
    return {
        "archive": {"relative": archive_path, "sha256": archive_hash},
        "receipt": {"relative": receipt_path, "sha256": receipt_hash},
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
    }, rows


def escape_xml(value: str) -> str:
    require(type(value) is str, "chart text must be safely escaped")
    return (value.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;")
            .replace("'", "&apos;"))


def make_svg(rows: list[dict[str, Any]], source_hash: str, manifest_hash: str) -> bytes:
    require(type(rows) is list and len(rows) == 4,
            "show the Python baseline and all three independent engines")
    colors = (("passed", "#15803d", "Matches Python"),
              ("failed", "#dc2626", "Does not match Python"),
              ("not_measured", "#94a3b8", "Not yet measured"))
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="530" '
        'viewBox="0 0 1120 530" role="img" aria-labelledby="lifetime-title lifetime-desc">',
        '<title id="lifetime-title">Memory and buffer safety compared with Python</title>',
        '<desc id="lifetime-desc">Python, Rust, C, and Zig are shown against '
        'the same separate 1,024 Python memory and buffer safety checks. '
        'Green matches Python; red does not; gray has not yet been measured. '
        'No speed or hidden benchmark is included.</desc>',
        '<rect width="1120" height="530" rx="18" fill="#f8fafc"/>',
        '<text x="42" y="53" fill="#0f172a" font-family="system-ui,sans-serif" '
        'font-size="26" font-weight="700">Memory and buffer safety</text>',
        '<text x="42" y="82" fill="#475569" font-family="system-ui,sans-serif" '
        'font-size="15">Same 1,024 extra Python checks for every engine '
        '· speed not measured</text>',
    ]
    for index, (_, color, label) in enumerate(colors):
        x = 43 + index * 232
        parts.append(f'<rect x="{x}" y="104" width="14" height="14" rx="3" '
                     f'fill="{color}"/><text x="{x + 22}" y="116" '
                     'fill="#334155" font-family="system-ui,sans-serif" '
                     f'font-size="13">{escape_xml(label)}</text>')
    for index, row in enumerate(rows):
        top = 151 + index * 78
        title = escape_xml(row["label"])
        if row["not_measured"]:
            caption = "NOT MEASURED"
            caption_color = "#64748b"
        else:
            caption = f'{row["passed"]:,} / {CASE_COUNT:,} match Python'
            caption_color = "#dc2626" if row["failed"] else "#15803d"
        parts.append(f'<text x="43" y="{top + 17}" fill="#0f172a" '
                     'font-family="system-ui,sans-serif" font-size="17" '
                     f'font-weight="700">{title}</text>')
        parts.append(f'<text x="1038" y="{top + 17}" fill="{caption_color}" '
                     'text-anchor="end" font-family="system-ui,sans-serif" '
                     f'font-size="14" font-weight="600">{escape_xml(caption)}</text>')
        parts.append(f'<rect x="43" y="{top + 27}" width="996" height="24" '
                     'rx="6" fill="#e2e8f0"/>')
        cumulative = 0
        for state, color, label in colors:
            start = 43 + cumulative * 996 // CASE_COUNT
            cumulative += row[state]
            ending = 43 + cumulative * 996 // CASE_COUNT
            if ending > start:
                parts.append(f'<rect x="{start}" y="{top + 27}" '
                             f'width="{ending - start}" height="24" fill="{color}">'
                             f'<title>{title}: {row[state]:,} '
                             f'{escape_xml(label.lower())} out of {CASE_COUNT:,}</title></rect>')
    parts.extend([
        '<text x="43" y="475" fill="#475569" font-family="system-ui,sans-serif" '
        'font-size="12">These are 1,024 separately frozen safety checks; '
        'they do not change the original 2,807-check comparison.</text>',
        f'<text x="43" y="502" fill="#64748b" font-family="system-ui,sans-serif" '
        f'font-size="10">Manifest SHA-256: {manifest_hash} '
        f'· renderer SHA-256: {source_hash}</text>',
        "</svg>\n",
    ])
    return "\n".join(parts).encode("utf-8")


def build_documents(
    manifest: Mapping[str, Any], source_hash: str, manifest_hash: str,
    loader: Loader, digestor: Callable[[Any], str] = digest,
) -> tuple[bytes, bytes]:
    valid_hash(source_hash, "chart source")
    valid_hash(manifest_hash, "frozen chart manifest")
    baseline, rows = manifest_rows(manifest, loader, digestor)
    svg = make_svg(rows, source_hash, manifest_hash)
    summary = {
        "schema": SCHEMA + "-summary", "python": "3.14.6",
        "source_relative": SOURCE_RELATIVE, "source_sha256": source_hash,
        "frozen_v1_renderer_relative": FROZEN_V1_RELATIVE,
        "frozen_v1_renderer_sha256": FROZEN_V1_SHA256,
        "manifest_relative": MANIFEST_RELATIVE, "manifest_sha256": manifest_hash,
        "svg_relative": SVG_RELATIVE, "svg_sha256": hashlib.sha256(svg).hexdigest(),
        "oracle_relative": ORACLE_RELATIVE, "oracle_source_sha256": ORACLE_SHA256,
        "candidate_recorder_relative": RECORDER_RELATIVE,
        "candidate_recorder_sha256": RECORDER_SHA256,
        "baseline_recorder_relative": BASELINE_RECORDER_RELATIVE,
        "baseline_recorder_sha256": BASELINE_RECORDER_SHA256,
        "matrix_sha256": MATRIX_SHA256, "published_seed": PUBLISHED_SEED,
        "case_denominator": CASE_COUNT,
        "independent_of_original_2807_case_denominator": True,
        "baseline": baseline, "families": rows,
        "actual_candidate_workers": 0, "actual_candidate_imports": 0,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "final_holdout_opened": False,
        "winner_selected": False,
    }
    return svg, canonical(summary)


def read_archive(
    relative: str, expected: str, fields: frozenset[str],
    report_sha256: str, report_bytes: int,
) -> dict[str, Any]:
    with open_owned(relative, MAX_ARCHIVE_BYTES) as (descriptor, before):
        reader = VerifiedGzipReader(
            descriptor, before.st_size, expected, report_bytes, report_sha256,
        )
        result = StreamingObject(reader).select(fields)
        require(reader.finished, "the streamed archive was not fully authenticated")
        return result


def actual_loader(
    relative: str, expected: str, kind: str,
    plain_sha256: str | None, plain_bytes: int | None,
) -> dict[str, Any]:
    parts = safe_parts(relative)
    require(parts[:2] == ("experiments", "rust_public_practice_v1")
            and len(parts) == 3, "only exact frozen correctness evidence may be read")
    if kind == "receipt":
        require(relative.endswith("-publication-receipt.json")
                and plain_sha256 is None and plain_bytes is None,
                "only the exact pinned durable publication receipt is approved")
        return decode_document(read_frozen(relative, expected, MAX_RECEIPT_BYTES), relative)
    require(kind in {"baseline", "candidate"} and relative.endswith(".json.gz")
            and type(plain_sha256) is str and type(plain_bytes) is int,
            "only one exact complete frozen gzip report can be streamed")
    if kind == "baseline":
        require(relative == BASELINE_ARCHIVE_RELATIVE
                and expected == BASELINE_ARCHIVE_SHA256
                and plain_sha256 == BASELINE_REPORT_SHA256
                and plain_bytes == BASELINE_REPORT_BYTES,
                "the immutable authentic Python baseline archive was replaced")
    return read_archive(relative, expected,
                        BASELINE_FIELDS if kind == "baseline" else CANDIDATE_FIELDS,
                        plain_sha256, plain_bytes)


def atomic_output(directory: int, basename: str, value: bytes) -> None:
    require(basename in {safe_parts(SVG_RELATIVE)[-1],
                         safe_parts(SUMMARY_RELATIVE)[-1]}
            and type(value) is bytes and 0 < len(value) <= MAX_SOURCE_BYTES,
            "only two exact bounded chart outputs can be published")
    try:
        actual = os.open(
            basename, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory,
        )
    except FileNotFoundError:
        actual = None
    if actual is not None:
        try:
            info = os.fstat(actual)
            require(stat.S_ISREG(info.st_mode) and info.st_size == len(value),
                    "refusing to overwrite a non-identical existing chart")
            remaining = info.st_size
            blocks: list[bytes] = []
            while remaining:
                block = os.read(actual, min(CHUNK_BYTES, remaining))
                require(bool(block), "an existing chart was truncated")
                blocks.append(block)
                remaining -= len(block)
            require(os.read(actual, 1) == b"" and b"".join(blocks) == value,
                    "refusing to overwrite different existing chart bytes")
            return
        finally:
            os.close(actual)
    temporary = (".rebar-managed-buffer-overview-v1-" + basename + "-"
                 + str(os.getpid()) + "-" + hashlib.sha256(value).hexdigest()[:16])
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(temporary, flags, 0o644, dir_fd=directory)
    linked = False
    try:
        original = os.fstat(descriptor)
        require(stat.S_ISREG(original.st_mode), "the graph temporary is not regular")
        offset = 0
        while offset < len(value):
            written = os.write(descriptor, value[offset:])
            require(type(written) is int and written > 0,
                    "the generated graph was not fully written")
            offset += written
        os.fsync(descriptor)
        named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
        require((named.st_dev, named.st_ino)
                == (original.st_dev, original.st_ino),
                "the owned generated-graph temporary was replaced")
        os.link(temporary, basename, src_dir_fd=directory,
                dst_dir_fd=directory, follow_symlinks=False)
        linked = True
        os.fsync(directory)
        destination = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        require((destination.st_dev, destination.st_ino, destination.st_size)
                == (original.st_dev, original.st_ino, len(value)),
                "the atomically published graph was substituted")
        os.unlink(temporary, dir_fd=directory)
        os.fsync(directory)
    except BaseException:
        if not linked:
            try:
                named = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
                if (named.st_dev, named.st_ino) == (original.st_dev, original.st_ino):
                    os.unlink(temporary, dir_fd=directory)
                    os.fsync(directory)
            except (OSError, OverviewError):
                pass
        raise
    finally:
        os.close(descriptor)




PREVIOUS_SUMMARY_FIELDS = frozenset({
    "schema", "python", "source_relative", "source_sha256",
    "manifest_relative", "manifest_sha256", "svg_relative", "svg_sha256",
    "oracle_relative", "oracle_source_sha256", "candidate_recorder_relative",
    "candidate_recorder_sha256", "baseline_recorder_relative",
    "baseline_recorder_sha256", "matrix_sha256", "published_seed",
    "case_denominator", "independent_of_original_2807_case_denominator",
    "baseline", "families", "actual_candidate_workers",
    "actual_candidate_imports", "hidden_cases_read", "benchmark_files_read",
    "clock_samples", "timing_trials_run", "performance",
    "final_holdout_opened", "winner_selected",
})
V2_PREVIOUS_FIELDS = PREVIOUS_SUMMARY_FIELDS | frozenset({
    "frozen_v1_renderer_relative", "frozen_v1_renderer_sha256",
})


def validate_previous_outputs(
    old_svg: Any, old_summary: Any, previous_svg_sha256: Any,
    previous_summary_sha256: Any, current_source_sha256: str,
) -> dict[str, Any]:
    """Authenticate both real previous outputs, history, and frozen sources."""
    require(type(old_svg) is bytes and 0 < len(old_svg) <= MAX_SOURCE_BYTES
            and type(old_summary) is bytes
            and 0 < len(old_summary) <= MAX_SOURCE_BYTES,
            "authenticate both complete previous memory-safety graph files")
    expected_svg = valid_hash(previous_svg_sha256, "previous memory-safety SVG")
    expected_summary = valid_hash(previous_summary_sha256,
                                  "previous memory-safety summary")
    valid_hash(current_source_sha256, "current frozen V2 graph renderer")
    require(hashlib.sha256(old_svg).hexdigest() == expected_svg
            and hashlib.sha256(old_summary).hexdigest() == expected_summary,
            "the explicit previous memory-safety graph pair was substituted")
    previous = decode_document(old_summary, "complete previous memory-safety summary",
                               MAX_SOURCE_BYTES)
    names = set(previous)
    require(names in (PREVIOUS_SUMMARY_FIELDS, V2_PREVIOUS_FIELDS),
            "a complete prior V1 or V2 graph summary field was concealed")
    fixed_fields(previous, {
        "schema": SCHEMA + "-summary",
        "python": "3.14.6",
        "manifest_relative": MANIFEST_RELATIVE,
        "svg_relative": SVG_RELATIVE,
        "svg_sha256": expected_svg,
        "oracle_relative": ORACLE_RELATIVE,
        "oracle_source_sha256": ORACLE_SHA256,
        "candidate_recorder_relative": RECORDER_RELATIVE,
        "candidate_recorder_sha256": RECORDER_SHA256,
        "baseline_recorder_relative": BASELINE_RECORDER_RELATIVE,
        "baseline_recorder_sha256": BASELINE_RECORDER_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_denominator": CASE_COUNT,
        "independent_of_original_2807_case_denominator": True,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "final_holdout_opened": False,
        "winner_selected": False,
    }, "the genuine prior correctness-only memory-safety graph")
    prior_manifest = valid_hash(
        previous.get("manifest_sha256"), "previous frozen graph manifest",
    )
    require(len(set(prior_manifest)) > 1,
            "the previous graph used an invented all-identical manifest hash")
    if names == PREVIOUS_SUMMARY_FIELDS:
        fixed_fields(previous, {
            "source_relative": FROZEN_V1_RELATIVE,
            "source_sha256": FROZEN_V1_SHA256,
        }, "the exact independently frozen V1 graph ancestor")
    else:
        fixed_fields(previous, {
            "source_relative": SOURCE_RELATIVE,
            "source_sha256": current_source_sha256,
            "frozen_v1_renderer_relative": FROZEN_V1_RELATIVE,
            "frozen_v1_renderer_sha256": FROZEN_V1_SHA256,
        }, "the exact frozen V2 memory-safety graph ancestor")

    baseline = previous.get("baseline")
    require(type(baseline) is dict and set(baseline) == {
        "archive", "receipt", "baseline_records_sha256",
    } and baseline.get("baseline_records_sha256") == BASELINE_RECORDS_SHA256,
            "the previous chart replaced its genuine two-reference baseline")
    used: set[str] = set()
    archive_path, archive_sha = evidence_pin(baseline["archive"], used)
    receipt_path, receipt_sha = evidence_pin(baseline["receipt"], used)
    require((archive_path, archive_sha)
            == (BASELINE_ARCHIVE_RELATIVE, BASELINE_ARCHIVE_SHA256)
            and (receipt_path, receipt_sha)
            == (BASELINE_RECEIPT_RELATIVE, BASELINE_RECEIPT_SHA256),
            "the previous graph substituted its frozen baseline report or receipt")

    rows = previous.get("families")
    require(type(rows) is list and len(rows) == 4,
            "the previous graph omitted Python or a from-scratch engine")
    for index, expected in enumerate(("python", *FAMILY_ORDER)):
        item = rows[index]
        require(type(item) is dict and item.get("family") == expected
                and item.get("label")
                == {"python": "Python baseline", "rust": "Rust",
                    "c": "C", "zig": "Zig"}[expected]
                and type(item.get("case_denominator")) is int
                and item["case_denominator"] == CASE_COUNT
                and all(type(item.get(name)) is int and item[name] >= 0
                        for name in ("passed", "failed", "not_measured"))
                and item["passed"] + item["failed"] + item["not_measured"]
                == CASE_COUNT,
                "the previous graph concealed a family or changed its denominator")
        counts = item.get("mismatches_by_group")
        if expected == "python":
            require(set(item) == {
                "family", "label", "state", "passed", "failed", "not_measured",
                "case_denominator", "mismatches_by_group",
            } and item.get("state") == "RUN"
                    and item["passed"] == CASE_COUNT and item["failed"] == 0
                    and item["not_measured"] == 0
                    and type(counts) is dict and set(counts) == set(GROUPS)
                    and all(counts[group] == 0 for group in GROUPS),
                    "the previous graph forged the passing Python baseline")
            continue
        require(set(item) == {
            "family", "label", "candidate_source_sha256", "state",
            "case_denominator", "superseded", "passed", "failed",
            "not_measured", "report", "receipt", "mismatches_by_group",
        }, "a previous engine concealed a complete result or historical pair")
        valid_hash(item.get("candidate_source_sha256"),
                   "previous independently owned " + expected + " adapter")
        state = item.get("state")
        require(state in {"RUN", "NOT MEASURED"}
                and type(item.get("superseded")) is list,
                "a prior engine or preserved failure was misclassified")
        if state == "NOT MEASURED":
            require(item["passed"] == 0 and item["failed"] == 0
                    and item["not_measured"] == CASE_COUNT
                    and item.get("report") is None
                    and item.get("receipt") is None and counts is None,
                    "the previous graph disguised missing observations as results")
        else:
            require(item["not_measured"] == 0 and type(counts) is dict
                    and set(counts) == set(GROUPS)
                    and all(type(counts[group]) is int
                            and 0 <= counts[group] <= CASES_PER_GROUP
                            for group in GROUPS)
                    and sum(counts.values()) == item["failed"],
                    "the previous graph concealed an actual memory-safety failure")
            evidence_pin(item["report"], used)
            evidence_pin(item["receipt"], used)
        for old in item["superseded"]:
            require(type(old) is dict and set(old) == {
                "report", "receipt", "candidate_source_sha256", "passed", "failed",
            } and type(old.get("passed")) is int and old["passed"] >= 0
                    and type(old.get("failed")) is int and old["failed"] >= 0
                    and old["passed"] + old["failed"] == CASE_COUNT,
                    "a complete historical memory-safety failure was hidden")
            valid_hash(old.get("candidate_source_sha256"),
                       "historical independently owned " + expected + " source")
            evidence_pin(old["report"], used)
            evidence_pin(old["receipt"], used)
    return previous


def read_existing_output(
    directory: int, basename: str, operations: Any = os,
) -> tuple[bytes, os.stat_result] | None:
    require(basename in {safe_parts(SVG_RELATIVE)[-1],
                         safe_parts(SUMMARY_RELATIVE)[-1]},
            "only the two exact frozen memory-safety outputs may be read")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    try:
        descriptor = operations.open(basename, flags, dir_fd=directory)
    except FileNotFoundError:
        return None
    try:
        first = operations.fstat(descriptor)
        named = operations.stat(basename, dir_fd=directory,
                                follow_symlinks=False)
        require(stat.S_ISREG(first.st_mode)
                and (first.st_dev, first.st_ino, first.st_size)
                == (named.st_dev, named.st_ino, named.st_size)
                and 0 < first.st_size <= MAX_SOURCE_BYTES,
                "a previous graph became a symlink, special file, or oversized file")
        pieces: list[bytes] = []
        remaining = first.st_size
        while remaining:
            block = operations.read(descriptor, min(CHUNK_BYTES, remaining))
            require(type(block) is bytes and bool(block),
                    "the exact previous memory-safety graph was truncated")
            pieces.append(block)
            remaining -= len(block)
        require(operations.read(descriptor, 1) == b"",
                "the exact previous memory-safety graph gained hidden bytes")
        final = operations.fstat(descriptor)
        named = operations.stat(basename, dir_fd=directory,
                                follow_symlinks=False)
        require((first.st_dev, first.st_ino, first.st_size)
                == (final.st_dev, final.st_ino, final.st_size)
                == (named.st_dev, named.st_ino, named.st_size),
                "the previous memory-safety graph changed while authenticated")
        return b"".join(pieces), first
    finally:
        operations.close(descriptor)


def retained_directory(
    directory: int, identity: tuple[int, int], operations: Any,
) -> None:
    require(type(directory) is int and directory >= 0
            and type(identity) is tuple and len(identity) == 2
            and all(type(item) is int and item >= 0 for item in identity),
            "retain one exact no-follow graph directory")
    actual = operations.fstat(directory)
    require(stat.S_ISDIR(actual.st_mode)
            and (actual.st_dev, actual.st_ino) == identity,
            "the retained memory-safety graph directory was replaced")


def owned_stage(
    directory: int, basename: str, raw: bytes, operations: Any,
) -> tuple[str, tuple[int, int, int]]:
    require(basename in {safe_parts(SVG_RELATIVE)[-1],
                         safe_parts(SUMMARY_RELATIVE)[-1]}
            and type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES,
            "stage only the two exact bounded generated memory-safety files")
    temporary = (
        ".rebar-managed-buffer-overview-v2-stage-" + basename + "-"
        + str(os.getpid()) + "-" + hashlib.sha256(raw).hexdigest()[:20]
    )
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = operations.open(temporary, flags, 0o644, dir_fd=directory)
    initial = operations.fstat(descriptor)
    try:
        require(stat.S_ISREG(initial.st_mode),
                "the staged memory-safety output is not an owned regular file")
        offset = 0
        while offset < len(raw):
            written = operations.write(descriptor, raw[offset:])
            require(type(written) is int and written > 0,
                    "the complete staged memory-safety graph was not written")
            offset += written
        operations.fsync(descriptor)
        current = operations.fstat(descriptor)
        named = operations.stat(temporary, dir_fd=directory,
                                follow_symlinks=False)
        expected = (initial.st_dev, initial.st_ino, len(raw))
        require((current.st_dev, current.st_ino, current.st_size)
                == (named.st_dev, named.st_ino, named.st_size)
                == expected,
                "the fully flushed graph staging file was substituted")
        return temporary, expected
    except BaseException:
        try:
            named = operations.stat(temporary, dir_fd=directory,
                                    follow_symlinks=False)
            if (named.st_dev, named.st_ino) == (initial.st_dev, initial.st_ino):
                operations.unlink(temporary, dir_fd=directory)
                operations.fsync(directory)
        except (OSError, OverviewError):
            pass
        raise
    finally:
        operations.close(descriptor)


def remove_owned_name(
    directory: int, basename: str, identity: tuple[int, int, int],
    operations: Any,
) -> None:
    try:
        named = operations.stat(basename, dir_fd=directory,
                                follow_symlinks=False)
    except FileNotFoundError:
        return
    require(stat.S_ISREG(named.st_mode)
            and (named.st_dev, named.st_ino, named.st_size) == identity,
            "refusing to remove an unowned memory-safety transaction file")
    operations.unlink(basename, dir_fd=directory)


def approve_publication(
    old_svg: bytes | None, old_summary: bytes | None,
    new_svg: bytes, new_summary: bytes,
    replace_generated: bool, previous_svg_sha256: str | None,
    previous_summary_sha256: str | None, source_sha256: str,
) -> bool:
    require(type(new_svg) is bytes and 0 < len(new_svg) <= MAX_SOURCE_BYTES
            and type(new_summary) is bytes
            and 0 < len(new_summary) <= MAX_SOURCE_BYTES
            and type(replace_generated) is bool,
            "exact bounded graph bytes and an explicit refresh choice are mandatory")
    if not replace_generated:
        require(previous_svg_sha256 is None and previous_summary_sha256 is None,
                "previous-file pins cannot authorize an implicit graph refresh")
        require((old_svg is None or old_svg == new_svg)
                and (old_summary is None or old_summary == new_summary),
                "different existing graphs require explicit --replace-generated")
        return False
    validate_previous_outputs(
        old_svg, old_summary, previous_svg_sha256,
        previous_summary_sha256, source_sha256,
    )
    return old_svg != new_svg or old_summary != new_summary


def atomic_refresh_pair(
    directory: int, identity: tuple[int, int],
    old_svg: bytes, old_summary: bytes,
    new_svg: bytes, new_summary: bytes,
    operations: Any = os,
) -> None:
    """Commit both owned outputs or restore both exact previous outputs."""
    retained_directory(directory, identity, operations)
    pairs = (
        (safe_parts(SVG_RELATIVE)[-1], old_svg, new_svg),
        (safe_parts(SUMMARY_RELATIVE)[-1], old_summary, new_summary),
    )
    stages: dict[str, tuple[str, tuple[int, int, int]]] = {}
    backups: dict[str, tuple[str, tuple[int, int, int]]] = {}
    committed: list[str] = []
    expected_new = {name: new for name, _, new in pairs}
    expected_old = {name: old for name, old, _ in pairs}
    try:
        for name, previous, updated in pairs:
            current = read_existing_output(directory, name, operations)
            require(current is not None and current[0] == previous,
                    "the authenticated previous graph changed before staging")
            stages[name] = owned_stage(directory, name, updated, operations)
            retained_directory(directory, identity, operations)
        for name, previous, _ in pairs:
            observed = read_existing_output(directory, name, operations)
            require(observed is not None and observed[0] == previous,
                    "the authenticated old graph changed before its backup")
            backup = (
                ".rebar-managed-buffer-overview-v2-backup-" + name + "-"
                + str(os.getpid()) + "-"
                + hashlib.sha256(previous).hexdigest()[:20]
            )
            operations.link(
                name, backup, src_dir_fd=directory, dst_dir_fd=directory,
                follow_symlinks=False,
            )
            info = operations.stat(backup, dir_fd=directory,
                                   follow_symlinks=False)
            original = observed[1]
            require(stat.S_ISREG(info.st_mode)
                    and (info.st_dev, info.st_ino, info.st_size)
                    == (original.st_dev, original.st_ino, original.st_size),
                    "the rollback backup was not linked to the exact old graph")
            backups[name] = (backup, (info.st_dev, info.st_ino, info.st_size))
            retained_directory(directory, identity, operations)
        operations.fsync(directory)
        for name, previous, updated in pairs:
            current = read_existing_output(directory, name, operations)
            require(current is not None and current[0] == previous,
                    "the old graph changed after the rollback backup")
            stage_name, stage_identity = stages[name]
            info = operations.stat(stage_name, dir_fd=directory,
                                   follow_symlinks=False)
            require((info.st_dev, info.st_ino, info.st_size) == stage_identity,
                    "a fully staged memory-safety graph was substituted")
            operations.replace(
                stage_name, name,
                src_dir_fd=directory, dst_dir_fd=directory,
            )
            committed.append(name)
            observed = read_existing_output(directory, name, operations)
            require(observed is not None and observed[0] == updated,
                    "the replaced graph failed its complete byte readback")
            retained_directory(directory, identity, operations)
        operations.fsync(directory)
        for name, _, updated in pairs:
            observed = read_existing_output(directory, name, operations)
            require(observed is not None and observed[0] == updated,
                    "the committed graph pair failed its exact final readback")
        retained_directory(directory, identity, operations)
    except BaseException as original_error:
        rollback_error: BaseException | None = None
        for name in reversed(committed):
            try:
                observed = read_existing_output(directory, name, operations)
                require(observed is not None
                        and observed[0] == expected_new[name],
                        "refusing to roll back an externally changed graph")
                backup, backup_identity = backups[name]
                actual = operations.stat(backup, dir_fd=directory,
                                         follow_symlinks=False)
                require((actual.st_dev, actual.st_ino, actual.st_size)
                        == backup_identity,
                        "the verified graph rollback backup was substituted")
                operations.replace(
                    backup, name,
                    src_dir_fd=directory, dst_dir_fd=directory,
                )
                restored = read_existing_output(directory, name, operations)
                require(restored is not None
                        and restored[0] == expected_old[name],
                        "the complete original graph could not be restored")
                del backups[name]
            except BaseException as error:
                rollback_error = error
                break
        if rollback_error is None:
            try:
                for name, (backup, backup_identity) in list(backups.items()):
                    remove_owned_name(directory, backup, backup_identity,
                                      operations)
                    del backups[name]
                for name, (stage, stage_identity) in list(stages.items()):
                    if name not in committed:
                        remove_owned_name(directory, stage, stage_identity,
                                          operations)
                operations.fsync(directory)
                for name, previous, _ in pairs:
                    current = read_existing_output(directory, name, operations)
                    require(current is not None and current[0] == previous,
                            "the transaction failed to restore the full old pair")
            except BaseException as error:
                rollback_error = error
        if rollback_error is not None:
            raise OverviewError(
                "memory-safety graph refresh failed; preserve owned rollback "
                "backups because complete restoration could not be verified"
            ) from rollback_error
        raise original_error
    for name, (backup, backup_identity) in list(backups.items()):
        remove_owned_name(directory, backup, backup_identity, operations)
        del backups[name]
    operations.fsync(directory)
    for name, _, updated in pairs:
        observed = read_existing_output(directory, name, operations)
        require(observed is not None and observed[0] == updated,
                "the safely refreshed memory-safety graph pair was changed")



def render(
    source_hash: str, manifest_relative: str, manifest_hash: str,
    replace_generated: bool = False,
    previous_svg_sha256: str | None = None,
    previous_summary_sha256: str | None = None,
) -> dict[str, Any]:
    verify_runtime()
    source_hash = valid_hash(source_hash, "frozen V2 memory-safety renderer")
    manifest_hash = valid_hash(manifest_hash, "frozen memory-safety manifest")
    require(manifest_relative == MANIFEST_RELATIVE,
            "only the exact unchanged V1 memory-safety manifest may be rendered")
    for relative, pinned in (
        (SOURCE_RELATIVE, source_hash),
        (FROZEN_V1_RELATIVE, FROZEN_V1_SHA256),
        (ORACLE_RELATIVE, ORACLE_SHA256),
        (BASELINE_RECORDER_RELATIVE, BASELINE_RECORDER_SHA256),
        (RECORDER_RELATIVE, RECORDER_SHA256),
        (ORIGINAL_V5_RELATIVE, ORIGINAL_V5_SHA256),
    ):
        read_frozen(relative, pinned, MAX_SOURCE_BYTES)
    manifest = decode_document(
        read_frozen(MANIFEST_RELATIVE, manifest_hash, MAX_SOURCE_BYTES),
        "exact unchanged frozen lifetime chart manifest", MAX_SOURCE_BYTES,
    )
    svg, summary = build_documents(
        manifest, source_hash, manifest_hash, actual_loader,
    )
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_DIRECTORY", 0)
    )
    opened: list[int] = []
    refreshed = False
    try:
        current = os.open(ROOT, directory_flags)
        opened.append(current)
        for part in ("docs", "evidence"):
            current = os.open(part, directory_flags, dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "the exact generated memory-safety graph parent changed")
        directory_info = os.fstat(current)
        identity = (directory_info.st_dev, directory_info.st_ino)
        old_svg_result = read_existing_output(
            current, safe_parts(SVG_RELATIVE)[-1],
        )
        old_summary_result = read_existing_output(
            current, safe_parts(SUMMARY_RELATIVE)[-1],
        )
        old_svg = old_svg_result[0] if old_svg_result is not None else None
        old_summary = (
            old_summary_result[0] if old_summary_result is not None else None
        )
        refreshed = approve_publication(
            old_svg, old_summary, svg, summary, replace_generated,
            previous_svg_sha256, previous_summary_sha256, source_hash,
        )
        if replace_generated and refreshed:
            require(type(old_svg) is bytes and type(old_summary) is bytes,
                    "the exact previous generated chart pair is mandatory")
            atomic_refresh_pair(
                current, identity, old_svg, old_summary, svg, summary,
            )
        elif not replace_generated:
            atomic_output(current, safe_parts(SVG_RELATIVE)[-1], svg)
            atomic_output(current, safe_parts(SUMMARY_RELATIVE)[-1], summary)
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)
    verify_runtime()
    parsed = decode_document(summary, "complete refreshed safety summary",
                             MAX_SOURCE_BYTES)
    return {
        "schema": SCHEMA + "-rendered",
        "status": "PASS",
        "source_sha256": source_hash,
        "frozen_v1_renderer_relative": FROZEN_V1_RELATIVE,
        "frozen_v1_renderer_sha256": FROZEN_V1_SHA256,
        "manifest_sha256": manifest_hash,
        "svg_relative": SVG_RELATIVE,
        "svg_sha256": hashlib.sha256(svg).hexdigest(),
        "summary_relative": SUMMARY_RELATIVE,
        "summary_sha256": hashlib.sha256(summary).hexdigest(),
        "case_denominator": CASE_COUNT,
        "published_seed": PUBLISHED_SEED,
        "replaced_generated_pair": refreshed,
        "rows": [{
            "family": row["family"],
            "passed": row["passed"],
            "failed": row["failed"],
            "not_measured": row["not_measured"],
        } for row in parsed["families"]],
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "final_holdout_opened": False,
        "winner_selected": False,
    }


class SourceOnlyBoundary:
    def __init__(self) -> None:
        self.originals: list[tuple[Any, str, Any]] = []
        self.blocked = {
            "reads": 0, "writes": 0, "workers": 0,
            "imports": 0, "threads": 0, "clocks": 0,
        }

    def install(self, owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        old = getattr(owner, name)
        self.originals.append((owner, name, old))

        def denied(*args: Any, **kwargs: Any) -> Any:
            actual = category
            if category == "reads":
                mode = args[1] if len(args) > 1 else kwargs.get("mode", "r")
                if (type(mode) is str and any(item in mode for item in "wax+")) or (
                    type(mode) is int and bool(mode & (
                        os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
                    ))
                ):
                    actual = "writes"
            self.blocked[actual] += 1
            raise SourceOnlyError("source-only chart controls forbid " + actual)

        setattr(owner, name, denied)

    def __enter__(self) -> SourceOnlyBoundary:
        for owner, name, category in (
            (builtins, "open", "reads"), (io, "open", "reads"),
            (os, "open", "reads"), (os, "stat", "reads"),
            (os, "lstat", "reads"), (os, "scandir", "reads"),
            (os, "listdir", "reads"), (os, "write", "writes"),
            (os, "replace", "writes"), (os, "rename", "writes"),
            (os, "link", "writes"), (os, "unlink", "writes"),
            (os, "remove", "writes"), (os, "fsync", "writes"),
            (subprocess, "run", "workers"), (subprocess, "Popen", "workers"),
            (os, "system", "workers"), (os, "posix_spawn", "workers"),
            (importlib, "import_module", "imports"),
            (threading.Thread, "start", "threads"),
            (time, "time", "clocks"), (time, "time_ns", "clocks"),
            (time, "monotonic", "clocks"), (time, "monotonic_ns", "clocks"),
            (time, "perf_counter", "clocks"),
            (time, "perf_counter_ns", "clocks"),
        ):
            self.install(owner, name, category)
        return self

    def __exit__(self, error_type: Any, error: Any, trace: Any) -> bool:
        del error_type, error, trace
        for owner, name, original in reversed(self.originals):
            setattr(owner, name, original)
        self.originals.clear()
        return False


def synthetic_stream(
    raw: bytes, *, archive: bytes | None = None,
    archive_sha256: str | None = None, report_sha256: str | None = None,
    report_bytes: int | None = None,
    fields: frozenset[str] = frozenset({"proof", "value"}),
) -> dict[str, Any]:
    """Exercise the real streaming reader against a fake, in-memory fd only."""
    require(type(raw) is bytes and bool(raw),
            "complete in-memory original gzip controls are mandatory")
    if archive is None:
        compressor = zlib.compressobj(level=9, wbits=16 + zlib.MAX_WBITS)
        archive = compressor.compress(raw) + compressor.flush()
    require(type(archive) is bytes and bool(archive),
            "a genuine in-memory single gzip member is mandatory")
    archive_hash = (hashlib.sha256(archive).hexdigest()
                    if archive_sha256 is None else archive_sha256)
    plain_hash = (hashlib.sha256(raw).hexdigest()
                  if report_sha256 is None else report_sha256)
    plain_bytes = len(raw) if report_bytes is None else report_bytes
    position = 0
    descriptor = -917_024
    previous = os.read

    def read_memory(selected: int, count: int) -> bytes:
        nonlocal position
        require(selected == descriptor and type(count) is int and count > 0,
                "a synthetic gzip control attempted a real file descriptor")
        block = archive[position:position + count]
        position += len(block)
        return block

    os.read = read_memory
    try:
        stream = VerifiedGzipReader(
            descriptor, len(archive), archive_hash, plain_bytes, plain_hash,
        )
        value = StreamingObject(stream).select(fields)
        require(stream.finished and position == len(archive),
                "an in-memory gzip stream was not completely authenticated")
        return value
    finally:
        os.read = previous


def synthetic_owner(relative: str, expected: str, index: int) -> dict[str, Any]:
    return {"relative": relative, "sha256": expected,
            "bytes": 4096 + index, "device": 7, "inode": 1000 + index}


def synthetic_guard(family: str) -> dict[str, Any]:
    ffi = FAMILY_SPECS[family][4]
    result = {name: True for name in GUARD_TRUE}
    result.update({
        "public_type_names_used_for_ownership": False,
        "actual_method_guard_checks": 2 * CASE_COUNT,
        "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
        "owned_native_ffi_allowed": ffi,
        "trusted_stdlib_ctypes_preloaded": ffi,
        "trusted_stdlib_ctypes_builtin_verified": ffi,
        "trusted_stdlib_ctypes_pythonapi_initialized": ffi,
        "trusted_stdlib_ctypes_source_sha256": TRUSTED_CTYPES_SHA256 if ffi else None,
        "cached_original_matcher_descendant_count": 0,
        "cached_original_holder_count": 0,
        "owned_ctypes_load_count": 1 if ffi else 0,
        "owned_ctypes_symbol_count": 2 if ffi else 0,
    })
    return result


def synthetic_fixtures() -> tuple[dict[str, Any], dict[tuple[str, str], dict[str, Any]], Callable[[Any], str]]:
    outcome = {
        "status": "return", "stage": "synthetic", "value": {"type": "none"},
        "exception": None, "events": [], "checkpoints": [],
        "callbacks": [], "warnings": [],
    }
    baseline = [{
        "case": "managed-buffer-lifetime.v1." + format(index, "04d"),
        "group": GROUPS[index // CASES_PER_GROUP],
        "variant": index % CASES_PER_GROUP,
        "outcome": dict(outcome),
    } for index in range(CASE_COUNT)]

    def synthetic_digest(value: Any) -> str:
        return BASELINE_RECORDS_SHA256 if value == baseline else digest(value)

    source_hashes = {"rust": "12" * 32, "c": "34" * 32, "zig": "56" * 32}
    base_receipt = {
        "schema": "rebar-independent-managed-buffer-lifetime-v1-recorder-durable-publication-receipt",
        "status": "PASS", "baseline_result_status": "PASS",
        "label": "shared-suite-v1", "python": "3.14.6",
        "oracle_relative": ORACLE_RELATIVE, "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256, "published_seed": PUBLISHED_SEED,
        "group_count": len(GROUPS), "cases_per_group": CASES_PER_GROUP,
        "case_count": CASE_COUNT, "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "baseline_reference_pids": [82, 83], "actual_reference_workers": 2,
        "actual_candidate_workers": 0, "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
        "report_relative": BASELINE_REPORT_RELATIVE,
        "report_sha256": BASELINE_REPORT_SHA256,
        "report_bytes": BASELINE_REPORT_BYTES,
        "report_file_fsync_completed": True,
        "report_directory_fsync_completed": True,
        "report_atomic_no_overwrite_link": True,
        "report_complete_readback_verified": True,
        "receipt_relative": BASELINE_RECEIPT_RELATIVE,
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    base_report = {
        "schema": "rebar-independent-managed-buffer-lifetime-v1-recorder-complete-baseline-report",
        "status": "PASS", "label": "shared-suite-v1", "python": "3.14.6",
        "oracle_source_sha256": ORACLE_SHA256, "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED, "group_count": len(GROUPS),
        "cases_per_group": CASES_PER_GROUP, "case_count": CASE_COUNT,
        "groups": list(GROUPS), "source_closure_before": {"synthetic": True},
        "source_closure_after": {"synthetic": True}, "source_closure_unchanged": True,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "baseline_reference_pids": [82, 83],
        "validated_reference_a_case_count": CASE_COUNT,
        "validated_reference_b_case_count": CASE_COUNT,
        "reference_a_records": baseline, "reference_b_records": baseline,
        "actual_reference_workers": 2, "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_baseline_controller_invocations": 1,
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    family = "c"
    adapter, engine, bridge, sources, _ = FAMILY_SPECS[family]
    closure: dict[str, dict[str, Any]] = {}
    for index, path in enumerate((*sources, engine, bridge), start=1):
        if path not in closure:
            chosen = source_hashes[family] if path == adapter else hashlib.sha256(path.encode("ascii")).hexdigest()
            closure[path] = synthetic_owner(path, chosen, index)
    changed = []
    mismatches = []
    counts = {group: 0 for group in GROUPS}
    for index, original in enumerate(baseline):
        record = dict(original)
        if index < 237:
            different = dict(original["outcome"])
            different["stage"] = "synthetic-incompatible"
            record["outcome"] = different
            mismatch = {
                "case": original["case"], "group": original["group"],
                "input": {"case": original["case"], "group": original["group"],
                          "variant": original["variant"], "seed": PUBLISHED_SEED},
                "baseline_outcome": original["outcome"],
                "candidate_outcome": different,
            }
            mismatches.append(mismatch)
            counts[original["group"]] += 1
        changed.append(record)
    record_hash = digest(changed)
    report_path = EVIDENCE_DIRECTORY + "/c-managed-buffer-lifetime-v1-synthetic.json.gz"
    receipt_path = (EVIDENCE_DIRECTORY
                    + "/c-managed-buffer-lifetime-v1-synthetic-publication-receipt.json")
    report_hash = "78" * 32
    receipt_hash = "9a" * 32
    plain_hash = "bc" * 32
    report = {
        "schema": "rebar-independent-managed-buffer-candidate-recorder-v1-complete-candidate-report",
        "status": "FAIL", "python": "3.14.6", "candidate_family": family,
        "label": "synthetic", "recorder_source_sha256": RECORDER_SHA256,
        "managed_oracle_relative": ORACLE_RELATIVE,
        "managed_oracle_sha256": ORACLE_SHA256,
        "baseline_recorder_relative": BASELINE_RECORDER_RELATIVE,
        "baseline_recorder_sha256": BASELINE_RECORDER_SHA256,
        "original_v5_relative": ORIGINAL_V5_RELATIVE,
        "original_v5_sha256": ORIGINAL_V5_SHA256,
        "matrix_sha256": MATRIX_SHA256, "published_seed": PUBLISHED_SEED,
        "group_count": len(GROUPS), "cases_per_group": CASES_PER_GROUP,
        "case_count": CASE_COUNT, "groups": list(GROUPS),
        "baseline_receipt_relative": BASELINE_RECEIPT_RELATIVE,
        "baseline_receipt_sha256": BASELINE_RECEIPT_SHA256,
        "baseline_archive_relative": BASELINE_ARCHIVE_RELATIVE,
        "baseline_archive_sha256": BASELINE_ARCHIVE_SHA256,
        "baseline_uncompressed_report_sha256": BASELINE_REPORT_SHA256,
        "baseline_uncompressed_report_bytes": BASELINE_REPORT_BYTES,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "baseline_reference_pids": [82, 83],
        "candidate_owner_before": closure, "candidate_owner_after": closure,
        "candidate_owner_unchanged": True,
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": CASE_COUNT,
        "candidate_records_sha256": record_hash, "candidate_records": changed,
        "baseline_records": baseline, "mismatch_count": len(mismatches),
        "all_mismatches": mismatches, "mismatches_by_group": counts,
        "all_mismatches_preserved": True, "matcher_guard": synthetic_guard(family),
        "actual_method_guard_checks": 2 * CASE_COUNT,
        "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
        "actual_reference_workers": 0, "validated_prior_reference_workers": 2,
        "actual_candidate_workers": 1, "actual_candidate_imports": 3,
        "actual_candidate_process_invocations": 1, "actual_candidate_pid": 81001,
        "actual_candidate_process_returncode": 0,
        "actual_candidate_process_signal": None,
        "actual_candidate_process_timed_out": False,
        "actual_candidate_process_spawn_error": None,
        "all_failure_reasons": ["synthetic incompatibilities"], "failure_count": 1,
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    receipt = {
        "schema": "rebar-independent-managed-buffer-candidate-recorder-v1-durable-publication-receipt",
        "status": "PASS", "candidate_result_status": "FAIL",
        "python": "3.14.6", "candidate_family": family, "label": "synthetic",
        "recorder_source_sha256": RECORDER_SHA256,
        "managed_oracle_sha256": ORACLE_SHA256,
        "baseline_recorder_sha256": BASELINE_RECORDER_SHA256,
        "original_v5_sha256": ORIGINAL_V5_SHA256,
        "matrix_sha256": MATRIX_SHA256, "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "baseline_receipt_relative": BASELINE_RECEIPT_RELATIVE,
        "baseline_receipt_sha256": BASELINE_RECEIPT_SHA256,
        "baseline_archive_relative": BASELINE_ARCHIVE_RELATIVE,
        "baseline_archive_sha256": BASELINE_ARCHIVE_SHA256,
        "baseline_uncompressed_report_sha256": BASELINE_REPORT_SHA256,
        "baseline_uncompressed_report_bytes": BASELINE_REPORT_BYTES,
        "baseline_records_sha256": BASELINE_RECORDS_SHA256,
        "validated_baseline_record_count": CASE_COUNT,
        "validated_candidate_record_count": CASE_COUNT,
        "candidate_records_sha256": record_hash,
        "mismatch_count": len(mismatches), "mismatches_by_group": counts,
        "all_mismatches_preserved": True,
        "actual_method_guard_checks": 2 * CASE_COUNT,
        "actual_warning_registry_guard_checks": 2 * CASE_COUNT,
        "actual_candidate_workers": 1, "actual_candidate_imports": 3,
        "actual_candidate_process_invocations": 1,
        "candidate_owner_before": closure, "candidate_owner_after": closure,
        "candidate_owner_unchanged": True,
        "report_relative": report_path, "report_sha256": report_hash,
        "report_bytes": 4096, "report_uncompressed_sha256": plain_hash,
        "report_uncompressed_bytes": 12345,
        "report_compression": "gzip-mtime-zero-level-9",
        "report_file_fsync_completed": True,
        "report_directory_fsync_completed": True,
        "report_atomic_no_overwrite_link": True,
        "report_complete_readback_verified": True,
        "receipt_relative": receipt_path,
        "approved_fresh_path_count": 2,
        "fresh_paths_checked_before_candidate": True,
        "clock_samples": 0, "timing_trials_run": 0,
        "benchmark_files_read": 0, "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    manifest = {
        "schema": SCHEMA + "-inputs", "python": "3.14.6",
        "case_denominator": CASE_COUNT,
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "baseline": {
            "archive": {"relative": BASELINE_ARCHIVE_RELATIVE,
                        "sha256": BASELINE_ARCHIVE_SHA256},
            "receipt": {"relative": BASELINE_RECEIPT_RELATIVE,
                        "sha256": BASELINE_RECEIPT_SHA256},
        },
        "families": [
            {"family": "rust", "candidate_source_sha256": source_hashes["rust"],
             "state": "NOT MEASURED", "report": None, "receipt": None,
             "superseded": []},
            {"family": "c", "candidate_source_sha256": source_hashes["c"],
             "state": "RUN",
             "report": {"relative": report_path, "sha256": report_hash},
             "receipt": {"relative": receipt_path, "sha256": receipt_hash},
             "superseded": []},
            {"family": "zig", "candidate_source_sha256": source_hashes["zig"],
             "state": "NOT MEASURED", "report": None, "receipt": None,
             "superseded": []},
        ],
    }
    evidence = {
        (BASELINE_RECEIPT_RELATIVE, BASELINE_RECEIPT_SHA256): base_receipt,
        (BASELINE_ARCHIVE_RELATIVE, BASELINE_ARCHIVE_SHA256): base_report,
        (receipt_path, receipt_hash): receipt,
        (report_path, report_hash): report,
    }
    return manifest, evidence, synthetic_digest


class SyntheticPublication:
    """Exercise the real two-file transaction with only fake descriptors."""

    def __init__(
        self, svg: bytes, summary: bytes, *,
        fail_replace: int | None = None, fail_stage_write: bool = False,
    ) -> None:
        self.directory = 71
        self.next_descriptor = 81
        self.next_inode = 10_000
        self.files: dict[str, dict[str, Any]] = {}
        self.descriptors: dict[int, dict[str, Any]] = {}
        self.replace_count = 0
        self.fail_replace = fail_replace
        self.fail_stage_write = fail_stage_write
        self.failed_once = False
        self.sync_count = 0
        self.install(safe_parts(SVG_RELATIVE)[-1], svg)
        self.install(safe_parts(SUMMARY_RELATIVE)[-1], summary)

    def install(self, name: str, raw: bytes) -> None:
        self.next_inode += 1
        self.files[name] = {
            "raw": bytearray(raw), "device": 7, "inode": self.next_inode,
        }

    def info(self, entry: Mapping[str, Any]) -> os.stat_result:
        return os.stat_result((
            stat.S_IFREG | 0o644,
            entry["inode"], entry["device"], 1, 0, 0,
            len(entry["raw"]), 0, 0, 0,
        ))

    def open(
        self, name: str, flags: int, mode: int = 0o644, *,
        dir_fd: int | None = None,
    ) -> int:
        del mode
        require(dir_fd == self.directory and type(name) is str,
                "the synthetic transaction escaped its fake directory")
        if flags & os.O_CREAT:
            require(flags & os.O_EXCL and name not in self.files,
                    "a synthetic staging file was not exclusive")
            self.install(name, b"")
        elif name not in self.files:
            raise FileNotFoundError(name)
        self.next_descriptor += 1
        descriptor = self.next_descriptor
        self.descriptors[descriptor] = {
            "entry": self.files[name], "offset": 0,
            "writable": bool(flags & (os.O_WRONLY | os.O_RDWR)),
        }
        return descriptor

    def fstat(self, descriptor: int) -> os.stat_result:
        if descriptor == self.directory:
            return os.stat_result((
                stat.S_IFDIR | 0o755, 7001, 7, 1, 0, 0, 0, 0, 0, 0,
            ))
        require(descriptor in self.descriptors,
                "a synthetic transaction used a genuine descriptor")
        return self.info(self.descriptors[descriptor]["entry"])

    def stat(
        self, name: str, *, dir_fd: int | None = None,
        follow_symlinks: bool = False,
    ) -> os.stat_result:
        require(dir_fd == self.directory and follow_symlinks is False,
                "a synthetic transaction followed a genuine path")
        if name not in self.files:
            raise FileNotFoundError(name)
        return self.info(self.files[name])

    def read(self, descriptor: int, count: int) -> bytes:
        require(descriptor in self.descriptors
                and type(count) is int and count > 0,
                "a synthetic transaction attempted a genuine read")
        opened = self.descriptors[descriptor]
        start = opened["offset"]
        raw = bytes(opened["entry"]["raw"][start:start + count])
        opened["offset"] = start + len(raw)
        return raw

    def write(self, descriptor: int, raw: bytes) -> int:
        require(descriptor in self.descriptors
                and self.descriptors[descriptor]["writable"]
                and type(raw) is bytes,
                "a synthetic transaction attempted a genuine graph write")
        if self.fail_stage_write and not self.failed_once:
            self.failed_once = True
            raise OSError("synthetic staged-graph write failure")
        opened = self.descriptors[descriptor]
        opened["entry"]["raw"].extend(raw)
        opened["offset"] += len(raw)
        return len(raw)

    def fsync(self, descriptor: int) -> None:
        require(descriptor == self.directory or descriptor in self.descriptors,
                "a synthetic transaction synchronized a genuine descriptor")
        self.sync_count += 1

    def close(self, descriptor: int) -> None:
        require(descriptor in self.descriptors,
                "a synthetic transaction closed a genuine descriptor")
        del self.descriptors[descriptor]

    def link(
        self, source: str, destination: str, *,
        src_dir_fd: int | None = None, dst_dir_fd: int | None = None,
        follow_symlinks: bool = False,
    ) -> None:
        require(src_dir_fd == dst_dir_fd == self.directory
                and follow_symlinks is False and source in self.files
                and destination not in self.files,
                "a synthetic backup escaped its owned in-memory graph")
        self.files[destination] = self.files[source]

    def replace(
        self, source: str, destination: str, *,
        src_dir_fd: int | None = None, dst_dir_fd: int | None = None,
    ) -> None:
        require(src_dir_fd == dst_dir_fd == self.directory
                and source in self.files and destination in self.files,
                "a synthetic replacement escaped its in-memory graph pair")
        if source.startswith(".rebar-managed-buffer-overview-v2-stage-"):
            self.replace_count += 1
            if self.fail_replace == self.replace_count and not self.failed_once:
                self.failed_once = True
                raise OSError("synthetic atomic graph replacement failure")
        self.files[destination] = self.files.pop(source)

    def unlink(self, name: str, *, dir_fd: int | None = None) -> None:
        require(dir_fd == self.directory and name in self.files
                and name.startswith(".rebar-managed-buffer-overview-v2-"),
                "a synthetic transaction attempted to delete a genuine file")
        del self.files[name]

    def pair(self) -> tuple[bytes, bytes]:
        return (
            bytes(self.files[safe_parts(SVG_RELATIVE)[-1]]["raw"]),
            bytes(self.files[safe_parts(SUMMARY_RELATIVE)[-1]]["raw"]),
        )

    def only_outputs_remain(self) -> bool:
        return (set(self.files)
                == {safe_parts(SVG_RELATIVE)[-1],
                    safe_parts(SUMMARY_RELATIVE)[-1]}
                and not self.descriptors)




def self_test() -> dict[str, Any]:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True,
            "source-only chart tests require isolated pinned Python 3.14.6")
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, value: Any) -> None:
        require(type(name) is str and name not in accepted and bool(value),
                "a synthetic chart positive control failed: " + name)
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(type(name) is str and name not in rejected and callable(action),
                "a synthetic chart rejection was duplicated")
        try:
            action()
        except (OverviewError, OSError, TypeError, ValueError, KeyError, IndexError, zlib.error):
            rejected.append(name)
            return
        raise OverviewError("a forged chart control was accepted: " + name)

    with SourceOnlyBoundary() as boundary:
        stream_document = {"proof": "in-memory only", "value": [1, 2, 3]}
        stream_raw = canonical(stream_document)
        compressor = zlib.compressobj(level=9, wbits=16 + zlib.MAX_WBITS)
        stream_archive = compressor.compress(stream_raw) + compressor.flush()
        accept("authenticate-the-real-single-member-gzip-stream-in-memory",
               synthetic_stream(stream_raw, archive=stream_archive) == stream_document)
        reject("reject-a-clipped-single-member-gzip-stream",
               lambda: synthetic_stream(stream_raw, archive=stream_archive[:-1]))
        reject("reject-hidden-gzip-trailing-bytes",
               lambda: synthetic_stream(stream_raw, archive=stream_archive + b"hidden"))
        reject("reject-an-unapproved-second-gzip-member",
               lambda: synthetic_stream(stream_raw,
                                        archive=stream_archive + stream_archive))
        corrupt_crc = stream_archive[:-1] + bytes((stream_archive[-1] ^ 1,))
        reject("reject-a-corrupted-gzip-crc-or-size-footer",
               lambda: synthetic_stream(stream_raw, archive=corrupt_crc))
        reject("reject-a-substituted-compressed-gzip-digest",
               lambda: synthetic_stream(stream_raw, archive=stream_archive,
                                        archive_sha256="0" * 64))
        reject("reject-a-substituted-uncompressed-report-digest",
               lambda: synthetic_stream(stream_raw, archive=stream_archive,
                                        report_sha256="0" * 64))
        reject("reject-an-overexpanded-compressed-report",
               lambda: synthetic_stream(stream_raw, archive=stream_archive,
                                        report_bytes=len(stream_raw) - 1))
        reject("reject-a-clipped-uncompressed-report",
               lambda: synthetic_stream(stream_raw, archive=stream_archive,
                                        report_bytes=len(stream_raw) + 1))
        reject("reject-duplicate-compressed-report-fields",
               lambda: synthetic_stream(b'{"proof":1,"proof":2,"value":[]}\n'))
        reject("reject-an-omitted-compressed-report-field",
               lambda: synthetic_stream(b'{"proof":"missing value"}\n'))

        manifest, evidence, digestor = synthetic_fixtures()

        def loader(
            relative: str, expected: str, kind: str,
            plain_sha256: str | None, plain_bytes: int | None,
        ) -> dict[str, Any]:
            require(kind in {"receipt", "baseline", "candidate"},
                    "an actual evidence kind was forged")
            if kind == "receipt":
                require(plain_sha256 is None and plain_bytes is None,
                        "a synthetic receipt pretended to be compressed")
            else:
                require(type(plain_sha256) is str and type(plain_bytes) is int,
                        "a synthetic gzip omitted original authentication")
            value = evidence.get((relative, expected))
            require(type(value) is dict, "synthetic evidence pin was substituted")
            return value

        baseline, rows = manifest_rows(manifest, loader, digestor)
        accept("authenticate-the-independent-two-reference-baseline", bool(baseline))
        accept("show-all-four-original-and-from-scratch-engines",
               [row["family"] for row in rows] == ["python", "rust", "c", "zig"])
        accept("preserve-the-separate-1024-case-denominator",
               all(row["case_denominator"] == CASE_COUNT for row in rows))
        accept("never-credit-publication-success-as-candidate-correctness",
               rows[2]["passed"] == 787 and rows[2]["failed"] == 237)
        accept("keep-unobserved-rust-and-zig-explicitly-gray",
               rows[1]["not_measured"] == CASE_COUNT
               and rows[3]["not_measured"] == CASE_COUNT)
        svg, summary = build_documents(manifest, "de" * 32, digest(manifest),
                                       loader, digestor)
        decoded = decode_document(summary, "synthetic chart summary", MAX_SOURCE_BYTES)
        accept("render-a-complete-deterministic-accessible-safety-chart",
               b"<svg" in svg and b"NOT MEASURED" in svg
               and b"787 / 1,024 match Python" in svg
               and b"Memory and buffer safety" in svg)
        accept("preserve-all-real-losses-in-canonical-summary",
               decoded["families"][2]["failed"] == 237
               and decoded["performance"] == "NOT MEASURED"
               and decoded["independent_of_original_2807_case_denominator"] is True)
        accept("repeat-identical-graph-and-summary-bytes",
               (svg, summary) == build_documents(
                   manifest, "de" * 32, digest(manifest), loader, digestor,
               ))

        def altered_manifest(key: str, replacement: Any) -> None:
            forged = dict(manifest)
            forged[key] = replacement
            manifest_rows(forged, loader, digestor)

        for key, replacement in (
            ("schema", "foreign"), ("python", "3.14.5"),
            ("case_denominator", 1023), ("oracle_source_sha256", "0" * 64),
            ("matrix_sha256", "0" * 64),
            ("families", manifest["families"][:-1]),
            ("families", list(reversed(manifest["families"]))),
        ):
            reject("reject-forged-manifest-" + key + "-" + str(len(rejected)),
                   lambda key=key, replacement=replacement:
                   altered_manifest(key, replacement))

        receipt_path = manifest["families"][1]["receipt"]["relative"]
        receipt_hash = manifest["families"][1]["receipt"]["sha256"]
        report_path = manifest["families"][1]["report"]["relative"]
        report_hash = manifest["families"][1]["report"]["sha256"]
        receipt = evidence[(receipt_path, receipt_hash)]
        report = evidence[(report_path, report_hash)]
        for key, replacement in (
            ("status", "FAIL"), ("candidate_result_status", "PASS"),
            ("candidate_family", "rust"),
            ("recorder_source_sha256", "0" * 64),
            ("managed_oracle_sha256", "0" * 64),
            ("matrix_sha256", "0" * 64),
            ("baseline_archive_sha256", "0" * 64),
            ("baseline_receipt_sha256", "0" * 64),
            ("baseline_records_sha256", "0" * 64),
            ("case_count", 1023),
            ("validated_candidate_record_count", 1023),
            ("mismatch_count", 236),
            ("all_mismatches_preserved", False),
            ("actual_method_guard_checks", 2047),
            ("actual_warning_registry_guard_checks", 2047),
            ("actual_candidate_workers", 0),
            ("candidate_owner_unchanged", False),
            ("report_sha256", "0" * 64),
            ("report_compression", "none"),
            ("report_complete_readback_verified", False),
            ("clock_samples", 1), ("timing_trials_run", 1),
            ("benchmark_files_read", 1), ("hidden_cases_read", 1),
            ("performance", "fast"),
            ("candidate_qualified_for_hidden_benchmark", True),
            ("final_winner_selected", True),
        ):
            forged = dict(receipt)
            forged[key] = replacement
            reject("reject-forged-candidate-receipt-" + key,
                   lambda forged=forged: validate_candidate_receipt(
                       forged, "c", manifest["families"][1]["candidate_source_sha256"],
                       report_path, report_hash, receipt_path,
                   ))
        base_receipt = evidence[(BASELINE_RECEIPT_RELATIVE, BASELINE_RECEIPT_SHA256)]
        for key, replacement in (
            ("status", "FAIL"), ("baseline_result_status", "FAIL"),
            ("matrix_sha256", "0" * 64), ("case_count", 1023),
            ("actual_reference_workers", 1),
            ("actual_candidate_workers", 1),
            ("hidden_cases_read", 1), ("timing_trials_run", 1),
        ):
            forged = dict(base_receipt)
            forged[key] = replacement
            reject("reject-forged-baseline-receipt-" + key,
                   lambda forged=forged: validate_baseline_receipt(forged))
        for key, replacement in (
            ("status", "PASS"), ("mismatch_count", 236),
            ("validated_candidate_record_count", 1023),
            ("actual_method_guard_checks", 2047),
            ("clock_samples", 1), ("hidden_cases_read", 1),
            ("performance", "fast"),
            ("candidate_records", report["candidate_records"][:-1]),
            ("baseline_records", report["baseline_records"][:-1]),
            ("all_mismatches", report["all_mismatches"][:-1]),
        ):
            forged = dict(report)
            forged[key] = replacement
            reject("reject-forged-full-candidate-report-" + key,
                   lambda forged=forged: validate_candidate(
                       forged, receipt, "c",
                       manifest["families"][1]["candidate_source_sha256"],
                       evidence[(BASELINE_ARCHIVE_RELATIVE,
                                 BASELINE_ARCHIVE_SHA256)]["reference_a_records"],
                       digestor,
                   ))
        for path in ("", "/tmp/escape", "../escape", "a/../b", "a//b", "a\\b"):
            reject("reject-unsafe-path-" + repr(path),
                   lambda path=path: safe_parts(path))
        reject("reject-duplicate-json-fields",
               lambda: decode_document(b'{"a":1,"a":2}\n', "synthetic"))
        reject("reject-noncanonical-json",
               lambda: decode_document(b'{"a":1} \n', "synthetic"))
        reject("block-all-evidence-reads",
               lambda: builtins.open(BASELINE_ARCHIVE_RELATIVE, "rb"))
        reject("block-all-graph-writes",
               lambda: builtins.open(SVG_RELATIVE, "wb"))
        reject("block-no-follow-workspace-reads",
               lambda: os.open(BASELINE_ARCHIVE_RELATIVE, os.O_RDONLY))
        reject("block-hidden-benchmark-access", lambda: os.stat("performance"))
        reject("block-any-candidate-import",
               lambda: importlib.import_module("candidates.vm_candidate"))
        reject("block-candidate-and-reference-workers",
               lambda: subprocess.run([PINNED_PYTHON]))
        reject("block-background-threads",
               lambda: threading.Thread(target=lambda: None).start())
        reject("block-performance-timing", lambda: time.perf_counter())
        reject("block-graph-replacement",
               lambda: os.replace("synthetic-a", "synthetic-b"))
        reject("block-graph-no-clobber-publication",
               lambda: os.link("synthetic-a", "synthetic-b"))
        reject("block-graph-directory-synchronization", lambda: os.fsync(12345))

        previous_doc = dict(decoded)
        previous_doc.pop("frozen_v1_renderer_relative", None)
        previous_doc.pop("frozen_v1_renderer_sha256", None)
        previous_doc["source_relative"] = FROZEN_V1_RELATIVE
        previous_doc["source_sha256"] = FROZEN_V1_SHA256
        previous_svg = b"<svg>prior independently frozen memory graph</svg>\n"
        previous_doc["svg_sha256"] = hashlib.sha256(previous_svg).hexdigest()
        previous_summary = canonical(previous_doc)
        previous_svg_hash = hashlib.sha256(previous_svg).hexdigest()
        previous_summary_hash = hashlib.sha256(previous_summary).hexdigest()
        synthetic_source = "de" * 32
        authentic = validate_previous_outputs(
            previous_svg, previous_summary, previous_svg_hash,
            previous_summary_hash, synthetic_source,
        )
        accept("authenticate-both-exact-frozen-v1-previous-chart-files",
               authentic["source_relative"] == FROZEN_V1_RELATIVE
               and authentic["source_sha256"] == FROZEN_V1_SHA256)
        accept("preserve-the-exact-unrounded-64-bit-lifetime-seed",
               type(authentic["published_seed"]) is int
               and authentic["published_seed"] == 5_567_095_966_978_627_121)
        accept("authenticate-all-four-prior-family-denominators-and-losses",
               len(authentic["families"]) == 4
               and authentic["families"][2]["failed"] == 237)
        accept("require-explicit-authenticated-two-file-refresh",
               approve_publication(
                   previous_svg, previous_summary, svg, summary, True,
                   previous_svg_hash, previous_summary_hash, synthetic_source,
               ) is True)
        accept("allow-byte-identical-no-clobber-publication",
               approve_publication(
                   svg, summary, svg, summary, False,
                   None, None, synthetic_source,
               ) is False)

        def altered_previous(field: str, value: Any) -> None:
            forged = dict(previous_doc)
            forged[field] = value
            encoded = canonical(forged)
            validate_previous_outputs(
                previous_svg, encoded, previous_svg_hash,
                hashlib.sha256(encoded).hexdigest(), synthetic_source,
            )

        for field, value in (
            ("schema", "foreign"),
            ("python", "3.14.5"),
            ("source_relative", SOURCE_RELATIVE),
            ("source_sha256", "0" * 64),
            ("manifest_relative", "docs/evidence/foreign.json"),
            ("manifest_sha256", "0" * 64),
            ("svg_relative", "docs/evidence/foreign.svg"),
            ("svg_sha256", "0" * 64),
            ("oracle_source_sha256", "0" * 64),
            ("candidate_recorder_sha256", "0" * 64),
            ("baseline_recorder_sha256", "0" * 64),
            ("matrix_sha256", "0" * 64),
            ("published_seed", 5_567_095_966_978_627_120),
            ("published_seed", float(PUBLISHED_SEED)),
            ("case_denominator", 1023),
            ("independent_of_original_2807_case_denominator", False),
            ("actual_candidate_workers", 1),
            ("actual_candidate_imports", 1),
            ("hidden_cases_read", 1),
            ("benchmark_files_read", 1),
            ("clock_samples", 1),
            ("timing_trials_run", 1),
            ("performance", "faster"),
            ("final_holdout_opened", True),
            ("winner_selected", True),
            ("families", previous_doc["families"][:-1]),
            ("families", list(reversed(previous_doc["families"]))),
        ):
            reject("reject-forged-prior-memory-graph-" + field
                   + "-" + str(len(rejected)),
                   lambda field=field, value=value:
                   altered_previous(field, value))

        for title, old_svg, old_json, use_replace, svg_pin, summary_pin in (
            ("reject-implicit-graph-refresh", previous_svg, previous_summary,
             False, None, None),
            ("reject-a-missing-prior-svg", None, previous_summary,
             True, previous_svg_hash, previous_summary_hash),
            ("reject-a-missing-prior-summary", previous_svg, None,
             True, previous_svg_hash, previous_summary_hash),
            ("reject-a-forged-prior-svg-digest", previous_svg, previous_summary,
             True, "0" * 64, previous_summary_hash),
            ("reject-a-forged-prior-summary-digest", previous_svg, previous_summary,
             True, previous_svg_hash, "0" * 64),
            ("reject-prior-pins-without-explicit-replacement", svg, summary,
             False, hashlib.sha256(svg).hexdigest(),
             hashlib.sha256(summary).hexdigest()),
        ):
            reject(title, lambda old_svg=old_svg, old_json=old_json,
                   use_replace=use_replace, svg_pin=svg_pin,
                   summary_pin=summary_pin: approve_publication(
                       old_svg, old_json, svg, summary, use_replace,
                       svg_pin, summary_pin, synthetic_source,
                   ))

        successful = SyntheticPublication(previous_svg, previous_summary)
        atomic_refresh_pair(
            successful.directory, (7, 7001),
            previous_svg, previous_summary, svg, summary, successful,
        )
        accept("commit-both-staged-memory-graphs-without-real-files",
               successful.pair() == (svg, summary)
               and successful.only_outputs_remain()
               and successful.sync_count >= 3)
        for count in (1, 2):
            failed = SyntheticPublication(
                previous_svg, previous_summary, fail_replace=count,
            )
            reject("rollback-both-graphs-when-atomic-replace-" + str(count)
                   + "-fails",
                   lambda failed=failed: atomic_refresh_pair(
                       failed.directory, (7, 7001),
                       previous_svg, previous_summary, svg, summary, failed,
                   ))
            accept("restore-the-exact-full-prior-pair-after-replace-"
                   + str(count), failed.pair()
                   == (previous_svg, previous_summary)
                   and failed.only_outputs_remain())
        failed_stage = SyntheticPublication(
            previous_svg, previous_summary, fail_stage_write=True,
        )
        reject("rollback-the-full-pair-when-staging-cannot-be-written",
               lambda: atomic_refresh_pair(
                   failed_stage.directory, (7, 7001),
                   previous_svg, previous_summary, svg, summary,
                   failed_stage,
               ))
        accept("retain-both-old-files-when-a-staging-write-fails",
               failed_stage.pair() == (previous_svg, previous_summary)
               and failed_stage.only_outputs_remain())

        accept("exercise-every-source-only-external-effect-boundary",
               all(count > 0 for count in boundary.blocked.values()))

    return {
        "schema": SCHEMA + "-source-self-test", "status": "PASS",
        "accepted_control_count": len(accepted),
        "rejected_control_count": len(rejected),
        "accepted_controls": accepted, "rejected_controls": rejected,
        "oracle_source_sha256": ORACLE_SHA256,
        "candidate_recorder_sha256": RECORDER_SHA256,
        "matrix_sha256": MATRIX_SHA256, "case_denominator": CASE_COUNT,
        "published_seed": PUBLISHED_SEED,
        "frozen_v1_renderer_relative": FROZEN_V1_RELATIVE,
        "frozen_v1_renderer_sha256": FROZEN_V1_SHA256,
        "actual_candidate_workers": 0, "actual_candidate_imports": 0,
        "workspace_files_read": 0, "workspace_files_written": 0,
        "evidence_files_created": 0, "hidden_cases_read": 0,
        "benchmark_files_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "performance": "NOT MEASURED",
        "final_holdout_opened": False, "winner_selected": False,
    }



def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Safely refresh the independently frozen 1,024-case Python "
            "memory and buffer safety comparison"
        ),
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--manifest")
    parser.add_argument("--manifest-sha256")
    parser.add_argument(
        "--replace-generated", action="store_true",
        help="refresh only the explicitly authenticated previous graph pair",
    )
    parser.add_argument("--previous-svg-sha256")
    parser.add_argument("--previous-summary-sha256")
    options = parser.parse_args(arguments)
    try:
        if options.self_test:
            require(not options.replace_generated
                    and all(getattr(options, key) is None for key in (
                        "source_sha256", "manifest", "manifest_sha256",
                        "previous_svg_sha256", "previous_summary_sha256",
                    )),
                    "source-only controls cannot authorize graph rendering or replacement")
            result = self_test()
        else:
            require(options.render is True,
                    "explicitly request the frozen memory-safety graph")
            result = render(
                options.source_sha256, options.manifest,
                options.manifest_sha256, options.replace_generated,
                options.previous_svg_sha256,
                options.previous_summary_sha256,
            )
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (OverviewError, OSError, TypeError, ValueError, KeyError,
            IndexError, zlib.error) as error:
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA + "-failure",
            "status": "FAIL",
            "error_type": type(error).__name__,
            "error": str(error),
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "final_holdout_opened": False,
            "winner_selected": False,
        }))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
