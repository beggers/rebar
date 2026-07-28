#!/usr/bin/env python3
"""Show the frozen, untested Zig scanner change without claiming a result."""

from __future__ import annotations

import argparse
import builtins
import copy
import hashlib
import os
from pathlib import Path
import stat
import subprocess
import sys
import types


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v40.py"
OUTPUT = "docs/evidence/candidate-current-overview-v40"
SCHEMA = "rebar-candidate-current-overview-v40"
V39 = {
    "source": (
        "tools/render_candidate_current_overview_v39.py",
        "8adb7202644da2d19a4d2f50fe191de8d84007ce9b654a427a61fb4ea883c6b5",
        115526,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v39.inputs.json",
        "22e740d2f7a22e4bd485c5d6e83204bfd2c529f1b87dd041d4ed604849b69d6b",
        198039,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v39.json",
        "d25c486e36d82069c718f82a1f6281295d539606dcd72a0a6c2c295f5a4e4ca6",
        561943,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v39.svg",
        "eecc366a7e14e3bee67a801cbf4b07e848af3659a82cc0715a90525c05652a9a",
        11485,
    ),
}
ZIG = {
    "source": (
        "tools/apply_owned_zig_scanner_phrase_source_repair_v3.py",
        "9b5cf55b9d66729b84b91470f8ba5906208ccee09312b43c329acaab2ff34010",
        84556,
    ),
    "protocol": (
        "oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-REPAIR-V3.md",
        "78fccd7fffd33e5ecd9a9033d8225c294d82ee07f391eb46ccd621a08e0d38e1",
        6205,
    ),
    "contract": (
        "oracle/phase2/zig-scanner-phrase-source-repair-v3.json",
        "4eee672b4fe6f25f7481c34a34928f00d34a45a9e0675e024238a8ee5576fade",
        11117,
    ),
}
SCANNER_MATRIX = "83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c"
OVERFLOW_CASES = "e1b75493de4be5ea1583e30077737405112b22fdb072cd8b0e38e2770a2959e6"
FEATURE_STATUS = "SOURCE FROZEN; NOT APPLIED; CORRECTED CANDIDATE NOT RUN"


def previous_module() -> types.ModuleType:
    path, expected, size = V39["source"]
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags)
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != os.geteuid()
            or before.st_nlink != 1
            or stat.S_IMODE(before.st_mode) != 0o600
            or before.st_size != size
        ):
            raise ValueError("reject an incomplete or substituted committed V39 renderer")
        pieces: list[bytes] = []
        remaining = size
        while remaining:
            piece = os.read(descriptor, min(remaining, 262144))
            if not piece:
                raise ValueError("reject a truncated committed V39 renderer")
            pieces.append(piece)
            remaining -= len(piece)
        if os.read(descriptor, 1):
            raise ValueError("reject appended committed V39 renderer bytes")
        source = b"".join(pieces)
        after = os.fstat(descriptor)
        if (
            hashlib.sha256(source).hexdigest() != expected
            or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        ):
            raise ValueError("reject a changed committed V39 renderer")
    finally:
        os.close(descriptor)
    module = types.ModuleType("_rebar_exact_pushed_v39_for_v40_zig_feature")
    module.__file__ = str(ROOT / path)
    module.__package__ = ""
    exec(compile(source, module.__file__, "exec", dont_inherit=True), module.__dict__)
    module.runtime()
    module.need(
        module.SCHEMA == "rebar-candidate-current-overview-v39"
        and module.SELF == path,
        "load only the exact, complete, independently pushed V39 source",
    )
    return module


