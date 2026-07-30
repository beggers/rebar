#!/usr/bin/env python3
"""Freeze and exclusively publish independently owned Zig public-adapter fixes."""

from __future__ import annotations

import _io
import argparse
import ast
import builtins
import enum
import hashlib
import json
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SELF = "tools/apply_owned_zig_public_adapter_semantics_v1.py"
PROTOCOL = "oracle/phase2/ZIG-PUBLIC-ADAPTER-SEMANTICS-V1.md"
CONTRACT = "oracle/phase2/zig-public-adapter-semantics-v1.json"
TARGET = "candidates/zig/variants/public_adapter_semantics_v1/zig_candidate.py"
INPUT = (
    "candidates/zig/variants/scanner_phrase_guard_clean_lifetime_v1/"
    "zig_candidate.py"
)
INPUT_SHA256 = "e9e052fdd50bcec54145b828b1353cf082c6bc13869176486bcfa41d1624ab50"
INPUT_BYTES = 67294
SETTER_SAFE_SHA256 = "c16a6e4c9745eff3a55dcf85eb14c26ec84092d70ddbc40d5e841ab0140d3032"
SETTER_SAFE_BYTES = 67335
RECEIPT = (
    "oracle/phase2/evidence/repaired-zig-original-campaign-v13-"
    "phase2-v13-zig-guard-clean-lifetime-v1-original-p0-v13-"
    "failures-publication-receipt.json"
)
RECEIPT_SHA256 = "b3443a647c638cbbbe7905a2c668a734770f38cb678f06a387af497917fc4bca"
V15_SOURCE = "tools/run_owned_repaired_zig_original_campaign_v15.py"
V15_SOURCE_SHA256 = "4a0f50d3e6f5cc9ca987f306cb8b412149b0253d9b5add84abc05721a1a14c47"
V15_PROTOCOL = "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V15.md"
V15_PROTOCOL_SHA256 = "7576c945a29e691cdf211a1067dfa5d88837d19eca634c4114b1b58737e42950"
V15_CONTRACT = "oracle/phase2/repaired-zig-original-campaign-v15.json"
V15_CONTRACT_SHA256 = "311fa3803b1dae37f8aebb430584eb8d7c085b00302e11f0929bda71124dd205"
SETTER_SOURCE = "tools/apply_owned_zig_deallocator_setattr_source_repair_v2.py"
SETTER_SOURCE_SHA256 = "42d9ceea51f8a8cb4ba980580ccbc5b079134bc8330bc65b3c05e2f1ec83395b"
SETTER_PROTOCOL = "oracle/phase2/ZIG-DEALLOCATOR-SETATTR-SOURCE-REPAIR-V2.md"
SETTER_PROTOCOL_SHA256 = "5aad1504d2b834b2d794cff3659462bff89c573cb8f108010fd7f413683fc359"
SETTER_CONTRACT = "oracle/phase2/zig-deallocator-setattr-source-repair-v2.json"
SETTER_CONTRACT_SHA256 = "b0b87af889a9147975ccfefc8d3f9cf03f5200a6e6ad90cfaa8679c8c9b5d084"
PUBLIC_ORACLE = "tools/independent_public_type_identity_serialization_v1.py"
PUBLIC_ORACLE_SHA256 = "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20"

