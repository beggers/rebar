#!/usr/bin/env python3
"""Show a frozen C-only test runner without claiming six runnable engines."""

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
SELF = "tools/render_candidate_current_overview_v41.py"
OUTPUT = "docs/evidence/candidate-current-overview-v41"
SCHEMA = "rebar-candidate-current-overview-v41"
V40 = {
    "source": (
        "tools/render_candidate_current_overview_v40.py",
        "15dc12f2d6a3c329d326f8d5b53bd2b1db7e82d01bb7c55e1178bd4ec0587c14",
        50218,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v40.inputs.json",
        "a05ee04da984b618781bc31fe0deba6d1daf7c44256d7804e539ddd1392a2ffd",
        211598,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v40.json",
        "5e9f2216fc2a0ab4742d36a1aa49c422880a8ae17e3e1534da9b362ca0eeda92",
        602620,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v40.svg",
        "7e9189fb06410903b9f5d851648893e7984b8ecd1ba7d42c73329c1f985857e3",
        12009,
    ),
}

# All four values were independently reviewed and explicitly released by the
# experiment owner. The source inventory is not executable runner coverage.
RUNNER_PINS_RELEASED = True
RUNNER = {
    "runner": (
        "tools/run_frozen_p0_candidate_v10.py",
        "c114b578ac7ebfe28b45aa3b3407b81d05333f4470fa3047fd338ed3541c185a",
        91132,
    ),
    "worker": (
        "tools/run_frozen_p0_candidate_worker_v8.py",
        "78634bbcb5f55c560ea4b38c81ca395f4d4d5385c285bd0a3c25b395e3dd5ee1",
        95361,
    ),
    "protocol": (
        "oracle/phase2/P0-CANDIDATE-PROTOCOL-V10.md",
        "2d773fc55fe7c0a61e044a0e7deef81c8e36ffa0a9a744f4e60901f7a953c2ae",
        6792,
    ),
    "contract": (
        "oracle/phase2/p0-candidate-protocol-v10.json",
        "8eb72f1d94af85db1f1b282dda4d6ce1839f51f492ed2c7436c666d792f9b737",
        21238,
    ),
}
C_STATUS = "C-ONLY RUNNER SOURCE FROZEN; CORRECTED C MATCHING NOT RUN"
C_BLOCK_REASON = (
    "The corrected C-only V8/V10 test runner is frozen but no corrected C "
    "candidate run has been authorized or executed. Rust V6 is uncommitted; "
    "the five other first-party source designs have no frozen corrected runner."
)


def load_v40() -> tuple[types.ModuleType, types.ModuleType]:
    path, expected, size = V40["source"]
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
            raise ValueError("reject a substituted, incomplete, nonprivate V40 renderer")
        remaining = size
        pieces: list[bytes] = []
        while remaining:
            piece = os.read(descriptor, min(remaining, 262144))
            if not piece:
                raise ValueError("reject a truncated exact V40 renderer")
            pieces.append(piece)
            remaining -= len(piece)
        if os.read(descriptor, 1):
            raise ValueError("reject extra bytes after the exact V40 renderer")
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        if (
            hashlib.sha256(raw).hexdigest() != expected
            or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        ):
            raise ValueError("reject a changed or replaced published V40 renderer")
    finally:
        os.close(descriptor)
    previous = types.ModuleType("_rebar_exact_pushed_v40_for_c_only_v41")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    base = previous.previous_module()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v40"
        and previous.SELF == path,
        "load only the exact independently pushed V40 graph and its V39 safety wall",
    )
    return previous, base


def authenticate_v40(previous: types.ModuleType, base: types.ModuleType) -> tuple[dict, dict]:
    for owner in V40.values():
        base.read_owner(*owner, private=True)
    inputs_raw, _ = base.read_owner(*V40["inputs"], private=True)
    summary_raw, _ = base.read_owner(*V40["summary"], private=True)
    svg_raw, _ = base.read_owner(*V40["svg"], private=True)
    inputs = base.document(inputs_raw, "complete independently pushed V40 inputs")
    summary = base.document(summary_raw, "complete independently pushed V40 summary")
    snapshot = summary.get("snapshot")
    previous.validate_snapshot(base, snapshot)
    base.need(
        summary.get("schema") == "rebar-candidate-current-overview-v40-summary"
        and summary.get("version") == 40
        and summary.get("status") == "PASS"
        and summary.get("source") == base.pin(*V40["source"])
        and summary.get("inputs") == base.pin(*V40["inputs"])
        and summary.get("svg") == base.pin(*V40["svg"])
        and inputs.get("schema") == "rebar-candidate-current-overview-v40-inputs"
        and inputs.get("version") == 40
        and inputs.get("renderer") == base.pin(*V40["source"])
        and svg_raw == previous.make_svg(base, snapshot, V40["source"][1],
                                         V40["inputs"][1]),
        "independently preserve all four committed V40 graph owners and complete history",
    )
    return summary, inputs