def validate_zig_contract(base: types.ModuleType, value: object) -> None:
    base.need(type(value) is dict, "reject an absent first-party Zig source contract")
    assert isinstance(value, dict)
    base.need(
        value.get("schema") == "rebar-owned-zig-scanner-phrase-source-repair-v3"
        and value.get("version") == 3
        and value.get("status") == "SOURCE FROZEN; CORRECTED CANDIDATE NOT RUN"
        and value.get("source") == {"path": ZIG["source"][0], "sha256": ZIG["source"][1]}
        and value.get("protocol") == {"path": ZIG["protocol"][0], "sha256": ZIG["protocol"][1]},
        "authenticate the exact three first-party Zig scanner source owners",
    )
    python = value.get("pinned_cpython")
    original = value.get("original_oracle")
    previous = value.get("actual_previous_matching")
    repair = value.get("construction_repair")
    gate = value.get("shared_candidate_producer_gate")
    effects = value.get("source_only_effects")
    reference = value.get("actual_corrected_same_context_reference")
    bounds = value.get("authenticated_historical_lower_bounds")
    additional = value.get("additional_callable_reference")
    policy = value.get("from_scratch_policy")
    base.need(
        type(python) is dict and python.get("version") == "3.14.6"
        and python.get("path") == base.PYTHON and python.get("sha256") == base.PYTHON_SHA
        and type(original) is dict and original.get("case_execution_denominator") == 31237
        and original.get("suite_count") == 13
        and original.get("named_private_waiver_count") == 13
        and original.get("scanner_case_count") == 1024
        and original.get("scanner_matrix_sha256") == SCANNER_MATRIX,
        "retain pinned Python and every original case, suite, waiver and scanner stimulus",
    )
    base.need(
        type(previous) is dict and previous.get("candidate_status") == "FAIL"
        and previous.get("candidate_workers") == 13
        and previous.get("case_execution_denominator") == 31237
        and previous.get("semantic_mismatch_count") == 1764
        and previous.get("verified_passing_case_count") == 3711
        and previous.get("infrastructure_failure_count") == 0
        and previous.get("archive_opened_by_source_freeze") is False,
        "never replace the actual 1,764 Zig differences with a prospective repair",
    )
    base.need(type(repair) is dict, "reject an unbound Zig scanner construction correction")
    assert isinstance(repair, dict)
    matrix = repair.get("complete_original_scanner_matrix")
    base.need(
        type(matrix) is dict and matrix.get("matrix_case_count") == 1024
        and matrix.get("matrix_sha256") == SCANNER_MATRIX
        and matrix.get("overflow_case_count") == 64
        and matrix.get("overflow_case_ids_sha256") == OVERFLOW_CASES
        and matrix.get("preserved_nonoverflow_case_count") == 960
        and matrix.get("overflow_family_case_counts")
        == {"nested-captures": 32, "numbered-captures": 16, "named-captures": 16}
        and matrix.get("candidate_imports") == 0
        and matrix.get("candidate_workers_started") == 0
        and matrix.get("reference_workers_started") == 0
        and matrix.get("native_activations") == 0,
        "freeze all 1,024 scanner cases and exactly 64 prospective overflow cases",
    )
    adapter = repair.get("corrected_private_adapter")
    base.need(
        repair.get("candidate_qualified") is False
        and repair.get("corrected_candidate_matching") == "NOT RUN"
        and repair.get("original_adapter", {}).get("modified") is False
        and repair.get("original_engine_modified") is False
        and repair.get("original_bridge_modified") is False
        and type(adapter) is dict and adapter.get("materialized") is False
        and adapter.get("outside_block_unchanged") is True
        and repair.get("verbose_scanner_620_mismatches")
        == "NOT REPAIRED; CORRECTED CANDIDATE NOT RUN",
        "a frozen in-memory Zig correction is not installation, a candidate run or a repair result",
    )
    base.need(
        type(reference) is dict and reference.get("reference_status") == "PASS"
        and reference.get("actual_reference_worker_count") == 2
        and reference.get("actual_reference_process_ids") == [81, 82]
        and reference.get("case_count_per_reference") == 6912
        and reference.get("full_reference_records_sha256") == base.FULL_RECORDS_SHA
        and reference.get("candidate_imports") == 0
        and reference.get("candidate_workers_started") == 0
        and reference.get("archive_opened_by_source_freeze") is False,
        "distinguish the two genuine Python reference passes from any Zig candidate result",
    )
    base.need(
        type(gate) is dict and gate.get("all_candidate_matching_blocked") is True
        and gate.get("corrected_v4_status") == "SOURCE FROZEN; CANDIDATES NOT RUN"
        and gate.get("corrected_v4_source_sha256") == base.PRODUCER_V4["source"][1]
        and gate.get("corrected_engine_runner_status") == "NOT FROZEN"
        and gate.get("required_corrected_engine_runners") == ["V6", "V8", "V10"]
        and gate.get("reason") == base.BLOCK_REASON
        and gate.get("source_apply") == "BLOCKED; CORRECTED V6/V8/V10 NOT FROZEN"
        and gate.get("native_build") == "BLOCKED; CORRECTED V6/V8/V10 NOT FROZEN"
        and gate.get("candidate_matching") == "BLOCKED; CORRECTED V6/V8/V10 NOT FROZEN",
        "never activate Zig or run a candidate through an obsolete V7/V9/Rust-V5 worker",
    )
    current = gate.get("current_producer") if isinstance(gate, dict) else None
    base.need(
        type(current) is dict
        and current.get("sha256") == base.PRODUCER_V4["source"][1]
        and current.get("protocol_sha256") == base.PRODUCER_V4["protocol"][1]
        and current.get("contract_sha256") == base.PRODUCER_V4["contract"][1]
        and current.get("status") == "FROZEN; CANDIDATE WORKERS STILL STALE",
        "pin the genuine frozen six-family V4 producer without claiming a fresh worker",
    )
    base.need(
        type(bounds) is dict and bounds.get("overview") == "V39"
        and bounds.get("repository_evidence_owner_count") == 164
        and bounds.get("authenticated_reference_count") == 169
        and bounds.get("whole_repository_census_claimed") is False
        and type(additional) is dict and additional.get("case_count") == 50
        and additional.get("reference_status") == "PASS"
        and additional.get("candidate_status") == "NOT RUN"
        and additional.get("included_in_original_denominator") is False,
        "preserve the at-least-164/169 history and the separate 50 Python-only cases",
    )
    base.need(
        type(policy) is dict
        and policy.get("stdlib_matching_engine") == "FORBIDDEN"
        and policy.get("external_regex_package") == "FORBIDDEN"
        and policy.get("another_candidate_engine") == "FORBIDDEN"
        and policy.get("matching_fallback") == "FORBIDDEN"
        and policy.get("runtime_non_delegation") == "NOT ESTABLISHED"
        and type(effects) is dict
        and all(effects.get(name) == 0 for name in (
            "benchmark_files_opened", "candidate_imports", "candidate_workers_started",
            "clock_samples", "files_written", "holdout_files_opened",
            "matching_archives_inflated", "matching_archives_opened",
            "native_builds_started", "native_libraries_loaded",
            "reference_archives_opened", "reference_workers_started",
        ))
        and value.get("holdout") == "NOT OPENED"
        and value.get("performance") == "NOT MEASURED"
        and value.get("memory") == "NOT MEASURED"
        and value.get("undefined_behavior") == "NOT MEASURED"
        and value.get("winner_selected") is False,
        "forbid delegated matching, side effects, performance claims and holdout access",
    )


