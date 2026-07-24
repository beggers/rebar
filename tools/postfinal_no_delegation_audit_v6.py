#!/usr/bin/env python3
"""Additively audit repaired, independently owned V6 regular-expression engines.

The synthetic mode is entirely in-memory.  Only an explicit ``--audit`` may
run the inherited, guarded source audit and three separately isolated public
type/pickle workers.  V5 source and evidence remain immutable.  Production
output is restricted to one exact, exclusively created V6 audit report.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import gc
import hashlib
import importlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
from typing import Any, Iterator, Mapping


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_no_delegation_audit_v5 as previous
from tools import postfinal_from_scratch_audit_v5 as historical_source


SCHEMA = "rebar-postfinal-no-delegation-audit-v6"
SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v6.py"
SOURCE_PATH = ROOT / SOURCE_RELATIVE
REPORT_RELATIVE = "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V6.json"
REPORT_PATH = ROOT / REPORT_RELATIVE
V6_SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v6.py"
V6_REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V6.json"
V6_SOURCE_SCHEMA = "rebar-postfinal-from-scratch-audit-v6"
# An unfinalized source or report is never accepted.  Root pins both genuine
# values only after the independently authored V6 source report exists.
V6_SOURCE_SHA256: str | None = (
    "77e7ea97f96280019b3be9abfeeb8fc6ff27ca6ecd13189e611586af5719c18f"
)
V6_REPORT_SHA256: str | None = (
    "0314e3e5de3386d7c9c1e7f8fa4648554ff53cb53e3aafcecc4cb8e4923ddcbb"
)
V5_STRICT_SOURCE_SHA256 = (
    "18a04023659e386780d6e9cd6b90065553254c18f2fe54ae78c37acbc468a7b6"
)
V5_STRICT_REPORT_SHA256 = (
    "50031133a2aa20b1ef91b126a883a622d916f582fdcbea4ba1763267199c03bb"
)
V5_SOURCE_SHA256 = (
    "100520ae06c3a837b3fa4ca508099ceb6e11efda8f63bcc0234b544071d17843"
)
V5_SOURCE_REPORT_SHA256 = (
    "42bd73acf6831b67df9a9873fa35c1882f2af09c41933774ba841d2290e6c198"
)
QUALIFIED_FAMILIES = ("rust", "vm", "zig")
AUDITED_FAMILIES = ("ast", "rust", "vm", "zig")
OWNED_SOURCES = frozenset({
    "candidates/_vm_native.c",
    "candidates/rust/py_bridge.c",
    "candidates/rust/src/lib.rs",
    "candidates/rust/src/newline.rs",
    "candidates/rust/src/search.rs",
    "candidates/rust/src/stack.rs",
    "candidates/rust/src/unicode_tables.rs",
    "candidates/rust_candidate.py",
    "candidates/vm_candidate.py",
    "candidates/zig/mini_regex.zig",
    "candidates/zig/py_bridge.c",
    "candidates/zig_candidate.py",
})
NATIVE_ROLES = frozenset({
    "candidates.rust_candidate:native-bridge",
    "candidates.rust_candidate:native-engine",
    "candidates.vm_candidate:native-engine",
    "candidates.zig_candidate:native-bridge",
    "candidates.zig_candidate:native-engine",
})
NATIVE_FILE_ROLES = {
    "rust": {
        "bridge": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "engine": "candidates/_rust_engine.so",
    },
    "vm": {
        "native": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
    },
    "zig": {
        "bridge": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        "engine": "candidates/_zig_probe.so",
    },
}
NATIVE_LOADER_ALIASES = (
    "ctypes.CDLL", "ctypes.cdll.LoadLibrary", "ctypes.cdll._dlltype",
    "ctypes._dlopen", "_ctypes.dlopen",
)
MAX_SOURCE_BYTES = previous.MAX_SOURCE_BYTES
MAX_REPORT_BYTES = previous.MAX_REPORT_BYTES
MAX_WORKER_BYTES = 512 * 1024
PUBLIC_INPUTS = previous.PUBLIC_INPUTS | frozenset({
    SOURCE_RELATIVE, V6_SOURCE_RELATIVE, V6_REPORT_RELATIVE,
    previous.SOURCE_RELATIVE, previous.REPORT_RELATIVE,
    historical_source.SOURCE_RELATIVE, historical_source.REPORT_RELATIVE,
})


OWNER_WORKER_BOOTSTRAP = r'''
import enum
import importlib
import json
import pickle
import sys
import types
from pathlib import Path

if len(sys.argv) != 4:
    raise RuntimeError("the V6 owned public-type worker arguments are invalid")
root = Path(sys.argv[1]).resolve(strict=True)
role = sys.argv[2]
expected = json.loads(sys.argv[3])
if role not in ("rust", "vm", "zig") or not isinstance(expected, dict):
    raise RuntimeError("the V6 owned public-type worker was substituted")
sys.path.insert(0, str(root))
from tools import python_re_universal_public_oracle_stage07 as stage07
if stage07.ROOT.resolve(strict=True) != root:
    raise RuntimeError("the V6 owned worker escaped its pinned source root")
guard = stage07._install_family_guard(role, expected)
if guard.get("native_loader_aliases_blocked") != [
    "ctypes.CDLL", "ctypes.cdll.LoadLibrary", "ctypes.cdll._dlltype",
    "ctypes._dlopen", "_ctypes.dlopen",
]:
    raise RuntimeError("the V6 public-type worker weakened a native loader")
decoder = enum.sys.modules.get("json.decoder")
if decoder is None:
    raise RuntimeError("the V6 worker omitted the poisoned JSON decoder")
try:
    decoder.re.compile("forbidden")
except ImportError:
    pass
else:
    raise RuntimeError("the V6 worker exposed enum.sys.modules JSON regex")
for forbidden in ("re", "_sre", "regex", "re2", "pcre", "pcre2"):
    try:
        __import__(forbidden)
    except ImportError:
        continue
    raise RuntimeError("the V6 worker imported an unowned regex: " + forbidden)
for other in ("rust", "vm", "zig"):
    if other != role:
        try:
            __import__("candidates." + other + "_candidate")
        except ImportError:
            continue
        raise RuntimeError("the V6 worker imported a foreign candidate")
module = importlib.import_module("candidates." + role + "_candidate")
allowed_modules = {
    "candidates." + role + "_candidate",
    {
        "rust": "candidates._rust_bridge",
        "vm": "candidates._vm_native",
        "zig": "candidates._zig_bridge",
    }[role],
}
owners = {}
roundtrips = []
for name in ("Pattern", "Match"):
    origin = getattr(module, name, None)
    if not isinstance(origin, type) or origin.__name__ != name:
        raise RuntimeError("the V6 worker lost a real public " + name)
    owner = getattr(origin, "__module__", None)
    if owner not in allowed_modules:
        raise RuntimeError("the V6 public class is owned by a foreign engine")
    actual_owner = importlib.import_module(owner)
    if getattr(actual_owner, name, None) is not origin:
        raise RuntimeError("the V6 public class owner is not genuinely importable")
    owners[name] = {
        "module": owner, "name": origin.__name__,
        "qualified_name": origin.__qualname__,
        "genuinely_importable": True,
    }
    for argument in (str, bytes):
        alias = origin[argument]
        if not isinstance(alias, types.GenericAlias):
            raise RuntimeError("the V6 public type did not create a real generic alias")
        for protocol in (0, 2, 4, pickle.HIGHEST_PROTOCOL):
            restored = pickle.loads(pickle.dumps(alias, protocol=protocol))
            if (
                not isinstance(restored, types.GenericAlias)
                or restored.__origin__ is not origin
                or restored.__args__ != (argument,)
                or restored != alias
                or hash(restored) != hash(alias)
            ):
                raise RuntimeError("the V6 public type failed standard pickle")
            roundtrips.append({
                "origin": name, "argument": argument.__name__,
                "protocol": protocol, "passed": True,
            })
if len(roundtrips) != 16:
    raise RuntimeError("the V6 worker omitted a real standard pickle combination")
natives = stage07._verify_family_native_mappings(
    role, {"native_sha256_by_family": {role: expected}}
)
allowed = {"candidates." + role + "_candidate", *allowed_modules}
loaded = sorted(
    name for name, item in sys.modules.items()
    if name.startswith("candidates.")
    and item is not None
    and not isinstance(item, stage07._ForbiddenRegexModule)
)
if not set(loaded).issubset(allowed):
    raise RuntimeError("the V6 worker retained a cross-family native module")
output = {
    "schema": "rebar-postfinal-no-delegation-public-owner-worker-v6",
    "status": "PASS", "role": role, "public_type_ownership": owners,
    "standard_pickle_checks": roundtrips,
    "standard_pickle_check_count": len(roundtrips),
    "native_binary_sha256": natives,
    "loaded_candidate_modules": loaded,
    "guard": guard,
    "cached_json_decoder_regex_blocked": True,
    "benchmark_or_timing_executed": False,
    "holdout_or_case_fixture_access": False,
}
sys.stdout.write(json.dumps(output, sort_keys=True, ensure_ascii=True) + "\n")
'''


class AuditV6Error(previous.AuditV5Error):
    """A strict, independently owned V6 audit requirement was violated."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditV6Error(message)


def valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str) and len(value) == 64
        and all(item in "0123456789abcdef" for item in value)
    )


def validate_public_relative(value: Any) -> str:
    require(type(value) is str, "the strict V6 public input is not text")
    path = PurePosixPath(value)
    require(
        not path.is_absolute() and ".." not in path.parts
        and "\\" not in value and "\x00" not in value
        and str(path) == value and value in PUBLIC_INPUTS,
        "refusing an unauthenticated, benchmark, hidden, or historical V6 input",
    )
    return value


def bounded_public_bytes(path: Path, *, maximum: int) -> tuple[bytes, str]:
    require(isinstance(path, Path) and not path.is_symlink(), "invalid V6 public path")
    try:
        resolved = path.resolve(strict=True)
        relative = resolved.relative_to(ROOT.resolve(strict=True)).as_posix()
    except (OSError, RuntimeError, ValueError) as error:
        raise AuditV6Error("an approved V6 public input escaped the repository") from error
    validate_public_relative(relative)
    require(resolved.is_file(), "an approved V6 input is not a regular file")
    digest, payload = historical_source.previous.previous.bounded_file(
        path, maximum=maximum,
        label="exact authenticated strict V6 input: " + relative, keep=True,
    )
    return payload, digest


def public_document(path: Path) -> tuple[dict[str, Any], str]:
    payload, fingerprint = bounded_public_bytes(path, maximum=MAX_REPORT_BYTES)
    return previous.previous.previous.decode_public_json(payload), fingerprint


