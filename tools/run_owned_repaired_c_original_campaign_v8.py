#!/usr/bin/env python3
"""Freeze lossless reporting for the actual, independently built C18 engine.

Historical source is authenticated and transformed in memory.  Source-only
operations never import a candidate, activate native code, open an archive or
private root, create a worker, inspect holdout cases, or collect timings.
"""

from __future__ import annotations

import ast
import hashlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/run_owned_repaired_c_original_campaign_v8.py"
PROTOCOL = "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V8.md"
CONTRACT = "oracle/phase2/repaired-c-original-campaign-v8.json"
SCHEMA = "rebar-owned-repaired-c-original-campaign-v8"
LABEL = "phase2-v18-c-subject-buffer-root-provenance-original-p0-v8"
DEVICE = 2064
MAX_OWNER = 8 * 1024 * 1024
MAX_VECTOR_PREFIX = 24
MAX_TRANSPORT_DEPTH = 60
TRANSPORT_KIND = "__rebar_c_v8_transport_kind__"
SURFACE_RELATIVE = "tools/python_re_public_surface_oracle_stage19.py"
SURFACE_MODULE = "tools.python_re_public_surface_oracle_stage19"
SURFACE_SHA256 = (
    "fda386f3c00be660a41e92d8005fc287706d9dc050967cf2b708cb6f8aba113e"
)
THREADED_RELATIVE = "tools/python_re_threaded_pattern_oracle_v1.py"
THREADED_MODULE = "tools.python_re_threaded_pattern_oracle_v1"
THREADED_SHA256 = (
    "05226e59736d8721a975eda8afa10247213999690c2766a7b3235c567b9f8276"
)
SURFACE_OWNER = (SURFACE_RELATIVE, SURFACE_SHA256, 199366, 430521)
THREADED_OWNER = (THREADED_RELATIVE, THREADED_SHA256, 146417, 432206)
SOURCE_ATTESTATIONS: dict[tuple[str, str], tuple] = {}
V7 = (
    (
        "tools/run_owned_repaired_c_original_campaign_v7.py",
        "42d27c321a54cbe2a730ce20967f786bc354340c35501e9d2a4cd37b4948884e",
        56985,
        431138,
    ),
    (
        "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V7.md",
        "99b3321a54cc36ad065f0d4178e34e0baf60349b4c85fb22794dbf26b33b9b0a",
        5485,
        525186,
    ),
    (
        "oracle/phase2/repaired-c-original-campaign-v7.json",
        "ce59aa6e7b900095dad4875d6e911dd9983fa6834c7d810f2e8c729c1c880811",
        18786,
        525195,
    ),
)
V7_RECEIPT = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v7-c-"
    "phase2-v18-c-subject-buffer-root-provenance-original-p0-v7-"
    "failures-publication-receipt.json",
    "bba4b8498a37db0bf9651c0bb040deaf96f9eef363ba6f2e2c923379d7fa5080",
    7375,
    525199,
)
EXPECTED_V7_ROWS = (
    ("original_bounded_v5", 151, "CANDIDATE EXECUTION FAILURE", "NOT MEASURED"),
    ("public_v3", 864, "CANDIDATE EXECUTION FAILURE", "NOT MEASURED"),
    ("scanner_v3", 1024, "CANDIDATE EXECUTION FAILURE", "NOT MEASURED"),
    ("buffer_v3", 768, "CANDIDATE EXECUTION FAILURE", "NOT MEASURED"),
    ("managed_v1", 1024, "SEMANTIC MISMATCH", 16),
    ("scanner_verbose_v1", 2854, "PASS", 0),
    ("public_types_v1", 6912, "SEMANTIC MISMATCH", 216),
    ("substitution_v2", 5120, "WORKER INFRASTRUCTURE FAILURE", "NOT MEASURED"),
    ("shape_v2", 10240, "PASS", 0),
    ("public_surface_v19", 1376, "CANDIDATE EXECUTION FAILURE", "NOT MEASURED"),
    ("subinterpreter_v2", 128, "CANDIDATE EXECUTION FAILURE", "NOT MEASURED"),
    ("pep688_v4", 264, "SEMANTIC MISMATCH", 4),
    ("threaded_pattern_v1", 512, "CANDIDATE EXECUTION FAILURE", "NOT MEASURED"),
)
REPLACEMENTS = {
    V7[0][0]: SOURCE,
    V7[1][0]: PROTOCOL,
    V7[2][0]: CONTRACT,
    "rebar-owned-repaired-c-original-campaign-v7": SCHEMA,
    "phase2-v18-c-subject-buffer-root-provenance-original-p0-v7": LABEL,
    "/tmp/rebar-phase2-repaired-c-original-campaign-v7":
        "/tmp/rebar-phase2-repaired-c-original-campaign-v8",
    ".rebar-c-original-campaign-v7-original-native":
        ".rebar-c-original-campaign-v8-original-native",
    ".rebar-c-original-campaign-v7-staged-native":
        ".rebar-c-original-campaign-v8-staged-native",
    "original-native-recovery-journal-v7.json":
        "original-native-recovery-journal-v8.json",
    "repaired-c-original-campaign-v7-c-":
        "repaired-c-original-campaign-v8-c-",
    "SOURCE FROZEN; ACTUAL C18 V7 ORIGINAL CAMPAIGN NOT RUN":
        "SOURCE FROZEN; ACTUAL C18 V8 ORIGINAL CAMPAIGN NOT RUN",
    "SOURCE FREEZE, PRESERVED ACTUAL V6 FAILURE AND V7 RUN AUTHORIZATION; "
    "NOT A V7 CANDIDATE RESULT":
        "SOURCE FREEZE, PRESERVED ACTUAL V6 AND V7 FAILURES; "
        "NOT A V8 CANDIDATE RESULT",
    "LATEST P0 V4 AND EXPLICIT C V7 ONLY":
        "LATEST P0 V4 AND EXPLICIT C V8 ONLY",
    "NOT RUN BY V7": "NOT RUN BY V8",
    "v7_candidate_correctness": "v8_candidate_correctness",
}


class CampaignError(Exception):
    """Reject an unauthenticated owner or lossy reporting transformation."""


def need(condition: object, message: str) -> None:
    if not condition:
        raise CampaignError(message)