OLD_FINALIZER = (
    "    def __del__(self, _free=_zig_bridge.free, _getattr=getattr):\n"
    "        handle = _getattr(self, \"_handle\", None)\n"
    "        if handle:\n"
    "            self._handle = None\n"
    "            _free(handle)\n"
)
NEW_FINALIZER = (
    "    def __del__(self, _free=_zig_bridge.free, _getattr=getattr, "
    "_setattr=object.__setattr__):\n"
    "        handle = _getattr(self, \"_handle\", None)\n"
    "        if handle:\n"
    "            _setattr(self, \"_handle\", None)\n"
    "            _free(handle)\n"
)
OLD_FLAG_BODY = (
    "    def __repr__(self):\n"
    "        value = int(self)\n"
    "        if not value:\n"
    "            return \"re.NOFLAG\"\n"
    "        ordered = ((self.ASCII, \"ASCII\"), (self.IGNORECASE, \"IGNORECASE\"), "
    "(self.LOCALE, \"LOCALE\"), (self.UNICODE, \"UNICODE\"), "
    "(self.MULTILINE, \"MULTILINE\"), (self.DOTALL, \"DOTALL\"), "
    "(self.VERBOSE, \"VERBOSE\"), (self.DEBUG, \"DEBUG\"))\n"
    "        known = sum(int(bit) for bit, _ in ordered)\n"
    "        parts = [f\"re.{name}\" for bit, name in ordered if value & int(bit)]\n"
    "        unknown = value & ~known\n"
    "        if unknown:\n"
    "            parts.append(hex(unknown))\n"
    "        return \"|\".join(parts)\n"
)
NEW_FLAG_BODY = (
    "    @classmethod\n"
    "    def _missing_(cls, value):\n"
    "        member = super()._missing_(value)\n"
    "        if member is None:\n"
    "            return None\n"
    "        known = sum(int(flag) for flag in cls)\n"
    "        unknown = int(member) & ~known\n"
    "        if unknown and int(member) & known:\n"
    "            names = [flag.name for flag in sorted(cls, key=int)\n"
    "                     if int(member) & int(flag)]\n"
    "            member._name_ = \"|\".join(names + [hex(unknown)])\n"
    "        return member\n\n"
    "    def __repr__(self):\n"
    "        value = int(self)\n"
    "        if not value:\n"
    "            return \"re.NOFLAG\"\n"
    "        ordered = sorted(type(self), key=int)\n"
    "        known = sum(int(flag) for flag in ordered)\n"
    "        unknown = value & ~known\n"
    "        parts = [f\"re.{flag.name}\" for flag in ordered\n"
    "                 if value & int(flag)]\n"
    "        if unknown:\n"
    "            if not parts:\n"
    "                return f\"re.RegexFlag({value})\"\n"
    "            parts.append(hex(unknown))\n"
    "        return \"|\".join(parts)\n"
)
OLD_ERROR_HEADER = "class PatternError(Exception):\n    def __init__("
NEW_ERROR_HEADER = "class PatternError(Exception):\n    __module__ = \"re\"\n\n    def __init__("
OLD_EQUALITY = (
    "        return (type(self.pattern), self.pattern, self.flags) == "
    "(type(other.pattern), other.pattern, other.flags)\n"
)
NEW_EQUALITY = "        return (self.pattern, self.flags) == (other.pattern, other.flags)\n"
OLD_HASH = "        return hash((type(self.pattern), self.pattern, self.flags))\n"
NEW_HASH = "        return hash((self.pattern, self.flags))\n"
OLD_FLAG_NORMALIZATION = (
    "def compile(pattern, flags=0):\n"
    "    if isinstance(flags, RegexFlag):\n"
    "        flags = flags.value\n"
)
NEW_FLAG_NORMALIZATION = (
    "def compile(pattern, flags=0):\n"
    "    if isinstance(flags, RegexFlag):\n"
    "        flags = flags.value\n"
    "    elif not isinstance(flags, int):\n"
    "        flags & int(UNICODE)\n"
)

SUITES = (
    ("original_bounded_v5", 151, 0),
    ("public_v3", 864, 0),
    ("scanner_v3", 1024, 0),
    ("buffer_v3", 768, 0),
    ("managed_v1", 1024, 0),
    ("scanner_verbose_v1", 2854, 620),
    ("public_types_v1", 6912, 248),
    ("substitution_v2", 5120, 64),
    ("shape_v2", 10240, 672),
    ("public_surface_v19", 1376, 96),
    ("subinterpreter_v2", 128, None),
    ("pep688_v4", 264, 0),
    ("threaded_pattern_v1", 512, 0),
)
CORRECTED_COHORTS = {
    "module-public-error-alias": 96,
    "cache-pattern-type-separation": 96,
    "flags-unknown-bit-retention": 12,
    "pattern-and-match-representation": 12,
    "regexflag-intflag-and-noflag": 32,
    "unknown-flags-actually-compiled": 32,
    "mixed-inverted-and-indexed-flags": 32,
}
PRESERVED_FAILURES = {
    "scanner_verbose_v1": 620,
    "pickle-match-rejection": 32,
    "substitution_v2": 64,
    "shape_v2": 672,
}
ZERO_EFFECTS = (
    "candidate_imports", "candidate_processes", "candidate_matching_calls",
    "native_library_loads", "archive_opens", "holdout_opens",
    "benchmark_opens", "seed_opens", "private_root_opens",
    "files_written", "canonical_targets_changed", "subinterpreters_created",
    "reference_workers", "compiler_processes", "clock_samples",
)


