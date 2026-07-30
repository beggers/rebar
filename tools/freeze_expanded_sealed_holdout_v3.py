#!/usr/bin/env python3
"""Verify the public, ungenerated V3 holdout rekey without opening holdouts.

The verifier owns exactly its source and two public planning documents.  The
compromised V2 proposal receives one metadata-only lstat and is never opened.
There is no present seed, freeze authority, generated case, candidate run,
matcher delegation, native load, child process, clock sample, or file write.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

if any(name == root or name.startswith(root + ".")
       for name in sys.modules
       for root in ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
                    "ctypes", "subprocess", "socket", "random", "secrets",
                    "threading", "multiprocessing", "candidates", "rebar")):
    raise SystemExit("V3 source-only verifier cannot inherit a matcher or candidate")

import _io
import builtins
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
SOURCE = "tools/freeze_expanded_sealed_holdout_v3.py"
PROTOCOL = "oracle/phase3/EXPANDED-SEALED-HOLDOUT-V3.md"
PUBLIC_PLAN = "oracle/phase3/expanded-sealed-holdout-v3.json"
RETIRED_V2 = "oracle/phase3/expanded-sealed-holdout-v2.json"
PROTOCOL_SHA256 = "6199085b5a16557892c5501d9b7ce4850b7d85092116c521ec43422c9b68791b"
PROTOCOL_BYTES = 8946
PUBLIC_PLAN_SHA256 = "2d04f8b3bfb2f0f65a3d5c9435c4145d5d3aab29bd3f9acd3617a7f9fe2939c0"
PUBLIC_PLAN_BYTES = 12401
RETIRED_V2_PREVIOUSLY_AUTHENTICATED_SHA256 = (
    "5d9fa3920c1dcabc92a3521d742cd10ec399cff1a979b71ac079daba6f92cba0"
)
DEVICE = 2064
RETIRED_V2_INODE = 525920
RETIRED_V2_BYTES = 15561
RETIRED_V2_MODE = 0o600
MAX_OWNER_BYTES = 131072
MAX_JSON_DEPTH = 32
MAX_JSON_ITEMS = 16384
MINIMUM_CANDIDATE_FAMILIES = 3
CASE_COUNT = 226492416
PREVIOUS_CASE_COUNT = 141557760
COHORT_CASES = 4096
FULL_SWEEP_BATCHES = 55296

OPERATION_IDS = (
    "compile", "module_search", "module_match", "module_fullmatch",
    "module_finditer", "module_findall", "module_split", "module_sub",
    "module_subn", "pattern_search", "pattern_match", "pattern_fullmatch",
    "pattern_finditer", "pattern_findall", "pattern_split", "pattern_substitution",
)
PATTERN_IDS = (
    "literal_ascii", "literal_unicode_latin1", "literal_unicode_bmp",
    "literal_unicode_astral", "escaped_metacharacter", "wildcard_dot",
    "wildcard_dotall", "character_class_ascii", "character_class_unicode",
    "negated_character_class", "category_digit", "category_space", "category_word",
    "category_not_digit", "category_not_space", "category_not_word",
    "unicode_simple_casefold", "unicode_multichar_case_boundary",
    "ascii_casefold_flag", "locale_bytes_flag", "anchor_start", "anchor_end",
    "absolute_start", "absolute_end", "word_boundary", "nonword_boundary",
    "line_anchor_multiline", "newline_crlf", "alternation_flat",
    "alternation_prefix_overlap", "alternation_nested", "branch_empty",
    "greedy_star", "lazy_star", "greedy_plus", "lazy_plus", "greedy_optional",
    "lazy_optional", "counted_exact", "counted_bounded", "counted_open",
    "nested_repeat", "zero_width_repeat", "repeat_capture_restore",
    "capture_numbered", "capture_named", "capture_optional", "capture_nested",
    "backreference_numbered", "backreference_named", "conditional_group",
    "conditional_assertion_boundary", "lookahead_positive", "lookahead_negative",
    "lookbehind_positive_fixed", "lookbehind_negative_fixed", "lookaround_nested",
    "atomic_group", "possessive_repeat", "inline_flags_global",
    "inline_flags_scoped", "verbose_pattern", "bytes_high_bit",
    "invalid_pattern_diagnostic",
)
INPUT_IDS = (
    "str_ascii", "str_latin1", "str_bmp", "str_astral", "bytes", "bytearray",
    "memoryview_readonly", "memoryview_writable", "memoryview_strided",
    "array_unsigned_byte", "array_signed_byte", "custom_buffer_exporter",
)
LIFECYCLE_IDS = (
    "cold_compile", "warm_cache_hit", "compiled_pattern_reuse",
    "scanner_continuation", "iterator_partial_resume", "cache_purge_recompile",
    "match_object_projection", "nested_reentrant_callback",
)
LENGTH_IDS = (
    "empty", "unit", "tiny", "short", "medium", "cache_boundary", "page_edge",
    "large_bounded", "adversarial_bounded",
)
OUTCOME_IDS = (
    "positive_match", "negative_match", "empty_progress",
    "expected_exception_boundary",
)
MUTATION_IDS = (
    "identity", "prefix", "suffix", "interior", "unicode_boundary",
    "capture_boundary", "flag_boundary", "buffer_boundary",
)
DIMENSIONS = (
    ("operation_family", 16), ("operation_profile_per_family", 8),
    ("regex_pattern_family", 64), ("input_representation", 12),
    ("lifecycle_context", 8), ("input_length_regime", 9),
    ("expected_outcome_class", 4), ("mutation_family", 8),
)
DERIVATION_PLANS = (
    ("reservoir_index_permutation", "rebar/v3/reservoir/index"),
    ("primary_cohort", "rebar/v3/cohort/primary"),
    ("confirmation_cohort", "rebar/v3/cohort/confirmation"),
    ("regex_materialization", "rebar/v3/materialize/regex"),
    ("input_materialization", "rebar/v3/materialize/input"),
    ("lifecycle_sequencing", "rebar/v3/materialize/lifecycle"),
    ("case_mutation", "rebar/v3/materialize/mutation"),
    ("deterministic_replay", "rebar/v3/audit/replay"),
)


class ProposalError(Exception):
    """A public rekey contract or its physical source wall was violated."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise ProposalError(message)


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete immutable genuine bytes")
    return hashlib.sha256(raw).hexdigest()


