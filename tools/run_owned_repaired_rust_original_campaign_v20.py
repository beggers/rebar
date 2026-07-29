#!/usr/bin/env python3
"""Correct frozen first-party observer classification, not Rust semantics.

Source modes independently authenticate the complete small V19 failure
receipt, its first real producer exception, all 13 original rows, two genuine
semantic losses, five incomplete workers, and exact restored-owner evidence.
The two candidate-aware original-source overlays change one authenticated
runtime call each in memory, only after the real strict guard binds Rust.
No matcher, binary, archive, root, clock, benchmark, or holdout runs here.
"""

from __future__ import annotations

import ast
import hashlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
SOURCE = "tools/run_owned_repaired_rust_original_campaign_v20.py"
PROTOCOL = "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V20.md"
CONTRACT = "oracle/phase2/repaired-rust-original-campaign-v20.json"
SCHEMA = "rebar-owned-repaired-rust-original-campaign-v20"
VERSION = 20
BUILD_LABEL = "phase2-v21-rust-captured-findall-root-provenance"
BUILD_SUFFIX = BUILD_LABEL + "-original-p0"
LABEL = BUILD_SUFFIX + "-v20"
RECOVERY_PREFIX = "rebar-phase2-repaired-rust-original-campaign-v20-"
RECOVERY_ROOT = "/tmp/" + RECOVERY_PREFIX + BUILD_SUFFIX
V19 = (
    ("tools/run_owned_repaired_rust_original_campaign_v19.py",
     "146a47218b87ba15fbfdd357db6d10b101a2869f30b51413ef8f5d5df79a5b48",
     42364, 431246),
    ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V19.md",
     "e54bfacda42669e35e7052b058d41cb230aa128a4b2f8568316c03766de908d1",
     6300, 525235),
    ("oracle/phase2/repaired-rust-original-campaign-v19.json",
     "d97ab35ea90761a01d343648c1701e56140f81f27e0a7fc9a39cc5f7ff9f81c8",
     23675, 525236),
)
V19_RECEIPT = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v21-rust-captured-findall-root-provenance-"
    "original-p0-v19-failures-publication-receipt.json",
    "e48a4115a85d827cbf16a32b6b44390d2bf4b092e1823989c9bcafe874fa04fe",
    29374, 525287,
)
HARNESS = (
    "tools/rust_original_cpython_suite_v1.py",
    "cf0267e3766fb849891d182e5b57ced569a0634831dd494d8135e703844b6c95",
    67175, 430765,
)
CORE = (
    "tools/independent_public_contract_v3.py",
    "9a831571c81e542d7d43ae56aea271f8e6c69550173d97ae1c9f8213eef40bf3",
    91039, 430402,
)
DIRECT_GATE = (
    "tools/run_frozen_p0_candidate_v1.py",
    "c8378cd59a3b4dfaf75609c5b06f5a5ec20114d428e8e06ccc0f12ceec2076b8",
    104772, 432295,
)
PRODUCER = (
    "tools/run_owned_six_family_original_p0_producer_v5.py",
    "b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538",
    102286, 431370,
)
FIRST_STDOUT_SHA = (
    "46795942968fa9a528855999d13d857ca873dc9a1f66e5dd812a9a79f6e1dd88"
)
FIRST_STDERR_SHA = (
    "d541924638c02a9179ed2d0fbecd661cabb6254b876c1d6c9416cb2f1e77fdee"
)
FIRST_TRACEBACK_SHA = (
    "44c12197e1d8ebe7da081436299554602c441f0a557e46ca17df43494297135e"
)
FIRST_INNER_SHA = (
    "583f18377ba3b336826f1ccb3e96fc9449a8eae72bf5e0333dcc9b03036057ff"
)
FIRST_FAILURE = "a Rust candidate entered the original-only suite controller"
OUTER_FAILURE = "CampaignError: reject an incomplete, borrowed, or falsified V16 worker"
MARKER = b"REBAR-V16-AUTHENTIC-PRODUCER-FAILURE "
FAILURE_SUITES = (
    "original_bounded_v5", "public_v3", "scanner_v3", "buffer_v3",
    "subinterpreter_v2",
)
PASS_SUITES = (
    "managed_v1", "scanner_verbose_v1", "public_types_v1",
    "public_surface_v19", "pep688_v4", "threaded_pattern_v1",
)
KNOWN_MISMATCHES = (("substitution_v2", 240), ("shape_v2", 1056))
ACTUAL_V19_ROW_DIGESTS = (
    ("original_bounded_v5",
     "127d683a8cf34ee5878c226f50ec7decac652f43b870af96bef0da907fabaa6d"),
    ("public_v3",
     "9ab507e29180c31707e19f03a64819b52fae8a49549b744a5ba6642686f51f8c"),
    ("scanner_v3",
     "6455e3018592759702973f2ac3216a9be5c0ddb00f7d4768307aa2e2b37eaf5f"),
    ("buffer_v3",
     "aad5e4041214c4433b8efbf9e5b44d63a7eab63a5e1f61911a2ece3eba845a2b"),
    ("managed_v1",
     "63bca442093e55e059cef4a75f46d06e26aee90989e0f14512d7ef0b39da7388"),
    ("scanner_verbose_v1",
     "47ba23ba46074b4afdd965368fe0233607f6522abd4b06c66ac7c195429eb31c"),
    ("public_types_v1",
     "4eb1086816338051a7d82c815c0d7329a65cabac2e2d2efc68269ced5e176477"),
    ("substitution_v2",
     "f2ea8c6cf505f5979fa70578d61a86a9c86efb2087e443cb5ffbefd96a5d09b8"),
    ("shape_v2",
     "be96febfa16160f8adf97c3621b948670621c4c6c599f5f9f020b6de8a4dfd30"),
    ("public_surface_v19",
     "dc5d51584742f682c875341a43a170a479e07bd37fa9e1f97f91ecb37787a2ea"),
    ("subinterpreter_v2",
     "38cd5e71e6980978a29d475ae210ccdb7eeed0b6014ef0db576986e541525b9c"),
    ("pep688_v4",
     "fe6434984dca9c8b43748bac66ffbd39483c99b077719736522371d7b6f22d06"),
    ("threaded_pattern_v1",
     "84679c15aee0861b6947c60e7ee753737e364aa318a95890293119714bc10b5b"),
)


class CampaignError(Exception):
    """Authentic actual evidence or candidate-aware observer isolation failed."""


def need(value: object, reason: str) -> None:
    if value is not True:
        raise CampaignError(reason)


