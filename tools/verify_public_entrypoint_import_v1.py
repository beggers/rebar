#!/usr/bin/env python3
"""Freeze the real public import without importing a regular-expression engine."""

from __future__ import annotations

import sys


_BOOT_MODULES = frozenset(sys.modules)
if "re" in _BOOT_MODULES or "_sre" in _BOOT_MODULES:
    raise SystemExit("public-entrypoint source freeze requires no re or _sre import")

import ast
import builtins
import hashlib
import os
import stat


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SCHEMA = "rebar-python-re-public-entrypoint-import-v1"
SOURCE = "tools/verify_public_entrypoint_import_v1.py"
PROTOCOL = "oracle/phase1/P0-PUBLIC-ENTRYPOINT-IMPORT-V1.md"
CONTRACT = "oracle/phase1/p0-public-entrypoint-import-v1.json"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
MATRIX_SHA256 = "f67f8d4d62f9939c94250ad2e4df55b14df013df7212aa66930ecc3a772d2a58"
OVERVIEW_VERSION = 44
ORIGINAL_CASES = 31_237
ORIGINAL_SUITES = 13
PRIVATE_WAIVERS = 13
ADDITIONAL_SIGNATURE_CASES = 50
PLANNED_HOLDOUT_CASES = 4_194_304
MAX_JSON_BYTES = 4 * 1024 * 1024
MAX_JSON_DEPTH = 48
MAX_OWNER_BYTES = 40 * 1024 * 1024

# Exact immutable observations, not a request to load any candidate or archive.
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
    ("current_overview_renderer", "tools/render_candidate_current_overview_v44.py", "10b64e05336485445b5199acdf4626854812c16df6c8248371860a764450324d", 85131),
    ("current_overview_inputs", "docs/evidence/candidate-current-overview-v44.inputs.json", "7b51e6fa89d7b1d3ccc043e0268f405fe072999d22bd6067aaf2f20ab43e0d94", 334269),
    ("current_overview_summary", "docs/evidence/candidate-current-overview-v44.json", "5fa65d50eb041b0e12384846c5a7de548581cbc5f9183b1f72bc5f3d703a41c9", 973979),
    ("current_overview_svg", "docs/evidence/candidate-current-overview-v44.svg", "b23c43fab061df0cf192b9c5c869aee8854ad794397dc3c9512aa6f946150ab8", 14375),
    ("repaired_rust_v7_source", "tools/run_owned_repaired_rust_original_campaign_v7.py", "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104", 505616),
    ("repaired_rust_v7_protocol", "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V7.md", "0b5182a7eee74e586839abc3a0e8bdd122bac248e9cb3b76c603c5add9281840", 8433),
    ("repaired_rust_v7_contract", "oracle/phase2/repaired-rust-original-campaign-v7.json", "9c8e85dcc5dcf0a00953b36dd02c29c2ab7b1ed0b4281eb27f6693c058d155e5", 46385),
    ("pinned_python_executable", PYTHON, "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016", 32387816),
    ("pinned_stdlib_re_source", "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/__init__.py", "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35", 17876),
)

CASE_ROWS = (
    ("entrypoint.source.exact-bytes", "PASS"),
    ("entrypoint.source.ast-only-observation", "PASS"),
    ("entrypoint.source.no-import-during-freeze", "PASS"),
    ("entrypoint.surface.ordered-wildcard-exports", "PASS"),
    ("entrypoint.surface.pattern-error-alias", "PASS"),
    ("entrypoint.surface.direct-debug-attribute", "PASS"),
    ("entrypoint.surface.direct-scanner-attribute", "PASS"),
    ("entrypoint.surface.module-version", "FAIL"),
    ("entrypoint.selection.qualified-winner", "FAIL"),
    ("entrypoint.selection.historical-zig-qualification", "FAIL"),
    ("entrypoint.selection.no-premature-family", "FAIL"),
    ("entrypoint.native.no-eager-bridge-import", "FAIL"),
    ("entrypoint.native.no-eager-engine-load", "FAIL"),
    ("entrypoint.native.actual-freeze-load-count", "PASS"),
    ("entrypoint.packaging.uv-package-enabled", "FAIL"),
    ("entrypoint.packaging.installed-artifact", "NOT MEASURED"),
    ("entrypoint.provenance.owned-zig-source", "PASS"),
    ("entrypoint.provenance.runtime-no-delegation", "NOT ESTABLISHED"),
    ("entrypoint.p0.original-case-denominator", "PASS"),
    ("entrypoint.p0.original-suite-denominator", "PASS"),
    ("entrypoint.p0.named-private-waivers", "PASS"),
    ("entrypoint.p0.separate-signature-denominator", "PASS"),
    ("entrypoint.p0.two-reference-signature-baseline", "PASS"),
    ("entrypoint.p0.candidate-signature-observations", "NOT MEASURED"),
    ("entrypoint.p0.public-entrypoint-matching", "NOT MEASURED"),
    ("entrypoint.safety.native-undefined-behavior", "NOT MEASURED"),
    ("entrypoint.safety.native-memory", "NOT MEASURED"),
    ("entrypoint.performance.end-to-end", "NOT MEASURED"),
    ("entrypoint.performance.final-holdout", "NOT OPENED"),
    ("entrypoint.history.actual-rust-failure-preserved", "PASS"),
    ("entrypoint.history.actual-zig-failure-preserved", "PASS"),
    ("entrypoint.history.zero-qualified-families", "PASS"),
)


class FreezeError(Exception):
    """The pinned public-entrypoint observation failed closed."""


_AUDIT_INSTALLED = False
_BLOCKED_AUDIT_EVENTS: dict[str, int] = {}


def require(condition: object, message: str) -> None:
    if not condition:
        raise FreezeError(message)


def no_matcher_imports() -> None:
    require("re" not in sys.modules and "_sre" not in sys.modules,
            "the source-only oracle imported Python's regular-expression engine: " +
            "re=" + str("re" in sys.modules) + ", _sre=" +
            str("_sre" in sys.modules))
    require(not any(name == "candidates" or name.startswith("candidates.")
                    or name == "rebar" or name.startswith("rebar.")
                    for name in sys.modules),
            "the source-only oracle imported a public entrypoint or candidate")


def allowed_source_paths() -> frozenset[str]:
    paths = {ROOT + "/" + SOURCE, ROOT + "/" + PROTOCOL,
             ROOT + "/" + CONTRACT}
    for _name, path, _expected, _size in OWNERS:
        paths.add(path if path.startswith("/") else ROOT + "/" + path)
    return frozenset(paths)


def blocked_effect(event: str, message: str) -> None:
    _BLOCKED_AUDIT_EVENTS[event] = _BLOCKED_AUDIT_EVENTS.get(event, 0) + 1
    raise FreezeError("source-only audit wall blocked " + event + ": " + message)


def source_only_audit_hook(event: str, arguments: tuple[object, ...]) -> None:
    if event == "open":
        path = arguments[0] if arguments else None
        flags = arguments[2] if len(arguments) > 2 else None
        if type(path) is not str or path not in allowed_source_paths():
            blocked_effect(event, "path is outside the exact frozen owner allowlist")
        if type(flags) is not int:
            blocked_effect(event, "an exact read-only file descriptor is mandatory")
        forbidden = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC |
                     os.O_APPEND | getattr(os, "O_TMPFILE", 0))
        if flags & forbidden:
            blocked_effect(event, "file creation, modification, or truncation is forbidden")
        return
    if event == "compile":
        source = arguments[0] if arguments else None
        filename = arguments[1] if len(arguments) > 1 else None
        approved = {"rebar.py", "candidates/zig_candidate.py",
                    "pinned-stdlib/re/__init__.py", "<unknown>"}
        if filename not in approved or type(source) not in (str, bytes):
            blocked_effect(event, "only exact frozen-source AST compilation is allowed")
        if len(source) > MAX_JSON_BYTES:
            blocked_effect(event, "an AST source exceeded its frozen byte limit")
        return
    if event == "import":
        name = arguments[0] if arguments else "<unknown>"
        blocked_effect(event, "no module imports are permitted after clean bootstrap: " +
                       str(name))
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
        blocked_effect(event, "execution, native, process, network, or mutation is forbidden")


def install_source_only_audit_wall() -> None:
    global _AUDIT_INSTALLED
    require(not _AUDIT_INSTALLED,
            "the source-only physical audit wall cannot be installed twice")
    no_matcher_imports()
    sys.addaudithook(source_only_audit_hook)
    _AUDIT_INSTALLED = True
    no_matcher_imports()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def quoted(value: str) -> str:
    require(type(value) is str, "JSON object names and strings must be real strings")
    output = ['"']
    escapes = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
               "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    for char in value:
        code = ord(char)
        if char in escapes:
            output.append(escapes[char])
        elif code < 0x20 or 0x7F <= code <= 0xFFFF:
            output.append("\\u" + format(code, "04x"))
        elif code > 0xFFFF:
            code -= 0x10000
            output.append("\\u" + format(0xD800 + (code >> 10), "04x"))
            output.append("\\u" + format(0xDC00 + (code & 0x3FF), "04x"))
        else:
            output.append(char)
    output.append('"')
    return "".join(output)


