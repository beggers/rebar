#!/usr/bin/env python3
"""Explain the current regex evidence without hiding any setup failure."""

from __future__ import annotations

import argparse
import builtins
import contextlib
import copy
import hashlib
import html
import importlib
import io
import json
import multiprocessing
import os
from pathlib import Path
import stat
import subprocess
import sys
import threading
import time
import types
from typing import Any, Callable, Iterator


ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "rebar-current-native-correctness-v3"
SOURCE_PATH = "tools/render_current_correctness_v3.py"
CHART_PATH = "docs/evidence/current-native-correctness-v3.svg"
MANIFEST_PATH = "docs/evidence/current-native-correctness-v3.json"
V2_SOURCE_PATH = "tools/render_current_correctness_v2.py"
V2_SOURCE_SHA256 = "fb86e3b4a002b46cb7e5da710e3cfe515ff13eb81cec3d2537c04f3681b82784"
V14_SOURCE_PATH = "tools/postfinal_cpython_locale_oracle_v14.py"
V14_SOURCE_SHA256 = "834abdda264bfc81ecf5d6712e524ce1c852b84ed7d8f69cfc26aba6a9ebeb42"
V14_PROTOCOL_PATH = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V14.md"
V14_PROTOCOL_SHA256 = "68d8a9044540b0bfeca86316fd4fedded23587333370903d818fce9cc8cf33f9"
V6_REFERENCE_SHA256 = "1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf"
METHOD_MATRIX_SHA256 = "5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a"
RUST_V13_FAILURE_SHA256 = "18f572e44382130fe6ae29a05bb4c063fccf95d92fc305c9548cb1a63ac01844"
RUST_V13_CAPTURE_SHA256 = "7ae58265f0b845b9f50b30fcb7c7c75018cbcb40d49d240760373a517c2b46c1"
RUST_V14_FAILURE_PATH = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v14-rust-failures.json"
)
RUST_V14_FAILURE_SHA256 = "81112de149d835befaf605419d7426355a4be5d82d97f696d956bcd82627cd8f"
RUST_V14_FAILURE_BYTES = 9023
RUST_V14_CAPTURE_PATH = (
    "oracle/cpython-3.14.6/evidence/"
    "postfinal-locale-v14-rust-failures-production-summary.json"
)
RUST_V14_CAPTURE_SHA256 = "6390b27630888ea1dc77b3d65decb7680b32f7df859dfde8f227a92dc4b1951d"
RUST_V14_CAPTURE_BYTES = 9722
RUST_V14_WORKER_STDOUT_SHA256 = (
    "6a9273b3fb308dad3bd803cf299f64571378ba1b1c9a545b3ee6653733348b57"
)
RUST_V14_SETUP_ERROR = "the V11 correctness controller must never import a candidate"
FAMILIES = (("rust", "Rust"), ("vm", "C"), ("zig", "Zig"))
PUBLIC_METHODS = 152
METHOD_GUARDS = 304
MAX_INPUT_BYTES = 128 * 1024 * 1024


