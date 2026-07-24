#!/usr/bin/env python3
"""Present only independently replayed, current-source V6 public results."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import stat
import sys
import xml.etree.ElementTree as ElementTree
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from tools import postfinal_public_practice_presentation_v1 as primitives


ROOT = Path(__file__).resolve().parent.parent
VERSION = "postfinal-public-practice-v6"
PRESENTATION_VERSION = "postfinal-public-practice-presentation-v2"
PUBLIC_ROOT = ROOT / "performance" / "postfinal-public-v6"
EVIDENCE = PUBLIC_ROOT / "evidence"
MANIFEST = PUBLIC_ROOT / "manifest.json"
SUMMARY = EVIDENCE / f"{VERSION}-summary.json"
INTEGRITY = EVIDENCE / f"{VERSION}-integrity.json"
RAW = EVIDENCE / f"{VERSION}-raw.jsonl.gz"
RUNNER = ROOT / "tools" / "postfinal_public_practice_v6.py"
PRIMITIVE_SOURCE = ROOT / "tools" / "postfinal_public_practice_presentation_v1.py"
PRIMITIVE_SOURCE_SHA256 = (
    "53538d3a501388281b1603866f1336cb2ede067f2899a45b6c56c5a12d110842"
)

PLAN_SCHEMA = "rebar-rust-balanced-calibration-plan-v7"
PLAN_POSTFINAL_SCHEMA = "rebar-postfinal-public-practice-plan-v6"
SUMMARY_SCHEMA = "rebar-rust-balanced-calibration-pilot-v7"
SUMMARY_POSTFINAL_SCHEMA = "rebar-postfinal-public-practice-report-v6"
INTEGRITY_SCHEMA = "rebar-postfinal-public-practice-integrity-v6"

CASES = 8_192
CATEGORIES = 260
TRIALS = 13
WARMUPS = 4
BOOTSTRAPS = 2_000
MODULES = (
    "re",
    "candidates.rust_candidate",
    "candidates.vm_candidate",
    "candidates.zig_candidate",
)
CANDIDATES = MODULES[1:]
RAW_ROWS = CASES * TRIALS * len(MODULES)
CORRECTNESS_CHECKS = RAW_ROWS * 3
CONFIDENCE_INTERVALS = CASES * len(CANDIDATES) + len(CANDIDATES)
RUNTIME_GUARDS = len(MODULES) * (2 + 2 * CASES)
REGRESSION_THRESHOLD = 5.0 / 6.0
SPEED_TARGET = 1.5
FASTER_CASE_TARGET = (3 * CASES + 4) // 5
MAX_EVIDENCE_BYTES = 64 * 1024 * 1024
OPERATIONS = {
    "compile": 210,
    "escape": 161,
    "findall": 2_040,
    "finditer": 2_041,
    "fullmatch": 358,
    "match": 229,
    "match-surface": 241,
    "scanner": 427,
    "search": 1_057,
    "split": 451,
    "sub": 447,
    "subn": 530,
}
SUFFIXES = ("overall", "outcomes", "api", "regressions", "memory", "rankings")
LABELS = {
    "candidates.rust_candidate": "Rust",
    "candidates.vm_candidate": "C",
    "candidates.zig_candidate": "Zig",
}
COLORS = {
    "candidates.rust_candidate": "#d17852",
    "candidates.vm_candidate": "#238b86",
    "candidates.zig_candidate": "#7766c9",
}
FOOTER = "Public benchmark only; fresh final test unopened; no final winner."
MEMORY_LIMITATION = (
    "Tracemalloc reports Python-visible temporary allocations. "
    "RSS and high-water marks are process-level observations in "
    "separate dedicated engine workers; they do not establish exact "
    "per-allocation native-engine memory."
)
SVG_NAMESPACE = "http://www.w3.org/2000/svg"

BASE_AUDIT_PATH = ROOT / "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json"
BASE_AUDIT_SHA256 = (
    "5e299a767cbd494683100519a6ad461d1a0eb9de1564b1437c7e0229cca7a551"
)
BASE_AUDIT_SOURCE_PATH = ROOT / "tools/postfinal_from_scratch_audit_v2.py"
BASE_AUDIT_SOURCE_SHA256 = (
    "6f540074c9f7f4bdffe9e53939efe4cec25e5c029ca1f73ec791d377bddc9306"
)
STRICT_AUDIT_PATH = ROOT / "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V2.json"
STRICT_AUDIT_SHA256 = (
    "183cd04f5e1587c181505c09867566b4bd18db270f974475c2b456ff09af1d9f"
)
STRICT_AUDIT_SOURCE_PATH = ROOT / "tools/postfinal_no_delegation_audit_v2.py"
STRICT_AUDIT_SOURCE_SHA256 = (
    "571c11885f9c9694025ea0434e57bfaa56651057eee62fa4396a2bcb95ae4cb5"
)
STRICT_AUDIT_SCHEMA = "rebar-postfinal-no-delegation-audit-v2"
GUARDED_WORKER_SOURCE = ROOT / "tools/postfinal_no_delegation_audit_v1.py"
GUARDED_WORKER_SOURCE_SHA256 = (
    "e505e17f4849242d990ee8e184794962327335d807000d1a8a0e65a0cb10c0ed"
)
GUARDED_WORKER_REPORT = ROOT / "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V1.json"
GUARDED_WORKER_REPORT_SHA256 = (
    "c4605c8af5da805c099b1efb7f15e8390781768bb3014276b465a7712b4ed06b"
)
GUARDED_WORKER_SCHEMA = "rebar-postfinal-no-delegation-audit-v1"

UNIVERSAL_SOURCE = ROOT / "tools/python_re_universal_public_oracle_stage04.py"
UNIVERSAL_SOURCE_SHA256 = (
    "922de8886671e5bfc9db58ba92c134f4bf76b06acb01476f6fc9a9e3321815a6"
)
UNIVERSAL_REPORT = ROOT / "candidates/evidence/python-re-universal-public-oracle-v4-all.json"
UNIVERSAL_REPORT_SHA256 = (
    "facb736a3409f459cdc812e6dc740df399f98ebb84745a22b615ef130ccdb137"
)
FROZEN_ORACLE_SOURCE = ROOT / "tools/python_re_universal_public_oracle_v1.py"
FROZEN_ORACLE_SOURCE_SHA256 = (
    "744876e5b8409b8d49982ccfb61d93a99f3e2d4fd64d0543b29b831bd26796a0"
)
UNIVERSAL_CASE_SHA256 = (
    "8e5c120a4e637c30940363e20d6042324d65d9f7d03fbd35240ffabf2df282ae"
)

EXPECTED_NATIVE = {
    "candidates.rust_candidate:native-bridge": (
        "81fc4c4a92005f0588dd9b811988587d4d421dd8e1102eebcab53f4deb27cd36"
    ),
    "candidates.rust_candidate:native-engine": (
        "83394c5c3b5d9e9d98c8474aac60ca5a81517dc7ec7c53b3b625e6ed0a04c165"
    ),
    "candidates.vm_candidate:native-engine": (
        "6922d0869b67c82be9ae89a8f00c71777c04472d3606a33527bb13494326f18d"
    ),
    "candidates.zig_candidate:native-bridge": (
        "32dadc46281d13df784693f0785d4d149e6d3cd000aa3de6eb220a4a9ed50c9c"
    ),
    "candidates.zig_candidate:native-engine": (
        "474dde0bfb23f107f21ec4834ce15dbd1b437841bd171698de623d1c03742988"
    ),
}
EXPECTED_NATIVE_PATHS = {
    "candidates.rust_candidate:native-bridge": (
        ROOT / "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so"
    ),
    "candidates.rust_candidate:native-engine": ROOT / "candidates/_rust_engine.so",
    "candidates.vm_candidate:native-engine": (
        ROOT / "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so"
    ),
    "candidates.zig_candidate:native-bridge": (
        ROOT / "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so"
    ),
    "candidates.zig_candidate:native-engine": ROOT / "candidates/_zig_probe.so",
}
EXPECTED_SOURCES = {
    "candidates/_vm_native.c": (
        "0f55f704a93b273422295b4ccdc55194ba696cbf79d1d8b6d57abfe68f2e8dcb"
    ),
    "candidates/rust/py_bridge.c": (
        "3d432d8f53a75eb2c3c75d118c811ac7ba12c432d987422223d55773fbb36abe"
    ),
    "candidates/rust/src/lib.rs": (
        "398773b8542c88cfc55fe13ceac1e84a00155217b76b8461ddf9704d2f6c82c5"
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
        "ed210957f3fc7a8d87ce38cfc775cd380bed19dcde7e8acd23d09197abb60048"
    ),
    "candidates/vm_candidate.py": (
        "ef00948bb6138342501fbfef4070900ce1b4a57ecf9d805fc897fedcb36978d0"
    ),
    "candidates/zig/mini_regex.zig": (
        "8e961fbda077efb300ecfa90744519884171f93503f7128326b520ddc9da856a"
    ),
    "candidates/zig/py_bridge.c": (
        "17d8578bbc1e73db84aa59755bf3c8add2801066d238e506c0e6f16efa920568"
    ),
    "candidates/zig_candidate.py": (
        "b7330484e8436adc91d1d0960745a54be94752eb7f7fc7fbf747ddfa3cb80d6b"
    ),
}
EXPECTED_PROOFS: dict[str, tuple[str, str]] = {
    "rust-edge": (
        "candidates/evidence/rust-v7-edge-oracle-rust-postfinal-inline-state-v1.json.gz",
        "e728155608744a364c40b79acd552ff68fb88edf1b77db589bc2fc9ac88f2e28",
    ),
    "rust-deep-public-contract": (
        "candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-INLINE-STATE-V1.json.gz",
        "5a8f105f43e48106e3226a16e4d6cfc7690788734257528ea5b8830920cc60fb",
    ),
    "rust-observability": (
        "candidates/evidence/rust-v8-observability-rust-qualified-postfinal-inline-state-v1.json.gz",
        "434ddb1726485daf47107c34069a71167085fe58122aa3c5026cc70f16640612",
    ),
    "rust-complete-correctness-campaign": (
        "candidates/evidence/rust-v8-rust-postfinal-inline-state-v1-sealed-campaign.json",
        "e18169d8bbdf0feefc655527a210848cdb9053da5a2c996fc28f413d772809c6",
    ),
    "vm-edge": (
        "candidates/evidence/rust-v7-edge-oracle-vm-post-final-stage-05-universal-parity.json.gz",
        "05941ba203d777ec81e97ef8b97d0b27fe64a961a1ac12e8e470053fc23e52e4",
    ),
    "vm-deep-public-contract": (
        "candidates/audits/RUST-V8-DEEP-CONTRACT-C-POST-FINAL-STAGE-05-UNIVERSAL-PARITY.json.gz",
        "b1606a8076630650cd6092abbc3916c2755f4f0af071bc8861ff87a89b9e7207",
    ),
    "vm-observability": (
        "candidates/evidence/rust-v8-observability-vm-qualified-post-final-stage-05-universal-parity.json.gz",
        "ff5c563614900437375068b763aa40bf6557a943d4990bc5d86d3a94faa5255c",
    ),
    "vm-complete-correctness-campaign": (
        "candidates/evidence/rust-v8-vm-post-final-stage-05-universal-parity-sealed-campaign.json",
        "972ea7b8fb2618b389d7acdc5875bae81b2c0e3e568150dd298694d37ef16dc4",
    ),
    "zig-edge": (
        "candidates/evidence/rust-v7-edge-oracle-zig-post-final-stage-05-universal-parity.json.gz",
        "e348d7cfa16ee32c0ed202691bf65d0862fbc8b5da23065fdfe3dc1c857a7327",
    ),
    "zig-deep-public-contract": (
        "candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-POST-FINAL-STAGE-05-UNIVERSAL-PARITY.json.gz",
        "0c18b9c8222b0b642a95ebc3793cc48f3eb135842f35c4b370fd05bb45da1a41",
    ),
    "zig-observability": (
        "candidates/evidence/rust-v8-observability-zig-qualified-post-final-stage-05-universal-parity.json.gz",
        "4e31f020a3def0f125562af9010bbb54cd299ddf81fde33dff61219fd7d6c0c3",
    ),
    "zig-complete-correctness-campaign": (
        "candidates/evidence/rust-v8-zig-post-final-stage-05-universal-parity-sealed-campaign.json",
        "ecd9ea26e30ddc728e029ff30e9e849e94f45c94acabc2039c7017a697a99686",
    ),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def valid_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def require_candidate_free() -> None:
    loaded = [
        name
        for name in sys.modules
        if any(name == candidate or name.startswith(candidate + ".") for candidate in CANDIDATES)
    ]
    require(not loaded, "the public V6 presenter imported a production engine")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, "a verified public V6 JSON key was duplicated")
        result[key] = value
    return result


def reject_json_constant(value: str) -> None:
    raise ValueError(f"a verified public V6 JSON number is nonfinite: {value}")


def synthetic_sha(label: str) -> str:
    return hashlib.sha256(
        f"synthetic-public-v6-presentation-only:{label}".encode("utf-8")
    ).hexdigest()


def canonical_sha256(document: dict[str, Any]) -> str:
    payload = json.dumps(
        document,
        sort_keys=True,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def read_verified_bytes(path: Path, *, expected: Path, digest: str) -> bytes:
    require(isinstance(path, Path), "an exact public V6 evidence path is missing")
    require(path.resolve() == expected.resolve(), "a public V6 evidence path was substituted")
    require(not path.is_symlink(), "a public V6 evidence path is a symbolic link")
    require(valid_sha256(digest), "a public V6 evidence fingerprint is invalid")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode), "public V6 evidence is not a regular file")
        require(
            0 < before.st_size <= MAX_EVIDENCE_BYTES,
            "public V6 evidence exceeds its explicit bounded size",
        )
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(1024 * 1024, MAX_EVIDENCE_BYTES - total + 1))
            if not chunk:
                break
            total += len(chunk)
            require(total <= MAX_EVIDENCE_BYTES, "public V6 evidence exceeded its size limit")
            chunks.append(chunk)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    before_identity = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
        before.st_ctime_ns,
    )
    after_identity = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    )
    require(before_identity == after_identity, "public V6 evidence changed while being read")
    payload = b"".join(chunks)
    require(len(payload) == before.st_size, "public V6 evidence is incomplete")
    require(
        hashlib.sha256(payload).hexdigest() == digest,
        "the exact public V6 evidence fingerprint changed",
    )
    return payload


def read_verified_json(path: Path, *, expected: Path, digest: str) -> dict[str, Any]:
    payload = read_verified_bytes(path, expected=expected, digest=digest)
    result = json.loads(
        payload.decode("utf-8"),
        object_pairs_hook=unique_object,
        parse_constant=reject_json_constant,
    )
    require(isinstance(result, dict), "verified public V6 evidence is not a JSON object")
    return result


def verify_visual_primitives() -> None:
    require_candidate_free()
    imported = Path(getattr(primitives, "__file__", "")).resolve()
    require(imported == PRIMITIVE_SOURCE.resolve(), "the inherited visual source was substituted")
    read_verified_bytes(
        PRIMITIVE_SOURCE,
        expected=PRIMITIVE_SOURCE,
        digest=PRIMITIVE_SOURCE_SHA256,
    )
    require(
        primitives.SUFFIXES == SUFFIXES
        and primitives.LABELS == LABELS
        and primitives.COLORS == COLORS,
        "the inherited public visual primitives changed",
    )
    require_candidate_free()


@dataclass(frozen=True)
class PublicResults:
    manifest: dict[str, Any]
    summary: dict[str, Any]
    integrity: dict[str, Any]
    rankings: tuple[dict[str, Any], ...]
    rows_by_candidate: dict[str, tuple[dict[str, Any], ...]]
    losses_by_candidate: dict[str, tuple[dict[str, Any], ...]]
    operations: dict[str, int]
    regression_count: int


def require_audit_binding(
    document: dict[str, Any], *, reference: dict[str, Any], manifest: bool = False
) -> None:
    expected: dict[str, Any] = {
        "from_scratch_audit_sha256": BASE_AUDIT_SHA256,
        "from_scratch_audit_source_path": str(BASE_AUDIT_SOURCE_PATH.resolve()),
        "from_scratch_audit_source_sha256": BASE_AUDIT_SOURCE_SHA256,
        "postfinal_no_delegation_audit_path": str(STRICT_AUDIT_PATH.resolve()),
        "postfinal_no_delegation_audit_sha256": STRICT_AUDIT_SHA256,
        "postfinal_no_delegation_audit_source_path": str(STRICT_AUDIT_SOURCE_PATH.resolve()),
        "postfinal_no_delegation_audit_source_sha256": STRICT_AUDIT_SOURCE_SHA256,
        "postfinal_no_delegation_audit_schema": STRICT_AUDIT_SCHEMA,
        "postfinal_no_delegation_control_count": 32,
        "postfinal_guarded_worker_source_path": str(GUARDED_WORKER_SOURCE.resolve()),
        "postfinal_guarded_worker_source_sha256": GUARDED_WORKER_SOURCE_SHA256,
        "postfinal_guarded_worker_schema": GUARDED_WORKER_SCHEMA,
        "postfinal_guarded_worker_report_path": str(GUARDED_WORKER_REPORT.resolve()),
        "postfinal_guarded_worker_report_sha256": GUARDED_WORKER_REPORT_SHA256,
    }
    if manifest:
        expected["from_scratch_audit_path"] = str(BASE_AUDIT_PATH.resolve())
    for field, value in expected.items():
        require(
            document.get(field) == value and type(document.get(field)) is type(value),
            f"the public V6 independently owned {field} was substituted",
        )
        if field in reference:
            require(document[field] == reference[field], f"the V6 replay changed {field}")


def require_universal(document: dict[str, Any], reference: dict[str, Any]) -> None:
    expected: dict[str, Any] = {
        "python_re_universal_oracle_source_path": str(UNIVERSAL_SOURCE.resolve()),
        "python_re_universal_oracle_source_sha256": UNIVERSAL_SOURCE_SHA256,
        "python_re_universal_oracle_report_path": str(UNIVERSAL_REPORT.resolve()),
        "python_re_universal_oracle_report_sha256": UNIVERSAL_REPORT_SHA256,
        "python_re_universal_oracle_schema": "rebar-python-re-universal-public-oracle-v1",
        "python_re_universal_oracle_status": "PASS",
        "python_re_universal_oracle_selected": "all",
        "python_re_universal_oracle_candidates": ["rust", "vm", "zig"],
        "python_re_universal_oracle_cases": CASES,
        "python_re_universal_oracle_comparisons_per_case": 48,
        "python_re_universal_oracle_comparisons_per_candidate": CASES * 48,
        "python_re_universal_oracle_total_comparisons": CASES * 48 * len(CANDIDATES),
        "python_re_universal_oracle_mismatches": 0,
        "python_re_universal_oracle_seed": 2026072417,
        "python_re_universal_oracle_seed_domain": "rebar/python-re/universal-public/v1",
        "python_re_universal_oracle_case_sha256": UNIVERSAL_CASE_SHA256,
        "python_re_universal_oracle_grammar_family_count": 16,
        "python_re_universal_oracle_input_stratum_count": 16,
        "python_re_universal_oracle_examples_per_stratum": 32,
        "python_re_universal_oracle_original_audit_sha256": BASE_AUDIT_SHA256,
        "python_re_universal_oracle_postfinal_no_delegation_audit_sha256": (
            STRICT_AUDIT_SHA256
        ),
        "python_re_universal_oracle_frozen_source_path": str(
            FROZEN_ORACLE_SOURCE.resolve()
        ),
        "python_re_universal_oracle_frozen_source_sha256": FROZEN_ORACLE_SOURCE_SHA256,
    }
    require(len(expected) == 23, "the complete current Python comparison was weakened")
    for field, value in expected.items():
        require(
            document.get(field) == value and type(document.get(field)) is type(value),
            f"the current all-candidate public Python proof changed {field}",
        )
        require(
            reference.get(field) == value,
            f"the independently replayed public Python proof changed {field}",
        )


def require_correctness_proofs(document: dict[str, Any], reference: dict[str, Any]) -> None:
    artifacts = document.get("stage05_correctness_artifacts")
    require(
        isinstance(artifacts, list)
        and len(artifacts) == len(EXPECTED_PROOFS) == len(CANDIDATES) * 4,
        "a current V6 candidate correctness proof is missing",
    )
    seen: set[str] = set()
    for artifact in artifacts:
        require(isinstance(artifact, dict), "a public V6 correctness proof is invalid")
        role = artifact.get("role")
        require(
            isinstance(role, str) and role in EXPECTED_PROOFS and role not in seen,
            "a public V6 correctness proof was omitted, shared, or duplicated",
        )
        expected_path, expected_sha256 = EXPECTED_PROOFS[role]
        require(
            artifact.get("path") == expected_path
            and artifact.get("sha256") == expected_sha256,
            f"the source-bound public V6 {role} correctness proof changed",
        )
        seen.add(role)
    require(seen == set(EXPECTED_PROOFS), "a public V6 candidate proof family is incomplete")
    require(
        artifacts == reference.get("stage05_correctness_artifacts"),
        "the independent V6 replay substituted a complete correctness proof",
    )
    edges = document.get("verified_edge_oracles")
    require(
        isinstance(edges, list) and len(edges) == len(CANDIDATES),
        "a public V6 independently verified candidate edge oracle is missing",
    )
    seen_modules: set[str] = set()
    for edge in edges:
        require(isinstance(edge, dict), "a public V6 candidate edge oracle is invalid")
        module = edge.get("module")
        require(
            module in CANDIDATES and module not in seen_modules,
            "a public V6 candidate edge oracle was substituted or shared",
        )
        family = {CANDIDATES[0]: "rust", CANDIDATES[1]: "vm", CANDIDATES[2]: "zig"}[module]
        require(
            edge.get("path") == str((ROOT / EXPECTED_PROOFS[f"{family}-edge"][0]).resolve())
            and valid_sha256(edge.get("report_sha256")),
            f"the public V6 {family} runtime edge oracle changed",
        )
        seen_modules.add(module)
    require(
        edges == reference.get("verified_edge_oracles"),
        "the independently replayed public V6 edge evidence changed",
    )


def validate_documents(
    manifest: dict[str, Any],
    summary: dict[str, Any],
    integrity: dict[str, Any],
    *,
    manifest_sha256: str,
    summary_sha256: str,
    integrity_sha256: str,
    runner_sha256: str,
) -> PublicResults:
    """Reconcile every current V6 case against its genuine independent replay."""

    require_candidate_free()
    for label, digest in (
        ("frozen manifest", manifest_sha256),
        ("measured summary", summary_sha256),
        ("independent integrity replay", integrity_sha256),
        ("frozen runner", runner_sha256),
    ):
        require(valid_sha256(digest), f"the externally supplied V6 {label} hash is invalid")

    require(
        manifest.get("schema") == PLAN_SCHEMA
        and manifest.get("postfinal_schema") == PLAN_POSTFINAL_SCHEMA,
        "the frozen public V6 plan schema was substituted",
    )
    require(
        summary.get("schema") == SUMMARY_SCHEMA
        and summary.get("postfinal_schema") == SUMMARY_POSTFINAL_SCHEMA,
        "the measured public V6 summary schema was substituted",
    )
    require(
        integrity.get("schema") == INTEGRITY_SCHEMA and integrity.get("result") == "PASS",
        "the independent public V6 replay did not pass",
    )
    for name, document in (
        ("manifest", manifest),
        ("summary", summary),
        ("integrity", integrity),
    ):
        require(
            document.get("protocol_version") == VERSION,
            f"the public {name} is not current V6 evidence",
        )
        require(
            document.get("cohort") == "calibration",
            f"the public V6 {name} contains a nonpublic cohort",
        )
        require(
            document.get("holdout_accessed") is False
            and document.get("held_out_cases_generated") == 0
            and document.get("held_out_records_deserialized") == 0,
            f"the public V6 {name} claims hidden benchmark access",
        )
        require(
            document.get("runner_sha256") == runner_sha256,
            f"the public V6 {name} substituted its frozen runner",
        )
        require(document.get("failed") == 0, f"the public V6 {name} contains a failed check")
        require_audit_binding(document, reference=manifest, manifest=name == "manifest")
        require_universal(document, manifest)
        require_correctness_proofs(document, manifest)
        require(
            math.isclose(
                primitives.finite(document.get("strict_regression_speedup_threshold"),
                                  "public V6 slowdown threshold"),
                REGRESSION_THRESHOLD,
                rel_tol=0.0,
                abs_tol=1e-15,
            ),
            f"the public V6 {name} changed the greater-than-20-percent loss rule",
        )

    require(
        manifest.get("exclusive_slot") == VERSION
        and summary.get("exclusive_slot") == VERSION,
        "a current public V6 exclusive evidence slot was substituted",
    )
    require(manifest.get("python") == "3.14.6", "the pinned CPython baseline was changed")
    require(
        manifest.get("modules") == list(MODULES)
        and summary.get("modules") == list(MODULES)
        and integrity.get("module_order") == list(MODULES),
        "an independently owned public V6 candidate or Python baseline changed",
    )
    require(
        manifest.get("cases") == CASES and summary.get("cases") == CASES,
        "the genuine public V6 case denominator is not 8,192",
    )
    require(
        manifest.get("all_bounded_workload_categories") == CATEGORIES
        and summary.get("all_bounded_workload_categories") == CATEGORIES,
        "the current comparison does not cover all 260 workload categories",
    )
    require(
        manifest.get("public_operations") == OPERATIONS
        and summary.get("public_operations") == OPERATIONS
        and sum(OPERATIONS.values()) == CASES,
        "the frozen public V6 operation distribution was changed",
    )
    require(
        manifest.get("selection_seed") == 2026072404
        and manifest.get("order_seed") == 2026072405
        and manifest.get("bootstrap_seed") == 2026072406
        and summary.get("selection_seed") == 2026072404
        and summary.get("order_seed") == 2026072405
        and summary.get("bootstrap_seed") == 2026072406,
        "a frozen public V6 workload or uncertainty seed changed",
    )
    require(
        manifest.get("frozen_trials") == TRIALS
        and manifest.get("frozen_warmups") == WARMUPS
        and manifest.get("frozen_bootstrap_samples") == BOOTSTRAPS
        and summary.get("trials") == TRIALS
        and summary.get("warmups") == WARMUPS
        and summary.get("bootstrap_samples") == BOOTSTRAPS,
        "a frozen public V6 paired-trial or confidence rule changed",
    )
    predecessor = {
        "source_public_v5_runner_path": "tools/postfinal_public_practice_v5.py",
        "source_public_v5_runner_sha256": (
            "f4294a3b5434f43a92970635a958cf3b39db0eb926adef50e242ac0f6b9a1d22"
        ),
        "source_public_v5_manifest_path": "performance/postfinal-public-v5/manifest.json",
        "source_public_v5_manifest_sha256": (
            "c9950c87079ccc1909ba4470ed573b08afe1f275b85a8932cbfe83b547b24f96"
        ),
        "public_v5_case_population_preserved": True,
        "public_v5_case_population_count": CASES,
        "public_v5_workload_category_count": CATEGORIES,
        "private_worker_wire_ensure_ascii": True,
    }
    for field, value in predecessor.items():
        require(
            manifest.get(field) == value and type(manifest.get(field)) is type(value),
            f"the exact frozen public V5 population provenance changed {field}",
        )
    require(
        isinstance(manifest.get("private_worker_wire_format"), str)
        and bool(manifest["private_worker_wire_format"]),
        "the public V6 lossless Unicode worker protocol is missing",
    )
    require(
        summary.get("manifest_path") == str(MANIFEST.resolve())
        and summary.get("manifest_sha256") == manifest_sha256
        and summary.get("raw_path") == str(RAW.resolve())
        and integrity.get("manifest_sha256") == manifest_sha256
        and integrity.get("summary_sha256") == summary_sha256,
        "the independently replayed V6 measurement escaped its frozen files",
    )
    for field in ("raw_sha256", "compressed_raw_sha256"):
        require(
            valid_sha256(summary.get(field)) and integrity.get(field) == summary[field],
            f"the independently replayed public V6 {field} changed",
        )
    require(
        summary.get("paired_raw_rows") == RAW_ROWS
        and integrity.get("raw_rows") == RAW_ROWS
        and summary.get("correctness_checks") == CORRECTNESS_CHECKS
        and integrity.get("correctness_checks") == CORRECTNESS_CHECKS,
        "the current public V6 timing or answer-check observations are incomplete",
    )
    require(
        integrity.get("cases_per_candidate") == CASES
        and integrity.get("candidate_case_count") == CASES * len(CANDIDATES)
        and integrity.get("trials_per_module_case") == TRIALS
        and integrity.get("bootstrap_draws") == BOOTSTRAPS
        and integrity.get("confidence_intervals_recomputed") == CONFIDENCE_INTERVALS,
        "the independently replayed V6 cases or confidence intervals are incomplete",
    )
    require(
        summary.get("persistent_isolated_worker_count") == len(MODULES)
        and integrity.get("persistent_isolated_worker_count") == len(MODULES)
        and summary.get("per_case_runtime_guard_checks") == RUNTIME_GUARDS
        and integrity.get("per_case_runtime_guard_checks") == RUNTIME_GUARDS,
        "an independently guarded public V6 worker was omitted",
    )
    require(
        summary.get("controller_candidate_imported") is False
        and integrity.get("controller_candidate_imported") is False
        and integrity.get("candidate_imported") is False
        and integrity.get("timing_performed") is False,
        "the independent V6 replay imported a candidate or repeated timing",
    )
    require(
        integrity.get("memory_limitation") == MEMORY_LIMITATION,
        "the public V6 replay overclaims native-engine or final memory",
    )
    require(
        integrity.get("from_scratch_control_count") == 76
        and integrity.get("verified_independent_engine_count") == len(CANDIDATES)
        and integrity.get("verified_native_library_count") == len(EXPECTED_NATIVE),
        "the complete current-source public V6 independence audit is missing",
    )
    require(
        manifest.get("native_elf_fingerprints") == EXPECTED_NATIVE
        and integrity.get("native_elf_fingerprints") == EXPECTED_NATIVE,
        "a rebuilt or substituted public V6 native engine is unqualified",
    )
    require(
        manifest.get("qualified_source_fingerprints") == EXPECTED_SOURCES
        and integrity.get("qualified_source_fingerprints") == EXPECTED_SOURCES,
        "the independently owned public V6 source fingerprints changed",
    )
    before = summary.get("candidate_binary_sha256_before")
    require(
        isinstance(before, dict)
        and bool(before)
        and before == summary.get("candidate_binary_sha256_after")
        and before == integrity.get("candidate_binary_sha256_before")
        and before == integrity.get("candidate_binary_sha256_after"),
        "a guarded public V6 native artifact changed during measurement",
    )
    controls = integrity.get("self_test")
    require(
        isinstance(controls, dict)
        and controls.get("result") == "PASS"
        and controls.get("postfinal_v6_poisoned_control_count") == 43
        and controls.get("private_worker_wire_control_count") == 7
        and controls.get("mixed_correctness_artifact_count") == 12
        and controls.get("fresh_rust_correctness_artifact_count") == 4
        and controls.get("preserved_peer_correctness_artifact_count") == 8
        and controls.get("worker_processes_started") == 0
        and controls.get("benchmark_or_timing_executed") is False,
        "the independently replayed V6 candidate-free safety controls did not pass",
    )

    selected = manifest.get("selected_cases")
    require(
        isinstance(selected, list) and len(selected) == CASES,
        "one of the frozen 8,192 public V6 cases is missing",
    )
    frozen: dict[str, dict[str, Any]] = {}
    for entry in selected:
        require(isinstance(entry, dict), "a frozen V6 public case is invalid")
        case = entry.get("case")
        require(
            isinstance(case, str)
            and case.startswith("cal.")
            and case not in frozen
            and entry.get("cohort") == "calibration"
            and entry.get("api") in OPERATIONS
            and isinstance(entry.get("category"), str)
            and valid_sha256(entry.get("expected_result_sha256"))
            and type(entry.get("frozen_operations")) is int
            and entry["frozen_operations"] > 0,
            "a frozen public V6 case was duplicated, changed, or escaped its cohort",
        )
        frozen[case] = entry
    categories = manifest.get("categories")
    require(
        isinstance(categories, dict) and len(categories) == CATEGORIES,
        "the genuine public V6 workload categories are incomplete",
    )
    require(
        Counter(entry["api"] for entry in selected) == Counter(OPERATIONS)
        and Counter(entry["category"] for entry in selected) == Counter(categories),
        "the public V6 cases changed a frozen operation or workload weight",
    )

    rows = summary.get("case_results")
    require(
        isinstance(rows, list) and len(rows) == CASES * len(CANDIDATES),
        "the measured public V6 comparison omitted a candidate case",
    )
    rows_by_candidate: dict[str, list[dict[str, Any]]] = {
        candidate: [] for candidate in CANDIDATES
    }
    losses_by_candidate: dict[str, list[dict[str, Any]]] = {
        candidate: [] for candidate in CANDIDATES
    }
    identities: set[tuple[str, str]] = set()
    for row in rows:
        require(isinstance(row, dict), "an independently replayed V6 result is invalid")
        candidate = row.get("candidate")
        case = row.get("case")
        require(
            candidate in CANDIDATES and isinstance(case, str),
            "a measured public V6 candidate or case was substituted",
        )
        identity = (candidate, case)
        require(identity not in identities, "a measured public V6 candidate case is duplicated")
        identities.add(identity)
        original = frozen.get(case)
        require(original is not None, "an unfrozen case entered the public V6 comparison")
        for field in ("api", "category", "cohort"):
            require(
                row.get(field) == original.get(field),
                f"a measured public V6 case changed its frozen {field}",
            )
        require(
            type(row.get("weight")) is int and row["weight"] == 1,
            "a measured public V6 case silently changed its weight",
        )
        speed = primitives.finite(row.get("speedup"), "public V6 case speed")
        low = primitives.finite(row.get("ci95_low"), "public V6 case interval lower bound")
        high = primitives.finite(row.get("ci95_high"), "public V6 case interval upper bound")
        require(low <= high, "a measured public V6 confidence interval is inverted")
        primitives.finite(row.get("baseline_ns"), "pinned Python V6 observation")
        primitives.finite(row.get("candidate_ns"), "independent engine V6 observation")
        primitives.finite(
            row.get("peak_traced_ratio"), "Python-visible V6 allocation ratio", zero=True
        )
        require(
            type(row.get("statistically_faster")) is bool
            and row["statistically_faster"] == (low > 1.0),
            "a measured public V6 case changed its independently verified "
            "confidence classification",
        )
        require(
            type(row.get("regression_gt_20pct")) is bool
            and row["regression_gt_20pct"] == (speed < REGRESSION_THRESHOLD),
            "a measured public V6 slowdown was omitted or invented",
        )
        require(
            not (row["statistically_faster"] and row["regression_gt_20pct"]),
            "a measured public V6 case cannot be both clearly faster and a slowdown",
        )
        rows_by_candidate[candidate].append(row)
        if row["regression_gt_20pct"]:
            losses_by_candidate[candidate].append(row)

    for candidate, candidate_rows in rows_by_candidate.items():
        require(
            len(candidate_rows) == CASES
            and {row["case"] for row in candidate_rows} == set(frozen),
            f"{LABELS[candidate]} omitted a frozen public V6 case",
        )
        require(
            Counter(row["api"] for row in candidate_rows) == Counter(OPERATIONS)
            and Counter(row["category"] for row in candidate_rows) == Counter(categories),
            f"{LABELS[candidate]} omitted a public V6 workload category",
        )

    expected_losses = [row for row in rows if row["regression_gt_20pct"]]
    loss_count = len(expected_losses)
    losses = summary.get("regressions")
    replayed_losses = integrity.get("regressions")
    require(
        isinstance(losses, list) and losses == expected_losses,
        "an individually measured public V6 slowdown was changed or hidden",
    )
    require(
        isinstance(replayed_losses, list)
        and len(replayed_losses) == loss_count
        and sorted(replayed_losses, key=lambda item: (item["candidate"], item["case"]))
        == sorted(losses, key=lambda item: (item["candidate"], item["case"])),
        "an independently replayed public V6 slowdown was changed or hidden",
    )
    require(
        type(integrity.get("strict_regressions")) is int
        and integrity["strict_regressions"] == loss_count,
        "the V6 slowdown total was copied, guessed, or silently changed",
    )

    rankings = summary.get("rankings")
    require(
        isinstance(rankings, list)
        and len(rankings) == len(CANDIDATES)
        and integrity.get("rankings") == rankings,
        "an independently replayed public V6 candidate ranking is missing",
    )
    seen_candidates: set[str] = set()
    for ranking in rankings:
        require(isinstance(ranking, dict), "a public V6 ranking is invalid")
        candidate = ranking.get("candidate")
        require(
            candidate in CANDIDATES and candidate not in seen_candidates,
            "a current public V6 candidate ranking is missing or duplicated",
        )
        seen_candidates.add(candidate)
        candidate_rows = rows_by_candidate[candidate]
        require(
            ranking.get("cases") == CASES
            and ranking.get("weight") == CASES
            and ranking.get("cohort") == "calibration",
            "a public V6 ranking changed its case denominator or cohort",
        )
        measured = math.exp(
            math.fsum(math.log(row["speedup"]) for row in candidate_rows) / CASES
        )
        primitives.same_float(
            primitives.finite(ranking.get("geomean_speedup"), "overall V6 speed"),
            measured,
            "independently replayed V6 geometric-mean speed",
        )
        low = primitives.finite(ranking.get("ci95_low"), "overall V6 interval lower bound")
        high = primitives.finite(ranking.get("ci95_high"), "overall V6 interval upper bound")
        require(
            low <= ranking["geomean_speedup"] <= high,
            "a public V6 overall confidence interval is invalid",
        )
        require(
            ranking.get("statistically_faster_cases")
            == sum(row["statistically_faster"] for row in candidate_rows),
            "a public V6 ranking concealed a confidence-qualified faster case",
        )
        require(
            ranking.get("regressions_gt_20pct") == len(losses_by_candidate[candidate]),
            "a public V6 ranking concealed an individual genuine slowdown",
        )
    require(
        rankings
        == sorted(rankings, key=lambda ranking: ranking["geomean_speedup"], reverse=True),
        "the displayed public V6 ranking is not its actual measured order",
    )
    require(
        sum(len(values) for values in losses_by_candidate.values()) == loss_count,
        "a measured public V6 loss is omitted from its candidate",
    )
    require_candidate_free()
    return PublicResults(
        manifest=manifest,
        summary=summary,
        integrity=integrity,
        rankings=tuple(rankings),
        rows_by_candidate={key: tuple(value) for key, value in rows_by_candidate.items()},
        losses_by_candidate={key: tuple(value) for key, value in losses_by_candidate.items()},
        operations=dict(OPERATIONS),
        regression_count=loss_count,
    )


def begin_svg(
    suffix: str, *, title: str, description: str, height: int, subtitle: str
) -> list[str]:
    title_id = f"clear-v6-{suffix}-title"
    description_id = f"clear-v6-{suffix}-description"
    return [
        f'<svg xmlns="{SVG_NAMESPACE}" width="1120" height="{height}" '
        f'viewBox="0 0 1120 {height}" role="img" '
        f'aria-labelledby="{title_id} {description_id}">',
        f'<title id="{title_id}">{primitives.esc(title)}</title>',
        f'<desc id="{description_id}">{primitives.esc(description + " " + FOOTER)}</desc>',
        f"<style>{primitives.STYLE}</style>",
        primitives.rect(0, 0, 1120, height, fill="#f5f7fb"),
        primitives.rect(24, 20, 1072, height - 40, fill="#ffffff", radius=20),
        primitives.text(56, 57, "INDEPENDENTLY VERIFIED · CURRENT PUBLIC BENCHMARK", "eyebrow"),
        primitives.text(54, 101, title, "title"),
        primitives.text(56, 126, subtitle, "subtitle"),
    ]


def finish_svg(parts: list[str], *, height: int) -> str:
    parts.extend(
        (
            primitives.line(56, height - 66, 1064, height - 66, stroke="#e6ebf2"),
            primitives.text(56, height - 39, FOOTER, "footer"),
            primitives.text(
                1064,
                height - 39,
                f"{CASES:,} public cases · {TRIALS} paired trials",
                "small",
                text_anchor="end",
            ),
            "</svg>\n",
        )
    )
    return "\n".join(parts)


def confidence_mark(
    parts: list[str], ranking: dict[str, Any], y: float, *, left: float,
    right: float, bounds: tuple[float, float]
) -> None:
    color = COLORS[ranking["candidate"]]
    low = primitives.speed_x(ranking["ci95_low"], left=left, right=right, bounds=bounds)
    high = primitives.speed_x(ranking["ci95_high"], left=left, right=right, bounds=bounds)
    center = primitives.speed_x(
        ranking["geomean_speedup"], left=left, right=right, bounds=bounds
    )
    parts.extend(
        (
            primitives.line(low, y, high, y, stroke=color, width=5, stroke_linecap="round"),
            primitives.line(low, y - 8, low, y + 8, stroke=color, width=2),
            primitives.line(high, y - 8, high, y + 8, stroke=color, width=2),
            f'<circle cx="{center:.2f}" cy="{y:.2f}" r="7" fill="{color}" '
            'stroke="#ffffff" stroke-width="2"/>',
        )
    )


def target_sentences(results: PublicResults) -> tuple[str, str, str, str]:
    speed = [
        LABELS[row["candidate"]]
        for row in results.rankings
        if row["geomean_speedup"] >= SPEED_TARGET
    ]
    cases = [
        LABELS[row["candidate"]]
        for row in results.rankings
        if row["statistically_faster_cases"] >= FASTER_CASE_TARGET
    ]
    both = [
        LABELS[row["candidate"]]
        for row in results.rankings
        if row["geomean_speedup"] >= SPEED_TARGET
        and row["statistically_faster_cases"] >= FASTER_CASE_TARGET
    ]
    speed_text = (
        f"{', '.join(speed)} {'reach' if len(speed) != 1 else 'reaches'} "
        "the 1.5× public speed target."
        if speed
        else "No engine reaches the 1.5× public speed target."
    )
    case_text = (
        f"{', '.join(cases)} {'reach' if len(cases) != 1 else 'reaches'} "
        f"the {FASTER_CASE_TARGET:,}/{CASES:,} clearly-faster target."
        if cases
        else f"No engine reaches the {FASTER_CASE_TARGET:,}/{CASES:,} clearly-faster target."
    )
    both_text = (
        f"{', '.join(both)} {'meet' if len(both) != 1 else 'meets'} "
        "both public speed targets."
        if both
        else "No engine meets both public speed targets."
    )
    return speed_text, case_text, both_text, "This public comparison does not qualify a final winner."


def build_overall(results: PublicResults) -> str:
    height = 650
    parts = begin_svg(
        "overall",
        title="How fast are the current regex engines?",
        description=(
            "Measured overall speed relative to Python, with independently replayed "
            "95 percent confidence intervals for all three current engines."
        ),
        height=height,
        subtitle="Higher is faster. The 1× line is standard Python; bars show measured uncertainty.",
    )
    primitives.pill(parts, 56, 151, 174, "Shared public cases", f"{CASES:,} per engine")
    primitives.pill(parts, 242, 151, 174, "Workload coverage", "12 APIs · 260 groups")
    primitives.pill(parts, 428, 151, 190, "Uncertainty", "95% bootstrap interval")
    values = [
        bound
        for ranking in results.rankings
        for bound in (ranking["ci95_low"], ranking["ci95_high"])
    ]
    bounds = primitives.speed_bounds(values)
    left, right, top, bottom = 255.0, 824.0, 279.0, 486.0
    primitives.speed_axis(parts, left=left, right=right, top=top, bottom=bottom, bounds=bounds)
    for index, ranking in enumerate(results.rankings):
        y = 319 + index * 68
        parts.append(primitives.text(66, y + 5, LABELS[ranking["candidate"]], "label"))
        confidence_mark(parts, ranking, y, left=left, right=right, bounds=bounds)
        parts.append(primitives.text(851, y - 3, f'{ranking["geomean_speedup"]:.3f}×', "value"))
        parts.append(
            primitives.text(
                851,
                y + 17,
                f'{ranking["ci95_low"]:.3f}–{ranking["ci95_high"]:.3f}× · 95% CI',
                "small",
            )
        )
    speed_text, _, _, qualification = target_sentences(results)
    parts.append(primitives.text(58, 553, speed_text, "heading"))
    parts.append(primitives.text(58, 574, qualification, "body"))
    return finish_svg(parts, height=height)


def build_outcomes(results: PublicResults) -> str:
    height = 650
    parts = begin_svg(
        "outcomes",
        title=f"What happened across all {CASES:,} cases?",
        description=(
            "Every current measured candidate case is shown as clearly faster, "
            "more than 20 percent slower, or remaining uncertain."
        ),
        height=height,
        subtitle="Each bar includes every case. Clearly faster means its confidence interval supports the result.",
    )
    green, neutral, amber = "#238b75", "#e4eaf2", "#d59a60"
    for x, color, label in (
        (64, green, "Clearly faster"),
        (225, neutral, "Remaining / uncertain"),
        (445, amber, "More than 20% slower"),
    ):
        parts.append(primitives.rect(x, 167, 12, 12, fill=color, radius=3))
        parts.append(primitives.text(x + 20, 178, label, "body"))
    left, width = 222.0, 666.0
    for index, ranking in enumerate(results.rankings):
        y = 237 + index * 101
        wins = ranking["statistically_faster_cases"]
        losses = ranking["regressions_gt_20pct"]
        remaining = CASES - wins - losses
        require(remaining >= 0, "public V6 outcome categories overlap or omit a case")
        parts.append(primitives.text(65, y + 21, LABELS[ranking["candidate"]], "label"))
        offset = left
        for count, color in ((wins, green), (remaining, neutral), (losses, amber)):
            width_used = width * count / CASES
            if width_used:
                parts.append(primitives.rect(offset, y, width_used, 29, fill=color, radius=3))
            offset += width_used
        parts.append(primitives.text(901, y + 19, f"{CASES:,}/{CASES:,}", "value"))
        parts.append(
            primitives.text(
                left,
                y + 51,
                f"{wins:,} clearly faster · {remaining:,} remaining · "
                f"{losses:,} over 20% slower",
                "small",
            )
        )
    target_x = left + width * 0.60
    parts.append(
        primitives.line(
            target_x, 222, target_x, 473, stroke="#8a72bb", width=1.5,
            stroke_dasharray="5 5",
        )
    )
    parts.append(primitives.text(target_x + 7, 222, "60% clearly-faster target", "small"))
    _, case_text, _, _ = target_sentences(results)
    parts.append(primitives.text(59, 531, case_text, "body"))
    return finish_svg(parts, height=height)


def operation_means(results: PublicResults) -> dict[tuple[str, str], float]:
    means: dict[tuple[str, str], float] = {}
    for candidate, rows in results.rows_by_candidate.items():
        grouped: dict[str, list[float]] = {
            operation: [] for operation in results.operations
        }
        for row in rows:
            grouped[row["api"]].append(row["speedup"])
        for operation, speeds in grouped.items():
            require(
                len(speeds) == results.operations[operation],
                "a displayed public V6 operation omits a measured case",
            )
            means[(candidate, operation)] = math.exp(
                math.fsum(math.log(speed) for speed in speeds) / len(speeds)
            )
    require(
        len(means) == len(CANDIDATES) * len(results.operations),
        "a current public V6 candidate-operation cohort is missing",
    )
    return means


def build_api(results: PublicResults) -> str:
    height = 1_110
    parts = begin_svg(
        "api",
        title="Which Python operations are faster?",
        description=(
            "All 12 frozen Python operations are shown separately for every "
            "current engine using every independently replayed case."
        ),
        height=height,
        subtitle=(
            "Dots show measured per-operation means. Per-operation "
            "confidence intervals were not measured or invented."
        ),
    )
    means = operation_means(results)
    bounds = primitives.speed_bounds(list(means.values()))
    left, right, top, bottom = 281.0, 830.0, 174.0, 1_008.0
    primitives.speed_axis(parts, left=left, right=right, top=top, bottom=bottom, bounds=bounds)
    order = tuple(ranking["candidate"] for ranking in results.rankings)
    for index, (operation, count) in enumerate(results.operations.items()):
        y = 195 + index * 67
        if index:
            parts.append(primitives.line(57, y - 12, 1_059, y - 12, stroke="#edf0f5"))
        parts.append(primitives.text(63, y + 11, operation, "label"))
        parts.append(primitives.text(63, y + 29, f"{count:,} cases per engine", "small"))
        for candidate_index, candidate in enumerate(order):
            position_y = y + candidate_index * 17
            speed = means[(candidate, operation)]
            position_x = primitives.speed_x(speed, left=left, right=right, bounds=bounds)
            parts.append(
                f'<circle cx="{position_x:.2f}" cy="{position_y:.2f}" '
                f'r="4.5" fill="{COLORS[candidate]}">'
                f"<title>{primitives.esc(LABELS[candidate])}: "
                f"{primitives.esc(operation)}, {speed:.6f}×, {count:,} "
                "public cases</title></circle>"
            )
            parts.append(
                primitives.text(
                    849, position_y + 4, f"{LABELS[candidate]} · {speed:.2f}×", "small"
                )
            )
    return finish_svg(parts, height=height)


def build_regressions(results: PublicResults) -> str:
    columns = 112
    step = 6.65
    order = tuple(ranking["candidate"] for ranking in results.rankings)
    bands = {
        candidate: 47
        + math.ceil(len(results.losses_by_candidate[candidate]) / columns) * step
        for candidate in order
    }
    height = max(610, math.ceil(277 + sum(bands.values()) + 89))
    parts = begin_svg(
        "regressions",
        title="Every measured slowdown, shown once",
        description=(
            f"Each of the {results.regression_count:,} independently replayed "
            "current public slowdowns has its own visible and individually titled dot."
        ),
        height=height,
        subtitle=(
            "One dot is one current candidate case more than 20% slower "
            "than Python. Hover a dot for the exact case."
        ),
    )
    primitives.pill(
        parts,
        57,
        150,
        205,
        "Individually visible losses",
        f"{results.regression_count:,} / {CASES * len(CANDIDATES):,}",
    )
    primitives.pill(parts, 275, 150, 205, "Threshold", "more than 20% slower")
    primitives.pill(parts, 493, 150, 205, "Missing or merged cases", "0")
    y = 241.0
    shown = 0
    for candidate in order:
        losses = sorted(
            results.losses_by_candidate[candidate],
            key=lambda row: (row["api"], row["case"]),
        )
        parts.append(primitives.text(62, y + 8, LABELS[candidate], "label"))
        parts.append(primitives.text(62, y + 27, f"{len(losses):,}/{CASES:,} cases", "small"))
        for index, row in enumerate(losses):
            position_x = 296 + (index % columns) * step
            position_y = y + 4 + (index // columns) * step
            description = (
                f'{LABELS[candidate]} · {row["api"]} · {row["case"]} · '
                f'{row["speedup"]:.6f}× Python speed'
            )
            parts.append(
                f'<circle class="loss-mark" cx="{position_x:.2f}" '
                f'cy="{position_y:.2f}" r="2.45" fill="{COLORS[candidate]}">'
                f"<title>{primitives.esc(description)}</title></circle>"
            )
            shown += 1
        y += bands[candidate]
        if candidate != order[-1]:
            parts.append(primitives.line(58, y - 16, 1_056, y - 16, stroke="#edf0f5"))
    require(shown == results.regression_count, "a genuine current V6 slowdown is not visible")
    parts.append(
        primitives.text(
            59,
            height - 92,
            "Every dot is a current measured case; none is sampled, hidden, or copied.",
            "body",
        )
    )
    return finish_svg(parts, height=height)


def build_memory(results: PublicResults) -> str:
    height = 680
    parts = begin_svg(
        "memory",
        title="What memory was actually measured?",
        description=(
            "Python-visible temporary allocations only. Per-case native-engine "
            "allocations and final memory were not measured."
        ),
        height=height,
        subtitle=(
            "Points show median Python-traced allocations; bars span "
            "the measured 10th to 90th percentiles."
        ),
    )
    samples = {
        candidate: tuple(
            sorted(
                primitives.finite(row["peak_traced_ratio"], "V6 traced allocation", zero=True)
                for row in rows
            )
        )
        for candidate, rows in results.rows_by_candidate.items()
    }
    values = {
        candidate: (
            primitives.quantile(sample, 0.1),
            primitives.quantile(sample, 0.5),
            primitives.quantile(sample, 0.9),
        )
        for candidate, sample in samples.items()
    }
    left, right = 271.0, 800.0
    high = max(1.15, max(value[2] for value in values.values()) * 1.10)

    def axis_x(value: float) -> float:
        return left + value / high * (right - left)

    for tick in (0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0):
        if tick <= high:
            position = axis_x(tick)
            parts.append(
                primitives.line(
                    position,
                    203,
                    position,
                    439,
                    stroke="#8d9caf" if tick == 1.0 else "#e9edf3",
                    width=1.5 if tick == 1.0 else 1,
                )
            )
            parts.append(primitives.text(position, 457, f"{tick:g}×", "tick", text_anchor="middle"))
    parts.append(
        primitives.text(
            axis_x(1.0), 194, "Python traced allocation · 1×", "small", text_anchor="middle"
        )
    )
    for index, ranking in enumerate(results.rankings):
        candidate = ranking["candidate"]
        y = 245 + index * 69
        low, median, upper = values[candidate]
        color = COLORS[candidate]
        parts.append(primitives.text(66, y + 4, LABELS[candidate], "label"))
        parts.append(
            primitives.line(
                axis_x(low), y, axis_x(upper), y, stroke=color, width=5,
                stroke_linecap="round",
            )
        )
        parts.append(
            f'<circle cx="{axis_x(median):.2f}" cy="{y:.2f}" r="6.5" '
            f'fill="{color}" stroke="#ffffff" stroke-width="2"/>'
        )
        parts.append(primitives.text(823, y + 3, f"{median:.2f}× median", "value"))
        parts.append(primitives.text(823, y + 20, f"{CASES:,} Python-traced cases", "small"))
    parts.append(primitives.rect(57, 481, 1_003, 82, fill="#f3f6fb", radius=12))
    parts.append(
        primitives.text(
            74, 510, "Native-engine allocations and final memory: NOT MEASURED", "heading"
        )
    )
    parts.append(
        primitives.text(
            74,
            535,
            "Worker memory totals cannot identify per-case native allocations.",
            "body",
        )
    )
    return finish_svg(parts, height=height)


def build_rankings(results: PublicResults) -> str:
    height = 670
    parts = begin_svg(
        "rankings",
        title="How the current engines compare",
        description=(
            "The actual independently replayed public ranking shows every current "
            "engine, measured confidence interval, faster case, and slowdown."
        ),
        height=height,
        subtitle="Ranked only by this measured public comparison; the final test is unopened.",
    )
    bounds = primitives.speed_bounds(
        [
            value
            for ranking in results.rankings
            for value in (ranking["ci95_low"], ranking["ci95_high"])
        ]
    )
    left, right, top, bottom = 314.0, 788.0, 213.0, 456.0
    primitives.speed_axis(parts, left=left, right=right, top=top, bottom=bottom, bounds=bounds)
    for index, ranking in enumerate(results.rankings):
        y = 254 + index * 78
        candidate = ranking["candidate"]
        parts.append(primitives.text(64, y + 5, f"{index + 1:02d}", "small"))
        parts.append(primitives.text(105, y + 4, LABELS[candidate], "label"))
        parts.append(
            primitives.text(
                105,
                y + 22,
                f'{ranking["statistically_faster_cases"]:,}/{CASES:,} clearly faster',
                "small",
            )
        )
        confidence_mark(parts, ranking, y, left=left, right=right, bounds=bounds)
        parts.append(primitives.text(813, y - 2, f'{ranking["geomean_speedup"]:.3f}×', "value"))
        parts.append(
            primitives.text(
                813, y + 17,
                f'{ranking["ci95_low"]:.3f}–{ranking["ci95_high"]:.3f}×',
                "small",
            )
        )
        parts.append(
            primitives.text(955, y + 4, f'{ranking["regressions_gt_20pct"]:,} losses', "small")
        )
    _, _, both, qualification = target_sentences(results)
    parts.append(primitives.rect(58, 501, 1_001, 66, fill="#f4f6fb", radius=12))
    parts.append(primitives.text(75, 528, both, "heading"))
    parts.append(primitives.text(75, 550, qualification, "body"))
    return finish_svg(parts, height=height)


BUILDERS: dict[str, Callable[[PublicResults], str]] = {
    "overall": build_overall,
    "outcomes": build_outcomes,
    "api": build_api,
    "regressions": build_regressions,
    "memory": build_memory,
    "rankings": build_rankings,
}


def validate_svg(svg: str, *, suffix: str, results: PublicResults) -> None:
    require(
        isinstance(svg, str) and svg.endswith("</svg>\n"),
        "a clear current public V6 graph is not complete SVG",
    )
    root = ElementTree.fromstring(svg)
    namespace = f"{{{SVG_NAMESPACE}}}"
    require(root.tag == f"{namespace}svg", "a current public V6 graph has no SVG namespace")
    require(root.get("role") == "img", "a current public V6 graph has no accessible image role")
    require(
        root.get("aria-labelledby")
        == f"clear-v6-{suffix}-title clear-v6-{suffix}-description",
        "a current public V6 graph retained an old or nonunique accessibility identity",
    )
    title = root.find(f"{namespace}title")
    description = root.find(f"{namespace}desc")
    require(title is not None and bool(title.text), "a public V6 graph has no accessible title")
    require(
        description is not None and FOOTER in (description.text or ""),
        "a current public V6 graph misstated final-test status",
    )
    visible = " ".join(node.text or "" for node in root.iter(f"{namespace}text"))
    require(FOOTER in visible, "a public V6 graph concealed its final-test limitation")
    require("clear-v5-" not in svg, "a current public V6 graph copied a V5 identity")
    if suffix in ("overall", "api", "rankings"):
        require(
            "Python · 1×" in visible and "1.5× target" in visible,
            "a current public V6 speed graph omitted Python or its honest speed target",
        )
    if suffix == "overall":
        require(
            target_sentences(results)[0] in visible,
            "the current V6 overall graph misrepresented its measured speed target",
        )
    if suffix == "outcomes":
        require(
            "60% clearly-faster target" in visible
            and target_sentences(results)[1] in visible,
            "the current V6 outcomes graph misrepresented its measured case target",
        )
    if suffix == "rankings":
        require(
            target_sentences(results)[2] in visible,
            "the current public V6 ranking misrepresented its actual target outcomes",
        )
    if suffix == "regressions":
        marks = [
            node
            for node in root.iter(f"{namespace}circle")
            if node.get("class") == "loss-mark"
        ]
        require(
            len(marks) == results.regression_count,
            "a measured current V6 slowdown is not individually visible",
        )
        require(
            all(node.find(f"{namespace}title") is not None for node in marks),
            "an individual current public V6 slowdown has no accessible case description",
        )
        require(
            f"{results.regression_count:,} / {CASES * len(CANDIDATES):,}" in visible,
            "a current V6 slowdown graph changed its real denominator",
        )
    if suffix == "memory":
        require(
            "Native-engine allocations and final memory: NOT MEASURED" in visible,
            "a current V6 memory graph overclaims unmeasured native allocations",
        )


def build_charts(results: PublicResults) -> dict[str, str]:
    require_candidate_free()
    require(tuple(BUILDERS) == SUFFIXES, "a required current V6 clear graph was removed")
    charts = {suffix: BUILDERS[suffix](results) for suffix in SUFFIXES}
    for suffix, svg in charts.items():
        validate_svg(svg, suffix=suffix, results=results)
    require_candidate_free()
    return charts


def plan_clear_outputs(
    charts: dict[str, str], states: dict[str, tuple[str, bytes | None]]
) -> dict[str, bool]:
    require(
        tuple(charts) == SUFFIXES and tuple(states) == SUFFIXES,
        "a required exact public V6 clear output is missing or substituted",
    )
    create: dict[str, bool] = {}
    for suffix in SUFFIXES:
        state = states[suffix]
        require(
            isinstance(state, tuple) and len(state) == 2,
            "an exact current V6 presentation destination has an invalid state",
        )
        kind, existing = state
        if kind == "missing":
            require(existing is None, "a missing public V6 graph unexpectedly has bytes")
            create[suffix] = True
            continue
        require(kind == "regular", "a public V6 graph is a symbolic link or nonregular file")
        require(
            isinstance(existing, bytes) and existing == charts[suffix].encode("utf-8"),
            "an existing current V6 graph does not reproduce the same measured evidence",
        )
        create[suffix] = False
    return create


def require_render_inputs(
    *,
    summary: Path,
    summary_sha256: str,
    integrity: Path,
    integrity_sha256: str,
    manifest: Path,
    manifest_sha256: str,
    runner_sha256: str,
    output_dir: Path,
) -> None:
    for label, supplied, expected in (
        ("measured summary", summary, SUMMARY),
        ("independent replay", integrity, INTEGRITY),
        ("frozen manifest", manifest, MANIFEST),
        ("clear output directory", output_dir, EVIDENCE),
    ):
        require(
            isinstance(supplied, Path) and supplied.resolve() == expected.resolve(),
            f"the public V6 {label} escaped its exact versioned destination",
        )
    for label, digest in (
        ("measured summary", summary_sha256),
        ("independent replay", integrity_sha256),
        ("frozen manifest", manifest_sha256),
        ("frozen runner", runner_sha256),
    ):
        require(valid_sha256(digest), f"an externally supplied V6 {label} SHA-256 is required")


def synthetic_documents() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    """Construct a complete 8,192-case V6 fixture exclusively in memory."""

    selection: list[dict[str, Any]] = []
    for operation, count in OPERATIONS.items():
        for index in range(count):
            global_index = len(selection)
            selection.append(
                {
                    "case": f"cal.synthetic.v6.{operation}.{index:05d}",
                    "api": operation,
                    "category": f"synthetic-v6-category-{global_index % CATEGORIES:03d}",
                    "cohort": "calibration",
                    "expected_result_sha256": synthetic_sha(f"expected:{global_index}"),
                    "frozen_operations": 1,
                }
            )
    categories = dict(Counter(entry["category"] for entry in selection))
    scenarios = {
        "candidates.rust_candidate": (197, 5_112, 2.20),
        "candidates.vm_candidate": (283, 4_200, 1.36),
        "candidates.zig_candidate": (389, 5_030, 1.52),
    }
    rows: list[dict[str, Any]] = []
    rankings: list[dict[str, Any]] = []
    for candidate_index, candidate in enumerate(CANDIDATES):
        loss_count, wins, winning_speed = scenarios[candidate]
        require(loss_count + wins <= CASES, "an in-memory V6 case scenario overlaps")
        candidate_rows: list[dict[str, Any]] = []
        for index, entry in enumerate(selection):
            loss = index < loss_count
            faster = loss_count <= index < loss_count + wins
            speed = 0.71 if loss else winning_speed if faster else 1.02
            low = speed * (0.98 if faster else 0.91)
            high = speed * (1.02 if faster else 1.09)
            row = {
                **entry,
                "candidate": candidate,
                "weight": 1,
                "baseline_ns": 100.0,
                "candidate_ns": 100.0 / speed,
                "speedup": speed,
                "ci95_low": low,
                "ci95_high": high,
                "peak_traced_ratio": (index % 29) / 20 + candidate_index * 0.03,
                "statistically_faster": faster,
                "regression_gt_20pct": loss,
            }
            candidate_rows.append(row)
        rows.extend(candidate_rows)
        speed = math.exp(
            math.fsum(math.log(row["speedup"]) for row in candidate_rows) / CASES
        )
        rankings.append(
            {
                "candidate": candidate,
                "cases": CASES,
                "weight": CASES,
                "cohort": "calibration",
                "geomean_speedup": speed,
                "ci95_low": speed * 0.985,
                "ci95_high": speed * 1.015,
                "statistically_faster_cases": wins,
                "regressions_gt_20pct": loss_count,
            }
        )
    rankings.sort(key=lambda ranking: ranking["geomean_speedup"], reverse=True)
    losses = [row for row in rows if row["regression_gt_20pct"]]
    artifacts = [
        {"role": role, "path": path, "sha256": digest}
        for role, (path, digest) in EXPECTED_PROOFS.items()
    ]
    edges = [
        {
            "module": module,
            "path": str((ROOT / EXPECTED_PROOFS[f"{family}-edge"][0]).resolve()),
            "report_sha256": synthetic_sha(f"edge:{family}"),
        }
        for module, family in zip(CANDIDATES, ("rust", "vm", "zig"), strict=True)
    ]
    runner_sha256 = synthetic_sha("frozen-public-v6-runner")
    common: dict[str, Any] = {
        "protocol_version": VERSION,
        "cohort": "calibration",
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "runner_sha256": runner_sha256,
        "failed": 0,
        "strict_regression_speedup_threshold": REGRESSION_THRESHOLD,
        "from_scratch_audit_sha256": BASE_AUDIT_SHA256,
        "from_scratch_audit_source_path": str(BASE_AUDIT_SOURCE_PATH.resolve()),
        "from_scratch_audit_source_sha256": BASE_AUDIT_SOURCE_SHA256,
        "postfinal_no_delegation_audit_path": str(STRICT_AUDIT_PATH.resolve()),
        "postfinal_no_delegation_audit_sha256": STRICT_AUDIT_SHA256,
        "postfinal_no_delegation_audit_source_path": str(STRICT_AUDIT_SOURCE_PATH.resolve()),
        "postfinal_no_delegation_audit_source_sha256": STRICT_AUDIT_SOURCE_SHA256,
        "postfinal_no_delegation_audit_schema": STRICT_AUDIT_SCHEMA,
        "postfinal_no_delegation_control_count": 32,
        "postfinal_guarded_worker_source_path": str(GUARDED_WORKER_SOURCE.resolve()),
        "postfinal_guarded_worker_source_sha256": GUARDED_WORKER_SOURCE_SHA256,
        "postfinal_guarded_worker_schema": GUARDED_WORKER_SCHEMA,
        "postfinal_guarded_worker_report_path": str(GUARDED_WORKER_REPORT.resolve()),
        "postfinal_guarded_worker_report_sha256": GUARDED_WORKER_REPORT_SHA256,
        "stage05_correctness_artifacts": artifacts,
        "verified_edge_oracles": edges,
        "python_re_universal_oracle_source_path": str(UNIVERSAL_SOURCE.resolve()),
        "python_re_universal_oracle_source_sha256": UNIVERSAL_SOURCE_SHA256,
        "python_re_universal_oracle_report_path": str(UNIVERSAL_REPORT.resolve()),
        "python_re_universal_oracle_report_sha256": UNIVERSAL_REPORT_SHA256,
        "python_re_universal_oracle_schema": "rebar-python-re-universal-public-oracle-v1",
        "python_re_universal_oracle_status": "PASS",
        "python_re_universal_oracle_selected": "all",
        "python_re_universal_oracle_candidates": ["rust", "vm", "zig"],
        "python_re_universal_oracle_cases": CASES,
        "python_re_universal_oracle_comparisons_per_case": 48,
        "python_re_universal_oracle_comparisons_per_candidate": CASES * 48,
        "python_re_universal_oracle_total_comparisons": CASES * 48 * len(CANDIDATES),
        "python_re_universal_oracle_mismatches": 0,
        "python_re_universal_oracle_seed": 2026072417,
        "python_re_universal_oracle_seed_domain": "rebar/python-re/universal-public/v1",
        "python_re_universal_oracle_case_sha256": UNIVERSAL_CASE_SHA256,
        "python_re_universal_oracle_grammar_family_count": 16,
        "python_re_universal_oracle_input_stratum_count": 16,
        "python_re_universal_oracle_examples_per_stratum": 32,
        "python_re_universal_oracle_original_audit_sha256": BASE_AUDIT_SHA256,
        "python_re_universal_oracle_postfinal_no_delegation_audit_sha256": STRICT_AUDIT_SHA256,
        "python_re_universal_oracle_frozen_source_path": str(FROZEN_ORACLE_SOURCE.resolve()),
        "python_re_universal_oracle_frozen_source_sha256": FROZEN_ORACLE_SOURCE_SHA256,
    }
    manifest = {
        **common,
        "schema": PLAN_SCHEMA,
        "postfinal_schema": PLAN_POSTFINAL_SCHEMA,
        "python": "3.14.6",
        "exclusive_slot": VERSION,
        "modules": list(MODULES),
        "cases": CASES,
        "all_bounded_workload_categories": CATEGORIES,
        "public_operations": dict(OPERATIONS),
        "categories": categories,
        "selected_cases": selection,
        "selection_seed": 2026072404,
        "order_seed": 2026072405,
        "bootstrap_seed": 2026072406,
        "frozen_trials": TRIALS,
        "frozen_warmups": WARMUPS,
        "frozen_bootstrap_samples": BOOTSTRAPS,
        "from_scratch_audit_path": str(BASE_AUDIT_PATH.resolve()),
        "native_elf_fingerprints": dict(EXPECTED_NATIVE),
        "qualified_source_fingerprints": dict(EXPECTED_SOURCES),
        "source_public_v5_runner_path": "tools/postfinal_public_practice_v5.py",
        "source_public_v5_runner_sha256": (
            "f4294a3b5434f43a92970635a958cf3b39db0eb926adef50e242ac0f6b9a1d22"
        ),
        "source_public_v5_manifest_path": "performance/postfinal-public-v5/manifest.json",
        "source_public_v5_manifest_sha256": (
            "c9950c87079ccc1909ba4470ed573b08afe1f275b85a8932cbfe83b547b24f96"
        ),
        "public_v5_case_population_preserved": True,
        "public_v5_case_population_count": CASES,
        "public_v5_workload_category_count": CATEGORIES,
        "private_worker_wire_format": "synthetic-in-memory-ascii-safe-json",
        "private_worker_wire_ensure_ascii": True,
    }
    manifest_sha256 = canonical_sha256(manifest)
    binaries = {f"synthetic-role-{index}": synthetic_sha(f"binary:{index}") for index in range(11)}
    summary = {
        **common,
        "schema": SUMMARY_SCHEMA,
        "postfinal_schema": SUMMARY_POSTFINAL_SCHEMA,
        "exclusive_slot": VERSION,
        "modules": list(MODULES),
        "cases": CASES,
        "all_bounded_workload_categories": CATEGORIES,
        "public_operations": dict(OPERATIONS),
        "selection_seed": 2026072404,
        "order_seed": 2026072405,
        "bootstrap_seed": 2026072406,
        "trials": TRIALS,
        "warmups": WARMUPS,
        "bootstrap_samples": BOOTSTRAPS,
        "manifest_path": str(MANIFEST.resolve()),
        "manifest_sha256": manifest_sha256,
        "raw_path": str(RAW.resolve()),
        "raw_sha256": synthetic_sha("uncompressed-v6-raw"),
        "compressed_raw_sha256": synthetic_sha("compressed-v6-raw"),
        "paired_raw_rows": RAW_ROWS,
        "correctness_checks": CORRECTNESS_CHECKS,
        "persistent_isolated_worker_count": len(MODULES),
        "per_case_runtime_guard_checks": RUNTIME_GUARDS,
        "controller_candidate_imported": False,
        "candidate_binary_sha256_before": binaries,
        "candidate_binary_sha256_after": binaries,
        "case_results": rows,
        "regressions": losses,
        "rankings": rankings,
    }
    summary_sha256 = canonical_sha256(summary)
    integrity = {
        **common,
        "schema": INTEGRITY_SCHEMA,
        "result": "PASS",
        "module_order": list(MODULES),
        "cases_per_candidate": CASES,
        "candidate_case_count": CASES * len(CANDIDATES),
        "trials_per_module_case": TRIALS,
        "bootstrap_draws": BOOTSTRAPS,
        "raw_rows": RAW_ROWS,
        "correctness_checks": CORRECTNESS_CHECKS,
        "confidence_intervals_recomputed": CONFIDENCE_INTERVALS,
        "strict_regressions": len(losses),
        "manifest_sha256": manifest_sha256,
        "summary_sha256": summary_sha256,
        "raw_sha256": summary["raw_sha256"],
        "compressed_raw_sha256": summary["compressed_raw_sha256"],
        "persistent_isolated_worker_count": len(MODULES),
        "per_case_runtime_guard_checks": RUNTIME_GUARDS,
        "controller_candidate_imported": False,
        "candidate_imported": False,
        "timing_performed": False,
        "memory_limitation": MEMORY_LIMITATION,
        "from_scratch_control_count": 76,
        "verified_independent_engine_count": len(CANDIDATES),
        "verified_native_library_count": len(EXPECTED_NATIVE),
        "native_elf_fingerprints": dict(EXPECTED_NATIVE),
        "qualified_source_fingerprints": dict(EXPECTED_SOURCES),
        "candidate_binary_sha256_before": binaries,
        "candidate_binary_sha256_after": binaries,
        "rankings": rankings,
        "regressions": losses,
        "self_test": {
            "result": "PASS",
            "postfinal_v6_poisoned_control_count": 43,
            "private_worker_wire_control_count": 7,
            "mixed_correctness_artifact_count": 12,
            "fresh_rust_correctness_artifact_count": 4,
            "preserved_peer_correctness_artifact_count": 8,
            "worker_processes_started": 0,
            "benchmark_or_timing_executed": False,
        },
    }
    pins = {
        "manifest_sha256": manifest_sha256,
        "summary_sha256": summary_sha256,
        "integrity_sha256": canonical_sha256(integrity),
        "runner_sha256": runner_sha256,
    }
    return manifest, summary, integrity, pins


def reject_synthetic(name: str, action: Callable[[], Any]) -> None:
    try:
        action()
    except (KeyError, TypeError, ValueError, ElementTree.ParseError):
        return
    raise ValueError(f"a candidate-free public V6 presentation control accepted {name}")


def self_test() -> dict[str, Any]:
    """Exercise the complete presenter without any results, candidates, or timing."""

    require_candidate_free()
    verify_visual_primitives()
    manifest, summary, integrity, pins = synthetic_documents()
    results = validate_documents(manifest, summary, integrity, **pins)
    charts = build_charts(results)
    require(charts == build_charts(results), "current public V6 SVG generation is not deterministic")
    require(results.regression_count == 197 + 283 + 389, "synthetic losses are not independently derived")
    require(
        any(row["geomean_speedup"] >= SPEED_TARGET for row in results.rankings)
        and any(row["statistically_faster_cases"] >= FASTER_CASE_TARGET for row in results.rankings),
        "the synthetic V6 presenter did not exercise actual target achievement",
    )

    def validate(
        new_manifest: dict[str, Any] | None = None,
        new_summary: dict[str, Any] | None = None,
        new_integrity: dict[str, Any] | None = None,
        **new_pins: str,
    ) -> PublicResults:
        return validate_documents(
            manifest if new_manifest is None else new_manifest,
            summary if new_summary is None else new_summary,
            integrity if new_integrity is None else new_integrity,
            **{**pins, **new_pins},
        )

    def changed_row(**updates: Any) -> dict[str, Any]:
        changed = list(summary["case_results"])
        changed[0] = {**changed[0], **updates}
        return {**summary, "case_results": changed}

    controls: tuple[tuple[str, Callable[[], Any]], ...] = (
        ("substituted frozen-manifest pin", lambda: validate(manifest_sha256="0" * 64)),
        ("substituted measured-summary pin", lambda: validate(summary_sha256="0" * 64)),
        ("substituted independently replayed-summary pin", lambda: validate(integrity_sha256="")),
        ("substituted frozen-runner pin", lambda: validate(runner_sha256="0" * 64)),
        ("stale archived V5 protocol", lambda: validate({**manifest, "protocol_version": "postfinal-public-practice-v5"})),
        ("stale archived V5 plan schema", lambda: validate({**manifest, "postfinal_schema": "rebar-postfinal-public-practice-plan-v5"})),
        ("stale archived V5 summary schema", lambda: validate(new_summary={**summary, "postfinal_schema": "rebar-postfinal-public-practice-report-v5"})),
        ("stale archived V5 replay schema", lambda: validate(new_integrity={**integrity, "schema": "rebar-postfinal-public-practice-integrity-v5"})),
        ("public manifest accesses final holdout", lambda: validate({**manifest, "holdout_accessed": True})),
        ("public summary generates final cases", lambda: validate(new_summary={**summary, "held_out_cases_generated": 1})),
        ("public replay deserializes final records", lambda: validate(new_integrity={**integrity, "held_out_records_deserialized": 1})),
        ("substituted V2 source audit", lambda: validate({**manifest, "from_scratch_audit_sha256": "0" * 64})),
        ("substituted V2 source-audit path", lambda: validate({**manifest, "from_scratch_audit_path": str(ROOT / "candidates/audits/FROM-SCRATCH-AUDIT.json")})),
        ("substituted V2 isolation audit", lambda: validate({**manifest, "postfinal_no_delegation_audit_sha256": "0" * 64})),
        ("stale V1 isolation audit schema", lambda: validate({**manifest, "postfinal_no_delegation_audit_schema": GUARDED_WORKER_SCHEMA})),
        ("omitted V2 isolation control", lambda: validate(new_integrity={**integrity, "postfinal_no_delegation_control_count": 31})),
        ("substituted isolated worker source", lambda: validate({**manifest, "postfinal_guarded_worker_source_sha256": "0" * 64})),
        ("substituted isolated worker report", lambda: validate(new_summary={**summary, "postfinal_guarded_worker_report_sha256": "0" * 64})),
        ("stale all-engine oracle source", lambda: validate({**manifest, "python_re_universal_oracle_source_path": str(ROOT / "tools/python_re_universal_public_oracle_stage03.py")})),
        ("stale all-engine oracle report", lambda: validate({**manifest, "python_re_universal_oracle_report_sha256": "0" * 64})),
        ("nonzero all-engine oracle mismatch", lambda: validate(new_summary={**summary, "python_re_universal_oracle_mismatches": 1})),
        ("omitted all-engine oracle comparison", lambda: validate(new_integrity={**integrity, "python_re_universal_oracle_total_comparisons": CASES * 48 * len(CANDIDATES) - 1})),
        ("missing fresh Rust proof", lambda: validate({**manifest, "stage05_correctness_artifacts": manifest["stage05_correctness_artifacts"][1:]})),
        ("substituted old Rust proof", lambda: validate({**manifest, "stage05_correctness_artifacts": [{**manifest["stage05_correctness_artifacts"][0], "path": "candidates/evidence/rust-v7-edge-oracle-rust-post-final-stage-05-universal-parity.json.gz"}, *manifest["stage05_correctness_artifacts"][1:]]})),
        ("shared candidate correctness proof", lambda: validate({**manifest, "stage05_correctness_artifacts": [manifest["stage05_correctness_artifacts"][0], manifest["stage05_correctness_artifacts"][0], *manifest["stage05_correctness_artifacts"][2:]]})),
        ("omitted native engine", lambda: validate({**manifest, "native_elf_fingerprints": {key: value for index, (key, value) in enumerate(EXPECTED_NATIVE.items()) if index}})),
        ("restored historical Rust engine", lambda: validate({**manifest, "native_elf_fingerprints": {**EXPECTED_NATIVE, "candidates.rust_candidate:native-engine": "c6c09ae96e3a840dc7a62870b3f8c54f6ebc4d82537b319f77520175e84a3255"}})),
        ("substituted current Rust source", lambda: validate(new_integrity={**integrity, "qualified_source_fingerprints": {**EXPECTED_SOURCES, "candidates/rust/src/lib.rs": "0" * 64}})),
        ("omitted independently owned engine", lambda: validate(new_summary={**summary, "modules": list(MODULES[:-1])})),
        ("changed Python baseline", lambda: validate({**manifest, "python": "3.14.5"})),
        ("changed current case denominator", lambda: validate(new_summary={**summary, "cases": CASES - 1})),
        ("omitted frozen workload category", lambda: validate({**manifest, "all_bounded_workload_categories": CATEGORIES - 1})),
        ("changed frozen operation weight", lambda: validate({**manifest, "public_operations": {**OPERATIONS, "split": OPERATIONS["split"] - 1}})),
        ("changed case-selection seed", lambda: validate({**manifest, "selection_seed": 0})),
        ("changed bootstrap seed", lambda: validate(new_summary={**summary, "bootstrap_seed": 0})),
        ("changed paired-trial count", lambda: validate(new_summary={**summary, "trials": TRIALS - 1})),
        ("changed bootstrap-draw count", lambda: validate(new_integrity={**integrity, "bootstrap_draws": BOOTSTRAPS - 1})),
        ("broken archived-population provenance", lambda: validate({**manifest, "public_v5_case_population_preserved": False})),
        ("disabled Unicode-safe wire", lambda: validate({**manifest, "private_worker_wire_ensure_ascii": False})),
        ("substituted measured raw fingerprint", lambda: validate(new_integrity={**integrity, "compressed_raw_sha256": "0" * 64})),
        ("omitted timing observation", lambda: validate(new_summary={**summary, "paired_raw_rows": RAW_ROWS - 1})),
        ("omitted correctness answer gate", lambda: validate(new_integrity={**integrity, "correctness_checks": CORRECTNESS_CHECKS - 1})),
        ("omitted confidence interval", lambda: validate(new_integrity={**integrity, "confidence_intervals_recomputed": CONFIDENCE_INTERVALS - 1})),
        ("missing guarded worker", lambda: validate(new_summary={**summary, "persistent_isolated_worker_count": len(MODULES) - 1})),
        ("missing native-isolation guard", lambda: validate(new_integrity={**integrity, "per_case_runtime_guard_checks": RUNTIME_GUARDS - 1})),
        ("replay imports candidate", lambda: validate(new_integrity={**integrity, "candidate_imported": True})),
        ("replay performs new timing", lambda: validate(new_integrity={**integrity, "timing_performed": True})),
        ("unverified independent replay", lambda: validate(new_integrity={**integrity, "result": "FAIL"})),
        ("weakened replay safety control", lambda: validate(new_integrity={**integrity, "self_test": {**integrity["self_test"], "postfinal_v6_poisoned_control_count": 42}})),
        ("overclaimed native memory", lambda: validate(new_integrity={**integrity, "memory_limitation": "all native memory measured"})),
        ("omitted frozen public case", lambda: validate({**manifest, "selected_cases": manifest["selected_cases"][:-1]})),
        ("omitted measured candidate case", lambda: validate(new_summary={**summary, "case_results": summary["case_results"][:-1]})),
        ("changed candidate case weight", lambda: validate(new_summary=changed_row(weight=2))),
        ("nonfinite candidate speed", lambda: validate(new_summary=changed_row(speedup=float("nan")))),
        ("inverted confidence interval", lambda: validate(new_summary=changed_row(ci95_low=10.0))),
        ("false confidence-qualified faster flag", lambda: validate(new_summary=changed_row(statistically_faster=True))),
        ("confidence interval crosses the faster boundary", lambda: validate(new_summary=changed_row(ci95_low=1.01, ci95_high=1.02))),
        ("concealed individual slowdown", lambda: validate(new_summary={**summary, "regressions": summary["regressions"][1:]})),
        ("concealed replayed slowdown", lambda: validate(new_integrity={**integrity, "regressions": integrity["regressions"][1:]})),
        ("changed measured V6 slowdown count", lambda: validate(new_integrity={**integrity, "strict_regressions": results.regression_count + 1})),
        ("changed measured ranking order", lambda: validate(new_summary={**summary, "rankings": list(reversed(summary["rankings"]))})),
        ("concealed confidence-qualified faster case", lambda: validate(new_summary={**summary, "rankings": [{**summary["rankings"][0], "statistically_faster_cases": summary["rankings"][0]["statistically_faster_cases"] - 1}, *summary["rankings"][1:]]})),
        ("wrong current SVG accessibility identity", lambda: validate_svg(charts["overall"].replace("clear-v6-overall-title", "clear-v5-overall-title"), suffix="overall", results=results)),
        ("omitted measured slowdown SVG dot", lambda: validate_svg(charts["regressions"].replace('class="loss-mark"', 'class="hidden-loss"', 1), suffix="regressions", results=results)),
        ("false overall target sentence", lambda: validate_svg(charts["overall"].replace(target_sentences(results)[0], "No engine reaches the 1.5× public speed target."), suffix="overall", results=results)),
        ("false faster-case target sentence", lambda: validate_svg(charts["outcomes"].replace(target_sentences(results)[1], "No engine reaches the 4,916/8,192 clearly-faster target."), suffix="outcomes", results=results)),
        ("concealed native-memory limitation", lambda: validate_svg(charts["memory"].replace("Native-engine allocations and final memory: NOT MEASURED", "All native memory was measured"), suffix="memory", results=results)),
        ("concealed unopened final test", lambda: validate_svg(charts["rankings"].replace(FOOTER, "A final winner was proven."), suffix="rankings", results=results)),
    )
    for name, action in controls:
        reject_synthetic(name, action)

    missing = {suffix: ("missing", None) for suffix in SUFFIXES}
    existing = {
        suffix: ("regular", charts[suffix].encode("utf-8")) for suffix in SUFFIXES
    }
    require(all(plan_clear_outputs(charts, missing).values()), "missing V6 outputs are not exclusive")
    require(
        not any(plan_clear_outputs(charts, existing).values()),
        "existing current V6 graphs are not safely reproducible",
    )
    mixed = {**existing, "overall": ("missing", None)}
    require(
        plan_clear_outputs(charts, mixed)
        == {suffix: suffix == "overall" for suffix in SUFFIXES},
        "a single missing current V6 graph cannot be independently reproduced",
    )
    output_controls: tuple[tuple[str, Callable[[], Any]], ...] = (
        ("substituted existing graph", lambda: plan_clear_outputs(charts, {**existing, "overall": ("regular", b"substituted")})),
        ("symbolic-link graph destination", lambda: plan_clear_outputs(charts, {**existing, "overall": ("symlink", None)})),
        ("nonregular graph destination", lambda: plan_clear_outputs(charts, {**existing, "overall": ("nonregular", None)})),
        ("omitted required graph output", lambda: plan_clear_outputs(charts, {suffix: existing[suffix] for suffix in SUFFIXES[:-1]})),
        ("additional unowned graph output", lambda: plan_clear_outputs(charts, {**existing, "foreign": ("missing", None)})),
        ("unexpected missing-output bytes", lambda: plan_clear_outputs(charts, {**existing, "overall": ("missing", b"unexpected")})),
        ("non-byte existing graph", lambda: plan_clear_outputs(charts, {**existing, "overall": ("regular", None)})),
        ("changed deterministic graph source", lambda: plan_clear_outputs({**charts, "overall": charts["overall"] + "changed"}, existing)),
    )
    for name, action in output_controls:
        reject_synthetic(name, action)

    real_inputs = {
        "summary": SUMMARY,
        "summary_sha256": pins["summary_sha256"],
        "integrity": INTEGRITY,
        "integrity_sha256": pins["integrity_sha256"],
        "manifest": MANIFEST,
        "manifest_sha256": pins["manifest_sha256"],
        "runner_sha256": pins["runner_sha256"],
        "output_dir": EVIDENCE,
    }
    require_render_inputs(**real_inputs)
    input_controls: tuple[tuple[str, Callable[[], Any]], ...] = (
        ("historical V5 summary destination", lambda: require_render_inputs(**{**real_inputs, "summary": ROOT / "performance/postfinal-public-v5/evidence/postfinal-public-practice-v5-summary.json"})),
        ("historical V5 replay destination", lambda: require_render_inputs(**{**real_inputs, "integrity": ROOT / "performance/postfinal-public-v5/evidence/postfinal-public-practice-v5-integrity.json"})),
        ("historical V5 manifest destination", lambda: require_render_inputs(**{**real_inputs, "manifest": ROOT / "performance/postfinal-public-v5/manifest.json"})),
        ("historical V5 graph directory", lambda: require_render_inputs(**{**real_inputs, "output_dir": ROOT / "performance/postfinal-public-v5/evidence"})),
        ("missing external summary fingerprint", lambda: require_render_inputs(**{**real_inputs, "summary_sha256": ""})),
        ("missing external replay fingerprint", lambda: require_render_inputs(**{**real_inputs, "integrity_sha256": ""})),
        ("missing external manifest fingerprint", lambda: require_render_inputs(**{**real_inputs, "manifest_sha256": ""})),
        ("missing external frozen-runner fingerprint", lambda: require_render_inputs(**{**real_inputs, "runner_sha256": ""})),
    )
    for name, action in input_controls:
        reject_synthetic(name, action)
    require_candidate_free()
    return {
        "result": "PASS",
        "schema": "rebar-postfinal-public-practice-presentation-self-test-v2",
        "protocol_version": VERSION,
        "presentation_version": PRESENTATION_VERSION,
        "mode": (
            "candidate-free in-memory synthetic controls; only exact "
            "SHA-pinned V1 visual primitives are read; no results, "
            "candidate, subprocess, timing, or holdout access"
        ),
        "primitive_source_path": str(PRIMITIVE_SOURCE.resolve()),
        "primitive_source_sha256": PRIMITIVE_SOURCE_SHA256,
        "cases_per_candidate": CASES,
        "workload_categories": CATEGORIES,
        "operations": len(OPERATIONS),
        "paired_observations": RAW_ROWS,
        "correctness_checks": CORRECTNESS_CHECKS,
        "confidence_intervals": CONFIDENCE_INTERVALS,
        "current_synthetic_regressions": results.regression_count,
        "current_proof_artifacts": len(EXPECTED_PROOFS),
        "fresh_rust_proofs": 4,
        "preserved_peer_proofs": 8,
        "source_controls": 76,
        "isolation_controls": 32,
        "charts": len(charts),
        "deterministic": True,
        "candidate_free": True,
        "worker_processes_started": 0,
        "benchmark_or_timing_executed": False,
        "holdout_accessed": False,
        "results_read": False,
        "exclusive_missing_output_creation": True,
        "reproducible_existing_outputs": True,
        "document_poison_controls": len(controls),
        "output_poison_controls": len(output_controls),
        "input_poison_controls": len(input_controls),
        "poison_controls": len(controls) + len(output_controls) + len(input_controls),
        "final_holdout": "NOT OPENED",
        "native_final_memory": "NOT MEASURED",
    }


def verify_real_provenance() -> None:
    """Authenticate only explicit owned public source, proof, and ELF paths."""

    require_candidate_free()
    base_audit = read_verified_json(
        BASE_AUDIT_PATH, expected=BASE_AUDIT_PATH, digest=BASE_AUDIT_SHA256
    )
    strict_audit = read_verified_json(
        STRICT_AUDIT_PATH, expected=STRICT_AUDIT_PATH, digest=STRICT_AUDIT_SHA256
    )
    require(
        base_audit.get("postfinal_schema") == "rebar-postfinal-from-scratch-audit-v2"
        and base_audit.get("status") == "PASS"
        and base_audit.get("passed") is True
        and base_audit.get("verified_distinct_pipeline_count") == 4,
        "the actual current-source V2 audit no longer qualifies independent engines",
    )
    require(
        strict_audit.get("schema") == STRICT_AUDIT_SCHEMA
        and strict_audit.get("postfinal_schema") == STRICT_AUDIT_SCHEMA
        and strict_audit.get("status") == "PASS"
        and strict_audit.get("passed") is True
        and strict_audit.get("base_audit_report_sha256") == BASE_AUDIT_SHA256
        and strict_audit.get("native_elf_fingerprints") == EXPECTED_NATIVE
        and strict_audit.get("qualified_source_fingerprints") == EXPECTED_SOURCES,
        "the actual current V2 native-isolation audit was substituted",
    )
    for path, digest in (
        (BASE_AUDIT_SOURCE_PATH, BASE_AUDIT_SOURCE_SHA256),
        (STRICT_AUDIT_SOURCE_PATH, STRICT_AUDIT_SOURCE_SHA256),
        (GUARDED_WORKER_SOURCE, GUARDED_WORKER_SOURCE_SHA256),
        (GUARDED_WORKER_REPORT, GUARDED_WORKER_REPORT_SHA256),
        (UNIVERSAL_SOURCE, UNIVERSAL_SOURCE_SHA256),
        (FROZEN_ORACLE_SOURCE, FROZEN_ORACLE_SOURCE_SHA256),
    ):
        read_verified_bytes(path, expected=path, digest=digest)
    universal = read_verified_json(
        UNIVERSAL_REPORT, expected=UNIVERSAL_REPORT, digest=UNIVERSAL_REPORT_SHA256
    )
    require(
        universal.get("status") == "PASS"
        and universal.get("cases") == CASES
        and universal.get("observations_per_case") == 48
        and universal.get("total_comparisons") == CASES * 48 * len(CANDIDATES)
        and universal.get("mismatches") == 0
        and universal.get("comparison_complete") is True
        and universal.get("completed_candidates") == ["rust", "vm", "zig"]
        and universal.get("benchmark_or_timing_executed") is False
        and universal.get("holdout_cases_read") == 0
        and universal.get("external_regex_packages") == 0,
        "the actual current all-candidate Python compatibility proof is incomplete",
    )
    for role, (relative_path, digest) in EXPECTED_PROOFS.items():
        proof = ROOT / relative_path
        require(role in EXPECTED_PROOFS, "a current candidate proof role was substituted")
        read_verified_bytes(proof, expected=proof, digest=digest)
    for relative_path, digest in EXPECTED_SOURCES.items():
        path = ROOT / relative_path
        read_verified_bytes(path, expected=path, digest=digest)
    for role, path in EXPECTED_NATIVE_PATHS.items():
        read_verified_bytes(path, expected=path, digest=EXPECTED_NATIVE[role])
    require_candidate_free()


def render(
    *,
    summary: Path,
    summary_sha256: str,
    integrity: Path,
    integrity_sha256: str,
    manifest: Path,
    manifest_sha256: str,
    runner_sha256: str,
    output_dir: Path,
) -> dict[str, Any]:
    """Exclusively render six current SVGs from complete replayed V6 evidence."""

    require_candidate_free()
    verify_visual_primitives()
    require_render_inputs(
        summary=summary,
        summary_sha256=summary_sha256,
        integrity=integrity,
        integrity_sha256=integrity_sha256,
        manifest=manifest,
        manifest_sha256=manifest_sha256,
        runner_sha256=runner_sha256,
        output_dir=output_dir,
    )
    require(
        EVIDENCE.is_dir() and not EVIDENCE.is_symlink(),
        "the exact current public V6 evidence directory is missing or substituted",
    )
    read_verified_bytes(RUNNER, expected=RUNNER, digest=runner_sha256)
    verified_manifest = read_verified_json(
        manifest, expected=MANIFEST, digest=manifest_sha256
    )
    verified_summary = read_verified_json(
        summary, expected=SUMMARY, digest=summary_sha256
    )
    verified_integrity = read_verified_json(
        integrity, expected=INTEGRITY, digest=integrity_sha256
    )
    results = validate_documents(
        verified_manifest,
        verified_summary,
        verified_integrity,
        manifest_sha256=manifest_sha256,
        summary_sha256=summary_sha256,
        integrity_sha256=integrity_sha256,
        runner_sha256=runner_sha256,
    )
    read_verified_bytes(
        RAW,
        expected=RAW,
        digest=verified_summary["compressed_raw_sha256"],
    )
    verify_real_provenance()
    charts = build_charts(results)
    destinations = {
        suffix: EVIDENCE / f"{VERSION}-clear-{suffix}.svg" for suffix in SUFFIXES
    }
    states: dict[str, tuple[str, bytes | None]] = {}
    for suffix, destination in destinations.items():
        if destination.is_symlink():
            states[suffix] = ("symlink", None)
        elif not destination.exists():
            states[suffix] = ("missing", None)
        elif not destination.is_file():
            states[suffix] = ("nonregular", None)
        else:
            states[suffix] = ("regular", destination.read_bytes())
    create = plan_clear_outputs(charts, states)
    outputs = []
    for suffix in SUFFIXES:
        destination = destinations[suffix]
        payload = charts[suffix].encode("utf-8")
        if create[suffix]:
            flags = (
                os.O_WRONLY
                | os.O_CREAT
                | os.O_EXCL
                | getattr(os, "O_CLOEXEC", 0)
                | getattr(os, "O_NOFOLLOW", 0)
            )
            descriptor = os.open(destination, flags, 0o644)
            try:
                with os.fdopen(descriptor, "wb") as handle:
                    descriptor = -1
                    handle.write(payload)
                    handle.flush()
                    os.fsync(handle.fileno())
            finally:
                if descriptor != -1:
                    os.close(descriptor)
        outputs.append(
            {
                "chart": suffix,
                "path": str(destination.resolve()),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    require_candidate_free()
    return {
        "result": "PASS",
        "schema": "rebar-postfinal-public-practice-presentation-v2",
        "protocol_version": VERSION,
        "presentation_version": PRESENTATION_VERSION,
        "primitive_source_path": str(PRIMITIVE_SOURCE.resolve()),
        "primitive_source_sha256": PRIMITIVE_SOURCE_SHA256,
        "manifest_sha256": manifest_sha256,
        "runner_sha256": runner_sha256,
        "summary_sha256": summary_sha256,
        "integrity_sha256": integrity_sha256,
        "public_cases_per_candidate": CASES,
        "public_workload_categories": CATEGORIES,
        "public_operations": len(OPERATIONS),
        "public_raw_rows": RAW_ROWS,
        "public_correctness_checks": CORRECTNESS_CHECKS,
        "public_confidence_intervals": CONFIDENCE_INTERVALS,
        "individually_visible_public_losses": results.regression_count,
        "independent_candidates": len(CANDIDATES),
        "current_correctness_artifacts": len(EXPECTED_PROOFS),
        "source_audit_controls": 76,
        "isolation_audit_controls": 32,
        "candidate_imported": False,
        "timing_performed": False,
        "holdout_accessed": False,
        "final_holdout": "NOT OPENED",
        "native_final_memory": "NOT MEASURED",
        "charts": outputs,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render six clear, independently replayed current public V6 "
            "regex graphs without importing engines or accessing a final test."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run exclusively candidate-free, in-memory synthetic controls",
    )
    parser.add_argument("--summary", type=Path, help="exact current measured V6 summary")
    parser.add_argument(
        "--summary-sha256", help="externally supplied measured V6 summary SHA-256"
    )
    parser.add_argument("--integrity", type=Path, help="exact independent V6 replay")
    parser.add_argument(
        "--integrity-sha256", help="externally supplied independent V6 replay SHA-256"
    )
    parser.add_argument("--manifest", type=Path, help="exact prospectively frozen V6 plan")
    parser.add_argument(
        "--manifest-sha256", help="externally supplied frozen V6 plan SHA-256"
    )
    parser.add_argument(
        "--runner-sha256", help="externally supplied frozen V6 runner SHA-256"
    )
    parser.add_argument("--output-dir", type=Path, help="exact current V6 evidence directory")
    args = parser.parse_args(argv)
    values = (
        args.summary,
        args.summary_sha256,
        args.integrity,
        args.integrity_sha256,
        args.manifest,
        args.manifest_sha256,
        args.runner_sha256,
        args.output_dir,
    )
    if args.self_test:
        if any(value is not None for value in values):
            parser.error("candidate-free self-tests cannot read or write benchmark evidence")
    elif any(value is None for value in values):
        parser.error(
            "rendering requires --summary, --summary-sha256, --integrity, "
            "--integrity-sha256, --manifest, --manifest-sha256, "
            "--runner-sha256, and --output-dir"
        )
    elif any(
        not valid_sha256(value)
        for value in (
            args.summary_sha256,
            args.integrity_sha256,
            args.manifest_sha256,
            args.runner_sha256,
        )
    ):
        parser.error("all four external V6 evidence fingerprints must be lowercase SHA-256")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = (
            self_test()
            if args.self_test
            else render(
                summary=args.summary,
                summary_sha256=args.summary_sha256,
                integrity=args.integrity,
                integrity_sha256=args.integrity_sha256,
                manifest=args.manifest,
                manifest_sha256=args.manifest_sha256,
                runner_sha256=args.runner_sha256,
                output_dir=args.output_dir,
            )
        )
    except (
        KeyError,
        OSError,
        TypeError,
        UnicodeError,
        ValueError,
        ElementTree.ParseError,
    ) as error:
        print(f"independently verified public V6 presentation rejected: {error}")
        return 2
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
