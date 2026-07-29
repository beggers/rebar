#!/usr/bin/env python3
"""Run frozen original regex cases only after binding a first-party matcher.

This module's bootstrap deliberately does not import argparse, json, pathlib,
typing, unittest, or any other module that can preload ``re`` or ``_sre``.
The immutable V4 producer is a historical input, never a candidate observer.
"""

from __future__ import annotations

import builtins
import hashlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
SOURCE_RELATIVE = "tools/run_owned_six_family_original_p0_producer_v5.py"
PROTOCOL_RELATIVE = "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md"
DOCUMENT_RELATIVE = "oracle/phase2/six-family-p0-producer-v5.json"
SCHEMA = "rebar-owned-six-family-original-p0-producer-v5"
CONTRACT_SCHEMA = SCHEMA + "-source-freeze"
PINNED_PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PINNED_PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
SUITE_COUNT = 13
CASE_DENOMINATOR = 31237
PRIVATE_WAIVER_COUNT = 13
ORIGINAL_OBLIGATION_COUNT = 73
ORIGINAL_CROSSWALK_COUNT = 34
ORIGINAL_PUBLIC_RECORD_COUNT = 152
ORIGINAL_DEBUG_SKIP_COUNT = 1
PRIVATE_WAIVER_NAMES = (
    "DebugTests.test_debug_flag",
    "DebugTests.test_atomic_group",
    "DebugTests.test_possesive_repeat_one",
    "DebugTests.test_possesive_repeat",
    "ImplementationTest.test_immutable",
    "ImplementationTest.test_overlap_table",
    "ImplementationTest.test_signedness",
    "ImplementationTest.test_disallow_instantiation",
    "ImplementationTest.test_deprecated_modules",
    "ImplementationTest.test_case_helpers",
    "ImplementationTest.test_dealloc",
    "ImplementationTest.test_repeat_minmax_overflow_maxrepeat",
    "ImplementationTest.test_sre_template_invalid_group_index",
)
SUPPLEMENTAL_CASE_COUNT = 8244
NESTED_CASE_COUNT = 128
NESTED_CASE_EXECUTIONS = 394
NESTED_INTERPRETER_COUNT = 11
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_JSON_BYTES = 4 * 1024 * 1024
MAX_BINARY_BYTES = 256 * 1024 * 1024
EXTENSION_SUFFIX = ".cpython-314-x86_64-linux-gnu.so"
RUNTIME_GUARD_SOURCE = "tools/verify_owned_candidate_runtime_independence_v2.py"
RUNTIME_GUARD_PROTOCOL = "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md"
RUNTIME_GUARD_CONTRACT = "oracle/phase2/candidate-runtime-independence-v2.json"
CORRECTED_PUBLIC_RECORDS_SHA256 = "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2"
CORRECTED_PUBLIC_COHORT_RECORDS_SHA256 = "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad"
CORRECTED_PUBLIC_REFERENCE_PIDS = (81, 82)
UPSTREAM_TEST = "/tmp/rebar-cpython/cpython-3.14.6-upstream-source/Python-3.14.6/Lib/test/test_re.py"
UPSTREAM_SHA256 = "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2"