def clean_runtime() -> None:
    need(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and os.path.realpath(sys.executable) == PYTHON
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode is True
        and "re" not in sys.modules
        and "_sre" not in sys.modules
        and "ctypes" not in sys.modules
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "require clean, pinned CPython 3.14.6 -I -B -S without a matcher",
    )


def read_historical(owner: tuple) -> bytes:
    relative, expected, length, inode = owner
    need(
        type(relative) is str
        and relative in {item[0] for item in V7}
        | {V7_RECEIPT[0], SURFACE_OWNER[0], THREADED_OWNER[0]}
        and type(expected) is str
        and len(expected) == 64
        and all(item in "0123456789abcdef" for item in expected)
        and type(length) is int
        and 0 < length <= MAX_OWNER
        and type(inode) is int
        and inode > 0,
        "reject an invented or unbounded historical source-only owner",
    )
    descriptor = os.open(
        ROOT + "/" + relative,
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        before = os.fstat(descriptor)
        need(
            stat.S_ISREG(before.st_mode)
            and before.st_dev == DEVICE
            and before.st_ino == inode
            and before.st_size == length
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600,
            "reject a substituted exact historical owner: " + relative,
        )
        pieces = []
        remaining = length
        while remaining:
            piece = os.read(descriptor, min(262144, remaining))
            need(bool(piece), "reject truncated historical source: " + relative)
            pieces.append(piece)
            remaining -= len(piece)
        need(not os.read(descriptor, 1), "reject expanded historical owner")
        after = os.fstat(descriptor)
        raw = b"".join(pieces)
        need(
            hashlib.sha256(raw).hexdigest() == expected
            and (
                before.st_dev,
                before.st_ino,
                before.st_size,
                before.st_mtime_ns,
                before.st_ctime_ns,
                before.st_nlink,
            )
            == (
                after.st_dev,
                after.st_ino,
                after.st_size,
                after.st_mtime_ns,
                after.st_ctime_ns,
                after.st_nlink,
            ),
            "reject a changed authentic historical owner: " + relative,
        )
        return raw
    finally:
        os.close(descriptor)


class HistoricalV8Transform(ast.NodeTransformer):
    """Change exact controller identity, not a frozen original test."""

    def __init__(self) -> None:
        self.replacements = {key: 0 for key in REPLACEMENTS}
        self.versions = 0
        self.predecessor_receipt_bindings = 0

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if type(node.value) is str and node.value in REPLACEMENTS:
            self.replacements[node.value] += 1
            return ast.copy_location(
                ast.Constant(REPLACEMENTS[node.value]), node
            )
        return node

    def visit_Dict(self, node: ast.Dict) -> ast.AST:
        node = self.generic_visit(node)
        for key, value in zip(node.keys, node.values, strict=True):
            if (
                isinstance(key, ast.Constant)
                and key.value == "version"
                and isinstance(value, ast.Constant)
                and type(value.value) is int
                and value.value == 7
            ):
                value.value = 8
                self.versions += 1
        keys = {
            item.value for item in node.keys
            if isinstance(item, ast.Constant) and type(item.value) is str
        }
        if "preserved_actual_v6_failure_receipt_sha256" in keys:
            need("preserved_actual_v7_failure_receipt_sha256" not in keys,
                 "reject an already replaced historical C V7 receipt field")
            node.keys.append(ast.Constant(
                "preserved_actual_v7_failure_receipt_sha256"
            ))
            node.values.append(ast.Constant(V7_RECEIPT[1]))
            self.predecessor_receipt_bindings += 1
        return node

    def visit_Assign(self, node: ast.Assign) -> ast.AST:
        node = self.generic_visit(node)
        if (
            len(node.targets) == 1
            and isinstance(node.targets[0], ast.Subscript)
            and isinstance(node.targets[0].slice, ast.Constant)
            and node.targets[0].slice.value == "version"
            and isinstance(node.value, ast.Constant)
            and type(node.value.value) is int
            and node.value.value == 7
        ):
            node.value.value = 8
            self.versions += 1
        return node


def bootstrap_historical() -> tuple[types.ModuleType, dict]:
    clean_runtime()
    raw = read_historical(V7[0])
    tree = ast.parse(raw.decode("utf-8", "strict"), filename=V7[0][0])
    transform = HistoricalV8Transform()
    corrected = ast.fix_missing_locations(transform.visit(tree))
    need(
        all(count > 0 for count in transform.replacements.values())
        and transform.versions == 3
        and transform.predecessor_receipt_bindings == 2,
        "reject an incomplete or expanded historical V7 identity transform",
    )
    module = types.ModuleType("_rebar_owned_c_v8_authenticated_v7")
    module.__file__ = ROOT + "/" + SOURCE
    module.__package__ = ""
    exec(compile(corrected, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    need(
        module.SOURCE == SOURCE
        and module.PROTOCOL == PROTOCOL
        and module.CONTRACT == CONTRACT
        and module.SCHEMA == SCHEMA
        and module.LABEL == LABEL
        and module.WORKER_TIMEOUT_SECONDS == 120
        and module.MAX_WORKER_STDOUT == 3 * 1024 * 1024
        and module.MAX_VECTOR_PREFIX == MAX_VECTOR_PREFIX
        and module.V6_RECEIPT[1]
        == "868fdd4df9ed960113c324c1dda82d12d2e700d5c32213a4d8c147384b64b081",
        "reject an incompletely preserved first-party C V7 controller",
    )
    clean_runtime()
    return module, {
        "authenticated_historical_source_sha256": V7[0][1],
        "exact_controller_identity_replacements": dict(transform.replacements),
        "exact_version_field_replacements": transform.versions,
        "exact_actual_v7_receipt_bindings":
            transform.predecessor_receipt_bindings,
        "frozen_original_test_source_modifications": 0,
        "frozen_json_reader_modifications": 0,
        "candidate_semantics_modifications": 0,
        "runtime_guard_modifications": 0,
    }


def has_surrogate(value: str) -> bool:
    return any(0xD800 <= ord(item) <= 0xDFFF for item in value)


def attest_source_callable(module: object, owner: tuple,
                           function_name: str) -> types.FunctionType:
    relative, expected, _, _ = owner
    module_name = relative.removesuffix(".py").replace("/", ".")
    function = getattr(module, function_name, None)
    need(
        type(module) is types.ModuleType
        and module.__name__ == module_name
        and sys.modules.get(module_name) is module
        and os.path.abspath(getattr(module, "__file__", ""))
        == ROOT + "/" + relative
        and getattr(module, "SOURCE_RELATIVE", None) == relative
        and isinstance(function, types.FunctionType)
        and function.__module__ == module_name
        and function.__globals__ is module.__dict__
        and os.path.abspath(function.__code__.co_filename)
        == ROOT + "/" + relative,
        "reject an unowned, fabricated, or crossed frozen source callable: "
        + module_name + "." + function_name,
    )
    key = (module_name, function_name)
    cached = SOURCE_ATTESTATIONS.get(key)
    if cached is not None:
        need(cached == (module, function, function.__code__, expected),
             "reject a changed already authenticated frozen source callable")
        return function
    raw = read_historical(owner)
    tree = ast.parse(raw.decode("utf-8", "strict"),
                     filename=ROOT + "/" + relative)
    functions = [
        item for item in tree.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        and item.name == function_name
    ]
    need(len(functions) == 1 and isinstance(functions[0], ast.FunctionDef),
         "require exactly one authentic top-level frozen source callable")
    futures = [
        item for item in tree.body
        if isinstance(item, ast.ImportFrom) and item.module == "__future__"
    ]
    isolated = ast.fix_missing_locations(
        ast.Module(body=futures + functions, type_ignores=[])
    )
    namespace = {"__name__": module_name}
    exec(compile(isolated, ROOT + "/" + relative, "exec",
                 dont_inherit=True), namespace)
    source_function = namespace.get(function_name)
    need(isinstance(source_function, types.FunctionType),
         "require an independently compiled immutable source definition")
    actual = function.__code__
    reference = source_function.__code__
    need(
        actual.co_code == reference.co_code
        and actual.co_consts == reference.co_consts
        and actual.co_names == reference.co_names
        and actual.co_varnames == reference.co_varnames
        and actual.co_argcount == reference.co_argcount
        and actual.co_posonlyargcount == reference.co_posonlyargcount
        and actual.co_kwonlyargcount == reference.co_kwonlyargcount
        and actual.co_flags == reference.co_flags
        and actual.co_firstlineno == reference.co_firstlineno,
        "reject a forged function whose filename imitates frozen source: "
        + module_name + "." + function_name,
    )
    SOURCE_ATTESTATIONS[key] = (module, function, actual, expected)
    return function


def authenticate_envelope(value: object, producer: types.ModuleType) -> dict:
    identity = type(value)
    need(
        identity.__name__ == "_NormalizedEnvelope"
        and isinstance(value, dict),
        "reject a forged or unrelated normalized-envelope identity",
    )
    module = sys.modules.get(SURFACE_MODULE)
    spec = producer.suite_spec("public_surface_v19")
    need(
        type(module) is types.ModuleType
        and module.__name__ == SURFACE_MODULE
        and identity.__module__ == SURFACE_MODULE
        and sys.modules.get(SURFACE_MODULE) is module
        and os.path.abspath(getattr(module, "__file__", ""))
        == ROOT + "/" + SURFACE_RELATIVE
        and spec.source_relative == SURFACE_RELATIVE
        and spec.source_sha256 == SURFACE_SHA256
        and getattr(module, "_NormalizedEnvelope", None) is identity,
        "reject an unauthenticated public-surface normalized-envelope class",
    )
    factory = attest_source_callable(
        module, SURFACE_OWNER, "_new_normalized_envelope"
    )
    need(factory is getattr(module, "_new_normalized_envelope", None),
         "reject a replaced authentic private normalized-envelope factory")
    registry = getattr(module, "_AUTHENTIC_NORMALIZED_ENVELOPES", None)
    need(
        registry is not None
        and callable(getattr(registry, "get", None))
        and registry.get(id(value)) is value,
        "reject a forged, crossed, or unfactored normalized-envelope instance",
    )
    return {
        "source_relative": SURFACE_RELATIVE,
        "source_sha256": SURFACE_SHA256,
        "factory_registry_identity_confirmed": True,
    }


def normalize_transport(value: object, producer: types.ModuleType,
                        depth: int = 0) -> object:
    need(depth <= MAX_TRANSPORT_DEPTH,
         "reject excessively nested authentic transport evidence")
    if value is None or type(value) in (bool, int):
        return value
    if type(value) is str:
        if not has_surrogate(value):
            return value
        encoded = value.encode("utf-16-be", "surrogatepass")
        return {
            TRANSPORT_KIND: "python-str-utf16-surrogatepass",
            "utf16be_hex": encoded.hex(),
            "code_unit_count": len(encoded) // 2,
        }
    if type(value) is float:
        return {TRANSPORT_KIND: "python-float", "hex": value.hex()}
    if type(value) is bytes:
        return {TRANSPORT_KIND: "python-bytes", "hex": value.hex()}
    if type(value) is bytearray:
        return {
            TRANSPORT_KIND: "python-bytearray",
            "hex": bytes(value).hex(),
        }
    if type(value) is tuple:
        return {
            TRANSPORT_KIND: "python-tuple",
            "items": [normalize_transport(item, producer, depth + 1)
                      for item in value],
        }
    if type(value) is list:
        return [normalize_transport(item, producer, depth + 1)
                for item in value]
    if type(value) is dict:
        if (
            all(type(key) is str and not has_surrogate(key)
                for key in value)
            and TRANSPORT_KIND not in value
        ):
            return {
                key: normalize_transport(item, producer, depth + 1)
                for key, item in value.items()
            }
        entries = [
            [normalize_transport(key, producer, depth + 1),
             normalize_transport(item, producer, depth + 1)]
            for key, item in value.items()
        ]
        entries.sort(key=lambda item: producer.canonical(item[0]))
        return {TRANSPORT_KIND: "python-mapping", "entries": entries}
    if isinstance(value, dict):
        evidence = authenticate_envelope(value, producer)
        fields = normalize_transport(dict(value), producer, depth + 1)
        return {
            TRANSPORT_KIND: "authenticated-normalized-envelope",
            "identity": evidence,
            "fields": fields,
        }
    raise CampaignError(
        "reject an unowned or non-lossless reporting value: "
        + type(value).__qualname__
    )


def restore_transport(value: object, producer: types.ModuleType,
                      depth: int = 0) -> object:
    need(depth <= MAX_TRANSPORT_DEPTH,
         "reject excessively nested transport recovery")
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is list:
        return [restore_transport(item, producer, depth + 1)
                for item in value]
    need(type(value) is dict,
         "reject an invented normalized reporting document")
    kind = value.get(TRANSPORT_KIND)
    if kind is None:
        return {
            key: restore_transport(item, producer, depth + 1)
            for key, item in value.items()
        }
    if kind == "python-str-utf16-surrogatepass":
        need(set(value) == {TRANSPORT_KIND, "utf16be_hex", "code_unit_count"},
             "reject forged lossless surrogate transport fields")
        raw = bytes.fromhex(value["utf16be_hex"])
        need(len(raw) % 2 == 0
             and len(raw) // 2 == value["code_unit_count"],
             "reject changed complete surrogate code units")
        return raw.decode("utf-16-be", "surrogatepass")
    if kind == "python-float":
        need(set(value) == {TRANSPORT_KIND, "hex"},
             "reject forged lossless floating evidence")
        return float.fromhex(value["hex"])
    if kind in ("python-bytes", "python-bytearray"):
        need(set(value) == {TRANSPORT_KIND, "hex"},
             "reject changed complete byte evidence")
        raw = bytes.fromhex(value["hex"])
        return raw if kind == "python-bytes" else bytearray(raw)
    if kind == "python-tuple":
        need(set(value) == {TRANSPORT_KIND, "items"}
             and type(value["items"]) is list,
             "reject fabricated original tuple reporting")
        return tuple(restore_transport(item, producer, depth + 1)
                     for item in value["items"])
    if kind == "python-mapping":
        need(set(value) == {TRANSPORT_KIND, "entries"}
             and type(value["entries"]) is list,
             "reject fabricated lossless mapping reporting")
        restored = {}
        for pair in value["entries"]:
            need(type(pair) is list and len(pair) == 2,
                 "reject an omitted or expanded original mapping entry")
            key = restore_transport(pair[0], producer, depth + 1)
            need(key not in restored,
                 "reject duplicated authentic original mapping keys")
            restored[key] = restore_transport(pair[1], producer, depth + 1)
        return restored
    if kind == "authenticated-normalized-envelope":
        need(set(value) == {TRANSPORT_KIND, "identity", "fields"}
             and value["identity"] == {
                 "source_relative": SURFACE_RELATIVE,
                 "source_sha256": SURFACE_SHA256,
                 "factory_registry_identity_confirmed": True,
             }, "reject substituted private normalized-envelope provenance")
        fields = restore_transport(value["fields"], producer, depth + 1)
        need(type(fields) is dict,
             "reject incomplete authentic normalized-envelope fields")
        return fields
    raise CampaignError("reject an invented reporting transport tag")


def original_source_module(suite_name: str, producer: types.ModuleType
                           ) -> types.ModuleType:
    suite = producer.suite_spec(suite_name)
    module_name = suite.source_relative.removesuffix(".py").replace("/", ".")
    if suite_name == "public_surface_v19":
        need(suite.source_relative == SURFACE_RELATIVE
             and suite.source_sha256 == SURFACE_SHA256
             and module_name == SURFACE_MODULE,
             "reject changed frozen public-surface source provenance")
    if suite_name == "threaded_pattern_v1":
        need(suite.source_relative == THREADED_RELATIVE
             and suite.source_sha256 == THREADED_SHA256
             and module_name == THREADED_MODULE,
             "reject changed frozen threaded-source provenance")
    selected = sys.modules.get(module_name)
    need(type(selected) is types.ModuleType
         and selected.__name__ == module_name
         and sys.modules.get(module_name) is selected
         and os.path.abspath(getattr(selected, "__file__", ""))
         == ROOT + "/" + suite.source_relative,
         "require the canonical, authenticated frozen suite digest provider: "
         + suite_name)
    owner = {
        "public_surface_v19": SURFACE_OWNER,
        "threaded_pattern_v1": THREADED_OWNER,
    }.get(suite_name)
    need(owner is not None,
         "reject an unapproved source-specific original digest provider")
    attest_source_callable(selected, owner, "digest")
    return selected


def lossless_vector(records: object, producer: types.ModuleType,
                    *, expected: str | None = None,
                    suite_name: str | None = None) -> dict:
    need(type(records) in (list, tuple),
         "require the genuine complete original observation vector")
    original_modes = {}
    original_error = None
    try:
        original_raw = producer.canonical(records)
        need(original_raw.endswith(b"\n"),
             "preserve the frozen original canonical newline")
        original_modes[hashlib.sha256(original_raw).hexdigest()] = (
            "producer-canonical-with-newline"
        )
        original_modes[hashlib.sha256(original_raw[:-1]).hexdigest()] = (
            "source-canonical-without-newline"
        )
    except producer.ProducerError as error:
        original_error = error
    if expected is not None:
        need(
            type(expected) is str
            and len(expected) == 64
            and all(item in "0123456789abcdef" for item in expected),
            "require the complete independently observed source vector digest",
        )
        if expected not in original_modes:
            need(type(suite_name) is str,
                 "reject a crossed or missing original source digest")
            source = original_source_module(suite_name, producer)
            observed = source.digest(records)
            need(type(observed) is str and observed == expected,
                 "reject a substituted source-specific complete observation")
            original_modes[observed] = "authenticated-frozen-suite-source"
        source_digest = expected
        source_mode = original_modes[expected]
    else:
        if original_modes:
            source_digest = next(iter(original_modes))
            source_mode = original_modes[source_digest]
        else:
            source_digest = "NOT PROVIDED BY THE ORIGINAL OBSERVER"
            source_mode = "LOSSLESS TRANSPORT ONLY"
    digest = hashlib.sha256()
    digest.update(b"[")
    prefix = []
    for index, record in enumerate(records):
        normalized = normalize_transport(record, producer)
        encoded = producer.canonical(normalized)
        need(encoded.endswith(b"\n"),
             "preserve every normalized original record's canonical newline")
        if index:
            digest.update(b",")
        digest.update(encoded[:-1])
        if len(prefix) < MAX_VECTOR_PREFIX:
            prefix.append(normalized)
    digest.update(b"]\n")
    transport_digest = digest.hexdigest()
    complete_digest = (
        source_digest
        if source_digest != "NOT PROVIDED BY THE ORIGINAL OBSERVER"
        else transport_digest
    )
    return {
        "total_count": len(records),
        "complete_vector_sha256": complete_digest,
        "source_complete_vector_sha256": source_digest,
        "source_complete_vector_digest_mode": source_mode,
        "transport_complete_vector_sha256": transport_digest,
        "transport_canonical_newline_preserved": True,
        "original_source_vector_verified_before_transport":
            expected is None or source_digest == expected,
        "original_source_canonical_rejection":
            str(original_error) if original_error is not None else None,
        "prefix": prefix,
        "prefix_count": len(prefix),
        "truncated": len(records) > len(prefix),
        "complete_vector_digest_preserved": True,
        "complete_vector_embedded": len(records) == len(prefix),
    }


def validate_previous_receipt(value: object, previous: types.ModuleType
                              ) -> dict:
    need(type(value) is dict,
         "require the genuine compact actual C V7 publication receipt")
    expected = {
        "schema": "rebar-owned-repaired-c-original-campaign-v7-"
                  "durable-publication-receipt",
        "status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE CORRECTNESS PUBLICATION ONLY",
        "version": 7,
        "family": "c",
        "label": "phase2-v18-c-subject-buffer-root-provenance-original-p0-v7",
        "candidate_status": "FAIL",
        "candidate_qualified": False,
        "source_sha256": V7[0][1],
        "protocol_sha256": V7[1][1],
        "contract_sha256": V7[2][1],
        "actual_c18_build_receipt_sha256": previous.BUILD_RECEIPT[1],
        "actual_c18_root_receipt_sha256": previous.ROOT_RECEIPT[1],
        "corrected_source_sha256": previous.CORRECTED_SOURCE[1],
        "unchanged_adapter_sha256": previous.ADAPTER[1],
        "native_engine_sha256": previous.NATIVE_SHA256,
        "native_bridge_sha256": previous.NATIVE_SHA256,
        "suite_count": 13,
        "attempted_suite_count": 13,
        "completed_suite_count": 5,
        "case_execution_denominator": 31237,
        "actual_candidate_workers": 13,
        "actual_worker_process_ids_are_distinct": True,
        "semantic_mismatch_count": "NOT MEASURED",
        "observed_semantic_mismatch_lower_bound": 236,
        "verified_passing_case_count": 13094,
        "infrastructure_failure_count": 1,
        "candidate_execution_failure_count": 7,
        "worker_timeout_count": 0,
        "worker_timeout_seconds": 120,
        "named_private_waiver_count": 13,
        "separate_reference_case_count": 8244,
        "separate_reference_cases_counted_as_candidate_cases": False,
        "original_source_targets_modified": 0,
        "original_native_inode_restored": True,
        "expanded_holdout_proposed_case_count": 14155776,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
        "preserved_actual_v6_failure_receipt_sha256":
            "868fdd4df9ed960113c324c1dda82d12d2e700d5c32213a4d8c147384b64b081",
    }
    need(all(value.get(key) == item for key, item in expected.items()),
         "reject a changed actual C V7 result or a fabricated candidate pass")
    identifiers = value.get("actual_worker_process_ids")
    need(type(identifiers) is list and len(identifiers) == 13
         and all(type(item) is int and item > 0 for item in identifiers)
         and len(set(identifiers)) == 13,
         "preserve all 13 genuine, distinct historical C worker processes")
    rows = value.get("suite_outcomes")
    need(type(rows) is list and len(rows) == 13,
         "preserve all 13 separately named genuine C V7 suite outcomes")
    for index, (row, expected_row) in enumerate(
            zip(rows, EXPECTED_V7_ROWS, strict=True)):
        name, count, failure, mismatches = expected_row
        need(type(row) is dict and row.get("suite") == name
             and row.get("case_execution_denominator") == count
             and row.get("failure_class") == failure
             and row.get("mismatch_count") == mismatches
             and row.get("actual_candidate_workers") == 1
             and row.get("worker_process_id") == identifiers[index],
             "reject a suppressed or altered actual C V7 suite: " + name)
    need(sum(item[1] for item in EXPECTED_V7_ROWS) == 31237
         and sum(item[3] for item in EXPECTED_V7_ROWS
                 if type(item[3]) is int) == 236,
         "preserve the full original denominator and actual mismatch lower bound")
    archive = value.get("archive")
    need(type(archive) is dict
         and archive.get("sha256")
         == "5975fb4549ee6d848b2fc94dc58217982efcaf8ffc839c75d0e98430aa1eaab7"
         and archive.get("bytes") == 26603
         and archive.get("mode") == "0600"
         and archive.get("nlink") == 1
         and archive.get("exclusive_creation") is True
         and archive.get("file_fsync_completed") is True
         and archive.get("directory_fsync_completed") is True,
         "authenticate actual C V7 archive only by its unopened public receipt")
    return value


def preserved_previous(previous: types.ModuleType, old: types.ModuleType
                       ) -> dict:
    producer = old.load_producer(old.read_owner(old.PRODUCER[0]))
    raw = old.read_owner(V7_RECEIPT)
    receipt = validate_previous_receipt(
        previous.parse_document(producer, raw, "small actual C V7 public receipt"),
        previous,
    )
    return {
        "source_freeze_owners": [previous.record(item) for item in V7],
        "actual_failure_receipt": previous.record(V7_RECEIPT),
        "publication_status": receipt["publication_status"],
        "publication_pass_means": receipt["publication_pass_means"],
        "candidate_status": receipt["candidate_status"],
        "candidate_qualified": receipt["candidate_qualified"],
        "attempted_suite_count": receipt["attempted_suite_count"],
        "completed_suite_count": receipt["completed_suite_count"],
        "actual_candidate_workers": receipt["actual_candidate_workers"],
        "actual_worker_process_ids": receipt["actual_worker_process_ids"],
        "actual_worker_process_ids_are_distinct":
            receipt["actual_worker_process_ids_are_distinct"],
        "case_execution_denominator": receipt["case_execution_denominator"],
        "verified_passing_case_count": receipt["verified_passing_case_count"],
        "semantic_mismatch_count": receipt["semantic_mismatch_count"],
        "observed_semantic_mismatch_lower_bound":
            receipt["observed_semantic_mismatch_lower_bound"],
        "infrastructure_failure_count": receipt["infrastructure_failure_count"],
        "candidate_execution_failure_count":
            receipt["candidate_execution_failure_count"],
        "worker_timeout_count": receipt["worker_timeout_count"],
        "original_native_inode_restored":
            receipt["original_native_inode_restored"],
        "suite_outcomes": receipt["suite_outcomes"],
        "historical_archive_opened": False,
        "separate_reference_cases_counted_as_candidate_cases": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def nested_failure_details(details: object) -> tuple[str, str, list]:
    chain = []
    current = details
    for _ in range(16):
        if type(current) is not dict:
            break
        error_type = current.get("error_type")
        error_message = current.get("error_message")
        active_case = current.get("active_case")
        if type(error_type) is str or type(error_message) is str:
            chain.append({
                "error_type": error_type if type(error_type) is str
                              else "NOT ESTABLISHED",
                "error_message": error_message
                                 if type(error_message) is str
                                 else "NOT ESTABLISHED",
                "active_case": active_case,
                "completed_candidate_cases":
                    current.get("completed_candidate_cases"),
            })
        next_item = None
        for key in ("complete_original_failure_details", "child_failure",
                    "nested_failure", "failure_details", "details"):
            value = current.get(key)
            if type(value) is dict and value is not current:
                next_item = value
                break
        if next_item is None:
            break
        current = next_item
    if chain:
        innermost = chain[-1]
        return (innermost["error_type"], innermost["error_message"], chain)
    return ("NOT ESTABLISHED", "NOT ESTABLISHED", chain)


def install_corrections(module: types.ModuleType, transform: dict) -> None:
    historical_configure = module.configure_previous
    historical_contract = module.contract_document
    historical_controls = module.source_controls

    def configure_previous(previous: types.ModuleType) -> tuple:
        old, original_contract = historical_configure(previous)
        additions = V7 + (V7_RECEIPT, SURFACE_OWNER, THREADED_OWNER)
        paths = {item[0] for item in old.STATIC_OWNERS}
        old.STATIC_OWNERS = tuple(old.STATIC_OWNERS) + tuple(
            item for item in additions if item[0] not in paths
        )
        old.OWNED_PATHS = frozenset(old.OWNED_PATHS) | {
            item[0] for item in additions
        }
        prior_authority = previous.actual_authority

        def full_authority() -> dict:
            authority = prior_authority()
            authority["previous_v7_failure_receipt_sha256"] = V7_RECEIPT[1]
            return authority

        previous.actual_authority = full_authority
        need(previous.RECOVERY_ROOT.endswith("-v8")
             and previous.BACKUP_NAME.endswith("v8-original-native")
             and previous.STAGE_NAME.endswith("v8-staged-native")
             and previous.JOURNAL_NAME == "original-native-recovery-journal-v8.json"
             and previous.BUILD_RECEIPT[1]
             == "4070feca7129fdcf3dc9762fae853649c68c722940af6157ecdcfa59d23e65ae"
             and previous.ROOT_RECEIPT[1]
             == "a231eec31b29ca796c75cee03b702a3e35a9195e74675c8f56209419dfeb03c8",
             "bind only the previously published genuine C18 build and fresh V8 recovery")
        return old, original_contract

    def contract_document(parsed: dict, old: types.ModuleType, state: dict,
                          previous: types.ModuleType,
                          original_contract: object) -> dict:
        result = historical_contract(parsed, old, state, previous,
                                     original_contract)
        result["version"] = 8
        result["preserved_actual_c_v7_campaign"] = preserved_previous(
            previous, old
        )
        result["authenticated_v7_controller_transform"] = transform
        result["authenticated_reporting_suite_sources"] = [
            previous.record(SURFACE_OWNER),
            previous.record(THREADED_OWNER),
        ]
        result["actual_operation_policy"].update({
            "immutable_actual_v7_failure_receipt_sha256": V7_RECEIPT[1],
            "immutable_actual_v7_observed_semantic_mismatch_lower_bound": 236,
            "strict_original_json_reader_remains_unchanged": True,
            "strict_original_json_reader_rejects_unpaired_surrogates": True,
            "lossless_surrogate_transport_only_after_original_comparison": True,
            "authentic_normalized_envelope_factory_identity_required": True,
            "forged_normalized_envelopes_rejected": True,
            "source_specific_complete_vector_digest_verified": True,
            "transport_complete_vector_digest_verified_separately": True,
            "canonical_newline_difference_preserved": True,
            "all_13_literal_nested_failure_diagnostics_preserved": True,
            "complete_nested_pep688_buffer_flags_preserved": True,
            "no_semantic_mismatches_suppressed": True,
            "native_build_identity": "ACTUAL PUBLISHED C18 ONLY",
            "future_c19_build_authorized": False,
        })
        result["v8_candidate_correctness"] = "NOT MEASURED"
        return result

    def canonical_vector(records: object, producer: types.ModuleType,
                         *, expected: str | None = None) -> dict:
        return lossless_vector(records, producer, expected=expected)

    def protected_worker(parsed: dict, producer: types.ModuleType,
                         state: dict, previous: types.ModuleType) -> dict:
        try:
            row = previous.actual_worker(parsed, producer, state)
            observed = row.get("original_observation")
            if type(observed) is dict:
                compact = dict(observed)
                records = compact.get("candidate_records")
                if type(records) in (list, tuple):
                    compact["candidate_records"] = lossless_vector(
                        records, producer,
                        expected=compact.get("candidate_records_sha256"),
                        suite_name=parsed.get("--suite"),
                    )
                    need(
                        compact["candidate_records"]["total_count"]
                        == compact.get("actual_candidate_case_count",
                                       compact["candidate_records"]["total_count"]),
                        "preserve every actual observed original candidate case",
                    )
                mismatches = compact.get("all_mismatches")
                if type(mismatches) in (list, tuple):
                    need(len(mismatches) == row.get("mismatch_count"),
                         "preserve every genuine original semantic mismatch")
                    compact["all_mismatches"] = lossless_vector(
                        mismatches, producer,
                        suite_name=parsed.get("--suite"),
                    )
                row["original_observation"] = normalize_transport(
                    compact, producer
                )
                row["all_original_records_and_mismatches_preserved"] = False
                row["all_original_record_and_mismatch_digests_preserved"] = True
                row["original_record_prefix_explicitly_truncated"] = bool(
                    type(records) in (list, tuple)
                    and len(records) > MAX_VECTOR_PREFIX
                )
            if row.get("status") == "FAIL":
                details = row.get("complete_genuine_failure_details")
                error_type, message, chain = nested_failure_details(details)
                if error_type == "NOT ESTABLISHED":
                    error_type = str(row.get("error_type", "CandidateError"))
                    message = str(row.get("error_message",
                                          "guarded original case failed"))
                row["complete_genuine_failure_details"] = normalize_transport(
                    details, producer
                )
                row["literal_original_failure_chain"] = normalize_transport(
                    chain, producer
                )
                row["plain_failure_diagnostic"] = (
                    error_type + ": " + message
                )[:module.MAX_SUMMARY_DIAGNOSTIC]
                row.setdefault("failure_phase", "OBSERVE COMPLETE ORIGINAL SUITE")
            row.setdefault(
                "observed_semantic_mismatch_lower_bound",
                row.get("mismatch_count", 0)
                if type(row.get("mismatch_count")) is int else 0,
            )
            encoded = producer.canonical(normalize_transport(row, producer))
            need(len(encoded) <= module.MAX_WORKER_STDOUT
                 and len(encoded) < producer.MAX_JSON_BYTES,
                 "bound the lossless full-suite V8 worker below the frozen JSON reader")
            decoded = producer.JsonReader(encoded).parse()
            need(type(decoded) is dict
                 and decoded.get("schema") == SCHEMA + "-actual-original-worker"
                 and decoded.get("suite") == parsed.get("--suite"),
                 "strictly round-trip the actual complete guarded V8 worker")
            return decoded
        except Exception as error:
            return module.early_worker_failure(
                parsed, error, "ENCODE COMPLETE GUARDED RESULT", previous
            )

    def source_controls(previous: types.ModuleType, wall: object,
                        old: types.ModuleType) -> list:
        answers = historical_controls(previous, wall, old)
        producer = old.load_producer(old.read_owner(old.PRODUCER[0]))
        authentic = "before\ud800after\udcff"
        rejected = False
        try:
            producer.JsonReader(producer.canonical({"actual": authentic})).parse()
        except producer.ProducerError:
            rejected = True
        need(rejected,
             "the unchanged frozen JSON reader must reject unpaired surrogates")
        encoded = normalize_transport({"actual": authentic}, producer)
        raw = producer.canonical(encoded)
        decoded = producer.JsonReader(raw).parse()
        need(restore_transport(decoded, producer) == {"actual": authentic},
             "preserve every exact unpaired Python code unit without relaxing JSON")
        sample = [{"case": index, "value": "complete synthetic source"}
                  for index in range(MAX_VECTOR_PREFIX + 5)]
        with_newline = hashlib.sha256(producer.canonical(sample)).hexdigest()
        without_newline = hashlib.sha256(
            producer.canonical(sample)[:-1]
        ).hexdigest()
        complete = lossless_vector(sample, producer, expected=with_newline)
        threaded = lossless_vector(sample, producer, expected=without_newline)
        need(with_newline != without_newline
             and complete["complete_vector_sha256"] == with_newline
             and threaded["complete_vector_sha256"] == without_newline
             and complete["transport_complete_vector_sha256"] == with_newline
             and threaded["transport_complete_vector_sha256"] == with_newline
             and threaded["source_complete_vector_digest_mode"]
             == "source-canonical-without-newline"
             and threaded["total_count"] == len(sample)
             and threaded["prefix_count"] == MAX_VECTOR_PREFIX
             and threaded["truncated"] is True,
             "authenticate both complete newline-sensitive source and transport digests")
        bad = False
        try:
            lossless_vector(sample, producer, expected="0" * 64)
        except CampaignError:
            bad = True
        need(bad, "reject a fabricated complete source-vector digest")
        module_name = "_rebar_owned_c_v8_source_only_envelope_control"
        need(module_name not in sys.modules,
             "reject a crossed synthetic authenticated-envelope module")
        synthetic = types.ModuleType(module_name)
        synthetic.__file__ = ROOT + "/" + SURFACE_RELATIVE
        synthetic.SOURCE_RELATIVE = SURFACE_RELATIVE
        envelope = type("_NormalizedEnvelope", (dict,), {
            "__module__": module_name,
        })
        synthetic._NormalizedEnvelope = envelope
        synthetic._AUTHENTIC_NORMALIZED_ENVELOPES = {}

        def factory(**fields: object) -> dict:
            result = envelope(fields)
            synthetic._AUTHENTIC_NORMALIZED_ENVELOPES[id(result)] = result
            return result

        synthetic._new_normalized_envelope = factory
        sys.modules[module_name] = synthetic
        try:
            actual = factory(kind="mapping", items=["actual", authentic])
            spoofed = False
            try:
                normalize_transport(actual, producer)
            except CampaignError:
                spoofed = True
            need(spoofed,
                 "reject an arbitrary-module normalized-envelope spoof")
            projected = {
                TRANSPORT_KIND: "authenticated-normalized-envelope",
                "identity": {
                    "source_relative": SURFACE_RELATIVE,
                    "source_sha256": SURFACE_SHA256,
                    "factory_registry_identity_confirmed": True,
                },
                "fields": normalize_transport(dict(actual), producer),
            }
            restored = restore_transport(
                producer.JsonReader(producer.canonical(projected)).parse(),
                producer,
            )
            need(type(restored) is dict and restored == dict(actual)
                 and projected[TRANSPORT_KIND]
                 == "authenticated-normalized-envelope",
                 "preserve exact source-authenticated normalized-envelope fields")
            forged = envelope(kind="forged")
            for invalid in (forged, type("ForgedEnvelope", (envelope,), {
                    "__module__": module_name,
                })(kind="crossed")):
                denied = False
                try:
                    normalize_transport(invalid, producer)
                except CampaignError:
                    denied = True
                need(denied,
                     "reject forged, crossed, or subclassed private envelopes")
        finally:
            need(sys.modules.get(module_name) is synthetic,
                 "reject a substituted synthetic source-only module")
            sys.modules.pop(module_name, None)
        need(SURFACE_MODULE not in sys.modules,
             "never import the real public surface in a source-only control")
        canonical_spoof = types.ModuleType(SURFACE_MODULE)
        canonical_spoof.__file__ = ROOT + "/" + SURFACE_RELATIVE
        canonical_spoof.SOURCE_RELATIVE = SURFACE_RELATIVE
        false_envelope = type("_NormalizedEnvelope", (dict,), {
            "__module__": SURFACE_MODULE,
        })
        canonical_spoof._NormalizedEnvelope = false_envelope
        canonical_spoof._AUTHENTIC_NORMALIZED_ENVELOPES = {}
        forged_factory_source = (
            "from __future__ import annotations\n"
            "def _new_normalized_envelope(**fields):\n"
            "    value = _NormalizedEnvelope(fields)\n"
            "    _AUTHENTIC_NORMALIZED_ENVELOPES[id(value)] = value\n"
            "    return value\n"
        )
        exec(compile(forged_factory_source,
                     ROOT + "/" + SURFACE_RELATIVE,
                     "exec", dont_inherit=True),
             canonical_spoof.__dict__)
        sys.modules[SURFACE_MODULE] = canonical_spoof
        try:
            false_value = canonical_spoof._new_normalized_envelope(
                kind="forged canonical module"
            )
            denied = False
            try:
                normalize_transport(false_value, producer)
            except CampaignError:
                denied = True
            need(denied,
                 "reject forged exact-name, exact-filename source factories")
        finally:
            need(sys.modules.get(SURFACE_MODULE) is canonical_spoof,
                 "reject a substituted forged-source hostile control")
            sys.modules.pop(SURFACE_MODULE, None)
        need(THREADED_MODULE not in sys.modules,
             "never import the real threaded suite in a source-only control")
        fake_digest_module = types.ModuleType(THREADED_MODULE)
        fake_digest_module.__file__ = ROOT + "/" + THREADED_RELATIVE
        fake_digest_module.SOURCE_RELATIVE = THREADED_RELATIVE
        exec(compile(
            "from __future__ import annotations\n"
            "def digest(value):\n"
            "    return '0' * 64\n",
            ROOT + "/" + THREADED_RELATIVE,
            "exec", dont_inherit=True,
        ), fake_digest_module.__dict__)
        sys.modules[THREADED_MODULE] = fake_digest_module
        try:
            rejected_digest = False
            try:
                original_source_module("threaded_pattern_v1", producer)
            except CampaignError:
                rejected_digest = True
            need(rejected_digest,
                 "reject an exact-name, exact-filename forged source digest")
        finally:
            need(sys.modules.get(THREADED_MODULE) is fake_digest_module,
                 "reject a substituted forged threaded-source control")
            sys.modules.pop(THREADED_MODULE, None)
        lineage = HistoricalV8Transform()
        lineage.visit(ast.parse(
            "proof = {'preserved_actual_v6_failure_receipt_sha256': 'x'}\n"
        ))
        need(lineage.predecessor_receipt_bindings == 1,
             "bind exactly an authentic historical predecessor receipt field")
        missing_lineage = HistoricalV8Transform()
        missing_lineage.visit(ast.parse("proof = {'unrelated': 'x'}\n"))
        need(missing_lineage.predecessor_receipt_bindings == 0,
             "never insert predecessor evidence into unrelated documents")
        duplicate_lineage = False
        try:
            HistoricalV8Transform().visit(ast.parse(
                "proof = {"
                "'preserved_actual_v6_failure_receipt_sha256': 'x',"
                "'preserved_actual_v7_failure_receipt_sha256': 'y'}\n"
            ))
        except CampaignError:
            duplicate_lineage = True
        need(duplicate_lineage,
             "reject a preexisting or duplicate predecessor-receipt binding")
        collision = {
            TRANSPORT_KIND: "ordinary user data",
            "original": authentic,
        }
        need(restore_transport(normalize_transport(collision, producer),
                               producer) == collision,
             "preserve genuine original mappings containing transport-tag keys")
        nested_flags = {
            "buffer": {
                "flags": [0, 1, 4, 8],
                "nested": {"readonly": True, "contiguous": False},
            },
            "surrogate": authentic,
        }
        need(restore_transport(normalize_transport(nested_flags, producer),
                               producer) == nested_flags,
             "preserve every exact nested original PEP 688 buffer flag")
        inner_type, inner_message, genuine_chain = nested_failure_details({
            "error_type": "ActualSuiteFailure",
            "error_message": "authentic outer original failure",
            "active_case": "original.outer",
            "completed_candidate_cases": 7,
            "complete_original_failure_details": {
                "error_type": "BufferError",
                "error_message": "exact original nested buffer failure",
                "active_case": "pep688.nested.readonly",
                "completed_candidate_cases": 4,
            },
        })
        need(inner_type == "BufferError"
             and inner_message == "exact original nested buffer failure"
             and len(genuine_chain) == 2
             and genuine_chain[-1]["active_case"]
             == "pep688.nested.readonly"
             and genuine_chain[-1]["completed_candidate_cases"] == 4,
             "preserve the exact genuine nested original failure and active case")
        previous_result = preserved_previous(previous, old)
        need(previous_result["candidate_status"] == "FAIL"
             and previous_result["observed_semantic_mismatch_lower_bound"] == 236
             and len(previous_result["suite_outcomes"]) == 13,
             "preserve actual C V7 failure and every original suite")
        answers.extend((
            "strict frozen JSON reader rejects the real unpaired surrogate",
            "lossless transport restores every original UTF-16 code unit",
            "source-specific and transport complete-vector hashes remain distinct",
            "fabricated complete original vector hashes are rejected",
            "source- and factory-authenticated envelope fields round-trip exactly",
            "arbitrary-module normalized-envelope spoofs are rejected",
            "forged canonical-name and filename source factories are rejected",
            "forged canonical-name threaded digest providers are rejected",
            "forged private-envelope instances and subclasses are rejected",
            "exact historical receipt lineage rejects missing and duplicate targets",
            "genuine transport-key collision mappings round-trip exactly",
            "all original nested PEP 688 buffer flags are preserved",
            "literal nested original failures retain their genuine active cases",
            "all 13 historical C V7 failures and 236 mismatches are preserved",
        ))
        return answers

    module.configure_previous = configure_previous
    module.contract_document = contract_document
    module.canonical_vector = canonical_vector
    module.protected_worker = protected_worker
    module.source_controls = source_controls


def main(arguments: list[str]) -> int:
    module, transform = bootstrap_historical()
    install_corrections(module, transform)
    return module.main(arguments)


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as error:
        os.write(2, (
            "C18 original campaign V8: "
            + type(error).__qualname__ + ": " + str(error) + "\n"
        ).encode("utf-8", "backslashreplace"))
        raise SystemExit(2)