def authenticate_v39(base: types.ModuleType) -> tuple[dict, dict, bytes]:
    for owner in V39.values():
        base.read_owner(*owner, private=True)
    inputs_raw, _ = base.read_owner(*V39["inputs"], private=True)
    summary_raw, _ = base.read_owner(*V39["summary"], private=True)
    svg_raw, _ = base.read_owner(*V39["svg"], private=True)
    inputs = base.document(inputs_raw, "complete independently pushed V39 graph inputs")
    summary = base.document(summary_raw, "complete independently pushed V39 graph summary")
    snapshot = summary.get("snapshot")
    base.validate_snapshot(snapshot)
    base.need(
        summary.get("schema") == "rebar-candidate-current-overview-v39-summary"
        and summary.get("version") == 39 and summary.get("status") == "PASS"
        and summary.get("source") == base.pin(*V39["source"])
        and summary.get("inputs") == base.pin(*V39["inputs"])
        and summary.get("svg") == base.pin(*V39["svg"])
        and inputs.get("schema") == "rebar-candidate-current-overview-v39-inputs"
        and inputs.get("version") == 39
        and inputs.get("renderer") == base.pin(*V39["source"])
        and svg_raw == base.make_svg(snapshot, V39["source"][1], V39["inputs"][1]),
        "independently reproduce all four exact committed V39 graph owners",
    )
    return summary, inputs, svg_raw


def validate_zig_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict, "reject a missing authenticated Zig source-only feature")
    assert isinstance(proof, dict)
    base.need(
        proof.get("schema") == SCHEMA + "-authenticated-zig-scanner-phrase-source-v3"
        and proof.get("status") == FEATURE_STATUS
        and proof.get("scanner_case_count") == 1024
        and proof.get("prospective_overflow_case_count") == 64
        and proof.get("preserved_nonoverflow_case_count") == 960
        and proof.get("scanner_matrix_sha256") == SCANNER_MATRIX
        and proof.get("overflow_case_ids_sha256") == OVERFLOW_CASES
        and proof.get("historical_semantic_mismatch_count") == 1764
        and proof.get("historical_verified_passing_case_count") == 3711
        and proof.get("source_applied") is False
        and proof.get("candidate_workers_started") == 0
        and proof.get("native_builds_started") == 0
        and proof.get("reference_workers_started") == 0
        and proof.get("candidate_matching_status") == "NOT RUN"
        and proof.get("measured_compatibility_improvement") == "NOT MEASURED"
        and proof.get("measured_performance_improvement") == "NOT MEASURED"
        and proof.get("holdout") == "NOT OPENED",
        "reject a fabricated applied, passing or faster Zig scanner feature",
    )
    for role, expected in ZIG.items():
        owner = proof.get(role)
        base.need(
            type(owner) is dict and owner.get("path") == expected[0]
            and owner.get("sha256") == expected[1] and owner.get("bytes") == expected[2]
            and owner.get("mode") == "0600" and owner.get("nlink") == 1
            and type(owner.get("inode")) is int and owner["inode"] > 0,
            "independently bind the complete genuine Zig " + role + " source owner",
        )
    contract = proof.get("complete_frozen_contract")
    validate_zig_contract(base, contract)
    binding = base.digest(base.canonical({
        "source": proof["source"], "protocol": proof["protocol"],
        "contract": proof["contract"], "complete_frozen_contract": contract,
    }))
    base.need(
        proof.get("complete_feature_binding_sha256") == binding,
        "bind all three Zig owners to every canonical frozen feature-contract byte",
    )


def authenticate_zig(base: types.ModuleType) -> dict:
    owners: dict[str, dict] = {}
    contract_raw = b""
    for role, expected in ZIG.items():
        raw, owner = base.read_owner(*expected, private=True)
        owners[role] = owner
        if role == "contract":
            contract_raw = raw
    contract = base.document(contract_raw, "complete authentic Zig scanner V3 source contract")
    validate_zig_contract(base, contract)
    proof = {
        "schema": SCHEMA + "-authenticated-zig-scanner-phrase-source-v3",
        "status": FEATURE_STATUS,
        **owners,
        "complete_frozen_contract": contract,
        "scanner_case_count": 1024,
        "prospective_overflow_case_count": 64,
        "preserved_nonoverflow_case_count": 960,
        "scanner_matrix_sha256": SCANNER_MATRIX,
        "overflow_case_ids_sha256": OVERFLOW_CASES,
        "historical_semantic_mismatch_count": 1764,
        "historical_verified_passing_case_count": 3711,
        "source_applied": False,
        "candidate_workers_started": 0,
        "native_builds_started": 0,
        "reference_workers_started": 0,
        "candidate_matching_status": "NOT RUN",
        "measured_compatibility_improvement": "NOT MEASURED",
        "measured_performance_improvement": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }
    proof["complete_feature_binding_sha256"] = base.digest(base.canonical({
        "source": owners["source"], "protocol": owners["protocol"],
        "contract": owners["contract"], "complete_frozen_contract": contract,
    }))
    validate_zig_proof(base, proof)
    return proof


def validate_snapshot(base: types.ModuleType, snapshot: object) -> None:
    base.validate_snapshot(snapshot)
    assert isinstance(snapshot, dict)
    proof = snapshot.get("zig_scanner_phrase_source_repair_v3")
    validate_zig_proof(base, proof)
    assert isinstance(proof, dict)
    base.need(
        snapshot.get("zig_scanner_phrase_source_repair_status") == FEATURE_STATUS
        and snapshot.get("zig_scanner_phrase_source_sha256") == ZIG["source"][1]
        and snapshot.get("zig_scanner_phrase_protocol_sha256") == ZIG["protocol"][1]
        and snapshot.get("zig_scanner_phrase_contract_sha256") == ZIG["contract"][1]
        and snapshot.get("zig_scanner_phrase_matrix_case_count") == 1024
        and snapshot.get("zig_scanner_phrase_prospective_case_count") == 64
        and snapshot.get("zig_scanner_phrase_preserved_nonoverflow_case_count") == 960
        and snapshot.get("zig_scanner_phrase_correction_applied") is False
        and snapshot.get("zig_scanner_phrase_corrected_matching_status") == "NOT RUN"
        and snapshot.get("zig_scanner_phrase_measured_mismatch_reduction") == "NOT MEASURED"
        and snapshot.get("zig_scanner_phrase_measured_speedup") == "NOT MEASURED"
        and snapshot.get("zig_v3_original_campaign", {}).get("semantic_mismatch_count")
        == 1764
        and snapshot.get("zig_v3_original_campaign", {}).get("verified_passing_case_count")
        == 3711,
        "preserve actual Zig losses and mark all 64 prospective scanner repairs unmeasured",
    )


