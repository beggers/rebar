#!/usr/bin/env python3
"""Authenticate an unopened, source-only successor holdout proposal."""

from __future__ import annotations

import ast
import hashlib
import os
import stat
import sys


SCHEMA = "rebar-expanded-sealed-holdout-pre-phase3-proposal-v2"
SOURCE_RELATIVE = "tools/verify_expanded_sealed_holdout_v2.py"
PROTOCOL_RELATIVE = "oracle/phase3/EXPANDED-SEALED-HOLDOUT-V2.md"
CONTRACT_RELATIVE = "oracle/phase3/expanded-sealed-holdout-v2.json"
PREVIOUS_CONTRACT_RELATIVE = "oracle/phase3/expanded-sealed-holdout-v1.json"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
MAX_PUBLIC_SOURCE_BYTES = 131_072
JSON_FILENAME = "<rebar-expanded-sealed-holdout-v2-public-json>"
HEX = frozenset("0123456789abcdef")

OPERATIONS = (
    "fresh_compile_search",
    "warm_cached_compile_search",
    "module_search",
    "pattern_search",
    "module_match",
    "pattern_match",
    "module_fullmatch",
    "pattern_fullmatch",
    "module_findall",
    "pattern_findall",
    "module_finditer",
    "pattern_finditer",
    "module_split_keyword",
    "pattern_split_keyword",
    "module_split_positional",
    "pattern_split_positional",
    "module_sub_literal",
    "pattern_sub_literal",
    "module_sub_callable",
    "pattern_sub_callable",
    "module_subn_literal",
    "pattern_subn_literal",
    "module_subn_callable",
    "pattern_subn_callable",
    "module_sub_positional",
    "pattern_sub_positional",
    "module_subn_positional",
    "pattern_subn_positional",
    "scanner_search",
    "scanner_match",
    "scanner_repeated_search",
    "scanner_repeated_match",
    "lexicon_scan",
    "lexicon_scan_callback",
    "match_groups",
    "match_expand",
    "fresh_compile_match",
    "warm_cached_compile_match",
    "compile_cold_after_purge_search",
    "compile_hot_repeated_search",
    "compile_cache_hit_same_flags_search",
    "compile_cache_miss_distinct_flags_search",
    "compile_cache_churn_below_capacity_search",
    "compile_cache_churn_at_capacity_search",
    "compile_cache_churn_above_capacity_search",
    "compile_cache_eviction_then_recompile_search",
    "compile_purge_then_recompile_search",
    "compile_repeated_purge_then_search",
    "compile_invalid_pattern_then_valid_subject_search",
    "compile_invalid_flag_then_valid_subject_search",
    "compile_type_valid_locale_or_ascii_then_subject_search",
    "compile_type_valid_unicode_or_ascii_flag_then_subject_search",
    "module_search_positional_flags",
    "module_search_keyword_flags",
    "pattern_search_pos",
    "pattern_search_pos_endpos",
    "module_match_positional_flags",
    "pattern_match_pos",
    "pattern_match_pos_endpos",
    "module_fullmatch_positional_flags",
    "pattern_fullmatch_pos",
    "pattern_fullmatch_pos_endpos",
    "module_findall_positional_flags",
    "pattern_findall_pos",
    "pattern_findall_pos_endpos",
    "module_finditer_first_result",
    "module_finditer_exhausted",
    "pattern_finditer_first_result",
    "pattern_finditer_exhausted",
    "module_split_maxsplit_zero",
    "module_split_maxsplit_one",
    "module_split_capture_retention",
    "pattern_split_capture_retention",
    "module_sub_literal_count_zero",
    "module_sub_literal_count_one",
    "pattern_sub_literal_count_one",
    "module_sub_template_backreference",
    "pattern_sub_template_named_backreference",
    "module_sub_callable_side_effects",
    "pattern_sub_callable_side_effects",
    "module_sub_callable_raises",
    "pattern_sub_callable_raises",
    "module_subn_callable_raises",
    "pattern_subn_callable_raises",
    "scanner_search_empty_advance",
    "scanner_match_empty_advance",
    "scanner_search_exhausted",
    "scanner_match_exhausted",
    "lexicon_scan_mixed_tokens",
    "lexicon_scan_unmatched_remainder",
    "lexicon_scan_callback_side_effects",
    "lexicon_scan_callback_raises",
    "match_group_positional",
    "match_group_named",
    "match_groupdict_default",
    "match_groups_default",
)

PATTERN_FAMILIES = (
    "single_literal",
    "multiple_character_literal",
    "anchored_literal_prefix",
    "disjoint_alternation",
    "overlapping_alternation",
    "greedy_unbounded_repeat",
    "lazy_unbounded_repeat",
    "bounded_repeat",
    "possessive_repeat",
    "atomic_group",
    "positive_character_class",
    "negative_character_class",
    "predefined_categories_and_type_valid_flags",
    "start_anchor",
    "end_anchor",
    "word_boundary",
    "numbered_capture",
    "named_capture",
    "numbered_backreference",
    "named_backreference",
    "positive_lookahead",
    "negative_lookahead",
    "fixed_width_positive_or_negative_lookbehind",
    "conditionals_or_correctly_advancing_zero_length_matches",
    "nested_alternation_tree",
    "alternation_shared_prefix",
    "alternation_shared_suffix",
    "case_insensitive_ascii_fold",
    "case_insensitive_unicode_or_type_valid_ascii_fold",
    "scoped_inline_flags",
    "global_inline_flags_and_verbose_comments",
    "multiline_and_dotall_interactions",
    "type_valid_unicode_or_bytes_word_digit_space_classes",
    "type_valid_locale_or_ascii_character_classes",
    "astral_surrogate_or_type_valid_encoded_literals",
    "combining_marks_or_type_valid_encoded_sequences",
    "zero_width_empty_progress",
    "nested_bounded_repeat",
    "nested_lazy_repeat",
    "deeply_nested_group_structure",
    "many_numbered_captures",
    "many_named_captures",
    "conditional_group_existence",
    "nested_positive_negative_lookarounds",
    "fixed_width_lookbehind_alternations",
    "large_character_class_ranges",
    "escaped_literal_and_template_syntax",
    "adversarial_repeat_shape_with_frozen_safety_bounds",
)