def canonical_text(value: object, depth: int = 0) -> str:
    require(depth <= MAX_JSON_DEPTH, "canonical JSON exceeds the frozen depth")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is str:
        return quoted(value)
    if type(value) is int:
        return str(value)
    if type(value) is float:
        require(value == value and abs(value) != float("inf"),
                "non-finite JSON numbers are forbidden")
        return repr(value)
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical_text(item, depth + 1)
                                for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value),
                "non-string JSON object names are forbidden")
        return "{" + ",".join(quoted(key) + ":" +
                               canonical_text(value[key], depth + 1)
                               for key in sorted(value)) + "}"
    raise FreezeError("unsupported canonical JSON value: " + type(value).__name__)


class StrictJSON:
    """A bounded, duplicate-key-strict decoder that never imports json or re."""

    def __init__(self, raw: bytes):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_JSON_BYTES,
                "JSON input is missing or exceeds the frozen byte allowance")
        try:
            self.text = raw.decode("utf-8", "strict")
        except UnicodeError as error:
            raise FreezeError("JSON must be strict UTF-8") from error
        self.index = 0

    def whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def string(self) -> str:
        require(self.index < len(self.text) and self.text[self.index] == '"',
                "a quoted JSON string is required")
        self.index += 1
        result = []
        ordinary = {'"': '"', "\\": "\\", "/": "/", "b": "\b",
                    "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
        while self.index < len(self.text):
            character = self.text[self.index]
            self.index += 1
            if character == '"':
                return "".join(result)
            if character == "\\":
                require(self.index < len(self.text), "incomplete JSON string escape")
                escaped = self.text[self.index]
                self.index += 1
                if escaped == "u":
                    digits = self.text[self.index:self.index + 4]
                    require(len(digits) == 4 and
                            all(x in "0123456789abcdefABCDEF" for x in digits),
                            "invalid four-digit JSON Unicode escape")
                    self.index += 4
                    code = int(digits, 16)
                    if 0xD800 <= code <= 0xDBFF:
                        require(self.text[self.index:self.index + 2] == "\\u",
                                "unpaired high JSON Unicode surrogate")
                        lower = self.text[self.index + 2:self.index + 6]
                        require(len(lower) == 4 and
                                all(x in "0123456789abcdefABCDEF" for x in lower),
                                "invalid low JSON Unicode surrogate")
                        low_code = int(lower, 16)
                        require(0xDC00 <= low_code <= 0xDFFF,
                                "unpaired high JSON Unicode surrogate")
                        self.index += 6
                        result.append(chr(0x10000 + ((code - 0xD800) << 10)
                                          + low_code - 0xDC00))
                    else:
                        require(not 0xDC00 <= code <= 0xDFFF,
                                "unpaired low JSON Unicode surrogate")
                        result.append(chr(code))
                else:
                    require(escaped in ordinary, "invalid JSON string escape")
                    result.append(ordinary[escaped])
            else:
                require(ord(character) >= 0x20,
                        "unescaped JSON string control character")
                result.append(character)
        raise FreezeError("unterminated JSON string")

    def number(self) -> int | float:
        start = self.index
        if self.text[self.index:self.index + 1] == "-":
            self.index += 1
        require(self.index < len(self.text), "incomplete JSON number")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index == len(self.text) or
                    self.text[self.index] not in "0123456789",
                    "JSON numbers cannot have leading zeroes")
        else:
            require(self.text[self.index] in "123456789", "invalid JSON number")
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
        fraction = False
        if self.text[self.index:self.index + 1] == ".":
            fraction = True
            self.index += 1
            begin = self.index
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
            require(self.index > begin, "incomplete JSON fractional number")
        if self.text[self.index:self.index + 1] in ("e", "E"):
            fraction = True
            self.index += 1
            if self.text[self.index:self.index + 1] in ("+", "-"):
                self.index += 1
            begin = self.index
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
            require(self.index > begin, "incomplete JSON exponent")
        token = self.text[start:self.index]
        require(len(token) <= 128, "JSON number exceeds the frozen digit bound")
        if not fraction:
            return int(token)
        result = float(token)
        require(result == result and abs(result) != float("inf"),
                "non-finite JSON number")
        return result

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "JSON exceeds the frozen nesting depth")
        self.whitespace()
        require(self.index < len(self.text), "missing JSON value")
        character = self.text[self.index]
        if character == '"':
            return self.string()
        if character == "{":
            self.index += 1
            result = {}
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
                        "missing JSON object colon")
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
            result = []
            self.whitespace()
            if self.text[self.index:self.index + 1] == "]":
                self.index += 1
                return result
            while True:
                result.append(self.value(depth + 1))
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "]":
                    return result
                require(separator == ",", "invalid JSON array separator")
        if character == "-" or character in "0123456789":
            return self.number()
        for word, result in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(word, self.index):
                self.index += len(word)
                return result
        raise FreezeError("invalid JSON literal")

    def decode(self) -> object:
        result = self.value()
        self.whitespace()
        require(self.index == len(self.text), "trailing or multiple JSON documents")
        return result


def decode_json(raw: bytes) -> object:
    return StrictJSON(raw).decode()


def parse_simple_project(raw: bytes) -> dict[str, dict[str, object]]:
    """Parse only the exact, small TOML subset used by the pinned project."""
    require(type(raw) is bytes and 0 < len(raw) <= 16_384,
            "project configuration exceeds its bounded source allowance")
    try:
        text = raw.decode("utf-8", "strict")
    except UnicodeError as error:
        raise FreezeError("project configuration must be strict UTF-8") from error
    sections: dict[str, dict[str, object]] = {}
    active: dict[str, object] | None = None
    for number, original in enumerate(text.splitlines(), 1):
        line = original.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("["):
            require(line.endswith("]") and not line.startswith("[["),
                    "invalid project section at line " + str(number))
            name = line[1:-1].strip()
            require(bool(name) and all(piece and
                    all(character.isascii() and
                        (character.isalnum() or character in "_-")
                        for character in piece)
                    for piece in name.split(".")),
                    "invalid project section at line " + str(number))
            require(name not in sections,
                    "duplicate project section at line " + str(number))
            active = {}
            sections[name] = active
            continue
        require(active is not None and "=" in line,
                "project assignment outside a section at line " + str(number))
        key, value = (piece.strip() for piece in line.split("=", 1))
        require(bool(key) and all(character.isascii() and
                (character.isalnum() or character in "_-") for character in key),
                "invalid project key at line " + str(number))
        require(key not in active,
                "duplicate project key at line " + str(number))
        if value == "true":
            parsed = True
        elif value == "false":
            parsed = False
        elif value == "[]":
            parsed = []
        else:
            try:
                parsed = ast.literal_eval(value)
            except (ValueError, SyntaxError) as error:
                raise FreezeError("unsupported project value at line " +
                                  str(number)) from error
            require(type(parsed) is str,
                    "only exact string, boolean, or empty-array project values are allowed")
        active[key] = parsed
    require("project" in sections and "tool.uv" in sections,
            "the project and exact uv package-policy sections are mandatory")
    return sections


def owner_mapping() -> dict[str, dict[str, object]]:
    return {name: {"path": path, "sha256": expected, "bytes": size}
            for name, path, expected, size in OWNERS}


def read_exact(path: str, expected_hash: str, expected_size: int) -> bytes:
    require(type(path) is str and type(expected_size) is int and
            0 < expected_size <= MAX_OWNER_BYTES,
            "a source owner path or bounded size was substituted")
    absolute = path if path.startswith("/") else ROOT + "/" + path
    require(absolute == PYTHON or
            absolute == "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/__init__.py" or
            (absolute.startswith(ROOT + "/") and
             ".." not in absolute[len(ROOT) + 1:].split("/")),
            "a source owner escaped the exact frozen project")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(absolute, flags)
    except OSError as error:
        raise FreezeError("cannot read exact source owner: " + path) from error
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and before.st_size == expected_size,
                "the exact source owner size or regular-file type changed: " + path)
        pieces = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(1024 * 1024, expected_size + 1 - total))
            if not chunk:
                break
            pieces.append(chunk)
            total += len(chunk)
            require(total <= expected_size,
                    "a frozen source owner grew during authenticated reading: " + path)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    require(total == expected_size and
            (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns),
            "the exact source owner was replaced during authenticated reading: " + path)
    data = b"".join(pieces)
    require(digest(data) == expected_hash,
            "the exact source owner SHA-256 changed: " + path)
    return data


def read_self(relative: str, expected: str) -> bytes:
    absolute = ROOT + "/" + relative
    try:
        info = os.stat(absolute, follow_symlinks=False)
    except OSError as error:
        raise FreezeError("missing required source-freeze owner: " + relative) from error
    require(stat.S_ISREG(info.st_mode) and 0 < info.st_size <= MAX_JSON_BYTES,
            "a source-freeze owner is not a bounded regular file: " + relative)
    return read_exact(relative, expected, info.st_size)


def assignment(tree: ast.Module, name: str) -> object:
    values = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name
                   for target in node.targets):
                try:
                    values.append(ast.literal_eval(node.value))
                except (ValueError, SyntaxError) as error:
                    raise FreezeError("public assignment is not a safe literal: " + name) from error
    require(len(values) == 1,
            "exactly one safe public assignment is required: " + name)
    return values[0]


