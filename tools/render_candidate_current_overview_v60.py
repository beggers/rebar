#!/usr/bin/env python3
"""Report the actual failed regex test and a not-yet-run source build."""

from __future__ import annotations

import argparse
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
SELF = "tools/render_candidate_current_overview_v60.py"
OUTPUT = "docs/evidence/candidate-current-overview-v60"
SCHEMA = "rebar-candidate-current-overview-v60"
V59 = {
    "source": (
        "tools/render_candidate_current_overview_v59.py",
        "a5716931d30ab5f4dcb2bf5efa0bdb3fd24f7bad48f6ed77b5dce3714e547677",
        65821,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v59.inputs.json",
        "044d243432850b6eaa9f0d54b7bd8f77967dd0c234bfb64af9d37e27888e9fa3",
        902467,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v59.json",
        "73dd4701a9613795aeafa60c1b76a98900a5020dbe31a78fdc1922b534a4c0b0",
        2457553,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v59.svg",
        "9b3d0942adcd9bc29d13d895ba5e7a0acc2626520f1392a1c686ce341de43abe",
        14612,
    ),
}
BUILD = {
    "source": (
        "tools/reproduce_owned_rust_buffer_shape_source_build_v17.py",
        "192062b278aaf5a7a3097d9b5d15218d8d26893a3a8e716fe585f217eeff3471",
        107961,
    ),
    "protocol": (
        "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V17.md",
        "c53db893fce626325f806eb99868b900a35cbc220d9bbc5a9663aecdd2cadef3",
        6694,
    ),
    "contract": (
        "oracle/phase2/rust-buffer-shape-source-build-v17.json",
        "55809f7549dc138be966eaa4b8eaedac444cdcc7b84f4450f351738e4b59ad7b",
        16104,
    ),
}
BUILD_INODES = {
    "source": 432169,
    "protocol": 525064,
    "contract": 525065,
}
PUBLIC_COUNTS = {
    "PASS": 17, "FAIL": 7, "NOT MEASURED": 6,
    "NOT ESTABLISHED": 1, "NOT OPENED": 1,
}
LARGE_COUNTS = {
    "PASS": 22, "FAIL": 1, "NOT RUN": 3,
    "NOT ESTABLISHED": 2, "NOT MEASURED": 3, "NOT OPENED": 1,
}
WORKERS = [81, 87, 88, 89, 90, 91, 92, 93, 94, 95, 196, 197, 198]


def load_v59() -> tuple:
    path, fingerprint, size = V59["source"]
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags)
    try:
        before = os.fstat(handle)
        if (not stat.S_ISREG(before.st_mode)
                or before.st_uid != os.geteuid()
                or before.st_nlink != 1
                or stat.S_IMODE(before.st_mode) != 0o600
                or before.st_size != size):
            raise ValueError("reject substituted exact pushed V59 source")
        parts = []
        remaining = size
        while remaining:
            part = os.read(handle, min(remaining, 262144))
            if not part:
                raise ValueError("reject truncated pushed V59 source")
            parts.append(part)
            remaining -= len(part)
        if os.read(handle, 1):
            raise ValueError("reject extended pushed V59 source")
        raw = b"".join(parts)
        after = os.fstat(handle)
        if (hashlib.sha256(raw).hexdigest() != fingerprint
                or (before.st_dev, before.st_ino, before.st_size,
                    before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                != (after.st_dev, after.st_ino, after.st_size,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)):
            raise ValueError("reject changed exact pushed V59 source")
    finally:
        os.close(handle)
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v59")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    prior_modules = previous.load_v58()
    base = prior_modules[-1]
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v59"
        and previous.SELF == path
        and previous.PUBLIC_COUNTS == PUBLIC_COUNTS
        and previous.LARGE_COUNTS == LARGE_COUNTS
        and previous.WORKERS == WORKERS,
        "authenticate only exact pushed current V59 graph source",
    )
    return previous, prior_modules, base


def v59_options(previous: types.ModuleType) -> argparse.Namespace:
    return argparse.Namespace(
        source_sha256=V59["source"][1],
        source_bytes=V59["source"][2],
        previous_source_sha256=previous.V58["source"][1],
        previous_inputs_sha256=previous.V58["inputs"][1],
        previous_summary_sha256=previous.V58["summary"][1],
        previous_svg_sha256=previous.V58["svg"][1],
        feature_bridge_source_sha256=previous.FEATURE["bridge_source"][1],
        feature_applicator_sha256=previous.FEATURE["applicator"][1],
        feature_protocol_sha256=previous.FEATURE["protocol"][1],
        feature_contract_sha256=previous.FEATURE["contract"][1],
        inputs_sha256=None,
        summary_sha256=None,
        svg_sha256=None,
    )


def authenticate_v59(modules: tuple,
                     supplied: dict[str, str]) -> tuple[dict, dict, bytes]:
    previous, prior_modules, base = modules
    raw = {}
    for role, item in V59.items():
        base.need(
            base.checked(supplied.get(role), "pushed actual V59 " + role)
            == item[1],
            "reject substituted actual pushed V59 " + role,
        )
        raw[role], _ = base.read_owner(*item, private=True)
    old = base.document(raw["summary"], "complete pushed V59 summary")
    inputs = base.document(raw["inputs"], "complete pushed V59 inputs")
    previous.validate_snapshot(prior_modules, old.get("snapshot"))
    reconstructed, pairs = previous.build(prior_modules, v59_options(previous))
    expected = dict(pairs)
    base.need(
        old.get("schema") == "rebar-candidate-current-overview-v59-summary"
        and old.get("version") == 59
        and old.get("status") == "PASS"
        and old.get("source") == base.pin(*V59["source"])
        and old.get("inputs") == base.pin(*V59["inputs"])
        and old.get("svg") == base.pin(*V59["svg"])
        and inputs.get("schema")
            == "rebar-candidate-current-overview-v59-inputs"
        and inputs.get("version") == 59
        and inputs.get("renderer") == base.pin(*V59["source"])
        and old.get("snapshot") == reconstructed
        and raw["inputs"] == expected[V59["inputs"][0]]
        and raw["summary"] == expected[V59["summary"][0]]
        and raw["svg"] == expected[V59["svg"][0]]
        and old.get("actual_rust_semantic_mismatch_count") == 1440
        and old.get("actual_rust_verified_passing_case_count") == 14853
        and old.get("rust_original_campaign_semantic_mismatch_count") == 1440
        and old.get("rust_original_campaign_verified_passing_case_count")
            == 14853
        and old.get("actual_rust_v7_semantic_mismatch_count") == 928
        and old.get(
            "actual_rust_v7_explicitly_verified_passing_case_count") == 8965
        and old.get("actual_rust_v10_candidate_status") == "FAIL"
        and old.get("actual_rust_v10_semantic_mismatch_count") == 1440
        and old.get("actual_rust_v10_verified_passing_case_count") == 14853
        and old.get("actual_rust_v10_semantic_mismatch_regression_against_v7")
            == 512
        and old.get("actual_rust_v10_candidate_workers") == 13
        and old.get("actual_rust_v10_worker_process_ids") == WORKERS
        and old.get("actual_rust_v10_infrastructure_failure_count") == 0
        and old.get("actual_rust_v10_all_four_original_targets_restored")
            is True
        and len(old.get(
            "actual_rust_v10_complete_independently_authenticated_suite_results",
            [],
        )) == 13
        and len(old.get("actual_rust_v10_earliest_genuine_mismatch_witnesses",
                        [])) == 6
        and old.get("rust_buffer_shape_v2_feature_status") == "SOURCE FROZEN"
        and old.get("rust_buffer_shape_v2_build_status") == "NOT BUILT"
        and old.get("rust_buffer_shape_v2_matching_status") == "NOT RUN"
        and old.get("rust_buffer_shape_v2_candidate_workers_started") == 0
        and old.get("rust_buffer_shape_v2_independent_source_owner_count") == 4
        and old.get("authenticated_evidence_owner_lower_bound") == 201
        and old.get("authenticated_history_reference_lower_bound") == 206
        and old.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and old.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and old.get("first_party_source_inventory_family_count") == 6
        and old.get("qualified_candidate_count") == 0
        and old.get("final_comparison_planned_case_count") == 4194304
        and old.get("final_comparison_cases_generated") is False
        and old.get("final_holdout_opened") is False,
        "reproduce actual V59 aliases, genuine failure and unbuilt V2",
    )
    return old, inputs, raw["svg"]




