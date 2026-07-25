#!/usr/bin/env python3
"""Render complete, authenticated public results as plain-language charts.

This additive renderer never runs an engine, starts a benchmark, reads the
final holdout, or substitutes historical C or Zig measurements. Every result
is independently checked by the hash-pinned version-one evidence validator.
"""

from __future__ import annotations

import argparse
import builtins
import contextlib
from dataclasses import replace
import gc
import hashlib
import importlib
import io
import math
import os
from pathlib import Path
import stat
import subprocess
import sys
import threading
import time
import types
from typing import Any, Callable, Iterator, Mapping


ROOT = Path("/home/dev-user/src/rebar")
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
)
SOURCE_RELATIVE = "tools/render_rust_public_speed_v2.py"
LEGACY_RELATIVE = "tools/render_rust_public_speed_v1.py"
LEGACY_SHA256 = (
    "4a1a2e434d8d327471e7fe45c2e13e4c5248ba36956242f232fe4a3c03294db6"
)
LEGACY_MODULE = "tools._rebar_sha256_verified_public_speed_v1"
SCHEMA = "rebar-rust-public-practice-clear-speed-render-v2"
PUBLIC_LABEL = "PUBLIC DEVELOPMENT ONLY · FINAL HOLDOUT NOT OPENED"
OVERALL_RELATIVE = "docs/evidence/rust-public-speed-v2-overall.svg"
OUTCOMES_RELATIVE = "docs/evidence/rust-public-speed-v2-outcomes.svg"
OPERATIONS_RELATIVE = "docs/evidence/rust-public-speed-v2-operations.svg"
REGRESSIONS_RELATIVE = "docs/evidence/rust-public-speed-v2-regressions.svg"
MANIFEST_RELATIVE = "docs/evidence/rust-public-speed-v2.json"
APPROVED_OUTPUTS = (
    OVERALL_RELATIVE,
    OUTCOMES_RELATIVE,
    OPERATIONS_RELATIVE,
    REGRESSIONS_RELATIVE,
    MANIFEST_RELATIVE,
)
MAX_SOURCE_BYTES = 4 * 1024 * 1024
MAX_EVIDENCE_BYTES = 32 * 1024 * 1024
_LEGACY: types.ModuleType | None = None


