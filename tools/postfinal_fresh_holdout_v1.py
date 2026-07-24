#!/usr/bin/env python3
"""Prospectively freeze, but never counterfeit, a one-use fresh holdout.

`self-test` is candidate-free and uses a fixed, nonproduction key.  The first
`freeze` writes only a prospective distribution manifest.  A second `freeze`
can obtain production randomness only after every input, proof, audit, and the
manifest itself is verified at the same remotely pushed Git commit and an
exclusive, durable one-use guard already exists.  `open` deliberately fails
closed: the independently audited public worker exposes three correctness
checks, not the four observable channels required by this holdout.
"""

from __future__ import annotations

import argparse
import base64
from dataclasses import asdict, dataclass
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import stat
import subprocess
import sys
import sysconfig
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent.parent
HOLDOUT_DIRECTORY = ROOT / "performance" / "postfinal-fresh-holdout-v1"
RUNNER_PATH = ROOT / "tools" / "postfinal_fresh_holdout_v1.py"
PROTOCOL_PATH = HOLDOUT_DIRECTORY / "PROTOCOL.md"
DEFAULT_MANIFEST = HOLDOUT_DIRECTORY / "FREEZE-MANIFEST.json"
DEFAULT_GUARD = HOLDOUT_DIRECTORY / ".FRESH-HOLDOUT-V1.one-use.guard"
DEFAULT_PUBLIC_RUNNER = ROOT / "tools" / "postfinal_public_practice_v4.py"
DEFAULT_GUARD_SOURCE = ROOT / "tools" / "postfinal_no_delegation_audit_v1.py"
DEFAULT_GUARD_REPORT = (
    ROOT / "candidates" / "audits" / "POSTFINAL-NO-DELEGATION-AUDIT-V1.json"
)
DEFAULT_BASE_AUDIT_SOURCE = ROOT / "tools" / "audit_from_scratch.py"
DEFAULT_BASE_AUDIT_REPORT = (
    ROOT / "candidates" / "audits" / "FROM-SCRATCH-AUDIT.json"
)
DEFAULT_PUBLIC_ORACLE = ROOT / "tools" / "python_re_universal_public_oracle_v1.py"
DEFAULT_ORACLE_PROOF = (
    ROOT
    / "candidates"
    / "evidence"
    / "python-re-universal-public-oracle-v1-all.json"
)

SCHEMA = "rebar-postfinal-fresh-holdout-v1"
CASE_SCHEMA = SCHEMA + "-case"
GUARD_AUDIT_SCHEMA = "rebar-postfinal-no-delegation-audit-v1"
PUBLIC_ORACLE_SCHEMA = "rebar-python-re-universal-public-oracle-v1"
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_VERSION = (3, 14, 6)
PINNED_SOABI = "cpython-314-x86_64-linux-gnu"

FAMILY_COUNT = 16
STRATUM_COUNT = 16
VARIANTS_PER_STRATUM = 256
CASE_COUNT = FAMILY_COUNT * STRATUM_COUNT * VARIANTS_PER_STRATUM
TRIAL_COUNT = 19
BASELINE_FAMILY = "re"
CANDIDATE_FAMILIES = ("rust", "vm", "zig")
WORKER_FAMILIES = (BASELINE_FAMILY, *CANDIDATE_FAMILIES)
CORRECTNESS_CHANNELS = (
    "compiled-pattern-metadata",
    "return-values-match-spans-and-buffer-representation",
    "exception-class-arguments-and-public-pattern-error-fields",
    "documented-converter-callback-warning-and-scanner-traces",
)
RAW_OBSERVATION_COUNT = CASE_COUNT * TRIAL_COUNT * len(WORKER_FAMILIES)
CORRECTNESS_GATE_COUNT = (
    CASE_COUNT * TRIAL_COUNT * len(CANDIDATE_FAMILIES)
    * len(CORRECTNESS_CHANNELS)
)
CONFIDENCE_INTERVAL_COUNT = (
    CASE_COUNT * len(CANDIDATE_FAMILIES) + len(CANDIDATE_FAMILIES)
)

MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_BINARY_BYTES = 64 * 1024 * 1024
MAX_JSON_BYTES = 16 * 1024 * 1024
MAX_GIT_RESPONSE_BYTES = 1024 * 1024
MAX_GUARD_LINE_BYTES = 16 * 1024
MAX_PATTERN_BYTES = 512
MAX_SUBJECT_BYTES = 4096
MAX_MATCHES = 64
MAX_OPERATIONS_PER_TRIAL = 1024
BOOTSTRAP_SAMPLES = 2000
HMAC_DOMAIN = b"rebar/postfinal-fresh-holdout/v1/case\x00"

NATIVE_SOURCE_PATHS: Mapping[str, tuple[str, ...]] = {
    "vm": ("candidates/_vm_native.c",),
    "rust": (
        "candidates/rust/py_bridge.c",
        "candidates/rust/src/lib.rs",
        "candidates/rust/src/search.rs",
        "candidates/rust/src/newline.rs",
        "candidates/rust/src/stack.rs",
        "candidates/rust/src/unicode_tables.rs",
    ),
    "zig": (
        "candidates/zig/py_bridge.c",
        "candidates/zig/mini_regex.zig",
    ),
}
PYTHON_SOURCE_PATHS: Mapping[str, str] = {
    "ast": "candidates/ast_candidate.py",
    "vm": "candidates/vm_candidate.py",
    "rust": "candidates/rust_candidate.py",
    "zig": "candidates/zig_candidate.py",
}
NATIVE_BINARY_PATHS: Mapping[tuple[str, str], str] = {
    ("vm", "native"): "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
    ("rust", "engine"): "candidates/_rust_engine.so",
    ("rust", "bridge"): "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
    ("zig", "engine"): "candidates/_zig_probe.so",
    ("zig", "bridge"): "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
}
GUARD_NATIVE_KEYS: Mapping[tuple[str, str], str] = {
    ("vm", "native"): "candidates.vm_candidate:native-engine",
    ("rust", "engine"): "candidates.rust_candidate:native-engine",
    ("rust", "bridge"): "candidates.rust_candidate:native-bridge",
    ("zig", "engine"): "candidates.zig_candidate:native-engine",
    ("zig", "bridge"): "candidates.zig_candidate:native-bridge",
}


