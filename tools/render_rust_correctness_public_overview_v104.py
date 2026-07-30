#!/usr/bin/env python3
"""Render independently observed original and public Rust correctness results."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import stat
import sys


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SELF = "tools/render_rust_correctness_public_overview_v104.py"
OUTPUT = "docs/evidence/candidate-current-overview-v104"
VERSION = 104
ORIGINAL = 31_237
PUBLIC = 10_434
SUPPLEMENTAL = 8_244
UNMEASURED = "NOT MEASURED"
GOAL = (
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3_756,
)
PREVIOUS = {
    "source": (
        "tools/render_latest_rust_original_correctness_v103.py",
        "eb85f4e59a8b0463419fe917e6eb7f42096ae3f3e57d6609b660b6a672171859",
        58_150,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v103.inputs.json",
        "b2635cb27a2029434587711a08f4bf61b9b68cf32565b5c974a4975a3126a7b8",
        5_179,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v103.json",
        "0a53d2425265b12d176f0538e521b811328a25d44595bc33cf09b380813c3435",
        20_619,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v103.svg",
        "ecf2732a75d2c864e13ea9a4dbef44804b2d541cd2f9e58020b57c764f40c026",
        8_011,
    ),
}
ORIGINAL_RECEIPT = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v30-rust-complete-semantic-source-root-provenance-original-p0-v26-"
    "publication-receipt.json",
    "84804409997794ce7e8bfff67ca8ffdcada9651a1660bda2654742befbba20f5",
    12_055,
)
PUBLIC_RECEIPT = (
    "oracle/phase2/evidence/rust-full-public-correctness-v5-v33-full-public-v5-"
    "run-001-publication-receipt.json",
    "8e2343809a8d9226973b1b70ca9d7348f750573caa2729123afb007f02a03bd9",
    6_889,
)
AUDIT_RECEIPT = (
    "oracle/phase2/evidence/rust-clean-non-delegation-v5-actual-source-audit.json",
    "a6962420b66e4e450abeddaef552a7f3d81e922ceb5254e00574609eabfc8203",
    16_427,
)
SUITES = (
    ("original_bounded_v5", 151),
    ("public_v3", 864),
    ("scanner_v3", 1_024),
    ("buffer_v3", 768),
    ("managed_v1", 1_024),
    ("scanner_verbose_v1", 2_854),
    ("public_types_v1", 6_912),
    ("substitution_v2", 5_120),
    ("shape_v2", 10_240),
    ("public_surface_v19", 1_376),
    ("subinterpreter_v2", 128),
    ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)


class Rejected(ValueError):
    """Authentic evidence, truthful reporting, or source-only isolation changed."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise Rejected(message)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def pin(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(character in "0123456789abcdef" for character in value),
            "require a complete immutable SHA-256: " + label)
    return value


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, allow_nan=False,
                   separators=(",", ":"))
        + "\n"
    ).encode("ascii")


def unique(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "reject duplicate authenticated public JSON fields")
        result[key] = value
    return result


def document(payload: bytes, name: str) -> dict:
    try:
        value = json.loads(
            payload,
            object_pairs_hook=unique,
            parse_constant=lambda _: (_ for _ in ()).throw(
                Rejected("reject nonfinite authenticated JSON")),
        )
    except (ValueError, TypeError, UnicodeError) as failure:
        raise Rejected("reject invalid authenticated public JSON: " + name) from failure
    require(type(value) is dict and canonical(value) == payload,
            "reject noncanonical authenticated public JSON: " + name)
    return value


def same(actual: object, expected: dict, label: str) -> None:
    require(type(actual) is dict,
            "require a complete authenticated public object: " + label)
    for key, value in expected.items():
        require(actual.get(key) == value,
                "authenticated public evidence changed: " + label + ": " + key)


def reference(owner: tuple[str, str, int]) -> dict:
    return {"path": owner[0], "sha256": owner[1], "bytes": owner[2]}


def owners() -> tuple[tuple[str, str, int], ...]:
    return (GOAL, *PREVIOUS.values(), ORIGINAL_RECEIPT,
            PUBLIC_RECEIPT, AUDIT_RECEIPT)


class SourceWall:
    """Permit only explicitly digest-bound plaintext evidence and owned outputs."""

    def __init__(self, render: bool) -> None:
        self.render = render
        self.reads = frozenset(
            os.path.join(ROOT, owner[0]) for owner in owners()
        ) | {os.path.join(ROOT, SELF)}
        self.outputs = frozenset(
            os.path.join(ROOT, OUTPUT + suffix)
            for suffix in (".svg", ".inputs.json", ".json")
        )

    def check(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 and type(arguments[2]) is int else 0
            require(type(path) is str,
                    "reject descriptor-only, relative, hidden, or candidate access")
            writing = bool(flags & (
                os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC
            ))
            if writing:
                necessary = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                require(self.render and path in self.outputs
                        and flags & necessary == necessary,
                        "reject source-only, nonexclusive, or unowned output mutation")
            else:
                require(path in self.reads and flags & os.O_NOFOLLOW != 0,
                        "reject candidate, native object, archive, proposal, seed, or holdout")
            return
        forbidden = {
            "os.system", "os.fork", "os.posix_spawn", "os.mkdir", "os.remove",
            "os.rename", "os.rmdir", "os.chdir", "os.chmod", "os.link",
            "os.symlink", "os.truncate", "os.putenv", "time.time",
            "time.monotonic", "time.perf_counter", "_thread.start_new_thread",
        }
        if (event.startswith(("subprocess.", "socket.", "ctypes.",
                              "os.exec", "os.spawn"))
                or event in forbidden):
            raise Rejected("reject native loading, process, thread, timing, network, or mutation")
        if event == "import" and arguments:
            name = arguments[0]
            require(not (
                type(name) is str and (
                    name in {"re", "_sre", "regex", "re2", "ctypes", "gzip"}
                    or name.startswith(("candidates.", "rebar."))
                )
            ), "reject candidate, regex engine, decompressor, or native import")


def read(owner: tuple[str, str, int], accepted: tuple[tuple[str, str, int], ...]) -> bytes:
    require(owner in accepted, "reject public owner outside the V104 closed allowlist")
    path, sha256, size = owner
    descriptor = os.open(os.path.join(ROOT, path),
                         os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode)
                and stat.S_IMODE(identity.st_mode) == 0o600
                and identity.st_uid == os.getuid()
                and identity.st_nlink == 1
                and identity.st_size == size,
                "public evidence identity changed: " + path)
        blocks = []
        while True:
            block = os.read(descriptor, 1_048_576)
            if not block:
                break
            blocks.append(block)
        value = b"".join(blocks)
        require(digest(value) == sha256,
                "public evidence content digest changed: " + path)
        return value
    finally:
        os.close(descriptor)


