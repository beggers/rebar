#!/usr/bin/env python3
"""Independently audit the repaired, genuinely owned native regex engines."""

from __future__ import annotations

import sys

if __name__ == "__main__":
    import os as _v6_entry_os
    from pathlib import Path as _V6EntryPath

    _v6_entry_root = str(_V6EntryPath(__file__).resolve().parent.parent)
    _v6_entry = (
        "import sys;sys.path.insert(0,sys.argv[1]);"
        "from tools.postfinal_from_scratch_audit_v6 import main;"
        "raise SystemExit(main(sys.argv[2:]))"
    )
    _v6_entry_os.execv(
        sys.executable,
        [sys.executable, "-I", "-B", "-c", _v6_entry,
         _v6_entry_root, *sys.argv[1:]],
    )

import argparse
import gc
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import pickle
import stat
import subprocess
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_from_scratch_audit_v5 as source_v5


core = source_v5.previous.previous
original = source_v5.original
SCHEMA = "rebar-postfinal-from-scratch-audit-v6"
SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v6.py"
SOURCE_PATH = ROOT / SOURCE_RELATIVE
REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V6.json"
REPORT_PATH = ROOT / REPORT_RELATIVE
V5_SOURCE_SHA256 = "100520ae06c3a837b3fa4ca508099ceb6e11efda8f63bcc0234b544071d17843"
V5_REPORT_SHA256 = "42bd73acf6831b67df9a9873fa35c1882f2af09c41933774ba841d2290e6c198"
STRICT_V5_SOURCE_SHA256 = "18a04023659e386780d6e9cd6b90065553254c18f2fe54ae78c37acbc468a7b6"
STRICT_V5_REPORT_SHA256 = "50031133a2aa20b1ef91b126a883a622d916f582fdcbea4ba1763267199c03bb"
MAX_SOURCE_BYTES = source_v5.MAX_SOURCE_BYTES
MAX_REPORT_BYTES = source_v5.MAX_REPORT_BYTES
MAX_WORKER_BYTES = 256 * 1024
MAX_PROC_MAP_BYTES = 4 * 1024 * 1024
CORE_FAMILIES = ("rust", "vm", "zig")
NATIVE_LOADER_ALIASES = (
    "ctypes.CDLL",
    "ctypes.cdll.LoadLibrary",
    "ctypes.cdll._dlltype",
    "ctypes._dlopen",
    "_ctypes.dlopen",
)
OWNED_NATIVE_MODULES = {
    "rust": "candidates._rust_bridge",
    "vm": "candidates._vm_native",
    "zig": "candidates._zig_bridge",
}
OWNED_SOURCE_PATHS = {
    "rust": (
        "candidates/rust_candidate.py",
        "candidates/rust/py_bridge.c",
        "candidates/rust/src/lib.rs",
        "candidates/rust/src/search.rs",
        "candidates/rust/src/newline.rs",
        "candidates/rust/src/stack.rs",
        "candidates/rust/src/unicode_tables.rs",
    ),
    "vm": ("candidates/vm_candidate.py", "candidates/_vm_native.c"),
    "zig": (
        "candidates/zig_candidate.py",
        "candidates/zig/py_bridge.c",
        "candidates/zig/mini_regex.zig",
    ),
}
OWNED_NATIVE_PATHS = {
    "rust": {
        "bridge": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "engine": "candidates/_rust_engine.so",
    },
    "vm": {"native": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so"},
    "zig": {
        "bridge": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        "engine": "candidates/_zig_probe.so",
    },
}
FROZEN_PUBLIC_INPUTS = {
    "tools/postfinal_from_scratch_audit_v5.py": V5_SOURCE_SHA256,
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json": V5_REPORT_SHA256,
    "tools/postfinal_no_delegation_audit_v5.py": STRICT_V5_SOURCE_SHA256,
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json": STRICT_V5_REPORT_SHA256,
    "tools/python_re_universal_public_oracle_stage10.py":
        "a24cfa72f44931c76b425ea3eb6568ff67dc87236c8d5fe930837a14c2f58f08",
    "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V10.md":
        "c0194ee2ef1e32bd64dc646e2f395bee6036b9c053e31d95ebb3cfbc52b0a543",
    "oracle/cpython-3.14.6/evidence/public-contract-v10-self-oracle.json":
        "5207ca3829216b9482f0b5a2928b339261e2c51d673cce7d80da0f4f4622a8f9",
    "candidates/evidence/python-re-universal-public-oracle-v10-all.json":
        "0af512f940ce7c28e50c1977794e3fbb8a2c33206e77dd2379d4fa12b391fec7",
    "tools/python_re_generic_alias_public_oracle_stage11.py":
        "2d8b0417e837d830c3b01495657305536a9d14e289aeb61d503278f5944b16f3",
    "oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V11.md":
        "b9d93b2ee18d33ad3e474c7e7d9bf7f94cd612526e39982fec0c2a0d0a4d096e",
    "oracle/cpython-3.14.6/evidence/public-generic-alias-v11-self-oracle.json":
        "31245bf7864ae76e46e676a3a35d0fae399d1f6446af482db9f7aa47b5426f8a",
    "candidates/evidence/python-re-generic-alias-public-oracle-v11-rust-failures.json":
        "5d0fce04b95a6d15e4aaff28d2c59337136660a248616672928f7aa85f7efa36",
}


class AuditV6Error(source_v5.AuditV5Error):
    """A current source, owned native type, or historical proof is unsafe."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditV6Error(message)


def _canonical_relative(value: Any, allowed: Mapping[str, Any]) -> str:
    require(type(value) is str, "an approved V6 path must be text")
    path = PurePosixPath(value)
    require(
        not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in value
        and "\x00" not in value
        and str(path) == value
        and value in allowed,
        "refusing an unapproved, private, traversing, or substituted V6 path",
    )
    return value


def destination_name(value: Any) -> str:
    return _canonical_relative(value, {REPORT_RELATIVE: True})


def _read_frozen(relative: str) -> tuple[bytes, str]:
    relative = _canonical_relative(relative, FROZEN_PUBLIC_INPUTS)
    path = ROOT / relative
    require(not path.is_symlink(), "an immutable V6 public input is a symlink")
    maximum = MAX_REPORT_BYTES if relative.endswith(".json") else MAX_SOURCE_BYTES
    observed, payload = core.bounded_file(
        path, maximum=maximum, label="exact preserved V6 public input: " + relative,
        keep=True,
    )
    require(
        observed == FROZEN_PUBLIC_INPUTS[relative],
        "an immutable V5 or public correctness artifact changed: " + relative,
    )
    require(type(payload) is bytes, "a bounded public input returned no actual bytes")
    return payload, observed


def _validate_fresh_graph(document: Any) -> dict[str, Any]:
    require(isinstance(document, dict), "the fresh original source audit is absent")
    families = document.get("families")
    native = document.get("native_elf_provenance")
    manifest = document.get("manifest_provenance")
    runtime = document.get("runtime_native_mapping_provenance")
    require(
        isinstance(families, dict)
        and set(families) == {"ast", *CORE_FAMILIES}
        and isinstance(native, dict)
        and native.get("passed") is True
        and native.get("audited_binary_count") == 5
        and native.get("expected_binary_count") == 5
        and isinstance(native.get("families"), dict)
        and set(native["families"]) == set(CORE_FAMILIES)
        and isinstance(manifest, dict)
        and manifest.get("passed") is True
        and manifest.get("issues") == []
        and manifest.get("python_dependencies") == []
        and manifest.get("rust_third_party_dependency_count") == 0
        and manifest.get("rust_lock_packages") == ["rebar-rust-continuation"]
        and isinstance(runtime, dict)
        and runtime.get("passed") is True,
        "the actual V6 sources, lockfile, four pipelines, or five ELF files are unsafe",
    )
    all_sources: list[str] = []
    native_fingerprints: dict[str, dict[str, str]] = {}
    for family in CORE_FAMILIES:
        candidate = families.get(family)
        require(
            isinstance(candidate, dict)
            and candidate.get("passed") is True
            and isinstance(candidate.get("owned_pipeline"), dict)
            and candidate["owned_pipeline"].get("passed") is True
            and candidate["owned_pipeline"].get("issues") == [],
            "the current from-scratch parser, compiler, or executor failed: " + family,
        )
        python_source = candidate.get("python_source")
        native_sources = candidate.get("native_sources")
        require(
            isinstance(python_source, dict)
            and python_source.get("passed") is True
            and python_source.get("issues") == []
            and python_source.get("file") == OWNED_SOURCE_PATHS[family][0]
            and core.valid_sha256(python_source.get("sha256"))
            and isinstance(native_sources, list),
            "a candidate wrapper was omitted, substituted, or delegated: " + family,
        )
        actual_sources = [python_source["file"]]
        for item in native_sources:
            require(
                isinstance(item, dict)
                and item.get("passed") is True
                and item.get("issues") == []
                and type(item.get("file")) is str
                and core.valid_sha256(item.get("sha256")),
                "a native parser, compiler, or matcher was not freshly audited: " + family,
            )
            actual_sources.append(item["file"])
        require(
            tuple(actual_sources) == OWNED_SOURCE_PATHS[family],
            "the exact current closed candidate source graph changed: " + family,
        )
        all_sources.extend(actual_sources)
        entries = native["families"][family].get("files")
        require(
            isinstance(entries, dict)
            and set(entries) == set(OWNED_NATIVE_PATHS[family]),
            "an owned ELF bridge or matching engine is missing: " + family,
        )
        native_fingerprints[family] = {}
        for role, relative in OWNED_NATIVE_PATHS[family].items():
            entry = entries[role]
            require(
                isinstance(entry, dict)
                and entry.get("file") == relative
                and core.valid_sha256(entry.get("sha256"))
                and entry.get("elf_class") == 64
                and entry.get("forbidden_regex_symbols") == []
                and entry.get("cross_candidate_symbols") == []
                and entry.get("runpaths") == (
                    ["$ORIGIN"] if family in {"rust", "zig"} and role == "bridge"
                    else []
                )
                and isinstance(entry.get("needed"), list),
                "the actual V6 ELF links an unowned matching engine: " + relative,
            )
            native_fingerprints[family][relative] = entry["sha256"]
    require(
        len(all_sources) == 12 and len(set(all_sources)) == 12,
        "the audit omitted, duplicated, or changed an owned candidate source",
    )
    return {
        "source_paths": all_sources,
        "source_count": 12,
        "native_binary_count": 5,
        "native_sha256_by_family": native_fingerprints,
    }


OWNERSHIP_WORKER = r'''
import hashlib
import importlib
import json
import os
import pickle
from pathlib import Path
import sys
import types

NATIVE_LOADER_ALIASES = (
    "ctypes.CDLL",
    "ctypes.cdll.LoadLibrary",
    "ctypes.cdll._dlltype",
    "ctypes._dlopen",
    "_ctypes.dlopen",
)

if len(sys.argv) != 4:
    raise RuntimeError("the native-owner audit worker received unexpected inputs")
root = Path(sys.argv[1]).resolve(strict=True)
role = sys.argv[2]
if role not in ("rust", "vm", "zig"):
    raise RuntimeError("the native-owner audit worker received a foreign family")
native = json.loads(sys.argv[3])
if not isinstance(native, dict) or not native:
    raise RuntimeError("the native-owner audit worker has no source-bound native engine")
sys.path.insert(0, str(root))
from tools import python_re_universal_public_oracle_stage10 as stage10
guard = stage10.stage07._install_family_guard(role, native)
expected_bridge = {
    "rust": "candidates._rust_bridge",
    "vm": "candidates._vm_native",
    "zig": "candidates._zig_bridge",
}[role]
candidate_name = "candidates." + role + "_candidate"
candidate = importlib.import_module(candidate_name)
bridge = importlib.import_module(expected_bridge)
if not isinstance(guard, dict):
    raise RuntimeError("the owned-type worker omitted the real native import guard")
for key in (
    "enabled", "stdlib_re_blocked", "cpython_sre_blocked",
    "third_party_regex_blocked", "cross_family_blocked",
    "foreign_dynamic_libraries_blocked",
):
    if guard.get(key) is not True:
        raise RuntimeError("the native-owner audit weakened a guard: " + key)
if guard.get("family") != role:
    raise RuntimeError("the native-owner audit substituted a candidate family")
if (
    tuple(stage10.stage07.NATIVE_LOADER_ALIASES) != NATIVE_LOADER_ALIASES
    or guard.get("native_loader_aliases_blocked") != list(NATIVE_LOADER_ALIASES)
):
    raise RuntimeError("the native-owner audit weakened a native loader alias")
live = {
    name for name, value in sys.modules.items()
    if name.startswith("candidates.")
    and value is not None
    and not isinstance(value, stage10.stage07._ForbiddenRegexModule)
}
allowed = {candidate_name, expected_bridge}
if not live <= allowed or candidate_name not in live or expected_bridge not in live:
    raise RuntimeError("the native-owner audit loaded a foreign matching candidate")
with open("/proc/self/maps", "rb") as stream:
    maps = stream.read(4 * 1024 * 1024 + 1)
if len(maps) > 4 * 1024 * 1024:
    raise RuntimeError("the native-owner worker's memory map exceeds its bound")
observed = {}
for line in maps.splitlines():
    columns = line.split(maxsplit=5)
    if len(columns) != 6:
        continue
    raw = os.fsdecode(columns[5])
    if not raw.startswith("/"):
        continue
    try:
        relative = Path(raw).resolve(strict=True).relative_to(root).as_posix()
    except (OSError, RuntimeError, ValueError):
        continue
    if relative.startswith("candidates/") and ".so" in Path(relative).name:
        if relative not in native:
            raise RuntimeError("the native-owner worker mapped a foreign candidate binary")
        if relative not in observed:
            path = root / relative
            if path.is_symlink() or path.stat().st_size > 64 * 1024 * 1024:
                raise RuntimeError("an owned candidate binary is unsafe or too large")
            with path.open("rb") as stream:
                payload = stream.read(64 * 1024 * 1024 + 1)
            observed[relative] = hashlib.sha256(payload).hexdigest()
if observed != native:
    raise RuntimeError("the actual native mappings do not match audited ELF bytes")
records = []
owners = {}
for public_name in ("Pattern", "Match"):
    origin = getattr(candidate, public_name)
    if not isinstance(origin, type) or getattr(candidate, public_name, None) is not origin:
        raise RuntimeError("the public class is not the candidate's genuinely owned class")
    if origin.__name__ != public_name or origin.__qualname__ != public_name:
        raise RuntimeError("a native regex type changed its genuine public identity")
    native_bridge_identity = getattr(bridge, public_name, None) is origin
    expected_owner = expected_bridge if public_name == "Match" else candidate_name
    if origin.__module__ != expected_owner:
        raise RuntimeError("a public regex type claims a false or foreign import owner")
    if native_bridge_identity is not (public_name == "Match"):
        raise RuntimeError("a public regex type fabricated its native bridge identity")
    owner = importlib.import_module(origin.__module__)
    if getattr(owner, public_name, None) is not origin:
        raise RuntimeError("the native regex type cannot be genuinely reimported")
    owners[public_name] = {
        "module": origin.__module__,
        "name": origin.__name__,
        "qualified_name": origin.__qualname__,
        "native_bridge_module": expected_bridge,
        "candidate_identity": True,
        "native_bridge_identity": native_bridge_identity,
        "genuinely_importable": True,
    }
    for argument_name, argument in (("str", str), ("bytes", bytes)):
        alias = origin[argument]
        if type(alias) is not types.GenericAlias or alias.__origin__ is not origin:
            raise RuntimeError("the public regex type returned an imitation generic alias")
        for label, protocol in (
            ("protocol-0", 0), ("protocol-2", 2),
            ("protocol-4", 4), ("highest-protocol", pickle.HIGHEST_PROTOCOL),
        ):
            restored = pickle.loads(pickle.dumps(alias, protocol=protocol))
            if (
                type(restored) is not types.GenericAlias
                or restored.__origin__ is not origin
                or restored.__args__ != (argument,)
                or restored != alias
                or hash(restored) != hash(alias)
            ):
                raise RuntimeError("an unmodified ordinary pickle lost the owned regex type")
            records.append({
                "id": public_name + ":" + argument_name + ":" + label,
                "origin": public_name,
                "argument": argument_name,
                "protocol": protocol,
                "protocol_name": label,
                "passed": True,
                "genuine_generic_alias": True,
                "same_owned_native_origin": True,
                "standard_pickle_round_trip": True,
            })
live_after = {
    name for name, value in sys.modules.items()
    if name.startswith("candidates.")
    and value is not None
    and not isinstance(value, stage10.stage07._ForbiddenRegexModule)
}
if live_after != live:
    raise RuntimeError("ordinary native-type serialization loaded a foreign candidate")
print(json.dumps({
    "schema": "rebar-postfinal-from-scratch-audit-v6-owned-types",
    "status": "PASS", "result": "PASS", "passed": True,
    "family": role, "candidate_module": candidate_name,
    "native_bridge_module": expected_bridge,
    "public_types": owners, "records": records,
    "standard_pickle_checks": 16,
    "native_sha256": observed,
    "guard": guard,
    "loaded_candidate_modules": sorted(live),
    "candidate_regex_matching_executed": False,
    "third_party_regex_packages": 0,
    "benchmark_or_timing_executed": False,
    "fixture_accessed": False,
}, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
'''


def _validate_owner(document: Any, family: str, native: Mapping[str, str]) -> dict[str, Any]:
    require(
        isinstance(document, dict)
        and document.get("schema") == SCHEMA + "-owned-types"
        and document.get("status") == "PASS"
        and document.get("result") == "PASS"
        and document.get("passed") is True
        and document.get("family") == family
        and document.get("candidate_module") == "candidates." + family + "_candidate"
        and document.get("native_bridge_module") == OWNED_NATIVE_MODULES[family]
        and document.get("native_sha256") == dict(native)
        and document.get("standard_pickle_checks") == 16
        and document.get("candidate_regex_matching_executed") is False
        and document.get("third_party_regex_packages") == 0
        and document.get("benchmark_or_timing_executed") is False
        and document.get("fixture_accessed") is False,
        "a real guarded ordinary-pickle proof is missing: " + family,
    )
    owners = document.get("public_types")
    require(isinstance(owners, dict) and set(owners) == {"Pattern", "Match"},
            "a candidate concealed a genuine native type: " + family)
    for name in ("Pattern", "Match"):
        item = owners[name]
        expected_module = (
            OWNED_NATIVE_MODULES[family] if name == "Match"
            else "candidates." + family + "_candidate"
        )
        require(
            isinstance(item, dict)
            and item.get("module") == expected_module
            and item.get("name") == name
            and item.get("qualified_name") == name
            and item.get("native_bridge_module") == OWNED_NATIVE_MODULES[family]
            and item.get("candidate_identity") is True
            and item.get("native_bridge_identity") is (name == "Match")
            and item.get("genuinely_importable") is True,
            "the pickle proof substituted a foreign or synthetic type: " + family,
        )
    records = document.get("records")
    expected_rows = [
        (
            origin + ":" + argument + ":" + protocol_name,
            origin, argument, protocol_name, protocol,
        )
        for origin in ("Pattern", "Match")
        for argument in ("str", "bytes")
        for protocol_name, protocol in (
            ("protocol-0", 0), ("protocol-2", 2),
            ("protocol-4", 4), ("highest-protocol", pickle.HIGHEST_PROTOCOL),
        )
    ]
    require(
        isinstance(records, list)
        and len(records) == 16
        and all(isinstance(item, dict) for item in records)
        and [
            (item.get("id"), item.get("origin"), item.get("argument"),
             item.get("protocol_name"), item.get("protocol"))
            for item in records
        ] == expected_rows
        and all(
            item.get("passed") is True
            and item.get("genuine_generic_alias") is True
            and item.get("same_owned_native_origin") is True
            and item.get("standard_pickle_round_trip") is True
            for item in records
        ),
        "a real standard-pickle result was omitted, replaced, or failed: " + family,
    )
    guard = document.get("guard")
    require(
        isinstance(guard, dict)
        and guard.get("family") == family
        and all(guard.get(key) is True for key in (
            "enabled", "stdlib_re_blocked", "cpython_sre_blocked",
            "third_party_regex_blocked", "cross_family_blocked",
            "foreign_dynamic_libraries_blocked",
        ))
        and guard.get("native_loader_aliases_blocked") == list(NATIVE_LOADER_ALIASES)
        and document.get("loaded_candidate_modules") == sorted({
            "candidates." + family + "_candidate", OWNED_NATIVE_MODULES[family]
        }),
        "a genuine ordinary-pickle worker weakened native isolation: " + family,
    )
    return document


def _run_owner(family: str, native: Mapping[str, str]) -> dict[str, Any]:
    require(family in CORE_FAMILIES and isinstance(native, dict) and bool(native),
            "refusing an unowned V6 native type worker")
    payload = json.dumps(dict(native), sort_keys=True, ensure_ascii=True,
                         separators=(",", ":"))
    require(len(payload.encode("ascii")) <= 16 * 1024,
            "the candidate native fingerprints exceed their safe process boundary")
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    process = subprocess.run(
        [sys.executable, "-I", "-B", "-c", OWNERSHIP_WORKER,
         str(ROOT), family, payload],
        capture_output=True, check=False, timeout=45, env=env,
    )
    require(process.returncode == 0, "the guarded native ownership worker failed: " + family)
    require(not process.stderr and 0 < len(process.stdout) <= MAX_WORKER_BYTES,
            "the native ownership worker returned missing, unsafe, or noisy evidence")
    try:
        document = json.loads(process.stdout)
    except (UnicodeError, ValueError) as error:
        raise AuditV6Error("the native ownership worker returned invalid evidence") from error
    return _validate_owner(document, family, native)


def _synthetic_owner(family: str) -> tuple[dict[str, Any], dict[str, str]]:
    native = {path: "a" * 64 for path in OWNED_NATIVE_PATHS[family].values()}
    bridge = OWNED_NATIVE_MODULES[family]
    records = [
        {
            "id": name + ":" + argument + ":" + protocol,
            "origin": name, "argument": argument, "protocol": number,
            "protocol_name": protocol, "passed": True,
            "genuine_generic_alias": True, "same_owned_native_origin": True,
            "standard_pickle_round_trip": True,
        }
        for name in ("Pattern", "Match")
        for argument in ("str", "bytes")
        for protocol, number in (
            ("protocol-0", 0), ("protocol-2", 2),
            ("protocol-4", 4),
            ("highest-protocol", pickle.HIGHEST_PROTOCOL),
        )
    ]
    return {
        "schema": SCHEMA + "-owned-types", "status": "PASS",
        "result": "PASS", "passed": True, "family": family,
        "candidate_module": "candidates." + family + "_candidate",
        "native_bridge_module": bridge,
        "public_types": {
            name: {"module": bridge if name == "Match"
                   else "candidates." + family + "_candidate", "name": name,
                   "qualified_name": name, "native_bridge_module": bridge,
                   "candidate_identity": True,
                   "native_bridge_identity": name == "Match",
                   "genuinely_importable": True}
            for name in ("Pattern", "Match")
        },
        "records": records, "standard_pickle_checks": 16,
        "native_sha256": native,
        "guard": {
            "enabled": True, "family": family,
            "stdlib_re_blocked": True, "cpython_sre_blocked": True,
            "third_party_regex_blocked": True, "cross_family_blocked": True,
            "foreign_dynamic_libraries_blocked": True,
            "native_loader_aliases_blocked": list(NATIVE_LOADER_ALIASES),
        },
        "loaded_candidate_modules": sorted({
            "candidates." + family + "_candidate", bridge
        }),
        "candidate_regex_matching_executed": False,
        "third_party_regex_packages": 0,
        "benchmark_or_timing_executed": False,
        "fixture_accessed": False,
    }, native


def self_test() -> dict[str, Any]:
    core.ensure_candidate_free()
    inherited = source_v5.self_test()
    source_v5.validate_v5_controls(inherited)
    effects = core.previous.BlockSelfTestEffects()
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: Any) -> None:
        checks.append({"name": name, "passed": bool(passed)})

    def rejected(name: str, operation: Any) -> None:
        try:
            operation()
        except (source_v5.AuditV5Error, TypeError, ValueError, KeyError, UnicodeError):
            check(name, True)
        else:
            check(name, False)

    with effects:
        for item in inherited["checks"]:
            check("v5:" + item["name"], item["passed"] is True)
        check("preserve-at-least-198-genuine-v5-source-controls",
              inherited["check_count"] >= 198)
        check("preserve-exact-three-independent-native-families",
              CORE_FAMILIES == ("rust", "vm", "zig"))
        check("preserve-exact-twelve-owned-candidate-sources",
              sum(map(len, OWNED_SOURCE_PATHS.values())) == 12
              and len({p for paths in OWNED_SOURCE_PATHS.values() for p in paths}) == 12)
        check("preserve-exact-five-owned-native-binaries",
              sum(map(len, OWNED_NATIVE_PATHS.values())) == 5)
        check("preserve-exact-five-immutable-native-loader-aliases",
              NATIVE_LOADER_ALIASES == (
                  "ctypes.CDLL", "ctypes.cdll.LoadLibrary",
                  "ctypes.cdll._dlltype", "ctypes._dlopen", "_ctypes.dlopen",
              ))
        check("preserve-exact-v5-source-and-report-fingerprints",
              core.valid_sha256(V5_SOURCE_SHA256)
              and core.valid_sha256(V5_REPORT_SHA256))
        check("pin-exact-twelve-public-correctness-and-history-inputs",
              len(FROZEN_PUBLIC_INPUTS) == 12
              and all(core.valid_sha256(x) for x in FROZEN_PUBLIC_INPUTS.values()))
        check("permit-only-new-exclusive-v6-proof",
              destination_name(REPORT_RELATIVE) == REPORT_RELATIVE)
        for name, value in (
            ("reject-v5-report-overwrite", source_v5.REPORT_RELATIVE),
            ("reject-absolute-destination", "/" + REPORT_RELATIVE),
            ("reject-traversing-destination", "candidates/audits/../FROM.json"),
            ("reject-foreign-destination", "candidates/audits/FOREIGN.json"),
            ("reject-noncanonical-destination", "candidates//audits/X.json"),
            ("reject-backslash-destination", "candidates\\audits\\X.json"),
            ("reject-nul-destination", REPORT_RELATIVE + "\x00"),
            ("reject-nontext-destination", 7),
        ):
            rejected(name, lambda item=value: destination_name(item))
        for family in CORE_FAMILIES:
            fixture, native = _synthetic_owner(family)
            check("accept-complete-in-memory-owned-type-proof:" + family,
                  _validate_owner(fixture, family, native) is fixture)
            for field, poisoned in (
                ("passed", False), ("family", "foreign"),
                ("standard_pickle_checks", 15),
                ("candidate_regex_matching_executed", True),
                ("third_party_regex_packages", 1),
                ("benchmark_or_timing_executed", True),
                ("fixture_accessed", True),
                ("native_sha256", {}),
                ("records", fixture["records"][:-1]),
                ("loaded_candidate_modules", []),
            ):
                rejected("reject-poisoned-" + family + "-" + field,
                         lambda k=field, v=poisoned, d=fixture, n=native:
                         _validate_owner({**d, k: v}, family, n))
            for field, poisoned in (
                ("id", "Pattern:str:counterfeit"),
                ("origin", "Match"),
                ("argument", "bytes"),
                ("protocol_name", "protocol-2"),
                ("protocol", 2),
                ("passed", False),
                ("genuine_generic_alias", False),
                ("same_owned_native_origin", False),
                ("standard_pickle_round_trip", False),
            ):
                poisoned_records = [dict(row) for row in fixture["records"]]
                poisoned_records[0][field] = poisoned
                rejected(
                    "reject-" + family + "-counterfeit-pickle-record-" + field,
                    lambda rows=poisoned_records, d=fixture, n=native:
                    _validate_owner({**d, "records": rows}, family, n),
                )
            swapped_records = [dict(row) for row in fixture["records"]]
            swapped_records[0], swapped_records[1] = (
                swapped_records[1], swapped_records[0]
            )
            rejected(
                "reject-" + family + "-swapped-pickle-protocol-records",
                lambda rows=swapped_records, d=fixture, n=native:
                _validate_owner({**d, "records": rows}, family, n),
            )
            for label, aliases in (
                ("swapped", list(reversed(NATIVE_LOADER_ALIASES))),
                ("duplicate", [*NATIVE_LOADER_ALIASES[:-1], NATIVE_LOADER_ALIASES[0]]),
                ("missing", list(NATIVE_LOADER_ALIASES[:-1])),
                ("arbitrary", ["a", "b", "c", "d", "e"]),
            ):
                poisoned_guard = {
                    **fixture["guard"], "native_loader_aliases_blocked": aliases,
                }
                rejected(
                    "reject-" + family + "-" + label + "-native-loader-aliases",
                    lambda g=poisoned_guard, d=fixture, n=native:
                    _validate_owner({**d, "guard": g}, family, n),
                )
            for public_name in ("Pattern", "Match"):
                for field, poisoned in (
                    ("module", "re"), ("name", "Foreign"),
                    ("candidate_identity", False),
                    ("native_bridge_identity", public_name != "Match"),
                    ("genuinely_importable", False),
                ):
                    owners = dict(fixture["public_types"])
                    owners[public_name] = {**owners[public_name], field: poisoned}
                    rejected("reject-foreign-" + family + "-" + public_name + "-" + field,
                             lambda o=owners, d=fixture, n=native:
                             _validate_owner({**d, "public_types": o}, family, n))
        core.ensure_candidate_free()
    check("zero-public-evidence-file-reads", effects.counts["files"] == 0)
    check("zero-public-evidence-file-writes", effects.counts["files"] == 0)
    check("zero-candidate-or-subprocess-starts", effects.counts["processes"] == 0)
    check("zero-clock-samples", effects.counts["clocks"] == 0)
    check("zero-entropy-draws", effects.counts["entropy"] == 0)
    names = [item["name"] for item in checks]
    failed = sorted(item["name"] for item in checks if item["passed"] is not True)
    if len(names) != len(set(names)):
        failed.append("duplicate-v6-source-control-name")
    core.ensure_candidate_free()
    return {
        "schema": SCHEMA + "-self-test", "status": "PASS" if not failed else "FAIL",
        "result": "PASS" if not failed else "FAIL", "passed": not failed,
        "checks": checks, "check_count": len(checks), "failed": failed,
        "inherited_v5_self_test": inherited,
        "inherited_v5_control_count": inherited["check_count"],
        "fixture_storage": "in-memory only", "candidate_imported": False,
        "candidate_imports": 0, "file_reads": effects.counts["files"],
        "file_writes": 0, "subprocesses": effects.counts["processes"],
        "clock_samples": effects.counts["clocks"],
        "production_entropy_drawn": False,
        "holdout_or_case_fixture_access": False,
        "benchmark_or_timing_executed": False,
        "production_cases_materialized": 0, "report_written": False,
    }


def audit() -> dict[str, Any]:
    runtime = core.verify_production_runtime()
    core.ensure_candidate_free()
    preserved: dict[str, str] = {}
    documents: dict[str, Any] = {}
    for relative in FROZEN_PUBLIC_INPUTS:
        payload, fingerprint = _read_frozen(relative)
        preserved[relative] = fingerprint
        if relative.endswith(".json"):
            documents[relative] = core.decode_report(payload, label=relative)
    historical = documents[source_v5.REPORT_RELATIVE]
    source_v5.validate_v5_report(historical, label="immutable historical-only V5 source audit")
    require(
        historical.get("audit_source_sha256") == V5_SOURCE_SHA256,
        "the historical V5 source audit was detached from its frozen controller",
    )
    strict = documents["candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json"]
    require(
        isinstance(strict, dict)
        and strict.get("postfinal_schema") == "rebar-postfinal-no-delegation-audit-v5"
        and strict.get("status") == "PASS"
        and strict.get("passed") is True
        and strict.get("audit_source_sha256") == STRICT_V5_SOURCE_SHA256
        and strict.get("base_audit_report_sha256") == V5_REPORT_SHA256,
        "the genuine historical strict V5 audit was concealed or substituted",
    )
    baseline = documents[
        "oracle/cpython-3.14.6/evidence/public-generic-alias-v11-self-oracle.json"
    ]
    failure = documents[
        "candidates/evidence/python-re-generic-alias-public-oracle-v11-rust-failures.json"
    ]
    require(
        isinstance(baseline, dict)
        and baseline.get("status") == "PASS"
        and baseline.get("cases") == 128
        and baseline.get("mismatches") == 0
        and isinstance(failure, dict)
        and failure.get("status") == "FAIL"
        and failure.get("failed_role") == "rust"
        and failure.get("mismatches") == 16
        and isinstance(failure.get("failure_records"), list)
        and len(failure["failure_records"]) == 16,
        "the genuine public Python reference or 16-case Rust failure changed",
    )
    controls = self_test()
    require(controls.get("passed") is True, "the inherited source-only V6 controls failed")
    core.ensure_candidate_free()
    gc.collect()
    with source_v5.allow_owned_locale_ctype():
        current = core.audit()
    core.validate_v3_report(current, label="fresh live independently owned V6 source audit")
    graph = _validate_fresh_graph(current)
    core.ensure_candidate_free()
    owners = {
        family: _run_owner(family, graph["native_sha256_by_family"][family])
        for family in CORE_FAMILIES
    }
    core.ensure_candidate_free()
    source_digest, _ = core.bounded_file(
        SOURCE_PATH, maximum=MAX_SOURCE_BYTES,
        label="actual append-only V6 source audit controller",
    )
    result = dict(current)
    result.update({
        "schema": SCHEMA, "postfinal_schema": SCHEMA,
        "status": "PASS", "result": "PASS", "passed": True,
        "audit_source_path": SOURCE_RELATIVE,
        "audit_source_sha256": source_digest,
        "previous_v5_audit_source_path": source_v5.SOURCE_RELATIVE,
        "previous_v5_audit_source_sha256": V5_SOURCE_SHA256,
        "previous_v5_audit_report_path": source_v5.REPORT_RELATIVE,
        "previous_v5_audit_report_sha256": V5_REPORT_SHA256,
        "previous_v5_report_historical": True,
        "previous_v5_strict_audit_source_path":
            "tools/postfinal_no_delegation_audit_v5.py",
        "previous_v5_strict_audit_source_sha256": STRICT_V5_SOURCE_SHA256,
        "previous_v5_strict_audit_report_path":
            "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json",
        "previous_v5_strict_audit_report_sha256": STRICT_V5_REPORT_SHA256,
        "historical_public_input_sha256": preserved,
        "postfinal_wrapper_self_test": controls,
        "postfinal_interpreter": runtime,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": graph["source_count"],
        "verified_candidate_source_paths": graph["source_paths"],
        "verified_native_role_count": graph["native_binary_count"],
        "native_sha256_by_family": graph["native_sha256_by_family"],
        "public_type_ownership": owners,
        "standard_pickle_checks_per_family": 16,
        "standard_pickle_checks": 48,
        "v6_allowed_locale_libc_primitives": sorted(source_v5.LOCALE_SYMBOLS),
        "v6_owned_locale_sources": dict(source_v5.OWNED_LOCALE_SOURCES),
        "postfinal_scope": {
            "append_only": True,
            "exclusive_report_path": REPORT_RELATIVE,
            "previous_v5_report_preserved": True,
            "previous_v5_report_historical": True,
            "exact_current_owned_candidate_source_count": 12,
            "actual_current_native_binary_count": 5,
            "standard_pickle_checks": 48,
            "candidate_imports": "isolated guarded subprocesses only",
            "candidate_regex_matching_executed_by_ownership_workers": False,
            "mapped_binaries_hashed_against_static_elf": True,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
    })
    require(result["standard_pickle_checks"] == sum(
        item["standard_pickle_checks"] for item in owners.values()
    ), "the complete native-type lifecycle audit changed its denominator")
    core.ensure_candidate_free()
    return result


def write_report(report: Mapping[str, Any], target: Path) -> str:
    require(isinstance(target, Path), "the exclusive V6 source destination is not a path")
    destination_name(target.as_posix() if not target.is_absolute()
                     else target.relative_to(ROOT).as_posix()
                     if target.is_relative_to(ROOT) else "")
    require(not target.is_symlink()
            and target.name == REPORT_PATH.name
            and target.parent.resolve(strict=True) == REPORT_PATH.parent.resolve(strict=True),
            "only the exact new source-proof destination may be created")
    payload = core.canonical(report) + b"\n"
    require(len(payload) <= MAX_REPORT_BYTES,
            "the complete genuine V6 source report exceeds its bound")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory = os.open(REPORT_PATH.parent.resolve(strict=True), flags)
    try:
        require(stat.S_ISDIR(os.fstat(directory).st_mode),
                "the exclusive V6 source report parent is unsafe")
        create = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        create |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
        descriptor = os.open(REPORT_PATH.name, create, 0o644, dir_fd=directory)
        try:
            pending = memoryview(payload)
            while pending:
                written = os.write(descriptor, pending)
                require(written > 0, "the exclusive V6 source-proof write stalled")
                pending = pending[written:]
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
    args = parser.parse_args(arguments)
    try:
        core.ensure_candidate_free()
        if args.self_test:
            require(args.output == REPORT_PATH,
                    "the V6 synthetic controls cannot write any report")
            result = self_test()
            sys.stdout.buffer.write(core.canonical(result) + b"\n")
            return 0 if result["passed"] else 1
        result = audit()
        report_digest = write_report(result, args.output)
        sys.stdout.buffer.write(core.canonical({
            "schema": SCHEMA, "postfinal_schema": SCHEMA,
            "status": "PASS", "result": "PASS", "passed": True,
            "report": REPORT_RELATIVE, "report_sha256": report_digest,
            "audit_source_sha256": result["audit_source_sha256"],
            "verified_core_family_count": 3,
            "verified_distinct_pipeline_count": 4,
            "verified_candidate_source_count": 12,
            "verified_native_role_count": 5,
            "standard_pickle_checks": 48,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }) + b"\n")
        return 0
    except (
        source_v5.AuditV5Error, OSError, RuntimeError, TypeError, ValueError,
        KeyError, subprocess.SubprocessError, UnicodeError,
    ) as error:
        sys.stdout.buffer.write(core.canonical({
            "schema": SCHEMA, "postfinal_schema": SCHEMA,
            "status": "FAIL", "result": "FAIL", "passed": False,
            "error": str(error), "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }) + b"\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
