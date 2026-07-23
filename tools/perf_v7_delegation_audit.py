#!/usr/bin/env python3
"""Prove every frozen-v7 candidate performs regular-expression work from scratch."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from tools.perf_v7 import frozen


ROOT = Path(__file__).resolve().parents[1]
AUDITOR = ROOT / "tools" / "audit_candidate.py"
DEFAULT_OUTPUT = ROOT / "performance" / "v7" / "evidence" / "delegation-audit.jsonl"
SOURCE_AUDITS = (
    ("candidates/ast_candidate.py", "candidates.ast_candidate", None),
    (
        "candidates/vm_candidate.py",
        "candidates.vm_candidate",
        "candidates/_vm_native.c",
    ),
    (
        "candidates/rust_candidate.py",
        "candidates.rust_candidate",
        "candidates/rust/src/lib.rs",
    ),
    (
        "candidates/rust_candidate.py",
        "candidates.rust_candidate",
        "candidates/rust/py_bridge.c",
    ),
    (
        "candidates/rust_candidate.py",
        "candidates.rust_candidate",
        "candidates/rust/src/search.rs",
    ),
    (
        "candidates/rust_candidate.py",
        "candidates.rust_candidate",
        "candidates/rust/src/newline.rs",
    ),
    (
        "candidates/rust_candidate.py",
        "candidates.rust_candidate",
        "candidates/rust/src/stack.rs",
    ),
    (
        "candidates/rust_candidate.py",
        "candidates.rust_candidate",
        "candidates/rust/src/unicode_tables.rs",
    ),
    (
        "candidates/zig_candidate.py",
        "candidates.zig_candidate",
        "candidates/zig/mini_regex.zig",
    ),
    (
        "candidates/zig_candidate.py",
        "candidates.zig_candidate",
        "candidates/zig/py_bridge.c",
    ),
)
FORBIDDEN_LIBRARY_MARKERS = (
    "_sre",
    "pcre",
    "oniguruma",
    "libonig",
    "hyperscan",
    "libre2",
    "libregex",
)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(arguments, *, label):
    result = subprocess.run(
        arguments,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            f"{label} failed with exit {result.returncode}: "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )
    return result.stdout


def guarded_source_audit(source, module, native, expected_sha256):
    command = [sys.executable, str(AUDITOR), source, module]
    if native is not None:
        command.append(native)
    output = run(command, label=f"guarded from-scratch audit: {module} {native}")
    lines = [line for line in output.splitlines() if line.strip()]
    if len(lines) != 1:
        raise RuntimeError(f"from-scratch source audit emitted unexpected evidence: {module}")
    evidence = json.loads(lines[0])
    if (
        evidence.get("module") != module
        or evidence.get("source") != source
        or evidence.get("native_source") != native
        or evidence.get("blocked_attempts") != 0
        or evidence.get("forbidden_markers") != 0
        or evidence.get("smoke") != "pass"
    ):
        raise RuntimeError(f"a candidate delegated regular-expression work: {module}")
    record = {
        "schema": "rebar-performance-delegation-source-v7",
        "expected_sha256": expected_sha256,
        "source_sha256": sha256(ROOT / source),
        "audit_runner_sha256": sha256(AUDITOR),
        **evidence,
    }
    if native is not None:
        record["native_source_sha256"] = sha256(ROOT / native)
    return record


def rust_dependency_audit(expected_sha256):
    manifest = ROOT / "candidates" / "rust" / "Cargo.toml"
    lock = ROOT / "candidates" / "rust" / "Cargo.lock"
    metadata = json.loads(
        run(
            (
                "cargo",
                "metadata",
                "--locked",
                "--offline",
                "--format-version",
                "1",
                "--manifest-path",
                str(manifest),
                "--no-deps",
            ),
            label="locked offline Rust dependency audit",
        )
    )
    packages = metadata.get("packages")
    if not isinstance(packages, list) or len(packages) != 1:
        raise RuntimeError("the from-scratch Rust engine contains external packages")
    package = packages[0]
    if (
        package.get("name") != "rebar-rust-continuation"
        or package.get("source") is not None
        or package.get("dependencies") != []
    ):
        raise RuntimeError("the from-scratch Rust engine wraps an external dependency")
    return {
        "schema": "rebar-performance-delegation-rust-dependencies-v7",
        "expected_sha256": expected_sha256,
        "mode": "cargo metadata --locked --offline --no-deps",
        "package": package["name"],
        "external_packages": 0,
        "external_dependencies": 0,
        "manifest": "candidates/rust/Cargo.toml",
        "manifest_sha256": sha256(manifest),
        "lockfile": "candidates/rust/Cargo.lock",
        "lockfile_sha256": sha256(lock),
        "status": "pass",
    }


def needed_libraries(binary):
    output = run(("readelf", "-d", str(binary)), label=f"native linkage audit: {binary}")
    result = []
    for line in output.splitlines():
        if "(NEEDED)" not in line:
            continue
        left = line.find("[")
        right = line.find("]", left + 1)
        if left < 0 or right < 0:
            raise RuntimeError(f"cannot parse native library dependency: {line}")
        result.append(line[left + 1 : right])
    return result


def rust_linkage_audits(expected_sha256):
    engine = ROOT / "candidates" / "_rust_engine.so"
    bridges = sorted((ROOT / "candidates").glob("_rust_bridge*.so"))
    if not engine.is_file() or len(bridges) != 1:
        raise RuntimeError("the exact rebuilt Rust engine and Python bridge are missing")
    records = []
    for role, binary in (("rust-engine", engine), ("rust-python-bridge", bridges[0])):
        libraries = needed_libraries(binary)
        blocked = [
            name
            for name in libraries
            if any(marker in name.lower() for marker in FORBIDDEN_LIBRARY_MARKERS)
        ]
        if blocked:
            raise RuntimeError(f"the Rust candidate links an external regex engine: {blocked}")
        if role == "rust-python-bridge" and "_rust_engine.so" not in libraries:
            raise RuntimeError("the Python bridge does not link the from-scratch Rust engine")
        records.append(
            {
                "schema": "rebar-performance-delegation-native-linkage-v7",
                "expected_sha256": expected_sha256,
                "role": role,
                "binary": str(binary.relative_to(ROOT)),
                "binary_sha256": sha256(binary),
                "needed_libraries": libraries,
                "forbidden_regex_libraries": [],
                "status": "pass",
            }
        )
    return records


def audit(output):
    suite, _cases, _expected, manifest = frozen()
    if {item[1] for item in SOURCE_AUDITS} != set(suite.MODULES[1:]):
        raise RuntimeError("the delegation audit does not cover every independent candidate")
    source_records = [
        guarded_source_audit(source, module, native, manifest["expected_sha256"])
        for source, module, native in SOURCE_AUDITS
    ]
    dependency = rust_dependency_audit(manifest["expected_sha256"])
    linkage = rust_linkage_audits(manifest["expected_sha256"])
    records = [*source_records, dependency, *linkage]
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "".join(
            json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            + "\n"
            for record in records
        ),
        encoding="utf-8",
    )
    result = {
        "schema": "rebar-performance-delegation-summary-v7",
        "expected_sha256": manifest["expected_sha256"],
        "candidate_families": len(suite.MODULES) - 1,
        "guarded_source_audits": len(source_records),
        "native_linkage_audits": len(linkage),
        "external_rust_dependencies": dependency["external_dependencies"],
        "forbidden_regex_libraries": 0,
        "blocked_import_attempts": 0,
        "failed": 0,
        "evidence_records": len(records),
        "output": str(target),
    }
    print(json.dumps(result, sort_keys=True))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    audit(args.output)


if __name__ == "__main__":
    main()
