#!/usr/bin/env python3
"""Safely read the two complete, genuinely frozen V17 regex results."""

from __future__ import annotations

import sys

if __name__ == "__main__":
    import os as _reader_os
    from pathlib import Path as _ReaderPath

    _reader_root = str(_ReaderPath(__file__).resolve().parent.parent)
    _reader_entry = (
        "import sys;sys.path.insert(0,sys.argv[1]);"
        "from tools.python_re_universal_public_oracle_stage17_evidence "
        "import main;raise SystemExit(main(sys.argv[2:]))"
    )
    _reader_os.execv(
        sys.executable,
        [sys.executable, "-I", "-B", "-c", _reader_entry,
         _reader_root, *sys.argv[1:]],
    )

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import types
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import python_re_universal_public_oracle_stage17 as stage17


frozen = stage17.frozen
SOURCE_RELATIVE = "tools/python_re_universal_public_oracle_stage17_evidence.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V17-EVIDENCE.md"
SCHEMA = "rebar-python-re-public-contract-v17-bounded-evidence-v1"
SELF_TEST_SCHEMA = SCHEMA + "-self-test"
MAX_EVIDENCE_BYTES = 33_554_432
READ_CHUNK_BYTES = 262_144
STAGE17_SOURCE_RELATIVE = stage17.SOURCE_RELATIVE
STAGE17_SOURCE_SHA256 = (
    "9e5ca448ecc6a6de8745b0c84cf5b4ae5d92cd098914731a4047d45e6ce1b6d4"
)
STAGE17_PROTOCOL_RELATIVE = stage17.PROTOCOL_RELATIVE
STAGE17_PROTOCOL_SHA256 = (
    "8773d4fd2d0b9f04808b2a22358a233b44abfd892862aaaf224cd0d607081520"
)
SELF_ORACLE_RELATIVE = stage17.SELF_ORACLE_RELATIVE
SELF_ORACLE_SHA256 = (
    "de1272f7c3681402b8787ea2a53de8228ef0341760505dc052c52b023e3d3c3d"
)
SELF_ORACLE_BYTES = 11_556_111
ALL_CANDIDATE_RELATIVE = stage17.ALL_CANDIDATE_RELATIVE
ALL_CANDIDATE_SHA256 = (
    "255644709afe8fa8ce41cefcfd029b7f865bbcd0314d528902bb5a56d52aa288"
)
ALL_CANDIDATE_BYTES = 20_220_593
APPROVED_EVIDENCE = {
    SELF_ORACLE_RELATIVE: (SELF_ORACLE_SHA256, SELF_ORACLE_BYTES),
    ALL_CANDIDATE_RELATIVE: (ALL_CANDIDATE_SHA256, ALL_CANDIDATE_BYTES),
}
V15_FAILURE_SHA256 = (
    "cb71e1a44549c7c76c3bf08900e6107d2b49e789e5002afc725d1e9df0c92880"
)

_FROZEN_SHA256 = hashlib.sha256
_FROZEN_JSON_LOADS = json.loads


def _exact_evidence_target(
    relative: Any, expected_sha256: Any,
) -> tuple[tuple[str, ...], int]:
    frozen.require(
        type(relative) is str
        and relative in APPROVED_EVIDENCE
        and type(expected_sha256) is str
        and stage17.official_locale.is_sha256(expected_sha256),
        "only an explicitly pinned genuine V17 evidence file is allowed",
    )
    path = PurePosixPath(relative)
    pinned_sha, pinned_size = APPROVED_EVIDENCE[relative]
    frozen.require(
        not path.is_absolute()
        and ".." not in path.parts
        and "." not in path.parts
        and "\\" not in relative
        and "\x00" not in relative
        and str(path) == relative
        and expected_sha256 == pinned_sha
        and 0 < pinned_size <= MAX_EVIDENCE_BYTES,
        "the bounded reader rejected a substituted or escaping evidence path",
    )
    return tuple(path.parts), pinned_size


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        frozen.require(
            key not in result,
            "the bounded evidence JSON contains a duplicated object key",
        )
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> Any:
    raise frozen.OracleIntegrityError(
        "the bounded evidence JSON contains a nonfinite number: " + value,
    )