def verify_previous(context: dict) -> None:
    previous, inputs = context["previous_summary"], context["previous_inputs"]
    common = {
        "version": 103,
        "actual_current_graph_predecessor_version": 101,
        "goal_sha256": GOAL[1],
        "python": "3.14.6",
        "original_case_execution_denominator": ORIGINAL,
        "original_suite_count": len(SUITES),
        "separate_additional_reference_case_count": SUPPLEMENTAL,
        "additional_cases_included_in_original_denominator": False,
        "qualified_candidate_count": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "candidate_workers_started_by_graph": 0,
        "candidate_source_owners_opened_by_graph": 0,
        "native_binary_files_opened_by_graph": 0,
        "compressed_archives_opened_by_graph": 0,
        "holdout_proposal_files_opened_by_graph": 0,
        "holdout_proposal_files_statted_by_graph": 0,
        "holdout_cases_opened_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "final_holdout_opened": False,
        "winner_selected": False,
    }
    same(inputs, common, "immutable previous V103 correctness inputs")
    same(previous, common, "immutable previous V103 correctness publication")
    same(previous, {
        "schema": "rebar-candidate-current-overview-v103-summary",
        "status": "PASS",
        "candidate_status": "PASS",
        "candidate_original_oracle_pass": True,
        "original_suite_correctness_qualified": True,
        "candidate_qualified": False,
        "verified_passing_case_count": ORIGINAL,
        "semantic_mismatch_count": 0,
        "previous_rust_verified_passing_case_count": 15_877,
        "previous_rust_semantic_mismatch_count": 1_352,
    }, "preserve Rust's original-suite PASS and its earlier failure history")
    require(inputs.get("headline") == previous.get("headline")
            and inputs.get("previous_overview") == previous.get("previous_overview")
            and inputs.get("rust_v26_public_evidence")
                == previous.get("rust_v26_public_evidence"),
            "previous complete public overview documents diverged")
    same(previous.get("renderer"), reference(PREVIOUS["source"]),
         "immutable previous V103 renderer")
    same(previous.get("headline"), {
        "original_python_check_count": ORIGINAL,
        "original_python_suite_count": len(SUITES),
        "rust_current_verified_original_checks": ORIGINAL,
        "rust_current_exact_semantic_mismatch_count": 0,
        "rust_current_candidate_status": "PASS",
        "rust_current_candidate_qualified": False,
        "rust_current_original_oracle_pass": True,
        "c_current_verified_original_checks": 16_413,
        "c_current_observed_individual_mismatch_records": 606,
        "c_current_candidate_execution_failure_count": 1,
        "zig_current_verified_original_checks": 4_607,
        "rust_previous_verified_original_checks": 15_877,
        "rust_previous_exact_semantic_mismatch_count": 1_352,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": UNMEASURED,
        "speed_relative_to_python": UNMEASURED,
        "winner_selected": False,
    }, "preserve all observed original Python, Rust, C, and Zig results")
    same(previous["rust_v26_public_evidence"].get("receipt"),
         reference(ORIGINAL_RECEIPT), "previous independently published Rust PASS")
    require(type(previous.get("complete_original_suite_results")) is list
            and len(previous["complete_original_suite_results"]) == len(SUITES)
            and type(previous.get("previous_complete_original_suite_results")) is list
            and len(previous["previous_complete_original_suite_results"]) == len(SUITES)
            and type(previous.get("preserved_c_original_suite_results")) is list
            and len(previous["preserved_c_original_suite_results"]) == len(SUITES)
            and type(previous.get("preserved_c_observed_mismatch_vector_fingerprints"))
            is list
            and len(previous["preserved_c_observed_mismatch_vector_fingerprints"]) == 12,
            "preserve every original-suite outcome and every observed C mismatch")
    require(context["previous_svg"].startswith(b"<svg ")
            and b'role="img"' in context["previous_svg"]
            and b"31,237 / 31,237" in context["previous_svg"]
            and b"16,413 / 31,237" in context["previous_svg"]
            and b"4,607 / 31,237" in context["previous_svg"],
            "the immutable predecessor graph no longer preserves all family results")


