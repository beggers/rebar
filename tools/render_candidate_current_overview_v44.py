#!/usr/bin/env python3
"""Show a source-tested Rust fix without hiding its real predecessor failure."""

from __future__ import annotations

import argparse
import ast
import builtins
import copy
import hashlib
import os
from pathlib import Path
import stat
import subprocess
import sys
import tomllib
import types


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v44.py"
OUTPUT = "docs/evidence/candidate-current-overview-v44"
SCHEMA = "rebar-candidate-current-overview-v44"
V43 = {
    "source": (
        "tools/render_candidate_current_overview_v43.py",
        "3b3647a2090fd98e89ea421b2d2a3018983e1014adecf9f0b30731b54ca51e8b",
        67805,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v43.inputs.json",
        "394fb27e12b9a48fbd8bdd353930084891c09118e0cfa49fc90f596124e15017",
        281096,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v43.json",
        "1c5ea146e6d40f0e81f2fe274f2a1a50fe01efdd074ca7ea5b36cca420d16bf0",
        817337,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v43.svg",
        "bee43e78aa59a806927a50e1e807181c62a3f6497d75add1834de2c75fdc546b",
        13359,
    ),
}
V2_HELPER = (
    "tools/run_owned_repaired_rust_original_campaign_v2.py",
    "a6ffce3eb9ff09f27f3e35f84b35b9d1aba6e29dae225c56c036de85e089b7b3",
    143441,
)
V2_ACTUAL_ADAPTER = (
    "candidates/rust_candidate.py",
    "81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c",
    31464,
)
V6_WRONG_ADAPTER = (
    "f8afb6c6e020faad3452b59ceb84abc957ee74d1397397008b3178856abe01a5"
)
# Release only the independently reviewed, all-worker-and-recovery-safe V7.
RUST_V7_PINS_RELEASED = True
RUST_V7 = {
    "source": (
        "tools/run_owned_repaired_rust_original_campaign_v7.py",
        "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104",
        505616,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V7.md",
        "0b5182a7eee74e586839abc3a0e8bdd122bac248e9cb3b76c603c5add9281840",
        8433,
    ),
    "contract": (
        "oracle/phase2/repaired-rust-original-campaign-v7.json",
        "9c8e85dcc5dcf0a00953b36dd02c29c2ab7b1ed0b4281eb27f6693c058d155e5",
        46385,
    ),
}
PUBLIC_OWNERS = {
    "module": (
        "rebar.py",
        "289769bd637ea525ae7e71d263377e15c0f394ba20619c11b98e266f57fcc34f",
        212,
    ),
    "project": (
        "pyproject.toml",
        "7d50e8c6c2bc76a0e3ddcac6b5f157b013bcfd76944fdeb2c1c81e0181ae7825",
        224,
    ),
}
PUBLIC_STATUS = "UNQUALIFIED ZIG PROTOTYPE; NOT A WINNER"
V7_CURRENT_ACCOUNTING = {
    "actual_authenticated_reference_count_before_new_campaign": 171,
    "actual_evidence_owner_count_before_new_campaign": 166,
    "actual_v6_failure_evidence_owners_created": 2,
    "authenticated_reference_lower_bound_before_new_campaign": 171,
    "evidence_owner_lower_bound_before_new_campaign": 166,
    "future_campaign_evidence_owners_created": 0,
    "historical_pre_failure_evidence_owner_lower_bound": 164,
    "historical_pre_failure_reference_lower_bound": 169,
    "historical_v35_authenticated_reference_count": 164,
    "historical_v35_evidence_owner_count": 159,
    "later_append_only_evidence_allowed": True,
    "qualified_candidate_count": 0,
}
V7_FUTURE_PUBLICATION = {
    "actual_original_suite_worker_count": 13,
    "actual_worker_and_recovery_callables_source_wall_tested": True,
    "all_actual_mismatches_preserved": True,
    "all_original_case_records_preserved": True,
    "archive_and_receipt_distinct_fresh_owner_inodes": True,
    "archive_owner_mode": "0600",
    "authorized_run_entry_failure_retains_actual_effect_ledger": True,
    "both_owner_absolute_paths_are_independently_authenticated": True,
    "complete_publication_exercised_inside_source_wall": True,
    "controller_v13_source_build_archive_effect_ledger_required": True,
    "controller_v13_source_build_archive_read_count": 1,
    "corrected_original_reference_inputs_unchanged": True,
    "current_evidence_owner_lower_bound_before_publication": 166,
    "current_history_reference_lower_bound_before_publication": 171,
    "deterministic_single_member_zero_time_gzip": True,
    "distinct_positive_worker_process_ids_required": True,
    "historical_helper_module_verified_before_archive": True,
    "historical_helper_source_verified_before_archive": True,
    "maximum_complete_worker_stderr_bytes": 4194304,
    "maximum_complete_worker_stdout_bytes": 33554432,
    "maximum_failure_stream_prefix_bytes": 65536,
    "maximum_streamed_public_report_bytes": 33554432,
    "maximum_worker_compressed_observation_bytes": 16777216,
    "new_distinct_durable_publication_owner_count": 2,
    "numeric_total_mismatches_require_all_thirteen_observations": True,
    "only_controller_retains_v13_source_build_archive": True,
    "original_suite_worker_v13_source_build_archive_reads": 0,
    "original_suite_workers_retain_v13_source_build_archive": False,
    "oversized_worker_stream_retains_full_size_and_sha256": True,
    "partial_total_mismatches": "NOT MEASURED",
    "public_recovery_retain_v13_source_build_archive": False,
    "public_recovery_succeeds_without_source_build_archive": True,
    "public_recovery_v13_source_build_archive_reads": 0,
    "publication_failure_never_claims_resulting_counts": True,
    "publication_failure_never_reports_source_only_zero_effects": True,
    "publication_only_after_all_four_original_inodes_restored": True,
    "publication_pass_means": "DURABLE PUBLICATION ONLY",
    "receipt_owner_digest_size_uid_and_single_link_verified": True,
    "receipt_owner_mode": "0600",
    "reference_oracle_rerun_allowed": False,
    "resulting_counts_require_two_distinct_durable_owners": True,
    "resulting_evidence_owner_lower_bound_after_both_owners": 168,
    "resulting_history_reference_lower_bound_after_both_owners": 173,
    "source_build_archive_actual_inflation_count_retained": True,
    "source_build_archive_actual_read_count_retained": True,
    "source_build_archive_compressed_bytes_retained": True,
    "source_build_archive_effects_survive_entry_failure": True,
    "source_build_archive_inflation_attempt_recorded_before_inflation": True,
    "source_build_archive_read_attempt_recorded_before_read": True,
    "source_build_archive_uncompressed_bytes_and_sha256_retained": True,
    "started_worker_pid_retained_before_communication": True,
    "streaming_archive_owner_relative_is_evidence_basename": True,
    "truncated_worker_stream_never_counts_as_complete": True,
    "unledgered_retained_build_context_rejected_before_any_read": True,
    "v2_receipt_owner_relative_is_repository_evidence_path": True,
    "worker_attempts_starts_and_complete_observations_are_distinct": True,
    "worker_launch_attempt_recorded_before_spawn": True,
}
V7_PUBLISHED_V43_FIELDS = {
    "overview_version": 43,
    "authenticated_evidence_owner_lower_bound": 166,
    "authenticated_history_reference_lower_bound": 171,
    "actual_v6_controller_status": "FAIL",
    "actual_v6_controller_process_count": 1,
    "actual_v6_candidate_workers": 0,
    "actual_v6_native_activations": 0,
    "actual_v6_source_build_archive_read_count": 1,
    "actual_v6_source_build_archive_gzip_inflation_count": 1,
    "actual_v6_source_build_archive_compressed_bytes": 108985,
    "actual_v6_source_build_archive_uncompressed_bytes": 760477,
    "actual_v6_controller_ledger_omits_archive_effect": True,
    "actually_runnable_candidate_family_count": 0,
    "qualified_candidate_count": 0,
    "performance": "NOT MEASURED",
    "holdout": "NOT OPENED",
}
V7_STATUS = (
    "RUST V7 HELPER PREFLIGHT SOURCE FROZEN AND SOURCE-TESTED; "
    "ACTUAL CANDIDATE NOT RUN"
)
V7_BLOCK_REASON = (
    "The independently frozen version-7 historical-helper correction is "
    "source-tested only. It has not started a candidate, opened a build "
    "archive or established runtime independence. The one real version-6 "
    "controller failure and its omitted build-archive effect remain "
    "preserved. C remains inactive and the other four source families "
    "have no corrected runnable worker."
)


