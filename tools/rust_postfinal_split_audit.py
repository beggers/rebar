#!/usr/bin/env python3
"""Fail-closed replay of additive, post-final, public Rust split practice.

The original v9 final is permanently FALSIFIED.  This verifier reads only its
immutable failure *certificate*, never its marker, opening, raw observations,
holdout protocol, or holdout manifest.  All subsequently replayed observations
come from an explicitly named, four-way public-practice gzip and the frozen
public calibration plan.  No candidate is imported, timed, built, or executed.
"""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import io
import json
import os
import platform
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import rust_v7_multi_candidate_practice_audit as public


AuditError = public.AuditError
require = public.require

SCHEMA = "rebar-post-final-rust-split-public-practice-integrity-v1"
SELF_TEST_SCHEMA = f"{SCHEMA}-self-test"
DEFAULT_SLOT = "postfinal-rust-batched-split-01"
PRACTICE_EVIDENCE = ROOT / "performance" / "v7" / "evidence"
CANDIDATE_EVIDENCE = ROOT / "candidates" / "evidence"
CANDIDATE_AUDITS = ROOT / "candidates" / "audits"
DEFAULT_RAW = PRACTICE_EVIDENCE / f"{DEFAULT_SLOT}-raw.jsonl.gz"
DEFAULT_SUMMARY = PRACTICE_EVIDENCE / f"{DEFAULT_SLOT}-summary.json"
DEFAULT_OUTPUT = PRACTICE_EVIDENCE / f"{DEFAULT_SLOT}-integrity.json"
DEFAULT_RUST_EDGE = (
    CANDIDATE_EVIDENCE / "rust-v7-edge-oracle-rust-post-final-stage-01.json.gz"
)
DEFAULT_RUST_DEEP = (
    CANDIDATE_AUDITS / "RUST-V8-DEEP-CONTRACT-RUST-POST-FINAL-STAGE-01.json.gz"
)
DEFAULT_RUST_OBSERVABILITY = (
    CANDIDATE_EVIDENCE
    / "rust-v8-observability-rust-qualified-post-final-stage-01.json.gz"
)
DEFAULT_RUST_CAMPAIGN = (
    CANDIDATE_EVIDENCE / "rust-v8-rust-post-final-stage-01-sealed-campaign.json"
)

FINAL_FAILURE_PATH = (
    ROOT / "performance" / "v9" / "evidence"
    / "V9-FINAL-HOLDOUT-24576-FAILURE.json"
)
FINAL_FAILURE_SHA256 = (
    "b3c9ac416d0a748a9fbe4f80f97efefb56ae7f598eea425c614aa278cb177069"
)
FINAL_SCHEMA = "rebar-v9-sealed-final-holdout-failure-v1"
FINAL_CANDIDATE_FREEZE_SHA256 = (
    "52066760bb4210a57f7b10f13e9ff73e36c53982a5b97aff40ead330c79edf41"
)
FINAL_FROM_SCRATCH_SHA256 = (
    "a790fe1a75c8748df7f8bb6f1e39d0be841636055358aaee94db0aa35523f326"
)
POSTFINAL_FROM_SCRATCH_SHA256 = (
    "7c6575ee8a4dd373ebf7d59ce853fac47985b592429b9120f7d545fd184f2048"
)
POSTFINAL_RUST_CAMPAIGN_SHA256 = (
    "38f222f89694e13ce48bd33eb433a1234ab4da83b9e4f63b3656ac793b997413"
)
FINAL_MODULES = (
    "re",
    "candidates.vm_candidate",
    "candidates.rust_candidate",
    "candidates.zig_candidate",
)

HISTORICAL_PATH = (
    PRACTICE_EVIDENCE / "three-qualified-engines-public-practice-v9-integrity.json"
)
HISTORICAL_SHA256 = (
    "2385df233f0df4d5fd926920512357837c0c4c54295fe980620cac21dace8be0"
)
HISTORICAL_SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v9"
HISTORICAL_SOURCE_PATH = (
    ROOT / "tools" / "rust_v7_multi_candidate_practice_v9_audit.py"
)
HISTORICAL_SOURCE_SHA256 = (
    "29d9b7273afdd9ce64a9a44ca84f2af69f4e20d5399c12f58b88ba8c52da0add"
)
PUBLIC_SOURCE_SHA256 = (
    "bc093f114fe15833cab8f7c8d59bd1970345b6ddb47bc33349854be1af7f0ded"
)
HISTORICAL_SUMMARY_SHA256 = (
    "e0140380d6b3026e6195f27d3188e87e6d646b08d0e632c5e9eda38674e616ed"
)

C_MODULE = "candidates.vm_candidate"
RUST_MODULE = "candidates.rust_candidate"
ZIG_MODULE = "candidates.zig_candidate"
NATIVE_ROLES = {
    RUST_MODULE: frozenset({
        "bridge-source", "native-bridge", "native-engine", "native-source",
        "public-python",
    }),
    C_MODULE: frozenset({"native-source", "native-bridge", "public-python"}),
    ZIG_MODULE: frozenset({
        "bridge-source", "native-bridge", "native-engine", "native-source",
        "public-python",
    }),
}
EDGE_ROLES = {
    RUST_MODULE: NATIVE_ROLES[RUST_MODULE],
    C_MODULE: frozenset({"native-bridge", "public-python"}),
    ZIG_MODULE: frozenset({
        "native-bridge", "native-engine", "public-python",
    }),
}

HISTORICAL_SOURCES = {
    "candidates/_vm_native.c": (
        "2253ddd8608a19a06f25ed41251729365ecb1e25f6829f710cdcb858b10c4e0c"
    ),
    "candidates/rust/py_bridge.c": (
        "83afb5a709a6d0ea1701dfd64db30644edbf2cb0276c2db731a8119cfd52d8ed"
    ),
    "candidates/rust/src/lib.rs": (
        "4b89d916e4c33e2b516be570ff3e75694f03dcea5eccf9320cedf07471b07dac"
    ),
    "candidates/rust/src/newline.rs": (
        "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b"
    ),
    "candidates/rust/src/search.rs": (
        "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe"
    ),
    "candidates/rust/src/stack.rs": (
        "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e"
    ),
    "candidates/rust/src/unicode_tables.rs": (
        "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af"
    ),
    "candidates/rust_candidate.py": (
        "80812459261edb9585bdf703f137af3e0e788638af2ad7183d00b6d357e8a926"
    ),
    "candidates/vm_candidate.py": (
        "91d848e2627f19e552fef19b9943eb3e265e25537934128875645bab63cf7b80"
    ),
    "candidates/zig/mini_regex.zig": (
        "4deca5a442cccd02bebfcecd4ceeb73de62a68837c5a3bdadee4dcaf84cf0ee3"
    ),
    "candidates/zig/py_bridge.c": (
        "92d4039e1db2e01757edfd4edf56006c4735c3bc64352b6ce9c5d1f69decafcf"
    ),
    "candidates/zig_candidate.py": (
        "95a2010152099f2db61595927542b2f25a675eb72bd33125659969d804360239"
    ),
}
HISTORICAL_NATIVE = {
    f"{RUST_MODULE}:native-bridge": (
        "1f072e81ba9339a8b2e52a7e93b7bcde791c4d518620b6bd760af67c7c89af34"
    ),
    f"{RUST_MODULE}:native-engine": (
        "e7177c97070b2d0073a721044c4d23bb93e0d0883c1f2ccaa07c41eda8b96255"
    ),
    f"{C_MODULE}:native-engine": (
        "f6458cb4bf190f042e7d417a40020d2d58cebcb39671fda7352aab9725a7f633"
    ),
    f"{ZIG_MODULE}:native-bridge": (
        "80d7dab57cbee317ee1727862e27cd7dcf4cb22e1a944f4b29f2e4e983f940ed"
    ),
    f"{ZIG_MODULE}:native-engine": (
        "70bafca56a3f48477b2011f016a81b625e5f40a772af6a986d32b9098269f614"
    ),
}

FINAL_QUALIFICATIONS = (
    {
        "module": C_MODULE,
        "native_artifact_sha256": {
            "native-bridge": HISTORICAL_NATIVE[f"{C_MODULE}:native-engine"],
            "public-python": HISTORICAL_SOURCES["candidates/vm_candidate.py"],
        },
        "edge_sha256": (
            "c843dccc2d0b8eb1dcada2af282679ca05a1be2de98afc39bad95e7f448f4d7a"
        ),
        "deep_contract_sha256": (
            "0b25f1793636eac02d9231b0d5ec546aa6800eab118b0e98f98f5e6276dbb65e"
        ),
        "full_correctness_campaign_sha256": (
            "a29b540e01fc9f565e01e5cc62af14db30b38d9bacbaf55e4950e95b17c7ea40"
        ),
    },
    {
        "module": RUST_MODULE,
        "native_artifact_sha256": {
            "bridge-source": HISTORICAL_SOURCES["candidates/rust/py_bridge.c"],
            "native-bridge": HISTORICAL_NATIVE[f"{RUST_MODULE}:native-bridge"],
            "native-engine": HISTORICAL_NATIVE[f"{RUST_MODULE}:native-engine"],
            "native-source": HISTORICAL_SOURCES["candidates/rust/src/lib.rs"],
            "public-python": HISTORICAL_SOURCES["candidates/rust_candidate.py"],
        },
        "edge_sha256": (
            "c3e67b08ac34540dbbd248b5ffb07161ae7e9b815a6f6bcbc757ef178f7585b1"
        ),
        "deep_contract_sha256": (
            "f012d5e16305783d70fe6b7ece86a7692b2ac37c310c9a7e12cc856f91e0d1d0"
        ),
        "full_correctness_campaign_sha256": (
            "9ddbab81b16f0440ca19bffb8a539ea08d4a7ff33606ee3019eaf85977c2249a"
        ),
    },
    {
        "module": ZIG_MODULE,
        "native_artifact_sha256": {
            "native-bridge": HISTORICAL_NATIVE[f"{ZIG_MODULE}:native-bridge"],
            "native-engine": HISTORICAL_NATIVE[f"{ZIG_MODULE}:native-engine"],
            "public-python": HISTORICAL_SOURCES["candidates/zig_candidate.py"],
        },
        "edge_sha256": (
            "a4c8b75811b5304ab115fb387f821127a20ed2615e7948ab4b96443dbe1ebe5c"
        ),
        "deep_contract_sha256": (
            "422f662f7c01e961ae0e913ed8e1bc1927b80c70530d7982a4a65784bf649a91"
        ),
        "full_correctness_campaign_sha256": (
            "4ba7cb9c45a70b747cc0a6eb721f6bb51081157f527d1bf5e578e603715ae5dc"
        ),
    },
)