def verify_original(context: dict) -> None:
    original = context["original"]
    same(original, {
        "schema": "rebar-owned-repaired-rust-original-campaign-v26-durable-publication-receipt",
        "family": "rust",
        "status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": "PASS",
        "candidate_original_oracle_pass": True,
        "original_suite_correctness_qualified": True,
        "candidate_qualified": False,
        "case_execution_denominator": ORIGINAL,
        "verified_passing_case_count": ORIGINAL,
        "semantic_mismatch_count": 0,
        "suite_count": len(SUITES),
        "completed_suite_count": len(SUITES),
        "actual_candidate_workers": len(SUITES),
        "distinct_worker_process_id_count": len(SUITES),
        "worker_failure_capture_count": 0,
        "infrastructure_failure_count": 0,
        "all_four_original_targets_restored": True,
        "all_original_observation_vectors_complete": True,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "hidden_cases_read": 0,
        "winner_selected": False,
    }, "authenticate the complete real 31,237-case original Rust PASS")
    rows = original.get("suite_integrity")
    workers = original.get("actual_worker_process_ids")
    require(type(rows) is list and len(rows) == len(SUITES)
            and type(workers) is list and len(workers) == len(SUITES)
            and len(set(workers)) == len(SUITES),
            "all original suites must preserve distinct real worker identities")
    total = 0
    for row, (suite, denominator) in zip(rows, SUITES, strict=True):
        same(row, {
            "suite": suite,
            "case_execution_denominator": denominator,
            "fully_observed": True,
            "actual_worker_started": True,
            "worker_attempted": True,
            "failure_class": "PASS",
            "returncode": 0,
            "mismatch_count": 0,
            "verified_passing_case_count": denominator,
        }, "complete original Rust suite " + suite)
        require(row.get("pid") in workers,
                "every original suite requires a recorded actual worker process")
        total += denominator
    require(total == ORIGINAL,
            "the immutable original denominator must not absorb extra public cases")


def verify_public(context: dict) -> None:
    public = context["public"]
    same(public, {
        "schema": "rebar-owned-rust-full-public-correctness-v5-durable-publication-receipt",
        "version": 5,
        "session": "v33-full-public-v5-run-001",
        "status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": "PASS",
        "candidate_qualified": False,
        "public_10434_correctness_status": "PASS",
        "public_10434_case_count": PUBLIC,
        "public_10434_verified_passing_case_count": PUBLIC,
        "public_10434_mismatch_count": 0,
        "all_public_cases_observed": True,
        "all_public_mismatches_preserved": True,
        "public_api_operation_count": 111,
        "public_dataset_count": 94,
        "candidate_worker_count": 1,
        "reference_worker_count": 1,
        "canonical_candidate_modified": False,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_independent_family_count": 0,
        "minimum_qualified_independent_family_count": 3,
        "v26_original_pass_sha256": ORIGINAL_RECEIPT[1],
        "v26_original_verified_passing_case_count": ORIGINAL,
        "v5_static_pass_sha256": AUDIT_RECEIPT[1],
        "v5_static_external_regex_library_count": 0,
        "v5_static_external_regex_package_count": 0,
        "v5_static_external_regex_symbol_count": 0,
        "v28_historical_public_mismatch_count": 1_145,
        "proposal_content_opens": 0,
        "proposal_metadata_probes": 0,
        "hidden_cases_generated": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "paired_row_count": 0,
        "timing_trials_run": 0,
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "confidence_intervals": UNMEASURED,
        "undefined_behavior": UNMEASURED,
        "winner_selected": False,
    }, "authenticate all separately observed public correctness results")
    require(type(public.get("baseline_pid")) is int
            and type(public.get("rust_pid")) is int
            and public["baseline_pid"] > 0 and public["rust_pid"] > 0
            and public["baseline_pid"] != public["rust_pid"],
            "the public result needs separate actual baseline and candidate workers")
    require(type(public.get("artifacts")) is list and len(public["artifacts"]) == 3
            and all(type(row) is dict
                    and type(row.get("sha256")) is str
                    and type(row.get("bytes")) is int
                    and row["bytes"] > 0
                    for row in public["artifacts"]),
            "retain all public evidence references without opening raw records")
    require(public.get("canonical_candidates_before")
            == public.get("canonical_candidates_after")
            and type(public.get("canonical_candidates_before")) is list
            and len(public["canonical_candidates_before"]) == 6,
            "preserve restored canonical ownership from public receipt metadata only")


def verify_audit(context: dict) -> None:
    audit = context["audit"]
    same(audit, {
        "schema": "rebar-phase2-clean-first-party-rust-non-delegation-v5-root-static-audit",
        "status": "PASS",
        "audited_family": "rust",
        "independent_family_count": 1,
        "all_existing_candidate_families_audited": False,
        "finding_count": 0,
        "findings": [],
        "external_regex_libraries": 0,
        "external_regex_packages": 0,
        "external_regex_symbols": 0,
        "cross_family_dependencies": 0,
        "clean_candidate_source_static_non_delegation": "PASS",
        "clean_candidate_native_elf_static_non_delegation": "PASS",
        "legacy_private_inspect_getter": False,
        "historical_canonical_v4_status": "FAIL",
        "historical_canonical_v4_finding_count": 1,
        "historical_canonical_v4_failure_hidden": False,
        "runtime_non_delegation":
            "NOT ESTABLISHED; STATIC SOURCE AND ELF AUDIT ONLY",
        "candidate_qualified": False,
        "candidate_executions": 0,
        "native_library_loads": 0,
        "final_cases_generated": 0,
        "performance": UNMEASURED,
        "winner_selected": False,
    }, "separate first-party static PASS from still-unproven live runtime independence")
    same(audit.get("effects"), {
        "candidate_executions": 0,
        "candidate_imports": 0,
        "candidate_workers": 0,
        "native_library_loads": 0,
        "clock_samples": 0,
        "benchmark_reads": 0,
        "holdout_reads": 0,
        "hidden_case_reads": 0,
        "archive_reads": 0,
        "archive_decompressions": 0,
        "network_requests": 0,
        "workspace_mutations": 0,
    }, "the static first-party audit is not a live candidate execution")


def verify(context: dict) -> None:
    require(digest(context["goal"]) == GOAL[1],
            "the immutable user objective changed")
    for name, expected in (
        ("previous_inputs", PREVIOUS["inputs"][1]),
        ("previous_summary", PREVIOUS["summary"][1]),
        ("original", ORIGINAL_RECEIPT[1]),
        ("public", PUBLIC_RECEIPT[1]),
        ("audit", AUDIT_RECEIPT[1]),
    ):
        require(digest(canonical(context[name])) == expected,
                "complete authenticated public evidence changed: " + name)
    require(digest(context["previous_svg"]) == PREVIOUS["svg"][1],
            "the entire immutable V103 accessible correctness chart changed")
    verify_previous(context)
    verify_original(context)
    verify_public(context)
    verify_audit(context)


