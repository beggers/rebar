#!/usr/bin/env python3
"""Verify only the arithmetic and source of an unopened holdout proposal."""

from __future__ import annotations

import ast
import hashlib
import os
import stat
import sys


SCHEMA = "rebar-expanded-sealed-holdout-pre-phase3-proposal-v1"
SOURCE_RELATIVE = "tools/verify_expanded_sealed_holdout_v1.py"
PROTOCOL_RELATIVE = "oracle/phase3/EXPANDED-SEALED-HOLDOUT-V1.md"
CONTRACT_RELATIVE = "oracle/phase3/expanded-sealed-holdout-v1.json"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
MAX_DOCUMENT_BYTES = 1_048_576
MAX_EXECUTABLE_BYTES = 67_108_864
JSON_FILENAME = "<rebar-expanded-sealed-holdout-v1-public-json>"
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
)

SUBJECT_TYPES = ("str", "bytes", "bytearray", "memoryview")
LIFECYCLE_SLOTS = (
    "operation_valid_fresh_work",
    "operation_valid_warm_cache",
    "operation_valid_compiled_reuse",
    "operation_valid_existing_state",
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

PUBLIC_OWNERS = (
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
    "qualified_independent_family_count": 0,
    "minimum_qualified_independent_family_count": 3,
    "original_p0_case_count": 31_237,
    "original_p0_suite_count": 13,
    "named_private_waiver_count": 13,
    "separate_differential_case_count": 8_244,
    "pinned_python_version": "3.14.6",
    "pinned_python_path": PINNED_PYTHON,
    "pinned_python_sha256": PINNED_PYTHON_SHA256,
    "preserved_previous_proposal_case_count": 4_194_304,
    "case_count": 14_155_776,
    "timed_case_count": 14_155_776,
    "cases_per_stratum": 1_024,
    "operation_count": 36,
    "pattern_family_count": 24,
    "subject_type_count": 4,
    "lifecycle_count": 4,
    "stratum_count": 13_824,
    "cases_per_operation": 393_216,
    "cases_per_pattern_family": 589_824,
    "cases_per_subject_type": 3_538_944,
    "readonly_memoryview_variants_per_memoryview_stratum": 512,
    "writable_memoryview_variants_per_memoryview_stratum": 512,
    "baseline_participant_count": 1,
    "candidate_participant_count": 3,
    "participant_count": 4,
    "paired_round_count": 24,
    "participant_orders_per_case": 24,
    "participant_occurrences_per_order_position": 6,
    "preflight_correctness_observation_count": 56_623_104,
    "individually_correctness_gated_timed_observation_count": 1_358_954_496,
    "candidate_baseline_paired_observation_count": 1_019_215_872,
    "clock_bytes_per_timed_observation": 8,
    "raw_clock_bytes_only": 10_871_635_968,
    "raw_clock_gib_numerator": 81,
    "raw_clock_gib_denominator": 8,
    "operation_family_shard_count": 864,
    "raw_clock_bytes_per_operation_family_shard": 12_582_912,
    "bootstrap_replicate_count": 9_999,
    "bootstrap_stratum_draws_per_candidate": 138_226_176,
    "multiple_comparison_hypothesis_count": 42_467_328,
    "false_discovery_rate_numerator": 5,
    "false_discovery_rate_denominator": 100,
    "memory_cases_per_stratum": 16,
    "memory_case_count": 221_184,
    "memory_observation_count": 884_736,
    "boundary_cases_per_stratum": 4,
    "boundary_case_count": 55_296,
    "boundary_observation_count": 221_184,
    "minimum_faster_case_numerator": 60,
    "minimum_faster_case_denominator": 100,
    "minimum_significantly_faster_case_count": 8_493_466,
    "minimum_lower_confidence_speedup_numerator": 3,
    "minimum_lower_confidence_speedup_denominator": 2,
    "regression_explanation_threshold_percent": 20,
}

EXPECTED_ARRAYS = {
    "operations": OPERATIONS,
    "primary_pattern_families": PATTERN_FAMILIES,
    "subject_types": SUBJECT_TYPES,
    "lifecycle_slots": LIFECYCLE_SLOTS,
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
)


class ProposalVerificationError(RuntimeError):
    """A source-only proposal or external-effect gate was rejected."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProposalVerificationError(message)


def is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in HEX for character in value)
    )


def ensure_matchers_absent() -> None:
    for module_name in sys.modules:
        for prefix in FORBIDDEN_MODULE_PREFIXES:
            if module_name == prefix or module_name.startswith(prefix + "."):
                raise ProposalVerificationError(
                    "a matcher or candidate was already loaded: " + module_name
                )


def parse_arguments() -> tuple[str, str, str, str]:
    arguments = sys.argv[1:]
    require(len(arguments) == 7, "expected one source-only mode and three hashes")
    mode = arguments[0]
    require(
        mode in ("--self-test", "--verify-frozen-context"),
        "only two non-executing, source-only modes are permitted",
    )
    require(
        arguments[1] == "--source-sha256"
        and arguments[3] == "--protocol-sha256"
        and arguments[5] == "--contract-sha256",
        "provide source, public protocol, and contract hashes in that order",
    )
    for value in (arguments[2], arguments[4], arguments[6]):
        require(is_sha256(value), "every source fingerprint must be lowercase SHA-256")
    return mode, arguments[2], arguments[4], arguments[6]


def repository_root() -> str:
    actual_source = os.path.realpath(__file__)
    suffix = os.sep + SOURCE_RELATIVE.replace("/", os.sep)
    require(actual_source.endswith(suffix), "unexpected verifier source location")
    return actual_source[: -len(suffix)]


class ReadOnlyProposalGuard:
    def __init__(self, allowed_paths: set[str]) -> None:
        self.allowed_paths = frozenset(allowed_paths)
        self.blocked_effect_count = 0

    def reject(self, reason: str) -> None:
        self.blocked_effect_count += 1
        raise ProposalVerificationError("source-only guard rejected " + reason)

    def __call__(self, event: str, arguments: tuple[object, ...]) -> None:
        if event == "open":
            if not arguments or not isinstance(arguments[0], (str, bytes)):
                self.reject("an unapproved file descriptor or file")
            path = os.fsdecode(arguments[0])
            if os.path.realpath(path) not in self.allowed_paths:
                self.reject("a candidate, holdout, or unapproved file")
            if len(arguments) > 2 and isinstance(arguments[2], int):
                forbidden = (
                    os.O_WRONLY
                    | os.O_RDWR
                    | os.O_CREAT
                    | os.O_TRUNC
                    | os.O_APPEND
                )
                if arguments[2] & forbidden:
                    self.reject("a file write")
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
                "marshal.loads",
                "rebar.correctness.clock",
                "cpython.run_command",
            )
        ):
            self.reject(event)


def read_authenticated(
    path: str,
    expected_sha256: str,
    *,
    maximum_bytes: int = MAX_DOCUMENT_BYTES,
) -> bytes:
    require(is_sha256(expected_sha256), "invalid authenticated-owner SHA-256")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode), "authenticated owner is not a file")
        require(identity.st_size <= maximum_bytes, "authenticated owner exceeds its bound")
        chunks: list[bytes] = []
        remaining = identity.st_size
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            require(bool(chunk), "authenticated owner was truncated")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"", "authenticated owner grew")
        final_identity = os.fstat(descriptor)
        require(
            (identity.st_dev, identity.st_ino, identity.st_size, identity.st_mtime_ns)
            == (
                final_identity.st_dev,
                final_identity.st_ino,
                final_identity.st_size,
                final_identity.st_mtime_ns,
            ),
            "authenticated owner changed while it was read",
        )
        content = b"".join(chunks)
        require(
            hashlib.sha256(content).hexdigest() == expected_sha256,
            "authenticated owner hash does not match: " + path,
        )
        return content
    finally:
        os.close(descriptor)


def strict_public_json(content: bytes) -> dict[str, object]:
    require(0 < len(content) <= MAX_DOCUMENT_BYTES, "invalid public JSON size")
    require(b"\x00" not in content, "public JSON contains a zero byte")
    try:
        text = content.decode("ascii")
        tree = ast.parse(text, filename=JSON_FILENAME, mode="eval")
    except (UnicodeError, SyntaxError, ValueError) as error:
        raise ProposalVerificationError("invalid, non-ASCII public JSON") from error

    node_count = 0

    def validate_node(node: ast.AST, depth: int) -> None:
        nonlocal node_count
        node_count += 1
        require(node_count <= 8_192 and depth <= 24, "public JSON exceeds its bounds")
        if isinstance(node, ast.Expression):
            validate_node(node.body, depth + 1)
        elif isinstance(node, ast.Dict):
            seen: set[str] = set()
            for key, value in zip(node.keys, node.values, strict=True):
                require(
                    isinstance(key, ast.Constant) and type(key.value) is str,
                    "public JSON object keys must be strings",
                )
                require(key.value not in seen, "duplicate public JSON object key")
                seen.add(key.value)
                validate_node(value, depth + 1)
        elif isinstance(node, ast.List):
            for item in node.elts:
                validate_node(item, depth + 1)
        elif isinstance(node, ast.Constant):
            require(
                type(node.value) in (str, int),
                "public JSON permits only strings and nonnegative integers",
            )
            if type(node.value) is int:
                require(0 <= node.value < (1 << 63), "public integer is out of range")
        else:
            raise ProposalVerificationError("public JSON contains executable syntax")

    validate_node(tree, 0)
    result = ast.literal_eval(tree)
    require(type(result) is dict, "public JSON root must be an object")
    return result


def validate_contract(contract: dict[str, object]) -> None:
    expected_keys = set(EXPECTED_SCALARS)
    expected_keys.update(EXPECTED_ARRAYS)
    expected_keys.add("required_public_owners")
    require(set(contract) == expected_keys, "proposal fields were added, omitted, or changed")

    for key, expected in EXPECTED_SCALARS.items():
        actual = contract[key]
        require(type(actual) is type(expected), "proposal field has the wrong type: " + key)
        require(actual == expected, "proposal field has the wrong value: " + key)

    for key, expected in EXPECTED_ARRAYS.items():
        actual = contract[key]
        require(type(actual) is list, "proposal axis must be a list: " + key)
        require(tuple(actual) == expected, "proposal axis changed: " + key)
        require(len(set(actual)) == len(actual), "proposal axis contains duplicates: " + key)

    owners = contract["required_public_owners"]
    require(type(owners) is list, "published owners must be a list")
    observed: list[tuple[str, str]] = []
    for owner in owners:
        require(type(owner) is dict, "published owner must be an object")
        require(set(owner) == {"path", "sha256"}, "published owner shape changed")
        require(type(owner["path"]) is str, "published owner path is not a string")
        require(is_sha256(owner["sha256"]), "published owner hash is not SHA-256")
        observed.append((owner["path"], owner["sha256"]))
    require(tuple(observed) == PUBLIC_OWNERS, "published qualification owners changed")

    operation_count = len(OPERATIONS)
    family_count = len(PATTERN_FAMILIES)
    subject_count = len(SUBJECT_TYPES)
    lifecycle_count = len(LIFECYCLE_SLOTS)
    strata = operation_count * family_count * subject_count * lifecycle_count
    cases = strata * contract["cases_per_stratum"]
    participants = contract["baseline_participant_count"] + contract[
        "candidate_participant_count"
    ]
    rounds = contract["paired_round_count"]

    require(contract["stratum_count"] == strata, "stratum denominator changed")
    require(contract["case_count"] == cases, "case denominator changed")
    require(contract["timed_case_count"] == cases, "a timing subsample was introduced")
    require(
        cases * 8 == contract["preserved_previous_proposal_case_count"] * 27,
        "the 3.375-times expansion does not preserve the earlier proposal",
    )
    require(contract["cases_per_operation"] * operation_count == cases, "operation weights changed")
    require(
        contract["cases_per_pattern_family"] * family_count == cases,
        "pattern-family weights changed",
    )
    require(contract["cases_per_subject_type"] * subject_count == cases, "subject weights changed")
    require(
        contract["readonly_memoryview_variants_per_memoryview_stratum"]
        + contract["writable_memoryview_variants_per_memoryview_stratum"]
        == contract["cases_per_stratum"],
        "read-only and writable memory views are not balanced",
    )
    require(participants == contract["participant_count"], "participant denominator changed")
    require(participants == 4 and rounds == 24, "four-participant balance is not applicable")

    order_count = 1
    for number in range(2, participants + 1):
        order_count *= number
    require(order_count == contract["participant_orders_per_case"], "full order balance changed")
    require(rounds == order_count, "each participant order is not used exactly once")
    require(
        contract["participant_occurrences_per_order_position"] * participants == rounds,
        "participant positions are not balanced",
    )

    timed = cases * rounds * participants
    require(contract["preflight_correctness_observation_count"] == cases * participants, "preflight denominator changed")
    require(
        contract["individually_correctness_gated_timed_observation_count"] == timed,
        "individually gated timing denominator changed",
    )
    require(
        contract["candidate_baseline_paired_observation_count"]
        == cases * rounds * contract["candidate_participant_count"],
        "baseline-pair denominator changed",
    )
    clock_bytes = timed * contract["clock_bytes_per_timed_observation"]
    require(contract["raw_clock_bytes_only"] == clock_bytes, "raw clock accounting changed")
    require(
        clock_bytes * contract["raw_clock_gib_denominator"]
        == contract["raw_clock_gib_numerator"] * 1024**3,
        "raw clock GiB accounting changed",
    )
    shards = operation_count * family_count
    require(contract["operation_family_shard_count"] == shards, "shard denominator changed")
    require(
        contract["raw_clock_bytes_per_operation_family_shard"] * shards == clock_bytes,
        "raw-clock shards omit observations",
    )
    require(
        contract["bootstrap_stratum_draws_per_candidate"]
        == contract["bootstrap_replicate_count"] * strata,
        "bootstrap denominator changed",
    )
    require(
        contract["multiple_comparison_hypothesis_count"]
        == cases * contract["candidate_participant_count"],
        "multiple-comparison denominator changed",
    )
    for label in ("memory", "boundary"):
        cohort_cases = strata * contract[label + "_cases_per_stratum"]
        require(contract[label + "_case_count"] == cohort_cases, label + " case denominator changed")
        require(
            contract[label + "_observation_count"] == cohort_cases * participants,
            label + " observation denominator changed",
        )
    faster_numerator = cases * contract["minimum_faster_case_numerator"]
    faster_denominator = contract["minimum_faster_case_denominator"]
    minimum_faster = (faster_numerator + faster_denominator - 1) // faster_denominator
    require(
        contract["minimum_significantly_faster_case_count"] == minimum_faster,
        "60-percent corrected-case threshold changed",
    )


def validate_protocol(protocol: bytes) -> None:
    required = (
        b"PRE-PHASE-3 PROPOSAL",
        b"NOT FROZEN",
        b"NOT GENERATED",
        b"NOT OPENED",
        b"NOT RUN",
        b"NOT MEASURED",
        b"14,155,776",
        b"4,194,304",
        b"1,358,954,496",
        b"1,019,215,872",
        b"10,871,635,968",
        b"10.125 GiB",
        b"42,467,328",
        b"8,493,466",
        b"three independently authored engine families",
    )
    for token in required:
        require(token in protocol, "public proposal omits: " + token.decode("ascii"))


def assert_rejected(function: object, message: str) -> None:
    try:
        function()
    except ProposalVerificationError:
        return
    raise ProposalVerificationError("hostile self-test was not rejected: " + message)


def run_self_tests(contract: dict[str, object], guard: ReadOnlyProposalGuard) -> int:
    checks = 0
    validate_contract(contract)
    checks += 1

    duplicate_json = b'{"schema":"x","schema":"y"}'
    assert_rejected(lambda: strict_public_json(duplicate_json), "duplicate JSON keys")
    checks += 1
    executable_json = b'{"schema": __import__("re")}'
    assert_rejected(lambda: strict_public_json(executable_json), "executable JSON")
    checks += 1
    bool_json = b'{"schema": true}'
    assert_rejected(lambda: strict_public_json(bool_json), "JSON booleans")
    checks += 1

    for key, hostile in (
        ("final_protocol_status", "FROZEN"),
        ("case_status", "GENERATED"),
        ("timing_status", "MEASURED"),
        ("qualified_independent_family_count", 3),
        ("timed_case_count", 4_194_304),
        ("case_count", 4_194_304),
        ("participant_count", 5),
        ("paired_round_count", 12),
        ("multiple_comparison_hypothesis_count", 14_155_776),
        ("raw_clock_bytes_only", 3_221_225_472),
        ("minimum_significantly_faster_case_count", 8_493_465),
    ):
        mutated = dict(contract)
        mutated[key] = hostile
        assert_rejected(lambda value=mutated: validate_contract(value), key)
        checks += 1

    repeated_operations = list(contract["operations"])
    repeated_operations[-1] = repeated_operations[0]
    mutated = dict(contract)
    mutated["operations"] = repeated_operations
    assert_rejected(lambda: validate_contract(mutated), "duplicate operation")
    checks += 1

    before = guard.blocked_effect_count
    hostile_events = (
        ("import", ("re", None, None, None, None)),
        ("import", ("candidates.rust_candidate", None, None, None, None)),
        ("subprocess.Popen", ("regex", (), None, None)),
        ("socket.connect", (None, ("127.0.0.1", 80))),
        ("ctypes.dlopen", ("libpcre2-8.so",)),
        ("os.system", (b"true",)),
        ("time.perf_counter", ()),
        ("rebar.correctness.clock", ()),
        ("open", ("/etc/passwd", "r", os.O_RDONLY)),
    )
    for event, arguments in hostile_events:
        assert_rejected(
            lambda name=event, values=arguments: sys.audit(name, *values),
            "external effect " + event,
        )
        checks += 1
    require(
        guard.blocked_effect_count - before == len(hostile_events),
        "source-only audit-hook controls did not each reject exactly one effect",
    )
    ensure_matchers_absent()
    return checks


def main() -> int:
    ensure_matchers_absent()
    require(sys.version_info[:3] == (3, 14, 6), "the pinned Python 3.14.6 is required")
    require(sys.flags.isolated and sys.flags.dont_write_bytecode, "run Python with -I -B")
    require(os.path.realpath(sys.executable) == PINNED_PYTHON, "unexpected Python executable")
    mode, source_hash, protocol_hash, contract_hash = parse_arguments()
    root = repository_root()
    source_path = os.path.join(root, SOURCE_RELATIVE)
    protocol_path = os.path.join(root, PROTOCOL_RELATIVE)
    contract_path = os.path.join(root, CONTRACT_RELATIVE)
    public_paths = {os.path.realpath(os.path.join(root, path)) for path, _ in PUBLIC_OWNERS}
    allowed_paths = {
        os.path.realpath(source_path),
        os.path.realpath(protocol_path),
        os.path.realpath(contract_path),
        os.path.realpath(PINNED_PYTHON),
    }
    allowed_paths.update(public_paths)
    guard = ReadOnlyProposalGuard(allowed_paths)
    sys.addaudithook(guard)

    read_authenticated(source_path, source_hash)
    protocol = read_authenticated(protocol_path, protocol_hash)
    contract_content = read_authenticated(contract_path, contract_hash)
    read_authenticated(
        PINNED_PYTHON,
        PINNED_PYTHON_SHA256,
        maximum_bytes=MAX_EXECUTABLE_BYTES,
    )
    contract = strict_public_json(contract_content)
    validate_contract(contract)
    validate_protocol(protocol)

    for owner_path, owner_hash in PUBLIC_OWNERS:
        read_authenticated(os.path.join(root, owner_path), owner_hash)

    checks = run_self_tests(contract, guard)
    ensure_matchers_absent()
    print("status=PRE-PHASE-3 PROPOSAL VERIFIED")
    print("mode=" + mode)
    print("final_protocol=NOT FROZEN")
    print("holdout=NOT GENERATED; NOT OPENED; NOT RUN")
    print("candidate_qualification=0; minimum_required=3")
    print("independent_case_denominator=14155776")
    print("independent_timing_denominator=14155776")
    print("proposed_correctness_gated_timed_observations=1358954496")
    print("proposed_raw_clock_bytes_only=10871635968")
    print("performance=NOT MEASURED")
    print("actual_candidate_imports=0")
    print("actual_candidate_processes=0")
    print("actual_native_loads=0")
    print("actual_holdout_cases_read=0")
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