def parse_module(raw: bytes, label: str) -> ast.Module:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_JSON_BYTES,
            "module source exceeds the bounded AST allowance")
    try:
        source = raw.decode("utf-8", "strict")
        tree = ast.parse(source, filename=label, mode="exec")
    except (UnicodeError, SyntaxError) as error:
        raise FreezeError("module is not a valid exact Python source: " + label) from error
    require(type(tree) is ast.Module, "public source must be an AST module")
    return tree


def attribute_chain(node: ast.AST) -> tuple[str, ...]:
    if isinstance(node, ast.Name):
        return (node.id,)
    if isinstance(node, ast.Attribute):
        root = attribute_chain(node.value)
        return root + (node.attr,) if root else ()
    return ()


def walk_ast(node: ast.AST):
    """Traverse a bounded source AST without ast.walk importing collections."""
    pending = [node]
    while pending:
        current = pending.pop()
        yield current
        children = tuple(ast.iter_child_nodes(current))
        pending.extend(reversed(children))


def analyze_surface(shim_raw: bytes, zig_raw: bytes,
                    stdlib_raw: bytes) -> dict[str, object]:
    shim = parse_module(shim_raw, "rebar.py")
    zig = parse_module(zig_raw, "candidates/zig_candidate.py")
    standard = parse_module(stdlib_raw, "pinned-stdlib/re/__init__.py")
    standard_all = assignment(standard, "__all__")
    standard_version = assignment(standard, "__version__")
    zig_all = assignment(zig, "__all__")
    zig_version = assignment(zig, "__version__")
    require(type(standard_all) is list and
            all(type(item) is str for item in standard_all) and
            len(standard_all) == len(set(standard_all)),
            "the authentic standard-library wildcard surface is invalid")
    require(standard_version == "2.2.1" and zig_version == "2.2.1",
            "the authentic standard-library or source-candidate version changed")
    require(type(zig_all) is list and all(type(item) is str for item in zig_all),
            "the historical Zig wildcard surface is not a literal string list")

    body = shim.body
    require(len(body) == 4 and isinstance(body[0], ast.Expr) and
            isinstance(body[0].value, ast.Constant) and
            type(body[0].value.value) is str,
            "the frozen public entrypoint structure changed")
    imports = body[1:]
    require(all(isinstance(node, ast.ImportFrom) and
                node.module == "candidates.zig_candidate" and node.level == 0
                for node in imports),
            "the public entrypoint selected a different, hidden, or fallback engine")
    imported = tuple(tuple(item.name for item in node.names) for node in imports)
    require(imported == (("*",), ("DEBUG", "Scanner"), ("__all__",)),
            "the exact frozen public star-import and explicit imports changed")
    available = set(zig_all) | {"DEBUG", "Scanner", "__all__"}
    version_present = "__version__" in available

    bridge_import = any(isinstance(node, ast.ImportFrom) and
                        node.module == "candidates" and
                        any(alias.name == "_zig_bridge" for alias in node.names)
                        for node in zig.body)
    eager_constructor = any(isinstance(node, ast.Assign) and
                            any(isinstance(target, ast.Name) and
                                target.id == "_NATIVE" for target in node.targets) and
                            isinstance(node.value, ast.Call) and
                            isinstance(node.value.func, ast.Name) and
                            node.value.func.id == "_Native"
                            for node in zig.body)
    native_class = next((node for node in zig.body
                         if isinstance(node, ast.ClassDef) and node.name == "_Native"), None)
    native_loader = bool(native_class and any(
        isinstance(node, ast.Call) and
        attribute_chain(node.func) == ("ctypes", "CDLL")
        for node in walk_ast(native_class)))
    error_alias = any(isinstance(node, ast.Assign) and
                      any(isinstance(target, ast.Name) and target.id == "error"
                          for target in node.targets) and
                      isinstance(node.value, ast.Name) and
                      node.value.id == "PatternError"
                      for node in zig.body)
    scanner_present = any(isinstance(node, ast.ClassDef) and
                          node.name == "Scanner" for node in zig.body)
    debug_present = any(isinstance(node, ast.Assign) and
                        any(isinstance(target, ast.Name) and target.id == "DEBUG"
                            for target in node.targets)
                        for node in zig.body)
    require(zig_all == standard_all,
            "the actual current Zig wildcard surface no longer matches Python")
    require(error_alias and scanner_present and debug_present,
            "the actual current Zig public aliases or direct attributes changed")
    require(bridge_import and eager_constructor and native_loader,
            "the actual Zig eager native-load AST proof changed")
    require(not version_present,
            "the exact observed public __version__ omission no longer exists")
    return {
        "public_entrypoint_source_docstring": body[0].value.value,
        "historical_family": "zig",
        "historical_family_module": "candidates.zig_candidate",
        "exact_wildcard_exports": standard_all,
        "wildcard_exports_match_python": True,
        "direct_debug_attribute_present": True,
        "direct_scanner_attribute_present": True,
        "pattern_error_alias_matches": True,
        "stdlib_module_version": standard_version,
        "historical_zig_module_version": zig_version,
        "public_entrypoint_module_version": "MISSING",
        "historical_zig_version_exported_by_wildcard": False,
        "potential_eager_native_bridge_imports": 1,
        "potential_eager_native_engine_loads": 1,
        "potential_distinct_eager_native_loads": 2,
        "actual_candidate_imports_by_verifier": 0,
        "actual_public_entrypoint_imports_by_verifier": 0,
        "actual_stdlib_regex_imports_by_verifier": 0,
        "actual_native_loads_by_verifier": 0,
    }


def case_matrix() -> list[dict[str, str]]:
    return [{"id": name, "observed_status": status}
            for name, status in CASE_ROWS]


def clone(value: object) -> object:
    if type(value) is dict:
        return {key: clone(item) for key, item in value.items()}
    if type(value) is list:
        return [clone(item) for item in value]
    if type(value) is tuple:
        return tuple(clone(item) for item in value)
    return value


def validate_contract(document: object) -> dict[str, object]:
    require(type(document) is dict and
            document.get("schema") == SCHEMA + "-source-freeze" and
            document.get("version") == 1,
            "the frozen public-entrypoint contract schema changed")
    require(document.get("goal_sha256") == GOAL_SHA256,
            "the immutable original goal was substituted")
    original = document.get("original_correctness")
    require(type(original) is dict and original == {
        "case_count": ORIGINAL_CASES, "suite_count": ORIGINAL_SUITES,
        "private_waiver_count": PRIVATE_WAIVERS,
        "additional_signature_case_count": ADDITIONAL_SIGNATURE_CASES,
        "additional_signature_cases_in_original_denominator": False,
    }, "the frozen original or separately counted signature denominator changed")
    require(document.get("pinned_python") == PYTHON,
            "the sole pinned stable reference interpreter was substituted")
    require(document.get("current_overview_version") == OVERVIEW_VERSION,
            "the exact published current overview version changed")
    require(document.get("owners") == owner_mapping(),
            "an exact public-entrypoint or current-history source owner changed")
    rows = case_matrix()
    require(document.get("case_matrix") == rows and len(rows) == 32 and
            len({row["id"] for row in rows}) == len(rows),
            "the complete separately counted entrypoint observation matrix changed")
    actual_matrix_digest = digest(canonical_text(rows).encode("ascii"))
    require(MATRIX_SHA256 != "PENDING_PUBLIC_ENTRYPOINT_MATRIX_SHA256",
            "the separately frozen public-entrypoint matrix digest is not yet released")
    require(document.get("case_matrix_sha256") == MATRIX_SHA256 == actual_matrix_digest,
            "the exact separate public-entrypoint observation matrix digest changed")
    expected = {
        "source_freeze_status": "PASS",
        "observed_public_entrypoint_status": "FAIL",
        "observed_public_entrypoint_classification": "UNQUALIFIED_ZIG_PROTOTYPE",
        "public_entrypoint_qualified": False,
        "qualified_candidate_count": 0,
        "winner_selected": False,
        "stdlib_fallback_allowed": False,
        "external_engine_allowed": False,
        "cross_candidate_delegation_allowed": False,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "installed_public_artifact": "NOT MEASURED",
        "native_undefined_behavior": "NOT MEASURED",
        "native_memory": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "final_holdout_status": "NOT OPENED",
        "final_holdout_planned_case_count": PLANNED_HOLDOUT_CASES,
        "final_holdout_generated": False,
        "final_holdout_opened": False,
        "actual_reference_workers_started": 0,
        "actual_candidate_workers_started": 0,
        "actual_candidate_imports": 0,
        "actual_public_entrypoint_imports": 0,
        "actual_stdlib_regex_imports": 0,
        "actual_native_libraries_loaded": 0,
        "actual_archives_opened": 0,
        "actual_archives_decompressed": 0,
        "actual_subprocesses_started": 0,
        "actual_network_requests": 0,
        "actual_clock_samples": 0,
        "actual_holdout_cases_read": 0,
        "actual_hidden_cases_read": 0,
        "workspace_files_written": 0,
        "physical_audit_hook_required": True,
        "physical_audit_denies_unlisted_reads": True,
        "physical_audit_denies_module_imports": True,
        "physical_audit_denies_native_loading": True,
        "physical_audit_denies_execution_and_processes": True,
        "physical_audit_denies_network_and_writes": True,
    }
    require(document.get("boundaries") == expected,
            "the source-only effect boundary or honest failed-entrypoint status changed")
    future = document.get("future_public_winner_policy")
    require(type(future) is dict and future == {
        "allows_candidate_import_in_source_freeze": False,
        "allows_entrypoint_import_in_source_freeze": False,
        "allows_stdlib_regex_fallback": False,
        "allows_cross_family_fallback": False,
        "allows_external_regex_engine": False,
        "allows_premature_winner": False,
        "requires_three_distinct_correctness_qualified_families": True,
        "requires_original_case_count": ORIGINAL_CASES,
        "requires_original_suite_count": ORIGINAL_SUITES,
        "requires_original_private_waiver_count": PRIVATE_WAIVERS,
        "requires_separate_signature_case_count": ADDITIONAL_SIGNATURE_CASES,
        "requires_separate_signature_pass": True,
        "requires_actual_packaged_public_import": True,
        "requires_exact_public_module_version": "2.2.1",
        "requires_exact_python_wildcard_exports": True,
        "requires_direct_debug_and_scanner_attributes": True,
        "requires_independent_runtime_no_delegation": True,
        "requires_safety_gates": True,
        "requires_frozen_fair_performance_oracle": True,
        "requires_statistically_qualified_winner": True,
        "requires_verified_winner_native_provenance": True,
        "fixes_public_entrypoint_in_this_chunk": False,
    }, "the future fail-closed winner policy was weakened")
    return document


