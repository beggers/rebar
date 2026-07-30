#!/usr/bin/env python3
"""Render an honest, source-only comparison of frozen public Rust evidence.

Only four already published public evidence documents are opened.  In
particular, receipt entries naming raw artifacts are provenance information,
not permission to open those artifacts.  The V3 proposal size and missing seed
are explicitly user-supplied metadata; no proposal or seed file is inspected.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import math
import os
import stat
import sys
from dataclasses import dataclass
from typing import Any


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SELF = "tools/render_rust_architecture_comparison_v1.py"
SVG = "docs/evidence/rust-architecture-comparison-v1.svg"
INPUTS = "docs/evidence/rust-architecture-comparison-v1.inputs.json"
SUMMARY = "docs/evidence/rust-architecture-comparison-v1.json"
OUTPUTS = (SVG, INPUTS, SUMMARY)
SCHEMA = "rebar-rust-architecture-comparison-v1"
UNMEASURED = "NOT MEASURED"


@dataclass(frozen=True)
class Owner:
    role: str
    relative: str
    sha256: str
    size: int


ORIGINAL = Owner(
    "original_public_v2_profile_summary",
    "oracle/phase3/evidence/rust-public-profile-v2-complete-summary-v1.json",
    "1f2dcbdabfd8e7c054996fc044fcaa32bebf86f5a12e5486398a720833ea5e18",
    509123,
)
V26_RECEIPT = Owner(
    "root_owned_v26_public_publication_receipt",
    "oracle/phase2/evidence/"
    "rust-native-architecture-public-gate-v2-v26-anchor-public-run-001-"
    "publication-receipt.json",
    "23baf96a92f4fd2bf2809730bed056606de0c9c350ed46eea31fa9bdff6a8d80",
    40906,
)
V27_RECEIPT = Owner(
    "root_owned_v27_public_publication_receipt",
    "oracle/phase2/evidence/"
    "rust-native-architecture-public-gate-v2-v27-compiler-public-run-001-"
    "publication-receipt.json",
    "a825c358434fb44ab9d52eb8021271115b12e41c58b26243c7770faf4d533449",
    68330,
)
OVERVIEW = Owner(
    "existing_public_chart_inputs_v101",
    "docs/evidence/candidate-current-overview-v101.inputs.json",
    "157e2e63b154bf0360b9160ce110e0d97534a9bc1da3f57a3e98a2b1d532bda8",
    10788,
)
OWNERS = (ORIGINAL, V26_RECEIPT, V27_RECEIPT, OVERVIEW)

EXPECTED_ORIGINAL_SPEED = 0.8649792983684755
EXPECTED_V26_SPEED = 1.2520878685068846
EXPECTED_V26_LOWER = 1.1990748170405823
EXPECTED_V26_UPPER = 1.3083112791522158
EXPECTED_DENSE_SPEED = 1.979099276996251
EXPECTED_V27_SPEED = 0.7967512788167544
EXPECTED_V27_LOWER = 0.7477430408484538
EXPECTED_V27_UPPER = 0.8453719226231972
EXPECTED_V27_DENSE_SPEED = 0.4205648528352947
EXPECTED_FROZEN_ORIGINAL_FAILURES = 1352
EXPECTED_PUBLIC_FULL_FAILURES = 1145


class Rejected(ValueError):
    """The frozen public evidence or source-only boundary was violated."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise Rejected(message)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical(value: object) -> bytes:
    return (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("ascii")


def unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result, "duplicate JSON evidence field")
        result[key] = value
    return result


def parse(payload: bytes, label: str) -> dict[str, Any]:
    def reject_nonfinite(_: str) -> None:
        raise Rejected("nonfinite JSON evidence: " + label)

    try:
        value = json.loads(
            payload,
            object_pairs_hook=unique_object,
            parse_constant=reject_nonfinite,
        )
    except (UnicodeError, TypeError, ValueError) as failure:
        raise Rejected("invalid frozen public evidence: " + label) from failure
    require(type(value) is dict, "frozen public evidence must be an object: " + label)
    require(canonical(value) == payload, "noncanonical frozen public evidence: " + label)
    return value


def relative_path(value: str) -> str:
    require(type(value) is str, "an exact source or output path is required")
    require(
        value in {SELF, *(owner.relative for owner in OWNERS), *OUTPUTS},
        "a path escaped the exact public chart allowlist",
    )
    require(
        all(part not in ("", ".", "..") for part in value.split("/"))
        and "\\" not in value
        and "\x00" not in value,
        "an approved public path must be canonical",
    )
    return os.path.join(ROOT, value)


class SourceWall:
    """Reject every file, process, timer, or network effect outside ownership."""

    def __init__(self, mode: str) -> None:
        self.mode = mode
        self.sources = frozenset(
            relative_path(relative)
            for relative in (SELF, *(owner.relative for owner in OWNERS))
        )
        self.outputs = frozenset(relative_path(relative) for relative in OUTPUTS)

    def check(self, event: str, arguments: tuple[Any, ...]) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 else 0
            require(type(path) is str and type(flags) is int, "unapproved file descriptor")
            writing = bool(
                flags
                & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
            )
            if writing:
                mandatory = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                require(
                    self.mode == "render"
                    and path in self.outputs
                    and flags & mandatory == mandatory,
                    "source-only wall rejected an unowned or nonexclusive write",
                )
            else:
                approved_output = self.mode == "verify" and path in self.outputs
                require(
                    (path in self.sources or approved_output)
                    and bool(flags & os.O_NOFOLLOW),
                    "source-only wall rejected proposal, raw case, archive, or native data",
                )
            return

        if (
            event.startswith(
                (
                    "subprocess.",
                    "socket.",
                    "ctypes.",
                    "os.exec",
                    "os.spawn",
                    "time.",
                    "threading.",
                    "_thread.",
                )
            )
            or event
            in {
                "os.chdir",
                "os.chmod",
                "os.fork",
                "os.link",
                "os.mkdir",
                "os.posix_spawn",
                "os.putenv",
                "os.remove",
                "os.rename",
                "os.rmdir",
                "os.symlink",
                "os.system",
                "os.truncate",
            }
        ):
            raise Rejected("source-only wall rejected a process, timer, network, or mutation")

        if event == "import" and arguments:
            name = arguments[0]
            require(
                not (
                    type(name) is str
                    and (
                        name in {"ctypes", "subprocess"}
                        or name.startswith(("candidates.", "rebar."))
                    )
                ),
                "source-only wall rejected a candidate or process import",
            )


