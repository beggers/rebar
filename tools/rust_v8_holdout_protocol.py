#!/usr/bin/env python3
"""Verify a prospectively sealed, independent 12,288-case performance test.

Verification and self-tests never open a seed, generate a held-back case, import
a candidate, run a benchmark, or inspect an older performance fixture. Opening
the final test is deliberately a separate, explicit, irreversible operation.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import collections
import contextlib
import gzip
import hashlib
import hmac
import io
import json
import locale
import math
import os
import platform
import random
import select
import statistics
import subprocess
import sys
import time
import unicodedata
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "performance/v8/holdout-manifest.json"
EVIDENCE_PATH = ROOT / "performance/v8/evidence/HOLDOUT-PROTOCOL-SELF-TEST.json"
SCHEMA = "rebar-v8-prospective-performance-holdout-v1"
SELF_TEST_SCHEMA = "rebar-v8-prospective-performance-holdout-self-test-v1"
CASE_SCHEMA = "rebar-v8-prospective-performance-case-v1"
BUFFER_WIRE_SCHEMA = "rebar-v8-buffer-wire-v1"
ROW_SCHEMA = "rebar-v8-prospective-performance-paired-row-v1"
SUMMARY_SCHEMA = "rebar-v8-prospective-performance-summary-v1"
API_FAMILIES = (
    "compile",
    "escape",
    "search",
    "match",
    "fullmatch",
    "findall",
    "finditer",
    "split",
    "sub",
    "subn",
    "match-surface",
    "scanner",
)
WORKLOAD_FAMILIES = (
    "literal-and-long-prefix",
    "character-class-and-unicode",
    "anchors-boundaries-and-windows",
    "greedy-lazy-atomic-and-possessive",
    "alternation-groups-and-backreferences",
    "lookaround-and-zero-width",
    "replacement-split-and-result-density",
    "logs-paths-urls-identifiers-and-noise",
)
NORMAL_APIS = frozenset(
    {"search", "match", "fullmatch", "findall", "finditer", "split", "sub", "subn"}
)
BANNED_ENGINE_MODULES = frozenset(
    {
        "re",
        "_sre",
        "regex",
        "re2",
        "google_re2",
        "pcre",
        "pcre2",
        "hyperscan",
        "oniguruma",
    }
)
CASE_COUNT = 12_288
CASES_PER_CELL = 128
CASES_PER_API = 1_024
PAIRED_ROUNDS = 31
WARMUPS = 4
BOOTSTRAP_DRAWS = 9_999
MINIMUM_SIGNIFICANT_WINS = 7_373
STUDENT_T_DF30_975 = 2.0422724563012373
RUNTIME_REGRESSION_THRESHOLD = 5.0 / 6.0
SYNTHETIC_ORDER_SEED = 0x5245424152563853
EDGE_SCHEMA = "rebar-v7-independent-edge-oracle-v1"
CANDIDATE_FREEZE_SCHEMA = "rebar-v8-final-candidate-freeze-v1"
DEEP_CONTRACT_SCHEMA = "rebar-rust-v8-deep-public-contract-v1"
DEEP_CONTRACT_SOURCE_SHA256 = "ba4b640d12444a5346d918a039d8a7a9fef0c78a54f6b66c6f0eb0c9dddbe978"
DEEP_CONTRACT_FIXTURE_SHA256 = "c72a5e47f15c94ce13ce34d4918c05ef81eea5b010ac119b255264e60939ef16"
DEEP_CONTRACT_REFERENCE_SHA256 = "b184f3388320909b3c28fbd3ce9c15cefc992d3e852e9495ad8fb503d1cbaad8"
DEEP_CONTRACT_SEED = 2026072347
DEEP_CONTRACT_CHECKS = 393
DEEP_CONTRACT_PRIVATE_ROWS = 64
UNSEAL_AUTHORIZATION = "UNSEAL-FROZEN-V8-HOLDOUT-AFTER-CANDIDATE-SELECTION"
MEMORY_CELL_INDICES = frozenset({0, 17, 34, 51, 68, 85, 102, 119})
SYNTHETIC_CASE_OPENING = hashlib.sha256(
    b"rebar-v8-public-synthetic-structure-only-not-a-holdout-opening-v1"
).digest()


ISOLATED_WORKER = r'''
import builtins
import hashlib
import importlib
import marshal
import math
import os
import resource
import sys
import time

ROOT, NAME, KIND = sys.argv[1:]
BANNED = frozenset(("re", "_sre", "regex", "re2", "google_re2", "pcre", "pcre2", "hyperscan", "oniguruma"))
original_import = builtins.__import__

def send(document):
    payload = marshal.dumps(document)
    header = len(payload).to_bytes(8, "big")
    for part in (header, payload):
        view = memoryview(part)
        while view:
            written = os.write(1, view)
            if written <= 0:
                raise RuntimeError("worker response write failed")
            view = view[written:]

def receive():
    header = bytearray()
    while len(header) < 8:
        part = os.read(0, 8 - len(header))
        if not part:
            return None
        header.extend(part)
    length = int.from_bytes(header, "big")
    if not 0 < length <= 4 * 1024 * 1024:
        raise RuntimeError("invalid isolated worker frame")
    payload = bytearray()
    while len(payload) < length:
        part = os.read(0, min(65536, length - len(payload)))
        if not part:
            raise RuntimeError("truncated isolated worker request")
        payload.extend(part)
    return marshal.loads(bytes(payload))

def blocked_import(name, globals=None, locals=None, fromlist=(), level=0):
    if isinstance(name, str) and name.split(".", 1)[0] in BANNED:
        raise ImportError("v8 candidate cannot import a built-in or external regex engine")
    return original_import(name, globals, locals, fromlist, level)

def native_artifacts():
    found = {}
    prefix = os.path.join(ROOT, "candidates") + os.sep
    try:
        with original_import("builtins").open("/proc/self/maps", "r", encoding="utf-8", errors="surrogateescape") as stream:
            for line in stream:
                fields = line.split(maxsplit=5)
                if len(fields) != 6:
                    continue
                path = fields[5].strip()
                if path.startswith(prefix) and ".so" in os.path.basename(path) and not path.endswith(" (deleted)"):
                    if path not in found:
                        result = hashlib.sha256()
                        with original_import("builtins").open(path, "rb") as item:
                            for block in iter(lambda: item.read(1048576), b""):
                                result.update(block)
                        found[path] = result.hexdigest()
    except OSError as error:
        raise RuntimeError("candidate native mappings cannot be independently verified") from error
    return found

def forbidden_state(inspect_native=False):
    modules = sorted(BANNED.intersection(sys.modules))
    foreign = sorted(
        name for name in sys.modules
        if name.startswith("candidates.") and name.endswith("_candidate") and name != NAME
    )
    external = []
    if inspect_native:
        try:
            with original_import("builtins").open("/proc/self/maps", "r", encoding="utf-8", errors="surrogateescape") as stream:
                for line in stream:
                    fields = line.split(maxsplit=5)
                    if len(fields) != 6:
                        continue
                    location = fields[5].strip()
                    name = os.path.basename(location).lower()
                    if any(token in name for token in ("libpcre", "libregex", "libre2", "libhyperscan", "libonig")):
                        external.append(location)
        except OSError as error:
            raise RuntimeError("candidate external-engine mappings cannot be audited") from error
    return {"forbidden_loaded": modules, "foreign_candidates": foreign, "external_regex_libraries": sorted(set(external))}

def require_candidate_clean(inspect_native=False):
    if NAME == "re" or KIND != "timing":
        return {"forbidden_loaded": [], "foreign_candidates": [], "external_regex_libraries": []}
    state = forbidden_state(inspect_native)
    if any(state.values()):
        raise RuntimeError("candidate delegated to a built-in, external, or other candidate regex engine")
    return state

def normalize(value, subject, depth=0):
    if depth > 12:
        raise RuntimeError("candidate result exceeds frozen normalization depth")
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, bytes):
        return {"type": "bytes", "hex": value.hex(), "is_subject": value is subject}
    if isinstance(value, (tuple, list)):
        if len(value) > 128:
            raise RuntimeError("candidate result exceeds frozen result bound")
        return {"type": type(value).__name__, "items": [normalize(item, subject, depth + 1) for item in value]}
    if isinstance(value, dict):
        return {"type": "dict", "items": [[str(key), normalize(item, subject, depth + 1)] for key, item in sorted(value.items())]}
    if hasattr(value, "span") and hasattr(value, "groups") and hasattr(value, "groupdict"):
        return {
            "type": "match",
            "span": normalize(value.span(), subject, depth + 1),
            "groups": normalize(value.groups(), subject, depth + 1),
            "groupdict": normalize(value.groupdict(), subject, depth + 1),
            "lastindex": value.lastindex,
            "lastgroup": value.lastgroup,
            "regs": normalize(value.regs, subject, depth + 1),
            "same_subject": value.string is subject,
            "whole_match_is_subject": value.group(0) is subject,
        }
    if hasattr(value, "pattern") and hasattr(value, "flags") and hasattr(value, "groupindex"):
        return {
            "type": "compiled-pattern",
            "pattern": normalize(value.pattern, subject, depth + 1),
            "flags": value.flags,
            "groups": value.groups,
            "groupindex": normalize(dict(value.groupindex), subject, depth + 1),
        }
    if hasattr(value, "__iter__"):
        iterator = iter(value)
        results = []
        for _ in range(129):
            try:
                item = next(iterator)
            except StopIteration:
                return {"type": "iterator", "items": results}
            if len(results) == 128:
                raise RuntimeError("candidate iterator exceeds frozen result bound")
            results.append(normalize(item, subject, depth + 1))
    raise RuntimeError("candidate returned an unsupported or unobservable result")

def invoke(module, case):
    api = case["api"]
    pattern = case["pattern"]
    subject = case["subject"]
    source_kind = case.get("source_kind")
    if source_kind in ("bytearray", "memoryview"):
        if not isinstance(subject, dict) or set(subject) != {"schema", "kind", "hex"}:
            raise RuntimeError("mutable-byte subject has no exact transport representation")
        if subject.get("schema") != "rebar-v8-buffer-wire-v1" or subject.get("kind") != source_kind:
            raise RuntimeError("mutable-byte subject transport kind was substituted")
        encoded = subject.get("hex")
        if not isinstance(encoded, str):
            raise RuntimeError("mutable-byte subject transport is invalid")
        try:
            raw_subject = bytes.fromhex(encoded)
        except ValueError as error:
            raise RuntimeError("mutable-byte subject transport is corrupt") from error
        subject = bytearray(raw_subject) if source_kind == "bytearray" else memoryview(raw_subject)
    elif source_kind == "bytes":
        if not isinstance(subject, bytes):
            raise RuntimeError("bytes case did not materialize an actual bytes subject")
    elif source_kind == "str":
        if not isinstance(subject, str):
            raise RuntimeError("text case did not materialize an actual text subject")
    else:
        raise RuntimeError("case subject has an unknown frozen source type")
    flags = case["flags"]
    events = []
    replacement = case.get("replacement")

    if case.get("callback"):
        def replacement(match):
            events.append(normalize(match, subject))
            return b"X" if isinstance(subject, (bytes, bytearray, memoryview)) else "X"

    try:
        if api == "compile":
            value = module.compile(pattern, flags)
        elif api == "escape":
            value = module.escape(subject)
        elif api == "match-surface":
            compiled = module.compile(pattern, flags)
            found = compiled.search(subject) if case["surface"] == "compiled" else module.search(pattern, subject, flags)
            if found is None:
                raise RuntimeError("match-surface case did not produce a genuine match")
            mode = case["capture"]
            if mode == "numbered":
                value = (found.group(0), found.span(), found.groups())
            elif mode == "named":
                value = (found.groupdict(), found.lastgroup, found.lastindex)
            elif mode == "optional":
                value = (found.groups(None), found.regs)
            else:
                value = (found.group(0), found.groups(), found.groupdict(), found.regs)
        elif api == "scanner":
            scanner = module.compile(pattern, flags).scanner(subject)
            method = getattr(scanner, case["scanner_method"])
            value = []
            for _ in range(16):
                found = method()
                if found is None:
                    break
                value.append(found)
            else:
                raise RuntimeError("scanner exceeded frozen empty-match progression bound")
        elif case["surface"] == "compiled":
            compiled = module.compile(pattern, flags)
            method = getattr(compiled, api)
            if api in ("sub", "subn"):
                value = method(replacement, subject, case.get("count", 0))
            elif api == "split":
                value = method(subject, case.get("maxsplit", 0))
            elif api in ("search", "match", "fullmatch", "findall", "finditer") and case.get("window"):
                value = method(subject, case["window"][0], case["window"][1])
            else:
                value = method(subject)
        else:
            method = getattr(module, api)
            if api in ("sub", "subn"):
                value = method(pattern, replacement, subject, case.get("count", 0), flags)
            elif api == "split":
                value = method(pattern, subject, case.get("maxsplit", 0), flags)
            else:
                value = method(pattern, subject, flags)
        return {"status": "ok", "result": normalize(value, subject), "callbacks": events}
    except Exception as error:
        return {
            "status": "error",
            "type": type(error).__module__ + "." + type(error).__qualname__,
            "message": str(error),
            "args": normalize(error.args, subject),
            "position": getattr(error, "pos", None),
            "line": getattr(error, "lineno", None),
            "column": getattr(error, "colno", None),
            "callbacks": events,
        }

def prepare(module, case):
    if case["api"] == "compile" and case.get("lifecycle") == "cold-cache":
        module.purge()
    elif case["api"] == "compile" and case.get("lifecycle") == "warm-cache":
        module.compile(case["pattern"], case["flags"])

def rss_bytes():
    with original_import("builtins").open("/proc/self/statm", "r", encoding="ascii") as source:
        parts = source.read().split()
    return int(parts[1]) * os.sysconf("SC_PAGE_SIZE")

try:
    if NAME == "re":
        module = importlib.import_module("re")
    else:
        forbidden = sorted(BANNED.intersection(sys.modules))
        if forbidden:
            raise RuntimeError("candidate startup already contains a prohibited regex engine")
        sys.path.insert(0, ROOT)
        builtins.__import__ = blocked_import
        module = importlib.import_module(NAME)
        forbidden = sorted(BANNED.intersection(sys.modules))
        if forbidden:
            raise RuntimeError("candidate imported a prohibited regex engine")
    source_path = os.path.realpath(getattr(module, "__file__", ""))
    source_digest = None
    if source_path:
        digest = hashlib.sha256()
        with original_import("builtins").open(source_path, "rb") as stream:
            for chunk in iter(lambda: stream.read(1048576), b""):
                digest.update(chunk)
        source_digest = digest.hexdigest()
    if KIND == "memory":
        builtins.__import__ = original_import
        tracemalloc = importlib.import_module("tracemalloc")
        if NAME != "re":
            builtins.__import__ = blocked_import
    startup = require_candidate_clean(True)
    send({"kind": "ready", "module": NAME, "worker": KIND, "source": source_path, "source_sha256": source_digest, "native": native_artifacts(), "startup_forbidden": startup["forbidden_loaded"] if NAME != "re" else ["baseline-allowed"], "foreign_candidates": startup["foreign_candidates"], "external_regex_libraries": startup["external_regex_libraries"]})
    while True:
        request = receive()
        if request is None or request.get("action") == "close":
            break
        case = request["case"]
        if request["action"] == "warmup":
            prepare(module, case)
            send({"kind": "warmup", "observation": invoke(module, case)})
        elif request["action"] == "sample" and KIND == "timing":
            require_candidate_clean()
            prepare(module, case)
            before = invoke(module, case)
            prepare(module, case)
            start = time.perf_counter_ns()
            observed = invoke(module, case)
            elapsed = time.perf_counter_ns() - start
            prepare(module, case)
            after = invoke(module, case)
            state = require_candidate_clean()
            send({"kind": "sample", "before": before, "observed": observed, "after": after, "elapsed_ns": elapsed, **state})
        elif request["action"] == "memory" and KIND == "memory":
            before_rss = rss_bytes()
            tracemalloc.start()
            try:
                prepare(module, case)
                observation = invoke(module, case)
                current, peak = tracemalloc.get_traced_memory()
            finally:
                tracemalloc.stop()
            send({"kind": "memory", "observation": observation, "python_current_bytes": current, "python_peak_bytes": peak, "process_current_before_bytes": before_rss, "process_current_after_bytes": rss_bytes(), "process_peak_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024, "instrumentation_worker": True})
        elif request["action"] == "provenance":
            send({"kind": "provenance", "module": NAME, "source": source_path, "source_sha256": source_digest, "native": native_artifacts(), **require_candidate_clean(True)})
        else:
            raise RuntimeError("invalid isolated worker action or worker kind")
except BaseException as error:
    try:
        send({"kind": "error", "type": type(error).__name__, "message": str(error)})
    except BaseException:
        pass
    raise
'''


class ProtocolError(RuntimeError):
    """A seal, measurement, independence, or correctness obligation failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProtocolError(message)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def canonical_digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def is_hex_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def manifest_binding(document: dict[str, Any]) -> str:
    body = {key: value for key, value in document.items() if key != "binding_sha256"}
    return canonical_digest(body)


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    require(path.resolve() == MANIFEST_PATH.resolve(), "the v8 manifest path is not frozen")
    try:
        with path.open("rb") as stream:
            document = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ProtocolError("cannot decode the frozen v8 manifest") from error
    require(isinstance(document, dict), "the frozen v8 manifest is not an object")
    return document


