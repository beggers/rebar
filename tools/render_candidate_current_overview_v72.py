#!/usr/bin/env python3
"""Report the independently rebuilt Rust engine without claiming compatibility."""

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
SELF = "tools/render_candidate_current_overview_v72.py"
OUTPUT = "docs/evidence/candidate-current-overview-v72"
SCHEMA = "rebar-candidate-current-overview-v72"
BLOCKED = "BLOCKED PENDING INDEPENDENTLY ATTESTED PRIVATE ROOT"
V71 = {
    "source": ("tools/render_candidate_current_overview_v71.py", "449bab6c62755020c31b7048f7aece37393e3e88ef4f4426e414dfe1d69aed25", 31736, 431148),
    "inputs": ("docs/evidence/candidate-current-overview-v71.inputs.json", "38a852abea0f4b96867b70326f5fbcecac08a6393c911a55ce64c78c4db2fa8b", 1123806, 431149),
    "summary": ("docs/evidence/candidate-current-overview-v71.json", "ea5809db8bfd2dd73ee00084c24cd864a6a6eb05307f67de8416a35ba8e80a84", 3147645, 431150),
    "svg": ("docs/evidence/candidate-current-overview-v71.svg", "ec3b2d82469eda70b1363f297755b4c7b4518aec43269da7582ccc1e6779a7ac", 4770, 431160),
}
STEM = "oracle/phase2/evidence/native-source-build-v19-rust-phase2-v19-rust-buffer-shape-root-provenance"
EVIDENCE = {
    "archive": (STEM + ".json.gz", "c4e3971fc207af50081d920a98d29dc06b5bdce07c5e1fb19e3e6fdf99a1c1bb", 108250, 524772),
    "build_receipt": (STEM + "-publication-receipt.json", "27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc", 3486, 524773),
    "root_receipt": (STEM + "-root-provenance-receipt.json", "de13207235055665c605cce1b88a8f2127f291b84a5954119a033c7f4e9a3c99", 4367, 524774),
}
LABEL = "phase2-v19-rust-buffer-shape-root-provenance"
BUILD_RECEIPT_KEYS = frozenset({
    "actual_compiler_process_count", "archive_bytes", "archive_directory_fsync",
    "archive_publication", "archive_relative", "archive_sha256",
    "buffer_feature_contract_sha256", "buffer_feature_protocol_sha256",
    "buffer_feature_source_sha256", "buffer_variant_sha256", "build_status",
    "candidate_correctness", "candidate_imports", "candidate_matching",
    "candidate_processes_started", "candidate_qualified", "candidate_workers_started",
    "clock_samples", "combined_bridge_bytes", "combined_bridge_overlay_apply_count",
    "combined_bridge_sha256", "confidence_intervals", "contract_sha256",
    "corrected_public_adapter_bytes", "corrected_public_adapter_overlay_apply_count",
    "corrected_public_adapter_sha256", "current_graph_version",
    "evidence_owner_lower_bound_after_publication",
    "expected_actual_compiler_process_count", "family", "global_evidence_owner_census",
    "global_history_reference_census", "hidden_cases_read",
    "historical_actual_rust_candidate_workers", "historical_actual_rust_matching_status",
    "historical_actual_rust_mismatch_count",
    "historical_actual_rust_verified_passing_case_count",
    "history_reference_lower_bound_after_publication", "holdout", "label",
    "later_append_only_evidence_allowed", "memory", "native_libraries_loaded",
    "new_actual_evidence_owner_count", "performance", "pickle_feature_contract_sha256",
    "pickle_feature_protocol_sha256", "pickle_feature_source_sha256",
    "prepublication_evidence_owner_lower_bound",
    "prepublication_history_reference_lower_bound", "protocol_sha256",
    "publication_pass_means", "schema", "source_sha256", "status",
    "timing_trials_run", "uncompressed_bytes", "uncompressed_sha256",
    "undefined_behavior", "winner_selected",
})
ROOT_RECEIPT_KEYS = frozenset({
    "actual_compiler_process_count", "actual_source_phase_count",
    "adapter_overlay_apply_count", "bridge_overlay_apply_count",
    "candidate_correctness", "candidate_matching", "candidate_qualified",
    "candidate_workers_started", "canonical_build_archive_bytes",
    "canonical_build_archive_opened", "canonical_build_archive_relative",
    "canonical_build_archive_sha256", "canonical_build_receipt_bytes",
    "canonical_build_receipt_device", "canonical_build_receipt_inode",
    "canonical_build_receipt_relative", "canonical_build_receipt_sha256",
    "canonical_build_status", "canonical_sources_modified", "clock_samples",
    "contract_sha256", "expected_compiler_process_count", "family",
    "frozen_graph_summary_sha256", "frozen_graph_version", "hidden_cases_read",
    "historical_archives_opened", "holdout", "label", "memory",
    "native_libraries_loaded", "performance", "protocol_sha256",
    "publication_pass_means", "root", "runtime_non_delegation", "schema",
    "source_sha256", "status", "tmp_directory_scanned", "undefined_behavior",
    "version", "winner_selected",
})


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
        pieces: list[bytes] = []
        remaining = size
        while remaining:
            part = os.read(fd, min(remaining, 262144))
            if not part:
                raise ValueError("reject truncated " + label)
            pieces.append(part)
            remaining -= len(part)
        if os.read(fd, 1):
            raise ValueError("reject extended " + label)
        result = b"".join(pieces)
        after = os.fstat(fd)
        if hashlib.sha256(result).hexdigest() != expected or (
            before.st_dev, before.st_ino, before.st_size, before.st_nlink,
            before.st_mtime_ns, before.st_ctime_ns,
        ) != (
            after.st_dev, after.st_ino, after.st_size, after.st_nlink,
            after.st_mtime_ns, after.st_ctime_ns,
        ):
            raise ValueError("reject changed " + label)
        return result
    finally:
        os.close(fd)


