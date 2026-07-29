#!/usr/bin/env python3
"""Show real large-input requirements without claiming a candidate ran them."""

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
import types


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v47.py"
OUTPUT = "docs/evidence/candidate-current-overview-v47"
SCHEMA = "rebar-candidate-current-overview-v47"
V46 = {
    "source": (
        "tools/render_candidate_current_overview_v46.py",
        "ddb25b70d9f87ad3b6eabbc7c2917a434739931ad2f5b5d194b5cb25706a9334",
        78101,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v46.inputs.json",
        "c0633ec12f5aad3d0e0fb8fe29f143ccb6801ec63d5960c85afd47d982c4653d",
        382381,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v46.json",
        "ec5ecbbcb765bb845a133ad81d02312eb29e6b18718d5e4b346ff10e74c10b3f",
        1073582,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v46.svg",
        "913f8af0eae80bc48640551b589556a685f81b69f218783afc04e8d7e3746c14",
        16635,
    ),
}
LARGE = {
    "source": (
        "tools/verify_large_input_indexing_v1.py",
        "57a9e0d0e456b854cb46dfadb2b23db244597f01904fcf93587b1f5d8a5e4544",
        99829,
    ),
    "protocol": (
        "oracle/phase1/P0-LARGE-INPUT-INDEXING-V1.md",
        "0a640ee044c52394fa897d0221d51dfc3d85e9abb95608367698f11fba8ca879",
        5345,
    ),
    "contract": (
        "oracle/phase1/p0-large-input-indexing-v1.json",
        "23601fe4947c70979081d8248ee9891287e3fa618b554b97a8ee56024823bacf",
        17322,
    ),
}
LARGE_MATRIX_SHA256 = (
    "a105aea287d093ff977819dda8971f592c3ed396eabd3133e5c52838ce8e2f65"
)
PUBLIC_MATRIX_SHA256 = (
    "f67f8d4d62f9939c94250ad2e4df55b14df013df7212aa66930ecc3a772d2a58"
)
PUBLIC_STATUS = "UNQUALIFIED ZIG PROTOTYPE; NOT A WINNER"
PUBLIC_COUNTS = {
    "PASS": 17,
    "FAIL": 7,
    "NOT MEASURED": 6,
    "NOT ESTABLISHED": 1,
    "NOT OPENED": 1,
}
LARGE_COUNTS = {
    "PASS": 22,
    "FAIL": 1,
    "NOT RUN": 3,
    "NOT ESTABLISHED": 2,
    "NOT MEASURED": 3,
    "NOT OPENED": 1,
}
LARGE_ROWS = (
    ("large-source.clean-engine-freeze", "PASS"),
    ("large-source.physical-effect-wall", "PASS"),
    ("large-source.authenticated-upstream-source", "PASS"),
    ("large-source.exact-search-decorator", "PASS"),
    ("large-source.exact-subn-decorator", "PASS"),
    ("large-source.exact-search-semantics", "PASS"),
    ("large-source.exact-subn-semantics", "PASS"),
    ("large-reference.distinct-original-processes", "PASS"),
    ("large-reference.original-search-2g", "PASS"),
    ("large-reference.original-subn-2g", "PASS"),
    ("large-reference.original-40g-admission", "PASS"),
    ("large-reference.release-debug-skip-not-waiver", "PASS"),
    ("large-candidate.actual-input-cap-5147", "PASS"),
    ("large-candidate.actual-search-2g", "NOT RUN"),
    ("large-candidate.actual-subn-2g", "NOT RUN"),
    ("large-candidate.full-resource-qualification", "NOT ESTABLISHED"),
    ("preserved.original-31237-denominator", "PASS"),
    ("preserved.original-13-suite-denominator", "PASS"),
    ("preserved.original-13-private-waivers", "PASS"),
    ("preserved.signature-50-separate", "PASS"),
    ("preserved.signature-two-reference-pass", "PASS"),
    ("preserved.signature-candidate", "NOT RUN"),
    ("preserved.public-entrypoint-32-separate", "PASS"),
    ("preserved.public-entrypoint-actual-observation", "FAIL"),
    ("preserved.rust-v6-failure-and-archive-effect", "PASS"),
    ("preserved.rust-v7-no-archive-inflation", "PASS"),
    ("safety.future-resource-gated-worker-not-started", "PASS"),
    ("safety.native-runtime-no-delegation", "NOT ESTABLISHED"),
    ("safety.native-memory", "NOT MEASURED"),
    ("safety.native-undefined-behavior", "NOT MEASURED"),
    ("performance.end-to-end", "NOT MEASURED"),
    ("performance.final-holdout", "NOT OPENED"),
)
LARGE_SUBJECT = 2147483648
LARGE_SUBN_COUNT = 2147483649
CANDIDATE_SUBJECT_CAP = 5147
HISTORICAL_REFERENCE_MEMORY = 42949672960
MINIMUM_AVAILABLE_MEMORY = 42949672961
GOAL_SHA256 = (
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
)
STDLIB_SOURCE = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/re/__init__.py"
)
STDLIB_SHA256 = (
    "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35"
)
OWNER_ROWS = (
    ("goal", "GOAL.md", GOAL_SHA256, 3756),
    (
        "public_entrypoint", "rebar.py",
        "289769bd637ea525ae7e71d263377e15c0f394ba20619c11b98e266f57fcc34f",
        212,
    ),
    (
        "project_configuration", "pyproject.toml",
        "7d50e8c6c2bc76a0e3ddcac6b5f157b013bcfd76944fdeb2c1c81e0181ae7825",
        224,
    ),
    (
        "historical_zig_adapter", "candidates/zig_candidate.py",
        "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862",
        68422,
    ),
    (
        "original_p0_inventory", "oracle/phase1/p0-completeness-v1.json",
        "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
        45632,
    ),
    (
        "original_p0_protocol", "oracle/phase1/P0-COMPLETENESS-V1.md",
        "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798",
        10392,
    ),
    (
        "additional_signature_inventory",
        "oracle/phase1/p0-callable-introspection-v1.json",
        "e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349",
        14749,
    ),
    (
        "additional_signature_protocol",
        "oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md",
        "1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8",
        8952,
    ),
    (
        "actual_signature_reference_receipt",
        "oracle/phase1/evidence/"
        "callable-introspection-reference-v2-cpython-3.14.6-publication-receipt.json",
        "29b4a389e1b99cce15f07069ee1a0895f193e13400f944a037a4f42832619334",
        3533,
    ),
    (
        "first_party_source_inventory",
        "oracle/phase2/candidate-independence-v2.json",
        "89662570a643d94ae1581393ed48015c6fa78d5dbe5ad0419e9a2032e4609659",
        8798,
    ),
    (
        "first_party_source_protocol", "oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md",
        "80a1de729c067da36648dcfb9751f7bd3833ff561956df9ad82fc6106a19a16b",
        6194,
    ),
    (
        "released_zig_v1_worker",
        "tools/run_frozen_zig_original_p0_candidate_worker_v1.py",
        "ddafdc5b1fe06dbfa6449cbfde768d7fee6d16953b3c769c1e30aa600e3c62f9",
        123801,
    ),
    (
        "released_zig_v1_controller",
        "tools/run_frozen_zig_original_p0_candidate_v1.py",
        "8c9be13232fdbab7ff01b2313a816fd80e033fb5b6d0bf3d8cb07444eeba4856",
        55722,
    ),
    (
        "released_zig_v1_protocol",
        "oracle/phase2/ZIG-ORIGINAL-P0-CANDIDATE-PROTOCOL-V1.md",
        "294dfb6bc8e286d8415b329f8b2918b856ab3b2d1afb8261e3e04663028fda3c",
        9040,
    ),
    (
        "released_zig_v1_contract",
        "oracle/phase2/zig-original-p0-candidate-protocol-v1.json",
        "1ff289540457ecba4e91b3b9491b3c42872a5db09b95815b8f58fcdc34315470",
        19592,
    ),
    (
        "public_entrypoint_oracle_source",
        "tools/verify_public_entrypoint_import_v1.py",
        "c0a61c4cf520e82bf0c327a17c06daf64f57a1dcfd20b37c6e9f7b84177108b4",
        83957,
    ),
    (
        "public_entrypoint_oracle_protocol",
        "oracle/phase1/P0-PUBLIC-ENTRYPOINT-IMPORT-V1.md",
        "01ace52c6285142733bdcb2b4556feb43226e01c8b181b84019b8fa8c42697c0",
        7991,
    ),
    (
        "public_entrypoint_oracle_contract",
        "oracle/phase1/p0-public-entrypoint-import-v1.json",
        "b80ba35a6af481f0dd1c5b9141e2995f7b0ffd12f8ffa7060bab50344ddbda47",
        9823,
    ),
    (
        "upstream_original_test", "oracle/cpython-3.14.6/test_re.py",
        "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2",
        150895,
    ),
    (
        "upstream_original_accounting", "oracle/cpython-3.14.6/manifest-v5.json",
        "41b598475a6f756bf63dcd71141d602da05ebb7a810525c45b6c07635b78c0d7",
        75694,
    ),
    (
        "upstream_original_accounting_verifier",
        "tools/verify_original_cpython_accounting_v1.py",
        "f562ab8c998197880590487fa6e78f511db5c01596ab35731185ca8caead454c",
        136758,
    ),
    (
        "upstream_original_accounting_protocol",
        "oracle/cpython-3.14.6/UPSTREAM-ACCOUNTING-V5.md",
        "21e77143bbec1f54faa6fc8a74a842808e32bd36815802a0df3ddfef11c597e1",
        9201,
    ),
    (
        "bounded_original_candidate_controller",
        "tools/independent_original_cpython_suite_v5.py",
        "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce",
        123750,
    ),
    (
        "repaired_rust_v7_source",
        "tools/run_owned_repaired_rust_original_campaign_v7.py",
        "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104",
        505616,
    ),
    (
        "repaired_rust_v7_protocol",
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V7.md",
        "0b5182a7eee74e586839abc3a0e8bdd122bac248e9cb3b76c603c5add9281840",
        8433,
    ),
    (
        "repaired_rust_v7_contract",
        "oracle/phase2/repaired-rust-original-campaign-v7.json",
        "9c8e85dcc5dcf0a00953b36dd02c29c2ab7b1ed0b4281eb27f6693c058d155e5",
        46385,
    ),
    ("current_overview_renderer", *V46["source"]),
    ("current_overview_inputs", *V46["inputs"]),
    ("current_overview_summary", *V46["summary"]),
    ("current_overview_svg", *V46["svg"]),
    (
        "pinned_python_executable",
        "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
        "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
        32387816,
    ),
    ("pinned_stdlib_re_source", STDLIB_SOURCE, STDLIB_SHA256, 17876),
)