def validate_runner_contract(base: types.ModuleType, document: object) -> None:
    base.need(type(document) is dict, "reject a missing complete C-only runner contract")
    assert isinstance(document, dict)
    base.need(
        document.get("schema") == "rebar-frozen-python-re-p0-candidate-protocol-v10"
        and document.get("version") == 10
        and document.get("case_execution_denominator") == 31237
        and document.get("suite_count") == 13
        and document.get("named_private_waiver_count") == 13
        and document.get("source_family_count") == 6
        and document.get("source_inventory_family_count") == 6
        and document.get("source_inventory_owner_count") == 25
        and document.get("six_family_inventory_is_source_only") is True
        and document.get("candidate_execution_scope")
        == "C-ONLY; VERIFIED C15 NATIVE REQUIRED"
        and document.get("runnable_candidate_family_count") == 1
        and document.get("runnable_candidate_families") == ["c"]
        and type(document.get("source_inventory_families")) is list
        and [item.get("family") for item in document["source_inventory_families"]
             if type(item) is dict]
        == ["rust", "c", "zig", "cpp", "go", "fortran"],
        "preserve the complete original suite and distinguish six source families from one runnable family",
    )
    family = document.get("candidate_family")
    base.need(
        type(family) is dict and family.get("name") == "c"
        and family.get("external_regex_engine_allowed") is False
        and family.get("shared_candidate_engine_allowed") is False
        and family.get("stdlib_engine_delegation_allowed") is False,
        "reject any claim that the C-only worker runs Rust, Zig or six families",
    )
    for role in ("runner", "worker", "protocol"):
        owner = document.get(role)
        expected = RUNNER[role]
        base.need(
            type(owner) is dict and owner.get("path") == expected[0]
            and owner.get("sha256") == expected[1],
            "bind the exact caller-pinned C-only " + role + " owner",
        )
    runtime = document.get("pinned_runtime")
    phase_one = document.get("phase_one")
    boundary = document.get("phase_boundary")
    corrected = document.get("corrected_candidate_context_reference")
    published_v40 = document.get("published_current_overview_v40")
    original = document.get("original_suites")
    base.need(
        type(runtime) is dict and runtime.get("version") == "3.14.6"
        and runtime.get("path") == base.PYTHON
        and runtime.get("sha256") == base.PYTHON_SHA
        and type(phase_one) is dict
        and phase_one.get("case_execution_denominator") == 31237
        and phase_one.get("suite_count") == 13
        and phase_one.get("named_private_waiver_count") == 13
        and type(original) is list and len(original) == 13
        and all(type(item) is dict for item in original)
        and sum(item.get("case_execution_count", -1) for item in original) == 31237
        and type(corrected) is dict
        and corrected.get("records_sha256") == base.FULL_RECORDS_SHA
        and corrected.get("actual_independent_reference_pids") == [81, 82]
        and corrected.get("cache_cohort_case_count") == 96
        and corrected.get("cache_cohort_records_sha256") == base.CACHE_RECORDS_SHA
        and corrected.get("source_context_reads_reference_archive") is False
        and corrected.get("source_context_inflates_reference_archive") is False
        and corrected.get("c_pattern_equality_failure_waived") is False
        and type(published_v40) is dict
        and all(type(published_v40.get(role)) is dict
                and published_v40[role].get("path") == owner[0]
                and published_v40[role].get("sha256") == owner[1]
                for role, owner in V40.items()),
        "bind the corrected C runner to the exact stable Python and all unchanged cases",
    )
    base.need(
        type(boundary) is dict
        and boundary.get("actual_candidate_workers") == 0
        and boundary.get("actual_reference_workers") == 0
        and boundary.get("actual_native_activations") == 0
        and boundary.get("actual_source_builds") == 0
        and boundary.get("candidate_qualified_count") == 0
        and boundary.get("candidate_correctness") == "NOT MEASURED"
        and boundary.get("hidden_cases_read") == 0
        and boundary.get("benchmark_files_read") == 0
        and boundary.get("clock_samples") == 0
        and boundary.get("timing_trials_run") == 0
        and boundary.get("holdout") == "NOT OPENED"
        and boundary.get("performance") == "NOT MEASURED"
        and boundary.get("memory") == "NOT MEASURED"
        and boundary.get("winner_selected") is False,
        "a frozen C runner cannot qualify a candidate, start a worker or open the holdout",
    )