class ClearRenderError(Exception):
    """Reject incomplete evidence, false speed, and unsafe publication."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ClearRenderError(message)


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and bool(sys.path)
        and sys.path[0] == str(ROOT)
        and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
        and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
        "use only isolated, pinned, no-bytecode CPython 3.14.6",
    )
    require(
        not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "a graph renderer must never load a matching engine",
    )


def _parts(relative: Any, *, source: bool = False) -> tuple[str, ...]:
    require(type(relative) is str, "an exact approved relative path is required")
    if source:
        require(relative == LEGACY_RELATIVE, "only frozen V1 source can be read")
    else:
        require(
            relative in APPROVED_OUTPUTS,
            "publish or check only the five new V2 graph artifacts",
        )
    parts = tuple(relative.split("/"))
    require(
        all(component not in ("", ".", "..") for component in parts)
        and "\\" not in relative
        and "\x00" not in relative,
        "an approved graph path must remain canonical and inside the repository",
    )
    return parts


def _directory_flags() -> int:
    return (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )


@contextlib.contextmanager
def owned_parent(
    relative: str, *, source: bool = False,
) -> Iterator[tuple[int, str]]:
    parts = _parts(relative, source=source)
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), _directory_flags())
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode), "invalid repository root")
        for component in parts[:-1]:
            following = os.open(component, _directory_flags(), dir_fd=current)
            opened.append(following)
            require(
                stat.S_ISDIR(os.fstat(following).st_mode),
                "a graph directory is not an owned, non-symlink directory",
            )
            current = following
        yield current, parts[-1]
    finally:
        errors: list[Exception] = []
        for descriptor in reversed(opened):
            try:
                os.close(descriptor)
            except Exception as error:
                errors.append(error)
        if errors and sys.exc_info()[1] is None:
            raise ClearRenderError("an owned graph descriptor did not close") from errors[0]


def read_owned_regular(
    relative: str,
    expected_sha256: str,
    maximum: int,
    *,
    source: bool = False,
) -> bytes:
    require(
        type(expected_sha256) is str
        and len(expected_sha256) == 64
        and all(character in "0123456789abcdef" for character in expected_sha256),
        "an independent lowercase SHA-256 fingerprint is mandatory",
    )
    require(
        type(maximum) is int and 0 < maximum <= MAX_EVIDENCE_BYTES,
        "a complete bounded graph artifact is mandatory",
    )
    with owned_parent(relative, source=source) as (directory, basename):
        descriptor = os.open(
            basename,
            os.O_RDONLY
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=directory,
        )
        try:
            original = os.fstat(descriptor)
            named = os.stat(basename, dir_fd=directory, follow_symlinks=False)
            require(
                stat.S_ISREG(original.st_mode)
                and stat.S_ISREG(named.st_mode)
                and (original.st_dev, original.st_ino)
                == (named.st_dev, named.st_ino)
                and 0 < original.st_size <= maximum,
                "a graph source or artifact must be a bounded owned regular file",
            )
            remaining = original.st_size
            chunks: list[bytes] = []
            while remaining:
                part = os.read(descriptor, min(remaining, 1_048_576))
                require(type(part) is bytes and bool(part), "truncated graph artifact")
                chunks.append(part)
                remaining -= len(part)
            require(os.read(descriptor, 1) == b"", "unexpected graph artifact suffix")
            final = os.fstat(descriptor)
            require(
                (final.st_dev, final.st_ino, final.st_size)
                == (original.st_dev, original.st_ino, original.st_size),
                "a graph artifact changed during complete authentication",
            )
        finally:
            os.close(descriptor)
    payload = b"".join(chunks)
    require(
        hashlib.sha256(payload).hexdigest() == expected_sha256,
        "an externally pinned graph artifact changed: " + relative,
    )
    return payload


def verified_legacy() -> types.ModuleType:
    global _LEGACY
    verify_runtime()
    if _LEGACY is not None:
        require(
            _LEGACY is sys.modules.get(LEGACY_MODULE)
            and getattr(_LEGACY, "__file__", None) == str(ROOT / LEGACY_RELATIVE),
            "the independently verified original validator was replaced",
        )
        return _LEGACY
    require(LEGACY_MODULE not in sys.modules, "the validator module was preloaded")
    payload = read_owned_regular(
        LEGACY_RELATIVE, LEGACY_SHA256, MAX_SOURCE_BYTES, source=True,
    )
    module = types.ModuleType(LEGACY_MODULE)
    module.__file__ = str(ROOT / LEGACY_RELATIVE)
    module.__package__ = "tools"
    sys.modules[LEGACY_MODULE] = module
    try:
        exec(compile(payload, module.__file__, "exec"), module.__dict__)
        require(
            module.SOURCE_RELATIVE == LEGACY_RELATIVE
            and module.PUBLIC_CASE_COUNT == 864
            and module.PAIRED_TRIALS == 12
            and len(module.OPERATIONS) == 36,
            "the independently frozen complete public validator changed",
        )
        module.verify_runtime()
    except BaseException:
        sys.modules.pop(LEGACY_MODULE, None)
        raise
    _LEGACY = module
    return module


def _xml(value: Any) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _number(value: Any, places: int = 3) -> str:
    require(
        type(value) in (float, int) and math.isfinite(value),
        "a graph cannot display an invented or nonfinite speed",
    )
    return format(value, "." + str(places) + "f")


def _frame(key: str, title: str, description: str, height: int) -> list[str]:
    require(key in ("overall", "outcomes", "operations", "regressions"), "bad graph")
    return [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1120" '
        f'height="{height}" viewBox="0 0 1120 {height}" role="img" '
        f'aria-labelledby="speed-v2-{key}-title speed-v2-{key}-description">',
        f'<title id="speed-v2-{key}-title">{_xml(title)}</title>',
        f'<desc id="speed-v2-{key}-description">{_xml(description)}</desc>',
        '<rect width="100%" height="100%" rx="18" fill="#f8fafc"/>',
        '<g font-family="system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif">',
        f'<text x="40" y="47" fill="#0f172a" font-size="24" '
        f'font-weight="750">{_xml(title)}</text>',
        f'<text x="40" y="74" fill="#475569" font-size="13">'
        f'{_xml(PUBLIC_LABEL)}</text>',
    ]


def _finish(lines: list[str], height: int) -> bytes:
    lines.extend([
        f'<line x1="40" x2="1080" y1="{height - 46}" '
        f'y2="{height - 46}" stroke="#cbd5e1"/>',
        f'<text x="40" y="{height - 22}" fill="#475569" font-size="12">'
        "Python 3.14.6 · 864 public examples · 12 paired rounds · "
        "full Python-call and correctness-check costs included · "
        "final speed and native memory NOT MEASURED</text>",
        "</g>",
        "</svg>",
    ])
    return ("\n".join(lines) + "\n").encode("utf-8")


def render_overall(results: Mapping[str, Any]) -> bytes:
    ratio = results["weighted_geomean_speedup_vs_baseline"]
    interval = results["overall_speedup_confidence_interval"]
    require(
        type(ratio) in (float, int)
        and type(interval) is dict
        and interval.get("confidence_level") == 0.95
        and 0 < interval.get("lower", 0) <= ratio <= interval.get("upper", 0),
        "the complete measured overall speed and genuine 95% interval are required",
    )
    scale = max(1.65, ratio, interval["upper"])
    origin, width = 285, 650
    target = origin + int(width * 1.5 / scale)
    same = origin + int(width / scale)
    lines = _frame(
        "overall",
        "How fast are the replacements compared with Python?",
        "The authenticated measured Rust build is compared against Python "
        "using every public example and its complete 95 percent interval. "
        "The current C and Zig builds are explicitly not measured. "
        "Higher numbers are faster; 1.5 times is the predeclared goal.",
        420,
    )
    lines.extend([
        '<text x="42" y="103" fill="#334155" font-size="13">'
        "1.0× means the same speed as Python; higher is faster.</text>",
        '<rect x="32" y="118" width="1056" height="221" rx="13" fill="#ffffff"/>',
        f'<line x1="{same}" x2="{same}" y1="130" y2="322" '
        'stroke="#64748b" stroke-dasharray="4 4"/>',
        f'<line x1="{target}" x2="{target}" y1="130" y2="322" '
        'stroke="#7c3aed" stroke-width="2" stroke-dasharray="5 4"/>',
        f'<text x="{target + 7}" y="144" fill="#6d28d9" '
        'font-size="12" font-weight="700">1.5× goal</text>',
        '<text x="48" y="175" fill="#0f172a" font-size="15" '
        'font-weight="650">Python baseline</text>',
        f'<rect x="{origin}" y="156" width="{int(width / scale)}" '
        'height="23" rx="6" fill="#475569"/>',
        '<text x="1066" y="174" text-anchor="end" fill="#334155" '
        'font-size="15" font-weight="700">1.000×</text>',
        '<text x="48" y="225" fill="#0f172a" font-size="14" '
        'font-weight="700">Measured from-scratch Rust</text>',
        f'<rect x="{origin}" y="206" width="{int(width * ratio / scale)}" '
        'height="23" rx="6" fill="#047857"/>',
        f'<line x1="{origin + int(width * interval["lower"] / scale)}" '
        f'x2="{origin + int(width * interval["upper"] / scale)}" '
        'y1="238" y2="238" stroke="#064e3b" stroke-width="3"/>',
        f'<text x="1066" y="218" text-anchor="end" fill="#065f46" '
        f'font-size="14" font-weight="750">{_number(ratio)}×</text>',
        f'<text x="1066" y="238" text-anchor="end" fill="#475569" '
        f'font-size="11">95%: {_number(interval["lower"])}–'
        f'{_number(interval["upper"])}×</text>',
        '<text x="48" y="275" fill="#334155" font-size="14" '
        'font-weight="650">Current from-scratch C</text>',
        f'<rect x="{origin}" y="256" width="{width}" height="23" '
        'rx="6" fill="#f1f5f9" stroke="#cbd5e1" stroke-dasharray="5 4"/>',
        '<text x="1066" y="274" text-anchor="end" fill="#475569" '
        'font-size="13" font-weight="700">NOT MEASURED</text>',
        '<text x="48" y="316" fill="#334155" font-size="14" '
        'font-weight="650">Current from-scratch Zig</text>',
        f'<rect x="{origin}" y="297" width="{width}" height="23" '
        'rx="6" fill="#f1f5f9" stroke="#cbd5e1" stroke-dasharray="5 4"/>',
        '<text x="1066" y="315" text-anchor="end" fill="#475569" '
        'font-size="13" font-weight="700">NOT MEASURED</text>',
    ])
    return _finish(lines, 420)


def render_outcomes(results: Mapping[str, Any]) -> bytes:
    total = results["case_denominator"]
    faster = results["statistically_faster_case_count"]
    slower = results["statistically_slower_case_count"]
    uncertain = total - faster - slower
    require(
        type(total) is int
        and total == 864
        and all(type(value) is int and value >= 0 for value in (faster, slower, uncertain))
        and faster + uncertain + slower == total,
        "every faster, inconclusive and slower public example must remain visible",
    )
    origin, width = 50, 1018
    green = width * faster // total
    amber = width * uncertain // total
    red = width - green - amber
    minimum = math.ceil(total * 0.6)
    goal = origin + round(width * 0.6)
    lines = _frame(
        "outcomes",
        "How often is Rust convincingly faster?",
        "Every public case is classified using its complete paired 95 percent "
        "confidence interval. Faster, inconclusive, and slower examples add "
        "to the unchanged denominator. The goal is at least 60 percent.",
        312,
    )
    lines.extend([
        '<rect x="34" y="100" width="1052" height="137" rx="13" fill="#ffffff"/>',
        f'<rect x="{origin}" y="126" width="{green}" height="31" fill="#047857"/>',
        f'<rect x="{origin + green}" y="126" width="{amber}" '
        'height="31" fill="#d97706"/>',
        f'<rect x="{origin + green + amber}" y="126" width="{red}" '
        'height="31" fill="#be123c"/>',
        f'<line x1="{goal}" x2="{goal}" y1="115" y2="167" '
        'stroke="#6d28d9" stroke-width="3"/>',
        f'<text x="{goal + 8}" y="181" fill="#6d28d9" font-size="12" '
        f'font-weight="700">60% goal · at least {minimum} of {total}</text>',
        '<circle cx="56" cy="210" r="6" fill="#047857"/>',
        f'<text x="71" y="214" fill="#14532d" font-size="13">'
        f'Faster: {faster} / {total} ({100 * faster / total:.1f}%)</text>',
        '<circle cx="363" cy="210" r="6" fill="#d97706"/>',
        f'<text x="378" y="214" fill="#78350f" font-size="13">'
        f'Inconclusive: {uncertain} / {total}</text>',
        '<circle cx="740" cy="210" r="6" fill="#be123c"/>',
        f'<text x="755" y="214" fill="#881337" font-size="13">'
        f'Slower: {slower} / {total}</text>',
    ])
    return _finish(lines, 312)


def render_operations(
    operations: list[dict[str, Any]], legacy: types.ModuleType,
) -> bytes:
    require(
        type(operations) is list
        and len(operations) == 36
        and [row.get("operation") for row in operations] == list(legacy.OPERATIONS)
        and all(row.get("case_denominator") == 24 for row in operations),
        "show all 36 original operations and all 24 examples in each",
    )
    ratios = [row["speedup_vs_baseline"] for row in operations]
    require(
        all(type(value) in (float, int) and math.isfinite(value) and value > 0 for value in ratios),
        "every displayed operation must have an actual finite measured speed",
    )
    origin, width = 355, 600
    scale = max(1.65, *ratios)
    height = 180 + 31 * len(operations)
    baseline = origin + int(width / scale)
    goal = origin + int(width * 1.5 / scale)
    lines = _frame(
        "operations",
        "Every kind of regular-expression work",
        "All 36 frozen Python operations are displayed in original order, "
        "with all 24 public examples per operation. Higher is faster; "
        "the vertical lines show Python and the 1.5-times target.",
        height,
    )
    lines.extend([
        '<text x="42" y="102" fill="#475569" font-size="12">'
        "Every row includes all 24 examples; no slow operation is hidden.</text>",
        f'<line x1="{baseline}" x2="{baseline}" y1="113" '
        f'y2="{116 + 31 * len(operations)}" stroke="#64748b" '
        'stroke-dasharray="4 4"/>',
        f'<line x1="{goal}" x2="{goal}" y1="113" '
        f'y2="{116 + 31 * len(operations)}" stroke="#7c3aed" '
        'stroke-dasharray="5 4"/>',
    ])
    for index, row in enumerate(operations):
        y = 121 + 31 * index
        ratio = ratios[index]
        color = "#047857" if ratio >= 1.0 else "#be123c"
        lines.extend([
            f'<text x="43" y="{y + 12}" fill="#334155" '
            f'font-size="11">{_xml(row["operation"])}</text>',
            f'<rect x="{origin}" y="{y}" width="{width}" height="15" '
            'rx="5" fill="#e2e8f0"/>',
            f'<rect x="{origin}" y="{y}" '
            f'width="{int(width * ratio / scale)}" height="15" '
            f'rx="5" fill="{color}"/>',
            f'<text x="1080" y="{y + 12}" text-anchor="end" '
            f'fill="{color}" font-size="11" font-weight="650">'
            f'{_number(ratio)}× · 24 examples</text>',
        ])
    return _finish(lines, height)


def render_regressions(results: Mapping[str, Any]) -> bytes:
    rows = results["all_regressions_over_20_percent"]
    count = results["regression_over_20_percent_count"]
    require(
        type(rows) is list
        and type(count) is int
        and count >= 0
        and len(rows) == count
        and all(
            type(row) is dict
            and row.get("regression_exceeds_20_percent") is True
            and type(row.get("rust_change_percent")) in (float, int)
            and math.isfinite(row["rust_change_percent"])
            and row["rust_change_percent"] > 20.0
            for row in rows
        ),
        "every actual slowdown greater than 20 percent must be retained",
    )
    ordered = sorted(rows, key=lambda row: (-row["rust_change_percent"], row["case"]))
    height = 230 + 34 * len(ordered)
    lines = _frame(
        "regressions",
        "Every example more than 20% slower than Python",
        "Every authenticated public regression above the predeclared "
        "20 percent threshold is shown. An empty list is shown as zero, "
        "not omitted or replaced with old measurements.",
        height,
    )
    if not ordered:
        lines.extend([
            '<rect x="34" y="104" width="1052" height="68" rx="12" '
            'fill="#ecfdf5"/>',
            '<text x="52" y="145" fill="#065f46" font-size="17" '
            'font-weight="700">0 of 864 public examples are more than '
            "20% slower.</text>",
        ])
    else:
        maximum = max(row["rust_change_percent"] for row in ordered)
        for index, row in enumerate(ordered):
            y = 111 + index * 34
            percent = row["rust_change_percent"]
            lines.extend([
                f'<text x="45" y="{y + 12}" fill="#334155" font-size="10">'
                f'{_xml(row["case"])} · {_xml(row["operation"])}</text>',
                f'<rect x="480" y="{y}" '
                f'width="{int(410 * percent / maximum)}" '
                'height="15" rx="5" fill="#be123c"/>',
                f'<text x="1077" y="{y + 12}" text-anchor="end" '
                f'fill="#881337" font-size="11" font-weight="650">'
                f'+{_number(percent, 1)}%</text>',
            ])
    return _finish(lines, height)


def build_manifest(
    legacy: types.ModuleType,
    pins: Any,
    report: Mapping[str, Any],
    results: Mapping[str, Any],
    operations: list[dict[str, Any]],
    charts: Mapping[str, bytes],
) -> dict[str, Any]:
    require(
        set(charts)
        == {
            OVERALL_RELATIVE,
            OUTCOMES_RELATIVE,
            OPERATIONS_RELATIVE,
            REGRESSIONS_RELATIVE,
        },
        "exactly four new versioned, complete charts are required",
    )
    faster = results["statistically_faster_case_count"]
    slower = results["statistically_slower_case_count"]
    total = results["case_denominator"]
    require(total == 864 and len(operations) == 36, "incomplete public evidence")
    return {
        "schema": SCHEMA + "-manifest",
        "status": "PASS",
        "chart_label": PUBLIC_LABEL,
        "practice_label": legacy.PRACTICE_LABEL,
        "python": "3.14.6",
        "legacy_validator_relative": LEGACY_RELATIVE,
        "legacy_validator_sha256": LEGACY_SHA256,
        "checker_source_relative": legacy.CHECKER_RELATIVE,
        "checker_source_sha256": pins.checker,
        "correctness_renderer_relative": legacy.CORRECTNESS_RENDERER_RELATIVE,
        "correctness_renderer_sha256": pins.correctness_renderer,
        "correctness_recorder_sha256": pins.correctness_recorder,
        "public_report_relative": pins.report_relative,
        "public_report_sha256": pins.report,
        "correctness_receipt_relative": pins.correctness_receipt_relative,
        "correctness_receipt_sha256": pins.correctness_receipt,
        "candidate_source_relative": legacy.CANDIDATE_SOURCE_RELATIVE,
        "candidate_source_sha256": pins.candidate,
        "native_engine_relative": legacy.NATIVE_ENGINE_RELATIVE,
        "native_engine_sha256": pins.native_engine,
        "native_bridge_relative": legacy.NATIVE_BRIDGE_RELATIVE,
        "native_bridge_sha256": pins.native_bridge,
        "public_matrix_sha256": pins.matrix,
        "baseline_records_sha256": pins.baseline,
        "case_denominator": total,
        "paired_trials_per_case": legacy.PAIRED_TRIALS,
        "total_complete_paired_rows": total * legacy.PAIRED_TRIALS,
        "raw_paired_rows_sha256": report["raw_paired_rows_sha256"],
        "weight_policy": results["weight_policy"],
        "point_estimator": results["point_estimator"],
        "timed_interval": results["timed_interval"],
        "overall_speedup_vs_python": results["weighted_geomean_speedup_vs_baseline"],
        "overall_95_percent_confidence_interval": results[
            "overall_speedup_confidence_interval"
        ],
        "statistically_faster_case_count": faster,
        "uncertain_case_count": total - faster - slower,
        "statistically_slower_case_count": slower,
        "faster_case_goal_fraction": 0.6,
        "faster_case_goal_minimum": math.ceil(total * 0.6),
        "overall_speedup_goal": 1.5,
        "regression_over_20_percent_count": results[
            "regression_over_20_percent_count"
        ],
        "all_regressions_over_20_percent": results[
            "all_regressions_over_20_percent"
        ],
        "all_case_results": results["all_case_results"],
        "all_operation_results": operations,
        "candidate_rows": [
            {"name": "Python baseline", "status": "MEASURED", "speedup": 1.0},
            {
                "name": "Measured from-scratch Rust build",
                "status": "MEASURED",
                "speedup": results["weighted_geomean_speedup_vs_baseline"],
                "native_engine_sha256": pins.native_engine,
                "native_bridge_sha256": pins.native_bridge,
                "candidate_source_sha256": pins.candidate,
            },
            {"name": "Current from-scratch C", "status": "NOT MEASURED"},
            {"name": "Current from-scratch Zig", "status": "NOT MEASURED"},
        ],
        "charts": [
            {
                "path": relative,
                "sha256": hashlib.sha256(charts[relative]).hexdigest(),
                "bytes": len(charts[relative]),
            }
            for relative in APPROVED_OUTPUTS[:-1]
        ],
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "native_memory": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def render_actual(pins: Any) -> tuple[dict[str, bytes], bytes, dict[str, Any]]:
    legacy = verified_legacy()
    _, _, matrix = legacy.authenticate_frozen_sources(pins)
    raw = legacy.read_owned_regular(
        pins.report_relative, pins.report, legacy.MAX_EVIDENCE_BYTES,
    )
    receipt_raw = legacy.read_owned_regular(
        pins.correctness_receipt_relative,
        pins.correctness_receipt,
        legacy.MAX_EVIDENCE_BYTES,
    )
    report = legacy.decode_canonical(raw, "complete current public speed report")
    receipt = legacy.decode_canonical(
        receipt_raw, "independently durable current public correctness receipt",
    )
    results, operations = legacy.validate_public_report(
        report, raw, receipt, receipt_raw, matrix, pins,
    )
    charts = {
        OVERALL_RELATIVE: render_overall(results),
        OUTCOMES_RELATIVE: render_outcomes(results),
        OPERATIONS_RELATIVE: render_operations(operations, legacy),
        REGRESSIONS_RELATIVE: render_regressions(results),
    }
    manifest = build_manifest(legacy, pins, report, results, operations, charts)
    verify_runtime()
    return charts, legacy.canonical(manifest), manifest


def write_atomic(relative: str, payload: bytes) -> dict[str, Any]:
    require(
        relative in APPROVED_OUTPUTS
        and type(payload) is bytes
        and 0 < len(payload) <= MAX_EVIDENCE_BYTES,
        "only one complete, bounded V2 graph or manifest can be published",
    )
    with owned_parent(relative) as (directory, basename):
        try:
            previous = os.stat(basename, dir_fd=directory, follow_symlinks=False)
        except FileNotFoundError:
            previous = None
        if previous is not None:
            require(
                stat.S_ISREG(previous.st_mode),
                "refusing to overwrite a non-regular or symlinked V2 destination",
            )
        temporary = "." + basename + ".rust-public-speed-v2-" + str(os.getpid())
        flags = (
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0)
        )
        descriptor: int | None = None
        original: os.stat_result | None = None
        published = False
        try:
            descriptor = os.open(temporary, flags, 0o644, dir_fd=directory)
            original = os.fstat(descriptor)
            require(stat.S_ISREG(original.st_mode), "unsafe V2 temporary inode")
            require(os.write(descriptor, payload) == len(payload), "short graph write")
            os.fsync(descriptor)
            os.close(descriptor)
            descriptor = None
            os.replace(
                temporary, basename, src_dir_fd=directory, dst_dir_fd=directory,
            )
            published = True
            os.fsync(directory)
        finally:
            if descriptor is not None:
                os.close(descriptor)
            if not published and original is not None:
                try:
                    actual = os.stat(
                        temporary, dir_fd=directory, follow_symlinks=False,
                    )
                except FileNotFoundError:
                    actual = None
                if actual is not None:
                    require(
                        stat.S_ISREG(actual.st_mode)
                        and (actual.st_dev, actual.st_ino)
                        == (original.st_dev, original.st_ino),
                        "refusing to remove a foreign graph temporary",
                    )
                    os.unlink(temporary, dir_fd=directory)
                    os.fsync(directory)
    return {
        "path": relative,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "actual_write_calls": 1,
        "file_fsync_completed": True,
        "directory_fsync_completed": True,
    }


def source_self_test() -> dict[str, Any]:
    legacy = verified_legacy()
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(
            type(name) is str and name not in accepted and bool(condition),
            "a synthetic V2 graph control failed: " + name,
        )
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(name not in rejected, "duplicate synthetic rejection: " + name)
        try:
            action()
        except (
            ClearRenderError,
            legacy.RenderError,
            ValueError,
            TypeError,
            KeyError,
            OSError,
        ):
            rejected.append(name)
            return
        raise ClearRenderError("a forged graph was accepted: " + name)

    with legacy.source_only_boundary() as effects:
        report, receipt, raw, receipt_raw, matrix, pins, expected = (
            legacy._synthetic_documents()
        )
        results, operations = legacy.validate_public_report(
            report,
            raw,
            receipt,
            receipt_raw,
            matrix,
            pins,
            expected_results=expected,
        )
        charts = {
            OVERALL_RELATIVE: render_overall(results),
            OUTCOMES_RELATIVE: render_outcomes(results),
            OPERATIONS_RELATIVE: render_operations(operations, legacy),
            REGRESSIONS_RELATIVE: render_regressions(results),
        }
        manifest = build_manifest(legacy, pins, report, results, operations, charts)
        accept("complete-864-case-synthetic-evidence", len(matrix) == 864)
        accept("all-10368-paired-observations", len(report["raw_paired_rows"]) == 10368)
        accept("all-36-operations-and-24-cases-each", len(operations) == 36)
        accept("all-four-accessible-versioned-graphs", all(
            payload.startswith(b"<svg ")
            and b'role="img"' in payload
            and PUBLIC_LABEL.encode("utf-8") in payload
            for payload in charts.values()
        ))
        accept("visible-predeclared-speed-goal", b"1.5" in charts[OVERALL_RELATIVE])
        accept("visible-exact-519-example-goal", b"519" in charts[OUTCOMES_RELATIVE])
        accept("current-c-and-zig-not-measured", charts[OVERALL_RELATIVE].count(
            b"NOT MEASURED",
        ) >= 2)
        accept("all-candidates-visible-with-honest-status", len(
            manifest["candidate_rows"],
        ) == 4 and [row["status"] for row in manifest["candidate_rows"]]
            == ["MEASURED", "MEASURED", "NOT MEASURED", "NOT MEASURED"])
        accept("all-case-denominators-preserved", (
            manifest["statistically_faster_case_count"]
            + manifest["uncertain_case_count"]
            + manifest["statistically_slower_case_count"]
            == 864
        ))
        accept("all-regressions-retained", manifest[
            "all_regressions_over_20_percent"
        ] == results["all_regressions_over_20_percent"])
        accept("all-source-native-and-receipt-pins-retained", (
            manifest["candidate_source_sha256"] == pins.candidate
            and manifest["native_engine_sha256"] == pins.native_engine
            and manifest["native_bridge_sha256"] == pins.native_bridge
            and manifest["correctness_receipt_sha256"] == pins.correctness_receipt
        ))
        accept("final-and-native-memory-not-measured", (
            manifest["native_memory"] == "NOT MEASURED"
            and manifest["hidden_cases_read"] == 0
            and manifest["final_winner_selected"] is False
        ))

        for index, key in enumerate(sorted(legacy.REPORT_FIELDS)):
            changed = dict(report)
            changed.pop(key)
            changed_raw = legacy.canonical(changed)
            changed_pins = replace(
                pins, report=hashlib.sha256(changed_raw).hexdigest(),
            )
            reject(
                "reject-missing-authenticated-report-field-" + format(index, "02d"),
                lambda changed=changed, changed_raw=changed_raw,
                changed_pins=changed_pins: legacy.validate_public_report(
                    changed,
                    changed_raw,
                    receipt,
                    receipt_raw,
                    matrix,
                    changed_pins,
                    expected_results=expected,
                ),
            )

        for index, key in enumerate(sorted(legacy.RECEIPT_FIELDS)):
            changed = dict(receipt)
            changed.pop(key)
            changed_raw = legacy.canonical(changed)
            changed_pins = replace(
                pins,
                correctness_receipt=hashlib.sha256(changed_raw).hexdigest(),
            )
            reject(
                "reject-missing-durable-correctness-field-" + format(index, "02d"),
                lambda changed=changed, changed_raw=changed_raw,
                changed_pins=changed_pins: legacy.validate_public_report(
                    report,
                    raw,
                    changed,
                    changed_raw,
                    matrix,
                    changed_pins,
                    expected_results=expected,
                ),
            )

        for name, action in (
            ("reject-historical-v1-overwrite", lambda: _parts(
                "docs/evidence/rust-public-speed-v1-overall.svg",
            )),
            ("reject-hidden-or-performance-path", lambda: _parts(
                "performance/hidden.json",
            )),
            ("reject-parent-escaping-path", lambda: _parts(
                "docs/evidence/../unapproved.svg",
            )),
            ("reject-non-v1-source", lambda: _parts(
                "tools/rust_public_practice_benchmark_v1.py", source=True,
            )),
            ("block-actual-report-read", lambda: builtins.open(
                pins.report_relative, "rb",
            )),
            ("block-actual-receipt-read", lambda: io.open(
                pins.correctness_receipt_relative, "rb",
            )),
            ("block-actual-owned-file-open", lambda: os.open(
                pins.report_relative, os.O_RDONLY,
            )),
            ("block-actual-chart-write", lambda: os.write(1, b"forbidden")),
            ("block-actual-chart-replacement", lambda: os.replace(
                OVERALL_RELATIVE, OUTCOMES_RELATIVE,
            )),
            ("block-actual-candidate-import", lambda: importlib.import_module(
                "candidates.rust_candidate",
            )),
            ("block-actual-reference-process", lambda: subprocess.Popen(
                [str(PINNED_PYTHON)],
            )),
            ("block-actual-background-thread", lambda: threading.Thread(
                target=lambda: None,
            ).start()),
            ("block-actual-performance-clock", lambda: time.perf_counter()),
            ("block-actual-garbage-collection", lambda: gc.collect()),
        ):
            reject(name, action)

        accept("no-actual-source-test-external-effects", all(
            effects[key] == 0
            for key in (
                "file_reads",
                "file_writes",
                "candidate_imports",
                "reference_imports",
                "workers_started",
                "threads_started",
                "clock_samples",
                "gc_collections",
                "hidden_cases_read",
                "performance_files_read",
            )
        ))
        accept("all-seven-real-effects-intercepted", all(
            effects[key] > 0
            for key in (
                "blocked_reads",
                "blocked_writes",
                "blocked_imports",
                "blocked_workers",
                "blocked_threads",
                "blocked_clocks",
                "blocked_gc_collections",
            )
        ))
        accept("at-least-30-independent-poison-controls", len(rejected) >= 30)

    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "legacy_validator_source_sha256": LEGACY_SHA256,
        "case_denominator": 864,
        "operation_count": 36,
        "paired_trials_per_case": 12,
        "total_complete_paired_rows": 10368,
        "accepted_control_count": len(accepted),
        "rejected_control_count": len(rejected),
        "accepted_controls": accepted,
        "rejected_controls": rejected,
        "effects": effects,
        "actual_candidate_workers": 0,
        "candidate_import_count": 0,
        "actual_clock_samples": 0,
        "timing_trials_run": 0,
        "hidden_cases_read": 0,
        "performance_files_read": 0,
        "files_written": 0,
        "native_memory": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
        "synthetic": True,
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render complete, plain-language public speed evidence",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--write", action="store_true")
    modes.add_argument("--check", action="store_true")
    for name in (
        "report",
        "report-sha256",
        "correctness-receipt",
        "correctness-receipt-sha256",
        "practice-source-sha256",
        "correctness-renderer-source-sha256",
        "correctness-recorder-source-sha256",
        "candidate-source-sha256",
        "native-engine-sha256",
        "native-bridge-sha256",
    ):
        parser.add_argument("--" + name)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(
            all(
                getattr(options, key) is None
                for key in (
                    "report",
                    "report_sha256",
                    "correctness_receipt",
                    "correctness_receipt_sha256",
                    "practice_source_sha256",
                    "correctness_renderer_source_sha256",
                    "correctness_recorder_source_sha256",
                    "candidate_source_sha256",
                    "native_engine_sha256",
                    "native_bridge_sha256",
                )
            ),
            "synthetic graph controls cannot accept actual evidence or artifacts",
        )
        legacy = verified_legacy()
        document = source_self_test()
    else:
        legacy = verified_legacy()
        pins = legacy.command_pins(options)
        charts, manifest_raw, manifest = render_actual(pins)
        payloads = dict(charts)
        payloads[MANIFEST_RELATIVE] = manifest_raw
        publications: list[dict[str, Any]] = []
        for relative in APPROVED_OUTPUTS:
            payload = payloads[relative]
            if options.write:
                publications.append(write_atomic(relative, payload))
            else:
                actual = read_owned_regular(
                    relative,
                    hashlib.sha256(payload).hexdigest(),
                    MAX_EVIDENCE_BYTES,
                )
                require(actual == payload, "a complete V2 graph was changed")
        document = {
            "schema": SCHEMA + ("-published" if options.write else "-checked"),
            "status": "PASS",
            "chart_label": PUBLIC_LABEL,
            "public_matrix_sha256": pins.matrix,
            "case_denominator": legacy.PUBLIC_CASE_COUNT,
            "paired_trials_per_case": legacy.PAIRED_TRIALS,
            "total_complete_paired_rows": (
                legacy.PUBLIC_CASE_COUNT * legacy.PAIRED_TRIALS
            ),
            "report_sha256": pins.report,
            "correctness_receipt_sha256": pins.correctness_receipt,
            "manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
            "charts": manifest["charts"],
            "publications": publications,
            "hidden_cases_read": 0,
            "native_memory": "NOT MEASURED",
            "candidate_qualified_for_hidden_benchmark": False,
            "final_winner_selected": False,
        }
    verify_runtime()
    sys.stdout.buffer.write(legacy.canonical(document))
    sys.stdout.buffer.flush()
    return 0


if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