class FreezeError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FreezeError(message)


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def absolute(relative: str) -> str:
    require(type(relative) is str and relative and not relative.startswith("/"),
            "reject non-relative first-party owner")
    require(".." not in relative.split("/"), "reject parent traversal")
    return os.path.join(ROOT, relative)


class SourceWall:
    def __init__(self, allowed: set[str]):
        self.allowed = {absolute(owner) for owner in allowed}
        self.active = False
        self.rejections = 0

    def audit(self, event: str, arguments: tuple[object, ...]) -> None:
        if not self.active:
            return
        if event == "open":
            require(len(arguments) == 3 and type(arguments[0]) is str,
                    "source wall rejected unnamed file descriptor")
            path, mode, flags = arguments
            require(path in self.allowed, "source wall rejected unlisted owner")
            require(mode in (None, "r", "rb"), "source wall rejected non-read mode")
            require(type(flags) is int and flags & os.O_ACCMODE == os.O_RDONLY,
                    "source wall rejected mutable descriptor")
            forbidden = os.O_CREAT | os.O_TRUNC | os.O_APPEND
            require(flags & forbidden == 0, "source wall rejected file creation")
            return
        if event == "import":
            name = arguments[0] if arguments else ""
            banned = ("candidates", "re", "_sre", "regex", "ctypes", "inspect")
            require(not any(name == prefix or name.startswith(prefix + ".")
                            for prefix in banned),
                    "source wall rejected regex engine or candidate import")
            return
        forbidden_prefixes = (
            "subprocess.", "socket.", "ctypes.", "_posixsubprocess.",
            "os.mkdir", "os.rmdir", "os.remove", "os.rename", "os.replace",
            "os.unlink", "os.chmod", "os.chown", "os.system", "os.putenv",
            "os.posix_spawn", "os.fork", "os.exec", "threading.",
        )
        require(not event.startswith(forbidden_prefixes),
                "source wall rejected external action " + event)

    def __enter__(self) -> "SourceWall":
        sys.addaudithook(self.audit)
        self.active = True
        return self

    def __exit__(self, kind: object, value: object, traceback: object) -> None:
        self.active = False


def read_owner(relative: str, expected_sha256: str | None = None,
               expected_size: int | None = None) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(absolute(relative), flags)
    try:
        metadata = os.fstat(descriptor)
        require(stat.S_ISREG(metadata.st_mode), "reject nonregular owner " + relative)
        require(metadata.st_nlink == 1, "reject multiply-linked owner " + relative)
        require(metadata.st_uid == os.getuid(), "reject foreign owner " + relative)
        require(metadata.st_size <= 1024 * 1024, "reject oversized owner " + relative)
        if expected_size is not None:
            require(metadata.st_size == expected_size, "reject owner size " + relative)
        chunks = []
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            chunks.append(chunk)
    finally:
        os.close(descriptor)
    data = b"".join(chunks)
    if expected_sha256 is not None:
        require(digest(data) == expected_sha256, "reject owner digest " + relative)
    return data


def replace_once(source: str, before: str, after: str, label: str) -> str:
    require(source.count(before) == 1, "reject nonunique source obligation " + label)
    return source.replace(before, after, 1)


