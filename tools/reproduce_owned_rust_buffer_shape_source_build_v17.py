#!/usr/bin/env python3
"""Freeze an offline, first-party Rust build of the observed V2 lifetime fix."""

from __future__ import annotations

import sys

if "re" in sys.modules or "_sre" in sys.modules:
    raise SystemExit("the V17 source freeze cannot load a regular-expression engine")

import ast
import builtins
import hashlib
import os
import stat


ROOT = "/home/dev-user/src/rebar"
SCHEMA = "rebar-phase2-owned-rust-buffer-shape-source-build-v17"
VERSION = 17
FAMILY = "rust"
SOURCE_PATH = "tools/reproduce_owned_rust_buffer_shape_source_build_v17.py"
PROTOCOL_PATH = "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V17.md"
CONTRACT_PATH = "oracle/phase2/rust-buffer-shape-source-build-v17.json"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
ROOT_PREFIX = "rebar-phase2-native-build-v9-rust-"
BUILD_LABEL = "phase2-v17-rust-buffer-shape-pickle-lifetime"
MAX_OWNER_BYTES = 4 * 1024 * 1024
MAX_JSON_DEPTH = 64
MAX_AST_NODES = 75_000
GRAPH_VERSION = 59
EVIDENCE_FLOOR = 201
HISTORY_FLOOR = 206
PHASES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "rustc_version", "cargo_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "engine_symbols", "bridge_dynamic", "bridge_symbols", "engine_sections",
    "engine_notes", "bridge_sections", "bridge_notes",
)
ENGINE_NAME = "_rust_engine.so"
BRIDGE_NAME = "_rust_bridge.cpython-314-x86_64-linux-gnu.so"
BRIDGE_PATH = "candidates/rust/py_bridge.c"
PUBLIC_PATH = "candidates/rust_candidate.py"
V1_BRIDGE_SHA256 = "00271ad5fff71e2f2e30cda6b446a61d0c300cb91eec2091b8ada17662d9a335"
V1_BRIDGE_BYTES = 181_004
V2_BRIDGE_SHA256 = "afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740"
V2_BRIDGE_BYTES = 179_961
OUTSIDE_FUNCTION_SHA256 = "1a4e1713e2ea2dd6a42d56baac4e66907392b1971b94a1f5007fecab5c25830b"
CORRECTED_ADAPTER_SHA256 = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
CORRECTED_ADAPTER_BYTES = 31_934
CORRECTED_REFERENCE_SHA256 = "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2"
CORRECTED_CACHE_SHA256 = "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad"
FALSIFIED_REFERENCE_SHA256 = "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21"
FALSIFIED_RECEIPT_SHA256 = "6a8ce4334d0b605483e0f78a909f620a8bcdd0e5ad8cdb4fae4960fc237132fd"
PHASE_ONE_V2_SOURCE_PATH = "tools/verify_owned_p0_completeness_v2.py"
PHASE_ONE_V2_PROTOCOL_PATH = "oracle/phase1/P0-COMPLETENESS-V2.md"
PHASE_ONE_V2_CONTRACT_PATH = "oracle/phase1/p0-completeness-v2.json"

