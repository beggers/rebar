#!/usr/bin/env python3
"""Freeze CPython's real 2-GiB regex tests without running a regex engine."""

from __future__ import annotations

import sys


_BOOT_MODULES = frozenset(sys.modules)
if "re" in _BOOT_MODULES or "_sre" in _BOOT_MODULES:
    raise SystemExit("large-input source freeze requires no re or _sre import")

import ast
import builtins
import hashlib
import os
import stat


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
STDLIB_RE = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/re/__init__.py"
)
SCHEMA = "rebar-python-re-large-input-indexing-v1"
SOURCE = "tools/verify_large_input_indexing_v1.py"
PROTOCOL = "oracle/phase1/P0-LARGE-INPUT-INDEXING-V1.md"
CONTRACT = "oracle/phase1/p0-large-input-indexing-v1.json"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
MATRIX_SHA256 = "a105aea287d093ff977819dda8971f592c3ed396eabd3133e5c52838ce8e2f65"
OVERVIEW_VERSION = 46
ORIGINAL_CASES = 31_237
ORIGINAL_SUITES = 13
PRIVATE_WAIVERS = 13
SIGNATURE_CASES = 50
PUBLIC_ENTRYPOINT_CASES = 32
LARGE_SUBJECT_SIZE = 2_147_483_648
LARGE_SUBN_COUNT = 2_147_483_649
ORIGINAL_CANDIDATE_MAXIMUM = 5_147
FULL_REFERENCE_ALLOWANCE = 42_949_672_960
MIN_AVAILABLE_HOST_BYTES = 42_949_672_961
PLANNED_HOLDOUT_CASES = 4_194_304
MAX_JSON_BYTES = 4 * 1024 * 1024
MAX_JSON_DEPTH = 48
MAX_OWNER_BYTES = 40 * 1024 * 1024


OWNERS = (
    ("goal", "GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756),
    ("public_entrypoint", "rebar.py", "289769bd637ea525ae7e71d263377e15c0f394ba20619c11b98e266f57fcc34f", 212),
    ("project_configuration", "pyproject.toml", "7d50e8c6c2bc76a0e3ddcac6b5f157b013bcfd76944fdeb2c1c81e0181ae7825", 224),
    ("historical_zig_adapter", "candidates/zig_candidate.py", "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862", 68422),
    ("original_p0_inventory", "oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632),
    ("original_p0_protocol", "oracle/phase1/P0-COMPLETENESS-V1.md", "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798", 10392),
    ("additional_signature_inventory", "oracle/phase1/p0-callable-introspection-v1.json", "e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349", 14749),
    ("additional_signature_protocol", "oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md", "1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8", 8952),
    ("actual_signature_reference_receipt", "oracle/phase1/evidence/callable-introspection-reference-v2-cpython-3.14.6-publication-receipt.json", "29b4a389e1b99cce15f07069ee1a0895f193e13400f944a037a4f42832619334", 3533),
    ("first_party_source_inventory", "oracle/phase2/candidate-independence-v2.json", "89662570a643d94ae1581393ed48015c6fa78d5dbe5ad0419e9a2032e4609659", 8798),
    ("first_party_source_protocol", "oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md", "80a1de729c067da36648dcfb9751f7bd3833ff561956df9ad82fc6106a19a16b", 6194),
    ("released_zig_v1_worker", "tools/run_frozen_zig_original_p0_candidate_worker_v1.py", "ddafdc5b1fe06dbfa6449cbfde768d7fee6d16953b3c769c1e30aa600e3c62f9", 123801),
    ("released_zig_v1_controller", "tools/run_frozen_zig_original_p0_candidate_v1.py", "8c9be13232fdbab7ff01b2313a816fd80e033fb5b6d0bf3d8cb07444eeba4856", 55722),
    ("released_zig_v1_protocol", "oracle/phase2/ZIG-ORIGINAL-P0-CANDIDATE-PROTOCOL-V1.md", "294dfb6bc8e286d8415b329f8b2918b856ab3b2d1afb8261e3e04663028fda3c", 9040),
    ("released_zig_v1_contract", "oracle/phase2/zig-original-p0-candidate-protocol-v1.json", "1ff289540457ecba4e91b3b9491b3c42872a5db09b95815b8f58fcdc34315470", 19592),
    ("public_entrypoint_oracle_source", "tools/verify_public_entrypoint_import_v1.py", "c0a61c4cf520e82bf0c327a17c06daf64f57a1dcfd20b37c6e9f7b84177108b4", 83957),
    ("public_entrypoint_oracle_protocol", "oracle/phase1/P0-PUBLIC-ENTRYPOINT-IMPORT-V1.md", "01ace52c6285142733bdcb2b4556feb43226e01c8b181b84019b8fa8c42697c0", 7991),
    ("public_entrypoint_oracle_contract", "oracle/phase1/p0-public-entrypoint-import-v1.json", "b80ba35a6af481f0dd1c5b9141e2995f7b0ffd12f8ffa7060bab50344ddbda47", 9823),
    ("upstream_original_test", "oracle/cpython-3.14.6/test_re.py", "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2", 150895),
    ("upstream_original_accounting", "oracle/cpython-3.14.6/manifest-v5.json", "41b598475a6f756bf63dcd71141d602da05ebb7a810525c45b6c07635b78c0d7", 75694),
    ("upstream_original_accounting_protocol", "oracle/cpython-3.14.6/UPSTREAM-ACCOUNTING-V5.md", "21e77143bbec1f54faa6fc8a74a842808e32bd36815802a0df3ddfef11c597e1", 9201),
    ("upstream_original_accounting_verifier", "tools/verify_original_cpython_accounting_v1.py", "f562ab8c998197880590487fa6e78f511db5c01596ab35731185ca8caead454c", 136758),
    ("bounded_original_candidate_controller", "tools/independent_original_cpython_suite_v5.py", "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce", 123750),
    ("current_overview_renderer", "tools/render_candidate_current_overview_v46.py", "ddb25b70d9f87ad3b6eabbc7c2917a434739931ad2f5b5d194b5cb25706a9334", 78101),
    ("current_overview_inputs", "docs/evidence/candidate-current-overview-v46.inputs.json", "c0633ec12f5aad3d0e0fb8fe29f143ccb6801ec63d5960c85afd47d982c4653d", 382381),
    ("current_overview_summary", "docs/evidence/candidate-current-overview-v46.json", "ec5ecbbcb765bb845a133ad81d02312eb29e6b18718d5e4b346ff10e74c10b3f", 1073582),
    ("current_overview_svg", "docs/evidence/candidate-current-overview-v46.svg", "913f8af0eae80bc48640551b589556a685f81b69f218783afc04e8d7e3746c14", 16635),
    ("repaired_rust_v7_source", "tools/run_owned_repaired_rust_original_campaign_v7.py", "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104", 505616),
    ("repaired_rust_v7_protocol", "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V7.md", "0b5182a7eee74e586839abc3a0e8bdd122bac248e9cb3b76c603c5add9281840", 8433),
    ("repaired_rust_v7_contract", "oracle/phase2/repaired-rust-original-campaign-v7.json", "9c8e85dcc5dcf0a00953b36dd02c29c2ab7b1ed0b4281eb27f6693c058d155e5", 46385),
    ("pinned_python_executable", PYTHON, "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016", 32387816),
    ("pinned_stdlib_re_source", STDLIB_RE, "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35", 17876),
)

CASE_ROWS = (
    ("large-source.clean-engine-freeze", "PASS"),
    ("large-source.physical-effect-wall", "PASS"),
    ("large-source.authenticated-upstream-source", "PASS"),
    ("large-source.exact-search-decorator", "PASS"),
    ("large-source.exact-subn-decorator", "PASS"),
    ("large-source.exact-search-semantics", "PASS"),
    ("large-source.exact-subn-semantics", "PASS"),
    ("large-reference.distinct-original-processes", "PASS"),
    ("large-reference.original-search-2g", "PASS"),
    ("large-reference.original-subn-2g", "PASS"),
    ("large-reference.original-40g-admission", "PASS"),
    ("large-reference.release-debug-skip-not-waiver", "PASS"),
    ("large-candidate.actual-input-cap-5147", "PASS"),
    ("large-candidate.actual-search-2g", "NOT RUN"),
    ("large-candidate.actual-subn-2g", "NOT RUN"),
    ("large-candidate.full-resource-qualification", "NOT ESTABLISHED"),
    ("preserved.original-31237-denominator", "PASS"),
    ("preserved.original-13-suite-denominator", "PASS"),
    ("preserved.original-13-private-waivers", "PASS"),
    ("preserved.signature-50-separate", "PASS"),
    ("preserved.signature-two-reference-pass", "PASS"),
    ("preserved.signature-candidate", "NOT RUN"),
    ("preserved.public-entrypoint-32-separate", "PASS"),
    ("preserved.public-entrypoint-actual-observation", "FAIL"),
    ("preserved.rust-v6-failure-and-archive-effect", "PASS"),
    ("preserved.rust-v7-no-archive-inflation", "PASS"),
    ("safety.future-resource-gated-worker-not-started", "PASS"),
    ("safety.native-runtime-no-delegation", "NOT ESTABLISHED"),
    ("safety.native-memory", "NOT MEASURED"),
    ("safety.native-undefined-behavior", "NOT MEASURED"),
    ("performance.end-to-end", "NOT MEASURED"),
    ("performance.final-holdout", "NOT OPENED"),
)


class FreezeError(Exception):
    """The independently pinned large-input source freeze failed closed."""


_AUDIT_INSTALLED = False
_BLOCKED_AUDIT_EVENTS: dict[str, int] = {}


def require(condition: object, message: str) -> None:
    if not condition:
        raise FreezeError(message)


def no_engine_imports() -> None:
    require("re" not in sys.modules and "_sre" not in sys.modules,
            "large-input source freeze imported a Python regex engine")
    require(not any(name == "rebar" or name.startswith("rebar.") or
                    name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "large-input source freeze imported an entrypoint or candidate")


def source_paths() -> frozenset[str]:
    result = {ROOT + "/" + SOURCE, ROOT + "/" + PROTOCOL,
              ROOT + "/" + CONTRACT}
    for _name, path, _sha256, _size in OWNERS:
        result.add(path if path.startswith("/") else ROOT + "/" + path)
    return frozenset(result)


def block(event: str, reason: str) -> None:
    _BLOCKED_AUDIT_EVENTS[event] = _BLOCKED_AUDIT_EVENTS.get(event, 0) + 1
    raise FreezeError("large-input source-only wall blocked " + event + ": " + reason)


def source_audit_hook(event: str, arguments: tuple[object, ...]) -> None:
    if event == "open":
        path = arguments[0] if arguments else None
        flags = arguments[2] if len(arguments) > 2 else None
        if type(path) is not str or path not in source_paths():
            block(event, "read is not one of the exact frozen source owners")
        if type(flags) is not int:
            block(event, "only exact read-only file opens are admitted")
        forbidden = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC |
                     os.O_APPEND | getattr(os, "O_TMPFILE", 0))
        if flags & forbidden:
            block(event, "all source writes and creations are forbidden")
        return
    if event == "compile":
        raw = arguments[0] if arguments else None
        label = arguments[1] if len(arguments) > 1 else None
        if (label not in {"oracle/cpython-3.14.6/test_re.py",
                          "<large-input-self-test>"} or
                type(raw) not in (str, bytes) or len(raw) > MAX_JSON_BYTES):
            block(event, "only bounded, authenticated upstream AST parsing is admitted")
        return
    if event == "import":
        block(event, "imports are prohibited after the clean bootstrap")
    if (event == "exec" or event.startswith("ctypes.") or
            event.startswith("subprocess.") or event.startswith("socket.") or
            event.startswith("multiprocessing.") or event.startswith("threading.") or
            event.startswith("time.") or event in {
                "os.system", "os.fork", "os.forkpty", "os.posix_spawn",
                "os.spawn", "os.exec", "os.chdir", "os.putenv", "os.unsetenv",
                "os.remove", "os.rename", "os.replace", "os.mkdir", "os.rmdir",
                "os.symlink", "os.link", "os.chmod", "os.chown", "os.truncate",
                "os.utime", "code.__new__", "function.__new__", "marshal.loads",
            }):
        block(event, "native, process, network, clocks and mutation are forbidden")


def install_audit_wall() -> None:
    global _AUDIT_INSTALLED
    require(not _AUDIT_INSTALLED, "the physical source-only wall was installed twice")
    no_engine_imports()
    sys.addaudithook(source_audit_hook)
    _AUDIT_INSTALLED = True
    no_engine_imports()


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def quote(value: str) -> str:
    require(type(value) is str, "a canonical JSON string must be a string")
    result = ['"']
    escaped = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
               "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    for character in value:
        point = ord(character)
        if character in escaped:
            result.append(escaped[character])
        elif point < 0x20 or 0x7F <= point <= 0xFFFF:
            result.append("\\u" + format(point, "04x"))
        elif point > 0xFFFF:
            point -= 0x10000
            result.append("\\u" + format(0xD800 + (point >> 10), "04x"))
            result.append("\\u" + format(0xDC00 + (point & 0x3FF), "04x"))
        else:
            result.append(character)
    result.append('"')
    return "".join(result)


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= MAX_JSON_DEPTH, "canonical JSON exceeded its depth allowance")
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
        require(value == value and abs(value) != float("inf"),
                "canonical JSON rejected a nonfinite number")
        return repr(value)
    if type(value) in (tuple, list):
        return "[" + ",".join(canonical(item, depth + 1)
                               for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value),
                "canonical JSON rejected a non-string object key")
        return "{" + ",".join(quote(key) + ":" +
                               canonical(value[key], depth + 1)
                               for key in sorted(value)) + "}"
    raise FreezeError("unsupported canonical JSON value: " + type(value).__name__)