SUBJECT_REPRESENTATIONS = (
    "str_ascii",
    "str_unicode",
    "bytes",
    "bytearray",
    "memoryview_readonly_contiguous",
    "memoryview_writable_contiguous",
    "array_unsigned_byte_contiguous",
    "array_signed_byte_contiguous",
    "mmap_readonly_contiguous",
    "mmap_writable_contiguous",
)

LIFECYCLE_SLOTS = (
    "operation_valid_cold_compile_after_purge",
    "operation_valid_hot_compile_cache_hit",
    "operation_valid_compiled_object_reuse",
    "operation_valid_cache_near_capacity",
    "operation_valid_cache_eviction_churn",
    "operation_valid_explicit_purge_recovery",
    "operation_valid_existing_iterator_scanner_or_match_state",
    "operation_valid_failure_callback_and_cleanup_state",
)

SUBJECT_SCALES = (
    "tiny_0_to_16",
    "small_17_to_64",
    "medium_65_to_256",
    "large_257_to_4096",
    "very_large_4097_to_65536",
    "huge_65537_to_1048576",
)

TRANSACTION_PUBLIC_INVOCATIONS_BY_SUBJECT_SCALE = (4, 5, 6, 7, 8, 9)

MATCH_DENSITIES = (
    "no_match_full_scan",
    "single_or_sparse_match",
    "dense_nonoverlapping_matches",
    "clustered_overlapping_or_zero_width_progress",
)

CORPUS_FAMILIES = (
    "apache_and_nginx_access_logs",
    "structured_json_event_streams",
    "python_source_and_docstrings",
    "c_cpp_rust_source_tokens",
    "html_xml_markup_and_visible_text",
    "csv_and_tsv_tabular_records",
    "email_headers_and_message_bodies",
    "uri_paths_queries_and_percent_escapes",
    "filesystem_paths_and_shell_transcripts",
    "unicode_multilingual_natural_language",
    "combining_marks_graphemes_and_normalization",
    "emoji_astral_and_surrogate_edges",
    "genomic_ascii_sequence_windows",
    "network_protocol_and_binary_frames",
    "stack_traces_and_exception_text",
    "synthetic_security_redaction_token_shapes",
)

OUTCOME_FAMILIES = (
    "exact_match_result_and_captures",
    "correct_no_match_or_exhaustion",
    "correct_empty_and_zero_width_progress",
    "correct_capture_split_and_replacement_output",
    "correct_expected_compile_or_argument_exception",
    "correct_callback_side_effect_and_exception",
    "correct_warning_and_exception_metadata",
    "correct_resource_cleanup_buffer_release_and_lifetime",
)

BOUNDARY_CONTROL_FAMILIES = (
    "matched_first_party_empty_call",
    "python_argument_marshalling",
    "buffer_export_acquire_release",
    "pattern_wrapper_entry_exit",
    "subject_view_pin_unpin",
    "callback_trampoline_entry_exit",
    "match_result_materialization",
    "exception_translation_and_cleanup",
)

MEMORY_MEASUREMENT_FAMILIES = (
    "python_visible_allocation_count",
    "python_visible_allocation_bytes_and_peak",
    "authenticated_first_party_native_allocation_count",
    "authenticated_first_party_native_allocation_bytes_and_peak",
    "first_party_arena_retained_bytes",
    "resident_set_growth_under_matched_isolation",
    "buffer_export_pin_lifetime",
    "failure_callback_and_exception_cleanup",
)

PARTICIPANT_EQUALITY_CONDITIONS = (
    "pinned_interpreter_and_stdlib",
    "same_public_python_operation_and_arguments",
    "same_pattern_subject_and_replacement_content",
    "same_pattern_flags_positions_and_end_positions",
    "same_cache_state_and_compile_lifecycle",
    "same_buffer_mutability_exporter_and_lifetime",
    "same_callback_order_side_effects_and_errors",
    "same_process_isolation_cpu_affinity_and_priority",
    "same_clock_and_complete_timed_interval",
    "same_preflight_and_per_invocation_correctness_gate",
    "same_randomized_case_order_and_full_participant_rotation",
    "same_native_boundary_output_creation_and_cleanup",
)

PROHIBITED_DELEGATES = (
    "stdlib_re",
    "stdlib__sre",
    "PCRE",
    "PCRE2",
    "RE2",
    "Rust_regex",
    "Oniguruma",
    "Hyperscan",
    "Boost_regex",
    "std_regex",
    "POSIX_regex",
    "ICU_regex",
    "Tcl_regex",
    "JavaScript_regex",
    "WebAssembly_regex",
    "another_candidate",
    "dynamic_matcher_plugin",
    "external_process_matcher",
    "network_matcher",
    "cached_oracle_answers",
    "hidden_fallback",
)

# Every owner is a previously published, small, human-readable source file.
# No evidence archive, generated case, hidden input, secret, or executable is read.
PUBLIC_SOURCE_PINS = (
    (
        "GOAL.md",
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    ),
    (
        "docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md",
        "f7509c60065860d30aad7939dda76f53e1c9f6ebb9db5e1298d0881f63a016eb",
    ),
    (
        "oracle/phase1/P0-COMPLETENESS-V4.md",
        "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
    ),
    (
        "oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md",
        "1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8",
    ),
    (
        "oracle/phase1/P0-PUBLIC-ENTRYPOINT-IMPORT-V1.md",
        "01ace52c6285142733bdcb2b4556feb43226e01c8b181b84019b8fa8c42697c0",
    ),
    (
        "oracle/phase1/P0-LARGE-INPUT-INDEXING-V1.md",
        "0a640ee044c52394fa897d0221d51dfc3d85e9abb95608367698f11fba8ca879",
    ),
    (
        "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md",
        "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4",
    ),
    (
        "oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md",
        "80a1de729c067da36648dcfb9751f7bd3833ff561956df9ad82fc6106a19a16b",
    ),
    (
        "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md",
        "2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c",
    ),
    (
        "tools/verify_expanded_sealed_holdout_v1.py",
        "3dd9abcbd7a87486186ee8da804de595e65d79020a3fe33413d0157dde4f3309",
    ),
    (
        "oracle/phase3/EXPANDED-SEALED-HOLDOUT-V1.md",
        "818f1636d87ae721912f04a3fc8294ac04a59dff4a272319aa29a393f52a4fd4",
    ),
    (
        "oracle/phase3/expanded-sealed-holdout-v1.json",
        "676aac4f48c9404f5253c89b692efde5c425170f8d9f152b4f85b3e2a5225a76",
    ),
)