def secure_owner(owner: tuple, *, maximum: int = 4 * 1024 * 1024) -> bytes:
    need(type(owner) is tuple and len(owner) == 4,
         "require an exact immutable source-only V20 owner")
    path, fingerprint, size, inode = owner
    need(type(path) is str and bool(path) and not path.startswith("/")
         and ".." not in path.split("/")
         and not path.endswith((".gz", ".so"))
         and type(fingerprint) is str and len(fingerprint) == 64
         and all(item in "0123456789abcdef" for item in fingerprint)
         and type(size) is int and 0 < size <= maximum
         and type(inode) is int and inode > 0,
         "forbid native, archive, private-root and unpinned source access")
    descriptor = os.open(
        ROOT + "/" + path,
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode) and before.st_dev == 2064
             and before.st_ino == inode and before.st_size == size
             and before.st_uid == os.geteuid() and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o600,
             "reject a substituted immutable source owner: " + path)
        remaining = size
        pieces: list[bytes] = []
        while remaining:
            item = os.read(descriptor, min(remaining, 262144))
            need(bool(item), "reject truncated frozen source: " + path)
            pieces.append(item)
            remaining -= len(item)
        need(not os.read(descriptor, 1),
             "reject expanded frozen source: " + path)
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        need(hashlib.sha256(raw).hexdigest() == fingerprint
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject changed frozen source owner: " + path)
        return raw
    finally:
        os.close(descriptor)


def decode_bounded_base64(value: object, *, maximum: int,
                          encoder: object) -> bytes:
    need(type(value) is str and 0 < len(value) <= 4 * maximum + 4
         and len(value) % 4 == 0 and callable(encoder),
         "require exact bounded source-only canonical stream encoding")
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    lookup = {char: index for index, char in enumerate(alphabet)}
    result = bytearray()
    for offset in range(0, len(value), 4):
        group = value[offset:offset + 4]
        need(group[0] in lookup and group[1] in lookup
             and (group[2] in lookup or group[2] == "=")
             and (group[3] in lookup or group[3] == "=")
             and not (group[2] == "=" and group[3] != "=")
             and ("=" not in group or offset + 4 == len(value)),
             "reject malformed or nonfinal actual evidence base64")
        number = (
            lookup[group[0]] << 18
            | lookup[group[1]] << 12
            | (0 if group[2] == "=" else lookup[group[2]]) << 6
            | (0 if group[3] == "=" else lookup[group[3]])
        )
        result.append((number >> 16) & 255)
        if group[2] != "=":
            result.append((number >> 8) & 255)
        if group[3] != "=":
            result.append(number & 255)
    raw = bytes(result)
    need(0 < len(raw) <= maximum and encoder(raw) == value,
         "reject noncanonical, nonzero-pad, or oversized actual evidence")
    return raw


def validate_actual_v19_receipt(value: object, parent: types.ModuleType,
                               state: dict) -> dict:
    need(type(value) is dict, "require the complete genuine V19 public receipt")
    assert isinstance(value, dict)
    need(value.get("schema")
         == "rebar-owned-repaired-rust-original-campaign-v19-"
            "durable-publication-receipt"
         and value.get("status") == "PASS"
         and value.get("publication_status") == "PASS"
         and value.get("candidate_status") == "FAIL"
         and value.get("candidate_qualified") is False
         and value.get("family") == "rust"
         and value.get("label")
         == BUILD_SUFFIX + "-v19"
         and value.get("campaign_source_sha256") == V19[0][1]
         and value.get("campaign_protocol_sha256") == V19[1][1]
         and value.get("campaign_contract_sha256") == V19[2][1]
         and value.get("suite_count") == 13
         and value.get("case_execution_denominator") == 31237
         and value.get("named_private_waiver_count") == 13
         and value.get("attempted_suite_count") == 13
         and value.get("started_suite_count") == 13
         and value.get("completed_suite_count") == 8
         and value.get("actual_candidate_workers") == 13
         and value.get("distinct_worker_process_id_count") == 13
         and value.get("duplicate_worker_process_id_count") == 0
         and value.get("missing_worker_process_id_count") == 0
         and value.get("verified_passing_case_count") == 12942
         and value.get("semantic_mismatch_count") == "NOT MEASURED"
         and value.get("infrastructure_failure_count") == 5
         and value.get("all_original_observation_vectors_complete") is False
         and value.get("all_four_original_targets_restored") is True
         and value.get("restoration_verified_before_publication") is True
         and value.get("all_original_suite_rows_validated_before_publication")
         is True
         and value.get("holdout") == "NOT OPENED"
         and value.get("hidden_cases_read") == 0
         and value.get("benchmark_files_read") == 0
         and value.get("clock_samples") == 0
         and value.get("timing_trials_run") == 0
         and value.get("performance") == "NOT MEASURED"
         and value.get("original_v5_producer_source_sha256") == PRODUCER[1]
         and value.get("actual_v21_build_receipt_sha256")
         == parent.V21_PUBLICATION[1]
         and value.get("native_engine_sha256") == parent.ENGINE_SHA
         and value.get("native_bridge_sha256") == parent.BRIDGE_SHA
         and value.get("combined_bridge_source_sha256") == parent.CAPTURE_SHA
         and value.get("corrected_public_adapter_sha256") == parent.ADAPTER_SHA,
         "preserve actual failed candidate separately from durable publication")
    rows = value.get("suite_integrity")
    need(type(rows) is list and len(rows) == 13
         and tuple((row.get("suite"), row.get("case_execution_denominator"))
                   for row in rows) == parent.SUITES
         and tuple((row.get("suite"), row.get("complete_original_row_sha256"))
                   for row in rows) == ACTUAL_V19_ROW_DIGESTS
         and all(type(row.get("complete_original_row_sha256")) is str
                 and len(row["complete_original_row_sha256"]) == 64
                 and row.get("worker_attempted") is True
                 and row.get("actual_worker_started") is True
                 and type(row.get("pid")) is int and row["pid"] > 0
                 for row in rows)
         and len({row["pid"] for row in rows}) == 13,
         "retain 13 genuinely source-ordered distinct actual worker vectors")
    passed = tuple(row for row in rows
                   if row.get("failure_class") == "PASS")
    mismatches = tuple(row for row in rows
                       if row.get("failure_class") == "SEMANTIC MISMATCH")
    failures = tuple(row for row in rows
                     if row.get("failure_class") == "INFRASTRUCTURE FAILURE")
    need(tuple(row["suite"] for row in passed) == PASS_SUITES
         and all(row.get("fully_observed") is True
                 and row.get("mismatch_count") == 0
                 and row.get("verified_passing_case_count")
                 == row["case_execution_denominator"]
                 and row.get("returncode") == 0 for row in passed)
         and sum(row["verified_passing_case_count"] for row in passed) == 12942
         and tuple((row["suite"], row.get("mismatch_count"))
                   for row in mismatches) == KNOWN_MISMATCHES
         and all(row.get("fully_observed") is True
                 and row.get("returncode") == 1 for row in mismatches)
         and tuple(row["suite"] for row in failures) == FAILURE_SUITES
         and all(row.get("fully_observed") is False
                 and row.get("mismatch_count") == "NOT MEASURED"
                 and row.get("verified_passing_case_count") == 0
                 and row.get("returncode") == 2 for row in failures)
         and sum(row["case_execution_denominator"] for row in rows) == 31237
         and sum(row["case_execution_denominator"] for row in failures) == 2935,
         "never mix genuine semantic losses with incomplete infrastructure")
    capture = value.get("worker_failure_capture")
    need(type(capture) is dict
         and value.get("worker_failure_capture_count") == 5
         and value.get("worker_failure_capture_complete") is True
         and capture.get("actual_failure_count") == 5
         and capture.get("all_failure_metadata_preserved") is True
         and type(capture.get("suite_failure_summaries")) is list
         and len(capture["suite_failure_summaries"]) == 5
         and tuple(item.get("suite")
                   for item in capture["suite_failure_summaries"])
         == FAILURE_SUITES
         and all(item.get("error_type") == "CampaignError"
                 and item.get("error_message") == OUTER_FAILURE
                 and item.get("returncode") == 2
                 and item.get("stdout_complete") is True
                 and item.get("stderr_complete") is True
                 and item.get("traceback_complete") is True
                 for item in capture["suite_failure_summaries"]),
         "retain five actual bounded failures without inventing their causes")
    first = capture.get("first_worker_failure")
    need(type(first) is dict
         and first.get("suite") == "original_bounded_v5"
         and first.get("returncode") == 2
         and first.get("stderr_sha256") == FIRST_STDERR_SHA
         and first.get("stdout_sha256") == FIRST_STDOUT_SHA
         and first.get("traceback_sha256") == FIRST_TRACEBACK_SHA,
         "authenticate the sole genuinely published complete worker streams")
    encoder = state["parent"].source_only_base64
    streams: dict[str, bytes] = {}
    for key, digest, count in (
        ("stderr", FIRST_STDERR_SHA, 8046),
        ("stdout", FIRST_STDOUT_SHA, 1252),
    ):
        record = first.get(key)
        need(type(record) is dict and record.get("complete") is True
             and record.get("available") is True
             and record.get("source_size_bytes") == count
             and record.get("captured_size_bytes") == count
             and record.get("source_sha256") == digest,
             "require complete authenticated actual V19 " + key)
        raw = decode_bounded_base64(record.get("base64"),
                                    maximum=65536, encoder=encoder)
        need(len(raw) == count and hashlib.sha256(raw).hexdigest() == digest,
             "reject changed genuine full V19 " + key)
        streams[key] = raw
    need(streams["stderr"].count(MARKER) == 1,
         "require exactly one complete genuine original producer failure")
    line = streams["stderr"].split(b"\n", 1)[0]
    need(line.startswith(MARKER),
         "authenticate the first actual bounded V16 producer diagnostic")
    diagnostic = parent.document(
        state["original_base"], state["guard"],
        line[len(MARKER):] + b"\n",
        "genuine complete V19 original producer exception chain",
    )
    need(diagnostic.get("schema")
         == "rebar-owned-repaired-rust-original-campaign-v19-"
            "authenticated-original-producer-failure"
         and diagnostic.get("status") == "FAIL"
         and diagnostic.get("diagnostic_only") is True
         and diagnostic.get("suite") == "original_bounded_v5"
         and diagnostic.get("observer") == "observe_original_upstream"
         and diagnostic.get("candidate_family") == "rust"
         and diagnostic.get("case_execution_denominator") == 151
         and diagnostic.get("producer_source_sha256") == PRODUCER[1]
         and diagnostic.get("producer_failure_type") == "ActualSuiteFailure"
         and diagnostic.get("underlying_error_type") == "OriginalSuiteError"
         and diagnostic.get("underlying_error_message", {}).get("text")
         == FIRST_FAILURE
         and diagnostic.get("completed_candidate_case_count") == 0
         and diagnostic.get("active_case") is None
         and diagnostic.get("hidden_cases_read") == 0
         and diagnostic.get("clock_samples") == 0
         and diagnostic.get("holdout") == "NOT OPENED",
         "preserve actual original-only infrastructure, not a guessed mismatch")
    chain = diagnostic.get("authentic_exception_chain")
    need(type(chain) is list and len(chain) == 2
         and tuple(row.get("exception_type") for row in chain)
         == ("ActualSuiteFailure", "OriginalSuiteError")
         and chain[1].get("message", {}).get("text") == FIRST_FAILURE,
         "retain the authentic actual producer and underlying exception")
    encoded_details = diagnostic.get("complete_canonical_failure_details")
    need(type(encoded_details) is dict
         and encoded_details.get("complete") is True
         and encoded_details.get("source_sha256") == FIRST_INNER_SHA,
         "require complete authentic nested original failure details")
    nested_bytes = decode_bounded_base64(
        encoded_details.get("base64"), maximum=16384, encoder=encoder,
    )
    need(hashlib.sha256(nested_bytes).hexdigest() == FIRST_INNER_SHA,
         "reject changed canonical nested original failure")
    nested = parent.document(
        state["original_base"], state["guard"], nested_bytes,
        "actual canonical original V5 producer failure",
    )
    need(nested.get("schema")
         == "rebar-owned-six-family-original-p0-producer-v5-genuine-suite-failure"
         and nested.get("candidate_family") == "rust"
         and nested.get("suite") == "original_bounded_v5"
         and nested.get("error_type") == "OriginalSuiteError"
         and nested.get("error_message") == FIRST_FAILURE
         and nested.get("completed_candidate_cases") == 0,
         "reject invented or misclassified genuine upstream failure")
    stdout = parent.document(
        state["original_base"], state["guard"], streams["stdout"],
        "genuine actual V19 worker exception stdout",
    )
    need(stdout.get("schema")
         == "rebar-owned-repaired-rust-original-campaign-v19-entry-failure"
         and stdout.get("status") == "FAIL"
         and stdout.get("error_type") == "ActualSuiteFailure"
         and stdout.get("error_message")
         == "the guarded literal original upstream test failed",
         "preserve actual incomplete-worker stdout without calling it a pass")
    destructor = (
        b"AttributeError: 'NoneType' object has no attribute 'free'"
    )
    need(streams["stderr"].count(destructor) == 17,
         "preserve all 17 real destructor warnings as a separate lifecycle loss")
    return {"receipt": value, "rows": rows, "capture": capture,
            "first_diagnostic": diagnostic, "first_nested": nested,
            "first_stdout": stdout, "first_stderr": streams["stderr"],
            "destructor_warning_count": 17}


def clean_candidate_aware_source(raw: bytes, owner: tuple,
                                 function_name: str, line_number: int,
                                 keyword: str) -> bytes:
    need(type(raw) is bytes and len(raw) == owner[2]
         and hashlib.sha256(raw).hexdigest() == owner[1]
         and owner in (HARNESS, CORE),
         "authenticate one exact immutable family-aware observer source")
    need(
        (
            owner == HARNESS
            and function_name == "authenticate_original_sources"
            and line_number == 211
            and keyword == "candidate"
        )
        or (
            owner == CORE
            and function_name == "load_prerequisites"
            and line_number == 483
            and keyword == "candidate_loaded"
        ),
        "require the exact owner-specific candidate guard and frozen AST site",
    )
    try:
        text = raw.decode("utf-8", "strict")
        tree = ast.parse(text, filename=owner[0])
    except (UnicodeError, SyntaxError, ValueError, RecursionError) as error:
        raise CampaignError("reject altered genuine observer source") from error
    matches = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == function_name
    ]
    need(len(matches) == 1 and bool(matches[0].body),
         "require exactly one genuine observer runtime call: " + function_name)
    statement = matches[0].body[0]
    need(isinstance(statement, ast.Expr)
         and isinstance(statement.value, ast.Call)
         and isinstance(statement.value.func, ast.Name)
         and statement.value.func.id == "verify_runtime"
         and not statement.value.args and not statement.value.keywords
         and statement.lineno == line_number
         and statement.end_lineno == line_number,
         "reject a changed candidate-free original runtime guard site")
    lines = text.splitlines(keepends=True)
    need(len(lines) >= line_number
         and lines[line_number - 1]
         in ("    verify_runtime()\n", "    verify_runtime()\r\n"),
         "authenticate the exact source-ordered original-only verifier line")
    ending = "\r\n" if lines[line_number - 1].endswith("\r\n") else "\n"
    lines[line_number - 1] = (
        "    verify_runtime(" + keyword + "=True)" + ending
    )
    result = "".join(lines).encode("utf-8")
    changed = ast.parse(result.decode("utf-8"), filename=owner[0])
    statement.value.keywords = [
        ast.keyword(arg=keyword, value=ast.Constant(value=True)),
    ]
    need(ast.dump(tree, include_attributes=False)
         == ast.dump(changed, include_attributes=False),
         "reject oracle, matcher, records, tests, or observer-source changes")
    compile(result, ROOT + "/" + owner[0], "exec", dont_inherit=True)
    return result


