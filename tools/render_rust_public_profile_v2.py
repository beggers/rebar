#!/usr/bin/env python3
"""Render complete, honest public-practice V2 speed and memory evidence."""

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
SELF = "tools/render_rust_public_profile_v2.py"
SESSION = "experiments/rust_public_profile_v2/public-run-001"
OVERALL = "docs/evidence/rust-public-practice-overall-v2.svg"
MEMORY = "docs/evidence/rust-public-practice-memory-v2.svg"
INPUTS = "docs/evidence/rust-public-practice-overall-v2.inputs.json"
REPORT = "oracle/phase3/evidence/rust-public-profile-v2-complete-summary-v1.json"
SCHEMA = "rebar-rust-fresh-public-profile-v2"
LABEL = "FRESH PUBLIC PRACTICE ONLY; NOT A HOLDOUT OR FINAL BENCHMARK"
UNMEASURED = "NOT MEASURED"
SEED = 0x5255_5354_5052_4F31
MATRIX_SHA256 = "b13ff74122041ea792774fd5ee2d1f6d38033e94a1a6703c6e48522e461552a7"
RECORDS_SHA256 = "41f83dc761a93ea8e3203f46cedbba1e10918cf053194c20b37b8c209e992242"
ROWS_SHA256 = "6b9729005cd919f4de2e7137a35dd67ec18388a3f5362bcfb8142bab28545c11"
DRIVER = ("tools/rust_public_profile_v2.py", "a4eb77c29e06b1a77152ebb2275525bfd75b3fa26fd25f100059c79cfb39437a", 31941)
PROTOCOL = ("oracle/phase3/RUST-PUBLIC-PROFILE-V2.md", "aa96b3a2132be6557020a753da8e57e1c210b1a9b9216b6a015f36715e208b9d", 3128)
MANIFEST = ("oracle/phase3/rust-public-profile-v2.json", "9687806994bcbb401ed89cba11197b79a491da023b95be89e1686a7c6cccafea", 3926)
PREVIOUS = {
    "source": ("tools/rust_public_profile_v1.py", "ada1e9cfc8684ecb4fcf9294057347018b6058fc1619ae9de6a8b31097aa1562", 79693),
    "protocol": ("oracle/phase3/RUST-PUBLIC-PROFILE-V1.md", "6664f17ddd65c1953782f43b7fe1fa01427f1f510adfbad86fe8efdb135829ba", 5281),
    "manifest": ("oracle/phase3/rust-public-profile-v1.json", "b791b141eabbf6eb8a67484f5deb82bb41e324aedbdfe5b53a98ebc1553372c5", 1797),
}
SUMMARY = (SESSION + "/summary.json", "71468c3196d75994180de6ce27ab1a3c48e1253fd37f0e4d0f33ba7a6d4099cb", 28079)
TOP = {
    "stdlib.correctness.raw.json": (445036, "10db0e711cfbe8a97897a688e9b2f2bae5297db54febbf8565a2e454f2cab9ca"),
    "rust.correctness.raw.json": (445394, "88d1f5fcc6ea2e3e68a6345dff71858fb6ecfcaf8e88b366a559081c977cf52c"),
    "stdlib.timing-round-00.raw.json": (121117, "a5b0dfe1cbfa84c158d88b716886ac4f55c489f78b3faf936ab2008093373b86"),
    "rust.timing-round-00.raw.json": (121499, "07a16dd21ba65c174bab31a9a5f8289f10149cbb3f981528820f04ec26512070"),
    "rust.timing-round-01.raw.json": (121501, "d5f52056f67f47269f8c07d21b060e3c0e9178ac5c23e1a6e5c0037ea1645122"),
    "stdlib.timing-round-01.raw.json": (121116, "7017f13b91a7653be169e2ad24839a8977f9a538b08a4655335ab65f70983ef8"),
    "stdlib.timing-round-02.raw.json": (121118, "735832b0da2e427031cedd80a0a690d8d4ae306fc342f4094fd657bc0c675a89"),
    "rust.timing-round-02.raw.json": (121499, "06cce0f4fd288464d8c09d36755890b8a682db4c7a733fa55df99f8cfeebda66"),
    "rust.timing-round-03.raw.json": (121503, "ab1071b975bb254b0a058a8a07bc97374e118211ed8b722736fe4fc165f49e57"),
    "stdlib.timing-round-03.raw.json": (121121, "3ecc16177c3f8a603daef556cb0a9e3b797453bdea13cd9b6539bd135401b15f"),
    "paired-timing.raw.json": (504914, "cd237092007b231b37293414e417bce80afde3bc44a44e787adb53a0e66f7697"),
}
PROFILE = {
    "stdlib": {
        "collector.stdout.raw.txt": (2190, "505759c4b7aa18fc69ba3f4f1ccb1fa3ea09c4c1e00df34a218a8bcd09d1a895"),
        "collector.stderr.txt": (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        "collector.stdout.json": (2129, "8d5fb7c7519be19849da99607dbcb188550fb6126a5ca2da9905208b1a661f28"),
        "cpu.txt": (71158, "edd14c9958484fe9d1222d252181744e28609ffa42dd12dbd35c2340bf6b9a78"),
        "cpu.stderr.txt": (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        "ffi.txt": (517446, "82044c4fe4b8f5e70055f80a11b21d146a65bbf794835a091f8a1db84d3f8e86"),
        "ffi.stderr.txt": (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        "allocations.txt": (8835085, "9fd8f0b580a9679b3163f36046dcf1ec8c618e61ef350600e00f316bd39179ea"),
        "allocations.stderr.txt": (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        "heap.txt": (1429, "e27ed62af691ee1a14c91e80d5db4cfc4e54c8bf8fd8740fe1e517c7f8dec662"),
        "heap.stderr.txt": (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    },
    "rust": {
        "collector.stdout.raw.txt": (2578, "006e06462a56b1228093ca50eca1a24116c06a3ff94b291241e607f74dd68e82"),
        "collector.stderr.txt": (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        "collector.stdout.json": (2519, "ea390c1b0cd26d02858c7652c3e9f7dd57ebceaafebe5f8dc7e6121f06ea09a3"),
        "cpu.txt": (72934, "542b2fd936535ea5739db31f7cd6e97ff62642b20bbb448c09e33095e47a7d1d"),
        "cpu.stderr.txt": (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        "ffi.txt": (525686, "6957b8e19c2388173c719c757717e67aa8b116ba97243e226fed69619646d483"),
        "ffi.stderr.txt": (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        "allocations.txt": (8918549, "d698860b15c5785d53ae82501f738664d93b4447654847463a67cacb2bf63f76"),
        "allocations.stderr.txt": (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        "heap.txt": (1429, "ea98056637f2a3b9634549e57c28b2183167f4874441f31140913b0c93d68b9d"),
        "heap.stderr.txt": (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    },
}
LOGS = {
    "stdlib": (SESSION + "/stdlib.er/log.xml",
               "d99faf9c8dff6b6256a78f9928a33f5d8a93a606b61e37ee8ee61d1fda8b4225", 65536),
    "rust": (SESSION + "/rust.er/log.xml",
             "0a893318548fb3974ed0529a2379c5080c8f52142a8af81ae52645abbaf07dc2", 65536),
}
TIMER_FAILURE = b'<event kind="cerror" id="9">itimer could not be set</event>'
ROUND_PIDS = {("stdlib", 0): 83, ("rust", 0): 84, ("stdlib", 1): 86, ("rust", 1): 85,
              ("stdlib", 2): 87, ("rust", 2): 88, ("stdlib", 3): 90, ("rust", 3): 89}
OPERATIONS = (
    "module.compile", "module.search", "module.match", "module.fullmatch", "module.findall",
    "module.finditer", "module.split", "module.sub.literal", "module.sub.callback",
    "module.subn.literal", "pattern.search", "pattern.match", "pattern.fullmatch",
    "pattern.findall", "pattern.finditer", "pattern.split", "pattern.sub.literal",
    "pattern.sub.callback", "pattern.subn.literal", "pattern.scanner.search",
    "pattern.scanner.match", "pattern.scanner.loop", "scanner.scan", "match.group",
    "match.expand", "compile.fresh.search",
)
COHORTS = {
    "anchored_multiline_public": "Anchored multiline matching",
    "mandatory_literal_dense_same_first_byte": "Dense same-letter no-match",
    "overflow_assertion_guard_heap_spill": "Large lookahead capture guards",
    "overflow_capture_guard_heap_spill": "Large capture groups",
    "overflow_repeat_guard_heap_spill": "Deep bounded repetition",
    "scanner_and_callback_boundary": "Scanners and callbacks",
    "unicode_and_named_captures": "Unicode and named captures",
}
MARKERS = ("rebar_compile", "rebar_match", "rebar_collect", "_rust_bridge", "_rust_engine",
           "bridge_compile", "rust_pattern", "rust_scanner")
MEMORY_EXPECTED = {
    "stdlib": {"native_total_allocated_bytes": 100547111,
               "native_allocation_count": 284705, "native_peak_heap_bytes": 53002716,
               "native_leaked_bytes": 17097737, "native_leak_count": 2423,
               "native_distinct_allocation_count": 6776,
               "whole_process_peak_rss_kib": 38172, "python_tracemalloc_peak_bytes": 192184,
               "profile_pid": 91},
    "rust": {"native_total_allocated_bytes": 104211416,
             "native_allocation_count": 260204, "native_peak_heap_bytes": 53002684,
             "native_leaked_bytes": 16771634, "native_leak_count": 2941,
             "native_distinct_allocation_count": 6818,
             "whole_process_peak_rss_kib": 71660, "python_tracemalloc_peak_bytes": 114389,
             "profile_pid": 96},
}


class Rejected(ValueError):
    """Reject modified evidence, omitted losses, or false CPU/memory claims."""


def require(value: bool, message: str) -> None:
    if not value:
        raise Rejected(message)


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                       sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def value_digest(value: object) -> str:
    return digest(canonical(value))


def unique_object(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in items:
        require(type(key) is str and key not in result, "duplicate JSON evidence field")
        result[key] = value
    return result


def parsed(payload: bytes, label: str, *, canonical_required: bool = True) -> dict:
    try:
        value = json.loads(payload, object_pairs_hook=unique_object,
                           parse_constant=lambda _: (_ for _ in ()).throw(Rejected("nonfinite JSON")))
    except (UnicodeError, TypeError, ValueError) as failure:
        raise Rejected("invalid authenticated public evidence: " + label) from failure
    require(type(value) is dict and (not canonical_required or canonical(value) == payload),
            "noncanonical authenticated public evidence: " + label)
    return value


def owner_paths() -> set[str]:
    values = {SELF, DRIVER[0], PROTOCOL[0], MANIFEST[0], SUMMARY[0]}
    values.update(spec[0] for spec in PREVIOUS.values())
    values.update(spec[0] for spec in LOGS.values())
    values.update(SESSION + "/" + name for name in TOP)
    values.update(SESSION + "/" + engine + "." + suffix
                  for engine, files in PROFILE.items() for suffix in files)
    return values


class SourceWall:
    def __init__(self, render: bool) -> None:
        self.render = render
        self.owners = frozenset(os.path.join(ROOT, value) for value in owner_paths())
        self.outputs = frozenset(os.path.join(ROOT, value)
                                 for value in (OVERALL, MEMORY, INPUTS, REPORT))

    def check(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 and type(arguments[2]) is int else 0
            require(type(path) is str, "source-only wall rejected an unapproved descriptor")
            writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if writing:
                required = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                require(self.render and path in self.outputs and flags & required == required,
                        "source-only wall rejected a write outside the four owned public outputs")
            else:
                require(path in self.owners and bool(flags & os.O_NOFOLLOW),
                        "source-only wall rejected candidate, native executable, holdout, or archive")
            return
        if (event.startswith(("subprocess.", "socket.", "ctypes.", "os.exec", "os.spawn"))
                or event in {"os.system", "os.fork", "os.posix_spawn", "os.mkdir", "os.remove",
                             "os.rename", "os.rmdir", "os.chdir", "os.chmod", "os.link",
                             "os.symlink", "os.truncate", "os.putenv", "time.time",
                             "time.monotonic", "time.perf_counter", "_thread.start_new_thread"}):
            raise Rejected("source-only wall rejected process, profiler, network, clock, or mutation")
        if event == "import" and arguments:
            name = arguments[0]
            require(not (type(name) is str and (name in {"re", "_sre", "subprocess", "ctypes"}
                                                or name.startswith(("candidates.", "rebar.")))),
                    "source-only wall rejected candidate or matching imports")


def owner(spec: tuple[str, str, int]) -> bytes:
    path, expected, size = spec
    require(path in owner_paths(), "public evidence owner escaped its exact allowlist")
    descriptor = os.open(os.path.join(ROOT, path), os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        metadata = os.fstat(descriptor)
        require(stat.S_ISREG(metadata.st_mode) and stat.S_IMODE(metadata.st_mode) == 0o600
                and metadata.st_nlink == 1 and metadata.st_uid == os.getuid()
                and metadata.st_size == size,
                "public evidence owner identity or size changed: " + path)
        blocks = []
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            blocks.append(block)
        payload = b"".join(blocks)
        require(digest(payload) == expected, "public evidence owner SHA-256 changed: " + path)
        return payload
    finally:
        os.close(descriptor)


def same(actual: object, expected: dict, label: str) -> None:
    require(type(actual) is dict, "expected public evidence object: " + label)
    for key, value in expected.items():
        require(actual.get(key) == value, label + ": altered " + key)


def encoded(value: object) -> dict:
    if type(value) is str:
        return {"kind": "str", "value": value}
    if type(value) is bytes:
        return {"kind": "bytes", "hex": value.hex()}
    if type(value) is bytearray:
        return {"kind": "bytearray", "hex": bytes(value).hex()}
    if type(value) is memoryview:
        return {"kind": "memoryview", "hex": value.tobytes().hex(), "readonly": value.readonly,
                "format": value.format, "shape": list(value.shape)}
    raise Rejected("original fresh public case carrier changed")


def build_matrix() -> list[dict]:
    captures = "(?:" + "(a)" * 40 + "){2}Z"
    assertions = "(?=(?:" + "(a)" * 36 + ")Z)a{36}Z"
    datasets = (
        ("text.dense-first-byte.literal.no-match", "text", "AAAAAAB", "A" * 2048 + "C", 0, "mandatory_literal_dense_same_first_byte"),
        ("text.dense-first-byte.alternation.no-match", "text", "(?:AAAAAAB|AAAAAAC)", "A" * 2048 + "D", 0, "mandatory_literal_dense_same_first_byte"),
        ("text.capture.guard.spill", "text", captures, "a" * 80 + "Z", 0, "overflow_capture_guard_heap_spill"),
        ("text.repeat.guard.spill", "text", r"(?:(?:ab){16}){4}Z", "ab" * 64 + "Z", 0, "overflow_repeat_guard_heap_spill"),
        ("text.assertion.guard.spill", "text", assertions, "a" * 36 + "Z", 0, "overflow_assertion_guard_heap_spill"),
        ("text.unicode.named.words", "text", r"(?P<token>[^\W\d_]+)(?P<digits>\d*)", "Éclair42 Ζeta7 naïve3 cedar8", 0, "unicode_and_named_captures"),
        ("text.scanner.remainder", "text", r"(?P<token>[A-Za-z]+)(?P<digits>\d*)", "oak12 pine7 !fresh-tail9", 0, "scanner_and_callback_boundary"),
        ("text.multiline.anchors", "text", r"^(?P<token>[a-z]+)(?P<digits>\d*)$", "maple7\nCEDAR8\nspruce9", 10, "anchored_multiline_public"),
        ("bytes.dense-first-byte.literal.no-match", "bytes", b"AAAAAAB", b"A" * 2048 + b"C", 0, "mandatory_literal_dense_same_first_byte"),
        ("bytes.dense-first-byte.alternation.no-match", "bytes", rb"(?:AAAAAAB|AAAAAAC)", memoryview(b"A" * 2048 + b"D"), 0, "mandatory_literal_dense_same_first_byte"),
        ("bytes.capture.guard.spill", "bytes", captures.encode(), bytearray(b"a" * 80 + b"Z"), 0, "overflow_capture_guard_heap_spill"),
        ("bytes.repeat.guard.spill", "bytes", rb"(?:(?:ab){16}){4}Z", b"ab" * 64 + b"Z", 0, "overflow_repeat_guard_heap_spill"),
        ("bytes.assertion.guard.spill", "bytes", assertions.encode(), b"a" * 36 + b"Z", 0, "overflow_assertion_guard_heap_spill"),
        ("bytes.high-bit.named.words", "bytes", rb"(?P<token>[A-Za-z]+)(?P<digits>\d*)", b"\xe9oak42 cedar7 \xfffir3", 0, "unicode_and_named_captures"),
        ("bytes.scanner.mutable-memoryview.remainder", "bytes", rb"(?P<token>[A-Za-z]+)(?P<digits>\d*)", memoryview(bytearray(b"oak12 pine7 !fresh-tail9")), 0, "scanner_and_callback_boundary"),
        ("bytes.multiline.anchors", "bytes", rb"^(?P<token>[a-z]+)(?P<digits>\d*)$", b"maple7\nCEDAR8\nspruce9", 10, "anchored_multiline_public"),
    )
    result = []
    for dataset_index, (dataset, domain, pattern, subject, flags, cohort) in enumerate(datasets):
        phrase = r"[A-Za-z]+\d*" if domain == "text" else rb"[A-Za-z]+\d*"
        replacement = r"<\g<0>>" if domain == "text" else rb"<\g<0>>"
        for operation_index, operation in enumerate(OPERATIONS):
            lifecycle = ("fresh-native-compile" if operation == "compile.fresh.search"
                         else "native-scanner-boundary" if operation == "scanner.scan"
                         else "module-call" if operation.startswith("module.")
                         else "live-match" if operation.startswith("match.")
                         else "live-pattern-scanner" if ".scanner." in operation
                         else "precompiled-pattern")
            result.append({"case": "rust-public-profile.v1." + format(len(result), "04d"),
                           "dataset": dataset, "domain": domain, "cohort": cohort,
                           "operation": operation, "lifecycle": lifecycle,
                           "pattern": encoded(pattern), "subject": encoded(subject),
                           "replacement": encoded(replacement), "scanner_phrase": encoded(phrase),
                           "flags": flags,
                           "limit": 1 + (SEED + dataset_index * 37 + operation_index * 11) % 3,
                           "weight_numerator": 1})
    require(len(result) == 416 and value_digest(result) == MATRIX_SHA256,
            "the complete balanced fresh-public case matrix was altered")
    return result


def reference(spec: tuple[str, str, int]) -> dict:
    return {"path": spec[0], "sha256": spec[1], "bytes": spec[2]}


def verify_manifest(manifest: dict, protocol: bytes) -> None:
    same(manifest, {"schema": SCHEMA + "-source-freeze", "source": DRIVER[0],
                    "source_sha256": DRIVER[1], "protocol": PROTOCOL[0],
                    "protocol_sha256": PROTOCOL[1], "published_seed": SEED,
                    "matrix_sha256": MATRIX_SHA256, "case_count": 416,
                    "dataset_count": 16, "operation_count": 26,
                    "approved_output_prefix": "experiments/rust_public_profile_v2",
                    "pinned_cpython": "3.14.6", "pinned_python": PYTHON},
         "committed V2 public-practice source manifest")
    same(manifest.get("profile_configuration"),
         {"batch_iterations": 3, "paired_rounds": 4, "profile_passes": 3,
          "warmup_iterations": 1, "reports": ["allocations", "cpu", "ffi", "heap"]},
         "committed V2 public-practice profiler configuration")
    same(manifest.get("provenance"), {
        "archive_files_read": 0, "candidate_imports_in_source_modes": 0,
        "data": "fresh embedded public literals only", "fixture_files_read": 0,
        "holdout_files_read": 0, "preserved_public_failed_runs_mutated": 0,
        "source_mode_clock_samples": 0, "source_mode_workspace_mutations": 0,
    }, "committed V2 source-only provenance")
    previous = manifest.get("previous")
    for key, spec in PREVIOUS.items():
        same(previous, {key: spec[0], key + "_sha256": spec[1]},
             "committed V2 preserved V1 " + key)
    same(manifest.get("preserved_failure"), {
        "collector_stdout_sha256": "057d2eb19a2c24e11688fa0419047e50f6720cbafd41b7ec3bd7ee763691aff0",
        "paired_timing_sha256": "3da06bdb04ace9897d359aaa962ca412f3e9260a5c1a337703e0aa35567b6b85",
        "paired_rows": 1664, "expected_records_sha256": RECORDS_SHA256,
    }, "committed immutable V1 prepublication failure")
    same(manifest.get("collector_output_policy"), {
        "ascii_banner_count": 1, "canonical_json_document_count": 1,
        "preserve_complete_raw_stdout": True,
        "preserve_separate_canonical_worker_json": True,
        "banner_positive_decimal_pid_matches_worker_pid": True,
        "banner_engine_matches_expected_engine": True,
        "banner_experiment_matches_expected_engine": True,
        "forbid_extra_output_control_bytes_and_trailing_data": True,
    }, "complete V2 gprofng announcement normalization")
    for token in (b"fresh public practice only", b"416", b"1,664", b"NOT FROZEN",
                  b"NOT GENERATED", b"NOT OPENED", b"NOT MEASURED"):
        require(token.lower() in protocol.lower(), "committed V2 public protocol omitted " + token.decode())


def verify_summary(summary: dict) -> None:
    same(summary, {"schema": SCHEMA + "-published-public-profile", "status": "PASS",
                   "label": LABEL, "python": "3.14.6", "source_sha256": DRIVER[1],
                   "manifest_sha256": MANIFEST[1], "published_seed": SEED,
                   "matrix_sha256": MATRIX_SHA256, "dataset_count": 16,
                   "case_count": 416, "operation_count": 26, "paired_rounds": 4,
                   "batch_iterations": 3, "warmup_iterations": 1,
                   "profile_passes": 3, "raw_paired_rows_sha256": ROWS_SHA256,
                   "approved_output_directory": SESSION, "fixture_files_read": 0,
                   "holdout_files_read": 0, "archive_files_read": 0,
                   "profiler_binary_archiving": "DISABLED", "final_winner_selected": False},
         "complete authentic public-only V2 profiling summary")
    same(summary.get("correctness_gate"), {
        "status": "PASS", "baseline_pid": 81, "rust_pid": 82,
        "compared_cases": 416, "completed_before_any_timing_or_profiler": True,
        "records_sha256": RECORDS_SHA256,
        "candidate_owned_reference_import_attempts": [],
    }, "actual complete V2 416-case isolated public correctness gate")
    artifacts = summary.get("artifacts")
    require(type(artifacts) is list and len(artifacts) == 11,
            "an actual top-level public correctness/timing artifact disappeared")
    observed = {}
    for artifact in artifacts:
        require(type(artifact) is dict and set(artifact) == {"path", "bytes", "sha256"},
                "an actual public timing artifact identity was changed")
        path = artifact["path"]
        require(path.startswith(SESSION + "/"), "public artifact escaped its approved session")
        name = path[len(SESSION) + 1:]
        require(name in TOP and TOP[name] == (artifact["bytes"], artifact["sha256"]),
                "an actual public correctness/timing artifact was substituted")
        require(name not in observed, "a top-level actual public artifact was duplicated")
        observed[name] = artifact
    require(set(observed) == set(TOP), "a top-level public timing artifact was omitted")
    profiles = summary.get("native_profiles")
    require(type(profiles) is dict and set(profiles) == {"stdlib", "rust"},
            "the actual complete native-profiler engine comparison was changed")
    for engine, profile in profiles.items():
        same(profile, {
            "engine": engine, "collector_pid": MEMORY_EXPECTED[engine]["profile_pid"],
            "target_pid": MEMORY_EXPECTED[engine]["profile_pid"],
            "experiment": SESSION + "/" + engine + ".er",
            "archive_collection": "DISABLED (-a off)",
            "descendant_collection": "DISABLED (-F off)",
            "native_heap_tracing": "ENABLED (-H on)",
            "cpu_sampling": "ENABLED (-p hi)", "correctness_checks": 1248,
        }, "actual complete public " + engine + " profiler")
        same(profile.get("python_heap"), {
            "maximum_rss_kib": MEMORY_EXPECTED[engine]["whole_process_peak_rss_kib"],
            "tracemalloc_peak_bytes": MEMORY_EXPECTED[engine]["python_tracemalloc_peak_bytes"],
        }, "actual public " + engine + " process RSS and Python-only allocation peak")
        expected = PROFILE[engine]
        documents = profile.get("artifacts")
        require(type(documents) is list and len(documents) == 11,
                "an actual public " + engine + " profiling artifact disappeared")
        seen = set()
        for document in documents:
            path = document.get("path") if type(document) is dict else None
            prefix = SESSION + "/" + engine + "."
            require(type(path) is str and path.startswith(prefix),
                    "a public native-profiler artifact escaped its exact namespace")
            suffix = path[len(prefix):]
            require(suffix in expected and expected[suffix] == (document.get("bytes"), document.get("sha256"))
                    and suffix not in seen,
                    "an actual public native-profiler artifact was changed")
            seen.add(suffix)
        require(seen == set(expected), "an actual public profiler report or stderr was omitted")


def verify_worker(worker: dict, *, engine: str, role: str, schema: str, pid: int) -> None:
    same(worker, {"schema": SCHEMA + "-isolated-" + schema, "status": "PASS", "label": LABEL,
                  "engine": engine, "role": role, "pid": pid,
                  "python": "3.14.6", "published_seed": SEED,
                  "matrix_sha256": MATRIX_SHA256, "case_count": 416,
                  "fixture_files_read": 0, "holdout_files_read": 0,
                  "archive_files_read": 0, "files_written": 0},
         "actual isolated " + engine + " public " + schema + " worker")
    require(worker.get("candidate_import_count") == (0 if engine == "stdlib" else 3),
            "actual isolated public worker candidate identity changed")
    provenance = worker.get("engine_provenance")
    if engine == "stdlib":
        same(provenance, {"stdlib_origin":
             "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/__init__.py"},
             "actual isolated official CPython reference")
    else:
        same(provenance, {
            "adapter_origin": "/home/dev-user/src/rebar/candidates/rust_candidate.py",
            "bridge_origin": "/home/dev-user/src/rebar/candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
            "candidate_owned_forbidden_import_attempts": [],
            "native_bridge_exports": ["compile", "compile_scanner", "run", "collect",
                                      "pattern_match", "pattern_type", "pattern_descriptors", "bind"],
        }, "actual isolated first-party public Rust worker")


def verify_correctness(context: dict) -> dict[str, dict]:
    baseline = context["top"]["stdlib.correctness.raw.json"]
    rust = context["top"]["rust.correctness.raw.json"]
    for engine, document, pid in (("stdlib", baseline, 81), ("rust", rust, 82)):
        verify_worker(document, engine=engine,
                      role="public-profile-correctness-" + engine,
                      schema="observations", pid=pid)
        same(document, {"records_sha256": RECORDS_SHA256,
                        "clock_samples": 0, "timing_trials_run": 0},
             "actual untimed full public correctness vector")
        records = document.get("records")
        require(type(records) is list and len(records) == 416
                and value_digest(records) == RECORDS_SHA256,
                "an actual public correctness observation was removed")
        for case, actual in zip(context["matrix"], records, strict=True):
            require(type(actual) is dict and set(actual) == {"case", "outcome"}
                    and actual["case"] == case["case"] and type(actual["outcome"]) is dict,
                    "an original public correctness case was changed or reordered")
    require(baseline["records"] == rust["records"] and baseline["pid"] != rust["pid"],
            "all 416 first-party public Rust outcomes no longer match CPython")
    return {record["case"]: record["outcome"] for record in baseline["records"]}


def ordered_cases(number: int, actual_matrix: list[dict]) -> list[str]:
    cases = [case["case"] for case in actual_matrix]
    offset = (SEED + number * 37) % len(cases)
    values = cases[offset:] + cases[:offset]
    return values[::-1] if number % 2 else values


def verify_rounds(context: dict, outcomes: dict[str, dict]) -> None:
    for (engine, number), pid in ROUND_PIDS.items():
        name = engine + ".timing-round-" + format(number, "02d") + ".raw.json"
        document = context["top"][name]
        verify_worker(document, engine=engine,
                      role="public-timing-" + format(number, "02d") + "-" + engine,
                      schema="timing", pid=pid)
        same(document, {"expected_records_sha256": RECORDS_SHA256, "round": number,
                        "iterations": 3, "warmups": 1, "clock_samples": 832},
             "actual complete isolated public timing worker")
        rows = document.get("rows")
        require(type(rows) is list and len(rows) == 416
                and value_digest(rows) == document.get("rows_sha256"),
                "an actual isolated V2 public timing row disappeared")
        expected = ordered_cases(number, context["matrix"])
        for position, row in enumerate(rows):
            case = context["matrix_by_case"][expected[position]]
            same(row, {"case": expected[position], "cohort": case["cohort"],
                       "operation": case["operation"], "position": position,
                       "round": number, "iterations": 3, "correctness_checks": 5,
                       "expected_outcome_sha256": value_digest(outcomes[expected[position]])},
                 "actual correctness-gated isolated public timing row")
            require(type(row.get("elapsed_ns")) is int and row["elapsed_ns"] > 0,
                    "an actual isolated public elapsed-time sample was hidden")


def verify_pairs(context: dict) -> list[dict]:
    paired = context["top"]["paired-timing.raw.json"]
    same(paired, {"schema": SCHEMA + "-paired-timing-rows", "matrix_sha256": MATRIX_SHA256,
                  "rows_sha256": ROWS_SHA256}, "actual 1,664-row public paired timing")
    rows = paired.get("rows")
    require(type(rows) is list and len(rows) == 1664 and value_digest(rows) == ROWS_SHA256,
            "an actual equal-weight public paired timing row or regression was removed")
    for index, row in enumerate(rows):
        number, position = divmod(index, 416)
        baseline = context["top"]["stdlib.timing-round-" + format(number, "02d") + ".raw.json"]
        rust = context["top"]["rust.timing-round-" + format(number, "02d") + ".raw.json"]
        left = baseline["rows"][position]
        right = rust["rows"][position]
        same(row, {"case": left["case"], "round": number, "position": position,
                   "cohort": left["cohort"], "operation": left["operation"],
                   "pair_order": ["stdlib", "rust"] if number % 2 == 0 else ["rust", "stdlib"],
                   "baseline_pid": baseline["pid"], "rust_pid": rust["pid"],
                   "iterations": 3, "correctness_checks_per_engine": 5,
                   "baseline_elapsed_ns": left["elapsed_ns"],
                   "rust_elapsed_ns": right["elapsed_ns"]},
             "actual balanced complete public paired observation")
        require(right["case"] == left["case"] and baseline["pid"] != rust["pid"],
                "an actual public pair lost its independently isolated reference worker")
    return rows


def integer_line(text: str, prefix: str) -> int:
    values = [line.strip()[len(prefix):].strip() for line in text.splitlines()
              if line.strip().startswith(prefix)]
    require(len(values) == 1 and values[0].isdigit(), "native heap report changed: " + prefix)
    return int(values[0])


def heap_values(text: str, engine: str) -> dict:
    lines = text.splitlines()
    totals = [line.strip()[len("Total bytes"):].strip() for line in lines
              if line.strip().startswith("Total bytes")]
    require(len(totals) == 2 and all(value.isdigit() for value in totals),
            "native heap allocation/leak byte totals were conflated")
    values = {
        "native_peak_heap_bytes": integer_line(text, "Heap size bytes"),
        "native_allocation_count": integer_line(text, "Total allocations"),
        "native_total_allocated_bytes": int(totals[0]),
        "native_leak_count": integer_line(text, "Total leaked"),
        "native_leaked_bytes": int(totals[1]),
        "profile_pid": integer_line(text, "Process Id"),
    }
    same(values, {key: MEMORY_EXPECTED[engine][key] for key in values},
         "actual public " + engine + " native allocation/heap report")
    return values


def scan_reports(raw: dict[str, bytes], engine: str) -> dict:
    marker_lines = []
    metric_lines = []
    for kind in ("cpu", "ffi", "allocations", "heap"):
        text = raw[kind + ".txt"].decode("utf-8")
        if kind in ("cpu", "ffi"):
            require(text.startswith("Functions sorted by metric: Inclusive Bytes Leaked\n"),
                    "mislabeled public .cpu/.ffi report was falsely treated as CPU samples")
            require("CPU Time" not in text.splitlines()[:8],
                    "the genuine public leaked-byte report was replaced with a CPU claim")
        if kind == "allocations":
            expected = MEMORY_EXPECTED[engine]
            first = text.splitlines()[0]
            require(first == "Summary Results: Distinct Allocations = "
                    + str(expected["native_distinct_allocation_count"])
                    + ", Total Instances = " + str(expected["native_allocation_count"])
                    + ", Total Bytes Allocated = " + str(expected["native_total_allocated_bytes"]),
                    "native allocation totals or counts were fabricated")
        for line in text.splitlines():
            if len(marker_lines) < 80 and any(marker in line for marker in MARKERS):
                marker_lines.append(line.strip()[:300])
            if len(metric_lines) < 80 and any(metric in line.lower() for metric in
                                               ("cpu", "allocated", "allocation", "heap", "leaked", "bytes")):
                metric_lines.append(line.strip()[:300])
    return {"native_ffi_marker_count": len(marker_lines), "native_ffi_marker_lines": marker_lines,
            "cpu_heap_allocation_metric_lines": metric_lines}


def verify_profile(context: dict, engine: str) -> dict:
    profile = context["summary"]["native_profiles"][engine]
    files = context["profile"][engine]
    pid = MEMORY_EXPECTED[engine]["profile_pid"]
    log = context["logs"][engine]
    require(log.count(TIMER_FAILURE) == 1 and log.count(b'<profile name="') == 1
            and log.count(b'<profile name="heaptrace">') == 1
            and (b'<process pid="' + str(pid).encode("ascii") + b'">') in log,
            "the actual gprofng CPU sampling timer failure or heap-only profile was hidden")
    raw_stdout = files["collector.stdout.raw.txt"]
    normalized = files["collector.stdout.json"]
    banner = f"Creating experiment directory {engine}.er (Process ID: {pid}) ...".encode()
    require(raw_stdout == banner + b"\n" + normalized,
            "the actual profiler announcement/canonical JSON framing changed")
    worker = parsed(normalized, "actual normalized " + engine + " gprofng worker")
    verify_worker(worker, engine=engine, role="public-profile-" + engine,
                  schema="profile", pid=pid)
    same(worker, {"expected_records_sha256": RECORDS_SHA256, "profile_passes": 3,
                  "public_case_executions": 1248}, "actual profiled public " + engine + " worker")
    require(worker.get("python_heap") == profile.get("python_heap"),
            "actual whole-process RSS/Python-traced memory no longer matches the profiler summary")
    expected_cohorts = {key: 312 if key == "mandatory_literal_dense_same_first_byte" else 156
                        for key in COHORTS}
    require(worker.get("executions_by_cohort") == expected_cohorts
            and profile.get("cohort_execution_counts") == expected_cohorts,
            "actual balanced profiled public workload was changed")
    same(profile.get("authenticated_collector_banner"), {
        "engine": engine, "experiment": engine + ".er", "target_pid": pid,
        "normalized_stdout_bytes": len(normalized),
        "normalized_stdout_sha256": digest(normalized),
        "banner_sha256": digest(banner + b"\n"),
    }, "authenticated actual gprofng collector announcement")
    for suffix in ("collector.stderr.txt", "cpu.stderr.txt", "ffi.stderr.txt",
                   "allocations.stderr.txt", "heap.stderr.txt"):
        require(files[suffix] == b"", "an actual public profiler diagnostic was hidden")
    values = heap_values(files["heap.txt"].decode("utf-8"), engine)
    summary_signals = scan_reports(files, engine)
    require(profile.get("native_ffi") == summary_signals,
            "actual complete public first-party FFI marker evidence changed")
    require(summary_signals["native_ffi_marker_count"] == (80 if engine == "rust" else 0),
            "actual public Rust first-party FFI/native owner markers were hidden")
    values.update({
        "native_distinct_allocation_count": MEMORY_EXPECTED[engine]["native_distinct_allocation_count"],
        "whole_process_peak_rss_kib": worker["python_heap"]["maximum_rss_kib"],
        "python_tracemalloc_peak_bytes": worker["python_heap"]["tracemalloc_peak_bytes"],
        "python_tracemalloc_after_bytes": worker["python_heap"]["tracemalloc_after_bytes"],
        "python_allocated_blocks_delta": worker["python_heap"]["allocated_blocks_delta"],
        "whole_process_user_cpu_seconds": worker["python_heap"]["user_cpu_seconds"],
        "whole_process_system_cpu_seconds": worker["python_heap"]["system_cpu_seconds"],
        "profile_elapsed_ns": worker["elapsed_ns"],
        "first_party_native_ffi_marker_count": summary_signals["native_ffi_marker_count"],
        "per_function_cpu_profile": UNMEASURED,
        "clock_cpu_sampling_operational": False,
        "profiler_timer_status": "FAILED; itimer could not be set",
        "profiler_recorded_profile_types": ["heaptrace"],
        "cpu_filename_actual_sort_metric": "INCLUSIVE BYTES LEAKED; NOT CPU TIME",
    })
    return values


def aggregate(rows: list[dict]) -> dict:
    baseline = rust = faster = slower = ties = 0
    logs = 0.0
    for row in rows:
        original, candidate = row["baseline_elapsed_ns"], row["rust_elapsed_ns"]
        baseline += original
        rust += candidate
        logs += math.log(original / candidate)
        faster += original > candidate
        slower += original < candidate
        ties += original == candidate
    return {"pairs": len(rows), "baseline_total_ns": baseline, "rust_total_ns": rust,
            "aggregate_total_elapsed_speedup": baseline / rust,
            "equal_pair_geometric_speedup": math.exp(logs / len(rows)),
            "rust_faster_pair_count": faster, "rust_slower_pair_count": slower,
            "tied_pair_count": ties}


def calculate(context: dict, rows: list[dict]) -> dict:
    by_cohort = {key: [] for key in COHORTS}
    by_operation = {key: [] for key in OPERATIONS}
    by_domain = {"text": [], "bytes": []}
    by_case = {case["case"]: [] for case in context["matrix"]}
    for row in rows:
        case = context["matrix_by_case"][row["case"]]
        by_cohort[row["cohort"]].append(row)
        by_operation[row["operation"]].append(row)
        by_domain[case["domain"]].append(row)
        by_case[row["case"]].append(row)
    result = aggregate(rows)
    same(result, {"pairs": 1664, "baseline_total_ns": 97941980,
                  "rust_total_ns": 164386504,
                  "aggregate_total_elapsed_speedup": 0.595803047189324,
                  "equal_pair_geometric_speedup": 0.8608014813128971,
                  "rust_faster_pair_count": 807,
                  "rust_slower_pair_count": 857, "tied_pair_count": 0},
         "complete actual equal-weight public-practice speed observations")
    published = context["summary"]["paired_results"]
    same(published.get("overall"), {
        "pairs": 1664, "baseline_total_ns": result["baseline_total_ns"],
        "rust_total_ns": result["rust_total_ns"],
        "baseline_over_rust_ratio": result["aggregate_total_elapsed_speedup"],
    }, "actual complete public aggregate speed summary")
    cohorts, operations, domains = {}, {}, {}
    for key, values in sorted(by_cohort.items()):
        require(len(values) == (416 if key == "mandatory_literal_dense_same_first_byte" else 208),
                "an actual equal-weight public cohort was changed")
        current = aggregate(values)
        same(published["by_cohort"].get(key), {
            "pairs": current["pairs"], "baseline_total_ns": current["baseline_total_ns"],
            "rust_total_ns": current["rust_total_ns"],
            "baseline_over_rust_ratio": current["aggregate_total_elapsed_speedup"],
        }, "actual public cohort summary")
        if key == "mandatory_literal_dense_same_first_byte":
            require(current["aggregate_total_elapsed_speedup"] == 0.21409330078969788,
                    "actual dense-prefix public regression was hidden")
        else:
            require(current["aggregate_total_elapsed_speedup"] > 1,
                    "an actual favorable public cohort was falsely reported slow")
        cohorts[key] = current
    require(set(published.get("by_cohort", {})) == set(COHORTS),
            "a complete public cohort was removed")
    for key, values in sorted(by_operation.items()):
        require(len(values) == 64, "an actual public operation lost an equal-weight observation")
        current = aggregate(values)
        same(published["by_operation"].get(key), {
            "pairs": 64, "baseline_total_ns": current["baseline_total_ns"],
            "rust_total_ns": current["rust_total_ns"],
            "baseline_over_rust_ratio": current["aggregate_total_elapsed_speedup"],
        }, "actual public operation regression")
        operations[key] = current
    require(set(published.get("by_operation", {})) == set(OPERATIONS),
            "an actual public operation or regression was hidden")
    for key, values in by_domain.items():
        require(len(values) == 832, "equal public text/bytes weights were changed")
        domains[key] = aggregate(values)
    cases = []
    for case in context["matrix"]:
        values = by_case[case["case"]]
        require(len(values) == 4 and {row["round"] for row in values} == set(range(4)),
                "an actual public case lost an independently ordered paired round")
        cases.append({"case": case["case"], "dataset": case["dataset"], "domain": case["domain"],
                      "cohort": case["cohort"], "operation": case["operation"],
                      "results": aggregate(values)})
    case_log = sum(math.log(case["results"]["aggregate_total_elapsed_speedup"])
                   for case in cases)
    computed_case_geometric = math.exp(case_log / len(cases))
    require(math.isclose(computed_case_geometric, 0.8649792983684755,
                         rel_tol=0.0, abs_tol=1e-15),
            "the actual equally weighted 416-case geometric speed changed")
    result["equal_case_geometric_speedup"] = 0.8649792983684755
    result["rust_faster_case_count"] = sum(
        case["results"]["aggregate_total_elapsed_speedup"] > 1 for case in cases)
    result["rust_slower_case_count"] = sum(
        case["results"]["aggregate_total_elapsed_speedup"] < 1 for case in cases)
    result["tied_case_count"] = sum(
        case["results"]["aggregate_total_elapsed_speedup"] == 1 for case in cases)
    same(result, {"rust_faster_case_count": 222, "rust_slower_case_count": 194,
                  "tied_case_count": 0}, "complete distinct-case Rust wins and losses")
    large_regressions = [case for case in cases
                         if case["results"]["aggregate_total_elapsed_speedup"] < 1 / 1.2]
    dense_cases = [case for case in cases
                   if case["cohort"] == "mandatory_literal_dense_same_first_byte"]
    dense_regressions = [case for case in large_regressions
                         if case["cohort"] == "mandatory_literal_dense_same_first_byte"]
    dense_geometric = math.exp(sum(math.log(case["results"]["aggregate_total_elapsed_speedup"])
                                   for case in dense_cases) / len(dense_cases))
    require(len(dense_cases) == 104 and len(large_regressions) == 73
            and len(dense_regressions) == 69
            and math.isclose(dense_geometric, 0.4216836278497641,
                             rel_tol=0.0, abs_tol=1e-15),
            "the complete dense same-first-byte case-regression distribution was hidden")
    other_rows = [row for row in rows
                  if row["cohort"] != "mandatory_literal_dense_same_first_byte"]
    other_aggregate = aggregate(other_rows)
    require(math.isclose(other_aggregate["aggregate_total_elapsed_speedup"],
                         1.2681207102924326, rel_tol=0.0, abs_tol=1e-15),
            "the six combined non-dense public cohorts changed")
    losses = []
    for row in rows:
        if row["baseline_elapsed_ns"] < row["rust_elapsed_ns"]:
            losses.append({"case": row["case"], "round": row["round"],
                           "position": row["position"], "cohort": row["cohort"],
                           "operation": row["operation"],
                           "domain": context["matrix_by_case"][row["case"]]["domain"],
                           "pair_order": row["pair_order"],
                           "baseline_pid": row["baseline_pid"], "rust_pid": row["rust_pid"],
                           "baseline_elapsed_ns": row["baseline_elapsed_ns"],
                           "rust_elapsed_ns": row["rust_elapsed_ns"],
                           "baseline_over_rust_speedup":
                               row["baseline_elapsed_ns"] / row["rust_elapsed_ns"]})
    require(len(losses) == 857, "an actual public slower pair/regression was hidden")
    return {"overall": result, "by_cohort": cohorts, "by_operation": operations,
            "by_domain": domains, "complete_case_results": cases,
            "dense_equal_case_geometric_speedup": dense_geometric,
            "dense_case_count": len(dense_cases),
            "non_dense_combined": other_aggregate,
            "cases_more_than_twenty_percent_slower": large_regressions,
            "cases_more_than_twenty_percent_slower_sha256": value_digest(large_regressions),
            "dense_cases_more_than_twenty_percent_slower": len(dense_regressions),
            "all_slower_pairs": losses, "all_slower_pairs_sha256": value_digest(losses)}


def verify(context: dict) -> dict:
    verify_manifest(context["manifest"], context["protocol"])
    verify_summary(context["summary"])
    actual_matrix = context["matrix"]
    require(value_digest(actual_matrix) == MATRIX_SHA256 and len(actual_matrix) == 416,
            "actual fresh-public case matrix was weakened")
    require(sum(row["domain"] == "text" for row in actual_matrix)
            == sum(row["domain"] == "bytes" for row in actual_matrix) == 208,
            "actual fresh public text/bytes cases are not balanced")
    for operation in OPERATIONS:
        require(sum(row["operation"] == operation for row in actual_matrix) == 16,
                "an actual fresh-public operation or case was omitted")
    outcomes = verify_correctness(context)
    verify_rounds(context, outcomes)
    rows = verify_pairs(context)
    memory = {engine: verify_profile(context, engine) for engine in ("stdlib", "rust")}
    return {"metrics": calculate(context, rows), "memory": memory}


def escaped(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def overall_svg(result: dict) -> bytes:
    metrics = result["metrics"]
    order = (
        "mandatory_literal_dense_same_first_byte", "anchored_multiline_public",
        "overflow_assertion_guard_heap_spill", "overflow_capture_guard_heap_spill",
        "overflow_repeat_guard_heap_spill", "scanner_and_callback_boundary",
        "unicode_and_named_captures",
    )
    plot_x, plot_width, maximum = 477, 455, 1.5
    baseline_x = plot_x + round(plot_width / maximum)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1480" height="1100" '
        'viewBox="0 0 1480 1100" role="img" aria-labelledby="title description">',
        '<title id="title">Public practice only: Rust is slower overall despite six faster cohorts</title>',
        '<desc id="description">Public practice only, not final benchmarking. All 416 public Rust '
        'correctness cases match Python. Across 1,664 paired public timings, aggregate Python-over-Rust '
        'speed is 0.595803047189324 times, equal-case geometric speed is 0.8649792983684755 times, '
        'and equal-pair geometric speed is 0.8608014813128971 times. Rust wins 222 of 416 cases and '
        '807 of 1,664 individual pairs. Dense same-letter no-match workloads are '
        '0.21409330078969788 times as fast in aggregate and 0.42168362785 times as fast by equal case; '
        'the other six cohorts combined are 1.26812071029 times as fast. Of 73 cases over twenty '
        'percent slower, 69 are dense. Native CPU per-function profiling and confidence intervals '
        'are not measured: both profiler timers failed and the supposed CPU report is leaked bytes. '
        'The final holdout remains unopened, no candidate qualifies, and no winner is selected.</desc>',
        '<rect width="1480" height="1100" rx="24" fill="#0b1220"/>',
        '<rect x="56" y="39" width="271" height="36" rx="10" fill="#713f12"/>',
        '<text x="72" y="64" fill="#fef3c7" font-size="16" font-family="system-ui,sans-serif" '
        'font-weight="730">PUBLIC PRACTICE ONLY</text>',
        '<text x="57" y="116" fill="#f8fafc" font-size="35" font-family="system-ui,sans-serif" '
        'font-weight="760">Rust is slower overall on this complete public run</text>',
        '<text x="60" y="150" fill="#cbd5e1" font-size="18" font-family="system-ui,sans-serif">'
        'All 416 exploratory cases match Python; this is not qualification or a final benchmark.</text>',
        '<rect x="57" y="177" width="423" height="119" rx="15" fill="#291820" stroke="#794254"/>',
        '<text x="80" y="209" fill="#fda4af" font-size="15" font-family="system-ui,sans-serif" '
        'font-weight="650">TOTAL ELAPSED-TIME SPEED</text>',
        '<text x="79" y="255" fill="#fb7185" font-size="42" font-family="system-ui,sans-serif" '
        'font-weight="770">0.596×</text>',
        '<text x="239" y="251" fill="#f8fafc" font-size="17" font-family="system-ui,sans-serif">'
        '1.68× more total time</text>',
        '<rect x="501" y="177" width="432" height="119" rx="15" fill="#142238" stroke="#324155"/>',
        '<text x="524" y="209" fill="#cbd5e1" font-size="15" font-family="system-ui,sans-serif" '
        'font-weight="650">EQUAL-CASE GEOMETRIC SPEED</text>',
        '<text x="524" y="254" fill="#f8fafc" font-size="39" font-family="system-ui,sans-serif" '
        'font-weight="740">0.865×</text>',
        '<text x="676" y="251" fill="#e2e8f0" font-size="16" font-family="system-ui,sans-serif">'
        '222 / 416 cases faster</text>',
        '<rect x="955" y="177" width="466" height="119" rx="15" fill="#142238" stroke="#324155"/>',
        '<text x="978" y="209" fill="#cbd5e1" font-size="15" font-family="system-ui,sans-serif" '
        'font-weight="650">FASTER INDIVIDUAL PAIRS</text>',
        '<text x="977" y="254" fill="#f8fafc" font-size="38" font-family="system-ui,sans-serif" '
        'font-weight="750">807 / 1,664</text>',
        '<text x="980" y="279" fill="#fda4af" font-size="14" font-family="system-ui,sans-serif">'
        '857 slower  ·  none hidden</text>',
        '<text x="66" y="340" fill="#94a3b8" font-size="14" font-family="system-ui,sans-serif" '
        'font-weight="650">PUBLIC WORKLOAD COHORT</text>',
        '<text x="477" y="340" fill="#94a3b8" font-size="14" font-family="system-ui,sans-serif" '
        'font-weight="650">TOTAL-TIME SPEED  ·  1.00× = SAME SPEED</text>',
        '<text x="1071" y="340" fill="#94a3b8" font-size="14" font-family="system-ui,sans-serif" '
        'font-weight="650">OBSERVATIONS</text>',
    ]
    for index, key in enumerate(order):
        top = 370 + index * 64
        values = metrics["by_cohort"][key]
        ratio = values["aggregate_total_elapsed_speedup"]
        color = "#fb7185" if ratio < 1 else "#34d399"
        width = min(plot_width, round(plot_width * ratio / maximum))
        parts.append(f'<rect x="58" y="{top}" width="1363" height="53" rx="10" fill="#101b2b"/>')
        parts.append(f'<text x="76" y="{top + 32}" fill="#f8fafc" font-size="15" '
                     f'font-family="system-ui,sans-serif">{escaped(COHORTS[key])}</text>')
        parts.append(f'<rect x="{plot_x}" y="{top + 14}" width="{plot_width}" height="18" '
                     'rx="6" fill="#27364b"/>')
        parts.append(f'<rect x="{plot_x}" y="{top + 14}" width="{width}" height="18" '
                     f'rx="6" fill="{color}"/>')
        parts.append(f'<line x1="{baseline_x}" y1="{top + 8}" x2="{baseline_x}" '
                     f'y2="{top + 37}" stroke="#f8fafc" stroke-width="2"/>')
        parts.append(f'<text x="951" y="{top + 32}" fill="{color}" font-size="17" '
                     f'font-family="system-ui,sans-serif" font-weight="710">{ratio:.3f}×</text>')
        parts.append(f'<text x="1073" y="{top + 32}" fill="#e2e8f0" font-size="14" '
                     f'font-family="system-ui,sans-serif">{values["pairs"]} pairs · '
                     f'{values["rust_slower_pair_count"]} slower</text>')
    parts.extend([
        '<text x="72" y="822" fill="#cbd5e1" font-size="12" font-family="system-ui,sans-serif">'
        'Exact public values: aggregate 0.595803047189324×  ·  dense 0.21409330078969788×  ·  '
        'equal-case geometric 0.8649792983684755×  ·  equal-pair geometric 0.8608014813128971×</text>',
        '<text x="72" y="845" fill="#fda4af" font-size="13" font-family="system-ui,sans-serif">'
        '73 cases &gt;20% slower (69 dense)  ·  dense equal-case 0.42168362785×  ·  '
        'six non-dense cohorts combined 1.26812071029×</text>',
        '<rect x="59" y="860" width="1361" height="102" rx="14" fill="#2a1c26" stroke="#794254"/>',
        '<text x="80" y="889" fill="#fda4af" font-size="18" font-family="system-ui,sans-serif" '
        'font-weight="720">Per-function CPU: NOT MEASURED</text>',
        '<text x="81" y="916" fill="#f8fafc" font-size="14" font-family="system-ui,sans-serif">'
        'Both profiler logs: itimer could not be set. Files named .cpu.txt are sorted by Inclusive Bytes Leaked.</text>',
        '<text x="81" y="943" fill="#e2e8f0" font-size="14" font-family="system-ui,sans-serif">'
        '80 independently owned Rust FFI markers confirm native participation, not per-function CPU time.</text>',
        '<rect x="59" y="973" width="1361" height="90" rx="14" fill="#142238" stroke="#324155"/>',
        '<text x="81" y="1008" fill="#fcd34d" font-size="15" font-family="system-ui,sans-serif">'
        'FINAL SPEED: NOT MEASURED  ·  CONFIDENCE: NOT MEASURED  ·  FINAL HOLDOUT: NOT OPENED</text>',
        '<text x="81" y="1038" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">'
        'Public practice only. All 26 operations and all 857 slower pairs are retained. '
        'No candidate qualifies; no winner.</text>',
        '</svg>',
    ])
    return ("\n".join(parts) + "\n").encode("utf-8")


def memory_svg(result: dict) -> bytes:
    stdlib, rust = result["memory"]["stdlib"], result["memory"]["rust"]
    rows = (
        ("Total native bytes allocated", stdlib["native_total_allocated_bytes"], rust["native_total_allocated_bytes"], "bytes", "Cumulative allocations over the whole public run"),
        ("Native allocation events", stdlib["native_allocation_count"], rust["native_allocation_count"], "events", "Number of native allocation calls"),
        ("Peak native heap", stdlib["native_peak_heap_bytes"], rust["native_peak_heap_bytes"], "bytes", "Profiler-observed live native heap peak"),
        ("Peak whole-process RSS", stdlib["whole_process_peak_rss_kib"], rust["whole_process_peak_rss_kib"], "KiB", "Entire Python process, native engine, and profiler overhead"),
        ("Peak Python-traced allocations", stdlib["python_tracemalloc_peak_bytes"], rust["python_tracemalloc_peak_bytes"], "bytes", "Python tracemalloc only; native allocations are excluded"),
        ("Native leaked bytes reported", stdlib["native_leaked_bytes"], rust["native_leaked_bytes"], "bytes", "Profiler leak accounting; not total RSS or live heap"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1480" height="1140" '
        'viewBox="0 0 1480 1140" role="img" aria-labelledby="title description">',
        '<title id="title">Public practice memory: native heap, process RSS, and Python allocations are different</title>',
        '<desc id="description">Public practice only. Rust allocated 104,211,416 native bytes '
        'over 260,204 allocation calls; Python allocated 100,547,111 bytes over 284,705 calls. '
        'Native heap peaks were 53,002,684 Rust and 53,002,716 Python bytes. Whole-process peak RSS '
        'was 71,660 Rust and 38,172 Python kibibytes. Python-only tracemalloc peaks were 114,389 '
        'Rust and 192,184 Python bytes. These measure different scopes and must never be conflated. '
        'The files called CPU reports are sorted by leaked bytes; per-function CPU is not measured. '
        'Both profiler logs explicitly report that the sampling timer could not be set. '
        'Confidence, final memory, final speed, and the sealed holdout remain unmeasured or unopened.</desc>',
        '<rect width="1480" height="1140" rx="24" fill="#0b1220"/>',
        '<rect x="55" y="36" width="271" height="36" rx="10" fill="#713f12"/>',
        '<text x="72" y="61" fill="#fef3c7" font-size="16" font-family="system-ui,sans-serif" '
        'font-weight="730">PUBLIC PRACTICE ONLY</text>',
        '<text x="57" y="113" fill="#f8fafc" font-size="35" font-family="system-ui,sans-serif" '
        'font-weight="760">Three memory scopes tell different stories</text>',
        '<text x="59" y="147" fill="#cbd5e1" font-size="18" font-family="system-ui,sans-serif">'
        'Native heap, whole-process RSS, and Python-only tracing are separate measurements.</text>',
        '<rect x="60" y="169" width="1349" height="72" rx="13" fill="#172338" stroke="#324155"/>',
        '<rect x="85" y="192" width="15" height="15" rx="4" fill="#94a3b8"/>',
        '<text x="111" y="205" fill="#e2e8f0" font-size="15" font-family="system-ui,sans-serif">Python stdlib</text>',
        '<rect x="253" y="192" width="15" height="15" rx="4" fill="#60a5fa"/>',
        '<text x="280" y="205" fill="#e2e8f0" font-size="15" font-family="system-ui,sans-serif">Rust first-party engine</text>',
        '<text x="532" y="205" fill="#fcd34d" font-size="14" font-family="system-ui,sans-serif">'
        'Compare bars only within the same row; units and scopes differ.</text>',
    ]
    for index, (label, baseline, candidate, unit, explanation) in enumerate(rows):
        top = 265 + index * 105
        maximum = max(baseline, candidate)
        base_width = round(374 * baseline / maximum)
        rust_width = round(374 * candidate / maximum)
        delta = (candidate / baseline - 1) * 100
        delta_label = (f"{delta:+.1f}%" if abs(delta) >= .05 else "approximately equal")
        delta_color = "#fb7185" if delta > .05 else "#34d399" if delta < -.05 else "#cbd5e1"
        parts.append(f'<rect x="58" y="{top}" width="1350" height="94" rx="11" fill="#101b2b"/>')
        parts.append(f'<text x="77" y="{top + 26}" fill="#f8fafc" font-size="16" '
                     f'font-family="system-ui,sans-serif" font-weight="660">{escaped(label)}</text>')
        parts.append(f'<text x="77" y="{top + 50}" fill="#cbd5e1" font-size="12" '
                     f'font-family="system-ui,sans-serif">{escaped(explanation)}</text>')
        parts.append(f'<rect x="561" y="{top + 17}" width="{base_width}" height="14" rx="5" fill="#94a3b8"/>')
        parts.append(f'<rect x="561" y="{top + 43}" width="{rust_width}" height="14" rx="5" fill="#60a5fa"/>')
        parts.append(f'<text x="956" y="{top + 30}" fill="#e2e8f0" font-size="14" '
                     f'font-family="system-ui,sans-serif">{baseline:,} {unit}</text>')
        parts.append(f'<text x="956" y="{top + 56}" fill="#93c5fd" font-size="14" '
                     f'font-family="system-ui,sans-serif">{candidate:,} {unit}</text>')
        parts.append(f'<text x="1377" y="{top + 47}" text-anchor="end" fill="{delta_color}" '
                     f'font-size="14" font-family="system-ui,sans-serif" font-weight="680">'
                     f'{escaped(delta_label)}</text>')
    parts.extend([
        '<rect x="59" y="909" width="1350" height="104" rx="14" fill="#291820" stroke="#794254"/>',
        '<text x="81" y="944" fill="#fda4af" font-size="18" font-family="system-ui,sans-serif" '
        'font-weight="730">Per-function CPU is NOT MEASURED</text>',
        '<text x="82" y="973" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif">'
        'Both logs: itimer could not be set. The .cpu.txt files are sorted by Inclusive Bytes Leaked.</text>',
        '<text x="82" y="997" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">'
        '80 genuine first-party Rust FFI markers show native participation; they do not provide CPU timings.</text>',
        '<text x="64" y="1052" fill="#fcd34d" font-size="15" font-family="system-ui,sans-serif">'
        'FINAL MEMORY: NOT MEASURED  ·  CONFIDENCE: NOT MEASURED  ·  FINAL HOLDOUT: NOT OPENED</text>',
        '<text x="65" y="1082" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">'
        'Measured practice RSS includes the complete process; tracemalloc excludes native allocations; '
        'native bytes are cumulative.</text>',
        '</svg>',
    ])
    return ("\n".join(parts) + "\n").encode("utf-8")


def public_assets(context: dict, result: dict, source_digest: str, source_size: int) -> dict[str, bytes]:
    performance = result["metrics"]
    memory = result["memory"]
    overall_graph = overall_svg(result)
    memory_graph = memory_svg(result)
    raw_owners = {name: {"path": SESSION + "/" + name, "bytes": item[0], "sha256": item[1]}
                  for name, item in sorted(TOP.items())}
    profile_owners = {
        engine: {suffix: {"path": SESSION + "/" + engine + "." + suffix,
                          "bytes": item[0], "sha256": item[1]}
                 for suffix, item in sorted(artifacts.items())}
        for engine, artifacts in PROFILE.items()
    }
    profiler_log_owners = {engine: reference(spec) for engine, spec in LOGS.items()}
    headline = {
        "scope": "PUBLIC PRACTICE ONLY; NOT QUALIFICATION; NOT FINAL; NOT HOLDOUT",
        "public_correctness_cases": 416,
        "public_correctness_cases_matching_python": 416,
        "public_operation_count": 26,
        "public_dataset_count": 16,
        "public_paired_round_count": 4,
        "public_paired_observation_count": 1664,
        "public_aggregate_total_elapsed_speedup": 0.595803047189324,
        "public_equal_case_geometric_speedup": 0.8649792983684755,
        "public_equal_pair_geometric_speedup": 0.8608014813128971,
        "public_dense_aggregate_speedup": 0.21409330078969788,
        "public_dense_equal_case_geometric_speedup": performance["dense_equal_case_geometric_speedup"],
        "public_dense_case_count": 104,
        "public_non_dense_combined_aggregate_speedup": 1.2681207102924326,
        "public_rust_faster_case_count": 222,
        "public_rust_slower_case_count": 194,
        "public_case_count_more_than_twenty_percent_slower": 73,
        "public_dense_case_count_more_than_twenty_percent_slower": 69,
        "public_rust_faster_pair_count": 807,
        "public_rust_slower_pair_count": 857,
        "other_public_cohort_count_faster_by_total_elapsed": 6,
        "rust_native_total_allocated_bytes": 104211416,
        "python_native_total_allocated_bytes": 100547111,
        "rust_native_allocation_count": 260204,
        "python_native_allocation_count": 284705,
        "rust_native_peak_heap_bytes": 53002684,
        "python_native_peak_heap_bytes": 53002716,
        "rust_whole_process_peak_rss_kib": 71660,
        "python_whole_process_peak_rss_kib": 38172,
        "rust_python_only_tracemalloc_peak_bytes": 114389,
        "python_python_only_tracemalloc_peak_bytes": 192184,
        "first_party_rust_native_ffi_marker_count": 80,
        "per_function_cpu_profile": UNMEASURED,
        "clock_cpu_sampling_operational": False,
        "profiler_timer_status": "FAILED; itimer could not be set",
        "cpu_artifact_actual_sort_metric": "INCLUSIVE BYTES LEAKED; NOT CPU TIME",
        "confidence_interval": UNMEASURED,
        "final_holdout_speed": UNMEASURED,
        "final_holdout_memory": UNMEASURED,
        "final_holdout_status": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    inputs = {
        "schema": "rebar-rust-public-practice-overall-v2-graph-inputs",
        "status": "PASS", "scope": "PUBLIC PRACTICE ONLY",
        "renderer": {"path": SELF, "sha256": source_digest, "bytes": source_size},
        "committed_sources": {"driver": reference(DRIVER), "protocol": reference(PROTOCOL),
                              "manifest": reference(MANIFEST),
                              "preserved_v1": {name: reference(spec)
                                               for name, spec in PREVIOUS.items()}},
        "actual_complete_summary": reference(SUMMARY),
        "all_authenticated_public_timing_artifacts": raw_owners,
        "all_authenticated_public_profile_artifacts": profile_owners,
        "all_authenticated_public_profiler_logs": profiler_log_owners,
        "published_seed": SEED, "matrix_sha256": MATRIX_SHA256,
        "records_sha256": RECORDS_SHA256, "paired_rows_sha256": ROWS_SHA256,
        "headline": headline, "overall": performance["overall"],
        "by_cohort": performance["by_cohort"],
        "by_operation": performance["by_operation"],
        "by_domain": performance["by_domain"],
        "dense_equal_case_geometric_speedup": performance["dense_equal_case_geometric_speedup"],
        "dense_case_count": performance["dense_case_count"],
        "non_dense_combined": performance["non_dense_combined"],
        "case_count_more_than_twenty_percent_slower": 73,
        "dense_case_count_more_than_twenty_percent_slower": 69,
        "case_records_more_than_twenty_percent_slower_sha256":
            performance["cases_more_than_twenty_percent_slower_sha256"],
        "memory_measurements": memory,
        "complete_slower_pair_count": len(performance["all_slower_pairs"]),
        "complete_slower_pair_records_sha256": performance["all_slower_pairs_sha256"],
        "complete_slower_pair_records_path": REPORT,
        "per_function_cpu_profile": UNMEASURED,
        "clock_cpu_sampling_operational": False,
        "profiler_timer_status": "FAILED; itimer could not be set",
        "confidence_intervals": UNMEASURED,
        "final_speed": UNMEASURED,
        "final_native_memory": UNMEASURED,
        "final_holdout_opened": False,
        "qualified_candidate_count": 0, "winner_selected": False,
        "source_mode_candidate_imports": 0,
        "source_mode_processes_started": 0,
        "source_mode_profiler_invocations": 0,
        "source_mode_clock_samples": 0,
        "source_mode_holdout_files_read": 0,
        "source_mode_native_candidate_files_opened": 0,
    }
    inputs_bytes = canonical(inputs)
    publication = {
        "schema": "rebar-rust-public-profile-v2-complete-evidence-publication-v1",
        "status": "PASS", "status_scope": "COMPLETE PUBLIC PRACTICE ONLY; NEVER QUALIFICATION OR FINAL HOLDOUT",
        "actual_public_session_summary": reference(SUMMARY),
        "renderer": {"path": SELF, "sha256": source_digest, "bytes": source_size},
        "committed_sources": inputs["committed_sources"],
        "public_correctness_status": "PASS", "public_correctness_case_count": 416,
        "public_correctness_records_sha256": RECORDS_SHA256,
        "public_correctness_worker_pids": {"stdlib": 81, "rust": 82},
        "public_timing_status": "COMPLETE; PUBLIC PRACTICE ONLY",
        "public_timing_paired_observation_count": 1664,
        "public_timing_rows_sha256": ROWS_SHA256,
        "all_authenticated_public_timing_artifacts": raw_owners,
        "all_authenticated_public_native_profile_artifacts": profile_owners,
        "all_authenticated_public_profiler_logs": profiler_log_owners,
        "overall": performance["overall"],
        "cohort_results": performance["by_cohort"],
        "operation_results": performance["by_operation"],
        "domain_results": performance["by_domain"],
        "complete_case_results": performance["complete_case_results"],
        "dense_equal_case_geometric_speedup": performance["dense_equal_case_geometric_speedup"],
        "dense_case_count": performance["dense_case_count"],
        "non_dense_combined": performance["non_dense_combined"],
        "case_records_more_than_twenty_percent_slower":
            performance["cases_more_than_twenty_percent_slower"],
        "case_count_more_than_twenty_percent_slower": 73,
        "dense_case_count_more_than_twenty_percent_slower": 69,
        "case_records_more_than_twenty_percent_slower_sha256":
            performance["cases_more_than_twenty_percent_slower_sha256"],
        "all_slower_paired_observations": performance["all_slower_pairs"],
        "all_slower_paired_observation_count": 857,
        "all_slower_paired_observations_sha256": performance["all_slower_pairs_sha256"],
        "memory_measurements": memory,
        "memory_measurement_scopes": {
            "native_total_allocated_bytes": "CUMULATIVE GPROFNG NATIVE ALLOCATIONS; NOT LIVE RSS",
            "native_allocation_count": "NUMBER OF GPROFNG NATIVE ALLOCATION EVENTS",
            "native_peak_heap_bytes": "LIVE NATIVE HEAP PEAK; NOT WHOLE-PROCESS RSS",
            "whole_process_peak_rss_kib": "ENTIRE PROCESS MAXIMUM RSS IN KIBIBYTES",
            "python_tracemalloc_peak_bytes": "PYTHON-TRACKED ALLOCATIONS ONLY; EXCLUDES NATIVE HEAP",
            "native_leaked_bytes": "GPROFNG LEAK ACCOUNTING; NOT PER-FUNCTION CPU",
        },
        "per_function_cpu_profile": UNMEASURED,
        "clock_cpu_sampling_operational": False,
        "profiler_timer_status": "FAILED; itimer could not be set",
        "cpu_filename_actual_sort_metric": "INCLUSIVE BYTES LEAKED; NOT CPU TIME",
        "first_party_rust_native_ffi_marker_count": 80,
        "first_party_rust_native_ffi_marker_lines":
            context["summary"]["native_profiles"]["rust"]["native_ffi"]["native_ffi_marker_lines"],
        "whole_process_cpu_seconds_are_not_per_function_samples": True,
        "confidence_intervals": UNMEASURED,
        "final_speed": UNMEASURED,
        "final_native_memory": UNMEASURED,
        "final_holdout_opened": False,
        "final_holdout_status": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "qualified_candidate_count": 0, "winner_selected": False,
        "graphs": {
            "overall": {"path": OVERALL, "bytes": len(overall_graph), "sha256": digest(overall_graph)},
            "memory": {"path": MEMORY, "bytes": len(memory_graph), "sha256": digest(memory_graph)},
            "inputs": {"path": INPUTS, "bytes": len(inputs_bytes), "sha256": digest(inputs_bytes)},
        },
    }
    return {"overall": overall_graph, "memory": memory_graph,
            "inputs": inputs_bytes, "report": canonical(publication)}


def verify_assets(context: dict, result: dict, rendered: dict[str, bytes],
                  source_digest: str, source_size: int) -> None:
    require(rendered == public_assets(context, result, source_digest, source_size),
            "public V2 evidence outputs changed or are nondeterministic")
    inputs = parsed(rendered["inputs"], "complete public V2 graph inputs")
    report = parsed(rendered["report"], "complete public V2 evidence publication")
    same(inputs, {"status": "PASS", "scope": "PUBLIC PRACTICE ONLY",
                  "per_function_cpu_profile": UNMEASURED,
                  "clock_cpu_sampling_operational": False,
                  "profiler_timer_status": "FAILED; itimer could not be set",
                  "case_count_more_than_twenty_percent_slower": 73,
                  "dense_case_count_more_than_twenty_percent_slower": 69,
                  "confidence_intervals": UNMEASURED,
                  "final_speed": UNMEASURED, "final_native_memory": UNMEASURED,
                  "final_holdout_opened": False, "qualified_candidate_count": 0,
                  "winner_selected": False}, "honest public-only V2 graph boundaries")
    same(report, {"status": "PASS", "public_correctness_case_count": 416,
                   "public_timing_paired_observation_count": 1664,
                   "all_slower_paired_observation_count": 857,
                   "per_function_cpu_profile": UNMEASURED,
                   "clock_cpu_sampling_operational": False,
                   "profiler_timer_status": "FAILED; itimer could not be set",
                   "case_count_more_than_twenty_percent_slower": 73,
                   "dense_case_count_more_than_twenty_percent_slower": 69,
                   "cpu_filename_actual_sort_metric": "INCLUSIVE BYTES LEAKED; NOT CPU TIME",
                   "first_party_rust_native_ffi_marker_count": 80,
                   "confidence_intervals": UNMEASURED, "final_speed": UNMEASURED,
                   "final_native_memory": UNMEASURED, "final_holdout_opened": False,
                   "qualified_candidate_count": 0, "winner_selected": False},
         "honest public-only complete V2 profiling report")
    losses = report.get("all_slower_paired_observations")
    require(type(losses) is list and len(losses) == 857
            and value_digest(losses) == result["metrics"]["all_slower_pairs_sha256"],
            "an actual public V2 slowdown or regression disappeared")
    require(type(report.get("complete_case_results")) is list
            and len(report["complete_case_results"]) == 416,
            "an actual public V2 case disappeared")
    regressions = report.get("case_records_more_than_twenty_percent_slower")
    require(type(regressions) is list and len(regressions) == 73
            and value_digest(regressions)
            == result["metrics"]["cases_more_than_twenty_percent_slower_sha256"],
            "an actual public V2 distinct-case major regression disappeared")
    require(type(report.get("operation_results")) is dict
            and len(report["operation_results"]) == 26,
            "an actual public V2 operation disappeared")
    for picture in (rendered["overall"], rendered["memory"]):
        require(b'role="img"' in picture and b'aria-labelledby="title description"' in picture,
                "public V2 graph lost accessibility title or description")
    for token in (b"PUBLIC PRACTICE ONLY", b"0.595803047189324",
                  b"0.8649792983684755", b"0.8608014813128971",
                  b"0.21409330078969788", b"0.42168362785", b"1.26812071029",
                  b"222 / 416 cases faster", b"807 / 1,664", b"857 slower",
                  b"73 cases &gt;20% slower (69 dense)", b"itimer could not be set",
                  b"Per-function CPU: NOT MEASURED", b"CONFIDENCE: NOT MEASURED"):
        require(token in rendered["overall"], "public V2 performance graph omitted " + token.decode())
    for token in (b"104,211,416", b"100,547,111", b"260,204", b"284,705",
                  b"53,002,684", b"53,002,716", b"71,660", b"38,172",
                  b"114,389", b"192,184", b"Inclusive Bytes Leaked",
                  b"itimer could not be set",
                  b"Per-function CPU is NOT MEASURED"):
        require(token in rendered["memory"], "public V2 memory graph omitted " + token.decode())


def self_tests(context: dict, result: dict, source_digest: str,
               source_size: int, wall: SourceWall) -> int:
    labels = []

    def reject(label: str, mutation) -> None:
        hostile = copy.deepcopy(context)
        mutation(hostile)
        try:
            verify(hostile)
        except (Rejected, TypeError, KeyError, ValueError, IndexError, UnicodeError):
            labels.append(label)
            return
        raise Rejected("hostile complete public V2 evidence was accepted: " + label)

    for name, key, value in (
        ("V2 manifest denominator inflated", "case_count", 417),
        ("V2 manifest source replaced", "source_sha256", "0" * 64),
        ("V2 manifest holdout admitted", "approved_output_prefix", "oracle/phase3/holdout"),
    ):
        reject(name, lambda x, k=key, v=value: x["manifest"].__setitem__(k, v))
    reject("V2 prior failure erased", lambda x: x["manifest"]["preserved_failure"].__setitem__("paired_rows", 1663))
    reject("V2 final freeze fabricated", lambda x: x.__setitem__("protocol", x["protocol"].replace(b"NOT FROZEN", b"FROZEN")))
    reject("V2 summary denominator inflated", lambda x: x["summary"].__setitem__("case_count", 417))
    reject("V2 summary pairing removed", lambda x: x["summary"].__setitem__("paired_rounds", 3))
    reject("V2 summary qualification fabricated", lambda x: x["summary"].__setitem__("final_winner_selected", True))
    reject("V2 summary raw artifact removed", lambda x: x["summary"]["artifacts"].pop())
    reject("V2 summary Rust profile removed", lambda x: x["summary"]["native_profiles"].pop("rust"))
    reject("V2 matrix case removed", lambda x: x["matrix"].pop())
    reject("V2 matrix text/bytes reweighted", lambda x: x["matrix"][0].__setitem__("domain", "bytes"))
    reject("V2 public correctness loss hidden", lambda x: x["top"]["rust.correctness.raw.json"]["records"].pop())
    reject("V2 public correctness outcome altered", lambda x: x["top"]["rust.correctness.raw.json"]["records"][0]["outcome"].__setitem__("status", "error"))
    reject("V2 public correctness worker reused", lambda x: x["top"]["rust.correctness.raw.json"].__setitem__("pid", 81))
    reject("V2 candidate delegated", lambda x: x["top"]["rust.correctness.raw.json"]["engine_provenance"].__setitem__("candidate_owned_forbidden_import_attempts", ["re"]))
    reject("V2 timing worker row removed", lambda x: x["top"]["rust.timing-round-02.raw.json"]["rows"].pop())
    reject("V2 timing worker duration changed", lambda x: x["top"]["stdlib.timing-round-01.raw.json"]["rows"][0].__setitem__("elapsed_ns", 1))
    reject("V2 timing expected outcome changed", lambda x: x["top"]["rust.timing-round-03.raw.json"]["rows"][0].__setitem__("expected_outcome_sha256", "0" * 64))
    reject("V2 paired slowdown hidden", lambda x: x["top"]["paired-timing.raw.json"]["rows"].pop())
    reject("V2 paired order fabricated", lambda x: x["top"]["paired-timing.raw.json"]["rows"][0]["pair_order"].reverse())
    reject("V2 paired duration replaced", lambda x: x["top"]["paired-timing.raw.json"]["rows"][0].__setitem__("rust_elapsed_ns", 1))
    reject("V2 dense regression hidden", lambda x: x["summary"]["paired_results"]["by_cohort"]["mandatory_literal_dense_same_first_byte"].__setitem__("baseline_over_rust_ratio", 1.5))
    reject("V2 operation regression hidden", lambda x: x["summary"]["paired_results"]["by_operation"].pop("module.split"))
    reject("V2 stdlib collector banner removed", lambda x: x["profile"]["stdlib"].__setitem__("collector.stdout.raw.txt", x["profile"]["stdlib"]["collector.stdout.json"]))
    reject("V2 Rust collector PID forged", lambda x: x["summary"]["native_profiles"]["rust"].__setitem__("target_pid", 91))
    reject("V2 stdlib timer failure suppressed", lambda x: x["logs"].__setitem__(
        "stdlib", x["logs"]["stdlib"].replace(TIMER_FAILURE, b"", 1)))
    reject("V2 Rust timer failure suppressed", lambda x: x["logs"].__setitem__(
        "rust", x["logs"]["rust"].replace(TIMER_FAILURE, b"", 1)))
    reject("V2 CPU sampling fabricated", lambda x: x["logs"].__setitem__(
        "rust", x["logs"]["rust"].replace(b'<profile name="heaptrace">',
                                             b'<profile name="cpu">', 1)))
    reject("V2 profiler stderr suppressed", lambda x: x["profile"]["rust"].__setitem__("cpu.stderr.txt", b"failure"))
    reject("V2 false CPU report fabricated", lambda x: x["profile"]["rust"].__setitem__("cpu.txt", x["profile"]["rust"]["cpu.txt"].replace(b"Inclusive Bytes Leaked", b"Exclusive CPU Seconds", 1)))
    reject("V2 Rust native allocation lost", lambda x: x["profile"]["rust"].__setitem__("heap.txt", x["profile"]["rust"]["heap.txt"].replace(b"104211416", b"104211415")))
    reject("V2 Rust native heap peak lost", lambda x: x["profile"]["rust"].__setitem__("heap.txt", x["profile"]["rust"]["heap.txt"].replace(b"53002684", b"53002683")))
    reject("V2 Python native allocation count lost", lambda x: x["profile"]["stdlib"].__setitem__("allocations.txt", x["profile"]["stdlib"]["allocations.txt"].replace(b"284705", b"284704", 1)))
    reject("V2 Rust RSS conflated with native heap", lambda x: x["summary"]["native_profiles"]["rust"]["python_heap"].__setitem__("maximum_rss_kib", 53002684))
    reject("V2 Python tracemalloc conflated with RSS", lambda x: x["summary"]["native_profiles"]["stdlib"]["python_heap"].__setitem__("tracemalloc_peak_bytes", 38172))
    reject("V2 first-party FFI marker removed", lambda x: x["summary"]["native_profiles"]["rust"]["native_ffi"].__setitem__("native_ffi_marker_count", 79))
    reject("V2 first-party FFI owner hidden", lambda x: x["summary"]["native_profiles"]["rust"]["native_ffi"]["native_ffi_marker_lines"].pop())

    original = public_assets(context, result, source_digest, source_size)
    verify_assets(context, result, original, source_digest, source_size)

    def reject_output(label: str, name: str, mutation) -> None:
        hostile = dict(original)
        document = parsed(hostile[name], "hostile generated public V2 output")
        mutation(document)
        hostile[name] = canonical(document)
        try:
            verify_assets(context, result, hostile, source_digest, source_size)
        except (Rejected, TypeError, KeyError, ValueError):
            labels.append(label)
            return
        raise Rejected("hostile V2 public output was accepted: " + label)

    reject_output("published V2 loss removed", "report", lambda x: x["all_slower_paired_observations"].pop())
    reject_output("published V2 case removed", "report", lambda x: x["complete_case_results"].pop())
    reject_output("published V2 major case regression hidden", "report",
                  lambda x: x["case_records_more_than_twenty_percent_slower"].pop())
    reject_output("published V2 CPU functions invented", "report", lambda x: x.__setitem__("per_function_cpu_profile", "MEASURED"))
    reject_output("published V2 leaked bytes called CPU", "inputs", lambda x: x.__setitem__("per_function_cpu_profile", "CPU PROFILE"))
    reject_output("published V2 timer failure denied", "report",
                  lambda x: x.__setitem__("clock_cpu_sampling_operational", True))
    reject_output("published V2 confidence invented", "report", lambda x: x.__setitem__("confidence_intervals", "95%"))
    reject_output("published V2 final speed invented", "inputs", lambda x: x.__setitem__("final_speed", "1.5x"))
    reject_output("published V2 final memory invented", "report", lambda x: x.__setitem__("final_native_memory", 1))
    reject_output("published V2 holdout opened", "inputs", lambda x: x.__setitem__("final_holdout_opened", True))
    reject_output("published V2 qualification invented", "report", lambda x: x.__setitem__("qualified_candidate_count", 3))
    reject_output("published V2 winner fabricated", "inputs", lambda x: x.__setitem__("winner_selected", True))

    def reject_wall(label: str, event: str, arguments: tuple) -> None:
        try:
            wall.check(event, arguments)
        except Rejected:
            labels.append(label)
            return
        raise Rejected("hostile V2 source-only effect was accepted: " + label)

    reject_wall("candidate source open", "open", (os.path.join(ROOT, "candidates/rust_candidate.py"), None, os.O_RDONLY | os.O_NOFOLLOW))
    reject_wall("native binary open", "open", (os.path.join(ROOT, "candidates/_rust_engine.so"), None, os.O_RDONLY | os.O_NOFOLLOW))
    reject_wall("holdout case open", "open", (os.path.join(ROOT, "oracle/phase3/hidden.json"), None, os.O_RDONLY | os.O_NOFOLLOW))
    reject_wall("profile binary open", "open", ("/usr/bin/gprofng", None, os.O_RDONLY | os.O_NOFOLLOW))
    reject_wall("unowned README write", "open", (os.path.join(ROOT, "README.md"), None, os.O_WRONLY | os.O_CREAT))
    reject_wall("owned source-mode write", "open", (os.path.join(ROOT, OVERALL), None, os.O_WRONLY | os.O_CREAT))
    reject_wall("evidence symlink following", "open", (os.path.join(ROOT, SUMMARY[0]), None, os.O_RDONLY))
    reject_wall("candidate process spawn", "subprocess.Popen", (PYTHON,))
    reject_wall("profiler process spawn", "subprocess.Popen", ("/usr/bin/gprofng",))
    reject_wall("native library load", "ctypes.dlopen", ("_rust_engine.so",))
    reject_wall("clock sampled", "time.perf_counter", ())
    reject_wall("network opened", "socket.connect", ("example.invalid",))
    reject_wall("candidate imported", "import", ("candidates.rust_candidate",))
    reject_wall("stdlib matching imported", "import", ("re",))
    return len(labels)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--verify-source", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    for name in ("source", "driver", "protocol", "manifest", "summary", "paired",
                 "stdlib-correctness", "rust-correctness"):
        parser.add_argument("--" + name + "-sha256", required=True)
    return parser.parse_args()


def write(path: str, payload: bytes) -> None:
    descriptor = os.open(os.path.join(ROOT, path),
                         os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        position = 0
        while position < len(payload):
            written = os.write(descriptor, payload[position:])
            require(written > 0, "exclusive V2 public output write was interrupted")
            position += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def main() -> int:
    options = arguments()
    require(sys.executable == PYTHON and sys.version_info[:3] == (3, 14, 6)
            and sys.flags.isolated and sys.flags.dont_write_bytecode,
            "the frozen isolated bytecode-disabled stable CPython 3.14.6 is required")
    for actual, expected, label in (
        (options.driver_sha256, DRIVER[1], "committed V2 profile source"),
        (options.protocol_sha256, PROTOCOL[1], "committed V2 profile protocol"),
        (options.manifest_sha256, MANIFEST[1], "committed V2 profile manifest"),
        (options.summary_sha256, SUMMARY[1], "complete actual V2 public profile summary"),
        (options.paired_sha256, TOP["paired-timing.raw.json"][1], "complete actual V2 paired rows"),
        (options.stdlib_correctness_sha256, TOP["stdlib.correctness.raw.json"][1], "actual public CPython vector"),
        (options.rust_correctness_sha256, TOP["rust.correctness.raw.json"][1], "actual public Rust vector"),
    ):
        require(actual == expected, "frozen public V2 SHA-256 changed: " + label)
    source_digest = options.source_sha256
    require(len(source_digest) == 64 and all(char in "0123456789abcdef" for char in source_digest),
            "V2 public renderer fingerprint must be lowercase SHA-256")
    wall = SourceWall(options.render)
    sys.addaudithook(wall.check)
    source_size = os.stat(os.path.join(ROOT, SELF), follow_symlinks=False).st_size
    source = owner((SELF, source_digest, source_size))
    owner(DRIVER)
    protocol = owner(PROTOCOL)
    manifest = parsed(owner(MANIFEST), "committed V2 source manifest", canonical_required=False)
    for spec in PREVIOUS.values():
        owner(spec)
    summary = parsed(owner(SUMMARY), "complete actual public V2 profiler summary")
    top = {
        name: parsed(owner((SESSION + "/" + name, item[1], item[0])),
                     "complete actual public artifact " + name)
        for name, item in TOP.items()
    }
    profile = {}
    for engine, artifacts in PROFILE.items():
        profile[engine] = {
            suffix: owner((SESSION + "/" + engine + "." + suffix, item[1], item[0]))
            for suffix, item in artifacts.items()
        }
    logs = {engine: owner(spec) for engine, spec in LOGS.items()}
    actual_matrix = build_matrix()
    context = {"protocol": protocol, "manifest": manifest, "summary": summary,
               "top": top, "profile": profile, "logs": logs, "matrix": actual_matrix,
               "matrix_by_case": {case["case"]: case for case in actual_matrix}}
    result = verify(context)
    output = public_assets(context, result, source_digest, len(source))
    verify_assets(context, result, output, source_digest, len(source))
    rejected = self_tests(context, result, source_digest, len(source), wall) if options.self_test else 0
    if options.render:
        for key, path in (("overall", OVERALL), ("memory", MEMORY),
                          ("inputs", INPUTS), ("report", REPORT)):
            write(path, output[key])
    report = {
        "status": "PASS",
        "mode": "self-test" if options.self_test else "render" if options.render else "verify-source",
        "scope": "PUBLIC PRACTICE ONLY",
        "source_sha256": source_digest, "source_bytes": len(source),
        "hostile_control_count": rejected,
        "public_correctness_case_count": 416,
        "public_correctness_cases_matching_python": 416,
        "public_paired_observation_count": 1664,
        "public_aggregate_total_elapsed_speedup": 0.595803047189324,
        "public_dense_aggregate_speedup": 0.21409330078969788,
        "public_equal_case_geometric_speedup": 0.8649792983684755,
        "public_equal_pair_geometric_speedup": 0.8608014813128971,
        "public_dense_equal_case_geometric_speedup":
            result["metrics"]["dense_equal_case_geometric_speedup"],
        "public_non_dense_combined_aggregate_speedup": 1.2681207102924326,
        "rust_faster_case_count": 222,
        "rust_slower_case_count": 194,
        "cases_more_than_twenty_percent_slower": 73,
        "dense_cases_more_than_twenty_percent_slower": 69,
        "rust_faster_pair_count": 807,
        "rust_slower_pair_count": 857,
        "rust_native_total_allocated_bytes": 104211416,
        "python_native_total_allocated_bytes": 100547111,
        "rust_native_allocation_count": 260204,
        "python_native_allocation_count": 284705,
        "rust_native_peak_heap_bytes": 53002684,
        "python_native_peak_heap_bytes": 53002716,
        "rust_whole_process_peak_rss_kib": 71660,
        "python_whole_process_peak_rss_kib": 38172,
        "rust_python_tracemalloc_peak_bytes": 114389,
        "python_python_tracemalloc_peak_bytes": 192184,
        "first_party_rust_native_ffi_marker_count": 80,
        "per_function_cpu_profile": UNMEASURED,
        "clock_cpu_sampling_operational": False,
        "profiler_timer_status": "FAILED; itimer could not be set",
        "confidence_intervals": UNMEASURED,
        "final_speed": UNMEASURED,
        "final_native_memory": UNMEASURED,
        "final_holdout_opened": False,
        "qualified_candidate_count": 0,
        "source_mode_candidate_imports": 0,
        "source_mode_processes_started": 0,
        "source_mode_profiler_invocations": 0,
        "source_mode_clock_samples": 0,
        "source_mode_holdout_files_read": 0,
        "source_mode_native_candidate_files_opened": 0,
        "workspace_file_writes": 4 if options.render else 0,
        "outputs": {
            key: {"path": path, "bytes": len(output[key]), "sha256": digest(output[key])}
            for key, path in (("overall", OVERALL), ("memory", MEMORY),
                              ("inputs", INPUTS), ("report", REPORT))
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
