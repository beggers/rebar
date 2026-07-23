#!/usr/bin/env python3
"""Run the unchanged, frozen 393-case public contract on independent engines.

No candidate is eligible without its own passing, artifact-bound, frozen
223,198-case edge result.  Candidate processes poison all 13 CPython regex
entry points and actively refuse other candidate engines and external regex
packages.  Every successful or failing gate writes a new, deterministic gzip
archive; existing evidence and the original frozen failure are never replaced.
The self-test uses only archived observations and private ``/tmp`` evidence.
"""

from __future__ import annotations

import argparse
import ast
import collections
import copy
import gzip
import hashlib
import importlib
import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator


ROOT = Path(__file__).resolve().parent.parent
RUNNER = Path(__file__).resolve()
AUDITS = ROOT / "candidates" / "audits"
FROZEN_SUITE = ROOT / "tools" / "rust_v8_deep_contract_oracle.py"
FROZEN_SUITE_SHA256 = (
    "ba4b640d12444a5346d918a039d8a7a9fef0c78a54f6b66c6f0eb0c9dddbe978"
)
FROZEN_FAILURE = AUDITS / "RUST-V8-DEEP-CONTRACT.json.gz"
FROZEN_FAILURE_SHA256 = (
    "db43cbf8be1d6891eb4f009b8ae92995a6434f9753b944fbf0a8ed0b44237192"
)
FROZEN_SCHEMA = "rebar-rust-v8-deep-public-contract-v1"
FROZEN_SEED = 2026072347
FROZEN_CASES = 393
FROZEN_SEEDED_CASES = 64
FROZEN_FIXTURE_SHA256 = (
    "c72a5e47f15c94ce13ce34d4918c05ef81eea5b010ac119b255264e60939ef16"
)
FROZEN_REFERENCE_SHA256 = (
    "b184f3388320909b3c28fbd3ce9c15cefc992d3e852e9495ad8fb503d1cbaad8"
)
FROZEN_BASELINE_CANDIDATE_SHA256 = (
    "f7e55d7715f887ccde54b09f323512b684f486e560b497e7107097822f504185"
)
FROZEN_BASELINE_FAILURES = 104
FROZEN_BASELINE_PRIVATE_DIFFERENCES = 64

EDGE_SCRIPT = ROOT / "tools" / "rust_v7_edge_oracle.py"
EDGE_SCRIPT_SHA256 = (
    "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca"
)
EDGE_SCHEMA = "rebar-v7-independent-edge-oracle-v1"
EDGE_SEED = 2026072329
EDGE_CHECKS = 223198
EDGE_CATEGORIES = 49
EDGE_REFERENCE_SHA256 = (
    "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526"
)
EDGE_INDEPENDENT_SEEDS = {
    "edge_generation": 2026072329,
    "memory_safety": 5928217332825410871,
    "module_api": 35403857216905324734871187764,
    "object_contract": 5928217332825411394,
    "parser_grammar": 6518143889424763005106639421778,
    "repeat_stream": 23157159151883287,
}
GRAMMAR_FIXTURE_SHA256 = (
    "f2b0e9bfaa7dedacdf201e66499019f30860050b75dd722310f27bb1c79e35dd"
)
PINNED_EXECUTABLE = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
HEX_DIGITS = frozenset("0123456789abcdef")
FORBIDDEN_EXTERNAL_ROOTS = frozenset(
    {
        "regex",
        "_regex",
        "pcre",
        "pcre2",
        "re2",
        "pyre2",
        "rure",
        "hyperscan",
        "oniguruma",
        "onig",
    }
)


@dataclass(frozen=True)
class CandidateSpec:
    module: str
    family: str
    public_path: str
    native_module: str | None
    engine_path: str | None
    source_paths: tuple[tuple[str, str], ...]


SPECS: dict[str, CandidateSpec] = {
    "candidates.rust_candidate": CandidateSpec(
        module="candidates.rust_candidate",
        family="RUST",
        public_path="candidates/rust_candidate.py",
        native_module="candidates._rust_bridge",
        engine_path="candidates/_rust_engine.so",
        source_paths=(
            ("bridge-source", "candidates/rust/py_bridge.c"),
            ("native-source", "candidates/rust/src/lib.rs"),
        ),
    ),
    "candidates.zig_candidate": CandidateSpec(
        module="candidates.zig_candidate",
        family="ZIG",
        public_path="candidates/zig_candidate.py",
        native_module="candidates._zig_bridge",
        engine_path="candidates/_zig_probe.so",
        source_paths=(
            ("bridge-source", "candidates/zig/py_bridge.c"),
            ("native-source", "candidates/zig/mini_regex.zig"),
        ),
    ),
    "candidates.vm_candidate": CandidateSpec(
        module="candidates.vm_candidate",
        family="C",
        public_path="candidates/vm_candidate.py",
        native_module="candidates._vm_native",
        engine_path=None,
        source_paths=(("native-source", "candidates/_vm_native.c"),),
    ),
    "candidates.ast_candidate": CandidateSpec(
        module="candidates.ast_candidate",
        family="AST",
        public_path="candidates/ast_candidate.py",
        native_module=None,
        engine_path=None,
        source_paths=(),
    ),
}


def sha256_path(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def require_sha256(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in HEX_DIGITS for character in value)
    ):
        raise AssertionError(f"invalid SHA-256 for {label}")
    return value


def load_frozen_suite() -> Any:
    actual = sha256_path(FROZEN_SUITE)
    if actual != FROZEN_SUITE_SHA256:
        raise AssertionError(
            "immutable deep-contract suite changed: "
            f"expected {FROZEN_SUITE_SHA256}, observed {actual}"
        )
    edge_actual = sha256_path(EDGE_SCRIPT)
    if edge_actual != EDGE_SCRIPT_SHA256:
        raise AssertionError(
            "immutable edge suite changed: "
            f"expected {EDGE_SCRIPT_SHA256}, observed {edge_actual}"
        )
    spec = importlib.util.spec_from_file_location(
        "rebar_immutable_v8_multifamily_contract", FROZEN_SUITE
    )
    if spec is None or spec.loader is None:
        raise AssertionError("cannot import the verified frozen deep-contract suite")
    suite = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = suite
    spec.loader.exec_module(suite)
    entry_module = sys.modules.get("__main__")
    if entry_module is None:
        raise AssertionError("the isolated frozen worker lost its script module")
    for item in tuple(vars(suite).values()):
        if isinstance(item, type) and item.__module__ == spec.name:
            item.__module__ = "__main__"
            setattr(entry_module, item.__name__, item)
    if suite.SCHEMA != FROZEN_SCHEMA or suite.SEED != FROZEN_SEED:
        raise AssertionError("the immutable suite changed its schema or seed")
    if suite.SEEDED_CASES != FROZEN_SEEDED_CASES:
        raise AssertionError("the immutable suite changed its seeded denominator")
    if suite.SCRIPT != FROZEN_SUITE:
        raise AssertionError("the frozen suite no longer identifies its own source")
    cases = suite.build_cases()
    if len(cases) != FROZEN_CASES:
        raise AssertionError("the immutable deep-contract denominator changed")
    if suite.digest(cases) != FROZEN_FIXTURE_SHA256:
        raise AssertionError("the immutable 393-case fixture changed")
    suite.verify_runtime()
    return suite