class StrictJSON:
    """Decode bounded, duplicate-key-free JSON without importing json or re."""

    def __init__(self, raw: bytes):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_JSON_BYTES,
                "JSON was empty or exceeded the frozen source byte allowance")
        try:
            self.text = raw.decode("utf-8", "strict")
        except UnicodeError as error:
            raise FreezeError("JSON must be strictly valid UTF-8") from error
        self.index = 0

    def whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def string(self) -> str:
        require(self.text[self.index:self.index + 1] == '"',
                "a strictly quoted JSON string is mandatory")
        self.index += 1
        result: list[str] = []
        short = {'"': '"', "\\": "\\", "/": "/", "b": "\b",
                 "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
        while self.index < len(self.text):
            character = self.text[self.index]
            self.index += 1
            if character == '"':
                return "".join(result)
            if character != "\\":
                require(ord(character) >= 0x20,
                        "an unescaped JSON string control character is forbidden")
                require(not 0xD800 <= ord(character) <= 0xDFFF,
                        "an unpaired literal JSON surrogate is forbidden")
                result.append(character)
                continue
            require(self.index < len(self.text), "incomplete JSON string escape")
            escaped = self.text[self.index]
            self.index += 1
            if escaped != "u":
                require(escaped in short, "unknown JSON string escape")
                result.append(short[escaped])
                continue
            digits = self.text[self.index:self.index + 4]
            require(len(digits) == 4 and
                    all(char in "0123456789abcdefABCDEF" for char in digits),
                    "invalid four-digit JSON Unicode escape")
            self.index += 4
            point = int(digits, 16)
            if 0xD800 <= point <= 0xDBFF:
                require(self.text[self.index:self.index + 2] == "\\u",
                        "an unpaired high JSON Unicode surrogate is forbidden")
                lower = self.text[self.index + 2:self.index + 6]
                require(len(lower) == 4 and
                        all(char in "0123456789abcdefABCDEF" for char in lower),
                        "invalid low JSON Unicode surrogate")
                low = int(lower, 16)
                require(0xDC00 <= low <= 0xDFFF,
                        "an unpaired high JSON Unicode surrogate is forbidden")
                self.index += 6
                result.append(chr(0x10000 + ((point - 0xD800) << 10)
                                  + low - 0xDC00))
            else:
                require(not 0xDC00 <= point <= 0xDFFF,
                        "an unpaired low JSON Unicode surrogate is forbidden")
                result.append(chr(point))
        raise FreezeError("unterminated JSON string")

    def number(self) -> int | float:
        start = self.index
        if self.text[self.index:self.index + 1] == "-":
            self.index += 1
        require(self.index < len(self.text), "an incomplete JSON number is forbidden")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index == len(self.text) or
                    self.text[self.index] not in "0123456789",
                    "JSON numbers cannot contain leading zeroes")
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
            require(self.index > begin, "an incomplete JSON fraction is forbidden")
        if self.text[self.index:self.index + 1] in ("e", "E"):
            floating = True
            self.index += 1
            if self.text[self.index:self.index + 1] in ("+", "-"):
                self.index += 1
            begin = self.index
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
            require(self.index > begin, "an incomplete JSON exponent is forbidden")
        token = self.text[start:self.index]
        require(len(token) <= 128, "a JSON number exceeded its frozen digit bound")
        if not floating:
            return int(token)
        result = float(token)
        require(result == result and abs(result) != float("inf"),
                "a nonfinite JSON number is forbidden")
        return result

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "JSON exceeded its frozen nesting depth")
        self.whitespace()
        require(self.index < len(self.text), "missing JSON value")
        character = self.text[self.index]
        if character == '"':
            return self.string()
        if character == "{":
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
                require(self.text[self.index:self.index + 1] == ":",
                        "a JSON object member must have a colon")
                self.index += 1
                result[key] = self.value(depth + 1)
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "}":
                    return result
                require(separator == ",", "invalid JSON object separator")
        if character == "[":
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
        if character == "-" or character in "0123456789":
            return self.number()
        for literal, result in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(literal, self.index):
                self.index += len(literal)
                return result
        raise FreezeError("unrecognized JSON literal")

    def decode(self) -> object:
        result = self.value()
        self.whitespace()
        require(self.index == len(self.text),
                "trailing JSON content or a second document is forbidden")
        return result


def decode_json(raw: bytes) -> object:
    return StrictJSON(raw).decode()


def owner_mapping() -> dict[str, dict[str, object]]:
    return {name: {"path": path, "sha256": expected, "bytes": size}
            for name, path, expected, size in OWNERS}


def read_exact(path: str, expected_hash: str, expected_size: int) -> bytes:
    require(type(path) is str and type(expected_size) is int and
            0 < expected_size <= MAX_OWNER_BYTES,
            "a bounded exact source owner path or size was substituted")
    absolute = path if path.startswith("/") else ROOT + "/" + path
    require(absolute in source_paths(),
            "an attempted read was not an exact frozen source owner")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) |
             getattr(os, "O_NOFOLLOW", 0))
    try:
        descriptor = os.open(absolute, flags)
    except OSError as error:
        raise FreezeError("cannot authenticate source owner: " + path) from error
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and before.st_size == expected_size,
                "source owner size or regular-file identity changed: " + path)
        pieces: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(1_048_576,
                                            expected_size + 1 - total))
            if not chunk:
                break
            pieces.append(chunk)
            total += len(chunk)
            require(total <= expected_size,
                    "a source owner grew during authenticated reading: " + path)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    require(total == expected_size and
            (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns),
            "a source owner was replaced during authenticated reading: " + path)
    raw = b"".join(pieces)
    require(digest(raw) == expected_hash,
            "source owner SHA-256 did not match: " + path)
    return raw


def read_self(relative: str, expected_hash: str) -> bytes:
    absolute = ROOT + "/" + relative
    try:
        info = os.stat(absolute, follow_symlinks=False)
    except OSError as error:
        raise FreezeError("a required large-input freeze owner is missing: " +
                          relative) from error
    require(stat.S_ISREG(info.st_mode) and 0 < info.st_size <= MAX_JSON_BYTES,
            "a large-input freeze owner is not a bounded regular file: " + relative)
    return read_exact(relative, expected_hash, info.st_size)


def expected_original() -> dict[str, object]:
    return {
        "case_execution_denominator": ORIGINAL_CASES,
        "suite_count": ORIGINAL_SUITES,
        "private_waiver_count": PRIVATE_WAIVERS,
        "additional_signature_case_count": SIGNATURE_CASES,
        "additional_signature_in_original_denominator": False,
        "public_entrypoint_source_case_count": PUBLIC_ENTRYPOINT_CASES,
        "public_entrypoint_cases_in_original_denominator": False,
        "public_entrypoint_cases_in_signature_denominator": False,
        "large_input_source_cases_in_original_denominator": False,
        "original_denominator_changed": False,
    }


def expected_runtime() -> dict[str, object]:
    return {
        "implementation": "CPython",
        "python_version": "3.14.6",
        "executable": PYTHON,
        "executable_sha256":
            "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
        "stdlib_re_source": STDLIB_RE,
        "stdlib_re_source_sha256":
            "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35",
        "isolated": True,
        "bytecode_writes": False,
    }


def expected_upstream() -> dict[str, object]:
    return {
        "case_count": 2,
        "subject_size": LARGE_SUBJECT_SIZE,
        "subject_code_point": "a",
        "source_case_matrix_included_in_original_denominator": False,
        "source_execution": "AST ONLY; NO REGEX MATCHING",
        "cases": [
            {
                "id": "ReTests.test_large_search",
                "decorator": "bigmemtest(size=_2G, memuse=1)",
                "memuse": 1,
                "api": "re.search",
                "pattern": "$",
                "expected_match_start": LARGE_SUBJECT_SIZE,
                "expected_match_end": LARGE_SUBJECT_SIZE,
            },
            {
                "id": "ReTests.test_large_subn",
                "decorator": "bigmemtest(size=_2G, memuse=16 + 2)",
                "memuse": 18,
                "api": "re.subn",
                "pattern": "",
                "replacement": "",
                "expected_result_equals_original_subject": True,
                "expected_replacement_count": LARGE_SUBN_COUNT,
            },
        ],
    }


def expected_reference() -> dict[str, object]:
    return {
        "status": "PASS; HISTORICAL PINNED MANIFEST EVIDENCE",
        "executed_by_this_source_oracle": False,
        "reference_process_count": 2,
        "reference_roles": ["reference_a", "reference_b"],
        "passing_public_methods_per_reference": 151,
        "failing_public_methods_per_reference": 0,
        "release_debug_skips_per_reference": 1,
        "release_debug_skip_is_private_waiver": False,
        "large_search_subject_size": LARGE_SUBJECT_SIZE,
        "large_subn_subject_size": LARGE_SUBJECT_SIZE,
        "real_max_memory_bytes": FULL_REFERENCE_ALLOWANCE,
        "exclusive_big_memory_worker": True,
        "reference_report": {
            "path": "oracle/cpython-3.14.6/evidence/postfinal-locale-v5-self-oracle.json",
            "sha256":
                "3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916",
        },
        "reference_report_read_by_this_source_oracle": False,
    }