def load_v46() -> tuple[
    types.ModuleType, types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType, types.ModuleType, types.ModuleType, types.ModuleType,
]:
    path, fingerprint, size = V46["source"]
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
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
            raise ValueError("reject a substituted pushed V46 graph source")
        pieces: list[bytes] = []
        remaining = size
        while remaining:
            piece = os.read(descriptor, min(262144, remaining))
            if not piece:
                raise ValueError("reject a truncated pushed V46 graph source")
            pieces.append(piece)
            remaining -= len(piece)
        if os.read(descriptor, 1):
            raise ValueError("reject appended pushed V46 renderer bytes")
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        if (
            hashlib.sha256(raw).hexdigest() != fingerprint
            or (
                before.st_dev, before.st_ino, before.st_size,
                before.st_nlink, before.st_mtime_ns,
            ) != (
                after.st_dev, after.st_ino, after.st_size,
                after.st_nlink, after.st_mtime_ns,
            )
        ):
            raise ValueError("reject replacement during V46 authentication")
    finally:
        os.close(descriptor)
    previous = types.ModuleType("_rebar_pushed_large_input_history_v46")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(
        compile(raw, previous.__file__, "exec", dont_inherit=True),
        previous.__dict__,
    )
    v45, v44, v43, v42, v41, v40, base = previous.load_v45()
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v46"
        and previous.SELF == path
        and previous.PUBLIC_STATUS == PUBLIC_STATUS,
        "load only the exact main-branch pushed V46 three-runner renderer",
    )
    return previous, v45, v44, v43, v42, v41, v40, base


def large_rows() -> list[dict[str, str]]:
    return [{"id": name, "status": status} for name, status in LARGE_ROWS]


def owner_mapping(base: types.ModuleType) -> dict[str, dict]:
    owners: dict[str, dict] = {}
    for role, path, fingerprint, size in OWNER_ROWS:
        base.checked(fingerprint, "large-input source owner " + role)
        base.need(
            type(role) is str and role not in owners
            and type(path) is str and bool(path)
            and type(size) is int and 0 < size <= 40 * 1024 * 1024,
            "bound and uniquely pin the complete large-input owner " + role,
        )
        owners[role] = {"path": path, "sha256": fingerprint, "bytes": size}
    base.need(len(owners) == 32, "preserve all 32 independently frozen owners")
    return owners