def synthetic_observer_call(raw: bytes, owner: tuple,
                            function_name: str, *, candidate: bool) -> dict:
    tree = ast.parse(raw.decode("utf-8"), filename=owner[0])
    found = [node for node in tree.body
             if isinstance(node, ast.FunctionDef)
             and node.name == function_name]
    need(len(found) == 1 and bool(found[0].body)
         and isinstance(found[0].body[0], ast.Expr),
         "require the authentic isolated observer call expression")
    statement = found[0].body[0]
    assert isinstance(statement, ast.Expr)
    recorded: list[dict] = []

    def synthetic_verify_runtime(**kwargs: object) -> None:
        recorded.append(dict(kwargs))
        flag = kwargs.get("candidate") if owner == HARNESS else (
            kwargs.get("candidate_loaded")
        )
        if flag is not True:
            raise CampaignError(
                FIRST_FAILURE if owner == HARNESS
                else "a candidate escaped into an original-only public controller",
            )

    expression = ast.Expression(body=statement.value)
    try:
        eval(compile(ast.fix_missing_locations(expression), owner[0], "eval",
                     dont_inherit=True),
             {"__builtins__": {}, "verify_runtime": synthetic_verify_runtime})
    except CampaignError as error:
        need(candidate is False and len(recorded) == 1,
             "misclassify an authentic isolated original-only verifier")
        return {"status": "FAIL", "error_message": str(error),
                "candidate_guard_invocations": 1}
    need(candidate is True and len(recorded) == 1,
         "fail to invoke the genuine candidate-aware original verifier")
    return {"status": "PASS", "keyword": dict(recorded[0]),
            "candidate_guard_invocations": 1}


