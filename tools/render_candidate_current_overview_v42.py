#!/usr/bin/env python3
"""Show separate frozen C and Rust test runners without inventing a result."""

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
SELF = "tools/render_candidate_current_overview_v42.py"
OUTPUT = "docs/evidence/candidate-current-overview-v42"
SCHEMA = "rebar-candidate-current-overview-v42"
V41 = {
    "source": (
        "tools/render_candidate_current_overview_v41.py",
        "c0ab9b19acd895a122a171ca1d9df9010de0ec732b81b0f52f29b96cbc88f87a",
        50242,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v41.inputs.json",
        "3abaa207a8d25f03c59bd9f7443dcd0bfb5fd6934c7f1fa388e2abf636893fc4",
        235674,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v41.json",
        "e2835917d55d654a6d4c167298737c51f5f3b299ab7e2bc2c2eba60f9bff4f9f",
        675118,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v41.svg",
        "882e8ddb4e233a1c569c0330bbbf618f65f54bcf3d0bb59dc1c99542677dd2b7",
        12401,
    ),
}

# All three exact first-party Rust owners were independently reviewed and
# explicitly released by the experiment owner before rendering was enabled.
RUST_PINS_RELEASED = True
RUST = {
    "source": (
        "tools/run_owned_repaired_rust_original_campaign_v6.py",
        "c25cbdf3674fc3e054c388e53de3ed38d4b1dab0a820808c42848e1803909f5e",
        374429,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V6.md",
        "ddc5c212d3e188bc1d1cdde992bf872a38962e64d3b07d6ec7c275ba4f55f13c",
        8551,
    ),
    "contract": (
        "oracle/phase2/repaired-rust-original-campaign-v6.json",
        "ce044f18be388ab0608d0bd3bb68751e6970973f8e6ef758971e75e6d6b584a5",
        33386,
    ),
}
RUST_STATUS = "RUST-ONLY RUNNER SOURCE FROZEN; CORRECTED RUST MATCHING NOT RUN"
DUAL_STATUS = (
    "V4 SOURCE FROZEN; SEPARATE C-ONLY V8/V10 AND RUST-ONLY V6 "
    "RUNNERS FROZEN; BOTH MATCHING NOT RUN"
)
DUAL_BLOCK_REASON = (
    "Separate first-party C-only V8/V10 and Rust-only V6 runner sources "
    "are frozen. Neither 31,237-case corrected candidate campaign has "
    "been authorized or executed. Zig, C++, Go and Fortran remain "
    "source-only designs without a frozen corrected test runner."
)


def load_v41() -> tuple[types.ModuleType, types.ModuleType, types.ModuleType]:
    path, fingerprint, size = V41["source"]
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
            raise ValueError("reject the nonprivate, substituted or truncated V41 renderer")
        remaining = size
        parts: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(262144, remaining))
            if not chunk:
                raise ValueError("reject incomplete independently pushed V41 source")
            parts.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise ValueError("reject appended bytes after the authentic V41 renderer")
        raw = b"".join(parts)
        after = os.fstat(descriptor)
        if (
            hashlib.sha256(raw).hexdigest() != fingerprint
            or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        ):
            raise ValueError("reject V41 renderer changes during authentication")
    finally:
        os.close(descriptor)
    previous = types.ModuleType("_rebar_exact_pushed_v41_for_independent_rust_v42")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    middle, base = previous.load_v40()
    base.need(previous.SCHEMA == "rebar-candidate-current-overview-v41"
              and previous.SELF == path,
              "load only the exact independently committed V41 corrected C graph")
    return previous, middle, base


def authenticate_v41(previous: types.ModuleType, middle: types.ModuleType,
                     base: types.ModuleType) -> tuple[dict, dict]:
    for owner in V41.values():
        base.read_owner(*owner, private=True)
    inputs_raw, _ = base.read_owner(*V41["inputs"], private=True)
    summary_raw, _ = base.read_owner(*V41["summary"], private=True)
    svg_raw, _ = base.read_owner(*V41["svg"], private=True)
    inputs = base.document(inputs_raw, "complete independently pushed V41 inputs")
    summary = base.document(summary_raw, "complete independently pushed V41 summary")
    snapshot = summary.get("snapshot")
    previous.validate_snapshot(middle, base, snapshot)
    base.need(
        summary.get("schema") == "rebar-candidate-current-overview-v41-summary"
        and summary.get("version") == 41 and summary.get("status") == "PASS"
        and summary.get("source") == base.pin(*V41["source"])
        and summary.get("inputs") == base.pin(*V41["inputs"])
        and summary.get("svg") == base.pin(*V41["svg"])
        and inputs.get("schema") == "rebar-candidate-current-overview-v41-inputs"
        and inputs.get("version") == 41
        and inputs.get("renderer") == base.pin(*V41["source"])
        and svg_raw == previous.make_svg(
            middle, base, snapshot, V41["source"][1], V41["inputs"][1],
        ),
        "reproduce all four complete, true C-only V41 history owners",
    )
    return summary, inputs


