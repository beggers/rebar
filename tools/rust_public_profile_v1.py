#!/usr/bin/env python3
"""Frozen, fresh-public-only, correctness-gated Rust/CPython profiling.

``--verify-source`` and ``--self-test`` never import a candidate, spawn a
process, sample a clock, start a profiler, or mutate the workspace.  Candidate
execution, paired timing, native CPU/heap collection, and approved publication
are possible only through an explicit ``--run`` after complete public parity.
No fixture, prior result, holdout, archive, or undisclosed input is consumed.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import hashlib
import importlib
from importlib.machinery import EXTENSION_SUFFIXES, ExtensionFileLoader
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys
import types
from typing import Any, Callable, Mapping
import warnings


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/rust_public_profile_v1.py"
MANIFEST_RELATIVE = "oracle/phase3/rust-public-profile-v1.json"
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
)
PINNED_STDLIB_RE = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/re/__init__.py",
)
GPROFNG = Path("/usr/bin/gprofng")
GPROFNG_EXECUTABLE = Path("/usr/bin/x86_64-linux-gnu-gprofng")
GPROFNG_COLLECTOR = Path("/usr/bin/x86_64-linux-gnu-gp-collect-app")
GPROFNG_DISPLAY = Path("/usr/bin/x86_64-linux-gnu-gp-display-text")
APPROVED_OUTPUT_PREFIX = "experiments/rust_public_profile_v1"
SCHEMA = "rebar-rust-fresh-public-profile-v1"
PUBLIC_LABEL = "FRESH PUBLIC PRACTICE ONLY; NOT A HOLDOUT OR FINAL BENCHMARK"
PUBLISHED_SEED = 0x5255_5354_5052_4F31
MATRIX_SHA256 = "b13ff74122041ea792774fd5ee2d1f6d38033e94a1a6703c6e48522e461552a7"
MAX_SOURCE_BYTES = 2 * 1024 * 1024
MAX_PROCESS_BYTES = 32 * 1024 * 1024
MAX_ARTIFACT_BYTES = 64 * 1024 * 1024
DEFAULT_PAIRED_ROUNDS = 4
DEFAULT_BATCH_ITERATIONS = 3
DEFAULT_WARMUP_ITERATIONS = 1
DEFAULT_PROFILE_PASSES = 3
PROCESS_TIMEOUT_SECONDS = 600
MULTILINE = 8
IGNORECASE = 2

OPERATIONS = (
    "module.compile",
    "module.search",
    "module.match",
    "module.fullmatch",
    "module.findall",
    "module.finditer",
    "module.split",
    "module.sub.literal",
    "module.sub.callback",
    "module.subn.literal",
    "pattern.search",
    "pattern.match",
    "pattern.fullmatch",
    "pattern.findall",
    "pattern.finditer",
    "pattern.split",
    "pattern.sub.literal",
    "pattern.sub.callback",
    "pattern.subn.literal",
    "pattern.scanner.search",
    "pattern.scanner.match",
    "pattern.scanner.loop",
    "scanner.scan",
    "match.group",
    "match.expand",
    "compile.fresh.search",
)

FORBIDDEN_OUTPUT_TOKENS = (
    "archive", "final", "fixture", "hidden", "holdout", "legacy",
    "private", "sealed", "secret",
)
FORBIDDEN_REFERENCE_ROOTS = frozenset({
    "re", "_sre", "regex", "_regex", "re2", "pcre", "pcre2",
    "oniguruma", "sre_compile", "sre_parse", "sre_constants",
})
NATIVE_FFI_MARKERS = (
    "rebar_compile", "rebar_match", "rebar_collect", "_rust_bridge",
    "_rust_engine", "bridge_compile", "rust_pattern", "rust_scanner",
)
PROFILE_REPORTS = {
    "cpu": "-functions",
    "ffi": "-callers-callees",
    "allocations": "-allocs",
    "heap": "-heapstat",
}


class PublicProfileError(Exception):
    """Fail closed on changed public input, isolation, correctness, or output."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise PublicProfileError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, allow_nan=False,
        sort_keys=True, separators=(",", ":"),
    ).encode("ascii") + b"\n"


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in result,
                "duplicate JSON object keys are forbidden")
        result[key] = value
    return result


def decode_document(
    payload: bytes, label: str, *, canonical_required: bool = True,
) -> dict[str, Any]:
    require(type(payload) is bytes and 0 < len(payload) <= MAX_PROCESS_BYTES,
            "bounded complete public-profile JSON is required: " + label)
    try:
        result = json.loads(
            payload, object_pairs_hook=_unique_json_object,
            parse_constant=lambda value: (_ for _ in ()).throw(
                PublicProfileError("nonfinite public-profile JSON is forbidden"),
            ),
        )
    except (ValueError, TypeError, UnicodeError, json.JSONDecodeError) as error:
        raise PublicProfileError("invalid public-profile JSON: " + label) from error
    require(type(result) is dict
            and (not canonical_required or canonical(result) == payload),
            "substituted or noncanonical public-profile JSON: " + label)
    return result


def encode_typed(value: Any) -> dict[str, Any]:
    if type(value) is str:
        return {"kind": "str", "value": value}
    if type(value) is bytes:
        return {"kind": "bytes", "hex": value.hex()}
    if type(value) is bytearray:
        return {"kind": "bytearray", "hex": bytes(value).hex()}
    if type(value) is memoryview:
        require(value.format == "B" and value.ndim == 1 and value.contiguous,
                "an original one-dimensional public byte carrier is required")
        return {
            "kind": "memoryview", "hex": value.tobytes().hex(),
            "readonly": value.readonly, "format": value.format,
            "shape": list(value.shape),
        }
    raise PublicProfileError("an original fresh public input type was substituted")


def decode_typed(value: Any) -> str | bytes | bytearray | memoryview:
    require(type(value) is dict, "an exact public input document is mandatory")
    kind = value.get("kind")
    if kind == "str":
        require(set(value) == {"kind", "value"}
                and type(value.get("value")) is str,
                "an exact fresh public text input was substituted")
        return value["value"]
    if kind in ("bytes", "bytearray", "memoryview"):
        try:
            actual = bytes.fromhex(value.get("hex"))
        except (TypeError, ValueError) as error:
            raise PublicProfileError("invalid public byte encoding") from error
        require(actual.hex() == value.get("hex"),
                "noncanonical fresh public byte encoding")
        if kind == "bytes":
            require(set(value) == {"kind", "hex"},
                    "the exact fresh public bytes shape changed")
            return actual
        if kind == "bytearray":
            require(set(value) == {"kind", "hex"},
                    "the exact fresh public bytearray shape changed")
            return bytearray(actual)
        require(set(value) == {"kind", "hex", "readonly", "format", "shape"}
                and type(value.get("readonly")) is bool
                and value.get("format") == "B"
                and value.get("shape") == [len(actual)],
                "the original public memoryview mutability or shape changed")
        return memoryview(actual if value["readonly"] else bytearray(actual))
    raise PublicProfileError("an original fresh public carrier was substituted")


