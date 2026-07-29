#!/usr/bin/env python3
"""Render complete results for the clean first-party original-test producer."""

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
SELF = "tools/render_candidate_current_overview_v76.py"
OUTPUT = "docs/evidence/candidate-current-overview-v76"
SCHEMA = "rebar-candidate-current-overview-v76"
V75 = {
    "source": (
        "tools/render_candidate_current_overview_v75.py",
        "0610a7ba73f13eec6c9e59d766971568581b056cb54057b8dbaa95798d0c78fe",
        44198,
        431363,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v75.inputs.json",
        "5a3d9eed1e46b941c5456ff601ce04167b4d451c25ff07d9a6a2279ea54689cb",
        1164810,
        431399,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v75.json",
        "a8214d808a1edf13ba2afb6181864133415751bdaaa7e384f72a1699ad805f5f",
        3355331,
        431400,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v75.svg",
        "62763a4668c3ccbafbb0aed4e2c22533c6bf830d0e76c0ea3bb3883aa0bfb37f",
        4897,
        431401,
    ),
}
FEATURE = {
    "source": (
        "tools/run_owned_six_family_original_p0_producer_v5.py",
        "b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538",
        102286,
        431370,
    ),
    "protocol": (
        "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md",
        "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4",
        5270,
        524884,
    ),
    "contract": (
        "oracle/phase2/six-family-p0-producer-v5.json",
        "c751b8882fa331b4850271e68a1b43f965b5ddcb77c7ad0d0b4d3dec8ba79b53",
        21036,
        524885,
    ),
}
GUARD = {
    "source": (
        "tools/verify_owned_candidate_runtime_independence_v2.py",
        "f693b1576b63ae5ebe45663801834c05e7d03671a5d6f2b4beb1b62034d37c0a",
        67097,
        431371,
    ),
    "protocol": (
        "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md",
        "2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c",
        4437,
        524886,
    ),
    "contract": (
        "oracle/phase2/candidate-runtime-independence-v2.json",
        "813bbab0898d5a65a6b43533f7bfa024c4c215609c4f9fa6eb0f4cbe2791f473",
        7671,
        524887,
    ),
}
SUITES = (
    ("original_bounded_v5", 151),
    ("public_v3", 864),
    ("scanner_v3", 1024),
    ("buffer_v3", 768),
    ("managed_v1", 1024),
    ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912),
    ("substitution_v2", 5120),
    ("shape_v2", 10240),
    ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128),
    ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
FAMILIES = {
    "rust": ("candidates.rust_candidate", "candidates._rust_bridge"),
    "c": ("candidates.vm_candidate", "candidates._vm_native"),
    "zig": ("candidates.zig_candidate", "candidates._zig_bridge"),
    "cpp": ("candidates.cpp_candidate", "candidates._cpp_bridge"),
    "go": ("candidates.go_candidate", "candidates._go_bridge"),
    "fortran": ("candidates.fortran_candidate", "candidates._fortran_bridge"),
}
CONTRACT_KEYS = frozenset({
    "actual_candidate_imports",
    "actual_candidate_workers",
    "actual_reference_workers",
    "candidate_matching",
    "candidate_qualification",
    "case_execution_denominator",
    "corrected_candidate_context_public_type_reference",
    "current_graph",
    "families",
    "family_count",
    "goal_sha256",
    "guarded_nested_lifecycle",
    "holdout",
    "memory",
    "named_private_waiver_count",
    "named_private_waivers",
    "original_crosswalk_count",
    "original_obligation_count",
    "original_upstream",
    "performance",
    "phase",
    "phase_one_v4",
    "pinned_cpython",
    "previous_v4_producer",
    "protocol",
    "qualified_candidate_count",
    "runtime_bootstrap",
    "runtime_guard_v2",
    "runtime_non_delegation",
    "schema",
    "source",
    "source_owner_count",
    "status",
    "status_scope",
    "suite_count",
    "suites",
    "supplemental_case_count",
    "supplemental_cases_counted_in_original_denominator",
    "undefined_behavior",
    "verification_effects",
    "version",
    "winner_selected",
})


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    relative, expected, size, inode = item
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / relative), flags)
    try:
        before = os.fstat(descriptor)
        if not (
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_dev == 2064
            and before.st_ino == inode
            and before.st_nlink == 1
            and before.st_size == size
            and stat.S_IMODE(before.st_mode) == 0o600
        ):
            raise ValueError("reject substituted complete owner: " + label)
        blocks: list[bytes] = []
        left = size
        while left:
            block = os.read(descriptor, min(left, 262144))
            if not block:
                raise ValueError("reject truncated complete owner: " + label)
            blocks.append(block)
            left -= len(block)
        if os.read(descriptor, 1):
            raise ValueError("reject extended complete owner: " + label)
        raw = b"".join(blocks)
        after = os.fstat(descriptor)
        if hashlib.sha256(raw).hexdigest() != expected or (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_nlink,
            before.st_mtime_ns,
            before.st_ctime_ns,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_nlink,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ):
            raise ValueError("reject changed complete owner: " + label)
        return raw
    finally:
        os.close(descriptor)