def expected_candidate() -> dict[str, object]:
    return {
        "original_controller_bigmem_dry_run": True,
        "original_controller_maximum_subject_size": ORIGINAL_CANDIDATE_MAXIMUM,
        "full_resource_large_search": "NOT RUN",
        "full_resource_large_subn": "NOT RUN",
        "full_resource_candidate_qualification": "NOT ESTABLISHED",
        "large_candidate_workers_started_by_this_source_oracle": 0,
        "candidate_qualified": False,
    }


def expected_public() -> dict[str, object]:
    return {
        "case_count": PUBLIC_ENTRYPOINT_CASES,
        "case_matrix_sha256":
            "f67f8d4d62f9939c94250ad2e4df55b14df013df7212aa66930ecc3a772d2a58",
        "source_freeze_status": "PASS",
        "actual_observed_status": "FAIL",
        "actual_classification": "UNQUALIFIED_ZIG_PROTOTYPE",
        "public_module_version_status": "FAIL/MISSING",
        "public_entrypoint_qualified": False,
        "case_matrix_in_original_denominator": False,
        "case_matrix_in_signature_denominator": False,
    }


def expected_rust() -> dict[str, object]:
    return {
        "actual_v6_controller_status": "FAIL",
        "actual_v6_source_build_archive_read_count": 1,
        "actual_v6_source_build_archive_inflation_count": 1,
        "actual_v6_controller_ledger_omits_source_build_archive_effect": True,
        "corrected_v7_source_sha256":
            "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104",
        "corrected_v7_source_status":
            "SOURCE FROZEN; CORRECTED RUST V13 CANDIDATE NOT RUN",
        "corrected_v7_candidate_matching": "NOT RUN",
        "corrected_v7_source_self_test_control_count": 517,
        "corrected_v7_archive_reads_in_source_freeze": 0,
        "corrected_v7_archive_inflations_in_source_freeze": 0,
    }


def expected_zig_v1() -> dict[str, object]:
    return {
        "source_freeze_status": "SOURCE FROZEN; FIRST-PARTY ZIG CANDIDATE NOT RUN",
        "worker_source_sha256":
            "ddafdc5b1fe06dbfa6449cbfde768d7fee6d16953b3c769c1e30aa600e3c62f9",
        "controller_source_sha256":
            "8c9be13232fdbab7ff01b2313a816fd80e033fb5b6d0bf3d8cb07444eeba4856",
        "protocol_sha256":
            "294dfb6bc8e286d8415b329f8b2918b856ab3b2d1afb8261e3e04663028fda3c",
        "contract_sha256":
            "1ff289540457ecba4e91b3b9491b3c42872a5db09b95815b8f58fcdc34315470",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "actual_candidate_workers": 0,
        "actual_compiler_processes": 0,
        "actual_native_activations": 0,
        "actual_native_libraries_loaded": 0,
        "actual_reference_workers": 0,
        "stdlib_regex_engine_dependency_count": 0,
        "external_regex_package_count": 0,
        "cross_candidate_engine_dependency_count": 0,
        "matching_fallback_count": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "frozen_corrected_runner_source_families": ["c", "rust", "zig"],
        "frozen_corrected_runner_source_family_count": 3,
        "actually_runnable_candidate_families": [],
        "actually_runnable_candidate_family_count": 0,
        "dedicated_corrected_runnable_families": [],
        "dedicated_corrected_runnable_family_count": 0,
    }


def expected_policy() -> dict[str, object]:
    return {
        "execution_implemented_in_this_source_oracle": False,
        "reference_execution_mode": "NOT IMPLEMENTED",
        "candidate_execution_mode": "NOT IMPLEMENTED",
        "requires_separately_frozen_owned_worker_source": True,
        "requires_separately_authenticated_worker_source": True,
        "requires_explicit_available_host_memory_admission": True,
        "available_host_memory_must_be_strictly_greater_than_bytes":
            FULL_REFERENCE_ALLOWANCE,
        "minimum_available_host_memory_bytes": MIN_AVAILABLE_HOST_BYTES,
        "requires_independent_worker_resource_limit": True,
        "requires_independent_worker_timeout": True,
        "requires_exact_pinned_python_interpreter": True,
        "requires_exact_original_upstream_methods": True,
        "requires_exact_subject_size": LARGE_SUBJECT_SIZE,
        "requires_exact_search_start_and_end": LARGE_SUBJECT_SIZE,
        "requires_exact_subn_count": LARGE_SUBN_COUNT,
        "requires_exact_subn_result_equality": True,
        "requires_complete_stdout_stderr_and_exit_observations": True,
        "requires_isolated_reference_process": True,
        "requires_isolated_candidate_process": True,
        "allows_stdlib_regex_for_reference_only": True,
        "allows_stdlib_regex_for_candidate": False,
        "allows_sre_for_candidate": False,
        "allows_external_regex_engine_for_candidate": False,
        "allows_cross_candidate_engine_for_candidate": False,
        "allows_candidate_fallback": False,
        "requires_first_party_independent_candidate_engine_proof": True,
        "requires_actual_both_large_candidate_cases": True,
        "insufficient_resources_count_as_pass": False,
        "insufficient_resources_status": "NOT RUN; INSUFFICIENT RESOURCES",
        "synthetic_admission_is_actual_candidate_evidence": False,
    }


def expected_boundaries() -> dict[str, object]:
    return {
        "source_freeze_status": "PASS",
        "actual_reference_workers_started": 0,
        "actual_candidate_workers_started": 0,
        "actual_candidate_imports": 0,
        "actual_entrypoint_imports": 0,
        "actual_stdlib_regex_imports": 0,
        "actual_native_libraries_loaded": 0,
        "actual_archives_opened": 0,
        "actual_archives_decompressed": 0,
        "actual_subprocesses_started": 0,
        "actual_network_requests": 0,
        "actual_clock_samples": 0,
        "actual_host_memory_queries": 0,
        "actual_large_subject_allocations": 0,
        "maximum_candidate_subject_allocated": 0,
        "actual_holdout_cases_read": 0,
        "actual_hidden_cases_read": 0,
        "workspace_files_written": 0,
        "physical_audit_hook_required": True,
        "physical_audit_denies_unlisted_reads": True,
        "physical_audit_denies_module_imports": True,
        "physical_audit_denies_native_loading": True,
        "physical_audit_denies_execution_and_processes": True,
        "physical_audit_denies_network_and_writes": True,
        "qualified_candidate_count": 0,
        "winner_selected": False,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "holdout_generated": False,
        "holdout_planned_case_count": PLANNED_HOLDOUT_CASES,
    }


def case_matrix() -> list[dict[str, str]]:
    return [{"id": identity, "status": status}
            for identity, status in CASE_ROWS]


def validate_contract(document: object) -> dict[str, object]:
    require(type(document) is dict, "the frozen large-input contract must be an object")
    required = {
        "schema", "version", "status", "goal_sha256", "pinned_runtime",
        "original_correctness", "upstream_large_input",
        "historical_full_resource_reference", "actual_candidate_large_input",
        "public_entrypoint_preservation", "corrected_rust_preservation",
        "released_zig_v1_preservation",
        "current_overview_version", "owners", "case_matrix",
        "case_matrix_sha256", "future_execution_policy", "boundaries",
    }
    require(set(document) == required,
            "the frozen large-input contract gained or lost a required section")
    require(document.get("schema") == SCHEMA + "-source-freeze" and
            document.get("version") == 1,
            "the versioned large-input source contract was substituted")
    require(document.get("status") ==
            "SOURCE FROZEN; ORIGINAL 2-GIB TESTS AUTHENTICATED; CANDIDATES NOT RUN",
            "source freezing must not claim candidate execution or qualification")
    require(document.get("goal_sha256") == GOAL_SHA256,
            "the immutable original objective was substituted")
    sections = (
        ("pinned_runtime", expected_runtime()),
        ("original_correctness", expected_original()),
        ("upstream_large_input", expected_upstream()),
        ("historical_full_resource_reference", expected_reference()),
        ("actual_candidate_large_input", expected_candidate()),
        ("public_entrypoint_preservation", expected_public()),
        ("corrected_rust_preservation", expected_rust()),
        ("released_zig_v1_preservation", expected_zig_v1()),
        ("future_execution_policy", expected_policy()),
        ("boundaries", expected_boundaries()),
    )
    for name, expected in sections:
        require(document.get(name) == expected,
                "a frozen large-input section changed or omitted a boundary: " + name)
    require(document.get("current_overview_version") == OVERVIEW_VERSION,
            "the exact pushed overview version changed")
    require(document.get("owners") == owner_mapping() and len(OWNERS) == 32,
            "an independently pinned source owner changed or was omitted")
    expected_matrix = case_matrix()
    require(len(expected_matrix) == 32 and
            len({row["id"] for row in expected_matrix}) == 32,
            "the independent large-input source case identities were duplicated")
    require(document.get("case_matrix") == expected_matrix,
            "an independent large-input source observation changed")
    observed_sha256 = digest(canonical(expected_matrix).encode("ascii"))
    require(observed_sha256 == MATRIX_SHA256 and
            document.get("case_matrix_sha256") == MATRIX_SHA256,
            "the exact independent large-input source matrix was substituted")
    return document


def is_name(node: ast.AST, name: str) -> bool:
    return isinstance(node, ast.Name) and node.id == name


def is_constant(node: ast.AST, value: object) -> bool:
    return (isinstance(node, ast.Constant) and
            type(node.value) is type(value) and node.value == value)


def attribute_name(node: ast.AST) -> tuple[str, ...]:
    if isinstance(node, ast.Name):
        return (node.id,)
    if isinstance(node, ast.Attribute):
        base = attribute_name(node.value)
        return base + (node.attr,) if base else ()
    return ()


def exact_call(node: ast.AST, chain: tuple[str, ...], argc: int) -> ast.Call:
    require(isinstance(node, ast.Call) and attribute_name(node.func) == chain and
            len(node.args) == argc and not node.keywords,
            "the exact upstream large-input call changed: " + ".".join(chain))
    return node


def assert_upstream_decorator(method: ast.FunctionDef, memuse: int) -> None:
    require(len(method.decorator_list) == 1 and
            isinstance(method.decorator_list[0], ast.Call),
            "the upstream large-input method lost its sole big-memory decorator")
    decorator = method.decorator_list[0]
    require(is_name(decorator.func, "bigmemtest") and not decorator.args and
            len(decorator.keywords) == 2 and
            [item.arg for item in decorator.keywords] == ["size", "memuse"] and
            is_name(decorator.keywords[0].value, "_2G"),
            "the upstream large-input bigmemtest(size=_2G) changed")
    value = decorator.keywords[1].value
    if memuse == 1:
        require(is_constant(value, 1),
                "the original large-search memory-use expression changed")
    else:
        require(isinstance(value, ast.BinOp) and isinstance(value.op, ast.Add) and
                is_constant(value.left, 16) and is_constant(value.right, 2),
                "the original large-subn memory-use expression 16 + 2 changed")
    args = method.args
    require(len(args.args) == 2 and [item.arg for item in args.args] == ["self", "size"]
            and not args.posonlyargs and not args.kwonlyargs and not args.defaults
            and args.vararg is None and args.kwarg is None,
            "the exact upstream large-input method arguments changed")


