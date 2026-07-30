#!/usr/bin/env python3
"""Show, without running candidates, how close six engines are to Python re."""

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
SELF = "tools/render_candidate_current_overview_v94.py"
OUTPUT = "docs/evidence/candidate-current-overview-v94"
INPUT_PATH = OUTPUT + ".inputs.json"
SUMMARY_PATH = OUTPUT + ".summary.json"
SVG_PATH = OUTPUT + ".svg"
SCHEMA = "rebar-candidate-current-overview-v94"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
OWNER_LIMIT = 4 * 1024 * 1024
CASE_COUNT = 31237
SUPPLEMENTAL_CASE_COUNT = 8244
HOLDOUT_PROPOSAL_COUNT = 14155776
HISTORICAL_HOLDOUT_PROPOSAL_COUNT = 4194304
EVIDENCE_FLOOR = 332
HISTORY_FLOOR = 337

V93 = {
    "source": (
        "tools/render_candidate_current_overview_v93.py",
        "acea17f73861bcd648589a3b43f70db2a13c3c5751daf233ac1c13156cefbb89",
        96257,
        430855,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v93.inputs.json",
        "03930c3b2ce8c115187b3229b64bb71b8e1e4f36951ed78ebdd71ae65c41cd8a",
        15419,
        430882,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v93.summary.json",
        "845c3c7b85aa5e33404aa0085fb97c503a144d686fd7694c59c11f28b4512c5b",
        3465158,
        430891,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v93.svg",
        "e53b9f0d834cbc4b8cacc4f32cc54885f591d45fccef09a6e43ad4e01ae394f2",
        9016,
        430893,
    ),
}

ZIG_SOURCE = {
    "source": (
        "tools/run_owned_repaired_zig_original_campaign_v13.py",
        "fa46d4029f5590adceb22bfe4e612248da5f7f90ed6362d58faa5b631fee7ff8",
        246570,
        430932,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V13.md",
        "6b42893161e37baec1695aefb414fb7179b778f2164018b024bd68b3c9bb5c2c",
        9553,
        525201,
    ),
    "contract": (
        "oracle/phase2/repaired-zig-original-campaign-v13.json",
        "327b14096e36c7a2e4cab977a452fc2477fbf148396f50433cbf1dc8aba31a3f",
        106084,
        525206,
    ),
}

ZIG_RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-zig-original-campaign-v13-phase2-v13-zig-guard-clean-lifetime-v1-"
    "original-p0-v13-failures-publication-receipt.json",
    "b3443a647c638cbbbe7905a2c668a734770f38cb678f06a387af497917fc4bca",
    78911,
    525299,
)

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

WORKER_PIDS = (81, 83, 84, 85, 86, 87, 88, 89, 90, 91, 188, 189, 190)
MISMATCHES = {
    "scanner_verbose_v1": 620,
    "public_types_v1": 248,
    "substitution_v2": 64,
    "shape_v2": 672,
    "public_surface_v19": 96,
}

V93_C_POOL = (
    "lossless_v93_c_v9_original_campaign_evidence_pool",
    45248,
    "7b189ab906dbe14af8fd149de69f6275aa0d1c1e0bf5948ff88f9ff5cfff7ed9",
    1,
)
V93_SNAPSHOT_SHA256 = (
    "9f33962923de9f8229e722b9761d5154cba9d4e83921b39431f22ff5d47abb68"
)
V93_SNAPSHOT_BYTES = 9547

POOL_KEY = "lossless_v94_zig_v13_original_campaign_evidence_pool"
POOL_SCHEMA = SCHEMA + "-lossless-complete-zig-original-campaign-pool-v1"
ENTRY_SCHEMA = SCHEMA + "-lossless-complete-zig-original-campaign-entry-v1"
REFERENCE_SCHEMA = SCHEMA + "-complete-zig-original-campaign-reference-v1"
LATEST_KEY = "zig_v13_actual_original_campaign"

CONTRACT_KEYS = frozenset({
    "corrected_original_matching",
    "corrected_supplemental_matching",
    "current_qualified_candidates",
    "expanded_sealed_holdout_proposal",
    "family",
    "first_party_lifetime_adapter",
    "future_actual_run",
    "goal",
    "historical_first_party_v13_native_build",
    "holdout",
    "holdout_case_count",
    "immutable_v2_runtime_guard",
    "immutable_v5_original_producer",
    "label",
    "memory",
    "minimum_qualified_candidates",
    "original_oracle",
    "performance",
    "pinned_cpython",
    "protocol",
    "pushed_v12_actual_predecessor",
    "pushed_v3_real_interpreter_guard",
    "qualified_candidate_count",
    "repaired_subinterpreter",
    "repaired_warning",
    "runtime_non_delegation",
    "schema",
    "source",
    "source_only_effects",
    "source_only_worker_transport",
    "status",
    "undefined_behavior",
    "version",
    "winner_selected",
})

RECEIPT_KEYS = frozenset({
    "actual_candidate_workers",
    "all_original_suites_attempted",
    "all_three_original_targets_restored",
    "archive",
    "benchmark_files_read",
    "candidate_qualified",
    "candidate_status",
    "case_execution_denominator",
    "completed_suite_count",
    "contract_sha256",
    "failed_suites",
    "family",
    "hidden_cases_read",
    "holdout",
    "infrastructure_failure_count",
    "infrastructure_failure_suites",
    "label",
    "maximum_serial_worker_timeout_seconds",
    "memory",
    "observed_semantic_mismatch_lower_bound",
    "original_campaign_passed",
    "original_suite_diagnostics",
    "per_suite_timeout_seconds",
    "performance",
    "protocol_sha256",
    "publication_pass_means",
    "schema",
    "semantic_mismatch_count",
    "source_sha256",
    "status",
    "suite_count",
    "supplemental_candidate_matching",
    "timed_out_suites",
    "timeout_classification",
    "timeout_count",
    "timing_trials_run",
    "uncompressed_bytes",
    "uncompressed_sha256",
    "undefined_behavior",
    "unique_candidate_worker_count",
    "verified_passing_case_count",
    "winner_selected",
})

ROW_KEYS = frozenset({
    "activation_stage",
    "actual_worker_schema",
    "candidate_imported",
    "case_execution_denominator",
    "complete_actual_suite_failure_details",
    "error_class",
    "error_message",
    "error_message_detail",
    "error_traceback",
    "error_type",
    "guard_installed_before_candidate_import",
    "infrastructure_failure",
    "observed_semantic_mismatch_count",
    "observer_source_proxy",
    "pid",
    "returncode",
    "status",
    "stderr",
    "stderr_literal_excerpt",
    "stdout",
    "suite",
    "timed_out",
    "timeout_classification",
    "timeout_seconds",
    "traceback_frames",
    "traceback_frames_truncated",
})