EXPECTED_SCALARS = {
    "schema": SCHEMA,
    "proposal_status": "PRE-PHASE-3 PROPOSAL",
    "final_protocol_status": "NOT FROZEN",
    "generator_status": "NOT FROZEN",
    "secret_status": "NOT GENERATED",
    "case_status": "NOT GENERATED; NOT OPENED",
    "timing_status": "NOT RUN; NOT MEASURED",
    "memory_status": "NOT RUN; NOT MEASURED",
    "runtime_independence_status": "NOT ESTABLISHED",
    "winner_status": "NOT SELECTED",
    "phase3_gate_status": "BLOCKED UNTIL THREE DISTINCT COMPLETE-P0 NO-DELEGATION PASSES",
    "legal_domain_status": "NOT FROZEN; REQUIRED FOR EVERY CROSSED CELL BEFORE GENERATION",
    "invalid_or_inapplicable_cross_cell_policy": "REJECT ENTIRE GENERATION; NEVER DROP OR SUBSTITUTE",
    "crossed_axis_materiality_policy": "EVERY CROSSED AXIS AFFECTS A REAL PUBLIC-OPERATION TRANSACTION",
    "typed_pattern_policy": "TYPE-VALID STR OR BYTES PATTERN FOR EVERY SUBJECT CELL",
    "corpus_transform_policy": "TYPE-PRESERVING CORPUS WINDOWS PASSED TO EVERY PUBLIC OPERATION",
    "match_density_policy": "EXACT LEGAL NO-MATCH SPARSE DENSE OR CLUSTERED WINDOW DISTRIBUTIONS",
    "qualified_independent_family_count": 0,
    "minimum_qualified_independent_family_count": 3,
    "original_p0_case_count": 31_237,
    "original_p0_suite_count": 13,
    "named_private_waiver_count": 13,
    "separate_differential_case_count": 8_244,
    "pinned_python_version": "3.14.6",
    "pinned_python_path": PINNED_PYTHON,
    "pinned_python_sha256": PINNED_PYTHON_SHA256,
    "preserved_original_proposal_case_count": 4_194_304,
    "preserved_immediate_previous_proposal_case_count": 14_155_776,
    "preserved_immediate_previous_operation_count": 36,
    "preserved_immediate_previous_pattern_family_count": 24,
    "case_count": 141_557_760,
    "timed_case_count": 141_557_760,
    "cases_per_stratum": 16,
    "operation_count": 96,
    "pattern_family_count": 48,
    "subject_representation_count": 10,
    "lifecycle_count": 8,
    "subject_scale_count": 6,
    "match_density_count": 4,
    "corpus_family_count": 16,
    "stratum_count": 8_847_360,
    "cases_per_operation": 1_474_560,
    "cases_per_pattern_family": 2_949_120,
    "cases_per_subject_representation": 14_155_776,
    "cases_per_lifecycle": 17_694_720,
    "cases_per_subject_scale": 23_592_960,
    "cases_per_match_density": 35_389_440,
    "cases_per_corpus_family": 8_847_360,
    "ascii_str_case_count": 14_155_776,
    "unicode_str_case_count": 14_155_776,
    "readonly_memoryview_case_count": 14_155_776,
    "writable_memoryview_case_count": 14_155_776,
    "readonly_mmap_case_count": 14_155_776,
    "writable_mmap_case_count": 14_155_776,
    "maximum_subject_scale_inclusive": 1_048_576,
    "minimum_public_operations_per_timed_transaction": 4,
    "maximum_public_operations_per_timed_transaction": 9,
    "public_operation_invocations_per_participant_unpaired": 920_125_440,
    "preflight_public_operation_invocation_count": 3_680_501_760,
    "individually_correctness_gated_public_operation_invocation_count": 88_332_042_240,
    "outcome_family_count": 8,
    "boundary_control_family_count": 8,
    "memory_measurement_family_count": 8,
    "participant_equality_condition_count": 12,
    "baseline_participant_count": 1,
    "candidate_participant_count": 3,
    "participant_count": 4,
    "paired_round_count": 24,
    "participant_orders_per_case": 24,
    "participant_occurrences_per_order_position": 6,
    "preflight_correctness_observation_count": 566_231_040,
    "individually_correctness_gated_timed_observation_count": 13_589_544_960,
    "candidate_baseline_paired_observation_count": 10_192_158_720,
    "clock_bytes_per_timed_observation": 8,
    "raw_clock_bytes_only": 108_716_359_680,
    "raw_clock_gib_numerator": 405,
    "raw_clock_gib_denominator": 4,
    "operation_family_shard_count": 4_608,
    "raw_clock_bytes_per_operation_family_shard": 23_592_960,
    "bootstrap_replicate_count": 9_999,
    "bootstrap_stratum_draws_per_candidate": 88_464_752_640,
    "multiple_comparison_hypothesis_count": 424_673_280,
    "false_discovery_rate_numerator": 5,
    "false_discovery_rate_denominator": 100,
    "memory_cases_per_stratum": 4,
    "memory_case_count": 35_389_440,
    "memory_observation_count": 141_557_760,
    "boundary_cases_per_stratum": 2,
    "boundary_case_count": 17_694_720,
    "boundary_observation_count": 70_778_880,
    "minimum_faster_case_numerator": 60,
    "minimum_faster_case_denominator": 100,
    "minimum_significantly_faster_case_count": 84_934_656,
    "minimum_lower_confidence_speedup_numerator": 3,
    "minimum_lower_confidence_speedup_denominator": 2,
    "regression_explanation_threshold_percent": 20,
}

