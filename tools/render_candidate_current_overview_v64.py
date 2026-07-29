#!/usr/bin/env python3
"""Reconcile the corrected Python reference without inventing a passing suite."""

from __future__ import annotations

import argparse
import builtins
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import types

ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v64.py"
OUTPUT = "docs/evidence/candidate-current-overview-v64"
SCHEMA = "rebar-candidate-current-overview-v64"
V63 = {
    "source": (
        "tools/render_candidate_current_overview_v63.py",
        "4f33bd240aa70ca8a47de1c56ec8eb405da4f23f587cfab362f4a7ebbed648c4",
        67015,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v63.inputs.json",
        "fafba28ae2628e1f1b9747a865747a0ad35ba943b746c95893b0fd3381b91581",
        967168,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v63.json",
        "e78207ec0e2af2470287d3afbc12bee0270d29fa7ed7483a1f62eb72a0b4016c",
        2660089,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v63.svg",
        "9860367eb080240efd36e5c241fe0f7d6305d351d87152e2007b92beff496d7e",
        14765,
    ),
}
READINESS = {
    "source": (
        "tools/verify_owned_p0_completeness_v4.py",
        "8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d",
        29094,
    ),
    "protocol": (
        "oracle/phase1/P0-COMPLETENESS-V4.md",
        "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
        4261,
    ),
    "contract": (
        "oracle/phase1/p0-completeness-v4.json",
        "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
        34875,
    ),
}
READINESS_INODES = {
    "source": 428927,
    "protocol": 524712,
    "contract": 524713,
}
STALE_V17_AUTHORIZATION_OUTPUTS = {
    "inputs": (
        "docs/evidence/candidate-current-overview-v64.inputs.json",
        "8e312afd9802a4a663e64337b9567f37ea75fb1430bd19f5c10f09d0a37e8355",
        1004658,
        428929,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v64.json",
        "c5f793445e2dd8c964d2518cc4051111a583c32408925771785f78fe33d12183",
        2775627,
        428930,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v64.svg",
        "b87138258b4009523f9aae5cb25a4e2286c43cd6905aba92f0f39d7f142f9cf6",
        14725,
        428931,
    ),
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
READINESS_EXPECTATIONS = {
    "actual_supplemental_two_reference": {
        "actual_reference_worker_count": 2,
        "actual_reference_worker_process_ids": [
            81,
            82,
        ],
        "aggregate": {
            "bytes": 3658,
            "device": 2064,
            "inode": 524707,
            "mode": "0600",
            "path": "oracle/phase1/evidence/differential-fuzz-reference-v3-cpython-3146-two-worker-8244-v3/two-independent-reference-result.json",
            "sha256": "8377e9c526a487c2e8838d7b8ba74e595b42d069f572bf7ed29f926f82d5b096",
        },
        "case_count_per_worker": [
            8244,
            8244,
        ],
        "case_denominator_included_in_original_31237": False,
        "controller_protocol": {
            "bytes": 3929,
            "device": 2064,
            "inode": 525081,
            "mode": "0600",
            "path": "oracle/phase1/P0-DIFFERENTIAL-FUZZ-REFERENCE-V3.md",
            "sha256": "8d67e3f4162945a454d8945abac3880a9c42620a04c2332ac2adc52f013305b6",
        },
        "controller_source": {
            "bytes": 43757,
            "device": 2064,
            "inode": 432216,
            "mode": "0600",
            "path": "tools/run_owned_differential_fuzz_reference_v3.py",
            "sha256": "9367bf224996296a9c8a0e01040d0776b292984e1a8b7a6362c8e943c27438ac",
        },
        "failed_per_worker": [
            0,
            0,
        ],
        "frozen_seeds": {
            "deep_bytes": 1979121302,
            "deep_str": 1979121301,
            "invalid_patterns": 1511506921,
            "invalid_templates": 1511506922,
            "properties": 1511506920,
            "valid_bytes": 1511506919,
            "valid_str": 1511506918,
        },
        "historical_source_contract": {
            "bytes": 5288,
            "device": 2064,
            "inode": 525082,
            "mode": "0600",
            "path": "oracle/phase1/p0-differential-fuzz-reference-v3.json",
            "sha256": "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff",
        },
        "record_kind_counts": {
            "byteslike": 11,
            "byteslike-escape": 2,
            "cache": 1,
            "call": 7359,
            "compile": 2,
            "debug": 1,
            "error": 456,
            "escape": 2,
            "exports": 1,
            "flags": 1,
            "generic": 4,
            "match-copy": 3,
            "pattern-equality": 1,
            "positional-warning": 3,
            "property": 384,
            "representation": 5,
            "roundtrip": 1,
            "scanner": 2,
            "warning": 5,
        },
        "record_mapped_obligation_ids": [
            "API-BYTESLIKE",
            "API-COMPILE",
            "API-ESCAPE",
            "API-EXPORTS",
            "API-FINDALL",
            "API-FINDITER",
            "API-FLAGS",
            "API-FULLMATCH",
            "API-GENERIC",
            "API-MATCH",
            "API-MATCH-COPY",
            "API-MATCH-OBJECT",
            "API-PATTERN",
            "API-REPRESENTATION",
            "API-SCANNER",
            "API-SEARCH",
            "API-SPLIT",
            "API-SUB",
            "API-SUBN",
            "E-DEBUG",
            "E-DEPRECATION",
            "E-PATTERN",
            "E-TEMPLATE",
            "E-TYPE",
            "E-WARNING",
            "S-ALTERNATION",
            "S-ANCHOR",
            "S-ASCII",
            "S-ATOMIC",
            "S-BACKREF",
            "S-CONDITIONAL",
            "S-DEEP-FUZZ",
            "S-DOT-CLASS",
            "S-EMPTY",
            "S-GROUP",
            "S-INLINE",
            "S-LITERAL",
            "S-LOCALE",
            "S-LOOKAROUND",
            "S-LOOKBEHIND-REF",
            "S-POSSESSIVE",
            "S-QUANTIFIER",
            "S-UNICODE",
            "S-VERBOSE",
            "S-WINDOW",
        ],
        "reference_one": {
            "bytes": 270,
            "device": 2064,
            "inode": 524693,
            "mode": "0600",
            "path": "oracle/phase1/evidence/differential-fuzz-reference-v3-cpython-3146-two-worker-8244-v3/reference-1.json",
            "sha256": "98e91a0b0ca63ec6718e32d682219df65d12bf0d947fe54934caf4b42412b8ce",
        },
        "reference_two": {
            "bytes": 270,
            "device": 2064,
            "inode": 524692,
            "mode": "0600",
            "path": "oracle/phase1/evidence/differential-fuzz-reference-v3-cpython-3146-two-worker-8244-v3/reference-2.json",
            "sha256": "98e91a0b0ca63ec6718e32d682219df65d12bf0d947fe54934caf4b42412b8ce",
        },
        "status": "PASS",
        "supplemental_corpus": {
            "bytes": 7602476,
            "case_count": 8244,
            "device": 2064,
            "inode": 428243,
            "maximum_observed_record_bytes": 83668,
            "mode": "0600",
            "path": "oracle/v2/expected.jsonl",
            "per_record_limit_bytes": 262144,
            "plaintext_corpus_loaded_whole": False,
            "record_kind_counts": {
                "byteslike": 11,
                "byteslike-escape": 2,
                "cache": 1,
                "call": 7359,
                "compile": 2,
                "debug": 1,
                "error": 456,
                "escape": 2,
                "exports": 1,
                "flags": 1,
                "generic": 4,
                "match-copy": 3,
                "pattern-equality": 1,
                "positional-warning": 3,
                "property": 384,
                "representation": 5,
                "roundtrip": 1,
                "scanner": 2,
                "warning": 5,
            },
            "record_mapped_obligation_ids": [
                "API-BYTESLIKE",
                "API-COMPILE",
                "API-ESCAPE",
                "API-EXPORTS",
                "API-FINDALL",
                "API-FINDITER",
                "API-FLAGS",
                "API-FULLMATCH",
                "API-GENERIC",
                "API-MATCH",
                "API-MATCH-COPY",
                "API-MATCH-OBJECT",
                "API-PATTERN",
                "API-REPRESENTATION",
                "API-SCANNER",
                "API-SEARCH",
                "API-SPLIT",
                "API-SUB",
                "API-SUBN",
                "E-DEBUG",
                "E-DEPRECATION",
                "E-PATTERN",
                "E-TEMPLATE",
                "E-TYPE",
                "E-WARNING",
                "S-ALTERNATION",
                "S-ANCHOR",
                "S-ASCII",
                "S-ATOMIC",
                "S-BACKREF",
                "S-CONDITIONAL",
                "S-DEEP-FUZZ",
                "S-DOT-CLASS",
                "S-EMPTY",
                "S-GROUP",
                "S-INLINE",
                "S-LITERAL",
                "S-LOCALE",
                "S-LOOKAROUND",
                "S-LOOKBEHIND-REF",
                "S-POSSESSIVE",
                "S-QUANTIFIER",
                "S-UNICODE",
                "S-VERBOSE",
                "S-WINDOW",
            ],
            "sha256": "ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2",
            "unique_record_case_count": 8244,
        },
        "total_actual_reference_case_executions": 16488,
        "v1_parent_corpus": {
            "bytes": 1203505,
            "case_count": 2048,
            "device": 2064,
            "inode": 427910,
            "maximum_observed_record_bytes": 40442,
            "mode": "0600",
            "path": "oracle/v1/expected.jsonl",
            "per_record_limit_bytes": 262144,
            "plaintext_corpus_loaded_whole": False,
            "sha256": "983885ee6411fd806edf3d72efbcc989f9b9f7775a6d127dc7c865673eeb0fed",
        },
        "worker_exit_codes": [
            0,
            0,
        ],
        "worker_result_provenance": [
            {
                "case_count": 8244,
                "exit_code": 0,
                "failed": 0,
                "failures": [],
                "module": "re",
                "passed": 8244,
                "pid": 81,
                "result": {
                    "bytes": 270,
                    "device": 2064,
                    "inode": 524693,
                    "mode": "0600",
                    "path": "/home/dev-user/src/rebar/oracle/phase1/evidence/differential-fuzz-reference-v3-cpython-3146-two-worker-8244-v3/reference-1.json",
                    "sha256": "98e91a0b0ca63ec6718e32d682219df65d12bf0d947fe54934caf4b42412b8ce",
                },
                "result_schema": "rebar-correctness-result-v2",
                "role": "independent-reference-a",
                "stderr": {
                    "bytes": 0,
                    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                    "text": "",
                },
                "stdout": {
                    "bytes": 234,
                    "sha256": "c8e57eba27a87f84adf0667fc5111e20894f21d4b39353dc5c490ffb41b691c7",
                    "text": "{\"cases\": 8244, \"expected_sha256\": \"ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2\", \"failed\": 0, \"mapped_obligations\": 45, \"module\": \"re\", \"obligations\": 45, \"passed\": 8244, \"schema\": \"rebar-correctness-result-v2\"}\n",
                },
            },
            {
                "case_count": 8244,
                "exit_code": 0,
                "failed": 0,
                "failures": [],
                "module": "re",
                "passed": 8244,
                "pid": 82,
                "result": {
                    "bytes": 270,
                    "device": 2064,
                    "inode": 524692,
                    "mode": "0600",
                    "path": "/home/dev-user/src/rebar/oracle/phase1/evidence/differential-fuzz-reference-v3-cpython-3146-two-worker-8244-v3/reference-2.json",
                    "sha256": "98e91a0b0ca63ec6718e32d682219df65d12bf0d947fe54934caf4b42412b8ce",
                },
                "result_schema": "rebar-correctness-result-v2",
                "role": "independent-reference-b",
                "stderr": {
                    "bytes": 0,
                    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                    "text": "",
                },
                "stdout": {
                    "bytes": 234,
                    "sha256": "c8e57eba27a87f84adf0667fc5111e20894f21d4b39353dc5c490ffb41b691c7",
                    "text": "{\"cases\": 8244, \"expected_sha256\": \"ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2\", \"failed\": 0, \"mapped_obligations\": 45, \"module\": \"re\", \"obligations\": 45, \"passed\": 8244, \"schema\": \"rebar-correctness-result-v2\"}\n",
                },
            },
        ],
    },
    "authenticated_inherited_source_owner_count": 61,
    "candidate_qualification_gate": {
        "blockers": [
            "ORIGINAL_31237_CANDIDATE_GATE_NOT_PASSED",
            "SUPPLEMENTAL_8244_CANDIDATE_GATE_NOT_RUN",
            "PUBLIC_IMPORT_FAIL",
            "PUBLIC_CALLABLE_SIGNATURE_CANDIDATE_GATE_NOT_RUN",
            "FULL_SIZE_2GIB_CANDIDATE_SEARCH_NOT_RUN",
            "FULL_SIZE_2GIB_CANDIDATE_SUBSTITUTION_NOT_RUN",
            "RUNTIME_NO_DELEGATION_NOT_ESTABLISHED",
        ],
        "candidate_family_count": 6,
        "candidate_fuzz_status": "NOT RUN",
        "final_holdout_opened": False,
        "memory": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "status": "BLOCKED",
        "status_scope": "PHASE 2 CANDIDATE QUALIFICATION ONLY",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    },
    "corrected_candidate_context_public_type_reference": {
        "actual_reference_receipt": {
            "bytes": 2509,
            "device": 2064,
            "inode": 524769,
            "mode": "0600",
            "path": "oracle/phase1/evidence/public-type-reference-context-v1-cpython-3-14-6-candidate-context-p0-publication-receipt.json",
            "sha256": "ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966",
        },
        "actual_reference_worker_count": 2,
        "attempted_reference_worker_count": 2,
        "cache_case_count": 96,
        "cache_case_ids_sha256": "df43bd52adb112c0fde2bfe24a45200ca2ac30a9c41dfdc5716e3e81cbe19ce0",
        "cache_records_sha256": "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad",
        "candidate_facing_reference": True,
        "case_count": 6912,
        "completed_reference_worker_count": 2,
        "contract": {
            "bytes": 13965,
            "device": 2064,
            "inode": 524741,
            "mode": "0600",
            "path": "oracle/phase1/p0-public-type-reference-context-v1.json",
            "sha256": "dd0ea680e9a73345f7c323e278ba7ccebd5a3bb26cb606a9bdbecf7c3fb8298b",
        },
        "controller_v10_contract": {
            "bytes": 21238,
            "device": 2064,
            "inode": 524828,
            "mode": "0600",
            "path": "oracle/phase2/p0-candidate-protocol-v10.json",
            "sha256": "8eb72f1d94af85db1f1b282dda4d6ce1839f51f492ed2c7436c666d792f9b737",
        },
        "controller_v10_protocol": {
            "bytes": 6792,
            "device": 2064,
            "inode": 524827,
            "mode": "0600",
            "path": "oracle/phase2/P0-CANDIDATE-PROTOCOL-V10.md",
            "sha256": "2d773fc55fe7c0a61e044a0e7deef81c8e36ffa0a9a744f4e60901f7a953c2ae",
        },
        "controller_v10_source": {
            "bytes": 91132,
            "device": 2064,
            "inode": 431751,
            "mode": "0600",
            "path": "tools/run_frozen_p0_candidate_v10.py",
            "sha256": "c114b578ac7ebfe28b45aa3b3407b81d05333f4470fa3047fd338ed3541c185a",
        },
        "falsification": {
            "bytes": 3892,
            "device": 2064,
            "inode": 524739,
            "mode": "0600",
            "path": "oracle/phase1/evidence/public-type-candidate-context-falsification-v1.json",
            "sha256": "319f0f75aaaea16fd1f41d814785d67060c57060852893349366cc3b482c4670",
        },
        "historical_reference_records_sha256": "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21",
        "matching_archive_opened_by_v2": False,
        "matrix_sha256": "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123",
        "new_candidate_workers_started_by_v2": 0,
        "new_reference_workers_started_by_v2": 0,
        "producer_v4_contract": {
            "bytes": 30867,
            "device": 2064,
            "inode": 524783,
            "mode": "0600",
            "path": "oracle/phase2/six-family-p0-producer-v4.json",
            "sha256": "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5",
        },
        "producer_v4_protocol": {
            "bytes": 5981,
            "device": 2064,
            "inode": 524782,
            "mode": "0600",
            "path": "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md",
            "sha256": "e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5",
        },
        "producer_v4_source": {
            "bytes": 230782,
            "device": 2064,
            "inode": 431710,
            "mode": "0600",
            "path": "tools/run_owned_six_family_original_p0_producer_v4.py",
            "sha256": "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8",
        },
        "protocol": {
            "bytes": 10691,
            "device": 2064,
            "inode": 524740,
            "mode": "0600",
            "path": "oracle/phase1/P0-PUBLIC-TYPE-REFERENCE-CONTEXT-V1.md",
            "sha256": "11ca046ccd5087b2212b8ad8496896fb1fd60e408a193e038bae4b19fb360018",
        },
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "records_sha256": "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2",
        "reference_pids": [
            81,
            82,
        ],
        "reference_status": "PASS",
        "source": {
            "bytes": 102474,
            "device": 2064,
            "inode": 431631,
            "mode": "0600",
            "path": "tools/verify_owned_public_type_reference_context_v1.py",
            "sha256": "bff95e5630e875e1b389eeb4555810a112728dbed5f2cc7c43e1ec83d0817ddc",
        },
        "status": "PASS",
        "validated_reference_worker_count": 2,
    },
    "first_party_candidate_family_count": 6,
    "historical_phase_transition": {
        "historical_single_context_worker_provenance": "NOT CAPTURED",
        "original_case_execution_denominator_unchanged": True,
        "previous_phase_gate_status": "BLOCKED",
        "previous_version": 2,
        "resolution": "TWO AUTHENTICATED COMPLETE REFERENCE WORKERS PASSED",
        "resolved_reference_blocker": "SUPPLEMENTAL_8244_TWO_INDEPENDENT_REFERENCE_PROCESSES_NOT_RUN",
    },
    "historical_supplemental_differential_property_fuzz": {
        "candidate_case_count": 0,
        "candidate_qualified": False,
        "candidate_status": "NOT RUN",
        "case_count": 8244,
        "case_denominator_included_in_original_31237": False,
        "combined_count_is_new_original_denominator": False,
        "combined_separately_counted_case_count": 39481,
        "complete_streamed_newline_count": 8244,
        "expected_records": {
            "bytes": 7602476,
            "device": 2064,
            "inode": 428243,
            "mode": "0600",
            "path": "oracle/v2/expected.jsonl",
            "sha256": "ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2",
        },
        "expected_records_bytes": 7602476,
        "expected_records_sha256": "ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2",
        "first_case_id": "api.exports",
        "frozen_seed_values": {
            "deep_bytes": 1979121302,
            "deep_str": 1979121301,
            "invalid_patterns": 1511506921,
            "invalid_templates": 1511506922,
            "properties": 1511506920,
            "valid_bytes": 1511506919,
            "valid_str": 1511506918,
        },
        "historical_abstract_private_waivers": [
            "PRIVATE-CACHE-LAYOUT",
            "PRIVATE-DEBUG-TEXT",
        ],
        "historical_abstract_waivers_inherited_into_original": 0,
        "historical_independent_reference_process_ids": "NOT CAPTURED",
        "historical_single_context_stdlib_evidence": {
            "bytes": 270,
            "device": 2064,
            "inode": 428249,
            "mode": "0600",
            "path": "oracle/v2/evidence/correctness-self.json",
            "sha256": "98e91a0b0ca63ec6718e32d682219df65d12bf0d947fe54934caf4b42412b8ce",
        },
        "historical_single_context_stdlib_passing_case_count": 8244,
        "historical_single_context_stdlib_status": "PASS",
        "independently_referenced_case_count": 0,
        "last_case_id": "v2.deep.bytes.2047",
        "manifest": {
            "bytes": 1359,
            "device": 2064,
            "inode": 428246,
            "mode": "0600",
            "path": "oracle/v2/manifest.json",
            "sha256": "91ce7da8cd0ebcdf2861fbb82cd531855631e52815aa8c1684f6a798da6563f6",
        },
        "maximum_observed_record_bytes": 83668,
        "maximum_observed_record_payload_bytes": 83667,
        "per_record_limit_bytes": 262144,
        "plaintext_corpus_loaded_whole": False,
        "protocol": {
            "bytes": 2531,
            "device": 2064,
            "inode": 428247,
            "mode": "0600",
            "path": "oracle/v2/P0.md",
            "sha256": "50fe34edd81ae22f3a2b8fb836a615fe625dc2b7c32ce0f045275554bf3b9e44",
        },
        "record_kind_counts": {
            "byteslike": 11,
            "byteslike-escape": 2,
            "cache": 1,
            "call": 7359,
            "compile": 2,
            "debug": 1,
            "error": 456,
            "escape": 2,
            "exports": 1,
            "flags": 1,
            "generic": 4,
            "match-copy": 3,
            "pattern-equality": 1,
            "positional-warning": 3,
            "property": 384,
            "representation": 5,
            "roundtrip": 1,
            "scanner": 2,
            "warning": 5,
        },
        "record_mapped_obligation_ids": [
            "API-EXPORTS",
            "API-FLAGS",
            "API-COMPILE",
            "API-SEARCH",
            "API-MATCH",
            "API-FULLMATCH",
            "API-FINDALL",
            "API-FINDITER",
            "API-SPLIT",
            "API-SUB",
            "API-SUBN",
            "API-ESCAPE",
            "API-PATTERN",
            "API-MATCH-OBJECT",
            "API-SCANNER",
            "S-LITERAL",
            "S-DOT-CLASS",
            "S-ANCHOR",
            "S-QUANTIFIER",
            "S-POSSESSIVE",
            "S-ALTERNATION",
            "S-GROUP",
            "S-BACKREF",
            "S-CONDITIONAL",
            "S-LOOKAROUND",
            "S-ATOMIC",
            "S-INLINE",
            "S-VERBOSE",
            "S-UNICODE",
            "S-ASCII",
            "S-LOCALE",
            "S-EMPTY",
            "S-WINDOW",
            "E-PATTERN",
            "E-TYPE",
            "E-TEMPLATE",
            "E-WARNING",
            "E-DEBUG",
            "API-GENERIC",
            "API-BYTESLIKE",
            "API-REPRESENTATION",
            "API-MATCH-COPY",
            "E-DEPRECATION",
            "S-LOOKBEHIND-REF",
            "S-DEEP-FUZZ",
        ],
        "runner": {
            "bytes": 14248,
            "device": 2064,
            "inode": 428240,
            "mode": "0600",
            "path": "tools/oracle_v2.py",
            "sha256": "f038145dc0527f802203e18556f03b4bba636bb219105dc38c675c52a23e0fbb",
        },
        "seeds": {
            "bytes": 210,
            "device": 2064,
            "inode": 428245,
            "mode": "0600",
            "path": "oracle/v2/seeds.json",
            "sha256": "761d074856c36880db60965583207c78a46b8fced204e0f3b4e03e744fed74c7",
        },
        "source": {
            "bytes": 12393,
            "device": 2064,
            "inode": 428239,
            "mode": "0600",
            "path": "oracle/v2/suite.py",
            "sha256": "a05912d8f3ef01e3f8ccd5e421647afd55a72963fefbfd431140ac5977b333a1",
        },
        "status": "BLOCKED",
        "transitive_v1_parent": {
            "complete_streamed_newline_count": 2048,
            "expected_records": {
                "bytes": 1203505,
                "device": 2064,
                "inode": 427910,
                "mode": "0600",
                "path": "oracle/v1/expected.jsonl",
                "sha256": "983885ee6411fd806edf3d72efbcc989f9b9f7775a6d127dc7c865673eeb0fed",
            },
            "historical_abstract_waivers_inherited_into_original": 0,
            "historical_reference_worker_provenance": "NOT ESTABLISHED",
            "historical_single_context_stdlib_evidence": {
                "bytes": 270,
                "device": 2064,
                "inode": 427913,
                "mode": "0600",
                "path": "oracle/v1/evidence/correctness-self.json",
                "sha256": "517e948197ead373e74139aa86692efff861da4700bb7f4524a3e1b6b239bf54",
            },
            "historical_single_context_stdlib_status": "PASS",
            "manifest": {
                "bytes": 1039,
                "device": 2064,
                "inode": 427911,
                "mode": "0600",
                "path": "oracle/v1/manifest.json",
                "sha256": "4c3e5ebd70ceb2352dfd6f0708ad8172d53b53dc3c9e42f2eeafb9e4736200ba",
            },
            "protocol": {
                "bytes": 4619,
                "device": 2064,
                "inode": 427902,
                "mode": "0600",
                "path": "oracle/v1/P0.md",
                "sha256": "30dc3dd121c8e2d7a080884923109164b4bbdf37103f56c2bac84727acbd4424",
            },
            "runner": {
                "bytes": 19573,
                "device": 2064,
                "inode": 427905,
                "mode": "0600",
                "path": "tools/oracle.py",
                "sha256": "fda0ca974afaea3e37106fce59169eaead387cf8f63e7b6f93bdee5992eab541",
            },
            "seeds": {
                "bytes": 156,
                "device": 2064,
                "inode": 427943,
                "mode": "0600",
                "path": "oracle/v1/seeds.json",
                "sha256": "75d159b2bfb9e3343c9bb3787b398db3de8a44f39b973ea74cd921257469feea",
            },
            "source": {
                "bytes": 19888,
                "device": 2064,
                "inode": 427903,
                "mode": "0600",
                "path": "oracle/v1/suite.py",
                "sha256": "097d51609c1f8d677a7ddb98bcb1a5c245764fff6246ee6239d642a264fb5fc9",
            },
        },
        "two_independent_reference_process_status": "NOT RUN",
        "unique_record_case_count": 8244,
    },
    "holdout": "NOT OPENED",
    "memory": "NOT MEASURED",
    "original_case_execution_denominator": 31237,
    "original_crosswalk_count": 34,
    "original_named_private_waiver_count": 13,
    "original_obligation_count": 73,
    "original_oracle": {
        "additional_named_obligation_count": 28,
        "additional_obligation_ids": [
            "API-UPSTREAM-ALL-165",
            "API-UPSTREAM-403-CORPUS",
            "API-UPSTREAM-11-EXTERNAL-ASSERTIONS",
            "API-MODULE-SCANNER",
            "API-SCANNER-CALLBACK-ORDER",
            "API-SCANNER-LEXICON-IDENTITY",
            "API-VERBOSE-ESCAPED-COMMENTS",
            "API-PUBLIC-TYPE-IDENTITY",
            "API-GENERIC-ALIASES",
            "API-WEAKREF-COPY-ATOMICITY",
            "API-PICKLE-PROTOCOLS-0-5",
            "API-PUBLIC-CACHE-PURGE",
            "API-PEP688-DIRECT-EXPORTER",
            "API-PEP688-NESTED-EXPORTER",
            "API-BUFFER-ACQUIRE-RELEASE-ORDER",
            "API-SCANNER-GC-RETAINED-CYCLE",
            "API-SHAPE-CHANGING-EXPORTER",
            "API-CALLBACK-EXCEPTION-IDENTITY",
            "API-LOCALE-CROSS-TRANSITION",
            "API-SUBINTERPRETER-ISOLATION",
            "API-SUBINTERPRETER-TEARDOWN",
            "S-UNICODE-ESCAPED-LONE-SURROGATES",
            "E-EXACT-PATTERN-ATTRIBUTES",
            "E-WARNING-CATEGORY-MESSAGE-LOCATION",
            "E-64BIT-INDEX-OVERFLOW",
            "E-FIXTURE-VERSUS-USER-EXCEPTION",
            "API-THREAD-SHARED-PATTERN-REENTRANCY",
            "API-MODULE-VERSION-METADATA",
        ],
        "all_13_named_waiver_ids_sha256": "9f8932d7c832b8c6ecf30f7408ac3228ea46980d4d196e2b0854a372236d79b9",
        "all_13_named_waiver_objects_sha256": "ca3f6deb77518c7112790001ab1deb4a74f0282fc1d7326f79a09dc6ca60f61e",
        "all_34_crosswalk_ids_sha256": "0a293c79d4bd541ddad84e8c0745e51b61eec3b8ca1745f9d6f6c90156938551",
        "all_34_crosswalk_objects_sha256": "349c524e070ad701608aaeed30b14717dd262dbe9956e535a4234a25ba13366f",
        "all_73_obligation_ids_sha256": "0eee54994b1d740b2b7660329f5aca2b06ae415ae064f9263fd962daea9eae99",
        "all_73_obligation_objects_sha256": "599105639814150f3076563f597114db9a2d746ed9ad4ae8554b604dea44b728",
        "case_execution_denominator": 31237,
        "crosswalk_count": 34,
        "full_resource_reference_history_double_counted": False,
        "historical_inventory": {
            "bytes": 45632,
            "device": 2064,
            "inode": 524385,
            "mode": "0600",
            "path": "oracle/phase1/p0-completeness-v1.json",
            "sha256": "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
        },
        "historical_protocol": {
            "bytes": 10392,
            "device": 2064,
            "inode": 524381,
            "mode": "0600",
            "path": "oracle/phase1/P0-COMPLETENESS-V1.md",
            "sha256": "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798",
        },
        "historical_verifier": {
            "bytes": 118040,
            "device": 2064,
            "inode": 432204,
            "mode": "0600",
            "path": "tools/verify_p0_completeness_v1.py",
            "sha256": "0bb256c3d1140688f0f466d90cae020345aafcb5d3e8130b38b09e9de3930a0c",
        },
        "inherited_obligation_count": 45,
        "inherited_obligation_ids": [
            "API-EXPORTS",
            "API-FLAGS",
            "API-COMPILE",
            "API-SEARCH",
            "API-MATCH",
            "API-FULLMATCH",
            "API-FINDALL",
            "API-FINDITER",
            "API-SPLIT",
            "API-SUB",
            "API-SUBN",
            "API-ESCAPE",
            "API-PATTERN",
            "API-MATCH-OBJECT",
            "API-SCANNER",
            "S-LITERAL",
            "S-DOT-CLASS",
            "S-ANCHOR",
            "S-QUANTIFIER",
            "S-POSSESSIVE",
            "S-ALTERNATION",
            "S-GROUP",
            "S-BACKREF",
            "S-CONDITIONAL",
            "S-LOOKAROUND",
            "S-ATOMIC",
            "S-INLINE",
            "S-VERBOSE",
            "S-UNICODE",
            "S-ASCII",
            "S-LOCALE",
            "S-EMPTY",
            "S-WINDOW",
            "E-PATTERN",
            "E-TYPE",
            "E-TEMPLATE",
            "E-WARNING",
            "E-DEBUG",
            "API-GENERIC",
            "API-BYTESLIKE",
            "API-REPRESENTATION",
            "API-MATCH-COPY",
            "E-DEPRECATION",
            "S-LOOKBEHIND-REF",
            "S-DEEP-FUZZ",
        ],
        "legacy_abstract_fuzz_waivers_inherited": 0,
        "named_private_waiver_count": 13,
        "named_private_waivers": [
            "DebugTests.test_debug_flag",
            "DebugTests.test_atomic_group",
            "DebugTests.test_possesive_repeat_one",
            "DebugTests.test_possesive_repeat",
            "ImplementationTest.test_immutable",
            "ImplementationTest.test_overlap_table",
            "ImplementationTest.test_signedness",
            "ImplementationTest.test_disallow_instantiation",
            "ImplementationTest.test_deprecated_modules",
            "ImplementationTest.test_case_helpers",
            "ImplementationTest.test_dealloc",
            "ImplementationTest.test_repeat_minmax_overflow_maxrepeat",
            "ImplementationTest.test_sre_template_invalid_group_index",
        ],
        "public_method_count": 152,
        "public_release_debug_skip": "ReTests.test_memory_leaks",
        "public_release_debug_skip_is_private_waiver": False,
        "runnable_public_method_count": 151,
        "source_method_count": 165,
        "source_ordered_suite_ids_sha256": "0bc6bb35f7584fd41331f180ac7764e3edcee8bd7920a33690099376b1bd1a07",
        "status": "CORRECTED ORIGINAL CROSSWALK PASS; UNIVERSAL GATE BLOCKED",
        "suite_count": 13,
        "suites": [
            {
                "candidate_context_reference_records_sha256": "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276",
                "case_execution_count": 151,
                "historical_reference_records_sha256": "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276",
                "id": "original_bounded_v5",
                "matrix_sha256": "93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240",
                "published_seed_decimal": None,
                "source": {
                    "bytes": 123750,
                    "device": 2064,
                    "inode": 431594,
                    "mode": "0600",
                    "path": "tools/independent_original_cpython_suite_v5.py",
                    "sha256": "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce",
                },
            },
            {
                "candidate_context_reference_records_sha256": "0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c",
                "case_execution_count": 864,
                "historical_reference_records_sha256": "0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c",
                "id": "public_v3",
                "matrix_sha256": "367d30517874745b11d6facf43685a906784dc94c0246dc6a6381c17afcc776e",
                "published_seed_decimal": "5928217332825411633",
                "source": {
                    "bytes": 80268,
                    "device": 2064,
                    "inode": 430397,
                    "mode": "0600",
                    "path": "tools/rust_public_practice_benchmark_v1.py",
                    "sha256": "d74932c13bdda64e1340c958cbea48d65db36531b849e202dfc16170de150b37",
                },
            },
            {
                "candidate_context_reference_records_sha256": "37de08e1991adf28990e35b72c2130ebafa78c72b04750d28550cce08555666d",
                "case_execution_count": 1024,
                "historical_reference_records_sha256": "37de08e1991adf28990e35b72c2130ebafa78c72b04750d28550cce08555666d",
                "id": "scanner_v3",
                "matrix_sha256": "83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c",
                "published_seed_decimal": "5999710933164053041",
                "source": {
                    "bytes": 39826,
                    "device": 2064,
                    "inode": 430580,
                    "mode": "0600",
                    "path": "tools/rust_scanner_differential_v1.py",
                    "sha256": "fcc82a76e7bcaaa25d92a8482d4dc611b643d887d7fd983db0906c7340b91fd7",
                },
            },
            {
                "candidate_context_reference_records_sha256": "8312263785cd49f7283ab8c6fac13443befe9c5a3d739b2e068aebdcf3f59b75",
                "case_execution_count": 768,
                "historical_reference_records_sha256": "8312263785cd49f7283ab8c6fac13443befe9c5a3d739b2e068aebdcf3f59b75",
                "id": "buffer_v3",
                "matrix_sha256": "b40fb92f42c7019a73eec72800077f262f1a6be516886a6ddda372e24807eb60",
                "published_seed_decimal": "5567953616029762609",
                "source": {
                    "bytes": 47223,
                    "device": 2064,
                    "inode": 431004,
                    "mode": "0600",
                    "path": "tools/rust_memoryview_expand_differential_v1.py",
                    "sha256": "226f129f0e90b060c977e599e6e8369f5a5285890089c69108b718cfcb2980e6",
                },
            },
            {
                "candidate_context_reference_records_sha256": "80293f5332300220f38c3f017d38611a5514b1b686918e692a53491945b196df",
                "case_execution_count": 1024,
                "historical_reference_records_sha256": "80293f5332300220f38c3f017d38611a5514b1b686918e692a53491945b196df",
                "id": "managed_v1",
                "matrix_sha256": "28ef84b6989542ba8865c98e5296639c780c786078e2a99c7c0a95bfcb4b0976",
                "published_seed_decimal": "5567095966978627121",
                "source": {
                    "bytes": 123890,
                    "device": 2064,
                    "inode": 430528,
                    "mode": "0600",
                    "path": "tools/independent_managed_buffer_lifetime_v1.py",
                    "sha256": "cedbab1227ea58a97d407cb339d2959a9f9be58a2085ce3106b65bb3385de489",
                },
            },
            {
                "candidate_context_reference_records_sha256": "d7e2d499eb4dbe6ae0f8743d8b152e4835898656daa8b3167598636ef7be6012",
                "case_execution_count": 2854,
                "historical_reference_records_sha256": "d7e2d499eb4dbe6ae0f8743d8b152e4835898656daa8b3167598636ef7be6012",
                "id": "scanner_verbose_v1",
                "matrix_sha256": "01bca287cd481a5e4ae134b910911e2e2f8f1501eebb7ffd2947092ab170d17b",
                "published_seed_decimal": "5999725261024810545",
                "source": {
                    "bytes": 88737,
                    "device": 2064,
                    "inode": 431462,
                    "mode": "0600",
                    "path": "tools/independent_scanner_verbose_comments_v1.py",
                    "sha256": "5508910eae3f5e59d2013bc9fa4f1a8948a823e27de09bf416de2fffc8e91c9d",
                },
            },
            {
                "candidate_context_reference_records_sha256": "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2",
                "case_execution_count": 6912,
                "historical_reference_records_sha256": "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21",
                "id": "public_types_v1",
                "matrix_sha256": "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123",
                "published_seed_decimal": "6077977430793212465",
                "source": {
                    "bytes": 150015,
                    "device": 2064,
                    "inode": 432032,
                    "mode": "0600",
                    "path": "tools/independent_public_type_identity_serialization_v1.py",
                    "sha256": "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20",
                },
            },
            {
                "candidate_context_reference_records_sha256": "2bc65461b9ac60fd19a3c66856bd33ee48db038ab6a5de62193837800840f61b",
                "case_execution_count": 5120,
                "historical_reference_records_sha256": "2bc65461b9ac60fd19a3c66856bd33ee48db038ab6a5de62193837800840f61b",
                "id": "substitution_v2",
                "matrix_sha256": "26f46fe7f1abc5135d1265a7882ccd4a2e2b45cdec80ba293520fda510235b54",
                "published_seed_decimal": "6004778603531028017",
                "source": {
                    "bytes": 317541,
                    "device": 2064,
                    "inode": 432058,
                    "mode": "0600",
                    "path": "tools/independent_substitution_buffer_semantics_v2.py",
                    "sha256": "e7cc951b4fbb90b2826c3730bbb3b3e81b50e8a5eac8a3d758962358d9414573",
                },
            },
            {
                "candidate_context_reference_records_sha256": "58bbc78828ba2d4cde6b99cbebea815ce9381cda24d0acec03f6cc095b8b643c",
                "case_execution_count": 10240,
                "historical_reference_records_sha256": "58bbc78828ba2d4cde6b99cbebea815ce9381cda24d0acec03f6cc095b8b643c",
                "id": "shape_v2",
                "matrix_sha256": "10fe3e3fd4b4650bff1da6a745b5b883f01033ed14df3f9795aa2f7a30c6d8d8",
                "published_seed_decimal": "6001118316486346290",
                "source": {
                    "bytes": 137527,
                    "device": 2064,
                    "inode": 432070,
                    "mode": "0600",
                    "path": "tools/independent_shape_changing_buffer_semantics_v2.py",
                    "sha256": "0262807f793a818307f2c8c6ecfd84bf970264a6ef5d656acf30c9d3606f0e2c",
                },
            },
            {
                "candidate_context_reference_records_sha256": "c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef",
                "case_execution_count": 1376,
                "historical_reference_records_sha256": "c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef",
                "id": "public_surface_v19",
                "matrix_sha256": "7885a9ac0b2e22db88db7dc4ab9c33c4ba229ddb6d15fcdd4bfe9b0d6f10e8aa",
                "published_seed_decimal": "2026072483",
                "source": {
                    "bytes": 199366,
                    "device": 2064,
                    "inode": 430521,
                    "mode": "0600",
                    "path": "tools/python_re_public_surface_oracle_stage19.py",
                    "sha256": "fda386f3c00be660a41e92d8005fc287706d9dc050967cf2b708cb6f8aba113e",
                },
            },
            {
                "candidate_context_reference_records_sha256": "450fccc859099ca78aec725911b6195695cd932ad281af931ca7945cec8c51e8",
                "case_execution_count": 128,
                "historical_reference_records_sha256": "450fccc859099ca78aec725911b6195695cd932ad281af931ca7945cec8c51e8",
                "id": "subinterpreter_v2",
                "matrix_sha256": "edda77658c5eef9746c6d4769734c69e40db4c9d986171fa63799093f4cb62d3",
                "published_seed_decimal": "2026072501",
                "source": {
                    "bytes": 151395,
                    "device": 2064,
                    "inode": 432166,
                    "mode": "0600",
                    "path": "tools/python_re_subinterpreter_oracle_v2.py",
                    "sha256": "54735efb77a099feb2dd076723d3a93d81415226b9b9213307c32cc0f38c52c8",
                },
            },
            {
                "candidate_context_reference_records_sha256": "7827586e0c7d4f43ac1fbd288f6b28f6a44b810b46274830d3803505c76692a8",
                "case_execution_count": 264,
                "historical_reference_records_sha256": "7827586e0c7d4f43ac1fbd288f6b28f6a44b810b46274830d3803505c76692a8",
                "id": "pep688_v4",
                "matrix_sha256": "2d9eb4e637387bc89020d2f883f59ff03dd98cbebd2f2aaa2a30dc55d0836891",
                "published_seed_decimal": None,
                "source": {
                    "bytes": 162181,
                    "device": 2064,
                    "inode": 432192,
                    "mode": "0600",
                    "path": "tools/python_re_buffer_exporter_oracle_v4.py",
                    "sha256": "8da0b8e5c5519e7335cd1b53ceb7042f1da1f902c486ad8ac35ddf53d8a04490",
                },
            },
            {
                "candidate_context_reference_records_sha256": "928ea100d6fdaecc7c1dcf01e32c24fd98a146964c0955989a8149c1216ffe81",
                "case_execution_count": 512,
                "historical_reference_records_sha256": "928ea100d6fdaecc7c1dcf01e32c24fd98a146964c0955989a8149c1216ffe81",
                "id": "threaded_pattern_v1",
                "matrix_sha256": "a7d467e3e529204946fe00ddb819e734421e7087ea909af9ec24b757e42afa0b",
                "published_seed_decimal": "2026072701",
                "source": {
                    "bytes": 146417,
                    "device": 2064,
                    "inode": 432206,
                    "mode": "0600",
                    "path": "tools/python_re_threaded_pattern_oracle_v1.py",
                    "sha256": "05226e59736d8721a975eda8afa10247213999690c2766a7b3235c567b9f8276",
                },
            },
        ],
        "supplemental_cases_silently_added": False,
        "total_named_obligation_count": 73,
        "upstream_corpus_case_count": 403,
        "upstream_external_fixture_count": 11,
    },
    "original_suite_count": 13,
    "performance": "NOT MEASURED",
    "phase": "CORRECTNESS ORACLE",
    "phase1_canonical_candidate_context_crosswalk": "PASS",
    "phase_gate": {
        "candidate_evaluation_authorized": True,
        "final_holdout_authorized": False,
        "native_build_authorized": True,
        "performance_oracle_authorized": False,
        "qualified_candidate_count": 0,
        "source_crosswalk_status": "PASS",
        "status": "PASS",
        "status_scope": "PHASE 1 PYTHON-ORACLE READINESS ONLY",
        "winner_selected": False,
    },
    "pinned_cpython": {
        "bytes": 32387816,
        "device": 2049,
        "inode": 9594007,
        "mode": "0711",
        "path": "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
        "sha256": "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
    },
    "previous_overview": {
        "inputs": {
            "bytes": 967168,
            "device": 2064,
            "inode": 428906,
            "mode": "0600",
            "path": "docs/evidence/candidate-current-overview-v63.inputs.json",
            "sha256": "fafba28ae2628e1f1b9747a865747a0ad35ba943b746c95893b0fd3381b91581",
        },
        "source": {
            "bytes": 67015,
            "device": 2064,
            "inode": 428905,
            "mode": "0600",
            "path": "tools/render_candidate_current_overview_v63.py",
            "sha256": "4f33bd240aa70ca8a47de1c56ec8eb405da4f23f587cfab362f4a7ebbed648c4",
        },
        "summary": {
            "bytes": 2660089,
            "device": 2064,
            "inode": 428907,
            "mode": "0600",
            "path": "docs/evidence/candidate-current-overview-v63.json",
            "sha256": "e78207ec0e2af2470287d3afbc12bee0270d29fa7ed7483a1f62eb72a0b4016c",
        },
        "svg": {
            "bytes": 14765,
            "device": 2064,
            "inode": 428916,
            "mode": "0600",
            "path": "docs/evidence/candidate-current-overview-v63.svg",
            "sha256": "9860367eb080240efd36e5c241fe0f7d6305d351d87152e2007b92beff496d7e",
        },
    },
    "previous_overview_version": 63,
    "previous_phase1_completeness": {
        "bytes": 28440,
        "device": 2064,
        "inode": 525073,
        "mode": "0600",
        "path": "oracle/phase1/p0-completeness-v2.json",
        "sha256": "fcd7abac619a6a4733e090cf49acbb958f8162eeb7dc6909a9d14501809e8237",
    },
    "previous_phase1_completeness_status": "BLOCKED",
    "protocol": {
        "bytes": 4261,
        "device": 2064,
        "inode": 524712,
        "mode": "0600",
        "path": "oracle/phase1/P0-COMPLETENESS-V4.md",
        "sha256": "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
    },
    "qualified_candidate_count": 0,
    "schema": "rebar-cpython-re-p0-completeness-v4",
    "source": {
        "bytes": 29094,
        "device": 2064,
        "inode": 428927,
        "mode": "0600",
        "path": "tools/verify_owned_p0_completeness_v4.py",
        "sha256": "8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d",
    },
    "source_crosswalk_status": "PASS",
    "source_only_effects": {
        "actual_candidate_workers_started": 0,
        "actual_compiler_processes_started": 0,
        "actual_native_activations": 0,
        "actual_reference_workers_started": 0,
        "clock_samples": 0,
        "compressed_archives_opened": 0,
        "hidden_holdout_opened": False,
        "memory": "NOT MEASURED",
        "network_operations": 0,
        "performance": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    },
    "status": "PASS",
    "status_scope": "PHASE 1 PYTHON-ORACLE READINESS ONLY",
    "supplemental_public_contracts": {
        "all_supplemental_case_denominators_separate": True,
        "callable_introspection": {
            "actual_reference_process_ids": [
                81,
                82,
            ],
            "actual_reference_receipt": {
                "bytes": 3533,
                "device": 2064,
                "inode": 524690,
                "mode": "0600",
                "path": "oracle/phase1/evidence/callable-introspection-reference-v2-cpython-3.14.6-publication-receipt.json",
                "sha256": "29b4a389e1b99cce15f07069ee1a0895f193e13400f944a037a4f42832619334",
            },
            "candidate_qualified": False,
            "candidate_status": "NOT RUN",
            "case_count": 50,
            "contract": {
                "bytes": 14749,
                "device": 2064,
                "inode": 524650,
                "mode": "0600",
                "path": "oracle/phase1/p0-callable-introspection-v1.json",
                "sha256": "e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349",
            },
            "included_in_original_case_denominator": False,
            "matrix_sha256": "89ff9e5197ac0fee63a5b7f3880d9d66083f7e25255d0d062e14ff84ab5c884b",
            "protocol": {
                "bytes": 8952,
                "device": 2064,
                "inode": 524649,
                "mode": "0600",
                "path": "oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md",
                "sha256": "1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8",
            },
            "reference_contract": {
                "bytes": 7253,
                "device": 2064,
                "inode": 524694,
                "mode": "0600",
                "path": "oracle/phase1/callable-introspection-reference-v2.json",
                "sha256": "0f87ef8926771cfe39e33d95b3b871f03c9f1c44fe932615f7067d391eb68f42",
            },
            "reference_protocol": {
                "bytes": 7487,
                "device": 2064,
                "inode": 524684,
                "mode": "0600",
                "path": "oracle/phase1/CALLABLE-INTROSPECTION-REFERENCE-V2.md",
                "sha256": "1e316b848e5d7a44b83a8f44605f08370faacb33074c2b79c042c76d9390a59f",
            },
            "reference_source": {
                "bytes": 86258,
                "device": 2064,
                "inode": 431230,
                "mode": "0600",
                "path": "tools/run_owned_callable_introspection_reference_v2.py",
                "sha256": "00c543077bfbe38e5c48e9970f7881119d21cb32cf91e838d21587f8f820ada4",
            },
            "two_reference_status": "PASS",
            "worker": {
                "bytes": 75608,
                "device": 2064,
                "inode": 428944,
                "mode": "0600",
                "path": "tools/verify_python_re_callable_introspection_v1.py",
                "sha256": "5a64fb4546bdccd13b6d8d9ba32a7472b01cb86dd0d9f2c643678e6bbf919653",
            },
        },
        "genuine_large_input": {
            "actual_candidate_dry_run_maximum": 5147,
            "candidate_qualified": False,
            "contract": {
                "bytes": 17322,
                "device": 2064,
                "inode": 524819,
                "mode": "0600",
                "path": "oracle/phase1/p0-large-input-indexing-v1.json",
                "sha256": "23601fe4947c70979081d8248ee9891287e3fa618b554b97a8ee56024823bacf",
            },
            "exact_subject_size": 2147483648,
            "full_size_candidate_search": "NOT RUN",
            "full_size_candidate_substitution": "NOT RUN",
            "historical_reference_memory_allowance_bytes": 42949672960,
            "historical_two_reference_status": "PASS",
            "included_in_original_case_denominator": False,
            "matrix_sha256": "a105aea287d093ff977819dda8971f592c3ed396eabd3133e5c52838ce8e2f65",
            "original_large_method_count": 2,
            "protocol": {
                "bytes": 5345,
                "device": 2064,
                "inode": 524897,
                "mode": "0600",
                "path": "oracle/phase1/P0-LARGE-INPUT-INDEXING-V1.md",
                "sha256": "0a640ee044c52394fa897d0221d51dfc3d85e9abb95608367698f11fba8ca879",
            },
            "source": {
                "bytes": 99829,
                "device": 2064,
                "inode": 431873,
                "mode": "0600",
                "path": "tools/verify_large_input_indexing_v1.py",
                "sha256": "57a9e0d0e456b854cb46dfadb2b23db244597f01904fcf93587b1f5d8a5e4544",
            },
            "source_observation_count": 32,
        },
        "module_version_observations_already_in_thread_suite": 32,
        "module_version_observations_counted_again": False,
        "public_import": {
            "actual_public_entrypoint_status": "FAIL",
            "candidate_qualified": False,
            "classification": "UNQUALIFIED_ZIG_PROTOTYPE",
            "contract": {
                "bytes": 9823,
                "device": 2064,
                "inode": 524881,
                "mode": "0600",
                "path": "oracle/phase1/p0-public-entrypoint-import-v1.json",
                "sha256": "b80ba35a6af481f0dd1c5b9141e2995f7b0ffd12f8ffa7060bab50344ddbda47",
            },
            "included_in_original_case_denominator": False,
            "installed_public_artifact": "NOT MEASURED",
            "matrix_sha256": "f67f8d4d62f9939c94250ad2e4df55b14df013df7212aa66930ecc3a772d2a58",
            "protocol": {
                "bytes": 7991,
                "device": 2064,
                "inode": 524880,
                "mode": "0600",
                "path": "oracle/phase1/P0-PUBLIC-ENTRYPOINT-IMPORT-V1.md",
                "sha256": "01ace52c6285142733bdcb2b4556feb43226e01c8b181b84019b8fa8c42697c0",
            },
            "source": {
                "bytes": 83957,
                "device": 2064,
                "inode": 431858,
                "mode": "0600",
                "path": "tools/verify_public_entrypoint_import_v1.py",
                "sha256": "c0a61c4cf520e82bf0c327a17c06daf64f57a1dcfd20b37c6e9f7b84177108b4",
            },
            "source_observation_count": 32,
            "source_observation_status": "PASS",
        },
    },
    "undefined_behavior": "NOT MEASURED",
    "version": 4,
    "winner_selected": False,
}


def load_v63() -> tuple:
    path, fingerprint, size = V63["source"]
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
            raise ValueError("reject substituted exact pushed V63 source")
        parts = []
        remaining = size
        while remaining:
            part = os.read(handle, min(remaining, 262144))
            if not part:
                raise ValueError("reject truncated pushed V63 source")
            parts.append(part)
            remaining -= len(part)
        if os.read(handle, 1):
            raise ValueError("reject extended pushed V63 source")
        raw = b"".join(parts)
        after = os.fstat(handle)
        if (hashlib.sha256(raw).hexdigest() != fingerprint
                or (before.st_dev, before.st_ino, before.st_size,
                    before.st_nlink, before.st_mtime_ns, before.st_ctime_ns)
                != (after.st_dev, after.st_ino, after.st_size,
                    after.st_nlink, after.st_mtime_ns, after.st_ctime_ns)):
            raise ValueError("reject changed exact pushed V63 source")
    finally:
        os.close(handle)
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v63")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    prior_modules = previous.load_v62()
    base = prior_modules[-1]
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v63"
        and previous.SELF == path
        and previous.PUBLIC_COUNTS == PUBLIC_COUNTS
        and previous.LARGE_COUNTS == LARGE_COUNTS
        and previous.WORKERS == WORKERS,
        "authenticate only exact pushed current V63 graph source",
    )
    return previous, prior_modules, base