def validate_original(document: object) -> None:
    require(type(document) is dict and
            document.get("schema") == "rebar-cpython-re-p0-completeness-v1",
            "the original immutable compatibility inventory changed")
    denominator = document.get("denominator")
    require(type(denominator) is dict and
            denominator.get("final_required_case_execution_denominator") == ORIGINAL_CASES and
            denominator.get("private_upstream_methods_outside_public_denominator") == PRIVATE_WAIVERS and
            type(denominator.get("counted_suite_ids")) is list and
            len(denominator["counted_suite_ids"]) == ORIGINAL_SUITES,
            "the exact original 31,237 / 13 / 13 denominator changed")
    runtime = document.get("runtime")
    require(type(runtime) is dict and runtime.get("python_version") == "3.14.6" and
            type(runtime.get("executable")) is dict and
            runtime["executable"].get("path") == PYTHON and
            runtime["executable"].get("sha256") ==
            "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
            "the pinned stable CPython reference was substituted")
    obligations = document.get("obligations")
    require(type(obligations) is dict and type(obligations.get("additional")) is list,
            "the exact original public obligation crosswalk is missing")
    versions = [row for row in obligations["additional"]
                if type(row) is dict and row.get("id") == "API-MODULE-VERSION-METADATA"]
    require(len(versions) == 1 and versions[0].get("expected_version") == "2.2.1" and
            versions[0].get("status") == "PASS",
            "the mandatory original public module-version obligation changed")


def validate_signatures(matrix: object, receipt: object) -> None:
    require(type(matrix) is dict and
            matrix.get("schema") == "rebar-python-re-callable-introspection-v1-source-freeze",
            "the separately frozen callable-signature inventory changed")
    addition = matrix.get("additional_obligation")
    require(type(addition) is dict and addition.get("case_count") == ADDITIONAL_SIGNATURE_CASES and
            addition.get("included_in_original_31237_denominator") is False and
            addition.get("matrix_sha256") ==
            "89ff9e5197ac0fee63a5b7f3880d9d66083f7e25255d0d062e14ff84ab5c884b",
            "the separately frozen fifty public signatures were omitted or double-counted")
    require(type(receipt) is dict and
            receipt.get("schema") ==
            "rebar-owned-callable-introspection-reference-v2-durable-publication-receipt" and
            receipt.get("publication_status") == "PASS" and
            receipt.get("reference_status") == "PASS" and
            receipt.get("additional_case_count") == ADDITIONAL_SIGNATURE_CASES and
            receipt.get("reference_failure_count") == 0 and
            receipt.get("candidate_introspection") == "NOT MEASURED" and
            receipt.get("matrix_sha256") == addition["matrix_sha256"],
            "the actual independent signature baseline or unmeasured candidate was misreported")


def validate_inventory(document: object) -> None:
    require(type(document) is dict and
            document.get("schema") ==
            "rebar-phase2-six-candidate-independence-static-audit-v2" and
            document.get("family_count") == 6 and
            document.get("source_owner_count") == 25 and
            document.get("python_baseline_is_a_candidate") is False,
            "six first-party source designs were misrepresented as qualified engines")
    families = document.get("families")
    require(type(families) is list and len(families) == 6,
            "the exact distinct-family source inventory changed")
    zig = [row for row in families if type(row) is dict and row.get("name") == "zig"]
    require(len(zig) == 1 and type(zig[0].get("owners")) is list,
            "the first-party historical Zig source owner is missing")
    matches = [owner for owner in zig[0]["owners"]
               if type(owner) is dict and
               owner.get("path") == "candidates/zig_candidate.py"]
    require(len(matches) == 1 and
            matches[0].get("sha256") == owner_mapping()["historical_zig_adapter"]["sha256"],
            "the authenticated historical Zig adapter was replaced")
    project = document.get("python_project_support_owners")
    require(type(project) is dict and type(project.get("owners")) is list,
            "the authenticated project support-owner inventory is missing")
    configs = [owner for owner in project["owners"] if type(owner) is dict and
               owner.get("path") == "pyproject.toml"]
    require(len(configs) == 1 and
            configs[0].get("sha256") == owner_mapping()["project_configuration"]["sha256"],
            "the independently authenticated project configuration changed")
    boundaries = document.get("boundaries")
    require(type(boundaries) is dict and
            boundaries.get("runtime_no_delegation") == "NOT ESTABLISHED" and
            boundaries.get("candidate_correctness_qualified_count") == 0,
            "a static source inventory was misrepresented as runtime qualification")


def validate_repaired_rust_v7(document: object) -> dict[str, object]:
    require(type(document) is dict and
            document.get("schema") ==
            "rebar-owned-repaired-rust-original-campaign-v7-recoverable-source-freeze" and
            document.get("version") == 7 and document.get("family") == "rust" and
            document.get("status") ==
            "SOURCE FROZEN; CORRECTED RUST V13 CANDIDATE NOT RUN",
            "the actually pushed repaired Rust V7 source freeze was substituted")
    source = document.get("source")
    protocol = document.get("protocol")
    require(type(source) is dict and
            source.get("path") == "tools/run_owned_repaired_rust_original_campaign_v7.py" and
            source.get("sha256") ==
            owner_mapping()["repaired_rust_v7_source"]["sha256"] and
            type(protocol) is dict and
            protocol.get("path") ==
            "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V7.md" and
            protocol.get("sha256") ==
            owner_mapping()["repaired_rust_v7_protocol"]["sha256"],
            "the repaired Rust V7 source or protocol owner was forged")
    original = document.get("original_oracle")
    require(type(original) is dict and
            original.get("case_execution_denominator") == ORIGINAL_CASES and
            original.get("suite_count") == ORIGINAL_SUITES and
            original.get("named_private_waiver_count") == PRIVATE_WAIVERS and
            original.get("stdlib_re_fallback_allowed") is False and
            original.get("cross_family_matching_allowed") is False and
            original.get("external_regex_dependency_allowed") is False,
            "the repaired Rust V7 changed the original oracle or allowed fallback")
    accounting = document.get("current_historical_accounting")
    require(type(accounting) is dict and
            accounting.get("evidence_owner_lower_bound_before_new_campaign") == 166 and
            accounting.get("authenticated_reference_lower_bound_before_new_campaign") == 171 and
            accounting.get("qualified_candidate_count") == 0 and
            accounting.get("future_campaign_evidence_owners_created") == 0,
            "the repaired Rust V7 claimed future evidence or an early qualified candidate")
    effects = document.get("source_only_effects")
    require(type(effects) is dict and
            effects.get("actual_candidate_imports") == 0 and
            effects.get("actual_candidate_workers") == 0 and
            effects.get("actual_native_activations") == 0 and
            effects.get("actual_native_library_loads") == 0 and
            effects.get("actual_reference_workers") == 0 and
            effects.get("v13_source_build_archive_read_count") == 0 and
            effects.get("matching_archive_bytes_read") == 0 and
            effects.get("candidate_correctness") == "NOT MEASURED" and
            effects.get("candidate_qualified") is False and
            effects.get("holdout") == "NOT OPENED" and
            effects.get("performance") == "NOT MEASURED" and
            effects.get("winner_selected") is False,
            "the repaired Rust source freeze was represented as an actual candidate run")
    failure = document.get("preserved_actual_v6_preflight_failure")
    require(type(failure) is dict and failure.get("status") == "FAIL" and
            failure.get("actual_controller_process_count") == 1 and
            failure.get("actual_candidate_workers") == 0 and
            failure.get("actual_source_build_archive_read_count") == 1 and
            failure.get("historical_controller_ledger_omitted_archive_effect") is True and
            failure.get("matching_archive_read_count") == 0,
            "the actual failed historical Rust V6 controller or archive effect was concealed")
    return document