def load_v43() -> tuple[types.ModuleType, types.ModuleType,
                        types.ModuleType, types.ModuleType, types.ModuleType]:
    path, fingerprint, size = V43["source"]
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags)
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != os.geteuid()
            or before.st_nlink != 1
            or stat.S_IMODE(before.st_mode) != 0o600
            or before.st_size != size
        ):
            raise ValueError("reject a substituted, shared or nonprivate V43 source")
        pieces: list[bytes] = []
        remaining = size
        while remaining:
            piece = os.read(descriptor, min(262144, remaining))
            if not piece:
                raise ValueError("reject a truncated real-failure V43 source")
            pieces.append(piece)
            remaining -= len(piece)
        if os.read(descriptor, 1):
            raise ValueError("reject appended bytes after immutable V43 source")
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        if (
            hashlib.sha256(raw).hexdigest() != fingerprint
            or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        ):
            raise ValueError("reject V43 source replacement during authentication")
    finally:
        os.close(descriptor)
    previous = types.ModuleType("_rebar_pushed_actual_rust_failure_v43_for_v44")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    v42, v41, v40, base = previous.load_v42()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v43"
        and previous.SELF == path,
        "load only the genuinely pushed actual-failure V43 source",
    )
    return previous, v42, v41, v40, base


def authenticate_v43(previous: types.ModuleType, v42: types.ModuleType,
                     v41: types.ModuleType, v40: types.ModuleType,
                     base: types.ModuleType) -> tuple[dict, dict]:
    for owner in V43.values():
        base.read_owner(*owner, private=True)
    inputs_raw, _ = base.read_owner(*V43["inputs"], private=True)
    summary_raw, _ = base.read_owner(*V43["summary"], private=True)
    svg_raw, _ = base.read_owner(*V43["svg"], private=True)
    inputs = base.document(inputs_raw, "complete actual-failure V43 inputs")
    summary = base.document(summary_raw, "complete actual-failure V43 summary")
    snapshot = summary.get("snapshot")
    previous.validate_snapshot(v42, v41, v40, base, snapshot)
    base.need(
        summary.get("schema") == "rebar-candidate-current-overview-v43-summary"
        and summary.get("version") == 43
        and summary.get("status") == "PASS"
        and summary.get("source") == base.pin(*V43["source"])
        and summary.get("inputs") == base.pin(*V43["inputs"])
        and summary.get("svg") == base.pin(*V43["svg"])
        and inputs.get("schema") == "rebar-candidate-current-overview-v43-inputs"
        and inputs.get("version") == 43
        and inputs.get("renderer") == base.pin(*V43["source"])
        and svg_raw == previous.make_svg(
            v42, v41, v40, base, snapshot,
            V43["source"][1], V43["inputs"][1],
        ),
        "authenticate all four genuine V43 owners without opening any archive",
    )
    actual = previous.authenticate_failure(
        base, previous.FAILURE[1], previous.OBSERVATION[1],
    )
    previous.validate_failure_proof(base, actual)
    base.need(snapshot.get("actual_rust_preflight_failure") == actual,
              "bind V44 to both complete original Rust failure observations")
    return summary, inputs


def validate_helper_preflight(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict,
              "reject a missing immutable V2 AST helper preflight")
    assert isinstance(proof, dict)
    owner = proof.get("helper_source")
    base.need(
        type(owner) is dict
        and owner.get("path") == V2_HELPER[0]
        and owner.get("sha256") == V2_HELPER[1]
        and owner.get("bytes") == V2_HELPER[2]
        and owner.get("mode") == "0600"
        and owner.get("nlink") == 1
        and type(owner.get("inode")) is int
        and owner["inode"] > 0
        and proof.get("actual_v2_adapter") == base.pin(*V2_ACTUAL_ADAPTER)
        and proof.get("incorrect_v6_adapter_sha256") == V6_WRONG_ADAPTER
        and V2_ACTUAL_ADAPTER[1] != V6_WRONG_ADAPTER
        and proof.get("immutable_helper_extracted_without_execution") is True
        and proof.get("helper_preflight_before_build_archive") is True
        and type(proof.get("helper_preflight_line")) is int
        and proof["helper_preflight_line"] > 0
        and type(proof.get("build_context_line")) is int
        and proof["build_context_line"] > proof["helper_preflight_line"]
        and proof.get("candidate_target_reads") == 0
        and proof.get("candidate_workers") == 0
        and proof.get("reference_archive_reads") == 0
        and proof.get("matching_archive_reads") == 0
        and proof.get("source_build_archive_reads") == 0,
        "require true V2 AST adapter 81089 and V7 helper guard before archive",
    )


def authenticate_helper_preflight(base: types.ModuleType,
                                  v7_source_raw: bytes) -> dict:
    helper_raw, owner = base.read_owner(*V2_HELPER, private=True)
    try:
        helper_tree = ast.parse(
            helper_raw, filename=str(ROOT / V2_HELPER[0]),
        )
        repaired = [
            item for item in helper_tree.body
            if isinstance(item, ast.AnnAssign)
            and isinstance(item.target, ast.Name)
            and item.target.id == "REPAIRED_SOURCE_OWNERS"
        ]
        base.need(
            len(repaired) == 1 and repaired[0].value is not None,
            "require the unique immutable V2 repaired-owner AST assignment",
        )
        values = ast.literal_eval(repaired[0].value)
        base.need(
            type(values) is tuple and len(values) == 9
            and type(values[0]) is tuple
            and values[0] == V2_ACTUAL_ADAPTER,
            "extract only the true 81089 historical V2 adapter source tuple",
        )
        candidate = ast.parse(
            v7_source_raw, filename=str(ROOT / RUST_V7["source"][0]),
        )
        campaigns = [
            item for item in candidate.body
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            and item.name == "run_campaign"
        ]
        base.need(len(campaigns) == 1,
                  "require exactly one genuine V7 candidate campaign definition")
        calls = [
            (
                node.lineno,
                node.func.id
                if isinstance(node.func, ast.Name)
                else node.func.attr
                if isinstance(node.func, ast.Attribute)
                else "",
            )
            for node in ast.walk(campaigns[0])
            if isinstance(node, ast.Call)
        ]
        helper_lines = [
            line for line, name in calls
            if name in (
                "patched_v2_helpers",
                "preflight_patched_v2_helpers",
                "preflight_v2_helpers",
                "verify_historical_helper_preflight",
                "verify_immutable_historical_helpers",
            )
        ]
        contexts = [
            line for line, name in calls if name == "verify_context"
        ]
        base.need(
            len(helper_lines) == 1 and len(contexts) == 1
            and helper_lines[0] < contexts[0],
            "run the exact immutable V2 helper guard before retained V13 build",
        )
    except (SyntaxError, UnicodeError, TypeError, ValueError) as error:
        raise base.GraphError(
            "reject an unverified or executable V2/V7 helper AST",
        ) from error
    proof = {
        "helper_source": owner,
        "actual_v2_adapter": base.pin(*V2_ACTUAL_ADAPTER),
        "incorrect_v6_adapter_sha256": V6_WRONG_ADAPTER,
        "immutable_helper_extracted_without_execution": True,
        "helper_preflight_before_build_archive": True,
        "helper_preflight_line": helper_lines[0],
        "build_context_line": contexts[0],
        "candidate_target_reads": 0,
        "candidate_workers": 0,
        "reference_archive_reads": 0,
        "matching_archive_reads": 0,
        "source_build_archive_reads": 0,
    }
    validate_helper_preflight(base, proof)
    return proof


def validate_v7_contract(base: types.ModuleType, document: object) -> None:
    base.need(type(document) is dict,
              "reject a missing separately frozen Rust V7 machine contract")
    assert isinstance(document, dict)
    status = document.get("status")
    base.need(
        type(document.get("schema")) is str
        and "repaired-rust-original-campaign-v7" in document["schema"]
        and document.get("version") == 7
        and document.get("family") == "rust"
        and type(status) is str
        and "SOURCE FROZEN" in status
        and "NOT RUN" in status
        and document.get("source")
        == {"path": RUST_V7["source"][0], "sha256": RUST_V7["source"][1]}
        and document.get("protocol")
        == {"path": RUST_V7["protocol"][0], "sha256": RUST_V7["protocol"][1]},
        "require exact independently released Rust V7 source and no candidate run",
    )
    python = document.get("pinned_cpython")
    original = document.get("original_oracle")
    base.need(
        type(python) is dict
        and python.get("version") == "3.14.6"
        and python.get("path") == base.PYTHON
        and python.get("sha256") == base.PYTHON_SHA
        and type(original) is dict
        and original.get("case_execution_denominator") == 31237
        and original.get("suite_count") == 13
        and original.get("named_private_waiver_count") == 13
        and original.get("candidate_wrapper_allowed") is False
        and original.get("cross_family_matching_allowed") is False
        and original.get("external_regex_dependency_allowed") is False
        and original.get("stdlib_re_fallback_allowed") is False,
        "freeze only the complete from-scratch original Rust public contract",
    )
    suites = original.get("source_ordered_suites")
    base.need(
        type(suites) is list and len(suites) == 13
        and all(
            type(row) is dict
            and type(row.get("case_execution_count")) is int
            and row["case_execution_count"] > 0
            for row in suites
        )
        and sum(row["case_execution_count"] for row in suites) == 31237,
        "retain all thirteen complete original V7 correctness suites",
    )
    accounting = document.get("current_historical_accounting")
    publication = document.get("future_lossless_publication")
    published = document.get("published_current_v43_overview")
    base.need(
        type(accounting) is dict and accounting == V7_CURRENT_ACCOUNTING
        and type(publication) is dict
        and publication == V7_FUTURE_PUBLICATION
        and type(published) is dict
        and all(
            published.get(field) == expected
            for field, expected in V7_PUBLISHED_V43_FIELDS.items()
        )
        and published.get("owners") == {
            role: base.pin(*owner) for role, owner in V43.items()
        },
        "require the complete receipt-path-safe V7 source-tested publication "
        "contract: current 166/171; future 168/173 only after two durable "
        "distinct owners; exact unchanged V43 and actual V6 archive effect",
    )
    effects = document.get("source_only_effects")
    base.need(
        type(effects) is dict
        and all(
            type(effects.get(name)) is int and effects[name] == 0
            for name in (
                "actual_candidate_imports", "actual_candidate_workers",
                "actual_native_activations", "actual_native_library_loads",
                "actual_reference_workers", "actual_source_builds",
                "benchmark_files_read", "canonical_target_reads",
                "canonical_target_replacements", "canonical_target_stats",
                "clock_samples", "hidden_cases_read", "threads_started",
                "timing_trials_run", "workspace_mutations",
            )
        )
        and effects.get("candidate_correctness") == "NOT MEASURED"
        and effects.get("candidate_qualified") is False
        and effects.get("holdout") == "NOT OPENED"
        and effects.get("performance") == "NOT MEASURED"
        and effects.get("memory") == "NOT MEASURED"
        and effects.get("undefined_behavior") == "NOT MEASURED"
        and effects.get("winner_selected") is False,
        "a V7 helper source freeze cannot activate or qualify a replacement",
    )