class HoldoutIntegrityError(RuntimeError):
    """A prospective freeze or irreversible one-use condition failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HoldoutIntegrityError(message)


def canonical(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def ensure_candidate_free() -> None:
    loaded = sorted(
        name
        for name in sys.modules
        if name.startswith("candidates.")
        and (
            name.endswith("_candidate")
            or name.rsplit(".", 1)[-1]
            in {"_vm_native", "_rust_bridge", "_zig_bridge"}
        )
    )
    require(not loaded, f"the prospective holdout parent loaded a candidate: {loaded!r}")


def safe_repository_file(path: Path) -> tuple[Path, str]:
    require(not path.is_symlink(), f"a frozen input is a symlink: {path}")
    try:
        resolved = path.resolve(strict=True)
        relative = resolved.relative_to(ROOT.resolve()).as_posix()
    except (OSError, RuntimeError, ValueError) as error:
        raise HoldoutIntegrityError(
            f"a required frozen input is missing or escapes the repository: {path}"
        ) from error
    require(resolved.is_file(), f"a frozen input is not a regular file: {relative}")
    for component in Path(relative).parts:
        lowered = component.casefold()
        forbidden = (
            lowered == "v9"
            or lowered.startswith("v9-")
            or lowered.startswith("v9.")
            or "hidden" in lowered
            or lowered in {"holdout", "final"}
            or lowered.startswith("holdout-")
            or lowered.startswith("final-")
        )
        require(not forbidden, f"a restricted historical input was refused: {relative}")
    return resolved, relative


def destination(path: Path, *, purpose: str) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    parent = candidate.parent.resolve(strict=True)
    require(
        parent == HOLDOUT_DIRECTORY.resolve(strict=True),
        f"the {purpose} must be directly within the fresh-holdout directory",
    )
    require(not candidate.is_symlink(), f"the {purpose} must not be a symlink")
    return parent / candidate.name


def read_bounded(path: Path, maximum: int) -> bytes:
    resolved, relative = safe_repository_file(path)
    try:
        with resolved.open("rb") as stream:
            data = stream.read(maximum + 1)
    except OSError as error:
        raise HoldoutIntegrityError(f"cannot read frozen input: {relative}") from error
    require(len(data) <= maximum, f"frozen input exceeds its bound: {relative}")
    return data


def load_document(path: Path) -> tuple[dict[str, Any], bytes]:
    data = read_bounded(path, MAX_JSON_BYTES)
    try:
        value = json.loads(data)
    except (UnicodeError, ValueError) as error:
        raise HoldoutIntegrityError(f"a frozen JSON proof is invalid: {path}") from error
    require(isinstance(value, dict), f"a frozen JSON proof is not an object: {path}")
    return value, data


@dataclass(frozen=True)
class Family:
    name: str
    semantic: str
    optional_flag: str
    optional_flag_value: int


FAMILIES: tuple[Family, ...] = (
    Family("literal", "exact literal and positional boundaries", "IGNORECASE", 2),
    Family("character-class", "ASCII ranges and negated-class boundaries", "ASCII", 256),
    Family("alternation", "ordered alternatives and common prefixes", "IGNORECASE", 2),
    Family("greedy-repeat", "bounded greedy quantified dot", "DOTALL", 16),
    Family("lazy-repeat", "bounded non-greedy quantified dot", "DOTALL", 16),
    Family("counted-repeat", "minimum and maximum digit repetitions", "ASCII", 256),
    Family("named-captures", "named and positional capture metadata", "IGNORECASE", 2),
    Family("backreference", "named group backreference equality", "IGNORECASE", 2),
    Family("lookahead", "positive zero-width lookahead", "ASCII", 256),
    Family("fixed-lookbehind", "fixed-width positive lookbehind", "ASCII", 256),
    Family("multiline-anchor", "line anchors and multiline flag", "MULTILINE", 8),
    Family("dotall-newline", "dot/newline interaction and dotall flag", "DOTALL", 16),
    Family("ignorecase", "ASCII case-folding and literal classes", "IGNORECASE", 2),
    Family("unicode-word", "word categories and ASCII restriction", "ASCII", 256),
    Family("word-boundary", "zero-width word boundary transitions", "ASCII", 256),
    Family("empty-progress", "zero-width matches and scanner exhaustion", "ASCII", 256),
)


def stratum_descriptor(index: int) -> dict[str, Any]:
    require(0 <= index < STRATUM_COUNT, "fresh stratum index is out of bounds")
    return {
        "index": index,
        "input_domain": "bytes-like" if index & 8 else "text",
        "flag_tier": "family-flag" if index & 4 else "default",
        "window": "bounded" if index & 2 else "default",
        "lifecycle": "compiled" if index & 1 else "module",
    }


def wire_value(value: str | bytes, *, kind: str) -> dict[str, str]:
    if isinstance(value, str):
        require(kind == "str", "a text wire value has a nontext representation")
        return {"kind": kind, "text": value}
    require(kind in {"bytes", "bytearray", "memoryview"}, "invalid byte wire kind")
    return {
        "kind": kind,
        "base64": base64.b64encode(value).decode("ascii"),
    }


def decoded_wire(value: Mapping[str, Any]) -> str | bytes | bytearray | memoryview:
    kind = value.get("kind")
    if kind == "str":
        text = value.get("text")
        require(isinstance(text, str), "invalid text case representation")
        return text
    require(kind in {"bytes", "bytearray", "memoryview"}, "invalid bytes case representation")
    encoded = value.get("base64")
    require(isinstance(encoded, str), "invalid base64 case representation")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError) as error:
        raise HoldoutIntegrityError("invalid base64 in a fresh case") from error
    if kind == "bytearray":
        return bytearray(raw)
    if kind == "memoryview":
        return memoryview(raw)
    return raw


def family_payload(index: int, digest: bytes, *, text_domain: bool) -> tuple[str, str]:
    letters = "abcdefghijklmnopqrstuvwxyz"
    word = "".join(letters[item % len(letters)] for item in digest[:6])
    digits = "".join(str(item % 10) for item in digest[6:11])
    if index == 0:
        return word, word
    if index == 1:
        return r"[A-Za-z][A-Za-z0-9_]{1,5}", word[:4] + digits[:2]
    if index == 2:
        return r"(?:cat|cater|dog)", ("cater", "cat", "dog")[digest[11] % 3]
    if index == 3:
        return r"a.{0,8}z", "a" + word[:4] + "z"
    if index == 4:
        return r"a.{0,8}?z", "a" + word[:3] + "z" + word[:2] + "z"
    if index == 5:
        return r"[0-9]{2,5}", digits
    if index == 6:
        return r"(?P<left>[A-Za-z]+)-(?P<right>[0-9]{1,4})", word + "-" + digits[:4]
    if index == 7:
        piece = word[: 2 + digest[12] % 4]
        return r"(?P<word>[A-Za-z]{2,5})-(?P=word)", piece + "-" + piece
    if index == 8:
        return r"\b[A-Za-z]+(?=:)", word + ":" + digits[:2]
    if index == 9:
        return r"(?<=#)[A-Za-z]{2,6}", "#" + word
    if index == 10:
        return r"^item[0-9]{2}$", "before\nitem" + digits[:2] + "\nafter"
    if index == 11:
        return r"start.{0,12}end", "start" + word[:2] + "\n" + word[2:4] + "end"
    if index == 12:
        return r"token[a-z]{2}", "ToKeN" + word[:2]
    if index == 13:
        core = ("é" + word[:4]) if text_domain else word[:5]
        return r"\w{2,8}", core
    if index == 14:
        return r"\b(?:id|name)\b", "name " + word + " id"
    if index == 15:
        return r"(?=a)", "a" + word[:2] + "aa"
    raise HoldoutIntegrityError("fresh semantic family index is out of bounds")


def fresh_case(key: bytes, family_index: int, stratum_index: int, variant: int) -> dict[str, Any]:
    require(isinstance(key, bytes) and len(key) == 32, "fresh HMAC key must contain exactly 32 bytes")
    require(0 <= family_index < FAMILY_COUNT, "fresh semantic family index is out of bounds")
    require(0 <= variant < VARIANTS_PER_STRATUM, "fresh variant index is out of bounds")
    stratum = stratum_descriptor(stratum_index)
    material = (
        HMAC_DOMAIN
        + family_index.to_bytes(1, "big")
        + stratum_index.to_bytes(1, "big")
        + variant.to_bytes(2, "big")
    )
    digest = hmac.new(key, material, hashlib.sha256).digest()
    family = FAMILIES[family_index]
    text_domain = stratum["input_domain"] == "text"
    pattern_text, core = family_payload(family_index, digest, text_domain=text_domain)
    left = "p" + str(digest[20] % 10) + " "
    right = " q" + str(digest[21] % 10)
    subject_text = left + core + right
    bounded = stratum["window"] == "bounded"
    pos = len(left) if bounded else None
    endpos = len(left) + len(core) if bounded else None
    flags = family.optional_flag_value if stratum["flag_tier"] == "family-flag" else 0
    if text_domain:
        pattern = wire_value(pattern_text, kind="str")
        subject = wire_value(subject_text, kind="str")
        replacement = wire_value("R" + str(digest[22] % 10), kind="str")
    else:
        pattern = wire_value(pattern_text.encode("ascii"), kind="bytes")
        subject_kind = ("bytes", "bytearray", "memoryview")[digest[23] % 3]
        subject = wire_value(subject_text.encode("ascii"), kind=subject_kind)
        replacement = wire_value(
            ("R" + str(digest[22] % 10)).encode("ascii"),
            kind="bytes",
        )
    operations = (
        ("search", "match", "fullmatch", "findall", "finditer", "scanner", "split", "sub", "subn")
        if stratum["lifecycle"] == "compiled"
        else ("search", "match", "fullmatch", "findall", "finditer", "split", "sub", "subn")
    )
    result = {
        "schema": CASE_SCHEMA,
        "id": f"fresh.{family.name}.{stratum_index:02d}.{variant:03d}",
        "family": family.name,
        "family_index": family_index,
        "stratum": stratum,
        "variant": variant,
        "pattern": pattern,
        "subject": subject,
        "flags": flags,
        "pos": pos,
        "endpos": endpos,
        "lifecycle": stratum["lifecycle"],
        "operation": operations[digest[24] % len(operations)],
        "replacement": replacement,
        "maxsplit": digest[25] % 5,
        "replacement_count": digest[26] % 5,
        "max_matches": MAX_MATCHES,
    }
    require(len(pattern_text.encode("utf-8")) <= MAX_PATTERN_BYTES, "fresh pattern exceeded its bound")
    require(len(subject_text.encode("utf-8")) <= MAX_SUBJECT_BYTES, "fresh subject exceeded its bound")
    return result


def candidate_free_self_test() -> dict[str, Any]:
    ensure_candidate_free()
    import re as standard_re

    require(len(FAMILIES) == FAMILY_COUNT, "fresh semantic family cardinality changed")
    require(len({item.name for item in FAMILIES}) == FAMILY_COUNT, "fresh semantic families are not distinct")
    require(CASE_COUNT == 65_536, "the frozen case count changed")
    require(RAW_OBSERVATION_COUNT == 4_980_736, "the frozen raw observation count changed")
    require(CORRECTNESS_GATE_COUNT == 14_942_208, "the frozen correctness gate count changed")
    require(CONFIDENCE_INTERVAL_COUNT == 196_611, "the frozen confidence interval count changed")
    fixed_nonproduction_key = bytes(range(32))
    digest = hashlib.sha256()
    smoke_cases = 0
    for family_index in range(FAMILY_COUNT):
        for stratum_index in range(STRATUM_COUNT):
            for variant in (0, VARIANTS_PER_STRATUM - 1):
                case = fresh_case(fixed_nonproduction_key, family_index, stratum_index, variant)
                require(
                    case == fresh_case(fixed_nonproduction_key, family_index, stratum_index, variant),
                    "fixed-key fresh case generation is not deterministic",
                )
                pattern = decoded_wire(case["pattern"])
                require(isinstance(pattern, (str, bytes)), "a fresh pattern has an invalid type")
                standard_re.compile(pattern, case["flags"])
                subject = decoded_wire(case["subject"])
                require(
                    isinstance(subject, (str, bytes, bytearray, memoryview)),
                    "a fresh subject has an invalid type",
                )
                digest.update(canonical(case))
                smoke_cases += 1
    ensure_candidate_free()
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS",
        "candidate_imported": False,
        "production_entropy_drawn": False,
        "guard_created": False,
        "production_cases_materialized": 0,
        "fixed_key_smoke_cases": smoke_cases,
        "fixed_key_smoke_sha256": digest.hexdigest(),
        "semantic_families": FAMILY_COUNT,
        "strata_per_family": STRATUM_COUNT,
        "variants_per_stratum": VARIANTS_PER_STRATUM,
        "prospective_cases": CASE_COUNT,
        "prospective_raw_observations": RAW_OBSERVATION_COUNT,
        "prospective_correctness_gates": CORRECTNESS_GATE_COUNT,
        "prospective_confidence_intervals": CONFIDENCE_INTERVAL_COUNT,
        "historical_holdout_accessed": False,
        "benchmark_or_timing_executed": False,
    }


@dataclass(frozen=True)
class FreezeConfiguration:
    manifest: Path
    guard: Path
    public_runner: Path
    guard_source: Path
    guard_report: Path
    public_oracle: Path
    oracle_proof: Path
    additional_proofs: tuple[Path, ...]


def configured(arguments: argparse.Namespace) -> FreezeConfiguration:
    return FreezeConfiguration(
        manifest=destination(arguments.manifest, purpose="prospective manifest"),
        guard=destination(arguments.guard, purpose="one-use guard"),
        public_runner=arguments.public_runner,
        guard_source=arguments.guard_source,
        guard_report=arguments.guard_report,
        public_oracle=arguments.public_oracle,
        oracle_proof=arguments.oracle_proof,
        additional_proofs=tuple(arguments.proof),
    )


def input_records(configuration: FreezeConfiguration) -> dict[str, dict[str, Any]]:
    specifications: list[tuple[str, Path, int]] = [
        ("fresh-generator", RUNNER_PATH, MAX_SOURCE_BYTES),
        ("fresh-protocol", PROTOCOL_PATH, MAX_SOURCE_BYTES),
        ("public-runner", configuration.public_runner, MAX_SOURCE_BYTES),
        ("no-delegation-audit-source", configuration.guard_source, MAX_SOURCE_BYTES),
        ("no-delegation-audit-proof", configuration.guard_report, MAX_JSON_BYTES),
        ("from-scratch-audit-source", DEFAULT_BASE_AUDIT_SOURCE, MAX_SOURCE_BYTES),
        ("from-scratch-audit-proof", DEFAULT_BASE_AUDIT_REPORT, MAX_JSON_BYTES),
        ("public-oracle-source", configuration.public_oracle, MAX_SOURCE_BYTES),
        ("public-oracle-proof", configuration.oracle_proof, MAX_JSON_BYTES),
        ("public-oracle-campaign-source", ROOT / "tools" / "rust_postfinal_quote_parity_stage03_oracle.py", MAX_SOURCE_BYTES),
        ("public-practice-campaign-source", ROOT / "tools" / "postfinal_public_practice_v3.py", MAX_SOURCE_BYTES),
        ("project-manifest", ROOT / "pyproject.toml", MAX_SOURCE_BYTES),
        ("rust-manifest", ROOT / "candidates" / "rust" / "Cargo.toml", MAX_SOURCE_BYTES),
        ("rust-lockfile", ROOT / "candidates" / "rust" / "Cargo.lock", MAX_SOURCE_BYTES),
    ]
    for family, relative in sorted(PYTHON_SOURCE_PATHS.items()):
        specifications.append((f"{family}-python-source", ROOT / relative, MAX_SOURCE_BYTES))
    for family, paths in sorted(NATIVE_SOURCE_PATHS.items()):
        for relative in paths:
            specifications.append((f"{family}-native-source", ROOT / relative, MAX_SOURCE_BYTES))
    for (family, role), relative in sorted(NATIVE_BINARY_PATHS.items()):
        specifications.append((f"{family}-{role}-native-binary", ROOT / relative, MAX_BINARY_BYTES))
    for proof in configuration.additional_proofs:
        specifications.append(("additional-public-proof", proof, MAX_JSON_BYTES))

    records: dict[str, dict[str, Any]] = {}
    for role, path, maximum in specifications:
        resolved, relative = safe_repository_file(path)
        data = read_bounded(resolved, maximum)
        previous = records.get(relative)
        if previous is None:
            records[relative] = {
                "path": relative,
                "sha256": sha256_bytes(data),
                "bytes": len(data),
                "roles": [role],
            }
        else:
            require(previous["sha256"] == sha256_bytes(data), "a frozen file changed while being read")
            previous["roles"].append(role)
    for record in records.values():
        record["roles"].sort()
    return records


def verify_original_audit(records: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    report, _ = load_document(DEFAULT_BASE_AUDIT_REPORT)
    require(
        report.get("schema_version") == 1
        and report.get("audit") == "bounded-from-scratch-engine-provenance"
        and report.get("passed") is True
        and report.get("result") == "PASS",
        "the frozen original from-scratch audit is not an exact PASS",
    )
    tests = report.get("self_test")
    require(
        isinstance(tests, dict)
        and tests.get("passed") is True
        and tests.get("check_count") == 76
        and isinstance(tests.get("checks"), list)
        and len(tests["checks"]) == 76
        and all(isinstance(row, dict) and row.get("passed") is True for row in tests["checks"]),
        "the frozen original audit does not contain all 76 passing controls",
    )
    native = report.get("native_elf_provenance")
    require(
        isinstance(native, dict)
        and native.get("passed") is True
        and native.get("audited_binary_count") == 5,
        "the frozen original audit does not verify all five native artifacts",
    )
    native_families = native.get("families")
    require(
        isinstance(native_families, dict),
        "the frozen original audit omitted its native artifact families",
    )
    require(
        isinstance(report.get("runtime_native_mapping_provenance"), dict)
        and report["runtime_native_mapping_provenance"].get("passed") is True,
        "the original audit does not attest actual isolated native mappings",
    )
    families = report.get("families")
    require(isinstance(families, dict), "the original audit omitted engine families")
    for family in CANDIDATE_FAMILIES:
        evidence = families.get(family)
        require(
            isinstance(evidence, dict)
            and evidence.get("passed") is True
            and isinstance(evidence.get("isolated_runtime"), dict)
            and evidence["isolated_runtime"].get("passed") is True,
            f"the original audit did not independently verify {family}",
        )
        python = evidence.get("python_source")
        python_path = PYTHON_SOURCE_PATHS[family]
        require(
            isinstance(python, dict)
            and python.get("file") == python_path
            and python.get("sha256") == records[python_path]["sha256"],
            f"the audited {family} Python source no longer matches its freeze",
        )
        observed_native = {
            row.get("file"): row
            for row in evidence.get("native_sources", ())
            if isinstance(row, dict)
        }
        for relative in NATIVE_SOURCE_PATHS[family]:
            item = observed_native.get(relative)
            require(
                isinstance(item, dict)
                and item.get("passed") is True
                and item.get("sha256") == records[relative]["sha256"],
                f"the audited {family} native source no longer matches: {relative}",
            )
        family_elf = native_families.get(family)
        require(
            isinstance(family_elf, dict) and family_elf.get("passed") is True,
            f"the audited {family} ELF failed",
        )
        family_files = family_elf.get("files")
        require(
            isinstance(family_files, dict),
            f"the audited {family} native artifact roles are missing",
        )
        for (owner, role), relative in NATIVE_BINARY_PATHS.items():
            if owner != family:
                continue
            item = family_files.get(role)
            require(
                isinstance(item, dict)
                and item.get("file") == relative
                and item.get("sha256") == records[relative]["sha256"],
                f"the audited {family}/{role} native binary no longer matches its freeze",
            )
    return report


def verify_guard_audit(
    configuration: FreezeConfiguration,
    records: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    report, _ = load_document(configuration.guard_report)
    source_relative = safe_repository_file(configuration.guard_source)[1]
    base_relative = safe_repository_file(DEFAULT_BASE_AUDIT_REPORT)[1]
    base_source_relative = safe_repository_file(DEFAULT_BASE_AUDIT_SOURCE)[1]
    require(
        report.get("schema") == GUARD_AUDIT_SCHEMA
        and report.get("passed") is True
        and report.get("result") == "PASS",
        "the frozen persistent no-delegation audit is not an exact PASS",
    )
    require(
        report.get("audit_source_path") == source_relative
        and report.get("audit_source_sha256") == records[source_relative]["sha256"]
        and report.get("base_audit_source_path") == base_source_relative
        and report.get("base_audit_source_sha256") == records[base_source_relative]["sha256"]
        and report.get("base_audit_report_path") == base_relative
        and report.get("base_audit_report_sha256") == records[base_relative]["sha256"],
        "the no-delegation proof is not bound to the exact frozen audit sources",
    )
    tests = report.get("self_test")
    require(
        isinstance(tests, dict)
        and tests.get("passed") is True
        and tests.get("check_count") == 32
        and isinstance(tests.get("checks"), list)
        and len(tests["checks"]) == 32
        and all(isinstance(row, dict) and row.get("passed") is True for row in tests["checks"])
        and report.get("inherited_control_count") == 76,
        "the no-delegation proof omitted a passing 32-control or 76-control gate",
    )
    graph = report.get("source_graph_provenance")
    require(
        isinstance(graph, dict)
        and graph.get("passed") is True
        and graph.get("implicit_rust_build_script_present") is False
        and graph.get("zig_build_manifest_present") is False,
        "the owned Rust/Zig source graph is not closed",
    )
    source_hashes = report.get("source_fingerprints")
    qualified_hashes = report.get("qualified_source_fingerprints")
    native_hashes = report.get("native_elf_fingerprints")
    require(
        isinstance(source_hashes, dict)
        and isinstance(qualified_hashes, dict)
        and isinstance(native_hashes, dict),
        "the no-delegation proof omitted exact source or native fingerprints",
    )
    for family in CANDIDATE_FAMILIES:
        for relative in (PYTHON_SOURCE_PATHS[family], *NATIVE_SOURCE_PATHS[family]):
            require(
                source_hashes.get(relative) == records[relative]["sha256"]
                and qualified_hashes.get(relative) == records[relative]["sha256"],
                f"the no-delegation source fingerprint changed: {relative}",
            )
    for owner_role, relative in NATIVE_BINARY_PATHS.items():
        require(
            native_hashes.get(GUARD_NATIVE_KEYS[owner_role])
            == records[relative]["sha256"],
            f"the no-delegation native fingerprint changed: {relative}",
        )
    families = report.get("families")
    require(
        isinstance(families, dict)
        and all(
            isinstance(families.get(name), dict)
            and families[name].get("passed") is True
            and isinstance(families[name].get("isolated_runtime"), dict)
            and families[name]["isolated_runtime"].get("passed") is True
            for name in CANDIDATE_FAMILIES
        ),
        "a frozen candidate does not have a continuously guarded isolated runtime",
    )
    scope = report.get("scope")
    require(
        isinstance(scope, dict)
        and scope.get("closed_owned_source_graph") is True
        and scope.get("persistent_measurement_worker_available") is True
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "the frozen worker audit has an unsafe or inapplicable scope",
    )
    return report


def verify_public_oracle(
    configuration: FreezeConfiguration,
    records: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    report, _ = load_document(configuration.oracle_proof)
    oracle_relative = safe_repository_file(configuration.public_oracle)[1]
    base_relative = safe_repository_file(DEFAULT_BASE_AUDIT_REPORT)[1]
    require(
        report.get("schema") == PUBLIC_ORACLE_SCHEMA
        and report.get("status") == "PASS"
        and report.get("selected") == "all"
        and report.get("selected_candidates") == list(CANDIDATE_FAMILIES)
        and report.get("cases") == 8192
        and report.get("observations_per_case") == 48
        and report.get("observations_per_candidate") == 393_216
        and report.get("total_comparisons") == 1_179_648
        and report.get("mismatches") == 0
        and report.get("performance_fixtures_read") == 0
        and report.get("holdout_cases_read") == 0
        and report.get("external_regex_packages") == 0
        and report.get("benchmark_or_timing_executed") is False,
        "the committed universal public correctness proof is not an all-candidate PASS",
    )
    audit = report.get("audit")
    require(
        isinstance(audit, dict)
        and audit.get("oracle_source_path") == oracle_relative
        and audit.get("oracle_source_sha256") == records[oracle_relative]["sha256"]
        and audit.get("audit_path") == base_relative
        and audit.get("audit_sha256") == records[base_relative]["sha256"]
        and audit.get("selected_candidates") == list(CANDIDATE_FAMILIES),
        "the public oracle proof is not source-bound to the frozen candidate audit",
    )
    original_campaign = audit.get("original_public_campaign")
    require(
        isinstance(original_campaign, dict),
        "the public oracle omitted its frozen source-only campaign bindings",
    )
    for label, relative in (
        ("quote-parity-stage-03", "tools/rust_postfinal_quote_parity_stage03_oracle.py"),
        ("public-practice-v3", "tools/postfinal_public_practice_v3.py"),
    ):
        evidence = original_campaign.get(label)
        require(
            isinstance(evidence, dict)
            and evidence.get("path") == relative
            and evidence.get("sha256") == records[relative]["sha256"],
            f"the universal oracle's public campaign source changed: {relative}",
        )
    source_hashes = audit.get("source_sha256")
    binary_hashes = audit.get("native_binary_sha256")
    reports = report.get("candidate_reports")
    require(
        isinstance(source_hashes, dict)
        and isinstance(binary_hashes, dict)
        and isinstance(reports, dict),
        "the public oracle proof omitted candidate source or binary provenance",
    )
    for family in CANDIDATE_FAMILIES:
        candidate = reports.get(family)
        require(
            isinstance(candidate, dict)
            and candidate.get("status") == "PASS"
            and candidate.get("cases") == 8192
            and candidate.get("checks") == 393_216
            and candidate.get("mismatches") == 0
            and candidate.get("holdout_cases_read") == 0
            and candidate.get("external_regex_packages") == 0
            and candidate.get("benchmark_or_timing_executed") is False,
            f"the public oracle did not completely validate {family}",
        )
        poison_guards = candidate.get("poison_guards")
        require(
            isinstance(poison_guards, dict)
            and len(poison_guards) == 7
            and all(value is True for value in poison_guards.values()),
            f"the public oracle omitted an isolated poison guard for {family}",
        )
        frozen_source = source_hashes.get(family)
        frozen_binary = binary_hashes.get(family)
        require(
            isinstance(frozen_source, dict) and isinstance(frozen_binary, dict),
            f"the public oracle omitted exact {family} artifacts",
        )
        for relative in (PYTHON_SOURCE_PATHS[family], *NATIVE_SOURCE_PATHS[family]):
            require(
                frozen_source.get(relative) == records[relative]["sha256"],
                f"the public oracle source fingerprint changed: {relative}",
            )
        for (owner, _role), relative in NATIVE_BINARY_PATHS.items():
            if owner == family:
                require(
                    frozen_binary.get(relative) == records[relative]["sha256"],
                    f"the public oracle native fingerprint changed: {relative}",
                )
    return report


def pinned_interpreter() -> dict[str, Any]:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == PINNED_VERSION
        and Path(sys.executable).resolve() == PINNED_PYTHON.resolve(strict=True)
        and sysconfig.get_config_var("SOABI") == PINNED_SOABI
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode,
        "freeze/open require the exact pinned CPython 3.14.6 invoked with -I -B",
    )
    try:
        with PINNED_PYTHON.open("rb") as stream:
            data = stream.read(MAX_BINARY_BYTES + 1)
    except OSError as error:
        raise HoldoutIntegrityError("the pinned interpreter cannot be fingerprinted") from error
    require(len(data) <= MAX_BINARY_BYTES, "the pinned interpreter exceeds its safe bound")
    return {
        "implementation": "cpython",
        "version": list(PINNED_VERSION),
        "executable": str(PINNED_PYTHON),
        "executable_sha256": sha256_bytes(data),
        "soabi": PINNED_SOABI,
        "isolated_mode": True,
        "bytecode_writes_disabled": True,
    }


def build_manifest(configuration: FreezeConfiguration) -> dict[str, Any]:
    ensure_candidate_free()
    interpreter = pinned_interpreter()
    records = input_records(configuration)
    verify_original_audit(records)
    verify_guard_audit(configuration, records)
    verify_public_oracle(configuration, records)
    require(CASE_COUNT == 65_536, "prospective case arithmetic changed")
    require(RAW_OBSERVATION_COUNT == 4_980_736, "prospective observation arithmetic changed")
    require(CORRECTNESS_GATE_COUNT == 14_942_208, "prospective correctness arithmetic changed")
    require(CONFIDENCE_INTERVAL_COUNT == 196_611, "prospective interval arithmetic changed")
    guard_relative = configuration.guard.relative_to(ROOT.resolve()).as_posix()
    manifest = {
        "schema": SCHEMA,
        "state": "prospective-distribution-only",
        "measurement_role": "fresh one-use holdout; never a public practice or historical holdout",
        "pinned_python": interpreter,
        "workers": {
            "baseline": BASELINE_FAMILY,
            "candidates": list(CANDIDATE_FAMILIES),
            "isolated_families": list(WORKER_FAMILIES),
            "guard_audit_schema": GUARD_AUDIT_SCHEMA,
            "public_oracle_schema": PUBLIC_ORACLE_SCHEMA,
            "secret_in_worker_argv_or_environment": False,
            "separate_persistent_process_per_family": True,
            "candidate_stdlib_regex_delegation_permitted": False,
            "cross_candidate_delegation_permitted": False,
            "mapped_native_fingerprint_verification_required": True,
            "source_to_binary_hermetic_reproducibility_attested": False,
        },
        "distribution": {
            "case_schema": CASE_SCHEMA,
            "families": [asdict(family) for family in FAMILIES],
            "family_count": FAMILY_COUNT,
            "strata": [stratum_descriptor(index) for index in range(STRATUM_COUNT)],
            "strata_per_family": STRATUM_COUNT,
            "variants_per_stratum": VARIANTS_PER_STRATUM,
            "case_count": CASE_COUNT,
            "variant_derivation": "HMAC-SHA256 over the frozen domain and binary family/stratum/variant indices",
            "hmac_domain_ascii": HMAC_DOMAIN.decode("ascii"),
            "production_key_bytes": 32,
            "production_key_source": "OS secrets.token_bytes after pushed-commit verification and durable exclusive guard",
            "cases_materialized_before_exclusive_guard": 0,
            "maximum_pattern_utf8_bytes": MAX_PATTERN_BYTES,
            "maximum_subject_utf8_bytes": MAX_SUBJECT_BYTES,
            "maximum_matches_per_case": MAX_MATCHES,
            "maximum_operations_per_trial": MAX_OPERATIONS_PER_TRIAL,
        },
        "measurement": {
            "shuffled_paired_trials": TRIAL_COUNT,
            "participants_per_trial": len(WORKER_FAMILIES),
            "raw_observations": RAW_OBSERVATION_COUNT,
            "correctness_channels": list(CORRECTNESS_CHANNELS),
            "candidate_correctness_gates": CORRECTNESS_GATE_COUNT,
            "bootstrap_samples_per_interval": BOOTSTRAP_SAMPLES,
            "per_case_candidate_intervals": CASE_COUNT * len(CANDIDATE_FAMILIES),
            "aggregate_candidate_intervals": len(CANDIDATE_FAMILIES),
            "confidence_intervals": CONFIDENCE_INTERVAL_COUNT,
            "pair_order": "independently HMAC-derived, shuffled four-family order for each case and trial",
            "ipc_and_correctness_checks_inside_timed_region": False,
            "python_tracemalloc_peak_label": "Python-visible traced allocations only; excludes native engine allocations",
            "worker_rss_high_water_label": "whole isolated worker resident-set high-water; not exact per-case native allocation",
        },
        "fingerprints": [records[path] for path in sorted(records)],
        "git": {
            "manifest_must_be_tracked_in_frozen_commit": True,
            "all_fingerprints_must_match_worktree_and_HEAD_blobs": True,
            "head_must_equal_configured_upstream_and_live_remote": True,
            "freeze_commit_is_recorded_in_exclusive_guard": True,
        },
        "one_use": {
            "guard_path": guard_relative,
            "create_flags": "O_CREAT|O_EXCL|O_NOFOLLOW",
            "mode": "0600",
            "guard_fsync_before_entropy": True,
            "parent_directory_fsync_before_entropy": True,
            "append_only_events": True,
            "failed_guard_is_permanently_poisoned": True,
            "overwrite_or_reuse_permitted": False,
            "external_user_secret_required": False,
        },
        "executor": {
            "state": "not-implemented-fail-closed",
            "public_worker_checks_per_observation": 3,
            "required_observable_correctness_channels": len(CORRECTNESS_CHANNELS),
            "opening_permitted": False,
            "reason": (
                "The frozen public v4 worker exposes three timed correctness checks; "
                "no committed holdout adapter yet establishes all four independently "
                "specified observable-equivalence channels in isolated workers."
            ),
        },
        "historical_holdout_or_final_inputs": "never-read-never-required",
    }
    ensure_candidate_free()
    return manifest


def git_output(arguments: list[str], *, maximum: int = MAX_GIT_RESPONSE_BYTES) -> bytes:
    command = ["git", "-C", str(ROOT), *arguments]
    environment = dict(os.environ)
    environment["GIT_TERMINAL_PROMPT"] = "0"
    try:
        process = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=60,
            env=environment,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise HoldoutIntegrityError("cannot verify the prospective frozen Git state") from error
    require(
        len(process.stdout) <= maximum and len(process.stderr) <= MAX_GIT_RESPONSE_BYTES,
        "prospective Git verification exceeded its bounded response",
    )
    require(process.returncode == 0, f"prospective Git verification failed: {' '.join(arguments)}")
    return process.stdout


def git_text(arguments: list[str]) -> str:
    try:
        value = git_output(arguments).decode("utf-8").strip()
    except UnicodeError as error:
        raise HoldoutIntegrityError("frozen Git verification returned invalid text") from error
    require(bool(value), f"frozen Git verification returned no value: {' '.join(arguments)}")
    return value


def verify_frozen_remote(configuration: FreezeConfiguration) -> str:
    root = Path(git_text(["rev-parse", "--show-toplevel"])).resolve()
    require(root == ROOT.resolve(), "prospective Git root does not match the workspace")
    head = git_text(["rev-parse", "HEAD"])
    require(len(head) == 40 and all(item in "0123456789abcdef" for item in head), "invalid frozen Git commit")
    branch = git_text(["symbolic-ref", "--quiet", "--short", "HEAD"])
    remote = git_text(["config", "--get", f"branch.{branch}.remote"])
    merge_ref = git_text(["config", "--get", f"branch.{branch}.merge"])
    require(merge_ref.startswith("refs/heads/"), "the frozen branch has no exact remote branch")
    require(git_text(["rev-parse", "@{upstream}"]) == head, "the frozen commit is not the local upstream")
    remote_rows = git_output(["ls-remote", "--exit-code", remote, merge_ref]).decode("ascii").splitlines()
    require(
        len(remote_rows) == 1
        and remote_rows[0].split("\t") == [head, merge_ref],
        "the exact frozen commit has not been independently confirmed on the remote",
    )
    changes = git_output(["status", "--porcelain=v1", "--untracked-files=normal", "-z"])
    guard_relative = configuration.guard.relative_to(ROOT.resolve()).as_posix()
    expected_guard = b"?? " + os.fsencode(guard_relative)
    for row in changes.split(b"\0"):
        if not row:
            continue
        require(row == expected_guard, "the frozen workspace contains an uncommitted or untracked change")
    return head


def git_blob_fingerprint(head: str, relative: str, maximum: int) -> tuple[str, int]:
    object_name = f"{head}:{relative}"
    size_text = git_text(["cat-file", "-s", object_name])
    require(size_text.isascii() and size_text.isdecimal(), "a frozen Git blob has an invalid size")
    size = int(size_text)
    require(size <= maximum, f"a frozen Git blob exceeds its safe bound: {relative}")
    data = git_output(["cat-file", "blob", object_name], maximum=maximum)
    require(len(data) == size, f"a frozen Git blob changed while being verified: {relative}")
    return sha256_bytes(data), size


def verify_committed_manifest(
    configuration: FreezeConfiguration,
    manifest: Mapping[str, Any],
) -> tuple[str, str]:
    expected = build_manifest(configuration)
    expected_bytes = canonical(expected)
    actual = read_bounded(configuration.manifest, MAX_JSON_BYTES)
    require(actual == expected_bytes, "the prospectively frozen manifest or an audited input changed")
    require(canonical(manifest) == expected_bytes, "the in-memory frozen manifest is inconsistent")
    head = verify_frozen_remote(configuration)
    for record in expected["fingerprints"]:
        relative = record["path"]
        maximum = MAX_BINARY_BYTES if "-native-binary" in " ".join(record["roles"]) else MAX_JSON_BYTES
        digest, size = git_blob_fingerprint(head, relative, maximum)
        require(
            digest == record["sha256"] and size == record["bytes"],
            f"a frozen source, binary, proof, or audit is not committed at HEAD: {relative}",
        )
    manifest_relative = configuration.manifest.relative_to(ROOT.resolve()).as_posix()
    digest, size = git_blob_fingerprint(head, manifest_relative, MAX_JSON_BYTES)
    require(
        digest == sha256_bytes(expected_bytes) and size == len(expected_bytes),
        "the exact prospective manifest has not been committed and pushed",
    )
    ensure_candidate_free()
    return head, sha256_bytes(expected_bytes)


def write_all(descriptor: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        written = os.write(descriptor, view)
        require(written > 0, "an exclusive prospective write made no progress")
        view = view[written:]


def fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def exclusive_write(path: Path, payload: bytes) -> None:
    flags = (
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = os.open(path, flags, 0o600)
    except FileExistsError as error:
        raise HoldoutIntegrityError("refusing to overwrite an existing prospective freeze file") from error
    try:
        write_all(descriptor, payload)
        os.fsync(descriptor)
        fsync_directory(path.parent)
    finally:
        os.close(descriptor)


def append_guard_failure(descriptor: int, message: str) -> None:
    try:
        write_all(
            descriptor,
            canonical({"event": "poisoned", "schema": SCHEMA, "reason": message}),
        )
        os.fsync(descriptor)
    except (HoldoutIntegrityError, OSError, ValueError):
        pass


def seal_one_use_guard(
    configuration: FreezeConfiguration,
    manifest: Mapping[str, Any],
    head: str,
    manifest_sha256: str,
) -> None:
    flags = (
        os.O_WRONLY | os.O_CREAT | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = os.open(configuration.guard, flags, 0o600)
    except FileExistsError as error:
        raise HoldoutIntegrityError(
            "the one-use guard already exists; a sealed or poisoned holdout can never be recreated"
        ) from error
    completed = False
    try:
        armed = {
            "event": "armed-before-entropy",
            "schema": SCHEMA,
            "frozen_commit": head,
            "manifest_sha256": manifest_sha256,
        }
        write_all(descriptor, canonical(armed))
        os.fsync(descriptor)
        fsync_directory(configuration.guard.parent)

        rechecked_head, rechecked_manifest = verify_committed_manifest(configuration, manifest)
        require(
            rechecked_head == head and rechecked_manifest == manifest_sha256,
            "the committed freeze changed after the durable guard and before entropy",
        )

        # This is the only production randomness in the complete protocol.
        # It is intentionally unreachable until the exclusive guard and its
        # parent directory are durable and the exact pushed freeze is rechecked.
        production_key = secrets.token_bytes(32)
        require(len(production_key) == 32, "the operating system returned an invalid fresh key")
        sealed = {
            "event": "sealed-after-durable-guard",
            "schema": SCHEMA,
            "frozen_commit": head,
            "manifest_sha256": manifest_sha256,
            "production_key_sha256": sha256_bytes(production_key),
        }
        secret = {
            "event": "private-production-key",
            "schema": SCHEMA,
            "key_hex": production_key.hex(),
        }
        write_all(descriptor, canonical(sealed) + canonical(secret))
        os.fsync(descriptor)
        fsync_directory(configuration.guard.parent)
        completed = True
    except BaseException:
        if not completed:
            append_guard_failure(descriptor, "freeze interrupted; this guard is permanently one-use")
            try:
                fsync_directory(configuration.guard.parent)
            except OSError:
                pass
        raise
    finally:
        os.close(descriptor)


def read_guard_public_events(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise HoldoutIntegrityError("the exclusively sealed one-use guard is absent") from error
    try:
        metadata = os.fstat(descriptor)
        require(stat.S_ISREG(metadata.st_mode), "the one-use guard is not a regular file")
        require(metadata.st_mode & 0o077 == 0, "the one-use guard is not private mode 0600")
        values: list[dict[str, Any]] = []
        for _ in range(2):
            line = bytearray()
            while len(line) <= MAX_GUARD_LINE_BYTES:
                character = os.read(descriptor, 1)
                require(bool(character), "the one-use guard was poisoned or incompletely sealed")
                line.extend(character)
                if character == b"\n":
                    break
            require(len(line) <= MAX_GUARD_LINE_BYTES, "a public guard event exceeds its bound")
            try:
                event = json.loads(line)
            except (UnicodeError, ValueError) as error:
                raise HoldoutIntegrityError("a public one-use guard event is invalid") from error
            require(isinstance(event, dict), "a public one-use guard event is not an object")
            values.append(event)
        require(values[0].get("event") == "armed-before-entropy", "the guard was not durably armed")
        require(values[1].get("event") == "sealed-after-durable-guard", "the guard was poisoned or not sealed")
        require(
            values[0].get("schema") == SCHEMA and values[1].get("schema") == SCHEMA,
            "the one-use guard belongs to a different protocol",
        )
        return values[0], values[1]
    finally:
        os.close(descriptor)


def freeze(configuration: FreezeConfiguration) -> dict[str, Any]:
    ensure_candidate_free()
    manifest = build_manifest(configuration)
    payload = canonical(manifest)
    if not configuration.manifest.exists():
        exclusive_write(configuration.manifest, payload)
        ensure_candidate_free()
        return {
            "schema": SCHEMA,
            "status": "PROSPECTIVE_MANIFEST_PREPARED",
            "manifest": configuration.manifest.relative_to(ROOT.resolve()).as_posix(),
            "manifest_sha256": sha256_bytes(payload),
            "action_required": (
                "commit and push this exact manifest, generator, protocol, public proofs, "
                "audit reports, worker sources, candidate sources, and all five binaries; "
                "then invoke the identical freeze command once more"
            ),
            "production_entropy_drawn": False,
            "guard_created": False,
            "production_cases_materialized": 0,
            "historical_holdout_accessed": False,
        }
    actual = read_bounded(configuration.manifest, MAX_JSON_BYTES)
    require(actual == payload, "refusing to overwrite or reinterpret a different prospective manifest")
    head, manifest_digest = verify_committed_manifest(configuration, manifest)
    seal_one_use_guard(configuration, manifest, head, manifest_digest)
    ensure_candidate_free()
    return {
        "schema": SCHEMA,
        "status": "PROSPECTIVE_FREEZE_SEALED",
        "frozen_commit": head,
        "manifest": configuration.manifest.relative_to(ROOT.resolve()).as_posix(),
        "manifest_sha256": manifest_digest,
        "guard": configuration.guard.relative_to(ROOT.resolve()).as_posix(),
        "guard_created": True,
        "production_entropy_drawn_after_durable_guard": True,
        "production_cases_materialized": 0,
        "executor": "NOT_IMPLEMENTED_FAIL_CLOSED",
        "historical_holdout_accessed": False,
    }


def open_holdout(configuration: FreezeConfiguration, *, affirm_one_use: bool) -> dict[str, Any]:
    ensure_candidate_free()
    require(
        affirm_one_use,
        "opening is irreversible and requires the explicit --affirm-one-use flag",
    )
    manifest, raw = load_document(configuration.manifest)
    require(raw == canonical(manifest), "the committed holdout manifest is not canonical")
    head, manifest_digest = verify_committed_manifest(configuration, manifest)
    armed, sealed = read_guard_public_events(configuration.guard)
    for event in (armed, sealed):
        require(
            event.get("frozen_commit") == head
            and event.get("manifest_sha256") == manifest_digest,
            "the one-use guard is not bound to the exact remotely frozen manifest",
        )
    executor = manifest.get("executor")
    require(
        isinstance(executor, dict)
        and executor.get("state") == "not-implemented-fail-closed"
        and executor.get("public_worker_checks_per_observation") == 3
        and executor.get("required_observable_correctness_channels") == 4
        and executor.get("opening_permitted") is False,
        "the frozen holdout executor contract was modified or falsely declared complete",
    )
    # Do not read the private third guard event, derive a production case,
    # import a candidate, spawn a worker, take a timing, or claim a result.
    raise HoldoutIntegrityError(
        "FRESH HOLDOUT NOT OPENED: the frozen public worker provides three "
        "checks, but the prospective 14,942,208-gate protocol requires four "
        "independent observable-equivalence channels. A committed, separately "
        "audited isolated holdout adapter and streaming standard-library "
        "oracle do not yet exist. The private key was not read, no fresh case "
        "was generated, and the exclusive one-use guard was preserved."
    )


def parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser(description=__doc__)
    commands = argument_parser.add_subparsers(dest="command", required=True)
    commands.add_parser("self-test", help="exercise fixed-key, candidate-free distribution controls only")
    for name in ("freeze", "open"):
        command = commands.add_parser(name)
        command.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
        command.add_argument("--guard", type=Path, default=DEFAULT_GUARD)
        command.add_argument("--public-runner", type=Path, default=DEFAULT_PUBLIC_RUNNER)
        command.add_argument("--guard-source", type=Path, default=DEFAULT_GUARD_SOURCE)
        command.add_argument("--guard-report", type=Path, default=DEFAULT_GUARD_REPORT)
        command.add_argument("--public-oracle", type=Path, default=DEFAULT_PUBLIC_ORACLE)
        command.add_argument("--oracle-proof", type=Path, default=DEFAULT_ORACLE_PROOF)
        command.add_argument("--proof", type=Path, action="append", default=[])
        if name == "open":
            command.add_argument("--affirm-one-use", action="store_true")
    return argument_parser


def main(arguments: list[str] | None = None) -> int:
    parsed = parser().parse_args(arguments)
    try:
        ensure_candidate_free()
        if parsed.command == "self-test":
            result = candidate_free_self_test()
        elif parsed.command == "freeze":
            result = freeze(configured(parsed))
        else:
            result = open_holdout(
                configured(parsed),
                affirm_one_use=parsed.affirm_one_use,
            )
        sys.stdout.buffer.write(canonical(result))
        return 0
    except (
        HoldoutIntegrityError,
        OSError,
        ValueError,
        TypeError,
        KeyError,
        subprocess.SubprocessError,
    ) as error:
        sys.stdout.buffer.write(
            canonical({
                "schema": SCHEMA,
                "status": "FAIL_CLOSED",
                "error": str(error),
                "candidate_imported": False,
                "historical_holdout_accessed": False,
            })
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