def validate_overview(document: object, *, inputs: bool,
                      repaired_rust: dict[str, object]) -> None:
    suffix = "inputs" if inputs else "summary"
    require(type(document) is dict and
            document.get("schema") ==
            "rebar-candidate-current-overview-v" + str(OVERVIEW_VERSION) + "-" + suffix and
            document.get("version") == OVERVIEW_VERSION,
            "the authenticated current overview " + suffix + " was substituted")
    exact = {
        "full_case_denominator": ORIGINAL_CASES,
        "suite_count": ORIGINAL_SUITES,
        "private_waiver_count": PRIVATE_WAIVERS,
        "additional_signature_frozen_case_count": ADDITIONAL_SIGNATURE_CASES,
        "additional_signature_reference_status": "PASS",
        "additional_signature_candidate_status": "NOT RUN",
        "qualified_candidate_count": 0,
        "winner_selected": False,
        "first_party_source_inventory_family_count": 6,
        "frozen_corrected_runner_source_family_count": 2,
        "actually_runnable_candidate_family_count": 0,
        "actual_rust_controller_status": "FAIL",
        "actual_rust_candidate_workers": 0,
        "actual_rust_source_build_archive_read_count": 1,
        "actual_rust_controller_ledger_omits_source_build_archive_effect": True,
        "zig_original_campaign_status": "FAIL",
        "zig_original_campaign_semantic_mismatch_count": 1764,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "authenticated_evidence_owner_lower_bound": 166,
        "authenticated_history_reference_lower_bound": 171,
        "source_build_archive_gzip_inflation_count_by_graph": 0,
        "matching_archive_gzip_inflation_count": 0,
        "reference_archive_gzip_inflation_count": 0,
        "final_holdout_opened": False,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "corrected_rust_v7_source_sha256":
            "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104",
        "corrected_rust_v7_protocol_sha256":
            "0b5182a7eee74e586839abc3a0e8bdd122bac248e9cb3b76c603c5add9281840",
        "corrected_rust_v7_contract_sha256":
            "9c8e85dcc5dcf0a00953b36dd02c29c2ab7b1ed0b4281eb27f6693c058d155e5",
        "corrected_rust_v7_source_status":
            "RUST V7 HELPER PREFLIGHT SOURCE FROZEN AND SOURCE-TESTED; ACTUAL CANDIDATE NOT RUN",
        "corrected_rust_v7_actual_candidate_workers": 0,
        "corrected_rust_v7_actual_native_activations": 0,
        "corrected_rust_v7_candidate_matching_status": "NOT RUN",
        "corrected_rust_v7_candidate_qualified": False,
        "corrected_rust_v7_matching_archive_reads": 0,
        "corrected_rust_v7_source_build_archive_reads": 0,
        "corrected_rust_v7_current_evidence_owner_lower_bound": 166,
        "corrected_rust_v7_current_history_reference_lower_bound": 171,
        "corrected_rust_v7_future_evidence_owner_lower_bound": 168,
        "corrected_rust_v7_future_history_reference_lower_bound": 173,
        "corrected_rust_v7_future_publication_distinct_owner_count": 2,
        "corrected_rust_v7_future_results_require_all_thirteen_workers": True,
        "corrected_rust_v7_all_worker_and_recovery_source_wall_tested": True,
        "corrected_rust_v7_publication_source_tested_only": True,
        "corrected_rust_v7_runtime_no_delegation": "NOT ESTABLISHED",
        "public_entrypoint_status": "UNQUALIFIED ZIG PROTOTYPE; NOT A WINNER",
        "public_entrypoint_module_sha256":
            "289769bd637ea525ae7e71d263377e15c0f394ba20619c11b98e266f57fcc34f",
        "public_entrypoint_project_sha256":
            "7d50e8c6c2bc76a0e3ddcac6b5f157b013bcfd76944fdeb2c1c81e0181ae7825",
        "public_entrypoint_selected_family": "zig",
        "public_entrypoint_module_version_status": "FAIL/MISSING",
        "public_entrypoint_qualified": False,
        "public_entrypoint_winner_selected": False,
        "public_entrypoint_package_mode": False,
        "public_entrypoint_installation_status": "NOT MEASURED",
        "public_entrypoint_runtime_no_delegation": "NOT ESTABLISHED",
        "public_entrypoint_historical_zig_mismatch_count": 1764,
        "public_entrypoint_actual_imports_by_graph": 0,
        "public_entrypoint_actual_native_loads_by_graph": 0,
        "public_entrypoint_packaged_artifact": "NOT MEASURED",
    }
    for name, expected in exact.items():
        require(document.get(name) == expected,
                "the actual frozen public-entrypoint history changed: " + name)
    rust_freeze = document.get("corrected_rust_v7_source_freeze")
    require(type(rust_freeze) is dict and
            rust_freeze.get("complete_frozen_contract") == repaired_rust and
            rust_freeze.get("actual_candidate_matching") == "NOT RUN" and
            rust_freeze.get("actual_candidate_workers") == 0 and
            rust_freeze.get("actual_matching_archive_reads") == 0 and
            rust_freeze.get("actual_source_build_archive_reads") == 0 and
            rust_freeze.get("actual_native_activations") == 0 and
            rust_freeze.get("candidate_qualified") is False,
            "the current graph does not bind the exact actually pushed Rust V7 source freeze")
    public = document.get("public_entrypoint_static_audit")
    require(type(public) is dict and
            public.get("schema") ==
            "rebar-candidate-current-overview-v44-static-public-entrypoint" and
            public.get("status") == "UNQUALIFIED ZIG PROTOTYPE; NOT A WINNER" and
            public.get("public_module_version_status") == "FAIL/MISSING" and
            public.get("selected_candidate_family") == "zig" and
            public.get("selected_historical_zig_mismatch_count") == 1764 and
            public.get("public_module_qualified") is False and
            public.get("winner_selected") is False and
            public.get("actual_imports_by_graph") == 0 and
            public.get("actual_native_loads_by_graph") == 0 and
            public.get("project_package_mode") is False and
            public.get("packaged_artifact") == "NOT MEASURED" and
            type(public.get("module")) is dict and
            public["module"].get("sha256") ==
            owner_mapping()["public_entrypoint"]["sha256"] and
            type(public.get("project")) is dict and
            public["project"].get("sha256") ==
            owner_mapping()["project_configuration"]["sha256"],
            "the current V44 graph concealed the actual failed public entrypoint")
    if inputs:
        for name in ("actual_candidate_imports", "actual_candidate_workers_started_by_graph",
                     "actual_reference_workers_started_by_graph",
                     "actual_compiler_processes_started_by_graph", "clock_samples",
                     "timing_trials_run", "hidden_cases_read", "performance_files_read"):
            require(document.get(name) == 0,
                    "the published graph performed an unauthorized effect: " + name)


def validate_future_winner(document: object) -> None:
    require(type(document) is dict,
            "a future public winner needs independently authenticated actual evidence")
    exact = {
        "winner_selected": True,
        "winner_original_case_count": ORIGINAL_CASES,
        "winner_original_suite_count": ORIGINAL_SUITES,
        "winner_original_private_waiver_count": PRIVATE_WAIVERS,
        "winner_original_status": "PASS",
        "winner_signature_case_count": ADDITIONAL_SIGNATURE_CASES,
        "winner_signature_status": "PASS",
        "actual_public_entrypoint_status": "PASS",
        "actual_installed_public_import": "PASS",
        "actual_public_module_version": "2.2.1",
        "exact_public_wildcard_exports": True,
        "direct_debug_attribute": True,
        "direct_scanner_attribute": True,
        "runtime_no_delegation": "PASS",
        "native_safety_status": "PASS",
        "frozen_fair_performance_status": "PASS",
        "statistical_winner_status": "PASS",
        "winner_native_provenance_status": "PASS",
        "stdlib_fallback_used": False,
        "external_regex_engine_used": False,
        "cross_candidate_engine_used": False,
    }
    for name, expected in exact.items():
        require(document.get(name) == expected,
                "a future public winner weakened a mandatory gate: " + name)
    families = document.get("distinct_correctness_qualified_families")
    require(type(families) is list and len(families) >= 3 and
            all(type(name) is str for name in families) and
            len(set(families)) == len(families) and
            set(families).issubset({"c_vm", "rust", "zig", "cpp", "go", "fortran"}),
            "at least three actual distinct first-party families must be qualified")
    require(document.get("winner_family") in families,
            "the public winner is not one of the actually qualified source families")


