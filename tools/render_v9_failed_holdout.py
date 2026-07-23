#!/usr/bin/env python3
"""Render only the independently audited, irreversible final-run failure."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from html import escape
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "performance" / "v9" / "evidence"
PREFIX = EVIDENCE / "V9-FINAL-HOLDOUT-24576-FAILURE"
FAILURE = EVIDENCE / "V9-FINAL-HOLDOUT-24576-FAILURE.json"
FAILURE_EVIDENCE_SHA256 = "b3c9ac416d0a748a9fbe4f80f97efefb56ae7f598eea425c614aa278cb177069"
FAILURE_AUDITOR = ROOT / "tools" / "audit_v9_failed_holdout.py"
FAILURE_AUDITOR_SHA256 = "510695deb6f6383fe321f0ae13225034f455011fcb5c22614815c24529b8a822"

SCHEMA = "rebar-v9-sealed-final-holdout-failure-v1"
STATE = "irreversibly-authorized-no-retry"
MARKER_SHA256 = "1df71b41bfdad7e850344242c16dc15c79039b9b925b1fbc709de18cce917cb2"
PARTIAL_RAW_SHA256 = "b93b5318fbd260d0778196f1ab5c668f003647c86b66b015fe369261f72ac53e"
CANDIDATE_FREEZE_SHA256 = "52066760bb4210a57f7b10f13e9ff73e36c53982a5b97aff40ead330c79edf41"
MANIFEST_SHA256 = "d747bfbca78e94b7dada3fdc24acd027fc8cd2e31a46a9441c328fb72153460f"
PROTOCOL_SOURCE_SHA256 = "a699ce1e661ead447af0643584d69f080e72712059ad611fbd6b998f2ca19219"
PROTOCOL_BINDING_SHA256 = "1ebfa3b1a57c285826627e0362c78daff016b4029529639502325550a1ac0aaf"
FROM_SCRATCH_AUDIT_SHA256 = "a790fe1a75c8748df7f8bb6f1e39d0be841636055358aaee94db0aa35523f326"
CASE = "v9.split.literal-and-long-prefix.006"
PHASE = "warmup"
FAILED_MODULE = "candidates.zig_candidate"
FAILURE_MESSAGE = (
    "v9 sealed protocol rejected: pinned CPython result mismatch: "
    "v9.split.literal-and-long-prefix.006:warmup:candidates.zig_candidate"
)
MODULES = (
    "re",
    "candidates.vm_candidate",
    "candidates.rust_candidate",
    "candidates.zig_candidate",
)
NAMES = {
    "re": "Standard Python",
    "candidates.vm_candidate": "C",
    "candidates.rust_candidate": "Rust",
    "candidates.zig_candidate": "Zig",
}
COMPLETE_CASES = 14_342
REQUIRED_CASES = 24_576
OBSERVED_ROWS = 1_778_408
REQUIRED_ROWS = 3_047_424
PAIRED_MODULES = 4
TRIALS = 31
OPERATIONS_PER_SAMPLE = 16
SUFFIXES = ("correctness", "progress", "speed", "memory", "regressions", "rankings")
CANDIDATE_QUALIFICATIONS = (
    {
        "module": "candidates.vm_candidate",
        "full_correctness_campaign_sha256": "a29b540e01fc9f565e01e5cc62af14db30b38d9bacbaf55e4950e95b17c7ea40",
        "deep_contract_sha256": "0b25f1793636eac02d9231b0d5ec546aa6800eab118b0e98f98f5e6276dbb65e",
        "edge_sha256": "c843dccc2d0b8eb1dcada2af282679ca05a1be2de98afc39bad95e7f448f4d7a",
        "native_artifact_sha256": {
            "native-bridge": "f6458cb4bf190f042e7d417a40020d2d58cebcb39671fda7352aab9725a7f633",
            "public-python": "91d848e2627f19e552fef19b9943eb3e265e25537934128875645bab63cf7b80",
        },
    },
    {
        "module": "candidates.rust_candidate",
        "full_correctness_campaign_sha256": "9ddbab81b16f0440ca19bffb8a539ea08d4a7ff33606ee3019eaf85977c2249a",
        "deep_contract_sha256": "f012d5e16305783d70fe6b7ece86a7692b2ac37c310c9a7e12cc856f91e0d1d0",
        "edge_sha256": "c3e67b08ac34540dbbd248b5ffb07161ae7e9b815a6f6bcbc757ef178f7585b1",
        "native_artifact_sha256": {
            "bridge-source": "83afb5a709a6d0ea1701dfd64db30644edbf2cb0276c2db731a8119cfd52d8ed",
            "native-bridge": "1f072e81ba9339a8b2e52a7e93b7bcde791c4d518620b6bd760af67c7c89af34",
            "native-engine": "e7177c97070b2d0073a721044c4d23bb93e0d0883c1f2ccaa07c41eda8b96255",
            "native-source": "4b89d916e4c33e2b516be570ff3e75694f03dcea5eccf9320cedf07471b07dac",
            "public-python": "80812459261edb9585bdf703f137af3e0e788638af2ad7183d00b6d357e8a926",
        },
    },
    {
        "module": "candidates.zig_candidate",
        "full_correctness_campaign_sha256": "4ba7cb9c45a70b747cc0a6eb721f6bb51081157f527d1bf5e578e603715ae5dc",
        "deep_contract_sha256": "422f662f7c01e961ae0e913ed8e1bc1927b80c70530d7982a4a65784bf649a91",
        "edge_sha256": "a4c8b75811b5304ab115fb387f821127a20ed2615e7948ab4b96443dbe1ebe5c",
        "native_artifact_sha256": {
            "native-bridge": "80d7dab57cbee317ee1727862e27cd7dcf4cb22e1a944f4b29f2e4e983f940ed",
            "native-engine": "70bafca56a3f48477b2011f016a81b625e5f40a772af6a986d32b9098269f614",
            "public-python": "95a2010152099f2db61595927542b2f25a675eb72bd33125659969d804360239",
        },
    },
)
FORBIDDEN_RESULTS = frozenset({
    "summary",
    "summary_path",
    "summary_sha256",
    "rankings",
    "ranking",
    "winner",
    "winner_module",
    "geomean_speedup",
    "ci95_low",
    "ci95_high",
    "speed_results",
    "memory_results",
    "final_memory",
    "regressions",
    "regression_count",
})


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as source:
            for block in iter(lambda: source.read(1_048_576), b""):
                digest.update(block)
    except OSError as error:
        raise ValueError(f"cannot verify audited final-failure source: {path}") from error
    return digest.hexdigest()


def read_failure(path: Path) -> dict:
    require(path.resolve() == FAILURE.resolve(), "refusing a substituted final-failure evidence file")
    require(digest_file(path) == FAILURE_EVIDENCE_SHA256, "the unique, independently verified irreversible final-failure evidence changed")
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("cannot read the independently verified final failure") from error
    require(isinstance(result, dict), "final-failure evidence is not an object")
    return result


def check_failure(record: dict, *, check_auditor: bool = True) -> dict:
    require(isinstance(record, dict), "final failure is not a JSON object")
    expected = {
        "schema": SCHEMA,
        "result": "FALSIFIED",
        "auditor_result": "PASS",
        "holdout_state": STATE,
        "retry_permitted": False,
        "auditor_timing_performed": False,
        "partial_timing_performed": True,
        "complete_final_timing": False,
        "final_speed": "NOT MEASURED",
        "complete_final_summary": False,
        "complete_final_ranking_count": 0,
        "final_holdout_unsealed": True,
        "auditor_holdout_opened": False,
        "failed": 1,
        "runner_exit_code": 2,
        "failure_message": FAILURE_MESSAGE,
        "failure_case": CASE,
        "failure_api": "split",
        "failure_round": PHASE,
        "failure_candidate": FAILED_MODULE,
        "marker_sha256": MARKER_SHA256,
        "partial_raw_sha256": PARTIAL_RAW_SHA256,
        "candidate_freeze_sha256": CANDIDATE_FREEZE_SHA256,
        "manifest_sha256": MANIFEST_SHA256,
        "protocol_source_sha256": PROTOCOL_SOURCE_SHA256,
        "protocol_binding_sha256": PROTOCOL_BINDING_SHA256,
        "from_scratch_audit_sha256": FROM_SCRATCH_AUDIT_SHA256,
        "module_order": list(MODULES),
        "observed_raw_rows": OBSERVED_ROWS,
        "required_raw_rows": REQUIRED_ROWS,
        "complete_cases": COMPLETE_CASES,
        "required_cases": REQUIRED_CASES,
        "paired_modules_per_case": PAIRED_MODULES,
        "trials_per_module_case": TRIALS,
        "operations_per_sample": OPERATIONS_PER_SAMPLE,
        "incomplete_case_rows": 0,
        "gzip_valid": True,
        "source_sha256": FAILURE_AUDITOR_SHA256,
        "candidate_qualifications": [dict(row) for row in CANDIDATE_QUALIFICATIONS],
        "rows_by_module": {name: OBSERVED_ROWS // PAIRED_MODULES for name in MODULES},
        "rows_by_round": {str(index): OBSERVED_ROWS // TRIALS for index in range(TRIALS)},
    }
    for field, actual in expected.items():
        require(record.get(field) == actual, f"the independently audited final failure does not prove {field}")
    require(
        COMPLETE_CASES * PAIRED_MODULES * TRIALS == OBSERVED_ROWS,
        "completed final-case and raw-row denominators disagree",
    )
    require(
        REQUIRED_CASES * PAIRED_MODULES * TRIALS == REQUIRED_ROWS,
        "required final-case and raw-row denominators disagree",
    )
    require(COMPLETE_CASES < REQUIRED_CASES, "the failed final run was falsely represented as complete")
    require(OBSERVED_ROWS < REQUIRED_ROWS, "the failed final timing rows were falsely represented as complete")
    require(not (set(record) & FORBIDDEN_RESULTS), "incomplete final data was represented as final speed, memory, rankings, or a winner")
    controls = record.get("self_test")
    require(isinstance(controls, dict) and bool(controls), "the independent final-failure verifier omitted corruption controls")
    require(controls.get("schema") == f"{SCHEMA}-self-test", "the independent final-failure verifier changed its synthetic-control schema")
    require(controls.get("result") == "PASS", "the independent final-failure verifier failed its synthetic controls")
    require(controls.get("synthetic_only") is True, "the independent final-failure controls used live final cases")
    require(controls.get("timing_performed") is False, "the independent final-failure controls performed timing")
    require(controls.get("holdout_opened") is False, "the independent final-failure controls reopened the benchmark")
    count = controls.get("poisoned_control_count")
    poisoned = controls.get("poisoned_controls")
    require(isinstance(count, int) and not isinstance(count, bool) and count >= 20, "the independent failure verifier omitted required poisoned-evidence controls")
    require(isinstance(poisoned, list) and len(poisoned) == count, "the independent failure verifier omitted or duplicated poisoned-evidence controls")
    require(
        all(isinstance(control, dict) and control.get("passed") is True for control in poisoned),
        "an independent final-failure poisoned-evidence control failed",
    )
    source = record.get("source_sha256")
    require(source == FAILURE_AUDITOR_SHA256, "the independently verified final-failure auditor source was substituted")
    if check_auditor:
        require(digest_file(FAILURE_AUDITOR) == source, "the independent final-failure verifier was substituted")
    return record


def opening(width: int, height: int, title: str, subtitle: str) -> list[str]:
    description = (
        "The final benchmark failed and cannot be retried. "
        f"Only {COMPLETE_CASES:,} of {REQUIRED_CASES:,} final cases completed before "
        f"a real Zig split mismatch during warmup. Final speed, confidence, memory, "
        "regressions, rankings, and a winner are not established. "
        f"{subtitle}"
    )
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title, quote=True)}">',
        f"<title>{escape(title)}</title>",
        f"<desc>{escape(description)}</desc>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#172033}.title{font-size:25px;font-weight:760}.sub{font-size:13px;fill:#52627a}.head{font-size:15px;font-weight:720}.label{font-size:12px}.small{font-size:11px;fill:#52627a}.value{font-size:12px;font-weight:720}.banner{font-size:13px;font-weight:750;fill:#991b1b}.panel{fill:#fff7f7;stroke:#fecaca;stroke-width:1}.neutral{fill:#f8fafc;stroke:#e2e8f0;stroke-width:1}.failed{fill:#b91c1c}.unknown{fill:#64748b}.note{font-size:11px;fill:#7f1d1d}</style>',
        f'<text x="26" y="39" class="title">{escape(title)}</text>',
        f'<text x="26" y="63" class="sub">{escape(subtitle)}</text>',
        f'<rect x="20" y="78" width="{width - 40}" height="39" rx="7" fill="#fef2f2" stroke="#fca5a5"/>',
        '<text x="33" y="103" class="banner">FINAL FAILED — NO RETRY — NO COMPLETE SPEED, MEMORY, RANKING, OR WINNER</text>',
    ]


def footer(body: list[str], height: int) -> None:
    body.append(
        f'<text x="26" y="{height - 15}" class="small">'
        'One irreversible, independently audited run; partial measurements cannot establish a final result.'
        '</text>'
    )


def status_panel(body: list[str], *, top: int, name: str, status: str, detail: str, failed: bool = False) -> None:
    width = 1120
    panel_class = "panel" if failed else "neutral"
    colour = "#b91c1c" if failed else "#64748b"
    body.append(f'<rect x="22" y="{top}" width="{width}" height="70" rx="8" class="{panel_class}"/>')
    body.append(f'<text x="40" y="{top + 27}" class="head">{escape(name)}</text>')
    body.append(f'<text x="265" y="{top + 27}" style="font-size:13px;font-weight:750;fill:{colour}">{escape(status)}</text>')
    body.append(f'<text x="265" y="{top + 49}" class="small">{escape(detail)}</text>')


def correctness_chart(_record: dict) -> str:
    width, height = 1180, 603
    body = opening(
        width,
        height,
        "The final compatibility test failed",
        "A real hidden split case disagreed with pinned standard Python during warmup.",
    )
    body.append('<rect x="22" y="139" width="1120" height="105" rx="9" class="panel"/>')
    body.append('<text x="40" y="168" class="head">First observed final mismatch</text>')
    body.append(f'<text x="40" y="193" class="value">Case: {escape(CASE)}</text>')
    body.append('<text x="40" y="215" class="value">Operation: split · phase: warmup · replacement: Zig</text>')
    body.append('<text x="40" y="234" class="note">The runner stopped immediately. Remaining cases were not tested.</text>')
    status_panel(body, top=263, name="Standard Python", status="ORACLE ONLY", detail="Pinned reference; no complete final comparison was produced.")
    status_panel(body, top=342, name="C", status="FINAL QUALIFICATION NOT ESTABLISHED", detail="The final correctness campaign stopped before all 24,576 cases completed.")
    status_panel(body, top=421, name="Rust", status="FINAL QUALIFICATION NOT ESTABLISHED", detail="The final correctness campaign stopped before all 24,576 cases completed.")
    status_panel(body, top=500, name="Zig", status="FINAL MISMATCH OBSERVED", detail="The hidden split case disagreed with standard Python during warmup.", failed=True)
    footer(body, height)
    return "\n".join((*body, "</svg>", ""))


def progress_chart(_record: dict) -> str:
    width, height = 1180, 459
    body = opening(
        width,
        height,
        "How far the failed final run progressed",
        "Only completed, independently verified cases and paired timing rows are counted.",
    )
    case_left, case_width = 42, 1000
    completed_width = case_width * COMPLETE_CASES / REQUIRED_CASES
    incomplete_cases = REQUIRED_CASES - COMPLETE_CASES
    incomplete_rows = REQUIRED_ROWS - OBSERVED_ROWS
    body.append('<text x="42" y="156" class="head">Completed final cases</text>')
    body.append(f'<rect x="{case_left}" y="171" width="{case_width}" height="27" rx="4" fill="#fee2e2"/>')
    body.append(f'<rect x="{case_left}" y="171" width="{completed_width:.2f}" height="27" rx="4" fill="#64748b"/>')
    body.append(f'<text x="{case_left}" y="221" class="value">{COMPLETE_CASES:,}/{REQUIRED_CASES:,} completed · {incomplete_cases:,} never completed</text>')
    body.append(f'<text x="{case_left}" y="241" class="small">The failed case produced no partial paired timing rows.</text>')
    body.append('<text x="42" y="287" class="head">Complete paired timing rows</text>')
    body.append(f'<rect x="{case_left}" y="302" width="{case_width}" height="27" rx="4" fill="#fee2e2"/>')
    body.append(f'<rect x="{case_left}" y="302" width="{case_width * OBSERVED_ROWS / REQUIRED_ROWS:.2f}" height="27" rx="4" fill="#64748b"/>')
    body.append(f'<text x="{case_left}" y="352" class="value">{OBSERVED_ROWS:,}/{REQUIRED_ROWS:,} recorded · {incomplete_rows:,} required rows missing</text>')
    body.append(f'<text x="{case_left}" y="375" class="small">{PAIRED_MODULES} modules × {TRIALS} rounds per completed case; no complete {REQUIRED_CASES:,}-case result exists.</text>')
    footer(body, height)
    return "\n".join((*body, "</svg>", ""))


def speed_chart(_record: dict) -> str:
    width, height = 1180, 498
    body = opening(
        width,
        height,
        "Final speed and confidence: not established",
        "The run recorded partial timings, but it did not complete the frozen final protocol.",
    )
    status_panel(body, top=145, name="Standard Python", status="REFERENCE ONLY", detail="No complete, candidate-versus-Python final comparison exists.")
    for index, module in enumerate(MODULES[1:]):
        status_panel(
            body,
            top=224 + index * 79,
            name=NAMES[module],
            status="FINAL SPEED NOT ESTABLISHED",
            detail="No complete geometric speed, 95% confidence interval, or final case-win count.",
        )
    footer(body, height)
    return "\n".join((*body, "</svg>", ""))


def memory_chart(_record: dict) -> str:
    width, height = 1180, 429
    body = opening(
        width,
        height,
        "Final memory: not established",
        "The required final memory campaign did not finish; no native or whole-process comparison is available.",
    )
    for index, module in enumerate(MODULES[1:]):
        status_panel(
            body,
            top=146 + index * 79,
            name=NAMES[module],
            status="FINAL MEMORY NOT ESTABLISHED",
            detail="No completed isolated native-engine, total-process, or final memory measurement.",
        )
    body.append('<text x="38" y="399" class="small">Earlier public-practice Python-traced memory remains historical; it is not a final native-memory result.</text>')
    return "\n".join((*body, "</svg>", ""))


def regressions_chart(_record: dict) -> str:
    width, height = 1180, 438
    body = opening(
        width,
        height,
        "Final timing regressions: not established",
        "An incomplete 24,576-case final run cannot establish candidate slowdown totals.",
    )
    for index, module in enumerate(MODULES[1:]):
        status_panel(
            body,
            top=146 + index * 79,
            name=NAMES[module],
            status="FINAL REGRESSIONS NOT ESTABLISHED",
            detail="No complete final-case denominator or more-than-20%-slower total exists.",
        )
    body.append('<text x="38" y="404" class="small">The observed Zig split error is a correctness failure, not a measured performance regression.</text>')
    footer(body, height)
    return "\n".join((*body, "</svg>", ""))


def rankings_chart(_record: dict) -> str:
    width, height = 1180, 500
    body = opening(
        width,
        height,
        "Final rankings and winner: not established",
        "No candidate completed the final correctness and performance qualification.",
    )
    status_panel(body, top=145, name="Standard Python", status="REFERENCE ONLY", detail="The pinned oracle was not assigned a fabricated final score or rank.")
    for index, module in enumerate(MODULES[1:]):
        status_panel(
            body,
            top=224 + index * 79,
            name=NAMES[module],
            status="NOT RANKED · NOT ESTABLISHED",
            detail="No complete final correctness pass, speed, confidence range, or winner.",
        )
    body.append(
        f'<text x="28" y="{height - 31}" class="note">'
        'FINAL WINNER NOT ESTABLISHED — no candidate completed the final qualification.'
        '</text>'
    )
    footer(body, height)
    return "\n".join((*body, "</svg>", ""))


def build_charts(record: dict) -> dict[str, str]:
    graphs = {
        "correctness": correctness_chart(record),
        "progress": progress_chart(record),
        "speed": speed_chart(record),
        "memory": memory_chart(record),
        "regressions": regressions_chart(record),
        "rankings": rankings_chart(record),
    }
    require(tuple(graphs) == SUFFIXES, "a required independent final-failure graph was omitted")
    for suffix, graph in graphs.items():
        require("FINAL FAILED" in graph and "NO RETRY" in graph, f"the {suffix} graph concealed the irreversible final failure")
        require("NOT ESTABLISHED" in graph or suffix == "progress", f"the {suffix} graph implied a successful final result")
        require(f"{REQUIRED_CASES:,}" in graph, f"the {suffix} graph omitted the full final-case denominator")
        try:
            ElementTree.fromstring(graph)
        except ElementTree.ParseError as error:
            raise ValueError(f"invalid final-failure SVG: {suffix}") from error
    require(CASE in graphs["correctness"], "the exact failing hidden-case identity was omitted")
    require(f"{COMPLETE_CASES:,}/{REQUIRED_CASES:,}" in graphs["progress"], "the exact completed case count was omitted")
    require(f"{OBSERVED_ROWS:,}/{REQUIRED_ROWS:,}" in graphs["progress"], "the exact completed timing-row count was omitted")
    for suffix in ("correctness", "speed", "memory", "regressions", "rankings"):
        for module in MODULES[1:]:
            require(escape(NAMES[module]) in graphs[suffix], f"the {suffix} graph omitted {NAMES[module]}")
    return graphs


def synthetic_record() -> dict:
    return {
        "schema": SCHEMA,
        "result": "FALSIFIED",
        "auditor_result": "PASS",
        "holdout_state": STATE,
        "retry_permitted": False,
        "auditor_timing_performed": False,
        "partial_timing_performed": True,
        "complete_final_timing": False,
        "final_speed": "NOT MEASURED",
        "complete_final_summary": False,
        "complete_final_ranking_count": 0,
        "final_holdout_unsealed": True,
        "auditor_holdout_opened": False,
        "failed": 1,
        "runner_exit_code": 2,
        "failure_message": FAILURE_MESSAGE,
        "failure_case": CASE,
        "failure_api": "split",
        "failure_round": PHASE,
        "failure_candidate": FAILED_MODULE,
        "marker_sha256": MARKER_SHA256,
        "partial_raw_sha256": PARTIAL_RAW_SHA256,
        "candidate_freeze_sha256": CANDIDATE_FREEZE_SHA256,
        "manifest_sha256": MANIFEST_SHA256,
        "protocol_source_sha256": PROTOCOL_SOURCE_SHA256,
        "protocol_binding_sha256": PROTOCOL_BINDING_SHA256,
        "from_scratch_audit_sha256": FROM_SCRATCH_AUDIT_SHA256,
        "module_order": list(MODULES),
        "observed_raw_rows": OBSERVED_ROWS,
        "required_raw_rows": REQUIRED_ROWS,
        "complete_cases": COMPLETE_CASES,
        "required_cases": REQUIRED_CASES,
        "paired_modules_per_case": PAIRED_MODULES,
        "trials_per_module_case": TRIALS,
        "operations_per_sample": OPERATIONS_PER_SAMPLE,
        "incomplete_case_rows": 0,
        "gzip_valid": True,
        "source_sha256": FAILURE_AUDITOR_SHA256,
        "candidate_qualifications": [dict(row) for row in CANDIDATE_QUALIFICATIONS],
        "rows_by_module": {name: OBSERVED_ROWS // PAIRED_MODULES for name in MODULES},
        "rows_by_round": {str(index): OBSERVED_ROWS // TRIALS for index in range(TRIALS)},
        "self_test": {
            "schema": f"{SCHEMA}-self-test",
            "result": "PASS",
            "synthetic_only": True,
            "timing_performed": False,
            "holdout_opened": False,
            "poisoned_control_count": 20,
            "poisoned_controls": [
                {"name": f"synthetic-failure-control-{index:02d}", "passed": True}
                for index in range(20)
            ],
        },
    }


def expect_rejection(record: dict, key: str, value: object, label: str) -> None:
    corrupted = copy.deepcopy(record)
    corrupted[key] = value
    try:
        check_failure(corrupted, check_auditor=False)
    except (ValueError, TypeError, KeyError, OverflowError):
        return
    raise ValueError(f"synthetic final-failure evidence incorrectly accepted {label}")


def self_test() -> None:
    record = synthetic_record()
    check_failure(record, check_auditor=False)
    cases = (
        ("schema", "rebar-v9-sealed-final-holdout-success-v1", "substituted success schema"),
        ("result", "PASS", "invented successful final result"),
        ("result", "QUALIFIED", "invented final candidate qualification"),
        ("auditor_result", "FAIL", "concealed independent failure-auditor failure"),
        ("holdout_state", "retry-permitted", "unauthorized final retry"),
        ("retry_permitted", True, "unauthorized final re-opening"),
        ("auditor_timing_performed", True, "failure verifier executes a timing run"),
        ("partial_timing_performed", False, "concealed genuine partial final timing"),
        ("complete_final_timing", True, "fabricated completed final timing"),
        ("final_speed", "1.5x", "fabricated complete final speed"),
        ("complete_final_summary", True, "fabricated complete final summary"),
        ("complete_final_ranking_count", 1, "fabricated complete final ranking"),
        ("final_holdout_unsealed", False, "concealed irreversible final opening"),
        ("auditor_holdout_opened", True, "failure auditor reopens final holdout"),
        ("failed", 0, "concealed correctness failure"),
        ("runner_exit_code", 0, "fabricated passing final exit"),
        ("failure_message", "success", "changed actual final failure"),
        ("failure_case", "v9.other.case", "concealed failing split case"),
        ("failure_api", "search", "concealed failing split operation"),
        ("failure_round", "timed", "concealed warmup mismatch"),
        ("failure_candidate", "candidates.rust_candidate", "substituted failing candidate"),
        ("marker_sha256", "0" * 64, "substituted irreversible marker"),
        ("partial_raw_sha256", "0" * 64, "substituted partial timing record"),
        ("candidate_freeze_sha256", "0" * 64, "substituted candidate freeze"),
        ("manifest_sha256", "0" * 64, "substituted frozen manifest"),
        ("protocol_source_sha256", "0" * 64, "substituted frozen protocol source"),
        ("protocol_binding_sha256", "0" * 64, "substituted protocol binding"),
        ("from_scratch_audit_sha256", "0" * 64, "substituted source independence audit"),
        ("module_order", list(reversed(MODULES)), "substituted final candidate order"),
        ("candidate_qualifications", [], "concealed the frozen candidate qualifications"),
        ("rows_by_module", {}, "concealed complete paired rows by final module"),
        ("rows_by_round", {}, "concealed complete paired rows by final round"),
        ("observed_raw_rows", REQUIRED_ROWS, "invented complete final timing rows"),
        ("required_raw_rows", OBSERVED_ROWS, "silently reduced final timing denominator"),
        ("complete_cases", REQUIRED_CASES, "invented completed final run"),
        ("required_cases", COMPLETE_CASES, "silently reduced final-case denominator"),
        ("paired_modules_per_case", 3, "dropped a final replacement"),
        ("trials_per_module_case", 30, "dropped a frozen paired round"),
        ("operations_per_sample", 15, "silently changed frozen final operations per sample"),
        ("incomplete_case_rows", 1, "fabricated incomplete-case observations"),
        ("gzip_valid", False, "invalidated actual partial raw archive"),
        ("source_sha256", "0", "invalid independent failure-auditor identity"),
        ("self_test", {}, "removed independent failure-auditor controls"),
    )
    for key, value, label in cases:
        expect_rejection(record, key, value, label)
    for key in sorted(FORBIDDEN_RESULTS):
        expect_rejection(record, key, 1, f"fabricated incomplete final result: {key}")

    graphs = build_charts(record)
    require(build_charts(record) == graphs, "final-failure SVG graphs are not deterministic")
    require("NOT RANKED" in graphs["rankings"], "failed candidates were falsely ranked")
    require("NOT ESTABLISHED" in graphs["speed"], "an incomplete final speed was fabricated")
    require("NOT ESTABLISHED" in graphs["memory"], "an incomplete final memory result was fabricated")
    require("NOT ESTABLISHED" in graphs["regressions"], "an incomplete final slowdown count was fabricated")
    print(json.dumps({
        "schema": f"{SCHEMA}-charts-self-test",
        "result": "PASS",
        "synthetic_only": True,
        "timing_performed": False,
        "retry_permitted": False,
        "opening_accessed": False,
        "raw_accessed": False,
        "failure_controls": len(cases),
        "fabricated_result_controls": len(FORBIDDEN_RESULTS),
        "poisoned_control_count": len(cases) + len(FORBIDDEN_RESULTS),
        "chart_count": len(SUFFIXES),
        "charts_deterministic": True,
        "final_result": "FAILED — NOT ESTABLISHED",
    }, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render six honest graphs from the one irreversible, independently audited failed final run.")
    parser.add_argument("--failure", type=Path, default=FAILURE, help="the actual independently audited failed-final-run JSON")
    parser.add_argument("--prefix", type=Path, default=PREFIX, help="the unique audited-failure SVG prefix")
    parser.add_argument("--self-test", action="store_true", help="run synthetic-only final-failure integrity controls")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
        return

    prefix = args.prefix.resolve()
    require(prefix == PREFIX.resolve(), "refusing to overwrite original final graphs or unrelated evidence")
    require(prefix.parent == EVIDENCE.resolve(), "refusing to write outside final-failure evidence")
    document = check_failure(read_failure(args.failure.resolve()))
    graphs = build_charts(document)
    destinations = tuple(prefix.parent / f"{prefix.name}-{suffix}.svg" for suffix in SUFFIXES)
    require(all(not path.exists() for path in destinations), "refusing to overwrite an existing irreversible final-failure graph")
    for suffix, path in zip(SUFFIXES, destinations, strict=True):
        with path.open("x", encoding="utf-8") as destination:
            destination.write(graphs[suffix])
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