def assert_subject(statement: ast.stmt) -> None:
    require(isinstance(statement, ast.Assign) and len(statement.targets) == 1 and
            is_name(statement.targets[0], "s") and
            isinstance(statement.value, ast.BinOp) and
            isinstance(statement.value.op, ast.Mult) and
            is_constant(statement.value.left, "a") and
            is_name(statement.value.right, "size"),
            "the exact upstream subject must remain 'a' * size")


def assert_assertion(statement: ast.stmt, method: str, argc: int) -> ast.Call:
    require(isinstance(statement, ast.Expr),
            "the original upstream large-input assertion was omitted")
    return exact_call(statement.value, ("self", method), argc)


def validate_upstream_large_ast(raw: bytes) -> dict[str, object]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_JSON_BYTES,
            "the pinned upstream test source exceeded its bounded AST allowance")
    try:
        tree = ast.parse(raw.decode("utf-8", "strict"),
                         filename="oracle/cpython-3.14.6/test_re.py", mode="exec")
    except (SyntaxError, UnicodeError) as error:
        raise FreezeError("the upstream original test is not exact Python source") from error
    require(isinstance(tree, ast.Module), "the upstream source is not a Python module")
    supports = [node for node in tree.body
                if isinstance(node, ast.ImportFrom) and node.module == "test.support"]
    require(len(supports) == 1 and
            {item.name for item in supports[0].names}.issuperset({"bigmemtest", "_2G"}),
            "the original upstream bigmemtest and _2G imports were changed")
    classes = [node for node in tree.body
               if isinstance(node, ast.ClassDef) and node.name == "ReTests"]
    require(len(classes) == 1,
            "the unique upstream original ReTests class was substituted")
    methods = {
        name: [node for node in classes[0].body
               if isinstance(node, ast.FunctionDef) and node.name == name]
        for name in ("test_large_search", "test_large_subn")
    }
    require(all(len(items) == 1 for items in methods.values()),
            "an original upstream 2-GiB method was omitted or duplicated")
    search = methods["test_large_search"][0]
    subn = methods["test_large_subn"][0]
    assert_upstream_decorator(search, 1)
    assert_upstream_decorator(subn, 18)

    require(len(search.body) == 5,
            "the exact upstream 2-GiB large-search assertion count changed")
    assert_subject(search.body[0])
    match_statement = search.body[1]
    require(isinstance(match_statement, ast.Assign) and
            len(match_statement.targets) == 1 and
            is_name(match_statement.targets[0], "m"),
            "the original upstream match assignment changed")
    search_call = exact_call(match_statement.value, ("re", "search"), 2)
    require(is_constant(search_call.args[0], "$") and
            is_name(search_call.args[1], "s"),
            "the original large-search end-anchor or exact subject changed")
    not_none = assert_assertion(search.body[2], "assertIsNotNone", 1)
    require(is_name(not_none.args[0], "m"),
            "the original large-search non-null match assertion changed")
    for statement, member in ((search.body[3], "start"),
                              (search.body[4], "end")):
        assertion = assert_assertion(statement, "assertEqual", 2)
        exact_call(assertion.args[0], ("m", member), 0)
        require(is_name(assertion.args[1], "size"),
                "the upstream large-search exact 2-GiB index assertion changed")

    require(len(subn.body) == 4,
            "the exact upstream 2-GiB large-subn assertion count changed")
    assert_subject(subn.body[0])
    substitution = subn.body[1]
    require(isinstance(substitution, ast.Assign) and
            len(substitution.targets) == 1 and
            isinstance(substitution.targets[0], ast.Tuple) and
            len(substitution.targets[0].elts) == 2 and
            is_name(substitution.targets[0].elts[0], "r") and
            is_name(substitution.targets[0].elts[1], "n"),
            "the original large-subn returned result and count were changed")
    call = exact_call(substitution.value, ("re", "subn"), 3)
    require(is_constant(call.args[0], "") and is_constant(call.args[1], "") and
            is_name(call.args[2], "s"),
            "the original large-subn empty pattern, replacement or subject changed")
    returned = assert_assertion(subn.body[2], "assertEqual", 2)
    require(is_name(returned.args[0], "r") and is_name(returned.args[1], "s"),
            "the original large-subn exact returned subject assertion changed")
    counted = assert_assertion(subn.body[3], "assertEqual", 2)
    count = counted.args[1]
    require(is_name(counted.args[0], "n") and isinstance(count, ast.BinOp) and
            isinstance(count.op, ast.Add) and is_name(count.left, "size") and
            is_constant(count.right, 1),
            "the original large-subn exact 2-GiB-plus-one count changed")
    no_engine_imports()
    return {
        "case_count": 2,
        "large_search_method": "ReTests.test_large_search",
        "large_subn_method": "ReTests.test_large_subn",
        "large_search_memuse": 1,
        "large_subn_memuse": 18,
        "exact_subject_size": LARGE_SUBJECT_SIZE,
        "exact_search_start": LARGE_SUBJECT_SIZE,
        "exact_search_end": LARGE_SUBJECT_SIZE,
        "exact_subn_count": LARGE_SUBN_COUNT,
        "actual_regex_engines_imported": 0,
        "actual_large_subject_allocations": 0,
    }


def validate_manifest(document: object) -> None:
    require(type(document) is dict and
            document.get("schema") == "rebar-cpython-original-upstream-accounting-v5"
            and document.get("python") == "3.14.6",
            "the historical full-resource original accounting was substituted")
    require(document.get("pinned_python") == {
        "path": PYTHON,
        "sha256": "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
    }, "the full-resource original reference used a different Python baseline")
    bounded = document.get("bounded_candidate_facing_original_v5")
    require(type(bounded) is dict, "the actual bounded candidate controller was omitted")
    for key, expected in {
        "status": "SOURCE AUTHENTICATED; NOT RUN BY THIS VERIFIER",
        "original_bigmem_dry_run": True,
        "original_bigmem_maximum_size": ORIGINAL_CANDIDATE_MAXIMUM,
        "full_resource_candidate_qualification": "NOT ESTABLISHED",
        "controller": {
            "path": "tools/independent_original_cpython_suite_v5.py",
            "sha256": "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce",
        },
    }.items():
        require(bounded.get(key) == expected,
                "the actual original bounded candidate policy changed: " + key)
    full = document.get("full_resource_postfinal_v5")
    require(type(full) is dict,
            "the actual historical two-reference full-resource accounting was omitted")
    for key, expected in {
        "reference_count": 2,
        "reference_roles": ["reference_a", "reference_b"],
        "passes_per_role": 151,
        "failures_per_role": 0,
        "debug_skips_per_role": 1,
        "genuinely_delivered_large_method_sizes": {
            "ReTests.test_large_search": LARGE_SUBJECT_SIZE,
            "ReTests.test_large_subn": LARGE_SUBJECT_SIZE,
        },
        "real_max_memory_bytes": FULL_REFERENCE_ALLOWANCE,
        "exclusive_big_memory_worker": True,
        "holdout": "NOT ACCESSED",
        "performance": "NOT MEASURED",
        "reference_report": expected_reference()["reference_report"],
    }.items():
        require(full.get(key) == expected,
                "the historical actual two-reference 2-GiB evidence changed: " + key)
    accounting = document.get("source_accounting")
    require(type(accounting) is dict and
            accounting.get("private_method_count") == PRIVATE_WAIVERS and
            accounting.get("public_method_count") == 152 and
            accounting.get("public_method_waivers") == [],
            "the actual original public/private accounting was silently changed")
    debug = accounting.get("release_build_debug_condition")
    require(type(debug) is dict and
            debug.get("method") == "ReTests.test_memory_leaks" and
            debug.get("status") == "SKIP" and
            debug.get("reason") == "requires debug build" and
            debug.get("counts_as_public_waiver") is False,
            "the honest release-build debug skip was changed into a public waiver")


def validate_original_inventory(document: object) -> None:
    require(type(document) is dict and
            document.get("schema") == "rebar-cpython-re-p0-completeness-v1" and
            document.get("version") == 1,
            "the original P0 completeness inventory was substituted")
    denominator = document.get("denominator")
    require(type(denominator) is dict,
            "the complete original 31,237-case denominator was omitted")
    for key in ("final_required_case_execution_denominator",
                "frozen_planned_case_execution_denominator",
                "available_frozen_vector_case_executions"):
        require(denominator.get(key) == ORIGINAL_CASES,
                "the complete original denominator changed: " + key)
    suite_ids = denominator.get("counted_suite_ids")
    require(type(suite_ids) is list and len(suite_ids) == ORIGINAL_SUITES and
            len(set(suite_ids)) == ORIGINAL_SUITES and
            denominator.get("private_upstream_methods_outside_public_denominator") ==
            PRIVATE_WAIVERS and
            denominator.get("public_original_skip_cases_outside_runnable_denominator") == 1,
            "the original suites, private waivers or honest release skip changed")
    runtime = document.get("runtime")
    require(type(runtime) is dict and runtime.get("python_implementation") == "CPython"
            and runtime.get("python_version") == "3.14.6" and
            runtime.get("executable") == {
                "path": PYTHON,
                "sha256": "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
            }, "the exact original P0 stable CPython runtime changed")
    gate = document.get("phase_gate")
    require(type(gate) is dict and gate.get("all_obligations_mapped") is True and
            gate.get("blockers") == [] and
            gate.get("final_holdout_authorized") is False and
            gate.get("phase") == "CORRECTNESS ORACLE" and
            gate.get("status") == "PASS",
            "the original correctness gate or final holdout boundary changed")