P0_OWNERS = (
    ("tools/verify_owned_p0_completeness_v4.py", "8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d", 29094, 428927),
    ("oracle/phase1/P0-COMPLETENESS-V4.md", "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2", 4261, 524712),
    ("oracle/phase1/p0-completeness-v4.json", "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
)
V4_OWNERS = (
    ("tools/run_owned_six_family_original_p0_producer_v4.py", "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8", 230782, 431710),
    ("oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md", "e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5", 5981, 524782),
    ("oracle/phase2/six-family-p0-producer-v4.json", "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5", 30867, 524783),
)
GRAPH_OWNERS = (
    ("tools/render_candidate_current_overview_v75.py", "0610a7ba73f13eec6c9e59d766971568581b056cb54057b8dbaa95798d0c78fe", 44198, 431363),
    ("docs/evidence/candidate-current-overview-v75.inputs.json", "5a3d9eed1e46b941c5456ff601ce04167b4d451c25ff07d9a6a2279ea54689cb", 1164810, 431399),
    ("docs/evidence/candidate-current-overview-v75.json", "a8214d808a1edf13ba2afb6181864133415751bdaaa7e384f72a1699ad805f5f", 3355331, 431400),
    ("docs/evidence/candidate-current-overview-v75.svg", "62763a4668c3ccbafbb0aed4e2c22533c6bf830d0e76c0ea3bb3883aa0bfb37f", 4897, 431401),
)
HARNESS_OWNER = ("tools/rust_original_cpython_suite_v1.py", "cf0267e3766fb849891d182e5b57ced569a0634831dd494d8135e703844b6c95", 67175, 430765)
ORIGINAL_EVALUATOR_OWNER = ("tools/independent_original_cpython_suite_v5.py", "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce", 123750, 431594)
DIRECT_GATE_OWNER = ("tools/run_frozen_p0_candidate_v1.py", "c8378cd59a3b4dfaf75609c5b06f5a5ec20114d428e8e06ccc0f12ceec2076b8", 104772, 432295)
NESTED_OWNER = ("tools/run_owned_candidate_subinterpreters_v1.py", "45e9b47c7c635fc30ebdb2cb4830d2d1fe382a5a7e4b663fb1a8e0112779e1a7", 190460, 432320)
RUNTIME_GUARD_V2_OWNERS = (
    ("tools/verify_owned_candidate_runtime_independence_v2.py", "f693b1576b63ae5ebe45663801834c05e7d03671a5d6f2b4beb1b62034d37c0a", 67097, 431371),
    ("oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md", "2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c", 4437, 524886),
    ("oracle/phase2/candidate-runtime-independence-v2.json", "813bbab0898d5a65a6b43533f7bfa024c4c215609c4f9fa6eb0f4cbe2791f473", 7671, 524887),
)


class ProducerError(Exception):
    """A frozen input, candidate identity, or original observation failed."""


class ActualSuiteFailure(ProducerError):
    def __init__(self, message: str, details: object) -> None:
        super().__init__(message)
        self.details = details


def require(condition: object, message: str) -> None:
    if not condition:
        raise ProducerError(message)


def quote(value: str) -> str:
    out = ['"']
    table = {"\\": "\\\\", '"': '\\"', "\b": "\\b", "\f": "\\f", "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    for character in value:
        if character in table:
            out.append(table[character])
        elif ord(character) < 32:
            out.append("\\u" + format(ord(character), "04x"))
        elif ord(character) > 127:
            encoded = character.encode("utf-16-be", "surrogatepass")
            for index in range(0, len(encoded), 2):
                out.append("\\u" + format(int.from_bytes(encoded[index:index + 2], "big"), "04x"))
        else:
            out.append(character)
    out.append('"')
    return "".join(out)


def canonical(value: object) -> bytes:
    def encode(item: object, depth: int) -> str:
        require(depth <= 64, "reject excessive canonical nesting")
        if item is None:
            return "null"
        if item is True:
            return "true"
        if item is False:
            return "false"
        if type(item) is int:
            return str(item)
        if type(item) is str:
            return quote(item)
        if type(item) in (tuple, list):
            return "[" + ",".join(encode(child, depth + 1) for child in item) + "]"
        if type(item) is dict:
            require(all(type(key) is str for key in item), "reject non-string canonical keys")
            return "{" + ",".join(quote(key) + ":" + encode(item[key], depth + 1) for key in sorted(item)) + "}"
        raise ProducerError("reject non-canonical value: " + type(item).__name__)
    return (encode(value, 0) + "\n").encode("ascii")


class JsonReader:
    """Decode bounded evidence without importing ``json`` and its ``re``."""

    def __init__(self, raw: bytes) -> None:
        require(type(raw) is bytes and 0 < len(raw) <= MAX_JSON_BYTES, "reject absent or oversized JSON")
        self.text = raw.decode("utf-8", "strict")
        self.index = 0

    def whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def string(self) -> str:
        require(self.index < len(self.text) and self.text[self.index] == '"', "require a JSON string")
        self.index += 1
        pieces: list[str] = []
        escaped = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
        while self.index < len(self.text):
            item = self.text[self.index]
            self.index += 1
            if item == '"':
                return "".join(pieces)
            require(ord(item) >= 32, "reject JSON control character")
            if item != "\\":
                pieces.append(item)
                continue
            require(self.index < len(self.text), "reject truncated JSON escape")
            item = self.text[self.index]
            self.index += 1
            if item == "u":
                digits = self.text[self.index:self.index + 4]
                require(len(digits) == 4 and all(ch in "0123456789abcdefABCDEF" for ch in digits), "reject invalid unicode escape")
                self.index += 4
                value = int(digits, 16)
                if 0xD800 <= value <= 0xDBFF:
                    require(self.text[self.index:self.index + 2] == "\\u", "reject unpaired JSON high surrogate")
                    self.index += 2
                    tail = self.text[self.index:self.index + 4]
                    require(len(tail) == 4 and all(ch in "0123456789abcdefABCDEF" for ch in tail), "reject invalid low surrogate")
                    low = int(tail, 16)
                    require(0xDC00 <= low <= 0xDFFF, "reject unpaired JSON high surrogate")
                    self.index += 4
                    pieces.append(chr(0x10000 + ((value - 0xD800) << 10) + low - 0xDC00))
                else:
                    require(not 0xDC00 <= value <= 0xDFFF, "reject unpaired JSON low surrogate")
                    pieces.append(chr(value))
            else:
                require(item in escaped, "reject invalid JSON escape")
                pieces.append(escaped[item])
        raise ProducerError("reject unterminated JSON string")

    def value(self, depth: int = 0) -> object:
        require(depth <= 64, "reject excessive JSON nesting")
        self.whitespace()
        require(self.index < len(self.text), "reject missing JSON value")
        first = self.text[self.index]
        if first == '"':
            return self.string()
        if first == "{":
            self.index += 1
            result: dict[str, object] = {}
            self.whitespace()
            if self.index < len(self.text) and self.text[self.index] == "}":
                self.index += 1
                return result
            while True:
                self.whitespace()
                key = self.string()
                require(key not in result, "reject duplicate JSON key: " + key)
                self.whitespace()
                require(self.index < len(self.text) and self.text[self.index] == ":", "reject missing JSON colon")
                self.index += 1
                result[key] = self.value(depth + 1)
                self.whitespace()
                require(self.index < len(self.text), "reject unterminated JSON object")
                mark = self.text[self.index]
                self.index += 1
                if mark == "}":
                    return result
                require(mark == ",", "reject malformed JSON object")
        if first == "[":
            self.index += 1
            result_list: list[object] = []
            self.whitespace()
            if self.index < len(self.text) and self.text[self.index] == "]":
                self.index += 1
                return result_list
            while True:
                result_list.append(self.value(depth + 1))
                self.whitespace()
                require(self.index < len(self.text), "reject unterminated JSON array")
                mark = self.text[self.index]
                self.index += 1
                if mark == "]":
                    return result_list
                require(mark == ",", "reject malformed JSON array")
        for literal, item in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(literal, self.index):
                self.index += len(literal)
                return item
        begin = self.index
        if first == "-":
            self.index += 1
        require(self.index < len(self.text) and self.text[self.index] in "0123456789", "reject non-integral JSON number")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index == len(self.text) or self.text[self.index] not in "0123456789", "reject leading zero")
        else:
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
        return int(self.text[begin:self.index])

    def parse(self) -> object:
        value = self.value()
        self.whitespace()
        require(self.index == len(self.text), "reject trailing JSON content")
        return value


class SuiteSpec:
    __slots__ = ("name", "case_count", "source_relative", "source_sha256", "matrix_sha256", "reference_sha256", "seed", "route")

    def __init__(self, name: str, case_count: int, source_relative: str, source_sha256: str, matrix_sha256: str, reference_sha256: str, seed: int | None, route: str) -> None:
        self.name, self.case_count = name, case_count
        self.source_relative, self.source_sha256 = source_relative, source_sha256
        self.matrix_sha256, self.reference_sha256 = matrix_sha256, reference_sha256
        self.seed, self.route = seed, route


class FamilySpec:
    __slots__ = ("name", "module", "adapter_relative", "bridge_module", "engine_relative", "bridge_relative", "source_owners", "combined_native", "owned_ctypes")

    def __init__(self, name: str, module: str, adapter_relative: str, bridge_module: str, engine_relative: str, bridge_relative: str, source_owners: tuple, combined_native: bool, owned_ctypes: bool) -> None:
        self.name, self.module, self.adapter_relative = name, module, adapter_relative
        self.bridge_module, self.engine_relative, self.bridge_relative = bridge_module, engine_relative, bridge_relative
        self.source_owners, self.combined_native, self.owned_ctypes = source_owners, combined_native, owned_ctypes


SUITES = (
    SuiteSpec("original_bounded_v5", 151, "tools/independent_original_cpython_suite_v5.py", "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce", "93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240", "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276", None, "unchanged-165-method-upstream-source"),
    SuiteSpec("public_v3", 864, "tools/rust_public_practice_benchmark_v1.py", "d74932c13bdda64e1340c958cbea48d65db36531b849e202dfc16170de150b37", "367d30517874745b11d6facf43685a906784dc94c0246dc6a6381c17afcc776e", "0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c", 5928217332825411633, "unchanged-public-source-evaluator"),
    SuiteSpec("scanner_v3", 1024, "tools/rust_scanner_differential_v1.py", "fcc82a76e7bcaaa25d92a8482d4dc611b643d887d7fd983db0906c7340b91fd7", "83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c", "37de08e1991adf28990e35b72c2130ebafa78c72b04750d28550cce08555666d", 5999710933164053041, "unchanged-scanner-and-callback-evaluator"),
    SuiteSpec("buffer_v3", 768, "tools/rust_memoryview_expand_differential_v1.py", "226f129f0e90b060c977e599e6e8369f5a5285890089c69108b718cfcb2980e6", "b40fb92f42c7019a73eec72800077f262f1a6be516886a6ddda372e24807eb60", "8312263785cd49f7283ab8c6fac13443befe9c5a3d739b2e068aebdcf3f59b75", 5567953616029762609, "unchanged-memoryview-evaluator"),
    SuiteSpec("managed_v1", 1024, "tools/independent_managed_buffer_lifetime_v1.py", "cedbab1227ea58a97d407cb339d2959a9f9be58a2085ce3106b65bb3385de489", "28ef84b6989542ba8865c98e5296639c780c786078e2a99c7c0a95bfcb4b0976", "80293f5332300220f38c3f017d38611a5514b1b686918e692a53491945b196df", 5567095966978627121, "unchanged-real-buffer-lifetime-evaluator"),
    SuiteSpec("scanner_verbose_v1", 2854, "tools/independent_scanner_verbose_comments_v1.py", "5508910eae3f5e59d2013bc9fa4f1a8948a823e27de09bf416de2fffc8e91c9d", "01bca287cd481a5e4ae134b910911e2e2f8f1501eebb7ffd2947092ab170d17b", "d7e2d499eb4dbe6ae0f8743d8b152e4835898656daa8b3167598636ef7be6012", 5999725261024810545, "unchanged-verbose-tokenizer-evaluator"),
    SuiteSpec("public_types_v1", 6912, "tools/independent_public_type_identity_serialization_v1.py", "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20", "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123", CORRECTED_PUBLIC_RECORDS_SHA256, 6077977430793212465, "unchanged-public-type-and-pickle-evaluator"),
    SuiteSpec("substitution_v2", 5120, "tools/independent_substitution_buffer_semantics_v2.py", "e7cc951b4fbb90b2826c3730bbb3b3e81b50e8a5eac8a3d758962358d9414573", "26f46fe7f1abc5135d1265a7882ccd4a2e2b45cdec80ba293520fda510235b54", "2bc65461b9ac60fd19a3c66856bd33ee48db038ab6a5de62193837800840f61b", 6004778603531028017, "unchanged-substitution-and-callback-evaluator"),
    SuiteSpec("shape_v2", 10240, "tools/independent_shape_changing_buffer_semantics_v2.py", "0262807f793a818307f2c8c6ecfd84bf970264a6ef5d656acf30c9d3606f0e2c", "10fe3e3fd4b4650bff1da6a745b5b883f01033ed14df3f9795aa2f7a30c6d8d8", "58bbc78828ba2d4cde6b99cbebea815ce9381cda24d0acec03f6cc095b8b643c", 6001118316486346290, "unchanged-real-changing-buffer-evaluator"),
    SuiteSpec("public_surface_v19", 1376, "tools/python_re_public_surface_oracle_stage19.py", "fda386f3c00be660a41e92d8005fc287706d9dc050967cf2b708cb6f8aba113e", "7885a9ac0b2e22db88db7dc4ab9c33c4ba229ddb6d15fcdd4bfe9b0d6f10e8aa", "c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef", 2026072483, "unchanged-real-64-locale-and-192-transition-evaluator"),
    SuiteSpec("subinterpreter_v2", 128, "tools/python_re_subinterpreter_oracle_v2.py", "54735efb77a099feb2dd076723d3a93d81415226b9b9213307c32cc0f38c52c8", "edda77658c5eef9746c6d4769734c69e40db4c9d986171fa63799093f4cb62d3", "450fccc859099ca78aec725911b6195695cd932ad281af931ca7945cec8c51e8", 2026072501, "unchanged-real-128-case-394-call-11-interpreter-lifecycle"),
    SuiteSpec("pep688_v4", 264, "tools/python_re_buffer_exporter_oracle_v4.py", "8da0b8e5c5519e7335cd1b53ceb7042f1da1f902c486ad8ac35ddf53d8a04490", "2d9eb4e637387bc89020d2f883f59ff03dd98cbebd2f2aaa2a30dc55d0836891", "7827586e0c7d4f43ac1fbd288f6b28f6a44b810b46274830d3803505c76692a8", None, "unchanged-real-python-buffer-exporter-evaluator"),
    SuiteSpec("threaded_pattern_v1", 512, "tools/python_re_threaded_pattern_oracle_v1.py", "05226e59736d8721a975eda8afa10247213999690c2766a7b3235c567b9f8276", "a7d467e3e529204946fe00ddb819e734421e7087ea909af9ec24b757e42afa0b", "928ea100d6fdaecc7c1dcf01e32c24fd98a146964c0955989a8149c1216ffe81", 2026072701, "unchanged-real-barrier-synchronized-shared-pattern-threads"),
)

OWNED_SOURCES = {
    "c": (("candidates/vm_candidate.py", "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096", 60707), ("candidates/_vm_native.c", "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55", 218185)),
    "rust": (("candidates/rust_candidate.py", "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151), ("candidates/rust/py_bridge.c", "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676), ("candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225), ("candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167), ("candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967), ("candidates/rust/src/newline.rs", "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416), ("candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773), ("candidates/rust/src/stack.rs", "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269), ("candidates/rust/src/unicode_tables.rs", "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989)),
    "zig": (("candidates/zig_candidate.py", "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862", 68422), ("candidates/zig/mini_regex.zig", "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28", 186915), ("candidates/zig/py_bridge.c", "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b", 173026)),
    "cpp": (("candidates/cpp_candidate.py", "8dcece29b1a194eea023143148af37bb679a9df4c39c01153f5ee23f778e16d5", 27488), ("candidates/cpp/engine.hpp", "66998fed1839f5e5f7f09382830ed9fda1a62b80bd545305c4eee95ed9a13df9", 4089), ("candidates/cpp/engine.cpp", "a9ceb37cfde77447a01a36a8882f7713faf5f201d7a15a193dd17e7b91d118f5", 62813), ("candidates/cpp/py_bridge.cpp", "1d930b63b2f9493dd4759b7521f75d8846daf2580a5699337fcf82540484ab6d", 25068)),
    "go": (("candidates/go_candidate.py", "816d21527b9806afbc9457122f72f8f6b62c39b8b791d3f363745d412cbe3d20", 31049), ("candidates/go/go.mod", "9297c4e8fe4649196150400d23a4da584d7ef721347f7095399a7382edad669b", 44), ("candidates/go/engine.go", "6472c4413921f3a877455315400c532e7632a871a96d46de9583fa6170a43192", 53782), ("candidates/go/py_bridge.c", "52101f0afe29a568e3c2e22a06d47c89c051e08a0e2024ad4891c5ae2d60fb6a", 39373)),
    "fortran": (("candidates/fortran_candidate.py", "8db564771d38c0896a5207f1241a44463432dc5bf75dfcf657740d8bcfefd194", 26521), ("candidates/fortran/engine.f90", "5180da085487b9932e3f769e6baded6a8409a0b778890e6197aaea6dad1923a5", 85062), ("candidates/fortran/py_bridge.c", "8540b708de4819f1b3340c32e78eaf083c1cad35f016c0f7af33a27773694b0d", 26311)),
}

FAMILIES = {
    "rust": FamilySpec("rust", "candidates.rust_candidate", "candidates/rust_candidate.py", "candidates._rust_bridge", "candidates/_rust_engine.so", "candidates/_rust_bridge" + EXTENSION_SUFFIX, OWNED_SOURCES["rust"], False, False),
    "c": FamilySpec("c", "candidates.vm_candidate", "candidates/vm_candidate.py", "candidates._vm_native", "candidates/_vm_native" + EXTENSION_SUFFIX, "candidates/_vm_native" + EXTENSION_SUFFIX, OWNED_SOURCES["c"], True, False),
    "zig": FamilySpec("zig", "candidates.zig_candidate", "candidates/zig_candidate.py", "candidates._zig_bridge", "candidates/_zig_probe.so", "candidates/_zig_bridge" + EXTENSION_SUFFIX, OWNED_SOURCES["zig"], False, True),
    "cpp": FamilySpec("cpp", "candidates.cpp_candidate", "candidates/cpp_candidate.py", "candidates._cpp_bridge", "candidates/_cpp_bridge" + EXTENSION_SUFFIX, "candidates/_cpp_bridge" + EXTENSION_SUFFIX, OWNED_SOURCES["cpp"], True, False),
    "go": FamilySpec("go", "candidates.go_candidate", "candidates/go_candidate.py", "candidates._go_bridge", "candidates/_go_engine.so", "candidates/_go_bridge" + EXTENSION_SUFFIX, OWNED_SOURCES["go"], False, False),
    "fortran": FamilySpec("fortran", "candidates.fortran_candidate", "candidates/fortran_candidate.py", "candidates._fortran_bridge", "candidates/_fortran_engine.so", "candidates/_fortran_bridge" + EXTENSION_SUFFIX, OWNED_SOURCES["fortran"], False, False),
}


def valid_digest(value: object) -> bool:
    return type(value) is str and len(value) == 64 and len(set(value)) > 1 and all(item in "0123456789abcdef" for item in value)


def read_owner(owner: tuple, *, maximum: int = MAX_SOURCE_BYTES) -> bytes:
    relative, expected, size, inode = owner
    require(type(relative) is str and not relative.startswith("/") and ".." not in relative.split("/") and valid_digest(expected) and type(size) is int and 0 < size <= maximum and type(inode) is int and inode > 0, "reject unbounded or substituted owner")
    descriptor = os.open(ROOT + "/" + relative, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and before.st_dev == 2064 and before.st_ino == inode and before.st_size == size and before.st_nlink == 1 and before.st_uid == os.geteuid() and stat.S_IMODE(before.st_mode) == 0o600, "reject owner inode, device, permissions, or size: " + relative)
        chunks: list[bytes] = []
        left = size
        while left:
            chunk = os.read(descriptor, min(left, 262144))
            require(bool(chunk), "reject truncated owner: " + relative)
            chunks.append(chunk)
            left -= len(chunk)
        require(not os.read(descriptor, 1), "reject expanded owner: " + relative)
        after = os.fstat(descriptor)
        raw = b"".join(chunks)
        require(hashlib.sha256(raw).hexdigest() == expected and (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns, before.st_nlink) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns, after.st_nlink), "reject modified owner: " + relative)
        return raw
    finally:
        os.close(descriptor)


def read_self(relative: str, expected: str, *, maximum: int = MAX_SOURCE_BYTES) -> bytes:
    require(relative in (SOURCE_RELATIVE, PROTOCOL_RELATIVE, DOCUMENT_RELATIVE) and valid_digest(expected), "require an exact version-five owner")
    path = ROOT + "/" + relative
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and before.st_dev == 2064 and before.st_uid == os.geteuid() and before.st_nlink == 1 and stat.S_IMODE(before.st_mode) == 0o600 and 0 < before.st_size <= maximum, "reject substituted V5 owner: " + relative)
        raw = b""
        while len(raw) < before.st_size:
            part = os.read(descriptor, min(262144, before.st_size - len(raw)))
            require(bool(part), "reject truncated V5 owner: " + relative)
            raw += part
        require(not os.read(descriptor, 1), "reject extended V5 owner: " + relative)
        after = os.fstat(descriptor)
        require(hashlib.sha256(raw).hexdigest() == expected and (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns, before.st_nlink) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns, after.st_nlink), "reject changed V5 owner: " + relative)
        return raw
    finally:
        os.close(descriptor)


