#!/usr/bin/env python3
"""Render a genuinely runnable, guarded full-suite Rust campaign accurately."""

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
SELF = "tools/render_candidate_current_overview_v77.py"
OUTPUT = "docs/evidence/candidate-current-overview-v77"
SCHEMA = "rebar-candidate-current-overview-v77"
V76 = {
    "source": (
        "tools/render_candidate_current_overview_v76.py",
        "ac825ba68a8a8c2845569403a9b348db8d5cf1009a3d6cf8df0db1e322b53a1c",
        42970,
        431408,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v76.inputs.json",
        "3e945e54576468e9e53cc757b1f0bb64064571e3862757666152a4f1b0963e9f",
        1188201,
        431409,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v76.json",
        "a7a09e9ccfaadeffc4a49ffdb229835658b4845dfd2fc8081edd1921997d58b1",
        3542645,
        431410,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v76.svg",
        "4aabb86916a20c9dc000bd2aad5fd99b7e339f5be8f2fb44f131dd2254130f40",
        4886,
        431411,
    ),
}
FEATURE = {
    "source": (
        "tools/run_owned_repaired_rust_original_campaign_v12.py",
        "fc3a40901989bf0ccef6fe5296101c6bb456a6d3117d8b60e75c2cdf1eb113f9",
        72836,
        431362,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V12.md",
        "1473e2d1f8967f6dfd565d8e3c05dec7383e8705d624cffab2fb0c13342a1674",
        8755,
        524871,
    ),
    "contract": (
        "oracle/phase2/repaired-rust-original-campaign-v12.json",
        "6ccc0f18dbcc7ff6f401d42f5fabb199420e2a1afe79558d035efcfc607fa375",
        7240,
        524872,
    ),
}
PRODUCER = {
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
ROLE_ORDER = ("bridge_source", "adapter", "engine", "bridge")
CONTRACT_KEYS = frozenset({
    "actual_build_archive_inflations",
    "actual_build_archive_opens",
    "actual_c_semantic_mismatch_count",
    "actual_c_verified_passing_case_count",
    "actual_candidate_imports",
    "actual_candidate_workers_started",
    "actual_clock_samples",
    "actual_compiler_processes_started",
    "actual_controller_dispatch",
    "actual_hidden_cases_read",
    "actual_native_libraries_loaded",
    "actual_private_build_root_opens",
    "actual_private_build_root_stats",
    "actual_recovery_dispatch",
    "actual_rust_semantic_mismatch_count",
    "actual_rust_verified_passing_case_count",
    "actual_v19_build_archive_metadata_bytes",
    "actual_v19_build_archive_metadata_sha256",
    "actual_v19_build_contract_sha256",
    "actual_v19_build_label",
    "actual_v19_build_protocol_sha256",
    "actual_v19_build_receipt_sha256",
    "actual_v19_build_source_sha256",
    "actual_v19_compiler_process_count",
    "actual_v19_native_bridge_bytes",
    "actual_v19_native_bridge_sha256",
    "actual_v19_native_engine_bytes",
    "actual_v19_native_engine_sha256",
    "actual_v19_private_build_root",
    "actual_v19_private_build_root_device",
    "actual_v19_private_build_root_inode",
    "actual_v19_private_build_root_provenance",
    "actual_v19_root_receipt_sha256",
    "actual_v19_source_build_phase_count",
    "actual_worker_bootstrap",
    "actual_worker_dispatch",
    "candidate_correctness",
    "candidate_matching",
    "candidate_qualified",
    "case_execution_denominator",
    "confidence_intervals",
    "corrected_original_producer_contract_sha256",
    "corrected_original_producer_protocol_sha256",
    "corrected_original_producer_source_sha256",
    "corrected_original_producer_version",
    "cpython_executable",
    "cpython_executable_sha256",
    "cpython_version",
    "current_evidence_owner_lower_bound",
    "current_history_reference_lower_bound",
    "frozen_graph_inputs_sha256",
    "frozen_graph_source_sha256",
    "frozen_graph_summary_sha256",
    "frozen_graph_svg_sha256",
    "frozen_graph_version",
    "frozen_worker_implementation_contract_sha256",
    "frozen_worker_implementation_protocol_sha256",
    "frozen_worker_implementation_source",
    "frozen_worker_implementation_source_sha256",
    "goal_sha256",
    "historical_original_v4_producer_source_sha256",
    "holdout",
    "legacy_v11_original_campaign",
    "memory",
    "named_private_waivers",
    "performance",
    "phase1_v4_reference_readiness",
    "phase2_candidate_qualification",
    "planned_actual_original_candidate_worker_count",
    "private_waiver_count",
    "prospective_evidence_owner_lower_bound",
    "prospective_history_reference_lower_bound",
    "protocol_sha256",
    "public_recovery_root",
    "qualified_candidate_count",
    "recovery_lock_filename",
    "recovery_restoration_order",
    "recovery_role_order",
    "reference_cache_records_sha256",
    "reference_records_sha256",
    "reference_worker_process_ids",
    "runtime_guard_contract_sha256",
    "runtime_guard_installation",
    "runtime_guard_protocol_sha256",
    "runtime_guard_source_sha256",
    "runtime_non_delegation",
    "schema",
    "source_sha256",
    "status",
    "suite_count",
    "suites",
    "supplemental_case_count",
    "supplemental_cases_counted_in_original_denominator",
    "timing_trials_run",
    "undefined_behavior",
    "version",
    "winner_selected",
    "worker_implementation_reuse",
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
            and before.st_size == size
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600
        ):
            raise ValueError("reject substituted exact owner: " + label)
        parts: list[bytes] = []
        left = size
        while left:
            part = os.read(descriptor, min(left, 262144))
            if not part:
                raise ValueError("reject truncated exact owner: " + label)
            parts.append(part)
            left -= len(part)
        if os.read(descriptor, 1):
            raise ValueError("reject extended exact owner: " + label)
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
            raise ValueError("reject changed complete owner: " + label)
        return raw
    finally:
        os.close(descriptor)


def load_previous() -> tuple:
    raw = read_fixed(V76["source"], "genuinely pushed complete V76 renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v76")
    previous.__file__ = str(ROOT / V76["source"][0])
    previous.__package__ = ""
    exec(
        compile(raw, previous.__file__, "exec", dont_inherit=True),
        previous.__dict__,
    )
    v75, v74, v73, v72, v71, v70, v69, modules, base = previous.load_previous()
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v76"
        and previous.SELF == V76["source"][0],
        "authenticate only the actual pushed clean-original-test V76 graph",
    )
    return previous, v75, v74, v73, v72, v71, v70, v69, modules, base


def authenticate_previous(
    previous: types.ModuleType,
    v75: types.ModuleType,
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
        "source_sha256": V76["source"][1],
        "source_bytes": V76["source"][2],
    }
    for role, item in previous.V75.items():
        pins["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.FEATURE.items():
        pins["feature_" + role + "_sha256"] = item[1]
    snapshot, assets = previous.build(
        v75,
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
        item = V76[role]
        base.need(
            assets[item[0]] == read_fixed(item, "actual full V76 " + role),
            "reproduce the complete actually pushed V76 " + role,
        )
    old = base.document(assets[V76["summary"][0]], "complete actual V76")
    inputs = base.document(assets[V76["inputs"][0]], "complete V76 inputs")
    base.need(
        old["snapshot"] == snapshot
        and old["version"] == 76
        and old["actual_current_graph_predecessor_version"] == 75
        and old["authenticated_evidence_owner_lower_bound"] == 252
        and old["authenticated_history_reference_lower_bound"] == 257
        and old["clean_original_producer_v5_candidate_matching"] == "NOT RUN"
        and old["runtime_no_delegation"] == "NOT ESTABLISHED",
        "preserve the entire clean original oracle and actually unrun campaign",
    )
    return old, inputs


def validate_contract(base: types.ModuleType, contract: object) -> None:
    base.need(
        type(contract) is dict and set(contract) == CONTRACT_KEYS,
        "reject fabricated, weakened, or incomplete original Rust controller",
    )
    assert isinstance(contract, dict)
    base.need(
        contract["schema"]
        == "rebar-owned-repaired-rust-original-campaign-v12-recoverable-source-freeze"
        and contract["version"] == 12
        and contract["status"]
        == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
        and contract["source_sha256"] == FEATURE["source"][1]
        and contract["protocol_sha256"] == FEATURE["protocol"][1]
        and contract["goal_sha256"]
        == "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
        and contract["cpython_version"] == "3.14.6"
        and contract["cpython_executable"]
        == "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
        and contract["cpython_executable_sha256"]
        == "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
        "require the actual recoverable V12 source and pinned stable CPython",
    )
    base.need(
        contract["frozen_graph_version"] == 76
        and contract["frozen_graph_source_sha256"] == V76["source"][1]
        and contract["frozen_graph_inputs_sha256"] == V76["inputs"][1]
        and contract["frozen_graph_summary_sha256"] == V76["summary"][1]
        and contract["frozen_graph_svg_sha256"] == V76["svg"][1]
        and contract["current_evidence_owner_lower_bound"] == 252
        and contract["current_history_reference_lower_bound"] == 257
        and contract["prospective_evidence_owner_lower_bound"] == 255
        and contract["prospective_history_reference_lower_bound"] == 260,
        "bind current V76 and exactly three new controller source owners",
    )
    base.need(
        contract["corrected_original_producer_version"] == 5
        and contract["corrected_original_producer_source_sha256"]
        == PRODUCER["source"][1]
        and contract["corrected_original_producer_protocol_sha256"]
        == PRODUCER["protocol"][1]
        and contract["corrected_original_producer_contract_sha256"]
        == PRODUCER["contract"][1]
        and contract["historical_original_v4_producer_source_sha256"]
        == "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8",
        "run only clean V5 original cases and preserve obsolete V4 as history",
    )
    base.need(
        contract["frozen_worker_implementation_source"]
        == "tools/run_owned_repaired_rust_original_campaign_v11.py"
        and contract["frozen_worker_implementation_source_sha256"]
        == "27bf88358d5a45a5b487680e70f5fa5b5192a05f053f33f6ddb651c972c94f2d"
        and contract["frozen_worker_implementation_protocol_sha256"]
        == "a3a5b35701aa6b149ff0b4fbebb9f6722dd08436d2f7e4f600f3db12c8c6ac2b"
        and contract["frozen_worker_implementation_contract_sha256"]
        == "e6cd2028e36d8ddac0937e6735132bf474327f2ff04855d44e6aa71f5f5c0f96"
        and contract["worker_implementation_reuse"]
        == "AUTHENTICATED FIRST-PARTY V11 IN MEMORY ONLY"
        and contract["actual_controller_dispatch"]
        == "AUTHENTICATED V11 run_campaign"
        and contract["actual_worker_dispatch"]
        == "AUTHENTICATED V11 run_original_worker"
        and contract["actual_recovery_dispatch"]
        == "AUTHENTICATED V11 recover_originals"
        and contract["actual_worker_bootstrap"]
        == "CPython -I -B -S; audit hook before candidate import"
        and contract["runtime_guard_installation"]
        == "REQUIRED BEFORE ANY ACTUAL CANDIDATE IMPORT"
        and contract["phase1_v4_reference_readiness"] == "PASS"
        and contract["phase2_candidate_qualification"] == "BLOCKED"
        and contract["legacy_v11_original_campaign"] == "BLOCKED; V18-ONLY",
        "authenticate actual first-party worker dispatch without accepting a stale run",
    )
    base.need(
        contract["runtime_guard_source_sha256"] == GUARD["source"][1]
        and contract["runtime_guard_protocol_sha256"] == GUARD["protocol"][1]
        and contract["runtime_guard_contract_sha256"] == GUARD["contract"][1]
        and contract["runtime_non_delegation"] == "NOT ESTABLISHED",
        "pin the actually hardened V2 guard without inventing runtime proof",
    )
    suites = contract["suites"]
    base.need(
        type(suites) is list
        and len(suites) == 13
        and [
            (
                row.get("suite", row.get("name", row.get("id"))),
                row.get("case_count", row.get("case_execution_count")),
            )
            for row in suites
        ]
        == list(SUITES)
        and contract["suite_count"] == 13
        and contract["case_execution_denominator"] == 31237
        and contract["planned_actual_original_candidate_worker_count"] == 13
        and contract["private_waiver_count"] == 13
        and type(contract["named_private_waivers"]) is list
        and len(contract["named_private_waivers"]) == 13
        and contract["supplemental_case_count"] == 8244
        and contract["supplemental_cases_counted_in_original_denominator"]
        is False,
        "preserve every original Python case, waiver, and separate fuzz denominator",
    )
    base.need(
        contract["recovery_role_order"] == list(ROLE_ORDER)
        and contract["recovery_restoration_order"]
        == list(reversed(ROLE_ORDER))
        and type(contract["public_recovery_root"]) is str
        and contract["public_recovery_root"].startswith("/tmp/")
        and type(contract["recovery_lock_filename"]) is str,
        "require real four-role exact restoration and a unique recoverable root",
    )
    base.need(
        contract["actual_v19_build_label"]
        == "phase2-v19-rust-buffer-shape-root-provenance"
        and contract["actual_v19_build_source_sha256"]
        == "650b33a10d253e09d48a423d12c8a1bb8180af4c4e96222aa13e72c75427bb5c"
        and contract["actual_v19_build_protocol_sha256"]
        == "4cdc322b2a516b28bf771440202efaca77074f7c8cd31c25692dc6ffc81797b5"
        and contract["actual_v19_build_contract_sha256"]
        == "78e31d32cd17e100613ea98cecec4051ca2f6563b0d3b198c66f69501171ac46"
        and contract["actual_v19_build_receipt_sha256"]
        == "27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc"
        and contract["actual_v19_root_receipt_sha256"]
        == "de13207235055665c605cce1b88a8f2127f291b84a5954119a033c7f4e9a3c99"
        and contract["actual_v19_private_build_root_device"] == 2049
        and contract["actual_v19_private_build_root_inode"] == 11673243
        and contract["actual_v19_private_build_root"]
        == "/tmp/rebar-phase2-native-build-v9-rust-9m_y1apm"
        and contract["actual_v19_private_build_root_provenance"]
        == "AUTHENTICATED RECEIPT ONLY; NOT OPENED"
        and contract["actual_v19_build_archive_metadata_sha256"]
        == "c4e3971fc207af50081d920a98d29dc06b5bdce07c5e1fb19e3e6fdf99a1c1bb"
        and contract["actual_v19_build_archive_metadata_bytes"] == 108250
        and contract["actual_v19_compiler_process_count"] == 28
        and contract["actual_v19_source_build_phase_count"] == 2
        and contract["actual_v19_native_engine_sha256"]
        == "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
        and contract["actual_v19_native_engine_bytes"] == 658344
        and contract["actual_v19_native_bridge_sha256"]
        == "7127b1b5d6e50947e34f39e6c33ff76e71a9f753473c6d5eac0f1bdf6b0e66d4"
        and contract["actual_v19_native_bridge_bytes"] == 148832,
        "authenticate exact first-party V19 native provenance by tiny receipts",
    )
    for key in (
        "actual_build_archive_inflations",
        "actual_build_archive_opens",
        "actual_candidate_imports",
        "actual_candidate_workers_started",
        "actual_clock_samples",
        "actual_compiler_processes_started",
        "actual_hidden_cases_read",
        "actual_native_libraries_loaded",
        "actual_private_build_root_opens",
        "actual_private_build_root_stats",
        "timing_trials_run",
    ):
        base.need(
            contract[key] == 0,
            "source verification cannot actually execute " + key,
        )
    base.need(
        contract["candidate_correctness"] == "NOT MEASURED"
        and contract["candidate_matching"] == "NOT RUN"
        and contract["candidate_qualified"] is False
        and contract["qualified_candidate_count"] == 0
        and contract["winner_selected"] is False
        and contract["holdout"] == "NOT OPENED"
        and contract["performance"] == "NOT MEASURED"
        and contract["memory"] == "NOT MEASURED"
        and contract["undefined_behavior"] == "NOT MEASURED"
        and contract["confidence_intervals"] == "NOT MEASURED"
        and contract["actual_rust_semantic_mismatch_count"] == 1440
        and contract["actual_rust_verified_passing_case_count"] == 14853
        and contract["actual_c_semantic_mismatch_count"] == 1230
        and contract["actual_c_verified_passing_case_count"] == 7325,
        "preserve actual failures and never turn a controller into a timed pass",
    )


def make_svg() -> bytes:
    rows = [
        ("Python re", "Original Python correctness checks pass", "BASELINE", "#22c55e"),
        ("Rust", "Guarded complete rerun ready; 1,440 previous differences", "NOT RETESTED", "#f59e0b"),
        ("C", "Build passes; 1,230 previous differences", "NOT COMPATIBLE", "#f59e0b"),
        ("Zig", "64 scanner fixes; 1,764 previous differences", "NOT RETESTED", "#f59e0b"),
        ("C++", "2,308 differences; five worker failures", "NOT COMPATIBLE", "#fb7185"),
        ("Go", "4,518 differences; four worker failures", "NOT COMPATIBLE", "#fb7185"),
        ("Fortran", "Full Python compatibility not tested", "NOT TESTED", "#94a3b8"),
    ]
    items = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="610" viewBox="0 0 1080 610" role="img" aria-labelledby="title description">',
        '<title id="title">Six first-party regex engines compared with Python</title>',
        '<desc id="description">A genuinely executable guarded Rust rerun is frozen but has not run. Existing compatibility failures remain visible. Speed is not measured.</desc>',
        '<rect width="1080" height="610" rx="18" fill="#0b1220"/>',
        '<text x="34" y="47" fill="#f8fafc" font-size="25" font-family="system-ui,sans-serif" font-weight="700">Building a faster Python re, from scratch</text>',
        '<text x="34" y="78" fill="#cbd5e1" font-size="16" font-family="system-ui,sans-serif">6 independent engines · 0 fully compatible · speed NOT MEASURED</text>',
        '<line x1="34" y1="100" x2="1046" y2="100" stroke="#334155"/>',
    ]
    for index, (name, detail, result, colour) in enumerate(rows):
        y = 137 + index * 46
        items.extend([
            f'<circle cx="43" cy="{y - 5}" r="6" fill="{colour}"/>',
            f'<text x="62" y="{y}" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="650">{name}</text>',
            f'<text x="180" y="{y}" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">{detail}</text>',
            f'<text x="1027" y="{y}" text-anchor="end" fill="{colour}" font-size="13" font-family="system-ui,sans-serif" font-weight="700">{result}</text>',
        ])
    items.extend([
        '<line x1="34" y1="449" x2="1046" y2="449" stroke="#334155"/>',
        '<text x="34" y="480" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">31,237 original Python checks; 8,244 separate additional checks.</text>',
        '<text x="34" y="508" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Guarded Rust runner: 13 complete original test groups; actual rerun NOT STARTED.</text>',
        '<text x="34" y="536" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">No fallback to Python, external regex packages, or another candidate.</text>',
        '<text x="34" y="564" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">Final 4,194,304-case speed test: NOT FROZEN, NOT GENERATED, NOT OPENED.</text>',
        '<text x="34" y="591" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 77 · genuine runner frozen · no measured winner.</text>',
        "</svg>",
        "",
    ])
    return "\n".join(items).encode("utf-8")


def build(
    previous: types.ModuleType,
    v75: types.ModuleType,
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
        "require complete caller-pinned V77 graph source",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "complete V77 graph renderer"),
        options.source_bytes,
        private=True,
    )
    for role, item in V76.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "require actually pushed complete V76 " + role,
        )
    for role, item in FEATURE.items():
        base.need(
            getattr(options, "feature_" + role + "_sha256") == item[1],
            "caller-pin the genuinely runnable actual Rust controller " + role,
        )
        read_fixed(item, "full real Rust controller source freeze " + role)
    raw = read_fixed(FEATURE["contract"], "complete canonical real runner policy")
    contract = base.document(raw, "complete canonical real Rust controller")
    base.need(
        base.canonical(contract) == raw,
        "reject rewritten, partial, or duplicate-key Rust controller evidence",
    )
    validate_contract(base, contract)
    old, previous_inputs = authenticate_previous(
        previous, v75, v74, v73, v72, v71, v70, v69, modules, base
    )
    proof = {
        "schema": SCHEMA + "-guarded-rust-original-campaign-v12",
        "version": 12,
        "status": contract["status"],
        "complete_feature_contract": copy.deepcopy(contract),
        "owners": {
            role: base.synthetic_owner(item[:3], item[3])
            for role, item in FEATURE.items()
        },
        "independent_source_owner_count": 3,
        "planned_actual_original_candidate_worker_count": 13,
        "original_case_execution_denominator": 31237,
        "recovery_role_order": list(ROLE_ORDER),
        "recovery_restoration_order": list(reversed(ROLE_ORDER)),
        "actual_candidate_workers_started": 0,
        "actual_build_archive_opens": 0,
        "actual_native_libraries_loaded": 0,
        "candidate_matching": "NOT RUN",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_qualified": False,
    }
    changes = {
        "actual_current_graph_predecessor_version": 76,
        "authenticated_evidence_owner_lower_bound": 255,
        "authenticated_history_reference_lower_bound": 260,
        "rust_v12_original_campaign_source_freeze": proof,
        "rust_v12_original_campaign_source_status": contract["status"],
        "rust_v12_original_campaign_source_owner_count": 3,
        "rust_v12_original_campaign_planned_worker_count": 13,
        "rust_v12_original_campaign_original_case_count": 31237,
        "rust_v12_original_campaign_actual_worker_count": 0,
        "rust_v12_original_campaign_actual_native_load_count": 0,
        "rust_v12_original_campaign_actual_archive_open_count": 0,
        "rust_v12_original_campaign_candidate_matching": "NOT RUN",
        "rust_v12_original_campaign_runtime_no_delegation": "NOT ESTABLISHED",
        "rust_v12_original_campaign_candidate_qualified": False,
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(copy.deepcopy(changes))
    snapshot["preserved_v76_replaced_snapshot_fields"] = {
        key: copy.deepcopy(old["snapshot"][key])
        for key in changes
        if key in old["snapshot"]
    }
    predecessor = {
        role: base.pin(item[0], item[1], item[2])
        for role, item in V76.items()
    }
    inputs = copy.deepcopy(previous_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 77,
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
        "preserve Python plus each actual independently written native family",
    )
    for row in families:
        if row["family"] != "python":
            row["authenticated_evidence_owner_lower_bound"] = 255
            row["authenticated_history_reference_lower_bound"] = 260
        if row["family"] == "rust":
            for key, value in changes.items():
                if key.startswith("rust_v12_original_campaign_"):
                    row[key] = copy.deepcopy(value)
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 77,
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
    original = old["clean_original_producer_v5_source_freeze"][
        "complete_feature_contract"
    ]
    hardened = old["candidate_runtime_independence_v2_source_freeze"][
        "complete_feature_contract"
    ]
    base.need(
        len(suites) == 13 and len(witnesses) == 6,
        "preserve every genuine original-suite history and failure witness",
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
            and layer["rust_v12_original_campaign_source_freeze"][
                "complete_feature_contract"
            ]
            == contract
            and layer["clean_original_producer_v5_source_freeze"][
                "complete_feature_contract"
            ]
            == original
            and layer["candidate_runtime_independence_v2_source_freeze"][
                "complete_feature_contract"
            ]
            == hardened
            and layer["rust_v12_original_campaign_candidate_matching"]
            == "NOT RUN"
            and layer["rust_v12_original_campaign_actual_worker_count"] == 0,
            "preserve full original+guarded complete provenance in " + name,
        )
    rust = next(row for row in families if row["family"] == "rust")
    base.need(
        rust["rust_v12_original_campaign_source_freeze"][
            "complete_feature_contract"
        ]
        == contract
        and rust["rust_v12_original_campaign_actual_worker_count"] == 0
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
        "never substitute source-only controller readiness for real matching",
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
        "publish exclusively created complete guarded-Rust results graphs",
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
                "write every complete V77 graph byte",
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
            "preserve complete exclusive durable V77 owner identities",
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
    base.need(confirmed == raw, "reauthenticate the complete actual V77 output")


def self_test(
    previous: types.ModuleType,
    v75: types.ModuleType,
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
        v75, v74, v73, v72, v71, v70, v69, modules, base
    )
    base.need(
        prior["status"] == "PASS"
        and prior["actual_current_graph_predecessor_version"] == 75
        and prior["authenticated_evidence_owner_lower_bound"] == 252
        and prior["authenticated_history_reference_lower_bound"] == 257,
        "inherit every passing V76 guarded-original source control",
    )
    raw = read_fixed(FEATURE["contract"], "whole real Rust V12 source contract")
    contract = base.document(raw, "whole recoverable real Rust V12 contract")
    base.need(
        base.canonical(contract) == raw,
        "reject rewritten full Rust original-campaign source evidence",
    )
    validate_contract(base, contract)
    cases: list[tuple[str, object]] = [("missing complete Rust controller", None)]
    for key in sorted(contract):
        forged = copy.deepcopy(contract)
        forged.pop(key)
        cases.append(("removed actual controller field " + key, forged))
    for name, wrong in (
        ("suite_count", 12),
        ("case_execution_denominator", 31236),
        ("private_waiver_count", 14),
        ("corrected_original_producer_version", 4),
        ("frozen_graph_version", 75),
        ("actual_candidate_workers_started", 1),
        ("actual_build_archive_opens", 1),
        ("runtime_non_delegation", "PASS"),
        ("candidate_matching", "PASS"),
        ("candidate_qualified", True),
        ("qualified_candidate_count", 1),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(contract)
        forged[name] = wrong
        cases.append(("fabricated guarded Rust campaign " + name, forged))
    for key in (
        "corrected_original_producer_source_sha256",
        "corrected_original_producer_contract_sha256",
        "runtime_guard_source_sha256",
        "runtime_guard_contract_sha256",
        "actual_v19_build_receipt_sha256",
        "actual_v19_root_receipt_sha256",
        "actual_v19_native_engine_sha256",
        "actual_v19_native_bridge_sha256",
    ):
        forged = copy.deepcopy(contract)
        forged[key] = "0" * 64
        cases.append(("substituted exact genuine provenance " + key, forged))
    for name, _ in SUITES:
        forged = copy.deepcopy(contract)
        forged["suites"] = [
            row
            for row in forged["suites"]
            if row.get("suite", row.get("name", row.get("id"))) != name
        ]
        cases.append(("removed actual original worker " + name, forged))
    rejected = 0
    for label, forged in cases:
        try:
            validate_contract(base, forged)
        except Exception:
            rejected += 1
        else:
            base.need(False, "accepted forged original Rust campaign: " + label)
    base.need(
        rejected == len(cases) and rejected >= 100,
        "reject every omitted full original worker, V5 guard, and native receipt",
    )
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "version": 77,
        "status": "PASS",
        "previous_overview_version": 76,
        "actual_current_graph_predecessor_version": 76,
        "inherited_rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": (
            prior["rejected_hostile_control_count"] + rejected
        ),
        "authenticated_evidence_owner_lower_bound": 255,
        "authenticated_history_reference_lower_bound": 260,
        "original_suite_count": 13,
        "original_case_execution_denominator": 31237,
        "planned_candidate_worker_count": 13,
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
    for role in V76:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in FEATURE:
        parser.add_argument("--feature-" + role + "-sha256")
    for role in ("inputs", "summary", "svg"):
        parser.add_argument("--" + role + "-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, v75, v74, v73, v72, v71, v70, v69, modules, base = (
            load_previous()
        )
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
                    for role in V76
                )
                and all(
                    getattr(options, "feature_" + role + "_sha256") is None
                    for role in FEATURE
                ),
                "source self-test cannot authorize actual workers or graph output",
            )
            result = self_test(
                previous,
                v75,
                v74,
                v73,
                v72,
                v71,
                v70,
                v69,
                modules,
                base,
            )
        else:
            _, assets = build(
                previous,
                v75,
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
                    "reject invented actual graph-output owner hashes",
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
                            "complete actual V77 " + role,
                        ),
                        len(assets[path]),
                        private=True,
                    )
                    base.need(
                        actual == assets[path],
                        "reproduce the complete frozen V77 " + role,
                    )
            result = {
                "schema": SCHEMA
                + (
                    "-published"
                    if options.render
                    else "-read-only-frozen-context"
                ),
                "version": 77,
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
                "previous_overview_version": 76,
                "actual_current_graph_predecessor_version": 76,
                "authenticated_evidence_owner_lower_bound": 255,
                "authenticated_history_reference_lower_bound": 260,
                "original_suite_count": 13,
                "original_case_execution_denominator": 31237,
                "planned_candidate_worker_count": 13,
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
        sys.stderr.write("current V77 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