def read(relative: str, *, expected_size: int | None = None) -> bytes:
    path = relative_path(relative)
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        metadata = os.fstat(descriptor)
        require(
            stat.S_ISREG(metadata.st_mode)
            and stat.S_IMODE(metadata.st_mode) == 0o600
            and metadata.st_nlink == 1
            and metadata.st_uid == os.getuid(),
            "frozen public owner identity changed: " + relative,
        )
        if expected_size is not None:
            require(metadata.st_size == expected_size, "frozen owner size changed: " + relative)
        blocks: list[bytes] = []
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            blocks.append(block)
        payload = b"".join(blocks)
        require(len(payload) == metadata.st_size, "frozen owner read was incomplete")
        return payload
    finally:
        os.close(descriptor)


def authenticate(owner: Owner) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = read(owner.relative, expected_size=owner.size)
    require(digest(payload) == owner.sha256, "frozen public owner SHA-256 changed: " + owner.role)
    return parse(payload, owner.role), {
        "bytes": owner.size,
        "path": owner.relative,
        "role": owner.role,
        "sha256": owner.sha256,
    }


def exact_number(actual: object, expected: float | int, label: str) -> None:
    require(type(actual) in (int, float) and actual == expected, "altered public metric: " + label)


def validate_architecture_receipt(
    receipt: dict[str, Any],
    *,
    architecture: str,
    session: str,
    expected_speed: float,
    expected_lower: float,
    expected_upper: float,
    expected_faster: int,
    expected_slower: int,
    expected_regressions: int,
    expected_dense_speed: float,
    expected_dense_faster: int,
) -> None:
    label = architecture.upper()
    require(
        receipt.get("schema")
        == "rebar-owned-rust-native-architecture-public-gate-v2-durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("architecture") == architecture
        and receipt.get("session") == session
        and receipt.get("root_authorization") == "EXPLICIT",
        "the " + label + " source is not the authentic root-owned public publication receipt",
    )
    require(
        receipt.get("candidate_qualified") is False and receipt.get("winner_selected") is False,
        label + " durable publication cannot manufacture a qualified candidate or winner",
    )
    require(
        receipt.get("performance_evidence_scope")
        == "EXPLORATORY CORRECTNESS-GATED PUBLIC 416 ONLY; PUBLIC 10434 FAILED",
        label + " exploratory public speed was mislabeled as qualification",
    )
    exact_number(receipt.get("public_10434_case_count"), 10434, label + " full public denominator")
    exact_number(
        receipt.get("public_10434_mismatch_count"),
        EXPECTED_PUBLIC_FULL_FAILURES,
        label + " full public semantic mismatches",
    )
    require(
        receipt.get("public_10434_correctness_status") == "FAIL"
        and receipt.get("public_416_timing_status") == "PASS",
        label + " full-public failure or measured timing status was omitted",
    )
    subset = receipt.get("public_416_correctness_gate")
    require(type(subset) is dict and subset.get("status") == "PASS", label + " public timing subset failed")
    exact_number(subset.get("case_count"), 416, label + " subset denominator")
    exact_number(subset.get("mismatch_count"), 0, label + " subset correctness mismatches")
    require(subset.get("all_mismatches") == [], label + " subset concealed a semantic mismatch")

    performance = receipt.get("performance_summary")
    require(type(performance) is dict, label + " actual measured public performance disappeared")
    for field, expected in (
        ("case_count", 416),
        ("paired_row_count", 1664),
        ("faster_case_count", expected_faster),
        ("slower_case_count", expected_slower),
        ("equal_case_count", 0),
        ("regression_over_20_percent_count", expected_regressions),
    ):
        exact_number(performance.get(field), expected, label + " " + field)
    exact_number(performance.get("geomean_speedup_vs_stdlib"), expected_speed, label + " public speedup")
    confidence = performance.get("confidence_interval_95")
    require(type(confidence) is dict, label + " measured 95% interval disappeared")
    exact_number(confidence.get("lower"), expected_lower, label + " 95% lower bound")
    exact_number(confidence.get("upper"), expected_upper, label + " 95% upper bound")
    exact_number(confidence.get("resamples"), 400, label + " confidence resample count")
    require(expected_lower < expected_speed < expected_upper, "invalid " + label + " confidence interval")

    cohorts = performance.get("cohorts")
    require(type(cohorts) is dict, label + " measured cohort evidence disappeared")
    dense = cohorts.get("mandatory_literal_dense_same_first_byte")
    require(type(dense) is dict, label + " dense same-first-byte cohort disappeared")
    exact_number(dense.get("case_count"), 104, label + " dense cohort denominator")
    exact_number(dense.get("faster_case_count"), expected_dense_faster, label + " dense cohort faster cases")
    exact_number(dense.get("geomean_speedup"), expected_dense_speed, label + " dense cohort speed")

    ratios = performance.get("case_ratios")
    require(type(ratios) is dict and len(ratios) == 416, label + " omitted a complete public case ratio")
    values = tuple(ratios.values())
    require(
        all(type(value) in (int, float) and math.isfinite(value) and value > 0 for value in values),
        label + " contains an invalid measured public case ratio",
    )
    require(
        sum(value > 1 for value in values) == expected_faster
        and sum(value < 1 for value in values) == expected_slower,
        label + " measured faster/slower case outcomes changed",
    )
    reconstructed = math.exp(math.fsum(math.log(value) for value in values) / 416)
    require(
        math.isclose(reconstructed, expected_speed, rel_tol=0.0, abs_tol=2e-15),
        label + " public speedup cannot be reconstructed from authenticated receipt ratios",
    )
    regressions = performance.get("all_regressions_over_20_percent")
    require(
        type(regressions) is list and len(regressions) == expected_regressions,
        label + " >20% public regressions disappeared",
    )
    cases: set[str] = set()
    for record in regressions:
        require(type(record) is dict, "invalid " + label + " public regression record")
        name = record.get("case")
        slowdown = record.get("slowdown_ratio")
        require(
            type(name) is str
            and name in ratios
            and name not in cases
            and type(slowdown) in (int, float)
            and math.isfinite(slowdown)
            and slowdown > 1.2
            and math.isclose(1 / ratios[name], slowdown, rel_tol=0.0, abs_tol=2e-15),
            label + " concealed or fabricated a public >20% slowdown",
        )
        cases.add(name)