def exact_keys(value: object, expected: tuple[str, ...], label: str) -> dict:
    require(type(value) is dict, "require exact object: " + label)
    assert isinstance(value, dict)
    require(set(value) == set(expected), "reject missing or extra keys: " + label)
    return value


def exact_list(value: object, expected: tuple[str, ...], label: str) -> None:
    require(type(value) is list and tuple(value) == expected,
            "require exact fixed unique list: " + label)
    require(len(set(expected)) == len(expected), "reject duplicate fixed ID: " + label)


def clean_imports() -> None:
    forbidden = (
        "re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma", "ctypes",
        "subprocess", "socket", "random", "secrets", "threading", "multiprocessing",
        "concurrent", "_interpreters", "candidates", "rebar",
    )
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in forbidden),
            "reject matcher, native loader, candidate, worker, network, or entropy")


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= MAX_JSON_DEPTH, "reject excessive report nesting")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is int:
        return str(value)
    if type(value) is str:
        escapes = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
                   "\n": "\\n", "\r": "\\r", "\t": "\\t"}
        require(not any(0xD800 <= ord(char) <= 0xDFFF for char in value),
                "reject unpaired output surrogate")
        return '"' + "".join(
            escapes.get(char, "\\u" + format(ord(char), "04x")
                        if ord(char) < 32 else char)
            for char in value
        ) + '"'
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value), "reject nontext report key")
        return "{" + ",".join(canonical(key) + ":" + canonical(value[key], depth + 1)
                                for key in sorted(value)) + "}"
    raise ProposalError("reject unsupported or nonfinite report value")


class StrictJson:
    """Small bounded JSON reader that never imports the regex-backed stdlib parser."""

    def __init__(self, raw: bytes) -> None:
        require(type(raw) is bytes and len(raw) <= MAX_OWNER_BYTES,
                "require a bounded genuine public JSON document")
        try:
            self.text = raw.decode("utf-8", "strict")
        except UnicodeError as error:
            raise ProposalError("reject malformed public JSON UTF-8") from error
        require(not self.text.startswith("\ufeff"), "reject JSON byte-order mark")
        self.position = 0
        self.items = 0

    def whitespace(self) -> None:
        while self.position < len(self.text) and self.text[self.position] in " \t\r\n":
            self.position += 1

    def take(self, expected: str) -> None:
        require(self.text.startswith(expected, self.position), "reject malformed public JSON")
        self.position += len(expected)

    def string(self) -> str:
        self.take('"')
        output: list[str] = []
        while self.position < len(self.text):
            char = self.text[self.position]
            self.position += 1
            if char == '"':
                return "".join(output)
            require(ord(char) >= 32, "reject unescaped public JSON control")
            if char != "\\":
                require(not 0xD800 <= ord(char) <= 0xDFFF,
                        "reject unpaired public JSON surrogate")
                output.append(char)
                continue
            require(self.position < len(self.text), "reject truncated public JSON escape")
            escaped = self.text[self.position]
            self.position += 1
            mapping = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
                       "n": "\n", "r": "\r", "t": "\t"}
            if escaped in mapping:
                output.append(mapping[escaped])
                continue
            require(escaped == "u" and self.position + 4 <= len(self.text),
                    "reject invalid public JSON escape")
            digits = self.text[self.position:self.position + 4]
            require(all(item in "0123456789abcdefABCDEF" for item in digits),
                    "reject invalid public JSON Unicode escape")
            codepoint = int(digits, 16)
            require(not 0xD800 <= codepoint <= 0xDFFF,
                    "reject public JSON surrogate code point")
            output.append(chr(codepoint))
            self.position += 4
        raise ProposalError("reject unterminated public JSON string")

    def integer(self) -> int:
        start = self.position
        if self.text[self.position] == "-":
            self.position += 1
        require(self.position < len(self.text)
                and self.text[self.position] in "0123456789",
                "reject malformed public JSON integer")
        if self.text[self.position] == "0":
            self.position += 1
            require(self.position == len(self.text)
                    or self.text[self.position] not in "0123456789",
                    "reject public JSON leading zero")
        else:
            while (self.position < len(self.text)
                   and self.text[self.position] in "0123456789"):
                self.position += 1
        require(self.position == len(self.text)
                or self.text[self.position] not in ".eE",
                "reject noninteger public JSON number")
        digits = self.text[start:self.position]
        require(len(digits) <= 20, "reject oversized public JSON integer")
        return int(digits)

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "reject deeply nested public JSON")
        self.whitespace()
        require(self.position < len(self.text), "reject truncated public JSON")
        self.items += 1
        require(self.items <= MAX_JSON_ITEMS, "reject oversized public JSON structure")
        char = self.text[self.position]
        if char == '"':
            return self.string()
        if char == "{":
            self.position += 1
            output: dict[str, object] = {}
            self.whitespace()
            if self.position < len(self.text) and self.text[self.position] == "}":
                self.position += 1
                return output
            while True:
                self.whitespace()
                require(self.position < len(self.text)
                        and self.text[self.position] == '"',
                        "require genuine public JSON object key")
                key = self.string()
                require(key not in output, "reject duplicate public JSON key: " + key)
                self.whitespace()
                self.take(":")
                output[key] = self.value(depth + 1)
                self.whitespace()
                require(self.position < len(self.text), "reject truncated public JSON object")
                if self.text[self.position] == "}":
                    self.position += 1
                    return output
                self.take(",")
        if char == "[":
            self.position += 1
            output_list: list[object] = []
            self.whitespace()
            if self.position < len(self.text) and self.text[self.position] == "]":
                self.position += 1
                return output_list
            while True:
                output_list.append(self.value(depth + 1))
                self.whitespace()
                require(self.position < len(self.text), "reject truncated public JSON list")
                if self.text[self.position] == "]":
                    self.position += 1
                    return output_list
                self.take(",")
        if char == "t":
            self.take("true")
            return True
        if char == "f":
            self.take("false")
            return False
        if char == "n":
            self.take("null")
            return None
        require(char == "-" or char in "0123456789", "reject invalid public JSON token")
        return self.integer()

    def parse(self) -> object:
        parsed = self.value()
        self.whitespace()
        require(self.position == len(self.text), "reject trailing public JSON content")
        return parsed


