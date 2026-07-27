#!/usr/bin/env python3
"""Verify or losslessly restore the frozen 1,024-case baseline archive."""

from __future__ import annotations

import argparse
import builtins
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
SOURCE_RELATIVE = "tools/restore_managed_buffer_lifetime_baseline_v1.py"
DIRECTORY_RELATIVE = "experiments/rust_public_practice_v1"
STEM = "managed-buffer-lifetime-v1-shared-suite-v1"
REPORT_NAME = STEM + ".json"
ARCHIVE_NAME = REPORT_NAME + ".gz"
RECEIPT_NAME = STEM + "-publication-receipt.json"
REPORT_RELATIVE = DIRECTORY_RELATIVE + "/" + REPORT_NAME
ARCHIVE_RELATIVE = DIRECTORY_RELATIVE + "/" + ARCHIVE_NAME
RECEIPT_RELATIVE = DIRECTORY_RELATIVE + "/" + RECEIPT_NAME
ARCHIVE_SHA256 = (
    "1840d5c5faf0422cfaaae0e277cf5d9bc5ed954fe50beca3d9794b9fd33e5fba"
)
ARCHIVE_BYTES = 4_374_362
REPORT_SHA256 = (
    "8c1acb346f476be4f05edd3e7afa73c9a4196bdafa19c2b6f90259ce6b622b68"
)
REPORT_BYTES = 108_978_141
RECEIPT_SHA256 = (
    "adb34ba45089983ac1857639995c51bdc3ae81e0656fa4b89fd5c0f72420b3ba"
)
ORACLE_RELATIVE = "tools/independent_managed_buffer_lifetime_v1.py"
ORACLE_SHA256 = (
    "cedbab1227ea58a97d407cb339d2959a9f9be58a2085ce3106b65bb3385de489"
)
MATRIX_SHA256 = (
    "28ef84b6989542ba8865c98e5296639c780c786078e2a99c7c0a95bfcb4b0976"
)
RECORDER_RELATIVE = "tools/record_independent_managed_buffer_lifetime_v1.py"
RECORDER_SHA256 = (
    "dddc90f3b6449deeb31098d062af9077e3bea558645b3f2d71de2cd4e6488abd"
)
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
STDLIB_DIRECTORY = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/"
)
SCHEMA = "rebar-independent-managed-buffer-lifetime-v1-archive-restore"
RECEIPT_SCHEMA = (
    "rebar-independent-managed-buffer-lifetime-v1-recorder"
    "-durable-publication-receipt"
)
MAX_ARCHIVE_BYTES = 100 * 1024 * 1024
MAX_REPORT_BYTES = 128 * 1024 * 1024
MAX_RECEIPT_BYTES = 1024 * 1024
MAX_SOURCE_BYTES = 8 * 1024 * 1024
CHUNK_BYTES = 1024 * 1024
PUBLISHED_SEED = 0x4D424C4946455631
BASELINE_RECORDS_SHA256 = (
    "80293f5332300220f38c3f017d38611a5514b1b686918e692a53491945b196df"
)
OWNER_SPECS: dict[str, tuple[str, str, int, bool]] = {
    "recorder": (RECORDER_RELATIVE, RECORDER_SHA256, 103_117, False),
    "oracle": (ORACLE_RELATIVE, ORACLE_SHA256, 123_890, False),
    "python": (PINNED_PYTHON, PINNED_PYTHON_SHA256, 32_387_816, True),
    "re": (
        STDLIB_DIRECTORY + "__init__.py",
        "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35",
        17_876,
        True,
    ),
    "re._compiler": (
        STDLIB_DIRECTORY + "_compiler.py",
        "d49f30cf9a1dbae33b200ed8befd9d0ce3ac612783a10ac35196536f98923e91",
        26_855,
        True,
    ),
    "re._constants": (
        STDLIB_DIRECTORY + "_constants.py",
        "42253b3181b81aad6c46392f44a0ab26dcfa31feea411296f43ba16616a1ab0b",
        6_036,
        True,
    ),
    "re._parser": (
        STDLIB_DIRECTORY + "_parser.py",
        "e57bd194a2d42398355ae7c1ccc2ddfb78421dd431eb81e3809dbe8ca9057dc4",
        40_353,
        True,
    ),
}
FIXED_RECEIPT: dict[str, Any] = {
    "schema": RECEIPT_SCHEMA,
    "status": "PASS",
    "baseline_result_status": "PASS",
    "label": "shared-suite-v1",
    "python": "3.14.6",
    "oracle_relative": ORACLE_RELATIVE,
    "oracle_source_sha256": ORACLE_SHA256,
    "matrix_sha256": MATRIX_SHA256,
    "published_seed": PUBLISHED_SEED,
    "group_count": 32,
    "cases_per_group": 32,
    "case_count": 1024,
    "baseline_records_sha256": BASELINE_RECORDS_SHA256,
    "validated_reference_a_case_count": 1024,
    "validated_reference_b_case_count": 1024,
    "actual_reference_workers": 2,
    "actual_candidate_workers": 0,
    "actual_candidate_imports": 0,
    "actual_baseline_controller_invocations": 1,
    "actual_baseline_process_signal": None,
    "actual_baseline_process_timed_out": False,
    "complete_reference_worker_failure": None,
    "source_closure_unchanged": True,
    "report_relative": REPORT_RELATIVE,
    "report_sha256": REPORT_SHA256,
    "report_bytes": REPORT_BYTES,
    "report_actual_write_calls": 1,
    "report_file_fsync_completed": True,
    "report_directory_fsync_completed": True,
    "report_atomic_no_overwrite_link": True,
    "report_complete_readback_verified": True,
    "receipt_relative": RECEIPT_RELATIVE,
    "approved_fresh_path_count": 2,
    "fresh_paths_checked_before_baseline": True,
    "clock_samples": 0,
    "timing_trials_run": 0,
    "benchmark_files_read": 0,
    "hidden_cases_read": 0,
    "performance": "NOT MEASURED",
    "candidate_qualified_for_hidden_benchmark": False,
    "final_winner_selected": False,
}
FORBIDDEN_ROOTS = frozenset({
    "candidates", "_regex", "fancy_regex", "google_re2", "hyperscan",
    "onig", "oniguruma", "pcre", "pcre2", "re2", "regex", "rust_regex",
    "sre_compile", "sre_constants", "sre_parse", "vectorscan",
})


