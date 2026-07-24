#!/usr/bin/env python3
"""Bounded, isolated, public-only Rust quote-parity differential evidence.

The original from-scratch audit is validated structurally and rebound to every
actual owned Rust source, both actual native binaries, and its original pinned
interpreter.  The standard-library reference and Rust candidate run in distinct
fresh pinned workers.  Cases are generated in memory; no case archive, timing,
benchmark, external regex package, or held-out input is used.
"""

from __future__ import annotations

import argparse
import builtins
import collections
import hashlib
import importlib
import json
import os
import random
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable


SCHEMA = "rebar-rust-postfinal-quote-parity-oracle-v3"
SEED = 0x52454241525F515032
PINNED_VERSION = (3, 14, 6)
ROOT = Path(__file__).resolve().parent.parent
RUNNER = Path(__file__).resolve()
AUDIT_PATH = ROOT / "candidates" / "audits" / "FROM-SCRATCH-AUDIT.json"
DEFAULT_OUTPUT = (
    ROOT / "candidates" / "evidence"
    / "rust-postfinal-quote-parity-stage-03-slot-batch-oracle.json"
)
CANDIDATE_MODULE = "candidates.rust_candidate"
NATIVE_MODULE = "candidates._rust_bridge"
SOURCE_PATHS = (
    "candidates/rust_candidate.py",
    "candidates/rust/py_bridge.c",
    "candidates/rust/src/lib.rs",
    "candidates/rust/src/search.rs",
    "candidates/rust/src/newline.rs",
    "candidates/rust/src/stack.rs",
    "candidates/rust/src/unicode_tables.rs",
)
BINARY_PATHS = {
    "bridge": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
    "engine": "candidates/_rust_engine.so",
}
MAX_AUDIT_BYTES = 8 * 1024 * 1024
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_BINARY_BYTES = 64 * 1024 * 1024
MAX_MAP_BYTES = 4 * 1024 * 1024
MAX_WORKER_LINE_BYTES = 1024 * 1024
MAX_WORKER_STDERR_BYTES = 1024 * 1024
MAX_OBSERVATIONS = 100_000
MAX_MISMATCH_EXAMPLES = 256
HASH_CHUNK_BYTES = 1024 * 1024
IGNORECASE = 2
MULTILINE = 8
ASCII = 256
SUBJECT_KINDS = (
    "str-kind1",
    "str-kind2",
    "str-kind4",
    "bytes",
    "bytearray",
    "memoryview",
)
DELIMITER_PAIRS = (
    (",", '"'),
    (";", "'"),
    ("|", '"'),
    ("[", "]"),
    ("\\", "^"),
    ("-", "\\"),
    ("\xe9", "\xf1"),
    ("\xff", "\xa1"),
    ("\x80", "~"),
    ("\n", '"'),
    (",", "\n"),
    (",", ","),
)
REGEX_ENGINE_ROOTS = frozenset({
    "re", "_sre", "sre", "sre_compile", "sre_parse", "sre_constants",
    "regex", "regex_lite", "regex_automata", "regex_syntax",
    "fancy_regex", "re2", "pcre", "pcre2", "onig", "oniguruma",
    "onigurumacffi", "_onigurumacffi", "hyperscan", "aho_corasick",
})