FORBIDDEN_EVENTS = frozenset({
    "subprocess.Popen",
    "os.system",
    "os.posix_spawn",
    "os.posix_spawnp",
    "os.fork",
    "os.forkpty",
    "ctypes.dlopen",
    "ctypes.dlsym",
    "socket.__new__",
    "socket.connect",
    "socket.bind",
    "socket.sendto",
    "os.remove",
    "os.rename",
    "os.rmdir",
    "os.mkdir",
})
FORBIDDEN_IMPORTS = frozenset({
    "regex",
    "re",
    "_sre",
    "ctypes",
    "subprocess",
    "multiprocessing",
    "socket",
    "time",
    "gzip",
    "bz2",
    "lzma",
    "tarfile",
    "zipfile",
    "candidates",
    "rebar",
})


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    """Read one exact public plaintext owner without following links."""
    relative, expected, size, inode = item
    if not (type(size) is int and 0 < size <= OWNER_LIMIT):
        raise ValueError("reject unbounded V94 plaintext owner: " + label)
    if (
        not isinstance(relative, str)
        or relative.startswith("/")
        or ".." in relative.split("/")
        or relative.endswith((".gz", ".bz2", ".xz", ".zip", ".so", ".dylib"))
    ):
        raise ValueError("reject private, native, or compressed V94 owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / relative), flags)
    try:
        before = os.fstat(handle)
        if not (
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_dev == 2064
            and before.st_ino == inode
            and before.st_size == size
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600
        ):
            raise ValueError("reject substituted complete V94 owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(handle, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject truncated complete V94 owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(handle, 1):
            raise ValueError("reject extended complete V94 owner: " + label)
        raw = b"".join(chunks)
        after = os.fstat(handle)
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
            raise ValueError("reject changed complete V94 owner: " + label)
        return raw
    finally:
        os.close(handle)


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    """Physically prohibit candidate runs, archives, holdouts, and writes."""
    if event in FORBIDDEN_EVENTS:
        raise ValueError("V94 source-only operation rejected " + event)
    if event == "import":
        name = arguments[0] if arguments else None
        if isinstance(name, str) and name.partition(".")[0] in FORBIDDEN_IMPORTS:
            raise ValueError("V94 source-only import rejected " + name)
        return
    if event != "open":
        return
    if len(arguments) < 3:
        raise ValueError("V94 rejected an unauthenticated file open")
    path, mode, flags = arguments[:3]
    if not isinstance(path, str) or not isinstance(flags, int):
        raise ValueError("V94 rejected an unverified descriptor or file owner")
    if mode not in (None, "r", "rb"):
        raise ValueError("V94 source-only operation cannot write files")
    if flags & os.O_ACCMODE != os.O_RDONLY or flags & (
        os.O_CREAT | os.O_TRUNC | os.O_APPEND
    ):
        raise ValueError("V94 source-only operation cannot create files")
    normalized = os.path.normpath(path)
    if os.path.isabs(normalized):
        if normalized != str(ROOT) and not normalized.startswith(str(ROOT) + "/"):
            raise ValueError("V94 rejected private roots or unopened holdout cases")
    elif "/" in normalized or normalized in (".", ".."):
        raise ValueError("V94 rejected an escaped relative evidence owner")
    if (
        normalized.endswith((".gz", ".bz2", ".xz", ".zip", ".so", ".dylib"))
        or "candidate-current-overview-v94." in normalized
        or "/.git/" in normalized
        or "/__pycache__/" in normalized
        or "/performance/" in normalized
        or "/experiments/" in normalized
    ):
        raise ValueError("V94 rejected output, archive, native, or holdout: " + normalized)


def load_previous() -> tuple[types.ModuleType, tuple, types.ModuleType]:
    raw = read_fixed(V93["source"], "whole published V93 renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v93")
    previous.__file__ = str(ROOT / V93["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    chain = previous.load_previous()
    base = chain[-1]
    base.runtime()
    base.need(
        os.path.realpath(sys.executable) == PYTHON
        and sys.implementation.name == "cpython"
        and sys.implementation.cache_tag == "cpython-314"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode is True
        and previous.SCHEMA == "rebar-candidate-current-overview-v93"
        and previous.SELF == V93["source"][0]
        and tuple(previous.SUITES) == SUITES
        and len(SUITES) == 13
        and sum(count for _, count in SUITES) == CASE_COUNT
        and len(chain) == 13,
        "require pinned isolated Python, exact V93 history, and all original cases",
    )
    return previous, chain, base


def previous_options(previous: types.ModuleType) -> argparse.Namespace:
    pins: dict[str, object] = {
        "source_sha256": V93["source"][1],
        "source_bytes": V93["source"][2],
        "c_receipt_sha256": previous.C_RECEIPT[1],
    }
    for role, item in previous.V92.items():
        pins["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.C_SOURCE.items():
        pins["c_" + role + "_sha256"] = item[1]
    return argparse.Namespace(**pins)


def previous_pools(previous: types.ModuleType) -> tuple:
    pools = tuple(previous.OLD_POOLS) + (V93_C_POOL,)
    if len(pools) != 15 or len({item[0] for item in pools}) != 15:
        raise ValueError("require all fifteen distinct immutable V93 proof pools")
    return pools


def validate_previous(
    previous: types.ModuleType,
    base: types.ModuleType,
    value: object,
) -> dict:
    base.need(
        type(value) is dict
        and value.get("schema") == "rebar-candidate-current-overview-v93-summary"
        and value.get("version") == 93
        and value.get("status") == "PASS"
        and value.get("authenticated_evidence_owner_lower_bound") == 328
        and value.get("authenticated_history_reference_lower_bound") == 333
        and value.get("original_case_execution_denominator") == CASE_COUNT
        and value.get("original_suite_count") == 13
        and value.get("named_private_waiver_count") == 13
        and value.get("separate_additional_reference_case_count")
        == SUPPLEMENTAL_CASE_COUNT
        and value.get("additional_cases_included_in_original_denominator") is False
        and value.get("qualified_candidate_count") == 0
        and value.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and value.get("performance") == "NOT MEASURED"
        and value.get("memory") == "NOT MEASURED"
        and value.get("undefined_behavior") == "NOT MEASURED"
        and value.get("expanded_holdout_proposed_case_count") == HOLDOUT_PROPOSAL_COUNT
        and value.get("preserved_previous_holdout_proposal_case_count")
        == HISTORICAL_HOLDOUT_PROPOSAL_COUNT
        and value.get("expanded_holdout_final_protocol_status") == "NOT FROZEN"
        and value.get("expanded_holdout_case_status") == "NOT GENERATED; NOT OPENED"
        and value.get("final_holdout_opened") is False
        and value.get("winner_selected") is False,
        "retain the whole real V93 baseline, denominator, history, and sealed holdout",
    )
    assert isinstance(value, dict)
    base.need(
        value.get("rust_v20_original_campaign_verified_passing_case_count") == 15749
        and value.get("rust_v20_original_campaign_observed_mismatch_lower_bound") == 1296
        and value.get("c_v9_original_campaign_verified_passing_case_count") == 13606
        and value.get("c_v9_original_campaign_observed_mismatch_lower_bound") == 492
        and value.get("c_v9_original_campaign_candidate_execution_failure_count") == 6
        and value.get("zig_v12_original_campaign_verified_passing_case_count") == 4607
        and value.get("zig_v12_original_campaign_observed_mismatch_lower_bound") == 1700
        and value.get("lossless_v93_c_v9_complete_plaintext_receipt_count") == 1
        and value.get("lossless_v93_c_v9_complete_source_owner_count") == 3
        and value.get("lossless_v93_c_v9_complete_original_suite_count") == 13,
        "retain real historical Rust, C, and Zig results without hiding failures",
    )
    snapshot = value.get("snapshot")
    snapshot_raw = base.canonical(snapshot)
    base.need(
        type(snapshot) is dict
        and snapshot.get("schema")
        == "rebar-candidate-current-overview-v93-compact-current-snapshot"
        and snapshot.get("version") == 93
        and len(snapshot_raw) == V93_SNAPSHOT_BYTES
        and base.digest(snapshot_raw) == V93_SNAPSHOT_SHA256,
        "retain every authenticated byte of the actual current V93 snapshot",
    )
    for key, size, expected, count in previous_pools(previous):
        pool = value.get(key)
        raw = base.canonical(pool)
        base.need(
            type(pool) is dict
            and len(raw) == size
            and base.digest(raw) == expected
            and type(pool.get("entries")) is dict
            and len(pool["entries"]) == count,
            "retain the complete immutable V93 evidence pool: " + key,
        )
    families = value.get("families")
    base.need(
        type(families) is list
        and len(families) == 7
        and [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"]
        and families[0].get("correctness") == "BASELINE PASS",
        "retain standard Python and all six distinct first-party approaches",
    )
    latest = value.get("latest_original_campaigns")
    base.need(
        type(latest) is dict
        and set(latest) == {"rust", "c", "zig"}
        and type(value.get("headline")) is dict
        and value["headline"].get("verified_original_checks_by_candidate")
        == {
            "c": 13606,
            "cpp": "NOT MEASURED",
            "fortran": "NOT MEASURED",
            "go": "NOT MEASURED",
            "rust": 15749,
            "zig": 4607,
        },
        "retain every measured approach without inventing unmeasured results",
    )
    return value


def authenticate_previous(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
) -> dict:
    snapshot, assets = previous.build(*chain, previous_options(previous))
    for role in ("inputs", "summary", "svg"):
        item = V93[role]
        base.need(
            assets[item[0]] == read_fixed(item, "whole published V93 " + role),
            "reconstruct every actual published V93 " + role + " byte",
        )
    old = base.document(assets[V93["summary"][0]], "whole published V93 summary")
    validate_previous(previous, base, old)
    base.need(
        base.canonical(snapshot) == base.canonical(old["snapshot"]),
        "retain the exact reconstructed V93 snapshot",
    )
    return old


def validate_source_contract(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict and set(value) == CONTRACT_KEYS,
        "authenticate all 35 complete first-party Zig V13 source-contract fields",
    )
    assert isinstance(value, dict)
    base.need(
        value["schema"]
        == "rebar-owned-repaired-zig-original-campaign-v13-guarded-lifetime-source-freeze"
        and value["version"] == 13
        and value["family"] == "zig"
        and value["label"] == "phase2-v13-zig-guard-clean-lifetime-v1-original-p0-v13"
        and value["status"] == "SOURCE FROZEN; V3-GUARDED LIFETIME ZIG MATCHING NOT RUN"
        and value["corrected_original_matching"] == "NOT RUN"
        and value["corrected_supplemental_matching"] == "NOT RUN"
        and value["current_qualified_candidates"] == 0
        and value["qualified_candidate_count"] == 0
        and value["minimum_qualified_candidates"] == 3
        and value["repaired_warning"] == "NOT MEASURED"
        and value["repaired_subinterpreter"] == "NOT MEASURED"
        and value["runtime_non_delegation"] == "NOT ESTABLISHED"
        and value["holdout"] == "NOT OPENED"
        and value["holdout_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and value["performance"] == "NOT MEASURED"
        and value["memory"] == "NOT MEASURED"
        and value["undefined_behavior"] == "NOT MEASURED"
        and value["winner_selected"] is False,
        "reject a source freeze mislabeled as repaired, compatible, or faster",
    )
    for role in ("source", "protocol"):
        item = ZIG_SOURCE[role]
        base.need(
            value[role]
            == {
                "path": item[0],
                "sha256": item[1],
                "bytes": item[2],
                "device": 2064,
                "inode": item[3],
                "mode": "0600",
                "nlink": 1,
            },
            "authenticate complete exact Zig V13 source owner: " + role,
        )
    oracle = value["original_oracle"]
    base.need(
        type(oracle) is dict
        and oracle.get("case_execution_denominator") == CASE_COUNT
        and oracle.get("suite_count") == 13
        and oracle.get("named_private_waiver_count") == 13
        and oracle.get("obligation_count") == 73
        and oracle.get("crosswalk_count") == 34
        and oracle.get("supplemental_reference_case_count") == SUPPLEMENTAL_CASE_COUNT
        and oracle.get("supplemental_reference_worker_count") == 2
        and oracle.get("supplemental_cases_added_to_original_denominator") is False
        and oracle.get("performance_oracle_authorized") is False
        and oracle.get("final_holdout_authorized") is False
        and oracle.get("supplemental_candidate_matching") == "NOT RUN"
        and type(oracle.get("suites")) is list
        and len(oracle["suites"]) == 13,
        "preserve the exact complete original oracle and separate reference checks",
    )
    for row, (suite, denominator) in zip(oracle["suites"], SUITES, strict=True):
        base.need(
            type(row) is dict
            and row.get("id") == suite
            and row.get("case_execution_count") == denominator,
            "reject a missing or changed original Zig suite: " + suite,
        )
    holdout = value["expanded_sealed_holdout_proposal"]
    base.need(
        type(holdout) is dict
        and holdout.get("case_count") == HOLDOUT_PROPOSAL_COUNT
        and holdout.get("historical_case_count") == HISTORICAL_HOLDOUT_PROPOSAL_COUNT
        and holdout.get("case_status") == "NOT GENERATED; NOT OPENED"
        and holdout.get("final_protocol_status") == "NOT FROZEN"
        and holdout.get("holdout_files_opened") == 0
        and holdout.get("benchmark_files_opened") == 0
        and holdout.get("timing_trials_run") == 0
        and holdout.get("qualified_independent_family_count") == 0,
        "reject an opened, generated, benchmarked, or falsely frozen holdout",
    )
    pinned = value["pinned_cpython"]
    base.need(
        type(pinned) is dict
        and pinned.get("path") == PYTHON
        and pinned.get("version") == "3.14.6"
        and pinned.get("isolated_flags") == ["-I", "-B", "-S"]
        and pinned.get("bytecode_written") is False,
        "preserve the exact immutable Python correctness baseline",
    )
    effects = value["source_only_effects"]
    base.need(
        type(effects) is dict
        and len(effects) == 25
        and all(type(number) is int and number == 0 for number in effects.values()),
        "reject source-only candidates, child guards, native loads, clocks, or writes",
    )
    transport = value["source_only_worker_transport"]
    base.need(
        type(transport) is dict
        and transport.get("actual_worker_started_in_source_gate") is False
        and transport.get("preserve_complete_worker_stdout_and_stderr") is True
        and transport.get("publish_all_13_public_worker_diagnostics") is True
        and transport.get("complete_nested_failures_preserved") is True,
        "preserve original full worker diagnostics without running a worker",
    )
    future = value["future_actual_run"]
    base.need(
        type(future) is dict
        and future.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and future.get("candidate_family") == "zig"
        and future.get("candidate_label") == value["label"]
        and future.get("case_execution_denominator") == CASE_COUNT
        and future.get("original_suite_worker_count") == 13
        and future.get("unique_original_worker_pid_count_required") == 13
        and future.get("guard_installed_before_candidate_import") is True
        and future.get("guard_version") == 3
        and future.get("continue_after_every_recorded_failure") is True
        and future.get("compiler_processes_authorized") is False
        and future.get("native_build_authorized") is False
        and future.get("holdout_files_opened") == 0
        and future.get("supplemental_candidate_matching") == "NOT RUN"
        and future.get("failure_publication_receipt") == ZIG_RECEIPT[0]
        and future.get("per_complete_original_suite_timeout_seconds") == 120
        and future.get("maximum_serial_worker_timeout_seconds") == 1560,
        "preserve the actual frozen campaign without authorizing another execution",
    )
    adapter = value["first_party_lifetime_adapter"]
    base.need(
        type(adapter) is dict
        and adapter.get("cross_candidate_engine_added") is False
        and adapter.get("external_regex_engine_added") is False
        and adapter.get("stdlib_regex_fallback_added") is False
        and adapter.get("matcher_parser_compiler_scanner_changed") is False,
        "reject external regex wrappers, stdlib delegation, or sibling engines",
    )
    return value


def validate_child_failure(base: types.ModuleType, row: dict) -> None:
    failure = row["complete_actual_suite_failure_details"]
    base.need(
        type(failure) is dict
        and failure.get("schema")
        == "rebar-owned-six-family-original-p0-producer-v5-genuine-nested-failure"
        and failure.get("status") == "FAIL"
        and failure.get("suite") == "subinterpreter_v2"
        and failure.get("candidate_family") == "zig"
        and failure.get("actual_candidate_subprocesses") == 0
        and failure.get("actual_child_guards_installed") == 0
        and failure.get("actual_guard_cleanup_interpreter_exec_calls") == 0
        and failure.get("expected_case_interpreter_exec_calls") == 394
        and failure.get("expected_interpreters_created") == 11
        and failure.get("holdout") == "NOT OPENED"
        and failure.get("performance") == "NOT MEASURED"
        and failure.get("benchmark_files_read") == 0
        and failure.get("hidden_cases_read") == 0
        and failure.get("clock_samples") == 0
        and failure.get("timing_trials_run") == 0
        and failure.get("winner_selected") is False,
        "reject a fabricated successful child guard or private interpreter",
    )
    nested = failure["complete_original_failure_details"]
    base.need(
        type(nested) is dict
        and nested.get("schema")
        == "rebar-owned-six-family-original-p0-producer-v4-genuine-nested-failure"
        and nested.get("status") == "FAIL"
        and nested.get("active_phase") == "create-genuine-owned-interpreter-A"
        and nested.get("error_type") == "GuardError"
        and nested.get("error_message")
        == "runtime guard blocked missing-or-fabricated-native-child-creation"
        and nested.get("actual_case_interpreter_exec_calls") == 0
        and nested.get("actual_guard_cleanup_interpreter_exec_calls") == 0
        and nested.get("actual_initialization_interpreter_exec_calls") == 0
        and nested.get("actual_interpreters_created") == 0
        and nested.get("actual_interpreters_destroyed") == 0
        and nested.get("actual_prepared_interpreter_ids") == []
        and nested.get("completed_a_records") == []
        and nested.get("completed_b_records") == []
        and nested.get("completed_fresh_records") == []
        and nested.get("completed_repeated_a_records") == []
        and nested.get("pipe_ledgers") == [],
        "reject invented child creation, child matching, or nested cleanup",
    )


def validate_zig_receipt(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict and set(value) == RECEIPT_KEYS,
        "authenticate all 42 complete actual Zig V13 public receipt fields",
    )
    assert isinstance(value, dict)
    base.need(
        value["schema"]
        == "rebar-owned-repaired-zig-original-campaign-v13-durable-publication-receipt"
        and value["family"] == "zig"
        and value["label"] == "phase2-v13-zig-guard-clean-lifetime-v1-original-p0-v13"
        and value["status"] == "PASS"
        and value["publication_pass_means"] == "DURABLE PUBLICATION ONLY"
        and value["candidate_status"] == "FAIL"
        and value["candidate_qualified"] is False
        and value["original_campaign_passed"] is False
        and value["source_sha256"] == ZIG_SOURCE["source"][1]
        and value["protocol_sha256"] == ZIG_SOURCE["protocol"][1]
        and value["contract_sha256"] == ZIG_SOURCE["contract"][1]
        and value["case_execution_denominator"] == CASE_COUNT
        and value["suite_count"] == 13
        and value["actual_candidate_workers"] == 13
        and value["unique_candidate_worker_count"] == 13
        and value["all_original_suites_attempted"] is True
        and value["all_three_original_targets_restored"] is True
        and value["completed_suite_count"] == 12
        and value["verified_passing_case_count"] == 4607
        and value["observed_semantic_mismatch_lower_bound"] == 1700
        and value["semantic_mismatch_count"] == "NOT MEASURED"
        and value["infrastructure_failure_count"] == 1
        and value["infrastructure_failure_suites"] == ["subinterpreter_v2"]
        and value["failed_suites"] == [
            "scanner_verbose_v1",
            "public_types_v1",
            "substitution_v2",
            "shape_v2",
            "public_surface_v19",
            "subinterpreter_v2",
        ]
        and value["timed_out_suites"] == []
        and value["timeout_count"] == 0
        and value["timeout_classification"] == "INFRASTRUCTURE FAILURE"
        and value["per_suite_timeout_seconds"] == 120
        and value["maximum_serial_worker_timeout_seconds"] == 1560
        and value["hidden_cases_read"] == 0
        and value["benchmark_files_read"] == 0
        and value["timing_trials_run"] == 0
        and value["supplemental_candidate_matching"] == "NOT RUN"
        and value["holdout"] == "NOT OPENED"
        and value["performance"] == "NOT MEASURED"
        and value["memory"] == "NOT MEASURED"
        and value["undefined_behavior"] == "NOT MEASURED"
        and value["winner_selected"] is False,
        "reject publication-as-success, hidden Zig failures, or invented speed",
    )
    archive = value["archive"]
    base.need(
        type(archive) is dict
        and set(archive)
        == {"bytes", "device", "inode", "mode", "name", "nlink", "sha256", "uid"}
        and archive["name"]
        == "repaired-zig-original-campaign-v13-phase2-v13-zig-guard-clean-"
        "lifetime-v1-original-p0-v13-failures.json.gz"
        and archive["sha256"]
        == "2d277e78ba5c87f9e1566e968369754290d848fd5f58b6adafc8b840c05908da"
        and archive["bytes"] == 5615638
        and archive["device"] == 2064
        and archive["inode"] == 525298
        and archive["mode"] == 384
        and archive["nlink"] == 1
        and archive["uid"] == os.geteuid()
        and value["uncompressed_bytes"] == 192348645
        and value["uncompressed_sha256"]
        == "864ffdf6c1a565062b32099ca1717ad5f676d8c3c5e7851ef8d20bd504a936c6",
        "retain actual archive metadata only; never open or stat the archive",
    )
    rows = value["original_suite_diagnostics"]
    base.need(
        type(rows) is list and len(rows) == 13,
        "retain all thirteen real complete public Zig worker diagnostics",
    )
    pids: set[int] = set()
    clean: list[dict] = []
    mismatches: list[dict] = []
    incomplete: list[dict] = []
    warning_examples = 0
    excerpt_bytes = 0
    stderr_bytes = 0
    stdout_bytes = 0
    truncated_count = 0
    literal_proofs: list[dict] = []
    for index, (row, (suite, denominator)) in enumerate(zip(rows, SUITES, strict=True)):
        base.need(
            type(row) is dict
            and set(row) == ROW_KEYS
            and row["suite"] == suite
            and row["case_execution_denominator"] == denominator
            and row["actual_worker_schema"] == (
                "rebar-owned-repaired-zig-original-campaign-v13-actual-worker-failure"
                if suite == "subinterpreter_v2"
                else "rebar-owned-repaired-zig-original-campaign-v13-actual-suite-worker"
            )
            and type(row["pid"]) is int
            and row["pid"] == WORKER_PIDS[index]
            and row["pid"] not in pids
            and row["candidate_imported"] is True
            and row["guard_installed_before_candidate_import"] is True
            and row["returncode"] == 0
            and row["timed_out"] is False
            and row["timeout_seconds"] == 120
            and row["timeout_classification"] == "NOT TIMED OUT",
            "reject an omitted, invented, duplicate, or unguarded Zig worker: " + suite,
        )
        pids.add(row["pid"])
        for stream_name in ("stdout", "stderr"):
            stream = row[stream_name]
            base.need(
                type(stream) is dict
                and set(stream)
                == {"bytes", "complete", "complete_payload_preserved_in_actual_archive", "sha256"}
                and type(stream["bytes"]) is int
                and stream["bytes"] >= 0
                and stream["complete"] is True
                and stream["complete_payload_preserved_in_actual_archive"] is True
                and base.checked(stream["sha256"], "complete actual " + stream_name)
                == stream["sha256"],
                "retain complete archived stream metadata without opening it: " + suite,
            )
        stderr = row["stderr"]
        excerpt = row["stderr_literal_excerpt"]
        base.need(
            type(excerpt) is dict
            and set(excerpt)
            == {
                "captured_bytes",
                "encoding",
                "limit_bytes",
                "sha256",
                "status",
                "text",
                "total_bytes",
                "truncated",
            }
            and excerpt["status"] == "CAPTURED"
            and excerpt["encoding"] == "UTF-8; INVALID BYTES BACKSLASH-ESCAPED"
            and excerpt["limit_bytes"] == 4096
            and type(excerpt["text"]) is str
            and type(excerpt["captured_bytes"]) is int
            and excerpt["captured_bytes"] == len(excerpt["text"].encode("utf-8"))
            and 0 < excerpt["captured_bytes"] <= excerpt["limit_bytes"]
            and excerpt["total_bytes"] == stderr["bytes"]
            and excerpt["sha256"] == stderr["sha256"]
            and type(excerpt["truncated"]) is bool
            and excerpt["truncated"]
            == (excerpt["captured_bytes"] < excerpt["total_bytes"]),
            "retain real warning text and label its digest as the full stream: " + suite,
        )
        text = excerpt["text"]
        occurrences = text.count("Exception ignored while calling deallocator")
        base.need(
            occurrences == 11
            and "Pattern.__del__" in text
            and "TypeError: argument of type 'NoneType'" in text,
            "reject a hidden genuine per-worker Zig deallocator warning: " + suite,
        )
        excerpt_digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if excerpt["truncated"]:
            truncated_count += 1
            base.need(
                excerpt_digest != stderr["sha256"],
                "do not mislabel a truncated literal excerpt as the complete stderr",
            )
        else:
            base.need(
                excerpt_digest == stderr["sha256"],
                "authenticate the single actual untruncated warning excerpt",
            )
        literal_proofs.append({
            "suite": suite,
            "worker_process_id": row["pid"],
            "literal_excerpt_sha256": excerpt_digest,
            "literal_excerpt_bytes": excerpt["captured_bytes"],
            "literal_excerpt_truncated": excerpt["truncated"],
            "literal_warning_occurrence_lower_bound": occurrences,
            "complete_stderr_sha256_from_receipt_metadata": stderr["sha256"],
            "complete_stderr_bytes_from_receipt_metadata": stderr["bytes"],
            "remaining_subinterpreter_warning_visible":
            "RuntimeWarning: remaining subinterpreters" in text,
        })
        warning_examples += occurrences
        excerpt_bytes += excerpt["captured_bytes"]
        stderr_bytes += stderr["bytes"]
        stdout_bytes += row["stdout"]["bytes"]
        if suite == "subinterpreter_v2":
            base.need(
                row["status"] == "FAIL"
                and row["infrastructure_failure"] is True
                and row["activation_stage"]
                == "OBSERVE_COMPLETE_ORIGINAL_SUBINTERPRETER_SUITE"
                and row["observed_semantic_mismatch_count"] == "NOT MEASURED"
                and row["error_type"] == "ActualSuiteFailure"
                and "RuntimeWarning: remaining subinterpreters" in text,
                "retain the real incomplete child-lifecycle infrastructure failure",
            )
            validate_child_failure(base, row)
            incomplete.append(row)
        elif suite in MISMATCHES:
            base.need(
                row["status"] == "FAIL"
                and row["infrastructure_failure"] is False
                and row["activation_stage"] == "COMPLETE_ORIGINAL_OBSERVATION"
                and row["observed_semantic_mismatch_count"] == MISMATCHES[suite]
                and row["error_type"] is None
                and row["complete_actual_suite_failure_details"] is None,
                "retain every real complete Zig mismatch group: " + suite,
            )
            mismatches.append(row)
        else:
            base.need(
                row["status"] == "PASS"
                and row["infrastructure_failure"] is False
                and row["activation_stage"] == "COMPLETE_ORIGINAL_OBSERVATION"
                and row["observed_semantic_mismatch_count"] == 0
                and row["error_type"] is None
                and row["complete_actual_suite_failure_details"] is None,
                "reject an invented complete passing Zig group: " + suite,
            )
            clean.append(row)
    base.need(
        len(pids) == 13
        and tuple(row["pid"] for row in rows) == WORKER_PIDS
        and len(clean) == 7
        and len(mismatches) == 5
        and len(incomplete) == 1
        and len(clean) + len(mismatches) == 12
        and sum(row["case_execution_denominator"] for row in clean) == 4607
        and {row["suite"]: row["observed_semantic_mismatch_count"] for row in mismatches}
        == MISMATCHES
        and sum(row["observed_semantic_mismatch_count"] for row in mismatches) == 1700
        and warning_examples == 143
        and truncated_count == 12
        and excerpt_bytes == 53211
        and stderr_bytes == 428866
        and stdout_bytes == 82236727
        and sum(proof["remaining_subinterpreter_warning_visible"] for proof in literal_proofs)
        == 1,
        "derive real Zig passes, differences, warnings, streams, and zero child guards",
    )
    return {
        "family": "zig",
        "display_name": "Zig",
        "actual_candidate_worker_count": 13,
        "unique_candidate_worker_count": 13,
        "actual_worker_process_ids": list(WORKER_PIDS),
        "attempted_suite_count": 13,
        "clean_suite_count": 7,
        "completed_suite_count": 12,
        "mismatch_suite_count": 5,
        "infrastructure_failure_count": 1,
        "infrastructure_failure_suite": "subinterpreter_v2",
        "worker_timeout_count": 0,
        "verified_passing_case_count": 4607,
        "observed_semantic_mismatch_lower_bound": 1700,
        "aggregate_semantic_mismatch_count": "NOT MEASURED",
        "individually_proven_guarded_candidate_import_count": 13,
        "candidate_import_status_unknown_count": 0,
        "actual_child_guards_installed": 0,
        "actual_child_interpreters_created": 0,
        "actual_child_case_interpreter_exec_calls": 0,
        "cleanup_warning_worker_count": 13,
        "cleanup_warning_captured_occurrence_lower_bound": 143,
        "cleanup_warning_full_occurrence_count": "NOT MEASURED",
        "cleanup_warning_excerpt_truncated_worker_count": 12,
        "cleanup_warning_excerpt_complete_worker_count": 1,
        "cleanup_warning_literal_excerpt_total_bytes": 53211,
        "complete_stderr_metadata_total_bytes": 428866,
        "complete_stdout_metadata_total_bytes": 82236727,
        "remaining_subinterpreter_runtime_warning_worker_count": 1,
        "literal_warning_excerpt_proofs": literal_proofs,
        "case_execution_denominator": CASE_COUNT,
        "candidate_status": "FAIL",
        "candidate_qualified": False,
        "original_campaign_passed": False,
        "all_original_suite_rows_validated": True,
        "all_original_observation_vectors_complete": False,
        "all_three_original_targets_restored": True,
        "source_sha256": ZIG_SOURCE["source"][1],
        "protocol_sha256": ZIG_SOURCE["protocol"][1],
        "contract_sha256": ZIG_SOURCE["contract"][1],
        "archive_metadata_sha256": archive["sha256"],
        "archive_metadata_bytes": archive["bytes"],
        "archive_opened_by_graph": False,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
    }


def load_zig_evidence(base: types.ModuleType) -> tuple[dict, dict, dict]:
    raws = {
        role: read_fixed(item, "whole first-party Zig V13 " + role)
        for role, item in ZIG_SOURCE.items()
    }
    contract = base.document(raws["contract"], "whole real Zig V13 source contract")
    base.need(
        base.canonical(contract) == raws["contract"],
        "reject a partial or noncanonical original Zig source contract",
    )
    validate_source_contract(base, contract)
    raw = read_fixed(ZIG_RECEIPT, "whole actual Zig V13 plaintext publication receipt")
    receipt = base.document(raw, "whole actual Zig V13 public plaintext receipt")
    base.need(
        base.canonical(receipt) == raw,
        "reject a partial, noncanonical, or synthetic Zig campaign receipt",
    )
    return contract, receipt, validate_zig_receipt(base, receipt)


def compact_suite_proof(base: types.ModuleType, row: dict) -> dict:
    complete = base.canonical(row)
    excerpt = row["stderr_literal_excerpt"]
    literal = excerpt["text"].encode("utf-8")
    return {
        "suite": row["suite"],
        "case_execution_denominator": row["case_execution_denominator"],
        "complete_public_suite_row_sha256": base.digest(complete),
        "complete_public_suite_row_canonical_bytes": len(complete),
        "actual_worker_process_id": row["pid"],
        "candidate_imported": row["candidate_imported"],
        "guard_installed_before_candidate_import":
        row["guard_installed_before_candidate_import"],
        "status": row["status"],
        "infrastructure_failure": row["infrastructure_failure"],
        "observed_semantic_mismatch_count": row["observed_semantic_mismatch_count"],
        "literal_warning_excerpt_sha256": hashlib.sha256(literal).hexdigest(),
        "literal_warning_excerpt_bytes": len(literal),
        "literal_warning_occurrence_lower_bound":
        excerpt["text"].count("Exception ignored while calling deallocator"),
        "literal_warning_excerpt_truncated": excerpt["truncated"],
        "complete_stderr_sha256_from_receipt_metadata": row["stderr"]["sha256"],
        "complete_stderr_bytes_from_receipt_metadata": row["stderr"]["bytes"],
    }


def make_evidence_pool(
    base: types.ModuleType,
    contract: dict,
    receipt: dict,
    facts: dict,
) -> dict:
    entry = {
        "schema": ENTRY_SCHEMA,
        "family": "zig",
        "complete_plaintext_receipt_owner": base.synthetic_owner(
            ZIG_RECEIPT[:3], ZIG_RECEIPT[3]
        ),
        "complete_plaintext_receipt_sha256": ZIG_RECEIPT[1],
        "complete_plaintext_receipt_bytes": ZIG_RECEIPT[2],
        "complete_plaintext_receipt_field_count": len(RECEIPT_KEYS),
        "complete_plaintext_receipt_embedded": True,
        "complete_plaintext_receipt": copy.deepcopy(receipt),
        "complete_first_party_source_owner_count": 3,
        "complete_first_party_source_owners": {
            role: base.synthetic_owner(item[:3], item[3])
            for role, item in ZIG_SOURCE.items()
        },
        "complete_source_contract_field_count": len(CONTRACT_KEYS),
        "complete_source_contract_embedded": True,
        "complete_source_contract": copy.deepcopy(contract),
        "complete_original_suite_count": 13,
        "complete_original_suite_rows": [
            compact_suite_proof(base, row)
            for row in receipt["original_suite_diagnostics"]
        ],
        "complete_public_archive_metadata": copy.deepcopy(receipt["archive"]),
        "validated_campaign_outcome": copy.deepcopy(facts),
        "compressed_archive_opened_by_graph": False,
        "private_build_root_opened_by_graph": False,
        "complete_warning_excerpts_preserved_without_archive": True,
        "complete_failure_diagnostics_available_without_archive": True,
    }
    pool = {
        "schema": POOL_SCHEMA,
        "version": 1,
        "hash_algorithm": "sha256",
        "complete_public_receipt_count": 1,
        "complete_first_party_source_owner_count": 3,
        "entries": {ZIG_RECEIPT[1]: entry},
    }
    validate_evidence_pool(base, pool, contract, receipt, facts)
    return pool


def validate_evidence_pool(
    base: types.ModuleType,
    pool: object,
    contract: dict,
    receipt: dict,
    facts: dict,
) -> None:
    base.need(
        type(pool) is dict
        and set(pool)
        == {
            "schema",
            "version",
            "hash_algorithm",
            "complete_public_receipt_count",
            "complete_first_party_source_owner_count",
            "entries",
        }
        and pool["schema"] == POOL_SCHEMA
        and pool["version"] == 1
        and pool["hash_algorithm"] == "sha256"
        and pool["complete_public_receipt_count"] == 1
        and pool["complete_first_party_source_owner_count"] == 3
        and type(pool["entries"]) is dict
        and set(pool["entries"]) == {ZIG_RECEIPT[1]},
        "require the one actual complete owner-addressed Zig V13 result",
    )
    assert isinstance(pool, dict)
    entry = pool["entries"][ZIG_RECEIPT[1]]
    rows = [
        compact_suite_proof(base, row)
        for row in receipt["original_suite_diagnostics"]
    ]
    base.need(
        type(entry) is dict
        and entry.get("schema") == ENTRY_SCHEMA
        and entry.get("family") == "zig"
        and base.canonical(entry.get("complete_plaintext_receipt_owner"))
        == base.canonical(base.synthetic_owner(ZIG_RECEIPT[:3], ZIG_RECEIPT[3]))
        and entry.get("complete_plaintext_receipt_sha256") == ZIG_RECEIPT[1]
        and entry.get("complete_plaintext_receipt_bytes") == ZIG_RECEIPT[2]
        and entry.get("complete_plaintext_receipt_field_count") == len(RECEIPT_KEYS)
        and entry.get("complete_plaintext_receipt_embedded") is True
        and base.canonical(entry.get("complete_plaintext_receipt"))
        == base.canonical(receipt)
        and entry.get("complete_first_party_source_owner_count") == 3
        and entry.get("complete_source_contract_field_count") == len(CONTRACT_KEYS)
        and entry.get("complete_source_contract_embedded") is True
        and base.canonical(entry.get("complete_source_contract"))
        == base.canonical(contract)
        and entry.get("complete_original_suite_count") == 13
        and base.canonical(entry.get("complete_original_suite_rows"))
        == base.canonical(rows)
        and base.canonical(entry.get("complete_public_archive_metadata"))
        == base.canonical(receipt["archive"])
        and base.canonical(entry.get("validated_campaign_outcome"))
        == base.canonical(facts)
        and entry.get("compressed_archive_opened_by_graph") is False
        and entry.get("private_build_root_opened_by_graph") is False
        and entry.get("complete_warning_excerpts_preserved_without_archive") is True
        and entry.get("complete_failure_diagnostics_available_without_archive") is True,
        "reject missing real Zig workers, warnings, source, or archive metadata",
    )
    owners = entry["complete_first_party_source_owners"]
    base.need(
        type(owners) is dict and set(owners) == set(ZIG_SOURCE),
        "retain exactly the three original independently pinned Zig source owners",
    )
    for role, item in ZIG_SOURCE.items():
        base.need(
            base.canonical(owners[role])
            == base.canonical(base.synthetic_owner(item[:3], item[3])),
            "reject a fabricated first-party Zig owner: " + role,
        )


def make_reference(base: types.ModuleType, pool: dict) -> dict:
    raw = base.canonical(pool["entries"][ZIG_RECEIPT[1]])
    return {
        "schema": REFERENCE_SCHEMA,
        "family": "zig",
        "complete_plaintext_receipt_sha256": ZIG_RECEIPT[1],
        "complete_plaintext_receipt_bytes": ZIG_RECEIPT[2],
        "complete_first_party_source_owner_count": 3,
        "complete_reference_sha256": base.digest(raw),
        "complete_reference_canonical_bytes": len(raw),
    }


def resolve_reference(
    base: types.ModuleType,
    pool: dict,
    value: object,
) -> dict:
    base.need(
        type(value) is dict
        and set(value)
        == {
            "schema",
            "family",
            "complete_plaintext_receipt_sha256",
            "complete_plaintext_receipt_bytes",
            "complete_first_party_source_owner_count",
            "complete_reference_sha256",
            "complete_reference_canonical_bytes",
        }
        and value["schema"] == REFERENCE_SCHEMA
        and value["family"] == "zig"
        and value["complete_plaintext_receipt_sha256"] == ZIG_RECEIPT[1]
        and value["complete_plaintext_receipt_bytes"] == ZIG_RECEIPT[2]
        and value["complete_first_party_source_owner_count"] == 3,
        "reject an omitted or invented actual Zig source and receipt reference",
    )
    assert isinstance(value, dict)
    entry = pool["entries"].get(ZIG_RECEIPT[1])
    raw = base.canonical(entry)
    base.need(
        type(entry) is dict
        and base.checked(value["complete_reference_sha256"], "whole Zig V13 proof")
        == base.digest(raw)
        and value["complete_reference_canonical_bytes"] == len(raw),
        "reject a fabricated actual Zig worker, warning, or failure proof",
    )
    return copy.deepcopy(entry)


def make_changes(reference: dict, facts: dict) -> dict:
    return {
        "actual_current_graph_predecessor_version": 93,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "v94_new_directly_authenticated_owner_count": 4,
        "v94_new_directly_authenticated_zig_source_owner_count": 3,
        "v94_new_directly_authenticated_zig_plaintext_receipt_owner_count": 1,
        "lossless_previous_v93_proof_pool_count": 15,
        "lossless_v93_all_fifteen_previous_pool_identity_status": "PASS",
        "lossless_v93_snapshot_identity_status": "PASS",
        "lossless_v93_family_identity_status": "PASS",
        "original_case_execution_denominator": CASE_COUNT,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "zig_v13_original_campaign_actual_worker_count": 13,
        "zig_v13_original_campaign_distinct_worker_count": 13,
        "zig_v13_original_campaign_attempted_suite_count": 13,
        "zig_v13_original_campaign_clean_suite_count": 7,
        "zig_v13_original_campaign_completed_suite_count": 12,
        "zig_v13_original_campaign_mismatch_suite_count": 5,
        "zig_v13_original_campaign_verified_passing_case_count": 4607,
        "zig_v13_original_campaign_observed_mismatch_lower_bound": 1700,
        "zig_v13_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "zig_v13_original_campaign_infrastructure_failure_count": 1,
        "zig_v13_original_campaign_infrastructure_failure_suite": "subinterpreter_v2",
        "zig_v13_original_campaign_worker_timeout_count": 0,
        "zig_v13_original_campaign_individually_proven_guarded_candidate_import_count":
        13,
        "zig_v13_original_campaign_candidate_import_status_unknown_count": 0,
        "zig_v13_original_campaign_actual_child_guards_installed": 0,
        "zig_v13_original_campaign_actual_child_interpreters_created": 0,
        "zig_v13_original_campaign_actual_child_case_interpreter_exec_calls": 0,
        "zig_v13_original_campaign_cleanup_warning_worker_count": 13,
        "zig_v13_original_campaign_cleanup_warning_captured_occurrence_lower_bound":
        143,
        "zig_v13_original_campaign_cleanup_warning_full_occurrence_count":
        "NOT MEASURED",
        "zig_v13_original_campaign_truncated_warning_excerpt_count": 12,
        "zig_v13_original_campaign_complete_warning_excerpt_count": 1,
        "zig_v13_original_campaign_warning_excerpt_total_bytes": 53211,
        "zig_v13_original_campaign_complete_stderr_metadata_total_bytes": 428866,
        "zig_v13_original_campaign_complete_stdout_metadata_total_bytes": 82236727,
        "zig_v13_original_campaign_remaining_subinterpreter_warning_worker_count": 1,
        "zig_v13_original_campaign_all_three_original_targets_restored": True,
        "zig_v13_original_campaign_candidate_status": "FAIL",
        "zig_v13_original_campaign_candidate_qualified": False,
        "current_aggregate_semantic_mismatch_counts": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "timing_trials_run": 0,
        "clock_samples_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "compressed_archives_opened_by_graph": 0,
        "private_build_roots_opened_by_graph": 0,
        "expanded_holdout_proposed_case_count": HOLDOUT_PROPOSAL_COUNT,
        "expanded_holdout_final_protocol_status": "NOT FROZEN",
        "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
        "preserved_previous_holdout_proposal_case_count":
        HISTORICAL_HOLDOUT_PROPOSAL_COUNT,
        "final_holdout_opened": False,
        "winner_selected": False,
        LATEST_KEY: copy.deepcopy(reference),
    }


def make_svg() -> bytes:
    rows = (
        ("Python re", CASE_COUNT, "13 complete groups; unchanged baseline", "BASELINE", "#34d399"),
        ("Rust", 15749, "10 clean; 2 differ; 1 incomplete", "NOT YET COMPATIBLE", "#fbbf24"),
        ("C", 13606, "3 clean; 4 differ; 6 execution failures", "NOT YET COMPATIBLE", "#fbbf24"),
        (
            "Zig",
            4607,
            "7 clean; 5 differ; 1 incomplete; warnings",
            "NOT YET COMPATIBLE",
            "#fbbf24",
        ),
        ("C++", None, "Full current result has not been measured", "NOT MEASURED", "#94a3b8"),
        ("Go", None, "Full current result has not been measured", "NOT MEASURED", "#94a3b8"),
        (
            "Fortran",
            None,
            "Builds disagreed; matching not measured",
            "BUILD FAILED",
            "#fb7185",
        ),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1020" '
        'viewBox="0 0 1440 1020" role="img" aria-labelledby="title description">',
        '<title id="title">How close are from-scratch alternatives to Python re?</title>',
        '<desc id="description">The bars show correctness, not speed. The standard Python '
        'baseline passes all 31,237 original checks. Rust has 15,749 verified passing '
        'checks; C has 13,606; Zig has 4,607. None is fully compatible. C++, Go, and '
        'Fortran do not have a measured complete current matching result. All thirteen '
        'actual Zig workers emitted cleanup warnings, with at least 143 warning examples '
        'captured in their excerpts; twelve excerpts are truncated, so the complete '
        'warning count is not measured. Zig has at least 1,700 actual mismatches and '
        'one genuine unfinished child-interpreter test with zero successfully created '
        'child interpreters or child guards. Speed and memory are not measured. The '
        'separate 8,244 checks are not added to the original denominator. The proposed '
        '14,155,776-case speed comparison is not frozen, generated, opened, or run. '
        'There is no winner.</desc>',
        '<rect width="1440" height="1020" rx="24" fill="#0b1220"/>',
        '<text x="46" y="65" fill="#f8fafc" font-size="32" '
        'font-family="system-ui,sans-serif" font-weight="740">'
        'Building a faster Python re, from scratch</text>',
        '<text x="47" y="103" fill="#cbd5e1" font-size="17" '
        'font-family="system-ui,sans-serif">'
        'Six independent approaches · no fully compatible replacement · no winner</text>',
        '<rect x="44" y="125" width="1352" height="78" rx="13" fill="#172338"/>',
        '<text x="63" y="155" fill="#f8fafc" font-size="16" '
        'font-family="system-ui,sans-serif" font-weight="690">'
        'These bars show matching correctness, not speed.</text>',
        '<text x="63" y="181" fill="#cbd5e1" font-size="14" '
        'font-family="system-ui,sans-serif">Each result uses the same 31,237 original '
        'Python checks. An unfinished or unmeasured check is never counted as a pass.</text>',
        '<text x="48" y="243" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">APPROACH</text>',
        '<text x="154" y="243" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">'
        'ORIGINAL CHECKS CONFIRMED</text>',
        '<text x="706" y="243" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">WHAT THE TESTS SHOW</text>',
        '<text x="1126" y="243" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">SPEED VS PYTHON</text>',
        '<text x="1393" y="243" text-anchor="end" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">RESULT</text>',
        '<line x1="44" y1="258" x2="1396" y2="258" stroke="#334155"/>',
    ]
    for index, (name, passed, details, result, colour) in enumerate(rows):
        y = 300 + 67 * index
        parts.append(
            f'<text x="49" y="{y}" fill="#f8fafc" font-size="16" '
            f'font-family="system-ui,sans-serif" font-weight="670">{name}</text>'
        )
        parts.append(
            f'<rect x="153" y="{y - 16}" width="314" height="20" '
            'rx="6" fill="#1e293b"/>'
        )
        if passed is None:
            count_label = "NOT MEASURED"
        else:
            width = max(3, round(314 * passed / CASE_COUNT))
            percent = 100 * passed / CASE_COUNT
            percent_label = "100%" if passed == CASE_COUNT else f"{percent:.1f}%"
            parts.append(
                f'<rect x="153" y="{y - 16}" width="{width}" height="20" '
                f'rx="6" fill="{colour}"/>'
            )
            count_label = f"{passed:,} / {CASE_COUNT:,} ({percent_label})"
        parts.append(
            f'<text x="478" y="{y}" fill="#e2e8f0" font-size="12" '
            f'font-family="system-ui,sans-serif">{count_label}</text>'
        )
        parts.append(
            f'<text x="706" y="{y}" fill="#cbd5e1" font-size="12" '
            f'font-family="system-ui,sans-serif">{details}</text>'
        )
        parts.append(
            f'<text x="1128" y="{y}" fill="#94a3b8" font-size="11" '
            'font-family="system-ui,sans-serif">NOT MEASURED</text>'
        )
        parts.append(
            f'<text x="1393" y="{y}" text-anchor="end" fill="{colour}" '
            f'font-size="10" font-family="system-ui,sans-serif" '
            f'font-weight="720">{result}</text>'
        )
    parts.extend((
        '<line x1="44" y1="747" x2="1396" y2="747" stroke="#334155"/>',
        '<text x="49" y="779" fill="#f8fafc" font-size="17" '
        'font-family="system-ui,sans-serif" font-weight="690">'
        'Why Zig is not a drop-in replacement yet</text>',
        '<text x="49" y="805" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">'
        'At least 1,700 real differences; all 13 test workers emitted cleanup warnings; '
        'at least 143 examples are visible in the saved excerpts.</text>',
        '<text x="49" y="829" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">'
        'Twelve warning excerpts are truncated, so the full warning count is '
        'NOT MEASURED. One child-interpreter test remains incomplete.</text>',
        '<text x="49" y="853" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">'
        'The failed child test created zero confirmed child interpreters and '
        'installed zero confirmed child guards.</text>',
        '<rect x="44" y="871" width="1352" height="104" rx="13" fill="#172338"/>',
        '<text x="63" y="900" fill="#f8fafc" font-size="16" '
        'font-family="system-ui,sans-serif" font-weight="680">'
        'Future speed comparison: proposed 14,155,776 cases</text>',
        '<text x="63" y="925" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">'
        'NOT FROZEN · NOT GENERATED · NOT OPENED · NOT RUN. '
        'Speed, memory, confidence, and rankings: NOT MEASURED.</text>',
        '<text x="63" y="949" fill="#cbd5e1" font-size="12" '
        'font-family="system-ui,sans-serif">'
        'The separate 8,244 reference checks are not added to the 31,237 original '
        'checks. All previous results remain preserved.</text>',
        '<text x="49" y="1001" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif">'
        'Overview 94 · original test results only · no full replacement · no speed '
        'claim · no winner</text>',
        "</svg>",
        "",
    ))
    return "\n".join(parts).encode("utf-8")


def validate_families(
    base: types.ModuleType,
    old: dict,
    families: object,
    pool: dict,
    reference: dict,
    facts: dict,
) -> None:
    base.need(
        type(families) is list
        and len(families) == 7
        and [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "retain standard Python and every original independent engine family",
    )
    assert isinstance(families, list)
    for row, original in zip(families, old["families"], strict=True):
        family = original["family"]
        base.need(
            type(row) is dict and row.get("family") == family,
            "reject a removed, renamed, or invented engine family: " + family,
        )
        if family == "python":
            base.need(
                base.canonical(row) == base.canonical(original),
                "preserve every unchanged original Python baseline field",
            )
            continue
        base.need(
            row.get("authenticated_evidence_owner_lower_bound") == EVIDENCE_FLOOR
            and row.get("authenticated_history_reference_lower_bound") == HISTORY_FLOOR
            and row.get("qualified") is False
            and row.get("runtime_no_delegation") == "NOT ESTABLISHED"
            and row.get("performance") == "NOT MEASURED",
            "reject invented candidate compatibility, speed, or independence: " + family,
        )
        restored = copy.deepcopy(row)
        restored["authenticated_evidence_owner_lower_bound"] = original[
            "authenticated_evidence_owner_lower_bound"
        ]
        restored["authenticated_history_reference_lower_bound"] = original[
            "authenticated_history_reference_lower_bound"
        ]
        if family == "zig":
            proof = resolve_reference(base, pool, row.get(LATEST_KEY))
            base.need(
                base.canonical(proof["validated_campaign_outcome"])
                == base.canonical(facts)
                and base.canonical(row.get("v94_latest_original_campaign"))
                == base.canonical(facts)
                and base.canonical(row.get(LATEST_KEY)) == base.canonical(reference),
                "retain real warning-bearing Zig evidence without claiming a repair",
            )
            restored.pop(LATEST_KEY)
            restored.pop("v94_latest_original_campaign")
        base.need(
            base.canonical(restored) == base.canonical(original),
            "retain the entire original V93 family and its historical evidence: "
            + family,
        )


def build(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> tuple[dict, dict[str, bytes]]:
    base.need(
        options.source_sha256 is not None
        and type(options.source_bytes) is int
        and 0 < options.source_bytes <= OWNER_LIMIT,
        "caller-pin the whole immutable V94 renderer source",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "whole immutable V94 renderer"),
        options.source_bytes,
        private=True,
    )
    for role, item in V93.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin the complete actual published V93 " + role,
        )
    for role, item in ZIG_SOURCE.items():
        base.need(
            getattr(options, "zig_" + role + "_sha256") == item[1],
            "caller-pin the exact first-party Zig V13 " + role,
        )
    base.need(
        options.zig_receipt_sha256 == ZIG_RECEIPT[1],
        "caller-pin the complete actual public Zig campaign receipt",
    )
    old = authenticate_previous(previous, chain, base)
    contract, receipt, facts = load_zig_evidence(base)
    pool = make_evidence_pool(base, contract, receipt, facts)
    reference = make_reference(base, pool)
    changes = make_changes(reference, facts)
    predecessor = {
        role: base.pin(item[0], item[1], item[2]) for role, item in V93.items()
    }
    source_owners = {
        role: base.pin(item[0], item[1], item[2])
        for role, item in ZIG_SOURCE.items()
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update({
        "schema": SCHEMA + "-compact-current-snapshot",
        "version": 94,
        "previous_complete_snapshot_sha256": V93_SNAPSHOT_SHA256,
        "previous_complete_snapshot_canonical_bytes": V93_SNAPSHOT_BYTES,
        "previous_complete_overview_sha256": V93["summary"][1],
        "previous_complete_overview_bytes": V93["summary"][2],
        **copy.deepcopy(changes),
    })
    headline = copy.deepcopy(old["headline"])
    headline["verified_original_checks_by_candidate"]["zig"] = 4607
    headline["latest_complete_candidate_mismatch_totals"] = "NOT MEASURED"
    headline["fully_compatible_candidate_count"] = 0
    headline["performance"] = "NOT MEASURED"
    headline["memory"] = "NOT MEASURED"
    headline["winner_selected"] = False
    headline["bars_measure"] = "VERIFIED ORIGINAL CORRECTNESS CHECKS; NOT SPEED"
    headline["speed_relative_to_python"] = "NOT MEASURED"
    headline["zig_cleanup_warning_worker_count"] = 13
    headline["zig_cleanup_warning_captured_occurrence_lower_bound"] = 143
    headline["zig_cleanup_warning_total_occurrence_count"] = "NOT MEASURED"
    headline["zig_incomplete_original_suite_count"] = 1
    inputs = {
        "schema": SCHEMA + "-inputs",
        "version": 94,
        "python": "3.14.6",
        "renderer": base.pin(SELF, options.source_sha256, len(own)),
        "previous_overview": copy.deepcopy(predecessor),
        "zig_v13_source_owners": copy.deepcopy(source_owners),
        "zig_v13_plaintext_receipt_owner": base.pin(
            ZIG_RECEIPT[0], ZIG_RECEIPT[1], ZIG_RECEIPT[2]
        ),
        "headline": copy.deepcopy(headline),
        "snapshot": copy.deepcopy(snapshot),
        "complete_original_suites": [
            {"suite": suite, "case_execution_denominator": count}
            for suite, count in SUITES
        ],
        **copy.deepcopy(changes),
    }
    families = copy.deepcopy(old["families"])
    for row in families:
        family = row["family"]
        if family == "python":
            continue
        row["authenticated_evidence_owner_lower_bound"] = EVIDENCE_FLOOR
        row["authenticated_history_reference_lower_bound"] = HISTORY_FLOOR
        if family == "zig":
            row[LATEST_KEY] = copy.deepcopy(reference)
            row["v94_latest_original_campaign"] = copy.deepcopy(facts)
    validate_families(base, old, families, pool, reference, facts)
    inputs_raw = base.canonical(inputs)
    svg_raw = make_svg()
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 94,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, options.source_sha256, len(own)),
        "inputs": base.pin(INPUT_PATH, base.digest(inputs_raw), len(inputs_raw)),
        "svg": base.pin(SVG_PATH, base.digest(svg_raw), len(svg_raw)),
        "previous_overview": copy.deepcopy(predecessor),
        "previous_v93_snapshot": copy.deepcopy(old["snapshot"]),
        "previous_v93_snapshot_canonical_sha256": V93_SNAPSHOT_SHA256,
        "previous_v93_snapshot_canonical_bytes": V93_SNAPSHOT_BYTES,
        "snapshot": copy.deepcopy(snapshot),
        "headline": copy.deepcopy(headline),
        "families": families,
        POOL_KEY: pool,
        "lossless_v94_zig_v13_complete_plaintext_receipt_count": 1,
        "lossless_v94_zig_v13_complete_source_owner_count": 3,
        "lossless_v94_zig_v13_complete_original_suite_count": 13,
        "preserved_v93_latest_original_campaigns": copy.deepcopy(
            old["latest_original_campaigns"]
        ),
        "latest_original_campaigns": {
            **copy.deepcopy(old["latest_original_campaigns"]),
            "zig": copy.deepcopy(facts),
        },
        **copy.deepcopy(changes),
    })
    for key, size, expected, count in previous_pools(previous):
        raw = base.canonical(summary[key])
        base.need(
            len(raw) == size
            and base.digest(raw) == expected
            and base.canonical(summary[key]) == base.canonical(old[key])
            and len(summary[key]["entries"]) == count,
            "preserve every original V93 pool without changing a byte: " + key,
        )
    base.need(
        base.canonical(summary["previous_v93_snapshot"])
        == base.canonical(old["snapshot"])
        and base.canonical(summary["previous_v92_snapshot"])
        == base.canonical(old["previous_v92_snapshot"])
        and base.canonical(summary["previous_v91_snapshot"])
        == base.canonical(old["previous_v91_snapshot"])
        and base.canonical(summary["previous_v90_snapshot"])
        == base.canonical(old["previous_v90_snapshot"])
        and base.canonical(summary["previous_v89_snapshot"])
        == base.canonical(old["previous_v89_snapshot"])
        and base.canonical(summary["previous_v88_snapshot"])
        == base.canonical(old["previous_v88_snapshot"])
        and base.canonical(summary["families"][0])
        == base.canonical(old["families"][0])
        and base.canonical(summary["latest_original_campaigns"]["rust"])
        == base.canonical(old["latest_original_campaigns"]["rust"])
        and base.canonical(summary["latest_original_campaigns"]["c"])
        == base.canonical(old["latest_original_campaigns"]["c"])
        and base.canonical(summary["preserved_v93_latest_original_campaigns"]["zig"])
        == base.canonical(old["latest_original_campaigns"]["zig"])
        and summary["rust_v20_original_campaign_verified_passing_case_count"] == 15749
        and summary["rust_v20_original_campaign_observed_mismatch_lower_bound"] == 1296
        and summary["c_v9_original_campaign_verified_passing_case_count"] == 13606
        and summary["c_v9_original_campaign_observed_mismatch_lower_bound"] == 492
        and summary["c_v9_original_campaign_candidate_execution_failure_count"] == 6
        and summary["zig_v12_original_campaign_verified_passing_case_count"] == 4607
        and summary["zig_v12_original_campaign_observed_mismatch_lower_bound"] == 1700
        and summary["zig_v13_original_campaign_verified_passing_case_count"] == 4607
        and summary["zig_v13_original_campaign_observed_mismatch_lower_bound"] == 1700
        and summary["zig_v13_original_campaign_cleanup_warning_worker_count"] == 13
        and summary["zig_v13_original_campaign_cleanup_warning_captured_occurrence_lower_bound"]
        == 143
        and summary["zig_v13_original_campaign_cleanup_warning_full_occurrence_count"]
        == "NOT MEASURED"
        and summary["zig_v13_original_campaign_actual_child_guards_installed"] == 0
        and summary["zig_v13_original_campaign_actual_child_interpreters_created"] == 0
        and summary["authenticated_evidence_owner_lower_bound"] == EVIDENCE_FLOOR
        and summary["authenticated_history_reference_lower_bound"] == HISTORY_FLOOR
        and summary["qualified_candidate_count"] == 0
        and summary["performance"] == "NOT MEASURED"
        and summary["memory"] == "NOT MEASURED"
        and summary["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and summary["expanded_holdout_case_status"] == "NOT GENERATED; NOT OPENED"
        and summary["final_holdout_opened"] is False
        and summary["winner_selected"] is False,
        "retain all real history, Zig warnings, failures, and unopened comparison",
    )
    validate_evidence_pool(base, summary[POOL_KEY], contract, receipt, facts)
    recovered = resolve_reference(base, pool, reference)
    base.need(
        base.canonical(recovered["validated_campaign_outcome"]) == base.canonical(facts)
        and base.canonical(summary[LATEST_KEY]) == base.canonical(reference)
        and base.canonical(snapshot[LATEST_KEY]) == base.canonical(reference)
        and base.canonical(inputs[LATEST_KEY]) == base.canonical(reference),
        "retain a complete independently recoverable genuine Zig campaign result",
    )
    assets = {
        INPUT_PATH: inputs_raw,
        SUMMARY_PATH: base.canonical(summary),
        SVG_PATH: svg_raw,
    }
    for path, raw in assets.items():
        base.need(
            type(raw) is bytes and 0 < len(raw) <= min(OWNER_LIMIT, base.OWNER_LIMIT),
            "reject oversized V94 evidence before any possible publication: " + path,
        )
    return snapshot, assets


def self_test(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> dict:
    prior = previous.self_test(*chain, previous_options(previous))
    base.need(
        prior.get("status") == "PASS"
        and prior.get("version") == 93
        and type(prior.get("rejected_hostile_control_count")) is int
        and prior["rejected_hostile_control_count"] >= 11227
        and prior.get("authenticated_evidence_owner_lower_bound") == 328
        and prior.get("authenticated_history_reference_lower_bound") == 333
        and prior.get("lossless_previous_v92_proof_pool_count") == 14
        and prior.get("lossless_v92_all_fourteen_previous_pool_identity_status") == "PASS"
        and prior.get("lossless_v93_c_v9_complete_original_suite_count") == 13
        and prior.get("c_v9_original_campaign_verified_passing_case_count") == 13606
        and prior.get("rust_v20_original_campaign_verified_passing_case_count") == 15749
        and prior.get("zig_v12_original_campaign_verified_passing_case_count") == 4607
        and prior.get("expanded_holdout_proposed_case_count") == HOLDOUT_PROPOSAL_COUNT
        and prior.get("qualified_candidate_count") == 0
        and prior.get("performance") == "NOT MEASURED"
        and prior.get("outputs_written") is False,
        "preserve all inherited published V93 hostile controls without fabricating them",
    )
    _, assets = build(previous, chain, base, options)
    old = authenticate_previous(previous, chain, base)
    contract, receipt, facts = load_zig_evidence(base)
    summary = base.document(assets[SUMMARY_PATH], "whole in-memory V94 summary")
    pool = summary[POOL_KEY]
    reference = summary[LATEST_KEY]
    rejected = 0

    def reject(label: str, callback: object) -> None:
        nonlocal rejected
        try:
            if not callable(callback):
                raise ValueError("require a callable hostile control")
            callback()
        except Exception:
            rejected += 1
        else:
            base.need(False, "V94 accepted fabricated evidence: " + label)

    for key in sorted(CONTRACT_KEYS):
        forged = copy.deepcopy(contract)
        forged.pop(key)
        reject(
            "omitted complete Zig source field " + key,
            lambda value=forged: validate_source_contract(base, value),
        )
    for key, wrong in (
        ("schema", "invented-source"),
        ("version", 12),
        ("family", "regex"),
        ("corrected_original_matching", "PASS"),
        ("corrected_supplemental_matching", "PASS"),
        ("qualified_candidate_count", 1),
        ("repaired_warning", "PASS"),
        ("repaired_subinterpreter", "PASS"),
        ("runtime_non_delegation", "PASS"),
        ("holdout", "OPENED"),
        ("performance", "FASTER"),
        ("memory", "MEASURED"),
        ("undefined_behavior", "PASS"),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(contract)
        forged[key] = wrong
        reject(
            "forged first-party Zig source field " + key,
            lambda value=forged: validate_source_contract(base, value),
        )
    for key in sorted(RECEIPT_KEYS):
        forged = copy.deepcopy(receipt)
        forged.pop(key)
        reject(
            "omitted actual Zig receipt field " + key,
            lambda value=forged: validate_zig_receipt(base, value),
        )
    for key, wrong in (
        ("schema", "invented-receipt"),
        ("status", "FAIL"),
        ("publication_pass_means", "CANDIDATE PASS"),
        ("candidate_status", "PASS"),
        ("candidate_qualified", True),
        ("original_campaign_passed", True),
        ("case_execution_denominator", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("suite_count", 12),
        ("actual_candidate_workers", 12),
        ("unique_candidate_worker_count", 12),
        ("completed_suite_count", 13),
        ("verified_passing_case_count", CASE_COUNT),
        ("observed_semantic_mismatch_lower_bound", 0),
        ("semantic_mismatch_count", 1700),
        ("infrastructure_failure_count", 0),
        ("timeout_count", 1),
        ("supplemental_candidate_matching", "PASS"),
        ("hidden_cases_read", 1),
        ("benchmark_files_read", 1),
        ("timing_trials_run", 1),
        ("holdout", "OPENED"),
        ("performance", "FASTER"),
        ("memory", "MEASURED"),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(receipt)
        forged[key] = wrong
        reject(
            "forged actual Zig publication field " + key,
            lambda value=forged: validate_zig_receipt(base, value),
        )
    for index, (suite, _) in enumerate(SUITES):
        for key in sorted(ROW_KEYS):
            forged = copy.deepcopy(receipt)
            forged["original_suite_diagnostics"][index].pop(key)
            reject(
                "omitted real Zig worker " + suite + ":" + key,
                lambda value=forged: validate_zig_receipt(base, value),
            )
        for field, wrong in (
            ("suite", "invented"),
            ("pid", 0),
            ("guard_installed_before_candidate_import", False),
            ("candidate_imported", False),
            ("case_execution_denominator", 0),
            ("timed_out", True),
        ):
            forged = copy.deepcopy(receipt)
            forged["original_suite_diagnostics"][index][field] = wrong
            reject(
                "fabricated genuine Zig worker " + suite + ":" + field,
                lambda value=forged: validate_zig_receipt(base, value),
            )
        for field, wrong in (
            ("text", "warnings fixed"),
            ("sha256", "0" * 64),
            ("total_bytes", 0),
            ("status", "NOT CAPTURED"),
        ):
            forged = copy.deepcopy(receipt)
            forged["original_suite_diagnostics"][index]["stderr_literal_excerpt"][
                field
            ] = wrong
            reject(
                "hidden real Zig cleanup warning " + suite + ":" + field,
                lambda value=forged: validate_zig_receipt(base, value),
            )
    for key, size, expected, count in previous_pools(previous):
        forged = copy.deepcopy(old)
        forged.pop(key)
        reject(
            "omitted whole prior V93 proof pool " + key,
            lambda value=forged: validate_previous(previous, base, value),
        )
        forged = copy.deepcopy(old)
        forged[key]["entries"] = {}
        reject(
            "discarded complete prior V93 proof pool " + key,
            lambda value=forged: validate_previous(previous, base, value),
        )
    for key, wrong in (
        ("version", 92),
        ("authenticated_evidence_owner_lower_bound", 329),
        ("authenticated_history_reference_lower_bound", 334),
        ("original_case_execution_denominator", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("qualified_candidate_count", 1),
        ("performance", "FASTER"),
        ("expanded_holdout_case_status", "OPENED"),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(old)
        forged[key] = wrong
        reject(
            "fabricated immutable V93 history " + key,
            lambda value=forged: validate_previous(previous, base, value),
        )
    for field, wrong in (
        ("complete_plaintext_receipt_sha256", "0" * 64),
        ("complete_plaintext_receipt_bytes", 1),
        ("complete_reference_sha256", "0" * 64),
        ("complete_reference_canonical_bytes", 1),
        ("family", "rust"),
    ):
        forged = copy.deepcopy(reference)
        forged[field] = wrong
        reject(
            "fabricated complete Zig campaign reference " + field,
            lambda value=forged: resolve_reference(base, pool, value),
        )
    for field in (
        "complete_plaintext_receipt",
        "complete_source_contract",
        "complete_original_suite_rows",
        "validated_campaign_outcome",
    ):
        forged = copy.deepcopy(pool)
        forged["entries"][ZIG_RECEIPT[1]].pop(field)
        reject(
            "omitted complete actual Zig proof " + field,
            lambda value=forged: validate_evidence_pool(
                base, value, contract, receipt, facts
            ),
        )
    for event, arguments in (
        ("subprocess.Popen", ("candidate",)),
        ("os.posix_spawn", ("candidate",)),
        ("os.fork", ()),
        ("ctypes.dlopen", ("candidate.so",)),
        ("socket.connect", ("holdout",)),
        ("os.remove", (str(ROOT / "GOAL.md"),)),
        ("os.rename", (str(ROOT / "GOAL.md"), str(ROOT / "forged"))),
        ("os.mkdir", (str(ROOT / "private"),)),
        ("import", ("re", None, None, None, None)),
        ("import", ("_sre", None, None, None, None)),
        ("import", ("regex", None, None, None, None)),
        ("import", ("candidates.zig_candidate", None, None, None, None)),
        ("import", ("gzip", None, None, None, None)),
        ("import", ("time", None, None, None, None)),
        ("open", (str(ROOT / SVG_PATH), None, os.O_RDONLY)),
        ("open", (str(ROOT / INPUT_PATH), None, os.O_RDONLY)),
        ("open", (str(ROOT / SUMMARY_PATH), None, os.O_RDONLY)),
        ("open", (str(ROOT / "performance/holdout.json"), None, os.O_RDONLY)),
        ("open", (str(ROOT / "private.json.gz"), None, os.O_RDONLY)),
        ("open", (str(ROOT / "candidates/_zig_probe.so"), None, os.O_RDONLY)),
        ("open", (str(ROOT / "new-file"), None, os.O_WRONLY | os.O_CREAT)),
        ("open", ("/tmp/private-root", None, os.O_RDONLY)),
    ):
        reject(
            "forbidden source-only effect " + event,
            lambda name=event, values=arguments: audit_wall(name, values),
        )
    base.need(rejected >= 600, "require complete new Zig V13 hostile controls")
    return result_payload(base, options, assets, False, {
        "schema": SCHEMA + "-source-only-self-test",
        "inherited_rejected_hostile_control_count":
        prior["rejected_hostile_control_count"],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count":
        prior["rejected_hostile_control_count"] + rejected,
    })


def result_payload(
    base: types.ModuleType,
    options: argparse.Namespace,
    assets: dict[str, bytes],
    outputs_written: bool,
    additional: dict | None = None,
) -> dict:
    result = {
        "schema": SCHEMA + (
            "-published" if outputs_written else "-source-only-frozen-context"
        ),
        "version": 94,
        "status": "PASS",
        "source_sha256": options.source_sha256,
        "source_bytes": options.source_bytes,
        "inputs_sha256": base.digest(assets[INPUT_PATH]),
        "inputs_bytes": len(assets[INPUT_PATH]),
        "summary_sha256": base.digest(assets[SUMMARY_PATH]),
        "summary_bytes": len(assets[SUMMARY_PATH]),
        "svg_sha256": base.digest(assets[SVG_PATH]),
        "svg_bytes": len(assets[SVG_PATH]),
        "actual_current_graph_predecessor_version": 93,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "v94_new_directly_authenticated_owner_count": 4,
        "v94_new_directly_authenticated_zig_source_owner_count": 3,
        "v94_new_directly_authenticated_zig_plaintext_receipt_owner_count": 1,
        "lossless_previous_v93_proof_pool_count": 15,
        "lossless_v93_all_fifteen_previous_pool_identity_status": "PASS",
        "lossless_v93_snapshot_identity_status": "PASS",
        "lossless_v93_family_identity_status": "PASS",
        "lossless_v93_c_v9_complete_original_suite_count": 13,
        "lossless_v94_zig_v13_complete_plaintext_receipt_count": 1,
        "lossless_v94_zig_v13_complete_source_owner_count": 3,
        "lossless_v94_zig_v13_complete_original_suite_count": 13,
        "original_case_execution_denominator": CASE_COUNT,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "rust_v20_original_campaign_verified_passing_case_count": 15749,
        "rust_v20_original_campaign_observed_mismatch_lower_bound": 1296,
        "c_v9_original_campaign_verified_passing_case_count": 13606,
        "c_v9_original_campaign_observed_mismatch_lower_bound": 492,
        "c_v9_original_campaign_candidate_execution_failure_count": 6,
        "zig_v12_original_campaign_verified_passing_case_count": 4607,
        "zig_v12_original_campaign_observed_mismatch_lower_bound": 1700,
        "zig_v13_original_campaign_actual_worker_count": 13,
        "zig_v13_original_campaign_distinct_worker_count": 13,
        "zig_v13_original_campaign_clean_suite_count": 7,
        "zig_v13_original_campaign_completed_suite_count": 12,
        "zig_v13_original_campaign_mismatch_suite_count": 5,
        "zig_v13_original_campaign_verified_passing_case_count": 4607,
        "zig_v13_original_campaign_observed_mismatch_lower_bound": 1700,
        "zig_v13_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "zig_v13_original_campaign_infrastructure_failure_count": 1,
        "zig_v13_original_campaign_worker_timeout_count": 0,
        "zig_v13_original_campaign_actual_child_guards_installed": 0,
        "zig_v13_original_campaign_actual_child_interpreters_created": 0,
        "zig_v13_original_campaign_actual_child_case_interpreter_exec_calls": 0,
        "zig_v13_original_campaign_cleanup_warning_worker_count": 13,
        "zig_v13_original_campaign_cleanup_warning_captured_occurrence_lower_bound":
        143,
        "zig_v13_original_campaign_cleanup_warning_full_occurrence_count":
        "NOT MEASURED",
        "zig_v13_original_campaign_truncated_warning_excerpt_count": 12,
        "zig_v13_original_campaign_complete_warning_excerpt_count": 1,
        "zig_v13_original_campaign_warning_excerpt_total_bytes": 53211,
        "zig_v13_original_campaign_complete_stderr_metadata_total_bytes": 428866,
        "zig_v13_original_campaign_complete_stdout_metadata_total_bytes": 82236727,
        "zig_v13_original_campaign_candidate_status": "FAIL",
        "zig_v13_original_campaign_candidate_qualified": False,
        "expanded_holdout_proposed_case_count": HOLDOUT_PROPOSAL_COUNT,
        "preserved_previous_holdout_proposal_case_count":
        HISTORICAL_HOLDOUT_PROPOSAL_COUNT,
        "expanded_holdout_status": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "compressed_archives_opened_by_graph": 0,
        "private_build_roots_opened_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "clock_samples_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "qualified_candidate_count": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
        "outputs_written": outputs_written,
    }
    if additional:
        result.update(additional)
    return result


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path in {INPUT_PATH, SUMMARY_PATH, SVG_PATH}
        and type(raw) is bytes
        and 0 < len(raw) <= min(OWNER_LIMIT, base.OWNER_LIMIT),
        "publish only a bounded, exclusively created V94 graph owner",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0, "publish complete V94 bytes")
            remaining = remaining[count:]
        os.fsync(handle)
        owner = os.fstat(handle)
        base.need(
            owner.st_uid == os.geteuid()
            and owner.st_dev == 2064
            and owner.st_nlink == 1
            and owner.st_size == len(raw)
            and stat.S_IMODE(owner.st_mode) == 0o600,
            "authenticate the entire exclusively created V94 graph owner",
        )
    finally:
        os.close(handle)
    directory = os.open(
        str(ROOT / "docs/evidence"),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    actual, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(actual == raw, "reauthenticate every complete final V94 graph byte")


def parse(arguments: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-preview", action="store_true")
    modes.add_argument("--render", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", required=True, type=int)
    for role in V93:
        parser.add_argument("--previous-" + role + "-sha256", required=True)
    for role in ZIG_SOURCE:
        parser.add_argument("--zig-" + role + "-sha256", required=True)
    parser.add_argument("--zig-receipt-sha256", required=True)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse(arguments)
    try:
        previous, chain, base = load_previous()
        if not options.render:
            sys.addaudithook(audit_wall)
        if options.self_test:
            result = self_test(previous, chain, base, options)
        else:
            _, assets = build(previous, chain, base, options)
            if options.render:
                for path, raw in assets.items():
                    publish(base, path, raw)
            result = result_payload(base, options, assets, bool(options.render))
            if options.render_preview:
                result["schema"] = SCHEMA + "-source-only-render-preview"
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except Exception as error:
        sys.stderr.write("current V94 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