@dataclass(frozen=True)
class ReferenceProof:
    module: str
    edge: Path
    edge_sha256: str
    edge_payload_sha256: str
    deep: Path
    deep_sha256: str
    observability: Path
    observability_sha256: str
    campaign: Path
    campaign_sha256: str


C_REFERENCE = ReferenceProof(
    module=C_MODULE,
    edge=(
        CANDIDATE_EVIDENCE
        / "rust-v8-edge-oracle-vm-deep-stage-21-singleton-split-memchr.json.gz"
    ),
    edge_sha256=(
        "a5214e9f0144b4549f8134d7df9bec21975f5debe9b6a392f47dd1097baec314"
    ),
    edge_payload_sha256=FINAL_QUALIFICATIONS[0]["edge_sha256"],
    deep=(
        CANDIDATE_AUDITS
        / "RUST-V8-DEEP-CONTRACT-C-STAGE-21-SINGLETON-SPLIT-MEMCHR.json.gz"
    ),
    deep_sha256=(
        "907d6c684cd5e7161ef27b167f1d3bdd18243dff61bad4d5586ff3ef5b2d13cd"
    ),
    observability=(
        CANDIDATE_EVIDENCE
        / "rust-v8-observability-vm-qualified-stage-21-singleton-split-memchr.json.gz"
    ),
    observability_sha256=(
        "0a975f63d3a5e20e317e3dc08c1324ce95a8ed371923b53c18e65f49c6414b8a"
    ),
    campaign=(
        CANDIDATE_EVIDENCE
        / "rust-v8-vm-stage-21-singleton-split-memchr-sealed-campaign.json"
    ),
    campaign_sha256=FINAL_QUALIFICATIONS[0][
        "full_correctness_campaign_sha256"
    ],
)
ZIG_REFERENCE = ReferenceProof(
    module=ZIG_MODULE,
    edge=(
        CANDIDATE_EVIDENCE / "rust-v8-edge-oracle-zig-deep-stage-13.json.gz"
    ),
    edge_sha256=(
        "b31af0559e865b93a506e0915073cef141a805b4462e7e4d4a692e11aff393fc"
    ),
    edge_payload_sha256=FINAL_QUALIFICATIONS[2]["edge_sha256"],
    deep=CANDIDATE_AUDITS / "RUST-V8-DEEP-CONTRACT-ZIG-STAGE-13.json.gz",
    deep_sha256=(
        "1adc32659fab774aeb77f74d3df6b005c14d2aec3aae52e5d6fdf6791bcd151e"
    ),
    observability=(
        CANDIDATE_EVIDENCE
        / "rust-v8-observability-zig-qualified-stage-13.json.gz"
    ),
    observability_sha256=(
        "99caa13c501461f9a95a71188ba41a00ead9b90bc2a816c9db307544032da081"
    ),
    campaign=(
        CANDIDATE_EVIDENCE / "rust-v8-zig-stage-13-sealed-campaign.json"
    ),
    campaign_sha256=FINAL_QUALIFICATIONS[2][
        "full_correctness_campaign_sha256"
    ],
)

MAX_PROOF_BYTES = 64 * 1024 * 1024
FINAL_POISONED_CONTROLS = 29
HISTORICAL_POISONED_CONTROLS = 284


def valid_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def assert_no_candidates_imported() -> None:
    require(
        not any(
            name == candidate or name.startswith(f"{candidate}.")
            for candidate in public.MODULES[1:]
            for name in sys.modules
        ),
        "the independent post-final verifier imported a production candidate",
    )


def authorized_path(path: Path, parent: Path, label: str) -> Path:
    try:
        resolved = path.resolve()
        allowed_parent = parent.resolve()
    except (OSError, RuntimeError) as error:
        raise AuditError(f"cannot resolve the authorized {label} path") from error
    require(
        resolved.is_relative_to(allowed_parent),
        f"the {label} path escapes its explicitly authorized public directory",
    )
    return resolved


def validate_slot(slot: object) -> str:
    require(
        isinstance(slot, str)
        and slot.startswith("postfinal-")
        and 8 < len(slot) <= 160
        and all(character.isascii() and (
            character.isalnum() or character in "-_"
        ) for character in slot)
        and "holdout" not in slot.lower()
        and "protocol" not in slot.lower()
        and "manifest" not in slot.lower(),
        "the exclusive slot is not an additive, explicitly named post-final public practice",
    )
    return slot


def validate_final_certificate(certificate: dict[str, Any]) -> None:
    require(certificate.get("schema") == FINAL_SCHEMA, "the original final failure schema was substituted")
    require(certificate.get("result") == "FALSIFIED", "the original final outcome is not permanently FALSIFIED")
    require(certificate.get("failed") == 1, "the original final failure count was altered")
    require(
        certificate.get("holdout_state") == "irreversibly-authorized-no-retry",
        "the final failure no longer preserves its irreversible no-retry state",
    )
    require(certificate.get("retry_permitted") is False, "a retry of the original final was authorized")
    require(certificate.get("final_holdout_unsealed") is True, "the original final opening was concealed")
    require(certificate.get("auditor_result") == "PASS", "the historical failure certificate no longer passed independent verification")
    require(certificate.get("auditor_holdout_opened") is False, "the historical auditor opened a held-out case")
    require(certificate.get("auditor_timing_performed") is False, "the historical auditor performed timing")
    require(certificate.get("complete_final_timing") is False, "an incomplete original final was represented as complete timing")
    require(certificate.get("complete_final_summary") is False, "an incomplete original final was represented as a final summary")
    require(certificate.get("complete_final_ranking_count") == 0, "a final winner or ranking was fabricated")
    require(certificate.get("final_speed") == "NOT MEASURED", "the failed final was assigned a final speed")
    require(certificate.get("winner") is None, "the failed original final was assigned a winner")
    require(certificate.get("required_cases") == 24_576, "the historical final denominator was rewritten")
    require(certificate.get("complete_cases") == 14_342, "the historical completed-case count was rewritten")
    require(certificate.get("required_raw_rows") == 3_047_424, "the historical final paired-row denominator was rewritten")
    require(certificate.get("observed_raw_rows") == 1_778_408, "the historical incomplete-row count was rewritten")
    require(certificate.get("paired_modules_per_case") == 4, "the historical final four-way candidate set was rewritten")
    require(certificate.get("trials_per_module_case") == 31, "the historical final trial count was rewritten")
    require(certificate.get("module_order") == list(FINAL_MODULES), "the historical final engine order was rewritten")
    require(certificate.get("runner_exit_code") == 2, "the genuine original final runner failure was concealed")
    require(
        certificate.get("candidate_freeze_sha256") == FINAL_CANDIDATE_FREEZE_SHA256,
        "the immutable original final candidate freeze was substituted",
    )
    require(
        certificate.get("from_scratch_audit_sha256") == FINAL_FROM_SCRATCH_SHA256,
        "the immutable original final independence-audit identity was rewritten",
    )
    require(
        certificate.get("candidate_qualifications") == list(FINAL_QUALIFICATIONS),
        "the immutable original final C, Rust, or Zig qualification was rewritten",
    )
    controls = certificate.get("self_test")
    require(
        isinstance(controls, dict)
        and controls.get("schema") == f"{FINAL_SCHEMA}-self-test"
        and controls.get("result") == "PASS"
        and controls.get("failed") == 0
        and controls.get("holdout_opened") is False
        and controls.get("timing_performed") is False
        and controls.get("synthetic_only") is True
        and controls.get("poisoned_control_count") == FINAL_POISONED_CONTROLS,
        "the immutable original final failure omitted its synthetic anti-tamper controls",
    )
    checks = controls.get("poisoned_controls")
    require(
        isinstance(checks, list)
        and len(checks) == FINAL_POISONED_CONTROLS
        and all(
            isinstance(check, dict) and check.get("passed") is True
            for check in checks
        ),
        "the immutable original final failure has missing or unsuccessful controls",
    )