def validate(context: dict[str, dict[str, Any]]) -> dict[str, Any]:
    original = context["original"]
    overview = context["overview"]

    require(
        original.get("schema") == "rebar-rust-public-profile-v2-complete-evidence-publication-v1"
        and original.get("status") == "PASS"
        and original.get("public_correctness_status") == "PASS",
        "the original public V2 profile is not complete authenticated passing evidence",
    )
    exact_number(original.get("public_correctness_case_count"), 416, "original public denominator")
    original_overall = original.get("overall")
    require(type(original_overall) is dict, "original public speed summary disappeared")
    exact_number(
        original_overall.get("equal_case_geometric_speedup"),
        EXPECTED_ORIGINAL_SPEED,
        "original public equal-case geometric speedup",
    )
    exact_number(original_overall.get("pairs"), 1664, "original public paired rows")
    exact_number(original_overall.get("rust_faster_case_count"), 222, "original faster cases")
    exact_number(original_overall.get("rust_slower_case_count"), 194, "original slower cases")
    exact_number(original.get("qualified_candidate_count"), 0, "original qualification count")
    require(
        original.get("winner_selected") is False and original.get("final_speed") == UNMEASURED,
        "original public practice cannot invent a qualification or final result",
    )

    require(
        overview.get("schema") == "rebar-candidate-current-overview-v101-inputs",
        "the existing original-suite public chart input was replaced",
    )
    headline = overview.get("headline")
    snapshot = overview.get("snapshot")
    require(type(headline) is dict and type(snapshot) is dict, "frozen original-suite history disappeared")
    for container, name in (
        (headline, "rust_current_exact_semantic_mismatch_count"),
        (headline, "rust_previous_actual_v24_exact_semantic_mismatch_count"),
        (snapshot, "rust_v24_original_campaign_semantic_mismatch_count"),
        (snapshot, "rust_v25_original_campaign_semantic_mismatch_count"),
    ):
        exact_number(container.get(name), EXPECTED_FROZEN_ORIGINAL_FAILURES, name)
    exact_number(overview.get("original_case_execution_denominator"), 31237, "original frozen denominator")
    exact_number(overview.get("qualified_candidate_count"), 0, "existing chart qualification count")
    require(overview.get("winner_selected") is False, "existing public chart invented a final winner")

    validate_architecture_receipt(
        context["v26_receipt"],
        architecture="v26",
        session="v26-anchor-public-run-001",
        expected_speed=EXPECTED_V26_SPEED,
        expected_lower=EXPECTED_V26_LOWER,
        expected_upper=EXPECTED_V26_UPPER,
        expected_faster=247,
        expected_slower=169,
        expected_regressions=11,
        expected_dense_speed=EXPECTED_DENSE_SPEED,
        expected_dense_faster=86,
    )
    validate_architecture_receipt(
        context["v27_receipt"],
        architecture="v27",
        session="v27-compiler-public-run-001",
        expected_speed=EXPECTED_V27_SPEED,
        expected_lower=EXPECTED_V27_LOWER,
        expected_upper=EXPECTED_V27_UPPER,
        expected_faster=138,
        expected_slower=278,
        expected_regressions=143,
        expected_dense_speed=EXPECTED_V27_DENSE_SPEED,
        expected_dense_faster=23,
    )

    return {
        "baseline_speedup": 1.0,
        "original_public_speedup": EXPECTED_ORIGINAL_SPEED,
        "original_public_faster_cases": 222,
        "original_public_slower_cases": 194,
        "original_frozen_case_execution_count": 31237,
        "original_frozen_semantic_mismatch_count": EXPECTED_FROZEN_ORIGINAL_FAILURES,
        "public_case_count": 416,
        "paired_public_rows": 1664,
        "v26_public_speedup": EXPECTED_V26_SPEED,
        "v26_public_95_percent_confidence_interval": {
            "lower": EXPECTED_V26_LOWER,
            "upper": EXPECTED_V26_UPPER,
        },
        "v26_public_faster_case_count": 247,
        "v26_public_slower_case_count": 169,
        "v26_public_faster_case_fraction": 247 / 416,
        "v26_dense_case_count": 104,
        "v26_dense_faster_case_count": 86,
        "v26_dense_cohort_speedup": EXPECTED_DENSE_SPEED,
        "v26_public_regression_over_20_percent_count": 11,
        "v26_public_full_case_count": 10434,
        "v26_public_full_semantic_mismatch_count": EXPECTED_PUBLIC_FULL_FAILURES,
        "v26_public_full_correctness_status": "FAIL",
        "v26_candidate_qualified": False,
        "v27_public_speedup": EXPECTED_V27_SPEED,
        "v27_public_95_percent_confidence_interval": {
            "lower": EXPECTED_V27_LOWER,
            "upper": EXPECTED_V27_UPPER,
        },
        "v27_public_faster_case_count": 138,
        "v27_public_slower_case_count": 278,
        "v27_public_faster_case_fraction": 138 / 416,
        "v27_dense_case_count": 104,
        "v27_dense_faster_case_count": 23,
        "v27_dense_cohort_speedup": EXPECTED_V27_DENSE_SPEED,
        "v27_public_regression_over_20_percent_count": 143,
        "v27_public_full_case_count": 10434,
        "v27_public_full_semantic_mismatch_count": EXPECTED_PUBLIC_FULL_FAILURES,
        "v27_public_full_correctness_status": "FAIL",
        "v27_candidate_qualified": False,
        "v3_public_final_proposal": {
            "claimed_case_count": "226m",
            "metadata_source": "USER-STATED PUBLIC PROPOSAL METADATA; PROPOSAL FILE NOT OPENED",
            "proposal_exists": True,
            "published_seed": "ABSENT",
            "seed_file_opened": False,
        },
        "final_speed": UNMEASURED,
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }


def tag(name: str, **attributes: object) -> str:
    fields = " ".join(
        f'{key.replace("_", "-")}="{html.escape(str(value), quote=True)}"'
        for key, value in attributes.items()
    )
    return "<" + name + (" " + fields if fields else "") + ">"


def text(value: object) -> str:
    return html.escape(str(value), quote=False)


def svg(facts: dict[str, Any]) -> bytes:
    axis_left = 344
    axis_width = 786
    axis_max = 2.2

    def x(value: float) -> float:
        return axis_left + axis_width * value / axis_max

    pieces = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="1180" '
        'viewBox="0 0 1280 1180" role="img" aria-labelledby="title description">',
        '<title id="title">Rust architecture comparison: public speed gains do not establish correctness</title>',
        '<desc id="description">Python standard-library baseline 1.0x; original public Rust '
        '0.8649792983684755x; Rust V26 exploratory public 1.2520878685068846x, 95 percent '
        'confidence interval 1.1990748170405823 to 1.3083112791522158; V26 dense public '
        'cohort 1.979099276996251x. Rust V27 exploratory public 0.7967512788167544x, '
        '95 percent confidence interval 0.7477430408484538 to 0.8453719226231972; '
        'V27 dense public cohort 0.4205648528352947x. V26 and V27 both remain unqualified: '
        'their full 10,434-case public gates failed with 1,145 mismatches. V26 has '
        '247 of 416 public cases faster and 11 regressions over 20 percent; V27 has '
        '138 of 416 faster and 143 regressions over 20 percent. The frozen original suite '
        'retains 1,352 mismatches; no final winner exists.</desc>',
        '<rect width="1280" height="1180" fill="#f6f8fc"/>',
        '<rect x="34" y="32" width="1212" height="1112" rx="24" fill="#ffffff" '
        'stroke="#d9e1ed" stroke-width="1.5"/>',
        '<text x="70" y="91" fill="#172238" font-family="system-ui, sans-serif" '
        'font-size="30" font-weight="760">Rust architecture: V26 faster, V27 slower, both fail</text>',
        '<text x="70" y="122" fill="#56647b" font-family="system-ui, sans-serif" '
        'font-size="15">Public development evidence only. Speed is relative to Python; '
        'above 1.0x is faster.</text>',
        '<rect x="70" y="145" width="574" height="33" rx="16.5" fill="#e7eefb"/>',
        '<text x="86" y="166" fill="#295097" font-family="system-ui, sans-serif" '
        'font-size="12.5" font-weight="700">BOTH 416-CASE TIMING SAMPLES PASSED; BOTH FULL GATES FAILED</text>',
    ]

    for tick in (0.0, 0.5, 1.0, 1.5, 2.0):
        position = x(tick)
        color = "#8795ac" if tick == 1.0 else "#e6ebf2"
        dash = ' stroke-dasharray="6 5"' if tick == 1.0 else ""
        pieces.append(
            f'<line x1="{position:.2f}" y1="209" x2="{position:.2f}" y2="588" '
            f'stroke="{color}" stroke-width="{1.5 if tick == 1.0 else 1}"{dash}/>'
        )
        pieces.append(
            f'<text x="{position:.2f}" y="200" text-anchor="middle" fill="#66748a" '
            f'font-family="system-ui, sans-serif" font-size="13">{tick:.1f}x</text>'
        )

    rows = (
        {
            "y": 258,
            "label": "Python standard library",
            "detail": "Reference: same public cases",
            "value": facts["baseline_speedup"],
            "display": "1.00x",
            "exact": "baseline = 1.0",
            "color": "#8391a7",
        },
        {
            "y": 344,
            "label": "Original Rust",
            "detail": "Frozen public V2 profile",
            "value": facts["original_public_speedup"],
            "display": "0.865x",
            "exact": "exact: 0.8649792983684755",
            "color": "#df9252",
        },
        {
            "y": 433,
            "label": "V26 Rust: public overall",
            "detail": "Required-character search; 416 cases",
            "value": facts["v26_public_speedup"],
            "display": "1.252x",
            "exact": "exact: 1.2520878685068846",
            "color": "#2876ca",
        },
        {
            "y": 537,
            "label": "V27 Rust: public overall",
            "detail": "Compiler architecture; 416 cases",
            "value": facts["v27_public_speedup"],
            "display": "0.797x",
            "exact": "exact: 0.7967512788167544",
            "color": "#b45464",
        },
    )

    for row in rows:
        y = row["y"]
        value = row["value"]
        right = x(value)
        pieces.extend(
            (
                f'<text x="70" y="{y - 2}" fill="#253149" '
                f'font-family="system-ui, sans-serif" font-size="16" '
                f'font-weight="680">{text(row["label"])}</text>',
                f'<text x="70" y="{y + 19}" fill="#6a778a" '
                f'font-family="system-ui, sans-serif" font-size="12.5">'
                f'{text(row["detail"])}</text>',
                f'<rect x="{axis_left}" y="{y - 17}" width="{right - axis_left:.2f}" '
                f'height="30" rx="7" fill="{row["color"]}"/>',
                f'<text x="{right + 12:.2f}" y="{y + 3}" fill="#1e2b42" '
                f'font-family="system-ui, sans-serif" font-size="16" '
                f'font-weight="750">{text(row["display"])}</text>',
                f'<text x="{axis_left}" y="{y + 33}" fill="#657389" '
                f'font-family="ui-monospace, monospace" font-size="11.5">'
                f'{text(row["exact"])}</text>',
            )
        )
        if row["label"] in ("V26 Rust: public overall", "V27 Rust: public overall"):
            architecture = "v26" if row["label"].startswith("V26") else "v27"
            interval = facts[architecture + "_public_95_percent_confidence_interval"]
            lower = x(interval["lower"])
            upper = x(interval["upper"])
            interval_color = "#164a89" if architecture == "v26" else "#833845"
            pieces.extend(
                (
                    f'<line x1="{lower:.2f}" y1="{y - 26}" x2="{upper:.2f}" '
                    f'y2="{y - 26}" stroke="{interval_color}" stroke-width="3"/>',
                    f'<line x1="{lower:.2f}" y1="{y - 32}" x2="{lower:.2f}" '
                    f'y2="{y - 20}" stroke="{interval_color}" stroke-width="2"/>',
                    f'<line x1="{upper:.2f}" y1="{y - 32}" x2="{upper:.2f}" '
                    f'y2="{y - 20}" stroke="{interval_color}" stroke-width="2"/>',
                    f'<text x="{axis_left}" y="{y + 51}" fill="{interval_color}" '
                    'font-family="ui-monospace, monospace" font-size="11.5">'
                    f'95% CI: [{interval["lower"]}, {interval["upper"]}]</text>',
                )
            )

    pieces.extend(
        (
            '<rect x="70" y="606" width="1058" height="72" rx="11" fill="#eef7f3"/>',
            '<text x="89" y="634" fill="#2d5544" font-family="system-ui, sans-serif" '
            'font-size="14" font-weight="750">DENSE SAME-FIRST-BYTE COHORT: 104 PUBLIC CASES</text>',
            '<text x="89" y="657" fill="#236945" font-family="ui-monospace, monospace" '
            'font-size="12.5">V26: 1.979099276996251x (86 faster)</text>',
            '<text x="634" y="657" fill="#8b4650" font-family="ui-monospace, monospace" '
            'font-size="12.5">V27: 0.4205648528352947x (23 faster)</text>',
            '<rect x="70" y="696" width="540" height="179" rx="14" fill="#fff1ef" '
            'stroke="#edb2aa" stroke-width="1.4"/>',
            '<text x="91" y="728" fill="#9a2921" font-family="system-ui, sans-serif" '
            'font-size="13.5" font-weight="780">V26 + V27 FULL PUBLIC CORRECTNESS: FAIL</text>',
            '<text x="91" y="776" fill="#941f19" font-family="system-ui, sans-serif" '
            'font-size="38" font-weight="800">1,145 / 10,434</text>',
            '<text x="91" y="804" fill="#7d3530" font-family="system-ui, sans-serif" '
            'font-size="14">the same public mismatches in both designs</text>',
            '<rect x="91" y="822" width="218" height="32" rx="16" fill="#bf3529"/>',
            '<text x="200" y="843" text-anchor="middle" fill="#fff" '
            'font-family="system-ui, sans-serif" font-size="13" '
            'font-weight="790">BOTH UNQUALIFIED</text>',
            '<rect x="628" y="696" width="540" height="179" rx="14" fill="#fff8eb" '
            'stroke="#edcf99" stroke-width="1.4"/>',
            '<text x="649" y="728" fill="#865819" font-family="system-ui, sans-serif" '
            'font-size="14" font-weight="780">FROZEN ORIGINAL SUITE: STILL FAILING</text>',
            '<text x="649" y="776" fill="#724717" font-family="system-ui, sans-serif" '
            'font-size="38" font-weight="800">1,352 mismatches</text>',
            '<text x="649" y="804" fill="#735937" font-family="system-ui, sans-serif" '
            'font-size="14">V24/V25 unchanged; 31,237 original case executions</text>',
            '<text x="649" y="835" fill="#735937" font-family="system-ui, sans-serif" '
            'font-size="13">Different case set from the 10,434-case public gate.</text>',
            '<rect x="70" y="890" width="1058" height="93" rx="13" fill="#edf5fc"/>',
            '<line x1="606" y1="904" x2="606" y2="969" stroke="#c9dbee"/>',
            '<text x="91" y="922" fill="#173e69" font-family="system-ui, sans-serif" '
            'font-size="17" font-weight="740">V26: 247 / 416 cases faster</text>',
            '<text x="91" y="950" fill="#385474" font-family="system-ui, sans-serif" '
            'font-size="13.5">169 slower; 11 regressions &gt;20% slower</text>',
            '<text x="630" y="922" fill="#813a48" font-family="system-ui, sans-serif" '
            'font-size="17" font-weight="740">V27: 138 / 416 cases faster</text>',
            '<text x="630" y="950" fill="#813a48" font-family="system-ui, sans-serif" '
            'font-size="13.5">278 slower; 143 regressions &gt;20% slower</text>',
            '<rect x="70" y="999" width="1058" height="91" rx="13" fill="#f2f1f8"/>',
            '<text x="91" y="1031" fill="#443d63" font-family="system-ui, sans-serif" '
            'font-size="15" font-weight="760">V3 PUBLIC FINAL PROPOSAL: 226m proposed; '
            'SEED ABSENT; NO WINNER</text>',
            '<text x="91" y="1058" fill="#615a77" font-family="system-ui, sans-serif" '
            'font-size="12.5">Proposal size/seed status are user-supplied; proposal and '
            'seed files were not opened. Final speed: NOT MEASURED.</text>',
            '<text x="70" y="1120" fill="#66748a" font-family="system-ui, sans-serif" '
            'font-size="11.5">Authenticated owners: original V2 profile, root-owned V26 '
            'and V27 publication receipts, and existing V101 public chart inputs.</text>',
            "</svg>\n",
        )
    )
    return "\n".join(pieces).encode("utf-8")