def validate_signatures(document: object, receipt: object) -> None:
    require(type(document) is dict and
            document.get("schema") ==
            "rebar-python-re-callable-introspection-v1-source-freeze" and
            document.get("version") == 1,
            "the separately frozen 50 callable obligations were substituted")
    original = document.get("original_correctness")
    require(type(original) is dict and
            original.get("case_execution_denominator") == ORIGINAL_CASES and
            original.get("suite_count") == ORIGINAL_SUITES and
            original.get("private_waiver_count") == PRIVATE_WAIVERS and
            original.get("candidate_facing_large_input_maximum") ==
            ORIGINAL_CANDIDATE_MAXIMUM and
            original.get("full_resource_candidate_2g_search") == "NOT RUN" and
            original.get("full_resource_candidate_2g_subn") == "NOT RUN" and
            original.get("full_resource_reference_allowance_bytes") ==
            FULL_REFERENCE_ALLOWANCE and
            original.get("full_resource_reference_bytes") == LARGE_SUBJECT_SIZE and
            original.get("denominator_modified") is False,
            "the separate signature oracle concealed the real candidate 2-GiB gap")
    obligation = document.get("additional_obligation")
    signature_matrix = "89ff9e5197ac0fee63a5b7f3880d9d66083f7e25255d0d062e14ff84ab5c884b"
    require(type(obligation) is dict and
            obligation.get("case_count") == SIGNATURE_CASES and
            obligation.get("included_in_original_31237_denominator") is False and
            obligation.get("matrix_sha256") == signature_matrix,
            "the additional 50 signatures were merged or substituted")
    require(type(receipt) is dict and
            receipt.get("schema") ==
            "rebar-owned-callable-introspection-reference-v2-durable-publication-receipt"
            and receipt.get("version") == 2,
            "the actual separate signature reference receipt was substituted")
    for key, expected in {
        "status": "PASS",
        "publication_status": "PASS",
        "reference_status": "PASS",
        "reference_failure_count": 0,
        "actual_reference_processes_started": 2,
        "additional_case_count": SIGNATURE_CASES,
        "additional_cases_included_in_original_denominator": False,
        "original_case_denominator": ORIGINAL_CASES,
        "original_suite_count": ORIGINAL_SUITES,
        "original_private_waiver_count": PRIVATE_WAIVERS,
        "candidate_processes_started": 0,
        "candidate_imports": 0,
        "candidate_qualified": False,
        "candidate_introspection": "NOT MEASURED",
        "matrix_sha256": signature_matrix,
        "holdout": "NOT OPENED",
        "holdout_cases_read": 0,
        "clock_samples": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }.items():
        require(receipt.get(key) == expected,
                "the published two-reference signature evidence changed: " + key)
    processes = receipt.get("actual_distinct_process_ids")
    require(type(processes) is list and len(processes) == 2 and
            all(type(item) is int and item > 0 for item in processes) and
            processes[0] != processes[1],
            "the actual signature reference processes were not independent")
    archive = receipt.get("archive")
    require(type(archive) is dict and
            archive.get("path") ==
            "oracle/phase1/evidence/callable-introspection-reference-v2-cpython-3.14.6.json.gz"
            and archive.get("bytes") == 8538 and
            archive.get("sha256") ==
            "7875f249a6cec7910e31800566ef5ccb1ee7398a29a403f307c5de88e647736c",
            "the published signature archive identity changed; it must not be opened")


def validate_public(document: object) -> None:
    require(type(document) is dict and
            document.get("schema") ==
            "rebar-python-re-public-entrypoint-import-v1-source-freeze" and
            document.get("version") == 1,
            "the separately frozen public import contract was substituted")
    require(document.get("goal_sha256") == GOAL_SHA256 and
            document.get("pinned_python") == PYTHON and
            document.get("current_overview_version") == 44,
            "the independently pushed public-import context was rewritten")
    original = document.get("original_correctness")
    require(original == {
        "case_count": ORIGINAL_CASES,
        "suite_count": ORIGINAL_SUITES,
        "private_waiver_count": PRIVATE_WAIVERS,
        "additional_signature_case_count": SIGNATURE_CASES,
        "additional_signature_cases_in_original_denominator": False,
    }, "the independent public-import oracle changed the original denominators")
    matrix = document.get("case_matrix")
    public_hash = expected_public()["case_matrix_sha256"]
    require(type(matrix) is list and len(matrix) == PUBLIC_ENTRYPOINT_CASES and
            digest(canonical(matrix).encode("ascii")) == public_hash and
            document.get("case_matrix_sha256") == public_hash,
            "the separate 32 observed public-import cases were substituted")
    boundaries = document.get("boundaries")
    require(type(boundaries) is dict,
            "the honest public-entrypoint source-only boundaries were omitted")
    for key, expected in {
        "source_freeze_status": "PASS",
        "observed_public_entrypoint_status": "FAIL",
        "observed_public_entrypoint_classification": "UNQUALIFIED_ZIG_PROTOTYPE",
        "public_entrypoint_qualified": False,
        "qualified_candidate_count": 0,
        "winner_selected": False,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "actual_candidate_imports": 0,
        "actual_public_entrypoint_imports": 0,
        "actual_stdlib_regex_imports": 0,
        "actual_native_libraries_loaded": 0,
        "actual_archives_opened": 0,
        "actual_archives_decompressed": 0,
        "actual_subprocesses_started": 0,
        "actual_clock_samples": 0,
        "performance": "NOT MEASURED",
        "final_holdout_status": "NOT OPENED",
    }.items():
        require(boundaries.get(key) == expected,
                "a public-import source observation was silently rewritten: " + key)


def validate_families(document: object) -> None:
    require(type(document) is dict and
            document.get("schema") ==
            "rebar-phase2-six-candidate-independence-static-audit-v2" and
            document.get("version") == 2 and document.get("family_count") == 6,
            "the six first-party source families were substituted")
    families = document.get("families")
    require(type(families) is list and len(families) == 6 and
            [item.get("name") if type(item) is dict else None
             for item in families] ==
            ["c_vm", "rust", "zig", "cpp", "go", "fortran"],
            "source-family inventory must not be mistaken for qualified candidates")


def validate_rust(document: object) -> None:
    require(type(document) is dict and
            document.get("schema") ==
            "rebar-owned-repaired-rust-original-campaign-v7-recoverable-source-freeze"
            and document.get("version") == 7 and
            document.get("status") == expected_rust()["corrected_v7_source_status"],
            "the corrected Rust V7 source-only contract was substituted")
    require(document.get("source") == {
        "path": "tools/run_owned_repaired_rust_original_campaign_v7.py",
        "sha256": expected_rust()["corrected_v7_source_sha256"],
    }, "the exact corrected Rust V7 controller source was substituted")
    effects = document.get("source_only_effects")
    require(type(effects) is dict,
            "the actual corrected Rust V7 source-only effect ledger was omitted")
    for key, expected in {
        "actual_candidate_imports": 0,
        "actual_candidate_workers": 0,
        "actual_native_activations": 0,
        "actual_native_library_loads": 0,
        "actual_reference_workers": 0,
        "v13_source_build_archive_read_count": 0,
        "v13_source_build_archive_gzip_inflation_count": 0,
        "matching_archive_gzip_inflation_count": 0,
        "phase1_reference_archive_decompressed": False,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }.items():
        require(effects.get(key) == expected,
                "the corrected Rust V7 source-only effect changed: " + key)
    history = document.get("published_current_v43_overview")
    require(type(history) is dict,
            "the true failed Rust V6 controller history was omitted")
    for key, expected in {
        "actual_v6_controller_status": "FAIL",
        "actual_v6_source_build_archive_gzip_inflation_count": 1,
        "actual_v6_source_build_archive_read_count": 1,
        "actual_v6_controller_ledger_omits_archive_effect": True,
        "qualified_candidate_count": 0,
        "case_execution_denominator": ORIGINAL_CASES,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
    }.items():
        require(history.get(key) == expected,
                "the actual failed Rust V6 archive-effect history changed: " + key)
    additional = document.get("actual_supplementary_reference")
    require(type(additional) is dict and
            additional.get("reference_status") == "PASS" and
            additional.get("actual_reference_process_count") == 2 and
            additional.get("case_count") == SIGNATURE_CASES and
            additional.get("included_in_original_case_denominator") is False and
            additional.get("candidate_status") == "NOT RUN" and
            additional.get("candidate_cases_executed") == 0 and
            additional.get("reference_archive_decompressed") is False,
            "the corrected Rust source concealed the separate signature boundaries")


def validate_zig_v1(document: object) -> None:
    require(type(document) is dict and
            document.get("schema") ==
            "rebar-frozen-zig-original-p0-candidate-protocol-v1-source-freeze" and
            document.get("version") == 1 and document.get("family") == "zig" and
            document.get("phase") == "CANDIDATES" and
            document.get("status") == expected_zig_v1()["source_freeze_status"],
            "the actually pushed first-party Zig V1 source freeze was substituted")
    require(document.get("goal") == {
        "path": "GOAL.md", "sha256": GOAL_SHA256, "bytes": 3756,
    }, "the released first-party Zig source froze a different immutable objective")
    require(document.get("python") == {
        "isolated": True,
        "path": PYTHON,
        "sha256": "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
        "version": "3.14.6",
    }, "the released first-party Zig source froze a different CPython baseline")
    require(document.get("source") == {
        "protocol": {
            "path": "oracle/phase2/ZIG-ORIGINAL-P0-CANDIDATE-PROTOCOL-V1.md",
            "sha256": expected_zig_v1()["protocol_sha256"],
        },
        "runner": {
            "path": "tools/run_frozen_zig_original_p0_candidate_v1.py",
            "sha256": expected_zig_v1()["controller_source_sha256"],
        },
        "worker": {
            "path": "tools/run_frozen_zig_original_p0_candidate_worker_v1.py",
            "sha256": expected_zig_v1()["worker_source_sha256"],
        },
    }, "one of the actually pushed first-party Zig source owners was substituted")
    phase = document.get("phase_one")
    require(type(phase) is dict and
            phase.get("case_execution_denominator") == ORIGINAL_CASES and
            phase.get("suite_count") == ORIGINAL_SUITES and
            phase.get("named_private_waiver_count") == PRIVATE_WAIVERS and
            phase.get("supplemental_cases_added") is False,
            "the actual Zig source freeze rewrote the original P0 denominators")
    candidate = document.get("candidate_run_policy")
    require(type(candidate) is dict and
            candidate.get("candidate_matching_status") == "NOT RUN" and
            candidate.get("candidate_qualified") is False and
            candidate.get("runnable_candidate_families") == [] and
            candidate.get("runnable_candidate_family_count") == 0 and
            candidate.get("runner_builds_or_activates_native") is False and
            candidate.get("verified_live_zig_activation") ==
            "NOT FROZEN; FAIL CLOSED" and
            candidate.get("matching_pass_requires_all_31237_original_cases") is True
            and candidate.get("historical_build_does_not_activate_native") is True,
            "released Zig source-only readiness was reported as a runnable pass")
    first_party = document.get("first_party_zig_family")
    require(type(first_party) is dict and
            first_party.get("candidate_imported_by_source_freeze") is False and
            first_party.get("native_library_loaded_by_source_freeze") is False,
            "the first-party Zig source freeze imported or activated a candidate")
    family = first_party.get("family_spec")
    require(type(family) is dict and family.get("family") == "zig" and
            family.get("module") == "candidates.zig_candidate" and
            family.get("adapter_relative") == "candidates/zig_candidate.py" and
            family.get("owned_source_count") == 3,
            "the actual owned Zig matcher family was substituted")
    audit = first_party.get("source_audit")
    require(type(audit) is dict and audit.get("family") == "zig" and
            audit.get("cross_family_source_dependency_count") == 0 and
            audit.get("external_regex_source_dependency_count") == 0 and
            audit.get("stdlib_regex_engine_source_dependency_count") == 0 and
            audit.get("runtime_non_delegation") == "NOT ESTABLISHED",
            "the actually pushed Zig first-party source audit was weakened")
    require(document.get("from_scratch_policy") == {
        "another_candidate_engine": "FORBIDDEN",
        "external_regex_package": "FORBIDDEN",
        "matching_fallback": "FORBIDDEN",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "stdlib_matching_engine": "FORBIDDEN",
    }, "the actual Zig first-party no-delegation policy was weakened")
    effects = document.get("source_only_effects")
    require(type(effects) is dict,
            "the actual pushed first-party Zig source-only effect ledger is missing")
    for name, expected in {
        "actual_candidate_imports": 0,
        "actual_candidate_workers": 0,
        "actual_compiler_processes": 0,
        "actual_native_activations": 0,
        "actual_native_libraries_loaded": 0,
        "actual_native_promotions": 0,
        "actual_network_requests": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_threads_started": 0,
        "archives_inflated": 0,
        "archives_opened": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "compressed_archive_bytes_read": 0,
        "hidden_cases_read": 0,
        "holdout": "NOT OPENED",
        "memory": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "timing_trials_run": 0,
        "uncompressed_archive_bytes_read": 0,
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }.items():
        require(effects.get(name) == expected,
                "the actual Zig source-only effect was rewritten: " + name)
    require(document.get("candidate_correctness") == "NOT MEASURED" and
            document.get("qualified_candidate_count") == 0 and
            document.get("winner_selected") is False and
            document.get("holdout") == "NOT OPENED" and
            document.get("performance") == "NOT MEASURED" and
            document.get("memory") == "NOT MEASURED" and
            document.get("undefined_behavior") == "NOT MEASURED",
            "first-party Zig source freezing must not claim execution or a winner")