EXPECTED_ARRAYS = {
    "operations": OPERATIONS,
    "primary_pattern_families": PATTERN_FAMILIES,
    "subject_representations": SUBJECT_REPRESENTATIONS,
    "lifecycle_slots": LIFECYCLE_SLOTS,
    "subject_scales": SUBJECT_SCALES,
    "transaction_public_invocations_by_subject_scale": (
        TRANSACTION_PUBLIC_INVOCATIONS_BY_SUBJECT_SCALE
    ),
    "match_densities": MATCH_DENSITIES,
    "corpus_families": CORPUS_FAMILIES,
    "expected_outcome_families": OUTCOME_FAMILIES,
    "boundary_control_families": BOUNDARY_CONTROL_FAMILIES,
    "memory_measurement_families": MEMORY_MEASUREMENT_FAMILIES,
    "participant_equality_conditions": PARTICIPANT_EQUALITY_CONDITIONS,
    "prohibited_matcher_delegates": PROHIBITED_DELEGATES,
}

FORBIDDEN_MODULE_PREFIXES = (
    "re",
    "_sre",
    "regex",
    "pcre",
    "pcre2",
    "re2",
    "oniguruma",
    "hyperscan",
    "candidates",
    "rebar",
    "subprocess",
    "socket",
    "ctypes",
)


