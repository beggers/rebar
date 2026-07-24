#!/usr/bin/env python3
"""Render only an explicitly frozen, audited 8,192-case public comparison."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from tools import postfinal_public_practice_charts_v2 as original


ROOT = Path(__file__).resolve().parent.parent
PUBLIC_ROOT = ROOT / "performance" / "postfinal-public-v4"
EVIDENCE = PUBLIC_ROOT / "evidence"
MANIFEST = PUBLIC_ROOT / "manifest.json"
PREFIX = "postfinal-public-practice-v4"
SUMMARY = EVIDENCE / f"{PREFIX}-summary.json"
INTEGRITY = EVIDENCE / f"{PREFIX}-integrity.json"
PUBLIC_RAW = EVIDENCE / f"{PREFIX}-raw.jsonl.gz"

PLAN_SCHEMA = "rebar-rust-balanced-calibration-plan-v7"
PLAN_POSTFINAL_SCHEMA = "rebar-postfinal-public-practice-plan-v4"
SUMMARY_SCHEMA = "rebar-rust-balanced-calibration-pilot-v7"
SUMMARY_POSTFINAL_SCHEMA = "rebar-postfinal-public-practice-report-v4"
INTEGRITY_SCHEMA = "rebar-postfinal-public-practice-integrity-v4"

MODULES = (
    "re",
    "candidates.rust_candidate",
    "candidates.vm_candidate",
    "candidates.zig_candidate",
)
CANDIDATES = MODULES[1:]
CASES = 8_192
TRIALS = 13
WARMUPS = 4
BOOTSTRAPS = 2_000
CATEGORY_COUNT = 260
SOURCE_PUBLIC_CASES = 10_312
ELIGIBLE_PUBLIC_CASES = 9_731
MAX_OPERATIONS = 16
RAW_ROWS = CASES * TRIALS * len(MODULES)
CORRECTNESS_GATES = RAW_ROWS * 3
CONFIDENCE_INTERVALS = CASES * len(CANDIDATES) + len(CANDIDATES)
SOURCE_CONTROL_COUNT = 76
NATIVE_LIBRARY_COUNT = 5
NO_DELEGATION_CONTROL_COUNT = 32
ISOLATED_WORKER_COUNT = len(MODULES)
RUNTIME_GUARD_CHECKS = len(MODULES) * (2 + 2 * CASES)
SELECTION_SEED = 2_026_072_404
ORDER_SEED = 2_026_072_405
BOOTSTRAP_SEED = 2_026_072_406
SUFFIXES = (
    "overall",
    "outcomes",
    "api",
    "regressions",
    "memory",
    "rankings",
)
BOUNDED_API_CAPACITIES = {
    "compile": 210,
    "escape": 161,
    "findall": 2_882,
    "finditer": 2_738,
    "fullmatch": 358,
    "match": 229,
    "match-surface": 241,
    "scanner": 427,
    "search": 1_057,
    "split": 451,
    "sub": 447,
    "subn": 530,
}
EDGE_PROOF_PATHS = {
    "candidates.rust_candidate": str(
        ROOT
        / "candidates"
        / "evidence"
        / "rust-v7-edge-oracle-rust-post-final-stage-05-universal-parity.json.gz"
    ),
    "candidates.vm_candidate": str(
        ROOT
        / "candidates"
        / "evidence"
        / "rust-v7-edge-oracle-vm-post-final-stage-05-universal-parity.json.gz"
    ),
    "candidates.zig_candidate": str(
        ROOT
        / "candidates"
        / "evidence"
        / "rust-v7-edge-oracle-zig-post-final-stage-05-universal-parity.json.gz"
    ),
}
NO_DELEGATION_AUDIT_PATH = str(
    ROOT / "candidates" / "audits" / "POSTFINAL-NO-DELEGATION-AUDIT-V1.json"
)
NO_DELEGATION_SOURCE_PATH = str(
    ROOT / "tools" / "postfinal_no_delegation_audit_v1.py"
)
NO_DELEGATION_SCHEMA = "rebar-postfinal-no-delegation-audit-v1"
ORIGINAL_AUDIT_SOURCE_PATH = str(ROOT / "tools" / "audit_from_scratch.py")
UNIVERSAL_ORACLE_SOURCE_PATH = str(
    ROOT / "tools" / "python_re_universal_public_oracle_stage03.py"
)
UNIVERSAL_ORACLE_SOURCE_SHA256 = (
    "477c3f7e9955a9207b9345fc281705b6d643446b5d5c933009fa22a64b8d44ce"
)
UNIVERSAL_ORACLE_FROZEN_SOURCE_PATH = str(
    ROOT / "tools" / "python_re_universal_public_oracle_v1.py"
)
UNIVERSAL_ORACLE_REPORT_PATH = str(
    ROOT
    / "candidates"
    / "evidence"
    / "python-re-universal-public-oracle-v3-all.json"
)
UNIVERSAL_ORACLE_SCHEMA = "rebar-python-re-universal-public-oracle-v1"
UNIVERSAL_ORACLE_CANDIDATES = ["rust", "vm", "zig"]
UNIVERSAL_ORACLE_COMPARISONS_PER_CASE = 48
UNIVERSAL_ORACLE_COMPARISONS_PER_CANDIDATE = (
    CASES * UNIVERSAL_ORACLE_COMPARISONS_PER_CASE
)
UNIVERSAL_ORACLE_TOTAL_COMPARISONS = (
    UNIVERSAL_ORACLE_COMPARISONS_PER_CANDIDATE * len(CANDIDATES)
)
UNIVERSAL_ORACLE_SEED = 2_026_072_417
UNIVERSAL_ORACLE_SEED_DOMAIN = "rebar/python-re/universal-public/v1"
UNIVERSAL_ORACLE_GRAMMAR_FAMILIES = 16
UNIVERSAL_ORACLE_INPUT_STRATA = 16
UNIVERSAL_ORACLE_EXAMPLES_PER_STRATUM = 32
SUMMARY_ROLE = (
    "additive expanded public practice only; not a held-out or final result"
)
INTEGRITY_MEASUREMENT = (
    "independent replay of isolated expanded public practice; "
    "not a final or held-out result"
)
EXECUTION_TOPOLOGY = (
    "four persistent process-isolated engines; one pinned CPython baseline "
    "worker and one permanently guarded worker for each native candidate"
)
RUNTIME_NATIVE_HASH_POLICY = (
    "Force a complete SHA-256 of each actually mapped owned native ELF before "
    "the first case and after the last case; inspect /proc/self/maps, forbidden "
    "module reachability, native role identities, and exact file stat tuples "
    "before and after every case; reuse an already verified digest only while "
    "device, inode, size, nanosecond mtime, and nanosecond ctime remain "
    "unchanged. A malicious metadata-preserving change between the forced "
    "full hashes is not cryptographically ruled out."
)
EXECUTION_SAFETY = (
    "Candidate-free paired controller; no shared baseline or cross-candidate "
    "interpreter; additive-audited import, reachable-regex, and native-loader "
    "guards; independently checked loaded native mappings before and after "
    "every frozen public case; exact pre-sample, allocation-sample, and "
    "post-timing CPython-answer gates for every paired observation."
)
ISOLATED_MEMORY_LIMITATION = (
    "Tracemalloc reports Python-visible temporary allocations. "
    "RSS and high-water marks are process-level observations in "
    "separate dedicated engine workers; they do not establish exact "
    "per-allocation native-engine memory."
)
STAGE05_ARTIFACT_PATHS = {
    f"{family}-edge": (
        "candidates/evidence/"
        f"rust-v7-edge-oracle-{family}-post-final-stage-05-universal-parity.json.gz"
    )
    for family in ("rust", "vm", "zig")
}
STAGE05_ARTIFACT_PATHS.update(
    {
        f"{family}-deep-public-contract": (
            "candidates/audits/"
            f"RUST-V8-DEEP-CONTRACT-"
            f"{'C' if family == 'vm' else family.upper()}-POST-FINAL-"
            "STAGE-05-UNIVERSAL-PARITY.json.gz"
        )
        for family in ("rust", "vm", "zig")
    }
)
STAGE05_ARTIFACT_PATHS.update(
    {
        f"{family}-observability": (
            "candidates/evidence/"
            f"rust-v8-observability-{family}-qualified-post-final-"
            "stage-05-universal-parity.json.gz"
        )
        for family in ("rust", "vm", "zig")
    }
)
STAGE05_ARTIFACT_PATHS.update(
    {
        f"{family}-complete-correctness-campaign": (
            "candidates/evidence/"
            f"rust-v8-{family}-post-final-stage-05-universal-parity-"
            "sealed-campaign.json"
        )
        for family in ("rust", "vm", "zig")
    }
)

require = original.require
valid_sha256 = original.valid_sha256
base = original.original


def require_public_quotas(value: object) -> dict[str, int]:
    require(isinstance(value, dict), "the frozen public operation quotas are missing")
    require(
        set(value) == set(BOUNDED_API_CAPACITIES),
        "the expanded public comparison omitted one of its 12 operations",
    )
    quotas: dict[str, int] = {}
    for name, capacity in BOUNDED_API_CAPACITIES.items():
        quota = value.get(name)
        require(
            type(quota) is int and 0 < quota <= capacity,
            f"the expanded public {name} quota exceeds bounded calibration cases",
        )
        quotas[name] = quota
    require(
        sum(quotas.values()) == CASES,
        "the selected public cases do not total exactly 8,192",
    )
    require(
        sum(BOUNDED_API_CAPACITIES.values()) == ELIGIBLE_PUBLIC_CASES,
        "the bounded public calibration pool no longer contains 9,731 cases",
    )
    return quotas


def require_audit_binding(document: object, *, reference: dict | None = None) -> None:
    require(isinstance(document, dict), "the public no-delegation binding is missing")
    expected = {
        "postfinal_no_delegation_audit_path": NO_DELEGATION_AUDIT_PATH,
        "postfinal_no_delegation_audit_source_path": NO_DELEGATION_SOURCE_PATH,
        "postfinal_no_delegation_audit_schema": NO_DELEGATION_SCHEMA,
    }
    for key, value in expected.items():
        require(
            document.get(key) == value,
            f"the expanded public {key} is missing or substituted",
        )
    for key in (
        "postfinal_no_delegation_audit_sha256",
        "postfinal_no_delegation_audit_source_sha256",
    ):
        require(valid_sha256(document.get(key)), f"the expanded public {key} is invalid")
    count = document.get("postfinal_no_delegation_control_count")
    require(
        type(count) is int and count == NO_DELEGATION_CONTROL_COUNT,
        "the independently verified 32 no-delegation controls are incomplete",
    )
    require(
        document.get("from_scratch_audit_source_path")
        == ORIGINAL_AUDIT_SOURCE_PATH,
        "the original 76-control audit source was substituted",
    )
    require(
        valid_sha256(document.get("from_scratch_audit_source_sha256")),
        "the original 76-control audit source fingerprint is missing",
    )
    require(
        valid_sha256(document.get("from_scratch_audit_sha256")),
        "the original 76-control independence report fingerprint is missing",
    )
    if reference is not None:
        for key in (
            "from_scratch_audit_sha256",
            "from_scratch_audit_source_path",
            "from_scratch_audit_source_sha256",
            "postfinal_no_delegation_audit_path",
            "postfinal_no_delegation_audit_sha256",
            "postfinal_no_delegation_audit_source_path",
            "postfinal_no_delegation_audit_source_sha256",
            "postfinal_no_delegation_audit_schema",
            "postfinal_no_delegation_control_count",
        ):
            require(
                document.get(key) == reference.get(key),
                f"the expanded public replay changed {key}",
            )


def require_universal_oracle(
    document: object,
    *,
    reference: dict | None = None,
) -> None:
    require(
        isinstance(document, dict),
        "the complete all-candidate Python compatibility proof is missing",
    )
    expected = {
        "python_re_universal_oracle_source_path": UNIVERSAL_ORACLE_SOURCE_PATH,
        "python_re_universal_oracle_source_sha256": (
            UNIVERSAL_ORACLE_SOURCE_SHA256
        ),
        "python_re_universal_oracle_frozen_source_path": (
            UNIVERSAL_ORACLE_FROZEN_SOURCE_PATH
        ),
        "python_re_universal_oracle_report_path": UNIVERSAL_ORACLE_REPORT_PATH,
        "python_re_universal_oracle_schema": UNIVERSAL_ORACLE_SCHEMA,
        "python_re_universal_oracle_status": "PASS",
        "python_re_universal_oracle_selected": "all",
        "python_re_universal_oracle_mismatches": 0,
        "python_re_universal_oracle_cases": CASES,
        "python_re_universal_oracle_comparisons_per_case": (
            UNIVERSAL_ORACLE_COMPARISONS_PER_CASE
        ),
        "python_re_universal_oracle_comparisons_per_candidate": (
            UNIVERSAL_ORACLE_COMPARISONS_PER_CANDIDATE
        ),
        "python_re_universal_oracle_total_comparisons": (
            UNIVERSAL_ORACLE_TOTAL_COMPARISONS
        ),
        "python_re_universal_oracle_candidates": UNIVERSAL_ORACLE_CANDIDATES,
        "python_re_universal_oracle_seed": UNIVERSAL_ORACLE_SEED,
        "python_re_universal_oracle_seed_domain": UNIVERSAL_ORACLE_SEED_DOMAIN,
        "python_re_universal_oracle_grammar_family_count": (
            UNIVERSAL_ORACLE_GRAMMAR_FAMILIES
        ),
        "python_re_universal_oracle_input_stratum_count": (
            UNIVERSAL_ORACLE_INPUT_STRATA
        ),
        "python_re_universal_oracle_examples_per_stratum": (
            UNIVERSAL_ORACLE_EXAMPLES_PER_STRATUM
        ),
    }
    for key, value in expected.items():
        require(
            document.get(key) == value
            and type(document.get(key)) is type(value),
            f"the complete all-candidate Python compatibility {key} changed",
        )
    digest_keys = (
        "python_re_universal_oracle_source_sha256",
        "python_re_universal_oracle_frozen_source_sha256",
        "python_re_universal_oracle_report_sha256",
        "python_re_universal_oracle_case_sha256",
        "python_re_universal_oracle_original_audit_sha256",
        "python_re_universal_oracle_postfinal_no_delegation_audit_sha256",
    )
    for key in digest_keys:
        require(
            valid_sha256(document.get(key)),
            f"the complete all-candidate Python compatibility {key} is missing",
        )
    require(
        document["python_re_universal_oracle_original_audit_sha256"]
        == document.get("from_scratch_audit_sha256"),
        "the all-candidate Python proof substitutes the original source audit",
    )
    require(
        document["python_re_universal_oracle_postfinal_no_delegation_audit_sha256"]
        == document.get("postfinal_no_delegation_audit_sha256"),
        "the all-candidate Python proof substitutes the no-delegation audit",
    )
    require(
        UNIVERSAL_ORACLE_GRAMMAR_FAMILIES
        * UNIVERSAL_ORACLE_INPUT_STRATA
        * UNIVERSAL_ORACLE_EXAMPLES_PER_STRATUM
        == CASES,
        "the complete Python proof does not cover all 8,192 public cases",
    )
    if reference is not None:
        for key in (*expected, *digest_keys):
            require(
                document.get(key) == reference.get(key),
                f"the independently replayed universal Python proof changed {key}",
            )


def require_stage05_artifacts(
    document: object,
    *,
    reference: dict | None = None,
) -> None:
    require(isinstance(document, dict), "the stage-05 correctness proofs are missing")
    artifacts = document.get("stage05_correctness_artifacts")
    require(
        isinstance(artifacts, list)
        and len(artifacts) == len(STAGE05_ARTIFACT_PATHS)
        and len(artifacts) == len(CANDIDATES) * 4,
        "one of the 12 independent stage-05 correctness proofs is missing",
    )
    seen: set[str] = set()
    for artifact in artifacts:
        require(isinstance(artifact, dict), "invalid stage-05 correctness proof")
        role = artifact.get("role")
        require(
            role in STAGE05_ARTIFACT_PATHS and role not in seen,
            "a stage-05 correctness proof is substituted or duplicated",
        )
        require(
            artifact.get("path") == STAGE05_ARTIFACT_PATHS[role],
            "a stage-05 correctness proof escaped its exact frozen path",
        )
        require(
            valid_sha256(artifact.get("sha256")),
            "a stage-05 correctness proof has no valid SHA-256",
        )
        seen.add(role)
    if reference is not None:
        require(
            artifacts == reference.get("stage05_correctness_artifacts"),
            "the expanded public replay changed a frozen stage-05 proof",
        )


def require_worker_topology(
    document: object,
    *,
    reference: dict | None = None,
    measured: bool,
) -> None:
    require(isinstance(document, dict), "the isolated worker proof is missing")
    expected = {
        "execution_topology": EXECUTION_TOPOLOGY,
        "runtime_native_hash_policy": RUNTIME_NATIVE_HASH_POLICY,
        "execution_safety": EXECUTION_SAFETY,
    }
    for key, value in expected.items():
        require(
            document.get(key) == value,
            f"the isolated public-worker {key} was omitted or misrepresented",
        )
        if reference is not None:
            require(
                document[key] == reference.get(key),
                f"the expanded public replay changed its frozen {key}",
            )
    if measured:
        exact = {
            "persistent_isolated_worker_count": ISOLATED_WORKER_COUNT,
            "per_case_runtime_guard_checks": RUNTIME_GUARD_CHECKS,
            "controller_candidate_imported": False,
        }
        for key, value in exact.items():
            require(
                document.get(key) == value
                and type(document.get(key)) is type(value),
                f"the expanded public replay omits its genuine {key}",
            )
    else:
        for key, value in (
            ("persistent_isolated_worker_count", ISOLATED_WORKER_COUNT),
            ("per_case_runtime_guard_checks", RUNTIME_GUARD_CHECKS),
            ("controller_candidate_imported", False),
        ):
            if key in document:
                require(
                    document[key] == value and type(document[key]) is type(value),
                    f"the frozen public plan misstates its {key}",
                )


@contextmanager
def v4_renderer(
    *,
    manifest_sha256: str,
    runner_sha256: str,
    public_operations: dict[str, int],
) -> Iterator[None]:
    """Reuse proven public graphs while restoring every inherited constant."""

    original.require_candidate_free()
    require(valid_sha256(manifest_sha256), "an explicit frozen public manifest SHA-256 is required")
    require(valid_sha256(runner_sha256), "the frozen public runner SHA-256 is missing")
    quotas = require_public_quotas(public_operations)
    require(original.MODULES == MODULES, "the four frozen public engines changed")
    require(original.CANDIDATES == CANDIDATES, "the frozen native engines changed")
    require(original.SUFFIXES == SUFFIXES, "a required public graph changed")
    base_api_counts = base.API_COUNTS
    updates = {
        "PUBLIC_ROOT": PUBLIC_ROOT,
        "EVIDENCE": EVIDENCE,
        "MANIFEST": MANIFEST,
        "MANIFEST_SHA256": manifest_sha256,
        "RUNNER_SHA256": runner_sha256,
        "PREFIX": PREFIX,
        "SUMMARY": SUMMARY,
        "INTEGRITY": INTEGRITY,
        "PUBLIC_RAW": PUBLIC_RAW,
        "PLAN_SCHEMA": PLAN_SCHEMA,
        "PLAN_POSTFINAL_SCHEMA": PLAN_POSTFINAL_SCHEMA,
        "SUMMARY_SCHEMA": SUMMARY_SCHEMA,
        "SUMMARY_POSTFINAL_SCHEMA": SUMMARY_POSTFINAL_SCHEMA,
        "INTEGRITY_SCHEMA": INTEGRITY_SCHEMA,
        "SUMMARY_ROLE": SUMMARY_ROLE,
        "INTEGRITY_MEASUREMENT": INTEGRITY_MEASUREMENT,
        "CASES": CASES,
        "TRIALS": TRIALS,
        "WARMUPS": WARMUPS,
        "BOOTSTRAPS": BOOTSTRAPS,
        "CATEGORY_COUNT": CATEGORY_COUNT,
        "SOURCE_PUBLIC_CASES": SOURCE_PUBLIC_CASES,
        "ELIGIBLE_PUBLIC_CASES": ELIGIBLE_PUBLIC_CASES,
        "MAX_OPERATIONS": MAX_OPERATIONS,
        "RAW_ROWS": RAW_ROWS,
        "CORRECTNESS_GATES": CORRECTNESS_GATES,
        "CONFIDENCE_INTERVALS": CONFIDENCE_INTERVALS,
        "SOURCE_CONTROL_COUNT": SOURCE_CONTROL_COUNT,
        "NATIVE_LIBRARY_COUNT": NATIVE_LIBRARY_COUNT,
        "SELECTION_SEED": SELECTION_SEED,
        "ORDER_SEED": ORDER_SEED,
        "BOOTSTRAP_SEED": BOOTSTRAP_SEED,
        "API_COUNTS": quotas,
        "BOUNDED_API_CAPACITIES": BOUNDED_API_CAPACITIES,
        "EDGE_PROOF_PATHS": EDGE_PROOF_PATHS,
    }
    saved = {name: getattr(original, name) for name in updates}
    try:
        base.API_COUNTS = quotas
        for name, value in updates.items():
            setattr(original, name, value)
        with original.v2_renderer():
            yield
    finally:
        for name, value in saved.items():
            setattr(original, name, value)
        base.API_COUNTS = base_api_counts


def check_v4_manifest(document: object, *, manifest_sha256: str) -> dict[str, dict]:
    selected = original.check_v2_manifest(document, manifest_sha256=manifest_sha256)
    require(isinstance(document, dict), "the expanded public manifest is invalid")
    require_audit_binding(document)
    require_universal_oracle(document)
    require_stage05_artifacts(document)
    require_worker_topology(document, measured=False)
    require(
        document.get("protocol_version") == PREFIX
        and document.get("exclusive_slot") == PREFIX,
        "the frozen expanded public protocol was substituted",
    )
    require(
        require_public_quotas(document.get("public_operations"))
        == original.API_COUNTS,
        "the frozen expanded public operation quotas changed",
    )
    return selected


def check_v4_summary(
    document: object,
    *,
    manifest: dict,
    selected_cases: dict[str, dict],
    summary_sha256: str,
    manifest_sha256: str,
) -> original.original.Results:
    results = original.check_v2_summary(
        document,
        manifest=manifest,
        selected_cases=selected_cases,
        summary_sha256=summary_sha256,
        manifest_sha256=manifest_sha256,
    )
    require_audit_binding(document, reference=manifest)
    require_universal_oracle(document, reference=manifest)
    require_stage05_artifacts(document, reference=manifest)
    require_worker_topology(document, reference=manifest, measured=True)
    require(
        isinstance(document, dict)
        and document.get("runner_sha256") == manifest.get("runner_sha256"),
        "the expanded public summary substituted its frozen runner source",
    )
    return results


def check_v4_integrity(
    document: object,
    results: original.original.Results,
    *,
    manifest: dict,
    integrity_sha256: str,
) -> None:
    require(
        isinstance(document, dict)
        and document.get("memory_limitation") == ISOLATED_MEMORY_LIMITATION,
        "the isolated-worker Python-traced memory limitation is misrepresented",
    )
    legacy_document = dict(document)
    legacy_document["memory_limitation"] = (
        "Python-traced allocations. " + ISOLATED_MEMORY_LIMITATION
    )
    original.check_v2_integrity(
        legacy_document,
        results,
        manifest=manifest,
        integrity_sha256=integrity_sha256,
    )
    require_audit_binding(document, reference=manifest)
    require_universal_oracle(document, reference=manifest)
    require_stage05_artifacts(document, reference=manifest)
    require_worker_topology(document, reference=manifest, measured=True)
    require(
        isinstance(document, dict)
        and document.get("runner_sha256") == manifest.get("runner_sha256"),
        "the expanded public replay substituted its frozen runner source",
    )


def add_target_guide(svg: str, *, suffix: str, results: original.original.Results) -> str:
    """Directly label the public target without declaring it achieved."""

    if suffix not in ("overall", "rankings"):
        return svg
    values = [
        1.0,
        *(
            value
            for candidate in results.candidates
            for value in (
                candidate.ranking["ci95_low"],
                candidate.ranking["ci95_high"],
            )
        ),
    ]
    lower = min(0.70, min(values) * 0.94)
    upper = max(1.65, max(values) * 1.08)
    if suffix == "overall":
        left, right, top, bottom, label_y = 351, 933, 261, 535, 236
    else:
        left, right, top, bottom, label_y = 323, 856, 289, 552, 273
    position = base.log_x(1.5, left=left, right=right, low=lower, high=upper)
    guide = (
        '<g aria-label="Public development target: 1.5 times CPython; '
        'not evidence of final success">'
        '<title>Public development target: 1.5 times CPython</title>'
        f'<line x1="{position:.2f}" y1="{top}" '
        f'x2="{position:.2f}" y2="{bottom}" '
        'stroke="#9a3412" stroke-width="2" stroke-dasharray="7 5"/>'
        f'<text x="{position:.2f}" y="{label_y}" text-anchor="middle" '
        'style="font-size:14px;font-weight:720;fill:#9a3412">'
        '1.5&#215; public target</text></g>'
    )
    require(svg.endswith("</svg>\n"), "the inherited public chart is not self-contained SVG")
    updated = svg.removesuffix("</svg>\n") + guide + "\n</svg>\n"
    base.validate_svg(updated, suffix=suffix, results=results)
    return updated


def build_v4_charts(results: original.original.Results) -> dict[str, str]:
    inherited = base.build_charts(results)
    require(tuple(inherited) == SUFFIXES, "an expanded public graph was removed")
    charts = {
        suffix: add_target_guide(inherited[suffix], suffix=suffix, results=results)
        for suffix in SUFFIXES
    }
    for suffix, svg in charts.items():
        base.validate_svg(svg, suffix=suffix, results=results)
    return charts


def synthetic_quotas() -> dict[str, int]:
    """Create explicitly synthetic quotas, never a predicted real selection."""

    quotas = {name: 1 for name in BOUNDED_API_CAPACITIES}
    while sum(quotas.values()) < CASES:
        available = [
            name
            for name, capacity in BOUNDED_API_CAPACITIES.items()
            if quotas[name] < capacity
        ]
        require(bool(available), "synthetic public capacity was exhausted")
        name = min(available, key=lambda item: (quotas[item], item))
        quotas[name] += 1
    return require_public_quotas(quotas)


def synthetic_documents() -> tuple[dict, dict, dict]:
    """Bind complete, in-memory audit, isolation, and universal-oracle controls."""

    manifest, summary, integrity = original.synthetic_documents()
    original_audit_source_sha256 = hashlib.sha256(
        b"synthetic-only-original-76-control-audit-source"
    ).hexdigest()
    bindings = {
        "from_scratch_audit_source_path": ORIGINAL_AUDIT_SOURCE_PATH,
        "from_scratch_audit_source_sha256": original_audit_source_sha256,
        "postfinal_no_delegation_audit_path": NO_DELEGATION_AUDIT_PATH,
        "postfinal_no_delegation_audit_sha256": hashlib.sha256(
            b"synthetic-only-stage-05-no-delegation-report"
        ).hexdigest(),
        "postfinal_no_delegation_audit_source_path": NO_DELEGATION_SOURCE_PATH,
        "postfinal_no_delegation_audit_source_sha256": hashlib.sha256(
            b"synthetic-only-stage-05-no-delegation-source"
        ).hexdigest(),
        "postfinal_no_delegation_audit_schema": NO_DELEGATION_SCHEMA,
        "postfinal_no_delegation_control_count": NO_DELEGATION_CONTROL_COUNT,
    }
    universal = {
        "python_re_universal_oracle_source_path": UNIVERSAL_ORACLE_SOURCE_PATH,
        "python_re_universal_oracle_source_sha256": (
            UNIVERSAL_ORACLE_SOURCE_SHA256
        ),
        "python_re_universal_oracle_frozen_source_path": (
            UNIVERSAL_ORACLE_FROZEN_SOURCE_PATH
        ),
        "python_re_universal_oracle_frozen_source_sha256": hashlib.sha256(
            b"synthetic-only-immutable-v1-universal-python-source"
        ).hexdigest(),
        "python_re_universal_oracle_report_path": UNIVERSAL_ORACLE_REPORT_PATH,
        "python_re_universal_oracle_report_sha256": hashlib.sha256(
            b"synthetic-only-stage-03-complete-all-candidate-PASS-report"
        ).hexdigest(),
        "python_re_universal_oracle_schema": UNIVERSAL_ORACLE_SCHEMA,
        "python_re_universal_oracle_status": "PASS",
        "python_re_universal_oracle_selected": "all",
        "python_re_universal_oracle_mismatches": 0,
        "python_re_universal_oracle_cases": CASES,
        "python_re_universal_oracle_comparisons_per_case": (
            UNIVERSAL_ORACLE_COMPARISONS_PER_CASE
        ),
        "python_re_universal_oracle_comparisons_per_candidate": (
            UNIVERSAL_ORACLE_COMPARISONS_PER_CANDIDATE
        ),
        "python_re_universal_oracle_total_comparisons": (
            UNIVERSAL_ORACLE_TOTAL_COMPARISONS
        ),
        "python_re_universal_oracle_candidates": list(
            UNIVERSAL_ORACLE_CANDIDATES
        ),
        "python_re_universal_oracle_seed": UNIVERSAL_ORACLE_SEED,
        "python_re_universal_oracle_seed_domain": UNIVERSAL_ORACLE_SEED_DOMAIN,
        "python_re_universal_oracle_case_sha256": hashlib.sha256(
            b"synthetic-only-universal-python-case-stream"
        ).hexdigest(),
        "python_re_universal_oracle_grammar_family_count": (
            UNIVERSAL_ORACLE_GRAMMAR_FAMILIES
        ),
        "python_re_universal_oracle_input_stratum_count": (
            UNIVERSAL_ORACLE_INPUT_STRATA
        ),
        "python_re_universal_oracle_examples_per_stratum": (
            UNIVERSAL_ORACLE_EXAMPLES_PER_STRATUM
        ),
        "python_re_universal_oracle_original_audit_sha256": manifest[
            "from_scratch_audit_sha256"
        ],
        "python_re_universal_oracle_postfinal_no_delegation_audit_sha256": (
            bindings["postfinal_no_delegation_audit_sha256"]
        ),
    }
    stage05_artifacts = [
        {
            "role": role,
            "path": path,
            "sha256": hashlib.sha256(
                f"synthetic-only-stage-05-correctness:{role}".encode("utf-8")
            ).hexdigest(),
        }
        for role, path in STAGE05_ARTIFACT_PATHS.items()
    ]
    isolation = {
        "execution_topology": EXECUTION_TOPOLOGY,
        "runtime_native_hash_policy": RUNTIME_NATIVE_HASH_POLICY,
        "execution_safety": EXECUTION_SAFETY,
    }
    manifest.update(bindings)
    manifest.update(universal)
    manifest.update(isolation)
    manifest["stage05_correctness_artifacts"] = copy.deepcopy(
        stage05_artifacts
    )
    manifest_sha256 = base.canonical_sha256(manifest)
    summary.update(bindings)
    summary.update(universal)
    summary.update(isolation)
    summary.update(
        {
            "runner_sha256": manifest["runner_sha256"],
            "stage05_correctness_artifacts": copy.deepcopy(
                stage05_artifacts
            ),
            "persistent_isolated_worker_count": ISOLATED_WORKER_COUNT,
            "per_case_runtime_guard_checks": RUNTIME_GUARD_CHECKS,
            "controller_candidate_imported": False,
        }
    )
    summary["manifest_sha256"] = manifest_sha256
    summary_sha256 = base.canonical_sha256(summary)
    integrity.update(bindings)
    integrity.update(universal)
    integrity.update(isolation)
    integrity.update(
        {
            "runner_sha256": manifest["runner_sha256"],
            "stage05_correctness_artifacts": copy.deepcopy(
                stage05_artifacts
            ),
            "persistent_isolated_worker_count": ISOLATED_WORKER_COUNT,
            "per_case_runtime_guard_checks": RUNTIME_GUARD_CHECKS,
            "controller_candidate_imported": False,
            "memory_limitation": ISOLATED_MEMORY_LIMITATION,
        }
    )
    integrity["manifest_sha256"] = manifest_sha256
    integrity["summary_sha256"] = summary_sha256
    return manifest, summary, integrity


def self_test() -> dict:
    """Run only in-memory public controls; never inspect real evidence."""

    original.require_candidate_free()
    fake_manifest_sha256 = hashlib.sha256(
        b"synthetic-only-stage-05-manifest-pin"
    ).hexdigest()
    fake_runner_sha256 = hashlib.sha256(
        b"synthetic-only-stage-05-runner-pin"
    ).hexdigest()
    quotas = synthetic_quotas()
    with v4_renderer(
        manifest_sha256=fake_manifest_sha256,
        runner_sha256=fake_runner_sha256,
        public_operations=quotas,
    ):
        inherited = original.self_test()
        require(inherited.get("result") == "PASS", "inherited public synthetic controls failed")
        require(
            inherited.get("protocol_version") == PREFIX,
            "inherited synthetic controls used the wrong public stage",
        )
        require(
            inherited.get("synthetic_cases_per_module") == CASES,
            "inherited controls changed the expanded public denominator",
        )
        require(
            inherited.get("synthetic_workload_categories") == CATEGORY_COUNT,
            "inherited controls hid a public workload category",
        )
        require(
            type(inherited.get("adversarial_rejections")) is int
            and inherited["adversarial_rejections"] >= 30,
            "an inherited public adversarial control was removed",
        )
        manifest, summary, integrity = synthetic_documents()
        manifest_sha256 = base.canonical_sha256(manifest)
        summary_sha256 = base.canonical_sha256(summary)
        selected = check_v4_manifest(
            manifest,
            manifest_sha256=manifest_sha256,
        )
        results = check_v4_summary(
            summary,
            manifest=manifest,
            selected_cases=selected,
            summary_sha256=summary_sha256,
            manifest_sha256=manifest_sha256,
        )
        check_v4_integrity(
            integrity,
            results,
            manifest=manifest,
            integrity_sha256=base.canonical_sha256(integrity),
        )
        charts = build_v4_charts(results)
        require(
            charts == build_v4_charts(results),
            "expanded public target guides are not deterministic",
        )
        mutated_documents = (
            ("changed no-delegation audit", "summary", "postfinal_no_delegation_audit_sha256", "0" * 64),
            ("changed no-delegation source", "summary", "postfinal_no_delegation_audit_source_sha256", "0" * 64),
            ("changed no-delegation schema", "summary", "postfinal_no_delegation_audit_schema", "substituted"),
            ("concealed no-delegation controls", "summary", "postfinal_no_delegation_control_count", 0),
            ("changed replayed no-delegation audit", "integrity", "postfinal_no_delegation_audit_sha256", "0" * 64),
            ("changed replayed no-delegation source", "integrity", "postfinal_no_delegation_audit_source_sha256", "0" * 64),
            ("concealed replayed no-delegation controls", "integrity", "postfinal_no_delegation_control_count", 0),
            ("substituted original audit source", "summary", "from_scratch_audit_source_sha256", "0" * 64),
            ("substituted replayed original audit source", "integrity", "from_scratch_audit_source_sha256", "0" * 64),
            ("incomplete universal correctness", "summary", "python_re_universal_oracle_status", "FAIL"),
            ("partially selected universal candidates", "summary", "python_re_universal_oracle_selected", "rust"),
            ("hidden universal mismatches", "summary", "python_re_universal_oracle_mismatches", 1),
            ("omitted universal case", "summary", "python_re_universal_oracle_cases", CASES - 1),
            ("omitted universal observation", "summary", "python_re_universal_oracle_comparisons_per_case", UNIVERSAL_ORACLE_COMPARISONS_PER_CASE - 1),
            ("omitted universal family", "summary", "python_re_universal_oracle_candidates", ["rust", "zig"]),
            ("substituted universal report", "summary", "python_re_universal_oracle_report_sha256", "0" * 64),
            ("substituted universal source", "summary", "python_re_universal_oracle_source_sha256", "0" * 64),
            ("substituted immutable V1 universal source", "summary", "python_re_universal_oracle_frozen_source_sha256", "0" * 64),
            ("substituted immutable V1 universal source path", "summary", "python_re_universal_oracle_frozen_source_path", "substituted"),
            ("changed universal source seed", "summary", "python_re_universal_oracle_seed", 0),
            ("changed universal seed domain", "summary", "python_re_universal_oracle_seed_domain", "substituted"),
            ("incomplete universal grammar", "summary", "python_re_universal_oracle_grammar_family_count", UNIVERSAL_ORACLE_GRAMMAR_FAMILIES - 1),
            ("incomplete universal input strata", "summary", "python_re_universal_oracle_input_stratum_count", UNIVERSAL_ORACLE_INPUT_STRATA - 1),
            ("incomplete universal stratum examples", "summary", "python_re_universal_oracle_examples_per_stratum", UNIVERSAL_ORACLE_EXAMPLES_PER_STRATUM - 1),
            ("substituted universal source audit", "summary", "python_re_universal_oracle_original_audit_sha256", "0" * 64),
            ("substituted universal no-delegation audit", "summary", "python_re_universal_oracle_postfinal_no_delegation_audit_sha256", "0" * 64),
            ("incomplete replayed universal correctness", "integrity", "python_re_universal_oracle_status", "FAIL"),
            ("hidden replayed universal mismatches", "integrity", "python_re_universal_oracle_mismatches", 1),
            ("substituted replayed universal report", "integrity", "python_re_universal_oracle_report_sha256", "0" * 64),
            ("substituted replayed immutable V1 universal source", "integrity", "python_re_universal_oracle_frozen_source_sha256", "0" * 64),
            ("omitted stage-05 correctness proof", "summary", "stage05_correctness_artifacts", []),
            ("omitted replayed stage-05 correctness proof", "integrity", "stage05_correctness_artifacts", []),
            ("shared candidate workers", "summary", "persistent_isolated_worker_count", ISOLATED_WORKER_COUNT - 1),
            ("omitted runtime guards", "summary", "per_case_runtime_guard_checks", RUNTIME_GUARD_CHECKS - 1),
            ("candidate imported by paired controller", "summary", "controller_candidate_imported", True),
            ("misrepresented runtime hash limitations", "summary", "runtime_native_hash_policy", "complete cryptographic protection"),
            ("shared replayed candidate workers", "integrity", "persistent_isolated_worker_count", ISOLATED_WORKER_COUNT - 1),
            ("omitted replayed runtime guards", "integrity", "per_case_runtime_guard_checks", RUNTIME_GUARD_CHECKS - 1),
            ("candidate imported by replayed controller", "integrity", "controller_candidate_imported", True),
            ("invented native memory evidence", "integrity", "memory_limitation", "native memory fully measured"),
        )
        for label, kind, key, value in mutated_documents:
            changed = copy.deepcopy(summary if kind == "summary" else integrity)
            changed[key] = value
            try:
                if kind == "summary":
                    check_v4_summary(
                        changed,
                        manifest=manifest,
                        selected_cases=selected,
                        summary_sha256=base.canonical_sha256(changed),
                        manifest_sha256=manifest_sha256,
                    )
                else:
                    check_v4_integrity(
                        changed,
                        results,
                        manifest=manifest,
                        integrity_sha256=base.canonical_sha256(changed),
                    )
            except (KeyError, TypeError, ValueError):
                continue
            raise ValueError(f"stage-05 synthetic controls accepted {label}")
    original.require_candidate_free()
    return {
        "result": "PASS",
        "mode": (
            "candidate-free in-memory synthetic only; "
            "no evidence or source files read or written"
        ),
        "protocol_version": PREFIX,
        "charts": len(SUFFIXES),
        "synthetic_cases_per_module": CASES,
        "synthetic_workload_categories": CATEGORY_COUNT,
        "synthetic_individually_visible_slowdowns": len(summary["regressions"]),
        "universal_oracle_cases": CASES,
        "universal_oracle_comparisons_per_case": (
            UNIVERSAL_ORACLE_COMPARISONS_PER_CASE
        ),
        "universal_oracle_comparisons_per_candidate": (
            UNIVERSAL_ORACLE_COMPARISONS_PER_CANDIDATE
        ),
        "universal_oracle_total_comparisons": (
            UNIVERSAL_ORACLE_TOTAL_COMPARISONS
        ),
        "stage05_independent_correctness_artifacts": len(
            STAGE05_ARTIFACT_PATHS
        ),
        "isolated_worker_count": ISOLATED_WORKER_COUNT,
        "runtime_guard_checks": RUNTIME_GUARD_CHECKS,
        "original_source_control_count": SOURCE_CONTROL_COUNT,
        "no_delegation_control_count": NO_DELEGATION_CONTROL_COUNT,
        "adversarial_rejections": (
            inherited["adversarial_rejections"] + len(mutated_documents)
        ),
        "manifest_binding": "explicit --manifest-sha256 required; never guessed",
        "genuine_stage_05_public_results": "NOT MEASURED",
        "historical_final_benchmark": "FAILED; no final winner",
    }


def render(
    *,
    summary: Path,
    integrity: Path,
    manifest: Path,
    manifest_sha256: str,
    runner_sha256: str | None,
    output_dir: Path,
) -> dict:
    original.require_candidate_free()
    require(
        output_dir.resolve() == EVIDENCE.resolve(),
        "expanded public charts must use the exact public-v4 evidence directory",
    )
    require(
        valid_sha256(manifest_sha256),
        "an explicit genuine frozen public --manifest-sha256 is required",
    )
    public_manifest, actual_manifest_sha256 = base.read_json(
        manifest,
        allowed=MANIFEST,
        label="explicitly frozen expanded public manifest",
        digest=manifest_sha256,
    )
    actual_runner_sha256 = public_manifest.get("runner_sha256")
    require(
        valid_sha256(actual_runner_sha256),
        "the verified public manifest omits its frozen runner fingerprint",
    )
    if runner_sha256 is not None:
        require(
            valid_sha256(runner_sha256)
            and runner_sha256 == actual_runner_sha256,
            "the explicit frozen public runner fingerprint changed",
        )
    quotas = require_public_quotas(public_manifest.get("public_operations"))
    with v4_renderer(
        manifest_sha256=actual_manifest_sha256,
        runner_sha256=actual_runner_sha256,
        public_operations=quotas,
    ):
        selected = check_v4_manifest(
            public_manifest,
            manifest_sha256=actual_manifest_sha256,
        )
        public_summary, summary_sha256 = base.read_json(
            summary,
            allowed=SUMMARY,
            label="measured expanded public summary",
        )
        results = check_v4_summary(
            public_summary,
            manifest=public_manifest,
            selected_cases=selected,
            summary_sha256=summary_sha256,
            manifest_sha256=actual_manifest_sha256,
        )
        public_integrity, integrity_sha256 = base.read_json(
            integrity,
            allowed=INTEGRITY,
            label="independently replayed expanded public integrity",
        )
        check_v4_integrity(
            public_integrity,
            results,
            manifest=public_manifest,
            integrity_sha256=integrity_sha256,
        )
        charts = build_v4_charts(results)
        original.require_candidate_free()
        try:
            EVIDENCE.mkdir(parents=True, exist_ok=True)
            outputs: list[dict[str, str]] = []
            for suffix in SUFFIXES:
                destination = EVIDENCE / f"{PREFIX}-{suffix}.svg"
                svg = charts[suffix]
                destination.write_text(svg, encoding="utf-8", newline="\n")
                outputs.append(
                    {
                        "chart": suffix,
                        "path": str(destination),
                        "sha256": hashlib.sha256(svg.encode("utf-8")).hexdigest(),
                    }
                )
        except OSError as error:
            raise ValueError(
                "cannot write the exact expanded public evidence directory"
            ) from error
    original.require_candidate_free()
    return {
        "result": "PASS",
        "protocol_version": PREFIX,
        "measurement": "independently replayed 8,192-case public practice only",
        "manifest_sha256": actual_manifest_sha256,
        "runner_sha256": actual_runner_sha256,
        "summary_sha256": summary_sha256,
        "integrity_sha256": integrity_sha256,
        "public_cases_per_module": CASES,
        "paired_trials": TRIALS,
        "bootstrap_draws": BOOTSTRAPS,
        "paired_raw_rows": RAW_ROWS,
        "correctness_checks": CORRECTNESS_GATES,
        "confidence_intervals_recomputed": CONFIDENCE_INTERVALS,
        "individually_visible_public_slowdowns": len(
            public_summary["regressions"]
        ),
        "postfinal_no_delegation_audit_sha256": public_manifest[
            "postfinal_no_delegation_audit_sha256"
        ],
        "postfinal_no_delegation_control_count": (
            NO_DELEGATION_CONTROL_COUNT
        ),
        "python_re_universal_oracle_report_sha256": public_manifest[
            "python_re_universal_oracle_report_sha256"
        ],
        "python_re_universal_oracle_frozen_source_sha256": public_manifest[
            "python_re_universal_oracle_frozen_source_sha256"
        ],
        "python_re_universal_oracle_cases": CASES,
        "python_re_universal_oracle_comparisons_per_case": (
            UNIVERSAL_ORACLE_COMPARISONS_PER_CASE
        ),
        "python_re_universal_oracle_comparisons_per_candidate": (
            UNIVERSAL_ORACLE_COMPARISONS_PER_CANDIDATE
        ),
        "python_re_universal_oracle_total_comparisons": (
            UNIVERSAL_ORACLE_TOTAL_COMPARISONS
        ),
        "stage05_independent_correctness_artifacts": len(
            STAGE05_ARTIFACT_PATHS
        ),
        "persistent_isolated_worker_count": ISOLATED_WORKER_COUNT,
        "per_case_runtime_guard_checks": RUNTIME_GUARD_CHECKS,
        "controller_candidate_imported": False,
        "final_failure_report_sha256": (
            base.previous.FINAL_FAILURE_REPORT_SHA256
        ),
        "final_failure_certificate_sha256": (
            base.previous.FINAL_FAILURE_CERTIFICATE_SHA256
        ),
        "historical_final_benchmark": (
            "FAILED; final speed, final memory, and final ranking "
            "NOT MEASURED; no final winner"
        ),
        "charts": outputs,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render six independently verified 8,192-case public charts "
            "without importing candidates or accessing a final benchmark."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run exclusively candidate-free in-memory adversarial controls",
    )
    parser.add_argument("--summary", type=Path, help="exact expanded public summary")
    parser.add_argument(
        "--integrity",
        type=Path,
        help="exact independently replayed public integrity evidence",
    )
    parser.add_argument("--manifest", type=Path, help="exact frozen public manifest")
    parser.add_argument(
        "--manifest-sha256",
        help="required genuine externally supplied frozen public manifest SHA-256",
    )
    parser.add_argument(
        "--runner-sha256",
        help="optional additional independently supplied frozen public runner SHA-256",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="exact additive public-v4 evidence directory",
    )
    args = parser.parse_args(argv)
    values = (
        args.summary,
        args.integrity,
        args.manifest,
        args.manifest_sha256,
        args.runner_sha256,
        args.output_dir,
    )
    if args.self_test:
        if any(value is not None for value in values):
            parser.error(
                "synthetic controls cannot read benchmark evidence or write outputs"
            )
    elif any(
        value is None
        for value in (
            args.summary,
            args.integrity,
            args.manifest,
            args.manifest_sha256,
            args.output_dir,
        )
    ):
        parser.error(
            "rendering requires explicit --summary, --integrity, --manifest, "
            "--manifest-sha256, and --output-dir"
        )
    elif not valid_sha256(args.manifest_sha256):
        parser.error("--manifest-sha256 must be a genuine 64-character lowercase SHA-256")
    elif args.runner_sha256 is not None and not valid_sha256(args.runner_sha256):
        parser.error("--runner-sha256 must be a genuine 64-character lowercase SHA-256")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = (
            self_test()
            if args.self_test
            else render(
                summary=args.summary,
                integrity=args.integrity,
                manifest=args.manifest,
                manifest_sha256=args.manifest_sha256,
                runner_sha256=args.runner_sha256,
                output_dir=args.output_dir,
            )
        )
    except (KeyError, OSError, TypeError, ValueError) as error:
        print(f"expanded public chart rendering rejected: {error}")
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
