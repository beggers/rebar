#!/usr/bin/env python3
"""Freeze a reproducible first-party, one-pass Rust literal-findall build."""

from __future__ import annotations

import sys

if "re" in sys.modules or "_sre" in sys.modules:
    raise SystemExit("a first-party Rust source freeze cannot import a matcher")

import builtins
import hashlib
import os
import stat


ROOT = "/home/dev-user/src/rebar"
SCHEMA = "rebar-phase2-owned-rust-literal-findall-source-build-v20"
VERSION = 20
FAMILY = "rust"
SOURCE_PATH = "tools/reproduce_owned_rust_literal_findall_source_build_v20.py"
PROTOCOL_PATH = "oracle/phase2/RUST-LITERAL-FINDALL-SOURCE-BUILD-V20.md"
CONTRACT_PATH = "oracle/phase2/rust-literal-findall-source-build-v20.json"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
DEVICE = 2064
MAX_OWNER_BYTES = 4 * 1024 * 1024
GRAPH_VERSION = 86
EVIDENCE_FLOOR = 277
HISTORY_FLOOR = 282
PROPOSED_FINAL_HOLDOUT_CASE_COUNT = 14_155_776
PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT = 4_194_304
ROOT_PREFIX = "rebar-phase2-native-build-v9-rust-"
BUILD_LABEL = "phase2-v20-rust-literal-findall-root-provenance"
EVIDENCE_PATH = "oracle/phase2/evidence"
PHASES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "rustc_version", "cargo_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "engine_symbols", "bridge_dynamic", "bridge_symbols", "engine_sections",
    "engine_notes", "bridge_sections", "bridge_notes",
)
V19 = {
    "source": (
        "v19_source", "tools/reproduce_owned_rust_buffer_shape_source_build_v19.py",
        "650b33a10d253e09d48a423d12c8a1bb8180af4c4e96222aa13e72c75427bb5c",
        88532, DEVICE, 430955,
    ),
    "protocol": (
        "v19_protocol", "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V19.md",
        "4cdc322b2a516b28bf771440202efaca77074f7c8cd31c25692dc6ffc81797b5",
        5808, DEVICE, 524752,
    ),
    "contract": (
        "v19_contract", "oracle/phase2/rust-buffer-shape-source-build-v19.json",
        "78e31d32cd17e100613ea98cecec4051ca2f6563b0d3b198c66f69501171ac46",
        14975, DEVICE, 524753,
    ),
}
V19_BUILD_RECEIPT = (
    "v19_actual_build_receipt",
    "oracle/phase2/evidence/native-source-build-v19-rust-phase2-v19-rust-"
    "buffer-shape-root-provenance-publication-receipt.json",
    "27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc",
    3486, DEVICE, 524773,
)
V19_ROOT_RECEIPT = (
    "v19_actual_root_receipt",
    "oracle/phase2/evidence/native-source-build-v19-rust-phase2-v19-rust-"
    "buffer-shape-root-provenance-root-provenance-receipt.json",
    "de13207235055665c605cce1b88a8f2127f291b84a5954119a033c7f4e9a3c99",
    4367, DEVICE, 524774,
)
V19_ARCHIVE_METADATA = {
    "path": "oracle/phase2/evidence/native-source-build-v19-rust-phase2-v19-"
            "rust-buffer-shape-root-provenance.json.gz",
    "sha256": "c4e3971fc207af50081d920a98d29dc06b5bdce07c5e1fb19e3e6fdf99a1c1bb",
    "bytes": 108250,
}
GRAPH = {
    "source": (
        "v86_graph_source", "tools/render_candidate_current_overview_v86.py",
        "49c529c7f8b695c501dd03f9d35056c2853c73fcd36425718d8bfceb599b1a7d",
        75354, DEVICE, 431699,
    ),
    "inputs": (
        "v86_graph_inputs", "docs/evidence/candidate-current-overview-v86.inputs.json",
        "42c534652a350eada8704581ebf8aa52c77687b6904e9fb486f03c2f117cbe6c",
        1345744, DEVICE, 430944,
    ),
    "summary": (
        "v86_graph_summary", "docs/evidence/candidate-current-overview-v86.json",
        "ed728687e919410e6e9dae22ad3c976aa900d7a857f85231aaa93d0fc674f7cc",
        4128155, DEVICE, 431704,
    ),
    "svg": (
        "v86_graph_svg", "docs/evidence/candidate-current-overview-v86.svg",
        "4bbf196a48997dbee3ea6b966d9a4eefce860962861675ad202506f685a80e55",
        6214, DEVICE, 431705,
    ),
}
LITERAL_VARIANT = (
    "one_pass_literal_findall_variant",
    "candidates/rust/variants/buffer_shape_pickle_findall_v1/py_bridge.c",
    "b707e924a23980385b0c5b0306daecd55bbb03d6f2511437f0532b6d39b2a112",
    178950, DEVICE, 525253,
)
LITERAL_FEATURE = {
    "source": (
        "literal_findall_feature_source",
        "tools/verify_owned_rust_literal_findall_source_v1.py",
        "21fb0878e344ead0bba49f932120a35a897ca44cfd7710287861ebc6415c555e",
        33883, DEVICE, 429583,
    ),
    "protocol": (
        "literal_findall_feature_protocol",
        "oracle/phase2/RUST-LITERAL-FINDALL-ONE-PASS-V1.md",
        "842d51127db54a26d0dd9f874f38834f122f7888ea71c6f3fe77b8911bbd65d6",
        4515, DEVICE, 525256,
    ),
    "contract": (
        "literal_findall_feature_contract",
        "oracle/phase2/rust-literal-findall-one-pass-v1.json",
        "a2226d823610a578aeb65e9a51a2a33517348b6c51130ad89db840cc50833164",
        3167, DEVICE, 525262,
    ),
}
EXPANDED_HOLDOUT_PROPOSAL = {
    "source": (
        "expanded_sealed_holdout_proposal_source",
        "tools/verify_expanded_sealed_holdout_v1.py",
        "3dd9abcbd7a87486186ee8da804de595e65d79020a3fe33413d0157dde4f3309",
        27311, DEVICE, 428806,
    ),
    "protocol": (
        "expanded_sealed_holdout_proposal_protocol",
        "oracle/phase3/EXPANDED-SEALED-HOLDOUT-V1.md",
        "818f1636d87ae721912f04a3fc8294ac04a59dff4a272319aa29a393f52a4fd4",
        13237, DEVICE, 524760,
    ),
    "contract": (
        "expanded_sealed_holdout_proposal_contract",
        "oracle/phase3/expanded-sealed-holdout-v1.json",
        "676aac4f48c9404f5253c89b692efde5c425170f8d9f152b4f85b3e2a5225a76",
        6628, DEVICE, 524761,
    ),
}
PROPOSAL_OPERATIONS = (
    "fresh_compile_search", "warm_cached_compile_search", "module_search",
    "pattern_search", "module_match", "pattern_match", "module_fullmatch",
    "pattern_fullmatch", "module_findall", "pattern_findall", "module_finditer",
    "pattern_finditer", "module_split_keyword", "pattern_split_keyword",
    "module_split_positional", "pattern_split_positional", "module_sub_literal",
    "pattern_sub_literal", "module_sub_callable", "pattern_sub_callable",
    "module_subn_literal", "pattern_subn_literal", "module_subn_callable",
    "pattern_subn_callable", "module_sub_positional", "pattern_sub_positional",
    "module_subn_positional", "pattern_subn_positional", "scanner_search",
    "scanner_match", "scanner_repeated_search", "scanner_repeated_match",
    "lexicon_scan", "lexicon_scan_callback", "match_groups", "match_expand",
)
PROPOSAL_PATTERN_FAMILIES = (
    "single_literal", "multiple_character_literal", "anchored_literal_prefix",
    "disjoint_alternation", "overlapping_alternation", "greedy_unbounded_repeat",
    "lazy_unbounded_repeat", "bounded_repeat", "possessive_repeat",
    "atomic_group", "positive_character_class", "negative_character_class",
    "predefined_categories_and_type_valid_flags", "start_anchor", "end_anchor",
    "word_boundary", "numbered_capture", "named_capture",
    "numbered_backreference", "named_backreference", "positive_lookahead",
    "negative_lookahead", "fixed_width_positive_or_negative_lookbehind",
    "conditionals_or_correctly_advancing_zero_length_matches",
)
PROPOSAL_SUBJECT_TYPES = ("str", "bytes", "bytearray", "memoryview")
PROPOSAL_LIFECYCLE_SLOTS = (
    "operation_valid_fresh_work", "operation_valid_warm_cache",
    "operation_valid_compiled_reuse", "operation_valid_existing_state",
)
PROPOSAL_PROHIBITED_DELEGATES = (
    "stdlib_re", "stdlib__sre", "PCRE", "PCRE2", "RE2", "Rust_regex",
    "Oniguruma", "Hyperscan", "Boost_regex", "std_regex", "POSIX_regex",
    "ICU_regex", "Tcl_regex", "JavaScript_regex", "WebAssembly_regex",
    "another_candidate", "dynamic_matcher_plugin", "external_process_matcher",
    "network_matcher", "cached_oracle_answers", "hidden_fallback",
)
PROPOSAL_PUBLIC_OWNERS = (
    ("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"),
    ("docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md",
     "f7509c60065860d30aad7939dda76f53e1c9f6ebb9db5e1298d0881f63a016eb"),
    ("oracle/phase1/P0-COMPLETENESS-V4.md",
     "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2"),
    ("oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md",
     "1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8"),
    ("oracle/phase1/P0-PUBLIC-ENTRYPOINT-IMPORT-V1.md",
     "01ace52c6285142733bdcb2b4556feb43226e01c8b181b84019b8fa8c42697c0"),
    ("oracle/phase1/P0-LARGE-INPUT-INDEXING-V1.md",
     "0a640ee044c52394fa897d0221d51dfc3d85e9abb95608367698f11fba8ca879"),
    ("oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md",
     "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4"),
    ("oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md",
     "80a1de729c067da36648dcfb9751f7bd3833ff561956df9ad82fc6106a19a16b"),
    ("oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md",
     "2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c"),
)
QUALIFICATION_BLOCKERS = (
    "ORIGINAL_31237_CANDIDATE_GATE_NOT_PASSED",
    "SUPPLEMENTAL_8244_CANDIDATE_GATE_NOT_RUN",
    "PUBLIC_IMPORT_FAIL",
    "PUBLIC_CALLABLE_SIGNATURE_CANDIDATE_GATE_NOT_RUN",
    "FULL_SIZE_2GIB_CANDIDATE_SEARCH_NOT_RUN",
    "FULL_SIZE_2GIB_CANDIDATE_SUBSTITUTION_NOT_RUN",
    "RUNTIME_NO_DELEGATION_NOT_ESTABLISHED",
)
_ROOT_CAPTURE: dict[str, object] | None = None


class GateError(Exception):
    """Reject stale first-party evidence or an unearned actual-build effect."""


def require(value: object, reason: str) -> None:
    if value is not True:
        raise GateError(reason)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only bounded first-party source bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_hash(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require an exact lowercase SHA-256: " + label)
    return value


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.realpath(sys.executable) == PYTHON
            and os.path.abspath(__file__) == ROOT + "/" + SOURCE_PATH
            and os.path.realpath(__file__) == ROOT + "/" + SOURCE_PATH
            and "re" not in sys.modules and "_sre" not in sys.modules
            and "regex" not in sys.modules
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "require isolated CPython 3.14.6 without a regex engine or candidate")


def bootstrap_v19() -> dict[str, object]:
    row = V19["source"]
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(ROOT + "/" + row[1], flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_uid == os.geteuid()
                and before.st_nlink == 1
                and (before.st_dev, before.st_ino, before.st_size)
                    == (row[4], row[5], row[3]),
                "bootstrap only the exact independently frozen V19 source")
        chunks: list[bytes] = []
        remaining = row[3]
        while remaining:
            part = os.read(descriptor, min(remaining, 262144))
            require(type(part) is bytes and bool(part),
                    "reject truncated first-party V19 source")
            chunks.append(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"",
                "reject extra first-party V19 source bytes")
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
                "reject V19 source changed during authenticated bootstrap")
    finally:
        os.close(descriptor)
    raw = b"".join(chunks)
    require(digest(raw) == row[2], "reject an unauthenticated V19 build controller")
    namespace: dict[str, object] = {
        "__name__": "_rebar_exact_v20_first_party_v19_source",
        "__file__": ROOT + "/" + row[1],
        "__package__": None,
    }
    exec(compile(raw, namespace["__file__"], "exec", dont_inherit=True), namespace)
    require(namespace.get("SCHEMA")
                == "rebar-phase2-owned-rust-buffer-shape-source-build-v19"
            and namespace.get("VERSION") == 19
            and namespace.get("FAMILY") == FAMILY
            and namespace.get("PYTHON") == PYTHON
            and namespace.get("PYTHON_SHA256") == PYTHON_SHA256
            and namespace.get("ROOT_PREFIX") == ROOT_PREFIX
            and tuple(namespace.get("PHASES", ())) == PHASES
            and tuple(namespace.get("PROCESS_NAMES", ())) == PROCESS_NAMES
            and namespace.get("SOURCE_PATH") == V19["source"][1]
            and namespace.get("PROTOCOL_PATH") == V19["protocol"][1]
            and namespace.get("CONTRACT_PATH") == V19["contract"][1]
            and "re" not in sys.modules and "_sre" not in sys.modules,
            "derive only the exact independently proven first-party V19 kernel")
    return namespace