def validate_rust_contract(base: types.ModuleType, document: object) -> None:
    base.need(type(document) is dict, "reject a missing exact Rust-only V6 freeze")
    assert isinstance(document, dict)
    status = document.get("status")
    base.need(
        type(document.get("schema")) is str
        and "repaired-rust-original-campaign-v6" in document["schema"]
        and document.get("version") == 6
        and document.get("family") == "rust"
        and type(status) is str and "SOURCE FROZEN" in status
        and "NOT RUN" in status
        and document.get("source")
        == {"path": RUST["source"][0], "sha256": RUST["source"][1]}
        and document.get("protocol")
        == {"path": RUST["protocol"][0], "sha256": RUST["protocol"][1]},
        "bind the actual separately owned Rust-only source, protocol and NOT RUN status",
    )
    python = document.get("pinned_cpython")
    original = document.get("original_oracle")
    effects = document.get("source_only_effects")
    base.need(
        type(python) is dict and python.get("version") == "3.14.6"
        and python.get("path") == base.PYTHON
        and python.get("sha256") == base.PYTHON_SHA
        and type(original) is dict
        and original.get("case_execution_denominator") == 31237
        and original.get("suite_count") == 13
        and original.get("named_private_waiver_count") == 13
        and original.get("candidate_wrapper_allowed") is False
        and original.get("cross_family_matching_allowed") is False
        and original.get("external_regex_dependency_allowed") is False
        and original.get("stdlib_re_fallback_allowed") is False,
        "bind Rust to its first-party engine and all original 31,237 obligations",
    )
    suites = original.get("source_ordered_suites")
    base.need(type(suites) is list and len(suites) == 13
              and all(type(row) is dict
                      and type(row.get("case_execution_count")) is int
                      and row["case_execution_count"] > 0
                      for row in suites)
              and sum(row["case_execution_count"] for row in suites) == 31237,
              "retain all 13 real source-ordered original correctness groups")
    base.need(
        type(effects) is dict
        and all(type(effects.get(name)) is int and effects[name] == 0 for name in (
            "actual_candidate_imports", "actual_candidate_workers",
            "actual_native_activations", "actual_native_library_loads",
            "actual_reference_workers", "actual_source_builds",
            "benchmark_files_read", "canonical_target_reads",
            "canonical_target_replacements", "canonical_target_stats",
            "clock_samples", "hidden_cases_read", "threads_started",
            "timing_trials_run", "workspace_mutations",
        ))
        and effects.get("candidate_correctness") == "NOT MEASURED"
        and effects.get("candidate_qualified") is False
        and effects.get("holdout") == "NOT OPENED"
        and effects.get("performance") == "NOT MEASURED"
        and effects.get("memory") == "NOT MEASURED"
        and effects.get("undefined_behavior") == "NOT MEASURED"
        and effects.get("winner_selected") is False,
        "a Rust source freeze cannot run, qualify, build or measure any candidate",
    )


def validate_rust_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict, "reject missing exact Rust-only source evidence")
    assert isinstance(proof, dict)
    base.need(
        proof.get("schema") == SCHEMA + "-authenticated-rust-only-original-runner-v6"
        and proof.get("status") == RUST_STATUS
        and proof.get("candidate_family") == "rust"
        and proof.get("runnable_candidate_family_count") == 1
        and proof.get("source_family_inventory_only") is True
        and proof.get("corrected_rust_matching_status") == "NOT RUN"
        and proof.get("actual_candidate_workers_started") == 0
        and proof.get("actual_reference_workers_started") == 0
        and proof.get("actual_compiler_processes_started") == 0
        and proof.get("candidate_qualified") is False
        and proof.get("performance") == "NOT MEASURED"
        and proof.get("memory") == "NOT MEASURED"
        and proof.get("holdout") == "NOT OPENED",
        "reject a fabricated six-family, executed, passing or faster Rust runner",
    )
    for role, expected in RUST.items():
        owner = proof.get(role)
        base.need(
            type(owner) is dict and owner.get("path") == expected[0]
            and owner.get("sha256") == expected[1]
            and owner.get("bytes") == expected[2]
            and owner.get("mode") == "0600"
            and owner.get("nlink") == 1
            and type(owner.get("inode")) is int and owner["inode"] > 0,
            "authenticate the complete genuine Rust-only " + role + " owner",
        )
    contract = proof.get("complete_frozen_contract")
    validate_rust_contract(base, contract)
    binding = base.digest(base.canonical({
        "source": proof["source"], "protocol": proof["protocol"],
        "contract": proof["contract"], "complete_frozen_contract": contract,
    }))
    base.need(proof.get("complete_rust_binding_sha256") == binding,
              "bind every complete Rust-only source, protocol and contract byte")