def synthetic_surface_sources() -> tuple[bytes, bytes, bytes]:
    shim = (b'"""Measured, from-scratch replacement for Python\'s public re interface."""\n'
            b"from candidates.zig_candidate import *\n"
            b"from candidates.zig_candidate import DEBUG, Scanner\n"
            b"from candidates.zig_candidate import __all__\n")
    names = ["match", "fullmatch", "search", "sub", "subn", "split", "findall",
             "finditer", "compile", "purge", "escape", "error", "Pattern", "Match",
             "A", "I", "L", "M", "S", "X", "U", "ASCII", "IGNORECASE",
             "LOCALE", "MULTILINE", "DOTALL", "VERBOSE", "UNICODE", "NOFLAG",
             "RegexFlag", "PatternError"]
    listing = repr(names).encode("ascii")
    zig = (b"import ctypes\nfrom candidates import _zig_bridge\n"
           b'__version__ = "2.2.1"\nDEBUG = 128\n'
           b"class PatternError(Exception):\n    pass\n"
           b"error = PatternError\nclass Scanner:\n    pass\n"
           b"class _Native:\n    def __init__(self):\n"
           b"        self.library = ctypes.CDLL('candidate-owned.so')\n"
           b"_NATIVE = _Native()\n__all__ = " + listing + b"\n")
    stdlib = b'__version__ = "2.2.1"\n__all__ = ' + listing + b"\n"
    return shim, zig, stdlib