class SourceWall:
    """Audit-backed deny-default owner reads plus one retired metadata-only lstat."""

    def __init__(self) -> None:
        self.allowed = frozenset(ROOT + "/" + item
                                 for item in (SOURCE, PROTOCOL, PUBLIC_PLAN))
        self.retired = ROOT + "/" + RETIRED_V2
        self.owner_descriptors: dict[int, str] = {}
        self.opened: set[str] = set()
        self.pending_owner: str | None = None
        self.retired_stat_count = 0
        self.retired_open_count = 0
        self.bytes_read: dict[str, int] = {}
        self.blocked: dict[str, int] = {}
        self.installed = False
        self._open = os.open
        self._read = os.read
        self._close = os.close
        self._fstat = os.fstat
        self._lstat = os.lstat
        self._builtin_open = builtins.open

    def deny(self, category: str) -> None:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise ProposalError("V3 source wall denied " + category)

    def forbidden(self, category: str):
        def reject(*_args: object, **_kwargs: object) -> None:
            self.deny(category)
        return reject

    def owner_flags(self, flags: object) -> bool:
        nofollow = getattr(os, "O_NOFOLLOW", 0)
        cloexec = getattr(os, "O_CLOEXEC", 0)
        disallowed = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_TRUNC
                      | os.O_APPEND | getattr(os, "O_DIRECTORY", 0)
                      | getattr(os, "O_PATH", 0) | getattr(os, "O_TMPFILE", 0))
        return (type(flags) is int and nofollow != 0 and cloexec != 0
                and flags & nofollow == nofollow and flags & cloexec == cloexec
                and not flags & disallowed)

    def audit(self, event: str, arguments: tuple[object, ...]) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 else None
            if (type(path) is str and path in self.allowed
                    and path == self.pending_owner and path not in self.opened
                    and self.owner_flags(flags)):
                return
            if path == self.retired:
                self.deny("retired-compromised-proposal-content")
            self.deny("unowned-final-case-candidate-native-or-write-open")
        self.deny("audit-event-" + event)

    def guarded_open(self, path: object, flags: object, mode: object = 0o777,
                     *, dir_fd: object = None) -> int:
        if (type(path) is not str or path not in self.allowed or path in self.opened
                or dir_fd is not None or type(mode) is not int
                or not self.owner_flags(flags) or self.pending_owner is not None):
            self.deny("unowned-or-repeated-owner-descriptor-open")
        assert isinstance(path, str) and isinstance(flags, int)
        self.pending_owner = path
        try:
            descriptor = self._open(path, flags)
        finally:
            self.pending_owner = None
        require(type(descriptor) is int and descriptor >= 0,
                "require an exact nonnegative owner descriptor")
        self.owner_descriptors[descriptor] = path
        self.opened.add(path)
        self.bytes_read[path] = 0
        return descriptor

    def guarded_read(self, descriptor: object, count: object) -> bytes:
        if (type(descriptor) is not int or descriptor not in self.owner_descriptors
                or type(count) is not int or not 0 <= count <= 65536):
            self.deny("unowned-descriptor-or-unbounded-read")
        assert isinstance(descriptor, int) and isinstance(count, int)
        raw = self._read(descriptor, count)
        path = self.owner_descriptors[descriptor]
        self.bytes_read[path] += len(raw)
        require(self.bytes_read[path] <= MAX_OWNER_BYTES,
                "reject oversized public owner source")
        return raw

    def guarded_fstat(self, descriptor: object) -> os.stat_result:
        if type(descriptor) is not int or descriptor not in self.owner_descriptors:
            self.deny("unowned-descriptor-metadata")
        assert isinstance(descriptor, int)
        return self._fstat(descriptor)

    def guarded_close(self, descriptor: object) -> None:
        if type(descriptor) is not int or descriptor not in self.owner_descriptors:
            self.deny("unowned-descriptor-close")
        assert isinstance(descriptor, int)
        self._close(descriptor)
        del self.owner_descriptors[descriptor]

    def guarded_lstat(self, path: object, *, dir_fd: object = None) -> os.stat_result:
        if path != self.retired or dir_fd is not None or self.retired_stat_count != 0:
            self.deny("unapproved-or-repeated-metadata-stat")
        self.retired_stat_count += 1
        result = self._lstat(path)
        require(result.st_dev == DEVICE and result.st_ino == RETIRED_V2_INODE
                and result.st_size == RETIRED_V2_BYTES
                and stat.S_ISREG(result.st_mode)
                and stat.S_IMODE(result.st_mode) == RETIRED_V2_MODE,
                "retired V2 metadata changed; stop without reading its contents")
        return result

    def install(self) -> None:
        require(not self.installed, "install immutable V3 source wall exactly once")
        authority = (self, self.audit)

        def immutable_hook(event: str, arguments: tuple[object, ...]) -> None:
            require(authority[0] is self, "reject changed source-wall authority")
            authority[1](event, arguments)

        sys.addaudithook(immutable_hook)
        self.installed = True
        sys.addaudithook = self.forbidden("additional-audit-hook")
        builtins.open = self.forbidden("builtin-file-open")
        io.open = self.forbidden("io-file-open")
        _io.open = self.forbidden("native-io-file-open")
        if hasattr(_io, "open_code"):
            _io.open_code = self.forbidden("native-code-open")
        if hasattr(io, "open_code"):
            io.open_code = self.forbidden("io-code-open")
        if hasattr(_io, "FileIO"):
            _io.FileIO = self.forbidden("native-fileio-constructor")
        if hasattr(io, "FileIO"):
            io.FileIO = self.forbidden("io-fileio-constructor")
        os.open = self.guarded_open
        os.read = self.guarded_read
        os.fstat = self.guarded_fstat
        os.close = self.guarded_close
        os.lstat = self.guarded_lstat
        for name in (
                "stat", "access", "listdir", "scandir", "walk", "fwalk", "readlink",
                "mkdir", "makedirs", "remove", "unlink", "rmdir", "removedirs",
                "rename", "replace", "chmod", "chown", "link", "symlink",
                "truncate", "ftruncate", "write", "writev", "pread", "preadv",
                "pwrite", "pwritev", "sendfile", "copy_file_range", "splice",
                "dup", "dup2", "pipe", "pipe2", "fdopen", "system", "popen",
                "fork", "forkpty", "posix_spawn", "posix_spawnp", "startfile",
                "execv", "execve", "execl", "execle", "execlp", "execlpe",
                "execvp", "execvpe", "spawnl", "spawnle", "spawnlp", "spawnlpe",
                "spawnv", "spawnve", "spawnvp", "spawnvpe", "putenv", "unsetenv",
                "urandom", "getrandom", "getpid", "getppid",
        ):
            if hasattr(os, name):
                setattr(os, name, self.forbidden("os-" + name))
        for name in (
                "time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
                "perf_counter_ns", "process_time", "process_time_ns", "thread_time",
                "thread_time_ns", "clock_gettime", "clock_gettime_ns", "sleep",
        ):
            if hasattr(time, name):
                setattr(time, name, self.forbidden("clock-" + name))
        builtins.__import__ = self.forbidden("dynamic-import")
        builtins.compile = self.forbidden("dynamic-compile")
        builtins.exec = self.forbidden("dynamic-exec")
        builtins.eval = self.forbidden("dynamic-eval")


