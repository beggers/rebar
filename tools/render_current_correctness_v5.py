#!/usr/bin/env python3
"""Render the complete, explicitly scoped from-scratch regex experiment."""

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
SCHEMA = "rebar-current-native-correctness-v5"
SOURCE_PATH = "tools/render_current_correctness_v5.py"
CHART_PATH = "docs/evidence/current-native-correctness-v5.svg"
MANIFEST_PATH = "docs/evidence/current-native-correctness-v5.json"
V4_SOURCE_PATH = "tools/render_current_correctness_v4.py"
V4_SOURCE_SHA256 = "9a96e8732a21381e97fd55bb983deb1884e7e1d833604cb59a8d9f0800df2287"
REFERENCE_PATH = "oracle/cpython-3.14.6/evidence/postfinal-locale-v6-self-oracle.json"
REFERENCE_SHA256 = "1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf"
METHOD_MATRIX_SHA256 = "5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a"
ALL_ORIGINAL_METHODS = 165
PUBLIC_METHODS = 152
PRIVATE_WAIVER_CLASSES = 2
PRIVATE_WAIVER_METHODS = 13
RUNNABLE_REFERENCE_METHODS = 151
METHOD_GUARDS = 304
NAMED_PRIVATE_CLASS_WAIVERS = {
    "DebugTests": {
        "methods": 4,
        "reason": "CPython-only textual disassembly of private matching opcodes",
    },
    "ImplementationTest": {
        "methods": 9,
        "reason": (
            "private CPython regex compiler, _sre, type internals, and "
            "deprecated private implementation modules"
        ),
    },
}
PRIVATE_DEBUG_METHOD = "ReTests.test_memory_leaks"
PRIVATE_DEBUG_REASON = "requires debug build"
PRIVATE_DEBUG_SKIP_KIND = "named-private-debug-condition"
PRIVATE_DEBUG_SOURCE_AST_SHA256 = (
    "840264aaf4bf27c06d29ac78664767327a8f4b90008c5db994c88542c692b389"
)
PICKLING_METHOD = "ReTests.test_pickling"
PICKLING_ERROR = "cannot import name '_compile' from 'candidates.rust_candidate'"
FAMILIES = (("rust", "Rust"), ("vm", "C"), ("zig", "Zig"))
MAX_INPUT_BYTES = 128 * 1024 * 1024