def feature_fields(proof: dict) -> dict:
    return {
        "zig_scanner_phrase_source_repair_v3": copy.deepcopy(proof),
        "zig_scanner_phrase_source_repair_status": FEATURE_STATUS,
        "zig_scanner_phrase_source_sha256": ZIG["source"][1],
        "zig_scanner_phrase_protocol_sha256": ZIG["protocol"][1],
        "zig_scanner_phrase_contract_sha256": ZIG["contract"][1],
        "zig_scanner_phrase_matrix_case_count": 1024,
        "zig_scanner_phrase_prospective_case_count": 64,
        "zig_scanner_phrase_preserved_nonoverflow_case_count": 960,
        "zig_scanner_phrase_correction_applied": False,
        "zig_scanner_phrase_corrected_matching_status": "NOT RUN",
        "zig_scanner_phrase_measured_mismatch_reduction": "NOT MEASURED",
        "zig_scanner_phrase_measured_speedup": "NOT MEASURED",
    }


def move_y(line: str, shift: int) -> str:
    marker = ' y="'
    start = line.find(marker)
    if start < 0:
        return line
    start += len(marker)
    end = line.find('"', start)
    if end < 0 or not line[start:end].isdigit():
        return line
    value = int(line[start:end])
    if value < 307:
        return line
    return line[:start] + str(value + shift) + line[end:]


def make_svg(base: types.ModuleType, snapshot: dict, source: str, inputs: str) -> bytes:
    validate_snapshot(base, snapshot)
    base.checked(source, "exact V40 graph source")
    base.checked(inputs, "exact V40 graph inputs")
    visible = base.make_svg(snapshot, source, inputs).decode("utf-8")
    visible = visible.replace('height="1930" viewBox="0 0 1440 1930"',
                              'height="2040" viewBox="0 0 1440 2040"', 1)
    visible = visible.replace("v39-title", "v40-title")
    visible = visible.replace("v39-description", "v40-description")
    visible = visible.replace(
        "baseline passes; replacement tests remain blocked</title>",
        "baseline passes; Zig scanner correction is frozen, untested</title>",
        1,
    )
    visible = visible.replace(
        "replacement families remain blocked until corrected V8/V10/V6 ",
        "replacement families remain blocked until corrected V8/V10/V6 ",
        1,
    )
    shifted = [move_y(line, 110) for line in visible.splitlines()]
    insertion = next(
        index + 1 for index, line in enumerate(shifted)
        if "V7/V9 and Rust V5 workers are stale." in line
    )
    shifted[insertion:insertion] = [
        '<rect x="44" y="302" width="1352" height="91" rx="14" '
        'fill="#eef5ff" stroke="#b6cbee"/>',
        '<text x="65" y="337" class="warning">ZIG SCANNER CORRECTION '
        'FROZEN — 64 OF 1,024 CASES TARGETED; NOT APPLIED OR TESTED</text>',
        '<text x="67" y="365" class="body">Previous Zig result remains '
        '1,764 differences and 3,711 passing cases. Compatibility and speed '
        'improvements have not been measured.</text>',
    ]
    shifted.insert(-1, '<!-- Zig source correction is frozen only; matching, '
                        'native builds, speed measurements and the holdout remain blocked. -->')
    image = ("\n".join(shifted) + "\n").encode("utf-8")
    for required in (
        b"ZIG SCANNER CORRECTION", b"64 OF 1,024", b"NOT APPLIED OR TESTED",
        b"1,764", b"3,711", b"31,237", b"96 / 96", b"V8/V10/V6",
        b"ALL REPLACEMENT RUNS REMAIN BLOCKED", b"NOT MEASURED",
        b"4,194,304", b"NOT OPENED", b"164 / 169",
    ):
        base.need(required.lower() in image.lower(),
                  "visibly preserve the V40 source-only evidence: " + repr(required))
    return image