def v63_options(previous: types.ModuleType) -> argparse.Namespace:
    return argparse.Namespace(
        source_sha256=V63["source"][1],
        source_bytes=V63["source"][2],
        previous_source_sha256=previous.V62["source"][1],
        previous_inputs_sha256=previous.V62["inputs"][1],
        previous_summary_sha256=previous.V62["summary"][1],
        previous_svg_sha256=previous.V62["svg"][1],
        evidence_reference_one_sha256=previous.EVIDENCE["reference_one"][1],
        evidence_reference_two_sha256=previous.EVIDENCE["reference_two"][1],
        evidence_aggregate_sha256=previous.EVIDENCE["aggregate"][1],
        inputs_sha256=None,
        summary_sha256=None,
        svg_sha256=None,
    )

def authenticate_v63(modules: tuple,
                     supplied: dict[str, str]) -> tuple[dict, dict, bytes]:
    previous, prior_modules, base = modules
    raw = {}
    for role, item in V63.items():
        base.need(
            base.checked(supplied.get(role), "actual pushed V63 " + role)
            == item[1],
            "reject substituted genuine two-worker V63 " + role,
        )
        raw[role], _ = base.read_owner(*item, private=True)
    old = base.document(raw["summary"], "complete actual V63 summary")
    inputs = base.document(raw["inputs"], "complete actual V63 inputs")
    previous.validate_snapshot(prior_modules, old.get("snapshot"))
    reconstructed, pairs = previous.build(prior_modules, v63_options(previous))
    expected = dict(pairs)
    base.need(
        old.get("schema") == "rebar-candidate-current-overview-v63-summary"
        and old.get("version") == 63
        and old.get("status") == "PASS"
        and old.get("source") == base.pin(*V63["source"])
        and old.get("inputs") == base.pin(*V63["inputs"])
        and old.get("svg") == base.pin(*V63["svg"])
        and inputs.get("schema")
            == "rebar-candidate-current-overview-v63-inputs"
        and inputs.get("version") == 63
        and inputs.get("renderer") == base.pin(*V63["source"])
        and old.get("snapshot") == reconstructed
        and raw["inputs"] == expected[V63["inputs"][0]]
        and raw["summary"] == expected[V63["summary"][0]]
        and raw["svg"] == expected[V63["svg"][0]]
        and old.get("actual_current_graph_predecessor_version") == 62
        and old["snapshot"].get("actual_current_graph_predecessor_version")
            == 62
        and inputs.get("actual_current_graph_predecessor_version") == 62
        and old.get("phase1_differential_fuzz_reference_v3_execution_status")
            == "PASS"
        and old.get("phase1_differential_fuzz_reference_v3_worker_count") == 2
        and old.get(
            "phase1_differential_fuzz_reference_v3_worker_process_ids")
            == [81, 82]
        and old.get(
            "phase1_differential_fuzz_reference_v3_actual_worker_owner_inodes")
            == [524693, 524692]
        and old.get(
            "phase1_differential_fuzz_reference_v3_actual_worker_exit_codes")
            == [0, 0]
        and old.get(
            "phase1_differential_fuzz_reference_v3_actual_worker_case_counts")
            == [8244, 8244]
        and old.get("actual_rust_semantic_mismatch_count") == 1440
        and old.get("actual_rust_verified_passing_case_count") == 14853
        and old.get("actual_rust_v7_semantic_mismatch_count") == 928
        and old.get("actual_rust_v7_explicitly_verified_passing_case_count")
            == 8965
        and old.get("actual_rust_v10_candidate_status") == "FAIL"
        and old.get("actual_rust_v10_candidate_workers") == 13
        and old.get("actual_rust_v10_worker_process_ids") == WORKERS
        and old.get("actual_rust_v10_semantic_mismatch_regression_against_v7")
            == 512
        and old.get("actual_rust_v10_infrastructure_failure_count") == 0
        and old.get("actual_rust_v10_all_four_original_targets_restored")
            is True
        and len(old.get(
            "actual_rust_v10_complete_independently_authenticated_suite_results",
            [],
        )) == 13
        and len(old.get("actual_rust_v10_earliest_genuine_mismatch_witnesses",
                        [])) == 6
        and old.get("candidate_facing_self_oracle_status") == "BLOCKED"
        and old.get("phase1_completeness_status") == "BLOCKED"
        and old.get("phase1_corrected_crosswalk_status") == "PASS"
        and old.get("phase1_canonical_candidate_context_crosswalk") == "PASS"
        and old.get("phase1_v2_reconciliation") == "BLOCKED"
        and old.get("phase1_v1_public_type_reference_status") == "FALSIFIED"
        and old.get("phase1_v2_corrected_reference_case_count") == 6912
        and old.get("phase1_v2_corrected_reference_process_ids") == [81, 82]
        and old.get("phase1_v2_supplemental_dual_reference_status") == "PASS"
        and old.get("phase1_v2_supplemental_candidate_status") == "NOT RUN"
        and old.get("candidate_evaluation_authorized") is False
        and old.get("authenticated_evidence_owner_lower_bound") == 213
        and old.get("authenticated_history_reference_lower_bound") == 218
        and old.get("public_entrypoint_case_status_counts") == PUBLIC_COUNTS
        and old.get("large_input_source_case_status_counts") == LARGE_COUNTS
        and old.get("first_party_source_inventory_family_count") == 6
        and old.get("qualified_candidate_count") == 0
        and old.get("final_comparison_planned_case_count") == 4194304
        and old.get("final_comparison_cases_generated") is False
        and old.get("final_holdout_opened") is False,
        "reproduce actual V63 workers, all suite vectors and sealed holdout",
    )
    return old, inputs, raw["svg"]