def validate_overview(document: object, *, inputs: bool) -> None:
    require(type(document) is dict,
            "the exact current candidate overview must be a JSON object")
    role = "inputs" if inputs else "summary"
    require(document.get("schema") ==
            "rebar-candidate-current-overview-v" + str(OVERVIEW_VERSION) + "-" + role
            and document.get("version") == OVERVIEW_VERSION,
            "the exact current pushed candidate overview changed: " + role)
    expected = {
        "full_case_denominator": ORIGINAL_CASES,
        "suite_count": ORIGINAL_SUITES,
        "private_waiver_count": PRIVATE_WAIVERS,
        "additional_signature_frozen_case_count": SIGNATURE_CASES,
        "additional_signature_reference_status": "PASS",
        "additional_signature_candidate_status": "NOT RUN",
        "qualified_candidate_count": 0,
        "winner_selected": False,
        "public_entrypoint_status": "UNQUALIFIED ZIG PROTOTYPE; NOT A WINNER",
        "public_entrypoint_module_version_status": "FAIL/MISSING",
        "public_entrypoint_qualified": False,
        "public_entrypoint_package_mode": False,
        "actual_rust_controller_status": "FAIL",
        "actual_rust_candidate_workers": 0,
        "actual_rust_controller_process_count": 1,
        "actual_rust_native_activations": 0,
        "actual_rust_source_build_archive_read_count": 1,
        "actual_rust_source_build_archive_gzip_inflation_count": 1,
        "actual_rust_controller_ledger_omits_source_build_archive_effect": True,
        "corrected_rust_v7_source_sha256":
            expected_rust()["corrected_v7_source_sha256"],
        "corrected_rust_v7_candidate_matching_status": "NOT RUN",
        "corrected_rust_v7_source_self_test_control_count": 517,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "authenticated_evidence_owner_lower_bound": 166,
        "authenticated_history_reference_lower_bound": 171,
        "first_party_source_inventory_family_count": 6,
        "frozen_corrected_runner_source_families": ["c", "rust", "zig"],
        "frozen_corrected_runner_source_family_count": 3,
        "actually_runnable_candidate_families": [],
        "actually_runnable_candidate_family_count": 0,
        "dedicated_corrected_runnable_families": [],
        "dedicated_corrected_runnable_family_count": 0,
        "zig_v1_runner_source_status":
            expected_zig_v1()["source_freeze_status"],
        "zig_v1_candidate_matching_status": "NOT RUN",
        "zig_v1_candidate_qualified": False,
        "zig_v1_actual_candidate_workers": 0,
        "zig_v1_actual_compiler_processes": 0,
        "zig_v1_actual_native_activations": 0,
        "zig_v1_actual_native_libraries_loaded": 0,
        "zig_v1_actual_reference_workers": 0,
        "zig_v1_worker_source_sha256":
            expected_zig_v1()["worker_source_sha256"],
        "zig_v1_controller_source_sha256":
            expected_zig_v1()["controller_source_sha256"],
        "zig_v1_protocol_sha256": expected_zig_v1()["protocol_sha256"],
        "zig_v1_contract_sha256": expected_zig_v1()["contract_sha256"],
        "zig_v1_cross_candidate_engine_dependency_count": 0,
        "zig_v1_external_regex_package_count": 0,
        "zig_v1_matching_fallback_count": 0,
        "zig_v1_runtime_no_delegation": "NOT ESTABLISHED",
        "zig_v1_stdlib_regex_engine_dependency_count": 0,
        "source_build_archive_gzip_inflation_count_by_graph": 0,
        "matching_archive_gzip_inflation_count": 0,
        "reference_archive_gzip_inflation_count": 0,
        "actual_candidate_imports_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "final_holdout_opened": False,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "public_entrypoint_case_matrix_count": PUBLIC_ENTRYPOINT_CASES,
        "public_entrypoint_case_matrix_sha256":
            expected_public()["case_matrix_sha256"],
        "public_entrypoint_source_only_control_count": 191,
        "public_entrypoint_physically_blocked_effect_attempt_count": 33,
        "public_entrypoint_pass_count": 17,
        "public_entrypoint_fail_count": 7,
        "public_entrypoint_not_measured_count": 6,
        "public_entrypoint_not_established_count": 1,
        "public_entrypoint_not_opened_count": 1,
        "public_entrypoint_cases_in_original_denominator": False,
        "public_entrypoint_cases_in_signature_denominator": False,
        "public_entrypoint_oracle_source_sha256":
            "c0a61c4cf520e82bf0c327a17c06daf64f57a1dcfd20b37c6e9f7b84177108b4",
        "public_entrypoint_oracle_protocol_sha256":
            "01ace52c6285142733bdcb2b4556feb43226e01c8b181b84019b8fa8c42697c0",
        "public_entrypoint_oracle_contract_sha256":
            "b80ba35a6af481f0dd1c5b9141e2995f7b0ffd12f8ffa7060bab50344ddbda47",
        "public_entrypoint_oracle_source_freeze_status": "PASS",
        "public_entrypoint_actual_observed_status": "FAIL",
    }
    for key, value in expected.items():
        require(document.get(key) == value,
                "the exact current " + role + " overview changed: " + key)


def admit_future_run(observation: object) -> dict[str, object]:
    """Check synthetic future admission; this function never starts a worker."""
    require(type(observation) is dict,
            "a future large-input admission must be a complete observation")
    expected_keys = {
        "role", "free_host_memory_bytes", "resource_limit_bytes",
        "worker_timeout_seconds", "worker_source_sha256", "pinned_python",
        "subject_size", "search_start", "search_end", "subn_count",
        "subn_result_equals_subject", "complete_stdout", "complete_stderr",
        "exact_exit_status", "candidate_uses_stdlib_re", "candidate_uses_sre",
        "candidate_uses_external_regex", "candidate_uses_other_candidate",
        "candidate_uses_fallback", "first_party_engine_proof_sha256",
    }
    require(set(observation) == expected_keys,
            "a future worker observation is incomplete or contains hidden fields")
    role = observation.get("role")
    require(role in ("reference", "candidate"),
            "a future worker must explicitly be an isolated reference or candidate")
    available = observation.get("free_host_memory_bytes")
    require(type(available) is int,
            "actual free host memory must be admitted as an integer")
    require(available > FULL_REFERENCE_ALLOWANCE,
            "NOT RUN; INSUFFICIENT RESOURCES: more than 40 GiB is mandatory")
    resource = observation.get("resource_limit_bytes")
    require(type(resource) is int and resource >= MIN_AVAILABLE_HOST_BYTES,
            "the isolated large-input worker resource budget is insufficient")
    timeout = observation.get("worker_timeout_seconds")
    require(type(timeout) is int and 0 < timeout <= 86_400,
            "a positive bounded isolated large-input timeout is mandatory")
    for name in ("worker_source_sha256", "first_party_engine_proof_sha256"):
        value = observation.get(name)
        require(type(value) is str and len(value) == 64 and
                all(char in "0123456789abcdef" for char in value),
                "a separately authenticated future worker proof is mandatory: " + name)
    for name, expected in {
        "pinned_python": PYTHON,
        "subject_size": LARGE_SUBJECT_SIZE,
        "search_start": LARGE_SUBJECT_SIZE,
        "search_end": LARGE_SUBJECT_SIZE,
        "subn_count": LARGE_SUBN_COUNT,
        "subn_result_equals_subject": True,
        "complete_stdout": True,
        "complete_stderr": True,
        "exact_exit_status": 0,
        "candidate_uses_stdlib_re": False,
        "candidate_uses_sre": False,
        "candidate_uses_external_regex": False,
        "candidate_uses_other_candidate": False,
        "candidate_uses_fallback": False,
    }.items():
        require(observation.get(name) == expected,
                "a future complete large-input observation failed: " + name)
    return {
        "status": "SYNTHETIC ADMISSION ONLY; NO WORKER STARTED",
        "role": role,
        "actual_reference_workers_started": 0,
        "actual_candidate_workers_started": 0,
        "actual_host_memory_queries": 0,
        "actual_large_subject_allocations": 0,
        "actual_candidate_evidence": False,
    }


