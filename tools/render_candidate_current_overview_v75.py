#!/usr/bin/env python3
"""Render the complete current evidence without claiming an engine has passed."""

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
SELF = "tools/render_candidate_current_overview_v75.py"
OUTPUT = "docs/evidence/candidate-current-overview-v75"
SCHEMA = "rebar-candidate-current-overview-v75"
V74 = {
    "source": (
        "tools/render_candidate_current_overview_v74.py",
        "7fecafe25316c98bd6c86d6f82779250abb54ca3451abc84e04e2d8bc505d21d",
        30742,
        431284,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v74.inputs.json",
        "aa54170b8e4c426de1210f90c47b16677af80482418fb3cdf3327c173542b425",
        1153735,
        431290,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v74.json",
        "006f402dd3f8ec8150b844f8584d17d22afcd2fae99434e745bf6dbf3682a283",
        3266545,
        431315,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v74.svg",
        "1fac5fe3540dc0493e49ce581a30a04e1b843a73beddef8a876b8a6ae45a8060",
        4699,
        431316,
    ),
}
FEATURE = {
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
CONTRACT_KEYS = frozenset({
    "schema", "version", "status", "source", "protocol", "current_graph",
    "predecessor_v1", "phase1_v4_readiness", "first_party_candidate_families",
    "family_bridge_policy", "native_provenance", "subinterpreter_bootstrap",
    "original_public_test_exceptions", "supplemental_obligations",
    "source_only_effects", "runtime_isolation_policy", "runtime_non_delegation",
    "holdout", "performance", "memory", "undefined_behavior",
    "qualified_candidate_count", "winner_selected",
})
FAMILY_BRIDGES = {
    "rust": {
        "candidate_module": "candidates.rust_candidate",
        "owned_bridge_module": "candidates._rust_bridge",
    },
    "c": {
        "candidate_module": "candidates.vm_candidate",
        "owned_bridge_module": "candidates._vm_native",
    },
    "zig": {
        "candidate_module": "candidates.zig_candidate",
        "owned_bridge_module": "candidates._zig_bridge",
    },
    "cpp": {
        "candidate_module": "candidates.cpp_candidate",
        "owned_bridge_module": "candidates._cpp_bridge",
    },
    "go": {
        "candidate_module": "candidates.go_candidate",
        "owned_bridge_module": "candidates._go_bridge",
    },
    "fortran": {
        "candidate_module": "candidates.fortran_candidate",
        "owned_bridge_module": "candidates._fortran_bridge",
    },
}
V19_BUILD_RECEIPT = (
    "27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc"
)
V19_ROOT_RECEIPT = (
    "de13207235055665c605cce1b88a8f2127f291b84a5954119a033c7f4e9a3c99"
)
V19_RECEIPT_OWNERS = {
    "build_receipt": (
        "oracle/phase2/evidence/native-source-build-v19-rust-phase2-v19-rust-buffer-shape-root-provenance-publication-receipt.json",
        V19_BUILD_RECEIPT,
        3486,
        524773,
    ),
    "root_provenance_receipt": (
        "oracle/phase2/evidence/native-source-build-v19-rust-phase2-v19-rust-buffer-shape-root-provenance-root-provenance-receipt.json",
        V19_ROOT_RECEIPT,
        4367,
        524774,
    ),
}
NESTED_OWNERS = {
    "source": (
        "tools/run_owned_candidate_subinterpreters_v2.py",
        "7dd5b4a5cdfecbe6dd674632bb5cee456ee877291de88ffc76ba60472d81408a",
        98245,
        432388,
    ),
    "protocol": (
        "oracle/phase2/candidate-subinterpreters-v2.json",
        "f740da205f8431898f0a1089df5419f01612c2384def78c7d9831748ecca1b24",
        7875,
        524503,
    ),
    "explanation": (
        "oracle/phase2/CANDIDATE-SUBINTERPRETERS-V2.md",
        "c7a501f4487dfbe547c2cf8f5844be5179da035e7ae5f5e89f803234f3bf32dc",
        5390,
        524502,
    ),
}


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    path, expected, size, inode = item
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags)
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
            raise ValueError("reject substituted " + label)
        parts: list[bytes] = []
        remaining = size
        while remaining:
            part = os.read(descriptor, min(remaining, 262144))
            if not part:
                raise ValueError("reject truncated " + label)
            parts.append(part)
            remaining -= len(part)
        if os.read(descriptor, 1):
            raise ValueError("reject extended " + label)
        raw = b"".join(parts)
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
            raise ValueError("reject changed " + label)
        return raw
    finally:
        os.close(descriptor)