def load_previous() -> tuple[types.ModuleType, types.ModuleType, types.ModuleType, tuple, types.ModuleType]:
    raw = read_fixed(V71["source"], "genuinely published V71 renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v71")
    previous.__file__ = str(ROOT / V71["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    v70, v69, modules, base = previous.load_previous()
    base.runtime()
    base.need(previous.SCHEMA == "rebar-candidate-current-overview-v71"
              and previous.SELF == V71["source"][0],
              "authenticate only the genuinely published V71 predecessor")
    return previous, v70, v69, modules, base


def authenticate_previous(previous: types.ModuleType, v70: types.ModuleType,
                          v69: types.ModuleType, modules: tuple,
                          base: types.ModuleType) -> tuple[dict, dict]:
    values: dict[str, object] = {
        "source_sha256": V71["source"][1], "source_bytes": V71["source"][2],
        "c_receipt_sha256": previous.C_RECEIPT[1],
    }
    for role, item in previous.V70.items():
        values["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.FEATURE.items():
        values["feature_" + role + "_sha256"] = item[1]
    snapshot, pairs = previous.build(v70, v69, modules, base,
                                     argparse.Namespace(**values))
    for role in ("inputs", "summary", "svg"):
        item = V71[role]
        base.need(pairs[item[0]] == read_fixed(item, "published V71 " + role),
                  "reproduce the complete genuinely pushed V71 " + role)
    old = base.document(pairs[V71["summary"][0]], "complete pushed V71 summary")
    old_inputs = base.document(pairs[V71["inputs"][0]], "complete pushed V71 inputs")
    base.need(old["snapshot"] == snapshot and old["version"] == 71
              and old["actual_current_graph_predecessor_version"] == 70
              and old["authenticated_evidence_owner_lower_bound"] == 236
              and old["authenticated_history_reference_lower_bound"] == 241
              and old["actual_rust_semantic_mismatch_count"] == 1440
              and old["actual_rust_verified_passing_case_count"] == 14853,
              "never substitute V19's historical V70 receipt for current Rust results")
    return old, old_inputs


def stat_only_archive(base: types.ModuleType, receipt: dict,
                      provenance: dict) -> dict:
    path, fingerprint, size, inode = EVIDENCE["archive"]
    owner = os.stat(str(ROOT / path), follow_symlinks=False)
    base.need(stat.S_ISREG(owner.st_mode) and owner.st_uid == os.geteuid()
              and owner.st_dev == 2064 and owner.st_ino == inode
              and owner.st_size == size and owner.st_nlink == 1
              and stat.S_IMODE(owner.st_mode) == 0o600,
              "stat but never open the compressed V19 build evidence")
    archive = receipt["archive_publication"]
    base.need(receipt["archive_relative"] == path
              and receipt["archive_sha256"] == fingerprint
              and receipt["archive_bytes"] == size
              and archive["path"] == str(ROOT / path)
              and archive["sha256"] == fingerprint
              and archive["bytes"] == size
              and archive["inode"] == inode
              and archive["device"] == 2064
              and archive["exclusive_creation"] is True
              and archive["file_fsync_completed"] is True
              and provenance["canonical_build_archive_relative"] == path
              and provenance["canonical_build_archive_sha256"] == fingerprint
              and provenance["canonical_build_archive_bytes"] == size
              and provenance["canonical_build_archive_opened"] is False,
              "attest archive identity only from actual tiny durable receipts")
    return {"path": path, "sha256": fingerprint, "bytes": size,
            "device": 2064, "inode": inode,
            "sha256_provenance": "ATTESTED BY DURABLE BUILD RECEIPT ONLY",
            "archive_opened_by_graph": False,
            "archive_bytes_read_by_graph": 0}


def validate_evidence(base: types.ModuleType, previous: types.ModuleType,
                      receipt: object, provenance: object) -> None:
    base.need(type(receipt) is dict and type(provenance) is dict,
              "require both complete, genuinely published V19 build receipts")
    assert isinstance(receipt, dict) and isinstance(provenance, dict)
    base.need(set(receipt) == BUILD_RECEIPT_KEYS
              and set(provenance) == ROOT_RECEIPT_KEYS,
              "reject any omitted, invented, or silently weakened receipt field")
    base.need(receipt["schema"] == "rebar-phase2-owned-rust-buffer-shape-source-build-v19-durable-publication-receipt"
              and receipt["status"] == "PASS"
              and receipt["build_status"] == "PASS"
              and receipt["actual_compiler_process_count"] == 28
              and receipt["label"] == LABEL
              and receipt["source_sha256"] == previous.FEATURE["source"][1]
              and receipt["protocol_sha256"] == previous.FEATURE["protocol"][1]
              and receipt["contract_sha256"] == previous.FEATURE["contract"][1]
              and receipt["current_graph_version"] == 70
              and receipt["prepublication_evidence_owner_lower_bound"] == 233
              and receipt["prepublication_history_reference_lower_bound"] == 238
              and receipt["historical_actual_rust_mismatch_count"] == 928
              and receipt["historical_actual_rust_verified_passing_case_count"] == 8965
              and receipt["candidate_imports"] == 0
              and receipt["candidate_processes_started"] == 0
              and receipt["candidate_workers_started"] == 0
              and receipt["candidate_matching"] == "NOT RUN"
              and receipt["candidate_correctness"] == "NOT MEASURED"
              and receipt["candidate_qualified"] is False
              and receipt["native_libraries_loaded"] == 0
              and receipt["clock_samples"] == 0
              and receipt["holdout"] == "NOT OPENED",
              "reject a fabricated build or treat historical 928 cases as current")
    base.need(provenance["schema"] == "rebar-phase2-owned-rust-buffer-shape-source-build-v19-durable-root-provenance-receipt"
              and provenance["version"] == 19
              and provenance["status"] == "PASS"
              and provenance["canonical_build_status"] == "PASS"
              and provenance["actual_compiler_process_count"] == 28
              and provenance["expected_compiler_process_count"] == 28
              and provenance["actual_source_phase_count"] == 2
              and provenance["source_sha256"] == previous.FEATURE["source"][1]
              and provenance["protocol_sha256"] == previous.FEATURE["protocol"][1]
              and provenance["contract_sha256"] == previous.FEATURE["contract"][1]
              and provenance["label"] == LABEL
              and provenance["frozen_graph_version"] == 70
              and provenance["frozen_graph_summary_sha256"] == previous.V70["summary"][1]
              and provenance["canonical_build_receipt_relative"] == EVIDENCE["build_receipt"][0]
              and provenance["canonical_build_receipt_sha256"] == EVIDENCE["build_receipt"][1]
              and provenance["canonical_build_receipt_bytes"] == EVIDENCE["build_receipt"][2]
              and provenance["canonical_build_receipt_device"] == 2064
              and provenance["canonical_build_receipt_inode"] == EVIDENCE["build_receipt"][3]
              and provenance["tmp_directory_scanned"] is False
              and provenance["native_libraries_loaded"] == 0
              and provenance["candidate_workers_started"] == 0
              and provenance["candidate_matching"] == "NOT RUN"
              and provenance["candidate_correctness"] == "NOT MEASURED"
              and provenance["candidate_qualified"] is False
              and provenance["clock_samples"] == 0
              and provenance["holdout"] == "NOT OPENED"
              and provenance["runtime_non_delegation"] == "NOT ESTABLISHED",
              "bind only the actually published provenance of this exact build")
    root = provenance["root"]
    base.need(root["device"] == 2049 and root["inode"] == 11673243
              and root["uid"] == os.geteuid() and root["mode"] == "0700"
              and root["phase_count"] == 2
              and root["directory_scanned"] is False
              and root["nofollow_directory_descriptor"] is True
              and root["descriptor_opened_during_live_verification"] is True
              and root["prefix"] == "rebar-phase2-native-build-v9-rust-"
              and root["path"] == "/tmp/rebar-phase2-native-build-v9-rust-9m_y1apm",
              "use the genuine attested private device 2049 without opening its root")
    phases = root["phases"]
    base.need(type(phases) is list and len(phases) == 2
              and [phase["name"] for phase in phases] == ["reference-a", "reference-b"]
              and [phase["inode"] for phase in phases] == [11673244, 11673255]
              and all(phase["device"] == 2049 and phase["uid"] == os.geteuid()
                      and phase["mode"] == "0700" for phase in phases),
              "authenticate exactly two independently built descriptor-owned phases")
    role_outputs: dict[str, list[dict]] = {"engine": [], "bridge": []}
    for phase in phases:
        base.need(type(phase["native_outputs"]) is list
                  and len(phase["native_outputs"]) == 2,
                  "preserve both genuinely built native artifact roles")
        for artifact in phase["native_outputs"]:
            base.need(artifact["role"] in role_outputs
                      and artifact["device"] == 2049
                      and artifact["uid"] == os.geteuid()
                      and artifact["nlink"] == 1
                      and artifact["native_loaded"] is False,
                      "attest native metadata without loading or reading a native file")
            role_outputs[artifact["role"]].append(artifact)
    engine = role_outputs["engine"]
    bridge = role_outputs["bridge"]
    base.need(len(engine) == 2 and len(bridge) == 2
              and {entry["inode"] for entry in engine} == {11673291, 11673321}
              and {entry["inode"] for entry in bridge} == {11673297, 11673324}
              and all(entry["sha256"] == "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
                      and entry["bytes"] == 658344 for entry in engine)
              and all(entry["sha256"] == "7127b1b5d6e50947e34f39e6c33ff76e71a9f753473c6d5eac0f1bdf6b0e66d4"
                      and entry["bytes"] == 148832 for entry in bridge),
              "prove independently identical full engine and bridge artifacts")


def make_svg() -> bytes:
    rows = [
        ("Python re", "Correctness reference passes", "BASELINE", "#22c55e"),
        ("Rust", "Traceable build passes; 1,440 earlier differences", "NOT COMPATIBLE", "#f59e0b"),
        ("C", "Corrected build passes; 1,230 earlier differences", "NOT COMPATIBLE", "#f59e0b"),
        ("Zig", "1,764 earlier differences", "NOT COMPATIBLE", "#fb7185"),
        ("C++", "2,308 differences; five worker failures", "NOT COMPATIBLE", "#fb7185"),
        ("Go", "4,518 differences; four worker failures", "NOT COMPATIBLE", "#fb7185"),
        ("Fortran", "Full Python compatibility not tested", "NOT TESTED", "#94a3b8"),
    ]
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1060" height="570" viewBox="0 0 1060 570" role="img" aria-labelledby="title description">',
        '<title id="title">Python and six from-scratch regular-expression engines</title>',
        '<desc id="description">Python is the correctness baseline. Rust and C have reproducible first-party builds, but no replacement has passed all compatibility tests and speed has not been measured.</desc>',
        '<rect width="1060" height="570" rx="18" fill="#0b1220"/>',
        '<text x="34" y="47" fill="#f8fafc" font-size="25" font-family="system-ui,sans-serif" font-weight="700">Building a faster Python re, from scratch</text>',
        '<text x="34" y="78" fill="#cbd5e1" font-size="16" font-family="system-ui,sans-serif">6 independent engines · 0 compatible replacements · speed NOT MEASURED</text>',
        '<line x1="34" y1="99" x2="1026" y2="99" stroke="#334155"/>',
    ]
    for index, (name, detail, outcome, color) in enumerate(rows):
        y = 136 + index * 45
        out.extend([
            f'<circle cx="43" cy="{y-5}" r="6" fill="{color}"/>',
            f'<text x="62" y="{y}" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="650">{name}</text>',
            f'<text x="179" y="{y}" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">{detail}</text>',
            f'<text x="1007" y="{y}" text-anchor="end" fill="{color}" font-size="13" font-family="system-ui,sans-serif" font-weight="700">{outcome}</text>',
        ])
    out.extend([
        '<line x1="34" y1="442" x2="1026" y2="442" stroke="#334155"/>',
        '<text x="34" y="473" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">Compatibility reference: 31,237 original Python checks; 8,244 extra checks are separate.</text>',
        '<text x="34" y="500" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Traceable Rust build: PASS, 28 checks · Corrected C build: PASS, 14 checks.</text>',
        '<text x="34" y="527" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Final comparison: 4,194,304 proposed cases; NOT GENERATED, NOT OPENED, NOT MEASURED.</text>',
        '<text x="34" y="551" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 72 · independent build evidence is not a passing compatibility result.</text>',
        '</svg>', '',
    ])
    return "\n".join(out).encode("utf-8")


def build(previous: types.ModuleType, v70: types.ModuleType,
          v69: types.ModuleType, modules: tuple, base: types.ModuleType,
          options: argparse.Namespace) -> tuple[dict, dict[str, bytes]]:
    base.need(options.source_sha256 is not None and options.source_bytes is not None,
              "require the exact V72 renderer source")
    source_raw, _ = base.read_owner(SELF, base.checked(options.source_sha256, "V72 source"),
                                    options.source_bytes, private=True)
    for role, item in V71.items():
        base.need(getattr(options, "previous_" + role + "_sha256") == item[1],
                  "require complete genuinely pushed V71 predecessor " + role)
    for role, item in EVIDENCE.items():
        base.need(getattr(options, "evidence_" + role + "_sha256") == item[1],
                  "require exact genuine newly published V19 " + role)
    build_raw = read_fixed(EVIDENCE["build_receipt"], "complete tiny V19 build receipt")
    root_raw = read_fixed(EVIDENCE["root_receipt"], "complete tiny V19 root receipt")
    receipt = base.document(build_raw, "complete genuine V19 build receipt")
    provenance = base.document(root_raw, "complete genuine V19 root provenance")
    base.need(base.canonical(receipt) == build_raw
              and base.canonical(provenance) == root_raw,
              "require canonical entire actual build and provenance receipts")
    validate_evidence(base, previous, receipt, provenance)
    archive = stat_only_archive(base, receipt, provenance)
    old, old_inputs = authenticate_previous(previous, v70, v69, modules, base)
    evidence_owners = {
        role: base.synthetic_owner(item[:3], item[3])
        for role, item in EVIDENCE.items()
    }
    proof = {
        "schema": SCHEMA + "-actual-first-party-rust-v19-build",
        "version": 19, "family": "rust", "status": "PASS",
        "publication_pass_means": "INDEPENDENT ROOT-ATTESTED BUILD ONLY",
        "actual_compiler_process_count": 28,
        "independent_source_phase_count": 2,
        "independent_actual_evidence_owner_count": 3,
        "actual_evidence_owners": evidence_owners,
        "complete_build_receipt": copy.deepcopy(receipt),
        "complete_root_provenance_receipt": copy.deepcopy(provenance),
        "archive_metadata_attested_without_opening": archive,
        "historical_build_receipt_graph_version": 70,
        "historical_build_receipt_evidence_owner_lower_bound": 233,
        "historical_build_receipt_history_reference_lower_bound": 238,
        "historical_build_receipt_rust_mismatch_count": 928,
        "historical_build_receipt_rust_verified_passing_case_count": 8965,
        "latest_actual_rust_original_mismatch_count": 1440,
        "latest_actual_rust_original_verified_passing_case_count": 14853,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
    }
    changes = {
        "actual_current_graph_predecessor_version": 71,
        "authenticated_evidence_owner_lower_bound": 239,
        "authenticated_history_reference_lower_bound": 244,
        "rust_native_build_v19_actual_build": proof,
        "rust_native_build_v19_status": "PASS",
        "rust_native_build_v19_actual_compiler_process_count": 28,
        "rust_native_build_v19_compiler_process_count": 28,
        "rust_native_build_v19_independent_phase_count": 2,
        "rust_native_build_v19_actual_evidence_owner_count": 3,
        "rust_native_build_v19_private_root_provenance": "PASS",
        "rust_native_build_v19_private_root_device": 2049,
        "rust_native_build_v19_private_root_inode": 11673243,
        "rust_native_build_v19_matching_status": "NOT RUN",
        "rust_native_build_v19_candidate_correctness": "NOT MEASURED",
        "rust_native_build_v19_candidate_qualified": False,
        "rust_native_build_v19_archive_opened_by_graph": False,
        "rust_native_build_v19_archive_bytes_read_by_graph": 0,
        "rust_native_build_v19_archive_inflations_by_graph": 0,
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(copy.deepcopy(changes))
    snapshot["preserved_v71_replaced_snapshot_fields"] = {
        key: copy.deepcopy(old["snapshot"][key])
        for key in changes if key in old["snapshot"]
    }
    predecessor = {role: base.pin(item[0], item[1], item[2])
                   for role, item in V71.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({"schema": SCHEMA + "-inputs", "version": 72,
                   "python": "3.14.6", "renderer": base.pin(SELF, options.source_sha256, len(source_raw)),
                   "previous_overview": predecessor, **copy.deepcopy(changes)})
    input_raw = base.canonical(inputs)
    svg_raw = make_svg()
    families = copy.deepcopy(old["families"])
    base.need([row.get("family") for row in families]
              == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
              "preserve Python and every independent first-party engine")
    for row in families:
        if row["family"] != "python":
            row["authenticated_evidence_owner_lower_bound"] = 239
            row["authenticated_history_reference_lower_bound"] = 244
        if row["family"] == "rust":
            for key, value in changes.items():
                if key.startswith("rust_native_build_v19_"):
                    row[key] = copy.deepcopy(value)
    summary = copy.deepcopy(old)
    summary.update({"schema": SCHEMA + "-summary", "version": 72,
                    "status": "PASS", "python": "3.14.6",
                    "source": base.pin(SELF, options.source_sha256, len(source_raw)),
                    "inputs": base.pin(OUTPUT + ".inputs.json", base.digest(input_raw), len(input_raw)),
                    "svg": base.pin(OUTPUT + ".svg", base.digest(svg_raw), len(svg_raw)),
                    "previous_overview": predecessor, "snapshot": snapshot,
                    "families": families, **copy.deepcopy(changes)})
    suites = old["actual_complete_rust_campaign"]["complete_independently_authenticated_suite_results"]
    witnesses = old["actual_complete_rust_campaign"]["earliest_genuine_mismatch_witnesses"]
    base.need(len(suites) == 13 and len(witnesses) == 6,
              "retain all genuine original-suite and mismatch witness records")
    for name, layer in (("inputs", inputs), ("summary", summary), ("snapshot", snapshot)):
        campaign = layer["actual_complete_rust_campaign"]
        base.need(campaign["complete_independently_authenticated_suite_results"] == suites
                  and campaign["earliest_genuine_mismatch_witnesses"] == witnesses
                  and layer["rust_native_build_v19_status"] == "PASS"
                  and layer["rust_native_build_v19_actual_compiler_process_count"] == 28
                  and layer["rust_native_build_v19_candidate_correctness"] == "NOT MEASURED"
                  and layer["c_subject_buffer_ownership_v1_build_status"] == "PASS"
                  and layer["c_subject_buffer_ownership_v1_compiler_process_count"] == 14,
                  "retain full original and first-party build evidence in " + name)
    rust = next(row for row in families if row["family"] == "rust")
    c = next(row for row in families if row["family"] == "c")
    base.need(rust["rust_native_build_v19_status"] == "PASS"
              and rust["rust_native_build_v19_actual_compiler_process_count"] == 28
              and c["c_subject_buffer_ownership_v1_build_status"] == "PASS"
              and c["c_subject_buffer_ownership_v1_compiler_process_count"] == 14
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
              "never treat native-build success as an original-suite pass")
    return snapshot, {
        OUTPUT + ".inputs.json": input_raw,
        OUTPUT + ".json": base.canonical(summary),
        OUTPUT + ".svg": svg_raw,
    }


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(path in {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
              and type(raw) is bytes and 0 < len(raw) <= base.OWNER_LIMIT,
              "publish only the three complete V72 evidence-graph assets")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(str(ROOT / path), flags, 0o600)
    try:
        view = memoryview(raw)
        while view:
            count = os.write(fd, view)
            base.need(type(count) is int and count > 0, "publish the entire V72 asset")
            view = view[count:]
        os.fsync(fd)
        owner = os.fstat(fd)
        base.need(owner.st_uid == os.geteuid() and owner.st_dev == 2064
                  and owner.st_nlink == 1 and owner.st_size == len(raw)
                  and stat.S_IMODE(owner.st_mode) == 0o600,
                  "require a complete, exclusive, privately owned V72 asset")
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
    base.need(confirmed == raw, "reauthenticate the exact complete V72 graph asset")


def self_test(previous: types.ModuleType, v70: types.ModuleType,
              v69: types.ModuleType, modules: tuple, base: types.ModuleType) -> dict:
    inherited = previous.self_test(v70, v69, modules, base)
    base.need(inherited["status"] == "PASS"
              and inherited["actual_current_graph_predecessor_version"] == 70
              and inherited["authenticated_evidence_owner_lower_bound"] == 236
              and inherited["authenticated_history_reference_lower_bound"] == 241,
              "preserve every actual V71 source-only hostile control")
    receipt = base.document(read_fixed(EVIDENCE["build_receipt"], "tiny build receipt"),
                            "tiny genuine V19 build receipt")
    provenance = base.document(read_fixed(EVIDENCE["root_receipt"], "tiny root receipt"),
                               "tiny genuine V19 root receipt")
    validate_evidence(base, previous, receipt, provenance)
    stat_only_archive(base, receipt, provenance)
    rejected = 0
    probes = [("missing build receipt", None, provenance),
              ("missing root receipt", receipt, None)]
    for key in receipt:
        hostile = copy.deepcopy(receipt)
        hostile.pop(key)
        probes.append(("omitted actual build field " + key, hostile, provenance))
    for key in provenance:
        hostile = copy.deepcopy(provenance)
        hostile.pop(key)
        probes.append(("omitted genuine root field " + key, receipt, hostile))
    for label, bad_receipt, bad_provenance in probes:
        try:
            validate_evidence(base, previous, bad_receipt, bad_provenance)
        except Exception:
            rejected += 1
        else:
            base.need(False, "accepted forged V19 build evidence: " + label)
    base.need(rejected >= 80, "reject omitted actual build and root receipt fields")
    return {
        "schema": SCHEMA + "-source-only-self-test", "version": 72,
        "status": "PASS", "previous_overview_version": 71,
        "inherited_rejected_hostile_control_count": inherited["rejected_hostile_control_count"],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": inherited["rejected_hostile_control_count"] + rejected,
        "actual_current_graph_predecessor_version": 71,
        "authenticated_evidence_owner_lower_bound": 239,
        "authenticated_history_reference_lower_bound": 244,
        "rust_native_build_v19_status": "PASS",
        "rust_native_build_v19_actual_compiler_process_count": 28,
        "rust_native_build_v19_matching_status": "NOT RUN",
        "actual_rust_semantic_mismatch_count": 1440,
        "actual_c_semantic_mismatch_count": 1230,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_compressed_evidence_owners_opened_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_hidden_cases_read_by_graph": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "final_holdout_opened": False,
        "performance": "NOT MEASURED",
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    for role in V71:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in EVIDENCE:
        parser.add_argument("--evidence-" + role.replace("_", "-") + "-sha256")
    for role in ("inputs", "summary", "svg"):
        parser.add_argument("--" + role + "-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, v70, v69, modules, base = load_previous()
        if options.self_test:
            forbidden = ("source_sha256", "source_bytes",
                         "inputs_sha256", "summary_sha256", "svg_sha256")
            base.need(all(getattr(options, key) is None for key in forbidden)
                      and all(getattr(options, "previous_" + role + "_sha256") is None
                              for role in V71)
                      and all(getattr(options, "evidence_" + role + "_sha256") is None
                              for role in EVIDENCE),
                      "self-test accepts no graph render authority")
            result = self_test(previous, v70, v69, modules, base)
        else:
            snapshot, outputs = build(previous, v70, v69, modules, base, options)
            if options.render:
                base.need(all(getattr(options, role + "_sha256") is None
                              for role in ("inputs", "summary", "svg")),
                          "render cannot accept guessed output digests")
                for path, raw in outputs.items():
                    publish(base, path, raw)
            else:
                for role, suffix in (("inputs", ".inputs.json"),
                                     ("summary", ".json"), ("svg", ".svg")):
                    path = OUTPUT + suffix
                    expected = base.checked(getattr(options, role + "_sha256"),
                                            "complete V72 " + role)
                    actual, _ = base.read_owner(path, expected, len(outputs[path]), private=True)
                    base.need(actual == outputs[path],
                              "reproduce the complete current V72 " + role)
            result = {
                "schema": SCHEMA + ("-published" if options.render
                                     else "-read-only-frozen-context"),
                "version": 72, "status": "PASS",
                "source_sha256": options.source_sha256,
                "source_bytes": options.source_bytes,
                **{role + "_sha256": base.digest(raw)
                   for role, raw in (("inputs", outputs[OUTPUT + ".inputs.json"]),
                                     ("summary", outputs[OUTPUT + ".json"]),
                                     ("svg", outputs[OUTPUT + ".svg"]))},
                "previous_overview_version": 71,
                "actual_current_graph_predecessor_version": 71,
                "authenticated_evidence_owner_lower_bound": 239,
                "authenticated_history_reference_lower_bound": 244,
                "rust_native_build_v19_status": "PASS",
                "rust_native_build_v19_actual_compiler_process_count": 28,
                "rust_native_build_v19_matching_status": "NOT RUN",
                "rust_native_build_v19_private_root_device": 2049,
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
        sys.stderr.write("current V72 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