def load_base(v19: dict[str, object]) -> dict[str, object]:
    base = v19["load_v18"]()
    require(type(base) is dict
            and base.get("SCHEMA")
                == "rebar-phase2-owned-rust-buffer-shape-source-build-v18"
            and base.get("VERSION") == 18
            and base.get("FAMILY") == FAMILY
            and base.get("PYTHON") == PYTHON
            and base.get("PYTHON_SHA256") == PYTHON_SHA256
            and base.get("V2_BRIDGE_SHA256")
                == "afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740"
            and base.get("V2_BRIDGE_BYTES") == 179961
            and base.get("CORRECTED_ADAPTER_SHA256")
                == "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
            and base.get("CORRECTED_ADAPTER_BYTES") == 31934
            and tuple(base.get("RUST_SOURCE_NAMES", ()))
                == ("cargo_lock", "cargo_manifest", "original_bridge", "rust_engine",
                    "rust_newline", "rust_search", "rust_stack", "rust_unicode",
                    "original_adapter"),
            "retain exactly nine original Rust sources and the audited V2 predecessor")
    additions = {
        ROOT + "/" + SOURCE_PATH,
        ROOT + "/" + PROTOCOL_PATH,
        ROOT + "/" + CONTRACT_PATH,
        ROOT + "/" + LITERAL_VARIANT[1],
        ROOT + "/" + V19_BUILD_RECEIPT[1],
        ROOT + "/" + V19_ROOT_RECEIPT[1],
    }
    additions.update(ROOT + "/" + row[1] for row in GRAPH.values())
    additions.update(ROOT + "/" + row[1] for row in V19.values())
    additions.update(ROOT + "/" + row[1] for row in LITERAL_FEATURE.values())
    additions.update(ROOT + "/" + row[1]
                     for row in EXPANDED_HOLDOUT_PROPOSAL.values())
    base["_ALLOWLIST"] = frozenset(set(base["_ALLOWLIST"]) | additions)
    return base


def canonical(base: dict[str, object], value: object) -> bytes:
    return (base["canonical"](value) + "\n").encode("ascii")


def document(base: dict[str, object], raw: bytes, label: str) -> dict[str, object]:
    value = base["StrictJSON"](raw).decode()
    require(type(value) is dict and canonical(base, value) == raw,
            "reject repeated keys, invalid JSON, or a noncanonical owner: " + label)
    return value


def row_document(row: tuple[object, ...]) -> dict[str, object]:
    return {"path": row[1], "sha256": row[2], "bytes": row[3],
            "device": row[4], "inode": row[5], "mode": "0600", "nlink": 1}


def public_document(row: tuple[object, ...]) -> dict[str, object]:
    return {"path": row[1], "sha256": row[2], "bytes": row[3]}


def row_group(rows: dict[str, tuple[object, ...]]) -> dict[str, dict[str, object]]:
    return {name: row_document(row) for name, row in sorted(rows.items())}