def authenticate_rust(base: types.ModuleType) -> dict:
    base.need(RUST_PINS_RELEASED is True,
              "refuse Rust evidence until three independently reviewed exact pins are released")
    owners: dict[str, dict] = {}
    contract_raw = b""
    for role, expected in RUST.items():
        raw, owner = base.read_owner(*expected, private=True)
        owners[role] = owner
        if role == "contract":
            contract_raw = raw
    contract = base.document(contract_raw, "complete exact Rust V6 source-only contract")
    validate_rust_contract(base, contract)
    proof = {
        "schema": SCHEMA + "-authenticated-rust-only-original-runner-v6",
        "status": RUST_STATUS,
        **owners,
        "complete_frozen_contract": contract,
        "candidate_family": "rust",
        "runnable_candidate_family_count": 1,
        "source_family_inventory_only": True,
        "corrected_rust_matching_status": "NOT RUN",
        "actual_candidate_workers_started": 0,
        "actual_reference_workers_started": 0,
        "actual_compiler_processes_started": 0,
        "candidate_qualified": False,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }
    proof["complete_rust_binding_sha256"] = base.digest(base.canonical({
        "source": owners["source"], "protocol": owners["protocol"],
        "contract": owners["contract"], "complete_frozen_contract": contract,
    }))
    validate_rust_proof(base, proof)
    return proof


def dual_runner_fields(rust: dict) -> dict:
    return {
        "corrected_rust_only_runner_v6": copy.deepcopy(rust),
        "corrected_rust_only_runner_status": RUST_STATUS,
        "corrected_rust_only_runner_family": "rust",
        "corrected_rust_only_runner_source_sha256": RUST["source"][1],
        "corrected_rust_only_runner_protocol_sha256": RUST["protocol"][1],
        "corrected_rust_only_runner_contract_sha256": RUST["contract"][1],
        "corrected_rust_matching_status": "NOT RUN",
        "corrected_rust_candidate_workers_started": 0,
        "corrected_rust_candidate_qualified": False,
        "corrected_rust_matching_mismatch_reduction": "NOT MEASURED",
        "corrected_rust_matching_speedup": "NOT MEASURED",
        "corrected_c_matching_status": "NOT RUN",
        "corrected_c_candidate_workers_started": 0,
        "corrected_c_candidate_qualified": False,
        "dedicated_corrected_runnable_family_count": 2,
        "dedicated_corrected_runnable_families": ["c", "rust"],
        "first_party_source_inventory_family_count": 6,
        "other_corrected_candidate_family_count": 4,
        "other_corrected_candidate_matching_status": "NOT RUN",
        "pending_corrected_candidate_families": ["zig", "cpp", "go", "fortran"],
        "candidate_case_producer_status": DUAL_STATUS,
        "candidate_matching_block_reason": DUAL_BLOCK_REASON,
        "all_candidate_matching_blocked": True,
        "qualified_candidate_count": 0,
        "rust_v6_runner_status": "SOURCE FROZEN; CORRECTED RUST MATCHING NOT RUN",
        "required_corrected_candidate_runner_versions": [],
        "stale_candidate_worker_versions": [],
        "historical_stale_candidate_worker_versions": ["V7", "V9", "RUST V5"],
    }


def project_v41_snapshot(previous: types.ModuleType, base: types.ModuleType,
                         snapshot: dict) -> dict:
    historical = copy.deepcopy(snapshot)
    proof = snapshot.get("corrected_c_only_runner_v10")
    previous.validate_runner_proof(base, proof)
    assert isinstance(proof, dict)
    old = previous.runner_fields(proof)
    for field in (
        "candidate_matching_block_reason", "candidate_case_producer_status",
        "other_corrected_candidate_family_count",
        "other_corrected_candidate_matching_status",
        "pending_corrected_candidate_families", "rust_v6_runner_status",
        "required_corrected_candidate_runner_versions",
        "stale_candidate_worker_versions",
    ):
        historical[field] = old[field]
    return historical