def observer_source_proof() -> dict:
    harness = secure_owner(HARNESS)
    core = secure_owner(CORE)
    secure_owner(DIRECT_GATE)
    secure_owner(PRODUCER)
    fixed_harness = clean_candidate_aware_source(
        harness, HARNESS, "authenticate_original_sources", 211, "candidate",
    )
    fixed_core = clean_candidate_aware_source(
        core, CORE, "load_prerequisites", 483, "candidate_loaded",
    )
    old_harness = synthetic_observer_call(
        harness, HARNESS, "authenticate_original_sources", candidate=False,
    )
    new_harness = synthetic_observer_call(
        fixed_harness, HARNESS, "authenticate_original_sources",
        candidate=True,
    )
    old_core = synthetic_observer_call(
        core, CORE, "load_prerequisites", candidate=False,
    )
    new_core = synthetic_observer_call(
        fixed_core, CORE, "load_prerequisites", candidate=True,
    )
    need(old_harness.get("status") == "FAIL"
         and old_harness.get("error_message") == FIRST_FAILURE
         and new_harness == {
             "status": "PASS", "keyword": {"candidate": True},
             "candidate_guard_invocations": 1,
         }
         and old_core.get("status") == "FAIL"
         and old_core.get("error_message")
         == "a candidate escaped into an original-only public controller"
         and new_core == {
             "status": "PASS", "keyword": {"candidate_loaded": True},
             "candidate_guard_invocations": 1,
         },
         "prove both exact genuine runtime checks without importing a matcher")
    return {"status": "PASS", "harness": harness, "core": core,
            "fixed_harness": fixed_harness, "fixed_core": fixed_core,
            "original_actual_error_reproduced": True,
            "public_core_incompatibility": "SOURCE-INFERRED; NOT OBSERVED",
            "harness_exact_call_changes": 1,
            "core_exact_call_changes": 1}


def require_guarded_rust(producer: types.ModuleType, bundle: dict,
                         parent: types.ModuleType) -> object:
    need(type(producer) is types.ModuleType
         and getattr(producer, "SCHEMA", None)
         == "rebar-owned-six-family-original-p0-producer-v5"
         and type(bundle) is dict
         and type(bundle.get("policy")) is type(bundle["policy"])
         and getattr(bundle["policy"], "installed", False) is True
         and bundle.get("candidate") is sys.modules.get("re")
         and sys.modules.get("re")
         is sys.modules.get("candidates.rust_candidate")
         and "_sre" not in sys.modules and "ctypes" not in sys.modules
         and callable(producer.family_spec)
         and callable(producer.require_selected),
         "install only after the exact immutable guard binds first-party Rust")
    family = producer.family_spec("rust")
    need(family.name == "rust"
         and family.module == "candidates.rust_candidate"
         and family.bridge_module == "candidates._rust_bridge"
         and family.combined_native is False
         and family.owned_ctypes is False
         and tuple(family.source_owners) == parent.CORRECTED_SOURCES
         and producer.require_selected(family) is bundle["candidate"]
         and callable(bundle["policy"].check_modules),
         "reject crossed family, fallback, foreign regex, or false native pins")
    bundle["policy"].check_modules()
    return family


def install_family_aware_observers(producer: types.ModuleType,
                                   bundle: dict,
                                   parent: types.ModuleType) -> dict:
    need(type(producer) is types.ModuleType
         and getattr(producer, "SCHEMA", None)
         == "rebar-owned-six-family-original-p0-producer-v5"
         and tuple(getattr(producer, "HARNESS_OWNER", ())) == HARNESS
         and tuple(getattr(producer, "DIRECT_GATE_OWNER", ())) == DIRECT_GATE
         and getattr(producer, "SOURCE_RELATIVE", None) == PRODUCER[0]
         and type(bundle) is dict
         and getattr(bundle.get("policy"), "installed", False) is True
         and bundle.get("candidate") is sys.modules.get("re")
         and "_sre" not in sys.modules and "ctypes" not in sys.modules
         and callable(getattr(producer, "load_module", None))
         and callable(getattr(producer, "read_owner", None)),
         "bind only the authenticated guarded genuine V5 producer")
    original_loader = producer.load_module
    counters = {"original_harness_overlays": 0,
                "public_core_overlays": 0,
                "other_family_overlays": 0,
                "native_libraries_loaded_by_overlay": 0}

    def guarded_loader(owner: object, name: str) -> types.ModuleType:
        if owner != HARNESS and owner != DIRECT_GATE:
            return original_loader(owner, name)
        require_guarded_rust(producer, bundle, parent)
        if owner == HARNESS:
            need(name == "_rebar_v5_original_harness_rust",
                 "reject a crossed or reference-family original harness")
            previous_read = producer.read_owner

            def guarded_read(item: object, *args: object,
                             **kwargs: object) -> bytes:
                raw = previous_read(item, *args, **kwargs)
                if item == HARNESS:
                    counters["original_harness_overlays"] += 1
                    return clean_candidate_aware_source(
                        raw, HARNESS, "authenticate_original_sources", 211,
                        "candidate",
                    )
                return raw

            producer.read_owner = guarded_read
            try:
                result = original_loader(owner, name)
            finally:
                producer.read_owner = previous_read
            need(producer.read_owner is previous_read
                 and counters["original_harness_overlays"] == 1
                 and getattr(result, "__file__", None)
                 == ROOT + "/" + HARNESS[0]
                 and "_sre" not in sys.modules
                 and "ctypes" not in sys.modules,
                 "restore the exact authenticated original harness reader")
            require_guarded_rust(producer, bundle, parent)
            return result
        need(name.startswith("_rebar_v5_direct_gate_rust_"),
             "reject a crossed original public-category observer")
        gate = original_loader(owner, name)
        original_route = getattr(gate, "source_module_for_core", None)
        need(type(gate) is types.ModuleType and callable(original_route),
             "retain the exact authenticated first-party direct gate")

        def candidate_aware_core(suite: object) -> tuple:
            require_guarded_rust(producer, bundle, parent)
            pair = original_route(suite)
            need(type(pair) is tuple and len(pair) == 2
                 and type(pair[0]) is types.ModuleType
                 and getattr(pair[0], "SOURCE_RELATIVE", None) == CORE[0]
                 and getattr(pair[0], "__file__", None)
                 == ROOT + "/" + CORE[0],
                 "retain the exact immutable category source and matrix")
            core, category = pair
            raw = secure_owner(CORE)
            fixed = clean_candidate_aware_source(
                raw, CORE, "load_prerequisites", 483, "candidate_loaded",
            )
            parsed = ast.parse(fixed.decode("utf-8"), filename=CORE[0])
            functions = [item for item in parsed.body
                         if isinstance(item, ast.FunctionDef)
                         and item.name == "load_prerequisites"]
            need(len(functions) == 1
                 and type(core.load_prerequisites) is types.FunctionType,
                 "reject replacement of the genuine public prerequisite")
            selected = ast.Module(
                body=[
                    ast.ImportFrom(
                        module="__future__",
                        names=[ast.alias(name="annotations")], level=0,
                    ),
                    functions[0],
                ],
                type_ignores=[],
            )
            exec(compile(ast.fix_missing_locations(selected),
                         ROOT + "/" + CORE[0], "exec", dont_inherit=True),
                 core.__dict__)
            counters["public_core_overlays"] += 1
            require_guarded_rust(producer, bundle, parent)
            return core, category

        gate.source_module_for_core = candidate_aware_core
        need(gate.source_module_for_core is candidate_aware_core
             and counters["other_family_overlays"] == 0
             and counters["native_libraries_loaded_by_overlay"] == 0,
             "reject non-Rust, matcher, native, or cross-family overlay")
        return gate

    producer.load_module = guarded_loader
    return counters