def read_owner(wall: SourceWall, relative: str) -> bytes:
    path = ROOT + "/" + relative
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
    descriptor = os.open(path, flags)
    try:
        metadata = os.fstat(descriptor)
        require(metadata.st_dev == DEVICE and stat.S_ISREG(metadata.st_mode)
                and 0 < metadata.st_size <= MAX_OWNER_BYTES,
                "require a bounded regular owned public source on the expected device")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            chunks.append(chunk)
        raw = b"".join(chunks)
        require(len(raw) == metadata.st_size, "reject incomplete or raced owner read")
        return raw
    finally:
        os.close(descriptor)


def verify_incident(plan: dict) -> None:
    incident = exact_keys(plan["incident"], (
        "date_utc", "cause", "hidden_cases_previously_generated", "secrecy_assumption",
        "incident_records", "incident_records_read_by_v3_author", "rekey_reason",
        "retired_v2", "historical_case_counts",
    ), "incident")
    require(incident["date_utc"] == "2026-07-30"
            and incident["cause"] == "read-only helper recursively searched tracked oracle paths"
            and incident["hidden_cases_previously_generated"] == 0
            and incident["secrecy_assumption"] == "CONSERVATIVELY_INVALIDATED"
            and incident["incident_records_read_by_v3_author"] is False,
            "require explicit conservative no-generated-case incident provenance")
    exact_list(incident["incident_records"], ("README.md", "docs/EXPERIMENT-LOG.md"),
               "unread incident provenance references")
    require(type(incident["rekey_reason"]) is str
            and "V2" in incident["rekey_reason"]
            and "secret" in incident["rekey_reason"], "require explicit rekey reason")
    retired = exact_keys(incident["retired_v2"], (
        "status", "path", "previously_authenticated_sha256", "device", "inode", "bytes",
        "mode_octal", "content_reads_allowed", "sha_recomputed_by_v3_verifier",
        "case_count", "operation_slots", "regex_families", "input_representations",
    ), "retired V2 metadata-only provenance")
    require(retired == {
        "status": "RETIRED_COMPROMISED_APPEND_ONLY", "path": RETIRED_V2,
        "previously_authenticated_sha256": RETIRED_V2_PREVIOUSLY_AUTHENTICATED_SHA256,
        "device": DEVICE, "inode": RETIRED_V2_INODE, "bytes": RETIRED_V2_BYTES,
        "mode_octal": "0600", "content_reads_allowed": 0,
        "sha_recomputed_by_v3_verifier": False, "case_count": PREVIOUS_CASE_COUNT,
        "operation_slots": 96, "regex_families": 48, "input_representations": 10,
    }, "require exact append-only compromised V2 metadata without content access")
    require(incident["historical_case_counts"] == {"v1": 14155776, "earliest": 4194304},
            "require exact historical proposal counts")


