#!/usr/bin/env python3
"""Fresh, bounded, public-only CPython 3.14 regular-expression differential.

Exactly 16 independent grammar families, 16 materialized input strata and 32
domain-separated examples produce 8,192 cases. Every case has exactly 48
aligned public observations. CPython re and each selected audited native
candidate execute in distinct pinned processes. No archived cases, held-out
input, performance fixture, clock, or external regular-expression package is
used. The candidate-free self-test uses in-memory synthetic controls only.
"""

from __future__ import annotations

import argparse
import array
import ast
import builtins
import collections
import copy
import ctypes
import hashlib
import importlib
import json
import locale
import os
import random
import subprocess
import sys
import warnings
from pathlib import Path
from typing import Any, Callable


SCHEMA = "rebar-python-re-universal-public-oracle-v1"
SEED = 2026072417
SEED_DOMAIN = "rebar/python-re/universal-public/v1"
PINNED_VERSION = (3, 14, 6)
PINNED_EXECUTABLE = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
ROOT = Path(__file__).resolve().parent.parent
RUNNER = Path(__file__).resolve()
AUDIT_PATH = ROOT / "candidates" / "audits" / "FROM-SCRATCH-AUDIT.json"
EVIDENCE_ROOT = ROOT / "candidates" / "evidence"
EXAMPLES_PER_STRATUM = 32
OBSERVATIONS_PER_CASE = 48
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_BINARY_BYTES = 64 * 1024 * 1024
MAX_AUDIT_BYTES = 8 * 1024 * 1024
MAX_MAP_BYTES = 4 * 1024 * 1024
MAX_WORKER_LINE_BYTES = 1024 * 1024
MAX_WORKER_STDERR_BYTES = 1024 * 1024
MAX_MISMATCH_EXAMPLES = 256
MAX_SUBJECT_CHARACTERS = 96
MAX_PATTERN_CHARACTERS = 192
MAX_RESULTS = 128
HASH_CHUNK_BYTES = 1024 * 1024
IGNORECASE = 2
LOCALE = 4
MULTILINE = 8
DOTALL = 16
UNICODE = 32
VERBOSE = 64
ASCII = 256

GRAMMAR_FAMILIES = (
    "literal-escape",
    "alternation-nullable",
    "character-class-range",
    "category-ascii-locale",
    "global-scoped-flags",
    "unicode-case-fold",
    "anchors-newline",
    "greedy-lazy-possessive",
    "atomic-backtracking",
    "capture-backreference",
    "lookahead",
    "fixed-lookbehind",
    "conditional-rollback",
    "quote-parity",
    "invalid-grammar-flags",
    "replacement-zero-width",
)
INPUT_STRATA = (
    "str-kind1",
    "str-kind2",
    "str-kind4",
    "str-subclass",
    "bytes",
    "bytes-subclass",
    "bytearray",
    "readonly-memoryview",
    "writable-memoryview",
    "cast-memoryview",
    "noncontiguous-memoryview",
    "released-memoryview",
    "array-B",
    "str-pattern-binary-subject",
    "bytes-pattern-str-subject",
    "newline-text",
)
EXTENSION_OPERATIONS = (
    "module-search",
    "module-match",
    "module-fullmatch",
    "module-findall",
    "module-finditer",
    "module-sub-template",
    "module-subn-template",
    "bound-sub-template",
    "bound-subn-template",
    "module-sub-callback",
    "module-subn-callback",
    "bound-sub-callback",
    "bound-subn-callback",
    "module-escape",
    "match-surface",
    "match-expand",
    "pattern-copy",
    "pattern-deepcopy",
    "warning-positional-split",
    "module-purge-recompile",
    "pattern-metadata",
    "malicious-window-index",
    "finditer-exhaustion",
    "scanner-exhaustion",
)
EXPECTED_CASES = (
    len(GRAMMAR_FAMILIES) * len(INPUT_STRATA) * EXAMPLES_PER_STRATUM
)
EXPECTED_OBSERVATIONS = EXPECTED_CASES * OBSERVATIONS_PER_CASE
CAMPAIGN_SOURCES = {
    "quote-parity-stage-03": {
        "path": "tools/rust_postfinal_quote_parity_stage03_oracle.py",
        "constants": {
            "SCHEMA": "rebar-rust-postfinal-quote-parity-oracle-v3",
            "SEED": 0x52454241525F515032,
            "PINNED_VERSION": PINNED_VERSION,
            "MAX_OBSERVATIONS": 100_000,
        },
    },
    "public-practice-v3": {
        "path": "tools/postfinal_public_practice_v3.py",
        "constants": {
            "VERSION": "postfinal-public-practice-v3",
            "CASES": 4_096,
            "FIXTURE_CASES": 10_312,
            "ELIGIBLE_CASES": 9_731,
            "CATEGORIES": 260,
            "PUBLIC_APIS": 12,
            "SELECTION_SEED": 2026072401,
            "ORDER_SEED": 2026072402,
            "BOOTSTRAP_SEED": 2026072403,
        },
    },
}
CANDIDATES = {
    "rust": {
        "module": "candidates.rust_candidate",
        "native_module": "candidates._rust_bridge",
        "sources": (
            "candidates/rust_candidate.py",
            "candidates/rust/py_bridge.c",
            "candidates/rust/src/lib.rs",
            "candidates/rust/src/search.rs",
            "candidates/rust/src/newline.rs",
            "candidates/rust/src/stack.rs",
            "candidates/rust/src/unicode_tables.rs",
        ),
        "binaries": {
            "bridge": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
            "engine": "candidates/_rust_engine.so",
        },
        "pipeline": {
            "parser": "rust::Parser",
            "compiler": "rust::Compiler",
            "executor": "rust::run_program",
        },
    },
    "vm": {
        "module": "candidates.vm_candidate",
        "native_module": "candidates._vm_native",
        "sources": (
            "candidates/vm_candidate.py",
            "candidates/_vm_native.c",
        ),
        "binaries": {
            "native": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        },
        "pipeline": {
            "parser": "_BytecodeParser",
            "compiler": "_BytecodeCompiler",
            "executor": "candidates/_vm_native.c:execute",
        },
    },
    "zig": {
        "module": "candidates.zig_candidate",
        "native_module": "candidates._zig_bridge",
        "sources": (
            "candidates/zig_candidate.py",
            "candidates/zig/py_bridge.c",
            "candidates/zig/mini_regex.zig",
        ),
        "binaries": {
            "bridge": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
            "engine": "candidates/_zig_probe.so",
        },
        "pipeline": {
            "parser": "zig::Parser",
            "compiler": "zig::Compiler",
            "executor": "zig::runBytecode/runCapturedAt",
        },
    },
}
REGEX_ENGINE_ROOTS = frozenset({
    "re", "_sre", "sre", "sre_compile", "sre_parse", "sre_constants",
    "regex", "_regex", "regex_lite", "regex_automata", "regex_syntax",
    "fancy_regex", "re2", "pyre2", "pcre", "pcre2", "onig",
    "oniguruma", "onigurumacffi", "_onigurumacffi", "hyperscan",
    "aho_corasick",
})


class OracleIntegrityError(RuntimeError):
    """Exact pinned provenance, bounded worker, or public evidence failed."""


class WorkerExecutionError(OracleIntegrityError):
    """Preserve a bounded isolated worker exit and its actual diagnostics."""

    def __init__(
        self,
        label: str,
        reason: str,
        *,
        exit_code: int | None,
        stderr: str,
        stderr_truncated: bool,
    ) -> None:
        super().__init__(
            f"isolated {label} {reason}; exit_code={exit_code!r}; "
            f"stderr={stderr[-4000:]!r}"
        )
        self.label = label
        self.reason = reason
        self.exit_code = exit_code
        self.stderr = stderr
        self.stderr_truncated = stderr_truncated

    def evidence(self) -> dict[str, Any]:
        return {
            "class": type(self).__name__,
            "label": self.label,
            "reason": self.reason,
            "exit_code": self.exit_code,
            "stderr": self.stderr,
            "stderr_truncated": self.stderr_truncated,
            "maximum_stderr_bytes": MAX_WORKER_STDERR_BYTES,
        }


class PublicCallbackError(Exception):
    """Deterministic exception deliberately raised by a public callback."""


class PublicIndexError(Exception):
    """Deterministic exception deliberately raised by a public index."""


class TextSubclass(str):
    """Public, deterministic text-subclass input."""