def validate_historical_report(report: dict[str, Any]) -> None:
    require(report.get("schema") == HISTORICAL_SCHEMA, "the immutable public-practice v9 report was substituted")
    require(report.get("result") == "PASS" and report.get("failed") == 0, "the frozen public-practice v9 integrity report did not pass")
    require(report.get("holdout_accessed") is False, "historical public practice accessed the final holdout")
    require(report.get("timing_performed") is False, "the historical public verifier performed timing")
    require(report.get("module_order") == list(public.MODULES), "historical public practice omitted or reordered an independent engine")
    require(report.get("cases_per_candidate") == public.EXPECTED_CASES, "historical public practice changed its 624-case denominator")
    require(report.get("trials_per_module_case") == public.EXPECTED_TRIALS, "historical public practice changed its seven paired trials")
    require(report.get("bootstrap_draws") == public.EXPECTED_BOOTSTRAPS, "historical public practice changed its 499 bootstrap draws")
    require(report.get("raw_rows") == public.EXPECTED_ROWS, "historical public practice changed its complete paired-row denominator")
    require(report.get("correctness_checks") == public.EXPECTED_CORRECTNESS_CHECKS, "historical public practice omitted a correctness check")
    require(report.get("frozen_plan_sha256") == public.EXPECTED_PLAN_SHA256, "the frozen public 624-case plan was substituted")
    require(report.get("source_sha256") == HISTORICAL_SOURCE_SHA256, "the frozen public-practice v9 verifier was substituted")
    require(report.get("summary_sha256") == HISTORICAL_SUMMARY_SHA256, "the frozen public-practice v9 summary was substituted")
    require(report.get("from_scratch_audit_sha256") == FINAL_FROM_SCRATCH_SHA256, "the immutable original-final independence audit was relabeled")
    require(report.get("strict_regression_speedup_threshold") == public.REGRESSION_THRESHOLD, "the frozen strict 20-percent loss threshold was changed")
    require(report.get("strict_regressions") == 256, "the genuine historical 256 public-practice losses were concealed")
    require(report.get("verified_native_library_count") == 5, "historical practice omitted an owned native library")
    require(report.get("verified_independent_engine_count") == 3, "historical practice omitted an independent replacement engine")
    require(report.get("qualified_source_fingerprints") == HISTORICAL_SOURCES, "the immutable original-final source fingerprints were rewritten")
    require(report.get("native_elf_fingerprints") == HISTORICAL_NATIVE, "the immutable original-final native fingerprints were rewritten")
    before = report.get("candidate_binary_sha256_before")
    after = report.get("candidate_binary_sha256_after")
    require(isinstance(before, dict) and before == after, "the historical production artifacts changed during public practice")
    require(valid_sha256(before.get("re:module")), "the immutable historical Python reference identity is missing")
    for key, digest in HISTORICAL_NATIVE.items():
        require(before.get(key) == digest, f"the historical native identity was rewritten: {key}")
    for module, path in (
        (RUST_MODULE, "candidates/rust_candidate.py"),
        (C_MODULE, "candidates/vm_candidate.py"),
        (ZIG_MODULE, "candidates/zig_candidate.py"),
    ):
        require(before.get(f"{module}:module") == HISTORICAL_SOURCES[path], f"the historical public wrapper was rewritten: {module}")
    require(before.get(f"{RUST_MODULE}:bridge-source") == HISTORICAL_SOURCES["candidates/rust/py_bridge.c"], "the historical Rust bridge source was rewritten")
    require(before.get(f"{RUST_MODULE}:native-source") == HISTORICAL_SOURCES["candidates/rust/src/lib.rs"], "the historical Rust engine source was rewritten")
    references = report.get("verified_edge_oracles")
    require(isinstance(references, list) and len(references) == 3, "historical public practice omitted a source-bound matching proof")
    for module, reference in zip(public.MODULES[1:], references, strict=True):
        require(isinstance(reference, dict) and reference.get("module") == module, "historical public practice cross-contaminated engine proofs")
        require(reference.get("correctness_checks") == 223_198, "historical matching proof dropped frozen Python checks")
        require(reference.get("actual_sha256") == public.EXPECTED_EDGE_ANSWER_SHA256, "historical matching proof changed frozen Python answers")
        require(reference.get("script_sha256") == public.EXPECTED_EDGE_SOURCE_SHA256, "historical matching proof changed the public matching verifier")
        require(reference.get("stdlib_baseline_sha256") == public.EXPECTED_STDLIB_EDGE_SHA256, "historical matching proof changed the Python baseline")
        final = next(item for item in FINAL_QUALIFICATIONS if item["module"] == module)
        require(reference.get("report_sha256") == final["edge_sha256"], "the immutable original-final matching qualification was rewritten")
        recorded_artifacts = reference.get("candidate_artifacts")
        require(isinstance(recorded_artifacts, dict), "historical matching proof omitted source-bound artifacts")
        require(
            {role: item.get("sha256") for role, item in recorded_artifacts.items() if isinstance(item, dict)}
            == final["native_artifact_sha256"],
            "the immutable original-final matching artifacts were rewritten",
        )
    controls = report.get("self_test")
    require(
        isinstance(controls, dict)
        and controls.get("result") == "PASS"
        and controls.get("failed") == 0
        and controls.get("synthetic_only") is True
        and controls.get("timing_performed") is False
        and controls.get("poisoned_control_count") == HISTORICAL_POISONED_CONTROLS,
        "historical public practice omitted its 284 frozen anti-tamper controls",
    )
    checks = controls.get("poisoned_controls")
    require(
        isinstance(checks, list)
        and len(checks) == HISTORICAL_POISONED_CONTROLS
        and all(isinstance(check, dict) and check.get("passed") is True for check in checks),
        "historical public practice contains a missing or unsuccessful anti-tamper control",
    )


def validate_postfinal_header(
    summary: dict[str, Any],
    plan: dict[str, Any],
    profile: public.Profile,
    raw_path: Path,
    slot: str,
) -> None:
    validate_slot(slot)
    public.validate_header(summary, plan, profile, None)
    require(summary.get("exclusive_slot") == slot, "post-final practice reused, substituted, or omitted its exclusive slot")
    require(summary.get("raw_path") == str(raw_path.resolve()), "post-final practice substituted the explicitly recorded public raw path")
    require(
        summary.get("measurement")
        == "balanced practice diagnostic only; not a holdout result or final speed claim",
        "post-final public practice was falsely represented as final or held-out performance",
    )


def artifact_shapes(
    entries: object,
    module: str,
    expected_roles: frozenset[str],
    label: str,
) -> dict[str, dict[str, str]]:
    require(isinstance(entries, list), f"{label} omitted its source-bound production artifacts")
    result: dict[str, dict[str, str]] = {}
    for entry in entries:
        require(
            isinstance(entry, dict) and set(entry) == {"role", "path", "sha256"},
            f"{label} changed its production-artifact fields",
        )
        role = entry.get("role")
        require(isinstance(role, str) and role in expected_roles and role not in result, f"{label} duplicated, omitted, or substituted an artifact role")
        path = public.checked_production_path(entry.get("path"), f"{module} production artifact")
        digest = entry.get("sha256")
        require(valid_sha256(digest), f"{label} has an invalid production-artifact SHA-256")
        result[role] = {"path": public.display_path(path), "sha256": digest}
    require(set(result) == expected_roles, f"{label} omitted or substituted a required production artifact")
    return result


def validate_bound_artifacts(
    entries: object,
    module: str,
    expected_roles: frozenset[str],
    sources: dict[str, str],
    measured: dict[str, str],
    label: str,
) -> dict[str, dict[str, str]]:
    artifacts = artifact_shapes(entries, module, expected_roles, label)
    for role, entry in artifacts.items():
        path = public.checked_production_path(entry["path"], f"{module} production artifact")
        digest = entry["sha256"]
        require(public.sha256_file(path) == digest, f"{label} production artifact changed after qualification")
        if role in {"bridge-source", "native-source"}:
            require(sources.get(entry["path"]) == digest, f"{label} source differs from the fresh from-scratch audit")
        if role == "public-python":
            key = f"{module}:module"
        elif role == "native-bridge" and module == C_MODULE:
            key = f"{module}:native-engine"
        else:
            key = f"{module}:{role}"
        if key in measured:
            require(measured[key] == digest, f"{label} differs from its actual measured production artifact")
        elif role not in {"bridge-source", "native-source"}:
            raise AuditError(f"{label} omitted a measured owned native artifact")
    return artifacts


def validate_edge_reference_shape(
    document: dict[str, Any],
    module: str,
    edge_path: Path,
    edge_sha256: str,
    label: str,
) -> dict[str, Any]:
    reference = document.get("edge_oracle")
    require(isinstance(reference, dict), f"{label} omitted its source-bound matching proof")
    require(reference.get("archive_sha256") == edge_sha256, f"{label} substituted its compressed matching proof")
    require(reference.get("path") == str(edge_path.resolve()), f"{label} substituted its matching-proof path")
    require(reference.get("module") == module, f"{label} bound another candidate family's matching proof")
    require(reference.get("checks") == 223_198 and reference.get("failed") == 0, f"{label} omitted or failed frozen public matching checks")
    if "script_sha256" in reference:
        require(reference.get("script_sha256") == public.EXPECTED_EDGE_SOURCE_SHA256, f"{label} substituted the frozen public matching oracle")
    return reference


def validate_deep_shape(
    document: dict[str, Any],
    module: str,
    edge_path: Path,
    edge_sha256: str,
) -> None:
    label = f"{module} 393-case post-final public deep-contract proof"
    require(document.get("schema") == "rebar-rust-v8-deep-public-contract-v1", f"{label} substituted the frozen public-contract schema")
    require(document.get("status") == "PASS", f"{label} did not pass")
    require(document.get("candidate_module") == module, f"{label} qualified another candidate family")
    require(document.get("checks") == 393, f"{label} changed its frozen 393-obligation denominator")
    require(document.get("public_mismatch_count") == 0, f"{label} concealed a public behavioral mismatch")
    require(document.get("stdlib_vs_stdlib_mismatches") == [], f"{label} concealed a Python self-oracle failure")
    require(document.get("holdout") == "NOT ACCESSED", f"{label} accessed held-out evidence")
    require(document.get("performance") == "NOT MEASURED", f"{label} performed benchmark timing")
    guards = document.get("cross_engine_guard_count")
    require(isinstance(guards, int) and not isinstance(guards, bool) and guards >= 10, f"{label} omitted frozen cross-engine delegation guards")
    validate_edge_reference_shape(document, module, edge_path, edge_sha256, label)
    artifact_shapes(document.get("native_artifacts"), module, NATIVE_ROLES[module], label)


def validate_observability_shape(
    document: dict[str, Any],
    module: str,
    edge_path: Path,
    edge_sha256: str,
    deep_path: Path,
    deep_sha256: str,
) -> None:
    label = f"{module} 479-case post-final public observability proof"
    require(document.get("schema") == "rebar-v8-multi-candidate-observability-v1", f"{label} substituted the frozen observability schema")
    require(document.get("status") == "PASS", f"{label} did not pass")
    require(document.get("candidate_module") == module, f"{label} qualified another candidate family")
    require(document.get("checks") == 479 and document.get("candidate_checks") == 479, f"{label} changed its frozen 479-obligation denominator")
    require(document.get("failures") == [] and document.get("candidate_failures") == 0, f"{label} concealed a public observation failure")
    require(document.get("private_binder_checks") == 34, f"{label} changed its frozen 34 native-binder obligations")
    require(document.get("private_binder_failures") == [], f"{label} concealed a native-binder failure")
    require(document.get("holdout") == "NOT ACCESSED", f"{label} accessed held-out evidence")
    require(document.get("performance") == "NOT MEASURED", f"{label} performed benchmark timing")
    validate_edge_reference_shape(document, module, edge_path, edge_sha256, label)
    proof = document.get("deep_proof")
    require(isinstance(proof, dict), f"{label} omitted its source-bound deep-contract proof")
    require(proof.get("archive_sha256") == deep_sha256, f"{label} substituted its compressed deep proof")
    require(proof.get("path") == str(deep_path.resolve()), f"{label} substituted its deep-proof path")
    require(proof.get("candidate_module") == module, f"{label} bound another candidate family's deep proof")
    require(proof.get("checks") == 393 and proof.get("status") == "PASS", f"{label} omitted or failed frozen deep obligations")
    require(proof.get("edge_archive_sha256") == edge_sha256, f"{label} changed the matching proof inside its deep chain")
    artifact_shapes(document.get("native_artifacts"), module, NATIVE_ROLES[module], label)