class ChartError(Exception):
    """No incomplete, fabricated, or substituted evidence may become a chart."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise ChartError(message)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                       sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def _read_regular(relative: str, *, optional: bool = False) -> bytes | None:
    require(type(relative) is str and relative and "\\" not in relative,
            "a correctness artifact requires a declared safe relative path")
    path = Path(relative)
    require(not path.is_absolute() and ".." not in path.parts,
            "correctness evidence cannot escape its repository")
    flags = (os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
             | getattr(os, "O_CLOEXEC", 0))
    try:
        descriptor = os.open(str(ROOT / path), flags)
    except FileNotFoundError:
        if optional:
            return None
        raise
    try:
        info = os.fstat(descriptor)
        require(stat.S_ISREG(info.st_mode)
                and 0 < info.st_size <= MAX_INPUT_BYTES,
                "a correctness artifact is not a bounded real regular file")
        pieces: list[bytes] = []
        while True:
            part = os.read(descriptor, 1024 * 1024)
            if not part:
                break
            pieces.append(part)
        raw = b"".join(pieces)
        require(len(raw) == info.st_size,
                "a real correctness artifact changed during inspection")
        return raw
    finally:
        os.close(descriptor)


def _checked_json(path: str, expected: str, expected_bytes: int) -> dict[str, Any]:
    raw = _read_regular(path)
    require(raw is not None and len(raw) == expected_bytes
            and hashlib.sha256(raw).hexdigest() == expected,
            "an exact frozen upstream failure was changed: " + path)
    try:
        result = json.loads(raw)
    except (ValueError, UnicodeError) as error:
        raise ChartError("the actual original failure is not valid JSON") from error
    require(type(result) is dict,
            "the actual original failure must contain a complete object")
    return result


def _frozen_module(path: str, expected: str, name: str) -> types.ModuleType:
    raw = _read_regular(path)
    require(raw is not None and hashlib.sha256(raw).hexdigest() == expected,
            "a separately frozen correctness validator was changed: " + path)
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / path)
    exec(compile(raw, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    return module


def _validate_v14_failure(
    document: dict[str, Any], capture: dict[str, Any],
    *, frozen: Any, legacy: Any,
) -> dict[str, Any]:
    schema = "rebar-postfinal-cpython-full-public-locale-v14-actual-role-failure"
    for name, observed in (("real failed role", document),
                           ("complete original capture", capture)):
        require(observed.get("schema") == schema
                and observed.get("status") == "FAIL"
                and observed.get("role") == "rust"
                and observed.get("source_sha256") == V14_SOURCE_SHA256
                and observed.get("protocol_sha256") == V14_PROTOCOL_SHA256
                and observed.get("immutable_v6_reference_sha256")
                == V6_REFERENCE_SHA256
                and observed.get("synthetic") is False
                and observed.get("production_observations_invented") is False
                and observed.get("performance") == "NOT MEASURED"
                and observed.get("holdout") == "NOT ACCESSED",
                "the frozen latest Rust setup failure was substituted: " + name)
    require(document.get("actual_failure_destination") == RUST_V14_FAILURE_PATH
            and document.get("details") == capture.get("details"),
            "the exact failed-role report and original complete output disagree")
    details = document["details"]
    require(type(details) is dict and details.get("returncode") == 2
            and details.get("complete_streams_available") is True,
            "the actual failing original worker streams were lost")
    stdout = details.get("stdout")
    stderr = details.get("stderr")
    require(type(stdout) is dict and stdout.get("bytes") == 1975
            and stdout.get("sha256") == RUST_V14_WORKER_STDOUT_SHA256
            and stdout.get("truncated") is False
            and type(stderr) is dict and stderr.get("bytes") == 0
            and stderr.get("sha256") == hashlib.sha256(b"").hexdigest()
            and stderr.get("truncated") is False,
            "the genuine once-only original Rust worker output was discarded")
    progress = legacy._failure_progress(details)
    require(progress.get("completed_methods") == 0
            and progress.get("native_owner_guards") == 0
            and progress.get("cached_matcher_guards") == 0
            and progress.get("actual_error") == RUST_V14_SETUP_ERROR,
            "the actual pre-test controller-isolation failure was misreported")
    nested = details.get("actual_worker_failure_details")
    require(type(nested) is dict
            and nested.get("actual_error_type") == "ProofV11Error"
            and nested.get("actual_error") == RUST_V14_SETUP_ERROR
            and nested.get("completed_original_method_count") == 0
            and nested.get("completed_original_method_records") == []
            and nested.get("actual_native_owner_method_guard_checks") == 0
            and nested.get("actual_cached_matcher_method_guard_checks") == 0,
            "the original correctness-controller guard or zero-test count changed")
    preserved = capture.get("actual_exclusively_preserved_failure_reports")
    require(type(preserved) is list and len(preserved) == 1
            and type(preserved[0]) is dict
            and preserved[0].get("path") == RUST_V14_FAILURE_PATH
            and preserved[0].get("sha256") == RUST_V14_FAILURE_SHA256,
            "the exactly once-published latest failure was hidden or replayed")
    receipt = frozen._validate_publication_receipt(
        preserved[0].get("actual_exclusive_publication_receipt"),
    )
    require(len(receipt) == 11 and receipt.get("path") == RUST_V14_FAILURE_PATH
            and receipt.get("expected_payload_sha256") == RUST_V14_FAILURE_SHA256
            and receipt.get("expected_payload_bytes") == RUST_V14_FAILURE_BYTES
            and receipt.get("actual_payload_bytes_written")
            == RUST_V14_FAILURE_BYTES
            and receipt.get("actual_file_created") is True
            and receipt.get("actual_file_fsync") is True
            and receipt.get("actual_directory_fsync") is True
            and receipt.get("fully_durable_publication") is True
            and receipt.get("canonical_reread_succeeded") is True,
            "the actual complete 11-field durable failure receipt is missing")
    return {
        "family": "rust", "label": "Rust", "status": "FAIL",
        "completed_methods": 0, "total_methods": PUBLIC_METHODS,
        "native_owner_guards": 0, "cached_matcher_guards": 0,
        "actual_error": RUST_V14_SETUP_ERROR,
        "actual_error_type": "ProofV11Error",
        "failure_classification": "test-harness correctness-controller isolation",
        "full_official_suite_qualified": False,
        "failure_path": RUST_V14_FAILURE_PATH,
        "failure_sha256": RUST_V14_FAILURE_SHA256,
        "failure_summary_path": RUST_V14_CAPTURE_PATH,
        "failure_summary_sha256": RUST_V14_CAPTURE_SHA256,
        "actual_durable_failure_receipt_verified": True,
    }


def _snapshot() -> tuple[dict[str, Any], list[dict[str, str]]]:
    legacy = _frozen_module(V2_SOURCE_PATH, V2_SOURCE_SHA256,
                            "_rebar_frozen_current_correctness_v2")
    frozen = _frozen_module(V14_SOURCE_PATH, V14_SOURCE_SHA256,
                            "_rebar_frozen_official_correctness_v14")
    raw_protocol = _read_regular(V14_PROTOCOL_PATH)
    require(raw_protocol is not None
            and hashlib.sha256(raw_protocol).hexdigest() == V14_PROTOCOL_SHA256
            and frozen.SCHEMA == "rebar-postfinal-cpython-full-public-locale-v14"
            and frozen.SOURCE_RELATIVE == V14_SOURCE_PATH
            and frozen.PROTOCOL_RELATIVE == V14_PROTOCOL_PATH
            and frozen.PROTOCOL_SHA256 == V14_PROTOCOL_SHA256
            and frozen.V6_REFERENCE_SHA256 == V6_REFERENCE_SHA256
            and frozen.METHOD_MATRIX_SHA256 == METHOD_MATRIX_SHA256
            and tuple(frozen.FAMILIES) == tuple(name for name, _ in FAMILIES),
            "the genuine frozen latest original-suite validator was replaced")
    previous, previous_inputs = legacy._snapshot()
    legacy._validate_snapshot(previous)
    older = previous.get("historical_v12_rust_upstream_failure")
    require(type(older) is dict and older.get("status") == "STOPPED BEFORE TESTS"
            and older.get("family") == "rust"
            and older.get("completed_methods") == 0
            and older.get("cause") == "test-harness bridge wiring",
            "the actual first missing-bridge setup failure was concealed")
    previous_roles = previous.get("full_python_suite")
    require(type(previous_roles) is list and len(previous_roles) == 3,
            "the real previous all-family official-suite state was omitted")
    middle = previous_roles[0]
    require(type(middle) is dict and middle.get("family") == "rust"
            and middle.get("status") == "FAIL"
            and middle.get("completed_methods") == 0
            and middle.get("native_owner_guards") == 0
            and middle.get("cached_matcher_guards") == 0
            and middle.get("actual_error") ==
            "stage-07 blocked unowned matching import: re"
            and middle.get("failure_classification") ==
            "test-harness anti-delegation setup"
            and middle.get("failure_sha256") == RUST_V13_FAILURE_SHA256
            and middle.get("failure_summary_sha256") == RUST_V13_CAPTURE_SHA256
            and middle.get("actual_durable_failure_receipt_verified") is True,
            "the actual second anti-delegation setup failure was concealed")
    failure = _checked_json(RUST_V14_FAILURE_PATH,
                            RUST_V14_FAILURE_SHA256,
                            RUST_V14_FAILURE_BYTES)
    capture = _checked_json(RUST_V14_CAPTURE_PATH,
                            RUST_V14_CAPTURE_SHA256,
                            RUST_V14_CAPTURE_BYTES)
    latest = _validate_v14_failure(failure, capture,
                                   frozen=frozen, legacy=legacy)
    result = copy.deepcopy(previous)
    result["historical_v13_rust_upstream_failure"] = copy.deepcopy(middle)
    result["full_python_suite"] = [latest, *copy.deepcopy(previous_roles[1:])]
    result["official_suite_candidate_passes"] = sum(
        row.get("status") == "PASS" for row in result["full_python_suite"]
    )
    result["full_drop_in_compatibility"] = "NOT ESTABLISHED"
    identities = [copy.deepcopy(row) for row in previous_inputs]
    identities.extend((
        {"purpose": "frozen-v2-complete-evidence-validator",
         "path": V2_SOURCE_PATH, "sha256": V2_SOURCE_SHA256},
        {"purpose": "frozen-v14-original-upstream-validator",
         "path": V14_SOURCE_PATH, "sha256": V14_SOURCE_SHA256},
        {"purpose": "frozen-v14-original-upstream-protocol",
         "path": V14_PROTOCOL_PATH, "sha256": V14_PROTOCOL_SHA256},
        {"purpose": "rust-v14-real-upstream-setup-failure",
         "path": RUST_V14_FAILURE_PATH, "sha256": RUST_V14_FAILURE_SHA256},
        {"purpose": "rust-v14-complete-original-worker-failure-capture",
         "path": RUST_V14_CAPTURE_PATH, "sha256": RUST_V14_CAPTURE_SHA256},
    ))
    identities.sort(key=lambda item: item["path"])
    require(len(identities) == 31
            and len({row["path"] for row in identities}) == 31,
            "the exact 31 independently frozen current correctness inputs changed")
    return result, identities


def _validate_snapshot(snapshot: dict[str, Any]) -> None:
    require(type(snapshot) is dict and snapshot.get("candidate_count") == 3
            and snapshot.get("original_candidate_checks") == 669_594
            and snapshot.get("deeper_candidate_checks") == 1_179
            and snapshot.get("observed_original_or_deeper_mismatches") == 0
            and snapshot.get("full_drop_in_compatibility") == "NOT ESTABLISHED"
            and snapshot.get("performance") == "NOT MEASURED"
            and snapshot.get("holdout") == "NOT ACCESSED",
            "the actual original coverage or current speed disclosure changed")
    original = snapshot.get("rows")
    require(type(original) is list and len(original) == 6
            and all(type(row) is dict and row.get("status") == "PASS"
                    and row.get("mismatches") == 0
                    and row.get("passed") == row.get("total")
                    for row in original),
            "a genuine original or deeper engine mismatch was concealed")
    first = snapshot.get("historical_v12_rust_upstream_failure")
    require(type(first) is dict and first.get("family") == "rust"
            and first.get("status") == "STOPPED BEFORE TESTS"
            and first.get("completed_methods") == 0
            and first.get("cause") == "test-harness bridge wiring",
            "the first missing-bridge harness failure was concealed")
    second = snapshot.get("historical_v13_rust_upstream_failure")
    require(type(second) is dict and second.get("family") == "rust"
            and second.get("status") == "FAIL"
            and second.get("completed_methods") == 0
            and second.get("native_owner_guards") == 0
            and second.get("cached_matcher_guards") == 0
            and second.get("actual_error") ==
            "stage-07 blocked unowned matching import: re"
            and second.get("failure_classification") ==
            "test-harness anti-delegation setup",
            "the second genuine anti-delegation setup failure was concealed")
    suites = snapshot.get("full_python_suite")
    require(type(suites) is list and len(suites) == 3
            and tuple(row.get("family") for row in suites)
            == tuple(name for name, _ in FAMILIES),
            "an original upstream family was removed or counted twice")
    passed = 0
    for row in suites:
        require(type(row) is dict and row.get("total_methods") == PUBLIC_METHODS
                and row.get("status") in {"PASS", "FAIL", "NOT RUN"},
                "a genuine full-suite denominator or candidate status changed")
        if row["status"] == "PASS":
            require(row.get("completed_methods") == PUBLIC_METHODS
                    and row.get("passed_methods") == 151
                    and row.get("named_private_debug_skips") == 1
                    and row.get("native_owner_guards") == METHOD_GUARDS
                    and row.get("cached_matcher_guards") == METHOD_GUARDS
                    and row.get("full_official_suite_qualified") is True,
                    "a complete upstream pass weakened 152 original methods or guards")
            passed += 1
        elif row["status"] == "FAIL":
            require(type(row.get("completed_methods")) is int
                    and 0 <= row["completed_methods"] <= PUBLIC_METHODS
                    and type(row.get("native_owner_guards")) is int
                    and 0 <= row["native_owner_guards"] <= METHOD_GUARDS
                    and row.get("full_official_suite_qualified") is False,
                    "a failed original upstream role was falsely qualified")
            if row.get("failure_classification") == (
                    "test-harness correctness-controller isolation"):
                require(row.get("family") == "rust"
                        and row.get("actual_error") == RUST_V14_SETUP_ERROR
                        and row.get("actual_error_type") == "ProofV11Error"
                        and row.get("completed_methods") == 0
                        and row.get("native_owner_guards") == 0
                        and row.get("cached_matcher_guards") == 0,
                        "the latest zero-test correctness-controller setup changed")
        else:
            require(row.get("completed_methods") is None
                    and row.get("native_owner_guards") is None
                    and row.get("full_official_suite_qualified") is False,
                    "an unexecuted official suite received invented observations")
    require(snapshot.get("official_suite_candidate_passes") == passed,
            "the actual full-upstream candidate count was altered")


def _text(x: int, y: int, value: str, css: str = "body") -> str:
    return (f'<text x="{x}" y="{y}" class="{css}">'
            + html.escape(value) + "</text>")


def render_svg(snapshot: dict[str, Any]) -> bytes:
    _validate_snapshot(snapshot)
    suites = snapshot["full_python_suite"]
    passed = snapshot["official_suite_candidate_passes"]
    description = (
        "Three independent Rust, C and Zig engines each pass all 223,198 "
        "original and 393 deeper checks. " + str(passed) +
        " of three have passed the complete original 152-method Python suite. "
        "Three different Rust test-harness setup failures are preserved; none "
        "is a demonstrated regex mismatch. Speed and memory are not measured."
    )
    output = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1260" '
        'viewBox="0 0 1200 1260" role="img" aria-labelledby="title description">',
        '<title id="title">How close are we to replacing Python’s re?</title>',
        '<desc id="description">' + html.escape(description) + '</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,'
        "'Segoe UI',sans-serif}.title{font-size:35px;font-weight:760;fill:#10223b}"
        '.subtitle{font-size:16px;fill:#43536b}.metric{font-size:30px;'
        'font-weight:750;fill:#10223b}.metric-label{font-size:14px;fill:#43536b}'
        '.heading{font-size:21px;font-weight:720;fill:#10223b}.body{font-size:'
        '15px;fill:#25364e}.small{font-size:13px;fill:#43536b}.strong{font-size:'
        '16px;font-weight:720;fill:#10223b}.pass{font-size:14px;font-weight:720;'
        'fill:#116139}.warning{font-size:13px;font-weight:720;fill:#8a4b08}'
        '.pending{font-size:14px;font-weight:720;fill:#485870}.footer{font-size:'
        '15px;font-weight:650;fill:#25364e}</style>',
        '<rect width="1200" height="1260" rx="20" fill="#f5f8fc"/>',
        _text(54, 73, "How close are we to replacing Python’s re?", "title"),
        _text(56, 104,
              "Current from-scratch engines · fairly checked against Python 3.14.6",
              "subtitle"),
    ]
    for x, number, label in (
        (54, "3", "independent engines"),
        (338, "669,594", "original candidate-checks"),
        (622, "1,179", "deeper candidate-checks"),
        (906, "0", "observed regex mismatches"),
    ):
        output.extend((
            f'<rect x="{x}" y="132" width="240" height="93" rx="14" '
            'fill="#ffffff" stroke="#dce5ef"/>',
            _text(x + 16, 173, number, "metric"),
            _text(x + 16, 200, label, "metric-label"),
        ))
    output.extend((
        _text(56, 262, "Original correctness checks", "heading"),
        _text(56, 284,
              "The same 223,198 cases for every engine · 49 categories", "small"),
    ))
    for index, label in enumerate(("Rust", "C", "Zig")):
        y = 302 + index * 44
        output.extend((
            _text(67, y + 20, label, "strong"),
            f'<rect x="158" y="{y}" width="686" height="26" rx="7" '
            'fill="#17844e"/>',
            _text(861, y + 19, "223,198 / 223,198", "strong"),
            _text(1073, y + 19, "100%", "pass"),
        ))
    output.extend((
        _text(56, 470, "Deeper correctness checks", "heading"),
        _text(56, 492,
              "The same 393 difficult cases · including 64 fixed-seed cases",
              "small"),
    ))
    for index, label in enumerate(("Rust", "C", "Zig")):
        y = 510 + index * 44
        output.extend((
            _text(67, y + 20, label, "strong"),
            f'<rect x="158" y="{y}" width="686" height="26" rx="7" '
            'fill="#17844e"/>',
            _text(861, y + 19, "393 / 393", "strong"),
            _text(1073, y + 19, "100%", "pass"),
        ))
    output.extend((
        _text(56, 680, "Latest complete Python test suite", "heading"),
        _text(56, 701,
              "A real pass requires all 152 original methods and 304 "
              "independent native-owner checks.", "small"),
    ))
    for index, row in enumerate(suites):
        x = (54, 437, 820)[index]
        status = row["status"]
        if status == "PASS":
            fill, border, css = "#edf8f1", "#badeca", "pass"
            count = "151 passed + 1 debug-only skip"
            explanation = "304 / 304 independent owner checks"
        elif status == "FAIL":
            fill, border, css = "#fff8eb", "#f2d199", "warning"
            count = (f'{row["completed_methods"]} / 152 tests; '
                     f'{row["native_owner_guards"]} / 304 owners')
            if row.get("failure_classification") == (
                    "test-harness correctness-controller isolation"):
                status = "HARNESS SETUP FAILED"
                explanation = "Controller isolation; not a regex mismatch"
            else:
                explanation = "Original Python suite not qualified"
        else:
            fill, border, css = "#f1f4f9", "#d9e1ec", "pending"
            count = "152 original methods not yet run"
            explanation = "No compatibility result claimed"
        output.extend((
            f'<rect x="{x}" y="719" width="326" height="123" rx="13" '
            f'fill="{fill}" stroke="{border}"/>',
            _text(x + 16, 749, row["label"], "strong"),
            _text(x + 16, 773, status, css),
            _text(x + 16, 799, count, "body"),
            _text(x + 16, 825, explanation, "small"),
        ))
    output.extend((
        _text(56, 883, "Three preserved Rust test-harness setup failures", "heading"),
        _text(56, 904,
              "All three stopped before the first original Python test. "
              "None demonstrates a regex mismatch.", "small"),
    ))
    failure_lines = (
        ("1", "Missing bridge wiring", "0 / 152 tests · 0 owner checks"),
        ("2", "Anti-delegation import guard", "0 / 152 tests · 0 owner checks"),
        ("3", "Correctness-controller isolation", "0 / 152 tests · 0 owner checks"),
    )
    for index, (number, title, count) in enumerate(failure_lines):
        y = 920 + 53 * index
        output.extend((
            f'<rect x="54" y="{y}" width="1092" height="43" rx="9" '
            'fill="#fff8eb" stroke="#f2d199"/>',
            _text(72, y + 27, number + ".  " + title, "body"),
            _text(780, y + 26, count, "small"),
        ))
    output.extend((
        '<rect x="54" y="1095" width="1092" height="119" rx="12" '
        'fill="#ffffff" stroke="#dce5ef"/>',
        _text(72, 1125,
              f"Overall: {passed} / 3 engines have passed the complete original "
              "Python test suite.", "footer"),
        _text(72, 1151,
              "Full drop-in compatibility remains NOT ESTABLISHED until all "
              "frozen public checks pass.", "small"),
        _text(72, 1176,
              "Speed and memory: NOT MEASURED · final holdout: NOT ACCESSED.",
              "small"),
        '</svg>\n',
    ))
    return "\n".join(output).encode("utf-8")


def _bundle() -> tuple[bytes, bytes, dict[str, Any]]:
    snapshot, identities = _snapshot()
    chart = render_svg(snapshot)
    manifest = {
        "schema": SCHEMA + "-manifest", "status": "PASS",
        "generator_path": SOURCE_PATH,
        "chart_path": CHART_PATH,
        "chart_sha256": hashlib.sha256(chart).hexdigest(),
        "chart_bytes": len(chart),
        "validated_input_count": len(identities),
        "validated_inputs": identities,
        "snapshot": snapshot,
        "production_observations_invented": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    return chart, canonical(manifest), manifest


def _exclusive_publish(name: str, payload: bytes, directory: int) -> str:
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    try:
        descriptor = os.open(name, flags, 0o644, dir_fd=directory)
    except FileExistsError:
        descriptor = os.open(name, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                             | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory)
        try:
            require(stat.S_ISREG(os.fstat(descriptor).st_mode),
                    "an existing generated correctness output is unsafe")
            pieces: list[bytes] = []
            while True:
                piece = os.read(descriptor, 1024 * 1024)
                if not piece:
                    break
                pieces.append(piece)
            require(b"".join(pieces) == payload,
                    "refusing to overwrite distinct current correctness evidence")
        finally:
            os.close(descriptor)
        return "EXISTING IDENTICAL"
    try:
        sent = 0
        while sent < len(payload):
            amount = os.write(descriptor, payload[sent:])
            require(type(amount) is int and amount > 0,
                    "a real exclusive correctness write failed")
            sent += amount
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.fsync(directory)
    return "EXCLUSIVELY CREATED"


def _write(chart: bytes, manifest: bytes) -> dict[str, str]:
    flags = (os.O_RDONLY | os.O_DIRECTORY
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    root = os.open(str(ROOT), flags)
    docs = -1
    evidence = -1
    try:
        docs = os.open("docs", flags, dir_fd=root)
        evidence = os.open("evidence", flags, dir_fd=docs)
        return {
            "chart": _exclusive_publish("current-native-correctness-v3.svg",
                                         chart, evidence),
            "manifest": _exclusive_publish("current-native-correctness-v3.json",
                                            manifest, evidence),
        }
    finally:
        if evidence != -1:
            os.close(evidence)
        if docs != -1:
            os.close(docs)
        os.close(root)


@contextlib.contextmanager
def _source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {
        "file_reads": 0, "file_writes": 0, "candidate_imports": 0,
        "workers": 0, "threads": 0, "clock_samples": 0,
        "holdout_cases_read": 0, "performance_fixtures_read": 0,
        "blocked_file_reads": 0, "blocked_file_writes": 0,
        "blocked_candidate_imports": 0, "blocked_workers": 0,
        "blocked_threads": 0, "blocked_clock_samples": 0,
    }
    restorations: list[tuple[Any, str, Any]] = []

    def deny(counter: str, message: str) -> Callable[..., Any]:
        def reject(*_args: Any, **_kwargs: Any) -> Any:
            effects[counter] += 1
            raise ChartError(message)
        return reject

    def patch(owner: Any, field: str, substitute: Any) -> None:
        if hasattr(owner, field):
            restorations.append((owner, field, getattr(owner, field)))
            setattr(owner, field, substitute)

    block_read = deny("blocked_file_reads", "synthetic controls cannot read")
    block_write = deny("blocked_file_writes", "synthetic controls cannot write")
    block_import = deny("blocked_candidate_imports", "synthetic controls cannot import")
    block_worker = deny("blocked_workers", "synthetic controls cannot execute")
    block_thread = deny("blocked_threads", "synthetic controls cannot start threads")
    block_clock = deny("blocked_clock_samples", "synthetic controls cannot measure")
    try:
        patch(builtins, "open", block_read)
        patch(io, "open", block_read)
        for key in ("open", "read_bytes", "read_text", "exists", "stat",
                    "is_file", "is_dir", "iterdir", "glob", "rglob"):
            patch(Path, key, block_read)
        for key in ("open", "stat", "lstat", "listdir", "scandir"):
            patch(os, key, block_read)
        for key in ("write", "fsync", "mkdir", "makedirs", "rename", "replace",
                    "unlink", "remove"):
            patch(os, key, block_write)
        patch(Path, "write_bytes", block_write)
        patch(Path, "write_text", block_write)
        patch(subprocess, "run", block_worker)
        patch(subprocess, "Popen", block_worker)
        patch(os, "fork", block_worker)
        patch(multiprocessing.Process, "start", block_worker)
        patch(threading.Thread, "start", block_thread)
        for key in ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "process_time",
                    "process_time_ns", "thread_time", "thread_time_ns"):
            patch(time, key, block_clock)
        patch(importlib, "import_module", block_import)
        patch(builtins, "__import__", block_import)
        yield effects
    finally:
        for owner, field, previous in reversed(restorations):
            setattr(owner, field, previous)


def _synthetic_snapshot(statuses: tuple[str, str, str]) -> dict[str, Any]:
    rows = [{"family": name, "label": label, "kind": kind,
             "status": "PASS", "passed": count, "total": count,
             "mismatches": 0}
            for kind, count in (("original", 223_198), ("deeper", 393))
            for name, label in FAMILIES]
    suites: list[dict[str, Any]] = []
    for (family, label), status in zip(FAMILIES, statuses, strict=True):
        if status == "PASS":
            suites.append({
                "family": family, "label": label, "status": "PASS",
                "completed_methods": PUBLIC_METHODS,
                "total_methods": PUBLIC_METHODS, "passed_methods": 151,
                "named_private_debug_skips": 1,
                "native_owner_guards": METHOD_GUARDS,
                "cached_matcher_guards": METHOD_GUARDS,
                "full_official_suite_qualified": True,
            })
        elif status == "FAIL":
            suites.append({
                "family": family, "label": label, "status": "FAIL",
                "completed_methods": 0 if family == "rust" else 17,
                "total_methods": PUBLIC_METHODS,
                "native_owner_guards": 0 if family == "rust" else 35,
                "cached_matcher_guards": 0 if family == "rust" else 35,
                "actual_error": RUST_V14_SETUP_ERROR if family == "rust"
                else "synthetic unqualified upstream failure",
                "actual_error_type": "ProofV11Error" if family == "rust"
                else "SyntheticOfficialFailure",
                "failure_classification": (
                    "test-harness correctness-controller isolation"
                    if family == "rust" else "failed upstream role"
                ),
                "full_official_suite_qualified": False,
            })
        else:
            suites.append({
                "family": family, "label": label, "status": "NOT RUN",
                "completed_methods": None, "total_methods": PUBLIC_METHODS,
                "native_owner_guards": None, "cached_matcher_guards": None,
                "full_official_suite_qualified": False,
            })
    return {
        "candidate_count": 3, "original_candidate_checks": 669_594,
        "deeper_candidate_checks": 1_179,
        "observed_original_or_deeper_mismatches": 0, "rows": rows,
        "historical_v12_rust_upstream_failure": {
            "family": "rust", "status": "STOPPED BEFORE TESTS",
            "completed_methods": 0, "cause": "test-harness bridge wiring",
        },
        "historical_v13_rust_upstream_failure": {
            "family": "rust", "status": "FAIL", "completed_methods": 0,
            "native_owner_guards": 0, "cached_matcher_guards": 0,
            "actual_error": "stage-07 blocked unowned matching import: re",
            "failure_classification": "test-harness anti-delegation setup",
        },
        "full_python_suite": suites,
        "official_suite_candidate_passes": sum(s == "PASS" for s in statuses),
        "full_drop_in_compatibility": "NOT ESTABLISHED",
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def _self_test() -> dict[str, Any]:
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "source-only visualizations must never import a candidate")
    accepted = 0
    rejected = 0

    def reject(action: Callable[[], Any], why: str) -> None:
        nonlocal rejected
        try:
            action()
        except (ChartError, OSError, TypeError, ValueError, KeyError, ImportError):
            rejected += 1
        else:
            raise ChartError("an invalid synthetic chart was accepted: " + why)

    with _source_only_boundary() as effects:
        for status in (
            ("NOT RUN", "NOT RUN", "NOT RUN"),
            ("FAIL", "NOT RUN", "NOT RUN"),
            ("PASS", "NOT RUN", "NOT RUN"),
            ("PASS", "PASS", "NOT RUN"),
            ("PASS", "PASS", "PASS"),
            ("PASS", "FAIL", "NOT RUN"),
            ("PASS", "PASS", "FAIL"),
        ):
            synthetic = _synthetic_snapshot(status)
            image = render_svg(synthetic)
            require(image == render_svg(copy.deepcopy(synthetic))
                    and image.startswith(b"<svg ")
                    and image.endswith(b"</svg>\n")
                    and image.count(b"223,198 / 223,198") == 3
                    and image.count(b"393 / 393") == 3
                    and b"669,594" in image and b"1,179" in image
                    and b"Three preserved Rust test-harness setup failures" in image
                    and b"Missing bridge wiring" in image
                    and b"Anti-delegation import guard" in image
                    and b"Correctness-controller isolation" in image
                    and b"NOT MEASURED" in image and b"NOT ACCESSED" in image,
                    "a current synthetic chart changed its exact evidence")
            accepted += 1
        correct = _synthetic_snapshot(("FAIL", "NOT RUN", "NOT RUN"))
        image = render_svg(correct)
        require(b"HARNESS SETUP FAILED" in image
                and b"Controller isolation; not a regex mismatch" in image
                and b"0 / 152 tests; 0 / 304 owners" in image
                and image.count(b">NOT RUN</text>") == 2,
                "a genuine third harness failure was mislabeled")
        accepted += 1
        for field, bad in (
            ("candidate_count", 2),
            ("original_candidate_checks", 669_593),
            ("deeper_candidate_checks", 1_178),
            ("observed_original_or_deeper_mismatches", 1),
            ("official_suite_candidate_passes", 1),
            ("full_drop_in_compatibility", "PASS"),
            ("performance", "1.5x"),
            ("holdout", "ACCESSED"),
        ):
            changed = copy.deepcopy(correct)
            changed[field] = bad
            reject(lambda changed=changed: render_svg(changed), field)
        for index in range(6):
            for field, bad in (("status", "FAIL"), ("mismatches", 1),
                               ("passed", correct["rows"][index]["total"] - 1)):
                changed = copy.deepcopy(correct)
                changed["rows"][index][field] = bad
                reject(lambda changed=changed: render_svg(changed),
                       "concealed original mismatch")
        for field, bad in (("completed_methods", 1),
                           ("native_owner_guards", 1),
                           ("cached_matcher_guards", 1),
                           ("actual_error", "invented regex mismatch"),
                           ("actual_error_type", "InventedError"),
                           ("full_official_suite_qualified", True),
                           ("total_methods", 151)):
            changed = copy.deepcopy(correct)
            changed["full_python_suite"][0][field] = bad
            reject(lambda changed=changed: render_svg(changed),
                   "forged latest setup failure: " + field)
        for index in (1, 2):
            for field, bad in (("status", "PASS"),
                               ("completed_methods", PUBLIC_METHODS),
                               ("native_owner_guards", METHOD_GUARDS),
                               ("full_official_suite_qualified", True)):
                changed = copy.deepcopy(correct)
                changed["full_python_suite"][index][field] = bad
                reject(lambda changed=changed: render_svg(changed),
                       "invented unexecuted original suite")
        for name in ("historical_v12_rust_upstream_failure",
                     "historical_v13_rust_upstream_failure"):
            for field, bad in (("status", "PASS"), ("completed_methods", 152)):
                changed = copy.deepcopy(correct)
                changed[name][field] = bad
                reject(lambda changed=changed: render_svg(changed),
                       "concealed original setup failure")
        forged_pass = _synthetic_snapshot(("PASS", "NOT RUN", "NOT RUN"))
        for field, bad in (("passed_methods", 152),
                           ("named_private_debug_skips", 0),
                           ("native_owner_guards", METHOD_GUARDS - 1),
                           ("cached_matcher_guards", METHOD_GUARDS - 1)):
            changed = copy.deepcopy(forged_pass)
            changed["full_python_suite"][0][field] = bad
            reject(lambda changed=changed: render_svg(changed),
                   "forged authentic private skip or method guard")
        reject(lambda: builtins.open(RUST_V14_FAILURE_PATH, "rb"),
               "read actual root-owned original evidence")
        reject(lambda: os.open(RUST_V14_CAPTURE_PATH, os.O_RDONLY),
               "read actual original worker output")
        reject(lambda: (ROOT / V14_SOURCE_PATH).read_bytes(),
               "read an actual original proof controller")
        reject(lambda: (ROOT / "performance").exists(),
               "open a benchmark or holdout")
        reject(lambda: importlib.import_module("candidates.rust_candidate"),
               "execute a matching candidate")
        reject(lambda: builtins.__import__("candidates.zig_candidate"),
               "import a second matching candidate")
        reject(lambda: subprocess.run(["candidate-worker"]),
               "start an original worker")
        reject(lambda: threading.Thread(target=lambda: None).start(),
               "create a worker thread")
        reject(time.perf_counter, "measure a benchmark clock")
        reject(lambda: (ROOT / CHART_PATH).write_bytes(b"fabricated"),
               "write an unauthorized chart")
        require(all(effects[name] == 0 for name in (
            "file_reads", "file_writes", "candidate_imports", "workers",
            "threads", "clock_samples", "holdout_cases_read",
            "performance_fixtures_read",
        )), "a source-only chart control had a real production side effect")
        require(effects["blocked_file_reads"] >= 4
                and effects["blocked_file_writes"] >= 1
                and effects["blocked_candidate_imports"] >= 2
                and effects["blocked_workers"] >= 1
                and effects["blocked_threads"] >= 1
                and effects["blocked_clock_samples"] >= 1,
                "the candidate-free source boundary failed to block real effects")
        preserved = dict(effects)
    return {
        "schema": SCHEMA + "-source-self-test", "status": "PASS",
        "synthetic_only": True,
        "accepted_controls": accepted, "rejected_controls": rejected,
        "total_controls": accepted + rejected,
        "actual_v14_failure_reads": 0,
        "actual_candidates_qualified": 0,
        "frozen_v2_source_sha256": V2_SOURCE_SHA256,
        "frozen_v14_source_sha256": V14_SOURCE_SHA256,
        "frozen_v14_protocol_sha256": V14_PROTOCOL_SHA256,
        "effects": preserved,
        "production_observations_invented": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Show only genuinely frozen, current regex correctness evidence."
    )
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--self-test", action="store_true")
    actions.add_argument("--check", action="store_true")
    actions.add_argument("--write", action="store_true")
    selected = parser.parse_args(arguments)
    try:
        if selected.self_test:
            result = _self_test()
        else:
            chart, manifest, document = _bundle()
            if selected.write:
                publication = _write(chart, manifest)
            else:
                require(_read_regular(CHART_PATH) == chart
                        and _read_regular(MANIFEST_PATH) == manifest,
                        "the exact frozen chart and manifest cannot be reproduced")
                publication = {"chart": "VERIFIED", "manifest": "VERIFIED"}
            result = {
                "schema": SCHEMA + ("-write" if selected.write else "-check"),
                "status": "PASS", "chart_path": CHART_PATH,
                "chart_sha256": document["chart_sha256"],
                "manifest_path": MANIFEST_PATH,
                "manifest_sha256": hashlib.sha256(manifest).hexdigest(),
                "validated_input_count": document["validated_input_count"],
                "official_suite_candidate_passes": document["snapshot"][
                    "official_suite_candidate_passes"
                ],
                "publication": publication,
                "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
            }
    except (ChartError, AssertionError, OSError, ValueError,
            TypeError, KeyError, MemoryError) as error:
        print(json.dumps({
            "schema": SCHEMA + "-failure", "status": "FAIL",
            "actual_error_type": type(error).__name__,
            "reason": str(error),
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }, ensure_ascii=True, sort_keys=True, separators=(",", ":")),
              file=sys.stderr)
        return 2
    print(canonical(result).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