def validate_snapshot(previous: types.ModuleType, middle: types.ModuleType,
                      base: types.ModuleType, snapshot: object) -> None:
    base.need(type(snapshot) is dict, "reject a missing two-runner V42 snapshot")
    assert isinstance(snapshot, dict)
    previous.validate_snapshot(middle, base,
                               project_v41_snapshot(previous, base, snapshot))
    rust = snapshot.get("corrected_rust_only_runner_v6")
    validate_rust_proof(base, rust)
    assert isinstance(rust, dict)
    for key, expected in dual_runner_fields(rust).items():
        base.need(snapshot.get(key) == expected,
                  "reject a forged current C/Rust runner policy: " + key)
    base.need(
        snapshot.get("corrected_c_only_runner_family") == "c"
        and snapshot.get("corrected_c_only_runnable_family_count") == 1
        and snapshot.get("zig_scanner_phrase_prospective_case_count") == 64
        and snapshot.get("zig_scanner_phrase_correction_applied") is False
        and snapshot.get("zig_scanner_phrase_corrected_matching_status") == "NOT RUN"
        and snapshot.get("performance") == "NOT MEASURED"
        and snapshot.get("memory") == "NOT MEASURED"
        and snapshot.get("final_holdout_opened") is False
        and snapshot.get("winner_selected") is False,
        "keep C and Rust separate, the Zig feature unapplied and all results unmeasured",
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
    value = int(line[start:end])
    if value < 302:
        return line
    return line[:start] + str(value + shift) + line[end:]


def make_svg(previous: types.ModuleType, middle: types.ModuleType,
             base: types.ModuleType, snapshot: dict,
             source: str, inputs: str) -> bytes:
    validate_snapshot(previous, middle, base, snapshot)
    historical = project_v41_snapshot(previous, base, snapshot)
    visible = previous.make_svg(middle, base, historical, source, inputs).decode("utf-8")
    visible = visible.replace('height="2150" viewBox="0 0 1440 2150"',
                              'height="2260" viewBox="0 0 1440 2260"', 1)
    visible = visible.replace("v41-title", "v42-title")
    visible = visible.replace("v41-description", "v42-description")
    visible = visible.replace(
        "baseline passes; corrected C test runner is frozen, untested</title>",
        "baseline passes; separate C and Rust runners are frozen, untested</title>",
        1,
    )
    visible = visible.replace(
        "The corrected C-only V8/V10 runner is frozen, but C matching has "
        "not been run. Rust V6 is uncommitted and the other five first-party "
        "source designs do not yet have corrected runners.",
        "Separate C-only V8/V10 and Rust-only V6 runners are source frozen. "
        "Neither complete candidate test has been run; Zig, Go, C++ and "
        "Fortran remain source-only designs.",
        1,
    )
    visible = visible.replace(
        "Six first-party source designs; only the corrected C test runner is frozen.",
        "Six first-party source designs; separate C and Rust test runners are frozen, not tested.",
        1,
    )
    visible = visible.replace(
        "replacement families</text>",
        "first-party source designs</text>",
        1,
    )
    visible = visible.replace(
        "NO CORRECTED C MATCHING HAS RUN — FIVE OTHER RUNNERS ARE NOT FROZEN",
        "C AND RUST RUNNERS FROZEN — NEITHER COMPLETE MATCHING TEST HAS RUN",
        1,
    )
    visible = visible.replace(
        "One corrected C test runner is frozen. Rust V6 is uncommitted; "
        "no corrected candidate matching has run.",
        "C and Rust each have a separately frozen first-party test runner; "
        "neither 31,237-case matching campaign has run.",
        1,
    )
    visible = visible.replace(
        "Six first-party engines are source designs, not six runnable or "
        "passing replacements. Rust and the other four have not been retested.",
        "Six first-party engines are source designs, not six runnable or "
        "passing replacements. The separate C and Rust runners have not been used.",
        1,
    )
    visible = visible.replace(
        "V4 and the C-only V8/V10 runner are frozen; Rust V6 is uncommitted.",
        "V4 plus separate C-only V8/V10 and Rust-only V6 runner sources are frozen.",
        1,
    )
    visible = visible.replace(
        "Replacement test runner</text>",
        "Separate replacement test runners</text>",
        1,
    )
    visible = visible.replace(
        "C matching NOT RUN; Rust, Zig, Go, C++ and Fortran runners are NOT FROZEN.",
        "C and Rust matching NOT RUN; Zig, Go, C++ and Fortran runners NOT FROZEN.",
        1,
    )
    shifted = [move_y(line, 110) for line in visible.splitlines()]
    insertion = next(
        index + 1 for index, line in enumerate(shifted)
        if "neither 31,237-case matching campaign has run." in line
    )
    shifted[insertion:insertion] = [
        '<rect x="44" y="302" width="1352" height="91" rx="14" '
        'fill="#eef5ff" stroke="#b6cbee"/>',
        '<text x="65" y="337" class="warning">SEPARATE C AND RUST TEST '
        'RUNNERS FROZEN; BOTH FULL MATCHING CAMPAIGNS NOT RUN</text>',
        '<text x="67" y="365" class="body">Two dedicated first-party '
        'runner paths; six source designs; zero qualified replacements. '
        'No compatibility or speed result has been measured.</text>',
    ]
    image = ("\n".join(shifted) + "\n").encode("utf-8")
    for phrase in (
        b"SEPARATE C AND RUST TEST", b"RUNNERS FROZEN",
        b"BOTH FULL MATCHING CAMPAIGNS NOT RUN",
        b"Two dedicated first-party", b"six source designs",
        b"first-party source designs</text>",
        b"Separate replacement test runners</text>",
        b"zero qualified", b"C MATCHING NOT RUN", b"RUST MATCHING NOT RUN",
        b"ZIG SCANNER CORRECTION", b"64 OF 1,024",
        b"NOT APPLIED OR TESTED", b"1,764", b"3,711",
        b"31,237", b"96 / 96", b"NOT MEASURED",
        b"4,194,304", b"NOT OPENED", b"164 / 169",
    ):
        base.need(phrase.lower() in image.lower(),
                  "reject an omitted honest V42 status: " + repr(phrase))
    for stale in (
        b"rust v6 is uncommitted",
        b"only the corrected c test runner is frozen",
        b"five other runners are not frozen",
        b"rust and the other four have not been retested",
        b"all six replacement families remain blocked until corrected v8/v10/v6",
        b"pending corrected v8/v10/v6",
        b"v7/v9 and rust v5 remain stale",
    ):
        base.need(stale not in image.lower(),
                  "reject a stale inherited C-only or six-family V42 claim")
    base.need(image.endswith(b"\n") and not image.endswith(b"\n\n"),
              "render exactly one terminal V42 image linefeed")
    return image


def build(previous: types.ModuleType, middle: types.ModuleType,
          base: types.ModuleType, source_sha: str, source_bytes: int,
          archive_sha: str, receipt_sha: str,
          producer_source: str, producer_protocol: str, producer_contract: str,
          c_runner: str, c_worker: str, c_protocol: str, c_contract: str,
          rust_source: str, rust_protocol: str, rust_contract: str,
          ) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    base.need(RUST_PINS_RELEASED is True,
              "refuse V42 rendering until independently reviewed Rust-only V6 pins")
    source_sha = base.checked(source_sha, "exact V42 graph renderer")
    base.need(type(source_bytes) is int and 0 < source_bytes <= base.OWNER_LIMIT,
              "require independently supplied complete V42 source bytes")
    own_raw, _ = base.read_owner(SELF, source_sha, source_bytes, private=True)
    for observed, role in ((c_runner, "runner"), (c_worker, "worker"),
                           (c_protocol, "protocol"), (c_contract, "contract")):
        base.need(base.checked(observed, "genuine C-only " + role)
                  == previous.RUNNER[role][1],
                  "reject a substituted previously published C-only " + role)
    for observed, role in ((rust_source, "source"),
                           (rust_protocol, "protocol"),
                           (rust_contract, "contract")):
        base.need(base.checked(observed, "released Rust-only " + role)
                  == RUST[role][1],
                  "reject guessed or substituted Rust-only " + role + " evidence")
    old, old_inputs = authenticate_v41(previous, middle, base)
    frozen = base.authenticate_source_freeze()
    _, stale = base.read_owner(*base.STALE_PRODUCER, private=True)
    _, falsification = base.read_owner(*base.FALSIFICATION, private=True)
    reference = base.authenticate_reference(archive_sha, receipt_sha)
    producer = base.authenticate_producer_v4(producer_source, producer_protocol,
                                             producer_contract)
    rust = authenticate_rust(base)
    c_proof = old["snapshot"].get("corrected_c_only_runner_v10")
    previous.validate_runner_proof(base, c_proof)
    shared = base.shared_fields(reference)
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(shared)
    snapshot["corrected_candidate_producer_v4"] = copy.deepcopy(producer)
    snapshot.update(previous.runner_fields(c_proof))
    snapshot.update(dual_runner_fields(rust))
    validate_snapshot(previous, middle, base, snapshot)
    earlier = {role: base.pin(*owner) for role, owner in V41.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs", "version": 42, "python": "3.14.6",
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
        **previous.runner_fields(c_proof),
        **dual_runner_fields(rust),
    })
    inputs_raw = base.canonical(inputs)
    svg = make_svg(previous, middle, base, snapshot,
                   source_sha, base.digest(inputs_raw))
    families = copy.deepcopy(old["families"])
    dual = dual_runner_fields(rust)
    current_family_policy = {
        field: copy.deepcopy(dual[field])
        for field in (
            "corrected_c_matching_status",
            "corrected_rust_matching_status",
            "dedicated_corrected_runnable_family_count",
            "dedicated_corrected_runnable_families",
            "first_party_source_inventory_family_count",
            "other_corrected_candidate_family_count",
            "other_corrected_candidate_matching_status",
            "pending_corrected_candidate_families",
            "candidate_case_producer_status",
            "candidate_matching_block_reason",
            "all_candidate_matching_blocked",
            "qualified_candidate_count",
            "rust_v6_runner_status",
            "required_corrected_candidate_runner_versions",
            "stale_candidate_worker_versions",
            "historical_stale_candidate_worker_versions",
        )
    }
    for family in families:
        name = family.get("family")
        if name == "python":
            continue
        if name == "c":
            family.update(previous.runner_fields(c_proof))
        family.update(current_family_policy)
        family.update({
            "matching_blocked_pending_corrected_v4_producer": False,
            "matching_paused_for_reference_falsification": False,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
        })
        if name == "c":
            family.update({
                "corrected_runner_status":
                    "C-ONLY V8/V10 SOURCE FROZEN; CORRECTED C MATCHING NOT RUN",
                "matching_block_reason": DUAL_BLOCK_REASON,
                "matching_blocked_pending_corrected_candidate_runners": False,
                "candidate_run_under_corrected_reference": "NOT RUN",
                "qualified": False,
            })
        elif name == "rust":
            family.update({
                "corrected_rust_only_runner_v6": copy.deepcopy(rust),
                "corrected_runner_status": RUST_STATUS,
                "matching_block_reason": DUAL_BLOCK_REASON,
                "matching_blocked_pending_corrected_candidate_runners": False,
                "candidate_run_under_corrected_reference": "NOT RUN",
                "qualified": False,
            })
        else:
            family.update({
                "corrected_runner_status": "NOT FROZEN",
                "matching_block_reason":
                    "Only separate C and Rust runners are frozen; this first-party "
                    "engine remains a source-only design and matching has not run.",
                "matching_blocked_pending_corrected_candidate_runners": True,
                "candidate_run_under_corrected_reference": "NOT RUN",
                "qualified": False,
            })
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary", "version": 42, "status": "PASS",
        "python": "3.14.6", "source": base.pin(SELF, source_sha, len(own_raw)),
        "inputs": base.pin(OUTPUT + ".inputs.json", base.digest(inputs_raw),
                           len(inputs_raw)),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg), len(svg)),
        "previous_overview": earlier,
        "snapshot": snapshot,
        "families": families,
        "corrected_reference_source_freeze": frozen,
        "corrected_candidate_producer_v4": copy.deepcopy(producer),
        "preserved_actual_reference_falsification": falsification,
        "stale_original_candidate_producer": stale,
        "authenticated_digest_addressed_history_paths": 169,
        "qualified_candidate_count": 0,
        **shared,
        **previous.runner_fields(c_proof),
        **dual_runner_fields(rust),
    })
    return snapshot, (
        (OUTPUT + ".inputs.json", inputs_raw),
        (OUTPUT + ".json", base.canonical(summary)),
        (OUTPUT + ".svg", svg),
    )