class BytesSubclass(bytes):
    """Public, deterministic bytes-subclass input."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise OracleIntegrityError(message)


def canonical(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def normalize(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, str):
        if type(value) is str:
            return value
        return {"kind": type(value).__name__, "text": str(value)}
    if isinstance(value, (bytes, bytearray)):
        return {"kind": type(value).__name__, "hex": bytes(value).hex()}
    if isinstance(value, array.array):
        return {
            "kind": "array",
            "typecode": value.typecode,
            "hex": value.tobytes().hex(),
        }
    if isinstance(value, memoryview):
        try:
            return {
                "kind": "memoryview",
                "hex": value.tobytes().hex(),
                "format": value.format,
                "shape": normalize(value.shape),
                "strides": normalize(value.strides),
                "readonly": value.readonly,
                "c_contiguous": value.c_contiguous,
            }
        except ValueError:
            return {"kind": "memoryview", "released": True}
    if isinstance(value, tuple):
        return {"tuple": [normalize(item) for item in value]}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): normalize(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    raise OracleIntegrityError(
        f"nonportable documented observation type: {type(value).__name__}"
    )


def value_digest(value: Any) -> str:
    return hashlib.sha256(canonical(normalize(value)).encode("ascii")).hexdigest()


def sha256_path(path: Path, maximum: int) -> str:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while True:
            block = stream.read(HASH_CHUNK_BYTES)
            if not block:
                break
            size += len(block)
            require(size <= maximum, f"authorized source or binary exceeds its bound: {path.name}")
            digest.update(block)
    return digest.hexdigest()


def candidate_free() -> None:
    loaded = sorted(
        name
        for name in sys.modules
        if name.startswith("candidates.")
        and (
            name.endswith("_candidate")
            or "._rust_bridge" in name
            or "._zig_bridge" in name
            or "._vm_native" in name
        )
    )
    require(not loaded, f"candidate-free operation imported a production engine: {loaded!r}")


def require_pinned_runtime() -> None:
    require(sys.implementation.name == "cpython", "requires genuine pinned CPython")
    require(tuple(sys.version_info[:3]) == PINNED_VERSION, "requires exact CPython 3.14.6")
    require(
        Path(sys.executable).name == "python3.14"
        and Path(sys.executable).resolve() == PINNED_EXECUTABLE.resolve(),
        "requires the original exact pinned python3.14 executable",
    )


def selected_candidates(value: str) -> tuple[str, ...]:
    if value == "all":
        return ("rust", "vm", "zig")
    require(value in CANDIDATES, "unknown independently audited candidate")
    return (value,)


def default_output(candidate: str) -> Path:
    return EVIDENCE_ROOT / f"python-re-universal-public-oracle-v1-{candidate}.json"


def validate_output(value: Path, candidate: str) -> Path:
    resolved = value.resolve()
    require(
        resolved == default_output(candidate).resolve(),
        "output must use its exact candidate-specific universal-public evidence path",
    )
    require(
        resolved.parent == EVIDENCE_ROOT.resolve(),
        "universal-public evidence escaped candidates/evidence",
    )
    return resolved


def source_constants(data: bytes, path: str) -> dict[str, Any]:
    try:
        tree = ast.parse(data.decode("utf-8"), filename=path)
    except (SyntaxError, UnicodeError) as error:
        raise OracleIntegrityError(
            f"an original public campaign source cannot be independently parsed: {path}"
        ) from error
    result: dict[str, Any] = {}
    for statement in tree.body:
        targets: list[Any]
        if isinstance(statement, ast.Assign):
            targets = list(statement.targets)
            expression = statement.value
        elif isinstance(statement, ast.AnnAssign):
            targets = [statement.target]
            expression = statement.value
        else:
            continue
        if expression is None:
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                try:
                    result[target.id] = ast.literal_eval(expression)
                except (ValueError, TypeError):
                    continue
    return result


def verify_campaign_sources() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for label, item in sorted(CAMPAIGN_SOURCES.items()):
        relative = item["path"]
        path = ROOT / relative
        with path.open("rb") as stream:
            data = stream.read(MAX_SOURCE_BYTES + 1)
        require(
            len(data) <= MAX_SOURCE_BYTES,
            f"original public campaign source exceeds its safe bound: {relative}",
        )
        constants = source_constants(data, relative)
        for name, expected in item["constants"].items():
            require(
                constants.get(name) == expected,
                f"original frozen public campaign constant changed: {label}/{name}",
            )
        result[label] = {
            "path": relative,
            "sha256": hashlib.sha256(data).hexdigest(),
            "constants": normalize(item["constants"]),
        }
    return result


def validate_audit_document(
    document: Any,
    selected: tuple[str, ...],
    actual_sources: dict[str, dict[str, str]],
    actual_binaries: dict[str, dict[str, str]],
    interpreter: str,
) -> None:
    require(isinstance(document, dict), "original from-scratch audit is not an object")
    require(
        document.get("schema_version") == 1
        and document.get("audit") == "bounded-from-scratch-engine-provenance"
        and document.get("passed") is True
        and document.get("result") == "PASS"
        and document.get("input_issues") == [],
        "original fail-closed from-scratch audit is not independently passing",
    )
    require(
        document.get("minimum_required_independent_families") == 3
        and document.get("verified_core_family_count", 0) >= 3
        and document.get("verified_distinct_pipeline_count", 0) >= 3
        and document.get("core_families") == ["ast", "vm", "rust"]
        and document.get("all_public_source_families") == ["ast", "vm", "rust", "zig"],
        "original independent-family provenance or owned pipeline campaign changed",
    )
    tests = document.get("self_test")
    require(isinstance(tests, dict), "original isolated malicious-control audit is missing")
    execution = tests.get("execution")
    require(
        tests.get("passed") is True
        and tests.get("check_count") == 76
        and tests.get("failed") == []
        and tests.get("fixture_storage") == "in-memory only"
        and isinstance(execution, dict)
        and execution.get("isolated_subprocess") is True
        and execution.get("validated") is True
        and execution.get("expected_check_count") == 76
        and execution.get("validated_check_count") == 76
        and isinstance(execution.get("interpreter"), str)
        and Path(interpreter).name == "python3.14"
        and Path(execution["interpreter"]).resolve() == Path(interpreter).resolve(),
        "original exact-pinned 76-control isolated audit cannot be established",
    )
    scope = document.get("scope")
    require(
        isinstance(scope, dict)
        and scope.get("explicit_source_paths_only") is True
        and scope.get("repository_enumeration") is False
        and scope.get("mapped_binaries_hashed_against_static_elf") is True
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "original public-only no-timing/no-held-out audit scope changed",
    )
    families = document.get("families")
    require(
        isinstance(families, dict)
        and set(families) == {"ast", "vm", "rust", "zig"}
        and all(isinstance(value, dict) and value.get("passed") is True
                for value in families.values()),
        "original independent four-family audit is not completely passing",
    )
    global_native = document.get("native_elf_provenance")
    aggregate = document.get("runtime_native_mapping_provenance")
    require(
        isinstance(global_native, dict)
        and global_native.get("passed") is True
        and isinstance(global_native.get("families"), dict)
        and isinstance(aggregate, dict)
        and aggregate.get("passed") is True
        and isinstance(aggregate.get("families"), dict),
        "original actual mapped native ELF provenance is incomplete",
    )
    require(
        set(actual_sources) == set(selected)
        and set(actual_binaries) == set(selected),
        "actual selected candidate fingerprint manifest is incomplete",
    )
    for name in selected:
        spec = CANDIDATES[name]
        source_hashes = actual_sources[name]
        binary_hashes = actual_binaries[name]
        require(
            set(source_hashes) == set(spec["sources"])
            and set(binary_hashes) == set(spec["binaries"].values()),
            f"actual {name} owned source/native paths differ from the original audit",
        )
        family = families[name]
        public = family.get("python_source")
        public_path = spec["sources"][0]
        require(
            isinstance(public, dict)
            and public.get("passed") is True
            and not public.get("issues")
            and public.get("file") == public_path
            and public.get("sha256") == source_hashes[public_path],
            f"actual {name} public source is not bound to the original passing audit",
        )
        native_sources = family.get("native_sources")
        require(
            isinstance(native_sources, list)
            and len(native_sources) == len(spec["sources"]) - 1,
            f"original {name} owned native-source graph changed",
        )
        seen_sources: set[str] = set()
        for entry in native_sources:
            require(isinstance(entry, dict), f"invalid original {name} native-source evidence")
            relative = entry.get("file")
            require(
                isinstance(relative, str)
                and relative in spec["sources"][1:]
                and relative not in seen_sources
                and entry.get("passed") is True
                and not entry.get("issues")
                and entry.get("sha256") == source_hashes[relative],
                f"an actual {name} native source differs from its original passing audit",
            )
            seen_sources.add(relative)
        require(
            seen_sources == set(spec["sources"][1:]),
            f"an original audited {name} native source disappeared",
        )
        pipeline = family.get("owned_pipeline")
        require(
            isinstance(pipeline, dict)
            and pipeline.get("passed") is True
            and pipeline.get("issues") == []
            and all(pipeline.get(key) == value for key, value in spec["pipeline"].items()),
            f"original {name} owned parser/compiler/executor pipeline changed",
        )
        static_native = document.get(f"{name}_native_elf_provenance")
        require(
            isinstance(static_native, dict)
            and static_native.get("passed") is True
            and static_native.get("issues") == []
            and global_native["families"].get(name) == static_native,
            f"original global and {name} native ELF evidence disagree",
        )
        files = static_native.get("files")
        require(
            isinstance(files, dict) and set(files) == set(spec["binaries"]),
            f"original exact {name} owned native binary roles changed",
        )
        for role, relative in sorted(spec["binaries"].items()):
            entry = files[role]
            require(
                isinstance(entry, dict)
                and entry.get("file") == relative
                and entry.get("sha256") == binary_hashes[relative]
                and entry.get("forbidden_regex_symbols") == []
                and entry.get("cross_candidate_symbols") == [],
                f"actual {name} {role} ELF differs from the original audited binary",
            )
        require(
            family.get("native_binary_provenance")
            == "verified_exact_owned_elf_and_actual_hashed_memory_mappings",
            f"original {name} audit did not prove actual hashed native mappings",
        )
        runtime = family.get("isolated_runtime")
        require(
            isinstance(runtime, dict)
            and runtime.get("passed") is True
            and runtime.get("module") == spec["module"]
            and runtime.get("fixed_smoke_checks") == 3
            and runtime.get("forbidden_candidate_import_attempts") == []
            and runtime.get("forbidden_loaded_modules") == []
            and runtime.get("unexpected_candidate_modules") == [],
            f"original isolated {name} runtime or engine-independence checks failed",
        )
        probes = runtime.get("prohibited_import_and_loader_probes")
        require(
            isinstance(probes, dict)
            and set(probes) == {
                "stdlib_re", "cpython_sre", "third_party_regex",
                "other_candidate", "foreign_native_loader",
            }
            and all(value is True for value in probes.values()),
            f"original {name} poisoned regex/cross-engine controls changed",
        )
        mapping = runtime.get("native_mapping_provenance")
        binary_count = len(spec["binaries"])
        require(
            isinstance(mapping, dict)
            and mapping.get("passed") is True
            and mapping.get("source") == "/proc/self/maps"
            and mapping.get("expected_owned_mapping_count") == binary_count
            and mapping.get("observed_owned_mapping_count") == binary_count
            and mapping.get("issues") == [],
            f"original {name} actual native memory mappings are incomplete",
        )
        entries = mapping.get("observed_owned_mappings")
        require(
            isinstance(entries, list) and len(entries) == binary_count,
            f"original {name} mapped-binary evidence lost an owned role",
        )
        seen_roles: set[str] = set()
        for entry in entries:
            require(isinstance(entry, dict), f"invalid original {name} native mapping")
            role = entry.get("role")
            require(
                isinstance(role, str)
                and role in spec["binaries"]
                and role not in seen_roles
                and entry.get("file") == spec["binaries"][role]
                and entry.get("sha256") == binary_hashes[spec["binaries"][role]]
                and entry.get("matches_static_elf") is True
                and isinstance(entry.get("mapping_count"), int)
                and not isinstance(entry.get("mapping_count"), bool)
                and entry["mapping_count"] > 0,
                f"original {name} actual mapped native binary is not source-bound",
            )
            seen_roles.add(role)
        aggregate_family = aggregate["families"].get(name)
        require(
            isinstance(aggregate_family, dict)
            and aggregate_family.get("passed") is True
            and aggregate_family.get("expected_owned_mapping_count") == binary_count
            and aggregate_family.get("observed_owned_mapping_count") == binary_count,
            f"original aggregate actual-mapping evidence changed for {name}",
        )


def verified_provenance(selected: tuple[str, ...]) -> dict[str, Any]:
    require_pinned_runtime()
    with AUDIT_PATH.open("rb") as stream:
        audit_bytes = stream.read(MAX_AUDIT_BYTES + 1)
    require(len(audit_bytes) <= MAX_AUDIT_BYTES, "original passing audit exceeds its safe size")
    try:
        document = json.loads(audit_bytes)
    except (UnicodeError, ValueError) as error:
        raise OracleIntegrityError("cannot decode the exact original from-scratch audit") from error
    sources = {
        name: {
            relative: sha256_path(ROOT / relative, MAX_SOURCE_BYTES)
            for relative in CANDIDATES[name]["sources"]
        }
        for name in selected
    }
    binaries = {
        name: {
            relative: sha256_path(ROOT / relative, MAX_BINARY_BYTES)
            for relative in CANDIDATES[name]["binaries"].values()
        }
        for name in selected
    }
    validate_audit_document(document, selected, sources, binaries, sys.executable)
    return {
        "audit_path": AUDIT_PATH.relative_to(ROOT).as_posix(),
        "audit_sha256": hashlib.sha256(audit_bytes).hexdigest(),
        "oracle_source_path": RUNNER.relative_to(ROOT).as_posix(),
        "oracle_source_sha256": sha256_path(RUNNER, MAX_SOURCE_BYTES),
        "python_executable": str(Path(sys.executable).resolve()),
        "selected_candidates": list(selected),
        "source_sha256": {
            name: dict(sorted(values.items()))
            for name, values in sorted(sources.items())
        },
        "native_binary_sha256": {
            name: dict(sorted(values.items()))
            for name, values in sorted(binaries.items())
        },
        "original_public_campaign": verify_campaign_sources(),
    }


def case_random(family: str, stratum: str, example: int) -> random.Random:
    material = (
        f"{SEED_DOMAIN}\n{SEED}\n{family}\n{stratum}\n{example}"
    ).encode("ascii")
    return random.Random(int.from_bytes(hashlib.sha256(material).digest(), "big"))


def escape_atom(character: str) -> str:
    if character == "\n":
        return r"\n"
    if character == "\t":
        return r"\t"
    if ord(character) < 32:
        return f"\\x{ord(character):02x}"
    if character in r"\.^$*+?{}[]|()":
        return "\\" + character
    return character


def escape_class(character: str) -> str:
    if character == "\n":
        return r"\n"
    if ord(character) < 32:
        return f"\\x{ord(character):02x}"
    if character in "\\]^-":
        return "\\" + character
    return character


def grammar_pattern(
    family: str,
    rng: random.Random,
    binary: bool,
) -> tuple[str, int]:
    common_flags = (0, IGNORECASE, MULTILINE, DOTALL, ASCII, IGNORECASE | MULTILINE)
    flags = common_flags[rng.randrange(len(common_flags))]
    groups: dict[str, tuple[str, ...]] = {
        "literal-escape": (
            r"a", r"\.", r"\[", r"\x00", r"\t", r"\x80", r"a\-b",
        ),
        "alternation-nullable": (
            r"a|ab", r"(?:ab|a)b?", r"(?:|a)", r"(?:a|){0,3}", r"(?:x|xy|)",
        ),
        "character-class-range": (
            r"[a-z]+", r"[^a-z]{0,4}", r"[a-fA-F0-9]{1,4}",
            r"[\x00-\xff]+", r"[\]\-\\^]{0,3}",
        ),
        "category-ascii-locale": (
            r"\d+|\D+", r"\w+|\W+", r"\s+|\S+", r"\b\w+\b",
        ),
        "global-scoped-flags": (
            r"(?i:a)(?-i:B)", r"(?m:^a$)", r"(?s:a.b)",
            r"(?x: a \s* b )", r"(?a:\w+)",
        ),
        "anchors-newline": (
            r"^a|a$", r"\Aa", r"a\Z", r"a\z", r"^|$", r"(?m:^a$)",
        ),
        "greedy-lazy-possessive": (
            r"a{0,3}", r"a{1,4}?", r"a*?", r"a*+",
            r"a?+", r"(?:ab){0,4}",
        ),
        "atomic-backtracking": (
            r"(?>a|ab)b", r"(?>a{0,3})a", r"(?>ab|a)b",
            r"(?>(?:a|b){0,3})",
        ),
        "capture-backreference": (
            r"(?P<letter>a)(b)?", r"(a)(b)?\1",
            r"(?P<x>[ab])(?P=x)", r"((a)?b)(c)?",
        ),
        "lookahead": (
            r"(?=a)a", r"(?!b)a", r"(?=(a))\1",
            r"(?!(a))b", r"(?=.{0,4}$).",
        ),
        "fixed-lookbehind": (
            r"(?<=a)b", r"(?<!a)b", r"(?<=(a))b",
            r"(?<=ab)c", r"(?<!ab)c",
        ),
        "conditional-rollback": (
            r"(a)?(?(1)b|c)",
            r"(?:(a)b|a)(?(1)c|d)",
            r"(?P<x>a)?(?(x)b|c)",
        ),
        "invalid-grammar-flags": (
            "(", r"\q", r"[z-a]", r"(?P<x>a)(?P<x>b)",
            r"(?<=a+)b", r"a{2,1}", r"(?P=missing)",
        ),
        "replacement-zero-width": (
            r"(?P<letter>a)(b)?", r"(?:)", r"a*",
            r"(?=a)", r"(a)|(b)",
        ),
    }
    if family == "unicode-case-fold":
        patterns = (
            (r"(?i:k)", r"(?i:i)", r"(?i:s)", r"\w+",
             r"[^\x00-\xff]+", r"\u0100", r"\U00010400")
            if not binary
            else (r"(?i:\x4b)", r"(?i:[a-z])", r"[\x80-\xff]", r"\w+")
        )
        return patterns[rng.randrange(len(patterns))], flags
    if family == "quote-parity":
        pairs = (
            (",", '"'), ("|", "'"), ("\xe9", "\xf1"),
            ("\\", "^"), (",", "\n"), (",", ","),
        )
        separator, quote = pairs[rng.randrange(len(pairs))]
        start = escape_atom(separator)
        member = escape_class(quote)
        literal = escape_atom(quote)
        star = f"[^{member}]*"
        pair = f"{star}{literal}{star}{literal}"
        suffix = f"(?:{pair})*{star}$"
        patterns = (
            f"{start}(?={suffix})",
            f"({start})(?={suffix})",
            f"{start}(?=(?:{pair})*?{star}$)",
            f"{start}(?!{suffix})",
            f"{start}(?=(?:{pair}){{0,3}}{star}$)",
        )
        return patterns[rng.randrange(len(patterns))], flags
    require(family in groups, f"unrecognized fixed public grammar family: {family}")
    pattern = groups[family][rng.randrange(len(groups[family]))]
    if family == "category-ascii-locale":
        allowed = (0, ASCII, LOCALE) if binary else (0, ASCII)
        flags = allowed[rng.randrange(len(allowed))]
    elif family == "invalid-grammar-flags" and rng.randrange(4) == 0:
        pattern = "a"
        flags = (
            (UNICODE, LOCALE | ASCII)[rng.randrange(2)]
            if binary
            else (LOCALE, ASCII | UNICODE)[rng.randrange(2)]
        )
    require(
        0 < len(pattern) <= MAX_PATTERN_CHARACTERS,
        "generated public grammar exceeded its exact pattern bound",
    )
    return pattern, flags


def subject_payload(
    family: str,
    stratum: str,
    rng: random.Random,
) -> str:
    binary_subject = stratum in {
        "bytes", "bytes-subclass", "bytearray", "readonly-memoryview",
        "writable-memoryview", "cast-memoryview", "noncontiguous-memoryview",
        "released-memoryview", "array-B", "str-pattern-binary-subject",
    }
    alphabet = tuple("aAbBcCxXyYzZkKiIsS019_ -,.[]\\'\"\t\n")
    latin = ("\x00", "\x1c", "\x7f", "\x80", "\xa1", "\xe9", "\xf1", "\xff")
    choices = alphabet + latin
    lengths = (0, 1, 2, 3, 4, 7, 12, 20, 32, 48, 64)
    length = lengths[rng.randrange(len(lengths))]
    text = "".join(choices[rng.randrange(len(choices))] for _ in range(length))
    if family == "quote-parity":
        text = 'a,"x,y",b\n' + text[:48]
    elif family in {"capture-backreference", "conditional-rollback", "lookahead"}:
        text = "abacabc\n" + text[:48]
    elif family in {"anchors-newline", "global-scoped-flags"}:
        text = "a\nAb\nend\n" + text[:48]
    elif family == "replacement-zero-width":
        text = "aba" + text[:48]
    if not binary_subject:
        if stratum == "str-kind2":
            text = "\u0100" + text + "\u96ea"
        elif stratum == "str-kind4":
            text = "\U0001f600" + text + "\U00010400"
        elif family == "unicode-case-fold" and stratum != "str-kind1":
            text = "\u212a\u0130\u0131\u017f\u03a3\u03c2" + text
        if stratum == "newline-text":
            text = "\n" + text + "\n"
    require(
        len(text) <= MAX_SUBJECT_CHARACTERS,
        "generated public subject exceeded its exact safe bound",
    )
    if binary_subject:
        require(
            all(ord(value) <= 255 for value in text),
            "a binary public subject contains a non-Latin-1 character",
        )
    if stratum == "str-kind1":
        require(
            all(ord(value) <= 255 for value in text),
            "the one-byte public text stratum was silently widened",
        )
    if stratum == "str-kind2":
        require(
            any(ord(value) > 255 for value in text)
            and all(ord(value) <= 0xFFFF for value in text),
            "the two-byte public text stratum changed representation",
        )
    if stratum == "str-kind4":
        require(
            any(ord(value) > 0xFFFF for value in text),
            "the four-byte public text stratum changed representation",
        )
    return text


def build_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for family in GRAMMAR_FAMILIES:
        for stratum in INPUT_STRATA:
            binary_pattern = stratum in {
                "bytes", "bytes-subclass", "bytearray", "readonly-memoryview",
                "writable-memoryview", "cast-memoryview", "noncontiguous-memoryview",
                "released-memoryview", "array-B", "bytes-pattern-str-subject",
            }
            for example in range(EXAMPLES_PER_STRATUM):
                rng = case_random(family, stratum, example)
                pattern, flags = grammar_pattern(family, rng, binary_pattern)
                if binary_pattern:
                    require(
                        all(ord(value) <= 255 for value in pattern),
                        "a public bytes pattern contains a wide character",
                    )
                payload = subject_payload(family, stratum, rng)
                cases.append({
                    "id": f"{family}/{stratum}/{example:02d}",
                    "family": family,
                    "stratum": stratum,
                    "example": example,
                    "pattern_kind": "bytes" if binary_pattern else "str",
                    "pattern": pattern,
                    "subject": payload,
                    "flags": flags,
                    "extension_offset": rng.randrange(len(EXTENSION_OPERATIONS)),
                    "callback_mode": (
                        "value", "raise-first", "raise-second",
                        "wrong-domain", "reentrant",
                    )[rng.randrange(5)],
                })
    require(len(GRAMMAR_FAMILIES) == 16, "immutable public grammar-family denominator changed")
    require(len(INPUT_STRATA) == 16, "immutable public input-stratum denominator changed")
    require(len(cases) == EXPECTED_CASES == 8_192, "immutable universal-public case denominator changed")
    require(
        len({case["id"] for case in cases}) == len(cases),
        "an independent universal-public case identifier is duplicated",
    )
    return cases


def materialize_case(case: dict[str, Any]) -> tuple[Any, Any, Any]:
    text = case["subject"]
    stratum = case["stratum"]
    pattern = (
        case["pattern"].encode("latin-1")
        if case["pattern_kind"] == "bytes" else case["pattern"]
    )
    if stratum in {
        "str-kind1", "str-kind2", "str-kind4", "newline-text",
        "bytes-pattern-str-subject",
    }:
        return pattern, text, None
    if stratum == "str-subclass":
        return pattern, TextSubclass(text), None
    payload = text.encode("latin-1")
    if stratum in {"bytes", "str-pattern-binary-subject"}:
        return pattern, payload, None
    if stratum == "bytes-subclass":
        return pattern, BytesSubclass(payload), None
    if stratum == "bytearray":
        storage = bytearray(payload)
        return pattern, storage, storage
    if stratum == "readonly-memoryview":
        return pattern, memoryview(payload), None
    if stratum in {
        "writable-memoryview", "cast-memoryview",
        "noncontiguous-memoryview", "released-memoryview",
    }:
        storage = bytearray(payload)
        view = memoryview(storage)
        if stratum == "cast-memoryview":
            view = view.cast("c").cast("B")
        elif stratum == "noncontiguous-memoryview":
            view = view[::2]
        elif stratum == "released-memoryview":
            view.release()
        return pattern, view, storage
    if stratum == "array-B":
        storage = array.array("B", payload)
        return pattern, storage, storage
    raise OracleIntegrityError(f"unknown independently reconstructed public stratum: {stratum}")


def error_snapshot(error: BaseException, depth: int = 0) -> dict[str, Any]:
    require(depth <= 4, "documented public exception chain exceeded its safe bound")
    result: dict[str, Any] = {
        "class": type(error).__name__,
        "args": normalize(error.args),
        "notes": normalize(getattr(error, "__notes__", [])),
        "cause": (
            error_snapshot(error.__cause__, depth + 1)
            if error.__cause__ is not None else None
        ),
        "context": (
            error_snapshot(error.__context__, depth + 1)
            if error.__context__ is not None else None
        ),
        "suppress_context": error.__suppress_context__,
    }
    if hasattr(error, "msg") and hasattr(error, "pos"):
        result["pattern_error"] = {
            key: normalize(getattr(error, key, None))
            for key in ("msg", "pattern", "pos", "lineno", "colno")
        }
    return result


def attempted(action: Callable[[], Any]) -> dict[str, Any]:
    try:
        return {"status": "ok", "value": normalize(action())}
    except Exception as error:
        return {"status": "error", "error": error_snapshot(error)}


def pattern_snapshot(pattern: Any) -> dict[str, Any]:
    return {
        "pattern": normalize(pattern.pattern),
        "flags": int(pattern.flags),
        "groups": pattern.groups,
        "groupindex": normalize(dict(pattern.groupindex)),
    }


def match_snapshot(match: Any, subject: Any = None) -> dict[str, Any] | None:
    if match is None:
        return None
    default = "!" if isinstance(match.string, str) else b"!"
    return {
        "span": normalize(match.span()),
        "regs": normalize(match.regs),
        "regs_cached": match.regs is match.regs,
        "group0": normalize(match.group(0)),
        "groups": normalize(match.groups()),
        "groups_default": normalize(match.groups(default)),
        "groupdict": normalize(match.groupdict()),
        "groupdict_default": normalize(match.groupdict(default)),
        "lastindex": match.lastindex,
        "lastgroup": match.lastgroup,
        "pos": match.pos,
        "endpos": match.endpos,
        "same_subject": match.string is subject,
        "string": normalize(match.string),
    }


def exact_windows(length: int) -> tuple[tuple[int, int], ...]:
    return (
        (0, length),
        (0, 0),
        (min(1, length), length),
        (-2, length + 2),
        (min(3, length), min(1, length)),
    )


def scanner_values(pattern: Any, subject: Any, pos: int, endpos: int, mode: str) -> list[Any]:
    scanner = pattern.scanner(subject, pos, endpos)
    if mode == "mixed":
        methods = ("search", "match", "search", "search", "match", "search", "match", "match")
        return [match_snapshot(getattr(scanner, method)(), subject) for method in methods]
    values: list[Any] = []
    for _ in range(min(MAX_RESULTS, 2 * len(subject) + 12)):
        item = getattr(scanner, mode)()
        values.append(match_snapshot(item, subject))
        if item is None:
            values.append(match_snapshot(getattr(scanner, mode)(), subject))
            values.append(match_snapshot(getattr(scanner, mode)(), subject))
            require(len(values) <= MAX_RESULTS, "bounded public scanner returned too many results")
            return values
    raise OracleIntegrityError("documented public scanner exceeded its fixed termination bound")


class EventIndex:
    def __init__(self, events: list[Any], mode: str) -> None:
        self.events = events
        self.mode = mode

    def __index__(self) -> int:
        self.events.append(("__index__", self.mode))
        if self.mode == "raise":
            raise PublicIndexError("universal public index sentinel")
        if self.mode == "overflow":
            return 1 << 100
        if self.mode == "negative":
            return -1
        if self.mode == "noninteger":
            return "not-an-index"  # type: ignore[return-value]
        return 1


def callback_observation(
    module: Any,
    compiled: Any,
    pattern: Any,
    subject: Any,
    operation: str,
    bound: bool,
    mode: str,
) -> dict[str, Any]:
    events: list[Any] = []

    def replacement(match: Any) -> Any:
        number = len(events)
        events.append({
            "event": "callback",
            "index": number,
            "match": match_snapshot(match, subject),
        })
        if mode == "raise-first" and number == 0:
            raise PublicCallbackError("universal public replacement sentinel")
        if mode == "raise-second" and number == 1:
            raise PublicCallbackError("universal public replacement sentinel")
        if mode == "wrong-domain":
            return b"wrong" if isinstance(match.string, str) else "wrong"
        if mode == "reentrant":
            nested = compiled.search(subject)
            events.append({"event": "recursive-search", "match": match_snapshot(nested, subject)})
        value = match.group(0)
        return value + ("!" if isinstance(value, str) else b"!")

    if bound:
        outcome = attempted(
            lambda: getattr(compiled, operation)(replacement, subject, count=0)
        )
    else:
        outcome = attempted(
            lambda: getattr(module, operation)(pattern, replacement, subject, count=0)
        )
    return {"result": outcome, "events": normalize(events)}


def warning_observation(module: Any, pattern: Any, subject: Any, flags: int) -> dict[str, Any]:
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        result = attempted(lambda: module.split(pattern, subject, 1, flags))
    return {
        "result": result,
        "warnings": [
            {
                "category": warning.category.__name__,
                "message": normalize(str(warning.message)),
            }
            for warning in recorded
        ],
    }


def index_observation(compiled: Any, subject: Any, case: dict[str, Any]) -> dict[str, Any]:
    events: list[Any] = []
    modes = ("value", "negative", "raise", "noninteger", "overflow")
    index = EventIndex(events, modes[case["example"] % len(modes)])
    result = attempted(lambda: match_snapshot(compiled.search(subject, index), subject))
    return {"result": result, "events": normalize(events)}


def match_surface(compiled: Any, subject: Any) -> Any:
    match = compiled.search(subject)
    if match is None:
        return None
    captures = [
        {
            "index": index,
            "group": normalize(match.group(index)),
            "getitem": normalize(match[index]),
            "start": match.start(index),
            "end": match.end(index),
            "span": normalize(match.span(index)),
        }
        for index in range(compiled.groups + 1)
    ]
    named = {
        name: {
            "group": normalize(match.group(name)),
            "getitem": normalize(match[name]),
            "start": match.start(name),
            "end": match.end(name),
            "span": normalize(match.span(name),
            ),
        }
        for name in sorted(compiled.groupindex)
    }
    return {
        "match": match_snapshot(match, subject),
        "captures": captures,
        "named": named,
    }


def finditer_exhaustion(compiled: Any, subject: Any) -> dict[str, Any]:
    iterator = compiled.finditer(subject)
    matches: list[Any] = []
    for _ in range(MAX_RESULTS):
        item = next(iterator, None)
        if item is None:
            return {
                "matches": matches,
                "iterator_is_self": iter(iterator) is iterator,
                "exhausted_once": next(iterator, None) is None,
                "exhausted_twice": next(iterator, None) is None,
            }
        matches.append(match_snapshot(item, subject))
    raise OracleIntegrityError("public iterator exceeded its exact safe result bound")


def scanner_exhaustion(compiled: Any, subject: Any) -> dict[str, Any]:
    scanner = compiled.scanner(subject)
    values: list[Any] = []
    for _ in range(MAX_RESULTS):
        match = scanner.search()
        if match is None:
            return {
                "matches": values,
                "exhausted_once": scanner.search() is None,
                "exhausted_twice": scanner.search() is None,
            }
        values.append(match_snapshot(match, subject))
    raise OracleIntegrityError("public scanner exceeded its exact safe result bound")


def extension_action(
    operation: str,
    module: Any,
    compiled: Any,
    pattern: Any,
    subject: Any,
    flags: int,
    case: dict[str, Any],
) -> Callable[[], Any] | None:
    template = r"<\g<0>>" if isinstance(pattern, str) else rb"<\g<0>>"
    if operation == "module-search":
        return lambda: match_snapshot(module.search(pattern, subject, flags), subject)
    if operation == "module-match":
        return lambda: match_snapshot(module.match(pattern, subject, flags), subject)
    if operation == "module-fullmatch":
        return lambda: match_snapshot(module.fullmatch(pattern, subject, flags), subject)
    if operation == "module-findall":
        return lambda: module.findall(pattern, subject, flags)
    if operation == "module-finditer":
        return lambda: [
            match_snapshot(match, subject)
            for match in module.finditer(pattern, subject, flags)
        ]
    if operation in {"module-sub-template", "module-subn-template"}:
        name = "sub" if operation == "module-sub-template" else "subn"
        return lambda: getattr(module, name)(pattern, template, subject, count=2, flags=flags)
    if operation in {"bound-sub-template", "bound-subn-template"}:
        if compiled is None:
            return None
        name = "sub" if operation == "bound-sub-template" else "subn"
        return lambda: getattr(compiled, name)(template, subject, count=2)
    if operation in {
        "module-sub-callback", "module-subn-callback",
        "bound-sub-callback", "bound-subn-callback",
    }:
        bound = operation.startswith("bound-")
        if compiled is None:
            return None
        name = "subn" if "subn" in operation else "sub"
        return lambda: callback_observation(
            module, compiled, pattern, subject, name, bound, case["callback_mode"]
        )
    if operation == "module-escape":
        return lambda: module.escape(pattern)
    if operation == "warning-positional-split":
        return lambda: warning_observation(module, pattern, subject, flags)
    if operation == "module-purge-recompile":
        def purge_and_compile() -> dict[str, Any]:
            module.purge()
            return pattern_snapshot(module.compile(pattern, flags))
        return purge_and_compile
    if compiled is None:
        return None
    if operation == "match-surface":
        return lambda: match_surface(compiled, subject)
    if operation == "match-expand":
        def expanded() -> Any:
            match = compiled.search(subject)
            return None if match is None else match.expand(template)
        return expanded
    if operation == "pattern-copy":
        return lambda: {
            "same_object": copy.copy(compiled) is compiled,
            "pattern": pattern_snapshot(copy.copy(compiled)),
        }
    if operation == "pattern-deepcopy":
        return lambda: {
            "same_object": copy.deepcopy(compiled) is compiled,
            "pattern": pattern_snapshot(copy.deepcopy(compiled)),
        }
    if operation == "pattern-metadata":
        return lambda: pattern_snapshot(compiled)
    if operation == "malicious-window-index":
        return lambda: index_observation(compiled, subject, case)
    if operation == "finditer-exhaustion":
        return lambda: finditer_exhaustion(compiled, subject)
    if operation == "scanner-exhaustion":
        return lambda: scanner_exhaustion(compiled, subject)
    raise OracleIntegrityError(f"unrecognized independently frozen extension operation: {operation}")


def raise_error(error: Exception) -> Any:
    raise error


def observe_cases(
    module: Any,
    cases: list[dict[str, Any]],
    emit: Callable[[dict[str, Any]], None],
) -> dict[str, int]:
    operation_counts: collections.Counter[str] = collections.Counter()
    for case in cases:
        pattern, subject, _storage = materialize_case(case)
        flags = case["flags"]
        compiled = None
        try:
            compiled = module.compile(pattern, flags)
            compile_result = {
                "status": "ok",
                "value": pattern_snapshot(compiled),
            }
        except Exception as error:
            compile_result = attempted(lambda error=error: raise_error(error))
        per_case = 0

        def record(
            operation: str,
            action: Callable[[], Any] | None,
            *,
            result: dict[str, Any] | None = None,
        ) -> None:
            nonlocal per_case
            observation = (
                result
                if result is not None
                else {"status": "not-run", "reason": "compile-error"}
                if action is None
                else attempted(action)
            )
            operation_counts[operation.partition(":")[0]] += 1
            emit({
                "kind": "observation",
                "id": case["id"],
                "family": case["family"],
                "stratum": case["stratum"],
                "operation": operation,
                "result": observation,
            })
            per_case += 1

        record("compile", None, result=compile_result)
        try:
            subject_length = len(subject)
        except (TypeError, ValueError):
            subject_length = len(case["subject"])
        for index, (pos, endpos) in enumerate(exact_windows(subject_length)):
            suffix = f":w{index}:{pos}:{endpos}"
            for method in ("search", "match", "fullmatch"):
                action = (
                    None if compiled is None
                    else lambda owner=compiled, name=method, start=pos, end=endpos:
                    match_snapshot(getattr(owner, name)(subject, start, end), subject)
                )
                record(method + suffix, action)
            action = (
                None if compiled is None
                else lambda owner=compiled, start=pos, end=endpos:
                owner.findall(subject, start, end)
            )
            record("findall" + suffix, action)
            action = (
                None if compiled is None
                else lambda owner=compiled, start=pos, end=endpos:
                [
                    match_snapshot(match, subject)
                    for match in owner.finditer(subject, start, end)
                ]
            )
            record("finditer" + suffix, action)
            for mode in ("search", "match"):
                action = (
                    None if compiled is None
                    else lambda owner=compiled, start=pos, end=endpos, method=mode:
                    scanner_values(owner, subject, start, end, method)
                )
                record(f"scanner-{mode}{suffix}", action)
        action = (
            None if compiled is None
            else lambda owner=compiled:
            scanner_values(owner, subject, 0, len(subject), "mixed")
        )
        record("scanner-mixed", action)
        for maximum in (0, 1, 2):
            action = (
                None if compiled is None
                else lambda owner=compiled, count=maximum:
                owner.split(subject, maxsplit=count)
            )
            record(f"split:{maximum}", action)
            record(
                f"module-split:{maximum}",
                lambda count=maximum:
                module.split(pattern, subject, maxsplit=count, flags=flags),
            )
        for offset in range(5):
            operation = EXTENSION_OPERATIONS[
                (case["extension_offset"] + offset) % len(EXTENSION_OPERATIONS)
            ]
            record(
                f"{operation}:slot{offset}",
                extension_action(
                    operation, module, compiled, pattern, subject, flags, case
                ),
            )
        require(
            per_case == OBSERVATIONS_PER_CASE,
            f"universal case did not emit exactly 48 aligned observations: {case['id']}",
        )
    return dict(sorted(operation_counts.items()))


def foreign_native_basename(value: str) -> bool:
    name = Path(value).name.casefold().replace("-", "_")
    return name.startswith((
        "libpcre", "libonig", "libhyperscan", "libre2", "libregex",
        "libhs.", "pyinit__regex", "pyinit__re2", "pyinit__pcre",
        "pyinit__onig",
    ))


def install_candidate_guard(name: str) -> tuple[list[dict[str, str]], list[str]]:
    spec = CANDIDATES[name]
    allowed = frozenset({spec["module"], spec["native_module"]})
    blocked: list[dict[str, str]] = []
    owned_loads: list[str] = []
    zig_engine = str((ROOT / CANDIDATES["zig"]["binaries"]["engine"]).resolve())

    def prohibited(target: Any) -> bool:
        value = str(target)
        if value.partition(".")[0] in REGEX_ENGINE_ROOTS:
            return True
        return value.startswith("candidates.") and value not in allowed

    for module_name in tuple(sys.modules):
        if module_name.partition(".")[0] in REGEX_ENGINE_ROOTS:
            sys.modules.pop(module_name, None)

    def deny(kind: str, target: Any) -> None:
        blocked.append({"kind": kind, "target": str(target)})
        raise ImportError(f"universal public isolated worker rejected {kind}: {target}")

    def hook(event: str, arguments: tuple[Any, ...]) -> None:
        if event == "import" and arguments and prohibited(arguments[0]):
            deny("audit_import", arguments[0])
        elif event == "ctypes.dlopen":
            target = arguments[0] if arguments else None
            if (
                name == "zig"
                and target is not None
                and str(Path(os.fsdecode(target)).resolve()) == zig_engine
            ):
                owned_loads.append(zig_engine)
            else:
                deny("foreign_native_loader", target)
        elif event == "ctypes.dlsym":
            library = arguments[0] if arguments else None
            symbol = arguments[1] if len(arguments) > 1 else ""
            target = getattr(library, "_name", None)
            if (
                name != "zig"
                or target is None
                or str(Path(os.fsdecode(target)).resolve()) != zig_engine
                or not str(symbol).startswith("rebar_zig_")
            ):
                deny("foreign_native_symbol", symbol)
        elif (
            event == "subprocess.Popen"
            or event == "os.system"
            or event.startswith("os.exec")
            or event.startswith("os.spawn")
            or event in {"os.fork", "os.posix_spawn"}
        ):
            deny("external_process", event)
        elif event == "open" and arguments:
            target = str(arguments[0]).casefold().replace("\\", "/")
            if (
                "holdout" in target
                or "benchmark" in target
                or "/performance/" in target
                or "/hidden/" in target
                or "/markers/" in target
            ):
                deny("nonpublic_fixture_access", arguments[0])

    original_import = builtins.__import__
    original_import_module = importlib.import_module

    def guarded_import(
        module_name: str,
        globals: Any = None,
        locals: Any = None,
        fromlist: Any = (),
        level: int = 0,
    ) -> Any:
        if prohibited(module_name):
            deny("python_import", module_name)
        if module_name == "candidates":
            for item in fromlist or ():
                if (
                    isinstance(item, str)
                    and item != "*"
                    and prohibited(f"candidates.{item}")
                ):
                    deny("cross_candidate_import", f"candidates.{item}")
        return original_import(module_name, globals, locals, fromlist, level)

    def guarded_import_module(module_name: str, package: str | None = None) -> Any:
        if prohibited(module_name):
            deny("import_module", module_name)
        return original_import_module(module_name, package)

    sys.addaudithook(hook)
    builtins.__import__ = guarded_import
    importlib.import_module = guarded_import_module
    return blocked, owned_loads


def verify_candidate_worker(
    name: str,
    module: Any,
    provenance: dict[str, Any],
) -> dict[str, Any]:
    spec = CANDIDATES[name]
    public_path = ROOT / spec["sources"][0]
    require(
        getattr(module, "__name__", None) == spec["module"]
        and Path(module.__file__).resolve() == public_path.resolve()
        and sha256_path(Path(module.__file__), MAX_SOURCE_BYTES)
        == provenance["source_sha256"][name][spec["sources"][0]],
        f"isolated {name} worker loaded an unapproved or changed public source",
    )
    native = sys.modules.get(spec["native_module"])
    require(native is not None, f"isolated {name} did not load its owned native bridge")
    bridge_role = "native" if name == "vm" else "bridge"
    require(
        Path(native.__file__).resolve()
        == (ROOT / spec["binaries"][bridge_role]).resolve(),
        f"isolated {name} loaded a different owned native bridge",
    )
    expected = {
        str((ROOT / relative).resolve()): role
        for role, relative in spec["binaries"].items()
    }
    with Path("/proc/self/maps").open("r", encoding="utf-8") as stream:
        data = stream.read(MAX_MAP_BYTES + 1)
    require(len(data) <= MAX_MAP_BYTES, "actual native mapping exceeded its safe bound")
    observed: collections.Counter[str] = collections.Counter()
    candidate_root = str((ROOT / "candidates").resolve()) + os.sep
    for line in data.splitlines():
        fields = line.split(None, 5)
        if len(fields) != 6 or not fields[5].startswith("/"):
            continue
        raw = fields[5].strip()
        require(
            not foreign_native_basename(raw),
            f"isolated {name} mapped a forbidden third-party regex library",
        )
        deleted = raw.endswith(" (deleted)")
        path = raw[:-10] if deleted else raw
        if path in expected:
            require(not deleted, f"isolated {name} mapped a deleted owned binary")
            observed[path] += 1
        elif path.startswith(candidate_root) and (
            Path(path).name.endswith(".so") or ".so." in Path(path).name
        ):
            raise OracleIntegrityError(
                f"isolated {name} mapped a cross-candidate or unapproved native engine"
            )
    require(
        set(observed) == set(expected),
        f"isolated {name} did not map exactly its original audited native binaries",
    )
    mappings: list[dict[str, Any]] = []
    for path, role in sorted(expected.items(), key=lambda item: item[1]):
        relative = spec["binaries"][role]
        actual = sha256_path(Path(path), MAX_BINARY_BYTES)
        require(
            actual == provenance["native_binary_sha256"][name][relative],
            f"isolated actual {name} mapped native {role} changed during execution",
        )
        mappings.append({
            "role": role,
            "path": relative,
            "sha256": actual,
            "mapping_count": observed[path],
        })
    return {
        "module": spec["module"],
        "family": name,
        "native_mappings": mappings,
    }


def poison_guard_probes(name: str, blocked: list[dict[str, str]]) -> dict[str, bool]:
    controls: list[tuple[str, Callable[[], Any]]] = [
        ("stdlib-re", lambda: builtins.__import__("re")),
        ("cpython-sre", lambda: importlib.import_module("_sre")),
        ("third-party-regex", lambda: importlib.import_module("regex")),
        ("third-party-re2", lambda: importlib.import_module("re2")),
        ("ast-candidate", lambda: importlib.import_module("candidates.ast_candidate")),
    ]
    for other in sorted(set(CANDIDATES) - {name}):
        module_name = CANDIDATES[other]["module"]
        controls.append((
            f"{other}-candidate",
            lambda target=module_name: importlib.import_module(target),
        ))
    result: dict[str, bool] = {}
    for label, action in controls:
        count = len(blocked)
        try:
            action()
        except ImportError:
            result[label] = len(blocked) == count + 1
        else:
            result[label] = False
    require(
        all(result.values()) and len(result) == 7,
        f"isolated {name} failed its exact forbidden-engine poisoned controls",
    )
    return result


def run_worker(
    role: str,
    name: str,
    expected_provenance: dict[str, Any],
) -> None:
    candidate_free()
    selected = tuple(expected_provenance.get("selected_candidates", ()))
    require(
        selected and all(item in CANDIDATES for item in selected) and name in selected,
        "isolated public worker selected an unapproved audited candidate",
    )
    provenance = verified_provenance(selected)
    require(
        provenance == expected_provenance,
        "isolated worker original audit/campaign/source/native fingerprints changed",
    )
    locale.setlocale(locale.LC_CTYPE, "C")
    cases = build_cases()
    fixture_digest = value_digest(cases)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    blocked: list[dict[str, str]] = []
    owned_loads: list[str] = []
    artifacts: dict[str, Any] | None = None
    if role == "stdlib":
        module = importlib.import_module("re")
        candidate_free()
    elif role == "candidate":
        blocked, owned_loads = install_candidate_guard(name)
        module = importlib.import_module(CANDIDATES[name]["module"])
        require(not blocked, f"isolated {name} attempted engine delegation while importing")
        artifacts = verify_candidate_worker(name, module, provenance)
        require(not blocked, f"isolated {name} attempted engine delegation while verifying")
    else:
        raise OracleIntegrityError("unknown isolated universal-public worker role")

    digest = hashlib.sha256()
    emitted = 0

    def emit(row: dict[str, Any]) -> None:
        nonlocal emitted
        line = canonical(row)
        encoded = line.encode("ascii")
        require(
            len(encoded) <= MAX_WORKER_LINE_BYTES,
            "isolated public observation exceeded its exact bounded line size",
        )
        digest.update(encoded)
        digest.update(b"\n")
        sys.stdout.write(line)
        sys.stdout.write("\n")
        emitted += 1
        require(
            emitted <= EXPECTED_OBSERVATIONS,
            "isolated worker exceeded the exact 393,216-observation denominator",
        )

    operation_counts = observe_cases(module, cases, emit)
    require(
        emitted == EXPECTED_OBSERVATIONS,
        "isolated worker did not produce the exact 393,216 documented observations",
    )
    guards: dict[str, bool] = {}
    if role == "candidate":
        require(not blocked, f"isolated {name} delegated during public regex evaluation")
        guards = poison_guard_probes(name, blocked)
        artifacts = verify_candidate_worker(name, module, provenance)
        if name == "zig":
            expected = str(
                (ROOT / CANDIDATES["zig"]["binaries"]["engine"]).resolve()
            )
            require(
                owned_loads == [expected],
                "isolated Zig did not load exactly its single original audited engine",
            )
        else:
            require(not owned_loads, "a non-Zig candidate dynamically loaded a native engine")
    else:
        candidate_free()
    sys.stdout.write(canonical({
        "kind": "done",
        "schema": SCHEMA,
        "role": role,
        "candidate": name,
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "cases": len(cases),
        "case_sha256": fixture_digest,
        "observations": emitted,
        "observations_per_case": OBSERVATIONS_PER_CASE,
        "observation_sha256": digest.hexdigest(),
        "operation_counts": operation_counts,
        "provenance": provenance,
        "candidate_artifacts": artifacts,
        "poison_guards": guards,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "external_regex_packages": 0,
        "benchmark_or_timing_executed": False,
    }))
    sys.stdout.write("\n")
    sys.stdout.flush()


def failed_worker(
    process: subprocess.Popen[str],
    label: str,
    reason: str,
) -> WorkerExecutionError:
    if process.poll() is None:
        process.kill()
    stderr = ""
    if process.stderr is not None:
        stderr = process.stderr.read(MAX_WORKER_STDERR_BYTES + 1)
    encoded = stderr.encode("utf-8")
    truncated = len(encoded) > MAX_WORKER_STDERR_BYTES
    if truncated:
        stderr = encoded[:MAX_WORKER_STDERR_BYTES].decode(
            "utf-8",
            errors="replace",
        )
    return WorkerExecutionError(
        label,
        reason,
        exit_code=process.wait(),
        stderr=stderr,
        stderr_truncated=truncated,
    )


def read_worker_line(process: subprocess.Popen[str], label: str) -> dict[str, Any]:
    require(process.stdout is not None, f"isolated {label} stdout is unavailable")
    line = process.stdout.readline(MAX_WORKER_LINE_BYTES + 2)
    if not line:
        raise failed_worker(
            process,
            label,
            "ended before its exact canonical public JSON record",
        )
    require(
        line.endswith("\n")
        and len(line.encode("utf-8")) <= MAX_WORKER_LINE_BYTES + 1,
        f"isolated {label} emitted excessive or incomplete public evidence",
    )
    try:
        row = json.loads(line)
    except (UnicodeError, ValueError) as error:
        raise OracleIntegrityError(
            f"isolated {label} emitted invalid public JSON evidence"
        ) from error
    require(isinstance(row, dict), f"isolated {label} public row is not an object")
    require(
        canonical(row) + "\n" == line,
        f"isolated {label} did not emit exact canonical public JSON",
    )
    return row


def finish_worker(process: subprocess.Popen[str], label: str) -> None:
    require(process.stdout is not None, f"isolated {label} stdout is unavailable")
    trailing = process.stdout.readline(2)
    if trailing:
        raise failed_worker(process, label, "emitted trailing noncanonical records")
    require(process.stderr is not None, f"isolated {label} stderr is unavailable")
    stderr = process.stderr.read(MAX_WORKER_STDERR_BYTES + 1)
    encoded = stderr.encode("utf-8")
    truncated = len(encoded) > MAX_WORKER_STDERR_BYTES
    if truncated:
        stderr = encoded[:MAX_WORKER_STDERR_BYTES].decode(
            "utf-8",
            errors="replace",
        )
        if process.poll() is None:
            process.kill()
    code = process.wait()
    if code != 0 or stderr or truncated:
        raise WorkerExecutionError(
            label,
            "did not complete its silent canonical public worker",
            exit_code=code,
            stderr=stderr,
            stderr_truncated=truncated,
        )


def safe_worker_environment() -> dict[str, str]:
    environment = {
        key: value
        for key, value in os.environ.items()
        if not any(
            marker in key.casefold()
            for marker in ("holdout", "benchmark", "performance", "marker")
        )
    }
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return environment


def run_isolated_differential(
    name: str,
    cases: list[dict[str, Any]],
    provenance: dict[str, Any],
) -> dict[str, Any]:
    expected_case_digest = value_digest(cases)
    workers: dict[str, subprocess.Popen[str]] = {}
    expected_digest = hashlib.sha256()
    actual_digest = hashlib.sha256()
    mismatch_digest = hashlib.sha256()
    mismatches: list[dict[str, Any]] = []
    mismatch_count = 0
    check_count = 0
    operation_counts: collections.Counter[str] = collections.Counter()
    case_by_id = {case["id"]: case for case in cases}
    current_expected: dict[str, Any] | None = None
    done: dict[str, dict[str, Any]] = {}
    try:
        for role in ("stdlib", "candidate"):
            command = [
                str(PINNED_EXECUTABLE),
                "-I",
                "-B",
                "-u",
                str(RUNNER),
                "--worker",
                role,
                "--candidate",
                name,
                "--provenance-json",
                canonical(provenance),
            ]
            workers[role] = subprocess.Popen(
                command,
                cwd=str(ROOT),
                env=safe_worker_environment(),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
        while True:
            expected = read_worker_line(workers["stdlib"], f"{name}/stdlib")
            current_expected = (
                expected if expected.get("kind") == "observation" else None
            )
            actual = read_worker_line(workers["candidate"], f"{name}/candidate")
            if expected.get("kind") == "done" or actual.get("kind") == "done":
                require(
                    expected.get("kind") == "done" and actual.get("kind") == "done",
                    f"isolated {name} workers changed their exact observation denominator",
                )
                done = {"stdlib": expected, "candidate": actual}
                break
            require(
                set(expected)
                == {"kind", "id", "family", "stratum", "operation", "result"}
                and set(actual) == set(expected)
                and expected.get("kind") == "observation"
                and actual.get("kind") == "observation",
                f"isolated {name} worker changed the exact public observation schema",
            )
            case = case_by_id.get(expected.get("id"))
            require(
                case is not None
                and expected["id"] == actual["id"] == case["id"]
                and expected["family"] == actual["family"] == case["family"]
                and expected["stratum"] == actual["stratum"] == case["stratum"]
                and expected["operation"] == actual["operation"],
                f"isolated {name} worker reordered or substituted a fixed public case",
            )
            for digest, row in ((expected_digest, expected), (actual_digest, actual)):
                digest.update(canonical(row).encode("ascii"))
                digest.update(b"\n")
            operation_counts[expected["operation"].partition(":")[0]] += 1
            check_count += 1
            require(
                check_count <= EXPECTED_OBSERVATIONS,
                f"isolated {name} exceeded the exact 393,216 comparison bound",
            )
            if expected["result"] != actual["result"]:
                mismatch_count += 1
                mismatch = {
                    "id": case["id"],
                    "family": case["family"],
                    "stratum": case["stratum"],
                    "example": case["example"],
                    "pattern_kind": case["pattern_kind"],
                    "pattern": case["pattern"],
                    "subject": case["subject"],
                    "flags": case["flags"],
                    "operation": expected["operation"],
                    "expected": expected["result"],
                    "actual": actual["result"],
                }
                mismatch_digest.update(canonical(mismatch).encode("ascii"))
                mismatch_digest.update(b"\n")
                if len(mismatches) < MAX_MISMATCH_EXAMPLES:
                    mismatches.append(mismatch)
            current_expected = None
        require(
            check_count == EXPECTED_OBSERVATIONS,
            f"isolated {name} did not compare all exact 393,216 public observations",
        )
        counts = dict(sorted(operation_counts.items()))
        for role, digest in (
            ("stdlib", expected_digest),
            ("candidate", actual_digest),
        ):
            row = done[role]
            require(
                row.get("schema") == SCHEMA
                and row.get("role") == role
                and row.get("candidate") == name
                and row.get("seed") == SEED
                and row.get("seed_domain") == SEED_DOMAIN
                and row.get("cases") == EXPECTED_CASES
                and row.get("case_sha256") == expected_case_digest
                and row.get("observations") == EXPECTED_OBSERVATIONS
                and row.get("observations_per_case") == OBSERVATIONS_PER_CASE
                and row.get("observation_sha256") == digest.hexdigest()
                and row.get("operation_counts") == counts
                and row.get("provenance") == provenance
                and row.get("performance_fixtures_read") == 0
                and row.get("holdout_cases_read") == 0
                and row.get("external_regex_packages") == 0
                and row.get("benchmark_or_timing_executed") is False,
                f"isolated {name}/{role} changed its fixed source-bound worker contract",
            )
        require(
            done["stdlib"].get("candidate_artifacts") is None
            and done["stdlib"].get("poison_guards") == {},
            f"isolated standard-library {name} reference imported a production engine",
        )
        artifacts = done["candidate"].get("candidate_artifacts")
        guards = done["candidate"].get("poison_guards")
        require(
            isinstance(artifacts, dict)
            and artifacts.get("module") == CANDIDATES[name]["module"]
            and artifacts.get("family") == name
            and len(artifacts.get("native_mappings", ()))
            == len(CANDIDATES[name]["binaries"])
            and isinstance(guards, dict)
            and len(guards) == 7
            and all(value is True for value in guards.values()),
            f"isolated {name} lost exact native mapping or poisoned-engine controls",
        )
        for role in ("stdlib", "candidate"):
            finish_worker(workers[role], f"{name}/{role}")
        return {
            "candidate": name,
            "module": CANDIDATES[name]["module"],
            "status": "PASS" if mismatch_count == 0 else "FAIL",
            "comparison_complete": True,
            "cases": EXPECTED_CASES,
            "case_sha256": expected_case_digest,
            "checks": check_count,
            "expected_checks": EXPECTED_OBSERVATIONS,
            "observations_per_case": OBSERVATIONS_PER_CASE,
            "operation_counts": counts,
            "reference_observation_sha256": expected_digest.hexdigest(),
            "candidate_observation_sha256": actual_digest.hexdigest(),
            "mismatches": mismatch_count,
            "mismatch_sha256": mismatch_digest.hexdigest(),
            "mismatch_examples": mismatches,
            "mismatch_examples_truncated": mismatch_count > len(mismatches),
            "candidate_artifacts": artifacts,
            "poison_guards": guards,
            "worker_failure": None,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "external_regex_packages": 0,
            "benchmark_or_timing_executed": False,
        }
    except Exception as error:
        failure = (
            error.evidence()
            if isinstance(error, WorkerExecutionError)
            else {
                "class": type(error).__name__,
                "message": str(error),
                "args": normalize(error.args),
                "exit_code": None,
                "stderr": "",
                "stderr_truncated": False,
                "maximum_stderr_bytes": MAX_WORKER_STDERR_BYTES,
            }
        )
        failing_case = None
        if current_expected is not None:
            pending = case_by_id.get(current_expected.get("id"))
            if pending is not None:
                failing_case = {
                    "id": pending["id"],
                    "family": pending["family"],
                    "stratum": pending["stratum"],
                    "example": pending["example"],
                    "pattern_kind": pending["pattern_kind"],
                    "pattern": pending["pattern"],
                    "subject": pending["subject"],
                    "flags": pending["flags"],
                    "operation": current_expected["operation"],
                    "expected": current_expected["result"],
                }
        candidate_done = done.get("candidate", {})
        return {
            "candidate": name,
            "module": CANDIDATES[name]["module"],
            "status": "FAIL",
            "comparison_complete": False,
            "cases": EXPECTED_CASES,
            "case_sha256": expected_case_digest,
            "checks": check_count,
            "expected_checks": EXPECTED_OBSERVATIONS,
            "completed_cases": check_count // OBSERVATIONS_PER_CASE,
            "observations_per_case": OBSERVATIONS_PER_CASE,
            "operation_counts": dict(sorted(operation_counts.items())),
            "reference_observation_sha256": expected_digest.hexdigest(),
            "candidate_observation_sha256": actual_digest.hexdigest(),
            "mismatches": mismatch_count,
            "mismatch_sha256": mismatch_digest.hexdigest(),
            "mismatch_examples": mismatches,
            "mismatch_examples_truncated": mismatch_count > len(mismatches),
            "candidate_artifacts": candidate_done.get("candidate_artifacts"),
            "poison_guards": candidate_done.get("poison_guards", {}),
            "failing_case": failing_case,
            "worker_failure": failure,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "external_regex_packages": 0,
            "benchmark_or_timing_executed": False,
        }
    finally:
        for process in workers.values():
            if process.poll() is None:
                process.kill()
            if process.poll() is None:
                process.wait()


def synthetic_audit(
    selected: tuple[str, ...],
) -> tuple[dict[str, Any], dict[str, dict[str, str]], dict[str, dict[str, str]], str]:
    interpreter = "/synthetic/pinned/bin/python3.14"
    sources = {
        name: {
            relative: hashlib.sha256(
                f"synthetic-source:{name}:{relative}".encode("ascii")
            ).hexdigest()
            for relative in CANDIDATES[name]["sources"]
        }
        for name in selected
    }
    binaries = {
        name: {
            relative: hashlib.sha256(
                f"synthetic-binary:{name}:{relative}".encode("ascii")
            ).hexdigest()
            for relative in CANDIDATES[name]["binaries"].values()
        }
        for name in selected
    }
    families: dict[str, Any] = {
        "ast": {"passed": True},
        "vm": {"passed": True},
        "rust": {"passed": True},
        "zig": {"passed": True},
    }
    global_static: dict[str, Any] = {}
    aggregate_families: dict[str, Any] = {}
    document: dict[str, Any] = {
        "schema_version": 1,
        "audit": "bounded-from-scratch-engine-provenance",
        "passed": True,
        "result": "PASS",
        "input_issues": [],
        "minimum_required_independent_families": 3,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 3,
        "core_families": ["ast", "vm", "rust"],
        "all_public_source_families": ["ast", "vm", "rust", "zig"],
        "self_test": {
            "passed": True,
            "check_count": 76,
            "failed": [],
            "fixture_storage": "in-memory only",
            "execution": {
                "isolated_subprocess": True,
                "validated": True,
                "expected_check_count": 76,
                "validated_check_count": 76,
                "interpreter": interpreter,
            },
        },
        "scope": {
            "explicit_source_paths_only": True,
            "repository_enumeration": False,
            "mapped_binaries_hashed_against_static_elf": True,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
        "families": families,
    }
    for name in selected:
        spec = CANDIDATES[name]
        files = {
            role: {
                "file": relative,
                "sha256": binaries[name][relative],
                "forbidden_regex_symbols": [],
                "cross_candidate_symbols": [],
            }
            for role, relative in spec["binaries"].items()
        }
        static = {"passed": True, "issues": [], "files": files}
        document[f"{name}_native_elf_provenance"] = static
        global_static[name] = static
        mappings = [
            {
                "role": role,
                "file": relative,
                "sha256": binaries[name][relative],
                "mapping_count": 1,
                "matches_static_elf": True,
            }
            for role, relative in sorted(spec["binaries"].items())
        ]
        count = len(spec["binaries"])
        mapping = {
            "passed": True,
            "source": "/proc/self/maps",
            "expected_owned_mapping_count": count,
            "observed_owned_mapping_count": count,
            "issues": [],
            "observed_owned_mappings": mappings,
        }
        families[name] = {
            "passed": True,
            "python_source": {
                "passed": True,
                "issues": [],
                "file": spec["sources"][0],
                "sha256": sources[name][spec["sources"][0]],
            },
            "native_sources": [
                {
                    "passed": True,
                    "issues": [],
                    "file": relative,
                    "sha256": sources[name][relative],
                }
                for relative in spec["sources"][1:]
            ],
            "owned_pipeline": {
                "passed": True,
                "issues": [],
                **spec["pipeline"],
            },
            "native_binary_provenance":
                "verified_exact_owned_elf_and_actual_hashed_memory_mappings",
            "isolated_runtime": {
                "passed": True,
                "module": spec["module"],
                "fixed_smoke_checks": 3,
                "forbidden_candidate_import_attempts": [],
                "forbidden_loaded_modules": [],
                "unexpected_candidate_modules": [],
                "prohibited_import_and_loader_probes": {
                    "stdlib_re": True,
                    "cpython_sre": True,
                    "third_party_regex": True,
                    "other_candidate": True,
                    "foreign_native_loader": True,
                },
                "native_mapping_provenance": mapping,
            },
        }
        aggregate_families[name] = {
            "passed": True,
            "expected_owned_mapping_count": count,
            "observed_owned_mapping_count": count,
        }
    document["native_elf_provenance"] = {
        "passed": True,
        "families": global_static,
    }
    document["runtime_native_mapping_provenance"] = {
        "passed": True,
        "families": aggregate_families,
    }
    return document, sources, binaries, interpreter


def self_test() -> dict[str, Any]:
    """Validate fixed cases and poison controls without reading any file."""

    candidate_free()
    checks: list[dict[str, Any]] = []

    def check(name: str, value: Any) -> None:
        require(value, f"candidate-free in-memory universal self-test failed: {name}")
        checks.append({"name": name, "passed": True})

    first = build_cases()
    second = build_cases()
    check("exact-16-independent-grammar-families", len(GRAMMAR_FAMILIES) == 16)
    check("exact-16-independent-input-strata", len(INPUT_STRATA) == 16)
    check("exact-32-domain-separated-examples", EXAMPLES_PER_STRATUM == 32)
    check("exact-8192-public-descriptor-cases", len(first) == 8_192)
    check("independent-cases-deterministic", value_digest(first) == value_digest(second))
    check("case-identifiers-unique", len({item["id"] for item in first}) == len(first))
    check("complete-grammar-coverage", {item["family"] for item in first} == set(GRAMMAR_FAMILIES))
    check("complete-buffer-and-unicode-coverage", {
        item["stratum"] for item in first
    } == set(INPUT_STRATA))
    check("exact-48-documented-observations", OBSERVATIONS_PER_CASE == 48)
    check("exact-393216-public-comparisons", EXPECTED_OBSERVATIONS == 393_216)
    check("all-extension-slots-represented", {
        EXTENSION_OPERATIONS[
            (item["extension_offset"] + offset) % len(EXTENSION_OPERATIONS)
        ]
        for item in first
        for offset in range(5)
    } == set(EXTENSION_OPERATIONS))
    check("immutable-public-seed-domain", SEED_DOMAIN == "rebar/python-re/universal-public/v1")
    check(
        "public-seed-distinct-from-original-campaign",
        SEED not in {2026072401, 2026072402, 2026072403, 0x52454241525F515032},
    )
    check(
        "three-candidate-manifest",
        set(CANDIDATES) == {"rust", "vm", "zig"},
    )
    check(
        "stdlib-ctypes-preloaded-before-strict-zig-guard",
        sys.modules.get("ctypes") is ctypes,
    )
    synthetic_failure = WorkerExecutionError(
        "synthetic/candidate",
        "ended before its exact canonical public JSON record",
        exit_code=19,
        stderr="synthetic bounded worker traceback",
        stderr_truncated=False,
    )
    check(
        "bounded-worker-exit-and-stderr-preserved",
        synthetic_failure.evidence()
        == {
            "class": "WorkerExecutionError",
            "label": "synthetic/candidate",
            "reason": "ended before its exact canonical public JSON record",
            "exit_code": 19,
            "stderr": "synthetic bounded worker traceback",
            "stderr_truncated": False,
            "maximum_stderr_bytes": MAX_WORKER_STDERR_BYTES,
        },
    )
    check(
        "exact-candidate-specific-output-path",
        all(
            validate_output(default_output(name), name) == default_output(name).resolve()
            for name in ("rust", "vm", "zig", "all")
        ),
    )
    try:
        validate_output(default_output("rust").with_name("poisoned-public-oracle.json"), "rust")
    except OracleIntegrityError:
        rejected = True
    else:
        rejected = False
    check("reject-noncanonical-output", rejected)
    document, sources, binaries, interpreter = synthetic_audit(("rust", "vm", "zig"))
    validate_audit_document(document, ("rust", "vm", "zig"), sources, binaries, interpreter)
    check("accept-complete-in-memory-three-engine-audit", True)

    def reject_poison(
        label: str,
        mutate: Callable[[dict[str, Any]], None],
    ) -> None:
        poisoned = json.loads(canonical(document))
        mutate(poisoned)
        try:
            validate_audit_document(
                poisoned,
                ("rust", "vm", "zig"),
                sources,
                binaries,
                interpreter,
            )
        except (OracleIntegrityError, KeyError, TypeError, ValueError):
            check(label, True)
        else:
            check(label, False)

    reject_poison("reject-failing-original-audit", lambda item: item.update(passed=False))
    for name in ("rust", "vm", "zig"):
        reject_poison(
            f"reject-{name}-poisoned-public-source",
            lambda item, family=name:
            item["families"][family]["python_source"].update(sha256="0" * 64),
        )
        role = "native" if name == "vm" else "bridge"
        reject_poison(
            f"reject-{name}-poisoned-owned-native",
            lambda item, family=name, native_role=role:
            item[f"{family}_native_elf_provenance"]["files"][native_role]
            .update(sha256="0" * 64),
        )
        reject_poison(
            f"reject-{name}-poisoned-actual-mapping",
            lambda item, family=name:
            item["families"][family]["isolated_runtime"]
            ["native_mapping_provenance"]["observed_owned_mappings"][0]
            .update(matches_static_elf=False),
        )
    reject_poison(
        "reject-poisoned-pinned-interpreter",
        lambda item: item["self_test"]["execution"].update(
            interpreter="/synthetic/other/bin/python3.14"
        ),
    )
    reject_poison(
        "reject-nonpublic-original-audit-scope",
        lambda item: item["scope"].update(holdout_or_case_fixture_access=True),
    )
    reference = importlib.import_module("re")
    ordinary = dict(next(
        item for item in first
        if item["family"] == "literal-escape"
        and item["stratum"] == "str-kind1"
    ))
    ordinary.update(
        pattern="a",
        subject="aba",
        flags=0,
        extension_offset=EXTENSION_OPERATIONS.index("module-search"),
        callback_mode="value",
    )
    invalid = dict(next(
        item for item in first
        if item["family"] == "invalid-grammar-flags"
        and item["stratum"] == "str-kind1"
    ))
    invalid.update(pattern="(", subject="aba", flags=0)
    released = dict(next(
        item for item in first
        if item["family"] == "literal-escape"
        and item["stratum"] == "released-memoryview"
    ))
    released.update(pattern="a", subject="aba", flags=0)
    sample = [ordinary, invalid, released]

    def observations(module: Any) -> tuple[list[dict[str, Any]], dict[str, int]]:
        rows: list[dict[str, Any]] = []
        counts = observe_cases(module, sample, rows.append)
        return rows, counts

    expected, counts = observations(reference)
    repeated, repeated_counts = observations(reference)
    check("candidate-free-stdlib-self-oracle", expected == repeated and counts == repeated_counts)
    check(
        "exact-48-aligned-records-per-synthetic-case",
        len(expected) == len(sample) * OBSERVATIONS_PER_CASE,
    )
    check(
        "symmetric-invalid-pattern-exception-details",
        any(
            row["family"] == "invalid-grammar-flags"
            and row["operation"] == "compile"
            and row["result"].get("status") == "error"
            and "pattern_error" in row["result"].get("error", {})
            for row in expected
        ),
    )
    check(
        "released-buffer-error-preserved",
        any(
            row["stratum"] == "released-memoryview"
            and row["operation"].startswith("search:")
            and row["result"].get("status") == "error"
            for row in expected
        ),
    )

    class PoisonPattern:
        def __init__(self, pattern: Any) -> None:
            self.pattern = pattern.pattern
            self.flags = pattern.flags
            self.groups = pattern.groups
            self.groupindex = pattern.groupindex
            self._pattern = pattern

        def search(self, *args: Any, **kwargs: Any) -> None:
            return None

        def __getattr__(self, name: str) -> Any:
            return getattr(self._pattern, name)

    class PoisonModule:
        def compile(self, pattern: Any, flags: int = 0) -> PoisonPattern:
            return PoisonPattern(reference.compile(pattern, flags))

        def search(self, *args: Any, **kwargs: Any) -> None:
            return None

        def __getattr__(self, name: str) -> Any:
            return getattr(reference, name)

    poisoned, _poisoned_counts = observations(PoisonModule())
    check(
        "detect-poisoned-compiled-search",
        any(
            left["operation"].startswith("search:")
            and left["result"] != right["result"]
            for left, right in zip(expected, poisoned, strict=True)
        ),
    )
    check(
        "detect-poisoned-module-search",
        any(
            left["operation"].startswith("module-search:")
            and left["result"] != right["result"]
            for left, right in zip(expected, poisoned, strict=True)
        ),
    )
    check(
        "exact-synthetic-exception-class-and-args",
        attempted(lambda: raise_error(
            ValueError("universal public poisoned exception", 7)
        ))["error"]["args"]
        == {"tuple": ["universal public poisoned exception", 7]},
    )
    candidate_free()
    check("self-test-never-imported-production-candidates", True)
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS",
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "checks": checks,
        "check_count": len(checks),
        "cases": EXPECTED_CASES,
        "observations_per_case": OBSERVATIONS_PER_CASE,
        "observations_per_candidate": EXPECTED_OBSERVATIONS,
        "case_sha256": value_digest(first),
        "candidate_imports": 0,
        "candidate_processes": 0,
        "files_read": 0,
        "files_written": 0,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "external_regex_packages": 0,
        "benchmark_or_timing_executed": False,
    }


def write_exclusive(path: Path, report: dict[str, Any]) -> str:
    data = (canonical(report) + "\n").encode("ascii")
    with path.open("xb") as stream:
        stream.write(data)
    return hashlib.sha256(data).hexdigest()


def run_gate(candidate: str, output_argument: Path | None) -> int:
    candidate_free()
    require_pinned_runtime()
    selected = selected_candidates(candidate)
    output = validate_output(
        default_output(candidate) if output_argument is None else output_argument,
        candidate,
    )
    require(
        not output.exists(),
        "refusing to overwrite canonical universal-public differential evidence",
    )
    provenance = verified_provenance(selected)
    cases = build_cases()
    reports: dict[str, dict[str, Any]] = {}
    for name in selected:
        reports[name] = run_isolated_differential(name, cases, provenance)
        if not reports[name]["comparison_complete"]:
            break
    candidate_free()
    comparison_complete = (
        len(reports) == len(selected)
        and all(
            item.get("comparison_complete") is True
            and item.get("cases") == EXPECTED_CASES
            and item.get("checks") == EXPECTED_OBSERVATIONS
            for item in reports.values()
        )
    )
    completed = [
        name
        for name in selected
        if name in reports and reports[name].get("comparison_complete") is True
    ]
    failed = next(
        (
            name for name in selected
            if name in reports and reports[name].get("status") != "PASS"
        ),
        None,
    )
    actual_comparisons = sum(item["checks"] for item in reports.values())
    report = {
        "schema": SCHEMA,
        "status": (
            "PASS"
            if comparison_complete
            and all(item["mismatches"] == 0 for item in reports.values())
            else "FAIL"
        ),
        "python": ".".join(map(str, PINNED_VERSION)),
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "selected": candidate,
        "selected_candidates": list(selected),
        "completed_candidates": completed,
        "failed_candidate": failed,
        "comparison_complete": comparison_complete,
        "cases": EXPECTED_CASES,
        "examples_per_stratum": EXAMPLES_PER_STRATUM,
        "grammar_family_count": len(GRAMMAR_FAMILIES),
        "grammar_family_counts": dict(sorted(collections.Counter(
            case["family"] for case in cases
        ).items())),
        "input_stratum_count": len(INPUT_STRATA),
        "input_stratum_counts": dict(sorted(collections.Counter(
            case["stratum"] for case in cases
        ).items())),
        "case_sha256": value_digest(cases),
        "observations_per_case": OBSERVATIONS_PER_CASE,
        "observations_per_candidate": EXPECTED_OBSERVATIONS,
        "total_comparisons": actual_comparisons,
        "planned_total_comparisons": EXPECTED_OBSERVATIONS * len(selected),
        "audit": provenance,
        "candidate_reports": reports,
        "mismatches": sum(item["mismatches"] for item in reports.values()),
        "worker_failure": (
            reports[failed].get("worker_failure")
            if failed is not None else None
        ),
        "performance": "NOT MEASURED",
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout": "NOT ACCESSED",
        "holdout_cases_read": 0,
        "external_regex_packages": 0,
    }
    output_digest = write_exclusive(output, report)
    print(canonical({
        "schema": SCHEMA,
        "status": report["status"],
        "selected": candidate,
        "output": output.relative_to(ROOT).as_posix(),
        "output_sha256": output_digest,
        "audit_sha256": provenance["audit_sha256"],
        "oracle_source_sha256": provenance["oracle_source_sha256"],
        "cases": EXPECTED_CASES,
        "observations_per_case": OBSERVATIONS_PER_CASE,
        "observations_per_candidate": EXPECTED_OBSERVATIONS,
        "total_comparisons": report["total_comparisons"],
        "planned_total_comparisons": report["planned_total_comparisons"],
        "comparison_complete": report["comparison_complete"],
        "completed_candidates": completed,
        "failed_candidate": failed,
        "mismatches": report["mismatches"],
        "holdout_cases_read": 0,
    }))
    return 0 if report["status"] == "PASS" else 1


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run exclusively candidate-free, in-memory poisoned public controls",
    )
    parser.add_argument(
        "--candidate",
        choices=("rust", "vm", "zig", "all"),
        default="rust",
        help="independently source-audited native candidate or all three",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="exact exclusive-create candidate-specific canonical JSON evidence",
    )
    parser.add_argument(
        "--worker",
        choices=("stdlib", "candidate"),
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--provenance-json", help=argparse.SUPPRESS)
    args = parser.parse_args(arguments)
    if args.self_test:
        if args.worker is not None or args.provenance_json is not None:
            parser.error("candidate-free self-test cannot invoke a production worker")
        if args.output is not None:
            parser.error("candidate-free self-test does not read or write any output")
        print(canonical(self_test()))
        return 0
    if args.worker is not None:
        if args.candidate == "all":
            parser.error("each isolated worker must select exactly one candidate")
        if args.provenance_json is None or args.output is not None:
            parser.error("an isolated worker requires only exact canonical audited provenance")
        try:
            provenance = json.loads(args.provenance_json)
        except (UnicodeError, ValueError) as error:
            raise OracleIntegrityError(
                "isolated universal-public provenance is not valid JSON"
            ) from error
        require(isinstance(provenance, dict), "isolated worker provenance is not an object")
        require(
            canonical(provenance) == args.provenance_json,
            "isolated worker did not receive exact canonical audited provenance",
        )
        run_worker(args.worker, args.candidate, provenance)
        return 0
    if args.provenance_json is not None:
        parser.error("--provenance-json is reserved for the isolated pinned workers")
    return run_gate(args.candidate, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
