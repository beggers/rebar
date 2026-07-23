#!/usr/bin/env python3
"""Draw verified, same-test compatibility progress without opening speed tests."""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import io
import json
import platform
import sys
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "candidates" / "evidence"
AUTHORIZED_OUTPUT = EVIDENCE / "rust-v8-correctness-progress.svg"
SCHEMA = "rebar-v7-independent-edge-oracle-v1"
ORACLE_SHA256 = "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca"
EXPECTED_SHA256 = "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526"
CHECKS = 223_198
CATEGORY_COUNT = 49
PINNED_PYTHON = (3, 14, 6)
MAX_COMPRESSED_BYTES = 32 * 1024 * 1024
MAX_DECOMPRESSED_CHARS = 768 * 1024 * 1024
MAX_JSON_VALUE_CHARS = 16 * 1024 * 1024
JSON_CHUNK_CHARS = 64 * 1024
INDEPENDENT_SEEDS = {
    "edge_generation": 2026072329,
    "memory_safety": 5928217332825410871,
    "module_api": 35403857216905324734871187764,
    "object_contract": 5928217332825411394,
    "parser_grammar": 6518143889424763005106639421778,
    "repeat_stream": 23157159151883287,
}
EMBEDDED_ORACLES = [
    {
        "cases": 14783,
        "ephemeral_address_normalisation": "0xADDRESS",
        "name": "independent-object-contract",
        "schema": "rebar-independent-object-contract-v1",
        "seed": 5928217332825411394,
        "source_sha256": (
            "0da341ec86fb174b5114309eee6d375aedcdb90e46be0619bf509f982ea528d9"
        ),
    },
    {
        "cases": 20480,
        "cases_per_family": 1280,
        "families": [
            "quantified-positive-lookahead",
            "quantified-negative-lookahead",
            "quantified-positive-lookbehind",
            "quantified-negative-lookbehind",
            "nested-capture-conditionals",
            "conditional-error-offsets",
            "scoped-inline-flags",
            "invalid-inline-flags",
            "verbose-comments-and-escapes",
            "bytes-named-backreferences",
            "bytes-error-offsets",
            "atomic-ordered-alternation",
            "possessive-repeat-captures",
            "lookbehind-backreference-width",
            "nullable-branch-captures",
            "escape-and-character-class-errors",
        ],
        "fixture_sha256": (
            "f2b0e9bfaa7dedacdf201e66499019f30860050b75dd722310f27bb1c79e35dd"
        ),
        "name": "independent-parser-grammar",
        "schema": "rebar-independent-parser-grammar-fuzz-v1",
        "seed": 6518143889424763005106639421778,
        "source_sha256": (
            "1d9a05396b452f6b25b7023e4b1a91f18ea812de5aa97425f6ced9ca94ab02ce"
        ),
    },
]


@dataclass(frozen=True)
class Family:
    key: str
    label: str
    module: str
    roles: frozenset[str]
    public_path: str
    color: str


FAMILIES = (
    Family(
        "rust", "Rust", "candidates.rust_candidate",
        frozenset({"public-python", "native-bridge", "native-engine", "native-source", "bridge-source"}),
        "candidates/rust_candidate.py", "#2563eb",
    ),
    Family(
        "zig", "Zig", "candidates.zig_candidate",
        frozenset({"public-python", "native-bridge", "native-engine"}),
        "candidates/zig_candidate.py", "#7c3aed",
    ),
    Family(
        "c", "C", "candidates.vm_candidate",
        frozenset({"public-python", "native-bridge"}),
        "candidates/vm_candidate.py", "#d97706",
    ),
    Family(
        "python", "Independent Python", "candidates.ast_candidate",
        frozenset({"public-python"}),
        "candidates/ast_candidate.py", "#db2777",
    ),
)


@dataclass(frozen=True)
class Source:
    path: str
    sha256: str
    report: dict[str, Any]


