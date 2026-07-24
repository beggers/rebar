#!/usr/bin/env python3
"""Audit real native ownership without mistaking a public name for an engine."""

from __future__ import annotations

import argparse
import ast
import base64
import collections
import copy
import gc
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import pickle
import stat
import subprocess
import sys
from typing import Any, Callable, Mapping


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_from_scratch_audit_v5 as source_v5
from tools import postfinal_from_scratch_audit_v6 as source_v6
from tools import postfinal_from_scratch_audit_v7 as historical_v7


core = source_v6.core
SCHEMA = "rebar-postfinal-from-scratch-audit-v8"
SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v8.py"
SOURCE_PATH = ROOT / SOURCE_RELATIVE
REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V8.json"
REPORT_PATH = ROOT / REPORT_RELATIVE
PROTOCOL_RELATIVE = "candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V8.md"
PROTOCOL_SHA256 = (
    "5c60e6ce63ff1e4c5593eaafe29971cb3557b1a0389dcd5cf41cfb00647bc399"
)
CORE_FAMILIES = ("rust", "vm", "zig")
OWNED_NATIVE_MODULES = dict(source_v6.OWNED_NATIVE_MODULES)
OWNED_SOURCE_PATHS = dict(source_v6.OWNED_SOURCE_PATHS)
OWNED_NATIVE_PATHS = dict(source_v6.OWNED_NATIVE_PATHS)
NATIVE_LOADER_ALIASES = tuple(source_v6.NATIVE_LOADER_ALIASES)
MAX_SOURCE_BYTES = source_v6.MAX_SOURCE_BYTES
MAX_REPORT_BYTES = source_v6.MAX_REPORT_BYTES
MAX_WORKER_BYTES = source_v6.MAX_WORKER_BYTES
PICKLE_PROTOCOLS = (0, 2, 4, pickle.HIGHEST_PROTOCOL)
PINNED_EXECUTABLE = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
EDGE_SCHEMA = "rebar-v7-independent-edge-oracle-v1"
EDGE_SEED = 2026072329
EDGE_CHECKS = 223198
EDGE_CATEGORIES = 49
EDGE_REFERENCE_SHA256 = (
    "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526"
)
V7_EDGE_FAILURES = {
    "rust": (
        "candidates/evidence/"
        "rust-v7-edge-oracle-rust-postfinal-locale-v7-first-failure.json.gz",
        "3ffdb21d10f40deabd70fa1f408fa38ff2b027a2d269c4b75e607a05cefde3b8",
    ),
    "vm": (
        "candidates/evidence/"
        "rust-v7-edge-oracle-vm-postfinal-locale-v7-first-failure.json.gz",
        "2cce7c26d2487c8e400d2fd6b8cfbc81d4b734b08f7a8f356def910a9cbb385c",
    ),
    "zig": (
        "candidates/evidence/"
        "rust-v7-edge-oracle-zig-postfinal-locale-v7-first-failure.json.gz",
        "5fa7283942994139d531593cc1bdf25f5da48f6de424d7604ce2ce569100788a",
    ),
}
V7_EDGE_EXPECTATIONS = {
    "rust": {
        "failed": 16,
        "actual_sha256":
            "118c8606cd0d9826f79e7473495a36bd0b79c95c2b8ada351cdbad0b41bd4050",
        "failure_categories": {
            "public-object-and-buffer-contract": 4,
            "independent-object-contract/inspectable-public-signatures": 2,
            "independent-object-contract/match-copy-pickle-gc-and-readonly": 10,
        },
    },
    "vm": {
        "failed": 33,
        "actual_sha256":
            "a63c5ab97abc466c8eedcd9e6a89c8613c347e4b2166ef035c265d2369d08f27",
        "failure_categories": {
            "public-object-and-buffer-contract": 6,
            "independent-object-contract/compiled-pattern-contract": 15,
            "independent-object-contract/inspectable-public-signatures": 2,
            "independent-object-contract/match-copy-pickle-gc-and-readonly": 10,
        },
    },
    "zig": {
        "failed": 16,
        "actual_sha256":
            "eaccf982977fba97e2d01d3e43a42d4f43abeed5d8b342fab2f29a6a4e69a306",
        "failure_categories": {
            "public-object-and-buffer-contract": 4,
            "independent-object-contract/inspectable-public-signatures": 2,
            "independent-object-contract/match-copy-pickle-gc-and-readonly": 10,
        },
    },
}
FROZEN_HISTORY = {
    "GOAL.md":
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    PROTOCOL_RELATIVE: PROTOCOL_SHA256,
    "tools/postfinal_from_scratch_audit_v3.py":
        "d8230d1f0272bffc6ef2fb61136935047a4d4008afd8a66291c87c48b7a36767",
    "tools/postfinal_from_scratch_audit_v5.py":
        "100520ae06c3a837b3fa4ca508099ceb6e11efda8f63bcc0234b544071d17843",
    "tools/postfinal_from_scratch_audit_v6.py":
        "77e7ea97f96280019b3be9abfeeb8fc6ff27ca6ecd13189e611586af5719c18f",
    "tools/postfinal_from_scratch_audit_v7.py":
        "defa306e47a0d325af7d4c7fabb54324f6cb6d4653a494c46846838f5e2cf487",
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json":
        "efae1f94fb06a1eabbab352794410c4d8e20a78202dcbf769b08ff9c7cee130a",
    "tools/postfinal_no_delegation_audit_v7.py":
        "9283457064f32658747b449c4ee6ebd20ca7cc7dc442ce03ece6b02896cff4e4",
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json":
        "1f71caac01bffdffbf7ffdc2e21a9aa8d6936c452051cbdaa4c90ac67010fd34",
    "tools/python_re_universal_public_oracle_stage07.py":
        "150abcfc597658f48d64c04053889bd4b299c75ad7413bc1cafa5f864e9e7c25",
    "tools/rust_v7_edge_oracle.py":
        "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca",
    "tools/postfinal_current_build_proofs_v7.py":
        "9e25e5cbab24220b27ac279e17a5b02f48a5583f2dd27b93eb7d811ae6b827ff",
    "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V7.md":
        "781cf1e4c85a1de6d5d7d30ea8f451f0fd3417e0a81747ab8e1aa204b6478912",
    "candidates/evidence/"
    "rust-v8-rust-postfinal-locale-v7-sealed-campaign-first-failure.json":
        "62aba93fa8bdd6df7be93199aea6f58be7b24c095750c520179e96b98084b75a",
}


class AuditV8Error(source_v6.AuditV6Error):
    """A genuine native source, owner, public behavior, or history failed."""


class NativeWorkerFailure(AuditV8Error):
    """Preserve the complete bounded observations of a real failed native worker."""

    def __init__(self, message: str, evidence: Mapping[str, Any]):
        super().__init__(message)
        self.evidence = dict(evidence)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditV8Error(message)


def destination_name(value: Any) -> str:
    require(type(value) is str, "an exclusive V8 audit destination must be text")
    parsed = PurePosixPath(value)
    require(
        not parsed.is_absolute() and ".." not in parsed.parts
        and "\\" not in value and "\x00" not in value
        and str(parsed) == value and value == REPORT_RELATIVE,
        "only the exact append-only V8 source-audit report is authorized",
    )
    return value


def verify_fresh_report_target(target: Path = REPORT_PATH) -> Path:
    require(isinstance(target, Path),
            "the exclusively created V8 source report requires an exact path")
    absolute = target if target.is_absolute() else ROOT / target
    require(absolute.resolve() == absolute,
            "the V8 source report is not its exact canonical path")
    require(absolute.is_relative_to(ROOT),
            "the V8 source report escaped the approved workspace")
    destination_name(absolute.relative_to(ROOT).as_posix())
    require(absolute.parent == REPORT_PATH.parent
            and absolute.parent.is_dir() and not absolute.parent.is_symlink(),
            "the V8 source report parent is unsafe")
    require(not absolute.exists() and not absolute.is_symlink(),
            "refusing to rerun native workers or overwrite an existing V8 source report")
    return absolute


def read_frozen(relative: str, expected: str) -> tuple[bytes, str]:
    require(relative in FROZEN_HISTORY or any(
        relative == item[0] for item in V7_EDGE_FAILURES.values()
    ), "an unapproved historical, holdout, or performance file was requested")
    require(core.valid_sha256(expected), "a historical input has no authentic digest")
    path = ROOT / relative
    require(not path.is_symlink(), "a frozen historical input is a symlink")
    maximum = MAX_REPORT_BYTES if relative.endswith((".json", ".gz")) else MAX_SOURCE_BYTES
    observed, payload = core.bounded_file(
        path, maximum=maximum, label="exact preserved V8 historical input: " + relative,
        keep=True,
    )
    require(observed == expected and isinstance(payload, bytes),
            "an immutable historical V7 result changed: " + relative)
    return payload, observed