class ChartError(Exception):
    """A claimed result or the full original-suite denominator was unproven."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise ChartError(message)


def canonical(document: Any) -> bytes:
    return (json.dumps(document, ensure_ascii=True, allow_nan=False,
                       sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def _read_regular(relative: str) -> bytes:
    require(type(relative) is str and relative and "\\" not in relative,
            "only an exact frozen relative correctness artifact may be read")
    target = Path(relative)
    require(not target.is_absolute() and ".." not in target.parts,
            "a frozen correctness artifact escaped its repository")
    flags = (os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
             | getattr(os, "O_CLOEXEC", 0))
    descriptor = os.open(str(ROOT / target), flags)
    try:
        information = os.fstat(descriptor)
        require(stat.S_ISREG(information.st_mode)
                and 0 < information.st_size <= MAX_INPUT_BYTES,
                "a frozen correctness input is not a bounded regular file")
        pieces: list[bytes] = []
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            pieces.append(block)
        result = b"".join(pieces)
        require(len(result) == information.st_size,
                "an actual frozen correctness input changed while it was read")
        return result
    finally:
        os.close(descriptor)


def _frozen_module(relative: str, expected: str, name: str) -> types.ModuleType:
    source = _read_regular(relative)
    require(hashlib.sha256(source).hexdigest() == expected,
            "the frozen current-result validator was substituted: " + relative)
    result = types.ModuleType(name)
    result.__file__ = str(ROOT / relative)
    exec(compile(source, result.__file__, "exec", dont_inherit=True),
         result.__dict__)
    return result


def _validate_scope(reference: dict[str, Any], legacy: Any) -> dict[str, Any]:
    require(type(reference) is dict
            and reference.get("schema") ==
            "rebar-postfinal-cpython-full-public-locale-v6-self-oracle"
            and reference.get("status") == "PASS"
            and reference.get("python") == "3.14.6"
            and reference.get("synthetic") is False
            and reference.get("all_original_methods") == ALL_ORIGINAL_METHODS
            and reference.get("public_original_methods") == PUBLIC_METHODS
            and reference.get("private_original_methods") == PRIVATE_WAIVER_METHODS
            and reference.get("public_method_waivers") == []
            and reference.get("named_private_class_waivers")
            == NAMED_PRIVATE_CLASS_WAIVERS
            and reference.get("actual_independent_reference_count") == 2
            and reference.get("public_method_matrix_sha256") == METHOD_MATRIX_SHA256
            and reference.get("reference_candidate_imports") == 0
            and reference.get("reference_candidate_audits_read") == 0
            and reference.get("reference_candidate_proofs_read") == 0
            and reference.get("reference_holdout_cases_read") == 0
            and reference.get("performance") == "NOT MEASURED"
            and reference.get("holdout") == "NOT ACCESSED",
            "the genuine original 165/152/13 named-waiver baseline was changed")
    require(sum(item["methods"] for item in NAMED_PRIVATE_CLASS_WAIVERS.values())
            == PRIVATE_WAIVER_METHODS
            and len(NAMED_PRIVATE_CLASS_WAIVERS) == PRIVATE_WAIVER_CLASSES
            and ALL_ORIGINAL_METHODS == PUBLIC_METHODS + PRIVATE_WAIVER_METHODS,
            "the complete original-method denominator no longer balances")
    roles = reference.get("roles")
    require(type(roles) is dict
            and tuple(roles) == ("reference_a", "reference_b"),
            "both original independent Python reference roles are mandatory")
    vectors: list[list[dict[str, Any]]] = []
    role_summaries: list[dict[str, Any]] = []
    for label in ("reference_a", "reference_b"):
        role = roles[label]
        require(type(role) is dict
                and role.get("applicable") == RUNNABLE_REFERENCE_METHODS
                and role.get("passed") == RUNNABLE_REFERENCE_METHODS
                and role.get("named_private_debug_skips") == 1
                and type(role.get("records")) is list
                and len(role["records"]) == PUBLIC_METHODS,
                "a genuine independent public reference lost an original method")
        vector: list[dict[str, Any]] = []
        observed_skips: list[dict[str, str]] = []
        for record in role["records"]:
            require(type(record) is dict
                    and type(record.get("test")) is str
                    and type(record.get("source_ast_sha256")) is str
                    and len(record["source_ast_sha256"]) == 64,
                    "an original public Python method lost its exact source identity")
            if record.get("status") == "SKIP":
                require(record.get("test") == PRIVATE_DEBUG_METHOD
                        and record.get("reason") == PRIVATE_DEBUG_REASON
                        and record.get("skip_kind") == PRIVATE_DEBUG_SKIP_KIND
                        and record.get("source_ast_sha256")
                        == PRIVATE_DEBUG_SOURCE_AST_SHA256,
                        "the genuine in-scope private debug-build skip was forged")
                observed_skips.append({
                    "test": record["test"],
                    "reason": record["reason"],
                    "skip_kind": record["skip_kind"],
                    "source_ast_sha256": record["source_ast_sha256"],
                })
            else:
                require(record.get("status") == "PASS",
                        "a baseline public Python method did not genuinely pass")
            vector.append({
                "test": record["test"],
                "source_ast_sha256": record["source_ast_sha256"],
                "status": record["status"],
                "skip_kind": record.get("skip_kind"),
                "reason": record.get("reason"),
            })
        require(len(observed_skips) == 1,
                "a public method was waived under a false debug-build reason")
        vectors.append(vector)
        role_summaries.append({
            "role": label,
            "public_method_records": PUBLIC_METHODS,
            "passed": RUNNABLE_REFERENCE_METHODS,
            "named_private_debug_skips": 1,
            "debug_skip": observed_skips[0],
        })
    require(vectors[0] == vectors[1],
            "the two real original 152-method baseline vectors disagree")
    vector_bytes = json.dumps(
        vectors[0], ensure_ascii=True, allow_nan=False,
        sort_keys=True, separators=(",", ":"),
    ).encode("ascii")
    require(hashlib.sha256(vector_bytes).hexdigest()
            == reference.get("reference_status_vector_sha256"),
            "the exact original-source-ordered baseline vector was changed")
    require(legacy.V6_REFERENCE_SHA256 == REFERENCE_SHA256
            and legacy.METHOD_MATRIX_SHA256 == METHOD_MATRIX_SHA256,
            "the frozen full-upstream evidence references were substituted")
    return {
        "baseline": "CPython 3.14.6 re",
        "original_source_method_count": ALL_ORIGINAL_METHODS,
        "applicable_public_method_count": PUBLIC_METHODS,
        "named_private_class_waiver_count": PRIVATE_WAIVER_CLASSES,
        "named_private_method_waiver_count": PRIVATE_WAIVER_METHODS,
        "named_private_class_waivers": copy.deepcopy(NAMED_PRIVATE_CLASS_WAIVERS),
        "public_method_waivers": [],
        "independent_reference_count": 2,
        "reference_runnable_pass_count": RUNNABLE_REFERENCE_METHODS,
        "reference_named_private_debug_skip_count": 1,
        "reference_roles": role_summaries,
        "reference_status_vector_sha256": reference["reference_status_vector_sha256"],
        "reference_path": REFERENCE_PATH,
        "reference_sha256": REFERENCE_SHA256,
        "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
    }


def _snapshot() -> tuple[dict[str, Any], list[dict[str, str]]]:
    previous = _frozen_module(V4_SOURCE_PATH, V4_SOURCE_SHA256,
                              "_rebar_frozen_current_correctness_v4")
    require(previous.SCHEMA == "rebar-current-native-correctness-v4"
            and previous.SOURCE_PATH == V4_SOURCE_PATH
            and previous.V6_REFERENCE_PATH == REFERENCE_PATH
            and previous.V6_REFERENCE_SHA256 == REFERENCE_SHA256
            and previous.METHOD_MATRIX_SHA256 == METHOD_MATRIX_SHA256,
            "the frozen complete V4 current correctness controller was replaced")
    original_snapshot, verified = previous._snapshot()
    previous._validate_snapshot(original_snapshot)
    reference = previous._checked_json(REFERENCE_PATH, REFERENCE_SHA256)
    scope = _validate_scope(reference, previous)
    result = copy.deepcopy(original_snapshot)
    result["original_python_test_scope"] = scope
    result["full_drop_in_compatibility"] = "NOT ESTABLISHED"
    inputs = [copy.deepcopy(entry) for entry in verified]
    inputs.append({
        "purpose": "frozen-v4-all-history-current-correctness-validator",
        "path": V4_SOURCE_PATH,
        "sha256": V4_SOURCE_SHA256,
    })
    inputs.sort(key=lambda entry: entry["path"])
    require(len(inputs) == 40
            and len({entry["path"] for entry in inputs}) == 40,
            "the exact 40 immutable all-history correctness identities changed")
    return result, inputs


def _validate_snapshot(snapshot: dict[str, Any]) -> None:
    require(type(snapshot) is dict
            and snapshot.get("candidate_count") == 3
            and snapshot.get("original_candidate_checks") == 669_594
            and snapshot.get("deeper_candidate_checks") == 1_179
            and snapshot.get("observed_original_or_deeper_mismatches") == 0
            and snapshot.get("official_suite_candidate_passes") == 0
            and snapshot.get("full_drop_in_compatibility") == "NOT ESTABLISHED"
            and snapshot.get("performance") == "NOT MEASURED"
            and snapshot.get("holdout") == "NOT ACCESSED",
            "an original/deeper count, current pass, or timing was fabricated")
    rows = snapshot.get("rows")
    require(type(rows) is list and len(rows) == 6
            and all(type(row) is dict and row.get("status") == "PASS"
                    and row.get("passed") == row.get("total")
                    and row.get("mismatches") == 0 for row in rows),
            "a genuine frozen original or deeper compatibility failure was hidden")
    scope = snapshot.get("original_python_test_scope")
    require(type(scope) is dict
            and scope.get("baseline") == "CPython 3.14.6 re"
            and scope.get("original_source_method_count") == ALL_ORIGINAL_METHODS
            and scope.get("applicable_public_method_count") == PUBLIC_METHODS
            and scope.get("named_private_class_waiver_count")
            == PRIVATE_WAIVER_CLASSES
            and scope.get("named_private_method_waiver_count")
            == PRIVATE_WAIVER_METHODS
            and scope.get("named_private_class_waivers")
            == NAMED_PRIVATE_CLASS_WAIVERS
            and scope.get("public_method_waivers") == []
            and scope.get("independent_reference_count") == 2
            and scope.get("reference_runnable_pass_count")
            == RUNNABLE_REFERENCE_METHODS
            and scope.get("reference_named_private_debug_skip_count") == 1
            and scope.get("reference_path") == REFERENCE_PATH
            and scope.get("reference_sha256") == REFERENCE_SHA256
            and scope.get("public_method_matrix_sha256") == METHOD_MATRIX_SHA256,
            "the genuine original 165/152/13 public-versus-private scope changed")
    baseline = scope.get("reference_roles")
    require(type(baseline) is list and len(baseline) == 2
            and tuple(row.get("role") for row in baseline)
            == ("reference_a", "reference_b"),
            "the two independent actual Python reference runs disappeared")
    for reference in baseline:
        debug = reference.get("debug_skip")
        require(reference.get("public_method_records") == PUBLIC_METHODS
                and reference.get("passed") == RUNNABLE_REFERENCE_METHODS
                and reference.get("named_private_debug_skips") == 1
                and type(debug) is dict
                and debug.get("test") == PRIVATE_DEBUG_METHOD
                and debug.get("reason") == PRIVATE_DEBUG_REASON
                and debug.get("skip_kind") == PRIVATE_DEBUG_SKIP_KIND
                and debug.get("source_ast_sha256")
                == PRIVATE_DEBUG_SOURCE_AST_SHA256,
                "an actual baseline named debug skip or source identity changed")
    for key, name in (
        ("historical_v12_rust_upstream_failure", "V12"),
        ("historical_v13_rust_upstream_failure", "V13"),
        ("historical_v14_rust_upstream_failure", "V14"),
    ):
        historical = snapshot.get(key)
        require(type(historical) is dict
                and historical.get("family") == "rust"
                and historical.get("completed_methods") == 0,
                "a genuine preserved zero-method harness failure changed: " + name)
        if name == "V12":
            require(historical.get("status") == "STOPPED BEFORE TESTS"
                    and historical.get("cause") == "test-harness bridge wiring",
                    "the real missing-bridge harness failure was hidden")
        elif name == "V13":
            require(historical.get("status") == "FAIL"
                    and historical.get("native_owner_guards") == 0
                    and historical.get("actual_error") ==
                    "stage-07 blocked unowned matching import: re",
                    "the real anti-delegation harness failure was hidden")
        else:
            require(historical.get("status") == "FAIL"
                    and historical.get("native_owner_guards") == 0
                    and historical.get("actual_error") ==
                    "the V11 correctness controller must never import a candidate",
                    "the real correctness-controller setup failure was hidden")
    suites = snapshot.get("full_python_suite")
    require(type(suites) is list and len(suites) == 3
            and tuple(row.get("family") for row in suites)
            == tuple(name for name, _ in FAMILIES),
            "an independent candidate full-suite result was omitted")
    rust = suites[0]
    harness = rust.get("harness_interference_error_records")
    gaps = rust.get("genuine_candidate_error_records")
    require(rust.get("label") == "Rust"
            and rust.get("status") == "FAIL"
            and rust.get("completed_methods") == PUBLIC_METHODS
            and rust.get("total_methods") == PUBLIC_METHODS
            and rust.get("passed_methods") == 139
            and rust.get("error_methods") == 12
            and rust.get("harness_interference_errors") == 11
            and rust.get("genuine_candidate_errors") == 1
            and rust.get("named_private_debug_skips") == 1
            and rust.get("native_owner_guards") == METHOD_GUARDS
            and rust.get("cached_matcher_guards") == METHOD_GUARDS
            and rust.get("genuine_candidate_error_test") == PICKLING_METHOD
            and rust.get("genuine_candidate_error") == PICKLING_ERROR
            and type(harness) is list and len(harness) == 11
            and type(gaps) is list and len(gaps) == 1
            and gaps[0].get("test") == PICKLING_METHOD
            and rust.get("full_official_suite_qualified") is False
            and 139 + 11 + 1 + 1 == PUBLIC_METHODS,
            "the actual original 139/11/1/1 Rust outcome was misrepresented")
    for entry in harness:
        require(type(entry) is dict and type(entry.get("test")) is str
                and entry.get("test") != PICKLING_METHOD
                and entry.get("classification")
                == "test-harness matcher-guard interference"
                and type(entry.get("reason_sha256")) is str
                and len(entry["reason_sha256"]) == 64,
                "a genuine test-harness error was relabeled as candidate matching")
    require(gaps[0].get("classification")
            == "from-scratch Rust private pickle hook missing"
            and type(gaps[0].get("reason_sha256")) is str
            and len(gaps[0]["reason_sha256"]) == 64,
            "the genuine missing Rust `_compile` original requirement was hidden")
    for (family, label), role in zip(FAMILIES[1:], suites[1:], strict=True):
        require(role.get("family") == family and role.get("label") == label
                and role.get("status") == "NOT RUN"
                and role.get("completed_methods") is None
                and role.get("native_owner_guards") is None
                and role.get("full_official_suite_qualified") is False,
                "an unexecuted C or Zig full-suite result was fabricated")


def _text(x: int, y: int, value: str, style: str = "body") -> str:
    return (f'<text x="{x}" y="{y}" class="{style}">'
            + html.escape(value) + "</text>")


def render_svg(snapshot: dict[str, Any]) -> bytes:
    _validate_snapshot(snapshot)
    description = (
        "Python 3.14.6 has 165 original regular-expression test methods: "
        "152 are public compatibility tests and 13 are explicitly waived "
        "CPython-private tests from two named classes. Both Python baseline runs "
        "pass 151 public methods and skip one genuine debug-build method. "
        "Rust processed the same 152 records: 139 pass, 11 expose "
        "test-harness interference, one exposes a real missing _compile "
        "pickling hook, and the same debug-only test is skipped. "
        "C and Zig have not run the original public tests. Current speed "
        "and memory remain unmeasured."
    )
    result = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1565" '
        'viewBox="0 0 1200 1565" role="img" aria-labelledby="title description">',
        '<title id="title">How close are we to replacing Python’s re?</title>',
        '<desc id="description">' + html.escape(description) + '</desc>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,'
        "'Segoe UI',sans-serif}.title{font-size:34px;font-weight:760;fill:#10223b}"
        '.subtitle{font-size:15px;fill:#43536b}.metric{font-size:29px;'
        'font-weight:750;fill:#10223b}.metric-label{font-size:13px;fill:#43536b}'
        '.heading{font-size:20px;font-weight:730;fill:#10223b}.body{font-size:'
        '15px;fill:#25364e}.small{font-size:13px;fill:#43536b}.strong{font-size:'
        '16px;font-weight:720;fill:#10223b}.pass{font-size:14px;font-weight:720;'
        'fill:#116139}.warning{font-size:14px;font-weight:720;fill:#8a4b08}'
        '.fail{font-size:14px;font-weight:720;fill:#aa2831}'
        '.pending{font-size:14px;font-weight:720;fill:#485870}.footer{font-size:'
        '15px;font-weight:650;fill:#25364e}</style>',
        '<rect width="1200" height="1565" rx="20" fill="#f5f8fc"/>',
        _text(54, 71, "How close are we to replacing Python’s re?", "title"),
        _text(56, 103,
              "Three independently built engines · compared with Python 3.14.6",
              "subtitle"),
    ]
    cards = (
        (54, "165", "original Python test methods"),
        (338, "152", "public compatibility records"),
        (622, "13", "waived CPython-private tests"),
        (906, "0", "qualified replacement engines"),
    )
    for x, count, label in cards:
        result.extend((
            f'<rect x="{x}" y="131" width="240" height="91" rx="13" '
            'fill="#ffffff" stroke="#dce5ef"/>',
            _text(x + 15, 171, count, "metric"),
            _text(x + 15, 198, label, "metric-label"),
        ))
    result.extend((
        _text(56, 261, "What is included in the Python baseline?", "heading"),
        '<rect x="54" y="278" width="1092" height="138" rx="12" '
        'fill="#ffffff" stroke="#dce5ef"/>',
        _text(72, 305,
              "165 original methods = 152 public compatibility records "
              "+ 13 private tests from 2 named classes.", "body"),
        _text(72, 331,
              "Public baseline: 151 passing methods + 1 genuine "
              "debug-build-only skip. No public test is waived.", "small"),
        _text(72, 356,
              "DebugTests: 4 tests of CPython’s private matching-opcode display.",
              "small"),
        _text(72, 381,
              "ImplementationTest: 9 private compiler, _sre, type-internal "
              "and deprecated implementation tests.", "small"),
    ))
    result.extend((
        _text(56, 453, "Original correctness checks", "heading"),
        _text(56, 474,
              "The same 223,198 initial cases for each engine · 49 categories",
              "small"),
    ))
    for index, label in enumerate(("Rust", "C", "Zig")):
        y = 489 + 43 * index
        result.extend((
            _text(65, y + 19, label, "strong"),
            f'<rect x="157" y="{y}" width="686" height="25" rx="7" '
            'fill="#17844e"/>',
            _text(859, y + 18, "223,198 / 223,198", "strong"),
            _text(1070, y + 18, "100%", "pass"),
        ))
    result.extend((
        _text(56, 647, "Deeper correctness checks", "heading"),
        _text(56, 668,
              "The same 393 difficult cases for every engine · 64 fixed-seed cases",
              "small"),
    ))
    for index, label in enumerate(("Rust", "C", "Zig")):
        y = 683 + 43 * index
        result.extend((
            _text(65, y + 19, label, "strong"),
            f'<rect x="157" y="{y}" width="686" height="25" rx="7" '
            'fill="#17844e"/>',
            _text(859, y + 18, "393 / 393", "strong"),
            _text(1070, y + 18, "100%", "pass"),
        ))
    result.extend((
        _text(56, 843, "What happened in the full public Python test?", "heading"),
        _text(56, 865,
              "Rust accounted for all 152 public test records and "
              "both sets of 304 engine guards.", "small"),
        '<rect x="54" y="878" width="1092" height="161" rx="12" '
        'fill="#ffffff" stroke="#dce5ef"/>',
        _text(72, 907, "Rust", "strong"),
        _text(142, 907, "NOT YET COMPATIBLE", "fail"),
    ))
    for x, count, label in (
        (77, "139", "genuinely passing methods"),
        (326, "11", "test-harness errors"),
        (585, "1", "real missing _compile"),
        (847, "1", "debug-only skip"),
    ):
        result.extend((_text(x, 954, count, "metric"),
                       _text(x, 978, label, "metric-label")))
    result.extend((
        _text(73, 1012,
              "139 passes + 11 harness errors + 1 real candidate error + "
              "1 debug-only skip = 152", "small"),
        _text(56, 1077, "Why the failures are different", "heading"),
        '<rect x="54" y="1090" width="1092" height="68" rx="10" '
        'fill="#fff8eb" stroke="#f2d199"/>',
        _text(72, 1116,
              "11 errors come from the test harness blocking Python’s "
              "own warning and assertion helpers.", "body"),
        _text(72, 1139,
              "They are not 11 demonstrated regex-engine mismatches.", "small"),
        '<rect x="54" y="1166" width="1092" height="69" rx="10" '
        'fill="#fff1f1" stroke="#ecc6c8"/>',
        _text(72, 1192,
              "1 real drop-in gap: Python’s pickling test cannot import "
              "Rust’s required _compile helper.", "body"),
        _text(72, 1215,
              "This genuine original-test incompatibility still needs a fix.",
              "small"),
    ))
    for index, row in enumerate(snapshot["full_python_suite"][1:]):
        x = 54 if index == 0 else 615
        result.extend((
            f'<rect x="{x}" y="1252" width="530" height="62" rx="10" '
            'fill="#f1f4f9" stroke="#d9e1ec"/>',
            _text(x + 16, 1277, row["label"], "strong"),
            _text(x + 90, 1277, "NOT RUN", "pending"),
            _text(x + 16, 1298,
                  "No result claimed for the 152 public Python records.", "small"),
        ))
    result.extend((
        _text(56, 1350, "All earlier test-setup failures remain preserved", "heading"),
        _text(57, 1372,
              "Missing bridge wiring · anti-delegation import guard · "
              "candidate-free correctness-controller guard", "small"),
        _text(57, 1393,
              "All three stopped before the first test; none is counted "
              "as a matching-engine mismatch.", "small"),
        '<rect x="54" y="1420" width="1092" height="90" rx="11" '
        'fill="#ffffff" stroke="#dce5ef"/>',
        _text(73, 1451,
              "Overall: no from-scratch engine has yet passed every "
              "required public Python test.", "footer"),
        _text(73, 1478,
              "Current speed and memory: NOT MEASURED · "
              "final holdout: NOT ACCESSED.", "small"),
        '</svg>\n',
    ))
    return "\n".join(result).encode("utf-8")


def _bundle() -> tuple[bytes, bytes, dict[str, Any]]:
    snapshot, identities = _snapshot()
    svg = render_svg(snapshot)
    manifest = {
        "schema": SCHEMA + "-manifest", "status": "PASS",
        "generator_path": SOURCE_PATH,
        "chart_path": CHART_PATH,
        "chart_sha256": hashlib.sha256(svg).hexdigest(),
        "chart_bytes": len(svg),
        "validated_input_count": len(identities),
        "validated_inputs": identities,
        "snapshot": snapshot,
        "production_observations_invented": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    return svg, canonical(manifest), manifest


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
                    "an existing V5 chart is not a genuine regular file")
            blocks: list[bytes] = []
            while True:
                part = os.read(descriptor, 1024 * 1024)
                if not part:
                    break
                blocks.append(part)
            require(b"".join(blocks) == payload,
                    "refusing to overwrite an actual different V5 result")
        finally:
            os.close(descriptor)
        return "EXISTING IDENTICAL"
    try:
        completed = 0
        while completed < len(payload):
            observed = os.write(descriptor, payload[completed:])
            require(type(observed) is int and observed > 0,
                    "a genuine V5 exclusive chart write failed")
            completed += observed
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.fsync(directory)
    return "EXCLUSIVELY CREATED"


def _write(svg: bytes, manifest: bytes) -> dict[str, str]:
    flags = (os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    root = os.open(str(ROOT), flags)
    docs = -1
    evidence = -1
    try:
        docs = os.open("docs", flags, dir_fd=root)
        evidence = os.open("evidence", flags, dir_fd=docs)
        return {
            "chart": _exclusive_publish("current-native-correctness-v5.svg",
                                         svg, evidence),
            "manifest": _exclusive_publish("current-native-correctness-v5.json",
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
    restore: list[tuple[Any, str, Any]] = []

    def deny(counter: str, reason: str) -> Callable[..., Any]:
        def rejected(*_args: Any, **_kwargs: Any) -> Any:
            effects[counter] += 1
            raise ChartError(reason)
        return rejected

    def patch(owner: Any, name: str, substitute: Any) -> None:
        if hasattr(owner, name):
            restore.append((owner, name, getattr(owner, name)))
            setattr(owner, name, substitute)

    stop_read = deny("blocked_file_reads", "source-only controls cannot read")
    stop_write = deny("blocked_file_writes", "source-only controls cannot write")
    stop_import = deny("blocked_candidate_imports", "source-only controls cannot import")
    stop_worker = deny("blocked_workers", "source-only controls cannot start workers")
    stop_thread = deny("blocked_threads", "source-only controls cannot start threads")
    stop_clock = deny("blocked_clock_samples", "source-only controls cannot measure")
    try:
        patch(builtins, "open", stop_read)
        patch(io, "open", stop_read)
        for name in ("open", "read_bytes", "read_text", "exists", "stat",
                     "is_file", "is_dir", "iterdir", "glob", "rglob"):
            patch(Path, name, stop_read)
        for name in ("open", "stat", "lstat", "scandir", "listdir"):
            patch(os, name, stop_read)
        for name in ("write", "fsync", "mkdir", "makedirs", "remove",
                     "unlink", "rename", "replace"):
            patch(os, name, stop_write)
        patch(Path, "write_bytes", stop_write)
        patch(Path, "write_text", stop_write)
        patch(subprocess, "run", stop_worker)
        patch(subprocess, "Popen", stop_worker)
        patch(os, "fork", stop_worker)
        patch(multiprocessing.Process, "start", stop_worker)
        patch(threading.Thread, "start", stop_thread)
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns"):
            patch(time, name, stop_clock)
        patch(importlib, "import_module", stop_import)
        patch(builtins, "__import__", stop_import)
        yield effects
    finally:
        for owner, name, saved in reversed(restore):
            setattr(owner, name, saved)


def _synthetic_snapshot() -> dict[str, Any]:
    rows = [
        {"family": family, "label": label, "kind": kind,
         "status": "PASS", "passed": count, "total": count,
         "mismatches": 0}
        for kind, count in (("original", 223_198), ("deeper", 393))
        for family, label in FAMILIES
    ]
    harness = [{
        "test": "synthetic_warning_" + str(number),
        "reason_sha256": hashlib.sha256(str(number).encode("ascii")).hexdigest(),
        "classification": "test-harness matcher-guard interference",
    } for number in range(11)]
    gaps = [{
        "test": PICKLING_METHOD,
        "reason_sha256": hashlib.sha256(PICKLING_ERROR.encode("ascii")).hexdigest(),
        "classification": "from-scratch Rust private pickle hook missing",
    }]
    debug = {
        "test": PRIVATE_DEBUG_METHOD,
        "reason": PRIVATE_DEBUG_REASON,
        "skip_kind": PRIVATE_DEBUG_SKIP_KIND,
        "source_ast_sha256": PRIVATE_DEBUG_SOURCE_AST_SHA256,
    }
    reference_roles = [{
        "role": name, "public_method_records": PUBLIC_METHODS,
        "passed": RUNNABLE_REFERENCE_METHODS,
        "named_private_debug_skips": 1,
        "debug_skip": copy.deepcopy(debug),
    } for name in ("reference_a", "reference_b")]
    scope = {
        "baseline": "CPython 3.14.6 re",
        "original_source_method_count": ALL_ORIGINAL_METHODS,
        "applicable_public_method_count": PUBLIC_METHODS,
        "named_private_class_waiver_count": PRIVATE_WAIVER_CLASSES,
        "named_private_method_waiver_count": PRIVATE_WAIVER_METHODS,
        "named_private_class_waivers": copy.deepcopy(NAMED_PRIVATE_CLASS_WAIVERS),
        "public_method_waivers": [],
        "independent_reference_count": 2,
        "reference_runnable_pass_count": RUNNABLE_REFERENCE_METHODS,
        "reference_named_private_debug_skip_count": 1,
        "reference_roles": reference_roles,
        "reference_status_vector_sha256": hashlib.sha256(
            b"synthetic-only-not-actual-reference"
        ).hexdigest(),
        "reference_path": REFERENCE_PATH,
        "reference_sha256": REFERENCE_SHA256,
        "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
    }
    rust = {
        "family": "rust", "label": "Rust", "status": "FAIL",
        "completed_methods": PUBLIC_METHODS, "total_methods": PUBLIC_METHODS,
        "passed_methods": 139, "error_methods": 12,
        "harness_interference_errors": 11,
        "genuine_candidate_errors": 1,
        "named_private_debug_skips": 1,
        "native_owner_guards": METHOD_GUARDS,
        "cached_matcher_guards": METHOD_GUARDS,
        "full_official_suite_qualified": False,
        "harness_interference_error_records": harness,
        "genuine_candidate_error_records": gaps,
        "genuine_candidate_error_test": PICKLING_METHOD,
        "genuine_candidate_error": PICKLING_ERROR,
    }
    pending = [{
        "family": family, "label": label, "status": "NOT RUN",
        "completed_methods": None, "total_methods": PUBLIC_METHODS,
        "native_owner_guards": None, "cached_matcher_guards": None,
        "full_official_suite_qualified": False,
    } for family, label in FAMILIES[1:]]
    return {
        "candidate_count": 3,
        "original_candidate_checks": 669_594,
        "deeper_candidate_checks": 1_179,
        "observed_original_or_deeper_mismatches": 0,
        "official_suite_candidate_passes": 0,
        "full_drop_in_compatibility": "NOT ESTABLISHED",
        "rows": rows,
        "original_python_test_scope": scope,
        "full_python_suite": [rust, *pending],
        "historical_v12_rust_upstream_failure": {
            "family": "rust", "status": "STOPPED BEFORE TESTS",
            "completed_methods": 0, "cause": "test-harness bridge wiring",
        },
        "historical_v13_rust_upstream_failure": {
            "family": "rust", "status": "FAIL", "completed_methods": 0,
            "native_owner_guards": 0,
            "actual_error": "stage-07 blocked unowned matching import: re",
        },
        "historical_v14_rust_upstream_failure": {
            "family": "rust", "status": "FAIL", "completed_methods": 0,
            "native_owner_guards": 0,
            "actual_error": "the V11 correctness controller must never import a candidate",
        },
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def _self_test() -> dict[str, Any]:
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "pure chart source controls may not import matching candidates")
    checks: list[dict[str, Any]] = []

    def accept(name: str, condition: Any) -> None:
        require(not any(row["name"] == name for row in checks),
                "a source-only poison control was counted twice")
        require(condition is True, "an actual source-only control failed: " + name)
        checks.append({"name": name, "kind": "accepted", "passed": True})

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(not any(row["name"] == name for row in checks),
                "a source-only rejection control was counted twice")
        try:
            action()
        except (ChartError, OSError, AssertionError, TypeError,
                ValueError, KeyError, ImportError):
            checks.append({"name": name, "kind": "rejected", "passed": True})
        else:
            raise ChartError("an unsafe synthetic chart was accepted: " + name)

    with _source_only_boundary() as effects:
        snapshot = _synthetic_snapshot()
        picture = render_svg(snapshot)
        accept("render-synthetic-only-scope", picture.startswith(b"<svg "))
        accept("render-exact-repeatable-svg",
               picture == render_svg(copy.deepcopy(snapshot)))
        accept("terminate-synthetic-svg", picture.endswith(b"</svg>\n"))
        accept("show-complete-original-source-denominator", b"165" in picture)
        accept("show-exact-applicable-public-denominator", b"152" in picture)
        accept("show-exact-thirteen-waived-private-test-methods",
               b"13 private tests from 2 named classes" in picture)
        accept("show-exactly-two-named-private-waiver-classes",
               b"2 named classes" in picture)
        accept("show-authentic-four-opcode-waivers", b"DebugTests: 4" in picture)
        accept("show-authentic-nine-internal-waivers",
               b"ImplementationTest: 9" in picture)
        accept("show-real-151-baseline-passes", b"151 passing methods" in picture)
        accept("show-genuine-debug-build-only-skip",
               b"debug-build-only skip" in picture)
        accept("show-zero-public-method-waivers",
               b"No public test is waived" in picture)
        accept("show-all-three-original-case-denominators",
               picture.count(b"223,198 / 223,198") == 3)
        accept("show-all-three-deep-case-denominators",
               picture.count(b"393 / 393") == 3)
        accept("show-real-139-passing-rust-methods", b"139" in picture)
        accept("show-eleven-authentic-harness-errors",
               b"test-harness errors" in picture)
        accept("show-one-genuine-missing-compile",
               b"real missing _compile" in picture)
        accept("show-exact-complete-152-method-equation",
               b"139 passes + 11 harness errors + 1 real candidate error" in picture)
        accept("show-both-unexecuted-independent-engines",
               picture.count(b">NOT RUN</text>") == 2)
        accept("show-real-missing-bridge-history", b"Missing bridge wiring" in picture)
        accept("show-real-import-guard-history",
               b"anti-delegation import guard" in picture)
        accept("show-real-isolated-controller-history",
               b"candidate-free correctness-controller guard" in picture)
        accept("show-speed-honestly-not-measured", b"NOT MEASURED" in picture)
        accept("keep-final-holdout-sealed", b"NOT ACCESSED" in picture)
        for key, value in (
            ("candidate_count", 2),
            ("original_candidate_checks", 669_593),
            ("deeper_candidate_checks", 1_178),
            ("observed_original_or_deeper_mismatches", 1),
            ("official_suite_candidate_passes", 1),
            ("full_drop_in_compatibility", "PASS"),
            ("performance", "1.5x"),
            ("holdout", "ACCESSED"),
        ):
            changed = copy.deepcopy(snapshot)
            changed[key] = value
            reject("reject-fabricated-overall:" + key,
                   lambda changed=changed: render_svg(changed))
        for index in range(6):
            for key, value in (
                ("status", "FAIL"),
                ("mismatches", 1),
                ("passed", snapshot["rows"][index]["total"] - 1),
            ):
                changed = copy.deepcopy(snapshot)
                changed["rows"][index][key] = value
                reject("reject-fabricated-original-or-deep:"
                       + str(index) + ":" + key,
                       lambda changed=changed: render_svg(changed))
        for key, value in (
            ("baseline", "invented baseline"),
            ("original_source_method_count", 164),
            ("original_source_method_count", 166),
            ("applicable_public_method_count", 151),
            ("applicable_public_method_count", 153),
            ("named_private_class_waiver_count", 1),
            ("named_private_class_waiver_count", 3),
            ("named_private_method_waiver_count", 12),
            ("named_private_method_waiver_count", 14),
            ("independent_reference_count", 1),
            ("reference_runnable_pass_count", 150),
            ("reference_runnable_pass_count", 152),
            ("reference_named_private_debug_skip_count", 0),
            ("reference_named_private_debug_skip_count", 2),
            ("reference_path", "unverified-reference.json"),
            ("reference_sha256", "a" * 64),
            ("public_method_matrix_sha256", "b" * 64),
        ):
            changed = copy.deepcopy(snapshot)
            changed["original_python_test_scope"][key] = value
            reject("reject-fabricated-original-suite-scope:" + key + ":" + str(value),
                   lambda changed=changed: render_svg(changed))
        changed = copy.deepcopy(snapshot)
        changed["original_python_test_scope"]["public_method_waivers"] = [
            {"test": "invented public waiver"}
        ]
        reject("reject-any-public-method-waiver",
               lambda: render_svg(changed))
        for class_name in ("DebugTests", "ImplementationTest"):
            for mutation in ("missing", "methods", "reason"):
                changed = copy.deepcopy(snapshot)
                waivers = changed["original_python_test_scope"][
                    "named_private_class_waivers"
                ]
                if mutation == "missing":
                    waivers.pop(class_name)
                elif mutation == "methods":
                    waivers[class_name]["methods"] += 1
                else:
                    waivers[class_name]["reason"] = "invented private waiver"
                reject("reject-forged-private-class:" + class_name + ":" + mutation,
                       lambda changed=changed: render_svg(changed))
        for index in (0, 1):
            for key, value in (
                ("role", "invented_reference"),
                ("public_method_records", 151),
                ("passed", 150),
                ("passed", 152),
                ("named_private_debug_skips", 0),
            ):
                changed = copy.deepcopy(snapshot)
                changed["original_python_test_scope"]["reference_roles"][index][key] = value
                reject("reject-forged-reference-role:"
                       + str(index) + ":" + key + ":" + str(value),
                       lambda changed=changed: render_svg(changed))
            for key, value in (
                ("test", "ReTests.test_invented_skip"),
                ("reason", "invented skip reason"),
                ("skip_kind", "invented skip classification"),
                ("source_ast_sha256", "a" * 64),
            ):
                changed = copy.deepcopy(snapshot)
                changed["original_python_test_scope"][
                    "reference_roles"
                ][index]["debug_skip"][key] = value
                reject("reject-forged-real-debug-skip:"
                       + str(index) + ":" + key,
                       lambda changed=changed: render_svg(changed))
        for key, value in (
            ("status", "PASS"),
            ("completed_methods", 151),
            ("total_methods", 165),
            ("passed_methods", 138),
            ("passed_methods", 140),
            ("passed_methods", 151),
            ("passed_methods", 152),
            ("error_methods", 11),
            ("error_methods", 13),
            ("harness_interference_errors", 10),
            ("harness_interference_errors", 12),
            ("genuine_candidate_errors", 0),
            ("genuine_candidate_errors", 2),
            ("named_private_debug_skips", 0),
            ("named_private_debug_skips", 2),
            ("native_owner_guards", 303),
            ("cached_matcher_guards", 303),
            ("full_official_suite_qualified", True),
            ("genuine_candidate_error_test", "ReTests.test_matching"),
            ("genuine_candidate_error", "invented matching failure"),
        ):
            changed = copy.deepcopy(snapshot)
            changed["full_python_suite"][0][key] = value
            reject("reject-fabricated-real-rust-result:" + key + ":" + str(value),
                   lambda changed=changed: render_svg(changed))
        for field in ("harness_interference_error_records",
                      "genuine_candidate_error_records"):
            changed = copy.deepcopy(snapshot)
            changed["full_python_suite"][0][field].pop()
            reject("reject-suppressed-real-error-classification:" + field,
                   lambda changed=changed: render_svg(changed))
        changed = copy.deepcopy(snapshot)
        changed["full_python_suite"][0]["harness_interference_error_records"][0][
            "classification"
        ] = "genuine candidate matching failure"
        reject("reject-mislabelled-test-harness-as-engine-failure",
               lambda: render_svg(changed))
        changed = copy.deepcopy(snapshot)
        changed["full_python_suite"][0]["genuine_candidate_error_records"][0][
            "test"
        ] = "ReTests.test_matching"
        reject("reject-concealed-real-private-pickle-hook",
               lambda: render_svg(changed))
        for index in (1, 2):
            for key, value in (
                ("status", "PASS"),
                ("completed_methods", PUBLIC_METHODS),
                ("native_owner_guards", METHOD_GUARDS),
                ("full_official_suite_qualified", True),
            ):
                changed = copy.deepcopy(snapshot)
                changed["full_python_suite"][index][key] = value
                reject("reject-invented-unrun-engine:"
                       + str(index) + ":" + key,
                       lambda changed=changed: render_svg(changed))
        for key in (
            "historical_v12_rust_upstream_failure",
            "historical_v13_rust_upstream_failure",
            "historical_v14_rust_upstream_failure",
        ):
            for field, value in (("status", "PASS"),
                                 ("completed_methods", PUBLIC_METHODS)):
                changed = copy.deepcopy(snapshot)
                changed[key][field] = value
                reject("reject-concealed-original-harness-failure:"
                       + key + ":" + field,
                       lambda changed=changed: render_svg(changed))
        reject("reject-builtin-actual-frozen-reference-read",
               lambda: builtins.open(REFERENCE_PATH, "rb"))
        reject("reject-descriptor-actual-frozen-v4-source-read",
               lambda: os.open(V4_SOURCE_PATH, os.O_RDONLY))
        reject("reject-path-actual-correctness-evidence-read",
               lambda: (ROOT / REFERENCE_PATH).read_bytes())
        reject("reject-actual-performance-or-holdout-inspection",
               lambda: (ROOT / "performance").exists())
        reject("reject-direct-candidate-import",
               lambda: importlib.import_module("candidates.rust_candidate"))
        reject("reject-builtin-cross-engine-candidate-import",
               lambda: builtins.__import__("candidates.zig_candidate"))
        reject("reject-original-upstream-worker",
               lambda: subprocess.run(["production-candidate-worker"]))
        reject("reject-unrequested-background-worker",
               lambda: threading.Thread(target=lambda: None).start())
        reject("reject-hidden-performance-clock", time.perf_counter)
        reject("reject-unauthorized-chart-publication",
               lambda: (ROOT / CHART_PATH).write_bytes(b"fabricated"))
        actual_effects = (
            "file_reads", "file_writes", "candidate_imports", "workers",
            "threads", "clock_samples", "holdout_cases_read",
            "performance_fixtures_read",
        )
        for effect in actual_effects:
            accept("perform-zero-actual-source-effects:" + effect,
                   effects[effect] == 0)
        for effect, minimum in (
            ("blocked_file_reads", 4),
            ("blocked_file_writes", 1),
            ("blocked_candidate_imports", 2),
            ("blocked_workers", 1),
            ("blocked_threads", 1),
            ("blocked_clock_samples", 1),
        ):
            accept("actually-enforce-source-boundary:" + effect,
                   effects[effect] >= minimum)
        require(len(checks) >= 100,
                "at least 100 individually genuine chart source controls are required")
        preserved_effects = dict(effects)
    accepted = sum(row["kind"] == "accepted" for row in checks)
    rejected = sum(row["kind"] == "rejected" for row in checks)
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "synthetic_only": True,
        "accepted_controls": accepted,
        "rejected_controls": rejected,
        "total_controls": len(checks),
        "actual_evidence_reads": 0,
        "actual_candidates_qualified": 0,
        "frozen_v4_source_sha256": V4_SOURCE_SHA256,
        "effects": preserved_effects,
        "production_observations_invented": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Visualize exact complete Python regex compatibility scope."
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--write", action="store_true")
    options = parser.parse_args(arguments)
    try:
        if options.self_test:
            result = _self_test()
        else:
            svg, raw_manifest, manifest = _bundle()
            if options.write:
                publication = _write(svg, raw_manifest)
            else:
                require(_read_regular(CHART_PATH) == svg
                        and _read_regular(MANIFEST_PATH) == raw_manifest,
                        "the V5 chart and manifest are not exactly reproducible")
                publication = {"chart": "VERIFIED", "manifest": "VERIFIED"}
            result = {
                "schema": SCHEMA + ("-write" if options.write else "-check"),
                "status": "PASS",
                "chart_path": CHART_PATH,
                "chart_sha256": manifest["chart_sha256"],
                "manifest_path": MANIFEST_PATH,
                "manifest_sha256": hashlib.sha256(raw_manifest).hexdigest(),
                "validated_input_count": manifest["validated_input_count"],
                "publication": publication,
                "performance": "NOT MEASURED",
                "holdout": "NOT ACCESSED",
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