@dataclass(frozen=True)
class FailureSummary:
    count: int
    categories: frozenset[str]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def is_digest(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


class JsonStream:
    """Read one frozen report without expanding its 600 MB failure list."""

    def __init__(self, stream: Any) -> None:
        self.stream = stream
        self.decoder = json.JSONDecoder()
        self.buffer = ""
        self.index = 0
        self.total_chars = 0
        self.finished = False

    def refill(self) -> bool:
        if self.index > JSON_CHUNK_CHARS:
            self.buffer = self.buffer[self.index:]
            self.index = 0
        if self.finished:
            return False
        chunk = self.stream.read(JSON_CHUNK_CHARS)
        if not chunk:
            self.finished = True
            return False
        require(isinstance(chunk, str), "compressed JSON stream did not return text")
        self.total_chars += len(chunk)
        require(self.total_chars <= MAX_DECOMPRESSED_CHARS, "decompressed evidence exceeds its safety limit")
        self.buffer += chunk
        return True

    def skip_whitespace(self) -> None:
        while True:
            while self.index < len(self.buffer) and self.buffer[self.index] in " \t\r\n":
                self.index += 1
            if self.index < len(self.buffer) or not self.refill():
                return

    def consume(self, expected: str) -> None:
        self.skip_whitespace()
        require(
            self.index < len(self.buffer) and self.buffer[self.index] == expected,
            f"malformed compressed evidence: expected {expected!r}",
        )
        self.index += 1

    def take_if(self, expected: str) -> bool:
        self.skip_whitespace()
        if self.index < len(self.buffer) and self.buffer[self.index] == expected:
            self.index += 1
            return True
        return False

    def value(self) -> Any:
        self.skip_whitespace()
        while True:
            try:
                value, end = self.decoder.raw_decode(self.buffer, self.index)
            except json.JSONDecodeError as error:
                require(
                    len(self.buffer) - self.index <= MAX_JSON_VALUE_CHARS,
                    "a single compressed JSON value exceeds its safety limit",
                )
                if not self.refill():
                    raise ValueError("truncated or malformed compressed JSON evidence") from error
                continue
            if end == len(self.buffer) and not self.finished:
                require(
                    len(self.buffer) - self.index <= MAX_JSON_VALUE_CHARS,
                    "a single compressed JSON value exceeds its safety limit",
                )
                if self.refill():
                    continue
            self.index = end
            return value

    def failures(self) -> FailureSummary:
        self.consume("[")
        categories: set[str] = set()
        count = 0
        if self.take_if("]"):
            return FailureSummary(0, frozenset())
        while True:
            item = self.value()
            require(isinstance(item, dict), "a compatibility failure is not an object")
            require(
                {"category", "label", "expected", "actual"}.issubset(item),
                "a compatibility failure omits its reproducible observation",
            )
            category = item.get("category")
            require(isinstance(category, str) and bool(category), "a compatibility failure has no category")
            categories.add(category)
            count += 1
            require(count <= CHECKS, "failure count exceeds the frozen denominator")
            if self.take_if("]"):
                return FailureSummary(count, frozenset(categories))
            self.consume(",")

    def report(self) -> dict[str, Any]:
        self.consume("{")
        result: dict[str, Any] = {}
        if not self.take_if("}"):
            while True:
                key = self.value()
                require(isinstance(key, str), "a frozen report contains a non-string key")
                require(key not in result, "a frozen report contains a duplicated key")
                self.consume(":")
                result[key] = self.failures() if key == "failures" else self.value()
                if self.take_if("}"):
                    break
                self.consume(",")
        self.skip_whitespace()
        require(self.index == len(self.buffer) and self.finished, "compressed evidence contains trailing content")
        return result


def load_source(path: Path) -> Source:
    resolved = path.resolve()
    require(resolved.is_relative_to(EVIDENCE.resolve()), "evidence must stay in candidates/evidence")
    require(resolved.is_file(), "the explicitly requested evidence does not exist")
    require(resolved.name.endswith(".json.gz"), "compatibility evidence must be deterministic gzip")
    require(resolved.stat().st_size <= MAX_COMPRESSED_BYTES, "compressed evidence exceeds the safety limit")
    with resolved.open("rb") as stream:
        header = stream.read(10)
    require(len(header) == 10 and header[:3] == b"\x1f\x8b\x08", "invalid compressed evidence")
    require(header[4:8] == b"\0\0\0\0", "compressed evidence is not deterministically timestamped")
    # The digest covers the complete archive, including the bytes inspected above.
    with resolved.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    with gzip.open(resolved, "rt", encoding="utf-8") as stream:
        report = JsonStream(stream).report()
    require(isinstance(report, dict), "compatibility evidence must contain one JSON object")
    return Source(resolved.relative_to(ROOT).as_posix(), digest, report)


def validate_artifacts(report: dict[str, Any], family: Family | None, label: str) -> None:
    artifacts = report.get("candidate_artifacts")
    require(isinstance(artifacts, list), f"{label}: source provenance is missing")
    expected_roles = frozenset({"public-python"}) if family is None else family.roles
    require(len(artifacts) == len(expected_roles), f"{label}: source provenance is incomplete")
    require(all(isinstance(item, dict) for item in artifacts), f"{label}: invalid source provenance")
    require(
        frozenset(item.get("role") for item in artifacts) == expected_roles,
        f"{label}: engine or native source provenance changed",
    )
    for item in artifacts:
        path = item.get("path")
        require(isinstance(path, str) and path != "", f"{label}: source path is missing")
        require(is_digest(item.get("sha256")), f"{label}: source hash is invalid")
        if family is not None:
            parts = Path(path).parts
            require(not Path(path).is_absolute(), f"{label}: candidate path is not project-relative")
            require(parts and parts[0] == "candidates" and ".." not in parts, f"{label}: candidate path escapes its engine")
            if item["role"] == "public-python":
                require(path == family.public_path, f"{label}: public engine source changed families")


def validate_source(
    source: Source,
    family: Family | None,
    phase: str,
    reference_categories: dict[str, int] | None = None,
) -> dict[str, Any]:
    label = "Python reference" if family is None else f"{family.label} {phase}"
    report = source.report
    require(is_digest(source.sha256), f"{label}: evidence archive hash is invalid")
    require(report.get("schema") == SCHEMA, f"{label}: wrong frozen test")
    require(report.get("script_sha256") == ORACLE_SHA256, f"{label}: frozen test source changed")
    require(report.get("oracle") == "CPython standard-library re", f"{label}: Python reference changed")
    require(report.get("python") == "3.14.6", f"{label}: Python version changed")
    require(report.get("unicode") == "16.0.0", f"{label}: Unicode version changed")
    require(report.get("locale") == "C", f"{label}: locale changed")
    require(report.get("module") == ("re" if family is None else family.module), f"{label}: wrong candidate family")
    require(report.get("seed") == INDEPENDENT_SEEDS["edge_generation"], f"{label}: frozen seed changed")
    require(report.get("independent_source_seeds") == INDEPENDENT_SEEDS, f"{label}: independent frozen seeds changed")
    require(report.get("seeded_cases") == 8, f"{label}: generated-case count changed")
    require(report.get("unicode_stride") == 4099, f"{label}: Unicode test sampling changed")
    require(report.get("correctness_checks") == CHECKS, f"{label}: test denominator changed")
    require(report.get("expected_sha256") == EXPECTED_SHA256, f"{label}: expected Python answers changed")
    require(report.get("embedded_frozen_oracles") == EMBEDDED_ORACLES, f"{label}: embedded independent tests changed")
    categories = report.get("categories")
    require(isinstance(categories, dict) and len(categories) == CATEGORY_COUNT, f"{label}: frozen test categories changed")
    require(
        all(isinstance(key, str) and key and isinstance(value, int) and not isinstance(value, bool) and value >= 0 for key, value in categories.items()),
        f"{label}: invalid category counts",
    )
    require(sum(categories.values()) == CHECKS, f"{label}: category counts hide or duplicate tests")
    if reference_categories is not None:
        require(categories == reference_categories, f"{label}: frozen category distribution changed")
    failed = report.get("failed")
    require(isinstance(failed, int) and not isinstance(failed, bool), f"{label}: invalid mismatch count")
    require(0 <= failed <= CHECKS, f"{label}: mismatch count exceeds the frozen denominator")
    failures = report.get("failures")
    if isinstance(failures, FailureSummary):
        require(failures.count == failed, f"{label}: mismatch evidence was dropped")
        require(failures.categories.issubset(categories), f"{label}: a mismatch does not belong to the frozen test")
    else:
        require(isinstance(failures, list) and len(failures) == failed, f"{label}: mismatch evidence was dropped")
        require(
            all(isinstance(item, dict) and item.get("category") in categories for item in failures),
            f"{label}: a mismatch does not belong to the frozen test",
        )
    actual = report.get("actual_sha256")
    require(is_digest(actual), f"{label}: actual-answer digest is invalid")
    require((actual == EXPECTED_SHA256) == (failed == 0), f"{label}: actual answers contradict the mismatch count")
    require(report.get("performance") == "NOT MEASURED", f"{label}: speed data entered a compatibility chart")
    require(report.get("holdout") == "NOT ACCESSED", f"{label}: hidden cases entered a compatibility chart")
    validate_artifacts(report, family, label)
    if family is None:
        require(failed == 0, "Python compared against itself has unexplained failures")
    return {
        "failed": failed,
        "passed": CHECKS - failed,
        "path": source.path,
        "sha256": source.sha256,
    }


def validate_bundle(reference: Source, pairs: dict[str, dict[str, Source | None]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    require(set(pairs) == {family.key for family in FAMILIES}, "an independent engine was removed or added")
    reference_result = validate_source(reference, None, "reference")
    categories = reference.report["categories"]
    seen_paths = {reference.path}
    seen_digests = {reference.sha256}
    rows = []
    for family in FAMILIES:
        pair = pairs[family.key]
        require(isinstance(pair, dict) and set(pair) == {"original", "current"}, f"{family.label}: original/current labels changed")
        original = pair["original"]
        require(isinstance(original, Source), f"{family.label}: original result is missing")
        entries: dict[str, dict[str, Any] | None] = {}
        for phase in ("original", "current"):
            source = pair[phase]
            if source is None:
                require(phase == "current", f"{family.label}: original result is missing")
                entries[phase] = None
                continue
            require(isinstance(source, Source), f"{family.label}: invalid {phase} evidence")
            require(source.path not in seen_paths, f"{family.label}: evidence was reused across results")
            require(source.sha256 not in seen_digests, f"{family.label}: identical evidence was relabeled")
            result = validate_source(source, family, phase, categories)
            seen_paths.add(source.path)
            seen_digests.add(source.sha256)
            entries[phase] = result
        rows.append({"key": family.key, "label": family.label, "color": family.color, **entries})
    return reference_result, rows


def chart(reference: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    width, height = 1160, 608
    left, bar_width = 274, 474
    maximum = max(
        result["failed"]
        for row in rows
        for result in (row["original"], row["current"])
        if result is not None
    )
    maximum = max(1, maximum)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="chart-title chart-description">',
        '<title id="chart-title">How closely do the from-scratch replacements match Python?</title>',
        '<desc id="chart-description">Original and latest observed mismatches for four independently built regular-expression engines. Every row uses the same 223,198 frozen Python compatibility checks. A missing latest result is shown as not yet retested.</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#172033}.title{font-size:24px;font-weight:750}.sub{font-size:13px;fill:#52627a}.family{font-size:15px;font-weight:700}.phase{font-size:12px;fill:#52627a}.value{font-size:13px;font-weight:650}.tick{font-size:11px;fill:#52627a}.note{font-size:12px;fill:#52627a}.badge{font-size:13px;font-weight:700;fill:#166534}.grid{stroke:#e5eaf1;stroke-width:1}.missing{fill:#52627a;font-size:12px;font-weight:650}.complete{fill:#166534}.track{fill:#f1f5f9}</style>',
        '<text x="24" y="39" class="title">Are the replacements becoming compatible with Python?</text>',
        '<text x="24" y="63" class="sub">Original versus latest results on exactly the same 223,198 frozen tests. Shorter bars mean fewer differences.</text>',
        '<rect x="24" y="79" width="351" height="31" rx="15" fill="#ecfdf5"/>',
        '<text x="40" y="99" class="badge">Python reference: 223,198 / 223,198 correct</text>',
        '<text x="24" y="132" class="note">Each bar shows the actual number of behavior differences; zero is marked explicitly.</text>',
    ]
    grid_top, grid_bottom = 163, 485
    for fraction in (0, 0.25, 0.5, 0.75, 1):
        x = left + round(bar_width * fraction, 2)
        label = f"{round(maximum * fraction):,}"
        lines.append(f'<line x1="{x}" y1="{grid_top}" x2="{x}" y2="{grid_bottom}" class="grid"/>')
        lines.append(f'<text x="{x}" y="155" text-anchor="middle" class="tick">{label}</text>')
    for index, row in enumerate(rows):
        top = 179 + index * 78
        lines.append(f'<text x="24" y="{top + 18}" class="family">{escape(row["label"])}</text>')
        for phase_index, phase in enumerate(("original", "current")):
            y = top + phase_index * 29
            lines.append(f'<text x="172" y="{y + 14}" class="phase">{"Original" if phase == "original" else "Latest"}</text>')
            result = row[phase]
            if result is None:
                lines.append(f'<rect x="{left}" y="{y}" width="{bar_width}" height="19" rx="5" fill="#f8fafc" stroke="#94a3b8" stroke-dasharray="5 4"/>')
                lines.append(f'<text x="{left + 11}" y="{y + 14}" class="missing">NOT YET RETESTED</text>')
                lines.append(f'<text x="766" y="{y + 14}" class="missing">No current result; not counted as a pass</text>')
                continue
            failed = result["failed"]
            lines.append(f'<rect x="{left}" y="{y}" width="{bar_width}" height="19" rx="5" class="track"/>')
            if failed:
                observed_width = max(2, round(bar_width * failed / maximum, 2))
                lines.append(f'<rect x="{left}" y="{y}" width="{observed_width}" height="19" rx="5" fill="{row["color"]}"/>')
                detail = f'{failed:,} differences · {100 * result["passed"] / CHECKS:.4f}% correct'
                lines.append(f'<text x="766" y="{y + 14}" class="value">{escape(detail)}</text>')
            else:
                lines.append(f'<circle cx="{left + 9}" cy="{y + 9.5}" r="6" fill="#16a34a"/>')
                lines.append(f'<text x="766" y="{y + 14}" class="value complete">0 differences · 223,198 / 223,198 correct</text>')
        if index < len(rows) - 1:
            lines.append(f'<line x1="24" y1="{top + 66}" x2="1136" y2="{top + 66}" stroke="#eef2f7"/>')
    lines.extend([
        '<text x="24" y="528" class="note">“0 differences” applies only to these frozen tests. Additional real-world behavior tests are reported separately.</text>',
        '<text x="24" y="550" class="note">Compatibility only. Speed: NOT MEASURED by this chart. Hidden final cases: NOT ACCESSED.</text>',
    ])
    provenance = {
        "schema": "rebar-rust-v8-correctness-progress-v1",
        "checks_per_engine": CHECKS,
        "frozen_oracle_sha256": ORACLE_SHA256,
        "expected_python_answers_sha256": EXPECTED_SHA256,
        "reference": reference,
        "families": rows,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    lines.append('<metadata>' + escape(json.dumps(provenance, ensure_ascii=True, sort_keys=True, separators=(",", ":"))) + '</metadata>')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def synthetic_source(family: Family | None, phase: str, failed: int) -> Source:
    module = "re" if family is None else family.module
    key = "stdlib" if family is None else family.key
    categories = {f"synthetic-category-{index:02d}": 1 for index in range(CATEGORY_COUNT)}
    categories["synthetic-category-00"] = CHECKS - CATEGORY_COUNT + 1
    artifact_paths = {
        "public-python": "/pinned/python/re/__init__.py" if family is None else family.public_path,
        "native-bridge": f"candidates/_{key}_bridge.synthetic.so",
        "native-engine": f"candidates/_{key}_engine.synthetic.so",
        "native-source": "candidates/rust/src/lib.rs",
        "bridge-source": "candidates/rust/py_bridge.c",
    }
    roles = frozenset({"public-python"}) if family is None else family.roles
    artifacts = [
        {
            "role": role,
            "path": artifact_paths[role],
            "sha256": hashlib.sha256(f"synthetic/{key}/{phase}/{role}".encode()).hexdigest(),
        }
        for role in sorted(roles)
    ]
    failures = [
        {
            "category": "synthetic-category-00",
            "label": f"synthetic-{index}",
            "expected": {"synthetic": True},
            "actual": {"synthetic": False},
        }
        for index in range(failed)
    ]
    actual = EXPECTED_SHA256 if failed == 0 else hashlib.sha256(f"actual/{key}/{phase}".encode()).hexdigest()
    report = {
        "schema": SCHEMA,
        "script_sha256": ORACLE_SHA256,
        "oracle": "CPython standard-library re",
        "python": "3.14.6",
        "unicode": "16.0.0",
        "locale": "C",
        "module": module,
        "seed": INDEPENDENT_SEEDS["edge_generation"],
        "independent_source_seeds": copy.deepcopy(INDEPENDENT_SEEDS),
        "seeded_cases": 8,
        "unicode_stride": 4099,
        "embedded_frozen_oracles": copy.deepcopy(EMBEDDED_ORACLES),
        "candidate_artifacts": artifacts,
        "correctness_checks": CHECKS,
        "categories": categories,
        "expected_sha256": EXPECTED_SHA256,
        "actual_sha256": actual,
        "failed": failed,
        "failures": failures,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    relative = f"candidates/evidence/synthetic-{key}-{phase}.json.gz"
    digest = hashlib.sha256(f"synthetic/archive/{key}/{phase}".encode()).hexdigest()
    return Source(relative, digest, report)


def synthetic_bundle() -> tuple[Source, dict[str, dict[str, Source | None]]]:
    reference = synthetic_source(None, "reference", 0)
    pairs: dict[str, dict[str, Source | None]] = {}
    for index, family in enumerate(FAMILIES):
        pairs[family.key] = {
            "original": synthetic_source(family, "original", 12 + index),
            "current": synthetic_source(family, "current", 0 if index == 0 else 3 + index),
        }
    return reference, pairs


def self_test() -> dict[str, Any]:
    reference, pairs = synthetic_bundle()
    reference_result, rows = validate_bundle(reference, pairs)
    picture = chart(reference_result, rows)
    require(picture.startswith("<svg ") and picture.endswith("</svg>\n"), "synthetic SVG is invalid")
    require("223,198 / 223,198 correct" in picture, "zero mismatches are not stated explicitly")
    require("Hidden final cases: NOT ACCESSED" in picture, "hidden-case status is missing")
    streamed_report = JsonStream(io.StringIO(json.dumps(pairs["zig"]["original"].report))).report()
    streamed_source = Source(
        pairs["zig"]["original"].path,
        pairs["zig"]["original"].sha256,
        streamed_report,
    )
    validate_source(streamed_source, FAMILIES[1], "original", reference.report["categories"])

    def source_for(bundle: dict[str, dict[str, Source | None]], family: str = "rust", phase: str = "current") -> Source:
        source = bundle[family][phase]
        require(isinstance(source, Source), "synthetic corruption selected a missing result")
        return source

    checks: list[tuple[str, Any]] = [
        ("missing_family", lambda ref, bundle: bundle.pop("zig")),
        ("invented_family", lambda ref, bundle: bundle.update({"invented": bundle["zig"]})),
        ("missing_original", lambda ref, bundle: bundle["rust"].update(original=None)),
        ("wrong_phase_label", lambda ref, bundle: bundle["rust"].update({"latest": bundle["rust"].pop("current")})),
        ("wrong_candidate_family", lambda ref, bundle: source_for(bundle).report.update(module="candidates.zig_candidate")),
        ("changed_denominator", lambda ref, bundle: source_for(bundle).report.update(correctness_checks=CHECKS - 1)),
        ("missing_denominator", lambda ref, bundle: source_for(bundle).report.pop("correctness_checks")),
        ("changed_reference_answers", lambda ref, bundle: source_for(bundle).report.update(expected_sha256="0" * 64)),
        ("changed_oracle_source", lambda ref, bundle: source_for(bundle).report.update(script_sha256="0" * 64)),
        ("wrong_python", lambda ref, bundle: source_for(bundle).report.update(python="3.14.5")),
        ("wrong_unicode", lambda ref, bundle: source_for(bundle).report.update(unicode="15.0.0")),
        ("wrong_locale", lambda ref, bundle: source_for(bundle).report.update(locale="en_US.UTF-8")),
        ("changed_seed", lambda ref, bundle: source_for(bundle).report.update(seed=2026072330)),
        ("changed_independent_seed", lambda ref, bundle: source_for(bundle).report["independent_source_seeds"].update(memory_safety=0)),
        ("changed_generated_case_count", lambda ref, bundle: source_for(bundle).report.update(seeded_cases=7)),
        ("changed_unicode_stride", lambda ref, bundle: source_for(bundle).report.update(unicode_stride=4098)),
        ("dropped_category", lambda ref, bundle: source_for(bundle).report["categories"].pop("synthetic-category-01")),
        ("changed_category_denominator", lambda ref, bundle: source_for(bundle).report["categories"].update({"synthetic-category-01": 2})),
        ("boolean_failure_count", lambda ref, bundle: source_for(bundle).report.update(failed=False)),
        ("failure_count_outside_denominator", lambda ref, bundle: source_for(bundle).report.update(failed=CHECKS + 1)),
        ("hidden_failures", lambda ref, bundle: source_for(bundle, "zig").report["failures"].pop()),
        ("fake_zero", lambda ref, bundle: source_for(bundle, "zig").report.update(failed=0, failures=[])),
        ("fake_passing_digest", lambda ref, bundle: source_for(bundle).report.update(actual_sha256="0" * 64)),
        ("unknown_failure_category", lambda ref, bundle: source_for(bundle, "zig").report["failures"][0].update(category="invented")),
        ("missing_embedded_oracle", lambda ref, bundle: source_for(bundle).report["embedded_frozen_oracles"].pop()),
        ("changed_embedded_fixture", lambda ref, bundle: source_for(bundle).report["embedded_frozen_oracles"][1].update(fixture_sha256="0" * 64)),
        ("missing_native_source", lambda ref, bundle: source_for(bundle).report["candidate_artifacts"].pop()),
        ("wrong_engine_source", lambda ref, bundle: next(item for item in source_for(bundle).report["candidate_artifacts"] if item["role"] == "public-python").update(path="candidates/zig_candidate.py")),
        ("invalid_source_hash", lambda ref, bundle: source_for(bundle).report["candidate_artifacts"][0].update(sha256="not-a-digest")),
        ("candidate_source_escape", lambda ref, bundle: next(item for item in source_for(bundle).report["candidate_artifacts"] if item["role"] == "native-engine").update(path="candidates/../../foreign.so")),
        ("reused_original_evidence", lambda ref, bundle: bundle["rust"].update(current=bundle["rust"]["original"])),
        ("speed_contamination", lambda ref, bundle: source_for(bundle).report.update(performance="MEASURED")),
        ("hidden_case_contamination", lambda ref, bundle: source_for(bundle).report.update(holdout="ACCESSED")),
        ("reference_self_failure", lambda ref, bundle: ref.report.update(failed=1, failures=[{"category": "synthetic-category-00"}])),
    ]
    rejected = []
    for name, mutate in checks:
        bad_reference, bad_pairs = copy.deepcopy((reference, pairs))
        mutate(bad_reference, bad_pairs)
        try:
            validate_bundle(bad_reference, bad_pairs)
        except (KeyError, TypeError, ValueError):
            rejected.append(name)
        else:
            raise RuntimeError(f"corrupted evidence was accepted: {name}")

    for name, poisoned_json in (
        ("duplicate_json_key", '{"schema":1,"schema":2}'),
        ("trailing_json_content", '{"schema":1} {}'),
        ("truncated_failure_array", '{"failures":[{"category":"x"}'),
        ("nonobject_failure", '{"failures":[3]}'),
        ("nonreproducible_failure", '{"failures":[{"category":"x"}]}'),
        ("missing_failure_category", '{"failures":[{"label":"x","expected":1,"actual":2}]}'),
    ):
        try:
            JsonStream(io.StringIO(poisoned_json)).report()
        except (KeyError, TypeError, ValueError):
            rejected.append(name)
        else:
            raise RuntimeError(f"corrupted streaming evidence was accepted: {name}")

    partial_reference, partial_pairs = copy.deepcopy((reference, pairs))
    partial_pairs["zig"]["current"] = None
    partial_ref, partial_rows = validate_bundle(partial_reference, partial_pairs)
    partial_picture = chart(partial_ref, partial_rows)
    require("NOT YET RETESTED" in partial_picture, "missing results were silently treated as passes")
    require(partial_picture.count("0 differences · 223,198 / 223,198 correct") == 1, "a missing result was displayed as a zero")
    require(chart(reference_result, rows) == picture, "the chart is not deterministic")
    return {
        "schema": "rebar-rust-v8-correctness-progress-self-test-v1",
        "status": "PASS",
        "families": len(FAMILIES),
        "checks_per_engine": CHECKS,
        "categories_per_engine": CATEGORY_COUNT,
        "rejected_corruptions": len(rejected),
        "rejected_corruption_names": rejected,
        "missing_result_shown_explicitly": True,
        "synthetic_inputs_only": True,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("self-test", help="validate synthetic evidence and poisoned controls without opening any files")
    verify = subparsers.add_parser("verify", help="verify explicitly supplied evidence without creating a graph")
    generate = subparsers.add_parser("generate", help="draw explicitly supplied, frozen compatibility evidence")
    for command in (verify, generate):
        command.add_argument("--stdlib", type=Path, required=True)
        for family in FAMILIES:
            command.add_argument(f"--{family.key}-original", type=Path, required=True)
            command.add_argument(f"--{family.key}-current", type=Path)
    generate.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    require(
        platform.python_implementation() == "CPython" and tuple(sys.version_info[:3]) == PINNED_PYTHON,
        "requires the pinned CPython 3.14.6",
    )
    if args.command == "self-test":
        print(json.dumps(self_test(), ensure_ascii=True, sort_keys=True))
        return 0
    reference = load_source(args.stdlib)
    pairs: dict[str, dict[str, Source | None]] = {}
    for family in FAMILIES:
        original_path = getattr(args, f"{family.key}_original")
        current_path = getattr(args, f"{family.key}_current")
        pairs[family.key] = {
            "original": load_source(original_path),
            "current": None if current_path is None else load_source(current_path),
        }
    validated_reference, rows = validate_bundle(reference, pairs)
    summary: dict[str, Any] = {
        "schema": "rebar-rust-v8-correctness-progress-v1",
        "status": "PASS",
        "families": len(rows),
        "checks_per_engine": CHECKS,
        "categories_per_engine": CATEGORY_COUNT,
        "current_results": sum(row["current"] is not None for row in rows),
        "missing_current_results": sum(row["current"] is None for row in rows),
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    if args.command == "verify":
        summary["output_written"] = False
        summary["failed_by_family"] = {
            row["key"]: {
                phase: None if row[phase] is None else row[phase]["failed"]
                for phase in ("original", "current")
            }
            for row in rows
        }
        print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
        return 0
    destination = args.output.resolve()
    require(destination == AUTHORIZED_OUTPUT.resolve(), "only the authorized compatibility-progress SVG may be written")
    content = chart(validated_reference, rows)
    destination.write_text(content, encoding="utf-8")
    summary.update({
        "output": destination.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
    })
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