def readiness_expectations() -> dict:
    return copy.deepcopy(READINESS_EXPECTATIONS)


def make_readiness_proof(base: types.ModuleType, owners: dict,
                        contract: dict) -> dict:
    candidate = contract["candidate_qualification_gate"]
    return {
        "schema": SCHEMA + "-authenticated-p0-readiness-v4",
        "version": 4,
        "status": "PASS",
        "oracle_readiness_status": "PASS",
        "phase2_candidate_testing_authorized": True,
        "candidate_qualification_status": "BLOCKED",
        "candidate_qualification_blockers":
            copy.deepcopy(candidate["blockers"]),
        "candidate_qualified": False,
        "qualified_candidate_count": 0,
        "actual_reference_status": "PASS",
        "actual_reference_worker_count": 2,
        "actual_reference_case_count": 8244,
        "reference_workers_started_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "native_libraries_loaded_by_graph": 0,
        "compressed_archives_opened_by_graph": 0,
        "holdout_files_opened_by_graph": 0,
        "clock_samples_by_graph": 0,
        "owners": copy.deepcopy(owners),
        "complete_readiness_contract": copy.deepcopy(contract),
    }

def validate_readiness_proof(base: types.ModuleType,
                            proof: object) -> None:
    base.need(type(proof) is dict,
              "reject missing complete P0 phase-two readiness proof")
    assert isinstance(proof, dict)
    contract = readiness_expectations()
    owners = {
        role: base.synthetic_owner(item, READINESS_INODES[role])
        for role, item in READINESS.items()
    }
    expected = make_readiness_proof(base, owners, contract)
    base.need(set(proof) == set(expected),
              "reject omitted readiness or qualification proof fields")
    for key, value in expected.items():
        base.need(
            type(proof.get(key)) is type(value)
            and proof.get(key) == value,
            "reject invented candidate or phase-readiness result: " + key,
        )
    gate = contract["phase_gate"]
    candidate = contract["candidate_qualification_gate"]
    base.need(
        contract["status"] == "PASS"
        and gate["status"] == "PASS"
        and gate["candidate_evaluation_authorized"] is True
        and gate["performance_oracle_authorized"] is False
        and gate["final_holdout_authorized"] is False
        and gate["qualified_candidate_count"] == 0
        and candidate["status"] == "BLOCKED"
        and candidate["qualified_candidate_count"] == 0
        and len(candidate["blockers"]) == 7
        and proof["oracle_readiness_status"] == "PASS"
        and proof["phase2_candidate_testing_authorized"] is True
        and proof["candidate_qualification_status"] == "BLOCKED"
        and proof["candidate_qualified"] is False
        and proof["qualified_candidate_count"] == 0
        and proof["actual_reference_status"] == "PASS"
        and proof["actual_reference_worker_count"] == 2
        and proof["actual_reference_case_count"] == 8244
        and proof["reference_workers_started_by_graph"] == 0
        and proof["candidate_workers_started_by_graph"] == 0
        and proof["compiler_processes_started_by_graph"] == 0
        and proof["native_libraries_loaded_by_graph"] == 0
        and proof["compressed_archives_opened_by_graph"] == 0
        and proof["holdout_files_opened_by_graph"] == 0
        and proof["clock_samples_by_graph"] == 0,
        "separate a passing oracle from seven-blocker candidate qualification",
    )

