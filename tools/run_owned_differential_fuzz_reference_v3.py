#!/usr/bin/env python3
"""Freeze and, only when requested, run two real CPython fuzz references."""

from __future__ import annotations

import ast
import builtins
import hashlib
import os
import stat
import sys


ROOT = "/home/dev-user/src/rebar"
SCHEMA = "rebar-owned-differential-fuzz-reference-v3"
SELF = "tools/run_owned_differential_fuzz_reference_v3.py"
PROTOCOL = "oracle/phase1/P0-DIFFERENTIAL-FUZZ-REFERENCE-V3.md"
CONTRACT = "oracle/phase1/p0-differential-fuzz-reference-v3.json"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_HASH = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
P0_CONTRACT = (
    "oracle/phase1/p0-completeness-v2.json",
    "fcd7abac619a6a4733e090cf49acbb958f8162eeb7dc6909a9d14501809e8237",
    28440, 2064, 525073,
)
MANIFEST = (
    "oracle/v2/manifest.json",
    "91ce7da8cd0ebcdf2861fbb82cd531855631e52815aa8c1684f6a798da6563f6",
    1359, 2064, 428246,
)
SEEDS = (
    "oracle/v2/seeds.json",
    "761d074856c36880db60965583207c78a46b8fced204e0f3b4e03e744fed74c7",
    210, 2064, 428245,
)
CORPUS = (
    "oracle/v2/expected.jsonl",
    "ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2",
    7602476, 2064, 428243,
)
ORIGINAL = (
    "tools/oracle_v2.py",
    "f038145dc0527f802203e18556f03b4bba636bb219105dc38c675c52a23e0fbb",
    14248, 2064, 428240,
)
V1_CORPUS = (
    "oracle/v1/expected.jsonl",
    "983885ee6411fd806edf3d72efbcc989f9b9f7775a6d127dc7c865673eeb0fed",
    1203505, 2064, 427910,
)
KINDS = {
    "byteslike": 11, "byteslike-escape": 2, "cache": 1, "call": 7359,
    "compile": 2, "debug": 1, "error": 456, "escape": 2, "exports": 1,
    "flags": 1, "generic": 4, "match-copy": 3, "pattern-equality": 1,
    "positional-warning": 3, "property": 384, "representation": 5,
    "roundtrip": 1, "scanner": 2, "warning": 5,
}
FIXED_SEEDS = {
    "deep_bytes": 1979121302, "deep_str": 1979121301,
    "invalid_patterns": 1511506921, "invalid_templates": 1511506922,
    "properties": 1511506920, "valid_bytes": 1511506919,
    "valid_str": 1511506918,
}
MAXIMUM_LINE = 262144
MAXIMUM_STREAM = 262144
MAXIMUM_RESULT = 67108864
FORBIDDEN = (
    "re", "_sre", "subprocess", "selectors", "threading", "_thread",
    "socket", "gzip", "zipfile", "tarfile", "ctypes", "time",
)
INITIAL_FORBIDDEN = frozenset(
    name for name in sys.modules
    if any(name == forbidden or name.startswith(forbidden + ".")
           for forbidden in FORBIDDEN)
)