def verify_context(contract: dict[str, object]) -> dict[str, object]:
    require(_AUDIT_INSTALLED, "the physical large-input source audit wall is missing")
    no_engine_imports()
    records: dict[str, bytes] = {}
    for name, path, expected, size in OWNERS:
        records[name] = read_exact(path, expected, size)
        no_engine_imports()
    validate_original_inventory(decode_json(records["original_p0_inventory"]))
    validate_manifest(decode_json(records["upstream_original_accounting"]))
    upstream = validate_upstream_large_ast(records["upstream_original_test"])
    validate_signatures(decode_json(records["additional_signature_inventory"]),
                        decode_json(records["actual_signature_reference_receipt"]))
    validate_public(decode_json(records["public_entrypoint_oracle_contract"]))
    validate_families(decode_json(records["first_party_source_inventory"]))
    validate_zig_v1(decode_json(records["released_zig_v1_contract"]))
    validate_rust(decode_json(records["repaired_rust_v7_contract"]))
    validate_overview(decode_json(records["current_overview_inputs"]), inputs=True)
    validate_overview(decode_json(records["current_overview_summary"]), inputs=False)
    no_engine_imports()
    return {
        "schema": SCHEMA + "-frozen-context",
        "status": "PASS",
        "source_freeze_status": "PASS",
        "overview_version": OVERVIEW_VERSION,
        "authenticated_exact_owner_count": len(OWNERS),
        "physical_audit_hook_installed": _AUDIT_INSTALLED,
        "physically_blocked_effect_attempts": sum(_BLOCKED_AUDIT_EVENTS.values()),
        "case_matrix_count": len(CASE_ROWS),
        "case_matrix_sha256": MATRIX_SHA256,
        "large_upstream": upstream,
        "historical_reference_status": "PASS; MANIFEST EVIDENCE ONLY",
        "historical_reference_process_count": 2,
        "historical_reference_large_search_subject_size": LARGE_SUBJECT_SIZE,
        "historical_reference_large_subn_subject_size": LARGE_SUBJECT_SIZE,
        "historical_reference_real_max_memory_bytes": FULL_REFERENCE_ALLOWANCE,
        "historical_reference_report_opened": False,
        "candidate_original_bigmem_dry_run": True,
        "candidate_original_maximum_subject_size": ORIGINAL_CANDIDATE_MAXIMUM,
        "candidate_large_search": "NOT RUN",
        "candidate_large_subn": "NOT RUN",
        "candidate_full_resource_qualification": "NOT ESTABLISHED",
        "original_case_count": ORIGINAL_CASES,
        "original_suite_count": ORIGINAL_SUITES,
        "original_private_waiver_count": PRIVATE_WAIVERS,
        "large_input_source_cases_in_original_denominator": False,
        "additional_signature_case_count": SIGNATURE_CASES,
        "additional_signature_cases_in_original_denominator": False,
        "additional_signature_reference_status": "PASS",
        "additional_signature_candidate_status": "NOT RUN",
        "public_entrypoint_case_count": PUBLIC_ENTRYPOINT_CASES,
        "public_entrypoint_cases_in_original_denominator": False,
        "public_entrypoint_cases_in_signature_denominator": False,
        "public_entrypoint_actual_observed_status": "FAIL",
        "public_entrypoint_qualified": False,
        "actual_rust_v6_controller_status": "FAIL",
        "actual_rust_v6_source_build_archive_read_count": 1,
        "actual_rust_v6_source_build_archive_inflation_count": 1,
        "corrected_rust_v7_candidate_matching": "NOT RUN",
        "corrected_rust_v7_source_self_test_control_count": 517,
        "released_zig_v1_source_status":
            "SOURCE FROZEN; FIRST-PARTY ZIG CANDIDATE NOT RUN",
        "released_zig_v1_candidate_matching": "NOT RUN",
        "released_zig_v1_candidate_qualified": False,
        "released_zig_v1_actual_candidate_workers": 0,
        "frozen_corrected_runner_source_families": ["c", "rust", "zig"],
        "frozen_corrected_runner_source_family_count": 3,
        "actually_runnable_candidate_families": [],
        "actually_runnable_candidate_family_count": 0,
        "qualified_candidate_count": 0,
        "winner_selected": False,
        "future_execution_implemented": False,
        "minimum_available_host_memory_bytes": MIN_AVAILABLE_HOST_BYTES,
        "actual_reference_workers_started": 0,
        "actual_candidate_workers_started": 0,
        "actual_candidate_imports": 0,
        "actual_entrypoint_imports": 0,
        "actual_stdlib_regex_imports": 0,
        "actual_native_libraries_loaded": 0,
        "actual_archives_opened": 0,
        "actual_archives_decompressed": 0,
        "actual_subprocesses_started": 0,
        "actual_network_requests": 0,
        "actual_clock_samples": 0,
        "actual_host_memory_queries": 0,
        "actual_large_subject_allocations": 0,
        "actual_holdout_cases_read": 0,
        "workspace_files_written": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
    }


def clone(value: object) -> object:
    return decode_json(canonical(value).encode("utf-8"))


