#!/usr/bin/env python3
"""Produce a scalar-safe, additive diagnosis of the frozen V4 interruption.

The candidate-free self-test is entirely in memory.  Only explicit --diagnose
imports and authenticates the frozen V1 controller, verifies its preserved
evidence, and inherits its complete public-prefix and prepare-only guards.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any


SCHEMA = "rebar-postfinal-public-practice-v4-interrupted-diagnostic-v2"
V1_SCHEMA = "rebar-postfinal-public-practice-v4-interrupted-diagnostic-v1"
ROOT = Path(__file__).resolve().parent.parent
RUNNER = Path(__file__).resolve()
V1_SOURCE = ROOT / "tools" / "postfinal_public_practice_v4_failure_diagnostic.py"
VERSION_ROOT = ROOT / "performance" / "postfinal-public-v4"
EVIDENCE_ROOT = VERSION_ROOT / "evidence"
V1_REPORT = EVIDENCE_ROOT / "postfinal-public-practice-v4-interrupted-diagnostic.json"
OUTPUT_PATH = (
    EVIDENCE_ROOT / "postfinal-public-practice-v4-interrupted-diagnostic-v2.json"
)
V1_SOURCE_SHA256 = (
    "7a031fb7655cd287096c5b1401c4670bce89c42b22e0cc008fb3968578e4ca9c"
)
V1_REPORT_SHA256 = (
    "de46581ef793c3128d9bcd56348ca81a40ca2657c6f443dd61d4c6a2a9732bad"
)
MANIFEST_SHA256 = (
    "15789a8ab6ab35ea97b657fed2ae4be0e944da6300067bc7cb3e8222c7c5ea55"
)
COMPRESSED_RAW_SHA256 = (
    "4132e485b605f924fbc4edf09324987f09361f0562a9884fd0ceb06e09544f8a"
)
MODULES = (
    "re",
    "candidates.rust_candidate",
    "candidates.vm_candidate",
    "candidates.zig_candidate",
)
COMPLETE_CASES = 5_975
TRIALS = 13
COMPLETE_ROWS = 310_700
NEXT_CASE_INDEX = 5_975
NEXT_CASE_ID = "cal.broader.astral-emoji-run.00"
ENCODING_ERROR_POSITION = 224
HASH_CHUNK_BYTES = 1024 * 1024
MAX_SOURCE_BYTES = 16 * 1024 * 1024


class DiagnosticError(RuntimeError):
    """A frozen predecessor or scalar-safe additive diagnosis changed."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise DiagnosticError(message)


def candidate_free() -> None:
    loaded = sorted(
        name
        for name in sys.modules
        if any(
            name == candidate or name.startswith(candidate + ".")
            for candidate in MODULES[1:]
        )
    )
    require(not loaded, f"a production candidate reached the V2 controller: {loaded!r}")


def scalarize(value: Any) -> Any:
    if isinstance(value, str):
        return "".join(
            f"\\u{ord(character):04X}"
            if 0xD800 <= ord(character) <= 0xDFFF
            else character
            for character in value
        )
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, (list, tuple)):
        return [scalarize(item) for item in value]
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            require(isinstance(key, str), "scalar-safe report contains a non-string key")
            safe_key = scalarize(key)
            require(
                safe_key not in result,
                "scalar escaping would merge two distinct diagnostic report keys",
            )
            result[safe_key] = scalarize(item)
        return result
    raise DiagnosticError(
        f"scalar-safe interruption report contains unsupported {type(value).__name__}"
    )


def surrogate_paths(value: Any, prefix: str = "$") -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    if isinstance(value, str):
        for index, character in enumerate(value):
            if 0xD800 <= ord(character) <= 0xDFFF:
                result.append({
                    "path": prefix,
                    "character_index": index,
                    "codepoint": f"U+{ord(character):04X}",
                })
    elif isinstance(value, dict):
        for key, item in value.items():
            result.extend(surrogate_paths(key, f"{prefix}.<key>"))
            result.extend(surrogate_paths(item, f"{prefix}.{key}"))
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            result.extend(surrogate_paths(item, f"{prefix}[{index}]"))
    return result