def derive(source: bytes) -> tuple[bytes, bytes]:
    require(digest(source) == INPUT_SHA256 and len(source) == INPUT_BYTES,
            "reject altered first-party Zig lifetime input")
    text = source.decode("utf-8")
    setter_safe = replace_once(text, OLD_FINALIZER, NEW_FINALIZER, "owned finalizer")
    setter_bytes = setter_safe.encode()
    require(digest(setter_bytes) == SETTER_SAFE_SHA256
            and len(setter_bytes) == SETTER_SAFE_BYTES,
            "reject independently frozen first-party setter repair")
    corrected = replace_once(setter_safe, OLD_FLAG_BODY, NEW_FLAG_BODY,
                             "first-party public flag representation")
    corrected = replace_once(corrected, OLD_ERROR_HEADER, NEW_ERROR_HEADER,
                             "first-party public error module")
    corrected = replace_once(corrected, OLD_EQUALITY, NEW_EQUALITY,
                             "first-party pattern subclass equality")
    corrected = replace_once(corrected, OLD_HASH, NEW_HASH,
                             "first-party pattern subclass hash")
    corrected = replace_once(corrected, OLD_FLAG_NORMALIZATION,
                             NEW_FLAG_NORMALIZATION,
                             "first-party indexed flag rejection")
    corrected_bytes = corrected.encode()
    verify_source_ast(source, setter_bytes, corrected_bytes)
    return setter_bytes, corrected_bytes


def top_classes(tree: ast.Module) -> dict[str, ast.ClassDef]:
    return {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}


def methods(node: ast.ClassDef) -> dict[str, ast.AST]:
    return {item.name: item for item in node.body
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))}


def verify_source_ast(original: bytes, setter_safe: bytes, corrected: bytes) -> None:
    initial = ast.parse(original)
    setter = ast.parse(setter_safe)
    final = ast.parse(corrected)
    require(not any(isinstance(node, (ast.Import, ast.ImportFrom))
                    and any(alias.name in {"re", "_sre", "regex"}
                            or alias.name.startswith("candidates.")
                            and alias.name != "candidates"
                            for alias in node.names)
                    for node in ast.walk(final)),
            "reject delegated regular-expression engine import")
    initial_classes = top_classes(initial)
    setter_classes = top_classes(setter)
    final_classes = top_classes(final)
    require(initial_classes.keys() == setter_classes.keys() == final_classes.keys(),
            "reject added first-party parser or candidate class")
    require(set(methods(final_classes["RegexFlag"]))
            == set(methods(initial_classes["RegexFlag"])) | {"_missing_"},
            "reject unexpected public flag methods")
    require(set(methods(final_classes["PatternError"]))
            == set(methods(initial_classes["PatternError"])),
            "reject unexpected public error methods")
    require(set(methods(final_classes["Pattern"]))
            == set(methods(initial_classes["Pattern"])),
            "reject unexpected public pattern methods")
    permitted = {"RegexFlag", "PatternError", "Pattern"}
    for name, original_class in initial_classes.items():
        if name not in permitted:
            require(ast.dump(original_class, include_attributes=False)
                    == ast.dump(final_classes[name], include_attributes=False),
                    "reject changed independent Zig class " + name)
    initial_methods = methods(initial_classes["Pattern"])
    final_methods = methods(final_classes["Pattern"])
    for name in initial_methods:
        if name not in {"__del__", "__eq__", "__hash__"}:
            require(ast.dump(initial_methods[name], include_attributes=False)
                    == ast.dump(final_methods[name], include_attributes=False),
                    "reject changed first-party Zig matching method " + name)
    initial_functions = {node.name: node for node in initial.body
                         if isinstance(node, ast.FunctionDef)}
    final_functions = {node.name: node for node in final.body
                       if isinstance(node, ast.FunctionDef)}
    require(initial_functions.keys() == final_functions.keys(),
            "reject added public adapter top-level function")
    for name in initial_functions:
        if name != "compile":
            require(ast.dump(initial_functions[name], include_attributes=False)
                    == ast.dump(final_functions[name], include_attributes=False),
                    "reject changed first-party parser or scanner " + name)