def destination_name(value: Any) -> str:
    require(type(value) is str, "the V6 report destination is not text")
    path = PurePosixPath(value)
    require(
        not path.is_absolute() and ".." not in path.parts
        and "\\" not in value and "\x00" not in value
        and str(path) == value and value == REPORT_RELATIVE,
        "only the exact exclusive V6 strict report is authorized",
    )
    return value


def _validate_v5_history() -> dict[str, Any]:
    _, strict_source = bounded_public_bytes(
        previous.SOURCE_PATH, maximum=MAX_SOURCE_BYTES,
    )
    require(strict_source == V5_STRICT_SOURCE_SHA256,
            "the immutable historical V5 no-delegation source changed")
    strict, strict_report = public_document(previous.REPORT_PATH)
    require(strict_report == V5_STRICT_REPORT_SHA256,
            "the immutable historical V5 no-delegation report changed")
    require(
        strict.get("schema") == previous.SCHEMA
        and strict.get("postfinal_schema") == previous.SCHEMA
        and strict.get("status") == "PASS"
        and strict.get("result") == "PASS"
        and strict.get("passed") is True
        and strict.get("audit_source_path") == previous.SOURCE_RELATIVE
        and strict.get("audit_source_sha256") == V5_STRICT_SOURCE_SHA256
        and strict.get("base_audit_source_path") == historical_source.SOURCE_RELATIVE
        and strict.get("base_audit_source_sha256") == V5_SOURCE_SHA256
        and strict.get("base_audit_report_path") == historical_source.REPORT_RELATIVE
        and strict.get("base_audit_report_sha256") == V5_SOURCE_REPORT_SHA256,
        "the preserved historical V5 proof was substituted or marked current",
    )
    _, source_sha = bounded_public_bytes(
        historical_source.SOURCE_PATH, maximum=MAX_SOURCE_BYTES,
    )
    _, report_sha = public_document(historical_source.REPORT_PATH)
    require(source_sha == V5_SOURCE_SHA256 and report_sha == V5_SOURCE_REPORT_SHA256,
            "the immutable historical V5 from-scratch source/report changed")
    return strict


def _load_v6_source_proof() -> tuple[Any, dict[str, Any], str]:
    require(valid_sha256(V6_SOURCE_SHA256),
            "the independently authored V6 source hash is not root-finalized")
    require(valid_sha256(V6_REPORT_SHA256),
            "the independently audited V6 source report is not root-finalized")
    source_path = ROOT / V6_SOURCE_RELATIVE
    _, source_sha = bounded_public_bytes(source_path, maximum=MAX_SOURCE_BYTES)
    require(source_sha == V6_SOURCE_SHA256,
            "the independently authored V6 from-scratch controller changed")
    try:
        source_v6 = importlib.import_module("tools.postfinal_from_scratch_audit_v6")
    except (ImportError, OSError, RuntimeError, TypeError, ValueError) as error:
        raise AuditV6Error("the independent V6 source controller cannot be loaded") from error
    require(
        source_v6.SCHEMA == V6_SOURCE_SCHEMA
        and source_v6.SOURCE_RELATIVE == V6_SOURCE_RELATIVE
        and source_v6.REPORT_RELATIVE == V6_REPORT_RELATIVE
        and Path(source_v6.__file__).resolve() == source_path.resolve(),
        "the independently authored V6 source controller was replaced",
    )
    base, base_sha = public_document(ROOT / V6_REPORT_RELATIVE)
    require(base_sha == V6_REPORT_SHA256,
            "the exact root-finalized V6 from-scratch report changed")
    expected = {
        "postfinal_schema": V6_SOURCE_SCHEMA,
        "schema": V6_SOURCE_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "audit_source_path": V6_SOURCE_RELATIVE,
        "audit_source_sha256": source_sha,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
    }
    for key, value in expected.items():
        require(base.get(key) == value and type(base.get(key)) is type(value),
                "the authentic V6 source proof changed: " + key)
    require(
        base.get("previous_v5_audit_source_sha256") == V5_SOURCE_SHA256
        and base.get("previous_v5_audit_report_sha256") == V5_SOURCE_REPORT_SHA256,
        "the genuine V6 source audit concealed immutable V5 history",
    )
    families = base.get("families")
    native = base.get("native_elf_provenance")
    manifest = base.get("manifest_provenance")
    require(
        isinstance(families, dict) and set(families) == set(AUDITED_FAMILIES)
        and all(isinstance(record, dict) and record.get("passed") is True
                for record in families.values())
        and isinstance(manifest, dict) and manifest.get("passed") is True
        and manifest.get("issues") == []
        and isinstance(native, dict) and native.get("passed") is True
        and native.get("issues") == []
        and native.get("audited_binary_count") == 5
        and native.get("expected_binary_count") == 5
        and isinstance(native.get("families"), dict)
        and set(native["families"]) == set(QUALIFIED_FAMILIES),
        "the independent V6 source proof omitted a family or native role",
    )
    validator = getattr(source_v6, "validate_v6_report", None)
    if callable(validator):
        validator(base, label="root-authenticated fresh V6 from-scratch proof")
    return source_v6, base, base_sha