def canonical(value: Any) -> str:
    safe = scalarize(value)
    require(not surrogate_paths(safe), "canonical V2 report retained a non-scalar")
    encoded = json.dumps(
        safe,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    decoded = json.loads(encoded)
    require(
        not surrogate_paths(decoded),
        "canonical V2 JSON decodes to an unpaired Unicode surrogate",
    )
    encoded.encode("utf-8", errors="strict")
    return encoded


def sha256_path(path: Path, *, maximum: int | None = None) -> str:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while True:
            block = stream.read(HASH_CHUNK_BYTES)
            if not block:
                break
            size += len(block)
            require(
                maximum is None or size <= maximum,
                f"frozen predecessor source exceeded its bound: {path.name}",
            )
            digest.update(block)
    return digest.hexdigest()


def validate_output(value: Path) -> Path:
    resolved = value.resolve()
    require(
        resolved == OUTPUT_PATH.resolve()
        and resolved.parent == EVIDENCE_ROOT.resolve(),
        "V2 must exclusively create its exact additive interruption report",
    )
    return resolved


def load_frozen_v1() -> Any:
    candidate_free()
    require(
        sha256_path(V1_SOURCE, maximum=MAX_SOURCE_BYTES) == V1_SOURCE_SHA256,
        "the exact frozen V1 interruption diagnostic source changed",
    )
    spec = importlib.util.spec_from_file_location(
        "_rebar_frozen_postfinal_public_practice_v4_failure_diagnostic_v1",
        V1_SOURCE,
    )
    require(spec is not None and spec.loader is not None, "cannot load frozen V1")
    frozen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(frozen)
    candidate_free()
    require(
        Path(frozen.__file__).resolve() == V1_SOURCE.resolve()
        and frozen.SCHEMA == V1_SCHEMA
        and frozen.RUNNER.resolve() == V1_SOURCE.resolve()
        and frozen.OUTPUT_PATH.resolve() == V1_REPORT.resolve()
        and frozen.MANIFEST_SHA256 == MANIFEST_SHA256
        and frozen.COMPRESSED_RAW_SHA256 == COMPRESSED_RAW_SHA256
        and tuple(frozen.MODULES) == MODULES
        and frozen.COMPLETE_CASES == COMPLETE_CASES
        and frozen.COMPLETE_ROWS == COMPLETE_ROWS
        and frozen.TRIALS == TRIALS
        and frozen.NEXT_CASE_INDEX == NEXT_CASE_INDEX
        and frozen.NEXT_CASE_ID == NEXT_CASE_ID
        and frozen.ENCODING_ERROR_POSITION == ENCODING_ERROR_POSITION,
        "the frozen V1 predecessor no longer has its exact public-only protocol",
    )
    return frozen


def diagnose(output: Path) -> int:
    candidate_free()
    destination = validate_output(output)
    require(not destination.exists(), "refusing to overwrite the additive V2 report")
    frozen = load_frozen_v1()
    require(
        sha256_path(V1_REPORT) == V1_REPORT_SHA256,
        "the immutable successful V1 interruption evidence changed",
    )
    original_write = frozen.write_exclusive

    def write_scalar_safe(path: Path, report: dict[str, Any]) -> str:
        require(
            validate_output(path) == destination,
            "frozen V1 attempted to substitute the exclusive V2 evidence path",
        )
        require(
            sha256_path(V1_SOURCE, maximum=MAX_SOURCE_BYTES) == V1_SOURCE_SHA256
            and sha256_path(V1_REPORT) == V1_REPORT_SHA256,
            "the immutable frozen V1 predecessor changed during diagnosis",
        )
        require(
            report.get("schema") == SCHEMA
            and report.get("completed_public_cases") == COMPLETE_CASES
            and report.get("completed_public_rows") == COMPLETE_ROWS
            and report.get("manifest_sha256") == MANIFEST_SHA256
            and report.get("compressed_raw_sha256") == COMPRESSED_RAW_SHA256
            and report.get("prepare_requests") == len(MODULES)
            and report.get("observe_requests") == 0
            and report.get("timing_performed") is False
            and report.get("benchmark_performed") is False
            and report.get("holdout_accessed") is False,
            "the inherited V1 public prefix or prepare-only safety guards changed",
        )
        enriched = dict(report)
        enriched["predecessor"] = {
            "schema": V1_SCHEMA,
            "source_path": V1_SOURCE.relative_to(ROOT).as_posix(),
            "source_sha256": V1_SOURCE_SHA256,
            "report_path": V1_REPORT.relative_to(ROOT).as_posix(),
            "report_sha256": V1_REPORT_SHA256,
            "source_and_report_unchanged": True,
        }
        enriched["unicode_scalar_safety"] = {
            "json_decodes_to_unicode_scalars": True,
            "lone_surrogate_rendering": "literal printable \\\\uXXXX text",
            "original_error_codepoint": "U+D800",
            "original_error_character_position": ENCODING_ERROR_POSITION,
            "original_exception_type_and_cause_preserved": True,
            "worker_request_rewritten": False,
        }
        safe_report = scalarize(enriched)
        require(
            not surrogate_paths(safe_report),
            "the exclusive V2 report retained an unpaired Unicode surrogate",
        )
        candidate_free()
        return original_write(path, safe_report)

    frozen.SCHEMA = SCHEMA
    frozen.RUNNER = RUNNER
    frozen.OUTPUT_PATH = OUTPUT_PATH
    frozen.canonical = canonical
    frozen.write_exclusive = write_scalar_safe
    result = frozen.diagnose(destination)
    candidate_free()
    return result


def synthetic_self_test() -> dict[str, Any]:
    candidate_free()
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: Any) -> None:
        require(condition, f"candidate-free V2 interruption self-test failed: {name}")
        checks.append({"name": name, "passed": True})

    check("exact-four-independent-worker-families", len(MODULES) == 4)
    check(
        "exact-complete-public-row-denominator",
        COMPLETE_ROWS == COMPLETE_CASES * len(MODULES) * TRIALS,
    )
    check("exact-frozen-next-selected-index", NEXT_CASE_INDEX == COMPLETE_CASES)
    check("exact-frozen-first-interrupted-case", NEXT_CASE_ID == "cal.broader.astral-emoji-run.00")
    check(
        "hard-pinned-frozen-v1-source-fingerprint",
        len(V1_SOURCE_SHA256) == 64 and V1_SOURCE_SHA256.startswith("7a031fb7"),
    )
    check(
        "hard-pinned-preserved-v1-report-fingerprint",
        len(V1_REPORT_SHA256) == 64 and V1_REPORT_SHA256.startswith("de46581e"),
    )
    check(
        "hard-pinned-original-manifest-fingerprint",
        len(MANIFEST_SHA256) == 64 and MANIFEST_SHA256.startswith("15789a8a"),
    )
    check(
        "hard-pinned-original-compressed-stream-fingerprint",
        len(COMPRESSED_RAW_SHA256) == 64
        and COMPRESSED_RAW_SHA256.startswith("4132e485"),
    )
    check("exact-additive-exclusive-v2-output", validate_output(OUTPUT_PATH) == OUTPUT_PATH.resolve())
    for label, poisoned_path in (
        ("reject-immutable-v1-evidence-as-output", V1_REPORT),
        (
            "reject-substituted-v2-evidence-output",
            OUTPUT_PATH.with_name("poisoned-v4-interruption-diagnostic-v2.json"),
        ),
    ):
        try:
            validate_output(poisoned_path)
        except DiagnosticError:
            rejected = True
        else:
            rejected = False
        check(label, rejected)

    try:
        (("x" * ENCODING_ERROR_POSITION) + "\ud800").encode(
            "utf-8", errors="strict"
        )
    except UnicodeEncodeError as cause:
        original_error = {
            "class": type(cause).__name__,
            "message": str(cause),
            "args": list(cause.args),
            "encoding": cause.encoding,
            "reason": cause.reason,
            "start": cause.start,
            "end": cause.end,
            "codepoints": [
                f"U+{ord(character):04X}"
                for character in cause.object[cause.start:cause.end]
            ],
        }
    else:
        raise DiagnosticError("synthetic frozen controller surrogate encoded")

    check(
        "capture-original-strict-utf8-surrogate-error",
        original_error["class"] == "UnicodeEncodeError"
        and original_error["encoding"] == "utf-8"
        and original_error["reason"] == "surrogates not allowed"
        and original_error["start"] == ENCODING_ERROR_POSITION
        and original_error["codepoints"] == ["U+D800"],
    )
    check(
        "detect-unsanitized-surrogate-in-original-exception-args",
        any(item["codepoint"] == "U+D800" for item in surrogate_paths(original_error)),
    )
    wrapped = {
        "class": "RuntimeError",
        "message": "the independently guarded synthetic worker rejected a request",
        "args": ["the independently guarded synthetic worker rejected a request"],
        "cause": original_error,
        "context": None,
    }
    sanitized = scalarize(wrapped)
    check("recursively-sanitize-complete-nested-exception-cause", not surrogate_paths(sanitized))
    check(
        "preserve-original-unicode-error-type-and-position",
        sanitized["cause"]["class"] == "UnicodeEncodeError"
        and sanitized["cause"]["start"] == ENCODING_ERROR_POSITION
        and sanitized["cause"]["end"] == ENCODING_ERROR_POSITION + 1
        and sanitized["cause"]["codepoints"] == ["U+D800"],
    )
    check(
        "render-lone-surrogate-as-printable-escaped-text",
        sanitized["cause"]["args"][1]
        == ("x" * ENCODING_ERROR_POSITION) + "\\uD800",
    )
    wire = canonical({"error": wrapped, "low": "\udfff", "astral": "😀"})
    parsed = json.loads(wire)
    check("canonical-json-decodes-with-only-unicode-scalars", not surrogate_paths(parsed))
    check(
        "canonical-json-preserves-literal-high-surrogate-notation",
        parsed["error"]["cause"]["args"][1].endswith("\\uD800"),
    )
    check(
        "canonical-json-preserves-literal-low-surrogate-notation",
        parsed["low"] == "\\uDFFF",
    )
    check("canonical-json-preserves-valid-astral-unicode", parsed["astral"] == "😀")
    check("canonical-json-is-strict-utf8-encodable", bool(wire.encode("utf-8", errors="strict")))
    check(
        "canonical-json-double-escapes-printable-surrogate-marker",
        "\\\\uD800" in wire and "\\\\uDFFF" in wire,
    )
    try:
        scalarize({"\ud800": 1, "\\uD800": 2})
    except DiagnosticError:
        rejected_collision = True
    else:
        rejected_collision = False
    check("reject-surrogate-escaping-dictionary-key-collision", rejected_collision)
    case_only = {
        "op": "prepare",
        "case": {"value": "\ud800"},
        "expected": {"result": "normal"},
    }
    check(
        "detect-original-packed-case-surrogate-with-clean-expected",
        surrogate_paths(case_only, "$.request")
        == [{
            "path": "$.request.case.value",
            "character_index": 0,
            "codepoint": "U+D800",
        }],
    )
    families = [
        {
            "module": module,
            "prepare": "error",
            "unicode_encoding_error": original_error,
        }
        for module in MODULES
    ]
    check(
        "preserve-all-four-original-worker-surrogate-failures",
        len(families) == 4
        and all(
            item["prepare"] == "error"
            and item["unicode_encoding_error"]["codepoints"] == ["U+D800"]
            and item["unicode_encoding_error"]["start"] == ENCODING_ERROR_POSITION
            for item in families
        ),
    )
    safe_families = json.loads(canonical(families))
    check(
        "all-four-worker-error-reports-remain-strict-scalar-json",
        len(safe_families) == 4
        and not surrogate_paths(safe_families)
        and all(
            item["unicode_encoding_error"]["class"] == "UnicodeEncodeError"
            and item["unicode_encoding_error"]["start"] == ENCODING_ERROR_POSITION
            and item["unicode_encoding_error"]["codepoints"] == ["U+D800"]
            for item in safe_families
        ),
    )
    candidate_free()
    check("self-test-never-imported-any-production-candidate", True)
    check(
        "self-test-never-imported-frozen-v1-diagnostic",
        "_rebar_frozen_postfinal_public_practice_v4_failure_diagnostic_v1"
        not in sys.modules,
    )
    check(
        "self-test-never-imported-frozen-measurement-runner",
        "tools.postfinal_public_practice_v4" not in sys.modules,
    )
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS",
        "check_count": len(checks),
        "checks": checks,
        "completed_public_cases": COMPLETE_CASES,
        "completed_public_rows": COMPLETE_ROWS,
        "frozen_worker_families": len(MODULES),
        "next_selected_index": NEXT_CASE_INDEX,
        "next_case": NEXT_CASE_ID,
        "frozen_v1_source_sha256": V1_SOURCE_SHA256,
        "frozen_v1_report_sha256": V1_REPORT_SHA256,
        "manifest_sha256": MANIFEST_SHA256,
        "compressed_raw_sha256": COMPRESSED_RAW_SHA256,
        "json_decodes_to_unicode_scalars": True,
        "candidate_imports": 0,
        "worker_processes": 0,
        "files_read": 0,
        "files_written": 0,
        "observe_requests": 0,
        "timing_performed": False,
        "benchmark_performed": False,
        "holdout_accessed": False,
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--diagnose", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(arguments)
    if args.self_test:
        if args.output is not None:
            parser.error("candidate-free self-test never reads or writes evidence")
        print(canonical(synthetic_self_test()))
        return 0
    return diagnose(OUTPUT_PATH if args.output is None else args.output)


if __name__ == "__main__":
    raise SystemExit(main())