def generated(
    facts: dict[str, Any],
    owner_documents: list[dict[str, Any]],
    source_sha256: str,
    source_bytes: int,
) -> dict[str, bytes]:
    source = {"bytes": source_bytes, "path": SELF, "sha256": source_sha256}
    safety = {
        "actual_candidate_imports": 0,
        "actual_candidate_workers_started": 0,
        "actual_clock_samples": 0,
        "actual_native_artifacts_opened": 0,
        "actual_network_requests": 0,
        "actual_proposal_files_opened": 0,
        "actual_raw_case_archives_opened": 0,
        "actual_seed_files_opened": 0,
        "actual_timing_trials_run": 0,
        "v26_candidate_executed_by_renderer": False,
        "v27_candidate_executed_by_renderer": False,
    }
    input_document = {
        "schema": SCHEMA + "-inputs",
        "scope": "PUBLIC DEVELOPMENT ONLY; EXPLORATORY SPEED IS NOT QUALIFICATION",
        "frozen_public_owners": owner_documents,
        "facts": facts,
        "renderer": source,
        "source_only_effects": safety,
    }
    input_payload = canonical(input_document)
    picture = svg(facts)
    summary = {
        "schema": SCHEMA + "-summary",
        "status": "PASS; PUBLIC CHART PUBLISHED; V26 AND V27 CANDIDATES UNQUALIFIED",
        "scope": "PUBLIC DEVELOPMENT ONLY; NO FINAL RESULT OR WINNER",
        "renderer": source,
        "frozen_public_owners": owner_documents,
        "facts": facts,
        "source_only_effects": safety,
        "artifacts": {
            "inputs": {"bytes": len(input_payload), "path": INPUTS, "sha256": digest(input_payload)},
            "svg": {"bytes": len(picture), "path": SVG, "sha256": digest(picture)},
        },
        "ownership": {"renderer": SELF, "outputs": list(OUTPUTS)},
    }
    return {SVG: picture, INPUTS: input_payload, SUMMARY: canonical(summary)}