class ReferenceError(Exception):
    """Reject altered evidence, incomplete workers, or unsafe source modes."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise ReferenceError(message)


def canonical(value: object) -> bytes:
    """Encode canonical JSON without importing json and its regex engine."""
    if value is None:
        return b"null"
    if value is True:
        return b"true"
    if value is False:
        return b"false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value).encode("ascii")
    if isinstance(value, str):
        pieces = ['"']
        for character in value:
            point = ord(character)
            if character == '"':
                pieces.append('\\"')
            elif character == "\\":
                pieces.append("\\\\")
            elif point < 32:
                escapes = {8: "\\b", 9: "\\t", 10: "\\n", 12: "\\f", 13: "\\r"}
                pieces.append(escapes.get(point, "\\u%04x" % point))
            else:
                require(not 0xD800 <= point <= 0xDFFF, "reject unpaired Unicode surrogate")
                pieces.append(character)
        pieces.append('"')
        return "".join(pieces).encode("utf-8")
    if isinstance(value, (list, tuple)):
        return b"[" + b",".join(canonical(item) for item in value) + b"]"
    if isinstance(value, dict):
        require(all(isinstance(key, str) for key in value), "reject non-string JSON key")
        return b"{" + b",".join(
            canonical(key) + b":" + canonical(value[key]) for key in sorted(value)
        ) + b"}"
    raise ReferenceError("reject non-canonical JSON value")


class JsonReader:
    """Small strict JSON reader; rejects duplicate keys and invalid integers."""

    def __init__(self, raw: bytes, maximum: int = MAXIMUM_RESULT) -> None:
        require(isinstance(raw, bytes) and len(raw) <= maximum, "reject oversized JSON")
        try:
            self.text = raw.decode("utf-8", "strict")
        except UnicodeError as error:
            raise ReferenceError("reject invalid UTF-8") from error
        self.index = 0

    def whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def take_string(self) -> str:
        start = self.index
        require(start < len(self.text) and self.text[start] == '"', "require JSON string")
        self.index += 1
        while self.index < len(self.text):
            current = self.text[self.index]
            require(ord(current) >= 32, "reject unescaped string control")
            if current == '"':
                self.index += 1
                token = self.text[start:self.index]
                try:
                    result = ast.literal_eval(token)
                except (SyntaxError, ValueError, TypeError) as error:
                    raise ReferenceError("reject invalid JSON string escape") from error
                require(isinstance(result, str), "reject non-string literal")
                require(all(not 0xD800 <= ord(item) <= 0xDFFF for item in result),
                        "reject unpaired Unicode surrogate")
                return result
            if current == "\\":
                self.index += 1
                require(self.index < len(self.text), "reject truncated string escape")
                escape = self.text[self.index]
                require(escape in '"\\/bfnrtu', "reject non-JSON string escape")
                if escape == "u":
                    require(self.index + 4 < len(self.text), "reject truncated unicode escape")
                    digits = self.text[self.index + 1:self.index + 5]
                    require(all(item in "0123456789abcdefABCDEF" for item in digits),
                            "reject invalid unicode escape")
                    self.index += 4
            self.index += 1
        raise ReferenceError("reject unterminated JSON string")

    def value(self, depth: int = 0) -> object:
        require(depth <= 96, "reject excessive JSON nesting")
        self.whitespace()
        require(self.index < len(self.text), "reject truncated JSON")
        character = self.text[self.index]
        if character == '"':
            return self.take_string()
        if character == "{":
            self.index += 1
            result: dict[str, object] = {}
            self.whitespace()
            if self.index < len(self.text) and self.text[self.index] == "}":
                self.index += 1
                return result
            while True:
                self.whitespace()
                key = self.take_string()
                require(key not in result, "reject duplicate JSON object key")
                self.whitespace()
                require(self.index < len(self.text) and self.text[self.index] == ":",
                        "require JSON object colon")
                self.index += 1
                result[key] = self.value(depth + 1)
                self.whitespace()
                require(self.index < len(self.text), "reject truncated JSON object")
                separator = self.text[self.index]
                self.index += 1
                if separator == "}":
                    return result
                require(separator == ",", "reject invalid JSON object separator")
        if character == "[":
            self.index += 1
            result_list: list[object] = []
            self.whitespace()
            if self.index < len(self.text) and self.text[self.index] == "]":
                self.index += 1
                return result_list
            while True:
                result_list.append(self.value(depth + 1))
                self.whitespace()
                require(self.index < len(self.text), "reject truncated JSON array")
                separator = self.text[self.index]
                self.index += 1
                if separator == "]":
                    return result_list
                require(separator == ",", "reject invalid JSON array separator")
        for token, decoded in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(token, self.index):
                self.index += len(token)
                return decoded
        start = self.index
        if character == "-":
            self.index += 1
        require(self.index < len(self.text) and self.text[self.index].isascii()
                and self.text[self.index].isdigit(), "reject unsupported JSON number")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index >= len(self.text) or self.text[self.index] not in "0123456789",
                    "reject noncanonical leading-zero integer")
        else:
            while (self.index < len(self.text) and self.text[self.index].isascii()
                   and self.text[self.index].isdigit()):
                self.index += 1
        require(self.index >= len(self.text) or self.text[self.index] not in ".eE",
                "reject unsupported floating-point evidence")
        return int(self.text[start:self.index])

    def finish(self) -> object:
        result = self.value()
        self.whitespace()
        require(self.index == len(self.text), "reject trailing JSON content")
        return result


def decode(raw: bytes, maximum: int = MAXIMUM_RESULT) -> object:
    return JsonReader(raw, maximum).finish()


def exact_hash(value: object, label: str) -> str:
    require(isinstance(value, str) and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            "require canonical SHA-256 for " + label)
    return value


def owner(path: str, digest: str, size: int, device: int, inode: int,
          *, executable: bool = False,
          capture: bool = True) -> tuple[bytes, dict[str, object]]:
    require(isinstance(path, str) and path and not path.startswith("/")
            and ".." not in path.split("/") and not path.endswith((".gz", ".zip")),
            "reject unsafe, archived, or hidden owner")
    descriptor = os.open(os.path.join(ROOT, path),
                         os.O_RDONLY | os.O_CLOEXEC | getattr(os, "O_NOFOLLOW", 0))
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode), "require a regular owner: " + path)
        require(identity.st_nlink == 1, "reject hard-linked owner: " + path)
        require(identity.st_size == size and identity.st_dev == device
                and identity.st_ino == inode, "reject changed owner identity: " + path)
        require(stat.S_IMODE(identity.st_mode) == (0o711 if executable else 0o600),
                "reject owner permissions: " + path)
        pieces: list[bytes] = []
        hasher = hashlib.sha256()
        total = 0
        while True:
            piece = os.read(descriptor, 65536)
            if not piece:
                break
            total += len(piece)
            hasher.update(piece)
            if capture:
                pieces.append(piece)
        raw = b"".join(pieces) if capture else b""
    finally:
        os.close(descriptor)
    require(total == size and (not capture or len(raw) == size)
            and hasher.hexdigest() == exact_hash(digest, path),
            "reject changed owner bytes: " + path)
    return raw, {
        "path": path, "sha256": digest, "bytes": size, "device": device,
        "inode": inode, "mode": "0711" if executable else "0600",
    }


def fixed_owner(values: tuple[str, str, int, int, int]) -> tuple[bytes, dict[str, object]]:
    return owner(*values)


def runtime_owner() -> dict[str, object]:
    descriptor = os.open(PYTHON, os.O_RDONLY | os.O_CLOEXEC | getattr(os, "O_NOFOLLOW", 0))
    hasher = hashlib.sha256()
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode) and identity.st_nlink == 1
                and identity.st_dev == 2049 and identity.st_ino == 9594007
                and identity.st_size == 32387816
                and stat.S_IMODE(identity.st_mode) == 0o711,
                "reject unpinned Python executable")
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            hasher.update(chunk)
    finally:
        os.close(descriptor)
    require(hasher.hexdigest() == PYTHON_HASH, "reject modified pinned Python executable")
    require(sys.version_info[:3] == (3, 14, 6)
            and sys.implementation.name == "cpython"
            and os.path.realpath(sys.executable) == PYTHON,
            "require the pinned CPython 3.14.6 source verifier")
    return {"path": PYTHON, "sha256": PYTHON_HASH, "bytes": 32387816,
            "device": 2049, "inode": 9594007, "mode": "0711"}


def owner_records(value: object) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    if isinstance(value, dict):
        if {"path", "sha256", "bytes", "device", "inode"}.issubset(value):
            path = value["path"]
            require(isinstance(path, str) and not path.startswith("/")
                    and not path.endswith((".gz", ".zip")),
                    "reject archived or unsafe inherited owner")
            _, record = owner(path, value["sha256"], value["bytes"],
                              value["device"], value["inode"], capture=False)
            result.append(record)
        for nested in value.values():
            result.extend(owner_records(nested))
    elif isinstance(value, list):
        for nested in value:
            result.extend(owner_records(nested))
    return result


def corpus_records(values: tuple[str, str, int, int, int], expected_count: int,
                   *, full: bool) -> dict[str, object]:
    path, digest, size, device, inode = values
    descriptor = os.open(os.path.join(ROOT, path),
                         os.O_RDONLY | os.O_CLOEXEC | getattr(os, "O_NOFOLLOW", 0))
    hasher = hashlib.sha256()
    pending = b""
    count = 0
    highest = 0
    kinds: dict[str, int] = {}
    identifiers: set[str] = set()
    obligations: set[str] = set()
    total = 0
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode) and identity.st_nlink == 1
                and stat.S_IMODE(identity.st_mode) == 0o600
                and (identity.st_size, identity.st_dev, identity.st_ino)
                == (size, device, inode), "reject changed streaming corpus identity")
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            hasher.update(chunk)
            total += len(chunk)
            pending += chunk
            while b"\n" in pending:
                raw, pending = pending.split(b"\n", 1)
                physical = len(raw) + 1
                require(physical <= MAXIMUM_LINE, "reject oversized corpus record")
                highest = max(highest, physical)
                count += 1
                if full:
                    value = decode(raw, MAXIMUM_LINE)
                    require(isinstance(value, dict), "require a complete case object")
                    identifier = value.get("id")
                    kind = value.get("kind")
                    mapped = value.get("obligations")
                    require(isinstance(identifier, str) and identifier not in identifiers,
                            "reject missing or duplicate frozen case ID")
                    require(isinstance(kind, str) and kind in KINDS,
                            "reject unknown frozen case kind")
                    require(isinstance(mapped, list)
                            and all(isinstance(item, str) for item in mapped),
                            "reject unmapped frozen case")
                    identifiers.add(identifier)
                    kinds[kind] = kinds.get(kind, 0) + 1
                    obligations.update(mapped)
            require(len(pending) < MAXIMUM_LINE,
                    "reject an unterminated oversized corpus record")
        require(not pending, "reject unterminated corpus record")
    finally:
        os.close(descriptor)
    require(total == size and count == expected_count
            and hasher.hexdigest() == digest, "reject incomplete or altered frozen corpus")
    result: dict[str, object] = {
        "path": path, "sha256": digest, "bytes": size, "device": device,
        "inode": inode, "mode": "0600", "case_count": count,
        "maximum_observed_record_bytes": highest,
        "per_record_limit_bytes": MAXIMUM_LINE,
        "plaintext_corpus_loaded_whole": False,
    }
    if full:
        require(kinds == KINDS and len(identifiers) == 8244
                and len(obligations) == 45,
                "reject incomplete frozen case, category, or obligation coverage")
        result.update({"unique_record_case_count": len(identifiers),
                       "record_kind_counts": kinds,
                       "record_mapped_obligation_ids": sorted(obligations)})
    return result


def effects() -> dict[str, object]:
    return {
        "actual_reference_worker_count": 0,
        "actual_reference_worker_process_ids": [],
        "actual_candidate_worker_count": 0,
        "actual_native_activation_count": 0,
        "actual_compiler_process_count": 0,
        "compressed_archive_open_count": 0,
        "hidden_holdout_open_count": 0,
        "clock_sample_count": 0,
        "network_operation_count": 0,
        "two_independent_reference_process_status": "NOT RUN",
        "candidate_status": "NOT RUN",
        "candidate_qualified": False,
        "qualified_candidate_count": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
    }


def source_wall() -> None:
    inherited = sorted(
        name for name in sys.modules
        if name not in INITIAL_FORBIDDEN
        and any(name == forbidden or name.startswith(forbidden + ".")
                for forbidden in FORBIDDEN)
    )
    require(not inherited, "reject regex, process, clock, archive, or network import: "
            + ",".join(inherited))


def reconstruct(source_pin: str, protocol_pin: str) -> dict[str, object]:
    source_wall()
    runtime = runtime_owner()
    source_raw = os.stat(os.path.join(ROOT, SELF), follow_symlinks=False)
    _, own_source = owner(SELF, exact_hash(source_pin, "source"), source_raw.st_size,
                          source_raw.st_dev, source_raw.st_ino)
    protocol_raw = os.stat(os.path.join(ROOT, PROTOCOL), follow_symlinks=False)
    _, own_protocol = owner(PROTOCOL, exact_hash(protocol_pin, "protocol"),
                            protocol_raw.st_size, protocol_raw.st_dev, protocol_raw.st_ino)
    matrix_bytes, matrix_owner = fixed_owner(P0_CONTRACT)
    matrix = decode(matrix_bytes)
    require(isinstance(matrix, dict)
            and matrix.get("schema") == "rebar-cpython-re-p0-completeness-v2"
            and matrix.get("status") == "BLOCKED"
            and matrix.get("phase1_canonical_candidate_context_crosswalk") == "PASS",
            "reject incorrectly authorized or falsified phase-one reference")
    gate = matrix.get("phase_gate")
    require(isinstance(gate, dict) and gate.get("status") == "BLOCKED"
            and gate.get("candidate_evaluation_authorized") is False
            and gate.get("native_build_authorized") is False
            and gate.get("performance_oracle_authorized") is False
            and gate.get("final_holdout_authorized") is False
            and gate.get("qualified_candidate_count") == 0,
            "reject an opened candidate, native, timing, or holdout gate")
    supplement = matrix.get("supplemental_differential_property_fuzz")
    require(isinstance(supplement, dict) and supplement.get("case_count") == 8244
            and supplement.get("two_independent_reference_process_status") == "NOT RUN"
            and supplement.get("candidate_status") == "NOT RUN"
            and supplement.get("case_denominator_included_in_original_31237") is False,
            "reject fabricated supplemental references or denominator")
    original = matrix.get("original_oracle")
    require(isinstance(original, dict), "reject missing original 31,237-case matrix")
    inherited_records = owner_records(matrix)
    distinct_owners = {record["path"]: record for record in inherited_records}
    require(len(distinct_owners) >= 60,
            "reject incomplete authenticated phase-one source-owner closure")
    manifest_bytes, manifest_owner = fixed_owner(MANIFEST)
    manifest = decode(manifest_bytes)
    require(isinstance(manifest, dict)
            and manifest.get("schema") == "rebar-correctness-v2"
            and manifest.get("python") == "3.14.6"
            and manifest.get("implementation") == "CPython"
            and manifest.get("unicode") == "16.0.0"
            and manifest.get("locale") == "C"
            and manifest.get("cases") == 8244
            and manifest.get("obligations") == 45
            and manifest.get("mapped_obligations") == 45
            and manifest.get("kinds") == KINDS
            and manifest.get("seeds") == FIXED_SEEDS
            and manifest.get("expected_sha256") == CORPUS[1]
            and manifest.get("parent_expected_sha256") == V1_CORPUS[1]
            and manifest.get("runner_sha256") == ORIGINAL[1],
            "reject drift in the full pinned Python fuzz manifest")
    seed_bytes, seed_owner = fixed_owner(SEEDS)
    require(decode(seed_bytes) == FIXED_SEEDS, "reject altered frozen fuzz seeds")
    _, original_owner = fixed_owner(ORIGINAL)
    streamed = corpus_records(CORPUS, 8244, full=True)
    parent = corpus_records(V1_CORPUS, 2048, full=False)
    require(streamed["record_kind_counts"] == supplement.get("record_kind_counts")
            and streamed["record_mapped_obligation_ids"]
            == sorted(supplement.get("record_mapped_obligation_ids", []))
            and streamed["maximum_observed_record_bytes"] == 83668,
            "reject discrepancies with the frozen complete P0 crosswalk")
    return {
        "schema": SCHEMA,
        "version": 3,
        "status": "BLOCKED",
        "phase": "CORRECTNESS ORACLE",
        "source": own_source,
        "protocol": own_protocol,
        "pinned_cpython": runtime,
        "p0_completeness_v2": matrix_owner,
        "p0_source_crosswalk_status": "PASS",
        "phase1_canonical_candidate_context_crosswalk": "PASS",
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "original_named_private_waiver_count": 13,
        "original_obligation_count": 73,
        "original_crosswalk_count": 34,
        "authenticated_inherited_source_owner_count": len(distinct_owners),
        "frozen_manifest": manifest_owner,
        "frozen_seeds": seed_owner,
        "original_named_module_runner": original_owner,
        "seeds": FIXED_SEEDS,
        "supplemental_corpus": streamed,
        "v1_parent_corpus": parent,
        "case_denominator_included_in_original_31237": False,
        "historical_single_context_worker_provenance": "NOT CAPTURED",
        "planned_reference_worker_count": 2,
        "planned_reference_roles": ["independent-reference-a", "independent-reference-b"],
        "planned_original_worker_command": [PYTHON, "-I", "-B",
                                             ROOT + "/" + ORIGINAL[0],
                                             "verify", "--module", "re"],
        "planned_worker_context": {
            "runner": "original unchanged tools/oracle_v2.py",
            "module": "re", "locale": "C",
            "original_v1_named_module": "rebar_oracle_v1_runner",
            "warnings": "original unchanged oracle warnings",
            "result": "complete original result including all failures",
            "process_start": "two actual independently observed os.posix_spawn PIDs",
            "worker_output": "separate fresh exclusive result-directory files",
            "stdout_stderr": "both workers concurrently bounded and fully drained",
        },
        "source_only_effects": effects(),
        "phase_gate": {
            "status": "BLOCKED",
            "candidate_evaluation_authorized": False,
            "native_build_authorized": False,
            "performance_oracle_authorized": False,
            "final_holdout_authorized": False,
            "qualified_candidate_count": 0,
            "winner_selected": False,
        },
    }


def arguments(argv: list[str]) -> dict[str, object]:
    modes = ("--self-test", "--verify-frozen-context", "--render-contract",
             "--render-contract-preview", "--run-reference")
    chosen = [name for name in modes if name in argv]
    require(len(chosen) == 1, "choose exactly one explicit controller mode")
    result: dict[str, object] = {"mode": chosen[0]}
    index = 0
    while index < len(argv):
        item = argv[index]
        if item in modes:
            index += 1
            continue
        require(item in ("--source-sha256", "--protocol-sha256",
                         "--contract-sha256", "--label"), "reject unknown option: " + item)
        require(index + 1 < len(argv), "reject missing option value")
        require(item not in result, "reject duplicate controller option")
        result[item] = argv[index + 1]
        index += 2
    require("--source-sha256" in result and "--protocol-sha256" in result,
            "require explicit independently measured source and protocol hashes")
    if result["mode"] not in ("--render-contract", "--render-contract-preview"):
        require("--contract-sha256" in result,
                "require an independently measured frozen contract hash")
    return result


def checked_contract(options: dict[str, object]) -> dict[str, object]:
    document = reconstruct(str(options["--source-sha256"]),
                           str(options["--protocol-sha256"]))
    identity = os.stat(os.path.join(ROOT, CONTRACT), follow_symlinks=False)
    raw, _ = owner(CONTRACT, exact_hash(options["--contract-sha256"], "contract"),
                   identity.st_size, identity.st_dev, identity.st_ino)
    require(raw == canonical(document) + b"\n",
            "reject changed, noncanonical, or fabricated source-only contract")
    return document


def source_self_test(document: dict[str, object]) -> dict[str, object]:
    rejected = 0
    invalid = (
        b'{"a":1,"a":2}', b'{"a":01}', b'{"a":1.0}', b'{"a":1e3}',
        b'{"a":true} garbage', b'{"a":"\\q"}', b'{"a":"\\ud800"}',
        b'{"a":', b'[1,]', b'{"a":1,}', b'"unterminated', b'{"a":NaN}',
        b'{"a":Infinity}', b'\xff', b'{"a":"line\nbreak"}',
    )
    for raw in invalid:
        try:
            decode(raw, MAXIMUM_LINE)
        except (ReferenceError, UnicodeError, ValueError, SyntaxError):
            rejected += 1
        else:
            raise ReferenceError("accepted hostile malformed JSON")
    valid = {"array": [None, True, False, -12, "new\nline"],
             "nested": {"safe": "snowman ☃"}}
    require(decode(canonical(valid)) == valid,
            "reject canonical Unicode JSON round trip")
    for bad in ("", "0" * 63, "g" * 64, "A" * 64, 12, None):
        try:
            exact_hash(bad, "hostile")
        except ReferenceError:
            rejected += 1
        else:
            raise ReferenceError("accepted a forged SHA-256")
    for path in ("../GOAL.md", "/tmp/archive", "oracle/failure.json.gz",
                 "../performance/holdout.json", ""):
        try:
            owner(path, "0" * 64, 0, 0, 0)
        except (ReferenceError, OSError):
            rejected += 1
        else:
            raise ReferenceError("accepted an unsafe owner path")
    require(document["status"] == "BLOCKED"
            and document["source_only_effects"] == effects()
            and document["phase_gate"]["candidate_evaluation_authorized"] is False,
            "reject incorrectly authorized source-only verification")
    source_wall()
    return {"schema": SCHEMA + "-self-test", "status": "PASS",
            "hostile_controls_rejected": rejected,
            "reference_status": "NOT RUN", "phase_gate_status": "BLOCKED",
            "original_case_execution_denominator": 31237,
            "supplemental_case_count": 8244,
            "actual_reference_worker_count": 0,
            "actual_reference_worker_process_ids": [],
            "actual_candidate_worker_count": 0,
            "holdout": "NOT OPENED", "performance": "NOT MEASURED"}


def validate_label(label: object) -> str:
    require(isinstance(label, str) and 1 <= len(label) <= 96
            and label not in (".", "..")
            and all(item in "abcdefghijklmnopqrstuvwxyz0123456789-_" for item in label),
            "require a fresh, safe lowercase reference-run label")
    return label


def read_result(path: str) -> tuple[dict[str, object], dict[str, object]]:
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | getattr(os, "O_NOFOLLOW", 0))
    pieces: list[bytes] = []
    total = 0
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode) and identity.st_nlink == 1
                and 0 < identity.st_size <= MAXIMUM_RESULT,
                "reject incomplete or excessive genuine worker result")
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            total += len(chunk)
            require(total <= MAXIMUM_RESULT, "reject oversized genuine worker result")
            pieces.append(chunk)
    finally:
        os.close(descriptor)
    raw = b"".join(pieces)
    require(len(raw) == identity.st_size, "reject truncated genuine worker result")
    parsed = decode(raw)
    require(isinstance(parsed, dict), "reject malformed genuine worker result")
    return parsed, {"path": path, "sha256": hashlib.sha256(raw).hexdigest(),
                    "bytes": len(raw), "device": identity.st_dev,
                    "inode": identity.st_ino, "mode": "%04o" % stat.S_IMODE(identity.st_mode)}


def publish(directory: str, name: str, document: dict[str, object]) -> dict[str, object]:
    target = os.path.join(directory, name)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(target, flags, 0o600)
    raw = canonical(document) + b"\n"
    try:
        written = 0
        while written < len(raw):
            count = os.write(descriptor, raw[written:])
            require(count > 0, "reject incomplete exclusive evidence publication")
            written += count
        os.fsync(descriptor)
        identity = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    directory_fd = os.open(directory, os.O_RDONLY | os.O_CLOEXEC
                           | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    return {"path": target, "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw), "device": identity.st_dev,
            "inode": identity.st_ino, "mode": "0600"}


def start_worker(role: str, result_path: str) -> dict[str, object]:
    stdout_read, stdout_write = os.pipe2(os.O_CLOEXEC)
    stderr_read, stderr_write = os.pipe2(os.O_CLOEXEC)
    try:
        actions = [
            (os.POSIX_SPAWN_DUP2, stdout_write, 1),
            (os.POSIX_SPAWN_DUP2, stderr_write, 2),
            (os.POSIX_SPAWN_CLOSE, stdout_read),
            (os.POSIX_SPAWN_CLOSE, stderr_read),
        ]
        command = [PYTHON, "-I", "-B", ROOT + "/" + ORIGINAL[0],
                   "verify", "--module", "re", "--output", result_path]
        environment = {"PATH": "/usr/bin:/bin", "LC_ALL": "C",
                       "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"}
        pid = os.posix_spawn(PYTHON, command, environment, file_actions=actions)
    except BaseException:
        for descriptor in (stdout_read, stdout_write, stderr_read, stderr_write):
            try:
                os.close(descriptor)
            except OSError:
                pass
        raise
    os.close(stdout_write)
    os.close(stderr_write)
    os.set_blocking(stdout_read, False)
    os.set_blocking(stderr_read, False)
    return {"role": role, "pid": pid, "command": command,
            "result_path": result_path, "stdout_fd": stdout_read,
            "stderr_fd": stderr_read, "stdout": bytearray(),
            "stderr": bytearray()}


def drain_workers(workers: list[dict[str, object]]) -> None:
    select_module = builtins.__import__("select")
    poller = select_module.poll()
    descriptors: dict[int, tuple[dict[str, object], str]] = {}
    for worker in workers:
        for kind in ("stdout", "stderr"):
            descriptor = worker[kind + "_fd"]
            require(isinstance(descriptor, int), "require genuine worker pipe")
            descriptors[descriptor] = (worker, kind)
            poller.register(descriptor, select_module.POLLIN
                            | select_module.POLLHUP | select_module.POLLERR)
    while descriptors:
        ready = poller.poll(30000)
        require(ready, "reject a stalled genuine reference worker")
        for descriptor, _events in ready:
            if descriptor not in descriptors:
                continue
            worker, kind = descriptors[descriptor]
            try:
                piece = os.read(descriptor, 65536)
            except BlockingIOError:
                continue
            if piece:
                stream = worker[kind]
                require(isinstance(stream, bytearray), "require observed worker stream")
                require(len(stream) + len(piece) <= MAXIMUM_STREAM,
                        "reject oversized worker stdout or stderr")
                stream.extend(piece)
            else:
                poller.unregister(descriptor)
                os.close(descriptor)
                del descriptors[descriptor]


def genuine_references(options: dict[str, object], contract: dict[str, object]) -> dict[str, object]:
    require("--label" in options, "require a fresh explicit real-reference label")
    label = validate_label(options["--label"])
    directory = os.path.join(ROOT, "oracle/phase1/evidence",
                             "differential-fuzz-reference-v3-" + label)
    os.mkdir(directory, 0o700)
    workers: list[dict[str, object]] = []
    status = "FAIL"
    try:
        for index, role in enumerate(("independent-reference-a", "independent-reference-b")):
            output = os.path.join(directory, "reference-" + str(index + 1) + ".json")
            workers.append(start_worker(role, output))
            require(len({item["pid"] for item in workers}) == len(workers),
                    "reject invented or duplicated genuine reference PID")
        drain_workers(workers)
        observations: list[dict[str, object]] = []
        for worker in workers:
            pid = worker["pid"]
            require(isinstance(pid, int) and pid > 0, "reject a non-genuine worker PID")
            observed_pid, wait_status = os.waitpid(pid, 0)
            require(observed_pid == pid, "reject crossed real worker wait result")
            parsed, output_owner = read_result(str(worker["result_path"]))
            stdout = bytes(worker["stdout"])
            stderr = bytes(worker["stderr"])
            require(parsed.get("schema") == "rebar-correctness-result-v2"
                    and parsed.get("module") == "re"
                    and parsed.get("cases") == 8244
                    and parsed.get("obligations") == 45
                    and parsed.get("mapped_obligations") == 45
                    and parsed.get("expected_sha256") == CORPUS[1]
                    and isinstance(parsed.get("failures"), list),
                    "reject incomplete original Python worker result")
            failures = parsed["failures"]
            require(parsed.get("failed") == len(failures)
                    and parsed.get("passed") + len(failures) == 8244,
                    "reject unaccounted original Python case or failure")
            observations.append({
                "role": worker["role"], "pid": pid,
                "exit_code": os.waitstatus_to_exitcode(wait_status),
                "result": output_owner,
                "result_schema": parsed["schema"],
                "module": parsed["module"], "case_count": parsed["cases"],
                "passed": parsed["passed"], "failed": parsed["failed"],
                "failures": failures,
                "stdout": {"bytes": len(stdout),
                           "sha256": hashlib.sha256(stdout).hexdigest(),
                           "text": stdout.decode("utf-8", "replace")},
                "stderr": {"bytes": len(stderr),
                           "sha256": hashlib.sha256(stderr).hexdigest(),
                           "text": stderr.decode("utf-8", "replace")},
            })
        status = "PASS" if all(item["exit_code"] == 0
                               and item["passed"] == 8244
                               and item["failed"] == 0
                               for item in observations) else "FAIL"
        record = {
            "schema": SCHEMA + "-actual-reference",
            "status": status, "label": label,
            "source_sha256": contract["source"]["sha256"],
            "protocol_sha256": contract["protocol"]["sha256"],
            "pinned_cpython": contract["pinned_cpython"],
            "p0_completeness_v2": contract["p0_completeness_v2"],
            "original_case_execution_denominator": 31237,
            "supplemental_case_count": 8244,
            "case_denominator_included_in_original_31237": False,
            "corpus_sha256": CORPUS[1],
            "record_kind_counts": KINDS, "frozen_seeds": FIXED_SEEDS,
            "mapped_obligation_count": 45,
            "actual_reference_worker_count": len(observations),
            "actual_reference_worker_process_ids": [item["pid"] for item in observations],
            "workers": observations,
            "candidate_status": "NOT RUN", "actual_candidate_worker_count": 0,
            "candidate_qualified": False, "qualified_candidate_count": 0,
            "native_build_status": "NOT RUN", "holdout": "NOT OPENED",
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "winner_selected": False,
        }
        evidence = publish(directory, "two-independent-reference-result.json", record)
        return {"schema": SCHEMA + "-actual-publication", "status": status,
                "reference_status": status,
                "actual_reference_worker_count": len(observations),
                "actual_reference_worker_process_ids": [item["pid"] for item in observations],
                "case_count_per_worker": 8244,
                "total_reference_case_executions": 16488,
                "actual_candidate_worker_count": 0,
                "holdout": "NOT OPENED", "performance": "NOT MEASURED",
                "evidence": evidence}
    except BaseException as error:
        for worker in workers:
            for kind in ("stdout", "stderr"):
                descriptor = worker.get(kind + "_fd")
                if isinstance(descriptor, int):
                    try:
                        os.close(descriptor)
                    except OSError:
                        pass
            pid = worker.get("pid")
            if isinstance(pid, int):
                try:
                    os.kill(pid, 15)
                except (OSError, ProcessLookupError):
                    pass
                try:
                    os.waitpid(pid, 0)
                except (OSError, ChildProcessError):
                    pass
        failure = {"schema": SCHEMA + "-actual-controller-failure",
                   "status": "FAIL", "label": label,
                   "error_type": type(error).__name__, "error_message": str(error),
                   "attempted_reference_worker_count": len(workers),
                   "actual_reference_worker_process_ids": [
                       worker["pid"] for worker in workers if isinstance(worker.get("pid"), int)],
                   "preserved_directory": directory,
                   "candidate_status": "NOT RUN", "actual_candidate_worker_count": 0,
                   "holdout": "NOT OPENED", "performance": "NOT MEASURED"}
        try:
            published = publish(directory, "two-independent-reference-controller-failure.json",
                                failure)
            failure["failure_evidence"] = published
        except (OSError, ReferenceError):
            pass
        os.write(2, canonical(failure) + b"\n")
        raise


def main(argv: list[str]) -> int:
    options = arguments(argv)
    if options["mode"] in ("--render-contract", "--render-contract-preview"):
        require("--contract-sha256" not in options and "--label" not in options,
                "render mode must not supply a result hash or start a worker")
        document = reconstruct(str(options["--source-sha256"]),
                               str(options["--protocol-sha256"]))
        if options["mode"] == "--render-contract-preview":
            source_wall()
            os.write(1, canonical(document) + b"\n")
            return 0
        publication = publish(os.path.join(ROOT, "oracle/phase1"),
                              "p0-differential-fuzz-reference-v3.json", document)
        source_wall()
        os.write(1, canonical({"schema": SCHEMA + "-contract-render", "status": "PASS",
                               "reference_status": "NOT RUN",
                               "phase_gate_status": "BLOCKED",
                               "actual_reference_worker_count": 0,
                               "contract": publication}) + b"\n")
        return 0
    contract = checked_contract(options)
    if options["mode"] == "--self-test":
        require("--label" not in options, "source self-test must not run a worker")
        result = source_self_test(contract)
    elif options["mode"] == "--verify-frozen-context":
        require("--label" not in options, "source verification must not run a worker")
        source_wall()
        result = {"schema": SCHEMA + "-frozen-context", "status": "PASS",
                  "reference_status": "NOT RUN", "phase_gate_status": "BLOCKED",
                  "phase1_canonical_candidate_context_crosswalk": "PASS",
                  "original_case_execution_denominator": 31237,
                  "supplemental_case_count": 8244,
                  "mapped_obligation_count": 45,
                  "case_kind_count": 19,
                  "authenticated_inherited_source_owner_count":
                      contract["authenticated_inherited_source_owner_count"],
                  "source_only_effects": effects()}
    else:
        result = genuine_references(options, contract)
    os.write(1, canonical(result) + b"\n")
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except ReferenceError as error:
        os.write(2, canonical({"schema": SCHEMA + "-error", "status": "FAIL",
                               "error": str(error)}) + b"\n")
        raise SystemExit(2)
