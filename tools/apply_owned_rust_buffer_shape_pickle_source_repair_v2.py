#!/usr/bin/env python3
"""Authenticate a first-party Rust buffer-lifetime repair without running it."""

from __future__ import annotations

import sys

if "re" in sys.modules or "_sre" in sys.modules:
    raise SystemExit("source-only Rust verification must not import a regex engine")

import builtins
import hashlib
import os
import stat

ROOT = "/home/dev-user/src/rebar"
SOURCE = "tools/apply_owned_rust_buffer_shape_pickle_source_repair_v2.py"
PROTOCOL = "oracle/phase2/RUST-BUFFER-SHAPE-PICKLE-SOURCE-REPAIR-V2.md"
CONTRACT = "oracle/phase2/rust-buffer-shape-pickle-source-repair-v2.json"
VARIANT = "candidates/rust/variants/buffer_shape_pickle_v2/py_bridge.c"
SCHEMA = "rebar-phase2-owned-rust-buffer-shape-pickle-source-repair-v2-source-freeze"
VARIANT_SHA256 = "afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740"
VARIANT_BYTES = 179961
VARIANT_DEVICE = 2064
VARIANT_INODE = 525057
OUTSIDE_FUNCTION_SHA256 = "1a4e1713e2ea2dd6a42d56baac4e66907392b1971b94a1f5007fecab5c25830b"
MAX_OWNER_BYTES = 4 * 1024 * 1024
MAX_JSON_DEPTH = 64
NOT_PROJECTED = "NOT MEASURED FROM THE RETAINED SINGLE-READ FORENSIC PROJECTION"