def verify_history(receipt: bytes, v15: bytes, oracle: bytes) -> None:
    prior = json.loads(receipt)
    require(prior.get("candidate_status") == "FAIL"
            and prior.get("case_execution_denominator") == 31237
            and prior.get("actual_candidate_workers") == 13
            and prior.get("verified_passing_case_count") == 4607
            and prior.get("observed_semantic_mismatch_lower_bound") == 1700
            and prior.get("semantic_mismatch_count") == "NOT MEASURED",
            "reject incomplete first-party Zig original result")
    rows = prior.get("original_suite_diagnostics")
    require(isinstance(rows, list) and len(rows) == len(SUITES),
            "reject altered original Zig suite denominator")
    for row, (suite, count, mismatches) in zip(rows, SUITES, strict=True):
        require(row.get("suite") == suite
                and row.get("case_execution_denominator") == count,
                "reject changed original Zig suite " + suite)
        if mismatches is None:
            require(row.get("infrastructure_failure") is True
                    and row.get("observed_semantic_mismatch_count") == "NOT MEASURED",
                    "reject fabricated original Zig child-interpreter result")
        else:
            require(row.get("observed_semantic_mismatch_count") == mismatches,
                    "reject lost original Zig mismatch " + suite)
    frozen = json.loads(v15)
    require(frozen.get("family") == "zig"
            and frozen.get("original_oracle", {}).get("case_execution_denominator") == 31237
            and frozen.get("first_party_in_memory_setter_safe_adapter", {})
                   .get("whole_source_sha256") == SETTER_SAFE_SHA256,
            "reject independently frozen Zig campaign or finalizer")
    for witness in (
        b"cache-pattern-type-separation", b"module-public-error-alias",
        b"flags-unknown-bit-retention", b"pickle-match-rejection",
    ):
        require(witness in oracle, "reject absent public-oracle witness " + str(witness))


def snippet_class(tree: ast.Module, name: str, namespace: dict[str, object]) -> type:
    definition = top_classes(tree)[name]
    module = ast.Module(body=[definition], type_ignores=[])
    exec(compile(module, "<synthetic-first-party-zig-source>", "exec"), namespace)
    result = namespace[name]
    require(isinstance(result, type), "reject synthetic adapter class")
    return result


def self_test(candidate: bytes) -> int:
    controls = 0
    tree = ast.parse(candidate)
    flag_namespace: dict[str, object] = {"enum": enum, "__name__": "re"}
    flag_type = snippet_class(tree, "RegexFlag", flag_namespace)
    require(repr(flag_type(0)) == "re.NOFLAG", "reject NOFLAG representation")
    controls += 1
    require(repr(flag_type(1048576)) == "re.RegexFlag(1048576)",
            "reject standalone unknown flag representation")
    controls += 1
    require(repr(flag_type(258)) == "re.IGNORECASE|re.ASCII",
            "reject numeric public flag ordering")
    controls += 1
    require(flag_type(32 | 0x4036000).name == "UNICODE|0x4036000",
            "reject hexadecimal unknown flag name")
    controls += 1
    require(repr(flag_type(32 | 0x4036000)) == "re.UNICODE|0x4036000",
            "reject mixed public flag representation")
    controls += 1
    require(str(flag_type(0)) == "re.NOFLAG", "reject NOFLAG text")
    controls += 1
    error_type = snippet_class(tree, "PatternError", {"__name__": "synthetic"})
    require(error_type.__module__ == "re", "reject public PatternError module")
    controls += 1
    require(str(error_type("failure", "a\nb", 2))
            == "failure at position 2 (line 2, column 1)",
            "reject existing first-party PatternError behavior")
    controls += 1

    pattern_methods = methods(top_classes(tree)["Pattern"])
    releases: list[object] = []
    bridge = types.SimpleNamespace(free=releases.append)
    namespace = {"_zig_bridge": bridge, "__name__": "synthetic"}
    body = [pattern_methods[name] for name in ("__del__", "__eq__", "__hash__")]
    synthetic = ast.ClassDef(name="Pattern", bases=[], keywords=[], body=body,
                             decorator_list=[], type_params=[])
    ast.fix_missing_locations(synthetic)
    exec(compile(ast.Module(body=[synthetic], type_ignores=[]),
                 "<synthetic-owned-zig-pattern>", "exec"), namespace)
    pattern_type = namespace["Pattern"]
    first = pattern_type()
    second = pattern_type()
    first.pattern = "value"
    second.pattern = type("TextSubclass", (str,), {})("value")
    first.flags = second.flags = 16
    require(first == second and hash(first) == hash(second),
            "reject public subclass-pattern value equality")
    controls += 1
    require(type(first.pattern) is not type(second.pattern),
            "reject preserved public pattern type separation")
    controls += 1
    first._handle = 17
    first.__del__()
    first.__del__()
    require(first._handle is None and releases == [17],
            "reject safe exactly-once first-party Zig finalization")
    controls += 1

    compile_function = next(node for node in tree.body
                            if isinstance(node, ast.FunctionDef)
                            and node.name == "compile")
    normalize_body = compile_function.body[:1]
    normalize_body.append(ast.Return(value=ast.Name(id="flags", ctx=ast.Load())))
    normalize = ast.FunctionDef(
        name="normalize", args=ast.arguments(posonlyargs=[],
        args=[ast.arg(arg="flags")], kwonlyargs=[], kw_defaults=[], defaults=[]),
        body=normalize_body, decorator_list=[], returns=None, type_comment=None,
        type_params=[])
    ast.fix_missing_locations(normalize)
    normalization_namespace = {
        "RegexFlag": flag_type, "UNICODE": flag_type.UNICODE,
        "__name__": "synthetic",
    }
    exec(compile(ast.Module(body=[normalize], type_ignores=[]),
                 "<synthetic-owned-zig-flags>", "exec"), normalization_namespace)

    class IndexedFlag:
        def __index__(self) -> int:
            return 16

    try:
        normalization_namespace["normalize"](IndexedFlag())
    except TypeError as error:
        require(str(error) == "unsupported operand type(s) for &: 'IndexedFlag' and 'int'",
                "reject Python indexed-flag exception")
        controls += 1
    else:
        raise FreezeError("reject accepted unsupported indexed flags")
    require(normalization_namespace["normalize"](flag_type.IGNORECASE) == 2,
            "reject existing RegexFlag conversion")
    controls += 1
    require(normalization_namespace["normalize"](0x18E000) == 0x18E000,
            "reject real unknown integer flags")
    controls += 1

    poison_blocks = (
        (OLD_FINALIZER, "obsolete unsafe finalizer"),
        ("import re\n", "stdlib regex delegation"),
        ("import _sre\n", "CPython engine delegation"),
        ("import regex\n", "external regex delegation"),
    )
    text = candidate.decode()
    for marker, label in poison_blocks:
        require(marker not in text, "reject " + label)
        controls += 1
    require("(type(pattern), pattern, flags)" in text,
            "reject separately keyed base/subclass cache entries")
    controls += 1
    require("self._handle = None\n            _free(handle)" not in text,
            "reject teardown-dependent public setter")
    controls += 1
    return controls