def validate_outputs(assets: dict[str, bytes], expected: dict[str, bytes]) -> None:
    require(set(assets) == set(OUTPUTS), "public chart output ownership changed")
    for relative in OUTPUTS:
        require(assets[relative] == expected[relative], "nondeterministic or altered public output: " + relative)
    picture = assets[SVG]
    for token in (
        b'role="img"',
        b'aria-labelledby="title description"',
        b"0.8649792983684755",
        b"1.2520878685068846",
        b"1.1990748170405823",
        b"1.3083112791522158",
        b"1.979099276996251",
        b"0.7967512788167544",
        b"0.7477430408484538",
        b"0.8453719226231972",
        b"0.4205648528352947",
        b"247 / 416 cases faster",
        b"138 / 416 cases faster",
        b"1,145 / 10,434",
        b"1,352 mismatches",
        b"11 regressions &gt;20% slower",
        b"143 regressions &gt;20% slower",
        b"BOTH UNQUALIFIED",
        b"UNQUALIFIED",
        b"NOT MEASURED",
        b"226m proposed",
        b"SEED ABSENT",
        b"NO WINNER",
    ):
        require(token in picture, "the public comparison chart omitted: " + token.decode())
    require(
        b"<script" not in picture and b"href=" not in picture,
        "the self-contained public SVG cannot execute code or fetch external data",
    )
    inputs = parse(assets[INPUTS], "generated chart input manifest")
    summary = parse(assets[SUMMARY], "generated chart summary")
    require(
        inputs.get("facts") == summary.get("facts")
        and inputs.get("frozen_public_owners") == summary.get("frozen_public_owners"),
        "generated chart manifests disagree about authenticated public evidence",
    )
    for role, relative in (("inputs", INPUTS), ("svg", SVG)):
        record = summary["artifacts"][role]
        require(
            record == {"bytes": len(assets[relative]), "path": relative, "sha256": digest(assets[relative])},
            "generated chart artifact identity changed: " + role,
        )