def authenticate_readiness(base: types.ModuleType,
                          options: argparse.Namespace) -> dict:
    owners = {}
    actual_contract = None
    for role, item in READINESS.items():
        supplied = getattr(options, "readiness_" + role + "_sha256")
        base.need(
            base.checked(supplied, "exact P0 readiness " + role)
            == item[1],
            "reject substituted exact P0 readiness owner: " + role,
        )
        raw, meta = base.read_owner(*item, private=True)
        base.need(
            meta["device"] == 2064
            and meta["inode"] == READINESS_INODES[role]
            and meta["nlink"] == 1,
            "reject substituted private readiness owner: " + role,
        )
        owners[role] = base.synthetic_owner(item, READINESS_INODES[role])
        if role == "contract":
            actual_contract = base.document(raw, "complete P0 V3 contract")
    base.need(
        actual_contract == readiness_expectations(),
        "reject incomplete actual source-frozen readiness contract",
    )
    assert isinstance(actual_contract, dict)
    proof = make_readiness_proof(base, owners, actual_contract)
    validate_readiness_proof(base, proof)
    return proof

def result_fields(proof: dict) -> dict:
    return {
        "actual_current_graph_predecessor_version": 63,
        "actual_rust_semantic_mismatch_count": 1440,
        "actual_rust_verified_passing_case_count": 14853,
        "rust_actual_semantic_mismatch_count": 1440,
        "rust_original_campaign_semantic_mismatch_count": 1440,
        "rust_original_campaign_verified_passing_case_count": 14853,
        "rust_verified_passing_case_executions": 14853,
        "candidate_facing_self_oracle_status": "PASS",
        "phase1_completeness_status": "PASS",
        "phase1_corrected_crosswalk_status": "PASS",
        "phase1_canonical_candidate_context_crosswalk": "PASS",
        "phase1_v2_reconciliation": "BLOCKED",
        "phase1_v1_public_type_reference_status": "FALSIFIED",
        "phase1_v2_corrected_reference_case_count": 6912,
        "phase1_v2_corrected_reference_process_ids": [81, 82],
        "phase1_v2_supplemental_fuzz_stream_status": "VERIFIED",
        "phase1_v2_supplemental_fuzz_unique_record_count": 8244,
        "phase1_v2_supplemental_independently_referenced_case_count": 8244,
        "phase1_v2_supplemental_dual_reference_status": "PASS",
        "phase1_v2_supplemental_candidate_status": "NOT RUN",
        "supplemental_differential_fuzz_candidate_gate": "BLOCKED",
        "supplemental_differential_fuzz_case_count": 8244,
        "phase1_differential_fuzz_reference_v3_source_status":
            "SOURCE FROZEN",
        "phase1_differential_fuzz_reference_v3_execution_status": "PASS",
        "phase1_differential_fuzz_reference_v3_worker_count": 2,
        "phase1_differential_fuzz_reference_v3_worker_process_ids": [81, 82],
        "phase1_differential_fuzz_reference_v3_reference_case_count": 8244,
        "phase1_differential_fuzz_reference_v3_candidate_case_count": 0,
        "phase1_differential_fuzz_reference_v3_actual_worker_result_count": 2,
        "phase1_differential_fuzz_reference_v3_actual_worker_exit_codes":
            [0, 0],
        "phase1_differential_fuzz_reference_v3_actual_worker_case_counts":
            [8244, 8244],
        "phase1_differential_fuzz_reference_v3_actual_worker_failure_counts":
            [0, 0],
        "phase1_differential_fuzz_reference_v3_actual_worker_owner_inodes":
            [524693, 524692],
        "phase1_differential_fuzz_reference_v3_actual_run_label":
            "cpython-3146-two-worker-8244-v3",
        "phase1_v4_oracle_readiness_status": "PASS",
        "phase1_v4_candidate_testing_authorized": True,
        "phase1_v4_candidate_qualification_status": "BLOCKED",
        "phase1_v4_candidate_qualification_blockers":
            copy.deepcopy(proof["candidate_qualification_blockers"]),
        "phase1_v4_candidate_qualification_blocker_count": 7,
        "phase1_v4_readiness_source_freeze": copy.deepcopy(proof),
        "candidate_qualification_status": "BLOCKED",
        "candidate_qualification_blockers":
            copy.deepcopy(proof["candidate_qualification_blockers"]),
        "genuine_2gib_candidate_search": "NOT RUN",
        "genuine_2gib_candidate_substitution": "NOT RUN",
        "candidate_evaluation_authorized": True,
        "rust_native_build_v17_source_status": "SOURCE FROZEN",
        "rust_native_build_v17_status": "NOT RUN",
        "rust_native_build_v17_authorization_status": "BLOCKED",
        "rust_native_build_v17_blocking_reason":
            "FROZEN V17 REQUIRES HISTORICAL BLOCKED P0 V2",
        "rust_native_build_v17_matching_status": "NOT RUN",
        "rust_native_build_v17_candidate_correctness": "NOT MEASURED",
        "rust_native_build_v17_candidate_qualified": False,
        "rust_native_build_v17_compiler_process_count": 0,
        "rust_native_build_v17_compiler_process_ids": [],
        "rust_native_build_v17_native_binary_count": 0,
        "rust_native_build_v17_native_artifact_hashes": [],
        "rust_native_build_v17_candidate_workers_started": 0,
        "rust_native_build_v17_independent_source_owner_count": 3,
        "authenticated_evidence_owner_lower_bound": 216,
        "authenticated_history_reference_lower_bound": 221,
        "actual_phase1_readiness_source_owners_read_by_graph": 3,
        "actual_reference_workers_started_by_graph": 0,
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
              "reject missing complete oracle-ready V64 graph snapshot")
    assert isinstance(snapshot, dict)
    proof = snapshot.get("phase1_v4_readiness_source_freeze")
    validate_readiness_proof(base, proof)
    assert isinstance(proof, dict)
    updates = result_fields(proof)
    for key, value in updates.items():
        base.need(
            type(snapshot.get(key)) is type(value)
            and snapshot.get(key) == value,
            "reject invented P0 readiness or candidate result: " + key,
        )
    replaced = snapshot.get("preserved_v63_replaced_snapshot_fields")
    base.need(type(replaced) is dict and set(replaced).issubset(updates),
              "preserve all exact replaced actual V63 evidence fields")
    assert isinstance(replaced, dict)
    base.need(
        replaced.get("actual_current_graph_predecessor_version") == 62
        and replaced.get("phase1_completeness_status") == "BLOCKED"
        and replaced.get("candidate_evaluation_authorized") is False,
        "preserve exact V63 history without suppressing phase transition",
    )
    history = copy.deepcopy(snapshot)
    history.pop("preserved_v63_replaced_snapshot_fields", None)
    for key in updates:
        if key in replaced:
            history[key] = copy.deepcopy(replaced[key])
        else:
            history.pop(key, None)
    previous.validate_snapshot(prior_modules, history)
    base.need(
        snapshot.get("actual_current_graph_predecessor_version") == 63
        and snapshot.get("phase1_v2_reconciliation") == "BLOCKED"
        and snapshot.get("phase1_v4_oracle_readiness_status") == "PASS"
        and snapshot.get("candidate_qualification_status") == "BLOCKED"
        and len(snapshot.get("candidate_qualification_blockers", [])) == 7
        and snapshot.get(
            "phase1_differential_fuzz_reference_v3_worker_process_ids")
            == [81, 82]
        and snapshot.get(
            "phase1_differential_fuzz_reference_v3_actual_worker_owner_inodes")
            == [524693, 524692]
        and snapshot.get("actual_rust_semantic_mismatch_count") == 1440
        and snapshot.get("actual_rust_verified_passing_case_count") == 14853
        and snapshot.get("actual_rust_v7_semantic_mismatch_count") == 928
        and snapshot.get("actual_rust_v7_explicitly_verified_passing_case_count")
            == 8965
        and snapshot.get("actual_rust_v10_candidate_status") == "FAIL"
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
        and snapshot.get("phase1_v2_correctness_gate_blockers")
            == history.get("phase1_v2_correctness_gate_blockers")
        and len(snapshot.get("phase1_v2_correctness_gate_blockers", [])) == 7
        and snapshot.get("phase1_v2_oracle_reconciliation")
            == history.get("phase1_v2_oracle_reconciliation")
        and snapshot.get("phase1_differential_fuzz_reference_v3_actual_result")
            == history.get(
                "phase1_differential_fuzz_reference_v3_actual_result")
        and snapshot.get("rust_native_build_v17_authorization_status")
            == "BLOCKED"
        and snapshot.get("rust_native_build_v17_blocking_reason")
            == "FROZEN V17 REQUIRES HISTORICAL BLOCKED P0 V2"
        and snapshot.get("rust_native_build_v17_status") == "NOT RUN"
        and snapshot.get("rust_native_build_v17_compiler_process_count")
            == 0
        and snapshot.get("rust_buffer_shape_v2_feature_status")
            == "SOURCE FROZEN"
        and snapshot.get("rust_buffer_shape_v2_build_status") == "NOT BUILT"
        and snapshot.get("rust_buffer_shape_v2_matching_status") == "NOT RUN"
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
        and snapshot.get("first_party_source_inventory_family_count") == 6
        and snapshot.get("actually_tested_corrected_candidate_families")
            == ["rust"]
        and snapshot.get("actually_tested_corrected_candidate_family_count")
            == 1
        and snapshot.get("currently_activated_candidate_family_count") == 0
        and snapshot.get("actually_runnable_candidate_family_count") == 0
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("final_comparison_planned_case_count") == 4194304
        and snapshot.get("final_comparison_cases_generated") is False
        and snapshot.get("final_holdout_opened") is False,
        "authenticate oracle readiness without inventing passing candidates",
    )