def validate_runner_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict, "reject missing genuine C-only runner evidence")
    assert isinstance(proof, dict)
    base.need(
        proof.get("schema") == SCHEMA + "-authenticated-c-only-runner-v10"
        and proof.get("status") == C_STATUS
        and proof.get("candidate_family") == "c"
        and proof.get("runnable_candidate_family_count") == 1
        and proof.get("first_party_source_inventory_family_count") == 6
        and proof.get("other_corrected_candidate_family_count") == 5
        and proof.get("other_corrected_candidate_matching_status") == "NOT RUN"
        and proof.get("corrected_c_matching_status") == "NOT RUN"
        and proof.get("actual_candidate_workers_started") == 0
        and proof.get("actual_reference_workers_started") == 0
        and proof.get("actual_compiler_processes_started") == 0
        and proof.get("qualified_candidate_count") == 0
        and proof.get("rust_v6_runner_status") == "UNCOMMITTED"
        and proof.get("performance") == "NOT MEASURED"
        and proof.get("memory") == "NOT MEASURED"
        and proof.get("holdout") == "NOT OPENED",
        "reject a fabricated six-family, passing, measured or Rust-authorized C runner",
    )
    for role, expected in RUNNER.items():
        owner = proof.get(role)
        base.need(
            type(owner) is dict and owner.get("path") == expected[0]
            and owner.get("sha256") == expected[1]
            and owner.get("bytes") == expected[2]
            and owner.get("mode") == "0600"
            and owner.get("nlink") == 1
            and type(owner.get("inode")) is int and owner["inode"] > 0,
            "independently authenticate the complete C-only runner " + role + " owner",
        )
    contract = proof.get("complete_frozen_contract")
    validate_runner_contract(base, contract)
    expected = base.digest(base.canonical({
        "runner": proof["runner"], "worker": proof["worker"],
        "protocol": proof["protocol"], "contract": proof["contract"],
        "complete_frozen_contract": contract,
    }))
    base.need(
        proof.get("complete_runner_binding_sha256") == expected,
        "bind every complete C-only worker, controller and protocol byte",
    )