def install_full_failure_publication(legacy: types.ModuleType,
                                     parent: types.ModuleType) -> None:
    parent.install_exhaustive_publication(legacy)
    original = legacy.preserve_actual_campaign
    need(callable(original),
         "retain the actual authenticated 13-row durable Rust publisher")

    def preserve(report: dict, helper: object, recovery: object,
                 publication: object, ledger: dict) -> dict:
        rows = report.get("suite_results") if type(report) is dict else None
        need(type(rows) is list and len(rows) == 13,
             "preserve all actual original worker rows before diagnostics")
        all_failures = []
        for row in rows:
            if row.get("failure_class") != "INFRASTRUCTURE FAILURE":
                continue
            process = row.get("process")
            need(type(process) is dict and type(process.get("pid")) is int
                 and row.get("actual_worker_started") is True
                 and row.get("fully_observed") is False
                 and row.get("mismatch_count") == "NOT MEASURED"
                 and type(row.get("worker_failure_diagnostics")) is dict,
                 "never misclassify a real incomplete worker as semantics")
            stdout = process.get("stdout")
            stderr = process.get("stderr")
            traceback = row.get("traceback")
            need(type(stdout) is dict and type(stderr) is dict
                 and type(traceback) is dict,
                 "preserve each actual failure stream and active traceback")
            all_failures.append({
                "suite": row["suite"],
                "case_execution_denominator":
                    row["case_execution_denominator"],
                "pid": process["pid"],
                "returncode": process.get("returncode"),
                "error_type": row.get("error_type"),
                "error_message": row.get("error_message"),
                "stdout": dict(stdout),
                "stderr": dict(stderr),
                "traceback": dict(traceback),
                "worker_failure_diagnostics":
                    dict(row["worker_failure_diagnostics"]),
                "semantic_mismatch_count": "NOT MEASURED",
            })
        previous_writer = getattr(recovery, "write_evidence_receipt", None)
        need(callable(previous_writer),
             "retain the genuine exclusive fsynced V2 receipt writer")

        def write_all(name: str, receipt: dict) -> dict:
            need(type(receipt) is dict
                 and receipt.get("schema")
                 == SCHEMA + "-durable-publication-receipt"
                 and receipt.get("suite_count") == 13
                 and receipt.get("case_execution_denominator") == 31237
                 and receipt.get("all_four_original_targets_restored") is True,
                 "never publish crossed or unrestored real worker diagnostics")
            receipt["all_worker_failure_captures"] = all_failures
            receipt["all_worker_failure_capture_count"] = len(all_failures)
            receipt["all_worker_failure_capture_scope"] = (
                "COMPLETE INDIVIDUAL BOUNDED STDOUT STDERR TRACEBACK; "
                "ACTUAL INFRASTRUCTURE ONLY"
            )
            return previous_writer(name, receipt)

        recovery.write_evidence_receipt = write_all
        try:
            result = original(report, helper, recovery, publication, ledger)
        finally:
            recovery.write_evidence_receipt = previous_writer
        need(recovery.write_evidence_receipt is previous_writer
             and type(result) is dict,
             "restore the exact actual first-party durable receipt writer")
        result["all_worker_failure_captures"] = all_failures
        result["all_worker_failure_capture_count"] = len(all_failures)
        return result

    legacy.preserve_actual_campaign = preserve


def load_previous() -> tuple[types.ModuleType, types.ModuleType,
                             types.ModuleType, dict, dict, dict, dict, dict]:
    raw = secure_owner(V19[0])
    secure_owner(V19[1])
    secure_owner(V19[2])
    previous_campaign = types.ModuleType(
        "_rebar_v20_immutable_v19_original_campaign",
    )
    previous_campaign.__file__ = ROOT + "/" + V19[0][0]
    exec(compile(raw, previous_campaign.__file__, "exec", dont_inherit=True),
         previous_campaign.__dict__)
    need(previous_campaign.SOURCE == V19[0][0]
         and previous_campaign.PROTOCOL == V19[1][0]
         and previous_campaign.CONTRACT == V19[2][0]
         and previous_campaign.SCHEMA
         == "rebar-owned-repaired-rust-original-campaign-v19"
         and previous_campaign.VERSION == 19
         and previous_campaign.BUILD_LABEL == BUILD_LABEL,
         "authenticate complete frozen V19 worker, guard, and recovery")
    ancestor, parent, previous_v18, previous_state, failure_v18, historical, recovery_v19 = (
        previous_campaign.load_previous()
    )
    previous_campaign.prepare_parent(
        parent, ancestor, previous_v18, failure_v18, historical,
        recovery_v19,
    )
    context, state = parent.verify_context(
        V19[0][1], V19[1][1], V19[2][1],
    )
    previous = previous_campaign.enrich(
        context, ancestor, previous_v18, failure_v18,
        recovery_v19,
    )
    need(previous.get("status") == "PASS"
         and previous.get("version") == 19
         and previous.get("source_sha256") == V19[0][1]
         and previous.get("protocol_sha256") == V19[1][1]
         and previous.get("contract_sha256") == V19[2][1]
         and previous.get("historical_v2_preflight_status") == "PASS"
         and previous.get("historical_recovery_prefix_verifier_status")
         == "PASS"
         and previous.get("suite_count") == 13
         and previous.get("case_execution_denominator") == 31237
         and previous.get("expanded_holdout_cases_opened") == 0,
         "retain fully authenticated historical helper and recovery proofs")
    actual = parent.document(
        state["original_base"], state["guard"],
        secure_owner(V19_RECEIPT),
        "actual complete small V19 original candidate failure receipt",
    )
    evidence = validate_actual_v19_receipt(actual, parent, state)
    observer = observer_source_proof()
    previous_campaign.SCHEMA = SCHEMA
    previous_campaign.VERSION = VERSION
    previous_campaign.SOURCE = SOURCE
    previous_campaign.PROTOCOL = PROTOCOL
    previous_campaign.CONTRACT = CONTRACT
    previous_campaign.LABEL = LABEL
    previous_campaign.RECOVERY_PREFIX = RECOVERY_PREFIX
    previous_campaign.RECOVERY_ROOT = RECOVERY_ROOT
    recovery = previous_campaign.static_recovery_verifier(
        parent, previous, state,
    )
    parent.runtime()
    return (previous_campaign, ancestor, parent, previous,
            state, evidence, historical, {"recovery": recovery,
                                           "observer": observer,
                                           "failure_v18": failure_v18})


