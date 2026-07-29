#!/usr/bin/env python3
"""Verify the owned Rust two-capture findall source without executing it."""

from __future__ import annotations

import sys

if "re" in sys.modules or "_sre" in sys.modules or "regex" in sys.modules:
    raise SystemExit("source-only captured-findall verification imported a regex engine")

import builtins
import hashlib
import os
import stat

ROOT = "/home/dev-user/src/rebar"
PINNED_CPYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
SOURCE_PATH = "tools/verify_owned_rust_captured_findall_source_v1.py"
PROTOCOL_PATH = "oracle/phase2/RUST-CAPTURED-FINDALL-ONE-PASS-V1.md"
CONTRACT_PATH = "oracle/phase2/rust-captured-findall-one-pass-v1.json"
PROTOCOL_SHA256 = (
    "ffcaeec11704a81a2fd5ca25d7fc746c8a66fab033bb1f108f0e6c19445079fe"
)
EXPANDED_SOURCE_PATH = "tools/verify_expanded_sealed_holdout_v1.py"
EXPANDED_SOURCE_SHA256 = (
    "3dd9abcbd7a87486186ee8da804de595e65d79020a3fe33413d0157dde4f3309"
)
EXPANDED_PROTOCOL_PATH = "oracle/phase3/EXPANDED-SEALED-HOLDOUT-V1.md"
EXPANDED_PROTOCOL_SHA256 = (
    "818f1636d87ae721912f04a3fc8294ac04a59dff4a272319aa29a393f52a4fd4"
)
EXPANDED_CONTRACT_PATH = "oracle/phase3/expanded-sealed-holdout-v1.json"
EXPANDED_CONTRACT_SHA256 = (
    "676aac4f48c9404f5253c89b692efde5c425170f8d9f152b4f85b3e2a5225a76"
)
ORIGINAL_BRIDGE_PATH = (
    "candidates/rust/variants/buffer_shape_pickle_v2/py_bridge.c"
)
ORIGINAL_BRIDGE_SHA256 = (
    "afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740"
)
PREDECESSOR_PATH = (
    "candidates/rust/variants/buffer_shape_pickle_findall_v1/py_bridge.c"
)
PREDECESSOR_SHA256 = (
    "b707e924a23980385b0c5b0306daecd55bbb03d6f2511437f0532b6d39b2a112"
)
VARIANT_PATH = (
    "candidates/rust/variants/buffer_shape_pickle_findall_captures_v1/"
    "py_bridge.c"
)
VARIANT_SHA256 = (
    "a0b9e7fbfc92da4c3b97608cf156fb0ca2f94fb5358901b7b6baa0a819fffc8a"
)
BUILD_RECEIPT_PATH = (
    "oracle/phase2/evidence/"
    "native-source-build-v19-rust-phase2-v19-rust-buffer-shape-root-provenance"
    "-publication-receipt.json"
)
BUILD_RECEIPT_SHA256 = (
    "27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc"
)
ROOT_RECEIPT_PATH = (
    "oracle/phase2/evidence/"
    "native-source-build-v19-rust-phase2-v19-rust-buffer-shape-root-provenance"
    "-root-provenance-receipt.json"
)
ROOT_RECEIPT_SHA256 = (
    "de13207235055665c605cce1b88a8f2127f291b84a5954119a033c7f4e9a3c99"
)
LITERAL_SOURCE_PATH = "tools/verify_owned_rust_literal_findall_source_v1.py"
LITERAL_SOURCE_SHA256 = (
    "21fb0878e344ead0bba49f932120a35a897ca44cfd7710287861ebc6415c555e"
)
LITERAL_PROTOCOL_PATH = "oracle/phase2/RUST-LITERAL-FINDALL-ONE-PASS-V1.md"
LITERAL_PROTOCOL_SHA256 = (
    "842d51127db54a26d0dd9f874f38834f122f7888ea71c6f3fe77b8911bbd65d6"
)
LITERAL_CONTRACT_PATH = "oracle/phase2/rust-literal-findall-one-pass-v1.json"
LITERAL_CONTRACT_SHA256 = (
    "a2226d823610a578aeb65e9a51a2a33517348b6c51130ad89db840cc50833164"
)
PILOT_PATH = (
    "experiments/rust_public_practice_v1/"
    "rust-memoryview-native-exporter-fix-public-practice.json"
)
PILOT_SHA256 = (
    "76015482b066b613ec6290b6d0fb28bd5ea76df21a9930e64f4ea2628211c9b2"
)
SCHEMA = "rebar-phase2-owned-rust-captured-findall-one-pass-v1-source-freeze"
MAX_OWNER_BYTES = 8 * 1024 * 1024
MAX_JSON_DEPTH = 48
MAX_JSON_CONTAINER_ITEMS = 16384

FUNCTION_START = (
    b"static int rust_append_batched_findall(PyObject *result, "
    b"const RustSubject *subject, size_t groups, "
    b"const intptr_t *begins, const intptr_t *ends) {\n"
)
FUNCTION_FOLLOW = b"\nstatic PyObject *rust_batched_findall("
ORIGINAL_FUNCTION = b"""static int rust_append_batched_findall(PyObject *result, const RustSubject *subject, size_t groups, const intptr_t *begins, const intptr_t *ends) {
    size_t first = groups == 0 ? 0 : 1;
    size_t values = groups <= 1 ? 1 : groups;
    if (values == 1) {
        return rust_list_append_owned(result, rust_findall_item(subject, begins[first], ends[first]));
    }
    if (values > (size_t)PY_SSIZE_T_MAX) {
        PyErr_NoMemory();
        return -1;
    }
    PyObject *row = PyTuple_New((Py_ssize_t)values);
    if (row == NULL) return -1;
    for (size_t index = 0; index < values; index++) {
        size_t group = first + index;
        PyObject *piece = rust_findall_item(subject, begins[group], ends[group]);
        if (piece == NULL) {
            Py_DECREF(row);
            return -1;
        }
        PyTuple_SET_ITEM(row, (Py_ssize_t)index, piece);
    }
    return rust_list_append_owned(result, row);
}
"""
CAPTURE_FUNCTION = b"""static int rust_append_batched_findall(PyObject *result, const RustSubject *subject, size_t groups, const intptr_t *begins, const intptr_t *ends) {
    if (groups == 2) {
        PyObject *row = PyTuple_New(2);
        if (row == NULL) return -1;
        PyObject *first = rust_findall_item(subject, begins[1], ends[1]);
        if (first == NULL) {
            Py_DECREF(row);
            return -1;
        }
        PyTuple_SET_ITEM(row, 0, first);
        PyObject *second = rust_findall_item(subject, begins[2], ends[2]);
        if (second == NULL) {
            Py_DECREF(row);
            return -1;
        }
        PyTuple_SET_ITEM(row, 1, second);
        return rust_list_append_owned(result, row);
    }
    size_t first = groups == 0 ? 0 : 1;
    size_t values = groups <= 1 ? 1 : groups;
    if (values == 1) {
        return rust_list_append_owned(result, rust_findall_item(subject, begins[first], ends[first]));
    }
    if (values > (size_t)PY_SSIZE_T_MAX) {
        PyErr_NoMemory();
        return -1;
    }
    PyObject *row = PyTuple_New((Py_ssize_t)values);
    if (row == NULL) return -1;
    for (size_t index = 0; index < values; index++) {
        size_t group = first + index;
        PyObject *piece = rust_findall_item(subject, begins[group], ends[group]);
        if (piece == NULL) {
            Py_DECREF(row);
            return -1;
        }
        PyTuple_SET_ITEM(row, (Py_ssize_t)index, piece);
    }
    return rust_list_append_owned(result, row);
}
"""