def boundary() -> dict[str, object]:
    return {
        "actual_candidate_workers": 0,
        "actual_compiler_process_count": 0,
        "actual_reference_workers": 0,
        "actual_root_descriptor_opens": 0,
        "archive_bytes_read": 0,
        "archive_inflations": 0,
        "archive_opens": 0,
        "benchmark_files_read": 0,
        "candidate_build": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_imports": 0,
        "candidate_matching": "NOT RUN",
        "candidate_processes_started": 0,
        "candidate_qualified": False,
        "canonical_source_mutations": 0,
        "clock_samples": 0,
        "compiler_processes_started": 0,
        "confidence_intervals": "NOT MEASURED",
        "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
        "expanded_holdout_generator_status": "NOT FROZEN",
        "expanded_holdout_proposal_case_count": PROPOSED_FINAL_HOLDOUT_CASE_COUNT,
        "expanded_holdout_proposal_status": "PRE-PHASE-3 PROPOSAL",
        "expanded_holdout_protocol_status": "NOT FROZEN",
        "expanded_holdout_secret_status": "NOT GENERATED",
        "hidden_cases_read": 0,
        "holdout": "NOT OPENED",
        "literal_findall_practice_cases": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "native_activations": 0,
        "native_libraries_loaded": 0,
        "network_requests": 0,
        "performance": "NOT MEASURED",
        "previous_holdout_proposal_case_count":
            PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT,
        "private_root_path": "NOT MEASURED",
        "private_roots_created": 0,
        "qualified_candidate_count": 0,
        "root_provenance": "NOT MEASURED",
        "root_provenance_receipts_written": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "threads_started": 0,
        "timing_trials_run": 0,
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def validate_graph(summary: dict[str, object],
                   inputs: dict[str, object]) -> dict[str, object]:
    require(summary.get("schema") == "rebar-candidate-current-overview-v86-summary"
            and summary.get("version") == GRAPH_VERSION
            and summary.get("status") == "PASS"
            and inputs.get("schema") == "rebar-candidate-current-overview-v86-inputs"
            and inputs.get("version") == GRAPH_VERSION
            and summary.get("source") == public_document(GRAPH["source"])
            and summary.get("inputs") == public_document(GRAPH["inputs"])
            and summary.get("svg") == public_document(GRAPH["svg"]),
            "authenticate all four exact published current V86 graph owners")
    for observed in (summary, inputs):
        require(observed.get("actual_current_graph_predecessor_version") == 85
                and observed.get("authenticated_evidence_owner_lower_bound")
                    == EVIDENCE_FLOOR
                and observed.get("authenticated_history_reference_lower_bound")
                    == HISTORY_FLOOR
                and observed.get("full_case_denominator") == 31237
                and observed.get("suite_count") == 13
                and observed.get("private_waiver_count") == 13
                and observed.get("phase1_v4_oracle_readiness_status") == "PASS"
                and observed.get("candidate_qualification_status") == "BLOCKED"
                and observed.get("qualified_candidate_count") == 0
                and observed.get("candidate_qualification_blockers")
                    == list(QUALIFICATION_BLOCKERS)
                and observed.get("actual_rust_v10_candidate_status") == "FAIL"
                and observed.get("actual_rust_semantic_mismatch_count") == 1440
                and observed.get("actual_rust_verified_passing_case_count") == 14853
                and observed.get("actual_rust_candidate_workers") == 13
                and observed.get("rust_v15_original_campaign_attempted_suite_count")
                    == 13
                and observed.get("rust_v15_original_campaign_started_suite_count")
                    == 13
                and observed.get("rust_v15_original_campaign_completed_suite_count")
                    == 8
                and observed.get("rust_v15_original_campaign_verified_passing_case_count")
                    == 12942
                and observed.get("rust_v15_original_campaign_semantic_mismatch_count")
                    == "NOT MEASURED"
                and observed.get("rust_v15_original_campaign_infrastructure_failure_count")
                    == 5
                and observed.get("rust_v15_original_campaign_candidate_matching")
                    == "FAIL"
                and observed.get("rust_v15_original_campaign_candidate_qualified")
                    is False
                and observed.get("rust_v15_original_campaign_worker_failure_capture_complete")
                    is True
                and observed.get("rust_v15_original_campaign_worker_failure_capture_attempts")
                    == 5
                and observed.get("rust_v15_original_campaign_runtime_no_delegation")
                    == "NOT ESTABLISHED"
                and observed.get("actual_c_semantic_mismatch_count") == 1230
                and observed.get("actual_c_verified_passing_case_count") == 7325
                and observed.get("actual_zig_semantic_mismatch_count") == 1764
                and observed.get("rust_native_build_v19_status") == "PASS"
                and observed.get("rust_native_build_v19_compiler_process_count") == 28
                and observed.get("rust_native_build_v19_matching_status") == "NOT RUN"
                and observed.get("rust_native_build_v19_private_root_provenance")
                    == "PASS"
                and observed.get("rust_native_build_v19_candidate_correctness")
                    == "NOT MEASURED"
                and observed.get("rust_native_build_v19_candidate_qualified") is False
                and observed.get("rust_native_build_v19_archive_opened_by_graph")
                    is False
                and observed.get("final_holdout_opened") is False
                and observed.get("runtime_no_delegation") == "NOT ESTABLISHED"
                and observed.get("performance") == "NOT MEASURED"
                and observed.get("memory") == "NOT MEASURED"
                and observed.get("timing_trials_run") == 0
                and observed.get("winner_selected") is False,
                "preserve every genuine current Rust result and unopened holdout")
    return {
        "version": GRAPH_VERSION,
        "owner_count": 4,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "historical_complete_rust_semantic_mismatch_count": 1440,
        "historical_complete_rust_verified_passing_case_count": 14853,
        "latest_rust_attempted_suite_count": 13,
        "latest_rust_completed_suite_count": 8,
        "latest_rust_verified_passing_case_count": 12942,
        "latest_rust_worker_failure_count": 5,
        "latest_rust_semantic_mismatch_count": "NOT MEASURED",
        "current_c_semantic_mismatch_count": 1230,
        "current_zig_semantic_mismatch_count": 1764,
        "qualified_candidate_count": 0,
        "holdout": "NOT OPENED",
    }


def validate_previous_receipts(build: dict[str, object],
                               root: dict[str, object]) -> dict[str, object]:
    archive = build.get("archive_publication")
    require(build.get("schema")
                == "rebar-phase2-owned-rust-buffer-shape-source-build-v19-"
                   "durable-publication-receipt"
            and build.get("status") == "PASS"
            and build.get("build_status") == "PASS"
            and build.get("family") == FAMILY
            and build.get("label") == "phase2-v19-rust-buffer-shape-root-provenance"
            and build.get("source_sha256") == V19["source"][2]
            and build.get("protocol_sha256") == V19["protocol"][2]
            and build.get("contract_sha256") == V19["contract"][2]
            and build.get("actual_compiler_process_count") == 28
            and build.get("expected_actual_compiler_process_count") == 28
            and build.get("combined_bridge_sha256")
                == "afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740"
            and build.get("combined_bridge_bytes") == 179961
            and build.get("combined_bridge_overlay_apply_count") == 2
            and build.get("corrected_public_adapter_sha256")
                == "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
            and build.get("corrected_public_adapter_bytes") == 31934
            and build.get("corrected_public_adapter_overlay_apply_count") == 2
            and build.get("archive_relative") == V19_ARCHIVE_METADATA["path"]
            and build.get("archive_sha256") == V19_ARCHIVE_METADATA["sha256"]
            and build.get("archive_bytes") == V19_ARCHIVE_METADATA["bytes"]
            and type(archive) is dict
            and archive.get("sha256") == V19_ARCHIVE_METADATA["sha256"]
            and archive.get("bytes") == V19_ARCHIVE_METADATA["bytes"]
            and archive.get("device") == DEVICE
            and archive.get("inode") == 524772
            and archive.get("exclusive_creation") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("same_inode_readback_verified") is True
            and build.get("candidate_matching") == "NOT RUN"
            and build.get("candidate_qualified") is False
            and build.get("candidate_workers_started") == 0
            and build.get("native_libraries_loaded") == 0
            and build.get("hidden_cases_read") == 0
            and build.get("clock_samples") == 0
            and build.get("performance") == "NOT MEASURED"
            and build.get("holdout") == "NOT OPENED",
            "authenticate the actual complete V19 build without opening its archive")
    previous_root = root.get("root")
    require(root.get("schema")
                == "rebar-phase2-owned-rust-buffer-shape-source-build-v19-"
                   "durable-root-provenance-receipt"
            and root.get("status") == "PASS"
            and root.get("family") == FAMILY
            and root.get("label") == build["label"]
            and root.get("source_sha256") == V19["source"][2]
            and root.get("protocol_sha256") == V19["protocol"][2]
            and root.get("contract_sha256") == V19["contract"][2]
            and root.get("canonical_build_status") == "PASS"
            and root.get("canonical_build_archive_relative")
                == V19_ARCHIVE_METADATA["path"]
            and root.get("canonical_build_archive_sha256")
                == V19_ARCHIVE_METADATA["sha256"]
            and root.get("canonical_build_archive_bytes")
                == V19_ARCHIVE_METADATA["bytes"]
            and root.get("canonical_build_archive_opened") is False
            and root.get("canonical_build_receipt_relative") == V19_BUILD_RECEIPT[1]
            and root.get("canonical_build_receipt_sha256") == V19_BUILD_RECEIPT[2]
            and root.get("canonical_build_receipt_bytes") == V19_BUILD_RECEIPT[3]
            and root.get("actual_compiler_process_count") == 28
            and root.get("expected_compiler_process_count") == 28
            and root.get("actual_source_phase_count") == 2
            and root.get("bridge_overlay_apply_count") == 2
            and root.get("adapter_overlay_apply_count") == 2
            and root.get("candidate_correctness") == "NOT MEASURED"
            and root.get("candidate_matching") == "NOT RUN"
            and root.get("candidate_qualified") is False
            and root.get("candidate_workers_started") == 0
            and root.get("native_libraries_loaded") == 0
            and root.get("tmp_directory_scanned") is False
            and root.get("historical_archives_opened") == 0
            and root.get("hidden_cases_read") == 0
            and root.get("clock_samples") == 0
            and root.get("performance") == "NOT MEASURED"
            and root.get("holdout") == "NOT OPENED"
            and type(previous_root) is dict
            and type(previous_root.get("path")) is str
            and previous_root["path"].startswith("/tmp/" + ROOT_PREFIX)
            and previous_root.get("prefix") == ROOT_PREFIX
            and previous_root.get("mode") == "0700"
            and previous_root.get("uid") == os.geteuid()
            and previous_root.get("phase_count") == 2
            and previous_root.get("directory_scanned") is False
            and previous_root.get("nofollow_directory_descriptor") is True
            and previous_root.get("descriptor_opened_during_live_verification") is True,
            "authenticate actual historical V19 root evidence without accessing its root")
    phases = previous_root.get("phases")
    require(type(phases) is list and len(phases) == 2,
            "preserve both actually proven historical V19 source phases")
    artifact_identities: set[tuple[int, int]] = set()
    role_hashes: dict[str, str] = {}
    for index, phase in enumerate(phases):
        require(type(phase) is dict
                and phase.get("name") == PHASES[index]
                and phase.get("absolute_path")
                    == previous_root["path"] + "/" + PHASES[index]
                and phase.get("mode") == "0700"
                and phase.get("uid") == os.geteuid(),
                "reject a borrowed historical V19 source phase")
        outputs = phase.get("native_outputs")
        require(type(outputs) is list and len(outputs) == 2,
                "require both real historical engine and bridge artifact roles")
        for role_index, (role, file_name) in enumerate((
            ("engine", "_rust_engine.so"),
            ("bridge", "_rust_bridge.cpython-314-x86_64-linux-gnu.so"),
        )):
            item = outputs[role_index]
            require(type(item) is dict
                    and item.get("role") == role
                    and item.get("file_name") == file_name
                    and item.get("absolute_path")
                        == phase["absolute_path"] + "/native/" + file_name
                    and type(item.get("sha256")) is str
                    and len(item["sha256"]) == 64
                    and type(item.get("bytes")) is int and item["bytes"] > 0
                    and type(item.get("device")) is int
                    and type(item.get("inode")) is int
                    and item.get("uid") == os.geteuid()
                    and item.get("nlink") == 1
                    and item.get("native_loaded") is False
                    and item.get("hash_provenance")
                        == "COMPLETE ORIGINAL FIRST-PARTY ELF VERIFICATION",
                    "preserve receipt-attested, never-reopened historical native artifacts")
            identity = (item["device"], item["inode"])
            require(identity not in artifact_identities,
                    "reject duplicated historical native artifact ownership")
            artifact_identities.add(identity)
            if role in role_hashes:
                require(role_hashes[role] == item["sha256"],
                        "preserve actual historical two-phase native byte identity")
            else:
                role_hashes[role] = item["sha256"]
    require(len(artifact_identities) == 4 and len(role_hashes) == 2,
            "preserve all four separately owned historical native artifacts")
    return {
        "actual_previous_build_status": "PASS",
        "actual_previous_root_provenance_status": "PASS",
        "actual_previous_compiler_process_count": 28,
        "actual_previous_source_phase_count": 2,
        "receipt_attested_previous_native_artifact_count": 4,
        "previous_archive_opened": False,
        "previous_private_root_opened": False,
        "previous_private_root_scanned": False,
    }


def validate_one_pass_variant(base: dict[str, object],
                              v18_state: dict[str, object]) -> dict[str, object]:
    previous = v18_state.get("combined_bridge")
    require(type(previous) is bytes
            and len(previous) == base["V2_BRIDGE_BYTES"]
            and digest(previous) == base["V2_BRIDGE_SHA256"],
            "authenticate the full unchanged first-party buffer-shape V2 predecessor")
    previous_owner = base["read_exact"](base["OWNER_BY_NAME"]["v2_variant"])
    require(previous == previous_owner,
            "require the derived predecessor to equal its complete owned V2 file")
    literal = base["read_exact"](LITERAL_VARIANT)
    return validate_one_pass_bytes(base, previous, literal)


def validate_expanded_holdout_proposal(
    proposal: dict[str, object], verifier: bytes, protocol: bytes,
) -> dict[str, object]:
    expected_scalars: dict[str, object] = {
        "baseline_participant_count": 1,
        "bootstrap_replicate_count": 9999,
        "bootstrap_stratum_draws_per_candidate": 138226176,
        "boundary_case_count": 55296,
        "boundary_cases_per_stratum": 4,
        "boundary_observation_count": 221184,
        "candidate_baseline_paired_observation_count": 1019215872,
        "candidate_participant_count": 3,
        "case_count": PROPOSED_FINAL_HOLDOUT_CASE_COUNT,
        "case_status": "NOT GENERATED; NOT OPENED",
        "cases_per_operation": 393216,
        "cases_per_pattern_family": 589824,
        "cases_per_stratum": 1024,
        "cases_per_subject_type": 3538944,
        "clock_bytes_per_timed_observation": 8,
        "false_discovery_rate_denominator": 100,
        "false_discovery_rate_numerator": 5,
        "final_protocol_status": "NOT FROZEN",
        "generator_status": "NOT FROZEN",
        "individually_correctness_gated_timed_observation_count": 1358954496,
        "lifecycle_count": 4,
        "memory_case_count": 221184,
        "memory_cases_per_stratum": 16,
        "memory_observation_count": 884736,
        "memory_status": "NOT RUN; NOT MEASURED",
        "minimum_faster_case_denominator": 100,
        "minimum_faster_case_numerator": 60,
        "minimum_lower_confidence_speedup_denominator": 2,
        "minimum_lower_confidence_speedup_numerator": 3,
        "minimum_qualified_independent_family_count": 3,
        "minimum_significantly_faster_case_count": 8493466,
        "multiple_comparison_hypothesis_count": 42467328,
        "named_private_waiver_count": 13,
        "operation_count": 36,
        "operation_family_shard_count": 864,
        "original_p0_case_count": 31237,
        "original_p0_suite_count": 13,
        "paired_round_count": 24,
        "participant_count": 4,
        "participant_occurrences_per_order_position": 6,
        "participant_orders_per_case": 24,
        "pattern_family_count": 24,
        "pinned_python_path": PYTHON,
        "pinned_python_sha256": PYTHON_SHA256,
        "pinned_python_version": "3.14.6",
        "preflight_correctness_observation_count": 56623104,
        "preserved_previous_proposal_case_count":
            PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT,
        "proposal_status": "PRE-PHASE-3 PROPOSAL",
        "qualified_independent_family_count": 0,
        "raw_clock_bytes_only": 10871635968,
        "raw_clock_bytes_per_operation_family_shard": 12582912,
        "raw_clock_gib_denominator": 8,
        "raw_clock_gib_numerator": 81,
        "readonly_memoryview_variants_per_memoryview_stratum": 512,
        "regression_explanation_threshold_percent": 20,
        "runtime_independence_status": "NOT ESTABLISHED",
        "schema": "rebar-expanded-sealed-holdout-pre-phase3-proposal-v1",
        "secret_status": "NOT GENERATED",
        "separate_differential_case_count": 8244,
        "stratum_count": 13824,
        "subject_type_count": 4,
        "timed_case_count": PROPOSED_FINAL_HOLDOUT_CASE_COUNT,
        "timing_status": "NOT RUN; NOT MEASURED",
        "winner_status": "NOT SELECTED",
        "writable_memoryview_variants_per_memoryview_stratum": 512,
    }
    axes = {
        "operations": PROPOSAL_OPERATIONS,
        "primary_pattern_families": PROPOSAL_PATTERN_FAMILIES,
        "subject_types": PROPOSAL_SUBJECT_TYPES,
        "lifecycle_slots": PROPOSAL_LIFECYCLE_SLOTS,
        "prohibited_matcher_delegates": PROPOSAL_PROHIBITED_DELEGATES,
    }
    require(type(proposal) is dict and len(proposal) == 71
            and set(proposal) == set(expected_scalars) | set(axes)
                | {"required_public_owners"},
            "require exactly 71 complete public expanded-proposal fields")
    for key, expected in expected_scalars.items():
        observed = proposal.get(key)
        require(type(observed) is type(expected) and observed == expected,
                "reject an invented measurement or altered expanded proposal: " + key)
    for key, expected in axes.items():
        observed = proposal.get(key)
        require(type(observed) is list and tuple(observed) == expected
                and len(observed) == len(set(observed)),
                "reject missing, repeated, or reordered proposal axis: " + key)
    owners = proposal.get("required_public_owners")
    require(type(owners) is list and len(owners) == len(PROPOSAL_PUBLIC_OWNERS),
            "preserve exactly nine published historical source-only proposal owners")
    for index, expected in enumerate(PROPOSAL_PUBLIC_OWNERS):
        owner = owners[index]
        require(type(owner) is dict and set(owner) == {"path", "sha256"}
                and owner.get("path") == expected[0]
                and owner.get("sha256") == expected[1],
                "reject reordered or substituted public expanded-proposal owners")
    strata = (len(PROPOSAL_OPERATIONS) * len(PROPOSAL_PATTERN_FAMILIES)
              * len(PROPOSAL_SUBJECT_TYPES) * len(PROPOSAL_LIFECYCLE_SLOTS))
    cases = strata * proposal["cases_per_stratum"]
    participants = proposal["baseline_participant_count"] \
        + proposal["candidate_participant_count"]
    rounds = proposal["paired_round_count"]
    faster = (cases * proposal["minimum_faster_case_numerator"]
              + proposal["minimum_faster_case_denominator"] - 1) \
        // proposal["minimum_faster_case_denominator"]
    require(strata == proposal["stratum_count"]
            and cases == proposal["case_count"] == proposal["timed_case_count"]
            and cases * 8
                == proposal["preserved_previous_proposal_case_count"] * 27
            and cases == len(PROPOSAL_OPERATIONS) * proposal["cases_per_operation"]
            and cases == len(PROPOSAL_PATTERN_FAMILIES)
                * proposal["cases_per_pattern_family"]
            and cases == len(PROPOSAL_SUBJECT_TYPES)
                * proposal["cases_per_subject_type"]
            and participants == proposal["participant_count"] == 4
            and rounds == proposal["participant_orders_per_case"] == 24
            and rounds == participants
                * proposal["participant_occurrences_per_order_position"]
            and cases * participants
                == proposal["preflight_correctness_observation_count"]
            and cases * rounds * participants
                == proposal["individually_correctness_gated_timed_observation_count"]
            and cases * rounds * proposal["candidate_participant_count"]
                == proposal["candidate_baseline_paired_observation_count"]
            and proposal["raw_clock_bytes_only"]
                == proposal["individually_correctness_gated_timed_observation_count"]
                    * proposal["clock_bytes_per_timed_observation"]
            and proposal["memory_case_count"]
                == strata * proposal["memory_cases_per_stratum"]
            and proposal["boundary_case_count"]
                == strata * proposal["boundary_cases_per_stratum"]
            and proposal["minimum_significantly_faster_case_count"] == faster
            and proposal["multiple_comparison_hypothesis_count"]
                == cases * proposal["candidate_participant_count"]
            and proposal["readonly_memoryview_variants_per_memoryview_stratum"]
                + proposal["writable_memoryview_variants_per_memoryview_stratum"]
                == proposal["cases_per_stratum"],
            "verify only balanced proposal arithmetic, never generated case data")
    require(type(verifier) is bytes
            and len(verifier) == EXPANDED_HOLDOUT_PROPOSAL["source"][3]
            and digest(verifier) == EXPANDED_HOLDOUT_PROPOSAL["source"][2]
            and b'SCHEMA = "rebar-expanded-sealed-holdout-pre-phase3-proposal-v1"'
                in verifier
            and b"class ReadOnlyProposalGuard" in verifier
            and b"def validate_contract(" in verifier
            and type(protocol) is bytes
            and len(protocol) == EXPANDED_HOLDOUT_PROPOSAL["protocol"][3]
            and digest(protocol) == EXPANDED_HOLDOUT_PROPOSAL["protocol"][2],
            "authenticate the bounded public proposal verifier without executing it")
    for token in (
        b"PRE-PHASE-3 PROPOSAL", b"NOT FROZEN", b"NOT GENERATED",
        b"NOT OPENED", b"NOT RUN", b"NOT MEASURED", b"14,155,776",
        b"4,194,304", b"three independently authored engine families",
    ):
        require(token in protocol,
                "preserve complete public proposed status: " + token.decode("ascii"))
    return {
        "status": "PASS",
        "status_scope": "BOUNDED PUBLIC PROPOSAL SOURCE AUTHENTICATION ONLY",
        "source_owner_count": 3,
        "source_sha256": EXPANDED_HOLDOUT_PROPOSAL["source"][2],
        "protocol_sha256": EXPANDED_HOLDOUT_PROPOSAL["protocol"][2],
        "contract_sha256": EXPANDED_HOLDOUT_PROPOSAL["contract"][2],
        "proposal_status": "PRE-PHASE-3 PROPOSAL",
        "final_protocol_status": "NOT FROZEN",
        "generator_status": "NOT FROZEN",
        "secret_status": "NOT GENERATED",
        "case_status": "NOT GENERATED; NOT OPENED",
        "case_count": PROPOSED_FINAL_HOLDOUT_CASE_COUNT,
        "timed_case_count": PROPOSED_FINAL_HOLDOUT_CASE_COUNT,
        "preserved_previous_proposal_case_count":
            PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT,
        "source_field_count": 71,
        "stratum_count": strata,
        "operation_count": len(PROPOSAL_OPERATIONS),
        "pattern_family_count": len(PROPOSAL_PATTERN_FAMILIES),
        "subject_type_count": len(PROPOSAL_SUBJECT_TYPES),
        "lifecycle_count": len(PROPOSAL_LIFECYCLE_SLOTS),
        "cases_per_stratum": 1024,
        "qualified_independent_family_count": 0,
        "minimum_qualified_independent_family_count": 3,
        "timing_status": "NOT RUN; NOT MEASURED",
        "memory_status": "NOT RUN; NOT MEASURED",
        "runtime_independence_status": "NOT ESTABLISHED",
        "winner_status": "NOT SELECTED",
        "proposal_verifier_executed": False,
        "proposal_cases_generated": 0,
        "proposal_cases_opened": 0,
        "proposal_generator_run": False,
        "clock_samples": 0,
        "holdout": "NOT OPENED",
    }


def validate_literal_feature(contract: dict[str, object]) -> dict[str, object]:
    feature = contract.get("candidate_variant")
    predecessor = contract.get("predecessor")
    references = contract.get("frozen_python_reference")
    pilot = contract.get("historical_practice_pilot")
    effects = contract.get("phase_boundary")
    required = contract.get("required_future_gates")
    require(contract.get("schema")
                == "rebar-phase2-owned-rust-literal-findall-one-pass-v1-source-freeze"
            and contract.get("version") == 1
            and contract.get("status")
                == "SOURCE FROZEN; NOT BUILT; NOT RUN; NOT BENCHMARKED"
            and contract.get("family") == FAMILY
            and contract.get("source") == public_document(LITERAL_FEATURE["source"])
            and contract.get("protocol") == public_document(LITERAL_FEATURE["protocol"])
            and type(feature) is dict
            and feature.get("path") == LITERAL_VARIANT[1]
            and feature.get("sha256") == LITERAL_VARIANT[2]
            and feature.get("bytes") == LITERAL_VARIANT[3]
            and feature.get("changed_function") == "rust_pattern_literal_findall_direct"
            and feature.get("changed_function_count") == 1
            and feature.get("all_other_predecessor_bytes_unchanged") is True
            and feature.get("complete_independently_owned_source") is True
            and feature.get("native_build") == "NOT RUN"
            and feature.get("matching") == "NOT RUN"
            and feature.get("qualified") is False,
            "authenticate the independently reviewed complete one-pass feature freeze")
    previous_build = predecessor.get("native_build") if type(predecessor) is dict else None
    require(type(predecessor) is dict
            and predecessor.get("path")
                == "candidates/rust/variants/buffer_shape_pickle_v2/py_bridge.c"
            and predecessor.get("sha256")
                == "afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740"
            and predecessor.get("bytes") == 179961
            and type(previous_build) is dict
            and previous_build.get("compiler_process_count") == 28
            and previous_build.get("source_phase_count") == 2
            and previous_build.get("label")
                == "phase2-v19-rust-buffer-shape-root-provenance"
            and previous_build.get("publication_receipt")
                == {"path": V19_BUILD_RECEIPT[1],
                    "sha256": V19_BUILD_RECEIPT[2],
                    "bytes": V19_BUILD_RECEIPT[3], "status": "PASS"}
            and previous_build.get("root_provenance_receipt")
                == {"path": V19_ROOT_RECEIPT[1],
                    "sha256": V19_ROOT_RECEIPT[2],
                    "bytes": V19_ROOT_RECEIPT[3], "status": "PASS"},
            "cross-link the feature freeze to both genuine actual V19 receipts")
    require(type(references) is dict
            and references.get("cpython") == "3.14.6"
            and references.get("reference_status") == "PASS"
            and references.get("original_cases") == 31237
            and references.get("original_groups") == 13
            and references.get("named_private_waivers") == 13
            and references.get("additional_differential_property_cases") == 8244
            and references.get("candidate_status") == "NOT RUN"
            and type(pilot) is dict and pilot.get("case_count") == 864
            and pilot.get("literal_findall_case_count") == 0
            and pilot.get("one_pass_variant_exercised") is False
            and pilot.get("one_pass_variant_timed") is False
            and pilot.get("effect_on_historical_pilot") == "NOT MEASURED"
            and pilot.get("future_literal_practice_cases") == "NOT FROZEN",
            "preserve exact reference denominators and zero actual pilot coverage")
    require(type(effects) is dict
            and effects.get("archive_opens") == 0
            and effects.get("candidate_processes_started") == 0
            and effects.get("candidate_workers_started") == 0
            and effects.get("clock_samples") == 0
            and effects.get("compiler_processes_started") == 0
            and effects.get("correctness") == "NOT MEASURED"
            and effects.get("external_regex_dependencies") == 0
            and effects.get("hidden_cases_read") == 0
            and effects.get("holdout") == "NOT FROZEN; NOT GENERATED; NOT OPENED"
            and effects.get("holdout_case_count") == 4194304
            and effects.get("matching_operations") == 0
            and effects.get("native_libraries_loaded") == 0
            and effects.get("performance") == "NOT MEASURED"
            and effects.get("qualified_candidate_count") == 0
            and effects.get("runtime_non_delegation") == "NOT ESTABLISHED"
            and effects.get("stdlib_regex_delegation") is False
            and effects.get("timing_trials_run") == 0
            and effects.get("winner_selected") is False
            and type(required) is dict
            and required.get("complete_additional_correctness") == "NOT RUN"
            and required.get("complete_original_correctness") == "NOT RUN"
            and required.get("fresh_native_build_and_provenance") == "NOT RUN"
            and required.get("public_api_and_buffer_correctness") == "NOT RUN"
            and required.get("runtime_non_delegation") == "NOT ESTABLISHED"
            and required.get("separately_frozen_literal_practice_cases") == "NOT FROZEN",
            "reject invented candidate runs, clocks, qualifications, or literal speedups")
    return {
        "status": "PASS",
        "source_owner_count": 3,
        "source_sha256": LITERAL_FEATURE["source"][2],
        "protocol_sha256": LITERAL_FEATURE["protocol"][2],
        "contract_sha256": LITERAL_FEATURE["contract"][2],
        "one_pass_variant_sha256": LITERAL_VARIANT[2],
        "one_pass_variant_bytes": LITERAL_VARIANT[3],
        "changed_function_count": 1,
        "historical_practice_case_count": 864,
        "historical_practice_literal_findall_case_count": 0,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def validate_one_pass_bytes(base: dict[str, object], previous: bytes,
                            literal: bytes) -> dict[str, object]:
    require(type(previous) is bytes
            and len(previous) == base["V2_BRIDGE_BYTES"]
            and digest(previous) == base["V2_BRIDGE_SHA256"]
            and type(literal) is bytes
            and len(literal) == LITERAL_VARIANT[3]
            and digest(literal) == LITERAL_VARIANT[2],
            "authenticate the complete distinct V2 and one-pass bridge snapshots")
    marker = b"static PyObject *rust_pattern_literal_findall_direct(\n"
    suffix_marker = b"\nstatic PyObject *bridge_bound_literal_findall("
    require(previous.count(marker) == 1 and literal.count(marker) == 1
            and previous.count(suffix_marker) == 1
            and literal.count(suffix_marker) == 1,
            "require one exact original first-party literal-findall function")
    previous_prefix, previous_tail = previous.split(marker, 1)
    literal_prefix, literal_tail = literal.split(marker, 1)
    previous_body, previous_suffix = previous_tail.split(suffix_marker, 1)
    literal_body, literal_suffix = literal_tail.split(suffix_marker, 1)
    require(previous_prefix == literal_prefix and previous_suffix == literal_suffix
            and previous_body != literal_body
            and b"PyUnicode_Count(" in previous_body
            and b"PyList_New(count)" in previous_body
            and b"PyUnicode_Count(" not in literal_body
            and b"PyList_New(count)" not in literal_body
            and b"for (Py_ssize_t index = 0; index < count; index++)"
                not in literal_body
            and b"PyList_New(0)" in literal_body
            and b"while (cursor <= end && width <= end - cursor)" in literal_body
            and b"PyUnicode_FindChar(" in literal_body
            and b"PyUnicode_Find(" in literal_body
            and b"memmem(" in literal_body
            and b"rust_list_append_owned(" in literal_body
            and b"rust_findall_item(" in literal_body
            and b"rust_subject_release(&subject)" in literal_body
            and b"PyErr_Occurred()" in literal_body,
            "reject any change outside the exact owned one-pass literal bridge")
    return {
        "status": "PASS",
        "scope": "AUTHENTICATED FIRST-PARTY SOURCE SHAPE ONLY",
        "predecessor": {
            "path": base["OWNER_BY_NAME"]["v2_variant"][1],
            "sha256": base["V2_BRIDGE_SHA256"],
            "bytes": base["V2_BRIDGE_BYTES"],
        },
        "variant": row_document(LITERAL_VARIANT),
        "unchanged_prefix_and_suffix": True,
        "changed_first_party_function_count": 1,
        "subject_precount_pass_removed": True,
        "one_pass_unicode_search_present": True,
        "one_pass_bytes_search_present": True,
        "owned_append_helper_reused": True,
        "owned_findall_item_helper_reused": True,
        "subject_release_preserved": True,
        "python_error_propagation_preserved": True,
        "candidate_execution": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "speedup": "NOT MEASURED",
    }


def collect_context(v19: dict[str, object], base: dict[str, object],
                    source_pin: str, protocol_pin: str,
                    contract_pin: str | None = None
                    ) -> tuple[dict[str, object], dict[str, object]]:
    checked_hash(source_pin, "V20 one-pass Rust build source")
    checked_hash(protocol_pin, "V20 one-pass Rust build protocol")
    source_raw, source_info = base["read_self"](SOURCE_PATH, source_pin)
    protocol_raw, protocol_info = base["read_self"](PROTOCOL_PATH, protocol_pin)
    require(source_raw.endswith(b"\n") and not source_raw.endswith(b"\n\n")
            and protocol_raw.endswith(b"\n") and not protocol_raw.endswith(b"\n\n"),
            "require one final newline in the owned V20 source and protocol")
    previous_context, previous_state = v19["collect_context"](
        base, V19["source"][2], V19["protocol"][2], V19["contract"][2],
    )
    require(previous_context.get("status") == "PASS"
            and previous_context.get("version") == 19
            and previous_context.get("first_party_rust_source_owner_count") == 9
            and previous_context.get("future_total_compiler_process_count") == 28,
            "preserve the exact complete V19 source and predecessor provenance kernel")
    raw_graph = {role: base["read_exact"](row) for role, row in GRAPH.items()}
    summary = document(base, raw_graph["summary"], "complete current V86 summary")
    inputs = document(base, raw_graph["inputs"], "complete current V86 inputs")
    require(b"<svg" in raw_graph["svg"] and b"</svg>" in raw_graph["svg"],
            "authenticate the complete actual current V86 overview chart")
    graph = validate_graph(summary, inputs)
    previous_receipt = document(
        base, base["read_exact"](V19_BUILD_RECEIPT), "actual V19 publication receipt",
    )
    previous_root = document(
        base, base["read_exact"](V19_ROOT_RECEIPT), "actual V19 root receipt",
    )
    provenance = validate_previous_receipts(previous_receipt, previous_root)
    feature_contract = document(
        base, base["read_exact"](LITERAL_FEATURE["contract"]),
        "independently reviewed one-pass feature source-freeze contract",
    )
    for role in ("source", "protocol"):
        base["read_exact"](LITERAL_FEATURE[role])
    frozen_feature = validate_literal_feature(feature_contract)
    proposal_verifier = base["read_exact"](EXPANDED_HOLDOUT_PROPOSAL["source"])
    proposal_protocol = base["read_exact"](EXPANDED_HOLDOUT_PROPOSAL["protocol"])
    proposal_raw = base["read_exact"](EXPANDED_HOLDOUT_PROPOSAL["contract"])
    proposal_contract = base["StrictJSON"](proposal_raw).decode()
    require(type(proposal_contract) is dict
            and proposal_raw.endswith(b"\n"),
            "preserve the exact published pretty-formatted public proposal contract")
    expanded_proposal = validate_expanded_holdout_proposal(
        proposal_contract, proposal_verifier, proposal_protocol,
    )
    v18_state = previous_state.get("v18_state")
    require(type(v18_state) is dict
            and type(v18_state.get("originals")) is dict
            and len(v18_state["originals"]) == 9
            and type(v18_state.get("corrected_adapter")) is bytes
            and digest(v18_state["corrected_adapter"])
                == base["CORRECTED_ADAPTER_SHA256"]
            and len(v18_state["corrected_adapter"])
                == base["CORRECTED_ADAPTER_BYTES"]
            and type(v18_state.get("low_level_v9_source")) is bytes,
            "retain all original Rust sources, the corrected adapter, and original kernel")
    feature = validate_one_pass_variant(base, v18_state)
    own_context: dict[str, object] = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "version": VERSION,
        "status": "PASS",
        "family": FAMILY,
        "source": source_info,
        "protocol": protocol_info,
        "authenticated_current_graph_version": GRAPH_VERSION,
        "authenticated_graph_owner_count": 4,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "previous_v19_build_receipt_sha256": V19_BUILD_RECEIPT[2],
        "previous_v19_root_receipt_sha256": V19_ROOT_RECEIPT[2],
        "previous_v19_build_status": "PASS",
        "previous_v19_root_provenance_status": "PASS",
        "previous_v19_compiler_process_count": 28,
        "first_party_rust_source_owner_count": 9,
        "literal_findall_variant_sha256": LITERAL_VARIANT[2],
        "literal_findall_variant_bytes": LITERAL_VARIANT[3],
        "one_pass_feature_source_sha256": LITERAL_FEATURE["source"][2],
        "one_pass_feature_protocol_sha256": LITERAL_FEATURE["protocol"][2],
        "one_pass_feature_contract_sha256": LITERAL_FEATURE["contract"][2],
        "one_pass_feature_freeze_status": "PASS",
        "expanded_holdout_proposal_source_sha256":
            EXPANDED_HOLDOUT_PROPOSAL["source"][2],
        "expanded_holdout_proposal_protocol_sha256":
            EXPANDED_HOLDOUT_PROPOSAL["protocol"][2],
        "expanded_holdout_proposal_contract_sha256":
            EXPANDED_HOLDOUT_PROPOSAL["contract"][2],
        "expanded_holdout_proposal_source_field_count": 71,
        "expanded_holdout_proposal_verifier_executed": False,
        "expanded_holdout_proposal_cases_generated": 0,
        "expanded_holdout_proposal_cases_opened": 0,
        "one_pass_source_shape": "PASS",
        "phase1_v4_readiness": "PASS",
        "candidate_qualification": "BLOCKED",
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "supplemental_reference_cases_per_worker": 8244,
        "historical_complete_rust_semantic_mismatch_count": 1440,
        "historical_complete_rust_verified_passing_case_count": 14853,
        "latest_rust_completed_suite_count": 8,
        "latest_rust_verified_passing_case_count": 12942,
        "latest_rust_worker_failure_count": 5,
        "latest_rust_semantic_mismatch_count": "NOT MEASURED",
        "future_phase_count": 2,
        "future_compiler_process_count_per_phase": 14,
        "future_total_compiler_process_count": 28,
        **boundary(),
    }
    state: dict[str, object] = {
        "source_info": source_info,
        "protocol_info": protocol_info,
        "previous_context": previous_context,
        "previous_state": previous_state,
        "v18_state": v18_state,
        "graph": graph,
        "summary": summary,
        "inputs": inputs,
        "previous_build_receipt": previous_receipt,
        "previous_root_receipt": previous_root,
        "previous_provenance": provenance,
        "feature_contract": feature_contract,
        "frozen_feature": frozen_feature,
        "expanded_holdout_contract": proposal_contract,
        "expanded_holdout_proposal": expanded_proposal,
        "literal_feature": feature,
        "literal_bytes": base["read_exact"](LITERAL_VARIANT),
    }
    expected = contract_document(base, source_pin, protocol_pin, state)
    if contract_pin is not None:
        checked_hash(contract_pin, "V20 canonical machine contract")
        raw, contract_info = base["read_self"](CONTRACT_PATH, contract_pin)
        require(raw == canonical(base, expected)
                and document(base, raw, "V20 complete canonical contract") == expected,
                "reject a stale, incomplete, or noncanonical one-pass build contract")
        own_context["contract"] = contract_info
    base["no_matching_imports"]()
    return own_context, state


def contract_document(base: dict[str, object], source_pin: str,
                      protocol_pin: str,
                      state: dict[str, object]) -> dict[str, object]:
    original_rows = base["OWNER_BY_NAME"]
    original_names = base["RUST_SOURCE_NAMES"]
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION,
        "phase": "SOURCE FREEZE; ONE-PASS RUST NATIVE NOT BUILT OR RUN",
        "family": FAMILY,
        "source": {"path": SOURCE_PATH, "sha256": source_pin,
                   "bytes": state["source_info"]["bytes"]},
        "protocol": {"path": PROTOCOL_PATH, "sha256": protocol_pin,
                     "bytes": state["protocol_info"]["bytes"]},
        "pinned_cpython": {
            "implementation": "CPython", "version": "3.14.6",
            "executable": PYTHON, "sha256": PYTHON_SHA256,
            "isolated": True, "bytecode": False,
        },
        "published_current_graph": {
            "version": GRAPH_VERSION,
            "owners": row_group(GRAPH),
            "owner_count": 4,
            "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
            "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
            "lower_bounds_are_not_a_global_census": True,
        },
        "phase1_v4_readiness": {
            "owners": row_group(V19_PHASE1),
            "status": "PASS",
            "status_scope": "PHASE 1 PYTHON-ORACLE READINESS ONLY",
            "candidate_qualification_status": "BLOCKED",
        },
        "frozen_correctness_denominators": {
            "python_reference_readiness": "PASS",
            "candidate_qualification_status": "BLOCKED",
            "qualification_blockers": list(QUALIFICATION_BLOCKERS),
            "original_case_execution_denominator": 31237,
            "original_suite_count": 13,
            "named_private_waiver_count": 13,
            "supplemental_reference_worker_count": 2,
            "supplemental_case_count_per_reference": 8244,
            "supplemental_added_to_original_denominator": False,
        },
        "historical_rust_results": {
            "historical_complete_candidate_status": "FAIL",
            "historical_complete_semantic_mismatch_count": 1440,
            "historical_complete_verified_passing_case_count": 14853,
            "latest_guarded_candidate_status": "FAIL",
            "latest_guarded_attempted_suite_count": 13,
            "latest_guarded_completed_suite_count": 8,
            "latest_guarded_verified_passing_case_count": 12942,
            "latest_guarded_worker_failure_count": 5,
            "latest_guarded_semantic_mismatch_count": "NOT MEASURED",
            "latest_guarded_failure_capture_complete": True,
            "candidate_qualified": False,
        },
        "immutable_previous_v19": {
            "owners": row_group(V19),
            "source_modified": False,
            "build_receipt": row_document(V19_BUILD_RECEIPT),
            "root_provenance_receipt": row_document(V19_ROOT_RECEIPT),
            "previous_build_status": "PASS",
            "previous_root_provenance_status": "PASS",
            "previous_actual_compiler_process_count": 28,
            "previous_actual_phase_count": 2,
            "previous_actual_native_artifact_count": 4,
            "previous_archive_metadata_attested_by_receipt": {
                **V19_ARCHIVE_METADATA,
                "archive_opened": False,
                "archive_hash_recomputed": False,
                "archive_bytes_read": 0,
            },
            "previous_private_root_opened": False,
            "previous_private_root_scanned": False,
            "previous_candidate_matching": "NOT RUN",
        },
        "owned_rust_source_family": {
            "canonical_source_owners": [
                row_document(original_rows[name]) for name in original_names
            ],
            "canonical_source_owner_count": 9,
            "private_overlays_per_phase": 2,
            "cargo_package_count": 1,
            "external_cargo_dependency_count": 0,
            "external_regular_expression_engine": "FORBIDDEN",
            "stdlib_regex_engine": "FORBIDDEN",
            "cross_candidate_engine": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
            "canonical_sources_modified": False,
        },
        "one_pass_literal_findall_feature": state["literal_feature"],
        "independently_reviewed_one_pass_feature_freeze": {
            "owners": row_group(LITERAL_FEATURE),
            "status": "SOURCE FROZEN; NOT BUILT; NOT RUN; NOT BENCHMARKED",
            "source_owner_count": 3,
            "variant": row_document(LITERAL_VARIANT),
            "changed_first_party_function_count": 1,
            "historical_practice_case_count": 864,
            "historical_practice_literal_findall_case_count": 0,
            "correctness": "NOT MEASURED",
            "performance": "NOT MEASURED",
        },
        "published_expanded_sealed_holdout_proposal": {
            "owners": row_group(EXPANDED_HOLDOUT_PROPOSAL),
            "source_owner_count": 3,
            "source_field_count": 71,
            "schema": "rebar-expanded-sealed-holdout-pre-phase3-proposal-v1",
            "proposal_status": "PRE-PHASE-3 PROPOSAL",
            "final_protocol_status": "NOT FROZEN",
            "generator_status": "NOT FROZEN",
            "secret_status": "NOT GENERATED",
            "case_status": "NOT GENERATED; NOT OPENED",
            "case_count": PROPOSED_FINAL_HOLDOUT_CASE_COUNT,
            "timed_case_count": PROPOSED_FINAL_HOLDOUT_CASE_COUNT,
            "preserved_previous_proposal_case_count":
                PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT,
            "operation_count": len(PROPOSAL_OPERATIONS),
            "pattern_family_count": len(PROPOSAL_PATTERN_FAMILIES),
            "subject_type_count": len(PROPOSAL_SUBJECT_TYPES),
            "lifecycle_count": len(PROPOSAL_LIFECYCLE_SLOTS),
            "stratum_count": 13824,
            "cases_per_stratum": 1024,
            "qualified_independent_family_count": 0,
            "minimum_qualified_independent_family_count": 3,
            "timing_status": "NOT RUN; NOT MEASURED",
            "memory_status": "NOT RUN; NOT MEASURED",
            "runtime_independence_status": "NOT ESTABLISHED",
            "winner_status": "NOT SELECTED",
            "proposal_verifier_executed": False,
            "proposal_cases_generated": 0,
            "proposal_cases_opened": 0,
            "proposal_generator_run": False,
        },
        "authenticated_first_party_build_kernel": {
            "v19_source": row_document(V19["source"]),
            "v16": [
                row_document(original_rows[name])
                for name in ("v16_builder", "v16_protocol", "v16_contract")
            ],
            "v9": [
                row_document(original_rows[name])
                for name in ("low_level_v9", "low_level_v9_protocol",
                             "low_level_v9_contract")
            ],
            "v7": [
                row_document(original_rows[name])
                for name in ("low_level_v7", "low_level_v7_protocol",
                             "low_level_v7_contract")
            ],
            "build_kernel_run_during_source_freeze": False,
        },
        "future_offline_one_pass_root_provenance_build": {
            "authorization": "EXPLICIT FUTURE --build ONLY",
            "unique_label": BUILD_LABEL,
            "root_parent": "/tmp",
            "exact_owned_private_root_prefix": ROOT_PREFIX,
            "private_root_path": "NOT MEASURED",
            "private_root_device": "NOT MEASURED",
            "private_root_inode": "NOT MEASURED",
            "private_root_uid": "NOT MEASURED",
            "private_root_mode": "0700",
            "root_capture_flags": "O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW",
            "root_capture_origin":
                "ACTUAL verify_actual_phases(v9,v7,workdir,phases,steps) CALLBACK",
            "tmp_directory_scanning": "FORBIDDEN",
            "phase_names": list(PHASES),
            "independent_phase_count": 2,
            "source_owners_per_phase": 9,
            "unchanged_source_owners_per_phase": 7,
            "one_pass_literal_bridge_overlays": 2,
            "corrected_public_adapter_overlays": 2,
            "process_roles_per_phase": list(PROCESS_NAMES),
            "compiler_process_count_per_phase": 14,
            "expected_actual_compiler_process_count": 28,
            "cargo_flags": ["--release", "--locked", "--offline", "--frozen"],
            "phase_local_cargo_home": True,
            "external_cargo_dependency_count": 0,
            "verify_original_reproducibility_first": True,
            "compare_complete_owned_engine_and_bridge_elf": True,
            "root_receipt_exclusive_creation": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "root_receipt_file_fsync": True,
            "root_receipt_directory_fsync": True,
            "additional_root_receipt_count": 1,
            "native_activation": "FORBIDDEN",
            "matching_or_candidate_workers": "FORBIDDEN",
            "holdout": "FORBIDDEN",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "build_pass_means": "REPRODUCIBLE COMPILATION AND ROOT PROVENANCE ONLY",
        },
        "performance_evidence": {
            "existing_864_case_practice_literal_findall_cases": 0,
            "one_pass_literal_development_cohort": "NOT FROZEN",
            "candidate_matching": "NOT RUN",
            "speedup": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "final_holdout_proposal_status": "PRE-PHASE-3 PROPOSAL",
            "final_holdout_protocol_status": "NOT FROZEN",
            "final_holdout_generator_status": "NOT FROZEN",
            "final_holdout_secret_status": "NOT GENERATED",
            "final_holdout_case_status": "NOT GENERATED; NOT OPENED",
            "final_holdout_case_count": PROPOSED_FINAL_HOLDOUT_CASE_COUNT,
            "previous_holdout_proposal_case_count":
                PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT,
            "final_holdout": "NOT OPENED",
            "winner_selected": False,
        },
        "source_only_effects": boundary(),
    }


