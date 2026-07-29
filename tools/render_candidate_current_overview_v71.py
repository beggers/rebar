#!/usr/bin/env python3
"""Reproduce the honest, source-only six-engine compatibility overview."""

from __future__ import annotations

import argparse
import copy
import hashlib
import os
from pathlib import Path
import stat
import sys
import types


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v71.py"
OUTPUT = "docs/evidence/candidate-current-overview-v71"
SCHEMA = "rebar-candidate-current-overview-v71"
BLOCKED = "BLOCKED PENDING INDEPENDENTLY ATTESTED PRIVATE ROOT"
V70 = {
    "source": ("tools/render_candidate_current_overview_v70.py", "35495c3f330d9e11e4ee5d9b16dbc057b91c34e22cc6cb7fc340df7894ddc5b7", 75541, 430956),
    "inputs": ("docs/evidence/candidate-current-overview-v70.inputs.json", "719520244f366f538a2c3672ca575feebf47dc083028f24e84fbaa7b348913d2", 1107190, 430957),
    "summary": ("docs/evidence/candidate-current-overview-v70.json", "124cc1583b065aa656ecb9fb0d93aa8beecfebf4998a2f58fb619dd7d609702c", 3097493, 430958),
    "svg": ("docs/evidence/candidate-current-overview-v70.svg", "bb2ea5e22cd40f5ae767829f47c4bfcb4793e91126626d40507ba1887573670c", 6992, 430966),
}
FEATURE = {
    "source": ("tools/reproduce_owned_rust_buffer_shape_source_build_v19.py", "650b33a10d253e09d48a423d12c8a1bb8180af4c4e96222aa13e72c75427bb5c", 88532, 430955),
    "protocol": ("oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V19.md", "4cdc322b2a516b28bf771440202efaca77074f7c8cd31c25692dc6ffc81797b5", 5808, 524752),
    "contract": ("oracle/phase2/rust-buffer-shape-source-build-v19.json", "78e31d32cd17e100613ea98cecec4051ca2f6563b0d3b198c66f69501171ac46", 14975, 524753),
}
C_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v16-c-phase2-v16-c-subject-buffer-original-p0-publication-receipt.json",
    "16794f5b1487b76a909a176948f4bbac8ed3108768f3127e27c44f9f392ae3d6", 2671, 524751,
)
C_VARIANT = (
    "candidates/c/variants/subject_buffer_ownership_v1/vm_native.c",
    "8131aea768a122308716b8a67903794aa03f2fed2e2022f53bb6aa7b7e10e962", 222212, 524723,
)


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    path, expected, size, inode = item
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(str(ROOT / path), flags)
    try:
        before = os.fstat(fd)
        if not (stat.S_ISREG(before.st_mode) and before.st_uid == os.geteuid()
                and before.st_dev == 2064 and before.st_ino == inode
                and before.st_nlink == 1 and before.st_size == size
                and stat.S_IMODE(before.st_mode) == 0o600):
            raise ValueError("reject substituted " + label)
        parts: list[bytes] = []
        left = size
        while left:
            part = os.read(fd, min(left, 262144))
            if not part:
                raise ValueError("reject truncated " + label)
            parts.append(part)
            left -= len(part)
        if os.read(fd, 1):
            raise ValueError("reject extended " + label)
        raw = b"".join(parts)
        after = os.fstat(fd)
        if hashlib.sha256(raw).hexdigest() != expected or (
            before.st_dev, before.st_ino, before.st_size, before.st_nlink,
            before.st_mtime_ns, before.st_ctime_ns,
        ) != (
            after.st_dev, after.st_ino, after.st_size, after.st_nlink,
            after.st_mtime_ns, after.st_ctime_ns,
        ):
            raise ValueError("reject changed " + label)
        return raw
    finally:
        os.close(fd)


