#!/usr/bin/env python3
"""Refresh frozen correctness evidence for exactly the current V7 builds."""

from __future__ import annotations

import argparse
import collections
import copy
import gzip
import hashlib
import importlib.util
import json
import os
import platform
import stat
import subprocess
import sys
import tempfile
import unicodedata
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
PINNED_EXECUTABLE = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
SCHEMA = "rebar-postfinal-current-build-proofs-v7"
MAX_FILE_BYTES = 32 * 1024 * 1024
EDGE_SEED = 2026072329
EDGE_CASES = 223198
EDGE_CATEGORIES = 49
EDGE_SEEDED_CASES = 8
EDGE_UNICODE_STRIDE = 4099
EDGE_REFERENCE_SHA256 = (
    "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526"
)
DEEP_SEED = 2026072347
DEEP_CASES = 393
DEEP_SEEDED_CASES = 64
DEEP_REFERENCE_SHA256 = (
    "b184f3388320909b3c28fbd3ce9c15cefc992d3e852e9495ad8fb503d1cbaad8"
)

FROZEN_INPUTS = {
    "GOAL.md":
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V7.md":
        "781cf1e4c85a1de6d5d7d30ea8f451f0fd3417e0a81747ab8e1aa204b6478912",
    "tools/rust_v7_edge_oracle.py":
        "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca",
    "tools/rust_v8_deep_contract_oracle.py":
        "ba4b640d12444a5346d918a039d8a7a9fef0c78a54f6b66c6f0eb0c9dddbe978",
    "tools/rust_v8_multi_candidate_contract.py":
        "167f9d9114f95cd9c9821465339264f8b6eca9bf7f70b84774f4108f62f11a70",
    "candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz":
        "db43cbf8be1d6891eb4f009b8ae92995a6434f9753b944fbf0a8ed0b44237192",
    "tools/postfinal_from_scratch_audit_v7.py":
        "defa306e47a0d325af7d4c7fabb54324f6cb6d4653a494c46846838f5e2cf487",
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json":
        "efae1f94fb06a1eabbab352794410c4d8e20a78202dcbf769b08ff9c7cee130a",
    "tools/postfinal_no_delegation_audit_v7.py":
        "9283457064f32658747b449c4ee6ebd20ca7cc7dc442ce03ece6b02896cff4e4",
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json":
        "1f71caac01bffdffbf7ffdc2e21a9aa8d6936c452051cbdaa4c90ac67010fd34",
    "tools/rust_v8_multi_candidate_campaign.py":
        "46e53abac0d2347d5fc505aa792a5ee5f55489a6e73b1f57edf37a93a0a6d45d",
    "tools/rust_v8_multi_candidate_campaign_postfinal_v7.py":
        "92e397149585ee35ce5d26e984f00d093992471d3e92b929f65dd0386f75b243",
    "oracle/cpython-3.14.6/POSTFINAL-CAMPAIGN-V7.md":
        "dd7e6f80128fb9c8198398755caa178ede0a0ce178fedce2049a7e066be3250c",
    "candidates/evidence/"
    "rust-v8-rust-postfinal-locale-v7-sealed-campaign-first-failure.json":
        "62aba93fa8bdd6df7be93199aea6f58be7b24c095750c520179e96b98084b75a",
}

PRODUCTION_SHA256 = {
    "candidates/rust_candidate.py":
        "8ebf907cdd2c8150ab0b5741b65dbc4b4b53cede5b210db61fdbef9384c48a6f",
    "candidates/rust/py_bridge.c":
        "74c72c5a821429dafedebe253d773bea98bf99245c8059b8ea8bae20ce3b7fa3",
    "candidates/rust/src/lib.rs":
        "3a2ab20885daea11bbc90cb9707a154174742f836e818521c1d00e2a0afd0b64",
    "candidates/rust/src/search.rs":
        "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe",
    "candidates/rust/src/newline.rs":
        "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b",
    "candidates/rust/src/stack.rs":
        "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e",
    "candidates/rust/src/unicode_tables.rs":
        "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af",
    "candidates/vm_candidate.py":
        "28ea6e21b26c6cc0d29a68221d49c8d086b67007ee536e896b11056a676a68a5",
    "candidates/_vm_native.c":
        "ae8a6e8cdbe60f20cee453587bf84d1d8df643ccc3147975a1651e2f200ddcb6",
    "candidates/zig_candidate.py":
        "ab7d31011717dd0eca315de54cb0d7246b7ae609dc2de00f785dfa11eba97a1a",
    "candidates/zig/py_bridge.c":
        "cc3149471121c623c872f48e7933182a514718bfefe190d8a4a201676e24c31c",
    "candidates/zig/mini_regex.zig":
        "539bf5d378e0c2845c01519fcce62f1ef5e68610f477912c44a03027fb67a346",
    "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so":
        "2905f340b79d0b4aca472e9c4aeb1416b89ca993e25e184fc6ab54b1b39f1312",
    "candidates/_rust_engine.so":
        "d590300720215718782227dd8da1192047b4781bdb41ed94446cac06ba880e84",
    "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so":
        "cafef6a2bfe205e20bca030370d48fcbc0dc7188322629410b8e091bb1960798",
    "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so":
        "93672afac0efeaaad61b7316a4da934d6fe1f9216e8c4c823eb5c403f86c0491",
    "candidates/_zig_probe.so":
        "f658b2325642b38e8303d94c6bdc42e74ba8b1f021af76e80f0c8936aa10f81a",
}


@dataclass(frozen=True)
class Family:
    name: str
    module: str
    contract_name: str
    public_path: str
    native_sources: tuple[str, ...]
    native_mappings: tuple[tuple[str, str], ...]
    production_roles: tuple[tuple[str, str], ...]

    @property
    def edge_path(self) -> Path:
        return ROOT / "candidates" / "evidence" / (
            f"rust-v7-edge-oracle-{self.name}-postfinal-locale-v7.json.gz"
        )

    @property
    def edge_failure_path(self) -> Path:
        return ROOT / "candidates" / "evidence" / (
            f"rust-v7-edge-oracle-{self.name}-postfinal-locale-v7-first-failure.json.gz"
        )

    @property
    def deep_path(self) -> Path:
        return ROOT / "candidates" / "audits" / (
            f"RUST-V8-DEEP-CONTRACT-{self.contract_name}-POSTFINAL-LOCALE-V7.json.gz"
        )


FAMILIES = {
    "candidates.rust_candidate": Family(
        "rust", "candidates.rust_candidate", "RUST",
        "candidates/rust_candidate.py",
        (
            "candidates/rust/py_bridge.c", "candidates/rust/src/lib.rs",
            "candidates/rust/src/search.rs", "candidates/rust/src/newline.rs",
            "candidates/rust/src/stack.rs", "candidates/rust/src/unicode_tables.rs",
        ),
        (
            ("bridge", "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so"),
            ("engine", "candidates/_rust_engine.so"),
        ),
        (
            ("bridge-source", "candidates/rust/py_bridge.c"),
            ("native-bridge", "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so"),
            ("native-engine", "candidates/_rust_engine.so"),
            ("native-source", "candidates/rust/src/lib.rs"),
            ("public-python", "candidates/rust_candidate.py"),
        ),
    ),
    "candidates.vm_candidate": Family(
        "vm", "candidates.vm_candidate", "C",
        "candidates/vm_candidate.py", ("candidates/_vm_native.c",),
        (("native", "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so"),),
        (
            ("native-bridge", "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so"),
            ("native-source", "candidates/_vm_native.c"),
            ("public-python", "candidates/vm_candidate.py"),
        ),
    ),
    "candidates.zig_candidate": Family(
        "zig", "candidates.zig_candidate", "ZIG",
        "candidates/zig_candidate.py",
        ("candidates/zig/py_bridge.c", "candidates/zig/mini_regex.zig"),
        (
            ("bridge", "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so"),
            ("engine", "candidates/_zig_probe.so"),
        ),
        (
            ("bridge-source", "candidates/zig/py_bridge.c"),
            ("native-bridge", "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so"),
            ("native-engine", "candidates/_zig_probe.so"),
            ("native-source", "candidates/zig/mini_regex.zig"),
            ("public-python", "candidates/zig_candidate.py"),
        ),
    ),
}