def synthetic_root_plan(v19: dict[str, object],
                        base: dict[str, object]) -> dict[str, object]:
    plan = base["clone"](v19["synthetic_root_plan"](base))
    require(type(plan) is dict, "derive only the complete first-party synthetic plan")
    plan["schema"] = SCHEMA + "-synthetic-root-control"
    plan["graph_version"] = GRAPH_VERSION
    plan["variant_sha256"] = LITERAL_VARIANT[2]
    plan["variant_bytes"] = LITERAL_VARIANT[3]
    plan["predecessor_bridge_sha256"] = base["V2_BRIDGE_SHA256"]
    plan["predecessor_bridge_bytes"] = base["V2_BRIDGE_BYTES"]
    return plan


def validate_synthetic_root(v19: dict[str, object], base: dict[str, object],
                            plan: object) -> dict[str, object]:
    require(type(plan) is dict
            and plan.get("schema") == SCHEMA + "-synthetic-root-control"
            and plan.get("graph_version") == GRAPH_VERSION
            and plan.get("variant_sha256") == LITERAL_VARIANT[2]
            and plan.get("variant_bytes") == LITERAL_VARIANT[3]
            and plan.get("predecessor_bridge_sha256") == base["V2_BRIDGE_SHA256"]
            and plan.get("predecessor_bridge_bytes") == base["V2_BRIDGE_BYTES"]
            and plan.get("actual_root_descriptor_opens") == 0
            and plan.get("actual_compiler_process_count") == 0
            and plan.get("candidate_workers_started") == 0
            and plan.get("archive_opens") == 0
            and plan.get("native_libraries_loaded") == 0
            and plan.get("holdout") == "NOT OPENED",
            "reject a stale variant, real process, archive, native, or holdout")
    inherited = base["clone"](plan)
    inherited["schema"] = v19["SCHEMA"] + "-synthetic-root-control"
    inherited["graph_version"] = v19["GRAPH_VERSION"]
    for name in ("variant_sha256", "variant_bytes", "predecessor_bridge_sha256",
                 "predecessor_bridge_bytes"):
        inherited.pop(name)
    proof = v19["validate_synthetic_root"](inherited)
    require(proof.get("status") == "PASS"
            and proof.get("synthetic_only") is True
            and proof.get("synthetic_phase_count") == 2
            and proof.get("synthetic_native_owner_count") == 4
            and proof.get("synthetic_process_role_count") == 28
            and proof.get("actual_root_descriptor_opens") == 0
            and proof.get("actual_compiler_process_count") == 0,
            "preserve all 28 strictly synthetic controls without a real build")
    return {
        **proof,
        "one_pass_variant_sha256": LITERAL_VARIANT[2],
        "one_pass_variant_bytes": LITERAL_VARIANT[3],
    }