def synthetic_rust_contract(base: types.ModuleType) -> dict:
    return {
        "schema": "rebar-owned-repaired-rust-original-campaign-v6-source-freeze",
        "version": 6, "family": "rust",
        "status": "SOURCE FROZEN; CORRECTED RUST CANDIDATE NOT RUN",
        "source": {"path": RUST["source"][0], "sha256": RUST["source"][1]},
        "protocol": {"path": RUST["protocol"][0], "sha256": RUST["protocol"][1]},
        "pinned_cpython": {"version": "3.14.6", "path": base.PYTHON,
                           "sha256": base.PYTHON_SHA},
        "original_oracle": {
            "case_execution_denominator": 31237, "suite_count": 13,
            "named_private_waiver_count": 13,
            "candidate_wrapper_allowed": False,
            "cross_family_matching_allowed": False,
            "external_regex_dependency_allowed": False,
            "stdlib_re_fallback_allowed": False,
            "source_ordered_suites": [
                {"case_execution_count": count}
                for count in (151, 864, 1024, 768, 1024, 2854, 6912,
                              5120, 10240, 1376, 128, 264, 512)
            ],
        },
        "source_only_effects": {
            **{name: 0 for name in (
                "actual_candidate_imports", "actual_candidate_workers",
                "actual_native_activations", "actual_native_library_loads",
                "actual_reference_workers", "actual_source_builds",
                "benchmark_files_read", "canonical_target_reads",
                "canonical_target_replacements", "canonical_target_stats",
                "clock_samples", "hidden_cases_read", "threads_started",
                "timing_trials_run", "workspace_mutations",
            )},
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False,
            "holdout": "NOT OPENED", "performance": "NOT MEASURED",
            "memory": "NOT MEASURED", "undefined_behavior": "NOT MEASURED",
            "winner_selected": False,
        },
    }