def enrich(context: dict, campaign: types.ModuleType,
           ancestor: types.ModuleType, previous: dict,
           evidence: dict, proof: dict) -> dict:
    receipt = evidence["receipt"]
    first = evidence["first_diagnostic"]
    result = dict(context)
    result.update({
        "schema": SCHEMA + "-frozen-context",
        "version": VERSION,
        "previous_v19_source_sha256": V19[0][1],
        "previous_v19_protocol_sha256": V19[1][1],
        "previous_v19_contract_sha256": V19[2][1],
        "previous_v19_frozen_source_status": previous["status"],
        "actual_v19_failure_receipt_path": V19_RECEIPT[0],
        "actual_v19_failure_receipt_sha256": V19_RECEIPT[1],
        "actual_v19_failure_receipt_bytes": V19_RECEIPT[2],
        "actual_v19_failure_receipt_inode": V19_RECEIPT[3],
        "actual_v19_durable_publication_status": "PASS",
        "actual_v19_candidate_status": "FAIL",
        "actual_v19_candidate_qualified": False,
        "actual_v19_actual_candidate_workers": 13,
        "actual_v19_distinct_worker_process_count": 13,
        "actual_v19_completed_suite_count": 8,
        "actual_v19_fully_passing_suite_count": 6,
        "actual_v19_verified_passing_case_count": 12942,
        "actual_v19_fully_observed_semantic_mismatch_lower_bound": 1296,
        "actual_v19_substitution_observed_mismatch_count": 240,
        "actual_v19_shape_observed_mismatch_count": 1056,
        "actual_v19_total_semantic_mismatch_count": "NOT MEASURED",
        "actual_v19_infrastructure_failure_count": 5,
        "actual_v19_unobserved_infrastructure_case_count": 2935,
        "actual_v19_infrastructure_suites": list(FAILURE_SUITES),
        "actual_v19_infrastructure_underlying_causes_for_remaining_four":
            "NOT ESTABLISHED; V19 RECEIPT PUBLISHES FIRST FULL STREAM ONLY",
        "actual_v19_all_four_original_targets_restored": True,
        "actual_v19_restoration_verified_before_publication": True,
        "actual_v19_all_original_suite_rows_validated_before_publication": True,
        "actual_v19_complete_original_suite_integrity": [
            dict(row) for row in evidence["rows"]
        ],
        "actual_v19_first_producer_failure_suite": "original_bounded_v5",
        "actual_v19_first_producer_failure_observer":
            "observe_original_upstream",
        "actual_v19_first_producer_failure_type": "ActualSuiteFailure",
        "actual_v19_first_underlying_error_type": "OriginalSuiteError",
        "actual_v19_first_underlying_error_message": FIRST_FAILURE,
        "actual_v19_first_worker_stdout_sha256": FIRST_STDOUT_SHA,
        "actual_v19_first_worker_stderr_sha256": FIRST_STDERR_SHA,
        "actual_v19_first_worker_traceback_sha256": FIRST_TRACEBACK_SHA,
        "actual_v19_first_nested_failure_sha256": FIRST_INNER_SHA,
        "actual_v19_first_destructor_warning_count": 17,
        "actual_v19_destructor_defect_status":
            "ACTUALLY OBSERVED; NOT FIXED BY OBSERVER OVERLAY",
        "actual_v19_published_worker_failure_summary_count": 5,
        "actual_v19_all_remaining_worker_causes_proven": False,
        "actual_v19_receipt_archive_opened": False,
        "historical_upstream_harness_source_sha256": HARNESS[1],
        "historical_upstream_harness_source_bytes": HARNESS[2],
        "historical_public_core_source_sha256": CORE[1],
        "historical_public_core_source_bytes": CORE[2],
        "historical_direct_gate_source_sha256": DIRECT_GATE[1],
        "historical_original_producer_source_sha256": PRODUCER[1],
        "candidate_aware_harness_source_overlay_sites": 1,
        "candidate_aware_public_core_source_overlay_sites": 1,
        "candidate_aware_harness_actual_root_cause_reproduced": True,
        "candidate_aware_core_incompatibility":
            "AUTHENTICATED SOURCE-INFERRED; ACTUAL INDIVIDUAL CAUSE "
            "NOT ESTABLISHED",
        "candidate_aware_observer_overlay_scope":
            "ATTESTED RUST ONLY; STRICT GUARD INSTALLED BEFORE "
            "IN-MEMORY AUTHENTICATED ORIGINAL CALL",
        "candidate_aware_observer_changes_frozen_oracle_bytes": False,
        "candidate_aware_observer_changes_rust_candidate_bytes": False,
        "candidate_aware_observer_weakens_runtime_guard": False,
        "candidate_aware_observer_claims_semantic_repair": False,
        "future_all_failed_worker_diagnostics":
            "EACH COMPLETE BOUNDED STDOUT STDERR TRACEBACK IN REAL RECEIPT",
        "historical_recovery_prefix_verifier_status":
            proof["recovery"]["proof"]["status"],
        "historical_recovery_code_constants_changed": 1,
        "historical_recovery_function_wrapper_added": False,
        "historical_v2_preflight_status": "PASS",
        "historical_v7_premature_global_mutation_allowed": False,
        "historical_v7_scoped_promotion_wrapper_added": False,
        "actual_v17_entry_failure_sha256": ancestor.V17_FAILURE[1],
        "actual_v18_entry_failure_sha256": campaign.V18_FAILURE[1],
        "public_recovery_root": RECOVERY_ROOT,
        "recovery_lock_filename": "recoverable-controller-v20.lock",
        "expected_actual_evidence_stem":
            "repaired-rust-original-campaign-v16-rust-" + LABEL,
        "actual_v20_original_campaign_attempted": False,
        "actual_v20_worker_diagnostics_observed": 0,
        "actual_v20_candidate_semantic_mismatch_count": "NOT MEASURED",
        "first_actual_producer_diagnostic_schema": first["schema"],
        "actual_v19_archive_sha256_metadata_only":
            receipt["archive"]["sha256"],
    })
    return result