# Every row is an already pushed, plaintext, bounded, independently owned file.
# A compressed report, native library, temporary root, or holdout is never a row.
OWNERS = (
    ("goal", "GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756, 2064, 31364044),
    ("p0", "oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632, 2064, 524385),
    ("corrected_reference_source", "tools/verify_owned_public_type_reference_context_v1.py", "bff95e5630e875e1b389eeb4555810a112728dbed5f2cc7c43e1ec83d0817ddc", 102474, 2064, 431631),
    ("corrected_reference_protocol", "oracle/phase1/P0-PUBLIC-TYPE-REFERENCE-CONTEXT-V1.md", "11ca046ccd5087b2212b8ad8496896fb1fd60e408a193e038bae4b19fb360018", 10691, 2064, 524740),
    ("corrected_reference_contract", "oracle/phase1/p0-public-type-reference-context-v1.json", "dd0ea680e9a73345f7c323e278ba7ccebd5a3bb26cb606a9bdbecf7c3fb8298b", 13965, 2064, 524741),
    ("corrected_reference_receipt", "oracle/phase1/evidence/public-type-reference-context-v1-cpython-3-14-6-candidate-context-p0-publication-receipt.json", "ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966", 2509, 2064, 524769),
    ("public_context_falsification", "oracle/phase1/evidence/public-type-candidate-context-falsification-v1.json", "319f0f75aaaea16fd1f41d814785d67060c57060852893349366cc3b482c4670", 3892, 2064, 524739),
    ("v4_producer", "tools/run_owned_six_family_original_p0_producer_v4.py", "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8", 230782, 2064, 431710),
    ("v4_producer_protocol", "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md", "e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5", 5981, 2064, 524782),
    ("v4_producer_contract", "oracle/phase2/six-family-p0-producer-v4.json", "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5", 30867, 2064, 524783),
    ("cargo_lock", "candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167, 2064, 428098),
    ("cargo_manifest", "candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225, 2064, 428094),
    ("original_bridge", "candidates/rust/py_bridge.c", "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676, 2064, 419054),
    ("rust_engine", "candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967, 2064, 428096),
    ("rust_newline", "candidates/rust/src/newline.rs", "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416, 2064, 427958),
    ("rust_search", "candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773, 2064, 429682),
    ("rust_stack", "candidates/rust/src/stack.rs", "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269, 2064, 428151),
    ("rust_unicode", "candidates/rust/src/unicode_tables.rs", "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989, 2064, 428152),
    ("original_adapter", "candidates/rust_candidate.py", "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151, 2064, 428100),
    ("adapter_repair", "tools/apply_owned_rust_public_contract_source_repair_v3.py", "5e57da2379e736bba75eacdb57f84710dc144c0d4088d5827b3139a6b71d8859", 92060, 2064, 431033),
    ("adapter_protocol", "oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V3.md", "2aeb81e55548b46011c75815465d2bc2fa461d57ba7b990fc7a7b87d2d687a34", 6405, 2064, 524675),
    ("adapter_contract", "oracle/phase2/rust-public-contract-source-repair-v3.json", "82bce0066181dd16f3de52d88f31e930f25706b5ff3da2ba18b10c8b31b4f6a1", 14817, 2064, 524678),
    ("low_level_v9", "tools/reproduce_owned_native_source_build_v9.py", "c4a4b85b92ef0d600528732c9e0acb8f8303b7b2fbfc320e84c9b9e2d384219f", 81124, 2064, 429976),
    ("low_level_v9_protocol", "oracle/phase2/NATIVE-SOURCE-BUILD-V9.md", "18494d4b778a3c958b07903996e8a1b13f4466e08b2c9e72cd5d711957dbcecc", 4960, 2064, 524423),
    ("low_level_v9_contract", "oracle/phase2/native-source-build-v9.json", "6a4aee7f0c639b2b338d1497c35a69d35939841cf55b0dbe38abe404cea404da", 9134, 2064, 524424),
    ("low_level_v7", "tools/reproduce_owned_native_source_build_v7.py", "20d8e43a9c70f585049f81d38f9085661b50e4bf754320a6abcd95d566d854a7", 300624, 2064, 431752),
    ("low_level_v7_protocol", "oracle/phase2/NATIVE-SOURCE-BUILD-V7.md", "a7a5ce16bb7a98dfd6e0e4f9f3777912687aa09259cc1669c5e0932da2287313", 8063, 2064, 524508),
    ("low_level_v7_contract", "oracle/phase2/native-source-build-v7.json", "cfc774cfce1a0c4298f01e298d7ffaa982300375ba117e316bff2ebbf0be7819", 28924, 2064, 524509),
    ("v16_builder", "tools/reproduce_owned_rust_buffer_shape_source_build_v16.py", "bcea8f23fc5e52af1e8062145d75ef1a6ed835cea3ac113a155cc8ebf3116a8a", 134640, 2064, 431980),
    ("v16_protocol", "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V16.md", "315f0a24e64b50804565f86c6ca4187024c4a1db5a23ab2f57c8805ed37f51f5", 6497, 2064, 524984),
    ("v16_contract", "oracle/phase2/rust-buffer-shape-source-build-v16.json", "4f82f88da3329c6bacac2092af19d915d379f90101dcd9840366274355cc92b7", 18260, 2064, 524985),
    ("v16_build_receipt", "oracle/phase2/evidence/native-source-build-v16-rust-phase2-v16-rust-buffer-shape-pickle-publication-receipt.json", "c893812a1796cce056de5e2feff2289df34ff816158685730205996549e338cb", 3459, 2064, 524994),
    ("v2_repair", "tools/apply_owned_rust_buffer_shape_pickle_source_repair_v2.py", "7f22016b20da990b0ddb85114bf76a187918612ef68aae97c94d81518d3eb322", 47145, 2064, 432135),
    ("v2_protocol", "oracle/phase2/RUST-BUFFER-SHAPE-PICKLE-SOURCE-REPAIR-V2.md", "79ad2b88f7542c791cdf48956d432e6d9f2dad00a485056972eea1664e41ff66", 4060, 2064, 525058),
    ("v2_contract", "oracle/phase2/rust-buffer-shape-pickle-source-repair-v2.json", "0d5fe2ca190df54366b73850ce316a9d27f77c527bd5ddd8d5420d62dcb33be0", 7486, 2064, 525059),
    ("v1_variant", "candidates/rust/variants/buffer_shape_pickle_v1/py_bridge.c", "00271ad5fff71e2f2e30cda6b446a61d0c300cb91eec2091b8ada17662d9a335", 181004, 2064, 524972),
    ("v2_variant", "candidates/rust/variants/buffer_shape_pickle_v2/py_bridge.c", "afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740", 179961, 2064, 525057),
    ("v10_receipt", "oracle/phase2/evidence/repaired-rust-original-campaign-v10-rust-phase2-v16-rust-buffer-shape-pickle-original-p0-v10-failures-publication-receipt.json", "8735e5351f62de2a77369eb8401e225cebd31434b09f07db40e79550ba7cc7d2", 6708, 2064, 525044),
    ("v10_forensics", "oracle/phase2/evidence/repaired-rust-original-campaign-v10-rust-phase2-v16-rust-buffer-shape-pickle-original-p0-v10-failures-forensic-summary.json", "6e04771a48b4a460ad58ac9795ef91a697a33fa0aeae4671c9b3c9b35e4820cd", 24701, 2064, 525045),
    ("graph_renderer", "tools/render_candidate_current_overview_v59.py", "a5716931d30ab5f4dcb2bf5efa0bdb3fd24f7bad48f6ed77b5dce3714e547677", 65821, 2064, 432137),
    ("graph_inputs", "docs/evidence/candidate-current-overview-v59.inputs.json", "044d243432850b6eaa9f0d54b7bd8f77967dd0c234bfb64af9d37e27888e9fa3", 902467, 2064, 432138),
    ("graph_summary", "docs/evidence/candidate-current-overview-v59.json", "73dd4701a9613795aeafa60c1b76a98900a5020dbe31a78fdc1922b534a4c0b0", 2457553, 2064, 432139),
    ("graph_chart", "docs/evidence/candidate-current-overview-v59.svg", "9b3d0942adcd9bc29d13d895ba5e7a0acc2626520f1392a1c686ce341de43abe", 14612, 2064, 432141),
)
OWNER_BY_NAME = {row[0]: row for row in OWNERS}
RUST_SOURCE_NAMES = (
    "cargo_lock", "cargo_manifest", "original_bridge", "rust_engine",
    "rust_newline", "rust_search", "rust_stack", "rust_unicode",
    "original_adapter",
)
FORBIDDEN_ENGINE_BYTES = (
    b"import re\n", b"from re import", b"import _sre", b"from _sre",
    b"regex.compile", b"pcre", b"oniguruma", b"hyperscan",
    b"candidates.vm_candidate", b"candidates.zig_candidate",
    b"candidates.cpp_candidate", b"candidates.go_candidate",
    b"candidates.fortran_candidate",
)


class GateError(Exception):
    """Reject an altered owner, synthetic success, or forbidden real effect."""


def require(value: object, message: str) -> None:
    if value is not True:
        raise GateError(message)


def digest(value: bytes) -> str:
    require(type(value) is bytes, "hash only exact first-party bytes")
    return hashlib.sha256(value).hexdigest()


def checked_hash(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "an exact lowercase SHA-256 is required: " + label)
    return value


def quote(value: str) -> str:
    require(type(value) is str, "canonical JSON requires string keys")
    escapes = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
               "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    result = ['"']
    for char in value:
        point = ord(char)
        require(not 0xD800 <= point <= 0xDFFF,
                "canonical JSON rejects an unpaired surrogate")
        if char in escapes:
            result.append(escapes[char])
        elif point < 32:
            result.append("\\u" + format(point, "04x"))
        elif point > 126:
            if point <= 0xFFFF:
                result.append("\\u" + format(point, "04x"))
            else:
                adjusted = point - 0x10000
                result.append("\\u" + format(0xD800 + (adjusted >> 10), "04x")
                              + "\\u" + format(0xDC00 + (adjusted & 1023), "04x"))
        else:
            result.append(char)
    result.append('"')
    return "".join(result)


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= MAX_JSON_DEPTH, "canonical JSON exceeds the depth limit")
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
                "nonfinite JSON numbers are forbidden")
        return repr(value)
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value),
                "canonical JSON object keys must be strings")
        return "{" + ",".join(quote(key) + ":" + canonical(value[key], depth + 1)
                               for key in sorted(value)) + "}"
    raise GateError("unsupported canonical JSON value")


class StrictJSON:
    """Bounded duplicate-rejecting JSON without json, re, or _sre."""

    def __init__(self, raw: bytes):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_OWNER_BYTES,
                "JSON owner exceeds its exact bounded allowance")
        try:
            self.text = raw.decode("utf-8", "strict")
        except UnicodeError as error:
            raise GateError("JSON owner is not strict UTF-8") from error
        self.index = 0

    def whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def string(self) -> str:
        require(self.text[self.index:self.index + 1] == '"', "JSON string required")
        self.index += 1
        result: list[str] = []
        escaped = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
                   "n": "\n", "r": "\r", "t": "\t"}
        while self.index < len(self.text):
            char = self.text[self.index]
            self.index += 1
            if char == '"':
                return "".join(result)
            if char != "\\":
                require(ord(char) >= 32 and not 0xD800 <= ord(char) <= 0xDFFF,
                        "invalid JSON string character")
                result.append(char)
                continue
            require(self.index < len(self.text), "incomplete JSON escape")
            char = self.text[self.index]
            self.index += 1
            if char != "u":
                require(char in escaped, "invalid JSON escape")
                result.append(escaped[char])
                continue
            digits = self.text[self.index:self.index + 4]
            require(len(digits) == 4
                    and all(item in "0123456789abcdefABCDEF" for item in digits),
                    "invalid JSON Unicode escape")
            self.index += 4
            point = int(digits, 16)
            if 0xD800 <= point <= 0xDBFF:
                require(self.text[self.index:self.index + 2] == "\\u",
                        "unpaired high surrogate")
                lower = self.text[self.index + 2:self.index + 6]
                require(len(lower) == 4
                        and all(item in "0123456789abcdefABCDEF" for item in lower),
                        "invalid low surrogate")
                low = int(lower, 16)
                require(0xDC00 <= low <= 0xDFFF, "unpaired high surrogate")
                self.index += 6
                result.append(chr(0x10000 + ((point - 0xD800) << 10)
                                  + low - 0xDC00))
            else:
                require(not 0xDC00 <= point <= 0xDFFF, "unpaired low surrogate")
                result.append(chr(point))
        raise GateError("unterminated JSON string")

    def number(self) -> int | float:
        first = self.index
        if self.text[self.index:self.index + 1] == "-":
            self.index += 1
        require(self.index < len(self.text), "incomplete JSON number")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index == len(self.text)
                    or self.text[self.index] not in "0123456789",
                    "JSON number has a leading zero")
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
        token = self.text[first:self.index]
        require(len(token) <= 128, "JSON number exceeds its bounded allowance")
        if not floating:
            return int(token)
        value = float(token)
        require(value == value and abs(value) != float("inf"),
                "nonfinite JSON number")
        return value

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "JSON exceeds its bounded depth")
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
        raise GateError("invalid JSON literal")

    def decode(self) -> object:
        result = self.value()
        self.whitespace()
        require(self.index == len(self.text), "JSON has trailing content")
        return result


_WALL_ENABLED = False
_WALL_INSTALLED = False
_BLOCKED: dict[str, int] = {}
_ALLOWLIST = frozenset(
    [ROOT + "/" + SOURCE_PATH, ROOT + "/" + PROTOCOL_PATH,
     ROOT + "/" + CONTRACT_PATH]
    + [ROOT + "/" + row[1] for row in OWNERS]
)
_COMPILE_HASHES = frozenset((
    OWNER_BY_NAME["v2_repair"][2], OWNER_BY_NAME["adapter_repair"][2],
))


def no_matching_imports() -> None:
    require("re" not in sys.modules and "_sre" not in sys.modules
            and "regex" not in sys.modules
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "source-only verification imported a matching engine or candidate")


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    if not _WALL_ENABLED:
        return
    if event == "open":
        path = arguments[0] if arguments else None
        flags = arguments[2] if len(arguments) > 2 else None
        permitted = (type(path) is str and path in _ALLOWLIST
                     and type(flags) is int
                     and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT
                                  | os.O_TRUNC | os.O_APPEND) == 0)
        if permitted:
            return
        _BLOCKED["filesystem"] = _BLOCKED.get("filesystem", 0) + 1
        raise GateError("source-only gate rejected an unlisted or writable owner")
    if event == "compile":
        source = arguments[0] if arguments else None
        if type(source) is bytes and hashlib.sha256(source).hexdigest() in _COMPILE_HASHES:
            return
        _BLOCKED["dynamic_execution"] = _BLOCKED.get("dynamic_execution", 0) + 1
        raise GateError("source-only gate rejected unowned dynamic compilation")
    categories = (
        ("import", "matching_import"),
        ("subprocess", "process"),
        ("os.system", "process"),
        ("os.posix_spawn", "process"),
        ("ctypes.dlopen", "native"),
        ("socket", "network"),
        ("thread", "thread"),
        ("threading", "thread"),
        ("_thread", "thread"),
        ("time", "clock"),
        ("tempfile", "temporary"),
        ("os.mkdir", "filesystem"),
        ("os.rename", "filesystem"),
        ("os.remove", "filesystem"),
        ("os.rmdir", "filesystem"),
        ("os.chmod", "filesystem"),
        ("os.link", "filesystem"),
        ("os.symlink", "filesystem"),
        ("fcntl", "lock"),
        ("signal", "signal"),
        ("gzip", "archive"),
        ("zlib", "archive"),
        ("marshal", "dynamic_execution"),
        ("exec", "dynamic_execution"),
    )
    for prefix, category in categories:
        if event == prefix or event.startswith(prefix + "."):
            _BLOCKED[category] = _BLOCKED.get(category, 0) + 1
            raise GateError("source-only gate rejected " + category + ": " + event)


def install_wall() -> None:
    global _WALL_INSTALLED, _WALL_ENABLED
    no_matching_imports()
    if not _WALL_INSTALLED:
        sys.addaudithook(audit_wall)
        _WALL_INSTALLED = True
    _WALL_ENABLED = True


def read_exact(row: tuple[object, ...]) -> bytes:
    name, relative, expected_hash, expected_size, expected_device, expected_inode = row
    require(type(name) is str and type(relative) is str,
            "source ownership metadata is malformed")
    absolute = ROOT + "/" + relative
    require(absolute in _ALLOWLIST and not relative.startswith("/")
            and ".." not in relative.split("/")
            and not relative.endswith((".gz", ".zip", ".so", ".tar", ".xz", ".zst")),
            "reject a compressed, native, holdout, or escaped source owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(absolute, flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_nlink == 1
                and before.st_dev == expected_device
                and before.st_ino == expected_inode
                and before.st_size == expected_size
                and 0 < expected_size <= MAX_OWNER_BYTES,
                "source owner identity changed: " + relative)
        blocks: list[bytes] = []
        total = 0
        while total < expected_size:
            part = os.read(descriptor, min(262_144, expected_size - total))
            require(type(part) is bytes and len(part) > 0,
                    "source owner ended early: " + relative)
            total += len(part)
            blocks.append(part)
        require(os.read(descriptor, 1) == b"",
                "source owner grew while being authenticated: " + relative)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
                "source owner changed during its single bounded read: " + relative)
    finally:
        os.close(descriptor)
    content = b"".join(blocks)
    require(len(content) == expected_size and digest(content) == expected_hash,
            "source owner digest changed: " + relative)
    return content


def read_self(relative: str, expected_hash: str) -> tuple[bytes, dict[str, object]]:
    checked_hash(expected_hash, relative)
    absolute = ROOT + "/" + relative
    observed = os.stat(absolute, follow_symlinks=False)
    require(stat.S_ISREG(observed.st_mode)
            and stat.S_IMODE(observed.st_mode) == 0o600
            and observed.st_nlink == 1
            and 0 < observed.st_size <= MAX_OWNER_BYTES,
            "source-freeze owner is not an exclusive bounded regular file")
    row = (relative, relative, expected_hash, observed.st_size,
           observed.st_dev, observed.st_ino)
    raw = read_exact(row)
    return raw, {"path": relative, "sha256": expected_hash,
                 "bytes": len(raw), "device": observed.st_dev,
                 "inode": observed.st_ino}


def owner_document(name: str) -> dict[str, object]:
    row = OWNER_BY_NAME[name]
    return {"path": row[1], "sha256": row[2], "bytes": row[3],
            "device": row[4], "inode": row[5]}


def byte_assignments(raw: bytes, path: str,
                     expected: tuple[str, ...]) -> dict[str, bytes]:
    require(digest(raw) in _COMPILE_HASHES,
            "statically parse only an independently authenticated repair")
    try:
        tree = ast.parse(raw, filename=path, mode="exec")
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as error:
        raise GateError("bounded first-party repair AST is invalid") from error
    pending: list[ast.AST] = [tree]
    count = 0
    while pending:
        node = pending.pop()
        count += 1
        require(count <= MAX_AST_NODES,
                "first-party repair AST exceeds its frozen bound")
        pending.extend(ast.iter_child_nodes(node))
    found: dict[str, bytes] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in expected:
                require(target.id not in found
                        and isinstance(node.value, ast.Constant)
                        and type(node.value.value) is bytes,
                        "repair must contain exactly one literal byte anchor")
                found[target.id] = node.value.value
    require(set(found) == set(expected), "first-party byte anchors are incomplete")
    return found


def replace_once(raw: bytes, old: bytes, new: bytes, label: str) -> bytes:
    require(type(raw) is bytes and type(old) is bytes and type(new) is bytes
            and old != new and raw.count(old) == 1,
            "first-party source transformation is not unique: " + label)
    return raw.replace(old, new, 1)


def derive_adapter(original: bytes, repair: bytes) -> bytes:
    names = byte_assignments(
        repair, OWNER_BY_NAME["adapter_repair"][1],
        ("OLD_FLAG_BLOCK", "V2_FLAG_BLOCK", "OLD_ERROR_BLOCK",
         "V2_ERROR_BLOCK", "OLD_PATTERN_BLOCK", "V2_PATTERN_BLOCK",
         "V3_PATTERN_BLOCK"),
    )
    fixed = original
    for old, new, label in (
        ("OLD_FLAG_BLOCK", "V2_FLAG_BLOCK", "flags"),
        ("OLD_ERROR_BLOCK", "V2_ERROR_BLOCK", "pattern error"),
        ("OLD_PATTERN_BLOCK", "V2_PATTERN_BLOCK", "pattern value"),
        ("V2_PATTERN_BLOCK", "V3_PATTERN_BLOCK", "public adapter"),
    ):
        fixed = replace_once(fixed, names[old], names[new], label)
    require(len(fixed) == CORRECTED_ADAPTER_BYTES
            and digest(fixed) == CORRECTED_ADAPTER_SHA256,
            "historically corrected first-party public adapter did not reproduce")
    return fixed


def derive_lifetime_variant(original: bytes, repair: bytes) -> bytes:
    require(len(original) == V1_BRIDGE_BYTES
            and digest(original) == V1_BRIDGE_SHA256,
            "lifetime correction must start from the actually tested V1 bridge")
    names = byte_assignments(repair, OWNER_BY_NAME["v2_repair"][1],
                             ("SNAPSHOT_DECLARATION", "SNAPSHOT_BLOCK"))
    start_marker = b"static PyObject *rust_substitute_core("
    end_marker = b"static PyObject *rust_bound_substitute("
    require(original.count(start_marker) == 1 and original.count(end_marker) == 1,
            "the genuine substitution function boundary must be unique")
    start = original.index(start_marker)
    stop = original.index(end_marker, start)
    before, function, after = original[:start], original[start:stop], original[stop:]
    require(digest(before + after) == OUTSIDE_FUNCTION_SHA256,
            "the lifetime repair changed unrelated first-party source")
    declaration = names["SNAPSHOT_DECLARATION"]
    block = names["SNAPSHOT_BLOCK"]
    cleanup = b"Py_XDECREF(subject_snapshot);"
    require(function.count(declaration) == 1 and function.count(block) == 1
            and function.count(cleanup) == 8,
            "the observed premature snapshot and eight exits are not authentic")
    corrected = function.replace(declaration, b"", 1).replace(block, b"", 1)
    lines = corrected.splitlines(keepends=True)
    require(sum(line.strip() == cleanup for line in lines) == 8,
            "all eight obsolete snapshot releases must be removed exactly once")
    corrected = b"".join(line for line in lines if line.strip() != cleanup)
    require(b"subject_snapshot" not in corrected,
            "the premature exporter snapshot survived")
    require(corrected.count(b"rust_subject_open(&subject, pattern_value, value, 1)") == 1,
            "acquire the genuine original exporter exactly once")
    require(corrected.count(b"rust_subject_release(&subject);") == 8,
            "balance all eight genuine exporter cleanup exits")
    require(corrected.count(b"int callback = PyCallable_Check(replacement);") == 1,
            "preserve genuine callable replacement behavior")
    require(corrected.count(
        b"rust_match_allocate(pattern, value, groupindex, groups, 0, (Py_ssize_t)subject.length)"
    ) == 2, "preserve both match allocations against the genuine original subject")
    result = before + corrected + after
    require(len(result) == V2_BRIDGE_BYTES and digest(result) == V2_BRIDGE_SHA256,
            "complete first-party V2 bridge bytes do not independently reproduce")
    for marker in FORBIDDEN_ENGINE_BYTES:
        require(result.count(marker) == original.count(marker),
                "the correction introduced a delegated or external regex engine")
    return result


def phase_boundary() -> dict[str, object]:
    return {
        "candidate_build": "NOT RUN", "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED", "candidate_qualified": False,
        "qualified_candidate_count": 0, "candidate_workers_started": 0,
        "candidate_processes_started": 0, "candidate_imports": 0,
        "native_libraries_loaded": 0, "native_activations": 0,
        "compiler_processes_started": 0, "actual_compiler_process_count": 0,
        "archive_opens": 0, "archive_inflations": 0,
        "private_roots_created": 0, "recovery_operations": 0,
        "canonical_source_mutations": 0, "network_requests": 0,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "confidence_intervals": "NOT MEASURED", "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "undefined_behavior": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "phase1_canonical_candidate_context_crosswalk": "NOT ESTABLISHED",
        "phase1_v2_reconciliation": "NOT RUN",
        "supplemental_differential_fuzz_candidate_gate": "NOT ESTABLISHED",
        "genuine_2gib_candidate_search": "NOT RUN",
        "genuine_2gib_candidate_substitution": "NOT RUN",
        "holdout": "NOT OPENED", "winner_selected": False,
    }


def validate_p0(value: object) -> dict[str, object]:
    require(type(value) is dict
            and value.get("schema") == "rebar-cpython-re-p0-completeness-v1",
            "the pinned CPython completeness matrix is missing")
    denominator = value.get("denominator")
    obligations = value.get("obligations")
    suites = value.get("suites")
    require(type(denominator) is dict and type(obligations) is dict
            and type(suites) is list
            and denominator.get("final_required_case_execution_denominator") == 31_237
            and len(denominator.get("counted_suite_ids", [])) == 13
            and denominator.get("private_upstream_methods_outside_public_denominator") == 13
            and obligations.get("inherited_count") == 45
            and obligations.get("additional_named_count") == 28,
            "the historically recorded 31,237-case, 13-suite inventory changed")
    public = [row for row in suites
              if type(row) is dict and row.get("id") == "public_types_v1"]
    require(len(public) == 1,
            "the falsified historical public-types crosswalk must remain visible")
    baseline = public[0].get("baseline")
    require(type(baseline) is dict
            and public[0].get("baseline_records_sha256") == FALSIFIED_REFERENCE_SHA256
            and type(baseline.get("publication_receipt")) is dict
            and baseline["publication_receipt"].get("sha256")
            == FALSIFIED_RECEIPT_SHA256,
            "the historical matrix cannot be relabeled corrected or universally sound")
    return value


def validate_corrected_candidate_context(receipt: object, falsification: object,
                                         producer: object) -> dict[str, object]:
    require(type(receipt) is dict and type(falsification) is dict
            and type(producer) is dict,
            "bind the corrected reference, falsification, and V4 producer")
    require(receipt.get("schema")
            == "rebar-phase1-owned-public-type-reference-context-v1-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("publication_status") == "PASS"
            and receipt.get("reference_status") == "PASS"
            and receipt.get("actual_distinct_reference_process_ids") == [81, 82]
            and receipt.get("actual_reference_worker_count") == 2
            and receipt.get("validated_reference_worker_count") == 2
            and receipt.get("public_case_count_per_reference") == 6_912
            and receipt.get("original_case_execution_denominator") == 31_237
            and receipt.get("full_reference_records_sha256") == CORRECTED_REFERENCE_SHA256
            and receipt.get("cache_records_sha256") == CORRECTED_CACHE_SHA256
            and receipt.get("candidate_workers_started") == 0,
            "reject the falsified script-context baseline as a corrected reference")
    cases = falsification.get("falsifying_cases")
    require(falsification.get("schema")
            == "rebar-public-type-candidate-context-falsification-v1"
            and falsification.get("status") == "FALSIFIED"
            and falsification.get("candidate_facing_self_oracle_status") == "FAIL"
            and type(cases) is dict
            and cases.get("case_count") == 96
            and cases.get("actual_named_context_stdlib_records_sha256")
            == CORRECTED_CACHE_SHA256
            and cases.get("published_script_context_module") == "__main__"
            and cases.get("actual_candidate_facing_module")
            == "tools.independent_public_type_identity_serialization_v1",
            "preserve the genuine 96-case historical reference falsification")
    require(producer.get("schema")
            == "rebar-owned-six-family-original-p0-producer-v4-source-freeze"
            and producer.get("version") == 4
            and producer.get("case_execution_denominator") == 31_237
            and producer.get("suite_count") == 13,
            "the observed V10 campaign must retain its genuine V4 producer")
    corrected = producer.get("corrected_candidate_context_public_type_reference")
    historical = producer.get("frozen_public_type_reference")
    require(type(corrected) is dict and type(historical) is dict
            and corrected.get("candidate_facing_reference") is True
            and corrected.get("candidate_run_uses_both_complete_reference_vectors") is True
            and corrected.get("reference_pids") == [81, 82]
            and corrected.get("case_count") == 6_912
            and corrected.get("records_sha256") == CORRECTED_REFERENCE_SHA256
            and corrected.get("cache_records_sha256") == CORRECTED_CACHE_SHA256
            and corrected.get("historical_reference_records_sha256")
            == FALSIFIED_REFERENCE_SHA256
            and historical.get("records_sha256") == FALSIFIED_REFERENCE_SHA256
            and historical.get("receipt_sha256") == FALSIFIED_RECEIPT_SHA256
            and historical.get("reference_pids") == [82, 83]
            and historical.get("status")
            == "FALSIFIED FOR CANDIDATE-FACING EXECUTION CONTEXT",
            "never substitute the historical __main__ vector for corrected V4 vectors")
    return corrected


def validate_v10(forensics: object, receipt: object) -> dict[str, object]:
    require(type(forensics) is dict and type(receipt) is dict,
            "both independently durable V10 plaintext evidence owners are required")
    require(forensics.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v10-failures-forensic-summary-v1"
            and forensics.get("status") == "PASS"
            and forensics.get("analysis_status") == "PASS"
            and forensics.get("candidate_status") == "FAIL"
            and forensics.get("candidate_qualified") is False,
            "a passing forensic observation cannot become a passing candidate")
    totals = forensics.get("actual_result_totals")
    require(type(totals) is dict, "complete V10 case and worker totals are required")
    expected_totals = {
        "suite_count": 13, "case_execution_denominator": 31_237,
        "named_private_waiver_count": 13, "attempted_suite_count": 13,
        "started_suite_count": 13, "completed_suite_count": 13,
        "actual_candidate_workers": 13, "distinct_worker_process_id_count": 13,
        "duplicate_worker_process_id_count": 0,
        "missing_worker_process_id_count": 0,
        "all_original_observation_vectors_complete": True,
        "missing_original_case_observations": 0,
        "semantic_mismatch_count": 1_440,
        "verified_passing_case_count": 14_853,
        "verified_passing_cases_derived_by_subtraction": False,
        "records_from_fully_observed_failed_suites_are_counted_as_passing": False,
        "infrastructure_failure_count": 0,
        "candidate_status": "FAIL", "candidate_qualified": False,
    }
    for name, expected in expected_totals.items():
        require(totals.get(name) == expected,
                "genuine V10 candidate evidence changed: " + name)
    expected_pids = [81, 87, 88, 89, 90, 91, 92, 93, 94, 95, 196, 197, 198]
    require(totals.get("actual_worker_process_ids") == expected_pids,
            "the 13 independently recorded V10 workers changed")
    comparison = forensics.get("historical_comparison")
    require(type(comparison) is dict
            and comparison.get("previous_actual_rust_semantic_mismatch_count") == 928
            and comparison.get("previous_actual_rust_explicitly_verified_passing_case_count") == 8_965
            and comparison.get("new_actual_rust_semantic_mismatch_count") == 1_440
            and comparison.get("new_actual_rust_explicitly_verified_passing_case_count") == 14_853
            and comparison.get("semantic_mismatch_regression") == 512
            and comparison.get("passing_cases_derived_by_subtraction") is False,
            "keep genuine V7 and V10 results distinct")
    require(receipt.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v10-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("publication_status") == "PASS"
            and receipt.get("candidate_status") == "FAIL"
            and receipt.get("candidate_qualified") is False,
            "a durable receipt PASS cannot qualify the failing Rust candidate")
    for name, expected in (
        ("suite_count", 13), ("case_execution_denominator", 31_237),
        ("named_private_waiver_count", 13), ("semantic_mismatch_count", 1_440),
        ("verified_passing_case_count", 14_853), ("actual_candidate_workers", 13),
        ("distinct_worker_process_id_count", 13), ("holdout", "NOT OPENED"),
        ("performance", "NOT MEASURED"), ("memory", "NOT MEASURED"),
        ("benchmark_files_read", 0), ("clock_samples", 0),
    ):
        require(receipt.get(name) == expected,
                "genuine V10 failure publication changed: " + name)
    require(receipt.get("actual_worker_process_ids") == expected_pids,
            "durable genuine worker process identities changed")
    archive = receipt.get("archive")
    recorded_archive = forensics.get("failure_archive")
    require(type(archive) is dict and type(recorded_archive) is dict
            and archive.get("sha256")
            == recorded_archive.get("sha256")
            == "4be5a40ca3cdb0323eeb613a80c8eb22509dcbc21423156abbf0961fef19405e"
            and archive.get("size_bytes") == recorded_archive.get("bytes") == 3_746_528
            and archive.get("device") == recorded_archive.get("device") == 2064
            and archive.get("inode") == recorded_archive.get("inode") == 525043,
            "authenticate historical archive metadata without opening the archive")
    require(receipt.get("uncompressed_sha256")
            == recorded_archive.get("uncompressed_sha256")
            == "9e077ed42b0d092d0a53a640561a32ce4e4ab15d53ac2fa5c22d19c2664d4893"
            and receipt.get("uncompressed_bytes")
            == recorded_archive.get("uncompressed_bytes") == 5_385_134,
            "do not inflate or misrepresent historical failure data")
    return totals


def validate_v16(value: object) -> dict[str, object]:
    require(type(value) is dict
            and value.get("schema")
            == "rebar-phase2-owned-rust-buffer-shape-source-build-v16-durable-publication-receipt"
            and value.get("status") == "PASS"
            and value.get("build_status") == "PASS"
            and value.get("combined_bridge_sha256") == V1_BRIDGE_SHA256
            and value.get("combined_bridge_bytes") == V1_BRIDGE_BYTES
            and value.get("corrected_public_adapter_sha256") == CORRECTED_ADAPTER_SHA256
            and value.get("corrected_public_adapter_bytes") == CORRECTED_ADAPTER_BYTES
            and value.get("actual_compiler_process_count") == 28
            and value.get("expected_actual_compiler_process_count") == 28
            and value.get("candidate_correctness") == "NOT MEASURED"
            and value.get("candidate_matching") == "NOT RUN"
            and value.get("candidate_qualified") is False,
            "historical V16 built the old bridge only; it cannot prove V17")
    return value


def validate_v2(value: object, variant: bytes) -> dict[str, object]:
    require(type(value) is dict
            and value.get("schema")
            == "rebar-phase2-owned-rust-buffer-shape-pickle-source-repair-v2-source-freeze"
            and value.get("version") == 2 and value.get("family") == FAMILY,
            "require the independently frozen first-party V2 feature contract")
    source = value.get("source")
    protocol = value.get("protocol")
    target = value.get("candidate_variant")
    require(type(source) is dict and type(protocol) is dict and type(target) is dict,
            "complete V2 first-party feature ownership is required")
    for record, name in ((source, "v2_repair"), (protocol, "v2_protocol"),
                         (target, "v2_variant")):
        row = OWNER_BY_NAME[name]
        require(record.get("path") == row[1] and record.get("sha256") == row[2]
                and record.get("bytes") == row[3],
                "reject a borrowed or incomplete V2 owner: " + name)
    require(target.get("device") == OWNER_BY_NAME["v2_variant"][4]
            and target.get("inode") == OWNER_BY_NAME["v2_variant"][5]
            and target.get("derived_from_actually_tested_source") is True
            and target.get("new_candidate_family") is False
            and target.get("new_external_package") is False
            and target.get("premature_bytes_snapshot_count") == 0
            and target.get("live_original_exporter_open_count") == 1
            and target.get("live_exporter_release_exit_count") == 8
            and target.get("retained_original_subject_match_allocation_count") == 2
            and target.get("bytes_outside_substitution_function_sha256")
            == OUTSIDE_FUNCTION_SHA256
            and target.get("status") == "SOURCE FROZEN; NOT BUILT; NOT RUN"
            and len(variant) == V2_BRIDGE_BYTES
            and digest(variant) == V2_BRIDGE_SHA256,
            "reject a substituted, built, claimed-passing, or unrelated V2 bridge")
    previous = value.get("actual_previous_candidate_failure")
    boundary = value.get("phase_boundary")
    require(type(previous) is dict and type(boundary) is dict
            and previous.get("status") == "FAIL"
            and previous.get("actual_mismatch_count") == 1_440
            and previous.get("explicitly_verified_passing_case_count") == 14_853
            and previous.get("real_candidate_worker_count") == 13
            and previous.get("original_case_denominator") == 31_237
            and previous.get("original_suite_count") == 13
            and previous.get("genuine_failure_categories")
            == {"managed_v1": 16, "shape_v2": 1_056, "substitution_v2": 368}
            and boundary.get("candidate_variant_build") == "NOT RUN"
            and boundary.get("candidate_variant_qualified") is False
            and boundary.get("archive_opens") == 0
            and boundary.get("hidden_cases_read") == 0
            and boundary.get("holdout") == "NOT OPENED",
            "V2 source evidence cannot invent matching, an archive read, or a waiver")
    return value


def validate_graph(summary: object, inputs: object,
                   v2: dict[str, object]) -> dict[str, object]:
    require(type(summary) is dict and type(inputs) is dict,
            "all four pushed V59 graph owners are independently required")
    require(summary.get("schema") == "rebar-candidate-current-overview-v59-summary"
            and inputs.get("schema") == "rebar-candidate-current-overview-v59-inputs"
            and summary.get("version") == inputs.get("version") == GRAPH_VERSION,
            "reject stale V58, V50, or substituted current graphs")
    for document in (summary, inputs):
        for name, expected in (
            ("suite_count", 13), ("full_case_denominator", 31_237),
            ("actual_rust_semantic_mismatch_count", 1_440),
            ("actual_rust_verified_passing_case_count", 14_853),
            ("actual_rust_v10_semantic_mismatch_count", 1_440),
            ("actual_rust_v10_verified_passing_case_count", 14_853),
            ("authenticated_evidence_owner_lower_bound", EVIDENCE_FLOOR),
            ("authenticated_history_reference_lower_bound", HISTORY_FLOOR),
            ("qualified_candidate_count", 0),
        ):
            require(document.get(name) == expected,
                    "current pushed V59 evidence changed: " + name)
    require(summary.get("private_waiver_count") == 13
            and summary.get("additional_private_waivers") == 0
            and summary.get("original_cases_removed") == 0
            and summary.get("actual_rust_v10_candidate_status") == "FAIL"
            and summary.get("actual_rust_v10_candidate_workers") == 13
            and summary.get("actual_rust_v10_completed_suite_count") == 13
            and summary.get("runtime_no_delegation") == "NOT ESTABLISHED"
            and summary.get("performance") == "NOT MEASURED"
            and summary.get("memory") == "NOT MEASURED"
            and summary.get("undefined_behavior") == "NOT MEASURED"
            and summary.get("winner_selected") is False,
            "the actual V59 candidate history or source-only boundary changed")
    for field in ("actual_candidate_imports", "actual_candidate_workers_started_by_graph",
                  "actual_native_libraries_loaded_by_graph",
                  "actual_compiler_processes_started_by_graph",
                  "actual_clock_samples_by_graph"):
        require(summary.get(field) == 0,
                "the V59 graph performed a real matching or timing operation")
    families = summary.get("families")
    require(type(families) is list and len(families) == 7,
            "preserve six first-party families and the Python baseline")
    names = [item.get("family") for item in families if type(item) is dict]
    require(names == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
            "a wrapper, external package, or candidate family was substituted")
    rust = families[1]
    feature = rust.get("buffer_shape_v2_source_feature")
    require(rust.get("qualified") is False and type(feature) is dict
            and feature.get("complete_source_contract") == v2
            and feature.get("candidate_qualified") is False
            and feature.get("candidate_build_status") == "NOT BUILT"
            and feature.get("holdout") == "NOT OPENED",
            "the current graph must independently bind the exact unbuilt V2 repair")
    feature_owners = feature.get("owners")
    require(type(feature_owners) is dict,
            "all four independently pinned V2 owners are required")
    for role, name in (("applicator", "v2_repair"), ("protocol", "v2_protocol"),
                       ("contract", "v2_contract"), ("bridge_source", "v2_variant")):
        entry = feature_owners.get(role)
        row = OWNER_BY_NAME[name]
        require(type(entry) is dict and entry.get("path") == row[1]
                and entry.get("sha256") == row[2] and entry.get("bytes") == row[3],
                "reject an incomplete current V59 feature owner: " + role)
    return summary


def validate_package(raw: dict[str, bytes]) -> None:
    manifest = raw["cargo_manifest"].decode("utf-8", "strict")
    lock = raw["cargo_lock"].decode("utf-8", "strict")
    for marker in ('name = "rebar-rust-continuation"', 'version = "0.1.0"',
                   'edition = "2024"', 'rust-version = "1.85"',
                   "publish = false", 'crate-type = ["cdylib"]',
                   "opt-level = 3", "lto = true", "codegen-units = 1",
                   'panic = "abort"'):
        require(marker in manifest, "first-party Rust manifest changed: " + marker)
    for marker in ("[dependencies", "[dev-dependencies", "[build-dependencies",
                   "[workspace", "[patch", "[replace", "regex", "pcre",
                   "oniguruma", "hyperscan"):
        require(marker not in manifest.lower(),
                "external Rust packages or regular-expression engines are forbidden")
    require(lock.count("[[package]]") == 1
            and 'name = "rebar-rust-continuation"' in lock
            and 'version = "0.1.0"' in lock
            and "dependencies" not in lock,
            "Cargo.lock must contain exactly one owned offline package")


def current_history() -> dict[str, object]:
    return {
        "graph_version": GRAPH_VERSION,
        "actual_candidate_status": "FAIL",
        "actual_mismatch_count": 1_440,
        "actually_verified_passing_case_count": 14_853,
        "actual_candidate_worker_count": 13,
        "actual_completed_suite_count": 13,
        "actual_infrastructure_failure_count": 0,
        "verified_passing_cases_derived_by_subtraction": False,
        "historical_v7_mismatch_count": 928,
        "historical_v7_verified_passing_case_count": 8_965,
        "mismatch_regression_against_v7": 512,
        "case_execution_denominator": 31_237,
        "named_private_waiver_count": 13,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "qualified_candidate_count": 0,
        "holdout": "NOT OPENED", "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "winner_selected": False,
    }


def collect_context(source_pin: str, protocol_pin: str,
                    contract_pin: str | None = None
                    ) -> tuple[dict[str, object], dict[str, object]]:
    no_matching_imports()
    checked_hash(source_pin, "V17 source")
    checked_hash(protocol_pin, "V17 protocol")
    source_raw, source_info = read_self(SOURCE_PATH, source_pin)
    protocol_raw, protocol_info = read_self(PROTOCOL_PATH, protocol_pin)
    require(source_raw.endswith(b"\n") and not source_raw.endswith(b"\n\n")
            and protocol_raw.endswith(b"\n") and not protocol_raw.endswith(b"\n\n"),
            "source and protocol require exactly one final newline")
    if contract_pin is not None:
        checked_hash(contract_pin, "V17 contract")
    raw: dict[str, bytes] = {}
    for row in OWNERS:
        require(row[0] not in raw, "reject duplicate independently owned sources")
        raw[row[0]] = read_exact(row)
    p0 = validate_p0(StrictJSON(raw["p0"]).decode())
    corrected_reference = validate_corrected_candidate_context(
        StrictJSON(raw["corrected_reference_receipt"]).decode(),
        StrictJSON(raw["public_context_falsification"]).decode(),
        StrictJSON(raw["v4_producer_contract"]).decode(),
    )
    forensics = StrictJSON(raw["v10_forensics"]).decode()
    receipt = StrictJSON(raw["v10_receipt"]).decode()
    totals = validate_v10(forensics, receipt)
    v16 = validate_v16(StrictJSON(raw["v16_build_receipt"]).decode())
    variant = derive_lifetime_variant(raw["v1_variant"], raw["v2_repair"])
    require(variant == raw["v2_variant"],
            "the committed V2 source is not the independently reconstructed source")
    adapter = derive_adapter(raw["original_adapter"], raw["adapter_repair"])
    v2 = validate_v2(StrictJSON(raw["v2_contract"]).decode(), variant)
    summary = StrictJSON(raw["graph_summary"]).decode()
    inputs = StrictJSON(raw["graph_inputs"]).decode()
    graph = validate_graph(summary, inputs, v2)
    validate_package(raw)
    for marker in FORBIDDEN_ENGINE_BYTES:
        require(variant.count(marker) == raw["v1_variant"].count(marker)
                and adapter.count(marker) == raw["original_adapter"].count(marker),
                "reject a foreign matcher, cross-family call, or fallback")
    context = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS", "version": VERSION, "read_only": True,
        "source": source_info, "protocol": protocol_info,
        "current_history": current_history(),
        "graph_version": GRAPH_VERSION,
        "graph_owners": [owner_document(name) for name in
                         ("graph_renderer", "graph_inputs", "graph_summary", "graph_chart")],
        "first_party_rust_source_owner_count": len(RUST_SOURCE_NAMES),
        "from_scratch_candidate_family_count": 6,
        "baseline_count": 1,
        "v2_source_owners": [owner_document(name) for name in
                              ("v2_repair", "v2_protocol", "v2_contract", "v2_variant")],
        "v2_bridge_sha256": V2_BRIDGE_SHA256,
        "v2_bridge_bytes": V2_BRIDGE_BYTES,
        "outside_substitution_function_sha256": OUTSIDE_FUNCTION_SHA256,
        "corrected_adapter_sha256": CORRECTED_ADAPTER_SHA256,
        "corrected_adapter_bytes": CORRECTED_ADAPTER_BYTES,
        "future_independent_phase_count": 2,
        "future_process_roles_per_phase": len(PROCESS_NAMES),
        "future_total_compiler_process_count": 28,
        "future_native_engine_sha256": "NOT MEASURED",
        "future_native_bridge_sha256": "NOT MEASURED",
        "historical_v16_build_status": v16["build_status"],
        "historical_v16_bridge_sha256": V1_BRIDGE_SHA256,
        "v10_failure_evidence": [owner_document("v10_receipt"),
                                 owner_document("v10_forensics")],
        "corrected_v4_candidate_context": {
            "reference_process_ids": [81, 82],
            "public_cases_per_reference": 6_912,
            "full_reference_records_sha256": CORRECTED_REFERENCE_SHA256,
            "cache_records_sha256": CORRECTED_CACHE_SHA256,
            "falsified_historical_reference_records_sha256":
                FALSIFIED_REFERENCE_SHA256,
            "crosswalk_status": "NOT ESTABLISHED",
        },
        "source_owner_count": len(OWNERS),
        **phase_boundary(),
    }
    state: dict[str, object] = {
        "owners": raw,
        "originals": {OWNER_BY_NAME[name][1]: raw[name]
                      for name in RUST_SOURCE_NAMES},
        "combined_bridge": variant,
        "corrected_adapter": adapter,
        "low_level_v9_source": raw["low_level_v9"],
        "p0": p0, "forensics": forensics, "v10_totals": totals,
        "v2_contract": v2, "v59_graph": graph,
        "corrected_v4_candidate_context": corrected_reference,
        "source_info": source_info, "protocol_info": protocol_info,
    }
    expected = contract_document(source_pin, protocol_pin, state)
    if contract_pin is not None:
        expected_bytes = (canonical(expected) + "\n").encode("ascii")
        require(digest(expected_bytes) == contract_pin,
                "independently caller-pin the complete V17 canonical contract")
        contract_raw, contract_info = read_self(CONTRACT_PATH, contract_pin)
        require(contract_raw == expected_bytes
                and StrictJSON(contract_raw).decode() == expected,
                "V17 contract is not exact canonical JSON with one final newline")
        context["contract"] = contract_info
    no_matching_imports()
    return context, state