def replace_once(base: types.ModuleType, visible: str,
                 before: str, after: str, description: str) -> str:
    base.need(type(visible) is str and type(before) is str
              and type(after) is str and visible.count(before) == 1,
              "reject substituted pushed V63 chart section: " + description)
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
        forged["__forged_v64__"] = True
        return forged
    if value is None:
        return "FORGED"
    return object()



def make_svg(modules: tuple, snapshot: dict, old_svg: bytes,
             source_sha: str, inputs_sha: str) -> bytes:
    previous, prior_modules, base = modules
    validate_snapshot(modules, snapshot)
    source_sha = base.checked(source_sha, "exact current V64 renderer")
    inputs_sha = base.checked(inputs_sha, "exact current V64 inputs")
    visible = old_svg.decode("utf-8").replace(
        "v63-title", "v64-title").replace(
        "v63-description", "v64-description")
    lines = visible.splitlines()
    base.need(
        len(lines) > 10
        and lines[1].startswith('<title id="v64-title">')
        and lines[2].startswith('<desc id="v64-description">'),
        "preserve exact pushed accessible genuine V63 graph",
    )
    lines[1] = (
        '<title id="v64-title">Building a faster Python re: Python '
        'baseline verified; candidate testing can begin, but no '
        'replacement is qualified</title>'
    )
    lines[2] = (
        '<desc id="v64-description">Pinned stable Python 3.14.6 '
        'has a verified baseline. Two actual independent Python '
        'workers passed all 8,244 separately counted fuzz and '
        'differential cases. Their genuine current run PIDs 81 '
        'and 82, distinct evidence inodes 524693 and 524692, '
        'zero exits, seven seeds, 19 case categories and 45 '
        'mapped obligations remain independently authenticated. '
        'The additive phase-one V4 correctness oracle readiness '
        'is PASS and authorizes phase-two candidate correctness '
        'testing. This is not candidate qualification: the '
        'separate qualification gate is BLOCKED by all seven '
        'genuine candidate blockers. No candidate has passed '
        'the full original 31,237-case suite, the 8,244-case '
        'supplement, public import and callable checks, real '
        '2-GiB checks or the runtime independence audit. '
        'The immutable historical V2 phase-one gate remains '
        'BLOCKED. Six independent first-party candidate '
        'families and zero qualified replacements remain. '
        'The real from-scratch Rust campaign still has 1,440 '
        'mismatches, 14,853 explicitly verified passes, 13 '
        'actual workers, 13 full suites and six genuine '
        'witnesses. Historical V7 had 928 mismatches and '
        '8,965 verified passes; the regression is 512. '
        'Exactly three genuine new readiness owners raise '
        'the evidence and history lower bounds from 213 / '
        '218 to 216 / 221. Original 31,237 cases, 50 '
        'signature checks, 32 public-interface observations, '
        '32 large-input observations and 8,244 supplemental '
        'cases retain their separate denominators. The native '
        'frozen Rust V17 remains BLOCKED because it '
        'requires historical blocked P0 V2. The repair '
        'is NOT BUILT; actual builds are NOT RUN, '
        'with 0 compilers and 0 binaries. The hidden '
        '4,194,304-case holdout is NOT OPENED and not '
        'generated. Speed, memory, confidence intervals '
        'and undefined behavior are NOT MEASURED; runtime '
        'independence remains NOT ESTABLISHED.</desc>'
    )
    visible = "\n".join(lines)
    replacements = (
        (
            '<text x="65" y="398" class="heading">Two Python runs '
            'pass 8,244 tests; engines still unproven</text>',
            '<text x="65" y="398" class="heading">Python baseline '
            'verified; candidate testing can begin</text>',
            "show verified oracle readiness without qualifying an engine",
        ),
        (
            'Two real Python processes each pass all 8,244 tests. '
            'Replacement-engine tests remain NOT RUN.',
            'Two Python workers passed all 8,244 tests. Candidate '
            'testing is now authorized; zero engines are qualified.',
            "separate authorized candidate testing from measured correctness",
        ),
        (
            '<text x="64" y="1756" class="heading">Two genuine '
            'Python reference workers passed; candidates have not run</text>',
            '<text x="64" y="1756" class="heading">Oracle ready; '
            'all seven candidate qualification blockers remain</text>',
            "differentiate readiness PASS from candidate qualification BLOCKED",
        ),
        (
            'Exactly three actual reference-result owners raise '
            'lower bounds from 210 / 215 to 213 / 218.',
            'Exactly three new readiness-source owners raise '
            'lower bounds from 213 / 218 to 216 / 221.',
            "count only three independently authenticated readiness owners",
        ),
        (
            'Real Rust failures remain proven. Two Python '
            'reference workers passed; candidate correctness '
            'remains BLOCKED and speed is NOT MEASURED.',
            'Real Rust failures remain proven. Python is verified; '
            'candidate qualification remains BLOCKED and '
            'speed is NOT MEASURED.',
            "preserve actual failed Rust and no invented benchmarks",
        ),
    )
    for before, after, why in replacements:
        visible = replace_once(base, visible, before, after, why)
    lines = visible.splitlines()
    start = next(
        (i for i, line in enumerate(lines)
         if line.startswith('<rect x="44" y="1858" width="1352"')),
        None,
    )
    base.need(type(start) is int, "retain exact V63 evidence footer")
    assert isinstance(start, int)
    lines = lines[:start]
    lines.extend((
        '<rect x="44" y="1858" width="1352" height="381" rx="16" '
        'fill="#fff" stroke="#d8e2ed"/>',
        '<text x="64" y="1888" class="heading">Verified Python '
        'baseline and separate blocked candidate-qualification gate</text>',
    ))
    footers = (
        ("Graph inputs SHA-256", inputs_sha),
        ("Graph renderer SHA-256", source_sha),
        ("Historical V63 graph inputs SHA-256", V63["inputs"][1]),
        ("Historical V63 graph renderer SHA-256", V63["source"][1]),
        ("Historical V63 graph summary SHA-256", V63["summary"][1]),
        ("Historical V63 graph image SHA-256", V63["svg"][1]),
        ("Actual first distinct Python worker SHA-256",
         previous.EVIDENCE["reference_one"][1]),
        ("Actual second distinct Python worker SHA-256",
         previous.EVIDENCE["reference_two"][1]),
        ("Actual independently executed Python result SHA-256",
         previous.EVIDENCE["aggregate"][1]),
        ("Oracle-readiness verifier source SHA-256",
         READINESS["source"][1]),
        ("Oracle-readiness protocol SHA-256",
         READINESS["protocol"][1]),
        ("Complete PASS readiness contract SHA-256",
         READINESS["contract"][1]),
    )
    for i, (label, value) in enumerate(footers):
        lines.append(
            f'<text x="65" y="{1914 + i * 18}" class="foot">'
            f'{label}: {value}</text>'
        )
    lines.extend((
        '<text x="65" y="2139" class="small">Oracle readiness: '
        'PASS. Two Python workers each passed 8,244 cases.</text>',
        '<text x="65" y="2158" class="small">Candidate testing: '
        'AUTHORIZED. Qualification: BLOCKED; seven blockers.</text>',
        '<text x="65" y="2177" class="small">Actual Rust: '
        '1,440 differences; 14,853 verified passes; '
        '13 real workers.</text>',
        '<text x="65" y="2196" class="small">Qualified engines: '
        '0. Candidate correctness: NOT RUN. Speed: NOT MEASURED.</text>',
        '<text x="65" y="2215" class="small">Six independent '
        'families. Final holdout: NOT OPENED.</text>',
        '<!-- Source-only graph starts no reference or candidate, '
        'opens no archive or hidden holdout, performs no build '
        'or timing, and never identifies oracle readiness as '
        'candidate qualification. -->',
        "</svg>",
    ))
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    for label, value in footers:
        base.need(
            raw.count((label + ": " + value).encode("ascii")) == 1,
            "bind exact V64 readiness evidence footer: " + label,
        )
    lower = raw.lower()
    for phrase in (
            b'height="2250"', b"building a faster python re",
            b"python baseline verified", b"oracle readiness",
            b"candidate testing", b"candidate qualification",
            b"v17 remains blocked", b"historical blocked p0 v2",
            b"seven", b"blocked", b"8,244", b"two python workers",
            b"524693", b"524692", b"seven seeds", b"19",
            b"45", b"1,440", b"14,853", b"13 real workers",
            b"512", b"928", b"8,965",
            b"managed 16", b"substitution 368", b"shape 1,056",
            b"31,237", b"4.2m unopened", b"not opened",
            b"not built", b"not run", b"0 compilers", b"0 binaries",
            b"not measured", b"not established",
            b"213 / 218", b"216 / 221",
            b"signature checks", b"public-interface observations",
            b"large-input observations", b"17 pass", b"7 fail",
            b"22 pass", b"3 not run", b"2,147,483,648",
            b"1,087", b"1,036", b"1,262", b"1,230",
            b"2,172", b"1,764", b"not generated"):
        base.need(phrase in lower,
                  "preserve honest readiness transition: " + repr(phrase))
    for falsehood in (
            b"v17 authorized", b"v17 build authorized",
            b"candidate qualified", b"three qualified candidates",
            b"all candidate tests passed", b"phase-one v2 passed",
            b"holdout opened", b"holdout generated",
            b"benchmark speedup", b"winner selected",
            b"verify_p0_completeness_v2.py"):
        base.need(falsehood not in lower,
                  "reject invented candidate readiness: " + repr(falsehood))
    return raw

