#!/usr/bin/env python3
"""Freeze the guard-clean, V19-backed original Rust correctness campaign.

Source operations authenticate the actual V12 loss and the current V80 graph.
They never import a candidate, install an audit hook, open a private root or
archive, start a process, sample a clock, or open a holdout.  An independently
authorized actual worker preserves all thirteen original V5 observers while
removing only four authenticated historical, top-level ctypes imports.
"""

from __future__ import annotations

import ast
import hashlib
import importlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/run_owned_repaired_rust_original_campaign_v14.py"
PROTOCOL = "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V14.md"
CONTRACT = "oracle/phase2/repaired-rust-original-campaign-v14.json"
SCHEMA = "rebar-owned-repaired-rust-original-campaign-v14"
LABEL = "phase2-v19-rust-buffer-shape-root-provenance-original-p0-v14"
RECOVERY_PREFIX = "rebar-phase2-repaired-rust-original-campaign-v14-"
RECOVERY_ROOT = (
    "/tmp/" + RECOVERY_PREFIX
    + "phase2-v19-rust-buffer-shape-root-provenance-original-p0"
)
CURRENT_EVIDENCE_FLOOR = 262
CURRENT_HISTORY_FLOOR = 267
CASE_COUNT = 31237
WORKER_COUNT = 13
PRIVATE_WAIVER_COUNT = 13

V12 = (
    ("tools/run_owned_repaired_rust_original_campaign_v12.py",
     "fc3a40901989bf0ccef6fe5296101c6bb456a6d3117d8b60e75c2cdf1eb113f9",
     72836, 431362),
    ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V12.md",
     "1473e2d1f8967f6dfd565d8e3c05dec7383e8705d624cffab2fb0c13342a1674",
     8755, 524871),
    ("oracle/phase2/repaired-rust-original-campaign-v12.json",
     "6ccc0f18dbcc7ff6f401d42f5fabb199420e2a1afe79558d035efcfc607fa375",
     7240, 524872),
)
V13 = (
    ("tools/run_owned_repaired_rust_original_campaign_v13.py",
     "2b1a6a928df45e9dbad561b3101689de3ee5cac49df5269f18254ebf0f529f14",
     59547, 431504),
    ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V13.md",
     "21091d90c571c751dea19f10a57adfa1e1997f5178cba047df755391619e20fb",
     10348, 525022),
    ("oracle/phase2/repaired-rust-original-campaign-v13.json",
     "94f0acafa2e6c5ecf3c79f272ef1ded39c894a2abb00d50b35d420ddac84a5fe",
     9205, 525023),
)
V13_FAILURE = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v13-rust-phase2-v19-rust-"
    "buffer-shape-root-provenance-original-p0-v13-failures-"
    "publication-receipt.json",
    "6f990183501953c42af374a896fad6b64f909514c731cb9de4fb37faf4d3bf86",
    6744, 525049,
)
FAILURE_STREAM_LIMIT = 65536
FAILURE_TRACEBACK_LIMIT = 65536
FAILURE_TOTAL_DIAGNOSTIC_BUDGET = 4 * 1024 * 1024

V12_FAILURE = (
    "oracle/phase2/evidence/"
    "repaired-rust-original-campaign-v12-rust-phase2-v19-rust-"
    "buffer-shape-root-provenance-original-p0-v12-failures-"
    "publication-receipt.json",
    "6537561a46fe6b7ab294126628fa5d82c34f03c3d0bac6455112dae3eea11658",
    6744, 524989,
)
GRAPH = (
    ("tools/render_candidate_current_overview_v80.py",
     "8454705356bffd9e3c576b24df9ab8e572aff96c401ed60bd74657c8b5a1dd5a",
     57094, 431526),
    ("docs/evidence/candidate-current-overview-v80.inputs.json",
     "5f881e270b5080f1579e79ac16e79a5a53a905d1e708b7b47e2ea1c68a02ea19",
     1229041, 431527),
    ("docs/evidence/candidate-current-overview-v80.json",
     "21d0e0fc7c9603d7a2e83a66deb549947481334a8b51d65fff2d82038628f19d",
     3852490, 431528),
    ("docs/evidence/candidate-current-overview-v80.svg",
     "28fbe95147ca9dbf9d4a5874f6efa0d8d0f5ffc439c61d1f7bb361224a907547",
     5298, 431529),
)

# Each tuple is the unchanged authenticated source and its one exact line.
HISTORY = (
    ("v11", "tools/run_owned_repaired_rust_original_campaign_v11.py",
     "27bf88358d5a45a5b487680e70f5fa5b5192a05f053f33f6ddb651c972c94f2d",
     310760, 430525, 18),
    ("v7", "tools/run_owned_repaired_rust_original_campaign_v7.py",
     "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104",
     505616, 431856, 16),
    ("v2", "tools/run_owned_repaired_rust_original_campaign_v2.py",
     "a6ffce3eb9ff09f27f3e35f84b35b9d1aba6e29dae225c56c036de85e089b7b3",
     143441, 429079, 15),
    ("v4", "tools/run_owned_six_family_original_p0_producer_v4.py",
     "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8",
     230782, 431710, 21),
)
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1024), ("buffer_v3", 768), ("managed_v1", 1024),
    ("scanner_verbose_v1", 2854), ("public_types_v1", 6912),
    ("substitution_v2", 5120), ("shape_v2", 10240),
    ("public_surface_v19", 1376), ("subinterpreter_v2", 128),
    ("pep688_v4", 264), ("threaded_pattern_v1", 512),
)

PROXY_SOURCE = (
    "class _RebarV14ForbiddenCtypes:\n"
    "    __slots__ = ()\n"
    "    def __getattribute__(self, name):\n"
    "        raise RuntimeError(\n"
    "            'V14 forbids every historical ctypes operation: ' + str(name)\n"
    "        )\n"
    "ctypes = _RebarV14ForbiddenCtypes()\n"
)


class CampaignError(Exception):
    """A frozen owner, narrow transformation, or actual authority failed."""


def need(value: object, message: str) -> None:
    if not value:
        raise CampaignError(message)


def exact_digest(value: object, label: str) -> str:
    need(isinstance(value, str) and len(value) == 64
         and all(item in "0123456789abcdef" for item in value),
         "require exact SHA-256 for " + label)
    assert isinstance(value, str)
    return value


