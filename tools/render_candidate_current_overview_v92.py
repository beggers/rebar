#!/usr/bin/env python3
"""Show honestly how six from-scratch Python re replacements compare."""

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
SELF = "tools/render_candidate_current_overview_v92.py"
OUTPUT = "docs/evidence/candidate-current-overview-v92"
INPUT_PATH = OUTPUT + ".inputs.json"
SUMMARY_PATH = OUTPUT + ".summary.json"
SVG_PATH = OUTPUT + ".svg"
SCHEMA = "rebar-candidate-current-overview-v92"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
OWNER_LIMIT = 4 * 1024 * 1024
CASE_COUNT = 31237
SUPPLEMENTAL_CASE_COUNT = 8244
HOLDOUT_PROPOSAL_COUNT = 14155776
HISTORICAL_HOLDOUT_PROPOSAL_COUNT = 4194304
EVIDENCE_FLOOR = 324
HISTORY_FLOOR = 329

V91 = {
    "source": (
        "tools/render_candidate_current_overview_v91.py",
        "eec50d8322ef5d758a87af98b4e743446d36baf65bb1bcf198d350ee920dd051",
        76493,
        430337,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v91.inputs.json",
        "bb6f09340769e8c3429e312cca2ff4ae4a63d2d7ec5774a851afebb5cf3a592e",
        11440,
        430450,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v91.summary.json",
        "7a137275712f6ea18055c45922bc0c28babc0e9d933732bf574670bff76c6009",
        3252202,
        430451,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v91.svg",
        "65f03d0b14f80a17f82e172ece9b6b92548b05e1dd1024c770d7766115d3aa18",
        9062,
        430452,
    ),
}

ZIG_SOURCE = {
    "source": (
        "tools/run_owned_repaired_zig_original_campaign_v12.py",
        "329c8ac8c50b3f61fc176e07267f9771a3878167e9ab5eb9246e06cafac31cf8",
        251811,
        430069,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V12.md",
        "10bf90c29b0f23759acb3ea30ae9b364f90a9937d9b41388095b839e5ff5f551",
        5361,
        524830,
    ),
    "contract": (
        "oracle/phase2/repaired-zig-original-campaign-v12.json",
        "97a04675f4f8afc4a44061979a0a856bff2f5bb8cb9ed1381e6ee52168156b07",
        46081,
        524831,
    ),
}

ZIG_RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-zig-original-campaign-v12-phase2-v13-zig-guard-clean-v1-"
    "original-p0-v12-failures-publication-receipt.json",
    "ce7605be25bbb71e1b06b65b9aa3f79cfd09b39f0ce5f076ed9d986f15ee8de9",
    77604,
    524975,
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

OLD_POOLS = (
    (
        "lossless_family_evidence_pool", 126464,
        "5e82ece260c65c1b651512bf82cc952f6b5c9219e2baf5526148fc254b9a0570", 9,
    ),
    (
        "lossless_actual_outcome_evidence_pool", 33507,
        "8adefd9ea0901086064674c4a9ba1300792a15ba381ffe93a0ef85c372dd345a", 1,
    ),
    (
        "lossless_zig_source_evidence_pool", 23792,
        "1c4694aae8738a74713ddca5f9e88a83b4fdc0c81ddeac7bbfa30eb5db65f029", 1,
    ),
    (
        "lossless_zig_actual_build_evidence_pool", 248256,
        "437c0d0f2f80e841fa7091d50b2094f9054e82c0e792f5db9de817cf2609dcae", 1,
    ),
    (
        "lossless_v87_source_evidence_pool", 71364,
        "c4acf498232c0e95b3bb6c7425acb2258915e9fc369e66bd27b8e6bfd8c389ff", 6,
    ),
    (
        "lossless_v87_rust_actual_build_evidence_pool", 11169,
        "7dadc62631aa838cfaa2a0c96d978b1457de11a4d3501fc2a6b456b319a30c21", 1,
    ),
    (
        "lossless_v88_captured_source_evidence_pool", 19857,
        "ea9c5c1778e361c58e684e2d5e139a276af7751887f8a0e671df260080e2afa9", 1,
    ),
    (
        "lossless_v88_captured_actual_build_evidence_pool", 11916,
        "01ee89ebdcf462cc2fc61721110bc94d4177deb1949e66d6c350909992cc58e9", 1,
    ),
    (
        "lossless_v88_c_source_evidence_pool", 19315,
        "2818bd96e62af5aa82b3ee0e0f03f8cbe56ac54955599e32379755e8dd366d1b", 1,
    ),
    (
        "lossless_v88_c_actual_build_evidence_pool", 14406,
        "264678f27d7ee4d2965d42f3129941ee49a5b041f66b16d090e629675bd3dd00", 1,
    ),
    (
        "lossless_v89_original_campaign_receipt_reference_pool", 19205,
        "5627d67752d6efaefea4c77d2904c32d568b32eaeed06ad721727f3753f632d7", 3,
    ),
    (
        "lossless_v90_zig_v10_original_campaign_evidence_pool", 137388,
        "28e58f4d3ce45cf90eaac4e5e6698c603fd6b128b6ca6b799d79e200884d432f", 1,
    ),
    (
        "lossless_v91_rust_v20_original_campaign_evidence_pool", 83702,
        "8346e978978f837f092f2030f26522847cbbd5f473da96eab062212304d52a18", 1,
    ),
)

POOL_KEY = "lossless_v92_zig_v12_original_campaign_evidence_pool"
POOL_SCHEMA = SCHEMA + "-lossless-complete-zig-original-campaign-pool-v1"
ENTRY_SCHEMA = SCHEMA + "-lossless-complete-zig-original-campaign-entry-v1"
REFERENCE_SCHEMA = SCHEMA + "-complete-zig-original-campaign-reference-v1"
LATEST_KEY = "zig_v12_actual_original_campaign"
MISMATCHES = {
    "scanner_verbose_v1": 620,
    "public_types_v1": 248,
    "substitution_v2": 64,
    "shape_v2": 672,
    "public_surface_v19": 96,
}

STREAMS = {
    "original_bounded_v5": (
        44574,
        "bc8f0168569af04a36af1ec47e32030fca79e96c8543f43619a08677dec62dc9",
        137216,
        "0beca0304d82b71f2dede3c743c8a54f8fb0960d180dc0f6e2229e8f5895826f",
    ),
    "public_v3": (
        1548745,
        "d4c23cfacdd285aa0b8e87ddada0ec92d62bf1555bb82a916d783d9ab911587f",
        16884,
        "72fae8306fdd0df19a09bb895e99e3555ab0c51b469e80c8ac268196dd864945",
    ),
    "scanner_v3": (
        2245777,
        "01ed41747f0255b38769b0f5dbaa854219083fec9e0830a2f7292e1f7d6b93ed",
        4288,
        "b83d3bcda976d5936491a8408183d6c20bf74f6839ce704dd592316b52feee16",
    ),
    "buffer_v3": (
        675496,
        "a1b8bfc4f1ebb7b190a860d43a71b430dffb889e267ce406a4563358caaab7b4",
        7504,
        "f822cc7ba4160d6d7e36abfebbd67506e5015c586a451c60d9d689bd90b44f33",
    ),
    "managed_v1": (
        5394966,
        "0959c3d646fb6557c51a4f8b79668b5ee5f29fefc724aacbd256d4252a3b9c03",
        8040,
        "53cf620218572bb12d9c1adbc4c4516e2cea5bb9e7a663903384d50774b8da4a",
    ),
    "scanner_verbose_v1": (
        4574932,
        "abbcb83908efc25da650c9cb1d5539822a98538d7be4a37ba0a74cda5607885c",
        4288,
        "d2d1b6074a7cc5e8b5602993016ade6a989917b107f2176d276265edac827543",
    ),
    "public_types_v1": (
        15965045,
        "c5f0dbdbe601ee19c1ee6a29e31c528a5bbd6d93f59e88aa38928a0d3b50a977",
        51456,
        "d6f62d9f31770329f2d0fb73f8baff1d3a3c8200750438cf8cc3feac4ec514ba",
    ),
    "substitution_v2": (
        14567422,
        "bdc9ca44111b87bdb938b7a3661ab62b29f94ed300efcd3c4502951232422ce2",
        13936,
        "f7a3bba6fdbc1dd4d6310df2d092208ef15b830fe82b2348be2686c2ae83741c",
    ),
    "shape_v2": (
        33063408,
        "4f87b62c132a7f7ed4bc02807791b58d53725b56bf76a48d11308f6ef8f59cbc",
        5360,
        "c304f2be001462849541460db6af965e692df29324e0f41dcae8dad3128f7e46",
    ),
    "public_surface_v19": (
        2860642,
        "b7d6dcfac59a55e109885e5baf7caa1e0dd2d7f521c3b06e063b5cc7358ef526",
        50652,
        "11a8222f00a0a35897e4036d3895e35d0602fe2316f8b6a2c96f9a6a639c0cd7",
    ),
    "subinterpreter_v2": (
        4120,
        "b7b9532ae76b6a43f95b1803cb175b9872eef89298c68a25c915c6ce8e07c514",
        4288,
        "27ff1c197d53e348c08f1c3ecadddc7e043c20c88552d6a07aa6e16c4cd9bc79",
    ),
    "pep688_v4": (
        228940,
        "229432efe3b73d896777e1b6a362f79cc005c0298b18976e62456a4b51a5aaa9",
        4556,
        "091a1318e6b98bc4ce9951e320fe09479ebacc295f4b23fdfe3c2cfffac99fa7",
    ),
    "threaded_pattern_v1": (
        1062510,
        "f774398b2fdb75cf78f216fea656c8cb27d7828281c42bff6297a15ea902adb1",
        2948,
        "331be93e5b5a3c9d5e0acd1e363c03bcbeae913152584ec1a5c84ba4a036c442",
    ),
}

CONTRACT_KEYS = frozenset({
    "actual_v13_source_build", "actual_worker_evidence_transport",
    "authenticated_public_surface_evidence_transport",
    "authenticated_zig_observer_source_proxy", "bounded_original_campaign",
    "corrected_original_matching", "corrected_supplemental_matching",
    "current_qualified_candidates", "expanded_sealed_holdout_proposal", "family",
    "first_party_namespace", "first_party_zig", "future_actual_run", "goal",
    "historical_holdout_case_count", "holdout", "holdout_case_count",
    "holdout_case_status", "immutable_v2_runtime_guard", "immutable_v5_observer",
    "injective_worker_unicode_transport", "label", "memory",
    "minimum_qualified_candidates", "original_oracle", "performance",
    "pinned_cpython", "preserved_history", "protocol", "published_graph",
    "pushed_v10_predecessor", "pushed_v5_predecessor", "pushed_v6_predecessor",
    "pushed_v7_predecessor", "pushed_v8_predecessor", "pushed_v9_predecessor",
    "qualified_candidate_count", "runtime_non_delegation", "schema", "source",
    "source_only_effects", "status", "undefined_behavior", "version",
    "winner_selected",
})