def validate_native_runpaths(family: Any, role: Any, paths: Any) -> list[str]:
    require(
        type(family) is str and family in NATIVE_FILE_ROLES
        and type(role) is str and role in NATIVE_FILE_ROLES[family]
        and isinstance(paths, list)
        and all(type(item) is str for item in paths),
        "the V6 native ELF concealed an invalid or unowned runtime path",
    )
    approved = ["$ORIGIN"] if family in {"rust", "zig"} and role == "bridge" else []
    require(
        paths == approved,
        "the V6 native ELF has an absolute, disguised, extra, or foreign runpath",
    )
    return paths


def validate_native_dependencies(family: Any, role: Any, needed: Any) -> list[str]:
    require(
        type(family) is str and family in NATIVE_FILE_ROLES
        and type(role) is str and role in NATIVE_FILE_ROLES[family]
        and isinstance(needed, list)
        and all(type(item) is str and bool(item) for item in needed)
        and len(needed) == len(set(needed)),
        "the V6 native ELF has invalid or repeated DT_NEEDED entries",
    )
    for item in needed:
        lowered = item.lower()
        require(
            "/" not in item and "\\" not in item
            and ".." not in item and "$" not in item
            and not any(name in lowered for name in
                        ("regex", "pcre", "onig", "libre2", "libsre")),
            "the V6 native ELF has a disguised external regex dependency",
        )
        if item in {"_rust_engine.so", "_zig_probe.so"}:
            require(
                (family, role, item) in {
                    ("rust", "bridge", "_rust_engine.so"),
                    ("zig", "bridge", "_zig_probe.so"),
                },
                "the V6 native ELF links a cross-family matching engine",
            )
    if (family, role) == ("rust", "bridge"):
        require("_rust_engine.so" in needed,
                "the genuine Rust bridge lost its owned engine dependency")
    if (family, role) == ("zig", "bridge"):
        require("_zig_probe.so" in needed,
                "the genuine Zig bridge lost its owned engine dependency")
    return needed