def validate_v7_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict,
              "reject a fabricated Rust V7 source-tested helper repair")
    assert isinstance(proof, dict)
    base.need(
        proof.get("schema") == SCHEMA + "-authenticated-rust-v7-source-freeze"
        and proof.get("status") == V7_STATUS
        and proof.get("candidate_family") == "rust"
        and proof.get("version") == 7
        and proof.get("actual_candidate_workers") == 0
        and proof.get("actual_native_activations") == 0
        and proof.get("actual_reference_workers") == 0
        and proof.get("actual_source_build_archive_reads") == 0
        and proof.get("actual_matching_archive_reads") == 0
        and proof.get("actual_candidate_matching") == "NOT RUN"
        and proof.get("actually_runnable_candidate_family_count") == 0
        and proof.get("candidate_qualified") is False
        and proof.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and proof.get("performance") == "NOT MEASURED"
        and proof.get("memory") == "NOT MEASURED"
        and proof.get("holdout") == "NOT OPENED",
        "never confuse the V7 source-tested helper with an actual Rust run",
    )
    for role, expected in RUST_V7.items():
        owner = proof.get(role)
        base.need(
            type(owner) is dict
            and owner.get("path") == expected[0]
            and owner.get("sha256") == expected[1]
            and owner.get("bytes") == expected[2]
            and owner.get("mode") == "0600"
            and owner.get("nlink") == 1
            and type(owner.get("inode")) is int and owner["inode"] > 0,
            "authenticate the entire released private Rust V7 " + role,
        )
    preflight = proof.get("immutable_v2_helper_preflight")
    validate_helper_preflight(base, preflight)
    contract = proof.get("complete_frozen_contract")
    validate_v7_contract(base, contract)
    binding = base.digest(base.canonical({
        "source": proof["source"],
        "protocol": proof["protocol"],
        "contract": proof["contract"],
        "complete_frozen_contract": contract,
        "immutable_v2_helper_preflight": preflight,
    }))
    base.need(
        proof.get("complete_v7_source_binding_sha256") == binding,
        "bind all three complete independently released V7 source owners",
    )


def authenticate_v7(base: types.ModuleType, source_pin: str,
                    protocol_pin: str, contract_pin: str) -> dict:
    base.need(
        RUST_V7_PINS_RELEASED is True,
        "refuse unpublished or independently unreviewed Rust V7 source evidence",
    )
    for value, role in (
        (source_pin, "source"),
        (protocol_pin, "protocol"),
        (contract_pin, "contract"),
    ):
        base.need(
            base.checked(value, "exact reviewed Rust V7 " + role)
            == RUST_V7[role][1],
            "reject a missing or guessed Rust V7 " + role,
        )
    owners: dict[str, dict] = {}
    contract_raw = b""
    source_raw = b""
    for role, expected in RUST_V7.items():
        raw, owner = base.read_owner(*expected, private=True)
        owners[role] = owner
        if role == "contract":
            contract_raw = raw
        elif role == "source":
            source_raw = raw
    contract = base.document(contract_raw, "complete reviewed Rust V7 contract")
    validate_v7_contract(base, contract)
    preflight = authenticate_helper_preflight(base, source_raw)
    proof = {
        "schema": SCHEMA + "-authenticated-rust-v7-source-freeze",
        "status": V7_STATUS,
        **owners,
        "complete_frozen_contract": contract,
        "immutable_v2_helper_preflight": preflight,
        "candidate_family": "rust",
        "version": 7,
        "actual_candidate_workers": 0,
        "actual_native_activations": 0,
        "actual_reference_workers": 0,
        "actual_source_build_archive_reads": 0,
        "actual_matching_archive_reads": 0,
        "actual_candidate_matching": "NOT RUN",
        "actually_runnable_candidate_family_count": 0,
        "candidate_qualified": False,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }
    proof["complete_v7_source_binding_sha256"] = base.digest(
        base.canonical({
            "source": owners["source"],
            "protocol": owners["protocol"],
            "contract": owners["contract"],
            "complete_frozen_contract": contract,
            "immutable_v2_helper_preflight": preflight,
        }),
    )
    validate_v7_proof(base, proof)
    return proof


def validate_public_entrypoint(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict,
              "reject an invented public rebar compatibility result")
    assert isinstance(proof, dict)
    expected = {
        "schema": SCHEMA + "-static-public-entrypoint",
        "status": PUBLIC_STATUS,
        "audit_method":
            "BOUNDED COMPLETE SOURCE AST AND TOML; NO IMPORT OR EXECUTION",
        "selected_candidate_family": "zig",
        "selected_historical_zig_mismatch_count": 1764,
        "public_module_version_status": "FAIL/MISSING",
        "public_module_qualified": False,
        "project_package_mode": False,
        "packaged_artifact": "NOT MEASURED",
        "installation_status": "NOT MEASURED",
        "supplementary_signature_check_count": 50,
        "supplementary_signature_candidate_status": "NOT MEASURED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "actual_imports_by_graph": 0,
        "actual_native_loads_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "candidate_correctness": "NOT MEASURED",
        "winner_selected": False,
    }
    base.need(
        all(proof.get(key) == value for key, value in expected.items()),
        "never present the actual Zig-star public shim as a qualified, "
        "versioned, installed or measured re replacement",
    )
    for role, pin in PUBLIC_OWNERS.items():
        owner = proof.get(role)
        base.need(
            type(owner) is dict
            and owner.get("path") == pin[0]
            and owner.get("sha256") == pin[1]
            and owner.get("bytes") == pin[2]
            and owner.get("mode") == "0600"
            and owner.get("nlink") == 1
            and owner.get("uid") == os.geteuid()
            and type(owner.get("device")) is int
            and owner["device"] > 0
            and type(owner.get("inode")) is int
            and owner["inode"] > 0,
            "authenticate the complete tracked first-party public " + role,
        )
    base.need(
        proof.get("complete_public_entrypoint_binding_sha256")
        == base.digest(base.canonical({
            "module": proof["module"],
            "project": proof["project"],
            **expected,
        })),
        "bind complete tracked public owner identities to every source-only "
        "unqualified-Zig and missing-public-version audit fact",
    )


def public_entrypoint_fields(proof: dict) -> dict:
    return {
        "public_entrypoint_static_audit": copy.deepcopy(proof),
        "public_entrypoint_status": PUBLIC_STATUS,
        "public_entrypoint_module_sha256": PUBLIC_OWNERS["module"][1],
        "public_entrypoint_project_sha256": PUBLIC_OWNERS["project"][1],
        "public_entrypoint_selected_family": "zig",
        "public_entrypoint_historical_zig_mismatch_count": 1764,
        "public_entrypoint_module_version_status": "FAIL/MISSING",
        "public_entrypoint_qualified": False,
        "public_entrypoint_package_mode": False,
        "public_entrypoint_packaged_artifact": "NOT MEASURED",
        "public_entrypoint_installation_status": "NOT MEASURED",
        "public_entrypoint_actual_imports_by_graph": 0,
        "public_entrypoint_actual_native_loads_by_graph": 0,
        "public_entrypoint_runtime_no_delegation": "NOT ESTABLISHED",
        "supplementary_signature_check_count": 50,
        "supplementary_signature_candidate_status": "NOT MEASURED",
        "public_entrypoint_winner_selected": False,
    }