def expected_contract(base: types.ModuleType) -> dict:
    zig_owner = owner_mapping(base)
    return {
        "schema": "rebar-python-re-large-input-indexing-v1-source-freeze",
        "version": 1,
        "status":
            "SOURCE FROZEN; ORIGINAL 2-GIB TESTS AUTHENTICATED; "
            "CANDIDATES NOT RUN",
        "goal_sha256": GOAL_SHA256,
        "pinned_runtime": {
            "implementation": "CPython",
            "python_version": "3.14.6",
            "executable": base.PYTHON,
            "executable_sha256": base.PYTHON_SHA,
            "stdlib_re_source": STDLIB_SOURCE,
            "stdlib_re_source_sha256": STDLIB_SHA256,
            "isolated": True,
            "bytecode_writes": False,
        },
        "original_correctness": {
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "private_waiver_count": 13,
            "additional_signature_case_count": 50,
            "additional_signature_in_original_denominator": False,
            "public_entrypoint_source_case_count": 32,
            "public_entrypoint_cases_in_original_denominator": False,
            "public_entrypoint_cases_in_signature_denominator": False,
            "large_input_source_cases_in_original_denominator": False,
            "original_denominator_changed": False,
        },
        "upstream_large_input": {
            "case_count": 2,
            "subject_size": LARGE_SUBJECT,
            "subject_code_point": "a",
            "source_case_matrix_included_in_original_denominator": False,
            "source_execution": "AST ONLY; NO REGEX MATCHING",
            "cases": [
                {
                    "id": "ReTests.test_large_search",
                    "decorator": "bigmemtest(size=_2G, memuse=1)",
                    "memuse": 1,
                    "api": "re.search",
                    "pattern": "$",
                    "expected_match_start": LARGE_SUBJECT,
                    "expected_match_end": LARGE_SUBJECT,
                },
                {
                    "id": "ReTests.test_large_subn",
                    "decorator": "bigmemtest(size=_2G, memuse=16 + 2)",
                    "memuse": 18,
                    "api": "re.subn",
                    "pattern": "",
                    "replacement": "",
                    "expected_result_equals_original_subject": True,
                    "expected_replacement_count": LARGE_SUBN_COUNT,
                },
            ],
        },
        "historical_full_resource_reference": {
            "status": "PASS; HISTORICAL PINNED MANIFEST EVIDENCE",
            "executed_by_this_source_oracle": False,
            "reference_process_count": 2,
            "reference_roles": ["reference_a", "reference_b"],
            "passing_public_methods_per_reference": 151,
            "failing_public_methods_per_reference": 0,
            "release_debug_skips_per_reference": 1,
            "release_debug_skip_is_private_waiver": False,
            "large_search_subject_size": LARGE_SUBJECT,
            "large_subn_subject_size": LARGE_SUBJECT,
            "real_max_memory_bytes": HISTORICAL_REFERENCE_MEMORY,
            "exclusive_big_memory_worker": True,
            "reference_report": {
                "path": "oracle/cpython-3.14.6/evidence/"
                    "postfinal-locale-v5-self-oracle.json",
                "sha256":
                    "3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916",
            },
            "reference_report_read_by_this_source_oracle": False,
        },
        "actual_candidate_large_input": {
            "original_controller_bigmem_dry_run": True,
            "original_controller_maximum_subject_size": CANDIDATE_SUBJECT_CAP,
            "full_resource_large_search": "NOT RUN",
            "full_resource_large_subn": "NOT RUN",
            "full_resource_candidate_qualification": "NOT ESTABLISHED",
            "large_candidate_workers_started_by_this_source_oracle": 0,
            "candidate_qualified": False,
        },
        "public_entrypoint_preservation": {
            "case_count": 32,
            "case_matrix_sha256": PUBLIC_MATRIX_SHA256,
            "source_freeze_status": "PASS",
            "actual_observed_status": "FAIL",
            "actual_classification": "UNQUALIFIED_ZIG_PROTOTYPE",
            "public_module_version_status": "FAIL/MISSING",
            "public_entrypoint_qualified": False,
            "case_matrix_in_original_denominator": False,
            "case_matrix_in_signature_denominator": False,
        },
        "corrected_rust_preservation": {
            "actual_v6_controller_status": "FAIL",
            "actual_v6_source_build_archive_read_count": 1,
            "actual_v6_source_build_archive_inflation_count": 1,
            "actual_v6_controller_ledger_omits_source_build_archive_effect": True,
            "corrected_v7_source_sha256":
                "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104",
            "corrected_v7_source_status":
                "SOURCE FROZEN; CORRECTED RUST V13 CANDIDATE NOT RUN",
            "corrected_v7_candidate_matching": "NOT RUN",
            "corrected_v7_source_self_test_control_count": 517,
            "corrected_v7_archive_reads_in_source_freeze": 0,
            "corrected_v7_archive_inflations_in_source_freeze": 0,
        },
        "released_zig_v1_preservation": {
            "source_freeze_status":
                "SOURCE FROZEN; FIRST-PARTY ZIG CANDIDATE NOT RUN",
            "worker_source_sha256":
                zig_owner["released_zig_v1_worker"]["sha256"],
            "controller_source_sha256":
                zig_owner["released_zig_v1_controller"]["sha256"],
            "protocol_sha256":
                zig_owner["released_zig_v1_protocol"]["sha256"],
            "contract_sha256":
                zig_owner["released_zig_v1_contract"]["sha256"],
            "candidate_matching": "NOT RUN",
            "candidate_qualified": False,
            "actual_candidate_workers": 0,
            "actual_compiler_processes": 0,
            "actual_native_activations": 0,
            "actual_native_libraries_loaded": 0,
            "actual_reference_workers": 0,
            "stdlib_regex_engine_dependency_count": 0,
            "external_regex_package_count": 0,
            "cross_candidate_engine_dependency_count": 0,
            "matching_fallback_count": 0,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "frozen_corrected_runner_source_families": ["c", "rust", "zig"],
            "frozen_corrected_runner_source_family_count": 3,
            "actually_runnable_candidate_families": [],
            "actually_runnable_candidate_family_count": 0,
            "dedicated_corrected_runnable_families": [],
            "dedicated_corrected_runnable_family_count": 0,
        },
        "current_overview_version": 46,
        "owners": zig_owner,
        "case_matrix": large_rows(),
        "case_matrix_sha256": LARGE_MATRIX_SHA256,
        "future_execution_policy": {
            "execution_implemented_in_this_source_oracle": False,
            "reference_execution_mode": "NOT IMPLEMENTED",
            "candidate_execution_mode": "NOT IMPLEMENTED",
            "requires_separately_frozen_owned_worker_source": True,
            "requires_separately_authenticated_worker_source": True,
            "requires_explicit_available_host_memory_admission": True,
            "available_host_memory_must_be_strictly_greater_than_bytes":
                HISTORICAL_REFERENCE_MEMORY,
            "minimum_available_host_memory_bytes": MINIMUM_AVAILABLE_MEMORY,
            "requires_independent_worker_resource_limit": True,
            "requires_independent_worker_timeout": True,
            "requires_exact_pinned_python_interpreter": True,
            "requires_exact_original_upstream_methods": True,
            "requires_exact_subject_size": LARGE_SUBJECT,
            "requires_exact_search_start_and_end": LARGE_SUBJECT,
            "requires_exact_subn_count": LARGE_SUBN_COUNT,
            "requires_exact_subn_result_equality": True,
            "requires_complete_stdout_stderr_and_exit_observations": True,
            "requires_isolated_reference_process": True,
            "requires_isolated_candidate_process": True,
            "allows_stdlib_regex_for_reference_only": True,
            "allows_stdlib_regex_for_candidate": False,
            "allows_sre_for_candidate": False,
            "allows_external_regex_engine_for_candidate": False,
            "allows_cross_candidate_engine_for_candidate": False,
            "allows_candidate_fallback": False,
            "requires_first_party_independent_candidate_engine_proof": True,
            "requires_actual_both_large_candidate_cases": True,
            "insufficient_resources_count_as_pass": False,
            "insufficient_resources_status": "NOT RUN; INSUFFICIENT RESOURCES",
            "synthetic_admission_is_actual_candidate_evidence": False,
        },
        "boundaries": {
            "source_freeze_status": "PASS",
            "actual_reference_workers_started": 0,
            "actual_candidate_workers_started": 0,
            "actual_candidate_imports": 0,
            "actual_entrypoint_imports": 0,
            "actual_stdlib_regex_imports": 0,
            "actual_native_libraries_loaded": 0,
            "actual_archives_opened": 0,
            "actual_archives_decompressed": 0,
            "actual_subprocesses_started": 0,
            "actual_network_requests": 0,
            "actual_clock_samples": 0,
            "actual_host_memory_queries": 0,
            "actual_large_subject_allocations": 0,
            "maximum_candidate_subject_allocated": 0,
            "actual_holdout_cases_read": 0,
            "actual_hidden_cases_read": 0,
            "workspace_files_written": 0,
            "physical_audit_hook_required": True,
            "physical_audit_denies_unlisted_reads": True,
            "physical_audit_denies_module_imports": True,
            "physical_audit_denies_native_loading": True,
            "physical_audit_denies_execution_and_processes": True,
            "physical_audit_denies_network_and_writes": True,
            "qualified_candidate_count": 0,
            "winner_selected": False,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "holdout_generated": False,
            "holdout_planned_case_count": 4194304,
        },
    }


def validate_large_contract(base: types.ModuleType, contract: object) -> None:
    expected = expected_contract(base)
    base.need(type(contract) is dict, "reject a missing exact large-input contract")
    assert isinstance(contract, dict)
    base.need(
        set(contract) == set(expected),
        "reject an added or omitted exact large-input contract section",
    )
    for key, value in expected.items():
        base.need(
            contract.get(key) == value,
            "reject changed original 2-GiB source evidence: " + key,
        )
    matrix = contract["case_matrix"]
    base.need(
        len(matrix) == 32
        and len({row["id"] for row in matrix}) == 32
        and all(set(row) == {"id", "status"} for row in matrix)
        and hashlib.sha256(base.canonical(matrix)[:-1]).hexdigest()
        == LARGE_MATRIX_SHA256,
        "authenticate all 32 separate large-input observations using status",
    )
    counts = {name: 0 for name in LARGE_COUNTS}
    for row in matrix:
        base.need(row["status"] in counts, "reject invented large-input status")
        counts[row["status"]] += 1
    base.need(
        counts == LARGE_COUNTS,
        "retain the exact 22/1/3/2/3/1 separate large-input statuses",
    )


def expected_large_ast(base: types.ModuleType) -> dict:
    return {
        "source_ast_parsed_without_execution": True,
        "source_sha256": LARGE["source"][1],
        "source_bytes": LARGE["source"][2],
        "goal_sha256": GOAL_SHA256,
        "current_overview_version": 46,
        "authenticated_owner_count": 32,
        "owner_mapping": owner_mapping(base),
        "original_case_count": 31237,
        "original_suite_count": 13,
        "original_private_waiver_count": 13,
        "additional_signature_case_count": 50,
        "separate_public_case_count": 32,
        "large_input_case_count": 2,
        "large_input_subject_bytes": LARGE_SUBJECT,
        "large_input_subn_count": LARGE_SUBN_COUNT,
        "actual_candidate_subject_cap_bytes": CANDIDATE_SUBJECT_CAP,
        "historical_reference_memory_policy_bytes": HISTORICAL_REFERENCE_MEMORY,
        "minimum_available_host_memory_bytes": MINIMUM_AVAILABLE_MEMORY,
        "planned_holdout_case_count": 4194304,
        "separate_large_input_matrix": large_rows(),
        "separate_large_input_matrix_count": 32,
        "separate_large_input_matrix_sha256": LARGE_MATRIX_SHA256,
        "separate_large_input_matrix_status_counts": copy.deepcopy(LARGE_COUNTS),
        "pep578_audit_hook_defined": True,
        "pep578_audit_hook_installer_defined": True,
        "pep578_addaudithook_call_present": True,
        "pep578_actual_probe_tuple_count": 28,
        "source_self_test_defined": True,
        "source_context_defined": True,
        "source_control_count": 330,
        "source_physically_blocked_effect_count": 28,
        "forbidden_docstring_helper_present": False,
        "actual_candidate_imports_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_large_subject_allocations_by_graph": 0,
        "actual_archives_opened_by_graph": 0,
        "actual_archives_decompressed_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_hidden_cases_read_by_graph": 0,
    }