def _parse_durable_payload(
    payload: Any, *, expected_sha256: str, expected_size: int | None = None,
) -> dict[str, Any]:
    frozen.require(
        isinstance(payload, bytes)
        and 0 < len(payload) <= MAX_EVIDENCE_BYTES
        and (expected_size is None or len(payload) == expected_size)
        and stage17.official_locale.is_sha256(expected_sha256)
        and _FROZEN_SHA256(payload).hexdigest() == expected_sha256,
        "the exact bounded evidence bytes, size, or pinned SHA-256 changed",
    )
    try:
        text = payload.decode("utf-8", "strict")
        document = _FROZEN_JSON_LOADS(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite,
        )
    except (UnicodeError, ValueError, TypeError) as error:
        raise frozen.OracleIntegrityError(
            "the bounded evidence contains malformed UTF-8 or JSON",
        ) from error
    frozen.require(
        isinstance(document, dict)
        and stage17.canonical(document) + b"\n" == payload,
        "bounded evidence has trailing, noncanonical, or twice-encoded bytes",
    )
    parsed, canonical_payload = stage17._durable_round_trip(document)
    frozen.require(
        parsed == document and canonical_payload + b"\n" == payload,
        "bounded evidence changes after its exact durable JSON round trip",
    )
    return document


def _validate_directory_stat(snapshot: Any) -> None:
    frozen.require(
        hasattr(snapshot, "st_mode") and stat.S_ISDIR(snapshot.st_mode),
        "an exact bounded evidence parent is not a real directory",
    )


def _validate_file_stat(snapshot: Any, expected_size: int) -> None:
    frozen.require(
        hasattr(snapshot, "st_mode")
        and stat.S_ISREG(snapshot.st_mode)
        and type(snapshot.st_size) is int
        and 0 < snapshot.st_size <= MAX_EVIDENCE_BYTES
        and snapshot.st_size == expected_size,
        "bounded evidence is a symlink, nonregular, oversized, or truncated",
    )


def _same_file_stat(first: Any, second: Any) -> bool:
    return all(
        getattr(first, name, None) == getattr(second, name, None)
        for name in (
            "st_dev", "st_ino", "st_mode", "st_size",
            "st_mtime_ns", "st_ctime_ns",
        )
    )


def read_exact_evidence(
    relative: str, *, expected_sha256: str,
) -> tuple[dict[str, Any], str]:
    """Read exactly one pinned V17 result using root-anchored descriptors."""

    parts, expected_size = _exact_evidence_target(relative, expected_sha256)
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    directory_flags |= getattr(os, "O_CLOEXEC", 0)
    directory_flags |= getattr(os, "O_NOFOLLOW", 0)
    directory = os.open(ROOT, directory_flags)
    try:
        _validate_directory_stat(os.fstat(directory))
        for part in parts[:-1]:
            child = os.open(part, directory_flags, dir_fd=directory)
            try:
                _validate_directory_stat(os.fstat(child))
            except BaseException:
                os.close(child)
                raise
            os.close(directory)
            directory = child
        flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(parts[-1], flags, dir_fd=directory)
        try:
            before = os.fstat(descriptor)
            _validate_file_stat(before, expected_size)
            pending = expected_size
            payload = bytearray()
            hashed = _FROZEN_SHA256()
            while pending:
                chunk = os.read(descriptor, min(READ_CHUNK_BYTES, pending))
                frozen.require(bool(chunk),
                               "the bounded evidence was truncated during read")
                payload.extend(chunk)
                frozen.require(len(payload) <= MAX_EVIDENCE_BYTES,
                               "the evidence exceeded its immutable 32 MiB cap")
                hashed.update(chunk)
                pending -= len(chunk)
            frozen.require(
                os.read(descriptor, 1) == b"",
                "the actual bounded evidence grew while being streamed",
            )
            after = os.fstat(descriptor)
            _validate_file_stat(after, expected_size)
            frozen.require(
                _same_file_stat(before, after),
                "bounded evidence was substituted or changed during reading",
            )
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)
    actual_sha = hashed.hexdigest()
    frozen.require(actual_sha == expected_sha256,
                   "the streamed genuine complete V17 evidence was substituted")
    document = _parse_durable_payload(
        bytes(payload),
        expected_sha256=expected_sha256,
        expected_size=expected_size,
    )
    return document, actual_sha