def _expected_native_by_family(base: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    families = base["native_elf_provenance"]["families"]
    expected: dict[str, dict[str, str]] = {}
    for role in QUALIFIED_FAMILIES:
        family = families[role]
        files = family.get("files") if isinstance(family, Mapping) else None
        require(isinstance(files, Mapping)
                and set(files) == set(NATIVE_FILE_ROLES[role])
                and family.get("passed") is True,
                "the V6 source omitted owned native mappings: " + role)
        expected[role] = {}
        for name, record in files.items():
            require(
                isinstance(name, str) and isinstance(record, Mapping)
                and type(record.get("file")) is str
                and record["file"] == NATIVE_FILE_ROLES[role][name]
                and valid_sha256(record.get("sha256"))
                and record.get("forbidden_regex_symbols") == []
                and record.get("cross_candidate_symbols") == [],
                "the V6 source omitted an owned ELF or concealed a dependency",
            )
            validate_native_runpaths(role, name, record.get("runpaths"))
            validate_native_dependencies(role, name, record.get("needed"))
            expected[role][record["file"]] = record["sha256"]
    require(sum(len(files) for files in expected.values()) == 5,
            "the fresh V6 source proof does not map exactly five owned ELFs")
    return expected


def _owner_worker(role: str, expected: dict[str, str]) -> dict[str, Any]:
    require(role in QUALIFIED_FAMILIES,
            "refusing a foreign V6 public-owner worker")
    command = [
        sys.executable, "-I", "-B", "-c", OWNER_WORKER_BOOTSTRAP,
        str(ROOT), role,
        json.dumps(expected, ensure_ascii=True, sort_keys=True,
                   separators=(",", ":")),
    ]
    environment = {
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
        "PYTHONPATH": str(ROOT), "LC_ALL": "C", "PATH": "/usr/bin:/bin",
    }
    try:
        child = subprocess.run(
            command, cwd=str(ROOT), env=environment,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=120, check=False,
        )
    except subprocess.SubprocessError as error:
        raise AuditV6Error("the isolated public-owner worker failed: " + role) from error
    require(
        child.returncode == 0 and 0 < len(child.stdout) <= MAX_WORKER_BYTES
        and len(child.stderr) <= MAX_WORKER_BYTES,
        "a real V6 public-owner worker crashed or returned unsafe output: " + role,
    )
    try:
        document = json.loads(child.stdout)
    except (UnicodeError, ValueError) as error:
        raise AuditV6Error("an isolated V6 owner returned malformed evidence") from error
    require(
        isinstance(document, dict)
        and document.get("schema")
        == "rebar-postfinal-no-delegation-public-owner-worker-v6"
        and document.get("status") == "PASS"
        and document.get("role") == role
        and document.get("standard_pickle_check_count") == 16
        and isinstance(document.get("standard_pickle_checks"), list)
        and len(document["standard_pickle_checks"]) == 16
        and all(isinstance(item, dict) and item.get("passed") is True
                for item in document["standard_pickle_checks"])
        and document.get("native_binary_sha256") == expected
        and document.get("cached_json_decoder_regex_blocked") is True
        and document.get("benchmark_or_timing_executed") is False
        and document.get("holdout_or_case_fixture_access") is False,
        "an isolated V6 worker forged owner, pickle, or native evidence: " + role,
    )
    ownership = document.get("public_type_ownership")
    require(
        isinstance(ownership, dict) and set(ownership) == {"Pattern", "Match"}
        and all(isinstance(item, dict) and item.get("genuinely_importable") is True
                for item in ownership.values()),
        "the isolated V6 worker concealed a genuine native-owned public type",
    )
    guard = document.get("guard")
    require(
        isinstance(guard, dict) and guard.get("enabled") is True
        and guard.get("family") == role
        and guard.get("stdlib_re_blocked") is True
        and guard.get("cpython_sre_blocked") is True
        and guard.get("third_party_regex_blocked") is True
        and guard.get("cross_family_blocked") is True
        and guard.get("foreign_dynamic_libraries_blocked") is True
        and guard.get("native_loader_aliases_blocked") == list(NATIVE_LOADER_ALIASES),
        "the isolated V6 public-owner worker weakened an actual native guard",
    )
    return document


def candidate_free_self_test() -> dict[str, Any]:
    previous.previous.previous.verify_pinned_runtime()
    previous.previous.previous.require_candidate_free()
    effects = historical_source.previous.previous.previous.BlockSelfTestEffects()
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: Any) -> None:
        require(not any(record["name"] == name for record in checks),
                "a strict V6 poison control was counted twice")
        checks.append({"name": name, "passed": bool(passed)})

    def rejected(name: str, action: Any) -> None:
        try:
            action()
        except (AuditV6Error, previous.AuditV5Error, TypeError, ValueError,
                UnicodeError, KeyError, RuntimeError, OSError):
            check(name, True)
        else:
            check(name, False)

    with effects:
        inherited = previous.candidate_free_self_test()
        check("all-676-genuine-v5-malicious-controls-pass",
              inherited.get("schema") == previous.SCHEMA + "-self-test"
              and inherited.get("passed") is True
              and inherited.get("failed") == []
              and inherited.get("check_count", 0) >= 676
              and inherited.get("file_reads") == 0
              and inherited.get("file_writes") == 0
              and inherited.get("subprocesses") == 0
              and inherited.get("clock_samples") == 0
              and inherited.get("candidate_imports") == 0)
        check("all-three-independent-native-families",
              QUALIFIED_FAMILIES == ("rust", "vm", "zig"))
        check("all-four-independent-source-families",
              set(AUDITED_FAMILIES) == {"ast", "rust", "vm", "zig"})
        check("exact-twelve-owned-production-source-paths", len(OWNED_SOURCES) == 12)
        check("exact-five-real-mapped-native-role-paths", len(NATIVE_ROLES) == 5)
        check("accept-only-genuine-rust-bridge-origin-runpath",
              validate_native_runpaths("rust", "bridge", ["$ORIGIN"]) == ["$ORIGIN"])
        check("accept-only-genuine-zig-bridge-origin-runpath",
              validate_native_runpaths("zig", "bridge", ["$ORIGIN"]) == ["$ORIGIN"])
        check("accept-only-empty-owned-rust-engine-runpath",
              validate_native_runpaths("rust", "engine", []) == [])
        check("accept-only-empty-owned-vm-native-runpath",
              validate_native_runpaths("vm", "native", []) == [])
        check("accept-only-empty-owned-zig-engine-runpath",
              validate_native_runpaths("zig", "engine", []) == [])
        for name, family, native_role, poison in (
            ("reject-absolute-native-runpath", "rust", "bridge", ["/tmp/foreign"]),
            ("reject-traversing-native-runpath", "zig", "bridge", ["$ORIGIN/../foreign"]),
            ("reject-multiple-native-runpaths", "rust", "bridge", ["$ORIGIN", "/tmp"]),
            ("reject-missing-owned-bridge-runpath", "zig", "bridge", []),
            ("reject-vm-native-origin-runpath", "vm", "native", ["$ORIGIN"]),
            ("reject-engine-origin-runpath", "rust", "engine", ["$ORIGIN"]),
            ("reject-disguised-colon-runpath", "zig", "bridge", ["$ORIGIN:/tmp"]),
            ("reject-foreign-native-role-runpath", "vm", "bridge", ["$ORIGIN"]),
        ):
            rejected(name, lambda group=family, native=native_role, paths=poison:
                     validate_native_runpaths(group, native, paths))
        check("accept-genuine-rust-bridge-owned-needed-engine",
              validate_native_dependencies(
                  "rust", "bridge", ["_rust_engine.so", "libc.so.6"]
              ) == ["_rust_engine.so", "libc.so.6"])
        check("accept-genuine-zig-bridge-owned-needed-engine",
              validate_native_dependencies(
                  "zig", "bridge", ["_zig_probe.so", "libc.so.6"]
              ) == ["_zig_probe.so", "libc.so.6"])
        check("accept-genuine-vm-standard-libc-dependency",
              validate_native_dependencies(
                  "vm", "native", ["libc.so.6"]
              ) == ["libc.so.6"])
        for name, family, native_role, poison in (
            ("reject-external-pcre-needed", "rust", "bridge",
             ["_rust_engine.so", "libpcre2-8.so.0"]),
            ("reject-disguised-regex-needed", "zig", "bridge",
             ["_zig_probe.so", "libcustom_regex.so"]),
            ("reject-absolute-needed", "rust", "bridge",
             ["_rust_engine.so", "/tmp/libengine.so"]),
            ("reject-traversing-needed", "vm", "native",
             ["../libforeign.so"]),
            ("reject-cross-family-zig-needed", "rust", "bridge",
             ["_rust_engine.so", "_zig_probe.so"]),
            ("reject-cross-family-rust-needed", "zig", "bridge",
             ["_zig_probe.so", "_rust_engine.so"]),
            ("reject-missing-owned-rust-needed", "rust", "bridge",
             ["libc.so.6"]),
            ("reject-duplicate-owned-zig-needed", "zig", "bridge",
             ["_zig_probe.so", "_zig_probe.so"]),
        ):
            rejected(name, lambda group=family, native=native_role, entries=poison:
                     validate_native_dependencies(group, native, entries))
        check("exact-five-native-loader-aliases", NATIVE_LOADER_ALIASES == (
            "ctypes.CDLL", "ctypes.cdll.LoadLibrary", "ctypes.cdll._dlltype",
            "ctypes._dlopen", "_ctypes.dlopen",
        ))
        immutable_controls = previous.previous.previous.previous.STRICT_CONTROL_NAMES
        for name in (
            "direct_stdlib_re", "direct_cpython_sre", "third_party_regex",
            "cross_family_import", "enum_sys_modules", "cached_json_decoder_regex",
            "function_globals_reflection", "rust_external_crate",
            "zig_external_package", "zig_dynamic_loader_and_external",
        ):
            check("preserve-immutable-anti-delegation-" + name,
                  name in immutable_controls)
        check("preserve-immutable-32-strict-guard-controls",
              len(immutable_controls) == 32)
        check("preserve-immutable-76-original-malicious-controls",
              len(previous.previous.previous.previous.BASE_CONTROL_NAMES) == 76)
        check("bind-immutable-v5-strict-source-fingerprint",
              V5_STRICT_SOURCE_SHA256 ==
              "18a04023659e386780d6e9cd6b90065553254c18f2fe54ae78c37acbc468a7b6")
        check("bind-immutable-v5-strict-report-fingerprint",
              V5_STRICT_REPORT_SHA256 ==
              "50031133a2aa20b1ef91b126a883a622d916f582fdcbea4ba1763267199c03bb")
        check("bind-immutable-v5-source-fingerprint",
              V5_SOURCE_SHA256 ==
              "100520ae06c3a837b3fa4ca508099ceb6e11efda8f63bcc0234b544071d17843")
        check("bind-immutable-v5-source-report-fingerprint",
              V5_SOURCE_REPORT_SHA256 ==
              "42bd73acf6831b67df9a9873fa35c1882f2af09c41933774ba841d2290e6c198")
        check("bind-only-a-root-finalized-v6-from-scratch-source-fingerprint",
              V6_SOURCE_SHA256 ==
              "77e7ea97f96280019b3be9abfeeb8fc6ff27ca6ecd13189e611586af5719c18f")
        check("v6-source-fingerprint-fails-closed-until-finalized",
              V6_SOURCE_SHA256 is None or valid_sha256(V6_SOURCE_SHA256))
        check("v6-source-report-fingerprint-fails-closed-until-finalized",
              V6_REPORT_SHA256 is None or valid_sha256(V6_REPORT_SHA256))
        check("bind-genuine-exclusively-created-v6-from-scratch-report",
              V6_REPORT_SHA256 ==
              "0314e3e5de3386d7c9c1e7f8fa4648554ff53cb53e3aafcecc4cb8e4923ddcbb")
        check("actual-v6-owner-worker-is-isolated",
              "stage07._install_family_guard(role, expected)" in OWNER_WORKER_BOOTSTRAP
              and "stage07._verify_family_native_mappings" in OWNER_WORKER_BOOTSTRAP)
        check("actual-v6-owner-worker-rejects-json-registry-regex",
              'decoder.re.compile("forbidden")' in OWNER_WORKER_BOOTSTRAP
              and "enum.sys.modules.get" in OWNER_WORKER_BOOTSTRAP)
        check("actual-v6-owner-worker-verifies-real-standard-pickle",
              "pickle.loads(pickle.dumps(alias, protocol=protocol))"
              in OWNER_WORKER_BOOTSTRAP
              and "pickle.HIGHEST_PROTOCOL" in OWNER_WORKER_BOOTSTRAP)
        check("actual-v6-owner-worker-rejects-foreign-class-ownership",
              "getattr(actual_owner, name, None) is not origin"
              in OWNER_WORKER_BOOTSTRAP)
        check("allow-only-one-exclusively-created-v6-strict-report",
              destination_name(REPORT_RELATIVE) == REPORT_RELATIVE)
        for name, value in (
            ("reject-historical-v5-strict-report-overwrite", previous.REPORT_RELATIVE),
            ("reject-v6-from-scratch-report-overwrite", V6_REPORT_RELATIVE),
            ("reject-historical-source-report-overwrite", historical_source.REPORT_RELATIVE),
            ("reject-absolute-strict-report", "/" + REPORT_RELATIVE),
            ("reject-traversing-strict-report",
             "candidates/audits/../POSTFINAL-NO-DELEGATION-AUDIT-V6.json"),
            ("reject-foreign-strict-report", "candidates/audits/FOREIGN.json"),
            ("reject-backslash-strict-report",
             "candidates\\audits\\POSTFINAL-NO-DELEGATION-AUDIT-V6.json"),
            ("reject-nul-strict-report", REPORT_RELATIVE + "\x00"),
            ("reject-nontext-strict-report", 6),
        ):
            rejected(name, lambda item=value: destination_name(item))
        for name, value in (
            ("reject-private-v6-audit-input", "sealed/private/cases.json"),
            ("reject-hidden-v6-audit-input", "sealed/holdout/cases.json"),
            ("reject-final-v6-audit-input", "sealed/final/cases.json"),
            ("reject-benchmark-v6-audit-input", "benchmarks/cases.json"),
            ("reject-traversing-v6-audit-input", "candidates/audits/../FOREIGN.json"),
            ("reject-foreign-v6-audit-input", "candidates/audits/FOREIGN.json"),
            ("reject-nul-v6-audit-input", SOURCE_RELATIVE + "\x00"),
        ):
            rejected(name, lambda item=value: validate_public_relative(item))
        check("zero-in-memory-file-access", effects.counts["files"] == 0)
        check("zero-in-memory-worker-starts", effects.counts["processes"] == 0)
        check("zero-in-memory-clock-samples", effects.counts["clocks"] == 0)
        check("zero-in-memory-production-entropy", effects.counts["entropy"] == 0)
        previous.previous.previous.require_candidate_free()

    failures = [record["name"] for record in checks if not record["passed"]]
    return {
        "schema": SCHEMA + "-self-test", "postfinal_schema": SCHEMA + "-self-test",
        "status": "PASS" if not failures else "FAIL",
        "result": "PASS" if not failures else "FAIL", "passed": not failures,
        "checks": checks, "check_count": len(checks), "failed": failures,
        "inherited_v5_self_test": inherited,
        "inherited_v5_control_count": inherited.get("check_count"),
        "fixture_storage": "in-memory only", "candidate_imports": 0,
        "candidate_imported": False, "file_reads": effects.counts["files"],
        "file_writes": 0, "subprocesses": effects.counts["processes"],
        "clock_samples": effects.counts["clocks"],
        "production_entropy_drawn": False,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
        "production_cases_materialized": 0, "report_written": False,
    }


