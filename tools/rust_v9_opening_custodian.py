"""Create one blind v9 opening; never create or inspect a holdout case."""

from __future__ import annotations

import argparse
import base64
from collections.abc import Callable
import contextlib
import errno
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile


SCHEMA = "rebar-v9-opening-custodian-v1"
TARGET = Path("/tmp/rebar-v9-final-holdout-opening-20260723-24576-v1.bin")
SECRET_BYTES = 32
CUSTODY = "procedural_same_user_not_os_isolated"
SELF_TEST_DOMAIN = b"rebar:v9:opening-custodian:synthetic-self-test:v1:"


def _required_flag(name: str) -> int:
    value = getattr(os, name, None)
    if not isinstance(value, int):
        raise RuntimeError(f"required secure operating-system flag is unavailable: {name}")
    return value


def _fill_os_entropy(secret: bytearray) -> None:
    if not hasattr(os, "readv"):
        raise RuntimeError("direct, mutable-buffer operating-system entropy is unavailable")
    flags = os.O_RDONLY | _required_flag("O_CLOEXEC") | _required_flag("O_NOFOLLOW")
    entropy_fd = os.open("/dev/urandom", flags)
    try:
        with memoryview(secret) as view:
            offset = 0
            while offset < len(view):
                try:
                    received = os.readv(entropy_fd, (view[offset:],))
                except InterruptedError:
                    continue
                if received <= 0 or received > len(view) - offset:
                    raise OSError(errno.EIO, "operating-system entropy read was incomplete")
                offset += received
    finally:
        os.close(entropy_fd)


def _check_file(fd: int, expected_size: int) -> None:
    observed = os.fstat(fd)
    if (
        not stat.S_ISREG(observed.st_mode)
        or stat.S_IMODE(observed.st_mode) != 0o600
        or observed.st_uid != os.getuid()
        or observed.st_nlink != 1
        or observed.st_size != expected_size
    ):
        raise OSError(errno.EPERM, "opening file failed secure ownership or size checks")


def _write_all(
    fd: int,
    secret: bytearray,
    write: Callable[[int, memoryview], int],
) -> None:
    with memoryview(secret) as view:
        offset = 0
        while offset < len(view):
            try:
                written = write(fd, view[offset:])
            except InterruptedError:
                continue
            if not isinstance(written, int) or written <= 0 or written > len(view) - offset:
                raise OSError(errno.EIO, "opening file write was incomplete")
            offset += written


def _create_opening(
    target: Path,
    *,
    fill: Callable[[bytearray], None] = _fill_os_entropy,
    write: Callable[[int, memoryview], int] = os.write,
    sync: Callable[[int], None] = os.fsync,
) -> str:
    if not target.is_absolute() or target.name in ("", ".", ".."):
        raise ValueError("the opening target must be an absolute, named file")

    secret = bytearray(SECRET_BYTES)
    directory_fd: int | None = None
    opening_fd: int | None = None
    try:
        fill(secret)
        if len(secret) != SECRET_BYTES:
            raise ValueError("the opening must contain exactly 32 entropy bytes")

        directory_flags = (
            os.O_RDONLY
            | _required_flag("O_DIRECTORY")
            | _required_flag("O_CLOEXEC")
            | _required_flag("O_NOFOLLOW")
        )
        directory_fd = os.open(os.fspath(target.parent), directory_flags)
        opening_flags = (
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | _required_flag("O_CLOEXEC")
            | _required_flag("O_NOFOLLOW")
        )
        opening_fd = os.open(target.name, opening_flags, 0o600, dir_fd=directory_fd)
        os.fchmod(opening_fd, 0o600)
        _check_file(opening_fd, 0)
        _write_all(opening_fd, secret, write)
        _check_file(opening_fd, SECRET_BYTES)
        sync(opening_fd)
        sync(directory_fd)
        _check_file(opening_fd, SECRET_BYTES)
        return hashlib.sha256(secret).hexdigest()
    finally:
        try:
            if opening_fd is not None:
                os.close(opening_fd)
        finally:
            try:
                if directory_fd is not None:
                    os.close(directory_fd)
            finally:
                for index in range(len(secret)):
                    secret[index] = 0