FIXED_OWNERS = (
    (
        "GOAL.md",
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
        3756,
    ),
    (
        "oracle/phase1/P0-COMPLETENESS-V4.md",
        "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
        4261,
    ),
    (
        "oracle/phase1/p0-completeness-v4.json",
        "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
        34875,
    ),
    (
        "oracle/phase1/P0-DIFFERENTIAL-FUZZ-REFERENCE-V3.md",
        "8d67e3f4162945a454d8945abac3880a9c42620a04c2332ac2adc52f013305b6",
        3929,
    ),
    (
        "oracle/phase1/p0-differential-fuzz-reference-v3.json",
        "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff",
        5288,
    ),
    (
        "tools/reproduce_owned_rust_buffer_shape_source_build_v19.py",
        "650b33a10d253e09d48a423d12c8a1bb8180af4c4e96222aa13e72c75427bb5c",
        88532,
    ),
    (
        "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V19.md",
        "4cdc322b2a516b28bf771440202efaca77074f7c8cd31c25692dc6ffc81797b5",
        5808,
    ),
    (
        "oracle/phase2/rust-buffer-shape-source-build-v19.json",
        "78e31d32cd17e100613ea98cecec4051ca2f6563b0d3b198c66f69501171ac46",
        14975,
    ),
    (BUILD_RECEIPT_PATH, BUILD_RECEIPT_SHA256, 3486),
    (ROOT_RECEIPT_PATH, ROOT_RECEIPT_SHA256, 4367),
    (ORIGINAL_BRIDGE_PATH, ORIGINAL_BRIDGE_SHA256, 179961),
    (PREDECESSOR_PATH, PREDECESSOR_SHA256, 178950),
    (LITERAL_SOURCE_PATH, LITERAL_SOURCE_SHA256, 33883),
    (LITERAL_PROTOCOL_PATH, LITERAL_PROTOCOL_SHA256, 4515),
    (LITERAL_CONTRACT_PATH, LITERAL_CONTRACT_SHA256, 3167),
    (EXPANDED_SOURCE_PATH, EXPANDED_SOURCE_SHA256, 27311),
    (EXPANDED_PROTOCOL_PATH, EXPANDED_PROTOCOL_SHA256, 13237),
    (EXPANDED_CONTRACT_PATH, EXPANDED_CONTRACT_SHA256, 6628),
    (PILOT_PATH, PILOT_SHA256, 6229575),
    (VARIANT_PATH, VARIANT_SHA256, 179520),
)

ALLOWED_OWNER_PATHS = frozenset(
    os.path.join(ROOT, path)
    for path in (
        SOURCE_PATH,
        PROTOCOL_PATH,
        CONTRACT_PATH,
        *(entry[0] for entry in FIXED_OWNERS),
    )
)
FORBIDDEN_IMPORTS = frozenset(
    (
        "re",
        "_sre",
        "regex",
        "ctypes",
        "subprocess",
        "multiprocessing",
        "socket",
        "time",
        "gzip",
        "bz2",
        "lzma",
        "tarfile",
        "zipfile",
    )
)
FORBIDDEN_AUDIT_EVENTS = frozenset(
    (
        "subprocess.Popen",
        "os.system",
        "os.posix_spawn",
        "os.posix_spawnp",
        "os.spawn",
        "os.fork",
        "os.forkpty",
        "os.remove",
        "os.rmdir",
        "os.mkdir",
        "os.rename",
        "os.chmod",
        "os.chown",
        "os.truncate",
        "os.link",
        "os.symlink",
        "os.putenv",
        "os.unsetenv",
        "ctypes.dlopen",
        "ctypes.dlsym",
        "socket.__new__",
        "socket.connect",
        "socket.bind",
        "socket.sendto",
        "time.sleep",
    )
)