def escape(value: object) -> str:
    text = str(value)
    return (text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def percentage(value: int, denominator: int) -> str:
    return "100%" if value == denominator else f"{100 * value / denominator:.1f}%"


def svg() -> bytes:
    description = (
        "Correctness only, not speed. Both Python and Rust pass all 31,237 "
        "original checks and all 10,434 separate broader public checks. C passes "
        "16,413 original checks with 606 observed differences and an unfinished "
        "group. Zig passes 4,607 original checks with at least 1,700 observed "
        "differences and unfinished groups. C++, Go, and Fortran have no complete "
        "measurement. Rust's static first-party audit passes with zero external "
        "regex engines, packages, or symbols. Live runtime independence is not "
        "established, no candidate is fully qualified, final speed is not "
        "measured, and no winner has been selected."
    )
    elements = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1510" height="1180" '
        'viewBox="0 0 1510 1180" role="img" aria-labelledby="title description">',
        '<title id="title">Can our new engine replace Python re?</title>',
        f'<desc id="description">{escape(description)}</desc>',
        '<rect width="1510" height="1180" rx="24" fill="#0b1220"/>',
        '<text x="58" y="75" fill="#f8fafc" font-size="37" '
        'font-family="system-ui,sans-serif" font-weight="770">'
        'Can our new engine replace Python re?</text>',
        '<text x="60" y="110" fill="#cbd5e1" font-size="19" '
        'font-family="system-ui,sans-serif">'
        'Two separate test sets check correctness. Neither bar measures speed.</text>',
        '<rect x="56" y="140" width="1395" height="125" rx="16" '
        'fill="#122536" stroke="#326459"/>',
        '<text x="80" y="180" fill="#6ee7b7" font-size="24" '
        'font-family="system-ui,sans-serif" font-weight="750">'
        'Rust now matches Python in both test sets</text>',
        '<text x="82" y="219" fill="#f8fafc" font-size="20" '
        'font-family="system-ui,sans-serif" font-weight="660">'
        '31,237 / 31,237 original checks  +  10,434 / 10,434 broader checks</text>',
        '<text x="82" y="246" fill="#cbd5e1" font-size="14" '
        'font-family="system-ui,sans-serif">'
        'Zero differences. More safety and independence checks are still required.</text>',
        '<text x="69" y="303" fill="#94a3b8" font-size="13" '
        'font-family="system-ui,sans-serif" font-weight="690">APPROACH</text>',
        '<text x="179" y="303" fill="#94a3b8" font-size="13" '
        'font-family="system-ui,sans-serif" font-weight="690">'
        'ORIGINAL PYTHON CHECKS</text>',
        '<text x="658" y="303" fill="#94a3b8" font-size="13" '
        'font-family="system-ui,sans-serif" font-weight="690">'
        'BROADER PUBLIC CHECKS</text>',
        '<text x="1105" y="303" fill="#94a3b8" font-size="13" '
        'font-family="system-ui,sans-serif" font-weight="690">CURRENT STATUS</text>',
    ]
    rows = (
        ("Python re", ORIGINAL, PUBLIC, "#34d399", "REFERENCE", "All checks pass"),
        ("Rust", ORIGINAL, PUBLIC, "#60a5fa", "BOTH TEST SETS PASS",
         "Still not fully qualified"),
        ("C", 16_413, None, "#fbbf24", "NOT COMPATIBLE",
         "606 differences; unfinished"),
        ("Zig", 4_607, None, "#fbbf24", "NOT COMPATIBLE",
         "At least 1,700 differences"),
        ("C++", None, None, "#94a3b8", UNMEASURED, "Complete checks not measured"),
        ("Go", None, None, "#94a3b8", UNMEASURED, "Complete checks not measured"),
        ("Fortran", None, None, "#94a3b8", UNMEASURED,
         "Complete checks not measured"),
    )
    for index, (name, original, public, color, state, detail) in enumerate(rows):
        top = 321 + 86 * index
        background = "#10243a" if name == "Rust" else "#101b2b"
        elements += [
            f'<rect x="55" y="{top}" width="1396" height="74" rx="11" '
            f'fill="{background}"/>',
            f'<text x="74" y="{top + 37}" fill="#f8fafc" font-size="18" '
            f'font-family="system-ui,sans-serif" font-weight="690">'
            f'{escape(name)}</text>',
            f'<rect x="179" y="{top + 12}" width="256" height="17" '
            'rx="6" fill="#29384e"/>',
            f'<rect x="658" y="{top + 12}" width="224" height="17" '
            'rx="6" fill="#29384e"/>',
        ]
        if original is not None:
            width = round(256 * original / ORIGINAL)
            elements.append(
                f'<rect x="179" y="{top + 12}" width="{width}" height="17" '
                f'rx="6" fill="{color}"/>'
            )
            original_label = f"{original:,} / {ORIGINAL:,}  ·  {percentage(original, ORIGINAL)}"
        else:
            original_label = UNMEASURED
        if public is not None:
            width = round(224 * public / PUBLIC)
            elements.append(
                f'<rect x="658" y="{top + 12}" width="{width}" height="17" '
                f'rx="6" fill="{color}"/>'
            )
            public_label = f"{public:,} / {PUBLIC:,}  ·  {percentage(public, PUBLIC)}"
        else:
            public_label = UNMEASURED
        elements += [
            f'<text x="179" y="{top + 54}" fill="#e2e8f0" font-size="14" '
            f'font-family="system-ui,sans-serif">{escape(original_label)}</text>',
            f'<text x="658" y="{top + 54}" fill="#e2e8f0" font-size="14" '
            f'font-family="system-ui,sans-serif">{escape(public_label)}</text>',
            f'<text x="1104" y="{top + 31}" fill="{color}" font-size="12" '
            f'font-family="system-ui,sans-serif" font-weight="730">'
            f'{escape(state)}</text>',
            f'<text x="1104" y="{top + 54}" fill="#e2e8f0" font-size="12" '
            f'font-family="system-ui,sans-serif">{escape(detail)}</text>',
        ]
    elements += [
        '<rect x="55" y="942" width="677" height="158" rx="14" '
        'fill="#122536" stroke="#326459"/>',
        '<text x="77" y="975" fill="#6ee7b7" font-size="19" '
        'font-family="system-ui,sans-serif" font-weight="750">'
        'Built from scratch: static inspection passes</text>',
        '<text x="78" y="1007" fill="#f8fafc" font-size="14" '
        'font-family="system-ui,sans-serif">'
        'External regex engines: 0  ·  External regex packages: 0</text>',
        '<text x="78" y="1038" fill="#e2e8f0" font-size="14" '
        'font-family="system-ui,sans-serif">'
        'Python baseline and Rust ran in separate real processes.</text>',
        '<text x="78" y="1068" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">'
        'The older Rust failures and every C/Zig loss remain preserved.</text>',
        '<rect x="753" y="942" width="698" height="158" rx="14" '
        'fill="#291923" stroke="#754453"/>',
        '<text x="775" y="975" fill="#fda4af" font-size="19" '
        'font-family="system-ui,sans-serif" font-weight="750">'
        'What still needs to happen</text>',
        '<text x="775" y="1007" fill="#f8fafc" font-size="14" '
        'font-family="system-ui,sans-serif">'
        'A live runtime independence check has not yet been established.</text>',
        '<text x="775" y="1038" fill="#e2e8f0" font-size="14" '
        'font-family="system-ui,sans-serif">'
        'Three independently written engines must pass all requirements.</text>',
        '<text x="775" y="1068" fill="#fcd34d" font-size="14" '
        'font-family="system-ui,sans-serif">'
        'FINAL SPEED: NOT MEASURED  ·  NO WINNER</text>',
        '<text x="61" y="1138" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">'
        'Original and public test sets are separate. The hidden final comparison '
        'has not been generated or opened.</text>',
        '</svg>',
    ]
    return ("\n".join(elements) + "\n").encode("utf-8")