def verify_reservoir(plan: dict) -> None:
    reservoir = exact_keys(plan["holdout_reservoir"], (
        "case_count", "minimum_successor_case_count", "dimensions", "case_identity",
        "generation",
    ), "fixed virtual reservoir")
    require(reservoir["case_count"] == CASE_COUNT
            and reservoir["minimum_successor_case_count"] == PREVIOUS_CASE_COUNT
            and CASE_COUNT > PREVIOUS_CASE_COUNT,
            "require an exact larger successor holdout")
    raw_dimensions = reservoir["dimensions"]
    require(type(raw_dimensions) is list and len(raw_dimensions) == len(DIMENSIONS),
            "require exact complete mixed-radix axes")
    product = 1
    for row, expected in zip(raw_dimensions, DIMENSIONS):
        item = exact_keys(row, ("axis", "cardinality"), "mixed-radix dimension")
        require((item["axis"], item["cardinality"]) == expected,
                "reject changed mixed-radix dimension")
        product *= expected[1]
    require(product == CASE_COUNT
            and reservoir["case_identity"] == "bijective fixed-order mixed-radix tuple index",
            "require exact bijective reservoir cardinality")
    generation = exact_keys(reservoir["generation"], (
        "mode", "batch_case_count", "full_sweep_batch_count", "maximum_input_bytes_per_case",
        "default_authorized_batches", "future_default_postfreeze_batches",
        "full_sweep_requires_separate_authorization",
        "full_sweep_requires_finite_resource_budget", "case_files_currently_exist",
    ), "bounded deferred generation")
    require(generation == {
        "mode": "VIRTUAL_INDEXED_RESERVOIR_NOT_MATERIALIZED",
        "batch_case_count": COHORT_CASES, "full_sweep_batch_count": FULL_SWEEP_BATCHES,
        "maximum_input_bytes_per_case": 4096, "default_authorized_batches": 0,
        "future_default_postfreeze_batches": 2,
        "full_sweep_requires_separate_authorization": True,
        "full_sweep_requires_finite_resource_budget": True,
        "case_files_currently_exist": False,
    } and FULL_SWEEP_BATCHES * COHORT_CASES == CASE_COUNT,
            "require bounded scalable batches and no implicit giant final run")