REGEX_GUARDS = (
    ("re", "compile"), ("re", "search"), ("re", "match"),
    ("re", "fullmatch"), ("re", "findall"), ("re", "finditer"),
    ("re", "split"), ("re", "sub"), ("re", "subn"),
    ("re", "_compile"), ("_sre", "compile"),
    ("re._compiler", "compile"), ("re._parser", "parse"),
)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def decode_json(raw: bytes, label: str) -> Any:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            require(key not in result, f"{label} contains a duplicate JSON key")
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise ValueError(f"{label} contains non-finite JSON: {value}")

    return json.loads(
        raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=reject_constant
    )


def read_regular(path: Path, label: str) -> bytes:
    path = Path(path)
    require(path.is_absolute(), f"{label} is not an absolute path")
    require(path.resolve() == path, f"{label} is not its canonical path")
    require(not path.is_symlink(), f"{label} is a symlink")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode), f"{label} is not a regular file")
        require(before.st_size <= MAX_FILE_BYTES, f"{label} exceeds its bounded size")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = -1
            raw = stream.read(MAX_FILE_BYTES + 1)
            after = os.fstat(stream.fileno())
        require(len(raw) <= MAX_FILE_BYTES, f"{label} exceeded its bounded reader")
        require(
            (before.st_dev, before.st_ino, before.st_size,
             before.st_mtime_ns, before.st_ctime_ns)
            == (after.st_dev, after.st_ino, after.st_size,
                after.st_mtime_ns, after.st_ctime_ns),
            f"{label} changed while it was read",
        )
        require(len(raw) == before.st_size, f"{label} changed its exact byte size")
        return raw
    finally:
        if descriptor != -1:
            os.close(descriptor)


def digest_bytes(raw: bytes, expected: str, label: str) -> str:
    actual = hashlib.sha256(raw).hexdigest()
    require(actual == expected, f"{label} changed or is unproven")
    return actual


def expected_artifacts(family: Family) -> list[dict[str, str]]:
    return [
        {"role": role, "path": relative, "sha256": PRODUCTION_SHA256[relative]}
        for role, relative in sorted(family.production_roles)
    ]


def check_first_failure(document: Any) -> None:
    require(isinstance(document, dict), "the first campaign failure is not an object")
    exact = {
        "schema": "rebar-postfinal-campaign-v7-first-current-build-failure-v1",
        "status": "FAIL", "result": "FAIL", "candidate_family": "RUST",
        "candidate_module": "candidates.rust_candidate", "first_attempt": True,
        "phase": "candidate-edge-proof-validation-before-first-campaign-stage",
        "python": "3.14.6",
        "python_executable": str(PINNED_EXECUTABLE),
        "goal_path": "GOAL.md",
        "goal_sha256": FROZEN_INPUTS["GOAL.md"],
        "campaign_source_path": "tools/rust_v8_multi_candidate_campaign_postfinal_v7.py",
        "campaign_source_sha256": FROZEN_INPUTS[
            "tools/rust_v8_multi_candidate_campaign_postfinal_v7.py"
        ],
        "campaign_protocol_path": "oracle/cpython-3.14.6/POSTFINAL-CAMPAIGN-V7.md",
        "campaign_protocol_sha256": FROZEN_INPUTS[
            "oracle/cpython-3.14.6/POSTFINAL-CAMPAIGN-V7.md"
        ],
        "exit_code": 1, "exception_type": "AssertionError",
        "exception_message": "the RUST public-python is stale or unproven",
        "historical_edge_checks": EDGE_CASES,
        "historical_edge_categories": EDGE_CATEGORIES,
        "historical_deep_checks": DEEP_CASES,
        "historical_deep_seeded_cases": DEEP_SEEDED_CASES,
        "historical_deep_was_validated_by_failed_campaign": False,
        "campaign_output_created": False, "completed_campaign_stages": 0,
        "candidate_matching_workers_started": 0,
        "qualifies_current_engine": False, "holdout_accessed": False,
        "performance_fixtures_opened": 0, "timing_performed": False,
        "performance": "NOT MEASURED",
    }
    for key, value in exact.items():
        require(document.get(key) == value, f"the preserved first failure changed: {key}")
    changed = document.get("changed_rust_roles")
    require(isinstance(changed, list) and len(changed) == 3,
            "the original three genuinely stale Rust roles were changed")
    expected_changed = {
        "public-python": (
            "candidates/rust_candidate.py",
            "ed210957f3fc7a8d87ce38cfc775cd380bed19dcde7e8acd23d09197abb60048",
        ),
        "native-bridge": (
            "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
            "81fc4c4a92005f0588dd9b811988587d4d421dd8e1102eebcab53f4deb27cd36",
        ),
        "bridge-source": (
            "candidates/rust/py_bridge.c",
            "3d432d8f53a75eb2c3c75d118c811ac7ba12c432d987422223d55773fbb36abe",
        ),
    }
    observed: set[str] = set()
    for item in changed:
        require(isinstance(item, dict), "a preserved changed Rust role is malformed")
        role = item.get("role")
        require(role in expected_changed and role not in observed,
                "a preserved changed Rust role is missing or repeated")
        relative, historical = expected_changed[role]
        require(item.get("path") == relative and item.get("historical_sha256") == historical,
                f"the original Rust failure history was changed: {role}")
        require(item.get("current_sha256") == PRODUCTION_SHA256[relative],
                f"the first failure is not bound to the current Rust build: {role}")
        observed.add(role)
    unchanged = document.get("unchanged_rust_roles")
    require(isinstance(unchanged, list) and len(unchanged) == 2,
            "the preserved unchanged Rust roles were removed")
    require(
        {
            (item.get("role"), item.get("path"), item.get("sha256"))
            for item in unchanged if isinstance(item, dict)
        }
        == {
            ("native-source", "candidates/rust/src/lib.rs",
             PRODUCTION_SHA256["candidates/rust/src/lib.rs"]),
            ("native-engine", "candidates/_rust_engine.so",
             PRODUCTION_SHA256["candidates/_rust_engine.so"]),
        }, "the first-failure unchanged current Rust roles were substituted",
    )