def authenticate_runner(base: types.ModuleType) -> dict:
    base.need(
        RUNNER_PINS_RELEASED is True,
        "V41 rendering is prohibited until four independently reviewed C-only runner pins are released",
    )
    owners: dict[str, dict] = {}
    contract_raw = b""
    for role, expected in RUNNER.items():
        raw, owner = base.read_owner(*expected, private=True)
        owners[role] = owner
        if role == "contract":
            contract_raw = raw
    contract = base.document(contract_raw, "complete corrected C-only V10 source contract")
    validate_runner_contract(base, contract)
    proof = {
        "schema": SCHEMA + "-authenticated-c-only-runner-v10",
        "status": C_STATUS,
        **owners,
        "complete_frozen_contract": contract,
        "candidate_family": "c",
        "runnable_candidate_family_count": 1,
        "first_party_source_inventory_family_count": 6,
        "other_corrected_candidate_family_count": 5,
        "other_corrected_candidate_matching_status": "NOT RUN",
        "corrected_c_matching_status": "NOT RUN",
        "actual_candidate_workers_started": 0,
        "actual_reference_workers_started": 0,
        "actual_compiler_processes_started": 0,
        "qualified_candidate_count": 0,
        "rust_v6_runner_status": "UNCOMMITTED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }
    proof["complete_runner_binding_sha256"] = base.digest(base.canonical({
        "runner": owners["runner"], "worker": owners["worker"],
        "protocol": owners["protocol"], "contract": owners["contract"],
        "complete_frozen_contract": contract,
    }))
    validate_runner_proof(base, proof)
    return proof


def runner_fields(proof: dict) -> dict:
    return {
        "corrected_c_only_runner_v10": copy.deepcopy(proof),
        "corrected_c_only_runner_status": C_STATUS,
        "corrected_c_only_runner_family": "c",
        "corrected_c_only_runnable_family_count": 1,
        "first_party_source_inventory_family_count": 6,
        "other_corrected_candidate_family_count": 5,
        "other_corrected_candidate_matching_status": "NOT RUN",
        "corrected_c_matching_status": "NOT RUN",
        "corrected_c_candidate_workers_started": 0,
        "corrected_c_candidate_qualified": False,
        "all_candidate_matching_blocked": True,
        "candidate_matching_block_reason": C_BLOCK_REASON,
        "candidate_case_producer_status":
            "V4 SOURCE FROZEN; C-ONLY V8/V10 RUNNER FROZEN; C MATCHING NOT RUN",
        "historical_stale_candidate_worker_versions": ["V7", "V9", "RUST V5"],
        "stale_candidate_worker_versions": ["RUST V5"],
        "required_corrected_candidate_runner_versions": ["RUST V6"],
        "pending_corrected_candidate_families":
            ["rust", "zig", "cpp", "go", "fortran"],
        "rust_v6_runner_status": "UNCOMMITTED",
        "corrected_c_only_runner_source_sha256": RUNNER["runner"][1],
        "corrected_c_only_worker_source_sha256": RUNNER["worker"][1],
        "corrected_c_only_protocol_sha256": RUNNER["protocol"][1],
        "corrected_c_only_contract_sha256": RUNNER["contract"][1],
        "corrected_c_matching_mismatch_reduction": "NOT MEASURED",
        "corrected_c_matching_speedup": "NOT MEASURED",
    }


def project_v40_snapshot(base: types.ModuleType, snapshot: dict) -> dict:
    historical = copy.deepcopy(snapshot)
    reference = snapshot.get("actual_corrected_two_reference")
    base.need(type(reference) is dict,
              "preserve the exact historical complete two-process Python reference")
    old = base.shared_fields(reference)
    for name in (
        "candidate_matching_block_reason", "candidate_case_producer_status",
        "stale_candidate_worker_versions", "required_corrected_candidate_runner_versions",
    ):
        historical[name] = old[name]
    return historical


def validate_snapshot(previous: types.ModuleType, base: types.ModuleType,
                      snapshot: object) -> None:
    assert isinstance(snapshot, dict)
    previous.validate_snapshot(base, project_v40_snapshot(base, snapshot))
    proof = snapshot.get("corrected_c_only_runner_v10")
    validate_runner_proof(base, proof)
    for name, expected in runner_fields(proof).items():
        base.need(snapshot.get(name) == expected,
                  "reject a forged C-only V41 snapshot field: " + name)
    base.need(
        snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("performance") == "NOT MEASURED"
        and snapshot.get("memory") == "NOT MEASURED"
        and snapshot.get("final_holdout_opened") is False
        and snapshot.get("winner_selected") is False,
        "never confuse a frozen C worker with compatibility, speed or final evidence",
    )


def move_y(line: str, shift: int) -> str:
    marker = ' y="'
    start = line.find(marker)
    if start < 0:
        return line
    start += len(marker)
    end = line.find('"', start)
    if end < 0 or not line[start:end].isdigit():
        return line
    position = int(line[start:end])
    if position < 302:
        return line
    return line[:start] + str(position + shift) + line[end:]


def make_svg(previous: types.ModuleType, base: types.ModuleType,
             snapshot: dict, source: str, inputs: str) -> bytes:
    validate_snapshot(previous, base, snapshot)
    visible = previous.make_svg(
        base, project_v40_snapshot(base, snapshot), source, inputs,
    ).decode("utf-8")
    visible = visible.replace('height="2040" viewBox="0 0 1440 2040"',
                              'height="2150" viewBox="0 0 1440 2150"', 1)
    visible = visible.replace("v40-title", "v41-title")
    visible = visible.replace("v40-description", "v41-description")
    visible = visible.replace(
        "baseline passes; Zig scanner correction is frozen, untested</title>",
        "baseline passes; corrected C test runner is frozen, untested</title>",
        1,
    )
    visible = visible.replace(
        "Corrected V4 cases are source frozen, while all six replacement "
        "families remain blocked until corrected V8/V10/V6 workers are frozen.",
        "The corrected C-only V8/V10 runner is frozen, but C matching has "
        "not been run. Rust V6 is uncommitted and the other five first-party "
        "source designs do not yet have corrected runners.",
        1,
    )
    visible = visible.replace(
        "Corrected cases are frozen; replacement runners still need updating.",
        "Six first-party source designs; only the corrected C test runner is frozen.",
        1,
    )
    visible = visible.replace(
        "ALL REPLACEMENT RUNS REMAIN BLOCKED — V4 CASES FROZEN; V7/V9 RUNNERS STILL STALE",
        "NO CORRECTED C MATCHING HAS RUN — FIVE OTHER RUNNERS ARE NOT FROZEN",
        1,
    )
    visible = visible.replace(
        "V4 cases are frozen; V7/V9 and Rust V5 workers are stale. V8/V10/V6 must be frozen before any replacement is run.",
        "One corrected C test runner is frozen. Rust V6 is uncommitted; no corrected candidate matching has run.",
        1,
    )
    visible = visible.replace(
        "V4 FROZEN; V7/V9 and Rust V5 remain stale pending corrected V8/V10/V6.",
        "V4 and the C-only V8/V10 runner are frozen; Rust V6 is uncommitted.",
        1,
    )
    visible = visible.replace(
        "BLOCKED: freeze, commit, and push corrected V8/V10/V6 before any candidate run.",
        "C matching NOT RUN; Rust, Zig, Go, C++ and Fortran runners are NOT FROZEN.",
        1,
    )
    shifted = [move_y(line, 110) for line in visible.splitlines()]
    insertion = next(
        index + 1 for index, line in enumerate(shifted)
        if "Rust V6 is uncommitted; no corrected candidate matching has run." in line
    )
    shifted[insertion:insertion] = [
        '<rect x="44" y="302" width="1352" height="91" rx="14" '
        'fill="#eef5ff" stroke="#b6cbee"/>',
        '<text x="65" y="337" class="warning">CORRECTED C TEST RUNNER '
        'FROZEN; C MATCHING NOT RUN</text>',
        '<text x="67" y="365" class="body">Six first-party engines are '
        'source designs, not six runnable or passing replacements. Rust and '
        'the other four have not been retested.</text>',
    ]
    image = ("\n".join(shifted) + "\n").encode("utf-8")
    for phrase in (
        b"CORRECTED C TEST RUNNER", b"C MATCHING NOT RUN",
        b"Six first-party engines", b"not six runnable",
        b"Rust", b"uncommitted", b"ZIG SCANNER CORRECTION",
        b"64 OF 1,024", b"NOT APPLIED OR TESTED", b"1,764", b"3,711",
        b"31,237", b"96 / 96", b"NOT MEASURED", b"4,194,304",
        b"NOT OPENED", b"164 / 169",
    ):
        base.need(phrase.lower() in image.lower(),
                  "reject an omitted or exaggerated C-only V41 claim: " + repr(phrase))
    for stale in (
        b"all six replacement families remain blocked until corrected v8/v10/v6",
        b"pending corrected v8/v10/v6",
        b"v7/v9 and rust v5 remain stale",
        b"freeze, commit, and push corrected v8/v10/v6 before any candidate run",
    ):
        base.need(stale not in image.lower(),
                  "reject a false inherited unfrozen V8/V10 claim: " + repr(stale))
    base.need(image.endswith(b"\n") and not image.endswith(b"\n\n"),
              "render exactly one terminal V41 SVG linefeed")
    return image


def build(previous: types.ModuleType, base: types.ModuleType,
          source_sha: str, source_bytes: int,
          archive_sha: str, receipt_sha: str,
          producer_source: str, producer_protocol: str, producer_contract: str,
          runner_source: str, worker_source: str, runner_protocol: str,
          runner_contract: str,
          ) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    base.need(RUNNER_PINS_RELEASED is True,
              "never build V41 before independently reviewed C-only runner pin release")
    source_sha = base.checked(source_sha, "actual V41 renderer")
    base.need(type(source_bytes) is int and 0 < source_bytes <= base.OWNER_LIMIT,
              "require an independently exact V41 renderer byte count")
    own_raw, _ = base.read_owner(SELF, source_sha, source_bytes, private=True)
    for observed, role in ((runner_source, "runner"), (worker_source, "worker"),
                           (runner_protocol, "protocol"),
                           (runner_contract, "contract")):
        base.need(base.checked(observed, "frozen C-only " + role) == RUNNER[role][1],
                  "reject a guessed, substituted or old C-only " + role)
    old, old_inputs = authenticate_v40(previous, base)
    frozen = base.authenticate_source_freeze()
    _, stale = base.read_owner(*base.STALE_PRODUCER, private=True)
    _, falsification = base.read_owner(*base.FALSIFICATION, private=True)
    reference = base.authenticate_reference(archive_sha, receipt_sha)
    producer = base.authenticate_producer_v4(producer_source, producer_protocol,
                                             producer_contract)
    runner = authenticate_runner(base)
    shared = base.shared_fields(reference)
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(shared)
    snapshot["corrected_candidate_producer_v4"] = copy.deepcopy(producer)
    snapshot.update(runner_fields(runner))
    validate_snapshot(previous, base, snapshot)
    earlier = {name: base.pin(*owner) for name, owner in V40.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs", "version": 41, "python": "3.14.6",
        "renderer": base.pin(SELF, source_sha, len(own_raw)),
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
        **runner_fields(runner),
    })
    inputs_raw = base.canonical(inputs)
    svg = make_svg(previous, base, snapshot, source_sha, base.digest(inputs_raw))
    families = copy.deepcopy(old["families"])
    for family in families:
        if family.get("family") == "c":
            family.update(runner_fields(runner))
            family["matching_block_reason"] = C_BLOCK_REASON
            family["candidate_run_under_corrected_reference"] = "NOT RUN"
        if family.get("family") not in ("python", "c"):
            family["corrected_runner_status"] = "NOT FROZEN"
            family["candidate_run_under_corrected_reference"] = "NOT RUN"
            family["matching_block_reason"] = (
                "Only the C V8/V10 runner is frozen; this family's corrected "
                "test runner is not frozen and matching has not run."
            )
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary", "version": 41, "status": "PASS",
        "python": "3.14.6", "source": base.pin(SELF, source_sha, len(own_raw)),
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
        **runner_fields(runner),
    })
    return snapshot, (
        (OUTPUT + ".inputs.json", inputs_raw),
        (OUTPUT + ".json", base.canonical(summary)),
        (OUTPUT + ".svg", svg),
    )