def validate_manifest(document: dict[str, Any], *, check_source: bool = True) -> None:
    require(document.get("schema") == SCHEMA, "the expanded holdout schema changed")
    require(
        document.get("state") == "sealed-not-materialized",
        "the expanded holdout is no longer prospectively sealed",
    )
    reference = document.get("reference")
    require(isinstance(reference, dict), "the pinned reference is missing")
    require(reference.get("implementation") == "CPython", "the oracle must be CPython")
    require(reference.get("version") == "3.14.6", "the pinned CPython version changed")
    require(reference.get("unicode_version") == "16.0.0", "the Unicode oracle changed")
    require(reference.get("character_locale") == "C", "the frozen C locale changed")
    require(platform.python_implementation() == "CPython", "not running CPython")
    require(tuple(sys.version_info[:3]) == (3, 14, 6), "not running pinned CPython 3.14.6")
    require(unicodedata.unidata_version == "16.0.0", "the running Unicode version changed")

    source = document.get("source")
    require(isinstance(source, dict), "the frozen generator identity is missing")
    require(
        source.get("path") == "tools/rust_v8_holdout_protocol.py",
        "the frozen generator path changed",
    )
    require(is_hex_digest(source.get("sha256")), "the generator digest is invalid")
    if check_source:
        require(
            hmac.compare_digest(file_digest(Path(__file__).resolve()), source["sha256"]),
            "the frozen generator source has changed",
        )

    seal = document.get("seal")
    require(isinstance(seal, dict), "the holdout seal is missing")
    require(seal.get("algorithm") == "sha256", "the seed commitment algorithm changed")
    require(is_hex_digest(seal.get("opening_sha256")), "the blinded seed commitment is invalid")
    require(seal.get("opening_bytes") == 32, "the blinded opening size changed")
    require(seal.get("opening_mode") == "0600", "the blinded opening permissions changed")
    require(
        seal.get("opening_path")
        == "/tmp/rebar-v8-final-holdout-opening-20260723-12288-v1.bin",
        "the exact out-of-repository opening path changed",
    )
    require(
        seal.get("isolation") == "procedural-same-unix-user-not-security-boundary",
        "same-user temporary-file protection was misrepresented",
    )

    layout = document.get("layout")
    require(isinstance(layout, dict), "the frozen factorial layout is missing")
    require(layout.get("cases") == CASE_COUNT, "the 12,288-case denominator changed")
    require(layout.get("cases_per_api") == CASES_PER_API, "an API denominator changed")
    require(layout.get("cases_per_cell") == CASES_PER_CELL, "a workload-cell size changed")
    require(layout.get("apis") == list(API_FAMILIES), "the 12 public API families changed")
    require(
        layout.get("workloads") == list(WORKLOAD_FAMILIES),
        "the eight balanced workload families changed",
    )
    require(
        CASE_COUNT == len(API_FAMILIES) * len(WORKLOAD_FAMILIES) * CASES_PER_CELL,
        "the published case-count multiplication is false",
    )
    require(
        layout.get("case_identity")
        == "descriptor-coordinate-and-domain-separated-hmac-semantic-regex-comment",
        "expanded matching cases do not have independently unique frozen identities",
    )
    require(
        layout.get("mutable_buffer_transport")
        == "explicit-tagged-hex-materialized-as-bytearray-or-memoryview",
        "mutable byte cases do not require actual reconstructed buffer objects",
    )
    factors = layout.get("applicability")
    require(isinstance(factors, dict), "API-specific applicability rules are missing")
    require(set(factors) == set(API_FAMILIES), "an API applicability rule is missing")
    for api in NORMAL_APIS:
        rule = factors[api]
        require(
            rule.get("surface") == ["module", "compiled"]
            and rule.get("input") == ["str", "bytes"]
            and rule.get("outcome") == ["hit", "miss"]
            and rule.get("variants_per_factor") == 16,
            f"the genuine module/compiled factorial changed: {api}",
        )
    require(
        factors["compile"].get("surface") == ["module"]
        and factors["escape"].get("surface") == ["module"],
        "compile or escape was assigned a fictional compiled-pattern method",
    )
    require(
        factors["match-surface"].get("outcome") == ["hit"],
        "match-object access cannot be measured on a missing match",
    )
    require(
        factors["scanner"].get("surface") == ["compiled-pattern-scanner"],
        "scanner timing must use an actual compiled pattern scanner",
    )

    trials = document.get("trials")
    require(isinstance(trials, dict), "the paired-trial protocol is missing")
    require(trials.get("paired_rounds") == PAIRED_ROUNDS, "the 31 paired rounds changed")
    require(trials.get("warmups") == WARMUPS, "the four warmups changed")
    require(trials.get("maximum_operations") == 16, "the fixed operation bound changed")
    require(trials.get("case_timeout_seconds") == 1, "the frozen case timeout changed")
    require(
        isinstance(trials.get("order_seed"), int) and trials["order_seed"] >= 0,
        "the public, reproducible trial-order seed is invalid",
    )
    require(
        trials.get("order_method") == "seeded-counterbalanced-rotating-latin-square",
        "the counterbalanced paired measurement order changed",
    )
    require(
        trials.get("minimum_candidates") == 3,
        "the final comparison must include three correctness-qualified candidates",
    )

    stats = document.get("statistics")
    require(isinstance(stats, dict), "the predeclared statistical rules are missing")
    require(stats.get("confidence") == 0.95, "the 95% confidence level changed")
    require(stats.get("overall_bootstrap_draws") == BOOTSTRAP_DRAWS, "the bootstrap count changed")
    require(
        stats.get("overall_method") == "stratified-paired-case-cluster-percentile-bootstrap",
        "the stratified paired bootstrap method changed",
    )
    require(
        stats.get("case_method") == "paired-log-student-t-df30",
        "the explicitly disclosed 31-round case confidence method changed",
    )
    require(
        stats.get("case_student_t_critical") == STUDENT_T_DF30_975,
        "the predeclared two-sided 95% case critical value changed",
    )
    require(stats.get("case_win_lower_bound") == 1.0, "the significant-win rule changed")
    require(
        stats.get("minimum_significant_wins") == MINIMUM_SIGNIFICANT_WINS
        and MINIMUM_SIGNIFICANT_WINS == (3 * CASE_COUNT + 4) // 5,
        "the exact 60% significant-win cutoff changed",
    )
    require(stats.get("overall_lower_bound") == 1.5, "the required 1.5x lower bound changed")
    require(
        stats.get("runtime_regression") == "candidate_time > 1.2 * baseline_time",
        "the strict more-than-20-percent runtime regression rule changed",
    )

    correctness = document.get("correctness")
    require(isinstance(correctness, dict), "the correctness gate is missing")
    require(correctness.get("snapshots_per_timed_row") == 3, "a correctness gate was removed")
    require(correctness.get("mismatches_allowed") == 0, "a correctness waiver was introduced")
    require(correctness.get("crashes_allowed") == 0, "a crash waiver was introduced")
    require(correctness.get("timeouts_allowed") == 0, "a timeout waiver was introduced")
    require(
        correctness.get("edge_checks") == 223_198 and correctness.get("edge_categories") == 49,
        "the canonical complete frozen compatibility denominator changed",
    )
    require(
        correctness.get("edge_runner_sha256")
        == "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca",
        "the canonical comprehensive compatibility-oracle source changed",
    )
    require(
        correctness.get("edge_answer_sha256")
        == "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526",
        "the canonical comprehensive CPython answer digest changed",
    )
    require(
        correctness.get("grammar_checks") == 20_480
        and correctness.get("object_checks") == 14_783
        and correctness.get("unicode_checks") == 4_494_555
        and correctness.get("observable_checks") == 479
        and correctness.get("native_binder_checks") == 34,
        "a separately frozen grammar, object, Unicode, observability, or safety denominator changed",
    )
    require(
        correctness.get("deep_public_checks") == DEEP_CONTRACT_CHECKS
        and correctness.get("deep_public_mismatches_allowed") == 0,
        "the separately frozen 393-case real-user public-contract gate was removed",
    )
    require(
        correctness.get("deep_contract_seed") == DEEP_CONTRACT_SEED
        and correctness.get("deep_contract_source_sha256") == DEEP_CONTRACT_SOURCE_SHA256
        and correctness.get("deep_contract_fixture_sha256") == DEEP_CONTRACT_FIXTURE_SHA256
        and correctness.get("deep_contract_reference_sha256") == DEEP_CONTRACT_REFERENCE_SHA256,
        "the independently frozen real-user contract source, seed, fixture, or Python answers changed",
    )
    require(
        correctness.get("deep_private_gc_rows") == DEEP_CONTRACT_PRIVATE_ROWS
        and correctness.get("deep_private_gc_policy") == "record-all-diagnostics-not-a-public-waiver",
        "private GC diagnostics were omitted or misrepresented as public behavior",
    )
    require(
        correctness.get("legacy_p0_cases") == 44_084
        and correctness.get("legacy_p0_obligations") == 51,
        "the separately preserved original full P0 obligations changed",
    )
    require(
        correctness.get("legacy_p0_fixture_sha256")
        == "782c41ff0b1239eeb0bb5312b4a893b41d7882c7fdcf64b29587518839e51669",
        "the separately preserved legacy P0 fixture identity changed",
    )
    require(
        correctness.get("named_private_waivers")
        == ["PRIVATE-CACHE-LAYOUT", "PRIVATE-DEBUG-TEXT"],
        "a public compatibility obligation was silently waived",
    )

    independence = document.get("independence")
    require(isinstance(independence, dict), "the from-scratch independence gate is missing")
    require(independence.get("external_regex_packages") == "forbidden", "external regex was permitted")
    require(independence.get("candidate_delegation") == "forbidden", "candidate delegation was permitted")
    require(
        independence.get("candidate_worker_python_regex") == "forbidden",
        "a candidate worker was allowed to load Python's regex engine",
    )
    require(
        independence.get("memory_instrumentation") == "separate-worker-tracemalloc-loads-re",
        "tracemalloc contamination of isolated timing was concealed",
    )
    require(
        independence.get("prior_holdout_access") == "forbidden",
        "older frozen performance cases were made readable by this protocol",
    )
    require(
        independence.get("required_owned_native_elf_artifacts") == 5,
        "the complete VM, Rust, and Zig owned-native provenance requirement changed",
    )

    memory = document.get("memory")
    require(isinstance(memory, dict), "the memory and boundary cohort is missing")
    require(memory.get("cases") == 768, "the separate memory cohort denominator changed")
    require(memory.get("per_cell") == 8, "the balanced memory cell denominator changed")
    require(memory.get("python_peak") == "tracemalloc-bytes-separate-worker", "Python memory was mislabelled")
    require(memory.get("process_peak") == "peak-rss-bytes", "whole-process peak memory is missing")
    require(memory.get("process_current") == "procfs-rss-bytes", "whole-process current memory is missing")
    require(memory.get("boundary_cost") == "included-in-end-to-end-timed-call", "FFI costs were subtracted")

    history = document.get("history")
    require(isinstance(history, dict), "the original published holdout status is missing")
    require(history.get("original_v7_cases") == 10_312, "the original published holdout denominator changed")
    require(
        history.get("original_engines") == "historically-published",
        "existing published original-engine holdout results were concealed",
    )
    require(
        history.get("corrected_rust_original_holdout") == "NOT MEASURED",
        "corrected Rust was falsely claimed to have run on the original holdout",
    )
    require(
        history.get("v8_expansion") == "NOT MEASURED"
        and history.get("combined_result") == "NOT MEASURED",
        "the prospective final expansion or combined result was measured early",
    )
    require(
        trials.get("four_engine_timed_rows") == CASE_COUNT * PAIRED_ROUNDS * 4,
        "the frozen four-engine raw timing denominator changed",
    )
    require(
        trials.get("four_engine_correctness_snapshots") == CASE_COUNT * PAIRED_ROUNDS * 4 * 3,
        "the frozen four-engine three-snapshot correctness denominator changed",
    )
    require(
        isinstance(stats.get("bootstrap_seed"), int) and stats["bootstrap_seed"] >= 0,
        "the reproducible stratified bootstrap seed changed",
    )

    require(
        is_hex_digest(document.get("binding_sha256"))
        and hmac.compare_digest(document["binding_sha256"], manifest_binding(document)),
        "the source, seed commitment, case layout, controls, or stopping rule changed",
    )