def validate_historical_edge(
    document: Any, family: str, archive_sha256: str
) -> dict[str, Any]:
    require(family in CORE_FAMILIES and isinstance(document, dict),
            "a historical edge failure is not an owned family JSON object")
    require(set(V7_EDGE_FAILURES) == set(CORE_FAMILIES)
            and set(V7_EDGE_EXPECTATIONS) == set(CORE_FAMILIES),
            "a genuine Rust, C, or Zig historical failure was omitted")
    require(archive_sha256 == V7_EDGE_FAILURES[family][1],
            "the genuine complete historical edge failure digest was substituted")
    exact = {
        "schema": EDGE_SCHEMA,
        "module": "candidates." + family + "_candidate",
        "script_sha256": FROZEN_HISTORY["tools/rust_v7_edge_oracle.py"],
        "seed": EDGE_SEED, "seeded_cases": 8, "unicode_stride": 4099,
        "correctness_checks": EDGE_CHECKS,
        "expected_sha256": EDGE_REFERENCE_SHA256,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    for key, value in exact.items():
        require(document.get(key) == value,
                "the complete historical edge failure changed: " + key)
    categories = document.get("categories")
    failures = document.get("failures")
    count = document.get("failed")
    require(isinstance(categories, dict) and len(categories) == EDGE_CATEGORIES
            and all(type(value) is int and value > 0 for value in categories.values())
            and sum(categories.values()) == EDGE_CHECKS,
            "a historical edge failure lost its complete 223,198/49 denominator")
    require(type(count) is int and count > 0
            and isinstance(failures, list) and len(failures) == count
            and all(isinstance(item, dict) for item in failures),
            "a real historical edge failure was hidden or classified as a pass")
    require(core.valid_sha256(document.get("actual_sha256"))
            and document["actual_sha256"] != EDGE_REFERENCE_SHA256
            and document["actual_sha256"]
            == V7_EDGE_EXPECTATIONS[family]["actual_sha256"],
            "a historical failing candidate observation digest was substituted")
    require(count == V7_EDGE_EXPECTATIONS[family]["failed"]
            and dict(collections.Counter(item.get("category") for item in failures))
            == V7_EDGE_EXPECTATIONS[family]["failure_categories"],
            "the actual complete frozen edge failure families or counts changed")
    artifacts = document.get("candidate_artifacts")
    require(isinstance(artifacts, list) and len(artifacts) >= 2,
            "a historical edge failure lost its actual native provenance")
    by_role = {
        item.get("role"): item for item in artifacts
        if isinstance(item, dict) and core.valid_sha256(item.get("sha256"))
    }
    require(by_role.get("public-python", {}).get("path")
            == "candidates/" + family + "_candidate.py",
            "a historical native edge failure belongs to a foreign public family")
    expected_native_paths = set(OWNED_NATIVE_PATHS[family].values())
    observed_native_paths = {
        item["path"] for item in by_role.values()
        if item.get("role") in {"native-bridge", "native-engine"}
    }
    require(observed_native_paths == expected_native_paths,
            "a historical failed edge concealed an actual native bridge or engine")
    if family == "rust":
        require(count == 16, "the preserved actual sixteen Rust failures changed")
        require(all(
            item.get("category") in {
                "public-object-and-buffer-contract",
                "independent-object-contract/inspectable-public-signatures",
                "independent-object-contract/match-copy-pickle-gc-and-readonly",
            }
            for item in failures
        ), "the complete real Rust public-owner failures were substituted")
    if family == "zig":
        require(count == 16, "the preserved actual sixteen Zig failures changed")
        require(all(
            item.get("category") in {
                "public-object-and-buffer-contract",
                "independent-object-contract/inspectable-public-signatures",
                "independent-object-contract/match-copy-pickle-gc-and-readonly",
            }
            for item in failures
        ), "the complete real Zig public-owner failures were substituted")
    if family == "vm":
        require(count == 33, "the preserved actual thirty-three C failures changed")
        require(sum(
            "readonly-groupindex" in str(item.get("label", ""))
            for item in failures
        ) == 17,
            "the seventeen genuine C re.Pattern descriptor failures were concealed")
    return {
        "status": "FAIL", "qualifies_current_engine": False,
        "archive_sha256": archive_sha256,
        "family": family, "candidate_module": exact["module"],
        "seed": EDGE_SEED, "checks": EDGE_CHECKS,
        "category_count": EDGE_CATEGORIES, "failed": count,
        "expected_sha256": EDGE_REFERENCE_SHA256,
        "actual_sha256": document["actual_sha256"],
        "failure_rows_preserved": count,
    }


def verify_history() -> dict[str, Any]:
    require(set(V7_EDGE_FAILURES) == set(CORE_FAMILIES),
            "a real Rust, C, or Zig frozen edge failure was omitted")
    documents: dict[str, dict[str, Any]] = {}
    preserved: dict[str, str] = {}
    for relative, expected in FROZEN_HISTORY.items():
        raw, actual = read_frozen(relative, expected)
        preserved[relative] = actual
        if relative.endswith(".json"):
            documents[relative] = core.decode_report(raw, label=relative)
    old_base = documents["candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json"]
    old_strict = documents["candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json"]
    require(old_base.get("schema") == historical_v7.SCHEMA
            and old_base.get("status") == "PASS"
            and old_base.get("audit_source_sha256")
            == FROZEN_HISTORY["tools/postfinal_from_scratch_audit_v7.py"],
            "the real historical V7 source audit was concealed or changed")
    require(old_strict.get("schema") == "rebar-postfinal-no-delegation-audit-v7"
            and old_strict.get("status") == "PASS"
            and old_strict.get("audit_source_sha256")
            == FROZEN_HISTORY["tools/postfinal_no_delegation_audit_v7.py"]
            and old_strict.get("base_audit_report_sha256")
            == FROZEN_HISTORY["candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json"],
            "the real historical V7 strict audit was concealed or changed")
    first = documents[
        "candidates/evidence/"
        "rust-v8-rust-postfinal-locale-v7-sealed-campaign-first-failure.json"
    ]
    require(first.get("status") == "FAIL"
            and first.get("completed_campaign_stages") == 0
            and first.get("candidate_matching_workers_started") == 0
            and first.get("exception_message")
            == "the RUST public-python is stale or unproven",
            "the actual first stale-build campaign failure was hidden")
    edge_failures: dict[str, Any] = {}
    for family, (relative, expected) in V7_EDGE_FAILURES.items():
        compressed, observed = read_frozen(relative, expected)
        require(len(compressed) >= 10 and compressed[:2] == b"\x1f\x8b"
                and compressed[3] == 0
                and compressed[4:8] == b"\x00\x00\x00\x00",
                "an actual historical edge failure lost deterministic gzip metadata")
        try:
            payload = gzip.decompress(compressed)
            require(len(payload) <= MAX_REPORT_BYTES,
                    "a historical edge failure exceeds its bounded decompressed size")
            document = core.decode_report(payload, label=relative)
        except (OSError, EOFError, ValueError, UnicodeError) as error:
            raise AuditV8Error("the preserved actual edge failure is malformed") from error
        edge_failures[family] = validate_historical_edge(document, family, observed)
        preserved[relative] = observed
    return {
        "historical_input_sha256": preserved,
        "v7_source_report_historical": True,
        "v7_strict_report_historical": True,
        "first_campaign_failure_preserved": True,
        "real_edge_failures": edge_failures,
    }


NATIVE_OWNER_WORKER = r'''
import _ctypes
import builtins
import ctypes
import enum
import importlib
import importlib.abc
import inspect
import json
import pickle
import sys
import types
import weakref
from pathlib import Path

if len(sys.argv) != 4:
    raise RuntimeError("the V8 native-owner worker requires one exact family")
root = Path(sys.argv[1]).resolve(strict=True)
role = sys.argv[2]
expected = json.loads(sys.argv[3])
bridges = {
    "rust": "candidates._rust_bridge",
    "vm": "candidates._vm_native",
    "zig": "candidates._zig_bridge",
}
if role not in bridges or not isinstance(expected, dict) or not expected:
    raise RuntimeError("the V8 worker received a foreign engine or omitted native ELF")
sys.path.insert(0, str(root))
from tools import python_re_universal_public_oracle_stage07 as stage07
if stage07.ROOT.resolve(strict=True) != root:
    raise RuntimeError("the V8 owner worker escaped its immutable source root")
guard = stage07._install_family_guard(role, expected)
aliases = (
    "ctypes.CDLL", "ctypes.cdll.LoadLibrary", "ctypes.cdll._dlltype",
    "ctypes._dlopen", "_ctypes.dlopen",
)
if guard.get("native_loader_aliases_blocked") != list(aliases):
    raise RuntimeError("the V8 native worker weakened a forbidden dynamic loader")
for key in (
    "enabled", "stdlib_re_blocked", "cpython_sre_blocked",
    "third_party_regex_blocked", "cross_family_blocked",
    "foreign_dynamic_libraries_blocked",
):
    if guard.get(key) is not True:
        raise RuntimeError("the V8 native worker weakened isolation: " + key)

foreign = {
    "regex", "_regex", "re2", "pyre2", "pcre", "pcre2",
    "hyperscan", "rure", "oniguruma", "onig",
    "candidates.ast_candidate",
}
foreign.update("candidates." + other + "_candidate"
               for other in bridges if other != role)
foreign.update(bridge for other, bridge in bridges.items() if other != role)

class NativeFamilyFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in foreign or any(fullname.startswith(item + ".")
                                     for item in foreign):
            raise ImportError("V8 blocked a cross-family or external engine: " + fullname)
        return None

finder = NativeFamilyFinder()
sys.meta_path.insert(0, finder)

def audit_foreign_engines():
    observations = []
    for forbidden in sorted(foreign):
        try:
            importlib.import_module(forbidden)
        except ImportError:
            observations.append({"module": forbidden, "blocked": True})
            continue
        raise RuntimeError("the V8 native guard admitted an external engine: " + forbidden)
    return observations

foreign_guards_before = audit_foreign_engines()

regex_entries = (
    ("re", "compile"), ("re", "search"), ("re", "match"),
    ("re", "fullmatch"), ("re", "findall"), ("re", "finditer"),
    ("re", "split"), ("re", "sub"), ("re", "subn"),
    ("re", "_compile"), ("_sre", "compile"),
    ("re._compiler", "compile"), ("re._parser", "parse"),
)

def audit_python_matchers():
    observations = []
    for name, attribute in regex_entries:
        try:
            target = importlib.import_module(name)
            getattr(target, attribute)
        except (ImportError, AttributeError):
            observations.append({"module": name, "name": attribute, "blocked": True})
        else:
            raise RuntimeError("a V8 public owner can reach a Python matcher: " + name)
    if len(observations) != 13:
        raise RuntimeError("the V8 native worker dropped a Python matching poison")
    return observations


def current_native_loader_aliases():
    return (
        ctypes.CDLL,
        ctypes.cdll.LoadLibrary,
        ctypes.cdll._dlltype,
        ctypes._dlopen,
        _ctypes.dlopen,
    )


def callable_identity(value):
    return (
        id(getattr(value, "__func__", value)),
        id(getattr(value, "__self__", None)),
    )


def audit_native_loaders():
    blocked = []
    foreign_library = str(root / "candidates" / "_rust_engine.so")
    for label, loader in zip(aliases, current_native_loader_aliases(), strict=True):
        try:
            loader(foreign_library)
        except ImportError:
            blocked.append({"alias": label, "blocked": True})
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            raise RuntimeError("a V8 native loader was not explicitly blocked: " + label) from error
        else:
            raise RuntimeError("a V8 native worker loaded a forbidden library: " + label)
    return blocked


protected_import = builtins.__import__
protected_modules = {
    name: sys.modules.get(name)
    for name in ("re", "_sre", "regex", "re2", "pcre", "pcre2")
}
protected_loader_identities = tuple(
    callable_identity(item) for item in current_native_loader_aliases()
)
regex_guards = audit_python_matchers()
loader_guards = audit_native_loaders()

candidate_name = "candidates." + role + "_candidate"
bridge_name = bridges[role]
module = importlib.import_module(candidate_name)
bridge = importlib.import_module(bridge_name)
if module.Match is not bridge.Match or not isinstance(module.Match, type):
    raise RuntimeError("the V8 public Match is not the genuine owned native class")
if (module.Match.__module__ != "re" or module.Match.__name__ != "Match"
        or module.Match.__qualname__ != "Match"):
    raise RuntimeError("the owned native Match lacks the exact CPython public identity")
if (not isinstance(module.Pattern, type)
        or module.Pattern.__module__ != "re"
        or module.Pattern.__name__ != "Pattern"
        or module.Pattern.__qualname__ != "Pattern"):
    raise RuntimeError("the owned native Pattern lacks the exact CPython public identity")

before = stage07._verify_family_native_mappings(
    role, {"native_sha256_by_family": {role: expected}}
)
if before != expected:
    raise RuntimeError("the V8 native worker mapped an unaudited matching engine")

owners = {
    "Pattern": {
        "name": "Pattern", "qualified_name": module.Pattern.__qualname__,
        "public_module": module.Pattern.__module__,
        "native_owner_module": candidate_name,
        "native_bridge_identity": getattr(bridge, "Pattern", None) is module.Pattern,
        "public_type_identity": True,
    },
    "Match": {
        "name": "Match", "qualified_name": module.Match.__qualname__,
        "public_module": module.Match.__module__,
        "native_owner_module": bridge_name,
        "native_bridge_identity": module.Match is bridge.Match,
        "public_type_identity": True,
    },
}
records = []
for kind, pattern, subject, expected_piece in (
    ("str", r"(.+)(.*?)\1", "[abracadabra]", "abracadabra"),
    ("bytes", br"(.+)(.*?)\1", b"[abracadabra]", b"abracadabra"),
):
    compiled = module.compile(pattern)
    if type(compiled) is not module.Pattern:
        raise RuntimeError("a V8 matcher returned an unowned Pattern: " + kind)
    actual = compiled.search(subject)
    if actual is None or type(actual) is not module.Match or type(actual) is not bridge.Match:
        raise RuntimeError("a V8 matcher returned a foreign native Match: " + kind)
    if actual.span() != (1, 12) or actual.group(0) != expected_piece:
        raise RuntimeError("the V8 native matcher returned an incorrect real result")
    representation = repr(actual)
    expected_repr = (
        "<re.Match object; span=(1, 12), match=" + repr(expected_piece) + ">"
    )
    if representation != expected_repr:
        raise RuntimeError("the V8 native Match has a non-CPython public representation")

    def exact_error(action, error_type, expected_message):
        try:
            action()
        except error_type as error:
            message = str(error).replace(hex(id(actual)), "0xADDRESS")
            if message != expected_message:
                raise RuntimeError("a V8 public error is not Python-compatible: " + message)
            return {"type": error_type.__name__, "message": message, "passed": True}
        except BaseException as error:
            raise RuntimeError("the V8 native object changed a public error class") from error
        raise RuntimeError("the V8 native object omitted a required public error")

    class_signature = exact_error(
        lambda: inspect.signature(module.Match.group), ValueError,
        "no signature found for builtin <method 'group' of 're.Match' objects>",
    )
    bound_signature = exact_error(
        lambda: inspect.signature(actual.group), ValueError,
        "no signature found for builtin <built-in method group of re.Match "
        "object at 0xADDRESS>",
    )
    weak = exact_error(
        lambda: weakref.ref(actual), TypeError,
        "cannot create weak reference to 're.Match' object",
    )
    readonly = {
        name: exact_error(
            lambda name=name: setattr(actual, name, None), AttributeError,
            "attribute '" + name + "' of 're.Match' objects is not writable",
        )
        for name in ("lastindex", "lastgroup", "regs")
    }
    pattern_readonly = exact_error(
        lambda: setattr(compiled, "groupindex", {}), AttributeError,
        "attribute 'groupindex' of 're.Pattern' objects is not writable",
    )
    records.append({
        "id": role + ":match-repr:" + kind,
        "kind": kind, "role": role, "span": [1, 12],
        "pattern_representation": repr(pattern),
        "subject_representation": repr(subject),
        "matched_representation": repr(expected_piece),
        "public_type_module": "re", "native_owner_module": bridge_name,
        "public_pattern_type_module": module.Pattern.__module__,
        "compiled_pattern_type_identity": type(compiled) is module.Pattern,
        "match_qualified_name": "Match",
        "actual_repr": representation, "expected_repr": expected_repr,
        "native_type_identity": True, "public_bridge_type_identity": True,
        "result_type_identity": True,
        "class_signature_error": class_signature,
        "bound_signature_error": bound_signature,
        "weakref_error": weak, "readonly_errors": readonly,
        "pattern_readonly_groupindex_error": pattern_readonly,
        "genuine_matching_executed": True, "passed": True,
    })

roundtrips = []
for public_name, origin in (("Pattern", module.Pattern), ("Match", module.Match)):
    for argument in (str, bytes):
        alias = origin[argument]
        if not isinstance(alias, types.GenericAlias):
            raise RuntimeError("the V8 native public class lost an actual GenericAlias")
        for protocol in (0, 2, 4, pickle.HIGHEST_PROTOCOL):
            row = {
                "origin": public_name, "argument": argument.__name__,
                "protocol": protocol, "passed": False,
            }
            try:
                restored = pickle.loads(pickle.dumps(alias, protocol=protocol))
                row["passed"] = (
                    isinstance(restored, types.GenericAlias)
                    and restored.__origin__ is origin
                    and restored.__args__ == (argument,)
                    and restored == alias
                    and hash(restored) == hash(alias)
                )
                if not row["passed"]:
                    row["error_type"] = "NativeIdentityMismatch"
                    row["error_message"] = (
                        "ordinary pickle did not restore the exact owned public origin"
                    )
            except Exception as error:
                row["error_type"] = type(error).__name__
                row["error_message"] = str(error)
            roundtrips.append(row)

after = stage07._verify_family_native_mappings(
    role, {"native_sha256_by_family": {role: expected}}
)
if after != before or after != expected:
    raise RuntimeError("the V8 owned native mapping changed during genuine matching")
loaded = sorted(
    name for name, value in sys.modules.items()
    if name.startswith("candidates.") and value is not None
    and not isinstance(value, stage07._ForbiddenRegexModule)
)
if loaded != sorted({candidate_name, bridge_name}):
    raise RuntimeError("the V8 native worker retained a foreign candidate")
if not sys.meta_path or sys.meta_path[0] is not finder:
    raise RuntimeError("the V8 persistent cross-engine import guard disappeared")
if builtins.__import__ is not protected_import:
    raise RuntimeError("the genuine native engine replaced the guarded Python importer")
if any(sys.modules.get(name) is not value
       for name, value in protected_modules.items()):
    raise RuntimeError("the genuine native engine replaced a poisoned matching module")
if tuple(callable_identity(item) for item in current_native_loader_aliases()) != (
    protected_loader_identities
):
    raise RuntimeError("the genuine native engine replaced a protected dynamic loader")
regex_guards_after = audit_python_matchers()
foreign_guards_after = audit_foreign_engines()
loader_guards_after = audit_native_loaders()
if (regex_guards_after != regex_guards
        or foreign_guards_after != foreign_guards_before
        or loader_guards_after != loader_guards):
    raise RuntimeError("an active matching, external-engine, or loader poison changed")
passed = len(roundtrips) == 16 and all(row["passed"] for row in roundtrips)
output = {
    "schema": "rebar-postfinal-from-scratch-audit-v8-native-owner-worker",
    "status": "PASS" if passed else "FAIL",
    "result": "PASS" if passed else "FAIL", "passed": passed,
    "family": role, "candidate_module": candidate_name,
    "native_bridge_module": bridge_name,
    "native_binary_sha256": after,
    "loaded_candidate_modules": loaded,
    "guard": guard,
    "regex_guard_observations": regex_guards,
    "regex_guard_observations_after": regex_guards_after,
    "regex_guard_count": len(regex_guards),
    "foreign_engine_guard_observations": foreign_guards_before,
    "foreign_engine_guard_observations_after": foreign_guards_after,
    "native_loader_guard_observations": loader_guards,
    "native_loader_guard_observations_after": loader_guards_after,
    "native_loader_guard_count": len(loader_guards),
    "guarded_builtin_import_unchanged": True,
    "poisoned_module_bindings_unchanged": True,
    "protected_loader_identities_unchanged": True,
    "persistent_cross_engine_guard": True,
    "external_engine_guard_count": len(foreign),
    "public_type_ownership": owners,
    "records": records, "match_repr_checks": len(records),
    "standard_pickle_checks": roundtrips,
    "standard_pickle_check_count": len(roundtrips),
    "standard_pickle_failure_count": sum(not row["passed"] for row in roundtrips),
    "native_type_identity_verified": True,
    "public_cpython_module_verified": True,
    "genuine_matching_executed": True,
    "external_regex_packages": 0,
    "benchmark_or_timing_executed": False,
    "holdout_or_case_fixture_access": False,
}
sys.stdout.write(json.dumps(output, sort_keys=True, ensure_ascii=True) + "\n")
'''


def validate_worker_source(source: str = NATIVE_OWNER_WORKER) -> ast.Module:
    require(isinstance(source, str) and bool(source),
            "the exact V8 native-owner worker source is missing")
    try:
        tree = ast.parse(source, filename="<frozen-v8-native-owner>")
        compile(tree, "<frozen-v8-native-owner>", "exec")
    except (SyntaxError, TypeError, ValueError) as error:
        raise AuditV8Error("the real native-owner worker cannot be compiled") from error
    assignments: dict[str, list[int]] = {}
    for index, statement in enumerate(tree.body):
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name):
                    assignments.setdefault(target.id, []).append(index)
    for name in ("owners", "records", "roundtrips", "output"):
        require(len(assignments.get(name, [])) == 1,
                "a real native-owner assignment is unreachable or repeated: " + name)
    require(assignments["owners"][0] < assignments["records"][0]
            < assignments["roundtrips"][0] < assignments["output"][0],
            "the actual native-owner proof and matching evidence are unreachable")
    require('importlib.import_module("re")' not in source
            and "sys.modules['re'] =" not in source
            and 'sys.modules["re"] =' not in source,
            "the native-owner worker substituted the genuine Python re module")
    return tree