def check_audit_family(document: dict[str, Any], family: Family, strict: bool) -> None:
    families = document.get("families")
    require(isinstance(families, dict), "the source audit lost candidate families")
    detail = families.get(family.name)
    require(isinstance(detail, dict) and detail.get("passed") is True,
            f"the {family.contract_name} source audit did not pass")
    public = detail.get("python_source")
    require(isinstance(public, dict) and public.get("passed") is True,
            f"the {family.contract_name} public Python source is unaudited")
    require(public.get("file") == family.public_path
            and public.get("sha256") == PRODUCTION_SHA256[family.public_path],
            f"the {family.contract_name} audited public Python source is stale")
    sources = detail.get("native_sources")
    require(isinstance(sources, list), f"the {family.contract_name} lost native source proof")
    require(
        {
            (item.get("file"), item.get("sha256"))
            for item in sources if isinstance(item, dict) and item.get("passed") is True
        }
        == {(path, PRODUCTION_SHA256[path]) for path in family.native_sources},
        f"the {family.contract_name} source audit omitted or changed owned sources",
    )
    pipeline = detail.get("owned_pipeline")
    require(isinstance(pipeline, dict) and pipeline.get("passed") is True,
            f"the {family.contract_name} lacks its own matching pipeline")
    runtime = detail.get("isolated_runtime")
    require(isinstance(runtime, dict) and runtime.get("passed") is True,
            f"the {family.contract_name} isolated ownership audit failed")
    mappings = runtime.get("native_mapping_provenance")
    require(isinstance(mappings, dict) and mappings.get("passed") is True,
            f"the {family.contract_name} native-mapping audit failed")
    require(mappings.get("expected_owned_mapping_count") == len(family.native_mappings)
            and mappings.get("observed_owned_mapping_count") == len(family.native_mappings),
            f"the {family.contract_name} native-mapping denominator changed")
    rows = mappings.get("observed_owned_mappings")
    require(isinstance(rows, list) and len(rows) == len(family.native_mappings),
            f"the {family.contract_name} native mappings are missing or duplicated")
    require(
        {
            (item.get("role"), item.get("file"), item.get("sha256"))
            for item in rows
            if isinstance(item, dict)
            and item.get("matches_static_elf") is True
            and (not strict or item.get("content_sha256_recomputed") is True)
        }
        == {
            (role, relative, PRODUCTION_SHA256[relative])
            for role, relative in family.native_mappings
        }, f"the {family.contract_name} native binary or actual mapping is stale",
    )
    if strict:
        require(runtime.get("guard_persistent") is True,
                f"the {family.contract_name} lost its persistent no-delegation guard")
        registry = runtime.get("registry_provenance")
        require(isinstance(registry, dict) and registry.get("passed") is True,
                f"the {family.contract_name} registry no-delegation guard failed")
        for key in ("forbidden_loaded_modules", "retained_forbidden_module_references",
                    "unexpected_candidate_modules"):
            require(registry.get(key) == [],
                    f"the {family.contract_name} loaded a forbidden matching engine")
    else:
        require(runtime.get("module") == family.module,
                f"the {family.contract_name} audited a different public module")
        require(runtime.get("prohibited_import_and_loader_probes") == {
            "cpython_sre": True, "foreign_native_loader": True,
            "other_candidate": True, "stdlib_re": True,
            "third_party_regex": True,
        }, f"the {family.contract_name} lost an original anti-delegation probe")


def check_audits(base: Any, strict: Any) -> None:
    require(isinstance(base, dict) and isinstance(strict, dict),
            "the current-build audit records are not JSON objects")
    base_expected = {
        "schema": "rebar-postfinal-from-scratch-audit-v7",
        "status": "PASS", "result": "PASS",
        "audit_source_path": "tools/postfinal_from_scratch_audit_v7.py",
        "audit_source_sha256": FROZEN_INPUTS["tools/postfinal_from_scratch_audit_v7.py"],
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_native_role_count": 5,
    }
    strict_expected = {
        "schema": "rebar-postfinal-no-delegation-audit-v7",
        "status": "PASS", "result": "PASS",
        "audit_source_path": "tools/postfinal_no_delegation_audit_v7.py",
        "audit_source_sha256": FROZEN_INPUTS["tools/postfinal_no_delegation_audit_v7.py"],
        "base_audit_postfinal_schema": base_expected["schema"],
        "base_audit_report_path": "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json",
        "base_audit_report_sha256": FROZEN_INPUTS[
            "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json"
        ],
        "base_audit_source_path": "tools/postfinal_from_scratch_audit_v7.py",
        "base_audit_source_sha256": FROZEN_INPUTS[
            "tools/postfinal_from_scratch_audit_v7.py"
        ],
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_public_type_family_count": 3,
        "verified_standard_pickle_count": 48,
        "verified_match_repr_checks": 6,
    }
    for document, expected, label in (
        (base, base_expected, "from-scratch"),
        (strict, strict_expected, "no-delegation"),
    ):
        for key, value in expected.items():
            require(document.get(key) == value, f"the {label} audit changed: {key}")
        for family in FAMILIES.values():
            check_audit_family(document, family, strict=label == "no-delegation")
    owned_sources = tuple(path for path in PRODUCTION_SHA256 if not path.endswith(".so"))
    require(base.get("verified_candidate_source_paths") == list(owned_sources),
            "the current-build source audit no longer proves all 12 owned sources")


def verify_runtime() -> None:
    require(platform.python_implementation() == "CPython",
            "the refresh requires the pinned CPython oracle")
    require(tuple(sys.version_info[:3]) == (3, 14, 6),
            "the refresh requires exact CPython 3.14.6")
    require(Path(sys.executable).resolve() == PINNED_EXECUTABLE.resolve(),
            "the refresh requires the exact pinned CPython executable")
    require(unicodedata.unidata_version == "16.0.0",
            "the refresh requires pinned Unicode 16.0.0")
    require(sys.dont_write_bytecode and os.environ.get("PYTHONDONTWRITEBYTECODE") == "1",
            "the refresh requires -B and PYTHONDONTWRITEBYTECODE=1")
    require(str(ROOT) in os.environ.get("PYTHONPATH", "").split(os.pathsep),
            "the original frozen deep suite requires the canonical PYTHONPATH")


def preflight() -> dict[str, Any]:
    verify_runtime()
    verified: dict[str, bytes] = {}
    for relative, expected in FROZEN_INPUTS.items():
        raw = read_regular(ROOT / relative, relative)
        digest_bytes(raw, expected, relative)
        if relative.endswith(".json"):
            verified[relative] = raw
    for relative, expected in PRODUCTION_SHA256.items():
        raw = read_regular(ROOT / relative, relative)
        digest_bytes(raw, expected, f"current production artifact {relative}")
        if relative.endswith(".so"):
            require(raw.startswith(b"\x7fELF"),
                    f"the owned native binary is not a real ELF: {relative}")
    base_path = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json"
    strict_path = "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json"
    failure_path = (
        "candidates/evidence/"
        "rust-v8-rust-postfinal-locale-v7-sealed-campaign-first-failure.json"
    )
    base = decode_json(verified[base_path], base_path)
    strict = decode_json(verified[strict_path], strict_path)
    failure = decode_json(verified[failure_path], failure_path)
    check_audits(base, strict)
    check_first_failure(failure)
    return {"base": base, "strict": strict, "failure": failure}


def load_contract() -> Any:
    relative = "tools/rust_v8_multi_candidate_contract.py"
    path = ROOT / relative
    digest_bytes(read_regular(path, relative), FROZEN_INPUTS[relative], relative)
    name = "_rebar_postfinal_current_build_contract_v7"
    existing = sys.modules.get(name)
    if existing is None:
        spec = importlib.util.spec_from_file_location(name, path)
        require(spec is not None and spec.loader is not None,
                "the verified original proof producer cannot be loaded")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            sys.modules.pop(name, None)
            raise
    else:
        module = existing
    require(Path(module.RUNNER).resolve() == path,
            "a different multi-candidate proof producer was substituted")
    expected = {
        "EDGE_SCRIPT_SHA256": FROZEN_INPUTS["tools/rust_v7_edge_oracle.py"],
        "EDGE_SEED": EDGE_SEED, "EDGE_CHECKS": EDGE_CASES,
        "EDGE_CATEGORIES": EDGE_CATEGORIES,
        "EDGE_REFERENCE_SHA256": EDGE_REFERENCE_SHA256,
        "FROZEN_SUITE_SHA256": FROZEN_INPUTS["tools/rust_v8_deep_contract_oracle.py"],
        "FROZEN_FAILURE_SHA256": FROZEN_INPUTS[
            "candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz"
        ],
        "FROZEN_SEED": DEEP_SEED, "FROZEN_CASES": DEEP_CASES,
        "FROZEN_SEEDED_CASES": DEEP_SEEDED_CASES,
        "FROZEN_REFERENCE_SHA256": DEEP_REFERENCE_SHA256,
    }
    for key, value in expected.items():
        require(getattr(module, key, None) == value,
                f"the frozen multi-candidate producer changed: {key}")
    for family in FAMILIES.values():
        spec = module.SPECS.get(family.module)
        require(spec is not None and spec.module == family.module
                and spec.family == family.contract_name
                and spec.public_path == family.public_path,
                f"the original producer substituted the {family.contract_name} family")
    return module