def authenticate_public_entrypoint(
        base: types.ModuleType,
        module_sha: str,
        module_bytes: int,
        project_sha: str,
        project_bytes: int,
        ) -> dict:
    for role, supplied_sha, supplied_bytes in (
        ("module", module_sha, module_bytes),
        ("project", project_sha, project_bytes),
    ):
        base.need(
            base.checked(supplied_sha, "exact tracked public " + role)
            == PUBLIC_OWNERS[role][1]
            and type(supplied_bytes) is int
            and supplied_bytes == PUBLIC_OWNERS[role][2],
            "require the complete independently supplied public " + role,
        )
    module_raw, module_owner = base.read_owner(
        *PUBLIC_OWNERS["module"], private=True,
    )
    project_raw, project_owner = base.read_owner(
        *PUBLIC_OWNERS["project"], private=True,
    )
    try:
        tree = ast.parse(module_raw, filename=str(ROOT / "rebar.py"))
        imports = [
            node for node in tree.body if isinstance(node, ast.ImportFrom)
        ]
        shapes = [
            (
                node.module,
                node.level,
                tuple((alias.name, alias.asname) for alias in node.names),
            )
            for node in imports
        ]
        project = tomllib.loads(project_raw.decode("utf-8"))
    except (SyntaxError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise base.GraphError(
            "reject incomplete or executable public entrypoint source",
        ) from error
    base.need(
        len(tree.body) == 4
        and isinstance(tree.body[0], ast.Expr)
        and isinstance(tree.body[0].value, ast.Constant)
        and type(tree.body[0].value.value) is str
        and shapes == [
            ("candidates.zig_candidate", 0, (("*", None),)),
            (
                "candidates.zig_candidate", 0,
                (("DEBUG", None), ("Scanner", None)),
            ),
            ("candidates.zig_candidate", 0, (("__all__", None),)),
        ]
        and not any(
            isinstance(node, ast.Name) and node.id == "__version__"
            or isinstance(node, ast.alias)
            and (node.name == "__version__" or node.asname == "__version__")
            for node in ast.walk(tree)
        )
        and type(project) is dict
        and project.get("project") == {
            "name": "rebar-experiment",
            "version": "0.0.0",
            "description":
                "Falsifiable, phase-gated experiment for from-scratch "
                "Python re replacements",
            "requires-python": ">=3.14,<3.15",
            "dependencies": [],
        }
        and project.get("tool") == {"uv": {"package": False}},
        "statically prove the genuine tracked public shim star-exports only "
        "historically failing Zig, omits __version__, and disables packaging",
    )
    proof = {
        "schema": SCHEMA + "-static-public-entrypoint",
        "status": PUBLIC_STATUS,
        "module": module_owner,
        "project": project_owner,
        "audit_method":
            "BOUNDED COMPLETE SOURCE AST AND TOML; NO IMPORT OR EXECUTION",
        "selected_candidate_family": "zig",
        "selected_historical_zig_mismatch_count": 1764,
        "public_module_version_status": "FAIL/MISSING",
        "public_module_qualified": False,
        "project_package_mode": False,
        "packaged_artifact": "NOT MEASURED",
        "installation_status": "NOT MEASURED",
        "supplementary_signature_check_count": 50,
        "supplementary_signature_candidate_status": "NOT MEASURED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "actual_imports_by_graph": 0,
        "actual_native_loads_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "candidate_correctness": "NOT MEASURED",
        "winner_selected": False,
    }
    proof["complete_public_entrypoint_binding_sha256"] = base.digest(
        base.canonical({
            "module": module_owner,
            "project": project_owner,
            **{
                key: value for key, value in proof.items()
                if key not in ("module", "project")
            },
        }),
    )
    validate_public_entrypoint(base, proof)
    return proof


def source_fix_fields(proof: dict) -> dict:
    return {
        "corrected_rust_v7_source_freeze": copy.deepcopy(proof),
        "corrected_rust_v7_source_status": V7_STATUS,
        "corrected_rust_v7_source_sha256": RUST_V7["source"][1],
        "corrected_rust_v7_protocol_sha256": RUST_V7["protocol"][1],
        "corrected_rust_v7_contract_sha256": RUST_V7["contract"][1],
        "corrected_rust_v7_candidate_matching_status": "NOT RUN",
        "corrected_rust_v7_actual_candidate_workers": 0,
        "corrected_rust_v7_actual_native_activations": 0,
        "corrected_rust_v7_helper_preflight_before_build_archive": True,
        "corrected_rust_v7_publication_source_tested_only": True,
        "corrected_rust_v7_current_evidence_owner_lower_bound": 166,
        "corrected_rust_v7_current_history_reference_lower_bound": 171,
        "corrected_rust_v7_future_publication_distinct_owner_count": 2,
        "corrected_rust_v7_future_evidence_owner_lower_bound": 168,
        "corrected_rust_v7_future_history_reference_lower_bound": 173,
        "corrected_rust_v7_archive_uses_evidence_basename": True,
        "corrected_rust_v7_v2_receipt_uses_repository_evidence_path": True,
        "corrected_rust_v7_future_results_require_all_thirteen_workers": True,
        "corrected_rust_v7_all_worker_and_recovery_source_wall_tested": True,
        "corrected_rust_v7_only_controller_retains_source_build": True,
        "corrected_rust_v7_controller_ledgered_source_build_read_count": 1,
        "corrected_rust_v7_original_worker_source_build_read_count": 0,
        "corrected_rust_v7_public_recovery_source_build_read_count": 0,
        "corrected_rust_v7_unledgered_retained_context_rejected": True,
        "corrected_rust_v7_immutable_v2_helper_sha256": V2_HELPER[1],
        "corrected_rust_v7_immutable_v2_adapter_sha256":
            V2_ACTUAL_ADAPTER[1],
        "superseded_rust_v6_wrong_historical_adapter_sha256":
            V6_WRONG_ADAPTER,
        "corrected_rust_v7_source_build_archive_reads": 0,
        "corrected_rust_v7_matching_archive_reads": 0,
        "corrected_rust_v7_candidate_qualified": False,
        "corrected_rust_v7_runtime_no_delegation": "NOT ESTABLISHED",
        "corrected_rust_v7_measured_mismatch_reduction": "NOT MEASURED",
        "corrected_rust_v7_measured_speedup": "NOT MEASURED",
        "superseded_rust_v6_source_remains_immutable": True,
        "actual_rust_v6_preflight_failure_preserved": True,
        "frozen_corrected_runner_source_family_count": 2,
        "frozen_corrected_runner_source_families": ["c", "rust"],
        "dedicated_corrected_runnable_family_count": 0,
        "dedicated_corrected_runnable_families": [],
        "actually_runnable_candidate_family_count": 0,
        "actually_runnable_candidate_families": [],
        "first_party_source_inventory_family_count": 6,
        "other_corrected_candidate_family_count": 4,
        "pending_corrected_candidate_families":
            ["zig", "cpp", "go", "fortran"],
        "corrected_rust_matching_status": "NOT RUN",
        "corrected_c_matching_status": "NOT RUN",
        "qualified_candidate_count": 0,
        "reference_archive_gzip_inflation_count": 0,
        "matching_archive_gzip_inflation_count": 0,
        "source_build_archive_gzip_inflation_count_by_graph": 0,
        "candidate_matching_archives_opened_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    }


def validate_snapshot(previous: types.ModuleType, v42: types.ModuleType,
                      v41: types.ModuleType, v40: types.ModuleType,
                      base: types.ModuleType, snapshot: object) -> None:
    base.need(type(snapshot) is dict,
              "reject a missing real-failure and source-tested V7 graph")
    assert isinstance(snapshot, dict)
    previous.validate_snapshot(v42, v41, v40, base, snapshot)
    v7 = snapshot.get("corrected_rust_v7_source_freeze")
    validate_v7_proof(base, v7)
    assert isinstance(v7, dict)
    for key, expected in source_fix_fields(v7).items():
        base.need(
            snapshot.get(key) == expected,
            "reject an invented or omitted V7 source-only result: " + key,
        )
    public = snapshot.get("public_entrypoint_static_audit")
    validate_public_entrypoint(base, public)
    assert isinstance(public, dict)
    for key, expected in public_entrypoint_fields(public).items():
        base.need(
            snapshot.get(key) == expected,
            "reject a forged or hidden unqualified public entrypoint: " + key,
        )
    base.need(
        snapshot.get("actual_rust_controller_status") == "FAIL"
        and snapshot.get("actual_rust_controller_process_count") == 1
        and snapshot.get("actual_rust_attempted_suite_count") == 0
        and snapshot.get("actual_rust_started_suite_count") == 0
        and snapshot.get("actual_rust_completed_suite_count") == 0
        and snapshot.get("actual_rust_candidate_workers") == 0
        and snapshot.get("actual_rust_native_activations") == 0
        and snapshot.get("actual_rust_source_build_archive_read_count") == 1
        and snapshot.get("actual_rust_source_build_archive_gzip_inflation_count")
        == 1
        and snapshot.get("actual_rust_source_build_archive_compressed_bytes")
        == 108985
        and snapshot.get("actual_rust_source_build_archive_uncompressed_bytes")
        == 760477
        and snapshot.get(
            "actual_rust_controller_ledger_omits_source_build_archive_effect",
        ) is True
        and snapshot.get("actual_rust_matching_archive_read_count") == 0
        and snapshot.get("actual_rust_reference_archive_read_count") == 0
        and snapshot.get("actual_rust_semantic_mismatch_count") == "NOT MEASURED"
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 166
        and snapshot.get("authenticated_history_reference_lower_bound") == 171
        and snapshot.get("full_case_denominator") == 31237
        and snapshot.get("suite_count") == 13
        and snapshot.get("private_waiver_count") == 13
        and snapshot.get("corrected_reference_actual_worker_count") == 2
        and snapshot.get("corrected_reference_process_ids") == [81, 82]
        and snapshot.get("zig_scanner_phrase_prospective_case_count") == 64
        and snapshot.get("zig_scanner_phrase_correction_applied") is False
        and snapshot.get("zig_scanner_phrase_corrected_matching_status")
        == "NOT RUN",
        "preserve the actual V6 failure, exact old source-build effect and oracle",
    )


def make_svg(previous: types.ModuleType, v42: types.ModuleType,
             v41: types.ModuleType, v40: types.ModuleType,
             base: types.ModuleType, snapshot: dict,
             source: str, inputs: str) -> bytes:
    validate_snapshot(previous, v42, v41, v40, base, snapshot)
    visible = previous.make_svg(
        v42, v41, v40, base, snapshot, source, inputs,
    ).decode("utf-8")
    visible = visible.replace("v43-title", "v44-title")
    visible = visible.replace("v43-description", "v44-description")
    replacements = (
        (
            "baseline passes; Rust preflight fails before any candidate test</title>",
            "baseline passes; public Zig import is unqualified; "
            "Rust fix is source-tested only</title>",
            "honest source-only V7 title",
        ),
        (
            "One real Rust controller failed its historical helper check before "
            "activating a candidate or starting a test; C, Zig, Go, C++ and "
            "Fortran remain untested.",
            "The actual V6 Rust controller failed its historical helper check "
            "before activating a candidate. A separately frozen V7 helper fix "
            "passes all-worker and recovery source-only tests; no V7 "
            "candidate, C, Zig, Go, C++ or Fortran has been run. The actual "
            "public Zig prototype is unqualified, has no __version__, and "
            "has packaging disabled.",
            "actual V6 failure versus untested V7",
        ),
        (
            "Six first-party source designs; two frozen runner sources; "
            "zero actually runnable replacements.",
            "Six first-party source designs; two frozen runner sources; "
            "public Zig prototype unqualified; zero runnable replacements.",
            "lay-readable zero-runnable V7 status",
        ),
        (
            "RUST PREFLIGHT FAILED — ZERO CANDIDATE TEST WORKERS STARTED",
            "ACTUAL RUST V6 PREFLIGHT FAILED — ZERO TEST WORKERS STARTED",
            "preserve the actual immutable V6 failure",
        ),
        (
            "The actual Rust controller failed before any of the 31,237 "
            "compatibility tests. C matching has not run.",
            "The actual V6 Rust controller failed before any of 31,237 "
            "tests. The new V7 fix is source-tested only; C has not run.",
            "source-tested correction is not a compatibility result",
        ),
        (
            "1. Overall: Rust preflight failed; no replacement is runnable",
            "1. Overall: new Rust source fix; no replacement is runnable",
            "overall candidate state remains zero runnable",
        ),
        (
            "Two runner sources are frozen, but Rust preflight failed and "
            "zero candidates are runnable.",
            "Two runner sources are frozen. V6 really failed; V7 is "
            "source-tested only; zero candidates are runnable.",
            "frozen runner source is not runtime compatibility",
        ),
    )
    for before, after, label in replacements:
        visible = previous.replace_once(base, visible, before, after, label)
    visible = previous.replace_once(
        base, visible,
        'height="2370" viewBox="0 0 1440 2370"',
        'height="2590" viewBox="0 0 1440 2590"',
        "visible source-tested V7 correction and unqualified public entrypoint",
    )
    lines = [v42.move_y(line, 220) for line in visible.splitlines()]
    insertion = next(
        position + 1
        for position, line in enumerate(lines)
        if "source-tested only; C has not run." in line
    )
    lines[insertion:insertion] = [
        '<rect x="44" y="302" width="1352" height="91" rx="14" '
        'fill="#eef5ff" stroke="#b6cbee"/>',
        '<text x="65" y="337" class="warning">RUST V7 ALL-WORKER AND '
        'RECOVERY FIX SOURCE-TESTED ONLY — ZERO CANDIDATE WORKERS</text>',
        '<text x="67" y="365" class="body">All 13 real worker paths and '
        'recovery are source-tested; the actual V6 failure and its omitted '
        'build-archive read remain preserved.</text>',
        '<rect x="44" y="412" width="1352" height="91" rx="14" '
        'fill="#fff1ed" stroke="#e6b3a6"/>',
        '<text x="65" y="447" class="warning">PUBLIC REBAR IMPORT: '
        'UNQUALIFIED ZIG PROTOTYPE; NOT A WINNER</text>',
        '<text x="67" y="475" class="body">1,764 known Zig mismatches; '
        '__version__ missing; package mode false; 50 extra checks NOT '
        'MEASURED; actual public imports: 0.</text>',
    ]
    image = ("\n".join(lines) + "\n").encode("utf-8")
    for phrase in (
        b"rust v7", b"all-worker", b"recovery fix", b"source-tested only",
        b"zero candidate workers", b"actual rust v6 preflight failed",
        b"public rebar import", b"unqualified zig prototype; not a winner",
        b"__version__ missing", b"package mode false",
        b"50 extra checks not measured", b"actual public imports: 0",
        b"one historical build archive was read",
        b"ledger omitted", b"108,985", b"760,477",
        b"matching/reference archives: 0", b"candidate workers: 0",
        b"zero runnable", b"six source designs",
        b"31,237", b"96 / 96",
        b"1,036", b"8,965", b"1,230", b"7,325",
        b"1,764", b"3,711", b"64 of 1,024",
        b"not applied or tested", b"166 / 171",
        b"not measured", b"4,194,304", b"not opened",
    ):
        base.need(phrase.lower() in image.lower(),
                  "reject a missing source-only V7 graph truth: " + repr(phrase))
    for stale in (
        b"rust v7 matching pass",
        b"rust v7 candidate passed",
        b"rust v7 candidate qualified",
        b"rust v7 candidate workers: 1",
        b"two runnable candidates",
        b"2 runnable candidates",
        b"all archives read: 0",
        b"actual rust v6 preflight passed",
        b"public rebar import: qualified",
        b"zig prototype is a winner",
    ):
        base.need(stale not in image.lower(),
                  "reject a fabricated V7 candidate or hidden V6 failure")
    base.need(
        image.endswith(b"\n") and not image.endswith(b"\n\n"),
        "render exactly one final V44 SVG terminal linefeed",
    )
    return image


def build(previous: types.ModuleType, v42: types.ModuleType,
          v41: types.ModuleType, v40: types.ModuleType,
          base: types.ModuleType, source_sha: str, source_bytes: int,
          previous_source: str, previous_inputs: str,
          previous_summary: str, previous_svg: str,
          failure_sha: str, observation_sha: str,
          rust_source: str, rust_protocol: str, rust_contract: str,
          public_module_sha: str, public_module_bytes: int,
          public_project_sha: str, public_project_bytes: int,
          ) -> tuple[dict, tuple[tuple[str, bytes], ...]]:
    base.need(
        RUST_V7_PINS_RELEASED is True,
        "block V44 graph until the independently reviewed Rust V7 triple",
    )
    source_sha = base.checked(source_sha, "exact complete V44 renderer")
    base.need(
        type(source_bytes) is int and 0 < source_bytes <= base.OWNER_LIMIT,
        "require the independently supplied V44 source byte count",
    )
    own_raw, _ = base.read_owner(SELF, source_sha, source_bytes, private=True)
    for role, supplied in (
        ("source", previous_source),
        ("inputs", previous_inputs),
        ("summary", previous_summary),
        ("svg", previous_svg),
    ):
        base.need(
            base.checked(supplied, "exact independently supplied V43 " + role)
            == V43[role][1],
            "reject missing, substituted or unpushed predecessor " + role,
        )
    base.need(
        base.checked(failure_sha, "actual immutable V6 controller failure")
        == previous.FAILURE[1]
        and base.checked(
            observation_sha, "independently observed omitted build effect",
        ) == previous.OBSERVATION[1],
        "preserve both complete genuine Rust V6 failure owners",
    )
    old, old_inputs = authenticate_v43(previous, v42, v41, v40, base)
    proof = authenticate_v7(base, rust_source, rust_protocol, rust_contract)
    public = authenticate_public_entrypoint(
        base, public_module_sha, public_module_bytes,
        public_project_sha, public_project_bytes,
    )
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(source_fix_fields(proof))
    snapshot.update(public_entrypoint_fields(public))
    validate_snapshot(previous, v42, v41, v40, base, snapshot)
    predecessors = {
        role: base.pin(*owner) for role, owner in V43.items()
    }
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 44,
        "python": "3.14.6",
        "renderer": base.pin(SELF, source_sha, len(own_raw)),
        "previous_overview": predecessors,
        **source_fix_fields(proof),
        **public_entrypoint_fields(public),
    })
    inputs_raw = base.canonical(inputs)
    svg = make_svg(
        previous, v42, v41, v40, base, snapshot,
        source_sha, base.digest(inputs_raw),
    )
    families = copy.deepcopy(old["families"])
    common = {
        key: copy.deepcopy(snapshot[key])
        for key in (
            "frozen_corrected_runner_source_family_count",
            "frozen_corrected_runner_source_families",
            "dedicated_corrected_runnable_family_count",
            "dedicated_corrected_runnable_families",
            "actually_runnable_candidate_family_count",
            "actually_runnable_candidate_families",
            "first_party_source_inventory_family_count",
            "other_corrected_candidate_family_count",
            "pending_corrected_candidate_families",
            "corrected_c_matching_status",
            "corrected_rust_matching_status",
            "runtime_no_delegation",
            "performance",
            "qualified_candidate_count",
            "public_entrypoint_status",
            "public_entrypoint_module_version_status",
            "public_entrypoint_actual_imports_by_graph",
            "public_entrypoint_package_mode",
            "supplementary_signature_candidate_status",
        )
    }
    for family in families:
        name = family.get("family")
        if name == "python":
            continue
        family.update(copy.deepcopy(common))
        family.update({
            "candidate_run_under_corrected_reference": "NOT RUN",
            "qualified": False,
            "actual_candidate_workers": 0,
            "actual_native_activations": 0,
        })
        if name == "rust":
            family.update({
                "corrected_rust_v7_source_freeze": copy.deepcopy(proof),
                "corrected_runner_status":
                    "V7 SOURCE-TESTED ONLY; NOT RUNNABLE; "
                    "V6 PREFLIGHT FAILURE PRESERVED",
                "matching_block_reason": V7_BLOCK_REASON,
                "matching_blocked_pending_corrected_candidate_runners": True,
                "corrected_rust_v7_candidate_matching_status": "NOT RUN",
                "corrected_rust_v7_actual_candidate_workers": 0,
            })
        elif name == "c":
            family.update({
                "corrected_runner_status":
                    "SOURCE FROZEN; NOT RUNNABLE; C MATCHING NOT RUN",
                "matching_block_reason":
                    "The C runner source is frozen; the restored native "
                    "engine is not active and no C candidate has run.",
                "matching_blocked_pending_corrected_candidate_runners": True,
            })
        else:
            family.update({
                "corrected_runner_status": "NOT FROZEN; NOT RUNNABLE",
                "matching_block_reason":
                    "This first-party design has no runnable corrected "
                    "engine and has not run the original correctness suite.",
                "matching_blocked_pending_corrected_candidate_runners": True,
            })
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 44,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, source_sha, len(own_raw)),
        "inputs": base.pin(
            OUTPUT + ".inputs.json", base.digest(inputs_raw), len(inputs_raw),
        ),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg), len(svg)),
        "previous_overview": predecessors,
        "snapshot": snapshot,
        "families": families,
        **source_fix_fields(proof),
        **public_entrypoint_fields(public),
    })
    return snapshot, (
        (OUTPUT + ".inputs.json", inputs_raw),
        (OUTPUT + ".json", base.canonical(summary)),
        (OUTPUT + ".svg", svg),
    )