def read_exact(owner: tuple, *, maximum: int = 4 * 1024 * 1024) -> bytes:
    relative, digest, count, inode = owner
    need(isinstance(relative, str) and relative and not relative.startswith("/")
         and ".." not in relative.split("/")
         and not relative.endswith((".gz", ".so")),
         "reject an archive, binary, or unsafe source-only owner")
    exact_digest(digest, relative)
    need(isinstance(count, int) and 0 < count <= maximum
         and isinstance(inode, int) and inode > 0,
         "reject invalid immutable owner identity: " + relative)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(os.path.join(ROOT, relative), flags)
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode) and before.st_dev == 2064
             and before.st_ino == inode and before.st_size == count
             and before.st_uid == os.geteuid() and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o600,
             "reject substituted immutable owner: " + relative)
        pieces: list[bytes] = []
        remaining = count
        while remaining:
            part = os.read(descriptor, min(remaining, 262144))
            need(bool(part), "reject truncated immutable owner: " + relative)
            pieces.append(part)
            remaining -= len(part)
        need(not os.read(descriptor, 1),
             "reject expanded immutable owner: " + relative)
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        need(hashlib.sha256(raw).hexdigest() == digest
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject modified immutable owner: " + relative)
        return raw
    finally:
        os.close(descriptor)


def live_self(relative: str, digest: str) -> tuple:
    exact_digest(digest, relative)
    need(relative in (SOURCE, PROTOCOL, CONTRACT),
         "reject an unrelated V14 live owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(os.path.join(ROOT, relative), flags)
    try:
        found = os.fstat(descriptor)
        need(stat.S_ISREG(found.st_mode) and found.st_dev == 2064
             and found.st_uid == os.geteuid() and found.st_nlink == 1
             and stat.S_IMODE(found.st_mode) == 0o600
             and 0 < found.st_size <= 512 * 1024,
             "reject substituted V14 source-freeze owner: " + relative)
        return relative, digest, found.st_size, found.st_ino
    finally:
        os.close(descriptor)


def assert_sterile() -> None:
    need(sys.flags.isolated == 1 and sys.flags.no_site == 1
         and sys.dont_write_bytecode and sys.executable == PYTHON
         and sys.version_info[:3] == (3, 14, 6),
         "require pinned isolated, site-free CPython 3.14.6")
    need("re" not in sys.modules and "_sre" not in sys.modules
         and "ctypes" not in sys.modules and "regex" not in sys.modules
         and not any(name == "candidates" or name.startswith("candidates.")
                     for name in sys.modules),
         "reject a preloaded matcher, candidate, or native ctypes loader")


def owner_identity_matches(value: object, owner: tuple) -> bool:
    if not isinstance(value, dict):
        return False
    return (value.get("path") == owner[0]
            and value.get("sha256") == owner[1]
            and value.get("bytes") == owner[2]
            and value.get("device") == 2064
            and value.get("inode") == owner[3]
            and value.get("mode") == "0600"
            and value.get("nlink") == 1
            and value.get("uid") == os.geteuid())


def load_v12() -> types.ModuleType:
    raw = read_exact(V12[0])
    read_exact(V12[1])
    read_exact(V12[2])
    module = types.ModuleType("_rebar_v14_authenticated_v12_source")
    module.__file__ = os.path.join(ROOT, V12[0][0])
    exec(compile(raw, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    need(module.SOURCE == V12[0][0] and module.PROTOCOL == V12[1][0]
         and module.CONTRACT == V12[2][0]
         and module.SCHEMA == "rebar-owned-repaired-rust-original-campaign-v12"
         and tuple(module.SUITES) == SUITES
         and module.CASE_COUNT == CASE_COUNT
         and module.WORKER_COUNT == WORKER_COUNT
         and callable(module.verify_frozen_context)
         and callable(module.install_worker_guard)
         and callable(module.derive_v19_private_report),
         "reject an altered genuine V12 campaign or original dispatcher")
    return module


def historical_owner(record: tuple) -> tuple:
    return record[1], record[2], record[3], record[4]


def reject_dynamic_ctypes(tree: ast.AST, label: str) -> None:
    for item in ast.walk(tree):
        if isinstance(item, ast.ImportFrom):
            need(not (isinstance(item.module, str)
                      and (item.module == "ctypes"
                           or item.module.startswith("ctypes."))),
                 "reject hidden from-ctypes import: " + label)
        if isinstance(item, ast.Import):
            for alias in item.names:
                if alias.name == "ctypes" or alias.name.startswith("ctypes."):
                    need(item in getattr(tree, "body", ())
                         and len(item.names) == 1
                         and alias.name == "ctypes" and alias.asname is None,
                         "reject hidden or aliased ctypes import: " + label)
        if isinstance(item, ast.Call):
            first = item.args[0] if item.args else None
            if not (isinstance(first, ast.Constant)
                    and isinstance(first.value, str)
                    and (first.value == "ctypes"
                         or first.value.startswith("ctypes."))):
                continue
            direct = isinstance(item.func, ast.Name)
            direct = direct and item.func.id == "__import__"
            indirect = (isinstance(item.func, ast.Attribute)
                        and item.func.attr == "import_module")
            need(not (direct or indirect),
                 "reject a dynamic native ctypes import: " + label)


def clean_history(raw: bytes, record: tuple) -> bytes:
    role, relative, digest, count, _, exact_line = record
    need(isinstance(raw, bytes) and len(raw) == count
         and hashlib.sha256(raw).hexdigest() == digest,
         "authenticate original historical source before transformation: "
         + role)
    text = raw.decode("utf-8", "strict")
    tree = ast.parse(text, filename=relative)
    reject_dynamic_ctypes(tree, role)
    imports = [item for item in tree.body
               if isinstance(item, ast.Import)
               and any(alias.name == "ctypes" for alias in item.names)]
    need(len(imports) == 1, "require one top-level ctypes import: " + role)
    node = imports[0]
    need(len(node.names) == 1 and node.names[0].name == "ctypes"
         and node.names[0].asname is None and node.lineno == exact_line
         and node.end_lineno == exact_line and node.col_offset == 0,
         "reject moved, aliased, or expanded ctypes import: " + role)
    lines = text.splitlines(keepends=True)
    need(0 < exact_line <= len(lines)
         and lines[exact_line - 1] in ("import ctypes\n", "import ctypes\r\n"),
         "reject changed exact historical import line: " + role)
    before = "".join(lines[:exact_line - 1])
    after = "".join(lines[exact_line:])
    transformed = (before + PROXY_SOURCE + after).encode("utf-8")
    clean_tree = ast.parse(transformed, filename=relative)
    reject_dynamic_ctypes(clean_tree, role)
    need(not any(isinstance(item, ast.Import)
                 and any(alias.name == "ctypes"
                         or alias.name.startswith("ctypes.")
                         for alias in item.names)
                 for item in ast.walk(clean_tree)),
         "never execute a historical ctypes import: " + role)
    need(text == before + lines[exact_line - 1] + after
         and transformed == before.encode("utf-8")
         + PROXY_SOURCE.encode("utf-8") + after.encode("utf-8"),
         "change only the one authenticated top-level import: " + role)
    return transformed


def failure_and_graph(guard: types.ModuleType, base: types.ModuleType
                      ) -> tuple[dict, dict, dict]:
    for owner in GRAPH:
        read_exact(owner)
    failure = base.parse_document(
        guard, read_exact(V12_FAILURE), "actual durable V12 failure receipt",
    )
    need(failure.get("schema")
         == "rebar-owned-repaired-rust-original-campaign-v12-"
         "durable-publication-receipt"
         and failure.get("status") == "PASS"
         and failure.get("publication_status") == "PASS"
         and failure.get("publication_pass_means")
         == "DURABLE PUBLICATION ONLY"
         and failure.get("candidate_status") == "FAIL"
         and failure.get("candidate_qualified") is False
         and failure.get("suite_count") == WORKER_COUNT
         and failure.get("case_execution_denominator") == CASE_COUNT
         and failure.get("actual_candidate_workers") == WORKER_COUNT
         and failure.get("attempted_suite_count") == WORKER_COUNT
         and failure.get("started_suite_count") == WORKER_COUNT
         and failure.get("completed_suite_count") == 0
         and failure.get("distinct_worker_process_id_count") == WORKER_COUNT
         and failure.get("infrastructure_failure_count") == WORKER_COUNT
         and failure.get("semantic_mismatch_count") == "NOT MEASURED"
         and failure.get("verified_passing_case_count") == 0
         and failure.get("all_original_observation_vectors_complete") is False
         and failure.get("all_four_original_targets_restored") is True
         and failure.get("restoration_verified_before_publication") is True
         and failure.get("resulting_repository_evidence_owner_count") == 257
         and failure.get("resulting_authenticated_reference_count") == 262
         and failure.get("campaign_source_sha256") == V12[0][1]
         and failure.get("campaign_protocol_sha256") == V12[1][1]
         and failure.get("campaign_contract_sha256") == V12[2][1]
         and failure.get("actual_v19_build_archive_read_count") == 0
         and failure.get("actual_v19_build_archive_gzip_inflation_count") == 0
         and failure.get("hidden_cases_read") == 0
         and failure.get("benchmark_files_read") == 0
         and failure.get("clock_samples") == 0
         and failure.get("timing_trials_run") == 0
         and failure.get("holdout") == "NOT OPENED"
         and failure.get("performance") == "NOT MEASURED"
         and failure.get("winner_selected") is False,
         "preserve the genuine thirteen-worker V12 infrastructure failure")
    for owner in V13:
        read_exact(owner)
    previous_source = base.parse_document(
        guard, read_exact(V13[2]), "complete frozen V13 source contract",
    )
    need(previous_source.get("schema")
         == "rebar-owned-repaired-rust-original-campaign-v13-"
         "recoverable-source-freeze"
         and previous_source.get("status")
         == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
         and previous_source.get("version") == 13
         and previous_source.get("source_sha256") == V13[0][1]
         and previous_source.get("protocol_sha256") == V13[1][1]
         and previous_source.get("historical_ctypes_source_count") == 4
         and previous_source.get("historical_ctypes_proxy_native_load_permitted")
         is False
         and previous_source.get("historical_ctypes_preloaded") is False
         and previous_source.get("v12_actual_failure_receipt_sha256")
         == V12_FAILURE[1],
         "retain the unchanged four-way guard-clean V13 experiment")
    v13_failure = base.parse_document(
        guard, read_exact(V13_FAILURE), "actual durable V13 failure receipt",
    )
    need(v13_failure.get("schema")
         == "rebar-owned-repaired-rust-original-campaign-v13-"
         "durable-publication-receipt"
         and v13_failure.get("status") == "PASS"
         and v13_failure.get("publication_status") == "PASS"
         and v13_failure.get("publication_pass_means")
         == "DURABLE PUBLICATION ONLY"
         and v13_failure.get("candidate_status") == "FAIL"
         and v13_failure.get("candidate_qualified") is False
         and v13_failure.get("suite_count") == WORKER_COUNT
         and v13_failure.get("case_execution_denominator") == CASE_COUNT
         and v13_failure.get("actual_candidate_workers") == WORKER_COUNT
         and v13_failure.get("attempted_suite_count") == WORKER_COUNT
         and v13_failure.get("started_suite_count") == WORKER_COUNT
         and v13_failure.get("completed_suite_count") == 0
         and v13_failure.get("distinct_worker_process_id_count") == WORKER_COUNT
         and v13_failure.get("infrastructure_failure_count") == WORKER_COUNT
         and v13_failure.get("semantic_mismatch_count") == "NOT MEASURED"
         and v13_failure.get("verified_passing_case_count") == 0
         and v13_failure.get("all_original_observation_vectors_complete")
         is False
         and v13_failure.get("all_four_original_targets_restored") is True
         and v13_failure.get("restoration_verified_before_publication") is True
         and v13_failure.get("resulting_repository_evidence_owner_count")
         == CURRENT_EVIDENCE_FLOOR
         and v13_failure.get("resulting_authenticated_reference_count")
         == CURRENT_HISTORY_FLOOR
         and v13_failure.get("campaign_source_sha256") == V13[0][1]
         and v13_failure.get("campaign_protocol_sha256") == V13[1][1]
         and v13_failure.get("campaign_contract_sha256") == V13[2][1]
         and v13_failure.get("actual_v19_build_archive_read_count") == 0
         and v13_failure.get("actual_v19_build_archive_gzip_inflation_count") == 0
         and v13_failure.get("hidden_cases_read") == 0
         and v13_failure.get("benchmark_files_read") == 0
         and v13_failure.get("clock_samples") == 0
         and v13_failure.get("timing_trials_run") == 0
         and v13_failure.get("holdout") == "NOT OPENED"
         and v13_failure.get("performance") == "NOT MEASURED"
         and v13_failure.get("winner_selected") is False,
         "preserve the real thirteen-worker V13 empty-output failure")
    graph = base.parse_document(
        guard, read_exact(GRAPH[2]), "truthful current V80 summary",
    )
    need(graph.get("schema") == "rebar-candidate-current-overview-v80-summary"
         and graph.get("status") == "PASS" and graph.get("version") == 80
         and graph.get("actual_current_graph_predecessor_version") == 79
         and graph.get("full_case_denominator") == CASE_COUNT
         and graph.get("suite_count") == WORKER_COUNT
         and graph.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
         and graph.get("authenticated_evidence_owner_lower_bound")
         == CURRENT_EVIDENCE_FLOOR
         and graph.get("authenticated_history_reference_lower_bound")
         == CURRENT_HISTORY_FLOOR
         and graph.get("qualified_candidate_count") == 0
         and graph.get("runtime_no_delegation") == "NOT ESTABLISHED"
         and graph.get("performance") == "NOT MEASURED"
         and graph.get("final_holdout_opened") is False
         and graph.get("winner_selected") is False
         and graph.get("actual_candidate_workers_started_by_graph") == 0
         and graph.get("actual_native_libraries_loaded_by_graph") == 0
         and graph.get("actual_hidden_cases_read_by_graph") == 0
         and graph.get("actual_clock_samples_by_graph") == 0
         and graph.get("timing_trials_run") == 0,
         "require the current truthful V80 graph, not a stale result")
    source = graph.get("rust_v12_original_campaign_source_freeze")
    need(isinstance(source, dict)
         and source.get("schema")
         == "rebar-candidate-current-overview-v77-guarded-rust-"
         "original-campaign-v12"
         and source.get("version") == 12
         and source.get("status")
         == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
         and source.get("independent_source_owner_count") == 3,
         "retain the authentic V12 source-freeze feature")
    identities = source.get("owners")
    need(isinstance(identities, dict)
         and all(owner_identity_matches(identities.get(role), owner)
                 for role, owner in zip(("source", "protocol", "contract"),
                                        V12, strict=True)),
         "bind all three actual immutable V12 source owners")
    actual = graph.get("actual_rust_v12_original_campaign")
    need(isinstance(actual, dict)
         and actual.get("schema")
         == "rebar-candidate-current-overview-v78-actual-rust-"
         "original-campaign-v12-outcome"
         and actual.get("version") == 12
         and actual.get("candidate_status") == "FAIL"
         and actual.get("publication_status") == "PASS"
         and actual.get("publication_pass_means")
         == "DURABLE PUBLICATION ONLY"
         and actual.get("actual_candidate_worker_count") == WORKER_COUNT
         and actual.get("attempted_suite_count") == WORKER_COUNT
         and actual.get("started_suite_count") == WORKER_COUNT
         and actual.get("completed_suite_count") == 0
         and actual.get("distinct_worker_process_id_count") == WORKER_COUNT
         and actual.get("infrastructure_failure_count") == WORKER_COUNT
         and actual.get("semantic_mismatch_count") == "NOT MEASURED"
         and actual.get("verified_passing_case_count") == 0
         and actual.get("all_original_observation_vectors_complete") is False
         and actual.get("all_four_original_targets_restored") is True
         and actual.get("candidate_qualified") is False
         and actual.get("runtime_non_delegation") == "NOT ESTABLISHED"
         and owner_identity_matches(actual.get("receipt_owner"), V12_FAILURE)
         and actual.get("complete_publication_receipt") == failure,
         "bind the complete real V12 loss without opening its forensic archive")
    need(graph.get("rust_v12_original_campaign_failure_receipt_sha256")
         == V12_FAILURE[1]
         and graph.get("rust_v12_original_campaign_infrastructure_failure_count")
         == WORKER_COUNT
         and graph.get("rust_v12_original_campaign_completed_suite_count") == 0
         and graph.get("rust_v12_original_campaign_semantic_mismatch_count")
         == "NOT MEASURED"
         and graph.get("rust_v12_original_campaign_failure_archive_opened_by_graph")
         is False
         and graph.get("rust_v12_original_campaign_failure_archive_inflated_by_graph")
         is False,
         "never hide or reinterpret the real prior infrastructure failures")
    v13_source = graph.get("rust_v13_original_campaign_source_freeze")
    need(isinstance(v13_source, dict)
         and v13_source.get("schema")
         == "rebar-candidate-current-overview-v79-guarded-rust-"
         "original-campaign-v13-source"
         and v13_source.get("status")
         == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
         and v13_source.get("version") == 13
         and v13_source.get("independent_source_owner_count") == 3
         and v13_source.get("previous_failure_receipt_sha256")
         == V12_FAILURE[1],
         "retain the authentic four-transform V13 source feature")
    identities = v13_source.get("owners")
    need(isinstance(identities, dict)
         and all(owner_identity_matches(identities.get(role), owner)
                 for role, owner in zip(("source", "protocol", "contract"),
                                        V13, strict=True)),
         "bind all three exact prior V13 source owners")
    v13_actual = graph.get("actual_rust_v13_original_campaign")
    need(isinstance(v13_actual, dict)
         and v13_actual.get("schema")
         == "rebar-candidate-current-overview-v80-actual-rust-"
         "original-campaign-v13-outcome"
         and v13_actual.get("version") == 13
         and v13_actual.get("candidate_status") == "FAIL"
         and v13_actual.get("publication_status") == "PASS"
         and v13_actual.get("publication_pass_means")
         == "DURABLE PUBLICATION ONLY"
         and v13_actual.get("actual_candidate_worker_count") == WORKER_COUNT
         and v13_actual.get("attempted_suite_count") == WORKER_COUNT
         and v13_actual.get("started_suite_count") == WORKER_COUNT
         and v13_actual.get("completed_suite_count") == 0
         and v13_actual.get("distinct_worker_process_id_count")
         == WORKER_COUNT
         and v13_actual.get("infrastructure_failure_count") == WORKER_COUNT
         and v13_actual.get("semantic_mismatch_count") == "NOT MEASURED"
         and v13_actual.get("verified_passing_case_count") == 0
         and v13_actual.get("all_original_observation_vectors_complete")
         is False
         and v13_actual.get("all_four_original_targets_restored") is True
         and v13_actual.get("candidate_whole_project_qualified") is False
         and v13_actual.get("runtime_non_delegation") == "NOT ESTABLISHED"
         and owner_identity_matches(v13_actual.get("receipt_owner"), V13_FAILURE)
         and v13_actual.get("complete_publication_receipt") == v13_failure,
         "bind the complete actual V13 loss without opening its archive")
    return failure, v13_failure, graph


def history_record(role: str) -> tuple:
    matches = [item for item in HISTORY if item[0] == role]
    need(len(matches) == 1, "reject an unapproved historical helper: " + role)
    return matches[0]


def owner_role(value: object) -> str | None:
    relative = getattr(value, "path", None)
    digest = getattr(value, "sha256", None)
    count = getattr(value, "size", None)
    if isinstance(value, tuple) and len(value) >= 3:
        relative, digest, count = value[:3]
    for role, path, expected, size, _, _ in HISTORY:
        if relative == path:
            need(digest == expected and count == size,
                 "reject substituted historical loader owner: " + role)
            return role
    return None


class RecordingProcess:
    """Proxy one authentic child and retain its first actual pipe bytes."""

    __slots__ = ("_process", "_capture")

    def __init__(self, process: object, capture: dict) -> None:
        self._process = process
        self._capture = capture
        capture["pid"] = getattr(process, "pid", None)
        capture["returncode"] = getattr(process, "returncode", None)

    def __getattr__(self, name: str) -> object:
        return getattr(self._process, name)

    @property
    def pid(self) -> object:
        return getattr(self._process, "pid", None)

    @property
    def returncode(self) -> object:
        return getattr(self._process, "returncode", None)

    def poll(self, *args: object, **kwargs: object) -> object:
        return self._process.poll(*args, **kwargs)

    def kill(self, *args: object, **kwargs: object) -> object:
        return self._process.kill(*args, **kwargs)

    def communicate(self, *args: object, **kwargs: object) -> object:
        self._capture["communicate_calls"] += 1
        try:
            result = self._process.communicate(*args, **kwargs)
        except BaseException as error:
            if self._capture.get("communicate_exception") is None:
                self._capture["communicate_exception"] = {
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                }
            self._capture["returncode"] = getattr(
                self._process, "returncode", None,
            )
            raise
        if self._capture.get("first_communicate_recorded") is not True:
            if isinstance(result, tuple) and len(result) == 2:
                self._capture["stdout"], self._capture["stderr"] = result
            self._capture["first_communicate_recorded"] = True
            self._capture["returncode"] = getattr(
                self._process, "returncode", None,
            )
        return result

    def __enter__(self) -> object:
        enter = getattr(self._process, "__enter__", None)
        if enter is not None:
            enter()
        return self

    def __exit__(self, kind: object, value: object,
                 trace: object) -> object:
        leave = getattr(self._process, "__exit__", None)
        return leave(kind, value, trace) if leave is not None else None


def bounded_diagnostic_stream(legacy: types.ModuleType, raw: object,
                              limit: int, category: str,
                              budget: dict) -> dict:
    if type(raw) is not bytes:
        return {
            "available": False,
            "complete": False,
            "category": category,
            "reason": "WORKER DID NOT RETURN BYTES",
        }
    remaining = max(0, FAILURE_TOTAL_DIAGNOSTIC_BUDGET
                    - budget["captured_bytes"])
    maximum = min(FAILURE_STREAM_LIMIT, limit, remaining)
    prefix = raw[:maximum]
    budget["captured_bytes"] += len(prefix)
    record = legacy.stream_record(prefix, limit)
    record.update({
        "available": True,
        "category": category,
        "complete": len(prefix) == len(raw),
        "truncated": len(prefix) != len(raw),
        "source_size_bytes": len(raw),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "captured_size_bytes": len(prefix),
        "capture_limit_bytes": maximum,
    })
    return record


def bounded_diagnostic_traceback(legacy: types.ModuleType,
                                 budget: dict) -> dict:
    text = legacy.traceback.format_exc()
    need(isinstance(text, str), "require the live original worker traceback")
    raw = text.encode("utf-8", "strict")
    remaining = max(0, FAILURE_TOTAL_DIAGNOSTIC_BUDGET
                    - budget["captured_bytes"])
    maximum = min(FAILURE_TRACEBACK_LIMIT, remaining)
    prefix = raw[:maximum]
    budget["captured_bytes"] += len(prefix)
    return {
        "text": prefix.decode("utf-8", "replace"),
        "complete": len(prefix) == len(raw),
        "truncated": len(prefix) != len(raw),
        "source_size_bytes": len(raw),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "captured_size_bytes": len(prefix),
        "capture_limit_bytes": maximum,
    }


def make_preserving_worker(legacy: types.ModuleType) -> object:
    authentic_execute = legacy.execute_one_worker
    authentic_failed = legacy.failed_worker
    need(callable(authentic_execute) and callable(authentic_failed)
         and callable(legacy.subprocess.Popen)
         and callable(legacy.stream_record),
         "require the real immutable V11 controller and original publisher")
    budget = {"captured_bytes": 0, "attempted_workers": 0}

    def preserve_one(options: object, suite: str, count: int,
                     active: object, ledger: dict,
                     helper: types.ModuleType) -> dict:
        need(getattr(legacy, "_v14_worker_capture_active", False) is False,
             "reject nested or leaked global worker capture")
        original_popen = legacy.subprocess.Popen
        original_failed = legacy.failed_worker
        need(original_failed is authentic_failed and callable(original_popen),
             "reject substituted controller Popen or original failure function")
        capture = {
            "created": 0,
            "communicate_calls": 0,
            "first_communicate_recorded": False,
            "stdout": None,
            "stderr": None,
            "pid": None,
            "returncode": None,
            "communicate_exception": None,
        }

        def recording_popen(*args: object, **kwargs: object) -> object:
            need(capture["created"] == 0,
                 "reject a second candidate process in one original suite")
            process = original_popen(*args, **kwargs)
            capture["created"] += 1
            return RecordingProcess(process, capture)

        def recording_failed(name: str, cases: int, message: str,
                             **kwargs: object) -> dict:
            active_exception = sys.exc_info()[1]
            row = authentic_failed(name, cases, message, **kwargs)
            need(isinstance(row, dict)
                 and row.get("failure_class") == "INFRASTRUCTURE FAILURE"
                 and row.get("fully_observed") is False,
                 "preserve exact original failure classification")
            if capture["created"]:
                process = row.get("process")
                need(isinstance(process, dict)
                     and process.get("pid") == capture["pid"],
                     "preserve the actual failed original child PID")
                process["returncode"] = capture["returncode"]
                process["stdout"] = bounded_diagnostic_stream(
                    legacy, capture["stdout"], legacy.MAX_WORKER_STDOUT_BYTES,
                    "stdout", budget,
                )
                process["stderr"] = bounded_diagnostic_stream(
                    legacy, capture["stderr"], legacy.MAX_WORKER_STDERR_BYTES,
                    "stderr", budget,
                )
            trace = bounded_diagnostic_traceback(legacy, budget)
            row["error_type"] = (type(active_exception).__name__
                                 if active_exception is not None else None)
            row["traceback"] = trace
            row["worker_failure_diagnostics"] = {
                "capture_version": 14,
                "child_created": bool(capture["created"]),
                "first_communicate_recorded":
                capture["first_communicate_recorded"],
                "communicate_calls": capture["communicate_calls"],
                "communicate_exception": capture["communicate_exception"],
                "actual_child_returncode": capture["returncode"],
                "traceback_complete": trace["complete"],
            }
            row["worker_failure_diagnostics_preserved"] = (
                not capture["created"]
                or (capture["first_communicate_recorded"]
                    and process["stdout"]["available"]
                    and process["stderr"]["available"])
            )
            return row

        legacy._v14_worker_capture_active = True
        legacy.subprocess.Popen = recording_popen
        legacy.failed_worker = recording_failed
        try:
            row = authentic_execute(options, suite, count,
                                    active, ledger, helper)
            need(isinstance(row, dict)
                 and row.get("suite") == suite
                 and row.get("case_execution_denominator") == count,
                 "retain the original observer, suite, and full denominator")
            if row.get("actual_worker_started") is True:
                need(capture["created"] == 1
                     and row.get("process", {}).get("pid") == capture["pid"],
                     "retain exactly one original candidate child PID")
            if row.get("failure_class") == "INFRASTRUCTURE FAILURE":
                need(isinstance(row.get("worker_failure_diagnostics"), dict),
                     "never discard the actual child failure streams")
            budget["attempted_workers"] += 1
            need(budget["captured_bytes"]
                 <= FAILURE_TOTAL_DIAGNOSTIC_BUDGET,
                 "never exceed the explicit complete-campaign diagnostic budget")
            return row
        finally:
            legacy.failed_worker = original_failed
            legacy.subprocess.Popen = original_popen
            legacy._v14_worker_capture_active = False
            need(legacy.failed_worker is authentic_failed
                 and legacy.subprocess.Popen is original_popen,
                 "restore exact global Popen and historical failure function")

    preserve_one._v14_capture_budget = budget
    return preserve_one


def install_failure_preservation(legacy: types.ModuleType) -> None:
    original_preserve = legacy.preserve_actual_campaign
    need(callable(original_preserve),
         "retain the authentic first-party streaming evidence publisher")
    legacy.execute_one_worker = make_preserving_worker(legacy)

    def retain_publication(report: dict, helper: types.ModuleType,
                           recovery: types.ModuleType,
                           publication: types.ModuleType,
                           ledger: dict) -> dict:
        rows = report.get("suite_results")
        need(isinstance(rows, list) and len(rows) == WORKER_COUNT,
             "never publish fewer than all original suite rows")
        failed = [row for row in rows
                  if row.get("failure_class") == "INFRASTRUCTURE FAILURE"]
        need(all(isinstance(row.get("worker_failure_diagnostics"), dict)
                 for row in failed),
             "never publish an incomplete or silently discarded child failure")
        summaries = []
        for row in failed:
            process = row.get("process")
            streams = process if isinstance(process, dict) else {}
            summaries.append({
                "suite": row.get("suite"),
                "error_type": row.get("error_type"),
                "error_message": row.get("error_message"),
                "pid": streams.get("pid"),
                "returncode": streams.get("returncode"),
                "stdout_size_bytes": (streams.get("stdout", {}) or {})
                .get("source_size_bytes"),
                "stdout_sha256": (streams.get("stdout", {}) or {})
                .get("source_sha256"),
                "stdout_complete": (streams.get("stdout", {}) or {})
                .get("complete"),
                "stderr_size_bytes": (streams.get("stderr", {}) or {})
                .get("source_size_bytes"),
                "stderr_sha256": (streams.get("stderr", {}) or {})
                .get("source_sha256"),
                "stderr_complete": (streams.get("stderr", {}) or {})
                .get("complete"),
                "traceback_sha256": (row.get("traceback", {}) or {})
                .get("source_sha256"),
                "traceback_complete": (row.get("traceback", {}) or {})
                .get("complete"),
            })
        capture = {
            "schema": SCHEMA + "-complete-bounded-worker-failure-capture",
            "actual_failure_count": len(failed),
            "diagnostic_stream_limit_bytes": FAILURE_STREAM_LIMIT,
            "diagnostic_traceback_limit_bytes": FAILURE_TRACEBACK_LIMIT,
            "total_diagnostic_budget_bytes": FAILURE_TOTAL_DIAGNOSTIC_BUDGET,
            "suite_failure_summaries": summaries,
            "first_worker_failure": summaries[0] if summaries else None,
            "all_failure_metadata_preserved":
            all(row.get("worker_failure_diagnostics_preserved") is True
                for row in failed),
        }
        report["worker_failure_capture"] = capture
        previous_writer = recovery.write_evidence_receipt

        def retaining_receipt(name: str, receipt: dict) -> dict:
            need(isinstance(receipt, dict)
                 and receipt.get("schema")
                 == SCHEMA + "-durable-publication-receipt",
                 "retain the exact original V14 durable result publisher")
            receipt["worker_failure_capture"] = capture
            receipt["worker_failure_capture_count"] = len(failed)
            receipt["worker_failure_capture_complete"] = (
                capture["all_failure_metadata_preserved"]
            )
            return previous_writer(name, receipt)

        recovery.write_evidence_receipt = retaining_receipt
        try:
            result = original_preserve(report, helper, recovery,
                                       publication, ledger)
        finally:
            recovery.write_evidence_receipt = previous_writer
        need(recovery.write_evidence_receipt is previous_writer,
             "restore exact original durable evidence writer")
        result["worker_failure_capture"] = capture
        result["worker_failure_capture_count"] = len(failed)
        result["worker_failure_capture_complete"] = (
            capture["all_failure_metadata_preserved"]
        )
        return result

    legacy.preserve_actual_campaign = retain_publication


def failure_capture_hostile_controls() -> list[str]:
    controls: list[str] = []

    class FakeChild:
        def __init__(self, output: bytes, errors: bytes,
                     code: int) -> None:
            self.pid = 31337
            self.returncode = code
            self._output = output
            self._errors = errors

        def communicate(self, *args: object,
                        **kwargs: object) -> tuple[bytes, bytes]:
            return self._output, self._errors

        def poll(self) -> int:
            return self.returncode

        def kill(self) -> None:
            return None

    scenarios = (
        ("empty-stdout-nonempty-stderr", b"",
         b"guarded child actually failed\\n", 2),
        ("malformed-stdout-nonzero-exit", b"{invalid",
         b"actual Python traceback\\n", 3),
        ("signal-negative-exit", b"", b"terminated\\n", -9),
        ("oversized-stdout-truthfully-truncated",
         b"x" * (FAILURE_STREAM_LIMIT + 17), b"detail\\n", 4),
        ("oversized-stderr-truthfully-truncated", b"",
         b"z" * (FAILURE_STREAM_LIMIT + 23), 5),
    )
    for title, output, errors, code in scenarios:
        fake = types.SimpleNamespace()
        fake.subprocess = types.SimpleNamespace()
        fake.MAX_WORKER_STDOUT_BYTES = 32 * 1024 * 1024
        fake.MAX_WORKER_STDERR_BYTES = 4 * 1024 * 1024
        fake.traceback = types.SimpleNamespace(
            format_exc=lambda: "Traceback (most recent call last):\\n"
            "CampaignError: synthetic recorded worker failure\\n",
        )

        def source_process(*args: object, **kwargs: object) -> FakeChild:
            return FakeChild(output, errors, code)

        def record(raw: bytes, maximum: int) -> dict:
            need(type(raw) is bytes and len(raw) <= maximum,
                 "reject oversized fake stream record")
            return {"base64": "SOURCE-ONLY SYNTHETIC",
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "size_bytes": len(raw), "complete": True,
                    "limit_bytes": maximum}

        def failed(name: str, cases: int, message: str,
                   **kwargs: object) -> dict:
            return {
                "suite": name, "case_execution_denominator": cases,
                "worker_attempted": True, "actual_worker_started": True,
                "fully_observed": False,
                "failure_class": "INFRASTRUCTURE FAILURE",
                "mismatch_count": "NOT MEASURED",
                "verified_passing_case_count": 0,
                "error_message": message,
                "process": {"pid": 31337,
                            "actual_worker_processes": 1},
            }

        def execute(options: object, suite: str, count: int,
                    active: object, ledger: dict,
                    helper: types.ModuleType) -> dict:
            child = None
            try:
                child = fake.subprocess.Popen("synthetic-no-process")
                stdout, stderr = child.communicate(timeout=17)
                need(stdout == b'{"status":"PASS"}',
                     "synthetic strict JSON worker rejected actual stdout")
                return {"suite": suite, "case_execution_denominator": count,
                        "actual_worker_started": True,
                        "fully_observed": True,
                        "failure_class": "PASS",
                        "process": {"pid": child.pid,
                                    "returncode": child.returncode}}
            except BaseException as error:
                return fake.failed_worker(
                    suite, count, type(error).__name__ + ": " + str(error),
                    pid=None if child is None else child.pid,
                    started=child is not None,
                )

        fake.subprocess.Popen = source_process
        fake.stream_record = record
        fake.failed_worker = failed
        fake.execute_one_worker = execute
        authentic_popen = fake.subprocess.Popen
        authentic_failed = fake.failed_worker
        wrapped = make_preserving_worker(fake)
        row = wrapped(None, "original_bounded_v5", 151,
                      None, {}, types.ModuleType("_v14_fake"))
        process = row.get("process")
        need(row.get("failure_class") == "INFRASTRUCTURE FAILURE"
             and row.get("worker_failure_diagnostics_preserved") is True
             and isinstance(process, dict)
             and process.get("pid") == 31337
             and process.get("returncode") == code
             and process.get("stdout", {}).get("source_size_bytes")
             == len(output)
             and process.get("stdout", {}).get("source_sha256")
             == hashlib.sha256(output).hexdigest()
             and process.get("stderr", {}).get("source_size_bytes")
             == len(errors)
             and process.get("stderr", {}).get("source_sha256")
             == hashlib.sha256(errors).hexdigest()
             and isinstance(row.get("traceback"), dict)
             and fake.subprocess.Popen is authentic_popen
             and fake.failed_worker is authentic_failed
             and getattr(fake, "_v14_worker_capture_active", False)
             is False,
             "lose real failure diagnostics or leak global process patch: "
             + title)
        if len(output) > FAILURE_STREAM_LIMIT:
            need(process["stdout"]["complete"] is False
                 and process["stdout"]["truncated"] is True,
                 "misrepresent an oversized complete worker stdout")
        if len(errors) > FAILURE_STREAM_LIMIT:
            need(process["stderr"]["complete"] is False
                 and process["stderr"]["truncated"] is True,
                 "misrepresent an oversized complete worker stderr")
        controls.append("retain-fake-" + title)
    return controls


def source_hostile_controls(guard: types.ModuleType) -> list[str]:
    controls: list[str] = []
    for record in HISTORY:
        role = record[0]
        raw = read_exact(historical_owner(record))
        changed = clean_history(raw, record)
        compile(changed, record[1], "exec", dont_inherit=True)
        need("ctypes" not in sys.modules,
             "source controls must never preload the ctypes native loader")
        controls.append("authenticate-and-compile-only-" + role)
        for description, hostile in (
            ("missing", raw.replace(b"import ctypes\n", b"pass\n", 1)),
            ("aliased", raw.replace(b"import ctypes\n",
                                     b"import ctypes as hidden\n", 1)),
            ("from-import", raw.replace(b"import ctypes\n",
                                         b"from ctypes import CDLL\n", 1)),
            ("duplicate", raw.replace(b"import ctypes\n",
                                       b"import ctypes\nimport ctypes\n", 1)),
        ):
            try:
                clean_history(hostile, record)
            except (CampaignError, SyntaxError, UnicodeError):
                controls.append("reject-" + description + "-" + role)
            else:
                raise CampaignError("accepts hostile historical "
                                    + description + ": " + role)
    isolated: dict = {}
    exec(compile(PROXY_SOURCE, "<v14-fail-closed-ctypes-proxy>",
                 "exec", dont_inherit=True), isolated)
    proxy = isolated["ctypes"]
    for name in ("CDLL", "PyDLL", "_dlopen", "pythonapi",
                 "__dict__", "__class__"):
        try:
            getattr(proxy, name)
        except RuntimeError as error:
            need("V14 forbids every historical ctypes operation" in str(error),
                 "reject a proxy exception bypass")
            controls.append("reject-proxy-" + name)
        else:
            raise CampaignError("historical proxy permits native access: " + name)
    policy = guard.RuntimePolicy()
    need("ctypes.dlopen" in guard.DENIED_EVENTS
         and "ctypes.dlsym" in guard.DENIED_EVENTS,
         "never loosen the inherited physical native-loader audit policy")
    for event in ("ctypes.dlopen", "ctypes.dlsym"):
        try:
            policy.audit(event, ("forbidden-v14",))
        except guard.GuardError as error:
            need(event in str(error), "reject an unrelated native guard denial")
            controls.append("guard-rejects-" + event)
        else:
            raise CampaignError("runtime policy permits " + event)
    for forbidden in ("_sre", "regex", "re._compiler", "re._parser",
                      "candidates.vm_candidate", "candidates.zig_candidate"):
        try:
            policy.check_import(forbidden)
        except guard.GuardError:
            controls.append("guard-rejects-" + forbidden)
        else:
            raise CampaignError("runtime policy permits fallback: " + forbidden)
    need(not policy.installed and "ctypes" not in sys.modules
         and "re" not in sys.modules and "_sre" not in sys.modules,
         "source hostile controls installed a guard or loaded a matcher")
    controls.extend(failure_capture_hostile_controls())
    return controls


def verify_frozen_context(source_sha: str, protocol_sha: str,
                          contract_sha: str | None,
                          *, rendering: bool = False) -> tuple[dict, types.ModuleType,
                                                               types.ModuleType]:
    assert_sterile()
    source_raw = read_exact(live_self(SOURCE, source_sha))
    read_exact(live_self(PROTOCOL, protocol_sha))
    if not rendering:
        need(contract_sha is not None, "pin the exact V14 machine contract")
        read_exact(live_self(CONTRACT, contract_sha))
    base = load_v12()
    previous = base.verify_frozen_context(V12[0][1], V12[1][1], V12[2][1])
    guard = base.load_guard()
    need(previous.get("status") == "PASS"
         and previous.get("phase1_v4_reference_readiness") == "PASS"
         and previous.get("phase2_candidate_qualification") == "BLOCKED"
         and previous.get("corrected_original_producer_version") == 5
         and previous.get("suite_count") == WORKER_COUNT
         and previous.get("case_execution_denominator") == CASE_COUNT
         and previous.get("supplemental_case_count") == 8244
         and previous.get("supplemental_cases_counted_in_original_denominator")
         is False,
         "require the full authenticated V12 and guard-clean V5 original oracle")
    for record in HISTORY:
        clean_history(read_exact(historical_owner(record)), record)
    failure, v13_failure, graph = failure_and_graph(guard, base)
    source_tree = ast.parse(source_raw, filename=SOURCE)
    routes = {node.name for node in source_tree.body
              if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    need({"clean_history", "source_hostile_controls", "bind_v14_legacy",
          "v14_worker_arguments", "actual_operation", "verify_frozen_context",
          "make_preserving_worker", "install_failure_preservation",
          "failure_capture_hostile_controls"}
         <= routes,
         "require all four actual guarded helpers and complete V14 dispatch")
    result = {
        "schema": SCHEMA + "-frozen-context",
        "status": "PASS",
        "version": 14,
        "source_sha256": source_sha,
        "protocol_sha256": protocol_sha,
        "contract_sha256": contract_sha,
        "goal_sha256": previous["goal_sha256"],
        "cpython_version": "3.14.6",
        "cpython_executable": PYTHON,
        "cpython_executable_sha256": base.PYTHON_SHA256,
        "phase1_v4_reference_readiness": "PASS",
        "phase2_candidate_qualification": "BLOCKED",
        "qualified_candidate_count": 0,
        "corrected_original_producer_version": 5,
        "corrected_original_producer_source_sha256": base.PRODUCER[0][1],
        "corrected_original_producer_protocol_sha256": base.PRODUCER[1][1],
        "corrected_original_producer_contract_sha256": base.PRODUCER[2][1],
        "historical_original_v4_producer_source_sha256": history_record("v4")[2],
        "suite_count": WORKER_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "named_private_waivers": list(base.PRIVATE_WAIVERS),
        "supplemental_case_count": 8244,
        "supplemental_cases_counted_in_original_denominator": False,
        "suites": [{"id": name, "case_execution_count": count}
                   for name, count in SUITES],
        "reference_records_sha256": base.REFERENCE_SHA,
        "reference_cache_records_sha256": base.REFERENCE_CACHE_SHA,
        "reference_worker_process_ids": [81, 82],
        "frozen_worker_implementation_source": history_record("v11")[1],
        "frozen_worker_implementation_source_sha256": history_record("v11")[2],
        "historical_ctypes_source_count": len(HISTORY),
        "historical_ctypes_sources": [
            {"role": role, "path": path, "sha256": digest,
             "bytes": count, "inode": inode,
             "exact_top_level_import_line": line,
             "transformation":
             "AUTHENTICATE RAW; REPLACE ONLY TOP-LEVEL IMPORT WITH "
             "A FAIL-CLOSED MODULE-LOCAL PROXY"}
            for role, path, digest, count, inode, line in HISTORY
        ],
        "historical_ctypes_proxy_native_load_permitted": False,
        "historical_ctypes_preloaded": False,
        "historical_ctypes_transforms_executed": 0,
        "previous_v13_source_sha256": V13[0][1],
        "previous_v13_protocol_sha256": V13[1][1],
        "previous_v13_contract_sha256": V13[2][1],
        "v13_actual_failure_receipt_sha256": V13_FAILURE[1],
        "v13_actual_failure_receipt_bytes": V13_FAILURE[2],
        "v13_actual_failure_receipt_inode": V13_FAILURE[3],
        "v13_actual_candidate_worker_count": WORKER_COUNT,
        "v13_actual_completed_suite_count": 0,
        "v13_actual_infrastructure_failure_count": WORKER_COUNT,
        "v13_actual_semantic_mismatch_count": "NOT MEASURED",
        "v13_actual_verified_passing_case_count": 0,
        "v13_actual_candidate_qualified": False,
        "v13_actual_all_four_original_targets_restored": True,
        "v13_failure_archive_opened": False,
        "v13_failure_archive_inflated": False,
        "worker_failure_capture_mode":
        "SCOPED AUTHENTIC CONTROLLER; COMPLETE BOUNDED STDOUT, STDERR, "
        "EXIT AND ACTIVE TRACEBACK",
        "worker_failure_capture_stream_limit_bytes": FAILURE_STREAM_LIMIT,
        "worker_failure_capture_traceback_limit_bytes": FAILURE_TRACEBACK_LIMIT,
        "worker_failure_capture_total_budget_bytes":
        FAILURE_TOTAL_DIAGNOSTIC_BUDGET,
        "worker_failure_capture_attempts": 0,
        "worker_failure_capture_complete": "NOT RUN",
        "worker_failure_capture_processes_started": 0,
        "worker_failure_capture_native_loads": 0,
        "v12_source_sha256": V12[0][1],
        "v12_protocol_sha256": V12[1][1],
        "v12_contract_sha256": V12[2][1],
        "v12_actual_failure_receipt_sha256": V12_FAILURE[1],
        "v12_actual_failure_receipt_bytes": V12_FAILURE[2],
        "v12_actual_failure_receipt_inode": V12_FAILURE[3],
        "v12_actual_candidate_worker_count": WORKER_COUNT,
        "v12_actual_completed_suite_count": 0,
        "v12_actual_infrastructure_failure_count": WORKER_COUNT,
        "v12_actual_semantic_mismatch_count": "NOT MEASURED",
        "v12_actual_verified_passing_case_count": 0,
        "v12_actual_candidate_qualified": False,
        "v12_actual_all_four_original_targets_restored": True,
        "v12_failure_archive_opened": False,
        "v12_failure_archive_inflated": False,
        "actual_controller_dispatch": "AUTHENTICATED V11 run_campaign",
        "actual_worker_dispatch": "AUTHENTICATED V11 run_original_worker",
        "actual_recovery_dispatch": "AUTHENTICATED V11 recover_originals",
        "actual_worker_bootstrap":
        "CPython -I -B -S; audit hook before candidate import",
        "planned_actual_original_candidate_worker_count": WORKER_COUNT,
        "actual_candidate_workers_started": 0,
        "actual_candidate_imports": 0,
        "actual_native_libraries_loaded": 0,
        "actual_compiler_processes_started": 0,
        "actual_private_build_root_opens": 0,
        "actual_private_build_root_stats": 0,
        "actual_build_archive_opens": 0,
        "actual_build_archive_inflations": 0,
        "actual_hidden_cases_read": 0,
        "actual_clock_samples": 0,
        "runtime_guard_source_sha256": base.GUARD[0][1],
        "runtime_guard_protocol_sha256": base.GUARD[1][1],
        "runtime_guard_contract_sha256": base.GUARD[2][1],
        "runtime_guard_installation":
        "REQUIRED BEFORE ANY ACTUAL CANDIDATE IMPORT",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "actual_v19_build_source_sha256": base.BUILD[0][1],
        "actual_v19_build_protocol_sha256": base.BUILD[1][1],
        "actual_v19_build_contract_sha256": base.BUILD[2][1],
        "actual_v19_build_receipt_sha256": base.BUILD_RECEIPT[1],
        "actual_v19_root_receipt_sha256": base.ROOT_RECEIPT[1],
        "actual_v19_build_archive_metadata_sha256": base.BUILD_ARCHIVE_SHA,
        "actual_v19_build_archive_metadata_bytes": base.BUILD_ARCHIVE_BYTES,
        "actual_v19_build_label": base.BUILD_LABEL,
        "actual_v19_compiler_process_count": 28,
        "actual_v19_source_build_phase_count": 2,
        "actual_v19_private_build_root_provenance":
        "AUTHENTICATED RECEIPT ONLY; NOT OPENED",
        "actual_v19_private_build_root": base.ROOT_PATH,
        "actual_v19_private_build_root_device": base.ROOT_DEVICE,
        "actual_v19_private_build_root_inode": base.ROOT_INODE,
        "actual_v19_native_engine_sha256": base.ENGINE_SHA,
        "actual_v19_native_engine_bytes": base.ENGINE_BYTES,
        "actual_v19_native_bridge_sha256": base.BRIDGE_SHA,
        "actual_v19_native_bridge_bytes": base.BRIDGE_BYTES,
        "recovery_role_order": list(base.ROLE_ORDER),
        "recovery_restoration_order": list(reversed(base.ROLE_ORDER)),
        "public_recovery_root": RECOVERY_ROOT,
        "recovery_lock_filename": "recoverable-controller-v14.lock",
        "frozen_graph_version": 80,
        "frozen_graph_source_sha256": GRAPH[0][1],
        "frozen_graph_inputs_sha256": GRAPH[1][1],
        "frozen_graph_summary_sha256": GRAPH[2][1],
        "frozen_graph_svg_sha256": GRAPH[3][1],
        "current_evidence_owner_lower_bound": CURRENT_EVIDENCE_FLOOR,
        "current_history_reference_lower_bound": CURRENT_HISTORY_FLOOR,
        "prospective_evidence_owner_lower_bound": CURRENT_EVIDENCE_FLOOR + 3,
        "prospective_history_reference_lower_bound": CURRENT_HISTORY_FLOOR + 3,
        "historical_rust_semantic_mismatch_count": 1440,
        "historical_rust_verified_passing_case_count": 14853,
        "actual_c_semantic_mismatch_count": 1230,
        "actual_c_verified_passing_case_count": 7325,
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "timing_trials_run": 0,
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }
    need(graph.get("actual_rust_semantic_mismatch_count")
         == result["historical_rust_semantic_mismatch_count"]
         and graph.get("actual_rust_verified_passing_case_count")
         == result["historical_rust_verified_passing_case_count"]
         and sum(value for _, value in SUITES) == CASE_COUNT
         and len(SUITES) == WORKER_COUNT
         and failure.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT,
         "retain historical measured losses and the entire original denominator")
    if not rendering:
        assert contract_sha is not None
        machine = base.parse_document(
            guard, read_exact(live_self(CONTRACT, contract_sha)),
            "V14 frozen machine contract",
        )
        need(machine == contract_document(result),
             "reject an altered or incomplete V14 machine contract")
    assert_sterile()
    return result, base, guard


def contract_document(context: dict) -> dict:
    result = dict(context)
    result["schema"] = SCHEMA + "-recoverable-source-freeze"
    result["status"] = "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
    result.pop("contract_sha256", None)
    return result


def parse_cli(arguments: list[str]) -> dict:
    modes = ("--self-test", "--verify-frozen-context", "--render-contract",
             "--run", "--worker", "--recover")
    selected = [part for part in arguments if part in modes]
    need(len(selected) == 1, "select exactly one V14 operation")
    options: dict[str, object] = {"mode": selected[0]}
    cursor = 0
    while cursor < len(arguments):
        item = arguments[cursor]
        if item in modes:
            cursor += 1
            continue
        need(item.startswith("--") and cursor + 1 < len(arguments),
             "reject missing V14 authority")
        name = item[2:].replace("-", "_")
        need(name not in options, "reject repeated V14 authority: " + item)
        options[name] = arguments[cursor + 1]
        cursor += 2
    exact_digest(options.get("source_sha256"), "V14 source")
    exact_digest(options.get("protocol_sha256"), "V14 protocol")
    if options["mode"] == "--render-contract":
        need("contract_sha256" not in options,
             "contract rendering cannot pin its own missing output")
    else:
        exact_digest(options.get("contract_sha256"), "V14 contract")
    source_keys = {"mode", "source_sha256", "protocol_sha256",
                   "contract_sha256"}
    if options["mode"] in ("--self-test", "--verify-frozen-context",
                            "--render-contract"):
        need(set(options) <= source_keys,
             "source verification cannot authorize an actual candidate")
    return options


def actual_required_authority(base: types.ModuleType) -> dict[str, str]:
    return {
        "family": "rust",
        "label": LABEL,
        "activation_root": RECOVERY_ROOT,
        "build_private_root": base.ROOT_PATH,
        "build_private_root_device": str(base.ROOT_DEVICE),
        "build_private_root_inode": str(base.ROOT_INODE),
        "producer_source_sha256": base.PRODUCER[0][1],
        "producer_protocol_sha256": base.PRODUCER[1][1],
        "producer_contract_sha256": base.PRODUCER[2][1],
        "phase1_v4_source_sha256": base.P0[0][1],
        "phase1_v4_protocol_sha256": base.P0[1][1],
        "phase1_v4_contract_sha256": base.P0[2][1],
        "build_source_sha256": base.BUILD[0][1],
        "build_protocol_sha256": base.BUILD[1][1],
        "build_contract_sha256": base.BUILD[2][1],
        "build_archive_sha256": base.BUILD_ARCHIVE_SHA,
        "build_receipt_sha256": base.BUILD_RECEIPT[1],
        "root_receipt_sha256": base.ROOT_RECEIPT[1],
        "native_engine_sha256": base.ENGINE_SHA,
        "native_engine_bytes": str(base.ENGINE_BYTES),
        "native_bridge_sha256": base.BRIDGE_SHA,
        "native_bridge_bytes": str(base.BRIDGE_BYTES),
        "runtime_guard_source_sha256": base.GUARD[0][1],
        "runtime_guard_protocol_sha256": base.GUARD[1][1],
        "runtime_guard_contract_sha256": base.GUARD[2][1],
        "previous_failure_receipt_sha256": V13_FAILURE[1],
        "historical_v12_failure_receipt_sha256": V12_FAILURE[1],
        "current_graph_source_sha256": GRAPH[0][1],
        "current_graph_inputs_sha256": GRAPH[1][1],
        "current_graph_summary_sha256": GRAPH[2][1],
        "current_graph_svg_sha256": GRAPH[3][1],
    }


def actual_namespace(options: dict, base: types.ModuleType
                     ) -> types.SimpleNamespace:
    required = actual_required_authority(base)
    for name, expected in required.items():
        need(options.get(name) == expected,
             "require separately pinned actual V14 authority: " + name)
    permitted = {"mode", "source_sha256", "protocol_sha256",
                 "contract_sha256", *required}
    if options["mode"] == "--worker":
        need(options.get("suite") in dict(SUITES),
             "pin one complete original V14 suite")
        permitted.add("suite")
        for name in ("activation_report_sha256", "activation_receipt_sha256",
                     "recovery_journal_sha256"):
            exact_digest(options.get(name), name)
            permitted.add(name)
    elif options["mode"] == "--recover":
        exact_digest(options.get("recovery_journal_sha256"),
                     "V14 recovery journal")
        permitted.add("recovery_journal_sha256")
    else:
        need(options["mode"] == "--run", "reject invented V14 operation")
    need(set(options) <= permitted,
         "reject extra authority, hidden benchmark, or candidate fallback")
    result = dict(options)
    for key in ("build_private_root_device", "build_private_root_inode",
                "native_engine_bytes", "native_bridge_bytes"):
        result[key] = int(result[key])
    for key in ("suite", "activation_report_sha256",
                "activation_receipt_sha256", "recovery_journal_sha256",
                "inspection_report_sha256", "inspection_receipt_sha256"):
        result.setdefault(key, None)
    return types.SimpleNamespace(**result)


def v14_worker_arguments(namespace: types.SimpleNamespace, suite: str,
                         active: dict, base: types.ModuleType) -> list[str]:
    need(suite in dict(SUITES), "spawn only an original guarded V14 suite")
    arguments = [PYTHON, "-I", "-B", "-S", os.path.join(ROOT, SOURCE),
                 "--worker", "--source-sha256", namespace.source_sha256,
                 "--protocol-sha256", namespace.protocol_sha256,
                 "--contract-sha256", namespace.contract_sha256,
                 "--suite", suite]
    for key, value in actual_required_authority(base).items():
        arguments.extend(("--" + key.replace("_", "-"), value))
    for key, source in (("activation_report_sha256", "activation_owner"),
                        ("activation_receipt_sha256", "receipt_owner"),
                        ("recovery_journal_sha256", "journal_owner")):
        owner = active.get(source)
        need(isinstance(owner, dict),
             "require actual authenticated V14 activation: " + source)
        arguments.extend(("--" + key.replace("_", "-"),
                          exact_digest(owner.get("sha256"), key)))
    return arguments


def guarded_historical_module(legacy: types.ModuleType, owner: object,
                              name: str, loader: object,
                              route_counts: dict[str, int]
                              ) -> types.ModuleType:
    role = owner_role(owner)
    if role != "v7":
        return loader(owner, name)
    need(name == "_rebar_v14_frozen_reviewed_rust_v7",
         "reject an unapproved historical V7 module identity")
    previous = legacy.read_owner

    def cleaned_read(item: object, *args: object, **kwargs: object) -> tuple:
        answer = previous(item, *args, **kwargs)
        if owner_role(item) == "v7":
            route_counts["v7"] += 1
            return clean_history(answer[0], history_record("v7")), answer[1]
        return answer

    legacy.read_owner = cleaned_read
    try:
        module = loader(owner, name)
    finally:
        legacy.read_owner = previous
    patch_v7_loader(module, route_counts)
    return module


def patch_v7_loader(module: types.ModuleType,
                    route_counts: dict[str, int]) -> None:
    original_loader = module.load_frozen_module

    def cleaned_loader(owner: object, name: str) -> types.ModuleType:
        if owner_role(owner) != "v2":
            return original_loader(owner, name)
        need(name == "_rebar_frozen_rust_v2_helpers_for_actual_v7",
             "reject an unapproved V2 recovery helper identity")
        previous = module.read_owned

        def cleaned_read(item: object, *args: object,
                         **kwargs: object) -> tuple:
            answer = previous(item, *args, **kwargs)
            if owner_role(item) == "v2":
                route_counts["v2"] += 1
                return clean_history(answer[0], history_record("v2")), answer[1]
            return answer

        module.read_owned = cleaned_read
        try:
            return original_loader(owner, name)
        finally:
            module.read_owned = previous

    module.load_frozen_module = cleaned_loader


def patch_v5_loader(module: types.ModuleType,
                    route_counts: dict[str, int]) -> None:
    original_loader = module.load_module

    def cleaned_loader(owner: tuple, name: str) -> types.ModuleType:
        if owner_role(owner) != "v4":
            return original_loader(owner, name)
        need(isinstance(name, str)
             and (name.startswith("_rebar_v5_legacy_producer_rust_")
                  or name == "_rebar_v5_guarded_nested_legacy_rust"),
             "reject an unapproved historical V4 observer identity")
        previous = module.read_owner

        def cleaned_read(item: tuple, *args: object,
                         **kwargs: object) -> bytes:
            answer = previous(item, *args, **kwargs)
            if owner_role(item) == "v4":
                route_counts["v4"] += 1
                return clean_history(answer, history_record("v4"))
            return answer

        module.read_owner = cleaned_read
        try:
            return original_loader(owner, name)
        finally:
            module.read_owner = previous

    module.load_module = cleaned_loader


def bind_v14_legacy(context: dict, guard: types.ModuleType,
                    base: types.ModuleType, bundle: dict | None,
                    route_counts: dict[str, int]) -> types.ModuleType:
    record = history_record("v11")
    raw = read_exact(historical_owner(record))
    if bundle is not None:
        need(bundle["policy"].installed
             and sys.modules.get("re") is bundle["candidate"]
             and "ctypes" not in sys.modules and "_sre" not in sys.modules,
             "require installed physical isolation before historical surgery")
        raw = clean_history(raw, record)
        route_counts["v11"] += 1
    original = raw.decode("utf-8", "strict")
    original = original.replace(
        "phase2-v18-rust-buffer-shape-pickle-original-p0-v11", LABEL,
    ).replace(
        "phase2-v18-rust-buffer-shape-pickle-original-p0",
        "phase2-v19-rust-buffer-shape-root-provenance-original-p0",
    ).replace(
        "phase2-v18-rust-buffer-shape-pickle-lifetime", base.BUILD_LABEL,
    ).replace(
        "rebar-owned-six-family-original-p0-producer-v4",
        "rebar-owned-six-family-original-p0-producer-v5",
    ).replace(
        "frozen_original_six_family_v4", "frozen_original_six_family_v5",
    ).replace(
        '"original_v4_producer_version": 4',
        '"original_v5_producer_version": 5',
    ).replace(
        "original_v4_producer_", "original_v5_producer_",
    ).replace(
        '"original_observer_version": 4',
        '"original_observer_version": 5',
    ).replace(
        'observed.get("original_observer_version") == 4',
        'observed.get("original_observer_version") == 5',
    )
    for before, after in (("v11", "v14"), ("V11", "V14"),
                          ("v18", "v19"), ("V18", "V19"),
                          ("v69", "v80"), ("V69", "V80")):
        original = original.replace(before, after)
    legacy = types.ModuleType("_rebar_v14_authenticated_v11_original_campaign")
    legacy.__file__ = os.path.join(ROOT, record[1])
    exec(compile(original, legacy.__file__, "exec", dont_inherit=True),
         legacy.__dict__)
    need(tuple(legacy.ROLE_ORDER) == tuple(base.ROLE_ORDER)
         and tuple(legacy.RESTORATION_ORDER)
         == tuple(reversed(base.ROLE_ORDER))
         and tuple(legacy.SUITES) == SUITES
         and legacy.SUITE_COUNT == WORKER_COUNT
         and legacy.CASE_COUNT == CASE_COUNT
         and legacy.PRIVATE_WAIVER_COUNT == PRIVATE_WAIVER_COUNT
         and callable(legacy.run_original_worker)
         and callable(legacy.run_campaign)
         and callable(legacy.recover_originals),
         "retain all authenticated historical controller and recovery functions")

    def named(owner: tuple) -> object:
        return legacy.Owner(owner[0], owner[1], owner[2], 2064, owner[3])

    build_receipt, root_receipt = base.authenticate_root_receipts(guard)
    publication = build_receipt.get("archive_publication")
    need(isinstance(publication, dict)
         and publication.get("sha256") == base.BUILD_ARCHIVE_SHA
         and publication.get("bytes") == base.BUILD_ARCHIVE_BYTES
         and publication.get("device") == 2064
         and publication.get("inode") == base.BUILD_ARCHIVE_INODE
         and build_receipt.get("uncompressed_sha256") == base.BUILD_PLAIN_SHA
         and build_receipt.get("uncompressed_bytes") == base.BUILD_PLAIN_BYTES,
         "authenticate V19 archive metadata without opening an archive")
    legacy.SOURCE_PATH = SOURCE
    legacy.PROTOCOL_PATH = PROTOCOL
    legacy.CONTRACT_PATH = CONTRACT
    legacy.SCHEMA = SCHEMA
    legacy.CONTRACT_SCHEMA = SCHEMA + "-recoverable-source-freeze"
    legacy.WORKER_SCHEMA = SCHEMA + "-actual-original-suite-worker"
    legacy.CAMPAIGN_SCHEMA = SCHEMA + "-complete-original-campaign"
    legacy.RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
    legacy.LABEL = LABEL
    legacy.BUILD_LABEL = base.BUILD_LABEL
    legacy.PUBLIC_RECOVERY_PRIVATE_PREFIX = RECOVERY_PREFIX
    legacy.PUBLIC_RECOVERY_ROOT = RECOVERY_ROOT
    legacy.LOCK_NAME = "recoverable-controller-v14.lock"
    legacy.BUILD = tuple(named(owner) for owner in base.BUILD)
    legacy.BUILD_RECEIPT = named(base.BUILD_RECEIPT)
    legacy.BUILD_ARCHIVE = legacy.Owner(
        build_receipt["archive_relative"], base.BUILD_ARCHIVE_SHA,
        base.BUILD_ARCHIVE_BYTES, 2064, base.BUILD_ARCHIVE_INODE,
    )
    legacy.BUILD_PLAIN_SHA256 = base.BUILD_PLAIN_SHA
    legacy.BUILD_PLAIN_BYTES = base.BUILD_PLAIN_BYTES
    legacy.GRAPH = tuple(named(owner) for owner in GRAPH)
    legacy.CURRENT_GRAPH_VERSION = 80
    legacy.CURRENT_GRAPH_EVIDENCE_OWNER_LOWER_BOUND = CURRENT_EVIDENCE_FLOOR
    legacy.CURRENT_GRAPH_HISTORY_REFERENCE_LOWER_BOUND = CURRENT_HISTORY_FLOOR
    legacy.CURRENT_EVIDENCE_OWNER_LOWER_BOUND = CURRENT_EVIDENCE_FLOOR + 3
    legacy.CURRENT_HISTORY_REFERENCE_LOWER_BOUND = CURRENT_HISTORY_FLOOR + 3
    legacy.VERIFIED_BUILD_PRIVATE_ROOT = base.ROOT_PATH
    legacy.VERIFIED_BUILD_PRIVATE_ROOT_DEVICE = base.ROOT_DEVICE
    legacy.VERIFIED_BUILD_PRIVATE_ROOT_INODE = base.ROOT_INODE
    legacy.VERIFIED_NATIVE_ENGINE_SHA256 = base.ENGINE_SHA
    legacy.VERIFIED_NATIVE_ENGINE_BYTES = base.ENGINE_BYTES
    legacy.VERIFIED_NATIVE_BRIDGE_SHA256 = base.BRIDGE_SHA
    legacy.VERIFIED_NATIVE_BRIDGE_BYTES = base.BRIDGE_BYTES
    legacy.PRODUCER = tuple(named(owner) for owner in base.PRODUCER)
    legacy.PHASE_ONE_V4 = tuple(named(owner) for owner in base.P0)
    authenticated_loader = legacy.load_frozen_module

    def corrected_family(module: types.ModuleType,
                         producer: types.ModuleType) -> object:
        need(type(producer) is types.ModuleType
             and getattr(producer, "SCHEMA", None)
             == "rebar-owned-six-family-original-p0-producer-v5"
             and getattr(producer, "SUITE_COUNT", None) == WORKER_COUNT
             and getattr(producer, "CASE_DENOMINATOR", None) == CASE_COUNT
             and getattr(producer, "PRIVATE_WAIVER_COUNT", None)
             == PRIVATE_WAIVER_COUNT,
             "bind only the actual complete guard-clean V5 observer")
        original_family = producer.family_spec("rust")
        unchanged = tuple(module.ORIGINAL_SOURCE_OWNERS)
        need(tuple(original_family.source_owners) == unchanged
             and tuple(producer.OWNED_SOURCES["rust"]) == unchanged
             and original_family.name == "rust"
             and original_family.module == "candidates.rust_candidate"
             and original_family.adapter_relative == "candidates/rust_candidate.py"
             and original_family.bridge_module == "candidates._rust_bridge"
             and original_family.engine_relative == "candidates/_rust_engine.so"
             and original_family.bridge_relative
             == "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so"
             and original_family.combined_native is False
             and original_family.owned_ctypes is False,
             "reject replacement, wrapper, fallback, or cross-family engine")
        sources = tuple(legacy.corrected_source_tuples())
        need(sources == tuple(module.CORRECTED_SOURCE_OWNERS)
             and sources[0] == ("candidates/rust_candidate.py",
                                base.CORRECTED_ADAPTER_SHA,
                                base.CORRECTED_ADAPTER_BYTES),
             "bind only the receipt-authenticated corrected Rust source closure")
        corrected = producer.FamilySpec(
            original_family.name, original_family.module,
            original_family.adapter_relative, original_family.bridge_module,
            original_family.engine_relative, original_family.bridge_relative,
            sources, original_family.combined_native,
            original_family.owned_ctypes,
        )
        producer.OWNED_SOURCES["rust"] = sources
        producer.FAMILIES["rust"] = corrected
        need(producer.family_spec("rust") is corrected,
             "reject substituted actual first-party Rust engine")
        return corrected

    def frozen_loader(owner: object, name: str) -> types.ModuleType:
        if bundle is None:
            module = authenticated_loader(owner, name)
        else:
            module = guarded_historical_module(
                legacy, owner, name, authenticated_loader, route_counts,
            )
        if name == "_rebar_v14_frozen_reviewed_rust_v7":
            need(getattr(module, "SCHEMA", None)
                 == "rebar-owned-repaired-rust-original-campaign-v7"
                 and isinstance(getattr(module, "PRODUCER", None), dict),
                 "load only authenticated historical four-role recovery")
            module.PRODUCER = {
                **module.PRODUCER,
                "source": (base.PRODUCER[0][0], base.PRODUCER[0][1],
                           base.PRODUCER[0][2]),
                "protocol": (base.PRODUCER[1][0], base.PRODUCER[1][1],
                             base.PRODUCER[1][2]),
                "contract": (base.PRODUCER[2][0], base.PRODUCER[2][1],
                             base.PRODUCER[2][2]),
            }

            def family(producer: types.ModuleType) -> object:
                return corrected_family(module, producer)

            module.corrected_rust_family = family
        if bundle is not None and owner_role(owner) is None:
            if getattr(module, "SCHEMA", None) == base.PRODUCER[0][0]:
                raise CampaignError("reject mislabeled V5 producer")
        if (bundle is not None
                and getattr(module, "SCHEMA", None)
                == "rebar-owned-six-family-original-p0-producer-v5"):
            need(getattr(owner, "path", None) == base.PRODUCER[0][0]
                 and getattr(owner, "sha256", None) == base.PRODUCER[0][1],
                 "patch only the authenticated complete V5 producer")
            patch_v5_loader(module, route_counts)
        return module

    legacy.load_frozen_module = frozen_loader

    def verified_context(source_sha: str, protocol_sha: str,
                         contract_sha: str) -> dict:
        need((source_sha, protocol_sha, contract_sha)
             == (context["source_sha256"], context["protocol_sha256"],
                 context["contract_sha256"]),
             "reject a changed V14 controller or genuine original worker")
        return {**context, "build_receipt": dict(build_receipt)}

    def validated_receipt(value: dict) -> None:
        need(isinstance(value, dict) and value == build_receipt,
             "require the genuine V19 build receipt, never an earlier build")

    def private_report(namespace: types.SimpleNamespace,
                       ledger: dict) -> dict:
        return base.derive_v19_private_report(legacy, root_receipt,
                                               namespace, ledger)

    def worker_arguments(namespace: types.SimpleNamespace, suite: str,
                         active: dict) -> list[str]:
        return v14_worker_arguments(namespace, suite, active, base)

    legacy.verify_frozen_context = verified_context
    legacy.validate_build_receipt = validated_receipt
    legacy.read_inspected_build_report = private_report
    legacy.worker_arguments = worker_arguments
    if bundle is None:
        install_failure_preservation(legacy)
    if bundle is not None:
        legacy.ACTUAL_V14_RUNTIME_POLICY = bundle["policy"]
        legacy.ACTUAL_V14_RUNTIME_GUARD = guard
        legacy.ACTUAL_V14_RUNTIME_NATIVE_OWNERS = {
            "bridge": bundle["bridge"], "engine": bundle["engine"],
        }
    need(legacy.SOURCE_PATH == SOURCE
         and legacy.PUBLIC_RECOVERY_ROOT == RECOVERY_ROOT
         and legacy.BUILD[0].sha256 == base.BUILD[0][1]
         and legacy.BUILD_RECEIPT.sha256 == base.BUILD_RECEIPT[1]
         and legacy.BUILD_ARCHIVE.sha256 == base.BUILD_ARCHIVE_SHA
         and legacy.GRAPH[2].sha256 == GRAPH[2][1]
         and legacy.CURRENT_GRAPH_VERSION == 80,
         "reject stale controller, graph, V19 source, or recovery root")
    return legacy


def actual_operation(options: dict, context: dict, base: types.ModuleType,
                     guard: types.ModuleType) -> dict:
    namespace = actual_namespace(options, base)
    counts = {"v11": 0, "v7": 0, "v2": 0, "v4": 0}
    bundle = (base.install_worker_guard(guard)
              if options["mode"] == "--worker" else None)
    legacy = bind_v14_legacy(context, guard, base, bundle, counts)
    if options["mode"] == "--worker":
        need(bundle is not None and bundle["policy"].installed
             and sys.modules.get("re") is bundle["candidate"]
             and "_sre" not in sys.modules and "ctypes" not in sys.modules,
             "require actual V2 guard and exact owned candidate before matching")
        result = legacy.run_original_worker(namespace)
        expected_v4 = 0 if namespace.suite == "original_bounded_v5" else 1
        need(counts == {"v11": 1, "v7": 1, "v2": 1,
                        "v4": expected_v4},
             "execute exactly the narrow authenticated historical helper paths")
        need(isinstance(result, dict)
             and result.get("schema") == legacy.WORKER_SCHEMA
             and result.get("suite") == namespace.suite
             and result.get("case_execution_denominator")
             == dict(SUITES)[namespace.suite]
             and result.get("actual_candidate_workers") == 1
             and "ctypes" not in sys.modules and "_sre" not in sys.modules,
             "retain one complete guarded first-party original suite")
        bundle["policy"].check_modules()
        result["runtime_guard_source_sha256"] = base.GUARD[0][1]
        result["runtime_guard_protocol_sha256"] = base.GUARD[1][1]
        result["runtime_guard_contract_sha256"] = base.GUARD[2][1]
        result["runtime_guard_installed_before_candidate_import"] = True
        result["historical_ctypes_module_imported"] = False
        result["historical_ctypes_guarded_transform_counts"] = dict(counts)
        return result
    if options["mode"] == "--recover":
        result = legacy.recover_originals(namespace)
        need(isinstance(result, dict) and result.get("status") == "PASS"
             and result.get("activation_root") == RECOVERY_ROOT
             and result.get("candidate_workers_started") == 0,
             "restore only the exact original four journaled inodes")
        return result
    ledger = legacy.new_actual_ledger(namespace)
    result = legacy.run_campaign(namespace, ledger)
    need(isinstance(result, dict)
         and result.get("suite_count") == WORKER_COUNT
         and result.get("case_execution_denominator") == CASE_COUNT
         and result.get("current_overview_version") == 80
         and result.get("actual_v19_build_receipt_sha256")
         == base.BUILD_RECEIPT[1]
         and result.get("all_four_original_targets_restored") is True
         and result.get("candidate_qualified")
         is (result.get("semantic_mismatch_count") == 0
             and result.get("infrastructure_failure_count") == 0
             and result.get("actual_candidate_workers") == WORKER_COUNT),
         "preserve the genuine complete candidate result and exact recovery")
    return result


def main(arguments: list[str] | None = None) -> int:
    try:
        options = parse_cli(list(sys.argv[1:] if arguments is None else arguments))
        mode = options["mode"]
        context, base, guard = verify_frozen_context(
            options["source_sha256"], options["protocol_sha256"],
            options.get("contract_sha256"),
            rendering=mode == "--render-contract",
        )
        if mode == "--render-contract":
            result = contract_document(context)
        elif mode == "--self-test":
            result = dict(context)
            result["schema"] = SCHEMA + "-source-self-test"
            result["hostile_controls"] = source_hostile_controls(guard)
            result["hostile_control_count"] = len(result["hostile_controls"])
        elif mode == "--verify-frozen-context":
            result = context
        else:
            result = actual_operation(options, context, base, guard)
        sys.stdout.buffer.write(guard.canonical(result))
        sys.stdout.buffer.flush()
        return 0 if result.get("status") in (
            "PASS", "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED",
        ) else 1
    except Exception as error:
        sys.stderr.write("V14 campaign rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