def run_self_test(contract: dict[str, object]) -> dict[str, object]:
    no_matcher_imports()
    require(_AUDIT_INSTALLED, "the source-only physical audit wall was not installed")
    passed = []

    def accept(name: str, callback: object) -> None:
        require(name not in passed, "duplicate positive or hostile control: " + name)
        try:
            result = callback()  # type: ignore[operator]
        except Exception as error:
            raise FreezeError("a positive source-only control failed: " + name +
                              ": " + type(error).__name__ + ": " +
                              str(error)) from error
        require(result is not False, "a positive source-only control returned false: " + name)
        passed.append(name)

    def reject(name: str, callback: object) -> None:
        require(name not in passed, "duplicate positive or hostile control: " + name)
        try:
            callback()  # type: ignore[operator]
        except (FreezeError, ValueError, TypeError, OverflowError, UnicodeError, RecursionError):
            passed.append(name)
            return
        raise FreezeError("a hostile source-only control was accepted: " + name)

    accept("strict-json-basic-object", lambda: decode_json(b'{"b":[true,false,null],"a":2}') ==
           {"b": [True, False, None], "a": 2})
    accept("strict-json-canonical-sorted", lambda: canonical_text({"z": 2, "a": [True, None]}) ==
           '{"a":[true,null],"z":2}')
    accept("strict-json-unicode-escape", lambda: decode_json(b'"\\u00e9"') == "\u00e9")
    accept("strict-json-paired-unicode-surrogate",
           lambda: decode_json(b'"\\ud83d\\ude00"') == "\U0001f600")
    accept("strict-json-control-escape", lambda: decode_json(b'"a\\n\\t"') == "a\n\t")
    accept("strict-json-negative-index", lambda: decode_json(b'-2147483649') == -2147483649)
    accept("strict-json-floating-number", lambda: decode_json(b'1.25e2') == 125.0)
    json_attacks = (
        ("duplicate-key", b'{"a":1,"a":2}'),
        ("nested-duplicate-key", b'{"x":{"a":1,"a":2}}'),
        ("trailing-document", b'{"a":1}{"a":2}'),
        ("trailing-comma-object", b'{"a":1,}'),
        ("trailing-comma-array", b'[1,]'),
        ("leading-zero", b'01'),
        ("negative-leading-zero", b'-01'),
        ("missing-fraction", b'1.'),
        ("missing-exponent", b'1e'),
        ("infinite-exponent", b'1e99999'),
        ("plus-number", b'+1'),
        ("nan-number", b'NaN'),
        ("infinite-number", b'Infinity'),
        ("unquoted-key", b'{a:1}'),
        ("unclosed-array", b'[1'),
        ("unclosed-object", b'{"a":1'),
        ("unclosed-string", b'"x'),
        ("invalid-escape", b'"\\x"'),
        ("short-unicode-escape", b'"\\u12"'),
        ("invalid-unicode-escape", b'"\\ugg00"'),
        ("unpaired-high-surrogate", b'"\\ud800"'),
        ("unpaired-low-surrogate", b'"\\udc00"'),
        ("mismatched-surrogate", b'"\\ud800\\u0041"'),
        ("literal-control", b'"a\n"'),
        ("invalid-utf8", b'"\xff"'),
        ("empty-document", b''),
        ("oversized-number", (b'1' * 129)),
    )
    for name, raw in json_attacks:
        reject("reject-json-" + name, lambda data=raw: decode_json(data))
    reject("reject-json-nesting-bomb",
           lambda: decode_json(b"[" * 50 + b"0" + b"]" * 50))
    reject("reject-canonical-nan", lambda: canonical_text(float("nan")))
    reject("reject-canonical-infinity", lambda: canonical_text(float("inf")))
    reject("reject-non-string-object-key", lambda: canonical_text({1: "no"}))

    for name in ("re", "_sre", "rebar", "candidates", "candidates.zig_candidate",
                 "ctypes", "subprocess", "socket", "regex", "re2", "pcre2"):
        reject("physically-block-module-import-" + name,
               lambda module=name: __import__(module))
    for name, event, arguments in (
        ("foreign-native-load", "ctypes.dlopen", ("foreign-regex.so",)),
        ("foreign-native-symbol", "ctypes.dlsym", ("foreign-regex", "match")),
        ("foreign-subprocess", "subprocess.Popen", ("foreign-regex", [], None, None)),
        ("foreign-process-spawn", "os.posix_spawn", ("/bin/sh", [], {})),
        ("foreign-process-fork", "os.fork", ()),
        ("network-socket", "socket.__new__", (None, 2, 1, 0)),
        ("network-connection", "socket.connect", (None, ("127.0.0.1", 1))),
        ("network-name-resolution", "socket.getaddrinfo", ("example.invalid", 443, 0, 0, 0)),
        ("clock-sample", "time.time", ()),
        ("marshal-execution", "marshal.loads", (b"foreign",)),
        ("dynamic-execution", "exec", ("foreign-code",)),
        ("environment-mutation", "os.putenv", (b"REBAR_FOREIGN", b"1")),
        ("workspace-mutation", "os.remove", (ROOT + "/rebar.py", -1)),
    ):
        reject("physically-block-" + name,
               lambda label=event, args=arguments: sys.audit(label, *args))
    for name, path, mode in (
        ("unknown-source-owner", ROOT + "/not-a-frozen-source.json", "rb"),
        ("holdout-path", ROOT + "/holdout/cases.json.gz", "rb"),
        ("matching-archive", ROOT + "/oracle/phase2/evidence/matching.json.gz", "rb"),
        ("external-config", "/etc/passwd", "rb"),
        ("workspace-write", ROOT + "/rebar.py", "wb"),
        ("workspace-append", ROOT + "/rebar.py", "ab"),
    ):
        reject("physically-block-file-" + name,
               lambda location=path, access=mode: builtins.open(location, access))
    reject("physically-block-owner-create-truncate", lambda:
           os.open(ROOT + "/rebar.py", os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600))
    reject("physically-block-executable-compile", lambda:
           compile("__import__('re')", "foreign-executable.py", "exec"))
    reject("physically-block-eval", lambda: eval("2 + 2"))
    no_matcher_imports()

    project = (b'[project]\nname = "rebar-experiment"\nversion = "0.0.0"\n'
               b'description = "fixture"\nrequires-python = ">=3.14,<3.15"\n'
               b'dependencies = []\n\n[tool.uv]\npackage = false\n')
    accept("strict-project-package-disabled",
           lambda: parse_simple_project(project)["tool.uv"]["package"] is False)
    for name, attack in (
        ("duplicate-section", project + b"\n[tool.uv]\npackage = false\n"),
        ("duplicate-package", project + b"package = false\n"),
        ("missing-project", b"[tool.uv]\npackage = false\n"),
        ("missing-uv", b"[project]\nname = 'rebar-experiment'\n"),
        ("array-section", b"[[project]]\nname='x'\n[tool.uv]\npackage=false\n"),
        ("invalid-section", b"[../project]\nname='x'\n[tool.uv]\npackage=false\n"),
        ("invalid-key", b"[project]\na/b='x'\n[tool.uv]\npackage=false\n"),
        ("assignment-before-section", b"name='x'\n" + project),
        ("dynamic-value", b"[project]\nname = __import__('re')\n[tool.uv]\npackage=false\n"),
        ("foreign-dependencies", b"[project]\ndependencies=['regex']\n[tool.uv]\npackage=false\n"),
        ("invalid-utf8", b"[project]\nname='\xff'\n[tool.uv]\npackage=false\n"),
    ):
        reject("reject-project-" + name,
               lambda fixture=attack: parse_simple_project(fixture))

    shim, zig, standard = synthetic_surface_sources()
    accept("synthetic-exact-missing-public-version",
           lambda: analyze_surface(shim, zig, standard)["public_entrypoint_module_version"] == "MISSING")
    accept("synthetic-python-wildcard-is-not-falsely-rejected",
           lambda: analyze_surface(shim, zig, standard)["wildcard_exports_match_python"] is True)
    accept("synthetic-debug-and-scanner-are-not-falsely-rejected",
           lambda: (lambda result: result["direct_debug_attribute_present"] and
                    result["direct_scanner_attribute_present"])(analyze_surface(shim, zig, standard)))
    accept("synthetic-potential-native-loads-are-distinct-from-effects",
           lambda: (lambda result: result["potential_distinct_eager_native_loads"] == 2 and
                    result["actual_native_loads_by_verifier"] == 0)(
                        analyze_surface(shim, zig, standard)))

    shim_attacks = (
        ("stdlib-import", b"import re\n" + shim),
        ("private-stdlib-engine", b"import _sre\n" + shim),
        ("foreign-regex", b"import regex\n" + shim),
        ("pcre", b"import pcre2\n" + shim),
        ("re2", b"import re2\n" + shim),
        ("cross-family-rust", shim.replace(b"candidates.zig_candidate", b"candidates.rust_candidate")),
        ("cross-family-c", shim.replace(b"candidates.zig_candidate", b"candidates.vm_candidate")),
        ("cross-family-go", shim.replace(b"candidates.zig_candidate", b"candidates.go_candidate")),
        ("hidden-import", shim + b"__import__('re')\n"),
        ("computed-import", shim + b"__import__('r' + 'e')\n"),
        ("dynamic-loader", shim + b"ctypes.CDLL('foreign.so')\n"),
        ("native-process", shim + b"os.system('foreign-engine')\n"),
        ("module-version-silently-added", shim + b'__version__ = "2.2.1"\n'),
        ("wildcard-omitted", shim.replace(b" import *\n", b" import Pattern\n")),
        ("debug-omitted", shim.replace(b"DEBUG, Scanner", b"Scanner")),
        ("scanner-omitted", shim.replace(b"DEBUG, Scanner", b"DEBUG")),
        ("public-all-omitted", shim.replace(b"import __all__", b"import __version__")),
        ("premature-selected-winner", shim + b"WINNER = 'zig'\n"),
    )
    for name, attack in shim_attacks:
        reject("reject-entrypoint-" + name,
               lambda data=attack: analyze_surface(data, zig, standard))
    zig_attacks = (
        ("hidden-version-export", zig.replace(b"'PatternError']", b"'PatternError', '__version__']")),
        ("wrong-version", zig.replace(b'"2.2.1"', b'"2.2.2"')),
        ("missing-native-bridge", zig.replace(b"from candidates import _zig_bridge\n", b"")),
        ("missing-eager-constructor", zig.replace(b"_NATIVE = _Native()\n", b"")),
        ("hidden-native-loader", zig.replace(b"ctypes.CDLL", b"ctypes.PyDLL")),
        ("missing-scanner", zig.replace(b"class Scanner:", b"class OtherScanner:")),
        ("missing-debug", zig.replace(b"DEBUG = 128\n", b"OTHER_DEBUG = 128\n")),
        ("wrong-error-alias", zig.replace(b"error = PatternError", b"error = Exception")),
    )
    for name, attack in zig_attacks:
        reject("reject-zig-source-" + name,
               lambda data=attack: analyze_surface(shim, data, standard))
    for name, attack in (
        ("wrong-version", standard.replace(b'"2.2.1"', b'"2.2.0"')),
        ("duplicate-public-export", standard.replace(b"'PatternError']", b"'PatternError', 'PatternError']")),
        ("changed-wildcard-order", standard.replace(b"'match', 'fullmatch'", b"'fullmatch', 'match'")),
    ):
        reject("reject-stdlib-source-" + name,
               lambda data=attack: analyze_surface(shim, zig, data))

    accept("frozen-contract-remains-unqualified", lambda: validate_contract(contract))
    mutations = (
        ("false-source-pass-as-candidate-pass", ("boundaries", "observed_public_entrypoint_status"), "PASS"),
        ("false-qualified-entrypoint", ("boundaries", "public_entrypoint_qualified"), True),
        ("false-qualified-candidate", ("boundaries", "qualified_candidate_count"), 1),
        ("false-selected-winner", ("boundaries", "winner_selected"), True),
        ("stdlib-fallback", ("boundaries", "stdlib_fallback_allowed"), True),
        ("foreign-engine", ("boundaries", "external_engine_allowed"), True),
        ("cross-family-fallback", ("boundaries", "cross_candidate_delegation_allowed"), True),
        ("false-runtime-audit", ("boundaries", "runtime_no_delegation"), "PASS"),
        ("false-installed-artifact", ("boundaries", "installed_public_artifact"), "PASS"),
        ("false-safety", ("boundaries", "native_undefined_behavior"), "PASS"),
        ("false-performance", ("boundaries", "performance"), "PASS"),
        ("opened-holdout", ("boundaries", "final_holdout_opened"), True),
        ("generated-holdout", ("boundaries", "final_holdout_generated"), True),
        ("native-load", ("boundaries", "actual_native_libraries_loaded"), 1),
        ("candidate-import", ("boundaries", "actual_candidate_imports"), 1),
        ("entrypoint-import", ("boundaries", "actual_public_entrypoint_imports"), 1),
        ("stdlib-regex-import", ("boundaries", "actual_stdlib_regex_imports"), 1),
        ("archive-open", ("boundaries", "actual_archives_opened"), 1),
        ("archive-inflate", ("boundaries", "actual_archives_decompressed"), 1),
        ("subprocess", ("boundaries", "actual_subprocesses_started"), 1),
        ("network", ("boundaries", "actual_network_requests"), 1),
        ("clock", ("boundaries", "actual_clock_samples"), 1),
        ("hidden-case", ("boundaries", "actual_hidden_cases_read"), 1),
        ("holdout-case", ("boundaries", "actual_holdout_cases_read"), 1),
        ("workspace-write", ("boundaries", "workspace_files_written"), 1),
        ("wrong-original-denominator", ("original_correctness", "case_count"), ORIGINAL_CASES + 1),
        ("merged-signature-denominator", ("original_correctness", "additional_signature_cases_in_original_denominator"), True),
        ("wrong-private-waiver", ("original_correctness", "private_waiver_count"), PRIVATE_WAIVERS + 1),
        ("wrong-suite-denominator", ("original_correctness", "suite_count"), ORIGINAL_SUITES + 1),
        ("wrong-separate-signature-denominator", ("original_correctness", "additional_signature_case_count"), 49),
        ("future-stdlib-fallback", ("future_public_winner_policy", "allows_stdlib_regex_fallback"), True),
        ("future-external-fallback", ("future_public_winner_policy", "allows_external_regex_engine"), True),
        ("future-cross-family-fallback", ("future_public_winner_policy", "allows_cross_family_fallback"), True),
        ("future-premature-winner", ("future_public_winner_policy", "allows_premature_winner"), True),
        ("future-missing-runtime-proof", ("future_public_winner_policy", "requires_independent_runtime_no_delegation"), False),
        ("future-missing-packaged-import", ("future_public_winner_policy", "requires_actual_packaged_public_import"), False),
        ("future-missing-signature-gate", ("future_public_winner_policy", "requires_separate_signature_pass"), False),
        ("future-missing-three-families", ("future_public_winner_policy", "requires_three_distinct_correctness_qualified_families"), False),
        ("future-missing-safety", ("future_public_winner_policy", "requires_safety_gates"), False),
        ("future-missing-speed-evidence", ("future_public_winner_policy", "requires_frozen_fair_performance_oracle"), False),
        ("future-entrypoint-silently-fixed", ("future_public_winner_policy", "fixes_public_entrypoint_in_this_chunk"), True),
    )
    for name, location, value in mutations:
        def attack(place=location, replacement=value):
            poisoned = clone(contract)
            poisoned[place[0]][place[1]] = replacement  # type: ignore[index]
            return validate_contract(poisoned)
        reject("reject-" + name, attack)
    for owner_name in ("public_entrypoint", "project_configuration",
                       "historical_zig_adapter", "current_overview_inputs",
                       "current_overview_summary", "pinned_stdlib_re_source",
                       "actual_signature_reference_receipt"):
        def attack(name=owner_name):
            poisoned = clone(contract)
            poisoned["owners"][name]["sha256"] = "0" * 64  # type: ignore[index]
            return validate_contract(poisoned)
        reject("reject-tampered-owner-" + owner_name, attack)
    reject("reject-stale-overview", lambda:
           validate_contract({**contract, "current_overview_version": OVERVIEW_VERSION - 1}))
    reject("reject-truncated-matrix", lambda:
           validate_contract({**contract, "case_matrix": contract["case_matrix"][:-1]}))  # type: ignore[index]

    future = {
        "winner_selected": True, "winner_family": "rust",
        "distinct_correctness_qualified_families": ["rust", "c_vm", "zig"],
        "winner_original_case_count": ORIGINAL_CASES,
        "winner_original_suite_count": ORIGINAL_SUITES,
        "winner_original_private_waiver_count": PRIVATE_WAIVERS,
        "winner_original_status": "PASS",
        "winner_signature_case_count": ADDITIONAL_SIGNATURE_CASES,
        "winner_signature_status": "PASS",
        "actual_public_entrypoint_status": "PASS",
        "actual_installed_public_import": "PASS",
        "actual_public_module_version": "2.2.1",
        "exact_public_wildcard_exports": True,
        "direct_debug_attribute": True,
        "direct_scanner_attribute": True,
        "runtime_no_delegation": "PASS",
        "native_safety_status": "PASS",
        "frozen_fair_performance_status": "PASS",
        "statistical_winner_status": "PASS",
        "winner_native_provenance_status": "PASS",
        "stdlib_fallback_used": False,
        "external_regex_engine_used": False,
        "cross_candidate_engine_used": False,
    }
    accept("future-synthetic-fully-qualified-winner", lambda: validate_future_winner(future) or True)
    for key, wrong in (
        ("winner_selected", False),
        ("winner_family", "fortran"),
        ("distinct_correctness_qualified_families", ["rust", "zig"]),
        ("winner_original_case_count", ORIGINAL_CASES + ADDITIONAL_SIGNATURE_CASES),
        ("winner_original_suite_count", ORIGINAL_SUITES - 1),
        ("winner_original_private_waiver_count", PRIVATE_WAIVERS + 1),
        ("winner_original_status", "FAIL"),
        ("winner_signature_case_count", ADDITIONAL_SIGNATURE_CASES - 1),
        ("winner_signature_status", "NOT MEASURED"),
        ("actual_public_entrypoint_status", "FAIL"),
        ("actual_installed_public_import", "NOT MEASURED"),
        ("actual_public_module_version", "MISSING"),
        ("exact_public_wildcard_exports", False),
        ("direct_debug_attribute", False),
        ("direct_scanner_attribute", False),
        ("runtime_no_delegation", "NOT ESTABLISHED"),
        ("native_safety_status", "NOT MEASURED"),
        ("frozen_fair_performance_status", "NOT MEASURED"),
        ("statistical_winner_status", "NOT MEASURED"),
        ("winner_native_provenance_status", "NOT ESTABLISHED"),
        ("stdlib_fallback_used", True),
        ("external_regex_engine_used", True),
        ("cross_candidate_engine_used", True),
    ):
        reject("reject-future-winner-" + key,
               lambda name=key, value=wrong:
               validate_future_winner({**future, name: value}))

    no_matcher_imports()
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS",
        "control_count": len(passed),
        "unique_control_count": len(set(passed)),
        "control_names_sha256": digest(canonical_text(passed).encode("ascii")),
        "physical_audit_hook_installed": _AUDIT_INSTALLED,
        "physically_blocked_effect_attempts": sum(_BLOCKED_AUDIT_EVENTS.values()),
        "physically_blocked_effect_event_counts": dict(_BLOCKED_AUDIT_EVENTS),
        "source_freeze_status": "PASS",
        "observed_public_entrypoint_status": "FAIL",
        "observed_public_entrypoint_classification": "UNQUALIFIED_ZIG_PROTOTYPE",
        "actual_candidate_imports": 0,
        "actual_public_entrypoint_imports": 0,
        "actual_stdlib_regex_imports": 0,
        "actual_native_libraries_loaded": 0,
        "actual_archives_opened": 0,
        "actual_archives_decompressed": 0,
        "actual_subprocesses_started": 0,
        "actual_network_requests": 0,
        "actual_clock_samples": 0,
        "actual_holdout_cases_read": 0,
        "workspace_files_written": 0,
        "original_case_count": ORIGINAL_CASES,
        "original_suite_count": ORIGINAL_SUITES,
        "original_private_waiver_count": PRIVATE_WAIVERS,
        "additional_signature_case_count": ADDITIONAL_SIGNATURE_CASES,
        "additional_cases_included_in_original_denominator": False,
        "qualified_candidate_count": 0,
        "winner_selected": False,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
    }