def validate_campaign_shape(
    document: dict[str, Any],
    module: str,
    edge_path: Path,
    edge_sha256: str,
) -> None:
    label = f"{module} complete 22-stage post-final public correctness campaign"
    require(document.get("schema") == "rebar-rust-campaign-gate-v1", f"{label} substituted the frozen campaign schema")
    require(document.get("candidate") == module, f"{label} qualified another candidate family")
    require(document.get("passed") is True, f"{label} did not pass")
    require(document.get("holdout_accessed") is False, f"{label} accessed held-out evidence")
    require(document.get("timing_performed") is False, f"{label} performed benchmark timing")
    require(document.get("performance") == "NOT MEASURED", f"{label} misrepresented correctness as a performance result")
    require(document.get("required_correctness_step_count") == 22, f"{label} changed its frozen 22-stage denominator")
    steps = document.get("steps")
    require(
        isinstance(steps, list)
        and len(steps) == 22
        and all(isinstance(step, dict) and step.get("passed") is True for step in steps),
        f"{label} omitted or failed a required public correctness stage",
    )
    require(document.get("pinned_cpython") == "3.14.6", f"{label} substituted the frozen Python correctness baseline")
    require(document.get("python_executable") == str(public.PINNED_PYTHON), f"{label} substituted the exact pinned Python executable")
    require(document.get("mode") == "sealed-practice-only", f"{label} weakened practice-only correctness isolation")
    reference = validate_edge_reference_shape(document, module, edge_path, edge_sha256, label)
    artifact_shapes(document.get("native_artifacts"), module, NATIVE_ROLES[module], label)
    if "candidate_artifacts" in reference:
        candidate_entries = reference.get("candidate_artifacts")
        require(isinstance(candidate_entries, list), f"{label} omitted matching production artifacts")
        candidate_roles = frozenset(
            entry.get("role") for entry in candidate_entries if isinstance(entry, dict)
        )
        require(
            EDGE_ROLES[module].issubset(candidate_roles)
            and candidate_roles.issubset(NATIVE_ROLES[module]),
            f"{label} omitted or substituted its matching production pipeline",
        )
        artifact_shapes(candidate_entries, module, candidate_roles, label)
    if "production_artifacts" in reference:
        artifact_shapes(
            reference.get("production_artifacts"), module, NATIVE_ROLES[module], label,
        )


def read_public_json(path: Path, label: str) -> tuple[dict[str, Any], str]:
    digest = public.sha256_file(path)
    return public.read_json(path, label, digest), digest


def read_compressed_public_json(
    path: Path,
    label: str,
    expected_sha256: str | None = None,
) -> tuple[dict[str, Any], str, str]:
    compressed_sha256 = public.sha256_file(path)
    if expected_sha256 is not None:
        require(compressed_sha256 == expected_sha256, f"the frozen compressed {label} was substituted")
    try:
        with gzip.open(path, "rb") as source:
            payload = source.read(MAX_PROOF_BYTES + 1)
    except (OSError, EOFError, zlib.error) as error:
        raise AuditError(f"cannot decode the complete source-bound {label}") from error
    require(len(payload) <= MAX_PROOF_BYTES, f"the source-bound {label} exceeds its safe public size limit")
    document = public.decode_json(payload, label)
    return document, compressed_sha256, hashlib.sha256(payload).hexdigest()


def validate_proof_chain(
    module: str,
    edge_path: Path,
    deep_path: Path,
    observability_path: Path,
    campaign_path: Path,
    sources: dict[str, str],
    measured: dict[str, str],
    expected: ReferenceProof | None = None,
) -> dict[str, Any]:
    label = f"{module} post-final source-bound public correctness"
    edge_expected = expected.edge_sha256 if expected else None
    edge, edge_sha256, edge_payload = read_compressed_public_json(
        edge_path, f"{label} matching report", edge_expected,
    )
    public.validate_edge_document(edge, module)
    if expected:
        require(edge_payload == expected.edge_payload_sha256, f"{label} changed the immutable original-final matching answers")
    edge_artifacts = validate_bound_artifacts(
        edge.get("candidate_artifacts"), module, EDGE_ROLES[module],
        sources, measured, f"{label} matching report",
    )

    deep, deep_sha256, deep_payload = read_compressed_public_json(
        deep_path, f"{label} deep contract", expected.deep_sha256 if expected else None,
    )
    validate_deep_shape(deep, module, edge_path, edge_sha256)
    deep_artifacts = validate_bound_artifacts(
        deep.get("native_artifacts"), module, NATIVE_ROLES[module],
        sources, measured, f"{label} deep contract",
    )
    for role, artifact in edge_artifacts.items():
        require(deep_artifacts.get(role) == artifact, f"{label} matching and deep proofs qualify different engines")

    observation, observation_sha256, _ = read_compressed_public_json(
        observability_path, f"{label} observability",
        expected.observability_sha256 if expected else None,
    )
    validate_observability_shape(
        observation, module, edge_path, edge_sha256, deep_path, deep_sha256,
    )
    observation_artifacts = validate_bound_artifacts(
        observation.get("native_artifacts"), module, NATIVE_ROLES[module],
        sources, measured, f"{label} observability",
    )
    require(observation_artifacts == deep_artifacts, f"{label} observability and deep proofs qualify different engines")

    if expected:
        campaign = public.read_json(
            campaign_path, f"{label} immutable complete campaign",
            expected.campaign_sha256,
        )
        campaign_sha256 = expected.campaign_sha256
    else:
        campaign, campaign_sha256 = read_public_json(
            campaign_path, f"{label} complete 22-stage campaign",
        )
    validate_campaign_shape(campaign, module, edge_path, edge_sha256)
    campaign_artifacts = validate_bound_artifacts(
        campaign.get("native_artifacts"), module, NATIVE_ROLES[module],
        sources, measured, f"{label} complete campaign",
    )
    require(campaign_artifacts == deep_artifacts, f"{label} complete campaign and deep proof qualify different engines")
    campaign_edge = campaign["edge_oracle"]
    for field in ("candidate_artifacts", "production_artifacts"):
        if field in campaign_edge:
            entries = campaign_edge[field]
            roles = frozenset(
                entry.get("role") for entry in entries if isinstance(entry, dict)
            )
            matching = validate_bound_artifacts(
                entries, module, roles, sources, measured,
                f"{label} complete campaign matching chain",
            )
            for role, artifact in matching.items():
                require(campaign_artifacts.get(role) == artifact, f"{label} complete campaign references a different production engine")

    if expected:
        qualification = next(
            item for item in FINAL_QUALIFICATIONS if item["module"] == module
        )
        require(edge_payload == qualification["edge_sha256"], f"{label} no longer matches the failed final's frozen matching proof")
        require(deep_payload == qualification["deep_contract_sha256"], f"{label} no longer matches the failed final's frozen deep proof")
        require(campaign_sha256 == qualification["full_correctness_campaign_sha256"], f"{label} no longer matches the failed final's frozen full campaign")

    return {
        "module": module,
        "edge_path": str(edge_path.resolve()),
        "edge_sha256": edge_sha256,
        "edge_payload_sha256": edge_payload,
        "edge_checks": 223_198,
        "deep_path": str(deep_path.resolve()),
        "deep_sha256": deep_sha256,
        "deep_payload_sha256": deep_payload,
        "deep_checks": 393,
        "observability_path": str(observability_path.resolve()),
        "observability_sha256": observation_sha256,
        "observability_checks": 479,
        "observability_binder_checks": 34,
        "campaign_path": str(campaign_path.resolve()),
        "campaign_sha256": campaign_sha256,
        "campaign_steps": 22,
        "candidate_artifacts": deep_artifacts,
    }