class FreezeError(Exception):
    """The cumulative, source-only first-party experiment was not proved."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise FreezeError(message)


def valid_sha256(value: str, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        label + " must be exactly 64 lowercase hexadecimal characters",
    )
    return value


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "source-owner hashing requires exact bytes")
    return hashlib.sha256(raw).hexdigest()


def quote(value: str) -> str:
    require(type(value) is str, "canonical JSON requires an exact string")
    escaped = {
        '"': '\\"',
        "\\": "\\\\",
        "\b": "\\b",
        "\f": "\\f",
        "\n": "\\n",
        "\r": "\\r",
        "\t": "\\t",
    }
    pieces = ['"']
    for character in value:
        point = ord(character)
        require(
            not 0xD800 <= point <= 0xDFFF,
            "canonical JSON cannot contain an unpaired surrogate",
        )
        if character in escaped:
            pieces.append(escaped[character])
        elif point < 32:
            pieces.append("\\u" + format(point, "04x"))
        else:
            pieces.append(character)
    pieces.append('"')
    return "".join(pieces)


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= 32, "canonical source evidence is nested too deeply")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is int:
        return str(value)
    if type(value) is str:
        return quote(value)
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(
            all(type(key) is str for key in value),
            "canonical source evidence requires exact string keys",
        )
        return "{" + ",".join(
            quote(key) + ":" + canonical(value[key], depth + 1)
            for key in sorted(value)
        ) + "}"
    raise FreezeError("canonical source evidence has an unsupported value")


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    if event in FORBIDDEN_AUDIT_EVENTS:
        raise FreezeError("source-only verification denied " + event)
    if event == "import":
        name = arguments[0] if arguments else None
        if type(name) is str and name.partition(".")[0] in FORBIDDEN_IMPORTS:
            raise FreezeError("source-only verification denied import " + name)
    if event != "open":
        return
    require(len(arguments) >= 3, "source-only verification denied an unknown open")
    path, mode, flags = arguments[:3]
    require(type(path) is str, "source-only verification denied descriptor access")
    require(
        path in ALLOWED_OWNER_PATHS,
        "source-only verification denied an unlisted source or hidden file",
    )
    require(
        mode in ("r", "rb"),
        "source-only verification denied a writable open mode",
    )
    require(
        type(flags) is int
        and (flags & os.O_ACCMODE) == os.O_RDONLY
        and not (flags & (os.O_CREAT | os.O_TRUNC | os.O_APPEND)),
        "source-only verification denied writable open flags",
    )


def read_owner(path: str, expected_hash: str, expected_size: int | None) -> bytes:
    valid_sha256(expected_hash, path + " SHA-256")
    absolute = os.path.join(ROOT, path)
    require(
        absolute in ALLOWED_OWNER_PATHS,
        "the requested owner is outside the strict source-only read wall",
    )
    before = os.stat(absolute, follow_symlinks=False)
    require(stat.S_ISREG(before.st_mode), path + " is not a real regular source")
    require(
        0 < before.st_size <= MAX_OWNER_BYTES,
        path + " exceeds the exact source-only size bound",
    )
    if expected_size is not None:
        require(before.st_size == expected_size, path + " has the wrong exact size")
    with builtins.open(absolute, "rb") as handle:
        opened = os.fstat(handle.fileno())
        require(
            (opened.st_dev, opened.st_ino, opened.st_size)
            == (before.st_dev, before.st_ino, before.st_size),
            path + " changed between source stat and source open",
        )
        raw = handle.read(before.st_size + 1)
        require(
            len(raw) == before.st_size,
            path + " changed or exceeded its bounded source-only read",
        )
        after = os.fstat(handle.fileno())
        require(
            (after.st_dev, after.st_ino, after.st_size)
            == (opened.st_dev, opened.st_ino, opened.st_size),
            path + " changed during its source-only read",
        )
    require(sha256(raw) == expected_hash, path + " SHA-256 mismatch")
    return raw


class BoundedJSON:
    """Decode only authenticated, bounded public JSON without importing re."""

    __slots__ = ("text", "position", "length")

    def __init__(self, raw: bytes) -> None:
        require(type(raw) is bytes, "public JSON must be exact authenticated bytes")
        require(
            0 < len(raw) <= MAX_OWNER_BYTES,
            "public JSON exceeds its source-only bounded size",
        )
        try:
            text = raw.decode("utf-8", "strict")
        except UnicodeDecodeError as error:
            raise FreezeError("public JSON is not strict UTF-8") from error
        self.text = text
        self.position = 0
        self.length = len(text)

    def whitespace(self) -> None:
        while (
            self.position < self.length
            and self.text[self.position] in " \t\r\n"
        ):
            self.position += 1

    def string(self) -> str:
        require(
            self.position < self.length
            and self.text[self.position] == '"',
            "public JSON requires a quoted string",
        )
        self.position += 1
        pieces: list[str] = []
        while self.position < self.length:
            character = self.text[self.position]
            self.position += 1
            if character == '"':
                return "".join(pieces)
            require(ord(character) >= 32, "public JSON contains a control character")
            if character != "\\":
                require(
                    not 0xD800 <= ord(character) <= 0xDFFF,
                    "public JSON contains an unpaired surrogate",
                )
                pieces.append(character)
                continue
            require(self.position < self.length, "public JSON has a truncated escape")
            escaped = self.text[self.position]
            self.position += 1
            mapping = {
                '"': '"',
                "\\": "\\",
                "/": "/",
                "b": "\b",
                "f": "\f",
                "n": "\n",
                "r": "\r",
                "t": "\t",
            }
            if escaped in mapping:
                pieces.append(mapping[escaped])
                continue
            require(escaped == "u", "public JSON contains an invalid escape")
            require(
                self.position + 4 <= self.length,
                "public JSON contains a truncated Unicode escape",
            )
            digits = self.text[self.position : self.position + 4]
            require(
                all(digit in "0123456789abcdefABCDEF" for digit in digits),
                "public JSON contains a nonhex Unicode escape",
            )
            self.position += 4
            point = int(digits, 16)
            if 0xD800 <= point <= 0xDBFF:
                require(
                    self.text[self.position : self.position + 2] == "\\u",
                    "public JSON has an unpaired leading surrogate",
                )
                self.position += 2
                require(
                    self.position + 4 <= self.length,
                    "public JSON has a truncated trailing surrogate",
                )
                trailing_digits = self.text[
                    self.position : self.position + 4
                ]
                require(
                    all(
                        digit in "0123456789abcdefABCDEF"
                        for digit in trailing_digits
                    ),
                    "public JSON has a nonhex trailing surrogate",
                )
                trailing = int(trailing_digits, 16)
                require(
                    0xDC00 <= trailing <= 0xDFFF,
                    "public JSON has an invalid trailing surrogate",
                )
                self.position += 4
                point = 0x10000 + ((point - 0xD800) << 10) + (trailing - 0xDC00)
            else:
                require(
                    not 0xDC00 <= point <= 0xDFFF,
                    "public JSON has an unpaired trailing surrogate",
                )
            pieces.append(chr(point))
        raise FreezeError("public JSON has an unterminated string")

    def number(self) -> int | float:
        start = self.position
        if self.position < self.length and self.text[self.position] == "-":
            self.position += 1
        require(self.position < self.length, "public JSON has a truncated number")
        if self.text[self.position] == "0":
            self.position += 1
            require(
                self.position >= self.length
                or self.text[self.position] not in "0123456789",
                "public JSON has a leading-zero number",
            )
        else:
            require(
                self.text[self.position] in "123456789",
                "public JSON has an invalid number",
            )
            while (
                self.position < self.length
                and self.text[self.position] in "0123456789"
            ):
                self.position += 1
        fractional = False
        if self.position < self.length and self.text[self.position] == ".":
            fractional = True
            self.position += 1
            require(
                self.position < self.length
                and self.text[self.position] in "0123456789",
                "public JSON has a truncated fractional number",
            )
            while (
                self.position < self.length
                and self.text[self.position] in "0123456789"
            ):
                self.position += 1
        if self.position < self.length and self.text[self.position] in "eE":
            fractional = True
            self.position += 1
            if (
                self.position < self.length
                and self.text[self.position] in "+-"
            ):
                self.position += 1
            require(
                self.position < self.length
                and self.text[self.position] in "0123456789",
                "public JSON has a truncated numeric exponent",
            )
            while (
                self.position < self.length
                and self.text[self.position] in "0123456789"
            ):
                self.position += 1
        token = self.text[start : self.position]
        try:
            number = float(token) if fractional else int(token)
        except (ValueError, OverflowError) as error:
            raise FreezeError("public JSON has an invalid bounded number") from error
        if fractional:
            require(
                number == number
                and number != float("inf")
                and number != float("-inf"),
                "public JSON has a nonfinite number",
            )
        return number

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "public JSON exceeds its bounded depth")
        self.whitespace()
        require(self.position < self.length, "public JSON ends before its value")
        character = self.text[self.position]
        if character == '"':
            return self.string()
        if character == "{":
            self.position += 1
            result: dict[str, object] = {}
            self.whitespace()
            if self.position < self.length and self.text[self.position] == "}":
                self.position += 1
                return result
            while True:
                self.whitespace()
                key = self.string()
                require(key not in result, "public JSON contains a duplicate key")
                self.whitespace()
                require(
                    self.position < self.length
                    and self.text[self.position] == ":",
                    "public JSON object is missing a value separator",
                )
                self.position += 1
                result[key] = self.value(depth + 1)
                require(
                    len(result) <= MAX_JSON_CONTAINER_ITEMS,
                    "public JSON object exceeds its bounded key count",
                )
                self.whitespace()
                require(
                    self.position < self.length,
                    "public JSON object is unterminated",
                )
                separator = self.text[self.position]
                self.position += 1
                if separator == "}":
                    return result
                require(separator == ",", "public JSON object has an invalid separator")
        if character == "[":
            self.position += 1
            result_list: list[object] = []
            self.whitespace()
            if self.position < self.length and self.text[self.position] == "]":
                self.position += 1
                return result_list
            while True:
                result_list.append(self.value(depth + 1))
                require(
                    len(result_list) <= MAX_JSON_CONTAINER_ITEMS,
                    "public JSON array exceeds its bounded item count",
                )
                self.whitespace()
                require(
                    self.position < self.length,
                    "public JSON array is unterminated",
                )
                separator = self.text[self.position]
                self.position += 1
                if separator == "]":
                    return result_list
                require(separator == ",", "public JSON array has an invalid separator")
        for token, value in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(token, self.position):
                self.position += len(token)
                return value
        return self.number()

    def document(self) -> object:
        value = self.value()
        self.whitespace()
        require(
            self.position == self.length,
            "public JSON contains trailing data",
        )
        return value


def public_array(raw: bytes, key: str, next_key: str) -> list[object]:
    prefix = (quote(key) + ":[").encode("utf-8")
    suffix = ("]," + quote(next_key) + ":").encode("utf-8")
    require(raw.count(prefix) == 1, "the exact public " + key + " is ambiguous")
    require(raw.count(suffix) == 1, "the exact public " + key + " boundary is ambiguous")
    begin = raw.index(prefix) + len(prefix) - 1
    finish = raw.find(suffix, begin)
    require(finish >= begin, "the public " + key + " boundary is missing")
    decoded = BoundedJSON(raw[begin : finish + 1]).document()
    require(type(decoded) is list, "the public " + key + " is not an exact array")
    return decoded


def capture_group_names(pattern: str) -> tuple[int, tuple[str, ...]]:
    require(type(pattern) is str, "a captured pattern must be an exact string")
    captures = 0
    names: list[str] = []
    index = 0
    in_class = False
    while index < len(pattern):
        character = pattern[index]
        if character == "\\":
            index += 2
            continue
        if in_class:
            if character == "]":
                in_class = False
            index += 1
            continue
        if character == "[":
            in_class = True
            index += 1
            continue
        if character == "(":
            if pattern.startswith("(?P<", index):
                close = pattern.find(">", index + 4)
                require(close >= index + 4, "a named captured group is unterminated")
                name = pattern[index + 4 : close]
                require(name != "", "a named captured group cannot be empty")
                captures += 1
                names.append(name)
            elif not pattern.startswith("(?", index):
                captures += 1
        index += 1
    require(not in_class, "a captured pattern contains an unterminated class")
    return captures, tuple(names)


def verify_public_practice(raw: bytes) -> dict[str, int]:
    require(
        b'"schema":"rebar-rust-fresh-public-practice-v1-actual-public-practice-report"'
        in raw,
        "the authenticated historical report has the wrong public schema",
    )
    require(
        b'"case_count":864' in raw
        and b'"hidden_cases_read":0' in raw
        and b'"benchmark_files_read":0' in raw
        and b'"final_winner_selected":false' in raw,
        "the historical public evidence does not prove its unopened boundary",
    )
    matrix = public_array(raw, "matrix", "matrix_sha256")
    reference = public_array(
        raw,
        "correctness_reference_records",
        "correctness_reference_records_sha256",
    )
    require(len(matrix) == 864, "the exact public matrix denominator is not 864")
    require(
        len(reference) == 864,
        "the exact public CPython outcome denominator is not 864",
    )
    outcomes: dict[str, dict[str, object]] = {}
    for record in reference:
        require(type(record) is dict, "a public reference record is not an object")
        case = record.get("case")
        outcome = record.get("outcome")
        require(
            type(case) is str and type(outcome) is dict,
            "a public reference record does not own its case and outcome",
        )
        require(case not in outcomes, "the public CPython reference repeats a case")
        outcomes[case] = outcome

    selected = 0
    module_cases = 0
    pattern_cases = 0
    named_two = 0
    materialized = 0
    empty = 0
    selected_ids: set[str] = set()
    for row in matrix:
        require(type(row) is dict, "a public practice row is not an object")
        operation = row.get("operation")
        if operation not in ("module.findall", "pattern.findall"):
            continue
        selected += 1
        if operation == "module.findall":
            module_cases += 1
        else:
            pattern_cases += 1
        case = row.get("case")
        require(
            type(case) is str and case in outcomes and case not in selected_ids,
            "a captured public case has no unique CPython outcome",
        )
        selected_ids.add(case)
        pattern = row.get("pattern")
        require(type(pattern) is dict, "a captured public pattern is not typed")
        pattern_type = pattern.get("type")
        if pattern_type == "str":
            pattern_text = pattern.get("value")
            require(type(pattern_text) is str, "the public text pattern is not exact")
        elif pattern_type == "bytes":
            pattern_hex = pattern.get("hex")
            require(
                type(pattern_hex) is str and len(pattern_hex) % 2 == 0,
                "the public bytes pattern does not have canonical hex",
            )
            try:
                pattern_bytes = bytes.fromhex(pattern_hex)
                pattern_text = pattern_bytes.decode("ascii", "strict")
            except (UnicodeDecodeError, ValueError) as error:
                raise FreezeError(
                    "the public bytes capture pattern is not strict ASCII hex"
                ) from error
            require(
                pattern_bytes.hex() == pattern_hex,
                "the public bytes capture pattern is not canonical hex",
            )
        else:
            raise FreezeError("the public capture pattern has an unsupported type")

        captures, names = capture_group_names(pattern_text)
        require(
            captures == 2 and names == ("word", "number"),
            "the public findall case does not have exactly two named groups",
        )
        named_two += 1
        outcome = outcomes[case]
        require(
            outcome.get("status") == "return",
            "a captured public CPython reference did not return",
        )
        value = outcome.get("value")
        require(
            type(value) is dict and value.get("kind") == "list",
            "the captured public reference did not return a list",
        )
        items = value.get("items")
        require(type(items) is list, "the captured public result is not a list")
        if len(items) == 0:
            empty += 1
            continue
        materialized += 1
        for item in items:
            require(
                type(item) is dict and item.get("kind") == "tuple",
                "a public captured result is not a tuple",
            )
            pieces = item.get("items")
            require(
                type(pieces) is list and len(pieces) == 2,
                "a public captured result does not have exactly two values",
            )
            if pattern_type == "str":
                require(
                    all(type(piece) is str for piece in pieces),
                    "a public text capture changed its Python type",
                )
            else:
                for piece in pieces:
                    require(
                        type(piece) is dict
                        and piece.get("kind") == "bytes"
                        and type(piece.get("hex")) is str,
                        "a public bytes capture changed its Python type",
                    )
                    encoded = piece["hex"]
                    try:
                        exact_bytes = bytes.fromhex(encoded)
                    except ValueError as error:
                        raise FreezeError(
                            "a public bytes capture has invalid hex"
                        ) from error
                    require(
                        exact_bytes.hex() == encoded,
                        "a public bytes capture is not canonical hex",
                    )
    require(selected == 48, "the public captured-findall denominator changed")
    require(
        module_cases == 24 and pattern_cases == 24,
        "public module and compiled-pattern cases are not balanced",
    )
    require(named_two == 48, "the public two-named-group coverage changed")
    require(materialized == 44, "the public materialized capture count changed")
    require(empty == 4, "the public empty captured-list count changed")
    return {
        "public_cases": 864,
        "findall_cases": selected,
        "module_findall_cases": module_cases,
        "pattern_findall_cases": pattern_cases,
        "named_two_capture_cases": named_two,
        "materialized_capture_cases": materialized,
        "empty_capture_cases": empty,
    }


def verify_expanded_sealed_proposal(
    contract: bytes,
    protocol: bytes,
) -> dict[str, object]:
    proposal = BoundedJSON(contract).document()
    require(
        type(proposal) is dict,
        "the authenticated expanded sealed proposal is not an exact public object",
    )
    required = {
        "schema": "rebar-expanded-sealed-holdout-pre-phase3-proposal-v1",
        "case_count": 14155776,
        "proposal_status": "PRE-PHASE-3 PROPOSAL",
        "case_status": "NOT GENERATED; NOT OPENED",
        "final_protocol_status": "NOT FROZEN",
        "generator_status": "NOT FROZEN",
        "secret_status": "NOT GENERATED",
        "timing_status": "NOT RUN; NOT MEASURED",
        "memory_status": "NOT RUN; NOT MEASURED",
        "winner_status": "NOT SELECTED",
        "qualified_independent_family_count": 0,
        "minimum_qualified_independent_family_count": 3,
        "runtime_independence_status": "NOT ESTABLISHED",
        "preserved_previous_proposal_case_count": 4194304,
        "original_p0_case_count": 31237,
        "separate_differential_case_count": 8244,
    }
    for key, expected in required.items():
        require(
            proposal.get(key) == expected,
            "the expanded public-only proposal changed its frozen claim: " + key,
        )
    owners = proposal.get("required_public_owners")
    require(
        type(owners) is list and len(owners) == 9,
        "the expanded public-only proposal changed its authenticated owner count",
    )
    require(
        b"14,155,776" in protocol
        and b"NOT FROZEN" in protocol
        and b"NOT GENERATED" in protocol
        and b"NOT OPENED" in protocol,
        "the exact expanded public protocol does not preserve its sealed boundary",
    )
    return {
        "case_count": 14155776,
        "historical_previous_proposal_case_count": 4194304,
        "qualified_independent_family_count": 0,
        "minimum_qualified_independent_family_count": 3,
        "final_protocol_status": "NOT FROZEN",
        "case_status": "NOT GENERATED; NOT OPENED",
        "runtime_independence_status": "NOT ESTABLISHED",
    }


def verify_one_function(predecessor: bytes, variant: bytes) -> None:
    require(type(predecessor) is bytes, "the literal predecessor must be exact bytes")
    require(type(variant) is bytes, "the capture variant must be exact bytes")
    require(
        predecessor.count(FUNCTION_START) == 1,
        "the literal predecessor must own exactly one batched capture function",
    )
    require(
        variant.count(FUNCTION_START) == 1,
        "the cumulative variant must own exactly one batched capture function",
    )
    old_start = predecessor.index(FUNCTION_START)
    old_end = predecessor.find(FUNCTION_FOLLOW, old_start)
    new_start = variant.index(FUNCTION_START)
    new_end = variant.find(FUNCTION_FOLLOW, new_start)
    require(
        old_end >= 0 and new_end >= 0,
        "the exact batched capture-function boundary is missing",
    )
    require(
        predecessor[old_start:old_end] == ORIGINAL_FUNCTION,
        "the authenticated generic captured-findall function changed",
    )
    require(
        variant[new_start:new_end] == CAPTURE_FUNCTION,
        "the exact owned two-capture fast path is not authenticated",
    )
    require(
        predecessor[:old_start] == variant[:new_start],
        "source bytes before captured findall were changed",
    )
    require(
        predecessor[old_end:] == variant[new_end:],
        "source bytes after captured findall were changed",
    )
    marker = b"    size_t first = groups == 0 ? 0 : 1;\n"
    require(
        CAPTURE_FUNCTION.count(marker) == 1,
        "the unchanged zero-, one-, and general-group fallback is missing",
    )
    fast = CAPTURE_FUNCTION.split(marker, 1)[0]
    require(
        fast.count(b"if (groups == 2)") == 1,
        "the fast path must apply to exactly two capturing groups",
    )
    require(
        fast.count(b"PyTuple_New(2)") == 1,
        "the fast path must allocate exactly one two-item tuple",
    )
    require(
        fast.count(b"rust_findall_item(") == 2
        and b"rust_findall_item(subject, begins[1], ends[1])" in fast
        and b"rust_findall_item(subject, begins[2], ends[2])" in fast,
        "both existing, ordered, type-preserving captured-value helpers are required",
    )
    require(
        fast.count(b"PyTuple_SET_ITEM(") == 2
        and b"PyTuple_SET_ITEM(row, 0, first)" in fast
        and b"PyTuple_SET_ITEM(row, 1, second)" in fast,
        "both owned tuple slots must preserve capture order",
    )
    require(
        fast.count(b"Py_DECREF(row)") == 2,
        "both captured-value failures must release the tuple exactly once",
    )
    require(
        fast.count(b"return rust_list_append_owned(result, row);") == 1,
        "the existing amortized, ownership-safe list append is required",
    )
    require(
        b"for (" not in fast
        and b"PyList_SET_ITEM(" not in fast
        and b"PyList_Append(" not in fast
        and b"PyImport_" not in fast,
        "the direct capture branch cannot add iteration, unsafe ownership, or imports",
    )


def contract_model(
    source_hash: str,
    source_bytes: int,
    protocol_hash: str,
    protocol_bytes: int,
) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "version": 1,
        "status": "SOURCE FROZEN; NOT BUILT; NOT RUN; NOT BENCHMARKED",
        "family": "rust",
        "source": {
            "path": SOURCE_PATH,
            "sha256": source_hash,
            "bytes": source_bytes,
        },
        "protocol": {
            "path": PROTOCOL_PATH,
            "sha256": protocol_hash,
            "bytes": protocol_bytes,
        },
        "historical_native_predecessor": {
            "path": ORIGINAL_BRIDGE_PATH,
            "sha256": ORIGINAL_BRIDGE_SHA256,
            "bytes": 179961,
            "lines": 4774,
            "native_build": {
                "label": "phase2-v19-rust-buffer-shape-root-provenance",
                "actual_compiler_process_count": 28,
                "actual_source_phase_count": 2,
                "publication_receipt": {
                    "path": BUILD_RECEIPT_PATH,
                    "sha256": BUILD_RECEIPT_SHA256,
                    "bytes": 3486,
                    "status": "PASS",
                },
                "root_provenance_receipt": {
                    "path": ROOT_RECEIPT_PATH,
                    "sha256": ROOT_RECEIPT_SHA256,
                    "bytes": 4367,
                    "status": "PASS",
                },
            },
        },
        "immediate_literal_predecessor": {
            "path": PREDECESSOR_PATH,
            "sha256": PREDECESSOR_SHA256,
            "bytes": 178950,
            "lines": 4757,
            "source_status": "SOURCE FROZEN; NOT BUILT; NOT RUN; NOT BENCHMARKED",
            "verifier": {
                "path": LITERAL_SOURCE_PATH,
                "sha256": LITERAL_SOURCE_SHA256,
                "bytes": 33883,
            },
            "protocol": {
                "path": LITERAL_PROTOCOL_PATH,
                "sha256": LITERAL_PROTOCOL_SHA256,
                "bytes": 4515,
            },
            "contract": {
                "path": LITERAL_CONTRACT_PATH,
                "sha256": LITERAL_CONTRACT_SHA256,
                "bytes": 3167,
            },
        },
        "candidate_variant": {
            "path": VARIANT_PATH,
            "sha256": VARIANT_SHA256,
            "bytes": 179520,
            "lines": 4774,
            "changed_function": "rust_append_batched_findall",
            "changed_function_count": 1,
            "specialized_capture_count": 2,
            "all_other_immediate_predecessor_bytes_unchanged": True,
            "inherits_literal_single_pass": True,
            "complete_independently_owned_source": True,
            "native_build": "NOT RUN",
            "matching": "NOT RUN",
            "qualified": False,
        },
        "frozen_python_reference": {
            "cpython": "3.14.6",
            "original_cases": 31237,
            "original_groups": 13,
            "named_private_waivers": 13,
            "additional_differential_property_cases": 8244,
            "reference_status": "PASS",
            "candidate_status": "NOT RUN",
        },
        "historical_public_practice": {
            "path": PILOT_PATH,
            "sha256": PILOT_SHA256,
            "bytes": 6229575,
            "case_count": 864,
            "findall_case_count": 48,
            "module_findall_case_count": 24,
            "pattern_findall_case_count": 24,
            "two_named_capture_case_count": 48,
            "materialized_capture_case_count": 44,
            "empty_capture_case_count": 4,
            "new_variant_exercised": False,
            "new_variant_timed": False,
            "effect_on_historical_pilot": "NOT MEASURED",
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
        },
        "expanded_sealed_holdout_proposal": {
            "case_count": 14155776,
            "historical_previous_proposal_case_count": 4194304,
            "proposal_status": "PRE-PHASE-3 PROPOSAL",
            "final_protocol_status": "NOT FROZEN",
            "generator_status": "NOT FROZEN",
            "case_status": "NOT GENERATED; NOT OPENED",
            "qualified_independent_family_count": 0,
            "minimum_qualified_independent_family_count": 3,
            "runtime_independence_status": "NOT ESTABLISHED",
            "controller": {
                "path": EXPANDED_SOURCE_PATH,
                "sha256": EXPANDED_SOURCE_SHA256,
                "bytes": 27311,
            },
            "protocol": {
                "path": EXPANDED_PROTOCOL_PATH,
                "sha256": EXPANDED_PROTOCOL_SHA256,
                "bytes": 13237,
            },
            "contract": {
                "path": EXPANDED_CONTRACT_PATH,
                "sha256": EXPANDED_CONTRACT_SHA256,
                "bytes": 6628,
            },
        },
        "required_future_gates": {
            "fresh_native_build_and_provenance": "NOT RUN",
            "complete_original_correctness": "NOT RUN",
            "complete_additional_correctness": "NOT RUN",
            "public_api_and_buffer_correctness": "NOT RUN",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "separately_frozen_public_capture_practice": "NOT FROZEN",
        },
        "phase_boundary": {
            "archive_opens": 0,
            "candidate_processes_started": 0,
            "candidate_workers_started": 0,
            "compiler_processes_started": 0,
            "native_libraries_loaded": 0,
            "matching_operations": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "hidden_cases_read": 0,
            "holdout_case_count": 14155776,
            "historical_previous_holdout_proposal_case_count": 4194304,
            "holdout": "NOT FROZEN; NOT GENERATED; NOT OPENED",
            "correctness": "NOT MEASURED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "qualified_candidate_count": 0,
            "winner_selected": False,
            "external_regex_dependencies": 0,
            "stdlib_regex_delegation": False,
        },
    }


def expect_failure(callback: object, label: str) -> None:
    require(callable(callback), label + " is not a callable hostile control")
    try:
        callback()
    except FreezeError:
        return
    raise FreezeError("hostile source-only control was accepted: " + label)


def self_test() -> tuple[int, int]:
    positive = 0
    hostile = 0

    for index in range(192):
        prefix = ("/* synthetic capture predecessor " + str(index) + " */\n").encode(
            "ascii"
        )
        suffix = FUNCTION_FOLLOW + (
            "const void *handle) { /* bounded successor "
            + str(index)
            + " */ }\n"
        ).encode("ascii")
        original = prefix + ORIGINAL_FUNCTION + suffix
        captured = prefix + CAPTURE_FUNCTION + suffix
        verify_one_function(original, captured)
        positive += 1

    for index in range(32):
        prefix = ("/* adversarial capture case " + str(index) + " */\n").encode(
            "ascii"
        )
        suffix = FUNCTION_FOLLOW + (
            "const void *handle) { /* exact successor "
            + str(index)
            + " */ }\n"
        ).encode("ascii")
        original = prefix + ORIGINAL_FUNCTION + suffix
        captured = prefix + CAPTURE_FUNCTION + suffix
        failures = (
            (original, b"X" + captured, "modified cumulative prefix"),
            (original, captured + b"X", "modified cumulative suffix"),
            (
                original.replace(
                    b"rust_append_batched_findall(",
                    b"external_append_batched_findall(",
                    1,
                ),
                captured,
                "missing authenticated generic predecessor",
            ),
            (
                original,
                captured.replace(
                    b"rust_append_batched_findall(",
                    b"external_append_batched_findall(",
                    1,
                ),
                "missing owned cumulative capture function",
            ),
            (
                original,
                captured.replace(b"if (groups == 2)", b"if (groups <= 2)", 1),
                "incorrect zero- and one-group specialization",
            ),
            (
                original,
                captured.replace(b"PyTuple_New(2)", b"PyTuple_New(1)", 1),
                "incorrect captured tuple length",
            ),
            (
                original,
                captured.replace(b"begins[1], ends[1]", b"begins[2], ends[2]", 1),
                "reordered first capture",
            ),
            (
                original,
                captured.replace(b"begins[2], ends[2]", b"begins[1], ends[1]", 1),
                "reordered second capture",
            ),
            (
                original,
                captured.replace(b"PyTuple_SET_ITEM(row, 0, first)", b"/* leak */", 1),
                "unowned first captured tuple slot",
            ),
            (
                original,
                captured.replace(
                    b"PyTuple_SET_ITEM(row, 1, second)",
                    b"PyTuple_SET_ITEM(row, 0, second)",
                    1,
                ),
                "overwritten captured tuple slot",
            ),
            (
                original,
                captured.replace(b"Py_DECREF(row);", b"/* leaked tuple */", 1),
                "unbalanced captured tuple lifetime",
            ),
            (
                original,
                captured.replace(
                    b"return rust_list_append_owned(result, row);",
                    b"return external_regex(result, row);",
                    1,
                ),
                "delegated captured matcher",
            ),
            (
                original,
                captured.replace(
                    b"size_t values = groups <= 1 ? 1 : groups;",
                    b"size_t values = groups;",
                    1,
                ),
                "modified generic group semantics",
            ),
            (
                original,
                captured.replace(
                    FUNCTION_FOLLOW,
                    b"\nstatic PyObject *external_batched_findall(",
                    1,
                ),
                "missing authenticated exact function boundary",
            ),
        )
        for bad_original, bad_captured, label in failures:
            expect_failure(
                lambda left=bad_original, right=bad_captured: verify_one_function(
                    left,
                    right,
                ),
                label,
            )
            hostile += 1

    exact_allowed = os.path.join(ROOT, PREDECESSOR_PATH)
    for index in range(64):
        audit_wall("open", (exact_allowed, "rb", os.O_RDONLY))
        positive += 1
        denied = (
            ("open", ("/tmp/holdout-capture-" + str(index), "rb", os.O_RDONLY)),
            ("open", (exact_allowed, "wb", os.O_WRONLY | os.O_CREAT)),
            ("open", (exact_allowed, "r+", os.O_RDWR)),
            ("open", (index, "rb", os.O_RDONLY)),
            ("subprocess.Popen", ("candidate",)),
            ("ctypes.dlopen", ("candidate.so",)),
            ("socket.connect", ("example.invalid",)),
            ("import", ("re", None, None, None, None)),
            ("import", ("_sre", None, None, None, None)),
            ("import", ("regex.external", None, None, None, None)),
            ("import", ("time", None, None, None, None)),
            ("os.system", ("benchmark",)),
            ("os.remove", ("candidate",)),
            ("os.rename", ("old", "new")),
            ("time.sleep", (1,)),
        )
        for event, arguments in denied:
            expect_failure(
                lambda current=event, values=arguments: audit_wall(current, values),
                "denied source-only event " + event,
            )
            hostile += 1

    decoded = BoundedJSON(
        b'{"a":[true,false,null,-2,3.5e1],"z":"capture\\n\\u0041"}'
    ).document()
    require(
        decoded
        == {"a": [True, False, None, -2, 35.0], "z": "capture\nA"},
        "the bounded first-party public JSON decoder changed",
    )
    positive += 1
    for invalid in (
        b"",
        b"{",
        b"[]x",
        b'{"x":1,"x":2}',
        b"[01]",
        b"[1.]",
        b"[1e]",
        b'["\\q"]',
        b'["\\uZZZZ"]',
        b'["\\uD800"]',
        b'["\\uDC00"]',
        b'[true false]',
    ):
        expect_failure(
            lambda raw=invalid: BoundedJSON(raw).document(),
            "invalid bounded public JSON",
        )
        hostile += 1

    names = capture_group_names(
        r"(?<=ID:)(?P<word>[A-Z]+)(?P<number>\d+)"
    )
    require(
        names == (2, ("word", "number")),
        "lookbehind and the two named captures are not counted exactly",
    )
    positive += 1
    require(
        capture_group_names(r"\((?P<word>[()]+)(?P<number>\d*)\)")
        == (2, ("word", "number")),
        "escaped parentheses or a character class changed capture counting",
    )
    positive += 1

    for invalid in ("", "a", "A" * 64, "g" * 64, "0" * 63, "0" * 65):
        expect_failure(
            lambda value=invalid: valid_sha256(value, "hostile source pin"),
            "invalid exact SHA-256 pin",
        )
        hostile += 1

    require(
        canonical({"z": [True, False, None, 2], "a": "line\n"})
        == '{"a":"line\\n","z":[true,false,null,2]}',
        "first-party canonical source evidence changed",
    )
    positive += 1
    require(positive >= 250, "insufficient independent positive source controls")
    require(hostile >= 1400, "insufficient independent hostile source controls")
    return positive, hostile


def parse_arguments(arguments: list[str]) -> tuple[str, str, str, str]:
    require(
        len(arguments) == 7,
        "one source-only mode and exactly three caller-pinned hashes are required",
    )
    mode = arguments[0]
    require(
        mode in ("--self-test", "--verify-frozen-context"),
        "only the two immutable source-only modes are permitted",
    )
    pins: dict[str, str] = {}
    for index in range(1, len(arguments), 2):
        label = arguments[index]
        require(
            label
            in (
                "--source-sha256",
                "--protocol-sha256",
                "--contract-sha256",
            ),
            "the source-only verifier received an unknown unsafe option",
        )
        require(label not in pins, "a source-only hash option was repeated")
        pins[label] = valid_sha256(arguments[index + 1], label)
    require(
        len(pins) == 3,
        "the source, protocol, and contract must all be caller-pinned",
    )
    return (
        mode,
        pins["--source-sha256"],
        pins["--protocol-sha256"],
        pins["--contract-sha256"],
    )


def verify_pinned_interpreter() -> None:
    require(
        os.path.realpath(sys.executable) == PINNED_CPYTHON,
        "source verification requires the exact pinned CPython executable",
    )
    require(
        tuple(sys.version_info[:3]) == (3, 14, 6),
        "source verification requires exactly CPython 3.14.6",
    )
    require(
        sys.implementation.name == "cpython"
        and sys.implementation.cache_tag == "cpython-314",
        "source verification requires the pinned CPython cache implementation",
    )
    require(
        sys.flags.isolated == 1,
        "source verification requires isolated Python execution (-I)",
    )
    require(
        sys.dont_write_bytecode is True,
        "source verification requires bytecode writes disabled (-B)",
    )


def verify_frozen_context(
    source_pin: str,
    protocol_pin: str,
    contract_pin: str,
) -> dict[str, object]:
    require(
        protocol_pin == PROTOCOL_SHA256,
        "the exact cumulative captured-findall protocol was not caller-pinned",
    )
    source = read_owner(SOURCE_PATH, source_pin, None)
    protocol = read_owner(PROTOCOL_PATH, protocol_pin, 5953)
    contract = read_owner(CONTRACT_PATH, contract_pin, None)
    authenticated: dict[str, bytes] = {}
    for path, expected_hash, expected_size in FIXED_OWNERS:
        authenticated[path] = read_owner(path, expected_hash, expected_size)

    verify_one_function(
        authenticated[PREDECESSOR_PATH],
        authenticated[VARIANT_PATH],
    )
    build_receipt = authenticated[BUILD_RECEIPT_PATH]
    root_receipt = authenticated[ROOT_RECEIPT_PATH]
    require(
        b'"build_status":"PASS"' in build_receipt
        and b'"actual_compiler_process_count":28' in build_receipt
        and ORIGINAL_BRIDGE_SHA256.encode("ascii") in build_receipt,
        "the historical V19 native receipt does not authenticate the original bridge",
    )
    require(
        b'"status":"PASS"' in root_receipt
        and b'"actual_source_phase_count":2' in root_receipt
        and BUILD_RECEIPT_SHA256.encode("ascii") in root_receipt,
        "the historical V19 source-root receipt does not authenticate its build",
    )
    literal_contract = authenticated[LITERAL_CONTRACT_PATH]
    require(
        b'"changed_function":"rust_pattern_literal_findall_direct"'
        in literal_contract
        and PREDECESSOR_SHA256.encode("ascii") in literal_contract
        and LITERAL_SOURCE_SHA256.encode("ascii") in literal_contract
        and LITERAL_PROTOCOL_SHA256.encode("ascii") in literal_contract,
        "the immediate one-pass literal predecessor is not independently frozen",
    )
    coverage = verify_public_practice(authenticated[PILOT_PATH])
    expanded_proposal = verify_expanded_sealed_proposal(
        authenticated[EXPANDED_CONTRACT_PATH],
        authenticated[EXPANDED_PROTOCOL_PATH],
    )
    expected = (
        canonical(
            contract_model(
                source_pin,
                len(source),
                protocol_pin,
                len(protocol),
            )
        ).encode("utf-8")
        + b"\n"
    )
    require(
        contract == expected,
        "captured-findall evidence is not the exact canonical source-only contract",
    )
    return {
        "status": "PASS",
        "schema": SCHEMA,
        "source_only": True,
        "authenticated_plaintext_owners": len(FIXED_OWNERS) + 3,
        "historical_native_predecessor_sha256": ORIGINAL_BRIDGE_SHA256,
        "immediate_literal_predecessor_sha256": PREDECESSOR_SHA256,
        "candidate_variant_sha256": VARIANT_SHA256,
        "changed_function_count": 1,
        "specialized_capture_count": 2,
        "original_reference_cases": 31237,
        "additional_reference_cases": 8244,
        "public_case_count": coverage["public_cases"],
        "public_findall_case_count": coverage["findall_cases"],
        "public_module_findall_case_count": coverage["module_findall_cases"],
        "public_pattern_findall_case_count": coverage["pattern_findall_cases"],
        "public_named_two_capture_case_count": coverage["named_two_capture_cases"],
        "public_materialized_capture_case_count": coverage[
            "materialized_capture_cases"
        ],
        "public_empty_capture_case_count": coverage["empty_capture_cases"],
        "expanded_holdout_proposed_case_count": expanded_proposal["case_count"],
        "historical_previous_holdout_proposal_case_count": expanded_proposal[
            "historical_previous_proposal_case_count"
        ],
        "minimum_qualified_independent_family_count": expanded_proposal[
            "minimum_qualified_independent_family_count"
        ],
        "expanded_holdout_protocol": expanded_proposal["final_protocol_status"],
        "expanded_holdout_cases": expanded_proposal["case_status"],
        "native_build": "NOT RUN",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "native_libraries_loaded": 0,
        "candidate_processes_started": 0,
        "compiler_processes_started": 0,
        "archive_opens": 0,
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }


def main() -> int:
    verify_pinned_interpreter()
    require(
        "re" not in sys.modules
        and "_sre" not in sys.modules
        and "regex" not in sys.modules,
        "a forbidden matching engine loaded before the source-only audit",
    )
    mode, source_pin, protocol_pin, contract_pin = parse_arguments(sys.argv[1:])
    sys.addaudithook(audit_wall)
    result = verify_frozen_context(source_pin, protocol_pin, contract_pin)
    result["mode"] = mode[2:]
    if mode == "--self-test":
        positive, hostile = self_test()
        result["positive_controls"] = positive
        result["hostile_controls"] = hostile
    require(
        "re" not in sys.modules
        and "_sre" not in sys.modules
        and "regex" not in sys.modules,
        "a forbidden matching engine loaded during the source-only audit",
    )
    sys.stdout.write(canonical(result) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FreezeError as error:
        sys.stderr.write("source-only Rust captured-findall verification failed: ")
        sys.stderr.write(str(error))
        sys.stderr.write("\n")
        raise SystemExit(1) from error