def self_test(v19: dict[str, object], base: dict[str, object],
              source_pin: str, protocol_pin: str,
              contract_pin: str) -> dict[str, object]:
    context, state = collect_context(v19, base, source_pin, protocol_pin, contract_pin)
    accepted = 0
    rejected = 0

    def reject(operation: object, label: str) -> None:
        nonlocal rejected
        try:
            operation()
        except Exception:
            rejected += 1
            return
        raise GateError("accepted hostile V20 one-pass source control: " + label)

    plan = synthetic_root_plan(v19, base)
    proof = validate_synthetic_root(v19, base, plan)
    require(proof.get("synthetic_process_role_count") == 28,
            "prove every complete process role using synthetic controls only")
    accepted += 1
    require(context.get("status") == "PASS"
            and state["previous_provenance"]["actual_previous_build_status"] == "PASS"
            and state["previous_provenance"]["actual_previous_root_provenance_status"]
                == "PASS"
            and state["graph"]["version"] == GRAPH_VERSION
            and state["literal_feature"]["changed_first_party_function_count"] == 1
            and state["expanded_holdout_proposal"]["case_count"]
                == PROPOSED_FINAL_HOLDOUT_CASE_COUNT
            and state["expanded_holdout_proposal"]["proposal_verifier_executed"]
                is False
            and state["expanded_holdout_proposal"]["proposal_cases_opened"] == 0,
            "preserve actual V19, historical V86, one-pass source, and sealed proposal")
    accepted += 1
    valid_build_args = [
        "--build",
        "--source-sha256", source_pin,
        "--protocol-sha256", protocol_pin,
        "--contract-sha256", contract_pin,
        "--label", BUILD_LABEL,
        "--combined-bridge-sha256", LITERAL_VARIANT[2],
        "--combined-bridge-bytes", str(LITERAL_VARIANT[3]),
        "--corrected-adapter-sha256", base["CORRECTED_ADAPTER_SHA256"],
        "--corrected-adapter-bytes", str(base["CORRECTED_ADAPTER_BYTES"]),
        "--predecessor-bridge-sha256", base["V2_BRIDGE_SHA256"],
        "--predecessor-bridge-bytes", str(base["V2_BRIDGE_BYTES"]),
        "--previous-build-receipt-sha256", V19_BUILD_RECEIPT[2],
        "--previous-root-receipt-sha256", V19_ROOT_RECEIPT[2],
        "--graph-summary-sha256", GRAPH["summary"][2],
        "--literal-feature-source-sha256", LITERAL_FEATURE["source"][2],
        "--literal-feature-protocol-sha256", LITERAL_FEATURE["protocol"][2],
        "--literal-feature-contract-sha256", LITERAL_FEATURE["contract"][2],
        "--expanded-holdout-proposal-source-sha256",
        EXPANDED_HOLDOUT_PROPOSAL["source"][2],
        "--expanded-holdout-proposal-protocol-sha256",
        EXPANDED_HOLDOUT_PROPOSAL["protocol"][2],
        "--expanded-holdout-proposal-contract-sha256",
        EXPANDED_HOLDOUT_PROPOSAL["contract"][2],
        "--phase1-v4-source-sha256", V19_PHASE1["source"][2],
        "--phase1-v4-protocol-sha256", V19_PHASE1["protocol"][2],
        "--phase1-v4-contract-sha256", V19_PHASE1["contract"][2],
    ]
    for name in base["RUST_SOURCE_NAMES"]:
        row = base["OWNER_BY_NAME"][name]
        valid_build_args.extend(("--owned-source-sha256", row[1] + "=" + row[2]))
    parsed = parse_cli(base, valid_build_args)
    require(parsed.get("mode") == "--build"
            and parsed.get("combined_bridge_sha256") == LITERAL_VARIANT[2]
            and parsed.get("combined_bridge_bytes") == LITERAL_VARIANT[3]
            and len(parsed["owned_source_sha256"]) == 9
            and parsed.get("literal_feature_contract_sha256")
                == LITERAL_FEATURE["contract"][2]
            and parsed.get("expanded_holdout_proposal_source_sha256")
                == EXPANDED_HOLDOUT_PROPOSAL["source"][2]
            and parsed.get("expanded_holdout_proposal_protocol_sha256")
                == EXPANDED_HOLDOUT_PROPOSAL["protocol"][2]
            and parsed.get("expanded_holdout_proposal_contract_sha256")
                == EXPANDED_HOLDOUT_PROPOSAL["contract"][2]
            and _ROOT_CAPTURE is None
            and base.get("_WALL_ENABLED") is True,
            "validate the future exact build syntax without authorizing any build")
    accepted += 1
    proposal_verifier = base["read_exact"](EXPANDED_HOLDOUT_PROPOSAL["source"])
    proposal_protocol = base["read_exact"](EXPANDED_HOLDOUT_PROPOSAL["protocol"])
    expanded = state["expanded_holdout_contract"]
    for key, replacement in (
        ("schema", "rebar-expanded-sealed-holdout-pre-phase3-proposal-v0"),
        ("proposal_status", "FROZEN"),
        ("final_protocol_status", "FROZEN"),
        ("generator_status", "RUN"),
        ("secret_status", "GENERATED"),
        ("case_status", "GENERATED; OPENED"),
        ("timing_status", "RUN; MEASURED"),
        ("memory_status", "RUN; MEASURED"),
        ("runtime_independence_status", "PASS"),
        ("winner_status", "SELECTED"),
        ("case_count", PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT),
        ("timed_case_count", PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT),
        ("preserved_previous_proposal_case_count",
         PROPOSED_FINAL_HOLDOUT_CASE_COUNT),
        ("original_p0_case_count", 31236),
        ("original_p0_suite_count", 12),
        ("named_private_waiver_count", 12),
        ("separate_differential_case_count", 8243),
        ("qualified_independent_family_count", 3),
        ("minimum_qualified_independent_family_count", 1),
        ("operation_count", 35),
        ("pattern_family_count", 23),
        ("subject_type_count", 3),
        ("lifecycle_count", 3),
        ("stratum_count", 13823),
        ("cases_per_stratum", 1023),
        ("paired_round_count", 23),
        ("participant_count", 3),
        ("candidate_participant_count", 2),
        ("minimum_significantly_faster_case_count", 8493465),
        ("pinned_python_sha256", "0" * 64),
    ):
        changed = dict(expanded)
        changed[key] = replacement
        reject(lambda value=changed: validate_expanded_holdout_proposal(
            value, proposal_verifier, proposal_protocol,
        ), "expanded-sealed-proposal:" + key)
    for axis in (
        "operations", "primary_pattern_families", "subject_types",
        "lifecycle_slots", "prohibited_matcher_delegates",
    ):
        for label in ("omitted", "repeated"):
            changed = dict(expanded)
            original = expanded[axis]
            changed[axis] = (list(original[:-1]) if label == "omitted"
                             else list(original[:-1]) + [original[0]])
            reject(lambda value=changed: validate_expanded_holdout_proposal(
                value, proposal_verifier, proposal_protocol,
            ), "expanded-sealed-proposal:" + axis + ":" + label)
    for label, candidate_source, candidate_protocol in (
        ("truncated-verifier", proposal_verifier[:-1], proposal_protocol),
        ("extended-verifier", proposal_verifier + b"\n", proposal_protocol),
        ("truncated-protocol", proposal_verifier, proposal_protocol[:-1]),
        ("extended-protocol", proposal_verifier, proposal_protocol + b"\n"),
    ):
        reject(lambda current_source=candidate_source,
               current_protocol=candidate_protocol:
               validate_expanded_holdout_proposal(
                   expanded, current_source, current_protocol,
               ), "expanded-sealed-proposal:" + label)
    for label in ("omitted", "reordered"):
        changed = dict(expanded)
        owners = list(expanded["required_public_owners"])
        if label == "omitted":
            changed["required_public_owners"] = owners[:-1]
        else:
            owners[0], owners[1] = owners[1], owners[0]
            changed["required_public_owners"] = owners
        reject(lambda value=changed: validate_expanded_holdout_proposal(
            value, proposal_verifier, proposal_protocol,
        ), "expanded-sealed-proposal:public-owners:" + label)
    for key, replacement in (
        ("version", 85),
        ("actual_current_graph_predecessor_version", 69),
        ("authenticated_evidence_owner_lower_bound", 276),
        ("authenticated_history_reference_lower_bound", 281),
        ("full_case_denominator", 31236),
        ("suite_count", 12),
        ("private_waiver_count", 12),
        ("qualified_candidate_count", 1),
        ("actual_rust_semantic_mismatch_count", 0),
        ("actual_rust_verified_passing_case_count", 12942),
        ("rust_v15_original_campaign_completed_suite_count", 13),
        ("rust_v15_original_campaign_verified_passing_case_count", 14853),
        ("rust_v15_original_campaign_infrastructure_failure_count", 0),
        ("rust_native_build_v19_private_root_provenance", "NOT ESTABLISHED"),
        ("rust_native_build_v19_compiler_process_count", 27),
        ("final_holdout_opened", True),
        ("performance", "FASTER"),
        ("timing_trials_run", 1),
        ("winner_selected", True),
    ):
        changed = dict(state["summary"])
        changed[key] = replacement
        reject(lambda value=changed: validate_graph(value, state["inputs"]),
               "v86-summary:" + key)
    for key, replacement in (
        ("schema", "rebar-candidate-current-overview-v85-inputs"),
        ("version", 85),
        ("qualified_candidate_count", 1),
        ("rust_v15_original_campaign_completed_suite_count", 13),
        ("final_holdout_opened", True),
        ("performance", "FASTER"),
    ):
        changed = dict(state["inputs"])
        changed[key] = replacement
        reject(lambda value=changed: validate_graph(state["summary"], value),
               "v86-inputs:" + key)
    for key, replacement in (
        ("schema", SCHEMA + "-durable-publication-receipt"),
        ("status", "FAIL"),
        ("build_status", "FAIL"),
        ("source_sha256", "0" * 64),
        ("protocol_sha256", "0" * 64),
        ("contract_sha256", "0" * 64),
        ("actual_compiler_process_count", 27),
        ("combined_bridge_sha256", LITERAL_VARIANT[2]),
        ("combined_bridge_bytes", LITERAL_VARIANT[3]),
        ("archive_sha256", "0" * 64),
        ("candidate_matching", "PASS"),
        ("candidate_qualified", True),
        ("native_libraries_loaded", 1),
        ("hidden_cases_read", 1),
        ("clock_samples", 1),
        ("holdout", "OPENED"),
    ):
        changed = dict(state["previous_build_receipt"])
        changed[key] = replacement
        reject(lambda value=changed: validate_previous_receipts(
            value, state["previous_root_receipt"],
        ), "v19-build-receipt:" + key)
    for key, replacement in (
        ("schema", SCHEMA + "-durable-root-provenance-receipt"),
        ("status", "FAIL"),
        ("canonical_build_receipt_sha256", "0" * 64),
        ("canonical_build_archive_sha256", "0" * 64),
        ("canonical_build_archive_opened", True),
        ("actual_compiler_process_count", 27),
        ("actual_source_phase_count", 1),
        ("bridge_overlay_apply_count", 1),
        ("candidate_qualified", True),
        ("tmp_directory_scanned", True),
        ("historical_archives_opened", 1),
        ("hidden_cases_read", 1),
        ("holdout", "OPENED"),
    ):
        changed = dict(state["previous_root_receipt"])
        changed[key] = replacement
        reject(lambda value=changed: validate_previous_receipts(
            state["previous_build_receipt"], value,
        ), "v19-root-receipt:" + key)
    for key, replacement in (
        ("schema", "foreign-feature"),
        ("version", 2),
        ("status", "PASS"),
        ("family", "c"),
    ):
        changed = dict(state["feature_contract"])
        changed[key] = replacement
        reject(lambda value=changed: validate_literal_feature(value),
               "literal-feature:" + key)
    for section, key, replacement in (
        ("candidate_variant", "sha256", "0" * 64),
        ("candidate_variant", "bytes", 179961),
        ("candidate_variant", "changed_function_count", 2),
        ("candidate_variant", "qualified", True),
        ("predecessor", "sha256", LITERAL_VARIANT[2]),
        ("historical_practice_pilot", "literal_findall_case_count", 1),
        ("historical_practice_pilot", "one_pass_variant_timed", True),
        ("phase_boundary", "clock_samples", 1),
        ("phase_boundary", "hidden_cases_read", 1),
        ("phase_boundary", "performance", "FASTER"),
    ):
        changed = dict(state["feature_contract"])
        replacement_section = dict(changed[section])
        replacement_section[key] = replacement
        changed[section] = replacement_section
        reject(lambda value=changed: validate_literal_feature(value),
               "literal-feature:" + section + ":" + key)
    authentic_literal = state["literal_bytes"]
    authentic_previous = state["v18_state"]["combined_bridge"]
    for changed_previous, changed_literal, label in (
        (authentic_previous, authentic_literal[:-1], "truncated-variant"),
        (authentic_previous, authentic_literal + b"\n", "extra-variant-byte"),
        (authentic_previous, authentic_previous, "borrowed-v2-bridge"),
        (authentic_previous[:-1], authentic_literal, "truncated-predecessor"),
        (authentic_literal, authentic_literal, "substituted-predecessor"),
    ):
        reject(lambda previous=changed_previous, literal=changed_literal:
               validate_one_pass_bytes(base, previous, literal),
               "literal-source:" + label)
    for flag, replacement in (
        ("--combined-bridge-sha256", base["V2_BRIDGE_SHA256"]),
        ("--combined-bridge-bytes", str(base["V2_BRIDGE_BYTES"])),
        ("--corrected-adapter-sha256", "0" * 64),
        ("--predecessor-bridge-sha256", LITERAL_VARIANT[2]),
        ("--previous-build-receipt-sha256", "0" * 64),
        ("--previous-root-receipt-sha256", "0" * 64),
        ("--graph-summary-sha256", "0" * 64),
        ("--literal-feature-source-sha256", "0" * 64),
        ("--literal-feature-protocol-sha256", "0" * 64),
        ("--literal-feature-contract-sha256", "0" * 64),
        ("--expanded-holdout-proposal-source-sha256", "0" * 64),
        ("--expanded-holdout-proposal-protocol-sha256", "0" * 64),
        ("--expanded-holdout-proposal-contract-sha256", "0" * 64),
        ("--phase1-v4-source-sha256", "0" * 64),
        ("--label", "borrowed-build"),
    ):
        changed = list(valid_build_args)
        position = changed.index(flag)
        changed[position + 1] = replacement
        reject(lambda value=changed: parse_cli(base, value),
               "future-build-authority:" + flag)
    omitted = list(valid_build_args[:-2])
    reject(lambda: parse_cli(base, omitted), "future-build-authority:omitted-owner")
    duplicated = list(valid_build_args)
    duplicated.extend(valid_build_args[-2:])
    reject(lambda: parse_cli(base, duplicated),
           "future-build-authority:duplicated-owner")
    duplicate_flag = list(valid_build_args)
    duplicate_flag.extend(("--label", BUILD_LABEL))
    reject(lambda: parse_cli(base, duplicate_flag),
           "future-build-authority:duplicated-label")
    for key, replacement in (
        ("schema", "borrowed-root-schema"),
        ("graph_version", 70),
        ("variant_sha256", "0" * 64),
        ("variant_bytes", 179961),
        ("predecessor_bridge_sha256", LITERAL_VARIANT[2]),
        ("predecessor_bridge_bytes", LITERAL_VARIANT[3]),
        ("root_path", "/tmp/borrowed-root"),
        ("root_device", 0),
        ("root_inode", 0),
        ("root_uid", -1),
        ("root_mode", "0755"),
        ("root_evidence_kind", "ACTUAL ROOT"),
        ("phase_count", 1),
        ("expected_process_count", 27),
        ("actual_root_descriptor_opens", 1),
        ("actual_compiler_process_count", 1),
        ("candidate_workers_started", 1),
        ("archive_opens", 1),
        ("native_libraries_loaded", 1),
        ("holdout", "OPENED"),
    ):
        changed = base["clone"](plan)
        changed[key] = replacement
        reject(lambda value=changed: validate_synthetic_root(v19, base, value), key)
    for index in range(2):
        for key, replacement in (
            ("name", "borrowed"), ("inode", 0), ("mode", "0755"),
            ("evidence_kind", "ACTUAL ROOT"),
        ):
            changed = base["clone"](plan)
            changed["phases"][index][key] = replacement
            reject(lambda value=changed: validate_synthetic_root(v19, base, value),
                   "phase:" + str(index) + ":" + key)
        for role in ("engine", "bridge"):
            for key, replacement in (
                ("sha256", "0" * 64),
                ("inode", 0),
                ("file_name", "foreign_regex.so"),
                ("mode", "0644"),
                ("evidence_kind", "ACTUAL NATIVE"),
            ):
                changed = base["clone"](plan)
                changed["phases"][index]["native_outputs"][role][key] = replacement
                reject(lambda value=changed: validate_synthetic_root(v19, base, value),
                       "native:" + role + ":" + key)
    for index in range(28):
        for key, replacement in (
            ("name", "build_external_regex"),
            ("phase", "borrowed-phase"),
            ("pid", 0),
            ("exit_status", 1),
            ("evidence_kind", "ACTUAL COMPILER"),
        ):
            changed = base["clone"](plan)
            changed["processes"][index][key] = replacement
            reject(lambda value=changed: validate_synthetic_root(v19, base, value),
                   "process:" + str(index) + ":" + key)
    probes = (
        ("unlisted-file", lambda: builtins.open("/etc/hosts", "rb")),
        ("tmp-root-scan", lambda: builtins.open("/tmp", "rb")),
        ("v19-private-root", lambda: sys.audit(
            "open", "/tmp/" + ROOT_PREFIX + "forbidden", "r", os.O_RDONLY,
        )),
        ("source-mutation", lambda: builtins.open(ROOT + "/" + SOURCE_PATH, "w")),
        ("literal-mutation", lambda: builtins.open(
            ROOT + "/" + LITERAL_VARIANT[1], "w",
        )),
        ("v19-compressed-archive", lambda: builtins.open(
            ROOT + "/" + V19_ARCHIVE_METADATA["path"], "rb",
        )),
        ("hidden-holdout", lambda: builtins.open(
            ROOT + "/benchmarks/holdout.json", "rb",
        )),
        ("stdlib-regex", lambda: sys.audit("import", "re", None, None, None, None)),
        ("cpython-matcher", lambda: sys.audit(
            "import", "_sre", None, None, None, None,
        )),
        ("candidate-import", lambda: sys.audit(
            "import", "candidates.rust_candidate", None, None, None, None,
        )),
        ("native-load", lambda: sys.audit("ctypes.dlopen", "foreign.so")),
        ("compiler", lambda: sys.audit(
            "subprocess.Popen", "cargo", (), None, None,
        )),
        ("network", lambda: sys.audit("socket.__new__", None, 2, 1, 0)),
        ("thread", lambda: sys.audit("threading.Thread.start", None)),
        ("clock", lambda: sys.audit("time.perf_counter")),
        ("temporary-root", lambda: sys.audit(
            "tempfile.mkdtemp", "/tmp/forbidden",
        )),
        ("filesystem-rename", lambda: sys.audit("os.rename", "a", "b", -1, -1)),
        ("archive-inflation", lambda: sys.audit("gzip.decompress", b"forbidden")),
        ("foreign-execution", lambda: sys.audit("exec", "forbidden")),
        ("foreign-compilation", lambda: sys.audit(
            "compile", b"forbidden", "foreign.py",
        )),
    )
    for label, operation in probes:
        reject(operation, "physically-block:" + label)
    for category in ("filesystem", "matching_import", "native", "process",
                     "network", "thread", "clock", "temporary", "archive",
                     "dynamic_execution"):
        require(base["_BLOCKED"].get(category, 0) >= 1,
                "physically exercise the real source-only effect wall: " + category)
    require(rejected >= 190,
            "reject the complete one-pass source, root, native, and process matrix")
    base["no_matching_imports"]()
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS",
        "version": VERSION,
        "family": FAMILY,
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "accepted_positive_control_count": accepted,
        "rejected_hostile_controls": rejected,
        "blocked_effect_attempts": dict(base["_BLOCKED"]),
        "synthetic_control_proof": proof,
        "authenticated_current_graph_version": GRAPH_VERSION,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "expanded_holdout_proposal_source_sha256":
            EXPANDED_HOLDOUT_PROPOSAL["source"][2],
        "expanded_holdout_proposal_protocol_sha256":
            EXPANDED_HOLDOUT_PROPOSAL["protocol"][2],
        "expanded_holdout_proposal_contract_sha256":
            EXPANDED_HOLDOUT_PROPOSAL["contract"][2],
        "expanded_holdout_proposal_source_field_count": 71,
        "expanded_holdout_proposal_verifier_executed": False,
        "expanded_holdout_proposal_cases_generated": 0,
        "expanded_holdout_proposal_cases_opened": 0,
        "actual_previous_rust_build_status": "PASS",
        "actual_previous_rust_root_provenance_status": "PASS",
        "actual_previous_rust_compiler_process_count": 28,
        "one_pass_variant_sha256": LITERAL_VARIANT[2],
        "one_pass_variant_bytes": LITERAL_VARIANT[3],
        "changed_first_party_function_count": 1,
        "historical_complete_rust_semantic_mismatch_count": 1440,
        "historical_complete_rust_verified_passing_case_count": 14853,
        "latest_rust_completed_suite_count": 8,
        "latest_rust_verified_passing_case_count": 12942,
        "latest_rust_worker_failure_count": 5,
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "future_total_compiler_process_count": 28,
        **boundary(),
    }