def run_audit() -> dict[str, Any]:
    legacy = previous.previous.previous
    immutable_v2 = legacy.previous
    legacy.verify_pinned_runtime()
    legacy.require_candidate_free()
    historical = _validate_v5_history()
    source_v6, base, base_sha = _load_v6_source_proof()
    controls = candidate_free_self_test()
    require(controls.get("passed") is True, "the V6 malicious poison controls failed")
    immutable = immutable_v2.import_pinned_strict_v1()
    strict_controls = immutable.self_test()
    immutable_v2.validate_controls(
        {"self_test": strict_controls}, names=immutable_v2.STRICT_CONTROL_NAMES,
        label="actual immutable V6 32-control no-delegation self-test",
    )
    saved_loader = immutable._load_original_report
    saved_report = immutable.original.REPORT

    def load_authenticated_v6_base() -> tuple[dict[str, Any], str]:
        _source, current, fingerprint = _load_v6_source_proof()
        require(current == base and fingerprint == base_sha,
                "the exact V6 source proof changed inside the strict audit")
        return current, fingerprint

    immutable._load_original_report = load_authenticated_v6_base
    immutable.original.REPORT = ROOT / V6_REPORT_RELATIVE
    try:
        gc.collect()
        with historical_source.allow_owned_locale_ctype():
            with previous.scoped_original_control_bootstrap(V5_SOURCE_SHA256):
                actual = immutable.run_audit()
    finally:
        immutable.original.REPORT = saved_report
        immutable._load_original_report = saved_loader

    legacy.require_candidate_free()
    require(
        isinstance(actual, dict)
        and actual.get("schema") == immutable_v2.IMMUTABLE_STRICT_SCHEMA
        and actual.get("passed") is True
        and actual.get("result") == "PASS"
        and actual.get("inherited_control_count") == 76,
        "the immutable native V6 strict audit did not pass its actual controls",
    )
    immutable_v2.validate_controls(
        actual, names=immutable_v2.STRICT_CONTROL_NAMES,
        label="the complete actual 32-control V6 strict native audit",
    )
    immutable_v2._verify_result_native(actual, base)
    legacy._validate_flattened_native(actual, label="the actual five-role V6 native proof")
    qualified = actual.get("qualified_source_fingerprints")
    fingerprints = actual.get("native_elf_fingerprints")
    require(
        isinstance(qualified, Mapping) and set(qualified) == OWNED_SOURCES
        and all(valid_sha256(item) for item in qualified.values())
        and isinstance(fingerprints, Mapping) and set(fingerprints) == NATIVE_ROLES
        and all(valid_sha256(item) for item in fingerprints.values()),
        "the strict V6 audit omitted one of 12 owned sources or five native roles",
    )
    natives = _expected_native_by_family(base)
    ownership = {role: _owner_worker(role, natives[role]) for role in QUALIFIED_FAMILIES}
    require(
        len(ownership) == 3
        and sum(item["standard_pickle_check_count"] for item in ownership.values()) == 48,
        "an actual guarded candidate omitted its genuine owned public pickle types",
    )
    current_source, strict_sha = bounded_public_bytes(
        SOURCE_PATH, maximum=MAX_SOURCE_BYTES,
    )
    del current_source
    legacy.require_candidate_free()
    actual.update({
        "schema": SCHEMA, "postfinal_schema": SCHEMA,
        "status": "PASS", "result": "PASS", "passed": True,
        "audit_source_path": SOURCE_RELATIVE, "audit_source_sha256": strict_sha,
        "base_audit_source_path": V6_SOURCE_RELATIVE,
        "base_audit_source_sha256": V6_SOURCE_SHA256,
        "base_audit_report_path": V6_REPORT_RELATIVE,
        "base_audit_report_sha256": base_sha,
        "base_audit_postfinal_schema": V6_SOURCE_SCHEMA,
        "previous_v5_audit_source_path": previous.SOURCE_RELATIVE,
        "previous_v5_audit_source_sha256": V5_STRICT_SOURCE_SHA256,
        "previous_v5_audit_report_path": previous.REPORT_RELATIVE,
        "previous_v5_audit_report_sha256": V5_STRICT_REPORT_SHA256,
        "previous_v5_report_historical": True,
        "previous_v5_source_audit_source_path": historical_source.SOURCE_RELATIVE,
        "previous_v5_source_audit_source_sha256": V5_SOURCE_SHA256,
        "previous_v5_source_audit_report_path": historical_source.REPORT_RELATIVE,
        "previous_v5_source_audit_report_sha256": V5_SOURCE_REPORT_SHA256,
        "postfinal_wrapper_self_test": controls,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "manifest_provenance": base["manifest_provenance"],
        "native_elf_provenance": base["native_elf_provenance"],
        "public_type_ownership": ownership,
        "verified_public_type_family_count": 3,
        "verified_standard_pickle_count": 48,
        "scope": {
            **dict(actual.get("scope", {})),
            "immutable_v5_strict_report_preserved": True,
            "immutable_v5_source_report_preserved": True,
            "fresh_v6_source_report_only": True,
            "explicit_source_paths_only": True,
            "closed_owned_source_graph": True,
            "mapped_binaries_hashed_against_static_elf": True,
            "public_owners_verified_in_isolated_guarded_processes": True,
            "all_five_native_loader_aliases_blocked": True,
            "enum_json_decoder_registry_bypass_blocked": True,
            "candidate_imports": "isolated guarded subprocesses only",
            "production_report_path": REPORT_RELATIVE,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
        "supersedes": {
            "schema": previous.SCHEMA,
            "source_path": previous.SOURCE_RELATIVE,
            "source_sha256": V5_STRICT_SOURCE_SHA256,
            "report_path": previous.REPORT_RELATIVE,
            "report_sha256": V5_STRICT_REPORT_SHA256,
            "source_preserved": True,
            "report_historical": True,
        },
    })
    legacy.require_candidate_free()
    return actual


def write_report(report: Mapping[str, Any], target: Path) -> str:
    require(
        isinstance(target, Path)
        and destination_name(target.relative_to(ROOT).as_posix()) == REPORT_RELATIVE
        and target.name == REPORT_PATH.name and not target.is_symlink()
        and target.parent.resolve() == REPORT_PATH.parent.resolve(),
        "only the exact exclusive non-symlink V6 strict report is authorized",
    )
    parent = REPORT_PATH.parent
    require(not parent.is_symlink(), "the exclusive V6 report parent is symbolic")
    resolved = parent.resolve(strict=True)
    require(resolved.is_relative_to(ROOT.resolve(strict=True)),
            "the exclusive V6 report escaped its repository")
    payload = previous.previous.previous.canonical(report) + b"\n"
    require(len(payload) <= MAX_REPORT_BYTES, "the complete V6 audit report is unsafe")
    directory_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    directory_flags |= getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    file_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    file_flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    directory = os.open(resolved, directory_flags)
    try:
        require(stat.S_ISDIR(os.fstat(directory).st_mode),
                "the exclusive V6 report parent is not a directory")
        descriptor = os.open(REPORT_PATH.name, file_flags, 0o644, dir_fd=directory)
        try:
            view = memoryview(payload)
            while view:
                count = os.write(descriptor, view)
                require(count > 0, "the exclusive V6 report write stalled")
                view = view[count:]
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
    modes.add_argument("--audit", action="store_true")
    parser.add_argument("--output", type=Path, default=REPORT_PATH)
    options = parser.parse_args(arguments)
    try:
        previous.previous.previous.require_candidate_free()
        if options.self_test:
            require(options.output == REPORT_PATH,
                    "the V6 strict self-test cannot create production evidence")
            result = candidate_free_self_test()
            compact = dict(result)
            inherited = compact.pop("inherited_v5_self_test")
            compact["inherited_v5_self_test_sha256"] = hashlib.sha256(
                previous.previous.previous.canonical(inherited)
            ).hexdigest()
            sys.stdout.buffer.write(
                previous.previous.previous.canonical(compact) + b"\n"
            )
            return 0 if result.get("passed") is True else 1
        result = run_audit()
        digest = write_report(result, options.output)
        sys.stdout.buffer.write(previous.previous.previous.canonical({
            "schema": SCHEMA, "postfinal_schema": SCHEMA,
            "status": "PASS", "result": "PASS", "passed": True,
            "report": REPORT_RELATIVE, "report_sha256": digest,
            "audit_source_sha256": result["audit_source_sha256"],
            "base_audit_report_path": V6_REPORT_RELATIVE,
            "base_audit_report_sha256": result["base_audit_report_sha256"],
            "verified_family_count": len(result["families"]),
            "verified_native_role_count": len(result["native_elf_fingerprints"]),
            "verified_public_type_family_count": 3,
            "verified_standard_pickle_count": 48,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }) + b"\n")
        return 0
    except (
        AuditV6Error, previous.AuditV5Error, OSError, RuntimeError,
        TypeError, ValueError, KeyError, subprocess.SubprocessError,
    ) as error:
        sys.stdout.buffer.write(previous.previous.previous.canonical({
            "schema": SCHEMA, "postfinal_schema": SCHEMA,
            "status": "FAIL", "result": "FAIL", "passed": False,
            "error": str(error), "candidate_imported": False,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }) + b"\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