def case_descriptors() -> list[dict[str, Any]]:
    """Public identifiers and factorial labels only; never materialize inputs."""
    descriptors: list[dict[str, Any]] = []
    for api in API_FAMILIES:
        for workload in WORKLOAD_FAMILIES:
            for index in range(CASES_PER_CELL):
                descriptor: dict[str, Any] = {
                    "schema": CASE_SCHEMA,
                    "id": f"v8.{api}.{workload}.{index:03d}",
                    "api": api,
                    "workload": workload,
                    "index": index,
                }
                if api in NORMAL_APIS:
                    descriptor.update(
                        {
                            "surface": ("module", "compiled")[index & 1],
                            "input": ("str", "bytes")[(index >> 1) & 1],
                            "outcome": ("hit", "miss")[(index >> 2) & 1],
                            "variant": index >> 3,
                        }
                    )
                elif api == "compile":
                    descriptor.update(
                        {
                            "surface": "module",
                            "input": ("str", "bytes")[(index >> 1) & 1],
                            "lifecycle": ("cold-cache", "warm-cache")[index & 1],
                            "variant": index >> 2,
                        }
                    )
                elif api == "escape":
                    descriptor.update(
                        {
                            "surface": "module",
                            "input": ("str", "bytes")[(index >> 1) & 1],
                            "special_density": ("ordinary", "regex-special")[index & 1],
                            "variant": index >> 2,
                        }
                    )
                elif api == "match-surface":
                    descriptor.update(
                        {
                            "surface": ("module", "compiled")[index & 1],
                            "input": ("str", "bytes")[(index >> 1) & 1],
                            "outcome": "hit",
                            "capture": ("numbered", "named", "optional", "multiple")[(index >> 2) & 3],
                            "variant": index >> 4,
                        }
                    )
                else:
                    descriptor.update(
                        {
                            "surface": "compiled-pattern-scanner",
                            "input": ("str", "bytes")[(index >> 1) & 1],
                            "scanner_method": ("search", "match")[index & 1],
                            "progression": ("ordinary", "zero-width")[(index >> 2) & 1],
                            "variant": index >> 3,
                        }
                    )
                descriptors.append(descriptor)
    return descriptors


def validate_descriptors(descriptors: list[dict[str, Any]]) -> None:
    require(len(descriptors) == CASE_COUNT, "expanded holdout case count is not 12,288")
    ids = [descriptor.get("id") for descriptor in descriptors]
    require(len(set(ids)) == CASE_COUNT, "expanded holdout case identifiers are not unique")
    cells: collections.Counter[tuple[str, str]] = collections.Counter()
    api_totals: collections.Counter[str] = collections.Counter()
    normal_factors: collections.Counter[tuple[str, str, str, str, str]] = collections.Counter()
    for descriptor in descriptors:
        require(descriptor.get("schema") == CASE_SCHEMA, "an expanded case schema changed")
        api = descriptor.get("api")
        workload = descriptor.get("workload")
        require(api in API_FAMILIES and workload in WORKLOAD_FAMILIES, "an expanded stratum changed")
        require(isinstance(descriptor.get("index"), int), "a case index is invalid")
        require(0 <= descriptor["index"] < CASES_PER_CELL, "a case index escaped its frozen cell")
        cells[(api, workload)] += 1
        api_totals[api] += 1
        if api in NORMAL_APIS:
            factor = (
                api,
                workload,
                descriptor.get("surface"),
                descriptor.get("input"),
                descriptor.get("outcome"),
            )
            normal_factors[factor] += 1
    require(len(cells) == 96, "a complete API/workload stratum is missing")
    require(set(cells.values()) == {CASES_PER_CELL}, "API/workload cells are not equally weighted")
    require(set(api_totals.values()) == {CASES_PER_API}, "the 12 API families are not equally weighted")
    require(
        len(normal_factors) == len(NORMAL_APIS) * len(WORKLOAD_FAMILIES) * 8
        and set(normal_factors.values()) == {16},
        "genuine module/compiled, text/bytes, hit/miss cells are unbalanced",
    )


def counterbalanced_order(
    modules: tuple[str, ...], case_id: str, round_index: int, order_seed: int
) -> tuple[str, ...]:
    require(len(modules) >= 2 and modules[0] == "re", "the pinned Python baseline is missing")
    require(len(set(modules)) == len(modules), "a paired engine is duplicated")
    require(0 <= round_index < PAIRED_ROUNDS, "a paired round is outside the frozen protocol")
    payload = f"rebar-v8-order:{order_seed}:{case_id}".encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    shuffled = list(modules)
    random.Random(int.from_bytes(digest[:16], "big")).shuffle(shuffled)
    start = (int.from_bytes(digest[16:24], "big") + round_index) % len(shuffled)
    return tuple(shuffled[start:] + shuffled[:start])


def case_confidence(log_ratios: list[float]) -> tuple[float, float]:
    require(len(log_ratios) == PAIRED_ROUNDS, "a case does not contain all 31 paired rounds")
    require(all(math.isfinite(value) for value in log_ratios), "a paired log ratio is not finite")
    mean = statistics.fmean(log_ratios)
    deviation = statistics.stdev(log_ratios)
    half_width = STUDENT_T_DF30_975 * deviation / math.sqrt(PAIRED_ROUNDS)
    lower = math.exp(mean - half_width)
    upper = math.exp(mean + half_width)
    require(math.isfinite(lower) and math.isfinite(upper), "a case confidence interval is not finite")
    return lower, upper


def percentile(values: list[float], quantile: float) -> float:
    require(bool(values), "an empty confidence interval cannot be calculated")
    require(0.0 <= quantile <= 1.0, "a bootstrap quantile is invalid")
    ordered = sorted(values)
    location = (len(ordered) - 1) * quantile
    left = math.floor(location)
    right = math.ceil(location)
    fraction = location - left
    return ordered[left] * (1.0 - fraction) + ordered[right] * fraction


def bootstrap_case_clusters(
    ordered_cells: list[list[float]], *, seed: int, draws: int, cases_per_cell: int
) -> tuple[float, float]:
    """Resample intact paired case means, retaining exact frozen cell weights."""
    require(bool(ordered_cells), "a paired bootstrap has no case strata")
    require(isinstance(draws, int) and draws > 0, "a paired bootstrap draw count is invalid")
    require(isinstance(cases_per_cell, int) and cases_per_cell > 0, "a paired bootstrap cell size is invalid")
    require(all(len(values) == cases_per_cell for values in ordered_cells), "a paired bootstrap cell is unbalanced")
    require(
        all(math.isfinite(value) for values in ordered_cells for value in values),
        "a paired bootstrap case log is not finite",
    )
    generator = random.Random(seed)
    denominator = len(ordered_cells) * cases_per_cell
    samples: list[float] = []
    for _ in range(draws):
        total = 0.0
        for values in ordered_cells:
            total += sum(values[generator.randrange(cases_per_cell)] for _ in range(cases_per_cell))
        speedup = math.exp(total / denominator)
        require(math.isfinite(speedup), "a paired bootstrap speedup is not finite")
        samples.append(speedup)
    return percentile(samples, 0.025), percentile(samples, 0.975)


def stratified_bootstrap(
    case_logs: dict[tuple[str, str], list[float]], *, seed: int, draws: int
) -> tuple[float, float]:
    """Run all 9,999 prespecified whole-case, stratified paired draws."""
    require(draws >= BOOTSTRAP_DRAWS, "the predeclared bootstrap count was reduced")
    expected = {(api, family) for api in API_FAMILIES for family in WORKLOAD_FAMILIES}
    require(set(case_logs) == expected, "a paired bootstrap stratum was omitted")
    cells = [case_logs[(api, family)] for api in API_FAMILIES for family in WORKLOAD_FAMILIES]
    return bootstrap_case_clusters(cells, seed=seed, draws=draws, cases_per_cell=CASES_PER_CELL)


def is_significant_win(lower_confidence: float) -> bool:
    require(math.isfinite(lower_confidence) and lower_confidence > 0, "an invalid case confidence bound")
    return lower_confidence > 1.0


def is_runtime_regression(speedup: float) -> bool:
    require(math.isfinite(speedup) and speedup > 0.0, "an invalid runtime speedup")
    return speedup < RUNTIME_REGRESSION_THRESHOLD


def validate_modules(modules: tuple[str, ...], minimum_candidates: int = 3) -> None:
    require(bool(modules) and modules[0] == "re", "Python re is not the actual first baseline")
    require(len(set(modules)) == len(modules), "duplicate baseline or candidate module")
    require(len(modules) - 1 >= minimum_candidates, "three complete independent candidates are required")
    for module in modules[1:]:
        require(
            isinstance(module, str)
            and module.startswith("candidates.")
            and module.count(".") == 1,
            "a measured candidate is outside the frozen production package",
        )
        require(module.rsplit(".", 1)[-1] not in BANNED_ENGINE_MODULES, "external regex was selected")


def validate_candidate_python(path: Path) -> dict[str, Any]:
    root = (ROOT / "candidates").resolve()
    resolved = path.resolve()
    require(resolved.is_file() and resolved.is_relative_to(root), "candidate source escaped production")
    try:
        source = resolved.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(resolved))
    except (OSError, UnicodeError, SyntaxError) as error:
        raise ProtocolError("candidate Python source cannot be audited") from error
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module] if node.module else []
        else:
            continue
        for name in names:
            require(
                isinstance(name, str) and name.split(".", 1)[0] not in BANNED_ENGINE_MODULES,
                f"candidate imports a prohibited external or built-in regex engine: {name}",
            )
    return {"path": str(resolved.relative_to(ROOT)), "sha256": file_digest(resolved)}


def checked_evidence_path(path: Path, label: str, *, must_exist: bool) -> Path:
    root = (ROOT / "performance/v8/evidence").resolve()
    resolved = path.resolve()
    require(resolved.parent == root, f"{label} escaped expanded final evidence")
    if must_exist:
        require(resolved.is_file(), f"{label} does not exist")
    else:
        require(not resolved.exists(), f"refusing to overwrite {label}")
    return resolved


def read_json_document(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        if path.suffix == ".gz":
            with gzip.open(path, "rb") as stream:
                payload = stream.read()
        else:
            with path.open("rb") as stream:
                payload = stream.read()
        document = json.loads(payload)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ProtocolError(f"cannot read {label}") from error
    require(isinstance(document, dict), f"{label} is not a JSON object")
    return document, payload


def required_artifact_roles(module: str) -> frozenset[str]:
    mapping = {
        "candidates.rust_candidate": frozenset(
            {"public-python", "native-source", "bridge-source", "native-bridge", "native-engine"}
        ),
        "candidates.zig_candidate": frozenset({"public-python", "native-bridge", "native-engine"}),
        "candidates.vm_candidate": frozenset({"public-python", "native-bridge"}),
        "candidates.ast_candidate": frozenset({"public-python"}),
    }
    require(module in mapping, "candidate does not have an independently specified native identity")
    return mapping[module]


def verify_edge_qualifications(
    modules: tuple[str, ...], paths: list[Path]
) -> dict[str, dict[str, Any]]:
    require(len(paths) == len(modules) - 1, "every final candidate needs a frozen edge proof")
    candidates_root = (ROOT / "candidates").resolve()
    evidence_root = (candidates_root / "evidence").resolve()
    expected = set(modules[1:])
    proofs: dict[str, dict[str, Any]] = {}
    for given in paths:
        path = given.resolve()
        require(path.is_file() and path.is_relative_to(evidence_root), "candidate proof escaped correctness evidence")
        report, payload = read_json_document(path, "frozen candidate correctness proof")
        module = report.get("module")
        require(module in expected and module not in proofs, "candidate correctness proof is missing or duplicated")
        require(report.get("schema") == EDGE_SCHEMA, "candidate edge-proof schema changed")
        require(report.get("python") == "3.14.6", "candidate proof changed pinned CPython")
        require(report.get("unicode") == "16.0.0", "candidate proof changed pinned Unicode")
        require(report.get("locale") == "C", "candidate proof changed the frozen locale")
        require(report.get("failed") == 0, "candidate failed the comprehensive edge oracle")
        require(report.get("correctness_checks") == 223_198, "candidate edge-proof denominator changed")
        categories = report.get("categories")
        require(
            isinstance(categories, dict)
            and len(categories) == 49
            and all(isinstance(count, int) for count in categories.values())
            and sum(categories.values()) == 223_198,
            "candidate dropped an unchanged frozen correctness category",
        )
        require(
            report.get("expected_sha256")
            == report.get("actual_sha256")
            == "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526",
            "candidate does not exactly reproduce the frozen CPython oracle",
        )
        require(report.get("performance") == "NOT MEASURED", "performance leaked into a correctness proof")
        require(report.get("holdout") == "NOT ACCESSED", "hidden performance leaked into a correctness proof")
        artifacts = report.get("candidate_artifacts")
        require(isinstance(artifacts, list), "candidate native identities are missing")
        verified: dict[str, dict[str, str]] = {}
        for artifact in artifacts:
            require(isinstance(artifact, dict), "candidate native identity is invalid")
            require(set(artifact) == {"role", "path", "sha256"}, "candidate native identity fields changed")
            role = artifact.get("role")
            require(role in required_artifact_roles(module), "candidate native identity role is wrong")
            require(role not in verified, "candidate native identity role is duplicated")
            location = artifact.get("path")
            require(isinstance(location, str), "candidate native identity has no path")
            item = Path(location)
            resolved = item.resolve() if item.is_absolute() else (ROOT / item).resolve()
            require(resolved.is_file() and resolved.is_relative_to(candidates_root), "candidate artifact escaped production")
            require(is_hex_digest(artifact.get("sha256")), "candidate artifact digest is invalid")
            require(
                hmac.compare_digest(file_digest(resolved), artifact["sha256"]),
                "candidate source or native binary changed after its frozen correctness gate",
            )
            if role == "public-python":
                source = candidates_root / f"{module.rsplit('.', 1)[-1]}.py"
                require(resolved == source.resolve(), "candidate public source belongs to another engine")
                validate_candidate_python(resolved)
            verified[role] = {"path": str(resolved), "sha256": artifact["sha256"]}
        require(set(verified) == required_artifact_roles(module), "a required candidate native artifact is missing")
        proofs[module] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "artifacts": verified,
        }
    require(set(proofs) == expected, "the three final candidates do not all pass the same edge oracle")
    return proofs