def checked_label(value: object) -> str:
    require(type(value) is str and 0 < len(value) <= 48
            and all(char.isascii() and (char.isalnum() or char in "-_")
                    for char in value),
            "require one safe independently owned Rust build evidence label")
    return value


def evidence_names(label: str, failed: bool) -> tuple[str, str]:
    require(label == BUILD_LABEL and type(failed) is bool,
            "require the unique V20 one-pass Rust build outcome")
    stem = "native-source-build-v20-rust-" + checked_label(label)
    if failed:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def root_receipt_name(label: str) -> str:
    require(label == BUILD_LABEL,
            "reject another candidate's one-pass root provenance receipt")
    return "native-source-build-v20-rust-" + checked_label(label) \
        + "-root-provenance-receipt.json"


def assert_fresh_root_receipt(label: str) -> None:
    target = ROOT + "/" + EVIDENCE_PATH + "/" + root_receipt_name(label)
    try:
        os.lstat(target)
    except FileNotFoundError:
        return
    raise GateError("reject a pre-existing V20 one-pass root-provenance receipt")


def publish_root_provenance(v19: dict[str, object], base: dict[str, object],
                            module: object, state: dict[str, object],
                            result: dict[str, object],
                            options: dict[str, object]) -> dict[str, object]:
    require(result.get("status") == "PASS"
            and result.get("build_status") == "PASS"
            and result.get("family") == FAMILY
            and result.get("label") == BUILD_LABEL
            and type(_ROOT_CAPTURE) is dict,
            "publish provenance only after an actual complete one-pass Rust build")
    captured = _ROOT_CAPTURE
    assert isinstance(captured, dict)
    require(captured.get("unique_process_count") == 28
            and captured.get("phase_count") == 2,
            "require 28 distinct genuine compiler roles in two fresh phases")
    runtime_state = state.get("runtime_state")
    require(type(runtime_state) is dict,
            "retain the actual authenticated one-pass build state")
    kernel = runtime_state.get("kernel")
    require(kernel is not None, "retain the first-party durable publication kernel")
    relative = result.get("receipt_relative")
    receipt_hash = result.get("receipt_sha256")
    require(type(relative) is str
            and relative == EVIDENCE_PATH + "/" + evidence_names(BUILD_LABEL, False)[1],
            "bind only the fresh actual V20 one-pass build receipt")
    checked_hash(receipt_hash, "actual V20 one-pass build receipt")
    absolute = ROOT + "/" + relative
    observed = os.stat(absolute, follow_symlinks=False)
    row = ("actual_v20_one_pass_build_receipt", relative, receipt_hash,
           observed.st_size, observed.st_dev, observed.st_ino)
    base["_ALLOWLIST"] = frozenset(set(base["_ALLOWLIST"]) | {absolute})
    raw = base["read_exact"](row)
    receipt = document(base, raw, "fresh independently published V20 build receipt")
    require(receipt.get("schema") == SCHEMA + "-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and receipt.get("family") == FAMILY
            and receipt.get("label") == BUILD_LABEL
            and receipt.get("source_sha256") == options["source_sha256"]
            and receipt.get("protocol_sha256") == options["protocol_sha256"]
            and receipt.get("contract_sha256") == options["contract_sha256"]
            and receipt.get("expected_actual_compiler_process_count") == 28
            and receipt.get("actual_compiler_process_count") == 28
            and receipt.get("combined_bridge_sha256") == LITERAL_VARIANT[2]
            and receipt.get("combined_bridge_bytes") == LITERAL_VARIANT[3]
            and receipt.get("combined_bridge_overlay_apply_count") == 2
            and receipt.get("corrected_public_adapter_overlay_apply_count") == 2
            and receipt.get("archive_relative") == result.get("archive_relative")
            and receipt.get("archive_sha256") == result.get("archive_sha256")
            and receipt.get("candidate_matching") == "NOT RUN"
            and receipt.get("candidate_qualified") is False,
            "authenticate the complete real one-pass build receipt before root proof")
    root_record = {
        "schema": SCHEMA + "-durable-root-provenance-receipt",
        "version": VERSION,
        "status": "PASS",
        "publication_pass_means":
            "DURABLE REPRODUCIBLE FIRST-PARTY ONE-PASS BUILD ROOT PROVENANCE ONLY",
        "family": FAMILY,
        "label": BUILD_LABEL,
        "source_sha256": options["source_sha256"],
        "protocol_sha256": options["protocol_sha256"],
        "contract_sha256": options["contract_sha256"],
        "frozen_graph_version": GRAPH_VERSION,
        "frozen_graph_summary_sha256": GRAPH["summary"][2],
        "expanded_holdout_proposal_source_sha256":
            EXPANDED_HOLDOUT_PROPOSAL["source"][2],
        "expanded_holdout_proposal_protocol_sha256":
            EXPANDED_HOLDOUT_PROPOSAL["protocol"][2],
        "expanded_holdout_proposal_contract_sha256":
            EXPANDED_HOLDOUT_PROPOSAL["contract"][2],
        "expanded_holdout_proposal_status": "PRE-PHASE-3 PROPOSAL",
        "expanded_holdout_proposal_case_count": PROPOSED_FINAL_HOLDOUT_CASE_COUNT,
        "previous_holdout_proposal_case_count":
            PREVIOUS_PROPOSED_HOLDOUT_CASE_COUNT,
        "expanded_holdout_final_protocol_status": "NOT FROZEN",
        "expanded_holdout_generator_status": "NOT FROZEN",
        "expanded_holdout_secret_status": "NOT GENERATED",
        "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
        "expanded_holdout_proposal_verifier_executed": False,
        "expanded_holdout_cases_generated": 0,
        "expanded_holdout_cases_opened": 0,
        "previous_v19_build_receipt_sha256": V19_BUILD_RECEIPT[2],
        "previous_v19_root_receipt_sha256": V19_ROOT_RECEIPT[2],
        "previous_bridge_sha256": base["V2_BRIDGE_SHA256"],
        "previous_bridge_bytes": base["V2_BRIDGE_BYTES"],
        "one_pass_literal_bridge_sha256": LITERAL_VARIANT[2],
        "one_pass_literal_bridge_bytes": LITERAL_VARIANT[3],
        "canonical_build_status": "PASS",
        "canonical_build_archive_relative": receipt["archive_relative"],
        "canonical_build_archive_sha256": receipt["archive_sha256"],
        "canonical_build_archive_bytes": receipt["archive_bytes"],
        "canonical_build_archive_opened": False,
        "canonical_build_receipt_relative": relative,
        "canonical_build_receipt_sha256": receipt_hash,
        "canonical_build_receipt_bytes": observed.st_size,
        "canonical_build_receipt_device": observed.st_dev,
        "canonical_build_receipt_inode": observed.st_ino,
        "root": captured["root"],
        "actual_compiler_process_count": 28,
        "expected_compiler_process_count": 28,
        "actual_source_phase_count": 2,
        "bridge_overlay_apply_count": 2,
        "adapter_overlay_apply_count": 2,
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "candidate_workers_started": 0,
        "native_libraries_loaded": 0,
        "canonical_sources_modified": False,
        "tmp_directory_scanned": False,
        "historical_archives_opened": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    encoded = canonical(base, root_record)
    require(0 < len(encoded) <= MAX_OWNER_BYTES,
            "bound the independently owned complete V20 root receipt")
    destination = module.ROOT / EVIDENCE_PATH / root_receipt_name(BUILD_LABEL)
    published = kernel.write_fresh(destination, encoded, synchronize=True)
    directory = kernel.fsync_directory(module.ROOT / EVIDENCE_PATH)
    require(published.get("sha256") == digest(encoded)
            and published.get("bytes") == len(encoded)
            and published.get("exclusive_creation") is True
            and published.get("file_fsync_completed") is True
            and directory.get("completed") is True,
            "publish exactly one fresh exclusive, fsynced V20 root receipt")
    return {
        **result,
        "root_provenance_status": "PASS",
        "root_provenance_receipt_relative":
            EVIDENCE_PATH + "/" + root_receipt_name(BUILD_LABEL),
        "root_provenance_receipt_sha256": published["sha256"],
        "root_provenance_receipt_bytes": published["bytes"],
        "root_provenance_receipt_device": published["device"],
        "root_provenance_receipt_inode": published["inode"],
        "root_provenance_directory_fsync": directory,
        "actual_compiler_process_count": 28,
        "actual_private_phase_count": 2,
        "one_pass_literal_bridge_sha256": LITERAL_VARIANT[2],
        "one_pass_literal_bridge_bytes": LITERAL_VARIANT[3],
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
    }


def run_build(v19: dict[str, object], base: dict[str, object],
              options: dict[str, object]) -> dict[str, object]:
    global _ROOT_CAPTURE
    require(options.get("mode") == "--build"
            and options.get("label") == BUILD_LABEL
            and _ROOT_CAPTURE is None and base.get("_WALL_ENABLED") is False,
            "require one explicitly authorized future V20 first-party native build")
    base["verify_future_phase_one_v4"](options)
    context, state = collect_context(
        v19, base, options["source_sha256"], options["protocol_sha256"],
        options["contract_sha256"],
    )
    previous_state = state["v18_state"]
    raw = previous_state["owners"]["v16_builder"]
    owner = base["OWNER_BY_NAME"]["v16_builder"]
    require(type(raw) is bytes and digest(raw) == owner[2],
            "execute only the exact independently audited first-party V16 kernel")
    import types

    module_name = "_rebar_v20_explicit_owned_rust_one_pass_v16_kernel"
    require(module_name not in sys.modules,
            "reject reused or cross-family first-party build authority")
    module = types.ModuleType(module_name)
    module.__file__ = ROOT + "/" + owner[1]
    sys.modules[module_name] = module
    runtime_state: dict[str, object] | None = None
    try:
        exec(compile(raw, module.__file__, "exec", dont_inherit=True),
             module.__dict__)
        require(module.SCHEMA == "rebar-phase2-owned-rust-buffer-shape-source-build-v16"
                and module.VERSION == 16 and module.FAMILY == FAMILY
                and module.PHASES == PHASES
                and module.PROCESS_NAMES == PROCESS_NAMES
                and module.ROOT_PREFIX == ROOT_PREFIX,
                "reject substituted source family, compiler roles, or root kernel")
        module.SCHEMA = SCHEMA
        module.VERSION = VERSION
        module.SOURCE_PATH = SOURCE_PATH
        module.PROTOCOL_PATH = PROTOCOL_PATH
        module.CONTRACT_PATH = CONTRACT_PATH
        module.FINAL_GRAPH_VERSION = GRAPH_VERSION
        module.CURRENT_EVIDENCE_OWNER_LOWER_BOUND = EVIDENCE_FLOOR
        module.CURRENT_HISTORY_REFERENCE_LOWER_BOUND = HISTORY_FLOOR
        module.COMBINED_VARIANT = module.Owner(
            LITERAL_VARIANT[1], LITERAL_VARIANT[2], LITERAL_VARIANT[3],
        )
        module.BUFFER_VARIANT = module.COMBINED_VARIANT
        module.BUFFER_FEATURE = tuple(
            module.Owner(base["OWNER_BY_NAME"][name][1],
                         base["OWNER_BY_NAME"][name][2],
                         base["OWNER_BY_NAME"][name][3])
            for name in ("v2_repair", "v2_protocol", "v2_contract")
        )
        module.FINAL_GRAPH = tuple(
            module.Owner(row[1], row[2], row[3]) for row in GRAPH.values()
        )

        def verified_context(source_pin: str, protocol_pin: str,
                             contract_pin: str) -> tuple[dict[str, object],
                                                          dict[str, object]]:
            nonlocal runtime_state
            require((source_pin, protocol_pin, contract_pin)
                    == (options["source_sha256"], options["protocol_sha256"],
                        options["contract_sha256"]),
                    "reject substituted first-party V20 build authority")
            runtime_state = {
                "originals": previous_state["originals"],
                "combined_bridge": state["literal_bytes"],
                "corrected_adapter": previous_state["corrected_adapter"],
                "low_level_v9_source": previous_state["low_level_v9_source"],
            }
            state["runtime_state"] = runtime_state
            return context, runtime_state

        original_verifier = module.verify_reproduced_phases

        def verify_actual_phases(v9: object, v7: object, workdir: str,
                                 phases: list[object],
                                 steps: list[object]) -> dict[str, object]:
            global _ROOT_CAPTURE
            require(_ROOT_CAPTURE is None
                    and type(steps) is list and len(steps) == 28,
                    "require exactly one complete actual 28-process V20 build")
            process_ids: set[int] = set()
            for index, step in enumerate(steps):
                phase = PHASES[index // len(PROCESS_NAMES)]
                require(type(step) is dict
                        and step.get("name")
                            == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                        and ("phase" not in step or step.get("phase") == phase)
                        and type(step.get("pid")) is int and step["pid"] > 0
                        and step["pid"] not in process_ids
                        and step.get("exit_status") == 0
                        and step.get("working_directory")
                            == "<FRESH_PRIVATE_TMP>/" + phase,
                        "reject omitted, forged, reordered, or failed compiler roles")
                process_ids.add(step["pid"])
            descriptor, root = v19["capture_root_descriptor"](
                v9, workdir, phases,
            )
            try:
                proof = original_verifier(v9, v7, workdir, phases, steps)
                require(type(proof) is dict and proof.get("status") == "PASS"
                        and proof.get("unique_process_count") == 28
                        and proof.get("combined_bridge_overlay_count") == 2
                        and proof.get("corrected_public_adapter_overlay_count") == 2
                        and proof.get("combined_bridge_sha256") == LITERAL_VARIANT[2]
                        and proof.get("combined_bridge_bytes") == LITERAL_VARIANT[3]
                        and proof.get("byte_identical") is True
                        and proof.get("native_libraries_loaded") == 0,
                        "preserve the complete genuine first-party 28-process ELF proof")
                after = os.fstat(descriptor)
                named = os.stat(workdir, follow_symlinks=False)
                require(stat.S_ISDIR(after.st_mode)
                        and stat.S_IMODE(after.st_mode) == 0o700
                        and after.st_uid == os.geteuid()
                        and (after.st_dev, after.st_ino)
                            == (root["device"], root["inode"])
                        and (named.st_dev, named.st_ino)
                            == (root["device"], root["inode"]),
                        "reject an actual one-pass root swapped during ELF verification")
                _ROOT_CAPTURE = {
                    "root": root,
                    "phase_count": 2,
                    "unique_process_count": len(process_ids),
                    "original_reproducibility": "PASS",
                    "compiler_process_ids": sorted(process_ids),
                }
                return proof
            finally:
                os.close(descriptor)

        module.verify_frozen_context = verified_context
        module.evidence_names = evidence_names
        module.verify_reproduced_phases = verify_actual_phases
        assert_fresh_root_receipt(BUILD_LABEL)

        class Options:
            pass

        forwarded = Options()
        for name in (
            "source_sha256", "protocol_sha256", "contract_sha256",
            "owned_source_sha256", "combined_bridge_sha256",
            "combined_bridge_bytes", "corrected_adapter_sha256",
            "corrected_adapter_bytes", "label",
        ):
            setattr(forwarded, name, options[name])
        result = module.run_build(forwarded)
        require(type(result) is dict and result.get("family") == FAMILY,
                "publish the actual complete first-party V20 build outcome")
        if result.get("status") != "PASS":
            require(result.get("failure_preserved") is True,
                    "durably preserve an actual one-pass build failure")
            return result
        return publish_root_provenance(v19, base, module, state, result, options)
    finally:
        sys.modules.pop(module_name, None)


def parse_cli(base: dict[str, object], values: list[str]) -> dict[str, object]:
    modes = ("--self-test", "--verify-frozen-context", "--render-contract", "--build")
    chosen = [name for name in modes if name in values]
    require(len(chosen) == 1 and values.count(chosen[0]) == 1,
            "require exactly one explicitly authorized V20 source or build mode")
    selected = chosen[0]
    result: dict[str, object] = {"mode": selected, "owned_source_sha256": []}
    mapping = {
        "--source-sha256": "source_sha256",
        "--protocol-sha256": "protocol_sha256",
        "--contract-sha256": "contract_sha256",
        "--label": "label",
        "--combined-bridge-sha256": "combined_bridge_sha256",
        "--combined-bridge-bytes": "combined_bridge_bytes",
        "--corrected-adapter-sha256": "corrected_adapter_sha256",
        "--corrected-adapter-bytes": "corrected_adapter_bytes",
        "--predecessor-bridge-sha256": "predecessor_bridge_sha256",
        "--predecessor-bridge-bytes": "predecessor_bridge_bytes",
        "--previous-build-receipt-sha256": "previous_build_receipt_sha256",
        "--previous-root-receipt-sha256": "previous_root_receipt_sha256",
        "--graph-summary-sha256": "graph_summary_sha256",
        "--literal-feature-source-sha256": "literal_feature_source_sha256",
        "--literal-feature-protocol-sha256": "literal_feature_protocol_sha256",
        "--literal-feature-contract-sha256": "literal_feature_contract_sha256",
        "--expanded-holdout-proposal-source-sha256":
            "expanded_holdout_proposal_source_sha256",
        "--expanded-holdout-proposal-protocol-sha256":
            "expanded_holdout_proposal_protocol_sha256",
        "--expanded-holdout-proposal-contract-sha256":
            "expanded_holdout_proposal_contract_sha256",
        "--phase1-v4-source-sha256": "phase1_v4_source_sha256",
        "--phase1-v4-protocol-sha256": "phase1_v4_protocol_sha256",
        "--phase1-v4-contract-sha256": "phase1_v4_contract_sha256",
    }
    index = 0
    while index < len(values):
        flag = values[index]
        if flag == selected:
            index += 1
            continue
        if flag == "--owned-source-sha256":
            require(index + 1 < len(values), "reject an incomplete owned Rust pin")
            result["owned_source_sha256"].append(values[index + 1])
            index += 2
            continue
        require(flag in mapping and index + 1 < len(values),
                "reject unknown, abbreviated, or incomplete V20 authority")
        name = mapping[flag]
        require(name not in result, "reject duplicate V20 authority: " + flag)
        value: object = values[index + 1]
        if name.endswith("_bytes"):
            require(type(value) is str and value.isascii() and value.isdecimal(),
                    "require exact positive decimal first-party owner bytes")
            value = int(value)
        result[name] = value
        index += 2
    for name in ("source_sha256", "protocol_sha256"):
        require(name in result, "independently caller-pin the V20 source and protocol")
        checked_hash(result[name], name)
    build_only = (
        "label", "combined_bridge_sha256", "combined_bridge_bytes",
        "corrected_adapter_sha256", "corrected_adapter_bytes",
        "predecessor_bridge_sha256", "predecessor_bridge_bytes",
        "previous_build_receipt_sha256", "previous_root_receipt_sha256",
        "graph_summary_sha256", "literal_feature_source_sha256",
        "literal_feature_protocol_sha256", "literal_feature_contract_sha256",
        "expanded_holdout_proposal_source_sha256",
        "expanded_holdout_proposal_protocol_sha256",
        "expanded_holdout_proposal_contract_sha256",
        "phase1_v4_source_sha256",
        "phase1_v4_protocol_sha256", "phase1_v4_contract_sha256",
    )
    if selected == "--render-contract":
        require("contract_sha256" not in result,
                "render the canonical machine contract before its hash exists")
    else:
        require("contract_sha256" in result,
                "independently caller-pin the complete V20 machine contract")
        checked_hash(result["contract_sha256"], "complete V20 machine contract")
    if selected != "--build":
        require(not result["owned_source_sha256"]
                and all(name not in result for name in build_only),
                "source-only modes never authorize a candidate, root, or compiler")
        return result
    require(result.get("label") == BUILD_LABEL
            and checked_label(BUILD_LABEL) == BUILD_LABEL
            and result.get("combined_bridge_sha256") == LITERAL_VARIANT[2]
            and result.get("combined_bridge_bytes") == LITERAL_VARIANT[3]
            and result.get("corrected_adapter_sha256")
                == base["CORRECTED_ADAPTER_SHA256"]
            and result.get("corrected_adapter_bytes")
                == base["CORRECTED_ADAPTER_BYTES"]
            and result.get("predecessor_bridge_sha256") == base["V2_BRIDGE_SHA256"]
            and result.get("predecessor_bridge_bytes") == base["V2_BRIDGE_BYTES"]
            and result.get("previous_build_receipt_sha256") == V19_BUILD_RECEIPT[2]
            and result.get("previous_root_receipt_sha256") == V19_ROOT_RECEIPT[2]
            and result.get("graph_summary_sha256") == GRAPH["summary"][2]
            and result.get("literal_feature_source_sha256")
                == LITERAL_FEATURE["source"][2]
            and result.get("literal_feature_protocol_sha256")
                == LITERAL_FEATURE["protocol"][2]
            and result.get("literal_feature_contract_sha256")
                == LITERAL_FEATURE["contract"][2]
            and result.get("expanded_holdout_proposal_source_sha256")
                == EXPANDED_HOLDOUT_PROPOSAL["source"][2]
            and result.get("expanded_holdout_proposal_protocol_sha256")
                == EXPANDED_HOLDOUT_PROPOSAL["protocol"][2]
            and result.get("expanded_holdout_proposal_contract_sha256")
                == EXPANDED_HOLDOUT_PROPOSAL["contract"][2],
            "independently caller-pin the actual V19 receipts and exact one-pass overlay")
    for role, key in (
        ("source", "phase1_v4_source_sha256"),
        ("protocol", "phase1_v4_protocol_sha256"),
        ("contract", "phase1_v4_contract_sha256"),
    ):
        require(result.get(key) == V19_PHASE1[role][2],
                "independently caller-pin all passing frozen phase-one oracle owners")
    expected = {
        base["OWNER_BY_NAME"][name][1]
        + "=" + base["OWNER_BY_NAME"][name][2]
        for name in base["RUST_SOURCE_NAMES"]
    }
    provided = result["owned_source_sha256"]
    require(type(provided) is list and len(provided) == 9
            and set(provided) == expected,
            "independently caller-pin exactly nine canonical first-party Rust sources")
    return result


V19_PHASE1 = {
    "source": (
        "phase1_v4_source", "tools/verify_owned_p0_completeness_v4.py",
        "8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d",
        29094, DEVICE, 428927,
    ),
    "protocol": (
        "phase1_v4_protocol", "oracle/phase1/P0-COMPLETENESS-V4.md",
        "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
        4261, DEVICE, 524712,
    ),
    "contract": (
        "phase1_v4_contract", "oracle/phase1/p0-completeness-v4.json",
        "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
        34875, DEVICE, 524713,
    ),
}


def main() -> int:
    try:
        verify_runtime()
        previous = bootstrap_v19()
        base = load_base(previous)
        options = parse_cli(base, list(sys.argv[1:]))
        mode = options["mode"]
        if mode != "--build":
            base["install_wall"]()
        if mode == "--render-contract":
            _context, state = collect_context(
                previous, base, options["source_sha256"],
                options["protocol_sha256"],
            )
            result = contract_document(
                base, options["source_sha256"], options["protocol_sha256"], state,
            )
        elif mode == "--verify-frozen-context":
            result, _state = collect_context(
                previous, base, options["source_sha256"],
                options["protocol_sha256"], options["contract_sha256"],
            )
        elif mode == "--self-test":
            result = self_test(
                previous, base, options["source_sha256"],
                options["protocol_sha256"], options["contract_sha256"],
            )
        else:
            result = run_build(previous, base, options)
        encoded = canonical(base, result)
        require(0 < len(encoded) <= MAX_OWNER_BYTES,
                "bound the complete canonical one-pass Rust build result")
        sys.stdout.buffer.write(encoded)
        sys.stdout.buffer.flush()
        return 0 if mode == "--render-contract" or result.get("status") == "PASS" else 1
    except Exception as error:
        result = {
            "schema": SCHEMA + "-entry-failure",
            "status": "FAIL",
            "version": VERSION,
            "family": FAMILY,
            "error_type": type(error).__name__,
            "error_message": str(error)[:8192],
            **boundary(),
        }
        try:
            if "base" in locals():
                sys.stdout.buffer.write(canonical(base, result))
                sys.stdout.buffer.flush()
            else:
                sys.stdout.write(
                    '{"schema":"' + SCHEMA
                    + '-entry-failure","status":"FAIL","error_type":"'
                    + type(error).__name__ + '"}\n'
                )
                sys.stdout.flush()
        except (OSError, ValueError, TypeError):
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