def verify_coverage(plan: dict) -> None:
    coverage = exact_keys(plan["coverage"], (
        "operation_families", "regex_pattern_families", "input_representations",
        "lifecycle_contexts", "input_length_regimes", "expected_outcome_classes",
        "mutation_families",
    ), "expanded public coverage taxonomy")
    operations = coverage["operation_families"]
    require(type(operations) is list and len(operations) == len(OPERATION_IDS),
            "require sixteen fixed operation families")
    for item, expected_id in zip(operations, OPERATION_IDS):
        operation = exact_keys(item, ("id", "profiles", "cases"), "operation family")
        require(operation == {"id": expected_id, "profiles": 8,
                              "cases": CASE_COUNT // len(OPERATION_IDS)},
                "require eight profiles and exact balanced operation-family weight")
    exact_list(coverage["regex_pattern_families"], PATTERN_IDS, "64 regex families")
    exact_list(coverage["input_representations"], INPUT_IDS, "12 input representations")
    exact_list(coverage["lifecycle_contexts"], LIFECYCLE_IDS, "8 lifecycle contexts")
    exact_list(coverage["input_length_regimes"], LENGTH_IDS, "9 bounded length classes")
    exact_list(coverage["expected_outcome_classes"], OUTCOME_IDS, "4 expected outcomes")
    exact_list(coverage["mutation_families"], MUTATION_IDS, "8 mutation families")
    weights = exact_keys(plan["fixed_category_weights"], (
        "operation_family_cases", "operation_profile_cases", "regex_pattern_family_cases",
        "input_representation_cases", "lifecycle_context_cases", "input_length_regime_cases",
        "expected_outcome_class_cases", "mutation_family_cases",
    ), "exact category weights")
    require(weights == {
        "operation_family_cases": CASE_COUNT // 16,
        "operation_profile_cases": CASE_COUNT // 128,
        "regex_pattern_family_cases": CASE_COUNT // 64,
        "input_representation_cases": CASE_COUNT // 12,
        "lifecycle_context_cases": CASE_COUNT // 8,
        "input_length_regime_cases": CASE_COUNT // 9,
        "expected_outcome_class_cases": CASE_COUNT // 4,
        "mutation_family_cases": CASE_COUNT // 8,
    }, "require complete fixed, balanced reservoir category weights")


def verify_cohorts(plan: dict) -> None:
    cohorts = plan["paired_holdout_cohorts"]
    require(type(cohorts) is list and len(cohorts) == 2,
            "require exactly two practical paired holdout cohorts")
    for item, expected in zip(cohorts, (
            ("primary", "rebar/v3/cohort/primary"),
            ("confirmation", "rebar/v3/cohort/confirmation"),
    )):
        cohort = exact_keys(item, ("id", "cases", "derivation_domain"), "paired cohort")
        require(cohort == {"id": expected[0], "cases": COHORT_CASES,
                          "derivation_domain": expected[1]},
                "require independent fixed-size primary and confirmation cohorts")
    quotas = exact_keys(plan["cohort_marginal_quotas"], (
        "operation_family", "operation_profile", "regex_pattern_family",
        "input_representation", "lifecycle_context", "input_length_regime",
        "expected_outcome_class", "mutation_family", "require_disjoint_cohorts",
        "collision_repair_preserves_all_marginals",
        "pair_same_case_across_reference_and_candidates",
    ), "balanced cohort marginals")
    cardinalities = (
        ("operation_family", 16), ("operation_profile", 128),
        ("regex_pattern_family", 64), ("input_representation", 12),
        ("lifecycle_context", 8), ("input_length_regime", 9),
        ("expected_outcome_class", 4), ("mutation_family", 8),
    )
    for axis, cardinality in cardinalities:
        minimum, remainder = divmod(COHORT_CASES, cardinality)
        maximum = minimum + (1 if remainder else 0)
        require(quotas[axis] == {"minimum": minimum, "maximum": maximum,
                                 "remainder": remainder},
                "require exact per-cohort stratification: " + axis)
    require(quotas["require_disjoint_cohorts"] is True
            and quotas["collision_repair_preserves_all_marginals"] is True
            and quotas["pair_same_case_across_reference_and_candidates"] is True,
            "require disjoint, quota-preserving reference/candidate pairing")


def verify_qualification_and_entropy(plan: dict) -> None:
    qualification = exact_keys(plan["candidate_qualification"], (
        "minimum_independent_candidate_families", "qualified_families_currently_verified",
        "require_distinct_family_ids", "require_independent_source_lineages",
        "require_distinct_frozen_source_digests", "require_distinct_native_artifact_digests",
        "require_no_candidate_delegation", "require_no_stdlib_or_external_matcher_fallback",
        "require_independent_owned_non_delegation_attestations",
        "lock_candidate_sources_and_builds_before_entropy", "public_correctness_cases",
        "public_correctness_apis", "public_profiler_cases", "public_profiler_apis",
        "protected_data_read_before_qualification_allowed",
        "entropy_creation_before_qualification_allowed",
    ), "three independent candidate-family prerequisite")
    require(qualification == {
        "minimum_independent_candidate_families": MINIMUM_CANDIDATE_FAMILIES,
        "qualified_families_currently_verified": 0,
        "require_distinct_family_ids": True,
        "require_independent_source_lineages": True,
        "require_distinct_frozen_source_digests": True,
        "require_distinct_native_artifact_digests": True,
        "require_no_candidate_delegation": True,
        "require_no_stdlib_or_external_matcher_fallback": True,
        "require_independent_owned_non_delegation_attestations": True,
        "lock_candidate_sources_and_builds_before_entropy": True,
        "public_correctness_cases": 10434, "public_correctness_apis": 111,
        "public_profiler_cases": 416, "public_profiler_apis": 26,
        "protected_data_read_before_qualification_allowed": False,
        "entropy_creation_before_qualification_allowed": False,
    }, "require three genuinely independent, nondelegating publicly correct candidates")
    entropy = exact_keys(plan["post_correctness_entropy"], (
        "status", "seed_exists_now", "seed_commitment",
        "minimum_independent_external_custodians", "minimum_fresh_bits_per_custodian",
        "require_postqualification_os_csprng_contribution",
        "reject_existing_environment_seed", "reject_candidate_supplied_entropy",
        "publish_seed_commitment_only", "private_seed_must_never_enter_workspace",
        "encrypted_two_custodian_replay_escrow_required",
    ), "future external entropy and commitment-only custody")
    require(entropy == {
        "status": "NOT_CREATED", "seed_exists_now": False, "seed_commitment": None,
        "minimum_independent_external_custodians": 2,
        "minimum_fresh_bits_per_custodian": 256,
        "require_postqualification_os_csprng_contribution": True,
        "reject_existing_environment_seed": True,
        "reject_candidate_supplied_entropy": True,
        "publish_seed_commitment_only": True,
        "private_seed_must_never_enter_workspace": True,
        "encrypted_two_custodian_replay_escrow_required": True,
    }, "require nonexistent unpredictable future seed and commitment-only publication")


def verify_derivation_disclosure_and_wall(plan: dict) -> None:
    separation = exact_keys(plan["domain_separation"], (
        "derivation", "derived_keys_exist_now", "independent_plans",
    ), "future independent domain-separated keys")
    require(separation["derivation"]
            == "HKDF-SHA-256 from future externally created master seed"
            and separation["derived_keys_exist_now"] is False,
            "reject present seed/key material or unfrozen derivation")
    derivations = separation["independent_plans"]
    require(type(derivations) is list and len(derivations) == len(DERIVATION_PLANS),
            "require exact independent future derivation plan set")
    observed_domains: set[str] = set()
    for row, expected in zip(derivations, DERIVATION_PLANS):
        derivation = exact_keys(row, ("purpose", "domain"), "future derivation plan")
        require((derivation["purpose"], derivation["domain"]) == expected,
                "reject changed independent derivation plan")
        assert isinstance(derivation["domain"], str)
        observed_domains.add(derivation["domain"])
    require(len(observed_domains) == len(DERIVATION_PLANS),
            "reject shared future seed derivation domains")
    deterministic = exact_keys(plan["deterministic_generation"], (
        "seed_or_private_case_present", "reconstruct_from_frozen_metadata_and_escrowed_future_seed",
        "reservoir_permutation", "feistel_rounds", "feistel_bits",
        "maximum_cycle_walk_attempts", "independently_keyed_balanced_axis_shuffles",
        "fail_closed_on_quota_or_disjointness_error",
        "forbid_clock_pid_environment_filesystem_scheduler_or_candidate_inputs",
    ), "future deterministic reconstruction")
    require(deterministic == {
        "seed_or_private_case_present": False,
        "reconstruct_from_frozen_metadata_and_escrowed_future_seed": True,
        "reservoir_permutation": "ten-round 28-bit balanced Feistel with cycle walking",
        "feistel_rounds": 10, "feistel_bits": 28,
        "maximum_cycle_walk_attempts": 64,
        "independently_keyed_balanced_axis_shuffles": True,
        "fail_closed_on_quota_or_disjointness_error": True,
        "forbid_clock_pid_environment_filesystem_scheduler_or_candidate_inputs": True,
    } and 1 << deterministic["feistel_bits"] > CASE_COUNT,
            "require deterministic bounded post-freeze reconstruction only")
    disclosure = exact_keys(plan["disclosure_and_rotation"], (
        "private_outputs_encrypted_before_disclosure", "candidate_authors_can_read_private_cases",
        "candidate_authors_can_read_seed", "allow_commitment_publication_only",
        "retire_and_rekey_on_premature_proposal_or_case_read",
        "retire_and_rekey_on_seed_disclosure", "retire_and_rekey_on_candidate_set_change",
        "retire_and_rekey_on_independence_or_replay_failure",
        "rotation_requires_new_version_and_fresh_postqualification_entropy",
        "compromised_v2_must_remain_append_only",
    ), "private disclosure and irreversible rotation controls")
    require(disclosure == {
        "private_outputs_encrypted_before_disclosure": True,
        "candidate_authors_can_read_private_cases": False,
        "candidate_authors_can_read_seed": False,
        "allow_commitment_publication_only": True,
        "retire_and_rekey_on_premature_proposal_or_case_read": True,
        "retire_and_rekey_on_seed_disclosure": True,
        "retire_and_rekey_on_candidate_set_change": True,
        "retire_and_rekey_on_independence_or_replay_failure": True,
        "rotation_requires_new_version_and_fresh_postqualification_entropy": True,
        "compromised_v2_must_remain_append_only": True,
    }, "require strict disclosure, append-only retirement, and future reseeding")
    physical = exact_keys(plan["physical_source_wall"], (
        "deny_by_default", "allow_only_explicit_v3_public_owner_reads",
        "legacy_v2_metadata_stat_limit", "legacy_v2_content_read_limit",
        "final_proposal_or_case_read_limit", "candidate_execution_limit",
        "native_load_limit", "process_creation_limit", "network_access_limit",
        "clock_sample_limit", "entropy_read_limit", "workspace_write_limit",
        "dynamic_import_or_execution_limit", "no_recursive_search",
    ), "physical deny-default source wall")
    require(physical == {
        "deny_by_default": True, "allow_only_explicit_v3_public_owner_reads": True,
        "legacy_v2_metadata_stat_limit": 1, "legacy_v2_content_read_limit": 0,
        "final_proposal_or_case_read_limit": 0, "candidate_execution_limit": 0,
        "native_load_limit": 0, "process_creation_limit": 0,
        "network_access_limit": 0, "clock_sample_limit": 0,
        "entropy_read_limit": 0, "workspace_write_limit": 0,
        "dynamic_import_or_execution_limit": 0, "no_recursive_search": True,
    }, "require no final proposal/case/candidate/native/process/clock/write access")


def verify_gates_and_counters(plan: dict) -> None:
    gates = plan["verification_gates"]
    require(type(gates) is list and len(gates) == 4,
            "require exactly four normal/sterile source-only gates")
    for row, expected in zip(gates, (
            ("contract_normal", "normal", "contract", ("python3", "-B", SOURCE,
                                                        "--gate", "contract")),
            ("contract_sterile", "sterile", "contract", ("python3", "-I", "-S", "-B",
                                                           SOURCE, "--gate", "contract")),
            ("wall_normal", "normal", "wall", ("python3", "-B", SOURCE,
                                                "--gate", "wall")),
            ("wall_sterile", "sterile", "wall", ("python3", "-I", "-S", "-B",
                                                   SOURCE, "--gate", "wall")),
    )):
        gate = exact_keys(row, ("id", "mode", "gate", "command"), "verification gate")
        require(gate["id"] == expected[0] and gate["mode"] == expected[1]
                and gate["gate"] == expected[2]
                and type(gate["command"]) is list
                and tuple(gate["command"]) == expected[3],
                "require exact independent normal/sterile contract/wall gates")
    counters = exact_keys(plan["execution_counters"], (
        "private_cases_generated", "expected_results_generated", "entropy_samples",
        "seed_commitments_generated", "protected_proposal_or_case_reads",
        "candidate_runs", "native_loads", "child_processes", "clock_samples",
        "workspace_writes",
    ), "zero protected execution counters")
    require(all(type(value) is int and value == 0 for value in counters.values()),
            "reject seed generation, case generation, candidate execution, timing, or writes")


def verify_contract(wall: SourceWall) -> dict:
    source = read_owner(wall, SOURCE)
    protocol = read_owner(wall, PROTOCOL)
    plan_raw = read_owner(wall, PUBLIC_PLAN)
    require(len(protocol) == PROTOCOL_BYTES and sha256(protocol) == PROTOCOL_SHA256,
            "reject unauthenticated V3 public protocol")
    require(len(plan_raw) == PUBLIC_PLAN_BYTES and sha256(plan_raw) == PUBLIC_PLAN_SHA256,
            "reject unauthenticated V3 public planning metadata")
    require(source.startswith(b"#!/usr/bin/env python3\n")
            and b"--freeze" in source and b"FREEZE_REFUSED" in source
            and RETIRED_V2_PREVIOUSLY_AUTHENTICATED_SHA256.encode("ascii") in source,
            "require source-owned physical wall and permanently refused freeze mode")
    for marker in (b"PROPOSAL", b"NOT FROZEN", b"NOT GENERATED", b"226,492,416",
                   b"4,096", b"three", b"RETIRED / COMPROMISED"):
        require(marker in protocol, "require authenticated explicit public protocol marker")
    parsed = StrictJson(plan_raw).parse()
    plan = exact_keys(parsed, (
        "schema", "version", "status", "frozen", "generation_authorized",
        "freeze_mode_implemented", "owner_paths", "incident", "holdout_reservoir",
        "coverage", "fixed_category_weights", "paired_holdout_cohorts",
        "cohort_marginal_quotas", "candidate_qualification", "post_correctness_entropy",
        "domain_separation", "deterministic_generation", "disclosure_and_rotation",
        "physical_source_wall", "verification_gates", "execution_counters",
    ), "V3 public proposal")
    require(plan["schema"] == "rebar-expanded-sealed-holdout-v3-public-proposal"
            and plan["version"] == 3
            and plan["status"] == "PROPOSAL_NOT_FROZEN_NOT_GENERATED"
            and plan["frozen"] is False
            and plan["generation_authorized"] is False
            and plan["freeze_mode_implemented"] is False,
            "require a strictly public, unfrozen, unauthorized, ungenerated proposal")
    exact_list(plan["owner_paths"], (SOURCE, PROTOCOL, PUBLIC_PLAN),
               "exact three public source owners")
    verify_incident(plan)
    verify_reservoir(plan)
    verify_coverage(plan)
    verify_cohorts(plan)
    verify_qualification_and_entropy(plan)
    verify_derivation_disclosure_and_wall(plan)
    verify_gates_and_counters(plan)
    os.lstat(ROOT + "/" + RETIRED_V2)
    require(wall.retired_stat_count == 1 and wall.retired_open_count == 0
            and len(wall.opened) == 3 and not wall.owner_descriptors,
            "require exactly three owner reads and one unopened retired metadata probe")
    clean_imports()
    return {
        "source_sha256": sha256(source), "protocol_sha256": sha256(protocol),
        "public_plan_sha256": sha256(plan_raw), "case_count": CASE_COUNT,
        "full_sweep_batches": FULL_SWEEP_BATCHES, "cohort_case_count": COHORT_CASES,
        "independent_candidate_families_required": MINIMUM_CANDIDATE_FAMILIES,
    }


def expect_rejected(wall: SourceWall, label: str, action) -> None:
    count = sum(wall.blocked.values())
    try:
        action()
    except ProposalError:
        require(sum(wall.blocked.values()) == count + 1,
                "require physically recorded denied action: " + label)
        return
    raise ProposalError("source wall unexpectedly permitted " + label)


def verify_physical_denials(wall: SourceWall) -> int:
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
    denied = (
        ("retired-direct-descriptor",
         lambda: wall._open(ROOT + "/" + RETIRED_V2, flags)),
        ("retired-builtin-file", lambda: wall._builtin_open(ROOT + "/" + RETIRED_V2, "rb")),
        ("final-private-proposal",
         lambda: os.open(ROOT + "/oracle/phase3/final-sealed-holdout-v3.json", flags)),
        ("legacy-case-content",
         lambda: os.open(ROOT + "/oracle/phase3/expected-v2.json", flags)),
        ("owner-reopen-bypass", lambda: wall._open(ROOT + "/" + SOURCE, flags)),
        ("broad-directory-search", lambda: os.listdir(ROOT + "/oracle")),
        ("workspace-write", lambda: os.open(ROOT + "/oracle/phase3/v3-forbidden-output",
                                             os.O_WRONLY | os.O_CREAT | os.O_EXCL)),
        ("io-bypass", lambda: _io.open(ROOT + "/" + RETIRED_V2, "rb")),
        ("repeat-retired-stat", lambda: os.lstat(ROOT + "/" + RETIRED_V2)),
        ("generic-retired-stat", lambda: os.stat(ROOT + "/" + RETIRED_V2)),
        ("future-os-entropy", lambda: os.urandom(32)),
        ("clock-sample", lambda: time.time()),
        ("nanosecond-clock-sample", lambda: time.perf_counter_ns()),
        ("matcher-import", lambda: sys.audit("import", "re", None)),
        ("candidate-process", lambda: sys.audit("subprocess.Popen", "candidate", (), None)),
        ("native-binary", lambda: sys.audit("ctypes.dlopen", "candidate-native")),
        ("network-delegation", lambda: sys.audit("socket.connect", "external")),
        ("dynamic-execution", lambda: sys.audit("exec", "foreign")),
        ("secondary-audit-hook", lambda: sys.addaudithook(lambda *_args: None)),
        ("destructive-mutation", lambda: sys.audit("os.remove", ROOT + "/forbidden", -1)),
    )
    for label, action in denied:
        expect_rejected(wall, label, action)
    require(wall.retired_stat_count == 1 and wall.retired_open_count == 0
            and not wall.owner_descriptors,
            "physical rejection probes must not open protected proposals or cases")
    clean_imports()
    return len(denied)


def arguments(argv: list[str]) -> str:
    if argv == ["--freeze"]:
        return "freeze"
    if len(argv) == 2 and argv[0] == "--gate" and argv[1] in ("contract", "wall"):
        return argv[1]
    raise ProposalError("usage: --gate contract | --gate wall | --freeze (always refused)")


def main() -> int:
    try:
        gate = arguments(sys.argv[1:])
        clean_imports()
        wall = SourceWall()
        wall.install()
        if gate == "freeze":
            raise ProposalError(
                "FREEZE_REFUSED: no authority, no seed, no protected reads, and fewer than "
                "three independently qualified locked candidate families"
            )
        report = verify_contract(wall)
        denial_probes = verify_physical_denials(wall) if gate == "wall" else 0
        require(wall.retired_stat_count == 1 and wall.retired_open_count == 0
                and len(wall.opened) == 3 and not wall.owner_descriptors,
                "final physical wall accounting must stay source-only")
        report.update({
            "gate": gate,
            "interpreter_mode": "sterile" if sys.flags.isolated and sys.flags.no_site
                                else "normal",
            "status": "PROPOSAL_NOT_FROZEN_NOT_GENERATED",
            "seed_exists": False, "seed_commitment": None,
            "private_cases_generated": 0, "expected_results_generated": 0,
            "retired_v2_metadata_stats": wall.retired_stat_count,
            "retired_v2_content_reads": wall.retired_open_count,
            "protected_proposal_or_case_reads": 0,
            "candidate_runs": 0, "native_loads": 0, "child_processes": 0,
            "clock_samples": 0, "entropy_samples": 0, "workspace_writes": 0,
            "physical_denial_probes": denial_probes,
            "physically_blocked_categories": dict(wall.blocked),
        })
        sys.stdout.write(canonical(report) + "\n")
        return 0
    except (ProposalError, OSError, UnicodeError, ValueError, TypeError) as error:
        sys.stderr.write("expanded sealed holdout V3 failed closed: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