def _fresh_public_datasets() -> tuple[tuple[str, str, Any, Any, int, str], ...]:
    """All case material originates solely in the literals in this function."""
    text_capture_spill = "(?:" + "(a)" * 40 + "){2}Z"
    text_assertion_spill = "(?=(?:" + "(a)" * 36 + ")Z)a{36}Z"
    bytes_capture_spill = ("(?:" + "(a)" * 40 + "){2}Z").encode("ascii")
    bytes_assertion_spill = (
        "(?=(?:" + "(a)" * 36 + ")Z)a{36}Z"
    ).encode("ascii")
    return (
        (
            "text.dense-first-byte.literal.no-match", "text",
            "AAAAAAB", "A" * 2_048 + "C", 0,
            "mandatory_literal_dense_same_first_byte",
        ),
        (
            "text.dense-first-byte.alternation.no-match", "text",
            "(?:AAAAAAB|AAAAAAC)", "A" * 2_048 + "D", 0,
            "mandatory_literal_dense_same_first_byte",
        ),
        (
            "text.capture.guard.spill", "text", text_capture_spill,
            "a" * 80 + "Z", 0, "overflow_capture_guard_heap_spill",
        ),
        (
            "text.repeat.guard.spill", "text", r"(?:(?:ab){16}){4}Z",
            "ab" * 64 + "Z", 0, "overflow_repeat_guard_heap_spill",
        ),
        (
            "text.assertion.guard.spill", "text", text_assertion_spill,
            "a" * 36 + "Z", 0, "overflow_assertion_guard_heap_spill",
        ),
        (
            "text.unicode.named.words", "text",
            r"(?P<token>[^\W\d_]+)(?P<digits>\d*)",
            "Éclair42 Ζeta7 naïve3 cedar8", 0, "unicode_and_named_captures",
        ),
        (
            "text.scanner.remainder", "text",
            r"(?P<token>[A-Za-z]+)(?P<digits>\d*)",
            "oak12 pine7 !fresh-tail9", 0, "scanner_and_callback_boundary",
        ),
        (
            "text.multiline.anchors", "text",
            r"^(?P<token>[a-z]+)(?P<digits>\d*)$",
            "maple7\nCEDAR8\nspruce9", MULTILINE | IGNORECASE,
            "anchored_multiline_public",
        ),
        (
            "bytes.dense-first-byte.literal.no-match", "bytes",
            b"AAAAAAB", b"A" * 2_048 + b"C", 0,
            "mandatory_literal_dense_same_first_byte",
        ),
        (
            "bytes.dense-first-byte.alternation.no-match", "bytes",
            rb"(?:AAAAAAB|AAAAAAC)", memoryview(b"A" * 2_048 + b"D"), 0,
            "mandatory_literal_dense_same_first_byte",
        ),
        (
            "bytes.capture.guard.spill", "bytes", bytes_capture_spill,
            bytearray(b"a" * 80 + b"Z"), 0,
            "overflow_capture_guard_heap_spill",
        ),
        (
            "bytes.repeat.guard.spill", "bytes", rb"(?:(?:ab){16}){4}Z",
            b"ab" * 64 + b"Z", 0, "overflow_repeat_guard_heap_spill",
        ),
        (
            "bytes.assertion.guard.spill", "bytes", bytes_assertion_spill,
            b"a" * 36 + b"Z", 0, "overflow_assertion_guard_heap_spill",
        ),
        (
            "bytes.high-bit.named.words", "bytes",
            rb"(?P<token>[A-Za-z]+)(?P<digits>\d*)",
            b"\xe9oak42 cedar7 \xfffir3", 0,
            "unicode_and_named_captures",
        ),
        (
            "bytes.scanner.mutable-memoryview.remainder", "bytes",
            rb"(?P<token>[A-Za-z]+)(?P<digits>\d*)",
            memoryview(bytearray(b"oak12 pine7 !fresh-tail9")), 0,
            "scanner_and_callback_boundary",
        ),
        (
            "bytes.multiline.anchors", "bytes",
            rb"^(?P<token>[a-z]+)(?P<digits>\d*)$",
            b"maple7\nCEDAR8\nspruce9", MULTILINE | IGNORECASE,
            "anchored_multiline_public",
        ),
    )


def build_public_matrix() -> list[dict[str, Any]]:
    matrix: list[dict[str, Any]] = []
    for dataset_index, (name, domain, expression, subject, flags, cohort) \
            in enumerate(_fresh_public_datasets()):
        phrase = r"[A-Za-z]+\d*" if domain == "text" else rb"[A-Za-z]+\d*"
        replacement = r"<\g<0>>" if domain == "text" else rb"<\g<0>>"
        for operation_index, operation in enumerate(OPERATIONS):
            lifecycle = (
                "fresh-native-compile" if operation == "compile.fresh.search"
                else "native-scanner-boundary" if operation == "scanner.scan"
                else "module-call" if operation.startswith("module.")
                else "live-match" if operation.startswith("match.")
                else "live-pattern-scanner" if ".scanner." in operation
                else "precompiled-pattern"
            )
            matrix.append({
                "case": "rust-public-profile.v1." + format(len(matrix), "04d"),
                "dataset": name, "domain": domain, "cohort": cohort,
                "operation": operation, "lifecycle": lifecycle,
                "pattern": encode_typed(expression),
                "subject": encode_typed(subject),
                "replacement": encode_typed(replacement),
                "scanner_phrase": encode_typed(phrase),
                "flags": flags,
                "limit": 1 + (
                    (PUBLISHED_SEED + dataset_index * 37 + operation_index * 11)
                    % 3
                ),
                "weight_numerator": 1,
            })
    return matrix


def validate_public_matrix(matrix: Any) -> str:
    require(type(matrix) is list and len(matrix) == 16 * len(OPERATIONS)
            and matrix == build_public_matrix()
            and len({case["case"] for case in matrix}) == len(matrix)
            and digest(matrix) == MATRIX_SHA256,
            "the frozen fresh public profile cases, seed, or denominator changed")
    for operation in OPERATIONS:
        require(sum(case["operation"] == operation for case in matrix) == 16,
                "an exact balanced public operation was removed: " + operation)
    require(sum(case["domain"] == "text" for case in matrix)
            == sum(case["domain"] == "bytes" for case in matrix)
            == 8 * len(OPERATIONS),
            "fresh text and bytes must retain exactly equal public weight")
    for cohort in (
        "mandatory_literal_dense_same_first_byte",
        "overflow_capture_guard_heap_spill",
        "overflow_repeat_guard_heap_spill",
        "overflow_assertion_guard_heap_spill",
    ):
        require(any(case["cohort"] == cohort and case["domain"] == "text"
                    for case in matrix)
                and any(case["cohort"] == cohort and case["domain"] == "bytes"
                        for case in matrix),
                "an independently required balanced public cohort vanished: "
                + cohort)
    return MATRIX_SHA256


def _directory_open_flags() -> int:
    return (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    )


def _read_frozen_owned_file(relative: str) -> bytes:
    require(relative in (SOURCE_RELATIVE, MANIFEST_RELATIVE),
            "only the exact public profile source and manifest may be read")
    parts = PurePosixPath(relative).parts
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), _directory_open_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the frozen workspace root is not a real no-follow directory")
        for name in parts[:-1]:
            current = os.open(name, _directory_open_flags(), dir_fd=current)
            opened.append(current)
            require(stat.S_ISDIR(os.fstat(current).st_mode),
                    "a frozen source component is not a no-follow directory")
        descriptor = os.open(
            parts[-1], os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0), dir_fd=current,
        )
        opened.append(descriptor)
        require(stat.S_ISREG(os.fstat(descriptor).st_mode),
                "a frozen public source component is not a regular file")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, 128 * 1024)
            if not chunk:
                break
            total += len(chunk)
            require(total <= MAX_SOURCE_BYTES,
                    "a frozen public profile source exceeds its bounded size")
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def verify_pinned_runtime(*, permit_candidate: bool = False) -> None:
    expected_source = str(ROOT / SOURCE_RELATIVE)
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
            and os.path.realpath(sys.executable) == str(PINNED_PYTHON)
            and os.path.realpath(str(ROOT)) == str(ROOT)
            and os.path.abspath(__file__) == expected_source
            and os.path.realpath(__file__) == expected_source,
            "use the exact pinned isolated CPython and no-symlink frozen source")
    if not permit_candidate:
        require(not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ), "a candidate escaped into a strictly candidate-free source mode")


def _expected_profiler_manifest() -> dict[str, dict[str, str]]:
    return {
        "dispatcher": {
            "path": str(GPROFNG_EXECUTABLE),
            "sha256": (
                "91e03573aeedded12a3b80e96ba28316968a8a86af78f0434"
                "cd7e87b7691df62"
            ),
        },
        "collector": {
            "path": str(GPROFNG_COLLECTOR),
            "sha256": (
                "1b12058e818536a7c9febf81d621acf182d261f8464b1aee5"
                "d745be5dfcfa2b2"
            ),
        },
        "display": {
            "path": str(GPROFNG_DISPLAY),
            "sha256": (
                "2d7e0d598c873dc2b7735edc49309b7fab9db821cbb749b5a"
                "b8d62d1b9b66112"
            ),
        },
    }