def original_failure(suite: Any) -> tuple[dict[str, Any], bytes]:
    raw = FROZEN_FAILURE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FROZEN_FAILURE_SHA256:
        raise AssertionError("the preserved original 104-failure archive changed")
    if len(raw) < 10 or raw[:2] != b"\x1f\x8b":
        raise AssertionError("the preserved original failure is not a gzip archive")
    if raw[3] & 0x08 or raw[4:8] != b"\x00\x00\x00\x00":
        raise AssertionError("the original gzip evidence is not deterministic")
    try:
        payload = gzip.decompress(raw)
        document = json.loads(payload)
    except (OSError, ValueError, EOFError, UnicodeError) as error:
        raise AssertionError("the preserved original failure cannot be decoded") from error
    if suite.canonical(document) != payload:
        raise AssertionError("the preserved original failure lost canonical encoding")
    scalars = {
        "schema": FROZEN_SCHEMA,
        "status": "FAIL",
        "python": "3.14.6",
        "seed": FROZEN_SEED,
        "seeded_case_count": FROZEN_SEEDED_CASES,
        "checks": FROZEN_CASES,
        "fixture_sha256": FROZEN_FIXTURE_SHA256,
        "suite_path": "tools/rust_v8_deep_contract_oracle.py",
        "suite_sha256": FROZEN_SUITE_SHA256,
        "reference_a_sha256": FROZEN_REFERENCE_SHA256,
        "reference_b_sha256": FROZEN_REFERENCE_SHA256,
        "candidate_sha256": FROZEN_BASELINE_CANDIDATE_SHA256,
        "public_mismatch_count": FROZEN_BASELINE_FAILURES,
        "implementation_private_gc_topology_difference_count": (
            FROZEN_BASELINE_PRIVATE_DIFFERENCES
        ),
        "forbidden_regex_guards": 13,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    for key, expected in scalars.items():
        if document.get(key) != expected:
            raise AssertionError(f"the original failure changed: {key}")
    if document.get("stdlib_vs_stdlib_mismatches") != []:
        raise AssertionError("the archived standard-library self-control failed")
    if len(document.get("public_mismatches", ())) != FROZEN_BASELINE_FAILURES:
        raise AssertionError("the archived public failures are incomplete")
    if len(document.get("implementation_private_gc_topology_differences", ())) != (
        FROZEN_BASELINE_PRIVATE_DIFFERENCES
    ):
        raise AssertionError("the archived private GC diagnostics are incomplete")
    for key in ("reference", "reference_independent_repeat", "candidate"):
        report = document.get(key)
        if not isinstance(report, dict) or report.get("checks") != FROZEN_CASES:
            raise AssertionError(f"the archived {key} observations are incomplete")
        rows = report.get("observations")
        if not isinstance(rows, list) or len(rows) != FROZEN_CASES:
            raise AssertionError(f"the archived {key} case denominator changed")
        if suite.digest(rows) != report.get("observation_sha256"):
            raise AssertionError(f"the archived {key} observations failed integrity")
        for row in rows:
            if row.get("sha256") != suite.digest(row.get("observation")):
                raise AssertionError(f"the archived {key} case digest changed")
    replayed = suite.mismatches(
        document["reference"]["observations"],
        document["candidate"]["observations"],
    )
    if replayed != document["public_mismatches"]:
        raise AssertionError("the original 104 public failures cannot be replayed")
    diagnostics = suite.diagnostic_differences(
        document["reference"]["implementation_private_gc_diagnostics"],
        document["candidate"]["implementation_private_gc_diagnostics"],
    )
    if diagnostics != document["implementation_private_gc_topology_differences"]:
        raise AssertionError("the original 64 private GC differences cannot be replayed")
    return document, raw


def frozen_embedded_oracles() -> dict[str, dict[str, Any]]:
    tree = ast.parse(EDGE_SCRIPT.read_text(encoding="utf-8"))
    literal_sources: dict[str, str] = {}
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            names = [target.id for target in statement.targets if isinstance(target, ast.Name)]
            value = statement.value
        elif isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
            names = [statement.target.id]
            value = statement.value
        else:
            continue
        for name in names:
            if name not in {
                "FROZEN_OBJECT_CONTRACT_SOURCE",
                "FROZEN_PARSER_GRAMMAR_SOURCE",
            }:
                continue
            try:
                parsed = ast.literal_eval(value)
            except (TypeError, ValueError, SyntaxError) as error:
                raise AssertionError(f"frozen edge source is not literal: {name}") from error
            if not isinstance(parsed, str):
                raise AssertionError(f"frozen edge source has invalid type: {name}")
            literal_sources[name] = parsed
    if set(literal_sources) != {
        "FROZEN_OBJECT_CONTRACT_SOURCE",
        "FROZEN_PARSER_GRAMMAR_SOURCE",
    }:
        raise AssertionError("the frozen edge suite lost an embedded source")
    return {
        "independent-object-contract": {
            "source_sha256": hashlib.sha256(
                literal_sources["FROZEN_OBJECT_CONTRACT_SOURCE"].encode("utf-8")
            ).hexdigest(),
            "cases": 14783,
            "seed": EDGE_INDEPENDENT_SEEDS["object_contract"],
        },
        "independent-parser-grammar": {
            "source_sha256": hashlib.sha256(
                literal_sources["FROZEN_PARSER_GRAMMAR_SOURCE"].encode("utf-8")
            ).hexdigest(),
            "cases": 20480,
            "seed": EDGE_INDEPENDENT_SEEDS["parser_grammar"],
            "cases_per_family": 1280,
            "fixture_sha256": GRAMMAR_FIXTURE_SHA256,
        },
    }


def extension_path(module: str) -> str:
    suffixes = importlib.machinery.EXTENSION_SUFFIXES
    if not suffixes or not suffixes[0].startswith(".cpython-314-"):
        raise AssertionError("native provenance requires the pinned CPython ABI")
    basename = module.rsplit(".", 1)[-1]
    return f"candidates/{basename}{suffixes[0]}"


def expected_edge_paths(spec: CandidateSpec) -> dict[str, str]:
    paths = {"public-python": spec.public_path}
    if spec.native_module is not None:
        paths["native-bridge"] = extension_path(spec.native_module)
    if spec.engine_path is not None:
        paths["native-engine"] = spec.engine_path
    if spec.family == "RUST":
        paths.update(spec.source_paths)
    return paths


def checked_relative(relative: str, role: str) -> Path:
    if not isinstance(relative, str):
        raise AssertionError(f"invalid production path for {role}")
    relative_path = Path(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise AssertionError(f"production artifact escaped the workspace: {role}")
    path = (ROOT / relative_path).resolve()
    if not path.is_relative_to((ROOT / "candidates").resolve()):
        raise AssertionError(f"production artifact is outside candidates: {role}")
    if path != ROOT / relative_path:
        raise AssertionError(f"production artifact is not its canonical path: {role}")
    if not path.is_file():
        raise AssertionError(f"production artifact is unavailable: {role}")
    return path


def validate_edge_document(
    document: Any,
    spec: CandidateSpec,
    archive_sha256: str,
    source_path: Path,
) -> tuple[dict[str, tuple[str, str]], dict[str, Any]]:
    if not isinstance(document, dict):
        raise AssertionError("the candidate-specific edge proof must be a JSON object")
    scalars = {
        "schema": EDGE_SCHEMA,
        "seed": EDGE_SEED,
        "correctness_checks": EDGE_CHECKS,
        "failed": 0,
        "module": spec.module,
        "oracle": "CPython standard-library re",
        "python": "3.14.6",
        "unicode": "16.0.0",
        "locale": "C",
        "script_sha256": EDGE_SCRIPT_SHA256,
        "expected_sha256": EDGE_REFERENCE_SHA256,
        "actual_sha256": EDGE_REFERENCE_SHA256,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    for key, expected in scalars.items():
        if document.get(key) != expected:
            raise AssertionError(f"the candidate-specific edge proof is invalid: {key}")
    if document.get("failures") != []:
        raise AssertionError("the explicit edge proof contains correctness failures")
    if document.get("independent_source_seeds") != EDGE_INDEPENDENT_SEEDS:
        raise AssertionError("the explicit edge proof changed a frozen source seed")
    categories = document.get("categories")
    if not isinstance(categories, dict) or len(categories) != EDGE_CATEGORIES:
        raise AssertionError("the edge proof changed the 49-category denominator")
    if any(
        not isinstance(name, str)
        or not name
        or type(count) is not int
        or count <= 0
        for name, count in categories.items()
    ):
        raise AssertionError("the edge proof contains an invalid category count")
    if sum(categories.values()) != EDGE_CHECKS:
        raise AssertionError("the edge proof categories do not cover all 223,198 checks")

    embedded = document.get("embedded_frozen_oracles")
    expected_embedded = frozen_embedded_oracles()
    if not isinstance(embedded, list) or len(embedded) != len(expected_embedded):
        raise AssertionError("the edge proof lost an independently frozen sub-oracle")
    found_embedded: set[str] = set()
    for item in embedded:
        if not isinstance(item, dict):
            raise AssertionError("an embedded frozen sub-oracle is malformed")
        name = item.get("name")
        if name not in expected_embedded or name in found_embedded:
            raise AssertionError("an embedded frozen sub-oracle is missing or repeated")
        for key, expected in expected_embedded[name].items():
            if item.get(key) != expected:
                raise AssertionError(f"the frozen {name} sub-oracle changed: {key}")
        if not isinstance(item.get("schema"), str) or not item["schema"]:
            raise AssertionError(f"the frozen {name} sub-oracle lost its schema")
        if name == "independent-parser-grammar":
            families = item.get("families")
            if not isinstance(families, list) or len(families) != 16:
                raise AssertionError("the frozen grammar changed its 16 families")
            if len(set(families)) != len(families):
                raise AssertionError("the frozen grammar repeats a case family")
        found_embedded.add(name)

    expected_paths = expected_edge_paths(spec)
    artifacts = document.get("candidate_artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != len(expected_paths):
        raise AssertionError("the edge proof does not identify every family artifact")
    authorized: dict[str, tuple[str, str]] = {}
    for item in artifacts:
        if not isinstance(item, dict) or set(item) != {"role", "path", "sha256"}:
            raise AssertionError("the edge proof contains malformed artifact provenance")
        role = item["role"]
        if role not in expected_paths or role in authorized:
            raise AssertionError("the edge proof repeats or substitutes an artifact role")
        if item["path"] != expected_paths[role]:
            raise AssertionError(f"the edge proof substituted a {spec.family} {role}")
        path = checked_relative(item["path"], role)
        expected = require_sha256(item["sha256"], role)
        actual = sha256_path(path)
        if actual != expected:
            raise AssertionError(f"the {spec.family} {role} is stale or unproven")
        authorized[role] = (item["path"], expected)
    if set(authorized) != set(expected_paths):
        raise AssertionError("the edge proof omitted a candidate artifact")

    complete = dict(authorized)
    for role, relative in spec.source_paths:
        path = checked_relative(relative, role)
        current = (relative, sha256_path(path))
        if role in complete and complete[role] != current:
            raise AssertionError(f"the {spec.family} edge-proven source is stale: {role}")
        complete[role] = current

    def serialized(items: dict[str, tuple[str, str]]) -> list[dict[str, str]]:
        return [
            {"role": role, "path": relative, "sha256": value}
            for role, (relative, value) in sorted(items.items())
        ]

    proof = {
        "schema": EDGE_SCHEMA,
        "path": str(source_path.resolve()),
        "archive_sha256": require_sha256(archive_sha256, "edge proof archive"),
        "script_sha256": EDGE_SCRIPT_SHA256,
        "seed": EDGE_SEED,
        "checks": EDGE_CHECKS,
        "category_count": EDGE_CATEGORIES,
        "reference_sha256": EDGE_REFERENCE_SHA256,
        "candidate_sha256": EDGE_REFERENCE_SHA256,
        "failed": 0,
        "module": spec.module,
        "family": spec.family,
        "candidate_artifacts": serialized(authorized),
        "production_artifacts": serialized(complete),
    }
    return complete, proof


def read_edge_proof(
    path: Path, spec: CandidateSpec
) -> tuple[dict[str, tuple[str, str]], dict[str, Any], dict[str, Any]]:
    resolved = path.resolve()
    if resolved == FROZEN_FAILURE.resolve():
        raise AssertionError("the frozen deep-contract failure is not an edge proof")
    try:
        raw = resolved.read_bytes()
    except OSError as error:
        raise AssertionError("the explicit candidate edge proof is unavailable") from error
    if len(raw) < 10 or raw[:2] != b"\x1f\x8b":
        raise AssertionError("the explicit edge proof is not gzip")
    if raw[3] & 0x08 or raw[4:8] != b"\x00\x00\x00\x00":
        raise AssertionError("the explicit edge proof has nondeterministic metadata")
    try:
        document = json.loads(gzip.decompress(raw))
    except (OSError, ValueError, EOFError, UnicodeError) as error:
        raise AssertionError("the candidate edge proof cannot be decoded") from error
    authorized, proof = validate_edge_document(
        document, spec, hashlib.sha256(raw).hexdigest(), resolved
    )
    return authorized, proof, document


def verify_original_still_frozen() -> None:
    if sha256_path(FROZEN_SUITE) != FROZEN_SUITE_SHA256:
        raise AssertionError("the immutable deep-contract suite changed during the gate")
    if sha256_path(EDGE_SCRIPT) != EDGE_SCRIPT_SHA256:
        raise AssertionError("the immutable edge suite changed during the gate")
    if sha256_path(FROZEN_FAILURE) != FROZEN_FAILURE_SHA256:
        raise AssertionError("the preserved original 104-failure archive changed")


def mapped_candidate_libraries() -> set[str]:
    result: set[str] = set()
    candidate_root = (ROOT / "candidates").resolve()
    try:
        with Path("/proc/self/maps").open("r", encoding="ascii") as maps:
            for number, line in enumerate(maps, start=1):
                if number > 16384 or len(line) > 16384:
                    raise AssertionError("native mapping proof exceeded its safe bounds")
                fields = line.rstrip("\n").split(maxsplit=5)
                if len(fields) != 6:
                    continue
                location = fields[5].removesuffix(" (deleted)")
                if not location.startswith("/"):
                    continue
                mapped = Path(location)
                if mapped.is_relative_to(candidate_root) and ".so" in mapped.name:
                    if fields[5].endswith(" (deleted)"):
                        raise AssertionError("a candidate native mapping was deleted")
                    result.add(str(mapped.resolve()))
    except OSError as error:
        raise AssertionError("cannot independently verify native candidate mappings") from error
    return result


class CrossEngineImportGuard:
    """Reject foreign candidate and third-party regex imports in this worker."""

    def __init__(self, suite: Any, spec: CandidateSpec):
        self.suite = suite
        self.spec = spec
        self.forbidden_candidates = frozenset(set(SPECS) - {spec.module})
        native = {item.native_module for item in SPECS.values() if item.native_module}
        if spec.native_module is not None:
            native.discard(spec.native_module)
        self.forbidden_native = frozenset(native)

    def forbidden(self, fullname: str) -> bool:
        return (
            fullname in self.forbidden_candidates
            or fullname in self.forbidden_native
            or fullname.split(".", 1)[0] in FORBIDDEN_EXTERNAL_ROOTS
        )

    def find_spec(self, fullname: str, path: Any, target: Any = None) -> None:
        if self.forbidden(fullname):
            raise self.suite.GuardSignal(
                f"production reached a forbidden independent or external engine: {fullname}"
            )
        return None

    def verify_clean_modules(self) -> None:
        for name in tuple(sys.modules):
            if self.forbidden(name):
                raise AssertionError(f"a foreign candidate or regex package is loaded: {name}")


@contextmanager
def active_cross_engine_guard(suite: Any, spec: CandidateSpec) -> Iterator[CrossEngineImportGuard]:
    guard = CrossEngineImportGuard(suite, spec)
    guard.verify_clean_modules()
    sys.meta_path.insert(0, guard)
    try:
        if not sys.meta_path or sys.meta_path[0] is not guard:
            raise AssertionError("the independent-engine import guard was not installed")
        yield guard
        if not sys.meta_path or sys.meta_path[0] is not guard:
            raise AssertionError("the independent-engine import guard disappeared")
        guard.verify_clean_modules()
    finally:
        if guard in sys.meta_path:
            sys.meta_path.remove(guard)


def audit_cross_engine_guards(guard: CrossEngineImportGuard) -> list[dict[str, str]]:
    names = sorted(
        guard.forbidden_candidates
        | guard.forbidden_native
        | {"regex", "_regex", "pcre2", "re2", "hyperscan"}
    )
    observations: list[dict[str, str]] = []
    for name in names:
        try:
            importlib.import_module(name)
        except guard.suite.GuardSignal as error:
            observations.append(
                {
                    "module": name,
                    "type": type(error).__name__,
                    "message": str(error),
                }
            )
        except BaseException as error:
            raise AssertionError(
                f"independent-engine guard did not fail closed: {name}: "
                f"{type(error).__name__}"
            ) from error
        else:
            raise AssertionError(f"independent-engine guard permitted import: {name}")
    if len(observations) != len(names):
        raise AssertionError("the independent-engine guard changed its denominator")
    guard.verify_clean_modules()
    return observations


def production_provenance(
    module: Any,
    spec: CandidateSpec,
    authorized: dict[str, tuple[str, str]],
    guard: CrossEngineImportGuard,
) -> list[dict[str, str]]:
    if getattr(module, "__name__", None) != spec.module:
        raise AssertionError("the frozen evaluator selected the wrong candidate family")
    public = checked_relative(spec.public_path, "public-python")
    if Path(module.__file__).resolve() != public:
        raise AssertionError("the public candidate module was substituted")
    if sys.modules.get(spec.module) is not module:
        raise AssertionError("the selected public candidate is not the loaded module")
    expected_mapped: set[str] = set()
    if spec.native_module is not None:
        native = sys.modules.get(spec.native_module)
        if native is None:
            raise AssertionError("the selected native bridge was not imported")
        expected_bridge = checked_relative(
            expected_edge_paths(spec)["native-bridge"], "native-bridge"
        )
        if Path(native.__file__).resolve() != expected_bridge:
            raise AssertionError("the selected native bridge was substituted")
        expected_mapped.add(str(expected_bridge))
    if spec.engine_path is not None:
        expected_mapped.add(str(checked_relative(spec.engine_path, "native-engine")))
    actual_mapped = mapped_candidate_libraries()
    if actual_mapped != expected_mapped:
        raise AssertionError(
            "candidate native mappings include a missing or foreign engine: "
            f"expected={sorted(expected_mapped)}, observed={sorted(actual_mapped)}"
        )
    guard.verify_clean_modules()
    result: list[dict[str, str]] = []
    for role, (relative, expected) in sorted(authorized.items()):
        actual = sha256_path(checked_relative(relative, role))
        if actual != expected:
            raise AssertionError(f"the edge-proven {spec.family} {role} changed during execution")
        result.append({"role": role, "path": relative, "sha256": actual})
    return result


class FrozenEvaluatorImports:
    """Redirect only the frozen evaluator's canonical candidate selection."""

    def __init__(self, module: Any):
        self.module = module

    def import_module(self, name: str, package: str | None = None) -> Any:
        if name == "candidates.rust_candidate" and package is None:
            return self.module
        return importlib.import_module(name, package)


def evaluate_worker(role: str, module_name: str, edge_path: Path | None) -> dict[str, Any]:
    suite = load_frozen_suite()
    original_failure(suite)
    spec = SPECS.get(module_name)
    if spec is None:
        raise AssertionError("unsupported independent candidate module")
    if role in ("stdlib-a", "stdlib-b"):
        if edge_path is not None:
            read_edge_proof(edge_path, spec)
        report = suite.evaluate_worker(role)
        if report.get("observation_sha256") != FROZEN_REFERENCE_SHA256:
            raise AssertionError("the isolated pinned reference changed")
        verify_worker_report(suite, report, role, None)
        verify_original_still_frozen()
        return report
    if role == "guard-self-test":
        if edge_path is not None:
            raise AssertionError("the isolated guard self-test cannot load a candidate")
        with active_cross_engine_guard(suite, spec) as cross_guard:
            guards = suite.install_regex_guards()
            before = suite.audit_regex_guards(guards)
            cross = audit_cross_engine_guards(cross_guard)
            after = suite.audit_regex_guards(guards)
            if before != after or len(before) != 13:
                raise AssertionError("the thirteen original CPython guards changed")
            report = {
                "schema": FROZEN_SCHEMA,
                "role": role,
                "python": "3.14.6",
                "seed": FROZEN_SEED,
                "checks": FROZEN_CASES,
                "fixture_sha256": FROZEN_FIXTURE_SHA256,
                "guard_count": len(before),
                "guards": before,
                "cross_engine_guard_count": len(cross),
                "cross_engine_guards": cross,
                "module": spec.module,
                "family": spec.family,
                "performance": "NOT MEASURED",
                "holdout": "NOT ACCESSED",
            }
        verify_original_still_frozen()
        return report
    if role not in ("candidate", "poison") or edge_path is None:
        raise AssertionError("a production worker requires its explicit passing edge proof")
    authorized, proof, _ = read_edge_proof(edge_path, spec)
    with active_cross_engine_guard(suite, spec) as cross_guard:
        selected = importlib.import_module(spec.module)
        initial = production_provenance(selected, spec, authorized, cross_guard)
        if initial != proof["production_artifacts"]:
            raise AssertionError("the worker loaded production artifacts outside its edge proof")
        cross_before = audit_cross_engine_guards(cross_guard)
        suite.importlib = FrozenEvaluatorImports(selected)
        suite.CANONICAL_ARTIFACTS = authorized
        suite.production_provenance = lambda actual: production_provenance(
            actual, spec, authorized, cross_guard
        )
        report = suite.evaluate_worker(role)
        cross_after = audit_cross_engine_guards(cross_guard)
        if cross_before != cross_after:
            raise AssertionError("the independent-engine guards changed during execution")
        report["cross_engine_guard_count"] = len(cross_after)
        report["cross_engine_guards"] = cross_after
        report["candidate_module"] = spec.module
        report["candidate_family"] = spec.family
        if report.get("native_artifacts") != proof["production_artifacts"]:
            raise AssertionError("the isolated worker returned unproven native artifacts")
        verify_worker_report(suite, report, role, proof)
    verify_original_still_frozen()
    return report


def verify_worker_report(
    suite: Any,
    report: Any,
    role: str,
    proof: dict[str, Any] | None,
) -> None:
    if not isinstance(report, dict):
        raise AssertionError(f"isolated {role} worker did not produce an object")
    scalars = {
        "schema": FROZEN_SCHEMA,
        "role": role,
        "seed": FROZEN_SEED,
        "checks": FROZEN_CASES,
        "fixture_sha256": FROZEN_FIXTURE_SHA256,
    }
    for key, expected in scalars.items():
        if report.get(key) != expected:
            raise AssertionError(f"isolated {role} worker changed {key}")
    if role in ("candidate", "poison"):
        if proof is None:
            raise AssertionError("a production worker lost its explicit edge proof")
        if report.get("native_artifacts") != proof.get("production_artifacts"):
            raise AssertionError("a production worker changed its proven artifacts")
        if report.get("guard_count") != 13:
            raise AssertionError("a production worker lost an original CPython poison")
        if report.get("candidate_module") != proof.get("module"):
            raise AssertionError("a production worker substituted its candidate module")
        if report.get("candidate_family") != proof.get("family"):
            raise AssertionError("a production worker substituted its engine family")
        cross = report.get("cross_engine_guards")
        if (
            not isinstance(cross, list)
            or report.get("cross_engine_guard_count") != len(cross)
            or len(cross) < 10
        ):
            raise AssertionError("a production worker lost its independent-engine guards")
    if role == "poison":
        guards = report.get("guards")
        if not isinstance(guards, list) or len(guards) != 13:
            raise AssertionError("the isolated poison worker lost a CPython guard")
        if not isinstance(report.get("native_under_poison"), dict):
            raise AssertionError("the isolated poison worker did not execute its candidate")
        return
    rows = report.get("observations")
    if not isinstance(rows, list) or len(rows) != FROZEN_CASES:
        raise AssertionError(f"isolated {role} worker lost a frozen observation")
    expected_ids = [item["id"] for item in suite.build_cases()]
    if [item.get("id") for item in rows] != expected_ids:
        raise AssertionError(f"isolated {role} worker dropped or reordered a case")
    if suite.digest(rows) != report.get("observation_sha256"):
        raise AssertionError(f"isolated {role} observations failed integrity")
    if any(item.get("sha256") != suite.digest(item.get("observation")) for item in rows):
        raise AssertionError(f"isolated {role} worker changed a case digest")
    if not isinstance(report.get("implementation_private_gc_diagnostics"), list):
        raise AssertionError(f"isolated {role} worker dropped private GC diagnostics")
    if role in ("stdlib-a", "stdlib-b"):
        if report.get("observation_sha256") != FROZEN_REFERENCE_SHA256:
            raise AssertionError("an isolated standard-library reference was substituted")


def run_worker(
    suite: Any,
    role: str,
    spec: CandidateSpec,
    edge_path: Path | None,
) -> dict[str, Any]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPATH"] = str(ROOT)
    command = [
        str(PINNED_EXECUTABLE),
        "-B",
        str(RUNNER),
        "--worker",
        role,
        "--module",
        spec.module,
    ]
    if edge_path is not None:
        command.extend(("--edge-oracle", str(edge_path.resolve())))
    process = subprocess.run(
        command,
        cwd=str(ROOT),
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if process.returncode:
        raise RuntimeError(
            f"isolated {spec.family} {role} worker failed ({process.returncode}): "
            f"{process.stderr[-8000:]} {process.stdout[-3000:]}"
        )
    try:
        report = json.loads(process.stdout)
    except (TypeError, ValueError) as error:
        raise AssertionError(f"isolated {role} worker returned invalid JSON") from error
    if role == "guard-self-test":
        if (
            not isinstance(report, dict)
            or report.get("schema") != FROZEN_SCHEMA
            or report.get("role") != role
            or report.get("checks") != FROZEN_CASES
            or report.get("fixture_sha256") != FROZEN_FIXTURE_SHA256
            or report.get("guard_count") != 13
            or len(report.get("guards", ())) != 13
            or report.get("cross_engine_guard_count", 0) < 10
            or len(report.get("cross_engine_guards", ()))
            != report.get("cross_engine_guard_count")
            or report.get("module") != spec.module
            or report.get("family") != spec.family
        ):
            raise AssertionError("the isolated self-test lost an active production guard")
        return report
    proof = None
    if role in ("candidate", "poison"):
        if edge_path is None:
            raise AssertionError("the production worker is missing its edge proof")
        _, proof, _ = read_edge_proof(edge_path, spec)
    verify_worker_report(suite, report, role, proof)
    return report


def validated_output(
    path: Path,
    spec: CandidateSpec,
    temporary_root: Path | None = None,
) -> Path:
    resolved = path.resolve()
    if resolved == FROZEN_FAILURE.resolve():
        raise AssertionError("refusing to overwrite the immutable original failure")
    prefix = f"RUST-V8-DEEP-CONTRACT-{spec.family}-"
    if not resolved.name.startswith(prefix) or not resolved.name.endswith(".json.gz"):
        raise AssertionError("evidence requires its exact independent family and gzip suffix")
    stage = resolved.name[len(prefix) : -len(".json.gz")]
    if not stage or any(not (char.isascii() and (char.isalnum() or char in "- _")) for char in stage):
        raise AssertionError("evidence requires a safe, nonempty explicit stage name")
    if " " in stage or "_" in stage:
        raise AssertionError("evidence stage names use only letters, numbers, and hyphens")
    expected_parent = AUDITS.resolve()
    if temporary_root is not None:
        root = temporary_root.resolve()
        if root.parent != Path("/tmp"):
            raise AssertionError("self-test evidence must use a direct /tmp temporary directory")
        expected_parent = root
    if resolved.parent != expected_parent:
        raise AssertionError("evidence escaped its authorized family-specific directory")
    if not expected_parent.is_dir():
        raise AssertionError("the authorized evidence directory does not exist")
    if resolved.exists() or resolved.is_symlink():
        raise AssertionError("refusing to overwrite existing family-specific evidence")
    return resolved


def write_evidence(suite: Any, path: Path, report: dict[str, Any]) -> str:
    verify_original_still_frozen()
    if path.resolve() == FROZEN_FAILURE.resolve():
        raise AssertionError("refusing to write the original frozen failure")
    payload = suite.canonical(report)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        with gzip.GzipFile(
            filename="",
            fileobj=stream,
            mode="wb",
            compresslevel=9,
            mtime=0,
        ) as archive:
            archive.write(payload)
    raw = path.read_bytes()
    if len(raw) < 10 or raw[:2] != b"\x1f\x8b":
        raise AssertionError("family-specific evidence is not a valid gzip archive")
    if raw[3] & 0x08 or raw[4:8] != b"\x00\x00\x00\x00":
        raise AssertionError("family-specific gzip metadata is nondeterministic")
    if gzip.decompress(raw) != payload:
        raise AssertionError("family-specific evidence failed its canonical round-trip")
    verify_original_still_frozen()
    return hashlib.sha256(raw).hexdigest()


def build_report(
    suite: Any,
    baseline: dict[str, Any],
    spec: CandidateSpec,
    edge_path: Path,
) -> dict[str, Any]:
    _, proof, _ = read_edge_proof(edge_path, spec)
    first = run_worker(suite, "stdlib-a", spec, edge_path)
    second = run_worker(suite, "stdlib-b", spec, edge_path)
    reference_failures = suite.mismatches(first["observations"], second["observations"])
    if reference_failures:
        raise AssertionError("the two independently isolated pinned references differ")
    if first["observations"] != baseline["reference"]["observations"]:
        raise AssertionError("the first reference differs from the frozen 393 answers")
    if second["observations"] != baseline["reference_independent_repeat"]["observations"]:
        raise AssertionError("the second reference differs from the frozen 393 answers")
    poison = run_worker(suite, "poison", spec, edge_path)
    differential = suite.verify_differential_self_test()
    candidate = run_worker(suite, "candidate", spec, edge_path)
    if poison["native_artifacts"] != proof["production_artifacts"]:
        raise AssertionError("the isolated poison worker loaded unproven artifacts")
    if candidate["native_artifacts"] != proof["production_artifacts"]:
        raise AssertionError("the isolated candidate worker loaded unproven artifacts")
    if poison["cross_engine_guards"] != candidate["cross_engine_guards"]:
        raise AssertionError("the independent-engine guards changed between workers")
    failures = suite.mismatches(first["observations"], candidate["observations"])
    topology = suite.diagnostic_differences(
        first["implementation_private_gc_diagnostics"],
        candidate["implementation_private_gc_diagnostics"],
    )
    counts = collections.Counter(item.get("family", "missing") for item in failures)
    report = {
        "schema": FROZEN_SCHEMA,
        "status": "FAIL" if failures else "PASS",
        "python": "3.14.6",
        "seed": FROZEN_SEED,
        "seeded_case_count": FROZEN_SEEDED_CASES,
        "checks": FROZEN_CASES,
        "fixture_sha256": FROZEN_FIXTURE_SHA256,
        "suite_path": "tools/rust_v8_deep_contract_oracle.py",
        "suite_sha256": FROZEN_SUITE_SHA256,
        "reference_a_sha256": first["observation_sha256"],
        "reference_b_sha256": second["observation_sha256"],
        "candidate_sha256": candidate["observation_sha256"],
        "stdlib_vs_stdlib_mismatches": reference_failures,
        "public_mismatch_count": len(failures),
        "public_mismatch_family_counts": dict(sorted(counts.items())),
        "public_mismatches": failures,
        "implementation_private_gc_topology_difference_count": len(topology),
        "implementation_private_gc_topology_differences": topology,
        "implementation_private_gc_topology_policy": (
            "fully recorded and separately compared; explicitly not represented "
            "as documented public lifetime or collectability equality"
        ),
        "differential_poison_self_tests": differential,
        "forbidden_regex_guards": poison["guard_count"],
        "guard_observations": candidate["guard_observations"],
        "native_under_poison": poison["native_under_poison"],
        "native_artifacts": candidate["native_artifacts"],
        "cross_engine_guard_count": candidate["cross_engine_guard_count"],
        "cross_engine_guard_observations": candidate["cross_engine_guards"],
        "candidate_module": spec.module,
        "candidate_family": spec.family,
        "reference": first,
        "reference_independent_repeat": second,
        "candidate": candidate,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
        "edge_oracle": proof,
        "frozen_failure_evidence": {
            "path": "candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz",
            "archive_sha256": FROZEN_FAILURE_SHA256,
            "status": "FAIL",
            "public_mismatch_count": FROZEN_BASELINE_FAILURES,
        },
        "multifamily_runner": {
            "path": "tools/rust_v8_multi_candidate_contract.py",
            "sha256": sha256_path(RUNNER),
        },
    }
    verify_original_still_frozen()
    return report


def summarize(report: dict[str, Any], path: Path, archive_sha256: str) -> dict[str, Any]:
    keys = (
        "schema",
        "status",
        "python",
        "seed",
        "seeded_case_count",
        "checks",
        "fixture_sha256",
        "suite_sha256",
        "reference_a_sha256",
        "reference_b_sha256",
        "candidate_sha256",
        "public_mismatch_count",
        "public_mismatch_family_counts",
        "implementation_private_gc_topology_difference_count",
        "forbidden_regex_guards",
        "cross_engine_guard_count",
        "candidate_module",
        "candidate_family",
        "native_artifacts",
        "performance",
        "holdout",
    )
    result = {key: report[key] for key in keys}
    result["stdlib_vs_stdlib_mismatches"] = len(report["stdlib_vs_stdlib_mismatches"])
    result["differential_poison_self_tests"] = report["differential_poison_self_tests"]
    result["edge_oracle"] = report["edge_oracle"]
    result["frozen_failure_evidence"] = report["frozen_failure_evidence"]
    result["evidence_path"] = str(path)
    result["evidence_sha256"] = archive_sha256
    if report["public_mismatches"]:
        result["first_public_mismatches"] = report["public_mismatches"][:8]
    return result


def run_gate(
    spec: CandidateSpec,
    edge_path: Path,
    output_path: Path,
    temporary_root: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any], int]:
    suite = load_frozen_suite()
    baseline, _ = original_failure(suite)
    output = validated_output(output_path, spec, temporary_root)
    report = build_report(suite, baseline, spec, edge_path)
    archive_sha256 = write_evidence(suite, output, report)
    return report, summarize(report, output, archive_sha256), int(bool(report["public_mismatches"]))


def expect_rejection(name: str, action: Any) -> dict[str, str]:
    try:
        action()
    except (
        AssertionError,
        FileExistsError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as error:
        return {"name": name, "status": "PASS", "error_type": type(error).__name__}
    raise AssertionError(f"multi-candidate integrity poison unexpectedly passed: {name}")


def synthetic_edge_document(spec: CandidateSpec) -> dict[str, Any]:
    artifacts = []
    for role, relative in expected_edge_paths(spec).items():
        path = checked_relative(relative, role)
        artifacts.append({"role": role, "path": relative, "sha256": sha256_path(path)})
    embedded = []
    for name, expected in frozen_embedded_oracles().items():
        item = {"name": name, "schema": f"synthetic-frozen-{name}-v1", **expected}
        if name == "independent-parser-grammar":
            item["families"] = [f"synthetic-{index:02d}" for index in range(16)]
        embedded.append(item)
    return {
        "schema": EDGE_SCHEMA,
        "seed": EDGE_SEED,
        "correctness_checks": EDGE_CHECKS,
        "failed": 0,
        "module": spec.module,
        "oracle": "CPython standard-library re",
        "python": "3.14.6",
        "unicode": "16.0.0",
        "locale": "C",
        "script_sha256": EDGE_SCRIPT_SHA256,
        "expected_sha256": EDGE_REFERENCE_SHA256,
        "actual_sha256": EDGE_REFERENCE_SHA256,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
        "failures": [],
        "independent_source_seeds": copy.deepcopy(EDGE_INDEPENDENT_SEEDS),
        "categories": {
            **{f"synthetic-category-{index:02d}": 1 for index in range(EDGE_CATEGORIES - 1)},
            "synthetic-category-48": EDGE_CHECKS - EDGE_CATEGORIES + 1,
        },
        "embedded_frozen_oracles": embedded,
        "candidate_artifacts": artifacts,
    }


def self_test() -> dict[str, Any]:
    suite = load_frozen_suite()
    baseline, original_bytes = original_failure(suite)
    references: dict[str, dict[str, Any]] = {}
    standard_spec = SPECS["candidates.ast_candidate"]
    for role, baseline_name in (
        ("stdlib-a", "reference"),
        ("stdlib-b", "reference_independent_repeat"),
    ):
        reference = run_worker(suite, role, standard_spec, None)
        if reference["observations"] != baseline[baseline_name]["observations"]:
            raise AssertionError(f"fresh isolated {role} changed frozen public answers")
        references[role] = reference
    if suite.mismatches(
        references["stdlib-a"]["observations"],
        references["stdlib-b"]["observations"],
    ):
        raise AssertionError("the two fresh pinned reference controls do not agree")

    guards = run_worker(suite, "guard-self-test", standard_spec, None)
    rust = SPECS["candidates.rust_candidate"]
    document = synthetic_edge_document(rust)
    _, synthetic_proof = validate_edge_document(
        document, rust, "1" * 64, Path("/tmp/rebar-synthetic-edge.json.gz")
    )

    def poisoned(mutator: Any, *, spec: CandidateSpec = rust) -> Any:
        changed = copy.deepcopy(document)
        mutator(changed)
        return lambda: validate_edge_document(
            changed, spec, "1" * 64, Path("/tmp/rebar-synthetic-edge.json.gz")
        )

    checks = [
        expect_rejection(
            "wrong-candidate-family",
            poisoned(lambda _: None, spec=SPECS["candidates.zig_candidate"]),
        ),
        expect_rejection(
            "wrong-edge-schema", poisoned(lambda value: value.update({"schema": "poison"}))
        ),
        expect_rejection(
            "nonpassing-edge-result", poisoned(lambda value: value.update({"failed": 1}))
        ),
        expect_rejection(
            "unreported-edge-failure",
            poisoned(lambda value: value.update({"failures": [{"id": "poison"}]})),
        ),
        expect_rejection(
            "changed-edge-denominator",
            poisoned(lambda value: value.update({"correctness_checks": EDGE_CHECKS - 1})),
        ),
        expect_rejection(
            "changed-edge-reference",
            poisoned(lambda value: value.update({"expected_sha256": "0" * 64})),
        ),
        expect_rejection(
            "changed-edge-candidate",
            poisoned(lambda value: value.update({"actual_sha256": "0" * 64})),
        ),
        expect_rejection(
            "changed-independent-source-seed",
            poisoned(lambda value: value["independent_source_seeds"].update({"parser_grammar": 0})),
        ),
        expect_rejection(
            "missing-edge-category",
            poisoned(lambda value: value["categories"].pop("synthetic-category-00")),
        ),
        expect_rejection(
            "changed-edge-category-denominator",
            poisoned(lambda value: value["categories"].update({"synthetic-category-00": 2})),
        ),
        expect_rejection(
            "missing-independent-oracle",
            poisoned(lambda value: value["embedded_frozen_oracles"].pop()),
        ),
        expect_rejection(
            "changed-frozen-grammar-source",
            poisoned(
                lambda value: value["embedded_frozen_oracles"][1].update(
                    {"source_sha256": "0" * 64}
                )
            ),
        ),
        expect_rejection(
            "missing-edge-authorized-artifact",
            poisoned(lambda value: value["candidate_artifacts"].pop()),
        ),
        expect_rejection(
            "stale-edge-authorized-artifact",
            poisoned(
                lambda value: value["candidate_artifacts"][0].update(
                    {"sha256": "0" * 64}
                )
            ),
        ),
        expect_rejection(
            "edge-artifact-path-traversal",
            poisoned(
                lambda value: value["candidate_artifacts"][0].update(
                    {"path": "candidates/../candidates/rust_candidate.py"}
                )
            ),
        ),
        expect_rejection(
            "overwrite-original-frozen-failure",
            lambda: validated_output(FROZEN_FAILURE, rust),
        ),
        expect_rejection(
            "wrong-output-family",
            lambda: validated_output(
                AUDITS / "RUST-V8-DEEP-CONTRACT-ZIG-POISON.json.gz", rust
            ),
        ),
        expect_rejection(
            "wrong-output-suffix",
            lambda: validated_output(
                AUDITS / "RUST-V8-DEEP-CONTRACT-RUST-POISON.json", rust
            ),
        ),
        expect_rejection(
            "output-path-traversal",
            lambda: validated_output(
                AUDITS / ".." / "RUST-V8-DEEP-CONTRACT-RUST-POISON.json.gz", rust
            ),
        ),
    ]

    intact = copy.deepcopy(references["stdlib-a"])
    missing = copy.deepcopy(references["stdlib-a"])
    missing["observations"].pop()
    changed = copy.deepcopy(references["stdlib-a"])
    changed["observations"][0]["observation"] = {"poison": True}
    changed["observations"][0]["sha256"] = suite.digest({"poison": True})
    changed["observation_sha256"] = suite.digest(changed["observations"])
    reordered = copy.deepcopy(references["stdlib-a"])
    reordered["observations"][0], reordered["observations"][1] = (
        reordered["observations"][1],
        reordered["observations"][0],
    )
    reordered["observation_sha256"] = suite.digest(reordered["observations"])
    checks.extend(
        (
            expect_rejection(
                "missing-frozen-observation",
                lambda: verify_worker_report(suite, missing, "stdlib-a", None),
            ),
            expect_rejection(
                "changed-frozen-reference",
                lambda: verify_worker_report(suite, changed, "stdlib-a", None),
            ),
            expect_rejection(
                "reordered-frozen-observations",
                lambda: verify_worker_report(suite, reordered, "stdlib-a", None),
            ),
        )
    )
    verify_worker_report(suite, intact, "stdlib-a", None)

    with tempfile.TemporaryDirectory(
        prefix="rebar-v8-multifamily-contract-", dir="/tmp"
    ) as temporary:
        temporary_root = Path(temporary)
        output = validated_output(
            temporary_root / "RUST-V8-DEEP-CONTRACT-RUST-SELF-TEST.json.gz",
            rust,
            temporary_root,
        )
        replay = {
            "schema": FROZEN_SCHEMA,
            "mode": "archived-original-rust-replay",
            "status": "FAIL",
            "candidate_module": rust.module,
            "candidate_family": rust.family,
            "checks": FROZEN_CASES,
            "fixture_sha256": FROZEN_FIXTURE_SHA256,
            "reference_a_sha256": FROZEN_REFERENCE_SHA256,
            "reference_b_sha256": FROZEN_REFERENCE_SHA256,
            "candidate_sha256": FROZEN_BASELINE_CANDIDATE_SHA256,
            "public_mismatch_count": FROZEN_BASELINE_FAILURES,
            "public_mismatches": baseline["public_mismatches"],
            "implementation_private_gc_topology_difference_count": (
                FROZEN_BASELINE_PRIVATE_DIFFERENCES
            ),
            "implementation_private_gc_topology_differences": baseline[
                "implementation_private_gc_topology_differences"
            ],
            "reference": baseline["reference"],
            "reference_independent_repeat": baseline["reference_independent_repeat"],
            "candidate": baseline["candidate"],
            "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED",
        }
        replay_sha256 = write_evidence(suite, output, replay)
        if json.loads(gzip.decompress(output.read_bytes())) != replay:
            raise AssertionError("the archived original failure could not be reproduced")
        checks.append(
            expect_rejection(
                "existing-evidence-overwrite",
                lambda: validated_output(output, rust, temporary_root),
            )
        )
        checks.append(
            expect_rejection(
                "temporary-output-traversal",
                lambda: validated_output(
                    temporary_root / ".." / "RUST-V8-DEEP-CONTRACT-RUST-ESCAPED.json.gz",
                    rust,
                    temporary_root,
                ),
            )
        )

    if FROZEN_FAILURE.read_bytes() != original_bytes:
        raise AssertionError("the multi-candidate self-test changed original evidence")
    verify_original_still_frozen()
    return {
        "schema": FROZEN_SCHEMA,
        "mode": "multi-candidate-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "seed": FROZEN_SEED,
        "checks": FROZEN_CASES,
        "fixture_sha256": FROZEN_FIXTURE_SHA256,
        "suite_path": "tools/rust_v8_deep_contract_oracle.py",
        "suite_sha256": FROZEN_SUITE_SHA256,
        "edge_suite_path": "tools/rust_v7_edge_oracle.py",
        "edge_suite_sha256": EDGE_SCRIPT_SHA256,
        "supported_candidates": {name: spec.family for name, spec in sorted(SPECS.items())},
        "original_failure_sha256": FROZEN_FAILURE_SHA256,
        "original_failure_unchanged": True,
        "reference_a_sha256": references["stdlib-a"]["observation_sha256"],
        "reference_b_sha256": references["stdlib-b"]["observation_sha256"],
        "stdlib_vs_stdlib_mismatches": 0,
        "baseline_candidate_sha256": FROZEN_BASELINE_CANDIDATE_SHA256,
        "baseline_gate_status": "FAIL",
        "baseline_gate_exit": 1,
        "baseline_public_mismatches": FROZEN_BASELINE_FAILURES,
        "baseline_private_gc_differences": FROZEN_BASELINE_PRIVATE_DIFFERENCES,
        "baseline_complete_observations_replayed": True,
        "forbidden_regex_guards": guards["guard_count"],
        "cross_engine_guard_count": guards["cross_engine_guard_count"],
        "cross_engine_guard_observations": guards["cross_engine_guards"],
        "synthetic_edge_proof": synthetic_proof,
        "integrity_poison_self_test_count": len(checks),
        "integrity_poison_self_tests": checks,
        "temporary_replay_evidence_sha256": replay_sha256,
        "temporary_evidence_removed": True,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one unchanged frozen public contract on four independent engines."
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--gate", action="store_true")
    modes.add_argument(
        "--worker",
        choices=("stdlib-a", "stdlib-b", "candidate", "poison", "guard-self-test"),
    )
    parser.add_argument("--module", choices=tuple(SPECS))
    parser.add_argument("--edge-oracle", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(arguments)


def main(arguments: list[str]) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        if (
            options.module is not None
            or options.edge_oracle is not None
            or options.output is not None
        ):
            raise AssertionError("self-test never runs a candidate or writes repository evidence")
        suite = load_frozen_suite()
        print(suite.canonical(self_test()).decode("ascii"))
        return 0
    if options.module is None:
        raise AssertionError("workers and gates require an explicit independent candidate")
    spec = SPECS[options.module]
    if options.worker is not None:
        if options.output is not None:
            raise AssertionError("an isolated worker cannot write repository evidence")
        if options.worker == "guard-self-test" and options.edge_oracle is not None:
            raise AssertionError("the isolated guard self-test cannot load edge evidence")
        if options.worker in ("candidate", "poison") and options.edge_oracle is None:
            raise AssertionError("production workers require a passing explicit edge proof")
        suite = load_frozen_suite()
        print(
            suite.canonical(
                evaluate_worker(options.worker, spec.module, options.edge_oracle)
            ).decode("ascii")
        )
        return 0
    if options.edge_oracle is None or options.output is None:
        raise AssertionError("the multi-candidate gate requires --edge-oracle and --output")
    _, summary, status = run_gate(spec, options.edge_oracle, options.output)
    suite = load_frozen_suite()
    print(suite.canonical(summary).decode("ascii"))
    return status


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