class RestoreError(Exception):
    """The one prospectively fixed archive or receipt could not be verified."""


class SourceOnlyError(RestoreError):
    """A synthetic control attempted to observe or modify the workspace."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise RestoreError(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, ensure_ascii=True, allow_nan=False,
            sort_keys=True, separators=(",", ":"),
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, OverflowError) as error:
        raise RestoreError("evidence is not complete canonical JSON") from error


def validate_digest(value: Any, label: str) -> str:
    require(
        type(value) is str and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        "an exact lowercase SHA-256 is required: " + label,
    )
    return value


def safe_parts(value: Any) -> tuple[str, ...]:
    require(
        type(value) is str and bool(value)
        and "\\" not in value and "\x00" not in value,
        "an exact no-follow relative path is required",
    )
    parts = tuple(value.split("/"))
    require(
        all(part not in {"", ".", ".."} for part in parts)
        and "/".join(parts) == value,
        "a frozen evidence path escaped the workspace",
    )
    return parts


def verify_clean_modules(modules: Mapping[str, Any] | None = None) -> None:
    actual = sys.modules if modules is None else modules
    require(isinstance(actual, Mapping), "an authentic module table is required")
    for name in actual:
        require(
            type(name) is str and name.partition(".")[0] not in FORBIDDEN_ROOTS,
            "a candidate or external regex entered the evidence restorer",
        )


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == PINNED_PYTHON
        and os.path.realpath(sys.executable) == PINNED_PYTHON
        and os.path.abspath(__file__) == ROOT + "/" + SOURCE_RELATIVE
        and os.path.realpath(__file__) == ROOT + "/" + SOURCE_RELATIVE,
        "use the exact isolated pinned CPython and frozen restoration tool",
    )
    verify_clean_modules()


def directory_flags() -> int:
    return (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )


def regular_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)


@contextlib.contextmanager
def open_parent(relative: str) -> Iterator[tuple[int, str]]:
    parts = safe_parts(relative)
    descriptors: list[int] = []
    try:
        current = os.open(ROOT, directory_flags())
        descriptors.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode), "workspace root changed")
        for component in parts[:-1]:
            current = os.open(component, directory_flags(), dir_fd=current)
            descriptors.append(current)
            require(
                stat.S_ISDIR(os.fstat(current).st_mode),
                "a frozen parent is not a genuine no-follow directory",
            )
        yield current, parts[-1]
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


@contextlib.contextmanager
def open_regular(
    directory: int, name: str, maximum: int,
) -> Iterator[tuple[int, os.stat_result]]:
    require(
        type(name) is str and safe_parts(name) == (name,)
        and type(maximum) is int and 0 < maximum <= MAX_REPORT_BYTES,
        "a single bounded exact evidence filename is mandatory",
    )
    descriptor = os.open(name, regular_flags(), dir_fd=directory)
    try:
        before = os.fstat(descriptor)
        named = os.stat(name, dir_fd=directory, follow_symlinks=False)
        require(
            stat.S_ISREG(before.st_mode) and stat.S_ISREG(named.st_mode)
            and (before.st_dev, before.st_ino, before.st_size)
            == (named.st_dev, named.st_ino, named.st_size)
            and 0 < before.st_size <= maximum,
            "an expected regular evidence file was replaced or became unsafe",
        )
        yield descriptor, before
    finally:
        os.close(descriptor)


def read_regular(
    directory: int, name: str, expected: str, maximum: int,
    *, retain: bool = False,
) -> tuple[dict[str, Any], bytes | None]:
    validate_digest(expected, name)
    with open_regular(directory, name, maximum) as (descriptor, before):
        hasher = hashlib.sha256()
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(CHUNK_BYTES, remaining))
            require(type(block) is bytes and bool(block), "evidence was truncated")
            hasher.update(block)
            if retain:
                chunks.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"", "evidence gained a hidden suffix")
        after = os.fstat(descriptor)
        named = os.stat(name, dir_fd=directory, follow_symlinks=False)
        actual = hasher.hexdigest()
        require(
            (before.st_dev, before.st_ino, before.st_size)
            == (after.st_dev, after.st_ino, after.st_size)
            == (named.st_dev, named.st_ino, named.st_size)
            and actual == expected,
            "an evidence file changed or failed its exact frozen SHA-256",
        )
        return (
            {"sha256": actual, "bytes": before.st_size,
             "device": before.st_dev, "inode": before.st_ino},
            b"".join(chunks) if retain else None,
        )


def decode_receipt(raw: Any) -> dict[str, Any]:
    require(
        type(raw) is bytes and 0 < len(raw) <= MAX_RECEIPT_BYTES,
        "the complete bounded pinned receipt is mandatory",
    )

    def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(type(key) is str and key not in result, "receipt field duplicated")
            result[key] = value
        return result

    def reject_nonfinite(_: str) -> None:
        raise RestoreError("nonfinite receipt values are forbidden")

    try:
        value = json.loads(
            raw, object_pairs_hook=unique, parse_constant=reject_nonfinite,
        )
    except (RestoreError, TypeError, ValueError, UnicodeError) as error:
        raise RestoreError("the pinned receipt is not valid complete JSON") from error
    require(
        type(value) is dict and canonical(value) == raw,
        "the pinned receipt is not byte-for-byte canonical",
    )
    return value


def validate_receipt(value: Any) -> dict[str, Any]:
    require(type(value) is dict, "a complete passing baseline receipt is mandatory")
    extra_fields = {
        "baseline_reference_pids", "source_closure_before", "source_closure_after",
    }
    require(
        set(value) == set(FIXED_RECEIPT) | extra_fields,
        "the baseline receipt omitted or added an authenticated field",
    )
    for key, expected in FIXED_RECEIPT.items():
        actual = value[key]
        require(
            type(actual) is type(expected) and actual == expected,
            "the pinned passing baseline receipt changed: " + key,
        )
    pids = value["baseline_reference_pids"]
    require(
        type(pids) is list and len(pids) == 2
        and all(type(pid) is int and pid > 0 for pid in pids)
        and pids[0] != pids[1],
        "two distinct genuine reference processes are mandatory",
    )
    before = value["source_closure_before"]
    after = value["source_closure_after"]
    require(
        type(before) is dict and type(after) is dict
        and before == after and set(before) == set(OWNER_SPECS),
        "the complete independently pinned source closure changed",
    )
    for name, (path, digest, size, absolute) in OWNER_SPECS.items():
        owner = before[name]
        path_key = "path" if absolute else "relative"
        require(
            type(owner) is dict
            and set(owner) == {path_key, "sha256", "bytes", "device", "inode"}
            and type(owner.get(path_key)) is str and owner[path_key] == path
            and type(owner.get("sha256")) is str and owner["sha256"] == digest
            and type(owner.get("bytes")) is int and owner["bytes"] == size
            and type(owner.get("device")) is int and owner["device"] >= 0
            and type(owner.get("inode")) is int and owner["inode"] > 0,
            "a frozen reference source owner changed: " + name,
        )
    return value


def stream_gzip_blocks(
    blocks: Iterator[bytes], *, archive_sha256: str, archive_bytes: int,
    report_sha256: str, report_bytes: int,
    sink: Callable[[bytes], Any] | None = None,
) -> dict[str, Any]:
    validate_digest(archive_sha256, "compressed archive")
    validate_digest(report_sha256, "original report")
    require(
        type(archive_bytes) is int and 0 < archive_bytes <= MAX_ARCHIVE_BYTES
        and type(report_bytes) is int and 0 < report_bytes <= MAX_REPORT_BYTES
        and (sink is None or callable(sink)),
        "bounded exact original and compressed byte counts are mandatory",
    )
    inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
    compressed = hashlib.sha256()
    original = hashlib.sha256()
    compressed_size = 0
    original_size = 0
    for block in blocks:
        require(
            type(block) is bytes and 0 < len(block) <= CHUNK_BYTES,
            "archive input was clipped, empty, or unbounded",
        )
        compressed_size += len(block)
        require(compressed_size <= archive_bytes, "archive gained a hidden suffix")
        compressed.update(block)
        pending = block
        while pending:
            try:
                part = inflater.decompress(
                    pending, min(CHUNK_BYTES, report_bytes - original_size + 1),
                )
            except (zlib.error, ValueError, OverflowError) as error:
                raise RestoreError("the single-member gzip archive is invalid") from error
            require(
                not inflater.unused_data,
                "gzip trailing bytes or an additional member are forbidden",
            )
            if part:
                original_size += len(part)
                require(
                    original_size <= report_bytes,
                    "gzip output exceeded the exact bounded original report",
                )
                original.update(part)
                if sink is not None:
                    sink(part)
            pending = inflater.unconsumed_tail
    require(
        inflater.eof and not inflater.unused_data and not inflater.unconsumed_tail,
        "the complete single-member gzip footer was missing or clipped",
    )
    try:
        trailing = inflater.flush(CHUNK_BYTES)
    except (zlib.error, ValueError, OverflowError) as error:
        raise RestoreError("the gzip archive could not be completely finalized") from error
    require(not trailing, "gzip retained unauthenticated output")
    require(
        compressed_size == archive_bytes
        and compressed.hexdigest() == archive_sha256,
        "the compressed archive failed its exact frozen byte count or SHA-256",
    )
    require(
        original_size == report_bytes
        and original.hexdigest() == report_sha256,
        "the restored report failed its exact frozen byte count or SHA-256",
    )
    return {
        "archive_sha256": archive_sha256, "archive_bytes": compressed_size,
        "report_sha256": report_sha256, "report_bytes": original_size,
        "gzip_member_count": 1, "gzip_trailing_bytes": 0,
    }


def verify_archive(
    directory: int, *, sink: Callable[[bytes], Any] | None = None,
) -> dict[str, Any]:
    with open_regular(directory, ARCHIVE_NAME, MAX_ARCHIVE_BYTES) as (
        descriptor, before,
    ):
        require(before.st_size == ARCHIVE_BYTES, "the frozen archive size changed")

        def blocks() -> Iterator[bytes]:
            remaining = before.st_size
            while remaining:
                block = os.read(descriptor, min(CHUNK_BYTES, remaining))
                require(bool(block), "the gzip archive was truncated during use")
                remaining -= len(block)
                yield block
            require(os.read(descriptor, 1) == b"", "gzip archive gained a suffix")

        result = stream_gzip_blocks(
            blocks(), archive_sha256=ARCHIVE_SHA256, archive_bytes=ARCHIVE_BYTES,
            report_sha256=REPORT_SHA256, report_bytes=REPORT_BYTES, sink=sink,
        )
        after = os.fstat(descriptor)
        named = os.stat(ARCHIVE_NAME, dir_fd=directory, follow_symlinks=False)
        require(
            (before.st_dev, before.st_ino, before.st_size)
            == (after.st_dev, after.st_ino, after.st_size)
            == (named.st_dev, named.st_ino, named.st_size),
            "the pinned gzip archive changed during streaming verification",
        )
        return result


def existing_report(directory: int) -> dict[str, Any] | None:
    try:
        named = os.stat(REPORT_NAME, dir_fd=directory, follow_symlinks=False)
    except FileNotFoundError:
        return None
    require(
        stat.S_ISREG(named.st_mode) and named.st_size == REPORT_BYTES,
        "an existing original report cannot be overwritten or replaced",
    )
    owner, _ = read_regular(
        directory, REPORT_NAME, REPORT_SHA256, MAX_REPORT_BYTES,
    )
    require(owner["bytes"] == REPORT_BYTES, "existing report has the wrong size")
    return owner


def publish_restored_report(directory: int) -> dict[str, Any]:
    flags = (
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor: int | None = None
    temporary: str | None = None
    linked = False
    try:
        for attempt in range(32):
            candidate = "." + STEM + ".restore-" + str(os.getpid()) + "-" + str(attempt)
            try:
                descriptor = os.open(candidate, flags, 0o600, dir_fd=directory)
                temporary = candidate
                break
            except FileExistsError:
                continue
        require(
            descriptor is not None and temporary is not None,
            "a fresh exact no-clobber restoration temporary is required",
        )
        created = os.fstat(descriptor)
        require(stat.S_ISREG(created.st_mode), "restoration output is not regular")

        def write_all(block: bytes) -> None:
            view = memoryview(block)
            while view:
                written = os.write(descriptor, view)
                require(
                    type(written) is int and 0 < written <= len(view),
                    "the restored report was incompletely written",
                )
                view = view[written:]

        archive = verify_archive(directory, sink=write_all)
        os.fsync(descriptor)
        finished = os.fstat(descriptor)
        require(
            (created.st_dev, created.st_ino)
            == (finished.st_dev, finished.st_ino)
            and finished.st_size == REPORT_BYTES,
            "the fresh restoration output changed or was clipped",
        )
        try:
            os.link(
                temporary, REPORT_NAME,
                src_dir_fd=directory, dst_dir_fd=directory,
                follow_symlinks=False,
            )
            linked = True
            os.fsync(directory)
        except FileExistsError:
            require(
                existing_report(directory) is not None,
                "a competing original report was not byte-for-byte identical",
            )
        verified = existing_report(directory)
        require(verified is not None, "the restored original disappeared")
        return {
            **archive,
            "report_previously_present": not linked,
            "report_created": linked,
            "report_complete_readback_verified": True,
            "report_atomic_no_overwrite_link": linked,
            "report_file_fsync_completed": True,
            "report_directory_fsync_completed": linked,
        }
    finally:
        if descriptor is not None:
            try:
                if temporary is not None:
                    actual = os.stat(
                        temporary, dir_fd=directory, follow_symlinks=False,
                    )
                    retained = os.fstat(descriptor)
                    if (actual.st_dev, actual.st_ino) == (
                        retained.st_dev, retained.st_ino,
                    ):
                        os.unlink(temporary, dir_fd=directory)
                        os.fsync(directory)
            except FileNotFoundError:
                pass
            finally:
                os.close(descriptor)


def run_real(options: argparse.Namespace) -> dict[str, Any]:
    verify_runtime()
    require(
        validate_digest(options.source_sha256, "frozen restore tool")
        and validate_digest(options.archive_sha256, "frozen gzip archive")
        == ARCHIVE_SHA256
        and validate_digest(options.report_sha256, "frozen original report")
        == REPORT_SHA256
        and validate_digest(options.receipt_sha256, "frozen baseline receipt")
        == RECEIPT_SHA256
        and validate_digest(options.oracle_source_sha256, "frozen oracle")
        == ORACLE_SHA256
        and validate_digest(options.matrix_sha256, "frozen matrix")
        == MATRIX_SHA256,
        "authorize only the exact prospectively fixed restoration inputs",
    )
    with open_parent(SOURCE_RELATIVE) as (source_directory, source_name):
        source, _ = read_regular(
            source_directory, source_name, options.source_sha256, MAX_SOURCE_BYTES,
        )
    with open_parent(ARCHIVE_RELATIVE) as (directory, archive_name):
        require(archive_name == ARCHIVE_NAME, "the archive filename changed")
        receipt_owner, receipt_raw = read_regular(
            directory, RECEIPT_NAME, RECEIPT_SHA256, MAX_RECEIPT_BYTES,
            retain=True,
        )
        receipt = validate_receipt(decode_receipt(receipt_raw))
        archive = verify_archive(directory)
        present = existing_report(directory)
        if options.restore and present is None:
            result = publish_restored_report(directory)
        else:
            result = {
                **archive,
                "report_previously_present": present is not None,
                "report_created": False,
                "report_complete_readback_verified": present is not None,
                "report_atomic_no_overwrite_link": False,
                "report_file_fsync_completed": False,
                "report_directory_fsync_completed": False,
            }
        require(
            not options.restore or existing_report(directory) is not None,
            "explicit restoration did not preserve the exact original report",
        )
    with open_parent(SOURCE_RELATIVE) as (source_directory, source_name):
        source_after, _ = read_regular(
            source_directory, source_name, options.source_sha256, MAX_SOURCE_BYTES,
        )
    require(source_after == source, "the pinned restoration tool changed during use")
    verify_runtime()
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "mode": "restore" if options.restore else "verify",
        "source_relative": SOURCE_RELATIVE,
        "source_sha256": source["sha256"],
        "archive_relative": ARCHIVE_RELATIVE,
        "receipt_relative": RECEIPT_RELATIVE,
        "receipt_sha256": receipt_owner["sha256"],
        "oracle_source_sha256": receipt["oracle_source_sha256"],
        "matrix_sha256": receipt["matrix_sha256"],
        "baseline_result_status": receipt["baseline_result_status"],
        "case_count": receipt["case_count"],
        "actual_reference_workers": receipt["actual_reference_workers"],
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
        **result,
    }


class SourceOnlyBoundary:
    """Prevent synthetic self-tests from observing or changing the workspace."""

    def __init__(self) -> None:
        self.originals: list[tuple[Any, str, Any]] = []
        self.blocked: dict[str, int] = {
            "file_reads": 0, "file_writes": 0, "processes": 0,
            "dynamic_imports": 0, "threads": 0, "clock_samples": 0,
        }

    def install(self, owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)
        self.originals.append((owner, name, original))

        def denied(*args: Any, **kwargs: Any) -> Any:
            actual = category
            if category == "file_reads":
                mode = args[1] if len(args) > 1 else kwargs.get("mode", "r")
                if (
                    type(mode) is str and any(flag in mode for flag in "wax+")
                ) or (
                    type(mode) is int
                    and bool(mode & (
                        os.O_WRONLY | os.O_RDWR | os.O_CREAT
                        | os.O_TRUNC | os.O_APPEND
                    ))
                ):
                    actual = "file_writes"
            self.blocked[actual] += 1
            raise SourceOnlyError("source-only controls forbid " + actual)

        setattr(owner, name, denied)

    def __enter__(self) -> SourceOnlyBoundary:
        for owner, name, category in (
            (builtins, "open", "file_reads"),
            (io, "open", "file_reads"),
            (os, "open", "file_reads"),
            (os, "stat", "file_reads"),
            (os, "lstat", "file_reads"),
            (os, "scandir", "file_reads"),
            (os, "listdir", "file_reads"),
            (os, "replace", "file_writes"),
            (os, "rename", "file_writes"),
            (os, "link", "file_writes"),
            (os, "unlink", "file_writes"),
            (os, "remove", "file_writes"),
            (os, "write", "file_writes"),
            (os, "fsync", "file_writes"),
            (subprocess, "Popen", "processes"),
            (subprocess, "run", "processes"),
            (os, "system", "processes"),
            (os, "posix_spawn", "processes"),
            (importlib, "import_module", "dynamic_imports"),
            (threading.Thread, "start", "threads"),
            (time, "time", "clock_samples"),
            (time, "time_ns", "clock_samples"),
            (time, "monotonic", "clock_samples"),
            (time, "monotonic_ns", "clock_samples"),
            (time, "perf_counter", "clock_samples"),
            (time, "perf_counter_ns", "clock_samples"),
        ):
            self.install(owner, name, category)
        return self

    def __exit__(self, error_type: Any, error: Any, trace: Any) -> bool:
        del error_type, error, trace
        for owner, name, original in reversed(self.originals):
            setattr(owner, name, original)
        self.originals.clear()
        return False


def synthetic_receipt() -> dict[str, Any]:
    closure: dict[str, dict[str, Any]] = {}
    for number, (name, (path, digest, size, absolute)) in enumerate(
        OWNER_SPECS.items(), start=1001,
    ):
        closure[name] = {
            "path" if absolute else "relative": path,
            "sha256": digest,
            "bytes": size,
            "device": 7,
            "inode": number,
        }
    return {
        **FIXED_RECEIPT,
        "baseline_reference_pids": [58001, 58002],
        "source_closure_before": closure,
        "source_closure_after": {
            name: dict(owner) for name, owner in closure.items()
        },
    }


def source_self_test() -> dict[str, Any]:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1 and sys.dont_write_bytecode is True,
        "run source-only controls under isolated pinned CPython 3.14.6",
    )
    verify_clean_modules()
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(
            type(name) is str and name not in accepted and bool(condition),
            "a source-only positive control failed: " + name,
        )
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(
            type(name) is str and name not in rejected and callable(action),
            "a source-only rejection control was duplicated",
        )
        try:
            action()
        except (RestoreError, OSError, TypeError, ValueError, zlib.error):
            rejected.append(name)
            return
        raise RestoreError("a forged source-only control was accepted: " + name)

    with SourceOnlyBoundary() as boundary:
        receipt = synthetic_receipt()
        accept("validate-the-complete-passing-frozen-receipt", validate_receipt(receipt) is receipt)
        raw_receipt = canonical(receipt)
        accept(
            "reject-lossy-receipt-serialization",
            decode_receipt(raw_receipt) == receipt,
        )
        original = b'{"proof":"complete synthetic original"}\n'
        compressor = zlib.compressobj(level=9, wbits=16 + zlib.MAX_WBITS)
        archive = compressor.compress(original) + compressor.flush()
        archive_digest = hashlib.sha256(archive).hexdigest()
        original_digest = hashlib.sha256(original).hexdigest()

        def observe(
            data: bytes = archive, *, a_digest: str = archive_digest,
            a_bytes: int | None = None, r_digest: str = original_digest,
            r_bytes: int = len(original),
        ) -> dict[str, Any]:
            return stream_gzip_blocks(
                (data[offset:offset + 7] for offset in range(0, len(data), 7)),
                archive_sha256=a_digest,
                archive_bytes=len(data) if a_bytes is None else a_bytes,
                report_sha256=r_digest,
                report_bytes=r_bytes,
            )

        accept("verify-an-exact-single-member-stream", observe()["gzip_member_count"] == 1)
        recovered = bytearray()
        observed = stream_gzip_blocks(
            iter((archive,)), archive_sha256=archive_digest,
            archive_bytes=len(archive), report_sha256=original_digest,
            report_bytes=len(original), sink=recovered.extend,
        )
        accept(
            "recover-every-original-byte-without-reading-evidence",
            bytes(recovered) == original and observed["gzip_trailing_bytes"] == 0,
        )
        accept(
            "pin-the-actual-1024-case-baseline-archive",
            ARCHIVE_BYTES == 4_374_362 and REPORT_BYTES == 108_978_141
            and validate_digest(ARCHIVE_SHA256, "archive") == ARCHIVE_SHA256
            and validate_digest(REPORT_SHA256, "report") == REPORT_SHA256
            and validate_digest(RECEIPT_SHA256, "receipt") == RECEIPT_SHA256,
        )
        accept(
            "preserve-the-exact-independent-oracle-and-matrix",
            receipt["oracle_source_sha256"] == ORACLE_SHA256
            and receipt["matrix_sha256"] == MATRIX_SHA256,
        )
        accept(
            "preserve-two-distinct-reference-workers-and-all-1024-cases",
            receipt["actual_reference_workers"] == 2
            and receipt["validated_reference_a_case_count"] == 1024
            and receipt["validated_reference_b_case_count"] == 1024,
        )
        for path in ("", "/tmp/escape", "../escape", "a/../b", "a//b", "a\\b", "a/./b"):
            reject("reject-unsafe-relative-path-" + repr(path), lambda path=path: safe_parts(path))
        for field, replacement in (
            ("status", "FAIL"), ("baseline_result_status", "FAIL"),
            ("oracle_source_sha256", "0" * 64), ("matrix_sha256", "0" * 64),
            ("report_sha256", "0" * 64), ("report_bytes", REPORT_BYTES - 1),
            ("case_count", 1023), ("actual_reference_workers", 1),
            ("actual_candidate_workers", 1), ("actual_candidate_imports", 1),
            ("clock_samples", 1), ("timing_trials_run", 1),
            ("benchmark_files_read", 1), ("hidden_cases_read", 1),
            ("performance", "faster"), ("candidate_qualified_for_hidden_benchmark", True),
            ("final_winner_selected", True), ("report_relative", "../escape"),
            ("receipt_relative", "../escape"), ("source_closure_unchanged", False),
        ):
            forged = dict(receipt)
            forged[field] = replacement
            reject("reject-forged-receipt-" + field, lambda forged=forged: validate_receipt(forged))
        for name in OWNER_SPECS:
            forged = dict(receipt)
            before = {key: dict(value) for key, value in receipt["source_closure_before"].items()}
            before[name]["sha256"] = "0" * 64
            forged["source_closure_before"] = before
            forged["source_closure_after"] = {key: dict(value) for key, value in before.items()}
            reject("reject-forged-source-owner-" + name, lambda forged=forged: validate_receipt(forged))
        reject("reject-clipped-gzip", lambda: observe(archive[:-1]))
        reject("reject-gzip-trailing-bytes", lambda: observe(archive + b"hidden"))
        reject("reject-a-second-gzip-member", lambda: observe(archive + archive))
        reject("reject-the-wrong-archive-digest", lambda: observe(a_digest="0" * 64))
        reject("reject-the-wrong-original-digest", lambda: observe(r_digest="0" * 64))
        reject("reject-the-wrong-archive-size", lambda: observe(a_bytes=len(archive) + 1))
        reject("reject-an-overlong-original", lambda: observe(r_bytes=len(original) - 1))
        reject("reject-a-clipped-original", lambda: observe(r_bytes=len(original) + 1))
        reject("reject-an-oversized-archive", lambda: observe(a_bytes=MAX_ARCHIVE_BYTES + 1))
        reject("reject-an-oversized-original", lambda: observe(r_bytes=MAX_REPORT_BYTES + 1))
        reject("reject-duplicate-receipt-fields", lambda: decode_receipt(b'{"status":"PASS","status":"PASS"}\n'))
        reject("reject-noncanonical-receipt", lambda: decode_receipt(raw_receipt[:-1] + b" \n"))
        reject("reject-candidate-module-contamination", lambda: verify_clean_modules({"candidates.vm_candidate": object()}))
        reject("reject-external-regex-contamination", lambda: verify_clean_modules({"regex": object()}))
        reject("block-evidence-file-reads", lambda: builtins.open(REPORT_RELATIVE, "rb"))
        reject("block-evidence-file-writes", lambda: builtins.open(REPORT_RELATIVE, "wb"))
        reject("block-no-follow-file-reads", lambda: os.open(ARCHIVE_RELATIVE, os.O_RDONLY))
        reject("block-no-follow-file-writes", lambda: os.open(REPORT_RELATIVE, os.O_WRONLY | os.O_CREAT))
        reject("block-hidden-workspace-stat", lambda: os.stat("performance"))
        reject("block-candidate-imports", lambda: importlib.import_module("candidates.vm_candidate"))
        reject("block-worker-processes", lambda: subprocess.run([PINNED_PYTHON]))
        reject("block-background-threads", lambda: threading.Thread(target=lambda: None).start())
        reject("block-performance-clock", lambda: time.perf_counter())
        reject("block-evidence-replacement", lambda: os.replace("synthetic-a", "synthetic-b"))
        reject("block-evidence-no-clobber-links", lambda: os.link("synthetic-a", "synthetic-b"))
        reject("block-evidence-deletion", lambda: os.unlink("synthetic-a"))
        reject("block-evidence-directory-sync", lambda: os.fsync(12345))
        accept(
            "exercise-every-source-only-external-effect-boundary",
            all(boundary.blocked[name] > 0 for name in boundary.blocked),
        )

    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "accepted_control_count": len(accepted),
        "rejected_control_count": len(rejected),
        "accepted_controls": accepted,
        "rejected_controls": rejected,
        "archive_sha256": ARCHIVE_SHA256,
        "archive_bytes": ARCHIVE_BYTES,
        "report_sha256": REPORT_SHA256,
        "report_bytes": REPORT_BYTES,
        "receipt_sha256": RECEIPT_SHA256,
        "oracle_source_sha256": ORACLE_SHA256,
        "matrix_sha256": MATRIX_SHA256,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "workspace_files_read": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify or losslessly restore the exact frozen 1,024-case CPython baseline",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true", help="run source-only synthetic controls")
    modes.add_argument("--verify", action="store_true", help="verify the exact frozen archive and passing receipt without writing")
    modes.add_argument("--restore", action="store_true", help="atomically restore the exact report without overwriting")
    parser.add_argument("--source-sha256", help="explicit exact SHA-256 of this frozen restore tool")
    parser.add_argument("--archive-sha256", default=ARCHIVE_SHA256)
    parser.add_argument("--report-sha256", default=REPORT_SHA256)
    parser.add_argument("--receipt-sha256", default=RECEIPT_SHA256)
    parser.add_argument("--oracle-source-sha256", default=ORACLE_SHA256)
    parser.add_argument("--matrix-sha256", default=MATRIX_SHA256)
    options = parser.parse_args(argv)
    try:
        if options.self_test:
            require(
                options.source_sha256 is None
                and options.archive_sha256 == ARCHIVE_SHA256
                and options.report_sha256 == REPORT_SHA256
                and options.receipt_sha256 == RECEIPT_SHA256
                and options.oracle_source_sha256 == ORACLE_SHA256
                and options.matrix_sha256 == MATRIX_SHA256,
                "source-only self-tests cannot authorize actual evidence inputs",
            )
            result = source_self_test()
        else:
            require(options.source_sha256 is not None, "pin the exact restore tool with --source-sha256")
            result = run_real(options)
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (RestoreError, OSError, TypeError, ValueError, zlib.error) as error:
        result = {
            "schema": SCHEMA + "-failure",
            "status": "FAIL",
            "error_type": type(error).__name__,
            "error": str(error),
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
        sys.stdout.buffer.write(canonical(result))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