def verify_frozen_source() -> dict[str, Any]:
    verify_pinned_runtime()
    source = _read_frozen_owned_file(SOURCE_RELATIVE)
    manifest_payload = _read_frozen_owned_file(MANIFEST_RELATIVE)
    manifest = decode_document(
        manifest_payload, "frozen public profile source manifest",
        canonical_required=False,
    )
    matrix = build_public_matrix()
    validate_public_matrix(matrix)
    source_sha256 = hashlib.sha256(source).hexdigest()
    expected_keys = {
        "schema", "source", "source_sha256", "published_seed",
        "matrix_sha256", "dataset_count", "case_count", "operation_count",
        "pinned_python", "pinned_cpython", "approved_output_prefix",
        "profiler", "profile_configuration", "provenance",
    }
    require(set(manifest) == expected_keys
            and manifest.get("schema") == SCHEMA + "-source-freeze"
            and manifest.get("source") == SOURCE_RELATIVE
            and manifest.get("source_sha256") == source_sha256
            and manifest.get("published_seed") == PUBLISHED_SEED
            and manifest.get("matrix_sha256") == MATRIX_SHA256
            and manifest.get("dataset_count") == 16
            and manifest.get("case_count") == len(matrix)
            and manifest.get("operation_count") == len(OPERATIONS)
            and manifest.get("pinned_python") == str(PINNED_PYTHON)
            and manifest.get("pinned_cpython") == "3.14.6"
            and manifest.get("approved_output_prefix") == APPROVED_OUTPUT_PREFIX
            and manifest.get("profiler") == {
                "command": str(GPROFNG),
                "binaries": _expected_profiler_manifest(),
                "archive_policy": "off",
                "descendant_policy": "off",
                "heap_tracing": "on",
                "clock_sampling": "hi",
            }
            and manifest.get("profile_configuration") == {
                "paired_rounds": DEFAULT_PAIRED_ROUNDS,
                "batch_iterations": DEFAULT_BATCH_ITERATIONS,
                "warmup_iterations": DEFAULT_WARMUP_ITERATIONS,
                "profile_passes": DEFAULT_PROFILE_PASSES,
                "reports": sorted(PROFILE_REPORTS),
            }
            and manifest.get("provenance") == {
                "data": "fresh embedded public literals only",
                "candidate_imports_in_source_modes": 0,
                "fixture_files_read": 0,
                "holdout_files_read": 0,
                "archive_files_read": 0,
                "source_mode_clock_samples": 0,
                "source_mode_workspace_mutations": 0,
            },
            "the exact frozen public source, protocol, or manifest was changed")
    return {
        "schema": SCHEMA + "-source-verification", "status": "PASS",
        "label": PUBLIC_LABEL, "source": SOURCE_RELATIVE,
        "source_sha256": source_sha256,
        "manifest_sha256": hashlib.sha256(manifest_payload).hexdigest(),
        "published_seed": PUBLISHED_SEED, "matrix_sha256": MATRIX_SHA256,
        "case_count": len(matrix), "operation_count": len(OPERATIONS),
        "candidate_import_count": 0, "processes_started": 0,
        "clock_samples": 0, "profiler_runs": 0,
        "workspace_mutations": 0, "files_written": 0,
        "fixture_files_read": 0, "holdout_files_read": 0,
        "archive_files_read": 0,
    }