def _authenticate_provenance() -> dict[str, Any]:
    stage17.official_locale.verify_runtime()
    frozen.candidate_free()
    for relative, expected in (
        (STAGE17_SOURCE_RELATIVE, STAGE17_SOURCE_SHA256),
        (STAGE17_PROTOCOL_RELATIVE, STAGE17_PROTOCOL_SHA256),
    ):
        stage17._verify_source(relative, expected)
    provenance = stage17._authenticate_provenance()
    frozen.require(
        isinstance(provenance, dict)
        and provenance.get("source_path") == STAGE17_SOURCE_RELATIVE
        and provenance.get("source_sha256") == STAGE17_SOURCE_SHA256
        and provenance.get("protocol_path") == STAGE17_PROTOCOL_RELATIVE
        and provenance.get("protocol_sha256") == STAGE17_PROTOCOL_SHA256
        and provenance.get("matrix_sha256") == stage17.MATRIX_SHA256
        and provenance.get("stage15_reference_status") == "FALSIFIED"
        and provenance.get("stage15_failure_sha256") == V15_FAILURE_SHA256
        and provenance.get("stage15_reference_record_count") == 7_168
        and provenance.get("stage15_candidate_runs") == 0,
        "the bounded reader rejected substituted current V17 or failure proofs",
    )
    frozen.candidate_free()
    return provenance