def self_test(
    context: dict[str, dict[str, Any]],
    facts: dict[str, Any],
    assets: dict[str, bytes],
    wall: SourceWall,
) -> dict[str, Any]:
    rejected: list[str] = []

    def reject_context(label: str, mutation: Any) -> None:
        hostile = copy.deepcopy(context)
        mutation(hostile)
        try:
            validate(hostile)
        except (Rejected, KeyError, TypeError, ValueError, ZeroDivisionError):
            rejected.append(label)
            return
        raise Rejected("hostile public comparison evidence was accepted: " + label)

    cases = (
        ("replace original public speed", lambda value: value["original"]["overall"].__setitem__("equal_case_geometric_speedup", 1.2)),
        ("invent original qualification", lambda value: value["original"].__setitem__("qualified_candidate_count", 1)),
        ("invent original winner", lambda value: value["original"].__setitem__("winner_selected", True)),
        ("erase frozen original mismatches", lambda value: value["overview"]["headline"].__setitem__("rust_current_exact_semantic_mismatch_count", 0)),
        ("erase frozen V24 history", lambda value: value["overview"]["snapshot"].__setitem__("rust_v24_original_campaign_semantic_mismatch_count", 0)),
        ("inflate original denominator", lambda value: value["overview"].__setitem__("original_case_execution_denominator", 31238)),
        ("replace root publication schema", lambda value: value["v26_receipt"].__setitem__("schema", "unowned")),
        ("erase root authorization", lambda value: value["v26_receipt"].__setitem__("root_authorization", "IMPLICIT")),
        ("claim V26 is qualified", lambda value: value["v26_receipt"].__setitem__("candidate_qualified", True)),
        ("select a nonexistent winner", lambda value: value["v26_receipt"].__setitem__("winner_selected", True)),
        ("hide full public gate failure", lambda value: value["v26_receipt"].__setitem__("public_10434_correctness_status", "PASS")),
        ("hide full public mismatches", lambda value: value["v26_receipt"].__setitem__("public_10434_mismatch_count", 0)),
        ("inflate full public denominator", lambda value: value["v26_receipt"].__setitem__("public_10434_case_count", 10435)),
        ("convert exploratory speed to final", lambda value: value["v26_receipt"].__setitem__("performance_evidence_scope", "FINAL QUALIFICATION")),
        ("alter measured V26 public speed", lambda value: value["v26_receipt"]["performance_summary"].__setitem__("geomean_speedup_vs_stdlib", 1.5)),
        ("erase lower confidence bound", lambda value: value["v26_receipt"]["performance_summary"]["confidence_interval_95"].__setitem__("lower", 1.0)),
        ("erase upper confidence bound", lambda value: value["v26_receipt"]["performance_summary"]["confidence_interval_95"].__setitem__("upper", 1.4)),
        ("hide a slower public case", lambda value: value["v26_receipt"]["performance_summary"].__setitem__("slower_case_count", 168)),
        ("invent a faster public case", lambda value: value["v26_receipt"]["performance_summary"].__setitem__("faster_case_count", 248)),
        ("erase an actual public ratio", lambda value: value["v26_receipt"]["performance_summary"]["case_ratios"].pop("rust-public-profile.v1.0000")),
        ("alter an actual public ratio", lambda value: value["v26_receipt"]["performance_summary"]["case_ratios"].__setitem__("rust-public-profile.v1.0000", 1.8)),
        ("hide dense public cohort", lambda value: value["v26_receipt"]["performance_summary"]["cohorts"].pop("mandatory_literal_dense_same_first_byte")),
        ("inflate dense public speed", lambda value: value["v26_receipt"]["performance_summary"]["cohorts"]["mandatory_literal_dense_same_first_byte"].__setitem__("geomean_speedup", 2.2)),
        ("hide a >20% regression", lambda value: value["v26_receipt"]["performance_summary"]["all_regressions_over_20_percent"].pop()),
        ("mislabel a >20% regression", lambda value: value["v26_receipt"]["performance_summary"]["all_regressions_over_20_percent"][0].__setitem__("slowdown_ratio", 1.1)),
        ("introduce subset mismatch", lambda value: value["v26_receipt"]["public_416_correctness_gate"].__setitem__("mismatch_count", 1)),
        ("replace V27 root publication schema", lambda value: value["v27_receipt"].__setitem__("schema", "unowned")),
        ("erase V27 root authorization", lambda value: value["v27_receipt"].__setitem__("root_authorization", "IMPLICIT")),
        ("claim V27 is qualified", lambda value: value["v27_receipt"].__setitem__("candidate_qualified", True)),
        ("hide V27 full public gate failure", lambda value: value["v27_receipt"].__setitem__("public_10434_correctness_status", "PASS")),
        ("hide V27 full public mismatches", lambda value: value["v27_receipt"].__setitem__("public_10434_mismatch_count", 0)),
        ("alter measured V27 public speed", lambda value: value["v27_receipt"]["performance_summary"].__setitem__("geomean_speedup_vs_stdlib", 1.1)),
        ("erase V27 lower confidence bound", lambda value: value["v27_receipt"]["performance_summary"]["confidence_interval_95"].__setitem__("lower", 0.6)),
        ("erase V27 upper confidence bound", lambda value: value["v27_receipt"]["performance_summary"]["confidence_interval_95"].__setitem__("upper", 1.1)),
        ("invent a V27 faster public case", lambda value: value["v27_receipt"]["performance_summary"].__setitem__("faster_case_count", 139)),
        ("hide 143 V27 regressions", lambda value: value["v27_receipt"]["performance_summary"].__setitem__("regression_over_20_percent_count", 11)),
        ("erase an actual V27 regression", lambda value: value["v27_receipt"]["performance_summary"]["all_regressions_over_20_percent"].pop()),
        ("inflate V27 dense public speed", lambda value: value["v27_receipt"]["performance_summary"]["cohorts"]["mandatory_literal_dense_same_first_byte"].__setitem__("geomean_speedup", 2.0)),
        ("introduce V27 subset mismatch", lambda value: value["v27_receipt"]["public_416_correctness_gate"].__setitem__("mismatch_count", 1)),
    )
    for label, mutation in cases:
        reject_context(label, mutation)

    for label, payload in (
        ("duplicate JSON field", b'{"x":1,"x":2}\n'),
        ("nonfinite JSON number", b'{"x":NaN}\n'),
        ("noncanonical JSON evidence", b'{ "x": 1 }\n'),
    ):
        try:
            parse(payload, label)
        except (Rejected, TypeError, ValueError):
            rejected.append(label)
            continue
        raise Rejected("hostile JSON evidence was accepted: " + label)

    for label, relative, before, after in (
        ("hide unqualified SVG warning", SVG, b"UNQUALIFIED", b"QUALIFIED"),
        ("erase V27 actual measured speed", SVG, b"0.7967512788167544", b"1.7967512788167544"),
        ("hide V27 actual major regressions", SVG, b"143 regressions &gt;20% slower", b"000 regressions &gt;20% slower"),
        ("erase full-public failures", SVG, b"1,145 / 10,434", b"0,000 / 10,434"),
        ("erase frozen original failures", SVG, b"1,352 mismatches", b"0,000 mismatches"),
        ("erase slower-case regressions", SVG, b"11 regressions &gt;20% slower", b"00 regressions &gt;20% slower"),
        ("invent V3 proposal seed", SVG, b"SEED ABSENT", b"SEED EXISTS"),
        ("invent final winner", SVG, b"NO WINNER", b"A WINNER!"),
    ):
        hostile = dict(assets)
        require(before in hostile[relative], "self-test SVG mutation target disappeared")
        hostile[relative] = hostile[relative].replace(before, after, 1)
        try:
            validate_outputs(hostile, assets)
        except (Rejected, KeyError, TypeError, ValueError):
            rejected.append(label)
            continue
        raise Rejected("hostile generated public chart was accepted: " + label)

    disallowed = (
        ("candidate adapter read", "open", (os.path.join(ROOT, "candidates/rust_candidate.py"), None, os.O_RDONLY | os.O_NOFOLLOW)),
        ("native engine read", "open", (os.path.join(ROOT, "candidates/_rust_engine.so"), None, os.O_RDONLY | os.O_NOFOLLOW)),
        ("raw public case archive read", "open", (os.path.join(ROOT, "experiments/raw-public.json"), None, os.O_RDONLY | os.O_NOFOLLOW)),
        ("proposal document read", "open", (os.path.join(ROOT, "oracle/phase3/public-proposal-v3.json"), None, os.O_RDONLY | os.O_NOFOLLOW)),
        ("proposal seed read", "open", (os.path.join(ROOT, "oracle/phase3/public-proposal-v3.seed"), None, os.O_RDONLY | os.O_NOFOLLOW)),
        ("changing README read", "open", (os.path.join(ROOT, "README.md"), None, os.O_RDONLY | os.O_NOFOLLOW)),
        ("changing log read", "open", (os.path.join(ROOT, "docs/evidence/current.log"), None, os.O_RDONLY | os.O_NOFOLLOW)),
        ("nonexclusive owned chart write", "open", (os.path.join(ROOT, SVG), None, os.O_WRONLY | os.O_CREAT)),
        ("symlink-following owner read", "open", (os.path.join(ROOT, ORIGINAL.relative), None, os.O_RDONLY)),
        ("candidate process launch", "subprocess.Popen", (PYTHON,)),
        ("native library activation", "ctypes.dlopen", ("_rust_engine.so",)),
        ("timer sampling", "time.perf_counter", ()),
        ("network access", "socket.connect", ("example.invalid",)),
        ("candidate module import", "import", ("candidates.rust_candidate",)),
        ("background thread", "_thread.start_new_thread", ()),
        ("unowned file removal", "os.remove", (os.path.join(ROOT, "README.md"),)),
    )
    for label, event, arguments in disallowed:
        try:
            wall.check(event, arguments)
        except Rejected:
            rejected.append(label)
            continue
        raise Rejected("hostile source-only side effect was accepted: " + label)

    require(
        facts["v27_public_speedup"] == EXPECTED_V27_SPEED
        and facts["v27_public_regression_over_20_percent_count"] == 143
        and facts["v26_candidate_qualified"] is False
        and facts["v27_candidate_qualified"] is False
        and facts["v3_public_final_proposal"]["published_seed"] == "ABSENT"
        and facts["winner_selected"] is False,
        "the chart fabricated V27 performance, qualification, proposal seed, or a final winner",
    )
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "rejected_hostile_mutation_count": len(rejected),
        "rejected_hostile_mutations": rejected,
        "candidate_workers_started": 0,
        "native_artifacts_opened": 0,
        "proposal_files_opened": 0,
        "raw_case_archives_opened": 0,
        "seed_files_opened": 0,
        "timers_sampled": 0,
    }