def synthetic_v7_contract(base: types.ModuleType) -> dict:
    return {
        "schema": "rebar-owned-repaired-rust-original-campaign-v7-source-freeze",
        "version": 7,
        "family": "rust",
        "status": "SOURCE FROZEN; CORRECTED RUST CANDIDATE NOT RUN",
        "source": {
            "path": RUST_V7["source"][0],
            "sha256": RUST_V7["source"][1],
        },
        "protocol": {
            "path": RUST_V7["protocol"][0],
            "sha256": RUST_V7["protocol"][1],
        },
        "pinned_cpython": {
            "version": "3.14.6",
            "path": base.PYTHON,
            "sha256": base.PYTHON_SHA,
        },
        "current_historical_accounting": copy.deepcopy(V7_CURRENT_ACCOUNTING),
        "future_lossless_publication": copy.deepcopy(V7_FUTURE_PUBLICATION),
        "published_current_v43_overview": {
            **copy.deepcopy(V7_PUBLISHED_V43_FIELDS),
            "owners": {
                role: base.pin(*owner) for role, owner in V43.items()
            },
        },
        "original_oracle": {
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "named_private_waiver_count": 13,
            "candidate_wrapper_allowed": False,
            "cross_family_matching_allowed": False,
            "external_regex_dependency_allowed": False,
            "stdlib_re_fallback_allowed": False,
            "source_ordered_suites": [
                {"case_execution_count": count}
                for count in (
                    151, 864, 1024, 768, 1024, 2854, 6912,
                    5120, 10240, 1376, 128, 264, 512,
                )
            ],
        },
        "source_only_effects": {
            **{
                name: 0 for name in (
                    "actual_candidate_imports", "actual_candidate_workers",
                    "actual_native_activations", "actual_native_library_loads",
                    "actual_reference_workers", "actual_source_builds",
                    "benchmark_files_read", "canonical_target_reads",
                    "canonical_target_replacements", "canonical_target_stats",
                    "clock_samples", "hidden_cases_read", "threads_started",
                    "timing_trials_run", "workspace_mutations",
                )
            },
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False,
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "winner_selected": False,
        },
    }