def load_previous() -> tuple:
    raw = read_fixed(V75["source"], "actually pushed complete V75 renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v75")
    previous.__file__ = str(ROOT / V75["source"][0])
    previous.__package__ = ""
    exec(
        compile(raw, previous.__file__, "exec", dont_inherit=True),
        previous.__dict__,
    )
    v74, v73, v72, v71, v70, v69, modules, base = previous.load_previous()
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v75"
        and previous.SELF == V75["source"][0],
        "load only the exact independently pushed hardened V75 graph",
    )
    return previous, v74, v73, v72, v71, v70, v69, modules, base


def authenticate_previous(
    previous: types.ModuleType,
    v74: types.ModuleType,
    v73: types.ModuleType,
    v72: types.ModuleType,
    v71: types.ModuleType,
    v70: types.ModuleType,
    v69: types.ModuleType,
    modules: tuple,
    base: types.ModuleType,
) -> tuple[dict, dict]:
    pins: dict[str, object] = {
        "source_sha256": V75["source"][1],
        "source_bytes": V75["source"][2],
    }
    for role, item in previous.V74.items():
        pins["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.FEATURE.items():
        pins["feature_" + role + "_sha256"] = item[1]
    snapshot, assets = previous.build(
        v74,
        v73,
        v72,
        v71,
        v70,
        v69,
        modules,
        base,
        argparse.Namespace(**pins),
    )
    for role in ("inputs", "summary", "svg"):
        item = V75[role]
        base.need(
            assets[item[0]] == read_fixed(item, "actually pushed V75 " + role),
            "reproduce the entire hardened actual V75 " + role,
        )
    old = base.document(assets[V75["summary"][0]], "complete current V75")
    inputs = base.document(assets[V75["inputs"][0]], "complete current V75 inputs")
    base.need(
        old["snapshot"] == snapshot
        and old["version"] == 75
        and old["actual_current_graph_predecessor_version"] == 74
        and old["authenticated_evidence_owner_lower_bound"] == 249
        and old["authenticated_history_reference_lower_bound"] == 254
        and old["candidate_runtime_independence_v2_runtime_audit"] == "NOT RUN"
        and old["runtime_no_delegation"] == "NOT ESTABLISHED",
        "preserve complete genuine V75 history and the unexecuted guard",
    )
    return old, inputs


def validate_contract(base: types.ModuleType, contract: object) -> None:
    base.need(
        type(contract) is dict and set(contract) == CONTRACT_KEYS,
        "reject missing, additional, or substituted full clean-producer evidence",
    )
    assert isinstance(contract, dict)
    base.need(
        contract["schema"]
        == "rebar-owned-six-family-original-p0-producer-v5-source-freeze"
        and contract["version"] == 5
        and contract["status"]
        == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
        and contract["status_scope"]
        == "FROZEN ORIGINAL-SUITE PRODUCER ONLY; NO ACTUAL CANDIDATE RESULT"
        and contract["phase"] == "PHASE 2: CANDIDATES"
        and contract["goal_sha256"]
        == "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
        and contract["runtime_non_delegation"] == "NOT ESTABLISHED"
        and contract["candidate_matching"] == "NOT RUN"
        and contract["candidate_qualification"] == "NOT ESTABLISHED"
        and contract["qualified_candidate_count"] == 0
        and contract["winner_selected"] is False
        and contract["holdout"] == "NOT OPENED"
        and contract["performance"] == "NOT MEASURED"
        and contract["memory"] == "NOT MEASURED"
        and contract["undefined_behavior"] == "NOT MEASURED"
        and contract["actual_candidate_imports"] == 0
        and contract["actual_candidate_workers"] == 0
        and contract["actual_reference_workers"] == 0,
        "never claim actual matching or runtime proof from a source freeze",
    )
    for role in ("source", "protocol"):
        item = FEATURE[role]
        owner = contract[role]
        base.need(
            type(owner) is dict
            and set(owner) == {"path", "sha256"}
            and owner["path"] == item[0]
            and owner["sha256"] == item[1],
            "bind the exact actual clean-producer " + role,
        )
    graph = contract["current_graph"]
    base.need(
        type(graph) is dict
        and graph["version"] == 75
        and graph["authenticated_evidence_owner_lower_bound"] == 249
        and graph["authenticated_history_reference_lower_bound"] == 254,
        "authenticate only the independently committed V75 graph",
    )
    for role, item in V75.items():
        owner = graph[role]
        base.need(
            type(owner) is dict
            and owner["path"] == item[0]
            and owner["sha256"] == item[1]
            and owner["bytes"] == item[2]
            and owner["inode"] == item[3]
            and owner["device"] == 2064
            and owner["mode"] == "0600"
            and owner["nlink"] == 1,
            "reject a substituted actually current V75 " + role,
        )
    base.need(
        contract["suite_count"] == 13
        and contract["case_execution_denominator"] == 31237
        and contract["original_obligation_count"] == 73
        and contract["original_crosswalk_count"] == 34
        and contract["named_private_waiver_count"] == 13
        and type(contract["named_private_waivers"]) is list
        and len(contract["named_private_waivers"]) == 13
        and contract["supplemental_case_count"] == 8244
        and contract["supplemental_cases_counted_in_original_denominator"]
        is False,
        "preserve complete original P0 with no extra waiver or merged denominator",
    )
    suites = contract["suites"]
    base.need(
        type(suites) is list
        and len(suites) == 13
        and [
            (row["id"], row["case_execution_count"])
            for row in suites
        ]
        == list(SUITES)
        and sum(row["case_execution_count"] for row in suites) == 31237
        and all(
            set(row)
            == {
                "case_execution_count",
                "id",
                "matrix_sha256",
                "published_seed_decimal",
                "reference_records_sha256",
                "source_relative",
                "source_sha256",
                "unchanged_original_producer_route",
            }
            for row in suites
        ),
        "retain each independently pinned real original Python case and matrix",
    )
    records = contract["families"]
    base.need(
        type(records) is list
        and [row["name"] for row in records] == list(FAMILIES)
        and contract["family_count"] == 6
        and contract["source_owner_count"] == 25
        and sum(len(row["source_owners"]) for row in records) == 25,
        "preserve every separate first-party family and native source owner",
    )
    for row in records:
        family = row["name"]
        base.need(
            row["module"] == FAMILIES[family][0]
            and row["bridge_module"] == FAMILIES[family][1]
            and type(row["source_owners"]) is list
            and all(
                type(owner) is dict
                and set(owner) == {"bytes", "path", "sha256"}
                for owner in row["source_owners"]
            ),
            "bind only the independent first-party " + family + " sources",
        )
    upstream = contract["original_upstream"]
    base.need(
        type(upstream) is dict
        and upstream["all_source_ordered_method_count"] == 165
        and upstream["public_record_count"] == 152
        and upstream["runnable_public_method_count"] == 151
        and upstream["release_debug_skip_count"] == 1
        and upstream["private_waiver_count"] == 13
        and upstream["stdlib_regex_engine"] == "FORBIDDEN"
        and upstream["candidate_evaluation"]
        == "LITERAL FROZEN CPYTHON TEST SOURCE AGAINST THE GUARDED SELECTED re ALIAS"
        and type(upstream["named_private_waivers"]) is list
        and len(upstream["named_private_waivers"]) == 13,
        "require the untouched original Python test source without stdlib matching",
    )
    guard = contract["runtime_guard_v2"]
    base.need(
        type(guard) is dict
        and guard["status"]
        == "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE"
        and guard["runtime_non_delegation"] == "NOT ESTABLISHED"
        and guard["candidate_subprocesses"] == 0,
        "never convert a hardened guard source freeze into an actual runtime pass",
    )
    for role, item in GUARD.items():
        owner = guard[role]
        base.need(
            type(owner) is dict
            and owner["path"] == item[0]
            and owner["sha256"] == item[1]
            and owner["bytes"] == item[2]
            and owner["inode"] == item[3]
            and owner["device"] == 2064
            and owner["mode"] == "0600"
            and owner["nlink"] == 1,
            "pin exact actually committed hardened guard " + role,
        )
    nested = contract["guarded_nested_lifecycle"]
    base.need(
        type(nested) is dict
        and nested["suite"] == "subinterpreter_v2"
        and nested["case_count"] == 128
        and nested["case_execution_count"] == 394
        and nested["created_interpreter_count"] == 11
        and nested["destroyed_interpreter_count"] == 11
        and nested["actual_case_execution_count"] == 0
        and nested["actual_child_guards_installed"] == 0
        and nested["actual_created_interpreter_count"] == 0
        and nested["legacy_v4_bootstrap"] == "FORBIDDEN"
        and nested["legacy_v4_cleanup"]
        == "IMMUTABLE ORIGINAL SOURCE; GUARDED STACK NEVER RESTORES STDLIB"
        and nested["status"]
        == "SOURCE FROZEN; GUARDED CHILD CAMPAIGN NOT RUN"
        and nested["unrestricted_creation"] is False,
        "retain genuine guarded original children without fabricating execution",
    )
    runtime = contract["runtime_bootstrap"]
    base.need(
        type(runtime) is dict
        and runtime["python_flags"] == ["-I", "-B", "-S"]
        and runtime["candidate_module_imported_before_guard"] is False
        and runtime["candidate_subprocesses_permitted"] is False
        and runtime["cross_candidate_delegation_forbidden"] is True
        and runtime["external_regex_packages_forbidden"] is True
        and runtime["fallback_permitted"] is False
        and runtime["guard_installed_before_candidate_import"] is True
        and runtime["selected_re_alias_must_equal_candidate"] is True
        and runtime["stdlib_re_forbidden"] is True
        and runtime["stdlib_sre_forbidden"] is True
        and runtime["data_only_re_constants_maxgroups"] == 1073741823
        and runtime["external_prepared_locale_fixture_required"] is True
        and runtime["original_fork_case_scoped"] is True,
        "deny stdlib fallback, cross-family matching, and guessed locale results",
    )
    p0 = contract["phase_one_v4"]
    base.need(
        type(p0) is dict
        and p0["status"] == "PASS"
        and p0["original_case_execution_denominator"] == 31237
        and p0["suite_count"] == 13
        and p0["original_crosswalk_count"] == 34
        and p0["original_obligation_count"] == 73
        and p0["named_private_waiver_count"] == 13
        and p0["supplemental_case_count"] == 8244
        and p0["supplemental_reference_count"] == 2
        and p0["supplemental_cases_counted_in_original_denominator"] is False
        and p0["contract"]["sha256"]
        == "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
        "authenticate independently frozen P0 and both independent references",
    )
    original = contract["previous_v4_producer"]
    base.need(
        type(original) is dict
        and original["source"]["sha256"]
        == "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8"
        and original["contract"]["sha256"]
        == "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5"
        and original["nested_observer_calls"] == 0
        and original["original_observer_calls"] == 0
        and original["status"]
        == "IMMUTABLE HISTORY; NOT USED AS A CANDIDATE OBSERVER",
        "preserve, never run, the obsolete stdlib-dependent original producer",
    )
    python = contract["pinned_cpython"]
    base.need(
        type(python) is dict
        and python["version"] == "3.14.6"
        and python["path"]
        == "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
        and python["sha256"]
        == "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
        "freeze only independently verified stable CPython",
    )
    effects = contract["verification_effects"]
    base.need(
        type(effects) is dict
        and len(effects) >= 14
        and all(type(value) is int and value == 0 for value in effects.values()),
        "do not run candidates, native outputs, interpreters, or hidden cases",
    )


def make_svg() -> bytes:
    rows = [
        ("Python re", "Original Python correctness checks pass", "BASELINE", "#22c55e"),
        ("Rust", "Build passes; 1,440 earlier differences", "NOT COMPATIBLE", "#f59e0b"),
        ("C", "Build passes; 1,230 earlier differences", "NOT COMPATIBLE", "#f59e0b"),
        ("Zig", "64 scanner fixes; 1,764 earlier differences", "NOT RETESTED", "#f59e0b"),
        ("C++", "2,308 differences; five worker failures", "NOT COMPATIBLE", "#fb7185"),
        ("Go", "4,518 differences; four worker failures", "NOT COMPATIBLE", "#fb7185"),
        ("Fortran", "Full Python compatibility not tested", "NOT TESTED", "#94a3b8"),
    ]
    text = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="605" viewBox="0 0 1080 605" role="img" aria-labelledby="title description">',
        '<title id="title">Python compared with six independently written regex engines</title>',
        '<desc id="description">A clean runner now preserves every original Python test without importing Python\'s matcher into a candidate. No candidate has passed and no speed is measured.</desc>',
        '<rect width="1080" height="605" rx="18" fill="#0b1220"/>',
        '<text x="34" y="47" fill="#f8fafc" font-size="25" font-family="system-ui,sans-serif" font-weight="700">Building a faster Python re, from scratch</text>',
        '<text x="34" y="78" fill="#cbd5e1" font-size="16" font-family="system-ui,sans-serif">6 independent engines · 0 fully compatible · speed NOT MEASURED</text>',
        '<line x1="34" y1="100" x2="1046" y2="100" stroke="#334155"/>',
    ]
    for index, (name, detail, result, colour) in enumerate(rows):
        y = 137 + index * 46
        text.extend([
            f'<circle cx="43" cy="{y - 5}" r="6" fill="{colour}"/>',
            f'<text x="62" y="{y}" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="650">{name}</text>',
            f'<text x="180" y="{y}" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">{detail}</text>',
            f'<text x="1027" y="{y}" text-anchor="end" fill="{colour}" font-size="13" font-family="system-ui,sans-serif" font-weight="700">{result}</text>',
        ])
    text.extend([
        '<line x1="34" y1="449" x2="1046" y2="449" stroke="#334155"/>',
        '<text x="34" y="479" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">31,237 unchanged Python checks; 8,244 separate additional checks.</text>',
        '<text x="34" y="506" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Clean test runner frozen: no Python matcher, external engine, or candidate fallback.</text>',
        '<text x="34" y="533" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">All six engines and individually guarded child interpreters; candidate run NOT STARTED.</text>',
        '<text x="34" y="560" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Final 4,194,304-case speed test: NOT FROZEN, NOT GENERATED, NOT OPENED.</text>',
        '<text x="34" y="587" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 76 · complete original tests · no qualified candidate · no speed claims.</text>',
        "</svg>",
        "",
    ])
    return "\n".join(text).encode("utf-8")