def corrected_controller(campaign: types.ModuleType,
                         parent: types.ModuleType, historical: dict):
    owners = historical["historical_owners"]
    historical_values = historical["v7_values"]

    def bind(state: dict, context: dict, bundle: dict | None,
             counts: dict[str, int]) -> types.ModuleType:
        runner = state["runner"]
        base = state["base"]
        guard = state["guard"]
        legacy = runner.bind_v16_legacy(context, guard, base, bundle, counts)
        fixed = campaign.replace_exact_recovery_prefix(legacy)
        need(fixed["status"] == "PASS"
             and fixed["recovery_code_constants_changed"] == 1
             and fixed["production_wrapper_added"] is False,
             "retain the exact authenticated V20 one-constant recovery proof")
        originals = tuple(legacy.SOURCE_OWNERS)
        need(len(originals) == 9,
             "preserve all nine authenticated original Rust sources")
        legacy.COMBINED_BRIDGE_SHA256 = parent.CAPTURE_SHA
        legacy.COMBINED_BRIDGE_BYTES = parent.CAPTURE_BYTES
        legacy.CORRECTED_ADAPTER_SHA256 = parent.ADAPTER_SHA
        legacy.CORRECTED_ADAPTER_BYTES = parent.ADAPTER_BYTES
        legacy.SOURCE_OWNERS = tuple(
            (path, parent.CAPTURE_SHA, parent.CAPTURE_BYTES)
            if path == "candidates/rust/py_bridge.c"
            else (path, parent.ADAPTER_SHA, parent.ADAPTER_BYTES)
            if path == "candidates/rust_candidate.py"
            else (path, fingerprint, count)
            for path, fingerprint, count in originals
        )
        need(tuple(legacy.corrected_source_tuples())
             == parent.CORRECTED_SOURCES,
             "retain the complete actual first-party V21 source closure")
        previous_loader = legacy.load_frozen_module

        def historical_first_loader(owner: object,
                                    name: str) -> types.ModuleType:
            module = previous_loader(owner, name)
            if (type(module) is types.ModuleType
                    and getattr(module, "SCHEMA", None)
                    == "rebar-owned-repaired-rust-original-campaign-v7"):
                original_rows = tuple(module.ORIGINAL_SOURCE_OWNERS)
                need(len(original_rows) == 9
                     and original_rows[0]
                     == ("candidates/rust_candidate.py",
                         "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
                         31151)
                     and original_rows[1]
                     == ("candidates/rust/py_bridge.c",
                         "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
                         175676)
                     and original_rows[2:] == parent.CORRECTED_SOURCES[2:]
                     and tuple(module.HISTORICAL_V2_REPAIRED_SOURCE_OWNERS)
                     == owners
                     and module.BRIDGE_SOURCE_SHA256
                     == historical_values["BRIDGE_SOURCE_SHA256"]
                     and module.BRIDGE_SOURCE_BYTES
                     == historical_values["BRIDGE_SOURCE_BYTES"]
                     and module.HISTORICAL_V2_REPAIRED_PUBLIC_SHA256
                     == historical_values[
                         "HISTORICAL_V2_REPAIRED_PUBLIC_SHA256"
                     ]
                     and module.HISTORICAL_V2_REPAIRED_PUBLIC_BYTES
                     == historical_values[
                         "HISTORICAL_V2_REPAIRED_PUBLIC_BYTES"
                     ]
                     and module.CORRECTED_PUBLIC_SHA256
                     == historical_values["CORRECTED_PUBLIC_SHA256"]
                     and module.CORRECTED_PUBLIC_BYTES
                     == historical_values["CORRECTED_PUBLIC_BYTES"]
                     and module.ENGINE_SHA256 == parent.ENGINE_SHA
                     and module.BRIDGE_SHA256
                     == historical_values["BRIDGE_SHA256"]
                     and callable(module.patched_v2_helpers),
                     "retain unchanged V7/V2 verification before promotion")
            if (bundle is not None
                    and type(module) is types.ModuleType
                    and getattr(module, "SCHEMA", None)
                    == "rebar-owned-six-family-original-p0-producer-v5"):
                need(getattr(owner, "path", None) == PRODUCER[0]
                     and getattr(owner, "sha256", None) == PRODUCER[1],
                     "patch only the authentic guard-bound V5 Rust observer")
                install_family_aware_observers(module, bundle, parent)
            return module

        legacy.load_frozen_module = historical_first_loader
        legacy.LOCK_NAME = "recoverable-controller-v20.lock"
        need(legacy.SCHEMA == SCHEMA and legacy.LABEL == LABEL
             and legacy.PUBLIC_RECOVERY_PRIVATE_PREFIX == RECOVERY_PREFIX
             and legacy.PUBLIC_RECOVERY_ROOT == RECOVERY_ROOT
             and legacy.BUILD_LABEL == BUILD_LABEL
             and legacy.VERIFIED_BUILD_PRIVATE_ROOT == parent.ROOT_PATH
             and legacy.VERIFIED_BUILD_PRIVATE_ROOT_DEVICE == parent.ROOT_DEVICE
             and legacy.VERIFIED_BUILD_PRIVATE_ROOT_INODE == parent.ROOT_INODE
             and legacy.VERIFIED_NATIVE_ENGINE_SHA256 == parent.ENGINE_SHA
             and legacy.VERIFIED_NATIVE_ENGINE_BYTES == parent.ENGINE_BYTES
             and legacy.VERIFIED_NATIVE_BRIDGE_SHA256 == parent.BRIDGE_SHA
             and legacy.VERIFIED_NATIVE_BRIDGE_BYTES == parent.BRIDGE_BYTES
             and legacy.BUILD[0].sha256 == parent.V21[0][1]
             and legacy.BUILD_RECEIPT.sha256 == parent.V21_PUBLICATION[1]
             and tuple(legacy.ROLE_ORDER) == tuple(base.ROLE_ORDER)
             and tuple(legacy.SUITES) == parent.SUITES,
             "retain the exact actual V21 roots, native roles, and recovery")
        if bundle is None:
            install_full_failure_publication(legacy, parent)
        return legacy

    return bind


def prepare_parent(parent: types.ModuleType, campaign: types.ModuleType,
                   ancestor: types.ModuleType, previous: dict,
                   evidence: dict, historical: dict, proof: dict) -> None:
    old_make_runner = parent.make_runner

    def make_runner(previous_controller: types.ModuleType) -> types.ModuleType:
        runner = old_make_runner(previous_controller)
        old_required = runner.actual_required_authority

        def required(base: types.ModuleType) -> dict[str, str]:
            values = dict(old_required(base))
            values.update({
                "previous_v19_source_sha256": V19[0][1],
                "previous_v19_protocol_sha256": V19[1][1],
                "previous_v19_contract_sha256": V19[2][1],
                "previous_v19_failure_receipt_sha256": V19_RECEIPT[1],
            })
            return values

        runner.actual_required_authority = required
        return runner

    def contract_document(context: dict) -> dict:
        result = enrich(context, campaign, ancestor, previous, evidence, proof)
        result["schema"] = SCHEMA + "-recoverable-source-freeze"
        result["status"] = "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
        result.pop("contract_sha256", None)
        return result

    parent.SOURCE = SOURCE
    parent.PROTOCOL = PROTOCOL
    parent.CONTRACT = CONTRACT
    parent.SCHEMA = SCHEMA
    parent.VERSION = VERSION
    parent.LABEL = LABEL
    parent.RECOVERY_PREFIX = RECOVERY_PREFIX
    parent.RECOVERY_ROOT = RECOVERY_ROOT
    parent.make_runner = make_runner
    parent.contract_document = contract_document
    parent.bind_captured_controller = corrected_controller(
        campaign, parent, historical,
    )


def rejected(call: object, label: str, parent: types.ModuleType,
             campaign: types.ModuleType, ancestor: types.ModuleType) -> str:
    need(callable(call), "require an actual bounded source-only V20 control")
    try:
        call()
    except (CampaignError, parent.CampaignError, campaign.CampaignError,
            ancestor.CampaignError, ValueError, TypeError, SyntaxError,
            UnicodeError, OSError):
        return label
    raise CampaignError("accepted an altered actual V19 observation: " + label)