def _read_validated_pair(
    *, provenance: dict[str, Any],
    expected_self_sha256: str,
    expected_all_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    reference, reference_sha = read_exact_evidence(
        SELF_ORACLE_RELATIVE,
        expected_sha256=expected_self_sha256,
    )
    frozen.require(
        reference_sha == SELF_ORACLE_SHA256
        and stage17._validate_complete_reference(reference, provenance)
        is reference,
        "the exact complete Python reference failed its genuine V17 validator",
    )
    all_candidates, all_sha = read_exact_evidence(
        ALL_CANDIDATE_RELATIVE,
        expected_sha256=expected_all_sha256,
    )
    frozen.require(
        all_sha == ALL_CANDIDATE_SHA256
        and stage17._validate_complete_all(
            all_candidates,
            reference=reference,
            provenance=provenance,
        ) is all_candidates,
        "the exact complete native results failed their genuine V17 validator",
    )
    frozen.candidate_free()
    return reference, all_candidates


def read_stage17_self_and_all(
    *, expected_self_sha256: str, expected_all_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Read and validate both complete frozen reports without production."""

    return _read_validated_pair(
        provenance=_authenticate_provenance(),
        expected_self_sha256=expected_self_sha256,
        expected_all_sha256=expected_all_sha256,
    )


def validate_v17_evidence() -> dict[str, Any]:
    """Return both fully validated real reports; never write or run workers."""

    provenance = _authenticate_provenance()
    reference, all_candidates = _read_validated_pair(
        provenance=provenance,
        expected_self_sha256=SELF_ORACLE_SHA256,
        expected_all_sha256=ALL_CANDIDATE_SHA256,
    )
    reader_source = stage17.official_locale.sha256_path(
        stage17.official_locale.checked_repo_path(SOURCE_RELATIVE),
        maximum=frozen.MAX_SOURCE_BYTES,
    )
    reader_protocol = stage17.official_locale.sha256_path(
        stage17.official_locale.checked_repo_path(PROTOCOL_RELATIVE),
        maximum=frozen.MAX_SOURCE_BYTES,
    )
    frozen.candidate_free()
    return {
        "schema": SCHEMA,
        "status": "PASS", "result": "PASS",
        "source_path": SOURCE_RELATIVE,
        "source_sha256": reader_source,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": reader_protocol,
        "current_provenance": provenance,
        "reference": reference,
        "all_candidates": all_candidates,
        "reference_sha256": SELF_ORACLE_SHA256,
        "all_candidates_sha256": ALL_CANDIDATE_SHA256,
        "reference_bytes": SELF_ORACLE_BYTES,
        "all_candidates_bytes": ALL_CANDIDATE_BYTES,
        "max_evidence_bytes": MAX_EVIDENCE_BYTES,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }


def self_test() -> dict[str, Any]:
    """Exercise strict malformed-input controls without touching a file."""

    frozen.candidate_free()
    inherited = stage17.self_test()
    frozen.require(
        inherited.get("status") == "PASS"
        and inherited.get("check_count", 0) >= 200
        and inherited.get("candidate_imports") == 0
        and inherited.get("candidate_processes") == 0
        and inherited.get("files_read") == 0
        and inherited.get("files_written") == 0
        and inherited.get("clock_samples") == 0,
        "the immutable repaired V17 durable-source controls were weakened",
    )
    with stage17.stage06.previous._candidate_free_file_and_timing_guard() as effects:
        checks: list[dict[str, Any]] = []

        def check(name: str, condition: Any) -> None:
            frozen.require(bool(condition),
                           "a bounded evidence control failed: " + name)
            checks.append({"name": name, "passed": True})

        def reject(name: str, operation: Callable[[], Any]) -> None:
            try:
                operation()
            except (
                frozen.OracleIntegrityError, AssertionError,
                AttributeError, KeyError, OSError, TypeError,
                UnicodeError, ValueError,
            ):
                check(name, True)
            else:
                check(name, False)

        check("inherit-the-real-repaired-207-durable-source-controls",
              inherited["check_count"] >= 200)
        check("freeze-only-the-necessary-33554432-byte-ceiling",
              MAX_EVIDENCE_BYTES == 32 * 1024 * 1024
              and ALL_CANDIDATE_BYTES == 20_220_593
              and SELF_ORACLE_BYTES == 11_556_111
              and SELF_ORACLE_BYTES < ALL_CANDIDATE_BYTES
              < MAX_EVIDENCE_BYTES)
        check("allow-only-two-genuine-frozen-complete-stage17-evidence-paths",
              set(APPROVED_EVIDENCE)
              == {SELF_ORACLE_RELATIVE, ALL_CANDIDATE_RELATIVE})
        check("retain-both-actual-published-complete-report-fingerprints",
              all(stage17.official_locale.is_sha256(value[0])
                  for value in APPROVED_EVIDENCE.values()))
        for path, (fingerprint, size) in APPROVED_EVIDENCE.items():
            check("accept-exact-frozen-evidence-path/" + Path(path).name,
                  _exact_evidence_target(path, fingerprint)
                  == (tuple(PurePosixPath(path).parts), size))
            for kind, poisoned, poisoned_sha in (
                ("absolute", "/" + path, fingerprint),
                ("traversal", "../" + path, fingerprint),
                ("double-separator", path.replace("/", "//", 1), fingerprint),
                ("backslash", path.replace("/", "\\", 1), fingerprint),
                ("nul", path + "\x00", fingerprint),
                ("unpinned-hash", path, "0" * 64),
                ("missing-hash", path, None),
                ("other-evidence", stage17.V15_RAW_REFERENCE_RELATIVE,
                 fingerprint),
                ("hidden-fixture", "benchmarks/holdout.json", fingerprint),
            ):
                reject(
                    "reject-unapproved-bounded-evidence/"
                    + Path(path).name + "/" + kind,
                    lambda relative=poisoned, expected=poisoned_sha: (
                        _exact_evidence_target(relative, expected)
                    ),
                )

        synthetic = {
            "nested": ["\ud800", "\udfff", {
                "type": stage17.stage10.previous.SURROGATE_TAG,
                "encoding": "utf-8/surrogatepass",
                "hex": "eda080",
            }],
            "status": "PASS",
        }
        payload = stage17.canonical(synthetic) + b"\n"
        fingerprint = _FROZEN_SHA256(payload).hexdigest()
        parsed = _parse_durable_payload(
            payload, expected_sha256=fingerprint, expected_size=len(payload),
        )
        check("parse-exact-canonical-raw-and-tagged-surrogates-once",
              parsed == synthetic
              and stage17.canonical(parsed) + b"\n" == payload)
        check("preserve-the-exact-frozen-ascii-json-payload-digest",
              _FROZEN_SHA256(payload).hexdigest() == fingerprint)
        poison_payloads = (
            ("empty", b""),
            ("invalid-utf8", b"{\"x\":\xff}\n"),
            ("malformed-json", b"{\"x\":}\n"),
            ("truncated-json", b"{\"x\":1\n"),
            ("duplicate-key", b"{\"x\":1,\"x\":2}\n"),
            ("nan", b"{\"x\":NaN}\n"),
            ("infinity", b"{\"x\":Infinity}\n"),
            ("negative-infinity", b"{\"x\":-Infinity}\n"),
            ("trailing-bytes", payload + b"foreign"),
            ("extra-newline", payload + b"\n"),
            ("missing-newline", payload[:-1]),
            ("noncanonical-whitespace", b'{ "x" : 1 }\n'),
            ("top-level-list", b"[]\n"),
        )
        for kind, invalid in poison_payloads:
            reject(
                "reject-malformed-bounded-json/" + kind,
                lambda value=invalid: _parse_durable_payload(
                    value,
                    expected_sha256=_FROZEN_SHA256(value).hexdigest(),
                ),
            )
        reject(
            "reject-a-correct-payload-with-the-wrong-pinned-sha",
            lambda: _parse_durable_payload(
                payload, expected_sha256="0" * 64,
            ),
        )
        reject(
            "reject-a-correct-payload-with-a-truncated-stated-size",
            lambda: _parse_durable_payload(
                payload,
                expected_sha256=fingerprint,
                expected_size=len(payload) - 1,
            ),
        )

        regular = types.SimpleNamespace(
            st_mode=stat.S_IFREG | 0o600,
            st_size=42,
            st_dev=1,
            st_ino=2,
            st_mtime_ns=3,
            st_ctime_ns=4,
        )
        directory = types.SimpleNamespace(
            st_mode=stat.S_IFDIR | 0o700,
        )
        check("accept-only-a-genuine-root-anchored-directory",
              _validate_directory_stat(directory) is None)
        check("accept-only-a-sized-genuine-regular-evidence-file",
              _validate_file_stat(regular, 42) is None)
        check("preserve-all-six-before-and-after-file-identity-fields",
              _same_file_stat(regular, regular))
        for label, mode, size in (
            ("symlink", stat.S_IFLNK | 0o777, 42),
            ("directory", stat.S_IFDIR | 0o700, 42),
            ("pipe", stat.S_IFIFO | 0o600, 42),
            ("socket", stat.S_IFSOCK | 0o600, 42),
            ("empty", stat.S_IFREG | 0o600, 0),
            ("over-32mib", stat.S_IFREG | 0o600, MAX_EVIDENCE_BYTES + 1),
            ("truncated", stat.S_IFREG | 0o600, 41),
            ("appended", stat.S_IFREG | 0o600, 43),
        ):
            reject(
                "reject-unsafe-file-descriptor/" + label,
                lambda permission=mode, length=size: _validate_file_stat(
                    types.SimpleNamespace(st_mode=permission, st_size=length),
                    42,
                ),
            )
        reject(
            "reject-a-symlink-in-an-evidence-parent",
            lambda: _validate_directory_stat(types.SimpleNamespace(
                st_mode=stat.S_IFLNK | 0o777,
            )),
        )
        for field in (
            "st_dev", "st_ino", "st_mode", "st_size",
            "st_mtime_ns", "st_ctime_ns",
        ):
            altered = types.SimpleNamespace(**vars(regular))
            setattr(altered, field, getattr(altered, field) + 1)
            check("detect-in-stream-file-substitution/" + field,
                  not _same_file_stat(regular, altered))

        source, reference, all_candidates = stage17._synthetic_full()
        parsed_reference, raw_reference = stage17._durable_round_trip(reference)
        parsed_all, raw_all = stage17._durable_round_trip(all_candidates)
        check("accept-a-complete-context-free-durable-python-reference",
              stage17._validate_complete_reference(
                  parsed_reference, source,
              ) is parsed_reference)
        check("accept-all-10752-context-free-durable-native-observations",
              stage17._validate_complete_all(
                  parsed_all,
                  reference=parsed_reference,
                  provenance=source,
              ) is parsed_all)
        check("keep-full-synthetic-reports-below-the-declared-32mib-bound",
              len(raw_reference) < MAX_EVIDENCE_BYTES
              and len(raw_all) < MAX_EVIDENCE_BYTES)
        for output, document in (
            ("reference", parsed_reference),
            ("all-candidates", parsed_all),
        ):
            actual = stage17.canonical(document) + b"\n"
            parsed_document = _parse_durable_payload(
                actual,
                expected_sha256=_FROZEN_SHA256(actual).hexdigest(),
                expected_size=len(actual),
            )
            check("round-trip-the-complete-real-shape-report/" + output,
                  parsed_document == document)

        check("never-open-a-file-or-start-a-worker",
              all(value == 0 for value in effects.values()))
        frozen.candidate_free()
        names = [item["name"] for item in checks]
        frozen.require(len(names) == len(set(names)) and len(checks) >= 45,
                       "a bounded-reader malicious-input safeguard was weakened")
        return {
            "schema": SELF_TEST_SCHEMA,
            "status": "PASS", "result": "PASS",
            "check_count": len(checks), "checks": checks, "failed": [],
            "inherited_stage17_control_count": inherited["check_count"],
            "max_evidence_bytes": MAX_EVIDENCE_BYTES,
            "approved_evidence_paths": list(APPROVED_EVIDENCE),
            "reference_sha256": SELF_ORACLE_SHA256,
            "all_candidates_sha256": ALL_CANDIDATE_SHA256,
            "reference_bytes": SELF_ORACLE_BYTES,
            "all_candidates_bytes": ALL_CANDIDATE_BYTES,
            "candidate_imports": 0, "candidate_processes": 0,
            "files_read": 0, "files_written": 0,
            "clock_samples": 0, "entropy_drawn": False,
            "production_evidence_written": False,
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--validate", action="store_true")
    options = parser.parse_args(argv)
    try:
        if options.self_test:
            result = self_test()
        else:
            bundle = validate_v17_evidence()
            result = {
                key: value for key, value in bundle.items()
                if key not in {"reference", "all_candidates", "current_provenance"}
            }
        sys.stdout.buffer.write(stage17.canonical(result) + b"\n")
        sys.stdout.buffer.flush()
        return 0
    except (
        frozen.OracleIntegrityError, AssertionError, AttributeError,
        ImportError, KeyError, OSError, TypeError, UnicodeError, ValueError,
    ) as error:
        sys.stderr.buffer.write(stage17.canonical({
            "schema": SCHEMA, "status": "FAIL", "error": str(error),
        }) + b"\n")
        sys.stderr.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