def _approved_session_parts(value: Any) -> tuple[str, ...]:
    require(type(value) is str and bool(value)
            and "\x00" not in value and "\\" not in value,
            "one exact approved public-profile summary path is mandatory")
    if os.path.isabs(value):
        prefix = str(ROOT) + "/"
        require(value.startswith(prefix),
                "a public-profile path outside the owned workspace is forbidden")
        relative = value[len(prefix):]
    else:
        relative = value
    path = PurePosixPath(relative)
    require(not path.is_absolute() and path.as_posix() == relative
            and len(path.parts) == 4
            and path.parts[:2] == ("experiments", "rust_public_profile_v1")
            and path.parts[-1] == "summary.json",
            "use exactly experiments/rust_public_profile_v1/<session>/summary.json")
    session = path.parts[2]
    require(1 <= len(session) <= 80
            and session[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(character in "abcdefghijklmnopqrstuvwxyz0123456789-"
                    for character in session)
            and not any(token in session for token in FORBIDDEN_OUTPUT_TOKENS),
            "the public-profile session has a hostile or unapproved component")
    return path.parts


def _approved_artifact_name(value: Any) -> str:
    require(type(value) is str and 1 <= len(value) <= 120
            and value[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
            and all(character in "abcdefghijklmnopqrstuvwxyz0123456789-."
                    for character in value)
            and ".." not in value
            and not any(token in value for token in FORBIDDEN_OUTPUT_TOKENS),
            "an approved profile artifact name was substituted")
    return value


def _collector_command(engine: str) -> list[str]:
    require(engine in ("stdlib", "rust"),
            "only the original CPython and named Rust workers can be profiled")
    return [
        str(GPROFNG), "collect", "app",
        "-a", "off", "-F", "off", "-j", "off", "-S", "off",
        "-p", "hi", "-H", "on", "-o", engine + ".er",
        str(PINNED_PYTHON), "-I", "-B", str(ROOT / SOURCE_RELATIVE),
        "--internal-worker", "--engine", engine, "--worker-mode", "profile",
        "--role", "public-profile-" + engine,
    ]


def source_self_test() -> dict[str, Any]:
    verification = verify_frozen_source()
    matrix = build_public_matrix()
    validate_public_matrix(matrix)
    for case in matrix:
        for field in ("pattern", "subject", "replacement", "scanner_phrase"):
            require(encode_typed(decode_typed(case[field])) == case[field],
                    "a fresh public carrier failed an exact source-only round trip")
    dense = [
        case for case in matrix
        if case["operation"] == "pattern.search"
        and case["cohort"] == "mandatory_literal_dense_same_first_byte"
    ]
    dense_first_byte_counts = []
    for case in dense:
        subject = decode_typed(case["subject"])
        count = subject.count("A") if type(subject) is str \
            else bytes(subject).count(b"A")
        dense_first_byte_counts.append(count)
    require(len(dense) == 4
            and all(count >= 2_048 for count in dense_first_byte_counts),
            "a genuine dense same-first-byte no-match public cohort disappeared")
    capture_cases = [
        case for case in matrix
        if case["operation"] == "module.compile"
        and case["cohort"] == "overflow_capture_guard_heap_spill"
    ]
    require(len(capture_cases) == 2 and all(
        decode_typed(case["pattern"]).count(
            "(a)" if case["domain"] == "text" else b"(a)"
        ) == 40 for case in capture_cases
    ), "the independent forty-capture overflow allocation cohort disappeared")
    approved = _approved_session_parts(
        "experiments/rust_public_profile_v1/public-run-001/summary.json",
    )
    require(approved == (
        "experiments", "rust_public_profile_v1", "public-run-001", "summary.json",
    ), "the one exact approved public output layout changed")
    hostile_paths = (
        "/tmp/public-profile-escape/summary.json",
        "../experiments/rust_public_profile_v1/public-run/summary.json",
        "experiments/rust_public_profile_v1/../escape/summary.json",
        "experiments/rust_public_profile_v1/public-run/../summary.json",
        "experiments/rust_public_profile_v1/public-run//summary.json",
        "experiments/rust_public_profile_v1/public-run/report.json",
        "experiments/rust_public_profile_v1/.public/summary.json",
        "experiments/rust_public_profile_v1/PUBLIC/summary.json",
        "experiments/rust_public_profile_v1/hidden-run/summary.json",
        "experiments/rust_public_profile_v1/legacy-run/summary.json",
        "experiments/rust_public_profile_v1/final-run/summary.json",
        "experiments/rust_public_profile_v1/fixture-run/summary.json",
        "experiments/rust_public_profile_v1/holdout-run/summary.json",
        "experiments/rust_public_profile_v1/archive-run/summary.json",
        "experiments/rust_public_profile_v1/public\\run/summary.json",
        "experiments/rust_public_profile_v1/public\x00run/summary.json",
    )
    rejected = 0
    for value in hostile_paths:
        try:
            _approved_session_parts(value)
        except PublicProfileError:
            rejected += 1
        else:
            raise PublicProfileError("a hostile public output path was accepted")
    for value in ("../rust.er", "/tmp/rust.er", ".rust", "hidden.txt"):
        try:
            _approved_artifact_name(value)
        except PublicProfileError:
            rejected += 1
        else:
            raise PublicProfileError("a hostile profile artifact name was accepted")
    for engine in ("stdlib", "rust"):
        command = _collector_command(engine)
        require(command[0] == str(GPROFNG)
                and command[1:3] == ["collect", "app"]
                and command[3:5] == ["-a", "off"]
                and command[5:7] == ["-F", "off"]
                and command[11:13] == ["-p", "hi"]
                and command[13:15] == ["-H", "on"]
                and command[15:17] == ["-o", engine + ".er"]
                and "archive" not in command,
                "the frozen public CPU/heap no-archive command was changed")
    verification.update({
        "schema": SCHEMA + "-source-self-test",
        "dataset_count": 16,
        "text_case_count": 8 * len(OPERATIONS),
        "bytes_case_count": 8 * len(OPERATIONS),
        "dense_same_first_byte_dataset_count": len(dense),
        "capture_spill_groups": 40,
        "assertion_spill_groups": 36,
        "rejected_hostile_output_count": rejected,
        "approved_profiler_report_kinds": sorted(PROFILE_REPORTS),
        "candidate_owned_reference_import_policy": "DENY",
        "harness_warning_and_inspection_import_policy": "ALLOW",
        "performance": "NOT MEASURED",
        "final_winner_selected": False,
    })
    require(not any(
        name == "candidates" or name.startswith("candidates.")
        for name in sys.modules
    ), "a candidate escaped into the strictly source-only self-test")
    return verification


def _forbidden_reference_name(value: Any) -> bool:
    return type(value) is str \
        and value.split(".", 1)[0] in FORBIDDEN_REFERENCE_ROOTS


def _candidate_owned_filename(value: Any) -> bool:
    return type(value) is str and os.path.isabs(value) \
        and value.startswith(str(ROOT / "candidates") + os.sep)


def _install_candidate_import_guard() -> dict[str, Any]:
    attempts: list[str] = []
    original_import = builtins.__import__

    def guarded_import(
        name: str, globals: Any = None, locals: Any = None,
        fromlist: Any = (), level: int = 0,
    ) -> Any:
        caller = sys._getframe(1)
        if _candidate_owned_filename(caller.f_code.co_filename) \
                and _forbidden_reference_name(name):
            attempts.append(name)
            raise PublicProfileError(
                "candidate-owned production imported a reference regex engine: "
                + name,
            )
        return original_import(name, globals, locals, fromlist, level)

    def guarded_audit(event: str, arguments: tuple[Any, ...]) -> None:
        if event != "import" or not arguments \
                or not _forbidden_reference_name(arguments[0]):
            return
        frame = sys._getframe(1)
        while frame is not None:
            filename = frame.f_code.co_filename
            if filename.startswith("<frozen importlib"):
                frame = frame.f_back
                continue
            if _candidate_owned_filename(filename):
                name = str(arguments[0])
                attempts.append(name)
                raise PublicProfileError(
                    "candidate-owned production imported an external regex engine: "
                    + name,
                )
            break

    builtins.__import__ = guarded_import
    sys.addaudithook(guarded_audit)
    return {"attempts": attempts}


def _authenticate_owned_module(module: Any, label: str) -> str:
    origin = getattr(module, "__file__", None)
    require(type(origin) is str and os.path.isabs(origin)
            and os.path.abspath(origin) == origin
            and os.path.realpath(origin) == origin
            and os.path.commonpath((str(ROOT), origin)) == str(ROOT),
            "the owned public " + label + " origin was substituted")
    return origin


def _authenticate_candidate(candidate: Any, guard: Mapping[str, Any]) -> dict[str, Any]:
    origin = _authenticate_owned_module(candidate, "Rust adapter")
    require(candidate.__name__ == "candidates.rust_candidate"
            and origin == str(ROOT / "candidates/rust_candidate.py"),
            "the exact from-scratch Rust adapter was substituted")
    bridge = sys.modules.get("candidates._rust_bridge")
    require(isinstance(bridge, types.ModuleType),
            "the mandatory native Rust bridge was omitted")
    bridge_origin = _authenticate_owned_module(bridge, "native Rust bridge")
    bridge_spec = getattr(bridge, "__spec__", None)
    loader = getattr(bridge_spec, "loader", None)
    require(bridge.__name__ == "candidates._rust_bridge"
            and os.path.dirname(bridge_origin) == str(ROOT / "candidates")
            and any(bridge_origin.endswith(suffix) for suffix in EXTENSION_SUFFIXES)
            and bridge_spec is not None
            and getattr(bridge_spec, "name", None) == "candidates._rust_bridge"
            and getattr(bridge_spec, "origin", None) == bridge_origin
            and isinstance(loader, ExtensionFileLoader)
            and getattr(loader, "path", None) == bridge_origin,
            "the native Rust extension ownership or loader identity was forged")
    exports = (
        "compile", "compile_scanner", "run", "collect", "pattern_match",
        "pattern_type", "pattern_descriptors", "bind",
    )
    for name in exports:
        value = getattr(bridge, name, None)
        require(isinstance(value, types.BuiltinFunctionType)
                and getattr(value, "__self__", None) is bridge
                and getattr(value, "__module__", None)
                == "candidates._rust_bridge",
                "a mandatory owned native FFI operation was substituted: " + name)
    native = getattr(candidate, "_NATIVE", None)
    require(native is not None
            and getattr(native, "native_compile", None) is bridge.compile
            and getattr(native, "native_free", None) is bridge.free,
            "the Rust adapter's production native FFI surface was substituted")
    for value in vars(candidate).values():
        if isinstance(value, types.ModuleType):
            require(not _forbidden_reference_name(value.__name__),
                    "candidate-owned production retained a reference regex module")
    for name in (
        "compile", "search", "match", "fullmatch", "findall", "finditer",
        "split", "sub", "subn", "Scanner",
    ):
        value = getattr(candidate, name, None)
        module_name = getattr(value, "__module__", None)
        require(value is not None and module_name == "candidates.rust_candidate",
                "a candidate public entry point delegated to a foreign engine: "
                + name)
    require(not guard["attempts"],
            "candidate-owned production attempted a forbidden regex import")
    return {
        "adapter_origin": origin,
        "bridge_origin": bridge_origin,
        "native_bridge_exports": list(exports),
        "candidate_owned_forbidden_import_attempts": [],
        "preexisting_harness_reference_modules": sorted(
            name for name in sys.modules if _forbidden_reference_name(name)
        ),
    }


def load_engine(name: str) -> tuple[Any, dict[str, Any]]:
    require(name in ("stdlib", "rust"),
            "only the pinned CPython baseline and owned Rust engine are allowed")
    verify_pinned_runtime()
    if name == "stdlib":
        engine = importlib.import_module("re")
        require(engine.__name__ == "re"
                and os.path.abspath(engine.__file__) == str(PINNED_STDLIB_RE)
                and os.path.realpath(engine.__file__) == str(PINNED_STDLIB_RE),
                "the original pinned CPython regular-expression baseline changed")
        return engine, {"stdlib_origin": str(PINNED_STDLIB_RE)}
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    guard = _install_candidate_import_guard()
    engine = importlib.import_module("candidates.rust_candidate")
    return engine, _authenticate_candidate(engine, guard)


def normalize_pattern(value: Any) -> dict[str, Any]:
    groups = getattr(value, "groups")
    flags = getattr(value, "flags")
    require(type(groups) is int and groups >= 0 and type(flags) is int,
            "a public pattern concealed its exact flags or capture count")
    return {
        "kind": "compiled-pattern",
        "pattern": normalize_value(getattr(value, "pattern")),
        "flags": flags, "groups": groups,
        "groupindex": [
            [name, index]
            for name, index in sorted(dict(getattr(value, "groupindex")).items())
        ],
    }


def normalize_match(value: Any) -> dict[str, Any]:
    pattern = getattr(value, "re")
    groups = getattr(pattern, "groups")
    require(type(groups) is int and groups >= 0,
            "a genuine public match concealed its capture-group count")
    return {
        "kind": "match", "pattern": normalize_pattern(pattern),
        "string": normalize_value(getattr(value, "string")),
        "group": normalize_value(value.group(0)),
        "span": list(value.span(0)),
        "groups": [normalize_value(item) for item in value.groups()],
        "spans": [list(value.span(index)) for index in range(groups + 1)],
        "groupdict": [
            [name, normalize_value(item)]
            for name, item in sorted(value.groupdict().items())
        ],
        "lastindex": value.lastindex, "lastgroup": value.lastgroup,
        "pos": value.pos, "endpos": value.endpos,
    }


def normalize_value(value: Any) -> Any:
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is bytes:
        return {"kind": "bytes", "hex": value.hex()}
    if type(value) is bytearray:
        return {"kind": "bytearray", "hex": bytes(value).hex()}
    if type(value) is memoryview:
        return {
            "kind": "memoryview", "hex": value.tobytes().hex(),
            "readonly": value.readonly, "format": value.format,
            "itemsize": value.itemsize, "ndim": value.ndim,
            "shape": list(value.shape) if value.shape is not None else None,
            "strides": list(value.strides) if value.strides is not None else None,
            "contiguous": value.contiguous,
        }
    if type(value) in (list, tuple):
        return {
            "kind": "list" if type(value) is list else "tuple",
            "items": [normalize_value(item) for item in value],
        }
    if isinstance(value, Mapping):
        return {
            "kind": "mapping", "items": [
                [normalize_value(key), normalize_value(item)]
                for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
            ],
        }
    if hasattr(value, "group") and hasattr(value, "span") and hasattr(value, "re"):
        return normalize_match(value)
    if hasattr(value, "pattern") and hasattr(value, "groupindex"):
        return normalize_pattern(value)
    raise PublicProfileError(
        "an actual public profile outcome has unsupported type: "
        + type(value).__qualname__,
    )


def _normalize_exception(error: Exception, engine: Any) -> dict[str, Any]:
    engine_error = getattr(engine, "error", None)
    if isinstance(engine_error, type) and isinstance(error, engine_error):
        return {
            "kind": "public-regex-pattern-error",
            "args": normalize_value(error.args),
            "message": getattr(error, "msg", None),
            "pattern": normalize_value(getattr(error, "pattern", None)),
            "position": getattr(error, "pos", None),
            "line": getattr(error, "lineno", None),
            "column": getattr(error, "colno", None),
        }
    return {
        "kind": "ordinary-python-exception", "module": type(error).__module__,
        "type": type(error).__qualname__, "args": normalize_value(error.args),
    }


def prepare_case(engine: Any, case: Mapping[str, Any]) -> Callable[[], dict[str, Any]]:
    expression = decode_typed(case["pattern"])
    subject = decode_typed(case["subject"])
    replacement = decode_typed(case["replacement"])
    phrase = decode_typed(case["scanner_phrase"])
    operation = case["operation"]
    limit = case["limit"]
    flags = case["flags"]
    require(operation in OPERATIONS and type(flags) is int
            and type(limit) is int and 1 <= limit <= 3,
            "a frozen public profiling operation or limit was substituted")
    compiled = None
    if operation.startswith("pattern.") or operation.startswith("match."):
        compiled = engine.compile(expression, flags)
    fresh_serial = 0

    def perform_without_warnings() -> dict[str, Any]:
        nonlocal fresh_serial
        callbacks: list[dict[str, Any]] = []

        def replacement_callback(match: Any) -> str | bytes:
            callbacks.append(normalize_match(match))
            token = match.group(0)
            return b"<" + token.upper() + b">" if type(token) is bytes \
                else "<" + token.upper() + ">"

        def scanner_callback(scanner: Any, token: Any) -> str | bytes:
            match = scanner.match
            combined = scanner.scanner
            callbacks.append({
                "kind": "scanner-token", "token": normalize_value(token),
                "match": normalize_match(match),
                "combined_pattern": normalize_pattern(combined),
                "match_uses_combined_pattern": match.re is combined,
            })
            return b"<" + token.upper() + b">" if type(token) is bytes \
                else "<" + token.upper() + ">"

        try:
            if operation == "module.compile":
                result = engine.compile(expression, flags)
            elif operation in (
                "module.search", "module.match", "module.fullmatch",
                "module.findall", "module.finditer",
            ):
                name = operation.split(".", 1)[1]
                result = getattr(engine, name)(expression, subject, flags)
                if name == "finditer":
                    result = list(result)
            elif operation == "module.split":
                result = engine.split(
                    expression, subject, maxsplit=limit, flags=flags,
                )
            elif operation in (
                "module.sub.literal", "module.sub.callback", "module.subn.literal",
            ):
                function = engine.subn if operation == "module.subn.literal" \
                    else engine.sub
                value = replacement_callback if operation.endswith("callback") \
                    else replacement
                result = function(expression, value, subject, count=limit, flags=flags)
            elif operation in (
                "pattern.search", "pattern.match", "pattern.fullmatch",
                "pattern.findall", "pattern.finditer",
            ):
                name = operation.split(".", 1)[1]
                result = getattr(compiled, name)(subject)
                if name == "finditer":
                    result = list(result)
            elif operation == "pattern.split":
                result = compiled.split(subject, maxsplit=limit)
            elif operation in (
                "pattern.sub.literal", "pattern.sub.callback", "pattern.subn.literal",
            ):
                function = compiled.subn if operation == "pattern.subn.literal" \
                    else compiled.sub
                value = replacement_callback if operation.endswith("callback") \
                    else replacement
                result = function(value, subject, count=limit)
            elif operation in ("pattern.scanner.search", "pattern.scanner.match"):
                scanner = compiled.scanner(subject)
                result = getattr(scanner, operation.rsplit(".", 1)[1])()
            elif operation == "pattern.scanner.loop":
                scanner = compiled.scanner(subject)
                result = []
                while (match := scanner.search()) is not None:
                    result.append(match)
                    require(len(result) <= 512,
                            "a genuine public pattern scanner failed to advance")
            elif operation == "scanner.scan":
                whitespace = r"\s+" if type(phrase) is str else rb"\s+"
                scanner = engine.Scanner(
                    [(phrase, scanner_callback), (whitespace, None)], flags=0,
                )
                result = scanner.scan(subject)
            elif operation == "match.group":
                match = compiled.search(subject)
                result = None if match is None else {
                    "match": normalize_match(match),
                    "group_zero": match.group(0),
                    "groups": match.groups(),
                    "groupdict": dict(match.groupdict()),
                }
            elif operation == "match.expand":
                match = compiled.search(subject)
                result = None if match is None else match.expand(replacement)
            elif operation == "compile.fresh.search":
                suffix = "(?#fresh-public-profile-" + str(fresh_serial) + ")"
                fresh_serial += 1
                fresh = expression + suffix if type(expression) is str \
                    else expression + suffix.encode("ascii")
                match = engine.compile(fresh, flags).search(subject)
                result = None if match is None else {
                    "group": match.group(0), "span": tuple(match.span(0)),
                    "groups": tuple(match.groups()),
                    "groupdict": dict(match.groupdict()),
                }
            else:
                raise PublicProfileError("an unfrozen public operation was injected")
            return {
                "status": "return", "value": normalize_value(result),
                "callbacks": callbacks,
            }
        except PublicProfileError:
            raise
        except Exception as error:
            return {
                "status": "raise", "exception": _normalize_exception(error, engine),
                "callbacks": callbacks,
            }

    def perform() -> dict[str, Any]:
        with warnings.catch_warnings(record=True) as records:
            warnings.simplefilter("always")
            result = perform_without_warnings()
            result["warnings"] = [{
                "module": record.category.__module__,
                "category": record.category.__qualname__,
                "message": str(record.message),
            } for record in records]
            return result

    return perform


def _worker_document(
    *, role: str, engine: str, mode: str,
    provenance: Mapping[str, Any], **fields: Any,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-isolated-" + mode, "status": "PASS",
        "label": PUBLIC_LABEL, "role": role, "engine": engine,
        "pid": os.getpid(), "python": "3.14.6",
        "published_seed": PUBLISHED_SEED, "matrix_sha256": MATRIX_SHA256,
        "case_count": 16 * len(OPERATIONS),
        "candidate_import_count": sum(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "engine_provenance": dict(provenance),
        "fixture_files_read": 0, "holdout_files_read": 0,
        "archive_files_read": 0, "files_written": 0,
        **fields,
    }


def observe_worker(role: str, engine_name: str) -> dict[str, Any]:
    matrix = build_public_matrix()
    validate_public_matrix(matrix)
    engine, provenance = load_engine(engine_name)
    records = [{"case": case["case"], "outcome": prepare_case(engine, case)()}
               for case in matrix]
    require(len(records) == len(matrix),
            "an exact fresh public correctness case was omitted")
    return _worker_document(
        role=role, engine=engine_name, mode="observations", provenance=provenance,
        records_sha256=digest(records), records=records,
        clock_samples=0, timing_trials_run=0,
    )


def _validated_request(matrix: list[dict[str, Any]]) -> dict[str, Any]:
    request = decode_document(
        sys.stdin.buffer.read(MAX_PROCESS_BYTES + 1),
        "complete correctness-gated isolated worker request",
    )
    require(request.get("schema") == SCHEMA + "-worker-request"
            and request.get("published_seed") == PUBLISHED_SEED
            and request.get("matrix_sha256") == MATRIX_SHA256
            and type(request.get("expected_records")) is list
            and len(request["expected_records"]) == len(matrix)
            and digest(request["expected_records"])
            == request.get("expected_records_sha256"),
            "the complete pinned public correctness vector was substituted")
    for case, record in zip(matrix, request["expected_records"], strict=True):
        require(type(record) is dict and set(record) == {"case", "outcome"}
                and record.get("case") == case["case"]
                and type(record.get("outcome")) is dict,
                "an original full-vector public correctness record was omitted")
    return request


def timing_worker(role: str, engine_name: str) -> dict[str, Any]:
    from time import perf_counter_ns

    matrix = build_public_matrix()
    validate_public_matrix(matrix)
    request = _validated_request(matrix)
    rounds = request.get("round")
    iterations = request.get("iterations")
    warmups = request.get("warmups")
    order = request.get("case_order")
    matrix_by_case = {case["case"]: case for case in matrix}
    require(type(rounds) is int and 0 <= rounds < 64
            and type(iterations) is int and 1 <= iterations <= 128
            and type(warmups) is int and 0 <= warmups <= 32
            and type(order) is list and len(order) == len(matrix)
            and len(set(order)) == len(matrix) and set(order) == set(matrix_by_case),
            "the exact correctness-gated paired public timing request changed")
    expected = {
        record["case"]: record["outcome"]
        for record in request["expected_records"]
    }
    engine, provenance = load_engine(engine_name)
    rows: list[dict[str, Any]] = []
    for index, case_id in enumerate(order):
        case = matrix_by_case[case_id]
        actual = prepare_case(engine, case)
        reference = expected[case_id]
        for _ in range(warmups):
            require(actual() == reference,
                    "a public pre-timing correctness check failed: " + case_id)
        started = perf_counter_ns()
        for _ in range(iterations):
            require(actual() == reference,
                    "a public timed correctness check failed: " + case_id)
        stopped = perf_counter_ns()
        require(actual() == reference,
                "a public post-timing correctness check failed: " + case_id)
        elapsed = stopped - started
        require(type(elapsed) is int and elapsed > 0,
                "an actual monotonic public timing interval was not measured")
        rows.append({
            "case": case_id, "round": rounds, "position": index,
            "cohort": case["cohort"], "operation": case["operation"],
            "elapsed_ns": elapsed, "iterations": iterations,
            "correctness_checks": warmups + iterations + 1,
            "expected_outcome_sha256": digest(reference),
        })
    return _worker_document(
        role=role, engine=engine_name, mode="timing", provenance=provenance,
        round=rounds, iterations=iterations, warmups=warmups,
        expected_records_sha256=request["expected_records_sha256"],
        rows_sha256=digest(rows), rows=rows, clock_samples=len(rows) * 2,
    )


def profile_worker(role: str, engine_name: str) -> dict[str, Any]:
    import resource
    import tracemalloc
    from time import perf_counter_ns

    matrix = build_public_matrix()
    validate_public_matrix(matrix)
    request = _validated_request(matrix)
    passes = request.get("profile_passes")
    require(type(passes) is int and 1 <= passes <= 32,
            "the exact gated public native profile pass count was substituted")
    expected = {
        record["case"]: record["outcome"]
        for record in request["expected_records"]
    }
    engine, provenance = load_engine(engine_name)
    executions = {cohort: 0 for cohort in sorted({
        case["cohort"] for case in matrix
    })}
    tracemalloc.start(8)
    before_current, before_peak = tracemalloc.get_traced_memory()
    before_blocks = sys.getallocatedblocks()
    before_usage = resource.getrusage(resource.RUSAGE_SELF)
    started = perf_counter_ns()
    for _ in range(passes):
        for case in matrix:
            actual = prepare_case(engine, case)()
            require(actual == expected[case["case"]],
                    "a native-profile correctness check failed: " + case["case"])
            executions[case["cohort"]] += 1
    stopped = perf_counter_ns()
    after_usage = resource.getrusage(resource.RUSAGE_SELF)
    after_blocks = sys.getallocatedblocks()
    after_current, after_peak = tracemalloc.get_traced_memory()
    top_python_allocations = [{
        "file": os.path.basename(item.traceback[0].filename),
        "line": item.traceback[0].lineno,
        "bytes": item.size, "blocks": item.count,
    } for item in tracemalloc.take_snapshot().statistics("lineno")[:12]]
    tracemalloc.stop()
    require(stopped > started and sum(executions.values()) == len(matrix) * passes,
            "a complete correctness-gated native profile case was omitted")
    return _worker_document(
        role=role, engine=engine_name, mode="profile", provenance=provenance,
        expected_records_sha256=request["expected_records_sha256"],
        profile_passes=passes, public_case_executions=len(matrix) * passes,
        executions_by_cohort=executions,
        elapsed_ns=stopped - started,
        python_heap={
            "tracemalloc_before_bytes": before_current,
            "tracemalloc_before_peak_bytes": before_peak,
            "tracemalloc_after_bytes": after_current,
            "tracemalloc_peak_bytes": after_peak,
            "allocated_blocks_delta": after_blocks - before_blocks,
            "maximum_rss_kib": after_usage.ru_maxrss,
            "user_cpu_seconds": after_usage.ru_utime - before_usage.ru_utime,
            "system_cpu_seconds": after_usage.ru_stime - before_usage.ru_stime,
            "top_python_allocation_sites": top_python_allocations,
        },
    )


def _process_environment() -> dict[str, str]:
    return {
        "PATH": "/usr/bin:/bin", "LC_ALL": "C",
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
        "PYTHONMALLOC": "malloc",
    }


def _run_process(
    command: list[str], *, payload: bytes | None,
    cwd: str, descriptor: int | None = None, timed: bool,
) -> tuple[int, bytes, bytes, int]:
    import subprocess

    require(payload is None or len(payload) <= MAX_PROCESS_BYTES,
            "the bounded correctness-gated worker protocol was exceeded")
    process = subprocess.Popen(
        command, stdin=subprocess.PIPE if payload is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=cwd, shell=False, close_fds=True,
        pass_fds=() if descriptor is None else (descriptor,),
        env=_process_environment(),
    )
    try:
        if timed:
            stdout, stderr = process.communicate(
                input=payload, timeout=PROCESS_TIMEOUT_SECONDS,
            )
        else:
            # Even subprocess timeouts sample a clock; correctness is untimed.
            stdout, stderr = process.communicate(input=payload)
    except subprocess.TimeoutExpired as error:
        process.kill()
        process.communicate()
        raise PublicProfileError("a public profiling subprocess timed out") from error
    require(len(stdout) <= MAX_ARTIFACT_BYTES and len(stderr) <= MAX_ARTIFACT_BYTES,
            "a bounded public profiling process output was exceeded")
    return process.returncode, stdout, stderr, process.pid


def _validate_worker(
    document: Mapping[str, Any], *, role: str, engine: str,
    mode: str, pid: int,
) -> None:
    require(document.get("schema") == SCHEMA + "-isolated-" + mode
            and document.get("status") == "PASS"
            and document.get("label") == PUBLIC_LABEL
            and document.get("role") == role
            and document.get("engine") == engine
            and document.get("pid") == pid
            and document.get("python") == "3.14.6"
            and document.get("published_seed") == PUBLISHED_SEED
            and document.get("matrix_sha256") == MATRIX_SHA256
            and document.get("case_count") == 16 * len(OPERATIONS)
            and document.get("fixture_files_read") == 0
            and document.get("holdout_files_read") == 0
            and document.get("archive_files_read") == 0
            and document.get("files_written") == 0,
            "the complete isolated public worker or provenance was substituted")
    imports = document.get("candidate_import_count")
    require((engine == "stdlib" and imports == 0)
            or (engine == "rust" and type(imports) is int and imports > 0),
            "the two public engines were not isolated into distinct processes")
    if engine == "rust":
        provenance = document.get("engine_provenance")
        require(type(provenance) is dict
                and provenance.get("candidate_owned_forbidden_import_attempts") == []
                and provenance.get("adapter_origin")
                == str(ROOT / "candidates/rust_candidate.py"),
                "the candidate-owned production reference-import guard failed")


def _isolated_worker(
    role: str, engine: str, mode: str, *, request: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], bytes]:
    command = [
        str(PINNED_PYTHON), "-I", "-B", str(ROOT / SOURCE_RELATIVE),
        "--internal-worker", "--engine", engine,
        "--worker-mode", mode, "--role", role,
    ]
    payload = None if request is None else canonical(request)
    code, stdout, stderr, pid = _run_process(
        command, payload=payload, cwd=str(ROOT), timed=mode != "observe",
    )
    require(code == 0 and stderr == b"",
            "an isolated " + engine + " " + mode + " worker failed: "
            + stderr[-2_000:].decode("utf-8", "replace"))
    actual_mode = "observations" if mode == "observe" else mode
    document = decode_document(stdout, "isolated " + engine + " " + mode)
    _validate_worker(document, role=role, engine=engine, mode=actual_mode, pid=pid)
    if mode == "observe":
        require(type(document.get("records")) is list
                and len(document["records"]) == 16 * len(OPERATIONS)
                and digest(document["records"]) == document.get("records_sha256")
                and document.get("clock_samples") == 0,
                "an untimed complete public correctness vector was forged")
    elif mode == "timing":
        require(request is not None
                and document.get("expected_records_sha256")
                == request["expected_records_sha256"]
                and document.get("round") == request["round"]
                and type(document.get("rows")) is list
                and len(document["rows"]) == 16 * len(OPERATIONS)
                and digest(document["rows"]) == document.get("rows_sha256"),
                "an exact full-vector paired public timing was substituted")
    return document, stdout


class ApprovedRunWorkspace:
    """One exclusive, no-follow, descriptor-anchored approved public run."""

    def __init__(self, summary: str):
        self.parts = _approved_session_parts(summary)
        self.descriptors: list[int] = []
        self.directory: int | None = None

    def __enter__(self) -> "ApprovedRunWorkspace":
        current = os.open(str(ROOT), _directory_open_flags())
        self.descriptors.append(current)
        for index, name in enumerate(self.parts[:-1]):
            if index == len(self.parts) - 2:
                # Sessions are never reused, overwritten, cleaned, or archived.
                os.mkdir(name, mode=0o700, dir_fd=current)
            else:
                try:
                    os.mkdir(name, mode=0o755, dir_fd=current)
                except FileExistsError:
                    pass
            following = os.open(name, _directory_open_flags(), dir_fd=current)
            self.descriptors.append(following)
            require(stat.S_ISDIR(os.fstat(following).st_mode),
                    "an approved profile component is not a no-follow directory")
            current = following
        self.directory = current
        return self

    def __exit__(self, error_type: Any, error: Any, traceback: Any) -> None:
        for descriptor in reversed(self.descriptors):
            os.close(descriptor)
        self.descriptors.clear()
        self.directory = None

    @property
    def proc_path(self) -> str:
        require(type(self.directory) is int,
                "an actual no-follow approved run directory is mandatory")
        return "/proc/self/fd/" + str(self.directory)

    @property
    def relative_directory(self) -> str:
        return "/".join(self.parts[:-1])

    def write(self, name: str, payload: bytes) -> dict[str, Any]:
        leaf = _approved_artifact_name(name)
        require(type(payload) is bytes and len(payload) <= MAX_ARTIFACT_BYTES
                and type(self.directory) is int,
                "a bounded approved profile artifact payload is mandatory")
        descriptor = os.open(
            leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL
            | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
            0o600, dir_fd=self.directory,
        )
        try:
            require(stat.S_ISREG(os.fstat(descriptor).st_mode),
                    "the exclusively created public artifact is not a real file")
            position = 0
            while position < len(payload):
                count = os.write(descriptor, payload[position:])
                require(type(count) is int and count > 0,
                        "a complete approved public artifact write was interrupted")
                position += count
            os.fsync(descriptor)
            os.fsync(self.directory)
        finally:
            os.close(descriptor)
        return {
            "path": self.relative_directory + "/" + leaf,
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }


def _verify_profiler_binaries() -> dict[str, dict[str, str]]:
    require(os.path.islink(GPROFNG)
            and os.path.realpath(GPROFNG) == str(GPROFNG_EXECUTABLE),
            "the exact frozen /usr/bin/gprofng dispatcher was substituted")
    binaries = _expected_profiler_manifest()
    for label, expected in binaries.items():
        path = expected["path"]
        require(os.path.realpath(path) == path,
                "a frozen public profiler binary became a symlink: " + label)
        descriptor = os.open(
            path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_CLOEXEC", 0),
        )
        try:
            details = os.fstat(descriptor)
            require(stat.S_ISREG(details.st_mode)
                    and bool(details.st_mode & stat.S_IXUSR),
                    "a frozen profiler component is not an executable file")
            hasher = hashlib.sha256()
            while (chunk := os.read(descriptor, 128 * 1024)):
                hasher.update(chunk)
            require(hasher.hexdigest() == expected["sha256"],
                    "the frozen profiler component hash changed: " + label)
        finally:
            os.close(descriptor)
    return binaries


def _profile_report_markers(payloads: Mapping[str, bytes]) -> dict[str, Any]:
    joined = b"\n".join(payloads.values()).decode("utf-8", "replace")
    ffi_lines = [
        line.strip()[:300] for line in joined.splitlines()
        if any(marker in line for marker in NATIVE_FFI_MARKERS)
    ][:80]
    metric_lines = [
        line.strip()[:300] for line in joined.splitlines()
        if any(marker in line.lower() for marker in (
            "cpu", "allocated", "allocation", "heap", "leaked", "bytes",
        ))
    ][:80]
    return {
        "native_ffi_marker_count": len(ffi_lines),
        "native_ffi_marker_lines": ffi_lines,
        "cpu_heap_allocation_metric_lines": metric_lines,
    }


def _profile_engine(
    workspace: ApprovedRunWorkspace, engine: str, request: dict[str, Any],
) -> dict[str, Any]:
    role = "public-profile-" + engine
    command = _collector_command(engine)
    code, stdout, stderr, pid = _run_process(
        command, payload=canonical(request), cwd=workspace.proc_path,
        descriptor=workspace.directory, timed=True,
    )
    artifacts = [
        workspace.write(engine + ".collector.stdout.json", stdout),
        workspace.write(engine + ".collector.stderr.txt", stderr),
    ]
    require(code == 0,
            "gprofng CPU/heap collection failed for " + engine + ": "
            + stderr[-2_000:].decode("utf-8", "replace"))
    document = decode_document(stdout, engine + " complete profiled worker stdout")
    # gprofng executes the direct Python target rather than an untracked shell.
    _validate_worker(
        document, role=role, engine=engine, mode="profile", pid=document.get("pid"),
    )
    require(type(document.get("pid")) is int
            and document.get("expected_records_sha256")
            == request["expected_records_sha256"]
            and document.get("profile_passes") == request["profile_passes"]
            and document.get("public_case_executions")
            == 16 * len(OPERATIONS) * request["profile_passes"]
            and type(document.get("python_heap")) is dict,
            "the complete correctness-gated native profile worker was forged")
    require(type(workspace.directory) is int,
            "the approved profiler directory descriptor was lost")
    experiment = os.open(
        engine + ".er", _directory_open_flags(), dir_fd=workspace.directory,
    )
    try:
        require(stat.S_ISDIR(os.fstat(experiment).st_mode),
                "the approved native profiler experiment is not a real directory")
    finally:
        os.close(experiment)
    reports: dict[str, bytes] = {}
    for kind, option in PROFILE_REPORTS.items():
        report_command = [
            str(GPROFNG), "display", "text", option, engine + ".er",
        ]
        report_code, report, diagnostics, _ = _run_process(
            report_command, payload=None, cwd=workspace.proc_path,
            descriptor=workspace.directory, timed=True,
        )
        artifacts.append(workspace.write(engine + "." + kind + ".txt", report))
        artifacts.append(workspace.write(
            engine + "." + kind + ".stderr.txt", diagnostics,
        ))
        require(report_code == 0 and bool(report.strip()),
                "gprofng " + kind + " evidence failed for " + engine + ": "
                + diagnostics[-2_000:].decode("utf-8", "replace"))
        reports[kind] = report
    ffi = _profile_report_markers(reports)
    return {
        "engine": engine,
        "collector_pid": pid,
        "target_pid": document["pid"],
        "experiment": workspace.relative_directory + "/" + engine + ".er",
        "archive_collection": "DISABLED (-a off)",
        "descendant_collection": "DISABLED (-F off)",
        "native_heap_tracing": "ENABLED (-H on)",
        "cpu_sampling": "ENABLED (-p hi)",
        "correctness_checks": document["public_case_executions"],
        "cohort_execution_counts": document["executions_by_cohort"],
        "python_heap": document["python_heap"],
        "native_ffi": ffi,
        "engine_provenance": document["engine_provenance"],
        "artifacts": artifacts,
    }


def _summarize_paired_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_cohort: dict[str, list[tuple[int, int]]] = {}
    by_operation: dict[str, list[tuple[int, int]]] = {}
    for row in rows:
        pair = (row["baseline_elapsed_ns"], row["rust_elapsed_ns"])
        by_cohort.setdefault(row["cohort"], []).append(pair)
        by_operation.setdefault(row["operation"], []).append(pair)

    def summarize(values: list[tuple[int, int]]) -> dict[str, Any]:
        baseline = sum(item[0] for item in values)
        candidate = sum(item[1] for item in values)
        require(baseline > 0 and candidate > 0,
                "a complete paired public timing denominator disappeared")
        return {
            "pairs": len(values), "baseline_total_ns": baseline,
            "rust_total_ns": candidate,
            "baseline_over_rust_ratio": baseline / candidate,
        }

    return {
        "overall": summarize([
            (row["baseline_elapsed_ns"], row["rust_elapsed_ns"]) for row in rows
        ]),
        "by_cohort": {
            cohort: summarize(values) for cohort, values in sorted(by_cohort.items())
        },
        "by_operation": {
            operation: summarize(values)
            for operation, values in sorted(by_operation.items())
        },
    }


def run_public_profile(
    *, output: str, paired_rounds: int, iterations: int,
    warmups: int, profile_passes: int,
) -> dict[str, Any]:
    verification = verify_frozen_source()
    _approved_session_parts(output)
    require(type(paired_rounds) is int and 2 <= paired_rounds <= 32
            and paired_rounds % 2 == 0
            and type(iterations) is int and 1 <= iterations <= 128
            and type(warmups) is int and 0 <= warmups <= 32
            and type(profile_passes) is int and 1 <= profile_passes <= 32,
            "the exact balanced paired public profiling configuration is invalid")
    profiler = _verify_profiler_binaries()
    matrix = build_public_matrix()
    validate_public_matrix(matrix)
    baseline, baseline_raw = _isolated_worker(
        "public-profile-correctness-stdlib", "stdlib", "observe",
    )
    candidate, candidate_raw = _isolated_worker(
        "public-profile-correctness-rust", "rust", "observe",
    )
    require(baseline["pid"] != candidate["pid"],
            "the original CPython and Rust correctness processes were not isolated")
    if baseline["records"] != candidate["records"] \
            or baseline["records_sha256"] != candidate["records_sha256"]:
        first = next((
            {"case": original["case"], "baseline": original["outcome"],
             "rust": actual["outcome"]}
            for original, actual in zip(
                baseline["records"], candidate["records"], strict=True,
            )
            if original != actual
        ), None)
        raise PublicProfileError(
            "full fresh-public correctness gate failed before timing, profiler, "
            "or workspace writes: " + json.dumps(first, ensure_ascii=True),
        )

    with ApprovedRunWorkspace(output) as workspace:
        artifacts = [
            workspace.write("stdlib.correctness.raw.json", baseline_raw),
            workspace.write("rust.correctness.raw.json", candidate_raw),
        ]
        rows: list[dict[str, Any]] = []
        ids = [case["case"] for case in matrix]
        matrix_by_id = {case["case"]: case for case in matrix}
        for round_number in range(paired_rounds):
            offset = (PUBLISHED_SEED + round_number * 37) % len(ids)
            order = ids[offset:] + ids[:offset]
            if round_number % 2:
                order.reverse()
            request = {
                "schema": SCHEMA + "-worker-request",
                "published_seed": PUBLISHED_SEED,
                "matrix_sha256": MATRIX_SHA256,
                "expected_records_sha256": baseline["records_sha256"],
                "expected_records": baseline["records"],
                "round": round_number, "iterations": iterations,
                "warmups": warmups, "case_order": order,
            }
            engines = ("stdlib", "rust") if round_number % 2 == 0 \
                else ("rust", "stdlib")
            documents: dict[str, dict[str, Any]] = {}
            for engine in engines:
                role = "public-timing-" + format(round_number, "02d") + "-" + engine
                document, raw = _isolated_worker(
                    role, engine, "timing", request=request,
                )
                documents[engine] = document
                artifacts.append(workspace.write(
                    engine + ".timing-round-" + format(round_number, "02d")
                    + ".raw.json", raw,
                ))
            require(documents["stdlib"]["pid"] != documents["rust"]["pid"],
                    "a genuine paired round reused the original reference process")
            for original, actual in zip(
                documents["stdlib"]["rows"], documents["rust"]["rows"], strict=True,
            ):
                case_id = original["case"]
                require(actual["case"] == case_id
                        and actual["round"] == original["round"] == round_number
                        and actual["position"] == original["position"]
                        and actual["iterations"] == original["iterations"] == iterations
                        and actual["expected_outcome_sha256"]
                        == original["expected_outcome_sha256"],
                        "a correctness-gated paired public case was substituted")
                case = matrix_by_id[case_id]
                rows.append({
                    "case": case_id, "round": round_number,
                    "position": original["position"],
                    "cohort": case["cohort"], "operation": case["operation"],
                    "pair_order": list(engines),
                    "baseline_pid": documents["stdlib"]["pid"],
                    "rust_pid": documents["rust"]["pid"],
                    "iterations": iterations,
                    "correctness_checks_per_engine": original["correctness_checks"],
                    "baseline_elapsed_ns": original["elapsed_ns"],
                    "rust_elapsed_ns": actual["elapsed_ns"],
                })
        require(len(rows) == len(matrix) * paired_rounds,
                "an original equal-weight paired public timing case was omitted")
        artifacts.append(workspace.write(
            "paired-timing.raw.json", canonical({
                "schema": SCHEMA + "-paired-timing-rows",
                "matrix_sha256": MATRIX_SHA256,
                "rows_sha256": digest(rows), "rows": rows,
            }),
        ))
        profile_request = {
            "schema": SCHEMA + "-worker-request",
            "published_seed": PUBLISHED_SEED,
            "matrix_sha256": MATRIX_SHA256,
            "expected_records_sha256": baseline["records_sha256"],
            "expected_records": baseline["records"],
            "profile_passes": profile_passes,
        }
        profiles = {
            engine: _profile_engine(workspace, engine, profile_request)
            for engine in ("stdlib", "rust")
        }
        require(profiles["rust"]["native_ffi"]["native_ffi_marker_count"] > 0,
                "the candidate native CPU/heap reports contain no owned FFI evidence")
        summary = {
            "schema": SCHEMA + "-published-public-profile", "status": "PASS",
            "label": PUBLIC_LABEL, "python": "3.14.6",
            "source_sha256": verification["source_sha256"],
            "manifest_sha256": verification["manifest_sha256"],
            "published_seed": PUBLISHED_SEED, "matrix_sha256": MATRIX_SHA256,
            "dataset_count": 16, "case_count": len(matrix),
            "operation_count": len(OPERATIONS),
            "correctness_gate": {
                "status": "PASS", "baseline_pid": baseline["pid"],
                "rust_pid": candidate["pid"],
                "compared_cases": len(matrix),
                "records_sha256": baseline["records_sha256"],
                "completed_before_any_timing_or_profiler": True,
                "candidate_owned_reference_import_attempts": [],
            },
            "paired_rounds": paired_rounds,
            "batch_iterations": iterations,
            "warmup_iterations": warmups,
            "profile_passes": profile_passes,
            "raw_paired_rows_sha256": digest(rows),
            "paired_results": _summarize_paired_rows(rows),
            "profiler_binaries": profiler,
            "native_profiles": profiles,
            "artifacts": artifacts,
            "approved_output_directory": workspace.relative_directory,
            "fixture_files_read": 0, "holdout_files_read": 0,
            "archive_files_read": 0,
            "profiler_binary_archiving": "DISABLED",
            "final_winner_selected": False,
        }
        summary_artifact = workspace.write("summary.json", canonical(summary))
        return {
            "schema": SCHEMA + "-publication-receipt", "status": "PASS",
            "label": PUBLIC_LABEL,
            "matrix_sha256": MATRIX_SHA256,
            "source_sha256": verification["source_sha256"],
            "case_count": len(matrix),
            "correctness_gate": "PASS BEFORE ANY TIMING OR PROFILING",
            "paired_rounds": paired_rounds,
            "profiled_engines": ["stdlib", "rust"],
            "native_rust_ffi_marker_count": profiles["rust"]["native_ffi"][
                "native_ffi_marker_count"
            ],
            "summary": summary_artifact,
            "fixture_files_read": 0, "holdout_files_read": 0,
            "archive_files_read": 0,
            "final_winner_selected": False,
        }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Frozen fresh-public-only correctness-gated paired Rust/CPython "
            "CPU, heap, allocation, and native FFI profiling"
        ),
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--verify-source", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--internal-worker", action="store_true",
                       help=argparse.SUPPRESS)
    parser.add_argument("--output")
    parser.add_argument("--rounds", type=int, default=DEFAULT_PAIRED_ROUNDS)
    parser.add_argument("--iterations", type=int, default=DEFAULT_BATCH_ITERATIONS)
    parser.add_argument("--warmups", type=int, default=DEFAULT_WARMUP_ITERATIONS)
    parser.add_argument("--profile-passes", type=int, default=DEFAULT_PROFILE_PASSES)
    parser.add_argument("--engine", choices=("stdlib", "rust"),
                        help=argparse.SUPPRESS)
    parser.add_argument("--worker-mode", choices=("observe", "timing", "profile"),
                        help=argparse.SUPPRESS)
    parser.add_argument("--role", help=argparse.SUPPRESS)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.verify_source or options.self_test:
        require(options.output is None and options.engine is None
                and options.worker_mode is None and options.role is None
                and options.rounds == DEFAULT_PAIRED_ROUNDS
                and options.iterations == DEFAULT_BATCH_ITERATIONS
                and options.warmups == DEFAULT_WARMUP_ITERATIONS
                and options.profile_passes == DEFAULT_PROFILE_PASSES,
                "strict source-only modes cannot import candidates, time, or write")
        document = verify_frozen_source() if options.verify_source else source_self_test()
    elif options.run:
        require(options.output is not None and options.engine is None
                and options.worker_mode is None and options.role is None,
                "an actual public profile needs one explicit approved summary path")
        document = run_public_profile(
            output=options.output, paired_rounds=options.rounds,
            iterations=options.iterations, warmups=options.warmups,
            profile_passes=options.profile_passes,
        )
    else:
        require(options.output is None and options.engine in ("stdlib", "rust")
                and options.worker_mode in ("observe", "timing", "profile")
                and type(options.role) is str and bool(options.role)
                and options.rounds == DEFAULT_PAIRED_ROUNDS
                and options.iterations == DEFAULT_BATCH_ITERATIONS
                and options.warmups == DEFAULT_WARMUP_ITERATIONS
                and options.profile_passes == DEFAULT_PROFILE_PASSES,
                "an internal worker must have an exact frozen isolated public role")
        if options.worker_mode == "observe":
            document = observe_worker(options.role, options.engine)
        elif options.worker_mode == "timing":
            document = timing_worker(options.role, options.engine)
        else:
            document = profile_worker(options.role, options.engine)
    sys.stdout.buffer.write(canonical(document))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (PublicProfileError, OSError) as error:
        print("fresh public profile failed closed: " + str(error), file=sys.stderr)
        raise SystemExit(1) from error