def synthetic_runner_contract(base: types.ModuleType) -> dict:
    return {
        "schema": "rebar-frozen-python-re-p0-candidate-protocol-v10",
        "version": 10,
        "case_execution_denominator": 31237,
        "suite_count": 13,
        "named_private_waiver_count": 13,
        "source_family_count": 6,
        "source_inventory_family_count": 6,
        "source_inventory_owner_count": 25,
        "six_family_inventory_is_source_only": True,
        "candidate_execution_scope": "C-ONLY; VERIFIED C15 NATIVE REQUIRED",
        "runnable_candidate_family_count": 1,
        "runnable_candidate_families": ["c"],
        "source_inventory_families": [
            {"family": family}
            for family in ("rust", "c", "zig", "cpp", "go", "fortran")
        ],
        "candidate_family": {
            "name": "c", "external_regex_engine_allowed": False,
            "shared_candidate_engine_allowed": False,
            "stdlib_engine_delegation_allowed": False,
        },
        "runner": {"path": RUNNER["runner"][0],
                    "sha256": RUNNER["runner"][1]},
        "worker": {"path": RUNNER["worker"][0],
                    "sha256": RUNNER["worker"][1]},
        "protocol": {"path": RUNNER["protocol"][0],
                      "sha256": RUNNER["protocol"][1]},
        "pinned_runtime": {
            "version": "3.14.6", "path": base.PYTHON,
            "sha256": base.PYTHON_SHA,
        },
        "phase_one": {
            "case_execution_denominator": 31237, "suite_count": 13,
            "named_private_waiver_count": 13,
        },
        "original_suites": [
            {"case_execution_count": count}
            for count in (151, 864, 1024, 768, 1024, 2854, 6912,
                          5120, 10240, 1376, 128, 264, 512)
        ],
        "corrected_candidate_context_reference": {
            "records_sha256": base.FULL_RECORDS_SHA,
            "actual_independent_reference_pids": [81, 82],
            "cache_cohort_case_count": 96,
            "cache_cohort_records_sha256": base.CACHE_RECORDS_SHA,
            "source_context_reads_reference_archive": False,
            "source_context_inflates_reference_archive": False,
            "c_pattern_equality_failure_waived": False,
        },
        "published_current_overview_v40": {
            role: {"path": owner[0], "sha256": owner[1]}
            for role, owner in V40.items()
        },
        "phase_boundary": {
            "actual_candidate_workers": 0, "actual_reference_workers": 0,
            "actual_native_activations": 0, "actual_source_builds": 0,
            "candidate_qualified_count": 0,
            "candidate_correctness": "NOT MEASURED", "hidden_cases_read": 0,
            "benchmark_files_read": 0, "clock_samples": 0,
            "timing_trials_run": 0, "holdout": "NOT OPENED",
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "winner_selected": False,
        },
    }


