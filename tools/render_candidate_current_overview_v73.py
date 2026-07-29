#!/usr/bin/env python3
"""Show the from-scratch Zig scanner fix without inventing a passing engine."""

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
SELF = "tools/render_candidate_current_overview_v73.py"
OUTPUT = "docs/evidence/candidate-current-overview-v73"
SCHEMA = "rebar-candidate-current-overview-v73"
BLOCKED = "BLOCKED PENDING INDEPENDENTLY ATTESTED PRIVATE ROOT"
V72 = {
    "source": ("tools/render_candidate_current_overview_v72.py", "b279901481d2f4f6bc1adeae542d5aacf2453dedbcff88a944a79ce5c8478753", 37922, 431192),
    "inputs": ("docs/evidence/candidate-current-overview-v72.inputs.json", "28f235f8bbb7e49de25a1194fa0693e9764d3e5b0ef7a3e5a4da8e273f22eaef", 1134228, 431200),
    "summary": ("docs/evidence/candidate-current-overview-v72.json", "2b5dba28961c0842fc15df1afdca49eeb20613df05b31c1bd4a16491f7f9c25b", 3179471, 431201),
    "svg": ("docs/evidence/candidate-current-overview-v72.svg", "eb2708426467a85a6d7ee592c4dde21fc08b57f8a17822a0b60732f44f22e804", 4734, 431202),
}
FEATURE = {
    "source": ("tools/apply_owned_zig_scanner_phrase_source_repair_v4.py", "31dafa08a8f394a8803fa352dd31c806fdac7aa6ee9160e67f2d5f60b2736a63", 65425, 428967),
    "protocol": ("oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-REPAIR-V4.md", "e17a46e13652e2950171d84096a0bf812020c88168589c17e50e1bab187339cf", 6919, 524729),
    "contract": ("oracle/phase2/zig-scanner-phrase-source-repair-v4.json", "5c8f9a220bf93fc56e9d8054002ea4358323c23a9a951d3ce28201b59947b19c", 11500, 524730),
    "variant": ("candidates/zig/variants/scanner_phrase_v4/zig_candidate.py", "0ab9f56b469df7939af8a221a4deac9351de2162960085ca7fa2d69179480e2b", 68530, 428966),
}
CONTRACT_KEYS = frozenset({
    "current_graph", "first_party_source_feature", "from_scratch_policy",
    "frozen_source_owners", "holdout", "memory", "original_oracle",
    "performance", "phase", "preserved_current_graph_history",
    "previous_actual_zig_matching", "protocol", "qualified_candidate_count",
    "schema", "source", "source_only_effects", "status", "undefined_behavior",
    "version", "winner_selected",
})


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    path, fingerprint, size, inode = item
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
        remaining = size
        while remaining:
            part = os.read(fd, min(remaining, 262144))
            if not part:
                raise ValueError("reject truncated " + label)
            parts.append(part)
            remaining -= len(part)
        if os.read(fd, 1):
            raise ValueError("reject extended " + label)
        raw = b"".join(parts)
        after = os.fstat(fd)
        if hashlib.sha256(raw).hexdigest() != fingerprint or (
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


def load_previous() -> tuple[types.ModuleType, types.ModuleType, types.ModuleType,
                              types.ModuleType, tuple, types.ModuleType]:
    raw = read_fixed(V72["source"], "genuinely published V72 renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v72")
    previous.__file__ = str(ROOT / V72["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    v71, v70, v69, modules, base = previous.load_previous()
    base.runtime()
    base.need(previous.SCHEMA == "rebar-candidate-current-overview-v72"
              and previous.SELF == V72["source"][0],
              "authenticate only the genuinely pushed complete V72 renderer")
    return previous, v71, v70, v69, modules, base


def validate_contract(base: types.ModuleType, contract: object) -> None:
    base.need(type(contract) is dict and set(contract) == CONTRACT_KEYS,
              "reject omitted or invented complete Zig source-freeze evidence")
    assert isinstance(contract, dict)
    base.need(contract["schema"] == "rebar-owned-zig-scanner-phrase-source-repair-v4"
              and contract["version"] == 4
              and contract["status"] == "SOURCE FROZEN; FIRST-PARTY ZIG VARIANT NOT BUILT OR TESTED"
              and contract["phase"] == "PHASE 2 FIRST-PARTY ZIG SOURCE FEATURE"
              and contract["holdout"] == "NOT OPENED"
              and contract["performance"] == "NOT MEASURED"
              and contract["qualified_candidate_count"] == 0
              and contract["winner_selected"] is False,
              "never claim that the first-party Zig variant was built or tested")
    for role in ("source", "protocol"):
        item = FEATURE[role]
        owner = contract[role]
        base.need(owner["path"] == item[0] and owner["sha256"] == item[1]
                  and owner["bytes"] == item[2] and owner["inode"] == item[3]
                  and owner["device"] == 2064 and owner["mode"] == "0600"
                  and owner["nlink"] == 1,
                  "reject substituted complete first-party Zig " + role)
    graph = contract["current_graph"]
    base.need(graph["version"] == 72
              and graph["authenticated_evidence_owner_lower_bound"] == 239
              and graph["authenticated_history_reference_lower_bound"] == 244
              and graph["lower_bounds_are_whole_repository_census"] is False
              and graph["source_freeze_new_evidence_owner_count"] == 0
              and type(graph["owners"]) is list and len(graph["owners"]) == 4,
              "bind all four genuinely published current V72 graph owners")
    owners = {owner["path"]: owner for owner in graph["owners"]}
    base.need(set(owners) == {item[0] for item in V72.values()},
              "reject a guessed, omitted, or stale V72 graph owner")
    for item in V72.values():
        owner = owners[item[0]]
        base.need(owner["sha256"] == item[1] and owner["bytes"] == item[2]
                  and owner["inode"] == item[3] and owner["device"] == 2064
                  and owner["mode"] == "0600" and owner["nlink"] == 1,
                  "reject substituted full V72 predecessor graph owner")
    feature = contract["first_party_source_feature"]
    base.need(feature["family"] == "zig"
              and feature["function"] == "candidates.zig_candidate.Scanner.__init__"
              and feature["corrected_candidate_build"] == "NOT RUN"
              and feature["corrected_candidate_matching"] == "NOT RUN"
              and feature["corrected_candidate_qualified"] is False
              and feature["capture_check_occurs_before_native_compile"] is True
              and feature["outside_feature_block_unchanged"] is True
              and feature["original_engine_modified"] is False
              and feature["original_bridge_modified"] is False
              and feature["variant_materialized"] is True,
              "preserve the genuine independent Zig parser, matcher, and scanner")
    variant = feature["complete_materialized_variant"]
    item = FEATURE["variant"]
    base.need(variant["path"] == item[0] and variant["sha256"] == item[1]
              and variant["bytes"] == item[2] and variant["inode"] == item[3]
              and variant["device"] == 2064 and variant["mode"] == "0600"
              and variant["nlink"] == 1,
              "authenticate the complete independently materialized Zig variant")
    for field, path, digest in (
        ("independent_engine", "candidates/zig/mini_regex.zig",
         "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28"),
        ("independent_cpython_bridge", "candidates/zig/py_bridge.c",
         "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b"),
    ):
        owner = feature[field]
        base.need(owner["path"] == path and owner["sha256"] == digest
                  and owner["device"] == 2064 and owner["nlink"] == 1,
                  "never substitute an external regex engine for " + field)
        read_fixed((owner["path"], owner["sha256"], owner["bytes"], owner["inode"]),
                   "independent original Zig " + field)
    matrix = feature["scanner_matrix"]
    base.need(matrix["family_count"] == 32 and matrix["variants_per_family"] == 32
              and matrix["matrix_case_count"] == 1024
              and matrix["overflow_case_count"] == 64
              and matrix["preserved_nonoverflow_case_count"] == 960
              and matrix["candidate_imports"] == 0
              and matrix["candidate_workers_started"] == 0
              and matrix["native_activations"] == 0
              and matrix["reference_workers_started"] == 0,
              "preserve all 1,024 original scanner cases without inventing a run")
    previous = contract["previous_actual_zig_matching"]
    base.need(previous["status"] == "FAIL"
              and previous["semantic_mismatch_count"] == 1764
              and previous["verified_passing_case_count"] == 3711
              and previous["case_execution_denominator"] == 31237
              and previous["completed_suite_count"] == 13
              and previous["actual_candidate_worker_count"] == 13
              and previous["infrastructure_failure_count"] == 0
              and previous["matching_archive_read"] is False,
              "retain the genuine historical full-suite Zig failure")
    history = contract["preserved_current_graph_history"]
    rust = history["rust_original_matching"]
    c = history["c_original_matching"]
    v19 = history["rust_v19_native_build"]
    c16 = history["c_v16_native_build"]
    v11 = history["rust_v11_original_campaign"]
    base.need(rust["status"] == "FAIL"
              and rust["semantic_mismatch_count"] == 1440
              and rust["verified_passing_case_count"] == 14853
              and c["status"] == "FAIL" and c["semantic_mismatch_count"] == 1230
              and c["verified_passing_case_count"] == 7325
              and v19["status"] == "PASS" and v19["actual_compiler_process_count"] == 28
              and v19["matching_status"] == "NOT RUN"
              and v19["private_root_provenance"] == "PASS"
              and c16["status"] == "PASS" and c16["compiler_process_count"] == 14
              and c16["matching_status"] == "NOT RUN"
              and v11["execution_status"] == BLOCKED
              and v11["actual_worker_count"] == 0,
              "never overwrite actual Rust/C history or unlock the old Rust campaign")
    oracle = contract["original_oracle"]
    base.need(oracle["original_case_execution_denominator"] == 31237
              and oracle["suite_count"] == 13
              and oracle["mapped_obligation_count"] == 73
              and oracle["named_private_waiver_count"] == 13
              and oracle["additional_independently_referenced_case_count"] == 8244
              and oracle["additional_cases_included_in_original_denominator"] is False,
              "never merge distinct original and supplemental oracle denominators")
    policy = contract["from_scratch_policy"]
    base.need(policy["external_regex_package"] == "FORBIDDEN"
              and policy["stdlib_re_engine"] == "FORBIDDEN"
              and policy["stdlib_sre_engine"] == "FORBIDDEN"
              and policy["another_candidate_engine"] == "FORBIDDEN"
              and policy["matching_fallback"] == "FORBIDDEN"
              and policy["runtime_non_delegation"] == "NOT ESTABLISHED",
              "do not disguise a wrapper or claim an unperformed runtime audit")
    base.need(all(value == 0 for value in contract["source_only_effects"].values()),
              "reject hidden candidate, compiler, archive, clock, or holdout effects")


def authenticate_previous(previous: types.ModuleType, v71: types.ModuleType,
                          v70: types.ModuleType, v69: types.ModuleType,
                          modules: tuple, base: types.ModuleType) -> tuple[dict, dict]:
    values: dict[str, object] = {
        "source_sha256": V72["source"][1], "source_bytes": V72["source"][2],
    }
    for role, item in previous.V71.items():
        values["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.EVIDENCE.items():
        values["evidence_" + role + "_sha256"] = item[1]
    snapshot, pairs = previous.build(v71, v70, v69, modules, base,
                                     argparse.Namespace(**values))
    for role in ("inputs", "summary", "svg"):
        item = V72[role]
        base.need(pairs[item[0]] == read_fixed(item, "published V72 " + role),
                  "reproduce the complete actual V72 predecessor " + role)
    old = base.document(pairs[V72["summary"][0]], "complete pushed V72 summary")
    old_inputs = base.document(pairs[V72["inputs"][0]], "complete pushed V72 inputs")
    base.need(old["snapshot"] == snapshot and old["version"] == 72
              and old["actual_current_graph_predecessor_version"] == 71
              and old["authenticated_evidence_owner_lower_bound"] == 239
              and old["authenticated_history_reference_lower_bound"] == 244
              and old["rust_native_build_v19_status"] == "PASS"
              and old["rust_native_build_v19_actual_compiler_process_count"] == 28
              and old["actual_rust_semantic_mismatch_count"] == 1440,
              "preserve complete genuine independently attested V72 evidence")
    return old, old_inputs


def make_svg() -> bytes:
    rows = [
        ("Python re", "Correctness reference passes", "BASELINE", "#22c55e"),
        ("Rust", "Build passes; 1,440 earlier differences", "NOT COMPATIBLE", "#f59e0b"),
        ("C", "Build passes; 1,230 earlier differences", "NOT COMPATIBLE", "#f59e0b"),
        ("Zig", "64 scanner cases corrected; 1,764 earlier differences", "NOT RETESTED", "#f59e0b"),
        ("C++", "2,308 differences; five worker failures", "NOT COMPATIBLE", "#fb7185"),
        ("Go", "4,518 differences; four worker failures", "NOT COMPATIBLE", "#fb7185"),
        ("Fortran", "Full Python compatibility not tested", "NOT TESTED", "#94a3b8"),
    ]
    result = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="570" viewBox="0 0 1080 570" role="img" aria-labelledby="title description">',
        '<title id="title">Python and six independently written matching engines</title>',
        '<desc id="description">Python is the correctness baseline. The Zig scanner source fixes 64 of 1,024 frozen cases, but the corrected engine has not been built or retested. No replacement has qualified or measured a speedup.</desc>',
        '<rect width="1080" height="570" rx="18" fill="#0b1220"/>',
        '<text x="34" y="47" fill="#f8fafc" font-size="25" font-family="system-ui,sans-serif" font-weight="700">Building a faster Python re, from scratch</text>',
        '<text x="34" y="78" fill="#cbd5e1" font-size="16" font-family="system-ui,sans-serif">6 independent engines · 0 compatible replacements · speed NOT MEASURED</text>',
        '<line x1="34" y1="99" x2="1046" y2="99" stroke="#334155"/>',
    ]
    for index, (name, detail, outcome, color) in enumerate(rows):
        y = 136 + index * 45
        result.extend([
            f'<circle cx="43" cy="{y-5}" r="6" fill="{color}"/>',
            f'<text x="62" y="{y}" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="650">{name}</text>',
            f'<text x="179" y="{y}" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">{detail}</text>',
            f'<text x="1027" y="{y}" text-anchor="end" fill="{color}" font-size="13" font-family="system-ui,sans-serif" font-weight="700">{outcome}</text>',
        ])
    result.extend([
        '<line x1="34" y1="442" x2="1046" y2="442" stroke="#334155"/>',
        '<text x="34" y="473" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">Original reference: 31,237 Python checks; the 8,244 additional checks are separate.</text>',
        '<text x="34" y="500" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Zig scanner: 1,024 original cases · 64 fixed in source · 960 unchanged · build NOT RUN.</text>',
        '<text x="34" y="527" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Final comparison: 4,194,304 proposed cases; NOT GENERATED, NOT OPENED, NOT MEASURED.</text>',
        '<text x="34" y="551" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 73 · no external regex engine, no passing candidate, no winner.</text>',
        '</svg>', '',
    ])
    return "\n".join(result).encode("utf-8")


def build(previous: types.ModuleType, v71: types.ModuleType,
          v70: types.ModuleType, v69: types.ModuleType, modules: tuple,
          base: types.ModuleType, options: argparse.Namespace) -> tuple[dict, dict[str, bytes]]:
    base.need(options.source_sha256 is not None and options.source_bytes is not None,
              "require the complete exact V73 renderer source")
    own_raw, _ = base.read_owner(SELF, base.checked(options.source_sha256, "V73 source"),
                                 options.source_bytes, private=True)
    for role, item in V72.items():
        base.need(getattr(options, "previous_" + role + "_sha256") == item[1],
                  "require the actual published V72 predecessor " + role)
    for role, item in FEATURE.items():
        base.need(getattr(options, "feature_" + role + "_sha256") == item[1],
                  "require the complete independent Zig feature " + role)
        read_fixed(item, "independent frozen Zig " + role)
    contract_raw = read_fixed(FEATURE["contract"], "complete Zig V4 contract")
    contract = base.document(contract_raw, "complete exact Zig V4 contract")
    base.need(base.canonical(contract) == contract_raw,
              "reject altered or partially represented Zig source contract")
    validate_contract(base, contract)
    old, old_inputs = authenticate_previous(previous, v71, v70, v69, modules, base)
    proof = {
        "schema": SCHEMA + "-first-party-zig-scanner-source-v4",
        "version": 4, "family": "zig",
        "status": "SOURCE FROZEN; FIRST-PARTY ZIG VARIANT NOT BUILT OR TESTED",
        "owners": {role: base.synthetic_owner(item[:3], item[3])
                   for role, item in FEATURE.items()},
        "independent_feature_source_owner_count": 4,
        "complete_feature_contract": copy.deepcopy(contract),
        "complete_original_scanner_case_count": 1024,
        "corrected_original_scanner_case_count": 64,
        "preserved_original_scanner_case_count": 960,
        "actual_compiler_process_count": 0,
        "candidate_workers_started": 0,
        "candidate_build": "NOT RUN",
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "historical_actual_zig_matching_status": "FAIL",
        "historical_actual_zig_semantic_mismatch_count": 1764,
        "historical_actual_zig_verified_passing_case_count": 3711,
    }
    changes = {
        "actual_current_graph_predecessor_version": 72,
        "authenticated_evidence_owner_lower_bound": 243,
        "authenticated_history_reference_lower_bound": 248,
        "zig_scanner_phrase_v4_source_freeze": proof,
        "zig_scanner_phrase_v4_status": proof["status"],
        "zig_scanner_phrase_v4_complete_original_scanner_case_count": 1024,
        "zig_scanner_phrase_v4_corrected_original_scanner_case_count": 64,
        "zig_scanner_phrase_v4_preserved_original_scanner_case_count": 960,
        "zig_scanner_phrase_v4_actual_compiler_process_count": 0,
        "zig_scanner_phrase_v4_candidate_workers_started": 0,
        "zig_scanner_phrase_v4_candidate_build": "NOT RUN",
        "zig_scanner_phrase_v4_candidate_matching": "NOT RUN",
        "zig_scanner_phrase_v4_candidate_correctness": "NOT MEASURED",
        "zig_scanner_phrase_v4_candidate_qualified": False,
        "actual_zig_matching_status": "FAIL",
        "actual_zig_semantic_mismatch_count": 1764,
        "actual_zig_verified_passing_case_count": 3711,
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(copy.deepcopy(changes))
    snapshot["preserved_v72_replaced_snapshot_fields"] = {
        key: copy.deepcopy(old["snapshot"][key])
        for key in changes if key in old["snapshot"]
    }
    predecessor = {role: base.pin(item[0], item[1], item[2])
                   for role, item in V72.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({"schema": SCHEMA + "-inputs", "version": 73,
                   "python": "3.14.6", "renderer": base.pin(SELF, options.source_sha256, len(own_raw)),
                   "previous_overview": predecessor, **copy.deepcopy(changes)})
    input_raw = base.canonical(inputs)
    svg_raw = make_svg()
    families = copy.deepcopy(old["families"])
    base.need([row.get("family") for row in families]
              == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
              "preserve Python and the six genuinely distinct engine families")
    for row in families:
        if row["family"] != "python":
            row["authenticated_evidence_owner_lower_bound"] = 243
            row["authenticated_history_reference_lower_bound"] = 248
        if row["family"] == "zig":
            for key, value in changes.items():
                if key.startswith("zig_scanner_phrase_v4_") or key.startswith("actual_zig_"):
                    row[key] = copy.deepcopy(value)
    summary = copy.deepcopy(old)
    summary.update({"schema": SCHEMA + "-summary", "version": 73,
                    "status": "PASS", "python": "3.14.6",
                    "source": base.pin(SELF, options.source_sha256, len(own_raw)),
                    "inputs": base.pin(OUTPUT + ".inputs.json", base.digest(input_raw), len(input_raw)),
                    "svg": base.pin(OUTPUT + ".svg", base.digest(svg_raw), len(svg_raw)),
                    "previous_overview": predecessor, "snapshot": snapshot,
                    "families": families, **copy.deepcopy(changes)})
    suites = old["actual_complete_rust_campaign"]["complete_independently_authenticated_suite_results"]
    witnesses = old["actual_complete_rust_campaign"]["earliest_genuine_mismatch_witnesses"]
    base.need(len(suites) == 13 and len(witnesses) == 6,
              "preserve each complete original Rust suite and genuine witness")
    for name, layer in (("inputs", inputs), ("summary", summary), ("snapshot", snapshot)):
        campaign = layer["actual_complete_rust_campaign"]
        base.need(campaign["complete_independently_authenticated_suite_results"] == suites
                  and campaign["earliest_genuine_mismatch_witnesses"] == witnesses
                  and layer["zig_scanner_phrase_v4_complete_original_scanner_case_count"] == 1024
                  and layer["zig_scanner_phrase_v4_corrected_original_scanner_case_count"] == 64
                  and layer["zig_scanner_phrase_v4_preserved_original_scanner_case_count"] == 960
                  and layer["actual_zig_semantic_mismatch_count"] == 1764,
                  "preserve the entire Zig feature and genuine original evidence in " + name)
    zig = next(row for row in families if row["family"] == "zig")
    c = next(row for row in families if row["family"] == "c")
    base.need(zig["zig_scanner_phrase_v4_candidate_build"] == "NOT RUN"
              and zig["zig_scanner_phrase_v4_candidate_matching"] == "NOT RUN"
              and zig["actual_zig_semantic_mismatch_count"] == 1764
              and summary["rust_native_build_v19_status"] == "PASS"
              and summary["rust_native_build_v19_actual_compiler_process_count"] == 28
              and c["c_subject_buffer_ownership_v1_build_status"] == "PASS"
              and c["c_subject_buffer_ownership_v1_compiler_process_count"] == 14
              and summary["actual_rust_semantic_mismatch_count"] == 1440
              and summary["actual_rust_verified_passing_case_count"] == 14853
              and summary["actual_c_semantic_mismatch_count"] == 1230
              and summary["actual_c_verified_passing_case_count"] == 7325
              and summary["rust_v11_original_campaign_execution_status"] == BLOCKED
              and summary["qualified_candidate_count"] == 0
              and summary["final_holdout_opened"] is False
              and summary["runtime_no_delegation"] == "NOT ESTABLISHED"
              and summary["performance"] == "NOT MEASURED",
              "never upgrade the new Zig source repair to matching or qualification")
    return snapshot, {
        OUTPUT + ".inputs.json": input_raw,
        OUTPUT + ".json": base.canonical(summary),
        OUTPUT + ".svg": svg_raw,
    }


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(path in {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
              and type(raw) is bytes and 0 < len(raw) <= base.OWNER_LIMIT,
              "publish only the three complete V73 overview assets")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(fd, remaining)
            base.need(type(count) is int and count > 0, "publish complete V73 asset")
            remaining = remaining[count:]
        os.fsync(fd)
        owner = os.fstat(fd)
        base.need(owner.st_uid == os.geteuid() and owner.st_dev == 2064
                  and owner.st_nlink == 1 and owner.st_size == len(raw)
                  and stat.S_IMODE(owner.st_mode) == 0o600,
                  "require an exclusively published private V73 asset")
    finally:
        os.close(fd)
    directory = os.open(str(ROOT / "docs/evidence"),
                        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                        | getattr(os, "O_CLOEXEC", 0))
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    checked, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(checked == raw, "reauthenticate the complete published V73 asset")


def self_test(previous: types.ModuleType, v71: types.ModuleType,
              v70: types.ModuleType, v69: types.ModuleType,
              modules: tuple, base: types.ModuleType) -> dict:
    inherited = previous.self_test(v71, v70, v69, modules, base)
    base.need(inherited["status"] == "PASS"
              and inherited["actual_current_graph_predecessor_version"] == 71
              and inherited["authenticated_evidence_owner_lower_bound"] == 239
              and inherited["authenticated_history_reference_lower_bound"] == 244,
              "preserve all existing V72 authenticated hostile controls")
    contract = base.document(read_fixed(FEATURE["contract"], "complete Zig contract"),
                             "complete authentic Zig source contract")
    validate_contract(base, contract)
    rejected = 0
    controls: list[tuple[str, object]] = [("missing contract", None)]
    for key in contract:
        hostile = copy.deepcopy(contract)
        hostile.pop(key)
        controls.append(("missing complete Zig contract " + key, hostile))
    for label, hostile in controls:
        try:
            validate_contract(base, hostile)
        except Exception:
            rejected += 1
        else:
            base.need(False, "accepted forged first-party Zig source: " + label)
    base.need(rejected >= 21, "reject omitted complete source-only Zig obligations")
    return {
        "schema": SCHEMA + "-source-only-self-test", "version": 73,
        "status": "PASS", "previous_overview_version": 72,
        "inherited_rejected_hostile_control_count": inherited["rejected_hostile_control_count"],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": inherited["rejected_hostile_control_count"] + rejected,
        "actual_current_graph_predecessor_version": 72,
        "authenticated_evidence_owner_lower_bound": 243,
        "authenticated_history_reference_lower_bound": 248,
        "zig_scanner_phrase_v4_complete_original_scanner_case_count": 1024,
        "zig_scanner_phrase_v4_corrected_original_scanner_case_count": 64,
        "zig_scanner_phrase_v4_preserved_original_scanner_case_count": 960,
        "zig_scanner_phrase_v4_actual_compiler_process_count": 0,
        "actual_zig_semantic_mismatch_count": 1764,
        "actual_rust_semantic_mismatch_count": 1440,
        "actual_c_semantic_mismatch_count": 1230,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_compressed_evidence_owners_opened_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_hidden_cases_read_by_graph": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "final_holdout_opened": False, "performance": "NOT MEASURED",
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    for role in V72:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in FEATURE:
        parser.add_argument("--feature-" + role + "-sha256")
    for role in ("inputs", "summary", "svg"):
        parser.add_argument("--" + role + "-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, v71, v70, v69, modules, base = load_previous()
        if options.self_test:
            base.need(all(getattr(options, name) is None for name in
                          ("source_sha256", "source_bytes", "inputs_sha256",
                           "summary_sha256", "svg_sha256"))
                      and all(getattr(options, "previous_" + role + "_sha256") is None
                              for role in V72)
                      and all(getattr(options, "feature_" + role + "_sha256") is None
                              for role in FEATURE),
                      "self-test does not authorize actual graph publication")
            result = self_test(previous, v71, v70, v69, modules, base)
        else:
            snapshot, outputs = build(previous, v71, v70, v69, modules, base, options)
            if options.render:
                base.need(all(getattr(options, role + "_sha256") is None
                              for role in ("inputs", "summary", "svg")),
                          "render rejects guessed V73 output digests")
                for path, raw in outputs.items():
                    publish(base, path, raw)
            else:
                for role, suffix in (("inputs", ".inputs.json"),
                                     ("summary", ".json"), ("svg", ".svg")):
                    path = OUTPUT + suffix
                    digest = base.checked(getattr(options, role + "_sha256"),
                                          "complete current V73 " + role)
                    actual, _ = base.read_owner(path, digest, len(outputs[path]), private=True)
                    base.need(actual == outputs[path], "reproduce the complete V73 " + role)
            result = {
                "schema": SCHEMA + ("-published" if options.render
                                     else "-read-only-frozen-context"),
                "version": 73, "status": "PASS",
                "source_sha256": options.source_sha256,
                "source_bytes": options.source_bytes,
                **{role + "_sha256": base.digest(raw)
                   for role, raw in (("inputs", outputs[OUTPUT + ".inputs.json"]),
                                     ("summary", outputs[OUTPUT + ".json"]),
                                     ("svg", outputs[OUTPUT + ".svg"]))},
                "previous_overview_version": 72,
                "actual_current_graph_predecessor_version": 72,
                "authenticated_evidence_owner_lower_bound": 243,
                "authenticated_history_reference_lower_bound": 248,
                "zig_scanner_phrase_v4_complete_original_scanner_case_count": 1024,
                "zig_scanner_phrase_v4_corrected_original_scanner_case_count": 64,
                "zig_scanner_phrase_v4_preserved_original_scanner_case_count": 960,
                "zig_scanner_phrase_v4_actual_compiler_process_count": 0,
                "actual_zig_semantic_mismatch_count": 1764,
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
        sys.stderr.write("current V73 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