def decode_archive(raw: bytes, label: str) -> tuple[dict[str, Any], bytes]:
    require(10 <= len(raw) <= MAX_FILE_BYTES,
            f"{label} is not a bounded gzip archive")
    require(raw[:2] == b"\x1f\x8b" and raw[2] == 8
            and raw[3] == 0 and raw[4:8] == b"\x00\x00\x00\x00",
            f"{label} has nondeterministic or invalid gzip metadata")
    try:
        decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
        payload = decompressor.decompress(raw, MAX_FILE_BYTES + 1)
        require(len(payload) <= MAX_FILE_BYTES and not decompressor.unconsumed_tail,
                f"{label} exceeded its bounded decompressed size")
        remaining = MAX_FILE_BYTES + 1 - len(payload)
        payload += decompressor.flush(remaining)
        require(len(payload) <= MAX_FILE_BYTES and decompressor.eof
                and not decompressor.unused_data,
                f"{label} is truncated, oversized, or has trailing gzip data")
        document = decode_json(payload, label)
    except (UnicodeError, ValueError, zlib.error) as error:
        raise AssertionError(f"{label} is not valid, bounded JSON gzip") from error
    require(isinstance(document, dict), f"{label} does not contain a JSON object")
    return document, payload


def validate_edge(
    raw: bytes, source_path: Path, family: Family, contract: Any
) -> tuple[dict[str, Any], dict[str, Any]]:
    label = f"{family.contract_name} complete current-build edge proof"
    document, payload = decode_archive(raw, label)
    canonical = (
        json.dumps(document, ensure_ascii=True, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")
    require(payload == canonical, f"{label} is not the original canonical edge JSON")
    for key, value in {
        "seeded_cases": EDGE_SEEDED_CASES,
        "unicode_stride": EDGE_UNICODE_STRIDE,
        "json_normalization": {"lone_surrogates": "surrogatepass_utf8_hex"},
    }.items():
        require(document.get(key) == value, f"{label} changed: {key}")
    spec = contract.SPECS[family.module]
    complete, proof = contract.validate_edge_document(
        document, spec, hashlib.sha256(raw).hexdigest(), source_path
    )
    require(proof["production_artifacts"] == expected_artifacts(family),
            f"{label} is not bound to all current owned production roles")
    require(
        complete == {
            item["role"]: (item["path"], item["sha256"])
            for item in expected_artifacts(family)
        }, f"{label} changed an authorized production role",
    )
    return document, proof


def validate_edge_failure(
    raw: bytes, source_path: Path, family: Family, contract: Any
) -> tuple[dict[str, Any], dict[str, Any]]:
    label = f"{family.contract_name} genuine complete current-build edge failure"
    document, payload = decode_archive(raw, label)
    canonical = (
        json.dumps(document, ensure_ascii=True, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")
    require(payload == canonical, f"{label} is not the original canonical edge JSON")
    for key, value in {
        "seeded_cases": EDGE_SEEDED_CASES,
        "unicode_stride": EDGE_UNICODE_STRIDE,
        "json_normalization": {"lone_surrogates": "surrogatepass_utf8_hex"},
    }.items():
        require(document.get(key) == value, f"{label} changed: {key}")
    failures = document.get("failures")
    count = document.get("failed")
    require(type(count) is int and count > 0
            and isinstance(failures, list) and len(failures) == count
            and all(isinstance(item, dict) for item in failures),
            f"{label} hid, invented, or changed its complete genuine failure rows")
    actual = document.get("actual_sha256")
    require(isinstance(actual, str) and len(actual) == 64
            and all(char in "0123456789abcdef" for char in actual)
            and actual != EDGE_REFERENCE_SHA256,
            f"{label} misrepresented the actual failing candidate observations")

    # Only the validator input is normalized. The original, complete failed
    # bytes are never edited, published as a pass, or used to qualify a family.
    provenance = copy.deepcopy(document)
    provenance["failed"] = 0
    provenance["failures"] = []
    provenance["actual_sha256"] = EDGE_REFERENCE_SHA256
    complete, proof = contract.validate_edge_document(
        provenance, contract.SPECS[family.module],
        hashlib.sha256(raw).hexdigest(), source_path,
    )
    require(proof["production_artifacts"] == expected_artifacts(family)
            and complete == {
                item["role"]: (item["path"], item["sha256"])
                for item in expected_artifacts(family)
            }, f"{label} is not bound to its exact current owned production roles")
    return document, proof


def fresh_target(path: Path, parent: Path, expected_name: str) -> Path:
    require(path.is_absolute(), "a current-build proof target is not absolute")
    require(path.name == expected_name, "the proof target substituted a family filename")
    require(path.parent == parent and path.resolve() == path,
            "the proof target escaped its exact authorized parent")
    require(parent.is_dir() and not parent.is_symlink(),
            "the proof target parent is missing or is a symlink")
    require(not path.exists() and not path.is_symlink(),
            "refusing to overwrite existing current-build proof evidence")
    return path


def child_command(family: Family, mode: str, temporary_path: Path | None = None) -> list[str]:
    if mode == "edge":
        require(temporary_path is not None,
                "the original edge producer requires private temporary evidence")
        return [
            str(PINNED_EXECUTABLE), "-I", "-B",
            str(ROOT / "tools/rust_v7_edge_oracle.py"),
            "--module", family.module, "--seed", str(EDGE_SEED),
            "--seeded-cases", str(EDGE_SEEDED_CASES),
            "--unicode-stride", str(EDGE_UNICODE_STRIDE),
            "--output", str(temporary_path),
        ]
    require(mode == "deep" and temporary_path is None,
            "an unsupported proof producer or temporary deep path was requested")
    return [
        str(PINNED_EXECUTABLE), "-I", "-B",
        str(ROOT / "tools/rust_v8_multi_candidate_contract.py"), "--gate",
        "--module", family.module,
        "--edge-oracle", str(family.edge_path),
        "--output", str(family.deep_path),
    ]


def run_original(command: list[str]) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPATH"] = str(ROOT)
    return subprocess.run(
        command, cwd=str(ROOT), env=environment, capture_output=True,
        text=True, check=False,
    )


class ProofFailure(AssertionError):
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.details = details or {}


def publish_exclusive(path: Path, raw: bytes) -> None:
    fresh_target(path, ROOT / "candidates/evidence", path.name)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor != -1:
            os.close(descriptor)
    require(read_regular(path, "published current-build edge archive") == raw,
            "the exclusively published edge archive changed")


def expected_cross_guards(family: Family, contract: Any) -> list[dict[str, str]]:
    names = {
        name for name in contract.SPECS if name != family.module
    }
    names.update(
        spec.native_module for spec in contract.SPECS.values()
        if spec.native_module is not None
        and spec.module != family.module
    )
    names.update({"regex", "_regex", "pcre2", "re2", "hyperscan"})
    return [
        {
            "module": name,
            "type": "GuardSignal",
            "message": (
                "production reached a forbidden independent or external engine: "
                + name
            ),
        }
        for name in sorted(names)
    ]


def validate_deep(
    raw: bytes, family: Family, edge: dict[str, Any], contract: Any,
    *, allow_failure: bool = False,
) -> dict[str, Any]:
    label = f"{family.contract_name} complete current-build deep proof"
    report, payload = decode_archive(raw, label)
    suite = contract.load_frozen_suite()
    contract.original_failure(suite)
    require(suite.canonical(report) == payload,
            f"{label} is not the original canonical deep JSON")
    exact = {
        "schema": contract.FROZEN_SCHEMA,
        "python": "3.14.6", "seed": DEEP_SEED,
        "seeded_case_count": DEEP_SEEDED_CASES,
        "checks": DEEP_CASES,
        "fixture_sha256": contract.FROZEN_FIXTURE_SHA256,
        "suite_path": "tools/rust_v8_deep_contract_oracle.py",
        "suite_sha256": FROZEN_INPUTS["tools/rust_v8_deep_contract_oracle.py"],
        "reference_a_sha256": DEEP_REFERENCE_SHA256,
        "reference_b_sha256": DEEP_REFERENCE_SHA256,
        "candidate_module": family.module,
        "candidate_family": family.contract_name,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    for key, value in exact.items():
        require(report.get(key) == value, f"{label} changed: {key}")
    require(report.get("native_artifacts") == expected_artifacts(family),
            f"{label} used stale, incomplete, or foreign production artifacts")
    require(report.get("edge_oracle") == edge,
            f"{label} is not bound to its own fresh current-build edge archive")
    require(report.get("stdlib_vs_stdlib_mismatches") == [],
            f"{label} concealed a Python-reference disagreement")
    require(report.get("differential_poison_self_tests") == {
        "changed_observation_poison": "PASS",
        "identical_reference": "PASS",
        "missing_observation_poison": "PASS",
    }, f"{label} lost a real original differential poison control")
    guards = report.get("guard_observations")
    require(isinstance(guards, list) and len(guards) == len(REGEX_GUARDS),
            f"{label} lost an original Python regex poison guard")
    require(
        {
            (item.get("module"), item.get("name"))
            for item in guards
            if isinstance(item, dict) and item.get("type") == "GuardSignal"
        }
        == set(REGEX_GUARDS), f"{label} changed its active Python poison guards",
    )
    require(report.get("forbidden_regex_guards") == len(REGEX_GUARDS),
            f"{label} changed the Python poison-guard denominator")
    cross = report.get("cross_engine_guard_observations")
    require(cross == expected_cross_guards(family, contract)
            and report.get("cross_engine_guard_count") == len(cross),
            f"{label} lost or substituted an active independent-engine guard")
    for field, role in (
        ("reference", "stdlib-a"),
        ("reference_independent_repeat", "stdlib-b"),
        ("candidate", "candidate"),
    ):
        worker = report.get(field)
        require(isinstance(worker, dict), f"{label} omitted the {role} worker")
        contract.verify_worker_report(
            suite, worker, role, edge if role == "candidate" else None
        )
        diagnostics = worker.get("implementation_private_gc_diagnostics")
        require(isinstance(diagnostics, list) and len(diagnostics) == DEEP_SEEDED_CASES,
                f"{label} changed the {role} private-diagnostic denominator")
    require(report["candidate"].get("cross_engine_guards") == cross,
            f"{label} changed the actual candidate's cross-engine poison guards")
    require(report.get("candidate_sha256")
            == report["candidate"].get("observation_sha256"),
            f"{label} substituted the actual candidate observation digest")
    reference_rows = report["reference"]["observations"]
    repeat_rows = report["reference_independent_repeat"]["observations"]
    candidate_rows = report["candidate"]["observations"]
    require(suite.mismatches(reference_rows, repeat_rows) == [],
            f"{label} contains disagreeing independently isolated Python references")
    mismatches = suite.mismatches(reference_rows, candidate_rows)
    require(report.get("public_mismatches") == mismatches,
            f"{label} omitted, substituted, or reordered a real public failure")
    require(report.get("public_mismatch_count") == len(mismatches),
            f"{label} changed its actual public mismatch denominator")
    counts = dict(sorted(collections.Counter(
        item.get("family", "missing") for item in mismatches
    ).items()))
    require(report.get("public_mismatch_family_counts") == counts,
            f"{label} concealed a public-failure category")
    expected_status = "FAIL" if mismatches else "PASS"
    require(report.get("status") == expected_status,
            f"{label} misrepresented the actual frozen differential result")
    require(allow_failure or expected_status == "PASS",
            f"{label} contains genuine frozen public mismatches")
    if expected_status == "PASS":
        require(report.get("candidate_sha256") == DEEP_REFERENCE_SHA256,
                f"{label} has a passing label but a changed reference digest")
    under_poison = report.get("native_under_poison")
    require(isinstance(under_poison, dict)
            and isinstance(under_poison.get("search"), dict)
            and under_poison["search"].get("group0") == "a"
            and under_poison.get("sub") == {"status": "value", "value": "xbx"},
            f"{label} did not prove actual native matching under poison")
    require(report.get("multifamily_runner") == {
        "path": "tools/rust_v8_multi_candidate_contract.py",
        "sha256": FROZEN_INPUTS["tools/rust_v8_multi_candidate_contract.py"],
    }, f"{label} was produced by an untracked or changed deep producer")
    require(report.get("frozen_failure_evidence") == {
        "path": "candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz",
        "archive_sha256": FROZEN_INPUTS[
            "candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz"
        ],
        "status": "FAIL", "public_mismatch_count": 104,
    }, f"{label} changed or concealed the original frozen failure")
    diagnostics = report.get("implementation_private_gc_topology_differences")
    require(isinstance(diagnostics, list)
            and report.get("implementation_private_gc_topology_difference_count")
            == len(diagnostics),
            f"{label} hid or changed implementation-private diagnostics")
    return report


def refresh_edge(family: Family) -> dict[str, Any]:
    preflight()
    target = fresh_target(
        family.edge_path, ROOT / "candidates/evidence", family.edge_path.name
    )
    failure_target = fresh_target(
        family.edge_failure_path, ROOT / "candidates/evidence",
        family.edge_failure_path.name,
    )
    contract = load_contract()
    with tempfile.TemporaryDirectory(
        prefix=f"rebar-v7-current-edge-{family.name}-", dir="/tmp"
    ) as directory:
        private_root = Path(directory).resolve()
        require(private_root.parent == Path("/tmp").resolve(),
                "the frozen edge suite escaped its private direct /tmp directory")
        temporary_path = private_root / "current-build-edge.json.gz"
        command = child_command(family, "edge", temporary_path)
        child = run_original(command)
        if child.returncode:
            details: dict[str, Any] = {
                "candidate_module": family.module,
                "candidate_family": family.contract_name,
                "child_exit_code": child.returncode,
                "stderr_tail": child.stderr[-8000:],
                "stdout_tail": child.stdout[-12000:],
                "passing_evidence_published": False,
                "failure_evidence_exclusively_preserved": False,
                "performance": "NOT MEASURED",
                "holdout": "NOT ACCESSED",
            }
            if temporary_path.exists() and not temporary_path.is_symlink():
                raw_failure = read_regular(temporary_path, "actual private edge failure")
                actual, proof = validate_edge_failure(
                    raw_failure, failure_target, family, contract
                )
                preflight()
                fresh_target(target, ROOT / "candidates/evidence", target.name)
                fresh_target(
                    failure_target, ROOT / "candidates/evidence", failure_target.name
                )
                publish_exclusive(failure_target, raw_failure)
                preserved = read_regular(
                    failure_target, "exclusively preserved real current-build edge failure"
                )
                preserved_document, preserved_proof = validate_edge_failure(
                    preserved, failure_target, family, contract
                )
                require(preserved == raw_failure
                        and preserved_proof["archive_sha256"] == proof["archive_sha256"]
                        and preserved_document == actual,
                        "exclusive publication changed the actual complete edge failure")
                details.update({
                    "actual_failure_count": actual.get("failed"),
                    "actual_check_count": actual.get("correctness_checks"),
                    "actual_category_count": len(actual["categories"]),
                    "actual_seed": actual["seed"],
                    "first_failures": actual.get("failures", [])[:5],
                    "complete_failure_row_count": len(actual["failures"]),
                    "failure_evidence_path": failure_target.relative_to(ROOT).as_posix(),
                    "failure_evidence_sha256": hashlib.sha256(preserved).hexdigest(),
                    "failure_evidence_exclusively_preserved": True,
                    "production_artifacts": proof["production_artifacts"],
                })
            raise ProofFailure(
                "the original frozen edge producer failed; no passing archive was published",
                details,
            )
        raw = read_regular(temporary_path, "private current-build edge archive")
        _, private_proof = validate_edge(raw, temporary_path, family, contract)
        preflight()
        fresh_target(target, ROOT / "candidates/evidence", target.name)
        fresh_target(failure_target, ROOT / "candidates/evidence", failure_target.name)
        publish_exclusive(target, raw)
    published = read_regular(target, "exclusively published current-build edge archive")
    _, proof = validate_edge(published, target, family, contract)
    require(proof["archive_sha256"] == private_proof["archive_sha256"],
            "publication substituted the original passing current-build edge archive")
    return {
        "schema": SCHEMA, "status": "PASS", "mode": "edge",
        "candidate_module": family.module, "candidate_family": family.contract_name,
        "seed": EDGE_SEED, "checks": EDGE_CASES,
        "category_count": EDGE_CATEGORIES,
        "reference_sha256": EDGE_REFERENCE_SHA256,
        "source_sha256": FROZEN_INPUTS["tools/rust_v7_edge_oracle.py"],
        "evidence_path": target.relative_to(ROOT).as_posix(),
        "evidence_sha256": proof["archive_sha256"],
        "production_artifacts": proof["production_artifacts"],
        "first_campaign_failure_sha256": FROZEN_INPUTS[
            "candidates/evidence/"
            "rust-v8-rust-postfinal-locale-v7-sealed-campaign-first-failure.json"
        ],
        "exclusive_creation": True,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def refresh_deep(family: Family) -> dict[str, Any]:
    preflight()
    contract = load_contract()
    edge_raw = read_regular(family.edge_path, "required current-build edge archive")
    _, edge = validate_edge(edge_raw, family.edge_path, family, contract)
    fresh_target(family.deep_path, ROOT / "candidates/audits", family.deep_path.name)
    child = run_original(child_command(family, "deep"))
    if child.returncode:
        details: dict[str, Any] = {
            "candidate_module": family.module,
            "candidate_family": family.contract_name,
            "child_exit_code": child.returncode,
            "stderr_tail": child.stderr[-8000:],
            "stdout_tail": child.stdout[-12000:],
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }
        if family.deep_path.exists() and not family.deep_path.is_symlink():
            raw = read_regular(family.deep_path, "preserved real deep failure")
            report = validate_deep(raw, family, edge, contract, allow_failure=True)
            require(report.get("status") == "FAIL",
                    "a failing original deep producer unexpectedly published a pass")
            details.update({
                "preserved_failure_path": family.deep_path.relative_to(ROOT).as_posix(),
                "preserved_failure_sha256": hashlib.sha256(raw).hexdigest(),
                "actual_check_count": report["checks"],
                "actual_failure_count": report["public_mismatch_count"],
                "first_failures": report["public_mismatches"][:5],
                "failure_evidence_exclusively_preserved": True,
            })
        raise ProofFailure(
            "the original frozen deep producer failed; genuine evidence was not retried",
            details,
        )
    raw = read_regular(family.deep_path, "exclusive current-build deep archive")
    report = validate_deep(raw, family, edge, contract)
    preflight()
    require(read_regular(family.edge_path, "verified bound current-build edge archive")
            == edge_raw, "the current-build edge archive changed during deep execution")
    require(read_regular(family.deep_path, "verified current-build deep archive") == raw,
            "the current-build deep archive changed during verification")
    return {
        "schema": SCHEMA, "status": "PASS", "mode": "deep",
        "candidate_module": family.module, "candidate_family": family.contract_name,
        "seed": DEEP_SEED, "checks": DEEP_CASES,
        "seeded_case_count": DEEP_SEEDED_CASES,
        "reference_sha256": DEEP_REFERENCE_SHA256,
        "source_sha256": FROZEN_INPUTS[
            "tools/rust_v8_multi_candidate_contract.py"
        ],
        "suite_sha256": FROZEN_INPUTS["tools/rust_v8_deep_contract_oracle.py"],
        "evidence_path": family.deep_path.relative_to(ROOT).as_posix(),
        "evidence_sha256": hashlib.sha256(raw).hexdigest(),
        "edge_evidence_path": family.edge_path.relative_to(ROOT).as_posix(),
        "edge_evidence_sha256": edge["archive_sha256"],
        "production_artifacts": report["native_artifacts"],
        "exclusive_creation": True,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def rejected(name: str, action: Callable[[], Any]) -> dict[str, str]:
    try:
        action()
    except (AssertionError, OSError, ValueError, TypeError, KeyError,
            json.JSONDecodeError, zlib.error) as error:
        return {"name": name, "status": "PASS", "error_type": type(error).__name__}
    raise AssertionError(f"a current-build refresh poison unexpectedly passed: {name}")


def self_test() -> dict[str, Any]:
    initial_candidates = {
        name for name in sys.modules
        if name == "candidates" or name.startswith("candidates.")
    }
    require(not initial_candidates,
            "the candidate-free controller self-test began with a loaded candidate")
    original_open = os.open

    def readonly_open(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
        write_flags = (os.O_WRONLY | os.O_RDWR | os.O_CREAT
                       | os.O_TRUNC | os.O_APPEND)
        require(not flags & write_flags,
                "the candidate-free refresh self-test attempted a filesystem write")
        if not isinstance(path, int):
            location = Path(os.fsdecode(path)).resolve()
            performance = (ROOT / "performance").resolve()
            require(not location.is_relative_to(performance)
                    and "holdout" not in location.name.casefold()
                    and not (location.parent == ROOT / "tools"
                             and location.name.startswith("perf_")),
                    "the candidate-free self-test attempted performance or holdout access")
        return original_open(path, flags, *args, **kwargs)

    blocked = AssertionError("the candidate-free self-test cannot start a worker")
    with (
        mock.patch.object(os, "open", side_effect=readonly_open),
        mock.patch.object(subprocess, "run", side_effect=blocked),
        mock.patch.object(subprocess, "Popen", side_effect=blocked),
        mock.patch.object(tempfile, "TemporaryDirectory", side_effect=blocked),
        mock.patch.object(tempfile, "mkdtemp", side_effect=blocked),
    ):
        authenticated = preflight()
        contract = load_contract()
        suite = contract.load_frozen_suite()
        baseline, _ = contract.original_failure(suite)
        controls: list[dict[str, str]] = []

        for family in FAMILIES.values():
            document = contract.synthetic_edge_document(contract.SPECS[family.module])
            document.update({
                "seeded_cases": EDGE_SEEDED_CASES,
                "unicode_stride": EDGE_UNICODE_STRIDE,
                "json_normalization": {"lone_surrogates": "surrogatepass_utf8_hex"},
            })
            edge_payload = (
                json.dumps(document, ensure_ascii=True, sort_keys=True, indent=2)
                + "\n"
            ).encode("utf-8")
            edge_raw = gzip.compress(edge_payload, compresslevel=9, mtime=0)
            _, edge = validate_edge(edge_raw, family.edge_path, family, contract)
            failed_document = copy.deepcopy(document)
            failed_document.update({
                "failed": 1,
                "failures": [{
                    "id": "synthetic-self-test-real-failure-control",
                    "expected": "synthetic-pinned-reference",
                    "actual": "synthetic-mismatch",
                }],
                "actual_sha256": "0" * 64,
            })

            def edge_archive(value: dict[str, Any]) -> bytes:
                payload = (
                    json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2)
                    + "\n"
                ).encode("utf-8")
                return gzip.compress(payload, compresslevel=9, mtime=0)

            failure_raw = edge_archive(failed_document)
            checked_failure, checked_failure_proof = validate_edge_failure(
                failure_raw, family.edge_failure_path, family, contract
            )
            require(checked_failure["failed"] == 1
                    and checked_failure_proof["production_artifacts"]
                    == expected_artifacts(family),
                    "the source-only genuine-failure control lost its owned provenance")
            cross = expected_cross_guards(family, contract)
            candidate = copy.deepcopy(baseline["reference"])
            candidate.update({
                "role": "candidate", "native_artifacts": expected_artifacts(family),
                "guard_count": len(REGEX_GUARDS),
                "candidate_module": family.module,
                "candidate_family": family.contract_name,
                "cross_engine_guards": cross,
                "cross_engine_guard_count": len(cross),
            })
            deep = {
                "schema": contract.FROZEN_SCHEMA, "status": "PASS",
                "python": "3.14.6", "seed": DEEP_SEED,
                "seeded_case_count": DEEP_SEEDED_CASES, "checks": DEEP_CASES,
                "fixture_sha256": contract.FROZEN_FIXTURE_SHA256,
                "suite_path": "tools/rust_v8_deep_contract_oracle.py",
                "suite_sha256": FROZEN_INPUTS[
                    "tools/rust_v8_deep_contract_oracle.py"
                ],
                "reference_a_sha256": DEEP_REFERENCE_SHA256,
                "reference_b_sha256": DEEP_REFERENCE_SHA256,
                "candidate_sha256": DEEP_REFERENCE_SHA256,
                "stdlib_vs_stdlib_mismatches": [],
                "public_mismatch_count": 0,
                "public_mismatch_family_counts": {}, "public_mismatches": [],
                "implementation_private_gc_topology_difference_count": 0,
                "implementation_private_gc_topology_differences": [],
                "differential_poison_self_tests": {
                    "changed_observation_poison": "PASS",
                    "identical_reference": "PASS",
                    "missing_observation_poison": "PASS",
                },
                "forbidden_regex_guards": len(REGEX_GUARDS),
                "guard_observations": [
                    {"module": module, "name": name, "type": "GuardSignal"}
                    for module, name in REGEX_GUARDS
                ],
                "native_under_poison": {
                    "search": {"group0": "a"},
                    "sub": {"status": "value", "value": "xbx"},
                },
                "native_artifacts": expected_artifacts(family),
                "cross_engine_guard_count": len(cross),
                "cross_engine_guard_observations": cross,
                "candidate_module": family.module,
                "candidate_family": family.contract_name,
                "reference": copy.deepcopy(baseline["reference"]),
                "reference_independent_repeat": copy.deepcopy(
                    baseline["reference_independent_repeat"]
                ),
                "candidate": candidate,
                "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
                "edge_oracle": edge,
                "frozen_failure_evidence": {
                    "path": "candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz",
                    "archive_sha256": FROZEN_INPUTS[
                        "candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz"
                    ],
                    "status": "FAIL", "public_mismatch_count": 104,
                },
                "multifamily_runner": {
                    "path": "tools/rust_v8_multi_candidate_contract.py",
                    "sha256": FROZEN_INPUTS[
                        "tools/rust_v8_multi_candidate_contract.py"
                    ],
                },
            }

            def archive(value: dict[str, Any]) -> bytes:
                return gzip.compress(suite.canonical(value), compresslevel=9, mtime=0)

            validate_deep(archive(deep), family, edge, contract)

            def edge_poison(name: str, change: Callable[[dict[str, Any]], None]) -> None:
                changed = copy.deepcopy(document)
                change(changed)
                raw = edge_archive(changed)
                controls.append(rejected(
                    f"{family.name}:{name}",
                    lambda: validate_edge(raw, family.edge_path, family, contract),
                ))

            def failure_poison(
                name: str, change: Callable[[dict[str, Any]], None]
            ) -> None:
                changed = copy.deepcopy(failed_document)
                change(changed)
                raw = edge_archive(changed)
                controls.append(rejected(
                    f"{family.name}:{name}",
                    lambda: validate_edge_failure(
                        raw, family.edge_failure_path, family, contract
                    ),
                ))

            def deep_poison(name: str, change: Callable[[dict[str, Any]], None]) -> None:
                changed = copy.deepcopy(deep)
                change(changed)
                raw = archive(changed)
                controls.append(rejected(
                    f"{family.name}:{name}",
                    lambda: validate_deep(raw, family, edge, contract),
                ))

            edge_poison("changed-edge-seed", lambda value: value.update({"seed": 0}))
            edge_poison("changed-edge-denominator", lambda value: value.update({
                "correctness_checks": EDGE_CASES - 1
            }))
            edge_poison("missing-edge-category", lambda value: value["categories"].pop(
                next(iter(value["categories"]))
            ))
            edge_poison("changed-generated-edge-count", lambda value: value.update({
                "seeded_cases": EDGE_SEEDED_CASES - 1
            }))
            edge_poison("changed-unicode-stride", lambda value: value.update({
                "unicode_stride": EDGE_UNICODE_STRIDE + 1
            }))
            edge_poison("changed-edge-reference", lambda value: value.update({
                "expected_sha256": "0" * 64
            }))
            edge_poison("hidden-edge-failure", lambda value: value.update({
                "failures": [{"id": "synthetic-hidden-failure"}]
            }))
            edge_poison("stale-public-artifact", lambda value: next(
                item for item in value["candidate_artifacts"]
                if item["role"] == "public-python"
            ).update({"sha256": "0" * 64}))
            edge_poison("foreign-edge-family", lambda value: value.update({
                "module": next(key for key in FAMILIES if key != family.module)
            }))
            failure_poison("counterfeit-edge-failure-status", lambda value: value.update({
                "failed": 0
            }))
            failure_poison("hidden-edge-failure-rows", lambda value: value.update({
                "failures": []
            }))
            failure_poison("changed-edge-failure-reference", lambda value: value.update({
                "expected_sha256": "0" * 64
            }))
            failure_poison("failing-edge-with-passing-digest", lambda value: value.update({
                "actual_sha256": EDGE_REFERENCE_SHA256
            }))
            failure_poison("changed-edge-failure-seed", lambda value: value.update({
                "seed": EDGE_SEED + 1
            }))
            failure_poison("incomplete-edge-failure-denominator", lambda value:
                           value.update({"correctness_checks": EDGE_CASES - 1}))
            failure_poison("missing-edge-failure-category", lambda value:
                           value["categories"].pop(next(iter(value["categories"]))))
            failure_poison("crossed-edge-failure-family", lambda value: value.update({
                "module": next(key for key in FAMILIES if key != family.module)
            }))
            failure_poison("stale-edge-failure-native-artifact", lambda value: next(
                item for item in value["candidate_artifacts"]
                if item["role"] == "native-bridge"
            ).update({"sha256": "0" * 64}))
            controls.append(rejected(
                f"{family.name}:failure-archive-misclassified-as-pass",
                lambda: validate_edge(failure_raw, family.edge_path, family, contract),
            ))
            controls.append(rejected(
                f"{family.name}:passing-archive-misclassified-as-failure",
                lambda: validate_edge_failure(
                    edge_raw, family.edge_failure_path, family, contract
                ),
            ))
            controls.append(rejected(
                f"{family.name}:truncated-full-failure-archive",
                lambda: validate_edge_failure(
                    failure_raw[:-1], family.edge_failure_path, family, contract
                ),
            ))
            deep_poison("changed-deep-seed", lambda value: value.update({"seed": 0}))
            deep_poison("changed-deep-denominator", lambda value: value.update({
                "checks": DEEP_CASES - 1
            }))
            deep_poison("missing-seeded-case", lambda value: value.update({
                "seeded_case_count": DEEP_SEEDED_CASES - 1
            }))
            deep_poison("foreign-deep-family", lambda value: value.update({
                "candidate_family": "FOREIGN"
            }))
            deep_poison("foreign-fresh-edge", lambda value: value["edge_oracle"].update({
                "archive_sha256": "0" * 64
            }))
            deep_poison("stale-native-artifact", lambda value: value["native_artifacts"][0]
                        .update({"sha256": "0" * 64}))
            deep_poison("hidden-public-failure", lambda value: value.update({
                "public_mismatch_count": 1
            }))
            deep_poison("changed-reference-digest", lambda value: value.update({
                "reference_a_sha256": "0" * 64
            }))
            deep_poison("missing-reference-observation", lambda value:
                        value["reference"]["observations"].pop())
            deep_poison("missing-candidate-observation", lambda value:
                        value["candidate"]["observations"].pop())
            deep_poison("missing-python-poison-guard", lambda value:
                        value["guard_observations"].pop())
            deep_poison("missing-independent-engine-guard", lambda value:
                        value["cross_engine_guard_observations"].pop())
            deep_poison("missing-differential-poison", lambda value:
                        value["differential_poison_self_tests"].pop(
                            "missing_observation_poison"
                        ))
            deep_poison("missing-native-under-poison", lambda value:
                        value["native_under_poison"].pop("search"))
            deep_poison("changed-original-deep-producer", lambda value:
                        value["multifamily_runner"].update({"sha256": "0" * 64}))
            deep_poison("hidden-original-failure", lambda value:
                        value["frozen_failure_evidence"].update({"status": "PASS"}))
            controls.append(rejected(
                f"{family.name}:crossed-edge-output-family",
                lambda: fresh_target(
                    family.edge_path, ROOT / "candidates/evidence",
                    "rust-v7-edge-oracle-foreign-postfinal-locale-v7.json.gz",
                ),
            ))
            controls.append(rejected(
                f"{family.name}:crossed-edge-failure-output-family",
                lambda: fresh_target(
                    family.edge_failure_path, ROOT / "candidates/evidence",
                    "rust-v7-edge-oracle-foreign-postfinal-locale-v7-first-failure.json.gz",
                ),
            ))
            controls.append(rejected(
                f"{family.name}:edge-failure-output-substituted-for-success",
                lambda: fresh_target(
                    family.edge_failure_path, ROOT / "candidates/evidence",
                    family.edge_path.name,
                ),
            ))
            controls.append(rejected(
                f"{family.name}:crossed-deep-output-family",
                lambda: fresh_target(
                    family.deep_path, ROOT / "candidates/audits",
                    "RUST-V8-DEEP-CONTRACT-FOREIGN-POSTFINAL-LOCALE-V7.json.gz",
                ),
            ))

        first = authenticated["failure"]
        for name, key, value in (
            ("hidden-first-failure", "status", "PASS"),
            ("hidden-first-failure-workers", "candidate_matching_workers_started", 1),
            ("changed-first-failure-campaign", "campaign_source_sha256", "0" * 64),
            ("hidden-stale-build", "exception_message", "synthetic substitution"),
        ):
            changed = copy.deepcopy(first)
            changed[key] = value
            controls.append(rejected(name, lambda value=changed: check_first_failure(value)))

        changed_base = copy.deepcopy(authenticated["base"])
        changed_base["families"]["rust"]["python_source"]["sha256"] = "0" * 64
        controls.append(rejected(
            "stale-current-build-source-audit",
            lambda: check_audits(changed_base, authenticated["strict"]),
        ))
        changed_strict = copy.deepcopy(authenticated["strict"])
        changed_strict["families"]["zig"]["isolated_runtime"][
            "guard_persistent"
        ] = False
        controls.append(rejected(
            "disabled-persistent-no-delegation-guard",
            lambda: check_audits(authenticated["base"], changed_strict),
        ))
        changed_mapping = copy.deepcopy(authenticated["strict"])
        changed_mapping["families"]["vm"]["isolated_runtime"][
            "native_mapping_provenance"
        ]["observed_owned_mappings"][0]["sha256"] = "0" * 64
        controls.append(rejected(
            "stale-current-native-elf-mapping",
            lambda: check_audits(authenticated["base"], changed_mapping),
        ))
        controls.append(rejected(
            "changed-frozen-producer-bytes",
            lambda: digest_bytes(b"synthetic-changed-source", "0" * 64,
                                 "synthetic frozen producer"),
        ))
        controls.append(rejected(
            "duplicate-evidence-json-key",
            lambda: decode_json(b'{"status":0,"status":1}', "synthetic duplicate"),
        ))
        controls.append(rejected(
            "nonfinite-evidence-json",
            lambda: decode_json(b'{"value":NaN}', "synthetic nonfinite"),
        ))
        controls.append(rejected(
            "truncated-deterministic-gzip",
            lambda: decode_archive(edge_raw[:-1], "synthetic truncated edge"),
        ))
        controls.append(rejected(
            "gzip-trailing-member",
            lambda: decode_archive(edge_raw + edge_raw,
                                   "synthetic trailing gzip member"),
        ))
        changed_header = bytearray(edge_raw)
        changed_header[4] = 1
        controls.append(rejected(
            "nondeterministic-gzip-timestamp",
            lambda: decode_archive(bytes(changed_header), "synthetic gzip timestamp"),
        ))
        failure_relative = (
            "candidates/evidence/"
            "rust-v8-rust-postfinal-locale-v7-sealed-campaign-first-failure.json"
        )
        original_failure_path = ROOT / failure_relative
        controls.append(rejected(
            "existing-evidence-overwrite",
            lambda: fresh_target(original_failure_path,
                                 ROOT / "candidates/evidence",
                                 original_failure_path.name),
        ))
        controls.append(rejected(
            "worker-execution-in-candidate-free-self-test",
            lambda: run_original([str(PINNED_EXECUTABLE), "-I", "-B"]),
        ))
        controls.append(rejected(
            "temporary-directory-in-candidate-free-self-test",
            lambda: tempfile.TemporaryDirectory(dir="/tmp"),
        ))
        controls.append(rejected(
            "evidence-write-in-candidate-free-self-test",
            lambda: os.open(ROOT / "candidates/evidence/synthetic-forbidden.json",
                            os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644),
        ))
        controls.append(rejected(
            "holdout-access-in-candidate-free-self-test",
            lambda: os.open(ROOT / "performance/synthetic-holdout", os.O_RDONLY),
        ))

        require(len(controls) >= 135,
                "the candidate-free refresh integrity controls lost a frozen denominator")
        require(len({item["name"] for item in controls}) == len(controls),
                "the candidate-free refresh integrity controls repeat a case")
        require(all(item["status"] == "PASS" for item in controls),
                "a candidate-free current-build refresh poison was accepted")
        require(not {
            name for name in sys.modules
            if name == "candidates" or name.startswith("candidates.")
        }, "the current-build self-test imported a production candidate")
        return {
            "schema": SCHEMA + "-self-test", "status": "PASS",
            "python": "3.14.6", "candidate_free": True,
            "candidate_workers_started": 0,
            "temporary_directories_created": 0,
            "repository_evidence_written": 0,
            "source_preflight": "PASS",
            "frozen_input_count": len(FROZEN_INPUTS),
            "current_production_source_count": 12,
            "current_native_binary_count": 5,
            "supported_families": {
                family.module: family.contract_name for family in FAMILIES.values()
            },
            "reserved_passing_edge_paths": [
                family.edge_path.relative_to(ROOT).as_posix()
                for family in FAMILIES.values()
            ],
            "reserved_edge_first_failure_paths": [
                family.edge_failure_path.relative_to(ROOT).as_posix()
                for family in FAMILIES.values()
            ],
            "first_campaign_failure_sha256": FROZEN_INPUTS[
                "candidates/evidence/"
                "rust-v8-rust-postfinal-locale-v7-sealed-campaign-first-failure.json"
            ],
            "edge_seed": EDGE_SEED,
            "edge_checks": EDGE_CASES, "edge_categories": EDGE_CATEGORIES,
            "deep_seed": DEEP_SEED, "deep_checks": DEEP_CASES,
            "deep_seeded_cases": DEEP_SEEDED_CASES,
            "integrity_poison_self_test_count": len(controls),
            "integrity_poison_self_tests": controls,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }


def main(arguments: list[str]) -> int:
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.environ["PYTHONPATH"] = str(ROOT)
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--edge", action="store_true")
    modes.add_argument("--deep", action="store_true")
    parser.add_argument("--module", choices=tuple(FAMILIES))
    options = parser.parse_args(arguments)
    if options.self_test:
        require(options.module is None,
                "the candidate-free self-test must not select a production candidate")
        report = self_test()
    else:
        require(options.module is not None,
                "a current-build proof requires one explicit independent family")
        family = FAMILIES[options.module]
        report = refresh_edge(family) if options.edge else refresh_deep(family)
    print(json.dumps(report, ensure_ascii=True, allow_nan=False,
                     sort_keys=True, separators=(",", ":")), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except ProofFailure as error:
        print(json.dumps({
            "schema": SCHEMA, "status": "FAIL", "error": str(error),
            **error.details,
        }, ensure_ascii=True, allow_nan=False, sort_keys=True,
            separators=(",", ":")), flush=True)
        raise SystemExit(1)