def synthetic_v7_proof(base: types.ModuleType) -> dict:
    owners = {
        role: base.synthetic_owner(value, 944001 + index)
        for index, (role, value) in enumerate(RUST_V7.items())
    }
    contract = synthetic_v7_contract(base)
    validate_v7_contract(base, contract)
    preflight = {
        "helper_source": base.synthetic_owner(V2_HELPER, 944099),
        "actual_v2_adapter": base.pin(*V2_ACTUAL_ADAPTER),
        "incorrect_v6_adapter_sha256": V6_WRONG_ADAPTER,
        "immutable_helper_extracted_without_execution": True,
        "helper_preflight_before_build_archive": True,
        "helper_preflight_line": 7001,
        "build_context_line": 7002,
        "candidate_target_reads": 0,
        "candidate_workers": 0,
        "reference_archive_reads": 0,
        "matching_archive_reads": 0,
        "source_build_archive_reads": 0,
    }
    validate_helper_preflight(base, preflight)
    proof = {
        "schema": SCHEMA + "-authenticated-rust-v7-source-freeze",
        "status": V7_STATUS,
        **owners,
        "complete_frozen_contract": contract,
        "immutable_v2_helper_preflight": preflight,
        "candidate_family": "rust",
        "version": 7,
        "actual_candidate_workers": 0,
        "actual_native_activations": 0,
        "actual_reference_workers": 0,
        "actual_source_build_archive_reads": 0,
        "actual_matching_archive_reads": 0,
        "actual_candidate_matching": "NOT RUN",
        "actually_runnable_candidate_family_count": 0,
        "candidate_qualified": False,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }
    proof["complete_v7_source_binding_sha256"] = base.digest(
        base.canonical({
            "source": owners["source"],
            "protocol": owners["protocol"],
            "contract": owners["contract"],
            "complete_frozen_contract": contract,
            "immutable_v2_helper_preflight": preflight,
        }),
    )
    validate_v7_proof(base, proof)
    return proof


def synthetic_public_entrypoint(base: types.ModuleType) -> dict:
    proof = {
        "schema": SCHEMA + "-static-public-entrypoint",
        "status": PUBLIC_STATUS,
        "module": base.synthetic_owner(PUBLIC_OWNERS["module"], 944201),
        "project": base.synthetic_owner(PUBLIC_OWNERS["project"], 944202),
        "audit_method":
            "BOUNDED COMPLETE SOURCE AST AND TOML; NO IMPORT OR EXECUTION",
        "selected_candidate_family": "zig",
        "selected_historical_zig_mismatch_count": 1764,
        "public_module_version_status": "FAIL/MISSING",
        "public_module_qualified": False,
        "project_package_mode": False,
        "packaged_artifact": "NOT MEASURED",
        "installation_status": "NOT MEASURED",
        "supplementary_signature_check_count": 50,
        "supplementary_signature_candidate_status": "NOT MEASURED",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "actual_imports_by_graph": 0,
        "actual_native_loads_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "candidate_correctness": "NOT MEASURED",
        "winner_selected": False,
    }
    proof["complete_public_entrypoint_binding_sha256"] = base.digest(
        base.canonical({
            "module": proof["module"],
            "project": proof["project"],
            **{
                key: value for key, value in proof.items()
                if key not in ("module", "project")
            },
        }),
    )
    validate_public_entrypoint(base, proof)
    return proof