def verify_current_campaigns(
    modules: tuple[str, ...], paths: list[Path]
) -> dict[str, dict[str, str]]:
    require(len(paths) == len(modules) - 1, "every final candidate needs a current complete compatibility campaign")
    evidence_root = (ROOT / "candidates/evidence").resolve()
    expected = set(modules[1:])
    verified: dict[str, dict[str, str]] = {}
    required_steps = frozenset(
        {
            "from-scratch-static-audit",
            "frozen-correctness-v2",
            "frozen-correctness-v3",
            "official-cpython-tests",
            "upstream-public-surface",
            "replacement-and-callback-adversarial",
            "deep-replacement-and-callback-adversarial",
            "isolated-crash-and-resource-safety",
            "isolated-depth-and-overflow-safety",
            "full-unicode-plane",
        }
    )
    required_exclusions = frozenset(
        {
            "frozen-performance-correctness-v6",
            "frozen-performance-v7-integrity",
            "frozen-performance-correctness-v7",
        }
    )
    for given in paths:
        path = given.resolve()
        require(path.is_file() and path.is_relative_to(evidence_root), "campaign proof escaped candidate evidence")
        report, payload = read_json_document(path, "complete candidate compatibility campaign")
        module = report.get("candidate")
        require(module in expected and module not in verified, "a complete candidate campaign is missing or duplicated")
        require(report.get("schema") == "rebar-rust-campaign-gate-v1", "current candidate campaign schema changed")
        require(report.get("pinned_cpython") == "3.14.6", "candidate campaign changed the pinned oracle")
        require(report.get("mode") == "sealed-practice-only", "candidate campaign can read frozen performance inputs")
        require(report.get("passed") is True, "candidate contains unresolved compatibility or safety failures")
        require(report.get("holdout_accessed") is False, "candidate campaign accessed a performance holdout")
        require(report.get("performance") == "NOT MEASURED", "candidate campaign contains performance measurements")
        require(report.get("timing_performed") is False, "candidate campaign executed performance timing")
        goal = report.get("goal")
        require(
            isinstance(goal, dict)
            and goal.get("passed") is True
            and goal.get("actual_sha256")
            == goal.get("expected_sha256")
            == "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
            "candidate campaign changed the immutable project objective",
        )
        steps = report.get("steps")
        require(isinstance(steps, list) and len(steps) >= 18, "candidate dropped a complete campaign step")
        require(
            all(isinstance(step, dict) and step.get("passed") is True for step in steps),
            "candidate has an unexplained public, safety, or no-delegation failure",
        )
        names = {step.get("name") for step in steps}
        require(required_steps <= names, "candidate omitted a required standalone compatibility or safety suite")
        plane = next(step for step in steps if step.get("name") == "full-unicode-plane")
        require(plane.get("expected_checks") == 4_494_555, "candidate did not preserve full Unicode coverage")
        exclusions = report.get("excluded_steps")
        require(
            isinstance(exclusions, list)
            and {item.get("name") for item in exclusions if isinstance(item, dict)} == required_exclusions,
            "candidate campaign did not exclude every original performance-reading step",
        )
        verified[module] = {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(payload).hexdigest()}
    require(set(verified) == expected, "three candidates do not pass the current full correctness campaign")
    return verified


def require_deep_public_outcome(checks: int, mismatches: int, private_rows: int) -> None:
    require(checks == DEEP_CONTRACT_CHECKS, "deep real-user public denominator changed")
    require(mismatches == 0, "candidate has an unwaived real-user public mismatch")
    require(private_rows == DEEP_CONTRACT_PRIVATE_ROWS, "private real-user diagnostics were omitted")


def verify_deep_contracts(
    modules: tuple[str, ...], paths: list[Path], edges: dict[str, dict[str, Any]]
) -> dict[str, dict[str, str]]:
    require(len(paths) == len(modules) - 1, "every final candidate needs the 393-case real-user proof")
    candidates_root = (ROOT / "candidates").resolve()
    expected = set(modules[1:])
    verified: dict[str, dict[str, str]] = {}
    suite = ROOT / "tools/rust_v8_deep_contract_oracle.py"
    require(
        suite.is_file()
        and hmac.compare_digest(file_digest(suite), DEEP_CONTRACT_SOURCE_SHA256),
        "the immutable 393-case real-user contract runner changed",
    )
    for given in paths:
        path = given.resolve()
        require(path.is_file() and path.is_relative_to(candidates_root), "deep public proof escaped candidate evidence")
        report, payload = read_json_document(path, "393-case real-user contract proof")
        require(report.get("schema") == DEEP_CONTRACT_SCHEMA, "deep public contract schema changed")
        require(report.get("status") == "PASS", "candidate fails the frozen real-user public contract")
        require(report.get("python") == "3.14.6", "deep public contract changed pinned Python")
        require(report.get("seed") == DEEP_CONTRACT_SEED, "deep public contract seed changed")
        require(report.get("seeded_case_count") == DEEP_CONTRACT_PRIVATE_ROWS, "deep public contract seeded count changed")
        require(report.get("checks") == DEEP_CONTRACT_CHECKS, "deep public contract dropped a public case")
        require(report.get("fixture_sha256") == DEEP_CONTRACT_FIXTURE_SHA256, "deep public fixture changed")
        require(report.get("suite_path") == "tools/rust_v8_deep_contract_oracle.py", "deep public suite path changed")
        require(report.get("suite_sha256") == DEEP_CONTRACT_SOURCE_SHA256, "deep public suite source hash changed")
        require(
            report.get("reference_a_sha256")
            == report.get("reference_b_sha256")
            == DEEP_CONTRACT_REFERENCE_SHA256,
            "independent pinned Python real-user references disagree",
        )
        require(report.get("candidate_sha256") == DEEP_CONTRACT_REFERENCE_SHA256, "candidate does not reproduce all real-user observations")
        require_deep_public_outcome(
            report.get("checks"),
            report.get("public_mismatch_count"),
            report.get("seeded_case_count"),
        )
        require(report.get("public_mismatches") == [], "candidate concealed real-user public failures")
        require(report.get("public_mismatch_family_counts") == {}, "candidate concealed a public failure category")
        require(
            report.get("stdlib_vs_stdlib_mismatches") in ([], 0),
            "real-user Python self-oracles contain unexplained failures",
        )
        require(
            report.get("implementation_private_gc_topology_policy")
            == "fully recorded and separately compared; explicitly not represented as documented public lifetime or collectability equality",
            "private object topology was misrepresented as a public waiver",
        )
        for key in ("reference", "reference_independent_repeat", "candidate"):
            record = report.get(key)
            require(isinstance(record, dict), "deep public contract omitted full reference or candidate evidence")
            diagnostics = record.get("implementation_private_gc_diagnostics")
            require(
                isinstance(diagnostics, list) and len(diagnostics) == DEEP_CONTRACT_PRIVATE_ROWS,
                "deep contract omitted one of the 64 separately recorded private diagnostics",
            )
        differences = report.get("implementation_private_gc_topology_differences")
        difference_count = report.get("implementation_private_gc_topology_difference_count")
        require(
            isinstance(differences, list)
            and isinstance(difference_count, int)
            and len(differences) == difference_count
            and 0 <= difference_count <= DEEP_CONTRACT_PRIVATE_ROWS,
            "private topology differences were omitted, miscounted, or added to public errors",
        )
        require(report.get("forbidden_regex_guards", 0) >= 13, "deep contract removed a native no-delegation guard")
        require(report.get("performance") == "NOT MEASURED", "deep public contract executed timing")
        require(report.get("holdout") == "NOT ACCESSED", "deep public contract opened performance fixtures")
        artifacts = report.get("native_artifacts")
        require(isinstance(artifacts, list), "deep public contract omitted actual native provenance")
        public = [item for item in artifacts if isinstance(item, dict) and item.get("role") == "public-python"]
        require(len(public) == 1 and is_hex_digest(public[0].get("sha256")), "deep public contract omitted candidate source")
        matches = [name for name in expected if edges[name]["artifacts"]["public-python"]["sha256"] == public[0]["sha256"]]
        require(len(matches) == 1, "deep public proof does not belong to exactly one frozen candidate")
        module = matches[0]
        require(module not in verified, "a candidate deep public proof was reused")
        observed_roles = {item.get("role"): item for item in artifacts if isinstance(item, dict)}
        for role, expected_artifact in edges[module]["artifacts"].items():
            require(role in observed_roles, "deep public contract omitted a correctness-qualified artifact")
            require(
                observed_roles[role].get("sha256") == expected_artifact["sha256"],
                "deep public contract used a stale candidate native artifact",
            )
        verified[module] = {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(payload).hexdigest()}
    require(set(verified) == expected, "at least one final candidate fails the frozen real-user public contract")
    return verified


def verify_from_scratch_audit(
    given: Path, modules: tuple[str, ...]
) -> dict[str, Any]:
    expected_path = (ROOT / "candidates/audits/FROM-SCRATCH-AUDIT.json").resolve()
    path = given.resolve()
    require(path == expected_path and path.is_file(), "the committed all-engine from-scratch audit is missing")
    report, payload = read_json_document(path, "all-engine native from-scratch audit")
    require(report.get("schema_version") == 1, "all-engine from-scratch schema changed")
    require(report.get("audit") == "bounded-from-scratch-engine-provenance", "all-engine from-scratch audit changed")
    require(report.get("passed") is True and report.get("result") == "PASS", "an engine delegates or uses an external regex package")
    require(report.get("minimum_required_independent_families") == 3, "fewer than three independent matching families were allowed")
    require(report.get("verified_core_family_count", 0) >= 3, "three distinct engine families were not verified")
    require(report.get("verified_distinct_pipeline_count", 0) >= 3, "candidate semantic engines are not genuinely independent")
    provenance = report.get("runtime_native_mapping_provenance")
    require(isinstance(provenance, dict) and provenance.get("passed") is True, "actual native mappings were not verified")
    mappings = provenance.get("families")
    require(isinstance(mappings, dict), "actual per-engine native mappings are missing")
    owned = 0
    observed = 0
    for family in ("vm", "rust", "zig"):
        item = mappings.get(family)
        require(isinstance(item, dict) and item.get("passed") is True, "a VM, Rust, or Zig native mapping failed")
        count = item.get("expected_owned_mapping_count")
        actual = item.get("observed_owned_mapping_count")
        require(isinstance(count, int) and isinstance(actual, int) and count == actual and count > 0, "an owned native artifact is missing or substituted")
        owned += count
        observed += actual
    require(owned == observed == 5, "all five exact VM, Rust, and Zig native ELF mappings are required")
    families = report.get("families")
    require(isinstance(families, dict), "the all-engine candidate audit is missing")
    for module in modules[1:]:
        suffix = module.rsplit(".", 1)[-1]
        family = {"rust_candidate": "rust", "zig_candidate": "zig", "vm_candidate": "vm", "ast_candidate": "ast"}.get(suffix)
        require(family is not None and isinstance(families.get(family), dict), "candidate has no from-scratch family audit")
        require(families[family].get("passed") is True, "candidate fails its independent no-delegation audit")
    scope = report.get("scope")
    require(isinstance(scope, dict), "all-engine audit scope was removed")
    require(scope.get("holdout_or_case_fixture_access") is False, "from-scratch audit accessed performance fixtures")
    require(scope.get("benchmark_or_timing_executed") is False, "from-scratch audit performed timing")
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(payload).hexdigest(), "owned_native_elf_artifacts": owned}


def verify_candidate_freeze(
    path: Path,
    document: dict[str, Any],
    modules: tuple[str, ...],
    edges: dict[str, dict[str, Any]],
    campaigns: dict[str, dict[str, str]],
    contracts: dict[str, dict[str, str]],
    scratch_audit: dict[str, Any],
) -> dict[str, Any]:
    resolved = checked_evidence_path(path, "candidate and stopping freeze", must_exist=True)
    freeze, payload = read_json_document(resolved, "candidate and stopping freeze")
    require(freeze.get("schema") == CANDIDATE_FREEZE_SCHEMA, "candidate stopping-freeze schema changed")
    require(
        freeze.get("protocol_binding_sha256") == document["binding_sha256"],
        "candidate selection was not sealed against this exact protocol",
    )
    require(
        freeze.get("from_scratch_audit_sha256") == scratch_audit["sha256"],
        "the frozen five-native-artifact no-delegation audit changed",
    )
    stopping = freeze.get("stopping_commit")
    require(
        isinstance(stopping, str)
        and len(stopping) in (40, 64)
        and all(character in "0123456789abcdef" for character in stopping),
        "candidate optimization has no frozen stopping commit",
    )
    entries = freeze.get("candidates")
    require(isinstance(entries, list) and len(entries) == len(modules) - 1, "candidate stopping manifest is incomplete")
    by_module: dict[str, dict[str, Any]] = {}
    for item in entries:
        require(isinstance(item, dict), "a frozen candidate entry is invalid")
        module = item.get("module")
        require(module in modules[1:] and module not in by_module, "a frozen candidate is missing or duplicated")
        require(item.get("edge_sha256") == edges[module]["sha256"], "frozen candidate edge proof changed")
        require(item.get("campaign_sha256") == campaigns[module]["sha256"], "frozen complete compatibility campaign changed")
        require(item.get("deep_contract_sha256") == contracts[module]["sha256"], "frozen 393-case real-user proof changed")
        require(item.get("artifacts") == edges[module]["artifacts"], "frozen candidate native artifacts changed")
        by_module[module] = item
    require(set(by_module) == set(modules[1:]), "candidate freeze omitted a measured engine")
    return {"document": freeze, "sha256": hashlib.sha256(payload).hexdigest(), "path": str(resolved.relative_to(ROOT))}


def encode_wire_subject(subject: str | bytes, source_kind: str) -> str | bytes | dict[str, str]:
    if source_kind in ("bytearray", "memoryview"):
        require(isinstance(subject, bytes), "a mutable byte case has no original byte payload")
        return {"schema": BUFFER_WIRE_SCHEMA, "kind": source_kind, "hex": subject.hex()}
    if source_kind == "bytes":
        require(isinstance(subject, bytes), "a bytes case does not contain bytes")
        return subject
    require(source_kind == "str" and isinstance(subject, str), "a text case does not contain text")
    return subject


def decode_wire_subject(
    subject: str | bytes | dict[str, str], source_kind: str
) -> str | bytes | bytearray | memoryview:
    if source_kind in ("bytearray", "memoryview"):
        require(isinstance(subject, dict), "a mutable byte case has no wire representation")
        require(set(subject) == {"schema", "kind", "hex"}, "mutable byte wire fields changed")
        require(
            subject.get("schema") == BUFFER_WIRE_SCHEMA and subject.get("kind") == source_kind,
            "mutable byte wire schema or subject kind changed",
        )
        encoded = subject.get("hex")
        require(isinstance(encoded, str), "mutable byte wire payload is invalid")
        try:
            raw = bytes.fromhex(encoded)
        except ValueError as error:
            raise ProtocolError("mutable byte wire payload is corrupt") from error
        return bytearray(raw) if source_kind == "bytearray" else memoryview(raw)
    require(source_kind in {"str", "bytes"}, "an unsupported subject source was declared")
    expected = str if source_kind == "str" else bytes
    require(isinstance(subject, expected), "declared and materialized subject types differ")
    return subject