def authenticate_large_source_ast(base: types.ModuleType, raw: bytes) -> dict:
    try:
        tree = ast.parse(raw.decode("utf-8"), filename=LARGE["source"][0])
    except (UnicodeError, SyntaxError, ValueError, RecursionError) as error:
        raise base.GraphError("reject an invalid released large-input AST") from error
    constants: dict[str, object] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
            value = node.value
        else:
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                try:
                    constants[target.id] = ast.literal_eval(value)
                except (ValueError, TypeError, RecursionError):
                    if target.id == "OWNERS" and isinstance(value, ast.Tuple):
                        resolved: list[tuple[object, ...]] = []
                        for row in value.elts:
                            base.need(
                                isinstance(row, ast.Tuple)
                                and len(row.elts) == 4,
                                "require four exact fields in each source owner",
                            )
                            fields: list[object] = []
                            for item in row.elts:
                                if isinstance(item, ast.Name):
                                    base.need(
                                        item.id in {"PYTHON", "STDLIB_RE"}
                                        and item.id in constants,
                                        "reject an unreviewed source owner name",
                                    )
                                    fields.append(constants[item.id])
                                else:
                                    try:
                                        fields.append(ast.literal_eval(item))
                                    except (
                                        ValueError, TypeError, RecursionError,
                                    ) as error:
                                        raise base.GraphError(
                                            "reject a nonliteral source owner",
                                        ) from error
                            resolved.append(tuple(fields))
                        constants[target.id] = tuple(resolved)
                    continue
    required = {
        "ROOT": str(ROOT),
        "PYTHON": base.PYTHON,
        "STDLIB_RE": STDLIB_SOURCE,
        "SCHEMA": "rebar-python-re-large-input-indexing-v1",
        "SOURCE": LARGE["source"][0],
        "PROTOCOL": LARGE["protocol"][0],
        "CONTRACT": LARGE["contract"][0],
        "GOAL_SHA256": GOAL_SHA256,
        "MATRIX_SHA256": LARGE_MATRIX_SHA256,
        "OVERVIEW_VERSION": 46,
        "ORIGINAL_CASES": 31237,
        "ORIGINAL_SUITES": 13,
        "PRIVATE_WAIVERS": 13,
        "SIGNATURE_CASES": 50,
        "PUBLIC_ENTRYPOINT_CASES": 32,
        "LARGE_SUBJECT_SIZE": LARGE_SUBJECT,
        "LARGE_SUBN_COUNT": LARGE_SUBN_COUNT,
        "ORIGINAL_CANDIDATE_MAXIMUM": CANDIDATE_SUBJECT_CAP,
        "FULL_REFERENCE_ALLOWANCE": HISTORICAL_REFERENCE_MEMORY,
        "MIN_AVAILABLE_HOST_BYTES": MINIMUM_AVAILABLE_MEMORY,
        "PLANNED_HOLDOUT_CASES": 4194304,
        "CASE_ROWS": LARGE_ROWS,
    }
    for key, value in required.items():
        base.need(
            constants.get(key) == value,
            "reject substituted large-input source-only AST: " + key,
        )
    source_owner_rows = constants.get("OWNERS")
    base.need(
        type(source_owner_rows) is tuple and len(source_owner_rows) == 32,
        "require all 32 actual large-input source owner literals",
    )
    assert isinstance(source_owner_rows, tuple)
    source_owners = {
        role: {"path": path, "sha256": fingerprint, "bytes": size}
        for role, path, fingerprint, size in source_owner_rows
    }
    base.need(
        source_owners == owner_mapping(base),
        "bind all 32 literal source owners to the actual pushed V46 graph",
    )
    functions = {
        node.name: node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    required_functions = {
        "no_engine_imports", "source_audit_hook", "install_audit_wall",
        "validate_contract", "validate_upstream_large_ast",
        "admit_future_run", "verify_context", "run_self_test",
        "parse_arguments", "main",
    }
    base.need(
        required_functions.issubset(functions),
        "preserve all actual PEP578 and bounded-source gate definitions",
    )
    add_hook = any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "sys"
        and node.func.attr == "addaudithook"
        for node in ast.walk(tree)
    )
    forbidden_helper = any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "ast"
        and node.func.attr == "get_docstring"
        for node in ast.walk(tree)
    )
    actual_block_count = None
    for node in ast.walk(functions["run_self_test"]):
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "actual_blocks"
                for target in node.targets
            )
            and isinstance(node.value, ast.Tuple)
        ):
            actual_block_count = len(node.value.elts)
    base.need(
        add_hook and not forbidden_helper and actual_block_count == 28,
        "require the real 28-probe PEP578 wall without forbidden helper calls",
    )
    proof = expected_large_ast(base)
    validate_large_source_ast(base, proof)
    return proof


def validate_large_source_ast(base: types.ModuleType, proof: object) -> None:
    base.need(
        proof == expected_large_ast(base),
        "reject executed, delegated, unbounded or substituted large-input AST",
    )


