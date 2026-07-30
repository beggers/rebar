#!/usr/bin/env python3
"""Publish a deterministic public V26/V27/V28 Rust architecture comparison.

Only immutable public chart sources and root-owned publication receipts may be
opened. Receipt references never grant access to raw cases, native artifacts,
candidate sources, proposals, logs, or other benchmark data.
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
SELF = "tools/render_rust_architecture_comparison_v2.py"
SVG = "docs/evidence/rust-architecture-comparison-v2.svg"
INPUTS = "docs/evidence/rust-architecture-comparison-v2.inputs.json"
SUMMARY = "docs/evidence/rust-architecture-comparison-v2.json"
OUTPUTS = (SVG, INPUTS, SUMMARY)
SCHEMA = "rebar-rust-architecture-comparison-v2"
UNMEASURED = "NOT MEASURED"


@dataclass(frozen=True)
class Owner:
    role: str
    path: str
    sha256: str
    size: int


ORIGINAL = Owner(
    "original_public_v2_profile_summary",
    "oracle/phase3/evidence/rust-public-profile-v2-complete-summary-v1.json",
    "1f2dcbdabfd8e7c054996fc044fcaa32bebf86f5a12e5486398a720833ea5e18",
    509123,
)
OVERVIEW = Owner(
    "immutable_v101_public_chart_inputs",
    "docs/evidence/candidate-current-overview-v101.inputs.json",
    "157e2e63b154bf0360b9160ce110e0d97534a9bc1da3f57a3e98a2b1d532bda8",
    10788,
)
V1_SOURCE = Owner(
    "immutable_v1_renderer",
    "tools/render_rust_architecture_comparison_v1.py",
    "2a7b6b214033ddf20cf91680b76a7f87ef53a89b7826137f898aae1b75e1c10c",
    52136,
)
V1_SVG = Owner(
    "immutable_v1_svg",
    "docs/evidence/rust-architecture-comparison-v1.svg",
    "2c61f795ba72ec7aabf9c4bc0ff7335050e8c78f7efaba97366a7b465d96efa7",
    9240,
)
V1_INPUTS = Owner(
    "immutable_v1_inputs",
    "docs/evidence/rust-architecture-comparison-v1.inputs.json",
    "3bdefc4f86ff5ac85ab8bca38b96094761e02292454e32db7f70bd254143415a",
    3389,
)
V1_SUMMARY = Owner(
    "immutable_v1_summary",
    "docs/evidence/rust-architecture-comparison-v1.json",
    "3bb50102768d291d398060e42a53a251293cf1b7d4d0cb1680319b04ce48ecc1",
    4042,
)
V26 = Owner(
    "root_owned_v26_publication_receipt",
    "oracle/phase2/evidence/"
    "rust-native-architecture-public-gate-v2-v26-anchor-public-run-001-publication-receipt.json",
    "23baf96a92f4fd2bf2809730bed056606de0c9c350ed46eea31fa9bdff6a8d80",
    40906,
)
V27 = Owner(
    "root_owned_v27_publication_receipt",
    "oracle/phase2/evidence/"
    "rust-native-architecture-public-gate-v2-v27-compiler-public-run-001-publication-receipt.json",
    "a825c358434fb44ab9d52eb8021271115b12e41c58b26243c7770faf4d533449",
    68330,
)
V28 = Owner(
    "root_owned_v28_combined_publication_receipt",
    "oracle/phase2/evidence/"
    "rust-native-architecture-public-gate-v3-v28-combined-public-run-001-publication-receipt.json",
    "c786b1216a58c4ac6a29363ce87d7741fb55fbb85f30665f795875bef244becb",
    40372,
)
OWNERS = (ORIGINAL, OVERVIEW, V1_SOURCE, V1_SVG, V1_INPUTS, V1_SUMMARY, V26, V27, V28)
ARCHITECTURES: dict[str, dict[str, Any]] = {
    "v26": {
        "receipt": V26,
        "schema": "rebar-owned-rust-native-architecture-public-gate-v2-durable-publication-receipt",
        "session": "v26-anchor-public-run-001",
        "label": "V26: required-character search",
        "speedup": 1.2520878685068846,
        "lower": 1.1990748170405823,
        "upper": 1.3083112791522158,
        "faster": 247,
        "slower": 169,
        "regressions": 11,
        "dense": 1.979099276996251,
        "dense_faster": 86,
        "color": "#2876ca",
    },
    "v27": {
        "receipt": V27,
        "schema": "rebar-owned-rust-native-architecture-public-gate-v2-durable-publication-receipt",
        "session": "v27-compiler-public-run-001",
        "label": "V27: compiler architecture",
        "speedup": 0.7967512788167544,
        "lower": 0.7477430408484538,
        "upper": 0.8453719226231972,
        "faster": 138,
        "slower": 278,
        "regressions": 143,
        "dense": 0.4205648528352947,
        "dense_faster": 23,
        "color": "#b45464",
    },
    "v28": {
        "receipt": V28,
        "schema": "rebar-owned-rust-native-architecture-public-gate-v3-durable-publication-receipt",
        "session": "v28-combined-public-run-001",
        "label": "V28: combined architecture",
        "speedup": 1.2298384265743338,
        "lower": 1.1780942933805956,
        "upper": 1.2849593897495446,
        "faster": 208,
        "slower": 208,
        "regressions": 8,
        "dense": 1.9603621849989858,
        "dense_faster": 81,
        "color": "#298b6c",
    },
}


class Rejected(ValueError):
    """A public evidence identity or the source-only wall was violated."""


def require(value: object, message: str) -> None:
    if not value:
        raise Rejected(message)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")


def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in items:
        require(type(name) is str and name not in result, "duplicate JSON evidence field")
        result[name] = value
    return result


def parse(payload: bytes, label: str) -> dict[str, Any]:
    def reject_constant(_: str) -> None:
        raise Rejected("nonfinite public JSON value: " + label)

    try:
        value = json.loads(payload, object_pairs_hook=unique, parse_constant=reject_constant)
    except (UnicodeError, TypeError, ValueError) as failure:
        raise Rejected("invalid public evidence: " + label) from failure
    require(type(value) is dict and canonical(value) == payload, "noncanonical public evidence: " + label)
    return value


def absolute(relative: str) -> str:
    require(
        type(relative) is str
        and relative in {SELF, *(owner.path for owner in OWNERS), *OUTPUTS}
        and all(part not in ("", ".", "..") for part in relative.split("/"))
        and "\\" not in relative
        and "\x00" not in relative,
        "an exact public chart owner or output path is required",
    )
    return os.path.join(ROOT, relative)


class SourceWall:
    def __init__(self, mode: str) -> None:
        self.mode = mode
        self.sources = frozenset(absolute(path) for path in (SELF, *(owner.path for owner in OWNERS)))
        self.outputs = frozenset(absolute(path) for path in OUTPUTS)

    def check(self, event: str, arguments: tuple[Any, ...]) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 else 0
            require(type(path) is str and type(flags) is int, "source wall rejected a descriptor")
            writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if writing:
                mandatory = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                require(
                    self.mode == "render" and path in self.outputs and flags & mandatory == mandatory,
                    "source-only wall rejected an unowned or nonexclusive write",
                )
            else:
                output_check = self.mode == "verify" and path in self.outputs
                require(
                    (path in self.sources or output_check) and bool(flags & os.O_NOFOLLOW),
                    "source-only wall rejected candidate, proposal, native, archive, or changing evidence",
                )
            return
        if event.startswith(("subprocess.", "socket.", "ctypes.", "os.exec", "os.spawn", "time.", "_thread.")) or event in {
            "os.chdir", "os.chmod", "os.fork", "os.link", "os.mkdir", "os.posix_spawn", "os.putenv",
            "os.remove", "os.rename", "os.rmdir", "os.symlink", "os.system", "os.truncate",
        }:
            raise Rejected("source-only wall rejected a process, timer, mutation, or network")
        if event == "import" and arguments:
            name = arguments[0]
            require(
                not (type(name) is str and (name in {"subprocess", "ctypes"} or name.startswith(("candidates.", "rebar.")))),
                "source-only wall rejected a candidate or process import",
            )


def read(relative: str, *, expected_size: int | None = None) -> bytes:
    descriptor = os.open(absolute(relative), os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        metadata = os.fstat(descriptor)
        require(
            stat.S_ISREG(metadata.st_mode)
            and stat.S_IMODE(metadata.st_mode) == 0o600
            and metadata.st_nlink == 1
            and metadata.st_uid == os.getuid()
            and (expected_size is None or metadata.st_size == expected_size),
            "public evidence owner identity or size changed: " + relative,
        )
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        payload = b"".join(chunks)
        require(len(payload) == metadata.st_size, "public evidence owner was incompletely read")
        return payload
    finally:
        os.close(descriptor)


def authenticate(owner: Owner) -> bytes:
    payload = read(owner.path, expected_size=owner.size)
    require(digest(payload) == owner.sha256, "public owner SHA-256 changed: " + owner.role)
    return payload


def number(actual: object, expected: float | int, label: str) -> None:
    require(type(actual) in (int, float) and actual == expected, "altered public metric: " + label)


def validate_receipt(architecture: str, receipt: dict[str, Any]) -> None:
    expected = ARCHITECTURES[architecture]
    label = architecture.upper()
    require(
        receipt.get("schema") == expected["schema"]
        and receipt.get("status") == "PASS"
        and receipt.get("architecture") == architecture
        and receipt.get("session") == expected["session"]
        and receipt.get("root_authorization") == "EXPLICIT",
        "the " + label + " receipt is not its authentic root-owned publication",
    )
    require(
        receipt.get("candidate_qualified") is False and receipt.get("winner_selected") is False,
        label + " publication cannot fabricate qualification or a final winner",
    )
    require(
        receipt.get("performance_evidence_scope")
        == "EXPLORATORY CORRECTNESS-GATED PUBLIC 416 ONLY; PUBLIC 10434 FAILED",
        label + " public-only exploratory timing was mislabeled as final evidence",
    )
    require(
        receipt.get("public_10434_correctness_status") == "FAIL"
        and receipt.get("public_416_timing_status") == "PASS",
        label + " concealed a failed full gate or fabricated timing",
    )
    number(receipt.get("public_10434_case_count"), 10434, label + " full public denominator")
    number(receipt.get("public_10434_mismatch_count"), 1145, label + " full public mismatches")
    gate = receipt.get("public_416_correctness_gate")
    require(type(gate) is dict and gate.get("status") == "PASS", label + " 416-case gate failed")
    number(gate.get("case_count"), 416, label + " timing-sample denominator")
    number(gate.get("mismatch_count"), 0, label + " timing-sample mismatches")
    require(gate.get("all_mismatches") == [], label + " concealed a timing-sample mismatch")

    performance = receipt.get("performance_summary")
    require(type(performance) is dict, label + " actual measured performance disappeared")
    for key, value in (
        ("case_count", 416),
        ("paired_row_count", 1664),
        ("faster_case_count", expected["faster"]),
        ("slower_case_count", expected["slower"]),
        ("equal_case_count", 0),
        ("regression_over_20_percent_count", expected["regressions"]),
    ):
        number(performance.get(key), value, label + " " + key)
    number(performance.get("geomean_speedup_vs_stdlib"), expected["speedup"], label + " public geometric speedup")
    interval = performance.get("confidence_interval_95")
    require(type(interval) is dict, label + " measured confidence interval disappeared")
    number(interval.get("lower"), expected["lower"], label + " confidence lower bound")
    number(interval.get("upper"), expected["upper"], label + " confidence upper bound")
    number(interval.get("resamples"), 400, label + " confidence resamples")
    require(expected["lower"] < expected["speedup"] < expected["upper"], label + " invalid confidence interval")

    cohorts = performance.get("cohorts")
    require(type(cohorts) is dict, label + " dense cohort disappeared")
    dense = cohorts.get("mandatory_literal_dense_same_first_byte")
    require(type(dense) is dict, label + " dense same-first-byte cohort disappeared")
    number(dense.get("case_count"), 104, label + " dense cohort denominator")
    number(dense.get("faster_case_count"), expected["dense_faster"], label + " dense faster cases")
    number(dense.get("geomean_speedup"), expected["dense"], label + " dense cohort speedup")

    ratios = performance.get("case_ratios")
    require(type(ratios) is dict and len(ratios) == 416, label + " omitted measured public cases")
    values = tuple(ratios.values())
    require(
        all(type(value) in (int, float) and math.isfinite(value) and value > 0 for value in values),
        label + " contains invalid public case ratios",
    )
    require(
        sum(value > 1 for value in values) == expected["faster"]
        and sum(value < 1 for value in values) == expected["slower"],
        label + " faster/slower case counts do not match authenticated public ratios",
    )
    reconstructed = math.exp(math.fsum(math.log(value) for value in values) / 416)
    require(
        math.isclose(reconstructed, expected["speedup"], rel_tol=0.0, abs_tol=2e-15),
        label + " geometric speedup cannot be reconstructed from public receipt ratios",
    )
    regressions = performance.get("all_regressions_over_20_percent")
    require(type(regressions) is list and len(regressions) == expected["regressions"], label + " hid a >20% regression")
    names: set[str] = set()
    for regression in regressions:
        require(type(regression) is dict, label + " invalid regression record")
        name = regression.get("case")
        slowdown = regression.get("slowdown_ratio")
        require(
            type(name) is str
            and name in ratios
            and name not in names
            and type(slowdown) in (int, float)
            and math.isfinite(slowdown)
            and slowdown > 1.2
            and math.isclose(1 / ratios[name], slowdown, rel_tol=0.0, abs_tol=2e-15),
            label + " fabricated or concealed an actual >20% regression",
        )
        names.add(name)


def validate(context: dict[str, Any]) -> dict[str, Any]:
    original = context["original"]
    require(
        original.get("schema") == "rebar-rust-public-profile-v2-complete-evidence-publication-v1"
        and original.get("status") == "PASS"
        and original.get("public_correctness_status") == "PASS"
        and original.get("winner_selected") is False
        and original.get("final_speed") == UNMEASURED,
        "the original authenticated V2 public profile was replaced or promoted to final",
    )
    number(original.get("public_correctness_case_count"), 416, "original public case denominator")
    number(original.get("qualified_candidate_count"), 0, "original qualification count")
    overall = original.get("overall")
    require(type(overall) is dict, "original V2 public performance disappeared")
    number(overall.get("equal_case_geometric_speedup"), 0.8649792983684755, "original Rust public speedup")
    number(overall.get("rust_faster_case_count"), 222, "original Rust public faster cases")
    number(overall.get("rust_slower_case_count"), 194, "original Rust public slower cases")

    overview = context["overview"]
    require(overview.get("schema") == "rebar-candidate-current-overview-v101-inputs", "original-suite source was replaced")
    headline = overview.get("headline")
    snapshot = overview.get("snapshot")
    require(type(headline) is dict and type(snapshot) is dict, "frozen original-suite loss history disappeared")
    for container, key in (
        (headline, "rust_current_exact_semantic_mismatch_count"),
        (headline, "rust_previous_actual_v24_exact_semantic_mismatch_count"),
        (snapshot, "rust_v24_original_campaign_semantic_mismatch_count"),
        (snapshot, "rust_v25_original_campaign_semantic_mismatch_count"),
    ):
        number(container.get(key), 1352, "frozen original-suite mismatches: " + key)
    number(overview.get("original_case_execution_denominator"), 31237, "frozen original-suite denominator")
    number(overview.get("qualified_candidate_count"), 0, "frozen overview qualification count")
    require(overview.get("winner_selected") is False, "frozen original overview invented a winner")

    previous_inputs = context["v1_inputs"]
    previous_summary = context["v1_summary"]
    require(
        previous_inputs.get("schema") == "rebar-rust-architecture-comparison-v1-inputs"
        and previous_summary.get("schema") == "rebar-rust-architecture-comparison-v1-summary"
        and previous_summary.get("status")
        == "PASS; PUBLIC CHART PUBLISHED; V26 AND V27 CANDIDATES UNQUALIFIED",
        "the immutable V1 architecture graph was replaced or misrepresented",
    )
    prior_facts = previous_inputs.get("facts")
    require(type(prior_facts) is dict and prior_facts == previous_summary.get("facts"), "V1 graph manifests disagree")
    for key, expected in (
        ("baseline_speedup", 1.0),
        ("original_public_speedup", 0.8649792983684755),
        ("v26_public_speedup", ARCHITECTURES["v26"]["speedup"]),
        ("v27_public_speedup", ARCHITECTURES["v27"]["speedup"]),
        ("original_frozen_semantic_mismatch_count", 1352),
        ("v26_public_full_semantic_mismatch_count", 1145),
        ("v27_public_full_semantic_mismatch_count", 1145),
        ("qualified_candidate_count", 0),
    ):
        number(prior_facts.get(key), expected, "immutable V1 chart metric " + key)
    require(
        prior_facts.get("v26_candidate_qualified") is False
        and prior_facts.get("v27_candidate_qualified") is False
        and prior_facts.get("winner_selected") is False,
        "the immutable V1 graph invented a qualification or winner",
    )
    proposal = prior_facts.get("v3_public_final_proposal")
    require(
        type(proposal) is dict
        and proposal.get("claimed_case_count") == "226m"
        and proposal.get("published_seed") == "ABSENT"
        and proposal.get("proposal_exists") is True
        and proposal.get("seed_file_opened") is False
        and proposal.get("metadata_source")
        == "USER-STATED PUBLIC PROPOSAL METADATA; PROPOSAL FILE NOT OPENED",
        "the V3 public proposal must remain explicitly user-supplied, seedless metadata",
    )
    previous_renderer = previous_summary.get("renderer")
    require(
        previous_renderer == {"bytes": V1_SOURCE.size, "path": V1_SOURCE.path, "sha256": V1_SOURCE.sha256},
        "the immutable V1 renderer identity changed",
    )
    artifacts = previous_summary.get("artifacts")
    require(type(artifacts) is dict, "immutable V1 graph artifacts disappeared")
    for key, owner in (("inputs", V1_INPUTS), ("svg", V1_SVG)):
        require(
            artifacts.get(key) == {"bytes": owner.size, "path": owner.path, "sha256": owner.sha256},
            "immutable V1 graph artifact identity changed: " + key,
        )
    require(
        previous_inputs.get("frozen_public_owners") == previous_summary.get("frozen_public_owners"),
        "immutable V1 graph provenance diverged",
    )
    previous_owners = previous_summary["frozen_public_owners"]
    require(type(previous_owners) is list and len(previous_owners) == 4, "immutable V1 public owners disappeared")
    for owner in (ORIGINAL, V26, V27, OVERVIEW):
        require(
            any(item.get("path") == owner.path and item.get("sha256") == owner.sha256 for item in previous_owners),
            "immutable V1 graph omitted prior authenticated owner: " + owner.role,
        )
    previous_picture = context["v1_svg"]
    for token in (b"1.2520878685068846", b"0.7967512788167544", b"BOTH UNQUALIFIED", b"1,145 / 10,434"):
        require(token in previous_picture, "immutable V1 graph omitted public fact: " + token.decode())

    for name in ARCHITECTURES:
        validate_receipt(name, context[name])

    architectures = {
        name: {
            "label": specification["label"],
            "public_speedup": specification["speedup"],
            "public_95_percent_confidence_interval": {
                "lower": specification["lower"],
                "upper": specification["upper"],
            },
            "public_case_count": 416,
            "public_faster_case_count": specification["faster"],
            "public_slower_case_count": specification["slower"],
            "public_regression_over_20_percent_count": specification["regressions"],
            "public_dense_case_count": 104,
            "public_dense_faster_case_count": specification["dense_faster"],
            "public_dense_cohort_speedup": specification["dense"],
            "full_public_case_count": 10434,
            "full_public_semantic_mismatch_count": 1145,
            "full_public_correctness_status": "FAIL",
            "candidate_qualified": False,
        }
        for name, specification in ARCHITECTURES.items()
    }
    return {
        "baseline_speedup": 1.0,
        "original_public_speedup": 0.8649792983684755,
        "original_public_faster_case_count": 222,
        "original_public_slower_case_count": 194,
        "original_frozen_case_execution_count": 31237,
        "original_frozen_semantic_mismatch_count": 1352,
        "architectures": architectures,
        "v3_public_final_proposal": proposal,
        "final_speed": UNMEASURED,
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }


def escape(value: object) -> str:
    return html.escape(str(value), quote=False)


def render_svg(facts: dict[str, Any]) -> bytes:
    axis_left = 344
    axis_width = 780
    axis_max = 1.55

    def x(value: float) -> float:
        return axis_left + axis_width * value / axis_max

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="1412" '
        'viewBox="0 0 1280 1412" role="img" aria-labelledby="title description">',
        '<title id="title">Rust architecture comparison: search, compiler, and combined public results</title>',
        '<desc id="description">Python baseline 1.0x; original Rust 0.8649792983684755x; '
        'V26 required-character search 1.2520878685068846x, confidence interval '
        '1.1990748170405823 to 1.3083112791522158; V27 compiler 0.7967512788167544x, '
        'interval 0.7477430408484538 to 0.8453719226231972; V28 combined '
        '1.2298384265743338x, interval 1.1780942933805956 to 1.2849593897495446. '
        'All three optimized designs remain unqualified: each fails the full 10,434-case '
        'public gate with 1,145 mismatches. V26 has 247 faster cases and 11 major regressions; '
        'V27 has 138 faster and 143 regressions; V28 has 208 faster and eight regressions. '
        'Frozen original-suite mismatches remain 1,352; final speed is not measured and '
        'no winner was selected.</desc>',
        '<rect width="1280" height="1412" fill="#f5f7fb"/>',
        '<rect x="32" y="30" width="1216" height="1350" rx="25" fill="#ffffff" '
        'stroke="#d9e1ed" stroke-width="1.5"/>',
        '<text x="69" y="89" fill="#18253a" font-family="system-ui, sans-serif" '
        'font-size="29" font-weight="780">Rust designs compared: gains are real; failures remain</text>',
        '<text x="69" y="120" fill="#59677d" font-family="system-ui, sans-serif" '
        'font-size="15">Public development evidence only. Above Python\'s 1.0x baseline is faster.</text>',
        '<rect x="69" y="143" width="596" height="34" rx="17" fill="#eaf0fb"/>',
        '<text x="86" y="165" fill="#325291" font-family="system-ui, sans-serif" '
        'font-size="12.5" font-weight="750">ALL THREE 416-CASE SAMPLES PASSED; ALL THREE FULL GATES FAILED</text>',
    ]

    for tick in (0.0, 0.5, 1.0, 1.5):
        position = x(tick)
        color = "#8897ac" if tick == 1.0 else "#e7ebf2"
        dash = ' stroke-dasharray="6 5"' if tick == 1.0 else ""
        parts.extend((
            f'<line x1="{position:.2f}" y1="211" x2="{position:.2f}" y2="738" '
            f'stroke="{color}" stroke-width="{1.5 if tick == 1.0 else 1}"{dash}/>',
            f'<text x="{position:.2f}" y="201" text-anchor="middle" fill="#66758b" '
            f'font-family="system-ui, sans-serif" font-size="13">{tick:.1f}x</text>',
        ))

    rows = [
        (257, "Python standard library", "Reference: same public cases", 1.0, "1.00x", "baseline = 1.0", "#8491a5", None),
        (350, "Original Rust", "Frozen public V2 profile", 0.8649792983684755, "0.865x", "exact: 0.8649792983684755", "#dc9254", None),
        (443, ARCHITECTURES["v26"]["label"], "Exploratory 416-case public sample", ARCHITECTURES["v26"]["speedup"], "1.252x", "exact: 1.2520878685068846", ARCHITECTURES["v26"]["color"], "v26"),
        (549, ARCHITECTURES["v27"]["label"], "Exploratory 416-case public sample", ARCHITECTURES["v27"]["speedup"], "0.797x", "exact: 0.7967512788167544", ARCHITECTURES["v27"]["color"], "v27"),
        (655, ARCHITECTURES["v28"]["label"], "Exploratory 416-case public sample", ARCHITECTURES["v28"]["speedup"], "1.230x", "exact: 1.2298384265743338", ARCHITECTURES["v28"]["color"], "v28"),
    ]
    for y, label, detail, value, display, exact, color, architecture in rows:
        right = x(value)
        parts.extend((
            f'<text x="69" y="{y - 2}" fill="#273249" font-family="system-ui, sans-serif" '
            f'font-size="15.5" font-weight="690">{escape(label)}</text>',
            f'<text x="69" y="{y + 19}" fill="#69778a" font-family="system-ui, sans-serif" '
            f'font-size="12">{escape(detail)}</text>',
            f'<rect x="{axis_left}" y="{y - 17}" width="{right - axis_left:.2f}" height="30" '
            f'rx="7" fill="{color}"/>',
            f'<text x="{right + 11:.2f}" y="{y + 3}" fill="#202c42" '
            f'font-family="system-ui, sans-serif" font-size="16" font-weight="760">{escape(display)}</text>',
            f'<text x="{axis_left}" y="{y + 34}" fill="#617086" '
            f'font-family="ui-monospace, monospace" font-size="11.5">{escape(exact)}</text>',
        ))
        if architecture is not None:
            interval = facts["architectures"][architecture]["public_95_percent_confidence_interval"]
            lower = x(interval["lower"])
            upper = x(interval["upper"])
            parts.extend((
                f'<line x1="{lower:.2f}" y1="{y - 27}" x2="{upper:.2f}" y2="{y - 27}" '
                f'stroke="{color}" stroke-width="3"/>',
                f'<line x1="{lower:.2f}" y1="{y - 33}" x2="{lower:.2f}" y2="{y - 21}" '
                f'stroke="{color}" stroke-width="2"/>',
                f'<line x1="{upper:.2f}" y1="{y - 33}" x2="{upper:.2f}" y2="{y - 21}" '
                f'stroke="{color}" stroke-width="2"/>',
                f'<text x="{axis_left}" y="{y + 54}" fill="{color}" '
                f'font-family="ui-monospace, monospace" font-size="11.5">'
                f'95% CI: [{interval["lower"]}, {interval["upper"]}]</text>',
            ))

    parts.extend((
        '<rect x="69" y="754" width="1105" height="92" rx="12" fill="#eef7f3"/>',
        '<text x="89" y="782" fill="#305746" font-family="system-ui, sans-serif" '
        'font-size="13.5" font-weight="760">DENSE SAME-FIRST-BYTE COHORT: 104 PUBLIC CASES</text>',
        '<text x="89" y="811" fill="#286c48" font-family="ui-monospace, monospace" '
        'font-size="12">search: 1.979099276996251x</text>',
        '<text x="456" y="811" fill="#88414c" font-family="ui-monospace, monospace" '
        'font-size="12">compiler: 0.4205648528352947x</text>',
        '<text x="826" y="811" fill="#286c48" font-family="ui-monospace, monospace" '
        'font-size="12">combined: 1.9603621849989858x</text>',
        '<rect x="69" y="863" width="542" height="181" rx="14" fill="#fff0ef" '
        'stroke="#ebb2ab" stroke-width="1.4"/>',
        '<text x="89" y="893" fill="#982a24" font-family="system-ui, sans-serif" '
        'font-size="13" font-weight="790">V26 + V27 + V28 FULL PUBLIC GATES: FAIL</text>',
        '<text x="89" y="945" fill="#90221b" font-family="system-ui, sans-serif" '
        'font-size="39" font-weight="810">1,145 / 10,434</text>',
        '<text x="89" y="973" fill="#7c3632" font-family="system-ui, sans-serif" '
        'font-size="13.5">same public mismatches in all three optimized designs</text>',
        '<rect x="89" y="986" width="254" height="34" rx="17" fill="#bd352c"/>',
        '<text x="216" y="1009" text-anchor="middle" fill="#fff" '
        'font-family="system-ui, sans-serif" font-size="12.5" '
        'font-weight="790">ALL THREE UNQUALIFIED</text>',
        '<rect x="629" y="863" width="545" height="181" rx="14" fill="#fff8eb" '
        'stroke="#edcf99" stroke-width="1.4"/>',
        '<text x="649" y="893" fill="#875819" font-family="system-ui, sans-serif" '
        'font-size="13" font-weight="790">FROZEN ORIGINAL SUITE: STILL FAILING</text>',
        '<text x="649" y="945" fill="#724817" font-family="system-ui, sans-serif" '
        'font-size="38" font-weight="810">1,352 mismatches</text>',
        '<text x="649" y="973" fill="#765a36" font-family="system-ui, sans-serif" '
        'font-size="13.5">V24/V25 unchanged; 31,237 original case executions</text>',
        '<text x="649" y="1002" fill="#765a36" font-family="system-ui, sans-serif" '
        'font-size="12.5">Different cases from the 10,434-case public gate.</text>',
        '<rect x="69" y="1060" width="1105" height="112" rx="13" fill="#edf4fb"/>',
        '<line x1="431" y1="1076" x2="431" y2="1157" stroke="#cbdcee"/>',
        '<line x1="805" y1="1076" x2="805" y2="1157" stroke="#cbdcee"/>',
        '<text x="88" y="1092" fill="#194575" font-family="system-ui, sans-serif" '
        'font-size="15.5" font-weight="750">SEARCH: 247 / 416 faster</text>',
        '<text x="88" y="1118" fill="#365576" font-family="system-ui, sans-serif" '
        'font-size="12.7">169 slower</text>',
        '<text x="88" y="1142" fill="#365576" font-family="system-ui, sans-serif" '
        'font-size="12.7">11 regressions &gt;20% slower</text>',
        '<text x="451" y="1092" fill="#853d4a" font-family="system-ui, sans-serif" '
        'font-size="15.5" font-weight="750">COMPILER: 138 / 416 faster</text>',
        '<text x="451" y="1118" fill="#853d4a" font-family="system-ui, sans-serif" '
        'font-size="12.7">278 slower</text>',
        '<text x="451" y="1142" fill="#853d4a" font-family="system-ui, sans-serif" '
        'font-size="12.7">143 regressions &gt;20% slower</text>',
        '<text x="825" y="1092" fill="#216b52" font-family="system-ui, sans-serif" '
        'font-size="15.5" font-weight="750">COMBINED: 208 / 416 faster</text>',
        '<text x="825" y="1118" fill="#365a4e" font-family="system-ui, sans-serif" '
        'font-size="12.7">208 slower</text>',
        '<text x="825" y="1142" fill="#365a4e" font-family="system-ui, sans-serif" '
        'font-size="12.7">8 regressions &gt;20% slower</text>',
        '<rect x="69" y="1189" width="1105" height="95" rx="13" fill="#f2f0f8"/>',
        '<text x="89" y="1222" fill="#463e64" font-family="system-ui, sans-serif" '
        'font-size="15" font-weight="770">V3 PUBLIC FINAL PROPOSAL: 226m proposed; '
        'SEED ABSENT; NO WINNER</text>',
        '<text x="89" y="1250" fill="#615975" font-family="system-ui, sans-serif" '
        'font-size="12.5">Proposal size and missing seed are user-supplied metadata; '
        'proposal and seed files were not opened. Final speed: NOT MEASURED.</text>',
        '<text x="69" y="1310" fill="#65738a" font-family="system-ui, sans-serif" '
        'font-size="11.5">V1 chart preserved and authenticated. Sources: original V2 public '
        'profile, immutable V101 inputs, and root-owned V26/V27/V28 publication receipts.</text>',
        '<text x="69" y="1334" fill="#65738a" font-family="system-ui, sans-serif" '
        'font-size="11.5">Speed is exploratory public evidence, not qualification; '
        'no candidate worker, proposal, raw archive, native binary, or timer was accessed.</text>',
        "</svg>\n",
    ))
    return "\n".join(parts).encode("utf-8")


def owner_record(owner: Owner) -> dict[str, Any]:
    return {"bytes": owner.size, "path": owner.path, "role": owner.role, "sha256": owner.sha256}


def generate(facts: dict[str, Any], source_sha256: str, source_size: int) -> dict[str, bytes]:
    source = {"bytes": source_size, "path": SELF, "sha256": source_sha256}
    owners = [owner_record(owner) for owner in OWNERS]
    source_effects = {
        "actual_candidate_imports": 0,
        "actual_candidate_workers_started": 0,
        "actual_clock_samples": 0,
        "actual_native_artifacts_opened": 0,
        "actual_network_requests": 0,
        "actual_previous_graph_mutations": 0,
        "actual_proposal_files_opened": 0,
        "actual_raw_case_archives_opened": 0,
        "actual_seed_files_opened": 0,
        "actual_timing_trials_run": 0,
    }
    inputs = canonical({
        "schema": SCHEMA + "-inputs",
        "scope": "PUBLIC DEVELOPMENT ONLY; EXPLORATORY SPEED IS NOT QUALIFICATION",
        "renderer": source,
        "frozen_public_owners": owners,
        "immutable_previous_graph": [owner_record(owner) for owner in (V1_SOURCE, V1_SVG, V1_INPUTS, V1_SUMMARY)],
        "facts": facts,
        "source_only_effects": source_effects,
    })
    picture = render_svg(facts)
    summary = canonical({
        "schema": SCHEMA + "-summary",
        "status": "PASS; V1 PRESERVED; V26, V27 AND V28 ALL UNQUALIFIED",
        "scope": "PUBLIC DEVELOPMENT ONLY; NO QUALIFIED CANDIDATE OR FINAL WINNER",
        "renderer": source,
        "frozen_public_owners": owners,
        "immutable_previous_graph": [owner_record(owner) for owner in (V1_SOURCE, V1_SVG, V1_INPUTS, V1_SUMMARY)],
        "facts": facts,
        "source_only_effects": source_effects,
        "artifacts": {
            "inputs": {"bytes": len(inputs), "path": INPUTS, "sha256": digest(inputs)},
            "svg": {"bytes": len(picture), "path": SVG, "sha256": digest(picture)},
        },
        "ownership": {"renderer": SELF, "outputs": list(OUTPUTS)},
    })
    return {SVG: picture, INPUTS: inputs, SUMMARY: summary}


def verify_outputs(actual: dict[str, bytes], expected: dict[str, bytes]) -> None:
    require(set(actual) == set(OUTPUTS), "V2 graph output ownership changed")
    for path in OUTPUTS:
        require(actual[path] == expected[path], "V2 graph output is altered or nondeterministic: " + path)
    picture = actual[SVG]
    tokens = (
        b'role="img"', b'aria-labelledby="title description"', b"0.8649792983684755",
        b"1.2520878685068846", b"1.1990748170405823", b"1.3083112791522158",
        b"0.7967512788167544", b"0.7477430408484538", b"0.8453719226231972",
        b"1.2298384265743338", b"1.1780942933805956", b"1.2849593897495446",
        b"1.979099276996251", b"0.4205648528352947", b"1.9603621849989858",
        b"247 / 416 faster", b"138 / 416 faster", b"208 / 416 faster",
        b"11 regressions &gt;20% slower", b"143 regressions &gt;20% slower",
        b"8 regressions &gt;20% slower", b"1,145 / 10,434", b"1,352 mismatches",
        b"ALL THREE UNQUALIFIED", b"226m proposed", b"SEED ABSENT", b"NO WINNER", b"NOT MEASURED",
    )
    for token in tokens:
        require(token in picture, "V2 public graph omitted: " + token.decode())
    require(b"<script" not in picture and b"href=" not in picture, "V2 graph cannot execute or fetch external data")
    inputs = parse(actual[INPUTS], "generated V2 chart inputs")
    summary = parse(actual[SUMMARY], "generated V2 chart summary")
    require(
        inputs.get("facts") == summary.get("facts")
        and inputs.get("frozen_public_owners") == summary.get("frozen_public_owners")
        and inputs.get("immutable_previous_graph") == summary.get("immutable_previous_graph"),
        "generated V2 chart manifests disagree",
    )
    for role, path in (("inputs", INPUTS), ("svg", SVG)):
        require(
            summary["artifacts"].get(role) == {"bytes": len(actual[path]), "path": path, "sha256": digest(actual[path])},
            "generated V2 chart artifact identity changed: " + role,
        )


def self_test(context: dict[str, Any], facts: dict[str, Any], assets: dict[str, bytes], wall: SourceWall) -> dict[str, Any]:
    rejected: list[str] = []

    def reject_context(label: str, mutate: Any) -> None:
        hostile = copy.deepcopy(context)
        mutate(hostile)
        try:
            validate(hostile)
        except (Rejected, KeyError, TypeError, ValueError, ZeroDivisionError):
            rejected.append(label)
            return
        raise Rejected("hostile V2 comparison evidence was accepted: " + label)

    for label, mutate in (
        ("replace original public speed", lambda value: value["original"]["overall"].__setitem__("equal_case_geometric_speedup", 1.1)),
        ("invent original final winner", lambda value: value["original"].__setitem__("winner_selected", True)),
        ("erase frozen original mismatches", lambda value: value["overview"]["headline"].__setitem__("rust_current_exact_semantic_mismatch_count", 0)),
        ("replace immutable V1 schema", lambda value: value["v1_summary"].__setitem__("schema", "mutable")),
        ("invent V1 final qualification", lambda value: value["v1_inputs"]["facts"].__setitem__("v26_candidate_qualified", True)),
        ("replace V1 renderer identity", lambda value: value["v1_summary"]["renderer"].__setitem__("sha256", "0" * 64)),
        ("replace V1 graph picture", lambda value: value.__setitem__("v1_svg", b"fabricated")),
        ("erase V1 owner receipt", lambda value: value["v1_summary"]["frozen_public_owners"].pop()),
        ("invent V3 proposal seed", lambda value: value["v1_inputs"]["facts"]["v3_public_final_proposal"].__setitem__("published_seed", "present")),
    ):
        reject_context(label, mutate)

    for architecture, specification in ARCHITECTURES.items():
        label = architecture.upper()
        for description, mutate in (
            ("replace root authorization", lambda receipt: receipt.__setitem__("root_authorization", "IMPLICIT")),
            ("replace architecture identity", lambda receipt: receipt.__setitem__("architecture", "invented")),
            ("claim false qualification", lambda receipt: receipt.__setitem__("candidate_qualified", True)),
            ("claim invented winner", lambda receipt: receipt.__setitem__("winner_selected", True)),
            ("hide full public failure", lambda receipt: receipt.__setitem__("public_10434_correctness_status", "PASS")),
            ("hide 1,145 public mismatches", lambda receipt: receipt.__setitem__("public_10434_mismatch_count", 0)),
            ("inflate full public denominator", lambda receipt: receipt.__setitem__("public_10434_case_count", 10435)),
            ("invent final evidence scope", lambda receipt: receipt.__setitem__("performance_evidence_scope", "FINAL WINNER")),
            ("alter measured speed", lambda receipt: receipt["performance_summary"].__setitem__("geomean_speedup_vs_stdlib", 2.0)),
            ("alter lower confidence bound", lambda receipt: receipt["performance_summary"]["confidence_interval_95"].__setitem__("lower", 0.1)),
            ("alter upper confidence bound", lambda receipt: receipt["performance_summary"]["confidence_interval_95"].__setitem__("upper", 3.0)),
            ("invent a faster case", lambda receipt: receipt["performance_summary"].__setitem__("faster_case_count", specification["faster"] + 1)),
            ("hide a >20% regression", lambda receipt: receipt["performance_summary"]["all_regressions_over_20_percent"].pop()),
            ("alter dense cohort speed", lambda receipt: receipt["performance_summary"]["cohorts"]["mandatory_literal_dense_same_first_byte"].__setitem__("geomean_speedup", 1.0)),
            ("erase a public case ratio", lambda receipt: receipt["performance_summary"]["case_ratios"].pop("rust-public-profile.v1.0000")),
            ("insert timing-sample mismatch", lambda receipt: receipt["public_416_correctness_gate"].__setitem__("mismatch_count", 1)),
        ):
            reject_context(label + " " + description, lambda value, action=mutate, name=architecture: action(value[name]))

    for label, payload in (
        ("duplicate JSON field", b'{"x":1,"x":2}\n'),
        ("nonfinite JSON", b'{"x":NaN}\n'),
        ("noncanonical JSON", b'{ "x": 1 }\n'),
    ):
        try:
            parse(payload, label)
        except (Rejected, TypeError, ValueError):
            rejected.append(label)
            continue
        raise Rejected("hostile V2 JSON evidence was accepted: " + label)

    for label, before, after in (
        ("hide all-three unqualified warning", b"ALL THREE UNQUALIFIED", b"ALL THREE QUALIFIED!!"),
        ("erase V28 actual speed", b"1.2298384265743338", b"2.2298384265743338"),
        ("erase V28 confidence bound", b"1.1780942933805956", b"0.1780942933805956"),
        ("erase V28 dense result", b"1.9603621849989858", b"0.9603621849989858"),
        ("erase V28 faster cases", b"208 / 416 faster", b"408 / 416 faster"),
        ("erase V28 regressions", b"8 regressions &gt;20% slower", b"0 regressions &gt;20% slower"),
        ("erase shared public failure", b"1,145 / 10,434", b"0,000 / 10,434"),
        ("erase original frozen failures", b"1,352 mismatches", b"0,000 mismatches"),
        ("invent V3 public seed", b"SEED ABSENT", b"SEED EXISTS"),
        ("invent final winner", b"NO WINNER", b"A WINNER!"),
    ):
        require(before in assets[SVG], "self-test graph mutation target disappeared")
        hostile = dict(assets)
        hostile[SVG] = hostile[SVG].replace(before, after, 1)
        try:
            verify_outputs(hostile, assets)
        except (Rejected, KeyError, TypeError, ValueError):
            rejected.append(label)
            continue
        raise Rejected("hostile V2 graph was accepted: " + label)

    forbidden = (
        ("candidate source read", "open", (os.path.join(ROOT, "candidates/rust_candidate.py"), None, os.O_RDONLY | os.O_NOFOLLOW)),
        ("native artifact read", "open", (os.path.join(ROOT, "candidates/_rust_engine.so"), None, os.O_RDONLY | os.O_NOFOLLOW)),
        ("raw public case archive read", "open", (os.path.join(ROOT, "experiments/raw-public.json"), None, os.O_RDONLY | os.O_NOFOLLOW)),
        ("V3 public proposal read", "open", (os.path.join(ROOT, "oracle/phase3/public-proposal-v3.json"), None, os.O_RDONLY | os.O_NOFOLLOW)),
        ("V3 proposal seed read", "open", (os.path.join(ROOT, "oracle/phase3/public-proposal-v3.seed"), None, os.O_RDONLY | os.O_NOFOLLOW)),
        ("changing README read", "open", (os.path.join(ROOT, "README.md"), None, os.O_RDONLY | os.O_NOFOLLOW)),
        ("changing log read", "open", (os.path.join(ROOT, "docs/evidence/current.log"), None, os.O_RDONLY | os.O_NOFOLLOW)),
        ("previous V1 graph mutation", "open", (absolute(V1_SVG.path), None, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW)),
        ("nonexclusive V2 graph mutation", "open", (absolute(SVG), None, os.O_WRONLY | os.O_CREAT)),
        ("symlink-following V28 owner read", "open", (absolute(V28.path), None, os.O_RDONLY)),
        ("candidate worker process", "subprocess.Popen", (PYTHON,)),
        ("native library activation", "ctypes.dlopen", ("_rust_engine.so",)),
        ("timer sample", "time.perf_counter", ()),
        ("network connection", "socket.connect", ("example.invalid",)),
        ("candidate module import", "import", ("candidates.rust_candidate",)),
        ("background thread", "_thread.start_new_thread", ()),
        ("unowned file deletion", "os.remove", (os.path.join(ROOT, "README.md"),)),
    )
    for label, event, arguments in forbidden:
        try:
            wall.check(event, arguments)
        except Rejected:
            rejected.append(label)
            continue
        raise Rejected("hostile V2 source-only effect was accepted: " + label)

    require(
        all(facts["architectures"][name]["candidate_qualified"] is False for name in ARCHITECTURES)
        and facts["v3_public_final_proposal"]["published_seed"] == "ABSENT"
        and facts["winner_selected"] is False,
        "the V2 graph fabricated qualification, proposal seed, or a final winner",
    )
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "rejected_hostile_mutation_count": len(rejected),
        "rejected_hostile_mutations": rejected,
        "candidate_workers_started": 0,
        "native_artifacts_opened": 0,
        "previous_graph_mutations": 0,
        "proposal_files_opened": 0,
        "raw_case_archives_opened": 0,
        "seed_files_opened": 0,
        "timers_sampled": 0,
    }


def publish(path: str, payload: bytes) -> None:
    descriptor = os.open(absolute(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        position = 0
        while position < len(payload):
            count = os.write(descriptor, payload[position:])
            require(count > 0, "exclusive V2 graph publication was interrupted")
            position += count
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
    parser.add_argument("--overview-inputs-sha256")
    for name in ("source", "svg", "inputs", "summary"):
        parser.add_argument("--previous-" + name + "-sha256")
    for name in ARCHITECTURES:
        parser.add_argument("--" + name + "-receipt-sha256")
    for name in ("svg", "inputs", "summary"):
        parser.add_argument("--" + name + "-sha256")
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
            "a public chart renderer cannot import candidate matching engines",
        )
        supplied_owners = (
            (options.original_sha256, ORIGINAL),
            (options.overview_inputs_sha256, OVERVIEW),
            (options.previous_source_sha256, V1_SOURCE),
            (options.previous_svg_sha256, V1_SVG),
            (options.previous_inputs_sha256, V1_INPUTS),
            (options.previous_summary_sha256, V1_SUMMARY),
            *((getattr(options, name + "_receipt_sha256"), ARCHITECTURES[name]["receipt"]) for name in ARCHITECTURES),
        )
        for supplied, owner in supplied_owners:
            require(supplied is None or supplied == owner.sha256, "incorrect public owner fingerprint: " + owner.role)

        mode = "render" if options.render else "verify" if options.verify else "self-test"
        wall = SourceWall(mode)
        sys.addaudithook(wall.check)
        source = read(SELF)
        source_sha256 = digest(source)
        require(options.source_sha256 is None or options.source_sha256 == source_sha256, "incorrect V2 renderer SHA-256")
        require(options.source_bytes is None or options.source_bytes == len(source), "incorrect V2 renderer size")

        payloads = {owner.role: authenticate(owner) for owner in OWNERS}
        context = {
            "original": parse(payloads[ORIGINAL.role], ORIGINAL.role),
            "overview": parse(payloads[OVERVIEW.role], OVERVIEW.role),
            "v1_svg": payloads[V1_SVG.role],
            "v1_inputs": parse(payloads[V1_INPUTS.role], V1_INPUTS.role),
            "v1_summary": parse(payloads[V1_SUMMARY.role], V1_SUMMARY.role),
        }
        for name, specification in ARCHITECTURES.items():
            context[name] = parse(payloads[specification["receipt"].role], specification["receipt"].role)
        facts = validate(context)
        assets = generate(facts, source_sha256, len(source))
        verify_outputs(assets, assets)

        for supplied, path in ((options.svg_sha256, SVG), (options.inputs_sha256, INPUTS), (options.summary_sha256, SUMMARY)):
            require(supplied is None or supplied == digest(assets[path]), "incorrect V2 output fingerprint: " + path)

        if options.render:
            require(
                options.svg_sha256 is None and options.inputs_sha256 is None and options.summary_sha256 is None,
                "new exclusive V2 graph publication cannot presume existing output identities",
            )
            for path in OUTPUTS:
                publish(path, assets[path])
            result = {
                "schema": SCHEMA + "-render",
                "status": "PASS",
                "outputs": {path: {"bytes": len(payload), "sha256": digest(payload)} for path, payload in assets.items()},
                "all_three_candidates_qualified": False,
                "v28_public_speedup": ARCHITECTURES["v28"]["speedup"],
                "winner_selected": False,
            }
        elif options.verify:
            actual = {path: read(path) for path in OUTPUTS}
            verify_outputs(actual, assets)
            result = {
                "schema": SCHEMA + "-verify-frozen-context",
                "status": "PASS",
                "source_sha256": source_sha256,
                "owners_sha256": {owner.role: owner.sha256 for owner in OWNERS},
                "output_sha256": {path: digest(payload) for path, payload in actual.items()},
                "candidate_workers_started": 0,
                "native_artifacts_opened": 0,
                "previous_graph_mutations": 0,
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
        sys.stderr.write("rust architecture comparison V2 rejected: " + str(failure) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