BUILD_CONTRACT_EXPECTATIONS = {
    "actual_previous_rust_result": {
        "candidate_qualified": False,
        "completed_suite_count": 13,
        "durable_failure_receipt": {
            "bytes": 6708,
            "device": 2064,
            "inode": 525044,
            "path": "oracle/phase2/evidence/repaired-rust-original-campaign-v10-rust-phase2-v16-rust-buffer-shape-pickle-original-p0-v10-failures-publication-receipt.json",
            "sha256": "8735e5351f62de2a77369eb8401e225cebd31434b09f07db40e79550ba7cc7d2",
        },
        "explicitly_verified_passing_case_count": 14853,
        "forensic_summary": {
            "bytes": 24701,
            "device": 2064,
            "inode": 525045,
            "path": "oracle/phase2/evidence/repaired-rust-original-campaign-v10-rust-phase2-v16-rust-buffer-shape-pickle-original-p0-v10-failures-forensic-summary.json",
            "sha256": "6e04771a48b4a460ad58ac9795ef91a697a33fa0aeae4671c9b3c9b35e4820cd",
        },
        "genuine_failure_categories": {
            "managed_v1": 16,
            "shape_v2": 1056,
            "substitution_v2": 368,
        },
        "historical_v7_mismatch_count": 928,
        "historical_v7_verified_passing_case_count": 8965,
        "infrastructure_failure_count": 0,
        "mismatch_regression_against_v7": 512,
        "semantic_mismatch_count": 1440,
        "status": "FAIL",
        "verified_passes_derived_by_subtraction": False,
        "worker_count": 13,
    },
    "authenticated_low_level_first_party_kernels": {
        "source_only_kernel_execution": False,
        "v7": [
            {
                "bytes": 300624,
                "device": 2064,
                "inode": 431752,
                "path": "tools/reproduce_owned_native_source_build_v7.py",
                "sha256": "20d8e43a9c70f585049f81d38f9085661b50e4bf754320a6abcd95d566d854a7",
            },
            {
                "bytes": 8063,
                "device": 2064,
                "inode": 524508,
                "path": "oracle/phase2/NATIVE-SOURCE-BUILD-V7.md",
                "sha256": "a7a5ce16bb7a98dfd6e0e4f9f3777912687aa09259cc1669c5e0932da2287313",
            },
            {
                "bytes": 28924,
                "device": 2064,
                "inode": 524509,
                "path": "oracle/phase2/native-source-build-v7.json",
                "sha256": "cfc774cfce1a0c4298f01e298d7ffaa982300375ba117e316bff2ebbf0be7819",
            },
        ],
        "v9": [
            {
                "bytes": 81124,
                "device": 2064,
                "inode": 429976,
                "path": "tools/reproduce_owned_native_source_build_v9.py",
                "sha256": "c4a4b85b92ef0d600528732c9e0acb8f8303b7b2fbfc320e84c9b9e2d384219f",
            },
            {
                "bytes": 4960,
                "device": 2064,
                "inode": 524423,
                "path": "oracle/phase2/NATIVE-SOURCE-BUILD-V9.md",
                "sha256": "18494d4b778a3c958b07903996e8a1b13f4466e08b2c9e72cd5d711957dbcecc",
            },
            {
                "bytes": 9134,
                "device": 2064,
                "inode": 524424,
                "path": "oracle/phase2/native-source-build-v9.json",
                "sha256": "6a4aee7f0c639b2b338d1497c35a69d35939841cf55b0dbe38abe404cea404da",
            },
        ],
    },
    "corrected_v4_candidate_facing_reference": {
        "actual_v10_used_corrected_v4_context": True,
        "corrected_cache_records_sha256": "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad",
        "corrected_full_records_sha256": "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2",
        "corrected_reference_receipt": {
            "bytes": 2509,
            "device": 2064,
            "inode": 524769,
            "path": "oracle/phase1/evidence/public-type-reference-context-v1-cpython-3-14-6-candidate-context-p0-publication-receipt.json",
            "sha256": "ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966",
        },
        "falsified_historical_receipt_sha256": "6a8ce4334d0b605483e0f78a909f620a8bcdd0e5ad8cdb4fae4960fc237132fd",
        "falsified_historical_records_sha256": "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21",
        "falsified_historical_reference_process_ids": [
            82,
            83,
        ],
        "historical_reference_falsification": {
            "bytes": 3892,
            "device": 2064,
            "inode": 524739,
            "path": "oracle/phase1/evidence/public-type-candidate-context-falsification-v1.json",
            "sha256": "319f0f75aaaea16fd1f41d814785d67060c57060852893349366cc3b482c4670",
        },
        "historical_reference_status": "FALSIFIED",
        "phase1_canonical_candidate_context_crosswalk": "NOT ESTABLISHED",
        "producer_contract": {
            "bytes": 30867,
            "device": 2064,
            "inode": 524783,
            "path": "oracle/phase2/six-family-p0-producer-v4.json",
            "sha256": "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5",
        },
        "producer_protocol": {
            "bytes": 5981,
            "device": 2064,
            "inode": 524782,
            "path": "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md",
            "sha256": "e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5",
        },
        "producer_source": {
            "bytes": 230782,
            "device": 2064,
            "inode": 431710,
            "path": "tools/run_owned_six_family_original_p0_producer_v4.py",
            "sha256": "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8",
        },
        "reference_cases_per_worker": 6912,
        "reference_contract": {
            "bytes": 13965,
            "device": 2064,
            "inode": 524741,
            "path": "oracle/phase1/p0-public-type-reference-context-v1.json",
            "sha256": "dd0ea680e9a73345f7c323e278ba7ccebd5a3bb26cb606a9bdbecf7c3fb8298b",
        },
        "reference_process_ids": [
            81,
            82,
        ],
        "reference_protocol": {
            "bytes": 10691,
            "device": 2064,
            "inode": 524740,
            "path": "oracle/phase1/P0-PUBLIC-TYPE-REFERENCE-CONTEXT-V1.md",
            "sha256": "11ca046ccd5087b2212b8ad8496896fb1fd60e408a193e038bae4b19fb360018",
        },
        "reference_source": {
            "bytes": 102474,
            "device": 2064,
            "inode": 431631,
            "path": "tools/verify_owned_public_type_reference_context_v1.py",
            "sha256": "bff95e5630e875e1b389eeb4555810a112728dbed5f2cc7c43e1ec83d0817ddc",
        },
    },
    "current_pushed_graph": {
        "authenticated_evidence_owner_lower_bound": 201,
        "authenticated_history_reference_lower_bound": 206,
        "current_rust_candidate_status": "FAIL",
        "current_rust_semantic_mismatch_count": 1440,
        "current_rust_verified_passing_case_count": 14853,
        "current_rust_worker_count": 13,
        "graph_candidate_family_count": 6,
        "graph_python_baseline_count": 1,
        "owners": [
            {
                "bytes": 65821,
                "device": 2064,
                "inode": 432137,
                "path": "tools/render_candidate_current_overview_v59.py",
                "sha256": "a5716931d30ab5f4dcb2bf5efa0bdb3fd24f7bad48f6ed77b5dce3714e547677",
            },
            {
                "bytes": 902467,
                "device": 2064,
                "inode": 432138,
                "path": "docs/evidence/candidate-current-overview-v59.inputs.json",
                "sha256": "044d243432850b6eaa9f0d54b7bd8f77967dd0c234bfb64af9d37e27888e9fa3",
            },
            {
                "bytes": 2457553,
                "device": 2064,
                "inode": 432139,
                "path": "docs/evidence/candidate-current-overview-v59.json",
                "sha256": "73dd4701a9613795aeafa60c1b76a98900a5020dbe31a78fdc1922b534a4c0b0",
            },
            {
                "bytes": 14612,
                "device": 2064,
                "inode": 432141,
                "path": "docs/evidence/candidate-current-overview-v59.svg",
                "sha256": "9b3d0942adcd9bc29d13d895ba5e7a0acc2626520f1392a1c686ce341de43abe",
            },
        ],
        "qualified_candidate_count": 0,
        "version": 59,
    },
    "family": "rust",
    "first_party_rust_source_family": {
        "canonical_source_owner_count": 9,
        "canonical_source_owners": [
            {
                "bytes": 167,
                "device": 2064,
                "inode": 428098,
                "path": "candidates/rust/Cargo.lock",
                "sha256": "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63",
            },
            {
                "bytes": 225,
                "device": 2064,
                "inode": 428094,
                "path": "candidates/rust/Cargo.toml",
                "sha256": "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966",
            },
            {
                "bytes": 175676,
                "device": 2064,
                "inode": 419054,
                "path": "candidates/rust/py_bridge.c",
                "sha256": "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
            },
            {
                "bytes": 177967,
                "device": 2064,
                "inode": 428096,
                "path": "candidates/rust/src/lib.rs",
                "sha256": "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d",
            },
            {
                "bytes": 14416,
                "device": 2064,
                "inode": 427958,
                "path": "candidates/rust/src/newline.rs",
                "sha256": "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b",
            },
            {
                "bytes": 14773,
                "device": 2064,
                "inode": 429682,
                "path": "candidates/rust/src/search.rs",
                "sha256": "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe",
            },
            {
                "bytes": 7269,
                "device": 2064,
                "inode": 428151,
                "path": "candidates/rust/src/stack.rs",
                "sha256": "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e",
            },
            {
                "bytes": 471989,
                "device": 2064,
                "inode": 428152,
                "path": "candidates/rust/src/unicode_tables.rs",
                "sha256": "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af",
            },
            {
                "bytes": 31151,
                "device": 2064,
                "inode": 428100,
                "path": "candidates/rust_candidate.py",
                "sha256": "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
            },
        ],
        "canonical_sources_modified": False,
        "cargo_package_count": 1,
        "cross_candidate_matching_delegation": "FORBIDDEN",
        "external_cargo_dependency_count": 0,
        "external_regular_expression_engines": "FORBIDDEN",
        "family": "rust",
        "matching_fallback": "FORBIDDEN",
        "private_overlay_count_per_phase": 2,
        "stdlib_matching_delegation": "FORBIDDEN",
        "unchanged_private_source_owner_count": 7,
    },
    "first_party_v2_buffer_lifetime_feature": {
        "actually_failed_v1_bridge": {
            "bytes": 181004,
            "device": 2064,
            "inode": 524972,
            "path": "candidates/rust/variants/buffer_shape_pickle_v1/py_bridge.c",
            "sha256": "00271ad5fff71e2f2e30cda6b446a61d0c300cb91eec2091b8ada17662d9a335",
        },
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "derived_bridge_bytes": 179961,
        "derived_bridge_sha256": "afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740",
        "live_original_exporter_acquisitions": 1,
        "live_original_exporter_releases": 8,
        "native_build_status": "NOT RUN",
        "original_subject_match_allocations": 2,
        "outside_function_sha256": "1a4e1713e2ea2dd6a42d56baac4e66907392b1971b94a1f5007fecab5c25830b",
        "owners": [
            {
                "bytes": 47145,
                "device": 2064,
                "inode": 432135,
                "path": "tools/apply_owned_rust_buffer_shape_pickle_source_repair_v2.py",
                "sha256": "7f22016b20da990b0ddb85114bf76a187918612ef68aae97c94d81518d3eb322",
            },
            {
                "bytes": 4060,
                "device": 2064,
                "inode": 525058,
                "path": "oracle/phase2/RUST-BUFFER-SHAPE-PICKLE-SOURCE-REPAIR-V2.md",
                "sha256": "79ad2b88f7542c791cdf48956d432e6d9f2dad00a485056972eea1664e41ff66",
            },
            {
                "bytes": 7486,
                "device": 2064,
                "inode": 525059,
                "path": "oracle/phase2/rust-buffer-shape-pickle-source-repair-v2.json",
                "sha256": "0d5fe2ca190df54366b73850ce316a9d27f77c527bd5ddd8d5420d62dcb33be0",
            },
            {
                "bytes": 179961,
                "device": 2064,
                "inode": 525057,
                "path": "candidates/rust/variants/buffer_shape_pickle_v2/py_bridge.c",
                "sha256": "afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740",
            },
        ],
        "repair_verifier_imported_or_executed": False,
        "static_ast_derivation_only": True,
    },
    "focused_source_evidence_accounting": {
        "current_pushed_evidence_owner_lower_bound": 201,
        "current_pushed_history_reference_lower_bound": 206,
        "future_build_evidence_counted": 0,
        "global_evidence_owner_census": "NOT MEASURED",
        "new_focused_v17_source_owners": 3,
        "resulting_evidence_owner_lower_bound": 204,
        "resulting_history_reference_lower_bound": 209,
    },
    "future_offline_native_build": {
        "actual_process_phase_binding": "AUTHENTICATED ORDERED 14-ROLE SLICE AND SANITIZED WORKING DIRECTORY",
        "authorization": "EXPLICIT FUTURE --build ONLY",
        "canonical_candidate_activation": False,
        "cargo_flags": [
            "--release",
            "--locked",
            "--offline",
            "--frozen",
        ],
        "compiler_process_count_per_phase": 14,
        "distinct_owned_sources_per_phase": 9,
        "expected_actual_compiler_process_count": 28,
        "fresh_corrected_adapter_overlays": 2,
        "fresh_v2_bridge_overlays": 2,
        "independent_phase_count": 2,
        "label": "phase2-v17-rust-buffer-shape-pickle-lifetime",
        "mandatory_low_level_root_prefix": "rebar-phase2-native-build-v9-rust-",
        "missing_real_process_phase_field_allowed": True,
        "native_bridge_bytes": "NOT MEASURED",
        "native_bridge_sha256": "NOT MEASURED",
        "native_engine_bytes": "NOT MEASURED",
        "native_engine_sha256": "NOT MEASURED",
        "phase1_v2_contract_path": "oracle/phase1/p0-completeness-v2.json",
        "phase1_v2_contract_sha256": "NOT MEASURED",
        "phase1_v2_protocol_path": "oracle/phase1/P0-COMPLETENESS-V2.md",
        "phase1_v2_protocol_sha256": "NOT MEASURED",
        "phase1_v2_reconciliation": "REQUIRED BEFORE BUILD; NOT ESTABLISHED",
        "phase1_v2_source_path": "tools/verify_owned_p0_completeness_v2.py",
        "phase1_v2_source_sha256": "NOT MEASURED",
        "phase_local_cargo_home_and_target": True,
        "phase_names": [
            "reference-a",
            "reference-b",
        ],
        "prebuilt_native_artifacts_permitted": False,
        "private_root_mode": "0700",
        "private_source_mode": "0600",
        "process_roles_per_phase": [
            "readelf_version",
            "gcc_version",
            "rustc_version",
            "cargo_version",
            "build_rust_engine",
            "build_rust_bridge",
            "engine_dynamic",
            "engine_symbols",
            "bridge_dynamic",
            "bridge_symbols",
            "engine_sections",
            "engine_notes",
            "bridge_sections",
            "bridge_notes",
        ],
        "publish_build_failure_durably": True,
        "root_parent": "/tmp",
        "two_independent_full_elf_comparisons_required": True,
        "unchanged_sources_per_phase": 7,
    },
    "historical_v16_first_party_build": {
        "actual_compiler_process_count": 28,
        "bridge_source_bytes": 181004,
        "bridge_source_sha256": "00271ad5fff71e2f2e30cda6b446a61d0c300cb91eec2091b8ada17662d9a335",
        "build_status": "PASS",
        "candidate_correctness": "NOT MEASURED",
        "contract": {
            "bytes": 18260,
            "device": 2064,
            "inode": 524985,
            "path": "oracle/phase2/rust-buffer-shape-source-build-v16.json",
            "sha256": "4f82f88da3329c6bacac2092af19d915d379f90101dcd9840366274355cc92b7",
        },
        "durable_receipt": {
            "bytes": 3459,
            "device": 2064,
            "inode": 524994,
            "path": "oracle/phase2/evidence/native-source-build-v16-rust-phase2-v16-rust-buffer-shape-pickle-publication-receipt.json",
            "sha256": "c893812a1796cce056de5e2feff2289df34ff816158685730205996549e338cb",
        },
        "historical_binary_proves_v17": False,
        "protocol": {
            "bytes": 6497,
            "device": 2064,
            "inode": 524984,
            "path": "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V16.md",
            "sha256": "315f0a24e64b50804565f86c6ca4187024c4a1db5a23ab2f57c8805ed37f51f5",
        },
        "public_adapter_bytes": 31934,
        "public_adapter_sha256": "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e",
        "source": {
            "bytes": 134640,
            "device": 2064,
            "inode": 431980,
            "path": "tools/reproduce_owned_rust_buffer_shape_source_build_v16.py",
            "sha256": "bcea8f23fc5e52af1e8062145d75ef1a6ed835cea3ac113a155cc8ebf3116a8a",
        },
    },
    "immutable_goal": {
        "bytes": 3756,
        "device": 2064,
        "inode": 31364044,
        "path": "GOAL.md",
        "sha256": "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    },
    "original_oracle": {
        "additional_callable_reference_case_count": 50,
        "additional_cases_included_in_original_denominator": False,
        "additional_obligation_count": 28,
        "canonical_candidate_context_crosswalk": "NOT ESTABLISHED",
        "case_execution_denominator": 31237,
        "genuine_2gib_candidate_search": "NOT RUN",
        "genuine_2gib_candidate_substitution": "NOT RUN",
        "historical_public_types_vector_status": "FALSIFIED",
        "implementation": "CPython",
        "inherited_obligation_count": 45,
        "matrix": {
            "bytes": 45632,
            "device": 2064,
            "inode": 524385,
            "path": "oracle/phase1/p0-completeness-v1.json",
            "sha256": "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
        },
        "named_private_waiver_count": 13,
        "python": {
            "path": "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
            "sha256": "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
        },
        "suite_count": 13,
        "supplemental_differential_fuzz_candidate_gate": "NOT ESTABLISHED",
        "supplemental_differential_fuzz_case_count": 8244,
        "version": "3.14.6",
    },
    "phase": "CANDIDATES",
    "phase_boundary": {
        "actual_compiler_process_count": 0,
        "archive_inflations": 0,
        "archive_opens": 0,
        "benchmark_files_read": 0,
        "candidate_build": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_imports": 0,
        "candidate_matching": "NOT RUN",
        "candidate_processes_started": 0,
        "candidate_qualified": False,
        "candidate_workers_started": 0,
        "canonical_source_mutations": 0,
        "clock_samples": 0,
        "compiler_processes_started": 0,
        "confidence_intervals": "NOT MEASURED",
        "genuine_2gib_candidate_search": "NOT RUN",
        "genuine_2gib_candidate_substitution": "NOT RUN",
        "hidden_cases_read": 0,
        "holdout": "NOT OPENED",
        "memory": "NOT MEASURED",
        "native_activations": 0,
        "native_libraries_loaded": 0,
        "network_requests": 0,
        "performance": "NOT MEASURED",
        "phase1_canonical_candidate_context_crosswalk": "NOT ESTABLISHED",
        "phase1_v2_reconciliation": "NOT RUN",
        "private_roots_created": 0,
        "qualified_candidate_count": 0,
        "recovery_operations": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "supplemental_differential_fuzz_candidate_gate": "NOT ESTABLISHED",
        "timing_trials_run": 0,
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    },
    "preserved_public_adapter": {
        "bytes": 31934,
        "independently_reconstructed": True,
        "owners": [
            {
                "bytes": 92060,
                "device": 2064,
                "inode": 431033,
                "path": "tools/apply_owned_rust_public_contract_source_repair_v3.py",
                "sha256": "5e57da2379e736bba75eacdb57f84710dc144c0d4088d5827b3139a6b71d8859",
            },
            {
                "bytes": 6405,
                "device": 2064,
                "inode": 524675,
                "path": "oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V3.md",
                "sha256": "2aeb81e55548b46011c75815465d2bc2fa461d57ba7b990fc7a7b87d2d687a34",
            },
            {
                "bytes": 14817,
                "device": 2064,
                "inode": 524678,
                "path": "oracle/phase2/rust-public-contract-source-repair-v3.json",
                "sha256": "82bce0066181dd16f3de52d88f31e930f25706b5ff3da2ba18b10c8b31b4f6a1",
            },
        ],
        "sha256": "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e",
    },
    "protocol": {
        "bytes": 6694,
        "path": "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V17.md",
        "sha256": "c53db893fce626325f806eb99868b900a35cbc220d9bbc5a9663aecdd2cadef3",
    },
    "schema": "rebar-phase2-owned-rust-buffer-shape-source-build-v17-source-freeze",
    "source": {
        "bytes": 107961,
        "path": "tools/reproduce_owned_rust_buffer_shape_source_build_v17.py",
        "sha256": "192062b278aaf5a7a3097d9b5d15218d8d26893a3a8e716fe585f217eeff3471",
    },
    "status": "SOURCE FROZEN; FIRST-PARTY V2 RUST BRIDGE NOT BUILT OR RUN",
    "version": 17,
}

def build_source_expectations() -> dict:
    return copy.deepcopy(BUILD_CONTRACT_EXPECTATIONS)

def validate_build_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict,
              "reject missing three-owner source-only V17 build freeze")
    assert isinstance(proof, dict)
    owners = proof.get("owners")
    base.need(type(owners) is dict and set(owners) == set(BUILD),
              "authenticate exactly three independent build source owners")
    assert isinstance(owners, dict)
    for role, item in BUILD.items():
        owner = owners.get(role)
        base.need(
            type(owner) is dict
            and owner.get("path") == item[0]
            and owner.get("sha256") == item[1]
            and owner.get("bytes") == item[2]
            and owner.get("device") == 2064
            and owner.get("inode") == BUILD_INODES[role]
            and owner.get("uid") == os.geteuid()
            and owner.get("mode") == "0600"
            and owner.get("nlink") == 1,
            "reject forged exact V17 build-source owner: " + role,
        )
    contract = proof.get("complete_source_contract")
    base.need(type(contract) is dict,
              "reject incomplete exact V17 build-source contract")
    assert isinstance(contract, dict)
    expected_contract = build_source_expectations()
    base.need(set(contract) == set(expected_contract),
              "reject erased or invented complete V17 source-contract fields")
    for key, value in expected_contract.items():
        base.need(type(contract.get(key)) is type(value)
                  and contract.get(key) == value,
                  "reject forged frozen V17 source contract: " + key)
    expected = {
        "schema": SCHEMA + "-authenticated-v17-source-build-freeze",
        "family": "rust",
        "feature_status": "SOURCE FROZEN",
        "native_build_status": "NOT RUN",
        "native_build_authorization_status": "BLOCKED",
        "native_build_blocking_reason":
            "PHASE 1 CORRECTED ORIGINAL CROSSWALK NOT ESTABLISHED",
        "phase1_completeness_status": "NOT ESTABLISHED",
        "phase1_corrected_crosswalk_status": "NOT ESTABLISHED",
        "candidate_evaluation_authorized": False,
        "candidate_matching_status": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "actual_compiler_process_count": 0,
        "actual_compiler_process_ids": [],
        "actual_native_libraries_loaded": 0,
        "actual_native_binary_count": 0,
        "actual_native_artifact_hashes": [],
        "candidate_workers_started": 0,
        "candidate_import_count": 0,
        "build_archives_opened_by_graph": 0,
        "build_archives_inflated_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "new_independent_source_owner_count": 3,
        "historical_evidence_owner_lower_bound": 201,
        "historical_history_reference_lower_bound": 206,
        "resulting_evidence_owner_lower_bound": 204,
        "resulting_history_reference_lower_bound": 209,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    base.need(
        set(proof) == set(expected) | {"owners", "complete_source_contract"},
        "reject erased or invented V17 build freeze or actual execution",
    )
    for key, value in expected.items():
        base.need(type(proof.get(key)) is type(value)
                  and proof.get(key) == value,
                  "reject invented V17 native build or binary: " + key)


def make_build_proof(base: types.ModuleType,
                     owners: dict[str, dict], contract: dict) -> dict:
    expected = build_source_expectations()
    base.need(type(contract) is dict and set(contract) == set(expected),
              "reject incomplete exact three-owner build-source contract")
    for key, value in expected.items():
        base.need(type(contract.get(key)) is type(value)
                  and contract.get(key) == value,
                  "reject substituted V17 build source contract: " + key)
    proof = {
        "schema": SCHEMA + "-authenticated-v17-source-build-freeze",
        "family": "rust",
        "feature_status": "SOURCE FROZEN",
        "native_build_status": "NOT RUN",
        "native_build_authorization_status": "BLOCKED",
        "native_build_blocking_reason":
            "PHASE 1 CORRECTED ORIGINAL CROSSWALK NOT ESTABLISHED",
        "phase1_completeness_status": "NOT ESTABLISHED",
        "phase1_corrected_crosswalk_status": "NOT ESTABLISHED",
        "candidate_evaluation_authorized": False,
        "candidate_matching_status": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "actual_compiler_process_count": 0,
        "actual_compiler_process_ids": [],
        "actual_native_libraries_loaded": 0,
        "actual_native_binary_count": 0,
        "actual_native_artifact_hashes": [],
        "candidate_workers_started": 0,
        "candidate_import_count": 0,
        "build_archives_opened_by_graph": 0,
        "build_archives_inflated_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "new_independent_source_owner_count": 3,
        "historical_evidence_owner_lower_bound": 201,
        "historical_history_reference_lower_bound": 206,
        "resulting_evidence_owner_lower_bound": 204,
        "resulting_history_reference_lower_bound": 209,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
        "owners": copy.deepcopy(owners),
        "complete_source_contract": copy.deepcopy(contract),
    }
    validate_build_proof(base, proof)
    return proof


def authenticate_build_source(base: types.ModuleType,
                              options: argparse.Namespace) -> dict:
    owners = {}
    contract = None
    for role, item in BUILD.items():
        supplied = getattr(options, "build_" + role + "_sha256")
        base.need(
            base.checked(supplied, "exact V17 build source owner " + role)
            == item[1],
            "reject substituted V17 build source owner: " + role,
        )
        raw, owner = base.read_owner(*item, private=True)
        owners[role] = owner
        if role == "contract":
            contract = base.document(
                raw, "complete frozen V17 source-build contract",
                exact=False,
            )
    base.need(type(contract) is dict,
              "authenticate one complete V17 source-build contract")
    assert isinstance(contract, dict)
    return make_build_proof(base, owners, contract)


def result_fields(proof: dict) -> dict:
    return {
        "actual_rust_semantic_mismatch_count": 1440,
        "actual_rust_verified_passing_case_count": 14853,
        "rust_actual_semantic_mismatch_count": 1440,
        "rust_original_campaign_semantic_mismatch_count": 1440,
        "rust_original_campaign_verified_passing_case_count": 14853,
        "rust_verified_passing_case_executions": 14853,
        "candidate_facing_self_oracle_status": "NOT ESTABLISHED",
        "phase1_completeness_status": "NOT ESTABLISHED",
        "phase1_corrected_crosswalk_status": "NOT ESTABLISHED",
        "phase1_canonical_candidate_context_crosswalk": "NOT ESTABLISHED",
        "phase1_v2_reconciliation": "NOT RUN",
        "phase1_v1_public_type_reference_status": "FALSIFIED",
        "supplemental_differential_fuzz_candidate_gate": "NOT ESTABLISHED",
        "supplemental_differential_fuzz_case_count": 8244,
        "genuine_2gib_candidate_search": "NOT RUN",
        "genuine_2gib_candidate_substitution": "NOT RUN",
        "candidate_evaluation_authorized": False,
        "rust_v17_source_build_freeze": copy.deepcopy(proof),
        "rust_native_build_v17_source_status": "SOURCE FROZEN",
        "rust_native_build_v17_status": "NOT RUN",
        "rust_native_build_v17_authorization_status": "BLOCKED",
        "rust_native_build_v17_blocking_reason":
            "PHASE 1 CORRECTED ORIGINAL CROSSWALK NOT ESTABLISHED",
        "rust_native_build_v17_matching_status": "NOT RUN",
        "rust_native_build_v17_candidate_correctness": "NOT MEASURED",
        "rust_native_build_v17_candidate_qualified": False,
        "rust_native_build_v17_compiler_process_count": 0,
        "rust_native_build_v17_compiler_process_ids": [],
        "rust_native_build_v17_native_binary_count": 0,
        "rust_native_build_v17_native_artifact_hashes": [],
        "rust_native_build_v17_candidate_workers_started": 0,
        "rust_native_build_v17_independent_source_owner_count": 3,
        "authenticated_evidence_owner_lower_bound": 204,
        "authenticated_history_reference_lower_bound": 209,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
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
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }


def validate_snapshot(modules: tuple, snapshot: object) -> None:
    previous, prior_modules, base = modules
    base.need(type(snapshot) is dict,
              "reject missing exact source-only V60 snapshot")
    assert isinstance(snapshot, dict)
    proof = snapshot.get("rust_v17_source_build_freeze")
    validate_build_proof(base, proof)
    assert isinstance(proof, dict)
    updates = result_fields(proof)
    for key, value in updates.items():
        base.need(type(snapshot.get(key)) is type(value)
                  and snapshot.get(key) == value,
                  "reject invented native V17 build result: " + key)
    replaced = snapshot.get("preserved_v59_replaced_snapshot_fields")
    base.need(type(replaced) is dict and set(replaced).issubset(updates),
              "preserve all exact replaced pushed V59 snapshot fields")
    assert isinstance(replaced, dict)
    history = copy.deepcopy(snapshot)
    history.pop("preserved_v59_replaced_snapshot_fields", None)
    for key in updates:
        if key in replaced:
            history[key] = copy.deepcopy(replaced[key])
        else:
            history.pop(key, None)
    previous.validate_snapshot(prior_modules, history)
    base.need(
        snapshot.get("actual_rust_semantic_mismatch_count") == 1440
        and snapshot.get("actual_rust_verified_passing_case_count") == 14853
        and snapshot.get("rust_original_campaign_semantic_mismatch_count")
            == 1440
        and snapshot.get("rust_original_campaign_verified_passing_case_count")
            == 14853
        and snapshot.get("actual_rust_v7_semantic_mismatch_count") == 928
        and snapshot.get(
            "actual_rust_v7_explicitly_verified_passing_case_count") == 8965
        and snapshot.get("actual_rust_v10_candidate_status") == "FAIL"
        and snapshot.get("actual_rust_v10_semantic_mismatch_count") == 1440
        and snapshot.get("actual_rust_v10_verified_passing_case_count")
            == 14853
        and snapshot.get(
            "actual_rust_v10_semantic_mismatch_regression_against_v7") == 512
        and snapshot.get("actual_rust_v10_candidate_workers") == 13
        and snapshot.get("actual_rust_v10_worker_process_ids") == WORKERS
        and snapshot.get("actual_rust_v10_infrastructure_failure_count") == 0
        and snapshot.get("actual_rust_v10_all_four_original_targets_restored")
            is True
        and len(snapshot.get(
            "actual_rust_v10_complete_independently_authenticated_suite_results",
            [],
        )) == 13
        and len(snapshot.get(
            "actual_rust_v10_earliest_genuine_mismatch_witnesses", [])) == 6
        and snapshot.get("rust_buffer_shape_v2_feature_status")
            == "SOURCE FROZEN"
        and snapshot.get("rust_buffer_shape_v2_build_status") == "NOT BUILT"
        and snapshot.get("rust_buffer_shape_v2_matching_status") == "NOT RUN"
        and snapshot.get("rust_buffer_shape_v2_candidate_workers_started")
            == 0
        and snapshot.get("rust_buffer_shape_v2_independent_source_owner_count")
            == 4
        and snapshot.get("candidate_facing_self_oracle_status")
            == "NOT ESTABLISHED"
        and snapshot.get("phase1_completeness_status") == "NOT ESTABLISHED"
        and snapshot.get("phase1_corrected_crosswalk_status")
            == "NOT ESTABLISHED"
        and snapshot.get("phase1_canonical_candidate_context_crosswalk")
            == "NOT ESTABLISHED"
        and snapshot.get("phase1_v2_reconciliation") == "NOT RUN"
        and snapshot.get("phase1_v1_public_type_reference_status")
            == "FALSIFIED"
        and snapshot.get("supplemental_differential_fuzz_candidate_gate")
            == "NOT ESTABLISHED"
        and snapshot.get("supplemental_differential_fuzz_case_count") == 8244
        and snapshot.get("genuine_2gib_candidate_search") == "NOT RUN"
        and snapshot.get("genuine_2gib_candidate_substitution") == "NOT RUN"
        and snapshot.get("candidate_evaluation_authorized") is False
        and snapshot.get("rust_native_build_v17_source_status")
            == "SOURCE FROZEN"
        and snapshot.get("rust_native_build_v17_status") == "NOT RUN"
        and snapshot.get("rust_native_build_v17_authorization_status")
            == "BLOCKED"
        and snapshot.get("rust_native_build_v17_blocking_reason")
            == "PHASE 1 CORRECTED ORIGINAL CROSSWALK NOT ESTABLISHED"
        and snapshot.get("rust_native_build_v17_matching_status") == "NOT RUN"
        and snapshot.get("rust_native_build_v17_candidate_correctness")
            == "NOT MEASURED"
        and snapshot.get("rust_native_build_v17_compiler_process_count") == 0
        and snapshot.get("rust_native_build_v17_compiler_process_ids") == []
        and snapshot.get("rust_native_build_v17_native_binary_count") == 0
        and snapshot.get("rust_native_build_v17_native_artifact_hashes") == []
        and snapshot.get("rust_native_build_v17_candidate_workers_started")
            == 0
        and snapshot.get("rust_native_build_v17_independent_source_owner_count")
            == 3
        and snapshot.get("full_case_denominator") == 31237
        and snapshot.get("suite_count") == 13
        and snapshot.get("private_waiver_count") == 13
        and snapshot.get("supplementary_signature_check_count") == 50
        and snapshot.get("public_entrypoint_case_matrix_count") == 32
        and snapshot.get("public_entrypoint_case_status_counts")
            == PUBLIC_COUNTS
        and snapshot.get("large_input_source_case_matrix_count") == 32
        and snapshot.get("large_input_source_case_status_counts")
            == LARGE_COUNTS
        and snapshot.get("large_input_upstream_original_case_count") == 2
        and snapshot.get("large_input_upstream_original_subject_bytes")
            == 2147483648
        and snapshot.get("first_party_source_inventory_family_count") == 6
        and snapshot.get("actually_tested_corrected_candidate_families")
            == ["rust"]
        and snapshot.get("actually_tested_corrected_candidate_family_count")
            == 1
        and snapshot.get("currently_activated_candidate_family_count") == 0
        and snapshot.get("actually_runnable_candidate_family_count") == 0
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 204
        and snapshot.get("authenticated_history_reference_lower_bound")
            == 209
        and snapshot.get("actual_candidate_workers_started_by_graph") == 0
        and snapshot.get("actual_compiler_processes_started_by_graph") == 0
        and snapshot.get("actual_native_libraries_loaded_by_graph") == 0
        and snapshot.get(
            "source_build_archive_gzip_inflation_count_by_graph") == 0
        and snapshot.get("actual_clock_samples_by_graph") == 0
        and snapshot.get("final_comparison_planned_case_count") == 4194304
        and snapshot.get("final_comparison_cases_generated") is False
        and snapshot.get("final_holdout_opened") is False
        and snapshot.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and snapshot.get("performance") == "NOT MEASURED"
        and snapshot.get("memory") == "NOT MEASURED"
        and snapshot.get("confidence_intervals") == "NOT MEASURED"
        and snapshot.get("undefined_behavior") == "NOT MEASURED"
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("winner_selected") is False,
        "preserve failed real V10 and forbid an invented V17 source build",
    )


def replace_once(base: types.ModuleType, visible: str,
                 before: str, after: str, description: str) -> str:
    base.need(type(visible) is str and type(before) is str
              and type(after) is str and visible.count(before) == 1,
              "reject substituted pushed V59 chart section: " + description)
    return visible.replace(before, after, 1)


def forged_value(value: object) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        return value + " [FORGED]"
    if type(value) is list:
        return copy.deepcopy(value) + ["FORGED"]
    if type(value) is dict:
        forged = copy.deepcopy(value)
        forged["__forged_v60__"] = True
        return forged
    if value is None:
        return "FORGED"
    return object()


def make_svg(modules: tuple, snapshot: dict, old_svg: bytes,
             source_sha: str, inputs_sha: str) -> bytes:
    previous, prior_modules, base = modules
    validate_snapshot(modules, snapshot)
    source_sha = base.checked(source_sha, "exact current V60 graph renderer")
    inputs_sha = base.checked(inputs_sha, "exact current V60 graph inputs")
    visible = old_svg.decode("utf-8").replace(
        "v59-title", "v60-title").replace(
        "v59-description", "v60-description")
    lines = visible.splitlines()
    base.need(len(lines) > 10
              and lines[1].startswith('<title id="v60-title">')
              and lines[2].startswith('<desc id="v60-description">'),
              "preserve exact pushed V59 accessible graph structure")
    lines[1] = (
        '<title id="v60-title">Building a faster Python re: actual Rust '
        'test failed; the next build is blocked by incomplete '
        'test coverage</title>'
    )
    lines[2] = (
        '<desc id="v60-description">Pinned stable Python 3.14.6 remains '
        'the verified baseline. The latest real from-scratch Rust engine '
        'was tested in 13 real workers on all 31,237 original cases. '
        'It has 1,440 proven compatibility differences and 14,853 '
        'explicitly verified passing cases, 512 more differences than the '
        'previous 928-difference result. Complete independent evidence '
        'preserves all 13 suite observations, six real witnesses, '
        'three failure categories and restoration of the original files. '
        'The original phase-one test-coverage checklist cites an '
        'incorrect older public-type reference; the corrected complete '
        'versioned crosswalk is NOT ESTABLISHED. New candidate '
        'evaluation is not authorized. A proposed first-party '
        'exporter-lifetime repair remains NOT BUILT and NOT RUN. '
        'A three-file reproducible-build recipe for '
        'that repair is SOURCE FROZEN, BLOCKED and NOT RUN; '
        'it has started zero '
        'compilers, produced zero binaries and run zero replacements. '
        'Exactly those three independently owned source files raise '
        'evidence and reference lower bounds from 201 / 206 to 204 / '
        '209. They are not a seventh engine, a passing candidate, an '
        'executed build or measured speed. Six first-party families '
        'and zero compatible replacements remain. Separate totals are '
        '31,237 original cases, 50 signature checks, 32 public-interface '
        'observations and 32 large-input observations. Another '
        '8,244 supplemental fuzz observations are NOT candidate-gated; '
        'the genuine 2-GiB candidate checks have NOT RUN. The '
        '4,194,304-case final holdout has not been generated or opened. '
        'Speed, memory, confidence intervals and undefined behavior are '
        'NOT MEASURED; runtime independence is NOT ESTABLISHED.</desc>'
    )
    visible = "\n".join(lines)
    replacements = (
        (
            '<text x="65" y="398" class="heading">Rust failed; '
            'next exporter repair is not yet run</text>',
            '<text x="65" y="398" class="heading">Rust failed; '
            'the next build is blocked by incomplete coverage</text>',
            "distinguish genuine matching failure from unrun build freeze",
        ),
        (
            'V10 really failed in 13 workers; all targets were restored. '
            'The new exporter repair is NOT BUILT and NOT RUN.',
            'V10 really failed in 13 workers; all files were restored. '
            'The new repair and its build are BLOCKED and NOT RUN.',
            "preserve failed actual run and zero proposed build effects",
        ),
        (
            '<text x="64" y="1756" class="heading">Four-file Rust '
            'exporter repair frozen; not built or tested</text>',
            '<text x="64" y="1756" class="heading">Reproducible Rust '
            'build recipe frozen; build blocked and not run</text>',
            "identify a frozen build recipe, not an executed native build",
        ),
        (
            'Exactly four source-only owners raise actual current '
            'lower bounds from 197 / 202 to 201 / 206.',
            'Exactly three build-source owners raise actual current '
            'lower bounds from 201 / 206 to 204 / 209.',
            "count precisely three independent source-build owners",
        ),
        (
            'Real V10 cohorts are independently authenticated. The new '
            'source has no build, workers, correctness or speed result.',
            'Real V10 failures remain proven. The source-only build '
            'is BLOCKED by incomplete phase-one coverage; no compiler, '
            'binary, matching or speed result exists.',
            "forbid invented build binaries, matching and performance",
        ),
    )
    for before, after, why in replacements:
        visible = replace_once(base, visible, before, after, why)
    lines = visible.splitlines()
    start = next(
        (index for index, line in enumerate(lines)
         if line.startswith('<rect x="44" y="1858" width="1352"')),
        None,
    )
    base.need(type(start) is int, "retain exact pushed V59 evidence chart")
    assert isinstance(start, int)
    lines = lines[:start]
    lines.extend((
        '<rect x="44" y="1858" width="1352" height="381" rx="16" '
        'fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="1888" class="heading">Exact failed-test '
        'evidence and unrun build-recipe sources</text>',
    ))
    v58 = previous
    v57 = prior_modules[0]
    footers = (
        ("Graph inputs SHA-256", inputs_sha),
        ("Graph renderer SHA-256", source_sha),
        ("Historical V59 graph inputs SHA-256", V59["inputs"][1]),
        ("Historical V59 graph renderer SHA-256", V59["source"][1]),
        ("Historical V59 graph summary SHA-256", V59["summary"][1]),
        ("Historical V59 graph image SHA-256", V59["svg"][1]),
        ("Small actual V10 durable receipt SHA-256", v57.RECEIPT[1]),
        ("Complete independent V10 forensic summary SHA-256",
         v57.FORENSIC[1]),
        ("V10 compressed report SHA-256 (not opened by this graph)",
         v57.ARCHIVE_SHA),
        ("Unrun V17 native-build source SHA-256", BUILD["source"][1]),
        ("Unrun V17 native-build protocol SHA-256", BUILD["protocol"][1]),
        ("Unrun V17 native-build contract SHA-256", BUILD["contract"][1]),
    )
    for index, (label, value) in enumerate(footers):
        lines.append(
            f'<text x="65" y="{1914 + index * 18}" class="foot">'
            f'{label}: {value}</text>'
        )
    lines.extend((
        '<text x="65" y="2139" class="small">Latest actual Rust: '
        '1,440 differences; 14,853 verified passes; 13 real workers; '
        '512 more differences than historical V7.</text>',
        '<text x="65" y="2158" class="small">Previous V7: '
        '928 differences and 8,965 verified passes. Current failed '
        'cohorts: 16, 368 and 1,056.</text>',
        '<text x="65" y="2177" class="small">Exporter repair: '
        'NOT BUILT, NOT RUN. Build recipe: SOURCE FROZEN, '
        'BLOCKED; BUILD NOT RUN.</text>',
        '<text x="65" y="2196" class="small">Build operations: '
        '0 compilers, 0 binaries, 0 candidate workers. Speed: '
        'NOT MEASURED.</text>',
        '<text x="65" y="2215" class="small">Six first-party families. '
        'Test checklist incomplete; candidate evaluation BLOCKED. '
        'Final holdout NOT OPENED.</text>',
        '<!-- This graph does not open, stat, hash or inflate any '
        'compressed archive, execute a compiler, load a candidate or '
        'native binary, read clocks or open the hidden holdout. -->',
        "</svg>",
    ))
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    for label, value in footers:
        base.need(
            raw.count((label + ": " + value).encode("ascii")) == 1,
            "bind exactly one actual or historic V60 footer: " + label,
        )
    lower = raw.lower()
    for phrase in (
            b'height="2250"', b"building a faster python re",
            b"1,440 differences", b"14,853",
            b"13 real workers", b"512 more", b"historical",
            b"928", b"8,965", b"managed 16",
            b"substitution 368", b"shape 1,056",
            b"31,237", b"4.2m unopened", b"not opened",
            b"not built", b"not run", b"source frozen",
            b"build not run", b"blocked", b"test coverage",
            b"not established", b"0 compilers", b"0 binaries",
            b"0 candidate workers", b"not measured",
            b"not established", b"201 / 206", b"204 / 209",
            b"signature checks", b"public-interface observations",
            b"large-input observations", b"17 pass", b"7 fail",
            b"22 pass", b"3 not run", b"2,147,483,648",
            b"1,087", b"1,036", b"1,262", b"1,230",
            b"2,172", b"1,764", b"not generated",
            b"not opened by this graph"):
        base.need(phrase in lower,
                  "retain honest V60 native-build freeze: " + repr(phrase))
    for falsehood in (
            b"v17 build passed", b"v17 build failed",
            b"v17 compiler started", b"v17 native binary produced",
            b"v17 candidate passed", b"v17 candidate failed",
            b"counts as a new engine family",
            b"rust candidate qualified", b"winner selected",
            b"holdout opened", b"faster than python",
            b"candidate correctness: pass"):
        base.need(falsehood not in lower,
                  "reject fabricated V17 execution: " + repr(falsehood))
    base.need(raw.endswith(b"\n") and not raw.endswith(b"\n\n"),
              "finish complete V60 chart with exactly one linefeed")
    return raw


def build(modules: tuple,
          options: argparse.Namespace) -> tuple[dict, tuple]:
    previous, prior_modules, base = modules
    source_sha = base.checked(options.source_sha256,
                              "exact current independent V60 source")
    base.need(type(options.source_bytes) is int
              and 0 < options.source_bytes <= base.OWNER_LIMIT,
              "bound actual current V60 source owner")
    own_raw, _ = base.read_owner(SELF, source_sha, options.source_bytes,
                                private=True)
    old, old_inputs, old_svg = authenticate_v59(
        modules,
        {role: getattr(options, "previous_" + role + "_sha256")
         for role in V59},
    )
    proof = authenticate_build_source(base, options)
    updates = result_fields(proof)
    original = old["snapshot"]
    snapshot = copy.deepcopy(original)
    snapshot.update(updates)
    snapshot["preserved_v59_replaced_snapshot_fields"] = {
        key: copy.deepcopy(original[key])
        for key in updates if key in original
    }
    validate_snapshot(modules, snapshot)
    predecessor = {role: base.pin(*item) for role, item in V59.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 60,
        "python": "3.14.6",
        "renderer": base.pin(SELF, source_sha, len(own_raw)),
        "previous_overview": predecessor,
        **updates,
    })
    input_raw = base.canonical(inputs)
    svg = make_svg(modules, snapshot, old_svg, source_sha,
                   base.digest(input_raw))
    families = copy.deepcopy(old["families"])
    base.need(
        [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "preserve baseline and exactly six first-party candidate families",
    )
    for row in families:
        if row.get("family") == "python":
            continue
        row.update({
            "authenticated_evidence_owner_lower_bound": 204,
            "authenticated_history_reference_lower_bound": 209,
            "actually_tested_corrected_candidate_family_count": 1,
            "actually_tested_corrected_candidate_families": ["rust"],
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified": False,
            "performance": "NOT MEASURED",
        })
        if row.get("family") == "rust":
            row.update({
                "current_original_campaign_semantic_mismatch_count": 1440,
                "current_original_campaign_verified_passing_case_count":
                    14853,
                "current_original_campaign_candidate_worker_count": 13,
                "actual_candidate_workers": 13,
                "actual_v10_candidate_correctness": "FAIL",
                "actual_v10_candidate_status": "FAIL",
                "actual_v10_matching_status": "FAIL",
                "actual_v10_semantic_mismatch_count": 1440,
                "actual_v10_verified_passing_case_count": 14853,
                "actual_v10_semantic_mismatch_regression_against_v7": 512,
                "actual_v10_candidate_workers": 13,
                "native_build_v17_source_freeze": copy.deepcopy(proof),
                "native_build_v17_source_status": "SOURCE FROZEN",
                "native_build_v17_status": "NOT RUN",
                "native_build_v17_candidate_matching_status": "NOT RUN",
                "native_build_v17_candidate_correctness": "NOT MEASURED",
                "native_build_v17_compiler_process_count": 0,
                "native_build_v17_native_binary_count": 0,
                "native_build_v17_candidate_workers_started": 0,
                "native_build_v17_independent_source_owner_count": 3,
            })
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 60,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, source_sha, len(own_raw)),
        "inputs": base.pin(OUTPUT + ".inputs.json",
                           base.digest(input_raw), len(input_raw)),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg), len(svg)),
        "previous_overview": predecessor,
        "snapshot": snapshot,
        "families": families,
        **updates,
    })
    summary_raw = base.canonical(summary)
    base.need(max(len(input_raw), len(summary_raw), len(svg))
              <= base.OWNER_LIMIT,
              "bound only three complete authorized V60 graph outputs")
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )


def reject_control(base: types.ModuleType, proof: dict,
                   description: str) -> int:
    try:
        validate_build_proof(base, proof)
    except (base.GraphError, TypeError, ValueError, KeyError,
            AttributeError, RecursionError):
        return 1
    raise base.GraphError("accepted forged V17 build freeze: " + description)


def self_test(modules: tuple) -> dict:
    previous, prior_modules, base = modules
    prior = previous.self_test(prior_modules)
    base.need(
        prior.get("status") == "PASS"
        and prior.get("rejected_hostile_control_count") == 4743
        and prior.get("actual_rust_semantic_mismatch_count") == 1440
        and prior.get("actual_rust_verified_passing_case_count") == 14853
        and prior.get("rust_original_campaign_semantic_mismatch_count")
            == 1440
        and prior.get("rust_original_campaign_verified_passing_case_count")
            == 14853
        and prior.get("actual_rust_v7_semantic_mismatch_count") == 928
        and prior.get(
            "actual_rust_v7_explicitly_verified_passing_case_count") == 8965
        and prior.get("actual_rust_v10_candidate_status") == "FAIL"
        and prior.get("actual_rust_v10_semantic_mismatch_count") == 1440
        and prior.get("actual_rust_v10_verified_passing_case_count") == 14853
        and prior.get("actual_rust_v10_semantic_mismatch_regression_against_v7")
            == 512
        and prior.get("actual_rust_v10_candidate_workers") == 13
        and prior.get("rust_buffer_shape_v2_build_status") == "NOT BUILT"
        and prior.get("rust_buffer_shape_v2_matching_status") == "NOT RUN"
        and prior.get("rust_buffer_shape_v2_candidate_workers_started") == 0
        and prior.get("authenticated_evidence_owner_lower_bound") == 201
        and prior.get("authenticated_history_reference_lower_bound") == 206
        and prior.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and prior.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and prior.get("actual_feature_source_owners_read_by_self_test") == 0
        and prior.get("actual_failure_archives_opened_by_self_test") == 0,
        "preserve all 4,743 real V59 hostile controls and zero V2 runs",
    )
    rejected = 0
    with base.SourceOnlyWall() as wall:
        owners = {
            role: base.synthetic_owner(item, BUILD_INODES[role])
            for role, item in BUILD.items()
        }
        contract = build_source_expectations()
        proof = make_build_proof(base, owners, contract)
        for key, value in proof.items():
            hostile = copy.deepcopy(proof)
            hostile[key] = forged_value(value)
            rejected += reject_control(base, hostile, "proof:" + key)
        for role, owner in proof["owners"].items():
            for key, value in owner.items():
                hostile = copy.deepcopy(proof)
                hostile["owners"][role][key] = forged_value(value)
                rejected += reject_control(
                    base, hostile, "owner:" + role + ":" + key)
        for key, value in proof["complete_source_contract"].items():
            hostile = copy.deepcopy(proof)
            hostile["complete_source_contract"][key] = forged_value(value)
            rejected += reject_control(base, hostile, "contract:" + key)
        checks = (
            ("filesystem", lambda: builtins.open("forbidden-v60")),
            ("filesystem", lambda: os.open("forbidden-v60", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v60")),
            ("write", lambda: os.mkdir("forbidden-v60")),
            ("process", lambda: subprocess.run(("forbidden-v60",))),
            ("process", lambda: subprocess.Popen(("forbidden-v60",))),
            ("process", lambda: os.execv("/forbidden-v60", [])),
        )
        for kind, action in checks:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(wall.blocked[kind] == before + 1,
                          "physically forbid V60 source-only " + kind)
            else:
                raise base.GraphError("forbidden V60 source-only effect")
        base.need(rejected >= 50,
                  "reject all forged V17 owner, contract and build effects")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 60,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v59_hostile_controls": 4743,
            "new_v60_hostile_controls": rejected,
            "rejected_hostile_control_count": 4743 + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "actual_feature_source_owners_read_by_self_test": 0,
            "actual_build_source_owners_read_by_self_test": 0,
            "actual_forensic_summary_owners_read_by_self_test": 0,
            "actual_failure_archives_opened_by_self_test": 0,
            "actual_failure_archives_inflated_by_self_test": 0,
            "actual_build_archives_opened_by_self_test": 0,
            "actual_build_archives_inflated_by_self_test": 0,
            "actual_candidate_imports_by_graph": 0,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "actual_native_libraries_loaded_by_graph": 0,
            "actual_large_subject_allocations_by_graph": 0,
            "actual_clock_samples_by_graph": 0,
            "actual_hidden_cases_read_by_graph": 0,
            "source_build_archive_gzip_inflation_count_by_graph": 0,
            "actual_current_graph_predecessor_version": 59,
            "actual_rust_semantic_mismatch_count": 1440,
            "actual_rust_verified_passing_case_count": 14853,
            "rust_original_campaign_semantic_mismatch_count": 1440,
            "rust_original_campaign_verified_passing_case_count": 14853,
            "actual_rust_v7_semantic_mismatch_count": 928,
            "actual_rust_v7_explicitly_verified_passing_case_count": 8965,
            "actual_rust_v7_candidate_workers": 13,
            "actual_rust_v8_matching_status": "NOT RUN",
            "actual_rust_v8_candidate_workers": 0,
            "actual_rust_v9_matching_status": "NOT RUN",
            "actual_rust_v9_candidate_workers": 0,
            "actual_rust_v10_candidate_status": "FAIL",
            "actual_rust_v10_semantic_mismatch_count": 1440,
            "actual_rust_v10_verified_passing_case_count": 14853,
            "actual_rust_v10_semantic_mismatch_regression_against_v7": 512,
            "actual_rust_v10_candidate_workers": 13,
            "actual_rust_v10_infrastructure_failure_count": 0,
            "actual_rust_v10_all_four_original_targets_restored": True,
            "rust_buffer_shape_v2_feature_status": "SOURCE FROZEN",
            "rust_buffer_shape_v2_build_status": "NOT BUILT",
            "rust_buffer_shape_v2_matching_status": "NOT RUN",
            "rust_buffer_shape_v2_candidate_workers_started": 0,
            "candidate_facing_self_oracle_status": "NOT ESTABLISHED",
            "phase1_completeness_status": "NOT ESTABLISHED",
            "phase1_corrected_crosswalk_status": "NOT ESTABLISHED",
            "phase1_canonical_candidate_context_crosswalk": "NOT ESTABLISHED",
            "phase1_v2_reconciliation": "NOT RUN",
            "phase1_v1_public_type_reference_status": "FALSIFIED",
            "supplemental_differential_fuzz_candidate_gate": "NOT ESTABLISHED",
            "supplemental_differential_fuzz_case_count": 8244,
            "genuine_2gib_candidate_search": "NOT RUN",
            "genuine_2gib_candidate_substitution": "NOT RUN",
            "candidate_evaluation_authorized": False,
            "rust_native_build_v17_source_status": "SOURCE FROZEN",
            "rust_native_build_v17_status": "NOT RUN",
            "rust_native_build_v17_authorization_status": "BLOCKED",
            "rust_native_build_v17_blocking_reason":
                "PHASE 1 CORRECTED ORIGINAL CROSSWALK NOT ESTABLISHED",
            "rust_native_build_v17_matching_status": "NOT RUN",
            "rust_native_build_v17_candidate_correctness": "NOT MEASURED",
            "rust_native_build_v17_compiler_process_count": 0,
            "rust_native_build_v17_compiler_process_ids": [],
            "rust_native_build_v17_native_binary_count": 0,
            "rust_native_build_v17_native_artifact_hashes": [],
            "rust_native_build_v17_candidate_workers_started": 0,
            "rust_native_build_v17_independent_source_owner_count": 3,
            "authenticated_evidence_owner_lower_bound": 204,
            "authenticated_history_reference_lower_bound": 209,
            "full_case_denominator": 31237,
            "suite_count": 13,
            "private_waiver_count": 13,
            "supplementary_signature_check_count": 50,
            "public_entrypoint_case_matrix_count": 32,
            "public_entrypoint_case_status_counts":
                copy.deepcopy(PUBLIC_COUNTS),
            "large_input_source_case_matrix_count": 32,
            "large_input_source_case_status_counts":
                copy.deepcopy(LARGE_COUNTS),
            "large_input_upstream_original_case_count": 2,
            "large_input_upstream_original_subject_bytes": 2147483648,
            "first_party_source_inventory_family_count": 6,
            "actually_tested_corrected_candidate_families": ["rust"],
            "actually_tested_corrected_candidate_family_count": 1,
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified_candidate_count": 0,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(path in {OUTPUT + ".inputs.json", OUTPUT + ".json",
                       OUTPUT + ".svg"}
              and type(raw) is bytes
              and 0 < len(raw) <= base.OWNER_LIMIT,
              "publish only three root-authorized complete V60 graph files")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0,
                      "publish every exact independently owned V60 byte")
            remaining = remaining[count:]
        os.fsync(handle)
        meta = os.fstat(handle)
        base.need(meta.st_uid == os.geteuid()
                  and meta.st_nlink == 1
                  and meta.st_size == len(raw)
                  and stat.S_IMODE(meta.st_mode) == 0o600,
                  "publish exactly one private complete V60 graph owner")
    finally:
        os.close(handle)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory = os.open(str(ROOT / Path(path).parent), flags)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    confirmed, _ = base.read_owner(path, base.digest(raw), len(raw),
                                  private=True)
    base.need(confirmed == raw,
              "reauthenticate exactly one complete current V60 graph owner")