def make_large_proof(base: types.ModuleType, owners: dict[str, dict],
                     contract: dict, source_ast: dict) -> dict:
    validate_large_contract(base, contract)
    validate_large_source_ast(base, source_ast)
    proof = {
        "schema": SCHEMA + "-authenticated-large-input-source-freeze",
        "version": 1,
        **owners,
        "complete_frozen_contract": copy.deepcopy(contract),
        "source_ast": copy.deepcopy(source_ast),
        "source_freeze_status":
            "SOURCE FROZEN; ORIGINAL 2-GIB TESTS AUTHENTICATED; "
            "CANDIDATES NOT RUN",
        "original_case_count": 31237,
        "original_suite_count": 13,
        "original_private_waiver_count": 13,
        "additional_signature_case_count": 50,
        "public_case_matrix_count": 32,
        "public_case_matrix_sha256": PUBLIC_MATRIX_SHA256,
        "public_case_status_counts": copy.deepcopy(PUBLIC_COUNTS),
        "large_input_case_count": 2,
        "large_input_subject_bytes": LARGE_SUBJECT,
        "large_input_subn_count": LARGE_SUBN_COUNT,
        "large_input_case_matrix_count": 32,
        "large_input_case_matrix_sha256": LARGE_MATRIX_SHA256,
        "large_input_case_matrix": large_rows(),
        "large_input_case_status_counts": copy.deepcopy(LARGE_COUNTS),
        "large_input_cases_in_original_denominator": False,
        "large_input_cases_in_signature_denominator": False,
        "large_input_cases_in_public_denominator": False,
        "actual_candidate_subject_cap_bytes": CANDIDATE_SUBJECT_CAP,
        "actual_candidate_large_search_status": "NOT RUN",
        "actual_candidate_large_subn_status": "NOT RUN",
        "actual_candidate_large_input_qualification": "NOT ESTABLISHED",
        "historical_reference_memory_policy_bytes": HISTORICAL_REFERENCE_MEMORY,
        "minimum_available_host_memory_bytes": MINIMUM_AVAILABLE_MEMORY,
        "large_input_source_control_count": 330,
        "large_input_physically_blocked_effect_count": 28,
        "actual_large_subject_allocations_by_graph": 0,
        "actual_host_memory_queries_by_graph": 0,
        "actual_candidate_imports_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "actual_archives_opened_by_graph": 0,
        "actual_archives_decompressed_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_hidden_cases_read_by_graph": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    proof["complete_large_input_source_binding_sha256"] = base.digest(
        base.canonical(proof),
    )
    validate_large_proof(base, proof)
    return proof


def validate_large_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict, "reject a missing full large-input proof")
    assert isinstance(proof, dict)
    expected = {
        "schema": SCHEMA + "-authenticated-large-input-source-freeze",
        "version": 1,
        "source_freeze_status":
            "SOURCE FROZEN; ORIGINAL 2-GIB TESTS AUTHENTICATED; "
            "CANDIDATES NOT RUN",
        "original_case_count": 31237,
        "original_suite_count": 13,
        "original_private_waiver_count": 13,
        "additional_signature_case_count": 50,
        "public_case_matrix_count": 32,
        "public_case_matrix_sha256": PUBLIC_MATRIX_SHA256,
        "public_case_status_counts": PUBLIC_COUNTS,
        "large_input_case_count": 2,
        "large_input_subject_bytes": LARGE_SUBJECT,
        "large_input_subn_count": LARGE_SUBN_COUNT,
        "large_input_case_matrix_count": 32,
        "large_input_case_matrix_sha256": LARGE_MATRIX_SHA256,
        "large_input_case_matrix": large_rows(),
        "large_input_case_status_counts": LARGE_COUNTS,
        "large_input_cases_in_original_denominator": False,
        "large_input_cases_in_signature_denominator": False,
        "large_input_cases_in_public_denominator": False,
        "actual_candidate_subject_cap_bytes": CANDIDATE_SUBJECT_CAP,
        "actual_candidate_large_search_status": "NOT RUN",
        "actual_candidate_large_subn_status": "NOT RUN",
        "actual_candidate_large_input_qualification": "NOT ESTABLISHED",
        "historical_reference_memory_policy_bytes": HISTORICAL_REFERENCE_MEMORY,
        "minimum_available_host_memory_bytes": MINIMUM_AVAILABLE_MEMORY,
        "large_input_source_control_count": 330,
        "large_input_physically_blocked_effect_count": 28,
        "actual_large_subject_allocations_by_graph": 0,
        "actual_host_memory_queries_by_graph": 0,
        "actual_candidate_imports_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "actual_archives_opened_by_graph": 0,
        "actual_archives_decompressed_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_hidden_cases_read_by_graph": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    for name, value in expected.items():
        base.need(
            proof.get(name) == value,
            "reject an invented large-input candidate or measurement: " + name,
        )
    for role, pin in LARGE.items():
        owner = proof.get(role)
        base.need(
            type(owner) is dict
            and owner.get("path") == pin[0]
            and owner.get("sha256") == pin[1]
            and owner.get("bytes") == pin[2]
            and owner.get("uid") == os.geteuid()
            and owner.get("mode") == "0600"
            and owner.get("nlink") == 1
            and type(owner.get("device")) is int and owner["device"] > 0
            and type(owner.get("inode")) is int and owner["inode"] > 0,
            "authenticate the exact released private large-input " + role,
        )
    validate_large_contract(base, proof.get("complete_frozen_contract"))
    validate_large_source_ast(base, proof.get("source_ast"))
    body = {
        key: value for key, value in proof.items()
        if key != "complete_large_input_source_binding_sha256"
    }
    base.need(
        proof.get("complete_large_input_source_binding_sha256")
        == base.digest(base.canonical(body)),
        "bind every actual large-input owner, original case and zero effect",
    )


def authenticate_large(base: types.ModuleType,
                       supplied: dict[str, str]) -> dict:
    owners: dict[str, dict] = {}
    raw: dict[str, bytes] = {}
    for role, pin in LARGE.items():
        base.need(
            base.checked(supplied.get(role), "released large-input " + role)
            == pin[1],
            "require the independently released V46-bound large-input " + role,
        )
        raw[role], owners[role] = base.read_owner(*pin, private=True)
    contract = base.document(
        raw["contract"], "complete exact released large-input contract",
        exact=False,
    )
    source_ast = authenticate_large_source_ast(base, raw["source"])
    return make_large_proof(base, owners, contract, source_ast)


def authenticate_v46(previous: types.ModuleType,
                     v45: types.ModuleType, v44: types.ModuleType,
                     v43: types.ModuleType, v42: types.ModuleType,
                     v41: types.ModuleType, v40: types.ModuleType,
                     base: types.ModuleType,
                     supplied: dict[str, str]) -> tuple[dict, dict, bytes]:
    raw: dict[str, bytes] = {}
    for role, pin in V46.items():
        base.need(
            base.checked(supplied.get(role), "exact pushed V46 " + role)
            == pin[1],
            "require the independently pushed V46 source owner " + role,
        )
        raw[role], _ = base.read_owner(*pin, private=True)
    old = base.document(raw["summary"], "complete pushed V46 summary")
    old_inputs = base.document(raw["inputs"], "complete pushed V46 inputs")
    snapshot = old.get("snapshot")
    previous.validate_snapshot(
        v45, v44, v43, v42, v41, v40, base, snapshot,
    )
    old45, _old45_inputs, old45svg = previous.authenticate_v45(
        v45, v44, v43, v42, v41, v40, base,
        {role: pin[1] for role, pin in previous.V45.items()},
    )
    base.need(
        old45.get("version") == 45
        and old.get("schema") ==
        "rebar-candidate-current-overview-v46-summary"
        and old.get("version") == 46
        and old.get("status") == "PASS"
        and old.get("source") == base.pin(*V46["source"])
        and old.get("inputs") == base.pin(*V46["inputs"])
        and old.get("svg") == base.pin(*V46["svg"])
        and old_inputs.get("schema") ==
        "rebar-candidate-current-overview-v46-inputs"
        and old_inputs.get("version") == 46
        and old_inputs.get("renderer") == base.pin(*V46["source"])
        and raw["svg"] == previous.make_svg(
            v45, v44, v43, v42, v41, v40, base,
            snapshot, old45svg, V46["source"][1], V46["inputs"][1],
        )
        and old.get("public_entrypoint_status") == PUBLIC_STATUS
        and old.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and old.get("frozen_corrected_runner_source_family_count") == 3
        and old.get("actually_runnable_candidate_family_count") == 0
        and old.get("qualified_candidate_count") == 0,
        "regenerate all four exact pushed V46 graph owners and preserve "
        "three frozen runners, zero candidates and all independent histories",
    )
    return old, old_inputs, raw["svg"]


def large_fields(proof: dict) -> dict:
    return {
        "large_input_source_oracle": copy.deepcopy(proof),
        "large_input_source_sha256": LARGE["source"][1],
        "large_input_protocol_sha256": LARGE["protocol"][1],
        "large_input_contract_sha256": LARGE["contract"][1],
        "large_input_source_freeze_status":
            "SOURCE FROZEN; ORIGINAL 2-GIB TESTS AUTHENTICATED; "
            "CANDIDATES NOT RUN",
        "large_input_upstream_original_case_count": 2,
        "large_input_upstream_original_subject_bytes": LARGE_SUBJECT,
        "large_input_upstream_original_subn_count": LARGE_SUBN_COUNT,
        "large_input_cases_in_original_denominator": False,
        "large_input_cases_in_signature_denominator": False,
        "large_input_cases_in_public_denominator": False,
        "large_input_source_case_matrix_count": 32,
        "large_input_source_case_matrix_sha256": LARGE_MATRIX_SHA256,
        "large_input_source_case_rows": large_rows(),
        "large_input_source_case_status_counts": copy.deepcopy(LARGE_COUNTS),
        "large_input_source_case_pass_count": 22,
        "large_input_source_case_fail_count": 1,
        "large_input_source_case_not_run_count": 3,
        "large_input_source_case_not_established_count": 2,
        "large_input_source_case_not_measured_count": 3,
        "large_input_source_case_not_opened_count": 1,
        "large_input_source_owner_count": 32,
        "large_input_source_control_count": 330,
        "large_input_physically_blocked_effect_count": 28,
        "large_input_historical_reference_memory_policy_bytes":
            HISTORICAL_REFERENCE_MEMORY,
        "large_input_minimum_available_host_memory_bytes":
            MINIMUM_AVAILABLE_MEMORY,
        "large_input_actual_candidate_maximum_subject_bytes":
            CANDIDATE_SUBJECT_CAP,
        "large_input_actual_candidate_search_status": "NOT RUN",
        "large_input_actual_candidate_subn_status": "NOT RUN",
        "large_input_actual_candidate_qualification": "NOT ESTABLISHED",
        "large_input_actual_candidate_workers": 0,
        "large_input_actual_reference_workers_by_graph": 0,
        "large_input_actual_large_subject_allocations_by_graph": 0,
        "large_input_actual_host_memory_queries_by_graph": 0,
        "large_input_actual_stdlib_regex_imports_by_graph": 0,
        "large_input_actual_archive_reads_by_graph": 0,
        "large_input_actual_archive_inflations_by_graph": 0,
        "large_input_actual_candidate_imports_by_graph": 0,
        "large_input_actual_compiler_processes_by_graph": 0,
        "large_input_actual_native_activations_by_graph": 0,
        "large_input_actual_clock_samples_by_graph": 0,
        "large_input_actual_hidden_cases_read_by_graph": 0,
        "actual_large_subject_allocations_by_graph": 0,
        "actual_host_memory_queries_by_graph": 0,
        "actual_candidate_imports_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "candidate_matching_archives_opened_by_graph": 0,
        "reference_archive_gzip_inflation_count": 0,
        "matching_archive_gzip_inflation_count": 0,
        "source_build_archive_gzip_inflation_count_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "timing_trials_run": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }


def validate_snapshot(previous: types.ModuleType,
                      v45: types.ModuleType, v44: types.ModuleType,
                      v43: types.ModuleType, v42: types.ModuleType,
                      v41: types.ModuleType, v40: types.ModuleType,
                      base: types.ModuleType, snapshot: object) -> None:
    base.need(type(snapshot) is dict, "reject missing large-input graph snapshot")
    assert isinstance(snapshot, dict)
    proof = snapshot.get("large_input_source_oracle")
    validate_large_proof(base, proof)
    assert isinstance(proof, dict)
    updates = large_fields(proof)
    for key, value in updates.items():
        base.need(
            snapshot.get(key) == value,
            "reject invented large-input work or changed denominator: " + key,
        )
    replaced = snapshot.get("preserved_v46_replaced_snapshot_fields")
    base.need(type(replaced) is dict, "preserve each changed pushed V46 field")
    assert isinstance(replaced, dict)
    historical = copy.deepcopy(snapshot)
    historical.pop("preserved_v46_replaced_snapshot_fields", None)
    for key in updates:
        if key in replaced:
            historical[key] = copy.deepcopy(replaced[key])
        else:
            historical.pop(key, None)
    previous.validate_snapshot(
        v45, v44, v43, v42, v41, v40, base, historical,
    )
    base.need(
        set(replaced).issubset(updates)
        and snapshot.get("full_case_denominator") == 31237
        and snapshot.get("suite_count") == 13
        and snapshot.get("private_waiver_count") == 13
        and snapshot.get("supplementary_signature_check_count") == 50
        and snapshot.get("public_entrypoint_case_matrix_count") == 32
        and snapshot.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and snapshot.get("public_entrypoint_status") == PUBLIC_STATUS
        and snapshot.get("large_input_upstream_original_case_count") == 2
        and snapshot.get("large_input_upstream_original_subject_bytes")
        == LARGE_SUBJECT
        and snapshot.get("large_input_source_case_matrix_count") == 32
        and snapshot.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and snapshot.get("large_input_actual_candidate_maximum_subject_bytes")
        == CANDIDATE_SUBJECT_CAP
        and snapshot.get("large_input_actual_candidate_search_status")
        == "NOT RUN"
        and snapshot.get("large_input_actual_candidate_subn_status")
        == "NOT RUN"
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 166
        and snapshot.get("authenticated_history_reference_lower_bound") == 171
        and snapshot.get("first_party_source_inventory_family_count") == 6
        and snapshot.get("frozen_corrected_runner_source_family_count") == 3
        and snapshot.get("frozen_corrected_runner_source_families")
        == ["c", "rust", "zig"]
        and snapshot.get("actually_runnable_candidate_family_count") == 0
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("actual_rust_source_build_archive_read_count") == 1
        and snapshot.get("source_build_archive_gzip_inflation_count_by_graph")
        == 0
        and snapshot.get("final_comparison_planned_case_count") == 4194304
        and snapshot.get("final_comparison_cases_generated") is False
        and snapshot.get("final_holdout_opened") is False,
        "preserve all four distinct denominators, actual 2-GiB requirements, "
        "zero candidate work, genuine Rust history and unopened holdout",
    )


def make_svg(previous: types.ModuleType,
             v45: types.ModuleType, v44: types.ModuleType,
             v43: types.ModuleType, v42: types.ModuleType,
             v41: types.ModuleType, v40: types.ModuleType,
             base: types.ModuleType, snapshot: dict, old_svg: bytes,
             source_sha: str, inputs_sha: str) -> bytes:
    validate_snapshot(
        previous, v45, v44, v43, v42, v41, v40, base, snapshot,
    )
    source_sha = base.checked(source_sha, "actual current V47 renderer footer")
    inputs_sha = base.checked(inputs_sha, "actual current V47 inputs footer")
    visible = old_svg.decode("utf-8")
    visible = visible.replace("v46-title", "v47-title")
    visible = visible.replace("v46-description", "v47-description")
    replacements = (
        (
            "three candidate test runners prepared; no replacement is "
            "yet compatible or faster</title>",
            "real 2-gigabyte tests frozen; no replacement is yet "
            "compatible or faster</title>",
            "state the real large-input obligations in plain language",
        ),
        (
            "A separate 32-observation public audit finds",
            "Two actual original CPython tests each require a "
            "2,147,483,648-byte subject. A separate 32-observation "
            "large-input source audit finds 22 passes, 1 existing public "
            "failure, 3 not run, 2 not established, 3 not measured and "
            "1 unopened holdout; no candidate has run either large-input "
            "test. A separate 32-observation public audit finds",
            "keep the two unrelated 32-observation matrices distinct",
        ),
        (
            "31,237 original checks; 50 separate signature checks; "
            "32 separate public-import observations; zero qualified "
            "replacements.",
            "31,237 original checks; 50 signatures; 32 public observations; "
            "2 upstream large-input tests; zero qualified replacements.",
            "visibly distinguish the original, signature, public and 2-GiB counts",
        ),
        (
            'height="3010" viewBox="0 0 1440 3010"',
            'height="3280" viewBox="0 0 1440 3280"',
            "make room for legible large-input observations and provenance",
        ),
        (
            '<rect width="1440" height="3010" rx="22"',
            '<rect width="1440" height="3280" rx="22"',
            "extend the readable background over all exact footer history",
        ),
    )
    for before, after, label in replacements:
        visible = v43.replace_once(base, visible, before, after, label)
    visible = v43.replace_once(
        base, visible,
        "Graph inputs SHA-256: " + V46["inputs"][1],
        "Graph inputs SHA-256: " + inputs_sha,
        "label only the current V47 input owner digest",
    )
    visible = v43.replace_once(
        base, visible,
        "Graph renderer SHA-256: " + V46["source"][1],
        "Graph renderer SHA-256: " + source_sha,
        "label only the current V47 renderer owner digest",
    )
    lines = [v42.move_y(line, 200) for line in visible.splitlines()]
    insertion = next(
        index + 1 for index, line in enumerate(lines)
        if "source-tested only; C has not run." in line
    )
    lines[insertion:insertion] = [
        '<rect x="44" y="302" width="1352" height="185" rx="14" '
        'fill="#eef5ff" stroke="#b6cbee"/>',
        '<text x="65" y="335" class="warning">TWO REAL 2-GIGABYTE '
        'PYTHON TESTS FROZEN; NO CANDIDATE HAS RUN THEM</text>',
        '<text x="67" y="362" class="body">Each original test needs '
        '2,147,483,648 bytes. The largest real candidate subject was only '
        '5,147 bytes.</text>',
        '<rect x="68" y="378" width="814" height="21" rx="5" '
        'fill="#268256"/>',
        '<rect x="882" y="378" width="37" height="21" '
        'fill="#bf5a43"/>',
        '<rect x="919" y="378" width="111" height="21" '
        'fill="#7086a1"/>',
        '<rect x="1030" y="378" width="74" height="21" '
        'fill="#bf9439"/>',
        '<rect x="1104" y="378" width="111" height="21" '
        'fill="#94a1b3"/>',
        '<rect x="1215" y="378" width="37" height="21" rx="5" '
        'fill="#7463a4"/>',
        '<text x="68" y="424" class="small">22 source checks pass</text>',
        '<text x="267" y="424" class="small">1 existing public failure</text>',
        '<text x="468" y="424" class="small">3 not run</text>',
        '<text x="628" y="424" class="small">2 not established</text>',
        '<text x="821" y="424" class="small">3 not measured</text>',
        '<text x="1022" y="424" class="small">1 holdout not opened</text>',
        '<text x="67" y="453" class="body">Historical Python memory '
        'allowance: 42,949,672,960 bytes. These 32 source observations are '
        'separate from all other case counts.</text>',
        '<text x="67" y="476" class="small">No 2-gigabyte allocation, '
        'candidate, compiler, benchmark, archive or holdout was run.</text>',
    ]
    historical = next(
        index for index, line in enumerate(lines)
        if line.startswith("<!-- Zig source correction is frozen only;")
    )
    lines[historical:historical] = [
        '<text x="47" y="3180" class="foot">Historical V46 graph '
        'inputs SHA-256: ' + V46["inputs"][1] + '</text>',
        '<text x="47" y="3202" class="foot">Historical V46 graph '
        'renderer SHA-256: ' + V46["source"][1] + '</text>',
    ]
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    current_inputs = ("Graph inputs SHA-256: " + inputs_sha).encode("ascii")
    current_source = ("Graph renderer SHA-256: " + source_sha).encode("ascii")
    historical_inputs = (
        "Historical V46 graph inputs SHA-256: " + V46["inputs"][1]
    ).encode("ascii")
    historical_source = (
        "Historical V46 graph renderer SHA-256: " + V46["source"][1]
    ).encode("ascii")
    base.need(
        raw.count(current_inputs) == 1
        and raw.count(current_source) == 1
        and raw.count(historical_inputs) == 1
        and raw.count(historical_source) == 1
        and (
            "Graph inputs SHA-256: " + V46["inputs"][1]
        ).encode("ascii") not in raw
        and (
            "Graph renderer SHA-256: " + V46["source"][1]
        ).encode("ascii") not in raw,
        "show actual current V47 footers and explicitly historical V46 digests",
    )
    lower = raw.lower()
    for phrase in (
        b"real 2-gigabyte tests frozen",
        b"two real 2-gigabyte python tests frozen",
        b"no candidate has run them",
        b"2,147,483,648",
        b"5,147",
        b"42,949,672,960",
        b"22 source checks pass",
        b"1 existing public failure",
        b"3 not run",
        b"2 not established",
        b"3 not measured",
        b"1 holdout not opened",
        b"32 source observations are separate",
        b"31,237 original checks",
        b"50 signatures",
        b"32 public observations",
        b"17 source observations pass",
        b"7 actual public checks fail",
        b"6 not measured",
        b"1 not established",
        b"1 not opened",
        b"three first-party runners prepared",
        b"zero usable or qualified replacements",
        b"1,036",
        b"1,087",
        b"1,230",
        b"1,764",
        b"2,172",
        b"166 / 171",
        b"4,194,304",
        b"not opened",
    ):
        base.need(
            phrase.lower() in lower,
            "reject an omitted large-input denominator or real history: "
            + repr(phrase),
        )
    for lie in (
        b"2-gigabyte candidate passes",
        b"22 candidate passes",
        b"candidate large-input passed",
        b"candidate large input passed",
        b"three runnable candidates",
        b"zig compiler executed",
        b"winner selected",
        b"31,269 original cases",
    ):
        base.need(lie not in lower, "reject invented large-input success")
    base.need(
        raw.endswith(b"\n") and not raw.endswith(b"\n\n"),
        "render exactly one final SVG linefeed",
    )
    return raw


def build(previous: types.ModuleType,
          v45: types.ModuleType, v44: types.ModuleType,
          v43: types.ModuleType, v42: types.ModuleType,
          v41: types.ModuleType, v40: types.ModuleType,
          base: types.ModuleType, options: argparse.Namespace) -> tuple[
              dict, tuple[tuple[str, bytes], ...],
          ]:
    source_sha = base.checked(options.source_sha256, "exact V47 graph source")
    base.need(
        type(options.source_bytes) is int
        and 0 < options.source_bytes <= base.OWNER_LIMIT,
        "require the independently supplied V47 renderer byte count",
    )
    own_raw, _ = base.read_owner(
        SELF, source_sha, options.source_bytes, private=True,
    )
    old, old_inputs, old_svg = authenticate_v46(
        previous, v45, v44, v43, v42, v41, v40, base,
        {
            "source": options.previous_source_sha256,
            "inputs": options.previous_inputs_sha256,
            "summary": options.previous_summary_sha256,
            "svg": options.previous_svg_sha256,
        },
    )
    proof = authenticate_large(
        base,
        {
            "source": options.large_source_sha256,
            "protocol": options.large_protocol_sha256,
            "contract": options.large_contract_sha256,
        },
    )
    historical_snapshot = old["snapshot"]
    updates = large_fields(proof)
    snapshot = copy.deepcopy(historical_snapshot)
    snapshot.update(updates)
    snapshot["preserved_v46_replaced_snapshot_fields"] = {
        key: copy.deepcopy(historical_snapshot[key])
        for key in updates if key in historical_snapshot
    }
    validate_snapshot(
        previous, v45, v44, v43, v42, v41, v40, base, snapshot,
    )
    predecessors = {role: base.pin(*pin) for role, pin in V46.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 47,
        "python": "3.14.6",
        "renderer": base.pin(SELF, source_sha, len(own_raw)),
        "previous_overview": predecessors,
        **updates,
    })
    input_raw = base.canonical(inputs)
    svg = make_svg(
        previous, v45, v44, v43, v42, v41, v40, base,
        snapshot, old_svg, source_sha, base.digest(input_raw),
    )
    families = copy.deepcopy(old["families"])
    base.need(
        [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "preserve Python and all six independent first-party families",
    )
    for row in families:
        if row.get("family") == "python":
            row.update({
                "historical_large_input_reference_status":
                    "PASS; HISTORICAL PINNED MANIFEST EVIDENCE",
                "historical_large_input_reference_rerun_by_graph": False,
            })
            continue
        row.update({
            "large_input_candidate_search_status": "NOT RUN",
            "large_input_candidate_subn_status": "NOT RUN",
            "large_input_candidate_qualification": "NOT ESTABLISHED",
            "large_input_actual_candidate_workers": 0,
            "large_input_actual_subject_cap_bytes": CANDIDATE_SUBJECT_CAP,
            "qualified": False,
            "performance": "NOT MEASURED",
        })
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 47,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, source_sha, len(own_raw)),
        "inputs": base.pin(
            OUTPUT + ".inputs.json", base.digest(input_raw), len(input_raw),
        ),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg), len(svg)),
        "previous_overview": predecessors,
        "snapshot": snapshot,
        "families": families,
        **updates,
    })
    summary_raw = base.canonical(summary)
    base.need(
        len(input_raw) <= base.OWNER_LIMIT
        and len(summary_raw) <= base.OWNER_LIMIT
        and len(svg) <= base.OWNER_LIMIT,
        "bound all complete V47 outputs without omitting source history",
    )
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )


def synthetic_proof(base: types.ModuleType) -> dict:
    owners = {
        role: base.synthetic_owner(pin, 947000 + index)
        for index, (role, pin) in enumerate(LARGE.items())
    }
    return make_large_proof(
        base, owners, expected_contract(base), expected_large_ast(base),
    )


def reject_control(base: types.ModuleType, proof: dict,
                   description: str) -> int:
    try:
        validate_large_proof(base, proof)
    except (
        base.GraphError, TypeError, ValueError, KeyError,
        AttributeError, RecursionError,
    ):
        return 1
    raise base.GraphError("accepted forged large-input proof: " + description)


def self_test(previous: types.ModuleType,
              v45: types.ModuleType, v44: types.ModuleType,
              v43: types.ModuleType, v42: types.ModuleType,
              v41: types.ModuleType, v40: types.ModuleType,
              base: types.ModuleType) -> dict:
    history = previous.self_test(v45, v44, v43, v42, v41, v40, base)
    base.need(
        history.get("status") == "PASS"
        and history.get("rejected_hostile_control_count") == 1718
        and history.get("reference_archive_gzip_inflation_count") == 0
        and history.get("matching_archive_gzip_inflation_count") == 0
        and history.get("source_build_archive_gzip_inflation_count_by_graph")
        == 0
        and history.get("frozen_corrected_runner_source_family_count") == 3
        and history.get("actually_runnable_candidate_family_count") == 0,
        "preserve all 1,718 pushed V46 source-only hostile controls",
    )
    rejected = 0
    with base.SourceOnlyWall() as wall:
        proof = synthetic_proof(base)
        for name, value in proof.items():
            hostile = copy.deepcopy(proof)
            hostile[name] = v43.forged_value(base, value)
            rejected += reject_control(base, hostile, name)
        for role in LARGE:
            for name, value in proof[role].items():
                hostile = copy.deepcopy(proof)
                hostile[role][name] = v43.forged_value(base, value)
                rejected += reject_control(base, hostile, role + ":" + name)
        for name, value in proof["source_ast"].items():
            hostile = copy.deepcopy(proof)
            hostile["source_ast"][name] = v43.forged_value(base, value)
            rejected += reject_control(base, hostile, "source-ast:" + name)
        contract = proof["complete_frozen_contract"]
        for name, value in contract.items():
            hostile = copy.deepcopy(proof)
            hostile["complete_frozen_contract"][name] = (
                v43.forged_value(base, value)
            )
            rejected += reject_control(base, hostile, "contract:" + name)
        for group in (
            "pinned_runtime", "original_correctness", "upstream_large_input",
            "historical_full_resource_reference", "actual_candidate_large_input",
            "public_entrypoint_preservation", "corrected_rust_preservation",
            "released_zig_v1_preservation", "future_execution_policy",
            "boundaries",
        ):
            for name, value in contract[group].items():
                hostile = copy.deepcopy(proof)
                hostile["complete_frozen_contract"][group][name] = (
                    v43.forged_value(base, value)
                )
                rejected += reject_control(
                    base, hostile, "contract:" + group + ":" + name,
                )
        for index, row in enumerate(large_rows()):
            hostile = copy.deepcopy(proof)
            hostile["complete_frozen_contract"]["case_matrix"][index]["status"] = (
                "FAIL" if row["status"] == "PASS" else "PASS"
            )
            rejected += reject_control(base, hostile, "case:" + row["id"])
        for role, owner in contract["owners"].items():
            hostile = copy.deepcopy(proof)
            hostile["complete_frozen_contract"]["owners"][role]["sha256"] = (
                v43.forged_value(base, owner["sha256"])
            )
            rejected += reject_control(base, hostile, "source-owner:" + role)
        probes = (
            ("filesystem", lambda: builtins.open("forbidden-v47")),
            ("filesystem", lambda: os.open("forbidden-v47", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v47")),
            ("write", lambda: os.mkdir("forbidden-v47")),
            ("process", lambda: subprocess.run(("forbidden-v47",))),
            ("process", lambda: subprocess.Popen(("forbidden-v47",))),
            ("process", lambda: os.execv("/forbidden-v47", [])),
        )
        for kind, action in probes:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(
                    wall.blocked[kind] == before + 1,
                    "physically block the real V47 source-only " + kind,
                )
            else:
                raise base.GraphError("a forbidden V47 source effect escaped")
        base.need(
            rejected >= 200,
            "reject every giant-input owner, matrix, resource and effect forgery",
        )
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 47,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v46_hostile_controls":
                history["rejected_hostile_control_count"],
            "new_v47_hostile_controls": rejected,
            "rejected_hostile_control_count":
                history["rejected_hostile_control_count"] + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "actual_large_source_owners_read_by_self_test": 0,
            "actual_large_subject_allocations_by_graph": 0,
            "actual_host_memory_queries_by_graph": 0,
            "actual_candidate_imports_by_graph": 0,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "actual_native_libraries_loaded_by_graph": 0,
            "reference_archive_gzip_inflation_count": 0,
            "matching_archive_gzip_inflation_count": 0,
            "source_build_archive_gzip_inflation_count_by_graph": 0,
            "actual_clock_samples_by_graph": 0,
            "actual_hidden_cases_read_by_graph": 0,
            "full_case_denominator": 31237,
            "suite_count": 13,
            "private_waiver_count": 13,
            "supplementary_signature_check_count": 50,
            "public_entrypoint_case_matrix_count": 32,
            "public_entrypoint_case_status_counts": copy.deepcopy(PUBLIC_COUNTS),
            "public_entrypoint_status": PUBLIC_STATUS,
            "large_input_upstream_original_case_count": 2,
            "large_input_upstream_original_subject_bytes": LARGE_SUBJECT,
            "large_input_source_case_matrix_count": 32,
            "large_input_source_case_matrix_sha256": LARGE_MATRIX_SHA256,
            "large_input_source_case_status_counts": copy.deepcopy(LARGE_COUNTS),
            "large_input_source_control_count": 330,
            "large_input_physically_blocked_effect_count": 28,
            "large_input_actual_candidate_maximum_subject_bytes":
                CANDIDATE_SUBJECT_CAP,
            "large_input_actual_candidate_search_status": "NOT RUN",
            "large_input_actual_candidate_subn_status": "NOT RUN",
            "authenticated_evidence_owner_lower_bound": 166,
            "authenticated_history_reference_lower_bound": 171,
            "first_party_source_inventory_family_count": 6,
            "frozen_corrected_runner_source_family_count": 3,
            "frozen_corrected_runner_source_families": ["c", "rust", "zig"],
            "actually_runnable_candidate_family_count": 0,
            "qualified_candidate_count": 0,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path in {
            OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg",
        }
        and type(raw) is bytes and 0 < len(raw) <= base.OWNER_LIMIT,
        "write only the three expressly authorized new V47 graph assets",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            written = os.write(descriptor, remaining)
            base.need(
                type(written) is int and written > 0,
                "reject incomplete independently owned V47 graph bytes",
            )
            remaining = remaining[written:]
        os.fsync(descriptor)
        owner = os.fstat(descriptor)
        base.need(
            owner.st_uid == os.geteuid()
            and owner.st_nlink == 1
            and owner.st_size == len(raw)
            and stat.S_IMODE(owner.st_mode) == 0o600,
            "publish one complete private independently owned V47 graph",
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
    base.need(observed == raw, "re-authenticate complete V47 graph output")


def result(base: types.ModuleType, snapshot: dict,
           outputs: dict[str, bytes], source_sha: str,
           *, written: bool, suffix: str) -> dict:
    keys = (
        "full_case_denominator", "suite_count", "private_waiver_count",
        "supplementary_signature_check_count",
        "public_entrypoint_case_matrix_count",
        "public_entrypoint_case_matrix_sha256",
        "public_entrypoint_case_status_counts", "public_entrypoint_status",
        "large_input_source_sha256", "large_input_protocol_sha256",
        "large_input_contract_sha256", "large_input_source_freeze_status",
        "large_input_upstream_original_case_count",
        "large_input_upstream_original_subject_bytes",
        "large_input_upstream_original_subn_count",
        "large_input_cases_in_original_denominator",
        "large_input_cases_in_signature_denominator",
        "large_input_cases_in_public_denominator",
        "large_input_source_case_matrix_count",
        "large_input_source_case_matrix_sha256",
        "large_input_source_case_status_counts",
        "large_input_source_control_count",
        "large_input_physically_blocked_effect_count",
        "large_input_historical_reference_memory_policy_bytes",
        "large_input_minimum_available_host_memory_bytes",
        "large_input_actual_candidate_maximum_subject_bytes",
        "large_input_actual_candidate_search_status",
        "large_input_actual_candidate_subn_status",
        "large_input_actual_candidate_qualification",
        "large_input_actual_candidate_workers",
        "actual_large_subject_allocations_by_graph",
        "actual_host_memory_queries_by_graph",
        "first_party_source_inventory_family_count",
        "frozen_corrected_runner_source_family_count",
        "frozen_corrected_runner_source_families",
        "actually_runnable_candidate_family_count",
        "actually_runnable_candidate_families", "qualified_candidate_count",
        "actual_rust_source_build_archive_read_count",
        "actual_rust_source_build_archive_gzip_inflation_count",
        "authenticated_evidence_owner_lower_bound",
        "authenticated_history_reference_lower_bound",
        "actual_candidate_imports_by_graph",
        "actual_candidate_workers_started_by_graph",
        "actual_reference_workers_started_by_graph",
        "actual_compiler_processes_started_by_graph",
        "actual_native_libraries_loaded_by_graph",
        "reference_archive_gzip_inflation_count",
        "matching_archive_gzip_inflation_count",
        "source_build_archive_gzip_inflation_count_by_graph",
        "actual_clock_samples_by_graph", "clock_samples",
        "hidden_cases_read", "timing_trials_run",
        "runtime_no_delegation", "performance", "memory",
        "confidence_intervals", "undefined_behavior",
        "final_comparison_planned_case_count",
        "final_comparison_cases_generated", "final_holdout_opened",
        "winner_selected",
    )
    return {
        "schema": SCHEMA + suffix,
        "version": 47,
        "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 46,
        **{
            "previous_overview_" + role + "_sha256": pin[1]
            for role, pin in V46.items()
        },
        "outputs_written": written,
        **{key: copy.deepcopy(snapshot[key]) for key in keys},
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
    parser.add_argument("--large-source-sha256")
    parser.add_argument("--large-protocol-sha256")
    parser.add_argument("--large-contract-sha256")
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, v45, v44, v43, v42, v41, v40, base = load_v46()
        if options.self_test:
            base.need(
                all(
                    getattr(options, name) is None
                    for name in (
                        "source_sha256", "source_bytes",
                        "previous_source_sha256", "previous_inputs_sha256",
                        "previous_summary_sha256", "previous_svg_sha256",
                        "large_source_sha256", "large_protocol_sha256",
                        "large_contract_sha256", "inputs_sha256",
                        "summary_sha256", "svg_sha256",
                    )
                ),
                "synthetic-only V47 self-test cannot accept actual owner pins",
            )
            sys.stdout.buffer.write(base.canonical(self_test(
                previous, v45, v44, v43, v42, v41, v40, base,
            )))
            return 0
        snapshot, pairs = build(
            previous, v45, v44, v43, v42, v41, v40, base, options,
        )
        outputs = dict(pairs)
        source_sha = base.checked(
            options.source_sha256, "exact V47 source renderer",
        )
        if options.render:
            base.need(
                options.inputs_sha256 is None
                and options.summary_sha256 is None
                and options.svg_sha256 is None,
                "render exactly the three authorized fresh V47 graph assets",
            )
            for path, raw in pairs:
                publish(base, path, raw)
            sys.stdout.buffer.write(base.canonical(result(
                base, snapshot, outputs, source_sha,
                written=True, suffix="-published",
            )))
            return 0
        expected = {
            OUTPUT + ".inputs.json": base.checked(
                options.inputs_sha256, "exact large-input V47 graph inputs",
            ),
            OUTPUT + ".json": base.checked(
                options.summary_sha256, "exact large-input V47 graph summary",
            ),
            OUTPUT + ".svg": base.checked(
                options.svg_sha256, "exact readable V47 large-input graph",
            ),
        }
        for path, fingerprint in expected.items():
            observed, _ = base.read_owner(
                path, fingerprint, len(outputs[path]), private=True,
            )
            base.need(
                observed == outputs[path],
                "reproduce every exact source-only V47 graph output byte",
            )
        sys.stdout.buffer.write(base.canonical(result(
            base, snapshot, outputs, source_sha,
            written=False, suffix="-read-only-frozen-context",
        )))
        return 0
    except (
        ValueError, OSError, TypeError, EOFError, KeyError,
        AttributeError, RecursionError,
    ) as error:
        sys.stderr.write("current V47 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V47 overview rejected: " + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