class ProposalVerificationError(RuntimeError):
    """A source-only proposal, provenance pin, or phase gate was rejected."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProposalVerificationError(message)


def is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in HEX for character in value)
    )


def ensure_forbidden_modules_absent() -> None:
    for module_name in sys.modules:
        for prefix in FORBIDDEN_MODULE_PREFIXES:
            if module_name == prefix or module_name.startswith(prefix + "."):
                raise ProposalVerificationError(
                    "a matcher, candidate, process, boundary, or network module was loaded: "
                    + module_name
                )


def parse_arguments() -> tuple[str, str, str, str]:
    arguments = sys.argv[1:]
    require(len(arguments) == 7, "expected one source-only mode and three hashes")
    mode = arguments[0]
    require(
        mode in ("--self-test", "--verify-source"),
        "only --self-test and --verify-source are allowed; neither freezes a holdout",
    )
    require(
        arguments[1] == "--source-sha256"
        and arguments[3] == "--protocol-sha256"
        and arguments[5] == "--contract-sha256",
        "provide source, public proposal, and public contract hashes in that order",
    )
    for value in (arguments[2], arguments[4], arguments[6]):
        require(is_sha256(value), "every source fingerprint must be lowercase SHA-256")
    return mode, arguments[2], arguments[4], arguments[6]


def repository_root() -> str:
    actual_source = os.path.realpath(__file__)
    suffix = os.sep + SOURCE_RELATIVE.replace("/", os.sep)
    require(actual_source.endswith(suffix), "unexpected verifier source location")
    return actual_source[: -len(suffix)]


class ReadOnlyPublicSourceGuard:
    def __init__(self, allowed_paths: set[str]) -> None:
        self.allowed_paths = frozenset(allowed_paths)
        self.blocked_effect_count = 0

    def reject(self, reason: str) -> None:
        self.blocked_effect_count += 1
        raise ProposalVerificationError("source-only guard rejected " + reason)

    def __call__(self, event: str, arguments: tuple[object, ...]) -> None:
        if event == "open":
            if not arguments or not isinstance(arguments[0], (str, bytes)):
                self.reject("an unapproved file descriptor or source")
            actual_path = os.path.realpath(os.fsdecode(arguments[0]))
            if actual_path not in self.allowed_paths:
                self.reject("a candidate, executable, archive, holdout, or unpinned source")
            if len(arguments) > 1 and isinstance(arguments[1], str):
                if any(flag in arguments[1] for flag in ("w", "a", "x", "+")):
                    self.reject("a source-file write mode")
            if len(arguments) > 2 and isinstance(arguments[2], int):
                prohibited_flags = (
                    os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
                )
                if arguments[2] & prohibited_flags:
                    self.reject("a source-file write")
            return
        if event == "compile":
            if len(arguments) < 2 or arguments[1] != JSON_FILENAME:
                self.reject("unapproved dynamic compilation")
            return
        if (
            event == "import"
            or event.startswith("socket.")
            or event.startswith("subprocess.")
            or event.startswith("ctypes.")
            or event.startswith("time.")
            or event.startswith("urllib.")
            or event.startswith("http.")
            or event.startswith("mmap.")
            or event in (
                "os.system",
                "os.fork",
                "os.posix_spawn",
                "os.exec",
                "os.spawn",
                "os.remove",
                "os.rename",
                "os.mkdir",
                "os.rmdir",
                "os.chdir",
                "os.chmod",
                "os.truncate",
                "os.listdir",
                "os.scandir",
                "marshal.loads",
                "builtins.input",
                "rebar.correctness.clock",
                "cpython.run_command",
            )
        ):
            self.reject(event)


def read_authenticated_plaintext(path: str, expected_sha256: str) -> bytes:
    require(is_sha256(expected_sha256), "invalid public-source SHA-256")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode), "pinned public source is not a regular file")
        require(
            0 < identity.st_size <= MAX_PUBLIC_SOURCE_BYTES,
            "pinned public plaintext source exceeds its strict size bound",
        )
        chunks: list[bytes] = []
        remaining = identity.st_size
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            require(bool(chunk), "pinned public plaintext source was truncated")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"", "pinned public plaintext source grew")
        final_identity = os.fstat(descriptor)
        require(
            (identity.st_dev, identity.st_ino, identity.st_size, identity.st_mtime_ns)
            == (
                final_identity.st_dev,
                final_identity.st_ino,
                final_identity.st_size,
                final_identity.st_mtime_ns,
            ),
            "pinned public plaintext source changed while it was read",
        )
        content = b"".join(chunks)
        require(b"\x00" not in content, "pinned public source is not plaintext")
        try:
            content.decode("utf-8")
        except UnicodeError as error:
            raise ProposalVerificationError("pinned public source is not UTF-8 plaintext") from error
        require(
            hashlib.sha256(content).hexdigest() == expected_sha256,
            "pinned public plaintext source hash does not match: " + path,
        )
        return content
    finally:
        os.close(descriptor)


def strict_public_json(content: bytes) -> dict[str, object]:
    require(0 < len(content) <= MAX_PUBLIC_SOURCE_BYTES, "invalid public JSON size")
    require(b"\x00" not in content, "public JSON contains a zero byte")
    try:
        text = content.decode("ascii")
        tree = ast.parse(text, filename=JSON_FILENAME, mode="eval")
    except (UnicodeError, SyntaxError, ValueError) as error:
        raise ProposalVerificationError("invalid, non-ASCII public proposal JSON") from error

    node_count = 0

    def validate_node(node: ast.AST, depth: int) -> None:
        nonlocal node_count
        node_count += 1
        require(node_count <= 16_384 and depth <= 24, "public proposal JSON exceeds its bounds")
        if isinstance(node, ast.Expression):
            validate_node(node.body, depth + 1)
        elif isinstance(node, ast.Dict):
            seen: set[str] = set()
            for key, value in zip(node.keys, node.values, strict=True):
                require(
                    isinstance(key, ast.Constant) and type(key.value) is str,
                    "public proposal object keys must be strings",
                )
                require(key.value not in seen, "duplicate public proposal JSON object key")
                seen.add(key.value)
                validate_node(value, depth + 1)
        elif isinstance(node, ast.List):
            for item in node.elts:
                validate_node(item, depth + 1)
        elif isinstance(node, ast.Constant):
            require(
                type(node.value) in (str, int),
                "public proposal JSON permits only strings and nonnegative integers",
            )
            if type(node.value) is int:
                require(0 <= node.value < 1 << 63, "public proposal integer is out of range")
        else:
            raise ProposalVerificationError("public proposal JSON contains executable syntax")

    validate_node(tree, 0)
    result = ast.literal_eval(tree)
    require(type(result) is dict, "public proposal JSON root must be an object")
    return result


def validate_previous_contract(previous: dict[str, object]) -> None:
    required_scalars = {
        "schema": "rebar-expanded-sealed-holdout-pre-phase3-proposal-v1",
        "proposal_status": "PRE-PHASE-3 PROPOSAL",
        "final_protocol_status": "NOT FROZEN",
        "generator_status": "NOT FROZEN",
        "secret_status": "NOT GENERATED",
        "case_status": "NOT GENERATED; NOT OPENED",
        "timing_status": "NOT RUN; NOT MEASURED",
        "qualified_independent_family_count": 0,
        "minimum_qualified_independent_family_count": 3,
        "preserved_previous_proposal_case_count": 4_194_304,
        "case_count": 14_155_776,
        "timed_case_count": 14_155_776,
        "operation_count": 36,
        "pattern_family_count": 24,
        "subject_type_count": 4,
        "lifecycle_count": 4,
        "cases_per_stratum": 1_024,
    }
    for key, value in required_scalars.items():
        require(
            key in previous and type(previous[key]) is type(value) and previous[key] == value,
            "the authenticated 14,155,776-case proposal or its three-candidate gate changed: "
            + key,
        )
    operations = previous.get("operations")
    families = previous.get("primary_pattern_families")
    require(type(operations) is list, "previous proposal operations are not a list")
    require(type(families) is list, "previous proposal pattern families are not a list")
    require(tuple(operations) == OPERATIONS[:36], "previous proposal operations were not preserved")
    require(tuple(families) == PATTERN_FAMILIES[:24], "previous pattern families were not preserved")
    require(
        previous["case_count"]
        == previous["operation_count"]
        * previous["pattern_family_count"]
        * previous["subject_type_count"]
        * previous["lifecycle_count"]
        * previous["cases_per_stratum"],
        "the previous proposal denominator is internally inconsistent",
    )


def validate_contract(contract: dict[str, object]) -> None:
    expected_keys = set(EXPECTED_SCALARS)
    expected_keys.update(EXPECTED_ARRAYS)
    expected_keys.add("required_public_source_pins")
    require(
        set(contract) == expected_keys,
        "successor proposal fields were added, omitted, or changed",
    )

    for key, expected in EXPECTED_SCALARS.items():
        actual = contract[key]
        require(type(actual) is type(expected), "proposal field has the wrong type: " + key)
        require(actual == expected, "proposal field has the wrong value: " + key)

    for key, expected in EXPECTED_ARRAYS.items():
        actual = contract[key]
        require(type(actual) is list, "proposal axis must be a list: " + key)
        require(tuple(actual) == expected, "proposal axis changed: " + key)
        require(len(set(actual)) == len(actual), "proposal axis contains duplicates: " + key)

    owners = contract["required_public_source_pins"]
    require(type(owners) is list, "public plaintext source pins must be a list")
    observed: list[tuple[str, str]] = []
    for owner in owners:
        require(type(owner) is dict, "public plaintext source pin must be an object")
        require(set(owner) == {"path", "sha256"}, "public plaintext source pin shape changed")
        require(type(owner["path"]) is str, "public plaintext source path is not a string")
        require(is_sha256(owner["sha256"]), "public plaintext source pin is not SHA-256")
        observed.append((owner["path"], owner["sha256"]))
    require(tuple(observed) == PUBLIC_SOURCE_PINS, "immutable prior proposal/source pins changed")

    axis_specs = (
        ("operation_count", "operations", "cases_per_operation"),
        ("pattern_family_count", "primary_pattern_families", "cases_per_pattern_family"),
        (
            "subject_representation_count",
            "subject_representations",
            "cases_per_subject_representation",
        ),
        ("lifecycle_count", "lifecycle_slots", "cases_per_lifecycle"),
        ("subject_scale_count", "subject_scales", "cases_per_subject_scale"),
        ("match_density_count", "match_densities", "cases_per_match_density"),
        ("corpus_family_count", "corpus_families", "cases_per_corpus_family"),
    )
    for count_key, axis_key, weight_key in axis_specs:
        require(contract[count_key] == len(contract[axis_key]), "axis count changed: " + axis_key)
        require(
            contract[weight_key] * contract[count_key] == contract["case_count"],
            "case weights, full-axis participation, or denominator changed: " + axis_key,
        )

    transaction_counts = contract["transaction_public_invocations_by_subject_scale"]
    require(
        len(transaction_counts) == len(SUBJECT_SCALES),
        "each subject scale must own exactly one public-transaction invocation count",
    )
    require(
        all(type(count) is int for count in transaction_counts),
        "public-transaction invocation counts must be exact integers",
    )
    require(
        all(
            previous_count < current_count
            for previous_count, current_count in zip(
                transaction_counts, transaction_counts[1:], strict=False
            )
        ),
        "subject scale must change real public-operation invocation work monotonically",
    )
    require(
        transaction_counts[0] == contract["minimum_public_operations_per_timed_transaction"]
        and transaction_counts[-1]
        == contract["maximum_public_operations_per_timed_transaction"]
        and transaction_counts[0] >= 4,
        "a dense/clustered/no-match/sparse transaction requires at least four actual calls",
    )

    stratum_count = (
        len(OPERATIONS)
        * len(PATTERN_FAMILIES)
        * len(SUBJECT_REPRESENTATIONS)
        * len(LIFECYCLE_SLOTS)
        * len(SUBJECT_SCALES)
        * len(MATCH_DENSITIES)
    )
    require(contract["stratum_count"] == stratum_count, "complete cross-product stratum count changed")
    require(
        contract["cases_per_stratum"] == len(CORPUS_FAMILIES),
        "every realistic corpus must occur exactly once in every complete stratum",
    )
    cases = stratum_count * len(CORPUS_FAMILIES)
    require(contract["case_count"] == cases, "full independent case denominator changed")
    require(contract["timed_case_count"] == cases, "a timing subsample or silent drop was introduced")
    require(
        cases == contract["preserved_immediate_previous_proposal_case_count"] * 10,
        "the exact ten-times expansion over the immutable 14,155,776-case proposal changed",
    )
    require(
        cases * 4 == contract["preserved_original_proposal_case_count"] * 135,
        "the 33.75-times expansion over the immutable 4,194,304-case proposal changed",
    )
    require(
        contract["preserved_immediate_previous_operation_count"] == 36
        and contract["preserved_immediate_previous_pattern_family_count"] == 24,
        "previous proposal operation or pattern-family preservation changed",
    )
    for field in (
        "ascii_str_case_count",
        "unicode_str_case_count",
        "readonly_memoryview_case_count",
        "writable_memoryview_case_count",
        "readonly_mmap_case_count",
        "writable_mmap_case_count",
    ):
        require(
            contract[field] == contract["cases_per_subject_representation"],
            "text, Unicode, exporter, or read/write subject balance changed: " + field,
        )

    for count_key, axis_key in (
        ("outcome_family_count", "expected_outcome_families"),
        ("boundary_control_family_count", "boundary_control_families"),
        ("memory_measurement_family_count", "memory_measurement_families"),
        ("participant_equality_condition_count", "participant_equality_conditions"),
    ):
        require(contract[count_key] == len(contract[axis_key]), "published control count changed")

    require(
        contract["qualified_independent_family_count"] == 0
        and contract["minimum_qualified_independent_family_count"] == 3
        and contract["phase3_gate_status"]
        == "BLOCKED UNTIL THREE DISTINCT COMPLETE-P0 NO-DELEGATION PASSES",
        "the distinct complete-P0 and live no-delegation phase-three gate was weakened",
    )
    participants = contract["baseline_participant_count"] + contract["candidate_participant_count"]
    rounds = contract["paired_round_count"]
    require(participants == contract["participant_count"] == 4, "equal-baseline participant count changed")
    require(rounds == 24, "four-participant paired-randomization round count changed")
    permutation_count = 1
    for value in range(2, participants + 1):
        permutation_count *= value
    require(
        contract["participant_orders_per_case"] == rounds == permutation_count,
        "full, exactly-once participant permutation balance changed",
    )
    require(
        contract["participant_occurrences_per_order_position"] * participants == rounds,
        "participant order-position balance changed",
    )

    timed_observations = cases * rounds * participants
    unpaired_public_invocations = contract["cases_per_subject_scale"] * sum(
        transaction_counts
    )
    require(
        contract["public_operation_invocations_per_participant_unpaired"]
        == unpaired_public_invocations,
        "scale-sensitive public-operation transaction invocation denominator changed",
    )
    require(
        contract["preflight_public_operation_invocation_count"]
        == unpaired_public_invocations * participants,
        "preflight must check every real public invocation in every participant transaction",
    )
    require(
        contract["individually_correctness_gated_public_operation_invocation_count"]
        == unpaired_public_invocations * rounds * participants,
        "timed transactions omitted an actual public call, scale, candidate, or paired round",
    )
    require(
        contract["preflight_correctness_observation_count"] == cases * participants,
        "complete baseline-and-candidate correctness preflight denominator changed",
    )
    require(
        contract["individually_correctness_gated_timed_observation_count"] == timed_observations,
        "individually correctness-gated full-call timing denominator changed",
    )
    require(
        contract["candidate_baseline_paired_observation_count"]
        == cases * rounds * contract["candidate_participant_count"],
        "same-case candidate-to-baseline paired observation count changed",
    )
    raw_clock_bytes = timed_observations * contract["clock_bytes_per_timed_observation"]
    require(contract["raw_clock_bytes_only"] == raw_clock_bytes, "raw clock-byte denominator changed")
    require(
        raw_clock_bytes * contract["raw_clock_gib_denominator"]
        == contract["raw_clock_gib_numerator"] * 1024**3,
        "raw eight-byte clock-only GiB accounting changed",
    )
    shard_count = len(OPERATIONS) * len(PATTERN_FAMILIES)
    require(contract["operation_family_shard_count"] == shard_count, "raw-clock shard count changed")
    require(
        contract["raw_clock_bytes_per_operation_family_shard"] * shard_count == raw_clock_bytes,
        "raw-clock shards omit a participant, round, case, or axis",
    )
    require(
        contract["bootstrap_stratum_draws_per_candidate"]
        == contract["bootstrap_replicate_count"] * stratum_count,
        "prospective full-stratum bootstrap denominator changed",
    )
    require(
        contract["multiple_comparison_hypothesis_count"]
        == cases * contract["candidate_participant_count"],
        "multiple-comparison denominator omitted a case or candidate",
    )
    for cohort in ("memory", "boundary"):
        cohort_cases = stratum_count * contract[cohort + "_cases_per_stratum"]
        require(
            contract[cohort + "_case_count"] == cohort_cases,
            cohort + " balanced secondary-cohort case count changed",
        )
        require(
            contract[cohort + "_observation_count"] == cohort_cases * participants,
            cohort + " balanced secondary-cohort participant count changed",
        )
        require(cohort_cases <= cases, cohort + " cohort exceeds the complete case denominator")
    faster_numerator = cases * contract["minimum_faster_case_numerator"]
    faster_denominator = contract["minimum_faster_case_denominator"]
    minimum_faster = (faster_numerator + faster_denominator - 1) // faster_denominator
    require(
        contract["minimum_significantly_faster_case_count"] == minimum_faster,
        "corrected 60-percent complete-denominator winner threshold changed",
    )


def validate_protocol(protocol: bytes) -> None:
    required = (
        b"PRE-PHASE-3 PROPOSAL",
        b"NOT FROZEN",
        b"NOT GENERATED",
        b"NOT OPENED",
        b"NOT RUN",
        b"NOT MEASURED",
        b"4,194,304",
        b"14,155,776",
        b"141,557,760",
        b"96 operations",
        b"48 primary pattern families",
        b"10 subject representations",
        b"8 operation-valid lifecycle states",
        b"6 subject scales",
        b"4 match-density classes",
        b"16 realistic corpus families",
        b"8,847,360 complete strata",
        b"13,589,544,960",
        b"10,192,158,720",
        b"108,716,359,680",
        b"101.25 GiB",
        b"88,332,042,240",
        b"424,673,280",
        b"84,934,656",
        b"three distinct independently authored candidates",
        b"complete original 31,237-case P0 suite",
        b"live runtime no-delegation",
        b"freeze, generate, or open",
        b"4, 5, 6, 7, 8, and 9",
        b"type-valid operation-specific equivalent",
        b"reject the entire generation",
        b"--verify-source",
        b"--self-test",
    )
    for token in required:
        require(token in protocol, "public successor proposal omits: " + token.decode("ascii"))


def assert_rejected(function: object, label: str) -> None:
    try:
        function()
    except ProposalVerificationError:
        return
    raise ProposalVerificationError("hostile source-only self-test was not rejected: " + label)


def run_self_tests(
    contract: dict[str, object],
    previous: dict[str, object],
    protocol: bytes,
    guard: ReadOnlyPublicSourceGuard,
) -> int:
    checks = 0
    validate_contract(contract)
    validate_previous_contract(previous)
    validate_protocol(protocol)
    checks += 3

    for hostile, label in (
        (b'{"schema":"first","schema":"second"}', "duplicate public JSON keys"),
        (b'{"schema": __import__("re")}', "executable public JSON syntax"),
        (b'{"schema": true}', "public JSON boolean masquerading as an integer"),
        (b'{"schema": -1}', "negative public JSON integer"),
        (b'{"schema": null}', "public JSON null"),
    ):
        assert_rejected(lambda value=hostile: strict_public_json(value), label)
        checks += 1

    for key, hostile in (
        ("final_protocol_status", "FROZEN"),
        ("generator_status", "FROZEN"),
        ("secret_status", "GENERATED"),
        ("case_status", "GENERATED; OPENED"),
        ("timing_status", "RUN; MEASURED"),
        ("memory_status", "RUN; MEASURED"),
        ("runtime_independence_status", "ESTABLISHED"),
        ("winner_status", "SELECTED"),
        ("phase3_gate_status", "OPEN AFTER TWO CANDIDATES"),
        ("legal_domain_status", "FROZEN AND GENERATED"),
        ("invalid_or_inapplicable_cross_cell_policy", "DROP INVALID CELLS"),
        ("crossed_axis_materiality_policy", "ALLOW IGNORED AXES"),
        ("typed_pattern_policy", "ALLOW INVALID STR/BYTES COMBINATIONS"),
        ("corpus_transform_policy", "IGNORE SUBJECT CORPUS"),
        ("match_density_policy", "COUNT IMPOSSIBLE EMPTY DENSE CELLS"),
        ("minimum_qualified_independent_family_count", 2),
        ("qualified_independent_family_count", 3),
        ("preserved_original_proposal_case_count", 14_155_776),
        ("preserved_immediate_previous_proposal_case_count", 4_194_304),
        ("case_count", 14_155_776),
        ("timed_case_count", 14_155_776),
        ("stratum_count", 8_847_359),
        ("cases_per_stratum", 15),
        ("operation_count", 95),
        ("subject_representation_count", 9),
        ("readonly_memoryview_case_count", 0),
        ("writable_mmap_case_count", 0),
        ("minimum_public_operations_per_timed_transaction", 1),
        ("maximum_public_operations_per_timed_transaction", 4),
        ("public_operation_invocations_per_participant_unpaired", 141_557_760),
        ("preflight_public_operation_invocation_count", 566_231_040),
        ("individually_correctness_gated_public_operation_invocation_count", 13_589_544_960),
        ("baseline_participant_count", 0),
        ("candidate_participant_count", 2),
        ("participant_count", 5),
        ("paired_round_count", 12),
        ("preflight_correctness_observation_count", 141_557_760),
        ("individually_correctness_gated_timed_observation_count", 141_557_760),
        ("candidate_baseline_paired_observation_count", 0),
        ("raw_clock_bytes_only", 10_871_635_968),
        ("multiple_comparison_hypothesis_count", 141_557_760),
        ("memory_case_count", 0),
        ("boundary_case_count", 0),
        ("minimum_significantly_faster_case_count", 84_934_655),
        ("false_discovery_rate_numerator", 100),
    ):
        mutated = dict(contract)
        mutated[key] = hostile
        assert_rejected(lambda value=mutated: validate_contract(value), key)
        checks += 1

    for axis_name in (
        "operations",
        "primary_pattern_families",
        "subject_representations",
        "lifecycle_slots",
        "subject_scales",
        "transaction_public_invocations_by_subject_scale",
        "match_densities",
        "corpus_families",
        "expected_outcome_families",
        "boundary_control_families",
        "memory_measurement_families",
        "participant_equality_conditions",
        "prohibited_matcher_delegates",
    ):
        duplicated = list(contract[axis_name])
        duplicated[-1] = duplicated[0]
        mutated = dict(contract)
        mutated[axis_name] = duplicated
        assert_rejected(lambda value=mutated: validate_contract(value), "duplicate " + axis_name)
        checks += 1

    removed_owner = dict(contract)
    removed_owner["required_public_source_pins"] = list(
        contract["required_public_source_pins"][:-1]
    )
    assert_rejected(lambda: validate_contract(removed_owner), "removed preserved proposal source pin")
    checks += 1
    changed_owner = dict(contract)
    owner_copies = [dict(owner) for owner in contract["required_public_source_pins"]]
    owner_copies[-1]["sha256"] = "0" * 64
    changed_owner["required_public_source_pins"] = owner_copies
    assert_rejected(lambda: validate_contract(changed_owner), "substituted preserved proposal pin")
    checks += 1

    for key, hostile in (
        ("minimum_qualified_independent_family_count", 2),
        ("qualified_independent_family_count", 3),
        ("preserved_previous_proposal_case_count", 0),
        ("case_count", 4_194_304),
        ("timed_case_count", 0),
        ("final_protocol_status", "FROZEN"),
        ("case_status", "OPENED"),
    ):
        mutated_previous = dict(previous)
        mutated_previous[key] = hostile
        assert_rejected(
            lambda value=mutated_previous: validate_previous_contract(value),
            "weakened authenticated previous proposal: " + key,
        )
        checks += 1

    for token in (
        b"NOT FROZEN",
        b"NOT GENERATED",
        b"NOT OPENED",
        b"141,557,760",
        b"three distinct independently authored candidates",
        b"live runtime no-delegation",
    ):
        hostile_protocol = protocol.replace(token, b"WITHHELD")
        assert_rejected(
            lambda value=hostile_protocol: validate_protocol(value),
            "removed public proposal safety token: " + token.decode("ascii"),
        )
        checks += 1

    before = guard.blocked_effect_count
    allowed_source = next(iter(guard.allowed_paths))
    hostile_events = (
        ("import", ("re", None, None, None, None)),
        ("import", ("candidates.rust_candidate", None, None, None, None)),
        ("subprocess.Popen", ("matcher", (), None, None)),
        ("os.posix_spawn", ("matcher", (), {})),
        ("socket.connect", (None, ("127.0.0.1", 80))),
        ("ctypes.dlopen", ("libpcre2-8.so",)),
        ("mmap.__new__", (None, 0, 0, 0)),
        ("os.system", (b"true",)),
        ("os.listdir", ("oracle/phase3",)),
        ("os.scandir", ("oracle/phase3",)),
        ("time.perf_counter", ()),
        ("rebar.correctness.clock", ()),
        ("cpython.run_command", ("matcher",)),
        ("open", ("/etc/passwd", "r", os.O_RDONLY)),
        ("open", (PINNED_PYTHON, "r", os.O_RDONLY)),
        ("open", ("oracle/phase3/secret-seed", "r", os.O_RDONLY)),
        ("open", (allowed_source, "w", os.O_WRONLY | os.O_CREAT)),
    )
    for event, arguments in hostile_events:
        assert_rejected(
            lambda name=event, values=arguments: sys.audit(name, *values),
            "external effect " + event,
        )
        checks += 1
    require(
        guard.blocked_effect_count - before == len(hostile_events),
        "source-only guard failed to reject every prohibited external effect exactly once",
    )
    ensure_forbidden_modules_absent()
    return checks


def main() -> int:
    ensure_forbidden_modules_absent()
    require(sys.version_info[:3] == (3, 14, 6), "the pinned Python 3.14.6 is required")
    require(sys.flags.isolated and sys.flags.dont_write_bytecode, "run Python with -I -B")
    require(os.path.realpath(sys.executable) == PINNED_PYTHON, "unexpected Python executable path")
    mode, source_hash, protocol_hash, contract_hash = parse_arguments()
    root = repository_root()
    source_path = os.path.join(root, SOURCE_RELATIVE)
    protocol_path = os.path.join(root, PROTOCOL_RELATIVE)
    contract_path = os.path.join(root, CONTRACT_RELATIVE)
    allowed_paths = {
        os.path.realpath(source_path),
        os.path.realpath(protocol_path),
        os.path.realpath(contract_path),
    }
    allowed_paths.update(
        os.path.realpath(os.path.join(root, owner_path))
        for owner_path, _ in PUBLIC_SOURCE_PINS
    )
    guard = ReadOnlyPublicSourceGuard(allowed_paths)
    sys.addaudithook(guard)

    read_authenticated_plaintext(source_path, source_hash)
    protocol = read_authenticated_plaintext(protocol_path, protocol_hash)
    contract_content = read_authenticated_plaintext(contract_path, contract_hash)
    contract = strict_public_json(contract_content)
    validate_contract(contract)
    validate_protocol(protocol)

    previous_content: bytes | None = None
    for owner_path, owner_hash in PUBLIC_SOURCE_PINS:
        content = read_authenticated_plaintext(os.path.join(root, owner_path), owner_hash)
        if owner_path == PREVIOUS_CONTRACT_RELATIVE:
            previous_content = content
    require(previous_content is not None, "authenticated previous proposal JSON was not read")
    previous = strict_public_json(previous_content)
    validate_previous_contract(previous)

    checks = run_self_tests(contract, previous, protocol, guard)
    ensure_forbidden_modules_absent()
    print("status=PRE-PHASE-3 SUCCESSOR PROPOSAL VERIFIED")
    print("mode=" + mode)
    print("final_protocol=NOT FROZEN")
    print("holdout=NOT GENERATED; NOT OPENED; NOT RUN")
    print("candidate_qualification=0; distinct_complete_p0_no_delegation_required=3")
    print("preserved_original_proposal_case_denominator=4194304")
    print("preserved_immediate_previous_proposal_case_denominator=14155776")
    print("independent_case_denominator=141557760")
    print("independent_timing_denominator=141557760")
    print("complete_cross_product_strata=8847360")
    print("proposed_correctness_gated_timed_observations=13589544960")
    print("proposed_correctness_gated_public_operation_invocations=88332042240")
    print("proposed_raw_clock_bytes_only=108716359680")
    print("performance=NOT MEASURED")
    print("actual_candidate_imports=0")
    print("actual_candidate_processes=0")
    print("actual_native_loads=0")
    print("actual_executable_reads=0")
    print("actual_archive_reads=0")
    print("actual_holdout_cases_read=0")
    print("actual_hidden_secrets_or_seeds_read=0")
    print("actual_clock_samples=0")
    print("actual_network_connections=0")
    print("actual_files_written=0")
    print("hostile_source_only_controls=" + str(checks))
    print("blocked_external_effect_controls=" + str(guard.blocked_effect_count))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ProposalVerificationError) as error:
        print("status=FAIL: " + str(error), file=sys.stderr)
        raise SystemExit(1) from error