def assets(context: dict, source_sha: str, source_bytes: int) -> dict:
    previous = context["previous_summary"]
    headline = {
        "purpose": "Build a faster, fully compatible Python re from scratch.",
        "bars_measure": "SEPARATE ORIGINAL AND PUBLIC CORRECTNESS; NOT SPEED",
        "python_version": "3.14.6",
        "original_python_check_count": ORIGINAL,
        "original_python_suite_count": len(SUITES),
        "broader_public_check_count": PUBLIC,
        "broader_public_api_operation_count": 111,
        "broader_public_dataset_count": 94,
        "python_verified_original_checks": ORIGINAL,
        "python_verified_broader_public_checks": PUBLIC,
        "rust_verified_original_checks": ORIGINAL,
        "rust_original_semantic_mismatch_count": 0,
        "rust_verified_broader_public_checks": PUBLIC,
        "rust_broader_public_semantic_mismatch_count": 0,
        "rust_original_oracle_pass": True,
        "rust_broader_public_correctness_pass": True,
        "rust_candidate_qualified": False,
        "rust_static_first_party_audit_status": "PASS",
        "rust_static_external_regex_library_count": 0,
        "rust_static_external_regex_package_count": 0,
        "rust_static_external_regex_symbol_count": 0,
        "rust_static_cross_family_dependency_count": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "c_verified_original_checks": 16_413,
        "c_observed_individual_mismatch_count": 606,
        "c_original_group_execution_failure_count": 1,
        "c_broader_public_checks": UNMEASURED,
        "zig_verified_original_checks": 4_607,
        "zig_observed_individual_mismatch_lower_bound": 1_700,
        "zig_complete_original_mismatch_count": UNMEASURED,
        "zig_broader_public_checks": UNMEASURED,
        "cpp_verified_original_checks": UNMEASURED,
        "go_verified_original_checks": UNMEASURED,
        "fortran_verified_original_checks": UNMEASURED,
        "previous_rust_original_verified_checks": 15_877,
        "previous_rust_original_semantic_mismatch_count": 1_352,
        "previous_rust_broader_public_semantic_mismatch_count": 1_145,
        "independent_first_party_candidate_family_count": 6,
        "minimum_fully_qualified_independent_family_count": 3,
        "fully_qualified_independent_candidate_family_count": 0,
        "fully_compatible_candidate_count": 0,
        "speed_relative_to_python": UNMEASURED,
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "winner_selected": False,
    }
    shared = {
        "version": VERSION,
        "actual_current_graph_predecessor_version": 103,
        "goal_sha256": GOAL[1],
        "python": "3.14.6",
        "headline": headline,
        "original_case_execution_denominator": ORIGINAL,
        "original_suite_count": len(SUITES),
        "broader_public_case_execution_denominator": PUBLIC,
        "broader_public_counted_in_original_denominator": False,
        "separate_additional_reference_case_count": SUPPLEMENTAL,
        "additional_cases_included_in_original_denominator": False,
        "named_private_waiver_count": len(SUITES),
        "renderer": {"path": SELF, "sha256": source_sha, "bytes": source_bytes},
        "previous_overview": {
            name: reference(owner) for name, owner in PREVIOUS.items()
        },
        "original_rust_pass_receipt": reference(ORIGINAL_RECEIPT),
        "broader_public_rust_pass_receipt": reference(PUBLIC_RECEIPT),
        "first_party_static_audit_pass_receipt": reference(AUDIT_RECEIPT),
        "candidate_source_owners_opened_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "reference_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "native_binary_files_opened_by_graph": 0,
        "native_binary_metadata_probes_by_graph": 0,
        "native_libraries_loaded_by_graph": 0,
        "private_build_roots_opened_by_graph": 0,
        "private_build_roots_statted_by_graph": 0,
        "compressed_archives_opened_by_graph": 0,
        "compressed_archives_statted_by_graph": 0,
        "compressed_archives_inflated_by_graph": 0,
        "raw_public_case_archives_opened_by_graph": 0,
        "raw_public_case_archives_statted_by_graph": 0,
        "holdout_proposal_files_opened_by_graph": 0,
        "holdout_proposal_files_statted_by_graph": 0,
        "seed_files_opened_by_graph": 0,
        "holdout_cases_opened_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "final_holdout_opened": False,
        "clock_samples_by_graph": 0,
        "timing_trials_run": 0,
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "undefined_behavior": UNMEASURED,
        "static_first_party_non_delegation": "PASS",
        "live_runtime_no_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
        "preserved_complete_history":
            "FULL V103 SOURCE, INPUTS, SUMMARY, SVG, AND ALL ORIGINAL RESULTS",
    }
    inputs = {
        **shared,
        "schema": "rebar-candidate-current-overview-v104-inputs",
    }
    summary = {
        **shared,
        "schema": "rebar-candidate-current-overview-v104-summary",
        "status": "PASS",
        "status_scope": "AUTHENTICATED ORIGINAL AND PUBLIC CORRECTNESS GRAPH ONLY",
        "rust_original_candidate_status": "PASS",
        "rust_broader_public_candidate_status": "PASS",
        "candidate_original_oracle_pass": True,
        "original_suite_correctness_qualified": True,
        "broader_public_suite_correctness_pass": True,
        "candidate_qualified": False,
        "original_verified_passing_case_count": ORIGINAL,
        "original_semantic_mismatch_count": 0,
        "broader_public_verified_passing_case_count": PUBLIC,
        "broader_public_semantic_mismatch_count": 0,
        "distinct_original_candidate_worker_count": len(SUITES),
        "public_candidate_worker_count": 1,
        "public_reference_worker_count": 1,
        "original_worker_failure_capture_count": 0,
        "original_infrastructure_failure_count": 0,
        "complete_original_suite_results": previous["complete_original_suite_results"],
        "previous_complete_original_suite_results":
            previous["previous_complete_original_suite_results"],
        "preserved_c_original_suite_results":
            previous["preserved_c_original_suite_results"],
        "preserved_c_observed_mismatch_vector_fingerprints":
            previous["preserved_c_observed_mismatch_vector_fingerprints"],
        "historical_c_original_observed_mismatch_count": 606,
        "historical_zig_original_observed_mismatch_lower_bound": 1_700,
        "historical_zig_complete_original_mismatch_count": UNMEASURED,
        "historical_previous_rust_original_mismatch_count": 1_352,
        "historical_previous_rust_public_mismatch_count": 1_145,
        "historical_canonical_static_v4_audit_status": "FAIL",
        "historical_canonical_static_v4_finding_count": 1,
        "current_clean_static_v5_audit_status": "PASS",
        "current_clean_static_v5_finding_count": 0,
    }
    return {"svg": svg(), "inputs": canonical(inputs), "summary": canonical(summary)}