def validate_worker(
    document: Any, family: str, expected_native: Mapping[str, str],
    *, allow_failure: bool = False,
) -> dict[str, Any]:
    require(family in CORE_FAMILIES and isinstance(document, dict),
            "the isolated V8 native-owner evidence is malformed")
    candidate = "candidates." + family + "_candidate"
    bridge = OWNED_NATIVE_MODULES[family]
    exact = {
        "schema": SCHEMA + "-native-owner-worker",
        "family": family, "candidate_module": candidate,
        "native_bridge_module": bridge,
        "match_repr_checks": 2,
        "standard_pickle_check_count": 16,
        "regex_guard_count": 13,
        "native_loader_guard_count": len(NATIVE_LOADER_ALIASES),
        "persistent_cross_engine_guard": True,
        "guarded_builtin_import_unchanged": True,
        "poisoned_module_bindings_unchanged": True,
        "protected_loader_identities_unchanged": True,
        "native_type_identity_verified": True,
        "public_cpython_module_verified": True,
        "genuine_matching_executed": True,
        "external_regex_packages": 0,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
    }
    for key, value in exact.items():
        require(document.get(key) == value,
                "the genuine V8 native owner changed: " + family + ":" + key)
    require(document.get("native_binary_sha256") == dict(expected_native)
            and document.get("loaded_candidate_modules") == sorted({candidate, bridge}),
            "a genuine V8 match used stale, foreign, or unmapped native binaries")
    guard = document.get("guard")
    require(isinstance(guard, dict) and guard.get("family") == family
            and guard.get("native_loader_aliases_blocked") == list(NATIVE_LOADER_ALIASES)
            and all(guard.get(key) is True for key in (
                "enabled", "stdlib_re_blocked", "cpython_sre_blocked",
                "third_party_regex_blocked", "cross_family_blocked",
                "foreign_dynamic_libraries_blocked",
            )), "a V8 native matching worker weakened its persistent owner guards")
    regex = document.get("regex_guard_observations")
    entries = (
        ("re", "compile"), ("re", "search"), ("re", "match"),
        ("re", "fullmatch"), ("re", "findall"), ("re", "finditer"),
        ("re", "split"), ("re", "sub"), ("re", "subn"),
        ("re", "_compile"), ("_sre", "compile"),
        ("re._compiler", "compile"), ("re._parser", "parse"),
    )
    require(isinstance(regex, list) and len(regex) == len(entries)
            and [
                (item.get("module"), item.get("name"), item.get("blocked"))
                for item in regex if isinstance(item, dict)
            ] == [(module, name, True) for module, name in entries],
            "the isolated V8 worker lost an original CPython regex poison")
    require(document.get("regex_guard_observations_after") == regex,
            "a V8 native matcher restored a poisoned Python regex entry point")
    expected_foreign = {
        "regex", "_regex", "re2", "pyre2", "pcre", "pcre2",
        "hyperscan", "rure", "oniguruma", "onig",
        "candidates.ast_candidate",
    }
    expected_foreign.update(
        "candidates." + other + "_candidate"
        for other in CORE_FAMILIES if other != family
    )
    expected_foreign.update(
        OWNED_NATIVE_MODULES[other]
        for other in CORE_FAMILIES if other != family
    )
    foreign = document.get("foreign_engine_guard_observations")
    require(isinstance(foreign, list)
            and foreign == [
                {"module": name, "blocked": True}
                for name in sorted(expected_foreign)
            ]
            and document.get("external_engine_guard_count") == len(expected_foreign)
            and document.get("foreign_engine_guard_observations_after") == foreign,
            "a V8 native matcher restored a foreign or cross-family engine")
    loaders = document.get("native_loader_guard_observations")
    require(loaders == [
        {"alias": name, "blocked": True} for name in NATIVE_LOADER_ALIASES
    ] and document.get("native_loader_guard_observations_after") == loaders,
            "a V8 native matcher restored a forbidden actual dynamic loader")
    owners = document.get("public_type_ownership")
    require(isinstance(owners, dict) and set(owners) == {"Pattern", "Match"},
            "the genuine V8 worker omitted its actual public Pattern or Match")
    match = owners["Match"]
    pattern = owners["Pattern"]
    require(isinstance(match, dict)
            and match.get("name") == "Match"
            and match.get("qualified_name") == "Match"
            and match.get("public_module") == "re"
            and match.get("native_owner_module") == bridge
            and match.get("native_bridge_identity") is True
            and match.get("public_type_identity") is True,
            "the real native Match is not both bridge-owned and Python-compatible")
    require(isinstance(pattern, dict)
            and pattern.get("name") == "Pattern"
            and pattern.get("qualified_name") == "Pattern"
            and pattern.get("public_module") == "re"
            and pattern.get("native_owner_module") == candidate
            and type(pattern.get("native_bridge_identity")) is bool
            and pattern.get("public_type_identity") is True,
            "the V8 public Pattern lost its genuine owned candidate identity")
    rows = document.get("records")
    require(isinstance(rows, list) and len(rows) == 2,
            "the V8 native owner omitted a genuine text or bytes result")
    for index, (kind, expression, subject, match_text) in enumerate((
        ("str", r"(.+)(.*?)\1", "[abracadabra]", "abracadabra"),
        ("bytes", br"(.+)(.*?)\1", b"[abracadabra]", b"abracadabra"),
    )):
        row = rows[index]
        display = "<re.Match object; span=(1, 12), match=" + repr(match_text) + ">"
        require(isinstance(row, dict)
                and row.get("id") == family + ":match-repr:" + kind
                and row.get("kind") == kind and row.get("role") == family
                and row.get("span") == [1, 12]
                and row.get("pattern_representation") == repr(expression)
                and row.get("subject_representation") == repr(subject)
                and row.get("matched_representation") == repr(match_text)
                and row.get("public_type_module") == "re"
                and row.get("native_owner_module") == bridge
                and row.get("public_pattern_type_module") == "re"
                and row.get("compiled_pattern_type_identity") is True
                and row.get("match_qualified_name") == "Match"
                and row.get("actual_repr") == display
                and row.get("expected_repr") == display
                and row.get("native_type_identity") is True
                and row.get("public_bridge_type_identity") is True
                and row.get("result_type_identity") is True
                and row.get("genuine_matching_executed") is True
                and row.get("passed") is True,
                "a V8 owned native match forged its Python-visible identity: "
                + family + "/" + kind)
        for field, error_type, message in (
            ("class_signature_error", "ValueError",
             "no signature found for builtin <method 'group' of 're.Match' objects>"),
            ("bound_signature_error", "ValueError",
             "no signature found for builtin <built-in method group of re.Match "
             "object at 0xADDRESS>"),
            ("weakref_error", "TypeError",
             "cannot create weak reference to 're.Match' object"),
        ):
            evidence = row.get(field)
            require(isinstance(evidence, dict)
                    and evidence.get("type") == error_type
                    and evidence.get("message") == message
                    and evidence.get("passed") is True,
                    "a V8 real native public error differs from CPython: "
                    + family + "/" + kind + "/" + field)
        readonly = row.get("readonly_errors")
        require(isinstance(readonly, dict)
                and set(readonly) == {"lastindex", "lastgroup", "regs"},
                "a V8 native match omitted a frozen read-only attribute")
        for name, detail in readonly.items():
            require(isinstance(detail, dict)
                    and detail.get("type") == "AttributeError"
                    and detail.get("message")
                    == "attribute '" + name + "' of 're.Match' objects is not writable"
                    and detail.get("passed") is True,
                    "a V8 genuine native attribute error is not CPython-identical")
        groupindex = row.get("pattern_readonly_groupindex_error")
        require(isinstance(groupindex, dict)
                and groupindex.get("type") == "AttributeError"
                and groupindex.get("message")
                == "attribute 'groupindex' of 're.Pattern' objects is not writable"
                and groupindex.get("passed") is True,
                "the actual native Pattern descriptor owner is not Python-compatible")

    checks = document.get("standard_pickle_checks")
    require(isinstance(checks, list) and len(checks) == 16,
            "a V8 owner concealed a genuine public pickle or GenericAlias case")
    expected = [
        (origin, argument, protocol)
        for origin in ("Pattern", "Match")
        for argument in ("str", "bytes")
        for protocol in PICKLE_PROTOCOLS
    ]
    require(all(isinstance(item, dict) for item in checks)
            and [(item.get("origin"), item.get("argument"), item.get("protocol"))
                 for item in checks] == expected,
            "the V8 public pickle observation denominator was changed")
    failures = sum(item.get("passed") is not True for item in checks)
    require(document.get("standard_pickle_failure_count") == failures,
            "an actual V8 native pickle failure was hidden")
    for item in checks:
        require(type(item.get("passed")) is bool,
                "a V8 genuine public pickle check has no actual result")
        if item["passed"] is False:
            require(isinstance(item.get("error_type"), str)
                    and isinstance(item.get("error_message"), str),
                    "a failed genuine native pickle lost its actual diagnosis")
    expected_status = "FAIL" if failures else "PASS"
    require(document.get("status") == expected_status
            and document.get("result") == expected_status
            and document.get("passed") is (not failures),
            "the V8 native owner relabeled a real pickle failure")
    require(allow_failure or not failures,
            "the native-owned re.Match generic alias cannot yet survive actual pickle")
    return document