RECEIPT_KEYS = frozenset({
    "actual_candidate_workers", "all_original_suites_attempted",
    "all_three_original_targets_restored", "archive", "benchmark_files_read",
    "candidate_qualified", "candidate_status", "case_execution_denominator",
    "completed_suite_count", "contract_sha256", "failed_suites", "family",
    "hidden_cases_read", "holdout", "infrastructure_failure_count",
    "infrastructure_failure_suites", "label", "maximum_serial_worker_timeout_seconds",
    "memory", "observed_semantic_mismatch_lower_bound", "original_campaign_passed",
    "original_suite_diagnostics", "per_suite_timeout_seconds", "performance",
    "protocol_sha256", "publication_pass_means", "schema", "semantic_mismatch_count",
    "source_sha256", "status", "suite_count", "supplemental_candidate_matching",
    "timed_out_suites", "timeout_classification", "timeout_count",
    "timing_trials_run", "uncompressed_bytes", "uncompressed_sha256",
    "undefined_behavior", "unique_candidate_worker_count",
    "verified_passing_case_count", "winner_selected",
})

ROW_KEYS = frozenset({
    "activation_stage", "actual_worker_schema", "candidate_imported",
    "case_execution_denominator", "complete_actual_suite_failure_details",
    "error_class", "error_message", "error_message_detail", "error_traceback",
    "error_type", "guard_installed_before_candidate_import",
    "infrastructure_failure", "observed_semantic_mismatch_count",
    "observer_source_proxy", "pid", "returncode", "status", "stderr",
    "stderr_literal_excerpt", "stdout", "suite", "timed_out",
    "timeout_classification", "timeout_seconds", "traceback_frames",
    "traceback_frames_truncated",
})


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    relative, expected, size, inode = item
    if not (type(size) is int and 0 < size <= OWNER_LIMIT):
        raise ValueError("reject unbounded complete V92 evidence: " + label)
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
            raise ValueError("reject substituted complete V92 owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(handle, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject truncated complete V92 owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(handle, 1):
            raise ValueError("reject extended complete V92 owner: " + label)
        raw = b"".join(chunks)
        after = os.fstat(handle)
        if hashlib.sha256(raw).hexdigest() != expected or (
            before.st_dev, before.st_ino, before.st_size, before.st_nlink,
            before.st_mtime_ns, before.st_ctime_ns,
        ) != (
            after.st_dev, after.st_ino, after.st_size, after.st_nlink,
            after.st_mtime_ns, after.st_ctime_ns,
        ):
            raise ValueError("reject changed complete V92 owner: " + label)
        return raw
    finally:
        os.close(handle)


FORBIDDEN_EVENTS = frozenset({
    "subprocess.Popen", "os.system", "os.posix_spawn", "os.posix_spawnp",
    "os.fork", "os.forkpty", "ctypes.dlopen", "ctypes.dlsym",
    "socket.__new__", "socket.connect", "socket.bind", "socket.sendto",
})
FORBIDDEN_IMPORTS = frozenset({
    "regex", "re", "_sre", "ctypes", "subprocess", "multiprocessing",
    "socket", "time", "gzip", "bz2", "lzma", "tarfile", "zipfile",
    "candidates", "rebar",
})


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    if event in FORBIDDEN_EVENTS:
        raise ValueError("V92 source-only operation rejected " + event)
    if event == "import":
        name = arguments[0] if arguments else None
        if isinstance(name, str) and name.partition(".")[0] in FORBIDDEN_IMPORTS:
            raise ValueError("V92 source-only import rejected " + name)
        return
    if event != "open":
        return
    if len(arguments) < 3:
        raise ValueError("V92 rejected an unauthenticated file open")
    path, mode, flags = arguments[:3]
    if not isinstance(path, str) or not isinstance(flags, int):
        raise ValueError("V92 rejected an unverified descriptor or file owner")
    if mode not in (None, "r", "rb"):
        raise ValueError("V92 source-only operation cannot open writable files")
    if flags & os.O_ACCMODE != os.O_RDONLY or flags & (
        os.O_CREAT | os.O_TRUNC | os.O_APPEND
    ):
        raise ValueError("V92 source-only operation cannot create or change files")
    normalized = os.path.normpath(path)
    if os.path.isabs(normalized):
        if normalized != str(ROOT) and not normalized.startswith(str(ROOT) + "/"):
            raise ValueError("V92 rejected private roots or unopened holdout cases")
    elif "/" in normalized or normalized in (".", ".."):
        raise ValueError("V92 rejected an escaped relative evidence owner")
    if (
        normalized.endswith((".gz", ".bz2", ".xz", ".zip", ".so", ".dylib"))
        or "candidate-current-overview-v92." in normalized
        or "/.git/" in normalized
        or "/__pycache__/" in normalized
        or "/performance/" in normalized
        or "/experiments/" in normalized
    ):
        raise ValueError(
            "V92 rejected outputs, archives, or benchmarks: "
            + normalized
        )


def load_previous() -> tuple[
    types.ModuleType, types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType, types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType, types.ModuleType, tuple, types.ModuleType,
]:
    raw = read_fixed(V91["source"], "whole actually published V91 renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v91")
    previous.__file__ = str(ROOT / V91["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    v90, v89, v88, v87, v86, v85, v84, v83, v82, chain, base = (
        previous.load_previous()
    )
    base.runtime()
    base.need(
        os.path.realpath(sys.executable) == PYTHON
        and sys.implementation.name == "cpython"
        and sys.implementation.cache_tag == "cpython-314"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode is True
        and previous.SCHEMA == "rebar-candidate-current-overview-v91"
        and previous.SELF == V91["source"][0]
        and tuple(previous.SUITES) == SUITES
        and sum(count for _, count in SUITES) == CASE_COUNT
        and len(chain) == 15,
        "require pinned isolated CPython, immutable V91 history and exact P0",
    )
    return previous, v90, v89, v88, v87, v86, v85, v84, v83, v82, chain, base


def previous_options(previous: types.ModuleType) -> argparse.Namespace:
    pins: dict[str, object] = {
        "source_sha256": V91["source"][1],
        "source_bytes": V91["source"][2],
        "rust_receipt_sha256": previous.RUST_RECEIPT[1],
    }
    for role, item in previous.V90.items():
        pins["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.RUST_SOURCE.items():
        pins["rust_" + role + "_sha256"] = item[1]
    return argparse.Namespace(**pins)


def authenticate_previous(
    previous: types.ModuleType,
    v90: types.ModuleType,
    v89: types.ModuleType,
    v88: types.ModuleType,
    v87: types.ModuleType,
    v86: types.ModuleType,
    v85: types.ModuleType,
    v84: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
) -> dict:
    snapshot, assets = previous.build(
        v90, v89, v88, v87, v86, v85, v84, v83, v82, chain, base,
        previous_options(previous),
    )
    for role in ("inputs", "summary", "svg"):
        item = V91[role]
        base.need(
            assets[item[0]] == read_fixed(item, "whole pushed V91 " + role),
            "reconstruct every complete byte of the published V91 " + role,
        )
    old = base.document(assets[V91["summary"][0]], "whole immutable V91 summary")
    historical = old["previous_v88_snapshot"]
    base.need(
        old["version"] == 91
        and old["snapshot"] == snapshot
        and old["authenticated_evidence_owner_lower_bound"] == 320
        and old["authenticated_history_reference_lower_bound"] == 325
        and [row.get("family") for row in old["families"]]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"]
        and old["families"][0]["correctness"] == "BASELINE PASS"
        and old["lossless_v89_all_eleven_previous_pool_identity_status"] == "PASS"
        and old["lossless_v90_all_twelve_previous_pool_identity_status"] == "PASS"
        and old["lossless_v89_complete_original_suite_reference_count"] == 39
        and old["lossless_v90_zig_v10_complete_plaintext_receipt_count"] == 1
        and old["lossless_v90_zig_v10_complete_source_owner_count"] == 3
        and old["lossless_v90_zig_v10_complete_original_suite_count"] == 13
        and old["lossless_v91_rust_v20_complete_plaintext_receipt_count"] == 1
        and old["lossless_v91_rust_v20_complete_source_owner_count"] == 3
        and old["lossless_v91_rust_v20_complete_original_suite_count"] == 13
        and old["original_case_execution_denominator"] == CASE_COUNT
        and old["original_suite_count"] == 13
        and old["named_private_waiver_count"] == 13
        and old["separate_additional_reference_case_count"] == SUPPLEMENTAL_CASE_COUNT
        and old["additional_cases_included_in_original_denominator"] is False
        and old["c_v7_original_campaign_clean_suite_count"] == 2
        and old["c_v7_original_campaign_completed_suite_count"] == 5
        and old["c_v7_original_campaign_verified_passing_case_count"] == 13094
        and old["c_v7_original_campaign_observed_mismatch_lower_bound"] == 236
        and old["c_v7_original_campaign_candidate_execution_failure_count"] == 7
        and old["c_v7_original_campaign_infrastructure_failure_count"] == 1
        and old["rust_v19_original_campaign_clean_suite_count"] == 6
        and old["rust_v19_original_campaign_completed_suite_count"] == 8
        and old["rust_v19_original_campaign_verified_passing_case_count"] == 12942
        and old["rust_v19_original_campaign_observed_mismatch_lower_bound"] == 1296
        and old["rust_v19_original_campaign_infrastructure_failure_count"] == 5
        and old["rust_v19_original_campaign_semantic_mismatch_count"] == "NOT MEASURED"
        and old["rust_v20_original_campaign_actual_worker_count"] == 13
        and old["rust_v20_original_campaign_distinct_worker_count"] == 13
        and old["rust_v20_original_campaign_clean_suite_count"] == 10
        and old["rust_v20_original_campaign_completed_suite_count"] == 12
        and old["rust_v20_original_campaign_mismatch_suite_count"] == 2
        and old["rust_v20_original_campaign_verified_passing_case_count"] == 15749
        and old["rust_v20_original_campaign_observed_mismatch_lower_bound"] == 1296
        and old["rust_v20_original_campaign_infrastructure_failure_count"] == 1
        and old["rust_v20_original_campaign_infrastructure_failure_suite"]
        == "subinterpreter_v2"
        and old["rust_v20_original_campaign_semantic_mismatch_count"] == "NOT MEASURED"
        and old["rust_v20_original_campaign_all_four_original_targets_restored"]
        is True
        and old["zig_v9_original_campaign_verified_passing_case_count"] == 927
        and old["zig_v9_original_campaign_infrastructure_failure_count"] == 10
        and old["zig_v10_original_campaign_verified_passing_case_count"] == 3583
        and old["zig_v10_original_campaign_clean_suite_count"] == 6
        and old["zig_v10_original_campaign_completed_suite_count"] == 9
        and old["zig_v10_original_campaign_mismatch_suite_count"] == 3
        and old["zig_v10_original_campaign_observed_mismatch_lower_bound"] == 1540
        and old["zig_v10_original_campaign_infrastructure_failure_count"] == 4
        and old["zig_v10_original_campaign_semantic_mismatch_count"] == "NOT MEASURED"
        and historical["actual_rust_semantic_mismatch_count"] == 1440
        and historical["actual_rust_verified_passing_case_count"] == 14853
        and historical["actual_c_semantic_mismatch_count"] == 1230
        and historical["actual_c_verified_passing_case_count"] == 7325
        and historical["actual_zig_semantic_mismatch_count"] == 1764
        and old["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and old["preserved_previous_holdout_proposal_case_count"]
        == HISTORICAL_HOLDOUT_PROPOSAL_COUNT
        and old["expanded_holdout_final_protocol_status"] == "NOT FROZEN"
        and old["expanded_holdout_case_status"] == "NOT GENERATED; NOT OPENED"
        and old["qualified_candidate_count"] == 0
        and old["runtime_no_delegation"] == "NOT ESTABLISHED"
        and old["performance"] == "NOT MEASURED"
        and old["memory"] == "NOT MEASURED"
        and old["undefined_behavior"] == "NOT MEASURED"
        and old["final_holdout_opened"] is False
        and old["winner_selected"] is False,
        "preserve every exact C, Rust, Zig and historical outcome and unopened P0",
    )
    for key, size, digest, count in OLD_POOLS:
        value = old.get(key)
        whole = base.canonical(value)
        base.need(
            type(value) is dict
            and len(whole) == size
            and base.digest(whole) == digest
            and type(value.get("entries")) is dict
            and len(value["entries"]) == count,
            "preserve complete exact historical V91 proof pool: " + key,
        )
    return old


def validate_source_contract(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict and set(value) == CONTRACT_KEYS,
        "authenticate all 45 fields of the complete Zig V12 source contract",
    )
    assert isinstance(value, dict)
    base.need(
        value["schema"]
        == "rebar-owned-repaired-zig-original-campaign-v12-guard-clean-source-freeze"
        and value["version"] == 12
        and value["family"] == "zig"
        and value["label"] == "phase2-v13-zig-guard-clean-v1-original-p0-v12"
        and value["status"] == "SOURCE FROZEN; CORRECTED ZIG MATCHING NOT RUN"
        and value["corrected_original_matching"] == "NOT RUN"
        and value["corrected_supplemental_matching"] == "NOT RUN"
        and value["current_qualified_candidates"] == 0
        and value["qualified_candidate_count"] == 0
        and value["minimum_qualified_candidates"] == 3
        and value["runtime_non_delegation"] == "NOT ESTABLISHED"
        and value["historical_holdout_case_count"] == HISTORICAL_HOLDOUT_PROPOSAL_COUNT
        and value["holdout_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and value["holdout_case_status"]
        == "PROPOSED; NOT FROZEN; NOT GENERATED; NOT OPENED"
        and value["holdout"] == "NOT OPENED"
        and value["performance"] == "NOT MEASURED"
        and value["memory"] == "NOT MEASURED"
        and value["undefined_behavior"] == "NOT MEASURED"
        and value["winner_selected"] is False,
        "reject invented Zig V12 qualification, delegation, timing or holdout use",
    )
    for role in ("source", "protocol"):
        item = ZIG_SOURCE[role]
        expected = base.synthetic_owner(item[:3], item[3])
        expected.pop("uid", None)
        base.need(
            base.canonical(value[role]) == base.canonical(expected),
            "authenticate exact complete first-party Zig V12 " + role,
        )
    oracle = value["original_oracle"]
    base.need(
        type(oracle) is dict
        and oracle["case_execution_denominator"] == CASE_COUNT
        and oracle["suite_count"] == len(SUITES)
        and oracle["named_private_waiver_count"] == len(SUITES)
        and oracle["supplemental_case_count"] == SUPPLEMENTAL_CASE_COUNT
        and oracle["supplemental_cases_added_to_original_denominator"] is False
        and oracle["supplemental_candidate_matching"] == "NOT RUN"
        and type(oracle["suites"]) is list
        and len(oracle["suites"]) == len(SUITES),
        "retain every frozen original obligation and separate supplemental checks",
    )
    for row, (suite, count) in zip(oracle["suites"], SUITES, strict=True):
        base.need(
            type(row) is dict
            and row.get("id") == suite
            and row.get("case_execution_count") == count,
            "reject changed complete Zig V12 original suite: " + suite,
        )
    guard = value["immutable_v2_runtime_guard"]
    base.need(
        type(guard) is dict
        and guard["installed_before_candidate_import"] is True
        and guard["ctypes_dlopen_permitted"] is False
        and guard["external_regex_package_permitted"] is False
        and guard["fallback_permitted"] is False
        and guard["other_candidate_permitted"] is False
        and guard["stdlib_regex_engine_permitted"] is False,
        "reject external packages, CPython regex, fallback or unguarded Zig imports",
    )
    first_party = value["first_party_zig"]
    base.need(
        type(first_party) is dict
        and first_party["complete_matching_ast_unchanged"] is True
        and first_party["exact_removed_ctypes_import_count"] == 1
        and first_party["v13_build_attests_guard_clean_adapter"] is False,
        "distinguish the actual first-party Zig source from any external wrapper",
    )
    transport = value["actual_worker_evidence_transport"]
    base.need(
        type(transport) is dict
        and transport["actual_worker_stdout_maximum_bytes"] == 67108864
        and transport["immutable_v5_global_json_maximum_bytes"] == OWNER_LIMIT
        and transport["canonical_wire_verified_before_transport_decode"] is True
        and transport["worker_stderr_preserved"] is True,
        "retain genuine complete bounded worker output and original producer",
    )
    proposal = value["expanded_sealed_holdout_proposal"]
    base.need(
        type(proposal) is dict
        and proposal["case_count"] == HOLDOUT_PROPOSAL_COUNT
        and proposal["case_status"] == "NOT GENERATED; NOT OPENED"
        and proposal["final_protocol_status"] == "NOT FROZEN"
        and proposal["holdout_files_opened"] == 0
        and proposal["holdout_generator_executed"] is False
        and proposal["timing_trials_run"] == 0
        and proposal["qualified_independent_family_count"] == 0
        and proposal["historical_proposal"]["case_count"]
        == HISTORICAL_HOLDOUT_PROPOSAL_COUNT,
        "keep both holdout proposals sealed and without invented performance",
    )
    effects = value["source_only_effects"]
    base.need(
        type(effects) is dict and len(effects) == 20
        and all(type(number) is int and number == 0 for number in effects.values()),
        "reject source-only matching, compilation, imports, clocks or file changes",
    )
    future = value["future_actual_run"]
    base.need(
        type(future) is dict
        and future["distinct_original_suite_workers"] == 13
        and future["canonical_role_count"] == 3
        and future["all_original_targets_restored_before_publication"] is True
        and future["publication_pass_means"] == "DURABLE PUBLICATION ONLY"
        and future["per_suite_timeout_seconds"] == 120
        and future["maximum_serial_worker_timeout_seconds"] == 1560,
        "preserve separate actual Zig execution, restoration and publication meaning",
    )
    pinned = value["pinned_cpython"]
    base.need(
        type(pinned) is dict
        and pinned["path"] == PYTHON
        and pinned["version"] == "3.14.6",
        "preserve the unchanged pinned CPython correctness baseline",
    )
    return value


def validate_zig_receipt(base: types.ModuleType, value: object) -> dict:
    base.need(
        type(value) is dict and set(value) == RECEIPT_KEYS,
        "authenticate all 42 fields of the actual complete Zig V12 public receipt",
    )
    assert isinstance(value, dict)
    base.need(
        value["schema"]
        == "rebar-owned-repaired-zig-original-campaign-v12-durable-publication-receipt"
        and value["family"] == "zig"
        and value["label"] == "phase2-v13-zig-guard-clean-v1-original-p0-v12"
        and value["status"] == "PASS"
        and value["publication_pass_means"] == "DURABLE PUBLICATION ONLY"
        and value["original_campaign_passed"] is False
        and value["candidate_status"] == "FAIL"
        and value["candidate_qualified"] is False
        and value["source_sha256"] == ZIG_SOURCE["source"][1]
        and value["protocol_sha256"] == ZIG_SOURCE["protocol"][1]
        and value["contract_sha256"] == ZIG_SOURCE["contract"][1]
        and value["suite_count"] == len(SUITES)
        and value["case_execution_denominator"] == CASE_COUNT
        and value["actual_candidate_workers"] == 13
        and value["unique_candidate_worker_count"] == 13
        and value["all_original_suites_attempted"] is True
        and value["completed_suite_count"] == 12
        and value["verified_passing_case_count"] == 4607
        and value["observed_semantic_mismatch_lower_bound"] == 1700
        and value["semantic_mismatch_count"] == "NOT MEASURED"
        and value["infrastructure_failure_count"] == 1
        and value["infrastructure_failure_suites"] == ["subinterpreter_v2"]
        and value["all_three_original_targets_restored"] is True
        and value["supplemental_candidate_matching"] == "NOT RUN"
        and value["timeout_count"] == 0
        and value["timed_out_suites"] == []
        and value["timeout_classification"] == "INFRASTRUCTURE FAILURE"
        and value["per_suite_timeout_seconds"] == 120
        and value["maximum_serial_worker_timeout_seconds"] == 1560
        and value["hidden_cases_read"] == 0
        and value["benchmark_files_read"] == 0
        and value["timing_trials_run"] == 0
        and value["holdout"] == "NOT OPENED"
        and value["performance"] == "NOT MEASURED"
        and value["memory"] == "NOT MEASURED"
        and value["undefined_behavior"] == "NOT MEASURED"
        and value["winner_selected"] is False,
        "reject publication-as-success, fake qualification, timings or hidden cases",
    )
    archive = value["archive"]
    base.need(
        type(archive) is dict
        and archive["name"]
        == "repaired-zig-original-campaign-v12-phase2-v13-zig-guard-clean-v1-"
        "original-p0-v12-failures.json.gz"
        and archive["sha256"]
        == "ab8aa0f69cce19d62ffb75f8c56ca57fc22d2441cb3b14b8718f5cc7280de5e4"
        and archive["bytes"] == 5618052
        and archive["device"] == 2064
        and archive["inode"] == 524970
        and archive["uid"] == os.geteuid()
        and archive["mode"] == 0o600
        and archive["nlink"] == 1
        and value["uncompressed_bytes"] == 192190446
        and value["uncompressed_sha256"]
        == "0e071a02da81620c063ad86e7d556d8ed4e91f7cc5fb8b50b9d99c913b9d383e",
        "retain compressed archive metadata exclusively from the public receipt",
    )
    rows = value["original_suite_diagnostics"]
    base.need(
        type(rows) is list and len(rows) == len(SUITES),
        "preserve all thirteen actual original Zig workers and complete diagnostics",
    )
    clean: list[dict] = []
    mismatch: list[dict] = []
    infrastructure: list[dict] = []
    pids: set[int] = set()
    for row, (suite, denominator) in zip(rows, SUITES, strict=True):
        base.need(
            type(row) is dict and set(row) == ROW_KEYS
            and row["suite"] == suite
            and row["case_execution_denominator"] == denominator
            and row["candidate_imported"] is True
            and row["guard_installed_before_candidate_import"] is True
            and type(row["pid"]) is int and row["pid"] > 0
            and row["pid"] not in pids
            and row["returncode"] == 0
            and row["timed_out"] is False
            and row["timeout_seconds"] == 120
            and row["timeout_classification"] == "NOT TIMED OUT",
            "reject omitted, unguarded, repeated or invented Zig worker: " + suite,
        )
        pids.add(row["pid"])
        expected_streams = STREAMS[suite]
        for stream_index, stream_name in enumerate(("stdout", "stderr")):
            stream = row[stream_name]
            base.need(
                type(stream) is dict
                and type(stream.get("bytes")) is int
                and stream["bytes"] == expected_streams[stream_index * 2]
                and stream.get("sha256") == expected_streams[stream_index * 2 + 1]
                and base.checked(stream.get("sha256"), "complete Zig " + stream_name)
                == stream["sha256"]
                and stream["complete"] is True
                and stream["complete_payload_preserved_in_actual_archive"] is True,
                "preserve real complete worker stream metadata: " + suite,
            )
        if row["infrastructure_failure"] is True:
            base.need(
                suite == "subinterpreter_v2"
                and row["status"] == "FAIL"
                and row["activation_stage"]
                == "OBSERVE_COMPLETE_ORIGINAL_SUBINTERPRETER_SUITE"
                and row["actual_worker_schema"]
                == "rebar-owned-repaired-zig-original-campaign-v12-actual-worker-failure"
                and row["observed_semantic_mismatch_count"] == "NOT MEASURED"
                and row["error_type"] == "ActualSuiteFailure"
                and row["error_class"]
                == "_rebar_guard_clean_zig_v5_producer.ActualSuiteFailure"
                and type(row["complete_actual_suite_failure_details"]) is dict,
                "retain the real guarded, incomplete Zig subinterpreter failure",
            )
            failure = row["complete_actual_suite_failure_details"]
            base.need(
                failure["schema"]
                == "rebar-owned-six-family-original-p0-producer-v5-genuine-nested-failure"
                and failure["candidate_family"] == "zig",
                "retain the authentic first-party Zig nested failure",
            )
            base.need(
                failure["status"] == "FAIL"
                and failure["suite"] == "subinterpreter_v2"
                and failure["error_type"] == "ActualSuiteFailure"
                and failure["actual_child_guards_installed"] == 1
                and failure["candidate_qualified"] is False
                and failure["hidden_cases_read"] == 0
                and failure["benchmark_files_read"] == 0
                and failure["clock_samples"] == 0
                and failure["timing_trials_run"] == 0
                and failure["holdout"] == "NOT OPENED"
                and failure["performance"] == "NOT MEASURED"
                and failure["winner_selected"] is False,
                "reject relabelling the genuine Zig lifecycle failure as a pass",
            )
            infrastructure.append(row)
        else:
            base.need(
                row["infrastructure_failure"] is False
                and row["activation_stage"] == "COMPLETE_ORIGINAL_OBSERVATION"
                and row["actual_worker_schema"]
                == "rebar-owned-repaired-zig-original-campaign-v12-actual-suite-worker"
                and row["complete_actual_suite_failure_details"] is None,
                "require a real, complete, source-authenticated Zig observation",
            )
            if row["status"] == "PASS":
                base.need(
                    row["observed_semantic_mismatch_count"] == 0
                    and suite not in MISMATCHES,
                    "reject an invented complete clean Zig suite: " + suite,
                )
                clean.append(row)
            else:
                base.need(
                    row["status"] == "FAIL"
                    and suite in MISMATCHES
                    and row["observed_semantic_mismatch_count"] == MISMATCHES[suite],
                    "reject concealed actual Zig semantic mismatches: " + suite,
                )
                mismatch.append(row)
    base.need(
        len(pids) == 13
        and len(clean) == 7
        and len(mismatch) == 5
        and len(infrastructure) == 1
        and len(clean) + len(mismatch) == value["completed_suite_count"]
        and sum(row["case_execution_denominator"] for row in clean) == 4607
        and sum(row["observed_semantic_mismatch_count"] for row in mismatch) == 1700
        and {
            row["suite"]: row["observed_semantic_mismatch_count"]
            for row in mismatch
        } == MISMATCHES
        and value["failed_suites"]
        == [*MISMATCHES, "subinterpreter_v2"],
        "derive seven clean, five genuinely different and one incomplete Zig groups",
    )
    return {
        "family": "zig",
        "display_name": "Zig",
        "actual_candidate_worker_count": 13,
        "unique_candidate_worker_count": 13,
        "attempted_suite_count": 13,
        "individually_proven_guarded_candidate_import_count": 13,
        "candidate_import_status_unknown_count": 0,
        "infrastructure_failure_with_individually_proven_guarded_import_count": 1,
        "clean_suite_count": 7,
        "completed_suite_count": 12,
        "mismatch_suite_count": 5,
        "infrastructure_failure_count": 1,
        "infrastructure_failure_suite": "subinterpreter_v2",
        "verified_passing_case_count": 4607,
        "observed_semantic_mismatch_lower_bound": 1700,
        "aggregate_semantic_mismatch_count": "NOT MEASURED",
        "all_original_suite_rows_validated": True,
        "all_original_observation_vectors_complete": False,
        "all_three_original_targets_restored": True,
        "case_execution_denominator": CASE_COUNT,
        "candidate_status": "FAIL",
        "candidate_qualified": False,
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
        role: read_fixed(item, "whole first-party Zig V12 " + role)
        for role, item in ZIG_SOURCE.items()
    }
    contract = base.document(raws["contract"], "whole actual Zig V12 source contract")
    base.need(
        base.canonical(contract) == raws["contract"],
        "reject noncanonical or partial Zig V12 source-freeze contract",
    )
    validate_source_contract(base, contract)
    raw = read_fixed(ZIG_RECEIPT, "whole actually pushed Zig V12 public receipt")
    receipt = base.document(raw, "whole actual pushed Zig V12 public receipt")
    base.need(
        base.canonical(receipt) == raw,
        "reject noncanonical or partial actual Zig V12 plaintext public receipt",
    )
    return contract, receipt, validate_zig_receipt(base, receipt)


def compact_suite_proof(base: types.ModuleType, row: dict) -> dict:
    raw = base.canonical(row)
    return {
        "suite": row["suite"],
        "case_execution_denominator": row["case_execution_denominator"],
        "complete_public_suite_row_sha256": base.digest(raw),
        "complete_public_suite_row_canonical_bytes": len(raw),
        "status": row["status"],
        "observed_semantic_mismatch_count": row[
            "observed_semantic_mismatch_count"
        ],
        "infrastructure_failure": row["infrastructure_failure"],
        "candidate_imported": row["candidate_imported"],
        "guard_installed_before_candidate_import": row[
            "guard_installed_before_candidate_import"
        ],
        "pid": row["pid"],
        "returncode": row["returncode"],
        "timed_out": row["timed_out"],
        "stdout_sha256": row["stdout"]["sha256"],
        "stdout_bytes": row["stdout"]["bytes"],
        "stderr_sha256": row["stderr"]["sha256"],
        "stderr_bytes": row["stderr"]["bytes"],
    }


def make_evidence_pool(
    base: types.ModuleType, contract: dict, receipt: dict, facts: dict,
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
        "validated_campaign_outcome": copy.deepcopy(facts),
        "compressed_archive_opened_by_graph": False,
        "private_build_root_opened_by_graph": False,
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
        and set(pool) == {
            "schema", "version", "hash_algorithm",
            "complete_public_receipt_count", "complete_first_party_source_owner_count",
            "entries",
        }
        and pool["schema"] == POOL_SCHEMA
        and pool["version"] == 1
        and pool["hash_algorithm"] == "sha256"
        and pool["complete_public_receipt_count"] == 1
        and pool["complete_first_party_source_owner_count"] == 3
        and type(pool["entries"]) is dict
        and set(pool["entries"]) == {ZIG_RECEIPT[1]},
        "require one complete actual Zig V12 owner-addressed campaign outcome",
    )
    assert isinstance(pool, dict)
    entry = pool["entries"][ZIG_RECEIPT[1]]
    rows = [
        compact_suite_proof(base, row)
        for row in receipt["original_suite_diagnostics"]
    ]
    base.need(
        type(entry) is dict
        and entry["schema"] == ENTRY_SCHEMA
        and entry["family"] == "zig"
        and base.canonical(entry["complete_plaintext_receipt_owner"])
        == base.canonical(base.synthetic_owner(ZIG_RECEIPT[:3], ZIG_RECEIPT[3]))
        and entry["complete_plaintext_receipt_sha256"] == ZIG_RECEIPT[1]
        and entry["complete_plaintext_receipt_bytes"] == ZIG_RECEIPT[2]
        and entry["complete_plaintext_receipt_field_count"] == len(RECEIPT_KEYS)
        and entry["complete_plaintext_receipt_embedded"] is True
        and base.canonical(entry["complete_plaintext_receipt"])
        == base.canonical(receipt)
        and entry["complete_first_party_source_owner_count"] == 3
        and entry["complete_source_contract_field_count"] == len(CONTRACT_KEYS)
        and entry["complete_source_contract_embedded"] is True
        and base.canonical(entry["complete_source_contract"])
        == base.canonical(contract)
        and entry["complete_original_suite_count"] == 13
        and base.canonical(entry["complete_original_suite_rows"])
        == base.canonical(rows)
        and base.canonical(entry["validated_campaign_outcome"])
        == base.canonical(facts)
        and entry["compressed_archive_opened_by_graph"] is False
        and entry["private_build_root_opened_by_graph"] is False
        and entry["complete_failure_diagnostics_available_without_archive"] is True,
        "reject omitted, fabricated or partial genuine Zig V12 campaign evidence",
    )
    owners = entry["complete_first_party_source_owners"]
    base.need(
        type(owners) is dict and set(owners) == set(ZIG_SOURCE),
        "retain exactly three individually authenticated Zig V12 source owners",
    )
    for role, item in ZIG_SOURCE.items():
        base.need(
            base.canonical(owners[role])
            == base.canonical(base.synthetic_owner(item[:3], item[3])),
            "retain the exact whole authenticated Zig V12 source owner: " + role,
        )


def make_reference(base: types.ModuleType, pool: dict) -> dict:
    entry = pool["entries"][ZIG_RECEIPT[1]]
    raw = base.canonical(entry)
    return {
        "schema": REFERENCE_SCHEMA,
        "family": "zig",
        "complete_plaintext_receipt_sha256": ZIG_RECEIPT[1],
        "complete_plaintext_receipt_bytes": ZIG_RECEIPT[2],
        "complete_first_party_source_owner_count": 3,
        "complete_reference_sha256": base.digest(raw),
        "complete_reference_canonical_bytes": len(raw),
    }


def resolve_reference(base: types.ModuleType, pool: dict, value: object) -> dict:
    base.need(
        type(value) is dict
        and set(value) == {
            "schema", "family", "complete_plaintext_receipt_sha256",
            "complete_plaintext_receipt_bytes", "complete_first_party_source_owner_count",
            "complete_reference_sha256", "complete_reference_canonical_bytes",
        }
        and value["schema"] == REFERENCE_SCHEMA
        and value["family"] == "zig"
        and value["complete_plaintext_receipt_sha256"] == ZIG_RECEIPT[1]
        and value["complete_plaintext_receipt_bytes"] == ZIG_RECEIPT[2]
        and value["complete_first_party_source_owner_count"] == 3,
        "reject a missing or invented complete actual Zig V12 owner reference",
    )
    assert isinstance(value, dict)
    entry = pool["entries"].get(ZIG_RECEIPT[1])
    base.need(
        type(entry) is dict
        and base.checked(value["complete_reference_sha256"], "whole Zig V12 proof")
        == base.digest(base.canonical(entry))
        and value["complete_reference_canonical_bytes"]
        == len(base.canonical(entry)),
        "reject fabricated complete Zig V12 receipt, source or suite evidence",
    )
    return copy.deepcopy(entry)


def make_changes(reference: dict) -> dict:
    return {
        "actual_current_graph_predecessor_version": 91,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "v92_new_directly_authenticated_owner_count": 4,
        "v92_new_directly_authenticated_zig_source_owner_count": 3,
        "v92_new_directly_authenticated_zig_plaintext_receipt_owner_count": 1,
        "original_case_execution_denominator": CASE_COUNT,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "zig_v12_original_campaign_actual_worker_count": 13,
        "zig_v12_original_campaign_distinct_worker_count": 13,
        "zig_v12_original_campaign_attempted_suite_count": 13,
        "zig_v12_original_campaign_individually_proven_guarded_candidate_import_count": 13,
        "zig_v12_original_campaign_candidate_import_status_unknown_count": 0,
        "zig_v12_original_campaign_clean_suite_count": 7,
        "zig_v12_original_campaign_completed_suite_count": 12,
        "zig_v12_original_campaign_mismatch_suite_count": 5,
        "zig_v12_original_campaign_verified_passing_case_count": 4607,
        "zig_v12_original_campaign_observed_mismatch_lower_bound": 1700,
        "zig_v12_original_campaign_infrastructure_failure_count": 1,
        "zig_v12_original_campaign_infrastructure_failure_suite":
        "subinterpreter_v2",
        "zig_v12_original_campaign_infrastructure_failure_with_proven_guarded_import_count":
        1,
        "zig_v12_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "zig_v12_original_campaign_all_three_original_targets_restored": True,
        "zig_v12_original_campaign_candidate_status": "FAIL",
        "zig_v12_original_campaign_candidate_qualified": False,
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
        ("Python re", CASE_COUNT, "13 of 13 groups", "BASELINE", "#34d399"),
        (
            "Rust", 15749,
            "10 clean · 2 differ · 1 incomplete",
            "NOT COMPATIBLE", "#fbbf24",
        ),
        (
            "C", 13094,
            "2 clean · 3 differ · 7 errors · 1 incomplete",
            "NOT COMPATIBLE", "#fbbf24",
        ),
        (
            "Zig", 4607,
            "7 clean · 5 differ · 1 incomplete",
            "NOT COMPATIBLE", "#fbbf24",
        ),
        (
            "C++", None,
            "Earlier differences; complete current result not measured",
            "NOT COMPATIBLE", "#fb7185",
        ),
        (
            "Go", None,
            "Earlier differences; complete current result not measured",
            "NOT COMPATIBLE", "#fb7185",
        ),
        (
            "Fortran", None,
            "Two builds disagreed; compatibility not measured",
            "BUILD FAILED", "#fb7185",
        ),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="970" viewBox="0 0 1440 970" role="img" aria-labelledby="title description">',
        '<title id="title">Progress toward a faster, fully compatible Python re</title>',
        '<desc id="description">Six independent first-party regular-expression engines are compared with unchanged Python 3.14.6 on the same original 31,237 checks in thirteen groups. The separate 8,244 differential checks are not included. Rust verified 15,749 original checks across ten clean groups, with two differing groups containing at least 1,296 observed differences and one genuine infrastructure failure. C verified 13,094 checks across two clean groups, with three differing groups containing at least 236 observed differences, seven candidate errors, and one infrastructure failure. The latest real Zig campaign started thirteen distinct workers, each with its runtime guard installed before the candidate was imported. Zig verified 4,607 checks across seven clean groups, observed 620, 248, 64, 672, and 96 real differences across five further groups, and recorded one genuinely incomplete guarded subinterpreter test. Twelve Zig groups completed; its full mismatch count remains unknown and all three original targets were restored. Every previous Rust, C and Zig result, and C++, Go and Fortran evidence, remains intact. No candidate is fully compatible. Speed, memory and confidence are not measured. The proposed 14,155,776-case final comparison is not frozen, generated, opened or run.</desc>',
        '<rect width="1440" height="970" rx="22" fill="#0b1220"/>',
        '<text x="44" y="60" fill="#f8fafc" font-size="31" font-family="system-ui,sans-serif" font-weight="730">Building a faster Python re, from scratch</text>',
        '<text x="44" y="97" fill="#cbd5e1" font-size="17" font-family="system-ui,sans-serif">6 independent engines · 0 fully compatible · speed NOT MEASURED</text>',
        '<rect x="44" y="119" width="1352" height="57" rx="11" fill="#172338"/>',
        '<text x="62" y="144" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">What the bars mean: checks actually confirmed against Python, out of 31,237.</text>',
        '<text x="62" y="165" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Unfinished checks are unknown, not passes. The separate 8,244-check comparison is not included.</text>',
        '<text x="45" y="211" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif" font-weight="650">ENGINE</text>',
        '<text x="161" y="211" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif" font-weight="650">CONFIRMED ORIGINAL CHECKS</text>',
        '<text x="724" y="211" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif" font-weight="650">WHAT ACTUALLY HAPPENED</text>',
        '<text x="1386" y="211" text-anchor="end" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif" font-weight="650">RESULT</text>',
        '<line x1="44" y1="226" x2="1396" y2="226" stroke="#334155"/>',
    ]
    for index, (name, passed, details, result, colour) in enumerate(rows):
        y = 267 + 62 * index
        parts.append(
            f'<text x="48" y="{y}" fill="#f8fafc" font-size="16" '
            f'font-family="system-ui,sans-serif" font-weight="650">{name}</text>'
        )
        parts.append(
            f'<rect x="161" y="{y - 16}" width="365" height="20" '
            'rx="6" fill="#1e293b"/>'
        )
        if passed is None:
            label = "NOT MEASURED"
        else:
            width = max(3, round(365 * passed / CASE_COUNT))
            parts.append(
                f'<rect x="161" y="{y - 16}" width="{width}" height="20" '
                f'rx="6" fill="{colour}"/>'
            )
            label = f"{passed:,} / {CASE_COUNT:,}"
        parts.append(
            f'<text x="540" y="{y}" fill="#e2e8f0" font-size="13" '
            f'font-family="system-ui,sans-serif">{label}</text>'
        )
        parts.append(
            f'<text x="724" y="{y}" fill="#cbd5e1" font-size="12" '
            f'font-family="system-ui,sans-serif">{details}</text>'
        )
        parts.append(
            f'<text x="1386" y="{y}" text-anchor="end" fill="{colour}" '
            f'font-size="11" font-family="system-ui,sans-serif" '
            f'font-weight="700">{result}</text>'
        )
    parts.extend((
        '<line x1="44" y1="677" x2="1396" y2="677" stroke="#334155"/>',
        '<text x="48" y="709" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="670">Progress is not the same as full compatibility</text>',
        '<text x="48" y="738" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Zig completed 12 of 13 groups: 7 clean, 5 with real differences, and 1 incomplete lifecycle test.</text>',
        '<text x="48" y="761" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Observed differences: Rust at least 1,296; C at least 236; Zig at least 1,700. Complete totals: NOT MEASURED.</text>',
        '<text x="48" y="784" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Every earlier Rust, C, and Zig result is preserved. Standard Python remains the unchanged baseline.</text>',
        '<text x="48" y="807" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">A successfully published result is not proof that a replacement is compatible or faster.</text>',
        '<rect x="44" y="830" width="1352" height="91" rx="12" fill="#172338"/>',
        '<text x="62" y="858" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="670">Proposed final speed comparison: 14,155,776 cases</text>',
        '<text x="62" y="882" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Not frozen, not generated, not opened, and not run. Speed, memory, confidence, and rankings: NOT MEASURED.</text>',
        '<text x="62" y="905" fill="#cbd5e1" font-size="12" font-family="system-ui,sans-serif">The earlier 4,194,304-case proposal and every prior result remain preserved; no winner has been selected.</text>',
        '<text x="48" y="951" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 92 · complete previous evidence preserved · no external regex wrapper · no fully compatible replacement.</text>',
        '</svg>',
        '',
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
        type(families) is list and len(families) == 7
        and [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "retain the unchanged Python baseline and exactly six first-party families",
    )
    assert isinstance(families, list)
    for row, original in zip(families, old["families"], strict=True):
        family = original["family"]
        base.need(
            type(row) is dict and row["family"] == family,
            "reject a missing, invented or substituted engine family: " + family,
        )
        if family == "python":
            base.need(
                base.canonical(row) == base.canonical(original),
                "preserve every byte of the unchanged standard Python baseline",
            )
            continue
        base.need(
            row["authenticated_evidence_owner_lower_bound"] == EVIDENCE_FLOOR
            and row["authenticated_history_reference_lower_bound"] == HISTORY_FLOOR
            and row["qualified"] is False
            and row["runtime_no_delegation"] == "NOT ESTABLISHED"
            and row["performance"] == "NOT MEASURED",
            "reject fabricated compatibility, independence or speed: " + family,
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
                and base.canonical(row["v92_latest_original_campaign"])
                == base.canonical(facts)
                and base.canonical(row[LATEST_KEY]) == base.canonical(reference)
                and base.canonical(row["v90_latest_original_campaign"])
                == base.canonical(original["v90_latest_original_campaign"])
                and row["v90_latest_original_campaign"]
                ["verified_passing_case_count"] == 3583,
                "preserve both exact historical Zig V10 and actual latest Zig V12",
            )
            restored.pop(LATEST_KEY)
            restored.pop("v92_latest_original_campaign")
        base.need(
            base.canonical(restored) == base.canonical(original),
            "restore the exact complete V91 first-party engine family: " + family,
        )


def build(
    previous: types.ModuleType,
    v90: types.ModuleType,
    v89: types.ModuleType,
    v88: types.ModuleType,
    v87: types.ModuleType,
    v86: types.ModuleType,
    v85: types.ModuleType,
    v84: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> tuple[dict, dict[str, bytes]]:
    base.need(
        options.source_sha256 is not None
        and type(options.source_bytes) is int
        and 0 < options.source_bytes <= OWNER_LIMIT,
        "caller-pin the complete immutable V92 renderer source",
    )
    own, _ = base.read_owner(
        SELF, base.checked(options.source_sha256, "whole immutable V92 renderer"),
        options.source_bytes, private=True,
    )
    for role, item in V91.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin the exact entire pushed V91 " + role,
        )
    for role, item in ZIG_SOURCE.items():
        base.need(
            getattr(options, "zig_" + role + "_sha256") == item[1],
            "caller-pin the complete exact first-party Zig V12 " + role,
        )
    base.need(
        options.zig_receipt_sha256 == ZIG_RECEIPT[1],
        "caller-pin the whole actually pushed Zig V12 public outcome receipt",
    )
    old = authenticate_previous(
        previous, v90, v89, v88, v87, v86, v85, v84, v83, v82, chain, base,
    )
    contract, receipt, facts = load_zig_evidence(base)
    pool = make_evidence_pool(base, contract, receipt, facts)
    reference = make_reference(base, pool)
    changes = make_changes(reference)
    predecessor = {
        role: base.pin(item[0], item[1], item[2]) for role, item in V91.items()
    }
    source_owners = {
        role: base.pin(item[0], item[1], item[2])
        for role, item in ZIG_SOURCE.items()
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update({
        "schema": SCHEMA + "-compact-current-snapshot",
        "version": 92,
        "previous_complete_snapshot_sha256": base.digest(
            base.canonical(old["snapshot"])
        ),
        "previous_complete_snapshot_canonical_bytes": len(
            base.canonical(old["snapshot"])
        ),
        "previous_complete_overview_sha256": V91["summary"][1],
        "previous_complete_overview_bytes": V91["summary"][2],
        **copy.deepcopy(changes),
    })
    headline = copy.deepcopy(old["headline"])
    headline["verified_original_checks_by_candidate"]["zig"] = 4607
    headline["latest_complete_candidate_mismatch_totals"] = "NOT MEASURED"
    headline["fully_compatible_candidate_count"] = 0
    headline["performance"] = "NOT MEASURED"
    headline["memory"] = "NOT MEASURED"
    inputs = {
        "schema": SCHEMA + "-inputs",
        "version": 92,
        "python": "3.14.6",
        "renderer": base.pin(SELF, options.source_sha256, len(own)),
        "previous_overview": copy.deepcopy(predecessor),
        "zig_v12_source_owners": copy.deepcopy(source_owners),
        "zig_v12_plaintext_receipt_owner": base.pin(
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
            row["v92_latest_original_campaign"] = copy.deepcopy(facts)
    validate_families(base, old, families, pool, reference, facts)
    inputs_raw = base.canonical(inputs)
    svg_raw = make_svg()
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 92,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, options.source_sha256, len(own)),
        "inputs": base.pin(INPUT_PATH, base.digest(inputs_raw), len(inputs_raw)),
        "svg": base.pin(SVG_PATH, base.digest(svg_raw), len(svg_raw)),
        "previous_overview": copy.deepcopy(predecessor),
        "previous_v91_snapshot": copy.deepcopy(old["snapshot"]),
        "previous_v91_snapshot_canonical_sha256": base.digest(
            base.canonical(old["snapshot"])
        ),
        "previous_v91_snapshot_canonical_bytes": len(
            base.canonical(old["snapshot"])
        ),
        "lossless_v91_snapshot_identity_status": "PASS",
        "lossless_v91_family_identity_status": "PASS",
        "lossless_v91_all_thirteen_previous_pool_identity_status": "PASS",
        "snapshot": copy.deepcopy(snapshot),
        "headline": copy.deepcopy(headline),
        "families": families,
        POOL_KEY: pool,
        "lossless_v92_zig_v12_complete_plaintext_receipt_count": 1,
        "lossless_v92_zig_v12_complete_source_owner_count": 3,
        "lossless_v92_zig_v12_complete_original_suite_count": 13,
        "preserved_v91_latest_original_campaigns": copy.deepcopy(
            old["latest_original_campaigns"]
        ),
        "latest_original_campaigns": {
            **copy.deepcopy(old["latest_original_campaigns"]),
            "zig": copy.deepcopy(facts),
        },
        **copy.deepcopy(changes),
    })
    for key, size, digest, count in OLD_POOLS:
        whole = base.canonical(summary[key])
        base.need(
            len(whole) == size
            and base.digest(whole) == digest
            and base.canonical(summary[key]) == base.canonical(old[key])
            and len(summary[key]["entries"]) == count,
            "retain every byte of the complete historical V91 proof pool: " + key,
        )
    base.need(
        base.canonical(summary["previous_v91_snapshot"])
        == base.canonical(old["snapshot"])
        and base.canonical(summary["previous_v90_snapshot"])
        == base.canonical(old["previous_v90_snapshot"])
        and base.canonical(summary["previous_v89_snapshot"])
        == base.canonical(old["previous_v89_snapshot"])
        and base.canonical(summary["previous_v88_snapshot"])
        == base.canonical(old["previous_v88_snapshot"])
        and base.canonical(families[0]) == base.canonical(old["families"][0])
        and base.canonical(summary["latest_original_campaigns"]["rust"])
        == base.canonical(old["latest_original_campaigns"]["rust"])
        and base.canonical(summary["latest_original_campaigns"]["c"])
        == base.canonical(old["latest_original_campaigns"]["c"])
        and base.canonical(summary["preserved_v91_latest_original_campaigns"]["zig"])
        == base.canonical(old["latest_original_campaigns"]["zig"])
        and summary["rust_v19_original_campaign_verified_passing_case_count"] == 12942
        and summary["rust_v20_original_campaign_verified_passing_case_count"] == 15749
        and summary["c_v7_original_campaign_verified_passing_case_count"] == 13094
        and summary["zig_v9_original_campaign_verified_passing_case_count"] == 927
        and summary["zig_v10_original_campaign_verified_passing_case_count"] == 3583
        and summary["zig_v12_original_campaign_verified_passing_case_count"] == 4607
        and summary["zig_v12_original_campaign_observed_mismatch_lower_bound"] == 1700
        and summary["zig_v12_original_campaign_semantic_mismatch_count"]
        == "NOT MEASURED"
        and summary["historical_original_rust_verified_passing_case_count"] == 14853
        and summary["authenticated_evidence_owner_lower_bound"] == EVIDENCE_FLOOR
        and summary["authenticated_history_reference_lower_bound"] == HISTORY_FLOOR
        and summary["qualified_candidate_count"] == 0
        and summary["runtime_no_delegation"] == "NOT ESTABLISHED"
        and summary["performance"] == "NOT MEASURED"
        and summary["memory"] == "NOT MEASURED"
        and summary["undefined_behavior"] == "NOT MEASURED"
        and summary["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and summary["expanded_holdout_case_status"] == "NOT GENERATED; NOT OPENED"
        and summary["final_holdout_opened"] is False,
        "preserve all actual histories, Python baseline and sealed proposed holdout",
    )
    validate_evidence_pool(base, summary[POOL_KEY], contract, receipt, facts)
    recovered = resolve_reference(base, pool, reference)
    base.need(
        base.canonical(recovered["validated_campaign_outcome"])
        == base.canonical(facts)
        and base.canonical(summary[LATEST_KEY]) == base.canonical(reference)
        and base.canonical(snapshot[LATEST_KEY]) == base.canonical(reference)
        and base.canonical(inputs[LATEST_KEY]) == base.canonical(reference),
        "retain complete independently verifiable actual Zig V12 evidence",
    )
    assets = {
        INPUT_PATH: inputs_raw,
        SUMMARY_PATH: base.canonical(summary),
        SVG_PATH: svg_raw,
    }
    for path, raw in assets.items():
        base.need(
            type(raw) is bytes
            and 0 < len(raw) <= min(OWNER_LIMIT, base.OWNER_LIMIT),
            "reject oversized complete V92 evidence before publication: " + path,
        )
    return snapshot, assets


def self_test(
    previous: types.ModuleType,
    v90: types.ModuleType,
    v89: types.ModuleType,
    v88: types.ModuleType,
    v87: types.ModuleType,
    v86: types.ModuleType,
    v85: types.ModuleType,
    v84: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> dict:
    prior = previous.self_test(
        v90, v89, v88, v87, v86, v85, v84, v83, v82, chain, base,
        previous_options(previous),
    )
    base.need(
        prior["status"] == "PASS"
        and prior["version"] == 91
        and prior["rejected_hostile_control_count"] == 10777
        and prior["authenticated_evidence_owner_lower_bound"] == 320
        and prior["authenticated_history_reference_lower_bound"] == 325
        and prior["lossless_previous_v90_proof_pool_count"] == 12
        and prior["lossless_v90_all_twelve_previous_pool_identity_status"] == "PASS"
        and prior["lossless_v89_complete_original_suite_reference_count"] == 39
        and prior["lossless_v90_zig_v10_complete_original_suite_count"] == 13
        and prior["lossless_v91_rust_v20_complete_plaintext_receipt_count"] == 1
        and prior["lossless_v91_rust_v20_complete_source_owner_count"] == 3
        and prior["lossless_v91_rust_v20_complete_original_suite_count"] == 13
        and prior["c_v7_original_campaign_verified_passing_case_count"] == 13094
        and prior["rust_v19_original_campaign_verified_passing_case_count"] == 12942
        and prior["rust_v20_original_campaign_verified_passing_case_count"] == 15749
        and prior["zig_v9_original_campaign_verified_passing_case_count"] == 927
        and prior["zig_v10_original_campaign_verified_passing_case_count"] == 3583
        and prior["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and prior["qualified_candidate_count"] == 0
        and prior["performance"] == "NOT MEASURED"
        and prior["outputs_written"] is False,
        "preserve all 10,777 hostile prior controls and exact complete V91 history",
    )
    _, assets = build(
        previous, v90, v89, v88, v87, v86, v85, v84, v83, v82,
        chain, base, options,
    )
    summary = base.document(assets[SUMMARY_PATH], "whole in-memory V92 summary")
    contract, receipt, facts = load_zig_evidence(base)
    pool = summary[POOL_KEY]
    reference = summary[LATEST_KEY]
    rejected = 0

    def reject(label: str, callback: object) -> None:
        nonlocal rejected
        try:
            assert callable(callback)
            callback()
        except Exception:
            rejected += 1
        else:
            base.need(False, "V92 accepted fabricated source evidence: " + label)

    for key in sorted(contract):
        forged = copy.deepcopy(contract)
        forged.pop(key)
        reject(
            "omitted complete Zig V12 source contract field " + key,
            lambda value=forged: validate_source_contract(base, value),
        )
    for key, wrong in (
        ("schema", "fabricated-source"),
        ("version", 11),
        ("family", "external-regex"),
        ("label", "fabricated-campaign"),
        ("status", "CANDIDATE PASS"),
        ("corrected_original_matching", "PASS"),
        ("corrected_supplemental_matching", "PASS"),
        ("current_qualified_candidates", 1),
        ("qualified_candidate_count", 1),
        ("minimum_qualified_candidates", 2),
        ("runtime_non_delegation", "PASS"),
        ("historical_holdout_case_count", HOLDOUT_PROPOSAL_COUNT),
        ("holdout_case_count", CASE_COUNT),
        ("holdout_case_status", "OPENED"),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("memory", "FASTER"),
        ("undefined_behavior", "PASS"),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(contract)
        forged[key] = wrong
        reject(
            "fabricated actual Zig V12 source result:" + key,
            lambda value=forged: validate_source_contract(base, value),
        )
    for role in ("source", "protocol"):
        for field in ("path", "sha256", "bytes", "inode", "device", "nlink", "mode"):
            forged = copy.deepcopy(contract)
            forged[role][field] = "fabricated"
            reject(
                "substituted actual Zig V12 " + role + ":" + field,
                lambda value=forged: validate_source_contract(base, value),
            )
    for index, (suite, _) in enumerate(SUITES):
        forged = copy.deepcopy(contract)
        forged["original_oracle"]["suites"][index]["id"] = "invented-suite"
        reject(
            "omitted frozen original Zig V12 obligation:" + suite,
            lambda value=forged: validate_source_contract(base, value),
        )
    for field, wrong in (
        ("case_execution_denominator", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("suite_count", 12),
        ("named_private_waiver_count", 12),
        ("supplemental_case_count", 0),
        ("supplemental_cases_added_to_original_denominator", True),
        ("supplemental_candidate_matching", "PASS"),
    ):
        forged = copy.deepcopy(contract)
        forged["original_oracle"][field] = wrong
        reject(
            "fabricated original Zig V12 obligation:" + field,
            lambda value=forged: validate_source_contract(base, value),
        )
    for field, wrong in (
        ("installed_before_candidate_import", False),
        ("ctypes_dlopen_permitted", True),
        ("external_regex_package_permitted", True),
        ("fallback_permitted", True),
        ("other_candidate_permitted", True),
        ("stdlib_regex_engine_permitted", True),
    ):
        forged = copy.deepcopy(contract)
        forged["immutable_v2_runtime_guard"][field] = wrong
        reject(
            "forged first-party Zig V12 runtime guard:" + field,
            lambda value=forged: validate_source_contract(base, value),
        )
    for field in sorted(contract["source_only_effects"]):
        forged = copy.deepcopy(contract)
        forged["source_only_effects"][field] = 1
        reject(
            "forbidden actual Zig V12 source-mode side effect:" + field,
            lambda value=forged: validate_source_contract(base, value),
        )
    for key in sorted(receipt):
        forged = copy.deepcopy(receipt)
        forged.pop(key)
        reject(
            "omitted complete actual Zig V12 receipt field " + key,
            lambda value=forged: validate_zig_receipt(base, value),
        )
    for key, wrong in (
        ("schema", "fabricated-receipt"),
        ("family", "external-regex"),
        ("label", "fabricated-campaign"),
        ("status", "FAIL"),
        ("publication_pass_means", "CANDIDATE QUALIFIED"),
        ("original_campaign_passed", True),
        ("candidate_status", "PASS"),
        ("candidate_qualified", True),
        ("source_sha256", "0" * 64),
        ("protocol_sha256", "0" * 64),
        ("contract_sha256", "0" * 64),
        ("suite_count", 12),
        ("case_execution_denominator", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("actual_candidate_workers", 12),
        ("unique_candidate_worker_count", 12),
        ("all_original_suites_attempted", False),
        ("completed_suite_count", 13),
        ("verified_passing_case_count", CASE_COUNT),
        ("observed_semantic_mismatch_lower_bound", 0),
        ("semantic_mismatch_count", 1700),
        ("infrastructure_failure_count", 0),
        ("infrastructure_failure_suites", []),
        ("all_three_original_targets_restored", False),
        ("supplemental_candidate_matching", "PASS"),
        ("timeout_count", 1),
        ("timed_out_suites", ["subinterpreter_v2"]),
        ("timeout_classification", "CANDIDATE PASS"),
        ("per_suite_timeout_seconds", 0),
        ("maximum_serial_worker_timeout_seconds", 0),
        ("hidden_cases_read", 1),
        ("benchmark_files_read", 1),
        ("timing_trials_run", 1),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("memory", "FASTER"),
        ("undefined_behavior", "PASS"),
        ("winner_selected", True),
        ("uncompressed_bytes", 1),
        ("uncompressed_sha256", "0" * 64),
        ("failed_suites", []),
    ):
        forged = copy.deepcopy(receipt)
        forged[key] = wrong
        reject(
            "fabricated actual Zig V12 campaign result:" + key,
            lambda value=forged: validate_zig_receipt(base, value),
        )
    for index, (suite, _) in enumerate(SUITES):
        for field in sorted(ROW_KEYS):
            forged = copy.deepcopy(receipt)
            forged["original_suite_diagnostics"][index].pop(field)
            reject(
                "omitted complete Zig V12 worker " + suite + ":" + field,
                lambda value=forged: validate_zig_receipt(base, value),
            )
        for field, wrong in (
            ("suite", "invented-suite"),
            ("case_execution_denominator", CASE_COUNT),
            ("candidate_imported", False),
            ("guard_installed_before_candidate_import", False),
            ("pid", 0),
            ("returncode", 1),
            ("timed_out", True),
            ("timeout_seconds", 0),
            ("timeout_classification", "INFRASTRUCTURE FAILURE"),
        ):
            forged = copy.deepcopy(receipt)
            forged["original_suite_diagnostics"][index][field] = wrong
            reject(
                "forged actual guarded Zig V12 worker " + suite + ":" + field,
                lambda value=forged: validate_zig_receipt(base, value),
            )
        for stream_name in ("stdout", "stderr"):
            for field, wrong in (
                ("sha256", "0" * 64),
                ("bytes", -1),
                ("complete", False),
                ("complete_payload_preserved_in_actual_archive", False),
            ):
                forged = copy.deepcopy(receipt)
                forged["original_suite_diagnostics"][index][stream_name][field] = wrong
                reject(
                    "forged complete actual Zig V12 "
                    + suite + ":" + stream_name + ":" + field,
                    lambda value=forged: validate_zig_receipt(base, value),
                )
    for suite in MISMATCHES:
        forged = copy.deepcopy(receipt)
        for row in forged["original_suite_diagnostics"]:
            if row["suite"] == suite:
                row["observed_semantic_mismatch_count"] = 0
        reject(
            "concealed actual Zig V12 semantic mismatches:" + suite,
            lambda value=forged: validate_zig_receipt(base, value),
        )
    for field, wrong in (
        ("status", "PASS"),
        ("candidate_qualified", True),
        ("actual_child_guards_installed", 0),
        ("hidden_cases_read", 1),
        ("benchmark_files_read", 1),
        ("clock_samples", 1),
        ("timing_trials_run", 1),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("winner_selected", True),
    ):
        forged = copy.deepcopy(receipt)
        forged["original_suite_diagnostics"][10][
            "complete_actual_suite_failure_details"
        ][field] = wrong
        reject(
            "concealed genuine guarded Zig V12 lifecycle failure:" + field,
            lambda value=forged: validate_zig_receipt(base, value),
        )
    for key, wrong in (
        ("schema", "fabricated-reference"),
        ("family", "external-regex"),
        ("complete_plaintext_receipt_sha256", "0" * 64),
        ("complete_plaintext_receipt_bytes", 1),
        ("complete_first_party_source_owner_count", 2),
        ("complete_reference_sha256", "0" * 64),
        ("complete_reference_canonical_bytes", 1),
    ):
        forged = copy.deepcopy(reference)
        forged[key] = wrong
        reject(
            "fabricated complete actual Zig V12 reference:" + key,
            lambda value=forged: resolve_reference(base, pool, value),
        )
    for field in sorted(pool):
        forged = copy.deepcopy(pool)
        forged.pop(field)
        reject(
            "omitted complete actual Zig V12 evidence pool field:" + field,
            lambda value=forged: validate_evidence_pool(
                base, value, contract, receipt, facts
            ),
        )
    forged = copy.deepcopy(pool)
    forged["entries"].pop(ZIG_RECEIPT[1])
    reject(
        "omitted complete actual Zig V12 evidence pool entry",
        lambda value=forged: validate_evidence_pool(
            base, value, contract, receipt, facts
        ),
    )
    entry = pool["entries"][ZIG_RECEIPT[1]]
    for field in sorted(entry):
        forged = copy.deepcopy(pool)
        forged["entries"][ZIG_RECEIPT[1]].pop(field)
        reject(
            "omitted complete actual Zig V12 evidence entry field:" + field,
            lambda value=forged: validate_evidence_pool(
                base, value, contract, receipt, facts
            ),
        )
    for index, (suite, _) in enumerate(SUITES):
        forged = copy.deepcopy(pool)
        forged["entries"][ZIG_RECEIPT[1]]["complete_original_suite_rows"].pop(index)
        reject(
            "omitted complete genuine Zig V12 original worker proof:" + suite,
            lambda value=forged: validate_evidence_pool(
                base, value, contract, receipt, facts
            ),
        )
    old = authenticate_previous(
        previous, v90, v89, v88, v87, v86, v85, v84, v83, v82, chain, base,
    )
    for index, row in enumerate(summary["families"]):
        if row["family"] == "python":
            forged = copy.deepcopy(summary["families"])
            forged[index]["correctness"] = "INVENTED"
            reject(
                "changed exact unchanged Python baseline",
                lambda value=forged: validate_families(
                    base, old, value, pool, reference, facts
                ),
            )
            continue
        for key, wrong in (
            ("qualified", True),
            ("runtime_no_delegation", "PASS"),
            ("performance", "1.5x"),
            ("authenticated_evidence_owner_lower_bound", EVIDENCE_FLOOR - 1),
            ("authenticated_history_reference_lower_bound", HISTORY_FLOOR + 1),
        ):
            forged = copy.deepcopy(summary["families"])
            forged[index][key] = wrong
            reject(
                "fabricated compatible or faster engine " + row["family"] + ":" + key,
                lambda value=forged: validate_families(
                    base, old, value, pool, reference, facts
                ),
            )
    for event, arguments in (
        ("open", (str(ROOT / "hidden.gz"), "rb", os.O_RDONLY)),
        ("open", (str(ROOT / INPUT_PATH), "rb", os.O_RDONLY)),
        ("open", (str(ROOT / SUMMARY_PATH), "rb", os.O_RDONLY)),
        ("open", (str(ROOT / SVG_PATH), "rb", os.O_RDONLY)),
        ("open", ("/tmp/rebar-private-root", "rb", os.O_RDONLY)),
        ("open", (str(ROOT / "safe.json"), "wb", os.O_WRONLY | os.O_CREAT)),
        ("subprocess.Popen", ("candidate",)),
        ("ctypes.dlopen", ("external-regex.so",)),
        ("socket.connect", ("example.invalid",)),
        ("import", ("regex", None, None, None, None)),
        ("import", ("re", None, None, None, None)),
        ("import", ("_sre", None, None, None, None)),
        ("import", ("candidates.zig_candidate", None, None, None, None)),
        ("import", ("gzip", None, None, None, None)),
        ("import", ("time", None, None, None, None)),
    ):
        reject(
            "forbidden source-only side effect " + event,
            lambda name=event, values=arguments: audit_wall(name, values),
        )
    base.need(rejected >= 700, "require comprehensive actual Zig V12 hostile controls")
    return result_payload(base, options, assets, False, {
        "schema": SCHEMA + "-source-only-self-test",
        "inherited_rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": prior[
            "rejected_hostile_control_count"
        ] + rejected,
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
        "version": 92,
        "status": "PASS",
        "source_sha256": options.source_sha256,
        "source_bytes": options.source_bytes,
        "inputs_sha256": base.digest(assets[INPUT_PATH]),
        "inputs_bytes": len(assets[INPUT_PATH]),
        "summary_sha256": base.digest(assets[SUMMARY_PATH]),
        "summary_bytes": len(assets[SUMMARY_PATH]),
        "svg_sha256": base.digest(assets[SVG_PATH]),
        "svg_bytes": len(assets[SVG_PATH]),
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "v92_new_directly_authenticated_owner_count": 4,
        "v92_new_directly_authenticated_zig_source_owner_count": 3,
        "v92_new_directly_authenticated_zig_plaintext_receipt_owner_count": 1,
        "lossless_previous_v91_proof_pool_count": len(OLD_POOLS),
        "lossless_v91_all_thirteen_previous_pool_identity_status": "PASS",
        "lossless_v91_snapshot_identity_status": "PASS",
        "lossless_v91_family_identity_status": "PASS",
        "lossless_v89_complete_original_suite_reference_count": 39,
        "lossless_v90_zig_v10_complete_original_suite_count": 13,
        "lossless_v91_rust_v20_complete_original_suite_count": 13,
        "lossless_v92_zig_v12_complete_plaintext_receipt_count": 1,
        "lossless_v92_zig_v12_complete_source_owner_count": 3,
        "lossless_v92_zig_v12_complete_original_suite_count": 13,
        "original_case_execution_denominator": CASE_COUNT,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "c_v7_original_campaign_clean_suite_count": 2,
        "c_v7_original_campaign_completed_suite_count": 5,
        "c_v7_original_campaign_verified_passing_case_count": 13094,
        "c_v7_original_campaign_observed_mismatch_lower_bound": 236,
        "c_v7_original_campaign_candidate_execution_failure_count": 7,
        "c_v7_original_campaign_infrastructure_failure_count": 1,
        "rust_v19_original_campaign_clean_suite_count": 6,
        "rust_v19_original_campaign_completed_suite_count": 8,
        "rust_v19_original_campaign_verified_passing_case_count": 12942,
        "rust_v19_original_campaign_observed_mismatch_lower_bound": 1296,
        "rust_v19_original_campaign_infrastructure_failure_count": 5,
        "rust_v20_original_campaign_actual_worker_count": 13,
        "rust_v20_original_campaign_clean_suite_count": 10,
        "rust_v20_original_campaign_completed_suite_count": 12,
        "rust_v20_original_campaign_mismatch_suite_count": 2,
        "rust_v20_original_campaign_verified_passing_case_count": 15749,
        "rust_v20_original_campaign_observed_mismatch_lower_bound": 1296,
        "rust_v20_original_campaign_infrastructure_failure_count": 1,
        "rust_v20_original_campaign_infrastructure_failure_suite":
        "subinterpreter_v2",
        "rust_v20_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "rust_v20_original_campaign_all_four_original_targets_restored": True,
        "zig_v9_original_campaign_verified_passing_case_count": 927,
        "zig_v10_original_campaign_clean_suite_count": 6,
        "zig_v10_original_campaign_completed_suite_count": 9,
        "zig_v10_original_campaign_verified_passing_case_count": 3583,
        "zig_v10_original_campaign_observed_mismatch_lower_bound": 1540,
        "zig_v10_original_campaign_infrastructure_failure_count": 4,
        "zig_v12_original_campaign_actual_worker_count": 13,
        "zig_v12_original_campaign_distinct_worker_count": 13,
        "zig_v12_original_campaign_individually_proven_guarded_candidate_import_count": 13,
        "zig_v12_original_campaign_candidate_import_status_unknown_count": 0,
        "zig_v12_original_campaign_clean_suite_count": 7,
        "zig_v12_original_campaign_completed_suite_count": 12,
        "zig_v12_original_campaign_mismatch_suite_count": 5,
        "zig_v12_original_campaign_verified_passing_case_count": 4607,
        "zig_v12_original_campaign_observed_mismatch_lower_bound": 1700,
        "zig_v12_original_campaign_infrastructure_failure_count": 1,
        "zig_v12_original_campaign_infrastructure_failure_suite":
        "subinterpreter_v2",
        "zig_v12_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "zig_v12_original_campaign_all_three_original_targets_restored": True,
        "historical_original_rust_semantic_mismatch_count": 1440,
        "historical_original_rust_verified_passing_case_count": 14853,
        "historical_original_c_semantic_mismatch_count": 1230,
        "historical_original_c_verified_passing_case_count": 7325,
        "historical_original_zig_semantic_mismatch_count": 1764,
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
        "publish only one bounded, exclusively created new V92 graph owner",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0, "publish complete V92 bytes")
            remaining = remaining[count:]
        os.fsync(handle)
        owner = os.fstat(handle)
        base.need(
            owner.st_uid == os.geteuid()
            and owner.st_dev == 2064
            and owner.st_nlink == 1
            and owner.st_size == len(raw)
            and stat.S_IMODE(owner.st_mode) == 0o600,
            "authenticate the whole exclusively published V92 evidence owner",
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
    base.need(actual == raw, "reauthenticate every complete final V92 evidence byte")


def parse(arguments: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", required=True, type=int)
    for role in V91:
        parser.add_argument("--previous-" + role + "-sha256", required=True)
    for role in ZIG_SOURCE:
        parser.add_argument("--zig-" + role + "-sha256", required=True)
    parser.add_argument("--zig-receipt-sha256", required=True)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse(arguments)
    try:
        previous, v90, v89, v88, v87, v86, v85, v84, v83, v82, chain, base = (
            load_previous()
        )
        if not options.render:
            sys.addaudithook(audit_wall)
        if options.self_test:
            result = self_test(
                previous, v90, v89, v88, v87, v86, v85, v84, v83, v82,
                chain, base, options,
            )
        else:
            _, assets = build(
                previous, v90, v89, v88, v87, v86, v85, v84, v83, v82,
                chain, base, options,
            )
            if options.render:
                for path, raw in assets.items():
                    publish(base, path, raw)
            result = result_payload(base, options, assets, bool(options.render))
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except Exception as error:
        sys.stderr.write("current V92 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