def publish(relative: str, payload: bytes) -> None:
    descriptor = os.open(
        relative_path(relative),
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
        0o600,
    )
    try:
        position = 0
        while position < len(payload):
            written = os.write(descriptor, payload[position:])
            require(written > 0, "exclusive public chart publication was interrupted")
            position += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def arguments(values: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--verify-frozen-context", "--verify", dest="verify", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    parser.add_argument("--original-sha256")
    parser.add_argument("--v26-receipt-sha256")
    parser.add_argument("--v27-receipt-sha256")
    parser.add_argument("--overview-inputs-sha256")
    parser.add_argument("--svg-sha256")
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    return parser.parse_args(values)


def main(values: list[str] | None = None) -> int:
    options = arguments(values)
    try:
        require(
            sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.flags.dont_write_bytecode == 1
            and os.path.abspath(sys.executable) == PYTHON
            and os.path.abspath(__file__) == os.path.join(ROOT, SELF),
            "use isolated, bytecode-disabled, pinned CPython 3.14.6 only",
        )
        require(
            not any(name == "candidates" or name.startswith("candidates.") for name in sys.modules),
            "a public chart renderer must not import matching candidates",
        )
        for supplied, owner in (
            (options.original_sha256, ORIGINAL),
            (options.v26_receipt_sha256, V26_RECEIPT),
            (options.v27_receipt_sha256, V27_RECEIPT),
            (options.overview_inputs_sha256, OVERVIEW),
        ):
            require(supplied is None or supplied == owner.sha256, "incorrect frozen owner fingerprint: " + owner.role)

        mode = "render" if options.render else "verify" if options.verify else "self-test"
        wall = SourceWall(mode)
        sys.addaudithook(wall.check)
        source_payload = read(SELF)
        source_sha256 = digest(source_payload)
        require(
            options.source_sha256 is None or options.source_sha256 == source_sha256,
            "incorrect public chart renderer SHA-256",
        )
        require(
            options.source_bytes is None or options.source_bytes == len(source_payload),
            "incorrect public chart renderer byte count",
        )
        documents = []
        context = {}
        for key, owner in (
            ("original", ORIGINAL),
            ("v26_receipt", V26_RECEIPT),
            ("v27_receipt", V27_RECEIPT),
            ("overview", OVERVIEW),
        ):
            context[key], document = authenticate(owner)
            documents.append(document)
        facts = validate(context)
        assets = generated(facts, documents, source_sha256, len(source_payload))
        validate_outputs(assets, assets)

        for supplied, relative in (
            (options.svg_sha256, SVG),
            (options.inputs_sha256, INPUTS),
            (options.summary_sha256, SUMMARY),
        ):
            require(supplied is None or supplied == digest(assets[relative]), "incorrect generated chart fingerprint: " + relative)

        if options.render:
            require(
                options.svg_sha256 is None
                and options.inputs_sha256 is None
                and options.summary_sha256 is None,
                "new exclusive public chart publication cannot presume output identities",
            )
            for relative in OUTPUTS:
                publish(relative, assets[relative])
            result = {
                "schema": SCHEMA + "-render",
                "status": "PASS",
                "outputs": {
                    relative: {"bytes": len(payload), "sha256": digest(payload)}
                    for relative, payload in assets.items()
                },
                "v26_candidate_qualified": False,
                "v27_candidate_qualified": False,
                "v27_public_speedup": EXPECTED_V27_SPEED,
                "winner_selected": False,
            }
        elif options.verify:
            actual = {relative: read(relative) for relative in OUTPUTS}
            validate_outputs(actual, assets)
            result = {
                "schema": SCHEMA + "-verify-frozen-context",
                "status": "PASS",
                "source_sha256": source_sha256,
                "original_public_v2_sha256": ORIGINAL.sha256,
                "v26_root_publication_receipt_sha256": V26_RECEIPT.sha256,
                "v27_root_publication_receipt_sha256": V27_RECEIPT.sha256,
                "v101_public_chart_inputs_sha256": OVERVIEW.sha256,
                "output_sha256": {relative: digest(payload) for relative, payload in actual.items()},
                "candidate_workers_started": 0,
                "native_artifacts_opened": 0,
                "proposal_files_opened": 0,
                "raw_case_archives_opened": 0,
                "seed_files_opened": 0,
                "timers_sampled": 0,
            }
        else:
            result = self_test(context, facts, assets, wall)
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (Rejected, OSError, TypeError, ValueError, KeyError, ArithmeticError) as failure:
        sys.stderr.write("rust architecture comparison rejected: " + str(failure) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