def materialize_case(
    descriptor: dict[str, Any], opening: bytes, *, synthetic: bool = False
) -> dict[str, Any]:
    """Derive one real case after unsealing, or a domain-isolated synthetic."""
    require(isinstance(opening, bytes) and len(opening) == 32, "invalid opened final-case seed")
    require(descriptor.get("schema") == CASE_SCHEMA, "unfrozen final case descriptor")
    identifier_text = descriptor.get("id")
    require(isinstance(identifier_text, str), "a generated case has no stable public identity")
    if synthetic:
        require(identifier_text.startswith("synthetic.v8."), "synthetic controls cannot use a genuine holdout identity")
        require(hmac.compare_digest(opening, SYNTHETIC_CASE_OPENING), "synthetic controls cannot use the blinded opening")
        domain = b"rebar-v8-synthetic-structure-only\x00"
    else:
        require(identifier_text.startswith("v8."), "a final case does not belong to the frozen holdout")
        domain = b"rebar-v8-performance-case\x00"
    identifier = identifier_text.encode("utf-8")
    derived = hmac.new(opening, domain + identifier, hashlib.sha256).digest()
    suffix = derived.hex()[:8]
    api = descriptor["api"]
    family = descriptor["workload"]
    variant = descriptor["variant"]
    index = descriptor.get("index")
    require(api in API_FAMILIES, "a generated case has an unknown public API")
    require(family in WORKLOAD_FAMILIES, "a generated case has an unknown workload family")
    require(isinstance(index, int) and 0 <= index < CASES_PER_CELL, "a generated case index escaped its frozen cell")
    require(isinstance(variant, int) and variant >= 0, "a generated case variant is invalid")
    marker = (
        f"x{API_FAMILIES.index(api):02x}{WORKLOAD_FAMILIES.index(family):02x}"
        f"{index:03x}{derived.hex()[:24]}"
    )
    if family == "literal-and-long-prefix":
        pattern = "token" + suffix
        hit, miss = pattern, "absent" + suffix
    elif family == "character-class-and-unicode":
        if descriptor.get("input") == "str" and variant % 3 == 0:
            pattern, hit, miss = r"(?u)\w{2,12}", "Straße42", "!?"
        else:
            pattern, hit, miss = r"[A-Za-z]{2,8}[0-9]{1,3}", "Ab42", "!?"
    elif family == "anchors-boundaries-and-windows":
        pattern, hit, miss = r"\A[A-Za-z]{2}[0-9]{2}\Z", "Az42", "!?"
    elif family == "greedy-lazy-atomic-and-possessive":
        patterns = (r"(?:ab){1,3}", r"(?:ab){1,3}?", r"(?>ab){1,3}", r"(?:ab){1,3}+")
        pattern, hit, miss = patterns[variant % len(patterns)], "abab", "zz"
    elif family == "alternation-groups-and-backreferences":
        pattern = r"(?P<lead>[A-Za-z]{2})(?P<num>[0-9]{2})(?:-(?P=lead))?"
        hit, miss = "az42-az", "!?"
    elif family == "lookaround-and-zero-width":
        if api in ("search", "findall", "finditer", "split", "sub", "subn", "scanner") and variant % 2:
            pattern, hit, miss = r"(?<=:)[A-Za-z]{2}(?=;)", ":az;", ":44;"
        else:
            pattern, hit, miss = r"(?=[A-Za-z]{2}[0-9]{2})([A-Za-z]{2}[0-9]{2})", "az42", "!?"
    elif family == "replacement-split-and-result-density":
        pattern, hit, miss = r"(?P<word>[A-Za-z]{2,8})", "alpha", "12345"
    else:
        pattern = r"(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>[0-9]+)"
        hit, miss = "level=200", "!?"

    subject = hit if descriptor.get("outcome", "hit") == "hit" else miss
    if api == "escape":
        if descriptor["special_density"] == "regex-special":
            subject = "[a-z]+.(item)?{" + marker + "}"
        else:
            subject = "ordinary_identifier_" + marker
    if api == "match-surface":
        pattern = r"(?P<first>[A-Za-z]+)(?P<number>[0-9]+)(?P<optional>[A-Z]+)?"
        subject = "item42"
    if api == "scanner" and descriptor["progression"] == "zero-width":
        pattern, subject = r"(?=[A-Za-z])", "abc"
    if api != "escape":
        pattern = f"{pattern}(?#{marker})"
    is_bytes = descriptor.get("input") == "bytes"
    if is_bytes:
        pattern = pattern.encode("ascii")
        subject = subject.encode("ascii")
    callback = api in ("sub", "subn") and bool(variant & 1)
    replacement: str | bytes = b"<\\g<0>>" if is_bytes else r"<\g<0>>"
    flags = (2 if variant & 4 else 0) | (8 if variant & 8 else 0)
    case = {
        **descriptor,
        "pattern": pattern,
        "subject": subject,
        "flags": flags,
        "replacement": replacement,
        "callback": callback,
        "count": variant % 3,
        "maxsplit": variant % 3,
        "source_kind": (
            ("bytes", "bytearray", "memoryview")[variant % 3]
            if is_bytes and api not in ("compile", "escape")
            else ("bytes" if is_bytes else "str")
        ),
    }
    if (
        api in ("search", "match", "fullmatch", "findall", "finditer")
        and descriptor.get("surface") == "compiled"
        and family != "anchors-boundaries-and-windows"
        and variant & 2
    ):
        prefix = b"!" if is_bytes else "!"
        suffix_text = b"?" if is_bytes else "?"
        case["subject"] = prefix + case["subject"] + suffix_text
        case["window"] = (len(prefix), len(prefix) + len(subject))
    case["subject"] = encode_wire_subject(case["subject"], case["source_kind"])
    require(len(subject) <= 8192, "generated final case exceeds its frozen subject bound")
    return case


class IsolatedWorker:
    """Persistent worker whose candidate timing process never loads `re`."""

    def __init__(self, module: str, kind: str, timeout: float = 1.0) -> None:
        require(kind in {"timing", "memory"}, "unknown isolated-worker kind")
        self.module = module
        self.kind = kind
        self.timeout = timeout
        environment = dict(os.environ)
        environment.pop("PYTHONPATH", None)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        startup_start = time.perf_counter_ns()
        self.process = subprocess.Popen(
            [sys.executable, "-I", "-S", "-B", "-c", ISOLATED_WORKER, str(ROOT), module, kind],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=environment,
        )
        self.ready = self.receive(max(timeout, 10.0))
        self.startup_elapsed_ns = time.perf_counter_ns() - startup_start
        require(self.startup_elapsed_ns > 0, "isolated cold-process startup is not measurable")
        require(self.ready.get("kind") == "ready", "isolated candidate worker failed to start")
        require(self.ready.get("module") == module and self.ready.get("worker") == kind, "isolated worker identity was swapped")
        if module != "re" and kind == "timing":
            require(self.ready.get("startup_forbidden") == [], "candidate worker loaded Python or external regex")

    def _read_exact(self, count: int, timeout: float) -> bytes:
        require(self.process.stdout is not None, "isolated worker has no response pipe")
        result = bytearray()
        while len(result) < count:
            ready, _, _ = select.select([self.process.stdout], [], [], timeout)
            require(bool(ready), "isolated final candidate timed out")
            chunk = os.read(self.process.stdout.fileno(), count - len(result))
            require(bool(chunk), "isolated final candidate crashed or closed its response")
            result.extend(chunk)
        return bytes(result)

    def receive(self, timeout: float | None = None) -> dict[str, Any]:
        import marshal

        limit = self.timeout if timeout is None else timeout
        header = self._read_exact(8, limit)
        length = int.from_bytes(header, "big")
        require(0 < length <= 4 * 1024 * 1024, "isolated final worker returned an invalid frame")
        response = marshal.loads(self._read_exact(length, limit))
        require(isinstance(response, dict), "isolated final worker returned an invalid response")
        require(response.get("kind") != "error", f"isolated final worker failed: {response.get('message')}")
        return response

    def call(self, action: str, case: dict[str, Any] | None = None) -> dict[str, Any]:
        import marshal

        require(self.process.stdin is not None, "isolated worker has no request pipe")
        document: dict[str, Any] = {"action": action}
        if case is not None:
            document["case"] = case
        payload = marshal.dumps(document)
        try:
            self.process.stdin.write(len(payload).to_bytes(8, "big"))
            self.process.stdin.write(payload)
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as error:
            raise ProtocolError("isolated final candidate crashed during its paired case") from error
        return self.receive()

    def close(self) -> None:
        if self.process.stdin is not None and self.process.poll() is None:
            import marshal

            payload = marshal.dumps({"action": "close"})
            try:
                self.process.stdin.write(len(payload).to_bytes(8, "big") + payload)
                self.process.stdin.flush()
            except (BrokenPipeError, OSError):
                pass
        try:
            self.process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=2)


def verify_live_worker(
    worker: IsolatedWorker,
    module: str,
    edge: dict[str, Any] | None,
) -> None:
    if module == "re":
        require(worker.ready.get("module") == "re", "live Python baseline was substituted")
        return
    require(edge is not None, "a live candidate has no independently qualified native artifacts")
    artifacts = edge["artifacts"]
    source = artifacts["public-python"]
    require(
        worker.ready.get("source") == source["path"]
        and worker.ready.get("source_sha256") == source["sha256"],
        "the actually imported candidate differs from its frozen correctness proof",
    )
    native = worker.ready.get("native")
    require(isinstance(native, dict), "actual candidate native mappings were not recorded")
    for role in ("native-bridge", "native-engine"):
        if role in artifacts:
            item = artifacts[role]
            require(
                native.get(item["path"]) == item["sha256"],
                f"candidate {role} is not actually mapped with its correctness-qualified digest",
            )


def open_blinded_seed(document: dict[str, Any]) -> bytes:
    seal = document["seal"]
    path = seal["opening_path"]
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ProtocolError("the exact, unopened 0600 final opening is unavailable") from error
    try:
        import stat

        metadata = os.fstat(descriptor)
        require(stat.S_ISREG(metadata.st_mode), "the holdout opening is not a regular file")
        require(stat.S_IMODE(metadata.st_mode) == 0o600, "holdout opening permissions changed")
        require(metadata.st_size == 32, "holdout opening size changed")
        opening = os.read(descriptor, 33)
    finally:
        os.close(descriptor)
    require(len(opening) == 32, "the blinded holdout opening is truncated or oversized")
    require(
        hmac.compare_digest(hashlib.sha256(opening).hexdigest(), seal["opening_sha256"]),
        "the actual holdout opening does not match the prospective commitment",
    )
    return opening