def verify_outputs(context: dict, result: dict,
                   source_sha: str, source_bytes: int) -> None:
    require(result == assets(context, source_sha, source_bytes),
            "the original/public correctness chart is not reproducible")
    inputs = document(result["inputs"], "V104 public graph inputs")
    summary = document(result["summary"], "V104 public graph summary")
    require(inputs.get("headline") == summary.get("headline")
            and inputs.get("previous_overview") == summary.get("previous_overview"),
            "public input and summary views must preserve identical history")
    same(summary, {
        "version": VERSION,
        "original_case_execution_denominator": ORIGINAL,
        "original_suite_count": len(SUITES),
        "broader_public_case_execution_denominator": PUBLIC,
        "broader_public_counted_in_original_denominator": False,
        "rust_original_candidate_status": "PASS",
        "rust_broader_public_candidate_status": "PASS",
        "candidate_original_oracle_pass": True,
        "original_suite_correctness_qualified": True,
        "broader_public_suite_correctness_pass": True,
        "candidate_qualified": False,
        "original_verified_passing_case_count": ORIGINAL,
        "original_semantic_mismatch_count": 0,
        "broader_public_verified_passing_case_count": PUBLIC,
        "broader_public_semantic_mismatch_count": 0,
        "static_first_party_non_delegation": "PASS",
        "live_runtime_no_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "clock_samples_by_graph": 0,
        "timing_trials_run": 0,
        "raw_public_case_archives_opened_by_graph": 0,
        "holdout_proposal_files_opened_by_graph": 0,
        "holdout_proposal_files_statted_by_graph": 0,
        "seed_files_opened_by_graph": 0,
        "holdout_cases_opened_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "final_holdout_opened": False,
        "winner_selected": False,
    }, "publish honest separate original and public matching without qualification")
    require(type(summary.get("complete_original_suite_results")) is list
            and len(summary["complete_original_suite_results"]) == len(SUITES)
            and type(summary.get("preserved_c_original_suite_results")) is list
            and len(summary["preserved_c_original_suite_results"]) == len(SUITES),
            "preserve every original Rust and C suite")
    for token in (
        b'role="img"',
        b'aria-labelledby="title description"',
        b"Rust now matches Python in both test sets",
        b"31,237 / 31,237 original checks",
        b"10,434 / 10,434 broader checks",
        b"Zero differences",
        b"16,413 / 31,237",
        b"4,607 / 31,237",
        b"606 differences; unfinished",
        b"At least 1,700 differences",
        b"External regex engines: 0",
        b"External regex packages: 0",
        b"live runtime independence check has not yet been established",
        b"Three independently written engines",
        b"FINAL SPEED: NOT MEASURED",
        b"NO WINNER",
        b"hidden final comparison has not been generated or opened",
    ):
        require(token in result["svg"],
                "the accessible plain-language V104 chart lost " + token.decode("ascii"))
    for forbidden in (b"141557760", b"141,557,760", b"226492416", b"226,492,416"):
        require(all(forbidden not in result[name]
                    for name in ("svg", "inputs", "summary")),
                "a correctness-only chart must not expose or repeat holdout proposals")