def owners(options: argparse.Namespace) -> set[str]:
    chosen = {
        SELF, PROTOCOL, INPUT, RECEIPT, V15_SOURCE, V15_PROTOCOL,
        V15_CONTRACT, SETTER_SOURCE, SETTER_PROTOCOL, SETTER_CONTRACT,
        PUBLIC_ORACLE,
    }
    if options.contract_sha256:
        chosen.add(CONTRACT)
    return chosen


def build(options: argparse.Namespace, *, run_self_test: bool) -> dict[str, object]:
    with SourceWall(owners(options)):
        own = read_owner(SELF, options.source_sha256, options.source_bytes)
        protocol = read_owner(PROTOCOL, options.protocol_sha256)
        original = read_owner(INPUT, options.input_sha256, options.input_bytes)
        receipt = read_owner(RECEIPT, options.receipt_sha256)
        v15_source = read_owner(V15_SOURCE, options.v15_source_sha256)
        v15_protocol = read_owner(V15_PROTOCOL, options.v15_protocol_sha256)
        v15_contract = read_owner(V15_CONTRACT, options.v15_contract_sha256)
        read_owner(SETTER_SOURCE, options.setter_source_sha256)
        read_owner(SETTER_PROTOCOL, options.setter_protocol_sha256)
        read_owner(SETTER_CONTRACT, options.setter_contract_sha256)
        oracle = read_owner(PUBLIC_ORACLE, options.public_oracle_sha256)
        verify_history(receipt, v15_contract, oracle)
        setter, variant = derive(original)
        require(digest(setter) == options.setter_adapter_sha256,
                "reject caller-pinned first-party safe setter")
        if options.variant_sha256 is not None:
            require(digest(variant) == options.variant_sha256,
                    "reject caller-pinned public Zig source")
        if options.variant_bytes is not None:
            require(len(variant) == options.variant_bytes,
                    "reject caller-pinned public Zig source size")
        require(not os.path.lexists(absolute(TARGET)),
                "reject already materialized Zig public adapter")
        controls = self_test(variant) if run_self_test else 0
        contract = {
            "schema": "rebar-owned-zig-public-adapter-semantics-v1-source-freeze",
            "status": "SOURCE FROZEN; CANDIDATE NOT RUN",
            "family": "zig",
            "source": {"path": SELF, "sha256": digest(own), "bytes": len(own)},
            "protocol": {"path": PROTOCOL, "sha256": digest(protocol),
                         "bytes": len(protocol)},
            "input": {"path": INPUT, "sha256": digest(original),
                      "bytes": len(original)},
            "independent_setter_safe_input": {
                "sha256": digest(setter), "bytes": len(setter),
                "materialized": False,
            },
            "prospective_variant": {
                "path": TARGET, "sha256": digest(variant), "bytes": len(variant),
                "physical_status": "NOT MATERIALIZED",
            },
            "original_oracle": {
                "case_execution_denominator": 31237,
                "suite_count": 13,
                "prior_verified_passing_cases": 4607,
                "prior_measured_semantic_mismatches": 1700,
                "prior_unfinished_subinterpreter_cases": 128,
                "prior_total_mismatch_count": "NOT MEASURED",
                "suite_mismatch_counts": {
                    suite: count for suite, _cases, count in SUITES
                    if count is not None and count != 0
                },
            },
            "preserved_public_failures": PRESERVED_FAILURES,
            "source_modeled_corrected_cohorts": CORRECTED_COHORTS,
            "source_modeled_corrected_case_count": sum(CORRECTED_COHORTS.values()),
            "source_modeled_remaining_measured_failures": sum(PRESERVED_FAILURES.values()),
            "modeled_results_are_actual_runs": False,
            "candidate_correctness": "NOT RUN",
            "candidate_qualified": False,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "native_engine_changed": False,
            "native_bridge_changed": False,
            "cross_candidate_engine_used": False,
            "stdlib_regex_engine_used": False,
            "external_regex_package_used": False,
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "source_only_effects": {name: 0 for name in ZERO_EFFECTS},
            "source_only_self_test_control_count": self_test(variant),
            "frozen_authority": {
                "v13_failure_receipt": digest(receipt),
                "v15_source": digest(v15_source),
                "v15_protocol": digest(v15_protocol),
                "v15_contract": digest(v15_contract),
                "setter_source": options.setter_source_sha256,
                "setter_protocol": options.setter_protocol_sha256,
                "setter_contract": options.setter_contract_sha256,
                "independent_public_oracle_source": digest(oracle),
            },
            "winner_selected": False,
        }
        if options.contract_sha256:
            frozen = read_owner(CONTRACT, options.contract_sha256)
            require(frozen == canonical(contract),
                    "reject changed complete Zig public adapter contract")
        if run_self_test:
            require(controls == contract["source_only_self_test_control_count"],
                    "reject unstable source-only synthetic checks")
    contract["_variant_bytes"] = variant
    return contract


def parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--render-contract", action="store_true")
    mode.add_argument("--verify-frozen-context", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", type=int, required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--input-sha256", required=True)
    parser.add_argument("--input-bytes", type=int, required=True)
    parser.add_argument("--setter-adapter-sha256", required=True)
    parser.add_argument("--receipt-sha256", required=True)
    parser.add_argument("--v15-source-sha256", required=True)
    parser.add_argument("--v15-protocol-sha256", required=True)
    parser.add_argument("--v15-contract-sha256", required=True)
    parser.add_argument("--setter-source-sha256", required=True)
    parser.add_argument("--setter-protocol-sha256", required=True)
    parser.add_argument("--setter-contract-sha256", required=True)
    parser.add_argument("--public-oracle-sha256", required=True)
    parser.add_argument("--variant-sha256")
    parser.add_argument("--variant-bytes", type=int)
    options = parser.parse_args()
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.flags.dont_write_bytecode == 1
            and os.path.abspath(sys.executable) == PYTHON
            and os.path.abspath(__file__) == absolute(SELF),
            "use isolated, bytecode-disabled, pinned CPython 3.14.6 only")
    require(options.input_sha256 == INPUT_SHA256 and options.input_bytes == INPUT_BYTES
            and options.setter_adapter_sha256 == SETTER_SAFE_SHA256
            and options.receipt_sha256 == RECEIPT_SHA256
            and options.v15_source_sha256 == V15_SOURCE_SHA256
            and options.v15_protocol_sha256 == V15_PROTOCOL_SHA256
            and options.v15_contract_sha256 == V15_CONTRACT_SHA256
            and options.setter_source_sha256 == SETTER_SOURCE_SHA256
            and options.setter_protocol_sha256 == SETTER_PROTOCOL_SHA256
            and options.setter_contract_sha256 == SETTER_CONTRACT_SHA256
            and options.public_oracle_sha256 == PUBLIC_ORACLE_SHA256,
            "reject incomplete or substituted independent caller authority")
    if not options.render_contract:
        require(options.contract_sha256 is not None
                and options.variant_sha256 is not None
                and options.variant_bytes is not None,
                "reject unpinned complete public Zig source contract")
    return options