def build(
    previous: types.ModuleType,
    v74: types.ModuleType,
    v73: types.ModuleType,
    v72: types.ModuleType,
    v71: types.ModuleType,
    v70: types.ModuleType,
    v69: types.ModuleType,
    modules: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> tuple[dict, dict[str, bytes]]:
    base.need(
        options.source_sha256 is not None and options.source_bytes is not None,
        "require exact V76 graph source authority",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "exact V76 graph source"),
        options.source_bytes,
        private=True,
    )
    for role, item in V75.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "authenticate the entire actually pushed V75 " + role,
        )
    for role, item in FEATURE.items():
        base.need(
            getattr(options, "feature_" + role + "_sha256") == item[1],
            "caller-pin the exact complete clean-test producer " + role,
        )
        read_fixed(item, "complete clean original-test producer " + role)
    raw = read_fixed(FEATURE["contract"], "full clean original-test contract")
    contract = base.document(raw, "full canonical clean original-test contract")
    base.need(
        base.canonical(contract) == raw,
        "reject omitted, noncanonical, or duplicate-key original test evidence",
    )
    validate_contract(base, contract)
    old, previous_inputs = authenticate_previous(
        previous, v74, v73, v72, v71, v70, v69, modules, base
    )
    proof = {
        "schema": SCHEMA + "-clean-original-six-family-producer-v5",
        "version": 5,
        "status": contract["status"],
        "complete_feature_contract": copy.deepcopy(contract),
        "owners": {
            role: base.synthetic_owner(item[:3], item[3])
            for role, item in FEATURE.items()
        },
        "independent_source_owner_count": 3,
        "original_suite_count": 13,
        "original_case_execution_denominator": 31237,
        "original_obligation_count": 73,
        "original_crosswalk_count": 34,
        "named_private_waiver_count": 13,
        "separate_supplemental_case_count": 8244,
        "first_party_family_count": 6,
        "first_party_source_owner_count": 25,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_subinterpreters_created": 0,
        "candidate_matching": "NOT RUN",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_qualified": False,
    }
    changes = {
        "actual_current_graph_predecessor_version": 75,
        "authenticated_evidence_owner_lower_bound": 252,
        "authenticated_history_reference_lower_bound": 257,
        "clean_original_producer_v5_source_freeze": proof,
        "clean_original_producer_v5_status": contract["status"],
        "clean_original_producer_v5_source_owner_count": 3,
        "clean_original_producer_v5_original_suite_count": 13,
        "clean_original_producer_v5_original_case_count": 31237,
        "clean_original_producer_v5_original_obligation_count": 73,
        "clean_original_producer_v5_original_crosswalk_count": 34,
        "clean_original_producer_v5_named_private_waiver_count": 13,
        "clean_original_producer_v5_separate_supplemental_case_count": 8244,
        "clean_original_producer_v5_family_count": 6,
        "clean_original_producer_v5_first_party_source_owner_count": 25,
        "clean_original_producer_v5_actual_candidate_workers": 0,
        "clean_original_producer_v5_actual_candidate_imports": 0,
        "clean_original_producer_v5_actual_child_interpreters": 0,
        "clean_original_producer_v5_candidate_matching": "NOT RUN",
        "clean_original_producer_v5_runtime_non_delegation": "NOT ESTABLISHED",
        "clean_original_producer_v5_candidate_qualified": False,
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(copy.deepcopy(changes))
    snapshot["preserved_v75_replaced_snapshot_fields"] = {
        key: copy.deepcopy(old["snapshot"][key])
        for key in changes
        if key in old["snapshot"]
    }
    predecessor = {
        role: base.pin(item[0], item[1], item[2])
        for role, item in V75.items()
    }
    inputs = copy.deepcopy(previous_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 76,
        "python": "3.14.6",
        "renderer": base.pin(SELF, options.source_sha256, len(own)),
        "previous_overview": predecessor,
        **copy.deepcopy(changes),
    })
    input_raw = base.canonical(inputs)
    svg_raw = make_svg()
    families = copy.deepcopy(old["families"])
    base.need(
        [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "preserve Python and all six actual distinct native matcher families",
    )
    for row in families:
        if row["family"] != "python":
            row["authenticated_evidence_owner_lower_bound"] = 252
            row["authenticated_history_reference_lower_bound"] = 257
            for key, value in changes.items():
                if key.startswith("clean_original_producer_v5_"):
                    row[key] = copy.deepcopy(value)
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 76,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, options.source_sha256, len(own)),
        "inputs": base.pin(
            OUTPUT + ".inputs.json", base.digest(input_raw), len(input_raw)
        ),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg_raw), len(svg_raw)),
        "previous_overview": predecessor,
        "snapshot": snapshot,
        "families": families,
        **copy.deepcopy(changes),
    })
    suites = old["actual_complete_rust_campaign"][
        "complete_independently_authenticated_suite_results"
    ]
    witnesses = old["actual_complete_rust_campaign"][
        "earliest_genuine_mismatch_witnesses"
    ]
    hardened = old["candidate_runtime_independence_v2_source_freeze"][
        "complete_feature_contract"
    ]
    base.need(
        len(suites) == 13 and len(witnesses) == 6,
        "never omit an original suite result or independently observed witness",
    )
    for name, layer in (
        ("inputs", inputs),
        ("summary", summary),
        ("snapshot", snapshot),
    ):
        campaign = layer["actual_complete_rust_campaign"]
        base.need(
            campaign["complete_independently_authenticated_suite_results"]
            == suites
            and campaign["earliest_genuine_mismatch_witnesses"] == witnesses
            and layer["clean_original_producer_v5_source_freeze"][
                "complete_feature_contract"
            ]
            == contract
            and layer["candidate_runtime_independence_v2_source_freeze"][
                "complete_feature_contract"
            ]
            == hardened
            and layer["clean_original_producer_v5_candidate_matching"]
            == "NOT RUN"
            and layer["clean_original_producer_v5_actual_candidate_workers"]
            == 0,
            "retain entire actual campaign, clean producer, and guard in " + name,
        )
    base.need(
        all(
            row["clean_original_producer_v5_source_freeze"][
                "complete_feature_contract"
            ]
            == contract
            and row["clean_original_producer_v5_candidate_matching"]
            == "NOT RUN"
            and row["candidate_runtime_independence_v2_source_freeze"][
                "complete_feature_contract"
            ]
            == hardened
            for row in families
            if row["family"] != "python"
        )
        and summary["actual_rust_semantic_mismatch_count"] == 1440
        and summary["actual_rust_verified_passing_case_count"] == 14853
        and summary["actual_c_semantic_mismatch_count"] == 1230
        and summary["actual_c_verified_passing_case_count"] == 7325
        and summary["actual_zig_semantic_mismatch_count"] == 1764
        and summary["actual_zig_verified_passing_case_count"] == 3711
        and summary["rust_native_build_v19_status"] == "PASS"
        and summary["rust_native_build_v19_actual_compiler_process_count"] == 28
        and summary["qualified_candidate_count"] == 0
        and summary["final_holdout_opened"] is False
        and summary["runtime_no_delegation"] == "NOT ESTABLISHED"
        and summary["performance"] == "NOT MEASURED",
        "never convert a clean original-source observer into actual qualification",
    )
    return snapshot, {
        OUTPUT + ".inputs.json": input_raw,
        OUTPUT + ".json": base.canonical(summary),
        OUTPUT + ".svg": svg_raw,
    }


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path
        in {
            OUTPUT + ".inputs.json",
            OUTPUT + ".json",
            OUTPUT + ".svg",
        }
        and type(raw) is bytes
        and 0 < len(raw) <= base.OWNER_LIMIT,
        "publish only independently created complete V76 overview assets",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(descriptor, remaining)
            base.need(
                type(count) is int and count > 0,
                "write every complete original-producer graph byte",
            )
            remaining = remaining[count:]
        os.fsync(descriptor)
        actual = os.fstat(descriptor)
        base.need(
            actual.st_uid == os.geteuid()
            and actual.st_dev == 2064
            and actual.st_nlink == 1
            and actual.st_size == len(raw)
            and stat.S_IMODE(actual.st_mode) == 0o600,
            "publish only an exclusively owned durable V76 evidence file",
        )
    finally:
        os.close(descriptor)
    directory = os.open(
        str(ROOT / "docs/evidence"),
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    verified, _ = base.read_owner(
        path, base.digest(raw), len(raw), private=True
    )
    base.need(verified == raw, "independently authenticate full actual V76 output")


def self_test(
    previous: types.ModuleType,
    v74: types.ModuleType,
    v73: types.ModuleType,
    v72: types.ModuleType,
    v71: types.ModuleType,
    v70: types.ModuleType,
    v69: types.ModuleType,
    modules: tuple,
    base: types.ModuleType,
) -> dict:
    prior = previous.self_test(
        v74, v73, v72, v71, v70, v69, modules, base
    )
    base.need(
        prior["status"] == "PASS"
        and prior["actual_current_graph_predecessor_version"] == 74
        and prior["authenticated_evidence_owner_lower_bound"] == 249
        and prior["authenticated_history_reference_lower_bound"] == 254,
        "inherit every independently verified hardened V75 hostile control",
    )
    raw = read_fixed(FEATURE["contract"], "complete clean producer contract")
    contract = base.document(raw, "complete canonical original-producer contract")
    base.need(
        base.canonical(contract) == raw,
        "reject noncanonical or duplicate-key clean producer evidence",
    )
    validate_contract(base, contract)
    cases: list[tuple[str, object]] = [("missing complete producer proof", None)]
    for key in sorted(contract):
        forged = copy.deepcopy(contract)
        forged.pop(key)
        cases.append(("omitted complete producer evidence " + key, forged))
    for name, wrong in (
        ("runtime_non_delegation", "PASS"),
        ("candidate_matching", "PASS"),
        ("qualified_candidate_count", 1),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("suite_count", 12),
        ("case_execution_denominator", 31236),
        ("named_private_waiver_count", 14),
        ("supplemental_cases_counted_in_original_denominator", True),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(contract)
        forged[name] = wrong
        cases.append(("fabricated clean producer result " + name, forged))
    for name, _ in SUITES:
        forged = copy.deepcopy(contract)
        forged["suites"] = [
            row for row in forged["suites"] if row["id"] != name
        ]
        cases.append(("removed original suite " + name, forged))
    for family in FAMILIES:
        forged = copy.deepcopy(contract)
        forged["families"] = [
            row for row in forged["families"] if row["name"] != family
        ]
        cases.append(("removed own native engine family " + family, forged))
    for role in GUARD:
        forged = copy.deepcopy(contract)
        forged["runtime_guard_v2"][role]["sha256"] = "0" * 64
        cases.append(("substituted hardened guard owner " + role, forged))
    for key in sorted(contract["verification_effects"]):
        forged = copy.deepcopy(contract)
        forged["verification_effects"][key] = 1
        cases.append(("invented clean-source execution " + key, forged))
    rejected = 0
    for label, forged in cases:
        try:
            validate_contract(base, forged)
        except Exception:
            rejected += 1
        else:
            base.need(False, "accepted a forged complete producer: " + label)
    base.need(
        rejected == len(cases) and rejected >= 80,
        "reject missing source ownership, test cases, native family, or guard",
    )
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "version": 76,
        "status": "PASS",
        "previous_overview_version": 75,
        "actual_current_graph_predecessor_version": 75,
        "inherited_rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": (
            prior["rejected_hostile_control_count"] + rejected
        ),
        "authenticated_evidence_owner_lower_bound": 252,
        "authenticated_history_reference_lower_bound": 257,
        "original_suite_count": 13,
        "original_case_execution_denominator": 31237,
        "original_obligation_count": 73,
        "named_private_waiver_count": 13,
        "separate_supplemental_case_count": 8244,
        "clean_first_party_family_count": 6,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_compressed_evidence_owners_opened_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_hidden_cases_read_by_graph": 0,
        "candidate_matching": "NOT RUN",
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
    for role in V75:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in FEATURE:
        parser.add_argument("--feature-" + role + "-sha256")
    for role in ("inputs", "summary", "svg"):
        parser.add_argument("--" + role + "-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, v74, v73, v72, v71, v70, v69, modules, base = load_previous()
        if options.self_test:
            base.need(
                all(
                    getattr(options, name) is None
                    for name in (
                        "source_sha256",
                        "source_bytes",
                        "inputs_sha256",
                        "summary_sha256",
                        "svg_sha256",
                    )
                )
                and all(
                    getattr(options, "previous_" + role + "_sha256") is None
                    for role in V75
                )
                and all(
                    getattr(options, "feature_" + role + "_sha256") is None
                    for role in FEATURE
                ),
                "self-test cannot authorize graphs, subprocesses, or candidates",
            )
            result = self_test(
                previous, v74, v73, v72, v71, v70, v69, modules, base
            )
        else:
            _, assets = build(
                previous,
                v74,
                v73,
                v72,
                v71,
                v70,
                v69,
                modules,
                base,
                options,
            )
            if options.render:
                base.need(
                    all(
                        getattr(options, role + "_sha256") is None
                        for role in ("inputs", "summary", "svg")
                    ),
                    "reject a rendered graph with invented output digests",
                )
                for path, raw in assets.items():
                    publish(base, path, raw)
            else:
                for role, suffix in (
                    ("inputs", ".inputs.json"),
                    ("summary", ".json"),
                    ("svg", ".svg"),
                ):
                    path = OUTPUT + suffix
                    actual, _ = base.read_owner(
                        path,
                        base.checked(
                            getattr(options, role + "_sha256"),
                            "complete published V76 " + role,
                        ),
                        len(assets[path]),
                        private=True,
                    )
                    base.need(
                        actual == assets[path],
                        "reproduce the entire frozen V76 " + role,
                    )
            result = {
                "schema": SCHEMA
                + (
                    "-published"
                    if options.render
                    else "-read-only-frozen-context"
                ),
                "version": 76,
                "status": "PASS",
                "source_sha256": options.source_sha256,
                "source_bytes": options.source_bytes,
                **{
                    role + "_sha256": base.digest(raw)
                    for role, raw in (
                        ("inputs", assets[OUTPUT + ".inputs.json"]),
                        ("summary", assets[OUTPUT + ".json"]),
                        ("svg", assets[OUTPUT + ".svg"]),
                    )
                },
                "previous_overview_version": 75,
                "actual_current_graph_predecessor_version": 75,
                "authenticated_evidence_owner_lower_bound": 252,
                "authenticated_history_reference_lower_bound": 257,
                "original_suite_count": 13,
                "original_case_execution_denominator": 31237,
                "clean_first_party_family_count": 6,
                "actual_candidate_workers_started_by_graph": 0,
                "actual_compiler_processes_started_by_graph": 0,
                "actual_compressed_evidence_owners_opened_by_graph": 0,
                "actual_clock_samples_by_graph": 0,
                "candidate_matching": "NOT RUN",
                "runtime_no_delegation": "NOT ESTABLISHED",
                "qualified_candidate_count": 0,
                "final_holdout_opened": False,
                "performance": "NOT MEASURED",
                "outputs_written": bool(options.render),
            }
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except Exception as error:
        sys.stderr.write("current V76 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
