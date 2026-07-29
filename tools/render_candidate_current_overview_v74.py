#!/usr/bin/env python3
"""Report the frozen clean-start guard without claiming candidate independence."""

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
SELF = "tools/render_candidate_current_overview_v74.py"
OUTPUT = "docs/evidence/candidate-current-overview-v74"
SCHEMA = "rebar-candidate-current-overview-v74"
BLOCKED = "BLOCKED PENDING INDEPENDENTLY ATTESTED PRIVATE ROOT"
V73 = {
    "source": ("tools/render_candidate_current_overview_v73.py", "484878fe7045f4fea8cf6e03cf99c6dce5e2216f28a1bfb9b10fb48b1d7fdead", 34407, 431239),
    "inputs": ("docs/evidence/candidate-current-overview-v73.inputs.json", "a83eb8d1eaf1dd70cc33df7e2664ccaf52dc93f508da048c2efe4c8f14901fc2", 1148124, 431240),
    "summary": ("docs/evidence/candidate-current-overview-v73.json", "5a44336584886dfe1ef97ad81e810407fe0df772437238918cc3ba1714bc7618", 3221471, 431241),
    "svg": ("docs/evidence/candidate-current-overview-v73.svg", "cdcdc323dddd4d3d5b77a5d75cd93e826c6cb6e480c5db5aab9d6555abfa5a31", 4769, 431245),
}
FEATURE = {
    "source": ("tools/verify_owned_candidate_runtime_independence_v1.py", "c511d72053957aaebeafe23d57c7d5438c72c00307bcbfed167a776666d0baa9", 35270, 431283),
    "protocol": ("oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V1.md", "7d0cd123f7306eb1468d65bf10ff224151752bc16d6e587576bb6a3ccb7a8795", 3464, 524839),
    "contract": ("oracle/phase2/candidate-runtime-independence-v1.json", "a784f0bc315a4cb946c09d160ed00387becd7fec9585a1e488d48a6c0f63f2fe", 3987, 524840),
}
CONTRACT_KEYS = frozenset({
    "schema", "version", "status", "source", "protocol", "current_graph",
    "phase1_v4_readiness", "first_party_candidate_families",
    "runtime_isolation_policy", "original_public_test_exceptions",
    "supplemental_obligations", "first_party_rust_native_provenance",
    "source_only_effects", "runtime_non_delegation", "holdout", "performance",
    "memory", "undefined_behavior", "qualified_candidate_count", "winner_selected",
})


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    path, digest, size, inode = item
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
            piece = os.read(fd, min(remaining, 262144))
            if not piece:
                raise ValueError("reject truncated " + label)
            pieces.append(piece)
            remaining -= len(piece)
        if os.read(fd, 1):
            raise ValueError("reject extended " + label)
        raw = b"".join(pieces)
        after = os.fstat(fd)
        if hashlib.sha256(raw).hexdigest() != digest or (
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
                              types.ModuleType, types.ModuleType, tuple,
                              types.ModuleType]:
    raw = read_fixed(V73["source"], "genuinely published V73 renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v73")
    previous.__file__ = str(ROOT / V73["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    v72, v71, v70, v69, modules, base = previous.load_previous()
    base.runtime()
    base.need(previous.SCHEMA == "rebar-candidate-current-overview-v73"
              and previous.SELF == V73["source"][0],
              "authenticate only the exact pushed Zig V73 overview")
    return previous, v72, v71, v70, v69, modules, base


def validate_contract(base: types.ModuleType, contract: object) -> None:
    base.need(type(contract) is dict and set(contract) == CONTRACT_KEYS,
              "reject omitted, fabricated, or weakened clean-runtime contract")
    assert isinstance(contract, dict)
    base.need(contract["schema"] == "rebar-owned-candidate-runtime-independence-v1-source-freeze"
              and contract["version"] == 1
              and contract["status"] == "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE"
              and contract["runtime_non_delegation"] == "NOT ESTABLISHED"
              and contract["holdout"] == "NOT OPENED"
              and contract["performance"] == "NOT MEASURED"
              and contract["memory"] == "NOT MEASURED"
              and contract["qualified_candidate_count"] == 0
              and contract["winner_selected"] is False,
              "never misstate a clean-source freeze as verified candidate runtime")
    for role in ("source", "protocol"):
        item = FEATURE[role]
        owner = contract[role]
        base.need(owner["path"] == item[0] and owner["sha256"] == item[1]
                  and owner["bytes"] == item[2] and owner["inode"] == item[3]
                  and owner["device"] == 2064 and owner["mode"] == "0600"
                  and owner["nlink"] == 1,
                  "reject substituted exact runtime guard " + role)
    graph = contract["current_graph"]
    base.need(graph["version"] == 73
              and graph["authenticated_evidence_owner_lower_bound"] == 243
              and graph["authenticated_history_reference_lower_bound"] == 248
              and type(graph["owners"]) is list and len(graph["owners"]) == 4,
              "preserve complete actually pushed V73 overview proof")
    owners = {owner["path"]: owner for owner in graph["owners"]}
    base.need(set(owners) == {item[0] for item in V73.values()},
              "reject missing, stale, or replaced current graph owner")
    for role, item in V73.items():
        owner = owners[item[0]]
        base.need(owner["sha256"] == item[1] and owner["bytes"] == item[2]
                  and owner["inode"] == item[3] and owner["device"] == 2064
                  and owner["mode"] == "0600" and owner["nlink"] == 1,
                  "reject substituted actual V73 graph " + role)
    policy = contract["runtime_isolation_policy"]
    base.need(policy["bootstrap"] == "CPython -I -B -S; audit hook before candidate import"
              and policy["candidate_alias"] == "sys.modules['re'] is the attested candidate"
              and policy["stdlib_re_engine"] == "FORBIDDEN"
              and policy["stdlib_sre_engine"] == "FORBIDDEN"
              and policy["external_regex_package"] == "FORBIDDEN"
              and policy["cross_candidate_engine"] == "FORBIDDEN"
              and policy["matching_fallback"] == "FORBIDDEN"
              and policy["guard_installed_before_candidate_import"] is True,
              "require actual pre-import denial of stdlib and external regex engines")
    exceptions = contract["original_public_test_exceptions"]
    base.need(exceptions["data_only_MAXGROUPS"] == 1073741823
              and exceptions["MAXGROUPS_module"] == "re._constants"
              and exceptions["only_fork_case"] == "ReTests.test_regression_gh94675"
              and exceptions["only_correctness_clock_case"]
                  == "ReTests.test_search_anchor_at_beginning"
              and exceptions["locale_fixture_origin"] == "SEPARATE ORACLE PROCESS ONLY"
              and exceptions["nested_interpreters"]
                  == "EACH MUST INSTALL AN INDEPENDENT GUARD",
              "do not disable or weaken actual upstream public regex tests")
    phase1 = contract["phase1_v4_readiness"]
    base.need(phase1["status"] == "PASS"
              and phase1["contract_sha256"]
                  == "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1"
              and phase1["original_case_execution_denominator"] == 31237
              and phase1["original_suite_count"] == 13
              and phase1["original_obligation_count"] == 73
              and phase1["named_private_waiver_count"] == 13
              and phase1["separate_supplemental_case_count"] == 8244,
              "preserve the entire original and independently frozen fuzz oracles")
    families = contract["first_party_candidate_families"]
    base.need(families == {
        "rust": "candidates.rust_candidate", "c": "candidates.vm_candidate",
        "zig": "candidates.zig_candidate", "cpp": "candidates.cpp_candidate",
        "go": "candidates.go_candidate", "fortran": "candidates.fortran_candidate",
    }, "preserve six separate first-party parsers, executors, and bridges")
    native = contract["first_party_rust_native_provenance"]
    base.need(native["build_receipt_sha256"]
                  == "27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc"
              and native["root_provenance_receipt_sha256"]
                  == "de13207235055665c605cce1b88a8f2127f291b84a5954119a033c7f4e9a3c99"
              and native["root_device"] == 2049
              and native["root_inode"] == 11673243
              and native["actual_compiler_process_count"] == 28
              and native["candidate_matching"] == "NOT RUN",
              "bind authentic native metadata without touching an engine or archive")
    base.need(all(value == 0 for value in contract["source_only_effects"].values()),
              "reject a source graph that runs a candidate, clock, or holdout")


def authenticate_previous(previous: types.ModuleType, v72: types.ModuleType,
                          v71: types.ModuleType, v70: types.ModuleType,
                          v69: types.ModuleType, modules: tuple,
                          base: types.ModuleType) -> tuple[dict, dict]:
    values: dict[str, object] = {
        "source_sha256": V73["source"][1], "source_bytes": V73["source"][2],
    }
    for role, item in previous.V72.items():
        values["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.FEATURE.items():
        values["feature_" + role + "_sha256"] = item[1]
    snapshot, pairs = previous.build(v72, v71, v70, v69, modules, base,
                                     argparse.Namespace(**values))
    for role in ("inputs", "summary", "svg"):
        item = V73[role]
        base.need(pairs[item[0]] == read_fixed(item, "actual pushed V73 " + role),
                  "reproduce every complete actual V73 graph " + role)
    old = base.document(pairs[V73["summary"][0]], "complete actual V73 summary")
    old_inputs = base.document(pairs[V73["inputs"][0]], "complete actual V73 inputs")
    base.need(old["snapshot"] == snapshot and old["version"] == 73
              and old["actual_current_graph_predecessor_version"] == 72
              and old["authenticated_evidence_owner_lower_bound"] == 243
              and old["authenticated_history_reference_lower_bound"] == 248
              and old["runtime_no_delegation"] == "NOT ESTABLISHED",
              "preserve complete current V73 source-only runtime blocker")
    return old, old_inputs


def make_svg() -> bytes:
    rows = [
        ("Python re", "Correctness reference passes", "BASELINE", "#22c55e"),
        ("Rust", "Build passes; 1,440 earlier differences", "NOT COMPATIBLE", "#f59e0b"),
        ("C", "Build passes; 1,230 earlier differences", "NOT COMPATIBLE", "#f59e0b"),
        ("Zig", "64 scanner fixes; 1,764 earlier differences", "NOT RETESTED", "#f59e0b"),
        ("C++", "2,308 differences; five worker failures", "NOT COMPATIBLE", "#fb7185"),
        ("Go", "4,518 differences; four worker failures", "NOT COMPATIBLE", "#fb7185"),
        ("Fortran", "Full compatibility not tested", "NOT TESTED", "#94a3b8"),
    ]
    result = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="570" viewBox="0 0 1080 570" role="img" aria-labelledby="title description">',
        '<title id="title">Python baseline and six independently implemented regex engines</title>',
        '<desc id="description">A clean-start candidate guard is frozen but no actual engine has passed runtime independence or full compatibility. No speed has been measured.</desc>',
        '<rect width="1080" height="570" rx="18" fill="#0b1220"/>',
        '<text x="34" y="47" fill="#f8fafc" font-size="25" font-family="system-ui,sans-serif" font-weight="700">Building a faster Python re, from scratch</text>',
        '<text x="34" y="78" fill="#cbd5e1" font-size="16" font-family="system-ui,sans-serif">6 independent engines · 0 compatible replacements · speed NOT MEASURED</text>',
        '<line x1="34" y1="99" x2="1046" y2="99" stroke="#334155"/>',
    ]
    for i, (name, detail, state, color) in enumerate(rows):
        y = 136 + i * 45
        result.extend([
            f'<circle cx="43" cy="{y-5}" r="6" fill="{color}"/>',
            f'<text x="62" y="{y}" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="650">{name}</text>',
            f'<text x="179" y="{y}" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">{detail}</text>',
            f'<text x="1027" y="{y}" text-anchor="end" fill="{color}" font-size="13" font-family="system-ui,sans-serif" font-weight="700">{state}</text>',
        ])
    result.extend([
        '<line x1="34" y1="442" x2="1046" y2="442" stroke="#334155"/>',
        '<text x="34" y="473" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">31,237 original Python checks; 8,244 separate extra checks; no tests removed.</text>',
        '<text x="34" y="500" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Anti-fallback guard: source self-tests PASS; actual engine independence NOT ESTABLISHED.</text>',
        '<text x="34" y="527" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Final comparison: 4,194,304 proposed cases; NOT GENERATED, NOT OPENED, NOT MEASURED.</text>',
        '<text x="34" y="551" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 74 · no external matcher, no candidate qualification, no winner.</text>',
        '</svg>', '',
    ])
    return "\n".join(result).encode("utf-8")


def build(previous: types.ModuleType, v72: types.ModuleType, v71: types.ModuleType,
          v70: types.ModuleType, v69: types.ModuleType, modules: tuple,
          base: types.ModuleType, options: argparse.Namespace) -> tuple[dict, dict[str, bytes]]:
    base.need(options.source_sha256 is not None and options.source_bytes is not None,
              "require exact V74 graph-renderer authority")
    own_raw, _ = base.read_owner(SELF, base.checked(options.source_sha256, "V74 source"),
                                 options.source_bytes, private=True)
    for role, item in V73.items():
        base.need(getattr(options, "previous_" + role + "_sha256") == item[1],
                  "require complete actually current V73 " + role)
    for role, item in FEATURE.items():
        base.need(getattr(options, "feature_" + role + "_sha256") == item[1],
                  "require frozen runtime guard exact " + role)
        read_fixed(item, "complete frozen candidate runtime guard " + role)
    contract_raw = read_fixed(FEATURE["contract"], "complete runtime guard contract")
    contract = base.document(contract_raw, "complete exact runtime guard contract")
    base.need(base.canonical(contract) == contract_raw,
              "reject duplicate-key or rewritten entire runtime policy")
    validate_contract(base, contract)
    old, old_inputs = authenticate_previous(previous, v72, v71, v70, v69,
                                            modules, base)
    proof = {
        "schema": SCHEMA + "-candidate-runtime-independence-source-v1",
        "version": 1, "status": contract["status"],
        "complete_feature_contract": copy.deepcopy(contract),
        "owners": {role: base.synthetic_owner(item[:3], item[3])
                   for role, item in FEATURE.items()},
        "independent_source_owner_count": 3,
        "candidate_workers_started": 0, "native_libraries_loaded": 0,
        "candidate_runtime_audit": "NOT RUN",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_qualified": False,
    }
    changes = {
        "actual_current_graph_predecessor_version": 73,
        "authenticated_evidence_owner_lower_bound": 246,
        "authenticated_history_reference_lower_bound": 251,
        "candidate_runtime_independence_v1_source_freeze": proof,
        "candidate_runtime_independence_v1_source_status": contract["status"],
        "candidate_runtime_independence_v1_source_owner_count": 3,
        "candidate_runtime_independence_v1_candidate_workers_started": 0,
        "candidate_runtime_independence_v1_native_libraries_loaded": 0,
        "candidate_runtime_independence_v1_runtime_audit": "NOT RUN",
        "candidate_runtime_independence_v1_runtime_no_delegation": "NOT ESTABLISHED",
        "candidate_runtime_independence_v1_candidate_qualified": False,
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(copy.deepcopy(changes))
    snapshot["preserved_v73_replaced_snapshot_fields"] = {
        key: copy.deepcopy(old["snapshot"][key])
        for key in changes if key in old["snapshot"]
    }
    predecessor = {role: base.pin(item[0], item[1], item[2])
                   for role, item in V73.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({"schema": SCHEMA + "-inputs", "version": 74,
                   "python": "3.14.6", "renderer": base.pin(SELF, options.source_sha256, len(own_raw)),
                   "previous_overview": predecessor, **copy.deepcopy(changes)})
    input_raw = base.canonical(inputs)
    svg_raw = make_svg()
    families = copy.deepcopy(old["families"])
    base.need([row.get("family") for row in families]
              == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
              "retain Python and each of the six independent engine families")
    for row in families:
        if row["family"] != "python":
            row["authenticated_evidence_owner_lower_bound"] = 246
            row["authenticated_history_reference_lower_bound"] = 251
            for key, value in changes.items():
                if key.startswith("candidate_runtime_independence_v1_"):
                    row[key] = copy.deepcopy(value)
    summary = copy.deepcopy(old)
    summary.update({"schema": SCHEMA + "-summary", "version": 74,
                    "status": "PASS", "python": "3.14.6",
                    "source": base.pin(SELF, options.source_sha256, len(own_raw)),
                    "inputs": base.pin(OUTPUT + ".inputs.json", base.digest(input_raw), len(input_raw)),
                    "svg": base.pin(OUTPUT + ".svg", base.digest(svg_raw), len(svg_raw)),
                    "previous_overview": predecessor, "snapshot": snapshot,
                    "families": families, **copy.deepcopy(changes)})
    suites = old["actual_complete_rust_campaign"]["complete_independently_authenticated_suite_results"]
    witnesses = old["actual_complete_rust_campaign"]["earliest_genuine_mismatch_witnesses"]
    base.need(len(suites) == 13 and len(witnesses) == 6,
              "preserve every original complete-suite result and genuine witness")
    for name, layer in (("inputs", inputs), ("summary", summary), ("snapshot", snapshot)):
        campaign = layer["actual_complete_rust_campaign"]
        base.need(campaign["complete_independently_authenticated_suite_results"] == suites
                  and campaign["earliest_genuine_mismatch_witnesses"] == witnesses
                  and layer["candidate_runtime_independence_v1_runtime_audit"] == "NOT RUN"
                  and layer["candidate_runtime_independence_v1_runtime_no_delegation"]
                      == "NOT ESTABLISHED"
                  and layer["candidate_runtime_independence_v1_candidate_workers_started"] == 0,
                  "retain exact original vectors and unrun guard in " + name)
    base.need(all(row["candidate_runtime_independence_v1_runtime_audit"] == "NOT RUN"
                  and row["candidate_runtime_independence_v1_runtime_no_delegation"]
                      == "NOT ESTABLISHED"
                  for row in families if row["family"] != "python")
              and summary["actual_rust_semantic_mismatch_count"] == 1440
              and summary["actual_rust_verified_passing_case_count"] == 14853
              and summary["actual_c_semantic_mismatch_count"] == 1230
              and summary["actual_c_verified_passing_case_count"] == 7325
              and summary["actual_zig_semantic_mismatch_count"] == 1764
              and summary["actual_zig_verified_passing_case_count"] == 3711
              and summary["rust_native_build_v19_status"] == "PASS"
              and summary["rust_native_build_v19_actual_compiler_process_count"] == 28
              and summary["rust_v11_original_campaign_execution_status"] == BLOCKED
              and summary["qualified_candidate_count"] == 0
              and summary["final_holdout_opened"] is False
              and summary["runtime_no_delegation"] == "NOT ESTABLISHED"
              and summary["performance"] == "NOT MEASURED",
              "never promote a source-only policy to actual matching or independence")
    return snapshot, {
        OUTPUT + ".inputs.json": input_raw,
        OUTPUT + ".json": base.canonical(summary),
        OUTPUT + ".svg": svg_raw,
    }


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(path in {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
              and type(raw) is bytes and 0 < len(raw) <= base.OWNER_LIMIT,
              "publish only complete and exclusively created V74 overview assets")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            amount = os.write(fd, remaining)
            base.need(type(amount) is int and amount > 0,
                      "write the entire complete V74 evidence asset")
            remaining = remaining[amount:]
        os.fsync(fd)
        owner = os.fstat(fd)
        base.need(owner.st_uid == os.geteuid() and owner.st_dev == 2064
                  and owner.st_nlink == 1 and owner.st_size == len(raw)
                  and stat.S_IMODE(owner.st_mode) == 0o600,
                  "require an exclusive fully synchronized V74 graph asset")
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
    base.need(confirmed == raw, "reauthenticate the entire published V74 asset")


def self_test(previous: types.ModuleType, v72: types.ModuleType,
              v71: types.ModuleType, v70: types.ModuleType,
              v69: types.ModuleType, modules: tuple,
              base: types.ModuleType) -> dict:
    prior = previous.self_test(v72, v71, v70, v69, modules, base)
    base.need(prior["status"] == "PASS"
              and prior["actual_current_graph_predecessor_version"] == 72
              and prior["authenticated_evidence_owner_lower_bound"] == 243
              and prior["authenticated_history_reference_lower_bound"] == 248,
              "preserve all authenticated V73 source hostile controls")
    contract = base.document(read_fixed(FEATURE["contract"], "full clean guard contract"),
                             "complete clean guard source contract")
    validate_contract(base, contract)
    rejected = 0
    cases: list[tuple[str, object]] = [("missing guard contract", None)]
    for key in contract:
        hostile = copy.deepcopy(contract)
        hostile.pop(key)
        cases.append(("missing complete guard evidence " + key, hostile))
    for label, forged in cases:
        try:
            validate_contract(base, forged)
        except Exception:
            rejected += 1
        else:
            base.need(False, "accepted forged runtime policy: " + label)
    base.need(rejected >= 21, "require complete guarded runtime hostile controls")
    return {
        "schema": SCHEMA + "-source-only-self-test", "version": 74,
        "status": "PASS", "previous_overview_version": 73,
        "inherited_rejected_hostile_control_count": prior["rejected_hostile_control_count"],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": prior["rejected_hostile_control_count"] + rejected,
        "actual_current_graph_predecessor_version": 73,
        "authenticated_evidence_owner_lower_bound": 246,
        "authenticated_history_reference_lower_bound": 251,
        "candidate_runtime_independence_v1_runtime_audit": "NOT RUN",
        "candidate_runtime_independence_v1_runtime_no_delegation": "NOT ESTABLISHED",
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
    for role in V73:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in FEATURE:
        parser.add_argument("--feature-" + role + "-sha256")
    for role in ("inputs", "summary", "svg"):
        parser.add_argument("--" + role + "-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, v72, v71, v70, v69, modules, base = load_previous()
        if options.self_test:
            base.need(all(getattr(options, name) is None for name in
                          ("source_sha256", "source_bytes", "inputs_sha256",
                           "summary_sha256", "svg_sha256"))
                      and all(getattr(options, "previous_" + role + "_sha256") is None
                              for role in V73)
                      and all(getattr(options, "feature_" + role + "_sha256") is None
                              for role in FEATURE),
                      "self-test cannot authorize actual V74 asset publication")
            result = self_test(previous, v72, v71, v70, v69, modules, base)
        else:
            snapshot, outputs = build(previous, v72, v71, v70, v69,
                                      modules, base, options)
            if options.render:
                base.need(all(getattr(options, role + "_sha256") is None
                              for role in ("inputs", "summary", "svg")),
                          "render rejects invented V74 output hashes")
                for path, raw in outputs.items():
                    publish(base, path, raw)
            else:
                for role, suffix in (("inputs", ".inputs.json"),
                                     ("summary", ".json"), ("svg", ".svg")):
                    path = OUTPUT + suffix
                    digest = base.checked(getattr(options, role + "_sha256"),
                                          "complete V74 " + role)
                    actual, _ = base.read_owner(path, digest, len(outputs[path]), private=True)
                    base.need(actual == outputs[path], "reproduce complete V74 " + role)
            result = {
                "schema": SCHEMA + ("-published" if options.render
                                     else "-read-only-frozen-context"),
                "version": 74, "status": "PASS",
                "source_sha256": options.source_sha256,
                "source_bytes": options.source_bytes,
                **{role + "_sha256": base.digest(raw)
                   for role, raw in (("inputs", outputs[OUTPUT + ".inputs.json"]),
                                     ("summary", outputs[OUTPUT + ".json"]),
                                     ("svg", outputs[OUTPUT + ".svg"]))},
                "previous_overview_version": 73,
                "actual_current_graph_predecessor_version": 73,
                "authenticated_evidence_owner_lower_bound": 246,
                "authenticated_history_reference_lower_bound": 251,
                "candidate_runtime_independence_v1_runtime_audit": "NOT RUN",
                "candidate_runtime_independence_v1_runtime_no_delegation": "NOT ESTABLISHED",
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
        sys.stderr.write("current V74 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