def contract_document(source_pin: str, protocol_pin: str,
                      state: dict[str, object]) -> dict[str, object]:
    checked_hash(source_pin, "V17 source")
    checked_hash(protocol_pin, "V17 protocol")
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION,
        "status": "SOURCE FROZEN; FIRST-PARTY V2 RUST BRIDGE NOT BUILT OR RUN",
        "phase": "CANDIDATES", "family": FAMILY,
        "source": {"path": SOURCE_PATH, "sha256": source_pin,
                   "bytes": state["source_info"]["bytes"]},
        "protocol": {"path": PROTOCOL_PATH, "sha256": protocol_pin,
                     "bytes": state["protocol_info"]["bytes"]},
        "immutable_goal": owner_document("goal"),
        "original_oracle": {
            "implementation": "CPython", "version": "3.14.6",
            "python": {"path": PYTHON, "sha256": PYTHON_SHA256},
            "matrix": owner_document("p0"), "suite_count": 13,
            "case_execution_denominator": 31_237,
            "named_private_waiver_count": 13,
            "inherited_obligation_count": 45,
            "additional_obligation_count": 28,
            "additional_callable_reference_case_count": 50,
            "additional_cases_included_in_original_denominator": False,
            "canonical_candidate_context_crosswalk": "NOT ESTABLISHED",
            "historical_public_types_vector_status": "FALSIFIED",
            "supplemental_differential_fuzz_case_count": 8_244,
            "supplemental_differential_fuzz_candidate_gate": "NOT ESTABLISHED",
            "genuine_2gib_candidate_search": "NOT RUN",
            "genuine_2gib_candidate_substitution": "NOT RUN",
        },
        "corrected_v4_candidate_facing_reference": {
            "producer_source": owner_document("v4_producer"),
            "producer_protocol": owner_document("v4_producer_protocol"),
            "producer_contract": owner_document("v4_producer_contract"),
            "reference_source": owner_document("corrected_reference_source"),
            "reference_protocol": owner_document("corrected_reference_protocol"),
            "reference_contract": owner_document("corrected_reference_contract"),
            "corrected_reference_receipt": owner_document("corrected_reference_receipt"),
            "historical_reference_falsification": owner_document("public_context_falsification"),
            "reference_process_ids": [81, 82],
            "reference_cases_per_worker": 6_912,
            "corrected_full_records_sha256": CORRECTED_REFERENCE_SHA256,
            "corrected_cache_records_sha256": CORRECTED_CACHE_SHA256,
            "falsified_historical_records_sha256": FALSIFIED_REFERENCE_SHA256,
            "falsified_historical_receipt_sha256": FALSIFIED_RECEIPT_SHA256,
            "falsified_historical_reference_process_ids": [82, 83],
            "historical_reference_status": "FALSIFIED",
            "phase1_canonical_candidate_context_crosswalk": "NOT ESTABLISHED",
            "actual_v10_used_corrected_v4_context": True,
        },
        "current_pushed_graph": {
            "version": GRAPH_VERSION,
            "owners": [owner_document(name) for name in
                       ("graph_renderer", "graph_inputs", "graph_summary", "graph_chart")],
            "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
            "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
            "current_rust_candidate_status": "FAIL",
            "current_rust_semantic_mismatch_count": 1_440,
            "current_rust_verified_passing_case_count": 14_853,
            "current_rust_worker_count": 13,
            "qualified_candidate_count": 0,
            "graph_candidate_family_count": 6,
            "graph_python_baseline_count": 1,
        },
        "actual_previous_rust_result": {
            "status": "FAIL", "candidate_qualified": False,
            "forensic_summary": owner_document("v10_forensics"),
            "durable_failure_receipt": owner_document("v10_receipt"),
            "semantic_mismatch_count": 1_440,
            "explicitly_verified_passing_case_count": 14_853,
            "verified_passes_derived_by_subtraction": False,
            "worker_count": 13, "completed_suite_count": 13,
            "infrastructure_failure_count": 0,
            "genuine_failure_categories":
                {"managed_v1": 16, "shape_v2": 1_056, "substitution_v2": 368},
            "historical_v7_mismatch_count": 928,
            "historical_v7_verified_passing_case_count": 8_965,
            "mismatch_regression_against_v7": 512,
        },
        "historical_v16_first_party_build": {
            "source": owner_document("v16_builder"),
            "protocol": owner_document("v16_protocol"),
            "contract": owner_document("v16_contract"),
            "durable_receipt": owner_document("v16_build_receipt"),
            "build_status": "PASS", "candidate_correctness": "NOT MEASURED",
            "actual_compiler_process_count": 28,
            "bridge_source_sha256": V1_BRIDGE_SHA256,
            "bridge_source_bytes": V1_BRIDGE_BYTES,
            "public_adapter_sha256": CORRECTED_ADAPTER_SHA256,
            "public_adapter_bytes": CORRECTED_ADAPTER_BYTES,
            "historical_binary_proves_v17": False,
        },
        "first_party_rust_source_family": {
            "family": FAMILY,
            "canonical_source_owners": [owner_document(name)
                                        for name in RUST_SOURCE_NAMES],
            "canonical_source_owner_count": 9,
            "unchanged_private_source_owner_count": 7,
            "private_overlay_count_per_phase": 2,
            "cargo_package_count": 1,
            "external_cargo_dependency_count": 0,
            "external_regular_expression_engines": "FORBIDDEN",
            "stdlib_matching_delegation": "FORBIDDEN",
            "cross_candidate_matching_delegation": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
            "canonical_sources_modified": False,
        },
        "first_party_v2_buffer_lifetime_feature": {
            "owners": [owner_document(name) for name in
                       ("v2_repair", "v2_protocol", "v2_contract", "v2_variant")],
            "actually_failed_v1_bridge": owner_document("v1_variant"),
            "derived_bridge_sha256": V2_BRIDGE_SHA256,
            "derived_bridge_bytes": V2_BRIDGE_BYTES,
            "outside_function_sha256": OUTSIDE_FUNCTION_SHA256,
            "live_original_exporter_acquisitions": 1,
            "live_original_exporter_releases": 8,
            "original_subject_match_allocations": 2,
            "static_ast_derivation_only": True,
            "repair_verifier_imported_or_executed": False,
            "native_build_status": "NOT RUN",
            "candidate_matching": "NOT RUN",
            "candidate_correctness": "NOT MEASURED",
        },
        "preserved_public_adapter": {
            "owners": [owner_document(name) for name in
                       ("adapter_repair", "adapter_protocol", "adapter_contract")],
            "sha256": CORRECTED_ADAPTER_SHA256,
            "bytes": CORRECTED_ADAPTER_BYTES,
            "independently_reconstructed": True,
        },
        "authenticated_low_level_first_party_kernels": {
            "v9": [owner_document(name) for name in
                   ("low_level_v9", "low_level_v9_protocol", "low_level_v9_contract")],
            "v7": [owner_document(name) for name in
                   ("low_level_v7", "low_level_v7_protocol", "low_level_v7_contract")],
            "source_only_kernel_execution": False,
        },
        "future_offline_native_build": {
            "authorization": "EXPLICIT FUTURE --build ONLY",
            "phase1_v2_reconciliation": "REQUIRED BEFORE BUILD; NOT ESTABLISHED",
            "phase1_v2_source_path": PHASE_ONE_V2_SOURCE_PATH,
            "phase1_v2_protocol_path": PHASE_ONE_V2_PROTOCOL_PATH,
            "phase1_v2_contract_path": PHASE_ONE_V2_CONTRACT_PATH,
            "phase1_v2_source_sha256": "NOT MEASURED",
            "phase1_v2_protocol_sha256": "NOT MEASURED",
            "phase1_v2_contract_sha256": "NOT MEASURED",
            "label": BUILD_LABEL,
            "root_parent": "/tmp",
            "mandatory_low_level_root_prefix": ROOT_PREFIX,
            "private_root_mode": "0700",
            "private_source_mode": "0600",
            "phase_names": list(PHASES),
            "independent_phase_count": 2,
            "distinct_owned_sources_per_phase": 9,
            "unchanged_sources_per_phase": 7,
            "fresh_v2_bridge_overlays": 2,
            "fresh_corrected_adapter_overlays": 2,
            "process_roles_per_phase": list(PROCESS_NAMES),
            "compiler_process_count_per_phase": 14,
            "expected_actual_compiler_process_count": 28,
            "actual_process_phase_binding":
                "AUTHENTICATED ORDERED 14-ROLE SLICE AND SANITIZED WORKING DIRECTORY",
            "missing_real_process_phase_field_allowed": True,
            "cargo_flags": ["--release", "--locked", "--offline", "--frozen"],
            "phase_local_cargo_home_and_target": True,
            "native_engine_sha256": "NOT MEASURED",
            "native_bridge_sha256": "NOT MEASURED",
            "native_engine_bytes": "NOT MEASURED",
            "native_bridge_bytes": "NOT MEASURED",
            "two_independent_full_elf_comparisons_required": True,
            "prebuilt_native_artifacts_permitted": False,
            "publish_build_failure_durably": True,
            "canonical_candidate_activation": False,
        },
        "focused_source_evidence_accounting": {
            "current_pushed_evidence_owner_lower_bound": EVIDENCE_FLOOR,
            "current_pushed_history_reference_lower_bound": HISTORY_FLOOR,
            "new_focused_v17_source_owners": 3,
            "resulting_evidence_owner_lower_bound": EVIDENCE_FLOOR + 3,
            "resulting_history_reference_lower_bound": HISTORY_FLOOR + 3,
            "global_evidence_owner_census": "NOT MEASURED",
            "future_build_evidence_counted": 0,
        },
        "phase_boundary": phase_boundary(),
    }