def compact_result(base: types.ModuleType, snapshot: dict,
                   outputs: dict[str, bytes], source_sha: str,
                   *, written: bool, suffix: str) -> dict:
    fields = (
        "actual_rust_semantic_mismatch_count",
        "actual_rust_verified_passing_case_count",
        "rust_original_campaign_semantic_mismatch_count",
        "rust_original_campaign_verified_passing_case_count",
        "actual_rust_v7_semantic_mismatch_count",
        "actual_rust_v7_explicitly_verified_passing_case_count",
        "actual_rust_v7_candidate_workers",
        "actual_rust_v8_matching_status",
        "actual_rust_v8_candidate_workers",
        "actual_rust_v9_matching_status",
        "actual_rust_v9_candidate_workers",
        "actual_rust_v10_candidate_status",
        "actual_rust_v10_semantic_mismatch_count",
        "actual_rust_v10_verified_passing_case_count",
        "actual_rust_v10_semantic_mismatch_regression_against_v7",
        "actual_rust_v10_candidate_workers",
        "actual_rust_v10_worker_process_ids",
        "actual_rust_v10_infrastructure_failure_count",
        "actual_rust_v10_all_four_original_targets_restored",
        "actual_rust_v10_complete_independently_authenticated_suite_results",
        "actual_rust_v10_earliest_genuine_mismatch_witnesses",
        "rust_buffer_shape_v2_feature_status",
        "rust_buffer_shape_v2_build_status",
        "rust_buffer_shape_v2_matching_status",
        "rust_buffer_shape_v2_candidate_correctness",
        "rust_buffer_shape_v2_candidate_workers_started",
        "rust_buffer_shape_v2_independent_source_owner_count",
        "candidate_facing_self_oracle_status",
        "phase1_completeness_status",
        "phase1_corrected_crosswalk_status",
        "phase1_canonical_candidate_context_crosswalk",
        "phase1_v2_reconciliation",
        "phase1_v1_public_type_reference_status",
        "supplemental_differential_fuzz_candidate_gate",
        "supplemental_differential_fuzz_case_count",
        "genuine_2gib_candidate_search",
        "genuine_2gib_candidate_substitution",
        "candidate_evaluation_authorized",
        "rust_native_build_v17_source_status",
        "rust_native_build_v17_status",
        "rust_native_build_v17_authorization_status",
        "rust_native_build_v17_blocking_reason",
        "rust_native_build_v17_matching_status",
        "rust_native_build_v17_candidate_correctness",
        "rust_native_build_v17_candidate_qualified",
        "rust_native_build_v17_compiler_process_count",
        "rust_native_build_v17_compiler_process_ids",
        "rust_native_build_v17_native_binary_count",
        "rust_native_build_v17_native_artifact_hashes",
        "rust_native_build_v17_candidate_workers_started",
        "rust_native_build_v17_independent_source_owner_count",
        "authenticated_evidence_owner_lower_bound",
        "authenticated_history_reference_lower_bound",
        "public_entrypoint_case_status_counts",
        "large_input_source_case_status_counts",
        "first_party_source_inventory_family_count",
        "actually_tested_corrected_candidate_families",
        "currently_activated_candidate_family_count",
        "actually_runnable_candidate_family_count",
        "qualified_candidate_count",
        "final_comparison_planned_case_count",
        "final_comparison_cases_generated",
        "final_holdout_opened",
        "runtime_no_delegation",
        "performance",
        "memory",
        "confidence_intervals",
        "undefined_behavior",
        "winner_selected",
    )
    return {
        "schema": SCHEMA + suffix,
        "version": 60,
        "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 59,
        **{"previous_overview_" + role + "_sha256": item[1]
           for role, item in V59.items()},
        **{"build_" + role + "_sha256": item[1]
           for role, item in BUILD.items()},
        **{key: copy.deepcopy(snapshot[key]) for key in fields},
        "outputs_written": written,
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    for role in V59:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in BUILD:
        parser.add_argument("--build-" + role.replace("_", "-")
                            + "-sha256")
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        modules = load_v59()
        base = modules[-1]
        if options.self_test:
            forbidden = ["source_sha256", "source_bytes"]
            forbidden.extend("previous_" + role + "_sha256" for role in V59)
            forbidden.extend("build_" + role + "_sha256" for role in BUILD)
            forbidden.extend(("inputs_sha256", "summary_sha256",
                              "svg_sha256"))
            base.need(all(getattr(options, name) is None
                          for name in forbidden),
                      "source-only V60 self-test receives no actual pins")
            sys.stdout.buffer.write(base.canonical(self_test(modules)))
            return 0
        snapshot, pairs = build(modules, options)
        outputs = dict(pairs)
        source_sha = base.checked(options.source_sha256,
                                  "complete exact V60 graph renderer")
        if options.render:
            base.need(options.inputs_sha256 is None
                      and options.summary_sha256 is None
                      and options.svg_sha256 is None,
                      "render only the three authorized V60 graph assets")
            for path, raw in pairs:
                publish(base, path, raw)
            result = compact_result(
                base, snapshot, outputs, source_sha,
                written=True, suffix="-published")
        else:
            expected = {
                OUTPUT + ".inputs.json": base.checked(
                    options.inputs_sha256, "exact actual V60 graph inputs"),
                OUTPUT + ".json": base.checked(
                    options.summary_sha256, "exact actual V60 graph summary"),
                OUTPUT + ".svg": base.checked(
                    options.svg_sha256, "exact actual V60 graph image"),
            }
            for path, fingerprint in expected.items():
                raw, _ = base.read_owner(
                    path, fingerprint, len(outputs[path]), private=True)
                base.need(raw == outputs[path],
                          "reproduce complete actual V60 output: " + path)
            result = compact_result(
                base, snapshot, outputs, source_sha,
                written=False, suffix="-read-only-frozen-context")
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except (ValueError, OSError, TypeError, EOFError, KeyError,
            AttributeError, RecursionError, UnicodeError) as error:
        sys.stderr.write("current V60 overview rejected: "
                         + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V60 overview rejected: "
                             + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