def build(base: types.ModuleType, source_sha: str, source_bytes: int,
          archive_sha: str, receipt_sha: str,
          producer_source: str, producer_protocol: str, producer_contract: str,
          zig_source: str, zig_protocol: str, zig_contract: str,
          ) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    source_sha = base.checked(source_sha, "actual V40 graph renderer")
    base.need(type(source_bytes) is int and 0 < source_bytes <= base.OWNER_LIMIT,
              "require the exact independently supplied V40 source size")
    source_raw, _ = base.read_owner(SELF, source_sha, source_bytes, private=True)
    for observed, role in ((zig_source, "source"), (zig_protocol, "protocol"),
                           (zig_contract, "contract")):
        base.need(base.checked(observed, "actual Zig feature " + role) == ZIG[role][1],
                  "reject a substituted Zig scanner feature " + role)
    previous, previous_inputs, _previous_svg = authenticate_v39(base)
    frozen = base.authenticate_source_freeze()
    _, stale = base.read_owner(*base.STALE_PRODUCER, private=True)
    _, falsification = base.read_owner(*base.FALSIFICATION, private=True)
    reference = base.authenticate_reference(archive_sha, receipt_sha)
    producer = base.authenticate_producer_v4(producer_source, producer_protocol,
                                             producer_contract)
    feature = authenticate_zig(base)
    shared = base.shared_fields(reference)
    snapshot = copy.deepcopy(previous["snapshot"])
    snapshot.update(shared)
    snapshot.update(feature_fields(feature))
    snapshot["corrected_candidate_producer_v4"] = copy.deepcopy(producer)
    validate_snapshot(base, snapshot)
    earlier = {name: base.pin(*owner) for name, owner in V39.items()}
    inputs = copy.deepcopy(previous_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs", "version": 40, "python": "3.14.6",
        "renderer": base.pin(SELF, source_sha, len(source_raw)),
        "previous_overview": earlier,
        "corrected_reference_source_freeze": frozen,
        "corrected_candidate_producer_v4": copy.deepcopy(producer),
        "actual_corrected_reference_archive": reference["archive"],
        "actual_corrected_reference_receipt": reference["receipt"],
        "preserved_actual_reference_falsification": falsification,
        "stale_original_candidate_producer": stale,
        "all_digest_addressed_history_path_count": 169,
        "candidate_qualified_count": 0,
        **shared,
        **feature_fields(feature),
    })
    inputs_raw = base.canonical(inputs)
    svg = make_svg(base, snapshot, source_sha, base.digest(inputs_raw))
    families = copy.deepcopy(previous["families"])
    for family in families:
        if family.get("family") == "zig":
            family.update(feature_fields(feature))
    summary = copy.deepcopy(previous)
    summary.update({
        "schema": SCHEMA + "-summary", "version": 40, "status": "PASS",
        "python": "3.14.6", "source": base.pin(SELF, source_sha, len(source_raw)),
        "inputs": base.pin(OUTPUT + ".inputs.json", base.digest(inputs_raw), len(inputs_raw)),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg), len(svg)),
        "previous_overview": earlier, "snapshot": snapshot, "families": families,
        "corrected_reference_source_freeze": frozen,
        "corrected_candidate_producer_v4": copy.deepcopy(producer),
        "preserved_actual_reference_falsification": falsification,
        "stale_original_candidate_producer": stale,
        "authenticated_digest_addressed_history_paths": 169,
        "qualified_candidate_count": 0,
        **shared,
        **feature_fields(feature),
    })
    return snapshot, (
        (OUTPUT + ".inputs.json", inputs_raw),
        (OUTPUT + ".json", base.canonical(summary)),
        (OUTPUT + ".svg", svg),
    )