def synthetic_plan() -> dict[str, object]:
    phases: list[dict[str, object]] = []
    for phase_index, phase in enumerate(PHASES):
        rows: dict[str, dict[str, object]] = {}
        for owner_index, name in enumerate(RUST_SOURCE_NAMES):
            row = OWNER_BY_NAME[name]
            expected_hash = V2_BRIDGE_SHA256 if name == "original_bridge" else (
                CORRECTED_ADAPTER_SHA256 if name == "original_adapter" else row[2]
            )
            expected_size = V2_BRIDGE_BYTES if name == "original_bridge" else (
                CORRECTED_ADAPTER_BYTES if name == "original_adapter" else row[3]
            )
            rows[row[1]] = {
                "sha256": expected_hash, "bytes": expected_size,
                "mode": 0o600, "nlink": 1, "device": 70017,
                "inode": 200_000 + phase_index * 100 + owner_index,
                "overlay_count": int(name in ("original_bridge", "original_adapter")),
            }
        outputs: dict[str, dict[str, object]] = {}
        for role_index, (role, filename) in enumerate(
                (("engine", ENGINE_NAME), ("bridge", BRIDGE_NAME))):
            outputs[role] = {
                "file_name": filename,
                "sha256": digest(("V17 SYNTHETIC CONTROL ONLY " + role).encode("ascii")),
                "size_bytes": 10_000 + role_index,
                "device": 71017,
                "inode": 300_000 + phase_index * 10 + role_index,
                "evidence_kind": "SYNTHETIC CONTROL; NOT A REAL NATIVE BUILD",
            }
        phases.append({
            "name": phase, "directory_mode": 0o700,
            "directory_device": 72017,
            "directory_inode": 400_000 + phase_index,
            "fresh_source_owners": rows,
            "native_outputs": outputs,
        })
    processes = [
        {
            "name": name,
            "phase": PHASES[index // len(PROCESS_NAMES)],
            "working_directory": "<FRESH_PRIVATE_TMP>/"
                                 + PHASES[index // len(PROCESS_NAMES)],
            "pid": 500_000 + index,
            "exit_status": 0,
            "evidence_kind": "SYNTHETIC CONTROL; NOT A REAL PROCESS",
        }
        for index, name in enumerate(PROCESS_NAMES * 2)
    ]
    return {
        "schema": SCHEMA + "-synthetic-control-only",
        "evidence_kind": "SYNTHETIC SELF-TEST; NO REAL BUILD OR PROCESS",
        "graph_version": GRAPH_VERSION,
        "root_prefix": ROOT_PREFIX,
        "case_execution_denominator": 31_237,
        "suite_count": 13,
        "named_private_waiver_count": 13,
        "current_mismatch_count": 1_440,
        "current_verified_passing_case_count": 14_853,
        "historical_v7_mismatch_count": 928,
        "historical_v7_verified_passing_case_count": 8_965,
        "qualified_candidate_count": 0,
        "candidate_workers_started": 0,
        "archive_opens": 0,
        "native_libraries_loaded": 0,
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "winner_selected": False,
        "phases": phases,
        "processes": processes,
    }


def validate_synthetic_plan(plan: object) -> dict[str, object]:
    require(type(plan) is dict, "require the complete synthetic-only V17 plan")
    required = {
        "schema": SCHEMA + "-synthetic-control-only",
        "evidence_kind": "SYNTHETIC SELF-TEST; NO REAL BUILD OR PROCESS",
        "graph_version": GRAPH_VERSION, "root_prefix": ROOT_PREFIX,
        "case_execution_denominator": 31_237, "suite_count": 13,
        "named_private_waiver_count": 13, "current_mismatch_count": 1_440,
        "current_verified_passing_case_count": 14_853,
        "historical_v7_mismatch_count": 928,
        "historical_v7_verified_passing_case_count": 8_965,
        "qualified_candidate_count": 0, "candidate_workers_started": 0,
        "archive_opens": 0, "native_libraries_loaded": 0,
        "clock_samples": 0, "hidden_cases_read": 0,
        "holdout": "NOT OPENED", "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "winner_selected": False,
    }
    for name, expected in required.items():
        require(plan.get(name) == expected,
                "reject a forged synthetic boundary or history: " + name)
    phases = plan.get("phases")
    require(type(phases) is list and len(phases) == 2
            and [item.get("name") for item in phases if type(item) is dict]
            == list(PHASES), "require two ordered, independently owned phases")
    phase_identities: set[tuple[int, int]] = set()
    source_identities: set[tuple[int, int]] = set()
    output_identities: set[tuple[int, int]] = set()
    expected_paths = {OWNER_BY_NAME[name][1] for name in RUST_SOURCE_NAMES}
    for phase_index, phase in enumerate(phases):
        require(type(phase) is dict and phase.get("directory_mode") == 0o700
                and type(phase.get("directory_device")) is int
                and type(phase.get("directory_inode")) is int,
                "reject an unsafe synthetic private root")
        phase_identity = (phase["directory_device"], phase["directory_inode"])
        require(phase_identity not in phase_identities,
                "reject a shared synthetic independent phase")
        phase_identities.add(phase_identity)
        rows = phase.get("fresh_source_owners")
        require(type(rows) is dict and set(rows) == expected_paths,
                "require all nine exact first-party source owners")
        for name in RUST_SOURCE_NAMES:
            owner = OWNER_BY_NAME[name]
            entry = rows[owner[1]]
            expected_hash = V2_BRIDGE_SHA256 if name == "original_bridge" else (
                CORRECTED_ADAPTER_SHA256 if name == "original_adapter" else owner[2]
            )
            expected_size = V2_BRIDGE_BYTES if name == "original_bridge" else (
                CORRECTED_ADAPTER_BYTES if name == "original_adapter" else owner[3]
            )
            overlay = int(name in ("original_bridge", "original_adapter"))
            require(type(entry) is dict and entry.get("sha256") == expected_hash
                    and entry.get("bytes") == expected_size
                    and entry.get("mode") == 0o600
                    and entry.get("nlink") == 1
                    and entry.get("overlay_count") == overlay
                    and type(entry.get("device")) is int
                    and type(entry.get("inode")) is int,
                    "reject missing, foreign, or repeated phase source: " + name)
            identity = (entry["device"], entry["inode"])
            require(identity not in source_identities,
                    "reject reused first-party source phase inodes")
            source_identities.add(identity)
        outputs = phase.get("native_outputs")
        require(type(outputs) is dict and set(outputs) == {"engine", "bridge"},
                "require both explicitly synthetic native control roles")
        for role, filename in (("engine", ENGINE_NAME), ("bridge", BRIDGE_NAME)):
            entry = outputs[role]
            expected_hash = digest(("V17 SYNTHETIC CONTROL ONLY " + role).encode("ascii"))
            require(type(entry) is dict and entry.get("file_name") == filename
                    and entry.get("sha256") == expected_hash
                    and type(entry.get("size_bytes")) is int
                    and entry["size_bytes"] > 0
                    and entry.get("evidence_kind")
                    == "SYNTHETIC CONTROL; NOT A REAL NATIVE BUILD"
                    and type(entry.get("device")) is int
                    and type(entry.get("inode")) is int,
                    "reject an actual, invented, or substituted synthetic output")
            identity = (entry["device"], entry["inode"])
            require(identity not in output_identities,
                    "reject a reused synthetic native inode")
            output_identities.add(identity)
    processes = plan.get("processes")
    require(type(processes) is list and len(processes) == 28,
            "require exactly two independent 14-role process slices")
    process_ids: set[int] = set()
    for index, process in enumerate(processes):
        phase = PHASES[index // len(PROCESS_NAMES)]
        require(type(process) is dict
                and process.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                and ("phase" not in process or process.get("phase") == phase)
                and process.get("working_directory")
                == "<FRESH_PRIVATE_TMP>/" + phase
                and type(process.get("pid")) is int and process["pid"] > 0
                and process["pid"] not in process_ids
                and process.get("exit_status") == 0
                and process.get("evidence_kind")
                == "SYNTHETIC CONTROL; NOT A REAL PROCESS",
                "reject a misplaced, forged, failed, or duplicated process role")
        process_ids.add(process["pid"])
    return {"status": "PASS", "synthetic_only": True,
            "independent_phase_count": 2,
            "source_owners_per_phase": 9,
            "distinct_source_inode_count": len(source_identities),
            "distinct_synthetic_native_inode_count": len(output_identities),
            "synthetic_process_role_count": len(process_ids),
            "actual_compiler_process_count": 0,
            "actual_native_libraries_loaded": 0}


def clone(value: object) -> object:
    return StrictJSON((canonical(value) + "\n").encode("ascii")).decode()


def self_test(source_pin: str, protocol_pin: str,
              contract_pin: str) -> dict[str, object]:
    context, state = collect_context(source_pin, protocol_pin, contract_pin)
    accepted: list[str] = []
    rejected: list[str] = []

    def reject(label: str, operation: object) -> None:
        try:
            operation()
        except (GateError, OSError, ValueError, TypeError, IndexError,
                UnicodeError, RecursionError, OverflowError):
            rejected.append(label)
            return
        raise GateError("hostile source-only control was accepted: " + label)

    plan = synthetic_plan()
    proof = validate_synthetic_plan(plan)
    accepted.append("complete-authenticated-synthetic-two-phase-plan")
    without_phase = clone(plan)
    for item in without_phase["processes"]:
        del item["phase"]
    validate_synthetic_plan(without_phase)
    accepted.append("genuine-ordered-process-records-do-not-require-phase-field")
    validate_v10(state["forensics"], StrictJSON(state["owners"]["v10_receipt"]).decode())
    accepted.append("actual-v10-failure-and-historical-v7-remain-distinct")
    require(derive_lifetime_variant(state["owners"]["v1_variant"],
                                    state["owners"]["v2_repair"])
            == state["owners"]["v2_variant"],
            "the exact full first-party V2 derivation must remain reproducible")
    accepted.append("statically-reproduce-exact-v2-live-exporter-bridge")
    require(derive_adapter(state["owners"]["original_adapter"],
                           state["owners"]["adapter_repair"])
            == state["corrected_adapter"],
            "the previously corrected first-party adapter must reproduce")
    accepted.append("statically-reproduce-exact-corrected-public-adapter")
    accepted.append("separately-authenticate-falsification-and-corrected-v4-reference")

    for name, bad in (
        ("graph_version", 58), ("root_prefix", "rebar-phase2-native-build-v17-rust-"),
        ("case_execution_denominator", 31_236), ("suite_count", 12),
        ("named_private_waiver_count", 14), ("current_mismatch_count", 928),
        ("current_verified_passing_case_count", 8_965),
        ("historical_v7_mismatch_count", 1_440),
        ("historical_v7_verified_passing_case_count", 14_853),
        ("qualified_candidate_count", 1), ("candidate_workers_started", 1),
        ("archive_opens", 1), ("native_libraries_loaded", 1),
        ("clock_samples", 1), ("hidden_cases_read", 1),
        ("holdout", "OPENED"), ("performance", "FAST"),
        ("memory", "LOW"), ("winner_selected", True),
    ):
        def mutate_top(key: str = name, value: object = bad) -> None:
            changed = clone(plan)
            changed[key] = value
            validate_synthetic_plan(changed)
        reject("reject-" + name, mutate_top)

    for index in range(2):
        for field, bad in (("name", "reference-c"), ("directory_mode", 0o755),
                           ("directory_device", "foreign")):
            def mutate_phase(at: int = index, key: str = field,
                             value: object = bad) -> None:
                changed = clone(plan)
                changed["phases"][at][key] = value
                validate_synthetic_plan(changed)
            reject("reject-phase-" + str(index) + "-" + field, mutate_phase)
        for name in RUST_SOURCE_NAMES:
            path = OWNER_BY_NAME[name][1]
            for field, bad in (("sha256", "0" * 64), ("bytes", 0),
                               ("mode", 0o644), ("nlink", 2),
                               ("overlay_count", 7), ("inode", "borrowed")):
                def mutate_owner(at: int = index, owner_path: str = path,
                                 key: str = field, value: object = bad) -> None:
                    changed = clone(plan)
                    changed["phases"][at]["fresh_source_owners"][owner_path][key] = value
                    validate_synthetic_plan(changed)
                reject("reject-phase-" + str(index) + "-" + name + "-" + field,
                       mutate_owner)
        for role in ("engine", "bridge"):
            for field, bad in (("file_name", "foreign_regex.so"),
                               ("sha256", "0" * 64), ("size_bytes", 0),
                               ("inode", "foreign"),
                               ("evidence_kind", "ACTUAL NATIVE BUILD")):
                def mutate_native(at: int = index, kind: str = role,
                                  key: str = field, value: object = bad) -> None:
                    changed = clone(plan)
                    changed["phases"][at]["native_outputs"][kind][key] = value
                    validate_synthetic_plan(changed)
                reject("reject-phase-" + str(index) + "-" + role + "-" + field,
                       mutate_native)
    for index in range(28):
        for field, bad in (("name", "build_external_regex"),
                           ("phase", "reference-c"),
                           ("working_directory", "<FRESH_PRIVATE_TMP>/reference-c"),
                           ("pid", 0), ("exit_status", 1),
                           ("evidence_kind", "ACTUAL COMPILER")):
            def mutate_process(at: int = index, key: str = field,
                               value: object = bad) -> None:
                changed = clone(plan)
                changed["processes"][at][key] = value
                validate_synthetic_plan(changed)
            reject("reject-process-" + str(index) + "-" + field,
                   mutate_process)

    def duplicate_phase() -> None:
        changed = clone(plan)
        changed["phases"][1]["directory_inode"] = changed["phases"][0]["directory_inode"]
        validate_synthetic_plan(changed)

    def duplicate_process() -> None:
        changed = clone(plan)
        changed["processes"][1]["pid"] = changed["processes"][0]["pid"]
        validate_synthetic_plan(changed)

    reject("reject-reused-independent-phase-inode", duplicate_phase)
    reject("reject-reused-genuine-process-id", duplicate_process)
    reject("reject-duplicate-json-owner-key",
           lambda: StrictJSON(b'{"owner":1,"owner":2}').decode())
    reject("reject-trailing-json-content",
           lambda: StrictJSON(b'{"owner":1} forged').decode())
    reject("reject-wrong-canonical-contract",
           lambda: collect_context(source_pin, protocol_pin, "0" * 64))

    def reject_unreconciled_future_build() -> None:
        provided = {
            "mode": "--build", "label": BUILD_LABEL,
            "source_sha256": source_pin,
            "protocol_sha256": protocol_pin,
            "contract_sha256": contract_pin,
            "phase1_v2_source_sha256": "1" * 64,
            "phase1_v2_protocol_sha256": "2" * 64,
            "phase1_v2_contract_sha256": "3" * 64,
        }
        run_build(provided)

    reject("reject-unreconciled-future-phase-one-before-build-or-private-root",
           reject_unreconciled_future_build)
    actual_receipt = StrictJSON(state["owners"]["corrected_reference_receipt"]).decode()
    actual_falsification = StrictJSON(state["owners"]["public_context_falsification"]).decode()
    actual_producer = StrictJSON(state["owners"]["v4_producer_contract"]).decode()
    for field, wrong in (
        ("actual_distinct_reference_process_ids", [82, 83]),
        ("full_reference_records_sha256", FALSIFIED_REFERENCE_SHA256),
        ("cache_records_sha256", "0" * 64),
        ("public_case_count_per_reference", 6_911),
        ("reference_status", "FAIL"),
    ):
        def swapped_receipt(key: str = field, value: object = wrong) -> None:
            changed = clone(actual_receipt)
            changed[key] = value
            validate_corrected_candidate_context(changed, actual_falsification,
                                                 actual_producer)
        reject("reject-falsified-public-reference-" + field, swapped_receipt)
    for field, wrong in (("records_sha256", FALSIFIED_REFERENCE_SHA256),
                         ("reference_pids", [82, 83]),
                         ("cache_records_sha256", "0" * 64),
                         ("candidate_facing_reference", False)):
        def swapped_producer(key: str = field, value: object = wrong) -> None:
            changed = clone(actual_producer)
            changed["corrected_candidate_context_public_type_reference"][key] = value
            validate_corrected_candidate_context(actual_receipt,
                                                 actual_falsification, changed)
        reject("reject-falsified-v4-reference-" + field, swapped_producer)
    probes = (
        ("unlisted-file", lambda: builtins.open("/etc/hosts", "rb")),
        ("source-mutation", lambda: builtins.open(ROOT + "/" + SOURCE_PATH, "w")),
        ("compressed-archive", lambda: builtins.open(
            ROOT + "/oracle/phase2/evidence/repaired-rust-original-campaign-v10-"
            "rust-phase2-v16-rust-buffer-shape-pickle-original-p0-v10-failures.json.gz", "rb")),
        ("hidden-holdout", lambda: builtins.open(ROOT + "/benchmarks/holdout.json", "rb")),
        ("stdlib-regex", lambda: sys.audit("import", "re", None, None, None, None)),
        ("cpython-matcher", lambda: sys.audit("import", "_sre", None, None, None, None)),
        ("candidate-import", lambda: sys.audit("import", "candidates.rust_candidate",
                                                None, None, None, None)),
        ("native-load", lambda: sys.audit("ctypes.dlopen", "foreign.so")),
        ("compiler", lambda: sys.audit("subprocess.Popen", "rustc", (), None, None)),
        ("network", lambda: sys.audit("socket.__new__", None, 2, 1, 0)),
        ("thread", lambda: sys.audit("threading.Thread.start", None)),
        ("clock", lambda: sys.audit("time.perf_counter")),
        ("temporary-root", lambda: sys.audit("tempfile.mkdtemp", "/tmp/forbidden")),
        ("filesystem-rename", lambda: sys.audit("os.rename", "a", "b", -1, -1)),
        ("archive-inflation", lambda: sys.audit("gzip.decompress", b"forbidden")),
        ("foreign-execution", lambda: sys.audit("exec", "forbidden")),
        ("foreign-compilation", lambda: sys.audit("compile", b"forbidden", "foreign.py")),
    )
    for label, operation in probes:
        reject("physically-block-" + label, operation)
    require(len(rejected) >= 300,
            "exercise the complete hostile owner, phase, process, and effect matrix")
    for category in ("filesystem", "matching_import", "native", "process",
                     "network", "thread", "clock", "temporary", "archive",
                     "dynamic_execution"):
        require(_BLOCKED.get(category, 0) >= 1,
                "exercise the irreversible real-effect audit wall: " + category)
    no_matching_imports()
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS", "version": VERSION,
        "source_sha256": source_pin, "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "accepted_positive_controls": accepted,
        "accepted_positive_control_count": len(accepted),
        "rejected_hostile_controls": len(rejected),
        "blocked_effect_attempts": dict(_BLOCKED),
        "synthetic_control_proof": proof,
        "authenticated_current_graph_version": GRAPH_VERSION,
        "authenticated_owner_count": len(OWNERS),
        "current_history": current_history(),
        "read_only": True,
        **phase_boundary(),
    }


def parse_cli(arguments: list[str]) -> dict[str, object]:
    modes = ("--self-test", "--verify-frozen-context", "--render-contract", "--build")
    selected = [mode for mode in modes if mode in arguments]
    require(len(selected) == 1 and arguments.count(selected[0]) == 1,
            "require one explicit, unambiguous V17 source-only or build mode")
    mode = selected[0]
    values: dict[str, object] = {"mode": mode, "owned_source_sha256": []}
    i = 0
    mapping = {
        "--source-sha256": "source_sha256",
        "--protocol-sha256": "protocol_sha256",
        "--contract-sha256": "contract_sha256",
        "--label": "label",
        "--combined-bridge-sha256": "combined_bridge_sha256",
        "--combined-bridge-bytes": "combined_bridge_bytes",
        "--corrected-adapter-sha256": "corrected_adapter_sha256",
        "--corrected-adapter-bytes": "corrected_adapter_bytes",
        "--phase1-v2-source-sha256": "phase1_v2_source_sha256",
        "--phase1-v2-protocol-sha256": "phase1_v2_protocol_sha256",
        "--phase1-v2-contract-sha256": "phase1_v2_contract_sha256",
    }
    while i < len(arguments):
        item = arguments[i]
        if item == mode:
            i += 1
            continue
        if item == "--owned-source-sha256":
            require(i + 1 < len(arguments), "an owned Rust source pin is incomplete")
            values["owned_source_sha256"].append(arguments[i + 1])
            i += 2
            continue
        require(item in mapping and i + 1 < len(arguments),
                "reject an unknown, abbreviated, or incomplete V17 option")
        name = mapping[item]
        require(name not in values, "reject repeated V17 source authority: " + item)
        value = arguments[i + 1]
        if name.endswith("_bytes"):
            require(value.isascii() and value.isdecimal(),
                    "require exact positive decimal overlay bytes")
            value = int(value)
        values[name] = value
        i += 2
    for name in ("source_sha256", "protocol_sha256"):
        require(name in values, "independently pin the V17 source and protocol")
        checked_hash(values[name], name)
    if mode == "--render-contract":
        require("contract_sha256" not in values,
                "contract rendering cannot assume its own future digest")
    else:
        require("contract_sha256" in values,
                "independently caller-pin the canonical V17 machine contract")
        checked_hash(values["contract_sha256"], "V17 contract")
    build_options = ("label", "combined_bridge_sha256", "combined_bridge_bytes",
                     "corrected_adapter_sha256", "corrected_adapter_bytes",
                     "phase1_v2_source_sha256", "phase1_v2_protocol_sha256",
                     "phase1_v2_contract_sha256")
    if mode == "--build":
        for name in ("phase1_v2_source_sha256", "phase1_v2_protocol_sha256",
                     "phase1_v2_contract_sha256"):
            require(name in values,
                    "future compilation requires an independently corrected P0 V2")
            checked_hash(values[name], name)
        require(values.get("label") == BUILD_LABEL,
                "require the exact fresh authorized V17 evidence label")
        require(values.get("combined_bridge_sha256") == V2_BRIDGE_SHA256
                and values.get("combined_bridge_bytes") == V2_BRIDGE_BYTES
                and values.get("corrected_adapter_sha256") == CORRECTED_ADAPTER_SHA256
                and values.get("corrected_adapter_bytes") == CORRECTED_ADAPTER_BYTES,
                "independently pin both complete reviewed first-party overlays")
        expected_pins = {OWNER_BY_NAME[name][1] + "=" + OWNER_BY_NAME[name][2]
                         for name in RUST_SOURCE_NAMES}
        provided = values["owned_source_sha256"]
        require(type(provided) is list and len(provided) == 9
                and set(provided) == expected_pins,
                "independently caller-pin all nine canonical Rust sources")
    else:
        require(not values["owned_source_sha256"]
                and all(name not in values for name in build_options),
                "source-only modes cannot contain candidate or build authority")
    return values


def read_future_phase_one_owner(relative: str, expected_hash: str) -> bytes:
    checked_hash(expected_hash, "future independently frozen Phase-1 V2 owner")
    require(_WALL_ENABLED is False,
            "source-only verification cannot access future Phase-1 V2 files")
    require(relative in (PHASE_ONE_V2_SOURCE_PATH, PHASE_ONE_V2_PROTOCOL_PATH,
                         PHASE_ONE_V2_CONTRACT_PATH),
            "reject a substituted future Phase-1 reconciliation owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(ROOT + "/" + relative, flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_nlink == 1
                and 0 < before.st_size <= MAX_OWNER_BYTES,
                "future Phase-1 V2 owner is not bounded, exclusive, and genuine")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(262_144, remaining))
            require(type(chunk) is bytes and len(chunk) > 0,
                    "future Phase-1 V2 owner ended before its exact length")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "future Phase-1 V2 owner grew during authentication")
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
                "future Phase-1 V2 owner changed under its read descriptor")
    finally:
        os.close(descriptor)
    result = b"".join(chunks)
    require(digest(result) == expected_hash,
            "the future Phase-1 V2 owner does not match its caller pin")
    return result