def validate_summary_edges(
    summary: dict[str, Any],
    measured: dict[str, str],
    chains: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    require(
        public.sha256_file(public.EDGE_SOURCE_PATH)
        == public.EXPECTED_EDGE_SOURCE_SHA256,
        "the immutable independent public matching-oracle source was changed",
    )
    baseline, baseline_digest = public.read_edge(
        public.STDLIB_EDGE_PATH, "immutable public Python matching baseline",
    )
    public.validate_edge_document(baseline, "re")
    require(baseline_digest == public.EXPECTED_STDLIB_EDGE_SHA256, "the immutable public Python matching baseline was changed")
    entries = summary.get("verified_edge_oracles")
    require(isinstance(entries, list) and len(entries) == 3, "post-final practice omitted an independently correctness-qualified candidate")
    for module, reference in zip(public.MODULES[1:], entries, strict=True):
        require(isinstance(reference, dict) and reference.get("module") == module, "post-final practice reordered or cross-contaminated candidate proofs")
        chain = chains[module]
        require(reference.get("path") == chain["edge_path"], f"{module} substituted its source-bound matching proof path")
        require(reference.get("report_sha256") == chain["edge_payload_sha256"], f"{module} substituted its matching proof payload")
        require(reference.get("correctness_checks") == 223_198, f"{module} dropped frozen public matching checks")
        require(reference.get("actual_sha256") == public.EXPECTED_EDGE_ANSWER_SHA256, f"{module} disagrees with the frozen public Python matching answers")
        require(reference.get("script_sha256") == public.EXPECTED_EDGE_SOURCE_SHA256, f"{module} substituted the frozen public matching oracle")
        require(reference.get("stdlib_baseline_sha256") == baseline_digest, f"{module} substituted the immutable Python matching baseline")
        artifacts = reference.get("candidate_artifacts")
        require(isinstance(artifacts, dict) and set(artifacts) == EDGE_ROLES[module], f"{module} omitted or substituted measured matching artifacts")
        for role, item in artifacts.items():
            require(item == chain["candidate_artifacts"].get(role), f"{module} matching evidence differs from its source-bound qualification")
            if role == "public-python":
                key = f"{module}:module"
            elif role == "native-bridge" and module == C_MODULE:
                key = f"{module}:native-engine"
            else:
                key = f"{module}:{role}"
            require(measured.get(key) == item["sha256"], f"{module} matching evidence differs from the actual paired production artifact")
    return entries


def validate_unchanged_references(
    historical: dict[str, Any],
    sources: dict[str, str],
    native: dict[str, str],
    measured: dict[str, str],
    audit_sha256: str,
) -> None:
    require(
        audit_sha256 != FINAL_FROM_SCRATCH_SHA256,
        "the original pre-final PASS report is stale; a fresh passing original from-scratch audit is required",
    )
    previous_sources = historical["qualified_source_fingerprints"]
    previous_native = historical["native_elf_fingerprints"]
    previous_measured = historical["candidate_binary_sha256_before"]
    require(set(sources) == set(previous_sources), "the post-final audit added or omitted an owned production source")
    require(set(native) == set(previous_native), "the post-final audit added or omitted an owned native library")
    require(set(measured) == set(previous_measured), "the post-final measurement added or omitted a production fingerprint")
    for path, expected in previous_sources.items():
        if path.startswith("candidates/zig/") or path in {
            "candidates/_vm_native.c",
            "candidates/vm_candidate.py",
            "candidates/zig_candidate.py",
        }:
            require(sources.get(path) == expected, f"the supposedly unchanged C or Zig production source was substituted: {path}")
    for role, expected in previous_native.items():
        if role.startswith(f"{C_MODULE}:") or role.startswith(f"{ZIG_MODULE}:"):
            require(native.get(role) == expected, f"the supposedly unchanged C or Zig native library was substituted: {role}")
            require(measured.get(role) == expected, f"the measured C or Zig native library differs from its final qualification: {role}")
    for role, expected in previous_measured.items():
        if role == "re:module" or role.startswith(f"{C_MODULE}:") or role.startswith(f"{ZIG_MODULE}:"):
            require(measured.get(role) == expected, f"the frozen Python, C, or Zig reference was substituted: {role}")
    rust_changed = any(
        sources.get(path) != previous_sources.get(path)
        for path in sources
        if path == "candidates/rust_candidate.py" or path.startswith("candidates/rust/")
    ) or any(
        native.get(role) != previous_native.get(role)
        for role in native
        if role.startswith(f"{RUST_MODULE}:")
    )
    require(rust_changed, "the purported post-final Rust split stage did not change any owned Rust production source or native binary")


def configure_profile(
    expanded_case_count: int | None,
    plan_path: Path,
    plan_sha256: str | None,
) -> tuple[public.Profile, dict[str, Any], str]:
    if expanded_case_count is None:
        cases = public.EXPECTED_CASES
        require(plan_path.resolve() == public.PLAN_PATH.resolve(), "the 624-case pilot substituted its immutable public calibration plan")
        frozen_sha256 = public.EXPECTED_PLAN_SHA256
        if plan_sha256 is not None:
            require(plan_sha256 == frozen_sha256, "the 624-case pilot substituted its frozen public calibration-plan hash")
    else:
        require(
            isinstance(expanded_case_count, int)
            and not isinstance(expanded_case_count, bool)
            and expanded_case_count > public.EXPECTED_CASES
            and expanded_case_count <= 1_000_000,
            "an expanded public denominator must be explicitly recorded and strictly exceed 624",
        )
        require(plan_path.resolve() != public.PLAN_PATH.resolve(), "the immutable 624-case plan cannot fabricate expanded public observations")
        require(valid_sha256(plan_sha256), "expanded public observations require an independently supplied expanded-plan SHA-256")
        cases = expanded_case_count
        frozen_sha256 = plan_sha256
    plan = public.read_json(plan_path, "explicit source-bound public calibration plan", frozen_sha256)
    categories = plan.get("all_bounded_workload_categories")
    require(isinstance(categories, int) and not isinstance(categories, bool) and categories > 0, "the explicit public practice plan omitted its workload-category denominator")
    profile = public.Profile(
        cases=cases,
        trials=public.EXPECTED_TRIALS,
        bootstraps=public.EXPECTED_BOOTSTRAPS,
        categories=categories,
        apis=public.EXPECTED_APIS,
    )
    public.validate_plan(plan, profile)
    if expanded_case_count is None:
        require(categories == public.EXPECTED_CATEGORIES, "the frozen 624-case plan changed its 260 public workload categories")
        require(plan.get("expected_sha256") == public.EXPECTED_FROZEN_ANSWER_SHA256, "the frozen 624-case plan changed its public Python reference answers")
    return profile, plan, frozen_sha256


def verify(args: argparse.Namespace) -> dict[str, Any]:
    assert_no_candidates_imported()
    require(
        platform.python_implementation() == "CPython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and Path(sys.executable).resolve() == public.PINNED_PYTHON.resolve(),
        "post-final public replay requires the exact frozen CPython 3.14.6 executable",
    )
    require(
        public.sha256_file(Path(public.__file__).resolve()) == PUBLIC_SOURCE_SHA256,
        "the immutable public-practice row, bootstrap, and independence verifier was substituted",
    )
    require(
        public.sha256_file(HISTORICAL_SOURCE_PATH) == HISTORICAL_SOURCE_SHA256,
        "the immutable historical public-practice v9 verifier was substituted",
    )

    slot = validate_slot(args.slot)
    raw_path = authorized_path(args.raw, PRACTICE_EVIDENCE, "post-final public raw observations")
    summary_path = authorized_path(args.summary, PRACTICE_EVIDENCE, "post-final public summary")
    output_path = authorized_path(args.output, PRACTICE_EVIDENCE, "post-final public integrity output")
    require(raw_path.name == f"{slot}-raw.jsonl.gz", "the post-final slot does not match its explicitly named public raw observations")
    require(summary_path.name == f"{slot}-summary.json", "the post-final slot does not match its explicitly named public summary")
    require(output_path.name == f"{slot}-integrity.json", "the post-final slot does not match its additive integrity output")
    require(not output_path.exists(), "the exclusive post-final public integrity report already exists")

    certificate_path = args.failure_certificate.resolve()
    require(certificate_path == FINAL_FAILURE_PATH.resolve(), "only the exact immutable original final failure certificate may be read")
    certificate = public.read_json(
        certificate_path, "immutable original v9 FALSIFIED final certificate",
        FINAL_FAILURE_SHA256,
    )
    validate_final_certificate(certificate)

    historical_path = args.historical_v9_integrity.resolve()
    require(historical_path == HISTORICAL_PATH.resolve(), "the immutable public-practice v9 integrity reference was redirected")
    historical = public.read_json(
        historical_path, "immutable public-practice v9 integrity reference",
        HISTORICAL_SHA256,
    )
    validate_historical_report(historical)

    plan_path = authorized_path(args.plan, CANDIDATE_EVIDENCE, "frozen public calibration plan")
    profile, plan, plan_sha256 = configure_profile(
        args.expanded_case_count, plan_path, args.plan_sha256,
    )
    summary, summary_sha256 = read_public_json(
        summary_path, "additive post-final four-way public practice summary",
    )
    validate_postfinal_header(summary, plan, profile, raw_path, slot)

    audit_path = args.from_scratch_audit.resolve()
    require(audit_path == public.AUDIT_PATH.resolve(), "post-final practice requires the actual original five-library from-scratch audit")
    audit = public.read_json(
        audit_path, "fresh original five-library from-scratch independence audit",
        POSTFINAL_FROM_SCRATCH_SHA256,
    )
    audit_sha256 = POSTFINAL_FROM_SCRATCH_SHA256
    sources, native = public.validate_independence(audit)
    measured = public.validate_measured_fingerprints(summary, sources, native)
    require(len(native) == 5, "the fresh independence audit omitted an owned loaded native library")
    validate_unchanged_references(historical, sources, native, measured, audit_sha256)

    rust_edge = authorized_path(args.rust_edge, CANDIDATE_EVIDENCE, "post-final Rust public matching proof")
    rust_deep = authorized_path(args.rust_deep, CANDIDATE_AUDITS, "post-final Rust public deep-contract proof")
    rust_observability = authorized_path(args.rust_observability, CANDIDATE_EVIDENCE, "post-final Rust public observability proof")
    rust_campaign = authorized_path(args.rust_campaign, CANDIDATE_EVIDENCE, "post-final Rust complete public correctness campaign")
    for label, path in (
        ("Rust edge", rust_edge),
        ("Rust deep", rust_deep),
        ("Rust observability", rust_observability),
        ("Rust campaign", rust_campaign),
    ):
        lowered = path.name.lower()
        require(
            ("post-final" in lowered or "postfinal" in lowered)
            and not any(token in lowered for token in (
                "holdout", "manifest", "protocol", "marker", "unseal", "opening",
            )),
            f"{label} is not explicitly named additive post-final public evidence",
        )
    if rust_campaign == DEFAULT_RUST_CAMPAIGN.resolve():
        require(
            public.sha256_file(rust_campaign) == POSTFINAL_RUST_CAMPAIGN_SHA256,
            "the frozen first post-final Rust 22-stage public campaign was substituted",
        )

    chains: dict[str, dict[str, Any]] = {}
    chains[RUST_MODULE] = validate_proof_chain(
        RUST_MODULE, rust_edge, rust_deep, rust_observability,
        rust_campaign, sources, measured,
    )
    for reference in (C_REFERENCE, ZIG_REFERENCE):
        chains[reference.module] = validate_proof_chain(
            reference.module, reference.edge, reference.deep,
            reference.observability, reference.campaign,
            sources, measured, reference,
        )
    edges = validate_summary_edges(summary, measured, chains)

    compressed_sha256 = public.sha256_file(raw_path)
    require(compressed_sha256 == summary.get("compressed_raw_sha256"), "the measured post-final public gzip hash does not match the summary")
    try:
        with raw_path.open("rb") as source:
            observations = public.read_observations(
                source, compressed_sha256, summary, plan, profile,
            )
    except OSError as error:
        raise AuditError("cannot read the explicitly named complete post-final public observations") from error
    results, rankings = public.recompute_results(plan, observations, profile)
    regressions = public.validate_results(summary, results, rankings, profile)
    controls = self_test()
    assert_no_candidates_imported()

    document = {
        "schema": SCHEMA,
        "result": "PASS",
        "failed": 0,
        "post_final": True,
        "holdout_accessed": False,
        "timing_performed": False,
        "retry_performed": False,
        "retry_permitted": False,
        "final_winner": None,
        "final_speed": "NOT MEASURED",
        "measurement": (
            "independent replay of additive post-final four-way public practice "
            "only; the original final remains FALSIFIED and cannot be retried"
        ),
        "original_final_result": "FALSIFIED",
        "original_final_failure_sha256": FINAL_FAILURE_SHA256,
        "original_final_failure_path": str(FINAL_FAILURE_PATH.resolve()),
        "original_final_candidate_freeze_sha256": FINAL_CANDIDATE_FREEZE_SHA256,
        "original_final_from_scratch_audit_sha256": FINAL_FROM_SCRATCH_SHA256,
        "historical_v9_integrity_sha256": HISTORICAL_SHA256,
        "historical_v9_auditor_sha256": HISTORICAL_SOURCE_SHA256,
        "historical_v9_strict_regressions": 256,
        "source_sha256": public.sha256_file(Path(__file__).resolve()),
        "public_replay_auditor_sha256": PUBLIC_SOURCE_SHA256,
        "exclusive_slot": slot,
        "module_order": list(public.MODULES),
        "cases_per_candidate": profile.cases,
        "expanded_case_count": args.expanded_case_count,
        "candidate_case_count": len(results),
        "trials_per_module_case": profile.trials,
        "raw_rows": len(observations),
        "correctness_checks": profile.rows * 3,
        "bootstrap_draws": profile.bootstraps,
        "confidence_intervals_recomputed": len(results) + len(rankings),
        "strict_regression_speedup_threshold": public.REGRESSION_THRESHOLD,
        "strict_regressions": len(regressions),
        "summary_sha256": summary_sha256,
        "compressed_raw_sha256": compressed_sha256,
        "raw_sha256": summary["raw_sha256"],
        "frozen_plan_sha256": plan_sha256,
        "from_scratch_audit_sha256": audit_sha256,
        "from_scratch_control_count": 76,
        "verified_independent_engine_count": 3,
        "verified_native_library_count": len(native),
        "qualified_source_fingerprints": sources,
        "native_elf_fingerprints": native,
        "candidate_binary_sha256_before": summary["candidate_binary_sha256_before"],
        "candidate_binary_sha256_after": summary["candidate_binary_sha256_after"],
        "verified_edge_oracles": edges,
        "rust_edge_sha256": chains[RUST_MODULE]["edge_sha256"],
        "rust_edge_payload_sha256": chains[RUST_MODULE]["edge_payload_sha256"],
        "rust_deep_contract_sha256": chains[RUST_MODULE]["deep_sha256"],
        "rust_deep_contract_checks": 393,
        "rust_observability_sha256": chains[RUST_MODULE]["observability_sha256"],
        "rust_observability_checks": 479,
        "rust_observability_binder_checks": 34,
        "rust_full_correctness_campaign_sha256": chains[RUST_MODULE]["campaign_sha256"],
        "rust_full_correctness_campaign_steps": 22,
        "c_edge_sha256": chains[C_MODULE]["edge_sha256"],
        "c_deep_contract_sha256": chains[C_MODULE]["deep_sha256"],
        "c_deep_contract_checks": 393,
        "c_observability_sha256": chains[C_MODULE]["observability_sha256"],
        "c_observability_checks": 479,
        "c_observability_binder_checks": 34,
        "c_full_correctness_campaign_sha256": chains[C_MODULE]["campaign_sha256"],
        "c_full_correctness_campaign_steps": 22,
        "zig_edge_sha256": chains[ZIG_MODULE]["edge_sha256"],
        "zig_deep_contract_sha256": chains[ZIG_MODULE]["deep_sha256"],
        "zig_deep_contract_checks": 393,
        "zig_observability_sha256": chains[ZIG_MODULE]["observability_sha256"],
        "zig_observability_checks": 479,
        "zig_observability_binder_checks": 34,
        "zig_full_correctness_campaign_sha256": chains[ZIG_MODULE]["campaign_sha256"],
        "zig_full_correctness_campaign_steps": 22,
        "unchanged_reference_candidates": ["re", C_MODULE, ZIG_MODULE],
        "source_bound_proof_chains": [
            chains[module] for module in public.MODULES[1:]
        ],
        "rankings": rankings,
        "regressions": regressions,
        "self_test": controls,
        "memory_limitation": (
            "Ratios cover Python-traced temporary allocations only; "
            "shared-process RSS does not establish isolated native-engine memory."
        ),
    }
    encoded = (
        json.dumps(document, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")
    try:
        with output_path.open("xb") as destination:
            destination.write(encoded)
            destination.flush()
            os.fsync(destination.fileno())
    except FileExistsError as error:
        raise AuditError("the exclusive additive post-final integrity output already exists") from error
    except OSError as error:
        raise AuditError("cannot persist the exclusive additive post-final integrity output") from error
    return {
        "schema": SCHEMA,
        "result": "PASS",
        "failed": 0,
        "post_final": True,
        "original_final_result": "FALSIFIED",
        "original_final_failure_sha256": FINAL_FAILURE_SHA256,
        "retry_permitted": False,
        "final_winner": None,
        "final_speed": "NOT MEASURED",
        "holdout_accessed": False,
        "timing_performed": False,
        "exclusive_slot": slot,
        "cases_per_candidate": profile.cases,
        "expanded_case_count": args.expanded_case_count,
        "candidate_case_count": len(results),
        "trials_per_module_case": profile.trials,
        "raw_rows": len(observations),
        "correctness_checks": profile.rows * 3,
        "bootstrap_draws": profile.bootstraps,
        "confidence_intervals_recomputed": len(results) + len(rankings),
        "strict_regressions": len(regressions),
        "verified_native_library_count": len(native),
        "rust_full_correctness_campaign_steps": 22,
        "c_full_correctness_campaign_steps": 22,
        "zig_full_correctness_campaign_steps": 22,
        "poisoned_control_count": controls["poisoned_control_count"],
        "output": public.display_path(output_path),
        "sha256": hashlib.sha256(encoded).hexdigest(),
    }


def synthetic_final_certificate() -> dict[str, Any]:
    return {
        "schema": FINAL_SCHEMA,
        "result": "FALSIFIED",
        "failed": 1,
        "holdout_state": "irreversibly-authorized-no-retry",
        "retry_permitted": False,
        "final_holdout_unsealed": True,
        "auditor_result": "PASS",
        "auditor_holdout_opened": False,
        "auditor_timing_performed": False,
        "complete_final_timing": False,
        "complete_final_summary": False,
        "complete_final_ranking_count": 0,
        "final_speed": "NOT MEASURED",
        "required_cases": 24_576,
        "complete_cases": 14_342,
        "required_raw_rows": 3_047_424,
        "observed_raw_rows": 1_778_408,
        "paired_modules_per_case": 4,
        "trials_per_module_case": 31,
        "module_order": list(FINAL_MODULES),
        "runner_exit_code": 2,
        "candidate_freeze_sha256": FINAL_CANDIDATE_FREEZE_SHA256,
        "from_scratch_audit_sha256": FINAL_FROM_SCRATCH_SHA256,
        "candidate_qualifications": copy.deepcopy(list(FINAL_QUALIFICATIONS)),
        "self_test": {
            "schema": f"{FINAL_SCHEMA}-self-test",
            "result": "PASS",
            "failed": 0,
            "holdout_opened": False,
            "timing_performed": False,
            "synthetic_only": True,
            "poisoned_control_count": FINAL_POISONED_CONTROLS,
            "poisoned_controls": [
                {"name": f"synthetic-final-control-{index}", "passed": True}
                for index in range(FINAL_POISONED_CONTROLS)
            ],
        },
    }


def synthetic_historical_report() -> dict[str, Any]:
    baseline = hashlib.sha256(b"synthetic-immutable-python-reference").hexdigest()
    measured = {
        "re:module": baseline,
        f"{RUST_MODULE}:module": HISTORICAL_SOURCES["candidates/rust_candidate.py"],
        f"{RUST_MODULE}:bridge-source": HISTORICAL_SOURCES["candidates/rust/py_bridge.c"],
        f"{RUST_MODULE}:native-source": HISTORICAL_SOURCES["candidates/rust/src/lib.rs"],
        f"{C_MODULE}:module": HISTORICAL_SOURCES["candidates/vm_candidate.py"],
        f"{ZIG_MODULE}:module": HISTORICAL_SOURCES["candidates/zig_candidate.py"],
        **HISTORICAL_NATIVE,
    }
    edges = []
    for module in public.MODULES[1:]:
        qualification = next(item for item in FINAL_QUALIFICATIONS if item["module"] == module)
        edges.append({
            "module": module,
            "correctness_checks": 223_198,
            "actual_sha256": public.EXPECTED_EDGE_ANSWER_SHA256,
            "script_sha256": public.EXPECTED_EDGE_SOURCE_SHA256,
            "stdlib_baseline_sha256": public.EXPECTED_STDLIB_EDGE_SHA256,
            "report_sha256": qualification["edge_sha256"],
            "candidate_artifacts": {
                role: {
                    "path": f"synthetic/{role}",
                    "sha256": digest,
                }
                for role, digest in qualification["native_artifact_sha256"].items()
            },
        })
    return {
        "schema": HISTORICAL_SCHEMA,
        "result": "PASS",
        "failed": 0,
        "holdout_accessed": False,
        "timing_performed": False,
        "module_order": list(public.MODULES),
        "cases_per_candidate": public.EXPECTED_CASES,
        "trials_per_module_case": public.EXPECTED_TRIALS,
        "bootstrap_draws": public.EXPECTED_BOOTSTRAPS,
        "raw_rows": public.EXPECTED_ROWS,
        "correctness_checks": public.EXPECTED_CORRECTNESS_CHECKS,
        "frozen_plan_sha256": public.EXPECTED_PLAN_SHA256,
        "source_sha256": HISTORICAL_SOURCE_SHA256,
        "summary_sha256": HISTORICAL_SUMMARY_SHA256,
        "from_scratch_audit_sha256": FINAL_FROM_SCRATCH_SHA256,
        "strict_regression_speedup_threshold": public.REGRESSION_THRESHOLD,
        "strict_regressions": 256,
        "verified_native_library_count": 5,
        "verified_independent_engine_count": 3,
        "qualified_source_fingerprints": copy.deepcopy(HISTORICAL_SOURCES),
        "native_elf_fingerprints": copy.deepcopy(HISTORICAL_NATIVE),
        "candidate_binary_sha256_before": measured,
        "candidate_binary_sha256_after": copy.deepcopy(measured),
        "verified_edge_oracles": edges,
        "self_test": {
            "result": "PASS",
            "failed": 0,
            "synthetic_only": True,
            "timing_performed": False,
            "poisoned_control_count": HISTORICAL_POISONED_CONTROLS,
            "poisoned_controls": [
                {"name": f"synthetic-history-control-{index}", "passed": True}
                for index in range(HISTORICAL_POISONED_CONTROLS)
            ],
        },
    }


def synthetic_artifacts(module: str) -> list[dict[str, str]]:
    paths = {
        RUST_MODULE: {
            "bridge-source": "candidates/rust/py_bridge.c",
            "native-bridge": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
            "native-engine": "candidates/_rust_engine.so",
            "native-source": "candidates/rust/src/lib.rs",
            "public-python": "candidates/rust_candidate.py",
        },
        C_MODULE: {
            "native-source": "candidates/_vm_native.c",
            "native-bridge": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
            "public-python": "candidates/vm_candidate.py",
        },
        ZIG_MODULE: {
            "bridge-source": "candidates/zig/py_bridge.c",
            "native-bridge": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
            "native-engine": "candidates/_zig_probe.so",
            "native-source": "candidates/zig/mini_regex.zig",
            "public-python": "candidates/zig_candidate.py",
        },
    }
    return [
        {
            "role": role,
            "path": path,
            "sha256": hashlib.sha256(f"synthetic:{module}:{role}".encode()).hexdigest(),
        }
        for role, path in sorted(paths[module].items())
    ]


def synthetic_proofs(
    module: str = RUST_MODULE,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], Path, str, Path, str]:
    edge_path = ROOT / "candidates" / "evidence" / "synthetic-post-final-edge.json.gz"
    deep_path = ROOT / "candidates" / "audits" / "SYNTHETIC-POST-FINAL-DEEP.json.gz"
    edge_sha256 = hashlib.sha256(b"synthetic-public-post-final-edge").hexdigest()
    deep_sha256 = hashlib.sha256(b"synthetic-public-post-final-deep").hexdigest()
    artifacts = synthetic_artifacts(module)
    edge_reference = {
        "archive_sha256": edge_sha256,
        "path": str(edge_path.resolve()),
        "module": module,
        "checks": 223_198,
        "failed": 0,
        "script_sha256": public.EXPECTED_EDGE_SOURCE_SHA256,
        "candidate_artifacts": copy.deepcopy(artifacts),
        "production_artifacts": copy.deepcopy(artifacts),
    }
    deep = {
        "schema": "rebar-rust-v8-deep-public-contract-v1",
        "status": "PASS",
        "candidate_module": module,
        "checks": 393,
        "public_mismatch_count": 0,
        "stdlib_vs_stdlib_mismatches": [],
        "holdout": "NOT ACCESSED",
        "performance": "NOT MEASURED",
        "cross_engine_guard_count": 10,
        "edge_oracle": copy.deepcopy(edge_reference),
        "native_artifacts": copy.deepcopy(artifacts),
    }
    observation = {
        "schema": "rebar-v8-multi-candidate-observability-v1",
        "status": "PASS",
        "candidate_module": module,
        "checks": 479,
        "candidate_checks": 479,
        "failures": [],
        "candidate_failures": 0,
        "private_binder_checks": 34,
        "private_binder_failures": [],
        "holdout": "NOT ACCESSED",
        "performance": "NOT MEASURED",
        "edge_oracle": copy.deepcopy(edge_reference),
        "deep_proof": {
            "archive_sha256": deep_sha256,
            "path": str(deep_path.resolve()),
            "candidate_module": module,
            "checks": 393,
            "status": "PASS",
            "edge_archive_sha256": edge_sha256,
        },
        "native_artifacts": copy.deepcopy(artifacts),
    }
    campaign = {
        "schema": "rebar-rust-campaign-gate-v1",
        "candidate": module,
        "passed": True,
        "holdout_accessed": False,
        "timing_performed": False,
        "performance": "NOT MEASURED",
        "required_correctness_step_count": 22,
        "steps": [
            {"name": f"synthetic-public-stage-{index}", "passed": True}
            for index in range(22)
        ],
        "pinned_cpython": "3.14.6",
        "python_executable": str(public.PINNED_PYTHON),
        "mode": "sealed-practice-only",
        "edge_oracle": copy.deepcopy(edge_reference),
        "native_artifacts": copy.deepcopy(artifacts),
    }
    return deep, observation, campaign, edge_path, edge_sha256, deep_path, deep_sha256


def self_test() -> dict[str, Any]:
    assert_no_candidates_imported()
    inherited = public.self_test()
    require(
        inherited.get("result") == "PASS"
        and inherited.get("failed") == 0
        and inherited.get("holdout_accessed") is False
        and inherited.get("timing_performed") is False,
        "the inherited in-memory four-way public replay controls did not pass",
    )
    inherited_controls = inherited.get("poisoned_controls")
    require(
        isinstance(inherited_controls, list)
        and len(inherited_controls) >= 28
        and all(isinstance(control, dict) and control.get("passed") is True for control in inherited_controls),
        "the original in-memory four-way public replay controls were omitted",
    )
    controls: list[dict[str, Any]] = [
        {"name": f"inherited-{control['name']}", "passed": True}
        for control in inherited_controls
    ]

    def reject(name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except (
            AuditError, KeyError, TypeError, ValueError, OverflowError,
            IndexError, OSError, zlib.error,
        ):
            controls.append({"name": name, "passed": True})
            return
        raise AuditError(f"synthetic poisoned post-final evidence was accepted: {name}")

    final = synthetic_final_certificate()
    validate_final_certificate(final)

    def poison_final(key: str, value: object) -> None:
        document = copy.deepcopy(final)
        document[key] = value
        validate_final_certificate(document)

    for name, key, value in (
        ("original-final-falsified-replaced-with-pass", "result", "PASS"),
        ("original-final-retry-authorized", "retry_permitted", True),
        ("original-final-no-retry-state-substituted", "holdout_state", "retry-authorized"),
        ("original-final-winner-fabricated", "winner", RUST_MODULE),
        ("original-final-speed-fabricated", "final_speed", "2x faster"),
        ("original-final-summary-fabricated", "complete_final_summary", True),
        ("original-final-timing-fabricated", "complete_final_timing", True),
        ("original-final-ranking-fabricated", "complete_final_ranking_count", 1),
        ("original-final-opening-concealed", "final_holdout_unsealed", False),
        ("original-final-historical-case-count-substituted", "complete_cases", 24_576),
        ("original-final-row-count-substituted", "observed_raw_rows", 3_047_424),
        ("original-final-required-cases-substituted", "required_cases", 624),
        ("original-final-trial-count-substituted", "trials_per_module_case", 7),
        ("original-final-engine-order-substituted", "module_order", list(public.MODULES)),
        ("original-final-runner-failure-concealed", "runner_exit_code", 0),
        ("original-final-candidate-freeze-substituted", "candidate_freeze_sha256", "0" * 64),
        ("original-final-independence-audit-substituted", "from_scratch_audit_sha256", "0" * 64),
        ("original-final-independent-verifier-opened-holdout", "auditor_holdout_opened", True),
        ("original-final-independent-verifier-timed-candidates", "auditor_timing_performed", True),
        ("original-final-failure-schema-substituted", "schema", SCHEMA),
    ):
        reject(name, lambda key=key, value=value: poison_final(key, value))

    def poison_final_qualification() -> None:
        document = copy.deepcopy(final)
        document["candidate_qualifications"][1]["native_artifact_sha256"][
            "native-engine"
        ] = "0" * 64
        validate_final_certificate(document)

    reject("original-final-frozen-rust-engine-rewritten", poison_final_qualification)

    historical = synthetic_historical_report()
    validate_historical_report(historical)

    def poison_history(key: str, value: object) -> None:
        document = copy.deepcopy(historical)
        document[key] = value
        validate_historical_report(document)

    for name, key, value in (
        ("historical-v9-schema-substituted", "schema", SCHEMA),
        ("historical-v9-failure-concealed", "result", "FAIL"),
        ("historical-v9-original-audit-substituted", "from_scratch_audit_sha256", "0" * 64),
        ("historical-v9-auditor-source-substituted", "source_sha256", "0" * 64),
        ("historical-v9-summary-substituted", "summary_sha256", "0" * 64),
        ("historical-v9-frozen-public-plan-substituted", "frozen_plan_sha256", "0" * 64),
        ("historical-v9-genuine-256-losses-concealed", "strict_regressions", 0),
        ("historical-v9-five-native-libraries-omitted", "verified_native_library_count", 4),
        ("historical-v9-independent-engine-omitted", "verified_independent_engine_count", 2),
        ("historical-v9-bootstrap-draws-substituted", "bootstrap_draws", 500),
        ("historical-v9-correctness-check-omitted", "correctness_checks", public.EXPECTED_CORRECTNESS_CHECKS - 1),
        ("historical-v9-frozen-source-map-substituted", "qualified_source_fingerprints", {}),
        ("historical-v9-frozen-native-map-substituted", "native_elf_fingerprints", {}),
        ("historical-v9-matching-proof-omitted", "verified_edge_oracles", []),
    ):
        reject(name, lambda key=key, value=value: poison_history(key, value))

    plan, summary, compressed, profile = public.synthetic_evidence()
    raw_path = PRACTICE_EVIDENCE / f"{DEFAULT_SLOT}-raw.jsonl.gz"
    summary = {
        **summary,
        "exclusive_slot": DEFAULT_SLOT,
        "raw_path": str(raw_path.resolve()),
        "measurement": (
            "balanced practice diagnostic only; not a holdout result or final speed claim"
        ),
    }

    def replay(current_summary: dict[str, Any], payload: bytes = compressed) -> None:
        public.validate_plan(plan, profile)
        validate_postfinal_header(current_summary, plan, profile, raw_path, DEFAULT_SLOT)
        observations = public.read_observations(
            io.BytesIO(payload), hashlib.sha256(payload).hexdigest(),
            current_summary, plan, profile,
        )
        results, rankings = public.recompute_results(plan, observations, profile)
        public.validate_results(current_summary, results, rankings, profile)

    replay(summary)

    def poison_summary(key: str, value: object) -> None:
        document = copy.deepcopy(summary)
        document[key] = value
        replay(document)

    for name, key, value in (
        ("post-final-exclusive-slot-substituted", "exclusive_slot", "three-qualified-engines-public-practice-v9"),
        ("post-final-exclusive-slot-omitted", "exclusive_slot", None),
        ("post-final-public-raw-path-substituted", "raw_path", str(HISTORICAL_PATH)),
        ("post-final-practice-claimed-as-original-final", "measurement", "complete successful final holdout"),
        ("post-final-public-engine-omitted", "modules", list(public.MODULES[:-1])),
        ("post-final-public-engine-reordered", "modules", list(FINAL_MODULES)),
        ("post-final-public-correctness-check-omitted", "correctness_checks", profile.rows * 3 - 1),
        ("post-final-public-bootstrap-draw-substituted", "bootstrap_samples", profile.bootstraps + 1),
        ("post-final-public-paired-trial-omitted", "trials", profile.trials - 1),
        ("post-final-public-raw-row-omitted", "paired_raw_rows", profile.rows - 1),
        ("post-final-public-denominator-fabricated", "cases", 625),
        ("post-final-public-compressed-hash-substituted", "compressed_raw_sha256", "0" * 64),
        ("post-final-public-raw-hash-substituted", "raw_sha256", "0" * 64),
        ("post-final-public-losses-concealed", "regressions", []),
        ("post-final-public-case-result-omitted", "case_results", summary["case_results"][:-1]),
        ("post-final-public-ranking-omitted", "rankings", summary["rankings"][:-1]),
        ("post-final-public-holdout-access-concealed", "holdout_accessed", True),
        ("post-final-public-correctness-failure-concealed", "failed", 1),
    ):
        reject(name, lambda key=key, value=value: poison_summary(key, value))

    deep, observation, campaign, edge_path, edge_sha256, deep_path, deep_sha256 = synthetic_proofs()
    validate_deep_shape(deep, RUST_MODULE, edge_path, edge_sha256)
    validate_observability_shape(
        observation, RUST_MODULE, edge_path, edge_sha256,
        deep_path, deep_sha256,
    )
    validate_campaign_shape(campaign, RUST_MODULE, edge_path, edge_sha256)

    def poison_deep(key: str, value: object) -> None:
        document = copy.deepcopy(deep)
        document[key] = value
        validate_deep_shape(document, RUST_MODULE, edge_path, edge_sha256)

    for name, key, value in (
        ("post-final-rust-deep-schema-substituted", "schema", "external-deep-contract"),
        ("post-final-rust-deep-family-substituted", "candidate_module", C_MODULE),
        ("post-final-rust-deep-obligation-omitted", "checks", 392),
        ("post-final-rust-deep-public-mismatch-concealed", "public_mismatch_count", 1),
        ("post-final-rust-deep-holdout-access", "holdout", "ACCESSED"),
        ("post-final-rust-deep-performance-timing", "performance", "MEASURED"),
        ("post-final-rust-deep-cross-engine-guard-omitted", "cross_engine_guard_count", 9),
        ("post-final-rust-deep-production-artifact-omitted", "native_artifacts", deep["native_artifacts"][:-1]),
    ):
        reject(name, lambda key=key, value=value: poison_deep(key, value))

    def poison_observation(key: str, value: object) -> None:
        document = copy.deepcopy(observation)
        document[key] = value
        validate_observability_shape(
            document, RUST_MODULE, edge_path, edge_sha256,
            deep_path, deep_sha256,
        )

    for name, key, value in (
        ("post-final-rust-observability-schema-substituted", "schema", "external-observability"),
        ("post-final-rust-observability-family-substituted", "candidate_module", ZIG_MODULE),
        ("post-final-rust-observability-obligation-omitted", "checks", 478),
        ("post-final-rust-observability-candidate-obligation-omitted", "candidate_checks", 478),
        ("post-final-rust-observability-failure-concealed", "candidate_failures", 1),
        ("post-final-rust-native-binder-obligation-omitted", "private_binder_checks", 33),
        ("post-final-rust-native-binder-failure-concealed", "private_binder_failures", [{"failed": True}]),
        ("post-final-rust-observability-holdout-access", "holdout", "ACCESSED"),
        ("post-final-rust-observability-performance-timing", "performance", "MEASURED"),
        ("post-final-rust-observability-deep-chain-omitted", "deep_proof", None),
    ):
        reject(name, lambda key=key, value=value: poison_observation(key, value))

    def poison_campaign(key: str, value: object) -> None:
        document = copy.deepcopy(campaign)
        document[key] = value
        validate_campaign_shape(document, RUST_MODULE, edge_path, edge_sha256)

    for name, key, value in (
        ("post-final-rust-full-campaign-schema-substituted", "schema", "external-campaign"),
        ("post-final-rust-full-campaign-family-substituted", "candidate", ZIG_MODULE),
        ("post-final-rust-full-campaign-failed", "passed", False),
        ("post-final-rust-full-campaign-step-omitted", "steps", campaign["steps"][:-1]),
        ("post-final-rust-full-campaign-denominator-substituted", "required_correctness_step_count", 21),
        ("post-final-rust-full-campaign-holdout-access", "holdout_accessed", True),
        ("post-final-rust-full-campaign-performance-timing", "timing_performed", True),
        ("post-final-rust-full-campaign-unsealed-mode", "mode", "holdout"),
        ("post-final-rust-full-campaign-python-substituted", "pinned_cpython", "3.13.0"),
        ("post-final-rust-full-campaign-matching-proof-omitted", "edge_oracle", None),
    ):
        reject(name, lambda key=key, value=value: poison_campaign(key, value))

    reject("post-final-slot-claims-a-holdout", lambda: validate_slot("postfinal-holdout-retry"))
    reject("post-final-slot-claims-a-protocol", lambda: validate_slot("postfinal-protocol-open"))
    reject("post-final-slot-claims-a-manifest", lambda: validate_slot("postfinal-manifest-open"))
    reject("post-final-slot-path-escapes-public-evidence", lambda: validate_slot("postfinal-../../escape"))
    reject(
        "post-final-public-output-escapes-authorized-directory",
        lambda: authorized_path(
            ROOT / "performance" / "v9" / "evidence" / "forbidden.json",
            PRACTICE_EVIDENCE,
            "synthetic post-final output",
        ),
    )
    require(len(controls) >= 100, "the post-final replay omitted a required synthetic anti-tamper control")
    names = [control["name"] for control in controls]
    require(len(names) == len(set(names)), "the post-final anti-tamper controls contain a duplicate")
    assert_no_candidates_imported()
    return {
        "schema": SELF_TEST_SCHEMA,
        "result": "PASS",
        "failed": 0,
        "synthetic_only": True,
        "holdout_accessed": False,
        "timing_performed": False,
        "candidate_imported": False,
        "original_final_remains_falsified": True,
        "original_final_retry_permitted": False,
        "original_final_winner": None,
        "inherited_public_replay_control_count": len(inherited_controls),
        "poisoned_control_count": len(controls),
        "poisoned_controls": controls,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Independently replay additive post-final, four-way public Rust "
            "practice without reopening, retrying, or rewriting the FALSIFIED final."
        ),
    )
    parser.add_argument("--self-test", action="store_true", help="run synthetic in-memory tamper controls only")
    parser.add_argument("--slot", default=DEFAULT_SLOT, help="exclusive additive post-final public slot")
    parser.add_argument("--raw", type=Path, default=DEFAULT_RAW, help="explicit post-final public gzip observations")
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY, help="explicit post-final public-practice summary")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="new exclusive additive post-final integrity report")
    parser.add_argument("--failure-certificate", "--failure", "--final-failure", type=Path, default=FINAL_FAILURE_PATH, help="exact immutable historical final failure certificate only")
    parser.add_argument("--historical-v9-integrity", "--historical-integrity", type=Path, default=HISTORICAL_PATH, help="immutable historical public-practice v9 integrity report")
    parser.add_argument("--from-scratch-audit", "--audit", type=Path, default=public.AUDIT_PATH, help="fresh original all-five-native-library independence report")
    parser.add_argument("--plan", type=Path, default=public.PLAN_PATH, help="frozen public-only calibration plan")
    parser.add_argument("--plan-sha256", default=None, help="independent SHA-256; mandatory for explicitly expanded public plans")
    parser.add_argument("--expanded-case-count", "--expanded-cases", type=int, default=None, help="explicit separately measured public denominator strictly greater than 624")
    parser.add_argument("--rust-edge", "--edge", type=Path, default=DEFAULT_RUST_EDGE, help="fresh source-bound post-final Rust public matching report")
    parser.add_argument("--rust-deep", "--deep", type=Path, default=DEFAULT_RUST_DEEP, help="fresh source-bound post-final Rust 393-obligation deep report")
    parser.add_argument("--rust-observability", "--observability", type=Path, default=DEFAULT_RUST_OBSERVABILITY, help="fresh source-bound post-final Rust 479-obligation observability report")
    parser.add_argument("--rust-campaign", "--campaign", type=Path, default=DEFAULT_RUST_CAMPAIGN, help="fresh source-bound post-final Rust complete 22-stage public campaign")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = self_test() if args.self_test else verify(args)
    except (
        AuditError, KeyError, TypeError, ValueError, OverflowError,
        IndexError, OSError, zlib.error,
    ) as error:
        print(
            json.dumps(
                {
                    "schema": SELF_TEST_SCHEMA if args.self_test else SCHEMA,
                    "result": "FAIL",
                    "failed": 1,
                    "post_final": True,
                    "original_final_result": "FALSIFIED",
                    "retry_permitted": False,
                    "final_winner": None,
                    "holdout_accessed": False,
                    "timing_performed": False,
                    "error": str(error),
                },
                sort_keys=True,
                ensure_ascii=True,
                separators=(",", ":"),
            ),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(result, sort_keys=True, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