def different(value: object) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        return value + " CHANGED"
    if type(value) is list:
        return value + ["CHANGED"]
    if type(value) is dict:
        return {**value, "__v104_hostile": True}
    if value is None:
        return "CHANGED"
    raise Rejected("unsupported public adversarial value")


def self_test(context: dict, output: dict,
              source_sha: str, source_bytes: int, wall: SourceWall) -> int:
    labels = []

    def reject_context(label: str, change) -> None:
        hostile = copy.deepcopy(context)
        change(hostile)
        try:
            verify(hostile)
        except (Rejected, ValueError, TypeError, KeyError, IndexError):
            labels.append(label)
            return
        raise Rejected("hostile current correctness evidence was accepted: " + label)

    for owner in ("previous_inputs", "previous_summary", "original", "public", "audit"):
        for key in sorted(context[owner]):
            reject_context(
                owner + " changed " + key,
                lambda candidate, name=owner, field=key:
                    candidate[name].__setitem__(field, different(candidate[name][field])),
            )
    for index in range(len(SUITES)):
        reject_context(
            f"actual original PASS suite {index} hidden",
            lambda candidate, number=index:
                candidate["original"]["suite_integrity"].pop(number),
        )
        reject_context(
            f"historical C suite {index} hidden",
            lambda candidate, number=index:
                candidate["previous_summary"]["preserved_c_original_suite_results"].pop(
                    number),
        )
        for key in ("suite", "case_execution_denominator", "fully_observed",
                    "actual_worker_started", "mismatch_count",
                    "verified_passing_case_count", "pid"):
            reject_context(
                f"actual original PASS suite {index} changed {key}",
                lambda candidate, number=index, field=key:
                    candidate["original"]["suite_integrity"][number].__setitem__(
                        field,
                        different(candidate["original"]["suite_integrity"][number][field]),
                    ),
            )

    def reject_output(label: str, name: str, change) -> None:
        altered = dict(output)
        value = document(altered[name], "hostile generated V104 public graph")
        change(value)
        altered[name] = canonical(value)
        try:
            verify_outputs(context, altered, source_sha, source_bytes)
        except (Rejected, ValueError, TypeError, KeyError, IndexError):
            labels.append(label)
            return
        raise Rejected("hostile original/public correctness chart was accepted: " + label)

    for name in ("inputs", "summary"):
        for key, value in (
            ("original_case_execution_denominator", ORIGINAL + PUBLIC),
            ("broader_public_case_execution_denominator", PUBLIC - 1),
            ("broader_public_counted_in_original_denominator", True),
            ("qualified_candidate_count", 1),
            ("static_first_party_non_delegation", "FAIL"),
            ("live_runtime_no_delegation", "ESTABLISHED"),
            ("performance", "1.5x"),
            ("memory", "10 bytes"),
            ("timing_trials_run", 1),
            ("raw_public_case_archives_opened_by_graph", 1),
            ("holdout_proposal_files_opened_by_graph", 1),
            ("holdout_proposal_files_statted_by_graph", 1),
            ("seed_files_opened_by_graph", 1),
            ("holdout_cases_opened_by_graph", 1),
            ("hidden_cases_read_by_graph", 1),
            ("final_holdout_opened", True),
            ("winner_selected", True),
        ):
            reject_output(
                name + " changed " + key,
                name,
                lambda candidate, field=key, replacement=value:
                    candidate.__setitem__(field, replacement),
            )
    for key, value in (
        ("candidate_qualified", True),
        ("original_semantic_mismatch_count", 1),
        ("broader_public_semantic_mismatch_count", 1),
        ("historical_c_original_observed_mismatch_count", 0),
        ("historical_zig_original_observed_mismatch_lower_bound", 0),
        ("current_clean_static_v5_finding_count", 1),
        ("historical_canonical_static_v4_finding_count", 0),
    ):
        reject_output(
            "summary dishonestly changed " + key,
            "summary",
            lambda candidate, field=key, replacement=value:
                candidate.__setitem__(field, replacement),
        )

    def reject_wall(label: str, event: str, arguments: tuple) -> None:
        try:
            wall.check(event, arguments)
        except Rejected:
            labels.append(label)
            return
        raise Rejected("hostile graph source-only side effect was accepted: " + label)

    for label, relative in (
        ("canonical Rust adapter", "candidates/rust_candidate.py"),
        ("canonical Rust source", "candidates/rust/src/lib.rs"),
        ("canonical Rust bridge", "candidates/rust/py_bridge.c"),
        ("installed native Rust engine", "candidates/_rust_engine.so"),
        ("raw public candidate results", "experiments/rust_public.raw.json"),
        ("compressed original evidence", "oracle/phase2/evidence/raw.json.gz"),
        ("retired proposal", "oracle/phase3/expanded-sealed-holdout-v2.json"),
        ("successor proposal", "oracle/phase3/expanded-sealed-holdout-v3.json"),
        ("future final seed", "oracle/phase3/final-holdout.seed"),
        ("future hidden final cases", "oracle/phase3/final-hidden-cases.json"),
        ("private source build root", "/tmp/rebar-phase2-native-build-v9-rust-private"),
    ):
        path = relative if relative.startswith("/") else os.path.join(ROOT, relative)
        reject_wall(label, "open", (path, None, os.O_RDONLY | os.O_NOFOLLOW))
    reject_wall("source-only chart output mutation", "open",
                (os.path.join(ROOT, OUTPUT + ".svg"), None,
                 os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW))
    reject_wall("candidate worker execution", "subprocess.Popen", (PYTHON,))
    reject_wall("native matcher load", "ctypes.dlopen", ("_rust_engine.so",))
    reject_wall("regex import", "import", ("re",))
    reject_wall("candidate import", "import", ("candidates.rust_candidate",))
    reject_wall("compressed archive", "import", ("gzip",))
    reject_wall("wall-clock sampling", "time.perf_counter", ())
    reject_wall("network connection", "socket.connect", ("example.invalid",))
    reject_wall("parallel thread", "_thread.start_new_thread", ())
    reject_wall("destructive rename", "os.rename", ("old", "new"))
    reject_wall("nofollow receipt omitted", "open",
                (os.path.join(ROOT, PUBLIC_RECEIPT[0]), None, os.O_RDONLY))
    verify_outputs(context, output, source_sha, source_bytes)
    require(len(labels) >= 400,
            "require broad immutable evidence, honest reporting, and physical-wall tests")
    return len(labels)