def build(modules: tuple,
          options: argparse.Namespace) -> tuple[dict, tuple]:
    previous, prior_modules, base = modules
    source_sha = base.checked(options.source_sha256,
                              "exact oracle-readiness V64 graph renderer")
    base.need(
        type(options.source_bytes) is int
        and 0 < options.source_bytes <= base.OWNER_LIMIT,
        "bound exact root-authorized private V64 renderer",
    )
    own_raw, _ = base.read_owner(
        SELF, source_sha, options.source_bytes, private=True,
    )
    old, old_inputs, old_svg = authenticate_v63(
        modules,
        {role: getattr(options, "previous_" + role + "_sha256")
         for role in V63},
    )
    proof = authenticate_readiness(base, options)
    updates = result_fields(proof)
    original = old["snapshot"]
    snapshot = copy.deepcopy(original)
    snapshot.update(updates)
    snapshot["preserved_v63_replaced_snapshot_fields"] = {
        key: copy.deepcopy(original[key])
        for key in updates if key in original
    }
    validate_snapshot(modules, snapshot)
    predecessor = {role: base.pin(*item) for role, item in V63.items()}
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 64,
        "python": "3.14.6",
        "renderer": base.pin(SELF, source_sha, len(own_raw)),
        "previous_overview": predecessor,
        **updates,
    })
    input_raw = base.canonical(inputs)
    svg = make_svg(
        modules, snapshot, old_svg, source_sha, base.digest(input_raw),
    )
    families = copy.deepcopy(old["families"])
    base.need(
        [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "preserve six independently authored from-scratch candidates",
    )
    for row in families:
        if row.get("family") == "python":
            row.update({
                "supplemental_reference_status": "PASS",
                "supplemental_reference_worker_count": 2,
                "supplemental_reference_case_count": 8244,
                "oracle_readiness_status": "PASS",
            })
            continue
        row.update({
            "authenticated_evidence_owner_lower_bound": 216,
            "authenticated_history_reference_lower_bound": 221,
            "actually_tested_corrected_candidate_family_count": 1,
            "actually_tested_corrected_candidate_families": ["rust"],
            "currently_activated_candidate_family_count": 0,
            "actually_runnable_candidate_family_count": 0,
            "qualified": False,
            "performance": "NOT MEASURED",
            "phase1_completeness_status": "PASS",
            "phase1_corrected_crosswalk_status": "PASS",
            "candidate_evaluation_authorized": True,
            "candidate_qualification_status": "BLOCKED",
            "candidate_qualification_blocker_count": 7,
            "differential_fuzz_reference_source_status": "SOURCE FROZEN",
            "differential_fuzz_reference_execution_status": "PASS",
            "differential_fuzz_reference_worker_count": 2,
            "differential_fuzz_candidate_status": "NOT RUN",
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
                "native_build_v17_source_status": "SOURCE FROZEN",
                "native_build_v17_status": "NOT RUN",
                "native_build_v17_candidate_matching_status": "NOT RUN",
                "native_build_v17_candidate_correctness": "NOT MEASURED",
                "native_build_v17_compiler_process_count": 0,
                "native_build_v17_native_binary_count": 0,
                "native_build_v17_candidate_workers_started": 0,
                "native_build_v17_independent_source_owner_count": 3,
                "oracle_readiness_source_freeze": copy.deepcopy(proof),
            })
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 64,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, source_sha, len(own_raw)),
        "inputs": base.pin(
            OUTPUT + ".inputs.json", base.digest(input_raw), len(input_raw),
        ),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg), len(svg)),
        "previous_overview": predecessor,
        "snapshot": snapshot,
        "families": families,
        **updates,
    })
    base.need(
        inputs["actual_current_graph_predecessor_version"] == 63
        and summary["actual_current_graph_predecessor_version"] == 63
        and snapshot["actual_current_graph_predecessor_version"] == 63
        and snapshot["preserved_v63_replaced_snapshot_fields"][
            "actual_current_graph_predecessor_version"] == 62
        and summary["previous_overview"]["source"]["path"]
            == V63["source"][0]
        and summary["phase1_v4_oracle_readiness_status"] == "PASS"
        and summary["candidate_qualification_status"] == "BLOCKED"
        and len(summary["candidate_qualification_blockers"]) == 7
        and summary["qualified_candidate_count"] == 0,
        "bind true V63 predecessor and separate oracle/candidate gates",
    )
    base.need(
        inputs["rust_native_build_v17_authorization_status"] == "BLOCKED"
        and summary["rust_native_build_v17_authorization_status"]
            == "BLOCKED"
        and snapshot["rust_native_build_v17_authorization_status"]
            == "BLOCKED"
        and summary["rust_native_build_v17_blocking_reason"]
            == "FROZEN V17 REQUIRES HISTORICAL BLOCKED P0 V2"
        and inputs["rust_native_build_v17_status"] == "NOT RUN"
        and summary["rust_native_build_v17_status"] == "NOT RUN"
        and summary["candidate_evaluation_authorized"] is True
        and summary["phase1_v4_oracle_readiness_status"] == "PASS"
        and summary["candidate_qualification_status"] == "BLOCKED",
        "separate general phase-two eligibility from frozen blocked V17",
    )
    summary_raw = base.canonical(summary)
    base.need(
        max(len(input_raw), len(summary_raw), len(svg))
        <= base.OWNER_LIMIT,
        "bound only three root-authorized readiness V64 assets",
    )
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )

def reject_control(base: types.ModuleType, proof: dict,
                   description: str) -> int:
    try:
        validate_readiness_proof(base, proof)
    except (base.GraphError, TypeError, ValueError, KeyError,
            AttributeError, RecursionError):
        return 1
    raise base.GraphError("accepted forged P0 readiness: " + description)

def self_test(modules: tuple) -> dict:
    previous, prior_modules, base = modules
    prior = previous.self_test(prior_modules)
    base.need(
        prior.get("status") == "PASS"
        and prior.get("rejected_hostile_control_count") == 5126
        and prior.get("actual_current_graph_predecessor_version") == 62
        and prior.get("actual_rust_semantic_mismatch_count") == 1440
        and prior.get("actual_rust_verified_passing_case_count") == 14853
        and prior.get("actual_rust_v10_candidate_status") == "FAIL"
        and prior.get("actual_rust_v10_candidate_workers") == 13
        and prior.get("phase1_completeness_status") == "BLOCKED"
        and prior.get("phase1_corrected_crosswalk_status") == "PASS"
        and prior.get("phase1_differential_fuzz_reference_v3_execution_status")
            == "PASS"
        and prior.get("phase1_differential_fuzz_reference_v3_worker_count")
            == 2
        and prior.get(
            "phase1_differential_fuzz_reference_v3_worker_process_ids")
            == [81, 82]
        and prior.get(
            "phase1_differential_fuzz_reference_v3_actual_worker_owner_inodes")
            == [524693, 524692]
        and prior.get("candidate_evaluation_authorized") is False
        and prior.get("authenticated_evidence_owner_lower_bound") == 213
        and prior.get("authenticated_history_reference_lower_bound") == 218
        and prior.get("actual_failure_archives_opened_by_self_test") == 0,
        "preserve exactly 5,126 V63 controls and real baseline results",
    )
    rejected = 0
    with base.SourceOnlyWall() as wall:
        owners = {
            role: base.synthetic_owner(item, READINESS_INODES[role])
            for role, item in READINESS.items()
        }
        proof = make_readiness_proof(
            base, owners, readiness_expectations(),
        )
        validate_readiness_proof(base, proof)
        for key, value in proof.items():
            hostile = copy.deepcopy(proof)
            hostile[key] = forged_value(value)
            rejected += reject_control(base, hostile, "proof:" + key)
        for role, owner in proof["owners"].items():
            for key, value in owner.items():
                hostile = copy.deepcopy(proof)
                hostile["owners"][role][key] = forged_value(value)
                rejected += reject_control(
                    base, hostile, "owner:" + role + ":" + key,
                )
        for key, value in proof["complete_readiness_contract"].items():
            hostile = copy.deepcopy(proof)
            hostile["complete_readiness_contract"][key] = (
                forged_value(value)
            )
            rejected += reject_control(base, hostile, "contract:" + key)
        for group in ("phase_gate", "candidate_qualification_gate"):
            for key, value in proof["complete_readiness_contract"][
                    group].items():
                hostile = copy.deepcopy(proof)
                hostile["complete_readiness_contract"][group][key] = (
                    forged_value(value)
                )
                rejected += reject_control(
                    base, hostile, group + ":" + key,
                )
        checks = (
            ("filesystem", lambda: builtins.open("forbidden-v64")),
            ("filesystem", lambda: os.open("forbidden-v64", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v64")),
            ("write", lambda: os.mkdir("forbidden-v64")),
            ("process", lambda: subprocess.run(("forbidden-v64",))),
            ("process", lambda: subprocess.Popen(("forbidden-v64",))),
            ("process", lambda: os.execv("/forbidden-v64", [])),
        )
        for kind, action in checks:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(
                    wall.blocked[kind] == before + 1,
                    "physically forbid source-only V64 " + kind,
                )
            else:
                raise base.GraphError("allowed forbidden V64 " + kind)
        base.need(rejected >= 50,
                  "reject forged oracle, candidate and source claims")
        updates = result_fields(proof)
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 64,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v63_hostile_controls": 5126,
            "new_v64_hostile_controls": rejected,
            "rejected_hostile_control_count": 5126 + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "actual_phase1_readiness_source_owners_read_by_self_test": 0,
            "actual_reference_evidence_owners_read_by_self_test": 0,
            "actual_fuzz_reference_source_owners_read_by_self_test": 0,
            "actual_phase1_oracle_source_owners_read_by_self_test": 0,
            "actual_feature_source_owners_read_by_self_test": 0,
            "actual_build_source_owners_read_by_self_test": 0,
            "actual_forensic_summary_owners_read_by_self_test": 0,
            "actual_failure_archives_opened_by_self_test": 0,
            "actual_failure_archives_inflated_by_self_test": 0,
            "actual_build_archives_opened_by_self_test": 0,
            "actual_build_archives_inflated_by_self_test": 0,
            "actual_candidate_imports_by_graph": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "actual_native_libraries_loaded_by_graph": 0,
            "actual_large_subject_allocations_by_graph": 0,
            "actual_clock_samples_by_graph": 0,
            "actual_hidden_cases_read_by_graph": 0,
            "source_build_archive_gzip_inflation_count_by_graph": 0,
            **updates,
            "actual_rust_v7_semantic_mismatch_count": 928,
            "actual_rust_v7_explicitly_verified_passing_case_count": 8965,
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
            "holdout": "NOT OPENED",
        }

def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(path in {OUTPUT + ".inputs.json", OUTPUT + ".json",
                       OUTPUT + ".svg"}
              and type(raw) is bytes
              and 0 < len(raw) <= base.OWNER_LIMIT,
              "publish only three root-authorized complete V64 graph files")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0,
                      "publish every exact independently owned V64 byte")
            remaining = remaining[count:]
        os.fsync(handle)
        meta = os.fstat(handle)
        base.need(meta.st_uid == os.geteuid()
                  and meta.st_nlink == 1
                  and meta.st_size == len(raw)
                  and stat.S_IMODE(meta.st_mode) == 0o600,
                  "publish exactly one private complete V64 graph owner")
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
              "reauthenticate exactly one complete current V64 graph owner")