def verify_future_phase_one_v2(options: dict[str, object]) -> dict[str, object]:
    require(_WALL_ENABLED is False,
            "a source-only audit wall can never authorize native compilation")
    source = read_future_phase_one_owner(
        PHASE_ONE_V2_SOURCE_PATH, options["phase1_v2_source_sha256"],
    )
    protocol = read_future_phase_one_owner(
        PHASE_ONE_V2_PROTOCOL_PATH, options["phase1_v2_protocol_sha256"],
    )
    contract_raw = read_future_phase_one_owner(
        PHASE_ONE_V2_CONTRACT_PATH, options["phase1_v2_contract_sha256"],
    )
    contract = StrictJSON(contract_raw).decode()
    require(type(contract) is dict and contract.get("version") == 2
            and contract.get("schema") in (
                "rebar-cpython-re-p0-completeness-v2",
                "rebar-phase1-owned-p0-completeness-v2-source-freeze",
            ) and contract.get("status") == "PASS",
            "future compilation requires a genuinely passing Phase-1 V2 crosswalk")
    source_owner = contract.get("source")
    protocol_owner = contract.get("protocol")
    require(type(source_owner) is dict and type(protocol_owner) is dict
            and source_owner.get("path") == PHASE_ONE_V2_SOURCE_PATH
            and source_owner.get("sha256") == options["phase1_v2_source_sha256"]
            and source_owner.get("bytes") == len(source)
            and protocol_owner.get("path") == PHASE_ONE_V2_PROTOCOL_PATH
            and protocol_owner.get("sha256") == options["phase1_v2_protocol_sha256"]
            and protocol_owner.get("bytes") == len(protocol),
            "future Phase-1 V2 source and explanation must bind their own digest")
    oracle = contract.get("original_oracle")
    reference = contract.get("corrected_candidate_context_public_type_reference")
    crosswalk = contract.get("phase1_canonical_candidate_context_crosswalk")
    require(type(oracle) is dict and type(reference) is dict
            and crosswalk == "PASS"
            and oracle.get("case_execution_denominator") == 31_237
            and oracle.get("suite_count") == 13
            and oracle.get("named_private_waiver_count") == 13
            and reference.get("reference_pids") == [81, 82]
            and reference.get("case_count") == 6_912
            and reference.get("records_sha256") == CORRECTED_REFERENCE_SHA256
            and reference.get("cache_records_sha256") == CORRECTED_CACHE_SHA256
            and reference.get("candidate_facing_reference") is True,
            "reject a missing, stale, falsified, or incomplete Phase-1 V2 reference")
    return contract


