#!/usr/bin/env python3
"""Publish the complete failed, public-practice-only Rust V1 profiling run."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import stat
import sys


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SELF = "tools/render_rust_public_profile_v1_failure.py"
SESSION = "experiments/rust_public_profile_v1/public-run-001"
SVG_OUTPUT = "docs/evidence/rust-public-practice-overall-v1.svg"
INPUTS_OUTPUT = "docs/evidence/rust-public-practice-overall-v1.inputs.json"
FAILURE_OUTPUT = "oracle/phase3/evidence/rust-public-profile-v1-run-001-prepublication-failure.json"
EVIDENCE_DIRECTORY = "oracle/phase3/evidence"
SCHEMA = "rebar-rust-fresh-public-profile-v1"
PUBLIC_LABEL = "FRESH PUBLIC PRACTICE ONLY; NOT A HOLDOUT OR FINAL BENCHMARK"
MATRIX_SHA256 = "b13ff74122041ea792774fd5ee2d1f6d38033e94a1a6703c6e48522e461552a7"
RECORDS_SHA256 = "41f83dc761a93ea8e3203f46cedbba1e10918cf053194c20b37b8c209e992242"
PAIRED_ROWS_SHA256 = "ce5ddb143be0d58588d2b18540c0db1b716eebb138cfe32a04690a0efe62c378"
PUBLISHED_SEED = 0x5255_5354_5052_4F31
UNMEASURED = "NOT MEASURED"
DRIVER = ("tools/rust_public_profile_v1.py", "ada1e9cfc8684ecb4fcf9294057347018b6058fc1619ae9de6a8b31097aa1562", 79693)
PROTOCOL = ("oracle/phase3/RUST-PUBLIC-PROFILE-V1.md", "6664f17ddd65c1953782f43b7fe1fa01427f1f510adfbad86fe8efdb135829ba", 5281)
MANIFEST = ("oracle/phase3/rust-public-profile-v1.json", "b791b141eabbf6eb8a67484f5deb82bb41e324aedbdfe5b53a98ebc1553372c5", 1797)
STDLIB_CORRECTNESS = (SESSION + "/stdlib.correctness.raw.json", "efe0a3cc37194290b9577d5bd4f502a5c482016bc2b8ae90acec6254545b5381", 445036)
RUST_CORRECTNESS = (SESSION + "/rust.correctness.raw.json", "8774ad035e17126252803e75494a80d376386a85e13c46cb3e0380b82dae89b0", 445394)
PAIRED = (SESSION + "/paired-timing.raw.json", "3da06bdb04ace9897d359aaa962ca412f3e9260a5c1a337703e0aa35567b6b85", 504907)
COLLECTOR_STDOUT = (SESSION + "/stdlib.collector.stdout.json", "057d2eb19a2c24e11688fa0419047e50f6720cbafd41b7ec3bd7ee763691aff0", 2200)
COLLECTOR_STDERR = (SESSION + "/stdlib.collector.stderr.txt", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 0)
HEAPTRACE = (SESSION + "/stdlib.er/heaptrace", "4fad5c396e49e7319fab843bd566f2c0013ce301d0eb7f3c5c26b1805fa3958c", 45219840)
ROUNDS = {
    ("stdlib", 0): (SESSION + "/stdlib.timing-round-00.raw.json", "df4e0c405409a38512276b0ffdb78417c87e84d036675d6d3b7a3a8300df9295", 121115, 83),
    ("rust", 0): (SESSION + "/rust.timing-round-00.raw.json", "e624f4adf0b975013b1666ee35bf8c03ccf9263fe009fa31a069b3edda5bbbd6", 121499, 84),
    ("stdlib", 1): (SESSION + "/stdlib.timing-round-01.raw.json", "23f932f097f90eebab9bbf9fdb8b35666505cb4fca7281f996ef51d7683b866a", 121117, 86),
    ("rust", 1): (SESSION + "/rust.timing-round-01.raw.json", "403fd14e281f3b6e104d588c6821b938040e544eea44e01f24e8a5468379d08b", 121500, 85),
    ("stdlib", 2): (SESSION + "/stdlib.timing-round-02.raw.json", "2c849dfc1585baa863f39441da1fb226fed2a607ca69304fe2679b83383df471", 121123, 87),
    ("rust", 2): (SESSION + "/rust.timing-round-02.raw.json", "8018f23aa8d3716937a1f5956e11b9bd5c2389f4e2c66df37eb323e6ddc2b822", 121498, 88),
    ("stdlib", 3): (SESSION + "/stdlib.timing-round-03.raw.json", "749c7fab9af672255104a8b4ca33c667683faa7e009492321862c596426bd1f8", 121114, 90),
    ("rust", 3): (SESSION + "/rust.timing-round-03.raw.json", "bb7e9452fb4a80c107a5496d55ed129b17fce4e9a42d517672901fa1f0fcd4f2", 121501, 89),
}
OPERATIONS = (
    "module.compile", "module.search", "module.match", "module.fullmatch",
    "module.findall", "module.finditer", "module.split", "module.sub.literal",
    "module.sub.callback", "module.subn.literal", "pattern.search", "pattern.match",
    "pattern.fullmatch", "pattern.findall", "pattern.finditer", "pattern.split",
    "pattern.sub.literal", "pattern.sub.callback", "pattern.subn.literal",
    "pattern.scanner.search", "pattern.scanner.match", "pattern.scanner.loop",
    "scanner.scan", "match.group", "match.expand", "compile.fresh.search",
)
COHORT_LABELS = {
    "anchored_multiline_public": "Anchored multiline matching",
    "mandatory_literal_dense_same_first_byte": "Dense same-letter no-match",
    "overflow_assertion_guard_heap_spill": "Large lookahead capture guards",
    "overflow_capture_guard_heap_spill": "Large capture groups",
    "overflow_repeat_guard_heap_spill": "Deep bounded repetition",
    "scanner_and_callback_boundary": "Scanners and callbacks",
    "unicode_and_named_captures": "Unicode and named captures",
}
MISSING_PROFILE_OUTPUTS = (
    SESSION + "/summary.json",
    SESSION + "/rust.collector.stdout.json",
    SESSION + "/rust.collector.stderr.txt",
    SESSION + "/rust.er",
    SESSION + "/stdlib.cpu.txt",
    SESSION + "/stdlib.ffi.txt",
    SESSION + "/stdlib.allocations.txt",
    SESSION + "/stdlib.heap.txt",
    SESSION + "/rust.cpu.txt",
    SESSION + "/rust.ffi.txt",
    SESSION + "/rust.allocations.txt",
    SESSION + "/rust.heap.txt",
)


class Rejected(ValueError):
    """A public source, raw observation, denominator, or loss was altered."""


def require(value: bool, message: str) -> None:
    if not value:
        raise Rejected(message)


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                       sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_sha256(value: object) -> str:
    return sha256(canonical(value))


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(type(key) is str and key not in result, "duplicate public evidence JSON key")
        result[key] = value
    return result


def parsed(raw: bytes, label: str, *, canonical_required: bool = True) -> dict:
    try:
        value = json.loads(raw, object_pairs_hook=unique_object,
                           parse_constant=lambda _: (_ for _ in ()).throw(Rejected("nonfinite JSON")))
    except (UnicodeError, ValueError, TypeError) as failure:
        raise Rejected("invalid public evidence JSON: " + label) from failure
    require(type(value) is dict and (not canonical_required or canonical(value) == raw),
            "noncanonical public evidence JSON: " + label)
    return value


def specs() -> tuple[tuple[str, str, int], ...]:
    result = (DRIVER, PROTOCOL, MANIFEST, STDLIB_CORRECTNESS, RUST_CORRECTNESS,
              PAIRED, COLLECTOR_STDOUT, COLLECTOR_STDERR, HEAPTRACE)
    return result + tuple((path, fingerprint, size) for path, fingerprint, size, _ in ROUNDS.values())


class SourceWall:
    """Permit exact public evidence reads and only the three owned report outputs."""

    def __init__(self, render: bool) -> None:
        self.render = render
        self.owners = frozenset(os.path.join(ROOT, item[0]) for item in specs()) | {
            os.path.join(ROOT, SELF)
        }
        self.outputs = frozenset(os.path.join(ROOT, item)
                                 for item in (SVG_OUTPUT, INPUTS_OUTPUT, FAILURE_OUTPUT))
        self.evidence_directory = os.path.join(ROOT, EVIDENCE_DIRECTORY)

    def check(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 and type(arguments[2]) is int else 0
            require(type(path) is str, "source wall rejected an unapproved descriptor")
            writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if writing:
                required = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                require(self.render and path in self.outputs and flags & required == required,
                        "source wall rejected a nonexclusive or unowned write")
            else:
                require(path in self.owners and bool(flags & os.O_NOFOLLOW),
                        "source wall rejected candidate, native, archive, profiler, or holdout access")
            return
        if event == "os.mkdir":
            require(self.render and arguments and arguments[0] == self.evidence_directory,
                    "source wall rejected an unowned directory mutation")
            return
        if (event.startswith(("subprocess.", "socket.", "ctypes.", "os.exec", "os.spawn"))
                or event in {"os.system", "os.fork", "os.posix_spawn", "os.remove", "os.rename",
                             "os.rmdir", "os.chdir", "os.chmod", "os.link", "os.symlink",
                             "os.truncate", "os.putenv", "time.time", "time.monotonic",
                             "time.perf_counter", "_thread.start_new_thread"}):
            raise Rejected("source wall rejected process, profiler, network, clock, or mutation")
        if event == "import" and arguments:
            name = arguments[0]
            require(not (type(name) is str and (name in {"re", "_sre", "ctypes", "subprocess"}
                                                or name.startswith(("candidates.", "rebar.")))),
                    "source wall rejected matching or candidate imports")


def authenticated_owner(spec: tuple[str, str, int], *, keep: bool = True) -> bytes | None:
    path, expected, size = spec
    descriptor = os.open(os.path.join(ROOT, path), os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        metadata = os.fstat(descriptor)
        require(stat.S_ISREG(metadata.st_mode) and stat.S_IMODE(metadata.st_mode) == 0o600
                and metadata.st_nlink == 1 and metadata.st_uid == os.getuid()
                and metadata.st_size == size,
                "public source/evidence identity, size, ownership, or mode changed: " + path)
        hasher = hashlib.sha256()
        chunks = [] if keep else None
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            hasher.update(block)
            if chunks is not None:
                chunks.append(block)
        require(hasher.hexdigest() == expected, "complete public evidence digest changed: " + path)
        return b"".join(chunks) if chunks is not None else None
    finally:
        os.close(descriptor)


def same(value: object, expected: dict, label: str) -> None:
    require(type(value) is dict, "expected public evidence object: " + label)
    for key, item in expected.items():
        require(value.get(key) == item, label + ": altered " + key)


def encode_typed(value: object) -> dict:
    if type(value) is str:
        return {"kind": "str", "value": value}
    if type(value) is bytes:
        return {"kind": "bytes", "hex": value.hex()}
    if type(value) is bytearray:
        return {"kind": "bytearray", "hex": bytes(value).hex()}
    if type(value) is memoryview:
        return {"kind": "memoryview", "hex": value.tobytes().hex(),
                "readonly": value.readonly, "format": value.format, "shape": list(value.shape)}
    raise Rejected("nonpublic original matrix value")


def matrix() -> list[dict]:
    capture = "(?:" + "(a)" * 40 + "){2}Z"
    assertion = "(?=(?:" + "(a)" * 36 + ")Z)a{36}Z"
    datasets = (
        ("text.dense-first-byte.literal.no-match", "text", "AAAAAAB", "A" * 2048 + "C", 0, "mandatory_literal_dense_same_first_byte"),
        ("text.dense-first-byte.alternation.no-match", "text", "(?:AAAAAAB|AAAAAAC)", "A" * 2048 + "D", 0, "mandatory_literal_dense_same_first_byte"),
        ("text.capture.guard.spill", "text", capture, "a" * 80 + "Z", 0, "overflow_capture_guard_heap_spill"),
        ("text.repeat.guard.spill", "text", r"(?:(?:ab){16}){4}Z", "ab" * 64 + "Z", 0, "overflow_repeat_guard_heap_spill"),
        ("text.assertion.guard.spill", "text", assertion, "a" * 36 + "Z", 0, "overflow_assertion_guard_heap_spill"),
        ("text.unicode.named.words", "text", r"(?P<token>[^\W\d_]+)(?P<digits>\d*)", "Éclair42 Ζeta7 naïve3 cedar8", 0, "unicode_and_named_captures"),
        ("text.scanner.remainder", "text", r"(?P<token>[A-Za-z]+)(?P<digits>\d*)", "oak12 pine7 !fresh-tail9", 0, "scanner_and_callback_boundary"),
        ("text.multiline.anchors", "text", r"^(?P<token>[a-z]+)(?P<digits>\d*)$", "maple7\nCEDAR8\nspruce9", 10, "anchored_multiline_public"),
        ("bytes.dense-first-byte.literal.no-match", "bytes", b"AAAAAAB", b"A" * 2048 + b"C", 0, "mandatory_literal_dense_same_first_byte"),
        ("bytes.dense-first-byte.alternation.no-match", "bytes", rb"(?:AAAAAAB|AAAAAAC)", memoryview(b"A" * 2048 + b"D"), 0, "mandatory_literal_dense_same_first_byte"),
        ("bytes.capture.guard.spill", "bytes", capture.encode("ascii"), bytearray(b"a" * 80 + b"Z"), 0, "overflow_capture_guard_heap_spill"),
        ("bytes.repeat.guard.spill", "bytes", rb"(?:(?:ab){16}){4}Z", b"ab" * 64 + b"Z", 0, "overflow_repeat_guard_heap_spill"),
        ("bytes.assertion.guard.spill", "bytes", assertion.encode("ascii"), b"a" * 36 + b"Z", 0, "overflow_assertion_guard_heap_spill"),
        ("bytes.high-bit.named.words", "bytes", rb"(?P<token>[A-Za-z]+)(?P<digits>\d*)", b"\xe9oak42 cedar7 \xfffir3", 0, "unicode_and_named_captures"),
        ("bytes.scanner.mutable-memoryview.remainder", "bytes", rb"(?P<token>[A-Za-z]+)(?P<digits>\d*)", memoryview(bytearray(b"oak12 pine7 !fresh-tail9")), 0, "scanner_and_callback_boundary"),
        ("bytes.multiline.anchors", "bytes", rb"^(?P<token>[a-z]+)(?P<digits>\d*)$", b"maple7\nCEDAR8\nspruce9", 10, "anchored_multiline_public"),
    )
    values = []
    for dataset_index, (dataset, domain, expression, subject, flags, cohort) in enumerate(datasets):
        phrase = r"[A-Za-z]+\d*" if domain == "text" else rb"[A-Za-z]+\d*"
        replacement = r"<\g<0>>" if domain == "text" else rb"<\g<0>>"
        for operation_index, operation in enumerate(OPERATIONS):
            lifecycle = ("fresh-native-compile" if operation == "compile.fresh.search"
                         else "native-scanner-boundary" if operation == "scanner.scan"
                         else "module-call" if operation.startswith("module.")
                         else "live-match" if operation.startswith("match.")
                         else "live-pattern-scanner" if ".scanner." in operation
                         else "precompiled-pattern")
            values.append({
                "case": "rust-public-profile.v1." + format(len(values), "04d"),
                "dataset": dataset, "domain": domain, "cohort": cohort,
                "operation": operation, "lifecycle": lifecycle,
                "pattern": encode_typed(expression), "subject": encode_typed(subject),
                "replacement": encode_typed(replacement), "scanner_phrase": encode_typed(phrase),
                "flags": flags,
                "limit": 1 + (PUBLISHED_SEED + dataset_index * 37 + operation_index * 11) % 3,
                "weight_numerator": 1,
            })
    require(len(values) == 416 and json_sha256(values) == MATRIX_SHA256,
            "the complete original 416-case public matrix changed")
    return values


def verify_manifest(manifest: dict, protocol: bytes) -> None:
    same(manifest, {
        "schema": SCHEMA + "-source-freeze", "source": DRIVER[0], "source_sha256": DRIVER[1],
        "published_seed": PUBLISHED_SEED, "matrix_sha256": MATRIX_SHA256,
        "case_count": 416, "dataset_count": 16, "operation_count": 26,
        "approved_output_prefix": "experiments/rust_public_profile_v1",
        "pinned_cpython": "3.14.6", "pinned_python": PYTHON,
    }, "committed public-only V1 source manifest")
    same(manifest.get("profile_configuration"),
         {"batch_iterations": 3, "paired_rounds": 4, "profile_passes": 3,
          "warmup_iterations": 1, "reports": ["allocations", "cpu", "ffi", "heap"]},
         "committed public-only profiling configuration")
    same(manifest.get("provenance"), {
        "data": "fresh embedded public literals only", "fixture_files_read": 0,
        "archive_files_read": 0, "holdout_files_read": 0,
        "candidate_imports_in_source_modes": 0,
        "source_mode_clock_samples": 0, "source_mode_workspace_mutations": 0,
    }, "committed public-only source-mode guarantees")
    same(manifest.get("profiler"), {
        "command": "/usr/bin/gprofng", "archive_policy": "off",
        "descendant_policy": "off", "clock_sampling": "hi", "heap_tracing": "on",
    }, "committed public gprofng collection policy")
    for token in (b"fresh public practice only", b"416 public cases", b"26 public operations",
                  b"NOT", b"gprofng", b"--run", b"holdout", b"summary.json"):
        require(token.lower() in protocol.lower(), "public V1 protocol omitted " + token.decode())


def verify_worker_identity(document: dict, *, engine: str, role: str, schema: str, pid: int) -> None:
    same(document, {
        "schema": SCHEMA + "-isolated-" + schema, "status": "PASS", "label": PUBLIC_LABEL,
        "role": role, "engine": engine, "pid": pid, "python": "3.14.6",
        "published_seed": PUBLISHED_SEED, "matrix_sha256": MATRIX_SHA256,
        "case_count": 416, "fixture_files_read": 0, "archive_files_read": 0,
        "holdout_files_read": 0, "files_written": 0,
    }, "isolated actual public " + engine + " " + schema + " worker")
    imports = document.get("candidate_import_count")
    require((engine == "stdlib" and imports == 0)
            or (engine == "rust" and type(imports) is int and imports == 3),
            "actual isolated public worker engine was substituted")
    provenance = document.get("engine_provenance")
    require(type(provenance) is dict, "actual isolated public worker lost provenance")
    if engine == "stdlib":
        same(provenance, {
            "stdlib_origin": "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/__init__.py",
        }, "actual CPython public worker provenance")
    else:
        same(provenance, {
            "adapter_origin": "/home/dev-user/src/rebar/candidates/rust_candidate.py",
            "bridge_origin": "/home/dev-user/src/rebar/candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
            "candidate_owned_forbidden_import_attempts": [],
        }, "actual first-party Rust public worker provenance")
        require(provenance.get("native_bridge_exports")
                == ["compile", "compile_scanner", "run", "collect", "pattern_match",
                    "pattern_type", "pattern_descriptors", "bind"],
                "actual first-party Rust native bridge exports changed")


def verify_correctness(context: dict) -> dict[str, dict]:
    actual_matrix = context["matrix"]
    baseline = context["stdlib_correctness"]
    rust = context["rust_correctness"]
    verify_worker_identity(baseline, engine="stdlib", role="public-profile-correctness-stdlib",
                           schema="observations", pid=81)
    verify_worker_identity(rust, engine="rust", role="public-profile-correctness-rust",
                           schema="observations", pid=82)
    for worker in (baseline, rust):
        same(worker, {"records_sha256": RECORDS_SHA256,
                      "clock_samples": 0, "timing_trials_run": 0},
             "complete untimed public-practice correctness vector")
        records = worker.get("records")
        require(type(records) is list and len(records) == 416
                and json_sha256(records) == RECORDS_SHA256,
                "a complete public-practice correctness observation was removed")
        for record, case in zip(records, actual_matrix, strict=True):
            require(type(record) is dict and set(record) == {"case", "outcome"}
                    and record["case"] == case["case"] and type(record["outcome"]) is dict,
                    "a public-practice correctness case was changed or reordered")
    require(baseline["records"] == rust["records"] and baseline["pid"] != rust["pid"],
            "all 416 isolated public-practice outcomes did not match byte for byte")
    return {record["case"]: record["outcome"] for record in baseline["records"]}


def expected_case_order(round_number: int, actual_matrix: list[dict]) -> list[str]:
    case_ids = [case["case"] for case in actual_matrix]
    offset = (PUBLISHED_SEED + round_number * 37) % len(case_ids)
    order = case_ids[offset:] + case_ids[:offset]
    return list(reversed(order)) if round_number % 2 else order


def verify_timing_workers(context: dict, outcomes: dict[str, dict]) -> None:
    for (engine, round_number), spec in ROUNDS.items():
        document = context["rounds"][(engine, round_number)]
        verify_worker_identity(document, engine=engine,
                               role="public-timing-" + format(round_number, "02d") + "-" + engine,
                               schema="timing", pid=spec[3])
        same(document, {
            "expected_records_sha256": RECORDS_SHA256, "round": round_number,
            "iterations": 3, "warmups": 1, "clock_samples": 832,
        }, "complete actual public paired-timing worker")
        rows = document.get("rows")
        require(type(rows) is list and len(rows) == 416
                and json_sha256(rows) == document.get("rows_sha256"),
                "an actual isolated public paired-timing row was removed")
        order = expected_case_order(round_number, context["matrix"])
        for index, row in enumerate(rows):
            require(type(row) is dict and set(row) == {
                "case", "cohort", "correctness_checks", "elapsed_ns", "expected_outcome_sha256",
                "iterations", "operation", "position", "round",
            }, "actual isolated public paired-timing row fields changed")
            case = context["matrix_by_case"][order[index]]
            same(row, {
                "case": order[index], "cohort": case["cohort"],
                "operation": case["operation"], "position": index,
                "round": round_number, "iterations": 3, "correctness_checks": 5,
                "expected_outcome_sha256": json_sha256(outcomes[order[index]]),
            }, "actual isolated public paired-timing case")
            require(type(row["elapsed_ns"]) is int and row["elapsed_ns"] > 0,
                    "a positive actual paired public elapsed observation vanished")


def verify_paired(context: dict) -> list[dict]:
    paired = context["paired"]
    same(paired, {"schema": SCHEMA + "-paired-timing-rows",
                  "matrix_sha256": MATRIX_SHA256, "rows_sha256": PAIRED_ROWS_SHA256},
         "actual complete public-practice paired timing")
    rows = paired.get("rows")
    require(type(rows) is list and len(rows) == 1664
            and json_sha256(rows) == PAIRED_ROWS_SHA256,
            "an actual public-practice paired timing row was removed or altered")
    worker_pids = set()
    for index, row in enumerate(rows):
        require(type(row) is dict and set(row) == {
            "baseline_elapsed_ns", "baseline_pid", "case", "cohort",
            "correctness_checks_per_engine", "iterations", "operation", "pair_order",
            "position", "round", "rust_elapsed_ns", "rust_pid",
        }, "actual public-practice paired timing row shape changed")
        round_number, position = divmod(index, 416)
        baseline = context["rounds"][("stdlib", round_number)]
        rust = context["rounds"][("rust", round_number)]
        baseline_row = baseline["rows"][position]
        rust_row = rust["rows"][position]
        expected_order = ["stdlib", "rust"] if round_number % 2 == 0 else ["rust", "stdlib"]
        same(row, {
            "case": baseline_row["case"], "round": round_number, "position": position,
            "cohort": baseline_row["cohort"], "operation": baseline_row["operation"],
            "pair_order": expected_order, "baseline_pid": baseline["pid"],
            "rust_pid": rust["pid"], "iterations": 3,
            "correctness_checks_per_engine": 5,
            "baseline_elapsed_ns": baseline_row["elapsed_ns"],
            "rust_elapsed_ns": rust_row["elapsed_ns"],
        }, "actual public-practice paired observation")
        require(rust_row["case"] == baseline_row["case"] and baseline["pid"] != rust["pid"],
                "an actual public-practice pair lost isolated original/Rust processes")
        worker_pids.update((baseline["pid"], rust["pid"]))
    require(worker_pids == {83, 84, 85, 86, 87, 88, 89, 90},
            "an actual paired public timing worker was substituted or reused")
    return rows


def verify_incomplete_profile(context: dict) -> dict:
    stdout = context["collector_stdout"]
    require(context["collector_stderr"] == b"", "genuine public stdlib collector stderr changed")
    banner, separator, raw_document = stdout.partition(b"\n")
    require(separator == b"\n"
            and banner == b"Creating experiment directory stdlib.er (Process ID: 91) ..."
            and raw_document.startswith(b"{") and raw_document.endswith(b"\n")
            and raw_document.count(b"\n") == 1,
            "the genuine gprofng pre-JSON stdout banner was hidden or fabricated")
    profile = parsed(raw_document, "genuine stdlib gprofng worker JSON after banner")
    verify_worker_identity(profile, engine="stdlib", role="public-profile-stdlib",
                           schema="profile", pid=91)
    same(profile, {"expected_records_sha256": RECORDS_SHA256,
                   "profile_passes": 3, "public_case_executions": 1248,
                   "elapsed_ns": 40102702327},
         "genuine incomplete stdlib-only public gprofng collection")
    require(type(profile.get("python_heap")) is dict,
            "the observed stdlib-only Python heap metadata disappeared")
    expected_executions = {name: (312 if name == "mandatory_literal_dense_same_first_byte" else 156)
                           for name in COHORT_LABELS}
    require(profile.get("executions_by_cohort") == expected_executions,
            "the complete 1,248 stdlib-only profiled public executions changed")
    missing = context.get("missing_profile_outputs")
    require(type(missing) is dict and set(missing) == set(MISSING_PROFILE_OUTPUTS)
            and all(value is True for value in missing.values()),
            "a Rust profile, native report, or successful session summary was fabricated")
    heap = context.get("heaptrace")
    same(heap, {"path": HEAPTRACE[0], "sha256": HEAPTRACE[1], "bytes": HEAPTRACE[2]},
         "genuine incomplete stdlib-only native heaptrace")
    return profile


def summarize(rows: list[dict]) -> dict:
    baseline = rust = faster = slower = ties = 0
    total_log = 0.0
    for row in rows:
        original = row["baseline_elapsed_ns"]
        candidate = row["rust_elapsed_ns"]
        baseline += original
        rust += candidate
        # Match the stable left-to-right public JavaScript accumulator exactly.
        total_log += math.log(original / candidate)
        faster += original > candidate
        slower += original < candidate
        ties += original == candidate
    require(rows and baseline > 0 and rust > 0,
            "an exact equal-case public-practice speed denominator disappeared")
    return {
        "paired_observation_count": len(rows), "baseline_total_ns": baseline,
        "rust_total_ns": rust, "equal_case_geometric_speedup": math.exp(total_log / len(rows)),
        "aggregate_total_elapsed_speedup": baseline / rust,
        "rust_faster_pair_count": faster, "rust_slower_pair_count": slower,
        "equal_pair_count": ties,
    }


def statistics(context: dict, rows: list[dict]) -> dict:
    by_cohort = {name: [] for name in COHORT_LABELS}
    by_operation = {name: [] for name in OPERATIONS}
    by_domain = {"text": [], "bytes": []}
    by_case = {case["case"]: [] for case in context["matrix"]}
    for row in rows:
        case = context["matrix_by_case"][row["case"]]
        by_cohort[row["cohort"]].append(row)
        by_operation[row["operation"]].append(row)
        by_domain[case["domain"]].append(row)
        by_case[row["case"]].append(row)
    overall = summarize(rows)
    same(overall, {
        "paired_observation_count": 1664, "baseline_total_ns": 96434251,
        "rust_total_ns": 161853767,
        "equal_case_geometric_speedup": 0.8485646292880136,
        "aggregate_total_elapsed_speedup": 0.5958109767071408,
        "rust_faster_pair_count": 723, "rust_slower_pair_count": 937,
        "equal_pair_count": 4,
    }, "all equal-weight actual public-practice observations")
    cohorts = {}
    for name, values in sorted(by_cohort.items()):
        require(len(values) == (416 if name == "mandatory_literal_dense_same_first_byte" else 208),
                "a balanced public-practice cohort was diluted: " + name)
        cohorts[name] = summarize(values)
    same(cohorts["mandatory_literal_dense_same_first_byte"], {
        "paired_observation_count": 416,
        "equal_case_geometric_speedup": 0.41613883193210616,
    }, "exact public-practice dense-prefix slowdown")
    for name, value in cohorts.items():
        if name != "mandatory_literal_dense_same_first_byte":
            require(value["equal_case_geometric_speedup"] > 1,
                    "another actual public-practice cohort was falsely reported faster")
    operations = {}
    for name, values in sorted(by_operation.items()):
        require(len(values) == 64, "an equal-weight public-practice operation was omitted: " + name)
        operations[name] = summarize(values)
    domains = {}
    for name, values in by_domain.items():
        require(len(values) == 832, "equal public text/bytes timing weights were changed")
        domains[name] = summarize(values)
    cases = []
    for case in context["matrix"]:
        values = by_case[case["case"]]
        require(len(values) == 4 and {row["round"] for row in values} == set(range(4)),
                "a balanced original public-practice case lost an exact paired round")
        cases.append({"case": case["case"], "dataset": case["dataset"],
                      "cohort": case["cohort"], "domain": case["domain"],
                      "operation": case["operation"], "results": summarize(values)})
    losses = []
    for row in rows:
        if row["baseline_elapsed_ns"] < row["rust_elapsed_ns"]:
            losses.append({
                "case": row["case"], "round": row["round"], "position": row["position"],
                "cohort": row["cohort"], "operation": row["operation"],
                "domain": context["matrix_by_case"][row["case"]]["domain"],
                "pair_order": row["pair_order"], "baseline_pid": row["baseline_pid"],
                "rust_pid": row["rust_pid"], "baseline_elapsed_ns": row["baseline_elapsed_ns"],
                "rust_elapsed_ns": row["rust_elapsed_ns"],
                "baseline_over_rust_speedup": row["baseline_elapsed_ns"] / row["rust_elapsed_ns"],
            })
    require(len(losses) == 937, "an observed slower Rust public-practice pair was hidden")
    return {"overall": overall, "by_cohort": cohorts, "by_operation": operations,
            "by_domain": domains, "by_case": cases,
            "every_slower_paired_observation": losses,
            "every_slower_paired_observation_sha256": json_sha256(losses)}


def verify_context(context: dict) -> dict:
    verify_manifest(context["manifest"], context["protocol"])
    actual_matrix = context["matrix"]
    require(len(actual_matrix) == 416 and json_sha256(actual_matrix) == MATRIX_SHA256,
            "the exact public-practice matrix denominator or cases changed")
    for operation in OPERATIONS:
        require(sum(case["operation"] == operation for case in actual_matrix) == 16,
                "a complete balanced public-practice operation was removed")
    require(sum(case["domain"] == "text" for case in actual_matrix)
            == sum(case["domain"] == "bytes" for case in actual_matrix) == 208,
            "public-practice text and bytes are not equally weighted")
    outcomes = verify_correctness(context)
    verify_timing_workers(context, outcomes)
    rows = verify_paired(context)
    profile = verify_incomplete_profile(context)
    metrics = statistics(context, rows)
    return {"profile": profile, "metrics": metrics}


def ref(spec: tuple[str, str, int]) -> dict:
    return {"path": spec[0], "sha256": spec[1], "bytes": spec[2]}


def escape(value: str) -> str:
    return (value.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def graph(metrics: dict) -> bytes:
    overall = metrics["overall"]
    pairs = overall["paired_observation_count"]
    rows = [
        ("mandatory_literal_dense_same_first_byte", "Dense same-letter no-match", "#fb7185"),
        ("anchored_multiline_public", "Anchored multiline matching", "#34d399"),
        ("overflow_assertion_guard_heap_spill", "Large lookahead capture guards", "#34d399"),
        ("overflow_capture_guard_heap_spill", "Large capture groups", "#34d399"),
        ("overflow_repeat_guard_heap_spill", "Deep bounded repetition", "#34d399"),
        ("scanner_and_callback_boundary", "Scanners and callbacks", "#34d399"),
        ("unicode_and_named_captures", "Unicode and named captures", "#34d399"),
    ]
    plot_x, plot_width, maximum = 485, 420, 1.4
    parity = plot_x + round(plot_width / maximum)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1480" height="1135" '
        'viewBox="0 0 1480 1135" role="img" aria-labelledby="title description">',
        '<title id="title">Public practice only: Rust is slower overall; profiling was incomplete</title>',
        '<desc id="description">This is public practice only, never a final benchmark or holdout. '
        'All 416 fresh public correctness cases matched CPython. Across 1,664 paired observations '
        'Rust geometric speedup is 0.8485646292880136 times and total-time speedup is '
        '0.5958109767071408 times. Rust was faster in 723 pairs and slower in 937. '
        'Dense same-letter no-match workloads are 0.41613883193210616 times as fast; six other '
        'public cohorts each have geometric speedup above one. Gprofng printed a banner before '
        'valid standard-library JSON, so profiling failed before Rust collection. Final speed, '
        'confidence, native memory, qualification, and a winner remain not measured.</desc>',
        '<rect width="1480" height="1135" rx="24" fill="#0b1220"/>',
        '<rect x="55" y="37" width="282" height="35" rx="10" fill="#78350f"/>',
        '<text x="72" y="61" fill="#fef3c7" font-size="16" font-family="system-ui,sans-serif" '
        'font-weight="730">PUBLIC PRACTICE ONLY</text>',
        '<text x="57" y="115" fill="#f8fafc" font-size="34" font-family="system-ui,sans-serif" '
        'font-weight="760">Rust matched public cases, but was slower overall</text>',
        '<text x="59" y="149" fill="#cbd5e1" font-size="18" font-family="system-ui,sans-serif">'
        'An exploratory run, not qualification, not the final benchmark, and not a holdout.</text>',
        '<rect x="57" y="177" width="426" height="118" rx="15" fill="#251821" stroke="#6b3145"/>',
        '<text x="79" y="209" fill="#fda4af" font-size="15" font-family="system-ui,sans-serif" '
        'font-weight="650">EQUAL-CASE OVERALL SPEED</text>',
        '<text x="78" y="253" fill="#fb7185" font-size="41" font-family="system-ui,sans-serif" '
        'font-weight="760">0.849×</text>',
        '<text x="241" y="251" fill="#f8fafc" font-size="18" font-family="system-ui,sans-serif">'
        'about 18% slower</text>',
        '<rect x="507" y="177" width="426" height="118" rx="15" fill="#172338" stroke="#324155"/>',
        '<text x="531" y="209" fill="#cbd5e1" font-size="15" font-family="system-ui,sans-serif" '
        'font-weight="650">ALL RECORDED TIME COMBINED</text>',
        '<text x="529" y="252" fill="#f8fafc" font-size="38" font-family="system-ui,sans-serif" '
        'font-weight="730">0.596×</text>',
        '<text x="682" y="249" fill="#e2e8f0" font-size="16" font-family="system-ui,sans-serif">'
        '1.68× more elapsed time</text>',
        '<rect x="958" y="177" width="464" height="118" rx="15" fill="#172338" stroke="#324155"/>',
        '<text x="981" y="209" fill="#cbd5e1" font-size="15" font-family="system-ui,sans-serif" '
        'font-weight="650">FASTER INDIVIDUAL PAIRS</text>',
        f'<text x="981" y="252" fill="#f8fafc" font-size="37" font-family="system-ui,sans-serif" '
        f'font-weight="730">{overall["rust_faster_pair_count"]:,} / {pairs:,}</text>',
        '<text x="984" y="279" fill="#fda4af" font-size="14" font-family="system-ui,sans-serif">'
        '937 slower  ·  4 tied</text>',
        '<text x="60" y="339" fill="#94a3b8" font-size="14" font-family="system-ui,sans-serif" '
        'font-weight="650">PUBLIC WORKLOAD COHORT</text>',
        '<text x="486" y="339" fill="#94a3b8" font-size="14" font-family="system-ui,sans-serif" '
        'font-weight="650">RUST SPEED VS PYTHON  ·  1.00× = SAME SPEED</text>',
        '<text x="1073" y="339" fill="#94a3b8" font-size="14" font-family="system-ui,sans-serif" '
        'font-weight="650">PUBLIC OBSERVATIONS</text>',
    ]
    for index, (key, label, color) in enumerate(rows):
        y = 369 + index * 63
        metric = metrics["by_cohort"][key]
        ratio = metric["equal_case_geometric_speedup"]
        width = min(plot_width, round(plot_width * ratio / maximum))
        parts.append(f'<rect x="57" y="{y}" width="1365" height="52" rx="10" fill="#101b2b"/>')
        parts.append(f'<text x="73" y="{y + 32}" fill="#f8fafc" font-size="15" '
                     f'font-family="system-ui,sans-serif">{escape(label)}</text>')
        parts.append(f'<rect x="{plot_x}" y="{y + 14}" width="{plot_width}" height="17" '
                     'rx="6" fill="#27364b"/>')
        parts.append(f'<rect x="{plot_x}" y="{y + 14}" width="{width}" height="17" '
                     f'rx="6" fill="{color}"/>')
        parts.append(f'<line x1="{parity}" y1="{y + 9}" x2="{parity}" y2="{y + 35}" '
                     'stroke="#e2e8f0" stroke-width="2"/>')
        parts.append(f'<text x="930" y="{y + 31}" fill="{color}" font-size="17" '
                     f'font-family="system-ui,sans-serif" font-weight="700">{ratio:.3f}×</text>')
        parts.append(f'<text x="1074" y="{y + 31}" fill="#e2e8f0" font-size="14" '
                     f'font-family="system-ui,sans-serif">{metric["paired_observation_count"]} pairs  ·  '
                     f'{metric["rust_slower_pair_count"]} slower</text>')
    parts.extend([
        '<text x="73" y="823" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">'
        'Exact public values: overall 0.8485646292880136×  ·  dense 0.41613883193210616×  ·  '
        'aggregate 0.5958109767071408×</text>',
        '<rect x="58" y="839" width="1364" height="118" rx="14" fill="#311a22" stroke="#874153"/>',
        '<text x="80" y="874" fill="#fda4af" font-size="19" font-family="system-ui,sans-serif" '
        'font-weight="720">Why profiling failed</text>',
        '<text x="81" y="906" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif">'
        'gprofng printed a banner before valid standard-library JSON. The controller expected pure JSON and stopped.</text>',
        '<text x="81" y="933" fill="#e2e8f0" font-size="15" font-family="system-ui,sans-serif">'
        'Only the standard-library heaptrace exists; the Rust native profile and published session summary do not.</text>',
        '<rect x="58" y="976" width="1364" height="105" rx="14" fill="#142238" stroke="#324155"/>',
        '<text x="80" y="1010" fill="#f8fafc" font-size="17" font-family="system-ui,sans-serif" '
        'font-weight="680">416 / 416 public cases matched  ·  26 operations  ·  4 paired rounds</text>',
        '<text x="81" y="1041" fill="#fcd34d" font-size="15" font-family="system-ui,sans-serif">'
        'FINAL SPEED: NOT MEASURED  ·  CONFIDENCE: NOT MEASURED  ·  NATIVE MEMORY: NOT MEASURED</text>',
        '<text x="81" y="1066" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">'
        'No candidate is qualified. Every slower pair and all 26 operation results are preserved in the failure report.</text>',
        '</svg>',
    ])
    return ("\n".join(parts) + "\n").encode("utf-8")


def assets(context: dict, result: dict, source_digest: str, source_bytes: int) -> dict[str, bytes]:
    metrics = result["metrics"]
    public_sources = {"driver": ref(DRIVER), "protocol": ref(PROTOCOL), "manifest": ref(MANIFEST)}
    public_run = {
        "stdlib_correctness": ref(STDLIB_CORRECTNESS), "rust_correctness": ref(RUST_CORRECTNESS),
        "paired_timing": ref(PAIRED), "stdlib_collector_stdout": ref(COLLECTOR_STDOUT),
        "stdlib_collector_stderr": ref(COLLECTOR_STDERR), "stdlib_heaptrace": ref(HEAPTRACE),
        "timing_rounds": {
            engine + "-" + format(number, "02d"): ref((item[0], item[1], item[2]))
            for (engine, number), item in sorted(ROUNDS.items())
        },
    }
    overall = metrics["overall"]
    headline = {
        "scope": "PUBLIC PRACTICE ONLY; NOT HOLDOUT; NOT QUALIFICATION; NOT FINAL BENCHMARK",
        "public_correctness_case_count": 416,
        "public_correctness_cases_matching_python": 416,
        "public_dataset_count": 16,
        "public_operation_count": 26,
        "public_paired_round_count": 4,
        "public_paired_observation_count": 1664,
        "public_equal_case_geometric_speedup": overall["equal_case_geometric_speedup"],
        "public_aggregate_total_elapsed_speedup": overall["aggregate_total_elapsed_speedup"],
        "public_rust_faster_pair_count": 723,
        "public_rust_slower_pair_count": 937,
        "public_tied_pair_count": 4,
        "dense_prefix_public_equal_case_geometric_speedup":
            metrics["by_cohort"]["mandatory_literal_dense_same_first_byte"]["equal_case_geometric_speedup"],
        "other_public_cohort_count_geometrically_faster_than_python": 6,
        "public_profiler_status": "FAIL; INCOMPLETE STDLIB-ONLY COLLECTION",
        "public_profiler_failure": "GPROFNG BANNER PRECEDES VALID JSON; RUST PROFILE NEVER STARTED",
        "final_holdout_speed": UNMEASURED,
        "final_confidence_intervals": UNMEASURED,
        "rust_native_cpu_profile": UNMEASURED,
        "rust_native_allocation_profile": UNMEASURED,
        "comparable_native_memory": UNMEASURED,
        "fully_qualified_candidate_count": 0,
        "winner_selected": False,
    }
    inputs = {
        "schema": "rebar-rust-public-practice-overall-v1-graph-inputs",
        "status": "PASS", "scope": "PUBLIC PRACTICE ONLY",
        "actual_run_status": "FAIL", "actual_public_profile_complete": False,
        "renderer": {"path": SELF, "sha256": source_digest, "bytes": source_bytes},
        "committed_public_sources": public_sources,
        "preserved_actual_public_run": public_run,
        "session": SESSION,
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "records_sha256": RECORDS_SHA256,
        "paired_rows_sha256": PAIRED_ROWS_SHA256,
        "headline": headline,
        "overall": overall,
        "by_cohort": metrics["by_cohort"],
        "by_operation": metrics["by_operation"],
        "by_domain": metrics["by_domain"],
        "complete_slower_pair_count": len(metrics["every_slower_paired_observation"]),
        "complete_slower_pair_records_sha256": metrics["every_slower_paired_observation_sha256"],
        "complete_slower_pair_records_path": FAILURE_OUTPUT,
        "source_mode_candidate_imports": 0,
        "source_mode_processes_started": 0,
        "source_mode_profiler_invocations": 0,
        "source_mode_clock_samples": 0,
        "source_mode_holdout_files_read": 0,
        "source_mode_native_candidate_files_opened": 0,
        "final_holdout_opened": False,
        "final_speed": UNMEASURED,
        "final_confidence": UNMEASURED,
        "final_native_memory": UNMEASURED,
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    svg = graph(metrics)
    encoded_inputs = canonical(inputs)
    failure = {
        "schema": "rebar-rust-public-profile-v1-run-001-complete-prepublication-failure",
        "status": "FAIL", "failure_scope": "PUBLIC PRACTICE ONLY; NOT QUALIFICATION OR FINAL BENCHMARK",
        "failure_class": "PREPUBLICATION GPROFNG STDOUT FRAMING ERROR",
        "failure_cause": "gprofng prepended a genuine experiment-creation banner before valid canonical stdlib worker JSON",
        "failure_location": "tools/rust_public_profile_v1.py:_profile_engine:decode_document(stdout)",
        "failure_happened_after_complete_correctness_and_timing": True,
        "failure_happened_before_rust_profiler_or_session_publication": True,
        "public_correctness_status": "PASS", "public_correctness_cases": 416,
        "public_correctness_records_sha256": RECORDS_SHA256,
        "public_correctness_worker_pids": {"stdlib": 81, "rust": 82},
        "public_timing_status": "PASS; PRACTICE ONLY", "public_timing_case_count": 416,
        "public_timing_round_count": 4, "public_timing_paired_observation_count": 1664,
        "public_timing_rows_sha256": PAIRED_ROWS_SHA256,
        "distinct_actual_public_process_ids": [81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91],
        "overall": overall,
        "cohort_results": metrics["by_cohort"],
        "operation_results": metrics["by_operation"],
        "domain_results": metrics["by_domain"],
        "complete_public_case_results": metrics["by_case"],
        "all_slower_paired_observations": metrics["every_slower_paired_observation"],
        "all_slower_paired_observation_count": 937,
        "all_slower_paired_observations_sha256": metrics["every_slower_paired_observation_sha256"],
        "stdlib_collector_banner": "Creating experiment directory stdlib.er (Process ID: 91) ...",
        "stdlib_collector_worker_json_was_valid_after_banner": True,
        "stdlib_profile_worker": result["profile"],
        "stdlib_native_heaptrace": ref(HEAPTRACE),
        "rust_native_profile_status": "NOT STARTED; NOT MEASURED",
        "comparable_native_memory": UNMEASURED,
        "native_cpu_reports": UNMEASURED,
        "native_allocation_reports": UNMEASURED,
        "native_heap_reports": UNMEASURED,
        "missing_expected_profile_outputs": list(MISSING_PROFILE_OUTPUTS),
        "session_summary_published": False,
        "committed_public_sources": public_sources,
        "preserved_actual_public_run": public_run,
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "final_holdout_opened": False,
        "final_speed": UNMEASURED,
        "final_confidence": UNMEASURED,
        "final_native_memory": UNMEASURED,
        "qualified_candidate_count": 0,
        "winner_selected": False,
        "graph": {
            "svg": {"path": SVG_OUTPUT, "bytes": len(svg), "sha256": sha256(svg)},
            "inputs": {"path": INPUTS_OUTPUT, "bytes": len(encoded_inputs), "sha256": sha256(encoded_inputs)},
        },
    }
    return {"svg": svg, "inputs": encoded_inputs, "failure": canonical(failure)}


def verify_generated(context: dict, result: dict, generated: dict[str, bytes],
                     source_digest: str, source_size: int) -> None:
    require(generated == assets(context, result, source_digest, source_size),
            "public-practice outputs were altered or are nondeterministic")
    inputs = parsed(generated["inputs"], "deterministic public-practice graph inputs")
    failure = parsed(generated["failure"], "deterministic public-practice failure report")
    same(inputs, {"status": "PASS", "scope": "PUBLIC PRACTICE ONLY",
                  "actual_run_status": "FAIL", "actual_public_profile_complete": False,
                  "qualified_candidate_count": 0, "winner_selected": False,
                  "final_speed": UNMEASURED, "final_confidence": UNMEASURED,
                  "final_native_memory": UNMEASURED},
         "honest public-practice graph boundaries")
    same(failure, {"status": "FAIL", "public_correctness_status": "PASS",
                    "public_correctness_cases": 416,
                    "public_timing_paired_observation_count": 1664,
                    "all_slower_paired_observation_count": 937,
                    "rust_native_profile_status": "NOT STARTED; NOT MEASURED",
                    "session_summary_published": False,
                    "final_speed": UNMEASURED, "final_confidence": UNMEASURED,
                    "final_native_memory": UNMEASURED,
                    "qualified_candidate_count": 0, "winner_selected": False},
         "complete actual failed public-practice profiler run")
    losses = failure.get("all_slower_paired_observations")
    require(type(losses) is list and len(losses) == 937
            and json_sha256(losses) == result["metrics"]["every_slower_paired_observation_sha256"],
            "an actual slower public-practice pair was omitted from the failure report")
    require(type(failure.get("complete_public_case_results")) is list
            and len(failure["complete_public_case_results"]) == 416,
            "a public-practice case disappeared from the complete failure report")
    require(type(failure.get("operation_results")) is dict
            and len(failure["operation_results"]) == 26,
            "a public-practice operation regression disappeared")
    require(b'role="img"' in generated["svg"]
            and b'aria-labelledby="title description"' in generated["svg"],
            "the public-practice graph lost its accessible title or description")
    for token in (b"PUBLIC PRACTICE ONLY", b"0.8485646292880136", b"0.5958109767071408",
                  b"0.41613883193210616", b"0.849", b"0.596", b"723 / 1,664",
                  b"937 slower", b"FINAL SPEED: NOT MEASURED", b"CONFIDENCE: NOT MEASURED",
                  b"NATIVE MEMORY: NOT MEASURED", b"profiling failed"):
        require(token in generated["svg"], "the public-practice graph omitted " + token.decode())


def controls(context: dict, result: dict, source_digest: str, source_size: int, wall: SourceWall) -> int:
    rejected = []

    def reject_context(label: str, mutation) -> None:
        hostile = copy.deepcopy(context)
        mutation(hostile)
        try:
            verify_context(hostile)
        except (Rejected, TypeError, KeyError, ValueError, IndexError):
            rejected.append(label)
            return
        raise Rejected("hostile public-practice evidence was accepted: " + label)

    for label, key, value in (
        ("manifest denominator inflated", "case_count", 417),
        ("manifest matrix substituted", "matrix_sha256", "0" * 64),
        ("manifest source substituted", "source_sha256", "0" * 64),
        ("manifest final holdout substituted", "approved_output_prefix", "oracle/phase3/holdout"),
    ):
        reject_context(label, lambda x, k=key, v=value: x["manifest"].__setitem__(k, v))
    reject_context("public matrix case omitted", lambda x: x["matrix"].pop())
    reject_context("public matrix domain reweighted", lambda x: x["matrix"][0].__setitem__("domain", "bytes"))
    reject_context("public correctness outcome changed", lambda x: x["rust_correctness"]["records"][0]["outcome"].__setitem__("status", "error"))
    reject_context("public correctness case omitted", lambda x: x["stdlib_correctness"]["records"].pop())
    reject_context("public correctness digest forged", lambda x: x["rust_correctness"].__setitem__("records_sha256", "0" * 64))
    reject_context("public correctness candidate process reused", lambda x: x["rust_correctness"].__setitem__("pid", 81))
    reject_context("public candidate delegated matching", lambda x: x["rust_correctness"]["engine_provenance"].__setitem__("candidate_owned_forbidden_import_attempts", ["re"]))
    reject_context("public correctness clocks sampled", lambda x: x["stdlib_correctness"].__setitem__("clock_samples", 1))
    reject_context("public round row omitted", lambda x: x["rounds"][("rust", 2)]["rows"].pop())
    reject_context("public round changed duration", lambda x: x["rounds"][("stdlib", 0)]["rows"][0].__setitem__("elapsed_ns", 1))
    reject_context("public round outcome changed", lambda x: x["rounds"][("rust", 3)]["rows"][7].__setitem__("expected_outcome_sha256", "0" * 64))
    reject_context("public timing pid duplicated", lambda x: x["rounds"][("rust", 1)].__setitem__("pid", 86))
    reject_context("public timing warmup invented", lambda x: x["rounds"][("stdlib", 2)].__setitem__("warmups", 2))
    reject_context("public paired row omitted", lambda x: x["paired"]["rows"].pop())
    reject_context("public paired denominator forged", lambda x: x["paired"].__setitem__("rows_sha256", "0" * 64))
    reject_context("public paired slowdown hidden", lambda x: x["paired"]["rows"][1].__setitem__("rust_elapsed_ns", 1))
    reject_context("public paired ordering changed", lambda x: x["paired"]["rows"][0]["pair_order"].reverse())
    reject_context("public paired rust pid reused", lambda x: x["paired"]["rows"][0].__setitem__("rust_pid", 83))
    reject_context("public paired correctness check omitted", lambda x: x["paired"]["rows"][0].__setitem__("correctness_checks_per_engine", 4))
    reject_context("public gprofng banner hidden", lambda x: x.__setitem__("collector_stdout", x["collector_stdout"].split(b"\n", 1)[1]))
    reject_context("public gprofng JSON corrupted", lambda x: x.__setitem__("collector_stdout", x["collector_stdout"].replace(b'"profile_passes":3', b'"profile_passes":2')))
    reject_context("public gprofng errors fabricated", lambda x: x.__setitem__("collector_stderr", b"fabricated error"))
    reject_context("public stdlib heaptrace replaced", lambda x: x["heaptrace"].__setitem__("sha256", "0" * 64))
    reject_context("missing rust profiler fabricated", lambda x: x["missing_profile_outputs"].__setitem__(SESSION + "/rust.er", False))
    reject_context("missing final summary fabricated", lambda x: x["missing_profile_outputs"].__setitem__(SESSION + "/summary.json", False))

    original = assets(context, result, source_digest, source_size)
    verify_generated(context, result, original, source_digest, source_size)

    def reject_output(label: str, kind: str, mutation) -> None:
        hostile = dict(original)
        document = parsed(hostile[kind], "hostile generated output")
        mutation(document)
        hostile[kind] = canonical(document)
        try:
            verify_generated(context, result, hostile, source_digest, source_size)
        except (Rejected, TypeError, KeyError, ValueError):
            rejected.append(label)
            return
        raise Rejected("hostile public-practice output was accepted: " + label)

    reject_output("published loss removed", "failure", lambda x: x["all_slower_paired_observations"].pop())
    reject_output("published denominator changed", "inputs", lambda x: x["headline"].__setitem__("public_paired_observation_count", 1663))
    reject_output("published profile falsely complete", "inputs", lambda x: x.__setitem__("actual_public_profile_complete", True))
    reject_output("published profile falsely succeeds", "failure", lambda x: x.__setitem__("status", "PASS"))
    reject_output("published rust profile invented", "failure", lambda x: x.__setitem__("rust_native_profile_status", "PASS"))
    reject_output("published final speed invented", "inputs", lambda x: x.__setitem__("final_speed", "1.5x"))
    reject_output("published confidence invented", "failure", lambda x: x.__setitem__("final_confidence", "95%"))
    reject_output("published native memory invented", "failure", lambda x: x.__setitem__("final_native_memory", 1))
    reject_output("published candidate falsely qualified", "inputs", lambda x: x.__setitem__("qualified_candidate_count", 1))
    reject_output("published winner selected", "failure", lambda x: x.__setitem__("winner_selected", True))
    reject_output("published operation loss omitted", "failure", lambda x: x["operation_results"].pop("module.split"))

    def reject_wall(label: str, event: str, arguments: tuple) -> None:
        try:
            wall.check(event, arguments)
        except Rejected:
            rejected.append(label)
            return
        raise Rejected("hostile source-only public-practice effect was accepted: " + label)

    reject_wall("candidate source read forbidden", "open", (os.path.join(ROOT, "candidates/rust_candidate.py"), None, os.O_RDONLY | os.O_NOFOLLOW))
    reject_wall("native candidate read forbidden", "open", (os.path.join(ROOT, "candidates/_rust_engine.so"), None, os.O_RDONLY | os.O_NOFOLLOW))
    reject_wall("holdout read forbidden", "open", (os.path.join(ROOT, "oracle/phase3/hidden.json"), None, os.O_RDONLY | os.O_NOFOLLOW))
    reject_wall("unapproved output write forbidden", "open", (os.path.join(ROOT, "README.md"), None, os.O_WRONLY | os.O_CREAT))
    reject_wall("approved output source write forbidden", "open", (os.path.join(ROOT, SVG_OUTPUT), None, os.O_WRONLY | os.O_CREAT))
    reject_wall("evidence symlink following forbidden", "open", (os.path.join(ROOT, STDLIB_CORRECTNESS[0]), None, os.O_RDONLY))
    reject_wall("candidate worker forbidden", "subprocess.Popen", (PYTHON,))
    reject_wall("profiler invocation forbidden", "subprocess.Popen", ("/usr/bin/gprofng",))
    reject_wall("native loading forbidden", "ctypes.dlopen", ("_rust_engine.so",))
    reject_wall("clock sampling forbidden", "time.perf_counter", ())
    reject_wall("network forbidden", "socket.connect", ("example.invalid",))
    reject_wall("candidate import forbidden", "import", ("candidates.rust_candidate",))
    reject_wall("matching import forbidden", "import", ("re",))
    reject_wall("unowned directory forbidden", "os.mkdir", (os.path.join(ROOT, "experiments/new-run"), 0o700, -1))
    return len(rejected)


def absent_profile_outputs() -> dict[str, bool]:
    result = {}
    for relative in MISSING_PROFILE_OUTPUTS:
        try:
            os.stat(os.path.join(ROOT, relative), follow_symlinks=False)
        except FileNotFoundError:
            result[relative] = True
        else:
            raise Rejected("incomplete public practice run unexpectedly contains " + relative)
    return result


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--verify-source", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    for name in ("source", "driver", "protocol", "manifest", "stdlib-correctness",
                 "rust-correctness", "paired", "collector", "heaptrace"):
        parser.add_argument("--" + name + "-sha256", required=True)
    return parser.parse_args()


def write_output(path: str, payload: bytes) -> None:
    descriptor = os.open(os.path.join(ROOT, path),
                         os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        position = 0
        while position < len(payload):
            written = os.write(descriptor, payload[position:])
            require(written > 0, "exclusive public-practice output write was interrupted")
            position += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def main() -> int:
    options = arguments()
    require(sys.executable == PYTHON and sys.version_info[:3] == (3, 14, 6)
            and sys.flags.isolated and sys.flags.dont_write_bytecode,
            "the exact isolated, bytecode-disabled stable CPython 3.14.6 is required")
    checks = (
        (options.driver_sha256, DRIVER[1], "committed V1 driver"),
        (options.protocol_sha256, PROTOCOL[1], "committed V1 protocol"),
        (options.manifest_sha256, MANIFEST[1], "committed V1 manifest"),
        (options.stdlib_correctness_sha256, STDLIB_CORRECTNESS[1], "actual stdlib vector"),
        (options.rust_correctness_sha256, RUST_CORRECTNESS[1], "actual Rust vector"),
        (options.paired_sha256, PAIRED[1], "actual 1,664 paired timing rows"),
        (options.collector_sha256, COLLECTOR_STDOUT[1], "actual gprofng-banner stdout"),
        (options.heaptrace_sha256, HEAPTRACE[1], "actual incomplete stdlib heaptrace"),
    )
    for actual, expected, label in checks:
        require(actual == expected, "frozen public-practice fingerprint changed: " + label)
    source_digest = options.source_sha256
    require(len(source_digest) == 64 and all(value in "0123456789abcdef" for value in source_digest),
            "renderer source fingerprint is not lowercase SHA-256")
    wall = SourceWall(options.render)
    sys.addaudithook(wall.check)
    source_bytes = os.stat(os.path.join(ROOT, SELF), follow_symlinks=False).st_size
    source = authenticated_owner((SELF, source_digest, source_bytes))
    require(source is not None, "renderer source fingerprint disappeared")
    committed_driver = authenticated_owner(DRIVER)
    require(committed_driver is not None and committed_driver.startswith(b"#!/usr/bin/env python3\n"),
            "committed public-practice V1 driver source was replaced")
    protocol = authenticated_owner(PROTOCOL)
    manifest = parsed(authenticated_owner(MANIFEST), "committed public-practice V1 manifest",
                      canonical_required=False)
    baseline = parsed(authenticated_owner(STDLIB_CORRECTNESS), "actual complete public stdlib vector")
    rust = parsed(authenticated_owner(RUST_CORRECTNESS), "actual complete public Rust vector")
    paired = parsed(authenticated_owner(PAIRED), "actual complete public paired observations")
    stdout = authenticated_owner(COLLECTOR_STDOUT)
    stderr = authenticated_owner(COLLECTOR_STDERR)
    authenticated_owner(HEAPTRACE, keep=False)
    round_documents = {
        identity: parsed(authenticated_owner((spec[0], spec[1], spec[2])),
                         "actual isolated " + identity[0] + " round " + str(identity[1]))
        for identity, spec in ROUNDS.items()
    }
    actual_matrix = matrix()
    context = {
        "protocol": protocol, "manifest": manifest,
        "matrix": actual_matrix, "matrix_by_case": {case["case"]: case for case in actual_matrix},
        "stdlib_correctness": baseline, "rust_correctness": rust,
        "paired": paired, "rounds": round_documents,
        "collector_stdout": stdout, "collector_stderr": stderr,
        "heaptrace": ref(HEAPTRACE),
        "missing_profile_outputs": absent_profile_outputs(),
    }
    result = verify_context(context)
    generated = assets(context, result, source_digest, len(source))
    verify_generated(context, result, generated, source_digest, len(source))
    hostile = controls(context, result, source_digest, len(source), wall) if options.self_test else 0
    created_directory = False
    if options.render:
        directory = os.path.join(ROOT, EVIDENCE_DIRECTORY)
        try:
            os.mkdir(directory, 0o700)
            created_directory = True
        except FileExistsError:
            details = os.stat(directory, follow_symlinks=False)
            require(stat.S_ISDIR(details.st_mode), "public failure-report parent is not a directory")
        write_output(SVG_OUTPUT, generated["svg"])
        write_output(INPUTS_OUTPUT, generated["inputs"])
        write_output(FAILURE_OUTPUT, generated["failure"])
    report = {
        "status": "PASS",
        "mode": "self-test" if options.self_test else "render" if options.render else "verify-source",
        "source_sha256": source_digest, "source_bytes": len(source),
        "hostile_control_count": hostile,
        "scope": "PUBLIC PRACTICE ONLY",
        "actual_profiler_run_status": "FAIL",
        "public_correctness_cases": 416,
        "public_correctness_cases_matching": 416,
        "public_operation_count": 26,
        "public_paired_observation_count": 1664,
        "public_equal_case_geometric_speedup": 0.8485646292880136,
        "public_aggregate_total_elapsed_speedup": 0.5958109767071408,
        "public_dense_geometric_speedup": 0.41613883193210616,
        "rust_faster_paired_observations": 723,
        "rust_slower_paired_observations": 937,
        "rust_profiler_started": False,
        "session_summary_published": False,
        "final_speed": UNMEASURED,
        "final_confidence": UNMEASURED,
        "final_native_memory": UNMEASURED,
        "qualified_candidate_count": 0,
        "source_mode_candidate_imports": 0,
        "source_mode_processes_started": 0,
        "source_mode_profiler_invocations": 0,
        "source_mode_clock_samples": 0,
        "source_mode_holdout_files_read": 0,
        "source_mode_native_candidate_files_opened": 0,
        "workspace_file_writes": 3 if options.render else 0,
        "required_parent_directories_created": 1 if created_directory else 0,
        "outputs": {
            "svg": {"path": SVG_OUTPUT, "bytes": len(generated["svg"]), "sha256": sha256(generated["svg"])},
            "inputs": {"path": INPUTS_OUTPUT, "bytes": len(generated["inputs"]), "sha256": sha256(generated["inputs"])},
            "failure": {"path": FAILURE_OUTPUT, "bytes": len(generated["failure"]), "sha256": sha256(generated["failure"])},
        },
    }
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, Rejected) as failure:
        print("FAIL: " + str(failure), file=sys.stderr)
        raise SystemExit(2)