def synthetic_rust_proof(base: types.ModuleType) -> dict:
    owners = {
        role: base.synthetic_owner(value, 844001 + index)
        for index, (role, value) in enumerate(RUST.items())
    }
    contract = synthetic_rust_contract(base)
    validate_rust_contract(base, contract)
    proof = {
        "schema": SCHEMA + "-authenticated-rust-only-original-runner-v6",
        "status": RUST_STATUS,
        **owners,
        "complete_frozen_contract": contract,
        "candidate_family": "rust",
        "runnable_candidate_family_count": 1,
        "source_family_inventory_only": True,
        "corrected_rust_matching_status": "NOT RUN",
        "actual_candidate_workers_started": 0,
        "actual_reference_workers_started": 0,
        "actual_compiler_processes_started": 0,
        "candidate_qualified": False,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }
    proof["complete_rust_binding_sha256"] = base.digest(base.canonical({
        "source": owners["source"], "protocol": owners["protocol"],
        "contract": owners["contract"], "complete_frozen_contract": contract,
    }))
    validate_rust_proof(base, proof)
    return proof


def self_test(previous: types.ModuleType, middle: types.ModuleType,
              base: types.ModuleType) -> dict:
    historical = previous.self_test(middle, base)
    base.need(historical.get("status") == "PASS"
              and historical.get("reference_archive_gzip_inflation_count") == 0
              and historical.get("matching_archive_gzip_inflation_count") == 0,
              "first exercise every independently frozen V41, V40 and V39 physical wall")
    rejected = 0
    with base.SourceOnlyWall() as wall:
        proof = synthetic_rust_proof(base)
        for field, value in proof.items():
            hostile = copy.deepcopy(proof)
            hostile[field] = base.forged(value)
            try:
                validate_rust_proof(base, hostile)
            except (base.GraphError, TypeError, ValueError, KeyError, AttributeError):
                rejected += 1
            else:
                raise base.GraphError("accepted a forged Rust-only proof: " + field)
        for role in ("source", "protocol", "contract"):
            for field, value in proof[role].items():
                hostile = copy.deepcopy(proof)
                hostile[role][field] = base.forged(value)
                try:
                    validate_rust_proof(base, hostile)
                except (base.GraphError, TypeError, ValueError, KeyError, AttributeError):
                    rejected += 1
                else:
                    raise base.GraphError("accepted a forged Rust-only " + role)
        contract = proof["complete_frozen_contract"]
        for field, value in contract.items():
            hostile = copy.deepcopy(proof)
            hostile["complete_frozen_contract"][field] = base.forged(value)
            try:
                validate_rust_proof(base, hostile)
            except (base.GraphError, TypeError, ValueError, KeyError, AttributeError):
                rejected += 1
            else:
                raise base.GraphError("accepted a forged Rust-only contract: " + field)
        for group in ("source", "protocol", "pinned_cpython",
                      "original_oracle", "source_only_effects"):
            for field, value in contract[group].items():
                hostile = copy.deepcopy(proof)
                hostile["complete_frozen_contract"][group][field] = base.forged(value)
                try:
                    validate_rust_proof(base, hostile)
                except (base.GraphError, TypeError, ValueError, KeyError, AttributeError):
                    rejected += 1
                else:
                    raise base.GraphError("accepted an altered Rust-only " + group)
        probes = (
            ("filesystem", lambda: builtins.open("forbidden-v42")),
            ("filesystem", lambda: os.open("forbidden-v42", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v42")),
            ("write", lambda: os.mkdir("forbidden-v42")),
            ("process", lambda: subprocess.run(("forbidden-v42",))),
            ("process", lambda: subprocess.Popen(("forbidden-v42",))),
            ("process", lambda: os.execv("/forbidden-v42", [])),
        )
        for kind, action in probes:
            old = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(wall.blocked[kind] == old + 1,
                          "physically block the exact V42 source-only " + kind)
            else:
                raise base.GraphError("a genuine dual-runner source effect escaped")
        base.need(rejected >= 60,
                  "reject all forged independent Rust families, owners and effects")
        return {
            "schema": SCHEMA + "-source-only-self-test", "version": 42,
            "status": "PASS", "synthetic_only": True,
            "previous_v41_hostile_controls": historical["rejected_hostile_control_count"],
            "rust_only_runner_hostile_controls": rejected,
            "rejected_hostile_control_count":
                historical["rejected_hostile_control_count"] + rejected,
            "previous_v41_blocked_effects_by_kind":
                historical["previous_v40_blocked_effects_by_kind"],
            "blocked_effects_by_kind": dict(wall.blocked),
            "full_case_denominator": 31237, "suite_count": 13,
            "private_waiver_count": 13,
            "dedicated_corrected_runnable_family_count": 2,
            "dedicated_corrected_runnable_families": ["c", "rust"],
            "first_party_source_inventory_family_count": 6,
            "other_corrected_candidate_family_count": 4,
            "corrected_c_matching_status": "NOT RUN",
            "corrected_rust_matching_status": "NOT RUN",
            "corrected_rust_only_runner_status": RUST_STATUS,
            "qualified_candidate_count": 0,
            "actual_reference_evidence_read_by_self_test": 0,
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
    base.need(RUST_PINS_RELEASED is True and path in allowed
              and type(raw) is bytes and 0 < len(raw) <= base.OWNER_LIMIT,
              "publish only exact new dual-runner graph owners after Rust pin release")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(descriptor, remaining)
            base.need(type(count) is int and count > 0,
                      "reject incomplete independently created V42 owner bytes")
            remaining = remaining[count:]
        os.fsync(descriptor)
        owner = os.fstat(descriptor)
        base.need(owner.st_uid == os.geteuid() and owner.st_nlink == 1
                  and owner.st_size == len(raw)
                  and stat.S_IMODE(owner.st_mode) == 0o600,
                  "require one private, uniquely created durable V42 graph owner")
    finally:
        os.close(descriptor)
    directory = os.open(str(ROOT / Path(path).parent),
                        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                        | getattr(os, "O_CLOEXEC", 0)
                        | getattr(os, "O_NOFOLLOW", 0))
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    observed, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(observed == raw, "reproduce every exact final dual-runner V42 byte")


def result(base: types.ModuleType, source: str, outputs: dict[str, bytes],
           written: bool, suffix: str) -> dict:
    return {
        "schema": SCHEMA + suffix, "version": 42, "status": "PASS",
        "source_sha256": source,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 41,
        "previous_overview_source_sha256": V41["source"][1],
        "previous_overview_inputs_sha256": V41["inputs"][1],
        "previous_overview_summary_sha256": V41["summary"][1],
        "previous_overview_svg_sha256": V41["svg"][1],
        "corrected_rust_only_runner_source_sha256": RUST["source"][1],
        "corrected_rust_only_runner_protocol_sha256": RUST["protocol"][1],
        "corrected_rust_only_runner_contract_sha256": RUST["contract"][1],
        "corrected_rust_only_runner_status": RUST_STATUS,
        "corrected_rust_only_runner_family": "rust",
        "corrected_rust_matching_status": "NOT RUN",
        "corrected_rust_candidate_workers_started": 0,
        "corrected_rust_candidate_qualified": False,
        "corrected_c_only_runner_family": "c",
        "corrected_c_matching_status": "NOT RUN",
        "corrected_c_candidate_workers_started": 0,
        "corrected_c_candidate_qualified": False,
        "dedicated_corrected_runnable_family_count": 2,
        "dedicated_corrected_runnable_families": ["c", "rust"],
        "first_party_source_inventory_family_count": 6,
        "other_corrected_candidate_family_count": 4,
        "other_corrected_candidate_matching_status": "NOT RUN",
        "pending_corrected_candidate_families": ["zig", "cpp", "go", "fortran"],
        "candidate_case_producer_status": DUAL_STATUS,
        "candidate_matching_block_reason": DUAL_BLOCK_REASON,
        "all_candidate_matching_blocked": True,
        "qualified_candidate_count": 0,
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
    parser.add_argument("--rust-source-sha256")
    parser.add_argument("--rust-protocol-sha256")
    parser.add_argument("--rust-contract-sha256")
    for role in ("inputs", "summary", "svg"):
        parser.add_argument("--" + role + "-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, middle, base = load_v41()
        if options.self_test:
            base.need(all(getattr(options, name) is None for name in (
                "source_sha256", "source_bytes", "archive_sha256",
                "receipt_sha256", "producer_source_sha256",
                "producer_protocol_sha256", "producer_contract_sha256",
                "runner_source_sha256", "worker_source_sha256",
                "runner_protocol_sha256", "runner_contract_sha256",
                "rust_source_sha256", "rust_protocol_sha256",
                "rust_contract_sha256", "inputs_sha256", "summary_sha256",
                "svg_sha256",
            )), "synthetic self-tests cannot accept any real source or archive pin")
            sys.stdout.buffer.write(base.canonical(self_test(previous, middle, base)))
            return 0
        base.need(RUST_PINS_RELEASED is True,
                  "block V42 graph rendering until independently reviewed Rust V6 release")
        source = base.checked(options.source_sha256, "exact final V42 renderer")
        archive = base.checked(options.archive_sha256, "genuine corrected Python archive")
        receipt = base.checked(options.receipt_sha256, "genuine corrected reference receipt")
        producer_source = base.checked(options.producer_source_sha256,
                                       "frozen six-source V4 producer")
        producer_protocol = base.checked(options.producer_protocol_sha256,
                                         "frozen V4 producer protocol")
        producer_contract = base.checked(options.producer_contract_sha256,
                                         "frozen V4 producer contract")
        c_runner = base.checked(options.runner_source_sha256,
                                "frozen C-only V10 controller")
        c_worker = base.checked(options.worker_source_sha256,
                                "frozen C-only V8 worker")
        c_protocol = base.checked(options.runner_protocol_sha256,
                                  "frozen C-only V10 protocol")
        c_contract = base.checked(options.runner_contract_sha256,
                                  "frozen C-only V10 contract")
        rust_source = base.checked(options.rust_source_sha256,
                                   "released Rust-only V6 source")
        rust_protocol = base.checked(options.rust_protocol_sha256,
                                     "released Rust-only V6 protocol")
        rust_contract = base.checked(options.rust_contract_sha256,
                                     "released Rust-only V6 contract")
        _snapshot, pairs = build(
            previous, middle, base, source, options.source_bytes,
            archive, receipt, producer_source, producer_protocol, producer_contract,
            c_runner, c_worker, c_protocol, c_contract,
            rust_source, rust_protocol, rust_contract,
        )
        outputs = dict(pairs)
        if options.render:
            base.need(options.inputs_sha256 is None
                      and options.summary_sha256 is None
                      and options.svg_sha256 is None,
                      "render only the three exact authorized new V42 graph owners")
            for path, raw in pairs:
                publish(base, path, raw)
            sys.stdout.buffer.write(base.canonical(result(base, source, outputs,
                                                         True, "-published")))
            return 0
        frozen = {
            OUTPUT + ".inputs.json": base.checked(options.inputs_sha256,
                                                  "exact V42 inputs"),
            OUTPUT + ".json": base.checked(options.summary_sha256,
                                            "exact V42 summary"),
            OUTPUT + ".svg": base.checked(options.svg_sha256,
                                           "exact V42 SVG"),
        }
        for path, fingerprint in frozen.items():
            observed, _ = base.read_owner(path, fingerprint, len(outputs[path]),
                                          private=True)
            base.need(observed == outputs[path],
                      "independently reproduce every immutable V42 output byte")
        sys.stdout.buffer.write(base.canonical(result(base, source, outputs,
                                                      False,
                                                      "-read-only-frozen-context")))
        return 0
    except (ValueError, OSError, TypeError, EOFError, KeyError, AttributeError,
            RecursionError) as error:
        sys.stderr.write("current V42 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V42 overview rejected: " + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