def load_previous() -> tuple[types.ModuleType, types.ModuleType, tuple, types.ModuleType]:
    raw = read_fixed(V70["source"], "published V70 graph source")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v70")
    previous.__file__ = str(ROOT / V70["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    v69, modules, base = previous.load_v69()
    base.runtime()
    base.need(previous.SCHEMA == "rebar-candidate-current-overview-v70"
              and previous.SELF == V70["source"][0],
              "reject an unpushed or substituted V70 predecessor")
    return previous, v69, modules, base


def validate_contract(base: types.ModuleType, contract: object,
                      receipt: object) -> None:
    base.need(type(contract) is dict and type(receipt) is dict,
              "require complete real V19 contract and C16 receipt")
    assert isinstance(contract, dict) and isinstance(receipt, dict)
    expected_keys = {
        "authenticated_first_party_build_kernel", "current_rust_candidate",
        "family", "future_offline_root_provenance_build",
        "immutable_first_party_v18", "owned_rust_source_family", "phase",
        "phase1_v4_readiness", "pinned_cpython", "preserved_independent_c_family",
        "protocol", "published_current_graph",
        "published_root_blocked_rust_v11_original_campaign", "schema",
        "source", "source_only_effects", "version",
    }
    base.need(set(contract) == expected_keys and contract["version"] == 19
              and contract["schema"] == "rebar-phase2-owned-rust-buffer-shape-source-build-v19-source-freeze"
              and contract["family"] == "rust"
              and contract["phase"] == "SOURCE FREEZE; OFFLINE RUST ROOT PROVENANCE NOT BUILT OR RUN",
              "reject omitted, invented, or weakened complete V19 contract")
    for role in ("source", "protocol"):
        item = FEATURE[role]
        base.need(contract[role] == base.pin(item[0], item[1], item[2]),
                  "reject unpinned V19 feature " + role)
    graph = contract["published_current_graph"]
    base.need(type(graph) is dict and graph["version"] == 70
              and graph["authenticated_evidence_owner_lower_bound"] == 233
              and graph["authenticated_history_reference_lower_bound"] == 238
              and graph["owner_count"] == 4,
              "reject a stale, guessed, or counted V70 predecessor")
    base.need(set(graph["owners"]) == set(V70),
              "preserve all four actual V70 predecessor owners")
    for role, item in V70.items():
        owner = graph["owners"][role]
        base.need(owner["path"] == item[0] and owner["sha256"] == item[1]
                  and owner["bytes"] == item[2] and owner["inode"] == item[3]
                  and owner["device"] == 2064 and owner["nlink"] == 1
                  and owner["mode"] == "0600",
                  "reject substituted complete V70 owner " + role)
    future = contract["future_offline_root_provenance_build"]
    base.need(future["expected_actual_compiler_process_count"] == 28
              and future["independent_phase_count"] == 2
              and future["additional_root_receipt_count"] == 1
              and future["unique_label"] == "phase2-v19-rust-buffer-shape-root-provenance"
              and future["external_cargo_dependency_count"] == 0
              and future["tmp_directory_scanning"] == "FORBIDDEN",
              "do not invent an actual V19 build or private native root")
    effects = contract["source_only_effects"]
    base.need(effects["actual_compiler_process_count"] == 0
              and effects["compiler_processes_started"] == 0
              and effects["actual_candidate_workers"] == 0
              and effects["actual_root_descriptor_opens"] == 0
              and effects["archive_opens"] == 0
              and effects["archive_bytes_read"] == 0
              and effects["clock_samples"] == 0
              and effects["root_provenance"] == "NOT MEASURED"
              and effects["runtime_non_delegation"] == "NOT ESTABLISHED"
              and effects["holdout"] == "NOT OPENED",
              "reject fabricated V19 source-freeze side effects")
    v11 = contract["published_root_blocked_rust_v11_original_campaign"]
    base.need(v11["version"] == 11 and v11["candidate_execution_status"] == BLOCKED
              and v11["build_inspection_status"] == BLOCKED
              and v11["candidate_workers_started"] == 0
              and v11["previous_private_root"] == "NOT MEASURED"
              and v11["previous_private_root_provenance"] == "NOT ESTABLISHED",
              "preserve the actual blocked V11 original correctness campaign")
    base.need(receipt["status"] == "PASS" and receipt["build_status"] == "PASS"
              and receipt["actual_compiler_process_count"] == 14
              and receipt["expected_compiler_process_count"] == 14
              and receipt["variant_source_sha256"] == C_VARIANT[1]
              and receipt["variant_source_bytes"] == C_VARIANT[2]
              and receipt["candidate_imports"] == 0
              and receipt["candidate_processes_started"] == 0
              and receipt["candidate_correctness"] == "NOT MEASURED"
              and receipt["runtime_non_delegation"] == "NOT ESTABLISHED"
              and receipt["holdout"] == "NOT OPENED",
              "derive corrected C feature status only from its genuine build receipt")
    c = contract["preserved_independent_c_family"]
    owner = c["build_receipt"]
    base.need(owner["path"] == C_RECEIPT[0] and owner["sha256"] == C_RECEIPT[1]
              and owner["bytes"] == C_RECEIPT[2] and owner["inode"] == C_RECEIPT[3]
              and c["actual_build_status"] == "PASS"
              and c["actual_compiler_process_count"] == 14
              and c["previous_matching_status"] == "FAIL"
              and c["semantic_mismatch_count"] == 1230
              and c["explicitly_verified_passing_case_count"] == 7325,
              "keep exact independent C matching failure distinct from build success")


def authenticate_previous(previous: types.ModuleType, v69: types.ModuleType,
                          modules: tuple, base: types.ModuleType) -> tuple[dict, dict]:
    inherited = previous.previous_options(v69, modules)
    values: dict[str, object] = {
        "source_sha256": V70["source"][1], "source_bytes": V70["source"][2],
        "inputs_sha256": None, "summary_sha256": None, "svg_sha256": None,
    }
    for role, item in previous.V69.items():
        values["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.FEATURE.items():
        values["feature_" + role + "_sha256"] = item[1]
    for role in ("source", "protocol", "contract"):
        values["readiness_" + role + "_sha256"] = getattr(
            inherited, "readiness_" + role + "_sha256")
    snapshot, pairs = previous.build(v69, modules, base, argparse.Namespace(**values))
    rendered = dict(pairs)
    for role in ("inputs", "summary", "svg"):
        item = V70[role]
        base.need(rendered[item[0]] == read_fixed(item, "published V70 " + role),
                  "reproduce every complete genuinely published V70 " + role)
    old = base.document(rendered[V70["summary"][0]], "complete V70 summary")
    old_inputs = base.document(rendered[V70["inputs"][0]], "complete V70 inputs")
    base.need(old["snapshot"] == snapshot and old["version"] == 70
              and old["actual_current_graph_predecessor_version"] == 69
              and old["authenticated_evidence_owner_lower_bound"] == 233
              and old["authenticated_history_reference_lower_bound"] == 238,
              "authenticate full genuinely pushed V70 history")
    return old, old_inputs


def make_svg(snapshot: dict) -> bytes:
    rows = [
        ("Python re", "Reference: original checks pass", "BASELINE", "#22c55e"),
        ("Rust", "1,440 differences; traceable rebuild not run", "NOT COMPATIBLE", "#f59e0b"),
        ("C", "1,230 differences; corrected build passes", "NOT COMPATIBLE", "#f59e0b"),
        ("Zig", "1,764 differences", "NOT COMPATIBLE", "#fb7185"),
        ("C++", "2,308 differences; five worker failures", "NOT COMPATIBLE", "#fb7185"),
        ("Go", "4,518 differences; four worker failures", "NOT COMPATIBLE", "#fb7185"),
        ("Fortran", "Full Python compatibility not tested", "NOT TESTED", "#94a3b8"),
    ]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1060" height="570" viewBox="0 0 1060 570" role="img" aria-labelledby="title description">',
        '<title id="title">Python and six from-scratch regular-expression engines</title>',
        '<desc id="description">Python is the correctness baseline. No replacement has passed all compatibility tests or measured a speedup. C and Rust have reproducible builds; the new traceable Rust build has not run.</desc>',
        '<rect width="1060" height="570" rx="18" fill="#0b1220"/>',
        '<text x="34" y="47" fill="#f8fafc" font-size="25" font-family="system-ui,sans-serif" font-weight="700">Building a faster Python re, from scratch</text>',
        '<text x="34" y="78" fill="#cbd5e1" font-size="16" font-family="system-ui,sans-serif">6 independent engine designs · 0 fully compatible replacements · speed NOT MEASURED</text>',
        '<line x1="34" y1="99" x2="1026" y2="99" stroke="#334155"/>',
    ]
    for i, (name, detail, outcome, color) in enumerate(rows):
        y = 136 + i * 45
        lines.extend([
            f'<circle cx="43" cy="{y-5}" r="6" fill="{color}"/>',
            f'<text x="62" y="{y}" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="650">{name}</text>',
            f'<text x="179" y="{y}" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">{detail}</text>',
            f'<text x="1007" y="{y}" text-anchor="end" fill="{color}" font-size="13" font-family="system-ui,sans-serif" font-weight="700">{outcome}</text>',
        ])
    lines.extend([
        '<line x1="34" y1="442" x2="1026" y2="442" stroke="#334155"/>',
        '<text x="34" y="473" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">Compatibility reference: 31,237 original Python checks; 8,244 extra checks are separate.</text>',
        '<text x="34" y="500" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">C build: PASS (14 checks) · Rust build: PASS (28 checks) · New traceable Rust build: NOT RUN.</text>',
        '<text x="34" y="527" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Final comparison: 4,194,304 proposed cases; NOT GENERATED, NOT OPENED, NOT MEASURED.</text>',
        '<text x="34" y="551" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 71 · independently verified source evidence; no engine selected as a winner.</text>',
        '</svg>', '',
    ])
    return "\n".join(lines).encode("utf-8")


def build(previous: types.ModuleType, v69: types.ModuleType, modules: tuple,
          base: types.ModuleType, options: argparse.Namespace) -> tuple[dict, dict[str, bytes]]:
    base.need(options.source_sha256 is not None and options.source_bytes is not None,
              "require the exact V71 renderer owner")
    own_raw, _ = base.read_owner(SELF, base.checked(options.source_sha256, "V71 source"),
                                 options.source_bytes, private=True)
    for role, item in V70.items():
        base.need(getattr(options, "previous_" + role + "_sha256") == item[1],
                  "require actual complete V70 predecessor " + role)
    for role, item in FEATURE.items():
        base.need(getattr(options, "feature_" + role + "_sha256") == item[1],
                  "require actual complete V19 feature " + role)
        read_fixed(item, "actual first-party V19 " + role)
    base.need(options.c_receipt_sha256 == C_RECEIPT[1],
              "require actual published corrected C build receipt")
    contract_raw = read_fixed(FEATURE["contract"], "complete V19 contract")
    contract = base.document(contract_raw, "complete V19 source-only contract")
    base.need(base.canonical(contract) == contract_raw,
              "reject rewritten complete V19 source-only contract")
    receipt_raw = read_fixed(C_RECEIPT, "actual C16 build receipt")
    receipt = base.document(receipt_raw, "complete durable C16 build receipt")
    read_fixed(C_VARIANT, "independently built corrected C subject-buffer variant")
    validate_contract(base, contract, receipt)
    old, old_inputs = authenticate_previous(previous, v69, modules, base)
    proof = {
        "schema": SCHEMA + "-first-party-rust-root-provenance-source-v19",
        "status": "SOURCE FROZEN; OFFLINE RUST ROOT PROVENANCE NOT BUILT OR RUN",
        "family": "rust", "version": 19,
        "owners": {role: base.synthetic_owner(item[:3], item[3])
                   for role, item in FEATURE.items()},
        "complete_feature_contract": copy.deepcopy(contract),
        "independent_feature_source_owner_count": 3,
        "actual_compiler_process_count": 0,
        "planned_compiler_process_count": 28,
        "private_root_provenance": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
    }
    changes = {
        "actual_current_graph_predecessor_version": 70,
        "authenticated_evidence_owner_lower_bound": 236,
        "authenticated_history_reference_lower_bound": 241,
        "rust_native_build_v19_source_freeze": proof,
        "rust_native_build_v19_status": proof["status"],
        "rust_native_build_v19_planned_compiler_process_count": 28,
        "rust_native_build_v19_actual_compiler_process_count": 0,
        "rust_native_build_v19_private_root_provenance": "NOT MEASURED",
        "rust_native_build_v19_matching_status": "NOT RUN",
        "rust_native_build_v19_candidate_correctness": "NOT MEASURED",
        "rust_native_build_v19_candidate_qualified": False,
        "c_subject_buffer_ownership_v1_build_status": "PASS",
        "c_subject_buffer_ownership_v1_compiler_process_count": 14,
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(copy.deepcopy(changes))
    snapshot["preserved_v70_replaced_snapshot_fields"] = {
        key: copy.deepcopy(old["snapshot"][key])
        for key in changes if key in old["snapshot"]
    }
    predecessor = {role: base.pin(item[0], item[1], item[2])
                   for role, item in V70.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({"schema": SCHEMA + "-inputs", "version": 71,
                   "python": "3.14.6", "renderer": base.pin(SELF, options.source_sha256, len(own_raw)),
                   "previous_overview": predecessor, **copy.deepcopy(changes)})
    input_raw = base.canonical(inputs)
    svg_raw = make_svg(snapshot)
    families = copy.deepcopy(old["families"])
    base.need([row.get("family") for row in families]
              == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
              "preserve Python plus all six independently written engines")
    for row in families:
        if row["family"] != "python":
            row["authenticated_evidence_owner_lower_bound"] = 236
            row["authenticated_history_reference_lower_bound"] = 241
        if row["family"] == "rust":
            for key, value in changes.items():
                if key.startswith("rust_native_build_v19_"):
                    row[key] = copy.deepcopy(value)
        if row["family"] == "c":
            row["c_subject_buffer_ownership_v1_build_status"] = "PASS"
            row["c_subject_buffer_ownership_v1_compiler_process_count"] = 14
    summary = copy.deepcopy(old)
    summary.update({"schema": SCHEMA + "-summary", "version": 71,
                    "status": "PASS", "python": "3.14.6",
                    "source": base.pin(SELF, options.source_sha256, len(own_raw)),
                    "inputs": base.pin(OUTPUT + ".inputs.json", base.digest(input_raw), len(input_raw)),
                    "svg": base.pin(OUTPUT + ".svg", base.digest(svg_raw), len(svg_raw)),
                    "previous_overview": predecessor, "snapshot": snapshot,
                    "families": families, **copy.deepcopy(changes)})
    suites = old["actual_complete_rust_campaign"]["complete_independently_authenticated_suite_results"]
    witnesses = old["actual_complete_rust_campaign"]["earliest_genuine_mismatch_witnesses"]
    base.need(len(suites) == 13 and len(witnesses) == 6,
              "preserve all genuine complete original suites and mismatch witnesses")
    for label, layer in (("inputs", inputs), ("summary", summary), ("snapshot", snapshot)):
        campaign = layer["actual_complete_rust_campaign"]
        base.need(campaign["complete_independently_authenticated_suite_results"] == suites
                  and campaign["earliest_genuine_mismatch_witnesses"] == witnesses,
                  "preserve each complete heterogeneous original result: " + label)
        base.need(layer["c_subject_buffer_ownership_v1_build_status"] == "PASS"
                  and layer["c_subject_buffer_ownership_v1_compiler_process_count"] == 14,
                  "correct real C build status in graph " + label)
    c = next(row for row in families if row["family"] == "c")
    base.need(c["c_subject_buffer_ownership_v1_build_status"] == "PASS"
              and c["c_subject_buffer_ownership_v1_compiler_process_count"] == 14
              and summary["c_native_build_v16_status"] == "PASS"
              and summary["c_native_build_v16_compiler_process_count"] == 14
              and summary["rust_native_build_v18_status"] == "PASS"
              and summary["rust_native_build_v18_compiler_process_count"] == 28
              and summary["actual_rust_semantic_mismatch_count"] == 1440
              and summary["actual_rust_verified_passing_case_count"] == 14853
              and summary["actual_c_semantic_mismatch_count"] == 1230
              and summary["actual_c_verified_passing_case_count"] == 7325
              and summary["rust_v11_original_campaign_execution_status"] == BLOCKED
              and summary["rust_v11_original_campaign_actual_worker_count"] == 0
              and summary["qualified_candidate_count"] == 0
              and summary["final_holdout_opened"] is False
              and summary["runtime_no_delegation"] == "NOT ESTABLISHED"
              and summary["performance"] == "NOT MEASURED",
              "never convert an old passing build or source freeze into passing matching")
    return snapshot, {
        OUTPUT + ".inputs.json": input_raw,
        OUTPUT + ".json": base.canonical(summary),
        OUTPUT + ".svg": svg_raw,
    }


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    allowed = {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
    base.need(path in allowed and type(raw) is bytes and 0 < len(raw) <= base.OWNER_LIMIT,
              "publish only one of the three complete V71 graph assets")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(str(ROOT / path), flags, 0o600)
    try:
        view = memoryview(raw)
        while view:
            count = os.write(fd, view)
            base.need(type(count) is int and count > 0, "publish the full V71 graph asset")
            view = view[count:]
        os.fsync(fd)
        owner = os.fstat(fd)
        base.need(owner.st_uid == os.geteuid() and owner.st_dev == 2064
                  and owner.st_nlink == 1 and owner.st_size == len(raw)
                  and stat.S_IMODE(owner.st_mode) == 0o600,
                  "require an exclusive, complete, privately owned V71 asset")
    finally:
        os.close(fd)
    directory = os.open(str(ROOT / "docs/evidence"),
                        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                        | getattr(os, "O_CLOEXEC", 0))
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    confirmed, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(confirmed == raw, "reauthenticate the exact complete V71 graph asset")


def self_test(previous: types.ModuleType, v69: types.ModuleType,
              modules: tuple, base: types.ModuleType) -> dict:
    inherited = previous.self_test(v69, modules, base)
    base.need(inherited["status"] == "PASS"
              and inherited["actual_current_graph_predecessor_version"] == 69
              and inherited["authenticated_evidence_owner_lower_bound"] == 233
              and inherited["authenticated_history_reference_lower_bound"] == 238,
              "preserve every genuinely authenticated V70 hostile control")
    contract_raw = read_fixed(FEATURE["contract"], "source-only V19 contract")
    contract = base.document(contract_raw, "source-only V19 contract")
    receipt = base.document(read_fixed(C_RECEIPT, "source-only actual C receipt"),
                            "source-only actual C receipt")
    validate_contract(base, contract, receipt)
    rejected = 0
    cases = [
        ("missing contract", None, receipt),
        ("missing receipt", contract, None),
    ]
    for key in contract:
        hostile = copy.deepcopy(contract)
        hostile.pop(key)
        cases.append(("omitted full contract " + key, hostile, receipt))
    for key in ("status", "build_status", "actual_compiler_process_count",
                "variant_source_sha256", "candidate_correctness"):
        hostile_receipt = copy.deepcopy(receipt)
        hostile_receipt.pop(key)
        cases.append(("omitted actual C receipt " + key, contract, hostile_receipt))
    for label, bad_contract, bad_receipt in cases:
        try:
            validate_contract(base, bad_contract, bad_receipt)
        except (Exception,):
            rejected += 1
        else:
            base.need(False, "accepted forged V71 control: " + label)
    base.need(rejected >= 24, "reject omitted V19 and C evidence controls")
    return {
        "schema": SCHEMA + "-source-only-self-test", "version": 71,
        "status": "PASS", "previous_overview_version": 70,
        "inherited_rejected_hostile_control_count": inherited["rejected_hostile_control_count"],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": inherited["rejected_hostile_control_count"] + rejected,
        "actual_current_graph_predecessor_version": 70,
        "authenticated_evidence_owner_lower_bound": 236,
        "authenticated_history_reference_lower_bound": 241,
        "rust_native_build_v19_planned_compiler_process_count": 28,
        "rust_native_build_v19_actual_compiler_process_count": 0,
        "c_subject_buffer_ownership_v1_build_status": "PASS",
        "c_subject_buffer_ownership_v1_compiler_process_count": 14,
        "actual_rust_semantic_mismatch_count": 1440,
        "actual_c_semantic_mismatch_count": 1230,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_compressed_evidence_owners_opened_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_hidden_cases_read_by_graph": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "qualified_candidate_count": 0, "final_holdout_opened": False,
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    for role in V70:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in FEATURE:
        parser.add_argument("--feature-" + role + "-sha256")
    parser.add_argument("--c-receipt-sha256")
    for role in ("inputs", "summary", "svg"):
        parser.add_argument("--" + role + "-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, v69, modules, base = load_previous()
        if options.self_test:
            forbidden = ("source_sha256", "source_bytes", "c_receipt_sha256",
                         "inputs_sha256", "summary_sha256", "svg_sha256")
            base.need(all(getattr(options, key) is None for key in forbidden)
                      and all(getattr(options, "previous_" + role + "_sha256") is None
                              for role in V70)
                      and all(getattr(options, "feature_" + role + "_sha256") is None
                              for role in FEATURE),
                      "self-test accepts no actual graph render authority")
            result = self_test(previous, v69, modules, base)
        else:
            snapshot, outputs = build(previous, v69, modules, base, options)
            if options.render:
                base.need(all(getattr(options, role + "_sha256") is None
                              for role in ("inputs", "summary", "svg")),
                          "render cannot accept guessed V71 output hashes")
                for path, raw in outputs.items():
                    publish(base, path, raw)
            else:
                for role, suffix in (("inputs", ".inputs.json"),
                                     ("summary", ".json"), ("svg", ".svg")):
                    path = OUTPUT + suffix
                    fingerprint = base.checked(getattr(options, role + "_sha256"),
                                               "complete V71 " + role)
                    actual, _ = base.read_owner(path, fingerprint,
                                                len(outputs[path]), private=True)
                    base.need(actual == outputs[path],
                              "reproduce the complete V71 " + role)
            result = {
                "schema": SCHEMA + ("-published" if options.render
                                     else "-read-only-frozen-context"),
                "version": 71, "status": "PASS",
                "source_sha256": options.source_sha256,
                "source_bytes": options.source_bytes,
                **{role + "_sha256": base.digest(raw)
                   for role, raw in (("inputs", outputs[OUTPUT + ".inputs.json"]),
                                     ("summary", outputs[OUTPUT + ".json"]),
                                     ("svg", outputs[OUTPUT + ".svg"]))},
                "previous_overview_version": 70,
                "actual_current_graph_predecessor_version": 70,
                "authenticated_evidence_owner_lower_bound": 236,
                "authenticated_history_reference_lower_bound": 241,
                "c_subject_buffer_ownership_v1_build_status": "PASS",
                "c_subject_buffer_ownership_v1_compiler_process_count": 14,
                "rust_native_build_v19_planned_compiler_process_count": 28,
                "rust_native_build_v19_actual_compiler_process_count": 0,
                "rust_v11_original_campaign_execution_status": BLOCKED,
                "actual_rust_semantic_mismatch_count": 1440,
                "actual_c_semantic_mismatch_count": 1230,
                "actual_candidate_workers_started_by_graph": 0,
                "actual_compiler_processes_started_by_graph": 0,
                "actual_compressed_evidence_owners_opened_by_graph": 0,
                "actual_clock_samples_by_graph": 0,
                "qualified_candidate_count": 0,
                "final_holdout_opened": False,
                "runtime_no_delegation": "NOT ESTABLISHED",
                "performance": "NOT MEASURED",
                "outputs_written": bool(options.render),
            }
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except Exception as error:
        sys.stderr.write("current V71 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