class OracleIntegrityError(RuntimeError):
    """A pinned input, isolated worker, or deterministic observation failed."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise OracleIntegrityError(message)


def canonical(value: Any) -> str:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    )


def normalise(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, (bytes, bytearray)):
        return {"kind": type(value).__name__, "hex": bytes(value).hex()}
    if isinstance(value, memoryview):
        return {
            "kind": "memoryview",
            "hex": value.tobytes().hex(),
            "format": value.format,
            "itemsize": value.itemsize,
            "readonly": value.readonly,
            "shape": normalise(value.shape),
            "strides": normalise(value.strides),
            "c_contiguous": value.c_contiguous,
        }
    if isinstance(value, tuple):
        return {"tuple": [normalise(item) for item in value]}
    if isinstance(value, list):
        return [normalise(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): normalise(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    raise OracleIntegrityError(
        f"nonportable observation type: {type(value).__name__}"
    )


def value_digest(value: Any) -> str:
    return hashlib.sha256(canonical(normalise(value)).encode("ascii")).hexdigest()


def sha256_path(path: Path, maximum_bytes: int) -> str:
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as stream:
        while True:
            block = stream.read(HASH_CHUNK_BYTES)
            if not block:
                break
            total += len(block)
            require(total <= maximum_bytes, f"bounded owned file is too large: {path.name}")
            digest.update(block)
    return digest.hexdigest()


def candidate_free() -> None:
    loaded = sorted(
        name for name in sys.modules
        if name.startswith("candidates.")
        and (
            name.endswith("_candidate")
            or "._rust_bridge" in name
            or "._zig_bridge" in name
            or "._vm_native" in name
        )
    )
    require(not loaded, f"candidate-free operation loaded a production engine: {loaded!r}")


def require_pinned_runtime() -> None:
    require(sys.implementation.name == "cpython", "requires genuine pinned CPython")
    require(
        tuple(sys.version_info[:3]) == PINNED_VERSION,
        "requires the exact pinned CPython 3.14.6",
    )
    require(
        Path(sys.executable).name == "python3.14",
        "invoke the exact pinned .../python3.14 executable",
    )


def validated_output(value: Path) -> Path:
    output = value.resolve()
    require(
        output == DEFAULT_OUTPUT.resolve(),
        "--output must be the unique stage-02 quote-parity evidence path",
    )
    require(
        output.parent == (ROOT / "candidates" / "evidence").resolve(),
        "stage-02 evidence escaped its exact candidates/evidence directory",
    )
    return output


def validate_audit_document(
    document: Any,
    source_hashes: dict[str, str],
    binary_hashes: dict[str, str],
    interpreter: str,
) -> None:
    """Validate the actual original audit without freezing an obsolete digest."""

    require(isinstance(document, dict), "original from-scratch audit is not an object")
    require(document.get("schema_version") == 1, "original audit schema changed")
    require(
        document.get("audit") == "bounded-from-scratch-engine-provenance",
        "the original from-scratch audit identity changed",
    )
    require(
        document.get("passed") is True and document.get("result") == "PASS",
        "the original from-scratch audit is not passing",
    )
    require(document.get("input_issues") == [], "the original audit has input issues")
    require(
        document.get("minimum_required_independent_families") == 3
        and document.get("verified_core_family_count", 0) >= 3
        and document.get("verified_distinct_pipeline_count", 0) >= 3,
        "the original audit no longer proves three distinct owned core families",
    )
    require(
        document.get("core_families") == ["ast", "vm", "rust"]
        and document.get("all_public_source_families") == ["ast", "vm", "rust", "zig"],
        "the original audited independent-family manifest changed",
    )
    self_test = document.get("self_test")
    require(isinstance(self_test, dict), "original isolated audit self-test is missing")
    execution = self_test.get("execution")
    require(
        self_test.get("passed") is True
        and self_test.get("check_count") == 76
        and self_test.get("failed") == []
        and self_test.get("fixture_storage") == "in-memory only"
        and isinstance(execution, dict)
        and execution.get("isolated_subprocess") is True
        and execution.get("validated") is True
        and execution.get("expected_check_count") == 76
        and execution.get("validated_check_count") == 76,
        "the original complete isolated audit self-test is not proven",
    )
    recorded_interpreter = execution.get("interpreter")
    require(
        isinstance(recorded_interpreter, str)
        and Path(interpreter).name == "python3.14"
        and Path(recorded_interpreter).resolve() == Path(interpreter).resolve(),
        "the original audit did not use this exact pinned python3.14 executable",
    )
    scope = document.get("scope")
    require(
        isinstance(scope, dict)
        and scope.get("explicit_source_paths_only") is True
        and scope.get("repository_enumeration") is False
        and scope.get("mapped_binaries_hashed_against_static_elf") is True
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "the original audit lost its explicit, candidate-isolated public-only scope",
    )
    require(
        set(source_hashes) == set(SOURCE_PATHS)
        and set(binary_hashes) == set(BINARY_PATHS.values()),
        "actual owned Rust artifact paths differ from the exact public manifest",
    )
    families = document.get("families")
    require(
        isinstance(families, dict)
        and set(families) == {"ast", "vm", "rust", "zig"}
        and all(isinstance(item, dict) and item.get("passed") is True for item in families.values()),
        "the original audit no longer has four independently passing families",
    )
    family = families["rust"]
    python_source = family.get("python_source")
    require(
        isinstance(python_source, dict)
        and python_source.get("passed") is True
        and not python_source.get("issues")
        and python_source.get("file") == SOURCE_PATHS[0]
        and python_source.get("sha256") == source_hashes[SOURCE_PATHS[0]],
        "actual Rust candidate Python source differs from the passing original audit",
    )
    native_sources = family.get("native_sources")
    require(
        isinstance(native_sources, list) and len(native_sources) == len(SOURCE_PATHS) - 1,
        "the original complete owned Rust source graph changed",
    )
    observed_sources: set[str] = set()
    for entry in native_sources:
        require(isinstance(entry, dict), "an original Rust native-source record is invalid")
        relative = entry.get("file")
        require(
            isinstance(relative, str)
            and relative in SOURCE_PATHS[1:]
            and relative not in observed_sources
            and entry.get("passed") is True
            and not entry.get("issues")
            and entry.get("sha256") == source_hashes[relative],
            "an actual owned Rust native source differs from its original passing audit",
        )
        observed_sources.add(relative)
    require(observed_sources == set(SOURCE_PATHS[1:]), "an audited owned Rust source is missing")
    pipeline = family.get("owned_pipeline")
    require(
        isinstance(pipeline, dict)
        and pipeline.get("passed") is True
        and pipeline.get("issues") == []
        and pipeline.get("parser") == "rust::Parser"
        and pipeline.get("compiler") == "rust::Compiler"
        and pipeline.get("executor") == "rust::run_program",
        "the original Rust parser/compiler/executor provenance changed",
    )
    global_native = document.get("native_elf_provenance")
    rust_native = document.get("rust_native_elf_provenance")
    require(
        isinstance(global_native, dict)
        and global_native.get("passed") is True
        and isinstance(global_native.get("families"), dict)
        and isinstance(rust_native, dict)
        and rust_native.get("passed") is True
        and rust_native.get("issues") == []
        and global_native["families"].get("rust") == rust_native,
        "the original global and Rust-specific native ELF evidence disagree",
    )
    static_files = rust_native.get("files")
    require(
        isinstance(static_files, dict) and set(static_files) == set(BINARY_PATHS),
        "the exact two original owned Rust native binary roles changed",
    )
    for role, relative in sorted(BINARY_PATHS.items()):
        evidence = static_files[role]
        require(
            isinstance(evidence, dict)
            and evidence.get("file") == relative
            and evidence.get("sha256") == binary_hashes[relative]
            and evidence.get("forbidden_regex_symbols") == []
            and evidence.get("cross_candidate_symbols") == [],
            f"actual owned Rust {role} ELF differs from the original passing audit",
        )
    require(
        family.get("native_binary_provenance")
        == "verified_exact_owned_elf_and_actual_hashed_memory_mappings",
        "the original audit did not prove actual mapped Rust binaries",
    )
    runtime = family.get("isolated_runtime")
    require(
        isinstance(runtime, dict)
        and runtime.get("passed") is True
        and runtime.get("module") == CANDIDATE_MODULE
        and runtime.get("fixed_smoke_checks") == 3
        and runtime.get("forbidden_candidate_import_attempts") == []
        and runtime.get("forbidden_loaded_modules") == []
        and runtime.get("unexpected_candidate_modules") == [],
        "the original isolated Rust runtime provenance failed",
    )
    probes = runtime.get("prohibited_import_and_loader_probes")
    require(
        isinstance(probes, dict)
        and set(probes) == {
            "stdlib_re", "cpython_sre", "third_party_regex",
            "other_candidate", "foreign_native_loader",
        }
        and all(value is True for value in probes.values()),
        "the original isolated Rust import/loader poison controls changed",
    )
    mapping = runtime.get("native_mapping_provenance")
    require(
        isinstance(mapping, dict)
        and mapping.get("passed") is True
        and mapping.get("source") == "/proc/self/maps"
        and mapping.get("expected_owned_mapping_count") == 2
        and mapping.get("observed_owned_mapping_count") == 2
        and mapping.get("issues") == [],
        "the original actual Rust native memory-mapping evidence is invalid",
    )
    observed = mapping.get("observed_owned_mappings")
    require(isinstance(observed, list) and len(observed) == 2, "original Rust mappings are incomplete")
    mapped_roles: set[str] = set()
    for entry in observed:
        require(isinstance(entry, dict), "an original Rust native mapping is invalid")
        role = entry.get("role")
        require(
            isinstance(role, str)
            and role in BINARY_PATHS
            and role not in mapped_roles
            and entry.get("file") == BINARY_PATHS[role]
            and entry.get("sha256") == binary_hashes[BINARY_PATHS[role]]
            and entry.get("matches_static_elf") is True
            and isinstance(entry.get("mapping_count"), int)
            and not isinstance(entry.get("mapping_count"), bool)
            and entry["mapping_count"] > 0,
            "an original mapped Rust binary is not bound to its actual static ELF",
        )
        mapped_roles.add(role)
    aggregate = document.get("runtime_native_mapping_provenance")
    require(
        isinstance(aggregate, dict)
        and aggregate.get("passed") is True
        and isinstance(aggregate.get("families"), dict)
        and isinstance(aggregate["families"].get("rust"), dict)
        and aggregate["families"]["rust"].get("passed") is True
        and aggregate["families"]["rust"].get("expected_owned_mapping_count") == 2
        and aggregate["families"]["rust"].get("observed_owned_mapping_count") == 2,
        "the original aggregate Rust actual-mapping evidence changed",
    )


def verified_provenance() -> dict[str, Any]:
    require_pinned_runtime()
    with AUDIT_PATH.open("rb") as stream:
        audit_bytes = stream.read(MAX_AUDIT_BYTES + 1)
    require(len(audit_bytes) <= MAX_AUDIT_BYTES, "original audit exceeds its bounded size")
    try:
        document = json.loads(audit_bytes)
    except (UnicodeError, ValueError) as error:
        raise OracleIntegrityError("cannot decode the exact original from-scratch audit") from error
    source_hashes = {
        relative: sha256_path(ROOT / relative, MAX_SOURCE_BYTES)
        for relative in SOURCE_PATHS
    }
    binary_hashes = {
        relative: sha256_path(ROOT / relative, MAX_BINARY_BYTES)
        for relative in BINARY_PATHS.values()
    }
    validate_audit_document(document, source_hashes, binary_hashes, sys.executable)
    return {
        "audit_path": AUDIT_PATH.relative_to(ROOT).as_posix(),
        "audit_sha256": hashlib.sha256(audit_bytes).hexdigest(),
        "oracle_source_path": RUNNER.relative_to(ROOT).as_posix(),
        "oracle_source_sha256": sha256_path(RUNNER, MAX_SOURCE_BYTES),
        "python_executable": str(Path(sys.executable).resolve()),
        "source_sha256": dict(sorted(source_hashes.items())),
        "native_binary_sha256": dict(sorted(binary_hashes.items())),
    }


def escape_atom(character: str) -> str:
    require(len(character) == 1, "a delimiter must be exactly one character")
    if character == "\n":
        return r"\n"
    if character == "\r":
        return r"\r"
    if character == "\t":
        return r"\t"
    if ord(character) < 0x20:
        return f"\\x{ord(character):02x}"
    if character in r"\.^$*+?{}[]|()":
        return "\\" + character
    return character


def escape_class(character: str) -> str:
    require(len(character) == 1, "a quote must be exactly one character")
    if character == "\n":
        return r"\n"
    if character == "\r":
        return r"\r"
    if character == "\t":
        return r"\t"
    if ord(character) < 0x20:
        return f"\\x{ord(character):02x}"
    if character in "\\]^-":
        return "\\" + character
    return character


def pattern_families(separator: str, quote: str) -> tuple[tuple[str, str, int], ...]:
    atom = escape_atom(separator)
    quoted = escape_atom(quote)
    member = escape_class(quote)
    star = f"[^{member}]*"
    pair = f"{star}{quoted}{star}{quoted}"
    tail = f"(?:{pair})*{star}$"
    duplicated = f"[^{member}{member}]*"
    duplicate_pair = f"{duplicated}{quoted}{duplicated}{quoted}"
    singleton = f"[^{member}-{member}]*"
    singleton_pair = f"{singleton}{quoted}{singleton}{quoted}"
    lazy = f"[^{member}]*?"
    lazy_pair = f"{lazy}{quoted}{lazy}{quoted}"
    bounded = f"[^{member}]{{0,3}}"
    bounded_pair = f"{bounded}{quoted}{bounded}{quoted}"
    uncertain = f"[^{member}\\x00]*"
    uncertain_pair = f"{uncertain}{quoted}{uncertain}{quoted}"
    return (
        ("recognized-greedy", f"{atom}(?={tail})", 0),
        (
            "recognized-duplicate-class",
            f"{atom}(?=(?:{duplicate_pair})*{duplicated}$)",
            0,
        ),
        (
            "recognized-singleton-range",
            f"{atom}(?=(?:{singleton_pair})*{singleton}$)",
            0,
        ),
        ("fallback-captured-separator", f"({atom})(?={tail})", 0),
        ("fallback-captured-lookahead", f"{atom}(?=({tail}))", 0),
        ("fallback-ignorecase", f"{atom}(?={tail})", IGNORECASE),
        ("fallback-ascii-ignorecase", f"{atom}(?={tail})", ASCII | IGNORECASE),
        ("fallback-multiline", f"{atom}(?={tail})", MULTILINE),
        ("fallback-scoped-ignorecase", f"(?i:{atom})(?={tail})", 0),
        (
            "fallback-scoped-multiline",
            f"{atom}(?=(?m:(?:{pair})*{star}$))",
            0,
        ),
        ("fallback-lazy-class", f"{atom}(?=(?:{lazy_pair})*{lazy}$)", 0),
        ("fallback-lazy-pair", f"{atom}(?=(?:{pair})*?{star}$)", 0),
        (
            "fallback-bounded-class",
            f"{atom}(?=(?:{bounded_pair})*{bounded}$)",
            0,
        ),
        ("fallback-bounded-pair", f"{atom}(?=(?:{pair}){{0,3}}{star}$)", 0),
        ("fallback-negative-lookahead", f"{atom}(?!{tail})", 0),
        (
            "fallback-uncertain-class",
            f"{atom}(?=(?:{uncertain_pair})*{uncertain}$)",
            0,
        ),
        ("fallback-absolute-anchor", f"{atom}(?=(?:{pair})*{star}\\Z)", 0),
        ("invalid-unclosed-lookahead", f"{atom}(?=(?:{pair})*{star}$", 0),
    )


def make_subject(
    separator: str,
    quote: str,
    kind: str,
    ordinal: int,
    rng: random.Random,
) -> str | bytes | bytearray | memoryview:
    fragments = (
        "",
        "a",
        "xY",
        f"{quote}x{quote}",
        f"a{quote}x",
        f"{quote}{quote}",
        "line\nend",
        f"x{quote}y{quote}z",
    )
    pieces = [fragments[rng.randrange(len(fragments))] for _ in range(2 + ordinal % 4)]
    text = separator.join(pieces)
    if ordinal % 3 == 0:
        text += separator
    if ordinal % 4 == 0:
        text += "\n"
    if ordinal % 5 == 0:
        text = quote + text + quote
    if kind == "str-kind1":
        require(all(ord(item) <= 0xFF for item in text), "one-byte text widened")
        return text
    if kind == "str-kind2":
        return "\u0100" + text + "\u96ea"
    if kind == "str-kind4":
        return "\U0001f600" + text + "\U00010400"
    payload = text.encode("latin-1")
    if kind == "bytes":
        return payload
    if kind == "bytearray":
        return bytearray(payload)
    if kind == "memoryview":
        return memoryview(payload)
    raise OracleIntegrityError(f"unknown deterministic subject kind: {kind}")


def build_cases() -> list[dict[str, Any]]:
    rng = random.Random(SEED)
    cases: list[dict[str, Any]] = []
    for pair_index, (separator, quote) in enumerate(DELIMITER_PAIRS):
        for family_index, (family, pattern, flags) in enumerate(
            pattern_families(separator, quote)
        ):
            for kind_index, kind in enumerate(SUBJECT_KINDS):
                ordinal = pair_index * 113 + family_index * 17 + kind_index
                subject = make_subject(separator, quote, kind, ordinal, rng)
                prepared = pattern if kind.startswith("str-") else pattern.encode("latin-1")
                cases.append({
                    "id": f"p{pair_index:02d}:{family}:{kind}",
                    "family": family,
                    "pair": pair_index,
                    "separator": separator,
                    "quote": quote,
                    "pattern": prepared,
                    "subject": subject,
                    "subject_kind": kind,
                    "flags": flags,
                })
    for pair_index, (separator, quote) in enumerate(DELIMITER_PAIRS[:4]):
        family, pattern, flags = pattern_families(separator, quote)[0]
        for kind_index, kind in enumerate(("bytes", "bytearray", "memoryview")):
            subject = make_subject(separator, quote, kind, 700 + pair_index * 3 + kind_index, rng)
            cases.append({
                "id": f"p{pair_index:02d}:invalid-str-pattern-{kind}",
                "family": "invalid-str-pattern-binary-subject",
                "pair": pair_index,
                "separator": separator,
                "quote": quote,
                "pattern": pattern,
                "subject": subject,
                "subject_kind": kind,
                "flags": flags,
            })
        subject = make_subject(separator, quote, "str-kind1", 800 + pair_index, rng)
        cases.append({
            "id": f"p{pair_index:02d}:invalid-bytes-pattern-str-kind1",
            "family": "invalid-bytes-pattern-text-subject",
            "pair": pair_index,
            "separator": separator,
            "quote": quote,
            "pattern": pattern.encode("latin-1"),
            "subject": subject,
            "subject_kind": "str-kind1",
            "flags": flags,
        })
    require(len(cases) == len(DELIMITER_PAIRS) * 18 * len(SUBJECT_KINDS) + 16,
            "the frozen quote-parity property-case denominator changed")
    require(len({case["id"] for case in cases}) == len(cases), "duplicate quote-parity case ID")
    return cases


def attempted(action: Callable[[], Any]) -> dict[str, Any]:
    try:
        return {"status": "ok", "value": normalise(action())}
    except Exception as error:
        result: dict[str, Any] = {
            "status": "error",
            "class": type(error).__name__,
            "args": normalise(error.args),
        }
        if hasattr(error, "msg") and hasattr(error, "pos"):
            result["pattern_error"] = {
                key: normalise(getattr(error, key, None))
                for key in ("msg", "pattern", "pos", "lineno", "colno")
            }
        return result


def match_snapshot(match: Any) -> dict[str, Any] | None:
    if match is None:
        return None
    default = "!" if isinstance(match.string, str) else b"!"
    return {
        "span": normalise(match.span()),
        "regs": normalise(match.regs),
        "group0": normalise(match.group(0)),
        "groups": normalise(match.groups()),
        "groups_default": normalise(match.groups(default)),
        "groupdict": normalise(match.groupdict()),
        "groupdict_default": normalise(match.groupdict(default)),
        "lastindex": match.lastindex,
        "lastgroup": match.lastgroup,
        "pos": match.pos,
        "endpos": match.endpos,
        "string": normalise(match.string),
    }


def pattern_snapshot(pattern: Any) -> dict[str, Any]:
    return {
        "pattern": normalise(pattern.pattern),
        "flags": int(pattern.flags),
        "groups": pattern.groups,
        "groupindex": normalise(dict(pattern.groupindex)),
    }


def windows(length: int) -> tuple[tuple[int, int], ...]:
    return tuple(dict.fromkeys((
        (0, length),
        (0, 0),
        (min(1, length), length),
        (-2, length + 2),
        (length + 1, length + 3),
        (min(3, length), min(1, length)),
    )))


def scanner_values(
    pattern: Any,
    subject: str | bytes | bytearray | memoryview,
    pos: int,
    endpos: int,
    mode: str,
) -> list[Any]:
    scanner = pattern.scanner(subject, pos, endpos)
    if mode == "mixed":
        methods = (
            "search", "match", "search", "search", "match",
            "search", "match", "match", "search", "search",
        )
        return [match_snapshot(getattr(scanner, method)()) for method in methods]
    values: list[Any] = []
    for _ in range(2 * len(subject) + 12):
        match = getattr(scanner, mode)()
        values.append(match_snapshot(match))
        if match is None:
            values.append(match_snapshot(getattr(scanner, mode)()))
            values.append(match_snapshot(getattr(scanner, mode)()))
            return values
    raise OracleIntegrityError(f"bounded {mode} scanner did not terminate")


def observe_cases(
    module: Any,
    cases: list[dict[str, Any]],
    emit: Callable[[dict[str, Any]], None],
) -> dict[str, int]:
    operation_counts: collections.Counter[str] = collections.Counter()
    for case in cases:
        pattern = case["pattern"]
        subject = case["subject"]
        flags = case["flags"]
        compiled = None
        try:
            compiled = module.compile(pattern, flags)
            compile_result = {"status": "ok", "value": pattern_snapshot(compiled)}
        except Exception as error:
            compile_result = attempted(lambda error=error: raise_error(error))

        def record(name: str, action: Callable[[], Any] | None) -> None:
            result = (
                {"status": "not-run", "reason": "compile-error"}
                if action is None else attempted(action)
            )
            if name == "compile":
                result = compile_result
            operation_counts[name.partition(":")[0]] += 1
            emit({
                "kind": "observation",
                "id": case["id"],
                "family": case["family"],
                "operation": name,
                "result": result,
            })

        record("compile", None)
        for pos, endpos in windows(len(subject)):
            suffix = f":{pos}:{endpos}"
            for operation in ("search", "match", "fullmatch"):
                action = None if compiled is None else (
                    lambda item=compiled, method=operation, start=pos, end=endpos:
                    match_snapshot(getattr(item, method)(subject, start, end))
                )
                record(f"{operation}{suffix}", action)
            action = None if compiled is None else (
                lambda item=compiled, start=pos, end=endpos:
                item.findall(subject, start, end)
            )
            record(f"findall{suffix}", action)
            action = None if compiled is None else (
                lambda item=compiled, start=pos, end=endpos:
                [match_snapshot(match) for match in item.finditer(subject, start, end)]
            )
            record(f"finditer{suffix}", action)
            for mode in ("search", "match", "mixed"):
                action = None if compiled is None else (
                    lambda item=compiled, start=pos, end=endpos, method=mode:
                    scanner_values(item, subject, start, end, method)
                )
                record(f"scanner-{mode}{suffix}", action)

        for operation in ("search", "match", "fullmatch"):
            record(
                f"module-{operation}",
                lambda method=operation: match_snapshot(
                    getattr(module, method)(pattern, subject, flags)
                ),
            )
        record("module-findall", lambda: module.findall(pattern, subject, flags))
        record(
            "module-finditer",
            lambda: [match_snapshot(match) for match in module.finditer(pattern, subject, flags)],
        )
        for maximum in (0, 1, 2, -1, 5):
            action = None if compiled is None else (
                lambda item=compiled, count=maximum:
                item.split(subject, maxsplit=count)
            )
            record(f"split:{maximum}", action)
            record(
                f"module-split:{maximum}",
                lambda count=maximum: module.split(
                    pattern, subject, maxsplit=count, flags=flags
                ),
            )
    return dict(sorted(operation_counts.items()))


def raise_error(error: Exception) -> Any:
    raise error


def forbidden_native_basename(value: str) -> bool:
    name = Path(value).name.casefold().replace("-", "_")
    return name.startswith((
        "libpcre", "libonig", "libhyperscan", "libre2", "libregex",
        "libhs.", "pyinit__regex", "pyinit__re2", "pyinit__pcre",
        "pyinit__onig", "_zig_bridge", "_zig_probe", "_vm_native",
    ))


def install_candidate_guard() -> list[dict[str, str]]:
    blocked: list[dict[str, str]] = []
    allowed = frozenset({CANDIDATE_MODULE, NATIVE_MODULE})

    def prohibited(name: Any) -> bool:
        value = str(name)
        if value.partition(".")[0] in REGEX_ENGINE_ROOTS:
            return True
        return value.startswith("candidates.") and value not in allowed

    for name in tuple(sys.modules):
        if name.partition(".")[0] in REGEX_ENGINE_ROOTS:
            sys.modules.pop(name, None)

    def deny(kind: str, target: Any) -> None:
        blocked.append({"kind": kind, "target": str(target)})
        raise ImportError(f"quote-parity isolated worker rejected {kind}: {target}")

    def hook(event: str, arguments: tuple[Any, ...]) -> None:
        if event == "import" and arguments and prohibited(arguments[0]):
            deny("audit_import", arguments[0])
        elif event == "ctypes.dlopen":
            deny("foreign_native_loader", arguments[0] if arguments else event)
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
            if "holdout" in target or "benchmark" in target or "/performance/" in target:
                deny("nonpublic_fixture_access", arguments[0])

    original_import = builtins.__import__
    original_import_module = importlib.import_module

    def guarded_import(
        name: str,
        globals: Any = None,
        locals: Any = None,
        fromlist: Any = (),
        level: int = 0,
    ) -> Any:
        if prohibited(name):
            deny("python_import", name)
        if name == "candidates":
            for item in fromlist or ():
                if isinstance(item, str) and item != "*" and prohibited(f"candidates.{item}"):
                    deny("cross_candidate_import", f"candidates.{item}")
        return original_import(name, globals, locals, fromlist, level)

    def guarded_import_module(name: str, package: str | None = None) -> Any:
        if prohibited(name):
            deny("import_module", name)
        return original_import_module(name, package)

    sys.addaudithook(hook)
    builtins.__import__ = guarded_import
    importlib.import_module = guarded_import_module
    return blocked


def verify_candidate_worker(
    module: Any,
    provenance: dict[str, Any],
) -> dict[str, Any]:
    require(
        Path(module.__file__).resolve() == (ROOT / SOURCE_PATHS[0]).resolve(),
        "isolated worker loaded a different Rust candidate source",
    )
    bridge = sys.modules.get(NATIVE_MODULE)
    require(bridge is not None, "isolated Rust candidate did not load its owned native bridge")
    require(
        Path(bridge.__file__).resolve() == (ROOT / BINARY_PATHS["bridge"]).resolve(),
        "isolated Rust candidate loaded a different native bridge",
    )
    require(
        sha256_path(Path(module.__file__), MAX_SOURCE_BYTES)
        == provenance["source_sha256"][SOURCE_PATHS[0]],
        "isolated Rust Python module changed after original-audit verification",
    )
    expected = {
        str((ROOT / relative).resolve()): role
        for role, relative in BINARY_PATHS.items()
    }
    with Path("/proc/self/maps").open("r", encoding="utf-8") as stream:
        data = stream.read(MAX_MAP_BYTES + 1)
    require(len(data) <= MAX_MAP_BYTES, "isolated native mapping exceeds its bounded size")
    observed: collections.Counter[str] = collections.Counter()
    candidate_root = str((ROOT / "candidates").resolve()) + os.sep
    for row in data.splitlines():
        fields = row.split(None, 5)
        if len(fields) != 6 or not fields[5].startswith("/"):
            continue
        raw = fields[5].strip()
        require(not forbidden_native_basename(raw), "a foreign regex/candidate native engine was mapped")
        deleted = raw.endswith(" (deleted)")
        path = raw[:-10] if deleted else raw
        if path in expected:
            require(not deleted, "an actual mapped owned Rust binary was deleted")
            observed[path] += 1
        elif path.startswith(candidate_root) and (
            Path(path).name.endswith(".so") or ".so." in Path(path).name
        ):
            raise OracleIntegrityError("isolated worker mapped an unapproved candidate native binary")
    require(set(observed) == set(expected), "both exact owned Rust binaries must actually be mapped")
    mappings: list[dict[str, Any]] = []
    for path, role in sorted(expected.items(), key=lambda item: item[1]):
        relative = BINARY_PATHS[role]
        actual = sha256_path(Path(path), MAX_BINARY_BYTES)
        require(
            actual == provenance["native_binary_sha256"][relative],
            f"isolated mapped Rust {role} changed after original-audit verification",
        )
        mappings.append({
            "role": role,
            "path": relative,
            "sha256": actual,
            "mapping_count": observed[path],
        })
    return {"module": CANDIDATE_MODULE, "native_mappings": mappings}


def poison_guard_probes(blocked: list[dict[str, str]]) -> dict[str, bool]:
    controls = (
        ("stdlib-re", lambda: builtins.__import__("re")),
        ("cpython-sre", lambda: importlib.import_module("_sre")),
        ("third-party-regex", lambda: importlib.import_module("regex")),
        ("vm-candidate", lambda: importlib.import_module("candidates.vm_candidate")),
        ("zig-candidate", lambda: importlib.import_module("candidates.zig_candidate")),
        ("ast-candidate", lambda: importlib.import_module("candidates.ast_candidate")),
    )
    result: dict[str, bool] = {}
    for label, operation in controls:
        count = len(blocked)
        try:
            operation()
        except ImportError:
            result[label] = len(blocked) == count + 1
        else:
            result[label] = False
    require(all(result.values()), "isolated Rust regex/cross-candidate poison control failed")
    return result


def run_worker(role: str, expected_provenance: dict[str, Any]) -> None:
    candidate_free()
    provenance = verified_provenance()
    require(provenance == expected_provenance, "isolated worker actual audit/source/binary provenance changed")
    cases = build_cases()
    fixture_sha256 = value_digest(cases)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    blocked: list[dict[str, str]] = []
    artifacts: dict[str, Any] | None = None
    if role == "stdlib":
        module = importlib.import_module("re")
        candidate_free()
    elif role == "candidate":
        blocked = install_candidate_guard()
        module = importlib.import_module(CANDIDATE_MODULE)
        require(not blocked, "candidate attempted a prohibited engine during import")
        artifacts = verify_candidate_worker(module, provenance)
        require(not blocked, "candidate attempted a prohibited engine during native verification")
    else:
        raise OracleIntegrityError("unknown isolated quote-parity worker role")

    digest = hashlib.sha256()
    count = 0

    def emit(row: dict[str, Any]) -> None:
        nonlocal count
        encoded = canonical(row)
        require(len(encoded.encode("ascii")) <= MAX_WORKER_LINE_BYTES,
                "bounded worker observation line exceeds its exact limit")
        digest.update(encoded.encode("ascii"))
        digest.update(b"\n")
        sys.stdout.write(encoded)
        sys.stdout.write("\n")
        count += 1
        require(count <= MAX_OBSERVATIONS, "fixed bounded quote-parity observation limit exceeded")

    operations = observe_cases(module, cases, emit)
    guards: dict[str, bool] = {}
    if role == "candidate":
        require(not blocked, "Rust candidate attempted a prohibited engine while matching")
        guards = poison_guard_probes(blocked)
        artifacts = verify_candidate_worker(module, provenance)
    else:
        candidate_free()
    sys.stdout.write(canonical({
        "kind": "done",
        "schema": SCHEMA,
        "role": role,
        "seed": SEED,
        "cases": len(cases),
        "case_sha256": fixture_sha256,
        "observations": count,
        "observation_sha256": digest.hexdigest(),
        "operation_counts": operations,
        "provenance": provenance,
        "candidate_artifacts": artifacts,
        "poison_guards": guards,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "external_regex_packages": 0,
    }))
    sys.stdout.write("\n")
    sys.stdout.flush()


def read_worker_line(process: subprocess.Popen[str], role: str) -> dict[str, Any]:
    require(process.stdout is not None, f"isolated {role} worker stdout is missing")
    line = process.stdout.readline(MAX_WORKER_LINE_BYTES + 2)
    require(bool(line), f"isolated {role} worker ended without a complete bounded JSON record")
    require(
        len(line.encode("utf-8")) <= MAX_WORKER_LINE_BYTES + 1 and line.endswith("\n"),
        f"isolated {role} worker emitted an excessive or incomplete observation",
    )
    try:
        row = json.loads(line)
    except (UnicodeError, ValueError) as error:
        raise OracleIntegrityError(f"isolated {role} worker emitted noncanonical JSON") from error
    require(isinstance(row, dict), f"isolated {role} worker observation is not an object")
    require(canonical(row) + "\n" == line, f"isolated {role} worker emitted noncanonical evidence")
    return row


def finish_worker(process: subprocess.Popen[str], role: str) -> None:
    require(process.stdout is not None, f"isolated {role} worker stdout is missing")
    require(process.stdout.readline(2) == "", f"isolated {role} worker emitted trailing evidence")
    require(process.stderr is not None, f"isolated {role} worker stderr is missing")
    stderr = process.stderr.read(MAX_WORKER_STDERR_BYTES + 1)
    require(len(stderr.encode("utf-8")) <= MAX_WORKER_STDERR_BYTES,
            f"isolated {role} worker stderr exceeded its exact bound")
    code = process.wait()
    require(code == 0, f"isolated {role} worker failed ({code}): {stderr[-4000:]}")
    require(not stderr, f"isolated {role} worker emitted unexpected stderr: {stderr[-2000:]}")


def run_isolated_differential(
    cases: list[dict[str, Any]],
    provenance: dict[str, Any],
) -> dict[str, Any]:
    fixture_sha256 = value_digest(cases)
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    workers: dict[str, subprocess.Popen[str]] = {}
    mismatches: list[dict[str, Any]] = []
    mismatch_digest = hashlib.sha256()
    expected_digest = hashlib.sha256()
    actual_digest = hashlib.sha256()
    operation_counts: collections.Counter[str] = collections.Counter()
    case_by_id = {case["id"]: case for case in cases}
    checks = 0
    mismatch_count = 0
    try:
        for role in ("stdlib", "candidate"):
            command = [
                sys.executable,
                "-I",
                "-B",
                str(RUNNER),
                "--worker",
                role,
                "--provenance-json",
                canonical(provenance),
            ]
            workers[role] = subprocess.Popen(
                command,
                cwd=str(ROOT),
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                bufsize=1,
            )
        done: dict[str, dict[str, Any]] = {}
        while True:
            expected = read_worker_line(workers["stdlib"], "stdlib")
            actual = read_worker_line(workers["candidate"], "candidate")
            if expected.get("kind") == "done" or actual.get("kind") == "done":
                require(
                    expected.get("kind") == "done" and actual.get("kind") == "done",
                    "isolated workers produced different exact observation denominators",
                )
                done = {"stdlib": expected, "candidate": actual}
                break
            require(
                set(expected) == {"kind", "id", "family", "operation", "result"}
                and set(actual) == set(expected)
                and expected.get("kind") == "observation"
                and actual.get("kind") == "observation",
                "isolated worker changed the exact quote-parity observation schema",
            )
            case = case_by_id.get(expected.get("id"))
            require(
                case is not None
                and expected["id"] == actual["id"]
                and expected["family"] == case["family"] == actual["family"]
                and expected["operation"] == actual["operation"],
                "isolated workers reordered or substituted a fixed property case",
            )
            for digest, row in ((expected_digest, expected), (actual_digest, actual)):
                digest.update(canonical(row).encode("ascii"))
                digest.update(b"\n")
            operation_counts[expected["operation"].partition(":")[0]] += 1
            checks += 1
            require(checks <= MAX_OBSERVATIONS, "quote-parity observations exceeded the fixed bound")
            if expected["result"] != actual["result"]:
                mismatch_count += 1
                mismatch = {
                    "id": case["id"],
                    "family": case["family"],
                    "operation": expected["operation"],
                    "pattern": normalise(case["pattern"]),
                    "subject": normalise(case["subject"]),
                    "subject_kind": case["subject_kind"],
                    "flags": case["flags"],
                    "expected": expected["result"],
                    "actual": actual["result"],
                }
                mismatch_digest.update(canonical(mismatch).encode("ascii"))
                mismatch_digest.update(b"\n")
                if len(mismatches) < MAX_MISMATCH_EXAMPLES:
                    mismatches.append(mismatch)
        expected_operations = dict(sorted(operation_counts.items()))
        for role, digest in (("stdlib", expected_digest), ("candidate", actual_digest)):
            final = done[role]
            require(
                final.get("schema") == SCHEMA
                and final.get("role") == role
                and final.get("seed") == SEED
                and final.get("cases") == len(cases)
                and final.get("case_sha256") == fixture_sha256
                and final.get("observations") == checks
                and final.get("observation_sha256") == digest.hexdigest()
                and final.get("operation_counts") == expected_operations
                and final.get("provenance") == provenance
                and final.get("performance_fixtures_read") == 0
                and final.get("holdout_cases_read") == 0
                and final.get("external_regex_packages") == 0,
                f"isolated {role} worker altered its exact pinned audit, cases, or observations",
            )
        require(
            done["stdlib"].get("candidate_artifacts") is None
            and done["stdlib"].get("poison_guards") == {},
            "the isolated standard-library reference imported production artifacts",
        )
        require(
            isinstance(done["candidate"].get("candidate_artifacts"), dict)
            and done["candidate"]["candidate_artifacts"].get("module") == CANDIDATE_MODULE
            and len(done["candidate"]["candidate_artifacts"].get("native_mappings", ())) == 2
            and isinstance(done["candidate"].get("poison_guards"), dict)
            and len(done["candidate"]["poison_guards"]) == 6
            and all(value is True for value in done["candidate"]["poison_guards"].values()),
            "isolated Rust worker lost exact owned mapping or poisoned-engine controls",
        )
        for role in ("stdlib", "candidate"):
            finish_worker(workers[role], role)
        return {
            "cases": len(cases),
            "case_sha256": fixture_sha256,
            "checks": checks,
            "operation_counts": expected_operations,
            "reference_observation_sha256": expected_digest.hexdigest(),
            "candidate_observation_sha256": actual_digest.hexdigest(),
            "mismatches": mismatch_count,
            "mismatch_sha256": mismatch_digest.hexdigest(),
            "mismatch_examples": mismatches,
            "mismatch_examples_truncated": mismatch_count > len(mismatches),
            "candidate_artifacts": done["candidate"]["candidate_artifacts"],
            "poison_guards": done["candidate"]["poison_guards"],
        }
    finally:
        for process in workers.values():
            if process.poll() is None:
                process.kill()
            if process.poll() is None:
                process.wait()


def synthetic_audit() -> tuple[dict[str, Any], dict[str, str], dict[str, str], str]:
    interpreter = "/synthetic/pinned/bin/python3.14"
    source_hashes = {
        path: hashlib.sha256(f"synthetic-source:{path}".encode("ascii")).hexdigest()
        for path in SOURCE_PATHS
    }
    binary_hashes = {
        path: hashlib.sha256(f"synthetic-binary:{path}".encode("ascii")).hexdigest()
        for path in BINARY_PATHS.values()
    }
    files = {
        role: {
            "file": path,
            "sha256": binary_hashes[path],
            "forbidden_regex_symbols": [],
            "cross_candidate_symbols": [],
        }
        for role, path in BINARY_PATHS.items()
    }
    rust_native = {"passed": True, "issues": [], "files": files}
    mapping = {
        "passed": True,
        "source": "/proc/self/maps",
        "expected_owned_mapping_count": 2,
        "observed_owned_mapping_count": 2,
        "issues": [],
        "observed_owned_mappings": [
            {
                "role": role,
                "file": path,
                "sha256": binary_hashes[path],
                "mapping_count": 1,
                "matches_static_elf": True,
            }
            for role, path in sorted(BINARY_PATHS.items())
        ],
    }
    family = {
        "passed": True,
        "python_source": {
            "passed": True, "issues": [], "file": SOURCE_PATHS[0],
            "sha256": source_hashes[SOURCE_PATHS[0]],
        },
        "native_sources": [
            {"passed": True, "issues": [], "file": path, "sha256": source_hashes[path]}
            for path in SOURCE_PATHS[1:]
        ],
        "owned_pipeline": {
            "passed": True, "issues": [], "parser": "rust::Parser",
            "compiler": "rust::Compiler", "executor": "rust::run_program",
        },
        "native_binary_provenance":
            "verified_exact_owned_elf_and_actual_hashed_memory_mappings",
        "isolated_runtime": {
            "passed": True,
            "module": CANDIDATE_MODULE,
            "fixed_smoke_checks": 3,
            "forbidden_candidate_import_attempts": [],
            "forbidden_loaded_modules": [],
            "unexpected_candidate_modules": [],
            "prohibited_import_and_loader_probes": {
                "stdlib_re": True, "cpython_sre": True,
                "third_party_regex": True, "other_candidate": True,
                "foreign_native_loader": True,
            },
            "native_mapping_provenance": mapping,
        },
    }
    document = {
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
        "families": {
            "ast": {"passed": True}, "vm": {"passed": True},
            "rust": family, "zig": {"passed": True},
        },
        "native_elf_provenance": {
            "passed": True, "families": {"rust": rust_native},
        },
        "rust_native_elf_provenance": rust_native,
        "runtime_native_mapping_provenance": {
            "passed": True,
            "families": {
                "rust": {
                    "passed": True,
                    "expected_owned_mapping_count": 2,
                    "observed_owned_mapping_count": 2,
                },
            },
        },
    }
    return document, source_hashes, binary_hashes, interpreter


def self_test() -> dict[str, Any]:
    """Use exclusively in-memory cases, synthetic audit data, and stdlib re."""

    candidate_free()
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: Any) -> None:
        require(condition, f"candidate-free synthetic self-test failed: {name}")
        checks.append({"name": name, "passed": True})

    first = build_cases()
    second = build_cases()
    check("fixed-case-denominator", len(first) == 1_312)
    check("seeded-cases-deterministic", value_digest(first) == value_digest(second))
    check("unique-case-identifiers", len({case["id"] for case in first}) == len(first))
    check("all-subject-kinds", {case["subject_kind"] for case in first} == set(SUBJECT_KINDS))
    check("distinct-latin1-delimiters", any(
        ord(case["separator"]) > 127 and case["separator"] != case["quote"]
        for case in first
    ))
    check("newline-quote-fallback", any(case["quote"] == "\n" for case in first))
    check("equal-quote-fallback", any(case["separator"] == case["quote"] for case in first))
    check("newline-separator", any(case["separator"] == "\n" for case in first))
    check("captures-scoped-lazy-bounded-negative-controls", {
        "fallback-captured-separator", "fallback-captured-lookahead",
        "fallback-scoped-ignorecase", "fallback-scoped-multiline",
        "fallback-lazy-class", "fallback-lazy-pair",
        "fallback-bounded-class", "fallback-bounded-pair",
        "fallback-negative-lookahead", "fallback-uncertain-class",
        "invalid-unclosed-lookahead",
    }.issubset({case["family"] for case in first}))
    check("incompatible-subject-negative-controls", {
        "invalid-str-pattern-binary-subject",
        "invalid-bytes-pattern-text-subject",
    }.issubset({case["family"] for case in first}))
    check("exact-canonical-output", validated_output(DEFAULT_OUTPUT) == DEFAULT_OUTPUT.resolve())
    try:
        validated_output(DEFAULT_OUTPUT.with_name("poisoned-quote-parity.json"))
    except OracleIntegrityError:
        rejected_output = True
    else:
        rejected_output = False
    check("reject-noncanonical-output", rejected_output)

    document, sources, binaries, interpreter = synthetic_audit()
    validate_audit_document(document, sources, binaries, interpreter)
    check("accept-complete-in-memory-audit", True)

    def reject_poison(name: str, mutate: Callable[[dict[str, Any]], None]) -> None:
        poisoned = json.loads(canonical(document))
        mutate(poisoned)
        try:
            validate_audit_document(poisoned, sources, binaries, interpreter)
        except (OracleIntegrityError, KeyError, TypeError):
            check(name, True)
        else:
            check(name, False)

    reject_poison("reject-failing-original-audit", lambda item: item.update(passed=False))
    reject_poison(
        "reject-poisoned-original-source",
        lambda item: item["families"]["rust"]["python_source"].update(sha256="0" * 64),
    )
    reject_poison(
        "reject-poisoned-original-native-source",
        lambda item: item["families"]["rust"]["native_sources"][1].update(sha256="0" * 64),
    )
    reject_poison(
        "reject-poisoned-original-native-path",
        lambda item: item["rust_native_elf_provenance"]["files"]["engine"].update(
            file="candidates/unapproved.so"
        ),
    )
    reject_poison(
        "reject-poisoned-actual-native-mapping",
        lambda item: item["families"]["rust"]["isolated_runtime"]
        ["native_mapping_provenance"]["observed_owned_mappings"][0]
        .update(matches_static_elf=False),
    )
    reject_poison(
        "reject-poisoned-pinned-interpreter",
        lambda item: item["self_test"]["execution"].update(
            interpreter="/synthetic/unapproved/bin/python3.14"
        ),
    )
    reject_poison(
        "reject-incomplete-original-poison-controls",
        lambda item: item["families"]["rust"]["isolated_runtime"]
        ["prohibited_import_and_loader_probes"].update(third_party_regex=False),
    )
    reject_poison(
        "reject-nonpublic-original-audit-scope",
        lambda item: item["scope"].update(holdout_or_case_fixture_access=True),
    )

    reference = importlib.import_module("re")
    matching_sample = dict(
        next(case for case in first if case["family"] == "recognized-greedy"
             and case["subject_kind"] == "str-kind1"
             and case["pair"] == 0)
    )
    matching_sample["subject"] = 'a,"x,y",b'
    sample = [
        matching_sample,
        next(case for case in first if case["family"] == "invalid-unclosed-lookahead"
             and case["subject_kind"] == "str-kind1"
             and case["pair"] == 0),
    ]

    def observations(module: Any) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        observe_cases(module, sample, rows.append)
        return rows

    expected = observations(reference)
    check("candidate-free-independent-self-oracle", expected == observations(reference))
    check("symmetric-invalid-pattern-exceptions", any(
        row["family"] == "invalid-unclosed-lookahead"
        and row["operation"] == "compile"
        and row["result"].get("status") == "error"
        and "class" in row["result"]
        and "args" in row["result"]
        and "pattern_error" in row["result"]
        for row in expected
    ))

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

    poisoned_rows = observations(PoisonModule())
    check("detect-poisoned-compiled-search", any(
        left["operation"].startswith("search:")
        and left["result"] != right["result"]
        for left, right in zip(expected, poisoned_rows, strict=True)
    ))
    check("detect-poisoned-module-search", any(
        left["operation"] == "module-search"
        and left["result"] != right["result"]
        for left, right in zip(expected, poisoned_rows, strict=True)
    ))
    check("exact-exception-args-preserved", attempted(
        lambda: raise_error(ValueError("synthetic poisoned exception", 7))
    ) == {
        "status": "error", "class": "ValueError",
        "args": {"tuple": ["synthetic poisoned exception", 7]},
    })
    candidate_free()
    check("self-test-never-imported-a-production-candidate", True)
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS",
        "seed": SEED,
        "checks": checks,
        "check_count": len(checks),
        "generated_cases": len(first),
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


def write_exclusive_report(path: Path, document: dict[str, Any]) -> str:
    payload = (canonical(document) + "\n").encode("ascii")
    with path.open("xb") as stream:
        stream.write(payload)
    return hashlib.sha256(payload).hexdigest()


def run_gate(output_argument: Path) -> int:
    candidate_free()
    require_pinned_runtime()
    output = validated_output(output_argument)
    require(not output.exists(), "refusing to overwrite existing stage-02 quote-parity evidence")
    provenance = verified_provenance()
    cases = build_cases()
    result = run_isolated_differential(cases, provenance)
    candidate_free()
    family_counts = dict(sorted(collections.Counter(case["family"] for case in cases).items()))
    report = {
        "schema": SCHEMA,
        "status": "PASS" if result["mismatches"] == 0 else "FAIL",
        "seed": SEED,
        "python": ".".join(map(str, PINNED_VERSION)),
        "module": CANDIDATE_MODULE,
        "audit": provenance,
        "family_counts": family_counts,
        **result,
        "performance": "NOT MEASURED",
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout": "NOT ACCESSED",
        "holdout_cases_read": 0,
        "external_regex_packages": 0,
    }
    report_sha256 = write_exclusive_report(output, report)
    print(canonical({
        "schema": SCHEMA,
        "status": report["status"],
        "output": output.relative_to(ROOT).as_posix(),
        "output_sha256": report_sha256,
        "audit_sha256": provenance["audit_sha256"],
        "oracle_source_sha256": provenance["oracle_source_sha256"],
        "cases": result["cases"],
        "checks": result["checks"],
        "mismatches": result["mismatches"],
        "holdout_cases_read": 0,
    }))
    return 0 if result["mismatches"] == 0 else 1


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run candidate-free in-memory poisoned controls")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="the exact exclusive-create stage-02 canonical JSON evidence path")
    parser.add_argument("--worker", choices=("stdlib", "candidate"),
                        help=argparse.SUPPRESS)
    parser.add_argument("--provenance-json", help=argparse.SUPPRESS)
    args = parser.parse_args(arguments)
    if args.self_test:
        if args.worker is not None or args.provenance_json is not None:
            parser.error("candidate-free --self-test cannot invoke an isolated candidate worker")
        print(canonical(self_test()))
        return 0
    if args.worker is not None:
        if args.provenance_json is None:
            parser.error("an isolated worker requires exact original audited provenance")
        try:
            expected = json.loads(args.provenance_json)
        except (UnicodeError, ValueError) as error:
            raise OracleIntegrityError("isolated worker provenance is not canonical JSON") from error
        require(isinstance(expected, dict), "isolated worker provenance is not an object")
        require(canonical(expected) == args.provenance_json,
                "isolated worker provenance is not canonical JSON")
        run_worker(args.worker, expected)
        return 0
    if args.provenance_json is not None:
        parser.error("--provenance-json is reserved for an isolated pinned worker")
    return run_gate(args.output)


if __name__ == "__main__":
    raise SystemExit(main())