def _source_sha256() -> str:
    with open(__file__, "rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def _create_report(
    target: Path,
    *,
    fill: Callable[[bytearray], None] = _fill_os_entropy,
    write: Callable[[int, memoryview], int] = os.write,
    sync: Callable[[int], None] = os.fsync,
) -> dict[str, object]:
    digest = _create_opening(target, fill=fill, write=write, sync=sync)
    return {
        "schema": SCHEMA,
        "command": "create",
        "status": "PASS",
        "custody": CUSTODY,
        "target": os.fspath(target),
        "opening_sha256": digest,
        "source_sha256": _source_sha256(),
        "randomness_method": "os.readv(/dev/urandom)",
        "opening_bytes": SECRET_BYTES,
        "mode": "0600",
        "owner_uid": os.getuid(),
        "exclusive_creation": True,
        "no_follow": True,
        "read_back": False,
        "file_fsync": True,
        "directory_fsync": True,
        "final_cases_generated": 0,
        "final_cases_opened": 0,
        "candidate_imports": 0,
        "timing_observations": 0,
    }


def _emit_json(report: dict[str, object], *, stream: io.TextIOBase | None = None) -> None:
    print(json.dumps(report, sort_keys=True, separators=(",", ":")), file=stream or sys.stdout)


def _self_test() -> dict[str, object]:
    checks: list[str] = []

    def check(name: str, condition: bool) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    def synthetic(label: bytes) -> tuple[bytes, Callable[[bytearray], None], list[bytearray]]:
        expected = hashlib.sha256(SELF_TEST_DOMAIN + label).digest()
        observed: list[bytearray] = []

        def fill(buffer: bytearray) -> None:
            observed.append(buffer)
            buffer[:] = expected

        return expected, fill, observed

    with tempfile.TemporaryDirectory(prefix="rebar-v9-opening-custodian-self-test-") as owned:
        root = Path(owned)
        expected, fill, observed = synthetic(b"successful-exclusive-opening")
        successful = root / "successful.bin"
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            report = _create_report(successful, fill=fill)
            _emit_json(report)
        encoded = stdout.getvalue()
        observed_stat = successful.stat()
        check("synthetic_domain_separated", not SELF_TEST_DOMAIN.startswith(b"holdout"))
        check("exactly_one_json_stdout_line", len(encoded.splitlines()) == 1)
        check("stdout_is_exact_public_json", json.loads(encoded) == report)
        check("raw_opening_hex_not_disclosed", expected.hex() not in encoded)
        check("raw_opening_base64_not_disclosed", base64.b64encode(expected).decode() not in encoded)
        check("public_digest_is_sha256", report["opening_sha256"] == hashlib.sha256(expected).hexdigest())
        check("public_source_digest_is_sha256", report["source_sha256"] == _source_sha256())
        check("exactly_32_bytes", observed_stat.st_size == SECRET_BYTES)
        check("exactly_private_mode", stat.S_IMODE(observed_stat.st_mode) == 0o600)
        check("owned_by_current_user", observed_stat.st_uid == os.getuid())
        check("single_regular_file", stat.S_ISREG(observed_stat.st_mode) and observed_stat.st_nlink == 1)
        check("successful_entropy_buffer_zeroized", len(observed) == 1 and not any(observed[0]))
        check("custody_is_honestly_procedural", report["custody"] == CUSTODY)
        check(
            "no_final_cases_candidates_or_timing",
            all(report[key] == 0 for key in (
                "final_cases_generated", "final_cases_opened", "candidate_imports", "timing_observations"
            )),
        )
        check("self_test_target_is_not_frozen_target", successful != TARGET and successful.parent == root)

        existing_expected, existing_fill, existing_observed = synthetic(b"reject-existing-file")
        try:
            _create_opening(successful, fill=existing_fill)
        except FileExistsError:
            existing_rejected = True
        else:
            existing_rejected = False
        check("existing_regular_file_rejected", existing_rejected)
        check("existing_file_not_overwritten", successful.stat().st_size == len(existing_expected))
        check("existing_file_failure_zeroized", len(existing_observed) == 1 and not any(existing_observed[0]))

        symlink = root / "existing-symlink.bin"
        symlink.symlink_to(successful.name)
        _, symlink_fill, symlink_observed = synthetic(b"reject-existing-symlink")
        try:
            _create_opening(symlink, fill=symlink_fill)
        except OSError as failure:
            symlink_rejected = failure.errno in (errno.EEXIST, errno.ELOOP)
        else:
            symlink_rejected = False
        check("existing_symlink_rejected_without_following", symlink_rejected and symlink.is_symlink())
        check("symlink_failure_zeroized", len(symlink_observed) == 1 and not any(symlink_observed[0]))

        partial_expected, partial_fill, partial_observed = synthetic(b"reliable-partial-writes")
        pieces: list[bytes] = []

        def partial_write(fd: int, view: memoryview) -> int:
            piece = bytes(view[: min(7, len(view))])
            pieces.append(piece)
            return os.write(fd, piece)

        partial_path = root / "partial-writes.bin"
        partial_digest = _create_opening(partial_path, fill=partial_fill, write=partial_write)
        check("partial_writes_complete_exactly", len(pieces) > 1 and b"".join(pieces) == partial_expected)
        check("partial_write_digest_is_exact", partial_digest == hashlib.sha256(partial_expected).hexdigest())
        check("partial_write_buffer_zeroized", len(partial_observed) == 1 and not any(partial_observed[0]))

        _, short_fill, short_observed = synthetic(b"reject-zero-byte-write")

        def zero_write(_fd: int, _view: memoryview) -> int:
            return 0

        short_path = root / "zero-write.bin"
        try:
            _create_opening(short_path, fill=short_fill, write=zero_write)
        except OSError as failure:
            short_rejected = failure.errno == errno.EIO
        else:
            short_rejected = False
        check("zero_byte_write_rejected", short_rejected and short_path.stat().st_size == 0)
        check("short_write_failure_zeroized", len(short_observed) == 1 and not any(short_observed[0]))

        _, failing_fill, failing_observed = synthetic(b"reject-sync-error")

        def failing_sync(_fd: int) -> None:
            raise OSError(errno.EIO, "synthetic-only synchronization failure")

        failed_sync_path = root / "failed-sync.bin"
        try:
            _create_opening(failed_sync_path, fill=failing_fill, sync=failing_sync)
        except OSError as failure:
            sync_rejected = failure.errno == errno.EIO
        else:
            sync_rejected = False
        check("synchronization_failure_rejected", sync_rejected)
        check("synchronization_failure_zeroized", len(failing_observed) == 1 and not any(failing_observed[0]))

    return {
        "schema": SCHEMA,
        "command": "self-test",
        "status": "PASS",
        "checks": len(checks),
        "check_names": checks,
        "source_sha256": _source_sha256(),
        "custody": CUSTODY,
        "synthetic_only": True,
        "real_target_touched": False,
        "final_cases_generated": 0,
        "final_cases_opened": 0,
        "candidate_imports": 0,
        "timing_observations": 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("self-test", "create"))
    arguments = parser.parse_args(argv)
    try:
        report = _self_test() if arguments.command == "self-test" else _create_report(TARGET)
    except (AssertionError, OSError, RuntimeError, TypeError, ValueError) as failure:
        _emit_json(
            {
                "schema": SCHEMA,
                "command": arguments.command,
                "status": "FAIL",
                "error_type": type(failure).__name__,
                "error": str(failure),
                "custody": CUSTODY,
                "final_cases_generated": 0,
                "final_cases_opened": 0,
                "candidate_imports": 0,
                "timing_observations": 0,
            },
            stream=sys.stderr,
        )
        return 1
    _emit_json(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