def contains_leaf(value: object, expected: object) -> bool:
    if type(value) is dict:
        return any(contains_leaf(item, expected) for item in value.values())
    if type(value) in (list, tuple):
        return any(contains_leaf(item, expected) for item in value)
    return type(value) is type(expected) and value == expected


def load_previous() -> tuple[
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    tuple,
    types.ModuleType,
]:
    raw = read_fixed(V74["source"], "actually published V74 renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v74")
    previous.__file__ = str(ROOT / V74["source"][0])
    previous.__package__ = ""
    exec(
        compile(raw, previous.__file__, "exec", dont_inherit=True),
        previous.__dict__,
    )
    v73, v72, v71, v70, v69, modules, base = previous.load_previous()
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v74"
        and previous.SELF == V74["source"][0],
        "authenticate only the actual, fully published V74 overview",
    )
    return previous, v73, v72, v71, v70, v69, modules, base


def authenticate_previous(
    previous: types.ModuleType,
    v73: types.ModuleType,
    v72: types.ModuleType,
    v71: types.ModuleType,
    v70: types.ModuleType,
    v69: types.ModuleType,
    modules: tuple,
    base: types.ModuleType,
) -> tuple[dict, dict]:
    options: dict[str, object] = {
        "source_sha256": V74["source"][1],
        "source_bytes": V74["source"][2],
    }
    for role, item in previous.V73.items():
        options["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.FEATURE.items():
        options["feature_" + role + "_sha256"] = item[1]
    snapshot, outputs = previous.build(
        v73, v72, v71, v70, v69, modules, base, argparse.Namespace(**options)
    )
    for role in ("inputs", "summary", "svg"):
        item = V74[role]
        base.need(
            outputs[item[0]] == read_fixed(item, "complete published V74 " + role),
            "independently reproduce the complete current V74 " + role,
        )
    old = base.document(outputs[V74["summary"][0]], "complete V74 summary")
    old_inputs = base.document(outputs[V74["inputs"][0]], "complete V74 inputs")
    base.need(
        old["snapshot"] == snapshot
        and old["version"] == 74
        and old["actual_current_graph_predecessor_version"] == 73
        and old["authenticated_evidence_owner_lower_bound"] == 246
        and old["authenticated_history_reference_lower_bound"] == 251
        and old["candidate_runtime_independence_v1_runtime_audit"] == "NOT RUN"
        and old["runtime_no_delegation"] == "NOT ESTABLISHED",
        "preserve the exact published V74 history and unexecuted first guard",
    )
    return old, old_inputs


def validate_contract(base: types.ModuleType, contract: object) -> None:
    base.need(
        type(contract) is dict and set(contract) == CONTRACT_KEYS,
        "reject omitted, added, or substituted complete V2 guard evidence",
    )
    assert isinstance(contract, dict)
    base.need(
        contract["schema"]
        == "rebar-owned-candidate-runtime-independence-v2-source-freeze"
        and contract["version"] == 2
        and contract["status"]
        == "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE"
        and contract["runtime_non_delegation"] == "NOT ESTABLISHED"
        and contract["holdout"] == "NOT OPENED"
        and contract["performance"] == "NOT MEASURED"
        and contract["memory"] == "NOT MEASURED"
        and contract["undefined_behavior"] == "NOT MEASURED"
        and contract["qualified_candidate_count"] == 0
        and contract["winner_selected"] is False,
        "never mistake a source-frozen guard for measured engine independence",
    )
    for role in ("source", "protocol"):
        item = FEATURE[role]
        owner = contract[role]
        base.need(
            type(owner) is dict
            and owner["path"] == item[0]
            and owner["sha256"] == item[1]
            and owner["bytes"] == item[2]
            and owner["inode"] == item[3]
            and owner["device"] == 2064
            and owner["mode"] == "0600"
            and owner["nlink"] == 1,
            "bind the exact fully reviewed V2 guard " + role,
        )
    graph = contract["current_graph"]
    base.need(
        type(graph) is dict
        and graph["version"] == 74
        and graph["authenticated_evidence_owner_lower_bound"] == 246
        and graph["authenticated_history_reference_lower_bound"] == 251
        and type(graph["owners"]) is list
        and len(graph["owners"]) == 4,
        "pin all four actual V74 evidence owners and both full history floors",
    )
    owners = {owner["path"]: owner for owner in graph["owners"]}
    base.need(
        set(owners) == {item[0] for item in V74.values()},
        "reject missing or substituted current V74 source or rendered asset",
    )
    for role, item in V74.items():
        owner = owners[item[0]]
        base.need(
            owner["sha256"] == item[1]
            and owner["bytes"] == item[2]
            and owner["inode"] == item[3]
            and owner["device"] == 2064
            and owner["mode"] == "0600"
            and owner["nlink"] == 1,
            "reject a replaced actual published V74 " + role,
        )
    predecessor = contract["predecessor_v1"]
    base.need(
        type(predecessor) is dict
        and contains_leaf(
            predecessor,
            "c511d72053957aaebeafe23d57c7d5438c72c00307bcbfed167a776666d0baa9",
        )
        and contains_leaf(
            predecessor,
            "7d0cd123f7306eb1468d65bf10ff224151752bc16d6e587576bb6a3ccb7a8795",
        )
        and contains_leaf(
            predecessor,
            "a784f0bc315a4cb946c09d160ed00387becd7fec9585a1e488d48a6c0f63f2fe",
        )
        and contains_leaf(predecessor, "NOT ESTABLISHED"),
        "preserve and authenticate all three first-guard owners and its limits",
    )
    families = contract["first_party_candidate_families"]
    base.need(
        families
        == {name: spec["candidate_module"] for name, spec in FAMILY_BRIDGES.items()},
        "preserve all six genuinely independent first-party engine families",
    )
    base.need(
        contract["family_bridge_policy"] == FAMILY_BRIDGES,
        "allow only the selected first-party engine and its exact own bridge",
    )
    p0 = contract["phase1_v4_readiness"]
    base.need(
        type(p0) is dict
        and p0["status"] == "PASS"
        and p0["contract_sha256"]
        == "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1"
        and p0["original_case_execution_denominator"] == 31237
        and p0["original_suite_count"] == 13
        and p0["original_obligation_count"] == 73
        and p0["named_private_waiver_count"] == 13
        and p0["separate_supplemental_case_count"] == 8244,
        "retain the full original suite and independently frozen extra checks",
    )
    native = contract["native_provenance"]
    base.need(
        type(native) is dict
        and set(native)
        == {
            "family",
            "build_version",
            "build_receipt",
            "root_provenance_receipt",
            "root_device",
            "root_inode",
            "actual_compiler_process_count",
            "attested_bridge_sha256",
            "attested_bridge_bytes",
            "attested_engine_sha256",
            "attested_engine_bytes",
            "native_load_policy",
            "source_mode_native_root_opens",
            "source_mode_native_libraries_loaded",
            "candidate_matching",
        }
        and native["family"] == "rust"
        and native["build_version"] == 19
        and native["root_device"] == 2049
        and native["root_inode"] == 11673243
        and native["actual_compiler_process_count"] == 28
        and native["attested_bridge_sha256"]
        == "7127b1b5d6e50947e34f39e6c33ff76e71a9f753473c6d5eac0f1bdf6b0e66d4"
        and native["attested_bridge_bytes"] == 148832
        and native["attested_engine_sha256"]
        == "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
        and native["attested_engine_bytes"] == 658344
        and native["native_load_policy"]
        == "ONLY SELECTED FAMILY AND EXACT ATTESTED ARTIFACT"
        and native["source_mode_native_root_opens"] == 0
        and native["source_mode_native_libraries_loaded"] == 0
        and native["candidate_matching"] == "NOT RUN",
        "pin exact independent V19 Rust provenance without touching native output",
    )
    for role, item in V19_RECEIPT_OWNERS.items():
        owner = native[role]
        base.need(
            type(owner) is dict
            and owner["path"] == item[0]
            and owner["sha256"] == item[1]
            and owner["bytes"] == item[2]
            and owner["inode"] == item[3]
            and owner["device"] == 2064
            and owner["mode"] == "0600"
            and owner["nlink"] == 1,
            "preserve the exact durable plaintext V19 " + role,
        )
    nested = contract["subinterpreter_bootstrap"]
    base.need(
        type(nested) is dict
        and set(nested)
        == {
            "suite",
            "source",
            "protocol",
            "explanation",
            "original_case_count",
            "expected_interpreters_created",
            "expected_interpreters_destroyed",
            "expected_case_interpreter_exec_calls",
            "require_child_guard_before_candidate_import",
            "unrestricted_creation",
            "actual_interpreters_created",
            "actual_interpreters_destroyed",
            "actual_case_interpreter_exec_calls",
            "actual_child_guards_installed",
            "candidate_status",
        }
        and nested["suite"] == "subinterpreter_v2"
        and nested["original_case_count"] == 128
        and nested["expected_interpreters_created"] == 11
        and nested["expected_interpreters_destroyed"] == 11
        and nested["expected_case_interpreter_exec_calls"] == 394
        and nested["require_child_guard_before_candidate_import"] is True
        and nested["unrestricted_creation"] is False
        and nested["actual_interpreters_created"] == 0
        and nested["actual_interpreters_destroyed"] == 0
        and nested["actual_case_interpreter_exec_calls"] == 0
        and nested["actual_child_guards_installed"] == 0
        and nested["candidate_status"] == "NOT RUN",
        "preserve individually guarded real nested interpreters as an unrun plan",
    )
    for role, item in NESTED_OWNERS.items():
        owner = nested[role]
        base.need(
            type(owner) is dict
            and owner["path"] == item[0]
            and owner["sha256"] == item[1]
            and owner["bytes"] == item[2]
            and owner["inode"] == item[3]
            and owner["device"] == 2064
            and owner["mode"] == "0600"
            and owner["nlink"] == 1,
            "preserve the actual frozen original nested-interpreter " + role,
        )
    exceptions = contract["original_public_test_exceptions"]
    base.need(
        type(exceptions) is dict
        and contains_leaf(exceptions, "re._constants")
        and contains_leaf(exceptions, 1073741823)
        and contains_leaf(exceptions, "ReTests.test_regression_gh94675")
        and contains_leaf(exceptions, "ReTests.test_search_anchor_at_beginning"),
        "preserve only the original data-only constant, public fork, and clock",
    )
    policy = contract["runtime_isolation_policy"]
    base.need(
        type(policy) is dict
        and policy["bootstrap"]
        == "CPython -I -B -S; audit hook before candidate import"
        and policy["candidate_alias"] == "sys.modules['re'] is the attested candidate"
        and policy["stdlib_re_engine"] == "FORBIDDEN"
        and policy["stdlib_sre_engine"] == "FORBIDDEN"
        and policy["external_regex_package"] == "FORBIDDEN"
        and policy["cross_candidate_engine"] == "FORBIDDEN"
        and policy["matching_fallback"] == "FORBIDDEN"
        and policy["guard_installed_before_candidate_import"] is True,
        "preserve fail-closed sterile bootstrap and the complete no-fallback ban",
    )
    extra = contract["supplemental_obligations"]
    base.need(
        type(extra) is dict
        and extra["callable_signature_case_count"] == 50
        and extra["candidate_supplemental_status"] == "NOT RUN"
        and extra["large_input_original_cases"] == "NOT RUN"
        and extra["separate_supplemental_case_count"] == 8244
        and extra["supplemental_merged_into_original"] is False,
        "never merge, omit, or guess supplemental and large-input test outcomes",
    )
    effects = contract["source_only_effects"]
    base.need(
        type(effects) is dict
        and set(effects)
        == {
            "candidate_imports",
            "candidate_workers_started",
            "clock_samples",
            "compiler_processes_started",
            "compressed_archives_opened",
            "hidden_cases_read",
            "holdout_cases_opened",
            "native_libraries_loaded",
            "native_roots_opened",
            "network_requests",
            "reference_workers_started",
            "subprocesses_started",
            "timing_trials_run",
        }
        and all(type(value) is int and value == 0 for value in effects.values()),
        "reject a graph feature that imports an engine or opens final test cases",
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
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="600" viewBox="0 0 1080 600" role="img" aria-labelledby="title description">',
        '<title id="title">How six original regex engines compare with Python</title>',
        '<desc id="description">Python remains the passing baseline. Six from-scratch alternatives exist, none has passed compatibility, speed has not been measured, and the improved no-fallback guard has not yet run on an engine.</desc>',
        '<rect width="1080" height="600" rx="18" fill="#0b1220"/>',
        '<text x="34" y="47" fill="#f8fafc" font-size="25" font-family="system-ui,sans-serif" font-weight="700">Building a faster Python re, from scratch</text>',
        '<text x="34" y="78" fill="#cbd5e1" font-size="16" font-family="system-ui,sans-serif">6 independent engines · 0 fully compatible · speed NOT MEASURED</text>',
        '<line x1="34" y1="100" x2="1046" y2="100" stroke="#334155"/>',
    ]
    for index, (name, detail, status, colour) in enumerate(rows):
        y = 137 + index * 46
        parts.extend([
            f'<circle cx="43" cy="{y - 5}" r="6" fill="{colour}"/>',
            f'<text x="62" y="{y}" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="650">{name}</text>',
            f'<text x="180" y="{y}" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">{detail}</text>',
            f'<text x="1027" y="{y}" text-anchor="end" fill="{colour}" font-size="13" font-family="system-ui,sans-serif" font-weight="700">{status}</text>',
        ])
    parts.extend([
        '<line x1="34" y1="449" x2="1046" y2="449" stroke="#334155"/>',
        '<text x="34" y="479" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">31,237 original Python checks; 8,244 separate additional checks.</text>',
        '<text x="34" y="506" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Improved guard: allows an engine’s own bridge; keeps Python and external regex forbidden.</text>',
        '<text x="34" y="533" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Nested-interpreter guard frozen; actual engine audit and guard use: NOT RUN.</text>',
        '<text x="34" y="560" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Final 4,194,304-case speed test: NOT FROZEN, NOT GENERATED, NOT OPENED.</text>',
        '<text x="34" y="585" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 75 · no wrapping, no qualified replacement, no speed claims.</text>',
        "</svg>",
        "",
    ])
    return "\n".join(parts).encode("utf-8")


def build(
    previous: types.ModuleType,
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
        "require exact independent V75 renderer authority",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "actual V75 renderer"),
        options.source_bytes,
        private=True,
    )
    for role, item in V74.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "require the exact complete current V74 " + role,
        )
    for role, item in FEATURE.items():
        base.need(
            getattr(options, "feature_" + role + "_sha256") == item[1],
            "pin the exact genuinely operational V2 guard " + role,
        )
        read_fixed(item, "independently frozen V2 guard " + role)
    raw = read_fixed(FEATURE["contract"], "complete canonical guard V2 contract")
    contract = base.document(raw, "complete first-party guard V2 contract")
    base.need(
        base.canonical(contract) == raw,
        "reject rewritten, partial, or duplicate-key operational guard evidence",
    )
    validate_contract(base, contract)
    old, old_inputs = authenticate_previous(
        previous, v73, v72, v71, v70, v69, modules, base
    )
    proof = {
        "schema": SCHEMA + "-candidate-runtime-independence-source-v2",
        "version": 2,
        "status": contract["status"],
        "complete_feature_contract": copy.deepcopy(contract),
        "owners": {
            role: base.synthetic_owner(item[:3], item[3])
            for role, item in FEATURE.items()
        },
        "independent_source_owner_count": 3,
        "family_bridge_policy": copy.deepcopy(FAMILY_BRIDGES),
        "subinterpreter_bootstrap": copy.deepcopy(
            contract["subinterpreter_bootstrap"]
        ),
        "candidate_workers_started": 0,
        "native_libraries_loaded": 0,
        "candidate_runtime_audit": "NOT RUN",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_qualified": False,
    }
    changes = {
        "actual_current_graph_predecessor_version": 74,
        "authenticated_evidence_owner_lower_bound": 249,
        "authenticated_history_reference_lower_bound": 254,
        "candidate_runtime_independence_v2_source_freeze": proof,
        "candidate_runtime_independence_v2_source_status": contract["status"],
        "candidate_runtime_independence_v2_source_owner_count": 3,
        "candidate_runtime_independence_v2_family_bridge_count": 6,
        "candidate_runtime_independence_v2_candidate_workers_started": 0,
        "candidate_runtime_independence_v2_native_libraries_loaded": 0,
        "candidate_runtime_independence_v2_runtime_audit": "NOT RUN",
        "candidate_runtime_independence_v2_runtime_no_delegation": (
            "NOT ESTABLISHED"
        ),
        "candidate_runtime_independence_v2_candidate_qualified": False,
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(copy.deepcopy(changes))
    snapshot["preserved_v74_replaced_snapshot_fields"] = {
        key: copy.deepcopy(old["snapshot"][key])
        for key in changes
        if key in old["snapshot"]
    }
    predecessor = {
        role: base.pin(item[0], item[1], item[2])
        for role, item in V74.items()
    }
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 75,
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
        "preserve baseline and all six distinct from-scratch engine families",
    )
    for row in families:
        if row["family"] != "python":
            row["authenticated_evidence_owner_lower_bound"] = 249
            row["authenticated_history_reference_lower_bound"] = 254
            for key, value in changes.items():
                if key.startswith("candidate_runtime_independence_v2_"):
                    row[key] = copy.deepcopy(value)
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 75,
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
    base.need(
        len(suites) == 13 and len(witnesses) == 6,
        "preserve every genuine complete original suite and mismatch witness",
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
            and layer["candidate_runtime_independence_v2_source_freeze"][
                "complete_feature_contract"
            ]
            == contract
            and layer["candidate_runtime_independence_v2_runtime_audit"]
            == "NOT RUN"
            and layer["candidate_runtime_independence_v2_runtime_no_delegation"]
            == "NOT ESTABLISHED"
            and layer["candidate_runtime_independence_v2_candidate_workers_started"]
            == 0,
            "preserve the entire original oracle and unrun V2 policy in " + name,
        )
    base.need(
        all(
            row["candidate_runtime_independence_v2_source_freeze"][
                "complete_feature_contract"
            ]
            == contract
            and row["candidate_runtime_independence_v2_runtime_audit"]
            == "NOT RUN"
            and row["candidate_runtime_independence_v2_runtime_no_delegation"]
            == "NOT ESTABLISHED"
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
        and summary["rust_v11_original_campaign_execution_status"].startswith(
            "BLOCKED"
        )
        and summary["qualified_candidate_count"] == 0
        and summary["final_holdout_opened"] is False
        and summary["runtime_no_delegation"] == "NOT ESTABLISHED"
        and summary["performance"] == "NOT MEASURED",
        "never fabricate compatibility, speed, runtime independence, or a winner",
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
        "publish only one complete, newly and exclusively created V75 graph",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            amount = os.write(descriptor, remaining)
            base.need(
                type(amount) is int and amount > 0,
                "write every byte of the actual V75 evidence asset",
            )
            remaining = remaining[amount:]
        os.fsync(descriptor)
        actual = os.fstat(descriptor)
        base.need(
            actual.st_uid == os.geteuid()
            and actual.st_dev == 2064
            and actual.st_nlink == 1
            and actual.st_size == len(raw)
            and stat.S_IMODE(actual.st_mode) == 0o600,
            "require a complete durable exclusively created V75 graph owner",
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
    confirmed, _ = base.read_owner(
        path, base.digest(raw), len(raw), private=True
    )
    base.need(
        confirmed == raw, "independently verify the entire published V75 asset"
    )


def self_test(
    previous: types.ModuleType,
    v73: types.ModuleType,
    v72: types.ModuleType,
    v71: types.ModuleType,
    v70: types.ModuleType,
    v69: types.ModuleType,
    modules: tuple,
    base: types.ModuleType,
) -> dict:
    prior = previous.self_test(v73, v72, v71, v70, v69, modules, base)
    base.need(
        prior["status"] == "PASS"
        and prior["actual_current_graph_predecessor_version"] == 73
        and prior["authenticated_evidence_owner_lower_bound"] == 246
        and prior["authenticated_history_reference_lower_bound"] == 251,
        "inherit every authenticated V74 no-fallback hostile control",
    )
    raw = read_fixed(FEATURE["contract"], "complete V2 source-only policy")
    contract = base.document(raw, "complete V2 runtime guard contract")
    base.need(
        base.canonical(contract) == raw,
        "self-test the entire canonical operational V2 source contract",
    )
    validate_contract(base, contract)
    cases: list[tuple[str, object]] = [("missing complete V2 contract", None)]
    for key in sorted(contract):
        forged = copy.deepcopy(contract)
        forged.pop(key)
        cases.append(("missing V2 contract field " + key, forged))
    for family, spec in FAMILY_BRIDGES.items():
        forged = copy.deepcopy(contract)
        replacement = next(
            other["owned_bridge_module"]
            for name, other in FAMILY_BRIDGES.items()
            if name != family
        )
        forged["family_bridge_policy"][family]["owned_bridge_module"] = (
            replacement
        )
        cases.append(("substituted cross-family native bridge " + family, forged))
        forged = copy.deepcopy(contract)
        forged["family_bridge_policy"].pop(family)
        cases.append(("missing independent engine family " + family, forged))
        forged = copy.deepcopy(contract)
        forged["first_party_candidate_families"][family] = (
            "candidates.foreign_regex"
        )
        cases.append(("substituted independently owned engine " + family, forged))
    for key, hostile in (
        ("runtime_non_delegation", "PASS"),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("qualified_candidate_count", 1),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(contract)
        forged[key] = hostile
        cases.append(("fabricated source-only outcome " + key, forged))
    for key in sorted(contract["native_provenance"]):
        forged = copy.deepcopy(contract)
        forged["native_provenance"].pop(key)
        cases.append(("omitted exact native provenance " + key, forged))
    for key in sorted(contract["subinterpreter_bootstrap"]):
        forged = copy.deepcopy(contract)
        forged["subinterpreter_bootstrap"].pop(key)
        cases.append(("omitted genuine interpreter safeguard " + key, forged))
    for key in sorted(contract["source_only_effects"]):
        forged = copy.deepcopy(contract)
        forged["source_only_effects"][key] = 1
        cases.append(("invented source-only execution " + key, forged))
    for key in (
        "stdlib_re_engine",
        "stdlib_sre_engine",
        "external_regex_package",
        "cross_candidate_engine",
        "matching_fallback",
    ):
        forged = copy.deepcopy(contract)
        forged["runtime_isolation_policy"][key] = "ALLOWED"
        cases.append(("relaxed selected-engine isolation " + key, forged))
    forged = copy.deepcopy(contract)
    forged["subinterpreter_bootstrap"]["unrestricted_creation"] = True
    cases.append(("unrestricted nested interpreter creation", forged))
    forged = copy.deepcopy(contract)
    forged["subinterpreter_bootstrap"][
        "require_child_guard_before_candidate_import"
    ] = False
    cases.append(("unguarded nested interpreter candidate import", forged))
    rejected = 0
    for label, forged in cases:
        try:
            validate_contract(base, forged)
        except Exception:
            rejected += 1
        else:
            base.need(False, "accepted hostile operational guard proof: " + label)
    base.need(
        rejected == len(cases) and rejected >= 45,
        "reject every omitted V2 owner, wrong bridge, and invented outcome",
    )
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "version": 75,
        "status": "PASS",
        "previous_overview_version": 74,
        "inherited_rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": (
            prior["rejected_hostile_control_count"] + rejected
        ),
        "actual_current_graph_predecessor_version": 74,
        "authenticated_evidence_owner_lower_bound": 249,
        "authenticated_history_reference_lower_bound": 254,
        "candidate_runtime_independence_v2_runtime_audit": "NOT RUN",
        "candidate_runtime_independence_v2_runtime_no_delegation": (
            "NOT ESTABLISHED"
        ),
        "candidate_runtime_independence_v2_family_bridge_count": 6,
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
    for role in V74:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in FEATURE:
        parser.add_argument("--feature-" + role + "-sha256")
    for role in ("inputs", "summary", "svg"):
        parser.add_argument("--" + role + "-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, v73, v72, v71, v70, v69, modules, base = load_previous()
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
                    for role in V74
                )
                and all(
                    getattr(options, "feature_" + role + "_sha256") is None
                    for role in FEATURE
                ),
                "self-tests cannot authorize graph output or engine execution",
            )
            result = self_test(
                previous, v73, v72, v71, v70, v69, modules, base
            )
        else:
            _, outputs = build(
                previous,
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
                    "graph rendering rejects invented output fingerprints",
                )
                for path, raw in outputs.items():
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
                            "complete actual V75 " + role,
                        ),
                        len(outputs[path]),
                        private=True,
                    )
                    base.need(
                        actual == outputs[path],
                        "independently reproduce the complete frozen V75 " + role,
                    )
            result = {
                "schema": SCHEMA
                + (
                    "-published"
                    if options.render
                    else "-read-only-frozen-context"
                ),
                "version": 75,
                "status": "PASS",
                "source_sha256": options.source_sha256,
                "source_bytes": options.source_bytes,
                **{
                    role + "_sha256": base.digest(raw)
                    for role, raw in (
                        ("inputs", outputs[OUTPUT + ".inputs.json"]),
                        ("summary", outputs[OUTPUT + ".json"]),
                        ("svg", outputs[OUTPUT + ".svg"]),
                    )
                },
                "previous_overview_version": 74,
                "actual_current_graph_predecessor_version": 74,
                "authenticated_evidence_owner_lower_bound": 249,
                "authenticated_history_reference_lower_bound": 254,
                "candidate_runtime_independence_v2_runtime_audit": "NOT RUN",
                "candidate_runtime_independence_v2_runtime_no_delegation": (
                    "NOT ESTABLISHED"
                ),
                "candidate_runtime_independence_v2_family_bridge_count": 6,
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
        sys.stderr.write("current V75 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