def apply_variant(options: argparse.Namespace, candidate: bytes) -> dict[str, object]:
    require(options.apply, "reject source-only candidate publication")
    directory = os.path.dirname(absolute(TARGET))
    parent = os.path.dirname(directory)
    parent_metadata = os.lstat(parent)
    require(stat.S_ISDIR(parent_metadata.st_mode) and not stat.S_ISLNK(parent_metadata.st_mode),
            "reject unowned Zig variant parent")
    require(not os.path.lexists(directory) and not os.path.lexists(absolute(TARGET)),
            "reject existing Zig variant publication")
    os.mkdir(directory, 0o700)
    descriptor = os.open(absolute(TARGET), os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | getattr(os, "O_NOFOLLOW", 0)
                         | getattr(os, "O_CLOEXEC", 0), 0o600)
    try:
        position = 0
        while position < len(candidate):
            written = os.write(descriptor, candidate[position:])
            require(written > 0, "reject interrupted Zig variant publication")
            position += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    directory_descriptor = os.open(directory, os.O_RDONLY
                                   | getattr(os, "O_DIRECTORY", 0)
                                   | getattr(os, "O_CLOEXEC", 0))
    try:
        os.fsync(directory_descriptor)
    finally:
        os.close(directory_descriptor)
    observed = read_owner(TARGET, options.variant_sha256, options.variant_bytes)
    require(observed == candidate, "reject changed materialized Zig source")
    return {
        "schema": "rebar-owned-zig-public-adapter-semantics-v1-application",
        "status": "PASS; SOURCE MATERIALIZED ONLY",
        "candidate_family": "zig",
        "target": TARGET,
        "source_sha256": digest(observed),
        "source_bytes": len(observed),
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "original_case_execution_denominator": 31237,
        "prior_preserved_mismatch_count": 1700,
        "source_modeled_corrected_case_count": sum(CORRECTED_COHORTS.values()),
        "source_modeled_remaining_measured_failures": sum(PRESERVED_FAILURES.values()),
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def main() -> int:
    try:
        options = parse()
        contract = build(options, run_self_test=options.self_test)
        candidate = contract.pop("_variant_bytes")
        if options.apply:
            print(canonical(apply_variant(options, candidate)).decode(), end="")
        elif options.render_contract:
            print(canonical(contract).decode(), end="")
        else:
            print(canonical({
                "status": "PASS",
                "mode": "self-test" if options.self_test else "verify-frozen-context",
                "source_sha256": options.source_sha256,
                "contract_sha256": options.contract_sha256,
                "prospective_variant_sha256": digest(candidate),
                "prospective_variant_bytes": len(candidate),
                "synthetic_control_count": contract["source_only_self_test_control_count"],
                "source_only_effects": {name: 0 for name in ZERO_EFFECTS},
                "candidate_matching": "NOT RUN",
                "holdout": "NOT OPENED",
                "performance": "NOT MEASURED",
            }).decode(), end="")
        return 0
    except (FreezeError, OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print("first-party Zig public adapter rejected: "
              + type(error).__name__ + ": " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