def verify_context(contract: dict[str, object]) -> dict[str, object]:
    no_matcher_imports()
    require(_AUDIT_INSTALLED, "the source-only physical audit wall was not installed")
    records = {}
    for name, path, expected, size in OWNERS:
        records[name] = read_exact(path, expected, size)
        no_matcher_imports()
    validate_original(decode_json(records["original_p0_inventory"]))
    validate_signatures(decode_json(records["additional_signature_inventory"]),
                        decode_json(records["actual_signature_reference_receipt"]))
    validate_inventory(decode_json(records["first_party_source_inventory"]))
    repaired_rust = validate_repaired_rust_v7(
        decode_json(records["repaired_rust_v7_contract"]))
    validate_overview(decode_json(records["current_overview_inputs"]),
                      inputs=True, repaired_rust=repaired_rust)
    validate_overview(decode_json(records["current_overview_summary"]),
                      inputs=False, repaired_rust=repaired_rust)
    project = parse_simple_project(records["project_configuration"])
    require(project["project"].get("name") == "rebar-experiment" and
            project["project"].get("version") == "0.0.0" and
            project["project"].get("requires-python") == ">=3.14,<3.15" and
            project["project"].get("dependencies") == [] and
            project["tool.uv"].get("package") is False,
            "the actual unconfigured public project or package policy changed")
    surface = analyze_surface(records["public_entrypoint"],
                              records["historical_zig_adapter"],
                              records["pinned_stdlib_re_source"])
    require(type(surface["public_entrypoint_source_docstring"]) is str and
            surface["public_entrypoint_source_docstring"].startswith("Measured,"),
            "the actual misleading measured public-entrypoint claim changed")
    no_matcher_imports()
    return {
        "schema": SCHEMA + "-frozen-context",
        "status": "PASS",
        "source_freeze_status": "PASS",
        "observed_public_entrypoint_status": "FAIL",
        "observed_public_entrypoint_classification": "UNQUALIFIED_ZIG_PROTOTYPE",
        "public_entrypoint_qualified": False,
        "overview_version": OVERVIEW_VERSION,
        "authenticated_exact_owner_count": len(OWNERS),
        "physical_audit_hook_installed": _AUDIT_INSTALLED,
        "physically_blocked_effect_attempts": sum(_BLOCKED_AUDIT_EVENTS.values()),
        "case_matrix_count": len(CASE_ROWS),
        "case_matrix_sha256": MATRIX_SHA256,
        "surface": surface,
        "uv_package_enabled": False,
        "installed_public_artifact": "NOT MEASURED",
        "original_case_count": ORIGINAL_CASES,
        "original_suite_count": ORIGINAL_SUITES,
        "original_private_waiver_count": PRIVATE_WAIVERS,
        "additional_signature_case_count": ADDITIONAL_SIGNATURE_CASES,
        "additional_cases_included_in_original_denominator": False,
        "additional_signature_reference_status": "PASS",
        "additional_signature_candidate_status": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
        "actual_rust_controller_status": "FAIL",
        "actual_rust_candidate_workers": 0,
        "actual_rust_source_build_archive_read_count": 1,
        "actual_rust_controller_ledger_omits_source_build_archive_effect": True,
        "actual_repaired_rust_v7_source_freeze_status":
            "SOURCE FROZEN; CORRECTED RUST V13 CANDIDATE NOT RUN",
        "actual_repaired_rust_v7_source_sha256":
            "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104",
        "actual_repaired_rust_v7_candidate_workers": 0,
        "actual_repaired_rust_v7_candidate_matching": "NOT RUN",
        "actual_zig_campaign_status": "FAIL",
        "actual_zig_semantic_mismatch_count": 1764,
        "authenticated_evidence_owner_lower_bound": 166,
        "authenticated_history_reference_lower_bound": 171,
        "actual_candidate_imports": 0,
        "actual_public_entrypoint_imports": 0,
        "actual_stdlib_regex_imports": 0,
        "actual_native_libraries_loaded": 0,
        "actual_archives_opened": 0,
        "actual_archives_decompressed": 0,
        "actual_subprocesses_started": 0,
        "actual_network_requests": 0,
        "actual_clock_samples": 0,
        "actual_holdout_cases_read": 0,
        "workspace_files_written": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def parse_arguments(argv: list[str]) -> tuple[str, dict[str, str]]:
    flags = {"--source-sha256": "source", "--protocol-sha256": "protocol",
             "--contract-sha256": "contract"}
    result: dict[str, str] = {}
    mode = ""
    index = 0
    while index < len(argv):
        item = argv[index]
        if item in ("--self-test", "--verify-frozen-context"):
            require(not mode, "exactly one source-only mode is mandatory")
            mode = item
            index += 1
            continue
        require(item in flags and index + 1 < len(argv),
                "unexpected public-entrypoint argument or missing exact owner hash")
        key = flags[item]
        require(key not in result, "duplicate exact owner hash: " + key)
        value = argv[index + 1]
        require(len(value) == 64 and all(char in "0123456789abcdef" for char in value),
                "an exact owner SHA-256 must be 64 lowercase hexadecimal digits")
        result[key] = value
        index += 2
    require(bool(mode) and set(result) == {"source", "protocol", "contract"},
            "one source-only mode and all three independent owner pins are mandatory")
    return mode, result


def main(argv: list[str]) -> int:
    no_matcher_imports()
    require(tuple(sys.version_info[:3]) == (3, 14, 6) and sys.executable == PYTHON,
            "run the source freeze only with the exact pinned stable CPython")
    install_source_only_audit_wall()
    mode, pins = parse_arguments(argv)
    read_self(SOURCE, pins["source"])
    read_self(PROTOCOL, pins["protocol"])
    raw = read_self(CONTRACT, pins["contract"])
    contract = validate_contract(decode_json(raw))
    result = (run_self_test(contract) if mode == "--self-test"
              else verify_context(contract))
    no_matcher_imports()
    sys.stdout.write(canonical_text(result) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except FreezeError as error:
        sys.stderr.write("public-entrypoint source freeze failed closed: " + str(error) + "\n")
        raise SystemExit(1)