def run_build(options: dict[str, object]) -> dict[str, object]:
    require(options.get("mode") == "--build"
            and options.get("label") == BUILD_LABEL,
            "native compilation requires an explicit uniquely labeled V17 build")
    verify_future_phase_one_v2(options)
    context, state = collect_context(
        options["source_sha256"], options["protocol_sha256"],
        options["contract_sha256"],
    )
    require(_WALL_ENABLED is False,
            "an irreversible source-only wall cannot authorize a native build")
    import types

    raw = state["owners"]["v16_builder"]
    require(digest(raw) == OWNER_BY_NAME["v16_builder"][2],
            "load only the exact historically audited V16 native build recorder")
    module_name = "_rebar_v17_explicit_authorized_v16_kernel"
    require(module_name not in sys.modules,
            "reject a reused or substituted first-party build recorder")
    module = types.ModuleType(module_name)
    module.__file__ = ROOT + "/" + OWNER_BY_NAME["v16_builder"][1]
    sys.modules[module_name] = module
    try:
        exec(compile(raw, module.__file__, "exec", dont_inherit=True),
             module.__dict__)
        require(module.SCHEMA == "rebar-phase2-owned-rust-buffer-shape-source-build-v16"
                and module.VERSION == 16 and module.FAMILY == FAMILY
                and module.PHASES == PHASES
                and module.PROCESS_NAMES == PROCESS_NAMES
                and module.ROOT_PREFIX == ROOT_PREFIX,
                "reject an unaudited, changed, or wrong-prefix native build kernel")
        module.SCHEMA = SCHEMA
        module.VERSION = VERSION
        module.SOURCE_PATH = SOURCE_PATH
        module.PROTOCOL_PATH = PROTOCOL_PATH
        module.CONTRACT_PATH = CONTRACT_PATH
        module.FINAL_GRAPH_VERSION = GRAPH_VERSION
        module.CURRENT_EVIDENCE_OWNER_LOWER_BOUND = EVIDENCE_FLOOR
        module.CURRENT_HISTORY_REFERENCE_LOWER_BOUND = HISTORY_FLOOR
        module.COMBINED_VARIANT = module.Owner(
            OWNER_BY_NAME["v2_variant"][1], V2_BRIDGE_SHA256, V2_BRIDGE_BYTES,
        )
        module.BUFFER_VARIANT = module.COMBINED_VARIANT
        module.BUFFER_FEATURE = tuple(
            module.Owner(OWNER_BY_NAME[name][1], OWNER_BY_NAME[name][2],
                         OWNER_BY_NAME[name][3])
            for name in ("v2_repair", "v2_protocol", "v2_contract")
        )
        module.FINAL_GRAPH = tuple(
            module.Owner(OWNER_BY_NAME[name][1], OWNER_BY_NAME[name][2],
                         OWNER_BY_NAME[name][3])
            for name in ("graph_renderer", "graph_inputs", "graph_summary", "graph_chart")
        )

        def verified_v17_context(source_pin: str, protocol_pin: str,
                                 contract_pin: str) -> tuple[dict[str, object],
                                                              dict[str, object]]:
            require((source_pin, protocol_pin, contract_pin)
                    == (options["source_sha256"], options["protocol_sha256"],
                        options["contract_sha256"]),
                    "do not substitute V17 source-only authorization")
            return context, {
                "originals": state["originals"],
                "combined_bridge": state["combined_bridge"],
                "corrected_adapter": state["corrected_adapter"],
                "low_level_v9_source": state["low_level_v9_source"],
            }

        def evidence_names(label: str, failed: bool) -> tuple[str, str]:
            require(label == BUILD_LABEL and type(failed) is bool,
                    "require a fresh V17-only durable build outcome")
            stem = "native-source-build-v17-rust-" + label
            if failed:
                stem += "-failures"
            return stem + ".json.gz", stem + "-publication-receipt.json"

        original_verifier = module.verify_reproduced_phases

        def verify_actual_phases(v9: object, v7: object, workdir: str,
                                 phases: list[object], steps: list[object]) -> object:
            require(type(steps) is list and len(steps) == 28,
                    "require exactly 28 authentic offline compiler records")
            process_ids: set[int] = set()
            for index, entry in enumerate(steps):
                phase = PHASES[index // len(PROCESS_NAMES)]
                require(type(entry) is dict
                        and entry.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                        and ("phase" not in entry or entry.get("phase") == phase)
                        and type(entry.get("pid")) is int and entry["pid"] > 0
                        and entry["pid"] not in process_ids
                        and entry.get("exit_status") == 0
                        and entry.get("working_directory")
                        == "<FRESH_PRIVATE_TMP>/" + phase,
                        "reject an invented, misplaced, failed, or duplicate build process")
                process_ids.add(entry["pid"])
            return original_verifier(v9, v7, workdir, phases, steps)

        module.verify_frozen_context = verified_v17_context
        module.evidence_names = evidence_names
        module.verify_reproduced_phases = verify_actual_phases

        class Options:
            pass

        forwarded = Options()
        for name in ("source_sha256", "protocol_sha256", "contract_sha256",
                     "owned_source_sha256", "combined_bridge_sha256",
                     "combined_bridge_bytes", "corrected_adapter_sha256",
                     "corrected_adapter_bytes", "label"):
            setattr(forwarded, name, options[name])
        result = module.run_build(forwarded)
        require(type(result) is dict and result.get("family") == FAMILY,
                "the explicit V17 build did not produce a genuine durable outcome")
        return result
    finally:
        sys.modules.pop(module_name, None)


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.executable == PYTHON
            and sys.flags.isolated and sys.dont_write_bytecode,
            "use the isolated, pinned CPython 3.14.6 source-only oracle")