def run_self_test(contract: dict[str, object]) -> dict[str, object]:
    context = verify_context(contract)
    passed: list[str] = []

    def accept(name: str, operation) -> None:
        try:
            result = operation()
        except Exception as error:
            raise FreezeError("positive large-input control failed: " + name) from error
        require(result is not False, "positive large-input control failed: " + name)
        passed.append(name)

    def reject(name: str, operation) -> None:
        try:
            operation()
        except (FreezeError, ValueError, TypeError, UnicodeError,
                OverflowError, SyntaxError, OSError):
            passed.append(name)
            no_engine_imports()
            return
        raise FreezeError("negative large-input control unexpectedly passed: " + name)

    accept("accept-exact-frozen-contract", lambda: bool(validate_contract(contract)))
    accept("accept-exact-authenticated-context", lambda: context["status"] == "PASS")
    accept("accept-independent-original-denominator", lambda:
           context["original_case_count"] == ORIGINAL_CASES)
    accept("accept-independent-signature-denominator", lambda:
           context["additional_signature_case_count"] == SIGNATURE_CASES)
    accept("accept-independent-public-denominator", lambda:
           context["public_entrypoint_case_count"] == PUBLIC_ENTRYPOINT_CASES)
    accept("accept-preserved-actual-public-failure", lambda:
           context["public_entrypoint_actual_observed_status"] == "FAIL")
    accept("accept-preserved-actual-rust-failure", lambda:
           context["actual_rust_v6_controller_status"] == "FAIL")
    accept("accept-preserved-rust-archive-effect", lambda:
           context["actual_rust_v6_source_build_archive_inflation_count"] == 1)
    accept("accept-historical-real-2g-reference", lambda:
           context["historical_reference_large_search_subject_size"] == LARGE_SUBJECT_SIZE)
    accept("accept-honest-candidate-2g-not-run", lambda:
           context["candidate_large_search"] == "NOT RUN" and
           context["candidate_large_subn"] == "NOT RUN")
    accept("accept-honest-candidate-resource-gap", lambda:
           context["candidate_full_resource_qualification"] == "NOT ESTABLISHED")
    accept("accept-physical-audit-wall", lambda: _AUDIT_INSTALLED)
    accept("accept-no-matcher-imports", lambda: no_engine_imports() is None)

    malformed: tuple[tuple[str, bytes], ...] = (
        ("empty", b""),
        ("duplicate-key", b'{"a":1,"a":2}'),
        ("trailing-document", b'{"a":1} {"b":2}'),
        ("leading-zero", b"01"),
        ("negative-leading-zero", b"-01"),
        ("missing-fraction", b"1."),
        ("missing-exponent", b"1e"),
        ("positive-sign", b"+1"),
        ("nonfinite-nan", b"NaN"),
        ("nonfinite-infinity", b"Infinity"),
        ("unicode-high-surrogate", b'"\\ud800"'),
        ("unicode-low-surrogate", b'"\\udc00"'),
        ("unicode-invalid-pair", b'"\\ud800\\u0041"'),
        ("unicode-invalid-digit", b'"\\u00q0"'),
        ("raw-string-control", b'"a\x00b"'),
        ("unterminated-string", b'"open'),
        ("trailing-array-comma", b"[1,]"),
        ("trailing-object-comma", b'{"x":1,}'),
        ("missing-colon", b'{"x" 1}'),
        ("missing-array-separator", b"[1 2]"),
        ("invalid-utf8", b"\xff"),
        ("excessive-depth", b"[" * 50 + b"0" + b"]" * 50),
        ("excessive-number", b"1" * 129),
    )
    for name, raw in malformed:
        reject("reject-strict-json-" + name,
               lambda payload=raw: decode_json(payload))
    accept("accept-paired-json-surrogate", lambda:
           decode_json(b'"\\ud83d\\ude00"') == "\U0001f600")
    accept("accept-bounded-json-number", lambda:
           decode_json(b"2147483649") == LARGE_SUBN_COUNT)
    accept("accept-strict-json-round-trip", lambda:
           decode_json(canonical(case_matrix()).encode("ascii")) == case_matrix())

    for key in sorted(contract):
        def without(name=key):
            modified = clone(contract)
            require(type(modified) is dict, "a contract clone was not an object")
            del modified[name]
            return validate_contract(modified)
        reject("reject-omitted-contract-" + key, without)
    reject("reject-unexpected-contract-section", lambda:
           validate_contract({**contract, "hidden_execution": True}))
    for section in (
        "pinned_runtime", "original_correctness", "upstream_large_input",
        "historical_full_resource_reference", "actual_candidate_large_input",
        "public_entrypoint_preservation", "corrected_rust_preservation",
        "released_zig_v1_preservation",
        "future_execution_policy", "boundaries",
    ):
        current = contract[section]
        require(type(current) is dict,
                "a frozen contract control section was not an object: " + section)
        for key in sorted(current):
            def without_field(group=section, field=key):
                modified = clone(contract)
                require(type(modified) is dict, "a contract clone was not an object")
                nested = modified[group]
                require(type(nested) is dict, "a nested contract was not an object")
                del nested[field]
                return validate_contract(modified)
            reject("reject-omitted-" + section + "-" + key, without_field)

    for name, _path, _sha256, _size in OWNERS:
        def poison(owner=name):
            modified = clone(contract)
            require(type(modified) is dict, "a contract clone was not an object")
            owners = modified["owners"]
            require(type(owners) is dict and type(owners[owner]) is dict,
                    "an exact owner control was not an object")
            owners[owner]["sha256"] = "0" * 64
            return validate_contract(modified)
        reject("reject-substituted-owner-" + name, poison)
    reject("reject-inflated-source-matrix", lambda:
           validate_contract({**contract, "case_matrix":
                              list(case_matrix()) + [case_matrix()[0]]}))
    reject("reject-shortened-source-matrix", lambda:
           validate_contract({**contract, "case_matrix": case_matrix()[:-1]}))
    reject("reject-forged-source-matrix-sha256", lambda:
           validate_contract({**contract, "case_matrix_sha256": "0" * 64}))
    reject("reject-stale-overview", lambda:
           validate_contract({**contract,
                              "current_overview_version": OVERVIEW_VERSION - 1}))

    source = owner_mapping()["upstream_original_test"]
    upstream_raw = read_exact(str(source["path"]), str(source["sha256"]),
                              int(source["bytes"]))
    accept("accept-authentic-upstream-large-ast", lambda:
           validate_upstream_large_ast(upstream_raw)["case_count"] == 2)
    source_attacks = (
        ("large-search-anchor", b"m = re.search('$', s)",
         b"m = re.search('x', s)"),
        ("large-search-start", b"self.assertEqual(m.start(), size)",
         b"self.assertEqual(m.start(), size - 1)"),
        ("large-search-end", b"self.assertEqual(m.end(), size)",
         b"self.assertEqual(m.end(), size - 1)"),
        ("large-search-non-null", b"self.assertIsNotNone(m)",
         b"self.assertIsNone(m)"),
        ("large-search-memuse", b"@bigmemtest(size=_2G, memuse=1)",
         b"@bigmemtest(size=_2G, memuse=2)"),
        ("large-subn-memuse", b"@bigmemtest(size=_2G, memuse=16 + 2)",
         b"@bigmemtest(size=_2G, memuse=16 + 1)"),
        ("large-subn-pattern", b"r, n = re.subn('', '', s)",
         b"r, n = re.subn('x', '', s)"),
        ("large-subn-replacement", b"r, n = re.subn('', '', s)",
         b"r, n = re.subn('', 'x', s)"),
        ("large-subn-result", b"self.assertEqual(r, s)",
         b"self.assertEqual(r, n)"),
        ("large-subn-count", b"self.assertEqual(n, size + 1)",
         b"self.assertEqual(n, size)"),
        ("large-subn-name", b"def test_large_subn(self, size):",
         b"def test_large_substitution(self, size):"),
        ("large-search-name", b"def test_large_search(self, size):",
         b"def test_large_lookup(self, size):"),
    )
    for name, old, replacement in source_attacks:
        require(upstream_raw.count(old) >= 1,
                "an authentic upstream AST self-control is missing: " + name)
        reject("reject-upstream-" + name,
               lambda before=old, after=replacement:
               validate_upstream_large_ast(upstream_raw.replace(before, after, 1)))

    future: dict[str, object] = {
        "role": "candidate",
        "free_host_memory_bytes": MIN_AVAILABLE_HOST_BYTES,
        "resource_limit_bytes": MIN_AVAILABLE_HOST_BYTES,
        "worker_timeout_seconds": 3_600,
        "worker_source_sha256": "1" * 64,
        "pinned_python": PYTHON,
        "subject_size": LARGE_SUBJECT_SIZE,
        "search_start": LARGE_SUBJECT_SIZE,
        "search_end": LARGE_SUBJECT_SIZE,
        "subn_count": LARGE_SUBN_COUNT,
        "subn_result_equals_subject": True,
        "complete_stdout": True,
        "complete_stderr": True,
        "exact_exit_status": 0,
        "candidate_uses_stdlib_re": False,
        "candidate_uses_sre": False,
        "candidate_uses_external_regex": False,
        "candidate_uses_other_candidate": False,
        "candidate_uses_fallback": False,
        "first_party_engine_proof_sha256": "2" * 64,
    }
    accept("accept-synthetic-future-candidate-admission-without-execution", lambda:
           admit_future_run(future)["actual_candidate_evidence"] is False)
    accept("accept-synthetic-future-reference-admission-without-execution", lambda:
           admit_future_run({**future, "role": "reference"})["role"] == "reference")
    invalid_admissions: tuple[tuple[str, str, object], ...] = (
        ("exactly-40g-not-enough", "free_host_memory_bytes", FULL_REFERENCE_ALLOWANCE),
        ("below-40g-not-enough", "free_host_memory_bytes", ORIGINAL_CANDIDATE_MAXIMUM),
        ("missing-resource-limit", "resource_limit_bytes", FULL_REFERENCE_ALLOWANCE),
        ("zero-timeout", "worker_timeout_seconds", 0),
        ("unbounded-timeout", "worker_timeout_seconds", 86_401),
        ("wrong-python", "pinned_python", "/usr/bin/python3"),
        ("wrong-subject-size", "subject_size", ORIGINAL_CANDIDATE_MAXIMUM),
        ("truncated-search-start", "search_start", 0),
        ("truncated-search-end", "search_end", 0),
        ("truncated-subn-count", "subn_count", LARGE_SUBJECT_SIZE),
        ("wrong-subn-result", "subn_result_equals_subject", False),
        ("incomplete-stdout", "complete_stdout", False),
        ("incomplete-stderr", "complete_stderr", False),
        ("nonzero-exit", "exact_exit_status", 1),
        ("stdlib-delegation", "candidate_uses_stdlib_re", True),
        ("sre-delegation", "candidate_uses_sre", True),
        ("external-engine-delegation", "candidate_uses_external_regex", True),
        ("cross-candidate-delegation", "candidate_uses_other_candidate", True),
        ("candidate-fallback", "candidate_uses_fallback", True),
        ("missing-worker-proof", "worker_source_sha256", "0"),
        ("missing-engine-proof", "first_party_engine_proof_sha256", "0"),
        ("wrong-worker-role", "role", "winner"),
    )
    for name, key, invalid in invalid_admissions:
        reject("reject-synthetic-future-" + name,
               lambda field=key, value=invalid:
               admit_future_run({**future, field: value}))
    for key in sorted(future):
        def omit_admission(field=key):
            modified = dict(future)
            del modified[field]
            return admit_future_run(modified)
        reject("reject-incomplete-future-" + key, omit_admission)
    reject("reject-hidden-future-worker-field", lambda:
           admit_future_run({**future, "hidden_worker": True}))

    actual_blocks = (
        ("stdlib-re-import", lambda: builtins.__import__("re")),
        ("candidate-import", lambda: builtins.__import__("candidates.zig_candidate")),
        ("entrypoint-import", lambda: builtins.__import__("rebar")),
        ("foreign-system-read", lambda: builtins.open("/etc/hosts", "rb")),
        ("reference-report-read", lambda: builtins.open(
            ROOT + "/oracle/cpython-3.14.6/evidence/postfinal-locale-v5-self-oracle.json", "rb")),
        ("signature-archive-read", lambda: builtins.open(
            ROOT + "/oracle/phase1/evidence/callable-introspection-reference-v2-cpython-3.14.6.json.gz", "rb")),
        ("holdout-read", lambda: builtins.open(
            ROOT + "/oracle/phase3/evidence/final-holdout.json.gz", "rb")),
        ("workspace-write", lambda: builtins.open(ROOT + "/large-input-forbidden", "wb")),
        ("owner-write", lambda: builtins.open(ROOT + "/" + CONTRACT, "wb")),
        ("native-dlopen", lambda: sys.audit("ctypes.dlopen", "/tmp/native.so")),
        ("native-dlsym", lambda: sys.audit("ctypes.dlsym", 0, "engine")),
        ("subprocess", lambda: sys.audit("subprocess.Popen", "sh", [], None, None)),
        ("network", lambda: sys.audit("socket.connect", None, ("127.0.0.1", 80))),
        ("multiprocessing", lambda: sys.audit("multiprocessing.Process.start", None)),
        ("thread", lambda: sys.audit("threading.start", None)),
        ("clock", lambda: sys.audit("time.time")),
        ("foreign-compile", lambda: sys.audit("compile", b"import re", "attack.py")),
        ("code-execution", lambda: sys.audit("exec", None)),
        ("shell", lambda: sys.audit("os.system", b"true")),
        ("fork", lambda: sys.audit("os.fork")),
        ("spawn", lambda: sys.audit("os.posix_spawn", "/bin/sh", [], {})),
        ("file-removal", lambda: sys.audit("os.remove", ROOT + "/GOAL.md", -1)),
        ("file-replacement", lambda: sys.audit("os.rename", "x", "y", -1, -1)),
        ("directory-creation", lambda: sys.audit("os.mkdir", ROOT + "/blocked", 448, -1)),
        ("symlink", lambda: sys.audit("os.symlink", "x", "y", -1)),
        ("file-mode", lambda: sys.audit("os.chmod", ROOT + "/GOAL.md", 420, -1)),
        ("environment-change", lambda: sys.audit("os.putenv", b"X", b"1")),
        ("marshal-execution", lambda: sys.audit("marshal.loads", b"x")),
    )
    for name, operation in actual_blocks:
        before = sum(_BLOCKED_AUDIT_EVENTS.values())
        reject("physically-block-" + name, operation)
        require(sum(_BLOCKED_AUDIT_EVENTS.values()) == before + 1,
                "a forbidden operation was not physically blocked: " + name)
    no_engine_imports()
    require(len(passed) == len(set(passed)),
            "large-input source self-test controls were counted more than once")
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS",
        "control_count": len(passed),
        "unique_control_count": len(set(passed)),
        "control_names_sha256": digest(canonical(passed).encode("ascii")),
        "physical_audit_hook_installed": _AUDIT_INSTALLED,
        "physically_blocked_effect_attempts": sum(_BLOCKED_AUDIT_EVENTS.values()),
        "physically_blocked_effect_event_counts": dict(_BLOCKED_AUDIT_EVENTS),
        "overview_version": OVERVIEW_VERSION,
        "authenticated_exact_owner_count": len(OWNERS),
        "case_matrix_count": len(CASE_ROWS),
        "case_matrix_sha256": MATRIX_SHA256,
        "historical_reference_status": "PASS; MANIFEST EVIDENCE ONLY",
        "candidate_large_search": "NOT RUN",
        "candidate_large_subn": "NOT RUN",
        "candidate_full_resource_qualification": "NOT ESTABLISHED",
        "original_case_count": ORIGINAL_CASES,
        "original_suite_count": ORIGINAL_SUITES,
        "original_private_waiver_count": PRIVATE_WAIVERS,
        "large_input_source_cases_in_original_denominator": False,
        "additional_signature_case_count": SIGNATURE_CASES,
        "additional_signature_cases_in_original_denominator": False,
        "public_entrypoint_case_count": PUBLIC_ENTRYPOINT_CASES,
        "public_entrypoint_cases_in_original_denominator": False,
        "public_entrypoint_cases_in_signature_denominator": False,
        "public_entrypoint_actual_observed_status": "FAIL",
        "released_zig_v1_source_status":
            "SOURCE FROZEN; FIRST-PARTY ZIG CANDIDATE NOT RUN",
        "released_zig_v1_candidate_matching": "NOT RUN",
        "released_zig_v1_candidate_qualified": False,
        "released_zig_v1_actual_candidate_workers": 0,
        "frozen_corrected_runner_source_families": ["c", "rust", "zig"],
        "frozen_corrected_runner_source_family_count": 3,
        "actually_runnable_candidate_families": [],
        "actually_runnable_candidate_family_count": 0,
        "future_execution_implemented": False,
        "future_admission_controls": "SYNTHETIC ONLY; NO WORKER STARTED",
        "minimum_available_host_memory_bytes": MIN_AVAILABLE_HOST_BYTES,
        "qualified_candidate_count": 0,
        "winner_selected": False,
        "actual_reference_workers_started": 0,
        "actual_candidate_workers_started": 0,
        "actual_candidate_imports": 0,
        "actual_entrypoint_imports": 0,
        "actual_stdlib_regex_imports": 0,
        "actual_native_libraries_loaded": 0,
        "actual_archives_opened": 0,
        "actual_archives_decompressed": 0,
        "actual_subprocesses_started": 0,
        "actual_network_requests": 0,
        "actual_clock_samples": 0,
        "actual_host_memory_queries": 0,
        "actual_large_subject_allocations": 0,
        "actual_holdout_cases_read": 0,
        "workspace_files_written": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
    }


def parse_arguments(argv: list[str]) -> tuple[str, dict[str, str]]:
    names = {"--source-sha256": "source", "--protocol-sha256": "protocol",
             "--contract-sha256": "contract"}
    pins: dict[str, str] = {}
    mode = ""
    index = 0
    while index < len(argv):
        item = argv[index]
        if item in ("--self-test", "--verify-frozen-context"):
            require(not mode, "exactly one large-input source-only mode is mandatory")
            mode = item
            index += 1
            continue
        require(item in names and index + 1 < len(argv),
                "unknown large-input argument or missing independent source pin")
        name = names[item]
        require(name not in pins, "duplicate independent large-input pin: " + name)
        value = argv[index + 1]
        require(len(value) == 64 and
                all(char in "0123456789abcdef" for char in value),
                "an independently pinned SHA-256 must be lowercase hexadecimal")
        pins[name] = value
        index += 2
    require(bool(mode) and set(pins) == {"source", "protocol", "contract"},
            "one source-only mode and all three independently pinned owners are required")
    return mode, pins


def main(argv: list[str]) -> int:
    no_engine_imports()
    require(tuple(sys.version_info[:3]) == (3, 14, 6) and sys.executable == PYTHON,
            "use only the exact pinned stable CPython 3.14.6 interpreter")
    require(sys.flags.isolated == 1 and sys.dont_write_bytecode,
            "run the source-only oracle with the exact -I -B isolation flags")
    install_audit_wall()
    mode, pins = parse_arguments(argv)
    read_self(SOURCE, pins["source"])
    read_self(PROTOCOL, pins["protocol"])
    raw = read_self(CONTRACT, pins["contract"])
    contract = validate_contract(decode_json(raw))
    result = (run_self_test(contract) if mode == "--self-test"
              else verify_context(contract))
    no_engine_imports()
    sys.stdout.write(canonical(result) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except FreezeError as error:
        sys.stderr.write("large-input source freeze failed closed: " + str(error) + "\n")
        raise SystemExit(1)