def source_hostile_controls(parent: types.ModuleType,
                            campaign: types.ModuleType,
                            ancestor: types.ModuleType,
                            state: dict, evidence: dict,
                            historical: dict, proof: dict) -> list[str]:
    controls = campaign.recovery_controls(
        parent, ancestor, state, historical,
        proof["failure_v18"], proof["recovery"],
    )
    base = state["original_base"]
    guard = state["guard"]
    receipt = evidence["receipt"]
    for key, changed, label in (
        ("status", "FAIL", "reject-failed-durable-publication"),
        ("candidate_status", "PASS", "reject-invented-rust-candidate-pass"),
        ("candidate_qualified", True, "reject-invented-rust-qualification"),
        ("semantic_mismatch_count", 1296,
         "reject-false-global-semantic-total"),
        ("infrastructure_failure_count", 0,
         "reject-hidden-real-incomplete-workers"),
        ("completed_suite_count", 13,
         "reject-invented-complete-original-workers"),
        ("verified_passing_case_count", 14238,
         "reject-counting-semantic-losses-as-passes"),
        ("all_four_original_targets_restored", False,
         "reject-discarded-real-four-inode-restoration"),
        ("all_original_suite_rows_validated_before_publication", False,
         "reject-omitted-genuine-row-integrity"),
        ("original_v5_producer_source_sha256", "0" * 64,
         "reject-swapped-frozen-original-producer"),
        ("native_bridge_sha256", "0" * 64,
         "reject-crossed-real-rust-native-engine"),
        ("hidden_cases_read", 1, "reject-opened-hidden-cases"),
        ("holdout", "OPENED", "reject-opened-expanded-holdout"),
    ):
        hostile = parent.copy_document(guard, base, receipt)
        hostile[key] = changed
        controls.append(rejected(
            lambda value=hostile: validate_actual_v19_receipt(
                value, parent, state,
            ), label, parent, campaign, ancestor,
        ))
    for key, changed, label in (
        ("fully_observed", True,
         "reject-invented-complete-original-upstream-worker"),
        ("returncode", 0, "reject-invented-successful-original-worker"),
        ("mismatch_count", 0, "reject-silent-incomplete-original-case"),
        ("complete_original_row_sha256", "0" * 64,
         "reject-changed-real-complete-row-digest"),
    ):
        hostile = parent.copy_document(guard, base, receipt)
        hostile["suite_integrity"][0][key] = changed
        controls.append(rejected(
            lambda value=hostile: validate_actual_v19_receipt(
                value, parent, state,
            ), label, parent, campaign, ancestor,
        ))
    for offset, changed, label in (
        (7, 0, "reject-hidden-real-substitution-mismatch"),
        (8, 0, "reject-hidden-real-shape-mismatch"),
    ):
        hostile = parent.copy_document(guard, base, receipt)
        hostile["suite_integrity"][offset]["mismatch_count"] = changed
        controls.append(rejected(
            lambda value=hostile: validate_actual_v19_receipt(
                value, parent, state,
            ), label, parent, campaign, ancestor,
        ))
    for stream in ("stdout", "stderr"):
        for key, value, label in (
            ("source_sha256", "0" * 64, "wrong-sha256"),
            ("complete", False, "incomplete"),
            ("captured_size_bytes", 1, "partial"),
            ("base64", "AAAA", "substituted-bytes"),
        ):
            hostile = parent.copy_document(guard, base, receipt)
            hostile["worker_failure_capture"]["first_worker_failure"]\
                [stream][key] = value
            controls.append(rejected(
                lambda item=hostile: validate_actual_v19_receipt(
                    item, parent, state,
                ), "reject-real-" + stream + "-" + label,
                parent, campaign, ancestor,
            ))
    observer = proof["observer"]
    for raw, owner, function, line, keyword, label in (
        (observer["harness"], HARNESS,
         "authenticate_original_sources", 211, "wrong",
         "reject-crossed-authentic-original-harness-keyword"),
        (observer["core"], CORE,
         "load_prerequisites", 483, "wrong",
         "reject-crossed-authentic-public-core-keyword"),
    ):
        controls.append(rejected(
            lambda material=raw, item=owner, name=function,
            lineno=line, argument=keyword:
                clean_candidate_aware_source(
                    material, item, name, lineno, argument,
                ), label, parent, campaign, ancestor,
        ))
    for owner, function, line, keyword, label in (
        (HARNESS, "authenticate_original_sources", 212, "candidate",
         "reject-relocated-original-harness-verification"),
        (CORE, "load_prerequisites", 484, "candidate_loaded",
         "reject-relocated-public-core-verification"),
    ):
        raw = observer["harness"] if owner == HARNESS else observer["core"]
        controls.append(rejected(
            lambda material=raw, item=owner, name=function,
            lineno=line, argument=keyword:
                clean_candidate_aware_source(
                    material, item, name, lineno, argument,
                ), label, parent, campaign, ancestor,
        ))
    need(observer_source_proof()["status"] == "PASS",
         "restore both clean immutable family-aware observer proofs")
    return controls


def help_text() -> str:
    return (
        "Frozen first-party Rust original correctness campaign V20\n"
        "Authenticates all real V19 losses and guards original observers "
        "with exact one-call, Rust-only in-memory overlays.\n"
        "Source-only: --render-contract | --self-test | "
        "--verify-frozen-context\n"
        "Actual, separately authorized: --run | --worker | --recover\n"
        "Always pin --source-sha256 and --protocol-sha256; all but "
        "--render-contract require --contract-sha256.\n"
        "No source mode activates a candidate, compiler, native library, "
        "archive, private root, clock, benchmark, or holdout.\n"
    )


def actual_failure(parent: types.ModuleType, guard: types.ModuleType,
                   options: dict | None, error: BaseException) -> dict:
    candidate = sys.modules.get("re")
    guarded = (
        type(options) is dict and options.get("mode") == "--worker"
        and type(candidate) is types.ModuleType
        and candidate is sys.modules.get("candidates.rust_candidate")
        and "_sre" not in sys.modules
    )
    if guarded:
        return {
            "schema": SCHEMA + "-actual-original-suite-worker-failure",
            "status": "FAIL",
            "failure_class": "INFRASTRUCTURE FAILURE",
            "version": VERSION,
            "suite": options.get("suite"),
            "error_type": type(error).__name__,
            "error_message": str(error)[:8192],
            "actual_candidate_workers": 1,
            "actual_candidate_imports": 1,
            "actual_native_libraries_loaded": 2,
            "runtime_guard_installed_before_candidate_import": True,
            "actual_candidate_case_count": 0,
            "semantic_mismatch_count": "NOT MEASURED",
            "candidate_qualified": False,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
    return {
        "schema": SCHEMA + "-entry-failure",
        "status": "FAIL",
        "version": VERSION,
        "error_type": type(error).__name__,
        "error_message": str(error)[:8192],
        **parent.zero_effects(),
    }


def main(arguments: list[str] | None = None) -> int:
    values = list(sys.argv[1:] if arguments is None else arguments)
    if values == ["--help"]:
        sys.stdout.write(help_text())
        return 0
    guard = None
    options = None
    try:
        campaign, ancestor, parent, previous, prior_state, evidence, historical, proof = (
            load_previous()
        )
        guard = prior_state["guard"]
        prepare_parent(parent, campaign, ancestor,
                       previous, evidence, historical, proof)
        options = parent.parse_options(values)
        mode = options["mode"]
        context, state = parent.verify_context(
            options["source_sha256"], options["protocol_sha256"],
            options.get("contract_sha256"),
            rendering=mode == "--render-contract",
        )
        context = enrich(context, campaign, ancestor,
                         previous, evidence, proof)
        state["historical_v2"] = historical
        state["v17_failure"] = parent.document(
            state["original_base"], guard,
            secure_owner(ancestor.V17_FAILURE),
            "actual V17 immutable first-source historical failure",
        )
        state["v18_failure"] = proof["failure_v18"]
        state["actual_v19_receipt"] = evidence
        if mode == "--render-contract":
            result = parent.contract_document(context)
        elif mode in ("--self-test", "--verify-frozen-context"):
            allowed = parent.allowed_source_paths(state["parent"])
            allowed.update(
                ROOT + "/" + owner[0]
                for owner in (
                    *V19, *campaign.V18,
                    *ancestor.V17, ancestor.V7, *ancestor.V2,
                    ancestor.V17_FAILURE, campaign.V18_FAILURE,
                    campaign.V11, V19_RECEIPT, HARNESS, CORE,
                    DIRECT_GATE, PRODUCER,
                )
            )
            wall = parent.StrictSourceWall(allowed)
            wall.install()
            if mode == "--self-test":
                result = dict(context)
                result["schema"] = SCHEMA + "-source-self-test"
                checks = parent.hostile_controls(context, state, wall)
                checks.extend(source_hostile_controls(
                    parent, campaign, ancestor, state,
                    evidence, historical, proof,
                ))
                need(len(checks) >= 200,
                     "require every authentic actual-loss hostile control")
                result["hostile_controls"] = checks
                result["hostile_control_count"] = len(checks)
                result["physically_blocked_effects"] = dict(wall.blocked)
            else:
                result = context
            parent.runtime()
        else:
            result = parent.actual_operation(options, context, state)
        payload = guard.canonical(result)
        need(type(payload) is bytes and 0 < len(payload) <= 1024 * 1024,
             "bound complete authentic V20 source or genuine campaign output")
        sys.stdout.buffer.write(payload)
        sys.stdout.buffer.flush()
        return 0 if result.get("status") in (
            "PASS", "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED",
        ) else 1
    except Exception as error:
        if guard is not None:
            try:
                sys.stdout.buffer.write(
                    guard.canonical(actual_failure(
                        parent, guard, options, error,
                    )),
                )
                sys.stdout.buffer.flush()
            except (OSError, TypeError, ValueError):
                pass
        else:
            sys.stderr.write("V20 campaign rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