# Each owner was frozen before this repair. The compressed failure archive is
# deliberately absent: this verifier never opens or inflates it.
OWNERS = (
    ("goal", "GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756, 2064, 31364044),
    ("tested_rust_bridge", "candidates/rust/variants/buffer_shape_pickle_v1/py_bridge.c", "00271ad5fff71e2f2e30cda6b446a61d0c300cb91eec2091b8ada17662d9a335", 181004, 2064, 524972),
    ("previous_graph_source", "tools/render_candidate_current_overview_v58.py", "98658308205a0dc25e1bf7cc5d8295408f248c1e4fdf62e1dee5782decb82c70", 119240, 2064, 432117),
    ("previous_graph_inputs", "docs/evidence/candidate-current-overview-v58.inputs.json", "3c58f7aa410ce287e1a718a2eb93e5cf9c7b6121bd1f0d404fbc7e67c9f6fd30", 892497, 2064, 432118),
    ("previous_graph_summary", "docs/evidence/candidate-current-overview-v58.json", "5d94286c55bce81a2b12fb54b39cb04e543cdad2588e21f3a13ade3adb03fd9a", 2426500, 2064, 432120),
    ("previous_graph_svg", "docs/evidence/candidate-current-overview-v58.svg", "25477c207348b7cdfee3aa24071b27354f31553fde55033dc7eff5852e81e04d", 14539, 2064, 432121),
    ("failure_publication_receipt", "oracle/phase2/evidence/repaired-rust-original-campaign-v10-rust-phase2-v16-rust-buffer-shape-pickle-original-p0-v10-failures-publication-receipt.json", "8735e5351f62de2a77369eb8401e225cebd31434b09f07db40e79550ba7cc7d2", 6708, 2064, 525044),
    ("independent_failure_forensics", "oracle/phase2/evidence/repaired-rust-original-campaign-v10-rust-phase2-v16-rust-buffer-shape-pickle-original-p0-v10-failures-forensic-summary.json", "6e04771a48b4a460ad58ac9795ef91a697a33fa0aeae4671c9b3c9b35e4820cd", 24701, 2064, 525045),
)

SUITES = (
    ("original_bounded_v5", 151, 0, 151, 81),
    ("public_v3", 864, 0, 864, 87),
    ("scanner_v3", 1024, 0, 1024, 88),
    ("buffer_v3", 768, 0, 768, 89),
    ("managed_v1", 1024, 16, 0, 90),
    ("scanner_verbose_v1", 2854, 0, 2854, 91),
    ("public_types_v1", 6912, 0, 6912, 92),
    ("substitution_v2", 5120, 368, 0, 93),
    ("shape_v2", 10240, 1056, 0, 94),
    ("public_surface_v19", 1376, 0, 1376, 95),
    ("subinterpreter_v2", 128, 0, 128, 196),
    ("pep688_v4", 264, 0, 264, 197),
    ("threaded_pattern_v1", 512, 0, 512, 198),
)

WITNESSES = (
    ("managed_v1", "managed-buffer-lifetime.v1.0453", True, True),
    ("managed_v1", "managed-buffer-lifetime.v1.0454", True, True),
    ("substitution_v2", "substitution-buffer-semantics.v1.03521", False, True),
    ("substitution_v2", "substitution-buffer-semantics.v1.03522", False, True),
    ("shape_v2", "shape-changing-buffer-semantics.v1.00020", False, False),
    ("shape_v2", "shape-changing-buffer-semantics.v1.00021", False, False),
)

SNAPSHOT_DECLARATION = b"    PyObject *subject_snapshot = NULL;\n"
SNAPSHOT_BLOCK = (
    b"    if (!callback && subject.view.obj != NULL) {\n"
    b"        if (subject.length > (size_t)PY_SSIZE_T_MAX) {\n"
    b"            rust_subject_release(&subject);\n"
    b"            return PyErr_NoMemory();\n"
    b"        }\n"
    b"        subject_snapshot = PyBytes_FromStringAndSize(\n"
    b"            (const char *)subject.data, (Py_ssize_t)subject.length\n"
    b"        );\n"
    b"        if (subject_snapshot == NULL) {\n"
    b"            rust_subject_release(&subject);\n"
    b"            return NULL;\n"
    b"        }\n"
    b"        rust_subject_release(&subject);\n"
    b"        if (!rust_subject_open(&subject, pattern_value, subject_snapshot, 1)) {\n"
    b"            rust_subject_release(&subject);\n"
    b"            Py_DECREF(subject_snapshot);\n"
    b"            return NULL;\n"
    b"        }\n"
    b"    }\n"
)


class FreezeError(Exception):
    """The source-only freeze failed closed."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise FreezeError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def quote(value: str) -> str:
    require(type(value) is str, "JSON object keys must be strings")
    short = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f", "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    result = ['"']
    for char in value:
        point = ord(char)
        require(not 0xD800 <= point <= 0xDFFF, "unpaired Unicode surrogate")
        result.append(short.get(char, "\\u" + format(point, "04x") if point < 32 else char))
    result.append('"')
    return "".join(result)


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= MAX_JSON_DEPTH, "JSON nesting exceeds its frozen bound")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is str:
        return quote(value)
    if type(value) is int:
        return str(value)
    if type(value) is float:
        require(value == value and abs(value) != float("inf"), "nonfinite JSON number")
        return repr(value)
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value), "JSON object keys must be strings")
        return "{" + ",".join(quote(key) + ":" + canonical(value[key], depth + 1) for key in sorted(value)) + "}"
    raise FreezeError("unsupported JSON value")


class StrictJSON:
    """Read bounded JSON without importing json, re, or a matching engine."""

    def __init__(self, raw: bytes):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_OWNER_BYTES, "JSON input is not bounded")
        try:
            self.text = raw.decode("utf-8", "strict")
        except UnicodeError as error:
            raise FreezeError("JSON must be valid UTF-8") from error
        self.index = 0

    def whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def string(self) -> str:
        require(self.text[self.index:self.index + 1] == '"', "JSON string required")
        self.index += 1
        result: list[str] = []
        short = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
        while self.index < len(self.text):
            char = self.text[self.index]
            self.index += 1
            if char == '"':
                return "".join(result)
            if char != "\\":
                require(ord(char) >= 32 and not 0xD800 <= ord(char) <= 0xDFFF, "invalid JSON character")
                result.append(char)
                continue
            require(self.index < len(self.text), "incomplete JSON escape")
            char = self.text[self.index]
            self.index += 1
            if char != "u":
                require(char in short, "invalid JSON escape")
                result.append(short[char])
                continue
            digits = self.text[self.index:self.index + 4]
            require(len(digits) == 4 and all(item in "0123456789abcdefABCDEF" for item in digits), "invalid Unicode escape")
            self.index += 4
            point = int(digits, 16)
            if 0xD800 <= point <= 0xDBFF:
                require(self.text[self.index:self.index + 2] == "\\u", "unpaired high surrogate")
                lower = self.text[self.index + 2:self.index + 6]
                require(len(lower) == 4 and all(item in "0123456789abcdefABCDEF" for item in lower), "invalid low surrogate")
                low = int(lower, 16)
                require(0xDC00 <= low <= 0xDFFF, "unpaired high surrogate")
                self.index += 6
                result.append(chr(0x10000 + ((point - 0xD800) << 10) + low - 0xDC00))
            else:
                require(not 0xDC00 <= point <= 0xDFFF, "unpaired low surrogate")
                result.append(chr(point))
        raise FreezeError("unterminated JSON string")

    def number(self) -> int | float:
        start = self.index
        if self.text[self.index:self.index + 1] == "-":
            self.index += 1
        require(self.index < len(self.text), "incomplete JSON number")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index == len(self.text) or self.text[self.index] not in "0123456789", "leading zero")
        else:
            require(self.text[self.index] in "123456789", "invalid JSON number")
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
        floating = False
        if self.text[self.index:self.index + 1] == ".":
            floating = True
            self.index += 1
            begin = self.index
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
            require(self.index > begin, "incomplete JSON fraction")
        if self.text[self.index:self.index + 1] in ("e", "E"):
            floating = True
            self.index += 1
            if self.text[self.index:self.index + 1] in ("+", "-"):
                self.index += 1
            begin = self.index
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
            require(self.index > begin, "incomplete JSON exponent")
        token = self.text[start:self.index]
        require(len(token) <= 128, "JSON number exceeds the frozen bound")
        if not floating:
            return int(token)
        value = float(token)
        require(value == value and abs(value) != float("inf"), "nonfinite JSON number")
        return value

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "JSON nesting exceeds its frozen bound")
        self.whitespace()
        require(self.index < len(self.text), "missing JSON value")
        char = self.text[self.index]
        if char == '"':
            return self.string()
        if char == "{":
            self.index += 1
            result: dict[str, object] = {}
            self.whitespace()
            if self.text[self.index:self.index + 1] == "}":
                self.index += 1
                return result
            while True:
                self.whitespace()
                key = self.string()
                require(key not in result, "duplicate JSON object key: " + key)
                self.whitespace()
                require(self.text[self.index:self.index + 1] == ":", "missing JSON colon")
                self.index += 1
                result[key] = self.value(depth + 1)
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "}":
                    return result
                require(separator == ",", "invalid JSON object separator")
        if char == "[":
            self.index += 1
            result_list: list[object] = []
            self.whitespace()
            if self.text[self.index:self.index + 1] == "]":
                self.index += 1
                return result_list
            while True:
                result_list.append(self.value(depth + 1))
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "]":
                    return result_list
                require(separator == ",", "invalid JSON array separator")
        if char == "-" or char in "0123456789":
            return self.number()
        for literal, result in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(literal, self.index):
                self.index += len(literal)
                return result
        raise FreezeError("invalid JSON literal")

    def decode(self) -> object:
        result = self.value()
        self.whitespace()
        require(self.index == len(self.text), "trailing JSON content")
        return result


_BLOCKED_EVENTS: dict[str, int] = {}
_ALLOWED_PATHS = frozenset(
    [ROOT + "/" + SOURCE, ROOT + "/" + PROTOCOL, ROOT + "/" + CONTRACT, ROOT + "/" + VARIANT]
    + [ROOT + "/" + path for _name, path, _sha, _size, _dev, _ino in OWNERS]
)


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    if event == "open":
        path = arguments[0] if arguments else None
        flags = arguments[2] if len(arguments) > 2 else None
        forbidden = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND | getattr(os, "O_TMPFILE", 0)
        if type(path) is str and path in _ALLOWED_PATHS and not path.endswith(".gz") and type(flags) is int and not flags & forbidden:
            return
    elif (
        event in {"import", "exec", "compile", "os.system", "os.rename", "os.remove", "os.mkdir", "os.rmdir", "os.chmod", "os.chown", "os.fork", "os.posix_spawn", "marshal.loads", "code.__new__", "function.__new__"}
        or event.startswith(("ctypes.", "subprocess.", "socket.", "multiprocessing.", "threading.", "tempfile.", "time.", "os.exec"))
    ):
        pass
    else:
        return
    _BLOCKED_EVENTS[event] = _BLOCKED_EVENTS.get(event, 0) + 1
    raise FreezeError("source-only audit wall rejected " + event)


def no_engine_imports() -> None:
    require("re" not in sys.modules and "_sre" not in sys.modules, "a Python regex engine was imported")
    require(not any(name == "rebar" or name.startswith("rebar.") or name == "candidates" or name.startswith("candidates.") for name in sys.modules), "a candidate or public entry point was imported")


def read_exact(path: str, expected_hash: str, expected_size: int | None = None, expected_device: int | None = None, expected_inode: int | None = None) -> bytes:
    absolute = ROOT + "/" + path
    require(absolute in _ALLOWED_PATHS and not absolute.endswith(".gz"), "unlisted or compressed owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(absolute, flags)
    except OSError as error:
        raise FreezeError("cannot open frozen source owner: " + path) from error
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, "owner is not a private regular file: " + path)
        require(0 < before.st_size <= MAX_OWNER_BYTES, "source owner exceeds its frozen bound: " + path)
        require(expected_size is None or before.st_size == expected_size, "source owner size changed: " + path)
        require(expected_device is None or before.st_dev == expected_device, "source owner device changed: " + path)
        require(expected_inode is None or before.st_ino == expected_inode, "source owner inode changed: " + path)
        parts: list[bytes] = []
        total = 0
        while True:
            part = os.read(descriptor, min(262144, before.st_size + 1 - total))
            if not part:
                break
            total += len(part)
            require(total <= before.st_size, "source owner grew during its single read: " + path)
            parts.append(part)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    require(total == before.st_size, "source owner changed during its single read: " + path)
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns, before.st_nlink) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns, after.st_nlink), "source owner identity changed during its single read: " + path)
    result = b"".join(parts)
    require(digest(result) == expected_hash, "source owner SHA-256 changed: " + path)
    return result


def split_function(raw: bytes) -> tuple[bytes, bytes, bytes]:
    begin = b"static PyObject *rust_substitute_core("
    ending = b"static PyObject *rust_bound_substitute("
    require(raw.count(begin) == 1 and raw.count(ending) == 1, "the real substitution function is missing or repeated")
    start = raw.index(begin)
    finish = raw.index(ending, start)
    return raw[:start], raw[start:finish], raw[finish:]


def derive_variant(original: bytes) -> bytes:
    require(digest(original) == OWNERS[1][2] and len(original) == OWNERS[1][3], "the actually tested Rust bridge changed")
    before, function, after = split_function(original)
    require(digest(before + after) == OUTSIDE_FUNCTION_SHA256, "source outside the substitution function changed")
    require(function.count(SNAPSHOT_DECLARATION) == 1, "the historical snapshot declaration is missing or repeated")
    require(function.count(SNAPSHOT_BLOCK) == 1, "the historical premature snapshot block is missing or repeated")
    require(function.count(b"Py_XDECREF(subject_snapshot);") == 8, "the eight historical snapshot cleanups changed")
    corrected = function.replace(SNAPSHOT_DECLARATION, b"", 1).replace(SNAPSHOT_BLOCK, b"", 1)
    pieces = corrected.splitlines(keepends=True)
    cleanup = [line for line in pieces if line.strip() == b"Py_XDECREF(subject_snapshot);"]
    require(len(cleanup) == 8, "the snapshot cleanup lines are missing or repeated")
    corrected = b"".join(line for line in pieces if line.strip() != b"Py_XDECREF(subject_snapshot);")
    require(b"subject_snapshot" not in corrected, "the premature bytes snapshot survives")
    require(corrected.count(b"rust_subject_open(&subject, pattern_value, value, 1)") == 1, "the live original exporter must be opened once")
    require(corrected.count(b"rust_subject_release(&subject);") == 8, "live exporter cleanup must remain balanced on all eight exits")
    require(corrected.count(b"int callback = PyCallable_Check(replacement);") == 1, "callback handling changed")
    require(corrected.count(b"rust_match_allocate(pattern, value, groupindex, groups, 0, (Py_ssize_t)subject.length)") == 2, "match objects no longer retain the real original subject")
    result = before + corrected + after
    require(len(result) == VARIANT_BYTES and digest(result) == VARIANT_SHA256, "the corrected first-party bridge is not the exact frozen derivation")
    return result


def validate_graph(raw: bytes) -> None:
    require(digest(raw) == OWNERS[4][2] and len(raw) == OWNERS[4][3], "the previous headline graph is not frozen V58")
    for marker in (
        b'"schema":"rebar-candidate-current-overview-v58-summary"',
        b'"actual_rust_v10_candidate_status":"FAIL"',
        b'"actual_rust_v10_semantic_mismatch_count":1440',
        b'"actual_rust_v10_verified_passing_case_count":14853',
        b'"actual_rust_v10_distinct_worker_process_id_count":13',
        b'"actual_rust_semantic_mismatch_count":928',
        b'"qualified_candidate_count":0',
        b'"performance":"NOT MEASURED"',
    ):
        require(marker in raw, "the frozen previous graph omitted a genuine historical or current result")


def validate_forensics(value: object) -> dict[str, object]:
    require(type(value) is dict, "failure forensics must be an object")
    data = value
    require(data.get("schema") == "rebar-owned-repaired-rust-original-campaign-v10-failures-forensic-summary-v1", "wrong independent forensic schema")
    require(data.get("status") == "PASS" and data.get("analysis_status") == "PASS", "the independent analysis did not pass")
    require(data.get("candidate_status") == "FAIL" and data.get("candidate_qualified") is False, "analysis or publication was misreported as candidate correctness")
    require(data.get("qualified_candidate_count") == 0 and data.get("from_scratch_candidate_family_count") == 6, "candidate counts changed")
    for key, expected in (("performance", "NOT MEASURED"), ("memory", "NOT MEASURED"), ("confidence_intervals", "NOT MEASURED"), ("undefined_behavior", "NOT MEASURED"), ("holdout", "NOT OPENED"), ("runtime_non_delegation", "NOT ESTABLISHED"), ("winner_selected", False)):
        require(data.get(key) == expected, "an unmeasured result or independence claim was invented: " + key)
    totals = data.get("actual_result_totals")
    require(type(totals) is dict, "missing actual failure totals")
    for key, expected in (("suite_count", 13), ("case_execution_denominator", 31237), ("named_private_waiver_count", 13), ("attempted_suite_count", 13), ("started_suite_count", 13), ("completed_suite_count", 13), ("actual_candidate_workers", 13), ("distinct_worker_process_id_count", 13), ("duplicate_worker_process_id_count", 0), ("missing_worker_process_id_count", 0), ("all_original_observation_vectors_complete", True), ("missing_original_case_observations", 0), ("semantic_mismatch_count", 1440), ("verified_passing_case_count", 14853), ("verified_passing_cases_derived_by_subtraction", False), ("records_from_fully_observed_failed_suites_are_counted_as_passing", False), ("infrastructure_failure_count", 0), ("candidate_status", "FAIL"), ("candidate_qualified", False)):
        require(totals.get(key) == expected, "the complete actual candidate failure changed: " + key)
    expected_processes = [row[4] for row in SUITES]
    require(totals.get("actual_worker_process_ids") == expected_processes, "genuine worker identities changed")
    rows = data.get("suite_results")
    require(type(rows) is list and len(rows) == len(SUITES), "an original suite was missing, repeated, or reordered")
    for actual, expected in zip(rows, SUITES, strict=True):
        require(type(actual) is dict, "an original suite observation is malformed")
        suite, cases, mismatches, passes, pid = expected
        require((actual.get("suite"), actual.get("case_execution_denominator"), actual.get("semantic_mismatch_count"), actual.get("explicitly_verified_passing_case_count"), actual.get("actual_worker_process_id")) == (suite, cases, mismatches, passes, pid), "an actual suite observation changed: " + suite)
        require(actual.get("fully_observed") is True and actual.get("actual_worker_started") is True, "a placeholder was substituted for a genuine worker: " + suite)
        require(actual.get("failure_class") == ("SEMANTIC MISMATCH" if mismatches else "PASS"), "suite pass or failure was invented: " + suite)
        require(actual.get("candidate_record_count") == cases + (1 if suite == "original_bounded_v5" else 0), "suite case observations changed: " + suite)
        if suite == "original_bounded_v5":
            require(actual.get("debug_build_skip_count") == 1, "the named CPython debug-only observation changed")
    require(sum(item[1] for item in SUITES) == 31237 and sum(item[2] for item in SUITES) == 1440 and sum(item[3] for item in SUITES) == 14853, "original denominators or verified-pass accounting changed")
    history = data.get("historical_comparison")
    require(type(history) is dict, "missing historical comparison")
    for key, expected in (("previous_actual_rust_semantic_mismatch_count", 928), ("previous_actual_rust_explicitly_verified_passing_case_count", 8965), ("new_actual_rust_semantic_mismatch_count", 1440), ("new_actual_rust_explicitly_verified_passing_case_count", 14853), ("semantic_mismatch_regression", 512), ("regression_derived_from_complete_mismatch_vectors", True), ("passing_cases_derived_by_subtraction", False)):
        require(history.get(key) == expected, "previous and current Rust results were confused: " + key)
    root = data.get("first_party_semantic_root_cause")
    require(type(root) is dict, "missing independently established first-party root cause")
    require(root.get("source_path") == OWNERS[1][1] and root.get("source_sha256") == OWNERS[1][2] and root.get("source_bytes") == OWNERS[1][3] and root.get("function") == "rust_substitute_core", "the failure was not attributed to the actually tested source")
    require(root.get("affected_genuine_suite_mismatches") == {"managed_v1": 16, "substitution_v2": 368, "shape_v2": 1056}, "genuine buffer failures changed")
    witnesses = data.get("earliest_genuine_mismatch_witnesses")
    require(type(witnesses) is list and len(witnesses) == len(WITNESSES), "a real mismatch witness was missing, repeated, or reordered")
    for actual, expected in zip(witnesses, WITNESSES, strict=True):
        require(type(actual) is dict, "a real mismatch witness is malformed")
        suite, case, expected_complete, actual_complete = expected
        require((actual.get("suite"), actual.get("case"), actual.get("expected_events_complete"), actual.get("actual_events_complete")) == (suite, case, expected_complete, actual_complete), "real mismatch evidence changed: " + case)
        require(actual.get("return_value_matches_reference") is True, "buffer event failures were confused with result-value failures: " + case)
        if expected_complete:
            events = actual.get("expected_events")
            observed = actual.get("actual_events")
            sequence = ("acquire", "acquire", "release", "release") if case.endswith("0453") else ("acquire", "acquire", "release", "acquire", "release", "release")
            require(type(events) is list and tuple(item.get("event") for item in events) == sequence, "a complete original buffer event vector changed: " + case)
            require(type(observed) is list and tuple(item.get("event") for item in observed) == ("acquire", "release"), "the observed premature exporter release changed: " + case)
            require(all(item.get("role") == "subject" for item in events + observed), "buffer event roles were fabricated: " + case)
        else:
            require(actual.get("expected_events") == NOT_PROJECTED, "an unobserved expected event vector was fabricated: " + case)
        if not actual_complete:
            require(actual.get("actual_events") == NOT_PROJECTED, "an unobserved shape-changing event vector was fabricated: " + case)
        elif not expected_complete:
            require(type(actual.get("actual_events")) is list, "a genuinely observed replacement event vector was dropped: " + case)
    require(data.get("resulting_authenticated_evidence_owner_lower_bound") == 197 and data.get("resulting_authenticated_history_reference_lower_bound") == 202, "previous evidence lower bounds changed")
    boundary = data.get("recovery_and_boundary_effects")
    require(type(boundary) is dict and boundary.get("all_four_original_targets_restored") is True and boundary.get("hidden_cases_read") == 0 and boundary.get("benchmark_files_read") == 0 and boundary.get("clock_samples") == 0 and boundary.get("timing_trials_run") == 0, "the original campaign boundary changed")
    return data


def validate_receipt(value: object, forensics: dict[str, object]) -> dict[str, object]:
    require(type(value) is dict, "durable publication receipt must be an object")
    receipt = value
    require(receipt.get("schema") == "rebar-owned-repaired-rust-original-campaign-v10-durable-publication-receipt", "wrong publication receipt schema")
    require(receipt.get("status") == "PASS" and receipt.get("candidate_status") == "FAIL" and receipt.get("candidate_qualified") is False, "publication was confused with a passing candidate")
    for key, expected in (("suite_count", 13), ("case_execution_denominator", 31237), ("named_private_waiver_count", 13), ("semantic_mismatch_count", 1440), ("verified_passing_case_count", 14853), ("actual_candidate_workers", 13), ("distinct_worker_process_id_count", 13), ("holdout", "NOT OPENED"), ("performance", "NOT MEASURED"), ("memory", "NOT MEASURED"), ("benchmark_files_read", 0), ("clock_samples", 0)):
        require(receipt.get(key) == expected, "the actual publication receipt changed: " + key)
    require(receipt.get("actual_worker_process_ids") == [row[4] for row in SUITES], "published genuine worker identities changed")
    archive = receipt.get("archive")
    previous = forensics.get("failure_archive")
    require(type(archive) is dict and type(previous) is dict, "missing authenticated failure archive description")
    for first, second in (("sha256", "sha256"), ("size_bytes", "bytes"), ("device", "device"), ("inode", "inode")):
        require(archive.get(first) == previous.get(second), "failure archive metadata disagrees without reopening it: " + first)
    require(archive.get("sha256") == "4be5a40ca3cdb0323eeb613a80c8eb22509dcbc21423156abbf0961fef19405e" and archive.get("size_bytes") == 3746528 and archive.get("device") == 2064 and archive.get("inode") == 525043, "the historical single-read failure archive was replaced")
    require(receipt.get("uncompressed_sha256") == previous.get("uncompressed_sha256") == "9e077ed42b0d092d0a53a640561a32ce4e4ab15d53ac2fa5c22d19c2664d4893" and receipt.get("uncompressed_bytes") == previous.get("uncompressed_bytes") == 5385134, "historical archive contents were misattributed")
    publication = forensics.get("durable_publication_receipt")
    require(type(publication) is dict and publication.get("sha256") == OWNERS[6][2] and publication.get("candidate_status") == "FAIL", "independent analysis did not authenticate this exact failed-candidate receipt")
    return receipt


def load_context() -> tuple[dict[str, bytes], dict[str, object], dict[str, object]]:
    observed: dict[str, bytes] = {}
    for label, path, sha, size, device, inode in OWNERS:
        observed[label] = read_exact(path, sha, size, device, inode)
    actual_variant = read_exact(VARIANT, VARIANT_SHA256, VARIANT_BYTES, VARIANT_DEVICE, VARIANT_INODE)
    expected_variant = derive_variant(observed["tested_rust_bridge"])
    require(actual_variant == expected_variant, "the complete corrected bridge was not derived from the actually tested failure")
    before, function, after = split_function(actual_variant)
    require(digest(before + after) == OUTSIDE_FUNCTION_SHA256 and b"subject_snapshot" not in function, "source outside the targeted buffer-lifetime repair changed")
    for marker in (b'PyImport_ImportModule("re")', b'PyImport_ImportModule("_sre")', b'PyImport_ImportModule("regex")', b"#include <regex.h>", b"#include <pcre"):
        require(marker not in actual_variant, "the first-party repair added external or Python regex delegation")
    validate_graph(observed["previous_graph_summary"])
    forensics = validate_forensics(StrictJSON(observed["independent_failure_forensics"]).decode())
    receipt = validate_receipt(StrictJSON(observed["failure_publication_receipt"]).decode(), forensics)
    observed["corrected_rust_bridge"] = actual_variant
    return observed, forensics, receipt


def owner_document(name: str, path: str, sha: str, size: int, device: int, inode: int) -> dict[str, object]:
    return {"name": name, "path": path, "sha256": sha, "bytes": size, "device": device, "inode": inode}


def contract_document(source_sha: str, source_raw: bytes, protocol_sha: str, protocol_raw: bytes, forensics: dict[str, object]) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "version": 2,
        "status": "SOURCE FROZEN; FIRST-PARTY RUST BUFFER-LIFETIME VARIANT NOT BUILT OR RUN",
        "phase": "PHASE 2: FIRST-PARTY CANDIDATE CORRECTNESS",
        "family": "rust",
        "source": {"path": SOURCE, "sha256": source_sha, "bytes": len(source_raw)},
        "protocol": {"path": PROTOCOL, "sha256": protocol_sha, "bytes": len(protocol_raw)},
        "authenticated_previous_owners": [owner_document(*owner) for owner in OWNERS],
        "candidate_variant": {"path": VARIANT, "sha256": VARIANT_SHA256, "bytes": VARIANT_BYTES, "device": VARIANT_DEVICE, "inode": VARIANT_INODE, "status": "SOURCE FROZEN; NOT BUILT; NOT RUN", "derived_from_actually_tested_source": True, "bytes_outside_substitution_function_sha256": OUTSIDE_FUNCTION_SHA256, "live_original_exporter_open_count": 1, "live_exporter_release_exit_count": 8, "premature_bytes_snapshot_count": 0, "retained_original_subject_match_allocation_count": 2, "new_external_package": False, "new_candidate_family": False},
        "actual_previous_candidate_failure": {"status": "FAIL", "candidate_qualified": False, "original_case_denominator": 31237, "original_suite_count": 13, "named_private_waiver_count": 13, "real_candidate_worker_count": 13, "real_worker_process_ids": [row[4] for row in SUITES], "actual_mismatch_count": 1440, "explicitly_verified_passing_case_count": 14853, "failed_suite_cases_counted_as_passing": False, "verified_passes_derived_by_subtraction": False, "infrastructure_failure_count": 0, "suite_results": [{"suite": row[0], "cases": row[1], "mismatches": row[2], "explicitly_verified_passes": row[3], "worker_process_id": row[4]} for row in SUITES], "previous_v7_mismatch_count": 928, "previous_v7_explicitly_verified_passing_case_count": 8965, "mismatch_regression_against_v7": 512, "genuine_failure_categories": {"managed_v1": 16, "substitution_v2": 368, "shape_v2": 1056}, "real_witnesses": [{"suite": row[0], "case": row[1], "expected_events_complete": row[2], "actual_events_complete": row[3]} for row in WITNESSES], "unprojected_witness_vectors": NOT_PROJECTED},
        "current_previous_graph": {"version": 58, "historical_generic_mismatch_alias": 928, "explicit_current_v10_mismatch_count": 1440, "explicit_current_v10_verified_passes": 14853, "qualified_candidate_count": 0, "authenticated_evidence_owner_lower_bound": 197, "authenticated_history_reference_lower_bound": 202},
        "resulting_source_evidence_lower_bounds": {"previous_authenticated_evidence_owner_lower_bound": 197, "previous_authenticated_history_reference_lower_bound": 202, "new_focused_source_owners": 4, "authenticated_evidence_owner_lower_bound": 201, "authenticated_history_reference_lower_bound": 206, "global_evidence_owner_census": "NOT MEASURED"},
        "phase_boundary": {"candidate_variant_build": "NOT RUN", "candidate_variant_correctness": "NOT MEASURED", "candidate_variant_matching": "NOT RUN", "candidate_variant_qualified": False, "qualified_candidate_count": 0, "first_party_candidate_family_count": 6, "candidate_processes_started": 0, "native_libraries_loaded": 0, "compiler_processes_started": 0, "archive_opens": 0, "archive_inflations": 0, "hidden_cases_read": 0, "benchmark_files_read": 0, "clock_samples": 0, "timing_trials_run": 0, "performance": "NOT MEASURED", "memory": "NOT MEASURED", "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "runtime_non_delegation": "NOT ESTABLISHED", "holdout": "NOT OPENED", "winner_selected": False},
    }


def parse_cli() -> tuple[str, dict[str, str]]:
    args = sys.argv[1:]
    require(len(args) > 0, "exactly one source-only mode is required")
    mode = args[0]
    require(mode in {"--render-contract", "--self-test", "--verify-frozen-context"}, "unknown or multiple source-only modes")
    names = ("--source-sha256", "--protocol-sha256")
    if mode != "--render-contract":
        names += ("--contract-sha256",)
    require(len(args) == 1 + 2 * len(names), "exactly the required independent owner hashes must be supplied")
    pins: dict[str, str] = {}
    for offset in range(1, len(args), 2):
        name, value = args[offset], args[offset + 1]
        require(name in names and name not in pins, "unknown or duplicate independent owner hash")
        require(len(value) == 64 and all(char in "0123456789abcdef" for char in value), "owner hashes must be lowercase SHA-256")
        pins[name] = value
    require(set(pins) == set(names), "a frozen owner hash is missing")
    return mode, pins


def expect_rejection(label: str, operation: object) -> None:
    try:
        operation()
    except (FreezeError, UnicodeError, ValueError, IndexError, TypeError, OverflowError):
        return
    raise FreezeError("hostile source-only control was accepted: " + label)


def clone(value: object) -> object:
    return StrictJSON((canonical(value) + "\n").encode("utf-8")).decode()


def run_self_tests(observed: dict[str, bytes], forensics: dict[str, object], receipt: dict[str, object], expected: dict[str, object]) -> tuple[int, int]:
    controls = 0

    def rejected(label: str, operation: object) -> None:
        nonlocal controls
        expect_rejection(label, operation)
        controls += 1

    original = observed["tested_rust_bridge"]
    variant = observed["corrected_rust_bridge"]
    for label, wrong in (("missing premature snapshot", original.replace(SNAPSHOT_BLOCK, b"", 1)), ("duplicate premature snapshot", original.replace(SNAPSHOT_BLOCK, SNAPSHOT_BLOCK + SNAPSHOT_BLOCK, 1)), ("missing snapshot declaration", original.replace(SNAPSHOT_DECLARATION, b"", 1)), ("wrong historical bridge", original + b"\n")):
        rejected(label, lambda value=wrong: derive_variant(value))
    for marker, replacement, label in ((b"rust_subject_open(&subject, pattern_value, value, 1)", b"rust_subject_open(&subject, pattern_value, replacement, 1)", "wrong live subject"), (b"rust_subject_release(&subject);", b"/* leaked real exporter */", "lost exporter cleanup"), (b"int callback = PyCallable_Check(replacement);", b"int callback = 0;", "lost callback behavior"), (b"rust_match_allocate(pattern, value, groupindex, groups, 0, (Py_ssize_t)subject.length)", b"rust_match_allocate(pattern, replacement, groupindex, groups, 0, (Py_ssize_t)subject.length)", "lost real match subject")):
        wrong = variant.replace(marker, replacement, 1)
        require(wrong != variant, "a hostile corrected-source marker disappeared: " + label)
        rejected(label, lambda value=wrong: require(value == derive_variant(original), "corrected source changed"))

    def reject_forensic(label: str, mutate: object) -> None:
        wrong = clone(forensics)
        require(type(wrong) is dict, "forensic control clone failed")
        mutate(wrong)
        rejected(label, lambda value=wrong: validate_forensics(value))

    for key, value in (("candidate_status", "PASS"), ("candidate_qualified", True), ("qualified_candidate_count", 1), ("performance", "1.5x"), ("memory", 0), ("holdout", "OPENED"), ("runtime_non_delegation", "ESTABLISHED"), ("winner_selected", True)):
        reject_forensic("fabricated forensic " + key, lambda item, field=key, wrong=value: item.__setitem__(field, wrong))
    for key, value in (("case_execution_denominator", 31236), ("suite_count", 12), ("semantic_mismatch_count", 0), ("verified_passing_case_count", 31237 - 1440), ("verified_passing_cases_derived_by_subtraction", True), ("records_from_fully_observed_failed_suites_are_counted_as_passing", True), ("actual_candidate_workers", 12), ("distinct_worker_process_id_count", 12), ("all_original_observation_vectors_complete", False), ("infrastructure_failure_count", 1)):
        reject_forensic("fabricated actual total " + key, lambda item, field=key, wrong=value: item["actual_result_totals"].__setitem__(field, wrong))
    reject_forensic("dropped original suite", lambda item: item["suite_results"].pop())
    reject_forensic("reordered original suites", lambda item: item["suite_results"].reverse())
    reject_forensic("fabricated failing-suite pass", lambda item: item["suite_results"][4].__setitem__("explicitly_verified_passing_case_count", 1008))
    reject_forensic("placeholder worker", lambda item: item["suite_results"][4].__setitem__("actual_worker_started", False))
    reject_forensic("altered mismatch", lambda item: item["suite_results"][8].__setitem__("semantic_mismatch_count", 1055))
    reject_forensic("dropped real witness", lambda item: item["earliest_genuine_mismatch_witnesses"].pop())
    reject_forensic("reordered real witnesses", lambda item: item["earliest_genuine_mismatch_witnesses"].reverse())
    reject_forensic("fabricated unobserved expected vector", lambda item: item["earliest_genuine_mismatch_witnesses"][2].__setitem__("expected_events", []))
    reject_forensic("fabricated unobserved shape vector", lambda item: item["earliest_genuine_mismatch_witnesses"][4].__setitem__("actual_events", []))
    reject_forensic("changed historical mismatch", lambda item: item["historical_comparison"].__setitem__("previous_actual_rust_semantic_mismatch_count", 1440))
    reject_forensic("changed evidence floor", lambda item: item.__setitem__("resulting_authenticated_evidence_owner_lower_bound", 201))

    def reject_receipt(label: str, mutate: object) -> None:
        wrong = clone(receipt)
        require(type(wrong) is dict, "receipt control clone failed")
        mutate(wrong)
        rejected(label, lambda value=wrong: validate_receipt(value, forensics))

    for key, value in (("candidate_status", "PASS"), ("candidate_qualified", True), ("semantic_mismatch_count", 0), ("verified_passing_case_count", 31237), ("case_execution_denominator", 31236), ("performance", "1.5x"), ("holdout", "OPENED"), ("clock_samples", 1)):
        reject_receipt("fabricated durable receipt " + key, lambda item, field=key, wrong=value: item.__setitem__(field, wrong))
    reject_receipt("substituted failure archive", lambda item: item["archive"].__setitem__("inode", 525044))
    reject_receipt("substituted worker identity", lambda item: item["actual_worker_process_ids"].__setitem__(0, 999))
    rejected("wrong previous headline chart", lambda: validate_graph(observed["previous_graph_summary"] + b"\n"))
    for raw in (b'{"x":1,"x":2}', b'{"x":01}', b'{"x":NaN}', b'{"x":"\\uD800"}', b'{"x":"\\uDC00"}', b'{"x":1}{"x":2}', b'{"x":1,}', b'["x",]'):
        rejected("duplicate-key or malformed JSON", lambda value=raw: StrictJSON(value).decode())
    for key, value in (("qualified_candidate_count", 1), ("performance", "1.5x"), ("holdout", "OPENED"), ("candidate_variant_build", "BUILT"), ("candidate_processes_started", 1), ("archive_opens", 1), ("clock_samples", 1)):
        wrong = clone(expected)
        require(type(wrong) is dict and type(wrong.get("phase_boundary")) is dict, "source-contract control clone failed")
        wrong["phase_boundary"][key] = value
        rejected("fabricated source-only boundary " + key, lambda value=wrong: require(value == expected, "source-only contract was changed"))

    physical = (
        ("unlisted plaintext", lambda: builtins.open("/etc/hosts", "rb")),
        ("compressed failures", lambda: builtins.open(ROOT + "/oracle/phase2/evidence/repaired-rust-original-campaign-v10-rust-phase2-v16-rust-buffer-shape-pickle-original-p0-v10-failures.json.gz", "rb")),
        ("hidden holdout", lambda: builtins.open(ROOT + "/benchmarks/holdout.json", "rb")),
        ("source mutation", lambda: builtins.open(ROOT + "/" + SOURCE, "w")),
        ("Python regex import", lambda: sys.audit("import", "re", None, None, None, None)),
        ("CPython matcher import", lambda: sys.audit("import", "_sre", None, None, None, None)),
        ("candidate import", lambda: sys.audit("import", "candidates.rust_candidate", None, None, None, None)),
        ("native library", lambda: sys.audit("ctypes.dlopen", "forbidden.so")),
        ("compiler or worker", lambda: sys.audit("subprocess.Popen", "rustc", (), None, None)),
        ("network", lambda: sys.audit("socket.__new__", None, 2, 1, 0)),
        ("dynamic execution", lambda: sys.audit("exec", "forbidden")),
        ("source rename", lambda: sys.audit("os.rename", "old", "new", -1, -1)),
        ("timing", lambda: sys.audit("time.monotonic")),
        ("temporary output", lambda: sys.audit("tempfile.mkdtemp", "/tmp/forbidden")),
    )
    for label, operation in physical:
        rejected("physical source-only wall: " + label, operation)
    require(sum(_BLOCKED_EVENTS.values()) >= len(physical), "physical forbidden operations were not rejected")
    no_engine_imports()
    return controls, len(physical)


def main() -> int:
    require(sys.implementation.name == "cpython" and tuple(sys.version_info[:3]) == (3, 14, 6), "the pinned stable CPython 3.14.6 oracle is required")
    require(sys.flags.isolated and sys.dont_write_bytecode, "run the source verifier with -I -B")
    no_engine_imports()
    digest(b"source-only Rust buffer-lifetime freeze")
    mode, pins = parse_cli()
    sys.addaudithook(audit_wall)
    source_raw = read_exact(SOURCE, pins["--source-sha256"])
    protocol_raw = read_exact(PROTOCOL, pins["--protocol-sha256"])
    observed, forensics, receipt = load_context()
    expected = contract_document(pins["--source-sha256"], source_raw, pins["--protocol-sha256"], protocol_raw, forensics)
    encoded = (canonical(expected) + "\n").encode("utf-8")
    if mode == "--render-contract":
        sys.stdout.write(encoded.decode("utf-8"))
        no_engine_imports()
        return 0
    actual_contract = read_exact(CONTRACT, pins["--contract-sha256"])
    require(actual_contract == encoded and StrictJSON(actual_contract).decode() == expected, "the independently pinned source contract changed")
    if mode == "--self-test":
        controls, physical = run_self_tests(observed, forensics, receipt, expected)
        result = {"status": "PASS", "mode": "self-test", "source_only_controls": controls, "physical_audit_controls": physical, "authenticated_plaintext_owner_count": len(OWNERS) + 4, "variant_sha256": VARIANT_SHA256, "actual_previous_candidate_status": "FAIL", "actual_previous_mismatch_count": 1440, "actual_previous_verified_passing_case_count": 14853, "candidate_variant_build": "NOT RUN", "candidate_variant_matching": "NOT RUN", "qualified_candidate_count": 0, "performance": "NOT MEASURED", "holdout": "NOT OPENED"}
    else:
        result = {"status": "PASS", "mode": "verify-frozen-context", "authenticated_plaintext_owner_count": len(OWNERS) + 4, "variant_sha256": VARIANT_SHA256, "actual_previous_candidate_status": "FAIL", "actual_previous_mismatch_count": 1440, "actual_previous_verified_passing_case_count": 14853, "full_case_denominator": 31237, "suite_count": 13, "genuine_candidate_worker_count": 13, "genuine_mismatch_witness_count": 6, "candidate_variant_build": "NOT RUN", "candidate_variant_matching": "NOT RUN", "qualified_candidate_count": 0, "performance": "NOT MEASURED", "holdout": "NOT OPENED"}
    sys.stdout.write(canonical(result) + "\n")
    no_engine_imports()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FreezeError as error:
        sys.stderr.write("Rust buffer-lifetime source freeze failed: " + str(error) + "\n")
        raise SystemExit(1)