def worker_failure_evidence(
    family: str, returncode: int | None, stdout: bytes | None,
    stderr: bytes | None, *, timed_out: bool = False,
    message: str,
) -> dict[str, Any]:
    observed_stdout = stdout if isinstance(stdout, bytes) else b""
    observed_stderr = stderr if isinstance(stderr, bytes) else b""
    stdout_complete = len(observed_stdout) <= MAX_WORKER_BYTES
    stderr_complete = len(observed_stderr) <= MAX_WORKER_BYTES
    retained_stdout = observed_stdout[:MAX_WORKER_BYTES]
    retained_stderr = observed_stderr[:MAX_WORKER_BYTES]
    return {
        "status": "FAIL", "family": family,
        "candidate_module": "candidates." + family + "_candidate",
        "native_bridge_module": OWNED_NATIVE_MODULES.get(family),
        "actual_returncode": returncode,
        "signal": -returncode if isinstance(returncode, int) and returncode < 0 else None,
        "timed_out": timed_out,
        "timeout_seconds": 120 if timed_out else None,
        "stdout_bytes": len(observed_stdout),
        "stderr_bytes": len(observed_stderr),
        "stdout_complete": stdout_complete,
        "stderr_complete": stderr_complete,
        "stdout_sha256": hashlib.sha256(observed_stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(observed_stderr).hexdigest(),
        "stdout_preserved_prefix_sha256": hashlib.sha256(retained_stdout).hexdigest(),
        "stderr_preserved_prefix_sha256": hashlib.sha256(retained_stderr).hexdigest(),
        "stdout_base64": base64.b64encode(retained_stdout).decode("ascii"),
        "stderr_base64": base64.b64encode(retained_stderr).decode("ascii"),
        "failure_message": message,
        "production_observations_invented": False,
        "qualifies_current_engine": False,
    }


def run_native_worker(family: str, expected: Mapping[str, str]) -> dict[str, Any]:
    require(family in CORE_FAMILIES and isinstance(expected, dict) and bool(expected),
            "refusing an unowned V8 native family worker")
    validate_worker_source()
    payload = json.dumps(expected, ensure_ascii=True,
                         sort_keys=True, separators=(",", ":"))
    require(len(payload.encode("ascii")) <= 16 * 1024,
            "the V8 native-owner command exceeded its safe boundary")
    environment = {
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
        "PYTHONPATH": str(ROOT), "LC_ALL": "C", "PATH": "/usr/bin:/bin",
    }
    try:
        child = subprocess.run(
            [str(PINNED_EXECUTABLE), "-I", "-B", "-c", NATIVE_OWNER_WORKER,
             str(ROOT), family, payload],
            cwd=str(ROOT), env=environment, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, timeout=120,
        )
    except subprocess.TimeoutExpired as error:
        evidence = worker_failure_evidence(
            family, None, error.stdout, error.stderr, timed_out=True,
            message="the genuine native-owner worker exceeded its fixed 120-second limit",
        )
        raise NativeWorkerFailure(evidence["failure_message"], evidence) from error
    if (child.returncode != 0 or not 0 < len(child.stdout) <= MAX_WORKER_BYTES
            or len(child.stderr) > MAX_WORKER_BYTES):
        evidence = worker_failure_evidence(
            family, child.returncode, child.stdout, child.stderr,
            message="the genuine isolated native-owner worker crashed or returned unsafe evidence",
        )
        raise NativeWorkerFailure(evidence["failure_message"], evidence)
    try:
        report = core.decode_report(child.stdout, label="genuine V8 native owner")
        return validate_worker(report, family, expected, allow_failure=True)
    except (source_v6.AuditV6Error, UnicodeError, ValueError, TypeError,
            KeyError) as error:
        evidence = worker_failure_evidence(
            family, child.returncode, child.stdout, child.stderr,
            message="the genuine native owner returned incomplete or forged evidence: "
            + str(error),
        )
        raise NativeWorkerFailure(evidence["failure_message"], evidence) from error


def synthetic_worker(family: str) -> tuple[dict[str, Any], dict[str, str]]:
    require(family in CORE_FAMILIES, "a synthetic V8 owner requested a foreign family")
    bridge = OWNED_NATIVE_MODULES[family]
    candidate = "candidates." + family + "_candidate"
    native = {
        relative: hashlib.sha256(("v8-synthetic:" + relative).encode("ascii")).hexdigest()
        for relative in OWNED_NATIVE_PATHS[family].values()
    }
    entries = (
        ("re", "compile"), ("re", "search"), ("re", "match"),
        ("re", "fullmatch"), ("re", "findall"), ("re", "finditer"),
        ("re", "split"), ("re", "sub"), ("re", "subn"),
        ("re", "_compile"), ("_sre", "compile"),
        ("re._compiler", "compile"), ("re._parser", "parse"),
    )
    rows = []
    foreign_names = {
        "regex", "_regex", "re2", "pyre2", "pcre", "pcre2",
        "hyperscan", "rure", "oniguruma", "onig",
        "candidates.ast_candidate",
    }
    foreign_names.update(
        "candidates." + other + "_candidate"
        for other in CORE_FAMILIES if other != family
    )
    foreign_names.update(
        OWNED_NATIVE_MODULES[other]
        for other in CORE_FAMILIES if other != family
    )
    foreign_guards = [
        {"module": name, "blocked": True} for name in sorted(foreign_names)
    ]
    loader_guards = [
        {"alias": name, "blocked": True} for name in NATIVE_LOADER_ALIASES
    ]
    for kind, expression, subject, match_text in (
        ("str", r"(.+)(.*?)\1", "[abracadabra]", "abracadabra"),
        ("bytes", br"(.+)(.*?)\1", b"[abracadabra]", b"abracadabra"),
    ):
        display = "<re.Match object; span=(1, 12), match=" + repr(match_text) + ">"
        row = {
            "id": family + ":match-repr:" + kind, "kind": kind, "role": family,
            "span": [1, 12], "pattern_representation": repr(expression),
            "subject_representation": repr(subject),
            "matched_representation": repr(match_text),
            "public_type_module": "re", "native_owner_module": bridge,
            "public_pattern_type_module": "re",
            "compiled_pattern_type_identity": True,
            "match_qualified_name": "Match",
            "actual_repr": display, "expected_repr": display,
            "native_type_identity": True, "public_bridge_type_identity": True,
            "result_type_identity": True, "genuine_matching_executed": True,
            "passed": True,
            "class_signature_error": {
                "type": "ValueError", "message":
                "no signature found for builtin <method 'group' of 're.Match' objects>",
                "passed": True,
            },
            "bound_signature_error": {
                "type": "ValueError", "message":
                "no signature found for builtin <built-in method group of re.Match "
                "object at 0xADDRESS>", "passed": True,
            },
            "weakref_error": {
                "type": "TypeError",
                "message": "cannot create weak reference to 're.Match' object",
                "passed": True,
            },
            "readonly_errors": {
                name: {
                    "type": "AttributeError",
                    "message": "attribute '" + name
                    + "' of 're.Match' objects is not writable",
                    "passed": True,
                }
                for name in ("lastindex", "lastgroup", "regs")
            },
            "pattern_readonly_groupindex_error": {
                "type": "AttributeError",
                "message":
                    "attribute 'groupindex' of 're.Pattern' objects is not writable",
                "passed": True,
            },
        }
        rows.append(row)
    pickles = [
        {"origin": origin, "argument": argument,
         "protocol": protocol, "passed": True}
        for origin in ("Pattern", "Match")
        for argument in ("str", "bytes") for protocol in PICKLE_PROTOCOLS
    ]
    report = {
        "schema": SCHEMA + "-native-owner-worker",
        "status": "PASS", "result": "PASS", "passed": True,
        "family": family, "candidate_module": candidate,
        "native_bridge_module": bridge,
        "native_binary_sha256": native,
        "loaded_candidate_modules": sorted({candidate, bridge}),
        "guard": {
            "enabled": True, "family": family,
            "stdlib_re_blocked": True, "cpython_sre_blocked": True,
            "third_party_regex_blocked": True, "cross_family_blocked": True,
            "foreign_dynamic_libraries_blocked": True,
            "native_loader_aliases_blocked": list(NATIVE_LOADER_ALIASES),
        },
        "regex_guard_observations": [
            {"module": module, "name": name, "blocked": True}
            for module, name in entries
        ],
        "regex_guard_observations_after": [
            {"module": module, "name": name, "blocked": True}
            for module, name in entries
        ],
        "regex_guard_count": 13,
        "foreign_engine_guard_observations": foreign_guards,
        "foreign_engine_guard_observations_after": copy.deepcopy(foreign_guards),
        "native_loader_guard_observations": loader_guards,
        "native_loader_guard_observations_after": copy.deepcopy(loader_guards),
        "native_loader_guard_count": len(NATIVE_LOADER_ALIASES),
        "guarded_builtin_import_unchanged": True,
        "poisoned_module_bindings_unchanged": True,
        "protected_loader_identities_unchanged": True,
        "persistent_cross_engine_guard": True,
        "external_engine_guard_count": len(foreign_names),
        "public_type_ownership": {
            "Pattern": {
                "name": "Pattern", "qualified_name": "Pattern",
                "public_module": "re", "native_owner_module": candidate,
                "native_bridge_identity": False, "public_type_identity": True,
            },
            "Match": {
                "name": "Match", "qualified_name": "Match",
                "public_module": "re", "native_owner_module": bridge,
                "native_bridge_identity": True, "public_type_identity": True,
            },
        },
        "records": rows, "match_repr_checks": 2,
        "standard_pickle_checks": pickles,
        "standard_pickle_check_count": 16,
        "standard_pickle_failure_count": 0,
        "native_type_identity_verified": True,
        "public_cpython_module_verified": True,
        "genuine_matching_executed": True, "external_regex_packages": 0,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
    }
    return report, native


def candidate_free_self_test() -> dict[str, Any]:
    core.ensure_candidate_free()
    inherited = historical_v7.self_test()
    require(inherited.get("passed") is True and inherited.get("check_count", 0) >= 468,
            "the unchanged 468 historical source-only protections failed")
    checks: list[dict[str, Any]] = []

    def accepted(name: str, condition: Any) -> None:
        checks.append({"name": name, "passed": bool(condition)})

    def rejected(name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except (AuditV8Error, source_v6.AuditV6Error,
                AssertionError, TypeError, ValueError, KeyError, OSError):
            accepted(name, True)
        else:
            accepted(name, False)

    effects = core.previous.BlockSelfTestEffects()
    with effects:
        for item in inherited["checks"]:
            accepted("historical-v7:" + item["name"], item.get("passed") is True)
        accepted("preserve-three-distinct-native-engine-families",
                 CORE_FAMILIES == ("rust", "vm", "zig"))
        accepted("preserve-twelve-current-owned-source-paths",
                 sum(len(paths) for paths in OWNED_SOURCE_PATHS.values()) == 12)
        accepted("preserve-five-current-owned-native-elf-roles",
                 sum(len(paths) for paths in OWNED_NATIVE_PATHS.values()) == 5)
        accepted("preserve-sixteen-genuine-public-pickle-cases-per-family",
                 len(PICKLE_PROTOCOLS) == 4)
        accepted("preserve-actual-complete-rust-edge-failure",
                 V7_EDGE_FAILURES.get("rust", (None, None))[1]
                 == "3ffdb21d10f40deabd70fa1f408fa38ff2b027a2d269c4b75e607a05cefde3b8")
        accepted("preserve-all-three-complete-real-current-build-edge-failures",
                 set(V7_EDGE_FAILURES) == set(CORE_FAMILIES)
                 and V7_EDGE_FAILURES["vm"][1]
                 == "2cce7c26d2487c8e400d2fd6b8cfbc81d4b734b08f7a8f356def910a9cbb385c"
                 and V7_EDGE_FAILURES["zig"][1]
                 == "5fa7283942994139d531593cc1bdf25f5da48f6de424d7604ce2ce569100788a")
        tree = validate_worker_source()
        accepted("compile-real-native-owner-worker-without-executing-candidates",
                 isinstance(compile(tree, "<frozen-v8-native-owner>", "exec"),
                            type(compile("pass", "<synthetic>", "exec"))))
        accepted("require-native-owner-records-at-worker-module-scope",
                 any(isinstance(statement, ast.Assign)
                     and any(isinstance(target, ast.Name) and target.id == "owners"
                             for target in statement.targets)
                     for statement in tree.body))
        rejected("reject-unreachable-nested-native-owner-proof",
                 lambda: validate_worker_source(NATIVE_OWNER_WORKER.replace(
                     "\nowners = {\n", "\n    owners = {\n", 1
                 )))
        rejected("reject-unreachable-native-result-records",
                 lambda: validate_worker_source(NATIVE_OWNER_WORKER.replace(
                     "\nrecords = []\n", "\n    records = []\n", 1
                 )))
        oversized = b"v8-real-worker-observation:" * (
            MAX_WORKER_BYTES // len(b"v8-real-worker-observation:") + 2
        )
        crash = worker_failure_evidence(
            "rust", -9, oversized, b"synthetic actual native signal",
            message="synthetic isolated native worker signal",
        )
        accepted("preserve-complete-observed-crash-stream-digest",
                 crash["stdout_sha256"] == hashlib.sha256(oversized).hexdigest()
                 and crash["stdout_preserved_prefix_sha256"]
                 == hashlib.sha256(oversized[:MAX_WORKER_BYTES]).hexdigest()
                 and crash["stdout_sha256"]
                 != crash["stdout_preserved_prefix_sha256"]
                 and crash["stdout_bytes"] == len(oversized)
                 and crash["stdout_complete"] is False)
        accepted("preserve-real-native-worker-signal-without-inventing-rows",
                 crash["signal"] == 9 and crash["actual_returncode"] == -9
                 and crash["production_observations_invented"] is False
                 and crash["qualifies_current_engine"] is False)
        accepted("preserve-candidate-native-identity-with-python-public-name",
                 "module.Match is not bridge.Match" in NATIVE_OWNER_WORKER
                 and 'module.Match.__module__ != "re"' in NATIVE_OWNER_WORKER
                 and "type(actual) is not bridge.Match" in NATIVE_OWNER_WORKER
                 and 'importlib.import_module("re")' not in NATIVE_OWNER_WORKER)
        for family in CORE_FAMILIES:
            original, native = synthetic_worker(family)
            accepted("accept-complete-in-memory-python-compatible-owner:" + family,
                     validate_worker(copy.deepcopy(original), family, native) is not None)

            def poison(label: str, change: Callable[[dict[str, Any]], None]) -> None:
                changed = copy.deepcopy(original)
                change(changed)
                rejected("reject-" + family + ":" + label,
                         lambda: validate_worker(changed, family, native))

            poison("native-match-owner-forgery", lambda row:
                   row["public_type_ownership"]["Match"].update(
                       native_owner_module=OWNED_NATIVE_MODULES[
                           next(item for item in CORE_FAMILIES if item != family)
                       ]
                   ))
            poison("public-match-module-not-re", lambda row:
                   row["public_type_ownership"]["Match"].update(
                       public_module=OWNED_NATIVE_MODULES[family]
                   ))
            poison("false-native-bridge-identity", lambda row:
                   row["public_type_ownership"]["Match"].update(
                       native_bridge_identity=False
                   ))
            poison("false-public-type-identity", lambda row:
                   row["public_type_ownership"]["Match"].update(
                       public_type_identity=False
                   ))
            poison("foreign-native-elf-mapping", lambda row:
                   row["native_binary_sha256"].update({"foreign.so": "0" * 64}))
            poison("missing-thirteenth-python-matching-guard", lambda row:
                   row["regex_guard_observations"].pop())
            poison("disabled-persistent-cross-engine-guard", lambda row:
                   row.update(persistent_cross_engine_guard=False))
            for field in (
                "guarded_builtin_import_unchanged",
                "poisoned_module_bindings_unchanged",
                "protected_loader_identities_unchanged",
            ):
                poison("changed-post-matching-guard:" + field,
                       lambda row, field=field: row.update({field: False}))
            poison("removed-post-matching-regex-guard", lambda row:
                   row["regex_guard_observations_after"].pop())
            poison("removed-post-matching-foreign-engine-guard", lambda row:
                   row["foreign_engine_guard_observations_after"].pop())
            poison("removed-post-matching-native-loader-guard", lambda row:
                   row["native_loader_guard_observations_after"].pop())
            for flag in ("stdlib_re_blocked", "cpython_sre_blocked",
                         "third_party_regex_blocked", "cross_family_blocked",
                         "foreign_dynamic_libraries_blocked"):
                poison("disabled-guard:" + flag,
                       lambda row, flag=flag: row["guard"].update({flag: False}))
            poison("missing-native-loader-alias", lambda row:
                   row["guard"]["native_loader_aliases_blocked"].pop())
            poison("missing-owned-string-or-bytes-observation", lambda row:
                   row["records"].pop())
            poison("synthetic-public-owner-only", lambda row:
                   row["records"][0].update(native_type_identity=False))
            poison("crossed-observed-native-owner", lambda row:
                   row["records"][0].update(native_owner_module="candidates._foreign"))
            poison("non-cpython-observed-repr", lambda row:
                   row["records"][0].update(actual_repr="<foreign.Match>"))
            poison("non-cpython-class-signature-error", lambda row:
                   row["records"][0]["class_signature_error"].update(message="foreign"))
            poison("non-cpython-bound-signature-error", lambda row:
                   row["records"][0]["bound_signature_error"].update(message="foreign"))
            poison("non-cpython-weak-reference-error", lambda row:
                   row["records"][0]["weakref_error"].update(message="foreign"))
            poison("non-cpython-native-pattern-groupindex-error", lambda row:
                   row["records"][0]["pattern_readonly_groupindex_error"].update(
                       message="foreign"
                   ))
            poison("foreign-native-pattern-descriptor-owner", lambda row:
                   row["public_type_ownership"]["Pattern"].update(
                       public_module="candidates._foreign.Pattern"
                   ))
            poison("non-cpython-actual-pattern-public-module", lambda row:
                   row["records"][0].update(public_pattern_type_module="candidates._foreign"))
            poison("foreign-compiled-native-pattern-identity", lambda row:
                   row["records"][0].update(compiled_pattern_type_identity=False))
            for attribute in ("lastindex", "lastgroup", "regs"):
                poison("non-cpython-readonly-" + attribute,
                       lambda row, attribute=attribute:
                       row["records"][1]["readonly_errors"][attribute].update(
                           message="foreign"
                       ))
            poison("missing-genuine-public-pickle-case", lambda row:
                   row["standard_pickle_checks"].pop())
            poison("changed-genuine-public-pickle-protocol", lambda row:
                   row["standard_pickle_checks"][0].update(protocol=99))
            poison("hidden-native-match-pickle-failure", lambda row:
                   row["standard_pickle_checks"][8].update(
                       passed=False, error_type="PicklingError",
                       error_message="re.Match is not the same native owner"
                   ))
            poison("reclassified-pickle-failure-as-pass", lambda row:
                   row.update(standard_pickle_failure_count=1))
            poison("retained-cross-family-native-module", lambda row:
                   row["loaded_candidate_modules"].append("candidates._foreign"))
            poison("benchmark-scope-fabrication", lambda row:
                   row.update(benchmark_or_timing_executed=True))
            poison("holdout-scope-fabrication", lambda row:
                   row.update(holdout_or_case_fixture_access=True))

            genuine_failure = copy.deepcopy(original)
            genuine_failure["standard_pickle_checks"][8].update({
                "passed": False, "error_type": "PicklingError",
                "error_message": "re.Match is not the same native owner",
            })
            genuine_failure.update({
                "status": "FAIL", "result": "FAIL", "passed": False,
                "standard_pickle_failure_count": 1,
            })
            accepted("preserve-genuine-full-pickle-failure-without-qualification:" + family,
                     validate_worker(genuine_failure, family, native,
                                     allow_failure=True)["status"] == "FAIL")
            rejected("reject-genuine-pickle-failure-as-a-passing-owner:" + family,
                     lambda failure=genuine_failure, role=family, owned=native:
                     validate_worker(failure, role, owned))

        for relative in (
            "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json",
            "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json",
            "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V8.json",
            "performance/held-out.json", "../POSTFINAL-FROM-SCRATCH-AUDIT-V8.json",
        ):
            rejected("reject-unapproved-source-audit-output:" + relative,
                     lambda relative=relative: destination_name(relative))
        accepted("accept-only-exact-exclusive-v8-source-output",
                 destination_name(REPORT_RELATIVE) == REPORT_RELATIVE)

    require(len(checks) >= 540 and all(item["passed"] for item in checks),
            "a candidate-free V8 native-ownership poison escaped its validator")
    require(len({item["name"] for item in checks}) == len(checks),
            "a V8 source-only ownership case was repeated")
    require(effects.counts["processes"] == 0
            and effects.counts["files"] == 0
            and effects.counts["clocks"] == 0,
            "the candidate-free V8 ownership self-test caused a production side effect")
    core.ensure_candidate_free()
    return {
        "schema": SCHEMA + "-self-test", "status": "PASS", "passed": True,
        "check_count": len(checks), "checks": checks,
        "historical_v7_control_count": inherited["check_count"],
        "candidate_imports": 0, "subprocesses": effects.counts["processes"],
        "file_reads": effects.counts["files"],
        "file_writes": effects.counts["files"],
        "clock_samples": effects.counts["clocks"],
        "owned_source_count": 12, "owned_native_binary_count": 5,
        "native_family_count": 3,
        "genuine_public_pickle_checks_required": 48,
        "genuine_python_matching_guards_per_family": 13,
        "historical_actual_rust_edge_failure_sha256": V7_EDGE_FAILURES["rust"][1],
        "synthetic_results_qualify_candidates": False,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
    }


def audit() -> dict[str, Any]:
    runtime = core.verify_production_runtime()
    core.ensure_candidate_free()
    history = verify_history()
    controls = candidate_free_self_test()
    core.ensure_candidate_free()
    gc.collect()
    with source_v5.allow_owned_locale_ctype():
        current = core.audit()
    core.validate_v3_report(current, label="genuine fresh V8 bounded native source audit")
    graph = source_v6._validate_fresh_graph(current)
    core.ensure_candidate_free()
    observations: dict[str, dict[str, Any]] = {}
    worker_failure: dict[str, Any] | None = None
    for family in CORE_FAMILIES:
        try:
            observations[family] = run_native_worker(
                family, graph["native_sha256_by_family"][family]
            )
        except NativeWorkerFailure as error:
            worker_failure = error.evidence
            break
    core.ensure_candidate_free()
    pickle_failures = sum(
        worker["standard_pickle_failure_count"] for worker in observations.values()
    )
    passed = worker_failure is None and len(observations) == len(CORE_FAMILIES)
    passed = passed and not pickle_failures
    source_sha256, _ = core.bounded_file(
        SOURCE_PATH, maximum=MAX_SOURCE_BYTES,
        label="actual immutable V8 native source-audit controller",
    )
    report = dict(current)
    report.update({
        "schema": SCHEMA, "postfinal_schema": SCHEMA,
        "status": "PASS" if passed else "FAIL",
        "result": "PASS" if passed else "FAIL", "passed": passed,
        "audit_source_path": SOURCE_RELATIVE,
        "audit_source_sha256": source_sha256,
        "native_ownership_protocol_path": PROTOCOL_RELATIVE,
        "native_ownership_protocol_sha256": PROTOCOL_SHA256,
        "historical_v7_source_path": "tools/postfinal_from_scratch_audit_v7.py",
        "historical_v7_source_sha256": FROZEN_HISTORY[
            "tools/postfinal_from_scratch_audit_v7.py"
        ],
        "historical_v7_source_report_path":
            "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json",
        "historical_v7_source_report_sha256": FROZEN_HISTORY[
            "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json"
        ],
        "historical_v7_strict_report_path":
            "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json",
        "historical_v7_strict_report_sha256": FROZEN_HISTORY[
            "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json"
        ],
        "historical_v7_results_qualify_current_build": False,
        "historical_public_input_sha256": history["historical_input_sha256"],
        "historical_current_build_edge_failures": history["real_edge_failures"],
        "historical_first_campaign_failure_preserved": True,
        "postfinal_wrapper_self_test": controls,
        "postfinal_interpreter": runtime,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": graph["source_count"],
        "verified_candidate_source_paths": graph["source_paths"],
        "verified_native_role_count": graph["native_binary_count"],
        "native_sha256_by_family": graph["native_sha256_by_family"],
        "public_type_ownership": {
            family: worker["public_type_ownership"]
            for family, worker in observations.items()
        },
        "public_match_repr": observations,
        "match_repr_checks_per_family": 2,
        "verified_match_repr_checks": sum(
            worker["match_repr_checks"] for worker in observations.values()
        ),
        "standard_pickle_checks_per_family": 16,
        "standard_pickle_checks": sum(
            worker["standard_pickle_check_count"] for worker in observations.values()
        ),
        "standard_pickle_failure_count": pickle_failures,
        "actual_native_owner_workers": observations,
        "actual_native_owner_worker_failure": worker_failure,
        "completed_native_owner_worker_count": len(observations),
        "unstarted_native_owner_families": [
            family for family in CORE_FAMILIES
            if family not in observations
            and (worker_failure is None or family != worker_failure.get("family"))
        ],
        "postfinal_scope": {
            "append_only": True, "exclusive_report_path": REPORT_RELATIVE,
            "previous_v7_source_report_preserved": True,
            "previous_v7_strict_report_preserved": True,
            "previous_v7_reports_historical": True,
            "actual_edge_failures_preserved": True,
            "exact_current_owned_candidate_source_count": 12,
            "actual_current_native_binary_count": 5,
            "actual_native_matching_workers": len(observations)
                + int(worker_failure is not None),
            "genuine_public_pickle_checks": sum(
                worker["standard_pickle_check_count"]
                for worker in observations.values()
            ),
            "genuine_match_repr_checks": sum(
                worker["match_repr_checks"] for worker in observations.values()
            ),
            "actual_python_matching_guards_per_family": 13,
            "native_identity_is_independent_of_public_module": True,
            "candidate_imports": "isolated guarded subprocesses only",
            "mapped_binaries_hashed_against_static_elf": True,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
    })
    require(report["verified_candidate_source_count"] == 12
            and report["verified_native_role_count"] == 5,
            "the actual V8 owned-source or native-ELF denominator changed")
    if passed:
        require(report["verified_match_repr_checks"] == 6
                and report["standard_pickle_checks"] == 48,
                "a passing V8 source audit weakened the match or pickle denominator")
    else:
        require(worker_failure is not None or pickle_failures > 0,
                "a failing V8 source audit invented its matching failure")
    core.ensure_candidate_free()
    return report


def write_report(report: Mapping[str, Any], target: Path = REPORT_PATH) -> str:
    require(isinstance(target, Path), "the exclusive V8 source destination is unsafe")
    relative = (
        target.relative_to(ROOT).as_posix()
        if target.is_absolute() and target.is_relative_to(ROOT)
        else target.as_posix() if not target.is_absolute() else ""
    )
    destination_name(relative)
    parent = REPORT_PATH.parent.resolve(strict=True)
    require(not target.is_symlink() and target.name == REPORT_PATH.name
            and target.parent.resolve(strict=True) == parent,
            "the exclusive V8 source destination is not the exact safe report")
    payload = core.canonical(report) + b"\n"
    require(len(payload) <= MAX_REPORT_BYTES,
            "the genuine complete V8 source evidence exceeds its bounded size")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    directory = os.open(parent, flags)
    try:
        require(stat.S_ISDIR(os.fstat(directory).st_mode),
                "the exclusive V8 report directory is not genuine")
        create = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        create |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
        descriptor = os.open(REPORT_PATH.name, create, 0o644, dir_fd=directory)
        try:
            pending = memoryview(payload)
            while pending:
                wrote = os.write(descriptor, pending)
                require(wrote > 0, "the exclusive V8 source-report write stalled")
                pending = pending[wrote:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.fsync(directory)
    finally:
        os.close(directory)
    return hashlib.sha256(payload).hexdigest()


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--gate", action="store_true")
    modes.add_argument("--audit", action="store_true")
    parser.add_argument("--output", type=Path, default=REPORT_PATH)
    options = parser.parse_args(arguments)
    try:
        core.ensure_candidate_free()
        if options.self_test:
            require(options.output == REPORT_PATH,
                    "a candidate-free V8 source self-test cannot redirect evidence")
            result = candidate_free_self_test()
            sys.stdout.buffer.write(core.canonical(result) + b"\n")
            return 0
        verify_fresh_report_target(options.output)
        report = audit()
        report_sha256 = write_report(report, options.output)
        result = {
            "schema": SCHEMA, "status": report["status"],
            "result": report["result"], "passed": report["passed"],
            "report": REPORT_RELATIVE, "report_sha256": report_sha256,
            "audit_source_sha256": report["audit_source_sha256"],
            "verified_core_family_count": 3,
            "verified_candidate_source_count": 12,
            "verified_native_role_count": 5,
            "verified_match_repr_checks": report["verified_match_repr_checks"],
            "standard_pickle_checks": report["standard_pickle_checks"],
            "standard_pickle_failure_count": report["standard_pickle_failure_count"],
            "completed_native_owner_worker_count": report[
                "completed_native_owner_worker_count"
            ],
            "actual_native_owner_worker_failure": report[
                "actual_native_owner_worker_failure"
            ],
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }
        sys.stdout.buffer.write(core.canonical(result) + b"\n")
        return int(not report["passed"])
    except (source_v6.AuditV6Error, OSError, RuntimeError, TypeError,
            ValueError, KeyError, UnicodeError, subprocess.SubprocessError) as error:
        sys.stdout.buffer.write(core.canonical({
            "schema": SCHEMA, "status": "FAIL", "result": "FAIL",
            "passed": False, "error_type": type(error).__name__,
            "error": str(error), "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }) + b"\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