class RawEvidence:
    """Exclusive, deterministic gzip stream with a complete raw-line digest."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.stream: Any = None
        self.compressed: Any = None
        self.digest = hashlib.sha256()
        self.rows = 0

    def __enter__(self) -> "RawEvidence":
        self.stream = self.path.open("xb")
        self.compressed = gzip.GzipFile(
            filename="", fileobj=self.stream, mode="wb", compresslevel=6, mtime=0
        )
        return self

    def append(self, row: dict[str, Any]) -> None:
        line = canonical_bytes(row) + b"\n"
        self.compressed.write(line)
        self.digest.update(line)
        self.rows += 1

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        if self.compressed is not None:
            self.compressed.close()
        if self.stream is not None:
            self.stream.close()


def require_observation(actual: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    require(actual == expected, f"the exact CPython correctness gate failed: {label}")


def final_measurement(args: argparse.Namespace, document: dict[str, Any]) -> dict[str, Any]:
    """One explicit final run; no earlier command can open or generate cases."""
    require(
        args.authorize_final_unseal == UNSEAL_AUTHORIZATION,
        "the irreversible final holdout has not been explicitly authorized",
    )
    validate_manifest(document)
    modules = tuple(args.module)
    validate_modules(modules, document["trials"]["minimum_candidates"])
    edges = verify_edge_qualifications(modules, args.edge_oracle)
    campaigns = verify_current_campaigns(modules, args.campaign_proof)
    contracts = verify_deep_contracts(modules, args.deep_proof, edges)
    scratch_audit = verify_from_scratch_audit(args.from_scratch_audit, modules)
    freeze = verify_candidate_freeze(
        args.candidate_freeze, document, modules, edges, campaigns, contracts, scratch_audit
    )
    descriptors = case_descriptors()
    validate_descriptors(descriptors)
    raw_path = checked_evidence_path(args.raw, "final complete raw rows", must_exist=False)
    memory_path = checked_evidence_path(args.memory, "final complete memory rows", must_exist=False)
    summary_path = checked_evidence_path(args.output, "final complete results", must_exist=False)
    marker_path = checked_evidence_path(args.unseal_marker, "single-use final opening marker", must_exist=False)
    require(len({raw_path, memory_path, summary_path, marker_path}) == 4, "final evidence outputs overlap")

    workers: dict[str, IsolatedWorker] = {}
    memory_workers: dict[str, IsolatedWorker] = {}
    by_candidate: dict[str, dict[tuple[str, str], list[float]]] = {
        name: {(api, workload): [] for api in API_FAMILIES for workload in WORKLOAD_FAMILIES}
        for name in modules[1:]
    }
    case_results: dict[str, list[dict[str, Any]]] = {name: [] for name in modules[1:]}
    correctness_snapshots = 0
    opening: bytes | None = None
    try:
        for module in modules:
            worker = IsolatedWorker(module, "timing", document["trials"]["case_timeout_seconds"])
            verify_live_worker(worker, module, edges.get(module))
            workers[module] = worker

        marker = {
            "schema": "rebar-v8-final-single-use-unseal-marker-v1",
            "protocol_binding_sha256": document["binding_sha256"],
            "candidate_freeze_sha256": freeze["sha256"],
            "modules": list(modules),
            "opening_sha256": document["seal"]["opening_sha256"],
            "state": "irreversibly-authorized-no-retry",
        }
        with marker_path.open("x", encoding="utf-8") as target:
            json.dump(marker, target, allow_nan=False, indent=2, sort_keys=True)
            target.write("\n")
        opening = open_blinded_seed(document)

        with RawEvidence(raw_path) as raw:
            for descriptor in descriptors:
                case = materialize_case(descriptor, opening)
                baseline_preflight = workers["re"].call("warmup", case)
                require(baseline_preflight.get("kind") == "warmup", "Python baseline preflight failed")
                expected = baseline_preflight.get("observation")
                require(isinstance(expected, dict) and expected.get("status") == "ok", "a timed holdout case is not valid for Python")

                for warmup in range(WARMUPS):
                    order = counterbalanced_order(modules, descriptor["id"], warmup, document["trials"]["order_seed"])
                    for name in order:
                        result = workers[name].call("warmup", case)
                        require_observation(result.get("observation"), expected, "isolated warmup")

                case_logs: dict[str, list[float]] = {name: [] for name in modules[1:]}
                for round_index in range(PAIRED_ROUNDS):
                    order = counterbalanced_order(
                        modules, descriptor["id"], round_index, document["trials"]["order_seed"]
                    )
                    round_samples: dict[str, dict[str, Any]] = {}
                    for position, name in enumerate(order):
                        sample = workers[name].call("sample", case)
                        require(sample.get("kind") == "sample", "an isolated timed sample is invalid")
                        for gate in ("before", "observed", "after"):
                            require_observation(sample.get(gate), expected, f"{descriptor['id']}:{round_index}:{name}:{gate}")
                            correctness_snapshots += 1
                        elapsed = sample.get("elapsed_ns")
                        require(isinstance(elapsed, int) and not isinstance(elapsed, bool) and elapsed > 0, "an isolated timed sample is not positive")
                        round_samples[name] = sample
                        raw.append(
                            {
                                "schema": ROW_SCHEMA,
                                "case": descriptor["id"],
                                "api": descriptor["api"],
                                "workload": descriptor["workload"],
                                "round": round_index,
                                "module": name,
                                "position": position,
                                "elapsed_ns": elapsed,
                                "correctness_pre": True,
                                "correctness_timed": True,
                                "correctness_post": True,
                            }
                        )
                    require(set(round_samples) == set(modules), "an isolated paired sample omitted an engine")
                    baseline_elapsed = round_samples["re"]["elapsed_ns"]
                    for name in modules[1:]:
                        case_logs[name].append(math.log(baseline_elapsed / round_samples[name]["elapsed_ns"]))

                for name in modules[1:]:
                    logs = case_logs[name]
                    mean = statistics.fmean(logs)
                    speedup = math.exp(mean)
                    lower, upper = case_confidence(logs)
                    case_results[name].append(
                        {
                            "case": descriptor["id"],
                            "api": descriptor["api"],
                            "workload": descriptor["workload"],
                            "speedup": speedup,
                            "confidence_low": lower,
                            "confidence_high": upper,
                            "statistically_faster": is_significant_win(lower),
                            "runtime_regression_over_20_percent": is_runtime_regression(speedup),
                            "paired_rounds": PAIRED_ROUNDS,
                        }
                    )
                    by_candidate[name][(descriptor["api"], descriptor["workload"])].append(mean)

            expected_rows = CASE_COUNT * PAIRED_ROUNDS * len(modules)
            require(raw.rows == expected_rows, "the final raw timed-row denominator is incomplete")
            require(correctness_snapshots == expected_rows * 3, "the complete three-gate correctness denominator changed")
            raw_summary = {
                "path": str(raw_path.relative_to(ROOT)),
                "rows": raw.rows,
                "uncompressed_rows_sha256": raw.digest.hexdigest(),
            }

        memory_descriptors = [item for item in descriptors if item["index"] in MEMORY_CELL_INDICES]
        require(len(memory_descriptors) == 768, "the balanced memory cohort changed")
        for module in modules:
            worker = IsolatedWorker(module, "memory", document["trials"]["case_timeout_seconds"])
            verify_live_worker(worker, module, edges.get(module))
            memory_workers[module] = worker
        with RawEvidence(memory_path) as memory:
            for descriptor in memory_descriptors:
                case = materialize_case(descriptor, opening)
                observations = {
                    name: memory_workers[name].call("memory", case) for name in modules
                }
                expected = observations["re"].get("observation")
                require(isinstance(expected, dict) and expected.get("status") == "ok", "baseline memory operation failed")
                for name, record in observations.items():
                    require(record.get("kind") == "memory", "memory worker returned an invalid record")
                    require_observation(record.get("observation"), expected, "separate memory correctness gate")
                    for field in (
                        "python_current_bytes",
                        "python_peak_bytes",
                        "process_current_before_bytes",
                        "process_current_after_bytes",
                        "process_peak_bytes",
                    ):
                        require(
                            isinstance(record.get(field), int)
                            and not isinstance(record[field], bool)
                            and record[field] >= 0,
                            f"an isolated memory measurement is invalid: {field}",
                        )
                    memory.append(
                        {
                            "schema": "rebar-v8-final-memory-row-v1",
                            "case": descriptor["id"],
                            "api": descriptor["api"],
                            "workload": descriptor["workload"],
                            "module": name,
                            "python_current_bytes": record["python_current_bytes"],
                            "python_peak_bytes": record["python_peak_bytes"],
                            "process_current_before_bytes": record["process_current_before_bytes"],
                            "process_current_after_bytes": record["process_current_after_bytes"],
                            "process_peak_bytes": record["process_peak_bytes"],
                            "instrumentation_worker": True,
                            "correctness": True,
                        }
                    )
            require(memory.rows == 768 * len(modules), "the final memory denominator is incomplete")
            memory_summary = {
                "path": str(memory_path.relative_to(ROOT)),
                "rows": memory.rows,
                "cases_per_module": 768,
                "uncompressed_rows_sha256": memory.digest.hexdigest(),
                "python_peak_definition": "tracemalloc-python-allocations-only",
                "process_peak_definition": "whole-process-peak-rss-bytes",
            }

        results: list[dict[str, Any]] = []
        for index, name in enumerate(modules[1:]):
            full = case_results[name]
            require(len(full) == CASE_COUNT, "a final candidate result omitted a case")
            means = by_candidate[name]
            all_means = [value for values in means.values() for value in values]
            require(len(all_means) == CASE_COUNT, "candidate case-log denominator changed")
            low, high = stratified_bootstrap(
                means,
                seed=document["statistics"]["bootstrap_seed"] + index,
                draws=BOOTSTRAP_DRAWS,
            )
            wins = sum(item["statistically_faster"] for item in full)
            regressions = [item for item in full if item["runtime_regression_over_20_percent"]]
            results.append(
                {
                    "module": name,
                    "cases": CASE_COUNT,
                    "geomean_speedup": math.exp(statistics.fmean(all_means)),
                    "confidence_low": low,
                    "confidence_high": high,
                    "statistically_faster_cases": wins,
                    "minimum_statistically_faster_cases": MINIMUM_SIGNIFICANT_WINS,
                    "regression_count": len(regressions),
                    "regressions": regressions,
                    "case_results": full,
                    "meets_speed_requirement": low >= 1.5,
                    "meets_case_requirement": wins >= MINIMUM_SIGNIFICANT_WINS,
                    "success": low >= 1.5 and wins >= MINIMUM_SIGNIFICANT_WINS,
                }
            )

        for name, worker in workers.items():
            proof = worker.call("provenance")
            require(proof.get("kind") == "provenance", "final live native provenance is missing")
            if name != "re":
                require(proof.get("forbidden_loaded") == [], "candidate acquired a regex engine during timing")
                require(proof.get("source_sha256") == edges[name]["artifacts"]["public-python"]["sha256"], "candidate source changed during final timing")
                for role in ("native-bridge", "native-engine"):
                    if role in edges[name]["artifacts"]:
                        artifact = edges[name]["artifacts"][role]
                        require(proof.get("native", {}).get(artifact["path"]) == artifact["sha256"], "candidate native code changed during final timing")

        summary = {
            "schema": SUMMARY_SCHEMA,
            "manifest_sha256": canonical_digest(document),
            "protocol_binding_sha256": document["binding_sha256"],
            "candidate_freeze": freeze,
            "from_scratch_audit": scratch_audit,
            "python": "3.14.6",
            "modules": list(modules),
            "cases": CASE_COUNT,
            "paired_rounds": PAIRED_ROUNDS,
            "warmups": WARMUPS,
            "overall_bootstrap_draws": BOOTSTRAP_DRAWS,
            "correctness_snapshots": correctness_snapshots,
            "cold_process_startup": [
                {
                    "module": name,
                    "elapsed_ns": workers[name].startup_elapsed_ns,
                    "definition": "isolated-process-start-import-and-native-proof",
                    "included_in_main_speedup": False,
                }
                for name in modules
            ],
            "raw": raw_summary,
            "memory": memory_summary,
            "results": results,
            "opening_sha256": document["seal"]["opening_sha256"],
            "opening_hex": opening.hex(),
            "original_holdout_accessed": False,
            "original_v7_cases": document["history"]["original_v7_cases"],
            "original_engines_original_holdout": "HISTORICALLY PUBLISHED",
            "corrected_rust_original_holdout": "NOT MEASURED",
            "combined_results": "NOT MEASURED",
            "failed": 0,
        }
        with summary_path.open("x", encoding="utf-8") as target:
            json.dump(summary, target, allow_nan=False, indent=2, sort_keys=True)
            target.write("\n")
        return {
            "schema": SUMMARY_SCHEMA,
            "path": str(summary_path.relative_to(ROOT)),
            "cases": CASE_COUNT,
            "paired_rounds": PAIRED_ROUNDS,
            "raw_rows": raw_summary["rows"],
            "correctness_snapshots": correctness_snapshots,
            "memory_rows": memory_summary["rows"],
            "opening_published_only_in_final_summary": True,
            "failed": 0,
        }
    finally:
        for worker in memory_workers.values():
            worker.close()
        for worker in workers.values():
            worker.close()


def validate_paired_rows(
    rows: list[dict[str, Any]],
    descriptors: list[dict[str, Any]],
    modules: tuple[str, ...],
    rounds: int,
    order_seed: int,
) -> dict[tuple[str, int, str], dict[str, Any]]:
    require(1 <= rounds <= PAIRED_ROUNDS, "the paired-round denominator is invalid")
    expected_rows = len(descriptors) * rounds * len(modules)
    require(len(rows) == expected_rows, "a timed case, candidate, or paired round is missing")
    known = {case["id"] for case in descriptors}
    observations: dict[tuple[str, int, str], dict[str, Any]] = {}
    for row in rows:
        require(isinstance(row, dict) and row.get("schema") == ROW_SCHEMA, "an observed row is invalid")
        identifier = row.get("case")
        round_index = row.get("round")
        module = row.get("module")
        require(identifier in known, "an observed case was not frozen")
        require(isinstance(round_index, int) and 0 <= round_index < rounds, "an observed round is invalid")
        require(module in modules, "an observed candidate was not frozen")
        key = (identifier, round_index, module)
        require(key not in observations, "an observed case/candidate/round was duplicated")
        elapsed = row.get("elapsed_ns")
        require(isinstance(elapsed, int) and not isinstance(elapsed, bool) and elapsed > 0, "elapsed nanoseconds are not positive")
        require(row.get("correctness_pre") is True, "the before-timing correctness gate failed")
        require(row.get("correctness_timed") is True, "the timed-result correctness gate failed")
        require(row.get("correctness_post") is True, "the after-timing correctness gate failed")
        require(
            row.get("position")
            == counterbalanced_order(modules, identifier, round_index, order_seed).index(module),
            "the randomized counterbalanced paired order changed",
        )
        observations[key] = row
    for descriptor in descriptors:
        for round_index in range(rounds):
            require(
                all((descriptor["id"], round_index, module) in observations for module in modules),
                "a baseline/candidate pair is incomplete",
            )
    return observations


@contextlib.contextmanager
def synthetic_io_guard() -> Any:
    """Fail before I/O on secret, historical performance, and poison paths."""
    original_builtin = builtins.open
    original_io = io.open
    attempts: list[str] = []

    def reject_if_forbidden(file: Any) -> None:
        if isinstance(file, (str, bytes, os.PathLike)):
            value = os.fsdecode(file)
            forbidden = (
                "/performance/v6/",
                "/performance/v7/",
                "/fixtures/",
                "/__rebar_v8_synthetic_poison__/",
                "rebar-v8-final-holdout-opening-",
            )
            if any(marker in value for marker in forbidden):
                attempts.append(value)
                raise ProtocolError("synthetic guard rejected a forbidden or poisoned input")

    def guarded_builtin(file: Any, *args: Any, **kwargs: Any) -> Any:
        reject_if_forbidden(file)
        return original_builtin(file, *args, **kwargs)

    def guarded_io(file: Any, *args: Any, **kwargs: Any) -> Any:
        reject_if_forbidden(file)
        return original_io(file, *args, **kwargs)

    builtins.open = guarded_builtin
    io.open = guarded_io
    try:
        yield attempts
    finally:
        builtins.open = original_builtin
        io.open = original_io


def expect_rejection(name: str, function: Any) -> dict[str, str]:
    try:
        function()
    except (ProtocolError, ValueError, TypeError, OverflowError, OSError) as error:
        return {"name": name, "result": "rejected", "reason": type(error).__name__}
    raise ProtocolError(f"synthetic poison was silently accepted: {name}")


def copy_json(document: object) -> Any:
    return json.loads(canonical_bytes(document))


def mutate(document: dict[str, Any], path: tuple[str, ...], value: object) -> dict[str, Any]:
    changed = copy_json(document)
    cursor: dict[str, Any] = changed
    for component in path[:-1]:
        cursor = cursor[component]
    cursor[path[-1]] = value
    return changed


def synthetic_rows(
    descriptor: dict[str, Any], modules: tuple[str, ...], rounds: int, order_seed: int
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for round_index in range(rounds):
        order = counterbalanced_order(modules, descriptor["id"], round_index, order_seed)
        for position, module in enumerate(order):
            rows.append(
                {
                    "schema": ROW_SCHEMA,
                    "case": descriptor["id"],
                    "round": round_index,
                    "module": module,
                    "position": position,
                    "elapsed_ns": 100 + round_index,
                    "correctness_pre": True,
                    "correctness_timed": True,
                    "correctness_post": True,
                }
            )
    return rows


def synthetic_case_structure(
    descriptors: list[dict[str, Any]], document: dict[str, Any]
) -> dict[str, Any]:
    """Check a tiny, explicitly separate case domain without unsealing."""
    import marshal

    reference = __import__("re")
    require(
        not hmac.compare_digest(
            hashlib.sha256(SYNTHETIC_CASE_OPENING).hexdigest(),
            document["seal"]["opening_sha256"],
        ),
        "the synthetic case opening collides with the secret holdout commitment",
    )
    patterns: set[tuple[str, str]] = set()
    escapes: set[tuple[str, bytes]] = set()
    subject_counts: collections.Counter[str] = collections.Counter()
    synthetic_descriptors: list[dict[str, Any]] = []

    def actual_kind(item: dict[str, Any]) -> str:
        if item.get("input") != "bytes":
            return "str"
        if item["api"] in ("compile", "escape"):
            return "bytes"
        return ("bytes", "bytearray", "memoryview")[item["variant"] % 3]

    for api_index, api in enumerate(API_FAMILIES):
        workload = WORKLOAD_FAMILIES[api_index % len(WORKLOAD_FAMILIES)]
        pool = [
            item for item in descriptors
            if item["api"] == api and item["workload"] == workload
        ]
        require(len(pool) == CASES_PER_CELL, "a synthetic structural cell is incomplete")
        source_types = ("str", "bytes") if api in ("compile", "escape") else (
            "str", "bytes", "bytearray", "memoryview"
        )
        for source_kind in source_types:
            suitable = [item for item in pool if actual_kind(item) == source_kind]
            require(bool(suitable), "a declared mutable-buffer source has no genuine materialization")
            base = suitable[0]
            descriptor = copy_json(base)
            descriptor["id"] = (
                f"synthetic.v8.{api}.{workload}.{descriptor['index']:03d}.{source_kind}"
            )
            require(not descriptor["id"].startswith("v8."), "a synthetic case reused a real holdout identity")
            generated = materialize_case(descriptor, SYNTHETIC_CASE_OPENING, synthetic=True)
            repeat = materialize_case(descriptor, SYNTHETIC_CASE_OPENING, synthetic=True)
            require(generated == repeat, "synthetic HMAC case generation is not deterministic")
            transported = marshal.loads(marshal.dumps(generated))
            require(transported == generated, "a synthetic case cannot cross the isolated-worker boundary")
            subject = decode_wire_subject(transported["subject"], source_kind)
            expected_type = {
                "str": str,
                "bytes": bytes,
                "bytearray": bytearray,
                "memoryview": memoryview,
            }[source_kind]
            require(type(subject) is expected_type, "declared mutable-buffer type was not actually reconstructed")
            subject_counts[source_kind] += 1
            pattern = transported["pattern"]
            if api == "escape":
                encoded = subject.encode("utf-8") if isinstance(subject, str) else bytes(subject)
                identity = (source_kind, encoded)
                require(identity not in escapes, "synthetic escape subjects are repeated")
                escapes.add(identity)
                reference.escape(subject)
            else:
                text = pattern.decode("ascii") if isinstance(pattern, bytes) else pattern
                require("(?#x" in text and text.endswith(")"), "a case lacks its semantic-preserving unique comment")
                identity = ("bytes" if isinstance(pattern, bytes) else "str", text)
                require(identity not in patterns, "distinct synthetic cases share an actual compiled pattern")
                patterns.add(identity)
                comment = text.rsplit("(?#", 1)[1][:-1].lower()
                require(
                    all(word not in comment for word in ("benchmark", "holdout", "calibration", "performance")),
                    "synthetic pattern contains a benchmark-detection marker",
                )
                compiled = reference.compile(pattern, transported["flags"])
                window = transported.get("window")
                if window:
                    compiled.search(subject, window[0], window[1])
                else:
                    compiled.search(subject)
            synthetic_descriptors.append(descriptor)

    require(len(synthetic_descriptors) == 44, "the tiny synthetic structural control denominator changed")
    require(subject_counts == {"str": 12, "bytes": 12, "bytearray": 10, "memoryview": 10}, "synthetic text and actual byte-buffer controls are incomplete")
    require(len(patterns) == 42 and len(escapes) == 2, "synthetic identities are not independently unique")
    return {
        "cases": len(synthetic_descriptors),
        "unique_patterns": len(patterns),
        "unique_escape_subjects": len(escapes),
        "actual_subject_types": dict(sorted(subject_counts.items())),
        "synthetic_descriptor": synthetic_descriptors[0],
        "real_descriptor": descriptors[0],
    }


def self_test(document: dict[str, Any]) -> dict[str, Any]:
    """Exercise public metadata and synthetic poison only; never unseal."""
    def phase(name: str) -> None:
        if os.environ.get("REBAR_V8_PROTOCOL_TRACE") == "1":
            print(f"v8-synthetic-phase={name}", file=sys.stderr, flush=True)

    checks: list[dict[str, str]] = []
    phase("start-no-opening-no-candidate")
    with synthetic_io_guard() as forbidden_attempts:
        validate_manifest(document)
        phase("manifest-verified")
        checks.append({"name": "frozen-source-and-canonical-manifest", "result": "passed"})
        descriptors = case_descriptors()
        validate_descriptors(descriptors)
        phase("12288-public-labels-verified")
        checks.append({"name": "12288-public-labels-no-patterns-no-opening", "result": "passed"})
        require(
            all("pattern" not in row and "subject" not in row and "seed" not in row for row in descriptors),
            "a public descriptor leaked a hidden input or seed",
        )
        checks.append({"name": "zero-heldout-inputs-generated", "result": "passed"})
        structural = synthetic_case_structure(descriptors, document)
        checks.append(
            {"name": "44-synthetic-unique-patterns-and-real-mutable-buffers", "result": "passed"}
        )
        phase("44-domain-isolated-unique-pattern-and-buffer-controls-verified")
        for name, action in (
            (
                "genuine-descriptor-in-synthetic-domain",
                lambda: materialize_case(
                    structural["real_descriptor"], SYNTHETIC_CASE_OPENING, synthetic=True
                ),
            ),
            (
                "synthetic-descriptor-in-live-domain",
                lambda: materialize_case(
                    structural["synthetic_descriptor"], SYNTHETIC_CASE_OPENING
                ),
            ),
            (
                "foreign-synthetic-opening",
                lambda: materialize_case(
                    structural["synthetic_descriptor"], b"\x00" * 32, synthetic=True
                ),
            ),
            (
                "bytearray-wire-kind-substitution",
                lambda: decode_wire_subject(
                    {"schema": BUFFER_WIRE_SCHEMA, "kind": "memoryview", "hex": "6162"},
                    "bytearray",
                ),
            ),
            (
                "memoryview-wire-schema-substitution",
                lambda: decode_wire_subject(
                    {"schema": "wrong", "kind": "memoryview", "hex": "6162"},
                    "memoryview",
                ),
            ),
            (
                "mutable-buffer-corrupt-wire-payload",
                lambda: decode_wire_subject(
                    {"schema": BUFFER_WIRE_SCHEMA, "kind": "bytearray", "hex": "not-hex"},
                    "bytearray",
                ),
            ),
            (
                "mutable-buffer-mislabeled-as-bytes",
                lambda: decode_wire_subject(b"plain", "memoryview"),
            ),
        ):
            checks.append(expect_rejection(name, action))

        mutations: tuple[tuple[str, tuple[str, ...], object], ...] = (
            ("schema-tamper", ("schema",), "wrong-schema"),
            ("state-already-unsealed", ("state",), "unsealed"),
            ("wrong-python", ("reference", "version"), "3.14.5"),
            ("wrong-unicode", ("reference", "unicode_version"), "15.0.0"),
            ("wrong-locale", ("reference", "character_locale"), "C.UTF-8"),
            ("wrong-generator-digest", ("source", "sha256"), "0" * 64),
            ("wrong-opening-digest", ("seal", "opening_sha256"), "0" * 64),
            ("wrong-opening-path", ("seal", "opening_path"), "/tmp/wrong-v8-opening"),
            ("weak-opening-mode", ("seal", "opening_mode"), "0644"),
            ("fictional-same-user-isolation", ("seal", "isolation"), "security-boundary"),
            ("one-case-missing", ("layout", "cases"), CASE_COUNT - 1),
            ("one-case-extra", ("layout", "cases"), CASE_COUNT + 1),
            ("api-denominator-minus-one", ("layout", "cases_per_api"), CASES_PER_API - 1),
            ("api-denominator-plus-one", ("layout", "cases_per_api"), CASES_PER_API + 1),
            ("cell-denominator", ("layout", "cases_per_cell"), CASES_PER_CELL - 1),
            ("repeated-nonunique-case-identities", ("layout", "case_identity"), "reused-pattern"),
            ("fictional-unmaterialized-byte-buffers", ("layout", "mutable_buffer_transport"), "label-only"),
            ("eleven-rounds", ("trials", "paired_rounds"), 11),
            ("missing-warmup", ("trials", "warmups"), WARMUPS - 1),
            ("changed-operation-bound", ("trials", "maximum_operations"), 15),
            ("missing-third-candidate", ("trials", "minimum_candidates"), 2),
            ("reduced-bootstrap", ("statistics", "overall_bootstrap_draws"), 1_999),
            ("mislabelled-case-bootstrap", ("statistics", "case_method"), "bootstrap"),
            ("7372-significant-wins", ("statistics", "minimum_significant_wins"), 7_372),
            ("weakened-overall-speed", ("statistics", "overall_lower_bound"), 1.49),
            ("removed-correctness-snapshot", ("correctness", "snapshots_per_timed_row"), 2),
            ("accepted-mismatch", ("correctness", "mismatches_allowed"), 1),
            ("accepted-crash", ("correctness", "crashes_allowed"), 1),
            ("accepted-timeout", ("correctness", "timeouts_allowed"), 1),
            ("downgraded-canonical-oracle-to-44084", ("correctness", "edge_checks"), 44_084),
            ("removed-canonical-oracle-category", ("correctness", "edge_categories"), 48),
            ("changed-canonical-oracle-source", ("correctness", "edge_runner_sha256"), "0" * 64),
            ("changed-canonical-python-answers", ("correctness", "edge_answer_sha256"), "0" * 64),
            ("removed-full-grammar", ("correctness", "grammar_checks"), 20_479),
            ("removed-object-contract", ("correctness", "object_checks"), 14_782),
            ("removed-full-unicode", ("correctness", "unicode_checks"), 4_494_554),
            ("removed-observable-callbacks", ("correctness", "observable_checks"), 478),
            ("removed-native-binder-safety", ("correctness", "native_binder_checks"), 33),
            ("removed-real-user-public-case", ("correctness", "deep_public_checks"), 392),
            ("waived-real-user-public-failure", ("correctness", "deep_public_mismatches_allowed"), 1),
            ("changed-real-user-seed", ("correctness", "deep_contract_seed"), DEEP_CONTRACT_SEED + 1),
            ("changed-real-user-suite-source", ("correctness", "deep_contract_source_sha256"), "0" * 64),
            ("changed-real-user-frozen-fixture", ("correctness", "deep_contract_fixture_sha256"), "0" * 64),
            ("changed-real-user-python-answers", ("correctness", "deep_contract_reference_sha256"), "0" * 64),
            ("omitted-private-gc-diagnostic", ("correctness", "deep_private_gc_rows"), 63),
            ("private-gc-falsely-counted-as-public", ("correctness", "deep_private_gc_policy"), "public-waiver"),
            ("changed-legacy-p0-count", ("correctness", "legacy_p0_cases"), 44_083),
            ("extra-public-waiver", ("correctness", "named_private_waivers"), ["PRIVATE-CACHE-LAYOUT", "PRIVATE-DEBUG-TEXT", "PUBLIC-API"]),
            ("external-engine-permitted", ("independence", "external_regex_packages"), "allowed"),
            ("candidate-delegation-permitted", ("independence", "candidate_delegation"), "allowed"),
            ("python-engine-in-candidate-worker", ("independence", "candidate_worker_python_regex"), "allowed"),
            ("tracemalloc-timing-contamination", ("independence", "memory_instrumentation"), "same-timing-worker"),
            ("old-heldout-input-permitted", ("independence", "prior_holdout_access"), "allowed"),
            ("missing-owned-native-elf", ("independence", "required_owned_native_elf_artifacts"), 4),
            ("wrong-memory-denominator", ("memory", "cases"), 767),
            ("python-memory-as-native", ("memory", "python_peak"), "native-allocations"),
            ("removed-process-memory", ("memory", "process_peak"), "not-measured"),
            ("removed-boundary-cost", ("memory", "boundary_cost"), "excluded"),
            ("concealed-original-published-results", ("history", "original_engines"), "NOT MEASURED"),
            ("changed-original-holdout-denominator", ("history", "original_v7_cases"), 10_311),
            ("falsely-published-corrected-rust-original", ("history", "corrected_rust_original_holdout"), "MEASURED"),
            ("early-expanded-holdout-result", ("history", "v8_expansion"), "MEASURED"),
            ("undeclared-combined-result", ("history", "combined_result"), "MEASURED"),
            ("removed-four-engine-timed-row", ("trials", "four_engine_timed_rows"), 1_523_711),
            ("removed-four-engine-correctness-gate", ("trials", "four_engine_correctness_snapshots"), 4_571_135),
            ("wrong-manifest-binding", ("binding_sha256",), "0" * 64),
        )
        for name, location, value in mutations:
            phase(f"manifest-poison:{name}")
            checks.append(
                expect_rejection(
                    name,
                    lambda p=location, v=value: validate_manifest(
                        mutate(document, p, v), check_source=False
                    ),
                )
            )
        phase("bounded-manifest-poisons-verified")

        checks.append(
            expect_rejection(
                "duplicate-frozen-case",
                lambda: validate_descriptors([descriptors[0], *descriptors[1:-1], descriptors[0]]),
            )
        )
        checks.append(
            expect_rejection("missing-frozen-case", lambda: validate_descriptors(descriptors[:-1]))
        )
        require_deep_public_outcome(393, 0, 64)
        checks.append({"name": "393-public-contract-zero-mismatch-64-private-diagnostics", "result": "passed"})
        for name, public_checks, public_mismatches, private_rows in (
            ("preserved-original-104-public-failures", 393, 104, 64),
            ("single-real-user-public-failure", 393, 1, 64),
            ("missing-real-user-public-case", 392, 0, 64),
            ("missing-real-user-private-diagnostic", 393, 0, 63),
        ):
            checks.append(
                expect_rejection(
                    name,
                    lambda c=public_checks, m=public_mismatches, p=private_rows:
                    require_deep_public_outcome(c, m, p),
                )
            )
        phase("deep-contract-poisons-verified")

        modules = ("re", "candidates.synthetic_a", "candidates.synthetic_b", "candidates.synthetic_c")
        validate_modules(modules)
        require(
            counterbalanced_order(modules, "synthetic.case", 0, SYNTHETIC_ORDER_SEED)
            == counterbalanced_order(modules, "synthetic.case", 0, SYNTHETIC_ORDER_SEED),
            "synthetic paired order is not reproducible",
        )
        first_positions = collections.Counter(
            counterbalanced_order(modules, "synthetic.case", trial, SYNTHETIC_ORDER_SEED)[0]
            for trial in range(PAIRED_ROUNDS)
        )
        require(
            set(first_positions) == set(modules)
            and max(first_positions.values()) - min(first_positions.values()) <= 1,
            "the 31-round synthetic paired order is positionally biased",
        )
        checks.append({"name": "31-round-four-engine-counterbalanced-order", "result": "passed"})

        for name, candidate_modules in (
            ("baseline-swapped", ("candidates.synthetic_a", "re", "candidates.synthetic_b", "candidates.synthetic_c")),
            ("baseline-duplicated", ("re", "re", "candidates.synthetic_b", "candidates.synthetic_c")),
            ("only-two-candidates", ("re", "candidates.synthetic_a", "candidates.synthetic_b")),
            ("external-regex-candidate", ("re", "candidates.regex", "candidates.synthetic_b", "candidates.synthetic_c")),
            ("nonproduction-candidate", ("re", "other.synthetic_a", "candidates.synthetic_b", "candidates.synthetic_c")),
        ):
            checks.append(expect_rejection(name, lambda m=candidate_modules: validate_modules(m)))

        descriptor = {"id": "synthetic.case"}
        rows = synthetic_rows(descriptor, modules, 3, SYNTHETIC_ORDER_SEED)
        validate_paired_rows(rows, [descriptor], modules, 3, SYNTHETIC_ORDER_SEED)
        checks.append({"name": "synthetic-pairs-and-three-exact-correctness-gates", "result": "passed"})
        for name, change in (
            ("missing-paired-row", lambda original: original[:-1]),
            ("duplicate-paired-row", lambda original: [*original[:-1], copy_json(original[0])]),
            ("nonpositive-elapsed", lambda original: [{**original[0], "elapsed_ns": 0}, *original[1:]]),
            ("negative-elapsed", lambda original: [{**original[0], "elapsed_ns": -1}, *original[1:]]),
            ("missing-before-gate", lambda original: [{**original[0], "correctness_pre": False}, *original[1:]]),
            ("missing-timed-gate", lambda original: [{**original[0], "correctness_timed": False}, *original[1:]]),
            ("missing-after-gate", lambda original: [{**original[0], "correctness_post": False}, *original[1:]]),
            ("swapped-round-position", lambda original: [{**original[0], "position": 99}, *original[1:]]),
            ("wrong-timed-engine", lambda original: [{**original[0], "module": "candidates.regex"}, *original[1:]]),
        ):
            checks.append(
                expect_rejection(
                    name,
                    lambda transform=change: validate_paired_rows(
                        transform(copy_json(rows)), [descriptor], modules, 3, SYNTHETIC_ORDER_SEED
                    ),
                )
            )
        phase("12-synthetic-paired-rows-verified")

        balanced = [[0.0, 0.0], [math.log(4.0), math.log(4.0)]]
        require(
            bootstrap_case_clusters(balanced, seed=SYNTHETIC_ORDER_SEED, draws=127, cases_per_cell=2)
            == (2.0, 2.0),
            "a heterogeneous synthetic bootstrap changed equal stratum weights",
        )
        varied = [[0.0, math.log(2.0)], [math.log(3.0), math.log(4.0)]]
        generator = random.Random(SYNTHETIC_ORDER_SEED)
        independent: list[float] = []
        for _ in range(127):
            first = varied[0][generator.randrange(2)] + varied[0][generator.randrange(2)]
            second = varied[1][generator.randrange(2)] + varied[1][generator.randrange(2)]
            independent.append(math.exp((first + second) / 4.0))
        brute_force = (percentile(independent, 0.025), percentile(independent, 0.975))
        require(
            bootstrap_case_clusters(varied, seed=SYNTHETIC_ORDER_SEED, draws=127, cases_per_cell=2)
            == brute_force,
            "efficient case-cluster resampling differs from its independent synthetic reference",
        )
        checks.append({"name": "exact-synthetic-stratified-case-cluster-bootstrap", "result": "passed"})
        for name, cells, draws, size in (
            ("missing-bootstrap-stratum", [], 127, 2),
            ("uneven-bootstrap-stratum", [[0.0], [0.0, 0.0]], 127, 2),
            ("zero-bootstrap-draws", balanced, 0, 2),
            ("nonfinite-bootstrap-log", [[0.0, float("nan")], [0.0, 0.0]], 127, 2),
        ):
            checks.append(
                expect_rejection(
                    name,
                    lambda c=cells, d=draws, n=size: bootstrap_case_clusters(
                        c, seed=SYNTHETIC_ORDER_SEED, draws=d, cases_per_cell=n
                    ),
                )
            )
        phase("127-tiny-stratified-draws-verified")

        require(case_confidence([0.0] * PAIRED_ROUNDS) == (1.0, 1.0), "self-comparison is not exactly 1x")
        require(not is_significant_win(1.0), "a confidence bound of exactly 1x was counted as a win")
        require(is_significant_win(math.nextafter(1.0, math.inf)), "a genuine lower-bound win was dropped")
        require(
            (3 * CASE_COUNT + 4) // 5 == 7_373 and (3 * (CASE_COUNT - 1) + 4) // 5 == 7_373,
            "the exact 60-percent significant-win arithmetic changed",
        )
        for value, expected in (
            (0.799, True),
            (0.8, True),
            (0.81, True),
            (0.833, True),
            (5.0 / 6.0, False),
            (0.834, False),
            (1.0, False),
        ):
            require(is_runtime_regression(value) is expected, "the strict 20-percent runtime boundary changed")
        for name, value in (
            ("zero-speedup", 0.0),
            ("negative-speedup", -1.0),
            ("nan-speedup", float("nan")),
            ("infinite-speedup", float("inf")),
        ):
            checks.append(expect_rejection(name, lambda x=value: is_runtime_regression(x)))
        checks.append({"name": "strict-five-sixths-regression-and-exact-confidence-boundaries", "result": "passed"})
        phase("confidence-and-strict-regression-boundaries-verified")

        phase("bounded-external-engine-poison-start")
        for name in ("re", "_sre", "regex", "re2", "pcre2", "hyperscan", "oniguruma"):
            require(name.split(".", 1)[0] in BANNED_ENGINE_MODULES, "synthetic built-in or external regex engine escaped detection")
        checks.append({"name": "synthetic-built-in-and-external-engine-import-poison", "result": "passed"})

        sentinel = "/__rebar_v8_synthetic_poison__/never-open"
        phase("synthetic-io-poison-start")
        checks.append(
            expect_rejection("poisoned-old-fixture-or-opening-open", lambda: builtins.open(sentinel, "rb"))
        )
        require(forbidden_attempts == [sentinel], "verification attempted a genuine holdout or secret read")
        phase("forbidden-io-poison-verified")

    report = {
        "schema": SELF_TEST_SCHEMA,
        "manifest_path": "performance/v8/holdout-manifest.json",
        "manifest_sha256": canonical_digest(document),
        "generator_sha256": file_digest(Path(__file__).resolve()),
        "cases": CASE_COUNT,
        "apis": len(API_FAMILIES),
        "workloads": len(WORKLOAD_FAMILIES),
        "cases_per_cell": CASES_PER_CELL,
        "paired_rounds": PAIRED_ROUNDS,
        "warmups": WARMUPS,
        "overall_bootstrap_draws": BOOTSTRAP_DRAWS,
        "minimum_significant_wins": MINIMUM_SIGNIFICANT_WINS,
        "synthetic_structural_cases": structural["cases"],
        "synthetic_unique_patterns": structural["unique_patterns"],
        "synthetic_actual_buffer_cases": (
            structural["actual_subject_types"]["bytearray"]
            + structural["actual_subject_types"]["memoryview"]
        ),
        "check_count": len(checks),
        "synthetic_poison_checks": sum(check["result"] == "rejected" for check in checks),
        "checks_sha256": canonical_digest(checks),
        "failed": 0,
        "old_holdout_accessed": False,
        "opening_read": False,
        "opening_displayed": False,
        "hidden_cases_generated": 0,
        "candidate_imported": False,
        "timing_performed": False,
        "memory_measured": False,
    }
    phase("complete-no-opening-no-timing")
    return report


def verify_recorded_self_test(document: dict[str, Any], path: Path = EVIDENCE_PATH) -> dict[str, Any]:
    require(path.resolve() == EVIDENCE_PATH.resolve(), "the frozen synthetic evidence path changed")
    try:
        with path.open("rb") as stream:
            recorded = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ProtocolError("cannot read the frozen synthetic self-test evidence") from error
    require(recorded == self_test(document), "frozen synthetic protocol evidence is stale or changed")
    return recorded


def freeze_candidate_selection(args: argparse.Namespace, document: dict[str, Any]) -> dict[str, Any]:
    """Freeze final qualified engines without reading or creating a case."""
    validate_manifest(document)
    modules = tuple(args.module)
    validate_modules(modules, document["trials"]["minimum_candidates"])
    edges = verify_edge_qualifications(modules, args.edge_oracle)
    campaigns = verify_current_campaigns(modules, args.campaign_proof)
    contracts = verify_deep_contracts(modules, args.deep_proof, edges)
    scratch_audit = verify_from_scratch_audit(args.from_scratch_audit, modules)
    stopping = args.stopping_commit
    require(
        isinstance(stopping, str)
        and len(stopping) in (40, 64)
        and all(character in "0123456789abcdef" for character in stopping),
        "candidate stopping commit must be a full lowercase Git object digest",
    )
    target = checked_evidence_path(args.candidate_freeze, "final candidate and stopping freeze", must_exist=False)
    freeze = {
        "schema": CANDIDATE_FREEZE_SCHEMA,
        "protocol_binding_sha256": document["binding_sha256"],
        "stopping_commit": stopping,
        "baseline": "re",
        "from_scratch_audit_sha256": scratch_audit["sha256"],
        "candidates": [
            {
                "module": module,
                "edge_sha256": edges[module]["sha256"],
                "campaign_sha256": campaigns[module]["sha256"],
                "deep_contract_sha256": contracts[module]["sha256"],
                "artifacts": edges[module]["artifacts"],
            }
            for module in modules[1:]
        ],
        "opening_read": False,
        "hidden_cases_generated": 0,
        "performance_measured": False,
    }
    with target.open("x", encoding="utf-8") as destination:
        json.dump(freeze, destination, allow_nan=False, indent=2, sort_keys=True)
        destination.write("\n")
    return {
        "schema": CANDIDATE_FREEZE_SCHEMA,
        "path": str(target.relative_to(ROOT)),
        "sha256": file_digest(target),
        "candidate_count": len(modules) - 1,
        "opening_read": False,
        "hidden_cases_generated": 0,
        "performance_measured": False,
        "failed": 0,
    }


def add_candidate_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument(
        "--module", action="append", required=True,
        help="repeat in frozen order, starting with re and including at least three candidates",
    )
    parser.add_argument(
        "--edge-oracle", type=Path, action="append", required=True,
        help="repeat once per candidate: exact passing 223,198-check native-provenance proof",
    )
    parser.add_argument(
        "--campaign-proof", type=Path, action="append", required=True,
        help="repeat once per candidate: current complete, passing, holdout-blind correctness campaign",
    )
    parser.add_argument(
        "--deep-proof", type=Path, action="append", required=True,
        help="repeat once per candidate: passing frozen 393-case real-user public-contract proof",
    )
    parser.add_argument(
        "--from-scratch-audit", type=Path, required=True,
        help="committed all-engine no-delegation audit proving all five VM, Rust, and Zig native artifacts",
    )
    parser.add_argument(
        "--candidate-freeze", type=Path, required=True,
        help="exclusive v8-evidence artifact freezing all qualified engines and the stopping commit",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    bind = commands.add_parser("binding", help="print the canonical seal digest without opening a seed")
    bind.add_argument("--manifest", type=Path, default=MANIFEST_PATH)

    verify = commands.add_parser("verify", help="verify frozen metadata without reading any holdout")
    verify.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    verify.add_argument("--evidence", action="store_true", help="also verify committed synthetic self-tests")

    test = commands.add_parser("self-test", help="run only deterministic synthetic protocol poison tests")
    test.add_argument("--manifest", type=Path, default=MANIFEST_PATH)

    freeze = commands.add_parser(
        "freeze-candidates",
        help="commit qualified candidate identities and stop optimizing without opening any test",
    )
    add_candidate_arguments(freeze)
    freeze.add_argument("--stopping-commit", required=True)

    preflight = commands.add_parser(
        "preflight",
        help="verify the frozen full-oracle and native identities without opening or timing cases",
    )
    add_candidate_arguments(preflight)

    final = commands.add_parser(
        "final",
        help="explicitly and irreversibly open and run the entirely new final holdout",
    )
    add_candidate_arguments(final)
    final.add_argument("--authorize-final-unseal", required=True)
    final.add_argument("--raw", type=Path, required=True)
    final.add_argument("--memory", type=Path, required=True)
    final.add_argument("--output", type=Path, required=True)
    final.add_argument("--unseal-marker", type=Path, required=True)

    args = parser.parse_args(argv)
    document = load_manifest(args.manifest)
    if args.command == "binding":
        print(json.dumps({"schema": SCHEMA, "binding_sha256": manifest_binding(document)}, sort_keys=True))
    elif args.command == "self-test":
        print(json.dumps(self_test(document), allow_nan=False, sort_keys=True))
    elif args.command == "freeze-candidates":
        print(json.dumps(freeze_candidate_selection(args, document), allow_nan=False, sort_keys=True))
    elif args.command == "preflight":
        validate_manifest(document)
        modules = tuple(args.module)
        validate_modules(modules, document["trials"]["minimum_candidates"])
        edges = verify_edge_qualifications(modules, args.edge_oracle)
        campaigns = verify_current_campaigns(modules, args.campaign_proof)
        contracts = verify_deep_contracts(modules, args.deep_proof, edges)
        scratch_audit = verify_from_scratch_audit(args.from_scratch_audit, modules)
        freeze = verify_candidate_freeze(
            args.candidate_freeze, document, modules, edges, campaigns, contracts, scratch_audit
        )
        print(
            json.dumps(
                {
                    "schema": CANDIDATE_FREEZE_SCHEMA,
                    "candidate_freeze_sha256": freeze["sha256"],
                    "cases": CASE_COUNT,
                    "candidate_count": len(modules) - 1,
                    "opening_read": False,
                    "hidden_cases_generated": 0,
                    "performance_measured": False,
                    "failed": 0,
                },
                allow_nan=False,
                sort_keys=True,
            )
        )
    elif args.command == "final":
        print(json.dumps(final_measurement(args, document), allow_nan=False, sort_keys=True))
    else:
        validate_manifest(document)
        report: dict[str, Any] = {
            "schema": SCHEMA,
            "manifest_sha256": canonical_digest(document),
            "generator_sha256": document["source"]["sha256"],
            "cases": CASE_COUNT,
            "apis": len(API_FAMILIES),
            "workloads": len(WORKLOAD_FAMILIES),
            "paired_rounds": PAIRED_ROUNDS,
            "overall_bootstrap_draws": BOOTSTRAP_DRAWS,
            "significant_wins_required": MINIMUM_SIGNIFICANT_WINS,
            "opening_read": False,
            "old_holdout_accessed": False,
            "hidden_cases_generated": 0,
            "candidate_imported": False,
            "timing_performed": False,
            "failed": 0,
        }
        if args.evidence:
            recorded = verify_recorded_self_test(document)
            report["synthetic_poison_checks"] = recorded["synthetic_poison_checks"]
            report["self_test_sha256"] = canonical_digest(recorded)
        print(json.dumps(report, allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProtocolError as error:
        print(f"v8 holdout protocol rejected: {error}", file=sys.stderr)
        raise SystemExit(2) from error
