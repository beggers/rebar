#!/usr/bin/env python3
"""Diagnose the frozen interrupted V4 public run without measuring again.

The candidate-free self-test uses only in-memory synthetic data.  Actual
diagnosis is available only through an explicit --diagnose request.  It
validates the immutable 310,700-row public prefix and invokes only the exact
audited V4 persistent workers' original prepare protocol.  It never sends an
observe request, collects timing, changes existing evidence, or opens a
held-out input.
"""

from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable


SCHEMA = "rebar-postfinal-public-practice-v4-interrupted-diagnostic-v1"
ROOT = Path(__file__).resolve().parent.parent
RUNNER = Path(__file__).resolve()
FROZEN_RUNNER = ROOT / "tools" / "postfinal_public_practice_v4.py"
VERSION_ROOT = ROOT / "performance" / "postfinal-public-v4"
MANIFEST_PATH = VERSION_ROOT / "manifest.json"
RAW_PATH = (
    VERSION_ROOT
    / "evidence"
    / "postfinal-public-practice-v4-raw.jsonl.gz"
)
OUTPUT_PATH = (
    VERSION_ROOT
    / "evidence"
    / "postfinal-public-practice-v4-interrupted-diagnostic.json"
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
NEXT_CASE_API = "findall"
SURROGATE_CODEPOINT = 0xD800
ENCODING_ERROR_POSITION = 224
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_ROW_BYTES = 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 1024 * 1024 * 1024
HASH_CHUNK_BYTES = 1024 * 1024


class DiagnosticError(RuntimeError):
    """Immutable public evidence or prepare-only diagnosis failed closed."""


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
    require(
        not loaded,
        f"prepare-only diagnostic controller imported a production engine: {loaded!r}",
    )


def canonical(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_path(path: Path, *, maximum: int | None = None) -> str:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while True:
            block = stream.read(HASH_CHUNK_BYTES)
            if not block:
                break
            size += len(block)
            if maximum is not None:
                require(
                    size <= maximum,
                    f"frozen diagnostic source exceeds its safe bound: {path.name}",
                )
            digest.update(block)
    return digest.hexdigest()


def normalize(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, bytes):
        return {"kind": "bytes", "hex": value.hex()}
    if isinstance(value, tuple):
        return {"tuple": [normalize(item) for item in value]}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): normalize(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    return {"kind": type(value).__name__, "text": str(value)}


def exception_snapshot(error: BaseException, depth: int = 0) -> dict[str, Any]:
    require(depth <= 8, "controller exception chain exceeds its safe bound")
    result: dict[str, Any] = {
        "class": type(error).__name__,
        "args": normalize(error.args),
        "message": str(error),
        "suppress_context": error.__suppress_context__,
        "cause": (
            exception_snapshot(error.__cause__, depth + 1)
            if error.__cause__ is not None else None
        ),
        "context": (
            exception_snapshot(error.__context__, depth + 1)
            if error.__context__ is not None else None
        ),
    }
    if isinstance(error, UnicodeEncodeError):
        result["encoding"] = error.encoding
        result["reason"] = error.reason
        result["start"] = error.start
        result["end"] = error.end
        result["codepoints"] = [
            f"U+{ord(character):04X}"
            for character in error.object[error.start:error.end]
        ]
    return result


def find_unicode_failure(snapshot: dict[str, Any]) -> dict[str, Any] | None:
    if snapshot.get("class") == "UnicodeEncodeError":
        return snapshot
    for key in ("cause", "context"):
        child = snapshot.get(key)
        if isinstance(child, dict):
            found = find_unicode_failure(child)
            if found is not None:
                return found
    return None


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
        for key in sorted(value, key=str):
            result.extend(surrogate_paths(value[key], f"{prefix}.{key}"))
    elif isinstance(value, (tuple, list)):
        for index, item in enumerate(value):
            result.extend(surrogate_paths(item, f"{prefix}[{index}]"))
    return result


def validate_output(value: Path) -> Path:
    resolved = value.resolve()
    require(
        resolved == OUTPUT_PATH.resolve(),
        "diagnosis must exclusively use the exact additive V4 interruption report",
    )
    require(
        resolved.parent == (VERSION_ROOT / "evidence").resolve(),
        "diagnosis escaped the exact frozen V4 public evidence directory",
    )
    return resolved


def validate_prefix(
    stream: Any,
    entries: list[Any],
    *,
    complete_cases: int,
    modules: tuple[str, ...],
    trials: int,
    order_seed: int,
    trial_order: Callable[..., Any],
    row_schema: str,
    practice: str,
    source_kind: Callable[[dict[str, Any]], str],
    density: Callable[[Any], str],
    max_operations: int,
) -> dict[str, Any]:
    require(
        len(entries) > complete_cases,
        "the immutable public manifest omits the first interrupted case",
    )
    digest = hashlib.sha256()
    rows = 0
    total_bytes = 0
    modules_seen: collections.Counter[str] = collections.Counter()
    for position in range(complete_cases):
        _index, case, expected, reasons = entries[position]
        require(
            isinstance(case, dict)
            and isinstance(expected, dict)
            and case.get("cohort") == practice
            and expected.get("cohort") == practice
            and case.get("id") == expected.get("id"),
            "a nonpublic or substituted frozen case reached prefix verification",
        )
        operations = min(case["ops"], max_operations)
        for trial in range(trials):
            order = trial_order(modules, case["id"], trial, order_seed)
            require(
                len(order) == len(modules) and set(order) == set(modules),
                "the frozen four-family public paired trial order changed",
            )
            for order_index, module in enumerate(order):
                line = stream.readline(MAX_ROW_BYTES + 1)
                require(
                    bool(line)
                    and isinstance(line, bytes)
                    and len(line) <= MAX_ROW_BYTES
                    and line.endswith(b"\n"),
                    "interrupted raw stream has a missing or excessive public row",
                )
                total_bytes += len(line)
                require(
                    total_bytes <= MAX_UNCOMPRESSED_BYTES,
                    "interrupted public raw stream exceeds its decompression bound",
                )
                try:
                    row = json.loads(line)
                except (UnicodeError, ValueError) as error:
                    raise DiagnosticError(
                        "interrupted public raw stream contains invalid JSON"
                    ) from error
                require(
                    isinstance(row, dict),
                    "interrupted public raw row is not an object",
                )
                encoded = (
                    json.dumps(
                        row,
                        ensure_ascii=False,
                        allow_nan=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                    + "\n"
                ).encode("utf-8")
                require(
                    encoded == line,
                    "interrupted public raw row is not exactly frozen canonical JSON",
                )
                require(
                    row.get("schema") == row_schema
                    and row.get("measurement")
                    == "bounded practice diagnostic only; not a holdout result"
                    and row.get("case") == case["id"]
                    and row.get("cohort") == practice
                    and row.get("category") == case["category"]
                    and row.get("api") == case["api"]
                    and row.get("lifecycle") == case["lifecycle"]
                    and row.get("input") == source_kind(case)
                    and row.get("result_density") == density(expected["result"])
                    and row.get("selection_reasons") == list(reasons)
                    and row.get("module") == module
                    and row.get("trial") == trial
                    and row.get("order") == order_index
                    and row.get("operations") == operations
                    and row.get("frozen_operations") == case["ops"]
                    and row.get("expected_sha256") == expected["result_sha256"],
                    "interrupted public raw stream changed a complete paired case",
                )
                digest.update(line)
                modules_seen[module] += 1
                rows += 1
    require(
        rows == complete_cases * len(modules) * trials,
        "interrupted raw complete-case denominator is not exact",
    )
    require(
        all(
            modules_seen[module] == complete_cases * trials
            for module in modules
        ),
        "interrupted raw prefix is missing an independent worker family",
    )
    trailing = stream.readline(MAX_ROW_BYTES + 1)
    require(
        trailing == b"",
        "interrupted public raw stream contains a partial or extra case",
    )
    return {
        "complete_cases": complete_cases,
        "complete_rows": rows,
        "trials_per_case": trials,
        "modules_per_trial": len(modules),
        "module_row_counts": dict(sorted(modules_seen.items())),
        "uncompressed_raw_sha256": digest.hexdigest(),
        "uncompressed_bytes": total_bytes,
        "trailing_partial_case": False,
    }


def load_frozen_runner() -> Any:
    candidate_free()
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    frozen = importlib.import_module("tools.postfinal_public_practice_v4")
    require(
        Path(frozen.__file__).resolve() == FROZEN_RUNNER.resolve(),
        "a substituted V4 public measurement runner was imported",
    )
    frozen.require_candidate_free()
    frozen.require_pinned_python()
    require(
        frozen.VERSION == "postfinal-public-practice-v4"
        and tuple(frozen.MODULES) == MODULES
        and frozen.CASES == 8_192
        and frozen.TRIALS == TRIALS
        and frozen.MAX_OPERATIONS == 16
        and frozen.MANIFEST_PATH.resolve() == MANIFEST_PATH.resolve()
        and frozen.RAW_PATH.resolve() == RAW_PATH.resolve(),
        "the immutable original V4 public protocol changed",
    )
    candidate_free()
    return frozen


def make_traced_worker(frozen: Any) -> type:
    class PrepareOnlyPersistentGuardedWorker(frozen.PersistentGuardedWorker):
        def __init__(
            self,
            runtime_audit: Any,
            module: str,
            native_fingerprints: dict[str, str],
        ) -> None:
            self.controller_trace: list[dict[str, Any]] = []
            super().__init__(runtime_audit, module, native_fingerprints)

        def request(self, document: dict[str, Any]) -> dict[str, Any]:
            operation = document.get("op")
            require(
                operation in {"verify", "prepare", "quit"},
                "prepare-only diagnostic refused an observation or timing request",
            )
            event: dict[str, Any] = {
                "operation": operation,
                "wire_json_ensure_ascii": False,
                "wire_text_encoding": "utf-8",
                "wire_text_errors": "strict",
            }
            if operation == "verify":
                event["force_hash"] = document.get("force_hash", False)
            try:
                response = super().request(document)
            except Exception as error:
                event["status"] = "error"
                event["error"] = exception_snapshot(error)
                self.controller_trace.append(event)
                raise
            event["status"] = "passed"
            event["response"] = normalize(response)
            self.controller_trace.append(event)
            return response

        def observe(self, **kwargs: Any) -> Any:
            raise DiagnosticError(
                "prepare-only interruption diagnostic must never observe or measure"
            )

    return PrepareOnlyPersistentGuardedWorker


def diagnose_prepare(
    frozen: Any,
    runtime_audit: Any,
    native: dict[str, str],
    case: dict[str, Any],
    expected: dict[str, Any],
) -> list[dict[str, Any]]:
    worker_type = make_traced_worker(frozen)
    workers: dict[str, Any] = {}
    results: dict[str, dict[str, Any]] = {}
    try:
        for module in MODULES:
            workers[module] = worker_type(runtime_audit, module, native)
            candidate_free()
        for module in MODULES:
            worker = workers[module]
            try:
                worker.prepare(case, expected)
            except Exception as error:
                snapshot = exception_snapshot(error)
                results[module] = {
                    "module": module,
                    "family": frozen.WORKER_FAMILIES[module],
                    "case": case["id"],
                    "prepare": "error",
                    "error": snapshot,
                    "unicode_encoding_error": find_unicode_failure(snapshot),
                }
            else:
                results[module] = {
                    "module": module,
                    "family": frozen.WORKER_FAMILIES[module],
                    "case": case["id"],
                    "prepare": "passed",
                    "error": None,
                    "unicode_encoding_error": None,
                }
            candidate_free()
    finally:
        for module in MODULES:
            worker = workers.get(module)
            if worker is None:
                continue
            try:
                worker.close()
            except Exception as error:
                if module in results:
                    results[module]["close_error"] = exception_snapshot(error)
                else:
                    results[module] = {
                        "module": module,
                        "family": frozen.WORKER_FAMILIES[module],
                        "case": case["id"],
                        "prepare": "not-run",
                        "error": exception_snapshot(error),
                        "unicode_encoding_error": None,
                    }
            if module in results:
                results[module]["controller_guard_trace"] = (
                    worker.controller_trace
                )
    require(
        set(results) == set(MODULES),
        "prepare-only diagnostic omitted a frozen independent worker family",
    )
    return [results[module] for module in MODULES]


def classify(results: list[dict[str, Any]]) -> dict[str, Any]:
    require(len(results) == len(MODULES), "prepare diagnosis lost a worker result")
    require(
        [item.get("module") for item in results] == list(MODULES),
        "prepare diagnosis reordered the four independent public workers",
    )
    errors = [item.get("unicode_encoding_error") for item in results]
    all_same = all(
        isinstance(item, dict)
        and item.get("class") == "UnicodeEncodeError"
        and item.get("encoding") == "utf-8"
        and item.get("reason") == "surrogates not allowed"
        and item.get("start") == ENCODING_ERROR_POSITION
        and item.get("codepoints") == ["U+D800"]
        for item in errors
    )
    all_failed = all(item.get("prepare") == "error" for item in results)
    return {
        "classification": (
            "frozen-controller-utf8-surrogate-serialization"
            if all_same and all_failed
            else "independent-prepare-divergence"
        ),
        "all_four_workers_failed": all_failed,
        "identical_unicode_encoding_failure": all_same,
        "mismatching_candidates": (
            []
            if all_same and all_failed
            else [
                item["module"]
                for item in results
                if item.get("prepare") != results[0].get("prepare")
                or item.get("unicode_encoding_error") != errors[0]
            ]
        ),
        "candidate_correctness_mismatch": (
            False if all_same and all_failed else None
        ),
        "wire_json_ensure_ascii": False,
        "wire_text_encoding": "utf-8",
        "wire_text_errors": "strict",
        "surrogate_codepoint": "U+D800",
        "expected_encoding_error_position": ENCODING_ERROR_POSITION,
        "observation_requests": 0,
        "timing_performed": False,
    }


def write_exclusive(path: Path, report: dict[str, Any]) -> str:
    encoded = (canonical(report) + "\n").encode("ascii")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(encoded)
    return hashlib.sha256(encoded).hexdigest()


def diagnose(output: Path) -> int:
    candidate_free()
    frozen = load_frozen_runner()
    destination = validate_output(output)
    require(
        not destination.exists(),
        "refusing to overwrite the frozen V4 interruption diagnostic",
    )
    manifest_hash = sha256_path(MANIFEST_PATH)
    require(
        manifest_hash == MANIFEST_SHA256,
        "the exact immutable interrupted V4 public manifest changed",
    )
    compressed_hash = sha256_path(RAW_PATH)
    require(
        compressed_hash == COMPRESSED_RAW_SHA256,
        "the exact immutable interrupted V4 compressed raw stream changed",
    )
    suite, entries, plan, verified_manifest_hash = (
        frozen.load_frozen_manifest(MANIFEST_PATH)
    )
    require(
        verified_manifest_hash == MANIFEST_SHA256
        and plan.get("runner_sha256")
        == sha256_path(FROZEN_RUNNER, maximum=MAX_SOURCE_BYTES)
        and plan.get("cases") == frozen.CASES
        and plan.get("frozen_trials") == TRIALS
        and plan.get("modules") == list(MODULES)
        and len(entries) == frozen.CASES,
        "the frozen V4 source, manifest, public cases, or trial campaign changed",
    )
    audit_hash, sources, native, additive = (
        frozen.require_matching_audits(plan)
    )
    frozen.current_measured_fingerprints(sources, native)
    candidate_free()
    with RAW_PATH.open("rb") as compressed:
        with gzip.GzipFile(fileobj=compressed, mode="rb") as public_rows:
            prefix = validate_prefix(
                public_rows,
                entries,
                complete_cases=COMPLETE_CASES,
                modules=MODULES,
                trials=TRIALS,
                order_seed=frozen.ORDER_SEED,
                trial_order=frozen.pilot.trial_order,
                row_schema=frozen.pilot.ROW_SCHEMA,
                practice=frozen.pilot.PRACTICE,
                source_kind=frozen.pilot.source_kind,
                density=frozen.pilot.density,
                max_operations=frozen.MAX_OPERATIONS,
            )
    require(
        prefix["complete_rows"] == COMPLETE_ROWS
        and prefix["complete_cases"] == COMPLETE_CASES
        and COMPLETE_ROWS == COMPLETE_CASES * len(MODULES) * TRIALS,
        "the exact 310,700-row complete public case prefix changed",
    )
    _original_index, case, expected, reasons = entries[NEXT_CASE_INDEX]
    require(
        case.get("id") == NEXT_CASE_ID
        and expected.get("id") == NEXT_CASE_ID
        and case.get("api") == NEXT_CASE_API
        and case.get("cohort") == frozen.pilot.PRACTICE
        and expected.get("cohort") == frozen.pilot.PRACTICE,
        "the first unmeasured frozen public findall case was substituted",
    )
    prepare_document = {
        "op": "prepare",
        "case": frozen.pilot.pack_calibration_value(case),
        "expected": frozen.pilot.pack_calibration_value(expected),
    }
    expected_surrogates = surrogate_paths(
        prepare_document["expected"], "$.request.expected"
    )
    case_surrogates = surrogate_paths(
        prepare_document["case"], "$.request.case"
    )
    request_surrogates = surrogate_paths(prepare_document, "$.request")
    require(
        any(
            item["codepoint"] == f"U+{SURROGATE_CODEPOINT:04X}"
            for item in request_surrogates
        ),
        "the original packed frozen prepare request no longer contains U+D800",
    )
    original_request = json.dumps(
        prepare_document,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"
    try:
        original_request.encode("utf-8", errors="strict")
    except UnicodeEncodeError as error:
        original_request_error = exception_snapshot(error)
    else:
        raise DiagnosticError(
            "the original packed frozen prepare request unexpectedly encoded"
        )
    require(
        original_request_error.get("encoding") == "utf-8"
        and original_request_error.get("reason") == "surrogates not allowed"
        and original_request_error.get("start") == ENCODING_ERROR_POSITION
        and original_request_error.get("codepoints") == ["U+D800"],
        "the original packed frozen prepare request changed its UTF-8 failure",
    )
    runtime_audit = frozen.load_guarded_worker_module(
        additive["postfinal_no_delegation_audit_source_sha256"]
    )
    results = diagnose_prepare(
        frozen,
        runtime_audit,
        native,
        case,
        expected,
    )
    frozen.require_candidate_free()
    candidate_free()
    verified_again, sources_again, native_again, additive_again = (
        frozen.require_matching_audits(plan)
    )
    require(
        verified_again == audit_hash
        and sources_again == sources
        and native_again == native
        and additive_again == additive
        and sha256_path(MANIFEST_PATH) == MANIFEST_SHA256
        and sha256_path(RAW_PATH) == COMPRESSED_RAW_SHA256,
        "frozen V4 public input, audit, source, or native artifact changed",
    )
    conclusion = classify(results)
    complete = (
        conclusion["classification"]
        == "frozen-controller-utf8-surrogate-serialization"
        and conclusion["all_four_workers_failed"] is True
        and conclusion["identical_unicode_encoding_failure"] is True
        and conclusion["mismatching_candidates"] == []
    )
    report = {
        "schema": SCHEMA,
        "status": "PASS" if complete else "FAIL",
        "measurement_status": "INTERRUPTED",
        "protocol_version": frozen.VERSION,
        "measurement": (
            "prepare-only diagnosis of frozen interrupted public practice; "
            "no observation, timing, benchmark replay, or held-out input"
        ),
        "controller_candidate_imports": 0,
        "manifest_path": str(MANIFEST_PATH.resolve()),
        "manifest_sha256": MANIFEST_SHA256,
        "raw_path": str(RAW_PATH.resolve()),
        "compressed_raw_sha256": COMPRESSED_RAW_SHA256,
        "raw_stream": prefix,
        "frozen_cases": frozen.CASES,
        "completed_public_cases": COMPLETE_CASES,
        "completed_public_rows": COMPLETE_ROWS,
        "next_selected_index": NEXT_CASE_INDEX,
        "next_case": {
            "id": case["id"],
            "api": case["api"],
            "category": case["category"],
            "cohort": case["cohort"],
            "selection_reasons": list(reasons),
            "expected_result_sha256": expected["result_sha256"],
            "case_surrogates": case_surrogates,
            "expected_surrogates": expected_surrogates,
            "request_surrogates": request_surrogates,
        },
        "controller_wire": {
            "implementation": (
                "tools.postfinal_public_practice_v4.PersistentGuardedWorker"
                ".request"
            ),
            "json_ensure_ascii": False,
            "text_encoding": "utf-8",
            "text_errors": "strict",
            "original_request_encoding_error": original_request_error,
            "replacement_or_wire_patch": False,
        },
        "guarded_workers": results,
        "classification": conclusion,
        "source": {
            "diagnostic_path": RUNNER.relative_to(ROOT).as_posix(),
            "diagnostic_sha256": sha256_path(RUNNER, maximum=MAX_SOURCE_BYTES),
            "frozen_v4_runner_path": FROZEN_RUNNER.relative_to(ROOT).as_posix(),
            "frozen_v4_runner_sha256": plan["runner_sha256"],
        },
        "audits": {
            "from_scratch_audit_sha256": audit_hash,
            "qualified_source_fingerprints": sources,
            "native_elf_fingerprints": native,
            "additive_no_delegation": additive,
        },
        "module_order": list(MODULES),
        "prepare_requests": len(results),
        "observe_requests": 0,
        "timing_performed": False,
        "benchmark_performed": False,
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "failed": 0 if complete else 1,
    }
    output_hash = write_exclusive(destination, report)
    print(canonical({
        "schema": SCHEMA,
        "status": report["status"],
        "measurement_status": report["measurement_status"],
        "classification": conclusion["classification"],
        "output": str(destination),
        "sha256": output_hash,
        "manifest_sha256": MANIFEST_SHA256,
        "compressed_raw_sha256": COMPRESSED_RAW_SHA256,
        "complete_cases": COMPLETE_CASES,
        "complete_rows": COMPLETE_ROWS,
        "next_case": NEXT_CASE_ID,
        "worker_count": len(results),
        "identical_unicode_encoding_failure": (
            conclusion["identical_unicode_encoding_failure"]
        ),
        "candidate_correctness_mismatch": (
            conclusion["candidate_correctness_mismatch"]
        ),
        "observe_requests": 0,
        "timing_performed": False,
        "holdout_accessed": False,
    }))
    return 0 if complete else 1


def synthetic_self_test() -> dict[str, Any]:
    candidate_free()
    checks: list[dict[str, Any]] = []

    def check(label: str, condition: Any) -> None:
        require(condition, f"candidate-free interruption self-test failed: {label}")
        checks.append({"name": label, "passed": True})

    check(
        "exact-complete-public-row-denominator",
        COMPLETE_ROWS == COMPLETE_CASES * len(MODULES) * TRIALS,
    )
    check("exact-four-independent-worker-families", len(MODULES) == 4)
    check("exact-frozen-next-selected-index", NEXT_CASE_INDEX == COMPLETE_CASES)
    check(
        "hard-pinned-original-manifest-fingerprint",
        len(MANIFEST_SHA256) == 64 and MANIFEST_SHA256.startswith("15789"),
    )
    check(
        "hard-pinned-original-compressed-stream-fingerprint",
        len(COMPRESSED_RAW_SHA256) == 64
        and COMPRESSED_RAW_SHA256.startswith("4132"),
    )
    check(
        "exact-additive-exclusive-output",
        validate_output(OUTPUT_PATH) == OUTPUT_PATH.resolve(),
    )
    try:
        validate_output(
            OUTPUT_PATH.with_name("poisoned-v4-interruption-diagnostic.json")
        )
    except DiagnosticError:
        rejected = True
    else:
        rejected = False
    check("reject-substituted-evidence-output", rejected)

    def make_error() -> RuntimeError:
        try:
            (("x" * ENCODING_ERROR_POSITION) + "\ud800").encode(
                "utf-8",
                errors="strict",
            )
        except UnicodeEncodeError as cause:
            try:
                raise RuntimeError(
                    "the independently guarded synthetic worker rejected a request"
                ) from cause
            except RuntimeError as outer:
                return outer
        raise DiagnosticError("synthetic strict UTF-8 surrogate unexpectedly encoded")

    synthetic_error = exception_snapshot(make_error())
    nested = find_unicode_failure(synthetic_error)
    check(
        "preserve-original-controller-unicode-cause",
        isinstance(nested, dict)
        and nested.get("class") == "UnicodeEncodeError"
        and nested.get("encoding") == "utf-8"
        and nested.get("reason") == "surrogates not allowed"
        and nested.get("start") == ENCODING_ERROR_POSITION
        and nested.get("codepoints") == ["U+D800"],
    )
    check(
        "json-report-losslessly-escapes-lone-surrogate",
        json.loads(canonical({"value": "\ud800"}))["value"] == "\ud800",
    )
    check(
        "discover-nested-frozen-result-surrogate",
        surrogate_paths(
            {"result": ["normal", {"value": "\ud800"}]},
            "$.expected",
        )
        == [{
            "path": "$.expected.result[1].value",
            "character_index": 0,
            "codepoint": "U+D800",
        }],
    )
    check(
        "discover-packed-case-surrogate-with-clean-expected",
        surrogate_paths(
            {
                "op": "prepare",
                "case": {"value": "\ud800"},
                "expected": {"result": "normal"},
            },
            "$.request",
        )
        == [{
            "path": "$.request.case.value",
            "character_index": 0,
            "codepoint": "U+D800",
        }],
    )
    synthetic_results = [
        {
            "module": name,
            "family": (
                "re" if name == "re"
                else name.rsplit(".", 1)[-1].removesuffix("_candidate")
            ),
            "prepare": "error",
            "error": synthetic_error,
            "unicode_encoding_error": nested,
        }
        for name in MODULES
    ]
    conclusion = classify(synthetic_results)
    check(
        "classify-all-four-identical-controller-failures",
        conclusion["classification"]
        == "frozen-controller-utf8-surrogate-serialization"
        and conclusion["identical_unicode_encoding_failure"] is True
        and conclusion["all_four_workers_failed"] is True
        and conclusion["mismatching_candidates"] == []
        and conclusion["candidate_correctness_mismatch"] is False,
    )
    poisoned = [
        {**item} for item in synthetic_results
    ]
    poisoned[2] = {
        **poisoned[2],
        "prepare": "passed",
        "error": None,
        "unicode_encoding_error": None,
    }
    divergent = classify(poisoned)
    check(
        "retain-genuine-independent-candidate-divergence",
        divergent["classification"] == "independent-prepare-divergence"
        and "candidates.vm_candidate" in divergent["mismatching_candidates"]
        and divergent["candidate_correctness_mismatch"] is None,
    )
    candidate_free()
    check("self-test-never-imported-any-production-candidate", True)
    check("self-test-never-imported-frozen-measurement-runner", (
        "tools.postfinal_public_practice_v4" not in sys.modules
    ))
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
    modes.add_argument(
        "--self-test",
        action="store_true",
        help="run only candidate-free, in-memory poisoned diagnostic controls",
    )
    modes.add_argument(
        "--diagnose",
        action="store_true",
        help="explicitly verify frozen public rows and use only guarded prepare",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="the sole exclusive-create frozen V4 interruption diagnostic path",
    )
    args = parser.parse_args(arguments)
    if args.self_test:
        if args.output is not None:
            parser.error("candidate-free self-test never reads or writes evidence")
        print(canonical(synthetic_self_test()))
        return 0
    return diagnose(OUTPUT_PATH if args.output is None else args.output)


if __name__ == "__main__":
    raise SystemExit(main())
