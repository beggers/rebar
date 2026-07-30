#!/usr/bin/env python3
"""Freeze and root-reproduce two fully corrected first-party Zig source builds."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/reproduce_owned_zig_final_original_source_build_v17.py"
PROTOCOL = "oracle/phase2/ZIG-FINAL-ORIGINAL-SOURCE-BUILD-V17.md"
CONTRACT = "oracle/phase2/zig-final-original-source-build-v17.json"
SCHEMA = "rebar-owned-zig-final-original-source-build-v17"
VERSION = 17
ROOT_PREFIX = "rebar-phase2-zig-final-original-source-build-v17-"
LABEL_PREFIX = "zig-final-original-source-build-v17-"
CANONICAL_PREFIX = "/rebar-owned-zig-final-original-v17-source"
GOAL = (
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3_756,
)
PREVIOUS = {
    "source": (
        "tools/reproduce_owned_zig_full_semantic_source_build_v16.py",
        "b53e0d01a0302021e4ef5671a8c9f4f6f80f2f2a09061e3385381cb76fd9f1f3",
        58_450,
    ),
    "protocol": (
        "oracle/phase2/ZIG-FULL-SEMANTIC-SOURCE-BUILD-V16.md",
        "fd4070d798da38b2b2473ebb480780f0b13b57e7378d05eaeb77a9efabab089e",
        6_580,
    ),
    "contract": (
        "oracle/phase2/zig-full-semantic-source-build-v16.json",
        "faeea68ada0ee3c47beb2e5ee24acbbb9e19c324fb4ddb0c2b8f098a54e4f543",
        18_059,
    ),
}
PREVIOUS_BUILD = (
    "oracle/phase2/evidence/zig-full-semantic-source-build-v16-"
    "phase2-v16-zig-full-semantic-root-provenance-build-receipt.json",
    "5a20e5fc1c052d58b25cf279db926bdf8c227e652d3a37be529b1491987b28f1",
    174_596,
)
LEGACY = {
    "source": (
        "tools/reproduce_owned_zig_scanner_phrase_source_build_v13.py",
        "673cb1a5a1b2b70d36e77032e01312fda2887828a8898900f1c91378fde8687e",
        123_672,
    ),
    "protocol": (
        "oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-BUILD-V13.md",
        "b8c3622d64041386c6202f0d980632c9e03a8c90c08455d1c38a50260ae68a40",
        8_765,
    ),
    "contract": (
        "oracle/phase2/zig-scanner-phrase-source-build-v13.json",
        "6b0b918da55d55144c1384d915027f9ba360048c910a4225568abce6fd3efd15",
        21_331,
    ),
}
CAMPAIGN = {
    "source": (
        "tools/run_owned_repaired_zig_original_campaign_v13.py",
        "fa46d4029f5590adceb22bfe4e612248da5f7f90ed6362d58faa5b631fee7ff8",
        246_570,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V13.md",
        "6b42893161e37baec1695aefb414fb7179b778f2164018b024bd68b3c9bb5c2c",
        9_553,
    ),
    "contract": (
        "oracle/phase2/repaired-zig-original-campaign-v13.json",
        "327b14096e36c7a2e4cab977a452fc2477fbf148396f50433cbf1dc8aba31a3f",
        106_084,
    ),
}
GUARD = {
    "source": (
        "tools/verify_owned_candidate_runtime_independence_v4.py",
        "5b498643fa730dc09090bdc9e189e2d395cbe41a2b14019937eb251fd38240f3",
        48_687,
    ),
    "protocol": (
        "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V4.md",
        "835473a98f62c9b2cb0dee61736b6cbbab4460f14d8371597e80933c64721a16",
        4_492,
    ),
    "contract": (
        "oracle/phase2/candidate-runtime-independence-v4.json",
        "30f5c52d5aadfd6e8a7be7c6f355d9628510384d7fd922bcfb609dfe854acea2",
        9_352,
    ),
}
REPAIR = {
    "source": (
        "tools/apply_owned_zig_final_original_semantics_v1.py",
        "82e10749aff7642511271b9520188ef45744454d36c57fb9e7d895e504bd30d7",
        60_115,
    ),
    "protocol": (
        "oracle/phase2/ZIG-FINAL-ORIGINAL-SEMANTICS-V1.md",
        "b88bb03cc7217db56238c6b2f0abc25959974481ca7941ca7b746a4acbd30b0b",
        5_277,
    ),
    "contract": (
        "oracle/phase2/zig-final-original-semantics-v1.json",
        "1ad1be3bd4816e63a9ba36bcd59cf2f7c1276acacb08e9f22128223c504dc080",
        4_175,
    ),
}
LOCK = (
    "toolchains/zig-0.16.0.lock.json",
    "a0f105b47dd60bab9c3136a7b7a44ab417bc034e680bf2d30693cc954422b3cd",
    628,
)
FAILURE = (
    "oracle/phase2/evidence/repaired-zig-original-campaign-v16-"
    "phase2-v16-zig-full-semantic-original-p0-v16-failures-"
    "publication-receipt.json",
    "a7019c02b2906eb15f622e9bd9e61eb7476c528019fac537ed7072b3f82efe7a",
    21_041,
)
MATERIALIZATION_PATH = (
    "oracle/phase2/evidence/zig-final-original-semantics-v1-application.json"
)
ENGINE = (
    "candidates/zig/mini_regex.zig",
    "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28",
    186_915,
)
ADAPTER = (
    "candidates/zig/variants/final_original_semantics_v1/zig_candidate.py",
    "a6587f43112cc54f2fbf86c8c62ea28426950caae94c6fce2ccead61fcc0f124",
    67_657,
)
BRIDGE = (
    "candidates/zig/variants/final_original_semantics_v1/py_bridge.c",
    "4228199b7c65c4d02a78e0e9764a52aed63ff9a4c8230381925d5d3f2eb588ac",
    176_761,
)
LEGACY_ADAPTER_KEY = "candidates/zig/variants/scanner_phrase_v4/zig_candidate.py"
LEGACY_BRIDGE_KEY = "candidates/zig/py_bridge.c"
LEGACY_CANONICAL_ADAPTER_KEY = "candidates/zig_candidate.py"
EXPECTED_COMPILER_SHA = (
    "2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c"
)
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1_024), ("buffer_v3", 768),
    ("managed_v1", 1_024), ("scanner_verbose_v1", 2_854),
    ("public_types_v1", 6_912), ("substitution_v2", 5_120),
    ("shape_v2", 10_240), ("public_surface_v19", 1_376),
    ("subinterpreter_v2", 128), ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
FAILED_GROUPS = ["original_bounded_v5", "public_v3", "scanner_v3",
                 "scanner_verbose_v1", "public_types_v1", "public_surface_v19"]


class FreezeError(ValueError):
    """A frozen owner, corrected build plan, or strict source boundary changed."""


def require(value: object, reason: str) -> None:
    if value is not True:
        raise FreezeError(reason)


def digest(value: bytes) -> str:
    require(type(value) is bytes, "hash only exact immutable bytes")
    return hashlib.sha256(value).hexdigest()


def sha(value: object, name: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            "require an independently pinned lowercase SHA-256: " + name)
    return value


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                       sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def unique(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "reject duplicate frozen source-evidence fields")
        result[key] = value
    return result


def document(value: bytes, name: str, *, canonical_required: bool = True) -> dict:
    try:
        result = json.loads(value, object_pairs_hook=unique,
                            parse_constant=lambda _: (_ for _ in ()).throw(
                                FreezeError("reject infinite frozen evidence")))
    except (TypeError, ValueError, UnicodeError) as failure:
        raise FreezeError("reject malformed frozen evidence: " + name) from failure
    require(type(result) is dict, "require one complete frozen object: " + name)
    if canonical_required:
        require(canonical(result) == value,
                "reject changed or noncanonical frozen evidence: " + name)
    return result


def same(actual: object, expected: dict, name: str) -> None:
    require(type(actual) is dict,
            "require one complete independently authenticated object: " + name)
    for key, value in expected.items():
        require(actual.get(key) == value,
                "frozen first-party evidence changed: " + name + ": " + key)


def reference(owner: tuple[str, str, int]) -> dict:
    return {"path": owner[0], "sha256": owner[1], "bytes": owner[2]}


def public_rows(materialization: tuple[str, str, int]
                ) -> tuple[tuple[str, str, int], ...]:
    return (GOAL, *PREVIOUS.values(), PREVIOUS_BUILD,
            *LEGACY.values(), *CAMPAIGN.values(), *GUARD.values(),
            *REPAIR.values(), LOCK, FAILURE, materialization)


class SourceWall:
    """Permit exact public owners; never permit candidates, build, or hidden data."""

    def __init__(self, rows: tuple[tuple[str, str, int], ...]):
        self.approved = frozenset(os.path.join(ROOT, owner[0]) for owner in rows)

    def check(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 and type(arguments[2]) is int else 0
            require(type(path) is str and path in self.approved
                    and not (flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT
                                      | os.O_TRUNC | os.O_APPEND))
                    and flags & os.O_NOFOLLOW != 0,
                    "deny candidate, private root, archive, final holdout, or mutation")
            return
        if event.startswith(("subprocess.", "socket.", "ctypes.",
                             "os.exec", "os.spawn")):
            raise FreezeError("deny source-only compiler, process, native load, network")
        if event in {"compile", "exec", "marshal.loads", "marshal.load",
                     "os.system", "os.fork", "os.posix_spawn", "os.mkdir",
                     "os.remove", "os.rename", "os.rmdir", "os.chdir", "os.chmod",
                     "os.link", "os.symlink", "os.truncate", "os.putenv",
                     "time.time", "time.monotonic", "time.perf_counter",
                     "_thread.start_new_thread"}:
            raise FreezeError("deny source-only code execution, mutation, clock, or thread")
        if event == "import" and arguments:
            name = arguments[0]
            require(not (type(name) is str and (
                name in {"re", "_sre", "regex", "re2", "pcre", "ctypes", "gzip"}
                or name.startswith(("candidates.", "rebar."))
            )), "deny regex engine, candidate, native loader, or archive import")


def read(owner: tuple[str, str, int], approved: tuple[tuple[str, str, int], ...]
         ) -> tuple[dict, bytes]:
    require(owner in approved, "read only an exact authenticated public owner")
    path, fingerprint, size = owner
    descriptor = os.open(os.path.join(ROOT, path),
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_uid == os.getuid()
                and before.st_nlink == 1 and before.st_size == size,
                "immutable public owner identity changed: " + path)
        chunks = []
        while True:
            chunk = os.read(descriptor, 1_048_576)
            if not chunk:
                break
            chunks.append(chunk)
        payload = b"".join(chunks)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_uid,
                 before.st_size, before.st_nlink, before.st_mtime_ns,
                 before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_uid,
                    after.st_size, after.st_nlink, after.st_mtime_ns,
                    after.st_ctime_ns)
                and digest(payload) == fingerprint,
                "immutable public source evidence changed: " + path)
        return ({"path": path, "sha256": fingerprint, "bytes": size,
                 "device": after.st_dev, "inode": after.st_ino,
                 "uid": after.st_uid, "mode": "0600", "nlink": after.st_nlink},
                payload)
    finally:
        os.close(descriptor)


def validate_failure(value: dict) -> None:
    same(value, {
        "schema": "rebar-owned-repaired-zig-original-campaign-v16-durable-publication-receipt",
        "status": "PASS", "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "family": "zig", "candidate_status": "FAIL", "candidate_qualified": False,
        "case_execution_denominator": 31_237,
        "verified_passing_case_count": 18_056,
        "semantic_mismatch_count": 1_156,
        "observed_semantic_mismatch_lower_bound": 1_156,
        "suite_count": 13, "completed_suite_count": 13,
        "actual_candidate_workers": 13, "unique_candidate_worker_count": 13,
        "infrastructure_failure_count": 0, "timeout_count": 0,
        "all_original_suites_attempted": True,
        "all_three_original_targets_restored": True,
        "original_campaign_passed": False,
        "hidden_cases_read": 0, "winner_selected": False,
    }, "preserve every genuinely observed complete Zig failure")
    require(value.get("failed_suites") == FAILED_GROUPS,
            "preserve the six actually failing Zig compatibility groups")
    rows = value.get("original_suite_diagnostics")
    require(type(rows) is list and len(rows) == 13,
            "preserve all 13 completed Zig worker observations")
    workers, mistakes, verified = set(), 0, 0
    for row, (name, count) in zip(rows, SUITES, strict=True):
        same(row, {"suite": name, "case_execution_denominator": count,
                   "candidate_imported": True,
                   "guard_installed_before_candidate_import": True,
                   "infrastructure_failure": False,
                   "timed_out": False, "returncode": 0},
             "preserve actual Zig worker " + name)
        worker = row.get("pid")
        errors = row.get("observed_semantic_mismatch_count")
        require(type(worker) is int and worker > 0 and worker not in workers
                and type(errors) is int and 0 <= errors <= count,
                "require distinct actual Zig worker and valid mismatch count")
        workers.add(worker)
        mistakes += errors
        if row.get("status") == "PASS":
            require(errors == 0, "never hide a Zig difference in a passing group")
            verified += count
        else:
            require(row.get("status") == "FAIL" and errors > 0,
                    "never promote a failing Zig worker to a candidate pass")
    require(len(workers) == 13 and mistakes == 1_156 and verified == 18_056,
            "preserve the exact public Zig failure count and denominator")


def validate_guard(value: dict) -> None:
    same(value, {
        "schema": "rebar-owned-candidate-runtime-independence-v4-source-freeze",
        "version": 4, "goal_sha256": GOAL[1],
        "status": "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "performance": "NOT MEASURED", "winner_selected": False,
    }, "authenticate strict corrected V4 interpreter guard")
    same(value.get("phase_one"), {
        "original_case_execution_denominator": 31_237,
        "original_suite_count": 13,
        "original_obligation_count": 73,
        "named_private_waiver_count": 13,
        "separate_supplemental_case_count": 8_244,
        "supplemental_cases_counted_in_original_denominator": False,
        "status": "PASS",
    }, "preserve complete original oracle and separate additional cases")
    same(value.get("runtime_isolation_policy"), {
        "guard_installed_before_candidate_import": True,
        "stdlib_re_engine": "FORBIDDEN", "stdlib_sre_engine": "FORBIDDEN",
        "external_regex_package": "FORBIDDEN",
        "cross_candidate_engine": "FORBIDDEN",
        "matching_fallback": "FORBIDDEN",
        "source_gate_interpreters": "NOT CREATED",
    }, "future Zig worker must install strict independent V4 guard")
    same(value.get("native_owner_policy"), {
        "required_field_count": 14, "native_loaded": False,
        "extra_or_missing_fields": "FORBIDDEN",
    }, "preserve strict future first-party native owner identity")


def validate_repair(value: dict) -> None:
    same(value, {
        "schema": "rebar-owned-zig-final-original-semantics-v1-source-freeze",
        "version": 1,
        "status": "SOURCE FROZEN; CORRECTED FIRST-PARTY ZIG NOT MATERIALIZED",
    }, "preserve independently frozen final Zig source transformations")
    same(value.get("source"), {"path": REPAIR["source"][0],
                               "sha256": REPAIR["source"][1]},
         "pin the final correction's complete source")
    same(value.get("protocol"), {"path": REPAIR["protocol"][0],
                                 "sha256": REPAIR["protocol"][1]},
         "pin the final correction's complete protocol")
    failure = value.get("immutable_latest_complete_failure")
    same(failure, {
        "receipt_path": FAILURE[0], "receipt_sha256": FAILURE[1],
        "receipt_bytes": FAILURE[2], "original_case_denominator": 31_237,
        "actual_independent_candidate_workers": 13,
        "completed_original_categories": 13,
        "verified_passing_case_count": 18_056,
        "observed_complete_mismatch_count": 1_156,
        "scanner_capture_projection_mismatches": 1_028,
        "flag_and_pattern_representation_mismatches": 128,
        "failed_candidate_qualified": False, "history_rewritten": False,
    }, "preserve every original mismatch while preparing corrected sources")
    changed = value.get("first_party_corrections")
    require(type(changed) is dict, "require final bridge and adapter corrections")
    same(changed.get("bridge_target"), {
        "path": BRIDGE[0], "sha256": BRIDGE[1], "bytes": BRIDGE[2],
        "source_sites_changed": 1, "scanner_mismatches_targeted": 1_028,
        "existing_nested_beginning_preserved": True,
        "active_branch_end_always_closed": True,
        "unrelated_groups_and_lastindex_unchanged": True,
    }, "require the exact owned scanner capture correction")
    same(changed.get("adapter_target"), {
        "path": ADAPTER[0], "sha256": ADAPTER[1], "bytes": ADAPTER[2],
        "source_sites_changed": 2, "flags_mismatches_targeted": 128,
        "regexflag_order": "DECLARATION ORDER",
        "compiled_pattern_flag_order": "NUMERIC BIT ORDER",
        "unknown_flag_object_format": "DECIMAL",
        "unknown_compiled_pattern_format": "HEXADECIMAL",
        "complete_cpython_flag_alias_surface": True,
    }, "require the exact independently corrected Python flag surface")
    same(changed, {
        "complete_observed_mismatches_targeted": 1_156,
        "candidate_families_added": 0, "external_regex_packages": 0,
        "stdlib_regex_delegation": False, "cross_candidate_delegation": False,
    }, "the final correction cannot import or delegate matching")
    synthetic = value.get("source_only_synthetic_controls")
    same(synthetic, {"flag_values_checked": 10_241,
                     "pattern_values_checked": 8_193,
                     "scanner_projection_cases_checked": 255_840,
                     "scanner_existing_end_overwrites_checked": 131_040,
                     "scanner_nested_beginnings_preserved": 131_040,
                     "historical_mismatches_explained": 1_156},
         "preserve the independently verified final synthetic controls")


def validate_materialization(value: dict) -> None:
    same(value, {
        "schema": "rebar-owned-zig-final-original-semantics-v1-source-freeze-application",
        "status": "APPLIED", "mode": "apply",
        "source_sha256": REPAIR["source"][1],
        "protocol_sha256": REPAIR["protocol"][1],
        "contract_sha256": REPAIR["contract"][1],
        "candidate_source_files_read": 2,
        "public_owner_files_read": 4,
        "workspace_mutations": 3,
        "historical_mismatches_targeted": 1_156,
        "historical_scanner_mismatches_targeted": 1_028,
        "historical_flags_mismatches_targeted": 128,
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "stdlib_matching_delegation_count": 0,
        "external_regex_dependency_count": 0,
        "candidate_correctness": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_qualified": False,
        "winner_selected": False,
    }, "require the genuine root-authorized final source materialization")
    created = value.get("created")
    require(type(created) is dict, "require exact final Zig target owner identities")
    same(created.get("directory"), {
        "path": "candidates/zig/variants/final_original_semantics_v1",
        "mode": "0700", "fsync_completed": True,
    }, "require one exclusive private final-source directory")
    for name, expected in (("adapter", ADAPTER), ("bridge", BRIDGE)):
        same(created.get(name), {"path": expected[0], "sha256": expected[1],
                                 "bytes": expected[2], "mode": "0600",
                                 "nlink": 1, "exclusive_no_follow": True,
                                 "fsync_completed": True},
             "authenticate the actual root-created final " + name)
    same(value.get("synthetic"), {"flag_values_checked": 10_241,
                                  "pattern_values_checked": 8_193,
                                  "scanner_projection_cases_checked": 255_840,
                                  "historical_mismatches_explained": 1_156},
         "bind actual source creation to every frozen modeled mismatch")


def validate_previous(state: dict) -> None:
    previous = state["previous_contract"]
    same(previous, {
        "schema": "rebar-owned-zig-full-semantic-source-build-v16-source-freeze",
        "version": 16, "family": "zig", "goal_sha256": GOAL[1],
        "qualified_candidate_count": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }, "preserve the proven first-party V16 two-phase build freeze")
    future = previous.get("future_native_build")
    same(future, {"independent_phase_count": 2,
                  "expected_process_count_per_phase": 13,
                  "expected_total_process_count": 26,
                  "source_snapshot_count_per_phase": 3,
                  "expected_source_snapshot_count": 6,
                  "candidate_matching": "NOT RUN",
                  "candidate_qualified": False},
         "retain the proven genuinely independent 26-process build plan")
    commands = future.get("planned_commands")
    require(type(commands) is list and len(commands) == 2
            and all(type(row) is dict and type(row.get("processes")) is list
                    and len(row["processes"]) == 13 for row in commands),
            "retain two actual compilable independently owned source-build phases")
    engine = previous.get("complete_first_party_sources", {}).get("engine")
    same(engine, {"path": ENGINE[0], "sha256": ENGINE[1], "bytes": ENGINE[2]},
         "retain the exact independently written Zig matching engine")
    actual = state["previous_build"]
    same(actual, {
        "schema": "rebar-owned-zig-full-semantic-source-build-v16-plaintext-build-receipt",
        "status": "PASS", "version": 16, "family": "zig",
        "source_sha256": PREVIOUS["source"][1],
        "protocol_sha256": PREVIOUS["protocol"][1],
        "contract_sha256": PREVIOUS["contract"][1],
        "candidate_correctness": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }, "require actual independently successful predecessor native builds")
    build = actual.get("complete_actual_build")
    same(build, {
        "schema": "rebar-owned-zig-full-semantic-source-build-v16-complete-actual-build",
        "status": "PASS", "version": 16,
        "actual_process_count": 26,
        "actual_source_snapshot_count": 6,
        "first_party_engine_source_sha256": ENGINE[1],
        "strict_runtime_guard_version": 4,
        "strict_runtime_guard_contract_sha256": GUARD["contract"][1],
        "external_regex_dependency_count": 0,
        "stdlib_regex_engine_count": 0,
        "cross_family_engine_count": 0,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "historical_zig_observed_mismatch_lower_bound": 1_700,
        "winner_selected": False,
    }, "preserve the actually successful V16 build and its older failures")
    reproducible = build.get("reproducibility")
    same(reproducible, {
        "status": "PASS", "independent_phase_count": 2,
        "compiler_process_count": 26, "source_snapshot_count": 6,
        "all_native_artifacts_byte_identical": True,
    }, "require genuine independently reproduced prior native binaries")
    process = build.get("processes")
    phases = build.get("build_phases")
    require(type(process) is list and len(process) == 26
            and type(phases) is list and len(phases) == 2,
            "preserve all actual predecessor process records and phases")


def validate_legacy(state: dict) -> None:
    legacy = state["legacy_contract"]
    same(legacy, {
        "schema": "rebar-owned-zig-scanner-phrase-source-build-v13-source-freeze",
        "version": 13, "qualified_candidate_count": 0,
        "performance": "NOT MEASURED", "winner_selected": False,
    }, "reuse only exact first-party V13 build plumbing")
    same(legacy.get("original_oracle"), {
        "python_implementation": "CPython", "python_version": "3.14.6",
        "original_case_execution_denominator": 31_237,
        "original_suite_count": 13,
        "original_named_private_waiver_count": 13,
        "mapped_original_obligation_count": 73,
        "original_crosswalk_count": 34,
        "supplemental_reference_case_count": 8_244,
        "supplemental_cases_added_to_original_denominator": False,
    }, "preserve the complete frozen original Python correctness oracle")
    toolchain = legacy.get("offline_toolchain")
    same(toolchain, {
        "zig_version": "0.16.0",
        "zig_exact_executable": "/tmp/zig-x86_64-linux-0.16.0/zig",
        "compiler_binaries_executed": 0,
        "network_requests": 0,
    }, "require exact official pinned offline Zig compiler")
    tools = toolchain.get("owners")
    require(type(tools) is list and len(tools) == 6
            and len([row for row in tools
                     if row.get("id") == "zig"
                     and row.get("sha256") == EXPECTED_COMPILER_SHA]) == 1,
            "preserve each authenticated compiler, CPython header, and ELF inspector")
    campaign = state["campaign_contract"]
    same(campaign, {
        "schema": "rebar-owned-repaired-zig-original-campaign-v13-guarded-lifetime-source-freeze",
        "version": 13, "qualified_candidate_count": 0,
        "corrected_original_matching": "NOT RUN",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "winner_selected": False,
    }, "preserve older Zig original failure and obsolete V3 guard as history only")
    same(campaign.get("original_oracle"), {
        "case_execution_denominator": 31_237, "suite_count": 13,
        "named_private_waiver_count": 13, "obligation_count": 73,
        "crosswalk_count": 34, "supplemental_reference_case_count": 8_244,
        "supplemental_cases_added_to_original_denominator": False,
        "final_holdout_authorized": False,
        "performance_oracle_authorized": False,
    }, "preserve the unchanged original case matrix and sealed holdout")


def validate_lock(value: dict) -> None:
    same(value, {
        "schema": "rebar-official-language-toolchain-v1", "language": "Zig",
        "version": "0.16.0", "release_channel": "stable",
        "platform": "x86_64-linux", "compiler_sha256": EXPECTED_COMPILER_SHA,
    }, "authenticate the exact official offline stable Zig toolchain")


def verify(state: dict) -> None:
    require(digest(state["raw"][GOAL[0]]) == GOAL[1],
            "the immutable user objective changed")
    for name, owner in (("previous_contract", PREVIOUS["contract"]),
                        ("previous_build", PREVIOUS_BUILD),
                        ("legacy_contract", LEGACY["contract"]),
                        ("campaign_contract", CAMPAIGN["contract"]),
                        ("guard_contract", GUARD["contract"]),
                        ("repair_contract", REPAIR["contract"]),
                        ("failure", FAILURE),
                        ("materialization", state["materialization_owner"])):
        require(digest(canonical(state[name])) == owner[1],
                "complete authenticated public evidence changed: " + name)
    validate_previous(state)
    validate_legacy(state)
    validate_guard(state["guard_contract"])
    validate_repair(state["repair_contract"])
    validate_materialization(state["materialization"])
    validate_failure(state["failure"])
    validate_lock(state["lock"])
    require(sum(count for _, count in SUITES) == 31_237,
            "never mix supplemental or hidden cases into the original denominator")


def source_effects() -> dict:
    return {
        "candidate_source_files_read": 0,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "reference_workers_started": 0,
        "runtime_guards_installed": 0,
        "subinterpreters_created": 0,
        "compiler_processes_started": 0,
        "compiler_binaries_executed": 0,
        "native_libraries_loaded": 0,
        "native_activations": 0,
        "private_roots_opened": 0,
        "private_roots_created": 0,
        "private_phase_directories_created": 0,
        "private_source_files_written": 0,
        "private_root_receipts_published": 0,
        "build_receipts_published": 0,
        "matching_archives_opened": 0,
        "matching_archives_inflated": 0,
        "holdout_proposals_opened": 0,
        "holdout_proposals_statted": 0,
        "hidden_cases_read": 0,
        "benchmark_files_opened": 0,
        "network_requests": 0,
        "clock_samples": 0,
        "threads_started": 0,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
    }


def replace_templates(value: object) -> object:
    if type(value) is dict:
        return {key: replace_templates(item) for key, item in value.items()}
    if type(value) is list:
        return [replace_templates(item) for item in value]
    if type(value) is str:
        return value.replace("/rebar-owned-zig-full-semantic-v16-source",
                             CANONICAL_PREFIX)
    return value


def build_templates(state: dict) -> list:
    result = replace_templates(
        state["previous_contract"]["future_native_build"]["planned_commands"]
    )
    require(type(result) is list and len(result) == 2
            and all(type(phase.get("processes")) is list
                    and len(phase["processes"]) == 13 for phase in result),
            "preserve all 26 actually implementable offline build command templates")
    return result


def contract_document(state: dict) -> dict:
    actual = state["failure"]
    return {
        "schema": SCHEMA + "-source-freeze", "version": VERSION,
        "status": "SOURCE FROZEN; FINAL CORRECTED FIRST-PARTY ZIG BUILD NOT RUN",
        "family": "zig", "goal_sha256": GOAL[1],
        "source": state["owners"][SOURCE],
        "protocol": state["owners"][PROTOCOL],
        "proven_predecessor_dual_build": {
            "source": state["owners"][PREVIOUS["source"][0]],
            "protocol": state["owners"][PREVIOUS["protocol"][0]],
            "contract": state["owners"][PREVIOUS["contract"][0]],
            "actual_build_receipt": state["owners"][PREVIOUS_BUILD[0]],
            "previous_version": 16, "actual_build_status": "PASS",
            "actual_independent_phase_count": 2,
            "actual_process_count": 26,
            "actual_source_snapshot_count": 6,
            "actual_external_regex_dependency_count": 0,
        },
        "legacy_first_party_build_plumbing": {
            "source": state["owners"][LEGACY["source"][0]],
            "protocol": state["owners"][LEGACY["protocol"][0]],
            "contract": state["owners"][LEGACY["contract"][0]],
            "version": 13, "executed_during_source_gates": False,
            "obsolete_v3_guard_reused": False,
        },
        "previous_original_campaign": {
            "source": state["owners"][CAMPAIGN["source"][0]],
            "protocol": state["owners"][CAMPAIGN["protocol"][0]],
            "contract": state["owners"][CAMPAIGN["contract"][0]],
            "executed_during_source_gates": False,
            "earlier_observed_mismatch_lower_bound_preserved": 1_700,
        },
        "latest_complete_actual_failure": {
            "receipt": state["owners"][FAILURE[0]],
            "candidate_status": actual["candidate_status"],
            "case_execution_denominator": 31_237,
            "suite_count": 13, "completed_suite_count": 13,
            "actual_candidate_worker_count": 13,
            "verified_passing_case_count": 18_056,
            "semantic_mismatch_count": 1_156,
            "scanner_capture_mismatch_count": 1_028,
            "flag_representation_mismatch_count": 128,
            "matching_archive_opened": False,
            "failure_history_rewritten": False,
        },
        "actual_final_source_materialization": {
            "receipt": state["owners"][state["materialization_owner"][0]],
            "status": "APPLIED", "immutable_candidate_sources_created": 2,
            "source_directory_created": 1,
            "historical_semantic_mismatches_targeted": 1_156,
            "final_adapter": state["materialization"]["created"]["adapter"],
            "final_bridge": state["materialization"]["created"]["bridge"],
        },
        "complete_first_party_sources": {
            "engine": state["previous_contract"]["complete_first_party_sources"]["engine"],
            "final_adapter": state["materialization"]["created"]["adapter"],
            "final_bridge": state["materialization"]["created"]["bridge"],
            "engine_authorship": "FIRST-PARTY ZIG PARSER, COMPILER, AND EXECUTOR",
            "bridge_authorship": "FIRST-PARTY CPYTHON C-API BRIDGE",
            "adapter_authorship": "FIRST-PARTY PYTHON PUBLIC COMPATIBILITY LAYER",
            "external_regex_engine_count": 0,
            "external_regex_package_count": 0,
            "cross_candidate_engine_count": 0,
            "matching_fallback_count": 0,
            "stdlib_regex_engine_count": 0,
        },
        "strict_v4_runtime_guard": {
            "source": state["owners"][GUARD["source"][0]],
            "protocol": state["owners"][GUARD["protocol"][0]],
            "contract": state["owners"][GUARD["contract"][0]],
            "version": 4,
            "guard_installed_before_future_candidate_import": True,
            "runtime_guard_executed_by_source_freeze": False,
            "required_native_owner_field_count": 14,
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "official_offline_toolchain": {
            "lock": state["owners"][LOCK[0]],
            "zig_version": "0.16.0",
            "zig_executable": "/tmp/zig-x86_64-linux-0.16.0/zig",
            "zig_compiler_sha256": EXPECTED_COMPILER_SHA,
            "owners": state["legacy_contract"]["offline_toolchain"]["owners"],
            "compiler_processes_started": 0, "network_requests": 0,
        },
        "narrow_copyreg_compatibility_exception": {
            "allowed_only_for_role": "bridge",
            "allowed_symbol": "PyImport_ImportModule",
            "allowed_exact_literal_module": "copyreg",
            "allowed_exact_literal_count": 1,
            "required_complete_corrected_bridge_sha256": BRIDGE[1],
            "engine_may_import_symbol": False,
            "external_regex_import_permitted": False,
            "runtime_non_delegation_established": False,
        },
        "future_native_build": {
            "status": "NOT RUN",
            "authorization": "ROOT-AUTHORIZED COMMITTED AND PUSHED SOURCE ONLY",
            "private_root_prefix": "/tmp/" + ROOT_PREFIX,
            "private_root_mode": "0700", "private_source_mode": "0600",
            "phase_names": ["reference-a", "reference-b"],
            "independent_phase_count": 2,
            "source_snapshot_count_per_phase": 3,
            "expected_source_snapshot_count": 6,
            "expected_process_count_per_phase": 13,
            "expected_total_process_count": 26,
            "planned_commands": build_templates(state),
            "actual_process_count": 0,
            "candidate_workers_started": 0,
            "candidate_matching": "NOT RUN",
            "candidate_qualified": False,
            "native_reproducibility": "NOT MEASURED",
            "private_root_receipt_schema": SCHEMA + "-private-root-receipt",
            "build_receipt_schema": SCHEMA + "-plaintext-build-receipt",
            "private_root_receipt_template": "oracle/phase2/evidence/"
                + LABEL_PREFIX + "<FRESH-LABEL>-private-root-receipt.json",
            "build_receipt_template": "oracle/phase2/evidence/"
                + LABEL_PREFIX + "<FRESH-LABEL>-build-receipt.json",
            "success_root_retained": True,
            "failure_cleanup_limited_to_exact_owned_private_root": True,
        },
        "source_only_effects": source_effects(),
        "original_oracle": {
            "case_execution_denominator": 31_237,
            "suite_count": 13,
            "suites": [{"id": name, "case_execution_count": count}
                       for name, count in SUITES],
            "named_private_waiver_count": 13,
            "obligation_count": 73, "crosswalk_count": 34,
            "supplemental_reference_case_count": 8_244,
            "supplemental_cases_counted_in_original_denominator": False,
            "final_holdout_authorized": False,
            "performance_oracle_authorized": False,
        },
        "from_scratch_policy": {
            "stdlib_regex_engine": "FORBIDDEN",
            "stdlib_sre_engine": "FORBIDDEN",
            "external_regex_package": "FORBIDDEN",
            "external_regex_library": "FORBIDDEN",
            "cross_candidate_engine": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
            "network_fetch": "FORBIDDEN",
            "copyreg_pickle_helper_only": "ALLOWED IF EXACT DIGEST-BOUND SOURCE",
        },
        "qualified_candidate_count": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def context(options: argparse.Namespace, *, source_only: bool) -> dict:
    require(type(options.source_bytes) is int and 1 <= options.source_bytes <= 524_288
            and type(options.protocol_bytes) is int
            and 1 <= options.protocol_bytes <= 65_536,
            "independently pin complete V17 source and protocol byte sizes")
    source_owner = (SOURCE, sha(options.source_sha256, "V17 source"),
                    options.source_bytes)
    protocol_owner = (PROTOCOL, sha(options.protocol_sha256, "V17 protocol"),
                      options.protocol_bytes)
    materialization = (MATERIALIZATION_PATH,
                       sha(options.materialization_sha256, "actual final source receipt"),
                       options.materialization_bytes)
    require(type(options.materialization_bytes) is int
            and 0 < options.materialization_bytes <= 262_144,
            "independently pin exact actual materialization receipt bytes")
    contract_owner = None
    if options.contract_sha256 is not None:
        require(type(options.contract_bytes) is int
                and 1 <= options.contract_bytes <= 524_288,
                "independently pin the complete V17 frozen machine contract")
        contract_owner = (CONTRACT, sha(options.contract_sha256, "V17 contract"),
                          options.contract_bytes)
    for group, mapping in (("previous", PREVIOUS), ("legacy", LEGACY),
                           ("campaign", CAMPAIGN), ("guard", GUARD),
                           ("repair", REPAIR)):
        for name, owner in mapping.items():
            require(getattr(options, group + "_" + name + "_sha256") == owner[1],
                    "independently pin public " + group + " " + name)
    for name, owner in (("previous_build", PREVIOUS_BUILD),
                        ("failure", FAILURE), ("lock", LOCK),
                        ("engine", ENGINE), ("adapter", ADAPTER),
                        ("bridge", BRIDGE)):
        require(getattr(options, name + "_sha256") == owner[1],
                "independently pin final first-party owner " + name)
    rows = (*public_rows(materialization), source_owner, protocol_owner)
    if contract_owner is not None:
        rows = (*rows, contract_owner)
    wall = None
    if source_only:
        wall = SourceWall(rows)
        sys.addaudithook(wall.check)
    metadata, raw = {}, {}
    for owner in rows:
        identity, payload = read(owner, rows)
        metadata[owner[0]], raw[owner[0]] = identity, payload
    result = {
        "options": options, "wall": wall, "owners": metadata, "raw": raw,
        "materialization_owner": materialization,
        "previous_contract": document(raw[PREVIOUS["contract"][0]], "V16 build freeze"),
        "previous_build": document(raw[PREVIOUS_BUILD[0]], "actual V16 dual build"),
        "legacy_contract": document(raw[LEGACY["contract"][0]], "V13 build plumbing"),
        "campaign_contract": document(raw[CAMPAIGN["contract"][0]], "historical campaign"),
        "guard_contract": document(raw[GUARD["contract"][0]], "corrected V4 guard"),
        "repair_contract": document(raw[REPAIR["contract"][0]], "final source repair"),
        "failure": document(raw[FAILURE[0]], "actual 1,156-difference failure"),
        "materialization": document(raw[materialization[0]], "actual corrected sources"),
        "lock": document(raw[LOCK[0]], "official Zig lock", canonical_required=False),
    }
    verify(result)
    if contract_owner is not None:
        current = document(raw[CONTRACT], "frozen V17 build contract")
        require(current == contract_document(result),
                "bind every actual immutable owner to the frozen build plan")
    return result


def changed(value: object) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        return value + " CHANGED"
    if type(value) is list:
        return value + ["CHANGED"]
    if type(value) is dict:
        return {**value, "__v17_hostile": True}
    if value is None:
        return "CHANGED"
    raise FreezeError("unsupported hostile frozen source value")


def hostile_controls(state: dict) -> int:
    seen = []

    def reject_context(name: str, action) -> None:
        forged = copy.deepcopy(state)
        action(forged)
        try:
            verify(forged)
        except (FreezeError, TypeError, ValueError, KeyError, IndexError):
            seen.append(name)
            return
        raise FreezeError("a forged final Zig source freeze was accepted: " + name)

    for name in ("previous_contract", "previous_build", "legacy_contract",
                 "campaign_contract", "guard_contract", "repair_contract",
                 "failure", "materialization"):
        for field in sorted(state[name]):
            reject_context(name + ": " + field,
                           lambda value, owner=name, key=field:
                               value[owner].__setitem__(
                                   key, changed(value[owner][key])))
    for index in range(len(SUITES)):
        reject_context("removed failed Zig worker " + str(index),
                       lambda value, number=index:
                           value["failure"]["original_suite_diagnostics"].pop(number))
    wall = state["wall"]
    require(wall is not None, "hostile controls require a strict active source wall")

    def reject_wall(name: str, event: str, arguments: tuple) -> None:
        try:
            wall.check(event, arguments)
        except FreezeError:
            seen.append(name)
            return
        raise FreezeError("the source-only final Zig wall allowed " + name)

    for name, path in (
        ("final adapter candidate source", ROOT + "/" + ADAPTER[0]),
        ("final bridge candidate source", ROOT + "/" + BRIDGE[0]),
        ("first-party matching engine", ROOT + "/" + ENGINE[0]),
        ("native engine", ROOT + "/candidates/_zig_probe.so"),
        ("native bridge", ROOT + "/candidates/_zig_bridge.so"),
        ("compressed matching archive", ROOT + "/oracle/phase2/evidence/failure.json.gz"),
        ("private build root", "/tmp/" + ROOT_PREFIX + "forbidden"),
        ("heldout proposal", ROOT + "/oracle/phase3/expanded-sealed-holdout-v3.json"),
        ("hidden seed", ROOT + "/oracle/phase3/final.seed"),
        ("hidden cases", ROOT + "/oracle/phase3/final-hidden.json"),
    ):
        reject_wall(name, "open", (path, None, os.O_RDONLY | os.O_NOFOLLOW))
    for name, event, args in (
        ("Zig compiler", "subprocess.Popen", ("zig",)),
        ("native loader", "ctypes.dlopen", ("engine.so",)),
        ("candidate import", "import", ("candidates.zig_candidate",)),
        ("stdlib matcher", "import", ("re",)),
        ("CPython sre engine", "import", ("_sre",)),
        ("external regex package", "import", ("regex",)),
        ("archive module", "import", ("gzip",)),
        ("benchmark timer", "time.perf_counter", ()),
        ("network access", "socket.connect", ("example.invalid",)),
        ("new thread", "_thread.start_new_thread", ()),
        ("destructive rename", "os.rename", ("old", "new")),
        ("dynamic compilation", "compile", (b"1", "synthetic")),
    ):
        reject_wall(name, event, args)
    for value in (None, "", "0" * 63, "0" * 65, "X" * 64):
        try:
            sha(value, "hostile candidate owner")
        except FreezeError:
            seen.append("malformed complete digest")
        else:
            raise FreezeError("a malformed source-owner digest was accepted")
    require(len(seen) >= 175,
            "cover every frozen owner, all 13 workers, candidate and hidden walls")
    return len(seen)


def strict_commit(value: object, name: str) -> str:
    require(type(value) is str and len(value) == 40
            and all(item in "0123456789abcdef" for item in value),
            "require an exact already-pushed main-branch commit: " + name)
    return value


def authorize_build(options: argparse.Namespace) -> None:
    require(options.root_authorized is True
            and options.frozen_committed_pushed is True
            and strict_commit(options.frozen_commit, "frozen commit")
                == strict_commit(options.pushed_commit, "pushed commit"),
            "only root may run the separately committed and pushed Zig V17 build")


def prepare_inner(state: dict) -> tuple[types.ModuleType, dict]:
    module = types.ModuleType("_rebar_owned_v17_authenticated_v16_build")
    module.__file__ = os.path.join(ROOT, PREVIOUS["source"][0])
    exec(compile(state["raw"][PREVIOUS["source"][0]], module.__file__,
                 "exec", dont_inherit=True), module.__dict__)
    require(module.SCHEMA == "rebar-owned-zig-full-semantic-source-build-v16"
            and module.VERSION == 16
            and module.ENGINE == ENGINE,
            "execute only the exact proven immutable V16 build controller")
    module.SOURCE = SOURCE
    module.PROTOCOL = PROTOCOL
    module.CONTRACT = CONTRACT
    module.SCHEMA = SCHEMA
    module.VERSION = VERSION
    module.ROOT_PREFIX = ROOT_PREFIX
    module.LABEL_PREFIX = LABEL_PREFIX
    module.ENGINE = ENGINE
    module.ADAPTER = ADAPTER
    module.BRIDGE = BRIDGE
    module.FAILURE = FAILURE

    def corrected_history(inner: dict) -> None:
        same(inner["legacy_contract"], {
            "schema": "rebar-owned-zig-scanner-phrase-source-build-v13-source-freeze",
            "version": 13, "qualified_candidate_count": 0,
        }, "authenticate first-party V13 executable build plumbing")
        same(inner["campaign_contract"], {
            "schema": "rebar-owned-repaired-zig-original-campaign-v13-guarded-lifetime-source-freeze",
            "version": 13, "qualified_candidate_count": 0,
            "corrected_original_matching": "NOT RUN",
        }, "retain old failed Zig campaign without executing its V3 guard")
        validate_failure(inner["failure"])

    module.validate_history = corrected_history
    inner = module.context(state["options"], wall=False)
    require(inner["owners"][ENGINE[0]]["sha256"] == ENGINE[1]
            and inner["owners"][ADAPTER[0]]["sha256"] == ADAPTER[1]
            and inner["owners"][BRIDGE[0]]["sha256"] == BRIDGE[1],
            "authenticate every exact final engine, adapter, and bridge only for build")
    legacy = module.legacy_module(inner)
    require(legacy.SCHEMA == SCHEMA and legacy.VERSION == VERSION
            and tuple(legacy.PHASE_NAMES) == ("reference-a", "reference-b")
            and len(legacy.PROCESS_ROLES) == 13,
            "reuse only the proven V13/V16 26-process first-party plumbing")
    legacy.CANONICAL_SOURCE_PREFIX = CANONICAL_PREFIX
    return legacy, inner


def bind_builder(state: dict, module: types.ModuleType,
                 inner_controller: dict) -> None:
    original_publish = module.publish_plaintext_pair
    v16 = types.ModuleType("_rebar_owned_v17_authenticated_v16_revalidator")
    v16.__file__ = os.path.join(ROOT, PREVIOUS["source"][0])
    exec(compile(state["raw"][PREVIOUS["source"][0]], v16.__file__,
                 "exec", dont_inherit=True), v16.__dict__)
    v16.SOURCE, v16.PROTOCOL, v16.CONTRACT = SOURCE, PROTOCOL, CONTRACT
    v16.SCHEMA, v16.VERSION = SCHEMA, VERSION
    v16.ROOT_PREFIX, v16.LABEL_PREFIX = ROOT_PREFIX, LABEL_PREFIX
    v16.ENGINE, v16.ADAPTER, v16.BRIDGE, v16.FAILURE = (
        ENGINE, ADAPTER, BRIDGE, FAILURE
    )

    def corrected_history(value: dict) -> None:
        same(value["legacy_contract"], {
            "schema": "rebar-owned-zig-scanner-phrase-source-build-v13-source-freeze",
            "version": 13, "qualified_candidate_count": 0,
        }, "retain proven build plumbing during every fresh source authentication")
        validate_failure(value["failure"])

    v16.validate_history = corrected_history

    def authenticate(options: argparse.Namespace) -> dict:
        public = context(options, source_only=False)
        fresh = v16.context(options, wall=False)
        for tool in module.TOOLCHAINS:
            module.read_external_owner(tool)
        owners = {
            ENGINE[0]: fresh["owners"][ENGINE[0]],
            LEGACY_BRIDGE_KEY: fresh["owners"][BRIDGE[0]],
            LEGACY_ADAPTER_KEY: fresh["owners"][ADAPTER[0]],
            LEGACY_CANONICAL_ADAPTER_KEY: fresh["owners"][ADAPTER[0]],
        }
        protected = {
            ENGINE[0]: fresh["raw"][ENGINE[0]],
            LEGACY_BRIDGE_KEY: fresh["raw"][BRIDGE[0]],
            LEGACY_ADAPTER_KEY: fresh["raw"][ADAPTER[0]],
            LEGACY_CANONICAL_ADAPTER_KEY: fresh["raw"][ADAPTER[0]],
        }
        require(public["materialization"]["created"]["adapter"]["sha256"]
                == ADAPTER[1]
                and public["materialization"]["created"]["bridge"]["sha256"]
                    == BRIDGE[1],
                "reauthenticate actual final source creation before every real build")
        fresh["owners"], fresh["protected"] = owners, protected
        return fresh

    def machine(options: argparse.Namespace, _inherited: dict) -> dict:
        actual = document(state["raw"][CONTRACT], "frozen final Zig V17 build plan")
        require(actual == contract_document(state),
                "never run after the committed source plan or public owners changed")
        return state["owners"][CONTRACT]

    def receipt(_context: dict, options: argparse.Namespace, report: dict) -> dict:
        return {
            "schema": SCHEMA + "-private-root-receipt", "version": VERSION,
            "status": report["status"], "family": "zig",
            "label": module.checked_label(options.label),
            "source_sha256": options.source_sha256,
            "protocol_sha256": options.protocol_sha256,
            "contract_sha256": options.contract_sha256,
            "frozen_commit": options.frozen_commit,
            "pushed_commit": options.pushed_commit,
            "private_root": report.get("private_root"),
            "private_root_retained": report["status"] == "PASS",
            "private_root_cleanup": report.get("failure_cleanup"),
            "phase_names": list(module.PHASE_NAMES),
            "phases": report.get("build_phases", []),
            "source_snapshots_per_completed_phase": 3,
            "actual_process_count": len(report["processes"]),
            "final_adapter_sha256": ADAPTER[1],
            "final_bridge_source_sha256": BRIDGE[1],
            "first_party_engine_source_sha256": ENGINE[1],
            "strict_runtime_guard_version": 4,
            "strict_runtime_guard_contract_sha256": GUARD["contract"][1],
            "actual_final_source_materialization_sha256":
                state["materialization_owner"][1],
            "latest_zig_failure_receipt_sha256": FAILURE[1],
            "latest_zig_observed_semantic_mismatch_count": 1_156,
            "preserved_earlier_zig_mismatch_lower_bound": 1_700,
            "candidate_workers_started": 0,
            "native_activations": 0, "runtime_guards_installed": 0,
            "candidate_correctness": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "holdout": "NOT OPENED", "performance": "NOT MEASURED",
            "winner_selected": False,
        }

    def publication(inherited: dict, options: argparse.Namespace,
                    report: dict) -> dict:
        report.pop("frozen_graph_version", None)
        report.pop("frozen_evidence_owner_lower_bound", None)
        report.pop("frozen_history_reference_lower_bound", None)
        originals = {
            ENGINE[0]: inner_controller["owners"][ENGINE[0]],
            BRIDGE[0]: inner_controller["owners"][BRIDGE[0]],
            ADAPTER[0]: inner_controller["owners"][ADAPTER[0]],
        }
        report["owned_original_sources_before"] = originals
        if report["status"] == "PASS":
            report["owned_original_sources_after"] = originals
        report.update({
            "frozen_commit": options.frozen_commit,
            "pushed_commit": options.pushed_commit,
            "corrected_adapter_sha256": ADAPTER[1],
            "first_party_bridge_source_sha256": BRIDGE[1],
            "first_party_engine_source_sha256": ENGINE[1],
            "strict_runtime_guard_version": 4,
            "strict_runtime_guard_contract_sha256": GUARD["contract"][1],
            "latest_zig_failure_receipt_sha256": FAILURE[1],
            "latest_zig_observed_semantic_mismatch_count": 1_156,
            "preserved_earlier_zig_mismatch_lower_bound": 1_700,
            "actual_final_source_materialization_sha256":
                state["materialization_owner"][1],
            "copyreg_compatibility_exception": {
                "allowed_role": "bridge", "literal_module": "copyreg",
                "allowed_import_count": 1,
                "required_complete_bridge_sha256": BRIDGE[1],
                "engine_import_allowed": False,
                "external_regex_engine_count": 0,
                "runtime_non_delegation_established": False,
            },
        })
        result = original_publish(inherited, options, report)
        result.update({
            "frozen_commit": options.frozen_commit,
            "pushed_commit": options.pushed_commit,
            "final_adapter_sha256": ADAPTER[1],
            "final_bridge_source_sha256": BRIDGE[1],
            "first_party_engine_source_sha256": ENGINE[1],
            "strict_runtime_guard_version": 4,
            "strict_runtime_guard_contract_sha256": GUARD["contract"][1],
            "actual_final_source_materialization_sha256":
                state["materialization_owner"][1],
            "latest_zig_failure_receipt_sha256": FAILURE[1],
            "latest_zig_observed_semantic_mismatch_count": 1_156,
            "external_regex_package_count": 0,
            "external_regex_engine_count": 0,
            "candidate_qualified": False,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "holdout": "NOT OPENED", "performance": "NOT MEASURED",
            "winner_selected": False,
        })
        return result

    module.authenticate_context = authenticate
    module.require_machine_contract = machine
    module.root_receipt_document = receipt
    module.publish_plaintext_pair = publication


def actual_build(options: argparse.Namespace) -> tuple[int, dict]:
    authorize_build(options)
    state = context(options, source_only=False)
    actual_contract = document(state["raw"][CONTRACT], "final V17 build contract")
    require(actual_contract == contract_document(state),
            "authenticate the complete V17 plan before executing build plumbing")
    module, inner = prepare_inner(state)
    bind_builder(state, module, inner)
    code, result = module.run_build(options)
    require(result.get("status") in {"PASS", "FAIL"}
            and result.get("candidate_qualified") is False,
            "a source build cannot become a qualified matching result")
    if result["status"] == "PASS":
        require(result.get("actual_compiler_process_count") == 26
                and result.get("actual_phase_count") == 2,
                "claim reproducibility only after 26 actual isolated processes")
    return code, result


def source_result(state: dict, *, hostile: bool) -> dict:
    checks = hostile_controls(state) if hostile else 0
    return {
        "schema": SCHEMA + "-source-only-result", "version": VERSION,
        "status": "PASS", "mode": "SELF-TEST" if hostile else "FROZEN CONTEXT",
        "source_sha256": state["options"].source_sha256,
        "protocol_sha256": state["options"].protocol_sha256,
        "contract_sha256": state["options"].contract_sha256,
        "actual_final_source_materialization_sha256":
            state["materialization_owner"][1],
        "final_adapter_sha256": ADAPTER[1], "final_adapter_bytes": ADAPTER[2],
        "final_bridge_sha256": BRIDGE[1], "final_bridge_bytes": BRIDGE[2],
        "first_party_engine_sha256": ENGINE[1], "first_party_engine_bytes": ENGINE[2],
        "strict_runtime_guard_version": 4,
        "historical_zig_failure_receipt_sha256": FAILURE[1],
        "historical_zig_verified_passing_case_count": 18_056,
        "historical_zig_observed_semantic_mismatch_count": 1_156,
        "preserved_earlier_zig_mismatch_lower_bound": 1_700,
        "original_case_execution_denominator": 31_237,
        "original_suite_count": 13,
        "future_independent_phase_count": 2,
        "future_processes_per_phase": 13,
        "future_total_processes": 26,
        "future_source_snapshots_per_phase": 3,
        "hostile_controls_rejected": checks,
        **source_effects(),
        "candidate_qualified": False, "qualified_candidate_count": 0,
        "holdout": "NOT OPENED", "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


class SafeParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise FreezeError("reject unauthorized final Zig source-build action: " + message)


def arguments() -> argparse.Namespace:
    tokens = [value for value in sys.argv[1:] if value.startswith("--")]
    require(len(tokens) == len(set(tokens)),
            "reject repeated final Zig modes, owner pins, or root capabilities")
    parser = SafeParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--build", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", required=True, type=int)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--protocol-bytes", required=True, type=int)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--contract-bytes", type=int)
    for group in ("previous", "legacy", "campaign", "guard", "repair"):
        for name in ("source", "protocol", "contract"):
            parser.add_argument("--" + group + "-" + name + "-sha256", required=True)
    for name in ("previous-build", "failure", "lock", "engine", "adapter", "bridge"):
        parser.add_argument("--" + name + "-sha256", required=True)
    parser.add_argument("--materialization-sha256", required=True)
    parser.add_argument("--materialization-bytes", required=True, type=int)
    parser.add_argument("--label")
    parser.add_argument("--root-authorized", action="store_true")
    parser.add_argument("--frozen-committed-pushed", action="store_true")
    parser.add_argument("--frozen-commit")
    parser.add_argument("--pushed-commit")
    options = parser.parse_args()
    if options.render_contract:
        require(options.contract_sha256 is None and options.contract_bytes is None
                and options.label is None and options.root_authorized is False
                and options.frozen_committed_pushed is False
                and options.frozen_commit is None and options.pushed_commit is None,
                "render only the prospective root-authorized final build contract")
    elif options.build:
        require(options.contract_sha256 is not None
                and options.contract_bytes is not None and options.label is not None,
                "actual corrected Zig build needs a frozen contract and fresh label")
    else:
        require(options.contract_sha256 is not None and options.contract_bytes is not None
                and options.label is None and options.root_authorized is False
                and options.frozen_committed_pushed is False
                and options.frozen_commit is None and options.pushed_commit is None,
                "source-only gates cannot hold a label or actual build authority")
    return options


def main() -> int:
    options = arguments()
    require(sys.executable == PYTHON and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.flags.no_site == 1
            and sys.flags.dont_write_bytecode == 1,
            "require exact isolated, no-site pinned stable CPython 3.14.6")
    if options.build:
        code, result = actual_build(options)
    else:
        state = context(options, source_only=True)
        if options.render_contract:
            sys.stdout.buffer.write(canonical(contract_document(state)))
            sys.stdout.buffer.flush()
            return 0
        result = source_result(state, hostile=options.self_test)
        code = 0
    sys.stdout.buffer.write(canonical(result))
    sys.stdout.buffer.flush()
    return code


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FreezeError, OSError, TypeError, ValueError, KeyError, IndexError,
            RecursionError, UnicodeError) as failure:
        sys.stderr.write("zig-final-original-source-build-v17: "
                         + type(failure).__name__ + ": " + str(failure) + "\n")
        raise SystemExit(1)