def write(path: str, value: bytes) -> None:
    descriptor = os.open(os.path.join(ROOT, path),
                         os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        offset = 0
        while offset < len(value):
            count = os.write(descriptor, value[offset:])
            require(count > 0, "exclusive public chart publication was interrupted")
            offset += count
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", required=True, type=int)
    for name in ("source", "inputs", "summary", "svg"):
        parser.add_argument("--previous-" + name + "-sha256", required=True)
    parser.add_argument("--original-receipt-sha256", required=True)
    parser.add_argument("--public-receipt-sha256", required=True)
    parser.add_argument("--audit-receipt-sha256", required=True)
    return parser.parse_args()


def main() -> int:
    options = arguments()
    require(sys.executable == PYTHON
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.flags.no_site == 1
            and sys.flags.dont_write_bytecode == 1,
            "use only pinned, isolated, no-site, bytecode-disabled CPython 3.14.6")
    own_sha = pin(options.source_sha256, "V104 graph renderer")
    require(type(options.source_bytes) is int
            and 1 <= options.source_bytes <= 262_144,
            "independently pin the complete public V104 renderer bytes")
    for name, owner in PREVIOUS.items():
        require(getattr(options, "previous_" + name + "_sha256") == owner[1],
                "immutable V103 public owner digest changed: " + name)
    require(options.original_receipt_sha256 == ORIGINAL_RECEIPT[1]
            and options.public_receipt_sha256 == PUBLIC_RECEIPT[1]
            and options.audit_receipt_sha256 == AUDIT_RECEIPT[1],
            "require all three separately authenticated actual PASS receipts")
    wall = SourceWall(options.render)
    sys.addaudithook(wall.check)
    accepted = owners()
    source_owner = (SELF, own_sha, options.source_bytes)
    source = read(source_owner, (*accepted, source_owner))
    previous = {name: read(owner, accepted) for name, owner in PREVIOUS.items()}
    context = {
        "goal": read(GOAL, accepted),
        "previous_inputs": document(previous["inputs"], "immutable V103 inputs"),
        "previous_summary": document(previous["summary"], "immutable V103 summary"),
        "previous_svg": previous["svg"],
        "original": document(read(ORIGINAL_RECEIPT, accepted),
                             "actual original Rust PASS"),
        "public": document(read(PUBLIC_RECEIPT, accepted),
                           "actual broader public Rust PASS"),
        "audit": document(read(AUDIT_RECEIPT, accepted),
                          "actual clean first-party static audit PASS"),
    }
    verify(context)
    output = assets(context, own_sha, len(source))
    verify_outputs(context, output, own_sha, len(source))
    controls = (self_test(context, output, own_sha, len(source), wall)
                if options.self_test else 0)
    if options.render:
        for name, extension in (("svg", ".svg"),
                                ("inputs", ".inputs.json"),
                                ("summary", ".json")):
            write(OUTPUT + extension, output[name])
    result = {
        "status": "PASS",
        "mode": "self-test" if options.self_test else (
            "render" if options.render else "verify-frozen-context"
        ),
        "source_sha256": own_sha,
        "source_bytes": len(source),
        "hostile_control_count": controls,
        "original_case_execution_denominator": ORIGINAL,
        "original_verified_passing_case_count": ORIGINAL,
        "original_semantic_mismatch_count": 0,
        "broader_public_case_execution_denominator": PUBLIC,
        "broader_public_verified_passing_case_count": PUBLIC,
        "broader_public_semantic_mismatch_count": 0,
        "candidate_original_oracle_pass": True,
        "broader_public_correctness_pass": True,
        "static_first_party_non_delegation": "PASS",
        "external_regex_packages": 0,
        "external_regex_libraries": 0,
        "external_regex_symbols": 0,
        "live_runtime_no_delegation": "NOT ESTABLISHED",
        "candidate_qualified": False,
        "candidate_source_owners_opened": 0,
        "candidate_workers_started": 0,
        "native_binary_files_opened": 0,
        "raw_public_case_archives_opened": 0,
        "compressed_archives_opened": 0,
        "holdout_proposal_files_opened": 0,
        "holdout_proposal_files_statted": 0,
        "seed_files_opened": 0,
        "holdout_cases_opened": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": UNMEASURED,
        "memory": UNMEASURED,
        "winner_selected": False,
    }
    if options.render:
        result.update({name + "_sha256": digest(value)
                       for name, value in output.items()})
    print(json.dumps(result, ensure_ascii=True, allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Rejected, OSError, ValueError, TypeError) as failure:
        print("REJECTED: " + str(failure), file=sys.stderr)
        raise SystemExit(1)