def load_module(owner: tuple, name: str) -> types.ModuleType:
    raw = read_owner(owner)
    require(type(name) is str and name.startswith("_rebar_v5_"), "require an isolated authenticated source module")
    module = types.ModuleType(name)
    module.__file__ = ROOT + "/" + owner[0]
    module.__package__ = ""
    previous = sys.modules.get(name)
    require(previous is None, "reject an already-loaded frozen evaluator")
    sys.modules[name] = module
    try:
        exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def suite_spec(value: object) -> SuiteSpec:
    require(type(value) is str, "require one named frozen original suite")
    matches = [item for item in SUITES if item.name == value]
    require(len(matches) == 1, "reject an unknown or repeated original suite")
    return matches[0]


def family_spec(value: object) -> FamilySpec:
    require(type(value) is str and value in FAMILIES, "reject a missing or external regex family")
    return FAMILIES[value]


def require_selected(spec: FamilySpec) -> types.ModuleType:
    module = sys.modules.get("re")
    bridge = sys.modules.get(spec.bridge_module)
    require(type(module) is types.ModuleType and module is sys.modules.get(spec.module) and module.__name__ == spec.module and type(bridge) is types.ModuleType and bridge.__name__ == spec.bridge_module and "_sre" not in sys.modules and all(name == spec.module or not name.startswith("candidates.") or name == spec.bridge_module for name in sys.modules), "require the exact selected first-party matcher and native bridge and no CPython or alternate regex engine")
    constants = sys.modules.get("re._constants")
    require(type(constants) is types.ModuleType and getattr(constants, "MAXGROUPS", None) == 1073741823 and not any(name in sys.modules for name in ("re._compiler", "re._parser", "sre_compile", "sre_parse", "regex", "re2")), "require only the data-only upstream regex constants")
    return module


def active_runtime_policy(spec: FamilySpec) -> object:
    """Find the physically installed, selected, irreversible audit guard."""
    candidate = require_selected(spec)
    matches = [
        item for item in sys.meta_path
        if getattr(item, "installed", False) is True
        and getattr(item, "selected", None) is candidate
        and getattr(item, "selected_family", None) == spec.module
        and callable(getattr(item, "check_modules", None))
        and callable(getattr(item, "prepare_family", None))
    ]
    require(len(matches) == 1, "require one physically installed version-two candidate runtime guard")
    policy = matches[0]
    require(getattr(policy, "constants", None) is sys.modules.get("re._constants"), "reject a guard with substituted data-only original constants")
    policy.check_modules()
    return policy


def active_guard_child_bootstrap(policy: object) -> tuple[object, dict]:
    """Recover only the exact source-authenticated V2 child bootstrap."""
    implementation = getattr(type(policy), "prepare_family", None)
    require(
        callable(implementation) and getattr(policy, "installed", False) is True,
        "reject an uninstalled or unowned operational version-two guard",
    )
    namespace = getattr(implementation, "__globals__", None)
    require(
        type(namespace) is dict
        and namespace.get("SELF") == RUNTIME_GUARD_SOURCE
        and namespace.get("PROTOCOL") == RUNTIME_GUARD_PROTOCOL
        and namespace.get("CONTRACT") == RUNTIME_GUARD_CONTRACT,
        "reject an unrelated or substituted runtime guard namespace",
    )
    child = namespace.get("child_bootstrap_source")
    require(callable(child), "require the exact authenticated guard-first child bootstrap")
    source_raw = read_owner(RUNTIME_GUARD_V2_OWNERS[0])
    read_owner(RUNTIME_GUARD_V2_OWNERS[1])
    raw = read_owner(RUNTIME_GUARD_V2_OWNERS[2], maximum=MAX_JSON_BYTES)
    source = owner_record(RUNTIME_GUARD_V2_OWNERS[0])
    protocol = owner_record(RUNTIME_GUARD_V2_OWNERS[1])
    contract = owner_record(RUNTIME_GUARD_V2_OWNERS[2])
    document = JsonReader(raw).parse()
    require(
        type(document) is dict
        and document.get("schema") == "rebar-owned-candidate-runtime-independence-v2-source-freeze"
        and document.get("version") == 2
        and document.get("status") == "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE"
        and document.get("runtime_non_delegation") == "NOT ESTABLISHED"
        and document.get("qualified_candidate_count") == 0,
        "reject an unreviewed, weakened, or falsely qualifying runtime guard",
    )
    for label, expected in (("source", source), ("protocol", protocol)):
        actual = document.get(label)
        require(
            type(actual) is dict
            and all(actual.get(key) == expected[key]
                    for key in ("path", "sha256", "bytes", "device", "inode", "mode", "nlink")),
            "reject a changed pinned runtime guard " + label,
        )
    nested = document.get("subinterpreter_bootstrap")
    require(
        type(nested) is dict
        and nested.get("suite") == "subinterpreter_v2"
        and nested.get("original_case_count") == NESTED_CASE_COUNT
        and nested.get("expected_interpreters_created") == NESTED_INTERPRETER_COUNT
        and nested.get("expected_interpreters_destroyed") == NESTED_INTERPRETER_COUNT
        and nested.get("expected_case_interpreter_exec_calls") == NESTED_CASE_EXECUTIONS
        and nested.get("require_child_guard_before_candidate_import") is True
        and nested.get("unrestricted_creation") is False,
        "reject unscoped or incomplete first-party child interpreter guards",
    )
    require(
        getattr(implementation, "__code__", None) is not None
        and implementation.__code__.co_filename
        == ROOT + "/" + RUNTIME_GUARD_SOURCE
        and hashlib.sha256(source_raw).hexdigest() == source["sha256"],
        "reject runtime guard code from an unverified source",
    )
    return child, {"source": source, "protocol": protocol, "contract": contract}


def guard_native_owner(spec: FamilySpec, native: dict, role: str) -> dict:
    require(role in ("engine", "bridge"), "reject an unknown child native role")
    key = "native_" + role
    current = native.get(key)
    relative = spec.engine_relative if role == "engine" else spec.bridge_relative
    require(
        type(current) is dict
        and current.get("relative") == relative
        and valid_digest(current.get("sha256")),
        "reject an unauthenticated child native role",
    )
    absolute = ROOT + "/" + relative
    info = os.stat(absolute, follow_symlinks=False)
    require(
        stat.S_ISREG(info.st_mode)
        and info.st_dev == current.get("device")
        and info.st_ino == current.get("inode")
        and info.st_size == current.get("bytes")
        and info.st_uid == os.geteuid()
        and info.st_nlink == 1,
        "reject a changed native role before child guard installation",
    )
    return {
        "role": role,
        "family": spec.name,
        "absolute_path": absolute,
        "relative": relative,
        "file_name": relative.rsplit("/", 1)[-1],
        "sha256": current["sha256"],
        "bytes": info.st_size,
        "size_bytes": info.st_size,
        "device": info.st_dev,
        "inode": info.st_ino,
        "mode": stat.S_IMODE(info.st_mode),
        "uid": info.st_uid,
        "nlink": info.st_nlink,
        "native_loaded": False,
    }


class PreparedOriginalLocales:
    """Verify externally prepared original locales; never start a process."""

    __slots__ = ("locale", "previous", "directory", "evidence")

    def __init__(self) -> None:
        self.locale = __import__("locale")
        self.previous = None
        self.directory = None
        self.evidence: dict = {}

    def __enter__(self) -> dict:
        directory = os.environ.get("LOCPATH")
        require(
            type(directory) is str
            and directory.startswith("/tmp/")
            and os.path.isabs(directory)
            and os.path.realpath(directory) == directory,
            "require a private locale fixture prepared outside the candidate worker",
        )
        identity = os.stat(directory, follow_symlinks=False)
        require(
            stat.S_ISDIR(identity.st_mode)
            and identity.st_uid == os.geteuid()
            and stat.S_IMODE(identity.st_mode) == 0o700,
            "reject a shared, substituted, or insecure prepared locale fixture",
        )
        self.directory = directory
        self.previous = self.locale.setlocale(self.locale.LC_CTYPE)
        self.evidence = {
            "fixture_prepared_outside_candidate_worker": True,
            "private_locale_root": directory,
            "private_locale_root_device": identity.st_dev,
            "private_locale_root_inode": identity.st_ino,
            "actual_candidate_localedef_workers": 0,
            "actual_candidate_subprocesses": 0,
            "iso_8859_1_verified": False,
            "utf_8_verified": False,
            "process_locale_restored": False,
            "locale_search_path_unchanged": False,
        }
        try:
            for locale_name, field in (
                ("en_US.iso88591", "iso_8859_1_verified"),
                ("en_US.utf8", "utf_8_verified"),
            ):
                self.locale.setlocale(self.locale.LC_CTYPE, locale_name)
                self.evidence[field] = True
            self.locale.setlocale(self.locale.LC_CTYPE, self.previous)
        except BaseException:
            self.locale.setlocale(self.locale.LC_CTYPE, self.previous)
            raise
        return self.evidence

    def __exit__(self, kind: object, value: object, trace: object) -> bool:
        require(self.previous is not None and self.directory is not None, "reject cleanup of an unprepared original locale")
        self.locale.setlocale(self.locale.LC_CTYPE, self.previous)
        self.evidence["process_locale_restored"] = self.locale.setlocale(self.locale.LC_CTYPE) == self.previous
        self.evidence["locale_search_path_unchanged"] = os.environ.get("LOCPATH") == self.directory
        require(self.evidence["process_locale_restored"] and self.evidence["locale_search_path_unchanged"], "restore the actual original locale without candidate process creation")
        return False