def synthetic_runner_proof(base: types.ModuleType) -> dict:
    owners = {
        role: base.synthetic_owner(item, 834001 + offset)
        for offset, (role, item) in enumerate(RUNNER.items())
    }
    contract = synthetic_runner_contract(base)
    validate_runner_contract(base, contract)
    proof = {
        "schema": SCHEMA + "-authenticated-c-only-runner-v10",
        "status": C_STATUS,
        **owners,
        "complete_frozen_contract": contract,
        "candidate_family": "c",
        "runnable_candidate_family_count": 1,
        "first_party_source_inventory_family_count": 6,
        "other_corrected_candidate_family_count": 5,
        "other_corrected_candidate_matching_status": "NOT RUN",
        "corrected_c_matching_status": "NOT RUN",
        "actual_candidate_workers_started": 0,
        "actual_reference_workers_started": 0,
        "actual_compiler_processes_started": 0,
        "qualified_candidate_count": 0,
        "rust_v6_runner_status": "UNCOMMITTED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }
    proof["complete_runner_binding_sha256"] = base.digest(base.canonical({
        "runner": owners["runner"], "worker": owners["worker"],
        "protocol": owners["protocol"], "contract": owners["contract"],
        "complete_frozen_contract": contract,
    }))
    validate_runner_proof(base, proof)
    return proof


def self_test(previous: types.ModuleType, base: types.ModuleType) -> dict:
    inherited = previous.self_test(base)
    base.need(
        inherited.get("status") == "PASS"
        and inherited.get("reference_archive_gzip_inflation_count") == 0
        and inherited.get("matching_archive_gzip_inflation_count") == 0,
        "exercise all exact V40 and V39 source-only effect walls before V41",
    )
    rejected = 0
    with base.SourceOnlyWall() as wall:
        fixture = base.synthetic_snapshot()
        zig_source = base.synthetic_owner(previous.ZIG["source"], 824001)
        zig_protocol = base.synthetic_owner(previous.ZIG["protocol"], 824002)
        zig_contract = base.synthetic_owner(previous.ZIG["contract"], 824003)
        zig_reference = fixture["actual_corrected_two_reference"]
        del zig_reference
        runner = synthetic_runner_proof(base)
        for field in runner_fields(runner):
            modified = copy.deepcopy(runner)
            if field in modified:
                modified[field] = base.forged(modified[field])
                try:
                    validate_runner_proof(base, modified)
                except (base.GraphError, TypeError, ValueError, KeyError, AttributeError):
                    rejected += 1
                else:
                    raise base.GraphError("accept a fabricated C-only runner field: " + field)
        for field, value in runner.items():
            modified = copy.deepcopy(runner)
            modified[field] = base.forged(value)
            try:
                validate_runner_proof(base, modified)
            except (base.GraphError, TypeError, ValueError, KeyError, AttributeError):
                rejected += 1
            else:
                raise base.GraphError("accept a fabricated C-only runner proof: " + field)
        for role in ("runner", "worker", "protocol", "contract"):
            for field, value in runner[role].items():
                modified = copy.deepcopy(runner)
                modified[role][field] = base.forged(value)
                try:
                    validate_runner_proof(base, modified)
                except (base.GraphError, TypeError, ValueError, KeyError, AttributeError):
                    rejected += 1
                else:
                    raise base.GraphError("accept a forged C-only runner owner: " + role)
        actual = runner["complete_frozen_contract"]
        for field, value in actual.items():
            modified = copy.deepcopy(runner)
            modified["complete_frozen_contract"][field] = base.forged(value)
            try:
                validate_runner_proof(base, modified)
            except (base.GraphError, TypeError, ValueError, KeyError, AttributeError):
                rejected += 1
            else:
                raise base.GraphError("accept forged C-only contract: " + field)
        for group in ("candidate_family", "runner", "worker", "protocol",
                      "pinned_runtime", "phase_one", "phase_boundary",
                      "corrected_candidate_context_reference"):
            for field, value in actual[group].items():
                modified = copy.deepcopy(runner)
                modified["complete_frozen_contract"][group][field] = base.forged(value)
                try:
                    validate_runner_proof(base, modified)
                except (base.GraphError, TypeError, ValueError, KeyError, AttributeError):
                    rejected += 1
                else:
                    raise base.GraphError("accept forged C-only contract " + group)
        probes = (
            ("filesystem", lambda: builtins.open("forbidden-v41")),
            ("filesystem", lambda: os.open("forbidden-v41", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v41")),
            ("write", lambda: os.mkdir("forbidden-v41")),
            ("process", lambda: subprocess.run(("forbidden-v41",))),
            ("process", lambda: subprocess.Popen(("forbidden-v41",))),
            ("process", lambda: os.execv("/forbidden-v41", [])),
        )
        for kind, action in probes:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(wall.blocked[kind] == before + 1,
                          "physically block the exact C-only V41 effect: " + kind)
            else:
                raise base.GraphError("a genuine V41 source-only side effect escaped")
        base.need(rejected >= 65, "reject every forged C-only family and runner owner")
        return {
            "schema": SCHEMA + "-source-only-self-test", "version": 41,
            "status": "PASS", "synthetic_only": True,
            "previous_v40_hostile_controls": inherited["rejected_hostile_control_count"],
            "c_only_runner_hostile_controls": rejected,
            "rejected_hostile_control_count":
                inherited["rejected_hostile_control_count"] + rejected,
            "previous_v40_blocked_effects_by_kind":
                inherited["previous_v39_blocked_effects_by_kind"],
            "blocked_effects_by_kind": dict(wall.blocked),
            "full_case_denominator": 31237, "suite_count": 13,
            "private_waiver_count": 13,
            "corrected_c_only_runner_status": C_STATUS,
            "corrected_c_only_runner_family": "c",
            "corrected_c_only_runnable_family_count": 1,
            "first_party_source_inventory_family_count": 6,
            "other_corrected_candidate_family_count": 5,
            "other_corrected_candidate_matching_status": "NOT RUN",
            "corrected_c_matching_status": "NOT RUN",
            "rust_v6_runner_status": "UNCOMMITTED",
            "corrected_c_candidate_workers_started": 0,
            "corrected_c_candidate_qualified": False,
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
    base.need(RUNNER_PINS_RELEASED is True and path in allowed
              and type(raw) is bytes and 0 < len(raw) <= base.OWNER_LIMIT,
              "publish only authorized V41 output after independently reviewed pins")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0,
                      "reject an incomplete private V41 graph owner")
            remaining = remaining[count:]
        os.fsync(handle)
        owner = os.fstat(handle)
        base.need(owner.st_uid == os.geteuid() and owner.st_nlink == 1
                  and owner.st_size == len(raw)
                  and stat.S_IMODE(owner.st_mode) == 0o600,
                  "require a durable owner-only exclusive V41 graph owner")
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
    base.need(observed == raw, "authenticate every durable final V41 output byte")


def result(base: types.ModuleType, source: str, outputs: dict[str, bytes],
           written: bool, suffix: str) -> dict:
    return {
        "schema": SCHEMA + suffix, "version": 41, "status": "PASS",
        "source_sha256": source,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 40,
        "previous_overview_source_sha256": V40["source"][1],
        "previous_overview_inputs_sha256": V40["inputs"][1],
        "previous_overview_summary_sha256": V40["summary"][1],
        "previous_overview_svg_sha256": V40["svg"][1],
        "corrected_c_only_runner_source_sha256": RUNNER["runner"][1],
        "corrected_c_only_worker_source_sha256": RUNNER["worker"][1],
        "corrected_c_only_protocol_sha256": RUNNER["protocol"][1],
        "corrected_c_only_contract_sha256": RUNNER["contract"][1],
        "corrected_c_only_runner_status": C_STATUS,
        "corrected_c_only_runner_family": "c",
        "corrected_c_only_runnable_family_count": 1,
        "first_party_source_inventory_family_count": 6,
        "other_corrected_candidate_family_count": 5,
        "other_corrected_candidate_matching_status": "NOT RUN",
        "corrected_c_matching_status": "NOT RUN",
        "corrected_c_candidate_workers_started": 0,
        "corrected_c_candidate_qualified": False,
        "all_candidate_matching_blocked": True,
        "candidate_matching_block_reason": C_BLOCK_REASON,
        "candidate_case_producer_status":
            "V4 SOURCE FROZEN; C-ONLY V8/V10 RUNNER FROZEN; C MATCHING NOT RUN",
        "historical_stale_candidate_worker_versions": ["V7", "V9", "RUST V5"],
        "stale_candidate_worker_versions": ["RUST V5"],
        "required_corrected_candidate_runner_versions": ["RUST V6"],
        "pending_corrected_candidate_families":
            ["rust", "zig", "cpp", "go", "fortran"],
        "rust_v6_runner_status": "UNCOMMITTED",
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
        "qualified_candidate_count": 0,
        "historical_rust_semantic_mismatch_count": 1036,
        "historical_c_semantic_mismatch_count": 1230,
        "historical_zig_semantic_mismatch_count": 1764,
        "historical_zig_verified_passing_case_count": 3711,
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
    parser.add_argument("--runner-source-sha256")
    parser.add_argument("--worker-source-sha256")
    parser.add_argument("--runner-protocol-sha256")
    parser.add_argument("--runner-contract-sha256")
    for name in ("inputs", "summary", "svg"):
        parser.add_argument("--" + name + "-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, base = load_v40()
        if options.self_test:
            base.need(all(getattr(options, key) is None for key in (
                "source_sha256", "source_bytes", "archive_sha256", "receipt_sha256",
                "producer_source_sha256", "producer_protocol_sha256",
                "producer_contract_sha256", "runner_source_sha256",
                "worker_source_sha256", "runner_protocol_sha256",
                "runner_contract_sha256", "inputs_sha256",
                "summary_sha256", "svg_sha256",
            )), "source-only tests may not accept archives, runner evidence or hidden outputs")
            sys.stdout.buffer.write(base.canonical(self_test(previous, base)))
            return 0
        base.need(RUNNER_PINS_RELEASED is True,
                  "refuse V41 rendering or context until reviewed C-only runner pins are released")
        source = base.checked(options.source_sha256, "exact final V41 graph source")
        archive = base.checked(options.archive_sha256, "actual corrected Python reference archive")
        receipt = base.checked(options.receipt_sha256, "actual corrected reference receipt")
        producer_source = base.checked(options.producer_source_sha256, "corrected V4 source")
        producer_protocol = base.checked(options.producer_protocol_sha256,
                                         "corrected V4 protocol")
        producer_contract = base.checked(options.producer_contract_sha256,
                                         "corrected V4 contract")
        runner = base.checked(options.runner_source_sha256, "reviewed C-only V10 runner")
        worker = base.checked(options.worker_source_sha256, "reviewed C-only V8 worker")
        protocol = base.checked(options.runner_protocol_sha256,
                                "reviewed C-only V10 protocol")
        contract = base.checked(options.runner_contract_sha256,
                                "reviewed C-only V10 contract")
        _snapshot, pairs = build(previous, base, source, options.source_bytes,
                                 archive, receipt, producer_source, producer_protocol,
                                 producer_contract, runner, worker, protocol, contract)
        outputs = dict(pairs)
        if options.render:
            base.need(options.inputs_sha256 is None
                      and options.summary_sha256 is None
                      and options.svg_sha256 is None,
                      "render only three exact, newly and exclusively authorized V41 outputs")
            for path, raw in pairs:
                publish(base, path, raw)
            sys.stdout.buffer.write(base.canonical(result(base, source, outputs,
                                                         True, "-published")))
            return 0
        expected = {
            OUTPUT + ".inputs.json": base.checked(options.inputs_sha256,
                                                  "frozen V41 graph inputs"),
            OUTPUT + ".json": base.checked(options.summary_sha256,
                                            "frozen V41 graph summary"),
            OUTPUT + ".svg": base.checked(options.svg_sha256,
                                           "frozen V41 graph image"),
        }
        for path, fingerprint in expected.items():
            observed, _ = base.read_owner(path, fingerprint, len(outputs[path]),
                                          private=True)
            base.need(observed == outputs[path],
                      "independently reproduce every complete frozen V41 output")
        sys.stdout.buffer.write(base.canonical(result(base, source, outputs, False,
                                                      "-read-only-frozen-context")))
        return 0
    except (ValueError, OSError, TypeError, EOFError, KeyError, AttributeError,
            RecursionError) as error:
        sys.stderr.write("current V41 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V41 overview rejected: " + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