def self_test(base: types.ModuleType) -> dict:
    historical = base.self_test()
    base.need(historical.get("status") == "PASS"
              and historical.get("reference_archive_gzip_inflation_count") == 0
              and historical.get("matching_archive_gzip_inflation_count") == 0,
              "first exercise every independently frozen V39 source-only boundary")
    rejected = 0
    with base.SourceOnlyWall() as wall:
        fixture = base.synthetic_snapshot()
        source = base.synthetic_owner(ZIG["source"], 824001)
        protocol = base.synthetic_owner(ZIG["protocol"], 824002)
        owner = base.synthetic_owner(ZIG["contract"], 824003)
        reference = fixture["actual_corrected_two_reference"]
        construction = {
            "candidate_qualified": False,
            "complete_original_scanner_matrix": {
                "matrix_case_count": 1024, "matrix_sha256": SCANNER_MATRIX,
                "overflow_case_count": 64, "overflow_case_ids_sha256": OVERFLOW_CASES,
                "preserved_nonoverflow_case_count": 960,
                "overflow_family_case_counts": {
                    "nested-captures": 32, "numbered-captures": 16,
                    "named-captures": 16,
                },
                "candidate_imports": 0, "candidate_workers_started": 0,
                "reference_workers_started": 0, "native_activations": 0,
            },
            "corrected_candidate_matching": "NOT RUN",
            "original_adapter": {"modified": False},
            "original_engine_modified": False, "original_bridge_modified": False,
            "corrected_private_adapter": {"materialized": False,
                                            "outside_block_unchanged": True},
            "verbose_scanner_620_mismatches":
                "NOT REPAIRED; CORRECTED CANDIDATE NOT RUN",
        }
        producer = fixture["corrected_candidate_producer_v4"]
        contract = {
            "schema": "rebar-owned-zig-scanner-phrase-source-repair-v3",
            "version": 3, "status": "SOURCE FROZEN; CORRECTED CANDIDATE NOT RUN",
            "source": {"path": ZIG["source"][0], "sha256": ZIG["source"][1]},
            "protocol": {"path": ZIG["protocol"][0], "sha256": ZIG["protocol"][1]},
            "pinned_cpython": {"path": base.PYTHON, "version": "3.14.6",
                               "sha256": base.PYTHON_SHA},
            "original_oracle": {"case_execution_denominator": 31237,
                                "suite_count": 13, "named_private_waiver_count": 13,
                                "scanner_case_count": 1024,
                                "scanner_matrix_sha256": SCANNER_MATRIX},
            "actual_previous_matching": {
                "candidate_status": "FAIL", "candidate_workers": 13,
                "case_execution_denominator": 31237, "semantic_mismatch_count": 1764,
                "verified_passing_case_count": 3711,
                "infrastructure_failure_count": 0,
                "archive_opened_by_source_freeze": False,
            },
            "construction_repair": construction,
            "actual_corrected_same_context_reference": {
                "reference_status": "PASS", "actual_reference_worker_count": 2,
                "actual_reference_process_ids": [81, 82],
                "case_count_per_reference": 6912,
                "full_reference_records_sha256": base.FULL_RECORDS_SHA,
                "candidate_imports": 0, "candidate_workers_started": 0,
                "archive_opened_by_source_freeze": False,
            },
            "shared_candidate_producer_gate": {
                "all_candidate_matching_blocked": True,
                "corrected_v4_status": "SOURCE FROZEN; CANDIDATES NOT RUN",
                "corrected_v4_source_sha256": base.PRODUCER_V4["source"][1],
                "corrected_engine_runner_status": "NOT FROZEN",
                "required_corrected_engine_runners": ["V6", "V8", "V10"],
                "reason": base.BLOCK_REASON,
                "source_apply": "BLOCKED; CORRECTED V6/V8/V10 NOT FROZEN",
                "native_build": "BLOCKED; CORRECTED V6/V8/V10 NOT FROZEN",
                "candidate_matching": "BLOCKED; CORRECTED V6/V8/V10 NOT FROZEN",
                "current_producer": {
                    "sha256": base.PRODUCER_V4["source"][1],
                    "protocol_sha256": base.PRODUCER_V4["protocol"][1],
                    "contract_sha256": base.PRODUCER_V4["contract"][1],
                    "status": "FROZEN; CANDIDATE WORKERS STILL STALE",
                },
            },
            "authenticated_historical_lower_bounds": {
                "overview": "V39", "repository_evidence_owner_count": 164,
                "authenticated_reference_count": 169,
                "whole_repository_census_claimed": False,
            },
            "additional_callable_reference": {
                "case_count": 50, "reference_status": "PASS",
                "candidate_status": "NOT RUN", "included_in_original_denominator": False,
            },
            "from_scratch_policy": {
                "stdlib_matching_engine": "FORBIDDEN",
                "external_regex_package": "FORBIDDEN",
                "another_candidate_engine": "FORBIDDEN",
                "matching_fallback": "FORBIDDEN",
                "runtime_non_delegation": "NOT ESTABLISHED",
            },
            "source_only_effects": {name: 0 for name in (
                "benchmark_files_opened", "candidate_imports", "candidate_workers_started",
                "clock_samples", "files_written", "holdout_files_opened",
                "matching_archives_inflated", "matching_archives_opened",
                "native_builds_started", "native_libraries_loaded",
                "reference_archives_opened", "reference_workers_started",
            )},
            "holdout": "NOT OPENED", "performance": "NOT MEASURED",
            "memory": "NOT MEASURED", "undefined_behavior": "NOT MEASURED",
            "winner_selected": False,
        }
        feature = {
            "schema": SCHEMA + "-authenticated-zig-scanner-phrase-source-v3",
            "status": FEATURE_STATUS, "source": source, "protocol": protocol,
            "contract": owner, "complete_frozen_contract": contract,
            "scanner_case_count": 1024, "prospective_overflow_case_count": 64,
            "preserved_nonoverflow_case_count": 960,
            "scanner_matrix_sha256": SCANNER_MATRIX,
            "overflow_case_ids_sha256": OVERFLOW_CASES,
            "historical_semantic_mismatch_count": 1764,
            "historical_verified_passing_case_count": 3711,
            "source_applied": False, "candidate_workers_started": 0,
            "native_builds_started": 0, "reference_workers_started": 0,
            "candidate_matching_status": "NOT RUN",
            "measured_compatibility_improvement": "NOT MEASURED",
            "measured_performance_improvement": "NOT MEASURED",
            "holdout": "NOT OPENED",
        }
        feature["complete_feature_binding_sha256"] = base.digest(base.canonical({
            "source": source, "protocol": protocol, "contract": owner,
            "complete_frozen_contract": contract,
        }))
        validate_zig_proof(base, feature)
        fixture.update(feature_fields(feature))
        fixture["zig_original_campaign_semantic_mismatch_count"] = 1764
        fixture["zig_original_campaign_verified_passing_case_count"] = 3711
        validate_snapshot(base, fixture)

        def reject(value: dict, label: str) -> None:
            nonlocal rejected
            try:
                validate_snapshot(base, value)
            except (base.GraphError, TypeError, ValueError, KeyError, AttributeError):
                rejected += 1
                return
            raise base.GraphError("accepted a forged V40 source-only feature: " + label)

        for key in feature_fields(feature):
            changed = copy.deepcopy(fixture)
            changed[key] = base.forged(changed[key])
            reject(changed, "visible-feature-" + key)
        for key, value in feature.items():
            changed = copy.deepcopy(fixture)
            changed["zig_scanner_phrase_source_repair_v3"][key] = base.forged(value)
            reject(changed, "feature-proof-" + key)
        for group in ("source", "protocol", "contract"):
            for key, value in feature[group].items():
                changed = copy.deepcopy(fixture)
                changed["zig_scanner_phrase_source_repair_v3"][group][key] = base.forged(value)
                reject(changed, "zig-owner-" + group + "-" + key)
        for group in (
            "pinned_cpython", "source", "protocol", "original_oracle",
            "actual_previous_matching", "actual_corrected_same_context_reference",
            "shared_candidate_producer_gate", "authenticated_historical_lower_bounds",
            "additional_callable_reference", "from_scratch_policy", "source_only_effects",
        ):
            for key, value in contract[group].items():
                changed = copy.deepcopy(fixture)
                changed["zig_scanner_phrase_source_repair_v3"]\
                    ["complete_frozen_contract"][group][key] = base.forged(value)
                reject(changed, "zig-contract-" + group + "-" + key)
        for group in ("complete_original_scanner_matrix", "corrected_private_adapter",
                      "original_adapter"):
            for key, value in construction[group].items():
                changed = copy.deepcopy(fixture)
                changed["zig_scanner_phrase_source_repair_v3"]\
                    ["complete_frozen_contract"]["construction_repair"][group][key]\
                    = base.forged(value)
                reject(changed, "zig-construction-" + group + "-" + key)
        image = make_svg(base, fixture, "a" * 64, "b" * 64)
        base.need(image.endswith(b"\n") and not image.endswith(b"\n\n"),
                  "emit exactly one final SVG linefeed")
        probes = (
            ("filesystem", lambda: builtins.open("forbidden-v40")),
            ("filesystem", lambda: os.open("forbidden-v40", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v40")),
            ("write", lambda: os.mkdir("forbidden-v40")),
            ("process", lambda: subprocess.run(("forbidden-v40",))),
            ("process", lambda: subprocess.Popen(("forbidden-v40",))),
            ("process", lambda: os.execv("/forbidden-v40", [])),
        )
        for kind, action in probes:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(wall.blocked[kind] == before + 1,
                          "physically block the genuine V40 source-only effect: " + kind)
            else:
                raise base.GraphError("a genuine V40 source-only effect escaped: " + kind)
        base.need(rejected >= 90, "independently reject altered Zig owner and feature controls")
        return {
            "schema": SCHEMA + "-source-only-self-test", "version": 40,
            "status": "PASS", "synthetic_only": True,
            "previous_v39_hostile_controls": historical["rejected_hostile_control_count"],
            "zig_feature_rejected_hostile_controls": rejected,
            "rejected_hostile_control_count":
                historical["rejected_hostile_control_count"] + rejected,
            "previous_v39_blocked_effects_by_kind": historical["blocked_effects_by_kind"],
            "blocked_effects_by_kind": dict(wall.blocked),
            "full_case_denominator": 31237, "suite_count": 13,
            "private_waiver_count": 13,
            "zig_scanner_phrase_source_repair_status": FEATURE_STATUS,
            "zig_scanner_phrase_matrix_case_count": 1024,
            "zig_scanner_phrase_prospective_case_count": 64,
            "zig_scanner_phrase_correction_applied": False,
            "zig_scanner_phrase_corrected_matching_status": "NOT RUN",
            "zig_scanner_phrase_measured_mismatch_reduction": "NOT MEASURED",
            "zig_scanner_phrase_measured_speedup": "NOT MEASURED",
            "actual_reference_evidence_read_by_self_test": 0,
            "all_candidate_matching_blocked": True,
            "candidate_case_producer_corrected_v4_status":
                "SOURCE FROZEN; CANDIDATES NOT RUN",
            "actual_candidate_workers_started_by_graph": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "candidate_matching_archives_opened_by_graph": 0,
            "matching_archive_gzip_inflation_count": 0,
            "reference_archive_gzip_inflation_count": 0,
            "hidden_cases_read": 0, "clock_samples": 0,
            "timing_trials_run": 0, "workspace_mutations": 0,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "final_holdout_opened": False, "winner_selected": False,
        }


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    allowed = {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
    base.need(path in allowed and type(raw) is bytes and 0 < len(raw) <= base.OWNER_LIMIT,
              "publish only one of the three exclusively authorized new V40 graph outputs")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0,
                      "reject an incompletely written exclusive V40 graph owner")
            remaining = remaining[count:]
        os.fsync(handle)
        observed = os.fstat(handle)
        base.need(observed.st_uid == os.geteuid() and observed.st_nlink == 1
                  and observed.st_size == len(raw)
                  and stat.S_IMODE(observed.st_mode) == 0o600,
                  "require an owner-only, private, synchronized V40 graph owner")
    finally:
        os.close(handle)
    directory = os.open(str(ROOT / Path(path).parent),
                        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                        | getattr(os, "O_CLOEXEC", 0)
                        | getattr(os, "O_NOFOLLOW", 0))
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    observed, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(observed == raw, "read back every durable generated V40 graph byte")


def result(base: types.ModuleType, source: str, outputs: dict[str, bytes],
           written: bool, suffix: str) -> dict:
    return {
        "schema": SCHEMA + suffix, "version": 40, "status": "PASS",
        "source_sha256": source,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 39,
        "previous_overview_source_sha256": V39["source"][1],
        "previous_overview_inputs_sha256": V39["inputs"][1],
        "previous_overview_summary_sha256": V39["summary"][1],
        "previous_overview_svg_sha256": V39["svg"][1],
        "zig_scanner_phrase_source_sha256": ZIG["source"][1],
        "zig_scanner_phrase_protocol_sha256": ZIG["protocol"][1],
        "zig_scanner_phrase_contract_sha256": ZIG["contract"][1],
        "zig_scanner_phrase_source_repair_status": FEATURE_STATUS,
        "zig_scanner_phrase_matrix_case_count": 1024,
        "zig_scanner_phrase_prospective_case_count": 64,
        "zig_scanner_phrase_correction_applied": False,
        "zig_scanner_phrase_corrected_matching_status": "NOT RUN",
        "zig_scanner_phrase_measured_mismatch_reduction": "NOT MEASURED",
        "zig_scanner_phrase_measured_speedup": "NOT MEASURED",
        "historical_zig_semantic_mismatch_count": 1764,
        "historical_zig_verified_passing_case_count": 3711,
        "corrected_candidate_producer_v4_source_sha256": base.PRODUCER_V4["source"][1],
        "corrected_candidate_producer_v4_protocol_sha256": base.PRODUCER_V4["protocol"][1],
        "corrected_candidate_producer_v4_contract_sha256": base.PRODUCER_V4["contract"][1],
        "phase_one_reference_gate_status": "PASS",
        "candidate_facing_self_oracle_status": "PASS",
        "same_context_reference_correction_status": "PASS",
        "corrected_reference_status": "PASS",
        "corrected_reference_actual_worker_count": 2,
        "corrected_reference_process_ids": [81, 82],
        "corrected_reference_case_count_per_worker": 6912,
        "corrected_reference_total_observed_case_count": 13824,
        "corrected_reference_full_records_sha256": base.FULL_RECORDS_SHA,
        "full_case_denominator": 31237, "suite_count": 13,
        "private_waiver_count": 13, "original_cases_removed": 0,
        "additional_private_waivers": 0, "case_denominator_changed": False,
        "c_pattern_equality_failure_waived": False,
        "zig_pattern_equality_failure_waived": False,
        "authenticated_evidence_owner_lower_bound": 164,
        "authenticated_history_reference_lower_bound": 169,
        "exact_whole_repository_evidence_owner_count": "NOT MEASURED",
        "exact_whole_repository_reference_count": "NOT MEASURED",
        "all_candidate_matching_blocked": True,
        "candidate_matching_block_reason": base.BLOCK_REASON,
        "candidate_case_producer_status": "FROZEN; CANDIDATE WORKERS STILL STALE",
        "candidate_case_producer_corrected_v4_status":
            "SOURCE FROZEN; CANDIDATES NOT RUN",
        "qualified_candidate_count": 0,
        "historical_rust_semantic_mismatch_count": 1036,
        "historical_c_semantic_mismatch_count": 1230,
        "additional_signature_reference_status": "PASS",
        "additional_signature_reference_cases_executed": 50,
        "additional_signature_candidate_status": "NOT RUN",
        "outputs_written": written,
        "reference_archive_gzip_inflation_count": 1,
        "reference_archive_compressed_bytes_read": base.ARCHIVE_PIN[2],
        "reference_archive_uncompressed_bytes_read": base.UNCOMPRESSED_BYTES,
        "reference_archive_uncompressed_sha256": base.UNCOMPRESSED_SHA,
        "candidate_matching_archives_opened_by_graph": 0,
        "matching_archive_gzip_inflation_count": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "canonical_target_reads": 0, "canonical_target_stats": 0,
        "hidden_cases_read": 0, "clock_samples": 0, "timing_trials_run": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False, "winner_selected": False,
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    parser.add_argument("--archive-sha256")
    parser.add_argument("--receipt-sha256")
    parser.add_argument("--producer-source-sha256")
    parser.add_argument("--producer-protocol-sha256")
    parser.add_argument("--producer-contract-sha256")
    parser.add_argument("--zig-source-sha256")
    parser.add_argument("--zig-protocol-sha256")
    parser.add_argument("--zig-contract-sha256")
    for name in ("inputs", "summary", "svg"):
        parser.add_argument("--" + name + "-sha256")
    options = parser.parse_args(arguments)
    try:
        base = previous_module()
        if options.self_test:
            base.need(all(getattr(options, name) is None for name in (
                "source_sha256", "source_bytes", "archive_sha256", "receipt_sha256",
                "producer_source_sha256", "producer_protocol_sha256",
                "producer_contract_sha256", "zig_source_sha256",
                "zig_protocol_sha256", "zig_contract_sha256", "inputs_sha256",
                "summary_sha256", "svg_sha256",
            )), "synthetic graph tests cannot accept actual archives or graph owners")
            sys.stdout.buffer.write(base.canonical(self_test(base)))
            return 0
        source = base.checked(options.source_sha256, "exact V40 graph renderer")
        archive = base.checked(options.archive_sha256, "actual corrected reference archive")
        receipt = base.checked(options.receipt_sha256, "actual corrected reference receipt")
        producer_source = base.checked(options.producer_source_sha256, "frozen V4 source")
        producer_protocol = base.checked(options.producer_protocol_sha256, "frozen V4 protocol")
        producer_contract = base.checked(options.producer_contract_sha256, "frozen V4 contract")
        zig_source = base.checked(options.zig_source_sha256, "frozen Zig feature source")
        zig_protocol = base.checked(options.zig_protocol_sha256, "frozen Zig feature protocol")
        zig_contract = base.checked(options.zig_contract_sha256, "frozen Zig feature contract")
        _snapshot, pairs = build(base, source, options.source_bytes, archive, receipt,
                                 producer_source, producer_protocol, producer_contract,
                                 zig_source, zig_protocol, zig_contract)
        outputs = dict(pairs)
        if options.render:
            base.need(options.inputs_sha256 is None and options.summary_sha256 is None
                      and options.svg_sha256 is None,
                      "render exactly the three new, exclusive V40 graph outputs")
            for path, raw in pairs:
                publish(base, path, raw)
            sys.stdout.buffer.write(base.canonical(result(base, source, outputs,
                                                         True, "-published")))
            return 0
        expected = {
            OUTPUT + ".inputs.json": base.checked(options.inputs_sha256,
                                                  "frozen V40 graph inputs"),
            OUTPUT + ".json": base.checked(options.summary_sha256,
                                            "frozen V40 graph summary"),
            OUTPUT + ".svg": base.checked(options.svg_sha256,
                                           "frozen V40 graph image"),
        }
        for path, fingerprint in expected.items():
            observed, _ = base.read_owner(path, fingerprint, len(outputs[path]),
                                          private=True)
            base.need(observed == outputs[path],
                      "independently reproduce every complete frozen V40 graph output")
        sys.stdout.buffer.write(base.canonical(result(base, source, outputs, False,
                                                      "-read-only-frozen-context")))
        return 0
    except (ValueError, OSError, TypeError, EOFError, KeyError, AttributeError,
            RecursionError) as error:
        sys.stderr.write("current V40 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V40 overview rejected: " + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