def main() -> int:
    try:
        verify_runtime()
        options = parse_cli(list(sys.argv[1:]))
        mode = options["mode"]
        if mode != "--build":
            install_wall()
        if mode == "--render-contract":
            _context, state = collect_context(
                options["source_sha256"], options["protocol_sha256"],
            )
            result = contract_document(options["source_sha256"],
                                       options["protocol_sha256"], state)
        elif mode == "--verify-frozen-context":
            result, _state = collect_context(
                options["source_sha256"], options["protocol_sha256"],
                options["contract_sha256"],
            )
        elif mode == "--self-test":
            result = self_test(options["source_sha256"],
                               options["protocol_sha256"],
                               options["contract_sha256"])
        else:
            result = run_build(options)
        encoded = (canonical(result) + "\n").encode("ascii")
        require(0 < len(encoded) <= MAX_OWNER_BYTES,
                "bound each complete canonical V17 source result")
        sys.stdout.buffer.write(encoded)
        sys.stdout.buffer.flush()
        return 0 if mode == "--render-contract" or result.get("status") == "PASS" else 1
    except (GateError, OSError, UnicodeError, ValueError, TypeError,
            KeyError, AttributeError, SyntaxError, RecursionError,
            OverflowError) as error:
        failure = {
            "schema": SCHEMA + "-entry-failure", "status": "FAIL",
            "error_type": type(error).__name__,
            "error_message": str(error)[:8192],
            "actual_candidate_workers_started": 0,
            "actual_compiler_process_count": 0,
            "candidate_matching": "NOT RUN",
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False,
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "winner_selected": False,
        }
        sys.stdout.buffer.write((canonical(failure) + "\n").encode("ascii"))
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