def exact_native_owners(spec: FamilySpec, pins: object, source_pins: object) -> dict:
    require(type(spec) is FamilySpec and type(pins) is dict and set(pins) == {"source", "native_engine", "native_bridge"} and all(valid_digest(value) for value in pins.values()) and type(source_pins) is dict and source_pins == {path: digest for path, digest, _ in spec.source_owners} and (pins["native_engine"] == pins["native_bridge"]) is spec.combined_native, "reject crossed, borrowed, omitted, or unowned native engines")
    result: dict[str, dict] = {}
    for relative, expected, size in spec.source_owners:
        descriptor = os.open(ROOT + "/" + relative, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
        try:
            info = os.fstat(descriptor)
            require(stat.S_ISREG(info.st_mode) and info.st_size == size and info.st_nlink == 1 and info.st_uid == os.geteuid(), "reject substituted family source: " + relative)
            state = hashlib.sha256()
            remaining = size
            while remaining:
                data = os.read(descriptor, min(262144, remaining))
                require(bool(data), "reject truncated family source: " + relative)
                state.update(data)
                remaining -= len(data)
            require(not os.read(descriptor, 1) and state.hexdigest() == expected, "reject modified family source: " + relative)
            if relative == spec.adapter_relative:
                result["source"] = {"relative": relative, "sha256": expected, "bytes": size, "device": info.st_dev, "inode": info.st_ino}
        finally:
            os.close(descriptor)
    require(pins["source"] == source_pins[spec.adapter_relative], "reject unowned candidate adapter")
    for role, relative in (("native_engine", spec.engine_relative), ("native_bridge", spec.bridge_relative)):
        if role == "native_bridge" and spec.combined_native:
            result[role] = dict(result["native_engine"])
            continue
        descriptor = os.open(ROOT + "/" + relative, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
        try:
            info = os.fstat(descriptor)
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_uid == os.geteuid() and 0 < info.st_size <= MAX_BINARY_BYTES, "reject substituted native owner: " + relative)
            state = hashlib.sha256()
            remaining = info.st_size
            while remaining:
                data = os.read(descriptor, min(262144, remaining))
                require(bool(data), "reject truncated native owner: " + relative)
                state.update(data)
                remaining -= len(data)
            require(not os.read(descriptor, 1) and state.hexdigest() == pins[role], "reject modified native owner: " + relative)
            result[role] = {"relative": relative, "sha256": pins[role], "bytes": info.st_size, "device": info.st_dev, "inode": info.st_ino}
        finally:
            os.close(descriptor)
    return result


def failure_details(suite: SuiteSpec, spec: FamilySpec, error: BaseException, records: list) -> dict:
    return {"schema": SCHEMA + "-genuine-suite-failure", "status": "FAIL", "suite": suite.name, "candidate_family": spec.name, "active_case": None, "completed_candidate_cases": len(records), "completed_candidate_records": records, "error_type": type(error).__qualname__, "error_message": str(error), "actual_candidate_workers": 1, "hidden_cases_read": 0, "benchmark_files_read": 0, "clock_samples": 0, "timing_trials_run": 0, "performance": "NOT MEASURED", "holdout": "NOT OPENED", "candidate_qualified": False, "winner_selected": False}


def observe_original_upstream(suite: SuiteSpec, spec: FamilySpec, pins: dict, source_pins: dict) -> dict:
    require(suite.name == "original_bounded_v5", "require the unchanged original public-method suite")
    candidate = require_selected(spec)
    policy = active_runtime_policy(spec)
    owners = exact_native_owners(spec, pins, source_pins)
    records: list = []
    try:
        harness = load_module(HARNESS_OWNER, "_rebar_v5_original_harness_" + spec.name)
        require(harness.TEST_SOURCE_SHA256 == UPSTREAM_SHA256 and harness.BASELINE_RECORDS_SHA256 == suite.reference_sha256 and harness.METHOD_MATRIX_SHA256 == suite.matrix_sha256, "reject a substituted pinned original test harness")
        if not sys.path or sys.path[0] != ROOT:
            sys.path.insert(0, ROOT)
        matrix = harness.build_matrix()
        require(harness.validate_matrix(matrix) == suite.matrix_sha256 and len(matrix) == 165, "reject modified original source-ordered method matrix")
        private = [row["test"] for row in matrix if row["classification"] == "named-private-waiver"]
        public = [row for row in matrix if row["classification"] == "public"]
        require(tuple(private) == PRIVATE_WAIVER_NAMES and tuple(harness.PRIVATE_METHODS) == PRIVATE_WAIVER_NAMES and len(private) == PRIVATE_WAIVER_COUNT and len(public) == ORIGINAL_PUBLIC_RECORD_COUNT, "reject omitted public tests or added private waivers")
        importlib = __import__("importlib")
        util = __import__("importlib.util", fromlist=["spec_from_file_location"])
        unittest = __import__("unittest")
        contextlib = __import__("contextlib")
        io = __import__("io")
        multiprocessing = __import__("multiprocessing")
        require("fork" in multiprocessing.get_all_start_methods(), "the original GH94675 test requires the authentic fork start method")
        multiprocessing.set_start_method("fork", force=True)
        require(multiprocessing.get_start_method() == "fork", "reject an emulated original multiprocessing regression")
        require_selected(spec)
        original_path = list(sys.path)
        previous = sys.modules.get("test.test_re")
        output, errors = io.StringIO(), io.StringIO()
        try:
            sys.path.insert(1, str(harness.UPSTREAM_LIB))
            support = importlib.import_module("test.support")
            helper = importlib.import_module("test.support.warnings_helper")
            corpus = importlib.import_module("test.re_tests")
            require(os.path.realpath(support.__file__) == str(harness.SUPPORT_SOURCE) and os.path.realpath(helper.__file__) == str(harness.WARNINGS_HELPER_SOURCE) and os.path.realpath(corpus.__file__) == str(harness.CORPUS_SOURCE) and support.use_resources is None and support.real_max_memuse == 0 and support.is_resource_enabled("cpu") and len(corpus.tests) == 403 and len(corpus.benchmarks) == 11, "reject substituted pinned original upstream support")
            require(importlib.import_module("re") is candidate, "an original test did not receive the selected first-party matcher")
            with PreparedOriginalLocales() as actual_locales:
                specification = util.spec_from_file_location("test.test_re", str(harness.TEST_SOURCE))
                require(specification is not None and specification.loader is not None, "the literal upstream test source cannot load")
                module = util.module_from_spec(specification)
                sys.modules["test.test_re"] = module
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                    specification.loader.exec_module(module)
                    require(os.path.realpath(module.__file__) == UPSTREAM_TEST, "reject substituted original CPython test source")
                    for requirement in public:
                        require_selected(spec)
                        actual = getattr(module, requirement["class"])(requirement["method"])
                        outcome = unittest.TestResult()
                        identity = requirement["test"]
                        previous_fork = getattr(policy, "fork_case", None)
                        previous_clock = getattr(policy, "correctness_clock_case", None)
                        require(previous_fork is None and previous_clock is None, "reject a leaked original-case runtime scope")
                        try:
                            if identity == "ReTests.test_regression_gh94675":
                                begin_fork = getattr(policy, "begin_fork_case", None)
                                require(callable(begin_fork), "require the authenticated original-only fork runtime scope")
                                begin_fork(identity)
                            if identity == "ReTests.test_search_anchor_at_beginning":
                                begin_clock = getattr(policy, "begin_correctness_clock", None)
                                require(callable(begin_clock), "require the authenticated original-only correctness-clock scope")
                                begin_clock(identity)
                            actual.run(outcome)
                        finally:
                            if identity == "ReTests.test_regression_gh94675":
                                end_fork = getattr(policy, "end_fork_case", None)
                                require(callable(end_fork), "require cleanup of the authenticated original-only fork scope")
                                end_fork()
                                require(getattr(policy, "fork_case", None) == previous_fork, "reject an escaped original GH94675 fork scope")
                            if identity == "ReTests.test_search_anchor_at_beginning":
                                end_clock = getattr(policy, "end_correctness_clock", None)
                                require(callable(end_clock), "require cleanup of the authenticated original-only correctness-clock scope")
                                end_clock()
                                require(getattr(policy, "correctness_clock_case", None) == previous_clock, "reject an escaped original correctness-clock scope")
                        records.append(harness.normalize_test_result(requirement, outcome))
                        require_selected(spec)
                        policy.check_modules()
        finally:
            sys.path[:] = original_path
            if previous is None:
                sys.modules.pop("test.test_re", None)
            else:
                sys.modules["test.test_re"] = previous
    except BaseException as error:
        raise ActualSuiteFailure("the guarded literal original upstream test failed", failure_details(suite, spec, error, records)) from error
    require(len(records) == ORIGINAL_PUBLIC_RECORD_COUNT, "reject omitted original public test records")
    skips = [record for record in records if record.get("status") == "SKIP"]
    require(len(skips) <= 1 and (not skips or (skips[0].get("test") == "ReTests.test_memory_leaks" and skips[0].get("skip_reasons") == ["requires debug build"])), "reject unnamed or forged original debug-build skips")
    actual_digest = hashlib.sha256(canonical(records)).hexdigest()
    failures = [record for record in records if record.get("status") == "FAIL"]
    if actual_digest != suite.reference_sha256 and not failures:
        failures = [{"type": "ActualOriginalVectorMismatch", "expected_records_sha256": suite.reference_sha256, "actual_records_sha256": actual_digest, "complete_actual_records": records}]
    passed = not failures and len(skips) == ORIGINAL_DEBUG_SKIP_COUNT and actual_digest == suite.reference_sha256
    return {"schema": SCHEMA + "-actual-original-suite", "status": "PASS" if passed else "FAIL", "suite": suite.name, "candidate_family": spec.name, "candidate_module": spec.module, "source_relative": suite.source_relative, "source_sha256": suite.source_sha256, "matrix_sha256": suite.matrix_sha256, "reference_records_sha256": suite.reference_sha256, "candidate_records_sha256": actual_digest, "case_execution_denominator": suite.case_count, "actual_candidate_case_count": suite.case_count, "actual_public_record_count": len(records), "actual_debug_skip_count": len(skips), "named_private_waiver_count": PRIVATE_WAIVER_COUNT, "named_private_waivers": private, "candidate_records": records, "mismatch_count": len(failures), "all_mismatches": failures, "native_provenance": owners, "locale_evidence": actual_locales, "matcher_guard": {"installed_before_candidate_import": True, "actual_method_guard_checks": 2 * ORIGINAL_PUBLIC_RECORD_COUNT, "stdlib_regex_engine_loaded": False, "selected_candidate_module": spec.module}, "actual_candidate_workers": 1, "actual_candidate_subprocesses": 0, "hidden_cases_read": 0, "benchmark_files_read": 0, "clock_samples": 0, "timing_trials_run": 0, "performance": "NOT MEASURED", "holdout": "NOT OPENED", "candidate_qualified": False, "winner_selected": False}


def observe_direct_suite(suite: SuiteSpec, spec: FamilySpec, pins: dict, source_pins: dict, manifest: dict) -> dict:
    require(suite.name not in ("original_bounded_v5", "subinterpreter_v2"), "route original and nested cases through guarded observers")
    candidate = require_selected(spec)
    policy = active_runtime_policy(spec)
    native = exact_native_owners(spec, pins, source_pins)
    records: list = []
    resource_evidence: dict = {}
    guard_checks = 0
    try:
        gate = load_module(DIRECT_GATE_OWNER, "_rebar_v5_direct_gate_" + spec.name + "_" + suite.name)
        previous = load_module(V4_OWNERS[0], "_rebar_v5_legacy_producer_" + spec.name + "_" + suite.name)
        original_spec = gate.suite_spec(suite.name)
        source = gate.import_suite_source(original_spec)
        core = category = None
        support = None
        if suite.name in {"public_v3", "scanner_v3", "buffer_v3"}:
            core, category = gate.source_module_for_core(original_spec)
            _, _, selected, matrix, _, _ = core.load_prerequisites(category)
            require(selected is source, "reject a substituted source-owned case evaluator")
        else:
            matrix = gate.producer_matrix(source, original_spec)
            if suite.name == "public_types_v1":
                support = source.preload_support_modules()
                source.verify_support_modules(support)
        if suite.name == "public_types_v1":
            baseline, second, baseline_evidence = previous.authenticate_original_public_type_baseline(previous.suite_spec(suite.name))
        else:
            baseline, second, baseline_evidence = gate.archived_vectors(manifest, original_spec)
        require(baseline == second and len(baseline) == suite.case_count and len(matrix) == suite.case_count, "reject changed independently observed original records")
        def verify_selected() -> None:
            nonlocal guard_checks
            require_selected(spec)
            policy.check_modules()
            guard_checks += 1

        if suite.name == "threaded_pattern_v1":
            records, resource_evidence = gate.observe_threaded_suite(
                source, candidate, matrix, {"verify": verify_selected},
            )
            require(
                guard_checks == 2 * len(source.COHORTS)
                and resource_evidence.get("actual_thread_starts") == 32
                and resource_evidence.get("actual_thread_joins") == 32
                and resource_evidence.get("actual_thread_case_executions") == 1024
                and resource_evidence.get("orphan_threads") == 0,
                "reject a missing genuine original shared-thread lifecycle",
            )
        elif suite.name == "public_surface_v19":
            with PreparedOriginalLocales() as locales:
                records, resource_evidence = gate.observe_public_surface(
                    source, candidate, matrix, {"verify": verify_selected},
                    {"iso8859_1": "en_US.iso88591", "utf8": "en_US.utf8"},
                )
                require(
                    type(locales) is dict
                    and locales.get("actual_candidate_localedef_workers") == 0
                    and locales.get("actual_candidate_subprocesses") == 0
                    and locales.get("fixture_prepared_outside_candidate_worker") is True
                    and locales.get("iso_8859_1_verified") is True
                    and locales.get("utf_8_verified") is True
                    and resource_evidence.get("real_locale_case_count") == 64
                    and resource_evidence.get("real_locale_transition_count") == 192
                    and guard_checks == 2 * suite.case_count,
                    "reject the genuine original locale provision or case lifecycle",
                )
                resource_evidence["actual_private_locale_provision"] = locales
        else:
            for case in matrix:
                verify_selected()
                records.append(gate.create_frozen_record(original_spec, source, case, candidate, core=core, category=category, support=support))
                verify_selected()
            require(guard_checks == 2 * suite.case_count, "reject an omitted original source-owned guard check")
        differences = previous.validate_direct_records(previous.suite_spec(suite.name), source, records, baseline)
    except BaseException as error:
        raise ActualSuiteFailure("the guarded original source-owned suite failed: " + suite.name, failure_details(suite, spec, error, records)) from error
    actual_digest = source.digest(records)
    return {"schema": SCHEMA + "-actual-original-suite", "status": "PASS" if not differences else "FAIL", "suite": suite.name, "candidate_family": spec.name, "candidate_module": spec.module, "case_execution_denominator": suite.case_count, "actual_candidate_case_count": len(records), "source_relative": suite.source_relative, "source_sha256": suite.source_sha256, "matrix_sha256": suite.matrix_sha256, "reference_records_sha256": suite.reference_sha256, "candidate_records_sha256": actual_digest, "baseline_evidence": baseline_evidence, "candidate_records": records, "mismatch_count": len(differences), "all_mismatches": differences, "matcher_guard": {"installed_before_candidate_import": True, "actual_method_guard_checks": guard_checks, "stdlib_regex_engine_loaded": False, "selected_candidate_module": spec.module}, "native_provenance": native, "resource_evidence": resource_evidence, "actual_candidate_workers": 1, "hidden_cases_read": 0, "benchmark_files_read": 0, "clock_samples": 0, "timing_trials_run": 0, "performance": "NOT MEASURED", "holdout": "NOT OPENED", "candidate_qualified": False, "winner_selected": False}


def observe_subinterpreters(suite: SuiteSpec, spec: FamilySpec, pins: dict, source_pins: dict, *, producer_sha256: str) -> dict:
    require(suite.name == "subinterpreter_v2" and valid_digest(producer_sha256), "require the complete guarded original subinterpreter suite")
    require_selected(spec)
    policy = active_runtime_policy(spec)
    native = exact_native_owners(spec, pins, source_pins)
    child, guard = active_guard_child_bootstrap(policy)
    engine = guard_native_owner(spec, native, "engine")
    bridge = guard_native_owner(spec, native, "bridge")
    require(
        (engine["sha256"] == bridge["sha256"]) is spec.combined_native,
        "reject crossed or aliased child native owners",
    )
    nested = load_module(NESTED_OWNER, "_rebar_v5_guarded_nested_" + spec.name)
    previous = load_module(V4_OWNERS[0], "_rebar_v5_guarded_nested_legacy_" + spec.name)
    previous_suite = previous.suite_spec(suite.name)
    previous_spec = previous.family_spec(spec.name)
    require(
        previous_suite.case_count == NESTED_CASE_COUNT
        and previous_suite.matrix_sha256 == suite.matrix_sha256
        and previous_suite.reference_sha256 == suite.reference_sha256
        and previous_spec.module == spec.module
        and previous_spec.bridge_module == spec.bridge_module,
        "reject altered original nested source, records, or family",
    )
    begin = getattr(policy, "begin_subinterpreters", None)
    end = getattr(policy, "end_subinterpreters", None)
    register = getattr(policy, "register_child_bootstrap", None)
    confirm = getattr(policy, "confirm_child_guard", None)
    require(
        callable(begin) and callable(end)
        and callable(register) and callable(confirm),
        "require explicit bounded parent interpreter creation and execution scopes",
    )
    importlib = __import__("importlib")
    public_interpreters = importlib.import_module("concurrent.interpreters")
    require(
        type(public_interpreters) is types.ModuleType
        and os.path.realpath(getattr(public_interpreters, "__file__", ""))
        == nested.PINNED_INTERPRETERS,
        "require the exact pinned public subinterpreter provider",
    )
    real_bootstraps = 0
    real_cleanups = 0
    pending_bootstraps: dict[str, dict] = {}
    actual_attestations: list[dict] = []
    previous_loader = previous.frozen_module
    previous_bootstrap = previous.interpreter_bootstrap_source
    previous_cleanup = nested.interpreter_cleanup_source
    previous_create = public_interpreters.create

    class GuardedOriginalInterpreter:
        """Register the exact bootstrap before a child's first real exec."""

        __slots__ = ("interpreter",)

        def __init__(self, interpreter: object) -> None:
            require(
                hasattr(interpreter, "id")
                and callable(getattr(interpreter, "exec", None))
                and callable(getattr(interpreter, "close", None)),
                "reject a fabricated public subinterpreter",
            )
            self.interpreter = interpreter

        @property
        def id(self) -> object:
            return self.interpreter.id

        def exec(self, source: str) -> object:
            require(type(source) is str, "reject non-source child execution")
            identity = int(self.interpreter.id)
            states = getattr(policy, "child_bootstraps", None)
            require(type(states) is dict, "reject a missing parent child ledger")
            if identity not in states:
                fingerprint = hashlib.sha256(source.encode("utf-8")).hexdigest()
                pending = pending_bootstraps.get(fingerprint)
                require(
                    type(pending) is dict,
                    "reject an unregistered first child execution",
                )
                reader = pending["reader"]
                writer = pending["writer"]
                try:
                    registered = register(
                        self.interpreter,
                        source,
                        family=spec.name,
                        source_sha256=guard["source"]["sha256"],
                        protocol_sha256=guard["protocol"]["sha256"],
                        contract_sha256=guard["contract"]["sha256"],
                        bridge_owner=bridge,
                        engine_owner=engine,
                        owner=pending["owner"],
                        attestation_fd=writer,
                        read_fd=reader,
                        challenge=pending["challenge"],
                    )
                    require(
                        registered is None
                        and identity in policy.child_bootstraps
                        and policy.child_bootstraps[identity]["dispatched"] is False
                        and policy.child_bootstraps[identity]["installed"] is False,
                        "reject a fabricated pre-execution child attestation",
                    )
                    pending["registered"] = True
                    result = self.interpreter.exec(source)
                    confirm(self.interpreter)
                    pending["writer"] = None
                    pending["reader"] = None
                    require(
                        policy.child_bootstraps[identity]["dispatched"] is True
                        and policy.child_bootstraps[identity]["installed"] is True,
                        "reject a child guard unconfirmed by its real owned pipe",
                    )
                    actual_attestations.append({
                        "interpreter_id": identity,
                        "owner": pending["owner"],
                        "bootstrap_sha256": fingerprint,
                        "challenge_sha256": hashlib.sha256(
                            pending["challenge"].encode("ascii")
                        ).hexdigest(),
                        "confirmation": "VERIFIED BY AUTHENTICATED GUARD FROM ITS OWN LIVE PIPE",
                        "positive_child_execution": True,
                        "all_descriptors_closed": True,
                    })
                    pending_bootstraps.pop(fingerprint)
                    return result
                finally:
                    actual_state = policy.child_bootstraps.get(identity)
                    if type(actual_state) is dict:
                        if actual_state.get("write_fd") is None:
                            pending["writer"] = None
                        if actual_state.get("read_fd") is None:
                            pending["reader"] = None
                    for key in ("writer", "reader"):
                        descriptor = pending.get(key)
                        if type(descriptor) is int:
                            pending[key] = None
                            os.close(descriptor)
            require(
                states[identity].get("installed") is True,
                "reject execution before a real child guard attestation",
            )
            return self.interpreter.exec(source)

        def close(self) -> object:
            return self.interpreter.close()

    def guarded_create() -> GuardedOriginalInterpreter:
        return GuardedOriginalInterpreter(previous_create())

    def load_exact(relative: str, digest: str) -> object:
        if relative == NESTED_OWNER[0]:
            require(digest == NESTED_OWNER[1], "reject a substituted frozen child recorder")
            return nested
        return previous_loader(relative, digest)

    def guarded_bootstrap(
        legacy_spec: object,
        candidate_pins: object,
        candidate_sources: object,
        *,
        owner: str,
        producer_sha256: str,
    ) -> str:
        nonlocal real_bootstraps
        require(
            legacy_spec is previous_spec
            and candidate_pins == pins
            and candidate_sources == source_pins
            and owner in ("A", "B", "C")
            and valid_digest(producer_sha256),
            "reject unscoped or borrowed guarded child bootstrap",
        )
        reader, writer = os.pipe()
        pending: dict | None = None
        try:
            challenge = os.urandom(32).hex()
            source = child(
                spec.name,
                source_sha256=guard["source"]["sha256"],
                protocol_sha256=guard["protocol"]["sha256"],
                contract_sha256=guard["contract"]["sha256"],
                bridge_owner=bridge,
                engine_owner=engine,
                owner=owner,
                attestation_fd=writer,
                challenge=challenge,
            )
            require(
                type(source) is str
                and 0 < len(source.encode("utf-8")) <= 131072,
                "reject absent or unbounded authenticated child bootstrap",
            )
            compile(
                source,
                "<frozen-first-party-v5-child-bootstrap>",
                "exec",
                dont_inherit=True,
            )
            fingerprint = hashlib.sha256(source.encode("utf-8")).hexdigest()
            require(
                fingerprint not in pending_bootstraps,
                "reject a repeated per-child attestation challenge",
            )
            pending = {
                "reader": reader,
                "writer": writer,
                "owner": owner,
                "challenge": challenge,
            }
            pending_bootstraps[fingerprint] = pending
            real_bootstraps += 1
            return source
        except BaseException:
            if pending is not None:
                pending_bootstraps.pop(fingerprint, None)
            os.close(writer)
            os.close(reader)
            raise

    def guarded_cleanup() -> str:
        nonlocal real_cleanups
        source = previous_cleanup()
        require(
            type(source) is str
            and 0 < len(source.encode("utf-8")) <= MAX_SOURCE_BYTES,
            "reject the immutable source-authenticated original child cleanup",
        )
        compile(
            source,
            "<immutable-original-owned-child-cleanup>",
            "exec",
            dont_inherit=True,
        )
        real_cleanups += 1
        return source

    previous.frozen_module = load_exact
    previous.interpreter_bootstrap_source = guarded_bootstrap
    nested.interpreter_cleanup_source = guarded_cleanup
    public_interpreters.create = guarded_create
    result = None
    primary: BaseException | None = None
    began = False
    try:
        begin(
            suite="subinterpreter_v2",
            expected_created=NESTED_INTERPRETER_COUNT,
            expected_exec=NESTED_CASE_EXECUTIONS,
        )
        began = True
        result = previous.observe_subinterpreters(
            previous_suite, previous_spec, pins, source_pins,
            producer_sha256=producer_sha256,
        )
    except BaseException as error:
        primary = error
    finally:
        previous.frozen_module = previous_loader
        previous.interpreter_bootstrap_source = previous_bootstrap
        nested.interpreter_cleanup_source = previous_cleanup
        public_interpreters.create = previous_create
        if began:
            try:
                end()
            except BaseException as cleanup_error:
                if primary is None:
                    primary = cleanup_error
    if primary is not None:
        extra = getattr(primary, "details", None)
        details = {
            "schema": SCHEMA + "-genuine-nested-failure",
            "status": "FAIL",
            "suite": suite.name,
            "candidate_family": spec.name,
            "error_type": type(primary).__qualname__,
            "error_message": str(primary),
            "actual_child_guards_installed": real_bootstraps,
            "actual_guard_cleanup_interpreter_exec_calls": real_cleanups,
            "expected_case_interpreter_exec_calls": NESTED_CASE_EXECUTIONS,
            "expected_interpreters_created": NESTED_INTERPRETER_COUNT,
            "guard_source_sha256": guard["source"]["sha256"],
            "guard_protocol_sha256": guard["protocol"]["sha256"],
            "guard_contract_sha256": guard["contract"]["sha256"],
            "actual_candidate_subprocesses": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "performance": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "candidate_qualified": False,
            "winner_selected": False,
        }
        if type(extra) is dict:
            details["complete_original_failure_details"] = extra
        raise ActualSuiteFailure("preserve the actual guarded original child lifecycle failure", details) from primary
    require(
        type(result) is dict
        and result.get("schema") == previous.SCHEMA + "-actual-original-suite"
        and result.get("status") == "PASS"
        and result.get("suite") == "subinterpreter_v2"
        and result.get("candidate_family") == spec.name
        and result.get("case_execution_denominator") == NESTED_CASE_COUNT
        and result.get("actual_candidate_case_count") == NESTED_CASE_COUNT
        and result.get("actual_case_interpreter_exec_calls") == NESTED_CASE_EXECUTIONS
        and result.get("actual_interpreters_created") == NESTED_INTERPRETER_COUNT
        and result.get("actual_interpreters_destroyed") == NESTED_INTERPRETER_COUNT
        and result.get("actual_initialization_interpreter_exec_calls") == NESTED_INTERPRETER_COUNT
        and result.get("actual_guard_cleanup_interpreter_exec_calls") == NESTED_INTERPRETER_COUNT
        and result.get("all_real_pipes_read_to_eof") is True
        and result.get("all_real_pipe_descriptors_closed") is True
        and result.get("interpreter_live_set_restored") is True
        and result.get("locale_restored") is True
        and result.get("mismatch_count") == 0
        and result.get("all_mismatches") == []
        and real_bootstraps == NESTED_INTERPRETER_COUNT
        and real_cleanups == NESTED_INTERPRETER_COUNT
        and not pending_bootstraps
        and len(actual_attestations) == NESTED_INTERPRETER_COUNT
        and len({item["interpreter_id"] for item in actual_attestations})
        == NESTED_INTERPRETER_COUNT
        and len({item["challenge_sha256"] for item in actual_attestations})
        == NESTED_INTERPRETER_COUNT
        and all(
            item["positive_child_execution"] is True
            and item["all_descriptors_closed"] is True
            for item in actual_attestations
        )
        and len(getattr(policy, "child_bootstraps", {}))
        == NESTED_INTERPRETER_COUNT
        and all(
            item.get("installed") is True
            for item in policy.child_bootstraps.values()
        ),
        "reject any omitted or fabricated original 128-case / 394-execution / 11-child lifecycle",
    )
    result["schema"] = SCHEMA + "-actual-original-suite"
    result["actual_child_guards_installed"] = real_bootstraps
    result["runtime_guard_source_sha256"] = guard["source"]["sha256"]
    result["runtime_guard_protocol_sha256"] = guard["protocol"]["sha256"]
    result["runtime_guard_contract_sha256"] = guard["contract"]["sha256"]
    result["guard_installed_before_every_child_candidate_import"] = True
    result["actual_child_guard_attestations"] = actual_attestations
    result["actual_attestation_pipe_count"] = len(actual_attestations)
    result["all_child_attestation_pipes_closed"] = True
    result["actual_candidate_subprocesses"] = 0
    result["legacy_v4_bootstrap_calls"] = 0
    result["legacy_v4_cleanup_calls"] = 0
    return result


def owner_record(owner: tuple) -> dict:
    return {"path": owner[0], "sha256": owner[1], "bytes": owner[2], "device": 2064, "inode": owner[3], "mode": "0600", "nlink": 1}


def suite_record(suite: SuiteSpec) -> dict:
    return {"id": suite.name, "case_execution_count": suite.case_count, "source_relative": suite.source_relative, "source_sha256": suite.source_sha256, "matrix_sha256": suite.matrix_sha256, "reference_records_sha256": suite.reference_sha256, "published_seed_decimal": None if suite.seed is None else str(suite.seed), "unchanged_original_producer_route": suite.route}


def no_effects() -> dict:
    return {"actual_candidate_imports": 0, "actual_candidate_workers": 0, "actual_reference_workers": 0, "actual_native_libraries_loaded": 0, "actual_private_build_root_opens": 0, "actual_private_build_root_stats": 0, "actual_archive_opens": 0, "actual_archive_inflations": 0, "actual_compiler_processes_started": 0, "actual_subinterpreters_created": 0, "actual_threads_started": 0, "actual_clock_samples": 0, "actual_hidden_cases_read": 0, "actual_benchmark_files_read": 0, "timing_trials_run": 0}


def source_runtime() -> None:
    require(sys.implementation.name == "cpython" and tuple(sys.version_info[:3]) == (3, 14, 6) and sys.flags.isolated == 1 and sys.dont_write_bytecode and os.path.abspath(sys.executable) == PINNED_PYTHON and os.path.realpath(sys.executable) == PINNED_PYTHON and os.path.abspath(__file__) == ROOT + "/" + SOURCE_RELATIVE and not any(name == "candidates" or name.startswith("candidates.") for name in sys.modules), "require isolated pinned CPython without any candidate")


def validate_inventory() -> None:
    require(len(SUITES) == SUITE_COUNT and len({item.name for item in SUITES}) == SUITE_COUNT and sum(item.case_count for item in SUITES) == CASE_DENOMINATOR, "reject a changed, double-counted, or omitted original suite")
    require(set(FAMILIES) == {"rust", "c", "zig", "cpp", "go", "fortran"} and set(FAMILIES) == set(OWNED_SOURCES) and sum(len(items) for items in OWNED_SOURCES.values()) == 25, "reject borrowed, omitted, or duplicate family source owners")
    require(all(family.name == name and family.source_owners == OWNED_SOURCES[name] for name, family in FAMILIES.items()), "reject an inauthentic first-party family")
    require(SUITES[0].case_count == 151 and SUITES[0].matrix_sha256 == "93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240" and SUITES[0].reference_sha256 == "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276" and ORIGINAL_PUBLIC_RECORD_COUNT == 152 and ORIGINAL_DEBUG_SKIP_COUNT == 1 and PRIVATE_WAIVER_COUNT == 13 and len(PRIVATE_WAIVER_NAMES) == PRIVATE_WAIVER_COUNT and len(set(PRIVATE_WAIVER_NAMES)) == PRIVATE_WAIVER_COUNT, "reject the literal original public tests or named private waivers")


def synthetic_alias_controls() -> int:
    """Prove exact aliases fail closed without importing an actual engine."""
    require("re" not in sys.modules and "_sre" not in sys.modules and not any(name == "candidates" or name.startswith("candidates.") for name in sys.modules), "reject synthetic controls over an actual loaded engine")
    controls = 0
    for spec in FAMILIES.values():
        candidate = types.ModuleType(spec.module)
        bridge = types.ModuleType(spec.bridge_module)
        constants = types.ModuleType("re._constants")
        constants.MAXGROUPS = 1073741823
        try:
            sys.modules[spec.module] = candidate
            sys.modules[spec.bridge_module] = bridge
            sys.modules["re"] = candidate
            sys.modules["re._constants"] = constants
            require(require_selected(spec) is candidate, "reject a genuinely selected synthetic first-party identity")
            controls += 1

            sys.modules["_sre"] = types.ModuleType("_sre")
            controls += reject(lambda item=spec: require_selected(item), "reject the actual CPython regex engine")
            sys.modules.pop("_sre", None)

            foreign = next(name for name in FAMILIES if name != spec.name)
            other = FAMILIES[foreign].module
            sys.modules[other] = types.ModuleType(other)
            controls += reject(lambda item=spec: require_selected(item), "reject another first-party candidate")
            sys.modules.pop(other, None)

            sys.modules["re"] = types.ModuleType("re")
            controls += reject(lambda item=spec: require_selected(item), "reject a nonidentical stdlib-like re alias")
            sys.modules["re"] = candidate

            constants.MAXGROUPS = 0
            controls += reject(lambda item=spec: require_selected(item), "reject substituted upstream constant data")
            constants.MAXGROUPS = 1073741823

            sys.modules.pop(spec.bridge_module, None)
            controls += reject(lambda item=spec: require_selected(item), "reject a missing native first-party bridge")
        finally:
            sys.modules.pop("_sre", None)
            sys.modules.pop(spec.bridge_module, None)
            sys.modules.pop(spec.module, None)
            sys.modules.pop("re._constants", None)
            sys.modules.pop("re", None)
        require("re" not in sys.modules and "_sre" not in sys.modules and not any(name == "candidates" or name.startswith("candidates.") for name in sys.modules), "a synthetic candidate alias escaped its control")
    require(controls == 6 * len(FAMILIES), "reject an omitted six-family hostile alias control")
    return controls


def synthetic_matrix_controls() -> int:
    """Reject any dropped or modified frozen original suite, in source order."""
    controls = 0
    previous = {"schema": "rebar-owned-six-family-original-p0-producer-v4-source-freeze", "version": 4, "suite_count": SUITE_COUNT, "case_execution_denominator": CASE_DENOMINATOR, "family_count": len(FAMILIES), "source_owner_count": 25, "phase_one": {"named_private_waiver_count": PRIVATE_WAIVER_COUNT}, "suites": [suite_record(item) for item in SUITES]}
    require(validate_v4(previous) is previous, "reject the complete synthetic unchanged original suite vector")
    for index in range(len(SUITES)):
        forged = dict(previous)
        forged["suites"] = [dict(item) for item in previous["suites"]]
        forged["suites"][index]["case_execution_count"] += 1
        controls += reject(lambda item=forged: validate_v4(item), "reject one modified original suite")
    for key in ("suite_count", "case_execution_denominator", "family_count", "source_owner_count"):
        forged = dict(previous)
        forged[key] = forged[key] - 1
        controls += reject(lambda item=forged: validate_v4(item), "reject an omitted frozen producer obligation")
    forged = dict(previous)
    forged["suites"] = list(reversed(previous["suites"]))
    controls += reject(lambda item=forged: validate_v4(item), "reject reordered original suite records")
    forged = dict(previous)
    forged["phase_one"] = {"named_private_waiver_count": PRIVATE_WAIVER_COUNT - 1}
    controls += reject(lambda item=forged: validate_v4(item), "reject a changed original private-waiver denominator")
    require(controls == SUITE_COUNT + 6, "reject omitted original matrix hostile controls")
    return controls


def synthetic_guard_controls() -> int:
    """Falsify every exact guarded child, scope, and six-family invariant."""
    nested = {
        "suite": "subinterpreter_v2",
        "original_case_count": NESTED_CASE_COUNT,
        "expected_interpreters_created": NESTED_INTERPRETER_COUNT,
        "expected_interpreters_destroyed": NESTED_INTERPRETER_COUNT,
        "expected_case_interpreter_exec_calls": NESTED_CASE_EXECUTIONS,
        "require_child_guard_before_candidate_import": True,
        "unrestricted_creation": False,
        "actual_interpreters_created": 0,
        "actual_interpreters_destroyed": 0,
        "actual_case_interpreter_exec_calls": 0,
        "actual_child_guards_installed": 0,
        "candidate_status": "NOT RUN",
    }
    rules = {
        "locale_fixture_origin": "SEPARATE ORACLE PROCESS ONLY",
        "only_fork_case": "ReTests.test_regression_gh94675",
        "only_correctness_clock_case": "ReTests.test_search_anchor_at_beginning",
        "data_only_MAXGROUPS": 1073741823,
    }
    original = {
        "schema": "rebar-owned-candidate-runtime-independence-v2-source-freeze",
        "version": 2,
        "status": "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
        "holdout": "NOT OPENED",
        "source": owner_record(RUNTIME_GUARD_V2_OWNERS[0]),
        "protocol": owner_record(RUNTIME_GUARD_V2_OWNERS[1]),
        "subinterpreter_bootstrap": nested,
        "original_public_test_exceptions": rules,
        "first_party_candidate_families": {
            name: family.module for name, family in FAMILIES.items()
        },
    }
    require(
        validate_runtime_guard_v2(original) is original,
        "reject the complete synthetic first-party guard",
    )
    controls = 0
    for key, invalid in (
        ("schema", "rebar-forged-guard"),
        ("version", 1),
        ("status", "PASS"),
        ("runtime_non_delegation", "PASS"),
        ("qualified_candidate_count", 1),
        ("winner_selected", True),
        ("holdout", "OPENED"),
    ):
        forged = dict(original)
        forged[key] = invalid
        controls += reject(
            lambda item=forged: validate_runtime_guard_v2(item),
            "reject a forged operational runtime guard",
        )
    for name in ("source", "protocol"):
        forged = dict(original)
        forged[name] = dict(original[name])
        forged[name]["sha256"] = "0" * 64
        controls += reject(
            lambda item=forged: validate_runtime_guard_v2(item),
            "reject a substituted authenticated runtime guard owner",
        )
    for name, invalid in (
        ("original_case_count", 127),
        ("expected_interpreters_created", 10),
        ("expected_interpreters_destroyed", 10),
        ("expected_case_interpreter_exec_calls", 393),
        ("require_child_guard_before_candidate_import", False),
        ("unrestricted_creation", True),
        ("actual_interpreters_created", 1),
        ("actual_interpreters_destroyed", 1),
        ("actual_case_interpreter_exec_calls", 1),
        ("actual_child_guards_installed", 1),
        ("candidate_status", "PASS"),
    ):
        forged = dict(original)
        forged["subinterpreter_bootstrap"] = dict(nested)
        forged["subinterpreter_bootstrap"][name] = invalid
        controls += reject(
            lambda item=forged: validate_runtime_guard_v2(item),
            "reject a fabricated or incomplete guarded child lifecycle",
        )
    for name, invalid in (
        ("locale_fixture_origin", "CANDIDATE PROCESS"),
        ("only_fork_case", "ReTests.another_case"),
        ("only_correctness_clock_case", "benchmark"),
        ("data_only_MAXGROUPS", 0),
    ):
        forged = dict(original)
        forged["original_public_test_exceptions"] = dict(rules)
        forged["original_public_test_exceptions"][name] = invalid
        controls += reject(
            lambda item=forged: validate_runtime_guard_v2(item),
            "reject an unrestricted original locale, fork, timer, or private API",
        )
    for name in FAMILIES:
        forged = dict(original)
        forged["first_party_candidate_families"] = dict(
            original["first_party_candidate_families"]
        )
        forged["first_party_candidate_families"].pop(name)
        controls += reject(
            lambda item=forged: validate_runtime_guard_v2(item),
            "reject an omitted first-party runtime guard family",
        )
    require(controls == 30, "reject an incomplete genuine runtime guard falsification")
    return controls


def reject(callable_value: object, message: str) -> int:
    try:
        callable_value()
    except (ProducerError, UnicodeError, ValueError, TypeError, OSError):
        return 1
    raise ProducerError("a hostile source-only control succeeded: " + message)


def self_test() -> dict:
    source_runtime()
    validate_inventory()
    controls = 0
    for raw in (b'{"a":1,"a":2}', b'{"a":01}', b'{"a":1} garbage', b'"\\ud800"', b'{"a":1.0}', b'[true,]'):
        controls += reject(lambda item=raw: JsonReader(item).parse(), "reject malformed frozen JSON")
    for invalid in ("missing", "re", "regex", "other", "", 1, None):
        controls += reject(lambda item=invalid: family_spec(item), "reject external or borrowed regex engines")
    for invalid in ("missing", "holdout", "benchmark", "", 1, None):
        controls += reject(lambda item=invalid: suite_spec(item), "reject invented original suites")
    for name in FAMILIES:
        controls += reject(lambda item=FAMILIES[name]: require_selected(item), "reject uninstalled candidate runtime guard")
    sample = {"b": [True, False, None, 7], "a": "quoted\\\"\n"}
    require(JsonReader(canonical(sample)).parse() == sample, "reject non-round-tripping regex-free evidence decoder")
    require(controls == 25, "reject omitted decoder, unknown-family, or unknown-suite hostile controls")
    controls += synthetic_alias_controls()
    controls += synthetic_matrix_controls()
    controls += synthetic_guard_controls()
    require(controls == 110 and "re" not in sys.modules and "_sre" not in sys.modules, "reject a missing hostile control or preloaded CPython matching engine")
    return {"schema": SCHEMA + "-self-test", "status": "PASS", "checks": controls + 5, "hostile_controls": controls, "suite_count": SUITE_COUNT, "original_case_execution_denominator": CASE_DENOMINATOR, "original_public_record_count": ORIGINAL_PUBLIC_RECORD_COUNT, "named_private_waiver_count": PRIVATE_WAIVER_COUNT, "family_count": len(FAMILIES), "supplemental_case_count": SUPPLEMENTAL_CASE_COUNT, "supplemental_cases_counted_in_original_denominator": False, "effects": no_effects(), "candidate_matching": "NOT RUN", "candidate_qualification": "NOT ESTABLISHED", "runtime_non_delegation": "NOT ESTABLISHED", "performance": "NOT MEASURED", "memory": "NOT MEASURED", "holdout": "NOT OPENED", "winner_selected": False}


def validate_p0(p0: object) -> dict:
    require(type(p0) is dict and p0.get("schema") == "rebar-cpython-re-p0-completeness-v4" and p0.get("version") == 4 and p0.get("status") == "PASS" and p0.get("original_case_execution_denominator") == CASE_DENOMINATOR and p0.get("original_suite_count") == SUITE_COUNT and p0.get("original_obligation_count") == ORIGINAL_OBLIGATION_COUNT and p0.get("original_crosswalk_count") == ORIGINAL_CROSSWALK_COUNT and p0.get("original_named_private_waiver_count") == PRIVATE_WAIVER_COUNT and p0.get("first_party_candidate_family_count") == len(FAMILIES) and p0.get("qualified_candidate_count") == 0, "reject the complete frozen phase-one oracle")
    oracle = p0.get("original_oracle")
    require(type(oracle) is dict and oracle.get("case_execution_denominator") == CASE_DENOMINATOR and oracle.get("suite_count") == SUITE_COUNT and oracle.get("total_named_obligation_count") == ORIGINAL_OBLIGATION_COUNT and oracle.get("crosswalk_count") == ORIGINAL_CROSSWALK_COUNT and oracle.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT and oracle.get("public_method_count") == ORIGINAL_PUBLIC_RECORD_COUNT and tuple(oracle.get("named_private_waivers", [])) == PRIVATE_WAIVER_NAMES, "reject original phase-one obligation, crosswalk, public method, or named-waiver evidence")
    supplement = p0.get("actual_supplemental_two_reference")
    require(type(supplement) is dict and supplement.get("actual_reference_worker_count") == 2 and supplement.get("case_count_per_worker") == [SUPPLEMENTAL_CASE_COUNT, SUPPLEMENTAL_CASE_COUNT] and supplement.get("failed_per_worker") == [0, 0] and supplement.get("case_denominator_included_in_original_31237") is False, "reject either genuine independent supplemental Python reference")
    return p0


def validate_v4(previous: object) -> dict:
    require(type(previous) is dict and previous.get("schema") == "rebar-owned-six-family-original-p0-producer-v4-source-freeze" and previous.get("version") == 4 and previous.get("suite_count") == SUITE_COUNT and previous.get("case_execution_denominator") == CASE_DENOMINATOR and previous.get("family_count") == len(FAMILIES) and previous.get("source_owner_count") == 25, "reject the complete immutable V4 original producer")
    actual = previous.get("suites")
    require(type(actual) is list and len(actual) == SUITE_COUNT, "reject omitted legacy original suite")
    for row, suite in zip(actual, SUITES, strict=True):
        require(type(row) is dict and row.get("id") == suite.name and row.get("case_execution_count") == suite.case_count and row.get("source_relative") == suite.source_relative and row.get("source_sha256") == suite.source_sha256 and row.get("matrix_sha256") == suite.matrix_sha256 and row.get("reference_records_sha256") == suite.reference_sha256 and row.get("unchanged_original_producer_route") == suite.route, "reject changed legacy original suite: " + suite.name)
    phase = previous.get("phase_one")
    require(type(phase) is dict and phase.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT, "reject historical original named-private waivers")
    return previous


def validate_runtime_guard_v2(document: object) -> dict:
    """Bind the already published operational guard without installing it."""
    require(
        type(document) is dict
        and document.get("schema")
        == "rebar-owned-candidate-runtime-independence-v2-source-freeze"
        and document.get("version") == 2
        and document.get("status")
        == "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE"
        and document.get("runtime_non_delegation") == "NOT ESTABLISHED"
        and document.get("qualified_candidate_count") == 0
        and document.get("winner_selected") is False
        and document.get("holdout") == "NOT OPENED",
        "reject a substituted, run, or falsely qualifying first-party guard",
    )
    for label, item in (
        ("source", RUNTIME_GUARD_V2_OWNERS[0]),
        ("protocol", RUNTIME_GUARD_V2_OWNERS[1]),
    ):
        require(
            document.get(label) == owner_record(item),
            "reject the authenticated version-two runtime guard " + label,
        )
    nested = document.get("subinterpreter_bootstrap")
    require(
        type(nested) is dict
        and nested.get("suite") == "subinterpreter_v2"
        and nested.get("original_case_count") == NESTED_CASE_COUNT
        and nested.get("expected_interpreters_created")
        == NESTED_INTERPRETER_COUNT
        and nested.get("expected_interpreters_destroyed")
        == NESTED_INTERPRETER_COUNT
        and nested.get("expected_case_interpreter_exec_calls")
        == NESTED_CASE_EXECUTIONS
        and nested.get("require_child_guard_before_candidate_import") is True
        and nested.get("unrestricted_creation") is False
        and nested.get("actual_interpreters_created") == 0
        and nested.get("actual_interpreters_destroyed") == 0
        and nested.get("actual_case_interpreter_exec_calls") == 0
        and nested.get("actual_child_guards_installed") == 0
        and nested.get("candidate_status") == "NOT RUN",
        "reject a substituted or falsely executed guarded child lifecycle",
    )
    rules = document.get("original_public_test_exceptions")
    require(
        type(rules) is dict
        and rules.get("locale_fixture_origin") == "SEPARATE ORACLE PROCESS ONLY"
        and rules.get("only_fork_case") == "ReTests.test_regression_gh94675"
        and rules.get("only_correctness_clock_case")
        == "ReTests.test_search_anchor_at_beginning"
        and rules.get("data_only_MAXGROUPS") == 1073741823,
        "reject the exact original-only locale, fork, clock, or constants policy",
    )
    families = document.get("first_party_candidate_families")
    require(
        type(families) is dict
        and families == {name: family.module for name, family in FAMILIES.items()},
        "reject a borrowed or omitted runtime-guard family",
    )
    return document


def validate_graph(value: object) -> dict:
    require(type(value) is dict and value.get("schema") == "rebar-candidate-current-overview-v75-summary" and value.get("version") == 75 and value.get("status") == "PASS" and value.get("full_case_denominator") == CASE_DENOMINATOR and value.get("suite_count") == SUITE_COUNT and value.get("private_waiver_count") == PRIVATE_WAIVER_COUNT and value.get("qualified_candidate_count") == 0 and value.get("authenticated_evidence_owner_lower_bound") == 249 and value.get("authenticated_history_reference_lower_bound") == 254 and value.get("actual_candidate_imports") == 0 and value.get("runtime_no_delegation") == "NOT ESTABLISHED" and value.get("final_holdout_opened") is False, "reject the complete actually pushed version-75 six-family evidence graph")
    return value


def create_contract(source_sha256: str, protocol_sha256: str) -> dict:
    require(valid_digest(source_sha256) and valid_digest(protocol_sha256), "pin the independently fingerprinted V5 source and protocol")
    validate_inventory()
    return {"schema": CONTRACT_SCHEMA, "version": 5, "phase": "PHASE 2: CANDIDATES", "status": "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED", "status_scope": "FROZEN ORIGINAL-SUITE PRODUCER ONLY; NO ACTUAL CANDIDATE RESULT", "goal_sha256": GOAL_SHA256, "source": {"path": SOURCE_RELATIVE, "sha256": source_sha256}, "protocol": {"path": PROTOCOL_RELATIVE, "sha256": protocol_sha256}, "pinned_cpython": {"path": PINNED_PYTHON, "sha256": PINNED_PYTHON_SHA256, "version": "3.14.6"}, "phase_one_v4": {"source": owner_record(P0_OWNERS[0]), "protocol": owner_record(P0_OWNERS[1]), "contract": owner_record(P0_OWNERS[2]), "status": "PASS", "original_case_execution_denominator": CASE_DENOMINATOR, "suite_count": SUITE_COUNT, "original_obligation_count": ORIGINAL_OBLIGATION_COUNT, "original_crosswalk_count": ORIGINAL_CROSSWALK_COUNT, "named_private_waiver_count": PRIVATE_WAIVER_COUNT, "supplemental_case_count": SUPPLEMENTAL_CASE_COUNT, "supplemental_reference_count": 2, "supplemental_cases_counted_in_original_denominator": False}, "previous_v4_producer": {"source": owner_record(V4_OWNERS[0]), "protocol": owner_record(V4_OWNERS[1]), "contract": owner_record(V4_OWNERS[2]), "status": "IMMUTABLE HISTORY; NOT USED AS A CANDIDATE OBSERVER", "original_observer_calls": 0, "nested_observer_calls": 0}, "runtime_guard_v2": {"source": owner_record(RUNTIME_GUARD_V2_OWNERS[0]), "protocol": owner_record(RUNTIME_GUARD_V2_OWNERS[1]), "contract": owner_record(RUNTIME_GUARD_V2_OWNERS[2]), "status": "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE", "runtime_non_delegation": "NOT ESTABLISHED", "child_bootstrap": "AUTHENTICATED GUARD-FIRST BEFORE EVERY CANDIDATE IMPORT", "candidate_subprocesses": 0}, "current_graph": {"version": 75, "source": owner_record(GRAPH_OWNERS[0]), "inputs": owner_record(GRAPH_OWNERS[1]), "summary": owner_record(GRAPH_OWNERS[2]), "svg": owner_record(GRAPH_OWNERS[3]), "authenticated_evidence_owner_lower_bound": 249, "authenticated_history_reference_lower_bound": 254}, "original_upstream": {"test_source_path": UPSTREAM_TEST, "test_source_sha256": UPSTREAM_SHA256, "all_source_ordered_method_count": 165, "public_record_count": ORIGINAL_PUBLIC_RECORD_COUNT, "runnable_public_method_count": 151, "release_debug_skip_count": ORIGINAL_DEBUG_SKIP_COUNT, "private_waiver_count": PRIVATE_WAIVER_COUNT, "named_private_waivers": list(PRIVATE_WAIVER_NAMES), "matrix_sha256": SUITES[0].matrix_sha256, "reference_records_sha256": SUITES[0].reference_sha256, "harness": owner_record(HARNESS_OWNER), "original_evaluator": owner_record(ORIGINAL_EVALUATOR_OWNER), "candidate_evaluation": "LITERAL FROZEN CPYTHON TEST SOURCE AGAINST THE GUARDED SELECTED re ALIAS", "stdlib_regex_engine": "FORBIDDEN", "legacy_v4_original_observer": "FORBIDDEN"}, "guarded_nested_lifecycle": {"suite": "subinterpreter_v2", "case_count": NESTED_CASE_COUNT, "case_execution_count": NESTED_CASE_EXECUTIONS, "created_interpreter_count": NESTED_INTERPRETER_COUNT, "destroyed_interpreter_count": NESTED_INTERPRETER_COUNT, "legacy_v4_bootstrap": "FORBIDDEN", "legacy_v4_cleanup": "IMMUTABLE ORIGINAL SOURCE; GUARDED STACK NEVER RESTORES STDLIB", "actual_case_execution_count": 0, "actual_created_interpreter_count": 0, "status": "SOURCE FROZEN; GUARDED CHILD CAMPAIGN NOT RUN", "implementation": "AUTHENTICATED V2 GUARD-FIRST BOOTSTRAP; EXACT ORIGINAL 128 CASES, 394 CALLS, AND 11 INTERPRETERS", "actual_child_guards_installed": 0, "unrestricted_creation": False}, "corrected_candidate_context_public_type_reference": {"reference_records_sha256": CORRECTED_PUBLIC_RECORDS_SHA256, "affected_cohort_records_sha256": CORRECTED_PUBLIC_COHORT_RECORDS_SHA256, "reference_worker_process_ids": list(CORRECTED_PUBLIC_REFERENCE_PIDS), "case_count": 6912, "reference_status": "PASS"}, "suite_count": SUITE_COUNT, "case_execution_denominator": CASE_DENOMINATOR, "original_obligation_count": ORIGINAL_OBLIGATION_COUNT, "original_crosswalk_count": ORIGINAL_CROSSWALK_COUNT, "named_private_waiver_count": PRIVATE_WAIVER_COUNT, "named_private_waivers": list(PRIVATE_WAIVER_NAMES), "supplemental_case_count": SUPPLEMENTAL_CASE_COUNT, "supplemental_cases_counted_in_original_denominator": False, "source_owner_count": 25, "family_count": len(FAMILIES), "families": [{"name": spec.name, "module": spec.module, "adapter_relative": spec.adapter_relative, "bridge_module": spec.bridge_module, "engine_relative": spec.engine_relative, "bridge_relative": spec.bridge_relative, "combined_native": spec.combined_native, "owned_ctypes": spec.owned_ctypes, "source_owners": [{"path": path, "sha256": sha, "bytes": count} for path, sha, count in spec.source_owners]} for spec in FAMILIES.values()], "suites": [suite_record(suite) for suite in SUITES], "runtime_bootstrap": {"python_flags": ["-I", "-B", "-S"], "candidate_module_imported_before_guard": False, "guard_installed_before_candidate_import": True, "selected_re_alias_must_equal_candidate": True, "stdlib_re_forbidden": True, "stdlib_sre_forbidden": True, "external_regex_packages_forbidden": True, "cross_candidate_delegation_forbidden": True, "data_only_re_constants_maxgroups": 1073741823, "candidate_subprocesses_permitted": False, "external_prepared_locale_fixture_required": True, "original_fork_case_scoped": True, "fallback_permitted": False}, "verification_effects": no_effects(), "actual_candidate_imports": 0, "actual_candidate_workers": 0, "actual_reference_workers": 0, "candidate_matching": "NOT RUN", "candidate_qualification": "NOT ESTABLISHED", "qualified_candidate_count": 0, "runtime_non_delegation": "NOT ESTABLISHED", "performance": "NOT MEASURED", "memory": "NOT MEASURED", "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED", "winner_selected": False}


def verify_frozen_context(source_sha: str, protocol_sha: str, contract_sha: str) -> dict:
    source_runtime()
    validate_inventory()
    read_self(SOURCE_RELATIVE, source_sha)
    read_self(PROTOCOL_RELATIVE, protocol_sha)
    document = JsonReader(read_self(DOCUMENT_RELATIVE, contract_sha, maximum=MAX_JSON_BYTES)).parse()
    require(document == create_contract(source_sha, protocol_sha), "reject missing, substituted, or silently weakened complete V5 contract")
    for item in P0_OWNERS + V4_OWNERS + GRAPH_OWNERS + RUNTIME_GUARD_V2_OWNERS + (HARNESS_OWNER, ORIGINAL_EVALUATOR_OWNER, DIRECT_GATE_OWNER, NESTED_OWNER):
        read_owner(item, maximum=MAX_JSON_BYTES if item[0].endswith(".json") else MAX_SOURCE_BYTES)
    p0 = validate_p0(JsonReader(read_owner(P0_OWNERS[2], maximum=MAX_JSON_BYTES)).parse())
    previous = validate_v4(JsonReader(read_owner(V4_OWNERS[2], maximum=MAX_JSON_BYTES)).parse())
    graph = validate_graph(JsonReader(read_owner(GRAPH_OWNERS[2], maximum=MAX_JSON_BYTES)).parse())
    validate_runtime_guard_v2(JsonReader(read_owner(RUNTIME_GUARD_V2_OWNERS[2], maximum=MAX_JSON_BYTES)).parse())
    require(len(previous["suites"]) == len(p0["original_oracle"]["suites"]) == len(SUITES), "reject missing original oracle suite mapping")
    require("re" not in sys.modules and "_sre" not in sys.modules, "a source-only check preloaded a CPython matching engine")
    return {"schema": SCHEMA + "-frozen-context", "status": "PASS", "source_sha256": source_sha, "protocol_sha256": protocol_sha, "contract_sha256": contract_sha, "graph_version": graph["version"], "authenticated_evidence_owner_lower_bound": graph["authenticated_evidence_owner_lower_bound"], "authenticated_history_reference_lower_bound": graph["authenticated_history_reference_lower_bound"], "suite_count": SUITE_COUNT, "original_case_execution_denominator": CASE_DENOMINATOR, "original_public_record_count": ORIGINAL_PUBLIC_RECORD_COUNT, "named_private_waiver_count": PRIVATE_WAIVER_COUNT, "family_count": len(FAMILIES), "supplemental_case_count": SUPPLEMENTAL_CASE_COUNT, "supplemental_cases_counted_in_original_denominator": False, "effects": no_effects(), "candidate_matching": "NOT RUN", "candidate_qualification": "NOT ESTABLISHED", "runtime_non_delegation": "NOT ESTABLISHED", "performance": "NOT MEASURED", "memory": "NOT MEASURED", "holdout": "NOT OPENED", "winner_selected": False}


def parse_arguments(arguments: list[str]) -> dict:
    require(type(arguments) is list and len(arguments) >= 1 and arguments[0] in ("--self-test", "--verify-frozen-context", "--render-contract"), "select exactly one safe source-only producer mode")
    result = {"mode": arguments[0]}
    index = 1
    allowed = {"--source-sha256": "source", "--protocol-sha256": "protocol", "--contract-sha256": "contract", "--document-sha256": "contract"}
    while index < len(arguments):
        require(arguments[index] in allowed and index + 1 < len(arguments), "reject unknown or incomplete pinned producer option")
        label = allowed[arguments[index]]
        require(label not in result and valid_digest(arguments[index + 1]), "reject duplicate or invalid producer pin")
        result[label] = arguments[index + 1]
        index += 2
    if result["mode"] == "--render-contract":
        require(set(result) == {"mode", "source", "protocol"}, "pin source and protocol before contract rendering")
    if result["mode"] == "--verify-frozen-context":
        require(set(result) == {"mode", "source", "protocol", "contract"}, "pin all three independently fingerprinted producer owners")
    return result


def main(arguments: list[str] | None = None) -> int:
    try:
        options = parse_arguments(list(sys.argv[1:] if arguments is None else arguments))
        if options["mode"] == "--self-test":
            result = self_test()
        elif options["mode"] == "--render-contract":
            source_runtime()
            read_self(SOURCE_RELATIVE, options["source"])
            read_self(PROTOCOL_RELATIVE, options["protocol"])
            result = create_contract(options["source"], options["protocol"])
        else:
            result = verify_frozen_context(options["source"], options["protocol"], options["contract"])
        os.write(1, canonical(result))
        return 0
    except BaseException as error:
        try:
            os.write(2, ("V5 original producer rejected: " + type(error).__name__ + ": " + str(error) + "\n").encode("utf-8", "backslashreplace"))
        except BaseException:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