def repair_v17_authorization_outputs(base: types.ModuleType,
                                     pairs: tuple) -> None:
    expected_paths = {
        item[0] for item in STALE_V17_AUTHORIZATION_OUTPUTS.values()
    }
    actual_pairs = dict(pairs)
    base.need(
        len(actual_pairs) == 3 and set(actual_pairs) == expected_paths,
        "repair only three self-created stale V64 graph owners",
    )
    stale = {}
    for role, (path, fingerprint, size, inode) in (
            STALE_V17_AUTHORIZATION_OUTPUTS.items()):
        raw, owner = base.read_owner(path, fingerprint, size, private=True)
        base.need(
            owner["device"] == 2064
            and owner["inode"] == inode
            and owner["nlink"] == 1,
            "reject changed exact stale V64 owner: " + role,
        )
        if role in {"inputs", "summary"}:
            document = base.document(raw, "exact stale V64 " + role)
            base.need(
                document.get("rust_native_build_v17_authorization_status")
                    == "AUTHORIZED"
                and document.get("actual_current_graph_predecessor_version")
                    == 63
                and document.get("phase1_v4_oracle_readiness_status")
                    == "PASS",
                "repair only identified false historical V17 alias: " + role,
            )
            if role == "summary":
                base.need(
                    document.get("snapshot", {}).get(
                        "rust_native_build_v17_authorization_status")
                        == "AUTHORIZED"
                    and document.get("previous_overview", {}).get(
                        "source", {}).get("path") == V63["source"][0],
                    "repair only exact unchanged V63-parent readiness graph",
                )
        stale[path] = (fingerprint, size, inode)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory = os.open(str(ROOT / "docs/evidence"), flags)
    try:
        prepared = []
        create = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        create |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        for path, raw in pairs:
            old_hash, _, _ = stale[path]
            basename = Path(path).name
            temporary = (
                basename + ".blocked-v17-" + old_hash[:16] + ".tmp"
            )
            handle = os.open(temporary, create, 0o600, dir_fd=directory)
            try:
                remaining = memoryview(raw)
                while remaining:
                    count = os.write(handle, remaining)
                    base.need(
                        type(count) is int and count > 0,
                        "publish complete immutable-V17 recovery owner",
                    )
                    remaining = remaining[count:]
                os.fsync(handle)
                meta = os.fstat(handle)
                base.need(
                    meta.st_dev == 2064
                    and meta.st_uid == os.geteuid()
                    and meta.st_nlink == 1
                    and meta.st_size == len(raw)
                    and stat.S_IMODE(meta.st_mode) == 0o600,
                    "require exclusive private complete V17 recovery asset",
                )
            finally:
                os.close(handle)
            prepared.append((path, raw, basename, temporary))
        os.fsync(directory)
        for path, raw, basename, temporary in prepared:
            old_hash, old_size, old_inode = stale[path]
            _, owner = base.read_owner(
                path, old_hash, old_size, private=True,
            )
            base.need(
                owner["device"] == 2064
                and owner["inode"] == old_inode
                and owner["nlink"] == 1,
                "refuse atomic replacement of modified V64: " + path,
            )
            os.replace(
                temporary, basename,
                src_dir_fd=directory, dst_dir_fd=directory,
            )
            os.fsync(directory)
            confirmed, _ = base.read_owner(
                path, base.digest(raw), len(raw), private=True,
            )
            base.need(
                confirmed == raw,
                "bind only exact fixed V17 readiness output: " + path,
            )
    finally:
        os.close(directory)


def compact_result(base: types.ModuleType, snapshot: dict,
                   outputs: dict[str, bytes], source_sha: str,
                   *, written: bool, suffix: str) -> dict:
    fields = (
        "actual_current_graph_predecessor_version",
        "actual_rust_semantic_mismatch_count",
        "actual_rust_verified_passing_case_count",
        "rust_original_campaign_semantic_mismatch_count",
        "rust_original_campaign_verified_passing_case_count",
        "actual_rust_v7_semantic_mismatch_count",
        "actual_rust_v7_explicitly_verified_passing_case_count",
        "actual_rust_v10_candidate_status",
        "actual_rust_v10_semantic_mismatch_count",
        "actual_rust_v10_verified_passing_case_count",
        "actual_rust_v10_semantic_mismatch_regression_against_v7",
        "actual_rust_v10_candidate_workers",
        "actual_rust_v10_worker_process_ids",
        "actual_rust_v10_infrastructure_failure_count",
        "actual_rust_v10_all_four_original_targets_restored",
        "rust_buffer_shape_v2_feature_status",
        "rust_buffer_shape_v2_build_status",
        "rust_buffer_shape_v2_matching_status",
        "candidate_facing_self_oracle_status",
        "phase1_completeness_status",
        "phase1_corrected_crosswalk_status",
        "phase1_canonical_candidate_context_crosswalk",
        "phase1_v2_reconciliation",
        "phase1_v1_public_type_reference_status",
        "phase1_v2_corrected_reference_case_count",
        "phase1_v2_corrected_reference_process_ids",
        "phase1_v2_supplemental_fuzz_stream_status",
        "phase1_v2_supplemental_fuzz_unique_record_count",
        "phase1_v2_supplemental_independently_referenced_case_count",
        "phase1_v2_supplemental_dual_reference_status",
        "phase1_v2_supplemental_candidate_status",
        "phase1_v2_correctness_gate_blockers",
        "supplemental_differential_fuzz_candidate_gate",
        "supplemental_differential_fuzz_case_count",
        "phase1_differential_fuzz_reference_v3_source_status",
        "phase1_differential_fuzz_reference_v3_execution_status",
        "phase1_differential_fuzz_reference_v3_worker_count",
        "phase1_differential_fuzz_reference_v3_worker_process_ids",
        "phase1_differential_fuzz_reference_v3_reference_case_count",
        "phase1_differential_fuzz_reference_v3_candidate_case_count",
        "phase1_differential_fuzz_reference_v3_actual_worker_result_count",
        "phase1_differential_fuzz_reference_v3_actual_worker_exit_codes",
        "phase1_differential_fuzz_reference_v3_actual_worker_case_counts",
        "phase1_differential_fuzz_reference_v3_actual_worker_failure_counts",
        "phase1_differential_fuzz_reference_v3_actual_worker_owner_inodes",
        "phase1_differential_fuzz_reference_v3_actual_run_label",
        "phase1_v4_oracle_readiness_status",
        "phase1_v4_candidate_testing_authorized",
        "phase1_v4_candidate_qualification_status",
        "phase1_v4_candidate_qualification_blockers",
        "phase1_v4_candidate_qualification_blocker_count",
        "candidate_qualification_status",
        "candidate_qualification_blockers",
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
        "actually_tested_corrected_candidate_family_count",
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
        "version": 64,
        "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 63,
        **{"previous_overview_" + role + "_sha256": item[1]
           for role, item in V63.items()},
        **{"readiness_" + role + "_sha256": item[1]
           for role, item in READINESS.items()},
        **{key: copy.deepcopy(snapshot[key]) for key in fields},
        "outputs_written": written,
    }

def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--repair-v17-authorization", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    for role in V63:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in READINESS:
        parser.add_argument("--readiness-" + role + "-sha256")
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        modules = load_v63()
        base = modules[-1]
        if options.self_test:
            forbidden = ["source_sha256", "source_bytes"]
            forbidden.extend("previous_" + role + "_sha256"
                             for role in V63)
            forbidden.extend("readiness_" + role + "_sha256"
                             for role in READINESS)
            forbidden.extend(("inputs_sha256", "summary_sha256",
                              "svg_sha256"))
            base.need(
                all(getattr(options, name) is None for name in forbidden),
                "source-only V64 self-test never reads genuine owners",
            )
            sys.stdout.buffer.write(base.canonical(self_test(modules)))
            return 0
        snapshot, pairs = build(modules, options)
        outputs = dict(pairs)
        source_sha = base.checked(
            options.source_sha256, "exact root-authorized V64 renderer",
        )
        if options.render or options.repair_v17_authorization:
            base.need(
                options.inputs_sha256 is None
                and options.summary_sha256 is None
                and options.svg_sha256 is None,
                "publish only three root-authorized V64 graph assets",
            )
            if options.repair_v17_authorization:
                repair_v17_authorization_outputs(base, pairs)
            else:
                for path, raw in pairs:
                    publish(base, path, raw)
            result = compact_result(
                base, snapshot, outputs, source_sha,
                written=True, suffix="-published",
            )
        else:
            expected = {
                OUTPUT + ".inputs.json": base.checked(
                    options.inputs_sha256, "complete V64 graph inputs",
                ),
                OUTPUT + ".json": base.checked(
                    options.summary_sha256, "complete V64 graph summary",
                ),
                OUTPUT + ".svg": base.checked(
                    options.svg_sha256, "complete V64 graph chart",
                ),
            }
            for path, fingerprint in expected.items():
                raw, _ = base.read_owner(
                    path, fingerprint, len(outputs[path]), private=True,
                )
                base.need(
                    raw == outputs[path],
                    "reproduce complete source-only V64 owner: " + path,
                )
            result = compact_result(
                base, snapshot, outputs, source_sha,
                written=False, suffix="-read-only-frozen-context",
            )
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except (ValueError, OSError, TypeError, EOFError, KeyError,
            AttributeError, RecursionError, UnicodeError) as error:
        sys.stderr.write("current V64 overview rejected: "
                         + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V64 overview rejected: "
                             + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