def self_test(previous: types.ModuleType, v42: types.ModuleType,
              v41: types.ModuleType, v40: types.ModuleType,
              base: types.ModuleType) -> dict:
    history = previous.self_test(v42, v41, v40, base)
    base.need(
        history.get("status") == "PASS"
        and history.get("reference_archive_gzip_inflation_count") == 0
        and history.get("matching_archive_gzip_inflation_count") == 0
        and history.get("source_build_archive_gzip_inflation_count_by_graph")
        == 0,
        "first exercise all immutable actual-failure V43 physical walls",
    )
    rejected = 0
    with base.SourceOnlyWall() as wall:
        proof = synthetic_v7_proof(base)
        public = synthetic_public_entrypoint(base)
        for field, value in proof.items():
            hostile = copy.deepcopy(proof)
            hostile[field] = previous.forged_value(base, value)
            try:
                validate_v7_proof(base, hostile)
            except (
                base.GraphError, TypeError, ValueError, KeyError, AttributeError,
            ):
                rejected += 1
            else:
                raise base.GraphError("accepted a forged V7 source proof: " + field)
        for role in ("source", "protocol", "contract"):
            for field, value in proof[role].items():
                hostile = copy.deepcopy(proof)
                hostile[role][field] = previous.forged_value(base, value)
                try:
                    validate_v7_proof(base, hostile)
                except (
                    base.GraphError, TypeError, ValueError,
                    KeyError, AttributeError,
                ):
                    rejected += 1
                else:
                    raise base.GraphError(
                        "accepted a substituted exact V7 " + role,
                    )
        contract = proof["complete_frozen_contract"]
        for field, value in contract.items():
            hostile = copy.deepcopy(proof)
            hostile["complete_frozen_contract"][field] = (
                previous.forged_value(base, value)
            )
            try:
                validate_v7_proof(base, hostile)
            except (
                base.GraphError, TypeError, ValueError, KeyError, AttributeError,
            ):
                rejected += 1
            else:
                raise base.GraphError("accepted a forged V7 contract: " + field)
        preflight = proof["immutable_v2_helper_preflight"]
        for field, value in preflight.items():
            hostile = copy.deepcopy(proof)
            hostile["immutable_v2_helper_preflight"][field] = (
                previous.forged_value(base, value)
            )
            try:
                validate_v7_proof(base, hostile)
            except (
                base.GraphError, TypeError, ValueError, KeyError, AttributeError,
            ):
                rejected += 1
            else:
                raise base.GraphError(
                    "accepted a forged immutable V2/V7 preflight: " + field,
                )
        for role in ("helper_source", "actual_v2_adapter"):
            for field, value in preflight[role].items():
                hostile = copy.deepcopy(proof)
                hostile["immutable_v2_helper_preflight"][role][field] = (
                    previous.forged_value(base, value)
                )
                try:
                    validate_v7_proof(base, hostile)
                except (
                    base.GraphError, TypeError, ValueError,
                    KeyError, AttributeError,
                ):
                    rejected += 1
                else:
                    raise base.GraphError(
                        "accepted a forged immutable V2 source or adapter",
                    )
        for group in (
            "source", "protocol", "pinned_cpython", "original_oracle",
            "source_only_effects", "current_historical_accounting",
            "future_lossless_publication", "published_current_v43_overview",
        ):
            for field, value in contract[group].items():
                hostile = copy.deepcopy(proof)
                hostile["complete_frozen_contract"][group][field] = (
                    previous.forged_value(base, value)
                )
                try:
                    validate_v7_proof(base, hostile)
                except (
                    base.GraphError, TypeError, ValueError,
                    KeyError, AttributeError,
                ):
                    rejected += 1
                else:
                    raise base.GraphError("accepted a forged V7 " + group)
        for field, value in public.items():
            hostile = copy.deepcopy(public)
            hostile[field] = previous.forged_value(base, value)
            try:
                validate_public_entrypoint(base, hostile)
            except (
                base.GraphError, TypeError, ValueError, KeyError, AttributeError,
            ):
                rejected += 1
            else:
                raise base.GraphError(
                    "accepted a forged public entrypoint fact: " + field,
                )
        for role in ("module", "project"):
            for field, value in public[role].items():
                hostile = copy.deepcopy(public)
                hostile[role][field] = previous.forged_value(base, value)
                try:
                    validate_public_entrypoint(base, hostile)
                except (
                    base.GraphError, TypeError, ValueError,
                    KeyError, AttributeError,
                ):
                    rejected += 1
                else:
                    raise base.GraphError(
                        "accepted a substituted public " + role,
                    )
        probes = (
            ("filesystem", lambda: builtins.open("forbidden-v44")),
            ("filesystem", lambda: os.open("forbidden-v44", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v44")),
            ("write", lambda: os.mkdir("forbidden-v44")),
            ("process", lambda: subprocess.run(("forbidden-v44",))),
            ("process", lambda: subprocess.Popen(("forbidden-v44",))),
            ("process", lambda: os.execv("/forbidden-v44", [])),
        )
        for kind, action in probes:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(
                    wall.blocked[kind] == before + 1,
                    "physically block the genuine V44 source-only " + kind,
                )
            else:
                raise base.GraphError("a real V44 source-only effect escaped")
        base.need(rejected >= 60,
                  "reject all forged helper fixes and invented V7 candidate runs")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 44,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v43_hostile_controls":
                history["rejected_hostile_control_count"],
            "rust_v7_hostile_controls": rejected,
            "rejected_hostile_control_count":
                history["rejected_hostile_control_count"] + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "actual_failure_evidence_read_by_self_test": 0,
            "actual_observation_evidence_read_by_self_test": 0,
            "rust_v7_real_source_read_by_self_test": 0,
            "reference_archive_gzip_inflation_count": 0,
            "matching_archive_gzip_inflation_count": 0,
            "source_build_archive_gzip_inflation_count_by_graph": 0,
            "candidate_matching_archives_opened_by_graph": 0,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "corrected_rust_v7_source_status": V7_STATUS,
            "corrected_rust_v7_candidate_matching_status": "NOT RUN",
            "corrected_rust_v7_actual_candidate_workers": 0,
            "corrected_rust_v7_source_build_archive_reads": 0,
            "corrected_rust_v7_helper_preflight_before_build_archive": True,
            "corrected_rust_v7_publication_source_tested_only": True,
            "corrected_rust_v7_current_evidence_owner_lower_bound": 166,
            "corrected_rust_v7_current_history_reference_lower_bound": 171,
            "corrected_rust_v7_future_publication_distinct_owner_count": 2,
            "corrected_rust_v7_future_evidence_owner_lower_bound": 168,
            "corrected_rust_v7_future_history_reference_lower_bound": 173,
            "corrected_rust_v7_archive_uses_evidence_basename": True,
            "corrected_rust_v7_v2_receipt_uses_repository_evidence_path": True,
            "corrected_rust_v7_future_results_require_all_thirteen_workers":
                True,
            "corrected_rust_v7_all_worker_and_recovery_source_wall_tested":
                True,
            "corrected_rust_v7_only_controller_retains_source_build": True,
            "corrected_rust_v7_controller_ledgered_source_build_read_count": 1,
            "corrected_rust_v7_original_worker_source_build_read_count": 0,
            "corrected_rust_v7_public_recovery_source_build_read_count": 0,
            "corrected_rust_v7_unledgered_retained_context_rejected": True,
            **public_entrypoint_fields(public),
            "corrected_rust_v7_immutable_v2_adapter_sha256":
                V2_ACTUAL_ADAPTER[1],
            "superseded_rust_v6_wrong_historical_adapter_sha256":
                V6_WRONG_ADAPTER,
            "frozen_corrected_runner_source_family_count": 2,
            "frozen_corrected_runner_source_families": ["c", "rust"],
            "actually_runnable_candidate_family_count": 0,
            "dedicated_corrected_runnable_family_count": 0,
            "actual_rust_v6_controller_status": "FAIL",
            "actual_rust_v6_controller_process_count": 1,
            "actual_rust_v6_candidate_workers": 0,
            "actual_rust_v6_source_build_archive_read_count": 1,
            "actual_rust_v6_ledger_omits_source_build_archive_effect": True,
            "actual_rust_v6_semantic_mismatch_count": "NOT MEASURED",
            "corrected_c_matching_status": "NOT RUN",
            "qualified_candidate_count": 0,
            "full_case_denominator": 31237,
            "suite_count": 13,
            "private_waiver_count": 13,
            "hidden_cases_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_mutations": 0,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "final_holdout_opened": False,
            "winner_selected": False,
        }


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    allowed = {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
    base.need(
        RUST_V7_PINS_RELEASED is True
        and path in allowed and type(raw) is bytes
        and 0 < len(raw) <= base.OWNER_LIMIT,
        "publish only the three expressly released V44 graph owners",
    )
    flags = (
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(descriptor, remaining)
            base.need(type(count) is int and count > 0,
                      "reject an incomplete source-only V44 graph")
            remaining = remaining[count:]
        os.fsync(descriptor)
        owner = os.fstat(descriptor)
        base.need(
            owner.st_uid == os.geteuid()
            and owner.st_nlink == 1
            and owner.st_size == len(raw)
            and stat.S_IMODE(owner.st_mode) == 0o600,
            "create exactly one complete private V44 graph owner",
        )
    finally:
        os.close(descriptor)
    directory = os.open(
        str(ROOT / Path(path).parent),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    observed, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(observed == raw, "authenticate every immutable V44 output byte")


def result(base: types.ModuleType, snapshot: dict,
           outputs: dict[str, bytes], source: str,
           *, written: bool, suffix: str) -> dict:
    return {
        "schema": SCHEMA + suffix,
        "version": 44,
        "status": "PASS",
        "source_sha256": source,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 43,
        **{
            "previous_overview_" + role + "_sha256": owner[1]
            for role, owner in V43.items()
        },
        "actual_failure_sha256":
            snapshot["actual_rust_failure_evidence_sha256"],
        "actual_observation_sha256":
            snapshot["actual_rust_observed_effects_sha256"],
        "rust_v7_source_sha256": RUST_V7["source"][1],
        "rust_v7_protocol_sha256": RUST_V7["protocol"][1],
        "rust_v7_contract_sha256": RUST_V7["contract"][1],
        **public_entrypoint_fields(snapshot["public_entrypoint_static_audit"]),
        "outputs_written": written,
        "reference_archive_gzip_inflation_count": 0,
        "matching_archive_gzip_inflation_count": 0,
        "source_build_archive_gzip_inflation_count_by_graph": 0,
        "candidate_matching_archives_opened_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        **{
            key: copy.deepcopy(snapshot[key])
            for key in (
                "corrected_rust_v7_source_status",
                "corrected_rust_v7_candidate_matching_status",
                "corrected_rust_v7_actual_candidate_workers",
                "corrected_rust_v7_actual_native_activations",
                "corrected_rust_v7_source_build_archive_reads",
                "corrected_rust_v7_helper_preflight_before_build_archive",
                "corrected_rust_v7_publication_source_tested_only",
                "corrected_rust_v7_current_evidence_owner_lower_bound",
                "corrected_rust_v7_current_history_reference_lower_bound",
                "corrected_rust_v7_future_publication_distinct_owner_count",
                "corrected_rust_v7_future_evidence_owner_lower_bound",
                "corrected_rust_v7_future_history_reference_lower_bound",
                "corrected_rust_v7_archive_uses_evidence_basename",
                "corrected_rust_v7_v2_receipt_uses_repository_evidence_path",
                "corrected_rust_v7_future_results_require_all_thirteen_workers",
                "corrected_rust_v7_all_worker_and_recovery_source_wall_tested",
                "corrected_rust_v7_only_controller_retains_source_build",
                "corrected_rust_v7_controller_ledgered_source_build_read_count",
                "corrected_rust_v7_original_worker_source_build_read_count",
                "corrected_rust_v7_public_recovery_source_build_read_count",
                "corrected_rust_v7_unledgered_retained_context_rejected",
                "corrected_rust_v7_immutable_v2_helper_sha256",
                "corrected_rust_v7_immutable_v2_adapter_sha256",
                "superseded_rust_v6_wrong_historical_adapter_sha256",
                "superseded_rust_v6_source_remains_immutable",
                "actual_rust_v6_preflight_failure_preserved",
                "actual_rust_controller_status",
                "actual_rust_controller_process_count",
                "actual_rust_attempted_suite_count",
                "actual_rust_started_suite_count",
                "actual_rust_completed_suite_count",
                "actual_rust_candidate_workers",
                "actual_rust_native_activations",
                "actual_rust_source_build_archive_read_count",
                "actual_rust_source_build_archive_gzip_inflation_count",
                "actual_rust_source_build_archive_compressed_bytes",
                "actual_rust_source_build_archive_uncompressed_bytes",
                "actual_rust_controller_ledger_omits_source_build_archive_effect",
                "actual_rust_matching_archive_read_count",
                "actual_rust_reference_archive_read_count",
                "actual_rust_semantic_mismatch_count",
                "frozen_corrected_runner_source_family_count",
                "frozen_corrected_runner_source_families",
                "actually_runnable_candidate_family_count",
                "actually_runnable_candidate_families",
                "dedicated_corrected_runnable_family_count",
                "dedicated_corrected_runnable_families",
                "first_party_source_inventory_family_count",
                "other_corrected_candidate_family_count",
                "pending_corrected_candidate_families",
                "corrected_c_matching_status",
                "corrected_rust_matching_status",
                "qualified_candidate_count",
                "authenticated_evidence_owner_lower_bound",
                "authenticated_history_reference_lower_bound",
                "exact_whole_repository_evidence_owner_count",
                "exact_whole_repository_reference_count",
                "full_case_denominator",
                "suite_count",
                "private_waiver_count",
                "hidden_cases_read",
                "clock_samples",
                "timing_trials_run",
                "runtime_no_delegation",
                "performance",
                "memory",
                "confidence_intervals",
                "undefined_behavior",
                "final_comparison_planned_case_count",
                "final_comparison_cases_generated",
                "final_holdout_opened",
                "winner_selected",
            )
        },
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    parser.add_argument("--previous-source-sha256")
    parser.add_argument("--previous-inputs-sha256")
    parser.add_argument("--previous-summary-sha256")
    parser.add_argument("--previous-svg-sha256")
    parser.add_argument("--failure-sha256")
    parser.add_argument("--observation-sha256")
    parser.add_argument("--rust-source-sha256")
    parser.add_argument("--rust-protocol-sha256")
    parser.add_argument("--rust-contract-sha256")
    parser.add_argument("--public-module-sha256")
    parser.add_argument("--public-module-bytes", type=int)
    parser.add_argument("--public-project-sha256")
    parser.add_argument("--public-project-bytes", type=int)
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, v42, v41, v40, base = load_v43()
        if options.self_test:
            base.need(
                all(
                    getattr(options, name) is None
                    for name in (
                        "source_sha256", "source_bytes",
                        "previous_source_sha256", "previous_inputs_sha256",
                        "previous_summary_sha256", "previous_svg_sha256",
                        "failure_sha256", "observation_sha256",
                        "rust_source_sha256", "rust_protocol_sha256",
                        "rust_contract_sha256", "public_module_sha256",
                        "public_module_bytes", "public_project_sha256",
                        "public_project_bytes", "inputs_sha256",
                        "summary_sha256", "svg_sha256",
                    )
                ),
                "synthetic V44 gates cannot accept actual owner or archive pins",
            )
            sys.stdout.buffer.write(base.canonical(
                self_test(previous, v42, v41, v40, base),
            ))
            return 0
        base.need(
            RUST_V7_PINS_RELEASED is True,
            "block graph output until independently released Rust V7 owners",
        )
        source = base.checked(options.source_sha256, "exact final V44 renderer")
        previous_source = base.checked(
            options.previous_source_sha256, "exact frozen V43 source",
        )
        previous_inputs = base.checked(
            options.previous_inputs_sha256, "exact frozen V43 inputs",
        )
        previous_summary = base.checked(
            options.previous_summary_sha256, "exact frozen V43 summary",
        )
        previous_svg = base.checked(
            options.previous_svg_sha256, "exact frozen V43 SVG",
        )
        failure = base.checked(
            options.failure_sha256, "genuine actual Rust V6 failure",
        )
        observation = base.checked(
            options.observation_sha256,
            "genuine omitted V6 source-build archive effect",
        )
        rust_source = base.checked(
            options.rust_source_sha256,
            "independently released V7 source",
        )
        rust_protocol = base.checked(
            options.rust_protocol_sha256,
            "independently released V7 protocol",
        )
        rust_contract = base.checked(
            options.rust_contract_sha256,
            "independently released V7 contract",
        )
        public_module = base.checked(
            options.public_module_sha256,
            "exact tracked unqualified public rebar source",
        )
        public_project = base.checked(
            options.public_project_sha256,
            "exact tracked package-disabled project source",
        )
        snapshot, pairs = build(
            previous, v42, v41, v40, base,
            source, options.source_bytes,
            previous_source, previous_inputs, previous_summary, previous_svg,
            failure, observation, rust_source, rust_protocol, rust_contract,
            public_module, options.public_module_bytes,
            public_project, options.public_project_bytes,
        )
        outputs = dict(pairs)
        if options.render:
            base.need(
                options.inputs_sha256 is None
                and options.summary_sha256 is None
                and options.svg_sha256 is None,
                "render exactly three authorized new V44 graph owners",
            )
            for path, raw in pairs:
                publish(base, path, raw)
            sys.stdout.buffer.write(base.canonical(result(
                base, snapshot, outputs, source,
                written=True, suffix="-published",
            )))
            return 0
        expected = {
            OUTPUT + ".inputs.json": base.checked(
                options.inputs_sha256, "exact V44 inputs",
            ),
            OUTPUT + ".json": base.checked(
                options.summary_sha256, "exact V44 summary",
            ),
            OUTPUT + ".svg": base.checked(
                options.svg_sha256, "exact V44 visible graph",
            ),
        }
        for path, fingerprint in expected.items():
            actual, _ = base.read_owner(
                path, fingerprint, len(outputs[path]), private=True,
            )
            base.need(
                actual == outputs[path],
                "reproduce every authenticated V44 source-fix graph byte",
            )
        sys.stdout.buffer.write(base.canonical(result(
            base, snapshot, outputs, source,
            written=False, suffix="-read-only-frozen-context",
        )))
        return 0
    except (
        ValueError, OSError, TypeError, EOFError, KeyError,
        AttributeError, RecursionError,
    ) as error:
        sys.stderr.write("current V44 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write(
                "current V44 overview rejected: " + str(error) + "\n",
            )
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
